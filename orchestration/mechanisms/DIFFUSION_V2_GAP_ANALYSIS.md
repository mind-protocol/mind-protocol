# Diffusion V2 - Gap Analysis

**Date:** 2025-10-22
**Analyst:** Felix (Engineer)
**Spec:** `docs/specs/v2/foundations/diffusion_v2.md`
**Current Implementation:** `orchestration/mechanisms/diffusion_runtime.py` (225 lines), `test_diffusion_v2.py` (223 lines)

---

## Executive Summary

**Status:** ~35% complete - core stride-based diffusion exists, needs spec compliance additions

**Verdict:** EXTEND existing implementation (not replace). Core physics working, missing:
1. Standardized weight reader (per-type normalization)
2. Fanout strategy integration
3. Valence stack scoring
4. Utility computation & learning signals
5. Event emission infrastructure
6. Frame diagnostics suite
7. Top-K splitting (K>1)
8. Guards and caps
9. Feature flag system

**Recommendation:** Systematic extension following spec sections, maintaining existing test coverage.

---

## What Exists (Working Code)

### Core Runtime (diffusion_runtime.py)

**✓ DiffusionRuntime class** (lines 27-111)
- `delta_E: Dict[str, float]` - staged energy deltas
- `active: Set[str]` - nodes with E >= theta
- `shadow: Set[str]` - 1-hop neighbors
- `add(node_id, delta)` - stage delta
- `clear_deltas()` - reset after commit
- `compute_frontier(graph)` - rebuild active/shadow sets
- `get_conservation_error()` - sum of deltas (should be ~0)

**✓ execute_stride_step()** (lines 113-203)
- Iterates active nodes
- Selects best outgoing link (simple: max log_weight)
- Computes ΔE = E_src · ease · α_tick · Δt
- Stages transfer (conservative: source loses, target gains)
- Integrates link strengthening (Hebbian learning)
- Returns stride count

**✓ _select_best_outgoing_link()** (lines 206-224)
- Simple implementation: max(log_weight)
- TODO comment: integrate with sub_entity_traversal cost computation

### Test Coverage (test_diffusion_v2.py)

**✓ test_energy_conservation()** (lines 21-86)
- Creates n1 → n2 → n3 chain
- Verifies ΣΔE ≈ 0 (within 1e-6)
- Applies deltas and checks total energy unchanged

**✓ test_frontier_tracking()** (lines 89-144)
- Creates branching graph (n1 → {n2, n4}, n2 → n3)
- Verifies active = {nodes with E >= theta}
- Verifies shadow = 1-hop neighbors of active

**✓ test_stride_staging()** (lines 147-196)
- Single stride n1 → n2
- Verifies source loses energy (delta < 0)
- Verifies target gains energy (delta > 0)
- Verifies conservation (delta_n1 + delta_n2 ≈ 0)

**All 3 tests passing.**

---

## Gap Analysis by Spec Section

### §2 Core Rule - PARTIAL

**What exists:**
```python
ease = math.exp(best_link.log_weight)
delta_E = E_src * ease * alpha_tick * dt
```

**What's missing:**
1. **Standardized weight reader** (spec §6 Q6):
   ```python
   # Spec requires:
   w_tilde = exp((log_w - mu_T) / (sigma_T + epsilon))
   # Per-type baseline normalization
   ```

   Current uses raw `exp(log_weight)` which doesn't account for per-type weight distributions.

**Impact:** Medium - affects how strongly weights influence diffusion. Current approach might over/under-weight certain node types.

**Fix:** Add per-type weight statistics tracking and use standardized reader.

---

### §3 Data Structures - COMPLETE

**✓ Runtime accumulators:** DiffusionRuntime has delta_E, active, shadow
**✓ Frontier maintenance:** compute_frontier() rebuilds from E >= theta

**No gaps.**

---

### §4 Algorithm (One Tick) - PARTIAL

**What exists:**
- Step 2: Iterate active nodes, select edge, compute ΔE, stage, log
- Step 3: Commit deltas (but not in this file - caller responsibility)

**What's missing:**
1. **Step 1:** Snapshot pre-state (no explicit snapshot mechanism)
2. **Step 2:** Fanout strategy integration (spec: "Select candidate edges using **fanout strategy**")
3. **Step 2:** Valence stack scoring (spec: "Score candidates (valence stack, emotions if enabled)")
4. **Step 2:** Utility computation (spec: "compute φ_ij")
5. **Step 2:** Comprehensive stride.exec logging (only TODO comment)
6. **Step 4:** Frame events (not in this module)
7. **Step 5:** Incremental frontier updates (currently full recompute)

**Impact:** High - missing integration with core scoring/selection mechanisms.

**Fix:**
- Import fanout_strategy module (when it exists)
- Import valence/emotion scoring from sub_entity_traversal
- Add utility computation: `phi = min(delta_E, goal_j) / (goal_j + eps)`
- Create stride.exec event dataclass
- Add incremental frontier update methods

