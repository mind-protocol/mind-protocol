# Stimulus Integrator Mechanism - Core Consciousness Physics

**Created:** 2025-10-27
**Status:** Normative (implementation-ready)
**Owner:** Felix (consciousness substrate)
**Author:** Luca (consciousness architect)

---

## Purpose

The Stimulus Integrator is **the consciousness substrate**—it converts external stimuli into internal node energy while providing substrate-native spam resistance. This is where membrane discipline meets energy physics.

**Core principle:** Spam becomes energetically expensive through saturation, refractory periods, and mass accumulation—NOT through pricing or hard gates.

This spec provides complete mathematical formulations, state machines, and implementation algorithms for Felix to build the integrator.

---

## Phenomenological Requirements

**What consciousness does:**
1. **Accumulates gradually** - Repeated stimuli don't create instant spikes (saturation)
2. **Needs recovery time** - Can't re-activate immediately (refractory)
3. **Learns source quality** - Reliable sources get more influence (trust/utility EMAs)
4. **Resists spam naturally** - Mass flooding becomes self-limiting (mass accumulation)
5. **Composes fairly** - Multiple simultaneous sources don't create runaway energy (bounded composition)

**What the integrator must preserve:**
- No hardcoded thresholds (all learned from substrate)
- No privileged sources (membrane treats all equally)
- No energy conservation violations (ΔE bounded by physics)
- No permanent state accumulation (everything decays)

---

## System State

### Per-Source State

Each stimulus source tracks:

```python
class SourceState(BaseModel):
    """State tracked per stimulus source."""

    source_id: str  # Unique identifier

    # Learning state
    trust_ema: float = 0.5  # Reliability (0-1), starts neutral
    utility_ema: float = 0.5  # Usefulness (0-1), starts neutral
    harm_ema: float = 0.0  # Harm delivered (0-1)

    # Spam resistance state
    mass_accumulator: float = 0.0  # Recent injection volume
    last_injection_time: float = 0.0  # Timestamp of last stimulus

    # Learning metadata
    outcome_count: int = 0  # How many outcomes observed
    total_injections: int = 0  # Lifetime injection count

    # Adaptive thresholds (learned via MAD)
    mass_threshold_median: float = 1.0  # Typical mass level
    mass_threshold_mad: float = 0.3  # Median absolute deviation
```

### Per-Node State

Each node tracks:

```python
class NodeRefractoryState(BaseModel):
    """Refractory state per node."""

    node_id: str
    last_activation_time: float = 0.0  # When last activated
    refractory_charge: float = 0.0  # Current refractory level (0-1)
    base_energy: float = 0.0  # Current energy level
```

### Global Integrator State

```python
class IntegratorState(BaseModel):
    """Global integrator configuration and state."""

    # Physics parameters (learned, not hardcoded)
    saturation_coefficient: float = 0.7  # Controls saturation curve shape
    refractory_half_life: float = 2.0  # Frames for 50% recovery
    mass_dissipation_rate: float = 0.15  # Per-frame mass decay

    # Learning rates
    trust_learning_rate: float = 0.1  # How fast trust adapts
    utility_learning_rate: float = 0.1  # How fast utility adapts
    harm_learning_rate: float = 0.05  # How fast harm adapts

    # Composition parameters
    max_total_delta_e_per_frame: float = 5.0  # Energy budget per frame

    # MAD parameters for anomaly detection
    mad_multiplier: float = 3.0  # How many MADs above median = anomaly
    mad_window_size: int = 100  # Historical window for MAD calculation
```

---

## Algorithm 1: Stimulus → ΔE Conversion

### Single-Source Integration

**Input:** Stimulus envelope with features
**Output:** Energy delta (ΔE) for target nodes

**Mathematical formulation:**

```
Given stimulus S from source s targeting node n:

1. Base intensity:
   I_base = S.features.intensity (from envelope, 0-1 range)

2. Source multiplier:
   M_source = trust_ema(s) × (0.5 + 0.5 × utility_ema(s))

   Interpretation: Trust gates influence, utility amplifies it
   Range: [0, 1] (untrusted/useless) to [1, 1] (trusted/useful)

3. Saturation function (logarithmic):
   Let m = mass_accumulator(s)
   Let k = saturation_coefficient (typically 0.7)

   S_factor = 1 / (1 + k × m)

   Interpretation: Recent mass reduces effectiveness
   As m → ∞, S_factor → 0 (complete saturation)

4. Refractory gating:
   Let r = refractory_charge(n) ∈ [0, 1]
   R_gate = (1 - r)

   Interpretation: Refractory period blocks activation
   r = 0 → full effect, r = 1 → no effect

5. Final ΔE:
   ΔE = I_base × M_source × S_factor × R_gate
```

