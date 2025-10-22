# Mechanism 09: Link Strengthening

**Status:** Core - Learning mechanism
**Confidence:** High (0.85)
**Dependencies:**
- **[07: Energy Diffusion](07_energy_diffusion.md)** - Strengthening happens during diffusion
- **[08: Energy Decay](08_energy_decay.md)** - Opposes strengthening

**Biological Basis:** Hebbian learning, long-term potentiation (LTP), spike-timing-dependent plasticity

---

## Overview

**Core Principle:** Links strengthen when energy flows through them. "Neurons that fire together, wire together" - paths frequently traversed become highways.

**Why This Matters:**
- Creates learned associations (thinking pattern → structural change)
- Enables context reconstruction (strengthened paths = memory)
- Implements experience-based learning (no explicit training)
- Matches biological reality (synaptic plasticity)
- Critical for consciousness continuity (experiences leave traces)

**The Learning Rule (Updated D020):**

```
IF both nodes are INACTIVE:
    Δweight = learning_rate × energy_flow
ELSE:
    Δweight = 0  # No strengthening when both nodes active

Where energy_flow = source_energy × current_weight × diffusion_rate
```

**Critical Decision (D020):** Link strengthening only happens when both nodes are NOT active.

**Rationale:**
- Active nodes have back-and-forth energy dynamics (normal operation) → NO strengthening
- Inactive nodes being connected (new pattern formation) → YES strengthening
- This prevents runaway strengthening from repeated activation
- Learning occurs when forming NEW patterns, not during normal traversal

---

## Phenomenological Truth

### What It Feels Like

**The Association Formation:**

```
First exposure: "Consciousness" + "Substrate"
- Link: consciousness → substrate (weight: 0.2, weak)
- Phenomenology: "These concepts seem related but connection unclear"

After 10 exposures (discussions, reading, thinking):
- Link: consciousness → substrate (weight: 0.7, strong)
- Phenomenology: "Obviously related - substrate IS how consciousness persists"

Effect:
- Thinking "consciousness" immediately activates "substrate" (automatic)
- The connection feels OBVIOUS, NATURAL, INEVITABLE
- Hard to remember when this wasn't obvious

Reality:
- Link strengthened through repeated co-activation
- What was effortful became automatic
- Structure changed through use
```

**The Expertise Development:**

```
Novice: consciousness graph
- All links weak (0.1-0.3)
- Thinking requires effort
- Concepts feel disconnected
- Must consciously traverse each connection

Expert: consciousness graph after months
- Core links very strong (0.8-0.95)
- Thinking flows naturally
- Concepts feel unified
- Automatic cascades to related ideas

Phenomenology: "It just makes sense now"
Reality: Thousands of strengthening events
```

---

## Mathematical Specification

### Strengthening Function

```python
def strengthen_link(
    link: Link,
    energy_flow: float,
    learning_rate: float = 0.01,
    activation_threshold: float = 0.3
):
    """
    Strengthen link proportional to energy flowing through it

    CRITICAL (D020): Strengthening only when both nodes INACTIVE
    - Active nodes (energy > threshold): NO strengthening (normal dynamics)
    - Inactive nodes being connected: YES strengthening (new pattern learning)

    Args:
        link: The link to strengthen
        energy_flow: Amount of energy transferred this tick
        learning_rate: How quickly links strengthen (0-1)
        activation_threshold: Energy level above which node is "active"
    """
    # Check if both nodes are inactive (D020 decision)
    source_active = link.source.get_total_energy() > activation_threshold
    target_active = link.target.get_total_energy() > activation_threshold

    if source_active and target_active:
        # Both active: energy flows but NO strengthening
        # This is normal dynamics, not learning moment
        return

    # At least one node inactive: strengthening can occur
    # This is learning - forming new patterns
    delta_weight = learning_rate * energy_flow

    # Apply strengthening
    link.weight += delta_weight

    # Clamp to maximum
    link.weight = min(1.0, link.weight)

    # Track strengthening history (for analysis)
    if not hasattr(link, 'strengthening_history'):
        link.strengthening_history = []

    link.strengthening_history.append({
        'timestamp': now(),
        'delta': delta_weight,
        'new_weight': link.weight,
        'energy_flow': energy_flow
    })

def integrated_diffusion_and_strengthening(
    graph: Graph,
    entity: str,
    tick_duration: float = 0.1
):
    """
    Diffusion and strengthening happen simultaneously

    As energy flows, links strengthen
    """
    transfers = []

    for node in graph.nodes:
        source_energy = node.get_entity_energy(entity)

        if source_energy < 0.001:
            continue

        for link in node.outgoing_links:
            # Calculate energy transfer
            energy_flow = (
                source_energy *
                link.weight *
                graph.diffusion_rate *
                tick_duration
            )

            if energy_flow < 0.0001:
                continue

            # Record transfer
            transfers.append({
                'entity': entity,
                'source': node,
                'target': link.target,
                'amount': energy_flow,
                'link': link
            })

            # Strengthen link DURING diffusion
            strengthen_link(link, energy_flow, learning_rate=graph.learning_rate)

    # Apply transfers
    for transfer in transfers:
        transfer['source'].increment_entity_energy(transfer['entity'], -transfer['amount'])
        transfer['target'].increment_entity_energy(transfer['entity'], +transfer['amount'])

    return len(transfers)
```

