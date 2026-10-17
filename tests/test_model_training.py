import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from model_training import (CONTEXT_FEATURES, FEATURES, RISK_FEATURES, build_context_features,
                            build_features, chronological_evaluation, dataset_provenance,
                            downside_risk_evaluation,
                            download_dataset, performance_metrics, portfolio_regime_evaluation,
                            regime_stability_evaluation, roc_auc, select_risk_threshold,
                            volatility_target_robustness, multi_asset_allocation_evaluation,
                            dynamic_growth_defense_evaluation, dynamic_allocation_uncertainty,
                            growth_sleeve_frontier,
                            external_growth_sleeve_frontier,
                            growth_sleeve_uncertainty,
                            experiment_registry,
                            merge_provenance_history,
                            risk_aware_sleeve_validation,
                            block_bootstrap_sharpe_difference, dynamic_allocation_sensitivity,
                            external_market_validation)


class ModelTrainingTests(unittest.TestCase):
    def test_dataset_fingerprint_is_stable_and_detects_revision(self):
        dates = pd.bdate_range("2026-01-01", periods=3)
        frame = pd.DataFrame({
            "date": [dates[0], dates[1], dates[2]],
            "ticker_id": ["SPY", "SPY", "SPY"],
            "future_return": [0.01, -0.02, 0.03],
        }).set_index(["date", "ticker_id"])
        first = dataset_provenance(frame)
        shuffled = dataset_provenance(frame.sample(frac=1, random_state=2))
        self.assertEqual(first["data_sha256"], shuffled["data_sha256"])
        revised = frame.copy()
        revised.iloc[1, 0] = -0.021
        self.assertNotEqual(first["data_sha256"], dataset_provenance(revised)["data_sha256"])
        self.assertEqual(first["rows"], 3)
        self.assertEqual(first["tickers"], 1)

    def test_provenance_history_deduplicates_reruns_and_numbers_revisions(self):
        current = {
            "provider": "test", "price_adjustment": "adjusted",
            "start_date": "2025-01-01", "end_date": "2026-01-02",
            "rows": 100, "tickers": 2, "data_sha256": "aaa",
        }
        history = merge_provenance_history(pd.DataFrame(), current)
        self.assertEqual(len(history), 1)
        self.assertEqual(int(history.iloc[0]["revision"]), 1)
        self.assertEqual(len(merge_provenance_history(history, current)), 1)
        revised = current | {"data_sha256": "bbb", "rows": 101}
        history = merge_provenance_history(history, revised)
        self.assertEqual(len(history), 2)
        self.assertEqual(int(history.iloc[-1]["revision"]), 2)
        next_date = current | {"end_date": "2026-01-05", "data_sha256": "ccc"}
        history = merge_provenance_history(history, next_date)
        self.assertEqual(int(history.iloc[-1]["revision"]), 1)

    def test_experiment_registry_is_unique_and_keeps_rejections(self):
        registry = experiment_registry("2026-10-09")
        self.assertTrue(registry["experiment_id"].is_unique)
        self.assertEqual(set(registry["decision"]), {"REJECTED", "PAPER_TRACKING"})
        self.assertGreaterEqual((registry["decision"] == "REJECTED").sum(), 1)
        self.assertTrue((registry["last_evaluated_market_date"] == "2026-10-09").all())
        risk_aware = registry.loc[registry["family"] == "Risk-aware sleeve"].iloc[0]
        self.assertEqual(risk_aware["decision"], "REJECTED")

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
        self.assertEqual(stats["worst_return"], -0.02)
        self.assertLessEqual(stats["expected_shortfall_5"], 0)

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

    def test_dynamic_growth_defense_is_fully_invested(self):
        dates = pd.bdate_range("2017-01-01", periods=1800)
        parts = []
        for offset, ticker in enumerate(("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")):
            frame = pd.DataFrame({
                "future_return": np.sin(np.arange(len(dates)) / (20 + offset)) * 0.01,
                "vol_21": 0.08 + offset * 0.02,
                "ret_63": np.sin(np.arange(len(dates)) / 45),
                "ma200_gap": np.cos(np.arange(len(dates)) / 55),
                "vix_level": 20 + 10 * (np.sin(np.arange(len(dates)) / 80) > 0),
                "credit_vs_treasury_21": np.sin(np.arange(len(dates)) / 70),
                "ticker_id": ticker,
            }, index=dates)
            parts.append(frame.set_index("ticker_id", append=True))
        panel = pd.concat(parts)
        panel.index.names = ["date", "ticker_id"]
        returns, summary = dynamic_growth_defense_evaluation(panel)
        self.assertFalse(returns.empty)
        self.assertTrue(returns["growth_share"].isin([0.0, 0.5]).all())
        self.assertEqual(len(summary[summary["scope"] == "Full history"]), 4)
        uncertainty = dynamic_allocation_uncertainty(returns)
        self.assertEqual(set(uncertainty["benchmark"]),
                         {"static_half_growth", "defensive_inverse_vol", "spy"})
        self.assertTrue((uncertainty["lower_95"] <= uncertainty["median"]).all())
        self.assertTrue((uncertainty["median"] <= uncertainty["upper_95"]).all())
        sensitivity = dynamic_allocation_sensitivity(panel)
        self.assertEqual(len(sensitivity), 9)
        self.assertEqual(set(sensitivity["rebalance_sessions"]), {5, 10, 20})
        self.assertTrue(np.isfinite(sensitivity.select_dtypes(include=["number"])).all().all())
        frontier = growth_sleeve_frontier(panel)
        self.assertEqual(set(frontier["growth_sleeve"]), {0.25, 0.5, 0.75})
        self.assertTrue(frontier["average_growth_share"].between(0, 0.75).all())
        self.assertTrue(np.isfinite(frontier.select_dtypes(include=["number"])).all().all())
        with self.assertRaises(ValueError):
            dynamic_growth_defense_evaluation(panel, growth_sleeve=1.1)
        with self.assertRaises(ValueError):
            dynamic_growth_defense_evaluation(panel, growth_sleeve=0.5, cautious_sleeve=0.75)
        cautious_returns, _ = dynamic_growth_defense_evaluation(
            panel, growth_sleeve=0.5, cautious_sleeve=0.25
        )
        self.assertTrue(cautious_returns["growth_share"].isin([0.0, 0.25, 0.5]).all())
        sleeve_uncertainty = growth_sleeve_uncertainty(panel, samples=100)
        self.assertEqual(len(sleeve_uncertainty), 2)
        self.assertEqual(set(sleeve_uncertainty["comparison_sleeve"]), {0.5, 0.75})

    def test_block_bootstrap_detects_clear_sharpe_advantage(self):
        rng = np.random.default_rng(22)
        candidate = pd.Series(rng.normal(0.01, 0.01, 500))
        benchmark = pd.Series(rng.normal(-0.005, 0.01, 500))
        result = block_bootstrap_sharpe_difference(candidate, benchmark, samples=300)
        self.assertGreater(result["lower_95"], 0)
        self.assertGreater(result["probability_positive"], 0.95)

    def test_external_validation_keeps_frozen_rule(self):
        dates = pd.bdate_range("2017-01-01", periods=1800)
        tickers = ("EFA", "EEM", "EWJ", "VGK", "TLT", "HYG", "GLD", "UUP")
        parts = []
        for offset, ticker in enumerate(tickers):
            frame = pd.DataFrame({
                "future_return": np.sin(np.arange(len(dates)) / (21 + offset)) * 0.01,
                "vol_21": 0.08 + offset * 0.01,
                "ret_63": np.sin(np.arange(len(dates)) / 45),
                "ma200_gap": np.cos(np.arange(len(dates)) / 55),
                "vix_level": 20 + 10 * (np.sin(np.arange(len(dates)) / 80) > 0),
                "credit_vs_treasury_21": np.sin(np.arange(len(dates)) / 70),
                "ticker_id": ticker,
            }, index=dates)
            parts.append(frame.set_index("ticker_id", append=True))
        panel = pd.concat(parts)
        panel.index.names = ["date", "ticker_id"]
        result = external_market_validation(panel)
        self.assertEqual(set(result["market"]), {"EFA", "EEM", "EWJ", "VGK"})
        self.assertTrue((result["years_tested"] >= 5).all())
        frontier = external_growth_sleeve_frontier(panel)
        self.assertEqual(len(frontier), 12)
        self.assertEqual(set(frontier["growth_sleeve"]), {0.25, 0.5, 0.75})
        self.assertEqual(set(frontier["market"]), {"EFA", "EEM", "EWJ", "VGK"})
        self.assertTrue(np.isfinite(frontier.select_dtypes(include=["number"])).all().all())
        uncertainty = growth_sleeve_uncertainty(panel, samples=100)
        self.assertEqual(len(uncertainty), 8)
        self.assertEqual(set(uncertainty["market"]), {"EFA", "EEM", "EWJ", "VGK"})
        risk_aware = risk_aware_sleeve_validation(panel)
        self.assertEqual(len(risk_aware), 12)
        self.assertEqual(set(risk_aware["strategy"]),
                         {"risk_aware_25_50", "fixed_25", "fixed_50"})
        self.assertTrue(np.isfinite(risk_aware.select_dtypes(include=["number"])).all().all())


if __name__ == "__main__":
    unittest.main()
