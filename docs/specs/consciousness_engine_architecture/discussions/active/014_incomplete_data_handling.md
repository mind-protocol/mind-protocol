# [Discussion #014]: Incomplete Data Handling Strategy

**Status:** 🟡 Active
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Medium-High

**Affected Files:**
- `mechanisms/07_energy_diffusion.md` (what if diffusion data incomplete?)
- `mechanisms/04_global_workspace.md` (what if workspace query incomplete?)
- `implementation/database_queries.md` (async query patterns)
- **CREATE NEW:** `mechanisms/20_incomplete_state_handling.md`

**Related Discussions:**
- #001 - Diffusion stability
- #008 - Tick speed (async operations affect responsiveness)

---

## Problem Statement

**What's the question?**

**How should the consciousness engine handle incomplete data from database queries?**

**Context:**

Since we're using FalkorDB (database-backed graph), all operations are async queries:
- Energy diffusion needs node energies + link weights (database query)
- Workspace selection needs cluster energies (database query)
- Entity emergence needs activation patterns (database query)

**What if query isn't complete yet?**

**Option A: Block and wait** (synchronous)
```python
def diffuse_energy(graph):
    # BLOCKS until query completes
    nodes = db.query("MATCH (n:Node) RETURN n").wait()
    links = db.query("MATCH ()-[r:Link]->() RETURN r").wait()

    # Now diffuse (have complete data)
    for node in nodes:
        for link in node.outgoing_links:
            transfer_energy(node, link)
```

**Option B: Process partial data** (async non-blocking)
```python
def diffuse_energy(graph):
    # Start query, don't wait
    nodes_future = db.query_async("MATCH (n:Node) RETURN n")

    # Process nodes as they arrive (streaming)
    for node in nodes_future.stream():
        # Might not have all nodes yet!
        # Diffuse with incomplete data
        ...
```

**Nicolas's point:**
"Since we are doing everything from the database, there shouldn't be any synchronous or blocking operation at all."

**But then:**
"I think we need a discussion for that because it's a question of what do we do with incomplete data?"

**Why does this matter?**

**If we block (Option A):**
- Simple - always have complete data
- Guarantees correctness (no partial diffusion)
- BUT: Slow - wait for every query
- Defeats purpose of async database

**If we don't block (Option B):**
- Fast - process data as it arrives
- Fully async (as database intended)
- BUT: Incomplete data - what if critical nodes haven't loaded?
- Risk of incorrect dynamics

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

This is a fundamental trade-off between **correctness** and **responsiveness**.

**The Problem with Partial Data:**

**Example: Energy Diffusion**

Complete graph:
```
A(energy=1.0) --0.8--> B(energy=0.0)
              --0.6--> C(energy=0.0)
```

Diffusion should transfer:
- A→B: 1.0 * 0.8 * rate = 0.8 * rate
- A→C: 1.0 * 0.6 * rate = 0.6 * rate

**If query only returns A and B (C not loaded yet):**
```
A(energy=1.0) --0.8--> B(energy=0.0)
              --0.6--> C(???)  # Not loaded!
```