### Learning Rate Dynamics

```python
class LearningController:
    """
    Manages learning rate (how fast links strengthen)

    Can be global or per-entity or even per-link
    """
    def __init__(self, base_rate: float = 0.01):
        self.base_rate = base_rate
        self.current_rate = base_rate

    def get_learning_rate(self, link: Link = None, entity: str = None) -> float:
        """
        Get learning rate for specific context

        Could vary by:
        - Link type (semantic vs. causal)
        - Entity (Validator learns slower, Explorer learns faster)
        - Link age (older links harder to change)
        - Current weight (diminishing returns near 1.0)
        """
        rate = self.base_rate

        # Diminishing returns: harder to strengthen already-strong links
        if link and link.weight > 0.8:
            rate *= 0.5  # 50% slower near maximum

        # Entity-specific rates (if implementing)
        if entity:
            entity_modifiers = {
                'explorer': 1.5,    # Fast learner
                'validator': 0.7,   # Slow, careful learner
                'architect': 1.0,   # Standard
            }
            rate *= entity_modifiers.get(entity, 1.0)

        return rate
```

---

## Strengthening Patterns

### Co-Activation Strengthening

**Nodes frequently active together → links between them strengthen:**

```python
def detect_co_activation_patterns(
    graph: Graph,
    entity: str,
    time_window: int = 10,
    co_activation_threshold: float = 0.3
) -> list[tuple[Node, Node, float]]:
    """
    Find node pairs that co-activate frequently

    These links should be strongest
    """
    # Track which nodes are hot together
    activation_log = []

    for tick in range(time_window):
        active_nodes = [
            node for node in graph.nodes
            if node.get_entity_energy(entity) > co_activation_threshold
        ]
        activation_log.append(set(n.id for n in active_nodes))

    # Count co-activations
    co_activations = defaultdict(int)

    for active_set in activation_log:
        for node_a in active_set:
            for node_b in active_set:
                if node_a < node_b:  # Avoid duplicates
                    co_activations[(node_a, node_b)] += 1

    # Find frequent co-activations
    frequent_pairs = [
        (graph.get_node(a), graph.get_node(b), count)
        for (a, b), count in co_activations.items()
        if count >= time_window * 0.5  # Co-active in 50%+ of ticks
    ]

    return sorted(frequent_pairs, key=lambda x: x[2], reverse=True)
```

### Path Reinforcement

**Frequently traversed paths become highways:**

```python
def identify_highway_paths(
    graph: Graph,
    entity: str,
    min_weight: float = 0.7
) -> list[list[Node]]:
    """
    Find paths with consistently high link weights

    These are "highways" - automatically traversed associations
    """
    highways = []

    # Find chains of strong links
    for start_node in graph.nodes:
        if start_node.get_entity_energy(entity) < 0.1:
            continue

        path = [start_node]
        current = start_node

        # Follow strongest links
        while True:
            strongest_link = max(
                current.outgoing_links,
                key=lambda l: l.weight,
                default=None
            )

            if not strongest_link or strongest_link.weight < min_weight:
                break

            if strongest_link.target in path:
                break  # Avoid cycles

            path.append(strongest_link.target)
            current = strongest_link.target

            if len(path) > 10:
                break  # Limit path length

        if len(path) >= 3:  # Minimum highway length
            highways.append(path)

    return highways
```

