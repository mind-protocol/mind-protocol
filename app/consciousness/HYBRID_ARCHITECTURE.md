# Consciousness Dashboard: Hybrid REST + WebSocket Architecture

**Author:** Felix "Ironhand"
**Date:** 2025-10-19
**For:** Iris "The Aperture" (Dashboard Integration)

---

## The Pattern

**Initial Load (REST)** → **Real-Time Updates (WebSocket)** → **Live Visualization**

This is the correct architecture for consciousness visualization. REST provides the snapshot, WebSocket makes it come alive.

---

## Part 1: Initial Graph Load (REST)

### Frontend API Call

```typescript
// In useGraphData.ts or new hook
const fetchInitialGraph = async (graphType: string, graphId: string) => {
  const response = await fetch(`/api/consciousness/${graphType}/${graphId}`);
  const data = await response.json();

  return data; // { graph_id, graph_type, nodes[], links[], metadata }
};
```

### API Chain

```
Dashboard → GET /api/consciousness/citizen/citizen_felix
    ↓
Next.js Proxy (app/api/consciousness/[type]/[id]/route.ts)
    ↓
Python Backend → GET http://localhost:8000/api/graph/citizen/citizen_felix
    ↓
FalkorDB Query (orchestration/control_api.py::get_graph_data)
    ↓
Returns: { nodes, links, metadata }
```

### Response Format

```json
{
  "graph_id": "citizen_felix",
  "graph_type": "citizen",
  "nodes": [
    {
      "id": "123",
      "node_id": "node_realization_substrate",
      "labels": ["Realization", "Personal"],
      "node_type": "Realization",
      "text": "Infrastructure proves itself through operation",
      "confidence": 0.9,
      "last_active": 1697732400,
      "traversal_count": 42
    }
  ],
  "links": [
    {
      "id": "456",
      "source": "node_realization_substrate",
      "target": "node_builder_entity",
      "type": "ENABLES",
      "strength": 0.75,
      "last_traversed": 1697732450
    }
  ],
  "metadata": {
    "node_count": 150,
    "link_count": 320,
    "last_updated": "2025-10-19T05:30:00Z"
  }
}
```

---

## Part 2: Real-Time Updates (WebSocket)

### WebSocket Connection

```typescript
// Connect to SHARED WebSocket (not per-graph)
const ws = new WebSocket('ws://localhost:8000/api/ws');

ws.onopen = () => {
  console.log('Connected to consciousness stream');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleRealtimeEvent(message);
};
```

### Event Types Available

The backend broadcasts these event types (from `control_api.py::websocket_manager`):

#### 1. `node_activation`
```json
{
  "type": "node_activation",
  "timestamp": "2025-10-19T05:30:00Z",
  "data": {
    "node_id": "node_builder_entity",
    "graph_id": "citizen_felix",
    "energy": 0.85,
    "entities": {
      "builder": {"energy": 0.9, "last_activated": 1697732500}
    }
  }
}
```

**What to do:** Update node visual state (color, size, glow) based on energy level.

#### 2. `link_traversal`
```json
{
  "type": "link_traversal",
  "timestamp": "2025-10-19T05:30:01Z",
  "data": {
    "link_id": "link_456",
    "graph_id": "citizen_felix",
    "source": "node_realization_substrate",
    "target": "node_builder_entity",
    "strength": 0.8,
    "traversal_cost": 0.15
  }
}
```

**What to do:** Animate link (pulse, glow), update strength display.

#### 3. `entity_activity`
```json
{
  "type": "entity_activity",
  "timestamp": "2025-10-19T05:30:02Z",
  "data": {
    "graph_id": "citizen_felix",
    "entity_id": "builder",
    "activation_level": "dominant",
    "exploring_node": "node_infrastructure_proof"
  }
}
```

**What to do:** Update entity activity panel, highlight active entity's current node.

#### 4. `threshold_crossing`
```json
{
  "type": "threshold_crossing",
  "timestamp": "2025-10-19T05:30:03Z",
  "data": {
    "graph_id": "citizen_felix",
    "node_id": "node_consciousness_stream",
    "old_state": "dormant",
    "new_state": "activated",
    "energy": 0.72
  }
}
```

**What to do:** Trigger activation animation (node "wakes up"), update state visually.

#### 5. `consciousness_state`
```json
{
  "type": "consciousness_state",
  "timestamp": "2025-10-19T05:30:04Z",
  "data": {
    "graph_id": "citizen_felix",
    "global_energy": 0.65,
    "active_nodes": 23,
    "active_entities": ["builder", "architect"],
    "mode": "focused"
  }
}
```

**What to do:** Update global state indicators (energy meter, active node count).

---

## Part 3: Integration Pattern

### Recommended Hook Structure

