"""
Membrane Bus Client - Shared Helper for Publishing Events

Both L2 and L3 use this to inject events into the membrane bus.
Maintains a single persistent WebSocket connection to /inject.

Usage:
    from orchestration.adapters.bus.membrane_bus import publish_to_membrane

    publish_to_membrane(
        channel="docs.view.request",
        payload={"request_id": "req123", "view_type": "architecture"},
        origin="l3.docs"
    )

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import websockets

logger = logging.getLogger(__name__)

# Shared connection pool
_ws_connection: Optional[websockets.WebSocketClientProtocol] = None
_connection_lock = asyncio.Lock()

# Configuration
MEMBRANE_HUB_URI = "ws://localhost:8765/inject"


async def get_connection():
    """Get or create persistent WebSocket connection to membrane hub."""
    global _ws_connection

    async with _connection_lock:
        if _ws_connection is None or _ws_connection.closed:
            try:
                _ws_connection = await websockets.connect(MEMBRANE_HUB_URI)
                logger.info(f"[MembraneBus] Connected to {MEMBRANE_HUB_URI}")
            except Exception as e:
                logger.error(f"[MembraneBus] Failed to connect: {e}")
                raise

        return _ws_connection


async def publish_to_membrane_async(channel: str, payload: Dict[str, Any], origin: str):
    """
    Publish event to membrane bus (async version).

    Args:
        channel: Event channel (e.g., "docs.view.request")
        payload: Event payload (dict)
        origin: Source identifier (e.g., "l3.docs", "l2.resolver")
    """
    envelope = {
        "type": "membrane.inject",
        "channel": channel,
        "payload": payload,
        "origin": origin,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        ws = await get_connection()
        await ws.send(json.dumps(envelope))
        logger.debug(f"[MembraneBus] Published to '{channel}' from {origin}")

    except Exception as e:
        logger.error(f"[MembraneBus] Failed to publish to '{channel}': {e}")
        # Reset connection on error
        global _ws_connection
        _ws_connection = None
        raise


def publish_to_membrane(channel: str, payload: Dict[str, Any], origin: str):
    """
    Publish event to membrane bus (sync wrapper).

    Use this in synchronous contexts. Creates event loop if needed.

    Args:
        channel: Event channel (e.g., "docs.view.request")
        payload: Event payload (dict)
        origin: Source identifier (e.g., "l3.docs", "l2.resolver")
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(publish_to_membrane_async(channel, payload, origin))


async def close_connection():
    """Close the persistent connection (cleanup)."""
    global _ws_connection

    if _ws_connection and not _ws_connection.closed:
        await _ws_connection.close()
        logger.info("[MembraneBus] Connection closed")
        _ws_connection = None
