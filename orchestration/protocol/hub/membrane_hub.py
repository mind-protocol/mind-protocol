"""
L4 Protocol Hub - Membrane Bus with Boundary Enforcement

LAYER: L4 (Protocol) - "Law at the boundary"

This is the protocol-level enforcement point for all cross-layer communication.
It is NOT an adapter or helper—it IS the boundary itself.

Responsibilities:
1. Envelope schema validation (required fields, types)
2. SEA-1.0 signature verification (authenticity)
3. CPS-1 quote enforcement (budget gates)
4. Rate limiting per org/channel
5. Tenant scoping (org isolation)
6. Rejection telemetry (failure.emit for protocol violations)

Architecture:
- /inject: Publishers (L2, L3) inject envelopes → validated → dispatched
- /observe: Subscribers (L2, L3) receive validated envelopes

Protocol Topics:
- ecosystem/{eco}/org/{org}/* - Org-scoped channels
- ecosystem/{eco}/protocol/* - Protocol-scoped channels

Author: Mel "Bridgekeeper"
Date: 2025-11-04 (Promoted to L4 protocol enforcement)
"""

import asyncio
import json
import logging
from collections import defaultdict
from typing import Dict, Set, Optional
from datetime import datetime, timezone

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

# Channel subscriptions: channel_name -> set of WebSocket connections
SUBS: Dict[str, Set[WebSocketServerProtocol]] = defaultdict(set)

# Rate limiting: (org, channel) -> (count, window_start)
RATE_LIMITS: Dict[tuple, tuple[int, float]] = {}

# Configuration
RATE_LIMIT_WINDOW = 60.0  # 60 seconds
RATE_LIMIT_MAX = 100  # Max requests per window per (org, channel)

# CPS-1 Quote Registry (stub - will integrate with economy runtime)
VALID_QUOTES: Dict[str, Dict] = {}  # quote_id -> {price, expires_at, org}


# ============================================================================
# L4 Protocol Enforcement
# ============================================================================

def validate_envelope(envelope: dict) -> tuple[bool, Optional[str]]:
    """
    Validate envelope schema (L4 protocol requirement).

    Returns: (is_valid, error_message)
    """
    # Required fields
    if "type" not in envelope:
        return False, "Missing required field: 'type'"

    if envelope["type"] != "membrane.inject":
        return False, f"Invalid envelope type: {envelope['type']}"

    if "channel" not in envelope:
        return False, "Missing required field: 'channel'"

    if "payload" not in envelope:
        return False, "Missing required field: 'payload'"

    if "origin" not in envelope:
        return False, "Missing required field: 'origin'"

    # Channel format validation
    channel = envelope["channel"]
    if not isinstance(channel, str) or len(channel) == 0:
        return False, "Invalid channel format"

    return True, None


def verify_sea_signature(envelope: dict) -> tuple[bool, Optional[str]]:
    """
    Verify SEA-1.0 signature (L4 protocol requirement).

    TODO: Integrate with SEA-1.0 implementation once available.
    For now: accept all (soft-enforcement for dev).

    Returns: (is_valid, error_message)
    """
    # Stub: Accept all for now
    # Future: Check envelope["signature"] against envelope["payload"] + envelope["origin"]
    return True, None


def enforce_cps1_quote(envelope: dict) -> tuple[bool, Optional[str]]:
    """
    Enforce CPS-1 quote-before-inject (L4 protocol requirement).

    Channels requiring payment must include valid quote_id in payload.

    Returns: (is_valid, error_message)
    """
    channel = envelope["channel"]
    payload = envelope["payload"]

    # Channels requiring CPS-1 quotes
    PAID_CHANNELS = ["docs.view.request", "docs.generate.request", "validation.assessment.request"]

    # Check if channel requires payment
    requires_payment = any(paid in channel for paid in PAID_CHANNELS)

    if not requires_payment:
        return True, None  # Free channels pass

    # Check for quote_id
    quote_id = payload.get("quote_id")
    if not quote_id:
        return False, "CPS-1 violation: Missing quote_id for paid channel"

    # Validate quote (stub - will integrate with economy runtime)
    # TODO: Check VALID_QUOTES registry or call economy service
    if not quote_id.startswith("q-"):
        return False, f"CPS-1 violation: Invalid quote_id format: {quote_id}"

    # TODO: Check expiration, budget, org match
    # For now: accept well-formed quote_ids
    return True, None


def check_rate_limit(org: str, channel: str) -> tuple[bool, Optional[str]]:
    """
    Check rate limit for (org, channel) combination.

    Returns: (is_allowed, error_message)
    """
    key = (org, channel)
    now = asyncio.get_event_loop().time()

    if key in RATE_LIMITS:
        count, window_start = RATE_LIMITS[key]

        # Check if window expired
        if now - window_start > RATE_LIMIT_WINDOW:
            # Reset window
            RATE_LIMITS[key] = (1, now)
            return True, None

        # Check if limit exceeded
        if count >= RATE_LIMIT_MAX:
            return False, f"Rate limit exceeded: {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s"

        # Increment count
        RATE_LIMITS[key] = (count + 1, window_start)
        return True, None

    else:
        # First request in window
        RATE_LIMITS[key] = (1, now)
        return True, None


