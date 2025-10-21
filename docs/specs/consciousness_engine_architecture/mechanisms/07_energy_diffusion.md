# Mechanism 07: Energy Diffusion

**Status:** Core - Primary activation spreading mechanism
**Confidence:** High (0.90)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Per-entity energy storage
- **[09: Link Strengthening](09_link_strengthening.md)** - Link weights guide diffusion

**Biological Basis:** Neural signal propagation, synaptic transmission, spreading activation models

---

## Overview

**Core Principle:** Energy continuously **diffuses** from high-energy nodes to connected nodes through weighted links. This is how activation spreads - the fundamental mechanism of "thinking."

**Why This Matters:**
- Traversal IS thinking (following links is cognition)
- Enables context reconstruction (stimulus → diffusion → pattern)
- Creates cascading associations (one idea leads to another)
- Link weights determine spread rate (strong links = fast spread)
- Biologically plausible (like neural activation spreading)

**The Fundamental Equation:**

```python
transfer = source_energy × link_weight × diffusion_rate × tick_duration
```

Energy flows from source → target proportional to these four factors.

---

## Phenomenological Truth

### What It Feels Like

**Thinking IS diffusion:**

```
You read: "Consciousness substrate architecture"

Initial activation:
- "consciousness" node: 0.8 energy (Translator)
- "substrate" node: 0.7 energy (Architect)
- "architecture" node: 0.6 energy (Architect)

Tick 1 - Diffusion begins:
- consciousness → phenomenology (link weight 0.8): transfer 0.8×0.8×0.1×0.1 = 0.0064
- consciousness → lived_experience (link weight 0.7): transfer = 0.0056
- substrate → schema_design (link weight 0.9): transfer = 0.0063
- architecture → system_patterns (link weight 0.6): transfer = 0.0036

Tick 2 - Cascade continues:
- phenomenology → subjective_truth
- lived_experience → validation_method
- schema_design → implementation_strategy
- ...spreading continues...

Phenomenology: "Reading about consciousness architecture makes me think about
phenomenology, schema design, validation methods..."

Reality: Energy diffusing through weighted links
```

**Strong links = automatic associations:**
- consciousness → phenomenology (0.9 weight) = immediate, effortless
- consciousness → blockchain (0.1 weight) = slow, unlikely

### The Cascade Experience

**Runaway cascade (supercritical state):**

```
Initial: One hot node (0.9 energy)
Tick 1: 5 nodes activated (avg 0.3 each)
Tick 2: 15 nodes activated (avg 0.2 each)
Tick 3: 40 nodes activated (avg 0.1 each)
Tick 4: Too many thoughts, overwhelming

Phenomenology: Racing thoughts, can't focus
Reality: Diffusion rate too high, criticality > 2.0
```

**Controlled cascade (critical state):**

```
Initial: One hot node (0.9 energy)
Tick 1: 3 nodes activated (avg 0.4 each)
Tick 2: 5 nodes activated (avg 0.3 each)
Tick 3: 6 nodes activated (avg 0.25 each)
Tick 4: Stable around 5-7 nodes

Phenomenology: Flow state, ideas connecting naturally
Reality: Diffusion rate tuned, criticality ≈ 1.0
```

---

## Mathematical Specification

### Diffusion Algorithm