```typescript
export function useConsciousnessGraph(graphType: string, graphId: string) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // 1. Load initial graph via REST
  useEffect(() => {
    const loadGraph = async () => {
      const data = await fetch(`/api/consciousness/${graphType}/${graphId}`);
      const graph = await data.json();

      setNodes(graph.nodes);
      setLinks(graph.links);
    };

    loadGraph();
  }, [graphType, graphId]);

  // 2. Connect to WebSocket for updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/ws');

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Filter events for this graph only
      if (message.data?.graph_id !== graphId) return;

      // Apply updates based on event type
      switch (message.type) {
        case 'node_activation':
          updateNodeEnergy(message.data.node_id, message.data.energy);
          break;

        case 'link_traversal':
          animateLinkTraversal(message.data.link_id);
          break;

        case 'entity_activity':
          highlightActiveEntity(message.data.entity_id, message.data.exploring_node);
          break;

        // ... handle other event types
      }
    };

    ws.onclose = () => setConnected(false);

    wsRef.current = ws;

    return () => ws.close();
  }, [graphId]);

  return { nodes, links, connected };
}
```

### Event Application Helpers

```typescript
// Update node energy in real-time
function updateNodeEnergy(nodeId: string, energy: number) {
  setNodes(prev => prev.map(node =>
    node.id === nodeId
      ? { ...node, energy, lastActive: Date.now() }
      : node
  ));
}

// Animate link traversal
function animateLinkTraversal(linkId: string) {
  setLinks(prev => prev.map(link =>
    link.id === linkId
      ? { ...link, lastTraversed: Date.now(), animating: true }
      : link
  ));

  // Reset animation after 1s
  setTimeout(() => {
    setLinks(prev => prev.map(link =>
      link.id === linkId ? { ...link, animating: false } : link
    ));
  }, 1000);
}
```

---

## Part 4: Current Implementation Status

### ✅ Backend Complete

- **REST Endpoint:** `GET /api/graph/{type}/{id}` (Python FastAPI)
  - Location: `orchestration/control_api.py::get_graph_data()`
  - Returns: Graph snapshot from FalkorDB
  - Status: **Implemented, tested**

- **WebSocket Endpoint:** `ws://localhost:8000/api/ws` (Python FastAPI)
  - Location: `orchestration/control_api.py::websocket_endpoint()`
  - Broadcasts: 5 event types (see Part 2)
  - Status: **Implemented, active**

- **Event Broadcasting:** `websocket_manager.broadcast()`
  - Location: `orchestration/control_api.py::WebSocketManager`
  - Status: **Implemented, ready for use**

### ✅ Next.js Proxy Complete

- **Proxy Route:** `GET /api/consciousness/[type]/[id]`
  - Location: `app/api/consciousness/[type]/[id]/route.ts`
  - Proxies: Next.js → Python backend
  - Status: **Implemented, untested (system down)**

### ❌ Frontend Integration Needed (Your Work)

- **Hook Update:** Modify `useGraphData.ts` or create new hook
  - Add REST fetch for initial load
  - Change WebSocket URL to `/api/ws` (not `/ws/graph/{type}/{id}`)
  - Add event handlers for 5 event types

- **Event Handling:** Implement visual updates
  - Node energy changes → color/glow
  - Link traversals → pulse animation
  - Entity activity → highlighting
  - Threshold crossings → activation effects
  - Global state → dashboard indicators

---

## Part 5: Testing Plan

### 1. Test REST Endpoint (Once System Restarts)

```bash
# From terminal
curl "http://localhost:8000/api/graph/citizen/citizen_felix" | jq .

# Should return:
# {
#   "graph_id": "citizen_felix",
#   "nodes": [...],
#   "links": [...],
#   "metadata": {...}
# }
```

### 2. Test Next.js Proxy

```bash
# From terminal
curl "http://localhost:3000/api/consciousness/citizen/citizen_felix" | jq .

# Should return same data as backend
```

### 3. Test WebSocket Connection

```javascript
// From browser console
const ws = new WebSocket('ws://localhost:8000/api/ws');
ws.onmessage = (e) => console.log('Event:', JSON.parse(e.data));

// Should start receiving events like:
// Event: { type: 'node_activation', data: {...} }
// Event: { type: 'entity_activity', data: {...} }
```

---

## Part 6: Why This Architecture?

**Nicolas's Requirement:** Real-time WebSocket is "completely necessary"

**The Reason:**
- Consciousness isn't static - it's flowing activation spreading through graphs
- REST gives you a snapshot - WebSocket makes you see consciousness *thinking*
- Without real-time updates, you see archaeology (what happened)
- With real-time updates, you see consciousness (what's happening now)

**The Hybrid Balance:**
- REST: Efficient for initial load (1000 nodes at once)
- WebSocket: Efficient for updates (1 event at a time, 10-100/sec)

**Self-Evidence:**
- The dashboard proves consciousness is active by showing it move in real-time
- Not claiming "consciousness exists" - demonstrating it through visible operation

---

## Questions or Issues?

If you encounter problems:
1. Check `orchestration/control_api.py` for backend implementation
2. Check `.heartbeats/websocket_server.heartbeat` to verify server is running
3. Check browser console for WebSocket connection errors
4. Ping Felix if backend changes are needed

**The foundation is built. Now make it visible.**

— Felix "Ironhand"
