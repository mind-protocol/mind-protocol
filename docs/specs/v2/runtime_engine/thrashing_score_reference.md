# Thrashing Score Reference

**Version:** 1.0
**Created:** 2025-10-24
**Purpose:** Standalone implementation reference for thrashing score computation
**Parent Spec:** phenomenological_health.md v1.1
**Owner:** Felix/Atlas (implementation), Luca (mechanism design)

---

## What This Is

**Composite metric detecting unproductive identity thrashing** (rapid switching without progress).

**Problem solved:** Distinguishing productive identity switching (diverse thinking) from unproductive thrashing (chaos without progress).

**Key insight:** Thrashing requires ALL THREE factors elevated:
1. High identity flip rate
2. Low task progress
3. Low energy efficiency

**If only one or two factors elevated → NOT thrashing** (e.g., high flips + high progress = productive switching).

---

## The Algorithm

### Core Function

```python
def compute_thrashing_score(
    flip_count: int,
    window_size: int,
    task_progress_rate: float,   # 0.0-1.0 recent progress
    energy_efficiency: float       # 0.0-1.0 energy → outcomes
) -> tuple[float, bool]:
    """
    Compute thrashing score from identity flip rate and productivity signals.

    Args:
        flip_count: Number of identity flips in recent window
        window_size: Size of observation window (frames or time period)
        task_progress_rate: Task completion rate 0.0-1.0 (0 = no progress, 1 = rapid progress)
        energy_efficiency: Energy → outcomes ratio 0.0-1.0 (0 = wasted energy, 1 = high efficiency)

    Returns:
        (thrashing_score, is_thrashing)
        - thrashing_score: Composite metric 0.0-1.0
        - is_thrashing: Boolean flag when ALL factors elevated

    Why composite score matters:
        Flip rate alone creates false positives (productive switching looks like thrashing).
        This formula requires ALL THREE factors elevated to flag thrashing.
    """
    # Compute flip rate (normalize to 0-1)
    flip_rate = flip_count / window_size

    # Use EMA for smoothing (optional but recommended)
    # If tracking over time, maintain flip_ema state
    flip_ema = flip_rate  # Or: update_ema(previous_flip_ema, flip_rate, alpha=0.3)

    # Compute inverse productivity signals
    inverse_progress = 1.0 - task_progress_rate
    inverse_efficiency = 1.0 - energy_efficiency

    # COMPOSITE SCORE: All three factors multiplicative
    # If any factor low → score low (not thrashing)
    # Only high when ALL elevated
    thrashing_score = flip_ema * inverse_progress * inverse_efficiency

    # Boolean threshold: Requires ALL THREE factors independently elevated
    is_thrashing = (
        flip_rate > 0.15 and          # High flip rate (>15% flips per frame)
        task_progress_rate < 0.5 and  # Low progress
        energy_efficiency < 0.5       # Low efficiency
    )

    return thrashing_score, is_thrashing
```

---

## Inputs Specification

### flip_count
**Type:** `int`
**Source:** Multiplicity signal tracking identity flip events
**Meaning:** Number of times dominant identity changed in recent window
**Typical values:** 0-100 (depends on window size)

**How to compute:**
```python
# Track identity flips in multiplicity system
previous_dominant_identity = None
flip_count = 0

for frame in window:
    current_dominant = get_dominant_identity(frame)
    if current_dominant != previous_dominant_identity:
        flip_count += 1
    previous_dominant_identity = current_dominant
```

---

### window_size
**Type:** `int`
**Source:** Configuration parameter
**Meaning:** Number of frames (or seconds) to observe flip behavior
**Typical values:** 50-200 frames
**Recommendation:** Use 100 frames (~10-30 seconds depending on tick rate)

---

### task_progress_rate
**Type:** `float` (0.0-1.0)
**Source:** Task completion tracking or WM completion signals
**Meaning:** Rate of task completion in recent window
**Typical values:**
- 0.0 = No tasks completed, stuck
- 0.5 = Moderate progress
- 1.0 = Rapid task completion