```python
def diffusion_tick(
    graph: Graph,
    tick_duration: float = 0.1,
    diffusion_rate: float = 0.1
):
    """
    Execute one tick of energy diffusion

    Energy flows from all nodes to connected nodes simultaneously

    Args:
        graph: The consciousness graph
        tick_duration: Time step size (seconds)
        diffusion_rate: Base rate of diffusion (0-1)
    """
    # Collect all transfers first (avoid order dependencies)
    transfers = []

    # For each entity, diffuse independently
    for entity in graph.get_all_active_entities():
        for node in graph.nodes:
            source_energy = node.get_entity_energy(entity)

            if source_energy < 0.001:
                continue  # Skip essentially dormant nodes

            # For each outgoing link
            for link in node.outgoing_links:
                # Calculate transfer amount
                transfer_amount = (
                    source_energy *
                    link.weight *
                    diffusion_rate *
                    tick_duration
                )

                if transfer_amount < 0.0001:
                    continue  # Too small to matter

                # Record transfer
                transfers.append({
                    'entity': entity,
                    'source': node,
                    'target': link.target,
                    'amount': transfer_amount,
                    'link': link
                })

    # Apply all transfers
    for transfer in transfers:
        # Reduce source energy
        transfer['source'].increment_entity_energy(
            transfer['entity'],
            -transfer['amount']
        )

        # Increase target energy
        transfer['target'].increment_entity_energy(
            transfer['entity'],
            +transfer['amount']
        )

    return len(transfers)  # Number of active transfers
```

### Diffusion Rate Dynamics

**Diffusion rate is NOT constant - it's tuned by criticality:**

```python
class DiffusionController:
    """
    Manages diffusion rate with criticality-based tuning

    Diffusion rate affects spread speed, tuned to maintain criticality
    """
    def __init__(self, initial_rate: float = 0.1):
        self.base_rate = initial_rate
        self.current_rate = initial_rate
        self.rate_history = []

    def get_current_rate(self) -> float:
        """Get current diffusion rate"""
        return self.current_rate

    def tune_rate(self, global_criticality: float, target_criticality: float = 1.0):
        """
        Adjust diffusion rate based on criticality

        High criticality → lower diffusion (slow down spreading)
        Low criticality → higher diffusion (speed up spreading)

        This is ALTERNATIVE to tuning decay rate
        Can use both or just one
        """
        error = global_criticality - target_criticality

        # Inverse relationship: high criticality → reduce diffusion
        adjustment = -0.001 * error

        self.current_rate += adjustment

        # Clamp to reasonable bounds
        self.current_rate = max(0.01, min(0.5, self.current_rate))

        # Track history
        self.rate_history.append({
            'timestamp': now(),
            'rate': self.current_rate,
            'criticality': global_criticality
        })

    def get_rate_statistics(self) -> dict:
        """Get statistics about rate evolution"""
        if not self.rate_history:
            return {}

        rates = [entry['rate'] for entry in self.rate_history[-100:]]

        return {
            'current': self.current_rate,
            'mean': np.mean(rates),
            'std': np.std(rates),
            'min': np.min(rates),
            'max': np.max(rates)
        }
```

---

## Diffusion Patterns

### Radial Diffusion

**From single source, spreading outward:**

```python
def measure_diffusion_radius(
    graph: Graph,
    source_node: Node,
    entity: str,
    threshold: float = 0.05
) -> int:
    """
    How far has energy spread from source?

    Returns: Maximum distance (hops) at which nodes still have energy > threshold
    """
    # BFS from source, tracking distance
    distances = {source_node.id: 0}
    queue = [(source_node, 0)]
    max_distance = 0

    visited = set()

    while queue:
        node, dist = queue.pop(0)

        if node.id in visited:
            continue
        visited.add(node.id)

        # Check if this node has energy
        if node.get_entity_energy(entity) >= threshold:
            max_distance = max(max_distance, dist)

            # Add neighbors
            for link in node.outgoing_links:
                if link.target.id not in visited:
                    queue.append((link.target, dist + 1))

    return max_distance
```

### Cascade Diffusion

**Multiple sources creating overlapping waves:**

