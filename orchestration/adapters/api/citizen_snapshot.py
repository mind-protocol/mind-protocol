"""
Citizen Graph Snapshot Endpoint

Provides REST endpoint for retrieving citizen consciousness graph snapshots.
Stops the frontend 404 flood by returning normalized graph data.

Author: Victor "The Resurrector" (Infrastructure fix)
Date: 2025-10-23
"""

from fastapi import APIRouter, HTTPException
from orchestration.adapters.storage.engine_registry import get_engine

router = APIRouter(prefix="/api/consciousness", tags=["consciousness"])


@router.get("/citizen/{citizen_id}")
async def get_citizen_snapshot(citizen_id: str):
    """
    Get consciousness graph snapshot for a citizen.

    Returns normalized graph data (nodes/links) for dashboard visualization.
    This endpoint stops the 404 flood from the frontend.

    Args:
        citizen_id: Citizen identifier (with or without "citizen_" prefix)

    Returns:
        {
            "id": "citizen_victor",
            "name": "Victor",
            "type": "personal",
            "nodes": [...],
            "links": [...],
            "metadata": {
                "node_count": 246,
                "link_count": 77,
                "tick_count": 1523
            }
        }
    """
    # Normalize citizen ID (accept with or without "citizen_" prefix)
    if not citizen_id.startswith("citizen_"):
        cid = f"citizen_{citizen_id}"
    else:
        cid = citizen_id

    # Try to get running engine
    engine = get_engine(citizen_id)
    if not engine:
        # Return minimal stub if engine not running yet
        return {
            "id": cid,
            "name": citizen_id.replace("citizen_", "").title(),
            "type": "personal",
            "nodes": [],
            "links": [],
            "metadata": {"status": "engine_not_running"}
        }

    # Get real snapshot from engine's graph
    graph = engine.graph
    nodes = []
    for node in graph.nodes.values():
        nodes.append({
            "id": node.id,
            "node_type": node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
            "energy": round(node.E, 3),
            "theta": round(node.theta, 3),
            "active": node.E >= node.theta,
            "log_weight": round(node.log_weight, 3)
        })

    links = []
    for link in graph.links.values():
        links.append({
            "id": f"{link.source_id}→{link.target_id}",
            "src": link.source_id,
            "dst": link.target_id,
            "type": link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type),
            "log_weight": round(link.log_weight, 3),
            "energy": round(link.energy, 3)
        })

    return {
        "id": cid,
        "name": citizen_id.replace("citizen_", "").title(),
        "type": "personal",
        "nodes": nodes,
        "links": links,
        "metadata": {
            "node_count": len(nodes),
            "link_count": len(links),
            "tick_count": engine.tick_count
        }
    }