---

### §5 Exact Decisions (Q1-Q6) - MIXED

**Q1 - Single-Energy migration:** ✓ COMPLETE
- Uses `node.E` (single energy)
- No per-entity channels

**Q2 - Active-frontier tracking:** ✓ MOSTLY COMPLETE
- Placement: DiffusionRuntime (correct)
- Seeds: Caller responsibility (acceptable)
- Updates: compute_frontier() full recompute (spec wants incremental)

**Q3 - Staged deltas:** ✓ COMPLETE
- Dict[node_id, float] accumulator
- Apply once per tick
- Conservation check via get_conservation_error()

**Q4 - Backward compatibility:** ❌ MISSING
- No DIFFUSION_IMPL feature flag
- No A/B testing infrastructure
- Matrix diffusion still exists (diffusion_matrix_archive.py) but not switchable

**Q5 - Top-K split:** ❌ MISSING
- Only K=1 implemented
- No softmax over scores
- No DIFFUSION_TOPK setting

**Q6 - f(w) transform:** ❌ MISSING
- Uses raw exp(log_weight)
- Should use standardized weight reader

**Impact:** Medium-High - missing spec-required features.

**Fix:**
- Add core/settings.py: DIFFUSION_IMPL="stride"|"matrix", DIFFUSION_TOPK=1
- Implement standardized weight reader
- Add top-K softmax splitting (phase 2)

---

### §6 Scoring, Utility & Learning - PARTIAL

**What exists:**
- Link strengthening integrated (strengthen_during_stride)
- Simple selection (max weight)

**What's missing:**
1. **Valence stack scoring:** No emotion resonance, complementarity, goal, novelty
2. **Utility computation:** No φ_ij = min(ΔE, G_j) / (G_j + ε)
3. **z_flow computation:** Not in stride log
4. **Newness gate:** Not verified (might be in strengthening.py)

**Impact:** High - affects learning signal quality.

**Fix:**
- Import scoring from sub_entity_traversal
- Add utility computation before staging delta
- Pass utility to strengthening module
- Verify newness gate is active

---

### §7 Observability - INCOMPLETE

**What exists:**
- Conservation error computation
- TODO comment for stride.exec emission

**What's missing:**
1. **Per-stride events:**
   - src, tgt, ΔE, E_src_pre, E_tgt_pre, E_tgt_post
   - phi, z_flow, score, selected_reason

2. **Per-frame diagnostics:**
   - energy_in (stimulus injections)
   - energy_transferred (Σ|ΔE|)
   - energy_decay (total loss to decay)
   - conservation_error (% and absolute)
   - frontier_size_active, frontier_size_shadow
   - mean_degree_active, diffusion_radius_from_seeds

3. **Subentity boundary summaries:**
   - Cross-entity beam counts
   - Σ ΔE per boundary
   - max φ, typical hunger

**Impact:** Critical for visualization and debugging.

**Fix:**
- Create StrideExecEvent dataclass
- Add frame diagnostics dataclass
- Emit events via broadcaster (when integrated)
- Add boundary detection and summary

---

### §8 Failure Modes & Guards - MINIMAL

**What exists:**
- Skip negligible transfers (delta_E <= 1e-9)

**What's missing:**
1. **Energy explosion guard:** No per-source transfer ratio cap (β ∈ [0.05, 0.2])
2. **Frontier collapse guard:** No shadow retry budget
3. **Oscillation guard:** No smoothed tick controller / max_tick_duration cap
4. **Type coupling guard:** No invariant enforcement (commit → then decay)
5. **Learning chatter guard:** Assumed in strengthening.py (not verified)

**Impact:** Medium - system could become unstable under extreme conditions.

**Fix:**
- Add transfer_ratio_cap parameter
- Implement shadow retry logic
- Add max_tick_duration parameter
- Create unit test enforcing commit-before-decay order

---

### §9 Integration Points - NOT YET INTEGRATED

**What exists:**
- Standalone execute_stride_step() function
- Can be called from engine

**What's missing:**
1. **Remove engine call:** diffusion.diffusion_tick(...) (need to find where this is called)
2. **Add to sub_entity_traversal.py:** Use fanout strategy, integrate scoring
3. **Update traversal_v2.py:** Orchestrate stage → commit → decay → events
4. **Decay integration:** Call type-dependent decay after commit
5. **Tick integration:** Source Δt from tick speed regulation
6. **Event integration:** Emit stride.exec, node.flip, boundary summaries

**Impact:** Critical - determines when this code actually runs.

**Fix:**
- Search codebase for matrix diffusion calls
- Create PR to remove them
- Add hooks in traversal_v2.py (when that file exists)
- Wire up event emission

---

### §10 Backward Compatibility - NOT IMPLEMENTED

