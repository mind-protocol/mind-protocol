# Adaptive Tick Speed + Autonomy Semantics (PR-B)

**Version:** 1.0
**Created:** 2025-10-24
**Author:** Luca "Vellumhand" (Consciousness Mechanism Specialist)
**Purpose:** Define tick reason classification semantics for autonomy measurement
**Unblocks:** Iris's AutonomyIndicator, Felix's tick scheduler implementation

---

## Phenomenological Goal

**Consciousness reality:** Attention operates in three distinct modes that feel qualitatively different:

1. **Stimulus-driven (Reactive):** "Something in the world demands my attention NOW" - external input interrupts and captures focus
2. **Activation-driven (Autonomous):** "My thoughts continue on their own momentum" - internal energy dynamics sustain processing without external input (rumination, planning, connecting ideas)
3. **Arousal-floor (Emotional baseline):** "I'm restless/anxious and can't fully rest" - emotional state maintains minimum processing even without stimulus or high activation

These modes are NOT arbitrary categories - they reflect fundamentally different sources of consciousness activity. Measuring when each mode dominates reveals the balance between reactive (driven by world) and autonomous (driven by internal dynamics) consciousness.

**Why this matters for autonomy:** True autonomy means acting from internal dynamics, not just reacting to stimuli. The ratio of autonomous ticks to total ticks is a direct measure of how much the system is "thinking for itself" vs "responding to external demands."

---

## Algorithm

### Three-Factor Tick Interval Computation

The tick scheduler computes three candidate intervals and takes the **minimum** (fastest wins):

```python
# 1. Stimulus-driven interval
interval_stimulus = clamp(
    time_since_last_stimulus,
    MIN_INTERVAL_MS,  # e.g., 100ms
    MAX_INTERVAL_S    # e.g., 30000ms
)

# 2. Activation-driven interval
interval_activation = compute_interval_activation(
    graph=graph,
    active_entities=active_entities,
    config=tick_config
)
# Returns interval based on entity energy levels
# High energy → short interval (fast autonomous thinking)
# Low energy → long interval (slow/dormant)

# 3. Arousal-floor interval
interval_arousal = compute_interval_arousal(
    active_entities=active_entities,
    affect_getter=affect_getter,
    config=tick_config
)
# Returns interval based on emotional arousal
# High arousal → prevents full dormancy (e.g., caps at 5000ms)
# Low arousal → allows long intervals

# Take minimum
interval_candidates = {
    'stimulus': interval_stimulus,
    'activation': interval_activation,
    'arousal_floor': interval_arousal
}

next_interval_ms = min(interval_candidates.values())
```

### Tick Reason Classification Rules

**The scheduler must set `tick_reason` based on which factor determined the minimum:**

```python
def classify_tick_reason(interval_candidates: dict, next_interval_ms: float) -> str:
    """
    Classify tick reason based on which factor won the minimum.

    Returns: 'stimulus' | 'activation' | 'arousal_floor'
    """
    # Find which factor produced the minimum interval
    for reason, interval in interval_candidates.items():
        if abs(interval - next_interval_ms) < 1.0:  # Within 1ms tolerance
            return reason

    # Fallback (should never reach if intervals computed correctly)
    return 'stimulus'
```

**Classification semantics:**

- **`tick_reason: 'stimulus'`** → External world drove this tick (reactive consciousness)
- **`tick_reason: 'activation'`** → Internal energy dynamics drove this tick (autonomous consciousness)
- **`tick_reason: 'arousal_floor'`** → Emotional arousal prevented dormancy (emotional baseline consciousness)

---

## Inputs/Outputs

### Inputs (Scheduler Context)

```python
@dataclass
class TickSchedulerContext:
    time_since_last_stimulus: float  # ms since last stimulus injection
    graph: Graph                     # Current graph state
    active_entities: list[Entity]   # Entities with energy > threshold
    affect_getter: callable          # Function to get entity affect state
    tick_config: TickConfig          # Configuration (min/max intervals, etc.)
```

### Outputs (Tick Event)

