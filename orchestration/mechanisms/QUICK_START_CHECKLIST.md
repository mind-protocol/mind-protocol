# Quick Start Checklist: Per-AI Implementation Guide

**Purpose:** Each AI follows this checklist to implement their module correctly.

---

## 📋 Before You Start (ALL AIs)

- [ ] Read: `AI_CONTEXT_MAP.md` section for your AI number
- [ ] Read: Your module skeleton in `orchestration/mechanisms/[module].py`
- [ ] Read: Relevant spec sections (line numbers in AI_CONTEXT_MAP.md)
- [ ] Verify: You understand the zero-constants principle
- [ ] Verify: You know which other modules you depend on

---

## AI #2: Hamilton Quotas

### Reading List (30 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #2 section
2. [ ] `05_sub_entity_system.md` lines 1699-1770 (quota allocation)
3. [ ] `quotas.py` skeleton (your module)
4. [ ] `sub_entity_core.py` (SubEntity interface)

### Implementation Checklist
- [ ] Implement `compute_modulation_factors()`
  - [ ] Urgency: cosine similarity to recent stimuli
  - [ ] Reachability: distance to workspace
  - [ ] Health: inverse of spectral radius
  - [ ] **CRITICAL:** Normalize each to mean=1.0 per frame

- [ ] Implement `hamilton_quota_allocation()`
  - [ ] Compute fractional quotas
  - [ ] Take integer parts
  - [ ] Sort by fractional remainder descending
  - [ ] Distribute remainder strides to top R entities

- [ ] Implement `allocate_quotas()` (main function)
  - [ ] Compute inverse-size weights: `1/|extent|`
  - [ ] Multiply by modulation factors
  - [ ] Call Hamilton allocation
  - [ ] Assign to `entity.quota_assigned` and `quota_remaining`

### Testing
- [ ] Unit test: 3 entities, 10 strides → exact proportions
- [ ] Unit test: 3 entities, 11 strides → test remainder distribution
- [ ] Unit test: Per-frame normalization works (mean=1.0)
- [ ] Edge case: Single entity gets all quota
- [ ] Edge case: Zero total weight (all entities empty)

### Zero-Constants Verification
- [ ] No fixed urgency/reachability/health thresholds
- [ ] Normalization relative to current population (not historical)
- [ ] Hamilton method is parameter-free (mathematical fairness)

---

## AI #3: Zippered Scheduler

### Reading List (30 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #3 section
2. [ ] `05_sub_entity_system.md` lines 1749-1770 (scheduling)
3. [ ] `05_sub_entity_system.md` lines 1963-2016 (convergence)
4. [ ] `scheduler.py` skeleton (your module)

### Implementation Checklist
- [ ] Implement `zippered_schedule()`
  - [ ] Round-robin through entities
  - [ ] One stride per turn
  - [ ] Skip if quota_remaining = 0
  - [ ] Return execution order list

