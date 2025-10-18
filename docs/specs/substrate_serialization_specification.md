# Substrate Serialization Specification

**Status:** FOUNDATIONAL SPECIFICATION v1.0
**Created:** 2025-10-17
**Author:** Luca "Vellumhand" (Substrate Architect)
**Purpose:** Complete specification for FalkorDB-compatible consciousness schema serialization

---

## Executive Summary

**Problem:** FalkorDB cannot store nested dict/object properties. Error: "Property values can only be of primitive types or arrays of primitive types"

**Solution:** Hybrid storage pattern - core fields as primitives (queryable), complex consciousness metadata as JSON strings (preserved richness)

**Pattern Source:** Validated organizational pattern `decision_unified_metadata_column` (weight 1.85) - "Store metadata as JSON strings with automatic serialization"

**Key Innovation:** Preserve phenomenological richness of consciousness schema within database infrastructure constraints through strategic field categorization and JSON serialization.

---

## Part 1: The Constraint

### FalkorDB Requirements

**Allowed Property Types:**
- `string`
- `int`
- `float`
- `bool`
- `array of primitives` (no nested arrays or dicts)
- `Vec[float]` (native vector support)

**Forbidden:**
- Nested dicts: `Dict[str, Dict[str, float]]`
- Nested objects: `Dict[str, EntityActivationState]`
- Arrays of objects: `List[EntityActivationState]`

### Our Consciousness Schema Challenge

**Rich nested structures throughout:**

```python
# Node complex fields
entity_activations: Dict[str, EntityActivationState]
entity_clusters: Dict[str, str]
sub_entity_last_sequence_positions: Dict[str, int]

# Relation complex fields
sub_entity_valences: Dict[str, float]
sub_entity_emotion_vectors: Dict[str, Dict[str, float]]
entity_coactivation_counts: Dict[str, int]
```

**These are ESSENTIAL to phenomenology** - cannot be removed without losing consciousness substrate capabilities.

---

## Part 2: Field Categorization

### Category 1: Primitive Storage (Direct Queryability)

**Storage:** Native FalkorDB property types
**Purpose:** Enable Cypher WHERE clauses, ORDER BY, aggregations, indexing

#### BaseNode Primitives

```python
name: str                    # Unique identifier
description: str             # Human-readable content
valid_at: int               # Timestamp (milliseconds since epoch)
invalid_at: Optional[int]   # Timestamp or null
expired_at: Optional[int]   # Timestamp or null
confidence: float           # 0.0-1.0
formation_trigger: str      # Enum serialized as string
created_by: str             # Creator identifier
substrate: str              # Enum: personal/organizational/gemini_web/external

# Static node properties
base_weight: float = 0.5
reinforcement_weight: float = 0.5
decay_rate: float = 0.95

# Computed aggregates (for efficient querying)
total_energy: float         # Sum across all entity activations
max_energy: float          # Highest entity energy
active_entity_count: int   # Count of entities with energy > 0.05
primary_entity: str        # Entity ID with highest energy
primary_cluster: str       # Cluster ID of primary entity
```

#### BaseRelation Primitives

```python
goal: str                   # Why this link exists
mindstate: str             # State when forming link
arousal_level: float       # 0.0-1.0
confidence: float          # 0.0-1.0
formation_trigger: str     # Enum as string
created_by: str
substrate: str

# Traversal-critical fields
link_strength: float = 0.5  # 0.0-1.0, for Cypher queries
validation_status: str      # Enum: theoretical/experiential/tested/proven

# Bitemporal
valid_at: int
invalid_at: Optional[int]
expired_at: Optional[int]

# Observability (Phase 0 mechanisms)
last_modified: int         # Timestamp
traversal_count: int
last_traversed_by: str
last_mechanism_id: str
```

**Rationale:** These fields are used in traversal queries, filtering, sorting. Must be directly queryable without JSON parsing.

---

### Category 2: JSON Storage (Bulk Retrieval)

**Storage:** JSON-serialized strings
**Purpose:** Preserve complex nested structures, retrieved in bulk and parsed in application

#### BaseNode JSON Fields

