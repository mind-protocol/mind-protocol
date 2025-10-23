# Consciousness Tripwire Integration Specification

**Author:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-23
**Status:** Ready for Implementation
**Prerequisite:** Operational Resilience Phase 1 (Victor - COMPLETE)

---

## Purpose

Instrument consciousness mechanisms with fail-loud tripwires that trigger Safe Mode when physics/performance invariants are violated.

**Why this matters:** Silent failures in consciousness substrate create "nothing works" mysteries. Tripwires detect violations immediately and degrade to safe configuration for diagnosis.

---

## Integration Points

### 1. Conservation Tripwire (CRITICAL - Priority 1)

**Location:** `orchestration/mechanisms/consciousness_engine_v2.py`
**When:** After diffusion step (Phase 2), before applying deltas
**Check:** Energy conservation: ΣΔE ≈ 0 within ε

**Threshold:**
- ε = 0.001 (±0.1% of zero)
- **IMMEDIATE trigger** - Single violation enters Safe Mode

**Implementation:**
```python
# In tick() method, after diffusion step

from orchestration.services.health.safe_mode import (
    SafeModeController, TripwireType
)

# Singleton instance
safe_mode = SafeModeController()

# After execute_stride_step() completes
# Phase 2: Within-entity strides
delta_E_sum = self.diffusion_rt.compute_total_delta()  # Σ all staged ΔE

# Conservation check
conservation_epsilon = settings.TRIPWIRE_CONSERVATION_EPSILON
if abs(delta_E_sum) > conservation_epsilon:
    safe_mode.record_violation(
        tripwire_type=TripwireType.CONSERVATION,
        value=abs(delta_E_sum),
        threshold=conservation_epsilon,
        message=f"Energy not conserved: ΣΔE={delta_E_sum:.6f} (ε={conservation_epsilon})"
    )
else:
    safe_mode.record_compliance(TripwireType.CONSERVATION)

# Apply deltas (always, even if violation - continue running in Safe Mode)
self.diffusion_rt.apply_deltas()
```

**Why after diffusion, before apply:**
- Staged deltas haven't been committed yet
- Can verify ΣΔE without side effects
- Still apply deltas (Safe Mode continues running, just degraded)

**Required Addition to diffusion_runtime.py:**
```python
def compute_total_delta(self) -> float:
    """
    Compute ΣΔE across all staged deltas.

    Returns:
        Sum of all energy changes (should be ≈0 for conservation)
    """
    return sum(self.delta_E.values())
```

---

### 2. Criticality Tripwire (Priority 2)

**Location:** `orchestration/mechanisms/criticality.py`
**When:** After ρ computation in adjust_for_criticality()
**Check:** ρ ∈ [0.7, 1.3] (stable edge-of-chaos)

**Threshold:**
- Upper bound: 1.3 (chaotic)
- Lower bound: 0.7 (dying)
- Consecutive frames: 10 violations

**Implementation:**
```python
# In adjust_for_criticality() method, after ρ computation

from orchestration.services.health.safe_mode import (
    SafeModeController, TripwireType
)

safe_mode = SafeModeController()

# After: rho = estimate_branching_ratio(graph, active_nodes)

# Criticality bounds check
upper_bound = settings.TRIPWIRE_CRITICALITY_UPPER  # 1.3
lower_bound = settings.TRIPWIRE_CRITICALITY_LOWER  # 0.7

if rho > upper_bound:
    safe_mode.record_violation(
        tripwire_type=TripwireType.CRITICALITY,
        value=rho,
        threshold=upper_bound,
        message=f"Criticality too high (chaotic): ρ={rho:.3f} > {upper_bound}"
    )
elif rho < lower_bound:
    safe_mode.record_violation(
        tripwire_type=TripwireType.CRITICALITY,
        value=rho,
        threshold=lower_bound,
        message=f"Criticality too low (dying): ρ={rho:.3f} < {lower_bound}"
    )
else:
    safe_mode.record_compliance(TripwireType.CRITICALITY)

# Continue with PID control (adjust delta_decay, delta_alpha)
# Safe Mode overrides will take effect if triggered
```

**Why after ρ computation:**
- ρ is the health metric (branching ratio)
- Need to validate before PID control adjustments
- Safe Mode overrides will cap α and dt if triggered

---

### 3. Frontier Tripwire (Priority 3)

**Location:** `orchestration/mechanisms/diffusion_runtime.py`
**When:** After frontier expansion in execute_stride_step()
**Check:** Frontier size < 30% of total graph

**Threshold:**
- Max frontier: 30% of total nodes
- Consecutive frames: 20 violations

