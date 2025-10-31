from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
import sys
from pathlib import Path

import pytest

try:  # FastAPI may not be available in minimal environments
    from fastapi.testclient import TestClient
except ModuleNotFoundError:  # pragma: no cover - test dependency guard
    pytest.skip("fastapi not installed", allow_module_level=True)

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from adapters.api.app import create_app
from orchestration.adapters.storage.engine_registry import (
    clear_registry,
    register_engine,
)


class _Node:
    def __init__(self, node_id: str, energy: float, theta: float = 0.0) -> None:
        self.id = node_id
        self.E = energy
        self.theta = theta

    def is_active(self) -> bool:
        return self.E >= self.theta


class _Graph:
    def __init__(self, *nodes: _Node) -> None:
        self.nodes = {node.id: node for node in nodes}

    def get_node(self, node_id: str) -> _Node | None:
        return self.nodes.get(node_id)


class _BranchingTracker:
    def __init__(self) -> None:
        self.calls = 0

    def measure_cycle(self, *_args, **_kwargs):
        self.calls += 1
        return {"branching_ratio": 0.5}


class _GraphPortProbe:
    def __init__(self) -> None:
        self.persist_calls: list[tuple[str, tuple[dict, ...]]] = []

    def persist(self, entity_id: str, intents):
        self.persist_calls.append((entity_id, tuple(intents)))


def _make_engine(entity_id: str, graph_port: _GraphPortProbe | None = None):
    graph = _Graph(_Node("n-high", 90.0, theta=10.0), _Node("n-low", 40.0, theta=30.0))
    config = SimpleNamespace(entity_id=entity_id, tick_interval_ms=100.0, max_energy=100.0, telemetry_event="engine.tick")
    legacy = SimpleNamespace(
        graph=graph,
        tick_count=1,
        last_tick_time=datetime(2025, 1, 1, 12, 0, 0),
        config=config,
        branching_tracker=_BranchingTracker(),
        tick_multiplier=1.0,
    )
    if graph_port is not None:
        legacy._graph_port = graph_port
    return legacy


@pytest.fixture(autouse=True)
def _reset_registry():
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def client():
    port = _GraphPortProbe()
    engine = _make_engine("citizen-api", graph_port=port)
    register_engine("citizen-api", engine)
    app = create_app()
    client = TestClient(app)
    client.graph_port = port  # type: ignore[attr-defined]
    client.engine = engine  # type: ignore[attr-defined]
    return client


def test_snapshot_endpoint_returns_state(client: TestClient):
    response = client.get("/snapshot/citizen-api")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["entity_id"] == "citizen-api"


def test_plan_endpoint_returns_intents(client: TestClient):
    response = client.post("/tasks/citizen-api/plan")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["intents"], list)


def test_dispatch_endpoint_uses_graph_port(client: TestClient):
    response = client.post("/tasks/citizen-api/dispatch")
    assert response.status_code == 200
    port = client.graph_port  # type: ignore[attr-defined]
    assert port.persist_calls
