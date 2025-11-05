"""Graph port adapter backed by the legacy Falkor utilities."""
from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Sequence

from adapters.falkor.driver import FalkorDriver, FalkorSettings
from consciousness.engine import GraphPort
from libs.law import implements

logger = logging.getLogger(__name__)

# Graph intent type constants
GRAPH_UPSERT_TYPE = "graph.upsert"


@implements("Mechanism:GRAPH_PORT", "Suite:GODFILE-1.0/A3")
class FalkorGraph(GraphPort):
    """Adapter that understands graph intents and forwards them to Falkor."""

    def __init__(
        self,
        legacy_adapter: Any,
        *,
        settings: FalkorSettings | None = None,
    ) -> None:
        self._driver = FalkorDriver(legacy_adapter, settings=settings)

    def load(self, entity_id: str) -> Any:
        return self._driver.load_graph(entity_id)

    @implements("Mechanism:GRAPH_PORT_UPSERT", "Suite:GODFILE-1.0/A3")
    def persist(self, entity_id: str, intents: Sequence[Mapping[str, Any]]) -> None:
        upserts = list(_iter_upsert_payloads(intents))
        if not upserts:
            return

        # Get the actual graph name from the driver (e.g., "mind-protocol_felix" not just "felix")
        graph_name = self._driver.settings.graph_name_for(entity_id)

        for payload in upserts:
            rows = payload.get("rows") or payload.get("nodes")
            if not rows:
                logger.debug("Skipping graph intent with no rows: %s", payload)
                continue

            # Use graph_name for namespace to match WriteGate expectations
            namespace = payload.get("namespace") or f"L1:{graph_name}"
            try:
                self._driver.persist_node_scalars_bulk(list(rows), namespace=namespace)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Falkor graph persist failed", extra={"entity_id": entity_id, "graph_name": graph_name})


def _iter_upsert_payloads(intents: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for intent in intents:
        if intent.get("type") != GRAPH_UPSERT_TYPE:
            continue
        payload = intent.get("payload")
        if isinstance(payload, Mapping):
            yield payload
