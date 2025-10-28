"""
Protocol (Layer-4) resolver API.

Provides cached lookups for protocol schemas, capabilities, and compatibility
metadata stored in the dedicated `protocol` FalkorDB graph. Designed to enforce
strict versioned lookups while emitting lightweight telemetry for observability.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List

from falkordb import FalkorDB


LOGGER = logging.getLogger(__name__)


class ProtocolResolutionError(Exception):
    """Base error for protocol resolver failures."""


class ProtocolNotFoundError(ProtocolResolutionError):
    """Raised when a schema or capability cannot be located."""


class ProtocolVersionRequiredError(ProtocolResolutionError):
    """Raised when a schema_ref omits mandatory version information."""


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


def _now() -> float:
    return time.time()


def _is_primitive_list(value: List[Any]) -> bool:
    return all(not isinstance(item, (dict, list)) for item in value)


def _decode_value(value: Any) -> Any:
    if isinstance(value, str) and value and value[0] in ("{", "["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, list) and not _is_primitive_list(value):
        return value
    return value


def _categorise_target(target_id: str) -> Optional[str]:
    if target_id.startswith("protocol/SDK_Release/"):
        return "sdks"
    if target_id.startswith("protocol/Sidecar_Release/"):
        return "sidecars"
    if target_id.startswith("protocol/Adapter_Release/"):
        return "adapters"
    return None


class ProtocolResolver:
    """Cached accessor for protocol graph metadata."""

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 6379,
        graph: str = "protocol",
        ttl_seconds: int = 60,
        negative_ttl_seconds: int = 10,
    ) -> None:
        self._db = FalkorDB(host=host, port=port)
        self._graph = self._db.select_graph(graph)
        self._ttl = ttl_seconds
        self._negative_ttl = negative_ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._negative_cache: Dict[str, float] = {}
        self._compat_cache: Dict[str, CacheEntry] = {}

    # ------------------------------------------------------------------ utility

    def _emit_telemetry(self, event: str, payload: Dict[str, Any]) -> None:
        LOGGER.info("telemetry.%s %s", event, payload)

    def _canonical_id(self, schema_ref: str) -> str:
        if schema_ref.startswith("protocol/"):
            return schema_ref
        if "@" not in schema_ref:
            raise ProtocolVersionRequiredError(
                "schema_ref must include @major.minor (e.g., membrane.inject@1.1)"
            )

        prefix, version = schema_ref.rsplit("@", 1)
        if ":" in prefix:
            type_hint, name = prefix.split(":", 1)
        else:
            type_hint, name = "event", prefix

        type_hint = type_hint.lower()
        if type_hint in {"event", "event_schema"}:
            return f"protocol/Event_Schema/{name}@{version}"
        if type_hint in {"envelope", "envelope_schema"}:
            return f"protocol/Envelope_Schema/{name}@{version}"
        if type_hint in {"capability"}:
            return f"protocol/Capability/{name}"
        if type_hint in {"tool", "tool_contract"}:
            return f"protocol/Tool_Contract/{name}"
        if type_hint in {"bundle", "schema_bundle"}:
            return f"protocol/Schema_Bundle/{name}@{version}"
        raise ProtocolResolutionError(f"Unknown schema_ref prefix '{type_hint}' for '{schema_ref}'.")

    def _fetch_node(self, node_id: str) -> Optional[Tuple[Dict[str, Any], List[str]]]:
        result = self._graph.query(
            """
            MATCH (n:ProtocolNode {id: $id})
            RETURN n, labels(n)
            """,
            params={"id": node_id},
        )
        if not result.result_set:
            return None
        node_obj, label_list = result.result_set[0]
        props = {key: _decode_value(value) for key, value in node_obj.properties.items()}
        return props, [label for label in label_list if label != "ProtocolNode"]

    def _cache_get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and entry.expires_at > _now():
            return entry.value
        if entry:
            self._cache.pop(key, None)
        return None

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = CacheEntry(value=value, expires_at=_now() + self._ttl)

    def _neg_cache_hit(self, key: str) -> bool:
        expires_at = self._negative_cache.get(key)
        if not expires_at:
            return False
        if expires_at > _now():
            return True
        self._negative_cache.pop(key, None)
        return False

    def _neg_cache_add(self, key: str) -> None:
        self._negative_cache[key] = _now() + self._negative_ttl

    # ------------------------------------------------------------------ public API

    def resolve_schema_id(
        self,
        schema_ref: str,
        *,
        caller: Optional[str] = None,
        org: Optional[str] = None,
        include_compat: bool = True,
    ) -> Dict[str, Any]:
        node_id = self._canonical_id(schema_ref)
        cached = self._cache_get(node_id)
        if cached is not None:
            self._emit_telemetry("resolver.hit", {"id": node_id, "caller": caller, "org": org})
            return cached

        if self._neg_cache_hit(node_id):
            self._emit_telemetry("resolver.negative_hit", {"id": node_id, "caller": caller, "org": org})
            raise ProtocolNotFoundError(f"{schema_ref} not found (cached miss).")

        result = self._fetch_node(node_id)
        if not result:
            self._neg_cache_add(node_id)
            self._emit_telemetry("resolver.miss", {"id": node_id, "caller": caller, "org": org})
            raise ProtocolNotFoundError(f"{schema_ref} not found.")

        props, labels = result
        props["id"] = node_id
        props["labels"] = labels
        if include_compat:
            props["compat"] = self.compat_for(node_id, caller=caller, org=org)
        self._cache_set(node_id, props)
        self._emit_telemetry("resolver.fetch", {"id": node_id, "caller": caller, "org": org})
        return props

    def resolve_latest(
        self,
        type_name: str,
        name: str,
        *,
        caller: Optional[str] = None,
        org: Optional[str] = None,
    ) -> Dict[str, Any]:
        type_name = type_name.strip()
        label = type_name if type_name.startswith("Protocol_") else type_name
        query = """
            MATCH (n:ProtocolNode:%s {name: $name})
            RETURN n.id, n.version
        """ % label
        result = self._graph.query(query, params={"name": name})
        if not result.result_set:
            self._emit_telemetry(
                "resolver.latest_miss",
                {"type": type_name, "name": name, "caller": caller, "org": org},
            )
            raise ProtocolNotFoundError(f"No versions found for {type_name} '{name}'.")

        candidates = []
        for node_id, version in result.result_set:
            candidates.append((self._parse_version(version or "0.0"), node_id))
        node_id = max(candidates)[1]
        return self.resolve_schema_id(node_id, caller=caller, org=org)

    def compat_for(
        self,
        node_id: str,
        *,
        caller: Optional[str] = None,
        org: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        cached = self._cache_get(f"compat:{node_id}")
        if cached is not None:
            return cached

        result = self._graph.query(
            """
            MATCH (n:ProtocolNode {id:$id})-[r]->(m:ProtocolNode)
            WHERE TYPE(r) IN [
                'COMPATIBLE_WITH', 'SUPPORTS', 'ADAPTER_SUPPORTS',
                'IMPLEMENTS', 'CERTIFIES_CONFORMANCE', 'GOVERNS'
            ]
            RETURN 'out' AS direction, TYPE(r) AS rel_type, m.id AS target_id, r AS rel
            UNION ALL
            MATCH (m:ProtocolNode)-[r]->(n:ProtocolNode {id:$id})
            WHERE TYPE(r) IN [
                'COMPATIBLE_WITH', 'SUPPORTS', 'ADAPTER_SUPPORTS',
                'IMPLEMENTS', 'CERTIFIES_CONFORMANCE', 'GOVERNS'
            ]
            RETURN 'in' AS direction, TYPE(r) AS rel_type, m.id AS target_id, r AS rel
            """,
            params={"id": node_id},
        )

        compat_map: Dict[str, List[Dict[str, Any]]] = {"sdks": [], "sidecars": [], "adapters": []}
        for direction, rel_type, target_id, rel in result.result_set:
            props = {key: _decode_value(value) for key, value in rel.properties.items()}
            bucket = _categorise_target(target_id)
            if bucket:
                compat_map[bucket].append({"target_id": target_id, "properties": props, "direction": direction})

        self._cache_set(f"compat:{node_id}", compat_map)
        self._emit_telemetry(
            "resolver.compat_fetch",
            {"id": node_id, "caller": caller, "org": org, "edge_count": len(result.result_set)},
        )
        return compat_map

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _parse_version(version: str) -> Tuple[int, ...]:
        try:
            return tuple(int(part) for part in version.split("."))
        except ValueError:
            return (0,)
