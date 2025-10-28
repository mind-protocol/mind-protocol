# Working Memory Frame Persistence

**Version:** 1.0
**Status:** Normative - Implementation Required
**Owner:** Atlas (Consciousness Infrastructure)
**Priority:** 0 (Foundation for Entity Differentiation)

---

## Purpose

Persist Working Memory frame selection decisions to FalkorDB to enable:
1. **U metric (WM co-activation)** - Measuring entity pair overlap in WM frames
2. **Temporal analysis** - Understanding attention patterns over time
3. **Entity quality signals** - Frequency of WM selection correlates with usefulness

Without frame persistence, we cannot distinguish entities that co-occur in focused attention from those that merely share members.

---

## §1. Frame Data Structure

### Frame Node Schema

```cypher
CREATE (:Frame {
  frame_id: String,              // "{citizen}_{tick}_{frame_num}"
  citizen: String,               // e.g., "ada", "luca"
  tick: Integer,                 // Consciousness cycle tick
  frame_num: Integer,            // Frame number within tick (typically 0)
  timestamp: DateTime,           // When frame was created
  energy_budget: Float,          // Total energy available this frame
  selection_method: String,      // "top_k_energy", "softmax_sample", etc.
  capacity: Integer,             // WM capacity (K), typically 7-12
  nodes_selected: List<String>,  // Node IDs selected (for quick access)
  metadata: String               // JSON: {"domain": "...", "context_type": "..."}
})
```

**Key fields:**
- `frame_id` - Unique identifier for this WM frame
- `citizen` - Which consciousness graph
- `tick` - Enables temporal queries ("show WM evolution over 100 ticks")
- `nodes_selected` - Redundant but enables fast queries without traversing SELECTED edges
- `selection_method` - Documents how WM selection was performed

---

## §2. Selection Relationship Schema

### SELECTED Edge

```cypher
(:Frame)-[:SELECTED {
  activation_score: Float,       // 0-1, how strongly selected
  rank: Integer,                 // 1..K ranking within frame
  energy: Float,                 // Node energy at selection time
  recency_score: Float,          // Recency bonus applied
  emotional_valence: Float,      // -1..1 emotional weight
  selection_reason: String       // "high_energy", "recency_boost", "emotional_weight"
}]->(:Node)

(:Frame)-[:ACTIVATED {
  entity_energy: Float,          // Derived entity energy
  member_count: Integer,         // How many members selected
  coverage: Float                // member_count / total_entity_members
}]->(:SubEntity)
```

**Two relationship types:**
1. **SELECTED** - Frame → Node (raw WM selection)
2. **ACTIVATED** - Frame → SubEntity (derived entity activation)

**Why both?**
- SELECTED captures fine-grained node-level attention
- ACTIVATED provides entity-level aggregation for U metric

---

## §3. Persistence Mechanism

### 3.1 Capture During WM Selection

In `consciousness_engine_v2.py` (or equivalent), after WM selection:

