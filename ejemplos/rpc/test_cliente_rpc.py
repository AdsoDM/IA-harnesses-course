import sys
import unittest
from pathlib import Path

from cliente_rpc import ClientePiRpc

FALSO = str(Path(__file__).with_name("pi_falso.py"))


def cliente(modo, gracia=1.0):
    # Se ejecuta: python pi_falso.py MODO --mode rpc (el falso ignora lo demás)
    return ClientePiRpc([], comando=[sys.executable, FALSO, modo], gracia_s=gracia)


class ClienteRpcTests(unittest.TestCase):
    def test_normal_espera_asentamiento(self):
        c = cliente("normal")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=5)
        finally:
            c.cerrar()
        self.assertEqual(r.estado, "completado")
        self.assertEqual(r.disposicion, "started")
        self.assertEqual(r.texto_final, '{"saludo":"año"}')
        self.assertEqual(r.eventos[-1]["type"], "agent_settled")
        estados = [e for _, e in c.transiciones]
        self.assertEqual(estados[:5], ["arrancando", "listo", "aceptado", "ejecutando", "asentado"])
        self.assertEqual(estados[-1], "cerrado")

    def test_rechazo_no_es_fallo_del_modelo(self):
        c = cliente("rechazo")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=5)
        finally:
            c.cerrar()
        self.assertEqual(r.estado, "rechazado")
        self.assertIn("rechazado", r.error)

    def test_plazo_envia_abort(self):
        c = cliente("lento")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=0.5)
        finally:
            c.cerrar()
        self.assertEqual(r.estado, "plazo_vencido")
        self.assertEqual(r.stop_reason, "aborted")
        self.assertTrue(any(reg.get("command") == "abort" for reg in c.registros))

    def test_caida_tras_aceptar(self):
        c = cliente("cae")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=5)
        finally:
            codigo = c.cerrar()
        self.assertEqual(r.estado, "fallido")
        self.assertIn("agent_settled", r.error)
        self.assertEqual(codigo, 3)

    def test_stderr_voluminoso_no_bloquea(self):
        c = cliente("ruido")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=5)
        finally:
            c.cerrar()
        self.assertEqual(r.estado, "completado")
        self.assertIn("diagnóstico", c.stderr)

    def test_fragmentacion_utf8(self):
        c = cliente("fragmentado")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=10)
        finally:
            c.cerrar()
        self.assertEqual(r.texto_final, '{"saludo":"año"}')

    def test_respuesta_con_id_ajeno_no_se_confunde(self):
        c = cliente("id-ajeno")
        try:
            c.iniciar()
            r = c.ejecutar_prompt("hola", plazo_s=5)
        finally:
            c.cerrar()
        self.assertEqual(r.estado, "completado")
        self.assertTrue(any("sin petición pendiente" in e for e in c.errores_protocolo))

    def test_cierre_de_proceso_terco(self):
        c = cliente("terco", gracia=0.5)
        c.iniciar()
        codigo = c.cerrar()
        self.assertIsNotNone(codigo)
        self.assertEqual(c.estado, "cerrado")


if __name__ == "__main__":
    unittest.main()
