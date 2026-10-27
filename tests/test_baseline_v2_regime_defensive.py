import unittest

import pandas as pd

from baseline_v2 import ASSETS
from baseline_v2_defensive import DEFENSIVE_ASSETS, DEFENSIVE_WEIGHT, TACTICAL_WEIGHT
from baseline_v2_regime_defensive import add_regime_defensive_sleeve


class RegimeDefensiveSleeveTests(unittest.TestCase):
    def test_only_defensive_dates_are_changed(self):
        index = pd.bdate_range("2026-01-02", periods=2)
        candidate = pd.DataFrame(0.0, index=index, columns=ASSETS)
        candidate.loc[:, "SPY"] = 0.5
        candidate.loc[:, "EFA"] = 0.5
        regime = pd.Series([False, True], index=index)
        result = add_regime_defensive_sleeve(candidate, regime)
        pd.testing.assert_series_equal(result.loc[index[0]], candidate.loc[index[0]])
        self.assertAlmostEqual(float(result.loc[index[1], "SPY"]), 0.5 * TACTICAL_WEIGHT)
        self.assertAlmostEqual(float(result.loc[index[1]].sum()), 1.0)
        for ticker in DEFENSIVE_ASSETS:
            expected = DEFENSIVE_WEIGHT / len(DEFENSIVE_ASSETS)
            self.assertGreaterEqual(float(result.loc[index[1], ticker]), expected)

    def test_weight_is_bounded_when_tactical_book_holds_cash(self):
        index = pd.bdate_range("2026-02-02", periods=1)
        candidate = pd.DataFrame(0.0, index=index, columns=ASSETS)
        candidate.loc[:, "SPY"] = 0.4
        regime = pd.Series([True], index=index)
        result = add_regime_defensive_sleeve(candidate, regime)
        self.assertAlmostEqual(float(result.sum(axis=1).iloc[0]), 0.4 * TACTICAL_WEIGHT + DEFENSIVE_WEIGHT)
        self.assertLessEqual(float(result.sum(axis=1).iloc[0]), 1.0)


if __name__ == "__main__":
    unittest.main()