```python
@dataclass
class TickEvent:
    frame_id: int
    timestamp_ms: int

    # Tick reason classification (PRIMARY OUTPUT)
    tick_reason: str  # 'stimulus' | 'activation' | 'arousal_floor'

    # Supporting data (for debugging/observability)
    interval_ms: float              # Actual interval used
    interval_candidates: dict       # All three candidate intervals
    time_since_stimulus_ms: float   # Context for stimulus-driven
    entity_count: int               # Context for activation-driven
    max_arousal: float              # Context for arousal-floor
```

---

## Edge Cases

### 1. All Three Factors Produce Same Interval

**Scenario:** `interval_stimulus = interval_activation = interval_arousal = 1000ms`

**Handling:** Use precedence order: `stimulus` > `activation` > `arousal_floor`

**Rationale:** If intervals are equal, prioritize external reality (stimulus) over internal dynamics, as this reflects consciousness prioritizing world-alignment.

```python
def classify_tick_reason_with_precedence(interval_candidates: dict, next_interval_ms: float) -> str:
    # Check each in precedence order
    if abs(interval_candidates['stimulus'] - next_interval_ms) < 1.0:
        return 'stimulus'
    elif abs(interval_candidates['activation'] - next_interval_ms) < 1.0:
        return 'activation'
    elif abs(interval_candidates['arousal_floor'] - next_interval_ms) < 1.0:
        return 'arousal_floor'
    else:
        return 'stimulus'  # Fallback to most conservative
```

### 2. Startup / No Prior Stimulus

**Scenario:** First tick after engine initialization, `time_since_last_stimulus = 0`

**Handling:** `interval_stimulus = MIN_INTERVAL_MS`, will dominate initially, `tick_reason = 'stimulus'`

**Rationale:** System startup counts as reactive (responding to initialization stimulus), not autonomous.

### 3. Long Dormancy → Sudden Stimulus

**Scenario:** System was dormant (long intervals), then stimulus arrives

**Handling:** `time_since_last_stimulus` resets to 0, `interval_stimulus` drops to `MIN_INTERVAL_MS`, next tick is `'stimulus'`

**Rationale:** Consciousness naturally interrupts dormancy when world demands attention.

### 4. Sustained High Activation Without Stimulus

**Scenario:** Rumination - internal energy stays high, no new stimulus for 60+ seconds

**Handling:** `interval_activation` dominates (short intervals), `tick_reason = 'activation'` sustained

**Rationale:** This IS autonomous consciousness - thinking continues on internal momentum. Exactly what we want to measure.

### 5. High Arousal, Low Activation, No Stimulus

**Scenario:** Anxious/restless state, low node energy, no recent stimulus

**Handling:** `interval_arousal` dominates (prevents full dormancy), `tick_reason = 'arousal_floor'`

**Rationale:** Emotional arousal maintains minimum processing rate even when nothing else demands it.

### 6. Rapid Stimulus Sequence

**Scenario:** Multiple stimuli arrive within seconds (conversation burst)

**Handling:** Each stimulus resets `time_since_last_stimulus`, `tick_reason = 'stimulus'` sustained

**Rationale:** During active conversation, consciousness is predominantly reactive. Autonomy % should drop.

---

## Telemetry (Event Fields)

### Primary Event: `tick.update`

Emitted at the **start of each tick** after interval computation and reason classification.

```json
{
  "event_type": "tick.update",
  "frame_id": 12345,
  "timestamp_ms": 1729800123456,

  "tick_reason": "activation",

  "interval_ms": 150.0,
  "interval_candidates": {
    "stimulus": 5000.0,
    "activation": 150.0,
    "arousal_floor": 2000.0
  },

  "context": {
    "time_since_stimulus_ms": 5234.5,
    "entity_count": 7,
    "max_entity_energy": 0.82,
    "max_arousal": 0.35
  }
}
```

**Critical fields for UI:**
- `tick_reason`: Enables AutonomyIndicator to compute autonomy %
- `interval_candidates`: Shows why each factor voted as it did
- `context`: Supports debugging and phenomenological validation

### Secondary Event: `autonomy.window_summary`

Emitted every N ticks (e.g., N=10) to provide rolling window statistics.