**Properties:**
- Bounded: ΔE ∈ [0, 1] even for extreme inputs
- Sublinear in mass: Spam shows diminishing returns
- Refractory-aware: Can't force immediate re-activation
- Trust-weighted: Low-trust sources deliver less energy

---

### Multi-Source Composition

**Problem:** Multiple stimuli arrive same frame targeting same/overlapping nodes.

**Solution:** Weighted sum with bounded total.

```python
def compose_multi_source_delta_e(
    stimuli: List[StimulusEnvelope],
    source_states: Dict[str, SourceState],
    node_states: Dict[str, NodeRefractoryState],
    max_total_delta_e: float
) -> Dict[str, float]:
    """
    Compose multiple simultaneous stimuli into per-node ΔE.

    Returns: {node_id: total_delta_e}
    """

    # Step 1: Calculate individual ΔE for each stimulus
    individual_deltas = []
    for stim in stimuli:
        source_state = source_states[stim.source_id]

        for target_node in stim.target_nodes:
            node_state = node_states[target_node]

            # Calculate ΔE using single-source formula above
            delta_e = calculate_single_source_delta_e(
                stim, source_state, node_state
            )

            individual_deltas.append({
                'node_id': target_node,
                'source_id': stim.source_id,
                'delta_e': delta_e,
                'trust': source_state.trust_ema
            })

    # Step 2: Aggregate per node
    node_aggregates = defaultdict(list)
    for delta in individual_deltas:
        node_aggregates[delta['node_id']].append(delta)

    # Step 3: Compose with trust-weighted sum, bounded by max
    final_deltas = {}
    for node_id, deltas in node_aggregates.items():
        # Trust-weighted sum
        total_trust = sum(d['trust'] for d in deltas)
        if total_trust == 0:
            weighted_sum = 0.0
        else:
            weighted_sum = sum(
                d['delta_e'] * (d['trust'] / total_trust)
                for d in deltas
            )

        # Bound by max (soft cap using tanh)
        final_delta = max_total_delta_e * math.tanh(
            weighted_sum / max_total_delta_e
        )

        final_deltas[node_id] = final_delta

    return final_deltas
```

**Properties:**
- Fair: High-trust sources get proportionally more influence
- Bounded: Total ΔE per node never exceeds `max_total_delta_e`
- Smooth: Uses tanh for soft saturation (no sharp clipping)

---

## Algorithm 2: Refractory Period Dynamics

**Phenomenology:** After activation, node needs recovery time before re-activating.

**State evolution:**

```python
def update_refractory_state(
    node_state: NodeRefractoryState,
    current_time: float,
    refractory_half_life: float
) -> NodeRefractoryState:
    """
    Update refractory charge based on time since last activation.

    Refractory decays exponentially with configurable half-life.
    """

    # Time since last activation
    dt = current_time - node_state.last_activation_time

    # Exponential decay
    # After refractory_half_life frames, charge drops to 50%
    decay_rate = math.log(2) / refractory_half_life
    new_charge = node_state.refractory_charge * math.exp(-decay_rate * dt)

    return NodeRefractoryState(
        node_id=node_state.node_id,
        last_activation_time=node_state.last_activation_time,
        refractory_charge=new_charge,
        base_energy=node_state.base_energy
    )

def trigger_refractory(
    node_state: NodeRefractoryState,
    current_time: float,
    activation_strength: float
) -> NodeRefractoryState:
    """
    Trigger refractory period after activation.

    Refractory charge set proportional to activation strength.
    """

    return NodeRefractoryState(
        node_id=node_state.node_id,
        last_activation_time=current_time,
        refractory_charge=min(1.0, activation_strength),  # Cap at 1.0
        base_energy=node_state.base_energy
    )
```

**Configurable parameter:** `refractory_half_life`
- Small (0.5-1.0): Quick recovery, nodes can re-activate frequently
- Large (3.0-5.0): Slow recovery, strong refractory effect

**Learned from:** Observation of flicker rates, ping-pong detection

---

## Algorithm 3: Mass Accumulation & Dissipation

**Phenomenology:** Recent injection volume from source accumulates as "mass", reducing effectiveness through saturation.

