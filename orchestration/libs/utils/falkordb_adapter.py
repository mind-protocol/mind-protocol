"""
FalkorDB Adapter - Serialization/Deserialization for consciousness structures.

Handles conversion between:
- Python Node/Link objects ↔ FalkorDB properties
- Single-energy scalar ↔ float (V2 architecture)
- Datetime ↔ milliseconds timestamp
- Enums ↔ string values

FalkorDB Limitations:
- No native datetime type → use milliseconds (int)
- No native dict type → use JSON string
- Properties must be primitives (int, float, string, bool)

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-23 - Fixed V1→V2 migration (energy dict → E scalar)
Architecture: V2 Single-Energy (foundations/diffusion.md)
"""

import json
import logging
import re
import redis
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from falkordb import FalkorDB

from orchestration.core.node import Node
from orchestration.core.link import Link
from orchestration.core.types import NodeType, LinkType
from orchestration.libs.write_gate import namespace_for_graph, write_gate

logger = logging.getLogger(__name__)


def safe_float(value, default=0.0, property_name="unknown"):
    """
    Safely convert value to float with defensive parsing.
    
    Handles corrupted data like "0.85 Rich, specific value" by extracting numeric prefix.
    
    Args:
        value: Value to convert (any type)
        default: Default value if conversion fails (default: 0.0)
        property_name: Name of property for logging (default: "unknown")
    
    Returns:
        float value or default
    
    Examples:
        >>> safe_float(0.85)
        0.85
        >>> safe_float("0.85")
        0.85
        >>> safe_float("0.85 Rich, specific value")
        0.85
        >>> safe_float("invalid", default=0.5)
        0.5
    """
    try:
        # Try direct conversion first (fast path for clean data)
        return float(value)
    except (ValueError, TypeError):
        # Defensive parsing: extract numeric prefix
        if isinstance(value, str):
            # Try to extract numeric part from beginning of string
            match = re.match(r"^([+-]?\d+\.?\d*)", value.strip())
            if match:
                try:
                    numeric_str = match.group(1)
                    result = float(numeric_str)
                    logger.warning(
                        f"[FalkorDB] Extracted numeric prefix from corrupted {property_name}: "
                        f"'{value}' -> {result}"
                    )
                    return result
                except ValueError:
                    pass
        
        # Fallback to default
        logger.warning(
            f"[FalkorDB] Could not convert {property_name} to float: '{value}', using default {default}"
        )
        return default



# --- Node Serialization ---

def serialize_node(node: Node) -> Dict[str, Any]:
    """
    Convert Node to FalkorDB property dict.

    Conversions:
    - Single-energy E → float (V2)
    - timestamps → milliseconds (int)
    - NodeType enum → string value
    - properties dict → JSON string

    Args:
        node: Node to serialize

    Returns:
        Dict of FalkorDB-compatible properties

    Example:
        >>> node = Node(id="n1", name="Test", E=0.5, ...)
        >>> props = serialize_node(node)
        >>> props['id']
        'n1'
        >>> props['E']  # float
        0.5
    """
    return {
        # Idsubentity
        'id': node.id,
        'name': node.name,
        'node_type': node.node_type.value,  # Enum → string
        'description': node.description,

        # V2 Single-Energy (scalar float, not dict)
        'E': node.E,
        'theta': node.theta,

        # Version tracking (V2 Bitemporal)
        'vid': node.vid,
        'supersedes': node.supersedes,
        'superseded_by': node.superseded_by,

        # Bitemporal - Reality timeline (datetime → milliseconds)
        'valid_at': _datetime_to_millis(node.valid_at),
        'invalidated_at': _datetime_to_millis(node.invalidated_at) if node.invalidated_at else None,

        # Bitemporal - Knowledge timeline
        'created_at': _datetime_to_millis(node.created_at),
        'expired_at': _datetime_to_millis(node.expired_at) if node.expired_at else None,

        # Learning infrastructure
        'log_weight': node.log_weight,
        'log_weight_overlays': json.dumps(node.log_weight_overlays),  # Dict[str, float] → JSON
        'ema_trace_seats': node.ema_trace_seats,
        'ema_wm_presence': node.ema_wm_presence,
        'ema_formation_quality': node.ema_formation_quality,
        'scope': node.scope,

        # SubEntity activation tracking (for frontend viz)
        'entity_activations': json.dumps(node.entity_activations),  # Dict[str, Dict[str, float]] → JSON

        # Properties (Dict → JSON string)
        'properties': json.dumps(node.properties),
    }


def deserialize_node(props: Dict[str, Any]) -> Node:
    """
    Convert FalkorDB properties to Node object.

    Conversions:
    - float → single-energy E (V2)
    - milliseconds (int) → timestamps
    - string value → NodeType enum
    - JSON string → properties dict

    Args:
        props: FalkorDB property dict

    Returns:
        Node object

    Example:
        >>> props = {'id': 'n1', 'name': 'Test', 'E': 0.5, ...}
        >>> node = deserialize_node(props)
        >>> node.id
        'n1'
        >>> node.E
        0.5
    """
    return Node(
        # Idsubentity
        id=props['id'],
        name=props['name'],
        node_type=NodeType(props['node_type']),  # String → enum
        description=props['description'],

        # V2 Single-Energy (scalar float, not dict)
        E=props.get('E', 0.0),
        theta=props.get('theta', 0.1),

        # Version tracking (V2 Bitemporal)
        vid=props.get('vid', f"v_{props['id'][:12]}"),  # Fallback for old nodes
        supersedes=props.get('supersedes'),
        superseded_by=props.get('superseded_by'),

        # Bitemporal - Reality timeline (milliseconds → datetime)
        valid_at=_millis_to_datetime(props['valid_at']),
        invalidated_at=_millis_to_datetime(props['invalidated_at']) if props.get('invalidated_at') else None,

        # Bitemporal - Knowledge timeline
        created_at=_millis_to_datetime(props['created_at']),
        expired_at=_millis_to_datetime(props['expired_at']) if props.get('expired_at') else None,

        # Learning infrastructure
        log_weight=props.get('log_weight', 0.0),
        log_weight_overlays=json.loads(props.get('log_weight_overlays', '{}')),  # JSON → Dict[str, float]
        ema_trace_seats=props.get('ema_trace_seats', 0.0),
        ema_wm_presence=props.get('ema_wm_presence', 0.0),
        ema_formation_quality=props.get('ema_formation_quality', 0.0),
        scope=props.get('scope', 'personal'),

        # SubEntity activation tracking (for frontend viz)
        entity_activations=json.loads(props.get('entity_activations', '{}')),  # JSON → Dict[str, Dict[str, float]]

        # Properties (JSON string → Dict)
        properties=json.loads(props.get('properties', '{}')),

        # Graph structure (will be populated by Graph.add_link)
        outgoing_links=[],
        incoming_links=[],
    )


# --- Link Serialization ---

def serialize_link(link: Link) -> Dict[str, Any]:
    """
    Convert Link to FalkorDB property dict.

    Conversions:
    - LinkType enum → string value
    - timestamps → milliseconds (int)
    - properties dict → JSON string

    Args:
        link: Link to serialize

    Returns:
        Dict of FalkorDB-compatible properties

    Example:
        >>> link = Link(id="l1", source_id="s", target_id="t", ...)
        >>> props = serialize_link(link)
        >>> props['link_type']
        'ENABLES'
    """
    # Build property dict, filtering out None values for FalkorDB compatibility
    props = {
        # Idsubentity
        'id': link.id,
        'source_id': link.source_id,
        'target_id': link.target_id,
        'link_type': link.link_type.value,  # Enum → string

        # Link metadata
        'subentity': link.subentity,
        'weight': link.weight,
        'energy': link.energy,

        # Bitemporal - Reality timeline
        'valid_at': _datetime_to_millis(link.valid_at),
        'invalidated_at': _datetime_to_millis(link.invalidated_at) if link.invalidated_at else None,

        # Bitemporal - Knowledge timeline
        'created_at': _datetime_to_millis(link.created_at),
        'expired_at': _datetime_to_millis(link.expired_at) if link.expired_at else None,

        # Consciousness metadata
        'goal': link.goal,
        'mindstate': link.mindstate,
        'formation_trigger': link.formation_trigger,
        'confidence': link.confidence,

        # Learning infrastructure
        'log_weight': link.log_weight,
        'log_weight_overlays': json.dumps(link.log_weight_overlays),  # Dict[str, float] → JSON
        'ema_trace_seats': link.ema_trace_seats,
        'ema_phi': link.ema_phi,
        'ema_formation_quality': link.ema_formation_quality,

        # Properties (Dict → JSON string)
        'properties': json.dumps(link.properties),
    }

    # Filter out None values - FalkorDB doesn't accept None in properties
    return {k: v for k, v in props.items() if v is not None}


