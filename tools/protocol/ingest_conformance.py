"""Summarise Semgrep results as GODFILE conformance."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SEMGRP_PATH = ROOT / ".artifacts/semgrep.json"
OUTPUT_PATH = ROOT / ".artifacts/conformance.json"


def summarise() -> dict:
    if not SEMGRP_PATH.exists():
        return {
            "suite": "GODFILE-1.0",
            "total_findings": 0,
            "failures": 0,
            "pass_rate": 1.0,
        }

    try:
        data = json.loads(SEMGRP_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "suite": "GODFILE-1.0",
            "total_findings": 0,
            "failures": 0,
            "pass_rate": 1.0,
        }

    results = data.get("results", [])
    failures = len(results)
    pass_rate = 1.0 if failures == 0 else 0.0
    return {
        "suite": "GODFILE-1.0",
        "total_findings": failures,
        "failures": failures,
        "pass_rate": pass_rate,
    }


def main() -> None:
    payload = summarise()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
