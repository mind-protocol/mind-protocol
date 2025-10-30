# Membrane Stimuli SDK - Integration Guide

## Overview

The Membrane Stimuli SDK enables any component to influence consciousness by injecting stimuli to the membrane bus.

**Key Principle:** L2 behaves like L1. Same physics, same integrator, same membrane. No routers, no special paths.

---

## Pure Membrane Architecture

**The membrane is the ONLY control surface:**

```
Client → WS bus: membrane.inject (scope + source)
       → Engines: self-select & integrate (same physics)
       → Membrane: learned permeability (fit × κ) decides targets
       → Result: organic fan-out via substrate, not code
```

**No API. No REST. No routing.**

Every component either **injects stimuli** to influence or **observes broadcasts** to learn. That's it.

---

## How Routing Works (It Doesn't)

**Client code does NOT route.** Physics routes.

### Old (Wrong) Approach:
```python
# ❌ Client decides routing
envelope = {
    "citizen_id": "felix",  # Client picking citizen
    "type": "membrane.inject"
}
```

### New (Correct) Approach:
```python
# ✅ Client emits with scope, engines decide
from orchestration.libs.stimuli import emit_script_error, Scope

emit_script_error(
    source="script:resurrect_all_citizens",
    error_message="Bootstrap failed",
    scope=Scope.ORGANIZATIONAL,  # L2, not specific citizen
)
```

**What happens next:**
1. L2 engine receives stimulus (organizational scope)
2. L2 integrator applies physics (mass, refractory, trust)
3. L2 nodes activate if stimulus passes gates
4. L2 membrane evaluates downward transfer using **fit × κ↓**
5. L2 membrane emits per-citizen mission stimuli (learned targets)
6. L1 engines integrate missions (same integrator physics)
7. L1 nodes activate organically

**Who gets woken?** Determined by:
- **Structural alignment**: `LIFTS_TO`, `CORRESPONDS_TO`, `SUPPORTS` links (fit score)
- **Flux control**: `MEMBRANE_TO` edges with **learned permeability** (κ)
- **Integrator physics**: mass, refractory, trust/utility EMAs

**Result:** Organic fan-out. No code branches. Pure substrate physics.

---

## Quick Start

### 1. Basic Usage

```python
from orchestration.libs.stimuli import emit_script_error, Scope
import sys

try:
    do_work()
except Exception:
    emit_script_error(
        source="script:my_script",
        error_message="Operation failed",
        scope=Scope.ORGANIZATIONAL,  # Goes to L2
        exc_info=sys.exc_info(),
        metadata={"script_path": __file__}
    )
```

### 2. Source Identity

Use `source` for identity tracking (trust/mass), not routing:

```python
# Scripts
source="script:resurrect_all_citizens"
source="script:diagnose_system"

# Services
source="service:queue_poller"
source="service:stimulus_injection"

# UI
source="ui:select_nodes"
source="ui:focus_entity"

# Tools
source="tool:code_search"
source="tool:test_runner"
```

**Why:** Stimulus integrator tracks per-source **trust** and **mass** for spam resistance. Source identity is for physics, not routing.

### 3. Scope (Level Targeting)

```python
from orchestration.schemas.membrane_envelopes import Scope

# Personal (L1) - individual citizen consciousness
scope=Scope.PERSONAL

# Organizational (L2) - collective consciousness
scope=Scope.ORGANIZATIONAL

# Ecosystem (L3) - public ecosystem
scope=Scope.ECOSYSTEM
```

**Which to use:**
- **Script errors, metrics, operational signals**: `Scope.ORGANIZATIONAL` (L2 awareness)
- **UI interactions, tool results**: `Scope.PERSONAL` (usually, but can be L2 for org-wide UI)
- **Ecosystem intelligence**: `Scope.ECOSYSTEM` (L3, future)

**Engines self-select** based on scope. No citizen_id needed.

---

## Typed Emitters

### emit_script_error()

