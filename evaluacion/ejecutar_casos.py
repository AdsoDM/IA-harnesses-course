"""Ejecuta los casos de evaluación contra Pi y produce resultados normalizados.

Cada caso (y cada repetición) usa un proceso Pi nuevo en modo RPC, con sesión
efímera. Se guardan la traza completa, la fila normalizada y la criba de score.py.

    python evaluacion/ejecutar_casos.py --config evaluacion/configuraciones/B-guion.json
    python evaluacion/ejecutar_casos.py --config evaluacion/configuraciones/A-guion.json --split dev
    python evaluacion/ejecutar_casos.py --config evaluacion/configuraciones/B-real.json --repeticiones 3 --plazo 180
    python evaluacion/ejecutar_casos.py --config evaluacion/configuraciones/B-guion.json --guion memoria
    python evaluacion/ejecutar_casos.py --config ... --simular      # muestra comandos sin ejecutar

Salidas (ignoradas por Git): trazas/<nombre>-r<k>/<caso>.jsonl,
resultados/<nombre>-r<k>.jsonl y resultados/<nombre>-r<k>.score.json.
Código de salida: 0 todos pasan la criba, 1 algún fallo, 2 error de configuración.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ejemplos" / "rpc"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cliente_rpc import ClientePiRpc, ErrorRpc, resolver_comando_pi  # noqa: E402
from normalizar_pi import normalizar  # noqa: E402
from score import evaluate, load_jsonl  # noqa: E402

CLAVES = {"nombre", "descripcion", "pi_args", "prompt", "entorno", "agente_aislado"}


def cargar_config(ruta: Path) -> dict:
    cfg = json.loads(ruta.read_text(encoding="utf-8"))
    faltan = {"nombre", "pi_args", "prompt"} - set(cfg)
    extra = set(cfg) - CLAVES
    if faltan or extra:
        raise ValueError(f"Configuración inválida: faltan {sorted(faltan)}, sobran {sorted(extra)}")
    if "{pregunta}" not in cfg["prompt"]:
        raise ValueError("'prompt' debe contener {pregunta}")
    if any("REEMPLAZAR" in str(x) for x in cfg["pi_args"]):
        raise ValueError("Sustituye los valores REEMPLAZAR (proveedor/modelo) antes de ejecutar")
    if not all(isinstance(x, str) for x in cfg["pi_args"]):
        raise ValueError("pi_args debe ser una lista de cadenas")
    return cfg


def version_pi(comando: list[str], env: dict) -> str:
    try:
        r = subprocess.run(comando + ["--version"], capture_output=True, text=True, timeout=30,
                           env=env, stdin=subprocess.DEVNULL)
        return (r.stdout or r.stderr).strip() or f"desconocida (código {r.returncode})"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"no disponible: {exc}"


def commit_actual() -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return None
        sucio = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() + ("+cambios" if sucio.stdout.strip() else "")
    except (OSError, subprocess.TimeoutExpired):
        return None


def ejecutar_caso(caso: dict, cfg: dict, comando: list[str], env: dict, plazo: float) -> tuple[list[dict], dict]:
    mensaje = cfg["prompt"].replace("{pregunta}", caso["question"])
    cliente = ClientePiRpc(cfg["pi_args"], comando=comando, cwd=RAIZ, env=env)
    t0 = time.monotonic()
    meta = {"estado_rpc": None, "error_rpc": None}
    try:
        cliente.iniciar()
        r = cliente.ejecutar_prompt(mensaje, plazo_s=plazo)
        meta.update(estado_rpc=r.estado, error_rpc=r.error)
    except (ErrorRpc, TimeoutError) as exc:
        meta.update(estado_rpc="fallido", error_rpc=str(exc))
    finally:
        codigo = cliente.cerrar()
    meta.update(duracion_s=round(time.monotonic() - t0, 3), codigo_salida=codigo,
                transiciones=cliente.transiciones, errores_protocolo=cliente.errores_protocolo[:20])
    if cliente.stderr.strip():
        meta["stderr_final"] = cliente.stderr[-2000:]
    return cliente.registros, meta


def main() -> int:
    p = argparse.ArgumentParser(description="Runner de evaluación del curso")
    p.add_argument("--config", required=True)
    p.add_argument("--casos-archivo", default=str(RAIZ / "evaluacion" / "casos.jsonl"))
    p.add_argument("--split", choices=["all", "dev", "holdout"], default="all")
    p.add_argument("--casos", help="IDs separados por comas, p. ej. c01,c05")
    p.add_argument("--repeticiones", type=int, default=1)
    p.add_argument("--plazo", type=float, default=120.0, help="segundos por caso")
    p.add_argument("--guion", help="modo del modelo de guion (auto, memoria, json-roto, bucle, lento, obediente...)")
    p.add_argument("--directorio", default=str(RAIZ), help="base para trazas/ y resultados/")
    p.add_argument("--simular", action="store_true")
    a = p.parse_args()

    try:
        cfg = cargar_config(Path(a.config))
        casos = load_jsonl(a.casos_archivo)
        if a.split != "all":
            casos = [c for c in casos if c["split"] == a.split]
        if a.casos:
            pedidos = [x.strip() for x in a.casos.split(",") if x.strip()]
            desconocidos = set(pedidos) - {c["id"] for c in casos}
            if desconocidos:
                raise ValueError(f"Casos desconocidos o fuera del split: {sorted(desconocidos)}")
            casos = [c for c in casos if c["id"] in pedidos]
        if not casos or a.repeticiones < 1:
            raise ValueError("No hay casos que ejecutar o repeticiones < 1")
        comando = resolver_comando_pi()
    except (ValueError, OSError, ErrorRpc) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    env = dict(os.environ)
    env.update(cfg.get("entorno") or {})
    if a.guion:
        env["CURSO_GUION"] = a.guion
        cfg["nombre"] = f"{cfg['nombre']}-{a.guion}"
    if cfg.get("agente_aislado"):
        env.setdefault("PI_CODING_AGENT_DIR", str(RAIZ / ".pi-curso" / "agente"))
    if a.simular:
        for c in casos:
            print(json.dumps({"caso": c["id"], "comando": comando + ["--mode", "rpc"] + cfg["pi_args"],
                              "prompt": cfg["prompt"].replace("{pregunta}", c["question"])}, ensure_ascii=False))
        return 0

    comun = {"config": cfg["nombre"], "pi_version": version_pi(comando, env), "commit": commit_actual(),
             "fecha": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    peor = 0
    for rep in range(1, a.repeticiones + 1):
        etiqueta = f"{cfg['nombre']}-{a.split}-r{rep}"
        base = Path(a.directorio)
        dir_trazas = base / "trazas" / etiqueta
        dir_trazas.mkdir(parents=True, exist_ok=True)
        salida = base / "resultados" / f"{etiqueta}.jsonl"
        salida.parent.mkdir(parents=True, exist_ok=True)
        filas = []
        for caso in casos:
            registros, meta = ejecutar_caso(caso, cfg, comando, env, a.plazo)
            traza = dir_trazas / f"{caso['id']}.jsonl"
            cabecera = {"type": "curso_ejecucion", "caso": caso["id"], "repeticion": rep, **comun}
            with open(traza, "w", encoding="utf-8", newline="\n") as f:
                for r in [cabecera, *registros]:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            fila = normalizar(registros, caso["id"], {**comun, **meta, "repeticion": rep,
                                                       "traza": traza.relative_to(base).as_posix()})
            filas.append(fila)
            estado = "ok " if fila["output"] else "err"
            print(f"[{etiqueta}] {caso['id']} {estado} rpc={meta['estado_rpc']} "
                  f"llamadas={len(fila['tool_calls'])} {meta['duracion_s']}s", file=sys.stderr)
        with open(salida, "w", encoding="utf-8", newline="\n") as f:
            for fila in filas:
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        informe = evaluate(casos, filas)
        informe["config"] = comun
        (salida.with_suffix(".score.json")).write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        t = informe["totals"]
        print(json.dumps({"repeticion": rep, "resultados": salida.relative_to(base).as_posix(),
                          "aprobados": f"{t['passed']}/{informe['total']}", "totales": t}, ensure_ascii=False))
        if t["passed"] != informe["total"]:
            peor = 1
    return peor


if __name__ == "__main__":
    sys.exit(main())
