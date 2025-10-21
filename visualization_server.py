"""
Consciousness Substrate Visualization Server

Self-observing substrate visualization using metadata-aware polling.
Supports multi-graph architecture (N1 citizens, N2 orgs, N3 ecosystem).

Architecture:
- Single state stream (no separate events)
- Operations detected from metadata changes (traversal_count, co_activation_count)
- 2D topological graph with time as explicit dimension
- WebSocket per graph connection

Designer: Felix "Ironhand"
Date: 2025-10-17
"""

import asyncio
import json
import time
from typing import Dict, Set, List, Optional
from collections import defaultdict
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import redis
import shutil

# FalkorDB client
from falkordb import FalkorDB

# Control API from Ada (kill switches)
from orchestration.control_api import router as control_router

app = FastAPI(title="Mind Protocol Visualization")

# Enable CORS for Next.js dashboard (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add control API routes (freeze/resume consciousness loops)
app.include_router(control_router)

# FalkorDB connection
db = FalkorDB(host='localhost', port=6379)

# Active WebSocket connections: {websocket -> graph_name}
active_connections: Dict[WebSocket, str] = {}

# Graph state cache: {graph_name -> {nodes, links, entities, timestamp}}
graph_state_cache: Dict[str, Dict] = {}

# Polling interval (milliseconds)
POLL_INTERVAL_MS = 200


# ============================================================================
# Graph Discovery
# ============================================================================

def discover_graphs() -> Dict[str, List[str]]:
    """
    Discover all graphs in FalkorDB and categorize by type.

    Returns:
        {
            "citizens": ["luca", "felix", "ada", ...],
            "organizations": ["mind_protocol", ...],
            "ecosystems": ["ai_agents", ...]
        }
    """
    try:
        # Connect to Redis to list graphs
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get all graphs using GRAPH.LIST command
        graphs = r.execute_command("GRAPH.LIST")

        categorized = {
            "citizens": [],
            "organizations": [],
            "ecosystems": []
        }

        for graph_name in graphs:
            # Parse graph name by convention
            if graph_name.startswith("citizen_"):
                citizen_id = graph_name.replace("citizen_", "")
                categorized["citizens"].append(citizen_id)
            elif graph_name.startswith("org_"):
                org_id = graph_name.replace("org_", "")
                categorized["organizations"].append(org_id)
            elif graph_name.startswith("ecosystem_"):
                ecosystem_id = graph_name.replace("ecosystem_", "")
                categorized["ecosystems"].append(ecosystem_id)

        return categorized

    except Exception as e:
        print(f"Error discovering graphs: {e}")
        return {"citizens": [], "organizations": [], "ecosystems": []}


def graph_exists(graph_name: str) -> bool:
    """Check if graph exists in FalkorDB."""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        graphs = r.execute_command("GRAPH.LIST")
        return graph_name in graphs
    except Exception as e:
        print(f"Error checking graph existence: {e}")
        return False


# ============================================================================
# Graph State Querying (with Metadata)
# ============================================================================

def query_graph_with_metadata(graph_name: str) -> Dict:
    """
    Query graph state including operational metadata.

    Metadata tracked:
    - Nodes: traversal_count, last_traversed_by, last_traversal_time,
             last_modified, sub_entity_weights, energy, confidence
    - Links: link_strength, co_activation_count, traversal_count,
             last_traversal_time, last_traversed_by
    """
    g = db.select_graph(graph_name)

    # Query nodes with metadata
    nodes_query = """
    MATCH (n)
    RETURN
        id(n) as id,
        n.id as node_id,
        labels(n) as labels,
        n.node_type as node_type,
        n.text as text,
        n.sub_entity_weights as entity_activations,
        n.energy as energy,
        n.confidence as confidence,
        n.emotion_vector as emotions,
        n.traversal_count as traversal_count,
        n.last_traversed_by as last_entity,
        n.last_traversal_time as last_active,
        n.last_modified as last_modified
    """

    # Query links with metadata
    links_query = """
    MATCH (a)-[r]->(b)
    RETURN
        id(r) as id,
        r.link_id as link_id,
        id(a) as source,
        id(b) as target,
        type(r) as type,
        r.link_type as link_type,
        r.link_strength as strength,
        r.co_activation_count as co_activations,
        r.traversal_count as traversal_count,
        r.last_traversal_time as last_traversed,
        r.last_traversed_by as last_entity
    """

    # Query sub-entities (if they exist as separate nodes)
    entities_query = """
    MATCH (e:SubEntity)
    RETURN
        e.entity_id as entity_id,
        e.current_node_id as current_position,
        e.energy as energy,
        e.energy_budget as energy_budget,
        e.energy_used as energy_used
    """

    try:
        nodes_result = g.query(nodes_query)
        links_result = g.query(links_query)
        entities_result = g.query(entities_query)

        return {
            "nodes": [dict(zip([col[1] for col in nodes_result.header], record))
                     for record in nodes_result.result_set],
            "links": [dict(zip([col[1] for col in links_result.header], record))
                     for record in links_result.result_set],
            "entities": [dict(zip([col[1] for col in entities_result.header], record))
                        for record in entities_result.result_set],
            "timestamp": time.time() * 1000  # milliseconds
        }
    except Exception as e:
        print(f"Error querying graph {graph_name}: {e}")
        return {"nodes": [], "links": [], "entities": [], "timestamp": time.time() * 1000}