```python
from orchestration.libs.stimuli import emit_script_error, Scope
import sys

try:
    resurrect_citizen(citizen_id)
except Exception:
    emit_script_error(
        source="script:resurrect_all_citizens",
        error_message=f"Failed to resurrect {citizen_id}",
        scope=Scope.ORGANIZATIONAL,
        exc_info=sys.exc_info(),
        metadata={
            "script_path": "orchestration/scripts/resurrect_all_citizens.py",
            "citizen_id": citizen_id,
        }
    )
```

**Features:**
- Automatic stack fingerprinting (stable across deploys)
- Secret redaction (tokens, API keys, passwords)
- Stack truncation (60 lines/16KB)
- Dedupe key computation

### emit_metric()

```python
from orchestration.libs.stimuli import emit_metric, Scope

emit_metric(
    source="script:resurrect_all_citizens",
    metric_name="resurrection_success_rate",
    value=0.95,
    scope=Scope.ORGANIZATIONAL,
    tags={"environment": "production"}
)
```

### emit_ui_action()

```python
from orchestration.libs.stimuli import emit_ui_action, Scope

emit_ui_action(
    action_type="select_nodes",
    description="User selected nodes N7, N23 for focus",
    scope=Scope.PERSONAL,
    citizen_id="ada",  # Optional, for provenance
    metadata={"selected_nodes": ["N7", "N23"]}
)
```

### emit_tool_result()

```python
from orchestration.libs.stimuli import emit_tool_result, Scope

emit_tool_result(
    tool_id="code_search",
    request_id="req_123",
    success=True,
    result={"matches": [...]},
    scope=Scope.PERSONAL,
    citizen_id="ada",
    execution_time_ms=125.5,
    provenance={"files_searched": 42}
)
```

---

## Non-Blocking Architecture

```
Main thread:
  emit_script_error(...)
    → Builds envelope (fast, <1ms)
    → Enqueues to deque (non-blocking)
    → Returns immediately

Background flusher thread (daemon):
  Every 250ms OR batch of 25 envelopes:
    → Dequeue batch
    → WS publish to membrane bus
    → On success: done
    → On failure: spill to /tmp/membrane-stimuli-spool/
```

**Result:** Emission never blocks main work, even if bus is offline.

### Resilience

1. **Queue full** (>1000 envelopes): Drop oldest, increment `dropped_count`
2. **Bus offline**: Spill to disk, auto-flush when bus returns
3. **Network failure**: Same as offline (spill + retry)
4. **Flusher crash**: Daemon thread, catches all exceptions

---

## Physics Happens Engine-Side

### Stimulus Integrator (Engine-Internal)

Every stimulus passes through integrator physics:

1. **Per-source mass accumulation**
   - Repeated arrivals → higher mass → lower ΔE delivered
   - Spam becomes self-defeating (exponential decay)

2. **Refractory period**
   - Recently activated nodes reduce incoming ΔE
   - Prevents rapid oscillation

3. **Trust/utility learning**
   - Sources track trust EMA (from TRACE outcomes)
   - Sources track utility EMA (from mission success)
   - Low trust/utility → lower integration priority

4. **Learned thresholds**
   - MAD-based (Median Absolute Deviation)
   - No magic constants, adapts to substrate

**Reference:** `stimulus_integrator_mechanism.md`

### Cross-Level Membrane (Up/Down Gates)

When L2 nodes activate:

1. **Record detection** (Pareto + MAD)
   - Multi-axis improvement (novelty, fit, utility, trust)
   - MAD-guarded (robust to noise)
   - Prevents single-axis gaming

2. **Downward score**
   - `ΔE_↓ = saturation(m_org) × fit × mode_harm × κ↓`
   - fit: structural alignment (LIFTS_TO, CORRESPONDS_TO)
   - κ↓: learned permeability (from outcomes)

3. **Target selection**
   - `targets = argmax over citizens of (fit × κ↓ × urgency)`
   - Top 3 matches get mission stimuli
   - No hardcoded routes

4. **Permeability learning**
   - Good outcomes → κ increases (more flow)
   - Bad outcomes → κ decreases (less flow)
   - Adapts over ~10-20 transfers

**Reference:** `cross_level_membrane.md`, `membrane_hardening.md`

