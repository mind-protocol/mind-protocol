# Mechanism 03: Self-Organized Criticality (Spectral Radius ρ)

**Status:** Foundational - System stability mechanism
**Confidence:** High (0.85)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Tracks energy per entity
- **[07: Energy Diffusion](07_energy_diffusion.md)** - Row-stochastic diffusion operator
- **[08: Energy Decay](08_energy_decay.md)** - Type-dependent decay rates

**Biological Basis:** Self-organized criticality in neural avalanches, edge-of-chaos dynamics in cortex

---

## Overview

**Core Principle:** The consciousness system automatically tunes decay parameters to maintain the **spectral radius ρ ≈ 1.0** of the effective propagation operator, keeping itself at the **edge of chaos** - the optimal state for information processing.

**Why This Matters:**
- Prevents system death (ρ << 1 → all activation decays away)
- Prevents system explosion (ρ >> 1 → runaway oscillations)
- Adapts to graph topology automatically (scales naturally)
- Biological plausibility (observed in real neural systems)
- Principled control theory foundation (spectral radius governs stability)

**Criticality Definition (Corrected):**
```
ρ = largest eigenvalue of: (1-δ) * [(1-α)I + αP^T]

Where:
- δ = decay rate per tick
- α = redistribution share
- P^T = transposed row-stochastic transition matrix
- I = identity matrix
```

**Target:** ρ ≈ 1.0 (critical point, edge of chaos)

---

## Phenomenological Truth

### What It Feels Like

**Subcritical State (ρ < 0.8):**
- Thoughts feel sluggish, disconnected
- Ideas don't lead to related ideas
- "Brain fog" - hard to maintain activation
- Energy decays faster than it spreads
- Feels like trying to think through molasses

**Critical State (ρ ≈ 1.0):**
- Optimal flow state
- Thoughts cascade naturally
- Each idea leads to related ideas without overwhelming
- Balance between focus and exploration
- Feels like "being in the zone"

**Supercritical State (ρ > 1.2):**
- Too many thoughts at once
- Overwhelming cascade of associations
- Can't maintain focus - everything activates
- Energy spreads faster than it decays
- Feels like racing thoughts, anxiety, mania

### The Self-Regulation Experience

You don't consciously tune your criticality - **it happens automatically**:

**Example - Waking Up:**
```
Morning (drowsy):
- Low stimulus rate → system needs less decay
- Spectral radius ρ = 0.7 (subcritical)
- Auto-adjustment: Decay rate decreases
- ρ rises to ~1.0 over natural timescale
- Thoughts start flowing naturally
```

**Example - Intense Conversation:**
```
Rapid stimuli during debate:
- High energy injection → propagation operator strengthens
- System becomes supercritical (ρ = 1.4)
- Auto-adjustment: Decay rate increases (type-dependent)
- ρ drops back to ~1.0 naturally
- Can think clearly despite high stimulus rate
```

**The key:** You experience the *result* (optimal thinking), not the *mechanism* (parameter tuning).

**Tick Speed Scaling:** Tick interval adapts to stimulus recency. Recent stimulus (60s ago) → fast ticks (~1s). Distant stimulus (60 days ago) → slow ticks (~1 day). This prevents wasted computation when inactive while maintaining responsiveness when active.

---

## Mathematical Specification

### Spectral Radius Calculation