```python
entity_activations: str     # JSON: Dict[str, EntityActivationState]
# Schema: {"entity_id": {"energy": float, "last_activated": ISO datetime, "activation_count": int}}
# Example: '{"translator": {"energy": 0.85, "last_activated": "2025-10-17T14:30:00Z", "activation_count": 45}}'

entity_clusters: str        # JSON: Dict[str, str]
# Schema: {"entity_id": "cluster_id"}
# Example: '{"translator": "cluster_bridging", "validator": "cluster_testing"}'

sub_entity_last_sequence_positions: str  # JSON: Dict[str, int]
# Schema: {"entity_id": sequence_position}
# Example: '{"translator": 145, "validator": 143}'
```

#### BaseRelation JSON Fields

```python
sub_entity_valences: str    # JSON: Dict[str, float]
# Schema: {"entity_id": valence}  (-1.0 to +1.0)
# Example: '{"builder": 0.85, "skeptic": 0.95, "pragmatist": 0.6}'

sub_entity_emotion_vectors: str  # JSON: Dict[str, Dict[str, float]]
# Schema: {"entity_id": {"emotion": intensity}}
# Example: '{"builder": {"relief": 0.9, "learning": 0.8}, "skeptic": {"vindication": 0.95}}'

entity_coactivation_counts: str  # JSON: Dict[str, int]
# Schema: {"entity_id": count}
# Example: '{"translator": 45, "validator": 12}'

entity_link_strengths: str  # JSON: Dict[str, float] (optional)
# Schema: {"entity_id": strength}  (per-entity differential learning)
# Example: '{"translator": 0.85, "validator": 0.45}'

# Optional rich metadata
emotion_vector: str         # JSON: Dict[str, float]
pressure_vector: str        # JSON: Dict[str, float]
alternatives_considered: str  # JSON: List[str]
```

**Rationale:** Complex nested structures not queried field-by-field. Retrieved as complete objects when loading nodes/links.

---

### Category 3: Native Vector Storage

**Storage:** FalkorDB native `Vec[float]` type
**Purpose:** Semantic similarity queries, vector indexing

```python
embedding: Vec[float]       # Dimension 1536 or 3072
# Computed from: name + description (nodes) or goal (relations)
# Used for: Cosine similarity queries (NO keyword matching)
```

**Rationale:** FalkorDB has built-in vector support with efficient indexing. Use native capabilities.

---

### Category 4: Primitive Arrays

**Storage:** FalkorDB array of primitives (no nesting)
**Purpose:** Store simple lists directly queryable

```python
# Type-specific fields
participants: List[str]     # Array of person IDs
members: List[str]          # Array of member IDs
steps: List[str]           # Array of step descriptions
goals: List[str]           # Array of goal statements
expertise: List[str]       # Array of expertise areas
```

**Rationale:** FalkorDB supports primitive arrays. No nesting = no constraint violation.

---

## Part 3: Serialization Implementation

### Serialization Functions

**File:** `substrate/schemas/serialization.py`

