# Frozen Research Baseline — 2026-10-20

This checkpoint closes the five-session direction-classification experiment.
Its failure is retained as evidence and it is no longer retrained by the daily
workflow. Historical code remains available only for reproducibility and
deliberate research runs.

The exact comparison values are sealed in
`frozen_baseline_2026-10-20.csv`. A test protects its SHA-256 digest. New
research must create a new dated result; it must not rewrite this checkpoint.

## Locked candidate gate

A candidate must satisfy all of the following after costs:

- annualized return at least 8%;
- Sharpe ratio at least 1.0 and at least 0.15 above a volatility-matched simple baseline;
- maximum drawdown no worse than -15%;
- profitable in a majority of rolling three-year windows;
- pass in at least three of the United States, Europe, Japan and emerging markets;
- remain viable outside one calendar year and across a reasonable parameter neighborhood.

Two consecutive out-of-sample failures retire a model family. The gate and
sealed test data may not be changed in response to a disappointing result.

## Daily workflow boundary

The scheduled workflow continues to archive market snapshots and prospective
paper signals. It does not retrain archived research models and never places
orders.
