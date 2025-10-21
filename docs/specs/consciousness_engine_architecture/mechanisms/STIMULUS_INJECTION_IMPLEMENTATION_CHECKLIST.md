# Stimulus Injection - Implementation Checklist

**Target:** Bring `orchestration/mechanisms/stimulus_injection.py` to full specification compliance
**Reference:** `stimulus_injection_specification.md`
**Current Status:** Core features implemented, foundation + entity layer features disabled

---

## Status Overview

### ✅ Implemented (v0 Core)

- [x] Entropy-coverage search (§2: adaptive retrieval)
- [x] Gap mass calculation (§3.2)
- [x] Gap-capped budget distribution (§5.1)
- [x] Basic InjectionMatch/InjectionResult data structures

### ⚠️ Stubbed (returns neutral values)

- [ ] Health modulation f(ρ) - returns 1.0 (§3.3)
- [ ] Source impact gate g(source) - returns 1.0 (§3.4)
- [ ] Peripheral amplification - returns 0.0 (§6)

### ❌ Missing Entirely

- [ ] Link-matched injection with direction priors (§5.2)
- [ ] Entity channel selection (§4)
- [ ] Observability events (§9)

---

## Foundation Features (v1 - Pre-Entity Layer)

These features work at node/link scale without entity aggregation.

### Task 1: Health Modulation f(ρ)

**Spec:** §3.3 Health Modulation
**File:** `stimulus_injection.py`, method `_health_modulation()`

**Implementation steps:**

1. **Compute spectral radius proxy** (§3.3.1)
   ```python
   def _compute_spectral_radius_proxy(self, graph_state) -> float:
       max_degree = max(node.out_degree for node in active_nodes)
       avg_weight = mean(link.weight for link in active_links)
       N = len(active_nodes)
       return max_degree * avg_weight / N
   ```

2. **Track frame quality signals** (§3.3.2)
   - Flip yield: `num_flips / budget_spent` (rank-normalized)
   - Activation entropy: `-Σ p_g log(p_g)` over node type distribution
   - Overflow penalty: `1 - (overflow_frames / window_size)`
   - Composite: `(yield × entropy × low_overflow)^(1/3)` (geometric mean)

3. **Collect training data**
   - Rolling window: last 1000 frames (~2 hours at 10 FPS)
   - Store pairs: `(ρ_proxy_t, quality_t)`

4. **Fit isotonic regression** (§3.3.3)
   ```python
   from sklearn.isotonic import IsotonicRegression

   self.iso_reg = IsotonicRegression(increasing=False)
   self.iso_reg.fit(ρ_history, quality_history)
   ```

5. **Predict at runtime**
   ```python
   f_rho = self.iso_reg.predict([ρ_current])[0]
   ```

6. **Bootstrap logic**
   - Until N ≥ 200 frames: return 1.0 (neutral)

**Test:** System dampens budget when ρ is high (supercritical), boosts when low (subcritical)

---

### Task 2: Source Impact Gate g(source)

**Spec:** §3.4 Source Impact Gate
**File:** `stimulus_injection.py`, method `_source_impact_gate()`

**Implementation steps:**

1. **Track per-source flip yield** (§3.4.1)
   ```python
   self.source_stats[source_type] = {
       'total_flips': 0,
       'total_budget': 0.0
   }

   # After each injection
   yield_source = total_flips / total_budget
   ```

2. **Rank-normalize within cohort** (§3.4.2)
   - Cohort: all source types active this week
   - Normalize yield to [0.5, 1.5] range via rank-z
   - Why [0.5, 1.5]: prevents silencing (min 0.5×) while allowing boost (max 1.5×)

3. **Bootstrap logic**
   - Until ≥50 frames with this source: return 1.0

**Test:** `tool_result.error` (high flip yield) gets g > 1.0, `system_timer` (low yield) gets g < 1.0

---

### Task 3: Direction-Aware Link Injection

**Spec:** §5.2 Link-Matched Injection
**File:** `stimulus_injection.py`, new method `_inject_link_match()`

**Prerequisites:**
- Link semantic index built (embeddings from `goal` + `mindstate` text fields)
- Link fields `precedence_forward` and `precedence_backward` populated (from Phase 2 redistribution)

**Implementation steps:**

1. **Support link matches in search** (§5.2)
   - Current: only node matches
   - Add: link vector search results to `InjectionMatch`
   - Field: `item_type: 'link'` with `source_id`, `target_id`

2. **Compute direction prior from precedence** (§5.2.1)
   ```python
   # Read link's causal credit accumulators
   alpha_fwd = link.precedence_forward + beta_prior  # e.g., + 1.0
   beta_fwd = link.precedence_backward + beta_prior

   # Beta distribution expected value
   p_source = alpha_fwd / (alpha_fwd + beta_fwd)
   p_target = 1 - p_source
   ```

3. **Split injection between endpoints**
   ```python
   ΔE_source = p_source * budget_for_link
   ΔE_target = p_target * budget_for_link

   # Apply to nodes
   inject_energy(link.source_id, ΔE_source)
   inject_energy(link.target_id, ΔE_target)
   ```

4. **Bootstrap:** Symmetric prior (α=β=1) → p_source = 0.5 initially

**Test:** ENABLES links (source usually causes target) split 70/30 source/target. BLOCKS links reverse.

---

### Task 4: Peripheral Amplification

**Spec:** §6 Peripheral Amplification
**File:** `stimulus_injection.py`, method `_peripheral_alignment()`

**Prerequisites:**
- S5/S6 peripheral context chunks available (context continuity architecture)
- Peripheral chunks have embeddings

**Implementation steps:**