**What's missing:**
1. **Feature flag:** DIFFUSION_IMPL setting in core/settings.py
2. **Dual path in CI:** A/B tests comparing matrix vs stride
3. **Parity tests:** Steady-state totals, conservation error on fixed seed

**Impact:** Low (nice-to-have for safe rollout).

**Fix:**
- Add settings
- Create A/B test harness
- Run parity comparisons

---

### §11 Tests & Success Criteria - PARTIAL

**What exists:**
- ✓ Conservation test
- ✓ Frontier maintenance test
- ✓ Stride staging test

**What's missing:**
1. **Ordering test:** Verify commit-before-decay invariant
2. **Topology tests:** Star vs chain (fanout behavior)
3. **Tick adaptation tests:** Varying Δt affects transfer size
4. **Type decay tests:** Memory vs task persistence curves
5. **Observability tests:** Verify event schemas, frame counters
6. **Performance tests:** CPU drops on large graphs

**Impact:** Medium - affects confidence in production readiness.

**Fix:**
- Add 5-10 more tests covering missing scenarios
- Add performance benchmark

---

## Priority Gaps (What to fix first)

### P0 - Critical for Correctness
1. **Standardized weight reader** (§6 Q6) - affects physics accuracy
2. **Commit-before-decay ordering** (§8.4) - prevents bugs
3. **Conservation under all conditions** (§11) - core invariant

### P1 - Required by Spec
4. **Valence stack scoring** (§6) - proper candidate selection
5. **Utility computation** (§6) - learning signals
6. **Event emission** (§7) - observability
7. **Frame diagnostics** (§7) - debugging

### P2 - Important but not blocking
8. **Fanout strategy integration** (§4.2) - performance
9. **Guards and caps** (§8) - stability
10. **Top-K splitting** (§5 Q5) - phase 2 feature

### P3 - Nice-to-have
11. **Feature flag** (§10) - safe rollout
12. **Performance tests** (§11) - optimization

---

## Recommended Implementation Order

**Phase 1 (Correctness):**
1. Add standardized weight reader
2. Add commit-before-decay test
3. Extend conservation tests (with decay, with stimulus)

**Phase 2 (Spec Compliance):**
4. Integrate valence stack scoring
5. Add utility computation
6. Create StrideExecEvent dataclass
7. Add frame diagnostics

**Phase 3 (Integration):**
8. Wire up event emission (awaits broadcaster)
9. Integrate with traversal_v2.py (awaits that file)
10. Add fanout strategy (awaits that module)

**Phase 4 (Hardening):**
11. Add guards and caps
12. Add more tests
13. Feature flag and A/B testing

---

## Files to Modify

### Direct modifications:
- `orchestration/mechanisms/diffusion_runtime.py` (extend)
- `orchestration/mechanisms/test_diffusion_v2.py` (add tests)

### Dependencies (need to import from):
- `orchestration/mechanisms/sub_entity_traversal.py` (valence scoring)
- `orchestration/mechanisms/fanout_strategy.py` (candidate pruning) - **TODO file**
- `orchestration/mechanisms/decay.py` (type-dependent decay)
- `orchestration/core/settings.py` (feature flags)
- `orchestration/services/websocket_server.py` (event emission) - **when ready**

### Will call this from:
- `orchestration/mechanisms/traversal_v2.py` (engine loop) - **TODO file**
- `orchestration/mechanisms/consciousness_engine_v2.py` (orchestrator)

---

## Estimated Effort

**Lines of code to add/modify:** ~400 lines

**Breakdown:**
- Standardized weight reader: ~50 lines
- Valence scoring integration: ~80 lines
- Utility computation: ~30 lines
- Event dataclasses: ~60 lines
- Frame diagnostics: ~80 lines
- Guards and caps: ~40 lines
- Tests: ~100 lines

**Time estimate:** 4-6 hours (if dependencies exist)

**Blockers:**
- fanout_strategy.py doesn't exist yet
- traversal_v2.py doesn't exist yet
- Websocket event emission not integrated

**Can do now (no blockers):**
- Standardized weight reader
- Utility computation
- Event dataclasses (prep for future emission)
- Frame diagnostics (prep for future emission)
- Guards and caps
- Extended tests

---

## Summary

Diffusion v2 stride-based implementation exists and works (3 tests passing, energy conserved). Core physics correct. Missing:

**Correctness additions:**
- Standardized weight reader (per-type normalization)
- Utility computation for learning

**Spec compliance additions:**
- Valence stack scoring (requires sub_entity_traversal integration)
- Event emission infrastructure (dataclasses ready, emission when broadcaster ready)
- Frame diagnostics
- Guards and caps

**Future integrations (blocked on other work):**
- Fanout strategy (awaits fanout_strategy.py)
- traversal_v2.py orchestration (awaits that file)
- Websocket event emission (awaits broadcaster integration)

**Recommendation:** Extend diffusion_runtime.py systematically, add unblocked features now, wire integrations when dependencies ready.
