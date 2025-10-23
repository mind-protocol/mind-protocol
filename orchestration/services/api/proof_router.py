from __future__ import annotations

import asyncio
import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from orchestration.scripts.proof_runner import ProofReport, run_proof

router = APIRouter(prefix="/v1/proof", tags=["proof"])

_active_results: Dict[str, Dict[str, Any]] = {}
_active_tasks: Dict[str, asyncio.Task] = {}


class ProofRunRequest(BaseModel):
    stimulus: str = Field(..., min_length=3)
    duration_s: int = Field(60, ge=5, le=600)


async def _execute_proof(run_id: str, stimulus: str, duration_s: int) -> None:
    try:
        report: ProofReport = await run_proof(stimulus, duration_s, run_id=run_id)
        _active_results[run_id] = report.to_dict()
    except Exception as exc:  # pragma: no cover - defensive guard for runtime issues
        _active_results[run_id] = {
            "run_id": run_id,
            "verdict": "error",
            "error": str(exc),
        }
    finally:
        _active_tasks.pop(run_id, None)


@router.post("/run")
async def start_proof(request: ProofRunRequest):
    timestamp = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    run_suffix = f"{int(time.time() * 1000) % 10000:04d}"
    run_id = f"{timestamp}-{run_suffix}"

    if run_id in _active_tasks:
        raise HTTPException(status_code=409, detail="Proof run already active")

    task = asyncio.create_task(
        _execute_proof(run_id, request.stimulus, request.duration_s)
    )
    _active_tasks[run_id] = task

    return {"run_id": run_id, "status": "running"}


@router.get("/list")
async def list_proofs():
    run_ids = set(_active_results.keys()) | set(_active_tasks.keys())
    return [
        {
            "run_id": run_id,
            "status": "running" if run_id in _active_tasks else "completed",
            "verdict": _active_results.get(run_id, {}).get("verdict"),
        }
        for run_id in sorted(run_ids)
    ]


@router.get("/report/{run_id}")
async def get_report(run_id: str):
    if run_id in _active_tasks:
        return {"run_id": run_id, "status": "running"}

    report = _active_results.get(run_id)
    if not report:
        raise HTTPException(status_code=404, detail="Proof run not found")
    return report