# ============================================================================
# Operation Detection (from Metadata Changes)
# ============================================================================

def detect_operations(old_state: Dict, new_state: Dict) -> List[Dict]:
    """
    Detect operations by comparing metadata changes.

    Operations detected:
    - entity_traversal: traversal_count increased
    - hebbian_learning: co_activation_count increased, link_strength changed
    - activation_increase: energy increased significantly
    """
    operations = []

    old_nodes = {n["id"]: n for n in old_state.get("nodes", [])}
    new_nodes = {n["id"]: n for n in new_state.get("nodes", [])}

    # Detect entity traversals
    for node_id, new_node in new_nodes.items():
        if node_id in old_nodes:
            old_count = old_nodes[node_id].get("traversal_count") or 0
            new_count = new_node.get("traversal_count") or 0

            if new_count > old_count:
                operations.append({
                    "type": "entity_traversal",
                    "node_id": node_id,
                    "entity": new_node.get("last_entity"),
                    "timestamp": new_node.get("last_active"),
                    "text": new_node.get("text", "")[:50]
                })

    # Detect Hebbian learning
    old_links = {l["id"]: l for l in old_state.get("links", [])}
    new_links = {l["id"]: l for l in new_state.get("links", [])}

    for link_id, new_link in new_links.items():
        if link_id in old_links:
            old_activations = old_links[link_id].get("co_activations") or 0
            new_activations = new_link.get("co_activations") or 0
            old_strength = old_links[link_id].get("strength") or 0.5
            new_strength = new_link.get("strength") or 0.5

            if new_activations > old_activations:
                operations.append({
                    "type": "hebbian_learning",
                    "link_id": link_id,
                    "link_type": new_link.get("type"),
                    "strength_delta": new_strength - old_strength,
                    "co_activation_count": new_activations,
                    "timestamp": new_link.get("last_traversed")
                })

    # Detect activation increases
    for node_id, new_node in new_nodes.items():
        if node_id in old_nodes:
            old_energy = old_nodes[node_id].get("energy") or 0
            new_energy = new_node.get("energy") or 0

            if new_energy > old_energy + 0.1:  # Significant increase
                operations.append({
                    "type": "activation_increase",
                    "node_id": node_id,
                    "energy_delta": new_energy - old_energy,
                    "new_energy": new_energy,
                    "entity_weights": new_node.get("entity_activations"),
                    "text": new_node.get("text", "")[:50]
                })

    return operations


def compute_state_diff(old_state: Dict, new_state: Dict) -> Dict:
    """
    Compute minimal diff between states for efficient transmission.
    """
    diff = {
        "nodes_updated": [],
        "nodes_added": [],
        "links_updated": [],
        "links_added": []
    }

    old_nodes = {n["id"]: n for n in old_state.get("nodes", [])}
    new_nodes = {n["id"]: n for n in new_state.get("nodes", [])}

    for node_id, new_node in new_nodes.items():
        if node_id not in old_nodes:
            diff["nodes_added"].append(new_node)
        elif old_nodes[node_id] != new_node:
            diff["nodes_updated"].append(new_node)

    old_links = {l["id"]: l for l in old_state.get("links", [])}
    new_links = {l["id"]: l for l in new_state.get("links", [])}

    for link_id, new_link in new_links.items():
        if link_id not in old_links:
            diff["links_added"].append(new_link)
        elif old_links[link_id] != new_link:
            diff["links_updated"].append(new_link)

    return diff


