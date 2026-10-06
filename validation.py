from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd

from strategy import backtest


def _performance(returns: pd.Series) -> dict[str, float]:
    returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
    if returns.empty:
        return {"return": 0.0, "annual_return": 0.0, "drawdown": 0.0, "sharpe": 0.0}
    wealth = (1 + returns).cumprod()
    years = max(len(returns) / 252, 1 / 252)
    volatility = float(returns.std())
    return {
        "return": float(wealth.iloc[-1] - 1),
        "annual_return": float(wealth.iloc[-1] ** (1 / years) - 1),
        "drawdown": float((wealth / wealth.cummax() - 1).min()),
        "sharpe": float(np.sqrt(252) * returns.mean() / volatility) if volatility else 0.0,
    }


def walk_forward_validate(
    df: pd.DataFrame,
    train_days: int = 504,
    test_days: int = 126,
    fasts: tuple[int, ...] = (10, 20, 30),
    slows: tuple[int, ...] = (40, 60, 100),
    fee: float = 0.001,
) -> dict:
    """Select parameters on past data, then evaluate them on the next unseen block."""
    data = df.sort_index().dropna(subset=["Open", "High", "Low", "Close"]).copy()
    if len(data) < train_days + test_days:
        raise ValueError("Not enough history for one training and test window.")

    fold_rows: list[dict] = []
    strategy_parts: list[pd.Series] = []
    benchmark_parts: list[pd.Series] = []

    fold_number = 1
    train_start, train_end = 0, train_days
    while train_end + test_days <= len(data):
        test_end = train_end + test_days
        train = data.iloc[train_start:train_end]

        candidates = []
        for fast in fasts:
            for slow in slows:
                if fast >= slow:
                    continue
                _, _, metrics = backtest(train, fast=fast, slow=slow, fee=fee)
                # Extremely sparse strategies often win by chance. Prefer candidates
                # with at least four completed actions when enough choices exist.
                candidates.append((fast, slow, metrics["夏普比率"], metrics["交易次数"]))
        eligible = [x for x in candidates if x[3] >= 4] or candidates
        fast, slow, train_sharpe, train_actions = max(eligible, key=lambda x: x[2])

        warmup = max(slow, 14) + 5
        context = data.iloc[max(0, train_end - warmup):test_end]
        curve, trades, _ = backtest(context, fast=fast, slow=slow, fee=fee)
        test_start_date = data.index[train_end]
        test_curve = curve.loc[curve.index >= test_start_date]
        strategy_returns = test_curve.pct_change().dropna()

        test_close = data.loc[test_start_date:data.index[test_end - 1], "Close"]
        benchmark_returns = test_close.pct_change().dropna()
        common = strategy_returns.index.intersection(benchmark_returns.index)
        strategy_returns = strategy_returns.loc[common]
        benchmark_returns = benchmark_returns.loc[common]
        if strategy_returns.empty:
            train_end = test_end
            fold_number += 1
            continue

        strategy_stats = _performance(strategy_returns)
        benchmark_stats = _performance(benchmark_returns)
        test_trades = trades.loc[trades["date"] >= test_start_date]
        fold_rows.append({
            "Fold": fold_number,
            "Train Start": train.index[0],
            "Train End": train.index[-1],
            "Test Start": common[0],
            "Test End": common[-1],
            "Fast MA": fast,
            "Slow MA": slow,
            "Train Sharpe": train_sharpe,
            "Test Return": strategy_stats["return"],
            "Buy & Hold Return": benchmark_stats["return"],
            "Test Sharpe": strategy_stats["sharpe"],
            "Test Drawdown": strategy_stats["drawdown"],
            "Trade Actions": len(test_trades),
        })
        strategy_parts.append(strategy_returns)
        benchmark_parts.append(benchmark_returns)
        train_end = test_end
        fold_number += 1

    if not fold_rows:
        raise ValueError("No complete out-of-sample folds could be evaluated.")

    folds = pd.DataFrame(fold_rows)
    strategy_returns = pd.concat(strategy_parts).sort_index()
    benchmark_returns = pd.concat(benchmark_parts).sort_index()
    curve = pd.DataFrame({
        "Strategy": (1 + strategy_returns).cumprod() * 100,
        "Buy & Hold": (1 + benchmark_returns).cumprod() * 100,
    }).dropna()
    selected = list(zip(folds["Fast MA"], folds["Slow MA"]))
    most_common_count = Counter(selected).most_common(1)[0][1]
    strategy_stats = _performance(strategy_returns)
    benchmark_stats = _performance(benchmark_returns)
    summary = {
        **strategy_stats,
        "benchmark_return": benchmark_stats["return"],
        "positive_folds": int((folds["Test Return"] > 0).sum()),
        "winning_folds": int((folds["Test Return"] > folds["Buy & Hold Return"]).sum()),
        "folds": len(folds),
        "parameter_stability": most_common_count / len(selected),
    }
    return {"summary": summary, "folds": folds, "curve": curve}
