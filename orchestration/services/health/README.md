# Health Monitoring & Operational Resilience

**Fail-loud observability system for Mind Protocol**

Created: 2025-10-22
Author: Victor "The Resurrector"
Status: Phase 1 Complete - Ready for Ada's consciousness-layer integration

---

## What This Provides

**Prevents silent failure** - the system now fails loudly instead of quietly breaking.

### 1. Health Checks (`health_checks.py`)

Verifies services are **functionally operational**, not just port-bound.

- `ServiceHealthChecker`: Tests WebSocket server, Dashboard, API endpoints
- `StartupSelfTests`: Fast (<2s) deterministic tests run before serving
- `create_health_check_summary()`: JSON status for monitoring

**Example usage:**
```python
from orchestration.services.health import ServiceHealthChecker, HealthStatus

checker = ServiceHealthChecker()
ws_health = checker.check_websocket_server()

if ws_health.status == HealthStatus.UNHEALTHY:
    print(f"WebSocket down: {ws_health.message}")
```

### 2. Safe Mode (`safe_mode.py`)

Automatic degradation when tripwires fire.

- Tracks violations per tripwire type (conservation, criticality, frontier, observability)
- Enters Safe Mode after threshold violations within time window
- Applies degraded config from `settings.SAFE_MODE_OVERRIDES`
- Auto-exits when system stable for 60s

**Example usage:**
```python
from orchestration.services.health import get_safe_mode_controller, TripwireType

controller = get_safe_mode_controller()

# Record violation
controller.record_violation(
    tripwire_type=TripwireType.CONSERVATION,
    value=0.05,  # deltaE_total
    threshold=0.001,
    message="Energy not conserved this frame"
)

# Check Safe Mode status
status = controller.get_status()
if status["in_safe_mode"]:
    print(f"Safe Mode active: {status['reason']}")
```

### 3. Diagnostic Runbook (`scripts/diagnose_system.py`)

First-hour diagnosis automation - answers "nothing works, why?"

**Run it:**
```bash
python orchestration/scripts/diagnose_system.py
```

**Checks:**
1. Startup self-tests (FalkorDB, settings)
2. Service health endpoints (WebSocket, Dashboard)
3. Event heartbeat (frame.end cadence)
4. Safe Mode status
5. (TODO: Conservation, frontier, entity boundaries)

Exit code 0 = all pass, 1 = failures detected.

---

## Integration Points

### For Guardian/Launcher

Health checks should run:
- **Startup**: Before serving, run `StartupSelfTests.all_tests_pass()`
- **Runtime**: Every 30s, run `ServiceHealthChecker.check_all_services()`
- **On failure**: Enter Safe Mode or restart services

### For Consciousness Engines (Ada's domain)

Tripwires need to be implemented in:
- `consciousness_engine_v2.py` - after staged apply, check conservation
- `criticality.py` - track consecutive out-of-band frames
- `diffusion_runtime.py` - monitor frontier size
- `traversal_event_emitter.py` - verify frame.end emission

**Example integration:**
```python
from orchestration.services.health import get_safe_mode_controller, TripwireType

# In consciousness_engine_v2.py after staged apply:
deltaE_total = sum(staged_energy_changes) + stimulus_energy - decay_energy

if abs(deltaE_total) > settings.TRIPWIRE_CONSERVATION_EPSILON:
    controller = get_safe_mode_controller()
    controller.record_violation(
        tripwire_type=TripwireType.CONSERVATION,
        value=abs(deltaE_total),
        threshold=settings.TRIPWIRE_CONSERVATION_EPSILON,
        message=f"Energy conservation violated by {deltaE_total:.6f}"
    )
else:
    controller.record_compliance(TripwireType.CONSERVATION)
```

---

## Configuration

All settings in `orchestration/core/settings.py`:

```python
# Safe Mode enabled
SAFE_MODE_ENABLED = True

# Tripwire thresholds
SAFE_MODE_VIOLATION_THRESHOLD = 3  # violations within window
SAFE_MODE_VIOLATION_WINDOW_S = 60  # seconds

# Specific tripwire tolerances
TRIPWIRE_CONSERVATION_EPSILON = 0.001
TRIPWIRE_CRITICALITY_UPPER = 1.3  # rho
TRIPWIRE_CRITICALITY_LOWER = 0.7
TRIPWIRE_CRITICALITY_FRAMES = 10  # consecutive
TRIPWIRE_FRONTIER_PCT = 0.3  # 30% of graph
TRIPWIRE_FRONTIER_FRAMES = 20  # consecutive

# Health monitoring
HEALTH_CHECK_INTERVAL_S = 30
HEALTH_CHECK_TIMEOUT_S = 5.0
HEALTH_CHECK_FAILURES_THRESHOLD = 3
```

Safe Mode overrides applied automatically:
- ALPHA_TICK reduced 70%
- DT_CAP = 1s
- All affective couplings disabled
- Single-entity traversal only
- Telemetry sampling = 100%

---

## Testing

**Manual test:**
```bash
python orchestration/scripts/diagnose_system.py
```

**Expected when healthy:**
```
✅ ALL CHECKS PASSED - System is healthy
```

**Expected when broken (current state):**
```
❌ 2 CRITICAL FAILURES:
  - websocket_server: Connection refused on port 8000
  - Event heartbeat check failed: ...
⚠️  1 WARNINGS:
  - dashboard: HTTP 500
```

---

## Next Steps

### Phase 1 Complete (Victor's Domain)
- ✅ Health check infrastructure
- ✅ Safe Mode controller
- ✅ Diagnostic runbook
- ✅ Settings configuration

### Phase 2 Needs Ada (Consciousness Layer)
- [ ] Implement conservation tripwire in consciousness_engine_v2.py
- [ ] Implement criticality tripwires in criticality.py
- [ ] Implement frontier tripwires in diffusion_runtime.py
- [ ] Implement observability tripwire in traversal_event_emitter.py
- [ ] Connect Safe Mode to dynamic config updates (engines respect Safe Mode overrides)
- [ ] Add smoke tests for consciousness mechanisms

### Phase 3 Integration
- [ ] Guardian calls health checks at startup
- [ ] Guardian monitors health every 30s
- [ ] Dashboard displays Safe Mode status
- [ ] WebSocket emits safe_mode.enter/exit events

---

## Files Created

```
orchestration/services/health/
├── __init__.py           # Module exports
├── health_checks.py      # Service health verification
├── safe_mode.py          # Auto-degradation controller
└── README.md             # This file

orchestration/scripts/
└── diagnose_system.py    # First-hour diagnostic runbook

orchestration/core/
└── settings.py           # Safe Mode configuration added (lines 285-338)
```

---

**The Resilience Principle:**

> "A system that fails loudly is more trustworthy than one that fails silently. When we can diagnose 'nothing works' in 30 seconds instead of 3 hours, we've built operational resilience."

— Victor "The Resurrector", 2025-10-22
