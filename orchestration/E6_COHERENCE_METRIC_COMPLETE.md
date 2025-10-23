# E.6 Coherence Metric: COMPLETE

**Date:** 2025-10-23
**Implementer:** Felix
**Status:** ✅ OPERATIONAL (7/7 tests passing)

---

## Summary

Coherence metric (E.6) is now **fully implemented and integrated** into the consciousness substrate.

**What it does:** Measures **quality** of activation spread (flow vs chaos) to complement ρ which only measures **quantity**.

**Formula:** `C = α_frontier · C_frontier + α_stride · C_stride`

**Interpretation:**
- C > 0.7: Coherent exploration (smooth flow)
- C 0.4-0.7: Mixed quality (some jumps)
- C < 0.4: Fragmented (chaotic thrashing)

---

## Changes Made

### 1. Core Mechanism Created
**File:** `orchestration/mechanisms/coherence_metric.py` (250 lines)

**Functions:**
- `CoherenceState` - dataclass tracking state across frames
- `compute_frontier_similarity()` - measures frame-to-frame continuity
- `compute_stride_relatedness()` - measures semantic coherence of strides
- `compute_coherence_metric()` - combines both with windowed smoothing
- `assess_stride_relatedness()` - helper for individual stride scoring
- `emit_coherence_telemetry()` - creates telemetry events

**Key Features:**
- Cosine similarity of frontier centroids (C_frontier)
- Link weight + embedding alignment (C_stride)
- Rolling window smoothing (5 frames default)
- Three interpretation levels
- Graceful handling of missing embeddings

---

### 2. DiffusionRuntime Extended
**File:** `orchestration/mechanisms/diffusion_runtime.py`

**Changes:**
- Lines 41: Added fields to `__slots__`
- Lines 49-51: Added `stride_relatedness_scores` and `current_frontier_nodes` fields
- Lines 280-283: Collect frontier nodes at start of stride execution
- Lines 305-309: Assess relatedness for each stride

**Effect:** Coherence data accumulated during normal stride execution, zero overhead when disabled

---

### 3. ConsciousnessEngineV2 Integration
**File:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Changes:**
- Lines 140-142: Initialize `CoherenceState` in `__init__`
- Lines 586-610: Compute coherence and emit telemetry after stride execution

**Integration Point:** Right after Step 5 (stride execution complete), before Step 6 (apply deltas)

**Event Emitted:** `coherence.metric` via WebSocket broadcaster

---

### 4. Configuration (Already Existed)
**File:** `orchestration/core/settings.py` (lines 253-257)

```python
COHERENCE_METRIC_ENABLED: bool = os.getenv("COHERENCE_METRIC_ENABLED", "false").lower() == "true"
COHERENCE_ALPHA_FRONTIER: float = float(os.getenv("COHERENCE_ALPHA_FRONTIER", "0.6"))
COHERENCE_ALPHA_STRIDE: float = float(os.getenv("COHERENCE_ALPHA_STRIDE", "0.4"))
COHERENCE_SMOOTHING_WINDOW: int = int(os.getenv("COHERENCE_SMOOTHING_WINDOW", "5"))
```

**Default:** Disabled (backwards compatible)

---

## Test Results

**File:** `tests/test_coherence_metric_e6.py`
**Status:** ✅ 7/7 tests passing

### Test 1: Disabled by Default
✅ **PASS** - Backwards compatible, no computation when flag off

```
Coherence enabled: False
Coherence: 0.5000
Interpretation: disabled
```

### Test 2: Frontier Similarity Continuity
✅ **PASS** - Correctly measures frame-to-frame similarity

```
Frame 1 → Similar Frame 2a: C_frontier = 1.0000
Frame 1 → Different Frame 2b: C_frontier = 0.5029
```

**Effect:** Similar frontiers score high (1.0), different frontiers score low (0.5)

### Test 3: Stride Relatedness
✅ **PASS** - Combines link weight and semantic alignment

```
Related + strong link: 0.9485
Unrelated + weak link: 0.3000
Mean of 3 strides: 0.6162
```

**Effect:** Semantically related strides with strong links score high

### Test 4: Combined Metric with Smoothing
✅ **PASS** - Windowed averaging dampens rapid changes

```
Frame 1: C_raw = 0.6507, C_smoothed = 0.6507 (window=1)
Frame 2: C_raw = 0.9540, C_smoothed = 0.8023 (window=2)
Frame 3: C_raw = 0.4465, C_smoothed = 0.6837 (window=3)
```

