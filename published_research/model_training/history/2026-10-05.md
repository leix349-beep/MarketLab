# MarketLab Model Training — 2026-10-05

Chronological out-of-sample research result. This model does not place orders.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|
| SPY | 1,689 | 59.7% | 98.2% | 59.9% | 133.6% | 160.5% | -31.7% |
| QQQ | 1,689 | 58.4% | 98.6% | 58.6% | 187.7% | 257.9% | -33.7% |
| IWM | 1,689 | 52.8% | 44.3% | 51.6% | -6.3% | 80.2% | -32.9% |
| XLK | 1,689 | 58.0% | 95.0% | 58.5% | 365.1% | 347.1% | -30.9% |
| XLF | 1,689 | 54.1% | 67.3% | 56.1% | 53.1% | 98.4% | -39.3% |
| XLE | 1,689 | 54.8% | 28.4% | 54.1% | -17.6% | 180.3% | -52.9% |

## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0227 |
| ret_21 | +0.0338 |
| ma_gap | -0.0492 |
| rsi14 | -0.0259 |
| vol_21 | +0.0100 |
| drawdown_63 | -0.0081 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days, separated from each test block by a five-day embargo, and requires a probability of at least 55% for exposure. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
