import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from model_training import FEATURES, build_features, chronological_evaluation, download_dataset


class ModelTrainingTests(unittest.TestCase):
    def test_future_rows_are_removed(self):
        index = pd.bdate_range("2020-01-01", periods=150)
        frame = pd.DataFrame({"Close": np.linspace(100, 150, len(index))}, index=index)
        features = build_features(frame, horizon=5)
        self.assertLessEqual(features.index.max(), index[-6])
        self.assertTrue(features[list(FEATURES) + ["future_return", "label"]].notna().all().all())

    def test_chronological_result_starts_after_training_window(self):
        rng = np.random.default_rng(5)
        index = pd.bdate_range("2015-01-01", periods=1200)
        data = pd.DataFrame(rng.normal(size=(len(index), len(FEATURES))), index=index, columns=FEATURES)
        data["future_return"] = rng.normal(0.001, 0.02, len(index))
        data["label"] = (data["future_return"] > 0).astype(float)
        result, summary = chronological_evaluation(data, min_train=600, retrain_every=100)
        self.assertEqual(result.index.min(), index[600])
        self.assertEqual(summary["observations"], 600)
        self.assertTrue(0 <= summary["accuracy"] <= 1)
        self.assertTrue(0 <= summary["balanced_accuracy"] <= 1)
        self.assertTrue(0 <= summary["brier_score"] <= 1)
        self.assertTrue((result["decision_threshold"] >= 0.55).all())

    @patch("model_training.yf.download", return_value=pd.DataFrame())
    def test_download_fails_cleanly_when_provider_is_empty(self, _download):
        with self.assertRaisesRegex(RuntimeError, "No training data"):
            download_dataset()


if __name__ == "__main__":
    unittest.main()
