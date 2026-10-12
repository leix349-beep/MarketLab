import unittest

import pandas as pd

from global_context import context_assessment, market_regime


class GlobalContextTests(unittest.TestCase):
    def test_regime_uses_market_confirmation(self):
        factors=pd.DataFrame([
            {"ticker":"SPY","return_5d":.02}, {"ticker":"EEM","return_5d":.01},
            {"ticker":"HYG","return_5d":.01}, {"ticker":"TLT","return_5d":-.01},
            {"ticker":"^VIX","return_5d":-.10},
        ])
        regime=market_regime(factors)
        self.assertEqual(regime["label"],"Risk-On")
        self.assertEqual(regime["score"],100)

    def test_news_does_not_override_market_state(self):
        news=pd.DataFrame({"headline_risk":[2,1,1]})
        result=context_assessment({"label":"Risk-On","score":100},news)
        self.assertEqual(result["stance"],"Mixed / no confirmation")


if __name__ == "__main__":
    unittest.main()