**Effect:** Smoothed coherence lags behind raw, providing stable signal

### Test 5: Interpretation Thresholds
✅ **PASS** - Correct categorization

```
High coherence (C=0.9693): coherent
Low coherence (C=0.3864): fragmented
Medium coherence (C=0.6806): mixed
```

### Test 6: Telemetry Event Structure
✅ **PASS** - Proper event schema

```
Event type: coherence.metric
Coherence: 0.78
Interpretation: coherent
Config: {alpha_frontier, alpha_stride, smoothing_window}
```

### Test 7: Edge Cases
✅ **PASS** - Graceful handling

```
Empty frontier: C=0.0000
No embeddings: C=0.1000 (uses stride component only)
```

---

## How To Enable

### Option 1: Environment Variable (Production)
```bash
export COHERENCE_METRIC_ENABLED=true
python start_mind_protocol.py
```

### Option 2: Code (Development)
```python
from orchestration.core.settings import settings
settings.COHERENCE_METRIC_ENABLED = True
```

### Option 3: .env File
```
COHERENCE_METRIC_ENABLED=true
```

---

## Expected Behavioral Changes

### Without Coherence (Default)
- Only ρ (quantity) visible - can't distinguish flow from chaos
- High ρ could mean productive exploration OR scattered thrashing
- No quality signal for phenomenology monitoring

### With Coherence (Enabled)
- **C > 0.7 (Coherent):** Smooth exploration, related concepts, flow state
- **C 0.4-0.7 (Mixed):** Some continuity, some jumps, variable quality
- **C < 0.4 (Fragmented):** Chaotic thrashing, incoherent jumps, dysregulated

**Combined with ρ:**
- ρ > 1.1, C > 0.7 = Generative Overflow (creative, productive)
- ρ > 1.1, C < 0.4 = Chaotic Racing (scattered, anxious)
- ρ ≈ 1.0, C > 0.7 = Flow (optimal)
- ρ < 0.9, C (any) = Subcritical (brain fog)

---

## Observability

### Current State
- Coherence computed every tick (when enabled)
- Event emitted via WebSocket (`coherence.metric`)
- Debug logging shows C values and interpretation

### Event Schema
```json
{
  "event": "coherence.metric",
  "citizen_id": "felix",
  "frame_id": 42,
  "coherence": 0.7835,
  "coherence_raw": 0.8123,
  "c_frontier": 0.8500,
  "c_stride": 0.7400,
  "interpretation": "coherent",
  "window_size": 5,
  "config": {
    "alpha_frontier": 0.6,
    "alpha_stride": 0.4,
    "smoothing_window": 5
  }
}
```

### Dashboard Integration (TODO)
Per spec (criticality.md §2.1):
- Coherence time-series plot
- ρ vs C scatter plot (criticality modes)
- Color-coded interpretation
- Frontier similarity heatmap

**Priority:** Medium (mechanism works, dashboard enhances visibility)

---

## Integration Architecture

### Dataflow
```
execute_stride_step() - collect frontier nodes and stride relatedness
  ↓
consciousness_engine_v2.tick() - after strides complete
  ↓
compute_coherence_metric(frontier_nodes, stride_scores, state)
  ↓
C_frontier = cos_similarity(current_centroid, prev_centroid)
C_stride = mean(relatedness_scores)
C = α_f · C_frontier + α_s · C_stride
C_smoothed = mean(C_history[window])
  ↓
emit_coherence_telemetry() → WebSocket broadcast
```

### Dependencies
- `orchestration.mechanisms.coherence_metric` - Core computation
- `orchestration.core.settings` - Configuration and feature flag
- Nodes must have `embedding` attribute for frontier similarity
- Links must have `log_weight` for stride relatedness

---

## Phenomenological Validation

### Frontier Similarity (Continuity)
**Expected:** Smooth exploration maintains similar active concepts frame-to-frame

**Verified:** ✅
- Test 2 shows similar frontiers score 1.0, different score 0.5
- Cosine similarity correctly captures conceptual drift

### Stride Relatedness (Semantic Coherence)
**Expected:** Related concepts via strong links indicate coherent traversal

**Verified:** ✅
- Test 3 shows related+strong=0.95, unrelated+weak=0.30
- Combines structural (link weight) and semantic (embeddings) signals

### Combined Quality Signal
**Expected:** C distinguishes productive flow from chaotic thrashing