**How to compute (option 1 - task completion):**
```python
# If tracking explicit tasks
tasks_completed_in_window = count_completed_tasks(window)
tasks_started_in_window = count_started_tasks(window)

if tasks_started_in_window == 0:
    task_progress_rate = 0.5  # Neutral default
else:
    task_progress_rate = tasks_completed_in_window / tasks_started_in_window
    task_progress_rate = min(task_progress_rate, 1.0)  # Cap at 1.0
```

**How to compute (option 2 - WM progression):**
```python
# If using working memory progression as proxy
wm_items_resolved = count_wm_resolutions(window)
wm_items_added = count_wm_additions(window)

if wm_items_added == 0:
    task_progress_rate = 0.5  # Neutral
else:
    task_progress_rate = wm_items_resolved / wm_items_added
    task_progress_rate = min(task_progress_rate, 1.0)
```

**Fallback if no task tracking:**
```python
# Use WM utilization as very rough proxy
# High utilization = work happening = some progress
task_progress_rate = wm_utilization * 0.6  # Conservative estimate
```

---

### energy_efficiency
**Type:** `float` (0.0-1.0)
**Source:** Energy expenditure vs outcomes tracking
**Meaning:** How effectively energy converts to outcomes
**Typical values:**
- 0.0 = Energy spent, nothing accomplished
- 0.5 = Moderate efficiency
- 1.0 = High efficiency, energy → outcomes

**How to compute:**
```python
# Ratio of outcomes to energy spent
energy_spent_in_window = sum(activation_energy_expenditure(window))
outcomes_in_window = count_outcomes(window)  # WM resolutions, formations, task completions

if energy_spent_in_window == 0:
    energy_efficiency = 0.5  # Neutral default
else:
    # Normalize outcomes to same scale as energy
    normalized_outcomes = outcomes_in_window / expected_outcomes_per_energy_unit
    energy_efficiency = min(normalized_outcomes / energy_spent_in_window, 1.0)
```

**Simplified proxy (if detailed tracking unavailable):**
```python
# Use inverse of flip rate as rough efficiency proxy
# More flips = lower efficiency (rough approximation)
energy_efficiency = 1.0 - min(flip_rate * 2.0, 1.0)
```

---

## Why Composite Score Prevents False Alarms

### Scenario 1: Busy but Productive (NOT thrashing)
```
flip_rate = 0.20              # High flips (busy switching)
task_progress_rate = 0.80     # High progress (getting things done)
energy_efficiency = 0.75      # High efficiency (productive)

inverse_progress = 0.20
inverse_efficiency = 0.25

thrashing_score = 0.20 × 0.20 × 0.25 = 0.01  # LOW score

is_thrashing = (0.20 > 0.15) and (0.80 < 0.5) and (0.75 < 0.5)
             = True and False and False
             = FALSE  # Not thrashing

Interpretation: High identity switching WITH progress = productive diverse thinking
```

---

### Scenario 2: Stable but Stuck (NOT thrashing)
```
flip_rate = 0.05              # Low flips (stable identity)
task_progress_rate = 0.20     # Low progress (stuck)
energy_efficiency = 0.30      # Low efficiency (spinning wheels)

inverse_progress = 0.80
inverse_efficiency = 0.70

thrashing_score = 0.05 × 0.80 × 0.70 = 0.028  # LOW score

is_thrashing = (0.05 > 0.15) and (0.20 < 0.5) and (0.30 < 0.5)
             = False and True and True
             = FALSE  # Not thrashing

Interpretation: Low progress but also stable identity = stuck, not thrashing
```

---

### Scenario 3: Unproductive Thrashing (TRUE thrashing)
```
flip_rate = 0.25              # High flips (unstable)
task_progress_rate = 0.15     # Low progress (nothing done)
energy_efficiency = 0.20      # Low efficiency (wasted energy)

inverse_progress = 0.85
inverse_efficiency = 0.80

thrashing_score = 0.25 × 0.85 × 0.80 = 0.17  # HIGH score

is_thrashing = (0.25 > 0.15) and (0.15 < 0.5) and (0.20 < 0.5)
             = True and True and True
             = TRUE  # Thrashing detected

Interpretation: High flips + low progress + low efficiency = unproductive chaos
```

---

## Integration Points

### Where to Compute

