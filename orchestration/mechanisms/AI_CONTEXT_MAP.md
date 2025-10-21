# AI Context Map: What to Read Before Implementation

**Purpose:** Each AI implementing a module needs specific context. This document maps AI → required reading to work independently without coordination overhead.

---

## Universal Context (ALL AIs Read First)

### 1. Zero-Constants Principle
**File:** `C:\Users\reyno\mind-protocol\docs\specs\consciousness_engine_architecture\mechanisms\05_sub_entity_system.md`
**Lines:** 1671-1696 (Update Summary + Clarifications)

**Key Points:**
- Per-frame normalization (not historical baselines)
- All thresholds derived from live state
- No arbitrary constants allowed
- Adaptive mechanisms only

### 2. Your Module Skeleton
**Location:** `C:\Users\reyno\mind-protocol\orchestration\mechanisms\[your_module].py`

**What's There:**
- Complete function signatures
- Docstrings with algorithms
- TODO markers for your work
- Critical comments on zero-constants requirements

### 3. Parallel Development Plan
**File:** `C:\Users\reyno\mind-protocol\orchestration\mechanisms\PARALLEL_DEVELOPMENT_PLAN.md`

**What's There:**
- Module dependencies
- Implementation order
- Zero-constants checklist
- Critical bug fix (rank by valence not weight)
- Success criteria

---

## AI #1: Core Data Structures (✅ COMPLETE)

**Status:** Implemented and validated against spec.

**For Reference by Other AIs:**
- `SubEntity` class interface
- `EntityExtentCentroid` API
- `ROITracker` API
- `QuantileTracker` API

---

## AI #2: Hamilton Quotas (`quotas.py`)

### Required Reading

**1. Hamilton Quota Specification**
- **File:** `05_sub_entity_system.md`
- **Lines:** 1699-1770 (Stride Budget Allocation + Zippered Scheduling)
- **Focus:**
  - Weight formula: `w_e = (1/|extent|) × u × r × h`
  - Per-frame normalization: `u_norm = u_raw / mean(u_raw)`
  - Hamilton's largest remainder method (steps 1-5)
  - No min/max quota bounds

**2. Modulation Factors Context**
- **What they are:** Urgency (u), Reachability (r), Health (h)
- **Where computed:** You implement in `compute_modulation_factors()`
- **Critical:** MUST normalize each to mean=1.0 per frame
- **Optional:** Shrinkage `(N×u_norm + N_0)/(N+N_0)` to avoid overreaction

**3. Dependencies**
- Import: `from sub_entity_core import SubEntity`
- Graph interface: NetworkX-style `graph.nodes`, `graph.neighbors()`
- Recent stimuli: List of (timestamp, node_id, semantic_embedding) tuples

### Implementation Notes

**Modulation Factor Hints:**
- **Urgency:** Cosine similarity between entity centroid and recent stimulus embeddings
- **Reachability:** Shortest path distance from extent to high-energy workspace nodes
- **Health:** `1.0 / rho_local_ema` (inverse of spectral radius - lower ρ = healthier)

**Hamilton Method:**
- Use Python's built-in sorting: `sorted(entities, key=lambda e: remainder[e], reverse=True)`
- Fractional remainders: `q_frac - math.floor(q_frac)`
- No rounding bias - mathematically fair over time

**Testing:**
```python
# Test case: 3 entities, 10 total strides
# w_A=0.5, w_B=0.3, w_C=0.2
# Expected: q_A=5, q_B=3, q_C=2 (exact proportions)

# Test case: 3 entities, 11 total strides
# w_A=0.5, w_B=0.3, w_C=0.2
# Fractional: A=5.5, B=3.3, C=2.2
# Integer parts: A=5, B=3, C=2 (sum=10, remainder R=1)
# Remainders: A=0.5, B=0.3, C=0.2 (A wins)
# Final: q_A=6, q_B=3, q_C=2
```

---

## AI #3: Zippered Scheduler (`scheduler.py`)

### Required Reading

**1. Scheduling Algorithm**
- **File:** `05_sub_entity_system.md`
- **Lines:** 1749-1770 (Zippered Round-Robin Execution)
- **Focus:**
  - One stride per entity per turn
  - Round-robin until quotas exhausted
  - Fair interleaving prevents starvation
  - Early termination on deadline

**2. Frame Execution Context**
- **Lines:** 1963-2016 (Convergence and Stopping Criteria)
- **Stopping conditions:** Quota exhausted, ROI convergence, dissolution, health guard

