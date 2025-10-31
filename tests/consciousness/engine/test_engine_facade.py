from datetime import datetime
from types import SimpleNamespace
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from consciousness.engine import Engine, EngineConfig, GraphPort


class _TelemetryProbe:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def publish(self, event: str, payload: dict) -> None:
        self.events.append((event, payload))


class _BranchingTracker:
    def __init__(self, ratio: float) -> None:
        self._ratio = ratio
        self.calls = 0

    def measure_cycle(self, *_args, **_kwargs):
        self.calls += 1
        return {"branching_ratio": self._ratio}


class _FakeNode:
    def __init__(self, node_id: str, energy: float, theta: float = 0.0) -> None:
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


class _GraphPortProbe(GraphPort):
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[dict, ...]]] = []

    def load(self, entity_id: str):
        raise NotImplementedError

    def persist(self, entity_id: str, intents):
        self.calls.append((entity_id, tuple(intents)))


def _build_legacy_stub(graph, config):
    return SimpleNamespace(
        graph=graph,
        tick_count=2,
        last_tick_time=datetime(2025, 1, 1, 12, 0, 0),
        config=config,
        branching_tracker=_BranchingTracker(0.5),
    )


def test_engine_facade_snapshot_and_intents(graph_with_nodes):
    telemetry = _TelemetryProbe()
    config = EngineConfig(entity_id="citizen.snapshot", tick_interval_ms=100.0, max_energy=100.0)
    legacy = _build_legacy_stub(graph_with_nodes, config)

    engine = Engine(legacy, telemetry=telemetry, config=config)

    decision = engine.plan_tick(branching_state={"branching_ratio": 0.5})
    state = decision.state

    assert state.entity_id == "citizen.snapshot"
    assert decision.intents
    assert telemetry.events  # Telemetry emitted because normalized energy >= threshold
    assert telemetry.events[0][0] == "engine.alert.high_energy"
    assert telemetry.events[0][1]["entity_id"] == "citizen.snapshot"
    assert engine.last_decision is decision


def test_engine_facade_snapshot_branches_when_none(graph_with_nodes):
    config = EngineConfig(entity_id="citizen.snapshot", tick_interval_ms=100.0, max_energy=100.0)
    legacy = _build_legacy_stub(graph_with_nodes, config)

    engine = Engine(legacy, config=config)

    snapshot = engine.snapshot()

    assert snapshot.branching_ratio == 0.5
    assert engine.last_decision is None


def test_engine_dispatches_graph_intents(graph_with_nodes):
    graph_port = _GraphPortProbe()
    config = EngineConfig(entity_id="citizen.dispatch", tick_interval_ms=100.0, max_energy=100.0)
    legacy = _build_legacy_stub(graph_with_nodes, config)

    engine = Engine(legacy, config=config, graph_port=graph_port)

    intents = (
        {
            "type": "graph.upsert",
            "payload": {
                "rows": ({"node_id": "n-high", "E": 1.0},),
                "namespace": "L1:citizen.dispatch",
            },
        },
    )

    engine.dispatch_intents(intents)

    assert graph_port.calls
    entity_id, captured_intents = graph_port.calls[0]
    assert entity_id == "citizen.dispatch"
    assert captured_intents[0]["payload"]["rows"][0]["node_id"] == "n-high"


# --- Fixtures ---


def _make_graph():
    graph = _FakeGraph()
    node_high = _FakeNode("n-high", 95.0, theta=10.0)
    node_low = _FakeNode("n-low", 90.0, theta=50.0)
    graph.add_node(node_high)
    graph.add_node(node_low)
    return graph


@pytest.fixture
def graph_with_nodes():
    return _make_graph()
