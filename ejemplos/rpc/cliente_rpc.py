"""Cliente RPC de Pi en Python (solo biblioteca estándar).

Arranca ``pi --mode rpc`` como proceso hijo y aplica el diseño del módulo 08:
- lectores independientes de stdout y stderr (una tubería llena no bloquea al hijo);
- framing JSONL por bytes con ``JsonlDecoder`` (no ``readline`` de texto);
- respuestas correlacionadas por ``id``, nunca por orden de llegada;
- aceptación (``response`` de ``prompt``) distinta de finalización (``agent_settled``);
- plazo con ``abort``, periodo de gracia y terminación del proceso;
- cierre ordenado: cerrar stdin, esperar, ``terminate`` y, en último caso, ``kill``.

Estados del cliente (atributo ``estado``; historial en ``transiciones``):
arrancando -> listo -> aceptado -> ejecutando -> asentado -> listo ...
y los terminales fallido, cancelado, plazo_vencido y cerrado.

Probado offline contra ``pi_falso.py`` y contra Pi 0.99.1 con el modelo de guion.
No es un producto: no gestiona UI de extensiones, colas de steering ni reconexión.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from framing import JsonlDecoder  # noqa: E402

RAIZ_CURSO = Path(__file__).resolve().parents[2]


class ErrorRpc(RuntimeError):
    """Fallo de protocolo o de proceso (no un fallo del modelo)."""


@dataclass
class ResultadoRun:
    estado: str                      # completado | rechazado | manejado | fallido | cancelado | plazo_vencido
    disposicion: str | None = None   # started | queued | handled (según la respuesta de prompt)
    eventos: list = field(default_factory=list)
    texto_final: str | None = None
    stop_reason: str | None = None
    error: str | None = None
    duracion_s: float = 0.0


def resolver_comando_pi() -> list[str]:
    """Devuelve el comando para lanzar Pi.

    ``PI_CMD`` permite fijarlo: una ruta o una lista JSON, p. ej.
    ``["node", "C:/ruta/cli.js"]``. En Windows se prefiere ``node cli.js`` al
    wrapper ``pi.cmd`` para que terminar el proceso no deje un ``node`` huérfano.
    """
    fijado = os.environ.get("PI_CMD")
    if fijado:
        return json.loads(fijado) if fijado.lstrip().startswith("[") else [fijado]
    encontrado = shutil.which("pi")
    if not encontrado:
        raise ErrorRpc("No se encuentra 'pi' en PATH. Instálalo o define PI_CMD.")
    if os.name == "nt" and encontrado.lower().endswith((".cmd", ".ps1", ".bat")):
        cli = Path(encontrado).parent / "node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"
        node = shutil.which("node")
        if cli.exists() and node:
            return [node, str(cli)]
    return [encontrado]


class ClientePiRpc:
    def __init__(self, argumentos: list[str], comando: list[str] | None = None,
                 cwd: str | os.PathLike | None = None, env: dict | None = None,
                 gracia_s: float = 5.0):
        self.comando = (comando or resolver_comando_pi()) + ["--mode", "rpc"] + list(argumentos)
        self.cwd = cwd
        self.env = env
        self.gracia_s = gracia_s
        self.estado = "creado"
        self.transiciones: list[tuple[float, str]] = []
        self.eventos: list[dict] = []          # eventos de sesión (sin respuestas)
        self.registros: list[dict] = []        # todo lo recibido por stdout, en orden
        self.errores_protocolo: list[str] = []
        self._stderr = collections.deque(maxlen=200)
        self._pendientes: dict[str, dict] = {}
        self._cond = threading.Condition()
        self._ids = itertools.count(1)
        self._eof = False
        self._proc: subprocess.Popen | None = None
        self._hilos: list[threading.Thread] = []
        self._t0 = time.monotonic()

    # ------------------------------------------------------------------ estado
    def _pasar(self, estado: str):
        self.estado = estado
        self.transiciones.append((round(time.monotonic() - self._t0, 3), estado))

    @property
    def stderr(self) -> str:
        return "".join(self._stderr)

    # ------------------------------------------------------------------ proceso
    def iniciar(self, plazo_s: float = 30.0) -> dict:
        self._pasar("arrancando")
        try:
            self._proc = subprocess.Popen(
                self.comando, cwd=self.cwd, env=self.env, bufsize=0,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            self._pasar("fallido")
            raise ErrorRpc(f"No se pudo arrancar Pi: {exc}") from exc
        for destino in (self._leer_stdout, self._leer_stderr):
            hilo = threading.Thread(target=destino, daemon=True)
            hilo.start()
            self._hilos.append(hilo)
        estado = self.enviar({"type": "get_state"}, plazo_s=plazo_s)
        if not estado.get("success"):
            self._pasar("fallido")
            raise ErrorRpc(f"get_state rechazado: {estado.get('error')}")
        self._pasar("listo")
        return estado.get("data") or {}

    def _leer_stdout(self):
        decoder = JsonlDecoder(tolerante=True)
        assert self._proc and self._proc.stdout
        while True:
            chunk = self._proc.stdout.read(65536)
            if not chunk:
                break
            registros = decoder.feed(chunk)
            with self._cond:
                self.errores_protocolo.extend(decoder.errores)
                decoder.errores.clear()
                for r in registros:
                    self.registros.append(r)
                    if r.get("type") == "response":
                        rid = r.get("id")
                        if isinstance(rid, str) and rid in self._pendientes:
                            self._pendientes[rid] = r
                        else:
                            self.errores_protocolo.append(f"Respuesta sin petición pendiente: {json.dumps(r)[:200]}")
                    else:
                        self.eventos.append(r)
                self._cond.notify_all()
        decoder.finish()
        with self._cond:
            self.errores_protocolo.extend(decoder.errores)
            self._eof = True
            self._cond.notify_all()

    def _leer_stderr(self):
        assert self._proc and self._proc.stderr
        while True:
            chunk = self._proc.stderr.read(65536)
            if not chunk:
                break
            self._stderr.append(chunk.decode("utf-8", errors="replace"))

    # ---------------------------------------------------------------- comandos
    def enviar(self, comando: dict, plazo_s: float = 10.0) -> dict:
        """Envía un comando y espera SU respuesta (correlación por id)."""
        if not self._proc or not self._proc.stdin:
            raise ErrorRpc("El proceso no está iniciado")
        comando = dict(comando)
        rid = comando.setdefault("id", f"req-{next(self._ids)}")
        with self._cond:
            if self._eof:
                raise ErrorRpc("Pi ya cerró stdout")
            self._pendientes[rid] = {}
        linea = json.dumps(comando, ensure_ascii=False).encode("utf-8") + b"\n"
        try:
            self._proc.stdin.write(linea)
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise ErrorRpc(f"No se pudo escribir en stdin: {exc}") from exc
        limite = time.monotonic() + plazo_s
        with self._cond:
            while not self._pendientes[rid] and not self._eof:
                restante = limite - time.monotonic()
                if restante <= 0:
                    del self._pendientes[rid]
                    raise TimeoutError(f"Sin respuesta a {comando['type']} ({rid}) en {plazo_s}s")
                self._cond.wait(restante)
            respuesta = self._pendientes.pop(rid)
        if not respuesta:
            raise ErrorRpc(f"Pi terminó antes de responder a {comando['type']}. stderr: {self.stderr[-500:]}")
        return respuesta

    def _esperar_evento(self, desde: int, tipo: str, plazo_s: float) -> bool:
        limite = time.monotonic() + plazo_s
        with self._cond:
            while True:
                if any(e.get("type") == tipo for e in self.eventos[desde:]):
                    return True
                if self._eof:
                    return False
                restante = limite - time.monotonic()
                if restante <= 0:
                    return False
                self._cond.wait(restante)

    def ejecutar_prompt(self, mensaje: str, plazo_s: float = 120.0) -> ResultadoRun:
        """Envía un prompt y espera a ``agent_settled`` o al plazo."""
        t0 = time.monotonic()
        with self._cond:
            desde = len(self.eventos)  # "suscribirse" antes de enviar: no se pierde un final rápido
        try:
            respuesta = self.enviar({"type": "prompt", "message": mensaje}, plazo_s=min(plazo_s, 30.0))
        except (ErrorRpc, TimeoutError) as exc:
            self._pasar("fallido")
            return ResultadoRun("fallido", error=str(exc), duracion_s=time.monotonic() - t0)
        if not respuesta.get("success"):
            return ResultadoRun("rechazado", error=respuesta.get("error"), duracion_s=time.monotonic() - t0)
        disposicion = (respuesta.get("data") or {}).get("disposition")
        if disposicion == "handled":  # ningún run empezó: no hay agent_settled que esperar
            return ResultadoRun("manejado", disposicion, duracion_s=time.monotonic() - t0)
        self._pasar("aceptado")
        self._pasar("ejecutando")
        restante = plazo_s - (time.monotonic() - t0)
        asentado = self._esperar_evento(desde, "agent_settled", max(0.0, restante))
        estado = None
        if not asentado and not self._eof:
            estado = "plazo_vencido"
            try:
                self.enviar({"type": "abort"}, plazo_s=self.gracia_s)
            except (ErrorRpc, TimeoutError) as exc:
                self.errores_protocolo.append(f"abort sin respuesta: {exc}")
            self._esperar_evento(desde, "agent_settled", self.gracia_s)
        with self._cond:
            eventos = list(self.eventos[desde:])
        final = next((e["message"] for e in reversed(eventos)
                      if e.get("type") == "message_end" and (e.get("message") or {}).get("role") == "assistant"), None)
        texto = stop = error = None
        if final:
            stop = final.get("stopReason")
            error = final.get("errorMessage")
            texto = "".join(b.get("text", "") for b in final.get("content", []) if b.get("type") == "text") or None
        if estado is None:
            if not asentado:
                estado, error = "fallido", error or f"Pi terminó sin agent_settled. stderr: {self.stderr[-500:]}"
            elif stop == "aborted":
                estado = "cancelado"
            elif stop == "error":
                estado = "fallido"
            else:
                estado = "completado"
        self._pasar("asentado" if estado == "completado" else estado)
        if estado == "completado":
            self._pasar("listo")
        return ResultadoRun(estado, disposicion, eventos, texto, stop, error, time.monotonic() - t0)

    # ------------------------------------------------------------------ cierre
    def cerrar(self, plazo_s: float | None = None) -> int | None:
        plazo_s = self.gracia_s if plazo_s is None else plazo_s
        if not self._proc:
            return None
        try:
            if self._proc.stdin and not self._proc.stdin.closed:
                self._proc.stdin.close()  # petición de cierre ordenado
        except OSError:
            pass
        for accion in (None, self._proc.terminate, self._proc.kill):
            if accion:
                accion()
            try:
                self._proc.wait(timeout=plazo_s)
                break
            except subprocess.TimeoutExpired:
                continue
        for hilo in self._hilos:
            hilo.join(timeout=2)
        for flujo in (self._proc.stdout, self._proc.stderr):
            if flujo:
                flujo.close()
        self._pasar("cerrado")
        return self._proc.returncode

    def __enter__(self):
        self.iniciar()
        return self

    def __exit__(self, *exc):
        self.cerrar()


def argumentos_guion(modo: str = "correcto", plantilla: bool = True) -> list[str]:
    """Argumentos de Pi para practicar sin credenciales con el modelo de guion."""
    base = RAIZ_CURSO / "ejemplos" / "pi-package"
    args = ["--no-session", "-ne", "-ns", "-np", "-nc", "--offline",
            "-e", str(base / "dobles" / "modelo-guion.ts"),
            "-e", str(base / "extensions" / "catalogue.ts"),
            "--tools", "lookup_document", "--provider", "curso", "--model", "guion", "--guion", modo]
    if plantilla:
        args += ["--prompt-template", str(base / "prompts" / "respuesta-documental.md")]
    return args


def main():
    p = argparse.ArgumentParser(description="Demostración del cliente RPC de Pi")
    p.add_argument("mensaje")
    p.add_argument("--guion", metavar="MODO", help="usar el modelo de guion (sin credenciales)")
    p.add_argument("--sin-plantilla", action="store_true")
    p.add_argument("--plazo", type=float, default=60.0)
    p.add_argument("pi_args", nargs=argparse.REMAINDER, help="argumentos adicionales de Pi tras --")
    a = p.parse_args()
    extra = [x for x in a.pi_args if x != "--"]
    args = (argumentos_guion(a.guion, not a.sin_plantilla) if a.guion else []) + extra
    env = dict(os.environ)
    if a.guion:
        env.setdefault("PI_CODING_AGENT_DIR", str(RAIZ_CURSO / ".pi-curso" / "agente"))
    mensaje = a.mensaje if a.sin_plantilla or not a.guion else f"/respuesta-documental {a.mensaje}"
    cliente = ClientePiRpc(args, cwd=RAIZ_CURSO, env=env)
    try:
        estado = cliente.iniciar()
        modelo = estado.get("model") or {}
        print(json.dumps({"modelo": f"{modelo.get('provider')}/{modelo.get('id')}"}, ensure_ascii=False), file=sys.stderr)
        r = cliente.ejecutar_prompt(mensaje, plazo_s=a.plazo)
        llamadas = [(e["toolName"], not e.get("isError")) for e in r.eventos if e.get("type") == "tool_execution_end"]
        print(json.dumps({"estado": r.estado, "disposicion": r.disposicion, "stop_reason": r.stop_reason,
                          "llamadas": llamadas, "texto_final": r.texto_final, "error": r.error,
                          "duracion_s": round(r.duracion_s, 3)}, ensure_ascii=False, indent=2))
        return 0 if r.estado == "completado" else 1
    except (ErrorRpc, TimeoutError) as exc:
        print(f"Error: {exc}\nstderr: {cliente.stderr[-1000:]}", file=sys.stderr)
        return 2
    finally:
        cliente.cerrar()
        print(json.dumps({"transiciones": cliente.transiciones}), file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
