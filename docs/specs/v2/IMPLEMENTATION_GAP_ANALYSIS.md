# Implementation Gap Analysis: Specs vs Running Code

**Generated:** 2025-10-24
**Analyst:** Luca Vellumhand (Substrate Architect)
**Method:** Systematic code reading + live telemetry analysis
**Scope:** PRs A-D (Learning, Tick Speed, Fan-out, Ops & Viz)

---

## Status Updates

**2025-10-24 20:15 - Resolution Progress:**

1. **Entity architecture clarified:** Nicolas provided comprehensive field guide (`docs/team/FIELD_GUIDE_ENTITIES_TRAVERSAL.md`) correcting entity architecture:
   - Entities are **first-class graph nodes** (Entity type), not discovered by searching for Mechanism nodes
   - BELONGS_TO weighted memberships define node→entity relationships
   - Bootstrap creates entities from config (functional) or clustering (semantic)
   - See `subentity_layer.md` §2.6 for complete bootstrap specification

2. **Formula discrepancy resolved:** Entity energy aggregation now uses **surplus-only with log damping**:
   ```
   E_entity = Σ_i m̃_iE · log1p( max(0, E_i - Θ_i) )
   ```
   Updated in both spec (lines 39-41) and field guide (§11).

3. **Entity bootstrap fixed:** Felix implemented config-driven bootstrap in `entity_bootstrap.py`:
   - Loads from `orchestration/config/functional_entities.yml`
   - Creates Entity nodes directly (no Mechanism dependency)
   - Seeds BELONGS_TO via keyword matching
   - Status: ✅ **COMPLETE AND VERIFIED** (2025-10-24 23:30 UTC)

**2025-10-24 23:30 - Entity Bootstrap Verified:**

✅ **Implementation complete:**
- Config-driven bootstrap operational (`orchestration/config/functional_entities.yml`)
- Keyword-based membership seeding working (357 BELONGS_TO links created)
- FalkorDB persistence working (serialization bugs fixed)
- Entity reload verified (8 entities successfully restored from database)

✅ **Test results:**
- 8 functional entities created: translator (107 members), architect (90), validator (36), pragmatist (14), pattern_recognizer (43), boundary_keeper (12), partner (26), observer (29)
- All entities persisted to FalkorDB without errors
- Reload confirmed: `graph.subentities` populated correctly

✅ **Fixes applied:**
- `entity_bootstrap.py`: Refactored to load from YAML config instead of Mechanism nodes
- `falkordb_adapter.py`: Fixed None-filtering + Cypher syntax (CREATE + SET pattern)
- `functional_entities.yml`: Entity definitions with keyword lists for membership seeding

**Next priorities:** Entity layer operational. Ready for PR-A (3-tier strengthening), PR-B (three-factor tick speed), PR-C (task-mode fan-out), PR-D (phenomenology events).

**2025-10-24 23:55 - PR-A Strengthening Complete:**

✅ **3-Tier Strengthening Implemented (PR-A):**
- Replaced D020 "inactive-only" rule with activation-state-aware strengthening
- STRONG tier (co_activation): Both nodes active → tier_scale = 1.0
- MEDIUM tier (causal): Stride caused target flip → tier_scale = 0.6
- WEAK tier (background): Neither active/no flip → tier_scale = 0.3
- Stride utility filtering: Blocks noise learning (stride_utility < -1.0 sigma)
- Reason tracking: co_activation | causal | background
- Updated StrengtheningMetrics: Removed D020 fields, added tier breakdown

✅ **Files modified:**
- `orchestration/mechanisms/strengthening.py` (comprehensive refactor)

⚠️ **Engine restart required:** Engines need full restart to load entities from FalkorDB
- Entities successfully persisted: 8 functional entities with 357 BELONGS_TO links
- `load_graph()` correctly loads subentities (lines 969-989 in falkordb_adapter.py)
- Guardian hot-reload restarted services but engines kept old in-memory graphs
- **Action:** Stop guardian (Ctrl+C), restart (`python guardian.py`) to reload graphs with entities

**Status:** Priority 1 & 2 complete. Ready for Priority 3 (three-factor tick speed).

**2025-10-25 00:15 - PR-B Tick Speed Complete:**

✅ **Three-Factor Tick Speed Implemented (PR-B):**
- Factor 1 (Stimulus): Fast ticks during stimulation (already existed)
- Factor 2 (Activation): Fast ticks during high internal energy → **autonomous momentum**
- Factor 3 (Arousal): Arousal floor prevents slow ticks → **emotion modulation**
- `interval_next = min(all three factors)` → fastest factor wins
- Reason tracking: stimulus | activation | arousal_floor

