# MarketLab Model Training — 2026-10-20

Chronological out-of-sample research result. This model does not place orders.

## Data Freshness

- Latest available market price: **2026-10-20**
- Latest sample with a fully observed five-session outcome: **2026-10-12**
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
| SPY | 1,689 | 59.8% | -0.4% | 49.8% | 7.2% | 56.6% | -13.1% | 155.2% | -19.0% |
| QQQ | 1,689 | 58.3% | -0.5% | 49.6% | 14.7% | 52.2% | 8.6% | 237.5% | -15.4% |
| IWM | 1,689 | 52.6% | -0.7% | 49.6% | 15.2% | 54.9% | -16.1% | 76.0% | -29.9% |
| XLK | 1,689 | 58.1% | -0.2% | 49.9% | 13.4% | 54.0% | -13.0% | 311.1% | -20.4% |
| XLF | 1,689 | 54.7% | -1.7% | 49.2% | 17.6% | 52.9% | -6.5% | 100.6% | -29.0% |
| XLE | 1,689 | 55.1% | -1.4% | 51.2% | 16.0% | 55.0% | -31.2% | 210.3% | -52.9% |

## Risk / Return Balance

| Asset | Model ann. return | B&H ann. return | Model vol. | B&H vol. | Model Sharpe | B&H Sharpe | Model Calmar | B&H Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | -2.1% | 15.0% | 7.4% | 18.5% | -0.25 | 0.85 | -0.11 | 0.47 |
| QQQ | 1.2% | 19.9% | 11.1% | 22.9% | 0.17 | 0.91 | 0.08 | 0.59 |
| IWM | -2.6% | 8.8% | 15.9% | 24.9% | -0.08 | 0.47 | -0.09 | 0.22 |
| XLK | -2.0% | 23.5% | 9.4% | 25.3% | -0.17 | 0.96 | -0.10 | 0.73 |
| XLF | -1.0% | 10.9% | 13.9% | 22.7% | -0.00 | 0.57 | -0.03 | 0.28 |
| XLE | -5.4% | 18.4% | 20.4% | 31.7% | -0.16 | 0.70 | -0.10 | 0.35 |

## Downside-Risk Filter Candidate: REJECTED AS A TRADING MODEL

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **3 / 6**

| Asset | Risk event rate | ROC AUC | Risk recall | Exit rate | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 13.3% | 0.573 | 10.2% | 9.1% | 9.8% | 0.75 | 1.03 | -25.0% | -23.2% |
| QQQ | 20.2% | 0.528 | 17.5% | 17.3% | 7.2% | 0.50 | 0.88 | -43.1% | -35.1% |
| IWM | 20.0% | 0.426 | 2.9% | 7.9% | 2.5% | 0.22 | 0.59 | -28.7% | -30.4% |
| XLK | 21.6% | 0.478 | 11.0% | 13.1% | 6.9% | 0.42 | 0.94 | -42.0% | -31.9% |
| XLF | 15.6% | 0.502 | 3.3% | 3.6% | 13.6% | 0.80 | 0.90 | -23.7% | -24.9% |
| XLE | 23.6% | 0.461 | 8.2% | 8.8% | 21.9% | 0.93 | 1.06 | -22.0% | -22.5% |

## Cross-Asset Risk Candidate: REJECTED AS A TRADING MODEL

Uses credit versus Treasuries, the dollar, gold, VIX, SPY trend and market breadth in addition to asset-price features.

- Assets with ROC AUC above 0.52: **2 / 6**
- Assets with higher Sharpe than buy and hold: **0 / 6**
- Assets with smaller maximum drawdown: **4 / 6**

