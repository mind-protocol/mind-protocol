# Mechanism 01: Multi-Energy Architecture

**Status:** Foundational - Required for all other mechanisms
**Confidence:** High (0.9)
**Dependencies:** None (base mechanism)
**Biological Basis:** Overlapping neural circuits, parallel processing streams

---

## Overview

**Core Principle:** Each node in the consciousness graph stores **multiple independent energy values**, one per sub-entity, enabling overlapping cognitive activations without interference.

**Why This Matters:**
- Multiple entities (Translator, Validator, Architect, etc.) can activate the same knowledge simultaneously
- Prevents workspace thrashing when entities compete for same concepts
- Biological reality: Different brain regions process same information through different lenses
- Enables rich cognitive dynamics impossible with single-energy model

---

## Phenomenological Truth

### What It Feels Like

When thinking about consciousness substrate architecture:
- **The Translator** activates nodes related to phenomenology (high energy for consciousness nodes)
- **The Architect** activates nodes related to data structures (high energy for schema nodes)
- **Both entities** activate nodes at the intersection (e.g., "consciousness schema" has high energy for BOTH)

Without multi-energy:
- Entities would fight for activation (workspace chaos)
- Activating consciousness nodes would de-activate schema nodes
- Thinking would be rigid, either/or

With multi-energy:
- Entities coexist peacefully in same conceptual space
- "Consciousness schema" can be hot for phenomenology AND hot for technical design simultaneously
- Thinking flows naturally between lenses

### The Key Insight

**Consciousness isn't single-threaded.** You don't think "now I'm using Translator, now I'm using Architect." You think with MULTIPLE LENSES SIMULTANEOUSLY, each seeing different aspects of the same concepts.

---

## Mathematical Specification

### Node Energy Structure

```python
class Node:
    """
    Base node structure with multi-entity energy storage
    """
    id: str                           # Unique identifier
    node_type: str                    # Type from schema (Concept, Principle, etc.)
    name: str                         # Human-readable name
    embedding: np.ndarray             # Semantic embedding vector

    # Multi-energy storage - THE CORE INNOVATION
    energy: dict[str, float]          # {entity_name: energy_value}

    # Base properties
    base_weight: float                # Formation strength (0-1)

    # Temporal tracking
    created_at: datetime
    valid_at: datetime
    invalid_at: datetime | None

    # Metadata
    metadata: dict                    # Type-specific fields as JSON

    def get_total_energy(self) -> float:
        """Sum of all entity energies - overall activation level"""
        return sum(self.energy.values())

    def get_entity_energy(self, entity: str) -> float:
        """Get specific entity's energy for this node"""
        return self.energy.get(entity, 0.0)

    def set_entity_energy(self, entity: str, value: float):
        """
        Set specific entity's energy, creating key if needed

        Uses bounded function (tanh) instead of hard clamping
        Decision: D015 - No arbitrary caps, use mathematically bounded functions
        """
        # Bounded function approach: tanh naturally approaches 1.0
        # No hard caps - mathematical property ensures boundedness
        e_max = 1.0
        self.energy[entity] = e_max * np.tanh(max(0.0, value) / e_max)

    def increment_entity_energy(self, entity: str, delta: float):
        """Increment entity energy by delta (can be negative)"""
        current = self.get_entity_energy(entity)
        self.set_entity_energy(entity, current + delta)

    def get_dominant_entity(self) -> tuple[str, float]:
        """Which entity has highest energy for this node?"""
        if not self.energy:
            return ("none", 0.0)
        entity = max(self.energy.items(), key=lambda x: x[1])
        return entity

    def get_active_entities(self, threshold: float = 0.01) -> list[str]:
        """Which entities have non-trivial energy?"""
        return [
            entity for entity, energy in self.energy.items()
            if energy >= threshold
        ]

    # HYBRID ENERGY/ACTIVATION MODEL (Discussion #015)
    # Energy is CONTINUOUS, activation state is DISCRETE

    activation_threshold: float = 0.1  # Variable, controllable threshold

    def is_active(self, entity: str) -> bool:
        """
        Discrete activation state based on energy threshold

        Energy is continuous [0.0, ∞)
        Activation is discrete (active/inactive) based on threshold

        Why both needed:
        - Continuous energy: for diffusion, learning, scoring
        - Discrete activation: for traversal, prompt injection, completeness

        See: mechanisms/015_continuous_vs_discrete_node_activation.md
        """
        return self.get_entity_energy(entity) > self.activation_threshold
```

