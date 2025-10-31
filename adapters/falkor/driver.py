"""Connection helpers for FalkorDB access."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class FalkorSettings:
    """Minimal connection settings for FalkorDB clients."""

    host: str = "localhost"
    port: int = 6379
    graph_name_factory: Callable[[str], str] | None = None

    def graph_name_for(self, entity_id: str) -> str:
        if self.graph_name_factory is not None:
            return self.graph_name_factory(entity_id)
        return f"citizen::{entity_id}"


class FalkorDriver:
    """Lightweight driver that proxies calls to the legacy Falkor adapter."""

    def __init__(self, adapter: Any, settings: FalkorSettings | None = None) -> None:
        self._adapter = adapter
        self._settings = settings or FalkorSettings()

    @property
    def settings(self) -> FalkorSettings:
        return self._settings

    def load_graph(self, entity_id: str) -> Any:
        graph_name = self._settings.graph_name_for(entity_id)
        return self._adapter.load_graph(graph_name)

    def persist_node_scalars_bulk(self, rows: list[dict[str, Any]], *, namespace: str) -> Any:
        ctx = {"ns": namespace}
        return self._adapter.persist_node_scalars_bulk(rows, ctx=ctx)
