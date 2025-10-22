# Mechanism 08: Energy Decay

**Status:** Core - Forgetting mechanism
**Confidence:** High (0.90)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Decays per-entity energy
- **[03: Self-Organized Criticality](03_self_organized_criticality.md)** - Tunes decay rate

**Biological Basis:** Synaptic depression, memory consolidation, forgetting curves (Ebbinghaus)

---

## Overview

**Core Principle:** All energy and link weights **decay exponentially** over time. This is the forgetting mechanism - preventing old, irrelevant patterns from persisting indefinitely.

**IMPORTANT UPDATE (2025-10-19):** Energy decay and weight decay now operate at **separate rates** that vary by **node/link type**. See **[Mechanism 19: Type-Dependent Decay](19_type_dependent_decay.md)** for full specification.

**Why This Matters:**
- Prevents "zombie activations" (outdated patterns lingering)
- Creates room for new patterns (finite energy budget)
- Matches biological reality (memories fade without reinforcement)
- Enables natural priority (frequently activated = persists, rare = fades)
- Critical for self-organized criticality (decay balances diffusion)
- **NEW:** Different node types have different persistence (Memory sticks, Tasks fade)

**Dual Decay System:**

```
Energy decay (fast):
Energy(t) = Energy(0) × e^(-δ_state × t)

Weight decay (slow):
Weight(t) = Weight(0) × e^(-δ_weight × t)

Type-dependent rates:
Memory: δ_weight = 0.0001/hour (very slow - "sticks")
Task:   δ_weight = 0.01/hour (fast - temporary)
```

**The Forgetting Curve (Energy):**

```
With δ_state = 0.1/hour (typical):
Half-life = 7 hours
After 1 hour: 90% remains
After 1 day: 9% remains

With δ_weight = 0.001/hour (Memory nodes):
Half-life = 700 hours (29 days)
After 1 day: 98% remains
After 1 week: 86% remains
```

---

## Phenomenological Truth

### What It Feels Like

**The Fading Memory:**

```
09:00 - Read about "bitemporal tracking"
- bitemporal_tracking node: 0.9 energy (Architect)
- Feels: Clear, vivid understanding

10:00 - Working on other things
- bitemporal_tracking: 0.9 → 0.4 energy
- Feels: "I know I read something about time tracking..."

12:00 - Trying to recall details
- bitemporal_tracking: 0.4 → 0.15 energy
- Feels: "Was it bitemporal? Or temporal? Something about timestamps..."

14:00 - Mostly forgotten
- bitemporal_tracking: 0.15 → 0.05 energy
- Feels: Vague awareness something existed, details gone
```

**The key:** Decay creates the phenomenology of forgetting - vivid → vague → gone.

### Decay vs. Reinforcement Competition

**Pattern that gets reinforced:**
```
Initial: consciousness_schema node at 0.6 energy

Every hour: Small stimulus reactivates (reading, discussing)
- Hour 0: 0.6
- Hour 1: Decay to 0.3, stimulus adds 0.4 → 0.7
- Hour 2: Decay to 0.35, stimulus adds 0.4 → 0.75
- Hour 3: Decay to 0.38, stimulus adds 0.4 → 0.78
→ Stabilizes around 0.7-0.8 (decay ≈ reinforcement)

Phenomenology: "I'm constantly thinking about this"
Reality: Rapid decay balanced by frequent reactivation
```

**Pattern WITHOUT reinforcement:**
```
Initial: random_concept at 0.6 energy

No further stimuli:
- Hour 1: 0.6 → 0.3
- Hour 2: 0.3 → 0.15
- Hour 3: 0.15 → 0.075
- Hour 4: 0.075 → 0.038 (below peripheral threshold)

Phenomenology: "Completely forgot about that"
Reality: Exponential decay to dormancy
```

---

## Mathematical Specification

### Decay Function

