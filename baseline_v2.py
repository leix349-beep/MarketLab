"""Frozen first-pass multi-asset baseline using versioned MarketLab data."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd

from raw_price_archive import ARCHIVE_ROOT, load_price_archive
from research_costs import (ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO,
                            CostScenario, scenario_table)


ARCHIVE_VERSION = "prices-a75b446717b99a55"
OUTPUT_DIR = Path("published_research/baseline_v2")
ASSETS = ("SPY", "EFA", "EWJ", "EEM", "TLT", "HYG", "GLD", "UUP")
EQUITY_MARKETS = ("SPY", "EFA", "EWJ", "EEM")
REBALANCE_SESSIONS = 21
TREND_WINDOW = 200
MOMENTUM_WINDOWS = (126, 252)
VOLATILITY_WINDOW = 63
TARGET_VOLATILITY = 0.10
MAX_ASSETS = 3
MAX_ASSET_WEIGHT = 0.50


def _capped_weights(score: pd.Series, cap: float = MAX_ASSET_WEIGHT) -> pd.Series:
    """Normalize positive scores while enforcing a fixed concentration cap."""
    score = score.clip(lower=0).dropna()
    if score.empty or score.sum() <= 0:
        return pd.Series(dtype=float)
    original = score / score.sum()
    weights = pd.Series(0.0, index=original.index)
    free = pd.Series(True, index=original.index)
    for _ in range(len(original) + 1):
        remaining = 1 - weights[~free].sum()
        if remaining <= 0 or not free.any():
            break
        proposal = original[free] / original[free].sum() * remaining
        over = proposal > cap
        if not over.any():
            weights.loc[free] = proposal
            break
        capped_names = proposal[over].index
        weights.loc[capped_names] = cap
        free.loc[capped_names] = False
    return weights


def build_signal_weights(closes: pd.DataFrame) -> pd.DataFrame:
    """Create fixed monthly close-t weights without using future observations."""
    closes = closes.loc[:, list(ASSETS)].sort_index().astype(float)
    returns = closes.pct_change(fill_method=None)
    ma200 = closes.rolling(TREND_WINDOW).mean()
    momentum = sum(closes.pct_change(window) for window in MOMENTUM_WINDOWS) / len(MOMENTUM_WINDOWS)
    volatility = returns.rolling(VOLATILITY_WINDOW).std() * np.sqrt(252)
    signals = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)

    for location in range(max(MOMENTUM_WINDOWS), len(closes), REBALANCE_SESSIONS):
        date = closes.index[location]
        eligible = (closes.loc[date] > ma200.loc[date]) & (momentum.loc[date] > 0)
        selected = momentum.loc[date, eligible].nlargest(MAX_ASSETS).index
        row = pd.Series(0.0, index=closes.columns)
        if len(selected):
            inverse_volatility = 1 / volatility.loc[date, selected].replace(0, np.nan)
            weights = _capped_weights(inverse_volatility)
            history = returns.loc[:date, selected].tail(VOLATILITY_WINDOW)
            covariance = history.cov() * 252
            estimated_volatility = float(np.sqrt(weights @ covariance @ weights))
            scale = min(1.0, TARGET_VOLATILITY / estimated_volatility) if estimated_volatility > 0 else 0.0
            row.loc[weights.index] = weights * scale
        signals.loc[date] = row

    return signals.ffill().fillna(0.0)


def execution_weights(signal_weights: pd.DataFrame) -> pd.DataFrame:
    """A close-t signal becomes tradable only at the next session's open."""
    return signal_weights.shift(1).fillna(0.0)


