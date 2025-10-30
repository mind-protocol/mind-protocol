# State-Dependent Weight Modulation

**Status:** Design Specification
**Owner:** Ada (Architect)
**For Implementation:** Felix (Core Consciousness)
**Version:** 1.0
**Date:** 2025-10-29

---

## Executive Summary

SubEntity membership uses **vector-weighted MEMBER_OF edges** with four dimensions:
- `w_semantic` - embedding fit (cortical prediction networks)
- `w_intent` - goal alignment (basal ganglia gating)
- `w_affect` - emotional resonance (LC/NE neuromodulation)
- `w_experience` - usage history (hippocampal consolidation)

During traversal, these **base weights** are modulated by **current state** to produce **effective weights** that control activation spreading.

This spec defines:
1. Where state variables come from (inputs)
2. How effective weights are computed (runtime algorithm)
3. When/where modulation happens (traversal integration)
4. Validation criteria (phenomenological correctness)

---

## Neuroscience Foundation

### Why State-Dependent Modulation?

Consciousness shifts routing based on internal state:

**High arousal** (crisis, excitement):
- Emotional reasoning dominates
- Semantic precision matters less
- Affect-driven activation spreads faster
- → Amplify `w_affect`, dampen `w_semantic`

**High precision** (focused analysis):
- Semantic fit matters more
- Emotional noise suppressed
- Intent gates strongly
- → Amplify `w_semantic` and `w_intent`

**High goal alignment** (mission-critical):
- Goal-relevant paths prioritized
- Intent-aligned SubEntities activate preferentially
- Exploratory drift reduced
- → Amplify `w_intent`, reduce random walk

This matches LC/NE neuromodulation and basal ganglia gating in biological systems.

---

## State Variables (Inputs)

### 1. Arousal (`arousal` ∈ [0,1])

**Definition:** Neuromodulatory drive from LC/NE system

**Inputs:**
- Energy magnitude (global activation level)
- Valence extremity (`|valence|` - intense emotions drive arousal)
- Temporal gradient (rapid energy changes → arousal spike)

**Computation (example):**
```python
def compute_arousal(graph: Graph) -> float:
    """Compute current arousal level from graph state."""

    # Global activation level
    total_energy = sum(node.energy for node in graph.nodes)
    energy_norm = total_energy / len(graph.nodes)

    # Valence extremity (intense emotions)
    avg_valence_abs = np.mean([abs(node.valence) for node in graph.nodes])

    # Temporal gradient (energy change rate)
    energy_delta = (total_energy - graph.prev_total_energy) / graph.dt
    energy_rate = abs(energy_delta) / max(total_energy, 0.01)

    # Combine factors
    arousal = np.clip(
        0.3 * energy_norm +
        0.4 * avg_valence_abs +
        0.3 * energy_rate,
        0.0, 1.0
    )

    return arousal
```

**Interpretation:**
- `arousal = 0.1` → Low arousal (calm, analytical)
- `arousal = 0.5` → Moderate arousal (engaged)
- `arousal = 0.9` → High arousal (crisis, intense emotion)

---

### 2. Goal Alignment (`goal_alignment` ∈ [0,1])

**Definition:** Current intent focus strength

**Inputs:**
- Intent vector magnitude (`||intent||`)
- Intent stability (low variance over recent frames)
- Working memory coherence (how aligned active nodes are)

**Computation (example):**
```python
def compute_goal_alignment(graph: Graph, intent: np.ndarray) -> float:
    """Compute intent focus strength."""

    # Intent vector magnitude
    intent_strength = np.linalg.norm(intent)

    # Intent stability (low variance = stable goal)
    intent_history = graph.intent_history[-10:]  # Last 10 frames
    intent_variance = np.var([np.linalg.norm(i) for i in intent_history])
    intent_stability = 1.0 / (1.0 + intent_variance)

    # Working memory coherence (active nodes align with intent)
    active_nodes = [n for n in graph.nodes if n.energy > 0.5]
    if active_nodes:
        intent_dots = [np.dot(n.embedding, intent) for n in active_nodes]
        wm_coherence = np.mean([max(0, dot) for dot in intent_dots])
    else:
        wm_coherence = 0.0

    # Combine factors
    goal_alignment = np.clip(
        0.4 * intent_strength +
        0.3 * intent_stability +
        0.3 * wm_coherence,
        0.0, 1.0
    )

    return goal_alignment
```