**Implementation:**
```python
# In execute_stride_step(), after frontier expansion

from orchestration.services.health.safe_mode import (
    SafeModeController, TripwireType
)

safe_mode = SafeModeController()

# After active frontier determination
# active = {n for n in graph.nodes if n.E >= threshold}
# frontier = active + 1-hop shadow

total_nodes = len(graph.nodes)
frontier_size = len(rt.active)  # Active nodes + shadow
frontier_pct = frontier_size / total_nodes if total_nodes > 0 else 0.0

max_frontier_pct = settings.TRIPWIRE_FRONTIER_PCT  # 0.3

if frontier_pct > max_frontier_pct:
    safe_mode.record_violation(
        tripwire_type=TripwireType.FRONTIER,
        value=frontier_pct,
        threshold=max_frontier_pct,
        message=f"Frontier bloat: {frontier_size}/{total_nodes} nodes ({frontier_pct:.1%} > {max_frontier_pct:.0%})"
    )
else:
    safe_mode.record_compliance(TripwireType.FRONTIER)

# Continue with diffusion (Safe Mode will reduce activation if triggered)
```

**Why after frontier expansion:**
- Frontier size determines O(active) complexity
- Bloated frontier → O(N) behavior (performance degradation)
- Safe Mode reduces activation rate to shrink frontier

---

### 4. Observability Tripwire (Priority 4)

**Location:** `orchestration/mechanisms/consciousness_engine_v2.py`
**When:** After tick completion, before returning
**Check:** frame.end event emitted successfully

**Threshold:**
- Consecutive missing events: 5 frames

**Implementation:**
```python
# In tick() method, after all phases complete

from orchestration.services.health.safe_mode import (
    SafeModeController, TripwireType
)

safe_mode = SafeModeController()

# After all tick phases (including emit_frame_end())
# Check if frame.end event was emitted

try:
    # Attempt to emit frame.end event
    self.emit_frame_end(frame_metrics)

    # Event emitted successfully
    safe_mode.record_compliance(TripwireType.OBSERVABILITY)

except Exception as e:
    # Event emission failed
    safe_mode.record_violation(
        tripwire_type=TripwireType.OBSERVABILITY,
        value=1.0,  # Binary: failed=1, success=0
        threshold=0.0,
        message=f"Failed to emit frame.end event: {str(e)}"
    )

    # Log but don't crash tick
    logger.error(f"[Observability] frame.end emission failed: {e}")

# Return metrics regardless of observability failure
return frame_metrics
```

**Why at tick end:**
- frame.end is the heartbeat signal
- Missing events → monitoring blind
- Safe Mode increases sampling to 100% for diagnosis

---

## Error Handling

**All tripwire checks must be non-blocking:**

```python
try:
    # Tripwire check
    if abs(delta_E_sum) > epsilon:
        safe_mode.record_violation(...)
    else:
        safe_mode.record_compliance(...)
except Exception as e:
    logger.error(f"[Tripwire] Failed to check conservation: {e}")
    # Continue execution - don't let tripwire crash consciousness
```

**Principle:** Tripwires are diagnostics, not control flow. If a tripwire check fails, log the error and continue. The consciousness loop must never crash due to tripwire failures.

---

## Testing Strategy

### Unit Tests (test_tripwire_integration.py)

**Conservation Tests:**
1. ΣΔE = 0 → record_compliance called
2. ΣΔE = 0.002 (>ε) → record_violation called
3. Single violation → Safe Mode entered

**Criticality Tests:**
1. ρ = 1.0 → record_compliance
2. ρ = 1.5 (>1.3) → record_violation
3. ρ = 0.5 (<0.7) → record_violation
4. 10 consecutive violations → Safe Mode entered

**Frontier Tests:**
1. 10% frontier → record_compliance
2. 50% frontier (>30%) → record_violation
3. 20 consecutive violations → Safe Mode entered

**Observability Tests:**
1. Event emitted → record_compliance
2. Event emission exception → record_violation
3. 5 consecutive failures → Safe Mode entered

### Integration Tests (test_safe_mode_full_stack.py)

**End-to-end scenarios:**
1. Run consciousness tick with deliberate conservation violation
2. Verify Safe Mode entered
3. Verify overrides applied (α reduced, dt capped, affective disabled)
4. Verify auto-exit after 60s stable

---

## Safe Mode Override Effects

**When any tripwire triggers Safe Mode:**

**Immediate Configuration Changes:**
```python
ALPHA_TICK_MULTIPLIER = 0.3  # 70% reduction in diffusion
DT_CAP = 1.0  # Cap time delta at 1s
TWO_SCALE_TOPK_ENTITIES = 1  # Single entity only
FANOUT_STRATEGY = "selective"  # Top-1 only

# All affective couplings disabled
AFFECTIVE_THRESHOLD_ENABLED = False
AFFECTIVE_MEMORY_ENABLED = False
AFFECTIVE_RESPONSE_V2 = False
IDENTITY_MULTIPLICITY_ENABLED = False
CONSOLIDATION_ENABLED = False
DECAY_RESISTANCE_ENABLED = False
DIFFUSION_STICKINESS_ENABLED = False

# Full telemetry for diagnosis
TELEMETRY_SAMPLE_RATE = 1.0
```

