# Prospective paper tracking

This folder records frozen growth/defense candidates after each market close. It is an evaluation log, not a brokerage connection.

Starting with the next new market date after the comparison was introduced, both the 25% conservative sleeve and the existing 50% sleeve are recorded in parallel. Older signals remain unchanged rather than being backfilled.

- `signals/`: weights calculated only from information available on the signal date.
- `outcomes/`: five-session results once enough later observations exist.
- `latest.md`: the newest paper allocation and regime.

To avoid same-close execution bias, scoring begins at the next archived market close. No historical signal is backfilled, no order is sent, and results are retained whether they win or lose.
