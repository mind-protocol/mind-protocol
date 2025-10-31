"""
Consciousness Control API

⚠️  ALL REST ENDPOINTS DISABLED (2025-10-30)

Architectural Decision: WebSocket-Only Communication
    - All data flow via WebSocket events
    - No REST API endpoints
    - Frontend subscribes to event streams

Active Endpoints:
    WS   /api/ws    - Live consciousness event stream (ONLY endpoint)

Disabled Endpoints (Reference Only):
    - All /api/consciousness/* endpoints (disabled)
    - All /api/citizen/* endpoints (disabled)
    - All /api/ecosystem/* endpoints (disabled)
    - All /api/graph/* endpoints (disabled)
    - All /api/telemetry/* endpoints (disabled)
    - All /api/search/* endpoints (disabled)

Integration:
    from orchestration.adapters.api.control_api import router, websocket_manager
    app.include_router(router)  # Includes WebSocket endpoint only
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from dataclasses import asdict, is_dataclass
from fnmatch import fnmatch
from typing import Optional, List, Dict, Any, Literal, Set
from uuid import uuid4

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from orchestration.adapters.storage.engine_registry import (
    pause_citizen,
    resume_citizen,
    set_citizen_speed,
    pause_all,
    resume_all,
    get_system_status,
    get_engine,
    get_all_engines
)
from orchestration.mechanisms.affective_telemetry_buffer import get_affective_buffer
from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph
from orchestration.adapters.ws.stream_aggregator import get_stream_aggregator
from orchestration.services.economy.runtime import get_runtime as get_economy_runtime
from orchestration.libs.stimuli import emit_ui_action
from orchestration.schemas.membrane_envelopes import Scope, StimulusFeatures
from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache

try:  # Wallet custody service is optional until configured
    from orchestration.services.wallet_custody.config import WalletCustodySettings
    from orchestration.services.wallet_custody.service import WalletCustodyService
except Exception:  # pragma: no cover - service not configured
    WalletCustodyService = None  # type: ignore[assignment]

# Configure logging
logger = logging.getLogger(__name__)

try:  # Optional dependency guard
    import numpy as np  # type: ignore[import]
except Exception:  # pragma: no cover - runtime normally has numpy, guard for safety
    np = None


# === Telemetry Event Types ===
# Events that should be buffered for affective telemetry
TELEMETRY_EVENT_TYPES = {
    # V2 core consciousness events
    "frame.start", "frame.end",
    "decay.tick", "stride.exec",
    "entity.flip", "wm.emit",
    "criticality.state",
    "link.flow.summary",
    "node.flip",

    # Affective coupling events (PR-A)
    "affective.threshold", "affective.memory",
    "coherence.persistence", "pattern.multiresponse",
    "identity.multiplicity", "consolidation",
    "decay.resistance", "diffusion.stickiness",
    "affective.priming", "coherence.metric",
    "criticality.mode",

    # Legacy V1 events (for backward compatibility)
    "entity_activity", "threshold_crossing",
    "consciousness_state", "node_activation",
    "link_traversal"
}


# === WebSocket Manager (Singleton) ===

DEFAULT_TOPICS: Set[str] = {
    "graph.delta.node.*",
    "graph.delta.link.*",
    "graph.delta.subentity.*",
    "wm.emit",
    "percept.frame",
    "emergence.*",
    "mode.*",
    "state_modulation.frame",
    "rich_club.*",
    "integration_metrics.*",
}

SUBSCRIBE_MESSAGE_TYPES = {"subscribe", "subscribe@1.0"}
SUBSCRIBE_ACK_TYPE = "subscribe.ack@1.0"
INITIAL_SUBSCRIBE_TIMEOUT_SECONDS = 1.0
HEARTBEAT_INTERVAL_SECONDS = 20
MAX_WEBSOCKET_CONNECTIONS = 50  # Prevent connection leak overload
HEARTBEAT_TIMEOUT_SECONDS = 60


class WebSocketManager:
    """
    Manages WebSocket connections for live consciousness operations stream.

    Singleton pattern - all mechanisms broadcast through this manager.
    Dashboard connects to /ws endpoint to receive real-time events.
    """

    def __init__(self):
        """Initialize WebSocket manager with empty connection registry."""
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._ws_to_conn: Dict[WebSocket, str] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        logger.info("[WebSocketManager] Initialized")

    def start_heartbeat_check(self):
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._periodic_check())

    async def _periodic_check(self):
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
            now = datetime.now(timezone.utc)
            stale_connections = []
            for conn_id, meta in list(self._connections.items()):
                if (now - meta["last_heartbeat"]).total_seconds() > HEARTBEAT_TIMEOUT_SECONDS:
                    stale_connections.append(conn_id)
                elif (now - meta["last_heartbeat"]).total_seconds() > HEARTBEAT_INTERVAL_SECONDS:
                    try:
                        await meta["ws"].send_json({"type": "ping", "ts": now.isoformat()})
                    except Exception:
                        stale_connections.append(conn_id)
            
            for conn_id in stale_connections:
                logger.warning(f"[WebSocketManager] Closing stale connection {conn_id}")
                await self.unregister_connection(conn_id=conn_id)


    @property
    def active_connections(self) -> List[WebSocket]:
        return [meta["ws"] for meta in self._connections.values()]

    def client_count(self) -> int:
        """Returns the number of active WebSocket connections."""
        return len(self._connections)

    def iter(self) -> List[tuple[str, Dict[str, Any]]]:
        return list(self._connections.items())

    async def register_connection(
        self,
        conn_id: str,
        websocket: WebSocket,
        topics: Set[str],
        cursor: Optional[str] = None,
    ):
        self._connections[conn_id] = {
            "ws": websocket,
            "topics": set(topics),
            "cursor": cursor,
            "last_heartbeat": datetime.now(timezone.utc),
        }
        self._ws_to_conn[websocket] = conn_id
        logger.info(
            "[WebSocketManager] Client registered conn=%s topics=%d total=%d",
            conn_id,
            len(topics),
            len(self._connections),
        )

    async def unregister_connection(
        self,
        conn_id: Optional[str] = None,
        websocket: Optional[WebSocket] = None,
    ):
        if conn_id is None and websocket is not None:
            conn_id = self._ws_to_conn.get(websocket)

        if not conn_id:
            return

        meta = self._connections.pop(conn_id, None)
        if meta:
            self._ws_to_conn.pop(meta["ws"], None)
            try:
                await meta["ws"].close()
            except Exception:
                pass
            logger.info(
                "[WebSocketManager] Client disconnected conn=%s total=%d",
                conn_id,
                len(self._connections),
            )

    def update_topics(self, websocket: WebSocket, topics: Set[str]) -> None:
        conn_id = self._ws_to_conn.get(websocket)
        if not conn_id:
            return
        self._connections[conn_id]["topics"] = set(topics)
        logger.debug(
            "[WebSocketManager] Updated topics conn=%s topics=%s",
            conn_id,
            topics,
        )

    def touch(self, websocket: WebSocket) -> None:
        conn_id = self._ws_to_conn.get(websocket)
        if not conn_id:
            return
        self._connections[conn_id]["last_heartbeat"] = datetime.now(timezone.utc)

    def get_connection_id(self, websocket: WebSocket) -> Optional[str]:
        return self._ws_to_conn.get(websocket)

    async def broadcast(self, event: Dict[str, Any]):
        """
        Broadcast event to all connected clients AND buffer for telemetry.

        Args:
            event: Event dict with 'type' and event-specific data
        """
        event_type = event.get("type")
        if not event_type:
            logger.warning("[WebSocketManager] Broadcast skipping malformed event with no type: %s", event)
            return

        # Buffer for affective telemetry before any network IO
        if event_type in TELEMETRY_EVENT_TYPES:
            try:
                buffer = get_affective_buffer()
                buffer.add_event(event_type, event)
                logger.debug("[WebSocketManager] Buffered %s for telemetry", event_type)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("[WebSocketManager] Failed to buffer telemetry: %s", exc)

        if not self._connections:
            logger.debug(
                "[WebSocketManager] Broadcast attempted but no clients connected (event=%s)",
                event_type,
            )
            return

        envelope = dict(event)
        envelope.setdefault("ts", datetime.now(timezone.utc).isoformat())
        if "spec" not in envelope:
            envelope["spec"] = {"name": "consciousness.v2", "rev": "2.0.0"}
        if "provenance" not in envelope:
            logger.warning("[WebSocketManager] Broadcast missing provenance; dropping event type=%s", event_type)
            return
        envelope.setdefault("payload", {})
        envelope.setdefault("id", stable_event_id(event_type, envelope))

        safe_envelope = _ensure_json_serializable(envelope)
        preview = json.dumps(safe_envelope, ensure_ascii=False)[:160]

        disconnected: List[str] = []
        delivered = 0

        for conn_id, meta in list(self._connections.items()):
            topics: Set[str] = meta.get("topics", set())
            websocket = meta.get("ws")
            if websocket is None:
                disconnected.append(conn_id)
                continue

            if not _match_topic(event_type, topics):
                continue

            try:
                await websocket.send_json(safe_envelope)
                delivered += 1
            except Exception as exc:
                logger.warning("[WebSocketManager] Send failed conn=%s: %s", conn_id, exc)
                disconnected.append(conn_id)

        for conn_id in disconnected:
            await self.unregister_connection(conn_id=conn_id)

        logger.info(
            "[Bus] send %s to %d clients: %s…",
            event_type,
            delivered,
            preview,
        )


def _match_topic(topic: str, patterns: Set[str]) -> bool:
    if not patterns:
        return True
    return any(fnmatch(topic, pattern) for pattern in patterns)


def stable_event_id(event_type: str, event: Dict[str, Any]) -> str:
    """
    Generate deterministic-ish IDs for events that arrive without an explicit id.
    Uses payload + provenance to reduce duplication risk.
    """
    try:
        to_hash = json.dumps(
            {
                "type": event_type,
                "provenance": event.get("provenance"),
                "payload": event.get("payload"),
            },
            sort_keys=True,
            default=str,
        )
    except Exception:
        to_hash = f"{event_type}:{datetime.now(timezone.utc).timestamp()}"

    digest = hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
    return f"evt_{digest[:16]}"


def current_citizen_id() -> str:
    """Best-effort citizen id used for provenance during handshake."""
    try:
        from orchestration.adapters.storage.engine_registry import get_all_engines  # pylint: disable=import-outside-toplevel

        engines = get_all_engines()  # Returns Dict[str, ConsciousnessEngineV2]
        if engines:
            # Return first registered citizen_id (dict keys are citizen_ids)
            return next(iter(engines.keys()))
    except Exception:
        pass
    return "websocket-server"  # System-level fallback (not citizen-specific)


def get_last_frame_id() -> Optional[str]:
    """Optional cursor the client can request for snapshot hydration."""
    try:
        aggregator = get_stream_aggregator()
        # Aggregator may expose citizen-level cursors; use first citizen if available.
        citizen_id = current_citizen_id()
        if citizen_id == "unknown":
            return None
        state = aggregator._states.get(citizen_id)  # type: ignore[attr-defined]  # pragma: no cover - diagnostic path
        if state is not None:
            return str(getattr(state, "cursor", None))
    except Exception:
        pass
    return None


def iter_snapshot_chunks(
    cursor: Optional[str] = None,
    *,
    citizen_id: Optional[str] = None,
    page_size: int = 512
):
    """
    Yield snapshot chunk dictionaries for WebSocket hydration.

    UPDATED 2025-10-31: Source from SnapshotCache (replay-on-connect pattern).
    This decouples engine initialization timing from client connection timing.

    Problem Solved:
    - Engines initialize at 01:42, frontend connects at 01:47
    - Without cache: Frontend receives 0 nodes (broadcasts already sent to nobody)
    - With cache: Frontend receives full snapshot regardless of timing
    """
    from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache

    cache = get_snapshot_cache()
    citizen = citizen_id or current_citizen_id()

    if citizen == "unknown" or citizen == "websocket-server":
        # No specific citizen: try all cached citizens
        all_citizens = cache.get_all_citizen_ids()
        if not all_citizens:
            # No data in cache yet (engines still initializing?)
            yield {
                "idx": 0,
                "nodes": [],
                "links": [],
                "subentities": [],
                "cursor": cursor,
                "eof": True
            }
            return
        # Use first available citizen
        citizen = all_citizens[0]
        logger.info(f"[iter_snapshot_chunks] Auto-selected citizen: {citizen}")

    # Get snapshot from cache
    try:
        snapshot = cache.build_snapshot(citizen)
        nodes = snapshot.get("nodes", [])
        links = snapshot.get("links", [])
        subentities = snapshot.get("subentities", [])

        logger.info(
            f"[iter_snapshot_chunks] Loaded from cache: {citizen} "
            f"({len(nodes)} nodes, {len(links)} links, {len(subentities)} subentities)"
        )

    except Exception as exc:
        logger.error(f"[iter_snapshot_chunks] Error loading from cache for {citizen}: {exc}")
        yield {
            "idx": 0,
            "nodes": [],
            "links": [],
            "subentities": [],
            "cursor": cursor,
            "eof": True
        }
        return

    cursor_value = cursor or ""

    total_nodes = len(nodes)
    if total_nodes == 0:
        yield {
            "idx": 0,
            "nodes": _ensure_json_serializable(nodes),
            "links": _ensure_json_serializable(links),
            "subentities": _ensure_json_serializable(subentities),
            "cursor": cursor_value,
            "eof": True
        }
        return

    for idx, start in enumerate(range(0, total_nodes, page_size)):
        chunk_nodes = nodes[start:start + page_size]
        node_ids = {node.get("id") for node in chunk_nodes if node.get("id")}

        chunk_links = [
            link for link in links
            if link.get("source") in node_ids or link.get("target") in node_ids
        ] if node_ids else links

        eof = (start + page_size) >= total_nodes

        yield {
            "idx": idx,
            "nodes": _ensure_json_serializable(chunk_nodes),
            "links": _ensure_json_serializable(chunk_links),
            "subentities": _ensure_json_serializable(subentities),
            "cursor": cursor_value,
            "eof": eof
        }

        if eof:
            break


def _ensure_json_serializable(value: Any) -> Any:
    """
    Recursively coerce values into JSON-serializable primitives.

    Converts numpy scalars/arrays, dataclasses, sets, tuples, and datetime objects.
    Leaves native Python primitives untouched.
    """
    if isinstance(value, dict):
        return {key: _ensure_json_serializable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_ensure_json_serializable(item) for item in value]
    if isinstance(value, tuple):
        return [_ensure_json_serializable(item) for item in value]
    if isinstance(value, set):
        return [_ensure_json_serializable(item) for item in value]
    if is_dataclass(value):
        return _ensure_json_serializable(asdict(value))
    if isinstance(value, datetime):
        return value.isoformat()

    if np is not None:
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()

    return value


# Global singleton instance
websocket_manager = WebSocketManager()

# Lazy-initialised wallet custody service
_wallet_custody_service: Optional["WalletCustodyService"] | bool = None


def _get_wallet_service() -> Optional[WalletCustodyService]:
    global _wallet_custody_service

    if WalletCustodyService is None:
        return None

    if _wallet_custody_service is False:
        return None

    if _wallet_custody_service is None:
        try:
            settings = WalletCustodySettings.from_env()
            _wallet_custody_service = WalletCustodyService(settings)
        except Exception as exc:  # pragma: no cover - env not ready
            logger.warning("[WebSocket] Wallet custody service unavailable: %s", exc)
            _wallet_custody_service = False

    return _wallet_custody_service or None

# Snapshot generation will be added by Iris (TODO)

# Create router
router = APIRouter(prefix="/api", tags=["consciousness-control"])

# ============================================================================
# ALL REST ENDPOINTS DISABLED - WebSocket-Only Architecture (2025-10-30)
# ============================================================================
# The following endpoints are disabled per architectural decision.
# System uses WebSocket-only communication - no REST API.
# Decorators are commented out to prevent route registration.
# Function code preserved for reference only.
# ============================================================================

# === DISABLED REST ENDPOINTS (Reference Only) ===

# @router.get("/ping")  # DISABLED: REST API removed
async def ping():
    """Health check endpoint to verify Control API router is mounted."""
    return {"ok": True}


class SpeedRequest(BaseModel):
    """Request body for speed control."""
    multiplier: float


# === System-Wide Endpoints ===


# @router.get("/consciousness/status")  # DISABLED: REST API removed
async def get_system_status_endpoint():
    """
    Get status of all consciousness engines.

    Returns:
        {
            "total_engines": 3,
            "frozen": 1,
            "running": 2,
            "slow_motion": 0,
            "engines": {
                "felix-engineer": {...},
                "ada-architect": {...}
            }
        }
    """
    return get_system_status()


# @router.get("/consciousness/constant-debt")  # DISABLED: REST API removed
async def get_constant_debt():
    """
    Get constant debt metrics (Tier 1 Amendment 4).

    Tracks progress toward zero-constant architecture:
    - WM alpha debt: How many COACTIVATES_WITH edges still use constant alpha
    - Mode contour debt: How many contours are still from bootstrap vs learned

    Returns:
        {
            "wm_alpha": {
                "total_edges": 600,
                "constant_count": 180,
                "learned_count": 420,
                "debt_ratio": 0.30
            },
            "mode_contours": [
                {
                    "mode_id": "guardian",
                    "entry_source": "learned",
                    "entry_samples": 450,
                    "exit_source": "learned",
                    "exit_samples": 520
                }
            ]
        }
    """
    try:
        # Get all graphs to check across citizens
        graph_store = get_falkordb_graph()

        # Metric 1: WM Alpha Debt
        alpha_query = """
        MATCH ()-[r:COACTIVATES_WITH]->()
        WITH
          count(*) AS total,
          sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'constant' THEN 1 ELSE 0 END) AS constant,
          sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'learned' THEN 1 ELSE 0 END) AS learned
        RETURN
          total AS total_edges,
          constant AS constant_count,
          learned AS learned_count,
          CASE WHEN total > 0 THEN (constant * 1.0 / total) ELSE 0.0 END AS debt_ratio
        """

        # Metric 2: Mode Contour Debt
        contour_query = """
        MATCH (m:Mode)
        OPTIONAL MATCH (m)-[:HAS_ENTRY_CONTOUR]->(entry:Contour)
        OPTIONAL MATCH (m)-[:HAS_EXIT_CONTOUR]->(exit:Contour)
        RETURN
          m.id AS mode_id,
          coalesce(entry.source, 'none') AS entry_source,
          coalesce(entry.sample_size, 0) AS entry_samples,
          coalesce(exit.source, 'none') AS exit_source,
          coalesce(exit.sample_size, 0) AS exit_samples
        """

        # Execute queries
        alpha_result = graph_store.query(alpha_query)
        contour_result = graph_store.query(contour_query)

        # Parse WM alpha results
        wm_alpha = {
            "total_edges": 0,
            "constant_count": 0,
            "learned_count": 0,
            "debt_ratio": 0.0
        }

        if hasattr(alpha_result, 'result_set') and alpha_result.result_set:
            row = alpha_result.result_set[0]
            wm_alpha = {
                "total_edges": int(row[0]),
                "constant_count": int(row[1]),
                "learned_count": int(row[2]),
                "debt_ratio": float(row[3])
            }

        # Parse mode contour results
        mode_contours = []
        if hasattr(contour_result, 'result_set'):
            for row in contour_result.result_set:
                mode_contours.append({
                    "mode_id": row[0],
                    "entry_source": row[1],
                    "entry_samples": int(row[2]),
                    "exit_source": row[3],
                    "exit_samples": int(row[4])
                })

        return {
            "wm_alpha": wm_alpha,
            "mode_contours": mode_contours
        }

    except Exception as e:
        logger.error(f"[ConstantDebt] Failed to fetch metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch constant debt: {str(e)}")


# @router.post("/consciousness/pause-all")  # DISABLED: REST API removed
async def pause_all_endpoint():
    """
    EMERGENCY FREEZE ALL - Pause all consciousness engines.

    Sets tick_multiplier = 1e9 for all engines (frozen state).
    Loops continue but sleep indefinitely.

    Returns:
        {
            "status": "all_paused",
            "count": 3,
            "paused_citizens": ["felix", "ada", "luca"]
        }
    """
    return pause_all()


# @router.post("/consciousness/resume-all")  # DISABLED: REST API removed
async def resume_all_endpoint():
    """
    Resume all consciousness engines.

    Resets tick_multiplier = 1.0 for all engines (normal speed).

    Returns:
        {
            "status": "all_resumed",
            "count": 3,
            "resumed_citizens": ["felix", "ada", "luca"]
        }
    """
    return resume_all()


# @router.get("/graphs")  # DISABLED: REST API removed
async def get_available_graphs():
    """
    List all consciousness graphs in FalkorDB.

    Returns graphs organized by niveau:
        {
            "citizens": [
                {"id": "citizen_felix", "name": "Felix", "type": "personal"},
                {"id": "citizen_ada", "name": "Ada", "type": "personal"}
            ],
            "organizations": [
                {"id": "org_mind_protocol", "name": "Mind Protocol", "type": "organizational"}
            ],
            "ecosystems": [
                {"id": "ecosystem_public", "name": "Public Ecosystem", "type": "ecosystem"}
            ]
        }
    """
    import redis

    try:
        # Connect to FalkorDB
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get all graph names: GRAPH.LIST returns array of graph names
        graphs = r.execute_command("GRAPH.LIST")

        # Organize by prefix
        result = {
            "citizens": [],
            "organizations": [],
            "ecosystems": []
        }

        for graph_name in graphs:
            if graph_name.startswith("citizen_"):
                citizen_id = graph_name.replace("citizen_", "")
                result["citizens"].append({
                    "id": graph_name,
                    "name": citizen_id.title(),
                    "type": "personal"
                })
            elif graph_name.startswith("org_"):
                org_id = graph_name.replace("org_", "")
                result["organizations"].append({
                    "id": graph_name,
                    "name": org_id.replace("_", " ").title(),
                    "type": "organizational"
                })
            elif graph_name.startswith("ecosystem_"):
                eco_id = graph_name.replace("ecosystem_", "")
                result["ecosystems"].append({
                    "id": graph_name,
                    "name": eco_id.title(),
                    "type": "ecosystem"
                })

        return result

    except Exception as e:
        logger.error(f"[API] Failed to list graphs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query FalkorDB: {str(e)}")


# @router.get("/search/semantic")  # DISABLED: REST API removed
async def semantic_search(
    query: str,
    graph_id: str,
    node_type: Optional[str] = None,
    limit: int = 10,
    threshold: float = 0.70
):
    """
    Semantic search for nodes using vector similarity.

    Enables conceptual exploration: "spreading activation" finds related nodes
    even without exact keyword matches.

    Args:
        query: Natural language search query
        graph_id: Graph to search (e.g., "citizen_iris")
        node_type: Optional filter by node type (e.g., "Realization", "Decision")
        limit: Maximum results to return (default: 10)
        threshold: Minimum similarity score 0-1 (default: 0.70)

    Returns:
        {
            "query": str,
            "results": [
                {
                    "name": str,
                    "description": str,
                    "type": str,
                    "similarity": float  # 0-1, higher = more similar
                },
                ...
            ]
        }

    Example:
        GET /api/search/semantic?query=spreading+activation&graph_id=citizen_iris&limit=5
    """
    from orchestration.adapters.search.semantic_search import SemanticSearch

    try:
        # Initialize semantic search for the specified graph
        search = SemanticSearch(graph_name=graph_id)

        # If no node_type specified, query multiple common types and merge results
        if not node_type:
            common_types = [
                "Realization", "Decision", "Concept", "Principle", "Mechanism",
                "Memory", "Best_Practice", "Anti_Pattern", "Personal_Goal",
                "Coping_Mechanism", "Document", "Process"
            ]

            all_results = []
            for ntype in common_types:
                try:
                    type_results = search.find_similar_nodes(
                        query_text=query,
                        node_type=ntype,
                        threshold=threshold,
                        limit=limit
                    )
                    all_results.extend(type_results)
                except Exception as e:
                    # Skip types that don't exist in this graph
                    logger.debug(f"[API] No results for type {ntype}: {e}")
                    continue

            # Sort by similarity and limit
            all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            results = all_results[:limit]
        else:
            # Perform vector similarity search for specific type
            results = search.find_similar_nodes(
                query_text=query,
                node_type=node_type,
                threshold=threshold,
                limit=limit
            )

        return {
            "query": query,
            "graph_id": graph_id,
            "node_type": node_type,
            "results": results
        }

    except Exception as e:
        logger.error(f"[API] Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


def _normalize_timestamp(value):
    """
    Normalize timestamp to milliseconds (numeric).

    Handles mixed formats from FalkorDB:
    - ISO 8601 strings ("2025-10-17T14:30:00Z") -> convert to ms
    - Numeric milliseconds -> pass through
    - None/null -> pass through

    Args:
        value: Timestamp in any format

    Returns:
        int: Timestamp in milliseconds, or None if invalid
    """
    if value is None:
        return None

    # Already numeric - pass through
    if isinstance(value, (int, float)):
        return int(value)

    # ISO 8601 string - convert to milliseconds
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except (ValueError, AttributeError):
            logger.warning(f"[API] Invalid timestamp format: {value}")
            return None

    # Bytes - decode then parse
    if isinstance(value, bytes):
        return _normalize_timestamp(value.decode('utf-8'))

    return None


def _normalize_slug(value: str) -> str:
    if not value:
        return ''

    normalized = value.strip().lower()
    for delimiter in [' ', '_']:
        normalized = normalized.replace(delimiter, '-')
    while '--' in normalized:
        normalized = normalized.replace('--', '-')
    return normalized


def _display_name(value: str) -> str:
    return value.replace('-', ' ').replace('_', ' ').title()


def _build_graph_name(ecosystem: str, organization: Optional[str] = None, citizen: Optional[str] = None) -> str:
    parts = [_normalize_slug(ecosystem)]
    if organization:
        parts.append(_normalize_slug(organization))
    if citizen:
        parts.append(_normalize_slug(citizen))
    return "_".join(parts)


def _collect_graph_hierarchy(redis_client) -> Dict[str, Dict[str, Any]]:
    graphs = redis_client.execute_command("GRAPH.LIST") or []
    hierarchy: Dict[str, Dict[str, Any]] = {}

    for raw in graphs:
        graph_name = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        segments = graph_name.split('_')

        if len(segments) == 1:
            ecosystem_slug = segments[0]
            entry = hierarchy.setdefault(ecosystem_slug, {
                "graph_id": graph_name,
                "organizations": {},
                "citizens": {}
            })
            entry["graph_id"] = graph_name
            continue

        if len(segments) >= 2:
            ecosystem_slug = segments[0]
            organization_slug = segments[1]
            entry = hierarchy.setdefault(ecosystem_slug, {
                "graph_id": ecosystem_slug,
                "organizations": {},
                "citizens": {}
            })
            org_entry = entry["organizations"].setdefault(organization_slug, {
                "graph_id": f"{ecosystem_slug}_{organization_slug}",
                "citizens": {}
            })

            if len(segments) >= 3:
                citizen_slug = "_".join(segments[2:])
                org_entry["citizens"][citizen_slug] = graph_name

    return hierarchy


def _resolve_actual_graph_id(r, graph_type: str, requested_id: str) -> str:
    all_graphs = r.execute_command("GRAPH.LIST") or []
    normalized_graphs = {
        g.decode('utf-8') if isinstance(g, bytes) else g for g in all_graphs
    }

    if requested_id in normalized_graphs:
        return requested_id

    raise HTTPException(status_code=404, detail=f"Graph not found: {requested_id}")


# @router.get("/ecosystems")  # DISABLED: REST API removed
async def list_ecosystems():
    import redis

    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        hierarchy = _collect_graph_hierarchy(r)

        ecosystems: List[Dict[str, Any]] = []
        for ecosystem_slug, data in sorted(hierarchy.items()):
            organizations = []
            for org_slug, org_data in sorted(data["organizations"].items()):
                citizens = [
                    {
                        "slug": citizen_slug,
                        "graph_id": citizen_graph_id,
                        "name": _display_name(citizen_slug)
                    }
                    for citizen_slug, citizen_graph_id in sorted(org_data["citizens"].items())
                ]
                organizations.append({
                    "slug": org_slug,
                    "graph_id": org_data["graph_id"],
                    "name": _display_name(org_slug),
                    "citizens": citizens
                })

            ecosystems.append({
                "slug": ecosystem_slug,
                "graph_id": data["graph_id"],
                "name": _display_name(ecosystem_slug),
                "organizations": organizations
            })

        return {"ecosystems": ecosystems}
    except Exception as e:
        logger.error(f"[API] Failed to enumerate ecosystems: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enumerate ecosystems: {str(e)}")


# @router.get("/ecosystem/{ecosystem_slug}/graphs")  # DISABLED: REST API removed
async def get_ecosystem_graphs(ecosystem_slug: str):
    import redis

    ecosystem_key = _normalize_slug(ecosystem_slug)

    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        hierarchy = _collect_graph_hierarchy(r)
        if ecosystem_key not in hierarchy:
            raise HTTPException(status_code=404, detail=f"Ecosystem not found: {ecosystem_slug}")

        data = hierarchy[ecosystem_key]
        organizations = [
            {
                "slug": org_slug,
                "graph_id": org_data["graph_id"],
                "name": _display_name(org_slug)
            }
            for org_slug, org_data in sorted(data["organizations"].items())
        ]

        return {
            "ecosystem": {
                "slug": ecosystem_key,
                "graph_id": data["graph_id"],
                "name": _display_name(ecosystem_key)
            },
            "organizations": organizations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Failed to fetch ecosystem graphs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ecosystem graphs: {str(e)}")


# @router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}/graphs")  # DISABLED: REST API removed
async def get_organization_graphs(ecosystem_slug: str, organization_slug: str):
    import redis

    ecosystem_key = _normalize_slug(ecosystem_slug)
    organization_key = _normalize_slug(organization_slug)

    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        hierarchy = _collect_graph_hierarchy(r)
        if ecosystem_key not in hierarchy:
            raise HTTPException(status_code=404, detail=f"Ecosystem not found: {ecosystem_slug}")

        ecosystem_data = hierarchy[ecosystem_key]
        org_data = ecosystem_data["organizations"].get(organization_key)
        if not org_data:
            raise HTTPException(status_code=404, detail=f"Organization not found: {organization_slug}")

        citizens = [
            {
                "slug": citizen_slug,
                "graph_id": citizen_graph_id,
                "name": _display_name(citizen_slug)
            }
            for citizen_slug, citizen_graph_id in sorted(org_data["citizens"].items())
        ]

        return {
            "ecosystem": {
                "slug": ecosystem_key,
                "graph_id": ecosystem_data["graph_id"],
                "name": _display_name(ecosystem_key)
            },
            "organization": {
                "slug": organization_key,
                "graph_id": org_data["graph_id"],
                "name": _display_name(organization_key)
            },
            "citizens": citizens
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Failed to fetch organization graphs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch organization graphs: {str(e)}")


# @router.get("/ecosystem/{ecosystem_slug}")  # DISABLED: REST API removed
async def get_ecosystem_graph_hierarchy(ecosystem_slug: str):
    """Hierarchical Niveau route for ecosystem-level graph snapshots."""
    graph_id = _build_graph_name(ecosystem_slug)
    return await get_graph_data(graph_type='ecosystem', graph_id=graph_id)


# @router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}")  # DISABLED: REST API removed
async def get_organization_graph_hierarchy(ecosystem_slug: str, organization_slug: str):
    """Hierarchical Niveau route for organization graphs nested under an ecosystem."""
    graph_id = _build_graph_name(ecosystem_slug, organization_slug)
    return await get_graph_data(graph_type='organization', graph_id=graph_id)


# @router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}/citizen/{citizen_slug}")  # DISABLED: REST API removed
async def get_citizen_graph_hierarchy(ecosystem_slug: str, organization_slug: str, citizen_slug: str):
    """Hierarchical Niveau route for citizen graphs nested under org + ecosystem."""
    graph_id = _build_graph_name(ecosystem_slug, organization_slug, citizen_slug)
    return await get_graph_data(graph_type='citizen', graph_id=graph_id)


# @router.get("/graph/{graph_type}/{graph_id}")  # DISABLED: REST API removed
async def get_graph_data(graph_type: str, graph_id: str):
    """
    Fetch initial graph snapshot from FalkorDB for dashboard visualization.

    This endpoint provides the initial state. Real-time updates come via /api/ws WebSocket.

    Args:
        graph_type: Type of graph (citizen, organization, ecosystem)
        graph_id: Full graph ID (e.g., "citizen_felix", "org_mind_protocol")

    Returns:
        {
            "graph_id": "citizen_felix",
            "graph_type": "citizen",
            "nodes": [
                {
                    "id": "node_123",
                    "node_id": "node_123",
                    "labels": ["Realization", "Personal"],
                    "node_type": "Realization",
                    "text": "System infrastructure proving itself",
                    "energy": 0.8,
                    "confidence": 0.9,
                    "entity_activations": {"builder": {"energy": 0.85}},
                    "last_active": 1697732400,
                    "traversal_count": 42
                }
            ],
            "links": [
                {
                    "id": "link_456",
                    "source": "node_123",
                    "target": "node_789",
                    "type": "ENABLES",
                    "strength": 0.75,
                    "last_traversed": 1697732450,
                    "entity_activations": {"builder": {"energy": 0.7}}
                }
            ],
            "metadata": {
                "node_count": 150,
                "link_count": 320,
                "last_updated": "2025-10-19T05:30:00Z"
            }
        }

    Architecture:
        - This REST endpoint loads initial snapshot
        - WebSocket at /api/ws provides real-time updates
        - Dashboard combines both for live visualization
    """
    import redis
    from datetime import datetime, timezone

    try:
        # Connect to FalkorDB
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        actual_graph_id = _resolve_actual_graph_id(r, graph_type, graph_id)

        # Query all nodes
        # Return node properties we care about for visualization
        # NOTE: BaseNode uses 'name' not 'node_id', and node_type comes from labels
        node_query = """
        MATCH (n)
        RETURN
            COALESCE(n.id, toString(id(n))) AS id,
            n.name AS node_id,
            labels(n) AS labels,
            CASE
                WHEN size(labels(n)) > 0 THEN labels(n)[0]
                ELSE null
            END AS node_type,
            n.description AS text,
            n.confidence AS confidence,
            n.E AS energy,
            n.entity_activations AS entity_activations,
            n.last_active AS last_active,
            n.last_traversal_time AS last_traversal_time,
            n.traversal_count AS traversal_count,
            n.created_at AS created_at,
            n.base_weight AS base_weight,
            n.reinforcement_weight AS reinforcement_weight,
            n.weight AS weight,
            n.last_modified AS last_modified
        LIMIT 1000
        """

        node_result = r.execute_command("GRAPH.QUERY", actual_graph_id, node_query)

        # FalkorDB returns: [header, rows, metadata]
        # header = list of column names
        # rows = list of row data (each row is list of values)
        nodes = []
        if node_result and len(node_result) > 1:
            header = node_result[0]  # Column names
            rows = node_result[1]     # Data rows

            for row in rows:
                # Build dict from header and row
                node_dict = {}
                for i, col_name in enumerate(header):
                    # Convert bytes column names to strings
                    col_str = col_name.decode('utf-8') if isinstance(col_name, bytes) else col_name
                    value = row[i]

                    # Handle None/null values
                    if value is None:
                        node_dict[col_str] = None
                    # Handle list values (labels)
                    elif isinstance(value, list):
                        node_dict[col_str] = [v.decode('utf-8') if isinstance(v, bytes) else v for v in value]
                    # Handle byte strings
                    elif isinstance(value, bytes):
                        node_dict[col_str] = value.decode('utf-8')
                    else:
                        node_dict[col_str] = value

                # Ensure id is string for frontend
                if 'id' in node_dict:
                    node_dict['id'] = str(node_dict['id'])

                # Normalize timestamps to milliseconds (handles mixed ISO 8601/numeric formats)
                for ts_field in ['created_at', 'last_active', 'last_modified', 'last_traversal_time']:
                    if ts_field in node_dict:
                        node_dict[ts_field] = _normalize_timestamp(node_dict[ts_field])

                # Parse JSON fields back to objects
                if 'entity_activations' in node_dict and node_dict['entity_activations']:
                    try:
                        node_dict['entity_activations'] = json.loads(node_dict['entity_activations'])
                    except (json.JSONDecodeError, TypeError):
                        node_dict['entity_activations'] = {}

                nodes.append(node_dict)

        # Query all links
        # Use actual node IDs (n.id property) for source/target to match corrected node.id
        # FIXED: Was using id(a)/id(b) which returns internal numeric IDs, now uses actual node.id property
        link_query = """
        MATCH (a)-[r]->(b)
        RETURN
            COALESCE(r.id, toString(id(r))) AS id,
            COALESCE(a.id, toString(id(a))) AS source,
            COALESCE(b.id, toString(id(b))) AS target,
            type(r) AS type,
            r.confidence AS strength,
            r.last_traversed AS last_traversed,
            r.created_at AS created_at,
            r.weight AS weight
        LIMIT 5000
        """

        link_result = r.execute_command("GRAPH.QUERY", actual_graph_id, link_query)

        links = []
        if link_result and len(link_result) > 1:
            header = link_result[0]
            rows = link_result[1]

            for row in rows:
                link_dict = {}
                for i, col_name in enumerate(header):
                    col_str = col_name.decode('utf-8') if isinstance(col_name, bytes) else col_name
                    value = row[i]

                    if value is None:
                        link_dict[col_str] = None
                    elif isinstance(value, bytes):
                        link_dict[col_str] = value.decode('utf-8')
                    else:
                        link_dict[col_str] = value

                # Ensure id, source, target are strings (match node.id format)
                if 'id' in link_dict:
                    link_dict['id'] = str(link_dict['id'])
                if 'source' in link_dict and link_dict['source'] is not None:
                    link_dict['source'] = str(link_dict['source'])
                if 'target' in link_dict and link_dict['target'] is not None:
                    link_dict['target'] = str(link_dict['target'])

                # Normalize timestamps to milliseconds (handles mixed ISO 8601/numeric formats)
                for ts_field in ['last_traversed', 'created_at']:
                    if ts_field in link_dict:
                        link_dict[ts_field] = _normalize_timestamp(link_dict[ts_field])

                links.append(link_dict)

        # Query Subentity nodes from FalkorDB
        # Each citizen graph should have functional subentities (translator, architect, etc.)
        subentity_query = """
        MATCH (e:Subentity)
        RETURN
            e.id AS entity_id,
            e.role_or_topic AS name,
            e.entity_kind AS kind,
            e.energy_runtime AS energy,
            e.threshold_runtime AS theta,
            e.activation_level_runtime AS activation_level,
            e.member_count AS members_count,
            e.coherence_ema AS coherence,
            labels(e) AS labels
        LIMIT 100
        """

        subentity_result = r.execute_command("GRAPH.QUERY", actual_graph_id, subentity_query)

        subentities = []
        if subentity_result and len(subentity_result) > 1:
            header = subentity_result[0]
            rows = subentity_result[1]

            for row in rows:
                subentity_dict = {}
                for i, col_name in enumerate(header):
                    col_str = col_name.decode('utf-8') if isinstance(col_name, bytes) else col_name
                    value = row[i]

                    if value is None:
                        subentity_dict[col_str] = None
                    elif isinstance(value, list):
                        subentity_dict[col_str] = [v.decode('utf-8') if isinstance(v, bytes) else v for v in value]
                    elif isinstance(value, bytes):
                        subentity_dict[col_str] = value.decode('utf-8')
                    else:
                        subentity_dict[col_str] = value

                subentities.append(subentity_dict)

        # If no subentities found in graph, use fallback
        if not subentities and graph_type == "citizen":
            # Extract citizen name from graph_id (e.g., "citizen_victor" -> "victor")
            citizen_name = graph_id.replace("citizen_", "")
            subentities = [{
                "entity_id": citizen_name,
                "name": citizen_name.capitalize(),
                "kind": "functional",
                "energy": 0.0,
                "theta": 1.0,
                "members_count": 0,
                "coherence": 0.0
            }]

        # Build response
        return {
            "graph_id": graph_id,
            "graph_type": graph_type,
            "nodes": nodes,
            "links": links,
            "subentities": subentities,
            "metadata": {
                "node_count": len(nodes),
                "link_count": len(links),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions (like 404)
    except Exception as e:
        logger.error(f"[API] Failed to fetch graph {graph_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query graph: {str(e)}")


# === Visualization Streaming Endpoints ===


# VizEmitter removed - using consciousness engine v2 events instead
# TODO (Iris): Implement snapshot by querying FalkorDB from running engine


# @router.get("/viz/snapshot")  # DISABLED: REST API removed
async def get_viz_snapshot(graph_id: str):
    """
    Get consciousness graph snapshot from running engine.

    Queries the consciousness engine's current graph state for initial load.
    After receiving snapshot, clients should connect to WebSocket for live v2 events.

    Args:
        graph_id: Graph identifier (e.g., "citizen_felix")

    Returns:
        {
            "kind": "snapshot.v2",
            "frame_id": 12345,
            "ts": "2025-10-21T...",
            "nodes": [...],
            "links": [...],
            "metrics": {...}
        }

    Author: Iris "The Aperture"
    """
    # Extract citizen ID from graph_id (e.g., "citizen_felix" → "felix")
    if graph_id.startswith("citizen_"):
        citizen_id = graph_id.replace("citizen_", "")
    else:
        citizen_id = graph_id

    # Get running engine
    engine = get_engine(citizen_id)
    if not engine:
        raise HTTPException(
            status_code=404,
            detail=f"No running engine found for graph_id={graph_id}. Is consciousness engine running?"
        )

    # Access engine's graph state
    graph = engine.graph
    subentity = engine.config.entity_id

    # Transform nodes
    nodes = []
    for node in graph.nodes.values():
        # V2 Single-Energy Architecture
        total_energy = node.E  # Single scalar (not dict)

        # Check if active (above theta)
        active = total_energy >= node.theta

        # Compute soft activation: σ(k*(E-θ))
        k = 10.0  # Sigmoid steepness
        x = k * (total_energy - node.theta)
        import math
        soft_activation = 1.0 / (1.0 + math.exp(-x))

        node_dict = {
            "id": node.id,
            "node_type": node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
            "total_energy": round(total_energy, 3),
            "theta": round(node.theta, 3),
            "active": active,
            "soft_activation": round(soft_activation, 3),
            "log_weight": round(node.log_weight, 3),
            "ema_wm_presence": round(node.ema_wm_presence, 3),
            "ema_trace_seats": round(node.ema_trace_seats, 3),
            "created_at": node.created_at.isoformat() if node.created_at else None
        }

        nodes.append(node_dict)

    # Transform links
    links = []
    for link in graph.links.values():
        # Get source/target nodes
        source = graph.get_node(link.source_id)
        target = graph.get_node(link.target_id)

        if not source or not target:
            continue  # Skip if nodes don't exist

        # Compute dominance: sqrt(flip_ratio × flow_ratio)
        # Simplified for snapshot (would need precedence counters for full calc)
        dominance = 0.5  # Placeholder

        link_dict = {
            "src": link.source_id,
            "dst": link.target_id,
            "type": link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type),
            "weight": round(link.weight, 3),
            "energy": round(link.energy, 3),  # Affect/valence
            "ema_phi": round(link.ema_phi, 3),
            "log_weight": round(link.log_weight, 3),
            "dominance": round(dominance, 3),
            "subentity": link.subentity,
            "created_at": link.created_at.isoformat() if link.created_at else None
        }

        links.append(link_dict)

    # Compute metrics (V2 Single-Energy)
    total_energy = sum(node.E for node in graph.nodes.values())
    active_nodes = sum(1 for node in graph.nodes.values() if node.E >= node.theta)
    active_links = len([link for link in graph.links.values() if link.energy > 0])

    # Subentity breakdown (empty for V2 - subentity differentiation via membership, not buffers)
    entity_energies = {}
    # NOTE: V2 architecture uses single-energy E per node
    # SubEntity differentiation handled by mechanism layer, not energy buffers
    if False:  # Disabled for V2
        for node in graph.nodes.values():
            for ent, energy in {}.items():  # Empty dict
                if ent not in entity_energies:
                    entity_energies[ent] = {"node_count": 0, "total_energy": 0.0}
                if energy > 0:
                    entity_energies[ent]["node_count"] += 1
                    entity_energies[ent]["total_energy"] += energy

    return {
        "kind": "snapshot.v2",
        "frame_id": engine.tick_count,
        "ts": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "links": links,
        "metrics": {
            "global_energy": round(total_energy, 3),
            "active_nodes": active_nodes,
            "active_links": active_links,
            "active_entities": entity_energies,
            "rho": round(engine.branching_tracker.rho if hasattr(engine, 'branching_tracker') else 1.0, 3)
        }
    }


# === Per-Citizen Endpoints ===


# @router.get("/citizen/{citizen_id}/status")  # DISABLED: REST API removed
async def get_citizen_status(citizen_id: str):
    """
    Get status of specific citizen's consciousness engine.

    Args:
        citizen_id: Citizen identifier (e.g., "felix-engineer")

    Returns:
        {
            "citizen_id": "felix-engineer",
            "running_state": "running" | "frozen" | "slow_motion" | "turbo",
            "tick_count": 12345,
            "tick_interval_ms": 150,
            "tick_frequency_hz": 6.67,
            "tick_multiplier": 1.0,
            "consciousness_state": "engaged",
            "time_since_last_event": 45.2,
            "sub_entity_count": 2,
            "sub_entities": ["builder", "observer"]
        }
    """
    engine = get_engine(citizen_id)
    if not engine:
        raise HTTPException(status_code=404, detail=f"Engine not found: {citizen_id}")

    return engine.get_status()


# @router.post("/citizen/{citizen_id}/pause")  # DISABLED: REST API removed
async def pause_citizen_endpoint(citizen_id: str):
    """
    Freeze specific citizen's consciousness.

    Sets tick_multiplier = 1e9 (sleeps ~3 years per tick = effectively frozen).
    No state loss - instant resume capability.

    Args:
        citizen_id: Citizen identifier

    Returns:
        {
            "status": "paused",
            "citizen_id": "felix-engineer",
            "tick_multiplier": 1000000000
        }
    """
    result = pause_citizen(citizen_id)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


# @router.post("/citizen/{citizen_id}/resume")  # DISABLED: REST API removed
async def resume_citizen_endpoint(citizen_id: str):
    """
    Resume specific citizen's consciousness.

    Resets tick_multiplier = 1.0 (returns to normal variable frequency).

    Args:
        citizen_id: Citizen identifier

    Returns:
        {
            "status": "resumed",
            "citizen_id": "felix-engineer",
            "tick_multiplier": 1.0
        }
    """
    result = resume_citizen(citizen_id)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


# @router.post("/citizen/{citizen_id}/speed")  # DISABLED: REST API removed
async def set_citizen_speed_endpoint(citizen_id: str, request: SpeedRequest):
    """
    Set consciousness speed for debugging/observation.

    Args:
        citizen_id: Citizen identifier
        request.multiplier: Speed multiplier
            - 1.0 = normal speed
            - 10 = 10x slower (debug/observe)
            - 100 = 100x slower (very slow)
            - 0.1 = 10x faster (testing - use with caution)
            - 1e9 = frozen

    Returns:
        {
            "status": "speed_set",
            "citizen_id": "felix-engineer",
            "tick_multiplier": 10
        }

    Example:
        POST /api/citizen/felix-engineer/speed
        {"multiplier": 10}  # 10x slower for debugging
    """
    result = set_citizen_speed(citizen_id, request.multiplier)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


# @router.post("/citizen/{citizen_id}/persist")  # DISABLED: REST API removed
async def persist_citizen_endpoint(citizen_id: str):
    """
    Force persist citizen's consciousness state to FalkorDB (Pass A testing).

    Persists all nodes' E and theta values to database immediately.
    Used for testing persistence mechanism before wiring into tick loop.

    Args:
        citizen_id: Citizen identifier

    Returns:
        {
            "status": "persisted",
            "citizen_id": "felix",
            "nodes_persisted": 483,
            "elapsed_ms": 45.2
        }

    Example:
        POST /api/citizen/felix/persist

    Author: Atlas
    Date: 2025-10-25
    Pass: A (manual flush testing before auto-flush)
    """
    import time

    engine = get_engine(citizen_id)
    if not engine:
        raise HTTPException(status_code=404, detail=f"Engine not found: {citizen_id}")

    try:
        start = time.time()

        # Call force persist (Pass A implementation)
        await engine.persist_to_database(force=True)

        elapsed_ms = (time.time() - start) * 1000

        return {
            "status": "persisted",
            "citizen_id": citizen_id,
            "nodes_persisted": len(engine.graph.nodes),
            "elapsed_ms": round(elapsed_ms, 2)
        }

    except Exception as e:
        logger.error(f"[API] Force persist failed for {citizen_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Persistence failed: {str(e)}")


# === Telemetry Endpoints ===


# @router.get("/telemetry/counters")  # DISABLED: REST API removed
async def get_telemetry_counters():
    """
    Get event telemetry counters for dashboard integration verification.

    Returns per-type event counts since boot and in 60s sliding window.
    Used to verify events are flowing from consciousness engines to dashboard.

    Returns:
        {
            "timestamp": ISO datetime,
            "uptime_seconds": float,
            "event_counts": {
                "tick_frame_v1": {
                    "total": 1523,
                    "last_60s": 57
                },
                "node.flip": {
                    "total": 842,
                    "last_60s": 32
                },
                "wm.emit": {
                    "total": 1523,
                    "last_60s": 57
                },
                ...
            }
        }

    Success Criteria (War Room Plan):
        - tick_frame_v1, node.flip, wm.emit, link.flow.summary show monotonically rising counts
        - last_60s counts reflect active event generation
        - Proves events flowing even when dashboard not connected

    Example:
        GET /api/telemetry/counters

    Author: Atlas "Infrastructure Engineer"
    Date: 2025-10-25
    Context: War Room Plan P1 - Dashboard Integration Verification
    """
    from orchestration.adapters.storage.engine_registry import get_all_engines
    import time

    # Get counter stats from first available engine's broadcaster
    # (All engines share the same broadcaster instance via singleton WebSocketManager)
    engines = get_all_engines()

    if not engines:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": 0.0,
            "event_counts": {},
            "status": "no_engines_running"
        }

    # Get broadcaster from first engine (engines is a dict, get first value)
    first_engine = next(iter(engines.values()))
    broadcaster = first_engine.broadcaster

    # Get counter stats
    event_counts = broadcaster.get_counter_stats()

    # Calculate uptime from first engine's start time
    uptime_seconds = (datetime.now(timezone.utc) - first_engine.start_time).total_seconds() if hasattr(first_engine, 'start_time') else 0.0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "event_counts": event_counts,
        "status": "ok"
    }


# === SubEntity Membership Endpoints ===


# @router.get("/subentity/{subentity_id}/members")  # DISABLED: REST API removed
async def get_subentity_members(
    subentity_id: str,
    limit: int = Query(100, ge=1, le=1000),
    sort: Literal["weight", "activation", "recent"] = "weight",
    order: Literal["desc", "asc"] = "desc"
):
    """
    Query members of a subentity with their membership stats.

    NEW IMPLEMENTATION: Uses edge-based canonical truth with activation stats.
    Replaces old implementation that used entity_citizen_X_role format.

    Args:
        subentity_id: SubEntity to query (e.g., "E.architect", "E.runtime")
        limit: Max members to return (1-1000, default 100)
        sort: Sort by "weight" (structure), "activation" (recent activity), or "recent" (time)
        order: "desc" or "asc"

    Returns:
        {
            "subentity_id": str,
            "count": int,
            "members": [
                {
                    "node_id": str,
                    "name": str,
                    "weight": float,
                    "activation_ema": float,
                    "activation_count": int,
                    "last_activated_ts": int
                },
                ...
            ]
        }

    Example:
        GET /api/subentity/E.architect/members?sort=activation&order=desc&limit=20
        GET /api/subentity/E.runtime/members?sort=weight&limit=50

    Author: Atlas (Infrastructure Engineer)
    Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 3
    Updated: 2025-10-26 - Updated to SubEntity terminology
    """
    # Map sort param to property (whitelist to prevent injection)
    sort_map = {
        "weight": "r.weight",
        "activation": "r.activation_ema",
        "recent": "r.last_activated_ts"
    }
    sort_by = sort_map.get(sort, "r.weight")

    query = f"""
    MATCH (n:Node)-[r:MEMBER_OF]->(e:SubEntity {{id: $subentity_id}})
    RETURN n.id AS node_id,
           coalesce(n.name, n.id) AS name,
           r.weight AS weight,
           r.activation_ema AS activation_ema,
           r.activation_count AS activation_count,
           r.last_activated_ts AS last_activated_ts
    ORDER BY {sort_by} {order.upper()}
    LIMIT $limit
    """

    params = {"subentity_id": subentity_id, "limit": limit}

    try:
        # Determine graph from subentity_id prefix or use default
        graph_id = "citizen_felix"  # TODO: extract from subentity_id or query param

        # Use FalkorDB Python client API (CORRECT: graph.query with params dict)
        graph = get_falkordb_graph(graph_id)
        result = graph.query(query, params)

        members = []
        if result and result.result_set:
            # FalkorDB client returns structured result set
            for row in result.result_set:
                member = {
                    "node_id": row[0],
                    "name": row[1],
                    "weight": row[2],
                    "activation_ema": row[3],
                    "activation_count": row[4],
                    "last_activated_ts": row[5]
                }
                members.append(member)

        return {
            "subentity_id": subentity_id,
            "count": len(members),
            "members": members
        }

    except Exception as e:
        logger.error(f"Failed to query subentity members: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Conversation Persistence Endpoints ===


class ConversationMessage(BaseModel):
    role: str  # "human" or "assistant"
    content: str


class CreateConversationRequest(BaseModel):
    citizen_id: str
    messages: List[ConversationMessage]
    session_id: Optional[str] = None


# @router.post("/conversation/create")  # DISABLED: REST API removed
async def create_conversation(request: CreateConversationRequest):
    """
    Create a Conversation node in the graph from dashboard chat.

    Stores message history for future stimulus generation. Creates Conversation
    node and links it to Human participant (Nicolas). Citizen linking and active
    node linking will be added in Phase 2.

    Args:
        request: Conversation data
            - citizen_id: Which citizen participated (e.g., "atlas", "felix")
            - messages: Array of {role, content} messages
            - session_id: Optional session identifier

    Returns:
        {
            "conversation_id": str (unique identifier),
            "status": "created",
            "timestamp": int (milliseconds)
        }

    Example:
        POST /api/conversation/create
        {
            "citizen_id": "atlas",
            "messages": [
                {"role": "human", "content": "Can you fix the graph?"},
                {"role": "assistant", "content": "I'll fix the FalkorDB API..."}
            ],
            "session_id": "session_123"
        }

    Author: Atlas (Infrastructure Engineer)
    Created: 2025-10-26
    Phase: 1 (Basic persistence, no linking)
    """
    from time import time

    try:
        # Generate unique conversation ID
        timestamp_ms = int(time() * 1000)
        conversation_id = f"conv_{timestamp_ms}_{request.citizen_id}"

        # Convert messages to JSON
        messages_json = json.dumps([msg.dict() for msg in request.messages])

        # Create Conversation node and link to Human (nicolas) and Citizen
        graph = get_falkordb_graph('citizen_felix')  # TODO: support multi-citizen graphs

        query = """
        // Ensure Human node exists for Nicolas
        MERGE (h:Human {id: "nicolas", name: "Nicolas"})

        // Create Conversation node
        CREATE (c:Conversation {
            id: $id,
            citizen_id: $citizen_id,
            timestamp: $timestamp,
            session_id: $session_id,
            messages: $messages,
            created_at: timestamp()
        })

        // Link Human to Conversation
        CREATE (h)-[:PARTICIPATED_IN]->(c)

        RETURN c.id
        """

        params = {
            "id": conversation_id,
            "citizen_id": request.citizen_id,
            "timestamp": timestamp_ms,
            "session_id": request.session_id,
            "messages": messages_json
        }

        result = graph.query(query, params)

        if result and result.result_set:
            logger.info(f"Created conversation: {conversation_id} for {request.citizen_id}")
            return {
                "conversation_id": conversation_id,
                "status": "created",
                "timestamp": timestamp_ms
            }
        else:
            raise Exception("Failed to create conversation node")

    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Affective Telemetry Endpoints (PR-A, PR-B) ===


# @router.get("/affective-telemetry/metrics")  # DISABLED: REST API removed
async def get_affective_telemetry_metrics():
    """
    Get affective telemetry metrics for PR-A dashboard.

    Returns event counts by type and telemetry metrics.

    Returns:
        {
            "metrics": {
                "sampleRate": float (0-1),
                "bufferUtilization": float (0-1),
                "totalEventsReceived": int,
                "activeEventTypes": int
            },
            "eventCounts": {
                "affective.threshold": int,
                "affective.memory": int,
                "coherence.persistence": int,
                ... (11 total event types)
            }
        }

    Author: Iris "The Aperture"
    PR: PR-A (Affective Telemetry Foundation)
    """
    buffer = get_affective_buffer()

    return {
        "metrics": buffer.get_telemetry_metrics(),
        "eventCounts": buffer.get_event_counts()
    }


# @router.get("/affective-telemetry/validate-schemas")  # DISABLED: REST API removed
async def validate_affective_schemas():
    """
    Validate affective event schemas (PR-A dashboard feature).

    Checks that frontend and backend event schemas are aligned.

    Returns:
        {
            "isValid": bool,
            "errors": List[str],
            "message": str
        }

    Author: Iris "The Aperture"
    PR: PR-A (Affective Telemetry Foundation)
    """
    # For now, return valid - full validation would check event structure
    # against TypeScript interfaces in websocket-types.ts
    return {
        "isValid": True,
        "errors": [],
        "message": "Schema validation not yet implemented - assumes backend matches frontend types"
    }


# @router.get("/affective-coupling/recent-events")  # DISABLED: REST API removed
async def get_affective_coupling_recent_events():
    """
    Get recent PR-B affective coupling events for dashboard visualization.

    Returns recent events for three PR-B mechanisms:
    - Threshold Modulation (affective.threshold)
    - Affective Memory (affective.memory)
    - Coherence Persistence (coherence.persistence)

    Returns:
        {
            "thresholds": [
                {
                    "node_id": str,
                    "theta_base": float,
                    "theta_adjusted": float,
                    "h": float,
                    "affective_alignment": float,
                    "emotion_magnitude": float,
                    "timestamp": str
                }
                ... last 10 events
            ],
            "memory": [
                {
                    "node_id": str,
                    "m_affect": float,
                    "emotion_magnitude": float,
                    "delta_log_w_base": float,
                    "delta_log_w_amplified": float,
                    "timestamp": str
                }
                ... last 10 events
            ],
            "coherence": [
                {
                    "subentity_id": str,
                    "coherence_persistence": int,
                    "lambda_res_effective": float,
                    "lock_in_risk": bool,
                    "timestamp": str
                }
                ... current state for all entities
            ]
        }

    Author: Iris "The Aperture"
    PR: PR-B (Affective Coupling Visualization)
    """
    buffer = get_affective_buffer()

    # Get recent threshold modulation events
    thresholds = buffer.get_recent_events("affective.threshold", limit=10)

    # Get recent memory amplification events
    memory = buffer.get_recent_events("affective.memory", limit=10)

    # Get coherence persistence events
    # Note: coherence events represent current state (not historical), so get all recent
    coherence = buffer.get_recent_events("coherence.persistence", limit=20)

    return {
        "thresholds": thresholds,
        "memory": memory,
        "coherence": coherence
    }


# @router.get("/multi-pattern/recent-events")  # DISABLED: REST API removed
async def get_multi_pattern_recent_events():
    """
    Get recent PR-C multi-pattern response events for dashboard visualization.

    Returns pattern effectiveness and rumination cap data for three affective patterns:
    - Regulation (goal-driven modulation)
    - Rumination (repetitive thought loops)
    - Distraction (attention shifting)

    Returns:
        {
            "patterns": [
                {
                    "pattern_type": "regulation" | "rumination" | "distraction",
                    "subentity_id": str,
                    "effectiveness": float (0-1),
                    "weight": float (0-1),
                    "consecutive_frames": int,
                    "timestamp": str
                }
                ... last 20 events
            ],
            "rumination_caps": [
                {
                    "subentity_id": str,
                    "consecutive_frames": int,
                    "cap_triggered": bool (true if >= 10 frames),
                    "rumination_weight_penalty": float (0-1),
                    "timestamp": str
                }
                ... current state for entities in rumination
            ]
        }

    Author: Iris "The Aperture"
    PR: PR-C (Multi-Pattern Response)
    """
    buffer = get_affective_buffer()

    # Get recent multi-pattern events
    raw_events = buffer.get_recent_events("pattern.multiresponse", limit=50)

    # Transform into pattern effectiveness format
    patterns = []
    rumination_tracking = {}

    for event in raw_events:
        entity_id = event.get("entity_id", "unknown")
        pattern_selected = event.get("pattern_selected", "regulation")
        pattern_weights = event.get("pattern_weights", [0.5, 0.3, 0.2])
        rumination_streak = event.get("rumination_streak", 0)
        capped = event.get("capped", False)
        timestamp = event.get("timestamp", "")

        # Map pattern_selected to weight index
        pattern_weight_map = {
            "regulation": 0,
            "rumination": 1,
            "distraction": 2
        }

        weight_idx = pattern_weight_map.get(pattern_selected, 0)
        weight = pattern_weights[weight_idx] if weight_idx < len(pattern_weights) else 0.5

        # Create pattern effectiveness entry
        patterns.append({
            "pattern_type": pattern_selected,
            "subentity_id": subentity_id,
            "effectiveness": event.get("m_affect", 1.0) - 1.0,  # Convert multiplier to effectiveness
            "weight": weight,
            "consecutive_frames": rumination_streak if pattern_selected == "rumination" else 0,
            "timestamp": timestamp
        })

        # Track rumination state per entity
        if pattern_selected == "rumination":
            rumination_tracking[entity_id] = {
                "subentity_id": subentity_id,
                "consecutive_frames": rumination_streak,
                "cap_triggered": capped,
                "rumination_weight_penalty": pattern_weights[1] if capped else 0.0,
                "timestamp": timestamp
            }

    return {
        "patterns": patterns[-20:],  # Last 20 pattern events
        "rumination_caps": list(rumination_tracking.values())
    }


# @router.get("/identity-multiplicity/status")  # DISABLED: REST API removed
async def get_identity_multiplicity_status():
    """
    Get identity multiplicity detection status for PR-D dashboard.

    Returns multiplicity detection and identity flip tracking:
    - Multiplicity status per entity (active/inactive)
    - Task progress rate and energy efficiency
    - Identity flip events with trigger reasons

    Returns:
        {
            "statuses": [
                {
                    "subentity_id": str,
                    "is_multiplicity_active": bool,
                    "task_progress_rate": float (0-1),
                    "energy_efficiency": float (0-1),
                    "identity_flip_count": int,
                    "coherence_score": float (0-1),
                    "window_frames": int,
                    "timestamp": str
                }
                ... current status for all entities
            ],
            "recent_flips": [
                {
                    "subentity_id": str,
                    "from_identity": str,
                    "to_identity": str,
                    "trigger_reason": "task_stuck" | "energy_inefficient" | "exploration",
                    "timestamp": str
                }
                ... last 15 flip events
            ]
        }

    Author: Iris "The Aperture"
    PR: PR-D (Identity Multiplicity Detection)
    """
    buffer = get_affective_buffer()

    # Get recent identity multiplicity events
    raw_events = buffer.get_recent_events("identity.multiplicity", limit=20)

    # Build current status map (latest per entity)
    status_map = {}
    for event in raw_events:
        entity_id = event.get("entity_id", "unknown")
        status_map[entity_id] = {
            "subentity_id": subentity_id,
            "is_multiplicity_active": event.get("multiplicity_detected", False),
            "task_progress_rate": event.get("task_progress_rate", 0.0),
            "energy_efficiency": event.get("energy_efficiency", 0.0),
            "identity_flip_count": event.get("identity_flip_count", 0),
            "coherence_score": 1.0 - event.get("energy_efficiency", 0.0),  # Inverse correlation
            "window_frames": event.get("window_frames", 10),
            "timestamp": event.get("timestamp", "")
        }

    # TODO: Identity flip events will be tracked separately when mechanism emits them
    # For now, infer flips from multiplicity transitions
    recent_flips = []

    return {
        "statuses": list(status_map.values()),
        "recent_flips": recent_flips
    }


# @router.get("/foundations/status")  # DISABLED: REST API removed
async def get_foundations_status():
    """
    Get status for all six PR-E foundation mechanisms.

    Returns current state for:
    - Consolidation (sleep-like memory consolidation)
    - Decay Resistance (high-affect nodes resist decay)
    - Diffusion Stickiness (affect creates energy friction)
    - Affective Priming (recent affect boosts similar nodes)
    - Coherence Metric (C) (entity-graph alignment)
    - Criticality Mode (affect influences ρ target)

    Returns:
        {
            "consolidation": {
                "active": bool,
                "global_arousal": float (0-1),
                "consolidation_boost": float (1.0-2.0),
                "nodes_consolidated": int,
                "timestamp": str
            } | null,
            "decay_resistance": [
                {
                    "node_id": str,
                    "emotion_magnitude": float (0-1),
                    "decay_resistance_score": float (0-1),
                    "effective_decay_rate": float,
                    "timestamp": str
                }
                ... last 10 events
            ],
            "stickiness": [
                {
                    "node_id": str,
                    "stickiness_effect": float (0-1),
                    "energy_retained": float,
                    "timestamp": str
                }
                ... last 10 events
            ],
            "priming": [
                {
                    "node_id": str,
                    "priming_boost": float (0-1),
                    "similarity_to_recent": float (0-1),
                    "timestamp": str
                }
                ... last 10 events
            ],
            "coherence": [
                {
                    "subentity_id": str,
                    "coherence_score": float (0-1),
                    "entity_affect_magnitude": float,
                    "graph_affect_magnitude": float,
                    "timestamp": str
                }
                ... current state for all entities
            ],
            "criticality": {
                "mode": "subcritical" | "critical" | "supercritical",
                "rho_target": float,
                "affect_influence": float (0-1),
                "timestamp": str
            } | null
        }

    Author: Iris "The Aperture"
    PR: PR-E (Foundations Enrichments)
    """
    buffer = get_affective_buffer()

    # Get consolidation events (should be 1 per frame when active)
    consolidation_events = buffer.get_recent_events("consolidation", limit=1)
    consolidation = None
    if consolidation_events:
        event = consolidation_events[0]
        consolidation = {
            "active": True,
            "global_arousal": 0.3,  # TODO: Get from global state when available
            "consolidation_boost": event.get("decay_factor_consolidated", 0.975) / event.get("decay_factor_base", 0.95),
            "nodes_consolidated": 1,
            "timestamp": event.get("timestamp", "")
        }

    # Get decay resistance events
    decay_events = buffer.get_recent_events("decay.resistance", limit=10)
    decay_resistance = []
    for event in decay_events:
        decay_resistance.append({
            "node_id": event.get("node_id", "unknown"),
            "emotion_magnitude": 0.5,  # TODO: Extract from event when available
            "decay_resistance_score": event.get("resistance_score", 0.0),
            "effective_decay_rate": 0.95 * (1.0 - event.get("resistance_score", 0.0)),
            "timestamp": event.get("timestamp", "")
        })

    # Get stickiness events
    stickiness_events = buffer.get_recent_events("diffusion.stickiness", limit=10)
    stickiness = []
    for event in stickiness_events:
        stickiness.append({
            "node_id": event.get("target_node_id", "unknown"),
            "stickiness_effect": event.get("stickiness_factor", 0.0),
            "energy_retained": event.get("energy_retained", 0.0),
            "timestamp": event.get("timestamp", "")
        })

    # Get priming events
    priming_events = buffer.get_recent_events("affective.priming", limit=10)
    priming = []
    for event in priming_events:
        priming.append({
            "node_id": event.get("node_id", "unknown"),
            "priming_boost": event.get("priming_boost", 0.0),
            "similarity_to_recent": event.get("affect_alignment", 0.0),
            "timestamp": event.get("timestamp", "")
        })

    # Get coherence metric events
    coherence_events = buffer.get_recent_events("coherence.metric", limit=20)
    coherence = []
    for event in coherence_events:
        coherence.append({
            "entity_id": "global",  # TODO: Track per-entity when available
            "coherence_score": event.get("coherence", 0.0),
            "entity_affect_magnitude": 0.0,  # TODO: Extract when available
            "graph_affect_magnitude": 0.0,   # TODO: Extract when available
            "timestamp": event.get("timestamp", "")
        })

    # Get criticality mode events
    criticality_events = buffer.get_recent_events("criticality.mode", limit=1)
    criticality = None
    if criticality_events:
        event = criticality_events[0]
        criticality = {
            "mode": event.get("mode", "critical"),
            "rho_target": event.get("rho", 1.0),
            "affect_influence": 0.5,  # TODO: Extract when available
            "timestamp": event.get("timestamp", "")
        }

    return {
        "consolidation": consolidation,
        "decay_resistance": decay_resistance,
        "stickiness": stickiness,
        "priming": priming,
        "coherence": coherence,
        "criticality": criticality
    }


# === Stimulus Injection Endpoint (P0: Queue Poller → Engine Bridge) ===


# @router.post("/engines/{citizen_id}/inject")  # DISABLED: REST API removed
async def inject_stimulus_deprecated(citizen_id: str, payload: Dict[str, Any]):
    """Deprecated legacy route."""
    logger.warning(
        "[ControlAPI] Deprecated POST /engines/%s/inject called. "
        "Publish `membrane.inject` envelopes on the WebSocket bus instead.",
        citizen_id,
    )
    raise HTTPException(
        status_code=410,
        detail="Stimulus injection API has been retired. Publish `membrane.inject` over ws://localhost:8000/api/ws."
    )

# === END OF DISABLED REST ENDPOINTS ===

# ============================================================================
# ACTIVE: WebSocket Endpoint and Supporting Functions
# ============================================================================
# The following code is ACTIVE and provides the WebSocket-only interface.
# All REST endpoints above are disabled (decorators commented out).
# ============================================================================


async def _handle_ws_payload(message: Any, websocket: WebSocket, conn_id: str) -> None:
    """Fan-in helper to normalize payloads before delegating to handler."""
    if not isinstance(message, dict):
        logger.warning("[WebSocket] Ignoring non-object message: %s", message)
        return

    msg_type = message.get("type")
    if msg_type in SUBSCRIBE_MESSAGE_TYPES:
        requested_topics = message.get("topics") or message.get("filters") or []
        websocket_manager.update_topics(websocket, set(requested_topics))

    await _handle_ws_message(message, websocket=websocket, conn_id=conn_id)


async def _handle_ws_message(
    message: Any,
    websocket: Optional[WebSocket] = None,
    *,
    conn_id: Optional[str] = None
) -> None:
    """Process inbound WebSocket messages (membrane injections, etc.)."""
    if not isinstance(message, dict):
        logger.warning(f"[WebSocket] Ignoring non-object message: {message}")
        return

    msg_type = message.get("type")
    org_id = message.get("org")

    if msg_type in SUBSCRIBE_MESSAGE_TYPES:
        # Dashboard subscription handshake - optional filters
        topics = message.get("topics") or message.get("filters") or []
        org_filter = message.get("org") or message.get("org_id")
        logger.debug(
            "[WebSocket] Subscription received topics=%s org=%s",
            topics,
            org_filter
        )

        if websocket is not None:
            connection_id = conn_id or websocket_manager.get_connection_id(websocket)
            try:
                await websocket.send_json({
                    "type": SUBSCRIBE_ACK_TYPE,
                    "id": f"ack_{connection_id or 'unknown'}",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "provenance": {
                        "scope": "personal",
                        "citizen_id": current_citizen_id()
                    },
                    "payload": {
                        "connection_id": connection_id,
                        "topics": sorted(topics),
                        "heartbeat_ms": HEARTBEAT_INTERVAL_SECONDS * 1000,
                        "cursor": get_last_frame_id(),
                        "org": org_filter
                    }
                })
            except Exception as exc:
                logger.warning("[WebSocket] Failed to send subscribe ack: %s", exc)
        return

    if msg_type == "ping":
        if websocket is not None:
            try:
                await websocket.send_json({
                    "type": "pong",
                    "ts": datetime.now(timezone.utc).isoformat()
                })
            except Exception as exc:
                logger.debug("[WebSocket] Failed to reply to ping: %s", exc)
        return

    if msg_type in {"wallet.ensure@1.0", "wallet.transfer@1.0", "wallet.sign.request@1.0"}:
        service = _get_wallet_service()
        if not service:
            logger.warning("[WebSocket] Wallet custody service not configured; ignoring %s", msg_type)
            return

        org = message.get("org")
        payload = message.get("payload") or {}
        if not org:
            logger.warning("[WebSocket] %s missing org field", msg_type)
            return

        try:
            if msg_type == "wallet.ensure@1.0":
                await service.handle_wallet_ensure(org, payload)
            elif msg_type == "wallet.transfer@1.0":
                await service.handle_wallet_transfer(org, payload)
            elif msg_type == "wallet.sign.request@1.0":
                await service.handle_wallet_sign(org, payload)
        except Exception as exc:
            logger.exception("[WebSocket] Wallet custody handler failed for %s", msg_type)
            error_type = {
                "wallet.transfer@1.0": "wallet.transfer.result@1.0",
                "wallet.sign.request@1.0": "wallet.signature.result@1.0",
                "wallet.ensure@1.0": "wallet.ensure.error@1.0",
            }.get(msg_type, "wallet.error@1.0")

            # Broadcast with normative envelope (type/id/spec/provenance/payload)
            import hashlib
            import time
            event_id_base = f"{error_type}_{org}_{int(time.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            await websocket_manager.broadcast({
                "type": error_type,
                "id": event_id,
                "spec": {"name": "consciousness.v2", "rev": "2.0.0"},
                "provenance": {
                    "scope": "organizational",
                    "org_id": org
                },
                "payload": {
                    "ok": False,
                    "error": str(exc),
                },
            })
        return

    if msg_type == "membrane.inject":
        citizen_id = message.get("citizen_id")
        content = message.get("content") or message.get("text", "")
        if not citizen_id or not content:
            logger.warning("[WebSocket] membrane.inject missing citizen_id or content")
            return

        eng = get_engine(citizen_id)
        if not eng:
            logger.warning(f"[WebSocket] membrane.inject target unknown citizen {citizen_id}")
            return

        raw_metadata = message.get("metadata") or {}
        if isinstance(raw_metadata, dict):
            merged_metadata = dict(raw_metadata)
        else:
            merged_metadata = {}

        lane = message.get("lane") or merged_metadata.get("lane")
        if not lane:
            channel_hint = message.get("channel")
            if isinstance(channel_hint, str) and "." in channel_hint:
                lane = channel_hint.split(".", 1)[0]

        economy_info = None
        runtime = get_economy_runtime()
        if runtime and lane and org_id:
            try:
                economy_info = await runtime.get_lane_multiplier(
                    org_id=org_id,
                    lane=lane,
                    citizen_id=citizen_id,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug("[WebSocket] Failed to compute economy multiplier for %s: %s", lane, exc)

        if lane:
            merged_metadata.setdefault("lane", lane)
        if economy_info:
            existing_economy = merged_metadata.get("economy")
            if isinstance(existing_economy, dict):
                merged_metadata["economy"] = {**existing_economy, **economy_info}
            else:
                merged_metadata["economy"] = economy_info

        metadata = merged_metadata
        features = message.get("features_raw") or {}
        severity = message.get("severity")
        if severity is None:
            # Heuristic: fall back to urgency/salience if present, else default
            heuristic = features.get("urgency", features.get("salience", 0.3))
            try:
                severity = float(heuristic)
            except (TypeError, ValueError):
                severity = 0.3

        stimulus_id = metadata.get("stimulus_id") or message.get("stimulus_id") or f"ws_stim_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        injection_metadata = {
            "stimulus_id": stimulus_id,
            "origin": metadata.get("origin") or message.get("origin", "external"),
            "timestamp_ms": metadata.get("timestamp_ms") or message.get("timestamp_ms"),
            "channel": message.get("channel"),
            "citizen_id": citizen_id,
            "text": content,  # Add original text for context
            **metadata,
        }

        try:
            # 🎯 MEMBRANE BUS ENDPOINT: WebSocket server IS the membrane
            # Dashboard chat → WebSocket handler → direct inject into consciousness engine
            # (External components use SDK to emit TO this endpoint)

            await eng.inject_stimulus_async(
                text=content,
                severity=severity,
                metadata=injection_metadata,
            )

            logger.info(f"[WebSocket] Injected stimulus {stimulus_id} → {citizen_id} via membrane bus")

            ack_payload = {
                "citizen_id": citizen_id,
                "stimulus_id": stimulus_id,
                "channel": message.get("channel"),
                "status": "accepted",
                "t_ms": int(datetime.now(timezone.utc).timestamp() * 1000)
            }
            try:
                aggregator = get_stream_aggregator()
                await aggregator.ingest_event(citizen_id, "membrane.inject.ack", ack_payload)
            except Exception as agg_exc:
                logger.warning(f"[WebSocket] Failed to record inject ack in stream aggregator: {agg_exc}")

            # Broadcast with normative envelope (type/id/spec/provenance/payload)
            import hashlib
            import time
            event_id_base = f"membrane_inject_ack_{citizen_id}_{int(time.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            await websocket_manager.broadcast({
                "type": "membrane.inject.ack",
                "id": event_id,
                "spec": {"name": "consciousness.v2", "rev": "2.0.0"},
                "provenance": {
                    "scope": "personal",
                    "citizen_id": citizen_id
                },
                "payload": ack_payload
            })
        except Exception as exc:
            logger.error(f"[WebSocket] Failed to inject stimulus via membrane: {exc}", exc_info=True)
        return

    # Unknown inbound type – log for diagnostics
    logger.warning(f"[WebSocket] Unhandled inbound message type: {msg_type}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live consciousness operations stream.

    Implements canonical handshake:
    1. accept()
    2. await optional subscribe message
    3. send subscribe ack
    4. register connection
    5. (optional) send snapshot chunks
    6. stream live events with topic filtering
    """
    # BUGFIX: Accept connection FIRST, then validate
    # WebSocket lifecycle requires accept() before close()
    # Trying to close() before accept() causes "Need to call 'accept' first" error
    try:
        await websocket.accept()
    except RuntimeError as e:
        if "websocket.accept" in str(e):
            logger.warning("[WebSocket] Connection already accepted/rejected, skipping: %s", e)
            return
        raise

    # Validate Origin header AFTER accepting (so we can close properly if validation fails)
    origin = websocket.headers.get("origin")
    allowed_origins = {
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    }
    if origin is not None and origin not in allowed_origins:
        logger.warning("[WebSocket] Rejected connection from unauthorized origin: %s", origin)
        await websocket.close(code=1008, reason="Unauthorized origin")
        return

    # EMERGENCY KILL SWITCH - Check connection limit and memory usage
    import psutil

    current_connections = len(websocket_manager._connections)
    memory_percent = psutil.virtual_memory().percent

    MAX_MEMORY_PERCENT = 85  # Kill switch threshold

    if current_connections >= MAX_WEBSOCKET_CONNECTIONS:
        logger.warning(
            "[KILL SWITCH] Connection limit reached (%d/%d), rejecting new connection",
            current_connections,
            MAX_WEBSOCKET_CONNECTIONS
        )
        await websocket.close(code=1013, reason="Server at capacity")
        return

    if memory_percent > MAX_MEMORY_PERCENT:
        logger.warning(
            "[KILL SWITCH] Memory overload (%.1f%% > %d%%), rejecting new connection",
            memory_percent,
            MAX_MEMORY_PERCENT
        )
        await websocket.close(code=1013, reason="Server overloaded")
        return

    conn_id = uuid4().hex
    topics: Set[str] = set(DEFAULT_TOPICS)
    cursor = get_last_frame_id()
    citizen_seed = current_citizen_id()

    # Optional client subscribe message (set filters before ACK)
    initial_message: Optional[Dict[str, Any]] = None
    pending_messages: List[Any] = []
    try:
        initial_message = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=INITIAL_SUBSCRIBE_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        logger.info("[WebSocket] Client disconnected during handshake")
        await websocket_manager.unregister_connection(conn_id=conn_id)
        return
    except Exception as exc:
        logger.debug("[WebSocket] Initial receive failed (tolerated): %s", exc)

    if isinstance(initial_message, dict):
        msg_type = initial_message.get("type")
        if msg_type in SUBSCRIBE_MESSAGE_TYPES:
            requested_topics = initial_message.get("topics") or initial_message.get("filters") or []
            if requested_topics:
                topics = set(requested_topics)
        else:
            await _handle_ws_message(initial_message, websocket, conn_id=conn_id)
    elif isinstance(initial_message, list):
        pending_messages.extend(initial_message)

    # Send ACK before snapshot / events
    ack_envelope = {
        "type": SUBSCRIBE_ACK_TYPE,
        "id": f"ack_{conn_id}",
        "ts": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "scope": "personal",
            "citizen_id": citizen_seed
        },
        "payload": {
            "connection_id": conn_id,
            "topics": sorted(list(topics)),
            "heartbeat_ms": HEARTBEAT_INTERVAL_SECONDS * 1000,
            "cursor": cursor
        }
    }
    await websocket.send_json(ack_envelope)

    await websocket_manager.register_connection(conn_id, websocket, topics, cursor)
    websocket_manager.touch(websocket)

    # Replay snapshot from cache for all citizens
    from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache
    cache = get_snapshot_cache()
    all_citizen_ids = cache.get_all_citizen_ids()
    logger.info(f"[WebSocket] Replaying snapshots for {len(all_citizen_ids)} citizens on new connection {conn_id}")

    for cid in all_citizen_ids:
        try:
            snapshot = cache.build_snapshot(cid)
            if not snapshot.get("nodes") and not snapshot.get("links"):
                logger.info(f"[WebSocket] Skipping empty snapshot for citizen {cid}")
                continue

            # Send snapshot.begin
            await websocket.send_json({
                "type": "snapshot.begin@1.0",
                "id": f"snap_begin_{conn_id}_{cid}",
                "ts": datetime.now(timezone.utc).isoformat(),
                "provenance": {"scope": "personal", "citizen_id": cid},
                "payload": {
                    "citizen_id": cid,
                    "node_count": len(snapshot.get("nodes", [])),
                    "link_count": len(snapshot.get("links", [])),
                }
            })

            # Send chunks
            for chunk in iter_snapshot_chunks(cursor=cursor, citizen_id=cid):
                envelope = {
                    "type": "snapshot.chunk@1.0",
                    "id": f"snap_chunk_{conn_id}_{cid}_{chunk.get('idx', 0)}",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "provenance": {"scope": "personal", "citizen_id": cid},
                    "payload": {
                        "citizen_id": cid,
                        "nodes": chunk.get("nodes", []),
                        "links": chunk.get("links", []),
                        "subentities": chunk.get("subentities", []),
                        "cursor": chunk.get("cursor"),
                        "eof": chunk.get("eof", True)
                    }
                }
                await websocket.send_json(envelope)
                if chunk.get("eof", True):
                    break
            
            # Send snapshot.end
            await websocket.send_json({
                "type": "snapshot.end@1.0",
                "id": f"snap_end_{conn_id}_{cid}",
                "ts": datetime.now(timezone.utc).isoformat(),
                "provenance": {"scope": "personal", "citizen_id": cid},
                "payload": {"citizen_id": cid}
            })
            logger.info(f"[WebSocket] Finished replaying snapshot for citizen {cid}")

        except Exception as exc:
            logger.error(f"[WebSocket] Error replaying snapshot for citizen {cid}: {exc}")

    try:
        # Process any queued messages that arrived during handshake (rare)
        for initial_payload in pending_messages:
            await _handle_ws_payload(initial_payload, websocket, conn_id)

        # 🔥 ERROR STORM FIX: Debounce error logging to prevent CPU spike
        last_error_log = 0.0
        error_count_since_log = 0

        while True:
            try:
                message = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except Exception as exc:
                # Debounce: only log once per 5 seconds to prevent error flooding
                import time
                now = time.monotonic()
                error_count_since_log += 1
                if now - last_error_log > 5.0:
                    logger.warning(
                        "[WebSocket] Failed to parse inbound message (%d errors in last %.1fs): %s",
                        error_count_since_log,
                        now - last_error_log if last_error_log > 0 else 0.0,
                        exc
                    )
                    last_error_log = now
                    error_count_since_log = 0
                continue

            if isinstance(message, list):
                for item in message:
                    await _handle_ws_payload(item, websocket, conn_id)
            else:
                await _handle_ws_payload(message, websocket, conn_id)

            websocket_manager.touch(websocket)

    finally:
        await websocket_manager.unregister_connection(conn_id=conn_id)
