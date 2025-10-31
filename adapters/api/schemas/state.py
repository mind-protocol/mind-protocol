"""Pydantic models mirroring the engine state dataclasses."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NodeActivationModel(BaseModel):
    node_id: str
    energy: float
    normalized_energy: float
    active: bool


class EngineStateModel(BaseModel):
    entity_id: str
    tick: int
    tick_interval_ms: float
    total_nodes: int
    active_nodes: int
    global_energy: float
    normalized_energy: float
    last_tick_time: datetime
    observed_at: datetime
    branching_ratio: float | None
    nodes: list[NodeActivationModel]
