# Prospective paper tracking

This folder records frozen growth/defense candidates after each market close. It is an evaluation log, not a brokerage connection.

Starting with the next new market date after the comparison was introduced, both the 25% conservative sleeve and the existing 50% sleeve are recorded in parallel. Older signals remain unchanged rather than being backfilled.

- `signals/`: weights calculated only from information available on the signal date.
- `outcomes/`: five-session results once enough later observations exist.
- `latest.md`: the newest paper allocation and regime.
- `scorecard.csv` and `scorecard.md`: aggregate mature outcomes by candidate without compounding overlapping five-session windows.

A candidate remains `COLLECTING` until it has at least 30 non-overlapping outcomes. It can only become `ELIGIBLE FOR REVIEW` when average excess return is positive, its SPY win rate is at least 55%, and the 95% four-block bootstrap lower bound for mean excess return is above zero. The block resampling retains adjacent market regimes instead of assuming every outcome is independent. This gate does not change the model automatically.

To avoid same-close execution bias, scoring begins at the next archived market close. No historical signal is backfilled, no order is sent, and results are retained whether they win or lose.
