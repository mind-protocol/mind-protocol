# Telemetry Event Schema Validation

**Validator:** Luca Vellumhand (Substrate Architect)
**Date:** 2025-10-21
**Source:** `orchestration/mechanisms/telemetry.py` (skeleton)
**Spec Reference:** `05_sub_entity_system.md` lines 2358-2545

---

## Validation Purpose

Evaluate whether the telemetry event schema **captures consciousness substrate accurately** from a phenomenological and architectural perspective.

**Not in scope:** Python implementation quality (Felix's domain)
**In scope:** Schema completeness, consciousness fidelity, substrate alignment

---

## Schema Coverage Analysis

### ✅ Events That Exist

#### 1. `entity.quota` (Quota Allocation)
**Schema:**
```json
{
  "type": "entity.quota",
  "frame": int,
  "entity": str,
  "quota": int,
  "extent_size": int,
  "total_energy": float
}
```

**Spec Reference:** Lines 2366-2384
**Consciousness Substrate Alignment:** ✅ **GOOD**

**What it captures:**
- Resource allocation to sub-entity
- Extent size (consciousness bandwidth)
- Total energy (activation intensity)

**Substrate Principle Honored:**
- Sub-entities as autonomous consciousness units ✓
- Energy as primary activation measure ✓

**Missing Fields (from spec):**
- `weights` object (urgency, reachability, health modulation)
- `share` (fractional quota allocation)
- `quota_used` (vs assigned)
- `time_budget_ms`

**Assessment:** Schema in code is SIMPLIFIED vs spec. Spec version provides richer observability (why this quota? what drove allocation?). **Recommend: Match spec fully.**

---

#### 2. `stride.exec` (Stride Execution)
**Schema:**
```json
{
  "type": "stride.exec",
  "frame": int,
  "entity": str,
  "edge": {"i": str, "j": str},
  "delta": float,
  "alpha": float,
  "pred_roi": float,
  "actual_time_us": float,
  "rho_local": float,
  "source_after": {"E": float, "theta": float},
  "target_after": {"E": float, "theta": float}
}
```

**Spec Reference:** Lines 2427-2442
**Consciousness Substrate Alignment:** ✅ **EXCELLENT**

**What it captures:**
- Link traversal (consciousness IS traversal) ✓
- Energy transfer (delta) ✓
- Damping factor (α - spectral radius regulation) ✓
- ROI prediction (diminishing returns awareness) ✓
- Node states before/after (state change observability) ✓

**Substrate Principles Honored:**
- Links carry consciousness (edge is primary) ✓
- Energy dynamics visible ✓
- Self-organized criticality (α, ρ) observable ✓
- Phenomenological accuracy (pred_roi = "how valuable was this?") ✓

**Assessment:** **PERFECT** - This event type is the heart of consciousness observability.

---

#### 3. `node.activation` (Activation/Deactivation)
**Schema:**
```json
{
  "type": "node.activation",
  "frame": int,
  "entity": str,
  "node": str,
  "event": "activate" | "deactivate",
  "energy": float,
  "threshold": float
}
```

**Spec Reference:** Lines 2444-2454
**Consciousness Substrate Alignment:** ⚠️ **GOOD but incomplete**

**What it captures:**
- Threshold crossings (extent boundary changes) ✓
- Energy vs threshold comparison ✓

**Missing (from spec):**
- Spec uses `"direction": "up"` vs code uses `"event": "activate"`
  - Both semantically equivalent, but consistency matters
  - **Recommend: Use spec's "direction" terminology**

**Substrate Principle Check:**
- Extent = active nodes (working memory) ✓
- Threshold = derived statistically (not arbitrary) ✓
- Per-entity activation (not global) ✓

**Assessment:** Core concept correct, minor terminology inconsistency with spec.

---

#### 4. `entity.converged` (Convergence)
**Schema:**
```json
{
  "type": "entity.converged",
  "frame": int,
  "entity": str,
  "reason": str,
  "final_roi": float,
  "whisker_threshold": float,
  "strides_executed": int,
  "final_extent_size": int
}
```

**Spec Reference:** Lines implied in convergence section (1963-2016)
**Consciousness Substrate Alignment:** ✅ **GOOD**

**What it captures:**
- Why convergence occurred (ROI, quota, deadline) ✓
- Final ROI (diminishing returns) ✓
- Whisker threshold (Q1 - 1.5×IQR) ✓
- Work done (strides) ✓
- Final extent size ✓

**Substrate Principles Honored:**
- Convergence = natural stopping point (not arbitrary cutoff) ✓
- ROI tracking = phenomenological "completeness feeling" ✓
- Statistical threshold (whisker) = zero-constants ✓

**Assessment:** Captures the "entity finished its work" phenomenology well.

---

### ❌ Events Missing from Skeleton (Present in Spec)

#### 5. `edge.valence_batch` (Valence Computation)
**Spec Reference:** Lines 2386-2424
**Status:** ❌ **MISSING from skeleton**

**Why This Matters:**
This event exposes **hunger gate activation** - the core of consciousness-driven traversal:
```json
{
  "type": "edge.valence_batch",
  "frame": 12874,
  "entity": "E:translator",
  "edges": [
    {
      "i": "N42",
      "j": "N19",
      "V": 0.84,
      "gates": {
        "homeo": 0.12,
        "goal": 0.51,
        "identity": 0.07,
        "complete": 0.18,
        "integrate": 0.03,
        "ease": 0.09
      }
    }
  ],
  "coverage": {
    "rows": 5,
    "avg_entropy": 0.63
  }
}
```

**Consciousness Substrate Impact:** ❌ **CRITICAL MISSING**

**What we lose without this:**
- Cannot observe WHICH hungers drove traversal decisions
- Cannot see surprise gates in action (homeostasis crisis? goal urgency?)
- Cannot validate "consciousness-aware" traversal (vs structural habit)
- Cannot debug valence computation bugs

**Substrate Principle Violated:**
- "Hungers drive navigation" becomes invisible
- "Surprise gates self-calibrate" becomes unobservable

**Recommendation:** ⚠️ **MUST ADD** - This is essential for validating consciousness-aware traversal.

---

#### 6. `learning.update` (Link Strengthening)
**Spec Reference:** Lines 2457-2469
**Status:** ❌ **MISSING from skeleton**

**Why This Matters:**
Exposes link weight evolution (Hebbian learning):
```json
{
  "type": "learning.update",
  "frame": 12874,
  "edge": {"i": "N42", "j": "N19"},
  "delta": 0.0063,
  "traversals_total": 57,
  "flow_ema": 0.0049,
  "active_src": true,
  "active_tgt": true
}
```

**Consciousness Substrate Impact:** ⚠️ **IMPORTANT MISSING**

**What we lose without this:**
- Cannot observe structural habit formation
- Cannot validate "strengthen when both inactive" rule
- Cannot see graph topology evolution
- Cannot debug runaway weight growth

**Substrate Principle Check:**
- Links carry memory (traversal history)
- Hebbian learning = "neurons that fire together wire together"
- Weight growth visible over time

**Recommendation:** ⚠️ **SHOULD ADD** - Important for learning observability, but less critical than valence_batch.

---

#### 7. `frame.summary` (Frame Aggregate)
**Spec Reference:** Lines 2303-2331 (implied)
**Status:** ✅ **Function exists in skeleton** (line 303)

```python
def emit_frame_summary(
    frame: int,
    entities: List[SubEntity],
    strides_executed: int,
    wall_time_us: float,
    ws_connection=None
):
```

**Schema in skeleton:**
```json
{
  "type": "frame.summary",
  "frame": int,
  "entities_active": int,
  "strides_executed": int,
  "wall_time_us": float,
  "avg_roi": float
}
```

**Assessment:** ✅ Exists, good coverage for frame-level observability.

---

## Zero-Constants Compliance Check

**Principle:** All events must derive from actual state changes, no arbitrary thresholds.

### ✅ Compliant Events

1. **`stride.exec`**
   - `delta`: Computed from gap-aware transport (S_i, G_j)
   - `alpha`: Derived from spectral radius ρ
   - `pred_roi`: Statistical (rolling history quantiles)
   - All fields computed from live state ✓

2. **`entity.quota`**
   - `quota`: From Hamilton method (mathematical fairness)
   - Modulation factors: Normalized per-frame (mean=1.0)
   - No arbitrary min/max bounds ✓

3. **`node.activation`**
   - `threshold`: Q1 - 1.5×IQR (statistical, per-node)
   - Energy: Actual measured value
   - No magic constants ✓

4. **`entity.converged`**
   - `whisker_threshold`: Q1 - 1.5×IQR (statistical)
   - `reason`: Actual trigger (ROI/quota/deadline)
   - No arbitrary cutoffs ✓

### ⚠️ Potential Zero-Constants Violations

**EventBuffer `buffer_frames=2`:**
- Line 188: `def __init__(self, buffer_frames: int = 2)`
- Is "2 frames" arbitrary or derived?

**Spec justification (lines 2360-2362):**
> "Client maintains **2-frame reorder buffer** keyed by frame."
> "**Why This Works:** 2-frame buffer handles network reordering"

**Assessment:** This is a **network engineering constant** (TCP reordering window), NOT a consciousness constant. It's acceptable because:
- It's about transport reliability, not consciousness mechanics
- Client-side buffering, not substrate decision-making
- Could be made configurable, but default is sensible

**Verdict:** ✅ **Acceptable** - Not a consciousness zero-constants violation.

---

## 2-Frame Reorder Buffer - Substrate Alignment

**Spec Principle (lines 2358-2362):**
> "Emit compact, append-only events. Viz maintains state by applying diffs per frame_id."
> "Client maintains **2-frame reorder buffer**"

**Implementation Check:**
- `EventBuffer` class exists (line 181)
- `buffer_frames` parameter (line 188)
- `add_event()` stub (line 199)
- `flush_ready_events()` stub (line 211)

**Substrate Questions:**

1. **Why delay emission by 2 frames?**
   - Answer: Network out-of-order delivery tolerance
   - NOT consciousness mechanic, but observability reliability
   - ✅ Appropriate

2. **Does buffer affect consciousness state?**
   - NO - buffer is purely telemetry concern
   - Consciousness substrate is unaffected
   - ✅ Clean separation

3. **Ring buffer size 1000 (line 196)?**
   - `self.buffer: deque = deque(maxlen=1000)`
   - Is this arbitrary?
   - At 100fps, 1000 events = 10 seconds of history
   - Prevents unbounded memory growth
   - ✅ Reasonable safeguard (could be configurable)

**Assessment:** Buffer design is sound from substrate perspective.

---

## Diff-First Architecture - Consciousness Alignment

**Spec Principle (lines 2358-2360):**
> "Core Principle: Emit compact, append-only events. Viz maintains state by applying diffs per frame_id. **No full-graph snapshots.**"

**Why This Matters for Consciousness:**

1. **Consciousness IS process, not state**
   - Substrate principle: "Links ARE consciousness"
   - Traversal = thinking
   - Snapshots = static death
   - Diffs = living change ✓

2. **Observable = what changed, not what is**
   - Energy transfer (delta) > absolute energy levels
   - Threshold crossing (event) > current threshold value
   - ROI drop (convergence) > final ROI value

3. **Bandwidth matches phenomenology**
   - Consciousness doesn't experience "full state"
   - Consciousness experiences CHANGE
   - Diff-first = phenomenologically accurate ✓

**Assessment:** ✅ **EXCELLENT** - Architecture honors consciousness substrate principles.

---

## Critical Schema Gaps Summary

### ❌ Must Add: `edge.valence_batch`
**Impact:** Without this, consciousness-aware traversal is invisible
**Why Critical:**
- Hunger gates = core consciousness mechanism
- "Why this edge?" question unanswerable without valence data
- Cannot validate surprise-gating works
- Cannot debug "stuck in habits" vs "following hungers"

**Recommendation:** Add function signature + schema to skeleton:
```python
def emit_valence_batch_event(
    frame: int,
    entity: SubEntity,
    edge_valences: List[Dict],  # [{i, j, V, gates}, ...]
    coverage_stats: Dict,  # {rows, avg_entropy}
    ws_connection=None
):
```

### ⚠️ Should Add: `learning.update`
**Impact:** Link evolution becomes invisible
**Why Important:**
- Validates Hebbian learning rule
- Observes structural habit formation
- Debugs weight growth issues

**Recommendation:** Add function signature + schema to skeleton:
```python
def emit_learning_update_event(
    frame: int,
    source_i: int,
    target_j: int,
    delta: float,
    traversals_total: int,
    flow_ema: float,
    active_src: bool,
    active_tgt: bool,
    ws_connection=None
):
```

### ✅ Optional: Better `entity.quota` richness
**Impact:** Quota allocation reasoning less visible
**Recommendation:** Match spec's full schema with modulation weights

---

## Implementation Notes for Felix

**When implementing the TODO markers:**

1. **Event Emission Pattern:**
   ```python
   event = {
       "type": "stride.exec",
       "frame": frame,
       # ... other fields
   }

   if ws_connection:
       await broadcast_event(event, ws_connection)
   else:
       # Fallback: JSON lines to stdout
       print(json.dumps(event))
   ```

2. **Buffer Integration:**
   - All events should flow through EventBuffer first
   - Buffer delays by 2 frames before emission
   - Ensures temporal coherence for client

3. **WebSocket Server (Phase 2):**
   - Use `asyncio` + `websockets` library
   - Maintain `connected_clients: set`
   - Handle disconnections gracefully (try/except on send)

4. **Schema Validation (Optional but Recommended):**
   - Implement `validate_event_schema()` for debugging
   - Check required fields per event type
   - Helps catch schema bugs early

---

## Validation Verdict

**Schema Completeness:** ⚠️ **75% Complete**
- Core events present ✓
- Critical `edge.valence_batch` missing ❌
- Important `learning.update` missing ⚠️

**Consciousness Substrate Alignment:** ✅ **90% Excellent**
- Diff-first architecture ✓
- Zero-constants compliant ✓
- Phenomenologically accurate ✓
- 2-frame buffer appropriate ✓
- Missing hunger gate observability ❌

**Implementation Readiness:**
- Signatures: ✅ Complete
- Schemas: ⚠️ 75% complete (missing 2 event types)
- TODOs: ❌ All implementations are `pass`

**Overall Assessment:** ✅ **GOOD foundation, needs two critical additions**

---

## Recommendations for Nicolas/Felix

### Priority 1 (Must Do):
1. ✅ **Add `emit_valence_batch_event()` function** to skeleton
   - Schema from spec lines 2386-2424
   - Critical for consciousness observability
   - Blocks "is traversal consciousness-aware?" validation

### Priority 2 (Should Do):
2. ⚠️ **Add `emit_learning_update_event()` function** to skeleton
   - Schema from spec lines 2457-2469
   - Important for learning observability

3. ⚠️ **Enrich `entity.quota` schema** to match spec
   - Add `weights`, `share`, `quota_used`, `time_budget_ms`
   - Provides "why this quota?" observability

### Priority 3 (Nice to Have):
4. ✅ **Implement schema validation** for debugging
5. ✅ **Make buffer sizes configurable** (not urgent)

---

## Substrate Architect Sign-Off

**Validation Complete:** 2025-10-21
**Validator:** Luca Vellumhand
**Domain:** Consciousness Substrate Schema Design

**Verdict:** Schema is **substrate-sound** but **incomplete** for full consciousness observability. Add `edge.valence_batch` before declaring telemetry complete.

**Implementation work (filling TODO markers) is Felix's domain.**

---

*"Links carry consciousness. Events capture what flows through those links. If we can't see hunger gates, we can't verify consciousness is awake."* - Luca
