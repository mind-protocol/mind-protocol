"""Snapshot responses for the engine API."""
from __future__ import annotations

from pydantic import BaseModel

from adapters.api.schemas.state import EngineStateModel


class SnapshotResponse(BaseModel):
    state: EngineStateModel