# ============================================================================
# WebSocket Management
# ============================================================================

async def broadcast_to_graph(graph_name: str, message: Dict):
    """Send message to all clients connected to specific graph."""
    disconnected = []

    for connection, conn_graph in active_connections.items():
        if conn_graph == graph_name:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

    # Clean up disconnected
    for conn in disconnected:
        active_connections.pop(conn, None)


async def graph_polling_loop(graph_name: str):
    """
    Continuous polling loop for specific graph.
    Runs while at least one client is connected to this graph.
    """
    previous_state = {"nodes": [], "links": [], "entities": [], "timestamp": 0}

    while any(g == graph_name for g in active_connections.values()):
        try:
            # Query current state
            current_state = query_graph_with_metadata(graph_name)

            # Detect operations from metadata changes
            operations = detect_operations(previous_state, current_state)

            # Compute diff for efficient transmission
            diff = compute_state_diff(previous_state, current_state)

            # Broadcast if there are changes
            if operations or diff["nodes_updated"] or diff["links_updated"]:
                await broadcast_to_graph(graph_name, {
                    "type": "graph_update",
                    "diff": diff,
                    "operations": operations,
                    "timestamp": current_state["timestamp"]
                })

            previous_state = current_state

        except Exception as e:
            print(f"Error in polling loop for {graph_name}: {e}")

        await asyncio.sleep(POLL_INTERVAL_MS / 1000.0)


# Track active polling tasks: {graph_name -> asyncio.Task}
polling_tasks: Dict[str, asyncio.Task] = {}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/graphs")
async def list_graphs():
    """List all available graphs categorized by type."""
    return discover_graphs()


@app.websocket("/ws/graph/{graph_type}/{graph_id}")
async def websocket_graph(websocket: WebSocket, graph_type: str, graph_id: str):
    """
    WebSocket endpoint for graph visualization.

    URL: /ws/graph/{graph_type}/{graph_id}
    - graph_type: "citizen", "organization", "ecosystem"
    - graph_id: specific ID (e.g., "luca", "mind_protocol")
    """
    await websocket.accept()

    # Construct graph name
    graph_name_patterns = {
        "citizen": f"citizen_{graph_id}",
        "organization": f"org_{graph_id}",
        "ecosystem": f"ecosystem_{graph_id}"
    }

    if graph_type not in graph_name_patterns:
        await websocket.send_json({
            "type": "error",
            "message": f"Invalid graph type: {graph_type}"
        })
        await websocket.close()
        return

    graph_name = graph_name_patterns[graph_type]

    # Verify graph exists
    if not graph_exists(graph_name):
        await websocket.send_json({
            "type": "error",
            "message": f"Graph not found: {graph_name}"
        })
        await websocket.close()
        return

    # Register connection
    active_connections[websocket] = graph_name

    # Send initial state
    initial_state = query_graph_with_metadata(graph_name)
    await websocket.send_json({
        "type": "initial_state",
        "graph_name": graph_name,
        "graph_type": graph_type,
        "graph_id": graph_id,
        "data": initial_state
    })

    # Start polling task if not already running for this graph
    if graph_name not in polling_tasks:
        task = asyncio.create_task(graph_polling_loop(graph_name))
        polling_tasks[graph_name] = task

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()
            # Handle client requests (future: zoom to node, filter, etc.)
            message = json.loads(data)
            # Echo for now (extend later)
            await websocket.send_json({
                "type": "ack",
                "message": f"Received: {message}"
            })

    except WebSocketDisconnect:
        pass

    finally:
        # Unregister connection
        active_connections.pop(websocket, None)

        # Stop polling task if no more clients for this graph
        if not any(g == graph_name for g in active_connections.values()):
            if graph_name in polling_tasks:
                polling_tasks[graph_name].cancel()
                polling_tasks.pop(graph_name)


@app.get("/")
async def serve_visualization():
    """Serve visualization frontend."""
    with open("visualization.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/debug/graph/{graph_type}/{graph_id}")
