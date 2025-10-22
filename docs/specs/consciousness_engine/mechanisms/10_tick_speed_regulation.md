# Mechanism 10: Tick Speed Regulation

**Status:** Efficiency mechanism
**Confidence:** Medium (0.70)
**Dependencies:**
- **[07: Energy Diffusion](07_energy_diffusion.md)** - Tick rate affects diffusion
- **[08: Energy Decay](08_energy_decay.md)** - Tick rate affects decay

**Biological Basis:** Metabolic efficiency, activity-dependent brain rhythms, sleep-wake cycles

---

## Overview

**Core Principle:** Tick interval (thinking speed) equals time since last stimulus. Fast stimulation = fast ticks. Long quiet periods = slow ticks. **Metabolic efficiency** - don't think fast when nothing's happening.

**Why This Matters:**
- Prevents runaway computation during idle periods
- Matches biological reality (brain slows during sleep)
- Enables natural rhythm (active during conversation, slow during dormancy)
- Self-regulating without manual control
- Saves computational resources

**The Self-Regulation Rule:**

```python
tick_interval = time_since_last_stimulus
# (with optional min/max bounds)

Examples:
- Stimulus 100ms ago → tick every 100ms (10 Hz, responsive)
- Stimulus 1 hour ago → tick every hour (0.0003 Hz, dormant)
- Stimulus 1 week ago → tick every day (max cap)
```

---

## Phenomenological Truth

### What It Feels Like

**Fast Thinking (Rapid Stimulation):**

```
Intense conversation:
- Stimuli every 1-5 seconds (questions, responses)
- Tick rate: Every 1-5 seconds
- Diffusion cycles: 10-50 per minute
- Energy patterns shift rapidly
- Many entities activate/deactivate
- Workspace updates frequently

Phenomenology: "Rapid-fire thinking", "ideas flying", "fully engaged"
Reality: High tick rate matching stimulus rate
```

**Slow Thinking (Sparse Stimulation):**

```
Overnight dormancy:
- No stimuli for 8 hours
- Tick rate: Every 30-60 minutes (capped)
- Diffusion cycles: ~8-16 total overnight
- Energy decays slowly
- Entities dissolve gradually
- Workspace mostly static

Phenomenology: "Mind at rest", "background processing", "sleeping"
Reality: Very low tick rate matching lack of stimulation
```

**The Transition:**

```
Wake up after 8 hours:
- First stimulus (alarm): tick_interval = 8 hours → cap at 1 hour
- Tick happens, processes alarm
- Next stimulus 5 seconds later (bird chirping): tick_interval = 5 seconds
- Tick rate increases 720x instantly (1 hour → 5 seconds)
- System "wakes up"

Phenomenology: "Consciousness returning", "becoming alert"
Reality: Tick rate adapting to stimulus frequency
```

---

## Mathematical Specification

### Tick Interval Calculation