```python
def decay_tick(
    graph: Graph,
    tick_duration: float = 0.1,
    decay_rate: float = 0.001
):
    """
    Apply exponential decay to all energy and weights

    Decay is CONTINUOUS - happens every tick regardless of activity

    Args:
        graph: The consciousness graph
        tick_duration: Time step (seconds)
        decay_rate: Base decay rate (per second)
    """
    # Decay factor for this tick
    decay_factor = 1.0 - (decay_rate * tick_duration)

    # Decay node energies
    for node in graph.nodes:
        # Decay each entity's energy independently
        for entity in list(node.energy.keys()):  # Copy keys (may delete)
            current_energy = node.energy[entity]
            new_energy = current_energy * decay_factor

            if new_energy < 0.001:
                # Remove dormant entity (cleanup)
                del node.energy[entity]
            else:
                node.energy[entity] = new_energy

        # Decay base weight
        node.base_weight *= decay_factor

    # Decay link weights
    for link in graph.links:
        link.weight *= decay_factor

        # Optionally remove very weak links (pruning)
        if link.weight < 0.01:
            # Mark for removal (don't delete during iteration)
            if not hasattr(link, '_marked_for_removal'):
                link._marked_for_removal = True

    # Prune marked links (optional - may want to keep skeleton)
    # graph.prune_marked_links()
```

### Decay Rate Dynamics

**Decay rate is NOT constant - tuned by criticality:**

```python
class DecayController:
    """
    Manages decay rate with criticality-based tuning

    Primary mechanism for maintaining criticality ≈ 1.0
    """
    def __init__(self, initial_rate: float = 0.001):
        self.base_rate = initial_rate
        self.current_rate = initial_rate
        self.rate_history = []

    def get_current_rate(self) -> float:
        """Get current decay rate"""
        return self.current_rate

    def tune_rate(
        self,
        global_criticality: float,
        target_criticality: float = 1.0,
        learning_rate: float = 0.001
    ):
        """
        Adjust decay rate to maintain criticality

        High criticality → increase decay (cool down system)
        Low criticality → decrease decay (preserve activation)
        """
        error = global_criticality - target_criticality

        # Direct relationship: high criticality → increase decay
        adjustment = learning_rate * error

        self.current_rate += adjustment

        # Clamp to safe bounds
        self.current_rate = max(0.0001, min(0.01, self.current_rate))

        # Track history
        self.rate_history.append({
            'timestamp': now(),
            'rate': self.current_rate,
            'criticality': global_criticality
        })

    def calculate_half_life(self) -> float:
        """
        Calculate current half-life in seconds

        Half-life = time for energy to decay to 50%
        """
        import math
        return math.log(2) / self.current_rate

    def get_rate_statistics(self) -> dict:
        """Statistics about decay rate evolution"""
        if not self.rate_history:
            return {}

        rates = [entry['rate'] for entry in self.rate_history[-100:]]

        return {
            'current': self.current_rate,
            'half_life_seconds': self.calculate_half_life(),
            'mean': np.mean(rates),
            'std': np.std(rates),
            'min': np.min(rates),
            'max': np.max(rates)
        }
```

---

## Decay Patterns

### Exponential Decay Curve

```python
def plot_decay_curve(initial_energy: float = 1.0, decay_rate: float = 0.001, duration_hours: int = 24):
    """
    Visualize energy decay over time

    Shows classic exponential forgetting curve
    """
    import matplotlib.pyplot as plt

    times = np.linspace(0, duration_hours * 3600, 1000)  # Convert hours to seconds
    energies = initial_energy * np.exp(-decay_rate * times)

    plt.figure(figsize=(10, 6))
    plt.plot(times / 3600, energies)  # Convert back to hours for display
    plt.xlabel('Time (hours)')
    plt.ylabel('Energy')
    plt.title(f'Energy Decay (rate={decay_rate}/sec, half-life={np.log(2)/decay_rate/60:.1f} min)')
    plt.grid(True)
    plt.axhline(y=0.5, color='r', linestyle='--', label='Half-life')
    plt.axhline(y=0.1, color='orange', linestyle='--', label='Peripheral threshold')
    plt.legend()
    plt.show()

# Output:
# Half-life at ~11.5 minutes
# Peripheral threshold (0.1) at ~38 minutes
# Near-zero (<0.01) at ~2 hours
```

