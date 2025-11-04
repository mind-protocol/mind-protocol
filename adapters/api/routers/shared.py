"""Shared helpers for API routers."""
from __future__ import annotations

from fastapi import HTTPException

from consciousness.engine import Engine, EngineConfig
from consciousness.engine.domain.state import EngineState, NodeActivation
from adapters.api.schemas.state import EngineStateModel, NodeActivationModel
from orchestration.adapters.storage.engine_registry import get_engine

# HTTP status codes
HTTP_NOT_FOUND = 404


def resolve_engine_facade(citizen_id: str) -> Engine:
    legacy_engine = get_engine(citizen_id)
    if legacy_engine is None:
        raise HTTPException(status_code=HTTP_NOT_FOUND, detail=f"Engine not found: {citizen_id}")

    graph_port = getattr(legacy_engine, "_graph_port", None)
    config = EngineConfig.from_legacy(getattr(legacy_engine, "config", None))
    return Engine(legacy_engine, config=config, graph_port=graph_port)


def to_state_model(state: EngineState) -> EngineStateModel:
    return EngineStateModel(
        entity_id=state.entity_id,
        tick=state.tick,
        tick_interval_ms=state.tick_interval_ms,
        total_nodes=state.total_nodes,
        active_nodes=state.active_nodes,
        global_energy=state.global_energy,
        normalized_energy=state.normalized_energy,
        last_tick_time=state.last_tick_time,
        observed_at=state.observed_at,
        branching_ratio=state.branching_ratio,
        nodes=[_to_node_model(node) for node in state.nodes],
    )


def _to_node_model(node: NodeActivation) -> NodeActivationModel:
    return NodeActivationModel(
        node_id=node.node_id,
        energy=node.energy,
        normalized_energy=node.normalized_energy,
        active=node.active,
    )