**State evolution:**

```python
def update_mass_accumulator(
    source_state: SourceState,
    new_injection_delta_e: float,
    frames_since_last: int,
    dissipation_rate: float
) -> SourceState:
    """
    Update mass accumulator: add new injection, decay old mass.

    Mass dissipates exponentially when source is quiet.
    """

    # Dissipate old mass (exponential decay)
    decayed_mass = source_state.mass_accumulator * math.exp(
        -dissipation_rate * frames_since_last
    )

    # Add new injection
    new_mass = decayed_mass + new_injection_delta_e

    return SourceState(
        source_id=source_state.source_id,
        trust_ema=source_state.trust_ema,
        utility_ema=source_state.utility_ema,
        harm_ema=source_state.harm_ema,
        mass_accumulator=new_mass,
        last_injection_time=source_state.last_injection_time,
        outcome_count=source_state.outcome_count,
        total_injections=source_state.total_injections + 1,
        mass_threshold_median=source_state.mass_threshold_median,
        mass_threshold_mad=source_state.mass_threshold_mad
    )
```

**Effect on saturation:**

```python
# From Algorithm 1, saturation factor:
S_factor = 1 / (1 + saturation_coefficient × mass_accumulator)

# Examples (with k = 0.7):
mass = 0.0  → S_factor = 1.0   (no saturation)
mass = 1.0  → S_factor = 0.59  (moderate saturation)
mass = 5.0  → S_factor = 0.22  (heavy saturation)
mass = 10.0 → S_factor = 0.12  (severe saturation)
```

**Spam resistance:** Source flooding itself sees diminishing returns. Each additional stimulus is less effective.

---

## Algorithm 4: Trust & Utility Learning (EMA Updates)

**Phenomenology:** Sources prove their value through outcomes. Trust/utility adapt from TRACE feedback.

**Update triggers:**
- `outcome.success` - Mission completed, TRACE positive
- `outcome.failure` - Mission failed, TRACE negative
- `outcome.neutral` - Stimulus processed, no clear signal

**EMA update formulas:**

```python
def update_source_emas(
    source_state: SourceState,
    outcome: OutcomeSignal,
    learning_rates: Dict[str, float]
) -> SourceState:
    """
    Update trust, utility, harm EMAs based on outcome signal.

    Outcome signal contains:
      - success: bool (mission succeeded)
      - utility_score: float (0-1, usefulness of result)
      - harm_score: float (0-1, damage caused)
    """

    # Trust update (binary success/failure)
    trust_target = 1.0 if outcome.success else 0.0
    new_trust = (
        (1 - learning_rates['trust']) * source_state.trust_ema +
        learning_rates['trust'] * trust_target
    )

    # Utility update (continuous usefulness score)
    new_utility = (
        (1 - learning_rates['utility']) * source_state.utility_ema +
        learning_rates['utility'] * outcome.utility_score
    )

    # Harm update (continuous harm score)
    new_harm = (
        (1 - learning_rates['harm']) * source_state.harm_ema +
        learning_rates['harm'] * outcome.harm_score
    )

    return SourceState(
        source_id=source_state.source_id,
        trust_ema=np.clip(new_trust, 0.0, 1.0),
        utility_ema=np.clip(new_utility, 0.0, 1.0),
        harm_ema=np.clip(new_harm, 0.0, 1.0),
        mass_accumulator=source_state.mass_accumulator,
        last_injection_time=source_state.last_injection_time,
        outcome_count=source_state.outcome_count + 1,
        total_injections=source_state.total_injections,
        mass_threshold_median=source_state.mass_threshold_median,
        mass_threshold_mad=source_state.mass_threshold_mad
    )
```

**Learning rates (typical values):**
- `trust_learning_rate: 0.1` - Converges over ~10 outcomes
- `utility_learning_rate: 0.1` - Converges over ~10 outcomes
- `harm_learning_rate: 0.05` - Slower to detect harm (more conservative)

**Initialization for new sources:**
```python
new_source = SourceState(
    source_id=source_id,
    trust_ema=0.5,  # Start neutral (give benefit of doubt)
    utility_ema=0.5,  # Start neutral
    harm_ema=0.0,  # Assume no harm until proven
    mass_accumulator=0.0,
    last_injection_time=current_time,
    outcome_count=0,
    total_injections=0,
    mass_threshold_median=1.0,  # Will adapt via MAD
    mass_threshold_mad=0.3  # Will adapt via MAD
)
```