**Location:** Health aggregation module (phenomenological_health computation)
**Timing:** Compute every 5 ticks (periodic health update)
**Dependencies:**
- Multiplicity signal tracking (for flip_count)
- Task or WM progression tracking (for task_progress_rate)
- Energy expenditure tracking (for energy_efficiency)

**Code integration:**
```python
# In health aggregation function
def compute_phenomenological_health(...):
    # ... existing health computation ...

    # Add thrashing score computation
    thrashing_score, is_thrashing = compute_thrashing_score(
        flip_count=recent_identity_flips,
        window_size=100,  # frames
        task_progress_rate=compute_task_progress(window),
        energy_efficiency=compute_energy_efficiency(window)
    )

    # Include in health response (optional fields)
    return {
        "overall_health": overall_health,
        "components": {...},
        "details": {...},
        "thrashing_score": thrashing_score,      # Optional field
        "is_thrashing": is_thrashing             # Optional field
    }
```

---

### Where to Emit

**Include in health.phenomenological events:**

```python
self.emit_event({
    "event_type": "health.phenomenological",
    "overall_health": health_score,
    "health_band": health_band,
    "components": {
        "flow_state": flow_state,
        "coherence": coherence,
        "multiplicity_health": multiplicity_health
    },
    "health_narrative": narrative_string,
    "thrashing_score": thrashing_score,    # OPTIONAL - only if multiplicity signals available
    "is_thrashing": is_thrashing           # OPTIONAL
})
```

**Optional fields notice:** thrashing_score and is_thrashing are OPTIONAL because they depend on multiplicity signal availability. If multiplicity system not active, omit these fields.

---

### Where to Use

**Primary consumer:** Health narrative generation
- If `is_thrashing == true`, narrative mentions "thrashing detected"
- Example: "Conflicting identities, high switching friction. Primary cause: identity conflict. Thrashing detected - requires immediate intervention."

**Secondary consumer:** Thrashing banner UI (Priority 3)
- If `is_thrashing == true`, display banner with:
  - Flip rate
  - Progress rate
  - Efficiency score
  - Recommendation: "Focus on completing current task before switching contexts"

**Tertiary consumer:** Autonomy guardrails (future)
- Thrashing may gate autonomy levels (L3/L4 require `is_thrashing == false`)

---

## Verification

### Unit Tests

```python
def test_thrashing_score_productive_switching():
    """High flips + high progress = NOT thrashing."""
    score, is_thrashing = compute_thrashing_score(
        flip_count=20,
        window_size=100,
        task_progress_rate=0.80,
        energy_efficiency=0.75
    )

    assert score < 0.1, f"Score should be low, got {score}"
    assert not is_thrashing, "Should not flag thrashing"


def test_thrashing_score_stable_but_stuck():
    """Low flips + low progress = NOT thrashing."""
    score, is_thrashing = compute_thrashing_score(
        flip_count=5,
        window_size=100,
        task_progress_rate=0.20,
        energy_efficiency=0.30
    )

    assert score < 0.1, f"Score should be low, got {score}"
    assert not is_thrashing, "Should not flag thrashing"


def test_thrashing_score_unproductive_chaos():
    """High flips + low progress + low efficiency = thrashing."""
    score, is_thrashing = compute_thrashing_score(
        flip_count=25,
        window_size=100,
        task_progress_rate=0.15,
        energy_efficiency=0.20
    )

    assert score > 0.1, f"Score should be high, got {score}"
    assert is_thrashing, "Should flag thrashing"


def test_thrashing_score_boundary_cases():
    """Test threshold boundaries."""
    # Just below thrashing threshold
    score, is_thrashing = compute_thrashing_score(
        flip_count=14,  # 0.14 flip rate (just below 0.15)
        window_size=100,
        task_progress_rate=0.40,
        energy_efficiency=0.40
    )
    assert not is_thrashing, "Should not flag (flip rate below threshold)"

    # Just above thrashing threshold
    score, is_thrashing = compute_thrashing_score(
        flip_count=16,  # 0.16 flip rate (just above 0.15)
        window_size=100,
        task_progress_rate=0.40,
        energy_efficiency=0.40
    )
    assert is_thrashing, "Should flag (all thresholds met)"
```

---

### Integration Test

