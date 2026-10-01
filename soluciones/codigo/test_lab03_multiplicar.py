import unittest

from lab03_multiplicar import ModeloMultiplica, multiplicar, run


class MultiplicarTests(unittest.TestCase):
    def test_positivo(self):
        r = run(ModeloMultiplica())
        self.assertEqual((r["status"], r["answer"]), ("completed", "42"))

    def test_negativos_de_contrato(self):
        for args in ({"a": "6", "b": 7}, {"a": True, "b": 7}, {"a": 6.0, "b": 7}, {"a": 6}, {"a": 6, "b": 7, "c": 1},
                     {"a": 2_000_000, "b": 1}, None):
            with self.subTest(args=args), self.assertRaises(ValueError):
                multiplicar(args)

    def test_error_llega_al_modelo_y_no_hay_efecto(self):
        r = run(ModeloMultiplica({"a": "6", "b": 7}))
        self.assertFalse(r["trace"][1]["result"]["ok"])
        self.assertIn("No pude ejecutar", r["answer"])

    def test_nombre_desconocido_sigue_rechazado(self):
        r = run(ModeloMultiplica(), herramientas={"sumar": lambda a: {"value": 0}})
        self.assertEqual(r["trace"][1]["result"], {"ok": False, "error": "Herramienta no permitida"})


if __name__ == "__main__":
    unittest.main()