def deserialize_link(props: Dict[str, Any]) -> Link:
    """
    Convert FalkorDB properties to Link object.

    Conversions:
    - string value → LinkType enum
    - milliseconds (int) → timestamps
    - JSON string → properties dict

    Args:
        props: FalkorDB property dict

    Returns:
        Link object

    Example:
        >>> props = {'id': 'l1', 'link_type': 'ENABLES', ...}
        >>> link = deserialize_link(props)
        >>> link.link_type
        <LinkType.ENABLES>
    """
    return Link(
        # Idsubentity
        id=props['id'],
        source_id=props['source_id'],
        target_id=props['target_id'],
        link_type=LinkType(props['link_type']),  # String → enum

        # Link metadata
        subentity=props['subentity'],
        weight=props.get('weight', 1.0),
        energy=props.get('energy', 0.0),

        # Bitemporal - Reality timeline
        valid_at=_millis_to_datetime(props['valid_at']),
        invalidated_at=_millis_to_datetime(props['invalidated_at']) if props.get('invalidated_at') else None,

        # Bitemporal - Knowledge timeline
        created_at=_millis_to_datetime(props['created_at']),
        expired_at=_millis_to_datetime(props['expired_at']) if props.get('expired_at') else None,

        # Consciousness metadata
        goal=props.get('goal'),
        mindstate=props.get('mindstate'),
        formation_trigger=props.get('formation_trigger'),
        confidence=props.get('confidence', 1.0),

        # Learning infrastructure
        log_weight=props.get('log_weight', 0.0),
        log_weight_overlays=json.loads(props.get('log_weight_overlays', '{}')),  # JSON → Dict[str, float]
        ema_trace_seats=props.get('ema_trace_seats', 0.0),
        ema_phi=props.get('ema_phi', 0.0),
        ema_formation_quality=props.get('ema_formation_quality', 0.0),

        # Properties (JSON string → Dict)
        properties=json.loads(props.get('properties', '{}')),

        # References (will be populated by Graph.add_link)
        source=None,
        target=None,
    )


# --- Subentity Serialization ---

def serialize_entity(entity: 'Subentity') -> Dict[str, Any]:
    """
    Convert Subentity to FalkorDB property dict.

    Conversions:
    - np.ndarray → base64 string
    - List/Dict → JSON string
    - timestamps → milliseconds (int)
    - Runtime state → NOT persisted (computed on load)

    Args:
        entity: Subentity to serialize

    Returns:
        Dict of FalkorDB-compatible properties
    """
    import base64
    import numpy as np

    # Serialize centroid_embedding (np.ndarray → base64 string)
    centroid_str = None
    if entity.centroid_embedding is not None:
        centroid_bytes = entity.centroid_embedding.tobytes()
        centroid_str = base64.b64encode(centroid_bytes).decode('utf-8')

    # Serialize prev_affect_for_coherence (Optional[np.ndarray] → base64 string or None)
    prev_affect_str = None
    if entity.prev_affect_for_coherence is not None:
        affect_bytes = entity.prev_affect_for_coherence.tobytes()
        prev_affect_str = base64.b64encode(affect_bytes).decode('utf-8')

    # Build property dict, filtering out None values for FalkorDB compatibility
    props = {
        # Identity
        'id': entity.id,
        'entity_kind': entity.entity_kind,
        'role_or_topic': entity.role_or_topic,
        'description': entity.description,

        # Semantic representation (np.ndarray → base64 string)
        'centroid_embedding': centroid_str,
        'centroid_dims': entity.centroid_embedding.shape[0] if entity.centroid_embedding is not None else 0,

        # NOTE: Runtime state (energy_runtime, threshold_runtime, activation_level_runtime)
        # is NOT persisted - it's computed from members on load

        # Structural quality
        'coherence_ema': entity.coherence_ema,
        'member_count': entity.member_count,

        # Learning infrastructure
        'ema_active': entity.ema_active,
        'log_weight': entity.log_weight,
        'ema_wm_presence': entity.ema_wm_presence,
        'ema_trace_seats': entity.ema_trace_seats,
        'ema_formation_quality': entity.ema_formation_quality,

        # Lifecycle state
        'stability_state': entity.stability_state,
        'quality_score': entity.quality_score,
        'last_quality_update': _datetime_to_millis(entity.last_quality_update) if entity.last_quality_update else None,

        # Quality tracking
        'frames_since_creation': entity.frames_since_creation,
        'high_quality_streak': entity.high_quality_streak,
        'low_quality_streak': entity.low_quality_streak,

        # Identity multiplicity metrics
        'task_progress_rate': entity.task_progress_rate,
        'energy_efficiency': entity.energy_efficiency,
        'identity_flip_count': entity.identity_flip_count,

        # Coherence persistence tracking
        'coherence_persistence': entity.coherence_persistence,
        'prev_affect_for_coherence': prev_affect_str,

        # Multi-pattern response (List/Dict → JSON)
        'pattern_weights': json.dumps(entity.pattern_weights),
        'rumination_frames_consecutive': entity.rumination_frames_consecutive,
        'pattern_effectiveness': json.dumps(entity.pattern_effectiveness),

        # Provenance
        'created_from': entity.created_from,
        'created_by': entity.created_by,
        'substrate': entity.substrate,
        'scope': entity.scope,

        # Bitemporal tracking (datetime → milliseconds)
        'valid_at': _datetime_to_millis(entity.valid_at),
        'invalidated_at': _datetime_to_millis(entity.invalidated_at) if entity.invalidated_at else None,
        'created_at': _datetime_to_millis(entity.created_at),
        'expired_at': _datetime_to_millis(entity.expired_at) if entity.expired_at else None,

        # Consciousness metadata
        'confidence': entity.confidence,
        'formation_trigger': entity.formation_trigger,

        # Last update timestamp
        'last_update_timestamp': _datetime_to_millis(entity.last_update_timestamp) if entity.last_update_timestamp else None,

        # Properties (Dict → JSON string)
        'properties': json.dumps(entity.properties),
    }

    # Filter out None values - FalkorDB doesn't accept None in properties
    return {k: v for k, v in props.items() if v is not None}