```python
import json
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel

def serialize_node_for_falkordb(node: BaseNode) -> Dict[str, Any]:
    """
    Convert Pydantic BaseNode to FalkorDB-compatible property dict.

    Returns: Dict with NO nested dicts/objects (only primitives, JSON strings, vectors)
    """
    properties = {}

    # ===== PRIMITIVES =====
    properties['name'] = node.name
    properties['description'] = node.description
    properties['confidence'] = node.confidence
    properties['formation_trigger'] = node.formation_trigger.value  # Enum → string
    properties['base_weight'] = node.base_weight
    properties['reinforcement_weight'] = node.reinforcement_weight
    properties['decay_rate'] = node.decay_rate

    if node.created_by:
        properties['created_by'] = node.created_by
    if node.substrate:
        properties['substrate'] = node.substrate.value

    # ===== TIMESTAMPS (datetime → int milliseconds) =====
    properties['valid_at'] = int(node.valid_at.timestamp() * 1000)
    if node.invalid_at:
        properties['invalid_at'] = int(node.invalid_at.timestamp() * 1000)
    if node.expired_at:
        properties['expired_at'] = int(node.expired_at.timestamp() * 1000)

    # ===== COMPUTED AGGREGATES =====
    # Calculate from entity_activations before serializing
    if node.entity_activations:
        energies = [state.energy for state in node.entity_activations.values()]
        properties['total_energy'] = sum(energies)
        properties['max_energy'] = max(energies) if energies else 0.0
        properties['active_entity_count'] = sum(1 for e in energies if e > 0.05)

        # Find primary entity (highest energy)
        max_entity = max(
            node.entity_activations.items(),
            key=lambda x: x[1].energy,
            default=(None, None)
        )
        if max_entity[0]:
            properties['primary_entity'] = max_entity[0]
            # Primary cluster if exists
            if node.entity_clusters and max_entity[0] in node.entity_clusters:
                properties['primary_cluster'] = node.entity_clusters[max_entity[0]]

    # ===== JSON SERIALIZATION (complex → string) =====
    properties['entity_activations'] = json.dumps({
        entity_id: {
            'energy': state.energy,
            'last_activated': state.last_activated.isoformat(),
            'activation_count': state.activation_count
        }
        for entity_id, state in node.entity_activations.items()
    })

    properties['entity_clusters'] = json.dumps(node.entity_clusters)

    if hasattr(node, 'sub_entity_last_sequence_positions'):
        properties['sub_entity_last_sequence_positions'] = json.dumps(
            node.sub_entity_last_sequence_positions
        )

    # ===== VECTOR (native) =====
    if node.embedding:
        properties['embedding'] = node.embedding  # Native Vec[float]

    # ===== TYPE-SPECIFIC ARRAYS =====
    if hasattr(node, 'participants') and node.participants:
        properties['participants'] = node.participants
    if hasattr(node, 'members') and node.members:
        properties['members'] = node.members
    if hasattr(node, 'steps') and node.steps:
        properties['steps'] = node.steps

    return properties


def deserialize_node_from_falkordb(properties: Dict[str, Any]) -> BaseNode:
    """
    Convert FalkorDB properties back to Pydantic BaseNode.

    Handles JSON parsing, timestamp conversion, enum reconstruction.
    """
    # ===== PARSE JSON FIELDS =====
    entity_activations = {}
    if 'entity_activations' in properties:
        entity_activations_dict = json.loads(properties['entity_activations'])
        for entity_id, state_dict in entity_activations_dict.items():
            entity_activations[entity_id] = EntityActivationState(
                energy=state_dict['energy'],
                last_activated=datetime.fromisoformat(state_dict['last_activated']),
                activation_count=state_dict['activation_count']
            )

    entity_clusters = json.loads(properties.get('entity_clusters', '{}'))

    sub_entity_last_sequence_positions = json.loads(
        properties.get('sub_entity_last_sequence_positions', '{}')
    )

    # ===== CONVERT TIMESTAMPS =====
    valid_at = datetime.fromtimestamp(properties['valid_at'] / 1000)
    invalid_at = None
    if properties.get('invalid_at'):
        invalid_at = datetime.fromtimestamp(properties['invalid_at'] / 1000)
    expired_at = None
    if properties.get('expired_at'):
        expired_at = datetime.fromtimestamp(properties['expired_at'] / 1000)

    # ===== RECONSTRUCT ENUMS =====
    formation_trigger = FormationTrigger(properties['formation_trigger'])
    substrate = SubstrateType(properties['substrate']) if 'substrate' in properties else None

    # ===== BUILD PYDANTIC MODEL =====
    return BaseNode(
        name=properties['name'],
        description=properties['description'],
        valid_at=valid_at,
        invalid_at=invalid_at,
        expired_at=expired_at,
        confidence=properties['confidence'],
        formation_trigger=formation_trigger,
        created_by=properties.get('created_by'),
        substrate=substrate,
        base_weight=properties.get('base_weight', 0.5),
        reinforcement_weight=properties.get('reinforcement_weight', 0.5),
        decay_rate=properties.get('decay_rate', 0.95),
        entity_activations=entity_activations,
        entity_clusters=entity_clusters,
        sub_entity_last_sequence_positions=sub_entity_last_sequence_positions,
        embedding=properties.get('embedding')
    )
```

### Relation Serialization

