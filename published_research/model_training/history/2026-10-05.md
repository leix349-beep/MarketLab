# MarketLab Model Training — 2026-10-05

Chronological out-of-sample research result. This model does not place orders.

## Verdict: REJECTED AS A TRADING MODEL

- Assets with predictive improvement over the naive baseline: **0 / 6**
- Assets outperforming buy and hold: **0 / 6**
- Assets improving risk-adjusted return (Sharpe): **0 / 6**
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

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| IWM | -2.3% | 9.2% | 15.5% | 24.8% | -0.07 | 0.48 | -0.08 | 0.23 |
| QQQ | 0.2% | 20.9% | 10.9% | 22.8% | 0.07 | 0.95 | 0.02 | 0.62 |
| SPY | -2.9% | 15.3% | 7.6% | 18.5% | -0.34 | 0.87 | -0.12 | 0.48 |
| XLE | -5.6% | 16.6% | 20.5% | 31.6% | -0.17 | 0.65 | -0.10 | 0.30 |
| XLF | -1.7% | 10.8% | 13.9% | 22.7% | -0.06 | 0.57 | -0.06 | 0.27 |
| XLK | -2.9% | 25.0% | 9.1% | 25.2% | -0.27 | 1.01 | -0.14 | 0.77 |

## Downside-Risk Filter Candidate: REJECTED AS A TRADING MODEL

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **3 / 6**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IWM | 19.8% | 0.441 | 2.6% | 6.1% | 7.0% | 0.44 | 0.66 | -28.7% | -30.4% |
| QQQ | 19.9% | 0.549 | 17.5% | 16.4% | 9.3% | 0.61 | 0.94 | -43.1% | -35.1% |
| SPY | 13.3% | 0.580 | 11.7% | 8.3% | 11.4% | 0.86 | 1.07 | -23.2% | -23.2% |
| XLE | 23.6% | 0.462 | 8.7% | 9.5% | 20.1% | 0.88 | 1.05 | -22.0% | -22.5% |
| XLF | 15.6% | 0.507 | 3.7% | 3.7% | 14.0% | 0.82 | 0.91 | -23.7% | -24.9% |
| XLK | 21.3% | 0.497 | 12.4% | 13.9% | 9.8% | 0.56 | 1.02 | -41.4% | -31.9% |

## Cross-Asset Risk Candidate: REJECTED AS A TRADING MODEL

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **3 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **2 / 6**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IWM | 0.450 | 28.2% | 24.4% | 0.27 | 0.0% | 8.0% | 0.52 | 0.66 | -31.3% | -30.4% |
| QQQ | 0.536 | 28.8% | 28.9% | 0.25 | 0.0% | 7.0% | 0.49 | 0.94 | -29.8% | -35.1% |
| SPY | 0.590 | 39.8% | 31.6% | 0.25 | 0.0% | 9.5% | 0.86 | 1.07 | -23.2% | -23.2% |
| XLE | 0.461 | 26.7% | 26.4% | 0.40 | 8.1% | 13.1% | 0.66 | 1.05 | -23.3% | -22.5% |
| XLF | 0.552 | 34.3% | 33.0% | 0.29 | 4.1% | 1.6% | 0.18 | 0.91 | -29.7% | -24.9% |
| XLK | 0.488 | 23.9% | 25.6% | 0.26 | 0.0% | 9.2% | 0.54 | 1.02 | -29.3% | -31.9% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML risk allocation | 9.8% | 9.0% | 1.09 | -13.7% | 0.72 |
| Volatility target only | 12.7% | 11.1% | 1.13 | -14.9% | 0.85 |
| Buy and hold | 16.7% | 15.5% | 1.07 | -23.2% | 0.72 |

- Average ML exposure: **64.5%**
- Average volatility-target exposure: **81.8%**


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
