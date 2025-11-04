"""
Membrane Hub - Minimal Event Bus for L2/L3 Communication

A tiny WebSocket-based pub/sub bus that preserves membrane discipline:
- /inject: accepts membrane.inject envelopes and fans out to subscribers
- /observe: subscribers register interest in channels

This is the "simplest thing that works" to unblock docs-as-views.
Later: swap for Redis-backed hub without changing L2/L3 code.

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import asyncio
import json
import logging
from collections import defaultdict
from typing import Dict, Set

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

# Channel subscriptions: channel_name -> set of WebSocket connections
SUBS: Dict[str, Set[WebSocketServerProtocol]] = defaultdict(set)


async def handle_observe(ws: WebSocketServerProtocol):
    """
    Handle /observe connections (subscribers).

    Clients send: {"type": "subscribe", "channels": ["docs.view.request", ...]}
    Server responds: {"type": "subscribe.ack", "channels": [...]}

    Then server pushes matching membrane.inject envelopes to this connection.
    """
    client_channels = set()

    try:
        async for raw in ws:
            msg = json.loads(raw)

            if msg.get("type") == "subscribe":
                channels = msg.get("channels", [])
                for ch in channels:
                    SUBS[ch].add(ws)
                    client_channels.add(ch)

                await ws.send(json.dumps({
                    "type": "subscribe.ack",
                    "channels": channels
                }))

                logger.info(f"[MembraneHub] Client subscribed to {len(channels)} channels: {channels}")

    except websockets.exceptions.ConnectionClosed:
        logger.debug(f"[MembraneHub] Observer connection closed")

    finally:
        # Cleanup: remove this connection from all subscriptions
        for ch in client_channels:
            SUBS[ch].discard(ws)

        logger.debug(f"[MembraneHub] Observer unsubscribed from {len(client_channels)} channels")


async def dispatch(envelope: dict):
    """
    Fan out envelope to all subscribers of the channel.

    Envelope format:
    {
        "type": "membrane.inject",
        "channel": "docs.view.request",
        "payload": {...},
        "origin": "l3.docs",
        "timestamp": "2025-11-04T14:00:00Z"
    }
    """
    ch = envelope.get("channel")
    if not ch:
        logger.warning(f"[MembraneHub] Envelope missing 'channel': {envelope}")
        return

    subscribers = list(SUBS.get(ch, []))

    if not subscribers:
        logger.debug(f"[MembraneHub] No subscribers for channel '{ch}'")
        return

    dead = []

    for conn in subscribers:
        try:
            await conn.send(json.dumps(envelope))
        except Exception as e:
            logger.error(f"[MembraneHub] Failed to send to subscriber: {e}")
            dead.append(conn)

    # Remove dead connections
    for d in dead:
        SUBS[ch].discard(d)

    logger.debug(f"[MembraneHub] Dispatched to {len(subscribers) - len(dead)} subscribers on '{ch}'")


async def handle_inject(ws: WebSocketServerProtocol):
    """
    Handle /inject connections (publishers).

    Publishers send: {
        "type": "membrane.inject",
        "channel": "docs.view.request",
        "payload": {...},
        "origin": "l3.docs"
    }

    Server dispatches to all subscribers of that channel.
    """
    try:
        async for raw in ws:
            env = json.loads(raw)

            # Expect membrane.inject envelopes
            if env.get("type") == "membrane.inject":
                await dispatch(env)
            else:
                logger.warning(f"[MembraneHub] Unexpected message type on /inject: {env.get('type')}")

    except websockets.exceptions.ConnectionClosed:
        logger.debug(f"[MembraneHub] Injector connection closed")


async def router(ws: WebSocketServerProtocol, path: str):
    """Route connections based on path."""

    if path == "/observe":
        await handle_observe(ws)
    elif path == "/inject":
        await handle_inject(ws)
    else:
        logger.warning(f"[MembraneHub] Unknown path: {path}")
        await ws.close(code=1008, reason="unknown path")


async def main():
    """Start the membrane hub."""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    host = "0.0.0.0"
    port = 8765

    logger.info(f"[MembraneHub] Starting on ws://{host}:{port}/{{inject,observe}}")

    async with websockets.serve(router, host, port):
        logger.info(f"[MembraneHub] Ready - accepting connections")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
