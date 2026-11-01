# MarketLab 1.0 — Final Status

Closeout date: 2026-11-01  
Final decision: **HOLD_NOT_PROMOTED**  
Purpose after closeout: reproducible student research archive and interface demonstration

## What 1.0 established

MarketLab 1.0 tested whether explainable price, trend and momentum rules could deliver a robust improvement after next-open execution, explicit costs and time-ordered evaluation. It did not establish a tradeable edge.

The strongest frozen candidate was Baseline V2:

| Metric | Base costs | Adverse costs |
|---|---:|---:|
| Annualized return | 8.28% | 6.82% |
| Sharpe ratio | 0.94 | 0.79 |
| Maximum drawdown | -9.59% | -10.77% |
| Annual turnover | 3.45x | 3.45x |

It passed the base return and drawdown thresholds but failed the Sharpe, benchmark-edge and later robustness requirements. Fixed defense, conditional defense and separated growth/defense variants were also rejected. No 1.0 candidate is approved for real-money trading.

## Preserve for MarketLab 2.0

- Versioned market-data archives and checksums
- Next-open execution and no-look-ahead conventions
- Base and adverse cost scenarios
- Performance, drawdown, turnover and attribution utilities
- Automated tests and GitHub Actions validation
- Append-only research reports and failed-experiment retention
- Streamlit navigation, bilingual controls and visual theme
- Daily market snapshots as raw contextual observations

## Keep only as historical evidence

- Moving-average, RSI, mean-reversion and breakout demonstrations
- Baseline V2 and V3 research outputs
- Defensive-sleeve experiments
- Early direction classifiers and allocation candidates
- Historical paper signals and their scorecards

These files remain reproducible but must not be presented as current recommendations.

## Do not migrate as active 2.0 logic

- Old model parameters or candidate weights
- Keyword-based news sentiment as a trading signal
- Claims that repeated daily runs constitute model learning
- Any 1.0 signal-to-order path

## Automation after closeout

The scheduled workflow continues to archive reusable daily market observations. It no longer creates new signals from retired 1.0 candidates. Historical paper-tracking files remain unchanged.

## MarketLab 2.0 boundary

MarketLab 2.0 will be a separate project centered on point-in-time earnings expectations, guidance changes, financial-statement trends, post-event price reactions and sector capital rotation. Migration begins with infrastructure and tests, not with 1.0 strategies.
