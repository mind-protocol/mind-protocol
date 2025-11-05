"""
Streaming graph aggregator

Maintains an in-memory working set per citizen so WebSocket clients can render
live deltas without hitting FalkorDB or replay buffers. No persistence, no
replay—this is purely a RAM cache updated by the broadcast loop.

Author: Codex agent (2025-10-27)
"""

from __future__ import annotations

import asyncio
import copy
import logging
import time
from typing import Any, Dict, Optional

from orchestration.core.graph import Graph
from orchestration.core.link import Link
from orchestration.core.node import Node
from orchestration.core.subentity import Subentity

logger = logging.getLogger(__name__)


def _node_to_payload(node: Node) -> Dict[str, Any]:
    """Serialize a graph node into a lightweight payload suitable for transport."""
    return {
        "id": node.id,
        "name": node.name,
        "type": getattr(node.node_type, "value", str(node.node_type)),
        "energy": float(getattr(node, "E", 0.0)),
        "theta": float(getattr(node, "theta", 0.0)),
        "energy_runtime": float(getattr(node, "energy_runtime", 0.0)),
        "log_weight": float(getattr(node, "log_weight", 0.0)),
        "scope": getattr(node, "scope", "personal"),
        "properties": dict(getattr(node, "properties", {}) or {}),
    }


def _link_to_payload(link: Link) -> Dict[str, Any]:
    """Serialize a graph link into a lightweight payload."""
    return {
        "id": link.id,
        "source": link.source_id,
        "target": link.target_id,
        "type": getattr(link.link_type, "value", str(link.link_type)),
        "weight": float(getattr(link, "weight", 0.0)),
        "energy": float(getattr(link, "energy", 0.0)),
        "confidence": float(getattr(link, "confidence", 0.0)),
        "scope": getattr(link, "scope", "organizational"),
        "properties": dict(getattr(link, "properties", {}) or {}),
    }


def _subentity_to_payload(entity: Subentity) -> Dict[str, Any]:
    """Serialize a subentity into the transport payload."""
    return {
        "id": entity.id,
        "energy": float(getattr(entity, "energy_runtime", 0.0)),
        "threshold": float(getattr(entity, "threshold_runtime", 0.0)),
        "activation_level": getattr(entity, "activation_level_runtime", "absent"),
        "member_count": int(getattr(entity, "member_count", 0)),
        "quality": float(getattr(entity, "quality_score", 0.0)),
        "stability": getattr(entity, "stability_state", "candidate"),
    }