```python
class TickController:
    """
    Manages tick interval based on stimulus timing

    Self-regulating - no manual tuning needed
    """
    def __init__(
        self,
        min_interval: float = 0.1,      # Minimum: 100ms (10 Hz max)
        max_interval: float = 3600.0,   # Maximum: 1 hour
        default_interval: float = 1.0   # Starting default
    ):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.current_interval = default_interval

        self.last_stimulus_time = now()
        self.last_tick_time = now()

        self.tick_history = []

    def calculate_next_interval(self) -> float:
        """
        Calculate next tick interval based on time since last stimulus

        Direct correlation: interval = time_since_stimulus
        """
        time_since_stimulus = (now() - self.last_stimulus_time).total_seconds()

        # Direct mapping with bounds
        interval = max(
            self.min_interval,
            min(self.max_interval, time_since_stimulus)
        )

        return interval

    def on_stimulus(self, stimulus: dict):
        """
        Record stimulus arrival - resets tick rate calculation
        """
        self.last_stimulus_time = now()

        # Immediate tick on stimulus (responsive)
        self.current_interval = self.min_interval

    def should_tick(self) -> bool:
        """
        Should we tick now?

        Returns True if enough time has passed since last tick
        """
        time_since_tick = (now() - self.last_tick_time).total_seconds()

        return time_since_tick >= self.current_interval

    def execute_tick(self, graph: Graph):
        """
        Execute one tick and update interval for next
        """
        # Run tick operations
        diffusion_tick(graph, tick_duration=self.current_interval)
        decay_tick(graph, tick_duration=self.current_interval)
        tune_criticality(graph)
        # ... other tick operations

        # Update timing
        self.last_tick_time = now()

        # Calculate next interval
        self.current_interval = self.calculate_next_interval()

        # Track history
        self.tick_history.append({
            'timestamp': now(),
            'interval': self.current_interval,
            'time_since_stimulus': (now() - self.last_stimulus_time).total_seconds()
        })

    def get_effective_tick_rate(self) -> float:
        """
        Current ticks per second

        Returns: Hz (ticks/second)
        """
        return 1.0 / self.current_interval if self.current_interval > 0 else 0.0

    def get_statistics(self) -> dict:
        """
        Statistics about tick rate evolution
        """
        if not self.tick_history:
            return {}

        intervals = [entry['interval'] for entry in self.tick_history[-100:]]

        return {
            'current_interval': self.current_interval,
            'current_hz': self.get_effective_tick_rate(),
            'mean_interval': np.mean(intervals),
            'std_interval': np.std(intervals),
            'min_interval': np.min(intervals),
            'max_interval': np.max(intervals),
            'time_since_last_stimulus': (now() - self.last_stimulus_time).total_seconds()
        }
```

---

## Tick Patterns

### Responsive Mode (Conversation)

```python
def simulate_conversation_tick_pattern():
    """
    Simulate tick pattern during active conversation
    """
    controller = TickController()

    # Simulate conversation (stimuli every 2-10 seconds)
    for i in range(100):
        # Random stimulus
        if random.random() < 0.3:  # 30% chance per iteration
            controller.on_stimulus({'type': 'message', 'content': 'test'})

        # Check if should tick
        if controller.should_tick():
            controller.execute_tick(graph)

        time.sleep(0.01)  # Simulate time passing

    stats = controller.get_statistics()
    print(f"Conversation mode - Mean interval: {stats['mean_interval']:.2f}s")
    print(f"Conversation mode - Mean rate: {stats['current_hz']:.2f} Hz")

    # Expected: Mean interval ~2-5 seconds, rate 0.2-0.5 Hz
```

### Dormant Mode (Sleep)

```python
def simulate_sleep_tick_pattern():
    """
    Simulate tick pattern during sleep (no stimuli)
    """
    controller = TickController()

    # No stimuli for 8 hours
    start_time = time.time()

    ticks_executed = 0
    while time.time() - start_time < 28800:  # 8 hours
        if controller.should_tick():
            controller.execute_tick(graph)
            ticks_executed += 1

        time.sleep(60)  # Check every minute

    print(f"Sleep mode - Total ticks: {ticks_executed}")
    print(f"Sleep mode - Average interval: {28800/ticks_executed:.0f} seconds")

    # Expected: ~8-16 ticks total (1-2 per hour)
```

---

## Edge Cases & Constraints

### Edge Case 1: Stimulus Burst

**Problem:** Many stimuli in rapid succession → tick rate oscillates

**Solution:** Smooth adaptation

```python
class SmoothedTickController(TickController):
    """
    Smooths tick rate changes to avoid oscillation

    Uses exponential moving average
    """
    def __init__(self, *args, smoothing_factor: float = 0.7, **kwargs):
        super().__init__(*args, **kwargs)
        self.smoothing_factor = smoothing_factor
        self.smoothed_interval = self.current_interval

    def calculate_next_interval(self) -> float:
        """
        Smooth interval changes with EMA
        """
        raw_interval = super().calculate_next_interval()

        # Exponential moving average
        self.smoothed_interval = (
            self.smoothing_factor * self.smoothed_interval +
            (1 - self.smoothing_factor) * raw_interval
        )

        return self.smoothed_interval
```

