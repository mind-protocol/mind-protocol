"""
Consciousness Control API

REST endpoints for controlling consciousness engines via dashboard.
Implements "ICE" solution - freeze/slow/resume via tick_multiplier.

Integration:
    from orchestration.adapters.api.control_api import router, websocket_manager
    app.include_router(router)  # Add to FastAPI app

Endpoints:
    GET  /api/consciousness/status                 - All engines status
    POST /api/consciousness/pause-all              - Emergency freeze all
    POST /api/consciousness/resume-all             - Resume all
    POST /api/citizen/{citizen_id}/pause           - Freeze one citizen
    POST /api/citizen/{citizen_id}/resume          - Resume one citizen
    POST /api/citizen/{citizen_id}/speed           - Set speed (slow/turbo)
    GET  /api/citizen/{citizen_id}/status          - Get citizen status
    WS   /ws                                       - Live operations stream
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
import json
import logging
from datetime import datetime, timezone

from orchestration.adapters.storage.engine_registry import (
    pause_citizen,
    resume_citizen,
    set_citizen_speed,
    pause_all,
    resume_all,
    get_system_status,
    get_engine
)
from orchestration.mechanisms.affective_telemetry_buffer import get_affective_buffer
from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph
from orchestration.adapters.ws.stream_aggregator import get_stream_aggregator
from orchestration.services.economy.runtime import get_runtime as get_economy_runtime

try:  # Wallet custody service is optional until configured
    from orchestration.services.wallet_custody.config import WalletCustodySettings
    from orchestration.services.wallet_custody.service import WalletCustodyService
except Exception:  # pragma: no cover - service not configured
    WalletCustodyService = None  # type: ignore[assignment]

# Configure logging
logger = logging.getLogger(__name__)


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

class WebSocketManager:
    """
    Manages WebSocket connections for live consciousness operations stream.

    Singleton pattern - all mechanisms broadcast through this manager.
    Dashboard connects to /ws endpoint to receive real-time events.
    """

    def __init__(self):
        """Initialize WebSocket manager with empty connections list."""
        self.active_connections: List[WebSocket] = []
        logger.info("[WebSocketManager] Initialized")

    async def connect(self, websocket: WebSocket):
        """
        Accept new WebSocket connection with Origin validation.

        Args:
            websocket: WebSocket connection to add

        Security:
            Validates Origin header to prevent unauthorized cross-origin WebSocket connections.
            Browsers send Origin during upgrade handshake - must be validated before accept().
        """
        # Validate Origin header (browsers send this, Python clients may not)
        origin = websocket.headers.get("origin")
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002"
        ]

        # If Origin present, must be in allowed list
        if origin is not None and origin not in allowed_origins:
            logger.warning(f"[WebSocketManager] Rejected connection from unauthorized origin: {origin}")
            await websocket.close(code=1008)  # Policy violation
            return

        await websocket.accept()
        self.active_connections.append(websocket)
        origin_str = f"from {origin}" if origin else "(no origin header)"
        logger.info(f"[WebSocketManager] Client connected {origin_str} (total: {len(self.active_connections)})")

    async def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[WebSocketManager] Client disconnected (total: {len(self.active_connections)})")

    async def broadcast(self, event: Dict[str, Any]):
        """
        Broadcast event to all connected clients AND buffer for telemetry.

        Args:
            event: Event dict with 'type' and event-specific data

        Event types:
            - entity_activity: SubEntity exploration updates
            - threshold_crossing: Node activation changes
            - consciousness_state: Global system state updates
            - node_activation: Individual node activity changes
            - link_traversal: Link traversal events
        """
        # CRITICAL FIX: Buffer for telemetry FIRST, before checking connections
        # This ensures telemetry works even when no dashboard watching
        event_type = event.get("type", "")
        if event_type in TELEMETRY_EVENT_TYPES:
            try:
                from orchestration.mechanisms.affective_telemetry_buffer import get_affective_buffer
                buffer = get_affective_buffer()
                buffer.add_event(event_type, event)
                logger.debug(f"[WebSocketManager] Buffered {event_type} for telemetry")
            except Exception as e:
                logger.error(f"[WebSocketManager] Failed to buffer telemetry: {e}")

        # THEN check WebSocket connections
        if not self.active_connections:
            logger.debug(f"[WebSocketManager] Broadcast attempted but no clients connected (event: {event_type}) - buffered anyway")
            return  # No clients connected, skip WebSocket broadcast

        logger.debug(f"[WebSocketManager] Broadcasting {event_type} to {len(self.active_connections)} clients")

        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()

        message = json.dumps(event)

        # Broadcast to all connections (handle disconnects gracefully)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.exception(f"[WebSocketManager] Failed to send to client ({type(e).__name__}): {e}")
                disconnected.append(connection)

        # Remove failed connections
        for connection in disconnected:
            await self.disconnect(connection)


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


@router.get("/ping")
async def ping():
    """Health check endpoint to verify Control API router is mounted."""
    return {"ok": True}


class SpeedRequest(BaseModel):
    """Request body for speed control."""
    multiplier: float


# === System-Wide Endpoints ===


@router.get("/consciousness/status")
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


@router.get("/consciousness/constant-debt")
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


@router.post("/consciousness/pause-all")
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


@router.post("/consciousness/resume-all")
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


@router.get("/graphs")
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


@router.get("/search/semantic")
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


@router.get("/ecosystems")
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


@router.get("/ecosystem/{ecosystem_slug}/graphs")
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


@router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}/graphs")
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


@router.get("/ecosystem/{ecosystem_slug}")
async def get_ecosystem_graph_hierarchy(ecosystem_slug: str):
    """Hierarchical Niveau route for ecosystem-level graph snapshots."""
    graph_id = _build_graph_name(ecosystem_slug)
    return await get_graph_data(graph_type='ecosystem', graph_id=graph_id)


@router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}")
async def get_organization_graph_hierarchy(ecosystem_slug: str, organization_slug: str):
    """Hierarchical Niveau route for organization graphs nested under an ecosystem."""
    graph_id = _build_graph_name(ecosystem_slug, organization_slug)
    return await get_graph_data(graph_type='organization', graph_id=graph_id)


@router.get("/ecosystem/{ecosystem_slug}/organization/{organization_slug}/citizen/{citizen_slug}")
async def get_citizen_graph_hierarchy(ecosystem_slug: str, organization_slug: str, citizen_slug: str):
    """Hierarchical Niveau route for citizen graphs nested under org + ecosystem."""
    graph_id = _build_graph_name(ecosystem_slug, organization_slug, citizen_slug)
    return await get_graph_data(graph_type='citizen', graph_id=graph_id)


@router.get("/graph/{graph_type}/{graph_id}")
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


@router.get("/viz/snapshot")
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


@router.get("/citizen/{citizen_id}/status")
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


@router.post("/citizen/{citizen_id}/pause")
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


@router.post("/citizen/{citizen_id}/resume")
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


@router.post("/citizen/{citizen_id}/speed")
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


@router.post("/citizen/{citizen_id}/persist")
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


@router.get("/telemetry/counters")
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


@router.get("/subentity/{subentity_id}/members")
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


@router.post("/conversation/create")
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


@router.get("/affective-telemetry/metrics")
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


@router.get("/affective-telemetry/validate-schemas")
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


@router.get("/affective-coupling/recent-events")
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


@router.get("/multi-pattern/recent-events")
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


@router.get("/identity-multiplicity/status")
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


@router.get("/foundations/status")
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


@router.post("/engines/{citizen_id}/inject")
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


# === WebSocket Endpoint ===


async def _handle_ws_message(message: Any):
    """Process inbound WebSocket messages (membrane injections, etc.)."""
    if not isinstance(message, dict):
        logger.warning(f"[WebSocket] Ignoring non-object message: {message}")
        return

    msg_type = message.get("type")
    org_id = message.get("org")

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
            await websocket_manager.broadcast({
                "type": error_type,
                "org": org,
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
            **metadata,
        }

        try:
            await eng.inject_stimulus_async(
                text=content,
                severity=severity,
                metadata=injection_metadata,
            )
            ack_payload = {
                "citizen_id": citizen_id,
                "stimulus_id": stimulus_id,
                "channel": message.get("channel"),
                "t_ms": int(datetime.now(timezone.utc).timestamp() * 1000)
            }
            try:
                aggregator = get_stream_aggregator()
                await aggregator.ingest_event(citizen_id, "membrane.inject.ack", ack_payload)
            except Exception as agg_exc:
                logger.warning(f"[WebSocket] Failed to record inject ack in stream aggregator: {agg_exc}")

            await websocket_manager.broadcast({"type": "membrane.inject.ack", **ack_payload})
        except Exception as exc:
            logger.error(f"[WebSocket] Failed to inject stimulus via membrane: {exc}", exc_info=True)
        return

    # Unknown inbound type – log for diagnostics
    logger.warning(f"[WebSocket] Unhandled inbound message type: {msg_type}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live consciousness operations stream.

    Dashboard connects here to receive real-time events:
    - entity_activity: SubEntity exploration updates
    - threshold_crossing: Node activation changes
    - consciousness_state: Global system state updates
    - node_activation: Individual node activity changes
    - link_traversal: Link traversal events

    Example client (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/api/ws');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.type, data);
        };

    Event format:
        {
            "type": "entity_activity",
            "timestamp": "2025-10-18T21:30:45.123Z",
            "data": {...}
        }
    """
    await websocket_manager.connect(websocket)

    try:
        # Keep connection alive - wait for client messages (if any)
        while True:
            raw = await websocket.receive_text()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(f"[WebSocket] Received non-JSON payload: {raw}")
                continue

            # Allow batching (array of events) or single object
            if isinstance(parsed, list):
                for item in parsed:
                    await _handle_ws_message(item)
            else:
                await _handle_ws_message(parsed)

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
        logger.info("[WebSocket] Client disconnected normally")

    except Exception as e:
        logger.error(f"[WebSocket] Connection error: {e}")
        await websocket_manager.disconnect(websocket)