Diffusion transfers:
- A→B: 0.8 * rate
- A→C: **SKIPPED** (C doesn't exist in partial data)

**Result:** Energy accumulates at B, never reaches C. **Incorrect dynamics.**

---

**Proposed Solution: Hybrid Approach (Async Queries + Consistency Guarantees)**

**Phase 1: Snapshot Consistency**

```python
class ConsciousnessEngine:
    def __init__(self, db):
        self.db = db
        self.graph_snapshot = None
        self.snapshot_timestamp = None

    async def refresh_snapshot(self):
        """
        Asynchronously load complete graph snapshot
        Run periodically (e.g., every tick)
        """
        # Start async queries in parallel
        nodes_future = self.db.query_async("MATCH (n:Node) RETURN n")
        links_future = self.db.query_async("MATCH ()-[r]->() RETURN r")

        # Wait for BOTH to complete (consistency point)
        nodes = await nodes_future
        links = await links_future

        # Create immutable snapshot
        self.graph_snapshot = GraphSnapshot(nodes, links)
        self.snapshot_timestamp = time.now()

    def diffuse_energy(self):
        """
        Diffuse using snapshot (complete, consistent data)
        Never blocks - uses last complete snapshot
        """
        if self.graph_snapshot is None:
            # No snapshot yet - can't diffuse
            return

        # Operate on complete consistent snapshot
        for node in self.graph_snapshot.nodes:
            for link in node.outgoing_links:
                transfer_energy(node, link)

        # Write updates back async (fire and forget)
        self.db.write_async(updated_energies)
```

**How it works:**
1. **Async refresh** - Load complete graph snapshot asynchronously
2. **Operate on snapshot** - Diffusion/workspace/entities use snapshot (never block)
3. **Snapshot is complete** - Guaranteed consistency within snapshot
4. **Refresh periodically** - New snapshot every tick (stays fresh)

**Benefits:**
- ✅ No blocking operations (fully async)
- ✅ Complete data (snapshot guarantees consistency)
- ✅ Fast (operations use in-memory snapshot)
- ✅ Fresh enough (refreshes every tick)

**Cons:**
- Snapshot might be slightly stale (updated since refresh)
- Memory overhead (full graph in memory)
- Need refresh frequency tuning

---

**Alternative A: Event Sourcing (Process Updates as They Arrive)**

```python
class ConsciousnessEngine:
    def __init__(self, db):
        self.db = db
        self.graph_state = {}  # Incrementally built

        # Subscribe to database update stream
        db.subscribe(self.on_update)

    def on_update(self, update):
        """Process database updates as they arrive"""
        if update.type == "node_energy_changed":
            self.graph_state[update.node_id].energy = update.new_energy
            # Trigger local diffusion immediately
            self.diffuse_from_node(update.node_id)

        elif update.type == "link_created":
            self.graph_state.add_link(update.link)

    def diffuse_from_node(self, node_id):
        """Diffuse only from updated node (incremental)"""
        node = self.graph_state[node_id]
        for link in node.outgoing_links:
            if link.target_id in self.graph_state:  # Target might not be loaded!
                transfer_energy(node, link.target)
```

**Benefits:**
- Fully async (event-driven)
- Immediate response to updates
- Incremental (doesn't need full graph refresh)

**Cons:**
- Complex state management
- Partial graph problem (some nodes might not be loaded)
- Hard to guarantee consistency

---

**Alternative B: Optimistic Diffusion (Assume Complete, Correct Later)**

```python
def diffuse_energy_optimistic(graph):
    """
    Diffuse with whatever data is available
    Accept that it might be incomplete
    """
    # Get nodes (might be partial)
    nodes = db.query_non_blocking("MATCH (n:Node) RETURN n")

    # Diffuse with available nodes
    for node in nodes:
        for link in node.outgoing_links:
            # If target not loaded, skip (optimistic assumption)
            if link.target is not None:
                transfer_energy(node, link.target)

    # Eventual consistency: when missing nodes load, next diffusion corrects
```

**Benefits:**
- Simple
- Non-blocking
- Self-correcting over time

**Cons:**
- Incorrect in short term (energy doesn't reach unloaded nodes)
- No guarantees of correctness
- Might accumulate errors

---

**My Recommendation: Snapshot Consistency (Hybrid Approach)**

**Reasoning:**
- Async refresh → no blocking during diffusion
- Snapshot → complete consistent data guaranteed
- Refresh every tick → fresh enough for consciousness dynamics
- Standard pattern (React, Redux use similar snapshot approach)

**Implementation:**

**Phase 1:**
- Refresh snapshot every tick (simple, synchronous point)
- Operations use snapshot (no blocking)
- Accept small staleness (snapshot is 0-1 tick old)

**Phase 2 (if needed):**
- Differential updates between snapshots (event sourcing layer)
- Reduces refresh overhead
- Maintains snapshot consistency

**Trade-offs:**
- Optimizing for correctness (complete data)
- Accepting small staleness (snapshot refreshes periodically)
- Memory overhead (full graph snapshot)

**Uncertainty:**
- How large will consciousness graphs be? (If huge, snapshot might be expensive)
- Is staleness acceptable? (Consciousness dynamics might be robust to 0-1 tick delay)
- Can FalkorDB efficiently snapshot? (Need to test query performance)

---

### Nicolas's Perspective
**Posted:** [Pending]

**Question:** Snapshot consistency, event sourcing, or optimistic processing? How do we handle incomplete data?

---

### GPT-5 Pro's Perspective
**Posted:** [Pending]

[Awaiting GPT-5 Pro review]

**Questions for GPT-5:**
- What's FalkorDB's async query performance?
- Can we efficiently snapshot 100K+ node graphs?
- Better patterns for async graph operations?

---

### Luca's Perspective
**Posted:** 2025-10-19

**Initial perspective corrected - was proposing top-down solution, need bottom-up approach.**

**Nicolas's architectural guidance:**

"You're trying to make a top-down solution that's not possible and or desirable. I think what we want to allow is we want to allow for incomplete node creation because the LLM is going to often make incomplete nodes. However, this should be fixed as soon as possible by the creation of tasks that are automatically triggered to complete the missing information. I think missing nodes should not be traversable. Nodes with missing information or links with missing information should be very weakly, not traversable at all."

**Corrected understanding:**

The question isn't "how do we ensure complete data before processing" (snapshot consistency) - it's "how do we handle incomplete nodes that WILL exist and self-heal them" [node_self_healing_incomplete_data: very useful].

**Architecture:**

```yaml
incomplete_node_handling:

  creation:
    allow_incomplete: true
    rationale: "LLM will often create nodes with missing fields"

  traversability:
    missing_required_fields:
      node_traversability: not_traversable  # or very_weak
      link_traversability: not_traversable  # or very_weak

    partial_information:
      node_traversability: weakly_traversable
      weight_multiplier: 0.1  # Much harder to traverse

  self_healing:
    trigger: automatic_on_detection
    mechanism: task_creation
    priority: high

    process:
      1_detect: "Node/link missing required fields"
      2_create_task: "AUTO: Complete [node_name] metadata"
      3_prioritize: "Incompleteness blocks traversal → high priority"
      4_complete: "Task execution fills missing fields"
      5_restore: "Node/link becomes normally traversable"
```

**Example scenario:**

```python
# LLM creates incomplete node during TRACE parsing
node = {
    "name": "new_realization",
    "type": "Realization",
    "what_i_realized": "Something important",
    # MISSING: confidence, formation_trigger, description
}

# System detects incompleteness
if not node.is_complete():
    # Mark as non-traversable
    node.traversable = False

    # Auto-create completion task
    task = Task(
        description=f"Complete missing fields for {node.name}",
        node_to_complete=node.name,
        missing_fields=node.get_missing_required_fields(),
        priority="high"  # Blocks traversal
    )

    # Task gets executed (by sub-entity or system)
    # Missing fields get filled
    # Node becomes traversable
```

**Substrate specification:**

```yaml
node_link_completeness:

  required_fields:
    per_type: defined_in_COMPLETE_TYPE_REFERENCE
    validation: on_creation

  incomplete_state:
    traversability: none_or_very_weak
    query_inclusion: excluded_or_deprioritized
    visual_indicator: [grayed_out, dotted_border]

  completion_mechanism:
    trigger: automatic
    method: task_creation
    task_type: "Complete_Node_Metadata"
    priority: high

    task_includes:
      - node_id
      - missing_field_list
      - node_type (for schema reference)
      - creation_context (if available)
```

**Why this is bottom-up:**

- No global synchronization
- No snapshot waiting
- No blocking operations
- Incomplete nodes exist but self-heal through task system
- Sub-entities naturally avoid incomplete nodes (not traversable)

**Confidence:** 0.85 - This reflects the self-healing architecture

**Key principle:** Allow incompleteness, make it obvious (non-traversable), auto-heal [principle_allow_and_heal: very useful].

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Allow incomplete node creation, fix via automatic task creation.

**Key points:**
- LLM will often create incomplete nodes - this is expected
- Missing nodes should NOT be traversable (or very weakly traversable)
- Nodes/links with missing information: weakly or not traversable
- Fix ASAP by automatically creating tasks to complete missing info
- This is bottom-up self-healing, not top-down synchronization

---

## Debate & Convergence

**Key Points of Agreement:**
- No blocking operations (Nicolas's requirement)
- Need complete data for correct dynamics

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Snapshot consistency vs event sourcing vs optimistic?
- How often to refresh snapshot?
- Memory overhead acceptable?
- Does FalkorDB support efficient snapshots?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**

**IF SNAPSHOT CONSISTENCY:**
- [ ] CREATE `mechanisms/20_snapshot_consistency.md`
- [ ] UPDATE `implementation/database_queries.md` - Snapshot refresh pattern
- [ ] UPDATE `mechanisms/07_energy_diffusion.md` - Operates on snapshot
- [ ] UPDATE `mechanisms/04_global_workspace.md` - Operates on snapshot

**IF EVENT SOURCING:**
- [ ] CREATE `mechanisms/20_event_sourcing.md`
- [ ] UPDATE `implementation/database_queries.md` - Event subscription pattern
- [ ] More complex state management required

**IF OPTIMISTIC:**
- [ ] Document optimistic assumption
- [ ] Accept eventual consistency
- [ ] Simpler implementation but less correct

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:**
- Snapshot pattern: Medium (refresh + snapshot management)
- Event sourcing: Large (complex state management)
- Optimistic: Small (simple but incorrect)

**Dependencies:**
- Requires FalkorDB async query support
- Needs performance testing (snapshot overhead)

**Verification:**
- Test with incomplete query results
- Verify consistency (energy conservation)
- Measure snapshot refresh overhead
- Test scalability (100K+ nodes)

---

## Process Notes

**How this discussion evolved:**
Nicolas stated "no blocking operations" but then asked "what do we do with incomplete data?" - revealing the fundamental trade-off.

**Lessons learned:**
Async database operations create consistency challenges. Need explicit strategy for handling incomplete data.