### Type-Dependent Dual Decay (Updated 2025-10-19)

**IMPORTANT:** Decay rates now vary by node/link type. See **[Mechanism 19: Type-Dependent Decay](19_type_dependent_decay.md)** for complete specification.

**Key Principle:** Energy decay (δ_state) and weight decay (δ_weight) are **separate** and **type-dependent**.

```python
class TypeDependentDecay:
    """
    Apply type-specific decay rates

    Rationale (Nicolas's architectural guidance):
    - Energy and weight should NOT decay at same rate
    - Memory nodes decay slowly ("sticks")
    - Task nodes decay fast (temporary structures)
    - Working memory span controlled by traversal algorithm, not just decay
    """

    def get_decay_rates(self, node):
        """Get type-specific decay rates for node"""
        type_config = {
            "Memory": {
                "delta_state": 0.05 / 3600,    # Energy: 5% per hour
                "delta_weight": 0.0001 / 3600  # Weights: 0.01% per hour (sticks!)
            },
            "Task": {
                "delta_state": 0.5 / 3600,     # Energy: 50% per hour
                "delta_weight": 0.01 / 3600    # Weights: 1% per hour (temporary)
            },
            "Realization": {
                "delta_state": 0.1 / 3600,
                "delta_weight": 0.0005 / 3600
            },
            "default": {
                "delta_state": 0.1 / 3600,
                "delta_weight": 0.001 / 3600
            }
        }
        return type_config.get(node.type, type_config["default"])

    def apply_type_dependent_decay(self, graph: Graph, tick_duration: float):
        """Apply decay with type-specific rates"""

        for node in graph.nodes:
            # Get node-specific rates
            rates = self.get_decay_rates(node)

            # Decay energy (delta_state)
            energy_factor = 1.0 - (rates["delta_state"] * tick_duration)
            for entity in list(node.energy.keys()):
                node.energy[entity] *= energy_factor
                if node.energy[entity] < 0.001:
                    del node.energy[entity]

            # Decay outgoing link weights (delta_weight)
            for link in node.outgoing_links:
                link_rates = self.get_link_decay_rates(link)
                weight_factor = 1.0 - (link_rates["delta_weight"] * tick_duration)
                link.weight *= weight_factor

    def get_link_decay_rates(self, link):
        """Get type-specific decay rates for link"""
        link_config = {
            "ENABLES": {"delta_weight": 0.0005 / 3600},      # Persistent
            "BLOCKS": {"delta_weight": 0.002 / 3600},        # Temporary obstacles
            "RELATES_TO": {"delta_weight": 0.0003 / 3600},   # Very persistent
            "default": {"delta_weight": 0.001 / 3600}
        }
        return link_config.get(link.type, link_config["default"])
```

**Phenomenological Example:**

```
Work on consciousness substrate for 3 hours, then 3-day break:

Memory node:
- Hour 0: energy=1.0, weight=1.0
- Hour 3: energy=0.86, weight=0.9997
- Hour 75 (3 days): energy=0.02, weight=0.993
→ Can resume context after break ✓

Task node:
- Hour 0: energy=1.0, weight=1.0
- Hour 3: energy=0.22, weight=0.97
- Hour 75: energy≈0.0, weight=0.48
→ Task fades appropriately ✓
```

**See [Mechanism 19](19_type_dependent_decay.md) for:**
- Complete type-specific decay configuration
- Working memory span discussion
- Timescale examples
- Tuning guide

---

## Edge Cases & Constraints

### Edge Case 1: Decay to Zero

**Problem:** All energy decays to zero → system death

**Solution:** Minimum baseline energy OR periodic stimuli

