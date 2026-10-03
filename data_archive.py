from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent / "research_records"

def _stamp():
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")

def archive_market_data(df: pd.DataFrame, symbol: str, metadata: dict) -> dict:
    folder = ROOT / "raw_data" / datetime.now().astimezone().strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{_stamp()}_{symbol}"
    csv_path = folder / f"{stem}.csv"
    manifest_path = folder / f"{stem}.json"
    df.to_csv(csv_path)
    digest = sha256(csv_path.read_bytes()).hexdigest()
    manifest = {
        "snapshot_id": stem, "symbol": symbol,
        "retrieved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "rows": len(df), "first_date": str(df.index.min()), "last_date": str(df.index.max()),
        "sha256": digest, "data_file": str(csv_path.relative_to(ROOT)), **metadata,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest

def archive_experiment(symbol: str, snapshot: dict, parameters: dict, metrics: dict) -> Path:
    folder = ROOT / "experiment_manifests"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{_stamp()}_{symbol}.json"
    record = {
        "experiment_id": path.stem,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "strategy_version": "daily-ma-rsi-next-open-v1",
        "data_snapshot_id": snapshot["snapshot_id"],
        "parameters": parameters, "metrics": metrics,
        "status": "completed", "observation": "", "limitations": [
            "Historical backtest", "No walk-forward validation yet", "Simplified execution model"
        ],
    }
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def archive_sector_snapshot(df: pd.DataFrame, period: str) -> Path:
    folder = ROOT / "sector_snapshots"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{_stamp()}_sector_{period}.csv"
    df.to_csv(path, index=False)
    return path

def archive_parameter_experiment(df: pd.DataFrame, symbol: str) -> Path:
    folder = ROOT / "parameter_experiments"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{_stamp()}_{symbol}_grid.csv"
    df.to_csv(path, index=False)
    return path

def archive_daily_report(report: str, symbol: str, language: str) -> Path:
    folder = ROOT / "daily_reports"
    folder.mkdir(parents=True, exist_ok=True)
    day = datetime.now().astimezone().strftime("%Y-%m-%d")
    path = folder / f"{day}_{symbol}_{language}.md"
    path.write_text(report, encoding="utf-8")
    return path

