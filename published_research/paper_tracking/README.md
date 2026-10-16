# Prospective paper tracking

This folder records the frozen growth/defense candidate after each market close. It is an evaluation log, not a brokerage connection.

- `signals/`: weights calculated only from information available on the signal date.
- `outcomes/`: five-session results once enough later observations exist.
- `latest.md`: the newest paper allocation and regime.

To avoid same-close execution bias, scoring begins at the next archived market close. No historical signal is backfilled, no order is sent, and results are retained whether they win or lose.
