"""Train and evaluate a small, explainable market model.

The model predicts whether the next five trading days have a positive return.
Evaluation is strictly chronological: every prediction is produced by a model
that has only seen earlier observations. No orders are placed.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

TRAIN_TICKERS = ("SPY", "QQQ", "IWM", "XLK", "XLF", "XLE")
DIVERSIFIED_TICKERS = ("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")
EXTERNAL_GROWTH_TICKERS = ("EFA", "EEM", "EWJ", "VGK")
FEATURES = ("ret_5", "ret_21", "ma_gap", "rsi14", "vol_21", "drawdown_63")
RISK_FEATURES = FEATURES + ("ret_63", "ma200_gap", "vol_ratio", "downside_vol_21")
CONTEXT_TICKERS = ("TLT", "HYG", "UUP", "GLD", "^VIX")
CONTEXT_FEATURES = ("market_ret_21", "market_ma_gap", "credit_vs_treasury_21",
                    "dollar_ret_21", "gold_ret_21", "vix_level", "vix_change_5",
                    "breadth_above_ma60")
CONTEXT_RISK_FEATURES = RISK_FEATURES + CONTEXT_FEATURES
OUTPUT_DIR = Path("published_research/model_training")


def performance_metrics(returns: pd.Series, periods_per_year: float = 252 / 5) -> dict[str, float]:
    """Risk/return metrics for non-overlapping five-session observations."""
    returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
    if returns.empty:
        return {"return": 0.0, "annual_return": 0.0, "volatility": 0.0,
                "sharpe": 0.0, "drawdown": 0.0, "calmar": 0.0,
                "sortino": 0.0, "expected_shortfall_5": 0.0, "worst_return": 0.0}
    wealth = (1 + returns).cumprod()
    drawdown = float((wealth / wealth.cummax() - 1).min())
    annual_return = float(wealth.iloc[-1] ** (periods_per_year / len(returns)) - 1)
    volatility = float(returns.std() * np.sqrt(periods_per_year))
    sharpe = float(returns.mean() / returns.std() * np.sqrt(periods_per_year)) if returns.std() else 0.0
    calmar = annual_return / abs(drawdown) if drawdown < 0 else 0.0
    downside_deviation = float(np.sqrt(np.mean(np.minimum(returns, 0) ** 2)) *
                               np.sqrt(periods_per_year))
    sortino = float(returns.mean() * periods_per_year / downside_deviation) if downside_deviation else 0.0
    tail_cutoff = returns.quantile(0.05)
    expected_shortfall = float(returns[returns <= tail_cutoff].mean())
    return {"return": float(wealth.iloc[-1] - 1), "annual_return": annual_return,
            "volatility": volatility, "sharpe": sharpe, "drawdown": drawdown, "calmar": calmar,
            "sortino": sortino, "expected_shortfall_5": expected_shortfall,
            "worst_return": float(returns.min())}


def build_features(frame: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    """Create features known at the close and a future-return label."""
    close = frame["Close"].astype(float).dropna()
    returns = close.pct_change()
    delta = close.diff()
    gains = delta.clip(lower=0).rolling(14).mean()
    losses = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gains / losses.replace(0, np.nan)
    rsi = (100 - 100 / (1 + rs)).fillna(50) / 100
    result = pd.DataFrame(index=close.index)
    result["ret_5"] = close.pct_change(5)
    result["ret_21"] = close.pct_change(21)
    result["ma_gap"] = close.rolling(20).mean() / close.rolling(60).mean() - 1
    result["rsi14"] = rsi
    result["vol_21"] = returns.rolling(21).std() * np.sqrt(252)
    result["drawdown_63"] = close / close.rolling(63).max() - 1
    result["ret_63"] = close.pct_change(63)
    result["ma200_gap"] = close / close.rolling(200).mean() - 1
    long_vol = returns.rolling(63).std() * np.sqrt(252)
    result["vol_ratio"] = result["vol_21"] / long_vol.replace(0, np.nan)
    result["downside_vol_21"] = returns.clip(upper=0).rolling(21).std() * np.sqrt(252)
    result["future_return"] = close.shift(-horizon) / close - 1
    result["label"] = (result["future_return"] > 0).astype(float)
    result["risk_label"] = (result["future_return"] <= -0.02).astype(float)
    result.loc[close.shift(-horizon).isna(), ["future_return", "label", "risk_label"]] = np.nan
    # Keep the direction-model history unchanged when longer-horizon candidate
    # features are added. Each candidate drops only the columns it actually uses.
    return result.dropna(subset=list(FEATURES) + ["future_return", "label", "risk_label"])


def build_context_features(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create cross-asset state variables using only same-day or earlier closes."""
    required = {"SPY", "TLT", "HYG", "UUP", "GLD", "^VIX"}
    if not required.issubset(frames):
        return pd.DataFrame()
    closes = {}
    for ticker, frame in frames.items():
        if frame.empty or "Close" not in frame:
            continue
        closes[ticker] = frame["Close"].astype(float)
    if not required.issubset(closes):
        return pd.DataFrame()
    prices = pd.concat(closes, axis=1, sort=False).sort_index().ffill(limit=3)
    result = pd.DataFrame(index=prices.index)
    result["market_ret_21"] = prices["SPY"].pct_change(21)
    result["market_ma_gap"] = prices["SPY"].rolling(20).mean() / prices["SPY"].rolling(60).mean() - 1
    result["credit_vs_treasury_21"] = prices["HYG"].pct_change(21) - prices["TLT"].pct_change(21)
    result["dollar_ret_21"] = prices["UUP"].pct_change(21)
    result["gold_ret_21"] = prices["GLD"].pct_change(21)
    result["vix_level"] = prices["^VIX"] / 100
    result["vix_change_5"] = prices["^VIX"].pct_change(5)
    breadth_members = [ticker for ticker in TRAIN_TICKERS if ticker in prices]
    breadth = pd.concat(
        [(prices[ticker] > prices[ticker].rolling(60).mean()).astype(float) for ticker in breadth_members],
        axis=1,
    )
    result["breadth_above_ma60"] = breadth.mean(axis=1)
    return result.replace([np.inf, -np.inf], np.nan)


@dataclass
class LogisticModel:
    mean: np.ndarray
    scale: np.ndarray
    weights: np.ndarray

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        z = np.clip(((x - self.mean) / self.scale) @ self.weights[:-1] + self.weights[-1], -30, 30)
        return 1 / (1 + np.exp(-z))


def fit_logistic(x: np.ndarray, y: np.ndarray, iterations: int = 800,
                 learning_rate: float = 0.08, regularization: float = 0.02) -> LogisticModel:
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1
    design = np.column_stack([(x - mean) / scale, np.ones(len(x))])
    weights = np.zeros(design.shape[1])
    for _ in range(iterations):
        probability = 1 / (1 + np.exp(-np.clip(design @ weights, -30, 30)))
        penalty = np.r_[weights[:-1], 0.0] * regularization
        weights -= learning_rate * (design.T @ (probability - y) / len(y) + penalty)
    return LogisticModel(mean, scale, weights)


def chronological_evaluation(dataset: pd.DataFrame, min_train: int = 756,
                             retrain_every: int = 63, threshold: float = 0.55,
                             embargo_days: int = 5, fee: float = 0.001,
                             minimum_edge: float = 0.03) -> tuple[pd.DataFrame, dict]:
    """Expanding-window predictions; test rows are never used before prediction."""
    data = dataset.sort_index().copy()
    if len(data) < min_train + retrain_every:
        raise ValueError("Not enough observations for chronological evaluation.")
    probabilities = pd.Series(np.nan, index=data.index, dtype=float)
    decision_thresholds = pd.Series(np.nan, index=data.index, dtype=float)
    for start in range(min_train, len(data), retrain_every):
        end = min(start + retrain_every, len(data))
        # Labels use the next five sessions. Excluding the final training rows
        # prevents their label period from crossing into the unseen test block.
        train = data.iloc[:start - embargo_days]
        model = fit_logistic(train[list(FEATURES)].to_numpy(), train["label"].to_numpy())
        probabilities.iloc[start:end] = model.predict_proba(data.iloc[start:end][list(FEATURES)].to_numpy())
        # A fixed 55% threshold can mean permanent exposure in assets that rise
        # more than 55% of the time. Require an edge over the observed training
        # base rate so the model must add information beyond "always bullish".
        decision_thresholds.iloc[start:end] = max(threshold, float(train["label"].mean()) + minimum_edge)
    evaluated = data.loc[probabilities.notna()].copy()
    evaluated["probability"] = probabilities.dropna()
    evaluated["prediction"] = (evaluated["probability"] >= 0.5).astype(int)
    evaluated["decision_threshold"] = decision_thresholds.dropna()
    evaluated["position"] = (evaluated["probability"] >= evaluated["decision_threshold"]).astype(float)
    evaluated["strategy_return"] = evaluated["position"] * evaluated["future_return"]
    active = evaluated[evaluated["position"] > 0]
    sampled = evaluated.iloc[::5]
    turnover = sampled["position"].diff().abs().fillna(sampled["position"])
    sampled = sampled.copy()
    sampled["strategy_return_net"] = sampled["strategy_return"] - turnover * fee
    strategy_stats = performance_metrics(sampled["strategy_return_net"])
    benchmark_stats = performance_metrics(sampled["future_return"])
    positives = evaluated["label"] == 1
    negatives = ~positives
    sensitivity = float((evaluated.loc[positives, "prediction"] == 1).mean()) if positives.any() else 0.0
    specificity = float((evaluated.loc[negatives, "prediction"] == 0).mean()) if negatives.any() else 0.0
    base_rate = float(evaluated["label"].mean())
    naive_accuracy = max(base_rate, 1 - base_rate)
    summary = {
        "observations": int(len(evaluated)),
        "accuracy": float((evaluated["prediction"] == evaluated["label"]).mean()),
        "naive_accuracy": naive_accuracy,
        "accuracy_edge": float((evaluated["prediction"] == evaluated["label"]).mean()) - naive_accuracy,
        "balanced_accuracy": (sensitivity + specificity) / 2,
        "brier_score": float(((evaluated["probability"] - evaluated["label"]) ** 2).mean()),
        "signal_rate": float(evaluated["position"].mean()),
        "signal_win_rate": float((active["future_return"] > 0).mean()) if len(active) else 0.0,
        "strategy_return": strategy_stats["return"],
        "strategy_annual_return": strategy_stats["annual_return"],
        "strategy_volatility": strategy_stats["volatility"],
        "strategy_sharpe": strategy_stats["sharpe"],
        "maximum_drawdown": strategy_stats["drawdown"],
        "strategy_calmar": strategy_stats["calmar"],
        "benchmark_return": benchmark_stats["return"],
        "benchmark_annual_return": benchmark_stats["annual_return"],
        "benchmark_volatility": benchmark_stats["volatility"],
        "benchmark_sharpe": benchmark_stats["sharpe"],
        "benchmark_drawdown": benchmark_stats["drawdown"],
        "benchmark_calmar": benchmark_stats["calmar"],
        "threshold": threshold,
        "average_decision_threshold": float(evaluated["decision_threshold"].mean()),
        "minimum_edge": minimum_edge,
        "fee": fee,
    }
    return evaluated, summary