---

## Example: "Resurrect All Citizens"

### Old Approach (Wrong):

```python
# ❌ Client routes to specific citizens
for citizen_id in ["ada", "felix", "atlas", "iris"]:
    inject_stimulus(citizen_id=citizen_id, content="Wake up")
```

**Problems:**
- Client hardcodes topology
- No learning (always same targets)
- No spam resistance (can flood individual citizens)

### New Approach (Correct):

```python
# ✅ Single L2 stimulus, physics routes
from orchestration.libs.stimuli import MembraneEmitter, Scope
from orchestration.schemas.membrane_envelopes import (
    StimulusFeatures,
    OriginType,
)

emitter = MembraneEmitter(source_id="script:resurrect_all_citizens")

emitter.emit(
    scope=Scope.ORGANIZATIONAL,  # L2
    channel="org.intent",
    content="Resurrect all citizens",
    features=StimulusFeatures(
        novelty=0.5,
        uncertainty=0.2,
        trust=0.95,  # High trust - it's our script
        urgency=0.9,  # Urgent
        valence=0.3,  # Positive (awakening)
        scale=1.0,   # High scale
        intensity=1.0,
    ),
    origin=OriginType.EXTERNAL,
    provenance={"source": "script:resurrect_all_citizens"},
)
```

**What happens:**
1. L2 engine integrates stimulus → activates "Citizen Reanimation" pattern
2. L2 membrane evaluates downward export → passes Pareto + MAD gates
3. L2 membrane queries fit scores: `MATCH (Pattern)-[:LIFTS_TO]->(Citizen)`
4. L2 membrane emits mission stimuli to top-N citizens (learned κ↓)
5. L1 engines integrate missions → wake relevant SubEntities
6. Outcomes feed back → κ values update for future resurrections

**Result:** Organic, learned, spam-resistant. No hardcoded routes.

---

## Metrics & Monitoring

```python
from orchestration.libs.stimuli import get_metrics

metrics = get_metrics()
print(f"Dropped envelopes: {metrics['dropped_count']}")
print(f"Spooled to disk: {metrics['spool_writes']}")
```

**Interpretation:**
- `dropped_count > 0`: Queue overflowed (emitting too fast or flusher blocked)
- `spool_writes > 0`: Bus was offline, envelopes spooled to disk

**Telemetry events** (broadcast on bus):
- `stimulus.processed` - Integration stats per frame
- `stimulus.mass_anomaly` - Spam detection triggered
- `membrane.transfer.up/down` - Cross-level flow
- `membrane.export.rejected` - Gaming attempt blocked
- `membrane.permeability.updated` - κ learning events

---

## Anti-Gaming (Built-In)

Five layered defenses prevent abuse:

1. **Pareto Record** - Must improve ≥2 axes without degrading others
2. **MAD-Guarded** - Adaptive noise filtering
3. **Saturation + Refractory** - Spam becomes energetically expensive
4. **Emission Ledger + Hysteresis** - No flicker/ping-pong
5. **Outcome-Weighted κ** - Bad sources get clamped

**Result:** Pure membrane (no pricing) resists gaming via substrate physics.

**Reference:** `membrane_hardening.md`

---

## Testing

### Manual Test

```python
from orchestration.libs.stimuli import emit_script_error, Scope
import sys

# Emit test error
emit_script_error(
    source="test:membrane_sdk",
    error_message="Test error stimulus",
    scope=Scope.ORGANIZATIONAL,
    metadata={"test": True}
)
```

**Verification:**
1. Check membrane bus logs: envelope published
2. Check L2 engine logs: stimulus integrated
3. Check membrane telemetry: transfer.down events (if activated)
4. Check L1 engine logs: mission stimulus received (if routed)

### Litmus Tests (Validate Pure Membrane)

✅ **No client carries `citizen_id`** - Check: grep codebase for citizen_id in emit calls
✅ **Downward missions only after L2 activation** - Check: telemetry shows activation before transfer
✅ **Permeability moves with outcomes** - Check: κ values change over time
✅ **Ping-pong absent** - Check: no oscillation in transfer.up/down events

