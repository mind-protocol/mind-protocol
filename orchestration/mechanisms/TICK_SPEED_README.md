# Tick Speed Regulation - Implementation Guide

**Spec:** `docs/specs/v2/runtime_engine/tick_speed.md`
**Implementation:** `orchestration/mechanisms/tick_speed.py`
**Tests:** `orchestration/mechanisms/test_tick_speed.py`
**Author:** Felix (Engineer)
**Date:** 2025-10-22

---

## Overview

Adaptive tick scheduling that follows stimulus timing with bounds and physics dt capping.

**Key principle:** Fast ticks (100ms) during active stimulation, slow ticks (60s) during dormancy, without destabilizing physics through dt capping.

**Core formula:**
```
interval_next = clamp(time_since_last_stimulus, min_interval, max_interval)
dt_used = min(interval_next, dt_cap)
```

---

## Core Components

### 1. TickSpeedConfig

Configuration dataclass for adaptive scheduler:

```python
from orchestration.mechanisms.tick_speed import TickSpeedConfig

config = TickSpeedConfig(
    min_interval_ms=100.0,   # Fast ticks (10 Hz)
    max_interval_s=60.0,     # Slow ticks (1/min)
    dt_cap_s=5.0,            # Physics dt cap
    ema_beta=0.3,            # Smoothing factor
    enable_ema=True          # EMA toggle
)
```

**Parameters:**
- `min_interval_ms`: Minimum tick interval (fastest rate) - Default 100ms (10 Hz)
- `max_interval_s`: Maximum tick interval (slowest rate) - Default 60s (1/min)
- `dt_cap_s`: Maximum physics integration step - Default 5.0s
- `ema_beta`: EMA smoothing factor (0=no smoothing, 1=no memory) - Default 0.3
- `enable_ema`: Whether to apply EMA smoothing - Default True

### 2. AdaptiveTickScheduler

Main scheduler class that tracks stimulus timing and computes adaptive intervals:

```python
from orchestration.mechanisms.tick_speed import AdaptiveTickScheduler, TickSpeedConfig

# Initialize
config = TickSpeedConfig()
scheduler = AdaptiveTickScheduler(config)

# Record stimulus arrival
scheduler.on_stimulus()

# Compute next tick interval (wall-clock)
interval_next = scheduler.compute_next_interval()

# Compute physics dt (capped)
dt_used, was_capped = scheduler.compute_dt(interval_next)

# Execute tick with dt_used
await tick(dt=dt_used)

# Sleep until next tick
await asyncio.sleep(interval_next)
```

---

## Usage Patterns

### Pattern 1: Conversation Mode (Rapid Stimuli)

```python
# User sends multiple messages
for message in user_messages:
    scheduler.on_stimulus()  # Record each stimulus

    interval = scheduler.compute_next_interval()
    # interval ≈ 0.1s (min_interval) - fast ticks

    dt, capped = scheduler.compute_dt(interval)
    # dt ≈ 0.1s, capped=False (under cap)

    await tick(dt=dt)
    await asyncio.sleep(interval)
```

**Result:** Sub-second tick rate for responsive interaction.

### Pattern 2: Dormancy Mode (No Stimuli)

```python
# No stimuli for extended period
# ... 30 seconds pass ...

interval = scheduler.compute_next_interval()
# interval ≈ 30s (clamped to max_interval if >60s)

dt, capped = scheduler.compute_dt(interval)
# dt = 5.0s, capped=True (hit dt_cap)

await tick(dt=dt)  # Physics uses capped dt
await asyncio.sleep(interval)  # But we sleep for full interval
```

**Result:** Slow tick rate to save compute, dt capped to prevent physics blow-ups.

### Pattern 3: Awakening After Long Sleep

```python
# System dormant for 2 hours
# ... 7200 seconds pass ...

# First tick after awakening
interval = scheduler.compute_next_interval()
# interval = 60s (clamped to max_interval_s)

dt, capped = scheduler.compute_dt(interval)
# dt = 5.0s, capped=True (dt_cap prevents 60s physics step)

# Physics integrates with dt=5.0s (safe)
# Diffusion: ΔE = E · α · 5.0  (not ΔE = E · α · 60.0!)
# Decay: e^(-λ·5.0)  (not e^(-λ·60.0)!)

await tick(dt=dt)
```

**Result:** First tick after long sleep uses capped dt to prevent over-integration.

---

## Integration with Consciousness Engine

