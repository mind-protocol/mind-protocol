---
title: Link Strengthening
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/09_link_strengthening.md
depends_on: [foundations/multi_energy.md, foundations/diffusion.md]
summary: >
  Links strengthen when traversed during consciousness stream generation. Frequently-used paths become easier to traverse (higher link energy). Implements Hebbian learning at relationship level.
---

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

**The Learning Rule (Activation-State-Aware):**

```
Strengthening tier based on activation state (replacing D020):

STRONG (co-activation):
    IF source AND target both ACTIVE (crossed threshold in same frame)
    Δweight = learning_rate × energy_flow × 1.0
    Reason: "co_activation"

MEDIUM (causal credit):
    IF stride i→j CAUSED j to cross threshold (from inactive to active)
    Δweight = learning_rate × energy_flow × 0.6
    Reason: "causal"

WEAK (background spillover):
    IF neither crosses threshold (background diffusion)
    Δweight = learning_rate × energy_flow × 0.3
    Reason: "background"

All scaled by:
- Staged flow utility (z-score of stride value)
- Affect-weighted multiplier: m_affect = 1 + κ·tanh(||E^emo||)

Where:
- energy_flow = source_energy × current_weight × diffusion_rate
- κ = AFFECTIVE_MEMORY_KAPPA (default 0.4)
- E^emo = emotion coloring vector on link
```

**Critical Decision (Replaces D020):** Strengthening tier depends on activation state, NOT inactive-only.

**Rationale:**
- **Co-activation** (both active): Strongest signal - expertise formation, "fire together wire together"
- **Causal credit** (caused flip): Medium signal - this stride specifically enabled activation
- **Background spillover** (neither active): Weak signal - ambient diffusion, prevents noise learning
- **Guards:** Require stride utility (z-score) to filter noise; scale by flow magnitude
- **Affect weighting:** High-emotion experiences strengthen faster (bounded by tanh)

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
    stride_utility: float,
    learning_rate: float = 0.01,
    activation_threshold: float = 0.3,
    source_was_active_pre: bool = False,
    target_was_active_pre: bool = False,
    target_crossed_threshold: bool = False,
    kappa: float = 0.4
):
    """
    Strengthen link based on activation state (3-tier rule)

    Replaces D020 with activation-state-aware strengthening:
    - STRONG: Both nodes active (co-activation) → full rate
    - MEDIUM: Stride caused target flip → 60% rate
    - WEAK: Neither active (background) → 30% rate

    All scaled by:
    - stride_utility (z-score): filters noise, rewards valuable flows
    - m_affect: affect-weighted multiplier (1 + κ·tanh(||E^emo||))

    Args:
        link: The link to strengthen
        energy_flow: Amount of energy transferred this tick
        stride_utility: z-score of stride value (filters noise)
        learning_rate: Base learning rate (0-1)
        activation_threshold: Energy level above which node is "active"
        source_was_active_pre: Source was active before this stride
        target_was_active_pre: Target was active before this stride
        target_crossed_threshold: This stride caused target to activate
        kappa: Affective memory scaling factor
    """
    # Check current activation states
    source_active_post = link.source.get_total_energy() > activation_threshold
    target_active_post = link.target.get_total_energy() > activation_threshold

    # Determine strengthening tier
    if source_active_post and target_active_post:
        # STRONG: Co-activation (both active same frame)
        tier_scale = 1.0
        reason = "co_activation"
    elif target_crossed_threshold and not target_was_active_pre:
        # MEDIUM: Causal credit (stride caused flip)
        tier_scale = 0.6
        reason = "causal"
    else:
        # WEAK: Background spillover (neither active or no flip)
        tier_scale = 0.3
        reason = "background"

    # Guard: require minimum stride utility to learn
    if stride_utility < -1.0:  # Below -1 sigma = noise
        return

    # Compute affect-weighted multiplier
    emotion_magnitude = np.linalg.norm(link.emotion_vector) if hasattr(link, 'emotion_vector') else 0.0
    m_affect = 1.0 + kappa * np.tanh(emotion_magnitude)

    # Compute strengthening delta
    delta_weight = (
        learning_rate *
        energy_flow *
        tier_scale *
        max(0.0, stride_utility) *  # Only positive utility contributes
        m_affect
    )

    # Apply strengthening
    link.weight += delta_weight

    # Clamp to maximum
    link.weight = min(1.0, link.weight)

    # Track strengthening history with reason
    if not hasattr(link, 'strengthening_history'):
        link.strengthening_history = []

    link.strengthening_history.append({
        'timestamp': now(),
        'delta': delta_weight,
        'new_weight': link.weight,
        'energy_flow': energy_flow,
        'reason': reason,
        'tier_scale': tier_scale,
        'stride_utility': stride_utility,
        'affective_multiplier': m_affect,
        'emotion_magnitude': emotion_magnitude
    })