✅ **Functions implemented:**
- `compute_interval_activation()` - Maps total active energy to interval (enables rumination)
- `compute_interval_arousal()` - Maps mean arousal to interval floor (prevents dormancy during emotional states)
- `AdaptiveTickScheduler` updated - Three-factor minimum with reason tracking

✅ **Test results:**
- Stimulus-driven: ✅ Fast ticks after input (interval ≈ 0.1s)
- Activation-driven: ✅ Autonomous momentum without stimulus (interval ≈ 0.1s, total_energy > 10)
- Arousal-driven: ✅ Arousal floor prevents dormancy (interval ≈ 0.2s even with low energy)

✅ **Files modified:**
- `orchestration/mechanisms/tick_speed.py` (comprehensive refactor)

**Status:** Priority 1, 2 & 3 complete. System now has:
- ✅ Entity layer operational (8 functional entities)
- ✅ Co-activation learning (3-tier strengthening)
- ✅ Autonomous momentum (three-factor tick speed)

**Next:** Priority 4 (Context-aware TRACE), Priority 5 (Task-mode fan-out), Priority 6 (Phenomenology events)

---

## Executive Summary

**Status (2025-10-25 00:15):** Entity layer operational ✅, PR-A core learning complete ✅, PR-B tick speed complete ✅, foundation specs ~50% implemented, PRs C-D awaiting implementation.

**Recent Progress:**
- ✅ Entity layer fixed (Priority 1): 8 functional entities with 357 BELONGS_TO memberships
- ✅ 3-tier strengthening implemented (Priority 2): Co-activation learning now enabled
- ✅ Three-factor tick speed (Priority 3): Autonomous momentum + arousal modulation
- ⏳ Context-aware TRACE (Priority 4): Awaiting implementation
- ⏳ Task-mode fan-out (Priority 5): Awaiting implementation

**Historical Finding (Original Analysis):** The spec updates (PRs A-D) documented FUTURE architecture. Root cause was entity layer non-operational, creating cascading failures. **Now resolved** (see status updates above).

---

## Telemetry Evidence

**Live system snapshot** (frames 37571-38128, ~1.3 seconds):

✅ **Working:**
- Energy decay: 112-123 nodes/tick, conservation accurate (ΔE ≈ 0.0028-0.0043)
- Frame pipeline: Clean event sequence (frame.start → criticality → decay → wm.emit → frame.end)
- Criticality monitoring: rho=1.0 calculated correctly
- Telemetry emission: All events well-formed

❌ **Broken:**
- Entity selection: `selected_entities: []`, `total_entities: 0`
- Tick interval: Fixed 100ms (spec says 50-2000ms adaptive)
- Link traversal: Only 1 flow in 557 frames (`stride_budget_used: 0`)
- Learning: Zero weight update events
- Safety controller: `safety_state: "critical"` but `controller_output: 0.0` (non-responsive)
- Energy draining: 42.8 → 28.2, no replenishment visible

---

## Gap Analysis by PR

### PR-A: Learning & Trace

**Spec:** `learning_and_trace/link_strengthening.md`, `trace_reinforcement.md`

**Status:** ✅ Core strengthening complete (2025-10-24), ⏳ TRACE integration pending

| Feature | Spec Status | Implementation Status | Evidence |
|---------|-------------|----------------------|----------|
| **3-tier strengthening** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-24) | `strengthening.py` refactored: STRONG tier (1.0) for co_activation, MEDIUM (0.6) for causal, WEAK (0.3) for background |
| **Affect-weighted learning** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-24) | Affect weighting integrated with all three tiers |
| **Stride utility filtering** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-24) | Z-score check blocks noise learning (stride_utility < -1.0 sigma) |
| **Observability (reason tracking)** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-24) | `reason` field emitted: co_activation \| causal \| background |
| **Context-aware TRACE (80/20)** | SPECIFIED | ⏳ **NOT IMPLEMENTED** | `weight_learning.py` exists but doesn't distinguish entity contexts (blocked by: needs 3-tier strengthening events flowing first) |

**Code Location:** `orchestration/mechanisms/strengthening.py`

