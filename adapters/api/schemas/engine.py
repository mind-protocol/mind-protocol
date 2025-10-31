"""Engine control schemas."""
from __future__ import annotations

from pydantic import BaseModel


class EngineListResponse(BaseModel):
    citizens: list[str]


class EngineControlResponse(BaseModel):
    status: str
    citizen_id: str | None = None
    tick_multiplier: float | None = None
    message: str | None = None


class EngineSpeedRequest(BaseModel):
    multiplier: float
