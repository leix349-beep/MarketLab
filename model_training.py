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
                "sharpe": 0.0, "drawdown": 0.0, "calmar": 0.0}
    wealth = (1 + returns).cumprod()
    drawdown = float((wealth / wealth.cummax() - 1).min())
    annual_return = float(wealth.iloc[-1] ** (periods_per_year / len(returns)) - 1)
    volatility = float(returns.std() * np.sqrt(periods_per_year))
    sharpe = float(returns.mean() / returns.std() * np.sqrt(periods_per_year)) if returns.std() else 0.0
    calmar = annual_return / abs(drawdown) if drawdown < 0 else 0.0
    return {"return": float(wealth.iloc[-1] - 1), "annual_return": annual_return,
            "volatility": volatility, "sharpe": sharpe, "drawdown": drawdown, "calmar": calmar}


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


def download_dataset() -> pd.DataFrame:
    parts = []
    frames: dict[str, pd.DataFrame] = {}
    for ticker in (*TRAIN_TICKERS, *CONTEXT_TICKERS):
        frame = yf.download(ticker, period="10y", auto_adjust=True, progress=False)
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        if frame.empty or "Close" not in frame:
            print(f"Skipping {ticker}: no usable training history")
            continue
        frames[ticker] = frame
    context = build_context_features(frames)
    for ticker in TRAIN_TICKERS:
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
    coefficient_parts = []
    available_tickers = list(data.index.get_level_values("ticker_id").unique())
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
    report = render_report(results, risk_results, context_results, coefficients, market_date)
    (OUTPUT_DIR / "latest.md").write_text(report, encoding="utf-8")
    history = OUTPUT_DIR / "history"
    history.mkdir(exist_ok=True)
    (history / f"{market_date}.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
