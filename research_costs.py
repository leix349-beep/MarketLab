"""Explicit, pre-tax research cost assumptions for future MarketLab candidates."""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CostScenario:
    """Auditable assumptions; basis-point fields are one-way trading costs."""

    name: str
    commission_bps: float
    half_spread_bps: float
    slippage_bps: float
    annual_fund_expense: float
    annual_cash_yield: float
    tax_treatment: str = "pre_tax_not_modeled"

    def __post_init__(self) -> None:
        values = (
            self.commission_bps,
            self.half_spread_bps,
            self.slippage_bps,
            self.annual_fund_expense,
            self.annual_cash_yield,
        )
        if any(not np.isfinite(value) or value < 0 for value in values):
            raise ValueError("Cost and yield assumptions must be finite and non-negative.")
        if self.annual_fund_expense >= 1 or self.annual_cash_yield >= 1:
            raise ValueError("Annual rates must be decimals below 1.0.")
        if self.tax_treatment != "pre_tax_not_modeled":
            raise ValueError("MarketLab currently reports pre-tax research results only.")

    @property
    def one_way_trading_cost(self) -> float:
        return (self.commission_bps + self.half_spread_bps + self.slippage_bps) / 10_000


# These are fixed research stress assumptions, not claims about a particular
# broker, fund, account, or today's interest rate.
BASE_COST_SCENARIO = CostScenario(
    name="base",
    commission_bps=0.0,
    half_spread_bps=1.0,
    slippage_bps=2.0,
    annual_fund_expense=0.0015,
    annual_cash_yield=0.03,
)

ADVERSE_COST_SCENARIO = CostScenario(
    name="adverse",
    commission_bps=1.0,
    half_spread_bps=5.0,
    slippage_bps=10.0,
    annual_fund_expense=0.0060,
    annual_cash_yield=0.0,
)

COST_SCENARIOS = (BASE_COST_SCENARIO, ADVERSE_COST_SCENARIO)


def scenario_table() -> pd.DataFrame:
    """Return every assumption in a publishable table."""
    rows = []
    for scenario in COST_SCENARIOS:
        row = asdict(scenario)
        row["one_way_trading_cost_bps"] = scenario.one_way_trading_cost * 10_000
        rows.append(row)
    return pd.DataFrame(rows)


def apply_cost_scenario(gross_return: pd.Series,
                        invested_weight: pd.Series,
                        turnover: pd.Series,
                        scenario: CostScenario,
                        periods_per_year: float = 252 / 5) -> pd.DataFrame:
    """Decompose net portfolio returns under one declared cost scenario.

    ``gross_return`` is the already weighted ETF return. ``invested_weight``
    is total long ETF exposure from 0 to 1; the remainder earns the declared
    cash yield. ``turnover`` is one-way traded notional divided by equity and
    may exceed 1 when the portfolio rotates across assets.
    """
    if periods_per_year <= 0 or not np.isfinite(periods_per_year):
        raise ValueError("periods_per_year must be finite and positive.")
    aligned = pd.concat(
        [gross_return.rename("gross_return"),
         invested_weight.rename("invested_weight"),
         turnover.rename("turnover")],
        axis=1,
    ).dropna()
    tolerance = 1e-12
    if ((aligned["invested_weight"] < -tolerance) |
            (aligned["invested_weight"] > 1 + tolerance)).any():
        raise ValueError("invested_weight must stay between 0 and 1.")
    if (aligned["turnover"] < 0).any():
        raise ValueError("turnover cannot be negative.")

    aligned["invested_weight"] = aligned["invested_weight"].clip(0, 1)
    fund_expense_rate = 1 - (1 - scenario.annual_fund_expense) ** (1 / periods_per_year)
    cash_return_rate = (1 + scenario.annual_cash_yield) ** (1 / periods_per_year) - 1
    result = aligned.copy()
    result["trading_cost"] = result["turnover"] * scenario.one_way_trading_cost
    result["fund_expense"] = result["invested_weight"] * fund_expense_rate
    result["cash_income"] = (1 - result["invested_weight"]) * cash_return_rate
    result["net_return"] = (
        result["gross_return"]
        - result["trading_cost"]
        - result["fund_expense"]
        + result["cash_income"]
    )
    return result
