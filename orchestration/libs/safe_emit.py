"""
Safe Emit - Choke-point for all WebSocket emissions

Prevents error storms by:
1. Checking connection state before sending
2. Debounced logging (max once per 5s)
3. Optional spill buffer for disconnected state
4. No retry loops

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-30
"""

import logging
from time import monotonic
from typing import Dict, Any, Optional, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Global state for debounced logging
_last_error_log = 0.0
_error_count_since_log = 0


async def safe_emit(
    ws: WebSocket,
    payload: Dict[str, Any],
    spill: Optional[List[Dict]] = None
) -> bool:
    """
    Safely emit event to WebSocket with error handling.

    Args:
        ws: WebSocket connection
        payload: Event dict to send
        spill: Optional spill buffer for failed sends

    Returns:
        True if sent successfully, False if failed
    """
    global _last_error_log, _error_count_since_log

    try:
        # Check connection state (Starlette sets .application_state on WebSocket)
        if hasattr(ws, 'application_state'):
            if ws.application_state.name != "CONNECTED":
                raise RuntimeError("ws_not_ready")

        # Send
        await ws.send_json(payload)
        return True

    except Exception as e:
        # Spill to buffer if provided
        if spill is not None:
            spill.append(payload)

        # Debounced logging (max once per 5s)
        _error_count_since_log += 1
        now = monotonic()

        if now - _last_error_log > 5.0:
            logger.warning(
                f"[SafeEmit] Failed to send (errors since last log: {_error_count_since_log}): {e}"
            )
            _last_error_log = now
            _error_count_since_log = 0

        return False


async def safe_broadcast(
    connections: Dict[str, Dict[str, Any]],
    payload: Dict[str, Any],
    spill: Optional[List[Dict]] = None
) -> int:
    """
    Safely broadcast to multiple WebSocket connections.

    Args:
        connections: Dict of conn_id -> {ws, topics, ...}
        payload: Event dict to broadcast
        spill: Optional spill buffer for failed sends

    Returns:
        Number of successful deliveries
    """
    delivered = 0
    disconnected = []

    for conn_id, meta in connections.items():
        ws = meta.get("ws")
        if ws is None:
            disconnected.append(conn_id)
            continue

        success = await safe_emit(ws, payload, spill)
        if success:
            delivered += 1
        else:
            disconnected.append(conn_id)

    # Log disconnected connections (caller should clean these up)
    if disconnected:
        logger.info(f"[SafeBroadcast] Detected {len(disconnected)} disconnected: {disconnected}")

    return delivered
