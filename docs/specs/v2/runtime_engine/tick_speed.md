---
title: Tick Speed Regulation (Stimulus‑Adaptive, ρ‑Aware Scheduling)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/10_tick_speed_regulation.md
depends_on:
  - foundations/criticality.md
  - foundations/decay.md
  - runtime_engine/traversal_v2.md
summary: >
  Schedule ticks from stimulus timing with bounds/smoothing; cap physics dt; let the ρ-controller tune decay/redistribution.
---

# Tick Speed Regulation

## 1) Context — Problem we’re solving
We want **fast ticks** under interaction and **slow ticks** at rest—without destabilizing physics. Tick scheduling should follow **time‑since‑last‑stimulus**, while the **ρ‑controller** handles stability by adjusting **decay/redistribution**, not by wildly changing dt used in physics. :contentReference[oaicite:6]{index=6}

## 2) Mechanism — What it is
Three factors determine tick speed:

1) **Stimulus-driven interval** (external):
   `interval_stimulus = clamp(time_since_last_stimulus, min_interval, max_interval)`

2) **Activation-driven interval** (internal):
   `interval_activation = compute_from_total_active_energy(graph)`
   High internal activation → fast ticks even without new stimuli (enables rumination, generative overflow).

3) **Arousal floor** (affective):
   `interval_arousal = compute_from_affect_arousal(active_entities)`
   High arousal prevents very slow ticks even during low external stimulus.

**Final interval:** `interval_next = min(interval_stimulus, interval_activation, interval_arousal)`

**Why minimum?** Keeps thinking fast for EITHER generative overflow / rumination (high activation) OR anxious/excited states (high arousal) OR new inputs (stimulus).

**Physics dt cap:** `dt_used = min(interval_next, dt_cap)` prevents blow-ups after long sleep.

**ρ‑controller** runs each tick to keep `ρ≈1` by tuning decay (and small α‑share), independent of **wall‑clock** interval.

### 2.1 Dual-Factor Computation

```python
def compute_interval_activation(graph, active_entities):
    """
    Compute interval from internal activation level

    High activation → fast ticks (enables autonomous momentum)
    """
    total_active_energy = sum(
        node.get_entity_energy(e)
        for node in graph.nodes
        for e in active_entities
        if node.get_entity_energy(e) > threshold
    )

    # Map activation to interval (inverse relationship)
    # High activation → short interval (fast ticks)
    # Low activation → long interval (slow ticks)

    if total_active_energy > 10.0:  # High activation
        return settings.MIN_INTERVAL_MS
    elif total_active_energy < 1.0:  # Low activation
        return settings.MAX_INTERVAL_S
    else:
        # Linear interpolation in log space
        log_energy = np.log10(total_active_energy)
        log_min = np.log10(1.0)
        log_max = np.log10(10.0)

        t = (log_energy - log_min) / (log_max - log_min)  # [0, 1]

        # Invert: high energy → short interval
        interval = settings.MAX_INTERVAL_S * (1 - t) + settings.MIN_INTERVAL_MS * t

        return interval

def compute_interval_arousal(active_entities, arousal_floor_enabled=True):
    """
    Compute interval floor from affect arousal

    High arousal → prevents very slow ticks (anxiety/excitement keeps mind active)
    """
    if not arousal_floor_enabled:
        return settings.MAX_INTERVAL_S  # No floor constraint

    # Compute mean arousal across active entities
    arousals = []
    for entity_id in active_entities:
        affect = get_entity_affect(entity_id)  # Valence + arousal vector
        arousal = np.linalg.norm(affect)  # Magnitude as arousal proxy
        arousals.append(arousal)

    mean_arousal = np.mean(arousals) if arousals else 0.0

    # Map arousal to interval floor
    # High arousal → short floor (prevents slow ticks)
    # Low arousal → no floor constraint

    if mean_arousal > 0.7:  # High arousal
        return settings.MIN_INTERVAL_MS * 2  # 2x minimum (still fast)
    elif mean_arousal < 0.3:  # Low arousal
        return settings.MAX_INTERVAL_S  # No constraint
    else:
        # Linear interpolation
        t = (mean_arousal - 0.3) / (0.7 - 0.3)
        floor = settings.MAX_INTERVAL_S * (1 - t) + (settings.MIN_INTERVAL_MS * 2) * t
        return floor
```

### 2.2 Pseudocode (Updated)

