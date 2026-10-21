# MarketLab Model Training — 2026-10-20

Chronological out-of-sample research result. This model does not place orders.

## Data Freshness

- Latest available market price: **2026-10-20**
- Latest sample with a fully observed five-session outcome: **2026-10-13**
- Recent trading sessions awaiting a mature label: **5**

The gap is intentional: the model predicts the following five trading sessions and does not score observations before their outcomes exist.

## Verdict: REJECTED AS A TRADING MODEL

- Assets with predictive improvement over the naive baseline: **0 / 6**
- Assets outperforming buy and hold: **0 / 6**
- Assets improving risk-adjusted return (Sharpe): **0 / 6**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 1,689 | 59.7% | -0.4% | 49.7% | 7.4% | 55.2% | 2.1% | 158.2% | -11.7% |
| QQQ | 1,689 | 58.3% | -0.5% | 49.6% | 14.9% | 52.0% | -27.1% | 239.9% | -33.8% |
| IWM | 1,689 | 52.6% | -0.6% | 49.7% | 15.1% | 54.5% | -9.4% | 80.6% | -26.2% |
| XLK | 1,689 | 58.0% | -0.2% | 49.9% | 13.3% | 52.2% | -6.0% | 310.4% | -24.5% |
| XLF | 1,689 | 54.8% | -1.7% | 49.2% | 17.5% | 53.0% | -21.0% | 105.9% | -40.3% |
| XLE | 1,689 | 55.2% | -1.3% | 51.2% | 16.3% | 55.6% | 0.7% | 208.9% | -55.8% |

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.3% | 15.2% | 8.4% | 18.3% | 0.08 | 0.87 | 0.03 | 0.45 |
| QQQ | -4.6% | 20.0% | 12.5% | 22.1% | -0.31 | 0.94 | -0.14 | 0.58 |
| IWM | -1.5% | 9.2% | 13.6% | 24.4% | -0.04 | 0.48 | -0.06 | 0.23 |
| XLK | -0.9% | 23.4% | 10.0% | 25.3% | -0.04 | 0.96 | -0.04 | 0.70 |
| XLF | -3.5% | 11.4% | 15.7% | 22.8% | -0.14 | 0.59 | -0.09 | 0.27 |
| XLE | 0.1% | 18.3% | 21.3% | 32.2% | 0.12 | 0.69 | 0.00 | 0.33 |

## Downside-Risk Filter Candidate: REJECTED AS A TRADING MODEL

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **0 / 6**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 13.3% | 0.574 | 10.2% | 9.2% | 10.5% | 0.75 | 1.01 | -24.9% | -24.3% |
| QQQ | 20.3% | 0.528 | 17.1% | 17.1% | 3.1% | 0.25 | 0.87 | -45.8% | -34.7% |
| IWM | 20.0% | 0.426 | 2.9% | 8.2% | 4.1% | 0.30 | 0.57 | -35.5% | -31.2% |
| XLK | 21.7% | 0.477 | 11.0% | 13.1% | 7.5% | 0.44 | 0.95 | -36.8% | -33.1% |
| XLF | 15.6% | 0.504 | 3.3% | 3.5% | 10.8% | 0.65 | 0.87 | -33.8% | -25.6% |
| XLE | 23.6% | 0.462 | 9.0% | 9.3% | 18.3% | 0.77 | 1.01 | -28.9% | -25.9% |

## Cross-Asset Risk Candidate: REJECTED AS A TRADING MODEL

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **5 / 6**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.584 | 29.1% | 20.9% | 0.29 | 0.0% | 10.2% | 0.82 | 1.01 | -20.6% | -24.3% |
| QQQ | 0.507 | 21.0% | 19.7% | 0.29 | 0.0% | 10.1% | 0.60 | 0.87 | -32.0% | -34.7% |
| IWM | 0.441 | 29.9% | 25.6% | 0.28 | 0.0% | 8.0% | 0.51 | 0.57 | -25.3% | -31.2% |
| XLK | 0.467 | 16.0% | 15.3% | 0.33 | 4.1% | 11.5% | 0.62 | 0.95 | -39.6% | -33.1% |
| XLF | 0.546 | 38.8% | 32.7% | 0.31 | 4.1% | 6.0% | 0.48 | 0.87 | -21.5% | -25.6% |
| XLE | 0.463 | 11.7% | 12.9% | 0.44 | 8.1% | 14.3% | 0.66 | 1.01 | -25.9% | -25.9% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | 8.9% | 9.7% | 0.93 | -12.9% | 0.69 |
| ML binary allocation | 9.2% | 9.9% | 0.94 | -13.1% | 0.70 |
| Volatility target only | 11.6% | 11.5% | 1.02 | -16.0% | 0.72 |
| Buy and hold | 15.9% | 15.8% | 1.01 | -24.3% | 0.65 |

