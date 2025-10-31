from __future__ import annotations
from collections import deque
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from adapters.falkor import FalkorGraph


class _LegacyAdapter:
    def __init__(self) -> None:
        self.calls = deque()

    def persist_node_scalars_bulk(self, rows, ctx):
        self.calls.append((list(rows), ctx))
        return len(rows)

    def load_graph(self, graph_name):  # pragma: no cover - smoke path
        return {"graph": graph_name}


@pytest.fixture
def legacy_adapter():
    return _LegacyAdapter()


def test_falkor_graph_persist_filters_intents(legacy_adapter):
    graph = FalkorGraph(legacy_adapter)

    intents = (
        {"type": "telemetry.emit", "payload": {}},
        {
            "type": "graph.upsert",
            "payload": {"rows": [{"node_id": "n-1"}], "namespace": "L1:test"},
        },
    )

    graph.persist("citizen-test", intents)

    assert legacy_adapter.calls
    rows, ctx = legacy_adapter.calls[0]
    assert rows[0]["node_id"] == "n-1"
    assert ctx["ns"] == "L1:test"


def test_falkor_graph_persist_ignores_empty_rows(legacy_adapter):
    graph = FalkorGraph(legacy_adapter)

    graph.persist(
        "citizen-test",
        ({"type": "graph.upsert", "payload": {"rows": []}},),
    )

    assert not legacy_adapter.calls
