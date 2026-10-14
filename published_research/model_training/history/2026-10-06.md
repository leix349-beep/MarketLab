# MarketLab Model Training — 2026-10-06

Chronological out-of-sample research result. This model does not place orders.

## Verdict: REJECTED AS A TRADING MODEL

- Assets with predictive improvement over the naive baseline: **0 / 6**
- Assets outperforming buy and hold: **0 / 6**
- Assets improving risk-adjusted return (Sharpe): **0 / 6**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 1,689 | 59.8% | -0.4% | 49.7% | 7.5% | 55.6% | 15.3% | 157.2% | -8.1% |
| QQQ | 1,689 | 58.4% | -0.5% | 49.7% | 13.6% | 52.6% | -16.3% | 249.7% | -24.0% |
| IWM | 1,689 | 52.5% | -0.8% | 49.5% | 15.6% | 54.0% | 2.4% | 77.8% | -26.2% |
| XLK | 1,689 | 58.0% | -0.4% | 49.8% | 12.9% | 54.1% | 0.9% | 333.3% | -17.9% |
| XLF | 1,689 | 54.2% | -2.0% | 48.8% | 17.2% | 52.1% | -27.4% | 98.5% | -40.3% |
| XLE | 1,689 | 55.0% | -1.2% | 51.4% | 16.6% | 54.6% | -6.2% | 188.2% | -55.8% |

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 2.1% | 15.1% | 8.4% | 18.3% | 0.29 | 0.86 | 0.26 | 0.45 |
| QQQ | -2.6% | 20.5% | 11.9% | 22.1% | -0.16 | 0.96 | -0.11 | 0.59 |
| IWM | 0.4% | 9.0% | 13.8% | 24.4% | 0.10 | 0.47 | 0.01 | 0.22 |
| XLK | 0.1% | 24.4% | 9.7% | 25.2% | 0.06 | 1.00 | 0.01 | 0.73 |
| XLF | -4.7% | 10.8% | 15.5% | 22.8% | -0.23 | 0.56 | -0.12 | 0.25 |
| XLE | -0.9% | 17.1% | 21.3% | 32.3% | 0.07 | 0.66 | -0.02 | 0.30 |

## Downside-Risk Filter Candidate: REJECTED AS A TRADING MODEL

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **2 / 6**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 13.3% | 0.578 | 11.2% | 8.6% | 9.8% | 0.71 | 1.05 | -24.1% | -24.3% |
| QQQ | 20.0% | 0.545 | 17.4% | 16.9% | 4.9% | 0.35 | 0.90 | -41.8% | -34.7% |
| IWM | 19.8% | 0.437 | 2.6% | 6.7% | 6.5% | 0.40 | 0.63 | -35.2% | -31.2% |
| XLK | 21.4% | 0.493 | 12.0% | 13.9% | 6.7% | 0.41 | 0.99 | -36.9% | -33.1% |
| XLF | 15.5% | 0.501 | 3.3% | 3.4% | 11.5% | 0.69 | 0.90 | -33.8% | -25.6% |
| XLE | 23.6% | 0.462 | 8.7% | 9.7% | 22.3% | 0.91 | 1.02 | -23.3% | -25.9% |

## Cross-Asset Risk Candidate: REJECTED AS A TRADING MODEL

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **3 / 6**
- Assets with higher Sharpe than buy and hold: **1 / 6**
- Assets with smaller maximum drawdown: **4 / 6**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.588 | 32.5% | 27.1% | 0.27 | 0.0% | 6.3% | 0.55 | 1.05 | -22.7% | -24.3% |
| QQQ | 0.531 | 20.6% | 20.6% | 0.27 | 0.0% | 9.4% | 0.58 | 0.90 | -31.7% | -34.7% |
| IWM | 0.447 | 23.7% | 21.5% | 0.34 | 8.1% | 13.5% | 0.76 | 0.63 | -25.3% | -31.2% |
| XLK | 0.484 | 22.3% | 22.6% | 0.28 | 0.0% | 8.0% | 0.49 | 0.99 | -40.7% | -33.1% |
| XLF | 0.545 | 40.7% | 37.6% | 0.28 | 4.1% | 1.4% | 0.17 | 0.90 | -31.5% | -25.6% |
| XLE | 0.462 | 17.2% | 17.8% | 0.41 | 8.1% | 16.0% | 0.72 | 1.02 | -25.9% | -25.9% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | 7.8% | 9.4% | 0.85 | -13.6% | 0.57 |
| ML binary allocation | 7.5% | 9.7% | 0.80 | -13.9% | 0.54 |
| Volatility target only | 12.2% | 11.4% | 1.06 | -16.0% | 0.76 |
| Buy and hold | 16.6% | 15.8% | 1.05 | -24.3% | 0.68 |