**Interpretation:**
- `goal_alignment = 0.1` → Exploratory mode (diffuse attention)
- `goal_alignment = 0.5` → Moderate focus
- `goal_alignment = 0.9` → Laser-focused (mission-critical task)

---

### 3. Precision (`precision` ∈ [0,1])

**Definition:** Confidence/certainty level (inverse of uncertainty)

**Inputs:**
- Prediction error (low error = high precision)
- Energy distribution entropy (low entropy = confident)
- Temporal stability (low energy variance = stable state)

**Computation (example):**
```python
def compute_precision(graph: Graph) -> float:
    """Compute current precision (inverse uncertainty)."""

    # Prediction error (from predictive coding)
    # Lower error = higher precision
    prediction_error = graph.get_prediction_error()  # ∈ [0,1]
    precision_from_error = 1.0 - prediction_error

    # Energy distribution entropy
    energies = np.array([n.energy for n in graph.nodes])
    energy_probs = energies / (np.sum(energies) + 1e-10)
    entropy = -np.sum(energy_probs * np.log(energy_probs + 1e-10))
    max_entropy = np.log(len(graph.nodes))
    normalized_entropy = entropy / max_entropy
    precision_from_entropy = 1.0 - normalized_entropy

    # Temporal stability
    energy_history = graph.energy_history[-10:]
    energy_variance = np.var(energy_history)
    precision_from_stability = 1.0 / (1.0 + energy_variance)

    # Combine factors
    precision = np.clip(
        0.5 * precision_from_error +
        0.3 * precision_from_entropy +
        0.2 * precision_from_stability,
        0.0, 1.0
    )

    return precision
```

**Interpretation:**
- `precision = 0.1` → High uncertainty (confused, unclear)
- `precision = 0.5` → Moderate confidence
- `precision = 0.9` → High certainty (clear understanding)

---

## Effective Weight Computation

### Runtime Algorithm

**During traversal**, for each MEMBER_OF edge, compute effective weights:

```python
def compute_effective_weights(
    base_weights: Dict[str, float],  # From MEMBER_OF edge
    arousal: float,                  # Current arousal [0,1]
    goal_alignment: float,           # Current intent focus [0,1]
    precision: float                 # Current precision [0,1]
) -> Dict[str, float]:
    """
    Compute state-dependent effective weights.

    Args:
        base_weights: {
            'w_semantic': float,
            'w_intent': float,
            'w_affect': float,
            'w_experience': float
        }
        arousal: Current arousal level
        goal_alignment: Current intent focus
        precision: Current precision/confidence

    Returns:
        Effective weights for this traversal step
    """

    return {
        'w_eff_semantic': base_weights['w_semantic'] * precision,
        'w_eff_intent': base_weights['w_intent'] * goal_alignment,
        'w_eff_affect': base_weights['w_affect'] * arousal,
        'w_eff_experience': base_weights['w_experience']  # Stable
    }
```

### Total Effective Weight

**For activation spreading**, combine effective weights:

```python
def compute_total_effective_weight(eff_weights: Dict[str, float]) -> float:
    """
    Combine effective weights into single activation coefficient.

    Using weighted sum (can be adjusted based on phenomenology).
    """
    return (
        eff_weights['w_eff_semantic'] +
        eff_weights['w_eff_intent'] +
        eff_weights['w_eff_affect'] +
        eff_weights['w_eff_experience']
    ) / 4.0  # Normalized average
```