def roc_auc(y: pd.Series, score: pd.Series) -> float:
    """Rank-based ROC AUC without an additional machine-learning dependency."""
    y = y.astype(int)
    positives = int(y.sum())
    negatives = len(y) - positives
    if positives == 0 or negatives == 0:
        return 0.5
    ranks = score.rank(method="average")
    return float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def select_risk_threshold(train: pd.DataFrame, feature_names: tuple[str, ...],
                          embargo_days: int = 5, fee: float = 0.001) -> float:
    """Choose an execution threshold inside training data only.

    The final 20% of the outer training window acts as an inner validation set.
    A value of 1.0 is an explicit no-filter fallback (remain invested).
    """
    validation_size = max(126, int(len(train) * 0.20))
    split = len(train) - validation_size
    if split - embargo_days < 252:
        return 1.0
    inner_train = train.iloc[:split - embargo_days]
    validation = train.iloc[split:]
    model = fit_logistic(inner_train[list(feature_names)].to_numpy(), inner_train["risk_label"].to_numpy())
    probabilities = model.predict_proba(validation[list(feature_names)].to_numpy())
    candidates = [float(value) for value in np.arange(0.10, 0.51, 0.05)] + [1.0]
    best_threshold, best_score = 1.0, -np.inf
    for candidate in candidates:
        position = pd.Series((probabilities < candidate).astype(float), index=validation.index)
        sampled = validation.assign(position=position).iloc[::5].copy()
        turnover = sampled["position"].diff().abs().fillna(1 - sampled["position"])
        net_return = sampled["position"] * sampled["future_return"] - turnover * fee
        stats = performance_metrics(net_return)
        # Sharpe is primary; Calmar breaks near-ties toward smaller drawdowns.
        score = stats["sharpe"] + 0.01 * stats["calmar"]
        if score > best_score:
            best_threshold, best_score = candidate, score
    return best_threshold


def downside_risk_evaluation(dataset: pd.DataFrame, min_train: int = 756,
                             retrain_every: int = 63, embargo_days: int = 5,
                             minimum_risk_probability: float = 0.20,
                             risk_margin: float = 0.05, fee: float = 0.001,
                             feature_names: tuple[str, ...] = RISK_FEATURES,
                             nested_threshold: bool = False) -> tuple[pd.DataFrame, dict]:
    """Test a candidate filter that exits when five-day downside risk is elevated."""
    data = dataset.sort_index().dropna(subset=list(feature_names) + ["future_return", "risk_label"]).copy()
    if len(data) < min_train + retrain_every:
        raise ValueError("Not enough observations for downside-risk evaluation.")
    probabilities = pd.Series(np.nan, index=data.index, dtype=float)
    thresholds = pd.Series(np.nan, index=data.index, dtype=float)
    for start in range(min_train, len(data), retrain_every):
        end = min(start + retrain_every, len(data))
        train = data.iloc[:start - embargo_days]
        model = fit_logistic(train[list(feature_names)].to_numpy(), train["risk_label"].to_numpy())
        probabilities.iloc[start:end] = model.predict_proba(data.iloc[start:end][list(feature_names)].to_numpy())
        if nested_threshold:
            chosen_threshold = select_risk_threshold(train, feature_names, embargo_days, fee)
        else:
            chosen_threshold = max(minimum_risk_probability,
                                   float(train["risk_label"].mean()) + risk_margin)
        thresholds.iloc[start:end] = chosen_threshold
    evaluated = data.loc[probabilities.notna()].copy()
    evaluated["risk_probability"] = probabilities.dropna()
    evaluated["risk_threshold"] = thresholds.dropna()
    evaluated["risk_signal"] = (evaluated["risk_probability"] >= evaluated["risk_threshold"]).astype(int)
    evaluated["position"] = 1.0 - evaluated["risk_signal"]
    active_risk = evaluated["risk_label"] == 1
    predicted_risk = evaluated["risk_signal"] == 1
    recall = float(evaluated.loc[active_risk, "risk_signal"].mean()) if active_risk.any() else 0.0
    precision = float(evaluated.loc[predicted_risk, "risk_label"].mean()) if predicted_risk.any() else 0.0
    sampled = evaluated.iloc[::5].copy()
    turnover = sampled["position"].diff().abs().fillna(1 - sampled["position"])
    sampled["strategy_return_net"] = sampled["position"] * sampled["future_return"] - turnover * fee
    strategy = performance_metrics(sampled["strategy_return_net"])
    benchmark = performance_metrics(sampled["future_return"])
    summary = {
        "observations": int(len(evaluated)),
        "risk_event_rate": float(evaluated["risk_label"].mean()),
        "roc_auc": roc_auc(evaluated["risk_label"], evaluated["risk_probability"]),
        "risk_recall": recall,
        "risk_precision": precision,
        "exit_rate": float(predicted_risk.mean()),
        "average_risk_threshold": float(evaluated["risk_threshold"].mean()),
        "fallback_rate": float((evaluated["risk_threshold"] == 1.0).mean()),
        "strategy_return": strategy["return"],
        "strategy_annual_return": strategy["annual_return"],
        "strategy_volatility": strategy["volatility"],
        "strategy_sharpe": strategy["sharpe"],
        "maximum_drawdown": strategy["drawdown"],
        "strategy_calmar": strategy["calmar"],
        "benchmark_return": benchmark["return"],
        "benchmark_annual_return": benchmark["annual_return"],
        "benchmark_volatility": benchmark["volatility"],
        "benchmark_sharpe": benchmark["sharpe"],
        "benchmark_drawdown": benchmark["drawdown"],
        "benchmark_calmar": benchmark["calmar"],
        "fee": fee,
    }
    return evaluated, summary


def portfolio_regime_evaluation(evaluated: pd.DataFrame, target_volatility: float = 0.12,
                                defensive_weight: float = 0.25,
                                fee: float = 0.001) -> tuple[pd.DataFrame, dict]:
    """Convert validated SPY risk probabilities into portfolio exposure.

    The comparison separates the contribution of ordinary volatility targeting
    from the incremental contribution of the learned cross-asset risk signal.
    """
    required = {"vol_21", "future_return", "risk_signal", "risk_probability", "risk_threshold"}
    if not required.issubset(evaluated.columns):
        raise ValueError("Portfolio evaluation is missing required validated columns.")
    sampled = evaluated.sort_index().iloc[::5].copy()
    sampled["vol_target_weight"] = (target_volatility / sampled["vol_21"]).clip(0, 1).fillna(0)
    multiplier = np.where(sampled["risk_signal"] == 1, defensive_weight, 1.0)
    sampled["model_weight"] = sampled["vol_target_weight"] * multiplier
    risk_intensity = ((sampled["risk_probability"] - 0.5 * sampled["risk_threshold"]) /
                      sampled["risk_threshold"].replace(0, np.nan)).clip(0, 1).fillna(0)
    sampled["smooth_weight"] = sampled["vol_target_weight"] * (1 - (1 - defensive_weight) * risk_intensity)
    vol_turnover = sampled["vol_target_weight"].diff().abs().fillna(sampled["vol_target_weight"])
    model_turnover = sampled["model_weight"].diff().abs().fillna(sampled["model_weight"])
    smooth_turnover = sampled["smooth_weight"].diff().abs().fillna(sampled["smooth_weight"])
    sampled["buy_hold_return"] = sampled["future_return"]
    sampled["vol_target_return"] = (sampled["vol_target_weight"] * sampled["future_return"] -
                                     vol_turnover * fee)
    sampled["model_return"] = sampled["model_weight"] * sampled["future_return"] - model_turnover * fee
    sampled["smooth_return"] = sampled["smooth_weight"] * sampled["future_return"] - smooth_turnover * fee
    buy_hold = performance_metrics(sampled["buy_hold_return"])
    vol_target = performance_metrics(sampled["vol_target_return"])
    model = performance_metrics(sampled["model_return"])
    smooth = performance_metrics(sampled["smooth_return"])
    summary = {
        "target_volatility": target_volatility,
        "defensive_weight": defensive_weight,
        "fee": fee,
        "average_model_weight": float(sampled["model_weight"].mean()),
        "average_smooth_weight": float(sampled["smooth_weight"].mean()),
        "average_vol_target_weight": float(sampled["vol_target_weight"].mean()),
    }
    for prefix, stats in (("smooth", smooth), ("model", model),
                          ("vol_target", vol_target), ("buy_hold", buy_hold)):
        for key, value in stats.items():
            summary[f"{prefix}_{key}"] = value
    return sampled, summary


