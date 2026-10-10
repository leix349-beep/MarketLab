from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_snapshot_history(directory: str | Path = "published_research/daily") -> pd.DataFrame:
    """Load the append-only daily snapshots into one tidy table."""
    frames = []
    for path in sorted(Path(directory).glob("20??-??-??.csv")):
        frame = pd.read_csv(path)
        if {"date", "ticker", "close"}.issubset(frame.columns):
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    history = pd.concat(frames, ignore_index=True)
    history["date"] = pd.to_datetime(history["date"])
    return (history.sort_values(["date", "ticker"])
            .drop_duplicates(["date", "ticker"], keep="last")
            .reset_index(drop=True))


def trading_day_lag(latest_date, current_date) -> int:
    """Count weekdays after the latest observation through the current date."""
    latest = pd.Timestamp(latest_date).normalize()
    current = pd.Timestamp(current_date).normalize()
    if current <= latest:
        return 0
    return max(0, len(pd.bdate_range(latest + pd.Timedelta(days=1), current)))


def build_forward_scorecard(history: pd.DataFrame) -> pd.DataFrame:
    """Evaluate each saved state against the next saved close, without hindsight."""
    if history.empty:
        return pd.DataFrame()
    scored = history.sort_values(["ticker", "date"]).copy()
    scored["next_return"] = scored.groupby("ticker")["close"].shift(-1) / scored["close"] - 1
    scored = scored.dropna(subset=["next_return"])
    if scored.empty:
        return pd.DataFrame()
    result = (scored.groupby("trend_state", as_index=False)
              .agg(observations=("next_return", "size"),
                   average_next_return=("next_return", "mean"),
                   win_rate=("next_return", lambda x: float((x > 0).mean()))))
    return result.sort_values("average_next_return", ascending=False).reset_index(drop=True)


def breadth_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        return pd.DataFrame(columns=["date", "above_both", "total", "breadth"])
    grouped = history.groupby("date")
    out = grouped["trend_state"].agg(
        above_both=lambda x: int((x == "Above MA20/60").sum()),
        total="size",
    ).reset_index()
    out["breadth"] = out["above_both"] / out["total"].replace(0, np.nan)
    return out