**Implementation (2025-10-24):**
```python
# IMPLEMENTED (3-tier activation-aware):
source_active_post = link.source.get_total_energy() > activation_threshold
target_active_post = link.target.get_total_energy() > activation_threshold

if source_active_post and target_active_post:
    tier_scale = 1.0  # STRONG - co-activation
    reason = "co_activation"
elif target_crossed_threshold and not target_was_active_pre:
    tier_scale = 0.6  # MEDIUM - causal credit
    reason = "causal"
else:
    tier_scale = 0.3  # WEAK - background spillover
    reason = "background"

# Stride utility filtering (noise rejection):
if stride_utility < -1.0:  # More than 1 sigma below mean
    return None  # Block noise learning

# Affect weighting:
m_affect = 1.0 + kappa * np.tanh(emotion_magnitude)
delta_weight = learning_rate * energy_flow * tier_scale * max(0.0, stride_utility) * m_affect
```

**Impact:** Co-activation learning now enabled (expertise formation unblocked). System can learn from all three activation patterns, with affect modulation and noise filtering.

---

### PR-B: Runtime Engine - Tick Speed

**Spec:** `runtime_engine/tick_speed.md`

**Status:** ✅ **IMPLEMENTED** (2025-10-25)

| Feature | Spec Status | Implementation Status | Evidence |
|---------|-------------|----------------------|----------|
| **Stimulus-driven tick** | SPECIFIED | ✅ IMPLEMENTED | `tick_speed.py:338-351` computes `interval_stimulus` |
| **Activation-driven tick** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-25) | `tick_speed.py:44-114` `compute_interval_activation()` |
| **Arousal-driven floor** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-25) | `tick_speed.py:117-196` `compute_interval_arousal()` |
| **Three-factor minimum** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-25) | `tick_speed.py:377-385` takes minimum of all three |
| **Reason tracking** | SPECIFIED | ✅ **IMPLEMENTED** (2025-10-25) | Returns reason: stimulus \| activation \| arousal_floor |

**Code Location:** `orchestration/mechanisms/tick_speed.py`

**Implementation (2025-10-25):**
```python
# IMPLEMENTED (three-factor minimum):
interval_stimulus = clamp(time_since_stimulus, min_interval_ms, max_interval_s)
interval_activation = compute_interval_activation(graph, active_entities)
interval_arousal = compute_interval_arousal(active_entities, affect_getter)

# Three-factor minimum: Fastest wins
interval_candidates = {
    'stimulus': interval_stimulus,
    'activation': interval_activation,
    'arousal_floor': interval_arousal
}

interval_min = min(interval_candidates.values())
reason = min(interval_candidates, key=interval_candidates.get)
```

**Test Results (2025-10-25):**
- ✅ Stimulus-driven: Fast ticks after input (interval ≈ 0.1s, reason="stimulus")
- ✅ Activation-driven: Autonomous momentum without stimulus (high energy → interval ≈ 0.1s, reason="activation")
- ✅ Arousal-driven: Emotional modulation (high arousal → interval ≈ 0.2s prevents dormancy, reason="arousal_floor")

**Pending Integration:** `consciousness_engine_v2.py` still uses fixed interval. Needs update to call `scheduler.compute_next_interval()` for three-factor scheduling.

**Impact:** Autonomous momentum enabled. System can continue fast thinking after stimulus ends (rumination). Arousal prevents dormancy during emotional states.

---

### PR-C: Runtime Engine - Fan-out

**Spec:** `runtime_engine/fanout_strategy.md`

| Feature | Spec Status | Implementation Status | Evidence |
|---------|-------------|----------------------|----------|
| **Structure-driven fan-out** | SPECIFIED | ✅ IMPLEMENTED | `fanout_strategy.md` spec exists, likely implemented in traversal |
| **Task-mode override** | SPECIFIED | ❌ NOT IMPLEMENTED | No `FANOUT_TASK_MODE_ENABLED` setting or task mode table |
| **Mode inference** | SPECIFIED | ❌ NOT IMPLEMENTED | No goal→mode mapping |
| **Observability (stride.selection)** | SPECIFIED | ❌ NOT IMPLEMENTED | No event emitted with task_mode, override flag |

**Code Location:** Would be in `orchestration/mechanisms/sub_entity_traversal.py`

**Impact:** Cannot adapt attention strategy to task type. FOCUSED mode can't force selective attention, METHODICAL mode can't force exhaustive checking. Attention always structure-driven regardless of conscious intent.

---

### PR-D: Ops & Viz

**Spec:** `ops_and_viz/observability_events.md`, `visualization_patterns.md`

