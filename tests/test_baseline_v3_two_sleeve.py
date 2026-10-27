import unittest

import numpy as np
import pandas as pd

from baseline_v2 import ASSETS
from baseline_v3_two_sleeve import (DEFENSIVE_ASSETS, GROWTH_ASSETS,
                                    build_two_sleeve_signal_weights)


def synthetic_two_sleeve_prices(periods: int = 700) -> pd.DataFrame:
    index = pd.bdate_range("2020-01-01", periods=periods)
    frame = pd.DataFrame(index=index)
    for offset, ticker in enumerate(ASSETS):
        frame[ticker] = 100 + offset + np.linspace(0, 70 - offset, periods)
    return frame


class TwoSleeveBaselineTests(unittest.TestCase):
    def test_weights_are_bounded_and_both_sleeves_can_be_present(self):
        weights = build_two_sleeve_signal_weights(synthetic_two_sleeve_prices())
        active = weights[weights.sum(axis=1) > 0]
        self.assertTrue((active >= 0).all().all())
        self.assertTrue((active <= 0.5 + 1e-12).all().all())
        self.assertTrue((active.sum(axis=1) <= 1 + 1e-12).all())
        self.assertTrue((active.loc[:, list(GROWTH_ASSETS)].sum(axis=1) > 0).any())
        self.assertTrue((active.loc[:, list(DEFENSIVE_ASSETS)].sum(axis=1) > 0).any())

    def test_future_prices_do_not_change_past_weights(self):
        prices = synthetic_two_sleeve_prices()
        cutoff = prices.index[500]
        first = build_two_sleeve_signal_weights(prices)
        changed = prices.copy()
        changed.loc[changed.index > cutoff] *= 4
        second = build_two_sleeve_signal_weights(changed)
        pd.testing.assert_frame_equal(first.loc[:cutoff], second.loc[:cutoff])


if __name__ == "__main__":
    unittest.main()
