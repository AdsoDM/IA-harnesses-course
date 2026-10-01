"""Harness didáctico offline. Modelo simulado: no llama a una API."""
from __future__ import annotations
import argparse
import json
import uuid


def sumar(args: dict) -> dict:
    if not isinstance(args, dict) or set(args) != {"a", "b"}:
        raise ValueError("Se requieren exactamente a y b")
    if any(type(args[k]) is not int for k in ("a", "b")):
        raise ValueError("a y b deben ser enteros, no bool ni texto")
    if any(abs(args[k]) > 1_000_000 for k in ("a", "b")):
        raise ValueError("Argumento fuera del límite didáctico")
    return {"value": args["a"] + args["b"]}


class MockModel:
    def __init__(self, scenario="normal"):
        self.scenario = scenario

    def next(self, messages):
        results = [m for m in messages if m["role"] == "tool"]
        if results and self.scenario != "loop":
            result = results[-1]["result"]
            answer = str(result["data"]["value"]) if result["ok"] else "No pude ejecutar: " + result["error"]
            return {"type": "final", "answer": answer}
        args = {"a": "2", "b": 3} if self.scenario == "invalid" else {"a": 2, "b": 3}
        return {"type": "tool_call", "id": f"call-{len(results)+1}", "name": "sumar", "arguments": args}


def run(model, user_input="Suma 2 y 3", max_steps=4):
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("max_steps debe ser un entero positivo")
    run_id = str(uuid.uuid4())
    messages = [{"role": "user", "content": user_input}]
    trace = [{"run_id": run_id, "step": 0, "event": "input", "content": user_input}]
    used_ids = set()
    for step in range(1, max_steps + 1):
        try:
            proposal = model.next(messages)
        except Exception as exc:
            trace.append({"run_id": run_id, "step": step, "event": "model_error", "error": str(exc)})
            return {"status": "model_error", "trace": trace}
        trace.append({"run_id": run_id, "step": step, "event": "proposal", "data": proposal})
        if not isinstance(proposal, dict):
            return {"status": "invalid_proposal", "trace": trace}
        if proposal.get("type") == "final":
            if set(proposal) != {"type", "answer"} or not isinstance(proposal["answer"], str) or not proposal["answer"].strip():
                return {"status": "invalid_final", "trace": trace}
            trace.append({"run_id": run_id, "step": step, "event": "completed"})
            return {"status": "completed", "answer": proposal["answer"], "trace": trace}
        if proposal.get("type") != "tool_call" or set(proposal) != {"type", "id", "name", "arguments"}:
            return {"status": "invalid_proposal", "trace": trace}
        call_id = proposal["id"]
        if not isinstance(call_id, str) or not call_id or call_id in used_ids:
            return {"status": "invalid_call_id", "trace": trace}
        used_ids.add(call_id)
        try:
            if proposal["name"] != "sumar":
                raise ValueError("Herramienta no permitida")
            result = {"ok": True, "data": sumar(proposal["arguments"])}
        except ValueError as exc:
            result = {"ok": False, "error": str(exc)}
        messages.append({"role": "assistant", "proposal": proposal})
        messages.append({"role": "tool", "tool_call_id": call_id, "result": result})
        trace.append({"run_id": run_id, "step": step, "event": "tool_result", "tool_call_id": call_id, "result": result})
    trace.append({"run_id": run_id, "step": max_steps, "event": "step_limit"})
    return {"status": "step_limit", "trace": trace}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["normal", "invalid", "loop"], default="normal")
    parser.add_argument("--max-steps", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(run(MockModel(args.scenario), max_steps=args.max_steps), ensure_ascii=False, indent=2))