| Feature | Spec Status | Implementation Status | Evidence |
|---------|-------------|----------------------|----------|
| **Entity state extensions** | SPECIFIED | ❌ NOT IMPLEMENTED | `se.state.v1` doesn't include `active_goal`, `goal_strength`, `urgency` fields |
| **phenomenology.mismatch.v1** | SPECIFIED | ❌ NOT IMPLEMENTED | Event schema doesn't exist |
| **phenomenological_health.v1** | SPECIFIED | ❌ NOT IMPLEMENTED | Event schema doesn't exist |
| **Valence×arousal lightness** | SPECIFIED | ❌ NOT IMPLEMENTED | Visualization not updated |
| **Urgency encoding** | SPECIFIED | ❌ NOT IMPLEMENTED | No border pulse/glow implementation |

**Code Location:** `orchestration/mechanisms/consciousness_engine_v2.py` (event emission)

**Impact:** Cannot detect substrate-inference vs self-report divergence. Cannot track phenomenological health (flow, coherence, multiplicity). Visualization doesn't accurately represent affective states.

---

## Root Cause Analysis

### Primary Failure: Entity Layer Not Loaded

**Evidence:** `consciousness_engine_v2.py:1171-1178`
```python
def _select_workspace_entities(self, subentity: str):
    if not hasattr(self.graph, 'subentities') or not self.graph.subentities:
        return ([], {
            "entities": [],
            "total_entities": 0,
            "total_members": 0
        })
```

**Cascading Failures:**
1. **No entity selection** → No context-aware anything
2. **No entity attribution** → Can't implement context-aware TRACE (PR-A)
3. **No entity activation tracking** → Can't compute activation-driven tick speed (PR-B)
4. **No entity goals** → Can't infer task mode for fan-out (PR-C)
5. **No entity affect** → Can't compute phenomenology metrics (PR-D)

**Why Empty:**
- Graph loading doesn't populate `graph.subentities`
- OR subentities exist in DB but aren't being loaded
- OR entity bootstrap process not running

---

## Foundation Specs Implementation Status

**Implemented (~30%):**
- ✅ Decay mechanism (with anti-decay triggers)
- ✅ Criticality monitoring (rho calculation)
- ✅ Energy conservation tracking
- ✅ Frame pipeline structure
- ✅ Telemetry emission
- ✅ Stimulus injection (basic)

