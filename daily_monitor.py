"""Create a small, auditable end-of-day market snapshot.

This script is used by GitHub Actions. It records observations and model state;
it does not place orders or claim that a signal predicts future returns.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from strategy import indicators


WATCHLIST = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA", "XLK", "XLE", "XLF"]
OUTPUT_DIR = Path("published_research/daily")


def summarize(ticker: str, frame: pd.DataFrame) -> dict:
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.dropna(subset=["Close"]).copy()
    if len(frame) < 61:
        raise ValueError(f"{ticker}: fewer than 61 observations")

    enriched = indicators(frame, fast=20, slow=60)
    latest = enriched.iloc[-1]
    returns = frame["Close"].pct_change()
    rsi = float(latest["rsi"])
    if np.isnan(rsi):
        recent_changes = frame["Close"].diff().tail(14)
        if (recent_changes.dropna() >= 0).all():
            rsi = 100.0
        elif (recent_changes.dropna() <= 0).all():
            rsi = 0.0
        else:
            rsi = 50.0
    if latest["fast"] > latest["slow"]:
        trend = "Above MA20/60"
    elif latest["fast"] < latest["slow"]:
        trend = "Below MA20/60"
    else:
        trend = "At MA20/60"

    return {
        "date": frame.index[-1].date().isoformat(),
        "ticker": ticker,
        "close": round(float(latest["Close"]), 4),
        "return_1d": float(returns.iloc[-1]),
        "return_5d": float(frame["Close"].iloc[-1] / frame["Close"].iloc[-6] - 1),
        "return_21d": float(frame["Close"].iloc[-1] / frame["Close"].iloc[-22] - 1),
        "volatility_21d_annualized": float(returns.tail(21).std() * np.sqrt(252)),
        "ma20": round(float(latest["fast"]), 4),
        "ma60": round(float(latest["slow"]), 4),
        "rsi14": round(rsi, 2),
        "trend_state": trend,
    }


def download_snapshot() -> pd.DataFrame:
    rows = []
    for ticker in WATCHLIST:
        try:
            data = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
            rows.append(summarize(ticker, data))
        except Exception as exc:
            print(f"Skipping {ticker}: {exc}")
    if not rows:
        raise RuntimeError("No market data was available; no snapshot was written.")
    return pd.DataFrame(rows).sort_values("ticker").reset_index(drop=True)


def markdown_report(snapshot: pd.DataFrame) -> str:
    market_date = snapshot["date"].max()
    ranked = snapshot.sort_values("return_21d", ascending=False)
    lines = [
        f"# MarketLab Daily Snapshot — {market_date}",
        "",
        "Prospective observation log generated after the market close. This is research, not investment advice.",
        "",
        "## Summary",
        "",
        f"- Strongest 21-day return: **{ranked.iloc[0]['ticker']}** ({ranked.iloc[0]['return_21d']:.2%})",
        f"- Weakest 21-day return: **{ranked.iloc[-1]['ticker']}** ({ranked.iloc[-1]['return_21d']:.2%})",
        f"- Assets above MA20 and MA60: **{(snapshot['trend_state'] == 'Above MA20/60').sum()} / {len(snapshot)}**",
        "",
        "## Observations",
        "",
        "| Ticker | Close | 1D | 5D | 21D | Ann. vol (21D) | RSI14 | Trend state |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in snapshot.itertuples(index=False):
        lines.append(
            f"| {row.ticker} | {row.close:,.2f} | {row.return_1d:.2%} | {row.return_5d:.2%} | "
            f"{row.return_21d:.2%} | {row.volatility_21d_annualized:.2%} | {row.rsi14:.1f} | {row.trend_state} |"
        )
    lines += [
        "",
        "## Method",
        "",
        "Adjusted daily prices from Yahoo Finance via `yfinance`. Moving averages use 20 and 60 trading days; RSI uses 14 trading days. No orders are generated.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    snapshot = download_snapshot()
    market_date = snapshot["date"].max()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(OUTPUT_DIR / f"{market_date}.csv", index=False)
    (OUTPUT_DIR / f"{market_date}.md").write_text(markdown_report(snapshot), encoding="utf-8")
    print(f"Saved {len(snapshot)} observations for {market_date}.")


if __name__ == "__main__":
    main()