def simulate_target_weights(target_weights: pd.DataFrame, open_returns: pd.DataFrame,
                            scenario: CostScenario) -> pd.DataFrame:
    """Run a self-financing portfolio; trade only when the target changes."""
    targets = target_weights.astype(float)
    asset_returns = open_returns.reindex_like(targets)
    current = pd.Series(0.0, index=targets.columns)
    current_cash = 1.0
    previous_target: pd.Series | None = None
    expense = 1 - (1 - scenario.annual_fund_expense) ** (1 / 252)
    cash_rate = (1 + scenario.annual_cash_yield) ** (1 / 252) - 1
    rows = []

    for date, target in targets.iterrows():
        returns = asset_returns.loc[date]
        if returns.isna().any():
            continue
        target_changed = previous_target is None or not np.allclose(
            target.to_numpy(), previous_target.to_numpy(), atol=1e-14, rtol=0
        )
        if target_changed:
            desired = target.copy()
            desired_cash = 1 - float(desired.sum())
            turnover = 0.5 * (float((desired - current).abs().sum())
                              + abs(desired_cash - current_cash))
        else:
            desired = current.copy()
            desired_cash = current_cash
            turnover = 0.0

        trading_cost = turnover * scenario.one_way_trading_cost
        gross_return = float((desired * returns).sum())
        fund_expense = float(desired.sum()) * expense
        cash_income = desired_cash * cash_rate
        pre_cost_total = 1 + gross_return - fund_expense + cash_income
        total = pre_cost_total * (1 - trading_cost)
        net_return = total - 1
        asset_values = desired * (1 + returns - expense) * (1 - trading_cost)
        cash_value = desired_cash * (1 + cash_rate) * (1 - trading_cost)
        current = asset_values / total
        current_cash = float(cash_value / total)
        previous_target = target.copy()
        row = {
            "date": date, "gross_return": gross_return, "turnover": turnover,
            "trading_cost": trading_cost, "fund_expense": fund_expense,
            "cash_income": cash_income, "net_return": net_return,
            "invested_weight": float(desired.sum()),
            "trading_cost_effect": -pre_cost_total * trading_cost,
        }
        for ticker in targets.columns:
            row[f"weight__{ticker}"] = float(desired[ticker])
            row[f"contribution__{ticker}"] = float(desired[ticker] * returns[ticker])
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


def _metrics(returns: pd.Series, turnover: pd.Series) -> dict[str, float]:
    returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
    wealth = (1 + returns).cumprod()
    years = len(returns) / 252
    annual_return = float(wealth.iloc[-1] ** (1 / years) - 1)
    volatility = float(returns.std() * np.sqrt(252))
    sharpe = float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() else 0.0
    drawdown = float((wealth / wealth.cummax() - 1).min())
    rolling = (1 + returns).rolling(756).apply(np.prod, raw=True) - 1
    rolling = rolling.dropna()
    return {
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "maximum_drawdown": drawdown,
        "annual_turnover": float(turnover.loc[returns.index].sum() / years),
        "rolling_3y_positive_rate": float((rolling > 0).mean()) if len(rolling) else float("nan"),
        "observations": int(len(returns)),
    }


def _markdown_table(frame: pd.DataFrame) -> str:
    """Render a small Markdown table without an optional tabulate dependency."""
    columns = [str(column) for column in frame.columns]
    rows = ["| " + " | ".join(columns) + " |",
            "| " + " | ".join("---" for _ in columns) + " |"]
    for values in frame.astype(str).itertuples(index=False, name=None):
        rows.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(rows)


def _static_weights(index: pd.Index, allocation: dict[str, float], columns: pd.Index) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=index, columns=columns)
    for ticker, weight in allocation.items():
        weights[ticker] = weight
    return weights


def _spy_vol_target(closes: pd.DataFrame) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=closes.index, columns=closes.columns)
    spy_volatility = closes["SPY"].pct_change(fill_method=None).rolling(VOLATILITY_WINDOW).std() * np.sqrt(252)
    weights["SPY"] = (TARGET_VOLATILITY / spy_volatility).clip(0, 1).shift(1).fillna(0.0)
    return weights


def evaluate_weights(name: str, weights: pd.DataFrame, open_returns: pd.DataFrame,
                     start_date: pd.Timestamp) -> tuple[list[dict[str, object]], pd.DataFrame]:
    weights = weights.loc[start_date:].copy()
    open_returns = open_returns.reindex(weights.index)
    rows = []
    daily = pd.DataFrame(index=weights.index)
    for scenario in (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO):
        decomposition = simulate_target_weights(weights, open_returns, scenario)
        stats = _metrics(decomposition["net_return"], decomposition["turnover"])
        rows.append({"strategy": name, "cost_scenario": scenario.name,
                     "average_invested_weight": float(decomposition["invested_weight"].mean()), **stats})
        daily[f"{name}__{scenario.name}"] = decomposition["net_return"]
    return rows, daily


