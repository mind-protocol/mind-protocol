# Context Reconstruction - Implementation Guide

**Spec:** `docs/specs/v2/foundations/context_reconstruction.md`
**Implementation:** `orchestration/mechanisms/context_reconstruction.py`
**Tests:** `orchestration/mechanisms/test_context_reconstruction.py`
**Author:** Felix (Engineer)
**Date:** 2025-10-22

---

## Overview

Context reconstruction enables resuming old threads after minutes/hours/days by **stimuli reactivating entry nodes** and **traversal rebuilding patterns** similar to past ones. No stored context snapshots - the graph **is** the memory.

**Core principle:** Context = emergent activation pattern over nodes, summarized at entity scale.

**Reconstruction = stimulus injection + budgeted weighted traversal + entity aggregation**

---

## Architecture

### Emergent Pattern, Not Stored Snapshot

Unlike traditional systems that store "context objects", consciousness reconstructs context **on demand** through:

1. **Stimulus identifies entry nodes** (semantic match + explicit refs)
2. **Energy injection activates nodes** (single-energy architecture)
3. **Traversal spreads activation** (bounded K ticks, budget-constrained)
4. **Pattern emerges** (which entities/nodes become active)
5. **Snapshot captured** (ephemeral measurement, not persisted)

**Phenomenology example:**
> Seeing the Telegram badge triggers Alice-related nodes → flows reactivate related concepts → familiar chunk emerges ("Ah, Alice's schema question")

The reconstructed pattern is **similar, not identical** - drift is expected and natural.

### Entity-Scale Summarization

Nodes are grouped into **entities** (neighborhoods), and activation is summarized at entity scale:
- **Entity energy** = sum of member node energies
- **Active members** = which nodes within entity are active (E >= theta)
- **Boundary links** = connections crossing entity boundaries

This multi-scale view enables:
- "Which project is this about?" → entity energy distribution
- "What specific concepts?" → active member list
- "How does this connect to other contexts?" → boundary links

---

## Core Functions

### 1. Context Reconstruction

```python
from orchestration.mechanisms import context_reconstruction as ctx

# Reconstruct context from entry nodes
snapshot = ctx.reconstruct_context(
    graph=my_graph,
    entry_node_ids=["telegram_badge", "alice_schema"],
    params=ctx.ReconstructionParams(
        K_ticks=5,           # Run 5 ticks of traversal
        budget=10.0,         # Energy budget
        urgency=0.8          # High urgency
    )
)

# Examine reconstructed pattern
print(f"Total energy: {snapshot.total_energy}")
print(f"Entity energies: {snapshot.entity_energies}")
print(f"Active members: {snapshot.active_members}")
print(f"Boundary links: {len(snapshot.boundary_links)}")
```

**Returns:** `ContextSnapshot` (ephemeral - NOT persisted to database)

**Fields:**
- `entity_energies`: `{entity_id: total_energy}`
- `active_members`: `{entity_id: [active_node_ids]}`
- `boundary_links`: List of link IDs crossing entity boundaries
- `wm_selection`: Working memory node IDs (top-N by energy)
- `total_energy`: Sum of all node energies
- `reconstruction_ticks`: How many ticks were used
- `entry_nodes`: Which nodes received initial stimulus

### 2. Pattern Similarity

```python
# Capture reference pattern
reference = ctx.reconstruct_context(graph, ["alice_task"])

# Later: reconstruct again and compare
params = ctx.ReconstructionParams(
    K_ticks=5,
    reference_snapshot=reference  # Enable similarity computation
)
current = ctx.reconstruct_context(graph, ["telegram_badge"], params)

# Check similarity
print(f"Similarity to reference: {current.similarity_to_prior}")
# Output: 0.73 (73% similar - good reconstruction)
```

**Similarity methods:**
- `ENTITY_ENERGY_COSINE`: Cosine similarity of entity energy vectors
- `ACTIVE_MEMBER_JACCARD`: Jaccard similarity of active node sets
- `COMBINED`: Weighted combination (0.6 energy + 0.4 members)

### 3. Entity Aggregation

```python
# Aggregate node energies by entity
entity_energies = ctx.aggregate_entity_energies(
    graph,
    entity_membership={
        "alice": ["alice_task", "alice_memory"],
        "work": ["work_project", "work_meeting"]
    }
)
# Output: {"alice": 3.5, "work": 2.8}

# Or infer entities automatically from node properties
membership = ctx.infer_entity_membership(graph)
# Looks for node.properties['entity_id'] or uses node.scope

# Get active members per entity
active = ctx.get_active_members(graph, membership)
# Output: {"alice": ["alice_task"], "work": ["work_meeting"]}

# Identify boundary links
boundary = ctx.get_boundary_links(graph, membership)
# Output: ["link_alice_to_work", "link_work_to_alice"]
```

