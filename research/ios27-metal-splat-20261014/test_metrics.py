#!/usr/bin/env python3
"""Portable sanity checks for published GPU/PLY research measurement summaries.

Only checks recorded datasets and internal consistency; does NOT reproduce GPU
experiments, prove hardware shader equivalence, or validate source PLY bytes.
"""
import json
import unittest
from pathlib import Path

METRICS = Path(__file__).parent / "metrics"

def read(name):
    return json.loads((METRICS / name).read_text())

class MetricsConsistency(unittest.TestCase):
    def test_shader_comparison(self):
        data = read("ios_vs_macos_shader_ir.json")
        self.assertEqual(len(data), 8)
        self.assertEqual(sum(bool(item["normalized_ir_identical"]) for item in data.values()), 6)
        self.assertFalse(data["Flyover_splat_vertex"]["normalized_ir_identical"])

    def test_gpu_barycentric_parity_summary(self):
        data = read("ANALYTIC_BARYCENTRIC_PIXEL_PARITY.json")
        self.assertEqual(data["actual_pixels"], 1014)
        self.assertEqual(data["pixel_set_symmetric_difference"], 1)
        self.assertLess(data["rmse"], 2e-5)

    def test_color_parity_summary(self):
        cases = read("REAL_RGB_GPU_COLOR_PARITY_4CASES.json")
        self.assertEqual(set(cases), {"tokyo0", "tokyo1", "tokyo2", "tokyo30"})
        for case in cases.values():
            self.assertEqual(case["pixels"], 1014)
            self.assertEqual(len(case["rgb_error"]), 3)
            for channel in case["rgb_error"]:
                self.assertLess(channel["rmse"], 1e-3)

    def test_approximation_fits(self):
        d = read("gaussian_fit_to_native_triangle_pixels.json")
        one = d["best_single_gaussian_optimized_sigma_amp"]["rmse"]
        three = d["best_three_gaussian_mixture_optimized"]["rmse"]
        self.assertLess(three, one)
        self.assertGreater(three, 0.0)

    def test_corrected_export_counts_and_assumptions(self):
        single = read("tokyo223_CORRECTED_planar_approx_c1_p20.json")
        triple = read("tokyo223_CORRECTED_3gaussians_per_triangle_SH0.json")
        self.assertEqual(single["input_count"], 417650)
        self.assertEqual(single["output_count"], 417650)
        self.assertEqual(single["alpha_concentration_hypothetical"], 1)
        self.assertEqual(single["alpha_pre_factor_hypothetical"], 20)
        self.assertEqual(triple["gaussians"], 3 * single["output_count"])
        self.assertEqual(triple["input_native_splats"], single["output_count"])

if __name__ == "__main__":
    unittest.main()
