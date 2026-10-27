# Conditional defensive-sleeve hypothesis

One change only: when close-t SPY is below its existing 200-day trend, the next-open allocation uses 80% of the frozen tactical book plus a 20% sleeve split equally across TLT, GLD and UUP. At all other times the frozen baseline is unchanged.

The 2023+ segment is a retrospective holdout, not clean OOS: those years were already visible when the hypothesis was proposed.

Defensive regime active on 17.7% of evaluated sessions.

| Strategy | Period | Annual return | Sharpe | Max drawdown | Turnover |
| --- | --- | ---: | ---: | ---: | ---: |
| frozen_baseline | full_history | 8.28% | 0.94 | -9.59% | 3.45x |
| frozen_baseline | retrospective_holdout_2023_plus | 10.32% | 1.06 | -9.59% | 3.54x |
| regime_defensive_sleeve | full_history | 8.21% | 0.94 | -9.25% | 3.94x |
| regime_defensive_sleeve | retrospective_holdout_2023_plus | 10.50% | 1.08 | -9.25% | 3.93x |

## Gates

- full_annual_return_at_least_8pct: **True**
- full_sharpe_at_least_1: **False**
- full_maximum_drawdown_no_worse_than_15pct: **True**
- holdout_sharpe_improves: **True**
- adverse_annual_return_at_least_8pct: **False**

**Hypothesis: REJECTED. Model promotion remains HOLD_NOT_PROMOTED.**
This is historical, pre-tax research and not trading advice.
