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
OUTPUT_DIR = Path("published_research/model_training")


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
    result["future_return"] = close.shift(-horizon) / close - 1
    result["label"] = (result["future_return"] > 0).astype(float)
    result.loc[close.shift(-horizon).isna(), ["future_return", "label"]] = np.nan
    return result.dropna()


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
    strategy_wealth = (1 + sampled["strategy_return_net"]).cumprod()
    benchmark_wealth = (1 + sampled["future_return"]).cumprod()
    drawdown = strategy_wealth / strategy_wealth.cummax() - 1
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
        "strategy_return": float(strategy_wealth.iloc[-1] - 1),
        "benchmark_return": float(benchmark_wealth.iloc[-1] - 1),
        "maximum_drawdown": float(drawdown.min()),
        "threshold": threshold,
        "average_decision_threshold": float(evaluated["decision_threshold"].mean()),
        "minimum_edge": minimum_edge,
        "fee": fee,
    }
    return evaluated, summary


def download_dataset() -> pd.DataFrame:
    parts = []
    for ticker in TRAIN_TICKERS:
        frame = yf.download(ticker, period="10y", auto_adjust=True, progress=False)
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        if frame.empty or "Close" not in frame:
            print(f"Skipping {ticker}: no usable training history")
            continue
        features = build_features(frame)
        if features.empty:
            print(f"Skipping {ticker}: insufficient feature history")
            continue
        features["ticker"] = ticker
        features.index = pd.MultiIndex.from_arrays(
            [features.index, np.repeat(ticker, len(features))], names=["date", "ticker_id"]
        )
        parts.append(features)
    if not parts:
        raise RuntimeError("No training data was downloaded.")
    return pd.concat(parts).sort_index()


def render_report(results: pd.DataFrame, coefficients: pd.Series, market_date: str) -> str:
    rows = "\n".join(f"| {name} | {value:+.4f} |" for name, value in coefficients.items())
    result_rows = "\n".join(
        f"| {row.ticker} | {row.observations:,} | {row.accuracy:.1%} | {row.accuracy_edge:+.1%} | "
        f"{row.balanced_accuracy:.1%} | {row.signal_rate:.1%} | "
        f"{row.signal_win_rate:.1%} | {row.strategy_return:.1%} | {row.benchmark_return:.1%} | "
        f"{row.maximum_drawdown:.1%} |" for row in results.itertuples(index=False)
    )
    predictive_assets = int(((results["accuracy_edge"] > 0) & (results["balanced_accuracy"] > 0.5)).sum())
    outperforming_assets = int((results["strategy_return"] > results["benchmark_return"]).sum())
    accepted = predictive_assets >= len(results) / 2 and outperforming_assets >= len(results) / 2
    verdict = "PASS FOR FURTHER PAPER TESTING" if accepted else "REJECTED AS A TRADING MODEL"
    return f"""# MarketLab Model Training — {market_date}

Chronological out-of-sample research result. This model does not place orders.

## Verdict: {verdict}

- Assets with predictive improvement over the naive baseline: **{predictive_assets} / {len(results)}**
- Assets outperforming buy and hold: **{outperforming_assets} / {len(results)}**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{result_rows}

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
        model = fit_logistic(asset[list(FEATURES)].to_numpy(), asset["label"].to_numpy())
        coefficient_parts.append(pd.Series(model.weights[:-1], index=FEATURES, name=ticker))
    results = pd.DataFrame(result_rows)[["ticker", "observations", "accuracy", "naive_accuracy",
                                         "accuracy_edge", "balanced_accuracy", "brier_score", "signal_rate",
                                         "signal_win_rate", "strategy_return", "benchmark_return",
                                         "maximum_drawdown", "threshold", "average_decision_threshold",
                                         "minimum_edge", "fee"]]
    coefficients = pd.concat(coefficient_parts, axis=1).mean(axis=1)
    market_date = pd.Timestamp(data.index.get_level_values("date").max()).date().isoformat()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.assign(market_date=market_date).to_csv(OUTPUT_DIR / "latest.csv", index=False)
    pd.concat(prediction_parts).sort_values(["date", "ticker"]).groupby("ticker").tail(100).to_csv(
        OUTPUT_DIR / "latest_predictions.csv", index=False
    )
    report = render_report(results, coefficients, market_date)
    (OUTPUT_DIR / "latest.md").write_text(report, encoding="utf-8")
    history = OUTPUT_DIR / "history"
    history.mkdir(exist_ok=True)
    (history / f"{market_date}.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
