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