def regime_stability_evaluation(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Measure conditional performance using states observable at each decision date."""
    required = {"market_ma_gap", "vix_level", "vol_21", "model_return", "smooth_return",
                "vol_target_return", "buy_hold_return"}
    if not required.issubset(portfolio.columns):
        raise ValueError("Regime audit is missing required portfolio or context columns.")
    data = portfolio.sort_index().copy()
    # The realized-volatility cutoff uses only prior observations, not a
    # full-sample percentile that would leak knowledge of the future.
    prior_median = data["vol_21"].expanding(min_periods=26).median().shift(1)
    definitions = {
        "Market trend": {
            "Positive": data["market_ma_gap"] >= 0,
            "Negative": data["market_ma_gap"] < 0,
        },
        "VIX state": {
            "Below 25": data["vix_level"] < 0.25,
            "25 or above": data["vix_level"] >= 0.25,
        },
        "Realized volatility": {
            "At/below prior median": data["vol_21"] <= prior_median,
            "Above prior median": data["vol_21"] > prior_median,
        },
    }
    rows = []
    for dimension, states in definitions.items():
        for state, mask in states.items():
            subset = data.loc[mask.fillna(False)]
            if len(subset) < 20:
                continue
            row = {"dimension": dimension, "state": state, "observations": int(len(subset))}
            for name, column in (("smooth", "smooth_return"), ("model", "model_return"),
                                 ("vol_target", "vol_target_return"),
                                 ("buy_hold", "buy_hold_return")):
                stats = performance_metrics(subset[column])
                row[f"{name}_annual_return"] = stats["annual_return"]
                row[f"{name}_volatility"] = stats["volatility"]
                row[f"{name}_sharpe"] = stats["sharpe"]
            rows.append(row)
    return pd.DataFrame(rows)


def volatility_target_robustness(data: pd.DataFrame, target_volatility: float = 0.12,
                                 fee: float = 0.001) -> pd.DataFrame:
    """Audit a fixed volatility target across assets and calendar periods."""
    if not isinstance(data.index, pd.MultiIndex) or "ticker_id" not in data.index.names:
        raise ValueError("Robustness audit requires a ticker-indexed training panel.")
    samples = []
    rows = []
    for ticker in data.index.get_level_values("ticker_id").unique():
        asset = data.xs(ticker, level="ticker_id").sort_index()
        if not {"vol_21", "future_return"}.issubset(asset.columns):
            continue
        sampled = asset[["vol_21", "future_return"]].dropna().iloc[::5].copy()
        if len(sampled) < 20:
            continue
        sampled["weight"] = (target_volatility / sampled["vol_21"]).clip(0, 1)
        turnover = sampled["weight"].diff().abs().fillna(sampled["weight"])
        sampled["vol_target_return"] = sampled["weight"] * sampled["future_return"] - turnover * fee
        sampled["buy_hold_return"] = sampled["future_return"]
        sampled["ticker"] = ticker
        samples.append(sampled)
        target = performance_metrics(sampled["vol_target_return"])
        benchmark = performance_metrics(sampled["buy_hold_return"])
        rows.append({
            "scope": "Asset", "label": ticker, "observations": len(sampled),
            "average_exposure": sampled["weight"].mean(),
            **{f"vol_target_{key}": value for key, value in target.items()},
            **{f"buy_hold_{key}": value for key, value in benchmark.items()},
        })
    if not samples:
        return pd.DataFrame()
    panel = pd.concat(samples)
    basket = panel.groupby(level=0)[["vol_target_return", "buy_hold_return"]].mean()
    for year, period in basket.groupby(basket.index.year):
        if len(period) < 20:
            continue
        target = performance_metrics(period["vol_target_return"])
        benchmark = performance_metrics(period["buy_hold_return"])
        rows.append({
            "scope": "Calendar year", "label": str(year), "observations": len(period),
            "average_exposure": float("nan"),
            **{f"vol_target_{key}": value for key, value in target.items()},
            **{f"buy_hold_{key}": value for key, value in benchmark.items()},
        })
    return pd.DataFrame(rows)


def multi_asset_allocation_evaluation(data: pd.DataFrame, fee: float = 0.001,
                                      tickers: tuple[str, ...] = TRAIN_TICKERS
                                      ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Test a fixed trend/inverse-volatility allocation without fitted parameters."""
    required = {"future_return", "vol_21", "ret_63", "ma200_gap"}
    if not required.issubset(data.columns):
        raise ValueError("Allocation audit is missing required observable features.")
    tickers = [ticker for ticker in tickers
               if ticker in data.index.get_level_values("ticker_id")]
    if "SPY" not in tickers or len(tickers) < 2:
        return pd.DataFrame(), pd.DataFrame()
    panels = {column: data[column].unstack("ticker_id").reindex(columns=tickers)
              for column in required}
    valid = pd.concat(panels, axis=1).dropna()
    if valid.empty:
        return pd.DataFrame(), pd.DataFrame()
    dates = valid.index[::5]
    future = panels["future_return"].loc[dates]
    inverse_vol = 1 / panels["vol_21"].loc[dates].replace(0, np.nan)
    inverse_vol_weights = inverse_vol.div(inverse_vol.sum(axis=1), axis=0).fillna(0)
    trend_mask = ((panels["ret_63"].loc[dates] > 0) &
                  (panels["ma200_gap"].loc[dates] > 0)).astype(float)
    trend_scores = inverse_vol * trend_mask
    trend_weights = trend_scores.div(trend_scores.sum(axis=1), axis=0).fillna(0)
    equal_weights = pd.DataFrame(1 / len(tickers), index=dates, columns=tickers)

    def net_return(weights: pd.DataFrame) -> pd.Series:
        turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
        return (weights * future).sum(axis=1) - turnover * fee

    returns = pd.DataFrame({
        "trend_risk_parity": net_return(trend_weights),
        "inverse_volatility": net_return(inverse_vol_weights),
        "equal_weight": net_return(equal_weights),
        "spy": future["SPY"],
    })
    returns["trend_exposure"] = trend_weights.sum(axis=1)
    returns["active_assets"] = (trend_weights > 0).sum(axis=1)
    rows = []
    for name in ("trend_risk_parity", "inverse_volatility", "equal_weight", "spy"):
        stats = performance_metrics(returns[name])
        rows.append({"scope": "Full history", "period": "All", "strategy": name,
                     "observations": len(returns), **stats})
    for year, period in returns.groupby(returns.index.year):
        if len(period) < 20:
            continue
        for name in ("trend_risk_parity", "inverse_volatility", "equal_weight", "spy"):
            stats = performance_metrics(period[name])
            rows.append({"scope": "Calendar year", "period": str(year), "strategy": name,
                         "observations": len(period), **stats})
    return returns, pd.DataFrame(rows)


def dynamic_growth_defense_evaluation(data: pd.DataFrame, fee: float = 0.001,
                                      rebalance_every: int = 1,
                                      tickers: tuple[str, ...] = DIVERSIFIED_TICKERS,
                                      growth_ticker: str = "SPY",
                                      growth_sleeve: float = 0.5,
                                      ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Switch a fixed growth sleeve into a diversified defensive sleeve."""
    if rebalance_every < 1:
        raise ValueError("Rebalance interval must be at least one five-session block.")
    if not 0 <= growth_sleeve <= 1:
        raise ValueError("Growth sleeve must be between zero and one.")
    required = {"future_return", "vol_21", "ret_63", "ma200_gap"}
    if not required.issubset(data.columns):
        raise ValueError("Dynamic allocation is missing required observable features.")
    expected_tickers = tuple(tickers)
    tickers = [ticker for ticker in expected_tickers
               if ticker in data.index.get_level_values("ticker_id")]
    if set(tickers) != set(expected_tickers) or growth_ticker not in tickers:
        return pd.DataFrame(), pd.DataFrame()
    panels = {column: data[column].unstack("ticker_id").reindex(columns=tickers)
              for column in required}
    valid = pd.concat(panels, axis=1).dropna()
    if valid.empty:
        return pd.DataFrame(), pd.DataFrame()
    dates = valid.index[::5]
    future = panels["future_return"].loc[dates]
    inverse_vol = 1 / panels["vol_21"].loc[dates].replace(0, np.nan)
    defensive = inverse_vol.div(inverse_vol.sum(axis=1), axis=0).fillna(0)
    growth = pd.DataFrame(0.0, index=dates, columns=tickers)
    growth[growth_ticker] = 1.0
    static_blend = growth_sleeve * growth + (1 - growth_sleeve) * defensive
    positive_trend = ((panels["ret_63"].loc[dates, growth_ticker] > 0) &
                      (panels["ma200_gap"].loc[dates, growth_ticker] > 0)).astype(float)
    growth_share = positive_trend * growth_sleeve
    dynamic = defensive.mul(1 - growth_share, axis=0) + growth.mul(growth_share, axis=0)

    def hold_weights(weights: pd.DataFrame) -> pd.DataFrame:
        if rebalance_every == 1:
            return weights
        return weights.iloc[::rebalance_every].reindex(weights.index).ffill()

    defensive = hold_weights(defensive)
    static_blend = hold_weights(static_blend)
    dynamic = hold_weights(dynamic)

    def net_return(weights: pd.DataFrame) -> pd.Series:
        turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
        return (weights * future).sum(axis=1) - turnover * fee

    returns = pd.DataFrame({
        "dynamic_growth_defense": net_return(dynamic),
        "static_half_growth": net_return(static_blend),
        "defensive_inverse_vol": net_return(defensive),
        "spy": future[growth_ticker],
        "growth_share": growth_share,
    })
    rows = []
    for name in ("dynamic_growth_defense", "static_half_growth", "defensive_inverse_vol", "spy"):
        rows.append({"scope": "Full history", "period": "All", "strategy": name,
                     "observations": len(returns), **performance_metrics(returns[name])})
    for year, period in returns.groupby(returns.index.year):
        if len(period) < 20:
            continue
        for name in ("dynamic_growth_defense", "static_half_growth", "defensive_inverse_vol", "spy"):
            rows.append({"scope": "Calendar year", "period": str(year), "strategy": name,
                         "observations": len(period), **performance_metrics(period[name])})
    return returns, pd.DataFrame(rows)


def growth_sleeve_frontier(data: pd.DataFrame) -> pd.DataFrame:
    """Compare three predeclared growth sleeves without selecting a winner."""
    rows = []
    for sleeve in (0.25, 0.50, 0.75):
        returns, summary = dynamic_growth_defense_evaluation(
            data, growth_sleeve=sleeve
        )
        if summary.empty:
            continue
        full = summary[summary["scope"] == "Full history"].set_index("strategy")
        yearly = summary[summary["scope"] == "Calendar year"].pivot(
            index="period", columns="strategy", values="sharpe"
        )
        annual = summary[(summary["scope"] == "Calendar year") &
                         (summary["strategy"] == "dynamic_growth_defense")]
        candidate = full.loc["dynamic_growth_defense"]
        rows.append({
            "growth_sleeve": sleeve,
            "observations": int(candidate["observations"]),
            "annual_return": candidate["annual_return"],
            "volatility": candidate["volatility"],
            "sharpe": candidate["sharpe"],
            "drawdown": candidate["drawdown"],
            "calmar": candidate["calmar"],
            "expected_shortfall_5": candidate["expected_shortfall_5"],
            "years_higher_sharpe_than_spy": int(
                (yearly["dynamic_growth_defense"] > yearly["spy"]).sum()
            ),
            "years_tested": int(len(yearly)),
            "positive_years": int((annual["annual_return"] > 0).sum()),
            "worst_calendar_return": float(annual["annual_return"].min()),
            "average_growth_share": float(returns["growth_share"].mean()),
        })
    return pd.DataFrame(rows)


def external_market_validation(data: pd.DataFrame) -> pd.DataFrame:
    """Apply the frozen growth/defense rule to previously unused equity regions."""
    rows = []
    defensive_assets = ("TLT", "HYG", "GLD", "UUP")
    for growth_ticker in EXTERNAL_GROWTH_TICKERS:
        universe = (growth_ticker, *defensive_assets)
        _, summary = dynamic_growth_defense_evaluation(
            data, tickers=universe, growth_ticker=growth_ticker
        )
        if summary.empty:
            continue
        full = summary[summary["scope"] == "Full history"].set_index("strategy")
        yearly = summary[summary["scope"] == "Calendar year"].pivot(
            index="period", columns="strategy", values="sharpe"
        )
        rows.append({
            "market": growth_ticker,
            "observations": int(full.loc["dynamic_growth_defense", "observations"]),
            "dynamic_annual_return": full.loc["dynamic_growth_defense", "annual_return"],
            "dynamic_sharpe": full.loc["dynamic_growth_defense", "sharpe"],
            "dynamic_drawdown": full.loc["dynamic_growth_defense", "drawdown"],
            "dynamic_sortino": full.loc["dynamic_growth_defense", "sortino"],
            "dynamic_expected_shortfall_5": full.loc["dynamic_growth_defense", "expected_shortfall_5"],
            "dynamic_worst_return": full.loc["dynamic_growth_defense", "worst_return"],
            "benchmark_annual_return": full.loc["spy", "annual_return"],
            "benchmark_sharpe": full.loc["spy", "sharpe"],
            "benchmark_drawdown": full.loc["spy", "drawdown"],
            "benchmark_sortino": full.loc["spy", "sortino"],
            "benchmark_expected_shortfall_5": full.loc["spy", "expected_shortfall_5"],
            "benchmark_worst_return": full.loc["spy", "worst_return"],
            "years_higher_sharpe": int((yearly["dynamic_growth_defense"] > yearly["spy"]).sum()),
            "years_tested": int(len(yearly)),
        })
    return pd.DataFrame(rows)


def external_growth_sleeve_frontier(data: pd.DataFrame) -> pd.DataFrame:
    """Apply each predeclared growth sleeve to untouched regional markets."""
    rows = []
    defensive_assets = ("TLT", "HYG", "GLD", "UUP")
    for sleeve in (0.25, 0.50, 0.75):
        for growth_ticker in EXTERNAL_GROWTH_TICKERS:
            universe = (growth_ticker, *defensive_assets)
            _, summary = dynamic_growth_defense_evaluation(
                data, tickers=universe, growth_ticker=growth_ticker,
                growth_sleeve=sleeve
            )
            if summary.empty:
                continue
            full = summary[summary["scope"] == "Full history"].set_index("strategy")
            yearly = summary[summary["scope"] == "Calendar year"].pivot(
                index="period", columns="strategy", values="sharpe"
            )
            candidate = full.loc["dynamic_growth_defense"]
            benchmark = full.loc["spy"]
            rows.append({
                "growth_sleeve": sleeve,
                "market": growth_ticker,
                "observations": int(candidate["observations"]),
                "annual_return": candidate["annual_return"],
                "sharpe": candidate["sharpe"],
                "drawdown": candidate["drawdown"],
                "expected_shortfall_5": candidate["expected_shortfall_5"],
                "benchmark_annual_return": benchmark["annual_return"],
                "benchmark_sharpe": benchmark["sharpe"],
                "benchmark_drawdown": benchmark["drawdown"],
                "benchmark_expected_shortfall_5": benchmark["expected_shortfall_5"],
                "years_higher_sharpe": int(
                    (yearly["dynamic_growth_defense"] > yearly["spy"]).sum()
                ),
                "years_tested": int(len(yearly)),
            })
    return pd.DataFrame(rows)


def dynamic_allocation_sensitivity(data: pd.DataFrame) -> pd.DataFrame:
    """Stress the fixed dynamic rule across costs and rebalance intervals."""
    rows = []
    for fee in (0.0005, 0.001, 0.002):
        for rebalance_every in (1, 2, 4):
            _, summary = dynamic_growth_defense_evaluation(
                data, fee=fee, rebalance_every=rebalance_every
            )
            if summary.empty:
                continue
            result = summary[(summary["scope"] == "Full history") &
                             (summary["strategy"] == "dynamic_growth_defense")].iloc[0]
            rows.append({
                "fee": fee,
                "rebalance_sessions": rebalance_every * 5,
                "annual_return": result["annual_return"],
                "volatility": result["volatility"],
                "sharpe": result["sharpe"],
                "drawdown": result["drawdown"],
                "calmar": result["calmar"],
            })
    return pd.DataFrame(rows)


def block_bootstrap_sharpe_difference(candidate: pd.Series, benchmark: pd.Series,
                                      samples: int = 1000, block_size: int = 4,
                                      seed: int = 20261013) -> dict[str, float]:
    """Paired circular-block bootstrap for five-session Sharpe differences."""
    paired = pd.concat([candidate, benchmark], axis=1).dropna().to_numpy(dtype=float)
    if len(paired) < block_size * 5:
        raise ValueError("Too few paired observations for block bootstrap.")
    rng = np.random.default_rng(seed)
    differences = []
    block_offsets = np.arange(block_size)
    blocks_needed = int(np.ceil(len(paired) / block_size))

    def sharpe(values: np.ndarray) -> float:
        deviation = values.std(ddof=1)
        return float(values.mean() / deviation * np.sqrt(252 / 5)) if deviation else 0.0

    for _ in range(samples):
        starts = rng.integers(0, len(paired), size=blocks_needed)
        indices = ((starts[:, None] + block_offsets) % len(paired)).ravel()[:len(paired)]
        draw = paired[indices]
        differences.append(sharpe(draw[:, 0]) - sharpe(draw[:, 1]))
    values = np.asarray(differences)
    lower, median, upper = np.quantile(values, [0.025, 0.5, 0.975])
    return {"lower_95": float(lower), "median": float(median), "upper_95": float(upper),
            "probability_positive": float((values > 0).mean()), "samples": samples,
            "block_size": block_size}


def growth_sleeve_uncertainty(data: pd.DataFrame, samples: int = 1000) -> pd.DataFrame:
    """Test whether the 25% sleeve has a credible Sharpe edge over larger sleeves."""
    rows = []
    markets = (("SPY", DIVERSIFIED_TICKERS),) + tuple(
        (ticker, (ticker, "TLT", "HYG", "GLD", "UUP"))
        for ticker in EXTERNAL_GROWTH_TICKERS
    )
    for market, universe in markets:
        candidate, _ = dynamic_growth_defense_evaluation(
            data, tickers=universe, growth_ticker=market, growth_sleeve=0.25
        )
        if candidate.empty:
            continue
        for comparison in (0.50, 0.75):
            benchmark, _ = dynamic_growth_defense_evaluation(
                data, tickers=universe, growth_ticker=market,
                growth_sleeve=comparison
            )
            if benchmark.empty:
                continue
            result = block_bootstrap_sharpe_difference(
                candidate["dynamic_growth_defense"],
                benchmark["dynamic_growth_defense"], samples=samples
            )
            rows.append({
                "market": market,
                "candidate_sleeve": 0.25,
                "comparison_sleeve": comparison,
                **result,
            })
    return pd.DataFrame(rows)


def dynamic_allocation_uncertainty(returns: pd.DataFrame) -> pd.DataFrame:
    """Quantify uncertainty in the dynamic candidate versus each baseline."""
    if returns.empty or "dynamic_growth_defense" not in returns:
        return pd.DataFrame()
    rows = []
    for benchmark in ("static_half_growth", "defensive_inverse_vol", "spy"):
        result = block_bootstrap_sharpe_difference(
            returns["dynamic_growth_defense"], returns[benchmark]
        )
        rows.append({"benchmark": benchmark, **result})
    return pd.DataFrame(rows)


def download_dataset() -> pd.DataFrame:
    parts = []
    frames: dict[str, pd.DataFrame] = {}
    download_tickers = tuple(dict.fromkeys((*TRAIN_TICKERS, *CONTEXT_TICKERS,
                                           *EXTERNAL_GROWTH_TICKERS)))
    for ticker in download_tickers:
        frame = yf.download(ticker, period="10y", auto_adjust=True, progress=False)
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        if frame.empty or "Close" not in frame:
            print(f"Skipping {ticker}: no usable training history")
            continue
        frames[ticker] = frame
    context = build_context_features(frames)
    research_tickers = tuple(dict.fromkeys((*TRAIN_TICKERS, *DIVERSIFIED_TICKERS,
                                           *EXTERNAL_GROWTH_TICKERS)))
    for ticker in research_tickers:
        if ticker not in frames:
            continue
        frame = frames[ticker]
        features = build_features(frame)
        if features.empty:
            print(f"Skipping {ticker}: insufficient feature history")
            continue
        if not context.empty:
            features = features.join(context.reindex(features.index).ffill(limit=3), how="left")
        features["ticker"] = ticker
        features.index = pd.MultiIndex.from_arrays(
            [features.index, np.repeat(ticker, len(features))], names=["date", "ticker_id"]
        )
        parts.append(features)
    if not parts:
        raise RuntimeError("No training data was downloaded.")
    return pd.concat(parts).sort_index()


def render_report(results: pd.DataFrame, risk_results: pd.DataFrame,
                  context_results: pd.DataFrame,
                  portfolio_result: dict | None,
                  regime_results: pd.DataFrame,
                  volatility_results: pd.DataFrame,
                  allocation_results: pd.DataFrame,
                  diversified_results: pd.DataFrame,
                  dynamic_results: pd.DataFrame,
                  dynamic_uncertainty: pd.DataFrame,
                  dynamic_sensitivity: pd.DataFrame,
                  growth_frontier: pd.DataFrame,
                  external_growth_frontier: pd.DataFrame,
                  growth_uncertainty: pd.DataFrame,
                  external_results: pd.DataFrame,
                  coefficients: pd.Series, market_date: str) -> str:
    rows = "\n".join(f"| {name} | {value:+.4f} |" for name, value in coefficients.items())
    result_rows = "\n".join(
        f"| {row.ticker} | {row.observations:,} | {row.accuracy:.1%} | {row.accuracy_edge:+.1%} | "
        f"{row.balanced_accuracy:.1%} | {row.signal_rate:.1%} | "
        f"{row.signal_win_rate:.1%} | {row.strategy_return:.1%} | {row.benchmark_return:.1%} | "
        f"{row.maximum_drawdown:.1%} |" for row in results.itertuples(index=False)
    )
    predictive_assets = int(((results["accuracy_edge"] > 0) & (results["balanced_accuracy"] > 0.5)).sum())
    outperforming_assets = int((results["strategy_return"] > results["benchmark_return"]).sum())
    risk_adjusted_assets = int((results["strategy_sharpe"] > results["benchmark_sharpe"]).sum())
    accepted = predictive_assets >= len(results) / 2 and risk_adjusted_assets >= len(results) / 2
    verdict = "PASS FOR FURTHER PAPER TESTING" if accepted else "REJECTED AS A TRADING MODEL"
    risk_rows = "\n".join(
        f"| {row.ticker} | {row.strategy_annual_return:.1%} | {row.benchmark_annual_return:.1%} | "
        f"{row.strategy_volatility:.1%} | {row.benchmark_volatility:.1%} | {row.strategy_sharpe:.2f} | "
        f"{row.benchmark_sharpe:.2f} | {row.strategy_calmar:.2f} | {row.benchmark_calmar:.2f} |"
        for row in results.itertuples(index=False)
    )
    filter_rows = "\n".join(
        f"| {row.ticker} | {row.risk_event_rate:.1%} | {row.roc_auc:.3f} | {row.risk_recall:.1%} | "
        f"{row.exit_rate:.1%} | {row.strategy_annual_return:.1%} | {row.strategy_sharpe:.2f} | "
        f"{row.benchmark_sharpe:.2f} | {row.maximum_drawdown:.1%} | {row.benchmark_drawdown:.1%} |"
        for row in risk_results.itertuples(index=False)
    )
    informative_filters = int((risk_results["roc_auc"] > 0.52).sum())
    better_sharpe_filters = int((risk_results["strategy_sharpe"] > risk_results["benchmark_sharpe"]).sum())
    lower_drawdown_filters = int((risk_results["maximum_drawdown"] > risk_results["benchmark_drawdown"]).sum())
    filter_pass = (informative_filters >= len(risk_results) / 2 and
                   better_sharpe_filters >= len(risk_results) / 2 and
                   lower_drawdown_filters >= len(risk_results) / 2)
    filter_verdict = "PASS FOR FURTHER PAPER TESTING" if filter_pass else "REJECTED AS A TRADING MODEL"
    if context_results.empty:
        context_section = """## Cross-Asset Risk Candidate: NOT RUN

One or more required context series were unavailable, so no stale or partial result was substituted.
"""
    else:
        context_rows = "\n".join(
            f"| {row.ticker} | {row.roc_auc:.3f} | {row.risk_recall:.1%} | {row.exit_rate:.1%} | "
            f"{row.average_risk_threshold:.2f} | {row.fallback_rate:.1%} | "
            f"{row.strategy_annual_return:.1%} | {row.strategy_sharpe:.2f} | {row.benchmark_sharpe:.2f} | "
            f"{row.maximum_drawdown:.1%} | {row.benchmark_drawdown:.1%} |"
            for row in context_results.itertuples(index=False)
        )
        context_informative = int((context_results["roc_auc"] > 0.52).sum())
        context_sharpe = int((context_results["strategy_sharpe"] > context_results["benchmark_sharpe"]).sum())
        context_drawdown = int((context_results["maximum_drawdown"] > context_results["benchmark_drawdown"]).sum())
        context_pass = (context_informative >= len(context_results) / 2 and
                        context_sharpe >= len(context_results) / 2 and
                        context_drawdown >= len(context_results) / 2)
        context_verdict = "PASS FOR FURTHER PAPER TESTING" if context_pass else "REJECTED AS A TRADING MODEL"
        context_section = f"""## Cross-Asset Risk Candidate: {context_verdict}

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **{context_informative} / {len(context_results)}**
- Assets with higher Sharpe than buy and hold: **{context_sharpe} / {len(context_results)}**
- Assets with smaller maximum drawdown: **{context_drawdown} / {len(context_results)}**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{context_rows}
"""
    if portfolio_result is None:
        portfolio_section = """## Portfolio Regime Candidate: NOT RUN

The validated SPY context series was unavailable; no partial portfolio result was substituted.
"""
    else:
        portfolio_pass = (
            portfolio_result["smooth_sharpe"] > portfolio_result["vol_target_sharpe"] and
            portfolio_result["smooth_sharpe"] > portfolio_result["buy_hold_sharpe"] and
            portfolio_result["smooth_drawdown"] > portfolio_result["vol_target_drawdown"] and
            portfolio_result["smooth_annual_return"] > 0
        )
        portfolio_verdict = "PASS FOR FURTHER PAPER TESTING" if portfolio_pass else "REJECTED AS A TRADING MODEL"
        portfolio_section = f"""## Portfolio Regime Candidate: {portfolio_verdict}

The learned risk signal controls exposure on top of a fixed {portfolio_result['target_volatility']:.0%} volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | {portfolio_result['smooth_annual_return']:.1%} | {portfolio_result['smooth_volatility']:.1%} | {portfolio_result['smooth_sharpe']:.2f} | {portfolio_result['smooth_drawdown']:.1%} | {portfolio_result['smooth_calmar']:.2f} |
| ML binary allocation | {portfolio_result['model_annual_return']:.1%} | {portfolio_result['model_volatility']:.1%} | {portfolio_result['model_sharpe']:.2f} | {portfolio_result['model_drawdown']:.1%} | {portfolio_result['model_calmar']:.2f} |
| Volatility target only | {portfolio_result['vol_target_annual_return']:.1%} | {portfolio_result['vol_target_volatility']:.1%} | {portfolio_result['vol_target_sharpe']:.2f} | {portfolio_result['vol_target_drawdown']:.1%} | {portfolio_result['vol_target_calmar']:.2f} |
| Buy and hold | {portfolio_result['buy_hold_annual_return']:.1%} | {portfolio_result['buy_hold_volatility']:.1%} | {portfolio_result['buy_hold_sharpe']:.2f} | {portfolio_result['buy_hold_drawdown']:.1%} | {portfolio_result['buy_hold_calmar']:.2f} |

- Average smooth ML exposure: **{portfolio_result['average_smooth_weight']:.1%}**
- Average binary ML exposure: **{portfolio_result['average_model_weight']:.1%}**
- Average volatility-target exposure: **{portfolio_result['average_vol_target_weight']:.1%}**
"""
    if regime_results.empty:
        stability_section = """## Observable-Regime Stability Audit: NOT RUN

Insufficient validated portfolio observations were available.
"""
    else:
        regime_rows = "\n".join(
            f"| {row.dimension} | {row.state} | {row.observations} | "
            f"{row.smooth_annual_return:.1%} | {row.smooth_sharpe:.2f} | "
            f"{row.vol_target_annual_return:.1%} | {row.vol_target_sharpe:.2f} | "
            f"{row.buy_hold_annual_return:.1%} | {row.buy_hold_sharpe:.2f} |"
            for row in regime_results.itertuples(index=False)
        )
        vol_wins = int((regime_results["vol_target_sharpe"] > regime_results["buy_hold_sharpe"]).sum())
        ml_wins = int((regime_results["smooth_sharpe"] > regime_results["vol_target_sharpe"]).sum())
        stability_section = f"""## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **{vol_wins} / {len(regime_results)}** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **{ml_wins} / {len(regime_results)}** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{regime_rows}

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.
"""
    if volatility_results.empty:
        volatility_section = """## Volatility-Target Robustness: NOT RUN

Insufficient multi-asset history was available.
"""
    else:
        asset_rows = volatility_results[volatility_results["scope"] == "Asset"]
        year_rows = volatility_results[volatility_results["scope"] == "Calendar year"]
        asset_wins = int((asset_rows["vol_target_sharpe"] > asset_rows["buy_hold_sharpe"]).sum())
        year_wins = int((year_rows["vol_target_sharpe"] > year_rows["buy_hold_sharpe"]).sum())
        drawdown_wins = int((asset_rows["vol_target_drawdown"] > asset_rows["buy_hold_drawdown"]).sum())
        volatility_pass = (asset_wins >= len(asset_rows) / 2 and
                           year_wins >= len(year_rows) / 2 and
                           drawdown_wins >= len(asset_rows) / 2)
        volatility_verdict = "PASS FOR PAPER TESTING" if volatility_pass else "NOT YET ROBUST"
        volatility_rows = "\n".join(
            f"| {row.scope} | {row.label} | {row.observations} | "
            f"{row.vol_target_annual_return:.1%} | {row.vol_target_sharpe:.2f} | "
            f"{row.vol_target_drawdown:.1%} | {row.buy_hold_annual_return:.1%} | "
            f"{row.buy_hold_sharpe:.2f} | {row.buy_hold_drawdown:.1%} |"
            for row in volatility_results.itertuples(index=False)
        )
        volatility_section = f"""## Volatility-Target Robustness: {volatility_verdict}

- Higher Sharpe across assets: **{asset_wins} / {len(asset_rows)}**
- Smaller drawdown across assets: **{drawdown_wins} / {len(asset_rows)}**
- Higher Sharpe across calendar years: **{year_wins} / {len(year_rows)}**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{volatility_rows}

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.
"""
    if allocation_results.empty:
        allocation_section = """## Multi-Asset Allocation Candidate: NOT RUN

Insufficient aligned asset history was available.
"""
    else:
        full = allocation_results[allocation_results["scope"] == "Full history"]
        yearly = allocation_results[allocation_results["scope"] == "Calendar year"]
        candidate = full[full["strategy"] == "trend_risk_parity"].iloc[0]
        inverse = full[full["strategy"] == "inverse_volatility"].iloc[0]
        equal = full[full["strategy"] == "equal_weight"].iloc[0]
        spy = full[full["strategy"] == "spy"].iloc[0]
        pivot = yearly.pivot(index="period", columns="strategy", values="sharpe")
        year_wins = int((pivot["trend_risk_parity"] > pivot[["inverse_volatility", "equal_weight", "spy"]].max(axis=1)).sum())
        allocation_pass = (candidate["sharpe"] > max(inverse["sharpe"], equal["sharpe"], spy["sharpe"]) and
                           candidate["annual_return"] > 0 and
                           year_wins >= len(pivot) / 2)
        allocation_verdict = "PASS FOR PAPER TESTING" if allocation_pass else "REJECTED AS A TRADING MODEL"
        allocation_rows = "\n".join(
            f"| {row.strategy.replace('_', ' ').title()} | {row.annual_return:.1%} | "
            f"{row.volatility:.1%} | {row.sharpe:.2f} | {row.drawdown:.1%} | {row.calmar:.2f} |"
            for row in full.itertuples(index=False)
        )
        allocation_section = f"""## Multi-Asset Allocation Candidate: {allocation_verdict}

- Trend/inverse-volatility allocation has the best yearly Sharpe in **{year_wins} / {len(pivot)}** years.
- Assets are selected only when their 63-day return and price-versus-200-day-average are positive; otherwise that sleeve stays in cash.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
{allocation_rows}

The rule is fixed before evaluation, uses only decision-date information, rebalances every five sessions, and deducts 0.10% turnover cost.
"""
    if diversified_results.empty:
        diversified_section = """## Diversified Allocation Candidate: NOT RUN

One or more required asset classes were unavailable.
"""
    else:
        full = diversified_results[diversified_results["scope"] == "Full history"]
        yearly = diversified_results[diversified_results["scope"] == "Calendar year"]
        candidate = full[full["strategy"] == "trend_risk_parity"].iloc[0]
        alternatives = full[full["strategy"] != "trend_risk_parity"]
        pivot = yearly.pivot(index="period", columns="strategy", values="sharpe")
        year_wins = int((pivot["trend_risk_parity"] > pivot.drop(columns="trend_risk_parity").max(axis=1)).sum())
        diversified_pass = (candidate["sharpe"] > alternatives["sharpe"].max() and
                            candidate["annual_return"] > 0 and
                            year_wins >= len(pivot) / 2)
        diversified_verdict = "PASS FOR PAPER TESTING" if diversified_pass else "REJECTED AS A TRADING MODEL"
        diversified_rows = "\n".join(
            f"| {row.strategy.replace('_', ' ').title()} | {row.annual_return:.1%} | "
            f"{row.volatility:.1%} | {row.sharpe:.2f} | {row.drawdown:.1%} | {row.calmar:.2f} |"
            for row in full.itertuples(index=False)
        )
        diversified_section = f"""## Diversified Allocation Candidate: {diversified_verdict}

This test uses SPY, IWM, long Treasuries, high-yield credit, gold and the U.S. dollar instead of six mostly correlated equity sleeves.

- Trend/inverse-volatility allocation has the best yearly Sharpe in **{year_wins} / {len(pivot)}** years.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
{diversified_rows}
"""
    if dynamic_results.empty:
        dynamic_section = """## Dynamic Growth / Defense Candidate: NOT RUN

The aligned diversified history was unavailable.
"""
    else:
        full = dynamic_results[dynamic_results["scope"] == "Full history"]
        yearly = dynamic_results[dynamic_results["scope"] == "Calendar year"]
        candidate = full[full["strategy"] == "dynamic_growth_defense"].iloc[0]
        alternatives = full[full["strategy"] != "dynamic_growth_defense"]
        pivot = yearly.pivot(index="period", columns="strategy", values="sharpe")
        year_wins = int((pivot["dynamic_growth_defense"] > pivot.drop(columns="dynamic_growth_defense").max(axis=1)).sum())
        uncertainty_pass = (not dynamic_uncertainty.empty and
                            (dynamic_uncertainty["lower_95"] > 0).all())
        dynamic_pass = (candidate["sharpe"] > alternatives["sharpe"].max() and
                        candidate["annual_return"] > 0 and
                        candidate["drawdown"] > full[full["strategy"] == "spy"]["drawdown"].iloc[0] and
                        year_wins >= len(pivot) / 2 and uncertainty_pass)
        dynamic_verdict = "PASS FOR PAPER TESTING" if dynamic_pass else "REJECTED AS A TRADING MODEL"
        dynamic_rows = "\n".join(
            f"| {row.strategy.replace('_', ' ').title()} | {row.annual_return:.1%} | "
            f"{row.volatility:.1%} | {row.sharpe:.2f} | {row.drawdown:.1%} | {row.calmar:.2f} |"
            for row in full.itertuples(index=False)
        )
        uncertainty_rows = "\n".join(
            f"| {row.benchmark.replace('_', ' ').title()} | {row.median:+.2f} | "
            f"[{row.lower_95:+.2f}, {row.upper_95:+.2f}] | {row.probability_positive:.1%} |"
            for row in dynamic_uncertainty.itertuples(index=False)
        ) if not dynamic_uncertainty.empty else "| Not available | — | — | — |"
        sensitivity_rows = "\n".join(
            f"| {row.fee:.2%} | {int(row.rebalance_sessions)} sessions | "
            f"{row.annual_return:.1%} | {row.sharpe:.2f} | {row.drawdown:.1%} |"
            for row in dynamic_sensitivity.itertuples(index=False)
        ) if not dynamic_sensitivity.empty else "| — | — | — | — | — |"
        sensitivity_pass = (not dynamic_sensitivity.empty and
                            (dynamic_sensitivity["annual_return"] > 0).all() and
                            (dynamic_sensitivity["sharpe"] > 1.0).all() and
                            (dynamic_sensitivity["drawdown"] > -0.20).all())
        dynamic_pass = dynamic_pass and sensitivity_pass
        dynamic_verdict = "PASS FOR PAPER TESTING" if dynamic_pass else "REJECTED AS A TRADING MODEL"
        dynamic_section = f"""## Dynamic Growth / Defense Candidate: {dynamic_verdict}

- The dynamic strategy has the best yearly Sharpe in **{year_wins} / {len(pivot)}** years.
- When SPY's 63-day return and price-versus-200-day average are positive, growth receives 50%; otherwise the diversified defensive sleeve receives 100%.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
{dynamic_rows}

### Paired block-bootstrap uncertainty

| Benchmark | Median Sharpe difference | 95% interval | Probability difference > 0 |
|---|---:|---:|---:|
{uncertainty_rows}

The resampling keeps four adjacent five-session observations together. A candidate passes only if every 95% interval remains above zero in addition to the chronological and yearly gates.

### Cost and rebalance sensitivity

| One-way cost | Rebalance interval | Annual return | Sharpe | Maximum drawdown |
|---:|---:|---:|---:|---:|
{sensitivity_rows}

The candidate must remain profitable, above 1.0 Sharpe and within a 20% drawdown in every predeclared stress scenario.
"""
    if growth_frontier.empty:
        frontier_section = """## Growth-Sleeve Risk / Return Frontier: NOT RUN

Insufficient aligned history was available.
"""
    else:
        frontier_rows = "\n".join(
            f"| {row.growth_sleeve:.0%} | {row.average_growth_share:.1%} | "
            f"{row.annual_return:.1%} | {row.volatility:.1%} | {row.sharpe:.2f} | "
            f"{row.drawdown:.1%} | {row.expected_shortfall_5:.1%} | "
            f"{int(row.positive_years)} / {int(row.years_tested)} | "
            f"{int(row.years_higher_sharpe_than_spy)} / {int(row.years_tested)} |"
            for row in growth_frontier.itertuples(index=False)
        )
        frontier_section = f"""## Growth-Sleeve Risk / Return Frontier

The trend rule, defensive basket, rebalance interval and costs are unchanged. Only three predeclared maximum growth sleeves are compared; no winner is promoted from this table alone.

| Max growth sleeve | Average growth exposure | Annual return | Volatility | Sharpe | Maximum drawdown | Worst-5% average | Positive years | Years beating SPY Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{frontier_rows}
"""
    if external_growth_frontier.empty:
        external_frontier_section = """## External Growth-Sleeve Validation: NOT RUN

The required regional ETF histories were unavailable.
"""
    else:
        external_frontier_rows = []
        for sleeve, group in external_growth_frontier.groupby("growth_sleeve"):
            sharpe_wins = int((group["sharpe"] > group["benchmark_sharpe"]).sum())
            drawdown_wins = int((group["drawdown"] > group["benchmark_drawdown"]).sum())
            tail_wins = int((group["expected_shortfall_5"] >
                             group["benchmark_expected_shortfall_5"]).sum())
            majority_years = int((group["years_higher_sharpe"] * 2 >=
                                  group["years_tested"]).sum())
            external_frontier_rows.append(
                f"| {sleeve:.0%} | {group['annual_return'].mean():.1%} | "
                f"{group['sharpe'].mean():.2f} | {group['drawdown'].min():.1%} | "
                f"{sharpe_wins} / {len(group)} | {drawdown_wins} / {len(group)} | "
                f"{tail_wins} / {len(group)} | {majority_years} / {len(group)} |"
            )
        external_frontier_section = f"""## External Growth-Sleeve Validation

The three U.S.-declared sleeve sizes are applied unchanged to EFA, EEM, EWJ and VGK. Averages summarize the four markets; no regional retuning is performed.

| Max growth sleeve | Avg annual return | Avg Sharpe | Worst market DD | Markets higher Sharpe | Markets smaller DD | Markets smaller tail loss | Markets winning most years |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(external_frontier_rows)}
"""
    if growth_uncertainty.empty:
        growth_uncertainty_section = """## Growth-Sleeve Statistical Uncertainty: NOT RUN

Insufficient paired observations were available.
"""
    else:
        significant = int((growth_uncertainty["lower_95"] > 0).sum())
        uncertainty_rows = "\n".join(
            f"| {row.market} | 25% vs {row.comparison_sleeve:.0%} | "
            f"{row.median:+.2f} | [{row.lower_95:+.2f}, {row.upper_95:+.2f}] | "
            f"{row.probability_positive:.1%} |"
            for row in growth_uncertainty.itertuples(index=False)
        )
        growth_uncertainty_section = f"""## Growth-Sleeve Statistical Uncertainty

- Comparisons with a 95% interval entirely above zero: **{significant} / {len(growth_uncertainty)}**

| Market | Comparison | Median Sharpe difference | 95% interval | Probability 25% is higher |
|---|---|---:|---:|---:|
{uncertainty_rows}

Paired circular-block resampling preserves four adjacent five-session observations. The 25% sleeve is not promoted unless the evidence is stable beyond point estimates.
"""
    if external_results.empty:
        external_section = """## External-Market Validation: NOT RUN

The required regional ETF histories were unavailable.
"""
    else:
        sharpe_wins = int((external_results["dynamic_sharpe"] > external_results["benchmark_sharpe"]).sum())
        drawdown_wins = int((external_results["dynamic_drawdown"] > external_results["benchmark_drawdown"]).sum())
        tail_wins = int((external_results["dynamic_expected_shortfall_5"] >
                         external_results["benchmark_expected_shortfall_5"]).sum())
        majority_years = int((external_results["years_higher_sharpe"] * 2 >=
                              external_results["years_tested"]).sum())
        external_pass = (sharpe_wins >= 3 and drawdown_wins >= 3 and
                         tail_wins >= 3 and majority_years >= 3)
        external_verdict = "PASS" if external_pass else "FAIL"
        external_rows = "\n".join(
            f"| {row.market} | {row.dynamic_annual_return:.1%} | {row.dynamic_sharpe:.2f} | "
            f"{row.dynamic_drawdown:.1%} | {row.dynamic_expected_shortfall_5:.1%} | "
            f"{row.benchmark_annual_return:.1%} | {row.benchmark_sharpe:.2f} | "
            f"{row.benchmark_drawdown:.1%} | {row.benchmark_expected_shortfall_5:.1%} | "
            f"{int(row.years_higher_sharpe)} / {int(row.years_tested)} |"
            for row in external_results.itertuples(index=False)
        )
        external_section = f"""## External-Market Validation: {external_verdict}

The U.S.-designed rule is frozen and applied without retuning to developed ex-U.S., emerging markets, Japan and Europe.

- Higher full-history Sharpe: **{sharpe_wins} / {len(external_results)}** markets
- Smaller maximum drawdown: **{drawdown_wins} / {len(external_results)}** markets
- Smaller average loss in the worst 5% of periods: **{tail_wins} / {len(external_results)}** markets
- Higher Sharpe in at least half of years: **{majority_years} / {len(external_results)}** markets

| Market | Dynamic ann. return | Dynamic Sharpe | Dynamic DD | Dynamic tail loss | Market ann. return | Market Sharpe | Market DD | Market tail loss | Years higher Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{external_rows}
"""
    return f"""# MarketLab Model Training — {market_date}

Chronological out-of-sample research result. This model does not place orders.

## Verdict: {verdict}

- Assets with predictive improvement over the naive baseline: **{predictive_assets} / {len(results)}**
- Assets outperforming buy and hold: **{outperforming_assets} / {len(results)}**
- Assets improving risk-adjusted return (Sharpe): **{risk_adjusted_assets} / {len(results)}**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{result_rows}

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{risk_rows}

## Downside-Risk Filter Candidate: {filter_verdict}

- Assets with ROC AUC above 0.52: **{informative_filters} / {len(risk_results)}**
- Assets with higher Sharpe than buy and hold: **{better_sharpe_filters} / {len(risk_results)}**
- Assets with smaller maximum drawdown: **{lower_drawdown_filters} / {len(risk_results)}**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{filter_rows}

{context_section}

{portfolio_section}

{stability_section}

{volatility_section}

{allocation_section}

{diversified_section}

{dynamic_section}

{frontier_section}

{external_frontier_section}

{growth_uncertainty_section}

{external_section}

## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
{rows}

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least {results.iloc[0]['threshold']:.0%} probability and a {results.iloc[0]['minimum_edge']:.0%} edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct {results.iloc[0]['fee']:.2%} when exposure changes. They remain historical research rather than evidence of future profit.
"""


def main() -> None:
    data = download_dataset()
    result_rows = []
    prediction_parts = []
    risk_result_rows = []
    risk_prediction_parts = []
    context_result_rows = []
    context_prediction_parts = []
    portfolio_result = None
    portfolio_predictions = None
    regime_results = pd.DataFrame()
    volatility_results = volatility_target_robustness(data)
    allocation_predictions, allocation_results = multi_asset_allocation_evaluation(data)
    diversified_predictions, diversified_results = multi_asset_allocation_evaluation(
        data, tickers=DIVERSIFIED_TICKERS
    )
    dynamic_predictions, dynamic_results = dynamic_growth_defense_evaluation(data)
    dynamic_uncertainty = dynamic_allocation_uncertainty(dynamic_predictions)
    dynamic_sensitivity = dynamic_allocation_sensitivity(data)
    growth_frontier = growth_sleeve_frontier(data)
    external_growth_frontier = external_growth_sleeve_frontier(data)
    growth_uncertainty = growth_sleeve_uncertainty(data)
    external_results = external_market_validation(data)
    coefficient_parts = []
    available_tickers = [ticker for ticker in TRAIN_TICKERS
                         if ticker in data.index.get_level_values("ticker_id")]
    for ticker in available_tickers:
        asset = data.xs(ticker, level="ticker_id").sort_index()
        evaluated, summary = chronological_evaluation(asset)
        summary["ticker"] = ticker
        result_rows.append(summary)
        evaluated = evaluated.copy()
        evaluated["ticker"] = ticker
        prediction_parts.append(evaluated.reset_index())
        risk_evaluated, risk_summary = downside_risk_evaluation(asset)
        risk_summary["ticker"] = ticker
        risk_result_rows.append(risk_summary)
        risk_evaluated = risk_evaluated.copy()
        risk_evaluated["ticker"] = ticker
        risk_prediction_parts.append(risk_evaluated.reset_index())
        if set(CONTEXT_RISK_FEATURES).issubset(asset.columns):
            context_evaluated, context_summary = downside_risk_evaluation(
                asset, feature_names=CONTEXT_RISK_FEATURES, nested_threshold=True
            )
            context_summary["ticker"] = ticker
            context_result_rows.append(context_summary)
            context_evaluated = context_evaluated.copy()
            context_evaluated["ticker"] = ticker
            context_prediction_parts.append(context_evaluated.reset_index())
            if ticker == "SPY":
                portfolio_predictions, portfolio_result = portfolio_regime_evaluation(context_evaluated)
                regime_results = regime_stability_evaluation(portfolio_predictions)
        model = fit_logistic(asset[list(FEATURES)].to_numpy(), asset["label"].to_numpy())
        coefficient_parts.append(pd.Series(model.weights[:-1], index=FEATURES, name=ticker))
    results = pd.DataFrame(result_rows)[["ticker", "observations", "accuracy", "naive_accuracy",
                                         "accuracy_edge", "balanced_accuracy", "brier_score", "signal_rate",
                                         "signal_win_rate", "strategy_return", "strategy_annual_return",
                                         "strategy_volatility", "strategy_sharpe", "maximum_drawdown",
                                         "strategy_calmar", "benchmark_return", "benchmark_annual_return",
                                         "benchmark_volatility", "benchmark_sharpe", "benchmark_drawdown",
                                         "benchmark_calmar", "threshold", "average_decision_threshold",
                                         "minimum_edge", "fee"]]
    coefficients = pd.concat(coefficient_parts, axis=1).mean(axis=1)
    risk_results = pd.DataFrame(risk_result_rows)
    context_results = pd.DataFrame(context_result_rows)
    market_date = pd.Timestamp(data.index.get_level_values("date").max()).date().isoformat()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.assign(market_date=market_date).to_csv(OUTPUT_DIR / "latest.csv", index=False)
    pd.concat(prediction_parts).sort_values(["date", "ticker"]).groupby("ticker").tail(100).to_csv(
        OUTPUT_DIR / "latest_predictions.csv", index=False
    )
    risk_results.assign(market_date=market_date).to_csv(OUTPUT_DIR / "latest_risk.csv", index=False)
    pd.concat(risk_prediction_parts).sort_values(["date", "ticker"]).groupby("ticker").tail(100).to_csv(
        OUTPUT_DIR / "latest_risk_predictions.csv", index=False
    )
    context_results.assign(market_date=market_date).to_csv(OUTPUT_DIR / "latest_context_risk.csv", index=False)
    if context_prediction_parts:
        context_predictions = pd.concat(context_prediction_parts).sort_values(["date", "ticker"])
        context_predictions.groupby("ticker").tail(100).to_csv(
            OUTPUT_DIR / "latest_context_risk_predictions.csv", index=False
        )
    else:
        pd.DataFrame().to_csv(OUTPUT_DIR / "latest_context_risk_predictions.csv", index=False)
    if portfolio_result is not None and portfolio_predictions is not None:
        pd.DataFrame([portfolio_result | {"market_date": market_date}]).to_csv(
            OUTPUT_DIR / "latest_portfolio.csv", index=False
        )
        portfolio_predictions.tail(200).to_csv(OUTPUT_DIR / "latest_portfolio_predictions.csv")
    else:
        pd.DataFrame().to_csv(OUTPUT_DIR / "latest_portfolio.csv", index=False)
        pd.DataFrame().to_csv(OUTPUT_DIR / "latest_portfolio_predictions.csv", index=False)
    regime_results.assign(market_date=market_date).to_csv(OUTPUT_DIR / "latest_regimes.csv", index=False)
    volatility_results.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_volatility_target.csv", index=False
    )
    allocation_results.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_multi_asset.csv", index=False
    )
    allocation_predictions.tail(200).to_csv(
        OUTPUT_DIR / "latest_multi_asset_predictions.csv"
    )
    diversified_results.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_diversified_allocation.csv", index=False
    )
    diversified_predictions.tail(200).to_csv(
        OUTPUT_DIR / "latest_diversified_allocation_predictions.csv"
    )
    dynamic_results.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_dynamic_allocation.csv", index=False
    )
    dynamic_predictions.tail(200).to_csv(
        OUTPUT_DIR / "latest_dynamic_allocation_predictions.csv"
    )
    dynamic_uncertainty.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_dynamic_uncertainty.csv", index=False
    )
    dynamic_sensitivity.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_dynamic_sensitivity.csv", index=False
    )
    growth_frontier.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_growth_sleeve_frontier.csv", index=False
    )
    external_growth_frontier.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_external_growth_sleeve_frontier.csv", index=False
    )
    growth_uncertainty.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_growth_sleeve_uncertainty.csv", index=False
    )
    external_results.assign(market_date=market_date).to_csv(
        OUTPUT_DIR / "latest_external_validation.csv", index=False
    )
    report = render_report(results, risk_results, context_results, portfolio_result,
                           regime_results, volatility_results, allocation_results, diversified_results,
                           dynamic_results, dynamic_uncertainty, dynamic_sensitivity, growth_frontier,
                           external_growth_frontier, growth_uncertainty, external_results,
                           coefficients, market_date)
    (OUTPUT_DIR / "latest.md").write_text(report, encoding="utf-8")
    history = OUTPUT_DIR / "history"
    history.mkdir(exist_ok=True)
    (history / f"{market_date}.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
