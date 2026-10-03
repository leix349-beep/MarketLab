# MarketLab Research Record

This folder is the project's reproducible research journal.

- `experiments.csv` is created automatically when **Run Analysis** is clicked.
- Daily market context, hypotheses, failures, observations, and next steps will be added as the research workflow develops.
- Records should be preserved even when an experiment performs poorly; negative results are part of the research.

New formal runs also create:

- `raw_data/YYYY-MM-DD/`: the exact adjusted daily dataset plus a JSON source/checksum manifest.
- `experiment_manifests/`: strategy version, linked snapshot ID, parameters, metrics and limitations.
- `sector_snapshots/`: timestamped sector-ranking tables.
- `parameter_experiments/`: timestamped grid-search result tables.
- `daily_reports/`: automatically archived bilingual Markdown reports.

## Daily entry fields

1. Date and market context
2. Research question and hypothesis
3. Data range and model version
4. Parameters and benchmark
5. In-sample and out-of-sample results
6. Successes, failures, and anomalies
7. Interpretation and limitations
8. Next experiment