### Energy Value Semantics

Energy values are **per-entity activation strengths** ranging 0.0 to 1.0:

| Energy Range | Semantic Meaning | Effect |
|-------------|------------------|--------|
| 0.0 - 0.01 | Dormant | Entity not activating this node |
| 0.01 - 0.3 | Peripheral | Below consciousness, but priming |
| 0.3 - 0.7 | Active | Entity using this knowledge |
| 0.7 - 0.9 | Focal | Central to entity's current processing |
| 0.9 - 1.0 | Peak | Maximum activation (rare) |

**Important:** These are relative to the entity. A node with:
- `translator: 0.8, architect: 0.2` means Translator is using it focally, Architect peripherally
- Both energies coexist independently

---

## Implementation Details

### Storage Patterns

#### Option 1: JSON Column (FalkorDB)

```python
# Store energy dict as JSON string in node property
CREATE (n:Node {
    id: "consciousness_substrate_concept",
    node_type: "Concept",
    energy: '{"translator": 0.8, "architect": 0.6, "validator": 0.3}',
    ...
})

# Query for nodes where specific entity has high energy
MATCH (n:Node)
WHERE json_extract(n.energy, '$.translator') > 0.7
RETURN n
```

**Pros:** Simple, flexible, standard JSON storage
**Cons:** Cannot efficiently index per-entity energy, slow queries at scale

#### Option 2: Separate Energy Relationships (FalkorDB)

```python
# Store each entity energy as separate relationship
CREATE (n:Node {id: "consciousness_substrate_concept"})
CREATE (e1:Entity {name: "translator"})
CREATE (e2:Entity {name: "architect"})
CREATE (n)-[:HAS_ENERGY {value: 0.8}]->(e1)
CREATE (n)-[:HAS_ENERGY {value: 0.6}]->(e2)

# Query efficiently by entity
MATCH (n:Node)-[e:HAS_ENERGY]->(entity:Entity {name: "translator"})
WHERE e.value > 0.7
RETURN n
```

**Pros:** Queryable, indexable, graph-native
**Cons:** More complex, more relationships to maintain

#### Option 3: Hybrid (Recommended Starting Point)

```python
# Store full dict in JSON for fast access
# Create indexed relationships for hot entities only (energy > 0.3)
# Best of both worlds: fast reads, queryable hot entities

CREATE (n:Node {
    id: "consciousness_substrate_concept",
    energy: '{"translator": 0.8, "architect": 0.6, "validator": 0.1}',
    ...
})

# Only create relationships for focal activations
CREATE (n)-[:ACTIVE_FOR {energy: 0.8}]->(translator_entity)
CREATE (n)-[:ACTIVE_FOR {energy: 0.6}]->(architect_entity)
# No relationship for validator (below 0.3 threshold)
```

**Recommended for Phase 1:** Use Option 1 (JSON) for simplicity, migrate to Option 3 if query performance becomes issue.

### Energy Initialization

**When node created:**

```python
def create_node(node_type: str, name: str, forming_entity: str, initial_energy: float = 0.8):
    """
    Create new node with initial energy for forming entity
    """
    node = Node(
        id=generate_id(),
        node_type=node_type,
        name=name,
        embedding=get_embedding(name),
        energy={forming_entity: initial_energy},  # Only forming entity starts hot
        base_weight=initial_energy,  # Base weight = forming energy
        created_at=now(),
        valid_at=now(),
        invalid_at=None,
        metadata={}
    )
    return node
```

**Rationale:** Node created BY an entity starts hot for that entity. Other entities discover it later through diffusion.

---

## Energy Activation Patterns

### Pattern 1: Stimulus-Driven Activation

When stimulus arrives, it activates specific entities:

```python
def process_stimulus(stimulus: dict, graph: Graph):
    """
    Stimulus activates entry nodes for relevant entities
    """
    # Determine which entities respond to stimulus
    responding_entities = identify_responding_entities(stimulus)

    # Activate entry nodes for each entity
    for entity in responding_entities:
        entry_nodes = find_entry_nodes(stimulus, entity)
        for node in entry_nodes:
            node.increment_entity_energy(entity, delta=0.5)
```