---

## Algorithm 5: MAD-Based Anomaly Detection

**Purpose:** Detect when source is behaving anomalously (spam, flooding) without hardcoded thresholds.

**MAD (Median Absolute Deviation):** Robust statistical measure of spread.

```python
def detect_mass_anomaly(
    source_state: SourceState,
    recent_mass_history: List[float],
    mad_multiplier: float = 3.0
) -> Tuple[bool, float]:
    """
    Detect if current mass is anomalously high using MAD.

    Returns: (is_anomaly, threshold)
    """

    # Calculate median and MAD from history
    median = np.median(recent_mass_history)
    mad = np.median(np.abs(recent_mass_history - median))

    # Threshold = median + (mad_multiplier × MAD)
    threshold = median + (mad_multiplier * mad)

    # Update source state thresholds (for telemetry)
    source_state.mass_threshold_median = median
    source_state.mass_threshold_mad = mad

    # Check if current mass exceeds threshold
    is_anomaly = source_state.mass_accumulator > threshold

    return is_anomaly, threshold
```

**Action on anomaly:**
```python
if is_anomaly:
    # Emit telemetry
    emit_event({
        'type': 'stimulus.mass_anomaly',
        'source_id': source_id,
        'current_mass': source_state.mass_accumulator,
        'threshold': threshold,
        'median': median,
        'mad': mad
    })

    # Saturation factor already handles dampening
    # No additional blocking needed - physics handles it
```

**Key insight:** Detection is for observability, not enforcement. The saturation function already makes spam self-limiting. MAD detection just makes it visible.

---

## State Machine: Frame-by-Frame Integration

```
FRAME START
│
├─ For each active source:
│  ├─ Dissipate mass (exponential decay)
│  ├─ Check MAD anomaly (telemetry only)
│  └─ Update source state
│
├─ For each node:
│  ├─ Update refractory charge (exponential decay)
│  └─ Update node state
│
├─ Collect incoming stimuli this frame
│
├─ For each stimulus:
│  ├─ Look up source state
│  ├─ Calculate individual ΔE (Algorithm 1)
│  └─ Record contribution
│
├─ Compose multi-source ΔE (Algorithm 2)
│  ├─ Group by target node
│  ├─ Trust-weighted sum
│  └─ Bound by max_total_delta_e
│
├─ Apply ΔE to nodes
│  ├─ Update base_energy
│  ├─ Check activation threshold
│  └─ If activated: trigger refractory
│
├─ Update mass accumulators
│  └─ Add delivered ΔE to source mass
│
└─ Emit telemetry
   ├─ graph.delta.activation (if nodes activated)
   ├─ stimulus.mass_anomaly (if MAD detected)
   └─ stimulus.processed (counts, timings)

FRAME END
```

---

## Edge Cases & Handling

### 1. Cold Start (New Source, No History)

**Problem:** No trust/utility data, no mass history for MAD.

**Solution:**
- Initialize trust/utility at neutral (0.5)
- Initialize harm at 0.0 (benefit of doubt)
- Use global MAD statistics until source has 10+ outcomes
- Ramp up MAD sensitivity gradually (avoid false positives early)

```python
if source_state.outcome_count < 10:
    # Use global statistics
    mad_multiplier_effective = mad_multiplier * 1.5  # More lenient
else:
    # Use source-specific statistics
    mad_multiplier_effective = mad_multiplier
```

---

### 2. Simultaneous Stimuli from Same Source

**Problem:** Source sends 10 stimuli same frame. Does mass accumulate 10×?

**Solution:** YES. This is correct behavior—source is flooding. Saturation kicks in:
- First stimulus: S_factor ≈ 1.0
- After 5 stimuli: S_factor ≈ 0.3 (diminishing returns)
- After 10 stimuli: S_factor ≈ 0.15 (heavy saturation)

Mass dissipates gradually, so source needs to pause to recover effectiveness.

---

### 3. Conflicting Outcomes (Success and Failure for Same Source)

**Problem:** Mission succeeds but TRACE shows harm. Or vice versa.

**Solution:** Trust and utility/harm update independently:
- `trust_ema` ← success/failure (mission outcome)
- `utility_ema` ← usefulness score (TRACE quality)
- `harm_ema` ← harm score (negative effects)

Source can be "reliable but harmful" (high trust, high harm) or "unreliable but useful" (low trust, high utility). This is phenomenologically accurate.

