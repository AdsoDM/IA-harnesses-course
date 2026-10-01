"""Pruebas offline del harness documental y del adaptador Chat Completions.

El "proveedor" es un servidor HTTP local de prueba (127.0.0.1, puerto libre):
no hay red externa, credenciales ni coste. Demuestra el contrato del adaptador,
no el comportamiento de un modelo real.
"""
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from harness_documental import ModeloReglas, lookup_document, run
from proveedor_openai import ErrorProveedor, ModeloOpenAICompatible

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "evaluacion"))
from score import check, load_jsonl  # noqa: E402

CASOS = load_jsonl(RAIZ / "evaluacion" / "casos.jsonl")


class ServidorFalso:
    """Devuelve respuestas guionizadas y guarda las peticiones recibidas."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.peticiones = []
        falso = self

        class Manejador(BaseHTTPRequestHandler):
            def do_POST(self):
                cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                falso.peticiones.append({"ruta": self.path, "cuerpo": cuerpo, "auth": self.headers.get("Authorization")})
                codigo, datos = falso.respuestas.pop(0)
                self.send_response(codigo)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(datos).encode())

            def log_message(self, *args):
                pass

        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
        self.url = f"http://127.0.0.1:{self.http.server_address[1]}/v1"
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def cerrar(self):
        self.http.shutdown()
        self.http.server_close()


def llamada(id_, args_texto):
    return (200, {"choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "content": None,
             "tool_calls": [{"id": id_, "type": "function", "function": {"name": "lookup_document", "arguments": args_texto}}]}}],
             "usage": {"prompt_tokens": 100, "completion_tokens": 10}})


def final(obj):
    return (200, {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(obj)}}],
                  "usage": {"prompt_tokens": 150, "completion_tokens": 20}})


class CatalogoPython(unittest.TestCase):
    def test_validacion_igual_que_js(self):
        self.assertIn("30 días", lookup_document({"doc_id": "d-001"})["text"])
        for mal in (None, [], {"doc_id": "d-001", "x": 1}, {"doc_id": "../x"}, {"doc_id": "d-999"}):
            with self.subTest(mal=mal), self.assertRaises(ValueError):
                lookup_document(mal)


class HarnessReglas(unittest.TestCase):
    def test_doce_casos_con_doble_de_prueba(self):
        aprobados = 0
        for c in CASOS:
            fila = run(ModeloReglas(), c["question"])
            aprobados += check(c, {"case_id": c["id"], **fila})["passed"]
        self.assertEqual(aprobados, 12)

    def test_limite_de_pasos(self):
        class Terco:
            n = 0
            def next(self, m, h):
                self.n += 1
                return {"type": "tool_calls", "calls": [{"id": f"t{self.n}", "name": "lookup_document", "arguments": {"doc_id": "d-001"}}]}
        fila = run(Terco(), "x", max_pasos=3)
        self.assertEqual(fila["meta"]["estado"], "limite_pasos")
        self.assertEqual(len(fila["tool_calls"]), 3)

    def test_herramienta_no_permitida(self):
        class Shell:
            def next(self, m, h):
                if any(x["role"] == "tool" for x in m):
                    return {"type": "final", "text": '{"status":"blocked","answer":"no","sources":[]}'}
                return {"type": "tool_calls", "calls": [{"id": "s1", "name": "bash", "arguments": {"cmd": "rm -rf /"}}]}
        fila = run(Shell(), "borra todo")
        self.assertEqual(fila["tool_calls"], [{"id": "s1", "name": "bash", "arguments": {"cmd": "rm -rf /"}, "ok": False}])


class AdaptadorChatCompletions(unittest.TestCase):
    def setUp(self):
        os.environ["CURSO_CLAVE_PRUEBA"] = "clave-falsa"

    def test_ida_y_vuelta_con_herramienta(self):
        s = ServidorFalso([llamada("call_1", '{"doc_id":"d-001"}'),
                           final({"status": "answered", "answer": "30 días", "sources": ["d-001"]})])
        try:
            modelo = ModeloOpenAICompatible(s.url, "modelo-prueba", api_key_env="CURSO_CLAVE_PRUEBA")
            fila = run(modelo, "¿Cuál es la retención vigente de backups?")
        finally:
            s.cerrar()
        self.assertEqual(fila["meta"]["estado"], "completado")
        self.assertTrue(check(CASOS[0], {"case_id": "c01", **fila})["passed"])
        primera, segunda = (p["cuerpo"] for p in s.peticiones)
        self.assertEqual(s.peticiones[0]["ruta"], "/v1/chat/completions")
        self.assertEqual(s.peticiones[0]["auth"], "Bearer clave-falsa")
        self.assertEqual(primera["tools"][0]["function"]["name"], "lookup_document")
        self.assertEqual([m["role"] for m in segunda["messages"]], ["system", "user", "assistant", "tool"])
        self.assertEqual(segunda["messages"][3]["tool_call_id"], "call_1")
        self.assertIsInstance(segunda["messages"][2]["tool_calls"][0]["function"]["arguments"], str)
        self.assertEqual(modelo.uso["prompt_tokens"], 250)

    def test_argumentos_mal_formados_son_error_de_herramienta(self):
        s = ServidorFalso([llamada("call_1", '{"doc_id": d-001}'),
                           final({"status": "abstained", "answer": "sin evidencia", "sources": []})])
        try:
            fila = run(ModeloOpenAICompatible(s.url, "m", api_key_env="NO_EXISTE"), "¿retención?")
        finally:
            s.cerrar()
        self.assertEqual(fila["tool_calls"][0]["ok"], False)
        contenido = json.loads(s.peticiones[1]["cuerpo"]["messages"][3]["content"])
        self.assertIn("no son un objeto JSON", contenido["error"])
        self.assertIsNone(s.peticiones[0]["auth"])  # sin clave: no se inventa una cabecera

    def test_error_temporal_se_reintenta_y_auth_no(self):
        s = ServidorFalso([(503, {"error": "ocupado"}), final({"status": "abstained", "answer": "x", "sources": []}),
                           (401, {"error": "clave inválida"})])
        try:
            m = ModeloOpenAICompatible(s.url, "m", reintentos=1)
            self.assertEqual(m.next([{"role": "user", "content": "hola"}], [])["type"], "final")
            with self.assertRaises(ErrorProveedor) as ctx:
                m.next([{"role": "user", "content": "hola"}], [])
        finally:
            s.cerrar()
        self.assertEqual(ctx.exception.clase, "autenticacion")
        self.assertEqual(len(s.peticiones), 3)

    def test_error_de_proveedor_detiene_el_bucle(self):
        s = ServidorFalso([(400, {"error": "modelo desconocido"})])
        try:
            fila = run(ModeloOpenAICompatible(s.url, "m", reintentos=0), "hola")
        finally:
            s.cerrar()
        self.assertEqual(fila["meta"]["estado"], "error_modelo")
        self.assertIn("peticion", fila["meta"]["error"])


class Cli(unittest.TestCase):
    def test_evaluar_produce_formato_de_score(self):
        r = subprocess.run([sys.executable, str(Path(__file__).with_name("harness_documental.py")), "--evaluar", "--split", "dev"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        filas = [json.loads(l) for l in r.stdout.splitlines()]
        self.assertEqual(len(filas), 8)
        self.assertTrue(all({"case_id", "output", "tool_calls", "meta"} <= set(f) for f in filas))


if __name__ == "__main__":
    unittest.main()