- Average smooth ML exposure: **70.5%**
- Average binary ML exposure: **70.8%**
- Average volatility-target exposure: **82.2%**


## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **2 / 6** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **2 / 6** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Market trend | Positive | 236 | 8.0% | 0.89 | 9.7% | 0.90 | 10.7% | 0.85 |
| Market trend | Negative | 75 | 12.0% | 1.03 | 17.9% | 1.33 | 33.8% | 1.41 |
| VIX state | Below 25 | 262 | 7.9% | 0.83 | 10.9% | 1.00 | 12.6% | 0.91 |
| VIX state | 25 or above | 49 | 14.7% | 1.45 | 15.6% | 1.12 | 35.5% | 1.43 |
| Realized volatility | At/below prior median | 174 | 8.2% | 0.84 | 11.6% | 1.06 | 12.5% | 1.07 |
| Realized volatility | Above prior median | 111 | 7.7% | 0.80 | 9.3% | 0.79 | 16.7% | 0.84 |

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.


## Volatility-Target Robustness: NOT YET ROBUST

- Higher Sharpe across assets: **6 / 14**
- Smaller drawdown across assets: **14 / 14**
- Higher Sharpe across calendar years: **0 / 10**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Asset | EEM | 489 | 5.0% | 0.46 | -28.4% | 8.2% | 0.51 | -38.5% |
| Asset | EFA | 489 | 4.8% | 0.46 | -23.5% | 8.9% | 0.60 | -33.4% |
| Asset | EWJ | 489 | 5.5% | 0.52 | -23.6% | 8.9% | 0.60 | -32.7% |
| Asset | GLD | 489 | 11.1% | 0.89 | -18.7% | 12.9% | 0.83 | -22.6% |
| Asset | HYG | 489 | 3.8% | 0.58 | -15.6% | 4.1% | 0.49 | -20.8% |
| Asset | IWM | 489 | 3.4% | 0.33 | -22.6% | 8.9% | 0.50 | -40.0% |
| Asset | QQQ | 489 | 13.9% | 1.14 | -15.9% | 20.9% | 1.02 | -33.7% |
| Asset | SPY | 489 | 11.4% | 1.01 | -15.7% | 15.2% | 0.93 | -31.7% |
| Asset | TLT | 489 | -1.1% | -0.05 | -41.1% | -1.5% | -0.04 | -47.4% |
| Asset | UUP | 489 | 3.2% | 0.51 | -12.6% | 3.1% | 0.49 | -13.9% |
| Asset | VGK | 489 | 4.8% | 0.44 | -24.2% | 9.4% | 0.59 | -36.6% |
| Asset | XLE | 489 | 2.8% | 0.28 | -41.3% | 10.9% | 0.51 | -63.9% |
| Asset | XLF | 489 | 6.3% | 0.54 | -21.0% | 11.3% | 0.62 | -39.3% |
| Asset | XLK | 489 | 14.8% | 1.19 | -13.6% | 24.6% | 1.08 | -32.3% |
| Calendar year | 2017 | 48 | 17.8% | 3.41 | -1.4% | 19.1% | 3.49 | -1.4% |
| Calendar year | 2018 | 50 | -8.1% | -0.93 | -11.3% | -9.9% | -0.83 | -12.9% |
| Calendar year | 2019 | 51 | 16.0% | 2.50 | -3.6% | 24.9% | 2.74 | -4.2% |
| Calendar year | 2020 | 50 | 2.8% | 0.32 | -11.6% | 13.6% | 0.65 | -26.3% |
| Calendar year | 2021 | 51 | 7.6% | 1.33 | -2.3% | 14.1% | 1.66 | -2.5% |
| Calendar year | 2022 | 50 | -7.0% | -0.71 | -12.1% | -9.1% | -0.40 | -18.6% |
| Calendar year | 2023 | 50 | 8.4% | 1.01 | -6.3% | 14.1% | 1.28 | -7.4% |
| Calendar year | 2024 | 50 | 11.3% | 1.45 | -4.3% | 15.7% | 1.49 | -5.8% |
| Calendar year | 2025 | 50 | 15.1% | 2.04 | -4.7% | 22.6% | 2.07 | -7.4% |
| Calendar year | 2026 | 39 | 7.4% | 1.24 | -2.9% | 13.9% | 1.47 | -4.5% |

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.


## Multi-Asset Allocation Candidate: REJECTED AS A TRADING MODEL