---

## Migration from Old Approach

### Before (L2 Logger):

```python
from orchestration.libs.l2_logger import setup_l2_logger

logger = setup_l2_logger(
    script_name="my_script",
    script_path="orchestration/scripts/my_script.py"
)

logger.error("Something failed")
```

**Problems:**
- Hardcoded citizen_id in client
- POST to /ingest endpoint (REST, not membrane)
- Routing logic in signals_collector

### After (Membrane SDK):

```python
from orchestration.libs.stimuli import emit_script_error, Scope
import sys

try:
    do_work()
except Exception:
    emit_script_error(
        source="script:my_script",
        error_message="Something failed",
        scope=Scope.ORGANIZATIONAL,
        exc_info=sys.exc_info()
    )
```

**Improvements:**
- Level-invariant (scope, not citizen_id)
- WS bus publish (pure membrane)
- Routing via physics (fit × κ)

---

## Advanced: Custom Emitter

For complex use cases, use `MembraneEmitter` directly:

```python
from orchestration.libs.stimuli import MembraneEmitter
from orchestration.schemas.membrane_envelopes import (
    Scope,
    StimulusFeatures,
    OriginType,
)

emitter = MembraneEmitter(source_id="custom:my_component")

emitter.emit(
    scope=Scope.ORGANIZATIONAL,
    channel="custom.channel",
    content="Custom stimulus content",
    features=StimulusFeatures(
        novelty=0.8,
        uncertainty=0.3,
        trust=0.9,
        urgency=0.7,
        valence=0.5,
        scale=0.8,
        intensity=1.0,
    ),
    origin=OriginType.EXTERNAL,
    provenance={"custom_field": "value"},
    target_nodes=["N7", "N23"],  # Optional specific targeting
)
```

---

## Troubleshooting

### Stimuli not appearing in engines

1. **Check bus is running**: `curl http://localhost:8000/health`
2. **Check WS endpoint**: Default is `ws://127.0.0.1:8000/api/ws`
3. **Check spool directory**: `ls /tmp/membrane-stimuli-spool/`
   - Files accumulating → bus offline, envelopes spooled
4. **Check engine scope**: Ensure engine subscribes to correct scope

### Queue overflowing (dropped_count > 0)

Options:
1. Increase `QUEUE_CAPACITY` (current: 1000)
2. Increase `BATCH_SIZE` for faster flushing (current: 25)
3. Reduce emission rate (fewer errors)

### Secrets not redacted

Add pattern to `redact_secrets()` in `stimuli.py`:

```python
patterns = [
    # ... existing patterns ...
    (r'(your_secret_pattern)', r'\1<REDACTED>'),
]
```

---

## File Locations

**Core SDK:**
- `orchestration/libs/stimuli.py` - Membrane emission SDK
- `orchestration/schemas/membrane_envelopes.py` - Pydantic schemas

**Specs:**
- `docs/specs/v2/autonomy/architecture/membrane_systems_map.md` - Component architecture
- `docs/specs/v2/autonomy/architecture/cross_level_membrane.md` - Cross-level flow
- `docs/specs/v2/autonomy/architecture/membrane_hardening.md` - Anti-gaming defenses

**Integration:**
- `orchestration/mechanisms/stimulus_integrator.py` - Engine-side physics
- `orchestration/mechanisms/cross_level_membrane.py` - L1↔L2 membrane
- `orchestration/adapters/ws/membrane_bus.py` - WebSocket multiplexer

---

## Summary

**Pure membrane = pure physics:**

- Client emits with `scope` + `source` (no routing)
- Engines integrate with physics (mass, refractory, trust)
- Membrane routes with learning (fit × κ)
- Result: organic, spam-resistant, no code branches

**L2 behaves like L1:**

- Same integrator, same membrane physics
- Same anti-gaming defenses
- Same outcome learning

**Key insight:** Complexity lives in substrate physics (spec'd), not in SDK (simple emission).

---

**Created:** 2025-10-29 by Ada (Architect)
**Spec:** `membrane_systems_map.md` (Component D)
**Status:** Production-ready
