"""Comprueba enlaces locales inline, JSON/JSONL, balance de fences y estructura de lecciones."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
errors = []
excluir = {"node_modules", ".venv", ".pi-curso", "trazas", "resultados"}
mds = [p for p in root.rglob("*.md") if not excluir.intersection(p.parts)]
for path in mds:
    text = path.read_text(encoding="utf-8")
    in_fence = False
    for n,line in enumerate(text.splitlines(),1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence: continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',line):
            target = link.split('#')[0]
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target): continue
            target = unquote(target)
            if not (path.parent/target).exists():
                errors.append(f"{path.relative_to(root)}:{n}: enlace inexistente {target}")
    if in_fence: errors.append(f"{path.relative_to(root)}: fence sin cerrar")
# Estructura mínima: cada lección tiene autoevaluación y laboratorio, y cada laboratorio vuelve a su lección.
for leccion in sorted((root/"docs").glob("[01][0-9]*.md")):
    if leccion.name == "00-programa.md": continue
    texto = leccion.read_text(encoding="utf-8")
    if "## Autoevaluación" not in texto:
        errors.append(f"docs/{leccion.name}: falta la sección Autoevaluación")
    if "../laboratorios/" not in texto:
        errors.append(f"docs/{leccion.name}: no enlaza su laboratorio")
for lab in sorted((root/"laboratorios").glob("*.md")):
    if "../docs/" not in lab.read_text(encoding="utf-8"):
        errors.append(f"laboratorios/{lab.name}: no enlaza su lección")
for path in list(root.rglob("*.json"))+list(root.rglob("*.jsonl")):
    if excluir.intersection(path.parts): continue
    try:
        data = path.read_text(encoding="utf-8-sig")
        if path.suffix == '.json': json.loads(data)
        else:
            for line in data.split('\n'):
                if line.strip(): json.loads(line)
    except Exception as exc: errors.append(f"{path.relative_to(root)}: {exc}")
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f"OK: {len(mds)} documentos Markdown; enlaces locales, fences y JSON válidos")
