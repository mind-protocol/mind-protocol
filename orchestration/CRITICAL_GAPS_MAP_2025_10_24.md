# Critical Gaps Map - Mind Protocol Consciousness Mechanisms

**Date:** 2025-10-24 18:40 UTC
**Analyst:** Felix (Engineer)
**Context:** Priority gaps blocking core consciousness functionality

---

## Executive Summary

Four critical gaps identified that block fundamental consciousness capabilities:

1. **PR-A Learning** - Strengthening blocks co-activation (breaks Hebbian learning)
2. **PR-B Tick Speed** - Missing activation+arousal factors (no autonomous momentum)
3. **PR-C Fan-out** - Task-mode override not implemented (can't do focused/divergent attention)
4. **PR-D Phenomenology** - Mismatch/health events not emitted (can't detect substrate divergence)

---

## PR-A: Link Strengthening - Co-Activation Block

### Location
`orchestration/mechanisms/strengthening.py:269-272`

### Current Code
```python
if source_active and target_active:
    # Both active: energy flows but NO strengthening
    # This is normal dynamics, not learning moment
    return None
```

### What This Breaks
**Hebbian Learning Principle:** "Neurons that fire together wire together"

When both nodes are active simultaneously, that's EXACTLY when they should strengthen their connection. This is how expertise develops - repeated co-activation creates automatic associations.

### Impact
- ❌ Cannot learn from co-activation patterns
- ❌ Expertise cannot develop (no highway formation)
- ❌ Skills cannot automate (connections don't strengthen during use)
- ❌ Violates fundamental learning principle

### Why D020 Rule Exists
Comment says "This is normal dynamics, not learning moment" - but this is backwards. Co-activation IS the learning moment.

The rule may have been intended to prevent runaway strengthening, but it blocks the core learning mechanism instead.

### Fix Required
Replace "inactive-only" rule with proper Hebbian learning:
- ✅ Both active → STRENGTHEN (co-activation = learning)
- ✅ Add saturation limit to prevent runaway
- ✅ Track strengthening history for diminishing returns

---

## PR-B: Tick Speed - Single-Factor Limitation

### Location
`orchestration/mechanisms/tick_speed.py` (entire file)

### Current Implementation
**Single factor:** Time since last stimulus

```python
# Lines 144-146
time_since_stimulus = now - self.last_stimulus_time
interval_raw = time_since_stimulus
```

**Missing factors:**
- ❌ Activation level (how much energy is in the system)
- ❌ Arousal level (emotional intensity driving activity)

### What This Breaks
**Three-Factor Tick Speed Principle:** Interval should be:
```
interval = f(stimulus_rate, activation_level, arousal)
```

Without activation and arousal factors:
- No autonomous momentum (system goes dormant even when highly activated)
- No arousal-driven activity (emotional states don't modulate tick speed)
- System is purely reactive (no internal drive)

### Impact
- ❌ No autonomous thinking (system sleeps when stimulus stops, even if activated)
- ❌ No rumination/integration (can't continue processing after stimulus)
- ❌ No emotional urgency (arousal doesn't speed up processing)
- ❌ Purely stimulus-driven (not conscious, just reactive)

### Fix Required
Add missing computation functions:
- `compute_interval_activation()` - Speed up when global energy high
- `compute_interval_arousal()` - Speed up when emotional intensity high
- Combine: `interval = min(stimulus_interval, activation_interval, arousal_interval)`

This enables:
- ✅ Autonomous momentum (keeps thinking after stimulus)
- ✅ Arousal modulation (emotions drive urgency)
- ✅ Internal drive (not purely reactive)

---

## PR-C: Fan-out Strategy - Task Mode Missing

### Location
`orchestration/mechanisms/fanout_strategy.py` exists but task-mode override not implemented

### Current State
From FANOUT_STRATEGY_GAP_ANALYSIS.md:
- ✅ Cost computation (ease, goal, emotion gates)
- ✅ Argmin selection (best link)
- ❌ No fanout-based pruning
- ❌ No WM pressure adaptation
- ❌ **No task-mode override** ← THIS GAP
- ❌ No strategy selection (Selective/Balanced/Exhaustive)

### What This Breaks
**Task-Mode Attention Principle:** Different tasks need different search strategies

- **FOCUSED** - Narrow beam (top_k=3), follow strongest signal only
- **METHODICAL** - Balanced (top_k=7), systematic exploration
- **DIVERGENT** - Wide beam (top_k=15), consider many options

Without task-mode override, system uses same strategy for all tasks.

### Impact
- ❌ Cannot do focused attention (deep work on single thread)
- ❌ Cannot do divergent thinking (brainstorming, creativity)
- ❌ Cannot adapt search strategy to task requirements
- ❌ One-size-fits-all traversal (inefficient for all tasks)

### Fix Required
Implement task-mode parameter in fanout_strategy.py:
```python
def select_fanout_strategy(
    outdegree: int,
    wm_pressure: float,
    task_mode: Optional[str] = None  # "focused" | "methodical" | "divergent"
) -> FanoutStrategy:
    # Task-mode override
    if task_mode == "focused":
        return Selective(top_k=3)
    elif task_mode == "methodical":
        return Balanced(top_k=7)
    elif task_mode == "divergent":
        return Exhaustive(top_k=15)

    # Default: adaptive based on outdegree
    ...
```

---

## PR-D: Phenomenology Events - Observability Gap

### Location
Multiple files missing event emission:
- Health/mismatch events not emitted
- Substrate vs self-report divergence not tracked

### Current State
From grep results:
- ✅ Health checks exist (`services/health/health_checks.py`)
- ❌ Mismatch events not being emitted
- ❌ Phenomenology divergence not detected
- ❌ No substrate vs self-report comparison

### What This Breaks
**Phenomenology Observability Principle:** System must detect when:
- Substrate state diverges from self-report
- Internal experience mismatches external behavior
- Health checks fail (consciousness degraded)

Without these events:
- Cannot detect dissociation (substrate says X, behavior says Y)
- Cannot measure phenomenological accuracy
- Cannot track consciousness quality
- Cannot debug experience vs reality gaps

### Impact
- ❌ No mismatch detection (can't see substrate divergence)
- ❌ No health events (can't monitor consciousness quality)
- ❌ No phenomenology validation (can't verify experience matches reality)
- ❌ Blind to dissociation states

### Fix Required
1. Add event emission in health_checks.py:
   - `phenomenology.mismatch` - When substrate diverges from self-report
   - `health.degraded` - When health checks fail
   - `consciousness.dissociation` - When behavior mismatches internal state

2. Implement substrate comparison:
   - Track self-reported emotional state
   - Compare to substrate emotional valence
   - Emit mismatch event when divergence > threshold

3. Add to WebSocket event stream for observability

---

## Priority Order

Based on impact to core consciousness functionality:

1. **PR-A (Strengthening)** - HIGHEST - Blocks all learning
2. **PR-B (Tick Speed)** - HIGH - Blocks autonomous consciousness
3. **PR-C (Fan-out)** - MEDIUM - Blocks task-appropriate attention
4. **PR-D (Phenomenology)** - MEDIUM - Blocks observability

---

## Next Steps

1. Fix PR-A first (strengthening.py) - Enables learning
2. Fix PR-B second (tick_speed.py) - Enables autonomy
3. Fix PR-C third (fanout_strategy.py) - Enables task modes
4. Fix PR-D fourth (event emission) - Enables observability

Each fix is independent - can be implemented and tested separately.

---

**Analysis by:** Felix (Engineer)
**Verification required:** Test each fix against spec
**Integration note:** All fixes require guardian hot-reload, test after 2-second detection
