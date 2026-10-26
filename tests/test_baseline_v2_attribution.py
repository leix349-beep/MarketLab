import unittest

import numpy as np
import pandas as pd

from baseline_v2 import ASSETS, simulate_target_weights
from baseline_v2_attribution import reconciliation_error
from research_costs import BASE_COST_SCENARIO


class BaselineV2AttributionTests(unittest.TestCase):
    def test_daily_components_reconcile_exactly_to_net_return(self):
        index = pd.bdate_range("2026-01-01", periods=4)
        targets = pd.DataFrame(0.0, index=index, columns=ASSETS)
        targets.loc[:, "SPY"] = 0.6
        targets.loc[:, "TLT"] = 0.2
        returns = pd.DataFrame(0.0, index=index, columns=ASSETS)
        returns.loc[:, "SPY"] = [0.01, -0.02, 0.015, 0.0]
        returns.loc[:, "TLT"] = [-0.005, 0.01, 0.0, 0.003]
        result = simulate_target_weights(targets, returns, BASE_COST_SCENARIO)
        self.assertLess(reconciliation_error(result), 1e-14)

    def test_recorded_asset_contributions_match_weight_times_return(self):
        index = pd.bdate_range("2026-02-01", periods=2)
        targets = pd.DataFrame(0.0, index=index, columns=ASSETS)
        targets.loc[:, "SPY"] = 0.5
        returns = pd.DataFrame(0.0, index=index, columns=ASSETS)
        returns.loc[:, "SPY"] = 0.02
        result = simulate_target_weights(targets, returns, BASE_COST_SCENARIO)
        expected = result["weight__SPY"] * 0.02
        self.assertTrue(np.allclose(result["contribution__SPY"], expected))


if __name__ == "__main__":
    unittest.main()