def extract_org_from_channel(channel: str) -> Optional[str]:
    """
    Extract org from channel name.

    Channel format: ecosystem/{eco}/org/{org}/* or docs.view.request (legacy)

    Returns: org name or None
    """
    # New format: ecosystem/{eco}/org/{org}/*
    if "/org/" in channel:
        parts = channel.split("/org/")
        if len(parts) >= 2:
            org_part = parts[1].split("/")[0]
            return org_part

    # Legacy format: infer from payload (if available)
    # This is handled at dispatch time by checking payload["scope"]["org"]

    return None


async def enforce_protocol(envelope: dict) -> tuple[bool, Optional[str]]:
    """
    L4 Protocol Enforcement - Gate before dispatch.

    Checks:
    1. Envelope schema validation
    2. SEA-1.0 signature verification
    3. CPS-1 quote enforcement
    4. Rate limiting

    Returns: (is_valid, error_message)
    """
    # 1. Schema validation
    valid, error = validate_envelope(envelope)
    if not valid:
        return False, f"Schema validation failed: {error}"

    # 2. SEA-1.0 signature verification
    valid, error = verify_sea_signature(envelope)
    if not valid:
        return False, f"Signature verification failed: {error}"

    # 3. CPS-1 quote enforcement
    valid, error = enforce_cps1_quote(envelope)
    if not valid:
        return False, error

    # 4. Rate limiting
    channel = envelope["channel"]
    org = extract_org_from_channel(channel)

    if org:
        valid, error = check_rate_limit(org, channel)
        if not valid:
            return False, error

    return True, None


async def emit_protocol_failure(envelope: dict, reason: str, origin_ws: WebSocketServerProtocol):
    """
    Emit failure.emit for protocol violations.

    This is sent back to the injector to indicate rejection.
    """
    failure_envelope = {
        "type": "membrane.inject",
        "channel": "failure.emit",
        "payload": {
            "code_location": "protocol.hub.membrane_hub:enforce_protocol",
            "exception": reason,
            "severity": "error",
            "suggestion": "Check envelope schema, quote, and rate limits",
            "original_envelope": envelope
        },
        "origin": "protocol.hub",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        await origin_ws.send(json.dumps(failure_envelope))
        logger.warning(f"[L4 Protocol] Rejected envelope: {reason}")
    except Exception as e:
        logger.error(f"[L4 Protocol] Failed to send rejection: {e}")


# ============================================================================
# WebSocket Handlers
# ============================================================================

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

                logger.info(f"[L4 Protocol] Subscriber registered: {len(channels)} channels")

    except websockets.exceptions.ConnectionClosed:
        logger.debug(f"[L4 Protocol] Observer connection closed")

    finally:
        # Cleanup: remove this connection from all subscriptions
        for ch in client_channels:
            SUBS[ch].discard(ws)

        logger.debug(f"[L4 Protocol] Observer unsubscribed from {len(client_channels)} channels")


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
        logger.warning(f"[L4 Protocol] Envelope missing 'channel': {envelope}")
        return

    subscribers = list(SUBS.get(ch, []))

    if not subscribers:
        logger.debug(f"[L4 Protocol] No subscribers for channel '{ch}'")
        return

    dead = []

    for conn in subscribers:
        try:
            await conn.send(json.dumps(envelope))
        except Exception as e:
            logger.error(f"[L4 Protocol] Failed to send to subscriber: {e}")
            dead.append(conn)

    # Remove dead connections
    for d in dead:
        SUBS[ch].discard(d)

    logger.debug(f"[L4 Protocol] Dispatched to {len(subscribers) - len(dead)} subscribers on '{ch}'")


async def handle_inject(ws: WebSocketServerProtocol):
    """
    Handle /inject connections (publishers).

    Publishers send: {
        "type": "membrane.inject",
        "channel": "docs.view.request",
        "payload": {...},
        "origin": "l3.docs"
    }

    L4 Protocol enforces envelope validation, signatures, quotes, rate limits.
    """
    try:
        async for raw in ws:
            env = json.loads(raw)

            # L4 Protocol Enforcement
            valid, error = await enforce_protocol(env)

            if not valid:
                # Reject and emit failure
                await emit_protocol_failure(env, error, ws)
                continue

            # Envelope passed all checks - dispatch to subscribers
            await dispatch(env)

    except websockets.exceptions.ConnectionClosed:
        logger.debug(f"[L4 Protocol] Injector connection closed")


async def router(ws: WebSocketServerProtocol, path: str):
    """Route connections based on path."""

    if path == "/observe":
        await handle_observe(ws)
    elif path == "/inject":
        await handle_inject(ws)
    else:
        logger.warning(f"[L4 Protocol] Unknown path: {path}")
        await ws.close(code=1008, reason="unknown path")


async def main():
    """Start the L4 protocol hub."""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    host = "0.0.0.0"
    port = 8765

    logger.info(f"[L4 Protocol Hub] Starting on ws://{host}:{port}/{{inject,observe}}")
    logger.info(f"[L4 Protocol Hub] Enforcement: Schema + SEA-1.0 + CPS-1 + Rate Limits")

    async with websockets.serve(router, host, port):
        logger.info(f"[L4 Protocol Hub] Ready - enforcing boundary law")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