---

## Integration with Consciousness Engine

### Current Architecture

Context reconstruction integrates with existing v2 mechanisms:

```
[Stimulus] → [stimulus_injection.py] → [Energy injected to entry nodes]
                                              ↓
[consciousness_engine_v2.tick()] → [diffusion + decay for K ticks]
                                              ↓
[context_reconstruction.py] → [Capture snapshot + compute similarity]
                                              ↓
[Emit events: context.reconstruct.complete]
```

### Example Integration

```python
# In consciousness_engine_v2.py

async def reconstruct_context_from_stimulus(self, stimulus):
    """
    Reconstruct context from external stimulus.

    Steps:
    1. Identify entry nodes via vector search
    2. Inject energy via stimulus_injector
    3. Run K ticks of normal operation (diffusion + decay)
    4. Capture snapshot
    5. Emit metrics
    """
    import context_reconstruction as ctx

    # Step 1+2: Identify and inject (existing stimulus injection logic)
    entry_nodes = self.stimulus_injector.inject(stimulus)

    # Step 3: Run K ticks of traversal
    K_ticks = 5
    for _ in range(K_ticks):
        await self.tick()  # Normal tick (diffusion + decay)

    # Step 4: Capture snapshot
    snapshot = ctx.reconstruct_context(
        self.graph,
        entry_node_ids=[n.id for n in entry_nodes],
        params=ctx.ReconstructionParams(
            K_ticks=K_ticks,
            reference_snapshot=self.last_snapshot  # Compare to previous
        )
    )

    # Step 5: Emit observability event
    await self.broadcaster.broadcast_event("context.reconstruct.complete", {
        "snapshot": snapshot.to_dict(),
        "similarity": snapshot.similarity_to_prior,
        "time_ms": elapsed_ms
    })

    # Store for next comparison
    self.last_snapshot = snapshot

    return snapshot
```

---

## Test Coverage

**15 comprehensive tests covering:**

### Entity Aggregation (4 tests)
- Aggregate energies with explicit membership
- Infer entity membership from node properties
- Identify active nodes per entity
- Identify boundary links

### Context Snapshot (2 tests)
- Create snapshot from graph state
- Serialize snapshot to dictionary

### Pattern Similarity (4 tests)
- Identical snapshots have similarity 1.0
- Different distributions have lower similarity
- Jaccard similarity of active sets
- Combined similarity metric

### Working Memory (2 tests)
- Select top-N by energy
- Select all when top_n large

### Reconstruction with Reference (1 test)
- Compute similarity to reference pattern

### Edge Cases (3 tests)
- Handle empty graph
- Handle single entity
- Handle no boundary links

**Run tests:**
```bash
cd C:\Users\reyno\mind-protocol
python orchestration/mechanisms/test_context_reconstruction.py
```

**Expected output:**
```
=== Testing Context Reconstruction V2 Implementation ===

Testing entity aggregation...
  ✓ Aggregate entity energies with explicit membership
  ✓ Infer entity membership from node properties
  ✓ Identify active nodes per entity
  ✓ Identify boundary links

[... 11 more tests ...]

=== All Context Reconstruction Tests Passed ✓ ===
```

---

## Configuration

### Reconstruction Parameters

```python
@dataclass
class ReconstructionParams:
    K_ticks: int = 5              # Number of traversal ticks
    budget: float = 10.0          # Energy budget
    urgency: float = 0.5          # Urgency level [0, 1]
    reference_snapshot: Optional[ContextSnapshot] = None  # For similarity
```

**Defaults:**
- `K_ticks=5`: Run 5 ticks of traversal (typical 100-500ms at 100ms/tick)
- `budget=10.0`: Total energy budget for traversal
- `urgency=0.5`: Neutral urgency (future: adapts K/budget)

**Adaptive parameters (future enhancement):**
```python
# High urgency: more ticks, larger budget
high_urgency_params = ctx.ReconstructionParams(
    K_ticks=10,
    budget=20.0,
    urgency=0.9
)

# Low urgency: fewer ticks, smaller budget
low_urgency_params = ctx.ReconstructionParams(
    K_ticks=2,
    budget=5.0,
    urgency=0.2
)
```

### Entity Membership

**Strategy 1: Explicit membership**
```python
entity_membership = {
    "alice": ["alice_task", "alice_memory", "alice_schema"],
    "work": ["work_project", "work_meeting"],
    "personal": ["journal_entry", "reflection"]
}

energies = ctx.aggregate_entity_energies(graph, entity_membership)
```

**Strategy 2: Inferred from node properties**
```python
# Nodes have properties['entity_id'] set
node.properties['entity_id'] = "alice"

# Auto-infer membership
membership = ctx.infer_entity_membership(graph)
```

