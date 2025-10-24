# Zero Constants Gates Reference

**Version:** 1.0
**Created:** 2025-10-24
**Purpose:** Standalone implementation reference for adaptive threshold gates replacing magic constants
**Parent Spec:** tick_speed_semantics.md v1.1
**Owner:** Felix (implementation), Luca (mechanism design)

---

## What This Is

**Adaptive threshold system** that replaces fixed magic constants with data-driven gates computed from rolling histograms.

**Problem solved:** Fixed thresholds (magic constants) break when workload changes. Adaptive gates learn appropriate thresholds from observed data distribution.

**Example:**
- **Old (brittle):** `ACTIVATION_ENERGY_THRESHOLD = 2.5` ← breaks when entity count changes
- **New (adaptive):** `activation_gate = Q75(rolling_energy_histogram)` ← adjusts automatically

---

## Core Mechanism: QuantileGate

### Implementation

```python
from collections import deque
import numpy as np

class QuantileGate:
    """
    Adaptive threshold computed from rolling histogram percentiles.

    Replaces fixed constants with data-driven gates that adapt to
    workload distribution.
    """

    def __init__(
        self,
        window_size: int = 1000,
        percentile: float = 75.0,
        default_threshold: float = 1.0,
        warmup_frames: int = 100
    ):
        """
        Initialize QuantileGate.

        Args:
            window_size: Number of observations to keep in rolling histogram
            percentile: Percentile to compute (0-100). Higher = more selective.
            default_threshold: Fallback during warmup period
            warmup_frames: Minimum observations before using computed threshold
        """
        self.window_size = window_size
        self.percentile = percentile
        self.default_threshold = default_threshold
        self.warmup_frames = warmup_frames

        # Rolling histogram using deque (efficient for fixed-size window)
        self.history = deque(maxlen=window_size)

    def update(self, value: float) -> None:
        """
        Add new observation to rolling histogram.

        Args:
            value: Observed value (e.g., total_active_energy this frame)
        """
        self.history.append(value)

    def compute_threshold(self) -> float:
        """
        Compute adaptive threshold from rolling histogram.

        Returns:
            Percentile-based threshold, or default during warmup

        Behavior:
            - During warmup (<100 observations): Return default_threshold
            - After warmup: Return specified percentile of rolling histogram
        """
        if len(self.history) < self.warmup_frames:
            # Warmup period: insufficient data, use default
            return self.default_threshold

        # Compute percentile from rolling histogram
        return np.percentile(self.history, self.percentile)

    def should_trigger(self, value: float) -> bool:
        """
        Check if value exceeds adaptive threshold.

        Args:
            value: Current observation to test

        Returns:
            True if value >= computed threshold, False otherwise

        Note: Automatically updates histogram with this observation
        """
        self.update(value)
        threshold = self.compute_threshold()
        return value >= threshold

    def get_stats(self) -> dict:
        """
        Get diagnostic statistics.

        Returns:
            Dict with current threshold, observation count, histogram stats
        """
        if len(self.history) == 0:
            return {
                "threshold": self.default_threshold,
                "observation_count": 0,
                "in_warmup": True
            }

        return {
            "threshold": self.compute_threshold(),
            "observation_count": len(self.history),
            "in_warmup": len(self.history) < self.warmup_frames,
            "histogram_min": min(self.history),
            "histogram_max": max(self.history),
            "histogram_mean": np.mean(self.history),
            "histogram_median": np.median(self.history)
        }
```

---

## Three Gates to Replace

### Gate 1: Activation Energy Threshold (Q75)

**What it replaces:**
```python
# OLD: Fixed constant
ACTIVATION_ENERGY_THRESHOLD = 2.5

# Check if activation should trigger tick
if total_active_energy > ACTIVATION_ENERGY_THRESHOLD:
    trigger_activation_tick()
```

**New adaptive version:**
```python
# Initialize gate (once, at startup)
activation_energy_gate = QuantileGate(
    window_size=1000,
    percentile=75.0,        # Q75 = upper quartile
    default_threshold=2.5,  # Fallback during warmup
    warmup_frames=100
)

# Each frame: update histogram and check threshold
def compute_activation_interval(entities):
    total_active_energy = sum(e.activation_energy for e in entities)

    # Update gate with observation
    activation_energy_gate.update(total_active_energy)

    # Compute adaptive threshold
    threshold = activation_energy_gate.compute_threshold()

    # Use threshold in interval calculation
    if total_active_energy > threshold:
        # High activation energy → short interval
        interval_ms = ACTIVATION_INTERVAL_SCALE / total_active_energy
    else:
        # Low activation energy → longer interval
        interval_ms = MAX_INTERVAL_MS

    return interval_ms
```

