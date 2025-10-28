# Membrane Hardening - Gaming Resistance Without Economy

**Created:** 2025-10-26
**Status:** Normative (Phases 1-2 implementation)
**Purpose:** Make record-based membranes robust against spam/gaming without requiring pricing layer

---

## Why This Matters

**Core question:** Can membrane-only design (no economy, no pricing) resist gaming?

**Answer:** Yes—if you use multi-axis defenses that make spam naturally expensive (in energy, not credits).

This spec details **five hardening mechanisms** that make membranes robust without touching the economy layer. These are substrate-native defenses built into the physics.

---

## The Gaming Threat Model

**What attackers might try:**

1. **Novelty inflation:** Generate random noise to trigger "record novelty" exports constantly
2. **Ping-pong:** Create artificial back-and-forth to inflate flow metrics
3. **Mass injection:** Spam stimuli to crowd out legitimate content
4. **Aligned spam:** Coordinate multiple sources to exploit collective patterns
5. **Permeability gaming:** Find edge cases where κ doesn't decay properly

**Defense strategy:** Make these attacks **self-defeating** through substrate physics, not through payment barriers.

---

## Defense 1: Multi-Axis Pareto Record

**Problem:** Single-axis record (e.g., "highest novelty ever") is trivially gameable with random noise.

**Solution:** Require **Pareto improvement** over recent frontier on **at least two axes** without degrading others.

### Axes for Export Triggering

**Primary axes:**
1. **Novelty** - How different from recent history (embedding distance)
2. **Fit** - How well aligned with receiving level's needs (LIFTS_TO.fit score)
3. **Expected utility** - Predicted usefulness based on source's utility_ema
4. **Trust** - Source's historical reliability (1 - harm_ema)

**Pareto condition:**
```python
def is_pareto_record(
    candidate: Dict,
    recent_frontier: List[Dict]
) -> bool:
    """
    Returns True only if candidate improves on ≥2 axes
    without degrading any axis below acceptable threshold.
    """
    improvements = 0
    acceptable_threshold = 0.3  # Don't degrade axes below this

    for item in recent_frontier:
        if (candidate.novelty > item.novelty and
            candidate.fit > item.fit):
            improvements += 1
        elif (candidate.novelty > item.novelty and
              candidate.expected_utility > item.expected_utility):
            improvements += 1
        # ... (check all axis pairs)

    # Must improve on ≥2 axes AND not degrade any below threshold
    degraded = any([
        candidate.novelty < acceptable_threshold,
        candidate.fit < acceptable_threshold,
        candidate.expected_utility < acceptable_threshold,
        candidate.trust < acceptable_threshold
    ])

    return improvements >= 2 and not degraded
```

**Why this works:**
- **Random noise** has high novelty but low fit/utility → fails Pareto
- **Spam** has low trust → fails threshold check
- **Legitimate insights** naturally improve multiple axes together

---

## Defense 2: MAD-Guarded Change-Points

**Problem:** Fixed percentile thresholds (e.g., "top 5%") create rigid targets that attackers can optimize against.

**Solution:** Use **Median Absolute Deviation (MAD)** to guard change-point detection, making the threshold adaptive to natural noise levels.

### Algorithm: MAD-Adjusted Record Detection

```python
def detect_record_with_mad_guard(
    signal_history: List[float],
    candidate_value: float,
    mad_multiplier: float = 3.0
) -> bool:
    """
    Detect record values while filtering out noise.
    Uses MAD to adapt to signal's natural variance.
    """
    # Compute robust statistics
    median = np.median(signal_history)
    mad = np.median(np.abs(signal_history - median))

    # Adaptive threshold (multiple of MAD above median)
    threshold = median + (mad_multiplier * mad)

    # Record detected if candidate exceeds adaptive threshold
    is_record = candidate_value > threshold

    return is_record
```

**Why MAD instead of standard deviation?**
- **Robust to outliers** - attackers can't inflate threshold by injecting extreme values
- **Adapts to natural noise** - high-variance signals get higher thresholds automatically
- **No fixed percentiles** - threshold moves with substrate reality

**Integration with Pareto:**
```python
def should_trigger_export(candidate, history):
    """
    Combine Pareto improvement with MAD-guarded record detection.
    """
    # Check Pareto improvement on multiple axes
    if not is_pareto_record(candidate, recent_frontier):
        return False

    # Additionally require MAD-significant change on primary axis
    novelty_is_significant = detect_record_with_mad_guard(
        [h.novelty for h in history],
        candidate.novelty,
        mad_multiplier=3.0
    )

    return novelty_is_significant
```

---

## Defense 3: Saturation + Refractory in Integrator

**Problem:** Repeated spam from same source/thread floods the membrane.

