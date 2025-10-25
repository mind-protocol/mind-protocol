"""
Graph container - manages nodes, subentities, and links.

ARCHITECTURAL PRINCIPLE: Container, not controller.

Graph provides:
- Storage (nodes, subentities, links)
- Basic operations (add, get, remove)
- Graph structure maintenance (link references)

Graph does NOT provide:
- Energy dynamics (see mechanisms/diffusion.py)
- Workspace selection (see services/workspace.py)
- Subentity detection (see services/subentity.py)

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1 Clean Break + Phase 7 Multi-Scale
"""

from typing import Dict, List, Optional, Set, Union
from datetime import datetime

from .node import Node
from .subentity import Subentity
from .link import Link
from .types import NodeID, EntityID, NodeType, LinkType


class Graph:
    """
    Container for nodes, subentities, and links with basic graph operations.

    This is a CONTAINER, not a CONTROLLER. Complex operations delegate to:
    - orchestration.mechanisms.* (energy dynamics)
    - orchestration.services.* (workspace, clustering, subentity detection)

    Storage:
        nodes: Dict[NodeID, Node] - All nodes by ID
        subentities: Dict[str, Subentity] - All subentities by ID
        links: Dict[LinkID, Link] - All links by ID

    Graph Structure:
        Maintains bidirectional references:
        - Node.outgoing_links / Node.incoming_links
        - Subentity.outgoing_links / Subentity.incoming_links
        - Link.source / Link.target (can be Node or Subentity)
    """

    def __init__(self, graph_id: str, name: str):
        """
        Initialize empty graph.

        Args:
            graph_id: Unique graph identifier (e.g., "citizen_luca")
            name: Human-readable name
        """
        self.id = graph_id
        self.name = name

        # Storage
        self.nodes: Dict[NodeID, Node] = {}
        self.subentities: Dict[str, Subentity] = {}
        self.links: Dict[str, Link] = {}

        # Metadata
        self.created_at = datetime.now()

    # --- Node Operations ---

    def add_node(self, node: Node) -> None:
        """
        Add node to graph.

        Args:
            node: Node to add

        Raises:
            ValueError: If node.id already exists
        """
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists in graph {self.id}")

        self.nodes[node.id] = node

    def get_node(self, node_id: NodeID) -> Optional[Node]:
        """
        Get node by ID.

        Args:
            node_id: Node identifier

        Returns:
            Node if found, None otherwise
        """
        return self.nodes.get(node_id)

    def remove_node(self, node_id: NodeID) -> None:
        """
        Remove node and all connected links.

        Args:
            node_id: Node identifier
        """
        node = self.nodes.get(node_id)
        if not node:
            return

        # Remove all connected links
        for link in list(node.outgoing_links):
            self.remove_link(link.id)
        for link in list(node.incoming_links):
            self.remove_link(link.id)

        # Remove node
        del self.nodes[node_id]

    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """
        Get all nodes of given type.

        Args:
            node_type: Type to filter by

        Returns:
            List of nodes with matching type
        """
        return [n for n in self.nodes.values() if n.node_type == node_type]

    # --- Subentity Operations ---

    def add_entity(self, subentity: Subentity) -> None:
        """
        Add subentity to graph.

        Args:
            subentity: Subentity to add

        Raises:
            ValueError: If subentity.id already exists
        """
        if subentity.id in self.subentities:
            raise ValueError(f"Subentity {subentity.id} already exists in graph {self.id}")

        self.subentities[subentity.id] = subentity

    def get_entity(self, entity_id: str) -> Optional[Subentity]:
        """
        Get subentity by ID.

        Args:
            entity_id: Subentity identifier

        Returns:
            Subentity if found, None otherwise
        """
        return self.subentities.get(entity_id)

    def remove_entity(self, entity_id: str) -> None:
        """
        Remove subentity and all connected links.

        Args:
            entity_id: Subentity identifier
        """
        subentity = self.subentities.get(entity_id)
        if not subentity:
            return

        # Remove all connected links
        for link in list(subentity.outgoing_links):
            self.remove_link(link.id)
        for link in list(subentity.incoming_links):
            self.remove_link(link.id)

        # Remove subentity
        del self.subentities[entity_id]

    def get_entities_by_kind(self, entity_kind: str) -> List[Subentity]:
        """
        Get all subentities of given kind.

        Args:
            entity_kind: Kind to filter by ("functional" or "semantic")

        Returns:
            List of subentities with matching kind
        """
        return [e for e in self.subentities.values() if e.entity_kind == entity_kind]

    def get_active_entities(self) -> List[Subentity]:
        """
        Get all subentities currently active (energy >= threshold).

        Returns:
            List of active subentities
        """
        return [e for e in self.subentities.values() if e.is_active()]

    # --- Link Operations ---

    def add_link(self, link: Link) -> None:
        """
        Add link to graph and update node/subentity references.

        Supports:
        - Node -> Node links (ENABLES, BLOCKS, etc.)
        - Node -> Subentity links (BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF"))
        - Subentity -> Subentity links (RELATES_TO)

        Args:
            link: Link to add

        Raises:
            ValueError: If link.id already exists or source/target not found
        """
        if link.id in self.links:
            raise ValueError(f"Link {link.id} already exists in graph {self.id}")

        # Try to find source in nodes, then subentities
        source: Union[Node, Subentity, None] = self.get_node(link.source_id)
        if not source:
            source = self.get_entity(link.source_id)

        # Try to find target in nodes, then subentities
        target: Union[Node, Subentity, None] = self.get_node(link.target_id)
        if not target:
            target = self.get_entity(link.target_id)

        if not source:
            raise ValueError(f"Source {link.source_id} not found in graph {self.id}")
        if not target:
            raise ValueError(f"Target {link.target_id} not found in graph {self.id}")

        # Update link references
        link.source = source
        link.target = target

        # Update source/target references
        source.outgoing_links.append(link)
        target.incoming_links.append(link)

        # Store link
        self.links[link.id] = link

    def get_link(self, link_id: str) -> Optional[Link]:
        """
        Get link by ID.

        Args:
            link_id: Link identifier

        Returns:
            Link if found, None otherwise
        """
        return self.links.get(link_id)

    def remove_link(self, link_id: str) -> None:
        """
        Remove link and update node references.

        Args:
            link_id: Link identifier
        """
        link = self.links.get(link_id)
        if not link:
            return

        # Remove from node references
        if link.source:
            link.source.outgoing_links.remove(link)
        if link.target:
            link.target.incoming_links.remove(link)

        # Remove link
        del self.links[link_id]

    def get_links_by_type(self, link_type: LinkType) -> List[Link]:
        """
        Get all links of given type.

        Args:
            link_type: Type to filter by

        Returns:
            List of links with matching type
        """
        return [l for l in self.links.values() if l.link_type == link_type]

    # --- Subentity Queries (delegate to mechanisms) ---

    def get_all_active_entities(self) -> Set[EntityID]:
        """
        Get all subentities with non-zero energy anywhere in graph.

        Scans all nodes for active energy.

        Returns:
            Set of subentity IDs with energy > 0

        NOTE: In V2 architecture, nodes use single-energy E (not per-entity buffers).
        Entity differentiation is handled by mechanism layer via membership/selection.
        This method returns empty set as there are no entity-specific energy buffers.
        """
        # V2: No per-entity buffers, entity differentiation via mechanism layer
        return set()

    def get_nodes_with_entity_energy(self, subentity: EntityID, min_energy: float = 0.0) -> List[Node]:
        """
        Get all nodes where subentity has energy above threshold.

        Args:
            subentity: Subentity identifier
            min_energy: Minimum energy threshold (default 0.0)

        Returns:
            List of nodes with subentity energy > min_energy
        """
        return [
            node for node in self.nodes.values()
            if node.get_entity_energy(subentity) > min_energy
        ]

    # --- Statistics ---

    def __len__(self) -> int:
        """Number of nodes in graph."""
        return len(self.nodes)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (f"Graph(id={self.id!r}, nodes={len(self.nodes)}, "
                f"subentities={len(self.subentities)}, links={len(self.links)})")
