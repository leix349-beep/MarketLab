# MarketLab Model Training — 2026-10-05

Chronological out-of-sample research result. This model does not place orders.

## Verdict: REJECTED AS A TRADING MODEL

- Assets with predictive improvement over the naive baseline: **0 / 6**
- Assets outperforming buy and hold: **0 / 6**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IWM | 1,689 | 52.8% | -0.5% | 49.7% | 15.5% | 53.8% | -14.5% | 80.2% | -30.4% |
| QQQ | 1,689 | 58.4% | -0.5% | 49.6% | 13.8% | 51.9% | 1.5% | 257.9% | -13.7% |
| SPY | 1,689 | 59.7% | -0.5% | 49.6% | 7.6% | 53.9% | -17.7% | 160.5% | -23.0% |
| XLE | 1,689 | 54.8% | -1.3% | 51.2% | 17.2% | 54.6% | -31.8% | 180.3% | -52.9% |
| XLF | 1,689 | 54.1% | -2.1% | 48.5% | 17.5% | 51.5% | -11.1% | 98.4% | -29.0% |
| XLK | 1,689 | 58.0% | -0.4% | 49.8% | 12.7% | 53.7% | -17.8% | 347.1% | -20.5% |

## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0227 |
| ret_21 | +0.0338 |
| ma_gap | -0.0492 |
| rsi14 | -0.0259 |
| vol_21 | +0.0100 |
| drawdown_63 | -0.0081 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least 55% probability and a 3% edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