### Edge Case 2: Never-Ending Conversation

**Problem:** Continuous stimulation → interval stays at minimum forever

**Solution:** This is CORRECT - active conversation should maintain fast ticks

```python
def verify_continuous_stimulation_maintains_rate():
    """
    Verify that continuous stimulation keeps tick rate high

    This is desired behavior, not a bug
    """
    controller = TickController()

    # Stimulate continuously for 1 hour
    for _ in range(3600):  # 3600 seconds
        controller.on_stimulus({'type': 'message'})
        time.sleep(1)

        if controller.should_tick():
            controller.execute_tick(graph)

    # Rate should stay at minimum interval
    assert controller.current_interval == controller.min_interval, \
        "Continuous stimulation should maintain maximum tick rate"
```

### Edge Case 3: First Tick After Long Sleep

**Problem:** After days of dormancy, first stimulus → huge tick_duration

**Solution:** Cap tick_duration separately from interval

```python
def execute_tick_with_duration_cap(
    graph: Graph,
    tick_interval: float,
    max_tick_duration: float = 3600.0  # 1 hour max
):
    """
    Execute tick but cap duration used in calculations

    Prevents extreme effects from very long intervals
    """
    effective_duration = min(tick_interval, max_tick_duration)

    # Use capped duration for operations
    diffusion_tick(graph, tick_duration=effective_duration)
    decay_tick(graph, tick_duration=effective_duration)

    # But actual interval can be longer (for scheduling next tick)
```

---

## Testing Strategy

### Unit Tests

```python
def test_interval_follows_stimulus_timing():
    """Test tick interval equals time since stimulus"""
    controller = TickController(min_interval=0.1, max_interval=3600)

    # Stimulus now
    controller.on_stimulus({'type': 'test'})

    assert controller.current_interval == 0.1, "Should be at minimum after stimulus"

    # Simulate 10 seconds passing
    controller.last_stimulus_time = now() - timedelta(seconds=10)

    new_interval = controller.calculate_next_interval()

    assert 9 < new_interval < 11, f"Interval should be ~10 seconds: {new_interval}"

def test_interval_capped_at_bounds():
    """Test interval respects min/max bounds"""
    controller = TickController(min_interval=0.1, max_interval=3600)

    # Very recent stimulus
    controller.last_stimulus_time = now() - timedelta(milliseconds=10)
    interval = controller.calculate_next_interval()

    assert interval >= 0.1, "Should not go below minimum"

    # Very old stimulus
    controller.last_stimulus_time = now() - timedelta(days=7)
    interval = controller.calculate_next_interval()

    assert interval <= 3600, "Should not exceed maximum"
```

### Integration Tests

```python
def test_tick_rate_adapts_to_activity():
    """Test tick rate increases with activity, decreases with quiet"""
    controller = TickController()
    graph = create_test_graph()

    # Phase 1: High activity
    for _ in range(50):
        controller.on_stimulus({'type': 'message'})
        time.sleep(0.5)  # Stimulus every 500ms

        if controller.should_tick():
            controller.execute_tick(graph)

    active_rate = controller.get_effective_tick_rate()

    # Phase 2: Quiet (no stimuli for 1 hour)
    controller.last_stimulus_time = now() - timedelta(hours=1)

    quiet_rate = controller.get_effective_tick_rate()

    # Active rate should be much higher
    assert active_rate > quiet_rate * 100, \
        f"Active rate ({active_rate:.2f} Hz) should be much higher than quiet ({quiet_rate:.2f} Hz)"
```

### Phenomenological Validation

