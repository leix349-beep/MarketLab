import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np
import pandas as pd

from daily_monitor import (candidate_weights, markdown_report, score_mature_signal, summarize,
                           update_paper_scorecard)


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
        conservative = candidate_weights(pd.DataFrame(rows), growth_sleeve=0.25)
        self.assertEqual(set(conservative["candidate"]), {"growth_25"})
        self.assertLessEqual(conservative["growth_share"].max(), 0.25)
        with self.assertRaises(ValueError):
            candidate_weights(pd.DataFrame(rows), growth_sleeve=1.1)

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

    def test_paper_outcome_scores_parallel_candidates(self):
        with TemporaryDirectory(dir=Path("tests")) as directory:
            root = Path(directory)
            daily = root / "daily"; daily.mkdir()
            paper = root / "paper"; (paper / "signals").mkdir(parents=True)
            dates = pd.bdate_range("2026-02-02", periods=7)
            tickers = ("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")
            for day_number, date in enumerate(dates):
                pd.DataFrame({
                    "date": date.date().isoformat(), "ticker": tickers,
                    "close": [100 + day_number, 100, 100, 100, 100, 100],
                }).to_csv(daily / f"{date.date().isoformat()}.csv", index=False)
            signal_rows = []
            for candidate, spy_weight in (("growth_25", 0.25), ("growth_50", 0.50)):
                other_weight = (1 - spy_weight) / 5
                for ticker in tickers:
                    signal_rows.append({
                        "signal_date": dates[0].date().isoformat(),
                        "candidate": candidate, "ticker": ticker,
                        "weight": spy_weight if ticker == "SPY" else other_weight,
                    })
            pd.DataFrame(signal_rows).to_csv(
                paper / "signals" / f"{dates[0].date().isoformat()}.csv", index=False
            )
            current = pd.read_csv(daily / f"{dates[-1].date().isoformat()}.csv")
            with patch("daily_monitor.OUTPUT_DIR", daily), patch("daily_monitor.PAPER_DIR", paper):
                outcome_path = score_mature_signal(current)
            outcomes = pd.read_csv(outcome_path).set_index("candidate")
            self.assertEqual(set(outcomes.index), {"growth_25", "growth_50"})
            self.assertGreater(outcomes.loc["growth_50", "candidate_return"],
                               outcomes.loc["growth_25", "candidate_return"])

    def test_scorecard_does_not_compound_overlapping_outcomes(self):
        with TemporaryDirectory(dir=Path("tests")) as directory:
            paper = Path(directory)
            outcomes = paper / "outcomes"; outcomes.mkdir()
            pd.DataFrame([
                {"signal_date": "2026-01-05", "candidate": "growth_25",
                 "entry_date": "2026-01-06", "evaluation_date": "2026-01-13",
                 "candidate_return": 0.02, "spy_return": 0.01, "excess_return": 0.01},
                {"signal_date": "2026-01-06", "candidate": "growth_25",
                 "entry_date": "2026-01-07", "evaluation_date": "2026-01-14",
                 "candidate_return": -0.01, "spy_return": 0.00, "excess_return": -0.01},
            ]).to_csv(outcomes / "2026-01-05.csv", index=False)
            with patch("daily_monitor.PAPER_DIR", paper):
                scorecard_path = update_paper_scorecard()
            scorecard = pd.read_csv(scorecard_path).iloc[0]
            self.assertEqual(scorecard["observations"], 2)
            self.assertAlmostEqual(scorecard["average_5d_return"], 0.005)
            self.assertAlmostEqual(scorecard["spy_win_rate"], 0.5)
            self.assertEqual(scorecard["non_overlapping_observations"], 1)
            self.assertEqual(scorecard["review_status"], "COLLECTING")
            self.assertNotIn("cumulative", pd.read_csv(scorecard_path).columns)

    def test_scorecard_requires_strong_non_overlapping_evidence(self):
        with TemporaryDirectory(dir=Path("tests")) as directory:
            paper = Path(directory)
            outcomes = paper / "outcomes"; outcomes.mkdir()
            rows = []
            for index in range(30):
                entry = pd.Timestamp("2024-01-02") + pd.Timedelta(days=index * 10)
                evaluation = entry + pd.Timedelta(days=7)
                rows.append({
                    "signal_date": (entry - pd.Timedelta(days=1)).date().isoformat(),
                    "entry_date": entry.date().isoformat(),
                    "evaluation_date": evaluation.date().isoformat(),
                    "candidate": "growth_25", "candidate_return": 0.02,
                    "spy_return": 0.01, "excess_return": 0.01,
                })
            pd.DataFrame(rows).to_csv(outcomes / "2024-01-01.csv", index=False)
            with patch("daily_monitor.PAPER_DIR", paper):
                scorecard_path = update_paper_scorecard()
            scorecard = pd.read_csv(scorecard_path).iloc[0]
            self.assertEqual(scorecard["non_overlapping_observations"], 30)
            self.assertGreater(scorecard["excess_mean_lower_95"], 0)
            self.assertEqual(scorecard["review_status"], "ELIGIBLE FOR REVIEW")


if __name__ == "__main__":
    unittest.main()
