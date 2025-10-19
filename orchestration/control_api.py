"""
Consciousness Control API

REST endpoints for controlling consciousness engines via dashboard.
Implements "ICE" solution - freeze/slow/resume via tick_multiplier.

Integration:
    from orchestration.control_api import router, websocket_manager
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

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from orchestration.engine_registry import (
    pause_citizen,
    resume_citizen,
    set_citizen_speed,
    pause_all,
    resume_all,
    get_system_status,
    get_engine
)

# Configure logging
logger = logging.getLogger(__name__)


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
        Accept new WebSocket connection.

        Args:
            websocket: WebSocket connection to add
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WebSocketManager] Client connected (total: {len(self.active_connections)})")

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
        Broadcast event to all connected clients.

        Args:
            event: Event dict with 'type' and event-specific data

        Event types:
            - entity_activity: SubEntity exploration updates
            - threshold_crossing: Node activation changes
            - consciousness_state: Global system state updates
            - node_activation: Individual node activity changes
            - link_traversal: Link traversal events
        """
        if not self.active_connections:
            return  # No clients connected, skip broadcast

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
                logger.error(f"[WebSocketManager] Failed to send to client: {e}")
                disconnected.append(connection)

        # Remove failed connections
        for connection in disconnected:
            await self.disconnect(connection)


# Global singleton instance
websocket_manager = WebSocketManager()

# Create router
router = APIRouter(prefix="/api", tags=["consciousness-control"])


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
                    "arousal": 0.8,
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

        # Verify graph exists
        all_graphs = r.execute_command("GRAPH.LIST")
        if graph_id not in all_graphs:
            raise HTTPException(status_code=404, detail=f"Graph not found: {graph_id}")

        # Query all nodes
        # Return node properties we care about for visualization
        # NOTE: BaseNode uses 'name' not 'node_id', and node_type comes from labels
        node_query = """
        MATCH (n)
        RETURN
            id(n) AS id,
            n.name AS node_id,
            labels(n) AS labels,
            CASE
                WHEN size(labels(n)) > 0 THEN labels(n)[0]
                ELSE null
            END AS node_type,
            n.description AS text,
            n.confidence AS confidence,
            n.last_active AS last_active,
            n.traversal_count AS traversal_count
        LIMIT 1000
        """

        node_result = r.execute_command("GRAPH.QUERY", graph_id, node_query)

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

                nodes.append(node_dict)

        # Query all links
        # NOTE: Nodes use 'name' not 'node_id' for identification
        link_query = """
        MATCH (a)-[r]->(b)
        RETURN
            id(r) AS id,
            a.name AS source,
            b.name AS target,
            type(r) AS type,
            r.confidence AS strength,
            r.last_traversed AS last_traversed
        LIMIT 5000
        """

        link_result = r.execute_command("GRAPH.QUERY", graph_id, link_query)

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

                # Ensure id is string
                if 'id' in link_dict:
                    link_dict['id'] = str(link_dict['id'])

                links.append(link_dict)

        # Build response
        return {
            "graph_id": graph_id,
            "graph_type": graph_type,
            "nodes": nodes,
            "links": links,
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


# === WebSocket Endpoint ===


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
            # Client can send messages (e.g., subscribe/unsubscribe filters)
            # For now, just receive and ignore
            data = await websocket.receive_text()
            logger.debug(f"[WebSocket] Received: {data}")

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
        logger.info("[WebSocket] Client disconnected normally")

    except Exception as e:
        logger.error(f"[WebSocket] Connection error: {e}")
        await websocket_manager.disconnect(websocket)
