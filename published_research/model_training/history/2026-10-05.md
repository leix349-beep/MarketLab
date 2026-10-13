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
| XLE | 23.6% | 0.462 | 9.0% | 9.6% | 20.3% | 0.88 | 1.05 | -22.0% | -22.5% |
| XLF | 15.5% | 0.504 | 3.3% | 3.4% | 14.0% | 0.82 | 0.91 | -23.7% | -24.9% |
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
| XLE | 0.463 | 26.4% | 26.1% | 0.41 | 8.1% | 13.1% | 0.66 | 1.05 | -23.3% | -22.5% |
| XLF | 0.548 | 35.7% | 39.0% | 0.27 | 4.1% | -1.1% | -0.01 | 0.91 | -29.7% | -24.9% |
| XLK | 0.488 | 23.9% | 25.6% | 0.26 | 0.0% | 9.2% | 0.54 | 1.02 | -29.3% | -31.9% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | 9.0% | 8.6% | 1.04 | -11.7% | 0.77 |
| ML binary allocation | 9.8% | 9.0% | 1.09 | -13.7% | 0.72 |
| Volatility target only | 12.7% | 11.1% | 1.13 | -14.9% | 0.85 |
| Buy and hold | 16.7% | 15.5% | 1.07 | -23.2% | 0.72 |

- Average smooth ML exposure: **63.5%**
- Average binary ML exposure: **64.5%**
- Average volatility-target exposure: **81.8%**


## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **2 / 6** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **2 / 6** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Market trend | Positive | 238 | 7.6% | 0.89 | 11.2% | 1.06 | 12.0% | 0.94 |
| Market trend | Negative | 73 | 13.8% | 1.51 | 17.6% | 1.34 | 33.5% | 1.42 |
| VIX state | Below 25 | 263 | 8.7% | 1.03 | 10.9% | 1.03 | 11.9% | 0.94 |
| VIX state | 25 or above | 48 | 10.4% | 1.11 | 22.7% | 1.58 | 46.7% | 1.64 |
| Realized volatility | At/below prior median | 166 | 10.9% | 1.26 | 14.3% | 1.35 | 15.2% | 1.37 |
| Realized volatility | Above prior median | 119 | 6.4% | 0.70 | 7.6% | 0.69 | 13.9% | 0.75 |

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.


## Volatility-Target Robustness: NOT YET ROBUST

- Higher Sharpe across assets: **2 / 6**
- Smaller drawdown across assets: **6 / 6**
- Higher Sharpe across calendar years: **2 / 10**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Asset | IWM | 489 | 3.3% | 0.30 | -22.8% | 9.2% | 0.49 | -38.6% |
| Asset | QQQ | 489 | 13.3% | 1.03 | -17.2% | 21.5% | 1.00 | -34.6% |
| Asset | SPY | 489 | 10.8% | 0.90 | -16.1% | 15.4% | 0.90 | -28.7% |
| Asset | XLE | 489 | 1.9% | 0.20 | -42.6% | 10.1% | 0.47 | -64.6% |
| Asset | XLF | 489 | 5.2% | 0.43 | -23.3% | 11.0% | 0.58 | -37.0% |
| Asset | XLK | 489 | 14.0% | 1.07 | -14.1% | 25.4% | 1.08 | -31.6% |
| Calendar year | 2017 | 49 | 20.1% | 3.05 | -2.9% | 21.9% | 3.01 | -2.9% |
| Calendar year | 2018 | 50 | -9.2% | -0.52 | -15.9% | -9.2% | -0.30 | -23.3% |
| Calendar year | 2019 | 51 | 15.2% | 1.36 | -7.4% | 30.5% | 2.04 | -7.7% |
| Calendar year | 2020 | 50 | 0.2% | 0.09 | -16.2% | 12.7% | 0.51 | -35.2% |
| Calendar year | 2021 | 51 | 18.4% | 1.69 | -4.1% | 34.7% | 1.93 | -5.5% |
| Calendar year | 2022 | 50 | -9.0% | -0.78 | -10.5% | -12.3% | -0.40 | -19.2% |
| Calendar year | 2023 | 50 | 14.1% | 1.23 | -7.1% | 25.8% | 1.52 | -8.6% |
| Calendar year | 2024 | 50 | 17.0% | 1.70 | -3.6% | 23.1% | 1.62 | -5.3% |
| Calendar year | 2025 | 50 | 6.6% | 0.59 | -12.7% | 17.7% | 0.88 | -20.2% |
| Calendar year | 2026 | 38 | 16.4% | 2.46 | -2.4% | 31.2% | 2.80 | -3.4% |

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.


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
