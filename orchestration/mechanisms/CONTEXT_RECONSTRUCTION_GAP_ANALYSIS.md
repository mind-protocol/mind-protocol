# Context Reconstruction: Gap Analysis (V2)

**Spec:** `docs/specs/v2/foundations/context_reconstruction.md`
**Current:** `orchestration/mechanisms/stimulus_injection.py`, `orchestration/mechanisms/sub_entity_traversal.py`, `orchestration/mechanisms/consciousness_engine_v2.py`
**Date:** 2025-10-22

## Executive Summary

Context reconstruction infrastructure **partially exists** across multiple modules but lacks:
1. Unified context reconstruction module/API
2. Bounded traversal for K ticks
3. Entity energy aggregation and summarization
4. Pattern similarity computation
5. Context reconstruction observability events

## What Exists (Keep)

### ✅ Stimulus Injection (`stimulus_injection.py`)
- **Purpose:** Inject activation energy from external stimuli
- **Capabilities:**
  - Entropy-coverage search for match identification
  - Gap-based budget calculation
  - Direction-aware distribution
  - Health modulation via criticality
  - Source impact learning
  - Peripheral amplification

**Compliance:** Implements step 1 (identify entry nodes) + step 2 (inject activation)

### ✅ Sub-Entity Traversal (`sub_entity_traversal.py`)
- **Purpose:** Goal-driven graph traversal
- **Capabilities:**
  - Multiple goal types (find_answer, explore_completely, seek_security, etc.)
  - Cost computation with emotional coloring
  - Complementarity/resonance multipliers
  - Budget-constrained traversal
  - Visited node tracking

**Compliance:** Implements step 3 (two-scale traversal) partially

### ✅ Tick Loop (`consciousness_engine_v2.py`)
- **Purpose:** Orchestrate mechanisms in 4-phase cycle
- **Current Phases:**
  1. Activation (stimulus injection)
  2. Redistribution (diffusion + decay)
  3. Workspace (WM selection)
  4. Learning (strengthening + weight learning)

**Compliance:** Infrastructure exists but context reconstruction not explicitly orchestrated

## What's Missing from V2 Spec

### ❌ MISSING: Unified Context Reconstruction Module

**Spec requirement:**
> "A context is an emergent activation pattern over nodes, summarized at the entity scale. Reconstruction = stimulus injection + budgeted, weighted traversal."

**Gap:**
- No `context_reconstruction.py` module
- No API like `reconstruct_context(stimulus, K_ticks, budget)`
- Context reconstruction scattered across multiple files
- No clear entry point for "resume old thread"

**Impact:** Cannot easily trigger context reconstruction as atomic operation

**Fix:** Create `context_reconstruction.py` with:
```python
def reconstruct_context(
    graph: Graph,
    stimulus: Stimulus,
    K_ticks: int,
    budget: float
) -> ContextSnapshot:
    """
    Reconstruct activation pattern from stimulus.

    Returns snapshot (ephemeral, not persisted).
    """
```

### ❌ MISSING: Bounded Traversal for K Ticks

**Spec requirement:**
> "Run two-scale traversal for K ticks (between-entity choices then within-entity strides)"

**Current state:**
- `sub_entity_traversal.py` has goal-driven traversal
- No explicit "run for K ticks" API
- No tick-bounded traversal loop
- Traversal integrated into main tick loop (continuous, not bounded)

**Gap:**
- Cannot say "reconstruct for exactly 5 ticks then stop"
- No termination condition based on tick count
- No separate reconstruction phase vs normal operation

**Impact:** Cannot implement reconstruction with bounded compute cost

**Fix:** Add `bounded_traversal(graph, entry_nodes, K_ticks, budget)`:
```python
def bounded_traversal(
    graph: Graph,
    entry_nodes: List[Node],
    K_ticks: int,
    budget: float
) -> TraversalResult:
    """
    Run K ticks of traversal starting from entry nodes.

    Returns activation pattern after K ticks.
    """
    for tick in range(K_ticks):
        # Between-entity choices
        # Within-entity strides (diffusion)
        # Budget tracking
    return snapshot
```

### ❌ MISSING: Entity Energy Aggregation

**Spec requirement:**
> "Summarize: entity energies (derived), active members, boundary links, WM selection"

**Current state:**
- Nodes have single energy `E`
- No entity aggregation computed
- No "entity energy = sum of member node energies" calculation
- No boundary link identification

**Gap:**
- Cannot answer "which entities are active?"
- Cannot summarize "entity A has 3.5 total energy"
- No notion of entity membership for aggregation

**Impact:** Cannot produce entity-scale summary for observability/analytics