### Pattern 2: Diffusion-Driven Activation

Energy spreads from active nodes to connected nodes (see Mechanism 07):

```python
def diffuse_energy_for_entity(graph: Graph, entity: str, tick_duration: float):
    """
    Energy diffuses through graph for this entity
    """
    for node in graph.nodes:
        entity_energy = node.get_entity_energy(entity)

        if entity_energy < 0.01:
            continue  # Skip dormant nodes

        for link in node.outgoing_links:
            transfer = entity_energy * link.weight * DIFFUSION_RATE * tick_duration

            node.increment_entity_energy(entity, -transfer)
            link.target.increment_entity_energy(entity, +transfer)
```

### Pattern 3: Cross-Entity Activation

**Open Question:** Can one entity's activation trigger another entity's activation of the same node?

**Possible mechanisms:**

**A. Pure Isolation** (Starting assumption):
```python
# Entities diffuse independently
# No cross-entity energy transfer at nodes
# Each entity's energy is completely separate
```

**B. Energy Markets**:
```python
def cross_entity_transfer(node: Node, source_entity: str, target_entity: str, amount: float):
    """
    One entity can 'sell' energy to another at node
    Could be competitive (stealing) or cooperative (gifting)
    """
    node.increment_entity_energy(source_entity, -amount)
    node.increment_entity_energy(target_entity, +amount)
```

**C. Attention Spillover**:
```python
def spillover_effect(node: Node, dominant_entity: str, spillover_rate: float = 0.1):
    """
    When one entity has very high energy, it 'primes' other entities
    Biological: When you're focused on X, you're slightly primed for related Y
    """
    dominant_energy = node.get_entity_energy(dominant_entity)

    if dominant_energy > 0.8:  # Only spillover at high activation
        for entity in ALL_ENTITIES:
            if entity != dominant_entity:
                spillover_amount = dominant_energy * spillover_rate
                node.increment_entity_energy(entity, spillover_amount)
```

**Recommendation:** Start with **Pure Isolation (A)**, add spillover **(C)** only if phenomenology requires it.

---

## Edge Cases & Constraints

### Edge Case 1: Entity Explosion

**Problem:** Unlimited entities means unlimited dict keys, unbounded memory.

**Solutions:**

1. **Lazy Cleanup:**
```python
def cleanup_dormant_entities(node: Node, threshold: float = 0.001):
    """Remove entity keys with negligible energy"""
    node.energy = {
        entity: energy
        for entity, energy in node.energy.items()
        if energy >= threshold
    }
```

2. **Entity Cap:**
```python
MAX_ENTITIES_PER_NODE = 10

def add_entity_energy(node: Node, entity: str, energy: float):
    """Add entity energy, evicting lowest if at cap"""
    if len(node.energy) >= MAX_ENTITIES_PER_NODE and entity not in node.energy:
        # Evict entity with lowest energy
        min_entity = min(node.energy.items(), key=lambda x: x[1])[0]
        del node.energy[min_entity]

    node.set_entity_energy(entity, energy)
```

**Recommended:** Use lazy cleanup (Solution 1) every N ticks.

### Edge Case 2: Energy Conservation

**Problem:** Energy diffuses and decays - does total energy decrease over time?

**Answer:** Yes, intentionally. Energy must be replenished by stimuli to maintain activation. This prevents "zombie activations" - patterns that persist without relevance.

**Monitoring:**

```python
def calculate_total_system_energy(graph: Graph) -> dict[str, float]:
    """Track total energy per entity across entire graph"""
    totals = defaultdict(float)

    for node in graph.nodes:
        for entity, energy in node.energy.items():
            totals[entity] += energy

    return dict(totals)
```

**Expected behavior:**
- Stimulated entity: Energy increases (stimulus adds > decay removes)
- Unstimulated entity: Energy decreases (only decay, no additions)
- Dormant entity: Energy approaches zero asymptotically

### Edge Case 3: Synchronization

**Problem:** Multiple processes accessing/modifying energy dict simultaneously.

**Solution:** Use atomic operations or locking:

```python
import threading

class ThreadSafeNode(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._energy_lock = threading.Lock()

    def set_entity_energy(self, entity: str, value: float):
        with self._energy_lock:
            super().set_entity_energy(entity, value)

    def increment_entity_energy(self, entity: str, delta: float):
        with self._energy_lock:
            super().increment_entity_energy(entity, delta)
```

