"""Check numerical examples and model boundary conditions."""

import math
import unittest

from power_supply_estimator import estimate_supply


class SupplyEstimateTests(unittest.TestCase):
    def test_reference_case(self):
        report = estimate_supply(secondary_rms_v=12, output_v=9, load_a=0.1)
        result = report["estimates"]
        self.assertAlmostEqual(result["reservoir_peak_v"], 15.570562748477143)
        self.assertAlmostEqual(result["reservoir_ripple_peak_to_peak_v"], 0.3787878787878788)
        self.assertAlmostEqual(result["dropout_margin_v"], 4.691774869689265)
        self.assertAlmostEqual(result["regulator_average_dissipation_w"], 0.6381168809083204)
        self.assertAlmostEqual(result["junction_temperature_c"], 31.381168809083205)
        self.assertTrue(report["regulation_supported_by_estimate"])

    def test_full_wave_ripple_and_load_scaling(self):
        light = estimate_supply(secondary_rms_v=12, output_v=9, load_a=0.1)
        heavy = estimate_supply(secondary_rms_v=12, output_v=9, load_a=0.2)
        larger_cap = estimate_supply(
            secondary_rms_v=12, output_v=9, load_a=0.2, capacitance_uf=4400
        )
        ripple = "reservoir_ripple_peak_to_peak_v"
        self.assertEqual(light["estimates"]["ripple_frequency_hz"], 120)
        self.assertAlmostEqual(heavy["estimates"][ripple], 2 * light["estimates"][ripple])
        self.assertAlmostEqual(larger_cap["estimates"][ripple], light["estimates"][ripple])

    def test_insufficient_headroom_is_identified(self):
        result = estimate_supply(secondary_rms_v=12, output_v=15, load_a=0.1)
        self.assertFalse(result["regulation_supported_by_estimate"])
        self.assertLess(result["estimates"]["dropout_margin_v"], 0)

    def test_invalid_inputs_are_rejected(self):
        for override in (
            {"capacitance_uf": 0},
            {"line_hz": -60},
            {"load_a": math.nan},
            {"secondary_rms_v": math.inf},
            {"diode_drop_v": -1},
            {"ambient_c": -300},
            {"capacitance_uf": 0.1},
        ):
            with self.subTest(override=override):
                inputs = {"secondary_rms_v": 12, "output_v": 9, "load_a": 0.1}
                inputs.update(override)
                with self.assertRaises(ValueError):
                    estimate_supply(**inputs)


if __name__ == "__main__":
    unittest.main()