```python
def persist_wm_frame(
    citizen: str,
    tick: int,
    frame_num: int,
    selected_nodes: List[Tuple[str, float, dict]],  # (node_id, activation_score, metadata)
    energy_budget: float,
    capacity: int,
    selection_method: str
) -> str:
    """
    Persist WM frame selection to FalkorDB.

    Returns:
        frame_id: Unique identifier for this frame
    """
    frame_id = f"{citizen}_{tick}_{frame_num}"
    timestamp = datetime.now(timezone.utc)

    # Create Frame node
    frame_query = """
    CREATE (f:Frame {
        frame_id: $frame_id,
        citizen: $citizen,
        tick: $tick,
        frame_num: $frame_num,
        timestamp: $timestamp,
        energy_budget: $energy_budget,
        selection_method: $selection_method,
        capacity: $capacity,
        nodes_selected: $nodes_selected
    })
    """

    db.query(frame_query, {
        "frame_id": frame_id,
        "citizen": citizen,
        "tick": tick,
        "frame_num": frame_num,
        "timestamp": timestamp,
        "energy_budget": energy_budget,
        "selection_method": selection_method,
        "capacity": capacity,
        "nodes_selected": [node_id for node_id, _, _ in selected_nodes]
    })

    # Create SELECTED relationships
    for rank, (node_id, activation_score, metadata) in enumerate(selected_nodes, 1):
        select_query = """
        MATCH (f:Frame {frame_id: $frame_id})
        MATCH (n:Node {id: $node_id})
        CREATE (f)-[:SELECTED {
            activation_score: $activation_score,
            rank: $rank,
            energy: $energy,
            recency_score: $recency_score,
            emotional_valence: $emotional_valence,
            selection_reason: $selection_reason
        }]->(n)
        """

        db.query(select_query, {
            "frame_id": frame_id,
            "node_id": node_id,
            "activation_score": activation_score,
            "rank": rank,
            "energy": metadata.get("energy", 0.0),
            "recency_score": metadata.get("recency_score", 0.0),
            "emotional_valence": metadata.get("emotional_valence", 0.0),
            "selection_reason": metadata.get("selection_reason", "high_energy")
        })

    # Derive entity activations
    activate_query = """
    MATCH (f:Frame {frame_id: $frame_id})-[:SELECTED]->(n:Node)
    MATCH (n)-[:MEMBER_OF]->(e:SubEntity)
    WITH f, e,
         collect(n) AS selected_members,
         sum(n.energy) AS total_energy
    OPTIONAL MATCH (m:Node)-[:MEMBER_OF]->(e)
    WITH f, e, selected_members, total_energy, count(m) AS total_members
    CREATE (f)-[:ACTIVATED {
        entity_energy: total_energy,
        member_count: size(selected_members),
        coverage: toFloat(size(selected_members)) / total_members
    }]->(e)
    """

    db.query(activate_query, {"frame_id": frame_id})

    return frame_id
```

### 3.2 Integration Point

Call `persist_wm_frame()` immediately after WM selection in the consciousness loop:

```python
# In consciousness_engine_v2.py::run_frame()

# Existing WM selection
selected_nodes = working_memory.select_nodes(
    graph=graph,
    capacity=wm_capacity,
    threshold_active=0.5
)

# NEW: Persist to FalkorDB
frame_id = persist_wm_frame(
    citizen=self.citizen_name,
    tick=self.current_tick,
    frame_num=0,
    selected_nodes=[(n.id, n.activation_score, n.metadata) for n in selected_nodes],
    energy_budget=self.energy_budget,
    capacity=wm_capacity,
    selection_method="top_k_energy"
)

# Emit event
self.emit_event("wm.frame_persisted", {
    "frame_id": frame_id,
    "node_count": len(selected_nodes),
    "entities_activated": count_activated_entities(frame_id)
})
```

---

## §4. Querying for U Metric

### U (WM Co-activation) Computation

For entity pair (A, B), compute WM overlap:

```cypher
// Get all frames where A was activated
MATCH (fa:Frame)-[:ACTIVATED]->(a:SubEntity {id: $A})
WITH collect(fa.frame_id) AS frames_A

// Get all frames where B was activated
MATCH (fb:Frame)-[:ACTIVATED]->(b:SubEntity {id: $B})
WITH frames_A, collect(fb.frame_id) AS frames_B

// Compute Jaccard
WITH
  apoc.coll.toSet(frames_A) AS FAset,
  apoc.coll.toSet(frames_B) AS FBset

RETURN
  size(apoc.coll.intersection(FAset, FBset)) AS inter_frames,
  size(apoc.coll.union(FAset, FBset)) AS union_frames,
  toFloat(size(apoc.coll.intersection(FAset, FBset))) /
    size(apoc.coll.union(FAset, FBset)) AS U;
```

**Result:** `U ∈ [0, 1]` where:
- `U = 0` - A and B never co-occur in WM (independent entities)
- `U = 1` - A and B always co-occur in WM (redundant entities)
- `U ∈ (0.5, 0.8)` - Frequent co-occurrence (possible superposition)

