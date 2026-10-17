# MarketLab Model Training — 2026-10-09

Chronological out-of-sample research result. This model does not place orders.

## Verdict: REJECTED AS A TRADING MODEL

- Assets with predictive improvement over the naive baseline: **0 / 6**
- Assets outperforming buy and hold: **0 / 6**
- Assets improving risk-adjusted return (Sharpe): **0 / 6**
- A rejected model remains a recorded baseline; it must not generate a live-trading recommendation.

## Test Result by Asset

| Asset | OOS rows | Accuracy | Edge vs naive | Balanced acc. | Exposure | Signal win rate | Model return | Buy & hold | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 1,691 | 59.8% | -0.2% | 49.9% | 7.4% | 56.8% | 1.8% | 152.9% | -12.6% |
| QQQ | 1,691 | 58.3% | -0.4% | 49.7% | 13.5% | 52.8% | -11.0% | 230.4% | -25.0% |
| IWM | 1,691 | 52.5% | -0.7% | 49.5% | 15.6% | 53.2% | -24.1% | 73.7% | -35.7% |
| XLK | 1,691 | 57.9% | -0.3% | 49.8% | 13.1% | 54.5% | 1.3% | 299.2% | -21.9% |
| XLF | 1,691 | 54.5% | -1.8% | 49.0% | 17.5% | 52.4% | -27.6% | 102.6% | -33.1% |
| XLE | 1,691 | 55.0% | -1.3% | 51.2% | 16.6% | 54.4% | -1.7% | 203.3% | -48.3% |

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.3% | 14.8% | 6.7% | 17.0% | 0.07 | 0.90 | 0.02 | 0.54 |
| QQQ | -1.7% | 19.4% | 11.3% | 21.6% | -0.10 | 0.93 | -0.07 | 0.55 |
| IWM | -4.0% | 8.6% | 12.1% | 23.5% | -0.27 | 0.47 | -0.11 | 0.24 |
| XLK | 0.2% | 22.9% | 10.2% | 24.5% | 0.07 | 0.97 | 0.01 | 0.72 |
| XLF | -4.7% | 11.1% | 10.7% | 21.0% | -0.39 | 0.61 | -0.14 | 0.31 |
| XLE | -0.3% | 17.9% | 18.6% | 31.0% | 0.08 | 0.69 | -0.01 | 0.36 |

## Downside-Risk Filter Candidate: REJECTED AS A TRADING MODEL

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **1 / 6**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 13.3% | 0.576 | 11.2% | 8.9% | 8.6% | 0.63 | 1.02 | -28.8% | -23.5% |
| QQQ | 20.1% | 0.538 | 17.3% | 17.0% | 7.4% | 0.47 | 0.89 | -42.4% | -34.6% |
| IWM | 19.9% | 0.432 | 2.6% | 7.5% | 0.1% | 0.11 | 0.60 | -45.6% | -31.0% |
| XLK | 21.6% | 0.488 | 11.9% | 13.6% | 13.7% | 0.71 | 0.99 | -37.0% | -31.6% |
| XLF | 15.5% | 0.501 | 3.3% | 3.3% | 13.6% | 0.77 | 0.88 | -24.3% | -24.9% |
| XLE | 23.6% | 0.463 | 8.7% | 9.7% | 15.7% | 0.68 | 0.99 | -26.3% | -26.3% |

## Cross-Asset Risk Candidate: REJECTED AS A TRADING MODEL

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **3 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **2 / 6**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.586 | 43.7% | 32.8% | 0.22 | 0.0% | 7.7% | 0.68 | 1.02 | -18.6% | -23.5% |
| QQQ | 0.522 | 31.6% | 28.8% | 0.28 | 0.0% | 10.0% | 0.62 | 0.89 | -25.4% | -34.6% |
| IWM | 0.443 | 38.4% | 34.4% | 0.28 | 4.1% | 5.6% | 0.40 | 0.60 | -42.4% | -31.0% |
| XLK | 0.479 | 26.6% | 33.4% | 0.26 | 0.0% | 6.6% | 0.42 | 0.99 | -31.6% | -31.6% |
| XLF | 0.544 | 29.0% | 29.0% | 0.30 | 4.1% | 0.7% | 0.13 | 0.88 | -35.7% | -24.9% |
| XLE | 0.464 | 24.8% | 25.7% | 0.40 | 8.1% | 9.9% | 0.50 | 0.99 | -30.3% | -26.3% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | 6.7% | 9.1% | 0.76 | -14.1% | 0.47 |
| ML binary allocation | 7.6% | 9.4% | 0.83 | -14.1% | 0.54 |
| Volatility target only | 12.0% | 11.8% | 1.02 | -15.4% | 0.78 |
| Buy and hold | 16.5% | 16.2% | 1.02 | -23.5% | 0.70 |

