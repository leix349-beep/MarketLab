from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent / "research_records"
EXPERIMENTS = ROOT / "experiments.csv"

def save_experiment(symbol, years, params, metrics):
    ROOT.mkdir(exist_ok=True)
    exists = EXPERIMENTS.exists()
    row = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "symbol": symbol, "history_years": years,
        **params, **metrics,
        "status": "completed", "observation": "", "next_step": "",
    }
    if exists:
        with EXPERIMENTS.open("r", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if rows:
            last = rows[-1]
            same = all(str(last.get(k, "")) == str(v) for k, v in row.items()
                       if k not in {"timestamp", "observation", "next_step"})
            try:
                last_time = datetime.fromisoformat(last["timestamp"])
                seconds = (datetime.now().astimezone() - last_time).total_seconds()
            except (ValueError, KeyError):
                seconds = 999
            if same and seconds < 30:
                return False
    with EXPERIMENTS.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not exists: writer.writeheader()
        writer.writerow(row)
    return True

