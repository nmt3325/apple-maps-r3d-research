"""Synthetic 8-bit and 16-bit Huff wrapper decoder tests."""
import struct
import unittest
from huff816_wrapper_decode import decode_envelope
from huff816_envelope import EnvelopeError

def literal(b):
    return struct.pack("<I", 0xe1000002) + b

class DecodeTests(unittest.TestCase):
    def test_segmented_8(self):
        a,b = literal(b"abc"),literal(b"de")
        src = struct.pack("<IIQ", 0x24000200, len(a), 3) + a
        src += struct.pack("<IQ", len(b), 2) + b
        self.assertEqual(decode_envelope(src, 8), b"abcde")
        with self.assertRaises(EnvelopeError):
            decode_envelope(src, 8, count=6)

    def test_single_and_16bit(self):
        b = struct.pack("<3H", 2, 1024, 65535)
        p = literal(b)
        src = struct.pack("<IIQ", 0x24000000, 999, 888) + p
        self.assertEqual(decode_envelope(src, 16, count=3), b)
        with self.assertRaises(EnvelopeError):
            decode_envelope(src, 16)

if __name__ == "__main__":
    unittest.main()
