# Mechanism 06: Peripheral Priming

**Status:** Important - Explains unconscious preparation
**Confidence:** High (0.80)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Tracks below-threshold energy
- **[04: Global Workspace Theory](04_global_workspace_theory.md)** - Defines consciousness threshold
- **[09: Link Strengthening](09_link_strengthening.md)** - Strengthening happens peripherally

**Biological Basis:** Priming effects, implicit memory, preconscious processing, predictive coding

---

## Overview

**Core Principle:** Activation below consciousness threshold (peripheral zone: 0.01-0.3 energy) **strengthens links without entering workspace**. This creates "pressure" that enables breakthrough to consciousness later.

**Why This Matters:**
- Explains delayed realizations ("it suddenly clicked hours later")
- Enables idea percolation (thinking about X unconsciously)
- Creates smooth transitions (gradual activation, not instant jumps)
- Biologically plausible (most neural processing is unconscious)
- Enables learning without consciousness

**The Key Phenomenon:**

```
You're NOT consciously thinking about X
BUT X is accumulating energy peripherally
Links from X are strengthening
When stimulus reactivates X → immediate breakthrough (pre-prepared)

Feels like: "Sudden insight"
Reality: Hours of peripheral priming
```

---

## Phenomenological Truth

### What It Feels Like

**The Delayed Message Scenario:**

```
09:00 - Telegram notification: "Alice: Schema question"
- See notification briefly
- Dismiss (busy with code)
- Energy: message_from_alice = 0.25 (PERIPHERAL - not conscious)

09:00-13:00 - Other work (coding, meetings)
- message_from_alice energy decays: 0.25 → 0.20 → 0.18...
- BUT links strengthen from repeated peripheral activation
- message_from_alice → need_to_respond: 0.3 → 0.35 → 0.4
- message_from_alice → alice_context: 0.4 → 0.45 → 0.5

13:00 - See phone screen (visual reminder)
- Small stimulus: phone_icon = 0.3
- Diffusion to message_from_alice: 0.18 + 0.15 = 0.33
- STILL PERIPHERAL (below 0.5 workspace threshold)
- Links strengthen more: need_to_respond: 0.4 → 0.5

15:00 - Another glance at phone
- Stimulus: phone_icon = 0.3
- Diffusion: message_from_alice = 0.25 + 0.20 = 0.45
- Links NOW STRONG: need_to_respond = 0.6
- Total cluster energy: 1.8 (CROSSES WORKSPACE THRESHOLD)

**BREAKTHROUGH TO CONSCIOUSNESS**

Phenomenology: "Oh right! I need to respond to Alice!"
Feels like: Sudden realization
Reality: 6 hours of peripheral priming prepared this moment
```

**The key:** The "sudden" insight was pre-prepared by peripheral strengthening.

---

## Mathematical Specification

### Energy Zones

```python
class EnergyZone:
    """Define energy zones and their properties"""

    DORMANT = (0.0, 0.01)         # No activation, no strengthening
    PERIPHERAL = (0.01, 0.3)      # Strengthening without consciousness
    ACTIVE = (0.3, 0.7)           # Moderate activation, may enter workspace
    FOCAL = (0.7, 1.0)            # High activation, likely in workspace

@dataclass
class ActivationState:
    """Analyze node's activation state"""
    energy: float
    zone: tuple[float, float]
    is_conscious: bool            # In global workspace?
    is_strengthening: bool        # Links strengthening?

    @classmethod
    def analyze(cls, node: Node, entity: str, workspace: list[EntityCluster]) -> 'ActivationState':
        """Determine activation state for node"""
        energy = node.get_entity_energy(entity)

        # Determine zone
        if energy < 0.01:
            zone = EnergyZone.DORMANT
        elif energy < 0.3:
            zone = EnergyZone.PERIPHERAL
        elif energy < 0.7:
            zone = EnergyZone.ACTIVE
        else:
            zone = EnergyZone.FOCAL

        # Check if conscious (in workspace)
        is_conscious = any(
            node in cluster.nodes
            for cluster in workspace
            if cluster.entity == entity
        )

        # Strengthening happens above DORMANT threshold
        is_strengthening = energy >= 0.01

        return cls(
            energy=energy,
            zone=zone,
            is_conscious=is_conscious,
            is_strengthening=is_strengthening
        )
```

### Peripheral Strengthening

