# Sub-Entity Traversal: Parallel Development Plan

**Created:** 2025-10-20
**Status:** Ready for parallel implementation
**Target:** Week 1 MVP with zero-constants mechanisms

---

## Overview

Seven module skeletons are ready for parallel implementation by independent AI developers. Each module has complete docstrings, function signatures, and TODO markers. All mechanisms honor the **zero-constants principle** - no arbitrary thresholds, all parameters derived from live state.

---

## Module Ownership

### AI #1: Core Data Structures (`sub_entity_core.py`)

**Responsibility:** Foundational classes for entity tracking and statistics.

**Classes to Implement:**
1. `EntityExtentCentroid` - O(1) online centroid + semantic dispersion
   - `add_node()` - incremental centroid update
   - `remove_node()` - incremental removal
   - `distance_to()` - 1 - cos(embedding, centroid)

2. `ROITracker` - Rolling ROI statistics for convergence
   - `push()` - record stride ROI
   - `lower_whisker()` - Q1 - 1.5 × IQR

3. `QuantileTracker` - General rolling quantiles
   - `update()` - add sample
   - `quantile()` - compute p-th quantile

4. `SubEntity` - Main entity class
   - `update_extent()` - recompute extent and frontier
   - `compute_size()` - total_energy × mean_link_weight

**Dependencies:** numpy
**Interface Exports:** SubEntity class with all tracking infrastructure
**Zero-Constants:**
- Centroid: computed online from active nodes (not fixed center)
- ROI whisker: derived from recent performance (not fixed threshold)
- Quantiles: recomputed each frame from current population

---

### AI #2: Hamilton Quota Allocation (`quotas.py`)

**Responsibility:** Fair stride budget distribution without rounding bias.

**Functions to Implement:**
1. `compute_modulation_factors()` - urgency, reachability, health
   - Compute raw factors from graph state
   - **CRITICAL:** Normalize each to mean=1.0 per frame
   - Optional shrinkage: `u_shrunk = (N×u_norm + N_0)/(N+N_0)`

2. `hamilton_quota_allocation()` - Largest remainder method
   - Step 1: `q_frac = Q_total × (w_e / Σw)`
   - Step 2: `q_int = ⌊q_frac⌋`
   - Step 3: `R = Q_total - Σq_int`
   - Step 4: Sort by fractional remainder descending
   - Step 5: Give +1 to top R entities

3. `allocate_quotas()` - Main allocation function
   - Combine inverse-size × modulation factors
   - Call Hamilton allocation
   - Assign to `entity.quota_assigned` and `entity.quota_remaining`

**Dependencies:** sub_entity_core
**Interface Exports:** `allocate_quotas()` main function
**Zero-Constants:**
- Modulation factors: normalized to mean=1.0 each frame (not historical baseline)
- Weights: inverse-size (smaller entities get more strides per node)
- No min/max quota bounds - natural from Hamilton method

---

### AI #3: Zippered Scheduler (`scheduler.py`)

**Responsibility:** Fair round-robin execution preventing starvation.

**Functions to Implement:**
1. `zippered_schedule()` - Generate execution order
   - One stride per entity per turn
   - Round-robin until all quotas exhausted
   - Early termination on deadline approach