def deserialize_entity(props: Dict[str, Any]) -> 'Subentity':
    """
    Convert FalkorDB properties to Subentity object.

    Conversions:
    - base64 string → np.ndarray
    - JSON string → List/Dict
    - milliseconds (int) → timestamps
    - Runtime state → initialized to defaults (recomputed on first frame)

    Args:
        props: FalkorDB property dict

    Returns:
        Subentity object
    """
    import base64
    import numpy as np
    from orchestration.core.subentity import Subentity

    # Deserialize centroid_embedding (base64 string → np.ndarray)
    centroid = None
    if props.get('centroid_embedding'):
        centroid_bytes = base64.b64decode(props['centroid_embedding'])
        dims = props.get('centroid_dims', 768)
        centroid = np.frombuffer(centroid_bytes, dtype=np.float64).reshape(dims)

    # Deserialize prev_affect_for_coherence (base64 string → np.ndarray or None)
    prev_affect = None
    if props.get('prev_affect_for_coherence'):
        affect_bytes = base64.b64decode(props['prev_affect_for_coherence'])
        dims = props.get('centroid_dims', 768)
        prev_affect = np.frombuffer(affect_bytes, dtype=np.float64).reshape(dims)

    return Subentity(
        # Identity
        id=props['id'],
        entity_kind=props.get('entity_kind', 'emergent'),  # Default to 'emergent' for legacy data
        role_or_topic=props.get('role_or_topic', 'unknown'),  # Default to 'unknown' for legacy data
        description=props.get('description', ''),  # Default to empty string for legacy data

        # Semantic representation
        centroid_embedding=centroid,

        # Runtime state (initialized to defaults, recomputed from members)
        energy_runtime=0.0,
        threshold_runtime=1.0,
        activation_level_runtime="absent",

        # Structural quality
        coherence_ema=props.get('coherence_ema', 0.0),
        member_count=props.get('member_count', 0),

        # Learning infrastructure
        ema_active=props.get('ema_active', 0.0),
        log_weight=props.get('log_weight', 0.0),
        ema_wm_presence=props.get('ema_wm_presence', 0.0),
        ema_trace_seats=props.get('ema_trace_seats', 0.0),
        ema_formation_quality=props.get('ema_formation_quality', 0.0),

        # Lifecycle state
        stability_state=props.get('stability_state', 'candidate'),
        quality_score=props.get('quality_score', 0.0),
        last_quality_update=_millis_to_datetime(props['last_quality_update']) if props.get('last_quality_update') else None,

        # Quality tracking
        frames_since_creation=props.get('frames_since_creation', 0),
        high_quality_streak=props.get('high_quality_streak', 0),
        low_quality_streak=props.get('low_quality_streak', 0),

        # Identity multiplicity metrics
        task_progress_rate=props.get('task_progress_rate', 0.0),
        energy_efficiency=props.get('energy_efficiency', 0.0),
        identity_flip_count=props.get('identity_flip_count', 0),

        # Coherence persistence tracking
        coherence_persistence=props.get('coherence_persistence', 0),
        prev_affect_for_coherence=prev_affect,

        # Multi-pattern response (JSON → List/Dict)
        pattern_weights=json.loads(props.get('pattern_weights', '[0.5, 0.3, 0.2]')),
        rumination_frames_consecutive=props.get('rumination_frames_consecutive', 0),
        pattern_effectiveness=json.loads(props.get('pattern_effectiveness', '{"regulation": 0.5, "rumination": 0.5, "distraction": 0.5}')),

        # Provenance
        created_from=props.get('created_from', 'unknown'),
        created_by=props.get('created_by', 'legacy_migration'),  # Default for legacy data
        substrate=props.get('substrate', 'organizational'),
        scope=props.get('scope', 'organizational'),

        # Bitemporal tracking (milliseconds → datetime)
        valid_at=_millis_to_datetime(props['valid_at']) if props.get('valid_at') else datetime.now(timezone.utc),
        invalidated_at=_millis_to_datetime(props['invalidated_at']) if props.get('invalidated_at') else None,
        created_at=_millis_to_datetime(props['created_at']) if props.get('created_at') else datetime.now(timezone.utc),
        expired_at=_millis_to_datetime(props['expired_at']) if props.get('expired_at') else None,

        # Consciousness metadata
        confidence=props.get('confidence', 1.0),
        formation_trigger=props.get('formation_trigger', 'systematic_analysis'),

        # Last update timestamp
        last_update_timestamp=_millis_to_datetime(props['last_update_timestamp']) if props.get('last_update_timestamp') else None,

        # Properties (JSON string → Dict)
        properties=json.loads(props.get('properties', '{}')),

        # Graph structure (will be populated by Graph.add_link)
        outgoing_links=[],
        incoming_links=[],
    )


def build_entity_creation_query(entity: 'Subentity') -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to create subentity in FalkorDB.

    Returns:
        Tuple of (cypher_query, parameters)
    """
    props = serialize_entity(entity)

    # Use SET instead of inline properties - FalkorDB doesn't support $props for CREATE
    query = """
    CREATE (e:Subentity)
    SET e = $props
    RETURN e
    """

    return (query.strip(), {'props': props})


# --- Timestamp Conversion ---

def _datetime_to_millis(dt: datetime) -> int:
    """
    Convert datetime to milliseconds since epoch.

    Args:
        dt: Datetime to convert

    Returns:
        Milliseconds since Unix epoch (int)

    Example:
        >>> dt = datetime(2025, 1, 1)
        >>> _datetime_to_millis(dt)
        1735689600000
    """
    return int(dt.timestamp() * 1000)


def _millis_to_datetime(millis: int) -> datetime:
    """
    Convert milliseconds since epoch to datetime.

    Args:
        millis: Milliseconds since Unix epoch

    Returns:
        Datetime object

    Example:
        >>> millis = 1735689600000
        >>> dt = _millis_to_datetime(millis)
        >>> dt.year
        2025
    """
    return datetime.fromtimestamp(millis / 1000)


# --- Query Builders ---

def build_node_creation_query(node: Node) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to create node in FalkorDB.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> node = Node(id="n1", name="Test", ...)
        >>> query, params = build_node_creation_query(node)
        >>> query
        'CREATE (n:Node $props) RETURN n'
        >>> params['props']['id']
        'n1'
    """
    props = serialize_node(node)

    query = """
    CREATE (n:Node $props)
    RETURN n
    """

    return (query.strip(), {'props': props})


def build_link_creation_query(link: Link) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to create link in FalkorDB.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> link = Link(id="l1", source_id="s", target_id="t", ...)
        >>> query, params = build_link_creation_query(link)
        >>> 'MATCH (source:Node {id: $source_id})' in query
        True
    """
    props = serialize_link(link)

    query = f"""
    MATCH (source:Node {{id: $source_id}})
    MATCH (target:Node {{id: $target_id}})
    CREATE (source)-[r:{link.link_type.value} $props]->(target)
    RETURN r
    """

    return (
        query.strip(),
        {
            'source_id': link.source_id,
            'target_id': link.target_id,
            'props': props
        }
    )


def build_node_query(node_id: str) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to retrieve node by ID.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> query, params = build_node_query("n1")
        >>> query
        'MATCH (n:Node {id: $node_id}) RETURN n'
    """
    query = "MATCH (n:Node {id: $node_id}) RETURN n"
    return (query, {'node_id': node_id})


def build_nodes_with_entity_energy_query(subentity: str, min_energy: float = 0.0) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to find nodes with energy above threshold.

    NOTE: V2 architecture uses single-energy E per node (not per-entity buffers).
    The subentity parameter is ignored in V2.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> query, params = build_nodes_with_entity_energy_query("validator", 0.1)
        >>> params['min_energy']
        0.1
    """
    # V2: Query by total energy E, not entity-specific buffers
    query = """
    MATCH (n:Node)
    WHERE n.E >= $min_energy
    RETURN n
    """

    return (query.strip(), {'min_energy': min_energy})


def build_links_by_type_query(link_type: LinkType) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to retrieve all links of given type.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> query, params = build_links_by_type_query(LinkType.ENABLES)
        >>> 'MATCH ()-[r:ENABLES]->()' in query
        True
    """
    query = f"MATCH ()-[r:{link_type.value}]->() RETURN r"
    return (query, {})


