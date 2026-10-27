"""Pre-registered conditional defensive-sleeve test for baseline V2."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from baseline_v2 import (ARCHIVE_VERSION, ASSETS, TREND_WINDOW,
                         simulate_target_weights)
from baseline_v2_attribution import load_frozen_candidate, performance_metrics
from baseline_v2_defensive import (DEFENSIVE_ASSETS, DEFENSIVE_WEIGHT,
                                   HOLDOUT_START, TACTICAL_WEIGHT)
from raw_price_archive import load_price_archive
from research_costs import ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO


OUTPUT_DIR = Path("published_research/baseline_v2/regime_defensive_sleeve")


def build_executable_defensive_regime(version_id: str, index: pd.Index) -> pd.Series:
    """Use close-t SPY versus its 200-day mean; act only at open t+1."""
    prices = load_price_archive(version_id)
    spy = prices[prices["ticker"] == "SPY"].set_index("date")["Close"].sort_index().astype(float)
    close_signal = spy < spy.rolling(TREND_WINDOW).mean()
    return close_signal.shift(1).reindex(index).fillna(False).astype(bool)


def add_regime_defensive_sleeve(candidate: pd.DataFrame, defensive_regime: pd.Series) -> pd.DataFrame:
    """Add the frozen 20% defensive sleeve only while the executable regime is defensive."""
    regime = defensive_regime.reindex(candidate.index).fillna(False).astype(bool)
    result = candidate.loc[:, list(ASSETS)].astype(float).copy()
    result.loc[regime] *= TACTICAL_WEIGHT
    for ticker in DEFENSIVE_ASSETS:
        result.loc[regime, ticker] += DEFENSIVE_WEIGHT / len(DEFENSIVE_ASSETS)
    return result


def _period_metrics(decomposition: pd.DataFrame, start: pd.Timestamp | None = None,
                    end: pd.Timestamp | None = None) -> dict[str, float]:
    return performance_metrics(decomposition.loc[start:end])


def evaluate_hypothesis(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, dict[str, object]]:
    candidate, open_returns = load_frozen_candidate(version_id)
    regime = build_executable_defensive_regime(version_id, candidate.index)
    conditional = add_regime_defensive_sleeve(candidate, regime)
    rows: list[dict[str, object]] = []

    for scenario in (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO):
        for name, weights in (("frozen_baseline", candidate), ("regime_defensive_sleeve", conditional)):
            decomposition = simulate_target_weights(weights, open_returns, scenario)
            for period, start, end in (
                ("full_history", None, None),
                ("development_2017_2022", None, HOLDOUT_START - pd.Timedelta(days=1)),
                ("retrospective_holdout_2023_plus", HOLDOUT_START, None),
            ):
                rows.append({
                    "strategy": name,
                    "cost_scenario": scenario.name,
                    "period": period,
                    **_period_metrics(decomposition, start, end),
                })

    metrics = pd.DataFrame(rows)
    lookup = metrics.set_index(["strategy", "cost_scenario", "period"])
    full = lookup.loc[("regime_defensive_sleeve", "base", "full_history")]
    old_full = lookup.loc[("frozen_baseline", "base", "full_history")]
    holdout = lookup.loc[("regime_defensive_sleeve", "base", "retrospective_holdout_2023_plus")]
    old_holdout = lookup.loc[("frozen_baseline", "base", "retrospective_holdout_2023_plus")]
    adverse = lookup.loc[("regime_defensive_sleeve", "adverse", "full_history")]
    gates = {
        "full_annual_return_at_least_8pct": bool(full["annual_return"] >= 0.08),
        "full_sharpe_at_least_1": bool(full["sharpe"] >= 1.0),
        "full_maximum_drawdown_no_worse_than_15pct": bool(full["maximum_drawdown"] >= -0.15),
        "holdout_sharpe_improves": bool(holdout["sharpe"] > old_holdout["sharpe"]),
        "adverse_annual_return_at_least_8pct": bool(adverse["annual_return"] >= 0.08),
    }
    accepted = all(gates.values())
    summary = {
        "archive_version": version_id,
        "pre_registered_change": {
            "regime": "SPY close below 200-day moving average, executed next open",
            "tactical_weight_while_defensive": TACTICAL_WEIGHT,
            "fixed_defensive_weight_while_defensive": DEFENSIVE_WEIGHT,
            "defensive_assets_equal_weighted": list(DEFENSIVE_ASSETS),
        },
        "defensive_regime_share": float(regime.mean()),
        "parameters_changed_after_results": False,
        "holdout_warning": (
            "The 2023+ segment is retrospective and not clean OOS because its history was already observed "
            "before this hypothesis was frozen."
        ),
        "base_full_sharpe_change": float(full["sharpe"] - old_full["sharpe"]),
        "base_holdout_sharpe_change": float(holdout["sharpe"] - old_holdout["sharpe"]),
        "gates": gates,
        "hypothesis_status": "ACCEPTED_FOR_NEXT_GATE" if accepted else "REJECTED",
        "promotion_status": "HOLD_NOT_PROMOTED",
    }
    return metrics, summary


def write_results(version_id: str = ARCHIVE_VERSION) -> dict[str, object]:
    metrics, summary = evaluate_hypothesis(version_id)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False)
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    view = metrics[
        (metrics["cost_scenario"] == "base")
        & metrics["period"].isin(["full_history", "retrospective_holdout_2023_plus"])
    ]
    lines = [
        "# Conditional defensive-sleeve hypothesis",
        "",
        "One change only: when close-t SPY is below its existing 200-day trend, the next-open allocation "
        "uses 80% of the frozen tactical book plus a 20% sleeve split equally across TLT, GLD and UUP. "
        "At all other times the frozen baseline is unchanged.",
        "",
        "The 2023+ segment is a retrospective holdout, not clean OOS: those years were already visible "
        "when the hypothesis was proposed.",
        "",
        f"Defensive regime active on {summary['defensive_regime_share']:.1%} of evaluated sessions.",
        "",
        "| Strategy | Period | Annual return | Sharpe | Max drawdown | Turnover |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
        *[
            f"| {row.strategy} | {row.period} | {row.annual_return:.2%} | {row.sharpe:.2f} | "
            f"{row.maximum_drawdown:.2%} | {row.annual_turnover:.2f}x |"
            for row in view.itertuples()
        ],
        "",
        "## Gates",
        "",
        *[f"- {name}: **{value}**" for name, value in summary["gates"].items()],
        "",
        f"**Hypothesis: {summary['hypothesis_status']}. Model promotion remains HOLD_NOT_PROMOTED.**",
        "This is historical, pre-tax research and not trading advice.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(write_results(), indent=2))
