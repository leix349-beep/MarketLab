"""Versioned, immutable adjusted-OHLCV archives for future MarketLab research."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path

import pandas as pd
import yfinance as yf

from model_training import (CONTEXT_TICKERS, EXTERNAL_GROWTH_TICKERS,
                            TRAIN_TICKERS, DIVERSIFIED_TICKERS)

ARCHIVE_ROOT = Path("published_research/raw_prices")
ARCHIVE_TICKERS = tuple(dict.fromkeys((
    *TRAIN_TICKERS, *DIVERSIFIED_TICKERS, *CONTEXT_TICKERS,
    *EXTERNAL_GROWTH_TICKERS,
)))
PRICE_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def archived_csv_sha256(path: Path) -> str:
    """Hash CSV content consistently across Git's LF/CRLF checkout modes."""
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return sha256(content).hexdigest()


def canonical_price_csv(prices: pd.DataFrame) -> bytes:
    """Return stable CSV bytes used both for storage and content identity."""
    required = {"date", "ticker", *PRICE_COLUMNS}
    if not required.issubset(prices.columns):
        raise ValueError(f"Raw prices are missing columns: {sorted(required - set(prices.columns))}")
    canonical = prices[["date", "ticker", *PRICE_COLUMNS]].copy()
    canonical["date"] = pd.to_datetime(canonical["date"]).dt.strftime("%Y-%m-%d")
    canonical = canonical.sort_values(["date", "ticker"]).reset_index(drop=True)
    if canonical.duplicated(["date", "ticker"]).any():
        raise ValueError("Raw prices contain duplicate date/ticker rows.")
    if canonical[list(PRICE_COLUMNS)].isna().any().any():
        raise ValueError("Raw prices contain missing OHLCV values.")
    buffer = io.StringIO(newline="")
    canonical.to_csv(buffer, index=False, lineterminator="\n", float_format="%.10g")
    return buffer.getvalue().encode("utf-8")


def download_adjusted_prices(tickers: tuple[str, ...] = ARCHIVE_TICKERS,
                             period: str = "10y") -> pd.DataFrame:
    """Download the exact adjusted OHLCV rows that will be archived."""
    parts = []
    failures = []
    for ticker in tickers:
        frame = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        if frame.empty or not set(PRICE_COLUMNS).issubset(frame.columns):
            failures.append(ticker)
            continue
        part = frame.loc[:, list(PRICE_COLUMNS)].dropna().reset_index()
        date_column = "Date" if "Date" in part.columns else part.columns[0]
        part = part.rename(columns={date_column: "date"})
        part["ticker"] = ticker
        parts.append(part[["date", "ticker", *PRICE_COLUMNS]])
    if failures:
        raise RuntimeError(f"Raw archive is incomplete; failed tickers: {', '.join(failures)}")
    if not parts:
        raise RuntimeError("No raw prices were downloaded.")
    return pd.concat(parts, ignore_index=True)


def archive_prices(prices: pd.DataFrame, root: Path = ARCHIVE_ROOT,
                   provider: str = "Yahoo Finance via yfinance",
                   period: str = "10y",
                   retrieved_at: str | None = None) -> dict[str, object]:
    """Write a content-addressed archive; existing versions are never replaced."""
    content = canonical_price_csv(prices)
    digest = sha256(content).hexdigest()
    version_id = f"prices-{digest[:16]}"
    version_dir = root / version_id
    data_path = version_dir / "prices.csv"
    manifest_path = version_dir / "manifest.json"
    if version_dir.exists():
        if not data_path.exists() or archived_csv_sha256(data_path) != digest:
            raise FileExistsError(f"Archive version {version_id} exists with different content.")
        if not manifest_path.exists():
            raise FileExistsError(f"Archive version {version_id} is missing its manifest.")
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    canonical = pd.read_csv(io.BytesIO(content))
    manifest = {
        "version_id": version_id,
        "provider": provider,
        "price_adjustment": "auto_adjust=True",
        "period_request": period,
        "retrieved_at_utc": retrieved_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_file": "prices.csv",
        "sha256": digest,
        "rows": int(len(canonical)),
        "tickers": sorted(canonical["ticker"].unique().tolist()),
        "ticker_count": int(canonical["ticker"].nunique()),
        "first_date": str(canonical["date"].min()),
        "last_date": str(canonical["date"].max()),
        "columns": ["date", "ticker", *PRICE_COLUMNS],
    }
    version_dir.mkdir(parents=True, exist_ok=False)
    data_path.write_bytes(content)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def load_price_archive(version_id: str, root: Path = ARCHIVE_ROOT) -> pd.DataFrame:
    """Load one explicit version and reject altered or ambiguous input."""
    if not version_id or version_id.lower() == "latest":
        raise ValueError("An explicit raw-price version_id is required; 'latest' is not allowed.")
    version_dir = root / version_id
    manifest_path = version_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Unknown raw-price archive: {version_id}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data_path = version_dir / str(manifest["data_file"])
    actual = archived_csv_sha256(data_path)
    if actual != manifest["sha256"]:
        raise ValueError(f"Raw-price archive hash mismatch for {version_id}.")
    return pd.read_csv(data_path, parse_dates=["date"])


def create_archive() -> dict[str, object]:
    prices = download_adjusted_prices()
    return archive_prices(prices)


if __name__ == "__main__":
    result = create_archive()
    print(json.dumps(result, indent=2))
