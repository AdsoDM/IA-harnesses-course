"""Parser de framing JSONL (un objeto JSON por línea terminada en LF).

No es un cliente RPC ni arranca Pi: solo convierte bytes en registros.
- Acumula bytes hasta LF; no divide en U+2028/U+2029 (válidos dentro de JSON).
- Acepta CRLF, rechaza registros vacíos, no-objeto o demasiado grandes.
- Modo estricto (por defecto): un registro inválido lanza ValueError.
- Modo tolerante: los registros inválidos se guardan en ``errores`` y el
  flujo continúa; útil para un cliente que no debe morir por una línea rota.
"""
import json


class JsonlDecoder:
    def __init__(self, max_record_bytes=1_000_000, tolerante=False):
        self.buffer = bytearray()
        self.limit = max_record_bytes
        self.tolerante = tolerante
        self.errores = []

    def _registro(self, line):
        if len(line) > self.limit:
            raise ValueError("Registro demasiado grande")
        if line.endswith(b"\r"):
            line = line[:-1]
        if not line:
            raise ValueError("Registro vacío")
        record = json.loads(line.decode("utf-8"))
        if not isinstance(record, dict):
            raise ValueError("Se requiere objeto JSON")
        return record

    def feed(self, chunk: bytes):
        self.buffer.extend(chunk)
        records = []
        while b"\n" in self.buffer:
            line, _, rest = self.buffer.partition(b"\n")
            self.buffer = bytearray(rest)
            try:
                records.append(self._registro(line))
            except ValueError as exc:  # json.JSONDecodeError y UnicodeDecodeError heredan de ValueError
                if not self.tolerante:
                    raise
                self.errores.append(f"{type(exc).__name__}: {exc}")
        if len(self.buffer) > self.limit:
            if not self.tolerante:
                raise ValueError("Registro incompleto demasiado grande")
            self.errores.append("Registro incompleto demasiado grande: descartado")
            self.buffer.clear()
        return records

    def finish(self):
        if self.buffer:
            if not self.tolerante:
                raise ValueError("EOF con registro sin LF")
            self.errores.append("EOF con registro sin LF")
            self.buffer.clear()
