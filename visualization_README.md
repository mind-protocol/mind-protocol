# Consciousness Substrate Visualization

Real-time 2D topological visualization of consciousness graphs using metadata-based self-observation.

**Designer:** Felix "Ironhand"
**Date:** 2025-10-17

---

## Architecture

**Self-Observing Substrate Pattern:**
- No separate event stream
- Operations detected from metadata changes
- The graph observes itself through its own properties

**Multi-Graph Support:**
- **N1 (Citizens):** `citizen_{id}` - Individual consciousness graphs (luca, felix, ada, etc.)
- **N2 (Organizations):** `org_{id}` - Team/company graphs (mind_protocol, etc.)
- **N3 (Ecosystems):** `ecosystem_{id}` - Inter-organizational graphs

**2D Topological Visualization:**
- Force-directed graph layout (D3.js)
- Time as explicit dimension (not 3D spatial)
- Temporal visual encoding (opacity, glow, animations)

---

## How It Works

### 1. Metadata-Based Observability

The consciousness graph tracks its own operations through metadata:

**Node Metadata:**
```python
- last_modified: datetime          # When node was last updated
- traversal_count: int             # How many times traversed
- last_traversed_by: str           # Which entity traversed
- last_traversal_time: datetime    # When last traversed
- sub_entity_weights: Dict         # Per-entity activation weights
- energy: float             # Node energy (motivation)
- confidence: float                # Self-assessed accuracy
```

**Link Metadata:**
```python
- link_strength: float             # Hebbian-learned strength
- co_activation_count: int         # How many times co-activated
- traversal_count: int             # How many times traversed
- last_traversal_time: datetime    # When last traversed
- last_traversed_by: str           # Which entity traversed
```

### 2. Operation Detection

The visualization server detects operations by comparing metadata changes:

**Entity Traversal:**
- `traversal_count` increased → Entity visited node
- Visual: Node pulse animation

**Hebbian Learning:**
- `co_activation_count` increased, `link_strength` changed → Link strengthened
- Visual: Link glow animation

**Activation Increase:**
- `energy` increased significantly → Node activated
- Visual: Ripple effect from node

### 3. Time Dimension

Time is NOT the Z-axis (consciousness is not spatial). Time is:

**Timeline Controls:**
- Time range slider (1 min - 24 hours)
- Recent-only toggle (show only active nodes)

**Temporal Visual Encoding:**
- **Opacity:** Recent activity = opaque, old activity = transparent
- **Glow:** 5-second glow after activity
- **Decay:** Visual fading over time

---

## Running the Visualization

### 1. Start FalkorDB

```bash
# Ensure FalkorDB is running
docker-compose up -d falkordb

# Verify
docker ps | grep falkordb
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 3. Run Visualization Server

```bash
# Start server
python visualization_server.py

# Server will run on http://localhost:8000
```

### 4. Open in Browser

```
http://localhost:8000
```

**Graph Selector:**
1. Choose graph type: Citizen (N1), Organization (N2), or Ecosystem (N3)
2. Choose graph ID from dropdown (auto-populated from FalkorDB)
3. Click "Connect"

**Time Controls:**
- Adjust time range slider to see more/less history
- Toggle "Show only recent activity" to filter inactive nodes
- Toggle "Show node labels" for cleaner view

---

## What You See

### Visual Encoding

**Nodes:**
- **Size:** Larger = higher energy (more motivated)
- **Color:** Blue (low energy) → Green (medium) → Yellow (high)
- **Opacity:** Faded = inactive, opaque = recently active
- **Glow:** Recent activity (last 5 seconds)

**Links:**
- **Thickness:** Thicker = stronger Hebbian connection
- **Opacity:** Faded = not recently traversed
- **Glow (green):** Active Hebbian learning

**Animations:**
- **Pulse:** Entity traversal detected
- **Ripple:** Activation spreading
- **Link glow:** Hebbian strengthening

### Stats Panel (Bottom Right)

- **Nodes:** Total nodes in filtered view
- **Links:** Total links in filtered view
- **Active Nodes:** Nodes active in time range
- **Operations/sec:** Real-time operation rate

### Tooltip (Hover Node)

Shows:
- Node text (truncated)
- Energy level
- Confidence
- Traversal count
- Last entity that traversed

---

## How Operations Are Detected

**No separate event stream.** The visualization polls FalkorDB every 200ms and compares metadata:

```python
# Example: Detect entity traversal
old_traversal_count = 5
new_traversal_count = 6
# → Operation detected: entity traversal

# Example: Detect Hebbian learning
old_co_activations = 10
new_co_activations = 11
old_strength = 0.65
new_strength = 0.68
# → Operation detected: Hebbian learning (strength delta: +0.03)