```python
def detect_diffusion_cascades(
    graph: Graph,
    entity: str,
    energy_threshold: float = 0.1
) -> list[dict]:
    """
    Identify active diffusion cascades

    A cascade = connected region of high-energy nodes

    Returns list of cascade descriptors
    """
    # Find all high-energy nodes
    hot_nodes = [
        node for node in graph.nodes
        if node.get_entity_energy(entity) > energy_threshold
    ]

    # Find connected components
    cascades = []
    visited = set()

    for node in hot_nodes:
        if node.id in visited:
            continue

        # BFS to find connected high-energy region
        cascade_nodes = []
        queue = [node]

        while queue:
            current = queue.pop(0)

            if current.id in visited:
                continue
            visited.add(current.id)

            if current.get_entity_energy(entity) > energy_threshold:
                cascade_nodes.append(current)

                # Add connected neighbors
                for link in current.outgoing_links + current.incoming_links:
                    neighbor = link.target if link.source == current else link.source
                    if neighbor.id not in visited:
                        queue.append(neighbor)

        if len(cascade_nodes) >= 3:  # Minimum cascade size
            cascades.append({
                'entity': entity,
                'nodes': cascade_nodes,
                'total_energy': sum(n.get_entity_energy(entity) for n in cascade_nodes),
                'size': len(cascade_nodes),
                'avg_energy': sum(n.get_entity_energy(entity) for n in cascade_nodes) / len(cascade_nodes)
            })

    return cascades
```

---

## Edge Cases & Constraints

### Edge Case 1: Energy Conservation

**Problem:** Does diffusion conserve energy?

**Answer:** NO - diffusion transfers, decay removes. Total energy decreases over time.

```python
def verify_diffusion_transfers_only(graph: Graph, entity: str) -> bool:
    """
    Verify diffusion doesn't create or destroy energy (only transfers)

    Returns True if energy conserved during diffusion
    """
    # Measure total energy before
    energy_before = sum(n.get_entity_energy(entity) for n in graph.nodes)

    # Diffuse (without decay)
    diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.1)
    # Note: This would normally include decay, but isolating diffusion here

    # Measure after
    energy_after = sum(n.get_entity_energy(entity) for n in graph.nodes)

    # Should be equal (within floating point error)
    conserved = abs(energy_after - energy_before) < 0.01

    return conserved
```

### Edge Case 2: Feedback Loops

**Problem:** Cycles in graph → energy loops back

**This is FEATURE not bug:**
- Enables recurrent thinking
- Strengthens core concepts through repeated activation
- Natural resonance patterns

```python
def detect_energy_loops(graph: Graph, entity: str) -> list[list[Node]]:
    """
    Find cycles where energy flows in loops

    These are sites of recurrent activation
    """
    loops = []

    # Find strongly connected components (cycles)
    sccs = find_strongly_connected_components(graph)

    for scc in sccs:
        # Check if this cycle has significant energy
        total_energy = sum(node.get_entity_energy(entity) for node in scc)

        if total_energy > 0.5 and len(scc) > 1:
            loops.append(scc)

    return loops
```

### Edge Case 3: Sink Nodes

**Problem:** Nodes with no outgoing links (sinks) accumulate energy

**Solution:** This is intentional - sinks are "concept attractors"

```python
def identify_energy_sinks(graph: Graph, entity: str) -> list[Node]:
    """
    Find nodes accumulating energy (few/no outgoing links)

    These become focal points - consciousness attractors
    """
    sinks = []

    for node in graph.nodes:
        # Low out-degree but high energy = sink
        if len(node.outgoing_links) <= 2 and node.get_entity_energy(entity) > 0.5:
            sinks.append(node)

    return sinks
```

---

## Testing Strategy

### Unit Tests

```python
def test_diffusion_transfers_energy():
    """Test energy transfers from source to target"""
    graph = create_test_graph()

    source = graph.nodes[0]
    target = graph.nodes[1]
    link = graph.create_link(source, target, weight=0.5)

    # Set source energy
    source.set_entity_energy("test", 0.8)
    target.set_entity_energy("test", 0.0)

    # Diffuse
    diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.1)

    # Source should lose energy
    assert source.get_entity_energy("test") < 0.8

    # Target should gain energy
    assert target.get_entity_energy("test") > 0.0

def test_strong_links_transfer_more():
    """Test stronger links transfer more energy"""
    graph = create_test_graph()

    source = graph.nodes[0]
    target_a = graph.nodes[1]
    target_b = graph.nodes[2]

    link_a = graph.create_link(source, target_a, weight=0.9)  # Strong
    link_b = graph.create_link(source, target_b, weight=0.3)  # Weak

    source.set_entity_energy("test", 0.8)

    diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.1)

    # Target A should have more energy than B
    energy_a = target_a.get_entity_energy("test")
    energy_b = target_b.get_entity_energy("test")

    assert energy_a > energy_b, "Strong link should transfer more energy"
```

