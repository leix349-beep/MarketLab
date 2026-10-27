"""Pre-registered two-sleeve growth/defense baseline."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from baseline_v2 import (ARCHIVE_VERSION, ASSETS, MAX_ASSET_WEIGHT,
                         MOMENTUM_WINDOWS, REBALANCE_SESSIONS,
                         TARGET_VOLATILITY, TREND_WINDOW, VOLATILITY_WINDOW,
                         _capped_weights, execution_weights,
                         simulate_target_weights)
from baseline_v2_attribution import performance_metrics
from baseline_v2_defensive import HOLDOUT_START
from raw_price_archive import load_price_archive
from research_costs import ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO


OUTPUT_DIR = Path("published_research/baseline_v3_two_sleeve")
GROWTH_ASSETS = ("SPY", "EFA", "EWJ", "EEM", "HYG")
DEFENSIVE_ASSETS = ("TLT", "GLD", "UUP")
GROWTH_BUDGET = 0.70
DEFENSIVE_BUDGET = 0.30
GROWTH_SELECTIONS = 2
DEFENSIVE_SELECTIONS = 1


def _sleeve_weights(volatility: pd.Series, selected: pd.Index,
                    budget: float) -> pd.Series:
    if len(selected) == 0:
        return pd.Series(dtype=float)
    inverse_volatility = 1 / volatility.loc[selected].replace(0, np.nan)
    relative_cap = min(1.0, MAX_ASSET_WEIGHT / budget)
    return _capped_weights(inverse_volatility, cap=relative_cap) * budget


def build_two_sleeve_signal_weights(closes: pd.DataFrame) -> pd.DataFrame:
    """Rank growth and defense independently, then volatility-scale the combined book."""
    closes = closes.loc[:, list(ASSETS)].sort_index().astype(float)
    returns = closes.pct_change(fill_method=None)
    ma200 = closes.rolling(TREND_WINDOW).mean()
    momentum = sum(closes.pct_change(window) for window in MOMENTUM_WINDOWS) / len(MOMENTUM_WINDOWS)
    volatility = returns.rolling(VOLATILITY_WINDOW).std() * np.sqrt(252)
    signals = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)

    for location in range(max(MOMENTUM_WINDOWS), len(closes), REBALANCE_SESSIONS):
        date = closes.index[location]
        eligible = (closes.loc[date] > ma200.loc[date]) & (momentum.loc[date] > 0)
        growth = momentum.loc[date, list(GROWTH_ASSETS)][eligible.loc[list(GROWTH_ASSETS)]].nlargest(
            GROWTH_SELECTIONS
        ).index
        defense = momentum.loc[date, list(DEFENSIVE_ASSETS)][eligible.loc[list(DEFENSIVE_ASSETS)]].nlargest(
            DEFENSIVE_SELECTIONS
        ).index
        row = pd.Series(0.0, index=closes.columns)
        growth_weights = _sleeve_weights(volatility.loc[date], growth, GROWTH_BUDGET)
        defense_weights = _sleeve_weights(volatility.loc[date], defense, DEFENSIVE_BUDGET)
        row.loc[growth_weights.index] = growth_weights
        row.loc[defense_weights.index] = defense_weights

        selected = row[row > 0].index
        if len(selected):
            covariance = returns.loc[:date, selected].tail(VOLATILITY_WINDOW).cov() * 252
            estimated_volatility = float(np.sqrt(row.loc[selected] @ covariance @ row.loc[selected]))
            scale = min(1.0, TARGET_VOLATILITY / estimated_volatility) if estimated_volatility > 0 else 0.0
            row *= scale
        signals.loc[date] = row

    return signals.ffill().fillna(0.0)


def load_two_sleeve_candidate(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, pd.DataFrame]:
    prices = load_price_archive(version_id)
    prices = prices[prices["ticker"].isin(ASSETS)]
    closes = prices.pivot(index="date", columns="ticker", values="Close").dropna()
    opens = prices.pivot(index="date", columns="ticker", values="Open").reindex(closes.index).dropna()
    closes = closes.reindex(opens.index)
    open_returns = opens.shift(-1).div(opens).sub(1)
    candidate = execution_weights(build_two_sleeve_signal_weights(closes))
    valid = candidate.sum(axis=1) > 0
    start = valid[valid].index[0]
    return candidate.loc[start:], open_returns.loc[start:]


def _period_metrics(decomposition: pd.DataFrame, start: pd.Timestamp | None = None,
                    end: pd.Timestamp | None = None) -> dict[str, float]:
    return performance_metrics(decomposition.loc[start:end])


def evaluate_candidate(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    weights, open_returns = load_two_sleeve_candidate(version_id)
    rows: list[dict[str, object]] = []
    base_decomposition: pd.DataFrame | None = None
    for scenario in (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO):
        decomposition = simulate_target_weights(weights, open_returns, scenario)
        if scenario.name == "base":
            base_decomposition = decomposition
        for period, start, end in (
            ("full_history", None, None),
            ("development_2017_2022", None, HOLDOUT_START - pd.Timedelta(days=1)),
            ("retrospective_holdout_2023_plus", HOLDOUT_START, None),
        ):
            rows.append({
                "strategy": "two_sleeve_growth_defense",
                "cost_scenario": scenario.name,
                "period": period,
                **_period_metrics(decomposition, start, end),
            })

    assert base_decomposition is not None
    contribution_rows = []
    for ticker in ASSETS:
        contribution_rows.append({
            "asset": ticker,
            "annualized_arithmetic_contribution": float(
                base_decomposition[f"contribution__{ticker}"].mean() * 252
            ),
            "average_weight": float(base_decomposition[f"weight__{ticker}"].mean()),
            "share_of_days_selected": float((base_decomposition[f"weight__{ticker}"] > 1e-12).mean()),
        })
    contributions = pd.DataFrame(contribution_rows)
    metrics = pd.DataFrame(rows)
    lookup = metrics.set_index(["cost_scenario", "period"])
    full = lookup.loc[("base", "full_history")]
    holdout = lookup.loc[("base", "retrospective_holdout_2023_plus")]
    adverse = lookup.loc[("adverse", "full_history")]
    positive_equity_markets = int(
        (contributions.set_index("asset").loc[["SPY", "EFA", "EWJ", "EEM"],
                                               "annualized_arithmetic_contribution"] > 0).sum()
    )
    top_asset_share = float(
        contributions["annualized_arithmetic_contribution"].clip(lower=0).max()
        / contributions["annualized_arithmetic_contribution"].clip(lower=0).sum()
    )
    gates = {
        "full_annual_return_at_least_8pct": bool(full["annual_return"] >= 0.08),
        "full_sharpe_at_least_1": bool(full["sharpe"] >= 1.0),
        "full_maximum_drawdown_no_worse_than_15pct": bool(full["maximum_drawdown"] >= -0.15),
        "adverse_annual_return_at_least_8pct": bool(adverse["annual_return"] >= 0.08),
        "holdout_annual_return_positive": bool(holdout["annual_return"] > 0),
        "at_least_three_equity_markets_contribute_positive": bool(positive_equity_markets >= 3),
        "largest_positive_asset_contribution_below_40pct": bool(top_asset_share < 0.40),
    }
    summary = {
        "archive_version": version_id,
        "pre_registered_structure": {
            "growth_assets": list(GROWTH_ASSETS),
            "defensive_assets": list(DEFENSIVE_ASSETS),
            "growth_budget": GROWTH_BUDGET,
            "defensive_budget": DEFENSIVE_BUDGET,
            "growth_selections": GROWTH_SELECTIONS,
            "defensive_selections": DEFENSIVE_SELECTIONS,
        },
        "parameters_changed_after_results": False,
        "holdout_warning": (
            "The 2023+ segment is retrospective and not clean OOS because its history was already observed."
        ),
        "positive_equity_market_count": positive_equity_markets,
        "largest_positive_asset_contribution_share": top_asset_share,
        "gates": gates,
        "candidate_status": "ACCEPTED_FOR_NEXT_GATE" if all(gates.values()) else "REJECTED",
        "promotion_status": "HOLD_NOT_PROMOTED",
    }
    return metrics, contributions, summary


def write_results(version_id: str = ARCHIVE_VERSION) -> dict[str, object]:
    metrics, contributions, summary = evaluate_candidate(version_id)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False)
    contributions.to_csv(OUTPUT_DIR / "asset_contributions.csv", index=False)
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Baseline V3 — separated growth and defensive sleeves",
        "",
        "One frozen structure only: a 70% growth sleeve selecting two assets and a 30% defensive sleeve "
        "selecting one asset. Both use the existing trend, momentum, volatility, execution and cost rules.",
        "",
        "The 2023+ segment is retrospective, not clean OOS, because those years were already observed.",
        "",
        "| Cost | Period | Annual return | Sharpe | Max drawdown | Turnover |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
        *[
            f"| {row.cost_scenario} | {row.period} | {row.annual_return:.2%} | {row.sharpe:.2f} | "
            f"{row.maximum_drawdown:.2%} | {row.annual_turnover:.2f}x |"
            for row in metrics.itertuples()
        ],
        "",
        "## Asset contribution",
        "",
        "| Asset | Annualized arithmetic contribution | Average weight |",
        "| --- | ---: | ---: |",
        *[
            f"| {row.asset} | {row.annualized_arithmetic_contribution:.2%} | {row.average_weight:.1%} |"
            for row in contributions.sort_values("annualized_arithmetic_contribution", ascending=False).itertuples()
        ],
        "",
        "## Gates",
        "",
        *[f"- {name}: **{value}**" for name, value in summary["gates"].items()],
        "",
        f"**Candidate: {summary['candidate_status']}. Model promotion remains HOLD_NOT_PROMOTED.**",
        "This is historical, pre-tax research and not trading advice.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(write_results(), indent=2))
