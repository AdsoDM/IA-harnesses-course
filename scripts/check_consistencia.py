"""Comprueba que los hechos del curso cambian juntos (véase MANTENIMIENTO.md).

- El catálogo JavaScript (shared/catalogue.mjs) y el de Python (catalogo.json) son idénticos.
- Los casos solo citan documentos existentes y tienen un contrato válido.
- La fixture de resultados cubre los mismos casos.
- La plantilla menciona todos los IDs y las configuraciones apuntan a archivos reales.
Requiere Node para comparar el catálogo JS; sin Node, esa parte se omite con aviso.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errores, avisos = [], []


def jsonl(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


py_docs = {d["doc_id"]: d for d in json.loads((RAIZ / "ejemplos/mini-harness/catalogo.json").read_text(encoding="utf-8"))}
ids = set(py_docs)

node = shutil.which("node")
if node:
    script = ("const m = await import(process.argv[1]);"
              "const out = {};"
              "for (const id of ['d-000','d-001','d-002','d-003','d-004','d-005']) {"
              "  try { out[id] = m.lookupDocument({doc_id: id}); } catch (e) { out[id] = null; } }"
              "console.log(JSON.stringify(out));")
    modulo = (RAIZ / "ejemplos/pi-package/shared/catalogue.mjs").resolve().as_uri()
    r = subprocess.run([node, "--input-type=module", "-e", script, modulo], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        errores.append(f"No se pudo cargar catalogue.mjs: {r.stderr.strip()[:300]}")
    else:
        js = {k: v for k, v in json.loads(r.stdout).items() if v is not None}
        if js != py_docs:
            errores.append(f"catalogue.mjs y catalogo.json difieren: JS={sorted(js)} PY={sorted(py_docs)}"
                           + ("" if set(js) != set(py_docs) else " (mismo conjunto de IDs, distinto contenido)"))
else:
    avisos.append("Node no disponible: no se ha comparado catalogue.mjs con catalogo.json")

casos = jsonl(RAIZ / "evaluacion/casos.jsonl")
vistos = set()
for c in casos:
    cid = c.get("id")
    if cid in vistos:
        errores.append(f"Caso duplicado: {cid}")
    vistos.add(cid)
    if c.get("split") not in {"dev", "holdout"}:
        errores.append(f"{cid}: split inválido")
    if c.get("status") not in {"answered", "abstained", "blocked"}:
        errores.append(f"{cid}: status inválido")
    for campo in ("sources", "required_calls", "allowed_sources"):
        desconocidos = set(c.get(campo, [])) - ids
        if desconocidos:
            errores.append(f"{cid}: {campo} cita documentos inexistentes {sorted(desconocidos)}")
    if c.get("status") == "blocked" and (c.get("sources") or c.get("required_calls")):
        errores.append(f"{cid}: un caso bloqueado no debería exigir fuentes ni consultas")
demo = {r["case_id"] for r in jsonl(RAIZ / "evaluacion/resultados-demo.jsonl")}
if demo != vistos:
    errores.append(f"resultados-demo no cubre los mismos casos: {sorted(demo ^ vistos)}")

plantilla = (RAIZ / "ejemplos/pi-package/prompts/respuesta-documental.md").read_text(encoding="utf-8")
for i in sorted(ids):
    if i not in plantilla:
        errores.append(f"La plantilla no menciona {i}")

for cfg_ruta in sorted((RAIZ / "evaluacion/configuraciones").glob("*.json")):
    cfg = json.loads(cfg_ruta.read_text(encoding="utf-8"))
    args = cfg.get("pi_args", [])
    for i, a in enumerate(args[:-1]):
        if a in ("-e", "--extension", "--prompt-template", "--append-system-prompt", "--skill"):
            if not (RAIZ / args[i + 1]).exists():
                errores.append(f"{cfg_ruta.name}: no existe {args[i + 1]}")

for a in avisos:
    print(f"AVISO: {a}")
if errores:
    print("\n".join(errores))
    sys.exit(1)
print(f"OK: {len(ids)} documentos, {len(casos)} casos, fixture y configuraciones coherentes")