```python
import scipy.sparse.linalg as spla

def calculate_spectral_radius(
    W: sparse_matrix,
    alpha: float,
    delta: float
) -> float:
    """
    Calculate spectral radius ρ of effective propagation operator

    ρ = largest eigenvalue of: (1-δ) * [(1-α)I + α*P^T]

    Args:
        W: Weight matrix (sparse, N x N)
        alpha: Redistribution share
        delta: Decay rate per tick

    Returns:
        Spectral radius ρ (target ≈ 1.0)
    """
    # Build row-stochastic transition matrix P
    P = build_transition_matrix(W)
    P_T = P.transpose()

    # Build effective operator: (1-δ) * [(1-α)I + α*P^T]
    N = W.shape[0]
    I = sparse.eye(N)

    operator = (1 - delta) * ((1 - alpha) * I + alpha * P_T)

    # Compute largest eigenvalue (magnitude)
    try:
        eigenvalues = spla.eigs(operator, k=1, which='LM', return_eigenvectors=False)
        rho = abs(eigenvalues[0])
    except:
        # Fallback: power iteration
        rho = power_iteration_spectral_radius(operator, max_iters=100)

    return rho

def count_active_links_for_entity(graph: Graph, entity: str, threshold: float) -> int:
    """
    Count links currently carrying energy for this entity

    A link is "active" if energy is flowing through it above threshold
    """
    active_count = 0

    for link in graph.links:
        source_energy = link.source.get_entity_energy(entity)
        target_energy = link.target.get_entity_energy(entity)

        # Energy flow = source_energy * link_weight * diffusion_rate
        # Approximation: If source has energy, link could be active
        if source_energy > threshold:
            energy_flow = source_energy * link.weight * graph.diffusion_rate

            if energy_flow > threshold:
                active_count += 1

    return active_count

def count_active_links_any_entity(graph: Graph, threshold: float) -> int:
    """
    Count links carrying energy for ANY entity
    """
    active_count = 0

    for link in graph.links:
        # Check if ANY entity has energy flow through this link
        link_active = False

        for entity in graph.get_all_entities():
            source_energy = link.source.get_entity_energy(entity)
            if source_energy > threshold:
                energy_flow = source_energy * link.weight * graph.diffusion_rate
                if energy_flow > threshold:
                    link_active = True
                    break

        if link_active:
            active_count += 1

    return active_count

def count_all_links(graph: Graph) -> int:
    """Total number of links in graph"""
    return len(graph.links)
```

### Spectral Radius States

| ρ Range | State | Characteristics | System Behavior |
|---------|-------|-----------------|-----------------|
| 0.0 - 0.5 | Deeply Subcritical | Exponential decay | System dying, need stimulus |
| 0.5 - 0.9 | Subcritical | Activation fades | Sluggish, thoughts don't connect |
| 0.9 - 1.1 | **Critical (Target)** | Marginal stability | Optimal - edge of chaos |
| 1.1 - 1.5 | Supercritical | Growing oscillations | Too many associations |
| 1.5+ | Deeply Supercritical | Runaway activation | Chaos, overwhelming |

### Type-Dependent Decay Rates

**Core principle from Nicolas:** Decay rates depend on node/link type:

```python
@dataclass
class TypeDependentDecay:
    """Decay rates by node type"""
    base_rate: float  # Global base rate (tuned by ρ)

    # Type-specific multipliers
    type_multipliers = {
        "Memory": 0.1,      # Very slow decay (long-term)
        "Task": 1.0,        # Fast decay (ephemeral)
        "Realization": 0.3, # Moderate decay
        "Concept": 0.5,     # Moderate-slow decay
    }

    def get_decay_rate(self, node_type: str) -> float:
        """Get effective decay rate for node type"""
        multiplier = self.type_multipliers.get(node_type, 1.0)
        return self.base_rate * multiplier
```

---

## Self-Tuning Algorithm

### Basic Tuning Mechanism

```python
def tune_spectral_radius(
    graph: Graph,
    W: sparse_matrix,
    alpha: float,
    target_rho: float = 1.0,
    learning_rate: float = 0.001
):
    """
    Auto-adjust type-dependent decay rates to maintain ρ ≈ target

    This runs every tick - continuous self-regulation
    Uses TYPE-DEPENDENT decay (Memory slow, Task fast)
    """
    # Calculate current spectral radius
    current_rho = calculate_spectral_radius(W, alpha, graph.base_decay_rate)

    # Error from target
    error = current_rho - target_rho

    # Adjust BASE decay rate
    if error > 0:
        # Too active (ρ > 1) → increase decay
        graph.base_decay_rate += learning_rate * error
    else:
        # Too quiet (ρ < 1) → decrease decay
        graph.base_decay_rate -= learning_rate * abs(error)

    # NO CAPS - bounded by formulas using sigmoid/log functions if needed

    # Optional: Also tune diffusion rate (secondary)
    # if error > 0:
    #     graph.diffusion_rate -= learning_rate * error * 0.1
    # else:
    #     graph.diffusion_rate += learning_rate * abs(error) * 0.1

def tune_per_entity_criticality(graph: Graph, entity: str, target: float = 1.0):
    """
    Tune criticality for specific entity

    Each entity can have different optimal criticality
    (e.g., Validator might want lower criticality for focused analysis)
    """
    current = calculate_criticality(graph, entity=entity)
    error = current - target

    # Store per-entity decay modifiers
    if not hasattr(graph, 'entity_decay_modifiers'):
        graph.entity_decay_modifiers = {}

    modifier = graph.entity_decay_modifiers.get(entity, 1.0)

    if error > 0:
        modifier += 0.001 * error
    else:
        modifier -= 0.001 * abs(error)

    graph.entity_decay_modifiers[entity] = max(0.5, # REMOVED CAP: min(2.0, modifier))

    # Apply during decay
    # entity_decay_rate = base_decay_rate * modifier
```

