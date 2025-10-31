"""Intent planning schemas."""
from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel

from adapters.api.schemas.state import EngineStateModel


class IntentModel(BaseModel):
    type: str
    payload: Mapping[str, Any]


class PlanResponse(BaseModel):
    state: EngineStateModel
    intents: list[IntentModel]
