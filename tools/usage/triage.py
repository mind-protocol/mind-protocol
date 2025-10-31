"""Merge evidence artifacts into a triage CSV.

The resulting `.artifacts/usage_triage.csv` file is a single table capturing
risk, coverage, reachability, and rule hits.  We intentionally tolerate missing
inputs so the pipeline can run early in the refactor even if some tools are not
available yet.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".artifacts"
TRIAGE_PATH = ARTIFACTS / "usage_triage.csv"


def _normalize(path: str) -> str:
    candidate = Path(path)
    try:
        relative = candidate.resolve(strict=False).relative_to(ROOT)
    except Exception:
        try:
            relative = Path(path).relative_to(ROOT)
        except Exception:
            relative = Path(path)
    return relative.as_posix()


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _load_complexity() -> List[dict]:
    data = _load_json(ARTIFACTS / "complexity.json") or {}
    return data.get("results", [])


def _load_coverage() -> Dict[str, float]:
    data = _load_json(ARTIFACTS / "coverage.json") or {}
    files = data.get("files", {})
    coverage: Dict[str, float] = {}
    for path, payload in files.items():
        summary = payload.get("summary", {})
        percent = summary.get("percent_covered")
        if percent is None:
            continue
        coverage[_normalize(path)] = float(percent)
    return coverage


def _load_churn() -> Dict[str, int]:
    churn_file = ARTIFACTS / "churn_180d.txt"
    churn: Dict[str, int] = {}
    if not churn_file.exists():
        return churn
    for line in churn_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        try:
            count = int(parts[0])
        except ValueError:
            continue
        churn[_normalize(parts[1])] = count
    return churn


def _load_semgrep_hits() -> Dict[str, List[str]]:
    data = _load_json(ARTIFACTS / "semgrep.json") or {}
    hits: Dict[str, List[str]] = defaultdict(list)
    for result in data.get("results", []):
        path = result.get("path")
        severity = (result.get("extra", {}) or {}).get("severity", "")
        if not path:
            continue
        hits[_normalize(path)].append(severity.upper() or "UNKNOWN")
    return hits


def _load_reachable() -> Dict[str, bool]:
    data = _load_json(ARTIFACTS / "import_graph_output.json") or {}
    reachable_sets: Iterable[List[str]] = data.get("reachable", {}).values()
    reachable: Dict[str, bool] = defaultdict(lambda: False)
    for collection in reachable_sets:
        for path in collection:
            reachable[_normalize(path)] = True
    return reachable


def build_rows() -> List[dict]:
    complexity_rows = _load_complexity()
    coverage = _load_coverage()
    churn = _load_churn()
    semgrep = _load_semgrep_hits()
    reachable = _load_reachable()

    rows: List[dict] = []
    for entry in complexity_rows:
        file_path = _normalize(entry.get("file", ""))
        row = {
            "file": file_path,
            "risk_score": entry.get("risk_score", 0.0),
            "loc": entry.get("loc", 0),
            "cc_max": entry.get("cc_max", 0),
            "cc_avg": round(entry.get("cc_avg", 0), 2) if entry.get("cc_avg") is not None else "",
            "mi": entry.get("mi", 0),
            "fanin": entry.get("fanin", 0),
            "churn90": entry.get("churn90", 0),
            "churn180": churn.get(file_path, 0),
            "coverage_pct": coverage.get(file_path, ""),
            "reachable": "yes" if reachable.get(file_path) else "no",
            "semgrep_hits": len(semgrep.get(file_path, [])),
            "semgrep_severities": ";".join(sorted(set(semgrep.get(file_path, [])))),
        }
        rows.append(row)

    rows.sort(key=lambda r: r.get("risk_score", 0), reverse=True)
    return rows


def write_csv(rows: List[dict]) -> None:
    TRIAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "file",
        "risk_score",
        "loc",
        "cc_max",
        "cc_avg",
        "mi",
        "fanin",
        "churn90",
        "churn180",
        "coverage_pct",
        "reachable",
        "semgrep_hits",
        "semgrep_severities",
    ]
    with TRIAGE_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    rows = build_rows()
    write_csv(rows)
    message = f"Wrote {len(rows)} rows to {TRIAGE_PATH.as_posix()}"
    print(message)
    sys.exit(0)
