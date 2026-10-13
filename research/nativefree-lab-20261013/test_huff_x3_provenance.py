"""Regression for static Huff callsite output-count argument sources."""
import unittest
from huff_x3_provenance import audit, orr, ldr_sp, call_target

class ProvenanceTest(unittest.TestCase):
    def test_instruction_decoders(self):
        self.assertEqual(orr(0xAA1403E3), (3, 31, 20, 0))
        self.assertEqual(orr(0xAA1C03E3), (3, 31, 28, 0))
        self.assertEqual(orr(0xAA0921BC), (28, 13, 9, 8))
        self.assertEqual(orr(0xAA1C22F8), (24, 23, 28, 8))
        self.assertEqual(ldr_sp(0xF9401BF4), (20, 0x30))
        self.assertEqual(ldr_sp(0xF9401BF3), (19, 0x30))
        self.assertEqual(call_target(0x97FFF033, 0x1B70A06E8), 0x1B709C7B4)

    def test_captured_calls(self):
        result = audit()
        self.assertEqual(result["callsiteCount"], 12)
        self.assertEqual(result["sources"], {"x20":4,"x28":4,"x19":2,"x24":2})
        self.assertEqual(sum(row["huff"] == "huff8" for row in result["calls"]), 9)
        self.assertEqual(sum(row["huff"] == "huff16" for row in result["calls"]), 3)

if __name__ == "__main__":
    unittest.main()
