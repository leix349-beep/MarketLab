# Research Integrity Audit — 2026-10-21

**Verdict: BLOCKED FOR NEW MODEL PROMOTION.** Daily collection and prospective paper tracking may continue, but archived historical returns cannot promote a strategy.

| Check | Area | Status | Evidence | Required action |
|---|---|---|---|---|
| DATA-001 | data | PASS | 11 dated snapshots; 13 unique tickers; no duplicate date/ticker rows. | Each archived observation must have one row per date and ticker. |
| DATA-002 | data | PASS | Engineered training panel has provider, coverage and SHA-256 metadata. | Every evaluated panel must carry source, coverage and content fingerprint. |
| DATA-003 | data | FAIL | No immutable raw-price archive exists; Yahoo data are downloaded again for each run. | Freeze the exact raw OHLC input before evaluating a new candidate. |
| DATA-004 | data | FAIL | 2 labeled end date(s) have multiple dataset hashes; without raw files the revisions cannot be reconstructed. | Revisions must retain both the old and new raw input, not only hashes. |
| TIME-001 | timing | FAIL | Archived build_features defines future_return as close[t+5] / close[t] - 1 while features include close[t]. | A close-t signal may execute no earlier than open[t+1] (or a predeclared later price). |
| TIME-002 | timing | PASS | Prospective paper scoring enters on the next archived session and evaluates five sessions later; unit tests cover the delay. | Prospective observations must never use the signal-date close as an executable fill. |
| LEAK-001 | leakage | PASS | Chronological classifier refits use a five-session embargo; tests verify future labels do not alter earlier predictions. | Training labels may not overlap the unseen test block. |
| LEAK-002 | leakage | PASS | Reported five-session model returns are sampled every five rows and paper scorecards do not compound overlapping outcomes. | Overlapping outcomes may be described but not compounded as independent returns. |
| COST-001 | cost | PASS | Archived evaluations deduct a fixed 0.10% one-way cost from turnover. | Every strategy comparison must deduct a visible turnover-linked cost. |
| COST-002 | cost | FAIL | The cost model does not separately represent bid-ask spread, slippage, fund fees, cash yield or tax assumptions. | New candidates need a documented base cost plus adverse cost scenarios and cash return. |

## Mandatory boundary for the next model

1. Archive the exact adjusted OHLC input before any experiment.
2. Form the signal after close t and execute no earlier than open t+1.
3. Include turnover cost, an adverse-cost scenario and cash yield.
4. Keep the sealed 2026-10-20 baselines unchanged; label their returns as non-executable historical references.

This audit does not place orders or establish future profitability.