| Asset | ROC AUC | Risk recall | Exit rate | Avg threshold | No-filter fallback | Ann. return | Model Sharpe | B&H Sharpe | Model DD | B&H DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 0.583 | 31.1% | 27.5% | 0.26 | 0.0% | 8.5% | 0.72 | 1.03 | -23.1% | -23.2% |
| QQQ | 0.508 | 31.8% | 32.8% | 0.27 | 2.6% | 6.3% | 0.46 | 0.88 | -29.8% | -35.1% |
| IWM | 0.442 | 30.9% | 25.1% | 0.27 | 0.0% | 6.9% | 0.46 | 0.59 | -26.3% | -30.4% |
| XLK | 0.467 | 24.1% | 29.2% | 0.26 | 0.0% | 6.7% | 0.42 | 0.94 | -38.0% | -31.9% |
| XLF | 0.545 | 33.5% | 32.5% | 0.28 | 4.1% | 2.0% | 0.21 | 0.90 | -24.2% | -24.9% |
| XLE | 0.460 | 22.1% | 21.1% | 0.44 | 12.2% | 15.3% | 0.73 | 1.06 | -22.5% | -22.5% |


## Portfolio Regime Candidate: REJECTED AS A TRADING MODEL

The learned risk signal controls exposure on top of a fixed 12% volatility target. This isolates whether machine learning adds value beyond ordinary risk scaling.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| ML smooth allocation | 8.7% | 9.2% | 0.95 | -13.1% | 0.67 |
| ML binary allocation | 9.0% | 9.6% | 0.95 | -13.6% | 0.66 |
| Volatility target only | 11.9% | 11.1% | 1.07 | -14.9% | 0.80 |
| Buy and hold | 15.9% | 15.5% | 1.03 | -23.2% | 0.69 |

- Average smooth ML exposure: **66.2%**
- Average binary ML exposure: **66.8%**
- Average volatility-target exposure: **81.8%**


## Observable-Regime Stability Audit

- Volatility target beats buy and hold on Sharpe in **2 / 6** observable states.
- Smooth ML allocation beats volatility target on Sharpe in **0 / 6** observable states.

| Dimension | State | Observations | Smooth ML ann. return | Smooth ML Sharpe | Vol-target ann. return | Vol-target Sharpe | B&H ann. return | B&H Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Market trend | Positive | 238 | 7.4% | 0.85 | 10.2% | 0.97 | 11.0% | 0.87 |
| Market trend | Negative | 73 | 13.0% | 1.24 | 17.6% | 1.34 | 33.5% | 1.42 |
| VIX state | Below 25 | 263 | 8.0% | 0.88 | 10.0% | 0.96 | 11.0% | 0.87 |
| VIX state | 25 or above | 48 | 12.6% | 1.31 | 22.7% | 1.58 | 46.7% | 1.64 |
| Realized volatility | At/below prior median | 171 | 11.7% | 1.27 | 13.9% | 1.31 | 15.0% | 1.35 |
| Realized volatility | Above prior median | 114 | 4.5% | 0.48 | 6.5% | 0.60 | 12.5% | 0.68 |

States use information available on each decision date: SPY MA20/60 trend, VIX 25, and an expanding prior median of realized volatility. No crisis dates are selected after seeing returns.


## Volatility-Target Robustness: NOT YET ROBUST

- Higher Sharpe across assets: **5 / 14**
- Smaller drawdown across assets: **14 / 14**
- Higher Sharpe across calendar years: **2 / 10**