```python
def test_tick_rate_matches_alertness():
    """
    Test tick rate creates phenomenology of alertness vs. dormancy

    Active conversation should feel "rapid-fire"
    Sleep should feel "slow background drift"
    """
    controller = TickController()
    graph = create_consciousness_graph()

    # Simulate active conversation (10 stimuli/minute)
    conversation_ticks = 0
    for minute in range(10):
        for _ in range(10):
            controller.on_stimulus({'type': 'message', 'content': 'test'})
            time.sleep(6)  # 10 per minute

            while controller.should_tick():
                controller.execute_tick(graph)
                conversation_ticks += 1

    # Simulate sleep (no stimuli)
    sleep_ticks = 0
    controller.last_stimulus_time = now()  # Reset

    for hour in range(8):
        time.sleep(3600)  # 1 hour

        while controller.should_tick():
            controller.execute_tick(graph)
            sleep_ticks += 1

    # Conversation should have MANY more ticks
    assert conversation_ticks > sleep_ticks * 50, \
        f"Conversation ({conversation_ticks}) should tick much more than sleep ({sleep_ticks})"

    # Phenomenology:
    # - Conversation: 100+ ticks in 10 minutes = rapid state changes
    # - Sleep: <20 ticks in 8 hours = slow drift
```

---

## Performance Considerations

### Computational Savings

```python
def measure_computational_savings():
    """
    Measure how much computation is saved by adaptive tick rate

    Compare fixed 10 Hz vs. adaptive
    """
    # Fixed rate: 10 Hz (every 100ms)
    fixed_ticks_per_day = 24 * 3600 * 10  # 864,000 ticks

    # Adaptive rate: Assume 8 hours active (5 Hz), 16 hours dormant (0.001 Hz)
    active_ticks = 8 * 3600 * 5  # 144,000 ticks
    dormant_ticks = 16 * 3600 * 0.001  # 58 ticks
    adaptive_ticks_per_day = active_ticks + dormant_ticks  # ~144,058 ticks

    savings = (fixed_ticks_per_day - adaptive_ticks_per_day) / fixed_ticks_per_day

    print(f"Fixed rate: {fixed_ticks_per_day:,} ticks/day")
    print(f"Adaptive rate: {adaptive_ticks_per_day:,} ticks/day")
    print(f"Savings: {savings*100:.1f}%")

    # Expected: ~83% reduction in ticks
```

---

## Open Questions

1. **Optimal min/max bounds?**
   - Current: 0.1s - 3600s
   - Confidence: Medium (0.6)
   - May need tuning based on usage

2. **Smoothing factor?**
   - Current: No smoothing (direct mapping)
   - Alternative: EMA with factor 0.7
   - Confidence: Low (0.5)

3. **Tick on stimulus always?**
   - Current: Yes (immediate tick on stimulus)
   - Alternative: Wait for scheduled tick
   - Confidence: High (0.8) - immediate better for responsiveness

4. **Sleep mode?**
   - Current: No special sleep mode
   - Alternative: Even slower ticks during designated sleep
   - Confidence: Low (0.4)

---

## Related Mechanisms

- **[07: Energy Diffusion](07_energy_diffusion.md)** - Affected by tick duration
- **[08: Energy Decay](08_energy_decay.md)** - Affected by tick duration
- **[03: Self-Organized Criticality](03_self_organized_criticality.md)** - Runs every tick

---

## Implementation Checklist

- [ ] Implement TickController class
- [ ] Implement calculate_next_interval() with bounds
- [ ] Implement on_stimulus() for rate reset
- [ ] Implement should_tick() for scheduling
- [ ] Implement execute_tick() with all operations
- [ ] Implement smoothed variant (optional)
- [ ] Implement tick duration capping
- [ ] Write unit tests for interval calculation
- [ ] Write unit tests for bound enforcement
- [ ] Write integration tests for adaptation
- [ ] Write phenomenological tests (alertness)
- [ ] Measure computational savings
- [ ] Add tick rate monitoring/visualization

---

**Next:** [11: Cluster Identification](11_cluster_identification.md) - Finding entity clusters for workspace selection