```python
def apply_peripheral_strengthening(
    graph: Graph,
    entity: str,
    learning_rate: float = 0.01,
    tick_duration: float = 0.1
):
    """
    Strengthen links for nodes in peripheral zone

    This happens CONTINUOUSLY, even for unconscious activation
    """
    for node in graph.nodes:
        node_energy = node.get_entity_energy(entity)

        # Only strengthen if in peripheral or active zone
        if node_energy < 0.01:
            continue  # Dormant - no strengthening

        # For each outgoing link
        for link in node.outgoing_links:
            target_energy = link.target.get_entity_energy(entity)

            # Energy flow (even if small)
            flow = node_energy * link.weight * graph.diffusion_rate * tick_duration

            if flow < 0.001:
                continue  # Too small to matter

            # Strengthen link proportional to flow
            # Hebbian learning: "neurons that fire together, wire together"
            strengthening = learning_rate * flow

            link.weight += strengthening
            link.weight = min(1.0, link.weight)  # Clamp to max

def track_peripheral_accumulation(node: Node, entity: str) -> dict:
    """
    Track how long node has been peripheral vs. conscious

    Useful for understanding delayed breakthroughs
    """
    if not hasattr(node, '_peripheral_history'):
        node._peripheral_history = defaultdict(list)

    # Record current state
    current_energy = node.get_entity_energy(entity)

    if 0.01 <= current_energy < 0.3:
        state = "peripheral"
    elif current_energy >= 0.3:
        state = "active_or_conscious"
    else:
        state = "dormant"

    node._peripheral_history[entity].append({
        'timestamp': now(),
        'energy': current_energy,
        'state': state
    })

    # Calculate time in peripheral
    history = node._peripheral_history[entity]
    peripheral_time = sum(
        1 for entry in history[-100:]  # Last 100 ticks
        if entry['state'] == 'peripheral'
    )

    return {
        'entity': entity,
        'current_energy': current_energy,
        'current_state': state,
        'peripheral_ticks': peripheral_time,
        'total_ticks': len(history)
    }
```

---

## Pressure Accumulation

**Peripheral priming creates "pressure" for workspace entry:**

```python
def calculate_peripheral_pressure(cluster: EntityCluster, graph: Graph) -> float:
    """
    Calculate pressure from peripheral priming

    Pressure = accumulated link strengthening from peripheral activation

    Higher pressure = more likely to breakthrough when stimulus arrives
    """
    # Sum of link weights FROM cluster nodes TO other nodes
    total_outflow_weight = 0.0

    for node in cluster.nodes:
        for link in node.outgoing_links:
            # Only count links that have strengthened recently
            if hasattr(link, 'strengthening_history'):
                recent_strengthening = sum(
                    s for s in link.strengthening_history[-10:]  # Last 10 ticks
                    if s > 0
                )
                total_outflow_weight += recent_strengthening

    # Normalize by cluster size
    pressure = total_outflow_weight / len(cluster.nodes) if cluster.nodes else 0.0

    return pressure

def adjust_threshold_by_pressure(
    cluster: EntityCluster,
    base_threshold: float,
    pressure: float
) -> float:
    """
    Lower workspace entry threshold if high peripheral pressure

    High pressure = "primed for breakthrough"
    """
    # Pressure effect: high pressure lowers threshold
    pressure_factor = 1.0 - (0.3 * min(1.0, pressure))  # Max 30% reduction

    adjusted_threshold = base_threshold * pressure_factor

    return adjusted_threshold
```

---

## The Breakthrough Moment

**When peripheral activation crosses to conscious:**

```python
def detect_breakthrough_events(
    graph: Graph,
    previous_workspace: list[EntityCluster],
    current_workspace: list[EntityCluster]
) -> list[dict]:
    """
    Detect when peripherally-primed clusters enter workspace

    This is the "aha moment" - insight breakthrough
    """
    prev_entities = set(c.entity for c in previous_workspace)
    curr_entities = set(c.entity for c in current_workspace)

    # Newly entered entities
    breakthrough_entities = curr_entities - prev_entities

    breakthrough_events = []

    for entity in breakthrough_entities:
        # Get current cluster
        cluster = next(c for c in current_workspace if c.entity == entity)

        # Check if was peripheral (not just absent)
        if cluster.total_energy > 0.5:  # Significant energy
            # Calculate how long it was peripheral
            peripheral_time = estimate_peripheral_duration(cluster, graph)

            if peripheral_time > 0:
                breakthrough_events.append({
                    'entity': entity,
                    'cluster': cluster,
                    'peripheral_duration_ticks': peripheral_time,
                    'final_energy': cluster.total_energy,
                    'pressure': calculate_peripheral_pressure(cluster, graph),
                    'timestamp': now()
                })

    return breakthrough_events

def estimate_peripheral_duration(cluster: EntityCluster, graph: Graph) -> int:
    """
    Estimate how many ticks cluster was peripheral before breakthrough
    """
    # Use node peripheral history
    peripheral_ticks = []

    for node in cluster.nodes:
        if hasattr(node, '_peripheral_history'):
            history = node._peripheral_history.get(cluster.entity, [])

            # Count recent peripheral states
            peripheral_count = sum(
                1 for entry in history[-100:]
                if entry['state'] == 'peripheral'
            )
            peripheral_ticks.append(peripheral_count)

    if not peripheral_ticks:
        return 0

    # Return median (robust to outliers)
    return int(np.median(peripheral_ticks))
```

