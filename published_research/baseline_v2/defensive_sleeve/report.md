# Frozen defensive-sleeve hypothesis

One change only: 80% of the frozen tactical strategy plus a permanent 20% sleeve split equally across TLT, GLD and UUP. No alternative sleeve weight was tested.

The 2023+ segment is a retrospective holdout, not clean OOS: those years were already visible when the hypothesis was proposed.

| Strategy | Period | Annual return | Sharpe | Max drawdown |
| --- | --- | ---: | ---: | ---: |
| frozen_baseline | full_history | 8.28% | 0.94 | -9.59% |
| frozen_baseline | retrospective_holdout_2023_plus | 10.32% | 1.06 | -9.59% |
| fixed_defensive_sleeve | full_history | 7.75% | 1.00 | -8.05% |
| fixed_defensive_sleeve | retrospective_holdout_2023_plus | 10.00% | 1.15 | -8.05% |

## Gates

- full_annual_return_at_least_8pct: **False**
- full_sharpe_at_least_1: **True**
- full_maximum_drawdown_no_worse_than_15pct: **True**
- holdout_sharpe_improves: **True**
- adverse_annual_return_at_least_8pct: **False**

**Hypothesis: REJECTED. Model promotion remains HOLD_NOT_PROMOTED.**
This is historical, pre-tax research and not trading advice.