- Average smooth ML exposure: **66.8%**
- Average binary ML exposure: **67.9%**
- Average volatility-target exposure: **82.2%**


## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **2 / 6** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **1 / 6** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Market trend | Positive | 236 | 6.9% | 0.82 | 10.5% | 0.97 | 11.6% | 0.91 |
| Market trend | Negative | 75 | 10.5% | 0.93 | 17.9% | 1.33 | 33.8% | 1.41 |
| VIX state | Below 25 | 262 | 7.0% | 0.77 | 11.6% | 1.06 | 13.3% | 0.96 |
| VIX state | 25 or above | 49 | 12.2% | 1.27 | 15.6% | 1.12 | 35.5% | 1.43 |
| Realized volatility | At/below prior median | 170 | 10.2% | 1.06 | 13.9% | 1.26 | 15.1% | 1.28 |
| Realized volatility | Above prior median | 115 | 4.2% | 0.46 | 7.0% | 0.61 | 13.6% | 0.72 |

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.


## Volatility-Target Robustness: NOT YET ROBUST

- Higher Sharpe across assets: **6 / 14**
- Smaller drawdown across assets: **14 / 14**
- Higher Sharpe across calendar years: **0 / 10**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Asset | EEM | 489 | 5.4% | 0.48 | -28.4% | 8.8% | 0.54 | -38.5% |
| Asset | EFA | 489 | 4.8% | 0.46 | -23.5% | 9.0% | 0.60 | -33.4% |
| Asset | EWJ | 489 | 5.7% | 0.53 | -23.6% | 9.1% | 0.61 | -32.7% |
| Asset | GLD | 489 | 11.3% | 0.90 | -18.7% | 13.1% | 0.84 | -22.6% |
| Asset | HYG | 489 | 3.8% | 0.58 | -15.6% | 4.2% | 0.49 | -20.8% |
| Asset | IWM | 489 | 3.5% | 0.34 | -22.6% | 9.0% | 0.50 | -40.0% |
| Asset | QQQ | 489 | 14.3% | 1.17 | -15.9% | 21.4% | 1.04 | -33.7% |
| Asset | SPY | 489 | 11.5% | 1.02 | -15.7% | 15.3% | 0.94 | -31.7% |
| Asset | TLT | 489 | -1.4% | -0.07 | -41.1% | -1.8% | -0.06 | -47.4% |
| Asset | UUP | 489 | 3.1% | 0.49 | -12.6% | 3.0% | 0.47 | -13.9% |
| Asset | VGK | 489 | 4.7% | 0.44 | -24.2% | 9.4% | 0.58 | -36.6% |
| Asset | XLE | 489 | 2.3% | 0.24 | -41.3% | 10.1% | 0.49 | -63.9% |
| Asset | XLF | 489 | 5.9% | 0.51 | -21.0% | 10.9% | 0.60 | -39.3% |
| Asset | XLK | 489 | 15.3% | 1.24 | -13.6% | 25.3% | 1.11 | -32.3% |
| Calendar year | 2017 | 49 | 17.0% | 3.27 | -1.4% | 18.3% | 3.36 | -1.4% |
| Calendar year | 2018 | 50 | -8.1% | -0.93 | -11.3% | -9.9% | -0.83 | -12.9% |
| Calendar year | 2019 | 51 | 16.0% | 2.50 | -3.6% | 24.9% | 2.74 | -4.2% |
| Calendar year | 2020 | 50 | 2.8% | 0.32 | -11.6% | 13.6% | 0.65 | -26.3% |
| Calendar year | 2021 | 51 | 7.6% | 1.33 | -2.3% | 14.1% | 1.66 | -2.5% |
| Calendar year | 2022 | 50 | -7.0% | -0.71 | -12.1% | -9.1% | -0.40 | -18.6% |
| Calendar year | 2023 | 50 | 8.4% | 1.01 | -6.3% | 14.1% | 1.28 | -7.4% |
| Calendar year | 2024 | 50 | 11.3% | 1.45 | -4.3% | 15.7% | 1.49 | -5.8% |
| Calendar year | 2025 | 50 | 15.1% | 2.04 | -4.7% | 22.6% | 2.07 | -7.4% |
| Calendar year | 2026 | 38 | 8.2% | 1.36 | -2.9% | 15.3% | 1.59 | -4.5% |

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.


## Multi-Asset Allocation Candidate: REJECTED AS A TRADING MODEL