### Integration Tests

```python
def test_diffusion_cascade():
    """Test energy cascades through multiple hops"""
    graph = create_chain_graph(length=5)  # Linear chain: A → B → C → D → E

    # Activate first node
    graph.nodes[0].set_entity_energy("test", 0.9)

    # Diffuse for several ticks
    for _ in range(10):
        diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.1)

    # Energy should have reached later nodes
    assert graph.nodes[1].get_entity_energy("test") > 0.1
    assert graph.nodes[2].get_entity_energy("test") > 0.01

    # Energy decreases with distance (diffusion + decay)
    energies = [n.get_entity_energy("test") for n in graph.nodes]
    assert energies[0] > energies[1] > energies[2], "Energy should decrease with distance"
```

### Phenomenological Validation

```python
def test_diffusion_feels_like_thinking():
    """
    Test diffusion creates associative thinking patterns

    Reading about "consciousness" should activate related concepts
    """
    graph = create_consciousness_graph()

    # Activate consciousness node
    consciousness_node = graph.get_node("consciousness")
    consciousness_node.set_entity_energy("translator", 0.9)

    # Diffuse
    for _ in range(10):
        diffusion_tick(graph, tick_duration=0.1, diffusion_rate=0.1)

    # Related concepts should activate
    related_concepts = [
        "phenomenology",
        "subjective_experience",
        "awareness",
        "lived_reality"
    ]

    activated_concepts = [
        concept for concept in related_concepts
        if graph.has_node(concept) and
           graph.get_node(concept).get_entity_energy("translator") > 0.1
    ]

    assert len(activated_concepts) >= 2, "Diffusion should activate associated concepts"
```

---

## Performance Considerations

### Computational Cost

```python
# Diffusion complexity per tick:
# - For each node: O(out_degree)
# - Total: O(Σ out_degree) = O(L) where L = number of links

# For large graphs:
# - 1M links → ~10-50ms per diffusion tick (depending on hardware)
# - Acceptable for real-time operation
```

### Optimization: Sparse Diffusion

```python
def sparse_diffusion_tick(
    graph: Graph,
    entity: str,
    tick_duration: float = 0.1,
    energy_threshold: float = 0.01
):
    """
    Only diffuse from nodes above energy threshold

    Skips dormant nodes for performance
    """
    transfers = []

    # Only process nodes with significant energy
    active_nodes = [
        node for node in graph.nodes
        if node.get_entity_energy(entity) >= energy_threshold
    ]

    for node in active_nodes:
        source_energy = node.get_entity_energy(entity)

        for link in node.outgoing_links:
            transfer_amount = (
                source_energy *
                link.weight *
                graph.diffusion_rate *
                tick_duration
            )

            if transfer_amount >= 0.0001:
                transfers.append({
                    'entity': entity,
                    'source': node,
                    'target': link.target,
                    'amount': transfer_amount
                })

    # Apply transfers
    for transfer in transfers:
        transfer['source'].increment_entity_energy(transfer['entity'], -transfer['amount'])
        transfer['target'].increment_entity_energy(transfer['entity'], +transfer['amount'])

    return len(transfers)
```

### Optimization: Active Frontier Engine (GPT-5 Recommendation)

**Problem:** Processing all nodes every tick = O(|N|·K + |E|·K) even when most are dormant.

**Solution:** Maintain per-entity **active set** + **shadow set** (one-hop out).