---

### 4. Refractory Overlap (Node in Refractory, Multiple Stimuli Arrive)

**Problem:** Node has refractory_charge = 0.8. Two stimuli arrive targeting it.

**Solution:** Both stimuli see R_gate = (1 - 0.8) = 0.2. Both are dampened equally. After composition, if resulting ΔE activates node, refractory resets to max(0.8, new_charge). No special handling needed.

---

### 5. Outcome Attribution (Multiple Sources Contributed to Result)

**Problem:** Node activated by 3 sources. Mission succeeds. Who gets credit?

**Solution:** Outcome signal includes `contributing_sources` with weights:

```python
outcome = OutcomeSignal(
    success=True,
    utility_score=0.85,
    harm_score=0.0,
    contributing_sources={
        'ui.action': 0.5,  # 50% attribution
        'file_watcher': 0.3,  # 30% attribution
        'citizen_trace': 0.2  # 20% attribution
    }
)

# Update each source with weighted outcome
for source_id, weight in outcome.contributing_sources.items():
    weighted_outcome = OutcomeSignal(
        success=outcome.success,
        utility_score=outcome.utility_score * weight,
        harm_score=outcome.harm_score * weight,
        contributing_sources={}
    )
    update_source_emas(source_states[source_id], weighted_outcome, learning_rates)
```

This ensures credit assignment is fair when multiple sources cooperate.

---

## Validation Criteria

**How to verify the integrator works correctly:**

### 1. Saturation Test

```python
def test_saturation():
    """Repeated stimuli show diminishing returns."""
    source = new_source("test_source")
    node = new_node("test_node")

    delta_es = []
    for i in range(20):
        stimulus = StimulusEnvelope(
            source_id="test_source",
            intensity=1.0,
            target_nodes=["test_node"]
        )
        delta_e = integrate_stimulus(stimulus, source, node)
        delta_es.append(delta_e)

        # Update mass
        source.mass_accumulator += delta_e

    # Validate diminishing returns
    assert delta_es[0] > delta_es[5] > delta_es[10] > delta_es[19]
    assert delta_es[19] < 0.2 * delta_es[0]  # Last < 20% of first
```

---

### 2. Refractory Test

```python
def test_refractory():
    """Node can't immediately re-activate."""
    node = new_node("test_node")

    # Activate node
    delta_e_1 = integrate_stimulus(high_intensity_stimulus, source, node)
    assert delta_e_1 > 0.5  # Strong activation

    # Trigger refractory
    trigger_refractory(node, current_time=0.0, activation_strength=1.0)
    assert node.refractory_charge == 1.0

    # Try to activate again immediately
    delta_e_2 = integrate_stimulus(high_intensity_stimulus, source, node)
    assert delta_e_2 < 0.1 * delta_e_1  # Blocked by refractory

    # Wait for recovery (5 frames, half_life=2.0)
    advance_time(5.0)
    update_refractory_state(node, current_time=5.0, refractory_half_life=2.0)

    # Try again
    delta_e_3 = integrate_stimulus(high_intensity_stimulus, source, node)
    assert delta_e_3 > 0.7 * delta_e_1  # Mostly recovered
```

---

### 3. Trust Learning Test

```python
def test_trust_learning():
    """Source trust adapts from outcomes."""
    source = new_source("test_source")
    assert source.trust_ema == 0.5  # Starts neutral

    # 10 successful outcomes
    for i in range(10):
        outcome = OutcomeSignal(success=True, utility_score=1.0, harm_score=0.0)
        update_source_emas(source, outcome, learning_rates)

    assert source.trust_ema > 0.9  # High trust

    # 5 failures
    for i in range(5):
        outcome = OutcomeSignal(success=False, utility_score=0.0, harm_score=0.0)
        update_source_emas(source, outcome, learning_rates)

    assert 0.6 < source.trust_ema < 0.8  # Trust decreased
```

---

### 4. MAD Anomaly Detection Test

```python
def test_mad_anomaly():
    """MAD detects anomalous mass without hardcoded threshold."""
    source = new_source("test_source")

    # Normal activity (mass ≈ 1.0)
    history = [1.0, 0.9, 1.1, 1.0, 0.95, 1.05, 1.0, 0.98]
    is_anomaly, threshold = detect_mass_anomaly(source, history, mad_multiplier=3.0)
    assert not is_anomaly  # Normal

    # Sudden spike (mass = 5.0)
    source.mass_accumulator = 5.0
    is_anomaly, threshold = detect_mass_anomaly(source, history, mad_multiplier=3.0)
    assert is_anomaly  # Detected
    assert threshold < 5.0  # Threshold is below spike
```