**Solution:** Integrator physics naturally clamps repeated arrivals through **mass accumulation** and **refractory periods**.

### How It Works

**Mass accumulation:**
```python
def integrate_stimulus(node, stimulus):
    """
    Repeated arrivals from same source increase mass,
    which reduces delivered ΔE.
    """
    # Track recent arrival mass per source
    source_mass = node.mass_by_source.get(stimulus.source_id, 0.0)

    # Delivered ΔE inversely proportional to accumulated mass
    delivered_delta_e = stimulus.planned_delta_e / (1.0 + source_mass)

    # Accumulate mass for this source
    node.mass_by_source[stimulus.source_id] += delivered_delta_e

    # Mass decays slowly
    decay_mass(node, decay_rate=0.95)

    return delivered_delta_e
```

**Refractory period:**
```python
def check_refractory(node, stimulus):
    """
    Recently activated nodes reduce incoming ΔE.
    """
    time_since_last_activation = now() - node.last_activation_time

    if time_since_last_activation < node.refractory_period:
        # Still in refractory - clamp incoming energy
        refractory_factor = time_since_last_activation / node.refractory_period
        stimulus.planned_delta_e *= refractory_factor

    return stimulus
```

**Effect on spam:**
- **First spam message:** Delivers ~90% of planned ΔE
- **Second spam message (immediate):** Delivers ~45% (mass accumulated)
- **Third spam message:** Delivers ~23%
- **Tenth spam message:** Delivers <5%

**Legitimate use case:** Different sources sending to same target don't accumulate mass (tracked per source_id).

---

## Defense 4: Emission Ledger + Hysteresis

**Problem:** Flicker—same content repeatedly crosses membrane due to noise in triggering conditions.

**Solution:** **Emission ledger** tracks what was already sent; **hysteresis** requires substantial change to re-emit.

### Emission Ledger

**Track on MEMBRANE_TO edge:**
```python
class MembraneProperties(BaseModel):
    """Properties stored on MEMBRANE_TO edge."""
    k_up: float  # Upward permeability
    k_down: float  # Downward permeability
    flow_ema: float  # Flow effectiveness EMA
    eff_ema: float  # Outcome effectiveness EMA

    # Emission ledger
    last_emit_up: Dict  # {"content_hash": str, "timestamp": datetime, "delta_e": float}
    last_emit_down: Dict
    emission_history: List[Dict]  # Last 10 emissions with hashes
```

**Check before emitting:**
```python
def should_emit_upward(membrane, candidate_stimulus):
    """
    Don't re-emit unless significantly changed.
    """
    # Compute content hash
    content_hash = hash_stimulus_content(candidate_stimulus)

    # Check if recently emitted
    if content_hash == membrane.last_emit_up.get("content_hash"):
        time_since = now() - membrane.last_emit_up["timestamp"]

        # Require cooling period before re-emitting same content
        if time_since < timedelta(minutes=30):
            return False

    # Check if in recent history
    recent_hashes = [e["content_hash"] for e in membrane.emission_history[-5:]]
    if content_hash in recent_hashes:
        return False  # Already sent recently

    return True
```

### Hysteresis (Entry > Exit)

**For state transitions (like "should this cross?"):**

```python
def hysteresis_gate(
    value: float,
    threshold_enter: float,
    threshold_exit: float,
    current_state: bool
) -> bool:
    """
    Hysteresis prevents flicker at boundaries.

    - To transition from OFF → ON: value must exceed threshold_enter
    - To transition from ON → OFF: value must fall below threshold_exit
    - threshold_enter > threshold_exit (gap creates hysteresis)
    """
    if current_state:  # Currently ON
        return value >= threshold_exit  # Stay ON unless falls below exit
    else:  # Currently OFF
        return value >= threshold_enter  # Turn ON if exceeds entry
```

**Example:**
- Entry threshold: novelty > 0.8 (high bar to start crossing)
- Exit threshold: novelty < 0.6 (low bar to keep crossing once started)
- Gap (0.6 to 0.8): prevents noise from causing rapid on/off flicker

---

## Defense 5: Outcome-Weighted Permeability Learning

**Problem:** Without economy, how do we prevent bad actors from exploiting membranes?

**Solution:** **Permeabilities (κ_up, κ_down) learn from receiving-side outcomes.** Sources that produce useless/harmful exports naturally get lower κ over time.

### Outcome Signals (Fast, Substrate-Native)

**Positive outcomes:**
1. **TRACE seats** - Exported content gets reinforced on receiving side (utility_seat > 0.5)
2. **Δρ improvement** - Criticality drops after content crosses (less crisis)
3. **Mission success** - Objectives achieved using cross-level content
4. **Coherence increase** - Receiving level's internal consistency improves

