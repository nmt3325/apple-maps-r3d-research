"""Synthetic tests for the isolated 0x24 wrapper parser."""
import struct
import unittest
from huff816_envelope import EnvelopeError, split_envelope

class Tests(unittest.TestCase):
    def test_single_uses_caller_count(self):
        p = struct.pack("<I", 0xe1000002) + b"abc"
        src = struct.pack("<IIQ", 0x24000000, 7, 123456) + p
        self.assertEqual(split_envelope(src)[0].symbol_count, None)

    def test_segment_boundaries(self):
        a = struct.pack("<I", 0xe1000002) + b"abc"
        b = struct.pack("<I", 0xe1000002) + b"de"
        src = struct.pack("<IIQ", 0x24000200, len(a), 3) + a
        src += struct.pack("<IQ", len(b), 2) + b
        s = split_envelope(src)
        self.assertEqual([(x.offset,x.compressed_size,x.symbol_count) for x in s],
                         [(16,7,3),(35,6,2)])
        with self.assertRaises(EnvelopeError):
            split_envelope(src[:-1])
        with self.assertRaises(EnvelopeError):
            split_envelope(src + b"x")

if __name__ == "__main__":
    unittest.main()