```python
if on_stimulus: schedule.tick_now()

if clock.now() - last_tick >= interval_next:
    # Compute three factors
    interval_stimulus = time_since_last_stimulus()
    interval_activation = compute_interval_activation(graph, active_entities)
    interval_arousal = compute_interval_arousal(active_entities)

    # Take minimum (fastest wins)
    interval_next = min(
        clamp(interval_stimulus, min_interval, max_interval),
        interval_activation,
        interval_arousal
    )

    # Determine reason for this interval (observability)
    if interval_next == interval_stimulus:
        reason = "stimulus"
    elif interval_next == interval_activation:
        reason = "activation"
    else:
        reason = "arousal_floor"

    # Apply EMA smoothing to prevent oscillation
    interval_next = ema(interval_next, beta)

    # Cap dt for physics stability
    dt_used = min(interval_next, settings.DT_CAP)

    # Run frame
    run_frame(dt_used)
    last_tick = clock.now()

    # Emit telemetry
    emit_tick_event(interval_next, dt_used, reason, {
        "interval_stimulus": interval_stimulus,
        "interval_activation": interval_activation,
        "interval_arousal": interval_arousal,
        "total_active_energy": total_active_energy,
        "mean_arousal": mean_arousal
    })
```

## 3) Why this makes sense

* **Phenomenology:** Responsiveness follows BOTH external stimulation AND internal activation (rumination, generative overflow). Arousal keeps mind active even during pauses.
* **Bio‑inspiration:** Arousal rhythms speed up under input, slow down at rest. Internal thought momentum (mind wandering, rumination) maintains activity without external stimuli.
* **Systems‑dynamics:** ρ loop maintains stability independent of tick speed; dt cap prevents huge one‑shot transfers; three-factor minimum ensures mind stays active when any factor demands it.

## 4) Expected behaviors

* **Conversation** → sub‑second to seconds ticks (stimulus-driven).
* **Post-conversation processing** → fast ticks continue briefly (activation-driven autonomous momentum).
* **Rumination** → fast ticks without new inputs (activation-driven high internal energy).
* **Anxious/excited states** → prevents very slow ticks via arousal floor.
* **Dormancy** → minutes (all three factors low).
* After long sleep, first frame uses **capped dt**, then quickly adapts to whichever factor dominates.

## 5) Why this vs alternatives

| Alternative                      | Issue                                   | This mechanism         |
| -------------------------------- | --------------------------------------- | ---------------------- |
| Make ρ directly change tick rate | Conflates stability with responsiveness | Separate control loops |
| Fixed tick rate                  | Wastes compute / sluggish               | Adaptive + bounded     |
| Use raw interval as dt           | First tick blow‑ups                     | `dt_cap` guard         |

## 6) Observability — How & what

* **Events:** `tick.update` with:
  ```json
  {
      "event": "tick.update",
      "interval_next": 0.5,
      "dt_used": 0.5,
      "reason": "activation",  # stimulus | activation | arousal_floor
      "details": {
          "interval_stimulus": 2.0,
          "interval_activation": 0.5,
          "interval_arousal": 1.0,
          "total_active_energy": 8.3,
          "mean_arousal": 0.42
      },
      "rho": 1.02,
      "notes": []
  }
  ```
* **Metrics:** Tick rate over time; **computational savings**; dt cap hits; reason distribution (% stimulus vs activation vs arousal).
* **Dashboards:** Per‑mode strips ("conversation", "autonomous_momentum", "rumination", "dormant"); three-factor timeline showing which factor dominates when.

## 7) Failure modes & guards

| Risk                     | Why bad          | Guard                                              |
| ------------------------ | ---------------- | -------------------------------------------------- |
| Oscillation after bursts | Jittery UX       | EMA smoothing; min dwell                           |
| Always at min interval   | Hot CPU          | min interval still bounded; ρ loop dampens physics |
| Over‑long first tick     | Over‑integration | `DT_CAP`                                           |

## 8) Integration in code

* **Where:** `consciousness_engine_v2.py` (scheduler + dt cap; calls `traversal_v2.run_frame(dt)`), `foundations/criticality` (ρ loop).
* **Settings:** `{MIN_INTERVAL_MS, MAX_INTERVAL_S, DT_CAP_S, EMA_BETA}`.

## 9) Success criteria

* Latency from stimulus→tick **≤ min_interval**; no dt blow‑ups; stable ρ across mode shifts.

## 10) Open questions / future

* Learn mode‑aware bounds; sleep windows; per‑device budgets.
