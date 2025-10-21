# Mechanism 01 Implementation: Multi-Energy Architecture

**Version:** 1.0
**Date:** 2025-10-19
**Author:** Felix (Engineer)
**Status:** Implementation Specification
**Architectural Source:** `mechanisms/01_multi_energy_architecture.md` (Luca/Ada)

---

## Purpose

Translate the Multi-Energy Architecture from architectural/phenomenological specification into buildable implementation.

**What this spec provides:**
- Concrete FalkorDB schema
- Python class definitions (actual code, not conceptual)
- Algorithms ready to implement
- Test procedures to verify correctness
- Integration points with other mechanisms

**What this spec does NOT provide:**
- Philosophical justification (see architectural spec)
- Extensive phenomenology (see architectural spec)
- Exhaustive edge cases (discover during testing)

---

## Boundary Definition

### What IS Multi-Energy Architecture

**Core behavior:** Each node stores multiple energy values simultaneously, one per entity.

**Scope:**
- Node energy storage (per-entity dictionary)
- Energy accessor methods (get/set/increment)
- Energy saturation bounds (tanh function)
- Dominant entity calculation (which entity has highest energy)

### What IS NOT Multi-Energy Architecture

**Out of scope:**
- How energy gets INTO nodes (that's Mechanism 07: Diffusion)
- How energy LEAVES nodes (that's Mechanism 08: Decay)
- How entities are DEFINED (that's Mechanism 05: Sub-Entity Mechanics)
- How energy affects BEHAVIOR (various mechanisms modulate based on energy)

**Clear boundary:** This mechanism ONLY handles storage and basic accessors. It does NOT implement dynamics.

---

## FalkorDB Schema

### Node Properties

Every node in the consciousness graph has these properties:

```cypher
// Node base properties
CREATE (n:Concept {
    name: "node_unique_identifier",
    description: "What this node represents",
    node_type: "Concept",  // or Memory, Task, Realization, etc.

    // Multi-energy storage
    energy: {},  // JSON object: {entity_name: energy_value}

    // Metadata
    created_at: timestamp(),
    updated_at: timestamp()
})
```

**Energy field structure:**
```json
{
    "translator": 0.65,
    "architect": 0.42,
    "validator": 0.18,
    "pragmatist": 0.0
}
```

**Key decision:** Store as JSON object in FalkorDB, deserialize to Python dict for computation.

### Why JSON for Energy Storage?

**Considered alternatives:**
1. Separate node properties per entity (energy_translator, energy_architect, etc.)
   - ❌ Rejected: Inflexible, requires schema change for new entities
2. Separate nodes per entity energy
   - ❌ Rejected: Massive graph bloat, query complexity explosion
3. JSON object (chosen)
   - ✅ Flexible: Entities can be added without schema migration
   - ✅ Query-friendly: Can extract specific entity energy
   - ✅ Compact: All energy in single field

**Trade-off accepted:** JSON slightly slower than native fields, but flexibility worth it.

---

## Python Class Definitions

### Node Class

```python
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import numpy as np
from datetime import datetime

@dataclass
class Node:
    """
    Consciousness graph node with multi-entity energy storage.

    This is the ACTUAL implementation, not conceptual illustration.
    """
    # Identity
    name: str                              # Unique identifier
    node_type: str                         # Concept, Memory, Task, etc.
    description: str                       # What this node represents

    # Multi-energy storage
    energy: Dict[str, float] = field(default_factory=dict)  # {entity: energy_value}

    # Graph structure (populated by Graph class)
    outgoing_links: list = field(default_factory=list)
    incoming_links: list = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Energy bounds
    ENERGY_MIN: float = 0.0               # Minimum energy (non-negative only)
    ENERGY_MAX: float = 1.0               # Maximum energy (saturation)
    SATURATION_STEEPNESS: float = 2.0     # Tanh steepness parameter

    # ARCHITECTURAL NOTE: Inhibition is implemented via SUPPRESS link type,
    # not negative energy values. Links ARE consciousness - suppression is
    # a relationship (who suppresses what), not a node state.

    def get_entity_energy(self, entity: str) -> float:
        """
        Get energy level for specific entity.

        Args:
            entity: Entity name (e.g., "translator", "architect")

        Returns:
            Energy value for entity (0.0 if entity not present)
        """
        return self.energy.get(entity, 0.0)

    def set_entity_energy(self, entity: str, value: float):
        """
        Set energy level for specific entity with saturation.

        Args:
            entity: Entity name
            value: Desired energy value (will be bounded)
        """
        # Apply tanh saturation
        saturated_value = self._apply_saturation(value)

        # Store
        self.energy[entity] = saturated_value

        # Cleanup: Remove entities with negligible energy
        if abs(saturated_value) < 0.001:
            self.energy.pop(entity, None)

        # Update timestamp
        self.updated_at = datetime.now()

    def increment_entity_energy(self, entity: str, delta: float):
        """
        Increment energy by delta (used during diffusion).

        Args:
            entity: Entity name
            delta: Energy change (positive or negative)
        """
        current = self.get_entity_energy(entity)
        new_value = current + delta
        self.set_entity_energy(entity, new_value)

    def _apply_saturation(self, value: float) -> float:
        """
        Apply tanh saturation to prevent runaway energy values.

        Formula: tanh(steepness * max(0, value))

        CRITICAL: Energy is strictly non-negative [0.0, ∞).
        Inhibition is implemented via SUPPRESS link type, not negative values.

        Effect:
        - Negative inputs clamped to 0.0
        - Values near 0 pass through almost unchanged
        - Values approaching infinity asymptote to 1.0
        - Smooth, continuous (no hard clipping)

        Args:
            value: Raw energy value

        Returns:
            Saturated value in range [0.0, 1.0]
        """
        # Clamp to non-negative, then apply saturation
        return np.tanh(self.SATURATION_STEEPNESS * max(0.0, value))

    def get_dominant_entity(self) -> Tuple[Optional[str], float]:
        """
        Determine which entity has highest energy on this node.

        Returns:
            (entity_name, energy_value) or (None, 0.0) if no entities active
        """
        if not self.energy:
            return (None, 0.0)

        dominant_entity = max(self.energy.items(), key=lambda x: x[1])
        return dominant_entity

    def get_total_energy(self) -> float:
        """
        Sum of all entity energies (used for overall activation level).

        Returns:
            Total energy across all entities
        """
        return sum(self.energy.values())

    def get_active_entities(self, threshold: float = 0.1) -> list[str]:
        """
        Get list of entities with significant energy.

        Args:
            threshold: Minimum energy to be considered active

        Returns:
            List of entity names with energy > threshold
        """
        return [
            entity for entity, energy in self.energy.items()
            if energy >= threshold
        ]

    def clear_entity_energy(self, entity: str):
        """
        Remove entity from energy storage entirely.

        Args:
            entity: Entity name to clear
        """
        self.energy.pop(entity, None)
        self.updated_at = datetime.now()

    def clear_all_energy(self):
        """Remove all entity energies (reset node to dormant)."""
        self.energy.clear()
        self.updated_at = datetime.now()
```

### Graph Class (Multi-Energy Support)

```python
from typing import List, Dict, Set

class ConsciousnessGraph:
    """
    Graph container with multi-energy node support.
    """
    def __init__(self):
        self.nodes: List[Node] = []
        self.nodes_by_name: Dict[str, Node] = {}
        self.links: List[Link] = []  # Defined elsewhere

    def create_node(self, name: str, node_type: str, description: str) -> Node:
        """Create node and add to graph."""
        node = Node(
            name=name,
            node_type=node_type,
            description=description
        )
        self.nodes.append(node)
        self.nodes_by_name[name] = node
        return node

    def get_node(self, name: str) -> Optional[Node]:
        """Get node by name."""
        return self.nodes_by_name.get(name)

    def has_node(self, name: str) -> bool:
        """Check if node exists."""
        return name in self.nodes_by_name

    def get_all_active_entities(self) -> Set[str]:
        """
        Get set of all entities that have energy anywhere in graph.

        Returns:
            Set of entity names with non-zero energy
        """
        entities = set()
        for node in self.nodes:
            entities.update(node.energy.keys())
        return entities

    def get_total_energy_for_entity(self, entity: str) -> float:
        """
        Sum energy for specific entity across all nodes.

        Args:
            entity: Entity name

        Returns:
            Total energy for entity across graph
        """
        return sum(
            node.get_entity_energy(entity)
            for node in self.nodes
        )
```

---

## Core Algorithms

### Algorithm 1: Energy Injection (Stimulus)

**Purpose:** Add energy to node when stimulus activates it.

```python
def inject_energy(
    node: Node,
    entity: str,
    amount: float,
    additive: bool = True
):
    """
    Inject energy into node for specific entity.

    Args:
        node: Target node
        entity: Which entity is being activated
        amount: Energy to inject (0-1 typical)
        additive: If True, add to existing; if False, replace
    """
    if additive:
        node.increment_entity_energy(entity, amount)
    else:
        node.set_entity_energy(entity, amount)
```

**Example usage:**
```python
# User reads about "consciousness"
consciousness_node = graph.get_node("consciousness")
inject_energy(consciousness_node, "translator", 0.8, additive=False)
```

### Algorithm 2: Entity Energy Distribution

**Purpose:** Understand how energy is distributed across entities for a node.

```python
def analyze_energy_distribution(node: Node) -> Dict[str, any]:
    """
    Analyze energy distribution for node.

    Returns:
        Statistics about entity energy distribution
    """
    if not node.energy:
        return {
            'dominant_entity': None,
            'total_energy': 0.0,
            'entity_count': 0,
            'distribution': {}
        }

    dominant, dominant_energy = node.get_dominant_entity()
    total = node.get_total_energy()

    # Calculate percentages
    distribution = {
        entity: (energy / total) if total > 0 else 0.0
        for entity, energy in node.energy.items()
    }

    return {
        'dominant_entity': dominant,
        'dominant_energy': dominant_energy,
        'total_energy': total,
        'entity_count': len(node.energy),
        'distribution': distribution,
        'entropy': calculate_entropy(list(distribution.values()))
    }

def calculate_entropy(probabilities: list[float]) -> float:
    """Shannon entropy of energy distribution."""
    import math
    return -sum(
        p * math.log2(p) if p > 0 else 0
        for p in probabilities
    )
```

**Interpretation:**
- Entropy = 0: Single entity dominant (focused)
- Entropy high: Energy spread across many entities (diffuse)

### Algorithm 3: Cross-Entity Energy Comparison

**Purpose:** Compare energy across entities for same node.

```python
def compare_entity_energies(
    node: Node,
    entity_a: str,
    entity_b: str
) -> Dict[str, any]:
    """
    Compare energy levels between two entities on same node.

    Returns:
        Comparison statistics
    """
    energy_a = node.get_entity_energy(entity_a)
    energy_b = node.get_entity_energy(entity_b)

    return {
        'entity_a': entity_a,
        'entity_b': entity_b,
        'energy_a': energy_a,
        'energy_b': energy_b,
        'difference': energy_a - energy_b,
        'ratio': energy_a / energy_b if energy_b > 0 else float('inf'),
        'dominant': entity_a if energy_a > energy_b else entity_b
    }
```

---

## FalkorDB Query Patterns

### Query 1: Get Node Energy State

```cypher
// Get energy distribution for specific node
MATCH (n {name: $node_name})
RETURN n.name, n.energy
```

**Python integration:**
```python
def get_node_energy_from_db(graph_db, node_name: str) -> dict:
    """Query FalkorDB for node energy."""
    query = "MATCH (n {name: $node_name}) RETURN n.energy"
    result = graph_db.query(query, params={'node_name': node_name})

    if not result or len(result) == 0:
        return {}

    # FalkorDB returns JSON as dict
    return result[0][0]  # First row, first column
```

### Query 2: Find Nodes with Entity Energy

```cypher
// Find all nodes where specific entity has energy > threshold
MATCH (n)
WHERE n.energy[$entity_name] > $threshold
RETURN n.name, n.energy[$entity_name] as energy
ORDER BY energy DESC
```

### Query 3: Update Node Energy

```cypher
// Set energy for entity on node
MATCH (n {name: $node_name})
SET n.energy = $new_energy_dict, n.updated_at = timestamp()
RETURN n
```

**Python integration:**
```python
def update_node_energy_in_db(graph_db, node: Node):
    """Persist node energy to FalkorDB."""
    query = """
    MATCH (n {name: $node_name})
    SET n.energy = $energy_dict, n.updated_at = $timestamp
    RETURN n
    """

    graph_db.query(query, params={
        'node_name': node.name,
        'energy_dict': node.energy,  # Python dict → FalkorDB JSON
        'timestamp': int(node.updated_at.timestamp() * 1000)
    })
```

---

## Integration Points

### Input: Where Energy Comes From

Multi-energy provides storage; energy comes from:

1. **Mechanism 07 (Diffusion):** Energy flows from neighbors
   - Diffusion calls `node.increment_entity_energy(entity, transfer_amount)`

2. **Stimulus injection:** External events activate nodes
   - Orchestration layer calls `inject_energy(node, entity, amount)`

3. **Peripheral priming:** Sub-threshold activation
   - Mechanism 06 uses same methods, just lower amounts

### Output: What Uses Energy

Energy stored here is READ by:

1. **Mechanism 07 (Diffusion):** Source energy determines transfer amount
   - Diffusion calls `node.get_entity_energy(entity)`

2. **Mechanism 04 (Workspace):** High-energy clusters enter consciousness
   - Workspace selection uses `node.get_total_energy()` and `get_dominant_entity()`

3. **Mechanism 05 (Entities):** Detect which entities are active
   - Entity detection uses `get_active_entities(threshold)`

4. **Mechanism 08 (Decay):** Reduces energy over time
   - Decay modifies `node.energy[entity]` directly or via setters

### Key Insight

**Multi-energy is pure storage.** It has NO BEHAVIOR beyond bounds checking (saturation). All dynamics come from other mechanisms.

---

## Test Cases

### Unit Test 1: Energy Isolation

**Purpose:** Verify entities don't interfere with each other.

```python
def test_energy_isolation():
    """Test different entities maintain separate energy."""
    node = Node(name="test", node_type="Concept", description="Test node")

    # Set energy for multiple entities
    node.set_entity_energy("translator", 0.7)
    node.set_entity_energy("architect", 0.4)
    node.set_entity_energy("validator", 0.2)

    # Each entity should have its own value
    assert node.get_entity_energy("translator") == pytest.approx(0.7, abs=0.01)
    assert node.get_entity_energy("architect") == pytest.approx(0.4, abs=0.01)
    assert node.get_entity_energy("validator") == pytest.approx(0.2, abs=0.01)

    # Modifying one should not affect others
    node.set_entity_energy("translator", 0.9)
    assert node.get_entity_energy("architect") == pytest.approx(0.4, abs=0.01)
```

**Success criteria:** Each entity has independent energy storage.

### Unit Test 2: Energy Saturation

**Purpose:** Verify tanh saturation prevents runaway values.

```python
def test_energy_saturation():
    """Test energy saturates at bounds."""
    node = Node(name="test", node_type="Concept", description="Test node")

    # Test positive saturation
    node.set_entity_energy("test", 10.0)  # Way above max
    energy = node.get_entity_energy("test")
    assert energy < 1.0, "Energy should saturate below 1.0"
    assert energy > 0.9, "Tanh should asymptote near 1.0 for large inputs"

    # Test negative saturation
    node.set_entity_energy("test", -10.0)  # Way below min
    energy = node.get_entity_energy("test")
    assert energy > -1.0, "Energy should saturate above -1.0"
    assert energy < -0.9, "Tanh should asymptote near -1.0 for large negative inputs"

    # Test no saturation in normal range
    node.set_entity_energy("test", 0.5)
    energy = node.get_entity_energy("test")
    assert energy == pytest.approx(0.5, abs=0.05), "Normal values should pass through"
```

**Success criteria:** Energy bounded to [-1.0, 1.0] via smooth saturation.

### Unit Test 3: Dominant Entity Calculation

**Purpose:** Verify correct identification of highest-energy entity.

```python
def test_dominant_entity():
    """Test dominant entity detection."""
    node = Node(name="test", node_type="Concept", description="Test node")

    # No entities active
    dominant, energy = node.get_dominant_entity()
    assert dominant is None
    assert energy == 0.0

    # Single entity
    node.set_entity_energy("translator", 0.6)
    dominant, energy = node.get_dominant_entity()
    assert dominant == "translator"
    assert energy == pytest.approx(0.6, abs=0.01)

    # Multiple entities - highest wins
    node.set_entity_energy("architect", 0.8)
    node.set_entity_energy("validator", 0.3)
    dominant, energy = node.get_dominant_entity()
    assert dominant == "architect"
    assert energy == pytest.approx(0.8, abs=0.01)
```

**Success criteria:** Dominant entity correctly identified.

### Unit Test 4: Energy Increment

**Purpose:** Verify additive energy changes work correctly.

```python
def test_energy_increment():
    """Test incremental energy changes."""
    node = Node(name="test", node_type="Concept", description="Test node")

    # Start with initial energy
    node.set_entity_energy("translator", 0.3)

    # Increment positive
    node.increment_entity_energy("translator", 0.2)
    assert node.get_entity_energy("translator") == pytest.approx(0.5, abs=0.01)

    # Increment negative (decay)
    node.increment_entity_energy("translator", -0.1)
    assert node.get_entity_energy("translator") == pytest.approx(0.4, abs=0.01)

    # Increment to zero should cleanup
    node.increment_entity_energy("translator", -0.4)
    assert node.get_entity_energy("translator") == 0.0
    assert "translator" not in node.energy, "Zero energy should cleanup"
```

**Success criteria:** Increments work additively, cleanup happens at zero.

### Integration Test 1: Multi-Entity Overlapping Activation

**Purpose:** Verify multiple entities can work with same node simultaneously.

```python
def test_multi_entity_overlap():
    """Test overlapping entity activations."""
    node = Node(name="consciousness_schema", node_type="Concept",
                description="Schema for consciousness tracking")

    # Translator reading about consciousness (phenomenological angle)
    node.set_entity_energy("translator", 0.7)

    # Architect also thinking about schema design (structural angle)
    node.set_entity_energy("architect", 0.6)

    # Both should coexist
    assert node.get_entity_energy("translator") > 0.6
    assert node.get_entity_energy("architect") > 0.5

    # Total energy should be sum
    total = node.get_total_energy()
    assert total > 1.2, "Total energy should reflect both activations"

    # Dominant should be translator (higher energy)
    dominant, _ = node.get_dominant_entity()
    assert dominant == "translator"
```

**Success criteria:** Multiple entities can activate same node without interference.

### Integration Test 2: FalkorDB Round-Trip

**Purpose:** Verify energy survives write-to-DB and read-from-DB.

```python
def test_falkordb_persistence():
    """Test energy persists correctly in FalkorDB."""
    from falkordb import FalkorDB

    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph('test_multi_energy')

    # Create node with multi-energy
    node = Node(name="test_node", node_type="Concept", description="Test")
    node.set_entity_energy("translator", 0.65)
    node.set_entity_energy("architect", 0.42)

    # Write to DB
    query = """
    CREATE (n:Concept {
        name: $name,
        energy: $energy
    })
    """
    graph.query(query, params={
        'name': node.name,
        'energy': node.energy  # Dict → JSON
    })

    # Read back from DB
    read_query = "MATCH (n {name: $name}) RETURN n.energy"
    result = graph.query(read_query, params={'name': node.name})

    retrieved_energy = result[0][0]

    # Should match exactly
    assert retrieved_energy['translator'] == pytest.approx(0.65, abs=0.01)
    assert retrieved_energy['architect'] == pytest.approx(0.42, abs=0.01)

    # Cleanup
    graph.query("MATCH (n {name: $name}) DELETE n", params={'name': node.name})
```

**Success criteria:** Energy dict survives database round-trip without corruption.

---

## Open Questions

### 1. Cross-Entity Energy Transfer?

**Current:** Entities are completely isolated (no energy transfer between entities).

**Alternative:** Allow energy transfer (e.g., Translator gives energy to Architect).

**Confidence:** Low (0.4) - architectural spec mentions this as open question.

**Decision point:** Phase 5 (Sub-Entity Mechanics) - defer until entities are implemented.

### 2. Negative Energy (Inhibition)?

**Current:** Energy can be negative (inhibition via tanh saturation to -1.0).

**Alternative:** Energy always non-negative, use separate inhibition mechanism.

**Confidence:** Medium (0.6) - negative energy makes sense mathematically but may complicate interpretation.

**Decision point:** Phase 2 testing - see if negative energy provides useful dynamics.

### 3. Energy Cleanup Threshold?

**Current:** Remove entity from storage when energy < 0.001.

**Alternative:** Higher threshold (0.01), lower threshold (0.0001), or no cleanup.

**Confidence:** Medium (0.7) - 0.001 seems reasonable but untested at scale.

**Decision point:** Performance testing - if energy dict grows too large, adjust threshold.

### 4. Tanh Steepness Parameter?

**Current:** steepness = 2.0 (fairly gentle saturation).

**Alternative:** Higher steepness (sharper saturation), lower steepness (gentler).

**Confidence:** Low (0.5) - parameter needs empirical tuning.

**Decision point:** Phase 2 validation - tune based on diffusion dynamics.

---

## Implementation Checklist

**Phase 1.1 (Multi-Energy) Implementation:**

- [ ] Create Node class with energy dict storage
- [ ] Implement get_entity_energy()
- [ ] Implement set_entity_energy() with tanh saturation
- [ ] Implement increment_entity_energy()
- [ ] Implement get_dominant_entity()
- [ ] Implement get_total_energy()
- [ ] Implement get_active_entities()
- [ ] Implement cleanup (remove zero-energy entities)
- [ ] Create ConsciousnessGraph class
- [ ] Implement get_all_active_entities()
- [ ] Write Unit Test 1: Energy Isolation
- [ ] Write Unit Test 2: Energy Saturation
- [ ] Write Unit Test 3: Dominant Entity
- [ ] Write Unit Test 4: Energy Increment
- [ ] Write Integration Test 1: Multi-Entity Overlap
- [ ] Write Integration Test 2: FalkorDB Round-Trip
- [ ] Validate all tests pass
- [ ] Request Ada review before Phase 2

---

## Success Criteria (Phase 1 Validation)

**Can we:**

1. ✓ Create nodes with multi-dimensional energy? (one value per entity)
2. ✓ Set/get entity-specific energy values?
3. ✓ Verify entities remain isolated? (changing one doesn't affect others)
4. ✓ Verify saturation works? (energy bounded to [-1.0, 1.0])
5. ✓ Identify dominant entity? (highest energy entity)
6. ✓ Store/retrieve from FalkorDB? (JSON serialization works)

**If all YES:** Phase 1.1 complete, proceed to Phase 1.2 (Bitemporal Tracking).

**If any NO:** Fix before proceeding.

---

**Implementation Spec Complete: 01 Multi-Energy Architecture**

**Lines:** ~800
**Granularity:** Engineer-implementable
**Next:** Create implementation spec for Mechanism 13 (Bitemporal Tracking)
