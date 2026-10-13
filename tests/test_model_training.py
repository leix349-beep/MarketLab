import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from model_training import (CONTEXT_FEATURES, FEATURES, RISK_FEATURES, build_context_features,
                            build_features, chronological_evaluation, downside_risk_evaluation,
                            download_dataset, performance_metrics, roc_auc)


class ModelTrainingTests(unittest.TestCase):
    def test_future_rows_are_removed(self):
        index = pd.bdate_range("2020-01-01", periods=300)
        frame = pd.DataFrame({"Close": np.linspace(100, 150, len(index))}, index=index)
        features = build_features(frame, horizon=5)
        self.assertLessEqual(features.index.max(), index[-6])
        self.assertTrue(features[list(FEATURES) + ["future_return", "label"]].notna().all().all())
        risk_ready = features.dropna(subset=list(RISK_FEATURES) + ["risk_label"])
        self.assertFalse(risk_ready.empty)
        self.assertTrue(risk_ready[list(RISK_FEATURES) + ["risk_label"]].notna().all().all())

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

    def test_risk_metrics_are_finite(self):
        stats = performance_metrics(pd.Series([0.01, -0.02, 0.015, 0.0]))
        self.assertTrue(all(np.isfinite(value) for value in stats.values()))
        self.assertLessEqual(stats["drawdown"], 0)

    def test_auc_and_downside_evaluation(self):
        self.assertAlmostEqual(roc_auc(pd.Series([0, 0, 1, 1]), pd.Series([0.1, 0.2, 0.8, 0.9])), 1.0)
        rng = np.random.default_rng(8)
        index = pd.bdate_range("2015-01-01", periods=1200)
        data = pd.DataFrame(rng.normal(size=(len(index), len(RISK_FEATURES))), index=index,
                            columns=RISK_FEATURES)
        data["future_return"] = rng.normal(0.001, 0.025, len(index))
        data["risk_label"] = (data["future_return"] <= -0.02).astype(float)
        result, summary = downside_risk_evaluation(data, min_train=600, retrain_every=100)
        self.assertEqual(result.index.min(), index[600])
        self.assertTrue(0 <= summary["roc_auc"] <= 1)
        self.assertTrue(((result["position"] == 0) | (result["position"] == 1)).all())

    def test_context_features_use_aligned_market_history(self):
        index = pd.bdate_range("2020-01-01", periods=260)
        frames = {}
        for offset, ticker in enumerate(("SPY", "QQQ", "IWM", "XLK", "XLF", "XLE",
                                         "TLT", "HYG", "UUP", "GLD", "^VIX")):
            close = 100 + offset + np.linspace(0, 30, len(index))
            frames[ticker] = pd.DataFrame({"Close": close}, index=index)
        context = build_context_features(frames).dropna()
        self.assertFalse(context.empty)
        self.assertTrue(context[list(CONTEXT_FEATURES)].notna().all().all())
        self.assertTrue(context["breadth_above_ma60"].between(0, 1).all())


if __name__ == "__main__":
    unittest.main()