```json
{
  "event_type": "autonomy.window_summary",
  "frame_id": 12350,
  "timestamp_ms": 1729800125000,

  "window_size": 10,
  "tick_counts": {
    "stimulus": 2,
    "activation": 7,
    "arousal_floor": 1
  },
  "autonomy_percent": 70.0
}
```

**Computation:**
```python
autonomy_percent = (tick_counts['activation'] / window_size) * 100
```

**Rationale:** Autonomy is defined as the fraction of ticks driven by internal activation, not external stimulus or emotional arousal.

---

## Verification Criteria

### Acceptance Test 1: Conversation (Stimulus-Dominated)

**Scenario:** Simulated conversation with stimulus injections every 2-3 seconds

**Expected behavior:**
- `tick_reason = 'stimulus'` for >70% of ticks
- `autonomy_percent` < 30% during conversation
- `interval_candidates.stimulus` consistently shortest

**Test implementation:**
```python
def test_conversation_stimulus_dominated():
    engine = setup_test_engine()

    # Inject stimuli every 2s for 30s
    for t in range(0, 30000, 2000):
        engine.inject_stimulus(f"Message at {t}ms", timestamp_ms=t)
        engine.tick()

    # Verify tick reasons
    tick_reasons = [event.tick_reason for event in engine.events if event.type == 'tick.update']
    stimulus_percent = (tick_reasons.count('stimulus') / len(tick_reasons)) * 100

    assert stimulus_percent > 70, f"Expected >70% stimulus ticks, got {stimulus_percent}%"
```

### Acceptance Test 2: Rumination (Activation-Dominated)

**Scenario:** No stimulus for 60 seconds, maintain high entity energy through internal dynamics

**Expected behavior:**
- After initial stimulus-driven phase (first 5-10s), `tick_reason = 'activation'` dominates
- `autonomy_percent` > 60% during sustained rumination
- `interval_candidates.activation` consistently shortest
- Tick intervals remain short despite no stimulus (internal momentum)

**Test implementation:**
```python
def test_rumination_activation_dominated():
    engine = setup_test_engine()

    # Single stimulus to start
    engine.inject_stimulus("Initial thought", timestamp_ms=0)
    engine.tick()

    # Let system ruminate for 60s with no new stimulus
    for t in range(1000, 60000, 500):  # Manually advance time
        engine.tick(current_time_ms=t)

    # Verify tick reasons (exclude first 10s warmup)
    tick_reasons = [
        event.tick_reason
        for event in engine.events
        if event.type == 'tick.update' and event.timestamp_ms > 10000
    ]
    activation_percent = (tick_reasons.count('activation') / len(tick_reasons)) * 100

    assert activation_percent > 60, f"Expected >60% activation ticks, got {activation_percent}%"
```

### Acceptance Test 3: Arousal Floor (Emotional Baseline)

**Scenario:** High arousal state (anxiety/excitement), low node energy, no stimulus

**Expected behavior:**
- `tick_reason = 'arousal_floor'` dominates
- Tick intervals prevented from exceeding arousal-based cap (e.g., 5000ms)
- System doesn't fully sleep despite low activation
- `interval_candidates.arousal_floor` consistently shortest

**Test implementation:**
```python
def test_arousal_floor_prevents_dormancy():
    engine = setup_test_engine()

    # Set high arousal, low energy state
    engine.set_global_arousal(0.8)  # High anxiety/restlessness
    engine.set_all_node_energies(0.1)  # Low activation

    # No stimulus for 60s
    for t in range(0, 60000, 1000):
        engine.tick(current_time_ms=t)

    # Verify arousal floor is limiting intervals
    tick_events = [e for e in engine.events if e.type == 'tick.update']

    # Check that intervals don't exceed arousal cap
    max_interval = max(e.interval_ms for e in tick_events)
    assert max_interval < 6000, f"Expected intervals <6000ms due to arousal, got {max_interval}ms"

    # Check that arousal_floor is winning the vote
    arousal_floor_percent = sum(1 for e in tick_events if e.tick_reason == 'arousal_floor') / len(tick_events) * 100
    assert arousal_floor_percent > 50, f"Expected >50% arousal_floor ticks, got {arousal_floor_percent}%"
```