- Trend/inverse-volatility allocation has the best yearly Sharpe in **1 / 10** years.
- Assets are selected only when their 63-day return and price-versus-200-day-average are positive; otherwise that sleeve stays in cash.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 14.4% | 17.2% | 0.87 | -23.1% | 0.62 |
| Inverse Volatility | 15.6% | 17.3% | 0.93 | -31.6% | 0.49 |
| Equal Weight | 16.2% | 17.7% | 0.94 | -32.1% | 0.50 |
| Spy | 15.1% | 15.9% | 0.97 | -27.4% | 0.55 |

The rule is fixed before evaluation, uses only decision-date information, rebalances every five sessions, and deducts 0.10% turnover cost.


## Diversified Allocation Candidate: REJECTED AS A TRADING MODEL

This test uses SPY, IWM, long Treasuries, high-yield credit, gold and the U.S. dollar instead of six mostly correlated equity sleeves.

- Trend/inverse-volatility allocation has the best yearly Sharpe in **1 / 10** years.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 6.2% | 7.5% | 0.84 | -9.2% | 0.68 |
| Inverse Volatility | 6.1% | 5.2% | 1.17 | -9.6% | 0.63 |
| Equal Weight | 7.8% | 8.0% | 0.98 | -16.1% | 0.49 |
| Spy | 15.1% | 15.9% | 0.97 | -27.4% | 0.55 |


## Dynamic Growth / Defense Candidate: REJECTED AS A TRADING MODEL

- The dynamic strategy has the best yearly Sharpe in **1 / 10** years.
- When SPY's 63-day return and price-versus-200-day average are positive, growth receives 50%; otherwise the diversified defensive sleeve receives 100%.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Dynamic Growth Defense | 9.6% | 7.7% | 1.22 | -12.4% | 0.78 |
| Static Half Growth | 10.7% | 10.1% | 1.06 | -17.3% | 0.62 |
| Defensive Inverse Vol | 6.1% | 5.2% | 1.17 | -9.6% | 0.63 |
| Spy | 15.1% | 15.9% | 0.97 | -27.4% | 0.55 |

### Paired block-bootstrap uncertainty

| Benchmark | Median Sharpe difference | 95% interval | Probability difference > 0 |
|---|---:|---:|---:|
| Static Half Growth | +0.15 | [-0.12, +0.44] | 86.6% |
| Defensive Inverse Vol | +0.05 | [-0.28, +0.39] | 61.6% |
| Spy | +0.24 | [-0.08, +0.58] | 93.9% |

The resampling keeps four adjacent five-session observations together. A candidate passes only if every 95% interval remains above zero in addition to the chronological and yearly gates.

### Cost and rebalance sensitivity

| One-way cost | Rebalance interval | Annual return | Sharpe | Maximum drawdown |
|---:|---:|---:|---:|---:|
| 0.05% | 5 sessions | 9.9% | 1.26 | -12.2% |
| 0.05% | 10 sessions | 10.0% | 1.27 | -12.4% |
| 0.05% | 20 sessions | 9.5% | 1.14 | -17.1% |
| 0.10% | 5 sessions | 9.6% | 1.22 | -12.4% |
| 0.10% | 10 sessions | 9.8% | 1.24 | -12.5% |
| 0.10% | 20 sessions | 9.4% | 1.12 | -17.1% |
| 0.20% | 5 sessions | 9.0% | 1.16 | -12.6% |
| 0.20% | 10 sessions | 9.4% | 1.20 | -12.7% |
| 0.20% | 20 sessions | 9.0% | 1.08 | -17.2% |

The candidate must remain profitable, above 1.0 Sharpe and within a 20% drawdown in every predeclared stress scenario.


## External-Market Validation: PASS

The U.S.-designed rule is frozen and applied without retuning to developed ex-U.S., emerging markets, Japan and Europe.

- Higher full-history Sharpe: **4 / 4** markets
- Smaller maximum drawdown: **4 / 4** markets
- Higher Sharpe in at least half of years: **3 / 4** markets

| Market | Dynamic ann. return | Dynamic Sharpe | Dynamic DD | Market ann. return | Market Sharpe | Market DD | Years higher Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| EFA | 4.9% | 0.73 | -12.4% | 7.9% | 0.56 | -29.3% | 4 / 10 |
| EEM | 5.8% | 0.72 | -15.0% | 7.0% | 0.46 | -38.6% | 5 / 10 |
| EWJ | 6.6% | 0.85 | -14.7% | 8.6% | 0.58 | -32.5% | 5 / 10 |
| VGK | 5.4% | 0.78 | -10.1% | 8.0% | 0.53 | -32.1% | 6 / 10 |


## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0227 |
| ret_21 | +0.0339 |
| ma_gap | -0.0484 |
| rsi14 | -0.0271 |
| vol_21 | +0.0105 |
| drawdown_63 | -0.0081 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least 55% probability and a 3% edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