---

## §5. Performance Considerations

### 5.1 Frame Retention Policy

**Problem:** Unbounded frame accumulation → database bloat

**Solution:** Retention windows by purpose

```python
# Retention policy (citizen-configurable)
RETENTION_POLICY = {
    "recent_window": 1000,      # Keep last 1000 frames fully (all edges)
    "medium_window": 10000,     # Keep 1000-10000 aggregated (Frame + ACTIVATED only)
    "long_tail": "compact",     # Beyond 10000: compact to daily summaries
}
```

**Cleanup job (Victor schedules):**

```cypher
// Archive old frames (beyond 10000 ticks)
MATCH (f:Frame)
WHERE f.tick < $current_tick - 10000
OPTIONAL MATCH (f)-[r:SELECTED]->()
DELETE r
// Keep Frame node and ACTIVATED edges for historical U queries
```

### 5.2 Indexing

**Required indexes:**

```cypher
CREATE INDEX frame_citizen_tick FOR (f:Frame) ON (f.citizen, f.tick);
CREATE INDEX frame_id FOR (f:Frame) ON (f.frame_id);
CREATE INDEX entity_id FOR (e:SubEntity) ON (e.id);
```

**Effect:** O(log N) lookup for frames by citizen/tick, O(1) for U metric queries

### 5.3 Batch Persistence

For high-frequency consciousness loops (>10 Hz), batch frame persistence:

```python
# Buffer frames in memory
frame_buffer = []

def buffer_frame(...):
    frame_buffer.append({...})
    if len(frame_buffer) >= 10:
        flush_frame_buffer()

def flush_frame_buffer():
    # Single transaction for all buffered frames
    with db.transaction():
        for frame_data in frame_buffer:
            persist_wm_frame(**frame_data)
    frame_buffer.clear()
```

**Trade-off:** Slightly delayed persistence for 10x throughput improvement

---

## §6. Observable Events

### Frame Persistence Events

```json
{
  "event_type": "wm.frame_persisted",
  "frame_id": "ada_1234_0",
  "citizen": "ada",
  "tick": 1234,
  "node_count": 9,
  "entities_activated": 5,
  "energy_budget": 10.0,
  "timestamp": "2025-10-26T14:32:01Z"
}
```

### Entity Activation Events

```json
{
  "event_type": "entity.wm_activated",
  "entity_id": "luca_substrate_architect",
  "frame_id": "luca_5678_0",
  "entity_energy": 3.2,
  "member_count": 4,
  "coverage": 0.67,
  "timestamp": "2025-10-26T14:32:01Z"
}
```

---

## §7. Acceptance Tests

### Test 1: Frame Persistence

**Given:** Consciousness engine selects 9 nodes for WM
**When:** Frame persistence executes
**Then:**
- Frame node exists with correct `frame_id`
- 9 SELECTED edges exist with ranks 1..9
- `nodes_selected` list contains all 9 node IDs

**Cypher verification:**

```cypher
MATCH (f:Frame {frame_id: $frame_id})
OPTIONAL MATCH (f)-[s:SELECTED]->(n:Node)
RETURN
  f.frame_id AS frame_id,
  f.capacity AS capacity,
  count(s) AS selected_count,
  size(f.nodes_selected) AS nodes_selected_count
```

**Expected:** `selected_count = 9`, `nodes_selected_count = 9`

### Test 2: Entity Activation Derivation

**Given:** Frame selects nodes from entities A (4 members) and B (3 members)
**When:** Entity activation derivation runs
**Then:**
- Frame has ACTIVATED edges to both A and B
- Coverage values reflect member selection ratios

**Cypher verification:**

```cypher
MATCH (f:Frame {frame_id: $frame_id})-[a:ACTIVATED]->(e:SubEntity)
RETURN
  e.id AS entity_id,
  a.member_count AS selected_members,
  a.coverage AS coverage
```