- Average smooth ML exposure: **61.7%**
- Average binary ML exposure: **63.4%**
- Average volatility-target exposure: **82.0%**


## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **2 / 6** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **1 / 6** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Market trend | Positive | 235 | 6.8% | 0.77 | 11.5% | 0.99 | 12.4% | 0.89 |
| Market trend | Negative | 76 | 6.4% | 0.72 | 13.5% | 1.11 | 30.0% | 1.36 |
| VIX state | Below 25 | 265 | 5.8% | 0.64 | 10.2% | 0.89 | 11.9% | 0.83 |
| VIX state | 25 or above | 46 | 12.1% | 1.86 | 23.1% | 1.71 | 46.9% | 1.82 |
| Realized volatility | At/below prior median | 174 | 6.4% | 0.73 | 10.4% | 0.94 | 11.3% | 0.96 |
| Realized volatility | Above prior median | 111 | 6.8% | 0.71 | 11.2% | 0.90 | 19.8% | 0.96 |

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.


## Volatility-Target Robustness: NOT YET ROBUST

- Higher Sharpe across assets: **7 / 14**
- Smaller drawdown across assets: **14 / 14**
- Higher Sharpe across calendar years: **1 / 10**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Asset | EEM | 490 | 4.8% | 0.44 | -28.0% | 8.2% | 0.51 | -38.6% |
| Asset | EFA | 490 | 5.4% | 0.52 | -21.4% | 9.0% | 0.61 | -33.7% |
| Asset | EWJ | 490 | 5.8% | 0.53 | -23.4% | 8.9% | 0.59 | -32.9% |
| Asset | GLD | 490 | 11.4% | 0.94 | -18.7% | 13.1% | 0.84 | -25.5% |
| Asset | HYG | 490 | 3.8% | 0.62 | -15.0% | 4.1% | 0.51 | -22.0% |
| Asset | IWM | 490 | 3.8% | 0.36 | -22.2% | 9.0% | 0.51 | -41.1% |
| Asset | QQQ | 490 | 14.1% | 1.19 | -16.8% | 20.9% | 1.05 | -34.6% |
| Asset | SPY | 490 | 11.8% | 1.10 | -15.1% | 15.2% | 0.95 | -33.6% |
| Asset | TLT | 490 | -0.9% | -0.03 | -40.5% | -1.5% | -0.04 | -47.8% |
| Asset | UUP | 490 | 3.0% | 0.50 | -12.5% | 3.1% | 0.48 | -13.9% |
| Asset | VGK | 490 | 5.5% | 0.51 | -22.1% | 9.6% | 0.60 | -36.8% |
| Asset | XLE | 490 | 3.0% | 0.29 | -41.2% | 10.6% | 0.50 | -66.3% |
| Asset | XLF | 490 | 6.7% | 0.58 | -20.3% | 11.5% | 0.63 | -42.9% |
| Asset | XLK | 490 | 14.9% | 1.22 | -14.0% | 24.5% | 1.09 | -33.6% |
| Calendar year | 2017 | 49 | 18.0% | 3.31 | -1.6% | 19.1% | 3.34 | -1.7% |
| Calendar year | 2018 | 50 | -7.4% | -0.86 | -10.5% | -8.1% | -0.72 | -11.9% |
| Calendar year | 2019 | 50 | 15.5% | 2.42 | -3.2% | 22.7% | 2.74 | -3.7% |
| Calendar year | 2020 | 51 | 3.6% | 0.43 | -11.5% | 13.9% | 0.65 | -27.0% |
| Calendar year | 2021 | 50 | 7.7% | 1.35 | -2.8% | 14.7% | 1.82 | -3.1% |
| Calendar year | 2022 | 51 | -6.4% | -0.82 | -10.7% | -9.7% | -0.57 | -17.9% |
| Calendar year | 2023 | 50 | 9.0% | 1.12 | -5.6% | 14.8% | 1.36 | -7.0% |
| Calendar year | 2024 | 50 | 11.0% | 1.44 | -4.8% | 15.1% | 1.50 | -6.3% |
| Calendar year | 2025 | 50 | 15.2% | 1.95 | -5.7% | 22.8% | 1.90 | -9.1% |
| Calendar year | 2026 | 39 | 7.5% | 1.18 | -3.7% | 14.2% | 1.32 | -5.9% |

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.


## Multi-Asset Allocation Candidate: REJECTED AS A TRADING MODEL

