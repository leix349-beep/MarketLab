# Baseline V3 — separated growth and defensive sleeves

One frozen structure only: a 70% growth sleeve selecting two assets and a 30% defensive sleeve selecting one asset. Both use the existing trend, momentum, volatility, execution and cost rules.

The 2023+ segment is retrospective, not clean OOS, because those years were already observed.

| Cost | Period | Annual return | Sharpe | Max drawdown | Turnover |
| --- | --- | ---: | ---: | ---: | ---: |
| base | full_history | 7.03% | 0.83 | -15.64% | 3.26x |
| base | development_2017_2022 | 2.51% | 0.37 | -15.64% | 3.28x |
| base | retrospective_holdout_2023_plus | 13.55% | 1.33 | -8.41% | 3.24x |
| adverse | full_history | 5.42% | 0.65 | -15.78% | 3.26x |
| adverse | development_2017_2022 | 0.89% | 0.15 | -15.78% | 3.28x |
| adverse | retrospective_holdout_2023_plus | 11.95% | 1.19 | -8.76% | 3.24x |

## Asset contribution

| Asset | Annualized arithmetic contribution | Average weight |
| --- | ---: | ---: |
| GLD | 2.34% | 13.3% |
| EEM | 1.37% | 8.4% |
| SPY | 1.30% | 16.4% |
| TLT | 0.55% | 3.3% |
| EFA | 0.45% | 6.0% |
| UUP | 0.41% | 7.9% |
| EWJ | 0.21% | 10.7% |
| HYG | -0.01% | 8.3% |

## Gates

- full_annual_return_at_least_8pct: **False**
- full_sharpe_at_least_1: **False**
- full_maximum_drawdown_no_worse_than_15pct: **False**
- adverse_annual_return_at_least_8pct: **False**
- holdout_annual_return_positive: **True**
- at_least_three_equity_markets_contribute_positive: **True**
- largest_positive_asset_contribution_below_40pct: **True**

**Candidate: REJECTED. Model promotion remains HOLD_NOT_PROMOTED.**
This is historical, pre-tax research and not trading advice.
