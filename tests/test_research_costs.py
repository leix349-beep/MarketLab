import unittest

import pandas as pd

from research_costs import (ADVERSE_COST_SCENARIO, BASE_COST_SCENARIO,
                            apply_cost_scenario, scenario_table)


class ResearchCostTests(unittest.TestCase):
    def test_scenarios_disclose_separate_components_and_tax_boundary(self):
        table = scenario_table().set_index("name")
        required = {"commission_bps", "half_spread_bps", "slippage_bps",
                    "annual_fund_expense", "annual_cash_yield",
                    "one_way_trading_cost_bps", "tax_treatment"}
        self.assertTrue(required.issubset(table.columns))
        self.assertEqual(set(table.index), {"base", "adverse"})
        self.assertTrue((table["tax_treatment"] == "pre_tax_not_modeled").all())
        self.assertGreater(table.loc["adverse", "one_way_trading_cost_bps"],
                           table.loc["base", "one_way_trading_cost_bps"])

    def test_cost_decomposition_reconciles_to_net_return(self):
        index = pd.date_range("2026-01-01", periods=3)
        result = apply_cost_scenario(
            pd.Series([0.02, -0.01, 0.00], index=index),
            pd.Series([1.0, 0.5, 0.0], index=index),
            pd.Series([1.0, 0.25, 0.0], index=index),
            BASE_COST_SCENARIO,
        )
        expected = (result["gross_return"] - result["trading_cost"]
                    - result["fund_expense"] + result["cash_income"])
        pd.testing.assert_series_equal(result["net_return"], expected, check_names=False)
        self.assertGreater(result.iloc[-1]["cash_income"], 0)
        self.assertEqual(result.iloc[-1]["fund_expense"], 0)

    def test_adverse_scenario_is_no_better_for_same_invested_path(self):
        index = pd.date_range("2026-01-01", periods=8)
        gross = pd.Series(0.002, index=index)
        weight = pd.Series(1.0, index=index)
        turnover = pd.Series(0.4, index=index)
        base = apply_cost_scenario(gross, weight, turnover, BASE_COST_SCENARIO)
        adverse = apply_cost_scenario(gross, weight, turnover, ADVERSE_COST_SCENARIO)
        self.assertTrue((adverse["net_return"] < base["net_return"]).all())

    def test_invalid_weight_and_turnover_are_rejected(self):
        values = pd.Series([0.0])
        with self.assertRaises(ValueError):
            apply_cost_scenario(values, pd.Series([1.1]), values, BASE_COST_SCENARIO)
        with self.assertRaises(ValueError):
            apply_cost_scenario(values, values, pd.Series([-0.1]), BASE_COST_SCENARIO)

    def test_harmless_floating_point_weight_is_clipped(self):
        result = apply_cost_scenario(
            pd.Series([0.01]), pd.Series([1.0 + 2e-16]), pd.Series([0.0]),
            BASE_COST_SCENARIO,
        )
        self.assertEqual(result.iloc[0]["invested_weight"], 1.0)


if __name__ == "__main__":
    unittest.main()