**Negative outcomes:**
1. **TRACE harm** - Exported content marked harmful (harm_seat > 0.5)
2. **Δρ degradation** - Criticality rises after content crosses (more crisis)
3. **Mission failure** - Objectives fail due to misleading cross-level content
4. **Coherence decrease** - Receiving level becomes more fragmented

### Permeability Update Rule

**After each cross-level event:**
```python
def update_membrane_permeability(
    membrane: MembraneProperties,
    direction: str,  # "up" or "down"
    outcome_score: float,  # -1 (harmful) to +1 (helpful)
    learning_rate: float = 0.1
):
    """
    Adjust permeability based on receiving-side outcomes.
    Good outcomes → increase κ
    Bad outcomes → decrease κ
    """
    if direction == "up":
        # Update upward permeability
        membrane.k_up += learning_rate * outcome_score * (1.0 - membrane.k_up)
        membrane.k_up = np.clip(membrane.k_up, 0.05, 0.95)  # Keep in bounds

        # Update effectiveness EMA
        membrane.eff_ema = 0.9 * membrane.eff_ema + 0.1 * max(0, outcome_score)

    elif direction == "down":
        # Update downward permeability
        membrane.k_down += learning_rate * outcome_score * (1.0 - membrane.k_down)
        membrane.k_down = np.clip(membrane.k_down, 0.05, 0.95)

        membrane.eff_ema = 0.9 * membrane.eff_ema + 0.1 * max(0, outcome_score)

    emit_event("membrane.permeability.updated", {
        "membrane_id": membrane.id,
        "direction": direction,
        "k_up": membrane.k_up,
        "k_down": membrane.k_down,
        "outcome_score": outcome_score,
        "eff_ema": membrane.eff_ema
    })
```

**Effect over time:**
- **Spammer:** Crosses membrane 50 times, 90% useless → κ_up drops from 0.5 to 0.12
- **Helpful source:** Crosses 50 times, 70% helpful → κ_up rises from 0.5 to 0.78
- **Eventually:** Spammer's exports get clamped to ~10% of requested ΔE; helper gets 80%

**This is self-regulating:** No manual intervention, no pricing—just physics responding to outcomes.

---

## Combined Defense: Layered Hardening

**How the five defenses work together:**

### Example Attack: Novelty Spam

1. **Attacker:** Generates 1000 random messages/minute to inflate novelty
2. **Defense 1 (Pareto):** Random messages fail Pareto check (high novelty but low fit/utility) → 95% rejected immediately
3. **Defense 2 (MAD):** Remaining 5% still need MAD-significant novelty → 90% of those filtered (novelty not significant given noise level)
4. **Defense 3 (Saturation):** ~5 messages cross initially, but mass accumulates rapidly → ΔE delivered drops to <10% by 3rd message
5. **Defense 4 (Ledger):** Duplicate content hashes detected → rejected
6. **Defense 5 (Permeability):** Receiving side marks exports as useless → κ_up drops from 0.5 to 0.1 over 20 events

**Result:** Attack becomes self-defeating. Attacker wastes compute generating spam that barely crosses the membrane and when it does, has minimal energy and learns to get blocked.

---

### Example Attack: Ping-Pong

1. **Attacker:** Coordinates two citizens to artificially inflate cross-level flow
2. **Defense 4 (Ledger):** Same content hash detected within 30min cooling period → rejected
3. **Defense 3 (Refractory):** Target nodes in refractory after first activation → second ping delivers <30% ΔE
4. **Defense 5 (Permeability):** Receiving sides mark ping-pong content as low utility → κ values decay
5. **Defense 1 (Pareto):** Artificial messages unlikely to Pareto-improve on legitimate frontier

**Result:** Ping-pong quickly becomes energetically expensive (low delivered ΔE) and gets naturally suppressed.

---

### Example Attack: Mass Injection

1. **Attacker:** Attempts to flood L1 → L2 with 10,000 stimuli
2. **Defense 3 (Saturation):** Each node has mass tracking per source → ΔE delivered drops exponentially
3. **Defense 2 (MAD):** Only MAD-significant novelty triggers export → bulk spam filtered at source
4. **Defense 5 (Permeability):** As spam proves useless, κ_up drops toward floor (0.05) → only 5% of planned ΔE crosses

**Result:** Mass injection is rate-limited by integrator physics and permeability learning, not by pricing.

---

## Implementation Checklist

**Phase 1 (Weeks 1-2):**
- ✅ Implement Pareto record detection (multi-axis)
- ✅ Implement MAD-guarded change-points
- ✅ Add mass tracking per source in integrator
- ✅ Add refractory period checks
- ✅ Create emission ledger on MEMBRANE_TO edges
- ✅ Add hysteresis to trigger gates