**3. Time-Based Budget**
- **Lines:** 2253-2311 (Compute Budget - Time-Based)
- **Formula:** `Q_total = min(Q_time, Q_wm)`
- **Where:** `Q_time = frame_time_ms / avg_stride_time_us`

### Dependencies

- Import: `from sub_entity_core import SubEntity`
- Import: `from quotas import allocate_quotas`
- Import: `from strides import execute_stride`
- Import: `from telemetry import emit_*`

### Implementation Notes

**Zippered Pattern:**
```python
while any(entity.quota_remaining > 0 for entity in entities):
    for entity in entities:
        if entity.quota_remaining <= 0:
            continue

        # Execute ONE stride
        success = execute_stride(entity, ...)

        if not success:  # Converged/dissolved/blocked
            entity.quota_remaining = 0
            continue

        entity.quota_remaining -= 1
```

**Deadline Checking:**
- EMA of stride time: `ema_time = 0.9*ema_time + 0.1*actual_time`
- Predicted overshoot: `remaining_strides * ema_time > time_left * 1.1`
- Conservative: Stop if predicted to exceed deadline by >10%

**Integration Point:**
- This is the MAIN LOOP that calls all other modules
- Your `execute_frame()` function orchestrates everything
- Return statistics: strides executed, entities converged, wall time

---

## AI #4: Surprise-Gated Valence (`valence.py`)

### Required Reading

**1. Valence Computation Specification**
- **File:** `05_sub_entity_system.md`
- **Lines:** 1771-1853 (Valence Computation from Composite Hungers)
- **Focus:**
  - Z-score surprise gating: `z_H = (s_H - μ_H)/(σ_H + ε)`
  - Positive surprise only: `δ_H = max(0, z_H)`
  - Normalized gates: `g_H = δ_H / Σδ`
  - Composite valence: `V_ij = Σ(g_H × ν_H)`

