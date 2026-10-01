import unittest
from framing import JsonlDecoder

class FramingTests(unittest.TestCase):
    def test_fragmented_utf8(self):
        d = JsonlDecoder()
        b = '{"text":"año"}\n'.encode()
        split = b.index(b'\xc3') + 1
        self.assertEqual(d.feed(b[:split]), [])
        self.assertEqual(d.feed(b[split:]), [{"text":"año"}])
        d.finish()
    def test_two_records_and_crlf(self):
        self.assertEqual(JsonlDecoder().feed(b'{"a":1}\r\n{"b":2}\n'), [{"a":1},{"b":2}])
    def test_unicode_separator_is_not_framing(self):
        self.assertEqual(JsonlDecoder().feed('{"x":"a\u2028b"}\n'.encode()), [{"x":"a\u2028b"}])
    def test_invalid_json(self):
        with self.assertRaises(ValueError): JsonlDecoder().feed(b'bad\n')
    def test_eof_missing_lf(self):
        d = JsonlDecoder(); d.feed(b'{"x":1}')
        with self.assertRaises(ValueError): d.finish()
    def test_record_limit(self):
        with self.assertRaises(ValueError): JsonlDecoder(3).feed(b'1234')

    def test_tolerant_mode_keeps_valid_records(self):
        d = JsonlDecoder(tolerante=True)
        self.assertEqual(d.feed(b'{"a":1}\nroto\n{"b":2}\n'), [{"a":1},{"b":2}])
        self.assertEqual(len(d.errores), 1)
        d.feed(b'{"c":'); d.finish()
        self.assertEqual(len(d.errores), 2)
    def test_invalid_utf8_is_value_error(self):
        with self.assertRaises(ValueError): JsonlDecoder().feed(b'{"x":"\xff"}\n')

if __name__ == "__main__": unittest.main()