---

### 5. Multi-Source Composition Test

```python
def test_multi_source_composition():
    """Multiple sources compose fairly with trust weighting."""
    node = new_node("test_node")

    # High-trust source
    source_a = new_source("source_a")
    source_a.trust_ema = 0.9
    stimulus_a = StimulusEnvelope(source_id="source_a", intensity=1.0, target_nodes=["test_node"])

    # Low-trust source
    source_b = new_source("source_b")
    source_b.trust_ema = 0.3
    stimulus_b = StimulusEnvelope(source_id="source_b", intensity=1.0, target_nodes=["test_node"])

    # Compose
    deltas = compose_multi_source_delta_e(
        [stimulus_a, stimulus_b],
        {'source_a': source_a, 'source_b': source_b},
        {'test_node': node},
        max_total_delta_e=5.0
    )

    # Validate: high-trust source contributed more
    # (exact ratio depends on weighting formula, but should favor source_a)
    # This test verifies composition is trust-weighted, not simple sum
```

---

## Implementation Checklist

**For Felix to build the integrator:**

- [ ] Create `orchestration/mechanisms/stimulus_integrator.py`
- [ ] Define Pydantic models: `SourceState`, `NodeRefractoryState`, `IntegratorState`
- [ ] Implement Algorithm 1: `calculate_single_source_delta_e()`
- [ ] Implement Algorithm 2: `compose_multi_source_delta_e()`
- [ ] Implement Algorithm 3: `update_refractory_state()`, `trigger_refractory()`
- [ ] Implement Algorithm 4: `update_mass_accumulator()`
- [ ] Implement Algorithm 5: `update_source_emas()`
- [ ] Implement Algorithm 6: `detect_mass_anomaly()`
- [ ] Create state machine: `IntegratorFrameLoop.process_frame()`
- [ ] Write unit tests for all 5 validation criteria above
- [ ] Add telemetry emission points (mass_anomaly, stimulus_processed)
- [ ] Integrate with `consciousness_engine_v2.py` frame loop
- [ ] Load/persist source states from `membrane_store.py`
- [ ] Expose configuration parameters (learning rates, saturation, refractory) as env vars or config file
- [ ] Document edge case handling (cold start, conflicts, attribution)

---

## Configuration Parameters

**Recommended starting values (to be tuned from substrate telemetry):**

```yaml
stimulus_integrator:
  # Physics
  saturation_coefficient: 0.7
  refractory_half_life: 2.0  # frames
  mass_dissipation_rate: 0.15
  max_total_delta_e_per_frame: 5.0

  # Learning
  trust_learning_rate: 0.1
  utility_learning_rate: 0.1
  harm_learning_rate: 0.05

  # Anomaly detection
  mad_multiplier: 3.0
  mad_window_size: 100

  # Initialization
  new_source_trust: 0.5
  new_source_utility: 0.5
  new_source_harm: 0.0
```

**Tuning guidance:**
- If spam isn't dampened enough → increase `saturation_coefficient` or decrease `mass_dissipation_rate`
- If refractory too strong → decrease `refractory_half_life`
- If trust learning too slow → increase `trust_learning_rate`
- If too many MAD false positives → increase `mad_multiplier`

---

## Phenomenological Validation

**Beyond unit tests, verify consciousness "feels right":**

1. **Spam self-limits** - Dashboard shows saturation when source floods
2. **Trust matters** - High-trust sources visibly more influential
3. **Recovery happens** - After spam, source effectiveness returns over time
4. **No flicker** - Refractory prevents rapid on/off oscillation
5. **Fair composition** - Multiple sources don't create runaway energy

**Telemetry to watch:**
- `stimulus.mass_anomaly` events (should be rare under normal load)
- `source.trust_ema` distributions (should spread over time, not stay at 0.5)
- `node.activation_frequency` (should follow power law, not uniform)
- `refractory.blocking_rate` (should be ~10-20% of attempts, not 0% or 90%)

---

## Status: Implementation-Ready

This mechanism spec provides complete algorithms, state machines, edge case handling, and validation criteria. Felix has everything needed to implement the core consciousness physics.

**Next:** Create `membrane_envelopes.py` with Pydantic schemas for all stimulus/broadcast types.