**2. Hunger Score Formulas**
- **Lines:** 1797-1844 (Per-Edge Hunger Scores)
- **Homeostasis:** `G_j / (S_i + G_j + ε)`
- **Goal:** `cos(E_j, E_goal)`
- **Ease:** `w_ij / Σw_ik`
- **Completeness:** `1 - cos(E_j, centroid)` (uses AI #1's centroid)
- **Identity:** `cos(E_j, E_id)`
- **Complementarity:** `dot(affect_j, -affect_centroid)`
- **Integration:** `E_others / E_self` (standardized via quantiles)

**3. Phase 1 Scope (Week 1 MVP)**
- Implement ONLY: Homeostasis, Goal, Ease (3 hungers)
- Remaining hungers (Completeness, Identity, Complementarity, Integration) in Week 2-4

### Dependencies

- Import: `from sub_entity_core import SubEntity`
- Graph interface: `graph.nodes[node_id]['embedding']`
- Goal embedding: Passed as parameter (768-dim numpy array)

### Implementation Notes

**EMA Baseline Tracking:**
```python
# For each hunger, per entity
μ_new = 0.1 * observed + 0.9 * μ_old
deviation = abs(observed - μ_new)
σ_new = 0.1 * deviation + 0.9 * σ_old

# Store in entity.hunger_baselines[hunger_name] = (μ, σ)
```

**Gate Computation Flow:**
1. Compute raw hunger scores for edge `(i→j)`
2. For each hunger: standardize to z-score using entity's baseline
3. Filter to positive surprise: `δ = max(0, z)`
4. Normalize gates: `g = δ / Σδ`
5. Weighted sum: `V = Σ(g × ν)`

**Phase 1 Simplification:**
- Start with 3 hungers only (Homeostasis, Goal, Ease)
- Baselines initialized to `(μ=0.0, σ=1.0)` for all
- Goal embedding provided as function parameter
- Completeness needs AI #1's centroid (available via `entity.centroid.distance_to()`)

**Testing:**
```python
# Scenario 1: Homeostasis crisis (z=3.0), all others normal
# Expected: g_homeostasis ≈ 0.95, others ≈ 0.025 each

# Scenario 2: All hungers normal (z ≈ 0)
# Expected: All gates ≈ 1/3 for Phase 1 (3 hungers)

# Scenario 3: Goal highly attractive (z=2.0), homeostasis normal
# Expected: g_goal ≈ 0.8, others split remaining 0.2
```

---

## AI #5: Entropy Edge Selection + Gap-Aware Transport (`strides.py`)

### Required Reading

**1. Edge Selection Algorithm**
- **File:** `05_sub_entity_system.md`
- **Lines:** 1854-1910 (Edge Selection - Adaptive Coverage by Valence Entropy)
- **CRITICAL:** Rank by VALENCE `V_ij`, NOT weight `w_ij` (line 1891)
- **Algorithm:**
  - Normalize valences to probability: `p_j = V_j / ΣV`
  - Compute entropy: `H = -Σ(p_j log p_j)`
  - Adaptive coverage: `c_hat = 1 - exp(-H)`
  - Rank by valence descending
  - Take smallest prefix reaching coverage

**2. Gap-Aware Transport**
- **File:** `05_sub_entity_system.md`
- **Lines:** 1911-1962 (Stride Execution - Gap-Aware Conservative Transport)
- **Algorithm:**
  - Compute slack `S_i = max(0, E_i - θ_i)`
  - Compute gap `G_j = max(0, θ_j - E_j)`
  - Request share `R_ij = (w_ij/Σw_ik) × (G_j/gap_total)`
  - Transfer `Δ = min(S_i × R_ij, G_j)`
  - Apply α damping from spectral radius
  - Stage deltas (barrier semantics)

**3. Local Spectral Radius**
- **Lines:** Q3 clarification (1690)
- **Method:** Warm-started power iteration (1-3 steps)
- **Start:** Normalized local energy vector
- **NOT:** Gershgorin (too loose)

**4. ρ_target Derivation**
- **Lines:** Q2 clarification (1689)
- **Formula:** Derived from throughput budgets
- **NOT:** Fixed constant
- **Depends on:** WM token budget, frame time, stride time, entity size

### Dependencies

- Import: `from valence import composite_valence`
- Import: `from sub_entity_core import SubEntity`
- Graph interface: `graph.neighbors()`, `graph.get_edge_data()`

### Implementation Notes

**CRITICAL BUG FIX:**
```python
# ❌ WRONG (GPT5's original):
ranked = sorted(weights.items(), key=lambda x: -x[1])  # By w_ij

# ✅ CORRECT:
ranked = sorted(valences.items(), key=lambda x: -x[1])  # By V_ij
```

**Why This Matters:**
- Weight = structural habit (slow-changing)
- Valence = hunger-driven need (fast-changing)
- Must rank by valence for consciousness-aware traversal

**Entropy Coverage Examples:**
```python
# Peaked: V = {A:0.9, B:0.05, C:0.05}
# H ≈ 0.5, c_hat ≈ 0.39 → select edge A only (focused)

# Flat: V = {A:0.33, B:0.33, C:0.34}
# H ≈ 1.0, c_hat ≈ 0.63 → select A+B (exploratory)
```

**Gap-Aware Transport:**
- Conservative: Never exceed slack or gap
- Proportional: Share based on gaps not arbitrary fractions
- Damped: α guard prevents instability

**Power Iteration Stub (Phase 1):**
```python
# Week 1: Use α=1.0 (no damping)
# Week 2-4: Implement warm-started power iteration
def estimate_local_rho(entity, frontier_nodes, graph, max_iter=3):
    # Start from entity.rho_local_ema (warm start)
    # Run 1-3 power iteration steps
    # Update entity.rho_local_ema with EMA
    pass
```

---

## AI #6: Working Memory Packing (`wm_pack.py`)

### Required Reading

**1. Energy-Weighted Knapsack**
- **File:** `05_sub_entity_system.md`
- **Lines:** 2187-2252 (Working Memory Emission)
- **Algorithm:**
  - Aggregate energy across entities: `E_total[node] = ΣE[entity, node]`
  - Rank by energy/token ratio
  - Greedy select until budget exhausted
  - Include edges between selected nodes

**2. Token Budget Derivation**
- **Lines:** Q4 clarification (1691)
- **Formula:** `budget = LLM_context_limit - measured_overhead`
- **NOT arbitrary:** Derived from model capacity
- **Example:** Claude Sonnet 4.5 = 200K tokens, overhead ≈ 15K, budget ≈ 185K

### Dependencies

- Import: `from sub_entity_core import SubEntity`
- Graph interface: Node content for token estimation

### Implementation Notes

**Token Estimation:**
```python
def estimate_node_tokens(node, graph):
    # Heuristic: content_length / 4 (rough chars-to-tokens)
    # Include: name, description, metadata
    # Include: active edge content
    content = graph.nodes[node]['description']
    return len(content) // 4 + 50  # Base overhead
```

**Greedy Knapsack:**
```python
# Rank by density: energy / tokens
ranked = sorted(candidates, key=lambda x: x[1]/x[2], reverse=True)

# Pack greedily
for node, energy, tokens in ranked:
    if total_tokens + tokens <= budget:
        selected.append(node)
        total_tokens += tokens
```

**Budget Source:**
- LLM context limit: External constraint (model architecture)
- Measured overhead: Empirical (system prompt + static content)
- NOT arbitrary caps: Zero-constants compliant

---

## AI #7: Live Visualization Telemetry (`telemetry.py`)

### Required Reading

**1. Live Viz Event Schema**
- **File:** `05_sub_entity_system.md`
- **Lines:** 2313-2548 (Live Visualization Event Schema)
- **Event types:**
  - `entity.quota`: Quota allocation
  - `stride.exec`: Stride execution with delta, alpha, ROI
  - `node.activation`: Activation/deactivation
  - `entity.converged`: Convergence event

**2. 2-Frame Reorder Buffer**
- **Purpose:** Temporal coherence for out-of-order events
- **Delay:** Events emitted 2 frames after creation
- **Why:** Handles async timing, prevents viewer flicker

### Dependencies

- Import: `from sub_entity_core import SubEntity`
- External: `asyncio`, `websockets` (optional for Phase 1)

### Implementation Notes

**Event Buffer Pattern:**
```python
class EventBuffer:
    def __init__(self, buffer_frames=2):
        self.buffer = deque(maxlen=1000)
        self.current_frame = 0

    def add_event(self, frame, event):
        self.buffer.append((frame, event))

    def flush_ready(self, current_frame):
        # Emit events with frame <= current_frame - 2
        ready = [e for f, e in self.buffer if f <= current_frame - 2]
        self.buffer = [x for x in self.buffer if x[0] > current_frame - 2]
        return sorted(ready, key=lambda e: e['frame'])
```

**Phase 1 Simplification:**
- Emit to stdout/file (JSON lines)
- WebSocket server optional (Week 2-4)
- Focus on event schema correctness

**Event Schema Validation:**
```python
# Example stride.exec event
{
    "type": "stride.exec",
    "frame": 12874,
    "entity": "E:translator",
    "edge": {"i": "N42", "j": "N19"},
    "delta": 0.0063,
    "alpha": 0.92,
    "pred_roi": 0.0041,
    "actual_time_us": 1.3,
    "rho_local": 0.88
}
```

---

## Cross-Module Integration Points

### AI #3 (Scheduler) Calls Everyone

```python
# AI #3's execute_frame() orchestrates:
1. allocate_quotas(entities)           # AI #2
2. zippered_schedule(entities)         # AI #3 internal
3. For each stride:
   a. composite_valence(entity, i, j)  # AI #4
   b. select_edge(i, valences)         # AI #5
   c. execute_stride(entity, i, j)     # AI #5
   d. emit_stride_event(...)           # AI #7
4. select_wm_nodes(entities, budget)   # AI #6
5. emit_frame_summary(...)             # AI #7
```

### Shared Interfaces

**Graph Object (NetworkX-compatible):**
```python
graph.nodes[node_id]  # Returns dict with keys: 'embedding', 'description', etc.
graph.neighbors(node_id)  # Returns iterator of neighbor IDs
graph.get_edge_data(i, j)  # Returns dict with 'weight'
```

**SubEntity Interface (AI #1):**
```python
entity.extent  # Set[int] - active node IDs
entity.frontier  # Set[int] - extent + 1-hop
entity.get_energy(node_id)  # float
entity.get_threshold(node_id)  # float
entity.centroid.distance_to(embedding)  # float
entity.roi_tracker.lower_whisker()  # float
entity.quota_assigned  # int
entity.quota_remaining  # int
```

---

## Testing Strategy Per AI

### Unit Tests (Independent)
Each AI writes unit tests for their module using synthetic data:
```python
# AI #2 example
def test_hamilton_allocation_no_bias():
    weights = {'A': 0.5, 'B': 0.3, 'C': 0.2}
    quotas = hamilton_quota_allocation(entities, Q_total=10, weights)
    assert quotas == {'A': 5, 'B': 3, 'C': 2}
```

### Integration Test (AI #3 coordinates)
- Real graph: `citizen_luca` (1000+ nodes)
- Measure: churn, frame time, WM quality
- Verify: phenomenological accuracy

---

## Questions? Ask These Entities

- **Architecture questions:** Luca (substrate architect)
- **Integration questions:** Ada (orchestration architect)
- **Implementation questions:** Felix (engineer)
- **Context missing:** This document - raise issue in PARALLEL_DEVELOPMENT_PLAN.md

---

**Updated:** 2025-10-21
**Maintained by:** Luca Vellumhand