**Alternative (for experimentation):**
```python
# Option 1: Max (winner-take-all)
total_weight = max(eff_weights.values())

# Option 2: Softmax (competitive)
weights_array = np.array(list(eff_weights.values()))
softmax_weights = np.exp(weights_array) / np.sum(np.exp(weights_array))
total_weight = np.dot(weights_array, softmax_weights)

# Option 3: Multiplicative (all must contribute)
total_weight = np.prod(list(eff_weights.values())) ** 0.25  # Geometric mean
```

**Recommendation:** Start with weighted sum, measure phenomenology, adjust if needed.

---

## Integration with Traversal

### Traversal Flow with State-Dependent Modulation

```python
def traverse_with_modulation(
    graph: Graph,
    source_node: Node,
    intent: np.ndarray,
    dt: float
) -> List[Node]:
    """
    Traverse graph with state-dependent weight modulation.

    Returns:
        Activated nodes after spreading activation
    """

    # 1. Compute current state variables
    arousal = compute_arousal(graph)
    goal_alignment = compute_goal_alignment(graph, intent)
    precision = compute_precision(graph)

    # Emit telemetry
    emit_telemetry({
        'type': 'state_modulation.frame',
        'arousal': arousal,
        'goal_alignment': goal_alignment,
        'precision': precision,
        'timestamp': now()
    })

    # 2. For each outgoing MEMBER_OF edge from source
    activated_nodes = []

    for edge in source_node.outgoing_member_of_edges:
        # Get base weights from edge
        base_weights = {
            'w_semantic': edge.w_semantic,
            'w_intent': edge.w_intent,
            'w_affect': edge.w_affect,
            'w_experience': edge.w_experience
        }

        # Compute effective weights
        eff_weights = compute_effective_weights(
            base_weights, arousal, goal_alignment, precision
        )

        # Compute total activation coefficient
        total_weight = compute_total_effective_weight(eff_weights)

        # Spread activation
        target_node = edge.target
        energy_transfer = source_node.energy * total_weight * dt

        target_node.energy += energy_transfer
        source_node.energy -= energy_transfer

        if target_node.energy > threshold_active:
            activated_nodes.append(target_node)

    return activated_nodes
```

---

## Validation Criteria

### Phenomenological Tests

**Test 1: High Arousal Shifts to Affect-Driven**

```python
# Setup: High arousal state (crisis)
graph.inject_stimulus(valence=0.9, magnitude=0.8)  # Intense positive
arousal = compute_arousal(graph)
assert arousal > 0.7, "High valence should drive arousal"

# Expected: Affect-weighted paths dominate
# SubEntities with high w_affect activate preferentially
# SubEntities with low w_affect but high w_semantic suppressed
```

**Test 2: High Precision Amplifies Semantic Fit**

```python
# Setup: Low prediction error (confident state)
graph.set_prediction_error(0.1)  # High confidence
precision = compute_precision(graph)
assert precision > 0.8, "Low error should yield high precision"

# Expected: Semantic-weighted paths dominate
# SubEntities with high embedding similarity activate
# Emotional noise reduced
```

**Test 3: High Goal Alignment Gates Intent**

```python
# Setup: Strong, stable intent vector
intent = np.array([0, 0, 1.0])  # Z-direction
graph.set_intent(intent, stable=True)
goal_alignment = compute_goal_alignment(graph, intent)
assert goal_alignment > 0.8, "Stable strong intent should align goals"

# Expected: Intent-weighted paths dominate
# SubEntities aligned with intent vector activate
# Orthogonal SubEntities suppressed
```

**Test 4: Experience Remains Stable**

```python
# All state variables change
arousal_t0 = 0.2
arousal_t1 = 0.8

# w_experience effective weight should be unchanged
eff_weights_t0 = compute_effective_weights(base, arousal_t0, 0.5, 0.5)
eff_weights_t1 = compute_effective_weights(base, arousal_t1, 0.5, 0.5)

assert eff_weights_t0['w_eff_experience'] == eff_weights_t1['w_eff_experience']
```