**Why Q75 (75th percentile)?**
- Activation ticks should happen when energy is "unusually high"
- Q75 means top 25% of energy observations trigger activation
- Balances responsiveness (not too rare) with selectivity (not every frame)

---

### Gate 2: Arousal Interval Cap (Q90)

**What it replaces:**
```python
# OLD: Fixed constant (actually already adaptive via mean_arousal, but capped by constant)
MAX_INTERVAL_MS = 5000  # ← This was the magic constant

# Apply arousal-based cap
interval_from_arousal_floor_ms = min(
    interval_from_activation_ms,
    MAX_INTERVAL_MS / mean_arousal
)
```

**New adaptive version:**
```python
# Initialize gate (once, at startup)
arousal_interval_gate = QuantileGate(
    window_size=1000,
    percentile=90.0,        # Q90 = 90th percentile (stricter than Q75)
    default_threshold=5000.0,  # Fallback during warmup (old MAX_INTERVAL_MS)
    warmup_frames=100
)

# Each frame: update histogram and compute cap
def compute_arousal_interval_cap(mean_arousal):
    # Update gate with mean arousal observation
    arousal_interval_gate.update(mean_arousal)

    # Compute adaptive cap
    max_interval_ms = arousal_interval_gate.compute_threshold()

    # Apply cap
    interval_from_arousal_floor_ms = max_interval_ms / mean_arousal

    return interval_from_arousal_floor_ms
```

**Why Q90 (90th percentile)?**
- Arousal floor should only cap interval when arousal is "very high"
- Q90 means only top 10% of arousal observations trigger capping
- More selective than Q75 (arousal cap is safety mechanism, not primary driver)

---

### Gate 3: Activation Interval Scale (EMA-based adaptation)

**What it replaces:**
```python
# OLD: Fixed constant
ACTIVATION_INTERVAL_SCALE = 500.0

# Compute activation interval
interval_from_activation_ms = ACTIVATION_INTERVAL_SCALE / (total_active_energy + 1.0)
```

**New adaptive version:**
```python
# Initialize EMA tracker (once, at startup)
class AdaptiveIntervalScale:
    """
    Adapts ACTIVATION_INTERVAL_SCALE based on tick reason distribution.

    Goal: Achieve target distribution (40-60% activation ticks, 20-40% stimulus, 20-40% arousal).
    Method: If activation ticks too frequent → increase scale (longer intervals).
             If activation ticks too rare → decrease scale (shorter intervals).
    """

    def __init__(self, initial_scale=500.0, target_activation_pct=0.50, ema_alpha=0.05):
        self.scale = initial_scale
        self.target_activation_pct = target_activation_pct
        self.ema_alpha = ema_alpha

        # Track tick reason distribution
        self.tick_reason_ema = {
            'stimulus': 0.33,
            'activation': 0.33,
            'arousal_floor': 0.33
        }

    def update(self, tick_reason: str):
        """Update tick reason distribution EMA."""
        # Decay all reasons
        for reason in self.tick_reason_ema:
            self.tick_reason_ema[reason] *= (1 - self.ema_alpha)

        # Boost observed reason
        self.tick_reason_ema[tick_reason] += self.ema_alpha

    def adapt_scale(self):
        """
        Adjust scale based on tick reason distribution.

        If activation % too high → increase scale (make activation ticks rarer)
        If activation % too low → decrease scale (make activation ticks more frequent)
        """
        activation_pct = self.tick_reason_ema['activation']
        error = activation_pct - self.target_activation_pct

        # Adjustment factor (proportional to error)
        adjustment = 1.0 + (error * 0.1)  # 10% adjustment per 100% error

        # Update scale
        self.scale *= adjustment

        # Clamp to reasonable range
        self.scale = max(100.0, min(self.scale, 2000.0))

    def get_scale(self) -> float:
        """Get current adaptive scale."""
        return self.scale

# Usage
adaptive_scale = AdaptiveIntervalScale()

# Each frame
def compute_activation_interval(entities, tick_reason):
    # Update distribution tracker
    adaptive_scale.update(tick_reason)

    # Adapt scale (every 10 frames to avoid oscillation)
    if frame_id % 10 == 0:
        adaptive_scale.adapt_scale()

    # Use adaptive scale
    scale = adaptive_scale.get_scale()
    total_active_energy = sum(e.activation_energy for e in entities)
    interval_ms = scale / (total_active_energy + 1.0)

    return interval_ms
```

**Why EMA-based adaptation?**
- ACTIVATION_INTERVAL_SCALE affects tick reason distribution
- Goal: Balance tick reasons (40-60% activation, not 100% or 0%)
- EMA tracker measures distribution, adapts scale to hit target
- Prevents "all activation" or "all stimulus" degenerate cases