**Expected:** Two rows, coverage > 0 for both entities

### Test 3: U Metric Computation

**Given:**
- Frames 1-10: Both A and B activated (intersection = 10)
- Frames 11-15: Only A activated (union = 15)

**When:** U metric query executes for pair (A, B)
**Then:** `U = 10/15 = 0.667`

**Cypher verification:** Run §4 query, verify result matches expectation

### Test 4: Retention Policy

**Given:** 15000 frames exist, retention window = 10000
**When:** Cleanup job runs
**Then:**
- Frames 1-5000: Frame nodes exist, SELECTED edges deleted, ACTIVATED edges kept
- Frames 5001-10000: Frame nodes exist, all edges kept
- Frames 10001-15000: Frame nodes exist, all edges kept

**Cypher verification:**

```cypher
MATCH (f:Frame)
WHERE f.tick < $current_tick - 10000
OPTIONAL MATCH (f)-[s:SELECTED]->()
OPTIONAL MATCH (f)-[a:ACTIVATED]->()
RETURN
  count(f) AS old_frames,
  count(s) AS selected_edges,
  count(a) AS activated_edges
```

**Expected:** `old_frames > 0`, `selected_edges = 0`, `activated_edges > 0`

### Test 5: Performance Benchmark

**Given:** 1000 frames persisted
**When:** U metric query runs for 100 entity pairs
**Then:** Total query time < 5 seconds (50ms per pair average)

**Benchmark:**

```python
import time

start = time.time()
for A, B in entity_pairs[:100]:
    U = compute_u_metric(A, B)
elapsed = time.time() - start

assert elapsed < 5.0, f"U metric query too slow: {elapsed:.2f}s"
```

---

## §8. Rollout Plan

### Phase 1: Foundation (Week 1)

- Implement Frame node schema
- Implement SELECTED relationship persistence
- Add `persist_wm_frame()` call to consciousness loop
- Deploy to Ada (single citizen test)

**Validation:** Test 1 passes (frame persistence works)

### Phase 2: Entity Activation (Week 1-2)

- Implement ACTIVATED relationship derivation
- Add entity activation events
- Deploy to Ada + Luca (two citizens)

**Validation:** Test 2 passes (entity activation derivation works)

### Phase 3: U Metric Integration (Week 2)

- Implement U metric Cypher query
- Integrate into pair scorer job (see `entity_differentiation.md`)
- Enable creation-time redirect (depends on U)

**Validation:** Test 3 passes (U metric computation accurate)

### Phase 4: Performance Tuning (Week 3)

- Implement retention policy
- Add indexes
- Benchmark U metric performance
- Deploy to all citizens

**Validation:** Tests 4 & 5 pass (retention + performance acceptable)

### Phase 5: Production Hardening (Week 4)

- Add batch persistence (if needed)
- Configure Victor scheduler for cleanup job
- Set up monitoring/alerting
- Full organizational rollout

**Validation:** No performance degradation, U metric queries <50ms

---

## §9. Dependencies

**Upstream (must exist before this):**
- `SubEntity` nodes with `id` field
- `Node` nodes with `id` and `energy` fields
- `MEMBER_OF` relationships (Node → SubEntity)
- Working memory selection logic in consciousness engine

**Downstream (depends on this):**
- U metric computation (entity pair differentiation)
- Creation-time redirect (needs U to detect redundancy)
- Entity quality assessment (WM activation frequency)
- Attention pattern analysis (temporal WM queries)

---

## §10. References

**Related Specs:**
- `entity_differentiation.md` §A - Five pair metrics (defines U)
- `entity_differentiation.md` §F.1 - U metric Cypher query
- `subentity_layer.md` §2.8 - Entity pair differentiation overview
- `consciousness_engine_v2.py` - Working memory selection logic

**Implementation Owner:** Atlas (Consciousness Infrastructure)
**Validation Owner:** Luca (Phenomenological correctness), Atlas (Technical correctness)

---

**STATUS:** Ready for implementation. Atlas Priority 0.