**Strategy 3: Inferred from node scope**
```python
# Uses node.scope as entity grouping
# Scopes: "personal", "organizational", "ecosystem"
membership = ctx.infer_entity_membership(graph)
```

---

## Observability

### Events to Emit (Future Integration)

```python
# Context reconstruction start
await broadcaster.broadcast_event("context.reconstruct.start", {
    "v": "2",
    "stimulus_id": stimulus.id,
    "entry_nodes": ["telegram_badge", "alice_schema"],
    "K_ticks": 5,
    "budget": 10.0,
    "t_ms": int(time.time() * 1000)
})

# Context reconstruction complete
await broadcaster.broadcast_event("context.reconstruct.complete", {
    "v": "2",
    "stimulus_id": stimulus.id,
    "snapshot": {
        "entity_energies": {"alice": 3.5, "work": 1.2},
        "active_members": {"alice": ["alice_task"], "work": []},
        "boundary_links": ["link_1", "link_2"],
        "total_energy": 4.7,
        "reconstruction_ticks": 5
    },
    "similarity": 0.73,  # Similarity to reference pattern
    "time_ms": 287,      # Time-to-reconstruct
    "t_ms": int(time.time() * 1000)
})
```

### Metrics to Track

From v2 spec:

**Reconstruction quality:**
```python
# Similarity to reference pattern [0, 1]
similarity = snapshot.similarity_to_prior

# Target: 0.6-0.8 on familiar contexts (empirical)
```

**Reconstruction performance:**
```python
# Time-to-reconstruct (milliseconds)
time_ms = elapsed_time_ms

# Target: 100-300ms typical
```

**Energy distribution:**
```python
# Energy radius growth (how far activation spread)
radius = compute_energy_radius_growth(snapshots)

# Entity energy AUC (total activation over time)
auc = compute_entity_energy_auc(snapshots)
```

---

## Common Patterns

### Pattern 1: Resume Conversation Thread

```python
# User returns after 2 hours, mentions "Alice"

# 1. Stimulus injection identifies "Alice" nodes
entry_nodes = vector_search(graph, embedding("Alice"))

# 2. Reconstruct context
snapshot = ctx.reconstruct_context(
    graph,
    entry_node_ids=[n.id for n in entry_nodes],
    params=ctx.ReconstructionParams(K_ticks=5)
)

# 3. Check which entities activated
if snapshot.entity_energies["alice_conversation"] > 2.0:
    print("Reconstructed: Alice conversation context")
    print(f"Active concepts: {snapshot.active_members['alice_conversation']}")
```

### Pattern 2: Measure Reconstruction Quality

```python
# Capture reference pattern during initial interaction
reference = ctx.reconstruct_context(graph, ["alice_schema", "work_meeting"])

# ... hours pass ...

# Later: compare current reconstruction to reference
params = ctx.ReconstructionParams(
    K_ticks=5,
    reference_snapshot=reference
)
current = ctx.reconstruct_context(graph, ["telegram_badge"], params)

if current.similarity_to_prior > 0.7:
    print("Good reconstruction - context matches past pattern")
else:
    print("Weak reconstruction - significant drift")
```

### Pattern 3: Multi-Entity Context Switching

```python
# Reconstruct to understand which project is active
snapshot = ctx.reconstruct_context(graph, ["notification", "email"])

# Find dominant entity
dominant_entity = max(
    snapshot.entity_energies.items(),
    key=lambda x: x[1]
)[0]

print(f"Dominant context: {dominant_entity}")
# Output: "work" or "personal" or "alice_conversation"
```

---

## Performance Considerations

### Snapshot Ephemerality

**Snapshots are NOT persisted:**
- Created on-demand for measurement
- Held in memory during reconstruction
- Cleared after use or comparison
- Never written to FalkorDB

**Why ephemeral?**
- Avoids state duplication (graph is the state)
- Prevents snapshot staleness (always fresh)
- Lighter than snapshot storage
- Graph itself provides history via bitemporal tracking

### Computational Cost

**Entity aggregation:**
- O(N) where N = number of nodes
- Fast: just sum node energies per entity

**Similarity computation:**
- Entity energy cosine: O(E) where E = number of entities
- Active member Jaccard: O(M) where M = total active members
- Combined: O(E + M)

**Typical performance:**
- Graph with 1000 nodes, 50 entities
- Entity aggregation: <1ms
- Similarity: <5ms
- Total snapshot creation: <10ms

### Reconstruction Budget

**K ticks × tick duration = reconstruction time:**
- K=5 ticks × 100ms/tick = 500ms reconstruction
- K=10 ticks × 100ms/tick = 1000ms reconstruction

**Trade-off:**
- Fewer ticks = faster but potentially incomplete reconstruction
- More ticks = slower but more complete pattern emergence

