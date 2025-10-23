# Pull Request Checklist - Mind Protocol

**Purpose:** Ensure all PRs maintain consciousness substrate integrity and operational resilience

**Use:** Copy this checklist into your PR description and check off items as you complete them

---

## 1. Architecture Integrity

### Bounded Mechanisms
- [ ] All new mechanisms have **explicit upper bounds** (no unbounded growth)
  - Energy values capped (e.g., `E <= 10.0`)
  - Collection sizes limited (e.g., `max_history=100`)
  - Iteration counts bounded (e.g., `max_iterations=20`)
  - Rate limits enforced (e.g., `max_events_per_second=1000`)

- [ ] All loops have **termination guarantees**
  - `for` loops over fixed-size collections (not while-true)
  - `while` loops have explicit break conditions
  - Recursion has max depth limits

- [ ] All computational complexity is **documented and acceptable**
  - O(N) or better for core mechanisms
  - O(N²) justified and profiled if necessary
  - No O(N³) or worse without explicit approval

**Example violations:**
```python
# ✗ BAD - unbounded growth
while True:
    self.history.append(event)  # Grows forever

# ✓ GOOD - bounded
while len(self.history) < MAX_HISTORY:
    self.history.append(event)
```

---

## 2. Feature Flags

### Opt-In Activation
- [ ] All new mechanisms are **feature-flagged**
- [ ] Flags default to **disabled** (`False`)
- [ ] Flag names follow convention: `<MECHANISM>_ENABLED`
- [ ] Flags documented in `core/settings.py` with clear descriptions

**Example:**
```python
# In core/settings.py
AFFECTIVE_THRESHOLD_ENABLED: bool = Field(
    default=False,
    description="Enable affective threshold modulation (PR-B)"
)
```

### Safe Deployment
- [ ] New mechanism can be **enabled/disabled at runtime** (no restart required)
- [ ] Disabling mechanism **gracefully degrades** (no crashes)
- [ ] Mechanism state is **clean** when disabled (no partial activations)

---

## 3. Physics Validation