class GraphWorkingSet:
    """In-memory view of the current working set for a citizen."""

    def __init__(self, citizen_id: str):
        self.citizen_id = citizen_id

        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.links: Dict[str, Dict[str, Any]] = {}
        self.subentities: Dict[str, Dict[str, Any]] = {}

        self.cursor: int = 0
        self.last_event_ts: float = time.time()
        self.metadata: Dict[str, Any] = {}

    def reset(self) -> None:
        """Clear working set back to empty state."""
        self.nodes.clear()
        self.links.clear()
        self.subentities.clear()
        self.cursor = 0
        self.last_event_ts = time.time()
        self.metadata.clear()

    def record_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        ts: Optional[float] = None
    ) -> Dict[str, Any]:
        """Append event to log, update working set, and return the record."""
        ts = ts or time.time()
        self.cursor += 1
        record = {
            "cursor": self.cursor,
            "type": event_type,
            "payload": payload,
            "ts": ts,
            "citizen_id": payload.get("citizen_id", self.citizen_id)
        }
        self.last_event_ts = ts
        self._apply_event(event_type, payload)
        return record

    # ------------------------------------------------------------------ helpers

    def _ensure_node_entry(self, node_id: str) -> Dict[str, Any]:
        node = self.nodes.get(node_id)
        if node is None:
            node = {"id": node_id}
            self.nodes[node_id] = node
        return node

    def _ensure_link_entry(self, link_id: str) -> Dict[str, Any]:
        link = self.links.get(link_id)
        if link is None:
            link = {"id": link_id}
            self.links[link_id] = link
        return link

    def _ensure_subentity_entry(self, entity_id: str) -> Dict[str, Any]:
        entity = self.subentities.get(entity_id)
        if entity is None:
            entity = {"id": entity_id}
            self.subentities[entity_id] = entity
        return entity

    def _update_metadata(self, key: str, data: Dict[str, Any]) -> None:
        sanitized = dict(data)
        sanitized.pop("citizen_id", None)
        sanitized["_cursor"] = self.cursor
        sanitized["_ts"] = time.time()
        self.metadata[key] = sanitized

    def _apply_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Update local working set representation based on event contents."""
        if event_type == "graph.delta.node.upsert":
            node = payload.get("node") or {}
            node_id = node.get("id")
            if not node_id:
                node_id = payload.get("node_id")
                if node_id:
                    # Normalize into unified structure expected by callers
                    node = {
                        "id": node_id,
                        "type": payload.get("node_type"),
                        "properties": payload.get("properties"),
                    }
            if node_id:
                entry = self._ensure_node_entry(node_id)
                entry.update({k: v for k, v in node.items() if v is not None})
                entry["last_cursor"] = self.cursor
        elif event_type == "graph.delta.link.upsert":
            link = payload.get("link") or {}
            link_id = link.get("id")
            if not link_id:
                source = payload.get("source")
                target = payload.get("target")
                if source and target:
                    link_id = f"{source}->{target}"
                    link = {
                        "id": link_id,
                        "source": source,
                        "target": target,
                        "type": payload.get("type"),
                        "weight": payload.get("weight"),
                    }
            if link_id:
                entry = self._ensure_link_entry(link_id)
                entry.update({k: v for k, v in link.items() if v is not None})
                entry["last_cursor"] = self.cursor
        elif event_type == "graph.delta.node.delete":
            node_id = payload.get("node_id") or payload.get("id")
            if node_id and node_id in self.nodes:
                self.nodes.pop(node_id, None)
        elif event_type == "graph.delta.link.delete":
            link_id = payload.get("link_id") or payload.get("id")
            if link_id and link_id in self.links:
                self.links.pop(link_id, None)
        elif event_type == "graph.delta.subentity.upsert":
            entity = payload.get("subentity") or {}
            entity_id = entity.get("id")
            if entity_id:
                entry = self._ensure_subentity_entry(entity_id)
                entry.update(entity)
                entry["last_cursor"] = self.cursor
        elif event_type == "graph.delta.subentity.delete":
            entity_id = payload.get("subentity_id") or payload.get("id")
            if entity_id and entity_id in self.subentities:
                self.subentities.pop(entity_id, None)
        elif event_type == "node.flip":
            nodes = payload.get("nodes")
            if not nodes and payload.get("node"):
                nodes = [payload]
            if nodes:
                for entry in nodes:
                    node_id = entry.get("id") or entry.get("node") or entry.get("node_id")
                    if not node_id:
                        continue
                    node = self._ensure_node_entry(node_id)
                    energy = entry.get("E_post", entry.get("E"))
                    if energy is not None:
                        node["energy"] = energy
                    if "dE" in entry:
                        node["delta_energy"] = entry["dE"]
                    if "delta_E" in entry:
                        node["delta_energy"] = entry["delta_E"]
                    node["last_flip_frame"] = payload.get("frame_id")
                    node["last_cursor"] = self.cursor
        elif event_type == "link.flow.summary":
            flows = payload.get("flows") or payload.get("links") or []
            for summary in flows:
                link_id = summary.get("link_id") or summary.get("id")
                if not link_id:
                    continue
                link = self._ensure_link_entry(link_id)
                if "weight" in summary:
                    link["weight"] = summary["weight"]
                if "flow" in summary:
                    link["flow"] = summary["flow"]
                link["last_flow_frame"] = payload.get("frame_id")
                link["last_cursor"] = self.cursor
        elif event_type == "node.emotion.update":
            updates = payload.get("items", [])
            for entry in updates:
                node_id = entry.get("id")
                if not node_id:
                    continue
                node = self._ensure_node_entry(node_id)
                node["emotion_mag"] = entry.get("mag")
                node["emotion_axes"] = entry.get("top_axes")
                node["last_emotion_cursor"] = self.cursor
            if updates:
                self._update_metadata("node_emotion", {"updates": updates})
        elif event_type == "link.emotion.update":
            updates = payload.get("items", [])
            for entry in updates:
                link_id = entry.get("id")
                if not link_id:
                    continue
                link = self._ensure_link_entry(link_id)
                link["emotion_mag"] = entry.get("mag")
                link["emotion_axes"] = entry.get("top_axes")
                link["last_emotion_cursor"] = self.cursor
            if updates:
                self._update_metadata("link_emotion", {"updates": updates})
        elif event_type == "wm.emit":
            self._update_metadata("working_memory", {
                "frame_id": payload.get("frame_id"),
                "mode": payload.get("mode"),
                "selected_entities": payload.get("selected_entities", []),
                "entity_token_shares": payload.get("entity_token_shares", []),
                "total_entities": payload.get("total_entities"),
                "total_members": payload.get("total_members"),
                "token_budget_used": payload.get("token_budget_used"),
                "selected_nodes": payload.get("selected_nodes", [])
            })
            for node_id in payload.get("selected_nodes", []):
                node = self._ensure_node_entry(node_id)
                node["last_wm_frame"] = payload.get("frame_id")
                node["last_cursor"] = self.cursor
        elif event_type == "wm.selected":
            self._update_metadata("wm_selected", {
                "frame_id": payload.get("frame_id"),
                "entities_active": payload.get("entities_active", []),
                "timestamp_ms": payload.get("timestamp_ms")
            })
        elif event_type == "subentity.snapshot":
            self._update_metadata("subentity_snapshot", payload)
            for entry in payload.get("active", []):
                entity_id = entry.get("id")
                if not entity_id:
                    continue
                entity = self._ensure_subentity_entry(entity_id)
                entity["energy_norm"] = entry.get("energy")
                entity["theta_norm"] = entry.get("theta")
                entity["last_snapshot_frame"] = payload.get("frame_id")
                entity["is_active_snapshot"] = entry.get("energy", 0) >= entry.get("theta", 0)
                entity["last_cursor"] = self.cursor
        elif event_type == "subentity.lifecycle":
            entity_id = payload.get("entity_id")
            if entity_id:
                entity = self._ensure_subentity_entry(entity_id)
                entity["lifecycle_state"] = payload.get("new_state")
                if "quality_score" in payload:
                    entity["quality_score"] = payload.get("quality_score")
                entity["last_lifecycle_frame"] = payload.get("frame_id")
                entity["last_cursor"] = self.cursor
            self._update_metadata("subentity_lifecycle", payload)
        elif event_type == "subentity.flip":
            entity_id = payload.get("entity_id")
            if entity_id:
                entity = self._ensure_subentity_entry(entity_id)
                if "energy" in payload:
                    entity["energy"] = payload.get("energy")
                if "threshold" in payload:
                    entity["threshold"] = payload.get("threshold")
                entity["activation_level"] = payload.get("activation_level")
                entity["last_flip_frame"] = payload.get("frame_id")
                entity["last_cursor"] = self.cursor
        elif event_type == "criticality.state":
            self._update_metadata("criticality", payload)
        elif event_type == "coherence.metric":
            self._update_metadata("coherence", payload)
        elif event_type == "decay.tick":
            self._update_metadata("decay", payload)
        elif event_type == "entity.multiplicity_assessment":
            self._update_metadata("multiplicity_assessment", payload)
        elif event_type == "entity.productive_multiplicity":
            self._update_metadata("multiplicity_productive", payload)
        elif event_type == "tick_frame_v1":
            self._update_metadata("frame_overview", payload)
        elif event_type == "health.phenomenological":
            self._update_metadata("phenomenology", payload)
        elif event_type in {"weights.updated", "weights.updated.trace", "weights.updated.traversal"}:
            updates = payload.get("updates", [])
            for update in updates:
                item_id = update.get("item_id")
                if not item_id:
                    continue
                item_type = update.get("type", "node")
                if item_type == "link":
                    link = self._ensure_link_entry(item_id)
                    if "log_weight_after" in update:
                        link["log_weight"] = update["log_weight_after"]
                    if "log_weight_new" in update:
                        link["log_weight"] = update["log_weight_new"]
                    link["last_weight_frame"] = payload.get("frame_id")
                    link["last_cursor"] = self.cursor
                else:
                    node = self._ensure_node_entry(item_id)
                    if "log_weight_after" in update:
                        node["log_weight"] = update["log_weight_after"]
                    if "log_weight_new" in update:
                        node["log_weight"] = update["log_weight_new"]
                    node["last_weight_frame"] = payload.get("frame_id")
                    node["last_cursor"] = self.cursor
            self._update_metadata("weights", payload)
        elif event_type == "subentity.weights.updated":
            pl = payload.get("payload", {})
            entity_info = pl.get("entity", {})
            entity_id = entity_info.get("id")
            if entity_id:
                entity = self._ensure_subentity_entry(entity_id)
                entity["cohesion_before"] = entity_info.get("cohesion_before")
                entity["cohesion_after"] = entity_info.get("cohesion_after")
                entity["stability_z"] = entity_info.get("stability_z")
                entity["formation_quality_q"] = entity_info.get("formation_quality_q")
                entity["last_weights_frame"] = payload.get("frame_id")
                entity["last_cursor"] = self.cursor
            for change in pl.get("memberships", []):
                node_id = change.get("node_id")
                if not node_id:
                    continue
                node = self._ensure_node_entry(node_id)
                node["membership_weight"] = change.get("weight_new")
                node["membership_weight_prev"] = change.get("weight_prev")
                node["membership_last_update"] = payload.get("frame_id")
                node["last_cursor"] = self.cursor
            self._update_metadata("subentity_weights", payload)
        elif event_type == "subentity.membership.pruned":
            pl = payload.get("payload", {})
            node_id = pl.get("node_id")
            if node_id:
                node = self._ensure_node_entry(node_id)
                node["membership_weight"] = None
                node["membership_last_update"] = payload.get("frame_id")
                node["last_cursor"] = self.cursor
            self._update_metadata("membership_pruned", payload)
        elif event_type == "se.boundary.summary":
            self._update_metadata("boundary_summary", payload)
        elif event_type == "stimulus.injection.debug":
            self._update_metadata("stimulus_debug", payload)
        elif event_type == "membrane.inject.ack":
            self._update_metadata("membrane_inject_ack", payload)
        elif event_type == "stride.exec":
            self._update_metadata("stride_exec", payload)
        elif event_type == "tick.update":
            self._update_metadata("tick", payload)

class GraphStreamAggregator:
    """Aggregates live deltas into a RAM working set (no persistence)."""

    def __init__(self):
        self._states: Dict[str, GraphWorkingSet] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    # ------------------------------------------------------------------ Helpers

    def _get_lock(self, citizen_id: str) -> asyncio.Lock:
        lock = self._locks.get(citizen_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[citizen_id] = lock
        return lock

    def _get_state(self, citizen_id: str) -> GraphWorkingSet:
        state = self._states.get(citizen_id)
        if state is None:
            state = GraphWorkingSet(citizen_id)
            self._states[citizen_id] = state
        return state

    # -------------------------------------------------------------- Public API

    async def seed_from_graph(
        self,
        citizen_id: str,
        graph: Graph,
        *,
        include_links: bool = True,
        include_subentities: bool = True,
        cause: str = "bootstrap"
    ) -> None:
        """
        Reset and seed the working set using an in-memory Graph snapshot.

        Emits `graph.delta.*` events for every node/link/subentity so downstream
        clients can rebuild state purely from the event stream.

        Also populates SnapshotCache so newly connected clients receive full graph state.
        """
        lock = self._get_lock(citizen_id)
        async with lock:
            state = self._get_state(citizen_id)
            state.reset()
            ts = time.time()

            # Also populate SnapshotCache for replay-on-connect
            from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache
            cache = get_snapshot_cache()

            for node in graph.nodes.values():
                payload = {
                    "citizen_id": citizen_id,
                    "node": _node_to_payload(node),
                    "cause": cause
                }
                state.record_event("graph.delta.node.upsert", payload, ts)

                # Populate cache
                node_data = payload["node"]
                cache.upsert_node(citizen_id, node_data)

            if include_links:
                for link in graph.links.values():
                    payload = {
                        "citizen_id": citizen_id,
                        "link": _link_to_payload(link),
                        "cause": cause
                    }
                    state.record_event("graph.delta.link.upsert", payload, ts)

                    # Populate cache
                    link_data = payload["link"]
                    cache.upsert_link(citizen_id, link_data)

            if include_subentities and graph.subentities:
                for entity in graph.subentities.values():
                    payload = {
                        "citizen_id": citizen_id,
                        "subentity": _subentity_to_payload(entity),
                        "cause": cause
                    }
                    state.record_event("graph.delta.subentity.upsert", payload, ts)

                    # Populate cache
                    subentity_data = payload["subentity"]
                    cache.upsert_subentity(citizen_id, subentity_data)

            subentities = getattr(graph, "subentities", None)
            state.metadata["seed"] = {
                "cause": cause,
                "ts": ts,
                "node_count": len(graph.nodes),
                "link_count": len(graph.links),
                "subentity_count": len(subentities) if subentities else 0
            }

            # Log cache population for debugging
            logger.info(
                f"[seed_from_graph] Populated SnapshotCache for {citizen_id}: "
                f"{len(graph.nodes)} nodes, {len(graph.links)} links, "
                f"{len(subentities) if subentities else 0} subentities"
            )

    async def ingest_event(
        self,
        citizen_id: str,
        event_type: str,
        payload: Any
    ) -> None:
        """
        Record an event and update working set.

        Unknown event types are still logged to preserve replay continuity.
        """
        lock = self._get_lock(citizen_id)
        async with lock:
            state = self._get_state(citizen_id)
            if isinstance(payload, dict):
                payload = dict(payload)
            elif isinstance(payload, list):
                items = [dict(item) if isinstance(item, dict) else item for item in payload]
                payload = {"items": items}
            else:
                payload = {"value": payload}
            payload.setdefault("citizen_id", citizen_id)
            state.record_event(event_type, payload)

    async def get_working_set(self, citizen_id: str) -> Dict[str, Any]:
        """
        Return the current working set snapshot (for REST/diagnostics fallback).
        """
        lock = self._get_lock(citizen_id)
        async with lock:
            state = self._get_state(citizen_id)
            return {
                "citizen_id": citizen_id,
                "cursor": state.cursor,
                "last_event_ts": state.last_event_ts,
                "nodes": [dict(node) for node in state.nodes.values()],
                "links": [dict(link) for link in state.links.values()],
                "subentities": [dict(entity) for entity in state.subentities.values()],
                "metadata": copy.deepcopy(state.metadata)
            }


_aggregator: Optional[GraphStreamAggregator] = None


def get_stream_aggregator() -> GraphStreamAggregator:
    """Singleton accessor used across services."""
    global _aggregator
    if _aggregator is None:
        _aggregator = GraphStreamAggregator()
    return _aggregator


# Convenience alias for modules that prefer direct import
stream_aggregator = get_stream_aggregator()
