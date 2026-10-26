# Baseline V2 return and risk attribution

Frozen archive: `prices-a75b446717b99a55`. No signal parameter was changed and no model was trained.

## Finding

The first issue is return consistency and asset-selection quality, not simply fees. Base-to-adverse assumptions reduce annual return by 1.47%, but the base case already misses the Sharpe gate. The portfolio held 18.5% cash on average; its weakest calendar-year Sharpe was -0.31 in 2022.

## Base-case arithmetic contribution

| Component | Annualized contribution |
| --- | ---: |
| GLD | 2.62% |
| SPY | 1.25% |
| EEM | 1.10% |
| TLT | 0.95% |
| EFA | 0.89% |
| EWJ | 0.77% |
| cash_income | 0.55% |
| UUP | 0.26% |
| HYG | 0.18% |
| trading_cost | -0.10% |
| fund_expense | -0.12% |

## Integrity check

Maximum daily reconciliation error: 3.175e-16.

## Next controlled hypothesis

Test one fixed broad defensive sleeve while keeping the signal, execution timing and cost model unchanged. This attribution does not promote the model and is not trading advice.