**Fix:** Add `aggregate_entity_energies(graph, entities)`:
```python
def aggregate_entity_energies(
    graph: Graph,
    entities: Dict[EntityID, List[NodeID]]
) -> Dict[EntityID, float]:
    """
    Aggregate node energies by entity membership.

    Returns: {entity_id: total_energy}
    """
    return {
        entity_id: sum(graph.nodes[nid].E for nid in members)
        for entity_id, members in entities.items()
    }
```

### ❌ MISSING: Context Snapshot Data Structure

**Spec requirement:**
> "Snapshots are ephemeral (not persisted)"

**Gap:**
- No `ContextSnapshot` dataclass
- No structured representation of reconstruction result
- No standard fields (entity_energies, active_members, boundary_links, etc.)

**Impact:** Cannot compare contexts, cannot serialize for analytics

**Fix:** Add dataclass:
```python
@dataclass
class ContextSnapshot:
    """
    Ephemeral snapshot of reconstructed context.

    NOT persisted - used only for analytics/comparison.
    """
    timestamp: datetime
    entity_energies: Dict[EntityID, float]
    active_members: Dict[EntityID, List[NodeID]]
    boundary_links: List[LinkID]  # Links crossing entity boundaries
    wm_selection: List[NodeID]    # Working memory nodes
    total_energy: float
    reconstruction_ticks: int
    similarity_to_prior: Optional[float] = None
```

### ❌ MISSING: Pattern Similarity Computation

**Spec requirement:**
> "Optionally compute similarity to a prior observed pattern for analytics"

**Gap:**
- No `context_similarity(snapshot_a, snapshot_b)` function
- No similarity metrics (set overlap, embedding cosine, energy distribution)
- No reference pattern storage/comparison

**Impact:** Cannot measure "how well did we reconstruct the Alice context?"

**Fix:** Add similarity function:
```python
def context_similarity(
    snapshot_a: ContextSnapshot,
    snapshot_b: ContextSnapshot,
    method: str = "entity_energy_cosine"
) -> float:
    """
    Compute similarity between two context snapshots.

    Methods:
    - "entity_energy_cosine": Cosine similarity of entity energy vectors
    - "active_member_jaccard": Jaccard similarity of active node sets
    - "combined": Weighted combination

    Returns: similarity in [0, 1]
    """
```

### ❌ MISSING: Context Reconstruction Observability

**Spec requirement:**
> "Events: stimulus.inject, stride.exec, wm.emit, se.boundary.summary"
> "Metrics: reconstruction similarity, time-to-reconstruct, energy radius growth, AUC of entity energies"

**Gap:**
- No `context.reconstruct.start` / `context.reconstruct.complete` events
- No reconstruction-specific metrics
- No time-to-reconstruct tracking
- No energy radius growth measurement
- No entity energy AUC computation

**Impact:** Cannot observe reconstruction quality, cannot tune K/budget

**Fix:** Add events:
```python
# Start event
await broadcaster.broadcast_event("context.reconstruct.start", {
    "stimulus_id": stimulus.id,
    "entry_nodes": [n.id for n in entry_nodes],
    "K_ticks": K_ticks,
    "budget": budget
})

# Complete event
await broadcaster.broadcast_event("context.reconstruct.complete", {
    "stimulus_id": stimulus.id,
    "snapshot": snapshot.to_dict(),
    "similarity": similarity_score,
    "time_ms": elapsed_ms,
    "ticks_executed": K_ticks
})
```

### ❌ MISSING: Adaptive K Ticks and Budget

**Spec requirement:**
> "Adaptive ticks & budget by urgency"

**Gap:**
- K ticks is hardcoded or not implemented
- Budget is global, not urgency-adjusted
- No urgency signal extraction from stimulus
- No learned mapping from urgency→K

**Impact:** Waste compute on low-urgency or over-reconstruct high-urgency

**Fix:** Add urgency-based adaptation:
```python
def compute_reconstruction_params(
    stimulus: Stimulus,
    urgency_model: UrgencyModel
) -> Tuple[int, float]:
    """
    Compute K_ticks and budget based on stimulus urgency.

    Returns: (K_ticks, budget)
    """
    urgency = extract_urgency(stimulus)
    K_ticks = urgency_model.predict_ticks(urgency)
    budget = urgency_model.predict_budget(urgency)
    return K_ticks, budget
```

### ⚠️ PARTIAL: Two-Scale Traversal

**Spec requirement:**
> "Two-scale traversal for K ticks (between-entity choices then within-entity strides)"

**Current state:**
- `sub_entity_traversal.py` has goal-driven traversal
- Has cost computation and candidate selection
- Supports energy budgets

**Gap:**
- Not explicitly two-scale (between-entity vs within-entity)
- No clear separation of "choose entity" vs "stride within entity"
- Traversal is one-step, not K-tick loop

