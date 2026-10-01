"""Pruebas offline del runner con el Pi FALSO (ejemplos/rpc/pi_falso.py).

El falso responde siempre {"saludo":"año"}: los casos deben FALLAR la criba.
Se comprueba el flujo (procesos, trazas, filas, código de salida), no un modelo.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RUNNER = AQUI / "ejecutar_casos.py"
FALSO = RAIZ / "ejemplos" / "rpc" / "pi_falso.py"


def ejecutar(*args, env_extra=None):
    env = dict(os.environ, PI_CMD=json.dumps([sys.executable, str(FALSO), "normal"]))
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(RUNNER), *args], capture_output=True, text=True,
                          env=env, timeout=120, stdin=subprocess.DEVNULL)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.cfg = self.dir / "cfg.json"
        self.cfg.write_text(json.dumps({"nombre": "prueba", "pi_args": ["--no-session"],
                                        "prompt": "{pregunta}"}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_flujo_completo_con_pi_falso(self):
        r = ejecutar("--config", str(self.cfg), "--casos", "c01,c06", "--directorio", str(self.dir))
        self.assertEqual(r.returncode, 1, r.stderr)  # el falso no cumple el contrato
        filas = [json.loads(l) for l in (self.dir / "resultados" / "prueba-all-r1.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([f["case_id"] for f in filas], ["c01", "c06"])
        self.assertTrue(all(f["meta"]["estado_rpc"] == "completado" for f in filas))
        # El normalizador acepta cualquier objeto JSON; es score.py quien exige el contrato.
        self.assertTrue(all(f["output"] == {"saludo": "año"} for f in filas))
        traza = (self.dir / "trazas" / "prueba-all-r1" / "c01.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(json.loads(traza[0])["type"], "curso_ejecucion")
        informe = json.loads((self.dir / "resultados" / "prueba-all-r1.score.json").read_text(encoding="utf-8"))
        self.assertEqual(informe["totals"]["passed"], 0)
        self.assertEqual(informe["totals"]["contract"], 0)

    def test_placeholder_rechazado(self):
        self.cfg.write_text(json.dumps({"nombre": "x", "pi_args": ["--model", "REEMPLAZAR"], "prompt": "{pregunta}"}), encoding="utf-8")
        r = ejecutar("--config", str(self.cfg), "--directorio", str(self.dir))
        self.assertEqual(r.returncode, 2)
        self.assertIn("REEMPLAZAR", r.stderr)

    def test_simular_no_ejecuta(self):
        r = ejecutar("--config", str(self.cfg), "--split", "holdout", "--simular", "--directorio", str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.strip().splitlines()), 4)
        self.assertFalse((self.dir / "resultados").exists())

    def test_caso_desconocido(self):
        r = ejecutar("--config", str(self.cfg), "--casos", "c99", "--directorio", str(self.dir))
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
