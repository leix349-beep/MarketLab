import unittest

import numpy as np
import pandas as pd

from daily_monitor import markdown_report, summarize


class DailyMonitorTests(unittest.TestCase):
    def sample(self):
        index = pd.bdate_range("2026-01-01", periods=90)
        close = pd.Series(np.linspace(100, 130, len(index)), index=index)
        return pd.DataFrame(
            {
                "Open": close.shift(1).fillna(close.iloc[0]),
                "High": close + 1,
                "Low": close - 1,
                "Close": close,
                "Volume": 1_000_000,
            },
            index=index,
        )

    def test_summary_is_finite_and_dated(self):
        row = summarize("TEST", self.sample())
        self.assertEqual(row["ticker"], "TEST")
        self.assertEqual(row["date"], "2026-05-06")
        for key in ["close", "return_1d", "return_5d", "return_21d", "rsi14"]:
            self.assertTrue(np.isfinite(row[key]))

    def test_report_contains_disclaimer_and_ticker(self):
        snapshot = pd.DataFrame([summarize("TEST", self.sample())])
        report = markdown_report(snapshot)
        self.assertIn("TEST", report)
        self.assertIn("not investment advice", report)


if __name__ == "__main__":
    unittest.main()
