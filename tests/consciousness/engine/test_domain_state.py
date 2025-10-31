from datetime import datetime, timedelta

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st  # type: ignore  # noqa: E402

from consciousness.engine import EngineConfig
from consciousness.engine.domain.state import build_engine_state
from consciousness.engine.services.scheduler import plan_next_tick


class _FakeNode:
    def __init__(self, node_id: str, energy: float, theta: float = 0.1) -> None:
        self.id = node_id
        self.E = energy
        self.theta = theta

    def is_active(self) -> bool:
        return self.E >= self.theta


class _FakeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, _FakeNode] = {}

    def add_node(self, node: _FakeNode) -> None:
        self.nodes[node.id] = node


def _make_node(node_id: str, energy: float, theta: float = 0.1) -> _FakeNode:
    return _FakeNode(node_id, energy, theta)


def test_build_engine_state_golden_snapshot():
    graph = _FakeGraph()
    node_a = _make_node("a", 90.0, theta=10.0)
    node_b = _make_node("b", 20.0, theta=30.0)
    graph.add_node(node_a)
    graph.add_node(node_b)

    config = EngineConfig(entity_id="citizen.test", tick_interval_ms=250.0, max_energy=100.0)
    observed_at = datetime(2025, 1, 1, 12, 0, 0)
    last_tick = observed_at - timedelta(milliseconds=250)
    branching_state = {"branching_ratio": 1.5}

    state = build_engine_state(
        graph=graph,
        tick_count=5,
        last_tick_time=last_tick,
        observed_at=observed_at,
        config=config,
        branching_state=branching_state,
    )

    assert state.entity_id == "citizen.test"
    assert state.tick == 5
    assert state.total_nodes == 2
    assert state.active_nodes == 1  # only node_a exceeds its theta
    assert state.global_energy == (90.0 + 20.0) / 2
    assert 0.0 <= state.normalized_energy <= 1.0
    assert state.branching_ratio == 1.5
    assert state.nodes[0].node_id == "a"
    assert state.nodes[0].normalized_energy == 0.9
    assert state.nodes[1].node_id == "b"
    assert state.nodes[1].active is False

    decision = plan_next_tick(state)
    assert decision.state is state
    assert decision.intents[0]["type"] == "telemetry.emit"
    assert decision.intents[0]["payload"]["data"]["normalized_energy"] == state.normalized_energy


@given(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=6))
def test_normalized_energy_clamped(node_energies):
    graph = _FakeGraph()
    for index, energy in enumerate(node_energies):
        graph.add_node(_make_node(f"n{index}", energy))

    config = EngineConfig(max_energy=100.0)
    observed_at = datetime.utcnow()

    state = build_engine_state(
        graph=graph,
        tick_count=1,
        last_tick_time=observed_at,
        observed_at=observed_at,
        config=config,
    )

    assert 0.0 <= state.normalized_energy <= 1.0
    for node in state.nodes:
        assert 0.0 <= node.normalized_energy <= 1.0