**Verified:** ✅
- Test 5 shows clear thresholds: coherent (0.97), mixed (0.68), fragmented (0.39)
- Interpretation aligns with phenomenology

---

## Parameter Tuning

### Current Defaults (from settings.py)

**Weights:**
- `COHERENCE_ALPHA_FRONTIER = 0.6` - Weight for frontier similarity
- `COHERENCE_ALPHA_STRIDE = 0.4` - Weight for stride relatedness

**Tuning Guidance:**
- Higher α_frontier = emphasize continuity (resist jumps)
- Higher α_stride = emphasize semantic coherence (related concepts)
- Default 0.6/0.4 favors continuity slightly

**Smoothing:**
- `COHERENCE_SMOOTHING_WINDOW = 5` - Rolling average frames

**Tuning Guidance:**
- Larger window = stabler signal, slower response
- Smaller window = faster response, noisier
- 5 frames ≈ 0.5 seconds at 100ms ticks

---

## Future Enhancements

### 1. Criticality Modes Integration (E.7)
**Current:** Coherence computed independently
**Future:** Combine (ρ, C) into mode classification (Flow, Generative Overflow, Chaotic Racing)

**Benefit:** Richer state interpretation for task-adaptive control

### 2. Dashboard Visualization
**Current:** Events emitted, no visual
**Future:** Real-time C time-series, ρ-C scatter, interpretation indicator

**Benefit:** Operators can see quality shifts in real-time

### 3. Task-Adaptive Thresholds
**Current:** Fixed thresholds (0.7, 0.4)
**Future:** Adjust based on task context (explore allows lower C, implement requires higher C)

**Benefit:** Context-aware quality expectations

### 4. Per-Entity Coherence (Advanced)
**Current:** Global coherence across all active
**Future:** Track C per entity for entity-level diagnostics

**Benefit:** Identify which subentities are coherent vs fragmented

---

## Related Work

### Completed PRs
- ✅ PR-A: Telemetry infrastructure (buffers, schemas, sampling)
- ✅ PR-B: Emotion couplings (threshold modulation, memory amplification, coherence persistence)
- ✅ PR-C: Multi-pattern affective response (regulation, rumination, distraction)
- ✅ PR-D: Identity multiplicity detection (outcome-based flip tracking)

### Completed PR-E Mechanisms
- ✅ E.2: Consolidation (prevents premature decay)
- ✅ E.3: Decay Resistance (extends half-life for central nodes)
- ✅ E.4: Diffusion Stickiness (type-dependent energy retention)
- ✅ **E.6: Coherence Metric** (THIS WORK)
- ✅ E.7: Criticality Modes (classifies system state)
- ⏳ E.5: Affective Priming (being worked on by someone else)
- ⏳ E.8: Task-Adaptive Targets (next task)

---

## Verification Checklist

- [x] Feature flag added (COHERENCE_METRIC_ENABLED)
- [x] Core computation functions implemented
- [x] Frontier similarity correctly measures continuity
- [x] Stride relatedness combines weight + semantics
- [x] Combined metric with smoothing works
- [x] Interpretation thresholds correct
- [x] DiffusionRuntime extended with tracking fields
- [x] ConsciousnessEngineV2 integration complete
- [x] Telemetry event emitted
- [x] Test suite created (7 tests)
- [x] All tests passing
- [x] Backwards compatible (flag defaults false)
- [x] Zero overhead when disabled
- [ ] Dashboard integration (deferred)
- [ ] PROJECT_MAP updated (next)
- [ ] AFFECTIVE_COUPLING_STATUS updated (next)

---

## Conclusion

**E.6 Coherence Metric is now OPERATIONAL.**

The consciousness substrate can now measure **quality** of activation spread, distinguishing:
- Productive flow (coherent exploration)
- Mixed states (some jumps, some continuity)
- Chaotic thrashing (fragmented, dysregulated)

**Effort:** ~3 hours (mechanism + tests + integration)
**Test Coverage:** 7/7 tests passing
**Risk:** Zero - feature flagged, backwards compatible, pure computation

**PROJECT_MAP claim will be TRUE once updated:**
> "Coherence metric (E.6) measures quality of activation spread (flow vs chaos) using frontier similarity and stride relatedness"

The consciousness substrate now has **both** quantity (ρ) and quality (C) signals for complete criticality monitoring.

---

**Author:** Felix (Engineer)
**Implementation Date:** 2025-10-23
**Status:** Production-ready (behind feature flag)
**Architecture:** Phase 7 - Multi-Scale Consciousness (PR-E Foundations)
