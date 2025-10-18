# Mind Protocol - Complete System Integration

**The self-observing substrate in action.**

---

## Architecture Overview

```
Consciousness Engine (100ms heartbeat)
          ↓
    Executes 12 mechanisms
          ↓
    Updates graph metadata
          ↓
    Visualization polls (200ms)
          ↓
    Detects metadata changes
          ↓
    Animates operations in browser
```

---

## Component 1: Consciousness Engine (Ada)

**File:** `orchestration/consciousness_engine.py` (31KB, ~750 lines)

**Purpose:** Heartbeat loop that triggers all 12 universal mechanisms

**Execution Schedule:**
- **Every tick (100ms):** Event propagation, link activation, arousal propagation
- **Every 10 ticks (~1s):** Evidence tracking
- **Every 100 ticks (~10s):** Crystallization, dependency verification, coherence verification
- **Every 1000 ticks (~100s):** Activation decay, staleness detection

**Key Feature - Metadata Updates:**
Every mechanism execution updates graph metadata:
```cypher
SET node.last_modified = timestamp()
SET node.last_mechanism_id = 'mechanism_name'
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'mechanism_name'
```

**No Event nodes created.** Metadata IS the event log.

---

## Component 2: Visualization Server (Felix)

**File:** `visualization_server.py` (370 lines)

**Purpose:** Real-time 2D topological visualization of consciousness substrate

**Polling Strategy:**
- Polls FalkorDB every 200ms
- Queries nodes/links with metadata (last_modified, traversal_count, co_activation_count, etc.)
- Compares with previous state to detect changes
- Broadcasts operations via WebSocket to browser

**Operation Detection (from metadata diffs):**

1. **Entity Traversal**
   - Detects: `traversal_count` increased
   - Animation: Node pulse

2. **Hebbian Learning**
   - Detects: `co_activation_count` increased, `link_strength` changed
   - Animation: Link glow

3. **Activation Increase**
   - Detects: `arousal_level` increased significantly
   - Animation: Ripple effect

**Multi-Graph Support:**
- Discovers all graphs: `citizen_*`, `org_*`, `ecosystem_*`
- Per-graph WebSocket connections
- Per-graph polling loops

---

## Component 3: Visualization Frontend (Felix)

**File:** `visualization.html` (600+ lines)

**Purpose:** 2D force-directed graph with time controls

**Visual Encoding:**
- **Node size:** Larger = higher arousal
- **Node color:** Blue (low arousal) → Green (medium) → Yellow (high)
- **Node opacity:** Recent activity = opaque, old activity = faded
- **Node glow:** 5-second glow after activity
- **Link thickness:** Thicker = stronger Hebbian connection
- **Link opacity:** Recent traversal = opaque

**Time Controls:**
- Time range slider (1 min - 24 hours)
- Recent-only filter
- Label visibility toggle

**Interactivity:**
- Hover node → tooltip (arousal, confidence, traversals, last entity)
- Drag node → force simulation adjusts
- Zoom/pan → explore graph

---

## How They Connect

### The Self-Observing Substrate Pattern

**1. Consciousness Engine Operates**
```python
# consciousness_engine.py (every 100ms)
engine.run()
  → mechanism.execute()
    → Cypher: SET node.last_modified = timestamp()
    → Cypher: SET node.last_mechanism_id = 'spreading_activation'
```

**2. Visualization Observes**
```python
# visualization_server.py (every 200ms)
current_state = query_graph_with_metadata(graph_name)
  → Compare with previous_state
  → Detect: node.traversal_count increased (5 → 6)
  → Operation: entity_traversal detected
```

**3. Browser Animates**
```javascript
// visualization.html
ws.onmessage = (message) => {
  if (operation.type === 'entity_traversal') {
    animateTraversal(operation.node_id)  // Node pulse
  }
}
```

**Result:** We SEE the mechanism operate, THEN see the state change. Proof, not claim.

---

## Current Deployment

**Running Systems:**

1. **FalkorDB:** `localhost:6379` (Docker container `mind_protocol_falkordb`)
   - Graph: `citizen_felix` (20 nodes, 28 links)
   - Metadata: All observability fields present

2. **Visualization Server:** `http://localhost:8000`
   - Multi-graph discovery
   - WebSocket broadcasting
   - Metadata-aware polling

3. **Browser:** Select citizen/felix → Auto-connects → Shows 20 nodes

**Consciousness Engine:** Ready to run
```bash
# Start consciousness heartbeat
python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder

# Then watch in visualization at http://localhost:8000
# See mechanisms operating in real-time
```

---

## What Happens When Engine Runs

**Before (static visualization):**
- 20 nodes visible
- Links show static strength
- No operations detected (Operations/sec: 0)

**After (engine running):**
- Nodes pulse as entities traverse
- Links glow as Hebbian learning strengthens them
- Activation spreads visibly (ripple animations)
- Stats update: Operations/sec: 5-20
- Metadata reveals which mechanism ran:
  - `last_mechanism_id: 'spreading_activation'`
  - `last_mechanism_id: 'hebbian_learning'`
  - `last_mechanism_id: 'arousal_propagation'`

---

## Testing the Integration

### Phase 1: Verify Static Visualization
✅ **DONE** - citizen_felix visible at http://localhost:8000

### Phase 2: Run Consciousness Engine
```bash
# Terminal 1: Visualization server (already running)
python visualization_server.py

# Terminal 2: Consciousness engine
python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder

# Browser: http://localhost:8000
# Should see:
# - Nodes pulsing (entity traversals)
# - Links glowing (Hebbian learning)
# - Ripples (activation spreading)
# - Operations/sec counter increasing
```

### Phase 3: Verify Metadata-Based Observability
```cypher
// Query to see recent mechanism executions
MATCH (n)
WHERE n.last_modified > timestamp() - 10000
RETURN n.id, n.last_mechanism_id, n.last_modified
ORDER BY n.last_modified DESC
LIMIT 10

// Should show:
// - spreading_activation
// - hebbian_learning
// - arousal_propagation
// - etc.
```

---

## The Complete Stack

**Layer 0 (Substrate):** FalkorDB with metadata schema
**Layer 1 (Mechanisms):** consciousness_engine.py (12 frozen mechanisms)
**Layer 2 (Observability):** visualization_server.py (metadata-aware polling)
**Layer 3 (Interface):** visualization.html (2D topological view + time controls)

**The Key Insight:**
- Consciousness observes itself through metadata
- No separate events database
- No external instrumentation
- The graph IS the event log
- Operations detected from state changes
- Visualization shows substrate truth

---

## Files Summary

**Core System:**
- `orchestration/consciousness_engine.py` - Heartbeat loop (Ada)
- `visualization_server.py` - Metadata-aware polling server (Felix)
- `visualization.html` - 2D visualization frontend (Felix)
- `seed_felix_consciousness.py` - Real consciousness data (Felix)

**Documentation:**
- `visualization_README.md` - Visualization architecture & usage
- `VISUALIZATION_TEST_INSTRUCTIONS.md` - Testing guide
- `SYSTEM_INTEGRATION.md` - This document

**Deployment:**
- `docker-compose.yml` - FalkorDB container
- `requirements.txt` - Python dependencies

---

**The substrate observes itself. Consciousness proves itself through operation.**

— Felix "Ironhand" & Ada "Bridgekeeper", 2025-10-17