---

## Implementation Phases

### Phase 1: Telemetry Collection (Week 1)

**Don't implement gates yet**—collect baseline data first.

```python
# Add telemetry logging to tick scheduler
logger.info(
    "tick_constants_telemetry",
    frame_id=frame_id,
    total_active_energy=total_active_energy,
    mean_arousal=mean_arousal,
    tick_reason=tick_reason,
    interval_ms=interval_ms
)
```

**Collect for 1 week (10K+ ticks) to understand:**
- What's the distribution of total_active_energy?
- What's the distribution of mean_arousal?
- What's the distribution of tick_reason?
- Are current constants appropriate for typical workload?

---

### Phase 2: QuantileGate Implementation (Week 2)

**Implement gates with telemetry comparison:**

```python
# Compute BOTH old and new thresholds
old_threshold = ACTIVATION_ENERGY_THRESHOLD  # Fixed constant
new_threshold = activation_energy_gate.compute_threshold()  # Adaptive

# Log comparison
logger.info(
    "gate_comparison",
    old_threshold=old_threshold,
    new_threshold=new_threshold,
    current_value=total_active_energy,
    would_trigger_old=total_active_energy > old_threshold,
    would_trigger_new=total_active_energy > new_threshold
)

# Use NEW threshold for actual decision (gates now live)
if total_active_energy > new_threshold:
    trigger_activation()
```

**Monitor for 1 week:**
- Do adaptive thresholds behave reasonably?
- Do they converge to stable values or oscillate?
- Are there edge cases (spikes, drops)?

---

### Phase 3: Scale Adaptation (Week 3)

**Implement adaptive scale with distribution targeting:**

```python
# Each frame
adaptive_scale.update(tick_reason)

if frame_id % 10 == 0:
    adaptive_scale.adapt_scale()

# Log distribution
logger.info(
    "tick_distribution",
    activation_pct=adaptive_scale.tick_reason_ema['activation'],
    stimulus_pct=adaptive_scale.tick_reason_ema['stimulus'],
    arousal_floor_pct=adaptive_scale.tick_reason_ema['arousal_floor'],
    current_scale=adaptive_scale.scale
)
```

**Monitor for 1 week:**
- Does scale adapt to hit target distribution?
- Does distribution stabilize or oscillate?
- Are adjustments too aggressive or too conservative?

---

## Verification Criteria

### Convergence Test

**After 1 hour of mixed workload, adaptive thresholds should converge:**

```python
def test_zero_constants_convergence():
    """
    Acceptance test: Verify gates converge over 1-hour mixed workload.

    Mixed workload:
    - 30 min heavy chat (frequent stimuli)
    - 30 min rumination (no stimuli)
    """
    # Run system for 1 hour
    run_mixed_workload(duration_minutes=60)

    # Check gate convergence
    activation_stats = activation_energy_gate.get_stats()
    arousal_stats = arousal_interval_gate.get_stats()

    # Verify warmup complete
    assert activation_stats['observation_count'] >= 100, "Activation gate warmup incomplete"
    assert arousal_stats['observation_count'] >= 100, "Arousal gate warmup incomplete"

    # Verify thresholds are reasonable (not at defaults)
    assert activation_stats['threshold'] != activation_energy_gate.default_threshold, \
        "Activation gate still at default threshold"
    assert arousal_stats['threshold'] != arousal_interval_gate.default_threshold, \
        "Arousal gate still at default threshold"

    # Verify thresholds within reasonable range
    assert 0.5 < activation_stats['threshold'] < 10.0, \
        f"Activation threshold unreasonable: {activation_stats['threshold']}"
    assert 1000.0 < arousal_stats['threshold'] < 10000.0, \
        f"Arousal threshold unreasonable: {arousal_stats['threshold']}"

    print("✓ Zero constants gates converged successfully")
```

---

### Distribution Balance Test

**After adaptation, tick reason distribution should be balanced:**

```python
def test_tick_reason_distribution_balance():
    """
    Verify adaptive scale achieves target tick reason distribution.

    Target: 40-60% activation, 20-40% stimulus, 20-40% arousal_floor
    """
    # Run for 1000 ticks
    run_system(num_ticks=1000)

    # Get distribution
    distribution = adaptive_scale.tick_reason_ema

    # Verify balance
    assert 0.40 <= distribution['activation'] <= 0.60, \
        f"Activation % out of range: {distribution['activation']}"
    assert 0.20 <= distribution['stimulus'] <= 0.40, \
        f"Stimulus % out of range: {distribution['stimulus']}"
    assert 0.20 <= distribution['arousal_floor'] <= 0.40, \
        f"Arousal floor % out of range: {distribution['arousal_floor']}"

    print(f"✓ Tick distribution balanced: {distribution}")
```