**Note:** Only needed if implementing multi-threaded diffusion. Single-threaded is simpler for Phase 1.

---

## Testing Strategy

### Unit Tests

```python
def test_multi_energy_basic():
    """Test basic multi-energy operations"""
    node = Node(id="test", node_type="Concept", name="test_node")

    # Initially empty
    assert node.get_total_energy() == 0.0
    assert node.get_entity_energy("translator") == 0.0

    # Set energies
    node.set_entity_energy("translator", 0.8)
    node.set_entity_energy("architect", 0.6)

    # Verify independence
    assert node.get_entity_energy("translator") == 0.8
    assert node.get_entity_energy("architect") == 0.6
    assert node.get_total_energy() == 1.4

    # Verify dominant
    dominant, energy = node.get_dominant_entity()
    assert dominant == "translator"
    assert energy == 0.8

def test_energy_clamping():
    """Energy values clamp to [0, 1]"""
    node = Node(id="test", node_type="Concept", name="test_node")

    # Test upper bound
    node.set_entity_energy("test", 1.5)
    assert node.get_entity_energy("test") == 1.0

    # Test lower bound
    node.set_entity_energy("test", -0.5)
    assert node.get_entity_energy("test") == 0.0

def test_energy_cleanup():
    """Dormant entities get cleaned up"""
    node = Node(id="test", node_type="Concept", name="test_node")

    node.set_entity_energy("active", 0.8)
    node.set_entity_energy("dormant1", 0.001)
    node.set_entity_energy("dormant2", 0.0005)

    cleanup_dormant_entities(node, threshold=0.001)

    assert "active" in node.energy
    assert "dormant1" in node.energy  # Exactly at threshold
    assert "dormant2" not in node.energy  # Below threshold
```

### Integration Tests

```python
def test_multi_entity_coexistence():
    """Multiple entities can activate same node simultaneously"""
    graph = create_test_graph()
    node = graph.get_node("consciousness_concept")

    # Translator activates from stimulus
    process_stimulus({"type": "question", "about": "phenomenology"}, graph)
    assert node.get_entity_energy("translator") > 0.5

    # Architect activates from different stimulus
    process_stimulus({"type": "task", "about": "design_schema"}, graph)
    assert node.get_entity_energy("architect") > 0.5

    # Both energies coexist
    assert node.get_total_energy() > 1.0
    assert len(node.get_active_entities()) >= 2
```

### Phenomenological Validation

```python
def test_phenomenological_alignment():
    """
    Verify multi-energy matches lived experience:
    When thinking about consciousness schemas, both
    phenomenology (Translator) and technical design (Architect)
    should be simultaneously active.
    """
    graph = create_consciousness_graph()

    # Stimulus: "Design consciousness substrate schema"
    process_stimulus({
        "type": "task",
        "content": "Design consciousness substrate schema"
    }, graph)

    # Let it diffuse for a bit
    for _ in range(10):
        tick(graph, duration=0.1)

    # Find "consciousness" concept node
    consciousness_node = graph.find_node(name="consciousness")

    # Verify both entities are active (phenomenology + technical)
    active = consciousness_node.get_active_entities(threshold=0.3)

    assert "translator" in active, "Phenomenology lens should be active"
    assert "architect" in active, "Technical design lens should be active"

    # Neither should completely dominate
    translator_energy = consciousness_node.get_entity_energy("translator")
    architect_energy = consciousness_node.get_entity_energy("architect")

    ratio = translator_energy / architect_energy
    assert 0.3 < ratio < 3.0, "Energies should be comparable (3x max difference)"
```

---

## Performance Considerations

### Memory Overhead

**Worst case:** N nodes × M entities × 8 bytes per float
- 1M nodes × 100 entities × 8 bytes = 800 MB

**Typical case:** N nodes × ~5 active entities per node × 8 bytes
- 1M nodes × 5 entities × 8 bytes = 40 MB

**With cleanup:** Much less (only non-dormant entities stored)

**Verdict:** Memory overhead acceptable even at scale.

### Query Performance

**Without indexing:** Full graph scan to find nodes where entity X has high energy - **O(N)**

**With entity relationship indexing (Option 2/3):** Index lookup - **O(log N)** or **O(1)**