def run_baseline(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prices = load_price_archive(version_id)
    prices = prices[prices["ticker"].isin(ASSETS)]
    closes = prices.pivot(index="date", columns="ticker", values="Close").dropna()
    opens = prices.pivot(index="date", columns="ticker", values="Open").reindex(closes.index).dropna()
    closes = closes.reindex(opens.index)
    open_returns = opens.shift(-1).div(opens).sub(1)

    signals = build_signal_weights(closes)
    candidate = execution_weights(signals)
    valid = candidate.sum(axis=1) > 0
    if not valid.any():
        raise RuntimeError("The frozen candidate never becomes investable.")
    start_date = valid[valid].index[0]
    benchmark_weights = {
        "trend_relative_momentum": candidate,
        "spy": _static_weights(closes.index, {"SPY": 1.0}, closes.columns),
        "equal_weight_equities": _static_weights(
            closes.index, {ticker: 1 / len(EQUITY_MARKETS) for ticker in EQUITY_MARKETS}, closes.columns
        ),
        "sixty_forty": _static_weights(closes.index, {"SPY": 0.6, "TLT": 0.4}, closes.columns),
        "spy_vol_target": _spy_vol_target(closes),
    }
    metric_rows = []
    daily_parts = []
    for name, weights in benchmark_weights.items():
        rows, daily = evaluate_weights(name, weights, open_returns, start_date)
        metric_rows.extend(rows)
        daily_parts.append(daily)
    metrics = pd.DataFrame(metric_rows)
    daily_returns = pd.concat(daily_parts, axis=1).dropna(how="all")
    return metrics, candidate.loc[start_date:], daily_returns


def write_results(version_id: str = ARCHIVE_VERSION) -> dict[str, object]:
    metrics, weights, daily_returns = run_baseline(version_id)
    raw_manifest = json.loads(
        (ARCHIVE_ROOT / version_id / "manifest.json").read_text(encoding="utf-8")
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False)
    weights.to_csv(OUTPUT_DIR / "weights.csv", index_label="execution_date")
    daily_returns.to_csv(OUTPUT_DIR / "daily_returns.csv", index_label="execution_date")
    scenario_table().to_csv(OUTPUT_DIR / "cost_scenarios.csv", index=False)

    base = metrics[metrics["cost_scenario"] == "base"].set_index("strategy")
    candidate = base.loc["trend_relative_momentum"]
    comparison = base.loc["spy_vol_target"]
    gates = {
        "annual_return_at_least_8pct": bool(candidate["annual_return"] >= 0.08),
        "sharpe_at_least_1": bool(candidate["sharpe"] >= 1.0),
        "sharpe_edge_at_least_0_15": bool(candidate["sharpe"] - comparison["sharpe"] >= 0.15),
        "maximum_drawdown_no_worse_than_15pct": bool(candidate["maximum_drawdown"] >= -0.15),
        "majority_rolling_3y_profitable": bool(candidate["rolling_3y_positive_rate"] > 0.5),
        "cross_market_gate": "NOT_TESTED_IN_BASELINE_ROUND",
    }
    manifest = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archive_version": version_id,
        "archive_sha256": raw_manifest["sha256"],
        "assets": list(ASSETS),
        "parameters": {
            "rebalance_sessions": REBALANCE_SESSIONS,
            "trend_window": TREND_WINDOW,
            "momentum_windows": list(MOMENTUM_WINDOWS),
            "volatility_window": VOLATILITY_WINDOW,
            "target_volatility": TARGET_VOLATILITY,
            "maximum_assets": MAX_ASSETS,
            "maximum_asset_weight": MAX_ASSET_WEIGHT,
        },
        "execution": "signal after close t; execute at open t+1; evaluate open-to-open",
        "selection_rule": "top three positive-trend assets ranked by equal-weighted 6/12 month momentum",
        "cost_requirement": "base and adverse scenarios; pre-tax",
        "promotion_status": "HOLD_NOT_PROMOTED",
        "gates": gates,
    }
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    report_rows = metrics.copy()
    for column in ("annual_return", "volatility", "maximum_drawdown", "rolling_3y_positive_rate"):
        report_rows[column] = report_rows[column].map(lambda value: f"{value:.2%}")
    report_rows["sharpe"] = report_rows["sharpe"].map(lambda value: f"{value:.2f}")
    report_rows["annual_turnover"] = report_rows["annual_turnover"].map(lambda value: f"{value:.2f}x")
    lines = [
        "# MarketLab Baseline V2 — Frozen First Run",
        "",
        f"Raw-data version: `{version_id}`",
        "",
        "No parameters were selected after viewing this result. Signals use close-t information and execute at open t+1.",
        "",
        _markdown_table(report_rows),
        "",
        "## Preliminary gates",
        "",
        *[f"- {name}: **{value}**" for name, value in gates.items()],
        "",
        "**Decision: HOLD_NOT_PROMOTED.** Cross-market and later robustness gates remain sealed. This is a historical, pre-tax research result and not a trading instruction.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(write_results(), indent=2))