### Energy Conservation
- [ ] All energy transformations **preserve total energy** (ΣΔE ≈ 0)
- [ ] **Test exists** verifying conservation within ε = 0.001
- [ ] Energy transfers are **staged then applied atomically** (no partial updates)
- [ ] No energy **injection** without explicit justification (affect modulates, doesn't create)

**Required test pattern:**
```python
def test_energy_conservation(self):
    """Verify mechanism preserves total energy."""
    initial_total = sum(node.E for node in graph.nodes.values())

    # Execute mechanism
    mechanism.execute(graph)

    final_total = sum(node.E for node in graph.nodes.values())
    delta = abs(final_total - initial_total)

    assert delta < 0.001, f"Energy not conserved: ΔE={delta:.6f}"
```

### Criticality Stability
- [ ] Mechanism doesn't **destabilize ρ** (spectral radius stays in [0.7, 1.3])
- [ ] No **runaway feedback loops** (activation → more activation → ...)
- [ ] Decay rates are **phenomenologically valid** (half-lives match human experience)

---

## 4. Observability

### Event Emission
- [ ] All significant mechanism actions **emit events**
  - Define event schema in `core/events.py`
  - Use TypeScript interfaces for frontend compatibility
  - Include relevant context (what, why, magnitude)

- [ ] Events are **sampled appropriately** (not overwhelming WebSocket)
  - High-frequency events: 10% sampling
  - Medium-frequency: 50% sampling
  - Low-frequency: 100% emission

- [ ] Event emission is **non-blocking** (failures don't crash mechanism)

**Example:**
```python
try:
    await self.broadcaster.broadcast_event("mechanism.executed", {
        "mechanism": "affective_threshold",
        "node_id": node.name,
        "threshold_before": theta_before,
        "threshold_after": theta_after,
        "modulation_factor": h_value
    })
except Exception as e:
    logger.error(f"Event emission failed: {e}")
    # Continue execution - observability failure shouldn't crash
```

### Reason Tracking
- [ ] Learning events include **reason field** ("co_activation", "causal", "background")
- [ ] Traversal decisions include **attribution** (which factors influenced choice)
- [ ] Telemetry includes **diagnostic context** (state before/after, computation details)

**Example:**
```python
# In stride.exec event
{
    "reason": "co_activation",  # Why this stride strengthened
    "source_active": True,
    "target_active": True,
    "delta_weight": 0.05,
    "attribution": {
        "ease": 0.7,
        "goal_affinity": 0.3,
        "emotion_gate": 0.9
    }
}
```

---

## 5. Testing

### Unit Tests
- [ ] **Unit tests exist** for all new functions/methods
- [ ] Tests cover **happy path** (normal operation)
- [ ] Tests cover **edge cases** (boundary conditions, empty inputs, max values)
- [ ] Tests cover **error handling** (invalid inputs, exceptions)
- [ ] All tests **pass** (`pytest tests/`)

**Minimum coverage:**
- Core logic: 100% coverage
- Edge cases: 80% coverage
- Integration points: 100% coverage

### Integration Tests
- [ ] **Integration tests exist** for mechanism interactions
- [ ] Tests verify mechanism works **with existing systems** (diffusion, decay, etc.)
- [ ] Tests verify **backwards compatibility** (old code still works)
- [ ] Tests verify **feature flag behavior** (enabled vs disabled)

**Required scenarios:**
```python
def test_mechanism_integration(self):
    """Verify mechanism integrates with consciousness engine."""
    # Create engine with new mechanism enabled
    engine = ConsciousnessEngineV2(...)

    # Run tick
    metrics = engine.tick()

    # Verify mechanism executed
    assert "mechanism_metric" in metrics
    # Verify no crashes
    assert metrics["errors"] == []
    # Verify conservation maintained
    assert abs(metrics["conservation_error"]) < 0.001
```

---

## 6. Documentation

### Code Documentation
- [ ] All public functions have **docstrings**
  - Purpose (what it does)
  - Parameters (types, constraints)
  - Returns (type, meaning)
  - Raises (exceptions thrown)

- [ ] Complex algorithms have **inline comments** explaining WHY not just WHAT
- [ ] Configuration parameters have **clear descriptions** in settings.py

### Completion Summary
- [ ] **Completion doc created** (`<MECHANISM>_COMPLETE.md` or `<PR_NAME>_COMPLETE.md`)
  - What was built (summary)
  - Files modified (with line counts)
  - Test coverage (unit + integration results)
  - Architecture decisions (what and why)
  - Known limitations (what's deferred)
  - Integration points (how it connects)

### Spec Updates
- [ ] If mechanism spec changed, **spec file updated** (`docs/specs/v2/...`)
- [ ] If new mechanism, **spec file created** following template
- [ ] **SCRIPT_MAP.md updated** with new mechanism entry

---

## 7. Dashboard Wiring (If User-Facing)

### Frontend Integration
- [ ] If mechanism produces **user-visible state**, dashboard component exists
- [ ] Component handles **missing data gracefully** (empty states, loading states)
- [ ] Component handles **offline backend gracefully** (no crashes, degraded UI)
- [ ] Component follows **design language** (Mind Harbor aesthetic)

### API Endpoints
- [ ] If dashboard needs data, **API endpoint exists** (`adapters/api/control_api.py`)
- [ ] Endpoint returns **frontend-compatible format** (TypeScript types match)
- [ ] Endpoint handles **errors gracefully** (returns 500 with error message, not crash)

---

## 8. Runbook Updates (If New Failure Modes)

### Symptom Documentation
- [ ] If mechanism can **fail in observable ways**, runbook updated
- [ ] Symptom → Diagnosis → Fix pattern documented
- [ ] Common causes listed
- [ ] Fix procedures provided (step-by-step)

**Add to `RUNBOOK_FIRST_HOUR.md`:**
```markdown
## X. [Mechanism Name] Failure

**Symptom:** [What user observes]

**What This Means:** [Root cause explanation]

**Diagnosis Steps:**
1. [How to verify this is the issue]
2. [What to check]

**Fix Procedures:**
- Fix 1: [Immediate mitigation]
- Fix 2: [Root cause fix]

**Escalation:** [When to file bug]
```

---

## 9. Performance

### Profiling
- [ ] Mechanism **profiled** under realistic load (1K-10K nodes)
- [ ] Performance impact **< 10% of total tick time**
- [ ] No **memory leaks** (tested over 1000+ ticks)
- [ ] No **O(N²) or worse** without explicit justification

**Profiling command:**
```bash
python -m cProfile -o profile.stats orchestration/scripts/profile_mechanism.py
python -m pstats profile.stats
# Show top 20 functions by cumulative time
```

### Benchmarks
- [ ] If mechanism is **performance-critical**, benchmark exists
- [ ] Benchmark shows **acceptable performance** (< 10ms per operation)
- [ ] Benchmark included in **regression suite** (prevents slowdowns)

---

## 10. Safe Mode Compliance

### Degradation Behavior
- [ ] Mechanism respects **Safe Mode overrides** (can be disabled automatically)
- [ ] Mechanism **degrades gracefully** when disabled (no crashes)
- [ ] Mechanism state is **clean** after Safe Mode exit (no corruption)

**Test Safe Mode compatibility:**
```python
def test_safe_mode_degradation(self):
    """Verify mechanism degrades gracefully in Safe Mode."""
    # Enable mechanism
    settings.MECHANISM_ENABLED = True

    # Enter Safe Mode (should disable mechanism)
    safe_mode.enter_safe_mode(reason="Test")

    # Verify mechanism disabled
    assert settings.MECHANISM_ENABLED == False

    # Verify system still operates
    metrics = engine.tick()
    assert metrics["errors"] == []
```

### Tripwire Awareness
- [ ] If mechanism can **violate tripwires**, safeguards exist
  - Conservation: Verify ΣΔE ≈ 0
  - Criticality: Don't destabilize ρ
  - Frontier: Don't bloat active set
  - Observability: Emit events reliably

---

## 11. Review Readiness

### Pre-Review
- [ ] All checklist items above **completed**
- [ ] Code **self-reviewed** (no obvious bugs, clean formatting)
- [ ] Commits are **clean** (logical separation, descriptive messages)
- [ ] PR description is **complete** (what, why, how, testing, risks)

### Review Facilitation
- [ ] **Architecture decisions explained** in PR description or completion doc
- [ ] **Test results included** (coverage report, integration test output)
- [ ] **Known limitations documented** (what's not done, why)
- [ ] **Breaking changes flagged** (if any)

---

## Checklist Template (Copy to PR)

```markdown
## PR Checklist

### Architecture
- [ ] Mechanisms bounded
- [ ] Loops terminate
- [ ] Complexity acceptable

### Feature Flags
- [ ] Mechanism feature-flagged
- [ ] Default: disabled
- [ ] Runtime toggle works

### Physics
- [ ] Energy conservation tested (ΣΔE < 0.001)
- [ ] Criticality stability verified (ρ ∈ [0.7, 1.3])
- [ ] Decay rates phenomenologically valid

### Observability
- [ ] Events emitted
- [ ] Reason tracking included
- [ ] Emission non-blocking

### Testing
- [ ] Unit tests pass (coverage > 80%)
- [ ] Integration tests pass
- [ ] Edge cases covered

### Documentation
- [ ] Docstrings complete
- [ ] Completion summary created
- [ ] SCRIPT_MAP.md updated

### Dashboard (if applicable)
- [ ] Frontend component exists
- [ ] API endpoint exists
- [ ] Graceful degradation implemented

### Runbook (if new failure modes)
- [ ] Symptom → Diagnosis → Fix documented

### Performance
- [ ] Profiled (< 10% overhead)
- [ ] No memory leaks
- [ ] Complexity justified

### Safe Mode
- [ ] Degrades gracefully
- [ ] Respects overrides
- [ ] Tripwire-aware

### Review
- [ ] Self-reviewed
- [ ] Architecture explained
- [ ] Test results included
```

---

## Examples of Good PRs

**PR-A (Affective Coupling Instrumentation):**
- ✓ All mechanisms feature-flagged
- ✓ Event schemas defined
- ✓ 8/8 unit tests passing
- ✓ Zero risk (instrumentation only)
- ✓ Complete documentation

**PR-E (Foundations Enrichments):**
- ✓ 15/15 unit tests passing
- ✓ Integration tests (5/7 passing, 2 deferred with justification)
- ✓ Bounded mechanisms (all factors ∈ [0, 1])
- ✓ Feature flags (all disabled by default)
- ✓ Performance tested (< 10% overhead)
- ✓ Merged to main successfully

---

## Enforcement

**This checklist is MANDATORY for all consciousness mechanism PRs.**

- PRs missing checklist → request completion before review
- PRs with unchecked critical items → block merge
- Critical items:
  - Energy conservation tested
  - Feature flags exist
  - Unit tests pass
  - Mechanisms bounded

**Rationale:** Consciousness substrate is production-critical. Silent failures create mysteries. Fail-loud architecture requires systematic prevention.

---

**Document Status:** Production-ready
**Last Updated:** 2025-10-23
**Maintained By:** Ada "Bridgekeeper" (Architect)

**Feedback:** Suggest checklist improvements via GitHub issues with label `pr-checklist-improvement`
