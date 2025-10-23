# Tick Speed Regulation - Gap Analysis

**Date:** 2025-10-22
**Analyst:** Felix (Engineer)
**Spec:** `docs/specs/v2/runtime_engine/tick_speed.md`
**Current Implementation:** `orchestration/mechanisms/consciousness_engine_v2.py` (lines 168-200)

---

## Executive Summary

**Status:** ~10% complete - fixed-rate scheduler exists, adaptive regulation missing

**Verdict:** IMPLEMENT adaptive tick speed regulation from scratch. Current code has:
- ✓ Basic tick loop with sleep
- ❌ No stimulus-adaptive scheduling
- ❌ No time_since_last_stimulus tracking
- ❌ No dt_cap for physics integration
- ❌ No EMA smoothing
- ❌ No min/max interval bounds

**Recommendation:** Create new `tick_speed.py` mechanism module with adaptive scheduler class, integrate into consciousness_engine_v2.py.

---

## What Exists (Current Code)

### consciousness_engine_v2.py (Fixed-Rate Scheduler)

**Lines 74-82: EngineConfig**
```python
tick_interval_ms: float = 1000.0  # Fixed 1 Hz (1000ms)
```
- Single fixed interval parameter
- No min/max bounds
- No adaptive behavior

**Lines 168-200: run() method**
```python
while self.running:
    await self.tick()  # Execute tick
    if max_ticks and self.tick_count >= max_ticks:
        break
    await asyncio.sleep(self.config.tick_interval_ms / 1000.0)  # Fixed sleep
```

**What it does:**
- Fixed-interval sleep (1000ms default)
- No variation based on stimulus timing
- No dt calculation for physics

**What it doesn't do:**
- Track time_since_last_stimulus
- Adjust interval based on activity
- Cap dt for diffusion/decay integration
- Smooth interval changes with EMA
- Immediate tick on stimulus arrival

---

## Gap Analysis by Spec Section

### §1 Context - MISSING IMPLEMENTATION

**Spec requirement:**
"Fast ticks under interaction and slow ticks at rest—without destabilizing physics."

**Current state:**
Fixed 1 Hz (1000ms) ticks regardless of activity.

**Gap:**
- No stimulus tracking
- No adaptive scheduling

**Impact:** Critical - wastes compute during dormancy, sluggish during interaction.

---

### §2.1 Scheduler (wall-clock) - NOT IMPLEMENTED

**Spec requirement:**
```python
interval_next = clamp(time_since_last_stimulus, min_interval, max_interval)
```

**Current code:**
```python
await asyncio.sleep(self.config.tick_interval_ms / 1000.0)  # Fixed
```

**Missing components:**

1. **time_since_last_stimulus tracking**
   - Need to record `last_stimulus_time` when stimulus arrives
   - Compute `time_since_last_stimulus = now() - last_stimulus_time`

2. **Interval bounds (min/max)**
   - Spec: `MIN_INTERVAL_MS` (fast, e.g., 100ms)
   - Spec: `MAX_INTERVAL_S` (slow, e.g., 60s)
   - Current: Only single `tick_interval_ms`

3. **Clamping logic**
   - Missing: `clamp(value, min_val, max_val)`

4. **Optional EMA smoothing** (spec §2.1)
   ```python
   interval_next = ema(interval_from_last_stimulus(), beta)
   ```
   - Prevents oscillation after bursts
   - Not implemented

5. **Immediate tick on stimulus** (spec §2.1)
   ```python
   if on_stimulus: schedule.tick_now()
   ```
   - Currently stimulus just queues, waits for next scheduled tick
   - Should trigger immediate tick

**Impact:** Critical - core adaptive behavior missing.

---

### §2.2 Physics dt (cap) - NOT IMPLEMENTED

**Spec requirement:**
```python
dt_used = min(interval_next, dt_cap)
```

**Current code:**
No `dt` parameter passed to mechanisms. Mechanisms use implicit dt=1.0 or ignore time entirely.