**Phase 2 (Weeks 3-4):**
- ✅ Implement outcome signal collection (TRACE, Δρ, missions)
- ✅ Implement permeability learning from outcomes
- ✅ Add effectiveness EMA tracking
- ✅ Emit membrane.permeability.updated events
- ✅ Add dashboard viz for κ_up/κ_down over time

**Validation:**
- Run attack simulations (novelty spam, ping-pong, mass injection)
- Verify defenses engage as expected
- Measure false positive rate (legitimate content blocked) < 5%
- Measure false negative rate (spam crosses) < 1%

---

## Performance Characteristics

**Computational overhead per stimulus:**
- Pareto check: O(k) where k = frontier size (~10) → <1ms
- MAD computation: O(n) where n = history window (~100) → <5ms
- Mass lookup: O(1) hash table → <0.1ms
- Ledger check: O(1) hash table → <0.1ms
- Permeability update: O(1) → <0.1ms

**Total overhead per stimulus: ~6ms (negligible compared to LLM latency)**

**Memory:**
- Emission ledger: ~1KB per membrane
- Mass tracking: ~100 bytes per (node, source) pair
- MAD history: ~4KB per signal

**Scales linearly with active membranes and nodes.**

---

## Acceptance Tests

### Test 1: Novelty Spam Filtered
**Given:** Attacker sends 100 random messages with high novelty but low fit/utility
**When:** Pareto check runs
**Then:** >95% rejected, <5% cross membrane, delivered ΔE <10% of planned

### Test 2: MAD Adapts to Noise
**Given:** Signal with natural variance σ=0.2
**When:** Candidate value = median + 2σ
**Then:** Not flagged as record (below MAD threshold of 3×MAD)

### Test 3: Mass Accumulation Clamps Spam
**Given:** Source sends 10 identical stimuli in rapid succession
**When:** Integrator processes each
**Then:** 1st delivers 90%, 2nd delivers 45%, 10th delivers <5%

### Test 4: Ledger Prevents Duplicates
**Given:** Content with hash H crosses upward at T0
**When:** Same hash H attempted at T0+10min
**Then:** Rejected (cooling period 30min not elapsed)

### Test 5: Permeability Learns from Outcomes
**Given:** Membrane starts with κ_up = 0.5
**When:** 20 exports produce outcome_score = -0.6 (harmful)
**Then:** κ_up drops below 0.2

### Test 6: Legitimate Content Not Blocked
**Given:** High-quality content with novelty, fit, and utility all >0.7
**When:** All defenses checked
**Then:** Pareto record detected, MAD threshold exceeded, no ledger block, full ΔE delivered

---

## Monitoring and Observability

**Events to track:**

1. **membrane.export.rejected**
   ```json
   {
     "event": "membrane.export.rejected",
     "membrane_id": "L1_felix_to_L2_mind",
     "direction": "up",
     "reason": "pareto_fail|mad_fail|ledger_block|saturation",
     "candidate_novelty": 0.85,
     "candidate_fit": 0.32,
     "timestamp": "2025-10-26T14:45:00Z"
   }
   ```

2. **membrane.saturation.triggered**
   ```json
   {
     "event": "membrane.saturation.triggered",
     "node_id": "subentity_translator",
     "source_id": "external_api",
     "accumulated_mass": 3.2,
     "delivered_delta_e": 0.08,
     "planned_delta_e": 0.5,
     "timestamp": "2025-10-26T14:45:01Z"
   }
   ```

3. **membrane.permeability.degraded**
   ```json
   {
     "event": "membrane.permeability.degraded",
     "membrane_id": "L1_felix_to_L2_mind",
     "direction": "up",
     "k_before": 0.45,
     "k_after": 0.32,
     "reason": "negative_outcomes",
     "recent_outcome_score": -0.5,
     "timestamp": "2025-10-26T14:46:00Z"
   }
   ```

**Dashboard widgets:**
- κ_up/κ_down time series per membrane
- Rejection rate by reason (Pareto, MAD, ledger, saturation)
- Mass accumulation heatmap per node
- Outcome score distribution per source

---

## Status

**Phase:** 1-2 (membrane-only, no economy)
**Complexity:** Medium (5 interacting defenses)
**Implementation time:** 2-3 weeks
**Dependencies:** Core membrane architecture (cross_level_membrane.md)
**Blocks:** None (orthogonal to economy layer)

---

## References

- `cross_level_membrane.md` - Core membrane transfer mechanisms
- `minimal_economy_phase0.md` - Optional flat-price credits (orthogonal)
- `consciousness_economy.md` - Full dynamic pricing (Phase 3, future)