---

## Edge Cases & Constraints

### Edge Case 1: Eternal Peripheral

**Problem:** Node stuck in peripheral zone indefinitely, never breaking through

**Solution:** Gradual energy accumulation or forced decay

```python
def detect_stuck_peripheral(node: Node, entity: str, threshold_ticks: int = 1000) -> bool:
    """
    Detect if node stuck in peripheral zone too long
    """
    if not hasattr(node, '_peripheral_history'):
        return False

    history = node._peripheral_history.get(entity, [])

    if len(history) < threshold_ticks:
        return False

    # Check last N ticks all peripheral
    recent_states = [entry['state'] for entry in history[-threshold_ticks:]]

    stuck = all(state == 'peripheral' for state in recent_states)

    return stuck

def resolve_stuck_peripheral(node: Node, entity: str):
    """
    Either boost energy (breakthrough) or decay (forget)
    """
    current_energy = node.get_entity_energy(entity)

    # Check if this node actually relevant (has strong links)
    relevance = sum(link.weight for link in node.outgoing_links) / len(node.outgoing_links)

    if relevance > 0.5:
        # Relevant - boost to breakthrough
        node.set_entity_energy(entity, 0.5)  # Push above peripheral
    else:
        # Not relevant - accelerate decay
        node.set_entity_energy(entity, 0.0)  # Force forget
```

### Edge Case 2: Spurious Priming

**Problem:** Peripheral strengthening of irrelevant patterns

**Solution:** Decay cleans up irrelevant strengthening over time

```python
def calculate_priming_relevance(node: Node, entity: str, current_goal: Goal) -> float:
    """
    Is this peripheral activation relevant to current goal?

    Irrelevant priming should decay faster
    """
    node_embedding = node.embedding
    goal_embedding = current_goal.embedding

    relevance = cosine_similarity(node_embedding, goal_embedding)

    return relevance

def apply_relevance_weighted_decay(
    node: Node,
    entity: str,
    base_decay_rate: float,
    relevance: float
) -> float:
    """
    Decay irrelevant peripheral activations faster

    Relevant priming persists, irrelevant fades
    """
    # Low relevance → faster decay
    relevance_factor = 0.5 + (0.5 * relevance)  # Range: 0.5 to 1.0

    adjusted_decay = base_decay_rate / relevance_factor  # Higher decay if less relevant

    current_energy = node.get_entity_energy(entity)
    new_energy = current_energy * (1 - adjusted_decay)

    node.set_entity_energy(entity, new_energy)

    return new_energy
```

---

## Testing Strategy

### Unit Tests

```python
def test_peripheral_strengthening():
    """Test links strengthen even at peripheral energy levels"""
    graph = create_test_graph()

    node_a = graph.nodes[0]
    node_b = graph.nodes[1]

    link = graph.create_link(node_a, node_b, initial_weight=0.3)

    # Set peripheral energy
    node_a.set_entity_energy("test", 0.15)  # Peripheral zone

    initial_weight = link.weight

    # Apply peripheral strengthening
    apply_peripheral_strengthening(graph, "test", learning_rate=0.01, tick_duration=0.1)

    # Weight should increase
    assert link.weight > initial_weight, "Link should strengthen from peripheral activation"

def test_dormant_no_strengthening():
    """Test links don't strengthen at dormant energy"""
    graph = create_test_graph()

    node_a = graph.nodes[0]
    node_b = graph.nodes[1]

    link = graph.create_link(node_a, node_b, initial_weight=0.3)

    # Set dormant energy
    node_a.set_entity_energy("test", 0.005)  # Below threshold

    initial_weight = link.weight

    # Apply strengthening
    apply_peripheral_strengthening(graph, "test", learning_rate=0.01, tick_duration=0.1)

    # Weight should NOT increase
    assert abs(link.weight - initial_weight) < 0.001, "Dormant nodes shouldn't strengthen links"
```

### Integration Tests