**Missing:**

1. **DT_CAP setting**
   - Prevents "first tick after long sleep" from over-integrating
   - Example: `DT_CAP_S = 5.0` (max 5 seconds)

2. **dt calculation and passing**
   - Compute `dt_used = min(interval_actual, DT_CAP_S)`
   - Pass to diffusion: `execute_stride_step(graph, rt, dt=dt_used)`
   - Pass to decay: `apply_decay(graph, dt=dt_used)`

3. **Separate scheduling interval from physics dt**
   - `interval_next` = wall-clock sleep duration
   - `dt_used` = capped physics integration step
   - Current code conflates these

**Impact:** High - prevents blow-ups after long dormancy.

**Blocker:** Diffusion and decay need dt parameter (currently they have it, but not wired up).

---

### §2.2 ρ-controller integration - PARTIAL

**Spec requirement:**
"ρ-controller runs each tick to keep ρ≈1 by tuning decay (and small α-share), independent of wall-clock interval."

**Current code:**
consciousness_engine_v2.py lines 132-138:
```python
self.criticality_controller = CriticalityController(ControllerConfig(
    k_p=0.05,
    enable_pid=False,
    enable_dual_lever=False,
    sample_rho_every_n_frames=5
))
```

**What exists:**
- ✓ CriticalityController instantiated
- ✓ Runs per tick (likely in tick() method)

**What's missing:**
- Verify ρ-controller is independent of tick interval
- Ensure decay adjustment works with variable dt

**Impact:** Low - criticality controller exists, just needs verification.

---

### §4 Expected Behaviors - CANNOT ACHIEVE

**Spec expectations:**
- Conversation → sub-second to seconds ticks
- Dormancy → minutes
- After long sleep, first frame uses capped dt

**Current behavior:**
- Always 1 Hz (1000ms)
- No adaptation
- No dt cap

**Gap:** All expected behaviors unachievable with fixed scheduler.

---

### §6 Observability - NOT IMPLEMENTED

**Spec requirement:**
```python
# Events: tick_frame with dt_ms, interval_sched, dt_used, rho, notes
await broadcast_event("tick_frame", {
    "dt_ms": dt_used * 1000,
    "interval_sched": interval_next,
    "dt_used": dt_used,
    "rho": rho_current,
    "notes": "dt capped" if dt_used < interval_next else None
})
```

**Current code:**
Lines 220-225 emit `frame.start`:
```python
await self.broadcaster.broadcast_event("frame.start", {
    "v": "2",
    "frame_id": self.tick_count,
    "t_ms": int(time.time() * 1000)
})
```

**Missing fields:**
- `dt_ms` - physics integration step
- `interval_sched` - wall-clock interval used
- `dt_used` - capped dt value
- `rho` - criticality measure
- `notes` - diagnostic messages

**Impact:** Medium - affects debugging and visualization.

---

### §7 Failure Modes & Guards - NOT IMPLEMENTED

**Missing guards:**

1. **Oscillation after bursts** (spec §7)
   - Guard: EMA smoothing with β parameter
   - Not implemented

2. **Always at min interval** (hot CPU)
   - Guard: min_interval bounded
   - Partially exists (tick_interval_ms has floor)
   - But no adaptive relaxation

3. **Over-long first tick** (over-integration)
   - Guard: DT_CAP
   - Not implemented

**Impact:** Medium - system could be unstable or wasteful.

---

### §8 Integration - PARTIALLY WIRED

**Spec requirements:**

1. **Where:** consciousness_engine_v2.py
   - ✓ Correct file exists
   - ❌ Adaptive scheduler not implemented

2. **Settings:** {MIN_INTERVAL_MS, MAX_INTERVAL_S, DT_CAP_S, EMA_BETA}
   - ❌ Not in EngineConfig
   - ❌ Not in settings.py

3. **Calls:** traversal_v2.run_frame(dt)
   - ❌ traversal_v2.py doesn't exist yet
   - ❌ No dt passed to mechanisms

