"""Pruebas del normalizador con trazas REALES de Pi 0.99.1 y el modelo de guion.

Las trazas de trazas-ejemplo/ se generaron con el proveedor simulado del curso:
demuestran el formato de eventos de Pi, no la calidad de ningún modelo.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from normalizar_pi import interpretar_salida, leer_registros, normalizar
from score import check, load_jsonl

AQUI = Path(__file__).parent
EJ = AQUI / "trazas-ejemplo"
CASOS = {c["id"]: c for c in load_jsonl(AQUI / "casos.jsonl")}


class NormalizarTests(unittest.TestCase):
    def fila(self, archivo, caso):
        return normalizar(leer_registros(EJ / archivo), caso)

    def test_json_mode_con_cabecera_de_sesion(self):
        f = self.fila("json-c02-guion.jsonl", "c02")
        self.assertEqual(f["output"]["status"], "answered")
        self.assertEqual([c["name"] for c in f["tool_calls"]], ["lookup_document"])
        self.assertTrue(f["meta"]["asentado"])
        self.assertIsNotNone(f["meta"]["sesion"])
        self.assertTrue(check(CASOS["c02"], f)["passed"])

    def test_rpc_dos_consultas_reales(self):
        f = self.fila("rpc-c09-guion.jsonl", "c09")
        ids = [c["arguments"]["doc_id"] for c in f["tool_calls"] if c["ok"]]
        self.assertEqual(sorted(ids), ["d-001", "d-003"])
        self.assertEqual(f["meta"]["proveedor"], "curso")
        self.assertTrue(check(CASOS["c09"], f)["passed"])

    def test_herramienta_inexistente_rompe_politica(self):
        f = self.fila("rpc-c07-obediente.jsonl", "c07")
        self.assertIn(("borrar_backups", False), [(c["name"], c["ok"]) for c in f["tool_calls"]])
        r = check(CASOS["c07"], f)
        self.assertFalse(r["policy"])
        self.assertFalse(r["status"])

    def test_bucle_detenido_sin_respuesta_final(self):
        f = self.fila("rpc-c01-bucle.jsonl", "c01")
        self.assertIsNone(f["output"])
        self.assertEqual(f["meta"]["stop_reason"], "toolUse")
        self.assertFalse(f["tool_calls"][-1]["ok"])  # la llamada bloqueada por presupuesto
        self.assertFalse(check(CASOS["c01"], f)["passed"])

    def test_prosa_incumple_contrato(self):
        f = self.fila("rpc-c01-json-roto.jsonl", "c01")
        self.assertIsNone(f["output"])
        self.assertIn("no es únicamente", f["meta"]["error_salida"])
        self.assertIn("30 días", f["meta"]["texto_final"])

    def test_sin_asentamiento_no_hay_salida(self):
        regs = [r for r in leer_registros(EJ / "json-c02-guion.jsonl") if r.get("type") != "agent_settled"]
        f = normalizar(regs, "c02")
        self.assertIsNone(f["output"])
        self.assertIn("agent_settled", f["meta"]["error_salida"])

    def test_llamada_sin_fin_cuenta_como_fallida(self):
        regs = [r for r in leer_registros(EJ / "json-c02-guion.jsonl") if r.get("type") != "tool_execution_end"]
        f = normalizar(regs, "c02")
        self.assertEqual([(c["ok"], c["completada"]) for c in f["tool_calls"]], [(False, False)])
        self.assertFalse(check(CASOS["c02"], f)["evidence"])

    def test_utf16_de_powershell(self):
        texto = (EJ / "json-c02-guion.jsonl").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "utf16.jsonl"
            p.write_bytes(texto.replace("\n", "\r\n").encode("utf-16"))
            self.assertEqual(len(leer_registros(p)), len(texto.strip().split("\n")))

    def test_linea_invalida_informa_numero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "roto.jsonl"
            p.write_text('{"type":"agent_start"}\nno json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "línea 2"):
                leer_registros(p)

    def test_contrato_de_salida(self):
        self.assertEqual(interpretar_salida('  {"a":1} ')[0], {"a": 1})
        for mal in (None, "hola", '```json\n{"a":1}\n```', "[1]", '{"a":'):
            with self.subTest(mal=mal):
                self.assertIsNone(interpretar_salida(mal)[0])

    def test_meta_externa_se_conserva(self):
        f = normalizar(leer_registros(EJ / "json-c02-guion.jsonl"), "c02", {"repeticion": 2})
        self.assertEqual(f["meta"]["repeticion"], 2)
        json.dumps(f)  # serializable


if __name__ == "__main__":
    unittest.main()
