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
from global_context import context_assessment, download_global_factors, fetch_news_context, market_regime


WATCHLIST = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA", "XLK", "XLE", "XLF",
             "TLT", "HYG", "GLD", "UUP"]
DIVERSIFIED_TICKERS = ("SPY", "IWM", "TLT", "HYG", "GLD", "UUP")
OUTPUT_DIR = Path("published_research/daily")
PAPER_DIR = Path("published_research/paper_tracking")


def summarize(ticker: str, frame: pd.DataFrame) -> dict:
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.dropna(subset=["Close"]).copy()
    if len(frame) < 201:
        raise ValueError(f"{ticker}: fewer than 201 observations")

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
        "return_63d": float(frame["Close"].iloc[-1] / frame["Close"].iloc[-64] - 1),
        "volatility_21d_annualized": float(returns.tail(21).std() * np.sqrt(252)),
        "ma20": round(float(latest["fast"]), 4),
        "ma60": round(float(latest["slow"]), 4),
        "ma200": round(float(frame["Close"].rolling(200).mean().iloc[-1]), 4),
        "rsi14": round(rsi, 2),
        "trend_state": trend,
    }


def download_snapshot() -> pd.DataFrame:
    rows = []
    for ticker in WATCHLIST:
        try:
            data = yf.download(ticker, period="2y", auto_adjust=True, progress=False)
            rows.append(summarize(ticker, data))
        except Exception as exc:
            print(f"Skipping {ticker}: {exc}")
    if not rows:
        raise RuntimeError("No market data was available; no snapshot was written.")
    return pd.DataFrame(rows).sort_values("ticker").reset_index(drop=True)


def candidate_weights(snapshot: pd.DataFrame, growth_sleeve: float = 0.5) -> pd.DataFrame:
    """Freeze the current growth/defense weights without placing an order."""
    if not 0 <= growth_sleeve <= 1:
        raise ValueError("Growth sleeve must be between zero and one.")
    current = snapshot.set_index("ticker")
    missing = set(DIVERSIFIED_TICKERS) - set(current.index)
    if missing:
        raise ValueError(f"Paper signal is missing assets: {sorted(missing)}")
    sleeve = current.loc[list(DIVERSIFIED_TICKERS)].copy()
    inverse_vol = 1 / sleeve["volatility_21d_annualized"].replace(0, np.nan)
    defensive = inverse_vol / inverse_vol.sum()
    spy = sleeve.loc["SPY"]
    positive_trend = bool(spy["return_63d"] > 0 and spy["close"] > spy["ma200"])
    growth_share = growth_sleeve if positive_trend else 0.0
    weights = defensive * (1 - growth_share)
    weights.loc["SPY"] += growth_share
    result = pd.DataFrame({
        "signal_date": snapshot["date"].max(),
        "ticker": weights.index,
        "weight": weights.values,
        "candidate": f"growth_{int(growth_sleeve * 100):02d}",
        "growth_share": growth_share,
        "regime": "growth" if positive_trend else "defense",
    })
    return result.reset_index(drop=True)


def record_paper_signal(snapshot: pd.DataFrame) -> Path:
    """Write immutable 25% and 50% paper candidates for prospective scoring."""
    weights = pd.concat([
        candidate_weights(snapshot, growth_sleeve=0.25),
        candidate_weights(snapshot, growth_sleeve=0.50),
    ], ignore_index=True)
    signal_date = str(weights["signal_date"].iloc[0])
    signal_dir = PAPER_DIR / "signals"
    signal_dir.mkdir(parents=True, exist_ok=True)
    path = signal_dir / f"{signal_date}.csv"
    if not path.exists():
        weights.to_csv(path, index=False)
    else:
        weights = pd.read_csv(path)
        if "candidate" not in weights:
            weights["candidate"] = "growth_50"
    sections = []
    for candidate, group in weights.groupby("candidate", sort=True):
        allocation = ", ".join(
            f"{row.ticker} {row.weight:.1%}" for row in group.itertuples(index=False)
        )
        sections.append(
            f"## {candidate.replace('_', ' ').title()}\n\n"
            f"Regime: **{group['regime'].iloc[0]}** · Growth sleeve: "
            f"**{group['growth_share'].iloc[0]:.0%}**\n\n{allocation}"
        )
    (PAPER_DIR / "latest.md").write_text(
        f"# Paper Candidate — {signal_date}\n\n"
        f"{'\n\n'.join(sections)}\n\nThis is a frozen research observation. No order is sent. "
        "Scoring begins at the next archived close to avoid same-close execution bias.\n",
        encoding="utf-8",
    )
    return path