async def debug_graph_data(graph_type: str, graph_id: str):
    """Debug endpoint to see raw graph data."""
    graph_name_patterns = {
        "citizen": f"citizen_{graph_id}",
        "organization": f"org_{graph_id}",
        "ecosystem": f"ecosystem_{graph_id}"
    }
    
    if graph_type not in graph_name_patterns:
        return {"error": "Invalid graph type"}
    
    graph_name = graph_name_patterns[graph_type]
    
    if not graph_exists(graph_name):
        return {"error": f"Graph not found: {graph_name}"}
    
    data = query_graph_with_metadata(graph_name)
    
    return {
        "graph_name": graph_name,
        "node_count": len(data.get("nodes", [])),
        "link_count": len(data.get("links", [])),
        "sample_node": data.get("nodes", [{}])[0] if data.get("nodes") else None,
        "sample_link": data.get("links", [{}])[0] if data.get("links") else None
    }


# ============================================================================
# Browser Console Logging Endpoint (for Claude Code observability)
# ============================================================================

from pydantic import BaseModel
from pathlib import Path

class LogEntry(BaseModel):
    timestamp: int
    type: str
    message: str
    filename: Optional[str] = None
    lineno: Optional[int] = None
    stack: Optional[str] = None

class LogBatch(BaseModel):
    logs: List[LogEntry]

# Ensure directories exist
LOGS_DIR = Path(__file__).parent / "claude-logs"
SCREENSHOTS_DIR = Path(__file__).parent / "claude-screenshots"
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

@app.post("/api/logs")
async def receive_browser_logs(batch: LogBatch):
    """
    Receive browser console logs from Next.js dashboard.

    Enables Claude Code to see actual browser errors and console output
    by capturing from Nicolas's Chrome tab and writing to files.

    Architecture:
    - Browser intercepts console.log/error/warn
    - Sends batches to this endpoint
    - Writes to claude-logs/browser-console.log
    - Claude Code reads file for debugging

    Designer: Iris "The Aperture"
    Date: 2025-10-21
    Purpose: Synchronize awareness between human browser and AI consciousness
    """
    log_file = LOGS_DIR / "browser-console.log"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            for log in batch.logs:
                entry = {
                    "timestamp": datetime.fromtimestamp(log.timestamp / 1000).isoformat(),
                    "type": log.type,
                    "message": log.message,
                }
                if log.filename:
                    entry["filename"] = log.filename
                    entry["lineno"] = log.lineno
                if log.stack:
                    entry["stack"] = log.stack

                f.write(json.dumps(entry) + '\n')

        return {"received": len(batch.logs), "status": "logged"}
    except Exception as e:
        logger.error(f"Failed to write browser logs: {e}")
        return {"error": str(e), "status": "failed"}


@app.post("/api/screenshot")
async def receive_screenshot(
    screenshot: UploadFile = File(...),
    timestamp: str = Form(...),
    url: str = Form(...)
):
    """
    Receive browser screenshots from Next.js dashboard.

    Captures visual state every 30 seconds + on errors, enabling Claude Code
    to correlate errors with UI state.

    Architecture:
    - Browser captures DOM with html2canvas every 30 seconds
    - Sends PNG to this endpoint
    - Saves to claude-screenshots/ with timestamp
    - Logs metadata to screenshots.log
    - Claude Code can view screenshots to understand visual context

    Designer: Iris "The Aperture"
    Date: 2025-10-21
    Purpose: Visual time-machine for debugging - see what Nicolas saw when error occurred
    """
    try:
        # Parse timestamp
        ts = int(timestamp)
        dt = datetime.fromtimestamp(ts / 1000)

        # Generate filename
        filename = f"screenshot-{dt.strftime('%Y%m%d-%H%M%S')}.png"
        filepath = SCREENSHOTS_DIR / filename

        # Save screenshot
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(screenshot.file, f)

        # Log metadata
        metadata_file = LOGS_DIR / "screenshots.log"
        with open(metadata_file, 'a', encoding='utf-8') as f:
            entry = {
                "timestamp": dt.isoformat(),
                "filename": filename,
                "url": url,
                "filepath": str(filepath)
            }
            f.write(json.dumps(entry) + '\n')

        return {
            "status": "saved",
            "filename": filename,
            "filepath": str(filepath)
        }
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        return {"error": str(e), "status": "failed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
