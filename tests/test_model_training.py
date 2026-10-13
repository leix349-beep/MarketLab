import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from model_training import (CONTEXT_FEATURES, FEATURES, RISK_FEATURES, build_context_features,
                            build_features, chronological_evaluation, downside_risk_evaluation,
                            download_dataset, performance_metrics, portfolio_regime_evaluation,
                            regime_stability_evaluation, roc_auc, select_risk_threshold,
                            volatility_target_robustness, multi_asset_allocation_evaluation)


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

    def test_nested_threshold_does_not_look_at_outer_test_labels(self):
        rng = np.random.default_rng(12)
        index = pd.bdate_range("2014-01-01", periods=1200)
        data = pd.DataFrame(rng.normal(size=(len(index), len(RISK_FEATURES))), index=index,
                            columns=RISK_FEATURES)
        data["future_return"] = rng.normal(0.001, 0.025, len(index))
        data["risk_label"] = (data["future_return"] <= -0.02).astype(float)
        first, _ = downside_risk_evaluation(data, min_train=600, retrain_every=100,
                                             nested_threshold=True)
        changed = data.copy()
        changed.iloc[600:, changed.columns.get_loc("future_return")] *= -1
        changed.iloc[600:, changed.columns.get_loc("risk_label")] = 1 - changed.iloc[600:]["risk_label"]
        second, _ = downside_risk_evaluation(changed, min_train=600, retrain_every=100,
                                              nested_threshold=True)
        pd.testing.assert_series_equal(first["risk_threshold"].iloc[:100],
                                       second["risk_threshold"].iloc[:100])
        pd.testing.assert_series_equal(first["risk_probability"].iloc[:100],
                                       second["risk_probability"].iloc[:100])

    def test_threshold_selector_can_choose_no_filter(self):
        rng = np.random.default_rng(13)
        index = pd.bdate_range("2015-01-01", periods=900)
        train = pd.DataFrame(rng.normal(size=(len(index), len(RISK_FEATURES))), index=index,
                             columns=RISK_FEATURES)
        train["future_return"] = 0.002
        train["risk_label"] = 0.0
        # Add both classes so logistic fitting is meaningful while remaining invested is optimal.
        train.loc[train.index[::20], "risk_label"] = 1.0
        threshold = select_risk_threshold(train, RISK_FEATURES)
        self.assertIn(threshold, [float(value) for value in np.arange(0.10, 0.51, 0.05)] + [1.0])

    def test_portfolio_weights_and_metrics_are_bounded(self):
        index = pd.bdate_range("2020-01-01", periods=500)
        evaluated = pd.DataFrame({
            "vol_21": np.linspace(0.08, 0.30, len(index)),
            "future_return": np.sin(np.arange(len(index)) / 20) * 0.02,
            "risk_signal": (np.arange(len(index)) % 11 == 0).astype(int),
            "risk_probability": 0.15 + (np.arange(len(index)) % 20) / 100,
            "risk_threshold": 0.25,
        }, index=index)
        sampled, summary = portfolio_regime_evaluation(evaluated)
        self.assertTrue(sampled["model_weight"].between(0, 1).all())
        self.assertTrue(sampled["smooth_weight"].between(0, 1).all())
        self.assertTrue((sampled["model_weight"] <= sampled["vol_target_weight"]).all())
        self.assertTrue((sampled["smooth_weight"] <= sampled["vol_target_weight"]).all())
        self.assertTrue(all(np.isfinite(value) for value in summary.values()))

    def test_regime_audit_uses_observable_states(self):
        index = pd.bdate_range("2018-01-01", periods=400)
        portfolio = pd.DataFrame({
            "market_ma_gap": np.sin(np.arange(len(index)) / 40) * 0.03,
            "vix_level": np.where(np.arange(len(index)) % 7 == 0, 0.30, 0.18),
            "vol_21": np.linspace(0.08, 0.30, len(index)),
            "model_return": 0.001,
            "smooth_return": 0.0009,
            "vol_target_return": 0.0008,
            "buy_hold_return": 0.0012,
        }, index=index)
        regimes = regime_stability_evaluation(portfolio)
        self.assertGreaterEqual(len(regimes), 5)
        self.assertTrue((regimes["observations"] >= 20).all())
        self.assertTrue(regimes.filter(like="sharpe").apply(np.isfinite).all().all())

    def test_volatility_target_audits_assets_and_time_periods(self):
        dates = pd.bdate_range("2018-01-01", periods=1500)
        parts = []
        for ticker, scale in (("SPY", 1.0), ("QQQ", 1.4), ("XLF", 1.2)):
            frame = pd.DataFrame({
                "vol_21": 0.10 * scale + 0.04 * np.abs(np.sin(np.arange(len(dates)) / 50)),
                "future_return": 0.002 + scale * np.sin(np.arange(len(dates)) / 30) * 0.015,
                "ticker_id": ticker,
            }, index=dates)
            parts.append(frame.set_index("ticker_id", append=True))
        panel = pd.concat(parts)
        panel.index.names = ["date", "ticker_id"]
        result = volatility_target_robustness(panel)
        self.assertEqual(set(result[result["scope"] == "Asset"]["label"]), {"SPY", "QQQ", "XLF"})
        self.assertGreaterEqual(len(result[result["scope"] == "Calendar year"]), 5)
        self.assertTrue(result.filter(like="sharpe").apply(np.isfinite).all().all())

    def test_multi_asset_allocation_uses_bounded_observable_weights(self):
        dates = pd.bdate_range("2017-01-01", periods=1800)
        parts = []
        for offset, ticker in enumerate(("SPY", "QQQ", "IWM", "XLK", "XLF", "XLE")):
            frame = pd.DataFrame({
                "future_return": np.sin(np.arange(len(dates)) / (20 + offset)) * 0.02,
                "vol_21": 0.10 + offset * 0.02,
                "ret_63": np.sin(np.arange(len(dates)) / 50),
                "ma200_gap": np.cos(np.arange(len(dates)) / 60),
                "ticker_id": ticker,
            }, index=dates)
            parts.append(frame.set_index("ticker_id", append=True))
        panel = pd.concat(parts)
        panel.index.names = ["date", "ticker_id"]
        returns, summary = multi_asset_allocation_evaluation(panel)
        self.assertFalse(returns.empty)
        self.assertTrue(returns["trend_exposure"].between(0, 1).all())
        self.assertTrue(returns["active_assets"].between(0, 6).all())
        self.assertEqual(len(summary[summary["scope"] == "Full history"]), 4)
        self.assertTrue(summary.filter(items=["sharpe", "drawdown"]).apply(np.isfinite).all().all())
        diversified_returns, diversified_summary = multi_asset_allocation_evaluation(
            panel, tickers=("SPY", "IWM", "XLE")
        )
        self.assertFalse(diversified_returns.empty)
        self.assertEqual(len(diversified_summary[diversified_summary["scope"] == "Full history"]), 4)


if __name__ == "__main__":
    unittest.main()
