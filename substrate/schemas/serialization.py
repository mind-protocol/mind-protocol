"""
Serialization layer for consciousness schema → FalkorDB storage.

FalkorDB Constraint: Property values must be primitive types or arrays of primitives.
Solution: Hybrid storage pattern (validated organizational decision weight 1.85)

Field Categories:
1. Primitives: Direct storage (name, description, confidence, timestamps)
2. Complex metadata: JSON-serialized strings (entity_activations, sub_entity_valences)
3. Vectors: Native FalkorDB Vec type (embeddings)
4. Arrays: Primitive arrays (participants, members, goals)

Author: Felix "Ironhand"
Date: 2025-10-17
Status: Implementing validated organizational pattern
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel

# Import what exists in consciousness_schema
try:
    from substrate.schemas.consciousness_schema import BaseNode, BaseRelation
except ImportError:
    # Fallback for testing - define minimal types
    class BaseNode(BaseModel):
        name: str
        description: str
        valid_at: datetime
        confidence: float
        formation_trigger: str

    class BaseRelation(BaseModel):
        goal: str
        mindstate: str
        energy: float
        confidence: float
        formation_trigger: str
        valid_at: datetime


def serialize_node_for_falkordb(node: BaseNode) -> Dict[str, Any]:
    """
    Convert Pydantic BaseNode to FalkorDB-compatible property dict.

    Transformations:
    - Primitives → direct storage
    - Complex dicts → JSON strings
    - datetime → int milliseconds (timestamp)
    - Lists → primitive arrays (if simple) or JSON (if nested)

    Returns:
        Dict with only primitive-type values (no nested dicts/objects)
    """
    properties = {}

    # Category 1: Core Idsubentity Primitives (directly queryable)
    properties['name'] = node.name
    properties['description'] = node.description
    properties['confidence'] = node.confidence
    properties['formation_trigger'] = node.formation_trigger

    # Timestamps: datetime → int milliseconds since epoch
    properties['valid_at'] = int(node.valid_at.timestamp() * 1000)
    if node.invalid_at:
        properties['invalid_at'] = int(node.invalid_at.timestamp() * 1000)
    if node.expired_at:
        properties['expired_at'] = int(node.expired_at.timestamp() * 1000)

    # Weight properties (for traversal queries)
    if hasattr(node, 'base_weight'):
        properties['base_weight'] = node.base_weight
    if hasattr(node, 'reinforcement_weight'):
        properties['reinforcement_weight'] = node.reinforcement_weight
    if hasattr(node, 'decay_rate'):
        properties['decay_rate'] = node.decay_rate

    # Category 2: Complex Consciousness Metadata → JSON strings

    # entity_activations: Dict → JSON (handles both dict and object types)
    if hasattr(node, 'entity_activations') and node.entity_activations:
        entity_activations_data = {}
        for entity_id, state in node.entity_activations.items():
            if isinstance(state, dict):
                # Already a dict
                entity_activations_data[entity_id] = state
            else:
                # Object with attributes
                entity_activations_data[entity_id] = {
                    'energy': getattr(state, 'energy', 0.0),
                    'last_activated': getattr(state, 'last_activated', datetime.now()).isoformat() if hasattr(state, 'last_activated') else None,
                    'activation_count': getattr(state, 'activation_count', 0),
                }
        properties['entity_activations'] = json.dumps(entity_activations_data)
    else:
        properties['entity_activations'] = '{}'

    # entity_clusters: Dict[str, str] → JSON
    if hasattr(node, 'entity_clusters') and node.entity_clusters:
        properties['entity_clusters'] = json.dumps(node.entity_clusters)
    else:
        properties['entity_clusters'] = '{}'

    # sub_entity_last_sequence_positions: Dict[str, int] → JSON
    if hasattr(node, 'sub_entity_last_sequence_positions') and node.sub_entity_last_sequence_positions:
        properties['sub_entity_last_sequence_positions'] = json.dumps(node.sub_entity_last_sequence_positions)
    else:
        properties['sub_entity_last_sequence_positions'] = '{}'

    # Category 3: Vector Embeddings (native FalkorDB support)
    if hasattr(node, 'embedding') and node.embedding:
        properties['embedding'] = node.embedding  # Native Vec type

    # Category 4: Simple Arrays (primitive arrays)
    # Type-specific fields that may be arrays
    if hasattr(node, 'participants') and node.participants:
        properties['participants'] = node.participants  # List[str]
    if hasattr(node, 'members') and node.members:
        properties['members'] = node.members  # List[str]
    if hasattr(node, 'goals') and node.goals:
        properties['goals'] = node.goals  # List[str]
    if hasattr(node, 'steps') and node.steps:
        properties['steps'] = node.steps  # List[str]

    # Observability fields (primitives)
    if hasattr(node, 'last_modified'):
        properties['last_modified'] = int(node.last_modified.timestamp() * 1000) if node.last_modified else None
    if hasattr(node, 'traversal_count'):
        properties['traversal_count'] = node.traversal_count
    if hasattr(node, 'last_traversed_by'):
        properties['last_traversed_by'] = node.last_traversed_by
    if hasattr(node, 'last_traversal_time'):
        properties['last_traversal_time'] = int(node.last_traversal_time.timestamp() * 1000) if node.last_traversal_time else None

    return properties


def serialize_dict_fields(obj: Any) -> Dict[str, Any]:
    """
    Generic serializer: Convert ANY object to FalkorDB-compatible dict.

    Handles:
    - Pydantic models → dict with model_dump()
    - Complex nested dicts → JSON strings
    - datetime → int timestamps
    - Lists of primitives → preserve
    - Lists of objects → JSON strings

    This is the KEY function for FalkorDB compatibility.

    Returns:
        Dict with ONLY primitive-type values
    """
    if isinstance(obj, BaseModel):
        data = obj.model_dump()
    elif isinstance(obj, dict):
        data = obj
    else:
        raise ValueError(f"Cannot serialize type {type(obj)}")

    result = {}

    for key, value in data.items():
        if value is None:
            result[key] = None
        elif isinstance(value, (str, int, float, bool)):
            # Primitive - store directly
            result[key] = value
        elif isinstance(value, datetime):
            # datetime → int timestamp
            result[key] = int(value.timestamp() * 1000)
        elif isinstance(value, dict):
            # Dict → JSON string
            result[key] = json.dumps(value)
        elif isinstance(value, list):
            # Check if list contains primitives or objects
            if not value:
                result[key] = []
            elif isinstance(value[0], (str, int, float, bool)):
                # List of primitives - OK
                result[key] = value
            else:
                # List of objects → JSON string
                result[key] = json.dumps(value)
        else:
            # Unknown type → JSON string (safe fallback)
            result[key] = json.dumps(str(value))

    return result


def deserialize_node_from_falkordb(properties: Dict[str, Any], node_type: str) -> Dict[str, Any]:
    """
    Convert FalkorDB properties back to dict suitable for Pydantic instantiation.

    Transformations:
    - JSON strings → parse to dicts
    - int timestamps → datetime
    - Vec → List[float]

    Args:
        properties: Raw FalkorDB node properties
        node_type: Node type for proper Pydantic model instantiation

    Returns:
        Dict suitable for BaseNode(**result)
    """
    result = {}

    for key, value in properties.items():
        if value is None:
            result[key] = None
        elif isinstance(value, str) and ('{' in value or '[' in value):
            # Likely JSON - try to parse
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                # Not JSON - keep as string
                result[key] = value
        elif key.endswith('_at') or key.endswith('_time') or key.endswith('_modified'):
            # Timestamp field - convert to datetime
            try:
                result[key] = datetime.fromtimestamp(value / 1000)
            except (ValueError, TypeError):
                result[key] = value
        else:
            # Pass through
            result[key] = value

    return result


def deserialize_node_from_falkordb_legacy(properties: Dict[str, Any], node_type: str) -> BaseNode:
    """
    Legacy: Convert FalkorDB properties back to Pydantic BaseNode object.
    Use deserialize_node_from_falkordb() instead for dict output.

    Args:
        properties: Raw FalkorDB node properties
        node_type: Node type for proper Pydantic model instantiation

    Returns:
        Validated BaseNode instance
    """
    # Parse JSON fields
    entity_activations = {}
    if 'entity_activations' in properties and properties['entity_activations']:
        entity_activations_dict = json.loads(properties['entity_activations'])
        # Keep as dict (no EntityActivationState needed)
        entity_activations = entity_activations_dict

    entity_clusters = json.loads(properties.get('entity_clusters', '{}'))
    sub_entity_last_sequence_positions = json.loads(properties.get('sub_entity_last_sequence_positions', '{}'))

    # Parse timestamps
    valid_at = datetime.fromtimestamp(properties['valid_at'] / 1000)
    invalid_at = None
    if properties.get('invalid_at'):
        invalid_at = datetime.fromtimestamp(properties['invalid_at'] / 1000)
    expired_at = None
    if properties.get('expired_at'):
        expired_at = datetime.fromtimestamp(properties['expired_at'] / 1000)

    last_modified = None
    if properties.get('last_modified'):
        last_modified = datetime.fromtimestamp(properties['last_modified'] / 1000)

    last_traversal_time = None
    if properties.get('last_traversal_time'):
        last_traversal_time = datetime.fromtimestamp(properties['last_traversal_time'] / 1000)

    # Construct BaseNode
    node_data = {
        'name': properties['name'],
        'description': properties['description'],
        'valid_at': valid_at,
        'invalid_at': invalid_at,
        'expired_at': expired_at,
        'confidence': properties['confidence'],
        'formation_trigger': properties['formation_trigger'],
        'entity_activations': entity_activations,
        'entity_clusters': entity_clusters,
        'sub_entity_last_sequence_positions': sub_entity_last_sequence_positions,
    }

    # Optional fields
    if 'base_weight' in properties:
        node_data['base_weight'] = properties['base_weight']
    if 'reinforcement_weight' in properties:
        node_data['reinforcement_weight'] = properties['reinforcement_weight']
    if 'decay_rate' in properties:
        node_data['decay_rate'] = properties['decay_rate']
    if 'embedding' in properties:
        node_data['embedding'] = properties['embedding']
    if 'participants' in properties:
        node_data['participants'] = properties['participants']
    if 'members' in properties:
        node_data['members'] = properties['members']
    if 'goals' in properties:
        node_data['goals'] = properties['goals']
    if 'steps' in properties:
        node_data['steps'] = properties['steps']
    if 'last_modified' in properties:
        node_data['last_modified'] = last_modified
    if 'traversal_count' in properties:
        node_data['traversal_count'] = properties['traversal_count']
    if 'last_traversed_by' in properties:
        node_data['last_traversed_by'] = properties['last_traversed_by']
    if 'last_traversal_time' in properties:
        node_data['last_traversal_time'] = last_traversal_time

    return BaseNode(**node_data)


def serialize_relation_for_falkordb(relation: BaseRelation) -> Dict[str, Any]:
    """
    Convert Pydantic BaseRelation to FalkorDB-compatible property dict.

    Transformations:
    - Primitives → direct storage
    - Complex consciousness metadata → JSON strings
    - datetime → int milliseconds

    Returns:
        Dict with only primitive-type values
    """
    properties = {}

    # Category 1: Core Primitives (directly queryable)
    properties['goal'] = relation.goal
    properties['mindstate'] = relation.mindstate
    properties['energy'] = relation.energy
    properties['confidence'] = relation.confidence
    properties['formation_trigger'] = relation.formation_trigger

    # Link strength (critical for traversal queries)
    if hasattr(relation, 'link_strength'):
        properties['link_strength'] = relation.link_strength

    # Timestamps
    properties['valid_at'] = int(relation.valid_at.timestamp() * 1000)
    if relation.invalid_at:
        properties['invalid_at'] = int(relation.invalid_at.timestamp() * 1000)

    # Category 2: Complex Consciousness Metadata → JSON strings

    # sub_entity_valences: Dict[str, float] → JSON
    if hasattr(relation, 'sub_entity_valences') and relation.sub_entity_valences:
        properties['sub_entity_valences'] = json.dumps(relation.sub_entity_valences)
    else:
        properties['sub_entity_valences'] = '{}'

    # sub_entity_emotion_vectors: Dict[str, Dict[str, float]] → JSON
    if hasattr(relation, 'sub_entity_emotion_vectors') and relation.sub_entity_emotion_vectors:
        properties['sub_entity_emotion_vectors'] = json.dumps(relation.sub_entity_emotion_vectors)
    else:
        properties['sub_entity_emotion_vectors'] = '{}'

    # entity_coactivation_counts: Dict[str, int] → JSON
    if hasattr(relation, 'entity_coactivation_counts') and relation.entity_coactivation_counts:
        properties['entity_coactivation_counts'] = json.dumps(relation.entity_coactivation_counts)
    else:
        properties['entity_coactivation_counts'] = '{}'

    # entity_link_strengths: Dict[str, float] → JSON
    if hasattr(relation, 'entity_link_strengths') and relation.entity_link_strengths:
        properties['entity_link_strengths'] = json.dumps(relation.entity_link_strengths)
    else:
        properties['entity_link_strengths'] = '{}'

    # Category 3: Vector Embeddings
    if hasattr(relation, 'embedding') and relation.embedding:
        properties['embedding'] = relation.embedding

    # Observability fields
    if hasattr(relation, 'last_modified'):
        properties['last_modified'] = int(relation.last_modified.timestamp() * 1000) if relation.last_modified else None
    if hasattr(relation, 'traversal_count'):
        properties['traversal_count'] = relation.traversal_count
    if hasattr(relation, 'last_traversed_by'):
        properties['last_traversed_by'] = relation.last_traversed_by
    if hasattr(relation, 'last_mechanism_id'):
        properties['last_mechanism_id'] = relation.last_mechanism_id

    return properties


def deserialize_relation_from_falkordb(properties: Dict[str, Any], relation_type: str) -> BaseRelation:
    """
    Convert FalkorDB properties back to Pydantic BaseRelation.

    Args:
        properties: Raw FalkorDB relation properties
        relation_type: Relation type for proper Pydantic model instantiation

    Returns:
        Validated BaseRelation instance
    """
    # Parse JSON fields
    sub_entity_valences = json.loads(properties.get('sub_entity_valences', '{}'))
    sub_entity_emotion_vectors = json.loads(properties.get('sub_entity_emotion_vectors', '{}'))
    entity_coactivation_counts = json.loads(properties.get('entity_coactivation_counts', '{}'))
    entity_link_strengths = json.loads(properties.get('entity_link_strengths', '{}'))

    # Parse timestamps
    valid_at = datetime.fromtimestamp(properties['valid_at'] / 1000)
    invalid_at = None
    if properties.get('invalid_at'):
        invalid_at = datetime.fromtimestamp(properties['invalid_at'] / 1000)

    last_modified = None
    if properties.get('last_modified'):
        last_modified = datetime.fromtimestamp(properties['last_modified'] / 1000)

    # Construct BaseRelation
    relation_data = {
        'goal': properties['goal'],
        'mindstate': properties['mindstate'],
        'energy': properties['energy'],
        'confidence': properties['confidence'],
        'formation_trigger': properties['formation_trigger'],
        'valid_at': valid_at,
        'invalid_at': invalid_at,
        'sub_entity_valences': sub_entity_valences,
        'sub_entity_emotion_vectors': sub_entity_emotion_vectors,
        'entity_coactivation_counts': entity_coactivation_counts,
        'entity_link_strengths': entity_link_strengths,
    }

    # Optional fields
    if 'link_strength' in properties:
        relation_data['link_strength'] = properties['link_strength']
    if 'embedding' in properties:
        relation_data['embedding'] = properties['embedding']
    if 'last_modified' in properties:
        relation_data['last_modified'] = last_modified
    if 'traversal_count' in properties:
        relation_data['traversal_count'] = properties['traversal_count']
    if 'last_traversed_by' in properties:
        relation_data['last_traversed_by'] = properties['last_traversed_by']
    if 'last_mechanism_id' in properties:
        relation_data['last_mechanism_id'] = properties['last_mechanism_id']

    return BaseRelation(**relation_data)


def verify_no_nested_dicts(properties: Dict[str, Any]) -> bool:
    """
    Verify that properties dict contains no nested dicts/objects.

    FalkorDB constraint: All property values must be primitives or arrays of primitives.

    Returns:
        True if valid (no nested structures), False if nested dicts found
    """
    for key, value in properties.items():
        if isinstance(value, dict):
            return False
        if isinstance(value, list):
            # Check if list contains dicts (not allowed)
            if any(isinstance(item, dict) for item in value):
                return False
    return True


# Validation test (runs on import in dev mode)
if __name__ == "__main__":
    print("Testing serialization layer...")

    # Test 1: Generic serializer with nested dict
    test_data = {
        "name": "test_decision",
        "description": "Test node",
        "confidence": 0.95,
        "valid_at": datetime.now(),
        "entity_activations": {
            "translator": {"energy": 0.85, "count": 45},
            "validator": {"energy": 0.65, "count": 32}
        },
        "entity_clusters": {
            "translator": "cluster_1",
            "validator": "cluster_2"
        },
        "simple_list": ["a", "b", "c"],
    }

    # Serialize with generic function
    serialized = serialize_dict_fields(test_data)

    # Verify no nested dicts
    assert verify_no_nested_dicts(serialized), "FAIL: Found nested dicts in serialized properties!"
    print("  [OK] No nested dicts in serialized data")

    # Verify complex fields are JSON strings
    assert isinstance(serialized['entity_activations'], str), "FAIL: entity_activations not JSON string"
    assert isinstance(serialized['entity_clusters'], str), "FAIL: entity_clusters not JSON string"
    print("  [OK] Complex fields JSON-serialized")

    # Verify simple list preserved
    assert isinstance(serialized['simple_list'], list), "FAIL: simple_list not preserved as list"
    assert serialized['simple_list'] == ["a", "b", "c"], "FAIL: simple_list values changed"
    print("  [OK] Simple arrays preserved")

    # Verify datetime converted to int
    assert isinstance(serialized['valid_at'], int), "FAIL: datetime not converted to int"
    print("  [OK] Datetimes converted to timestamps")

    # Test 2: Round-trip deserialization
    deserialized = deserialize_node_from_falkordb(serialized, "Decision")

    assert deserialized['name'] == test_data['name']
    assert deserialized['confidence'] == test_data['confidence']
    assert isinstance(deserialized['entity_activations'], dict), "FAIL: entity_activations not parsed back to dict"
    assert deserialized['entity_activations']['translator']['energy'] == 0.85
    assert isinstance(deserialized['valid_at'], datetime), "FAIL: timestamp not converted back to datetime"
    print("  [OK] Round-trip preserves data")

    print("\n[SUCCESS] ALL SERIALIZATION TESTS PASSED")
    print("Ready for FalkorDB integration")