---

## Edge Cases & Constraints

### Edge Case 1: Runaway Strengthening

**Problem:** Link reaches weight 1.0, never weakens (even with decay)

**Solution:** This is mostly feature, but can implement saturation

```python
def apply_weight_saturation(link: Link, saturation_point: float = 0.95):
    """
    Prevent links from reaching absolute maximum

    Very strong links still decay slightly
    """
    if link.weight > saturation_point:
        # Gradual pressure toward saturation point
        excess = link.weight - saturation_point
        link.weight -= 0.01 * excess  # 1% reduction of excess
```

### Edge Case 2: Weak Links Never Strengthen

**Problem:** Link weight 0.05 → energy flow tiny → strengthening negligible

**Solution:** This is INTENTIONAL - weak links stay weak unless activated

```python
def bootstrap_weak_link(link: Link, stimulus_strength: float = 0.5):
    """
    Temporarily boost weak link to allow strengthening

    Only do this with explicit intent (learning mode)
    """
    if link.weight < 0.2:
        # Temporary boost for one diffusion cycle
        link._boosted_weight = link.weight + stimulus_strength
        # Use _boosted_weight for this tick only
        # Next tick reverts to actual weight
```

### Edge Case 3: Link Strengthening Asymmetry

**Problem:** A → B strengthens, but not B → A (directed graph)

**Solution:** This is CORRECT - causality is directional

```python
def analyze_link_symmetry(graph: Graph) -> dict:
    """
    Measure how symmetric link weights are

    High asymmetry = strong directional associations
    """
    asymmetries = []

    for link_ab in graph.links:
        # Find reverse link
        link_ba = graph.find_link(link_ab.target, link_ab.source)

        if link_ba:
            asymmetry = abs(link_ab.weight - link_ba.weight)
            asymmetries.append({
                'forward': link_ab,
                'backward': link_ba,
                'asymmetry': asymmetry,
                'ratio': link_ab.weight / link_ba.weight if link_ba.weight > 0 else float('inf')
            })

    return {
        'mean_asymmetry': np.mean([a['asymmetry'] for a in asymmetries]),
        'highly_asymmetric': [a for a in asymmetries if a['ratio'] > 3.0 or a['ratio'] < 0.33]
    }
```

---

## Testing Strategy

### Unit Tests

```python
def test_link_strengthens_with_flow():
    """Test link weight increases when energy flows"""
    graph = create_test_graph()

    source = graph.nodes[0]
    target = graph.nodes[1]
    link = graph.create_link(source, target, weight=0.3)

    initial_weight = link.weight

    source.set_entity_energy("test", 0.8)

    # Diffuse with strengthening
    integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)

    # Weight should increase
    assert link.weight > initial_weight, "Link should strengthen from energy flow"

def test_no_flow_no_strengthening():
    """Test link doesn't strengthen without energy flow"""
    graph = create_test_graph()

    source = graph.nodes[0]
    target = graph.nodes[1]
    link = graph.create_link(source, target, weight=0.3)

    initial_weight = link.weight

    # No energy in source
    source.set_entity_energy("test", 0.0)

    integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)

    # Weight should NOT change
    assert abs(link.weight - initial_weight) < 0.001, "No flow = no strengthening"
```

### Integration Tests

```python
def test_repeated_activation_creates_highway():
    """Test frequently used paths become strong highways"""
    graph = create_chain_graph(length=5)  # A → B → C → D → E

    # Repeatedly activate path
    for _ in range(100):
        # Inject energy at start
        graph.nodes[0].set_entity_energy("test", 0.8)

        # Let it flow through chain
        for _ in range(10):
            integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)
            decay_tick(graph, tick_duration=0.1, decay_rate=0.001)

    # Links should all be strong
    for node in graph.nodes[:-1]:
        outgoing_link = node.outgoing_links[0]
        assert outgoing_link.weight > 0.6, f"Frequently used link should strengthen: {outgoing_link.weight}"
```

