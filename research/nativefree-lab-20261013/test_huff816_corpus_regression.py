"""Corpus regression for the independently parsed Huff816 wrappers."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

class CorpusEnvelopeRegression(unittest.TestCase):
    def test_tokyo223_oahu72(self):
        proc = subprocess.run(
            [sys.executable, str(HERE / "test_huff816_envelope_corpus.py")],
            cwd=HERE, capture_output=True, text=True, timeout=120, check=True)
        report = json.loads(proc.stdout)
        self.assertEqual((report["tokyo"], report["oahu"]), (223, 72))
        self.assertEqual(report["counts"], {"single": 2424, "segments": 2424})
        self.assertEqual(report["examples"], [])

if __name__ == "__main__":
    unittest.main()