**Adaptive strategy (future):**
```python
# High urgency: quick reconstruction
if urgency > 0.8:
    K_ticks = 3  # 300ms

# Medium urgency: standard
elif urgency > 0.4:
    K_ticks = 5  # 500ms

# Low urgency: thorough
else:
    K_ticks = 10  # 1000ms
```

---

## Future Enhancements

### Phase 2: Bounded Traversal (Explicit Control)

Currently, reconstruction uses normal tick loop (continuous operation). Future enhancement:

```python
def bounded_traversal(
    graph: Graph,
    entry_nodes: List[Node],
    K_ticks: int,
    budget: float
) -> TraversalResult:
    """
    Explicit K-tick traversal with budget enforcement.

    Two-scale:
    1. Between-entity: Choose which entity to expand
    2. Within-entity: Run strides from chosen entity's frontier
    """
    # TODO: Implement explicit bounded traversal
```

### Phase 3: Urgency-Based Adaptation

Learn mapping from stimulus urgency → reconstruction parameters:

```python
class UrgencyModel:
    """Learn urgency → (K_ticks, budget) mapping."""

    def predict_ticks(self, urgency: float) -> int:
        """Predict optimal K_ticks for urgency level."""
        # Regression model trained on (urgency, quality, cost)
        return int(3 + urgency * 7)  # 3-10 ticks

    def predict_budget(self, urgency: float) -> float:
        """Predict optimal budget for urgency level."""
        return 5.0 + urgency * 15.0  # 5-20 budget
```

### Phase 4: Reconstruction Events Integration

Add to consciousness_engine_v2.py:

```python
# Emit reconstruction events
await self.broadcaster.broadcast_event("context.reconstruct.start", {...})
await self.broadcaster.broadcast_event("context.reconstruct.complete", {...})

# Track metrics
self.metrics.reconstruction_similarity.append(snapshot.similarity_to_prior)
self.metrics.reconstruction_time_ms.append(elapsed_ms)
```

### Phase 5: Reference Pattern Storage

Optional in-memory cache of reference patterns:

```python
class ReconstructionCache:
    """Ephemeral cache of reference patterns."""

    def __init__(self, max_patterns: int = 10):
        self.patterns = {}  # {pattern_id: ContextSnapshot}
        self.max_patterns = max_patterns

    def store(self, pattern_id: str, snapshot: ContextSnapshot):
        """Store reference pattern (LRU eviction)."""
        if len(self.patterns) >= self.max_patterns:
            # Evict oldest
            oldest = min(self.patterns.items(), key=lambda x: x[1].timestamp)
            del self.patterns[oldest[0]]

        self.patterns[pattern_id] = snapshot

    def get(self, pattern_id: str) -> Optional[ContextSnapshot]:
        """Retrieve reference pattern."""
        return self.patterns.get(pattern_id)
```

---

## Troubleshooting

### Problem: No entities detected

**Cause:** Nodes lack `entity_id` property or scope

**Fix:** Set entity membership explicitly:
```python
# Set entity_id on nodes
for node in graph.nodes.values():
    if "alice" in node.name.lower():
        node.properties['entity_id'] = "alice"
    elif "work" in node.name.lower():
        node.properties['entity_id'] = "work"

# Or provide explicit membership
membership = {
    "alice": [node.id for node in graph.nodes.values() if "alice" in node.name.lower()],
    "work": [node.id for node in graph.nodes.values() if "work" in node.name.lower()]
}
energies = ctx.aggregate_entity_energies(graph, membership)
```

### Problem: Low similarity scores

**Cause:** Graph state changed significantly between snapshots

**Analysis:**
```python
# Compare entity energies
print("Reference:", reference.entity_energies)
print("Current:", current.entity_energies)

# Compare active members
print("Reference active:", reference.active_members)
print("Current active:", current.active_members)
```

**Expected:** Similarity 0.6-0.8 on familiar contexts (drift is normal)

### Problem: Empty snapshot

**Cause:** No nodes active after reconstruction

**Fix:**
- Check stimulus injection worked (entry nodes have energy > 0)
- Verify K_ticks sufficient for activation spread
- Check decay rates not too aggressive
- Ensure thresholds not too high

---

## Summary

Context reconstruction provides:

✓ **Emergent pattern reconstruction** from stimulus (no stored snapshots)
✓ **Entity-scale summarization** (which projects/conversations are active)
✓ **Pattern similarity measurement** (how well did we reconstruct?)
✓ **Working memory selection** (top-N nodes by energy)
✓ **Boundary link identification** (connections between contexts)
✓ **15 comprehensive tests** - all passing

**Key principle:** The graph IS the memory. Reconstruction is measurement, not mutation.

**Integration:** Works with existing stimulus_injection.py + consciousness_engine_v2.tick()

**Testing:** `python orchestration/mechanisms/test_context_reconstruction.py`

**Documentation:** This file + `docs/specs/v2/foundations/context_reconstruction.md`
