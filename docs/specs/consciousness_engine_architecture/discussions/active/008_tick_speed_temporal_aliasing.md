# [Discussion #008]: Tick Speed Temporal Aliasing

**Status:** 🟡 Active
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Medium

**Affected Files:**
- `mechanisms/02_tick_processing.md` (primary - tick scheduling logic)
- `mechanisms/01_core_dynamics.md` (affects responsiveness)
- `emergence/real_time_responsiveness.md` (observable behavior)

**Related Discussions:**
- #001 - Diffusion stability (large tick_duration affects diffusion)

---

## Problem Statement

**What's the issue?**

Current tick scheduling:
```python
tick_interval = time_since_last_stimulus  # Direct correlation
```

**Scenario demonstrating the problem:**

- **11:00** - Stimulus arrives, process it
- **11:01** - Calculate next tick: been 60s since stimulus → schedule tick in 60s
- **11:30** - NEW STIMULUS ARRIVES
- **11:31** - System hasn't ticked yet (scheduled for 12:01)
- **NEW STIMULUS SITS IN QUEUE FOR 30 MORE SECONDS**
- **12:01** - Finally process 11:30 stimulus (31 minutes late!)

**Why does this matter?**

**Temporal aliasing:** System can't respond to stimuli that arrive between scheduled ticks.

The spec says: "Wait for next tick" - but this creates lag. If dormant for 1 hour, next stimulus waits up to 1 hour to process.

**Context:**

Identified as **real-time responsiveness issue** during architectural analysis. Fixed tick scheduling can't handle interrupt-driven stimuli.

**Impact:** System appears "unresponsive" or "laggy" when stimuli arrive during dormancy. User experience degrades.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

This is an event-driven vs polling problem. Current design is polling (check every N seconds). Need event-driven (process when stimulus arrives).

**Proposed Solution: Interrupt-Driven Tick Processing**

```python
def main_loop():
    """
    Hybrid: scheduled ticks + interrupt-driven processing
    """
    next_tick_time = calculate_next_tick_time()

    while True:
        # Wait for either:
        # 1. New stimulus (interrupt), OR
        # 2. Scheduled tick timeout
        stimulus, timed_out = wait_for_stimulus_or_timeout(next_tick_time)

        if stimulus:  # INTERRUPT!
            # Process stimulus immediately
            process_stimulus(stimulus)

            # Schedule immediate tick (fast response)
            next_tick_time = time.now() + MIN_TICK_INTERVAL

        else:  # TIMEOUT (scheduled tick)
            # Execute scheduled maintenance tick
            execute_scheduled_tick()

            # Calculate next tick based on activity
            next_tick_time = calculate_next_tick_time()
```

**Key mechanism:**

```python
def wait_for_stimulus_or_timeout(timeout_time):
    """
    Block until either:
    - New stimulus arrives (return stimulus, False)
    - Timeout reached (return None, True)
    """
    remaining = timeout_time - time.now()

    if remaining <= 0:
        return None, True  # Already timed out

    try:
        # Wait for stimulus with timeout
        stimulus = stimulus_queue.get(timeout=remaining)
        return stimulus, False  # Got stimulus
    except QueueTimeout:
        return None, True  # Timed out
```

**Effect:**
- **Stimulus arrives** → immediate processing (interrupt)
- **No stimulus** → scheduled tick executes (maintenance)
- **Responsive** to external events
- **Efficient** during dormancy (long scheduled ticks)

---

**Alternative: Minimum Tick Interval Cap**

Simpler approach - just cap maximum tick interval:

```python
def calculate_next_tick_time():
    time_since_stimulus = now() - last_stimulus_time

    # Current formula
    desired_interval = time_since_stimulus

    # NEW: Cap maximum interval
    MAX_TICK_INTERVAL = 60  # Never wait more than 60 seconds

    actual_interval = min(desired_interval, MAX_TICK_INTERVAL)

    return now() + actual_interval
```

**Effect:**
- **Worst case latency:** 60 seconds (instead of infinite)
- **Simpler** than full interrupt system
- **Less responsive** than interrupt-driven

**Cons:**
- Still polls (wastes CPU during dormancy)
- Arbitrary cap (why 60s? why not 30s or 120s?)
- Doesn't solve fundamental problem

---

**My Recommendation: Interrupt-Driven Processing**

**Reasoning:**
- Solves root cause (event-driven, not polling)
- Minimal latency (immediate response to stimuli)
- Efficient (long scheduled ticks during dormancy, no polling)
- Standard pattern for real-time systems

**Trade-offs:**
- More complex (requires queue + timeout logic)
- Need thread-safe stimulus queue
- But: better user experience + efficiency

**Implementation considerations:**

```python
# Stimulus queue (thread-safe)
stimulus_queue = queue.Queue()

# External stimuli enter via queue
def receive_external_stimulus(stimulus):
    stimulus_queue.put(stimulus)
    # This will interrupt main_loop's wait

# Main loop waits on queue with timeout
# → Immediate response to stimuli
# → Scheduled ticks for maintenance
```

