"""Single pre-registered defensive-sleeve test for baseline V2."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from baseline_v2 import ASSETS, ARCHIVE_VERSION, simulate_target_weights
from baseline_v2_attribution import load_frozen_candidate, performance_metrics
from research_costs import ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO


OUTPUT_DIR = Path("published_research/baseline_v2/defensive_sleeve")
TACTICAL_WEIGHT = 0.80
DEFENSIVE_WEIGHT = 0.20
DEFENSIVE_ASSETS = ("TLT", "GLD", "UUP")
HOLDOUT_START = pd.Timestamp("2023-01-03")


def add_fixed_defensive_sleeve(candidate: pd.DataFrame) -> pd.DataFrame:
    """Scale the frozen tactical weights and add one fixed broad defensive sleeve."""
    result = candidate.loc[:, list(ASSETS)].astype(float) * TACTICAL_WEIGHT
    for ticker in DEFENSIVE_ASSETS:
        result[ticker] += DEFENSIVE_WEIGHT / len(DEFENSIVE_ASSETS)
    return result


def _period_metrics(decomposition: pd.DataFrame, start: pd.Timestamp | None = None,
                    end: pd.Timestamp | None = None) -> dict[str, float]:
    frame = decomposition.loc[start:end]
    return performance_metrics(frame)


def evaluate_hypothesis(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, dict[str, object]]:
    candidate, open_returns = load_frozen_candidate(version_id)
    defensive = add_fixed_defensive_sleeve(candidate)
    rows: list[dict[str, object]] = []

    for scenario in (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO):
        for name, weights in (("frozen_baseline", candidate), ("fixed_defensive_sleeve", defensive)):
            decomposition = simulate_target_weights(weights, open_returns, scenario)
            periods = {
                "full_history": (None, None),
                "development_2017_2022": (None, HOLDOUT_START - pd.Timedelta(days=1)),
                "retrospective_holdout_2023_plus": (HOLDOUT_START, None),
            }
            for period, (start, end) in periods.items():
                rows.append({
                    "strategy": name,
                    "cost_scenario": scenario.name,
                    "period": period,
                    **_period_metrics(decomposition, start, end),
                })

    metrics = pd.DataFrame(rows)
    lookup = metrics.set_index(["strategy", "cost_scenario", "period"])
    full = lookup.loc[("fixed_defensive_sleeve", "base", "full_history")]
    old_full = lookup.loc[("frozen_baseline", "base", "full_history")]
    holdout = lookup.loc[("fixed_defensive_sleeve", "base", "retrospective_holdout_2023_plus")]
    old_holdout = lookup.loc[("frozen_baseline", "base", "retrospective_holdout_2023_plus")]
    adverse = lookup.loc[("fixed_defensive_sleeve", "adverse", "full_history")]

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
            "tactical_weight": TACTICAL_WEIGHT,
            "fixed_defensive_weight": DEFENSIVE_WEIGHT,
            "defensive_assets_equal_weighted": list(DEFENSIVE_ASSETS),
        },
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
        & (metrics["period"].isin(["full_history", "retrospective_holdout_2023_plus"]))
    ].copy()
    lines = [
        "# Frozen defensive-sleeve hypothesis",
        "",
        "One change only: 80% of the frozen tactical strategy plus a permanent 20% sleeve split equally "
        "across TLT, GLD and UUP. No alternative sleeve weight was tested.",
        "",
        "The 2023+ segment is a retrospective holdout, not clean OOS: those years were already visible "
        "when the hypothesis was proposed.",
        "",
        "| Strategy | Period | Annual return | Sharpe | Max drawdown |",
        "| --- | --- | ---: | ---: | ---: |",
        *[
            f"| {row.strategy} | {row.period} | {row.annual_return:.2%} | {row.sharpe:.2f} | "
            f"{row.maximum_drawdown:.2%} |"
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