- Trend/inverse-volatility allocation has the best yearly Sharpe in **1 / 10** years.
- Assets are selected only when their 63-day return and price-versus-200-day-average are positive; otherwise that sleeve stays in cash.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 14.0% | 17.2% | 0.85 | -23.1% | 0.60 |
| Inverse Volatility | 15.4% | 17.3% | 0.91 | -31.6% | 0.49 |
| Equal Weight | 16.0% | 17.7% | 0.93 | -32.1% | 0.50 |
| Spy | 14.9% | 15.9% | 0.95 | -27.4% | 0.54 |

The rule is fixed before evaluation, uses only decision-date information, rebalances every five sessions, and deducts 0.10% turnover cost.


## Diversified Allocation Candidate: REJECTED AS A TRADING MODEL

This test uses SPY, IWM, long Treasuries, high-yield credit, gold and the U.S. dollar instead of six mostly correlated equity sleeves.

- Trend/inverse-volatility allocation has the best yearly Sharpe in **1 / 10** years.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 6.2% | 7.5% | 0.84 | -9.2% | 0.67 |
| Inverse Volatility | 6.0% | 5.2% | 1.16 | -9.6% | 0.63 |
| Equal Weight | 7.8% | 8.0% | 0.98 | -16.1% | 0.48 |
| Spy | 14.9% | 15.9% | 0.95 | -27.4% | 0.54 |


## Dynamic Growth / Defense Candidate: REJECTED AS A TRADING MODEL

- The dynamic strategy has the best yearly Sharpe in **1 / 10** years.
- When SPY's 63-day return and price-versus-200-day average are positive, growth receives 50%; otherwise the diversified defensive sleeve receives 100%.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Dynamic Growth Defense | 9.5% | 7.8% | 1.21 | -12.4% | 0.77 |
| Static Half Growth | 10.6% | 10.1% | 1.05 | -17.3% | 0.61 |
| Defensive Inverse Vol | 6.0% | 5.2% | 1.16 | -9.6% | 0.63 |
| Spy | 14.9% | 15.9% | 0.95 | -27.4% | 0.54 |

### Paired block-bootstrap uncertainty

| Benchmark | Median Sharpe difference | 95% interval | Probability difference > 0 |
|---|---:|---:|---:|
| Static Half Growth | +0.16 | [-0.13, +0.43] | 85.8% |
| Defensive Inverse Vol | +0.05 | [-0.30, +0.37] | 60.1% |
| Spy | +0.24 | [-0.06, +0.57] | 94.1% |

The resampling keeps four adjacent five-session observations together. A candidate passes only if every 95% interval remains above zero in addition to the chronological and yearly gates.

### Cost and rebalance sensitivity

| One-way cost | Rebalance interval | Annual return | Sharpe | Maximum drawdown |
|---:|---:|---:|---:|---:|
| 0.05% | 5 sessions | 9.8% | 1.24 | -12.2% |
| 0.05% | 10 sessions | 9.0% | 1.14 | -12.9% |
| 0.05% | 20 sessions | 8.2% | 1.01 | -18.0% |
| 0.10% | 5 sessions | 9.5% | 1.21 | -12.4% |
| 0.10% | 10 sessions | 8.8% | 1.11 | -12.9% |
| 0.10% | 20 sessions | 8.1% | 0.99 | -18.0% |
| 0.20% | 5 sessions | 8.9% | 1.14 | -12.6% |
| 0.20% | 10 sessions | 8.4% | 1.06 | -13.0% |
| 0.20% | 20 sessions | 7.7% | 0.95 | -18.0% |

The candidate must remain profitable, above 1.0 Sharpe and within a 20% drawdown in every predeclared stress scenario.


## Growth-Sleeve Risk / Return Frontier

The trend rule, defensive basket, rebalance interval and costs are unchanged. Only three predeclared maximum growth sleeves are compared; no winner is promoted from this table alone.

| Max growth sleeve | Average growth exposure | Annual return | Volatility | Sharpe | Maximum drawdown | Worst-5% average | Positive years | Years beating SPY Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 18.7% | 7.8% | 6.2% | 1.23 | -10.9% | -1.9% | 9 / 10 | 5 / 10 |
| 50% | 37.3% | 9.5% | 7.8% | 1.21 | -12.4% | -2.4% | 8 / 10 | 5 / 10 |
| 75% | 56.0% | 11.1% | 9.5% | 1.16 | -13.9% | -3.0% | 8 / 10 | 5 / 10 |


## External Growth-Sleeve Validation

The three U.S.-declared sleeve sizes are applied unchanged to EFA, EEM, EWJ and VGK. Averages summarize the four markets; no regional retuning is performed.