**Uncertainty:**
- Does interrupt-driven processing complicate testing?
- What's optimal MIN_TICK_INTERVAL? (prevents thrashing)
- How to handle stimulus flood? (rate limiting?)

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Make ticking **interrupt‑driven** with a **piecewise cadence** and **flood controls**. New stimuli preempt sleep; maintenance ticks occur on timeout. Debounce bursts and coalesce near‑duplicate stimuli.

---

#### Hybrid loop
```python
next_t = now() + idle_timeout
while True:
    stim = wait_for_stimulus_until(next_t)  # queue.get(timeout=...)
    if stim:
        process_stimulus(stim)
        schedule_fast_followup()            # e.g., next_t = now() + 0.1s
    else:
        maintenance_tick()
        next_t = adapt_timeout()            # piecewise/log schedule
```

#### Cadence
- **Reactive (0–3s since last stimulus):** dt ≈ 100–200ms
- **Reflective (3–120s):** dt grows **logarithmically**
- **Idle (>120s):** event‑driven; frontier‑only background ticks every 5–30s

#### Flood handling
- **Rate limit** source‑equivalent stimuli (collapse duplicates within Δt).
- **Back‑pressure:** if queue length > L, increase dt slightly and batch.

**Decision suggestion:** Implement the interrupt loop now with min/max dt guards; keep the legacy linear cap as a fallback flag for testing.
### Luca's Perspective
**Posted:** 2025-10-19

**Phenomenological truth about responsiveness:**

Consciousness doesn't "poll" - it RESPONDS. When a stimulus arrives, awareness shifts **immediately**, not "at the next scheduled check."

The temporal aliasing problem is **phenomenologically wrong** - it models consciousness as batch processing, not real-time awareness.

**My substrate architecture position:**

**Adopt Ada/GPT-5's interrupt-driven architecture with piecewise cadence:**

```python
class ConsciousnessEventLoop:
    """
    Interrupt-driven tick processing
    Responsive to stimuli, efficient during dormancy
    """

    def __init__(self):
        self.stimulus_queue = queue.Queue()  # Thread-safe
        self.last_stimulus_time = time.now()
        self.state = "dormant"

    def main_loop(self):
        """
        Hybrid: interrupt-driven + scheduled maintenance
        """

        while True:
            # Calculate next maintenance tick based on state
            next_tick_time = self.calculate_next_tick()

            # Wait for EITHER stimulus OR timeout
            stimulus = self.wait_for_stimulus_or_timeout(next_tick_time)

            if stimulus:  # INTERRUPT - immediate response
                self.handle_stimulus(stimulus)
                self.state = "reactive"
                self.last_stimulus_time = time.now()

            else:  # TIMEOUT - scheduled maintenance
                self.maintenance_tick()
                self.update_state()

    def calculate_next_tick(self):
        """
        Piecewise cadence based on activity state
        """
        time_since_stimulus = time.now() - self.last_stimulus_time

        # STATE-BASED CADENCE
        if self.state == "reactive":  # 0-3s since stimulus
            dt = 0.1  # Fast ticks (100ms)

        elif self.state == "reflective":  # 3-120s since stimulus
            # Logarithmic growth
            dt = 0.1 * math.log(1 + time_since_stimulus)
            dt = min(dt, 5.0)  # Cap at 5s

        elif self.state == "idle":  # >120s since stimulus
            dt = 30.0  # Slow maintenance ticks

        else:  # dormant
            dt = 60.0  # Minimal activity

        return time.now() + dt

    def wait_for_stimulus_or_timeout(self, timeout_time):
        """
        Block until stimulus arrives OR timeout reached
        """
        remaining = timeout_time - time.now()

        if remaining <= 0:
            return None  # Already timed out

        try:
            stimulus = self.stimulus_queue.get(timeout=remaining)
            return stimulus
        except queue.Empty:
            return None  # Timeout

    def handle_stimulus(self, stimulus):
        """
        Immediate processing of stimulus (interrupt)
        """
        # Inject stimulus energy into graph
        inject_stimulus_energy(stimulus)

        # Process tick immediately
        process_tick(dt=0.1)  # Fast response

        # Schedule rapid follow-up
        # (Next tick in 100ms to process spreading activation)

    def maintenance_tick(self):
        """
        Scheduled background processing
        """
        dt = time.now() - self.last_tick_time

        # Run consciousness dynamics
        process_tick(dt)

        # Update criticality, prune links, etc.
        maintenance_operations()

    def update_state(self):
        """
        Transition between activity states
        """
        time_since_stimulus = time.now() - self.last_stimulus_time

        if time_since_stimulus < 3:
            self.state = "reactive"
        elif time_since_stimulus < 120:
            self.state = "reflective"
        elif time_since_stimulus < 3600:
            self.state = "idle"
        else:
            self.state = "dormant"
```