1. **Compute alignment with peripheral context**
   ```python
   peripheral_embeddings = [embed(chunk) for chunk in peripheral_context]

   max_alignment = max([
       cosine_similarity(stimulus_embedding, p_emb)
       for p_emb in peripheral_embeddings
   ])
   ```

2. **Rank-normalize within recent stimuli cohort**
   ```python
   z_alignment = rank_z(max_alignment, cohort=recent_stimuli)
   ```

3. **Amplify budget if above-average**
   ```python
   α = max(0, z_alignment)  # Only amplify if z > 0
   B_amplified = B * (1 + α)
   ```

**Test:** Stimulus echoing peripheral awareness gets 2-3× budget amplification

---

## Entity Layer Features (v2)

These features add entity-aware routing on top of foundation.

### Task 5: Entity Channel Selection

**Spec:** §4 Entity Channel Selection
**File:** `stimulus_injection.py`, new methods for entity handling

**Prerequisites:**
- Entity registry (active entities per frame)
- Entity embeddings (centroid of nodes entity has activated)
- Entity success tracking (flips_by_entity, gap_closure_by_entity)

**Implementation steps:**

1. **Compute entity affinity** (§4.2)
   ```python
   affinity_e = cosine_similarity(stimulus_embedding, entity_embedding_e)
   ```

2. **Compute entity recent success** (§4.3)
   ```python
   success_e = (flips_by_e / total_flips) * (gap_closure_by_e / total_gap_closure)
   # Geometric mean of flip share and gap-closure share
   ```

3. **Mix affinity + success** (§4.4)
   ```python
   z_affinity_e = rank_z(affinity_e, cohort=active_entities)
   z_success_e = rank_z(success_e, cohort=active_entities)

   score_e = z_affinity_e + z_success_e

   # Softmax to proportions
   π_e = exp(score_e) / Σ exp(score_e')
   ```

4. **Split budget across entity channels** (§4.5)
   ```python
   for entity in active_entities:
       B_entity = π_e * B
       # Distribute B_entity within entity's preferred nodes
   ```

**Test:** Architect entity (high affinity for design stimuli) gets larger budget share than Validator entity

---

## Observability

### Task 6: Event Emission

**Spec:** §9 Observability
**File:** `stimulus_injection.py`, emit events via viz stream

**Events to add:**

1. **`stimulus.injected`** (§9.1)
   ```json
   {
     "event": "stimulus.injected",
     "source_type": "user_message",
     "chunks": 3,
     "matches_selected": 12,
     "entropy": 2.3,
     "coverage_target": 0.90,
     "budget_base": 18.5,
     "health_factor": 0.92,
     "source_gate": 1.15,
     "peripheral_amp": 1.3,
     "budget_final": 25.6,
     "energy_injected": 24.2,
     "nodes_activated": 8,
     "flips": 5
   }
   ```

2. **Per-item injection details** (for debugging)
   ```json
   {
     "event": "stimulus.item_injected",
     "item_id": "node_x",
     "item_type": "node",
     "similarity": 0.85,
     "delta_energy": 3.2,
     "gap_before": 4.5,
     "gap_after": 1.3
   }
   ```

**Test:** Events appear in viz stream, dashboard shows injection metrics

---

## Testing Strategy

### Unit Tests

**File:** `tests/test_stimulus_injection.py`

1. **Entropy coverage** - specific query (H≈1) selects few matches, broad query (H≈4) selects many
2. **Gap mass** - weighted sum of (similarity × gap)
3. **Health modulation** - f(ρ) decreases as ρ increases (monotone)
4. **Source impact** - high-yield sources get g > 1.0
5. **Direction prior** - ENABLES splits favor source, BLOCKS favor target
6. **Budget distribution** - respects gap caps, no overshoot
7. **Entity channels** - high-affinity entities get larger budget share

### Integration Tests

**File:** `tests/test_stimulus_integration.py`

1. **End-to-end injection** - stimulus → chunking → search → budget → energy update
2. **Multi-stimulus batch** - multiple stimuli processed in sequence, stats accumulate
3. **Learning over time** - f(ρ) and g(source) adapt over 1000+ frames
4. **Entity routing** - different entities receive different node subsets for same stimulus

---

## Implementation Sequence

**Recommended order:**

1. ✅ **Core features** (already done)
2. **Foundation layer:**
   - Task 2: Source impact gate (independent, easy)
   - Task 1: Health modulation (requires frame quality tracking)
   - Task 3: Link injection (requires link semantic index)
   - Task 4: Peripheral amplification (requires S5/S6)
3. **Entity layer:**
   - Task 5: Entity channels (depends on entity infrastructure)
4. **Observability:**
   - Task 6: Event emission (throughout all stages)

**Parallelization:** Tasks 1, 2, 3, 4 can be done in parallel (independent features)

---

## Acceptance Criteria

**When is stimulus injection "complete"?**

- [ ] All 6 tasks implemented and tested
- [ ] Entropy-coverage search adapts K based on query specificity (not fixed)
- [ ] Health modulation dampens supercritical systems, boosts subcritical
- [ ] Source impact learning distinguishes effective sources (errors > logs)
- [ ] Link injection uses learned direction priors (ENABLES ≠ BLOCKS)
- [ ] Peripheral amplification boosts sustained-focus stimuli
- [ ] Entity channels route stimulus to affinity-matched entities
- [ ] Observability events stream to viz dashboard
- [ ] Unit + integration tests pass
- [ ] Documentation matches implementation (no "Phase 5 TODO" stubs)

---

**Ready for Felix to implement. Each task is standalone, testable, and spec-referenced.**