def score_mature_signal(snapshot: pd.DataFrame) -> Path | None:
    """Score after a one-session execution delay and five-session holding period."""
    snapshot_paths = sorted(OUTPUT_DIR.glob("????-??-??.csv"))
    if len(snapshot_paths) < 7:
        return None
    signal_snapshot_path = snapshot_paths[-7]
    entry_path = snapshot_paths[-6]
    signal_path = PAPER_DIR / "signals" / signal_snapshot_path.name
    if not signal_path.exists():
        return None
    outcome_dir = PAPER_DIR / "outcomes"
    outcome_dir.mkdir(parents=True, exist_ok=True)
    outcome_path = outcome_dir / signal_snapshot_path.name
    if outcome_path.exists():
        return outcome_path
    entry = pd.read_csv(entry_path).set_index("ticker")
    end = snapshot.set_index("ticker")
    weights = pd.read_csv(signal_path)
    if "candidate" not in weights:
        weights["candidate"] = "growth_50"
    tickers = list(weights["ticker"].unique())
    if not set(tickers).issubset(entry.index) or not set(tickers).issubset(end.index):
        return None
    asset_returns = end.loc[tickers, "close"] / entry.loc[tickers, "close"] - 1
    benchmark_return = float(end.loc["SPY", "close"] / entry.loc["SPY", "close"] - 1)
    rows = []
    for candidate, group in weights.groupby("candidate", sort=True):
        group = group.set_index("ticker")
        candidate_return = float((group["weight"] * asset_returns.loc[group.index]).sum())
        rows.append({
            "signal_date": signal_snapshot_path.stem,
            "entry_date": entry_path.stem,
            "evaluation_date": snapshot["date"].max(),
            "sessions": 5,
            "candidate": candidate,
            "candidate_return": candidate_return,
            "spy_return": benchmark_return,
            "excess_return": candidate_return - benchmark_return,
        })
    pd.DataFrame(rows).to_csv(outcome_path, index=False)
    return outcome_path


def markdown_report(snapshot: pd.DataFrame, factors: pd.DataFrame | None = None,
                    news: pd.DataFrame | None = None) -> str:
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
    if factors is not None and not factors.empty:
        regime = market_regime(factors)
        assessment = context_assessment(regime, news if news is not None else pd.DataFrame())
        lines += [
            "## Global Market Context", "",
            f"- Market regime: **{assessment['market_regime']}** (score {assessment['market_score']:+d})",
            f"- Headline-risk score: **{assessment['headline_risk_score']:+.2f}**",
            f"- Cross-check: **{assessment['stance']}**", "",
            "Market score uses US equities, emerging markets, credit versus Treasuries, and VIX. "
            "Headline risk is a keyword-based research feature, not verified sentiment or a forecast probability.", "",
            "| Factor | Ticker | 1D | 5D | 21D |", "|---|---:|---:|---:|---:|",
        ]
        for row in factors.sort_values("factor").itertuples(index=False):
            lines.append(f"| {row.factor} | {row.ticker} | {row.return_1d:.2%} | {row.return_5d:.2%} | {row.return_21d:.2%} |")
        lines.append("")
    if news is not None and not news.empty:
        lines += ["## International Situation Watch", ""]
        for row in news.groupby("category", sort=False).head(2).itertuples(index=False):
            lines.append(f"- **{row.category}:** [{row.title}]({row.url}) — {row.source}")
        lines += ["", "Headlines are collected for scenario monitoring. They are not treated as facts until independently verified, and they do not generate orders.", ""]
    return "\n".join(lines)


def main() -> None:
    snapshot = download_snapshot()
    market_date = snapshot["date"].max()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = OUTPUT_DIR / f"{market_date}.csv"
    if snapshot_path.exists():
        print(f"Market date {market_date} is already archived; preserving the original observation without backfilling newer context.")
        # A code deployment can introduce paper tracking after the daily market
        # snapshot was already archived. Freeze today's signal from the fresh
        # download without rewriting the immutable observation.
        record_paper_signal(snapshot)
        score_mature_signal(snapshot)
        return
    try:
        factors = download_global_factors()
    except Exception as exc:
        print(f"Global factors unavailable: {exc}")
        factors = pd.DataFrame()
    news = fetch_news_context()
    snapshot.to_csv(snapshot_path, index=False)
    factor_dir = OUTPUT_DIR / "global_factors"; factor_dir.mkdir(exist_ok=True)
    news_dir = OUTPUT_DIR / "news_context"; news_dir.mkdir(exist_ok=True)
    if not factors.empty:
        factors.to_csv(factor_dir / f"{market_date}.csv", index=False)
    news_path = news_dir / f"{market_date}.csv"
    if not news.empty and not news_path.exists():
        news.to_csv(news_path, index=False)
    (OUTPUT_DIR / f"{market_date}.md").write_text(markdown_report(snapshot, factors, news), encoding="utf-8")
    record_paper_signal(snapshot)
    score_mature_signal(snapshot)
    print(f"Saved {len(snapshot)} observations for {market_date}.")
    print("Freshness is evaluated in the Daily Monitor; duplicate market dates are intentionally not recommitted.")


if __name__ == "__main__":
    main()