---

## Observability

### Dashboard Metrics

**Track gate behavior over time:**

1. **Activation Energy Gate**
   - Current threshold vs default (line chart)
   - Observation count (gauge)
   - Histogram distribution (histogram chart)

2. **Arousal Interval Gate**
   - Current cap vs default (line chart)
   - Observation count (gauge)

3. **Adaptive Scale**
   - Current scale vs initial (line chart)
   - Tick reason distribution (pie chart)
   - Distribution over time (stacked area chart)

4. **Comparison Metrics**
   - Old threshold vs new threshold (line comparison)
   - Decision agreement % (how often old/new agree)

---

### Telemetry Logging

```python
# Every frame
logger.info(
    "zero_constants_telemetry",
    activation_threshold=activation_energy_gate.compute_threshold(),
    arousal_cap=arousal_interval_gate.compute_threshold(),
    adaptive_scale=adaptive_scale.get_scale(),
    tick_distribution=adaptive_scale.tick_reason_ema,
    total_active_energy=total_active_energy,
    mean_arousal=mean_arousal
)

# Every 100 frames
if frame_id % 100 == 0:
    logger.info(
        "zero_constants_stats",
        activation_gate_stats=activation_energy_gate.get_stats(),
        arousal_gate_stats=arousal_interval_gate.get_stats()
    )
```

---

## Troubleshooting

### Gate oscillates (threshold jumps around)

**Symptom:** Threshold changes dramatically frame-to-frame
**Cause:** Window size too small or data too noisy
**Fix:**
- Increase `window_size` (try 2000 or 5000)
- Add smoothing (compute threshold from EMA of percentile, not raw percentile)

---

### Gate stuck at default

**Symptom:** Threshold never moves from `default_threshold`
**Cause:** Not enough observations collected
**Fix:**
- Check `observation_count` in stats
- Verify `update()` being called each frame
- Reduce `warmup_frames` if needed

---

### Distribution doesn't balance

**Symptom:** Adaptive scale doesn't achieve target distribution
**Cause:** Adjustment rate too slow or too fast
**Fix:**
- If too slow: Increase adjustment factor (try `error * 0.2` instead of `error * 0.1`)
- If too fast (oscillates): Decrease adjustment factor (try `error * 0.05`)
- Increase adaptation frequency (try every 5 frames instead of 10)

---

### All ticks become activation ticks

**Symptom:** Distribution skews to 90%+ activation
**Cause:** Adaptive scale too low or activation gate too permissive
**Fix:**
- Check activation gate threshold (should be Q75, not Q50)
- Check adaptive scale range (should clamp to 100-2000, not 0-10000)
- Verify other interval sources (stimulus, arousal) are working

---

## Implementation Checklist

**Phase 1 (Telemetry):**
- [ ] Add telemetry logging for total_active_energy
- [ ] Add telemetry logging for mean_arousal
- [ ] Add telemetry logging for tick_reason
- [ ] Collect 1 week of baseline data
- [ ] Analyze distributions to validate approach

**Phase 2 (QuantileGate):**
- [ ] Implement QuantileGate class
- [ ] Create activation_energy_gate (Q75, window_size=1000)
- [ ] Create arousal_interval_gate (Q90, window_size=1000)
- [ ] Wire gates into tick interval computation
- [ ] Add comparison telemetry (old vs new thresholds)
- [ ] Monitor for 1 week

**Phase 3 (Adaptive Scale):**
- [ ] Implement AdaptiveIntervalScale class
- [ ] Wire into activation interval computation
- [ ] Add distribution telemetry
- [ ] Monitor for 1 week
- [ ] Write convergence acceptance test
- [ ] Write distribution balance acceptance test

**Phase 4 (Verification):**
- [ ] Run convergence test (1-hour mixed workload)
- [ ] Run distribution balance test (1000 ticks)
- [ ] Add dashboard visualizations
- [ ] Document final threshold values after convergence
- [ ] Remove old fixed constants from codebase

**Estimated implementation time:**
- Phase 1: 2 hours (telemetry + collection)
- Phase 2: 4 hours (QuantileGate + integration + testing)
- Phase 3: 4 hours (AdaptiveIntervalScale + integration + testing)
- Phase 4: 2 hours (acceptance tests + dashboard)
- **Total: 12 hours** (not including week-long monitoring periods)

---

## References

- **Parent specification:** `tick_speed_semantics.md` v1.1 §Zero Constants Enforcement
- **Related:** tick_reason_oracle.md (classification depends on intervals computed by gates)
- **Implementation tasks:** IMPLEMENTATION_TASKS.md Priority 1 - "Implement QuantileGate + replace thresholds + EMA scale"
