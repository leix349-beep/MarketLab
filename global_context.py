from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import pandas as pd
import requests
import yfinance as yf


GLOBAL_PROXIES = {
    "SPY": "US Equities", "QQQ": "US Growth", "IWM": "US Small Caps",
    "EFA": "Developed ex-US", "EEM": "Emerging Markets", "FXI": "China Large Caps",
    "HYG": "High-Yield Credit", "TLT": "Long Treasuries", "UUP": "US Dollar",
    "GLD": "Gold", "USO": "Oil", "^VIX": "VIX",
}

NEWS_QUERIES = {
    "Geopolitical conflict": "(war OR conflict OR ceasefire OR military) markets when:1d",
    "Trade and sanctions": "(tariff OR sanctions OR export controls) markets when:1d",
    "Central banks": "(Federal Reserve OR ECB OR BOJ OR interest rates) markets when:1d",
    "Energy supply": "(oil supply OR OPEC OR energy disruption) markets when:1d",
}

ESCALATION_WORDS = {"war", "attack", "conflict", "sanctions", "tariff", "disruption", "crisis", "threat", "escalat"}
EASING_WORDS = {"ceasefire", "agreement", "deal", "easing", "de-escalat", "truce", "resume talks"}


def _flat_download(ticker: str) -> pd.DataFrame:
    frame = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    return frame.dropna(subset=["Close"])


def download_global_factors() -> pd.DataFrame:
    rows = []
    for ticker, label in GLOBAL_PROXIES.items():
        try:
            frame = _flat_download(ticker)
            if len(frame) < 22:
                continue
            close = frame["Close"]
            rows.append({
                "date": close.index[-1].date().isoformat(), "ticker": ticker, "factor": label,
                "close": float(close.iloc[-1]), "return_1d": float(close.iloc[-1] / close.iloc[-2] - 1),
                "return_5d": float(close.iloc[-1] / close.iloc[-6] - 1),
                "return_21d": float(close.iloc[-1] / close.iloc[-22] - 1),
                "volatility_21d": float(close.pct_change().tail(21).std() * (252 ** .5)),
            })
        except Exception as exc:
            print(f"Skipping global factor {ticker}: {exc}")
    if not rows:
        raise RuntimeError("No global factor data was available.")
    return pd.DataFrame(rows)


def market_regime(factors: pd.DataFrame) -> dict:
    by_ticker = factors.set_index("ticker")
    required = {"SPY", "HYG", "TLT", "^VIX", "EEM"}
    if not required.issubset(by_ticker.index):
        return {"score": 0, "label": "Incomplete", "signals": 0}
    votes = [
        1 if by_ticker.loc["SPY", "return_5d"] > 0 else -1,
        1 if by_ticker.loc["EEM", "return_5d"] > 0 else -1,
        1 if by_ticker.loc["HYG", "return_5d"] > by_ticker.loc["TLT", "return_5d"] else -1,
        1 if by_ticker.loc["^VIX", "return_5d"] < 0 else -1,
    ]
    score = int(round(100 * sum(votes) / len(votes)))
    label = "Risk-On" if score >= 50 else "Defensive" if score <= -50 else "Mixed"
    return {"score": score, "label": label, "signals": len(votes)}


def _headline_risk(title: str) -> int:
    text = title.lower()
    escalation = sum(word in text for word in ESCALATION_WORDS)
    easing = sum(word in text for word in EASING_WORDS)
    return max(-2, min(2, escalation - easing))


def fetch_news_context(limit_per_category: int = 5) -> pd.DataFrame:
    rows = []
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    headers = {"User-Agent": "MarketLab educational research/1.0"}
    for category, query in NEWS_QUERIES.items():
        try:
            url = ("https://news.google.com/rss/search?q=" + quote_plus(query) +
                   "&hl=en-US&gl=US&ceid=US:en")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item")[:limit_per_category]:
                title = item.findtext("title") or ""
                source_node = item.find("source")
                rows.append({
                    "captured_at_utc": captured, "category": category, "title": title,
                    "source": source_node.text if source_node is not None else "Unknown",
                    "published": item.findtext("pubDate") or "", "url": item.findtext("link") or "",
                    "headline_risk": _headline_risk(title),
                })
        except Exception as exc:
            print(f"Skipping news category {category}: {exc}")
    return pd.DataFrame(rows)


def context_assessment(regime: dict, news: pd.DataFrame) -> dict:
    news_score = float(news["headline_risk"].mean()) if not news.empty else 0.0
    high_news_risk = news_score >= .5
    if regime["label"] == "Defensive" and high_news_risk:
        stance = "Defensive confirmation"
    elif regime["label"] == "Risk-On" and not high_news_risk:
        stance = "Constructive confirmation"
    else:
        stance = "Mixed / no confirmation"
    return {"market_regime": regime["label"], "market_score": regime["score"],
            "headline_risk_score": news_score, "stance": stance}