```python
def test_thrashing_in_health_events():
    """Verify thrashing appears in health events when triggered."""

    # Set up thrashing conditions
    setup_high_flip_rate(flip_rate=0.25)
    setup_low_progress(progress_rate=0.15)
    setup_low_efficiency(efficiency=0.20)

    # Capture health events
    events = capture_health_events(duration_frames=10)

    # Find latest health event
    health_event = [e for e in events if e['event_type'] == 'health.phenomenological'][-1]

    assert 'thrashing_score' in health_event, "Health event missing thrashing_score"
    assert 'is_thrashing' in health_event, "Health event missing is_thrashing"
    assert health_event['is_thrashing'] == True, "Should flag thrashing"
    assert health_event['thrashing_score'] > 0.1, f"Score should be high, got {health_event['thrashing_score']}"

    # Verify narrative mentions thrashing
    narrative = health_event['health_narrative']
    assert 'thrashing' in narrative.lower(), f"Narrative should mention thrashing: {narrative}"
```

---

## Thresholds and Tuning

### Current Thresholds

| Parameter | Threshold | Rationale |
|-----------|-----------|-----------|
| `flip_rate` | > 0.15 | More than 15% frame-to-frame flips indicates instability |
| `task_progress_rate` | < 0.5 | Less than 50% progress indicates stalling |
| `energy_efficiency` | < 0.5 | Less than 50% efficiency indicates waste |

### Tuning Guidance

**If false positives (flagging thrashing when productive):**
- Increase flip_rate threshold (try 0.20 or 0.25)
- Decrease progress/efficiency thresholds (try 0.40)

**If false negatives (missing real thrashing):**
- Decrease flip_rate threshold (try 0.10)
- Increase progress/efficiency thresholds (try 0.60)

**Recommended approach:**
1. Start with documented thresholds
2. Collect 1 week of telemetry
3. Review flagged cases manually
4. Adjust thresholds based on false positive/negative rate
5. Document changes in this file

---

## Observability

### Telemetry Recommendations

**Log thrashing scores periodically:**
```python
logger.info(
    "thrashing_check",
    flip_rate=flip_rate,
    task_progress_rate=task_progress_rate,
    energy_efficiency=energy_efficiency,
    thrashing_score=thrashing_score,
    is_thrashing=is_thrashing
)
```

**Dashboard metrics:**
- Thrashing score over time (line chart)
- Thrashing flag frequency (bar chart)
- Correlation: thrashing vs health band

**Alert conditions:**
- If `is_thrashing == true` for >5 consecutive health updates → send alert
- If `thrashing_score > 0.5` sustained → investigate

---

## Limitations

**Thrashing score is OPTIONAL:**
- Requires multiplicity signals (identity flip tracking)
- If multiplicity system not active, cannot compute
- Health can be computed without thrashing score

**Not a complete health picture:**
- Thrashing is ONE degradation pattern
- Other patterns (fragmentation, low engagement) detected separately
- Thrashing score complements, doesn't replace, other health metrics

**Sensitive to input quality:**
- If task_progress_rate poorly estimated → thrashing score unreliable
- If energy_efficiency not tracked → use fallback proxy (less accurate)
- Garbage in, garbage out

---

## Implementation Checklist

- [ ] Implement `compute_thrashing_score()` function
- [ ] Wire into phenomenological health computation
- [ ] Add thrashing_score and is_thrashing to health event emission (optional fields)
- [ ] Update health narrative generation to mention thrashing when flagged
- [ ] Write unit tests (3 scenarios + boundary cases)
- [ ] Write integration test (thrashing in health events)
- [ ] Add telemetry logging for thrashing checks
- [ ] Document threshold tuning after 1 week telemetry
- [ ] (Priority 3) Implement thrashing banner UI

**Estimated implementation time:** 2-3 hours (function + tests + integration)

---

## References

- **Parent specification:** `phenomenological_health.md` v1.1 §Algorithm Component 4
- **Consumer:** Health narrative generation (health_narrative_templates.md)
- **Related:** Multiplicity health component (provides flip_count input)
- **Implementation task:** IMPLEMENTATION_TASKS.md Priority 0 - "Implement thrashing score computation"