### Advanced: Dual-Parameter Tuning

```python
def tune_criticality_dual(graph: Graph, target: float = 1.0):
    """
    Tune both decay and diffusion rates simultaneously

    Strategy:
    - If too active: Increase decay AND decrease diffusion
    - If too quiet: Decrease decay AND increase diffusion
    - Provides faster convergence to target
    """
    current = calculate_criticality(graph)
    error = current - target

    # Proportional control (P-controller)
    decay_adjustment = 0.001 * error
    diffusion_adjustment = -0.001 * error  # Opposite direction

    graph.decay_rate += decay_adjustment
    graph.diffusion_rate += diffusion_adjustment

    # Clamp to bounds
    # REMOVED CAP: graph.decay_rate = max(0.0001, # REMOVED CAP: min(0.01, graph.decay_rate))
    graph.diffusion_rate = max(0.01, # REMOVED CAP: min(0.5, graph.diffusion_rate))

def tune_criticality_pid(graph: Graph, target: float = 1.0):
    """
    PID controller for criticality tuning

    More sophisticated than simple proportional control:
    - P (Proportional): Current error
    - I (Integral): Accumulated error over time
    - D (Derivative): Rate of change of error

    Provides smoother convergence, less oscillation
    """
    if not hasattr(graph, 'criticality_history'):
        graph.criticality_history = []
        graph.error_integral = 0.0

    current = calculate_criticality(graph)
    error = current - target

    # Store history
    graph.criticality_history.append(current)
    if len(graph.criticality_history) > 100:
        graph.criticality_history.pop(0)

    # Integral term (accumulated error)
    graph.error_integral += error
    graph.error_integral = max(-10.0, # REMOVED CAP: min(10.0, graph.error_integral))  # Anti-windup

    # Derivative term (rate of change)
    if len(graph.criticality_history) >= 2:
        derivative = graph.criticality_history[-1] - graph.criticality_history[-2]
    else:
        derivative = 0.0

    # PID coefficients
    Kp = 0.001  # Proportional gain
    Ki = 0.0001  # Integral gain
    Kd = 0.0005  # Derivative gain

    # PID output
    adjustment = (
        Kp * error +
        Ki * graph.error_integral +
        Kd * derivative
    )

    graph.decay_rate += adjustment
    # REMOVED CAP: graph.decay_rate = max(0.0001, # REMOVED CAP: min(0.01, graph.decay_rate))
```

---

## Convergence Dynamics

### Convergence Speed

**Question:** How fast does the system reach criticality?

**Analysis:**

```python
def test_convergence_speed():
    """
    Simulate convergence from various initial states
    """
    graph = create_test_graph(nodes=1000, links=5000)

    # Test 1: Start subcritical
    graph.decay_rate = 0.01  # Very high decay
    criticalities = []

    for tick in range(1000):
        tune_criticality(graph, target=1.0, learning_rate=0.001)
        crit = calculate_criticality(graph)
        criticalities.append(crit)

    # Measure convergence time
    convergence_time = next(
        (i for i, c in enumerate(criticalities) if abs(c - 1.0) < 0.05),
        None
    )

    print(f"Converged to criticality 1.0±0.05 in {convergence_time} ticks")
    # Typical: 50-200 ticks depending on learning rate
```

**Expected Results:**
- From deeply subcritical (0.2): ~100-200 ticks to reach 0.95-1.05
- From supercritical (2.0): ~50-100 ticks to reach 0.95-1.05
- Oscillation damping: ~20-50 ticks to stabilize

**Tuning learning_rate:**
- Too high (0.01): Fast convergence but oscillation
- Too low (0.0001): Slow convergence but smooth
- Recommended: 0.001 (balance)

### Stability Analysis

