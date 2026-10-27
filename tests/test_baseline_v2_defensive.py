import unittest

import pandas as pd

from baseline_v2 import ASSETS
from baseline_v2_defensive import (DEFENSIVE_ASSETS, DEFENSIVE_WEIGHT,
                                   TACTICAL_WEIGHT, add_fixed_defensive_sleeve)


class DefensiveSleeveTests(unittest.TestCase):
    def test_zero_tactical_signal_still_has_exact_fixed_sleeve(self):
        candidate = pd.DataFrame(0.0, index=[pd.Timestamp("2026-01-02")], columns=ASSETS)
        result = add_fixed_defensive_sleeve(candidate)
        self.assertAlmostEqual(float(result.sum(axis=1).iloc[0]), DEFENSIVE_WEIGHT)
        for ticker in DEFENSIVE_ASSETS:
            self.assertAlmostEqual(float(result[ticker].iloc[0]), DEFENSIVE_WEIGHT / 3)

    def test_tactical_book_is_scaled_once_and_total_weight_is_bounded(self):
        candidate = pd.DataFrame(0.0, index=[pd.Timestamp("2026-01-02")], columns=ASSETS)
        candidate.loc[:, "SPY"] = 0.5
        candidate.loc[:, "EFA"] = 0.5
        result = add_fixed_defensive_sleeve(candidate)
        self.assertAlmostEqual(float(result["SPY"].iloc[0]), 0.5 * TACTICAL_WEIGHT)
        self.assertAlmostEqual(float(result["EFA"].iloc[0]), 0.5 * TACTICAL_WEIGHT)
        self.assertLessEqual(float(result.sum(axis=1).iloc[0]), 1.0)


if __name__ == "__main__":
    unittest.main()