### Modified: consciousness_engine_v2.py

```python
from orchestration.mechanisms.tick_speed import AdaptiveTickScheduler, TickSpeedConfig

class ConsciousnessEngineV2:
    def __init__(self, graph, adapter, config):
        # ... existing init ...

        # Add tick speed scheduler
        tick_config = TickSpeedConfig(
            min_interval_ms=100.0,
            max_interval_s=60.0,
            dt_cap_s=5.0
        )
        self.tick_scheduler = AdaptiveTickScheduler(tick_config)

    async def run(self, max_ticks=None):
        """Run consciousness engine with adaptive tick speed."""
        self.running = True

        while self.running:
            # Compute adaptive interval
            interval_next = self.tick_scheduler.compute_next_interval()
            dt_used, was_capped = self.tick_scheduler.compute_dt(interval_next)

            # Execute tick with dt
            await self.tick(dt=dt_used, was_capped=was_capped)

            # Check max ticks
            if max_ticks and self.tick_count >= max_ticks:
                break

            # Sleep until next tick (wall-clock interval)
            await asyncio.sleep(interval_next)

    async def tick(self, dt: float = 1.0, was_capped: bool = False):
        """Execute one consciousness tick with physics dt."""
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
            "dt_ms": dt * 1000,
            "interval_ms": interval_next * 1000,
            "dt_capped": was_capped,
            "rho": self.criticality_controller.rho
        })

    def inject_stimulus(self, stimulus):
        """Inject stimulus and trigger adaptive scheduling."""
        self.stimulus_queue.append(stimulus)
        self.tick_scheduler.on_stimulus()  # Record stimulus time
```

---

## Mechanism Behavior

### Interval Calculation

**Without EMA:**
```python
if last_stimulus_time is None:
    interval = max_interval_s  # Dormant
else:
    time_since = now() - last_stimulus_time
    interval = clamp(time_since, min_interval_ms/1000, max_interval_s)
```

**With EMA (β=0.3):**
```python
interval_raw = clamp(time_since_stimulus, min, max)
interval_smoothed = 0.3 * interval_raw + 0.7 * interval_prev
```

EMA smoothing reduces oscillation after stimulus bursts.

### dt Capping

```python
dt_used = min(interval_next, dt_cap_s)
was_capped = (dt_used < interval_next)
```

**Why cap dt separately from interval?**
- `interval_next` controls wall-clock sleep (responsiveness)
- `dt_used` controls physics integration (stability)
- After long dormancy: sleep 60s (save compute), but integrate physics with dt=5s (prevent blow-up)

---

## Test Coverage

**7 comprehensive tests (all passing):**

### Test 1: Interval Bounds
- No stimulus → max_interval (dormant)
- Fresh stimulus → min_interval (active)
- Mid-range → proportional
- Long inactivity → clamped to max

### Test 2: Physics dt Capping
- Short interval → dt = interval (under cap)
- At cap → dt = cap
- Long interval → dt = cap (capped=True)

### Test 3: EMA Smoothing
- With EMA: gradual transition
- Without EMA: immediate jumps
- Reduces oscillation

### Test 4: Stimulus Tracking
- Multiple rapid stimuli → stay at min_interval
- No stimulus → max_interval

### Test 5: Dormancy Behavior
- Gradual transition from active to dormant
- Interval grows linearly with time_since_stimulus (up to max)

### Test 6: dt Integration Flow
- Conversation mode: dt ≈ 0.1s (uncapped)
- Dormancy mode: dt = 5.0s (capped)

### Test 7: Diagnostics
- Accurate time tracking
- Config reflection

**Run tests:**
```bash
python orchestration/mechanisms/test_tick_speed.py
```

---

## Observability

### Diagnostic Output

```python
diag = scheduler.get_diagnostics()

# Returns:
{
    'last_stimulus_time': 1234567890.123,  # Wall-clock time
    'time_since_stimulus': 15.5,           # Seconds elapsed
    'interval_prev': 2.3,                  # Previous EMA value
    'config': {
        'min_interval_ms': 100.0,
        'max_interval_s': 60.0,
        'dt_cap_s': 5.0,
        'ema_beta': 0.3,
        'enable_ema': True
    }
}
```

### Event Emission (Integration Required)

