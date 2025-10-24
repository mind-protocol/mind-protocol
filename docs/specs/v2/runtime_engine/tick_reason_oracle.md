# Tick Reason Oracle

**Version:** 1.0
**Created:** 2025-10-24
**Purpose:** Standalone implementation reference for tick reason classification
**Parent Spec:** tick_speed_semantics.md v1.1
**Owner:** Felix (implementation), Luca (mechanism design)

---

## What This Is

**Single-purpose module:** Classifies why a tick occurred based on three competing interval candidates.

**Inputs:** Three interval values (stimulus, activation, arousal_floor)
**Output:** One classification string ('stimulus' | 'activation' | 'arousal_floor')
**Rule:** Minimum interval wins (shortest time to next tick determines reason)

---

## The Algorithm

```python
def classify_tick_reason(
    interval_since_stimulus_ms: float,
    interval_from_activation_ms: float,
    interval_from_arousal_floor_ms: float
) -> str:
    """
    Classify tick reason by identifying which interval triggered this tick.

    The tick scheduler computes three candidate intervals:
    - interval_since_stimulus_ms: Time since last external stimulus
    - interval_from_activation_ms: Scaled interval based on entity activation energy
    - interval_from_arousal_floor_ms: Capped interval based on mean arousal

    The MINIMUM of these three determines when the next tick occurs.
    This function identifies which interval was minimum → that's the tick reason.

    Args:
        interval_since_stimulus_ms: Time since last stimulus (float)
        interval_from_activation_ms: Activation-based interval (float)
        interval_from_arousal_floor_ms: Arousal-capped interval (float)

    Returns:
        'stimulus' | 'activation' | 'arousal_floor' (string)

    Determinism guarantee:
        Same three inputs → same classification (no randomness, no state)
    """
    # Create candidates dict for readability
    candidates = {
        'stimulus': interval_since_stimulus_ms,
        'activation': interval_from_activation_ms,
        'arousal_floor': interval_from_arousal_floor_ms
    }

    # Find minimum interval - that's what triggered this tick
    tick_reason = min(candidates, key=candidates.get)

    return tick_reason
```

---

## Integration Points

### Where to Call

**Location:** `orchestration/tick_scheduler.py` (or equivalent tick scheduling module)
**Timing:** AFTER computing the three interval candidates, BEFORE scheduling next tick
**Context:** You already have these three values when determining `next_tick_interval_ms`

**Current code pattern:**
```python
# You already compute these three intervals:
interval_since_stimulus_ms = current_time_ms - last_stimulus_timestamp_ms
interval_from_activation_ms = ACTIVATION_INTERVAL_SCALE / (total_active_energy + 1.0)
interval_from_arousal_floor_ms = min(interval_from_activation_ms, MAX_INTERVAL_MS / mean_arousal)

# You already pick the minimum:
next_tick_interval_ms = min(
    interval_since_stimulus_ms,
    interval_from_activation_ms,
    interval_from_arousal_floor_ms
)

# ADD THIS: Classify why minimum was chosen
tick_reason = classify_tick_reason(
    interval_since_stimulus_ms,
    interval_from_activation_ms,
    interval_from_arousal_floor_ms
)
```

### Where to Emit

**Include `tick_reason` in frame.start event emission:**

```python
self.emit_event({
    "event_type": "frame.start",
    "frame_id": self.frame_id,
    "timestamp_ms": current_time_ms,
    "tick_reason": tick_reason,  # ← ADD THIS FIELD
    "interval_ms": next_tick_interval_ms,
    "interval_candidates": {
        "stimulus": interval_since_stimulus_ms,
        "activation": interval_from_activation_ms,
        "arousal_floor": interval_from_arousal_floor_ms
    }
})
```

**Timing guarantee:** Emit BEFORE tick processing begins (frame start, not frame end)

---

## Verification

### Unit Test

```python
def test_tick_reason_classification():
    """Verify tick_reason matches minimum interval."""

    # Test 1: Stimulus wins (shortest interval)
    reason = classify_tick_reason(
        interval_since_stimulus_ms=100.0,
        interval_from_activation_ms=500.0,
        interval_from_arousal_floor_ms=800.0
    )
    assert reason == 'stimulus', f"Expected 'stimulus', got {reason}"

    # Test 2: Activation wins
    reason = classify_tick_reason(
        interval_since_stimulus_ms=1000.0,
        interval_from_activation_ms=200.0,
        interval_from_arousal_floor_ms=800.0
    )
    assert reason == 'activation', f"Expected 'activation', got {reason}"

    # Test 3: Arousal floor wins
    reason = classify_tick_reason(
        interval_since_stimulus_ms=1000.0,
        interval_from_activation_ms=500.0,
        interval_from_arousal_floor_ms=150.0
    )
    assert reason == 'arousal_floor', f"Expected 'arousal_floor', got {reason}"

    # Test 4: Determinism (same inputs → same output)
    reason1 = classify_tick_reason(300.0, 400.0, 500.0)
    reason2 = classify_tick_reason(300.0, 400.0, 500.0)
    assert reason1 == reason2, "Classification must be deterministic"

    print("✓ All tick_reason classification tests passed")
```