```python
def maintain_baseline_energy(graph: Graph, baseline_per_entity: float = 0.05):
    """
    Ensure system never fully dies

    Inject minimal energy if total drops too low
    """
    for entity in graph.get_all_known_entities():
        total_energy = sum(n.get_entity_energy(entity) for n in graph.nodes)

        if total_energy < baseline_per_entity:
            # Inject into random nodes
            injection_needed = baseline_per_entity - total_energy
            random_nodes = random.sample(graph.nodes, min(10, len(graph.nodes)))

            for node in random_nodes:
                node.increment_entity_energy(entity, injection_needed / len(random_nodes))
```

### Edge Case 2: Immortal High-Weight Nodes

**Problem:** Very high-weight nodes (0.99) decay incredibly slowly

**Solution:** This is INTENTIONAL - core concepts should persist

```python
def identify_core_concepts(graph: Graph, weight_threshold: float = 0.9) -> list[Node]:
    """
    Find nodes that resist decay (very high base weight)

    These are learned "core concepts" - fundamental to consciousness
    """
    core = [
        node for node in graph.nodes
        if node.base_weight > weight_threshold
    ]

    return core
```

### Edge Case 3: Decay Rate Too High

**Problem:** Decay so fast nothing persists even with stimulation

**Solution:** Criticality tuning auto-corrects

```python
def detect_excessive_decay(graph: Graph, entity: str, min_persistence: float = 0.1) -> bool:
    """
    Detect if decay is too aggressive

    Signs: Energy never builds up, always below threshold
    """
    # Inject test energy
    test_node = random.choice(graph.nodes)
    test_node.set_entity_energy(entity, 0.5)

    # Let it decay for 10 ticks (no diffusion)
    for _ in range(10):
        decay_tick(graph, tick_duration=0.1)

    remaining = test_node.get_entity_energy(entity)

    # If less than 10% remains after just 1 second, decay too high
    excessive = remaining < min_persistence

    return excessive
```

---

## Testing Strategy

### Unit Tests

```python
def test_energy_decays_exponentially():
    """Test energy follows exponential decay curve"""
    graph = create_test_graph()

    node = graph.nodes[0]
    node.set_entity_energy("test", 1.0)

    decay_rate = 0.001

    # Decay for 100 ticks
    energies = [1.0]
    for _ in range(100):
        decay_tick(graph, tick_duration=0.1, decay_rate=decay_rate)
        energies.append(node.get_entity_energy("test"))

    # Should follow exponential curve
    expected = [1.0 * np.exp(-decay_rate * 0.1 * t) for t in range(101)]

    # Check close match
    for actual, exp in zip(energies, expected):
        assert abs(actual - exp) < 0.01, f"Decay should be exponential: {actual} vs {exp}"

def test_half_life_calculation():
    """Test half-life matches expected value"""
    decay_rate = 0.001  # per second
    expected_half_life = np.log(2) / decay_rate  # ~693 seconds = 11.5 minutes

    controller = DecayController(initial_rate=decay_rate)
    calculated_half_life = controller.calculate_half_life()

    assert abs(calculated_half_life - expected_half_life) < 1.0, "Half-life calculation should be accurate"
```

### Integration Tests

```python
def test_decay_balanced_by_reinforcement():
    """Test frequent stimulation prevents decay"""
    graph = create_consciousness_graph()

    target_node = graph.get_node("test_concept")

    # Stimulus every 10 ticks
    for tick in range(100):
        if tick % 10 == 0:
            # Reinforce
            target_node.set_entity_energy("test", 0.7)

        # Decay
        decay_tick(graph, tick_duration=0.1, decay_rate=0.001)

        # Diffuse (small amount)
        diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.05)

    # Energy should stabilize (not decay to zero)
    final_energy = target_node.get_entity_energy("test")

    assert final_energy > 0.3, "Reinforced node should not decay completely"
```

### Phenomenological Validation