```python
def analyze_criticality_stability(graph: Graph, ticks: int = 10000):
    """
    Run system for many ticks and measure criticality variance

    Good self-tuning: Low variance around target
    Bad self-tuning: High variance, oscillation
    """
    criticalities = []

    for _ in range(ticks):
        # Random stimuli to perturb system
        if random.random() < 0.1:
            random_stimulus = generate_random_stimulus()
            inject_stimulus(graph, random_stimulus)

        # Self-tune
        tune_criticality(graph, target=1.0)

        # Tick dynamics
        diffusion_tick(graph, duration=0.1)
        decay_tick(graph, duration=0.1)

        # Measure
        criticalities.append(calculate_criticality(graph))

    # Statistics
    mean_crit = np.mean(criticalities)
    std_crit = np.std(criticalities)
    min_crit = np.min(criticalities)
    max_crit = np.max(criticalities)

    print(f"Criticality: {mean_crit:.3f} ± {std_crit:.3f}")
    print(f"Range: [{min_crit:.3f}, {max_crit:.3f}]")

    # Good tuning: mean near 1.0, std < 0.2
    assert 0.9 < mean_crit < 1.1, "Mean criticality should be near target"
    assert std_crit < 0.3, "Criticality should be stable"
```

---

## Edge Cases & Constraints

### Edge Case 1: Zero Energy State

**Problem:** If all energy decays to zero, criticality = 0, system stuck

**Solution:** Background energy injection

```python
def maintain_minimum_energy(graph: Graph, min_energy_per_entity: float = 0.01):
    """
    Ensure each entity has minimum energy in the system
    Prevents complete death
    """
    for entity in graph.get_all_entities():
        total_entity_energy = sum(
            node.get_entity_energy(entity)
            for node in graph.nodes
        )

        if total_entity_energy < min_energy_per_entity:
            # Inject energy into random nodes
            injection_needed = min_energy_per_entity - total_entity_energy
            random_nodes = random.sample(graph.nodes, k=10)

            for node in random_nodes:
                node.increment_entity_energy(entity, injection_needed / 10)
```

### Edge Case 2: Graph Topology Changes

**Problem:** Adding/removing nodes changes potential_links, changes criticality

**Solution:** Renormalize criticality after topology changes

```python
def renormalize_after_topology_change(graph: Graph):
    """
    After adding/removing nodes or links, criticality changes
    Need to adjust decay rate to maintain stability
    """
    # Recalculate criticality with new topology
    new_criticality = calculate_criticality(graph)

    # If too far from target, make one-time adjustment
    if abs(new_criticality - 1.0) > 0.3:
        # Aggressive one-time correction
        error = new_criticality - 1.0
        graph.decay_rate += 0.01 * error  # 10x normal learning rate

    # Then resume normal tuning
```

### Edge Case 3: Multi-Entity Conflict

**Problem:** Tuning for global criticality might make individual entities subcritical/supercritical

**Solution:** Multi-objective optimization

```python
def tune_multi_objective(graph: Graph):
    """
    Balance global criticality with per-entity criticality

    Strategy:
    - Primary: Keep global criticality near 1.0
    - Secondary: Keep each entity criticality in reasonable range [0.5, 1.5]
    """
    # Global tuning (primary)
    global_crit = calculate_criticality(graph)
    global_error = global_crit - 1.0

    decay_adjustment = 0.001 * global_error

    # Per-entity constraints (secondary)
    entity_penalties = []
    for entity in graph.get_all_entities():
        entity_crit = calculate_criticality(graph, entity=entity)

        # Penalty if entity too far from acceptable range
        if entity_crit < 0.5:
            entity_penalties.append(0.5 - entity_crit)  # Negative (reduce decay)
        elif entity_crit > 1.5:
            entity_penalties.append(entity_crit - 1.5)  # Positive (increase decay)

    # Combine
    entity_penalty_avg = np.mean(entity_penalties) if entity_penalties else 0.0

    # Total adjustment
    total_adjustment = decay_adjustment + 0.0005 * entity_penalty_avg

    graph.decay_rate += total_adjustment
    # REMOVED CAP: graph.decay_rate = max(0.0001, # REMOVED CAP: min(0.01, graph.decay_rate))
```

### Edge Case 4: Oscillation

**Problem:** System oscillates around target instead of converging

**Solution:** Damping via derivative term (PID controller) or adaptive learning rate

