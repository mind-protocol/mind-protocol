"""Render a static health report based on offline QA artifacts."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / ".artifacts"
REPORT_PATH = ROOT / "docs/health/INDEX.md"


@dataclass
class RiskRow:
    file: str
    risk_score: float
    loc: int
    cc_max: float
    coverage_pct: float | None
    reachable: str


def load_triage_rows(limit: int = 20) -> List[RiskRow]:
    path = ARTIFACTS / "usage_triage.csv"
    if not path.exists():
        return []

    rows: List[RiskRow] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            try:
                risk = float(raw.get("risk_score", 0.0))
            except (TypeError, ValueError):
                risk = 0.0
            try:
                loc = int(float(raw.get("loc", 0)))
            except (TypeError, ValueError):
                loc = 0
            try:
                cc_max = float(raw.get("cc_max", 0.0))
            except (TypeError, ValueError):
                cc_max = 0.0
            try:
                coverage = raw.get("coverage_pct")
                coverage_val = float(coverage) if coverage not in (None, "") else None
            except (TypeError, ValueError):
                coverage_val = None

            rows.append(
                RiskRow(
                    file=raw.get("file", "<unknown>"),
                    risk_score=round(risk, 3),
                    loc=loc,
                    cc_max=cc_max,
                    coverage_pct=coverage_val,
                    reachable=str(raw.get("reachable", "no")),
                )
            )

    rows.sort(key=lambda row: row.risk_score, reverse=True)
    return rows[:limit]


def load_unreachable(rows: Iterable[RiskRow]) -> List[str]:
    return [row.file for row in rows if row.reachable.lower() != "yes"]


def load_semgrep_hits(limit: int = 10) -> List[tuple[str, str, int]]:
    path = ARTIFACTS / "semgrep.json"
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    hits: List[tuple[str, str, int]] = []
    for result in data.get("results", []):
        check_id = result.get("check_id", "")
        file_path = result.get("path", "")
        start = (result.get("start", {}) or {}).get("line", 0)
        if check_id and file_path:
            hits.append((file_path, check_id, int(start)))

    hits.sort(key=lambda item: item[1])
    return hits[:limit]


def load_unreachable_from_import_graph() -> List[str]:
    path = ARTIFACTS / "import_graph_output.json"
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    unreachable = data.get("unreachable", [])
    if isinstance(unreachable, list):
        return sorted(set(unreachable))
    return []


def render_report() -> str:
    risk_rows = load_triage_rows()
    unreachable_from_triage = load_unreachable(risk_rows)
    unreachable_from_graph = load_unreachable_from_import_graph()
    semgrep_hits = load_semgrep_hits()

    lines = ["# Repository Health Report", ""]
    lines.append("## Top Risk Files")
    if risk_rows:
        lines.append("| File | Risk Score | LOC | CC Max | Coverage | Reachable |")
        lines.append("| --- | ---: | ---: | ---: | --- | --- |")
        for row in risk_rows:
            coverage_display = f"{row.coverage_pct:.1f}%" if row.coverage_pct is not None else "n/a"
            lines.append(
                f"| {row.file} | {row.risk_score:.3f} | {row.loc} | {row.cc_max:.1f} | {coverage_display} | {row.reachable} |"
            )
    else:
        lines.append("No triage data available. Run `make usage-scan`.")

    lines.append("")
    lines.append("## Unreachable Modules")
    merged_unreachable = sorted(set(unreachable_from_triage + unreachable_from_graph))
    if merged_unreachable:
        for path in merged_unreachable:
            lines.append(f"- {path}")
    else:
        lines.append("- No unreachable modules detected")

    lines.append("")
    lines.append("## Semgrep God-File Alerts")
    if semgrep_hits:
        for file_path, check_id, line in semgrep_hits:
            lines.append(f"- `{check_id}` at `{file_path}:{line}`")
    else:
        lines.append("- No Semgrep results captured")

    return "\n".join(lines) + "\n"


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(), encoding="utf-8")


if __name__ == "__main__":
    main()