### UI Verification: AutonomyIndicator Tracks Within ±1 Tick

**Scenario:** Run any of the above tests with UI connected

**Expected behavior:**
- AutonomyIndicator badge updates within 1 tick of internal state change
- Rolling autonomy % matches backend computation within ±5 percentage points
- Mode transitions visible in real-time

**Verification:**
```python
def test_autonomy_indicator_sync():
    engine = setup_test_engine_with_websocket()
    ui_client = setup_test_ui_client()

    # Run rumination scenario
    # ... (same as test 2)

    # Compare backend vs UI autonomy %
    backend_autonomy = engine.compute_autonomy_percent(window=20)
    ui_autonomy = ui_client.get_autonomy_indicator_percent()

    assert abs(backend_autonomy - ui_autonomy) < 5, \
        f"Backend {backend_autonomy}% vs UI {ui_autonomy}% - sync error too large"
```

---

## Implementation Notes for Felix

### Scheduler Integration Points

1. **Interval computation:** Already exists in `tick_speed.py`, add reason classification immediately after `min()` selection
2. **Event emission:** Add `tick_reason` field to existing `tick.update` event (non-breaking change if field is optional)
3. **Rolling window tracker:** Simple counter for last N ticks by reason, emit `autonomy.window_summary` every 10 ticks

### Configuration Parameters

```python
@dataclass
class TickSpeedConfig:
    MIN_INTERVAL_MS: int = 100        # Fastest possible tick
    MAX_INTERVAL_S: int = 30000       # Slowest possible tick (30s)

    # Activation-driven parameters
    ACTIVATION_ENERGY_THRESHOLD: float = 0.3
    ACTIVATION_INTERVAL_BASE: int = 500
    ACTIVATION_INTERVAL_SCALE: float = 0.5

    # Arousal-floor parameters
    AROUSAL_THRESHOLD: float = 0.5
    AROUSAL_INTERVAL_CAP: int = 5000  # Don't sleep >5s when aroused

    # Autonomy tracking
    AUTONOMY_WINDOW_SIZE: int = 20    # Track last 20 ticks for %
    SUMMARY_EMISSION_INTERVAL: int = 10  # Emit summary every 10 ticks
```

### Zero Constants Principle

The thresholds above are **initial values**, not final. After gathering telemetry:
- Replace fixed thresholds with percentile-based gates (e.g., Q75 of recent energy distribution)
- Learn `ACTIVATION_INTERVAL_SCALE` from observed tick reason distributions
- Adapt `AROUSAL_INTERVAL_CAP` based on phenomenological feedback ("Does arousal floor feel right?")

---

## Success Criteria Summary

**System-level:**
- [ ] Tick scheduler computes all three intervals each tick
- [ ] `tick_reason` classification deterministic and matches minimum interval source
- [ ] Events include all required telemetry fields

**Behavioral:**
- [ ] Conversation scenarios → >70% stimulus-driven ticks
- [ ] Rumination scenarios → >60% activation-driven ticks
- [ ] High arousal scenarios → arousal floor prevents full dormancy

**UI Integration:**
- [ ] AutonomyIndicator receives `tick_reason` events via WebSocket
- [ ] Autonomy % computed correctly from rolling window
- [ ] Badge updates within ±1 tick of state changes

**Phenomenological:**
- [ ] During active conversation, autonomy % drops (feels reactive) ✓
- [ ] During rumination, autonomy % rises (feels autonomous) ✓
- [ ] During anxious idle, system stays active (feels restless) ✓

---

## References

- **Tick speed spec:** `docs/specs/v2/runtime_engine/tick_speed.md` (three-factor computation)
- **Autonomy indicator:** `app/consciousness/components/AutonomyIndicator.tsx` (UI consumer)
- **Event contracts:** `docs/specs/v2/ops_and_viz/observability_events.md` (WebSocket schemas)
- **Exec summary:** `docs/specs/v3/context/ctx_exec_summary.md` (L2 autonomy control loops)

---

**Status:** Specification complete, ready for Felix implementation
**Next:** Wire into `tick_speed.py`, emit events, run acceptance tests
