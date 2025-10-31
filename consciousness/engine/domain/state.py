"""Pure state transitions for the consciousness engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Optional, Protocol, Tuple


class SupportsEngineConfig(Protocol):
    """Minimal protocol describing the configuration needed by the state builder."""

    entity_id: str
    tick_interval_ms: float
    max_energy: float


@dataclass(frozen=True)
class NodeActivation:
    """A lightweight projection of a node's activation state."""

    node_id: str
    energy: float
    normalized_energy: float
    active: bool


@dataclass(frozen=True)
class EngineState:
    """Immutable view of the engine suitable for pure reasoning."""

    entity_id: str
    tick: int
    tick_interval_ms: float
    total_nodes: int
    active_nodes: int
    global_energy: float
    normalized_energy: float
    last_tick_time: datetime
    observed_at: datetime
    branching_ratio: Optional[float]
    nodes: Tuple[NodeActivation, ...]


def build_engine_state(
    *,
    graph: Any,
    tick_count: int,
    last_tick_time: datetime,
    observed_at: datetime,
    config: SupportsEngineConfig,
    branching_state: Optional[Mapping[str, Any]] = None,
) -> EngineState:
    """Construct a pure engine state snapshot from graph-like inputs."""

    nodes = getattr(graph, "nodes", {})
    node_values: Iterable[Any] = nodes.values() if hasattr(nodes, "values") else []

    projected_nodes = []
    total_energy = 0.0
    max_energy = max(config.max_energy, 1.0)

    for raw_node in node_values:
        node_id = getattr(raw_node, "id", "<unknown>")
        energy_raw = float(getattr(raw_node, "E", 0.0))
        energy = max(0.0, min(max_energy, energy_raw))
        normalized = energy / max_energy
        is_active_callable = getattr(raw_node, "is_active", None)
        if callable(is_active_callable):
            active = bool(is_active_callable())
        else:
            active = energy > 0.0
        projected_nodes.append(
            NodeActivation(
                node_id=node_id,
                energy=energy,
                normalized_energy=normalized,
                active=active,
            )
        )
        total_energy += energy

    total_nodes = len(projected_nodes)
    active_nodes = sum(1 for node in projected_nodes if node.active)
    average_energy = total_energy / max(total_nodes, 1)
    normalized_average = max(0.0, min(1.0, average_energy / max_energy))

    branching_ratio = None
    if branching_state:
        maybe_ratio = branching_state.get("branching_ratio")
        if maybe_ratio is not None:
            branching_ratio = float(maybe_ratio)

    return EngineState(
        entity_id=config.entity_id,
        tick=tick_count,
        tick_interval_ms=float(config.tick_interval_ms),
        total_nodes=total_nodes,
        active_nodes=active_nodes,
        global_energy=average_energy,
        normalized_energy=normalized_average,
        last_tick_time=last_tick_time,
        observed_at=observed_at,
        branching_ratio=branching_ratio,
        nodes=tuple(projected_nodes),
    )