| Scope | Asset / period | Observations | Vol-target ann. return | Vol-target Sharpe | Vol-target DD | B&H ann. return | B&H Sharpe | B&H DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Asset | EEM | 489 | 4.4% | 0.39 | -30.9% | 8.6% | 0.51 | -39.8% |
| Asset | EFA | 489 | 4.6% | 0.42 | -23.4% | 9.0% | 0.58 | -32.0% |
| Asset | EWJ | 489 | 5.2% | 0.46 | -24.1% | 9.1% | 0.58 | -31.8% |
| Asset | GLD | 489 | 11.0% | 0.89 | -19.2% | 13.2% | 0.82 | -23.2% |
| Asset | HYG | 489 | 3.5% | 0.51 | -15.5% | 4.2% | 0.51 | -18.9% |
| Asset | IWM | 489 | 3.1% | 0.29 | -22.8% | 9.1% | 0.48 | -38.6% |
| Asset | QQQ | 489 | 13.0% | 1.02 | -17.2% | 21.2% | 0.99 | -34.6% |
| Asset | SPY | 489 | 10.8% | 0.90 | -16.1% | 15.3% | 0.90 | -28.7% |
| Asset | TLT | 489 | -1.2% | -0.06 | -40.9% | -1.5% | -0.04 | -47.6% |
| Asset | UUP | 489 | 3.2% | 0.51 | -12.6% | 3.0% | 0.47 | -14.1% |
| Asset | VGK | 489 | 4.7% | 0.42 | -23.6% | 9.5% | 0.56 | -35.3% |
| Asset | XLE | 489 | 2.2% | 0.22 | -42.6% | 10.7% | 0.49 | -64.6% |
| Asset | XLF | 489 | 5.5% | 0.44 | -23.3% | 11.3% | 0.59 | -37.0% |
| Asset | XLK | 489 | 13.7% | 1.05 | -14.1% | 25.0% | 1.06 | -31.6% |
| Calendar year | 2017 | 48 | 17.4% | 3.85 | -1.4% | 18.5% | 3.83 | -1.4% |
| Calendar year | 2018 | 50 | -8.1% | -0.72 | -13.0% | -8.0% | -0.49 | -14.7% |
| Calendar year | 2019 | 51 | 14.6% | 2.00 | -4.2% | 23.1% | 2.51 | -4.3% |
| Calendar year | 2020 | 50 | 2.2% | 0.25 | -12.4% | 13.1% | 0.59 | -25.7% |
| Calendar year | 2021 | 51 | 8.1% | 1.14 | -3.5% | 15.4% | 1.50 | -4.1% |
| Calendar year | 2022 | 50 | -9.0% | -1.01 | -12.1% | -11.0% | -0.59 | -18.3% |
| Calendar year | 2023 | 50 | 9.6% | 1.10 | -6.3% | 16.5% | 1.38 | -7.5% |
| Calendar year | 2024 | 50 | 11.3% | 1.61 | -2.8% | 15.0% | 1.61 | -3.7% |
| Calendar year | 2025 | 50 | 12.7% | 1.34 | -8.2% | 22.1% | 1.42 | -12.6% |
| Calendar year | 2026 | 39 | 9.0% | 1.54 | -2.9% | 17.2% | 1.71 | -4.6% |

The 12% target is fixed before evaluation. Weights use only trailing volatility, five-day returns do not overlap, and 0.10% turnover cost is deducted.


## Multi-Asset Allocation Candidate: REJECTED AS A TRADING MODEL

- Trend/inverse-volatility allocation has the best yearly Sharpe in **2 / 10** years.
- Assets are selected only when their 63-day return and price-versus-200-day-average are positive; otherwise that sleeve stays in cash.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 14.6% | 16.6% | 0.90 | -22.9% | 0.64 |
| Inverse Volatility | 15.6% | 18.3% | 0.88 | -38.3% | 0.41 |
| Equal Weight | 16.1% | 18.7% | 0.89 | -38.9% | 0.41 |
| Spy | 15.0% | 16.8% | 0.92 | -33.6% | 0.45 |

The rule is fixed before evaluation, uses only decision-date information, rebalances every five sessions, and deducts 0.10% turnover cost.


## Diversified Allocation Candidate: REJECTED AS A TRADING MODEL

This test uses SPY, IWM, long Treasuries, high-yield credit, gold and the U.S. dollar instead of six mostly correlated equity sleeves.

- Trend/inverse-volatility allocation has the best yearly Sharpe in **2 / 10** years.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Trend Risk Parity | 6.1% | 7.1% | 0.87 | -8.4% | 0.73 |
| Inverse Volatility | 6.2% | 5.3% | 1.15 | -9.0% | 0.69 |
| Equal Weight | 7.9% | 8.3% | 0.96 | -15.3% | 0.52 |
| Spy | 15.0% | 16.8% | 0.92 | -33.6% | 0.45 |


## Dynamic Growth / Defense Candidate: REJECTED AS A TRADING MODEL

- The dynamic strategy has the best yearly Sharpe in **1 / 10** years.
- When SPY's 63-day return and price-versus-200-day average are positive, growth receives 50%; otherwise the diversified defensive sleeve receives 100%.