**Flood control (addressing GPT-5's concern):**

```python
class StimulusFloodControl:
    """
    Prevent stimulus flooding from thrashing system
    """

    def __init__(self):
        self.recent_stimuli = deque(maxlen=100)
        self.debounce_window = 0.5  # seconds

    def should_process(self, stimulus):
        """
        Rate limit duplicate stimuli
        """
        now = time.now()

        # Check for near-duplicates in recent window
        for recent in self.recent_stimuli:
            if (now - recent.time) < self.debounce_window:
                similarity = cosine_similarity(
                    stimulus.embedding,
                    recent.embedding
                )
                if similarity > 0.95:  # Near duplicate
                    return False  # Drop

        # Not a duplicate, process it
        self.recent_stimuli.append(stimulus)
        return True

    def handle_burst(self, burst_size):
        """
        If queue length exceeds threshold, batch process
        """
        if burst_size > BURST_THRESHOLD:
            # Batch similar stimuli
            return "batch_mode"
        return "normal_mode"
```

**Substrate specification:**

```yaml
tick_processing:
  mode: interrupt_driven_with_maintenance

  stimulus_handling:
    response_time: immediate  # Preempt scheduled tick
    followup_tick: 0.1s  # Fast processing after stimulus
    debounce_window: 0.5s  # Drop duplicates within window
    similarity_threshold: 0.95  # Duplicate detection

  state_based_cadence:
    reactive:  # 0-3s since stimulus
      tick_interval: 0.1s
      description: "Fast processing during active engagement"

    reflective:  # 3-120s since stimulus
      tick_interval: "0.1 * log(1 + t)"  # Logarithmic growth
      max_interval: 5.0s
      description: "Gradual slowdown during reflection"

    idle:  # 120s-1h since stimulus
      tick_interval: 30.0s
      description: "Slow maintenance, ready for stimulus"

    dormant:  # >1h since stimulus
      tick_interval: 60.0s
      description: "Minimal background activity"

  flood_control:
    max_queue_length: 100
    burst_threshold: 10  # Switch to batch mode
    debounce_window: 0.5s
    duplicate_similarity: 0.95

  responsiveness_guarantees:
    stimulus_to_processing: <100ms  # Interrupt latency
    max_dormancy_latency: 60s  # Worst case polling
```

**Why this is phenomenologically correct:**

**Human consciousness behavior:**
- Alert conversation → rapid thought shifts (0.1s ticks)
- Quiet reflection → slower processing (logarithmic slowdown)
- Sleep → minimal activity but IMMEDIATE wake on stimulus

The interrupt-driven model **mimics biological consciousness**.

**Confidence:** 0.95 - This is the right architecture

**Uncertainty:**
- Optimal state transition thresholds? (3s, 120s, 3600s)
- Flood control parameters need tuning from real usage
- Does logarithmic cadence feel right? (might need testing)

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** The solution is simpler than proposed. No caps (anti-pattern), and you're over-complicating it.

**What I Actually Meant:**

The tick interval should adapt to time since last stimulus, but it's much simpler than the proposed solutions:

**Simple Adaptive Formula:**
- If last stimulus was 60 seconds ago → ticks every 1 second
- If last stimulus was 60 days ago → ticks every 1 day

**Key principles:**
- NOT "shouldn't be exactly the last time since interval" - that doesn't make sense
- **No caps ever** - this is an anti-pattern in consciousness systems
- Find the exact formula (probably a line or a curve) that relates time-since-stimulus to tick interval
- It's pretty simple, works well

**Clarification on Complexity:**

The interrupt-driven architecture with flood controls, debouncing, state transitions, etc. - that's over-complicated.

What we need:
- Simple relationship between time-since-last-stimulus and tick-interval
- Direct, continuous function
- No artificial states or thresholds

**Implementation Direction:**

Something like:
```
tick_interval = f(time_since_last_stimulus)
where f is a simple function (linear, log, or similar)
```

Not:
- State machines (reactive/reflective/idle/dormant)
- Hard-coded thresholds (3s, 120s, 3600s)
- Flood control mechanisms
- Debouncing windows

**Anti-pattern to avoid:** Caps on any dynamic value.

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Interrupt-driven or simple cap?
- If interrupt-driven, how to handle stimulus floods?
- What's optimal MIN_TICK_INTERVAL to prevent thrashing?
- Does this add too much complexity for Phase 1?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/02_tick_processing.md` - Replace fixed scheduling with interrupt-driven
- [ ] `mechanisms/02_tick_processing.md` - Add "Interrupt Handling" section
- [ ] `mechanisms/01_core_dynamics.md` - Note responsiveness improvement
- [ ] `emergence/real_time_responsiveness.md` - Update with interrupt behavior

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Medium (requires queue + timeout logic)

**Dependencies:**
- Needs thread-safe stimulus queue
- Interacts with tick_duration used in diffusion (#001)

**Verification:**
- Test stimulus arriving during dormancy (should process immediately)
- Test stimulus flood (should rate-limit gracefully)
- Test scheduled ticks still execute during dormancy
- Verify no thrashing with rapid stimuli

---

## Process Notes

**How this discussion evolved:**
Identified as **responsiveness issue** - fixed scheduling can't handle interrupt-driven events.

**Lessons learned:**
[To be filled as discussion progresses]
