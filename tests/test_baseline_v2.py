import unittest

import numpy as np
import pandas as pd

from baseline_v2 import (ASSETS, build_signal_weights, execution_weights,
                         simulate_target_weights)
from research_costs import BASE_COST_SCENARIO


def synthetic_prices(periods: int = 700) -> pd.DataFrame:
    index = pd.bdate_range("2020-01-01", periods=periods)
    frame = pd.DataFrame(index=index)
    for offset, ticker in enumerate(ASSETS):
        frame[ticker] = 100 + offset + np.linspace(0, 60 - offset, periods)
    return frame


class BaselineV2Tests(unittest.TestCase):
    def test_weights_are_bounded_and_hold_cash_when_scaled(self):
        signals = build_signal_weights(synthetic_prices())
        self.assertTrue((signals >= 0).all().all())
        self.assertTrue((signals <= 0.5 + 1e-12).all().all())
        self.assertTrue((signals.sum(axis=1) <= 1 + 1e-12).all())
        self.assertTrue((signals.sum(axis=1) > 0).any())

    def test_execution_is_delayed_one_session(self):
        signals = build_signal_weights(synthetic_prices())
        executed = execution_weights(signals)
        pd.testing.assert_series_equal(executed.iloc[1], signals.iloc[0], check_names=False)
        self.assertEqual(float(executed.iloc[0].sum()), 0.0)

    def test_future_prices_do_not_change_past_signals(self):
        prices = synthetic_prices()
        cutoff = prices.index[500]
        first = build_signal_weights(prices)
        changed = prices.copy()
        changed.loc[changed.index > cutoff] *= 5
        second = build_signal_weights(changed)
        pd.testing.assert_frame_equal(first.loc[:cutoff], second.loc[:cutoff])

    def test_static_target_is_not_rebalanced_for_free(self):
        index = pd.bdate_range("2026-01-01", periods=5)
        target = pd.DataFrame(0.0, index=index, columns=ASSETS)
        target["SPY"] = 0.6
        target["TLT"] = 0.4
        returns = pd.DataFrame(0.0, index=index, columns=ASSETS)
        returns["SPY"] = 0.02
        result = simulate_target_weights(target, returns, BASE_COST_SCENARIO)
        self.assertGreater(result.iloc[0]["turnover"], 0)
        self.assertTrue((result.iloc[1:]["turnover"] == 0).all())


if __name__ == "__main__":
    unittest.main()
