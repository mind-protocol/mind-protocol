"""
Schema Adapter for Graph Health Metrics

Provides weighted neighborhood membership computation to work with current production schema
without requiring explicit :MEMBER_OF relationships.

Weighted Membership Model:
  w_s(n) = max over paths p: s → n (|p| ≤ max_hops) of ∏_{e ∈ p} rel_weight(type(e))

Where relationship weights reflect semantic strength of membership signal.

Author: Felix (Consciousness Engineer)
Date: 2025-10-29
Spec: SYNC.md - "Health metrics now support prod schema via weighted-neighborhood adapter"
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SchemaConfig:
    """Schema configuration for health metrics"""
    view: str  # "prod-weighted-neighborhood" or "spec-explicit-membership"
    max_hops: int
    membership_threshold: float  # Nodes with w_s(n) >= threshold are "members"
    rel_weights: Dict[str, float]

    # Future: explicit relationship names for spec view
    member_rel: str = "MEMBER_OF"
    highway_rel: str = "RELATES_TO"


class SchemaMap:
    """
    Schema adapter that computes weighted membership from graph structure.

    Supports two views:
    1. "prod-weighted-neighborhood": Uses relationship weights and path exploration
    2. "spec-explicit-membership": Uses explicit MEMBER_OF/RELATES_TO relationships

    The prod view works with current deployed graphs where membership is implicit
    in the relationship topology rather than explicit edges.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize schema adapter with configuration."""
        if config_path and config_path.exists():
            self.config = self._load_config(config_path)
        else:
            # Default to prod view with sensible weights
            self.config = self._default_config()

        logger.info(f"SchemaMap initialized: view={self.config.view}, "
                   f"max_hops={self.config.max_hops}, "
                   f"threshold={self.config.membership_threshold}")

    def _default_config(self) -> SchemaConfig:
        """Default configuration for production schema."""
        return SchemaConfig(
            view="prod-weighted-neighborhood",
            max_hops=2,
            membership_threshold=0.5,
            rel_weights={
                # Strongest ownership/operational signals
                "OWNS": 0.85,
                "OPERATES": 0.85,
                "RUNS": 0.85,

                # Implementation/extension signals
                "IMPLEMENTS": 0.80,
                "EXTENDS": 0.80,

                # Documentation/specification signals
                "DOCUMENTS": 0.75,
                "DOCUMENTED_BY": 0.75,
                "PROCESS_FOR": 0.75,

                # Validation/measurement signals
                "MEASURES": 0.70,
                "JUSTIFIES": 0.70,
                "REFUTES": 0.70,

                # Dependency signals
                "ENABLES": 0.60,
                "REQUIRES": 0.60,
                "AFFECTS": 0.60,
                "AFFECTED_BY": 0.60,

                # Lateral/weak signals
                "RELATES_TO": 0.40,
                "SUPERSEDES": 0.40,
                "COACTIVATES_WITH": 0.30,

                # Fallback for unknown relationships
                "_default": 0.20
            }
        )

    def _load_config(self, config_path: Path) -> SchemaConfig:
        """Load schema configuration from YAML file."""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        return SchemaConfig(
            view=data.get('view', 'prod-weighted-neighborhood'),
            max_hops=data.get('max_hops', 2),
            membership_threshold=data.get('membership_threshold', 0.5),
            rel_weights=data.get('rel_weights', {}),
            member_rel=data.get('member_rel', 'MEMBER_OF'),
            highway_rel=data.get('highway_rel', 'RELATES_TO')
        )

    def get_rel_weight(self, rel_type: str) -> float:
        """Get weight for relationship type."""
        return self.config.rel_weights.get(rel_type, self.config.rel_weights.get('_default', 0.20))

    def compute_weighted_membership(self, graph, subentity_id: str) -> Dict[str, float]:
        """
        Compute weighted membership w_s(n) for all nodes reachable from SubEntity s.

        Uses BFS with path weight accumulation up to max_hops.

        Returns:
            Dict[node_id, weight] where weight = max path weight from s to node
        """
        if self.config.view == "spec-explicit-membership":
            # Use explicit MEMBER_OF edges
            return self._compute_explicit_membership(graph, subentity_id)

        # Use weighted neighborhood exploration
        return self._compute_neighborhood_membership(graph, subentity_id)

    def _compute_explicit_membership(self, graph, subentity_id: str) -> Dict[str, float]:
        """Compute membership using explicit MEMBER_OF relationships (future)."""
        query = f"""
        MATCH (s:SubEntity {{id: $subentity_id}})<-[:{self.config.member_rel}]-(n)
        RETURN id(n) AS node_id, 1.0 AS weight
        """
        result = graph.query(query, params={'subentity_id': subentity_id})

        membership = {}
        for record in result.result_set:
            membership[record[0]] = record[1]

        return membership

    def _compute_neighborhood_membership(self, graph, subentity_id: str) -> Dict[str, float]:
        """
        Compute membership using weighted neighborhood exploration.

        Algorithm:
        1. Start from SubEntity s
        2. Explore outgoing paths up to max_hops
        3. For each path, compute weight = ∏ rel_weights
        4. For each node, keep max weight across all paths
        """
        # Cypher query that explores paths and computes weights
        # Using variable-length path with relationship type filtering
        query = """
        MATCH (s:SubEntity {id: $subentity_id})
        CALL apoc.path.expandConfig(s, {
            minLevel: 1,
            maxLevel: $max_hops,
            relationshipFilter: null,
            uniqueness: 'NODE_GLOBAL'
        }) YIELD path
        WITH path, [r IN relationships(path) | type(r)] AS rel_types, nodes(path)[-1] AS end_node
        RETURN id(end_node) AS node_id,
               labels(end_node) AS node_labels,
               rel_types
        """

        try:
            result = graph.query(query, params={
                'subentity_id': subentity_id,
                'max_hops': self.config.max_hops
            })
        except Exception as e:
            # Fallback if apoc.path.expandConfig not available
            logger.warning(f"apoc.path.expandConfig failed ({e}), using simple traversal")
            return self._compute_neighborhood_simple(graph, subentity_id)

        # Compute max weight for each node
        node_weights: Dict[str, float] = {}

        for record in result.result_set:
            node_id = record[0]
            node_labels = record[1]
            rel_types = record[2]

            # Skip if this is another SubEntity (we want content nodes)
            if 'SubEntity' in node_labels or 'Subentity' in node_labels:
                continue

            # Compute path weight as product of relationship weights
            path_weight = 1.0
            for rel_type in rel_types:
                path_weight *= self.get_rel_weight(rel_type)

            # Keep max weight for this node
            if node_id not in node_weights or path_weight > node_weights[node_id]:
                node_weights[node_id] = path_weight

        return node_weights

    def _compute_neighborhood_simple(self, graph, subentity_id: str) -> Dict[str, float]:
        """
        Simple fallback when APOC not available.

        Uses fixed-depth queries instead of variable-length path traversal.
        """
        node_weights: Dict[str, float] = {}

        # Hop 1: Direct neighbors
        query_1 = """
        MATCH (s:SubEntity {id: $subentity_id})-[r]->(n)
        WHERE NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
        RETURN id(n) AS node_id, type(r) AS rel_type
        """
        result = graph.query(query_1, params={'subentity_id': subentity_id})

        for record in result.result_set:
            node_id, rel_type = record[0], record[1]
            weight = self.get_rel_weight(rel_type)
            node_weights[node_id] = weight

        # Hop 2: Second-degree neighbors (if max_hops >= 2)
        if self.config.max_hops >= 2:
            query_2 = """
            MATCH (s:SubEntity {id: $subentity_id})-[r1]->(m)-[r2]->(n)
            WHERE NOT 'SubEntity' IN labels(m) AND NOT 'Subentity' IN labels(m)
              AND NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
              AND id(n) <> id(s)
            RETURN id(n) AS node_id, type(r1) AS rel1, type(r2) AS rel2
            """
            result = graph.query(query_2, params={'subentity_id': subentity_id})

            for record in result.result_set:
                node_id, rel1, rel2 = record[0], record[1], record[2]
                weight = self.get_rel_weight(rel1) * self.get_rel_weight(rel2)

                # Keep max weight
                if node_id not in node_weights or weight > node_weights[node_id]:
                    node_weights[node_id] = weight

        return node_weights

    def get_members(self, graph, subentity_id: str) -> Set[str]:
        """
        Get set of node IDs that are "members" of SubEntity (w_s(n) >= threshold).

        Returns:
            Set of node IDs with membership weight >= threshold
        """
        weights = self.compute_weighted_membership(graph, subentity_id)
        return {node_id for node_id, w in weights.items()
                if w >= self.config.membership_threshold}

    def get_weighted_size(self, graph, subentity_id: str) -> float:
        """
        Get weighted size of SubEntity: sum of w_s(n) for all nodes.

        Returns:
            Weighted sum of membership weights
        """
        weights = self.compute_weighted_membership(graph, subentity_id)
        return sum(weights.values())

    def get_binary_size(self, graph, subentity_id: str) -> int:
        """
        Get binary size of SubEntity: count of nodes with w_s(n) >= threshold.

        Returns:
            Count of member nodes
        """
        return len(self.get_members(graph, subentity_id))

    def compute_overlap_weighted(self, graph, se1_id: str, se2_id: str) -> float:
        """
        Compute weighted Jaccard overlap between two SubEntities.

        J_w(s1, s2) = Σ_n min(w_s1(n), w_s2(n)) / Σ_n max(w_s1(n), w_s2(n))

        Returns:
            Weighted Jaccard coefficient [0, 1]
        """
        w1 = self.compute_weighted_membership(graph, se1_id)
        w2 = self.compute_weighted_membership(graph, se2_id)

        # Get union of all nodes
        all_nodes = set(w1.keys()) | set(w2.keys())

        if not all_nodes:
            return 0.0

        # Compute weighted Jaccard
        numerator = sum(min(w1.get(n, 0), w2.get(n, 0)) for n in all_nodes)
        denominator = sum(max(w1.get(n, 0), w2.get(n, 0)) for n in all_nodes)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def find_orphans(self, graph) -> List[Dict]:
        """
        Find orphan nodes: nodes with max_s w_s(n) < threshold.

        These are nodes weakly connected to all SubEntities.

        Returns:
            List of {id, labels, max_weight} for orphan nodes
        """
        # Get all SubEntities
        query = "MATCH (s:SubEntity) RETURN id(s) AS se_id, s.id AS se_name"
        result = graph.query(query)
        subentity_ids = [record[1] or record[0] for record in result.result_set]

        if not subentity_ids:
            return []

        # Compute membership for all SubEntities
        all_memberships: Dict[str, Dict[str, float]] = {}
        for se_id in subentity_ids:
            all_memberships[se_id] = self.compute_weighted_membership(graph, se_id)

        # Find all nodes and their max membership weight
        query = """
        MATCH (n)
        WHERE NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
        RETURN id(n) AS node_id, labels(n) AS node_labels
        """
        result = graph.query(query)

        orphans = []
        for record in result.result_set:
            node_id, node_labels = record[0], record[1]

            # Find max membership weight across all SubEntities
            max_weight = 0.0
            for se_id, memberships in all_memberships.items():
                weight = memberships.get(node_id, 0.0)
                if weight > max_weight:
                    max_weight = weight

            # If max weight below threshold, it's an orphan
            if max_weight < self.config.membership_threshold:
                orphans.append({
                    'id': node_id,
                    'labels': node_labels,
                    'max_weight': max_weight
                })

        return orphans

    def get_highway_query(self) -> str:
        """
        Get Cypher query for highway relationships.

        Returns query string for the appropriate schema view.
        """
        if self.config.view == "spec-explicit-membership":
            # Future: use explicit RELATES_TO
            return f"""
            MATCH (s1:SubEntity)-[r:{self.config.highway_rel}]->(s2:SubEntity)
            RETURN id(s1) AS source_id, id(s2) AS target_id, r.weight AS weight
            """
        else:
            # Current: use COACTIVATES_WITH
            return """
            MATCH (s1:SubEntity)-[r:COACTIVATES_WITH]->(s2:SubEntity)
            RETURN id(s1) AS source_id, id(s2) AS target_id,
                   coalesce(r.count, 1) AS weight
            """