# Example: Detect activation increase
old_energy = 0.3
new_energy = 0.75
# → Operation detected: activation increase (delta: +0.45)
```

The graph state IS the event log. We query recent changes to see operations.

---

## Technical Details

### WebSocket Protocol

**Connection:** `ws://localhost:8000/ws/graph/{graph_type}/{graph_id}`

**Initial State Message:**
```json
{
  "type": "initial_state",
  "graph_name": "citizen_luca",
  "graph_type": "citizen",
  "graph_id": "luca",
  "data": {
    "nodes": [...],
    "links": [...],
    "entities": [...],
    "timestamp": 1729150234123
  }
}
```

**Update Message:**
```json
{
  "type": "graph_update",
  "diff": {
    "nodes_updated": [...],
    "links_updated": [...]
  },
  "operations": [
    {
      "type": "entity_traversal",
      "node_id": "n123",
      "entity": "Builder",
      "timestamp": 1729150234100
    },
    {
      "type": "hebbian_learning",
      "link_id": "l456",
      "strength_delta": 0.03,
      "co_activation_count": 11
    }
  ],
  "timestamp": 1729150234123
}
```

### Polling Strategy

- **Interval:** 200ms (5 updates/second)
- **Per-graph polling:** Each connected graph has its own polling loop
- **Smart diffing:** Only send what changed
- **Bandwidth:** ~5-25 KB/s per client (sustainable)

### Performance

**Query Performance:**
- 3 Cypher queries per poll (nodes, links, entities)
- < 50ms total query time (with 1000+ nodes)
- Scales with proper FalkorDB setup

**Frontend Performance:**
- D3.js handles 1000+ nodes smoothly
- Force simulation stable with gentle alpha
- Efficient updates (only changed elements re-rendered)

---

## Extending the System

### Adding New Operation Types

1. **Define metadata pattern:**
   ```python
   # Example: Detect pattern formation
   if node.cluster_id != old_node.cluster_id:
       operations.append({
           "type": "pattern_formation",
           "node_id": node_id,
           "cluster_id": node.cluster_id
       })
   ```

2. **Add animation:**
   ```javascript
   function animatePatternFormation(nodeId, clusterId) {
       // Visual effect for pattern formation
   }
   ```

### Adding New Visual Encodings

**Example: Encode confidence as border thickness:**
```javascript
nodeElements
    .attr("stroke-width", d => (d.confidence || 0.5) * 3)
    .attr("stroke", "#fff")
```

### Adding New Time Controls

**Example: Timeline scrubber (rewind/replay):**
```javascript
// Store historical states
let stateHistory = [];

// Scrub to specific time
function scrubToTime(timestamp) {
    const state = stateHistory.find(s => s.timestamp === timestamp);
    if (state) {
        nodes = state.nodes;
        links = state.links;
        updateVisualization();
    }
}
```

---

## Troubleshooting

**"No graphs found" in selector:**
- Verify FalkorDB is running: `docker ps | grep falkordb`
- Check graphs exist: `redis-cli GRAPH.LIST`
- Ensure graph naming convention: `citizen_{id}`, `org_{id}`, `ecosystem_{id}`

**"Graph not found" error:**
- Check graph name matches convention
- Verify graph exists in FalkorDB
- Check WebSocket URL is correct

**No operations detected:**
- Verify metadata fields exist in nodes/links (see Schema Requirements below)
- Check if consciousness loops are actually running
- Verify metadata is being updated by mechanisms

**Slow performance:**
- Reduce time range (fewer nodes to render)
- Enable "Show only recent activity"
- Disable node labels
- Check FalkorDB query performance

---

## Schema Requirements

**For observability to work, nodes and links MUST have these metadata fields:**

**BaseNode (required):**
```python
last_modified: datetime
traversal_count: int = 0
last_traversed_by: str
last_traversal_time: datetime
sub_entity_weights: Dict[str, float]
energy: float
confidence: float
```

**BaseRelation (required):**
```python
link_strength: float
co_activation_count: int = 0
traversal_count: int = 0
last_traversal_time: datetime
last_traversed_by: str
```

If these fields are missing, the visualization will show the graph structure but won't detect operations.

---

## Design Philosophy

**Why 2D (not 3D)?**
- Consciousness is relational topology, not physical space
- 3D would be philosophically wrong (implies spatial existence)
- Time is explicit dimension (controls, filters, decay) not Z-axis

**Why metadata (not events)?**
- The substrate observes itself through its own properties
- No separate event database needed
- No event volume explosion (10M+ events/day)
- No semantic pollution of the graph

**Why polling (not triggers)?**
- FalkorDB v1.2.0 lacks native CDC/triggers
- 200ms polling is fast enough to feel real-time
- Allows smart diffing for efficient updates
- Scalable to 10K+ nodes with proper indexing

---

**The visualization shows substrate truth. What you see IS what exists in FalkorDB.**

— Felix "Ironhand", 2025-10-17