```python
# Enhanced frame.start event (spec §6)
await broadcaster.broadcast_event("frame.start", {
    "v": "2",
    "frame_id": tick_count,
    "t_ms": int(time.time() * 1000),
    "dt_ms": dt_used * 1000,           # Physics integration step
    "interval_ms": interval_next * 1000, # Wall-clock interval
    "dt_capped": was_capped,            # Whether dt hit cap
    "rho": rho_current,                 # Criticality measure
    "notes": "dt capped" if was_capped else None
})
```

---

## Configuration Recommendations

### Default (General Purpose)
```python
TickSpeedConfig(
    min_interval_ms=100.0,   # 10 Hz max
    max_interval_s=60.0,     # 1/min min
    dt_cap_s=5.0,            # Conservative cap
    ema_beta=0.3,            # Moderate smoothing
    enable_ema=True
)
```

### High Responsiveness (Real-time Chat)
```python
TickSpeedConfig(
    min_interval_ms=50.0,    # 20 Hz max
    max_interval_s=10.0,     # Faster dormancy wake
    dt_cap_s=2.0,            # Tighter physics control
    ema_beta=0.5,            # More responsive smoothing
    enable_ema=True
)
```

### Low Power (Background Processing)
```python
TickSpeedConfig(
    min_interval_ms=500.0,   # 2 Hz max
    max_interval_s=300.0,    # 5 min dormancy
    dt_cap_s=10.0,           # Relaxed cap
    ema_beta=0.2,            # Slower adaptation
    enable_ema=True
)
```

### No Smoothing (Deterministic Testing)
```python
TickSpeedConfig(
    min_interval_ms=100.0,
    max_interval_s=60.0,
    dt_cap_s=5.0,
    enable_ema=False  # Disable for predictable behavior
)
```

---

## Performance Characteristics

### Computational Cost

**Scheduler overhead per tick:**
- `on_stimulus()`: O(1) - single timestamp update
- `compute_next_interval()`: O(1) - arithmetic operations
- `compute_dt()`: O(1) - min comparison

**Total:** ~10-20 CPU cycles per tick (negligible)

### Memory Overhead

**Per scheduler instance:**
- `last_stimulus_time`: 8 bytes (float)
- `last_tick_time`: 8 bytes (float)
- `interval_prev`: 8 bytes (float)
- `config`: ~40 bytes (5 fields)

**Total:** ~64 bytes per scheduler (negligible)

### Savings from Adaptive Scheduling

**Example scenario:**
- Active: 10 Hz (100ms) for 5 minutes = 3000 ticks
- Dormant: 1/min (60s) for 55 minutes = 55 ticks
- **Total:** 3055 ticks in 60 minutes

**vs. Fixed 10 Hz:**
- 60 minutes × 60 s/min × 10 Hz = 36,000 ticks

**Savings:** 91.5% reduction in tick count during mixed usage.

---

## Troubleshooting

### Problem: Ticks too slow during interaction

**Cause:** min_interval_ms too high

**Fix:**
```python
config = TickSpeedConfig(min_interval_ms=50.0)  # Faster
```

### Problem: Ticks oscillating rapidly

**Cause:** EMA disabled or beta too high

**Fix:**
```python
config = TickSpeedConfig(
    ema_beta=0.2,    # Lower = smoother
    enable_ema=True  # Enable smoothing
)
```

### Problem: Physics unstable after long sleep

**Cause:** dt_cap_s too high

**Fix:**
```python
config = TickSpeedConfig(dt_cap_s=2.0)  # Tighter cap
```

### Problem: dt always capped (even during active periods)

**Cause:** dt_cap_s lower than min_interval_ms/1000

**Fix:**
```python
# Ensure dt_cap >= min_interval
config = TickSpeedConfig(
    min_interval_ms=100.0,  # 0.1s
    dt_cap_s=5.0            # 5s (well above min)
)
```

---

## Summary

Tick speed regulation provides:

✓ **Stimulus-adaptive scheduling** - Fast ticks during interaction, slow during dormancy
✓ **Physics dt capping** - Prevents blow-ups after long sleep
✓ **EMA smoothing** - Reduces oscillation
✓ **Bounded intervals** - [min, max] guarantees
✓ **7 comprehensive tests** - All passing

**Key principle:** Separate wall-clock scheduling (responsiveness) from physics dt (stability).

**Integration:** Replace fixed `asyncio.sleep(interval_ms/1000)` with adaptive scheduler in consciousness_engine_v2.py.

**Testing:** `python orchestration/mechanisms/test_tick_speed.py`

**Documentation:** This file + `docs/specs/v2/runtime_engine/tick_speed.md`
