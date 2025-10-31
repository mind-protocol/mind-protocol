"""Engine control router."""
from __future__ import annotations

from fastapi import APIRouter

from adapters.api.schemas.engine import (
    EngineControlResponse,
    EngineListResponse,
    EngineSpeedRequest,
)
from orchestration.adapters.storage.engine_registry import (
    all_citizens,
    pause_citizen,
    resume_citizen,
    set_citizen_speed,
)


router = APIRouter(prefix="/engine", tags=["engine"])


@router.get("/", response_model=EngineListResponse)
def list_engines() -> EngineListResponse:
    return EngineListResponse(citizens=sorted(all_citizens()))


@router.post("/{citizen_id}/pause", response_model=EngineControlResponse)
def pause_engine(citizen_id: str) -> EngineControlResponse:
    return EngineControlResponse(**pause_citizen(citizen_id))


@router.post("/{citizen_id}/resume", response_model=EngineControlResponse)
def resume_engine(citizen_id: str) -> EngineControlResponse:
    return EngineControlResponse(**resume_citizen(citizen_id))


@router.post("/{citizen_id}/speed", response_model=EngineControlResponse)
def set_engine_speed(citizen_id: str, request: EngineSpeedRequest) -> EngineControlResponse:
    return EngineControlResponse(**set_citizen_speed(citizen_id, request.multiplier))