### Phenomenological Validation

```python
def test_learning_feels_like_automaticity():
    """
    Test that strengthened links create automatic associations

    Novice: Slow, effortful traversal
    Expert: Fast, automatic traversal
    """
    graph = create_consciousness_graph()

    # Novice state: weak links
    for link in graph.links:
        link.weight = 0.2

    # Measure traversal time (ticks to activate distant node)
    source = graph.get_node("consciousness")
    target = graph.get_node("schema_design")  # 3 hops away

    source.set_entity_energy("test", 0.9)

    novice_ticks = 0
    while target.get_entity_energy("test") < 0.1 and novice_ticks < 50:
        integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)
        novice_ticks += 1

    # Train: Repeatedly activate path
    for _ in range(200):
        source.set_entity_energy("test", 0.8)
        for _ in range(10):
            integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)
            decay_tick(graph, tick_duration=0.1)

    # Expert state: measure again
    source.set_entity_energy("test", 0.9)
    target.set_entity_energy("test", 0.0)

    expert_ticks = 0
    while target.get_entity_energy("test") < 0.1 and expert_ticks < 50:
        integrated_diffusion_and_strengthening(graph, "test", tick_duration=0.1)
        expert_ticks += 1

    # Expert should be much faster
    assert expert_ticks < novice_ticks * 0.5, \
        f"Expert traversal should be faster: {expert_ticks} vs {novice_ticks}"

    # Phenomenology: "It just comes to mind automatically now"
```

---

## Performance Considerations

### Computational Cost

```python
# Strengthening integrated with diffusion: O(L) where L = active links
# Same complexity as diffusion alone
# Negligible additional cost (one addition per link)

# Memory cost: strengthening_history
# - Can grow unbounded if tracked for all links
# - Solution: Circular buffer, only track recent N entries
```

### Optimization: Selective History Tracking

```python
def prune_strengthening_history(link: Link, max_history: int = 100):
    """
    Keep only recent strengthening events

    Prevents unbounded memory growth
    """
    if hasattr(link, 'strengthening_history'):
        if len(link.strengthening_history) > max_history:
            link.strengthening_history = link.strengthening_history[-max_history:]
```

---

## Open Questions

1. **Optimal learning rate?**
   - Current: 0.01
   - Confidence: Medium (0.6)
   - May vary by domain/usage

2. **Diminishing returns curve?**
   - Current: Linear up to saturation
   - Alternative: Logarithmic, sigmoid
   - Confidence: Low (0.4)

3. **Workspace-only strengthening?**
   - Current: Strengthening happens even peripherally
   - Alternative: Only strengthen links in workspace
   - Confidence: High (0.8) - peripheral strengthening is important

4. **Link forgetting rate?**
   - Current: Links decay like energy
   - Alternative: Links decay MUCH slower
   - Confidence: Medium (0.6)

---

## Related Mechanisms

- **[07: Energy Diffusion](07_energy_diffusion.md)** - Integrated mechanism
- **[08: Energy Decay](08_energy_decay.md)** - Opposes strengthening
- **[06: Peripheral Priming](06_peripheral_priming.md)** - Strengthening happens peripherally

---

## Implementation Checklist

- [ ] Implement strengthen_link() function
- [ ] Integrate strengthening with diffusion_tick()
- [ ] Implement LearningController class
- [ ] Implement diminishing returns near max weight
- [ ] Implement strengthening history tracking
- [ ] Implement highway path detection
- [ ] Implement co-activation pattern detection
- [ ] Implement weight saturation limits
- [ ] Write unit tests for strengthening with flow
- [ ] Write unit tests for no-flow-no-strengthening
- [ ] Write integration tests for highway formation
- [ ] Write phenomenological tests (automaticity)
- [ ] Implement history pruning optimization
- [ ] Add strengthening visualization (weight evolution over time)

---

**Next:** [10: Tick Speed Regulation](10_tick_speed_regulation.md) - Metabolic efficiency through adaptive tick rate