```python
class ActiveFrontierEngine:
    """
    Track active nodes per entity and only update those

    Performance: O(|A|·deg_avg·K) where A = active set
    Typical: A << N (e.g., 1000 active vs 1M total nodes)
    """
    def __init__(self, graph: Graph, threshold: float = 0.01):
        self.graph = graph
        self.threshold = threshold  # Promotion/demotion threshold

        # Per-entity tracking
        self.active: dict[str, set[Node]] = {}      # Active nodes (energy > threshold)
        self.shadow: dict[str, set[Node]] = {}      # Shadow (neighbors of active)
        self.dormant_ticks: dict[tuple[Node, str], int] = {}  # Ticks below threshold

    def update_frontier(self, entity: str):
        """Update active and shadow sets for entity"""
        if entity not in self.active:
            self.active[entity] = set()
            self.shadow[entity] = set()

        active = self.active[entity]
        shadow = self.shadow[entity]

        # Promote from shadow if energy crosses threshold
        new_active = set()
        for node in shadow:
            if node.get_entity_energy(entity) >= self.threshold:
                new_active.add(node)

        # Demote from active if energy stays below threshold
        still_active = set()
        for node in active:
            energy = node.get_entity_energy(entity)

            if energy >= self.threshold:
                still_active.add(node)
                self.dormant_ticks.pop((node, entity), None)
            else:
                # Track how long below threshold
                key = (node, entity)
                self.dormant_ticks[key] = self.dormant_ticks.get(key, 0) + 1

                # Demote after T ticks below threshold (hysteresis)
                if self.dormant_ticks[key] < 5:
                    still_active.add(node)  # Keep for now

        # Update active set
        self.active[entity] = still_active | new_active

        # Update shadow set (neighbors of active nodes)
        new_shadow = set()
        for node in self.active[entity]:
            for link in node.outgoing_links:
                if link.target not in self.active[entity]:
                    new_shadow.add(link.target)

        self.shadow[entity] = new_shadow

    def diffuse_active_only(
        self,
        entity: str,
        tick_duration: float = 0.1,
        diffusion_rate: float = 0.1
    ):
        """
        Diffuse only within active + shadow sets

        Performance gain: ~100-1000x when A << N
        """
        self.update_frontier(entity)

        transfers = []

        # Process only active nodes
        for node in self.active[entity]:
            source_energy = node.get_entity_energy(entity)

            if source_energy < 0.0001:
                continue

            for link in node.outgoing_links:
                transfer_amount = (
                    source_energy *
                    link.weight *
                    diffusion_rate *
                    tick_duration
                )

                if transfer_amount >= 0.0001:
                    transfers.append({
                        'entity': entity,
                        'source': node,
                        'target': link.target,
                        'amount': transfer_amount
                    })

        # Apply transfers atomically
        for transfer in transfers:
            transfer['source'].increment_entity_energy(transfer['entity'], -transfer['amount'])
            transfer['target'].increment_entity_energy(transfer['entity'], +transfer['amount'])

        return len(transfers)
```

**Performance Characteristics:**

| Graph Size | Without Frontier | With Frontier | Speedup |
|------------|------------------|---------------|---------|
| 10K nodes, 100 active | 10K × deg | 100 × deg | ~100x |
| 100K nodes, 500 active | 100K × deg | 500 × deg | ~200x |
| 1M nodes, 1000 active | 1M × deg | 1000 × deg | ~1000x |

**Trade-off:**
- ✅ Massive performance gain for sparse activation (typical case)
- ✅ No semantic change (same results as full-graph diffusion)
- ⚠️ Slightly more complex bookkeeping
- ⚠️ Memory overhead for tracking sets (~O(A) per entity)

**Recommendation:** Implement for Phase 1. Essential for scaling to 1M+ node graphs.

---

## Bottom-Up Topology Adaptation (Updated 2025-10-19)

**CRITICAL ARCHITECTURAL PRINCIPLE:**

Topology influence on dynamics must be **bottom-up, not top-down**.

