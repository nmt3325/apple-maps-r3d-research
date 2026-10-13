"""Regression for inert AArch64 count-register constructor metadata."""
import unittest
from arm64_count_constructors import (
    audit, orr, load_unsigned, words, EXPECTED_X28, EXPECTED_X24
)

class CountConstructorTests(unittest.TestCase):
    def test_instruction_decoders(self):
        self.assertEqual(orr(0xAA0921BC), (64, 28, 13, 9, 8))
        self.assertEqual(orr(0xAA0D013C), (64, 28, 9, 13, 0))
        self.assertEqual(orr(0xAA1C22F8), (64, 24, 23, 28, 8))
        self.assertEqual(orr(0x2A094149), (32, 9, 10, 9, 16))
        self.assertEqual(load_unsigned(0x39439BE9), (1, 9, 31, 230))
        self.assertEqual(load_unsigned(0x7941CBEA), (2, 10, 31, 228))
        self.assertEqual(load_unsigned(0xB940E3EA), (4, 10, 31, 224))
        self.assertEqual(load_unsigned(0xF9400BED), (8, 13, 31, 16))

    def test_saved_capture(self):
        w = words()
        self.assertEqual(len(w), 5208)
        result = audit()
        self.assertEqual(result["verifiedConstructors"], 7)
        self.assertEqual(result["x28WideCandidates"], 4)
        self.assertEqual(result["x24Candidates"], 3)
        self.assertEqual(len(EXPECTED_X28), 4)
        self.assertEqual(len(EXPECTED_X24), 3)

if __name__ == "__main__":
    unittest.main()