**Impact:** Traversal exists but not structured as spec describes

**Fix:** Refactor to explicit two-scale:
```python
def two_scale_traversal_tick(
    graph: Graph,
    active_entities: Dict[EntityID, List[Node]],
    budget: float
) -> TraversalStepResult:
    """
    Execute one tick of two-scale traversal.

    1. Between-entity: Choose which entity to expand
    2. Within-entity: Run strides from chosen entity's frontier
    """
    # Phase 1: Entity selection
    chosen_entity = select_entity_to_expand(active_entities, budget)

    # Phase 2: Within-entity strides
    stride_results = execute_strides_within_entity(
        graph, chosen_entity, budget
    )

    return TraversalStepResult(...)
```

## Implementation Plan

### Phase 1: Core Context Reconstruction Module (CRITICAL)

1. Create `context_reconstruction.py`:
   - `ContextSnapshot` dataclass
   - `reconstruct_context(stimulus, K_ticks, budget)` function
   - `bounded_traversal(entry_nodes, K_ticks, budget)` helper
   - `aggregate_entity_energies(graph, entities)` helper

2. Integration with existing mechanisms:
   - Use `stimulus_injection.py` for step 1+2 (identify + inject)
   - Use `sub_entity_traversal.py` for traversal logic
   - Return `ContextSnapshot` (ephemeral)

### Phase 2: Pattern Similarity (Analytics)

1. Add `context_similarity(snapshot_a, snapshot_b)` function
2. Implement similarity methods:
   - Entity energy cosine similarity
   - Active member Jaccard similarity
   - Combined weighted score

3. Optional: Store reference patterns for comparison
   - In-memory only (ephemeral)
   - Clear on session boundary

### Phase 3: Observability & Metrics

1. Add reconstruction events:
   - `context.reconstruct.start`
   - `context.reconstruct.complete`
   - Include snapshot data, similarity, timing

2. Track metrics:
   - Time-to-reconstruct (milliseconds)
   - Reconstruction similarity (vs reference)
   - Energy radius growth (over K ticks)
   - Entity energy AUC (area under curve)

3. Emit metrics via broadcaster

### Phase 4: Adaptive Parameters (Future)

1. Add urgency extraction from stimulus
2. Learn urgency→K mapping via regression
3. Adjust budget dynamically based on criticality state
4. Track reconstruction quality vs compute cost

### Phase 5: Two-Scale Refactoring (Future)

1. Refactor `sub_entity_traversal.py` to explicit two-scale
2. Separate entity selection from within-entity strides
3. Implement entity-first traversal order
4. Validate against spec requirements

## Minimal Viable Implementation

To satisfy spec with minimal effort:

1. **Create `context_reconstruction.py`:**
   - `ContextSnapshot` dataclass
   - `reconstruct_context()` function that:
     - Calls `stimulus_injection.inject()` for entry nodes
     - Runs K ticks of diffusion (reuse existing diffusion)
     - Aggregates entity energies
     - Returns snapshot

2. **Add `context_similarity()`:**
   - Simple entity energy cosine similarity
   - Returns float in [0, 1]

3. **Emit events:**
   - `context.reconstruct.start` / `.complete`
   - Include similarity and timing

4. **Integration in engine:**
   - Add `engine.reconstruct_context(stimulus, K=5)` method
   - Call when resuming threads
   - Emit metrics

This gives 80% of spec value with 20% of effort.

## Open Questions

1. **Entity membership:** How do we know which nodes belong to which entity?
   - Option A: Node has `entity_id` field
   - Option B: Entities defined in separate registry
   - Option C: Derive from graph structure (clusters)

2. **Boundary links:** How to identify links crossing entity boundaries?
   - Requires entity membership (see Q1)
   - Filter links where `source.entity != target.entity`

3. **WM selection:** Should context reconstruction include WM selection?
   - Spec mentions "WM selection" in summary
   - Current WM logic is in engine Phase 3
   - Should reconstruction call WM selector or just report active nodes?

4. **Persistence:** Spec says "ephemeral, not persisted" - confirm no DB writes?
   - Snapshots only for analytics
   - Clear after comparison
   - Never write to FalkorDB

5. **K ticks:** Default value? Adaptive strategy?
   - Spec suggests 100-300ms typical
   - At 100ms/tick = 1-3 ticks?
   - Or K=5-10 ticks with faster ticks during reconstruction?

## Recommendation

**Implement Phase 1 + 2 + 3 (Core + Similarity + Observability):**

1. Create `context_reconstruction.py` module
2. Add `ContextSnapshot`, `reconstruct_context()`, `context_similarity()`
3. Emit reconstruction events
4. Skip adaptive params and two-scale refactoring for now

This satisfies core spec requirements and enables testing/validation.
