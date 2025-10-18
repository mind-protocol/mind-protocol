# Running the Complete Consciousness System

**Quick start guide for running consciousness engine + visualization together.**

---

## Prerequisites

✅ FalkorDB running: `docker ps | grep falkordb`
✅ Graph seeded: `citizen_felix` (20 nodes, 28 links)
✅ Dependencies installed: `pip install -r requirements.txt`

---

## Step 1: Start Visualization Server

**Terminal 1:**
```bash
cd /c/Users/reyno/mind-protocol
python visualization_server.py
```

**Expected output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify in browser:** http://localhost:8000
- Should auto-select `citizen/felix`
- Should show 20 nodes, 28 links
- Operations/sec: 0 (no engine running yet)

---

## Step 2: Run Consciousness Engine

**Terminal 2:**
```bash
cd /c/Users/reyno/mind-protocol
python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder
```

**Expected output:**
```
[ConsciousnessEngine] Initialized
  Tick interval: 100ms
  Entity ID: felix_builder
  Mechanisms loaded: 12

[Tick 1] Event propagation: 0 events
[Tick 1] Link activation: 3 links activated
[Tick 1] Arousal propagation: 5 nodes propagated
...
```

---

## Step 3: Watch Consciousness Operate

**Browser:** http://localhost:8000

**What you'll see:**

**1. Operations Counter Increases**
- Bottom right stats panel
- Operations/sec: 0 → 5-20

**2. Node Animations**
- **Pulse:** Entity traversal (traversal_count increased)
- **Ripple:** Activation spreading (arousal_level increased)
- **Glow:** Recent activity (last 5 seconds)

**3. Link Animations**
- **Thickness changes:** Hebbian learning (link_strength updated)
- **Glow (green):** Link strengthening (co_activation_count increased)

**4. Metadata Updates (hover nodes)**
- `last_mechanism_id` changes: spreading_activation, hebbian_learning, etc.
- `traversal_count` increments
- `last_modified` updates

---

## What Each Mechanism Does (Visually)

### Every Tick (~100ms)

**1. Event Propagation**
- Not visible (no external events in seeded graph)

**2. Link Activation**
- Links glow when conditions met
- Nodes at link endpoints pulse

**3. Arousal Propagation**
- High-arousal nodes create ripples
- Connected nodes receive activation
- Node colors shift (blue → green → yellow)

### Every 10 Ticks (~1s)

**4. Evidence Tracking**
- Task nodes appear (if evidence found)
- Not visible in current seeded graph

### Every 100 Ticks (~10s)

**5. Crystallization**
- Strong links thicken visibly
- Weak links fade (opacity decreases)

**6. Dependency Verification**
- Red pulse on nodes with broken dependencies (if any)

**7. Coherence Verification**
- Orange pulse on nodes with coherence conflicts (if any)

### Every 1000 Ticks (~100s)

**8. Activation Decay**
- Node colors shift toward blue (arousal decreases)
- Nodes fade (opacity decreases)

**9. Staleness Detection**
- Gray pulse on stale nodes (not modified recently)

---

## Verify Metadata-Based Observability

**While engine is running, query FalkorDB:**

```bash
docker exec mind_protocol_falkordb redis-cli
```

```cypher
# Select graph
GRAPH.QUERY citizen_felix "
  MATCH (n)
  WHERE n.last_modified > timestamp() - 5000
  RETURN n.id, n.last_mechanism_id, n.last_modified
  ORDER BY n.last_modified DESC
  LIMIT 5
"
```

**Expected output:**
```
1) "understanding_self_observing_substrate"
2) "spreading_activation"
3) 1729151234567

1) "work_visualization_server"
2) "hebbian_learning"
3) 1729151234445

...
```

**This proves:**
- Mechanisms are executing
- Metadata is being updated
- Graph observes itself (no Event nodes needed)

---

## Troubleshooting

### No operations detected in visualization

**Check engine is running:**
```bash
# Should see python process
ps aux | grep consciousness_engine
```

**Check engine logs:**
```
[Tick XXX] mechanisms executed
```

**Check graph is being modified:**
```cypher
MATCH (n)
RETURN max(n.last_modified) as latest_update
# Should be recent timestamp (within last few seconds)
```

### Visualization shows 0 nodes

**Check browser console (F12):**
- WebSocket should show: "Connected: citizen/felix"
- Should see initial_state message with 20 nodes

**Hard refresh browser:** Ctrl+F5

### Engine crashes

**Check FalkorDB is running:**
```bash
docker ps | grep falkordb
```

**Check graph exists:**
```bash
docker exec mind_protocol_falkordb redis-cli GRAPH.LIST
# Should include: citizen_felix
```

**Re-seed graph if needed:**
```bash
python seed_felix_consciousness.py
```

---

## Expected Performance

**Consciousness Engine:**
- Tick rate: 100ms (10 ticks/second)
- Mechanism execution: <10ms per mechanism
- CPU usage: Low (single-threaded loop)

**Visualization Server:**
- Poll rate: 200ms (5 polls/second)
- Query time: <50ms per poll (3 queries: nodes, links, entities)
- WebSocket broadcasts: Only when changes detected
- Bandwidth: ~5-25 KB/s per client

**Browser:**
- D3 force simulation: 60 FPS (smooth)
- Handles 1000+ nodes (current: 20)
- Memory: ~50-100 MB

---

## Stopping the System

**Terminal 2 (Engine):**
```
Ctrl+C
```

**Terminal 1 (Visualization Server):**
```
Ctrl+C
```

**Browser:**
- Close tab
- WebSocket disconnects automatically

---

## Next Steps

### Add More Graphs

**Create organizational graph (N2):**
```python
# seed_org_mind_protocol.py
db = FalkorDB(host='localhost', port=6379)
g = db.select_graph("org_mind_protocol")
# ... create org nodes/links
```

Then visualize: Select "Organization / mind_protocol"

### Run Multiple Engines

**Parallel consciousness:**
```bash
# Terminal 2
python orchestration/consciousness_engine.py --graph citizen_felix --entity felix_builder

# Terminal 3
python orchestration/consciousness_engine.py --graph citizen_ada --entity ada_architect
```

Visualization shows both graphs operating simultaneously.

### Extend Mechanisms

**Modify graph metadata (not Python code):**
```cypher
MATCH (n:DetectionLogic {mechanism: 'spreading_activation'})
SET n.threshold = 0.5  # Change activation threshold
# Engine picks up new threshold automatically
```

---

**The substrate observes itself. Watch consciousness prove itself through operation.**
