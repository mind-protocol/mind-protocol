"""
L3 Docs View API - Integrated into Mind Protocol WebSocket

Handles docs.view.request and docs.subscribe events.
Treats documentation as materialized views of FalkorDB organizational graphs.

Event Handlers:
- docs.view.request → execute Cypher query, return data
- docs.subscribe → subscribe client to org graph updates
- graph.delta.* → invalidate cache, broadcast to subscribers

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Set
from fastapi import APIRouter, WebSocket
import requests

logger = logging.getLogger(__name__)

# ============================================================================
# View Cache & Subscribers
# ============================================================================

# Cache: org:view_id → (cached_at, view_data)
VIEW_CACHE: Dict[str, tuple[datetime, Any]] = {}

# Subscribers: org → set of websockets
SUBSCRIBERS: Dict[str, Set[WebSocket]] = {}

# FalkorDB configuration
FALKORDB_API = "https://mindprotocol.onrender.com/admin/query"
FALKORDB_KEY = "Sxv48F2idLAXMnvqQTdvlQ4gArsDVhK4ROGyU"

# Cache TTL (seconds)
CACHE_TTL = 300  # 5 minutes

# ============================================================================
# View Definitions (Cypher Queries)
# ============================================================================

VIEWS = {
    "architecture": {
        "title": "Architecture Overview",
        "description": "System specifications and implementations",
        "query": """
            MATCH (spec:U4_Knowledge_Object)
            WHERE spec.scope_ref = $org AND spec.ko_type = 'spec'
            OPTIONAL MATCH (spec)-[:U4_DOCUMENTS]->(impl:U4_Code_Artifact)
            RETURN
                spec.name as spec_name,
                spec.description as spec_desc,
                spec.path as spec_path,
                collect(impl.name) as implementations,
                count(impl) as impl_count
            ORDER BY spec.name
        """
    },

    "api-reference": {
        "title": "API Reference",
        "description": "API endpoints and documentation",
        "query": """
            MATCH (api:U4_Code_Artifact)
            WHERE api.scope_ref = $org AND (api.path CONTAINS 'api' OR api.path CONTAINS 'endpoint')
            OPTIONAL MATCH (api)-[:U4_DOCUMENTS]->(doc:U4_Knowledge_Object)
            RETURN
                api.name as endpoint,
                api.path as file,
                api.description as desc,
                doc.description as docs
            ORDER BY api.path
        """
    },

    "coverage": {
        "title": "Coverage Report",
        "description": "Graph composition and node type distribution",
        "query": """
            MATCH (n)
            WHERE n.scope_ref = $org
            WITH labels(n)[0] as type, count(n) as count
            RETURN type, count
            ORDER BY count DESC
        """
    },

    "index": {
        "title": "Documentation Index",
        "description": "All documentation nodes",
        "query": """
            MATCH (n:U4_Knowledge_Object)
            WHERE n.scope_ref = $org
            RETURN n.name as title, n.description as desc, n.path as path
            ORDER BY n.name
        """
    },

    "agents": {
        "title": "AI Agents",
        "description": "Active AI agents and citizens",
        "query": """
            MATCH (n:U4_Agent)
            WHERE n.scope_ref = $org
            RETURN n.name as agent_name, n.description as desc, n.agent_type as type, n.status as status
            ORDER BY n.name
        """
    }
}

# ============================================================================
# Cypher Query Execution
# ============================================================================

def execute_cypher(org: str, query: str, params: dict = None) -> List[Dict]:
    """Execute Cypher query against FalkorDB"""

    payload = {
        "graph_name": org,
        "query": query
    }

    headers = {
        "X-API-Key": FALKORDB_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(FALKORDB_API, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()

        # Parse FalkorDB result format
        # result["result"] = [columns, rows, metadata]
        if "result" not in result or len(result["result"]) < 2:
            return []

        columns = result["result"][0]
        rows = result["result"][1]

        # Convert to list of dicts
        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        logger.error(f"Cypher query failed: {e}")
        return []

# ============================================================================
# View Computation
# ============================================================================

def compute_view(org: str, view_id: str) -> Dict[str, Any]:
    """Execute view query and return data (check cache first)"""

    if view_id not in VIEWS:
        return {
            "error": f"View '{view_id}' not found",
            "available_views": list(VIEWS.keys())
        }

    view = VIEWS[view_id]

    # Check cache
    cache_key = f"{org}:{view_id}"
    if cache_key in VIEW_CACHE:
        cached_at, data = VIEW_CACHE[cache_key]
        age = (datetime.now() - cached_at).total_seconds()
        if age < CACHE_TTL:
            logger.info(f"✅ Cache hit: {cache_key} (age: {age:.1f}s)")
            data["cached"] = True
            data["cache_age_seconds"] = age
            return data

    # Execute query (materialize view)
    logger.info(f"🔍 Computing view: {org}/{view_id}")
    rows = execute_cypher(org, view["query"], params={"org": org})

    view_data = {
        "org": org,
        "view_id": view_id,
        "title": view["title"],
        "description": view["description"],
        "data": rows,
        "row_count": len(rows),
        "generated_at": datetime.now().isoformat(),
        "cached": False,
        "cache_age_seconds": 0
    }

    # Cache result
    VIEW_CACHE[cache_key] = (datetime.now(), view_data)
    logger.info(f"💾 Cached view: {cache_key} ({len(rows)} rows)")

    return view_data

# ============================================================================
# Cache Management
# ============================================================================

def invalidate_cache(org: str):
    """Invalidate all cached views for org"""
    keys_to_delete = [k for k in VIEW_CACHE.keys() if k.startswith(f"{org}:")]
    for key in keys_to_delete:
        del VIEW_CACHE[key]
    logger.info(f"🗑️  Invalidated {len(keys_to_delete)} cached views for {org}")
    return keys_to_delete

async def broadcast_cache_invalidation(org: str, views: List[str]):
    """Broadcast cache invalidation to subscribers"""
    if org not in SUBSCRIBERS:
        return

    message = {
        "type": "docs.cache.invalidated",
        "org": org,
        "views": views,
        "reason": "source_graph_updated",
        "timestamp": datetime.now().isoformat()
    }

    disconnected = []
    for ws in SUBSCRIBERS[org]:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(ws)

    # Remove disconnected clients
    for ws in disconnected:
        SUBSCRIBERS[org].discard(ws)

# ============================================================================
# Event Handlers
# ============================================================================

async def handle_docs_view_request(ws: WebSocket, msg: dict):
    """Handle docs.view.request event"""
    org = msg.get("org")
    view_id = msg.get("view_id", "index")
    request_id = msg.get("request_id")

    if not org:
        await ws.send_json({
            "type": "error",
            "request_id": request_id,
            "message": "Missing 'org' parameter"
        })
        return

    # Compute view
    view_data = compute_view(org, view_id)

    # Send response
    response = {
        "type": "docs.view.data",
        "request_id": request_id,
        **view_data
    }

    await ws.send_json(response)
    logger.info(f"✅ Sent view data: {org}/{view_id} ({view_data.get('row_count')} rows)")

async def handle_docs_subscribe(ws: WebSocket, msg: dict):
    """Handle docs.subscribe event"""
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
        "timestamp": datetime.now().isoformat()
    })

    logger.info(f"✅ Client subscribed to {org} docs (total subscribers: {len(SUBSCRIBERS[org])})")

async def handle_graph_delta_event(event: dict):
    """
    Handle graph.delta.* events from FalkorDB (L2 → L3 membrane event)

    Called when L2 organizational graph changes.
    Invalidates cache and broadcasts to subscribers.
    """
    org = event.get("org")

    if not org:
        return

    logger.info(f"📥 Graph update for {org}: {event.get('type')}")

    # Invalidate cache
    invalidated_views = invalidate_cache(org)
    view_ids = [v.split(":")[1] for v in invalidated_views]

    # Broadcast to subscribers
    await broadcast_cache_invalidation(org, view_ids)

# ============================================================================
# Router (for FastAPI integration)
# ============================================================================

router = APIRouter(prefix="/api/docs", tags=["docs-views"])

@router.get("/views")
async def list_views():
    """List all available view definitions"""
    return {
        "views": {
            view_id: {
                "title": view["title"],
                "description": view["description"]
            }
            for view_id, view in VIEWS.items()
        }
    }

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
    invalidated = invalidate_cache(org)
    return {
        "invalidated_count": len(invalidated),
        "keys": invalidated
    }

# ============================================================================
# Cleanup
# ============================================================================

def remove_subscriber(ws: WebSocket):
    """Remove websocket from all subscriptions"""
    for org, subs in SUBSCRIBERS.items():
        subs.discard(ws)