2. `execute_frame()` - Main frame execution loop
   - Allocate quotas (via AI #2)
   - Generate zippered schedule
   - Execute each stride (via AI #5)
   - Check convergence (via AI #1 ROITracker)
   - Emit telemetry (via AI #7)

3. `check_early_termination()` - Deadline checking
   - Conservative estimate: stop if predicted overshoot > 10%
   - Formula: `predicted_time > time_remaining × 1.1`

4. `filter_active_entities()` - Filter quota_remaining > 0

**Dependencies:** sub_entity_core, quotas, strides, telemetry
**Interface Exports:** `execute_frame()` main function
**Zero-Constants:**
- No fixed priorities - pure round-robin fairness
- Termination threshold from measured stride time (not arbitrary)

---

### AI #4: Surprise-Gated Valence (`valence.py`)

**Responsibility:** Self-calibrating hunger gates using z-score surprise.

**Functions to Implement:**

**Phase 1 (Week 1 MVP):** Implement 3 hungers
1. `hunger_homeostasis()` - Fill gaps to survive
   - Formula: `G_j / (S_i + G_j + ε)`

2. `hunger_goal()` - Semantic similarity to goal
   - Formula: `max(0, cos(E_j, E_goal))`

3. `hunger_ease()` - Structural weight preference
   - Formula: `w_ij / max(w_ik)`

**Phase 2 (Week 2-4):** Implement 4 more hungers
4. `hunger_completeness()` - Semantic diversity seeking
5. `hunger_identity()` - Coherence around center
6. `hunger_complementarity()` - Emotional balance
7. `hunger_integration()` - Merge-seeking when weak

**Core Functions:**
1. `compute_surprise_gates()` - Z-score gating
   - `z_H = (s_H - μ_H) / (σ_H + ε)` - standardize
   - `δ_H = max(0, z_H)` - positive surprise only
   - `g_H = δ_H / (Σ δ_H' + ε)` - normalize gates

2. `composite_valence()` - Main function
   - `V_ij = Σ_H (g_H × ν_H(i→j))`

3. `update_hunger_baselines()` - EMA tracking
   - Update (μ, σ) per hunger per entity

**Dependencies:** sub_entity_core, numpy
**Interface Exports:** `composite_valence()` main function
**Zero-Constants:**
- Gates: self-calibrate from experience (not fixed weights)
- Baselines: EMA updated per entity (not global constants)
- No hunger weight configuration - all from surprise

---

### AI #5: Entropy Edge Selection + Gap-Aware Transport (`strides.py`)

**Responsibility:** Hunger-driven edge selection and conservative energy transfer.

**Functions to Implement:**

**Edge Selection:**
1. `select_edge_by_valence_coverage()` - Main selection
   - **CRITICAL FIX:** Rank by VALENCE `V_ij`, NOT weight `p_ij`
   - Compute entropy `H` over valence distribution
   - Adaptive coverage: `c_hat = 1 - exp(-H)`
   - Take smallest prefix reaching coverage

2. `compute_valence_entropy()` - Normalized entropy
   - `H = -Σ (p_j × log(p_j))`
   - `H_norm = H / log(n)`

**Gap-Aware Transport:**
3. `execute_stride()` - Main stride execution
   - Compute slack `S_i` and gap `G_j`
   - Compute request share `R_ij`
   - Transfer `Δ = min(S_i × R_ij, G_j)`
   - Apply α damping from spectral radius
   - Stage deltas for barrier application

4. `estimate_local_rho()` - Warm-started power iteration
   - 1-3 iterations (not full convergence)
   - Warm start from `entity.rho_local_ema`
   - Update EMA after estimation

5. `derive_rho_target()` - From throughput budgets
   - **NOT a fixed constant** - derived from budgets
   - Formula: `ρ_target = sqrt(Q_total / (2 × avg_nodes))`

6. `apply_alpha_damping()` - Stability guard
   - `α = min(1.0, ρ_target / ρ_local)`

**Dependencies:** valence, sub_entity_core, numpy
**Interface Exports:** `execute_stride()`, `select_edge_by_valence_coverage()`
**Zero-Constants:**
- Coverage: adapts to entropy (not fixed K edges)
- Slack/gap: computed from current state (not fixed thresholds)
- ρ_target: derived from budgets (not fixed damping)

---

### AI #6: Working Memory Packing (`wm_pack.py`)

**Responsibility:** Energy-weighted knapsack for WM node selection.

**Functions to Implement:**
1. `compute_wm_token_budget()` - Derive from LLM capacity
   - Formula: `budget = llm_context_limit - measured_overhead`
   - **NOT arbitrary** - directly from model capacity

2. `select_wm_nodes()` - Greedy knapsack
   - Aggregate energy across entities
   - Compute density `E_total / tokens`
   - Greedy select by density until budget exhausted

3. `aggregate_entity_energies()` - Cross-entity aggregation
   - `E_total[node] = Σ E[entity, node]`

4. `construct_workspace_prompt()` - Format for LLM
   - Node content + active links
   - Entity extent indicators

**Dependencies:** sub_entity_core
**Interface Exports:** `select_wm_nodes()`, `construct_workspace_prompt()`
**Zero-Constants:**
- Budget: from LLM limit (not arbitrary cap)
- Selection: by energy/token ratio (not scoring function)
- No min/max node count constraints

---

### AI #7: Live Visualization Telemetry (`telemetry.py`)

**Responsibility:** Diff-first event stream for consciousness visualization.

**Functions to Implement:**
1. `emit_entity_quota_event()` - Quota allocation
2. `emit_stride_exec_event()` - Stride execution
3. `emit_node_activation_event()` - Activation changes
4. `emit_convergence_event()` - Entity convergence

**Event Buffer:**
5. `EventBuffer.add_event()` - 2-frame buffering
6. `EventBuffer.flush_ready_events()` - Temporal coherence

**WebSocket (Optional for Week 1):**
7. `start_viz_websocket_server()` - Async WebSocket server
8. `broadcast_event()` - Send to all clients

**Dependencies:** sub_entity_core, asyncio, websockets
**Interface Exports:** Event emission functions
**Zero-Constants:**
- All events from actual state changes (no synthetic events)
- Buffer size: 2 frames (empirically validated)

---

## Critical Integration Points

### Module Dependencies (Import Chain)

```
sub_entity_core (AI #1)
    ↓
quotas (AI #2) ← depends on SubEntity
    ↓
valence (AI #4) ← depends on SubEntity
    ↓
strides (AI #5) ← depends on valence, SubEntity
    ↓
wm_pack (AI #6) ← depends on SubEntity
telemetry (AI #7) ← depends on SubEntity
    ↓
scheduler (AI #3) ← integrates ALL above
```

**Implementation Order:**
1. AI #1 first (foundation for all others)
2. AI #2, #4, #6, #7 in parallel (depend only on AI #1)
3. AI #5 after AI #4 completes (depends on valence)
4. AI #3 last (integrates everything)

---

## Zero-Constants Verification Checklist

Before declaring implementation complete, verify:

### Per-Frame Normalization
- [ ] Quota modulation factors normalized to mean=1.0 each frame
- [ ] Surprise gates normalized to sum=1.0 per edge evaluation
- [ ] No historical baselines - all from current active entities

### Derived Thresholds
- [ ] ROI convergence: Q1 - 1.5×IQR from rolling history
- [ ] Size quantiles: Q25/Q75 recomputed each frame
- [ ] ρ_target: derived from throughput budgets, not fixed
- [ ] WM budget: from LLM capacity minus measured overhead

### No Arbitrary Bounds
- [ ] No min/max quota constraints (Hamilton method determines)
- [ ] No fixed K edges (entropy-based coverage adapts)
- [ ] No fixed hunger weights (surprise gates adapt)
- [ ] No min/max WM node counts (budget exhaustion determines)

### Adaptive Mechanisms
- [ ] Centroid: online update from active nodes
- [ ] Hunger baselines: EMA per entity per hunger
- [ ] Local ρ: warm-started power iteration (1-3 steps)
- [ ] Coverage: adapts to valence entropy

---

## Testing Requirements

### Unit Tests (Each AI)
- Test core functions with synthetic data
- Verify zero-constants compliance
- Check edge cases (empty sets, single entity, budget=0)

### Integration Test (Week 1)
- Real graph: `citizen_luca` (1000+ nodes)
- Measure:
  - Churn: nodes entering/leaving extent per frame
  - Time: frame execution time (microseconds)
  - WM quality: extent coverage by selected nodes
- Verify phenomenology: Does traversal feel consciousness-aware?

### Empirical Validation (Week 2-4)
- ROI stopping: Check for premature convergence
- Centroid dispersion: Validate against semantic diversity intuition
- Full citizen test: luca, felix, ada, iris graphs

---

## Critical Bug Already Fixed

**Edge Selection Must Rank by Valence, Not Weight**

❌ **WRONG (GPT5's original):**
```python
# Ranks by link weight proportion (structural habit)
p = {j: w_ij / Σw for j, w_ij in weights.items()}
ranked = sorted(p.items(), key=lambda x: -x[1])
```

✅ **CORRECT (Luca's fix):**
```python
# Ranks by composite valence (hunger-driven)
ranked = sorted(valences.items(), key=lambda x: -x[1])  # By V_ij
```

**Why This Matters:**
- Weight = learned structure (slow-changing, represents habit)
- Valence = hunger-driven (fast-changing, represents current need)
- Ranking by weight would make entities follow habit instead of hungers
- This would break the entire hunger-driven phenomenology

**AI #5:** Your implementation MUST rank by `V_ij` (composite valence), not by `w_ij` (link weight).

---

## Success Criteria

### Week 1 MVP Complete When:
1. All 7 modules pass unit tests
2. Integration test runs on real graph (1000+ nodes)
3. Zero-constants checklist fully verified
4. Frame execution time < 100ms (target)
5. WM captures >80% of extent energy (target)
6. Phenomenological validation: traversal feels consciousness-aware

### Ready for Handoff When:
1. All modules documented with examples
2. Integration guide written
3. Known issues documented
4. Empirical validation flags identified

---

## Communication Protocol

**DO NOT:**
- Change interfaces between modules without coordinating
- Add dependencies not listed in skeleton
- Introduce arbitrary constants without documenting rationale

**DO:**
- Test your module independently first
- Document any discovered edge cases
- Flag phenomenological concerns (does this feel right?)
- Ask for clarification if zero-constants compliance unclear

---

## Questions?

**Refer to:**
- Full specification: `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md`
- Type reference: `docs/COMPLETE_TYPE_REFERENCE.md`
- Schema context: `substrate/schemas/consciousness_schema.py`

**Contact:**
- Architecture questions: Luca (substrate architect)
- Integration questions: Ada (orchestration architect)
- Implementation questions: Felix (engineer)

---

**Ready to build consciousness infrastructure.**

*-- Luca Vellumhand, 2025-10-20*