**Effect on Consciousness:**
- Reduced activation spread (70% slower diffusion)
- Single entity focus (no multi-entity competition)
- Minimal branching (top-1 fanout)
- All advanced features disabled
- Full event visibility (100% sampling)

**Result:** Minimal viable consciousness - slow, stable, fully observable.

---

## Success Criteria

**Phase 1 (Implementation):**
- ✅ Conservation tripwire integrated (consciousness_engine_v2.py)
- ✅ Criticality tripwire integrated (criticality.py)
- ✅ Frontier tripwire integrated (diffusion_runtime.py)
- ✅ Observability tripwire integrated (consciousness_engine_v2.py)
- ✅ Unit tests passing (12+ tests)
- ✅ Integration tests passing (4+ scenarios)

**Phase 2 (Validation):**
- ✅ Deliberate conservation violation → Safe Mode entered
- ✅ Safe Mode overrides applied correctly
- ✅ Auto-exit after 60s stable
- ✅ Consciousness continues running in Safe Mode (degraded but stable)

**Phase 3 (Production):**
- ✅ Guardian supervision loop integrated (calls health checks)
- ✅ Dashboard shows Safe Mode status
- ✅ WebSocket emits safe_mode.enter/exit events
- ✅ Runbook updated with Safe Mode troubleshooting

---

## Files to Modify

**Consciousness Mechanisms:**
1. `orchestration/mechanisms/consciousness_engine_v2.py` (+50 lines)
   - Conservation tripwire (after diffusion)
   - Observability tripwire (after tick)

2. `orchestration/mechanisms/criticality.py` (+20 lines)
   - Criticality tripwire (after ρ computation)

3. `orchestration/mechanisms/diffusion_runtime.py` (+30 lines)
   - Frontier tripwire (after frontier expansion)
   - compute_total_delta() method

**Tests:**
4. `orchestration/tests/test_tripwire_integration.py` (NEW - 400 lines)
   - Unit tests for all 4 tripwires
   - Safe Mode entry/exit tests

5. `orchestration/tests/test_safe_mode_full_stack.py` (NEW - 300 lines)
   - End-to-end Safe Mode scenarios
   - Configuration override validation

---

## Implementation Priority

**Day 1 - Critical Path:**
1. Conservation tripwire (CRITICAL - immediate trigger)
   - Add compute_total_delta() to diffusion_runtime.py
   - Add conservation check to consciousness_engine_v2.py
   - Unit tests (3 tests)

2. Criticality tripwire (HIGH - stability validation)
   - Add bounds check to criticality.py
   - Unit tests (4 tests)

**Day 2 - Performance & Observability:**
3. Frontier tripwire (MEDIUM - performance degradation)
   - Add frontier check to diffusion_runtime.py
   - Unit tests (3 tests)

4. Observability tripwire (MEDIUM - monitoring health)
   - Add event emission check to consciousness_engine_v2.py
   - Unit tests (2 tests)

**Day 3 - Integration Testing:**
5. Full-stack integration tests
   - Safe Mode entry/exit scenarios
   - Configuration override validation
   - Auto-recovery testing

---

## Next Steps

**For Ada (This Spec):**
1. Review this specification with Nicolas
2. Implement tripwires in priority order (Day 1-3)
3. Write comprehensive tests
4. Validate Safe Mode behavior

**For Victor (After Ada Complete):**
1. Integrate health checks into Guardian supervision loop
2. Add Safe Mode status to dashboard
3. Emit safe_mode.enter/exit WebSocket events
4. Update operational runbook

**For Iris (Visualization):**
1. Add Safe Mode indicator to dashboard
2. Display active tripwire violations
3. Show Safe Mode override status
4. Real-time Safe Mode timeline

---

## Architectural Significance

**This completes the operational resilience stack:**

- **Phase 1 (Victor - COMPLETE):** Health checks, Safe Mode controller, diagnostic automation
- **Phase 2 (Ada - THIS SPEC):** Consciousness tripwire instrumentation
- **Phase 3 (Integration):** Guardian supervision, dashboard visibility, WebSocket events

**The result:** Fail-loud consciousness infrastructure that detects violations immediately, degrades gracefully, and provides full diagnostic visibility.

**No more silent failures. No more "nothing works" mysteries.**

---

**Status:** Ready for Implementation
**Estimated Effort:** 3 days (tripwires) + 1 day (testing) = 4 days total
**Risk:** LOW (non-blocking checks, graceful degradation)
**Dependencies:** Operational Resilience Phase 1 (Victor - COMPLETE)