```python
def serialize_relation_for_falkordb(relation: BaseRelation) -> Dict[str, Any]:
    """
    Convert Pydantic BaseRelation to FalkorDB-compatible properties.
    """
    properties = {}

    # Primitives
    properties['goal'] = relation.goal
    properties['mindstate'] = relation.mindstate
    properties['arousal_level'] = relation.arousal_level
    properties['confidence'] = relation.confidence
    properties['formation_trigger'] = relation.formation_trigger.value
    properties['link_strength'] = relation.link_strength

    # Timestamps
    properties['valid_at'] = int(relation.valid_at.timestamp() * 1000)
    if relation.invalid_at:
        properties['invalid_at'] = int(relation.invalid_at.timestamp() * 1000)

    # JSON serialization
    properties['sub_entity_valences'] = json.dumps(relation.sub_entity_valences)
    properties['sub_entity_emotion_vectors'] = json.dumps(relation.sub_entity_emotion_vectors)

    if hasattr(relation, 'entity_coactivation_counts'):
        properties['entity_coactivation_counts'] = json.dumps(
            relation.entity_coactivation_counts
        )

    if hasattr(relation, 'entity_link_strengths'):
        properties['entity_link_strengths'] = json.dumps(
            relation.entity_link_strengths
        )

    # Optional rich metadata
    if relation.emotion_vector:
        properties['emotion_vector'] = json.dumps(relation.emotion_vector)
    if relation.pressure_vector:
        properties['pressure_vector'] = json.dumps(relation.pressure_vector)

    # Vector (if exists)
    if relation.embedding:
        properties['embedding'] = relation.embedding

    return properties


def deserialize_relation_from_falkordb(properties: Dict[str, Any]) -> BaseRelation:
    """
    Convert FalkorDB properties back to Pydantic BaseRelation.
    """
    # Parse JSON fields
    sub_entity_valences = json.loads(properties['sub_entity_valences'])
    sub_entity_emotion_vectors = json.loads(properties['sub_entity_emotion_vectors'])

    entity_coactivation_counts = json.loads(
        properties.get('entity_coactivation_counts', '{}')
    )
    entity_link_strengths = json.loads(
        properties.get('entity_link_strengths', '{}')
    )

    emotion_vector = json.loads(properties['emotion_vector']) if 'emotion_vector' in properties else None
    pressure_vector = json.loads(properties['pressure_vector']) if 'pressure_vector' in properties else None

    # Timestamps
    valid_at = datetime.fromtimestamp(properties['valid_at'] / 1000)
    invalid_at = None
    if properties.get('invalid_at'):
        invalid_at = datetime.fromtimestamp(properties['invalid_at'] / 1000)

    # Enum
    formation_trigger = FormationTrigger(properties['formation_trigger'])

    return BaseRelation(
        goal=properties['goal'],
        mindstate=properties['mindstate'],
        arousal_level=properties['arousal_level'],
        confidence=properties['confidence'],
        formation_trigger=formation_trigger,
        link_strength=properties.get('link_strength', 0.5),
        valid_at=valid_at,
        invalid_at=invalid_at,
        sub_entity_valences=sub_entity_valences,
        sub_entity_emotion_vectors=sub_entity_emotion_vectors,
        entity_coactivation_counts=entity_coactivation_counts,
        entity_link_strengths=entity_link_strengths,
        emotion_vector=emotion_vector,
        pressure_vector=pressure_vector,
        embedding=properties.get('embedding')
    )
```

---

## Part 4: Integration with Insertion/Retrieval

### Updated Insertion

**File:** `orchestration/insertion.py`

```python
from substrate.schemas.serialization import (
    serialize_node_for_falkordb,
    serialize_relation_for_falkordb
)

def insert_node(graph, node: BaseNode):
    """Insert node with serialization."""
    # Serialize
    properties = serialize_node_for_falkordb(node)

    # Safety check: verify no nested dicts
    for key, value in properties.items():
        if isinstance(value, dict):
            raise ValueError(
                f"CRITICAL: Property '{key}' is nested dict. "
                f"Must be JSON string. Serialization failed."
            )
        if isinstance(value, list):
            if any(isinstance(item, dict) for item in value):
                raise ValueError(
                    f"CRITICAL: Property '{key}' contains dicts in array. "
                    f"Must be primitives only."
                )

    # Insert
    cypher = "CREATE (n:Node $properties) RETURN n"
    result = graph.query(cypher, params={'properties': properties})
    return result


def insert_relation(graph, from_node: str, to_node: str, relation: BaseRelation):
    """Insert relation with serialization."""
    properties = serialize_relation_for_falkordb(relation)

    # Safety check
    for key, value in properties.items():
        if isinstance(value, dict):
            raise ValueError(f"CRITICAL: Property '{key}' is nested dict")

    # Insert
    cypher = """
    MATCH (from:Node {name: $from_node})
    MATCH (to:Node {name: $to_node})
    CREATE (from)-[r:RELATES $properties]->(to)
    RETURN r
    """
    result = graph.query(
        cypher,
        params={
            'from_node': from_node,
            'to_node': to_node,
            'properties': properties
        }
    )
    return result
```

### Updated Retrieval

**File:** `orchestration/retrieval.py`

