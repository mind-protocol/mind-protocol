from __future__ import annotations

import asyncio
import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

PROOF_API_BASE = os.getenv("PROOF_API_BASE", "http://localhost:8788")
PROOF_WS_URL = os.getenv("PROOF_WS_URL", "ws://localhost:8000/api/ws")
PROOF_CAPTURE_SECONDS = int(os.getenv("PROOF_CAPTURE_SECONDS", "60"))
PROOF_RHO_BAND_LOW = float(os.getenv("PROOF_RHO_BAND_LOW", "0.8"))
PROOF_RHO_BAND_HIGH = float(os.getenv("PROOF_RHO_BAND_HIGH", "1.2"))
PROOF_OUTPUT_DIR = Path(
    os.getenv("PROOF_OUTPUT_DIR", Path(tempfile.gettempdir()) / "mp_proof")
)


@dataclass
class ProofReport:
    """Structured proof-of-work attestation."""

    claim: str
    run_id: str
    inputs: Dict[str, Any]
    evidence: Dict[str, Any]
    verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def sha256(path: Path) -> str:
    """Compute SHA256 for a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


async def capture_ws(duration_s: int, output_path: Path) -> None:
    """Capture raw WebSocket events for a fixed duration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    end_time = time.time() + duration_s

    async with websockets.connect(PROOF_WS_URL) as ws, output_path.open(
        "w", encoding="utf-8"
    ) as sink:
        while time.time() < end_time:
            timeout = min(1.0, max(0.0, end_time - time.time()))
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            except asyncio.TimeoutError:
                continue
            except ConnectionClosed:
                break
            sink.write(message.rstrip() + "\n")


def _percentile(values: List[float], percentile: float) -> Optional[float]:
    if not values:
        return None
    values_sorted = sorted(values)
    idx = int(round(percentile * (len(values_sorted) - 1)))
    idx = max(0, min(len(values_sorted) - 1, idx))
    return float(values_sorted[idx])


def _extract_number(entry: Dict[str, Any], *paths: List[str]) -> Optional[float]:
    for path in paths:
        value: Any = entry
        for key in path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                value = None
                break
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def summarize_events(jsonl_path: Path) -> Dict[str, Any]:
    frames = flips = strides = boundaries = 0
    rho_values: List[float] = []
    conservation_eps: List[float] = []
    frontier_ratios: List[float] = []
    weights_updated = 0
    learning_reasons: Dict[str, int] = {}

    example_stride: Optional[str] = None
    example_boundary: Optional[str] = None
    example_learning: Optional[str] = None

    if not jsonl_path.exists():
        return {
            "frames": 0,
            "node_flips": 0,
            "stride_exec": 0,
            "boundary_summaries": 0,
            "example_stride_exec": None,
            "example_boundary_summary": None,
            "rho_p50": None,
            "conservation_eps_p95": None,
            "frontier_ratio_p95": None,
            "learning_updates": 0,
            "learning_reasons": learning_reasons,
            "example_learning_update": None,
        }

    with jsonl_path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            event = payload
            if isinstance(payload, dict) and isinstance(payload.get("event"), dict):
                event = payload["event"]

            evt_type = str(event.get("type") or event.get("kind") or "").lower()

            if "tick_frame" in evt_type:
                frames += 1
                rho = _extract_number(event, ("rho",), ("metrics", "rho"))
                if rho is not None:
                    rho_values.append(rho)
                active_frontier = event.get("active_frontier") or event.get("frontier")
                if isinstance(active_frontier, dict):
                    nodes = int(active_frontier.get("nodes") or active_frontier.get("active") or 0)
                    shadow = int(active_frontier.get("shadow") or active_frontier.get("shadow_nodes") or 0)
                    total = active_frontier.get("total") or active_frontier.get("total_nodes")
                    try:
                        total_int = int(total) if total is not None else nodes + shadow
                    except (TypeError, ValueError):
                        total_int = nodes + shadow
                    denom = max(1, total_int)
                    frontier_ratios.append((nodes + shadow) / denom)
            elif "node.flip" in evt_type:
                flips += 1
            elif "stride.exec" in evt_type:
                strides += 1
                if example_stride is None:
                    example_stride = line[:240]
            elif "se.boundary.summary" in evt_type:
                boundaries += 1
                if example_boundary is None:
                    example_boundary = line[:240]
            elif evt_type.startswith("frame.end"):
                delta_e = _extract_number(event, ("deltaE_total",), ("delta_e_total",))
                if delta_e is not None:
                    conservation_eps.append(abs(delta_e))

            if evt_type.startswith("weights.updated"):
                weights_updated += 1
                reason = event.get("reason")
                if isinstance(reason, str) and reason:
                    learning_reasons[reason] = learning_reasons.get(reason, 0) + 1
                if example_learning is None:
                    example_learning = line[:240]

    return {
        "frames": frames,
        "node_flips": flips,
        "stride_exec": strides,
        "boundary_summaries": boundaries,
        "example_stride_exec": example_stride,
        "example_boundary_summary": example_boundary,
        "rho_p50": _percentile(rho_values, 0.5),
        "conservation_eps_p95": _percentile(conservation_eps, 0.95),
        "frontier_ratio_p95": _percentile(frontier_ratios, 0.95),
        "learning_updates": weights_updated,
        "learning_reasons": learning_reasons,
        "example_learning_update": example_learning,
    }


