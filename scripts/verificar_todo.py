"""Ejecuta todas las comprobaciones del curso y resume el resultado.

    python scripts/verificar_todo.py            # offline: Python, Node, documentación, consistencia
    python scripts/verificar_todo.py --con-pi   # además, batería A/B real con Pi y el modelo de guion
    python scripts/verificar_todo.py --con-tipos  # además, tsc en ejemplos/pi-package y ejemplos/sdk
                                                  # (requiere npm install previo en cada carpeta)

Ninguna comprobación llama a un proveedor ni necesita credenciales. Las salidas
de --con-pi se escriben en un directorio temporal que se borra al terminar.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
resultados: list[tuple[str, bool, str]] = []


def paso(nombre: str, comando: list[str], cwd: Path = RAIZ, env: dict | None = None, esperado: int = 0) -> subprocess.CompletedProcess | None:
    t0 = time.monotonic()
    try:
        r = subprocess.run(comando, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, timeout=600, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as exc:
        resultados.append((nombre, False, str(exc)))
        return None
    ok = r.returncode == esperado
    detalle = f"{time.monotonic() - t0:.1f}s"
    if not ok:
        detalle += " | " + (r.stdout + r.stderr).strip().splitlines()[-1][:200] if (r.stdout + r.stderr).strip() else ""
    resultados.append((nombre, ok, detalle))
    return r


def main() -> int:
    p = argparse.ArgumentParser(description="Comprobaciones del curso")
    p.add_argument("--con-pi", action="store_true")
    p.add_argument("--con-tipos", action="store_true")
    a = p.parse_args()
    py = sys.executable
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    for carpeta in ("ejemplos/mini-harness", "ejemplos/rpc", "evaluacion", "soluciones/codigo"):
        paso(f"unittest {carpeta}", [py, "-m", "unittest", "discover", "-s", carpeta, "-t", carpeta], env=env)
    node = shutil.which("node")
    if node:
        paso("node --test catálogo", [node, "--test", "ejemplos/pi-package/tests/catalogue.test.mjs"])
        paso("node --test search (solución)", [node, "--test", "soluciones/codigo/search.test.mjs"])
    else:
        resultados.append(("node --test", False, "Node no encontrado"))
    paso("check_docs", [py, "scripts/check_docs.py"], env=env)
    paso("check_consistencia", [py, "scripts/check_consistencia.py"], env=env)
    paso("score fixture 12/12", [py, "evaluacion/score.py", "evaluacion/resultados-demo.jsonl"], env=env)

    if a.con_tipos:
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        for carpeta in ("ejemplos/pi-package", "ejemplos/sdk"):
            if not (RAIZ / carpeta / "node_modules").exists():
                resultados.append((f"tsc {carpeta}", False, "falta node_modules: ejecuta npm install --ignore-scripts"))
            elif npm:
                paso(f"tsc {carpeta}", [npm, "run", "check"], cwd=RAIZ / carpeta)

    if a.con_pi:
        with tempfile.TemporaryDirectory(prefix="curso-pi-") as tmp:
            env_pi = dict(env)
            env_pi.setdefault("PI_CODING_AGENT_DIR", str(Path(tmp) / "agente"))
            for cfg, esperado in (("A-guion", 3), ("B-guion", 12)):
                r = paso(f"Pi real {cfg}", [py, "evaluacion/ejecutar_casos.py", "--config",
                                            f"evaluacion/configuraciones/{cfg}.json", "--directorio", tmp],
                         env=env_pi, esperado=0 if esperado == 12 else 1)
                if r is None:
                    continue
                try:
                    aprobados = json.loads(r.stdout.strip().splitlines()[-1])["aprobados"]
                except (ValueError, IndexError, KeyError):
                    aprobados = "?"
                nombre, ok, detalle = resultados.pop()
                ok = ok and aprobados == f"{esperado}/12"
                resultados.append((nombre, ok, f"{aprobados} (esperado {esperado}/12) {detalle}"))

    ancho = max(len(n) for n, _, _ in resultados)
    for nombre, ok, detalle in resultados:
        print(f"{'OK ' if ok else 'ERR'}  {nombre.ljust(ancho)}  {detalle}")
    fallos = sum(not ok for _, ok, _ in resultados)
    print(f"\n{len(resultados) - fallos}/{len(resultados)} comprobaciones correctas")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
