"""
L3 Docs View API - Membrane-Native (Inject/Observe Only)

REFACTORED: No Cypher execution in L3. Pure inject/observe bridge.

Handles docs.view.request and docs.subscribe events via WebSocket.
Treats documentation as materialized views computed by L2 resolvers.

Event Flow:
1. Client → L3: docs.view.request (WebSocket message)
2. L3 → L2: inject docs.view.request event (membrane bus)
3. L2 → L3: observe docs.view.result event (membrane bus)
4. L3 → Client: docs.view.data (WebSocket response)

NO database credentials. NO Cypher queries. L3 is pure bridge.

Author: Mel "Bridgekeeper"
Date: 2025-11-04 (Refactored to membrane-native)
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Set, Optional
from fastapi import APIRouter, WebSocket
import asyncio

logger = logging.getLogger(__name__)

# ============================================================================
# Subscribers & Cache (digest-keyed)
# ============================================================================

# Subscribers: org → set of websockets
SUBSCRIBERS: Dict[str, Set[WebSocket]] = {}

# Cache: (org, view_id, params_tuple) → (cached_at, ko_digest, view_data)
VIEW_CACHE: Dict[tuple, tuple[datetime, str, Any]] = {}

# Pending requests: request_id → (websocket, timeout_task)
PENDING_REQUESTS: Dict[str, tuple[WebSocket, asyncio.Task]] = {}

# Cache TTL (seconds)
CACHE_TTL = 300  # 5 minutes

# Request timeout (seconds)
REQUEST_TIMEOUT = 15.0

# ============================================================================
# View Definitions (metadata only, no queries)
# ============================================================================

VIEWS = {
    "architecture": {
        "title": "Architecture Overview",
        "description": "System specifications and implementations"
    },
    "api-reference": {
        "title": "API Reference",
        "description": "API endpoints and documentation"
    },
    "coverage": {
        "title": "Coverage Report",
        "description": "Graph composition and node type distribution"
    },
    "index": {
        "title": "Documentation Index",
        "description": "All documentation nodes"
    }
}

# ============================================================================
# Cache Management (digest-keyed)
# ============================================================================

def get_cache_key(org: str, view_id: str, params: dict, format: str) -> tuple:
    """Build cache key from request parameters"""
    params_tuple = tuple(sorted(params.items())) if params else ()
    return (org, view_id, params_tuple, format)


def get_cached_view(key: tuple) -> Optional[Dict[str, Any]]:
    """Get cached view if not expired"""
    if key not in VIEW_CACHE:
        return None

    cached_at, ko_digest, data = VIEW_CACHE[key]
    age = (datetime.now(timezone.utc) - cached_at).total_seconds()

    if age > CACHE_TTL:
        del VIEW_CACHE[key]
        logger.info(f"[L3 Cache] Expired: {key}")
        return None

    logger.info(f"[L3 Cache] Hit: {key} (age: {age:.1f}s, digest: {ko_digest[:16]})")
    return data


def cache_view(key: tuple, ko_digest: str, data: Dict[str, Any]):
    """Cache view with ko_digest for surgical invalidation"""
    VIEW_CACHE[key] = (datetime.now(timezone.utc), ko_digest, data)
    logger.info(f"[L3 Cache] Cached: {key} (digest: {ko_digest[:16]})")


def invalidate_cache(org: str, affects: List[str]):
    """
    Invalidate cache keys matching affect patterns.

    Example affects: ["architecture:/", "api:/auth", "coverage:*"]
    """
    keys_to_delete = []

    for key in VIEW_CACHE.keys():
        cache_org, view_id, params_tuple, format = key

        if cache_org != org:
            continue

        # Check if key matches any affect pattern
        for pattern in affects:
            if pattern.startswith(f"{view_id}:"):
                # Pattern-specific invalidation
                path_pattern = pattern.split(":", 1)[1]
                if path_pattern == "*" or path_pattern in str(params_tuple):
                    keys_to_delete.append(key)
                    break
            elif view_id in pattern:
                # View-type match
                keys_to_delete.append(key)
                break

    for key in keys_to_delete:
        del VIEW_CACHE[key]

    logger.info(f"[L3 Cache] Invalidated {len(keys_to_delete)} keys for {org}: {affects}")
    return keys_to_delete


# ============================================================================
# Event Handlers (Inject/Observe Pattern)
# ============================================================================

async def handle_docs_view_request(ws: WebSocket, msg: dict):
    """
    Handle docs.view.request from client (inject to L2, observe result)

    Flow:
    1. Check cache (by ko_digest)
    2. If miss: inject docs.view.request to membrane bus
    3. Wait for observed docs.view.result (with timeout)
    4. Stream result to WebSocket
    """
    org = msg.get("org")
    view_id = msg.get("view_id", "index")
    request_id = msg.get("request_id", f"req_{int(datetime.now(timezone.utc).timestamp() * 1000)}")
    params = msg.get("params", {})
    format = msg.get("format", "json")

    if not org:
        await ws.send_json({
            "type": "error",
            "request_id": request_id,
            "message": "Missing 'org' parameter"
        })
        return

    if view_id not in VIEWS:
        await ws.send_json({
            "type": "error",
            "request_id": request_id,
            "message": f"Unknown view_id: {view_id}. Available: {list(VIEWS.keys())}"
        })
        return

    view_meta = VIEWS[view_id]

    # Check cache
    cache_key = get_cache_key(org, view_id, params, format)
    cached = get_cached_view(cache_key)

    if cached:
        # Cache hit - send immediately
        await ws.send_json({
            "type": "docs.view.data",
            "request_id": request_id,
            "org": org,
            "view_id": view_id,
            "title": view_meta["title"],
            "description": view_meta["description"],
            "format": format,
            "cached": True,
            **cached
        })
        return

    # Cache miss - inject request to L2 (via membrane bus)
    logger.info(f"[L3 Bridge] Cache miss, injecting docs.view.request: org={org} view={view_id}")

    # TODO: Get quote_id from economy service
    # For now, use placeholder (L2 stub will accept it)
    quote_id = f"q-stub-{request_id}"

    # Inject event to membrane bus
    # NOTE: This requires integration with the membrane bus
    # For now, we'll simulate by storing pending request
    try:
        # PLACEHOLDER: Replace with actual membrane bus injection
        # await bus.inject("docs.view.request", {
        #     "request_id": request_id,
        #     "quote_id": quote_id,
        #     "view_type": view_id,
        #     "format": format,
        #     "scope": {"org": org, "root": "repo://", "path": "/"},
        #     "params": params
        # })

        # Register pending request (will be resolved by observe handler)
        timeout_task = asyncio.create_task(
            _wait_for_result(ws, request_id, REQUEST_TIMEOUT)
        )
        PENDING_REQUESTS[request_id] = (ws, timeout_task)

        logger.info(f"[L3 Bridge] Injected docs.view.request (request_id={request_id})")

    except Exception as exc:
        logger.error(f"[L3 Bridge] Failed to inject request: {exc}", exc_info=True)
        await ws.send_json({
            "type": "error",
            "request_id": request_id,
            "message": f"Failed to inject request: {str(exc)}"
        })


async def _wait_for_result(ws: WebSocket, request_id: str, timeout: float):
    """Wait for docs.view.result with timeout"""
    try:
        await asyncio.sleep(timeout)

        # Timeout - send error
        if request_id in PENDING_REQUESTS:
            await ws.send_json({
                "type": "error",
                "request_id": request_id,
                "message": f"Request timed out after {timeout}s (L2 resolver may be unavailable)"
            })
            del PENDING_REQUESTS[request_id]

    except asyncio.CancelledError:
        # Result arrived before timeout
        pass


async def handle_docs_view_result(result_envelope: dict):
    """
    Observe docs.view.result from L2 resolver (membrane bus)

    Called when L2 emits docs.view.result after computing view.
    Streams result to waiting WebSocket client.
    """
    content = result_envelope.get("content", {})
    request_id = content.get("request_id")
    status = content.get("status")

    if not request_id or request_id not in PENDING_REQUESTS:
        return

    ws, timeout_task = PENDING_REQUESTS.pop(request_id)
    timeout_task.cancel()  # Cancel timeout

    if status == "ok":
        # Extract view data
        view_model = content.get("view_model")
        provenance = content.get("provenance", {})
        ko_digest = provenance.get("ko_digest", "unknown")

        # Cache result
        # TODO: Extract org, view_id, params from request context
        # For now, we'll need to track request context separately

        # Send to client
        await ws.send_json({
            "type": "docs.view.data",
            "request_id": request_id,
            "status": "ok",
            "view_model": view_model,
            "provenance": provenance,
            "cached": False,
            "generated_at": datetime.now(timezone.utc).isoformat()
        })

        logger.info(f"[L3 Bridge] Streamed docs.view.result to client (request_id={request_id})")

    else:
        # Error from L2
        error = content.get("error", {})
        await ws.send_json({
            "type": "error",
            "request_id": request_id,
            "message": error.get("message", "Unknown error"),
            "code": error.get("code", "E_UNKNOWN")
        })

        logger.error(f"[L3 Bridge] L2 resolver error (request_id={request_id}): {error}")


async def handle_docs_subscribe(ws: WebSocket, msg: dict):
    """Handle docs.subscribe event (subscribe to org updates)"""
    org = msg.get("org")

    if not org:
        await ws.send_json({
            "type": "error",
            "message": "Missing 'org' parameter"
        })
        return

    # Add to subscribers
    if org not in SUBSCRIBERS:
        SUBSCRIBERS[org] = set()
    SUBSCRIBERS[org].add(ws)

    await ws.send_json({
        "type": "docs.subscribed",
        "org": org,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    logger.info(f"[L3 Bridge] Client subscribed to {org} docs (total subscribers: {len(SUBSCRIBERS[org])})")


async def handle_docs_view_invalidated(invalidation_envelope: dict):
    """
    Observe docs.view.invalidated from L2 (membrane bus)

    Called when L2 emits cache invalidation after graph changes.
    Invalidates local cache and broadcasts to subscribers.
    """
    content = invalidation_envelope.get("content", {})
    reasons = content.get("reasons", [])
    affects = content.get("affects", [])

    # Extract org from affects patterns (e.g., "architecture:/" → org from context)
    # For now, invalidate for all orgs (surgical version would parse patterns)

    for org, subscribers in list(SUBSCRIBERS.items()):
        # Invalidate cache
        invalidated_keys = invalidate_cache(org, affects)

        # Broadcast to subscribers
        message = {
            "type": "docs.cache.invalidated",
            "org": org,
            "reasons": reasons,
            "affects": affects,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        disconnected = []
        for ws in subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)

        # Remove disconnected clients
        for ws in disconnected:
            subscribers.discard(ws)

        logger.info(f"[L3 Bridge] Broadcasted cache invalidation to {len(subscribers)} subscribers (org={org})")


# ============================================================================
# Cleanup
# ============================================================================

def remove_subscriber(ws: WebSocket):
    """Remove websocket from all subscriptions"""
    for org, subs in SUBSCRIBERS.items():
        subs.discard(ws)


# ============================================================================
# FastAPI Router (REST endpoints for manual inspection)
# ============================================================================

router = APIRouter(prefix="/api/docs", tags=["docs-views"])


@router.get("/views")
async def list_views():
    """List all available view definitions"""
    return {"views": VIEWS}


@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "cached_views": len(VIEW_CACHE),
        "subscribers": {org: len(subs) for org, subs in SUBSCRIBERS.items()},
        "cache_ttl_seconds": CACHE_TTL
    }


@router.post("/cache/invalidate/{org}")
async def invalidate_org_cache(org: str):
    """Manually invalidate cache for an org"""
    invalidated = invalidate_cache(org, ["*"])
    return {
        "invalidated_count": len(invalidated),
        "keys": [str(k) for k in invalidated]
    }