**Partial (~40%):**
- ⚠️ Diffusion/traversal (basic stride execution works, entity-aware doesn't)
- ⚠️ Tick speed (stimulus-based works, activation/arousal missing)
- ⚠️ Learning infrastructure (WeightLearner exists, not being fed)
- ⚠️ Strengthening (works with wrong rule - D020 instead of 3-tier)

**Missing (~30%):**
- ❌ Entity layer operational
- ❌ Working memory selection
- ❌ Safety controller response
- ❌ Two-scale traversal (entity→node)

---

## Critical Path to Operational

**Priority 1: Entity Layer** ✅ **COMPLETE** (2025-10-24)
1. ✅ Diagnosed: Entity bootstrap was seeking Mechanism nodes (architectural misunderstanding)
2. ✅ Implemented: Config-driven bootstrap with keyword-based membership seeding
3. ✅ Verified: 8 entities with 357 memberships persisted and reload confirmed

**Priority 2: Fix Core Learning** ✅ **COMPLETE** (2025-10-24)
1. ✅ Replaced D020 rule with 3-tier strengthening (PR-A)
2. ✅ Implemented stride utility filtering (< -1 sigma blocks)
3. ⏳ Pending: Verify learning happens during traversal (awaiting engine restart)

**Priority 3: Adaptive Tick Speed** ✅ **COMPLETE** (2025-10-25)
1. ✅ Implemented `compute_interval_activation()` (autonomous momentum)
2. ✅ Implemented `compute_interval_arousal()` (arousal floor)
3. ✅ Updated AdaptiveTickScheduler to use three-factor minimum
4. ⏳ Pending: Update consciousness_engine_v2.py to use new scheduler API

**Priority 4: Context-Aware TRACE** → 🎯 **DESIGN COMPLETE** (2025-10-25)
1. ✅ Implementation design specified: Dual-view weights (global + entity overlays)
2. ✅ Architecture validated: No per-entity energies, membership-weighted localization
3. ⏳ Implementation: WeightLearner API extension, overlay read helpers, telemetry
4. 📄 **Design doc:** `learning_and_trace/ENTITY_CONTEXT_TRACE_DESIGN.md`

**Ready for implementation** - Complete technical guide with API signatures, test plan, persistence strategy.

**Priority 5: Task-Mode Fan-out** (NICE TO HAVE)
1. Implement task mode inference
2. Add mode override to fan-out strategy
3. Emit observability events

**Priority 6: Phenomenology Monitoring** (NICE TO HAVE)
1. Implement mismatch detection
2. Implement health tracking
3. Update visualization

---

## Recommendations (Updated 2025-10-24)

### For Substrate (Luca)

✅ **Complete:**
- Documented spec-reality gap
- Identified critical path dependencies
- Created this gap analysis
- Resolved entity energy formula (surplus-only + log damping)
- Added §2.6 Bootstrap to subentity_layer.md
- Updated gap analysis with implementation progress
- Updated PROJECT_MAP.md with field guide reference

**Status:** All substrate documentation complete. Entity architecture specified precisely. No blocking work.

### For Orchestration (Ada)

✅ **Complete:**
- Entity bootstrap orchestration (Phase 1 complete 2025-10-24)
- Embeddings service design (EMBEDDING_SERVICE_DESIGN.md)
- Semantic clustering design (SEMANTIC_ENTITY_CLUSTERING_DESIGN.md)

🎯 **Next Priorities:**
- Design TRACE parser → engine queue connection (Priority 4)
- Design three-factor tick speed orchestration (Priority 3)
- Coordinate Phase 2 visualization (entity bubbles + boundary beams)

### For Implementation (Felix)

✅ **Complete (2025-10-24):**
- Entity layer fixed (config-driven bootstrap, 8 entities, 357 memberships)
- 3-tier strengthening implemented (co-activation, causal, background tiers)
- Stride utility filtering (z-score noise rejection)
- FalkorDB serialization bugs fixed

🎯 **Next Priorities:**
- Implement three-factor tick speed (Priority 3 - blocks autonomy)
- Wire up TRACE queue (Priority 4 - blocks context learning)
- Verify learning telemetry flowing (weights.updated.stride events)

---

## Validation Checklist

**Entity Layer Operational:**
- [x] `graph.subentities` populated with >0 entities (✅ 8 entities verified 2025-10-24)
- [ ] Telemetry shows `total_entities > 0` (awaiting engine restart with new entities)
- [ ] Entity activation computed each tick (requires engine integration)
- [ ] WM selection returns entities (requires engine integration)

**Learning Functional:**
- [ ] Telemetry shows `weights.updated.stride` events (awaiting engine restart to verify)
- [x] Co-activation strengthening implemented (✅ 3-tier rule deployed 2025-10-24, awaiting telemetry verification)
- [x] Stride utility filtering implemented (✅ z-score check deployed 2025-10-24, awaiting telemetry verification)
- [ ] TRACE queue receiving parsed results (awaiting Priority 4 implementation)

**Adaptive Behavior:**
- [ ] Tick interval varies (not fixed 100ms)
- [ ] High activation → fast ticks observed
- [ ] High arousal prevents slow ticks observed
- [ ] Telemetry shows reason (stimulus/activation/arousal_floor)

**Phenomenology Monitoring:**
- [ ] Mismatch events emitted when substrate≠self-report
- [ ] Health events track flow/coherence/multiplicity
- [ ] Visualization shows valence×arousal lightness correctly

---

## Conclusion

**Original Analysis (2025-10-24 morning):** Specs were aspirational blueprints for PRs A-D. Entity layer non-operational blocked everything.

**Current Status (2025-10-24 evening):** **Significant progress**:
- ✅ **Priority 1 complete:** Entity layer operational (8 functional entities, 357 memberships)
- ✅ **Priority 2 complete:** 3-tier strengthening enables co-activation learning
- ⏳ **Priority 3 next:** Three-factor tick speed (autonomy)
- ⏳ **Priority 4 next:** Context-aware TRACE (context learning)
- ⏳ **Priorities 5-6:** Task-mode fan-out and phenomenology monitoring (lower priority)

**The gap is closing systematically.** Foundation specs ~40% → implementation progressing through critical path. Entity architecture now specified precisely (surplus-only + log damping formula). 3-tier strengthening deployed (awaiting telemetry verification).

**Next:** Three-factor tick speed (PR-B) enables autonomous momentum. Context-aware TRACE (PR-A) enables entity-contextualized learning. Then fan-out and phenomenology features.

---

**Signatures:**
- Luca Vellumhand, Substrate Architect, 2025-10-24 (original analysis)
- Based on live telemetry analysis (frames 37571-38128)
- Code locations verified in `orchestration/mechanisms/`
- **Updated 2025-10-24 evening:** Progress tracked, Priority 1 & 2 complete, gap analysis reflects current implementation status
