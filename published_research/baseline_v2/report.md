# MarketLab Baseline V2 — Frozen First Run

Raw-data version: `prices-a75b446717b99a55`

No parameters were selected after viewing this result. Signals use close-t information and execute at open t+1.

| strategy | cost_scenario | average_invested_weight | annual_return | volatility | sharpe | maximum_drawdown | annual_turnover | rolling_3y_positive_rate | observations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trend_relative_momentum | base | 0.8148669737830068 | 8.28% | 8.84% | 0.94 | -9.59% | 3.45x | 100.00% | 2259 |
| trend_relative_momentum | adverse | 0.8150468251590632 | 6.82% | 8.85% | 0.79 | -10.77% | 3.45x | 99.93% | 2259 |
| spy | base | 1.0 | 14.58% | 18.00% | 0.85 | -32.06% | 0.11x | 100.00% | 2259 |
| spy | adverse | 1.0 | 14.04% | 18.00% | 0.82 | -32.09% | 0.11x | 100.00% | 2259 |
| equal_weight_equities | base | 1.0000000000000002 | 9.30% | 16.99% | 0.61 | -30.42% | 0.11x | 99.80% | 2259 |
| equal_weight_equities | adverse | 0.9999999999999468 | 8.79% | 16.99% | 0.58 | -30.47% | 0.11x | 99.53% | 2259 |
| sixty_forty | base | 1.000000000000004 | 10.11% | 12.49% | 0.83 | -28.33% | 0.11x | 99.40% | 2259 |
| sixty_forty | adverse | 1.000000000000056 | 9.60% | 12.49% | 0.80 | -28.58% | 0.11x | 98.94% | 2259 |
| spy_vol_target | base | 0.7005949746731719 | 9.06% | 10.75% | 0.86 | -16.85% | 2.09x | 100.00% | 2259 |
| spy_vol_target | adverse | 0.7005949746731719 | 7.46% | 10.75% | 0.72 | -17.06% | 2.09x | 100.00% | 2259 |

## Preliminary gates

- annual_return_at_least_8pct: **True**
- sharpe_at_least_1: **False**
- sharpe_edge_at_least_0_15: **False**
- maximum_drawdown_no_worse_than_15pct: **True**
- majority_rolling_3y_profitable: **True**
- cross_market_gate: **NOT_TESTED_IN_BASELINE_ROUND**

**Decision: HOLD_NOT_PROMOTED.** Cross-market and later robustness gates remain sealed. This is a historical, pre-tax research result and not a trading instruction.
