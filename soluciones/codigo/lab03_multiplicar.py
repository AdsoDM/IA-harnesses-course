"""Solución de referencia del laboratorio 03: añadir ``multiplicar`` sin ``eval``.

Cambio de diseño respecto a harness.py: el dispatcher usa un REGISTRO de
herramientas (nombre -> función validadora). Añadir una herramienta no toca el
bucle y un nombre desconocido sigue rechazándose antes de cualquier efecto.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ejemplos" / "mini-harness"))
from harness import sumar  # noqa: E402  reutiliza la validación existente

LIMITE = 1_000_000


def multiplicar(args: dict) -> dict:
    if not isinstance(args, dict) or set(args) != {"a", "b"}:
        raise ValueError("Se requieren exactamente a y b")
    if any(type(args[k]) is not int for k in ("a", "b")):  # excluye bool, float y texto
        raise ValueError("a y b deben ser enteros, no bool ni texto")
    if any(abs(args[k]) > LIMITE for k in ("a", "b")):
        raise ValueError("Argumento fuera del límite didáctico")
    return {"value": args["a"] * args["b"]}


HERRAMIENTAS = {"sumar": sumar, "multiplicar": multiplicar}


class ModeloMultiplica:
    """Doble de prueba: pide multiplicar y después responde con el resultado."""

    def __init__(self, args=None):
        self.args = args if args is not None else {"a": 6, "b": 7}

    def next(self, messages):
        resultados = [m for m in messages if m["role"] == "tool"]
        if resultados:
            r = resultados[-1]["result"]
            return {"type": "final", "answer": str(r["data"]["value"]) if r["ok"] else "No pude ejecutar: " + r["error"]}
        return {"type": "tool_call", "id": "call-1", "name": "multiplicar", "arguments": self.args}


def run(model, herramientas=HERRAMIENTAS, max_steps=4):
    """Mismo contrato que harness.run, con registro de herramientas."""
    run_id = str(uuid.uuid4())
    messages, trace, usados = [{"role": "user", "content": "calcula"}], [], set()
    for step in range(1, max_steps + 1):
        p = model.next(messages)
        trace.append({"run_id": run_id, "step": step, "event": "proposal", "data": p})
        if p.get("type") == "final":
            if set(p) != {"type", "answer"} or not isinstance(p["answer"], str) or not p["answer"].strip():
                return {"status": "invalid_final", "trace": trace}
            return {"status": "completed", "answer": p["answer"], "trace": trace}
        if p.get("type") != "tool_call" or set(p) != {"type", "id", "name", "arguments"} or p["id"] in usados:
            return {"status": "invalid_proposal", "trace": trace}
        usados.add(p["id"])
        funcion = herramientas.get(p["name"])
        try:
            if funcion is None:
                raise ValueError("Herramienta no permitida")
            result = {"ok": True, "data": funcion(p["arguments"])}
        except ValueError as exc:
            result = {"ok": False, "error": str(exc)}
        messages += [{"role": "assistant", "proposal": p}, {"role": "tool", "tool_call_id": p["id"], "result": result}]
        trace.append({"run_id": run_id, "step": step, "event": "tool_result", "tool_call_id": p["id"], "result": result})
    return {"status": "step_limit", "trace": trace}
