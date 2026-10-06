import unittest

import numpy as np
import pandas as pd

from validation import walk_forward_validate


class WalkForwardValidationTests(unittest.TestCase):
    def test_windows_are_ordered_and_non_overlapping(self):
        rng = np.random.default_rng(7)
        index = pd.bdate_range("2018-01-01", periods=900)
        close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(index))))
        frame = pd.DataFrame({
            "Open": close * (1 + rng.normal(0, 0.001, len(index))),
            "High": close * 1.01,
            "Low": close * 0.99,
            "Close": close,
        }, index=index)
        result = walk_forward_validate(frame, train_days=300, test_days=100, fasts=(10, 20), slows=(40, 60))
        folds = result["folds"]
        self.assertGreaterEqual(len(folds), 5)
        self.assertTrue((folds["Train End"] < folds["Test Start"]).all())
        self.assertTrue((folds["Test Start"].iloc[1:].reset_index(drop=True) >
                         folds["Test End"].iloc[:-1].reset_index(drop=True)).all())
        self.assertFalse(result["curve"].empty)


if __name__ == "__main__":
    unittest.main()