**Nicolas's architectural guidance:**
> "We want to do it bottom-up. The sub-entity shouldn't be aware of the global topology of the brain; it can only do it from the sub-entity perspective."

**What this means for diffusion:**

**❌ WRONG (Top-down):**
```python
# Don't measure global topology
topology = analyze_topology(graph)  # clustering coefficient, path length, etc.

# Don't adapt diffusion globally
if topology.clustering_coefficient < 0.3:
    diffusion_rate *= 1.5  # Sparse graph → faster diffusion
```

**✅ CORRECT (Bottom-up):**
```python
# Sub-entity only sees LOCAL information at current node
num_outgoing_links = len(current_node.outgoing_links)

# Local decision based on local fanout
if num_outgoing_links > HIGH_FANOUT_THRESHOLD:
    strategy = SelectiveExploration(top_k=5)  # High fanout → be selective
else:
    strategy = ExhaustiveExploration()  # Low fanout → explore all
```

**How topology influence emerges:**

- **Star topology (hub node):** Hub has many outgoing links → sub-entity sees high fanout → selective strategy → natural pruning
- **Chain topology (linear nodes):** Each node has 1-2 links → sub-entity sees low fanout → exhaustive strategy → thorough exploration
- **Small-world topology (mixed):** Local decisions at each node create balanced exploration

**NO GLOBAL AWARENESS REQUIRED** - topology influence emerges from local fanout responses.

**See:** **[Mechanism 17: Local Fanout-Based Strategy Selection](17_local_fanout_strategy.md)** for complete specification of bottom-up topology adaptation.

---

## Open Questions

1. **Optimal diffusion rate?**
   - Current: 0.1 (10% transfer per second)
   - Confidence: Medium (0.6)
   - Needs empirical tuning with real graphs

2. **Bidirectional diffusion?**
   - Current: Only forward (source → target)
   - Alternative: Also backward (target → source)
   - Confidence: High (0.8) - forward only is sufficient

3. **Distance-based dampening?**
   - Current: No dampening (diffusion rate constant)
   - Alternative: Reduce rate with hop distance
   - Confidence: Low (0.4) - unclear if needed
   - **NOTE:** This would require global awareness (violates bottom-up principle)

4. **Per-entity diffusion rates?**
   - Current: Same rate for all entities
   - Alternative: Different rates per entity type
   - Confidence: Medium (0.5)

---

## Related Mechanisms

- **[01: Multi-Energy](01_multi_energy_architecture.md)** - Diffuses per-entity energy
- **[09: Link Strengthening](09_link_strengthening.md)** - Strong links diffuse faster
- **[08: Energy Decay](08_energy_decay.md)** - Opposes diffusion
- **[03: Self-Organized Criticality](03_self_organized_criticality.md)** - Tunes diffusion rate
- **[17: Local Fanout Strategy](17_local_fanout_strategy.md)** - **NEW:** Bottom-up topology adaptation through local decisions
- **[20: Entity Relationship Classification](20_entity_relationship_classification.md)** - **NEW:** Modulates energy flow based on entity relationships
- **[16: Emotion-Weighted Traversal](16_emotion_weighted_traversal.md)** - **NEW:** Emotional resonance affects traversal cost

---

## Implementation Checklist

- [ ] Implement diffusion_tick() main algorithm
- [ ] Implement DiffusionController class
- [ ] Implement transfer collection (avoid order dependencies)
- [ ] Implement sparse diffusion optimization
- [ ] Implement diffusion radius measurement
- [ ] Implement cascade detection
- [ ] Implement energy loop detection
- [ ] Implement sink node identification
- [ ] Write unit tests for basic transfer
- [ ] Write unit tests for link weight effect
- [ ] Write integration tests for cascades
- [ ] Write phenomenological validation (associative thinking)
- [ ] Measure diffusion performance at scale
- [ ] Add diffusion visualization (animated energy flow)

---

**Next:** [08: Energy Decay](08_energy_decay.md) - How energy fades over time