```python
def test_forgetting_curve_phenomenology():
    """
    Test decay creates realistic forgetting curve

    Should match Ebbinghaus forgetting curve
    """
    graph = create_consciousness_graph()

    # Learn something (high initial energy)
    learned_node = graph.get_node("new_concept")
    learned_node.set_entity_energy("translator", 0.9)

    # Track energy over time (no reinforcement)
    time_points = [0, 1, 2, 4, 8, 24]  # Hours
    energies = [0.9]

    for hours in time_points[1:]:
        # Decay for this duration
        ticks = int(hours * 3600 / 0.1)  # Convert hours to ticks
        for _ in range(ticks):
            decay_tick(graph, tick_duration=0.1, decay_rate=0.001)

        energies.append(learned_node.get_entity_energy("translator"))

    # Should show rapid initial decay, then slower
    assert energies[1] < energies[0] * 0.5, "Should lose >50% in first hour"
    assert energies[-1] < 0.05, "Should be mostly forgotten after 24 hours"

    # Decay rate should slow (exponential)
    decay_rate_early = (energies[0] - energies[1]) / energies[0]
    decay_rate_late = (energies[-2] - energies[-1]) / energies[-2]

    assert decay_rate_early > decay_rate_late, "Exponential decay: faster early, slower late"
```

---

## Performance Considerations

### Computational Cost

```python
# Decay complexity per tick:
# - For each node: Multiply energy by decay factor: O(E) where E = entities per node
# - For each link: Multiply weight by decay factor: O(1)
# - Total: O(N×E + L) ≈ O(N) for typical cases

# For large graphs:
# - 1M nodes × 5 entities = 5M multiplications
# - 5M links × 1 multiplication = 5M multiplications
# - Total: ~10M operations → ~5-10ms per tick

# Very efficient - decay is embarrassingly parallel
```

### Optimization: Batch Decay

```python
def batch_decay(graph: Graph, num_ticks: int, tick_duration: float = 0.1, decay_rate: float = 0.001):
    """
    Apply multiple ticks of decay at once

    More efficient than individual ticks when no other operations
    """
    # Calculate compound decay factor
    total_decay_factor = (1.0 - decay_rate * tick_duration) ** num_ticks

    # Apply once
    for node in graph.nodes:
        for entity in list(node.energy.keys()):
            node.energy[entity] *= total_decay_factor
            if node.energy[entity] < 0.001:
                del node.energy[entity]

        node.base_weight *= total_decay_factor

    for link in graph.links:
        link.weight *= total_decay_factor
```

---

## Open Questions

1. **Optimal base decay rate?**
   - Current: 0.001/second (11.5 min half-life)
   - Confidence: Medium (0.6)
   - May need tuning based on usage patterns

2. **Differential decay rates?**
   - Current: Same rate for energy/weights/links
   - Alternative: Different rates for each
   - Confidence: Medium (0.5)

3. **Link pruning threshold?**
   - Current: Links persist even when very weak
   - Alternative: Remove links below threshold
   - Confidence: Low (0.4) - pruning may break structure

4. **Decay during sleep?**
   - Current: Continuous decay regardless of activity
   - Alternative: Slower decay during dormancy
   - Confidence: Low (0.3)

---

## Related Mechanisms

- **[07: Energy Diffusion](07_energy_diffusion.md)** - Opposes decay
- **[03: Self-Organized Criticality](03_self_organized_criticality.md)** - Tunes decay rate
- **[09: Link Strengthening](09_link_strengthening.md)** - Opposes link decay
- **[19: Type-Dependent Decay](19_type_dependent_decay.md)** - **NEW:** Complete specification of dual decay system and type-specific rates

---

## Implementation Checklist

- [ ] Implement decay_tick() main algorithm
- [ ] Implement DecayController class
- [ ] Implement differential decay (energy/weight/links)
- [ ] Implement baseline energy maintenance
- [ ] Implement half-life calculation
- [ ] Implement excessive decay detection
- [ ] Implement batch decay optimization
- [ ] Write unit tests for exponential decay
- [ ] Write unit tests for half-life accuracy
- [ ] Write integration tests for decay/reinforcement balance
- [ ] Write phenomenological tests (forgetting curve)
- [ ] Measure decay performance at scale
- [ ] Add decay visualization (energy over time)

---

**Next:** [09: Link Strengthening](09_link_strengthening.md) - Hebbian learning dynamics