def build_currently_valid_nodes_query(at_time: Optional[datetime] = None) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to find currently valid nodes (reality timeline).

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> query, params = build_currently_valid_nodes_query(datetime(2025, 6, 1))
        >>> 'valid_at' in query
        True
    """
    if at_time is None:
        at_time = datetime.now()

    at_millis = _datetime_to_millis(at_time)

    query = """
    MATCH (n:Node)
    WHERE n.valid_at <= $at_time
      AND (n.invalidated_at IS NULL OR n.invalidated_at > $at_time)
    RETURN n
    """

    return (query.strip(), {'at_time': at_millis})


# --- Batch Operations ---

def build_batch_node_creation_query(nodes: List[Node]) -> tuple[str, Dict[str, Any]]:
    """
    Build Cypher query to create multiple nodes efficiently.

    Returns:
        Tuple of (cypher_query, parameters)

    Example:
        >>> nodes = [Node(...), Node(...)]
        >>> query, params = build_batch_node_creation_query(nodes)
        >>> 'UNWIND $nodes' in query
        True
    """
    serialized_nodes = [serialize_node(n) for n in nodes]

    query = """
    UNWIND $nodes AS node_props
    CREATE (n:Node)
    SET n = node_props
    RETURN n
    """

    return (query.strip(), {'nodes': serialized_nodes})


# --- Graph Utilities ---

def extract_node_from_result(result: Any) -> Node:
    """
    Extract Node object from FalkorDB query result.

    FalkorDB returns results in specific format - this handles extraction.

    Args:
        result: FalkorDB result object

    Returns:
        Node object

    Example:
        >>> result = graph.query("MATCH (n:Node {id: 'n1'}) RETURN n").result_set
        >>> node = extract_node_from_result(result[0][0])
        >>> node.id
        'n1'
    """
    # FalkorDB result format: result_set[row_index][column_index]
    # Assuming result is the node object from result_set
    props = result.properties if hasattr(result, 'properties') else result
    return deserialize_node(props)


def extract_link_from_result(result: Any) -> Link:
    """
    Extract Link object from FalkorDB query result.

    Args:
        result: FalkorDB result object

    Returns:
        Link object

    Example:
        >>> result = graph.query("MATCH ()-[r:ENABLES]->() RETURN r").result_set
        >>> link = extract_link_from_result(result[0][0])
        >>> link.link_type
        <LinkType.ENABLES>
    """
    props = result.properties if hasattr(result, 'properties') else result
    return deserialize_link(props)


# --- MEMBER_OF Edge Persistence (Entity Membership) ---

def get_falkordb_client():
    """
    Get Redis client connected to FalkorDB.

    DEPRECATED: Use get_falkordb_graph() for parametrized queries.
    Only use this for raw redis commands.

    Returns:
        redis.Redis: Client connected to localhost:6379
    """
    return redis.Redis(host='localhost', port=6379, decode_responses=False)


def get_falkordb_graph(graph_name: str):
    """
    Get FalkorDB graph object for parametrized queries.

    This is the CORRECT way to execute parametrized Cypher queries in FalkorDB.
    Uses FalkorDB Python client's graph.query(query, params) API.

    Args:
        graph_name: Graph name (e.g., "citizen_felix", "citizen_luca")

    Returns:
        FalkorDB Graph object

    Example:
        >>> graph = get_falkordb_graph("citizen_felix")
        >>> result = graph.query("MATCH (n:Node {id: $id}) RETURN n", {'id': 'node_1'})

    Author: Atlas (Infrastructure Engineer)
    Fix: 2025-10-26 - Corrected API usage (was using redis-cli syntax in Python)
    """
    db = FalkorDB(host='localhost', port=6379)
    return db.select_graph(graph_name)


def flush_membership_edges(graph_id: str, memberships: List[Dict[str, Any]]) -> int:
    """
    Batch upsert MEMBER_OF edges with activation stats.

    Implements edge-based canonical truth for entity membership. Each membership edge
    contains weight, activation stats, and timestamps. This is the single source of
    truth for membership data - node.entity_activations is derived cache.

    Args:
        graph_id: Target graph (e.g., "citizen_felix")
        memberships: List of membership updates, each containing:
            {
                "node_id": str,
                "entity_id": str,
                "weight_new": float,        // updated weight
                "weight_init": float,       // initial weight if creating edge
                "activation_ema": float,    // running average of activation
                "activation_count_inc": int,  // increment to activation count
                "last_activated_ts": int    // milliseconds timestamp
            }

    Returns:
        Number of edges upserted

    Example:
        >>> memberships = [
        ...     {"node_id": "n1", "entity_id": "E.architect",
        ...      "weight_new": 1.42, "weight_init": 0.4,
        ...      "activation_ema": 0.63, "activation_count_inc": 1,
        ...      "last_activated_ts": 1730074800000},
        ...     {"node_id": "n2", "entity_id": "E.architect",
        ...      "weight_new": 0.88, "weight_init": 0.3,
        ...      "activation_ema": 0.27, "activation_count_inc": 0,
        ...      "last_activated_ts": 1730074798000}
        ... ]
        >>> flush_membership_edges("citizen_felix", memberships)
        2

    Author: Atlas (Infrastructure Engineer)
    Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 2
    Fixed: 2025-10-26 - Use FalkorDB graph.query() API instead of redis execute_command()
    """
    if not memberships:
        return 0

    # Batched upsert query - MERGE creates edge if not exists, updates if exists
    query = """
    UNWIND $memberships AS m
    MERGE (n:Node {id: m.node_id})
    MERGE (e:SubEntity {id: m.entity_id})
    MERGE (n)-[r:MEMBER_OF]->(e)
    ON CREATE SET
      r.weight = m.weight_init,
      r.activation_ema = coalesce(m.activation_ema, 0.0),
      r.activation_count = coalesce(m.activation_count_inc, 0),
      r.last_activated_ts = coalesce(m.last_activated_ts, timestamp()),
      r.created_at = timestamp(),
      r.updated_at = timestamp()
    ON MATCH SET
      r.weight = m.weight_new,
      r.activation_ema = m.activation_ema,
      r.activation_count = coalesce(r.activation_count, 0) + coalesce(m.activation_count_inc, 0),
      r.last_activated_ts = coalesce(m.last_activated_ts, r.last_activated_ts),
      r.updated_at = timestamp()
    """

    params = {"memberships": memberships}

    try:
        graph = get_falkordb_graph(graph_id)
        result = graph.query(query, params)  # CORRECT: FalkorDB Python client API
        logger.debug(f"Flushed {len(memberships)} membership edges to graph {graph_id}")
        return len(memberships)
    except Exception as e:
        logger.error(f"Failed to flush {len(memberships)} membership edges: {e}")
        raise


def rebuild_node_entity_activations_cache(graph_id: str, node_id: str, k: int = 10) -> Dict:
    """
    Rebuild node.entity_activations cache from MEMBER_OF edges (top-K by activation_ema).

    Implements write-through cache pattern: after updating MEMBER_OF edges, rebuild
    the denormalized cache on the node for fast access. Cache contains top-K entities
    by activation strength.

    APOC-free implementation: Builds dict in Python instead of using apoc.map.fromPairs
    for maximum FalkorDB compatibility.

    Args:
        graph_id: Target graph (e.g., "citizen_felix")
        node_id: Node to rebuild cache for
        k: Number of top entities to cache (default: 10)

    Returns:
        Rebuilt cache dict {entity_id: {activation_ema, last_ts, weight}}

    Example:
        >>> cache = rebuild_node_entity_activations_cache("citizen_felix", "n1", k=5)
        >>> cache
        {
            "E.architect": {"activation_ema": 0.63, "last_ts": 1730074800000, "weight": 1.42},
            "E.runtime": {"activation_ema": 0.27, "last_ts": 1730074798000, "weight": 0.88}
        }

    Author: Atlas (Infrastructure Engineer)
    Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 2
    Pattern: Write-through cache (truth on edges, cache on nodes)
    Fixed: 2025-10-26 - Use FalkorDB graph.query() API instead of redis execute_command()
    """
    graph = get_falkordb_graph(graph_id)

    # Query top-K MEMBER_OF edges by activation_ema
    query = """
    MATCH (n:Node {id: $node_id})-[r:MEMBER_OF]->(e:SubEntity)
    RETURN e.id AS eid, r.activation_ema AS a, r.last_activated_ts AS ts, r.weight AS w
    ORDER BY a DESC
    LIMIT $k
    """

    params = {"node_id": node_id, "k": k}
    result = graph.query(query, params)  # CORRECT: FalkorDB Python client API

    # Build cache dict in Python (APOC-free alternative)
    cache = {}
    if result and result.result_set:
        for row in result.result_set:
            eid = row[0]
            a = row[1] if row[1] is not None else 0.0
            ts = row[2] if row[2] is not None else 0
            w = row[3] if row[3] is not None else 0.0

            cache[eid] = {
                "activation_ema": a,
                "last_ts": ts,
                "weight": w
            }

    # Write cache back to node property
    update_query = """
    MATCH (n:Node {id: $node_id})
    SET n.entity_activations = $cache,
        n.entity_activations_updated_at = timestamp()
    """

    cache_json = json.dumps(cache)  # Dict → JSON string for FalkorDB storage
    graph.query(update_query, {"node_id": node_id, "cache": cache_json})  # CORRECT API

    logger.debug(f"Rebuilt entity_activations cache for {node_id}: {len(cache)} entities")
    return cache


# --- FalkorDB Adapter ---

class FalkorDBAdapter:
    """
    Adapter for loading/saving consciousness graphs from/to FalkorDB.

    Provides bridge between Python Node/Link objects and FalkorDB persistence.

    Example:
        >>> from llama_index.graph_stores.falkordb import FalkorDBGraphStore
        >>> graph_store = FalkorDBGraphStore(host="localhost", port=6379, database="falkordb")
        >>> adapter = FalkorDBAdapter(graph_store)
        >>> graph = adapter.load_graph("citizen_felix")
        >>> # ... modify graph ...
        >>> adapter.persist_graph(graph)
    """

    def __init__(self, graph_store):
        """
        Initialize adapter with FalkorDB connection.

        Args:
            graph_store: FalkorDBGraphStore instance
        """
        from orchestration.core.graph import Graph
        self.graph_store = graph_store
        self.Graph = Graph

    def load_graph(self, graph_name: str, limit: Optional[int] = None) -> 'Graph':
        """
        Load complete graph from FalkorDB.

        Args:
            graph_name: Name of graph in FalkorDB
            limit: Optional limit on number of nodes to load

        Returns:
            Graph object with all nodes and links

        Example:
            >>> graph = adapter.load_graph("citizen_felix")
            >>> len(graph.nodes)
            1523
        """
        from orchestration.core.graph import Graph

        graph = Graph(graph_id=graph_name, name=graph_name)

        # Note: graph_store is already connected to the correct database
        # (database parameter was set during FalkorDBGraphStore initialization)

        # Load all nodes
        if limit:
            query = f"MATCH (n) RETURN n LIMIT {limit}"
        else:
            query = "MATCH (n) RETURN n"

        result = self.graph_store.query(query)

        # Handle both QueryResult and list return types (FalkorDB API changed)
        result_set = []
        if result:
            if isinstance(result, list):
                result_set = result
            elif hasattr(result, 'result_set'):
                result_set = result.result_set

        if result_set:
            for row in result_set:
                node_obj = row[0]  # First column is the FalkorDB Node object

                # Get node labels to check if this is a Subentity
                labels = node_obj.labels if hasattr(node_obj, 'labels') else []

                # Skip Subentity nodes - they're loaded separately below
                # Check both 'Subentity' and 'SubEntity' (case variations)
                if any(label.lower() == 'subentity' for label in labels):
                    continue

                # Extract properties - actual schema varies by node type
                props = node_obj.properties if hasattr(node_obj, 'properties') else {}

                # Use ID from props, or generate unique one from internal db id
                node_id = props.get('id') or props.get('node_id') or f"node_{node_obj.id}"
                node_name = props.get('name', props.get('text', node_id))

                # Get node type from label or properties
                node_type_str = labels[0] if labels else props.get('node_type', 'Unknown')

                # Try to get NodeType enum, fallback to a default
                try:
                    from orchestration.core.types import NodeType
                    node_type = NodeType(node_type_str) if node_type_str in NodeType.__members__.values() else NodeType.CONCEPT
                except:
                    # If NodeType doesn't have this value, skip strict typing for now
                    node_type = node_type_str

                # Create minimal Node object
                from orchestration.core.node import Node
                from datetime import datetime

                # Handle energy field - might be JSON string or float
                # Supports both V1 format ({"entity_name": value}) and V2 format ({"default": value})
                energy_raw = props.get('energy', props.get('sub_entity_weights', '{}'))
                if isinstance(energy_raw, str):
                    try:
                        energy = json.loads(energy_raw)
                    except:
                        energy = {}
                elif isinstance(energy_raw, (int, float)):
                    energy = {"default": safe_float(energy_raw, default=0.0, property_name="node.energy")}
                else:
                    energy = {}

                # Extract scalar E value from energy dict (V1/V2 backward compatibility)
                if isinstance(energy, dict):
                    if "default" in energy:
                        # V2 format: {"default": value}
                        E = safe_float(energy["default"], default=0.0, property_name="node.E[default]")
                    elif energy:
                        # V1 format: {"entity_name": value} - use first entity's value
                        E = safe_float(next(iter(energy.values())), default=0.0, property_name="node.E[first_value]")
                    else:
                        # Empty dict
                        E = 0.0
                else:
                    # Not a dict (shouldn't happen given above logic, but handle gracefully)
                    E = safe_float(energy, default=0.0, property_name="node.E") if energy else 0.0

                # Extract theta (activation threshold) - default to 0.5 if not in DB
                theta = props.get('theta', props.get('Θ', 0.5))
                if isinstance(theta, str):
                    theta = safe_float(theta, default=0.5, property_name="node.theta")

                node = Node(
                    id=node_id,
                    name=node_name,
                    node_type=node_type,
                    description=props.get('description', ''),
                    E=E,
                    theta=theta,
                    valid_at=datetime.now(),  # Use current time as fallback
                    created_at=datetime.now(),
                    properties=props  # Store all props for later use
                )

                graph.add_node(node)

        # Load all subentities FIRST (before links) so MEMBER_OF links can reference them
        # NOTE: Query both 'SubEntity' (capital E, current standard) and 'Subentity' (legacy)
        query_subentities = "MATCH (e) WHERE 'SubEntity' IN labels(e) OR 'Subentity' IN labels(e) RETURN e"
        result_subentities = self.graph_store.query(query_subentities)

        # Handle both QueryResult and list return types
        result_set_subentities = []
        if result_subentities:
            if isinstance(result_subentities, list):
                result_set_subentities = result_subentities
            elif hasattr(result_subentities, 'result_set'):
                result_set_subentities = result_subentities.result_set

        if result_set_subentities:
            logger.info(f"Loaded {len(result_set_subentities)} subentities from FalkorDB")
            for row in result_set_subentities:
                entity_obj = row[0]
                props = entity_obj.properties if hasattr(entity_obj, 'properties') else {}

                # Deserialize subentity
                try:
                    entity = deserialize_entity(props)

                    # LAYER 2: Initialize functional entities with neutral EMAs to prevent premature dissolution
                    # Functional entities are permanent infrastructure - their quality shouldn't start at ~0.01
                    if entity.entity_kind == "functional":
                        # Set neutral baselines (0.4-0.6 range) so geometric mean yields healthy quality ~0.5-0.6
                        entity.ema_active = max(getattr(entity, 'ema_active', 0.6), 0.6)
                        entity.coherence_ema = max(getattr(entity, 'coherence_ema', 0.6), 0.6)
                        entity.ema_wm_presence = max(getattr(entity, 'ema_wm_presence', 0.5), 0.5)
                        entity.ema_trace_seats = max(getattr(entity, 'ema_trace_seats', 0.4), 0.4)
                        entity.ema_formation_quality = max(getattr(entity, 'ema_formation_quality', 0.6), 0.6)

                        # Start "old enough" to pass any age-based gates (1000 frames = ~100s)
                        entity.frames_since_creation = max(getattr(entity, 'frames_since_creation', 1000), 1000)

                        # Consider them stable from the start
                        if entity.stability_state == "candidate":
                            entity.stability_state = "mature"

                    # Skip duplicates gracefully (may exist from previous loads or FalkorDB duplicates)
                    if entity.id in graph.subentities:
                        logger.debug(f"  Skipping duplicate subentity: {entity.id}")
                    else:
                        graph.add_entity(entity)
                        logger.debug(f"  Loaded subentity: {entity.id} ({entity.entity_kind})")
                except Exception as e:
                    logger.warning(f"  Failed to deserialize subentity {props.get('id', 'unknown')}: {e}")

            logger.info(f"Loaded {len(graph.subentities)} subentities from FalkorDB")
        else:
            logger.debug("No subentities found in FalkorDB")

        # Load all links (AFTER subentities so MEMBER_OF links can reference entities)
        query = "MATCH ()-[r]->() RETURN r"
        result = self.graph_store.query(query)

        # Handle both QueryResult and list return types
        result_set_links = []
        if result:
            if isinstance(result, list):
                result_set_links = result
            elif hasattr(result, 'result_set'):
                result_set_links = result.result_set

        if result_set_links:
            # Need to query with source/target info
            query_with_nodes = "MATCH (a)-[r]->(b) RETURN r, a, b"
            result_with_nodes = self.graph_store.query(query_with_nodes)

            # Handle both QueryResult and list return types
            result_set_with_nodes = []
            if result_with_nodes:
                if isinstance(result_with_nodes, list):
                    result_set_with_nodes = result_with_nodes
                elif hasattr(result_with_nodes, 'result_set'):
                    result_set_with_nodes = result_with_nodes.result_set

            if result_set_with_nodes:
                for row in result_set_with_nodes:
                    link_obj = row[0]
                    source_obj = row[1]
                    target_obj = row[2]

                    # Extract link properties
                    props = link_obj.properties if hasattr(link_obj, 'properties') else {}

                    # Get source/target IDs - MUST match node ID extraction logic (line 561)
                    source_props = source_obj.properties if hasattr(source_obj, 'properties') else {}
                    target_props = target_obj.properties if hasattr(target_obj, 'properties') else {}

                    source_id = source_props.get('id') or source_props.get('node_id') or f"node_{source_obj.id}"
                    target_id = target_props.get('id') or target_props.get('node_id') or f"node_{target_obj.id}"

                    # Find source and target - could be Node or Subentity
                    source = graph.get_node(source_id) or graph.get_entity(source_id)
                    target = graph.get_node(target_id) or graph.get_entity(target_id)

                    if source and target:
                        # Get link type from relationship type or properties
                        link_type_str = link_obj.relationship if hasattr(link_obj, 'relationship') else props.get('link_type', 'RELATES_TO')

                        # Create minimal Link object
                        from orchestration.core.link import Link
                        from orchestration.core.types import LinkType
                        from datetime import datetime

                        try:
                            # Try to create LinkType enum from string
                            link_type = LinkType(link_type_str)
                        except (ValueError, KeyError):
                            # Fallback to RELATES_TO if invalid
                            link_type = LinkType.RELATES_TO

                        link = Link(
                            id=f"{source_id}_{target_id}_{link_type_str}",
                            source_id=source_id,
                            target_id=target_id,
                            link_type=link_type,
                            subentity=props.get('subentity', props.get('created_by', 'system')),
                            source=source,
                            target=target,
                            weight=safe_float(props.get('weight', props.get('link_strength', 0.5)), default=0.5, property_name="link.weight"),
                            goal=props.get('goal', ''),
                            mindstate=props.get('mindstate', ''),
                            energy=safe_float(props.get('energy', props.get('valence', 0.5)), default=0.5, property_name="link.energy"),
                            confidence=safe_float(props.get('confidence', 0.5), default=0.5, property_name="link.confidence"),
                            valid_at=datetime.now(),
                            created_at=datetime.now()
                        )

                        # Skip duplicate links (Bug #2 fix - 2025-10-23)
                        try:
                            graph.add_link(link)
                        except ValueError as e:
                            if "already exists" in str(e):
                                # Link already in graph, skip (likely from previous load or duplicate in DB)
                                logger.debug(f"Skipping duplicate link {link.id}: {e}")
                            else:
                                raise

        return graph

    def update_node_energy(self, node: 'Node'):
        """
        Persist node energy values to database.

        Args:
            node: Node with updated energy

        Example:
            >>> node.E = 0.8
            >>> adapter.update_node_energy(node)
        """
        # V2: Update single-energy E (not multi-energy dict)
        # Match by id property only (nodes have TRACE schema labels like Realization, Memory, etc.)
        query = """
        MATCH (n {id: $node_id})
        SET n.E = $energy
        RETURN n
        """

        params = {
            'node_id': node.id,
            'energy': node.E  # V2 single scalar, not dict
        }

        self.graph_store.query(query, params)

    @write_gate(lambda self, rows, *args, ctx=None, **kwargs: namespace_for_graph(getattr(self.graph_store, 'name', getattr(self.graph_store, 'database', None))))
    def persist_node_scalars_bulk(self, rows: list[dict], ctx: Optional[Dict[str, str]] = None) -> int:
        """
        Batch persist E and theta for many nodes using UNWIND.

        Args:
            rows: List of dicts with keys: id, name, label, E, theta
                  Example: [{"id": "node_123", "name": "my_node", "label": "Concept", "E": 42.0, "theta": 30.0}, ...]
            ctx: Optional context dict with 'ns' key for WriteGate namespace enforcement
                 Example: {"ns": "L1:citizen_felix"}

        Returns:
            Number of nodes updated

        Example:
            >>> rows = [{"id": "n1", "name": "n1", "label": "Concept", "E": 0.8, "theta": 0.5}]
            >>> updated = adapter.persist_node_scalars_bulk(rows, ctx={"ns": "L1:citizen_felix"})
            >>> print(f"Updated {updated} nodes")

        Note:
            Uses dual-path matching for schema migration:
            - Prefer matching by id if present in both row and database
            - Fallback to matching by name+label for nodes without id
            This allows gradual migration from name-based to id-based schema.

            WriteGate enforcement: ctx['ns'] must match graph namespace or PermissionError is raised
        """
        if not rows:
            return 0

        # Dual-path MATCH: try id first, fallback to name+label
        # This bridges old schema (name-only) and new schema (proper id)
        query = """
        UNWIND $rows AS r
        MATCH (n)
        WHERE (r.id IS NOT NULL AND n.id = r.id)
           OR ( (r.id IS NULL OR n.id IS NULL)
                AND n.name = r.name
                AND (r.label IS NULL OR r.label IN labels(n)) )
        SET n.E = r.E, n.theta = r.theta, n.entity_activations = r.entity_activations
        RETURN count(n) AS updated
        """

        result = self.graph_store.query(query, {"rows": rows})

        # Extract count from result
        # graph_store.query() returns list of rows: [[count]]
        if result and len(result) > 0 and len(result[0]) > 0:
            return int(result[0][0])
        return 0

    def update_link_weight(self, link: 'Link'):
        """
        Persist link weight to database.

        Args:
            link: Link with updated weight

        Example:
            >>> link.weight = 0.9
            >>> adapter.update_link_weight(link)
        """
        # Note: FalkorDB link update requires specifying link type
        query = f"""
        MATCH ()-[r:{link.link_type.value} {{id: $link_id}}]->()
        SET r.weight = $weight
        RETURN r
        """

        params = {
            'link_id': link.id,
            'weight': link.weight
        }

        self.graph_store.query(query, params)

    def persist_graph(self, graph: 'Graph'):
        """
        Persist entire graph state (batch update).

        Updates all node energies and link weights.

        Args:
            graph: Graph to persist

        Example:
            >>> # After running consciousness engine
            >>> adapter.persist_graph(graph)
        """
        # Batch update node energies
        for node in graph.nodes:
            self.update_node_energy(node)

        # Batch update link weights
        for link in graph.links:
            self.update_link_weight(link)


    def update_coactivation_edges(self, selected_entities: list, alpha: float = 0.1):
        """
        Update COACTIVATES_WITH edges between entity pairs based on WM co-selection.

        Lean U metric implementation (wm_coactivation_tracking.md).
        Instead of storing Frame nodes (7M/year, 280GB), maintains aggregate
        co-activation statistics on edges (~600 edges, 48KB).

        Updates O(k²) edges per WM event where k ≈ 5-7 entities.

        Args:
            selected_entities: List of entity IDs currently in WM
            alpha: EMA decay rate (default 0.1)

        Edge properties updated:
            both_ema: EMA of P(both entities in WM together)
            either_ema: EMA of P(either entity in WM)
            u_jaccard: both_ema / either_ema (U metric)
            both_count: Total co-occurrence count
            either_count: Total occurrence count
            last_ts: Last update timestamp

        Example:
            >>> adapter.update_coactivation_edges(
            ...     selected_entities=["entity_backend", "entity_consciousness"],
            ...     alpha=0.1
            ... )
        """
        if len(selected_entities) < 2:
            return  # Need at least 2 entities to form pairs

        try:
            # Update pairwise co-activation edges
            query = """
            UNWIND $pairs AS pair
            MERGE (a:SubEntity {id: pair.entity_a})
            MERGE (b:SubEntity {id: pair.entity_b})
            MERGE (a)-[r:COACTIVATES_WITH]-(b)
            ON CREATE SET
                r.both_ema = $alpha,
                r.either_ema = $alpha,
                r.u_jaccard = 1.0,
                r.both_count = 1,
                r.either_count = 1,
                r.last_ts = timestamp()
            ON MATCH SET
                r.both_ema = $alpha * 1.0 + (1 - $alpha) * r.both_ema,
                r.either_ema = $alpha * 1.0 + (1 - $alpha) * r.either_ema,
                r.both_count = r.both_count + 1,
                r.either_count = r.either_count + 1,
                r.u_jaccard = (r.both_ema + $alpha * 1.0) / (r.either_ema + $alpha * 1.0),
                r.last_ts = timestamp()
            """

            # Generate pairs (only upper triangle to avoid duplicates)
            pairs = []
            for i, entity_a in enumerate(selected_entities):
                for entity_b in selected_entities[i+1:]:
                    # Ensure consistent ordering (A < B lexicographically)
                    if entity_a < entity_b:
                        pairs.append({"entity_a": entity_a, "entity_b": entity_b})
                    else:
                        pairs.append({"entity_a": entity_b, "entity_b": entity_a})

            params = {
                "pairs": pairs,
                "alpha": alpha
            }

            self.graph_store.query(query, params)
            logger.debug(f"[WM Coactivation] Updated {len(pairs)} entity pair edges")

        except Exception as e:
            logger.error(f"[WM Coactivation] Failed to update edges: {e}")

    def persist_subentities(self, graph: 'Graph'):
        """
        Persist all subentities from graph to FalkorDB.

        Creates Subentity nodes and their MEMBER_OF/RELATES_TO links.
        Used after bootstrap to make subentities permanent.

        Args:
            graph: Graph with bootstrapped subentities

        Returns:
            Dict with persistence statistics

        Example:
            >>> # After entity bootstrap
            >>> stats = adapter.persist_subentities(graph)
            >>> print(f"Persisted {stats['entities_created']} subentities")
        """
        stats = {
            'entities_created': 0,
            'member_of_links': 0,
            'relates_to_links': 0,
            'errors': 0
        }

        # Check if subentities already exist in database
        check_query = "MATCH (e:Subentity) RETURN count(e) as count"
        result = self.graph_store.query(check_query)

        # Handle both list and QueryResult return types
        result_set = []
        if result:
            if isinstance(result, list):
                result_set = result
            elif hasattr(result, 'result_set'):
                result_set = result.result_set

        existing_count = result_set[0][0] if result_set else 0

        if existing_count > 0:
            logger.info(f"Subentities already exist in FalkorDB ({existing_count} found), skipping entity creation")
            # NOTE: We still persist MEMBER_OF and RELATES_TO links below (they may be missing)
        else:
            logger.info(f"Persisting {len(graph.subentities)} subentities to FalkorDB...")

            # Create all subentity nodes
            for entity in graph.subentities.values():
                try:
                    query, params = build_entity_creation_query(entity)
                    self.graph_store.query(query, params)
                    stats['entities_created'] += 1
                    logger.debug(f"  Created subentity: {entity.id}")
                except Exception as e:
                    logger.error(f"  Failed to create subentity {entity.id}: {e}")
                    stats['errors'] += 1

        # Create MEMBER_OF links (Node -> Subentity)
        from orchestration.core.types import LinkType
        member_of_links = graph.get_links_by_type(LinkType.MEMBER_OF)

        for link in member_of_links:
            try:
                # Check if target is a Subentity (not Node)
                target = graph.get_entity(link.target_id)
                if target:
                    # Create link in database (use MERGE for idempotency, SET for properties)
                    # NOTE: Don't use :Node label - nodes have specific labels (Concept, Realization, etc.)
                    query = f"""
                    MATCH (source {{id: $source_id}})
                    MATCH (target:Subentity {{id: $target_id}})
                    MERGE (source)-[r:MEMBER_OF]->(target)
                    SET r = $props
                    RETURN r
                    """

                    props = serialize_link(link)
                    params = {
                        'source_id': link.source_id,
                        'target_id': link.target_id,
                        'props': props
                    }

                    self.graph_store.query(query, params)
                    stats['member_of_links'] += 1
            except Exception as e:
                logger.error(f"  Failed to create MEMBER_OF link {link.id}: {e}")
                stats['errors'] += 1

        # Create RELATES_TO links (Subentity -> Subentity)
        relates_to_links = graph.get_links_by_type(LinkType.RELATES_TO)

        for link in relates_to_links:
            try:
                # Check if both source and target are Subentities
                source_entity = graph.get_entity(link.source_id)
                target_entity = graph.get_entity(link.target_id)

                if source_entity and target_entity:
                    # Create link in database (use MERGE for idempotency, SET for properties)
                    query = f"""
                    MATCH (source:Subentity {{id: $source_id}})
                    MATCH (target:Subentity {{id: $target_id}})
                    MERGE (source)-[r:RELATES_TO]->(target)
                    SET r = $props
                    RETURN r
                    """

                    props = serialize_link(link)
                    params = {
                        'source_id': link.source_id,
                        'target_id': link.target_id,
                        'props': props
                    }

                    self.graph_store.query(query, params)
                    stats['relates_to_links'] += 1
            except Exception as e:
                logger.error(f"  Failed to create RELATES_TO link {link.id}: {e}")
                stats['errors'] += 1

        logger.info(f"Subentity persistence complete: {stats}")
        return stats

    async def run_write(self, cypher: str, params: Dict[str, Any]) -> Any:
        """
        Execute write Cypher query asynchronously.

        Wraps synchronous FalkorDB query in async executor for non-blocking operation.

        Args:
            cypher: Cypher query string
            params: Query parameters

        Returns:
            Query result

        Example:
            >>> result = await adapter.run_write(
            ...     "MERGE (n:Node {id: $id}) SET n.value = $value",
            ...     {"id": "n1", "value": 42}
            ... )
        """
        import asyncio
        loop = asyncio.get_event_loop()

        # Run synchronous query in thread executor to avoid blocking
        def _execute():
            try:
                return self.graph_store.query(cypher, params)
            except Exception as e:
                logger.error(f"[FalkorDB] Write query failed: {e}")
                raise

        return await loop.run_in_executor(None, _execute)

    async def update_coactivation_edges_async(
        self,
        citizen_id: str,
        entities_active: List[str],
        alpha: float,
        timestamp_ms: int
    ) -> None:
        """
        Update COACTIVATES_WITH EMAs for all unordered pairs in entities_active.

        Implements lean U-metric (wm_coactivation_tracking.md Priority 0).
        Updates O(k^2) edges per WM event where k ≈ 5-7 entities.

        Edge properties updated:
            both_ema: EMA of P(both entities in WM together)
            either_ema: EMA of P(either entity in WM)
            u_jaccard: both_ema / either_ema (U metric)
            both_count: Total co-occurrence count
            either_count: Total occurrence count
            last_ts: Last update timestamp
            alpha: EMA decay rate

        Args:
            citizen_id: Citizen graph name (for context/logging)
            entities_active: List of entity IDs currently in WM
            alpha: EMA decay rate (default 0.1)
            timestamp_ms: Update timestamp in milliseconds

        Returns:
            None

        Example:
            >>> await adapter.update_coactivation_edges_async(
            ...     citizen_id="citizen_felix",
            ...     entities_active=["entity_backend", "entity_consciousness"],
            ...     alpha=0.1,
            ...     timestamp_ms=1730074800000
            ... )

        Author: Atlas (Infrastructure Engineer)
        Spec: docs/specs/v2/subentity/wm_coactivation_tracking.md
        Implementation: Priority 0 - COACTIVATES_WITH tracking
        """
        if not entities_active or len(entities_active) == 1:
            return  # Need at least 2 entities to form pairs

        # Ensure deterministic A<B ordering for undirected edge
        act = sorted(set(entities_active))
        updates = []

        # Generate all pairwise combinations (O(k^2) where k ≈ 5-7)
        for i in range(len(act)):
            for j in range(i+1, len(act)):
                A, B = act[i], act[j]
                updates.append({
                    "A": A,
                    "B": B,
                    "both_signal": 1.0,   # Both present in WM
                    "either_signal": 1.0,  # Either present
                    "alpha": alpha,
                    "ts": timestamp_ms
                })

        if not updates:
            return

        # Batched upsert with EMA math
        cypher = """
        UNWIND $updates AS u
        MERGE (a:SubEntity {id: u.A})-[r:COACTIVATES_WITH]->(b:SubEntity {id: u.B})
        ON CREATE SET
          r.both_ema=0.0, r.either_ema=0.0, r.u_jaccard=0.0,
          r.both_count=0, r.either_count=0, r.alpha=u.alpha
        SET
          r.both_ema   = u.alpha * u.both_signal   + (1 - u.alpha) * r.both_ema,
          r.either_ema = u.alpha * u.either_signal + (1 - u.alpha) * r.either_ema,
          r.both_count   = r.both_count   + u.both_signal,
          r.either_count = r.either_count + u.either_signal,
          r.last_ts = u.ts,
          r.u_jaccard = CASE WHEN r.either_ema > 1e-12 THEN r.both_ema / r.either_ema ELSE 0.0 END
        """

        try:
            await self.run_write(cypher, {"updates": updates})
            logger.debug(f"[WM Coactivation] Updated {len(updates)} COACTIVATES_WITH edges for {citizen_id}")
        except Exception as e:
            logger.error(f"[WM Coactivation] Failed to update edges for {citizen_id}: {e}")
            raise

    @write_gate(lambda self, graph_name, *args, **kwargs: namespace_for_graph(graph_name))
    def persist_membership(
        self,
        graph_name: str,
        node_id: str,
        entity_name: str,
        weight: float = 1.0,
        role: str = "primary",
        timestamp: Optional[int] = None,
        ctx: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Persist entity membership for a node using hardened MEMBER_OF pattern.

        Creates MEMBER_OF link from node to entity and sets primary_entity property.
        Uses MERGE with ON CREATE/ON MATCH for idempotency - safe to call multiple times.

        PRODUCTION-GRADE PATTERN (P1.3 Hardening + P1.2 Fix):
        - Match nodes by unique 'name' property (schema-based nodes)
        - Match entities by 'name' property with :Subentity label (label-safe)
        - Use MEMBER_OF (semantic: nodes can belong to multiple entities)
        - ε-policy: Update primary_entity only if missing or new weight > current + ε (0.1)
        - Add RETURN barrier to prevent read-after-write races

        Args:
            graph_name: Graph database name
            node_id: Node unique identifier (uses 'name' property for schema-based nodes)
            entity_name: Subentity name (e.g., 'entity_citizen_felix_translator')
            weight: Membership weight (0-1, default 1.0)
            role: Membership role ('primary' or 'secondary', default 'primary')
            timestamp: Creation timestamp in milliseconds (default: now)

        Returns:
            True if successful, False otherwise

        Example:
            >>> adapter.persist_membership(
            ...     "citizen_felix",
            ...     "realization_abc",
            ...     "entity_citizen_felix_translator",
            ...     weight=1.0,
            ...     role="primary"
            ... )
            True
        """
        _ = ctx  # Context enforced by WriteGate
        try:
            # Set graph context
            self.graph_store.database = graph_name

            # Default timestamp to now if not provided
            if timestamp is None:
                from datetime import datetime
                timestamp = int(datetime.now().timestamp() * 1000)

            # P1.3 Hardened pattern: label-safe MATCH + ε-policy for primary_entity
            # P1.2 FIX: Match by 'name' for schema-based nodes (not 'id')
            query = """
            MATCH (n {name: $node_id})
            MATCH (e:Subentity {name: $entity_name})
            MERGE (n)-[r:MEMBER_OF]->(e)
              ON CREATE SET r.role = $role, r.weight = $weight, r.at = $timestamp
              ON MATCH  SET r.role = $role, r.weight = $weight
            WITH n, e, r
            OPTIONAL MATCH (n)-[current_primary:MEMBER_OF]->(primary_e:Subentity)
              WHERE n.primary_entity = primary_e.name
            WITH n, e, r, current_primary
            SET n.primary_entity = CASE
              WHEN $role = 'primary' AND n.primary_entity IS NULL THEN $entity_name
              WHEN $role = 'primary' AND current_primary IS NULL THEN $entity_name
              WHEN $role = 'primary' AND r.weight > coalesce(current_primary.weight, 0.0) + 0.1 THEN $entity_name
              ELSE n.primary_entity
            END
            RETURN 1
            """

            params = {
                'node_id': node_id,
                'entity_name': entity_name,
                'weight': weight,
                'role': role,
                'timestamp': timestamp
            }

            result = self.graph_store.query(query, params)

            # RETURN 1 barrier ensures query completes before returning
            logger.debug(f"Persisted membership: {node_id} -[MEMBER_OF:{role}:{weight}]-> {entity_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to persist membership {node_id} -> {entity_name}: {e}")
            return False

    def get_node_count(self, graph_name: str) -> int:
        """
        Get number of nodes in graph.

        Args:
            graph_name: Graph name

        Returns:
            Node count
        """
        self.graph_store.database = graph_name
        result = self.graph_store.query("MATCH (n) RETURN count(n) as count")

        # FalkorDBGraphStore.query() returns a list: [[count]]
        if result and len(result) > 0:
            return result[0][0]
        return 0

    def get_link_count(self, graph_name: str) -> int:
        """
        Get number of links in graph.

        Args:
            graph_name: Graph name

        Returns:
            Link count
        """
        self.graph_store.database = graph_name
        result = self.graph_store.query("MATCH ()-[r]->() RETURN count(r) as count")

        # FalkorDBGraphStore.query() returns a list: [[count]]
        if result and len(result) > 0:
            return result[0][0]
        return 0