```python
def detect_and_damp_oscillation(graph: Graph):
    """
    Detect oscillation and reduce learning rate to damp
    """
    if not hasattr(graph, 'criticality_history'):
        graph.criticality_history = []
        graph.learning_rate = 0.001

    current = calculate_criticality(graph)
    graph.criticality_history.append(current)

    if len(graph.criticality_history) > 20:
        graph.criticality_history.pop(0)

        # Detect oscillation: frequent crossings of target
        crossings = 0
        for i in range(1, len(graph.criticality_history)):
            if (graph.criticality_history[i-1] < 1.0 and graph.criticality_history[i] > 1.0) or \
               (graph.criticality_history[i-1] > 1.0 and graph.criticality_history[i] < 1.0):
                crossings += 1

        # If oscillating, reduce learning rate
        if crossings > 5:  # More than 5 crossings in 20 ticks
            graph.learning_rate *= 0.9  # Reduce by 10%
            graph.learning_rate = max(0.0001, graph.learning_rate)
```

---

## Testing Strategy

### Unit Tests

```python
def test_criticality_calculation():
    """Test criticality calculation is correct"""
    graph = create_test_graph()

    # Set known state: 50 links, 10 active
    # Expected criticality: 10/50 = 0.2

    # Activate 10 specific links
    for i in range(10):
        link = graph.links[i]
        link.source.set_entity_energy("test_entity", 0.5)

    crit = calculate_criticality(graph, entity="test_entity", threshold=0.01)

    assert 0.15 < crit < 0.25, f"Expected ~0.2, got {crit}"

def test_tuning_increases_decay_when_supercritical():
    """Test tuning increases decay when system too active"""
    graph = create_test_graph()
    initial_decay = graph.decay_rate

    # Make system supercritical
    for node in graph.nodes:
        node.set_entity_energy("test", 0.9)

    crit = calculate_criticality(graph)
    assert crit > 1.5, "System should be supercritical"

    # Tune
    tune_criticality(graph, target=1.0, learning_rate=0.001)

    # Decay should increase
    assert graph.decay_rate > initial_decay, "Decay should increase when supercritical"

def test_tuning_decreases_decay_when_subcritical():
    """Test tuning decreases decay when system too quiet"""
    graph = create_test_graph()
    graph.decay_rate = 0.005  # Moderate decay

    # Make system subcritical (low energy everywhere)
    for node in graph.nodes:
        node.set_entity_energy("test", 0.05)

    crit = calculate_criticality(graph)
    assert crit < 0.5, "System should be subcritical"

    initial_decay = graph.decay_rate

    # Tune
    tune_criticality(graph, target=1.0, learning_rate=0.001)

    # Decay should decrease
    assert graph.decay_rate < initial_decay, "Decay should decrease when subcritical"
```

### Integration Tests

```python
def test_convergence_to_criticality():
    """Test system converges to target criticality"""
    graph = create_test_graph(nodes=1000, links=5000)

    # Start far from target
    graph.decay_rate = 0.01  # Very high

    criticalities = []
    for tick in range(500):
        tune_criticality(graph, target=1.0, learning_rate=0.001)

        # Simulate dynamics
        for node in random.sample(graph.nodes, k=10):
            node.set_entity_energy("test", 0.5)  # Random activation

        diffusion_tick(graph, duration=0.1)
        decay_tick(graph, duration=0.1)

        crit = calculate_criticality(graph)
        criticalities.append(crit)

    # Should converge within 500 ticks
    final_criticality = criticalities[-1]
    assert 0.8 < final_criticality < 1.2, f"Should converge near 1.0, got {final_criticality}"

    # Should be stable (low variance in last 100 ticks)
    final_variance = np.var(criticalities[-100:])
    assert final_variance < 0.1, f"Should stabilize, variance {final_variance}"
```

### Phenomenological Validation