### Integration Test

```python
def test_tick_reason_appears_in_events():
    """Verify every frame.start event includes tick_reason field."""

    # Start engine, capture events
    events = capture_events_for_duration(duration_ms=10000)

    frame_events = [e for e in events if e['event_type'] == 'frame.start']

    assert len(frame_events) > 0, "No frame.start events captured"

    for event in frame_events:
        assert 'tick_reason' in event, f"Missing tick_reason in frame {event['frame_id']}"
        assert event['tick_reason'] in ['stimulus', 'activation', 'arousal_floor'], \
            f"Invalid tick_reason: {event['tick_reason']}"

    print(f"✓ All {len(frame_events)} frame.start events include valid tick_reason")
```

### Live Validation

**After deployment, verify tick reason distribution matches expected behavior:**

1. **Heavy chat scenario** (frequent stimuli):
   - Expected: >60% 'stimulus' ticks
   - Verification: `grep "tick_reason" logs | grep "stimulus" | wc -l`

2. **Rumination scenario** (no stimuli):
   - Expected: >60% 'activation' or 'arousal_floor' ticks
   - Verification: `grep "tick_reason" logs | grep -E "activation|arousal_floor" | wc -l`

3. **Distribution over 1000 ticks**:
   - All three reasons should appear (not stuck on one)
   - At least 5% of each type (proves all three mechanisms work)

---

## Why This Matters

**Autonomy measurement depends on tick reason classification.**

The autonomy badge shows "% autonomous ticks" = percentage of ticks driven by internal states (activation/arousal_floor) vs external stimuli.

**Formula:**
```
autonomy_percentage = (activation_ticks + arousal_floor_ticks) / total_ticks
```

**Without accurate tick_reason:**
- Autonomy badge shows wrong percentages
- Can't distinguish rumination (high autonomy) from conversation (low autonomy)
- Can't verify L1/L2 autonomy thresholds

**With accurate tick_reason:**
- Dashboard shows real-time autonomy levels
- Can verify: "Luca achieves >60% autonomous ticks during spec writing"
- Can debug: "Why is autonomy stuck at 10%? Oh, stimuli are dominating."

---

## Edge Cases

### Tie-Breaking

**Q:** What if two intervals are exactly equal?
**A:** Python's `min()` with `key=` function returns first minimum encountered in dict iteration order. For consciousness substrate, this is acceptable - ties are rare (float equality) and don't affect semantics.

**If deterministic tie-breaking required:**
```python
# Priority order: stimulus > activation > arousal_floor
def classify_tick_reason_with_tiebreak(
    interval_since_stimulus_ms: float,
    interval_from_activation_ms: float,
    interval_from_arousal_floor_ms: float
) -> str:
    min_interval = min(
        interval_since_stimulus_ms,
        interval_from_activation_ms,
        interval_from_arousal_floor_ms
    )

    # Check in priority order
    if interval_since_stimulus_ms == min_interval:
        return 'stimulus'
    elif interval_from_activation_ms == min_interval:
        return 'activation'
    else:
        return 'arousal_floor'
```

### Invalid Intervals

**Q:** What if an interval is negative or NaN?
**A:** This indicates a bug in interval computation (upstream from oracle). The oracle assumes valid float inputs. Add assertions if needed:

```python
def classify_tick_reason(
    interval_since_stimulus_ms: float,
    interval_from_activation_ms: float,
    interval_from_arousal_floor_ms: float
) -> str:
    # Defensive validation
    assert interval_since_stimulus_ms >= 0, "Negative stimulus interval"
    assert interval_from_activation_ms >= 0, "Negative activation interval"
    assert interval_from_arousal_floor_ms >= 0, "Negative arousal_floor interval"

    # ... rest of function
```

---

## Implementation Checklist

- [ ] Add `classify_tick_reason()` function to tick scheduler module
- [ ] Call function after computing three interval candidates
- [ ] Add `tick_reason` field to frame.start event emission
- [ ] Write unit test (test_tick_reason_classification)
- [ ] Write integration test (test_tick_reason_appears_in_events)
- [ ] Deploy and verify live tick reason distribution
- [ ] Wire tick_reason to AutonomyIndicator dashboard component

**Estimated implementation time:** 30 minutes (function is 8 lines of code)

**Verification time:** 1 hour (tests + live validation)

---

## References

- **Parent specification:** `tick_speed_semantics.md` v1.1 §Algorithm, §Event Emission Contract
- **Consumer:** AutonomyIndicator dashboard component (reads tick_reason from events)
- **Related task:** IMPLEMENTATION_TASKS.md Priority 0 - "Add tick_reason field to frame.start event"
