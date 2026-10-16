import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np
import pandas as pd

from daily_monitor import candidate_weights, markdown_report, score_mature_signal, summarize


class DailyMonitorTests(unittest.TestCase):
    def sample(self):
        index = pd.bdate_range("2025-01-01", periods=260)
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
        self.assertEqual(row["date"], self.sample().index[-1].date().isoformat())
        for key in ["close", "return_1d", "return_5d", "return_21d", "return_63d",
                    "ma200", "rsi14"]:
            self.assertTrue(np.isfinite(row[key]))

    def test_report_contains_disclaimer_and_ticker(self):
        snapshot = pd.DataFrame([summarize("TEST", self.sample())])
        factors = pd.DataFrame([
            {"ticker":"SPY","factor":"US Equities","return_1d":.01,"return_5d":.02,"return_21d":.03},
        ])
        report = markdown_report(snapshot, factors)
        self.assertIn("TEST", report)
        self.assertIn("not investment advice", report)
        self.assertIn("Global Market Context", report)

    def test_candidate_weights_are_complete_and_bounded(self):
        rows = []
        for offset, ticker in enumerate(("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")):
            row = summarize(ticker, self.sample() * (1 + offset / 100))
            rows.append(row)
        weights = candidate_weights(pd.DataFrame(rows))
        self.assertAlmostEqual(weights["weight"].sum(), 1.0)
        self.assertTrue(weights["weight"].between(0, 1).all())
        self.assertEqual(set(weights["ticker"]), {"SPY", "IWM", "TLT", "HYG", "GLD", "UUP"})

    def test_paper_outcome_uses_next_session_as_entry(self):
        with TemporaryDirectory(dir=Path("tests")) as directory:
            root = Path(directory)
            daily = root / "daily"; daily.mkdir()
            paper = root / "paper"; (paper / "signals").mkdir(parents=True)
            dates = pd.bdate_range("2026-01-05", periods=7)
            tickers = ("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")
            for day_number, date in enumerate(dates):
                pd.DataFrame({
                    "date": date.date().isoformat(),
                    "ticker": tickers,
                    "close": [100 + day_number] * len(tickers),
                }).to_csv(daily / f"{date.date().isoformat()}.csv", index=False)
            pd.DataFrame({
                "signal_date": dates[0].date().isoformat(),
                "ticker": tickers,
                "weight": [1 / len(tickers)] * len(tickers),
            }).to_csv(paper / "signals" / f"{dates[0].date().isoformat()}.csv", index=False)
            current = pd.read_csv(daily / f"{dates[-1].date().isoformat()}.csv")
            with patch("daily_monitor.OUTPUT_DIR", daily), patch("daily_monitor.PAPER_DIR", paper):
                outcome_path = score_mature_signal(current)
            outcome = pd.read_csv(outcome_path).iloc[0]
            self.assertEqual(outcome["entry_date"], dates[1].date().isoformat())
            self.assertAlmostEqual(outcome["candidate_return"], 106 / 101 - 1)


if __name__ == "__main__":
    unittest.main()
