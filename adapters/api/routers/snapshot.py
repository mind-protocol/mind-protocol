"""Snapshot router exposing pure engine state."""
from __future__ import annotations

from fastapi import APIRouter

from adapters.api.routers.shared import resolve_engine_facade, to_state_model
from adapters.api.schemas.snapshot import SnapshotResponse


router = APIRouter(prefix="/snapshot", tags=["snapshot"])


@router.get("/{citizen_id}", response_model=SnapshotResponse)
def snapshot(citizen_id: str) -> SnapshotResponse:
    engine = resolve_engine_facade(citizen_id)
    state = engine.snapshot()
    return SnapshotResponse(state=to_state_model(state))
