"""Convierte una traza de Pi (JSON mode o RPC) en una fila para score.py.

La evidencia sale de los EVENTOS observados, no de lo que el modelo diga:
- ``tool_calls`` se reconstruye con ``tool_execution_start``/``_end`` por ``toolCallId``;
- ``output`` es el texto del último mensaje del asistente, solo si es un objeto JSON;
- ``meta`` conserva asentamiento, stopReason, errores, turnos, uso y modelo.

Uso:
    python evaluacion/normalizar_pi.py trazas/c01.jsonl --case c01
    python evaluacion/normalizar_pi.py trazas/c01.jsonl --case c01 --salida resultados/manual.jsonl

Admite UTF-8, UTF-8 con BOM y UTF-16 (redirección de Windows PowerShell 5.1).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def decodificar(datos: bytes) -> str:
    if datos.startswith((b"\xff\xfe", b"\xfe\xff")):
        return datos.decode("utf-16")
    return datos.decode("utf-8-sig")


def leer_registros(ruta: str | Path) -> list[dict]:
    registros = []
    texto = decodificar(Path(ruta).read_bytes())
    for n, linea in enumerate(texto.split("\n"), 1):
        linea = linea.rstrip("\r")
        if not linea.strip():
            continue
        try:
            r = json.loads(linea)
        except ValueError as exc:
            raise ValueError(f"{ruta}: JSON inválido en la línea {n}") from exc
        if not isinstance(r, dict):
            raise ValueError(f"{ruta}: la línea {n} no es un objeto")
        registros.append(r)
    return registros


def interpretar_salida(texto: str | None) -> tuple[dict | None, str | None]:
    """Aplica el contrato: la respuesta debe ser SOLO un objeto JSON."""
    if texto is None:
        return None, "sin respuesta final del asistente"
    limpio = texto.strip()
    if not (limpio.startswith("{") and limpio.endswith("}")):
        return None, "la respuesta no es únicamente un objeto JSON"
    try:
        valor = json.loads(limpio)
    except ValueError:
        return None, "JSON mal formado"
    if not isinstance(valor, dict):
        return None, "la respuesta JSON no es un objeto"
    return valor, None


def normalizar(registros: list[dict], case_id: str, meta: dict | None = None) -> dict:
    llamadas: dict[str, dict] = {}
    ultimo_asistente = None
    asentado = False
    turnos = 0
    uso = {"input": 0, "output": 0, "totalTokens": 0, "coste": 0.0}
    sesion = None
    for r in registros:
        tipo = r.get("type")
        if tipo == "session":
            sesion = r.get("id")
        elif tipo == "tool_execution_start":
            args = r.get("args")
            llamadas[r.get("toolCallId", f"sin-id-{len(llamadas)}")] = {
                "id": r.get("toolCallId"), "name": r.get("toolName"),
                "arguments": args if isinstance(args, dict) else {},
                "ok": False, "completada": False, "padre": r.get("parentToolCallId")}
        elif tipo == "tool_execution_end":
            c = llamadas.setdefault(r.get("toolCallId", ""), {
                "id": r.get("toolCallId"), "name": r.get("toolName"), "arguments": {},
                "padre": r.get("parentToolCallId")})
            c["ok"] = r.get("isError") is False
            c["completada"] = True
        elif tipo == "turn_end":
            turnos += 1
        elif tipo == "message_end":
            m = r.get("message") or {}
            if m.get("role") == "assistant":
                ultimo_asistente = m
                u = m.get("usage") or {}
                for k in ("input", "output", "totalTokens"):
                    uso[k] += u.get(k) or 0
                uso["coste"] += ((u.get("cost") or {}).get("total")) or 0.0
        elif tipo == "agent_settled":
            asentado = True
    texto = None
    stop = error = None
    if ultimo_asistente:
        stop = ultimo_asistente.get("stopReason")
        error = ultimo_asistente.get("errorMessage")
        if stop == "stop":
            texto = "".join(b.get("text", "") for b in ultimo_asistente.get("content", [])
                            if b.get("type") == "text")
    salida, error_salida = interpretar_salida(texto)
    if not asentado and error_salida is None:
        salida, error_salida = None, "la ejecución no llegó a agent_settled"
    fila_meta = {
        "asentado": asentado, "stop_reason": stop, "error_modelo": error,
        "error_salida": error_salida, "turnos": turnos, "uso": uso,
        "proveedor": (ultimo_asistente or {}).get("provider"),
        "modelo": (ultimo_asistente or {}).get("model"),
        "sesion": sesion, "texto_final": texto,
    }
    fila_meta.update(meta or {})
    return {"case_id": case_id, "output": salida, "tool_calls": list(llamadas.values()), "meta": fila_meta}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("traza")
    p.add_argument("--case", required=True, dest="case_id")
    p.add_argument("--salida", help="archivo JSONL al que añadir la fila")
    a = p.parse_args()
    try:
        fila = normalizar(leer_registros(a.traza), a.case_id, {"traza": str(a.traza)})
    except (ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 2
    linea = json.dumps(fila, ensure_ascii=False)
    if a.salida:
        Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
        with open(a.salida, "a", encoding="utf-8", newline="\n") as f:
            f.write(linea + "\n")
    print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())