---

## Edge Cases and Constraints

### 1. State Variable Clamping

All state variables must be clamped to [0,1]:
```python
arousal = np.clip(arousal, 0.0, 1.0)
goal_alignment = np.clip(goal_alignment, 0.0, 1.0)
precision = np.clip(precision, 0.0, 1.0)
```

### 2. Zero Energy Handling

If source node has zero energy:
```python
if source_node.energy < epsilon:
    return []  # No activation spreading
```

### 3. Numerical Stability

Prevent division by zero and overflow:
```python
# Safe normalization
total_energy = max(sum(energies), 1e-10)
energy_norm = total_energy / len(graph.nodes)

# Safe log
entropy = -np.sum(probs * np.log(probs + 1e-10))
```

### 4. Degenerate Cases

**All base weights zero:**
```python
if sum(base_weights.values()) < epsilon:
    # No path exists, skip this edge
    continue
```

**All effective weights zero (extreme precision=0, arousal=0, etc.):**
```python
total_weight = compute_total_effective_weight(eff_weights)
if total_weight < epsilon:
    # Effectively blocked, minimal transfer
    energy_transfer = source_node.energy * epsilon * dt
```

---

## Telemetry Events

Emit state modulation telemetry every frame:

```python
{
    "type": "state_modulation.frame",
    "timestamp": "2025-10-29T20:30:00Z",
    "arousal": 0.73,
    "goal_alignment": 0.45,
    "precision": 0.62,
    "state_interpretation": "high_arousal_exploratory",  # Optional label
    "energy_norm": 0.58,
    "intent_strength": 0.41,
    "prediction_error": 0.38
}
```

For debugging individual edges:

```python
{
    "type": "state_modulation.edge",
    "timestamp": "2025-10-29T20:30:00Z",
    "edge_id": "subentity_42_MEMBER_OF_subentity_17",
    "base_weights": {
        "w_semantic": 0.7,
        "w_intent": 0.3,
        "w_affect": 0.5,
        "w_experience": 0.6
    },
    "effective_weights": {
        "w_eff_semantic": 0.434,   # 0.7 × 0.62 (precision)
        "w_eff_intent": 0.135,     # 0.3 × 0.45 (goal_alignment)
        "w_eff_affect": 0.365,     # 0.5 × 0.73 (arousal)
        "w_eff_experience": 0.6    # Stable
    },
    "total_effective_weight": 0.3835,
    "energy_transfer": 0.042
}
```

---

## Implementation Checklist

**For Felix (Core Consciousness):**

- [ ] Implement `compute_arousal(graph)` from global state
- [ ] Implement `compute_goal_alignment(graph, intent)` from intent vector
- [ ] Implement `compute_precision(graph)` from prediction error + entropy
- [ ] Implement `compute_effective_weights()` runtime modulation
- [ ] Integrate into traversal loop (spreading activation)
- [ ] Add state variable telemetry emission
- [ ] Add edge-level telemetry (debug mode)
- [ ] Write unit tests for phenomenological validation
- [ ] Test edge cases (zero energy, zero weights, numerical stability)

**Success Criteria:**
- State variables computed correctly from graph state
- Effective weights modulate as expected
- Phenomenological tests pass (arousal → affect-driven, etc.)
- Telemetry shows state-dependent activation patterns
- No numerical instability or crashes

---

## Open Questions for Luca

1. **Combination function**: Weighted sum vs max vs softmax for total effective weight?
2. **State variable weighting**: Are the factor weightings (0.3, 0.4, 0.3 etc.) correct?
3. **Arousal from valence**: Should arousal be `|valence|` (extremity) or something else?
4. **Precision from prediction error**: Is this the right coupling?

**Next Review:** After Felix implements, validate phenomenology with real traversals.

---

**Author:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-29
**For Implementation:** Felix (Core Consciousness)
**Handoff from:** Luca (SubEntity emergence spec v2.1)