def integrated_diffusion_and_strengthening(
    graph: Graph,
    subentity: str,
    tick_duration: float = 0.1
):
    """
    Diffusion and strengthening happen simultaneously

    As energy flows, links strengthen
    """
    transfers = []

    for node in graph.nodes:
        source_energy = node.get_entity_energy(subentity)

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
                'subentity': subentity,
                'source': node,
                'target': link.target,
                'amount': energy_flow,
                'link': link
            })

            # Strengthen link DURING diffusion
            strengthen_link(link, energy_flow, learning_rate=graph.learning_rate)

    # Apply transfers
    for transfer in transfers:
        transfer['source'].increment_entity_energy(transfer['subentity'], -transfer['amount'])
        transfer['target'].increment_entity_energy(transfer['subentity'], +transfer['amount'])

    return len(transfers)
```

### Learning Rate Dynamics

```python
class LearningController:
    """
    Manages learning rate (how fast links strengthen)

    Can be global or per-subentity or even per-link
    """
    def __init__(self, base_rate: float = 0.01):
        self.base_rate = base_rate
        self.current_rate = base_rate

    def get_learning_rate(self, link: Link = None, subentity: str = None) -> float:
        """
        Get learning rate for specific context

        Could vary by:
        - Link type (semantic vs. causal)
        - Subentity (Validator learns slower, Explorer learns faster)
        - Link age (older links harder to change)
        - Current weight (diminishing returns near 1.0)
        """
        rate = self.base_rate

        # Diminishing returns: harder to strengthen already-strong links
        if link and link.weight > 0.8:
            rate *= 0.5  # 50% slower near maximum

        # Subentity-specific rates (if implementing)
        if subentity:
            entity_modifiers = {
                'explorer': 1.5,    # Fast learner
                'validator': 0.7,   # Slow, careful learner
                'architect': 1.0,   # Standard
            }
            rate *= entity_modifiers.get(subentity, 1.0)

        return rate
```

### Observability & Attribution

**Event Enrichment for weights.updated.*:**

```python
{
    "event": "weights.updated.stride",
    "link_id": "consciousness→substrate",
    "delta_log_w": 0.0023,
    "new_weight": 0.74,
    "reason": "co_activation",  # co_activation | causal | background
    "tier_scale": 1.0,
    "stride_utility": 1.8,  # z-score
    "affective_multiplier": 1.12,
    "emotion_magnitude": 0.35,
    "attribution": {
        "entity_ids": ["luca", "felix"],  # Which entities were active
        "task_context": "schema_design"
    },
    "timestamp": "..."
}
```

**Reason enum:**
- `co_activation`: Both nodes active in same frame (STRONG)
- `causal`: Stride caused target flip (MEDIUM)
- `background`: Neither active, background spillover (WEAK)

**Why attribution matters:**
- Understand WHICH context led to strengthening
- Debug unexpected weight evolution
- Validate learning is happening in right contexts
- Measure expertise formation per entity

### Read-Time Standardization

**Weight consumption (during traversal):**

Links are stored with raw learned weights, but may be **standardized** at read-time for stable dynamics:

```python
def get_effective_weight(link: Link, standardize: bool = True) -> float:
    """
    Get link weight for traversal

    Can apply standardization to prevent distribution drift:
    - Z-score normalization per node fan-out
    - Softmax per neighborhood
    - Raw (no standardization)

    Args:
        link: The link to read
        standardize: Whether to apply normalization

    Returns:
        Effective weight for this tick
    """
    raw_weight = link.weight

    if not standardize:
        return raw_weight

    # Z-score standardization per source node
    source_links = link.source.outgoing_links
    weights = [l.weight for l in source_links]

    mean_w = np.mean(weights)
    std_w = np.std(weights) if np.std(weights) > 0.01 else 1.0

    z_weight = (raw_weight - mean_w) / std_w

    # Convert back to [0, 1] via sigmoid
    effective = 1.0 / (1.0 + np.exp(-z_weight))

    return effective
```

**When to use:**
- **Raw weights**: Default for most use cases
- **Standardization**: When weight distributions drift over time (all links becoming strong or weak)
- **Softmax**: When selecting ONE link (competitive selection)

**Guard:** Monitor weight distributions; only standardize if drift detected (mean < 0.3 or mean > 0.7 after 1000 ticks).

---

## Strengthening Patterns

### Co-Activation Strengthening

**Nodes frequently active together → links between them strengthen:**

```python
def detect_co_activation_patterns(
    graph: Graph,
    subentity: str,
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
            if node.get_entity_energy(subentity) > co_activation_threshold
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
    subentity: str,
    min_weight: float = 0.7
) -> list[list[Node]]:
    """
    Find paths with consistently high link weights

    These are "highways" - automatically traversed associations
    """
    highways = []

    # Find chains of strong links
    for start_node in graph.nodes:
        if start_node.get_entity_energy(subentity) < 0.1:
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