| Portfolio | Annual return | Volatility | Sharpe | Maximum drawdown | Calmar |
|---|---:|---:|---:|---:|---:|
| Dynamic Growth Defense | 9.3% | 7.8% | 1.19 | -13.2% | 0.71 |
| Static Half Growth | 10.7% | 10.7% | 1.01 | -21.4% | 0.50 |
| Defensive Inverse Vol | 6.2% | 5.3% | 1.15 | -9.0% | 0.69 |
| Spy | 15.0% | 16.8% | 0.92 | -33.6% | 0.45 |

### Paired block-bootstrap uncertainty

| Benchmark | Median Sharpe difference | 95% interval | Probability difference > 0 |
|---|---:|---:|---:|
| Static Half Growth | +0.16 | [-0.14, +0.49] | 84.7% |
| Defensive Inverse Vol | +0.03 | [-0.26, +0.35] | 57.4% |
| Spy | +0.25 | [-0.09, +0.63] | 92.1% |

The resampling keeps four adjacent five-session observations together. A candidate passes only if every 95% interval remains above zero in addition to the chronological and yearly gates.

### Cost and rebalance sensitivity

| One-way cost | Rebalance interval | Annual return | Sharpe | Maximum drawdown |
|---:|---:|---:|---:|---:|
| 0.05% | 5 sessions | 9.6% | 1.22 | -12.9% |
| 0.05% | 10 sessions | 9.5% | 1.15 | -15.0% |
| 0.05% | 20 sessions | 8.3% | 0.97 | -22.3% |
| 0.10% | 5 sessions | 9.3% | 1.19 | -13.2% |
| 0.10% | 10 sessions | 9.3% | 1.13 | -15.1% |
| 0.10% | 20 sessions | 8.2% | 0.95 | -22.3% |
| 0.20% | 5 sessions | 8.7% | 1.12 | -13.6% |
| 0.20% | 10 sessions | 8.9% | 1.08 | -15.1% |
| 0.20% | 20 sessions | 7.9% | 0.92 | -22.3% |

The candidate must remain profitable, above 1.0 Sharpe and within a 20% drawdown in every predeclared stress scenario.


## Growth-Sleeve Risk / Return Frontier

The trend rule, defensive basket, rebalance interval and costs are unchanged. Only three predeclared maximum growth sleeves are compared; no winner is promoted from this table alone.

| Max growth sleeve | Average growth exposure | Annual return | Volatility | Sharpe | Maximum drawdown | Worst-5% average | Positive years | Years beating SPY Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 18.9% | 7.8% | 6.3% | 1.21 | -11.1% | -1.9% | 8 / 10 | 5 / 10 |
| 50% | 37.9% | 9.3% | 7.8% | 1.19 | -13.2% | -2.5% | 9 / 10 | 4 / 10 |
| 75% | 56.8% | 10.8% | 9.4% | 1.14 | -15.2% | -3.1% | 9 / 10 | 4 / 10 |


## External Growth-Sleeve Validation

The three U.S.-declared sleeve sizes are applied unchanged to EFA, EEM, EWJ and VGK. Averages summarize the four markets; no regional retuning is performed.

| Max growth sleeve | Avg annual return | Avg Sharpe | Worst market DD | Markets higher Sharpe | Markets smaller DD | Markets smaller tail loss | Markets winning most years |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25% | 5.3% | 0.93 | -11.5% | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| 50% | 5.6% | 0.75 | -14.4% | 4 / 4 | 4 / 4 | 4 / 4 | 4 / 4 |
| 75% | 5.7% | 0.62 | -18.9% | 4 / 4 | 4 / 4 | 4 / 4 | 3 / 4 |


## Growth-Sleeve Statistical Uncertainty

- Comparisons with a 95% interval entirely above zero: **7 / 10**