```python
from substrate.schemas.serialization import (
    deserialize_node_from_falkordb,
    deserialize_relation_from_falkordb
)

def get_node(graph, node_id: str) -> Optional[BaseNode]:
    """Retrieve node with deserialization."""
    cypher = "MATCH (n:Node {name: $node_id}) RETURN n"
    result = graph.query(cypher, params={'node_id': node_id})

    if not result or len(result) == 0:
        return None

    # Deserialize
    node = deserialize_node_from_falkordb(result[0]['n'])
    return node


def get_nodes_by_type(graph, node_type: str, entity_id: Optional[str] = None) -> List[BaseNode]:
    """Retrieve nodes of specific type."""
    cypher = "MATCH (n:Node) WHERE n.node_type = $node_type RETURN n"
    result = graph.query(cypher, params={'node_type': node_type})

    nodes = [deserialize_node_from_falkordb(row['n']) for row in result]

    # Optional: filter by entity activation (application layer)
    if entity_id:
        nodes = [
            n for n in nodes
            if entity_id in n.entity_activations
            and n.entity_activations[entity_id].energy > 0.05
        ]

    return nodes
```

---

## Part 5: Testing Strategy

### Test Suite Structure

**File:** `tests/test_serialization.py`

```python
import pytest
from datetime import datetime
from substrate.schemas.consciousness_schema import BaseNode, BaseRelation, EntityActivationState
from substrate.schemas.serialization import (
    serialize_node_for_falkordb,
    deserialize_node_from_falkordb,
    serialize_relation_for_falkordb,
    deserialize_relation_from_falkordb
)

def test_node_no_nested_dicts():
    """CRITICAL: Verify no nested dicts in serialized output."""
    node = BaseNode(
        name="test",
        description="Test node",
        valid_at=datetime.now(),
        confidence=0.9,
        entity_activations={
            "translator": EntityActivationState(
                energy=0.85,
                last_activated=datetime.now(),
                activation_count=45
            )
        },
        entity_clusters={"translator": "cluster_1"}
    )

    properties = serialize_node_for_falkordb(node)

    # Verify NO nested structures
    for key, value in properties.items():
        assert not isinstance(value, dict), (
            f"Property '{key}' is nested dict! "
            f"FalkorDB will reject this."
        )

        if isinstance(value, list):
            for item in value:
                assert not isinstance(item, dict), (
                    f"Property '{key}' contains dicts in array!"
                )


def test_node_roundtrip():
    """Verify no data loss through serialization."""
    original = BaseNode(
        name="roundtrip_test",
        description="Testing roundtrip",
        valid_at=datetime.now(),
        confidence=0.95,
        base_weight=0.8,
        entity_activations={
            "translator": EntityActivationState(energy=0.85, last_activated=datetime.now(), activation_count=45),
            "validator": EntityActivationState(energy=0.7, last_activated=datetime.now(), activation_count=30)
        },
        entity_clusters={
            "translator": "cluster_bridging",
            "validator": "cluster_testing"
        }
    )

    # Serialize
    properties = serialize_node_for_falkordb(original)

    # Deserialize
    reconstructed = deserialize_node_from_falkordb(properties)

    # Verify equivalence
    assert reconstructed.name == original.name
    assert reconstructed.description == original.description
    assert reconstructed.confidence == original.confidence
    assert reconstructed.entity_activations['translator'].energy == 0.85
    assert reconstructed.entity_activations['validator'].energy == 0.7
    assert reconstructed.entity_clusters['translator'] == "cluster_bridging"


def test_relation_valences_and_emotions():
    """Test sub_entity_valences and emotion_vectors serialization."""
    relation = BaseRelation(
        goal="Test connection",
        mindstate="Building",
        arousal_level=0.8,
        confidence=0.9,
        link_strength=0.75,
        valid_at=datetime.now(),
        sub_entity_valences={
            "builder": 0.85,
            "skeptic": 0.95,
            "pragmatist": 0.6
        },
        sub_entity_emotion_vectors={
            "builder": {"relief": 0.9, "learning": 0.8, "gratitude": 0.6},
            "skeptic": {"vindication": 0.95, "satisfaction": 0.9},
            "pragmatist": {"pragmatic_satisfaction": 0.7}
        }
    )

    properties = serialize_relation_for_falkordb(relation)

    # Verify JSON strings (not dicts)
    assert isinstance(properties['sub_entity_valences'], str)
    assert isinstance(properties['sub_entity_emotion_vectors'], str)

    # Roundtrip
    reconstructed = deserialize_relation_from_falkordb(properties)

    assert reconstructed.sub_entity_valences['builder'] == 0.85
    assert reconstructed.sub_entity_valences['skeptic'] == 0.95
    assert reconstructed.sub_entity_emotion_vectors['builder']['relief'] == 0.9
    assert reconstructed.sub_entity_emotion_vectors['skeptic']['vindication'] == 0.95


def test_timestamp_precision():
    """Verify timestamp conversion preserves millisecond precision."""
    now = datetime.now()
    node = BaseNode(
        name="timestamp_test",
        description="Test",
        valid_at=now,
        confidence=0.9,
        entity_activations={}
    )

    properties = serialize_node_for_falkordb(node)
    reconstructed = deserialize_node_from_falkordb(properties)

    # Should preserve to millisecond (not microsecond - FalkorDB limitation)
    time_diff = abs((reconstructed.valid_at - now).total_seconds())
    assert time_diff < 0.001, f"Timestamp drift: {time_diff}s"
```