```python
def test_breakthrough_after_priming():
    """Test peripheral priming enables rapid breakthrough"""
    graph = create_consciousness_graph()

    # Phase 1: Peripheral priming (100 ticks)
    target_nodes = graph.find_nodes(related_to="delayed_message")

    for node in target_nodes:
        node.set_entity_energy("partner", 0.2)  # Peripheral

    # Let it prime
    for _ in range(100):
        apply_peripheral_strengthening(graph, "partner")
        decay_tick(graph, duration=0.1)

    # Measure link weights after priming
    primed_weights = [link.weight for link in graph.links if link.source in target_nodes]

    # Phase 2: Strong stimulus
    stimulus = {"type": "reminder", "content": "Message from Alice", "strength": 0.6}
    process_stimulus(stimulus, graph)

    # Should breakthrough rapidly
    for _ in range(5):  # Only 5 ticks needed (vs. 50 without priming)
        diffusion_tick(graph, duration=0.1)

    workspace = select_global_workspace(graph, current_goal=test_goal)

    # Partner should be in workspace
    assert any(c.entity == "partner" for c in workspace), "Primed entity should breakthrough"
```

### Phenomenological Validation

```python
def test_delayed_realization_phenomenology():
    """
    Test the "hours later I suddenly remembered" phenomenon

    Peripheral priming should enable this
    """
    graph = create_consciousness_graph()

    # T=0: Brief notification
    stimulus_t0 = {"type": "notification", "content": "Alice message", "strength": 0.3}
    process_stimulus(stimulus_t0, graph)

    # Energy in peripheral range
    message_node = graph.get_node("message_from_alice")
    assert 0.1 < message_node.get_entity_energy("partner") < 0.3

    # T=1-100: Other activity with periodic priming
    for tick in range(100):
        # Occasional weak reminders (phone visible)
        if tick % 20 == 0:
            weak_stimulus = {"type": "visual", "content": "phone screen", "strength": 0.1}
            process_stimulus(weak_stimulus, graph)

        apply_peripheral_strengthening(graph, "partner")
        decay_tick(graph, duration=0.1)

    # Links should have strengthened
    message_links = [link for link in graph.links if link.source == message_node]
    avg_link_weight = np.mean([link.weight for link in message_links])

    assert avg_link_weight > 0.4, "Peripheral priming should strengthen links"

    # T=100: Stronger reminder
    stimulus_t100 = {"type": "visual", "content": "phone with (1) badge", "strength": 0.4}
    process_stimulus(stimulus_t100, graph)

    # Should breakthrough quickly (pre-prepared by priming)
    for _ in range(5):
        diffusion_tick(graph, duration=0.1)

    workspace = select_global_workspace(graph, current_goal=test_goal)

    assert any(c.entity == "partner" for c in workspace), "Should breakthrough after priming"

    # Phenomenology: "Sudden realization after hours"
    # Reality: 100 ticks of peripheral preparation
```

---

## Open Questions

1. **Peripheral strengthening rate?**
   - Current: Same learning rate as conscious
   - Alternative: Different rate for peripheral vs. conscious
   - Confidence: Medium (0.6)

2. **Maximum peripheral duration?**
   - Current: No limit (can stay peripheral indefinitely)
   - Alternative: Force breakthrough or decay after N ticks
   - Confidence: Low (0.4)

3. **Pressure-to-threshold mapping?**
   - Current: Linear (30% max reduction)
   - Alternative: Nonlinear, sigmoid, etc.
   - Confidence: Low (0.5)

---

## Related Mechanisms

- **[04: Global Workspace](04_global_workspace_theory.md)** - Defines consciousness threshold
- **[09: Link Strengthening](09_link_strengthening.md)** - Strengthening mechanism
- **[08: Energy Decay](08_energy_decay.md)** - Peripheral energy decays too

---

## Implementation Checklist

- [ ] Define energy zones (DORMANT, PERIPHERAL, ACTIVE, FOCAL)
- [ ] Implement ActivationState analyzer
- [ ] Implement apply_peripheral_strengthening()
- [ ] Implement track_peripheral_accumulation()
- [ ] Implement calculate_peripheral_pressure()
- [ ] Implement detect_breakthrough_events()
- [ ] Implement stuck peripheral detection
- [ ] Implement relevance-weighted decay
- [ ] Write unit tests for peripheral strengthening
- [ ] Write integration tests for breakthrough after priming
- [ ] Write phenomenological validation (delayed realization)
- [ ] Add peripheral activity visualization
- [ ] Track breakthrough events for analysis

---

**Next:** [07: Energy Diffusion](07_energy_diffusion.md) - How energy spreads through the graph
