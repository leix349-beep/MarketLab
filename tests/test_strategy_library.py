import unittest

import numpy as np
import pandas as pd

from strategy_library import compare_strategies, simulate_weights, volatility_target_weights


class VolatilityTargetStrategyTests(unittest.TestCase):
    def sample(self, n=500):
        rng=np.random.default_rng(11)
        index=pd.bdate_range("2022-01-03",periods=n)
        returns=np.r_[rng.normal(.0005,.008,n//2),rng.normal(.0005,.03,n-n//2)]
        close=100*np.exp(np.cumsum(returns))
        return pd.DataFrame({"Open":close*(1+rng.normal(0,.001,n)),"High":close*1.01,
                             "Low":close*.99,"Close":close,"Volume":1_000_000},index=index)

    def test_weights_fall_when_volatility_rises(self):
        frame=self.sample()
        weights=volatility_target_weights(frame,fast=5,slow=20,target_vol=.12)
        self.assertTrue(((weights>=0)&(weights<=1)).all())
        self.assertLess(weights.iloc[-100:].mean(),weights.iloc[100:200].mean())

    def test_weighted_simulation_and_comparison_are_finite(self):
        frame=self.sample()
        weights=volatility_target_weights(frame,fast=5,slow=20,target_vol=.12)
        curve,metrics=simulate_weights(frame,weights)
        self.assertTrue(np.isfinite(curve).all())
        self.assertTrue(all(np.isfinite(v) for v in metrics.values()))
        results,_=compare_strategies(frame,fast=5,slow=20,target_vol=.12)
        self.assertIn("Vol-Target Trend",results.Strategy.tolist())
        self.assertIn("Calmar Ratio",results.columns)


if __name__ == "__main__":
    unittest.main()