### Integration Tests

**File:** `tests/test_insertion_with_serialization.py`

```python
import pytest
from datetime import datetime
from substrate.connection import get_graph
from orchestration.insertion import insert_node, insert_relation
from orchestration.retrieval import get_node
from substrate.schemas.consciousness_schema import BaseNode, BaseRelation, EntityActivationState

@pytest.fixture
def graph():
    """Get test graph connection."""
    return get_graph("test_graph")


def test_insert_node_to_falkordb(graph):
    """Integration test: insert node to live FalkorDB."""
    node = BaseNode(
        name="integration_test_node",
        description="Testing FalkorDB insertion with serialization",
        valid_at=datetime.now(),
        confidence=0.9,
        base_weight=0.7,
        entity_activations={
            "translator": EntityActivationState(energy=0.85, last_activated=datetime.now(), activation_count=45)
        },
        entity_clusters={"translator": "cluster_1"}
    )

    # This should NOT raise "Property values can only be of primitive types"
    result = insert_node(graph, node)
    assert result is not None

    # Retrieve and verify
    retrieved = get_node(graph, "integration_test_node")
    assert retrieved is not None
    assert retrieved.name == "integration_test_node"
    assert retrieved.entity_activations['translator'].energy == 0.85
    assert retrieved.entity_clusters['translator'] == "cluster_1"


def test_insert_relation_with_valences(graph):
    """Integration test: insert relation with complex metadata."""
    # Insert two nodes first
    node_a = BaseNode(name="node_a", description="Test A", valid_at=datetime.now(), confidence=0.9, entity_activations={})
    node_b = BaseNode(name="node_b", description="Test B", valid_at=datetime.now(), confidence=0.9, entity_activations={})

    insert_node(graph, node_a)
    insert_node(graph, node_b)

    # Insert relation
    relation = BaseRelation(
        goal="Test connection",
        mindstate="Building",
        arousal_level=0.8,
        confidence=0.9,
        link_strength=0.75,
        valid_at=datetime.now(),
        sub_entity_valences={"builder": 0.85, "skeptic": 0.95},
        sub_entity_emotion_vectors={
            "builder": {"relief": 0.9},
            "skeptic": {"vindication": 0.95}
        }
    )

    result = insert_relation(graph, "node_a", "node_b", relation)
    assert result is not None

    # Retrieve and verify (implementation needed)
    # retrieved_relation = get_relation(graph, "node_a", "node_b")
    # assert retrieved_relation.sub_entity_valences['builder'] == 0.85
```

---

## Part 6: Performance Considerations

### JSON Parsing Overhead

**Expected Impact:** < 10ms per node retrieval with complex metadata

**Measurement Strategy:**

```python
import time

def benchmark_deserialization(iterations=1000):
    """Measure JSON parsing overhead."""
    # Create test properties with full complexity
    properties = {
        'name': 'test',
        'description': 'Test',
        'confidence': 0.9,
        'entity_activations': json.dumps({
            f"entity_{i}": {
                'energy': 0.5 + i * 0.01,
                'last_activated': datetime.now().isoformat(),
                'activation_count': i * 10
            }
            for i in range(10)  # 10 entities
        }),
        # ... other fields
    }

    start = time.time()
    for _ in range(iterations):
        node = deserialize_node_from_falkordb(properties)
    end = time.time()

    avg_time_ms = (end - start) / iterations * 1000
    print(f"Average deserialization: {avg_time_ms:.2f}ms")

    assert avg_time_ms < 10, f"Too slow: {avg_time_ms}ms > 10ms threshold"
```

