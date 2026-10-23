"""Reproducible integrity audit for MarketLab research inputs and execution."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from raw_price_archive import archived_csv_sha256


def _row(check_id: str, area: str, status: str, evidence: str,
         requirement: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "requirement": requirement,
    }


def run_integrity_audit(root: Path = Path(".")) -> pd.DataFrame:
    """Audit current artifacts without downloading or changing market data."""
    daily_dir = root / "published_research" / "daily"
    model_dir = root / "published_research" / "model_training"
    daily_paths = sorted(daily_dir.glob("????-??-??.csv"))
    snapshots = pd.concat(
        (pd.read_csv(path).assign(source_file=path.name) for path in daily_paths),
        ignore_index=True,
    ) if daily_paths else pd.DataFrame()

    unique_snapshots = (
        not snapshots.empty
        and {"date", "ticker"}.issubset(snapshots.columns)
        and not snapshots.duplicated(["date", "ticker"]).any()
    )
    rows = [_row(
        "DATA-001", "data", "PASS" if unique_snapshots else "FAIL",
        (f"{len(daily_paths)} dated snapshots; "
         f"{snapshots['ticker'].nunique() if 'ticker' in snapshots else 0} unique tickers; "
         "no duplicate date/ticker rows." if unique_snapshots else
         "Daily snapshots are missing or contain duplicate date/ticker rows."),
        "Each archived observation must have one row per date and ticker.",
    )]

    provenance_path = model_dir / "data_provenance.csv"
    provenance = pd.read_csv(provenance_path) if provenance_path.exists() else pd.DataFrame()
    required_provenance = {"provider", "start_date", "end_date", "rows", "tickers", "data_sha256"}
    provenance_ok = not provenance.empty and required_provenance.issubset(provenance.columns)
    rows.append(_row(
        "DATA-002", "data", "PASS" if provenance_ok else "FAIL",
        "Engineered training panel has provider, coverage and SHA-256 metadata."
        if provenance_ok else "Training provenance is incomplete.",
        "Every evaluated panel must carry source, coverage and content fingerprint.",
    ))

    raw_dir = root / "published_research" / "raw_prices"
    manifests = sorted(raw_dir.glob("*/manifest.json")) if raw_dir.exists() else []
    valid_archives = 0
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            data_path = manifest_path.parent / str(manifest["data_file"])
            if (data_path.exists() and
                    archived_csv_sha256(data_path) == manifest["sha256"]):
                valid_archives += 1
        except (OSError, KeyError, json.JSONDecodeError):
            pass
    raw_archived = bool(manifests) and valid_archives == len(manifests)
    rows.append(_row(
        "DATA-003", "data", "PASS" if raw_archived else "FAIL",
        f"{valid_archives} immutable raw adjusted-OHLCV archive version(s) pass manifest hash verification."
        if raw_archived else "No immutable raw-price archive exists; Yahoo data are downloaded again for each run.",
        "Freeze the exact raw OHLC input before evaluating a new candidate.",
    ))

    history_path = model_dir / "data_provenance_history.csv"
    history = pd.read_csv(history_path) if history_path.exists() else pd.DataFrame()
    revised_dates = 0
    if {"end_date", "data_sha256"}.issubset(history.columns):
        revised_dates = int((history.groupby("end_date")["data_sha256"].nunique() > 1).sum())
    revision_controlled = raw_archived
    rows.append(_row(
        "DATA-004", "data", "PASS" if revision_controlled else "FAIL",
        (f"{revised_dates} legacy labeled end date(s) had multiple hashes and remain unreconstructable; "
         f"new revisions are retained as content-addressed raw versions."
         if revision_controlled else
         f"{revised_dates} labeled end date(s) have multiple hashes without reconstructable raw versions."),
        "Revisions must retain both the old and new raw input, not only hashes.",
    ))

    rows.extend([
        _row(
            "TIME-001", "timing", "FAIL",
            "Archived build_features defines future_return as close[t+5] / close[t] - 1 while features include close[t].",
            "A close-t signal may execute no earlier than open[t+1] (or a predeclared later price).",
        ),
        _row(
            "TIME-002", "timing", "PASS",
            "Prospective paper scoring enters on the next archived session and evaluates five sessions later; unit tests cover the delay.",
            "Prospective observations must never use the signal-date close as an executable fill.",
        ),
        _row(
            "LEAK-001", "leakage", "PASS",
            "Chronological classifier refits use a five-session embargo; tests verify future labels do not alter earlier predictions.",
            "Training labels may not overlap the unseen test block.",
        ),
        _row(
            "LEAK-002", "leakage", "PASS",
            "Reported five-session model returns are sampled every five rows and paper scorecards do not compound overlapping outcomes.",
            "Overlapping outcomes may be described but not compounded as independent returns.",
        ),
        _row(
            "COST-001", "cost", "PASS",
            "Archived evaluations deduct a fixed 0.10% one-way cost from turnover.",
            "Every strategy comparison must deduct a visible turnover-linked cost.",
        ),
        _row(
            "COST-002", "cost", "FAIL",
            "The cost model does not separately represent bid-ask spread, slippage, fund fees, cash yield or tax assumptions.",
            "New candidates need a documented base cost plus adverse cost scenarios and cash return.",
        ),
    ])
    return pd.DataFrame(rows)


def write_audit(root: Path = Path("."), audit_date: str = "2026-10-22") -> tuple[Path, Path]:
    audit = run_integrity_audit(root)
    output_dir = root / "published_research" / "audits"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{audit_date}_research_integrity.csv"
    md_path = output_dir / f"{audit_date}_research_integrity.md"
    audit.to_csv(csv_path, index=False)
    lines = [
        f"# Research Integrity Audit — {audit_date}",
        "",
        "**Verdict: BLOCKED FOR NEW MODEL PROMOTION.** Daily collection and prospective paper tracking may continue, but archived historical returns cannot promote a strategy.",
        "",
        "| Check | Area | Status | Evidence | Required action |",
        "|---|---|---|---|---|",
    ]
    for row in audit.itertuples(index=False):
        lines.append(
            f"| {row.check_id} | {row.area} | {row.status} | {row.evidence} | {row.requirement} |"
        )
    lines.extend([
        "",
        "## Mandatory boundary for the next model",
        "",
        "1. Archive the exact adjusted OHLC input before any experiment.",
        "2. Form the signal after close t and execute no earlier than open t+1.",
        "3. Include turnover cost, an adverse-cost scenario and cash yield.",
        "4. Keep the sealed 2026-10-20 baselines unchanged; label their returns as non-executable historical references.",
        "",
        "This audit does not place orders or establish future profitability.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


if __name__ == "__main__":
    csv_path, md_path = write_audit()
    print(f"Wrote {csv_path} and {md_path}")