```python
def test_subcritical_feels_sluggish():
    """
    Test that subcritical state produces sluggish activation spread

    Phenomenology: Thoughts don't lead to other thoughts
    """
    graph = create_consciousness_graph()

    # Force subcritical
    graph.decay_rate = 0.02  # Very high decay

    # Inject stimulus
    entry_node = graph.get_node("test_concept")
    entry_node.set_entity_energy("translator", 0.8)

    # Diffuse for 10 ticks
    for _ in range(10):
        diffusion_tick(graph, duration=0.1)
        decay_tick(graph, duration=0.1)

    # Measure spread
    activated_nodes = [
        n for n in graph.nodes
        if n.get_entity_energy("translator") > 0.1
    ]

    # Should activate very few nodes (sluggish)
    assert len(activated_nodes) < 10, "Subcritical should activate few nodes"

def test_critical_feels_optimal():
    """
    Test that critical state produces balanced activation spread

    Phenomenology: Ideas flow naturally, not too many, not too few
    """
    graph = create_consciousness_graph()

    # Tune to criticality
    for _ in range(100):
        tune_criticality(graph, target=1.0)
        diffusion_tick(graph, duration=0.1)
        decay_tick(graph, duration=0.1)

    # Inject stimulus
    entry_node = graph.get_node("test_concept")
    entry_node.set_entity_energy("translator", 0.8)

    # Diffuse for 10 ticks
    for _ in range(10):
        diffusion_tick(graph, duration=0.1)
        decay_tick(graph, duration=0.1)

    # Measure spread
    activated_nodes = [
        n for n in graph.nodes
        if n.get_entity_energy("translator") > 0.1
    ]

    # Should activate moderate number (balanced)
    assert 10 < len(activated_nodes) < 100, "Critical should activate moderate nodes"
```

---

## Performance Considerations

### Computational Cost

```python
# Criticality calculation per tick:
# - Count active links: O(L) where L = number of links
# - Count potential links: O(1) if cached
# - Total: O(L)

# For large graphs:
# - 1M links → ~10ms to calculate criticality
# - Acceptable if done once per tick
# - Can optimize with sampling if needed
```

### Optimization: Sampling

```python
def calculate_criticality_sampled(graph: Graph, sample_size: int = 1000) -> float:
    """
    Estimate criticality by sampling links instead of checking all

    Faster for very large graphs (>1M links)
    """
    if len(graph.links) <= sample_size:
        return calculate_criticality(graph)  # Use exact if small enough

    # Sample random links
    sampled_links = random.sample(graph.links, sample_size)

    active_count = 0
    for link in sampled_links:
        # Check if link active (same logic as full calculation)
        if is_link_active(link, graph, threshold=0.01):
            active_count += 1

    # Estimate total active links
    estimated_active = (active_count / sample_size) * len(graph.links)
    criticality = estimated_active / len(graph.links)

    return criticality
```

---

## Open Questions

1. **Optimal target criticality?**
   - Current: 1.0
   - Confidence: Medium (0.6)
   - Question: Does optimal vary by task? (e.g., 0.8 for focused work, 1.2 for creative exploration)

2. **Per-entity vs global tuning?**
   - Current: Both supported
   - Confidence: Low (0.4)
   - Question: Should entities have independent criticality targets?

3. **Tuning algorithm choice?**
   - Current: Simple proportional control
   - Alternatives: PID, dual-parameter, adaptive
   - Confidence: Medium (0.5)
   - Needs empirical testing

4. **Convergence speed requirements?**
   - Current: ~100 ticks acceptable
   - Question: Do we need faster convergence? (e.g., <10 ticks)
   - Confidence: Low (0.3)

---

## Related Mechanisms

- **[07: Energy Diffusion](07_energy_diffusion.md)** - What criticality regulates
- **[08: Energy Decay](08_energy_decay.md)** - The primary tuning parameter
- **[04: Global Workspace](04_global_workspace_theory.md)** - Criticality affects workspace composition
- **[10: Tick Speed Regulation](10_tick_speed_regulation.md)** - Interacts with criticality tuning

---

## Implementation Checklist

- [ ] Implement calculate_criticality() with entity parameter
- [ ] Implement count_active_links helpers
- [ ] Implement basic tune_criticality() (proportional control)
- [ ] Implement decay rate clamping
- [ ] Add criticality to graph state tracking
- [ ] Write unit tests for criticality calculation
- [ ] Write unit tests for tuning direction (increase/decrease decay)
- [ ] Write integration test for convergence
- [ ] Write phenomenological tests (subcritical/critical/supercritical)
- [ ] Measure convergence speed empirically
- [ ] Implement PID controller variant (optional enhancement)
- [ ] Implement per-entity tuning (optional enhancement)
- [ ] Add criticality to monitoring/visualization
- [ ] Document optimal target values for different contexts

---

**Next:** [04: Global Workspace Theory](04_global_workspace_theory.md) - How clusters enter consciousness