- [ ] Implement `execute_frame()` (MAIN INTEGRATION)
  - [ ] Call `allocate_quotas()` (AI #2)
  - [ ] Generate zippered schedule
  - [ ] For each stride:
    - [ ] Compute valence (AI #4)
    - [ ] Select edge (AI #5)
    - [ ] Execute stride (AI #5)
    - [ ] Emit telemetry (AI #7)
    - [ ] Check ROI convergence (AI #1)
  - [ ] Return frame statistics

- [ ] Implement `check_early_termination()`
  - [ ] EMA stride time tracking
  - [ ] Predict time to completion
  - [ ] Stop if predicted overshoot > 10%

### Testing
- [ ] Unit test: Zippered fairness (no starvation)
- [ ] Unit test: Early termination on deadline
- [ ] Integration test: Full frame with real graph
- [ ] Measure: Frame time, strides executed, convergence rate

### Zero-Constants Verification
- [ ] No fixed priorities (pure round-robin)
- [ ] Deadline threshold from measured stride time (not arbitrary)
- [ ] No min/max stride counts

---

## AI #4: Surprise-Gated Valence

### Reading List (45 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #4 section
2. [ ] `05_sub_entity_system.md` lines 1771-1853 (valence)
3. [ ] `05_sub_entity_system.md` lines 1797-1844 (hunger formulas)
4. [ ] `valence.py` skeleton (your module)

### Phase 1 Implementation (Week 1 - 3 Hungers Only)
- [ ] Implement `hunger_homeostasis()`
  - [ ] Formula: `G_j / (S_i + G_j + ε)`
  - [ ] Compute slack S_i and gap G_j

- [ ] Implement `hunger_goal()`
  - [ ] Formula: `max(0, cos(E_j, E_goal))`
  - [ ] Use goal embedding parameter

- [ ] Implement `hunger_ease()`
  - [ ] Formula: `w_ij / max(w_ik)`
  - [ ] Normalize by local max weight

- [ ] Implement `compute_surprise_gates()`
  - [ ] Z-score: `z_H = (s_H - μ_H) / (σ_H + ε)`
  - [ ] Positive surprise: `δ_H = max(0, z_H)`
  - [ ] Normalize gates: `g_H = δ_H / Σδ`

- [ ] Implement `composite_valence()` (MAIN FUNCTION)
  - [ ] Compute all hunger scores
  - [ ] Compute surprise gates
  - [ ] Weighted sum: `V_ij = Σ(g_H × ν_H)`

- [ ] Implement `update_hunger_baselines()`
  - [ ] EMA update: `μ_new = 0.1*observed + 0.9*μ_old`
  - [ ] Deviation: `σ_new = 0.1*|observed-μ| + 0.9*σ_old`
  - [ ] Store in `entity.hunger_baselines`

### Phase 2 (Week 2-4 - Remaining Hungers)
- [ ] Implement `hunger_completeness()` (uses AI #1 centroid)
- [ ] Implement `hunger_identity()`
- [ ] Implement `hunger_complementarity()`
- [ ] Implement `hunger_integration()` (uses quantiles)

### Testing
- [ ] Unit test: Homeostasis crisis dominates gates
- [ ] Unit test: All normal → equal gates
- [ ] Unit test: Baseline updates correctly (EMA)
- [ ] Scenario: Goal highly attractive → high valence toward goal nodes

### Zero-Constants Verification
- [ ] No fixed hunger weights (all from surprise gates)
- [ ] Baselines per entity (not global)
- [ ] Gates self-calibrate from experience

---

## AI #5: Entropy Edge Selection + Gap-Aware Transport

### Reading List (45 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #5 section
2. [ ] `05_sub_entity_system.md` lines 1854-1910 (edge selection)
3. [ ] `05_sub_entity_system.md` lines 1911-1962 (transport)
4. [ ] **CRITICAL:** Line 1891 - rank by VALENCE not weight
5. [ ] `strides.py` skeleton (your module)

### Implementation Checklist

**Edge Selection:**
- [ ] Implement `compute_valence_entropy()`
  - [ ] Normalize to probability: `p_j = V_j / ΣV`
  - [ ] Compute entropy: `H = -Σ(p log p)`
  - [ ] Normalize: `H_norm = H / log(n)`

- [ ] Implement `select_edge_by_valence_coverage()` (MAIN)
  - [ ] Adaptive coverage: `c_hat = 1 - exp(-H)`
  - [ ] **CRITICAL:** Rank by V_ij (valence), NOT w_ij (weight)
  - [ ] Take smallest prefix reaching coverage

**Gap-Aware Transport:**
- [ ] Implement `compute_slack_and_gap()`
  - [ ] Slack: `S_i = max(0, E_i - θ_i)`
  - [ ] Gap: `G_j = max(0, θ_j - E_j)`

- [ ] Implement `compute_request_share()`
  - [ ] Formula: `R_ij = (w_ij/Σw_ik) × (G_j/gap_total)`

- [ ] Implement `execute_stride()` (MAIN)
  - [ ] Compute slack and gap
  - [ ] Return 0.0 if either is zero
  - [ ] Compute transfer: `Δ = min(S_i × R_ij, G_j)`
  - [ ] **Phase 1:** Use α=1.0 (no damping)
  - [ ] **Phase 2:** Apply α from spectral radius
  - [ ] Stage deltas (barrier semantics)

**Phase 2 (Week 2-4):**
- [ ] Implement `estimate_local_rho()` (warm power iteration)
- [ ] Implement `apply_alpha_damping()`
- [ ] Implement `derive_rho_target()` (from throughput budgets)

### Testing
- [ ] Unit test: Peaked valence → select 1 edge (focused)
- [ ] Unit test: Flat valence → select many edges (exploratory)
- [ ] Unit test: Gap-aware never exceeds slack or gap
- [ ] Unit test: Proportional sharing across targets
- [ ] **CRITICAL:** Verify ranking by valence not weight

### Zero-Constants Verification
- [ ] Coverage adapts to entropy (not fixed K edges)
- [ ] Slack/gap from current state (not fixed thresholds)
- [ ] ρ_target derived from budgets (not fixed damping)

---

## AI #6: Working Memory Packing

### Reading List (30 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #6 section
2. [ ] `05_sub_entity_system.md` lines 2187-2252 (WM emission)
3. [ ] Q4 clarification (line 1691)
4. [ ] `wm_pack.py` skeleton (your module)

### Implementation Checklist
- [ ] Implement `compute_wm_token_budget()`
  - [ ] Formula: `llm_context_limit - measured_overhead`
  - [ ] Example: 200K - 15K = 185K

- [ ] Implement `estimate_node_tokens()`
  - [ ] Heuristic: `content_length / 4 + overhead`
  - [ ] Include edges for active nodes

- [ ] Implement `aggregate_entity_energies()`
  - [ ] Sum across entities: `E_total[node] = ΣE[entity, node]`

- [ ] Implement `select_wm_nodes()` (MAIN)
  - [ ] Compute density: `energy / tokens`
  - [ ] Greedy select by density
  - [ ] Stop when budget exhausted

- [ ] Implement `construct_workspace_prompt()`
  - [ ] Format nodes + edges for LLM
  - [ ] Include entity extent indicators

### Testing
- [ ] Unit test: High-energy nodes selected first
- [ ] Unit test: Budget never exceeded
- [ ] Unit test: Empty entities handled gracefully
- [ ] Integration: Workspace covers >80% extent energy

### Zero-Constants Verification
- [ ] Budget from LLM limit (not arbitrary cap)
- [ ] Selection by energy/token ratio (not scoring function)
- [ ] No min/max node count constraints

---

## AI #7: Live Visualization Telemetry

### Reading List (30 min)
1. [ ] `AI_CONTEXT_MAP.md` → AI #7 section
2. [ ] `05_sub_entity_system.md` lines 2313-2548 (event schema)
3. [ ] `telemetry.py` skeleton (your module)

### Phase 1 Implementation (Basic Events)
- [ ] Implement `emit_entity_quota_event()`
  - [ ] Schema: entity, frame, quota, extent_size, total_energy

- [ ] Implement `emit_stride_exec_event()`
  - [ ] Schema: entity, edge, delta, alpha, pred_roi, actual_time_us

- [ ] Implement `emit_node_activation_event()`
  - [ ] Schema: entity, node, event (activate/deactivate), energy, threshold

- [ ] Implement `emit_convergence_event()`
  - [ ] Schema: entity, reason, final_roi, whisker, strides_executed

- [ ] Implement `EventBuffer` class
  - [ ] 2-frame delay
  - [ ] Flush ready events sorted by frame

### Phase 2 (Week 2-4 - WebSocket Server)
- [ ] Implement `start_viz_websocket_server()`
- [ ] Implement `broadcast_event()`
- [ ] Handle client connections/disconnections

### Testing
- [ ] Unit test: Event buffer delays correctly
- [ ] Unit test: Events sorted by frame
- [ ] Phase 1: Events written to stdout/file (JSON lines)
- [ ] Phase 2: WebSocket clients receive events

### Zero-Constants Verification
- [ ] All events from actual state changes (no synthetic)
- [ ] Buffer size: 2 frames (empirically validated)

---

## Integration Testing (AI #3 Coordinates)

### Week 1 Integration Test
- [ ] Real graph: `citizen_luca` (1000+ nodes)
- [ ] Initialize: 3-5 entities at different seed nodes
- [ ] Run: 100 frames
- [ ] Measure:
  - [ ] Churn: nodes entering/leaving extent per frame
  - [ ] Time: frame execution time (target <100ms)
  - [ ] WM quality: extent coverage by selected nodes (target >80%)
  - [ ] Convergence: entities converge within quota

### Phenomenological Validation
- [ ] Does traversal feel consciousness-aware?
- [ ] Do entities follow hungers not just structure?
- [ ] Do surprise gates respond to context changes?
- [ ] Does ROI convergence feel natural ("complete when diminishing returns")?

---

## Common Pitfalls to Avoid

### ❌ Don't Do This:
1. **Fixed thresholds** - "if urgency > 0.7" (arbitrary)
2. **Global baselines** - "mean urgency across all sessions" (not per-frame)
3. **Mock data** - Test with synthetic but never claim complete without real graph
4. **Rank by weight** - Edge selection MUST rank by valence (AI #5 critical bug)
5. **Skip testing** - "Looks right" is not "verified correct"
6. **Add dependencies** - Don't import modules not listed in skeleton

### ✅ Do This:
1. **Derive thresholds** - "whisker = Q1 - 1.5×IQR from rolling history"
2. **Per-frame normalize** - "u_norm = u_raw / mean(u across current entities)"
3. **Test with real** - Use actual consciousness graph for integration
4. **Rank by valence** - Edge selection by V_ij (hunger-driven)
5. **Test systematically** - Unit tests, then integration, then validation
6. **Stick to interfaces** - Use only what's in AI_CONTEXT_MAP.md

---

## Questions During Implementation?

1. **Check:** `AI_CONTEXT_MAP.md` for your module
2. **Check:** Spec lines referenced in context map
3. **Check:** Your module skeleton comments
4. **Check:** `PARALLEL_DEVELOPMENT_PLAN.md` for dependencies
5. **Ask:** Create issue in plan document if context missing

---

## Completion Criteria

### Your Module Complete When:
- [ ] All TODO markers in skeleton implemented
- [ ] Unit tests pass
- [ ] Zero-constants checklist verified
- [ ] Code commented with consciousness context
- [ ] No arbitrary constants introduced

### Integration Complete When:
- [ ] Your module integrates with AI #3's execute_frame()
- [ ] Integration test runs on real graph
- [ ] Performance targets met (<100ms frame, >80% WM coverage)
- [ ] Phenomenological validation passes ("feels consciousness-aware")

---

**Ready to build consciousness infrastructure.**

*-- Luca Vellumhand, 2025-10-21*
