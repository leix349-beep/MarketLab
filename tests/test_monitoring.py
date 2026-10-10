import tempfile
import unittest
from pathlib import Path

import pandas as pd

from monitoring import breadth_history, build_forward_scorecard, load_snapshot_history, trading_day_lag


class MonitoringTests(unittest.TestCase):
    def test_load_deduplicates_and_scores_without_lookahead(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            for day, closes in [("2026-10-01", [100, 50]), ("2026-10-02", [102, 49])]:
                pd.DataFrame({
                    "date": [day, day], "ticker": ["AAA", "BBB"], "close": closes,
                    "trend_state": ["Above MA20/60", "Below MA20/60"],
                }).to_csv(root / f"{day}.csv", index=False)
            history = load_snapshot_history(root)
            self.assertEqual(len(history), 4)
            score = build_forward_scorecard(history)
            self.assertEqual(int(score["observations"].sum()), 2)
            breadth = breadth_history(history)
            self.assertTrue((breadth["breadth"] == 0.5).all())

    def test_trading_day_lag_ignores_weekend(self):
        self.assertEqual(trading_day_lag("2026-10-08", "2026-10-10"), 1)
        self.assertEqual(trading_day_lag("2026-10-09", "2026-10-11"), 0)


if __name__ == "__main__":
    unittest.main()