- Trend/inverse-volatility allocation has the best yearly Sharpe in **2 / 10** years.
- Assets are selected only when their 63-day return and price-versus-200-day-average are positive; otherwise that sleeve stays in cash.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 11.8% | 17.5% | 0.73 | -32.4% | 0.36 |
| Inverse Volatility | 15.7% | 19.0% | 0.87 | -36.0% | 0.44 |
| Equal Weight | 16.3% | 19.6% | 0.87 | -36.8% | 0.44 |
| Spy | 15.1% | 17.0% | 0.92 | -29.1% | 0.52 |

The rule is fixed before evaluation, uses only decision-date information, rebalances every five sessions, and deducts 0.10% turnover cost.


## Diversified Allocation Candidate: REJECTED AS A TRADING MODEL

This test uses SPY, IWM, long Treasuries, high-yield credit, gold and the U.S. dollar instead of six mostly correlated equity sleeves.

- Trend/inverse-volatility allocation has the best yearly Sharpe in **1 / 10** years.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 6.2% | 8.0% | 0.79 | -12.2% | 0.51 |
| Inverse Volatility | 6.3% | 5.7% | 1.09 | -9.3% | 0.68 |
| Equal Weight | 7.9% | 8.8% | 0.91 | -16.3% | 0.49 |
| Spy | 15.1% | 17.0% | 0.92 | -29.1% | 0.52 |


## Dynamic Growth / Defense Candidate: REJECTED AS A TRADING MODEL

- The dynamic strategy has the best yearly Sharpe in **0 / 10** years.
- When SPY's 63-day return and price-versus-200-day average are positive, growth receives 50%; otherwise the diversified defensive sleeve receives 100%.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Dynamic Growth Defense | 9.2% | 8.5% | 1.09 | -16.0% | 0.58 |
| Static Half Growth | 10.8% | 10.9% | 1.00 | -19.6% | 0.55 |
| Defensive Inverse Vol | 6.3% | 5.7% | 1.09 | -9.3% | 0.68 |
| Spy | 15.1% | 17.0% | 0.92 | -29.1% | 0.52 |

### Paired block-bootstrap uncertainty

| Benchmark | Median Sharpe difference | 95% interval | Probability difference > 0 |
|---|---:|---:|---:|
| Static Half Growth | +0.08 | [-0.17, +0.35] | 76.3% |
| Defensive Inverse Vol | -0.01 | [-0.33, +0.34] | 48.6% |
| Spy | +0.16 | [-0.11, +0.47] | 88.3% |

The resampling keeps four adjacent five-session observations together. A candidate passes only if every 95% interval remains above zero in addition to the chronological and yearly gates.

### Cost and rebalance sensitivity

| One-way cost | Rebalance interval | Annual return | Sharpe | Maximum drawdown |
|---:|---:|---:|---:|---:|
| 0.05% | 5 sessions | 9.5% | 1.12 | -16.0% |
| 0.05% | 10 sessions | 8.8% | 1.00 | -19.6% |
| 0.05% | 20 sessions | 9.3% | 1.05 | -20.3% |
| 0.10% | 5 sessions | 9.2% | 1.09 | -16.0% |
| 0.10% | 10 sessions | 8.6% | 0.97 | -19.6% |
| 0.10% | 20 sessions | 9.2% | 1.03 | -20.3% |
| 0.20% | 5 sessions | 8.7% | 1.03 | -16.1% |
| 0.20% | 10 sessions | 8.1% | 0.93 | -19.6% |
| 0.20% | 20 sessions | 8.8% | 1.00 | -20.4% |

The candidate must remain profitable, above 1.0 Sharpe and within a 20% drawdown in every predeclared stress scenario.


## Growth-Sleeve Risk / Return Frontier

The trend rule, defensive basket, rebalance interval and costs are unchanged. Only three predeclared maximum growth sleeves are compared; no winner is promoted from this table alone.

| Max growth sleeve | Average growth exposure | Annual return | Volatility | Sharpe | Maximum drawdown | Worst-5% average | Positive years | Years beating SPY Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 18.5% | 7.8% | 6.9% | 1.13 | -12.7% | -2.3% | 9 / 10 | 6 / 10 |
| 50% | 37.0% | 9.2% | 8.5% | 1.09 | -16.0% | -2.9% | 9 / 10 | 4 / 10 |
| 75% | 55.5% | 10.6% | 10.3% | 1.04 | -19.3% | -3.6% | 8 / 10 | 4 / 10 |


## External Growth-Sleeve Validation

The three U.S.-declared sleeve sizes are applied unchanged to EFA, EEM, EWJ and VGK. Averages summarize the four markets; no regional retuning is performed.

