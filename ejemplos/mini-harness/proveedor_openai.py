"""Adaptador a una API compatible con OpenAI Chat Completions (solo biblioteca estándar).

Traduce el formato neutro del harness (``harness_documental.py``) al formato del
proveedor y de vuelta. Sirve para OpenAI y para servidores compatibles (Ollama,
llama.cpp server, vLLM, LM Studio, pasarelas...). Comprueba con tu proveedor qué
parámetros acepta: el adaptador solo envía model, messages, tools y tool_choice,
más los que pases en ``extra``.

Lo que el adaptador hace y el bucle no debe hacer:
- convertir mensajes y herramientas (``arguments`` viaja como TEXTO JSON);
- validar la respuesta y convertir argumentos mal formados en error de herramienta;
- clasificar errores HTTP: autenticación, cuota, temporal, petición;
- reintentar solo lo temporal, con límite (cada reintento puede costar tokens);
- acumular el uso de tokens que informe el proveedor.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


class ErrorProveedor(RuntimeError):
    def __init__(self, clase: str, mensaje: str, estado_http: int | None = None):
        super().__init__(f"[{clase}] {mensaje}")
        self.clase = clase          # autenticacion | cuota | temporal | peticion | respuesta | red
        self.estado_http = estado_http


def _clase_http(codigo: int) -> str:
    if codigo in (401, 403):
        return "autenticacion"
    if codigo == 429:
        return "cuota"
    if codigo in (408, 409) or codigo >= 500:
        return "temporal"
    return "peticion"


class ModeloOpenAICompatible:
    def __init__(self, base_url: str, modelo: str, api_key_env: str = "OPENAI_API_KEY",
                 timeout_s: float = 60.0, reintentos: int = 2, extra: dict | None = None):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.modelo = modelo
        self.api_key = os.environ.get(api_key_env)  # la clave nunca se registra ni se imprime
        self.timeout_s = timeout_s
        self.reintentos = reintentos
        self.extra = dict(extra or {})
        self.uso = {"prompt_tokens": 0, "completion_tokens": 0, "peticiones": 0}

    # ------------------------------------------------------------ traducción
    @staticmethod
    def convertir_mensajes(mensajes: list[dict]) -> list[dict]:
        salida = []
        for m in mensajes:
            if m["role"] in ("system", "user"):
                salida.append({"role": m["role"], "content": m["content"]})
            elif m["role"] == "assistant":
                salida.append({"role": "assistant", "content": m.get("content"),
                               "tool_calls": [{"id": c["id"], "type": "function",
                                               "function": {"name": c["name"],
                                                            "arguments": c.get("arguments_raw") or json.dumps(c["arguments"], ensure_ascii=False)}}
                                              for c in m.get("tool_calls", [])]})
            elif m["role"] == "tool":
                salida.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
        return salida

    @staticmethod
    def convertir_herramientas(herramientas: list[dict]) -> list[dict]:
        return [{"type": "function", "function": {"name": h["name"], "description": h["description"],
                                                  "parameters": h["parameters"]}} for h in herramientas]

    def interpretar(self, datos: dict) -> dict:
        try:
            eleccion = datos["choices"][0]
            mensaje = eleccion["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ErrorProveedor("respuesta", f"forma inesperada: {str(datos)[:200]}") from exc
        uso = datos.get("usage") or {}
        self.uso["prompt_tokens"] += uso.get("prompt_tokens") or 0
        self.uso["completion_tokens"] += uso.get("completion_tokens") or 0
        llamadas = mensaje.get("tool_calls") or []
        if llamadas:
            propuestas = []
            for tc in llamadas:
                fn = tc.get("function") or {}
                bruto = fn.get("arguments") or ""
                c = {"id": tc.get("id") or f"sin-id-{len(propuestas)}", "name": fn.get("name"), "arguments_raw": bruto}
                try:
                    args = json.loads(bruto) if bruto else {}
                    if not isinstance(args, dict):
                        raise ValueError("no es un objeto")
                    c["arguments"] = args
                except ValueError as exc:
                    # JSON inválido del modelo: se devuelve como error de herramienta, no como excepción
                    c["arguments"] = {}
                    c["error_argumentos"] = f"argumentos no son un objeto JSON válido: {exc}"
                propuestas.append(c)
            return {"type": "tool_calls", "calls": propuestas, "text": mensaje.get("content"),
                    "finish_reason": eleccion.get("finish_reason")}
        return {"type": "final", "text": mensaje.get("content") or "", "finish_reason": eleccion.get("finish_reason")}

    # ------------------------------------------------------------ transporte
    def _post(self, cuerpo: dict) -> dict:
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        cabeceras = {"Content-Type": "application/json"}
        if self.api_key:
            cabeceras["Authorization"] = f"Bearer {self.api_key}"
        ultimo = None
        for intento in range(self.reintentos + 1):
            self.uso["peticiones"] += 1
            peticion = urllib.request.Request(self.url, data=datos, headers=cabeceras, method="POST")
            try:
                with urllib.request.urlopen(peticion, timeout=self.timeout_s) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                cuerpo_error = exc.read().decode("utf-8", errors="replace")[:300]
                ultimo = ErrorProveedor(_clase_http(exc.code), f"HTTP {exc.code}: {cuerpo_error}", exc.code)
                if ultimo.clase not in ("temporal", "cuota") or intento == self.reintentos:
                    raise ultimo from None
                espera = exc.headers.get("Retry-After") if exc.headers else None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                ultimo = ErrorProveedor("red", str(exc))
                if intento == self.reintentos:
                    raise ultimo from None
                espera = None
            except ValueError as exc:
                raise ErrorProveedor("respuesta", f"cuerpo no JSON: {exc}") from None
            time.sleep(min(float(espera) if espera and str(espera).isdigit() else 0.5 * 2 ** intento, 10.0))
        raise ultimo or ErrorProveedor("red", "sin respuesta")

    def next(self, mensajes: list[dict], herramientas: list[dict]) -> dict:
        cuerpo = {"model": self.modelo, "messages": self.convertir_mensajes(mensajes),
                  "tools": self.convertir_herramientas(herramientas), "tool_choice": "auto", **self.extra}
        return self.interpretar(self._post(cuerpo))