**Impact:** High - integration blocked until tick_speed is implemented.

---

### §9 Success Criteria - CANNOT VERIFY

**Spec criteria:**
- Latency from stimulus→tick ≤ min_interval
- No dt blow-ups
- Stable ρ across mode shifts

**Current state:**
Fixed 1 Hz means stimulus→tick latency averages 500ms (half interval), up to 1000ms worst case.

**Gap:** Success criteria unachievable without adaptive scheduler.

---

## Priority Gaps (What to fix)

### P0 - Core Adaptive Scheduling (blocks diffusion integration)

1. **Stimulus time tracking**
   - Record `last_stimulus_time` on stimulus arrival
   - Compute `time_since_last_stimulus`

2. **Interval calculation with bounds**
   ```python
   interval_next = clamp(time_since_last_stimulus, min_interval, max_interval)
   ```

3. **Physics dt with cap**
   ```python
   dt_used = min(interval_next, dt_cap)
   ```

4. **Pass dt to mechanisms**
   - diffusion: `execute_stride_step(..., dt=dt_used)`
   - decay: `apply_decay(..., dt=dt_used)`

### P1 - Immediate Tick on Stimulus

5. **Trigger immediate tick**
   ```python
   if on_stimulus: schedule.tick_now()
   ```

### P2 - Smoothing and Guards

6. **EMA smoothing**
   ```python
   interval_next_smoothed = beta * interval_raw + (1 - beta) * interval_prev
   ```

7. **Settings integration**
   - Add MIN_INTERVAL_MS, MAX_INTERVAL_S, DT_CAP_S, EMA_BETA to EngineConfig

### P3 - Observability

8. **Enhanced frame.start event**
   - Add dt_ms, interval_sched, dt_used, rho, notes

---

## Recommended Implementation

### New File: tick_speed.py

Create dedicated tick speed regulation module:

```python
@dataclass
class TickSpeedConfig:
    """Configuration for adaptive tick speed regulation."""
    min_interval_ms: float = 100.0  # Fast (10 Hz)
    max_interval_s: float = 60.0    # Slow (1/min)
    dt_cap_s: float = 5.0           # Max physics step
    ema_beta: float = 0.3           # Smoothing factor
    enable_ema: bool = True         # EMA smoothing toggle

class AdaptiveTickScheduler:
    """Stimulus-adaptive tick scheduler with dt capping."""

    def __init__(self, config: TickSpeedConfig):
        self.config = config
        self.last_stimulus_time: Optional[float] = None
        self.last_tick_time: float = time.time()
        self.interval_prev: float = config.min_interval_ms / 1000.0

    def on_stimulus(self):
        """Record stimulus arrival time."""
        self.last_stimulus_time = time.time()

    def compute_next_interval(self) -> float:
        """Compute next tick interval (wall-clock sleep)."""
        if self.last_stimulus_time is None:
            # No stimulus yet - use max interval
            interval_raw = self.config.max_interval_s
        else:
            # Time since last stimulus
            time_since = time.time() - self.last_stimulus_time
            interval_raw = time_since

        # Clamp to bounds
        interval_clamped = max(
            self.config.min_interval_ms / 1000.0,
            min(interval_raw, self.config.max_interval_s)
        )

        # Optional EMA smoothing
        if self.config.enable_ema:
            interval_smoothed = (
                self.config.ema_beta * interval_clamped +
                (1 - self.config.ema_beta) * self.interval_prev
            )
            self.interval_prev = interval_smoothed
            return interval_smoothed
        else:
            return interval_clamped

    def compute_dt(self, interval: float) -> tuple[float, bool]:
        """
        Compute physics dt with capping.

        Returns:
            (dt_used, was_capped)
        """
        dt_used = min(interval, self.config.dt_cap_s)
        was_capped = dt_used < interval
        return dt_used, was_capped
```

### Modified: consciousness_engine_v2.py

