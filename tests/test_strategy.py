import unittest
import numpy as np
import pandas as pd
from strategy import backtest

class StrategyTests(unittest.TestCase):
    def sample(self, n=140):
        idx = pd.bdate_range("2024-01-01", periods=n)
        close = np.linspace(100, 160, n) + np.sin(np.arange(n)/3) * 3
        return pd.DataFrame({"Open": close + 1, "High": close + 2,
                             "Low": close - 2, "Close": close,
                             "Volume": 1_000_000}, index=idx)

    def test_trade_occurs_after_signal_history_exists(self):
        df = self.sample()
        _, trades, _ = backtest(df, fast=5, slow=15, rsi_buy=100)
        if len(trades):
            self.assertGreaterEqual(trades.iloc[0]["date"], df.index[15])

    def test_equity_and_metrics_are_finite(self):
        curve, _, metrics = backtest(self.sample(), fast=5, slow=15, rsi_buy=100)
        self.assertTrue(np.isfinite(curve).all())
        self.assertTrue(all(np.isfinite(v) for v in metrics.values()))
        self.assertGreater(len(curve), 0)

    def test_trades_alternate(self):
        _, trades, _ = backtest(self.sample(), fast=5, slow=15, rsi_buy=100)
        actions = trades.action.tolist()
        self.assertTrue(all(a != b for a, b in zip(actions, actions[1:])))

if __name__ == "__main__":
    unittest.main()
