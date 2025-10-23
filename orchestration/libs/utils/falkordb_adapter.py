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
from datetime import datetime
from typing import Dict, Any, Optional, List

from orchestration.core.node import Node
from orchestration.core.link import Link
from orchestration.core.types import NodeType, LinkType


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
        'ema_trace_seats': node.ema_trace_seats,
        'ema_wm_presence': node.ema_wm_presence,
        'ema_formation_quality': node.ema_formation_quality,
        'scope': node.scope,

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
        ema_trace_seats=props.get('ema_trace_seats', 0.0),
        ema_wm_presence=props.get('ema_wm_presence', 0.0),
        ema_formation_quality=props.get('ema_formation_quality', 0.0),
        scope=props.get('scope', 'personal'),

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
    return {
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

        # Properties (Dict → JSON string)
        'properties': json.dumps(link.properties),
    }


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

        # Properties (JSON string → Dict)
        properties=json.loads(props.get('properties', '{}')),

        # References (will be populated by Graph.add_link)
        source=None,
        target=None,
    )


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

        # FalkorDBGraphStore.query() returns a list directly
        if result:
            for row in result:
                node_obj = row[0]  # First column is the FalkorDB Node object

                # Extract properties - actual schema varies by node type
                props = node_obj.properties if hasattr(node_obj, 'properties') else {}

                # Use ID from props, or generate unique one from internal db id
                node_id = props.get('id') or props.get('node_id') or f"node_{node_obj.id}"
                node_name = props.get('name', props.get('text', node_id))

                # Get node type from label or properties
                labels = node_obj.labels if hasattr(node_obj, 'labels') else []
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
                energy_raw = props.get('energy', props.get('sub_entity_weights', '{}'))
                if isinstance(energy_raw, str):
                    try:
                        energy = json.loads(energy_raw)
                    except:
                        energy = {}
                elif isinstance(energy_raw, (int, float)):
                    energy = {"default": float(energy_raw)}
                else:
                    energy = {}

                node = Node(
                    id=node_id,
                    name=node_name,
                    node_type=node_type,
                    description=props.get('description', ''),
                    E=energy.get("default", 0.0) if isinstance(energy, dict) else (float(energy) if energy else 0.0),
                    valid_at=datetime.now(),  # Use current time as fallback
                    created_at=datetime.now(),
                    properties=props  # Store all props for later use
                )

                graph.add_node(node)

        # Load all links
        query = "MATCH ()-[r]->() RETURN r"
        result = self.graph_store.query(query)

        # FalkorDBGraphStore.query() returns a list directly
        if result:
            # Need to query with source/target info
            query_with_nodes = "MATCH (a)-[r]->(b) RETURN r, a, b"
            result_with_nodes = self.graph_store.query(query_with_nodes)

            if result_with_nodes:
                for row in result_with_nodes:
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

                    # Find nodes in graph
                    source = graph.get_node(source_id)
                    target = graph.get_node(target_id)

                    if source and target:
                        # Get link type from relationship type or properties
                        link_type_str = link_obj.relationship if hasattr(link_obj, 'relationship') else props.get('link_type', 'RELATES_TO')

                        # Create minimal Link object
                        from orchestration.core.link import Link
                        from orchestration.core.types import LinkType
                        from datetime import datetime

                        try:
                            link_type = LinkType(link_type_str) if link_type_str in LinkType.__members__.values() else LinkType.RELATES_TO
                        except:
                            link_type = link_type_str

                        link = Link(
                            id=f"{source_id}_{target_id}_{link_type_str}",
                            source_id=source_id,
                            target_id=target_id,
                            link_type=link_type,
                            subentity=props.get('subentity', props.get('created_by', 'system')),
                            source=source,
                            target=target,
                            weight=float(props.get('weight', props.get('link_strength', 0.5))),
                            goal=props.get('goal', ''),
                            mindstate=props.get('mindstate', ''),
                            energy=float(props.get('energy', props.get('valence', 0.5))),
                            confidence=float(props.get('confidence', 0.5)),
                            valid_at=datetime.now(),
                            created_at=datetime.now()
                        )

                        graph.add_link(link)

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
        query = """
        MATCH (n:Node {id: $node_id})
        SET n.E = $energy
        RETURN n
        """

        params = {
            'node_id': node.id,
            'energy': node.E  # V2 single scalar, not dict
        }

        self.graph_store.query(query, params)

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