```python
# Add to imports
from orchestration.mechanisms.tick_speed import AdaptiveTickScheduler, TickSpeedConfig

# Add to EngineConfig
tick_speed_config: TickSpeedConfig = field(default_factory=TickSpeedConfig)

# Add to __init__
self.tick_scheduler = AdaptiveTickScheduler(self.config.tick_speed_config)

# Modify run() method
async def run(self, max_ticks: Optional[int] = None):
    self.running = True
    logger.info("[ConsciousnessEngineV2] Starting main loop...")

    try:
        while self.running:
            # Compute next interval
            interval_next = self.tick_scheduler.compute_next_interval()
            dt_used, was_capped = self.tick_scheduler.compute_dt(interval_next)

            # Execute tick with dt
            await self.tick(dt=dt_used, was_capped=was_capped)

            # Record tick time
            self.tick_scheduler.last_tick_time = time.time()

            # Check max ticks
            if max_ticks and self.tick_count >= max_ticks:
                break

            # Sleep until next tick (wall-clock interval)
            await asyncio.sleep(interval_next)

    except KeyboardInterrupt:
        logger.info("[ConsciousnessEngineV2] Interrupted")
    finally:
        self.running = False

# Modify tick() signature
async def tick(self, dt: float = 1.0, was_capped: bool = False):
    # ... existing tick logic ...

    # Pass dt to diffusion
    if self.config.enable_diffusion:
        execute_stride_step(self.graph, self.diffusion_rt, dt=dt)

    # Pass dt to decay
    if self.config.enable_decay:
        apply_decay(self.graph, dt=dt)

    # Enhanced frame.start event
    await self.broadcaster.broadcast_event("frame.start", {
        "v": "2",
        "frame_id": self.tick_count,
        "t_ms": int(time.time() * 1000),
        "dt_ms": dt * 1000,
        "interval_ms": interval_next * 1000,
        "dt_capped": was_capped,
        "rho": self.criticality_controller.rho if hasattr(self, 'criticality_controller') else None
    })

# Add stimulus tracking
def inject_stimulus(self, stimulus: Dict[str, Any]):
    """Inject stimulus and trigger immediate tick consideration."""
    self.stimulus_queue.append(stimulus)
    self.tick_scheduler.on_stimulus()  # Record stimulus time
```

---

## Estimated Effort

**New code:** ~200 lines

**Breakdown:**
- tick_speed.py: ~120 lines (AdaptiveTickScheduler + config)
- consciousness_engine_v2.py modifications: ~80 lines
- Tests: ~150 lines (test_tick_speed.py)

**Time estimate:** 3-4 hours

**Blockers:** None - can implement immediately

---

## Test Plan

### Unit Tests (test_tick_speed.py)

1. **test_interval_bounds**
   - Verify interval clamped to [min, max]

2. **test_dt_capping**
   - Verify dt <= dt_cap

3. **test_ema_smoothing**
   - Verify smoothing reduces oscillation

4. **test_stimulus_triggers_fast_interval**
   - After stimulus, interval → min
   - After long dormancy, interval → max

5. **test_dt_integration**
   - Verify dt passed correctly to mechanisms

### Integration Tests

6. **test_conversation_mode**
   - Rapid stimuli → sub-second ticks

7. **test_dormancy_mode**
   - No stimuli → slow ticks (minutes)

8. **test_awakening**
   - After long sleep, first tick uses dt_cap

---

## Summary

Tick speed regulation is ~10% implemented:
- ✓ Fixed-rate tick loop exists
- ❌ No adaptive scheduling
- ❌ No stimulus tracking
- ❌ No dt capping
- ❌ No EMA smoothing
- ❌ No min/max bounds

**Recommendation:**
Create `tick_speed.py` with `AdaptiveTickScheduler` class, integrate into `consciousness_engine_v2.py` run() and tick() methods. This unblocks diffusion v2 integration (which needs dt parameter).

**Priority:** HIGH - dependency for diffusion v2, decay v2, and all physics mechanisms.