| Max growth sleeve | Avg annual return | Avg Sharpe | Worst market DD | Markets higher Sharpe | Markets smaller DD | Markets smaller tail loss | Markets winning most years |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 5.3% | 0.95 | -11.9% | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| 50% | 5.6% | 0.76 | -15.0% | 4 / 4 | 4 / 4 | 4 / 4 | 3 / 4 |
| 75% | 5.8% | 0.62 | -18.5% | 4 / 4 | 4 / 4 | 4 / 4 | 1 / 4 |


## Growth-Sleeve Statistical Uncertainty

- Comparisons with a 95% interval entirely above zero: **7 / 10**

| Market | Comparison | Median Sharpe difference | 95% interval | Probability 25% is higher |
|---|---|---:|---:|---:|
| SPY | 25% vs 50% | +0.02 | [-0.11, +0.17] | 60.6% |
| SPY | 25% vs 75% | +0.06 | [-0.14, +0.30] | 69.8% |
| EFA | 25% vs 50% | +0.19 | [+0.03, +0.35] | 99.1% |
| EFA | 25% vs 75% | +0.33 | [+0.08, +0.58] | 99.3% |
| EEM | 25% vs 50% | +0.19 | [+0.03, +0.35] | 99.2% |
| EEM | 25% vs 75% | +0.31 | [+0.06, +0.56] | 99.5% |
| EWJ | 25% vs 50% | +0.18 | [-0.00, +0.35] | 97.0% |
| EWJ | 25% vs 75% | +0.30 | [+0.01, +0.57] | 98.5% |
| VGK | 25% vs 50% | +0.18 | [+0.02, +0.35] | 98.2% |
| VGK | 25% vs 75% | +0.31 | [+0.06, +0.58] | 99.0% |

Paired circular-block resampling preserves four adjacent five-session observations. The 25% sleeve is not promoted unless the evidence is stable beyond point estimates.


## Risk-Aware 25% / 50% Growth Sleeve: REJECTED AS A REPLACEMENT

The sleeve is 50% only when trend is positive and neither VIX is at least 25 nor credit underperforms Treasuries; under either stress flag it falls to 25%, and under negative trend it falls to zero. Thresholds were fixed before this test.

- Highest Sharpe versus both fixed sleeves: **0 / 5** markets
- Smallest drawdown versus both fixed sleeves: **0 / 5** markets

| Market | Avg growth exposure | Annual return | Sharpe | Maximum drawdown | Worst-5% average | Fixed 25% Sharpe | Fixed 50% Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| SPY | 29.4% | 8.4% | 1.15 | -12.4% | -2.2% | 1.23 | 1.21 |
| EFA | 26.0% | 4.9% | 0.78 | -11.6% | -2.1% | 0.93 | 0.74 |
| EEM | 22.1% | 5.3% | 0.71 | -13.6% | -2.5% | 0.86 | 0.67 |
| EWJ | 24.6% | 6.7% | 0.94 | -13.9% | -2.2% | 1.01 | 0.83 |
| VGK | 24.8% | 5.0% | 0.79 | -10.0% | -2.2% | 0.97 | 0.79 |


## External-Market Validation: PASS

The U.S.-designed rule is frozen and applied without retuning to developed ex-U.S., emerging markets, Japan and Europe.

- Higher full-history Sharpe: **4 / 4** markets
- Smaller maximum drawdown: **4 / 4** markets
- Smaller average loss in the worst 5% of periods: **4 / 4** markets
- Higher Sharpe in at least half of years: **3 / 4** markets

| Market | Dynamic ann. return | Dynamic Sharpe | Dynamic DD | Dynamic tail loss | Market ann. return | Market Sharpe | Market DD | Market tail loss | Years higher Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EFA | 5.0% | 0.74 | -12.4% | -2.3% | 8.0% | 0.56 | -29.3% | -5.1% | 4 / 10 |
| EEM | 5.4% | 0.67 | -15.0% | -2.8% | 6.2% | 0.42 | -38.6% | -5.9% | 5 / 10 |
| EWJ | 6.4% | 0.83 | -14.7% | -2.5% | 8.2% | 0.56 | -32.5% | -5.0% | 5 / 10 |
| VGK | 5.4% | 0.79 | -10.1% | -2.3% | 8.2% | 0.54 | -32.1% | -5.6% | 7 / 10 |


## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0203 |
| ret_21 | +0.0321 |
| ma_gap | -0.0472 |
| rsi14 | -0.0263 |
| vol_21 | +0.0129 |
| drawdown_63 | -0.0089 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least 55% probability and a 3% edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