| Market | Comparison | Median Sharpe difference | 95% interval | Probability 25% is higher |
|---|---|---:|---:|---:|
| SPY | 25% vs 50% | +0.03 | [-0.10, +0.15] | 64.5% |
| SPY | 25% vs 75% | +0.07 | [-0.14, +0.29] | 72.6% |
| EFA | 25% vs 50% | +0.16 | [+0.01, +0.32] | 98.0% |
| EFA | 25% vs 75% | +0.29 | [+0.04, +0.53] | 98.9% |
| EEM | 25% vs 50% | +0.18 | [+0.02, +0.33] | 98.8% |
| EEM | 25% vs 75% | +0.29 | [+0.05, +0.54] | 99.1% |
| EWJ | 25% vs 50% | +0.17 | [-0.01, +0.34] | 97.3% |
| EWJ | 25% vs 75% | +0.29 | [+0.02, +0.56] | 98.0% |
| VGK | 25% vs 50% | +0.20 | [+0.05, +0.36] | 99.5% |
| VGK | 25% vs 75% | +0.34 | [+0.11, +0.59] | 99.9% |

Paired circular-block resampling preserves four adjacent five-session observations. The 25% sleeve is not promoted unless the evidence is stable beyond point estimates.


## Risk-Aware 25% / 50% Growth Sleeve: REJECTED AS A REPLACEMENT

The sleeve is 50% only when trend is positive and neither VIX is at least 25 nor credit underperforms Treasuries; under either stress flag it falls to 25%, and under negative trend it falls to zero. Thresholds were fixed before this test.

- Highest Sharpe versus both fixed sleeves: **0 / 5** markets
- Smallest drawdown versus both fixed sleeves: **0 / 5** markets

| Market | Avg growth exposure | Annual return | Sharpe | Maximum drawdown | Worst-5% average | Fixed 25% Sharpe | Fixed 50% Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| SPY | 30.4% | 8.1% | 1.12 | -13.2% | -2.3% | 1.21 | 1.19 |
| EFA | 26.8% | 5.1% | 0.80 | -10.6% | -2.1% | 0.95 | 0.78 |
| EEM | 22.6% | 5.9% | 0.77 | -13.2% | -2.4% | 0.88 | 0.70 |
| EWJ | 24.5% | 6.7% | 0.95 | -13.1% | -2.2% | 1.01 | 0.84 |
| VGK | 26.4% | 4.4% | 0.67 | -13.3% | -2.2% | 0.89 | 0.68 |


## External-Market Validation: PASS

The U.S.-designed rule is frozen and applied without retuning to developed ex-U.S., emerging markets, Japan and Europe.

- Higher full-history Sharpe: **4 / 4** markets
- Smaller maximum drawdown: **4 / 4** markets
- Smaller average loss in the worst 5% of periods: **4 / 4** markets
- Higher Sharpe in at least half of years: **4 / 4** markets

| Market | Dynamic ann. return | Dynamic Sharpe | Dynamic DD | Dynamic tail loss | Market ann. return | Market Sharpe | Market DD | Market tail loss | Years higher Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EFA | 5.3% | 0.78 | -11.6% | -2.3% | 7.9% | 0.54 | -33.7% | -5.2% | 7 / 10 |
| EEM | 5.7% | 0.70 | -14.1% | -2.6% | 6.4% | 0.42 | -38.6% | -5.9% | 6 / 10 |
| EWJ | 6.3% | 0.84 | -14.0% | -2.4% | 8.3% | 0.55 | -32.9% | -5.5% | 5 / 10 |
| VGK | 4.9% | 0.68 | -14.4% | -2.4% | 8.1% | 0.52 | -36.8% | -5.8% | 7 / 10 |


## Latest standardized coefficients

| Feature | Coefficient |
|---|---:|
| ret_5 | -0.0212 |
| ret_21 | +0.0326 |
| ma_gap | -0.0474 |
| rsi14 | -0.0265 |
| vol_21 | +0.0125 |
| drawdown_63 | -0.0087 |

Each asset is trained and tested independently with a regularized logistic regression. The model is refit every 63 trading days and separated from each test block by a five-day embargo. Exposure requires at least 55% probability and a 3% edge over the training-period base rate. Returns use non-overlapping five-day samples and deduct 0.10% when exposure changes. They remain historical research rather than evidence of future profit.