async def run_proof(
    stimulus: str,
    duration_s: Optional[int] = None,
    run_id: Optional[str] = None,
) -> ProofReport:
    """Execute a proof run and return the attestation report."""
    duration = duration_s or PROOF_CAPTURE_SECONDS

    if run_id is None:
        timestamp = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
        run_suffix = f"{int(time.time() * 1000) % 10000:04d}"
        run_id = f"{timestamp}-{run_suffix}"

    out_dir = PROOF_OUTPUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = out_dir / "events.jsonl"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Health checks
        try:
            health_resp = await client.get(f"{PROOF_API_BASE}/healthz")
            health_resp.raise_for_status()
            health = health_resp.json()
        except Exception as exc:
            health = {"status": "unknown", "error": str(exc)}

        try:
            selftest_resp = await client.get(
                f"{PROOF_API_BASE}/healthz", params={"selftest": 1}
            )
            selftest_resp.raise_for_status()
            selftests = selftest_resp.json()
        except Exception as exc:
            selftests = {"note": "selftests_not_available", "error": str(exc)}

        # Capture events while stimulus flows through the system
        capture_task = asyncio.create_task(capture_ws(duration, events_path))

        # Inject stimulus (best effort)
        try:
            await client.post(
                f"{PROOF_API_BASE}/v1/stimulus/inject",
                json={"text": stimulus, "source": "proof_runner"},
                timeout=5.0,
            )
        except Exception:
            # Injection is best-effort; absence shouldn't abort the proof run
            pass

        await capture_task

        # Dump API snapshot for auditability
        api_dump_path = out_dir / "proof_api.json"
        api_dump_path.write_text(
            json.dumps({"healthz": health, "selftests": selftests}, indent=2),
            encoding="utf-8",
        )

    events_summary = summarize_events(events_path)

    learning_info = {
        "updates": events_summary.get("learning_updates", 0),
        "reasons": events_summary.get("learning_reasons", {}),
        "example_update": events_summary.get("example_learning_update"),
    }

    fail_reasons: List[str] = []
    if events_summary.get("stride_exec", 0) <= 0:
        fail_reasons.append("no_stride_exec")
    if events_summary.get("boundary_summaries", 0) <= 0:
        fail_reasons.append("no_boundary_summaries")
    if events_summary.get("node_flips", 0) <= 0:
        fail_reasons.append("no_node_flips")

    conservation_eps_p95 = events_summary.get("conservation_eps_p95")
    if conservation_eps_p95 is not None and conservation_eps_p95 > 1e-3:
        fail_reasons.append("conservation_out_of_band")

    rho_p50 = events_summary.get("rho_p50")
    if rho_p50 is not None and not (PROOF_RHO_BAND_LOW <= rho_p50 <= PROOF_RHO_BAND_HIGH):
        fail_reasons.append("rho_out_of_band")

    frontier_ratio_p95 = events_summary.get("frontier_ratio_p95")
    if frontier_ratio_p95 is not None and frontier_ratio_p95 > 0.30:
        fail_reasons.append("frontier_ratio_out_of_band")

    if learning_info["updates"] <= 0:
        fail_reasons.append("no_learning_updates")

    verdict = "pass" if not fail_reasons else "fail"

    evidence = {
        "api_health": health,
        "selftests": selftests,
        "events": {
            key: value
            for key, value in events_summary.items()
            if key not in {"learning_updates", "learning_reasons", "example_learning_update"}
        },
        "learning": learning_info,
        "artifacts": {
            "ws_trace_path": str(events_path),
            "ws_trace_sha256": sha256(events_path),
            "api_dump_path": str(api_dump_path),
            "api_dump_sha256": sha256(api_dump_path),
        },
        "fail_reasons": fail_reasons,
    }

    report = ProofReport(
        claim="system verified",
        run_id=run_id,
        inputs={"stimulus": stimulus, "duration_s": duration},
        evidence=evidence,
        verdict=verdict,
    )

    attestation_path = out_dir / f"proof_{run_id}.json"
    attestation_path.write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )

    return report


if __name__ == "__main__":
    stimulus_text = os.getenv("PROOF_STIMULUS", "Boot check: reconstruct entity layer context")
    duration_override = os.getenv("PROOF_DURATION_SECONDS")
    duration_value = int(duration_override) if duration_override else None

    report = asyncio.run(run_proof(stimulus_text, duration_value))
    print(json.dumps(report.to_dict(), indent=2))
