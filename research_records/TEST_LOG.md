# MarketLab Test Log

## 2026-09-30 — Prototype validation

### Passed

- English and Chinese interface
- Manual Run Analysis behavior and retained results across tabs
- SPY and AAPL historical analysis
- Benchmark and sector comparison
- Candlestick, moving-average and volume charts
- Math Lab distribution and monthly heatmap
- Parameter experiment, bilingual headers and percentage formatting
- Trade log ordering and bilingual display
- Bilingual Markdown report and browser download
- Experiment CSV creation

### Issues found and fixed

- Nested parameter experiment initially cleared the main analysis state.
- English tables and reports contained Chinese or internal labels.
- Distribution chart labels overlapped.
- Asset risk metrics were not clearly distinguished from strategy metrics.
- Duplicate experiment clicks could create near-identical rows; a 30-second duplicate guard was added.
- Same-close signal and execution introduced timing bias. Signals now form after a close and execute at the next trading day's open.

### Consequence for research

Results produced before the next-open execution correction are prototype results only. They must not be used as final evidence. Baselines will be regenerated under the corrected execution model before formal comparisons begin.

### Remaining checks

- Execute automated strategy tests in the project's installed Python environment.
- Confirm corrected results in the web interface.
- Verify fee accounting and open-position valuation with hand calculations.
- Test one-year and ten-year windows, extreme parameters, missing data and network failure.
- Audit and classify legacy duplicate experiment records without deleting them.

## 2026-09-30 — Execution timing correction baseline

SPY, five years, MA 20/60, RSI limit 55, 5% stop loss, 10% take profit and 0.10% modeled cost:

| Metric | Same-close prototype | Next-open corrected |
|---|---:|---:|
| Strategy cumulative return | 16.7% | 14.7% |
| Maximum drawdown | -29.7% | -28.0% |
| Sharpe ratio | 0.36 | 0.32 |
| Number of trade actions | 37 | 39 |

Interpretation: the more realistic execution convention reduced return and risk-adjusted performance. The corrected result becomes the new prototype baseline; neither version is final evidence until walk-forward testing, cost verification and data-version archiving are complete.
