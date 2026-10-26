"""Auditable attribution for the frozen MarketLab baseline V2."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from baseline_v2 import (ARCHIVE_VERSION, ASSETS, build_signal_weights,
                         execution_weights, simulate_target_weights)
from raw_price_archive import load_price_archive
from research_costs import ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO


OUTPUT_DIR = Path("published_research/baseline_v2/attribution")


def load_frozen_candidate(version_id: str = ARCHIVE_VERSION) -> tuple[pd.DataFrame, pd.DataFrame]:
    prices = load_price_archive(version_id)
    prices = prices[prices["ticker"].isin(ASSETS)]
    closes = prices.pivot(index="date", columns="ticker", values="Close").dropna()
    opens = prices.pivot(index="date", columns="ticker", values="Open").reindex(closes.index).dropna()
    closes = closes.reindex(opens.index)
    open_returns = opens.shift(-1).div(opens).sub(1)
    candidate = execution_weights(build_signal_weights(closes))
    first_invested = (candidate.sum(axis=1) > 0)
    start = first_invested[first_invested].index[0]
    return candidate.loc[start:], open_returns.loc[start:]


def performance_metrics(decomposition: pd.DataFrame) -> dict[str, float]:
    returns = decomposition["net_return"].dropna()
    years = len(returns) / 252
    wealth = (1 + returns).cumprod()
    annual_return = float(wealth.iloc[-1] ** (1 / years) - 1)
    volatility = float(returns.std() * np.sqrt(252))
    return {
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": float(returns.mean() / returns.std() * np.sqrt(252)),
        "maximum_drawdown": float((wealth / wealth.cummax() - 1).min()),
        "average_invested_weight": float(decomposition["invested_weight"].mean()),
        "annual_turnover": float(decomposition["turnover"].sum() / years),
    }


def component_attribution(decomposition: pd.DataFrame, scenario: str) -> pd.DataFrame:
    components: dict[str, pd.Series] = {
        ticker: decomposition[f"contribution__{ticker}"] for ticker in ASSETS
    }
    components.update({
        "cash_income": decomposition["cash_income"],
        "fund_expense": -decomposition["fund_expense"],
        "trading_cost": decomposition["trading_cost_effect"],
    })
    rows = []
    for name, values in components.items():
        rows.append({
            "cost_scenario": scenario,
            "component": name,
            "annualized_arithmetic_contribution": float(values.mean() * 252),
            "total_arithmetic_contribution": float(values.sum()),
        })
    return pd.DataFrame(rows)


def exposure_attribution(decomposition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker in ASSETS:
        weights = decomposition[f"weight__{ticker}"]
        selected = weights > 1e-12
        rows.append({
            "asset": ticker,
            "average_weight": float(weights.mean()),
            "share_of_days_selected": float(selected.mean()),
            "average_weight_when_selected": float(weights[selected].mean()) if selected.any() else 0.0,
        })
    rows.append({
        "asset": "CASH",
        "average_weight": float((1 - decomposition["invested_weight"]).mean()),
        "share_of_days_selected": float((decomposition["invested_weight"] < 1 - 1e-12).mean()),
        "average_weight_when_selected": float(
            (1 - decomposition.loc[decomposition["invested_weight"] < 1 - 1e-12, "invested_weight"]).mean()
        ),
    })
    return pd.DataFrame(rows)


def yearly_attribution(decomposition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, frame in decomposition.groupby(decomposition.index.year):
        returns = frame["net_return"]
        wealth = (1 + returns).cumprod()
        rows.append({
            "year": int(year),
            "return": float(wealth.iloc[-1] - 1),
            "volatility": float(returns.std() * np.sqrt(252)),
            "sharpe": float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() else 0.0,
            "maximum_drawdown": float((wealth / wealth.cummax() - 1).min()),
            "average_invested_weight": float(frame["invested_weight"].mean()),
            "turnover": float(frame["turnover"].sum()),
        })
    return pd.DataFrame(rows)


def reconciliation_error(decomposition: pd.DataFrame) -> float:
    asset_columns = [f"contribution__{ticker}" for ticker in ASSETS]
    reconstructed = (
        decomposition[asset_columns].sum(axis=1)
        + decomposition["cash_income"]
        - decomposition["fund_expense"]
        + decomposition["trading_cost_effect"]
    )
    return float((reconstructed - decomposition["net_return"]).abs().max())


def write_attribution(version_id: str = ARCHIVE_VERSION) -> dict[str, object]:
    weights, open_returns = load_frozen_candidate(version_id)
    decompositions = {
        scenario.name: simulate_target_weights(weights, open_returns, scenario)
        for scenario in (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO)
    }
    metrics = pd.DataFrame([
        {"cost_scenario": name, **performance_metrics(frame)}
        for name, frame in decompositions.items()
    ])
    components = pd.concat([
        component_attribution(frame, name) for name, frame in decompositions.items()
    ], ignore_index=True)
    exposures = exposure_attribution(decompositions["base"])
    yearly = yearly_attribution(decompositions["base"])
    errors = {name: reconciliation_error(frame) for name, frame in decompositions.items()}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT_DIR / "scenario_metrics.csv", index=False)
    components.to_csv(OUTPUT_DIR / "return_components.csv", index=False)
    exposures.to_csv(OUTPUT_DIR / "exposures.csv", index=False)
    yearly.to_csv(OUTPUT_DIR / "yearly.csv", index=False)

    base = metrics.set_index("cost_scenario").loc["base"]
    adverse = metrics.set_index("cost_scenario").loc["adverse"]
    cost_penalty = float(base["annual_return"] - adverse["annual_return"])
    cash_weight = float(exposures.set_index("asset").loc["CASH", "average_weight"])
    weakest_year = yearly.loc[yearly["sharpe"].idxmin()]
    verdict = {
        "archive_version": version_id,
        "parameters_changed": False,
        "maximum_daily_reconciliation_error": errors,
        "base_to_adverse_annual_return_penalty": cost_penalty,
        "average_cash_weight": cash_weight,
        "weakest_calendar_year": int(weakest_year["year"]),
        "weakest_calendar_year_sharpe": float(weakest_year["sharpe"]),
        "diagnosis": (
            "Return consistency and selection quality are the first problem to test; "
            "costs materially worsen the result but do not explain the base-case Sharpe failure."
        ),
        "next_single_hypothesis": (
            "Test whether a fixed broad defensive sleeve improves weak-regime consistency "
            "without increasing turnover or changing the frozen signal parameters."
        ),
        "promotion_status": "HOLD_NOT_PROMOTED",
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    top = components[components["cost_scenario"] == "base"].sort_values(
        "annualized_arithmetic_contribution", ascending=False
    )
    lines = [
        "# Baseline V2 return and risk attribution",
        "",
        f"Frozen archive: `{version_id}`. No signal parameter was changed and no model was trained.",
        "",
        "## Finding",
        "",
        "The first issue is return consistency and asset-selection quality, not simply fees. "
        f"Base-to-adverse assumptions reduce annual return by {cost_penalty:.2%}, but the base case already misses the Sharpe gate. "
        f"The portfolio held {cash_weight:.1%} cash on average; its weakest calendar-year Sharpe was "
        f"{weakest_year['sharpe']:.2f} in {int(weakest_year['year'])}.",
        "",
        "## Base-case arithmetic contribution",
        "",
        "| Component | Annualized contribution |",
        "| --- | ---: |",
        *[f"| {row.component} | {row.annualized_arithmetic_contribution:.2%} |" for row in top.itertuples()],
        "",
        "## Integrity check",
        "",
        f"Maximum daily reconciliation error: {max(errors.values()):.3e}.",
        "",
        "## Next controlled hypothesis",
        "",
        "Test one fixed broad defensive sleeve while keeping the signal, execution timing and cost model unchanged. "
        "This attribution does not promote the model and is not trading advice.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verdict


if __name__ == "__main__":
    print(json.dumps(write_attribution(), indent=2))