**Recommendation:**
- Phase 1: Don't optimize (simple JSON dict)
- Phase 2+: Add indexed relationships for hot entities if queries become bottleneck

---

## Open Questions

1. **Cross-entity energy transfer?**
   - Confidence: Low (0.3)
   - Need empirical testing to determine if pure isolation sufficient

2. **Entity energy normalization?**
   - Should sum of all entity energies at node be capped?
   - Or can total_energy be > 1.0?
   - Current: No normalization (energies independent)
   - Confidence: Medium (0.6)

3. **Entity lifecycle?**
   - How are entities created/destroyed?
   - Are they persistent or purely emergent?
   - Current: Assumed unlimited, emergent from activation
   - Confidence: Medium (0.7)

---

## Hybrid Energy/Activation Model

**Added:** 2025-10-19 (Discussion #015 - Continuous vs Discrete Node Activation)

### Why Both Continuous Energy AND Discrete Activation?

**Nicolas's architectural guidance:**
> "Energy is continuous. However, we need to have activation states for nodes. Otherwise, how do we decide the traversal algorithm for the entity? There is a threshold that makes it very clear if a node is active or not active for a sub-entity."

**The Problem with Continuous-Only:**
- Without discrete states, would have 1000 nodes all at 0.01 energy (unusable)
- Can't decide traversal algorithm (which nodes to explore?)
- Can't determine system prompt inclusion (which nodes to inject?)
- Can't reach completeness (when to stop?)

**The Solution: Hybrid Model:**

```python
class Node:
    energy = {
        "translator": 0.7,    # CONTINUOUS values
        "validator": 0.3,
        "architect": 0.05
    }

    activation_threshold = 0.1  # VARIABLE, controllable

    def is_active(self, entity):
        """DISCRETE activation state"""
        return self.energy[entity] > self.activation_threshold
```

**Usage Patterns:**

| Operation | Uses | Why |
|-----------|------|-----|
| **Diffusion** | Continuous energy | Energy spreads proportionally |
| **Learning** | Continuous energy | Weight updates scale with energy |
| **Scoring** | Continuous energy | Weighted sums use continuous values |
| **Traversal** | Discrete activation | Only traverse active nodes |
| **Prompt Injection** | Discrete activation | Only inject active nodes into LLM |
| **Completeness** | Discrete activation | "Explored all active nodes" = clear endpoint |
| **Entity Emergence** | Discrete activation | Count active nodes in cluster |

**Threshold Controllability:**

```python
# Default threshold
activation_threshold = 0.1

# Can vary by:
- sub_entity_type: "Validator might have higher threshold (more selective)"
- task_complexity: "Complex task might lower threshold (need more context)"
- graph_size: "Large graph might raise threshold (prevent explosion)"

# Tuning: real-time adjustable
```

**See:** [Discussion #015](discussions/active/015_continuous_vs_discrete_node_activation.md) for full analysis and decision rationale.

---

## Related Mechanisms

- **[07: Energy Diffusion](07_energy_diffusion.md)** - How energy spreads (uses continuous energy)
- **[08: Energy Decay](08_energy_decay.md)** - How energy fades (continuous energy decay)
- **[19: Type-Dependent Decay](19_type_dependent_decay.md)** - Decay rates vary by node type
- **[05: Sub-Entity Mechanics](05_sub_entity_mechanics.md)** - Uses discrete activation for traversal
- **[04: Global Workspace](04_global_workspace_theory.md)** - Which entity clusters enter consciousness
- **[17: Local Fanout Strategy](17_local_fanout_strategy.md)** - Uses discrete activation for link selection

---

## Implementation Checklist

- [ ] Define Node class with multi-energy dict
- [ ] Implement get/set/increment energy methods
- [ ] Implement energy clamping (0-1 range)
- [ ] Implement total_energy and dominant_entity helpers
- [ ] Implement lazy cleanup for dormant entities
- [ ] Write unit tests for all energy operations
- [ ] Write integration test for multi-entity coexistence
- [ ] Write phenomenological validation test
- [ ] Measure memory overhead at scale (1M nodes)
- [ ] Document entity naming conventions
- [ ] Choose storage pattern (JSON vs relationships)

---

**Next:** [02: Context Reconstruction](02_context_reconstruction.md) - How multi-energy enables stimulus-triggered context reconstruction