| Max growth sleeve | Avg annual return | Avg Sharpe | Worst market DD | Markets higher Sharpe | Markets smaller DD | Markets smaller tail loss | Markets winning most years |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 5.0% | 0.83 | -12.2% | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| 50% | 4.8% | 0.63 | -15.8% | 4 / 4 | 4 / 4 | 4 / 4 | 2 / 4 |
| 75% | 4.5% | 0.49 | -19.2% | 1 / 4 | 4 / 4 | 4 / 4 | 0 / 4 |


## Growth-Sleeve Statistical Uncertainty

- Comparisons with a 95% interval entirely above zero: **8 / 10**

| Market | Comparison | Median Sharpe difference | 95% interval | Probability 25% is higher |
|---|---|---:|---:|---:|
| SPY | 25% vs 50% | +0.04 | [-0.10, +0.16] | 70.6% |
| SPY | 25% vs 75% | +0.09 | [-0.14, +0.30] | 77.6% |
| EFA | 25% vs 50% | +0.21 | [+0.04, +0.36] | 99.4% |
| EFA | 25% vs 75% | +0.36 | [+0.09, +0.60] | 99.5% |
| EEM | 25% vs 50% | +0.21 | [+0.07, +0.35] | 99.8% |
| EEM | 25% vs 75% | +0.35 | [+0.13, +0.57] | 100.0% |
| EWJ | 25% vs 50% | +0.18 | [+0.03, +0.34] | 98.9% |
| EWJ | 25% vs 75% | +0.31 | [+0.07, +0.56] | 99.4% |
| VGK | 25% vs 50% | +0.20 | [+0.03, +0.36] | 99.1% |
| VGK | 25% vs 75% | +0.35 | [+0.08, +0.61] | 99.6% |

Paired circular-block resampling preserves four adjacent five-session observations. The 25% sleeve is not promoted unless the evidence is stable beyond point estimates.


## Risk-Aware 25% / 50% Growth Sleeve: REJECTED AS A REPLACEMENT

The sleeve is 50% only when trend is positive and neither VIX is at least 25 nor credit underperforms Treasuries; under either stress flag it falls to 25%, and under negative trend it falls to zero. Thresholds were fixed before this test.

- Highest Sharpe versus both fixed sleeves: **0 / 5** markets
- Smallest drawdown versus both fixed sleeves: **0 / 5** markets

| Market | Avg growth exposure | Annual return | Sharpe | Maximum drawdown | Worst-5% average | Fixed 25% Sharpe | Fixed 50% Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| SPY | 29.4% | 8.4% | 1.07 | -12.7% | -2.7% | 1.13 | 1.09 |
| EFA | 25.6% | 4.4% | 0.67 | -11.3% | -2.2% | 0.83 | 0.63 |
| EEM | 22.5% | 5.0% | 0.65 | -11.9% | -2.6% | 0.77 | 0.56 |
| EWJ | 24.9% | 6.3% | 0.85 | -14.5% | -2.4% | 0.91 | 0.73 |
| VGK | 25.2% | 4.1% | 0.63 | -11.0% | -2.3% | 0.83 | 0.63 |


## External-Market Validation: FAIL

The U.S.-designed rule is frozen and applied without retuning to developed ex-U.S., emerging markets, Japan and Europe.

- Higher full-history Sharpe: **4 / 4** markets
- Smaller maximum drawdown: **4 / 4** markets
- Smaller average loss in the worst 5% of periods: **4 / 4** markets
- Higher Sharpe in at least half of years: **2 / 4** markets

| Market | Dynamic ann. return | Dynamic Sharpe | Dynamic DD | Dynamic tail loss | Market ann. return | Market Sharpe | Market DD | Market tail loss | Years higher Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EFA | 4.3% | 0.63 | -12.4% | -2.4% | 7.9% | 0.52 | -33.3% | -5.8% | 4 / 10 |
| EEM | 4.6% | 0.56 | -14.2% | -2.9% | 6.9% | 0.43 | -39.3% | -6.3% | 5 / 10 |
| EWJ | 5.7% | 0.73 | -15.8% | -2.6% | 8.5% | 0.56 | -32.8% | -5.4% | 3 / 10 |
| VGK | 4.4% | 0.63 | -11.5% | -2.5% | 8.0% | 0.49 | -36.9% | -6.5% | 5 / 10 |


## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0218 |
| ret_21 | +0.0326 |
| ma_gap | -0.0470 |
| rsi14 | -0.0278 |
| vol_21 | +0.0111 |
| drawdown_63 | -0.0080 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least 55% probability and a 3% edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