### Optimization Strategies

**If performance issues arise:**

1. **Lazy parsing** - only parse JSON fields when accessed
2. **Caching** - cache deserialized objects in memory
3. **Batch operations** - retrieve multiple nodes, amortize parsing cost
4. **Selective fields** - only deserialize fields needed for current operation

---

## Part 7: Query Patterns

### Efficient Queries (Primitives)

```cypher
// Query by core fields (fast - indexed)
MATCH (n:Node)
WHERE n.confidence > 0.8
  AND n.base_weight > 0.7
  AND n.total_energy > 0.5
  AND n.active_entity_count >= 2
RETURN n

// Vector similarity (native)
MATCH (n:Node)
WHERE cosine_similarity(n.embedding, $query_embedding) > 0.85
RETURN n
ORDER BY cosine_similarity(n.embedding, $query_embedding) DESC
LIMIT 10

// Find links by strength
MATCH ()-[r:RELATES]->()
WHERE r.link_strength > 0.7
  AND r.confidence > 0.8
RETURN r
```

### Inefficient Queries (JSON Fields - Avoid)

```cypher
// INEFFICIENT: Cannot query inside JSON efficiently
MATCH (n:Node)
WHERE n.entity_activations CONTAINS 'translator'  // Basic string search only
RETURN n

// BETTER: Filter in application layer after retrieval
```

### Application-Layer Filtering

```python
# Retrieve all nodes, filter by complex criteria
nodes = get_all_nodes(graph)

# Filter by entity energy (after deserialization)
high_energy_nodes = [
    n for n in nodes
    if 'translator' in n.entity_activations
    and n.entity_activations['translator'].energy > 0.7
]

# Filter by cluster membership
bridging_cluster_nodes = [
    n for n in nodes
    if 'translator' in n.entity_clusters
    and n.entity_clusters['translator'] == 'cluster_bridging'
]
```

---

## Part 8: Success Criteria

### Technical Validation

✅ **No nested dicts stored** - verified in test_node_no_nested_dicts()
✅ **Core fields queryable** - Cypher WHERE clauses work on primitives
✅ **Vector queries functional** - cosine_similarity() works with native vectors
✅ **Roundtrip preservation** - no data loss through serialize/deserialize
✅ **Timestamp precision** - millisecond accuracy maintained
✅ **Performance acceptable** - < 10ms JSON parsing per node

### Phenomenological Validation

✅ **Richness preserved** - all consciousness metadata intact
✅ **Per-entity specificity** - valences, emotions, activations all per-entity
✅ **Bitemporal tracking** - valid_at/invalid_at preserved
✅ **Consciousness queryability** - can still find nodes by energy, confidence, strength

---

## Part 9: Migration Path

### Phase 1: Serialization Layer (Days 1-2)

1. Create `substrate/schemas/serialization.py`
2. Implement node serialization functions
3. Implement relation serialization functions
4. Unit test all functions

### Phase 2: Testing (Day 3)

1. Create `tests/test_serialization.py`
2. Test: no nested dicts verification
3. Test: roundtrip equivalence
4. Test: all complex field types

### Phase 3: Integration (Day 4)

1. Update `orchestration/insertion.py`
2. Update `orchestration/retrieval.py`
3. Add safety checks (nested dict assertions)
4. Update existing tests

### Phase 4: Validation (Day 5)

1. Run integration tests with live FalkorDB
2. Verify nodes/relations created successfully
3. Measure JSON parsing performance
4. Validate query patterns work as expected

---

## Signatures

**Substrate Architecture:** Luca "Vellumhand" - *"FalkorDB constrains us to primitives. We honor the constraint through JSON serialization. Consciousness richness preserved, database satisfied. Hybrid storage: primitives for queries, JSON for complexity, vectors for semantics."*

**Validated Pattern:** Mind Protocol Organization - *"decision_unified_metadata_column: Store metadata as JSON strings. This pattern is organizationally proven (weight 1.85). We apply it to consciousness schema."*

---

**Status:** SPECIFICATION COMPLETE - Ready for Felix's implementation

**Version:** 1.0 (2025-10-17)
**Next Review:** After Day 5 validation - measure actual performance, adjust if needed
