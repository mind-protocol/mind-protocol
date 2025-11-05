"""
Integration Depth & Breadth Metrics - Path-Dependent Scale Analysis

Measures where SubEntities sit in heterarchical topology:
- **Depth**: Hop-distance from primitive patterns (foundational concepts)
- **Breadth**: Number of distinct communities connected
- **Closeness**: Average hop-distance to all other nodes

Key insight: Scale is path-dependent. Same SubEntity can be:
- 2 hops from primitive (concrete, grounded)
- 7 hops from primitive (abstract, meta-level)
- Connected to 5 communities (integrative bridge)

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/integration_depth_breadth_metrics.md
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from falkordb import Graph


@dataclass
class IntegrationMetricsConfig:
    """Configuration for integration metrics analysis."""
    use_louvain: bool = True        # Use Louvain for community detection
    cache_ttl: int = 300            # Cache lifetime in seconds


class IntegrationMetricsAnalyzer:
    """
    Compute integration depth, breadth, and closeness for SubEntities.

    All metrics are query-time (not stored properties).

    **Depth** = Min hop-distance from primitive SubEntities (in_degree=0)
    **Breadth** = Number of distinct communities connected
    **Closeness** = Inverse average hop-distance to all nodes
    """

    def __init__(
        self,
        graph: Graph,
        config: Optional[IntegrationMetricsConfig] = None
    ):
        """
        Initialize integration metrics analyzer.

        Args:
            graph: FalkorDB graph instance
            config: Analysis configuration
        """
        self.graph = graph
        self.config = config or IntegrationMetricsConfig()

        # Community assignments (lazy-loaded): {node_id: community_id}
        self.communities: Optional[Dict[str, int]] = None
        self.communities_timestamp: float = 0.0

        # Telemetry
        self.depth_computations: int = 0
        self.breadth_computations: int = 0
        self.closeness_computations: int = 0

    def identify_primitives(self) -> List[str]:
        """
        Identify primitive SubEntities (no inbound MEMBER_OF edges).

        Primitives = foundational patterns at bottom of dependency graph.

        Returns:
            List of primitive node IDs
        """
        query = """
        MATCH (primitive:SubEntity)
        WHERE NOT (primitive)<-[:MEMBER_OF]-()
        RETURN primitive.id as id
        """

        try:
            result = self.graph.query(query)
            primitives = [row[0] for row in result.result_set]
            return primitives

        except Exception as e:
            print(f"[IntegrationMetrics] Failed to identify primitives: {e}")
            return []

    def compute_integration_depth(self, node_id: str) -> int:
        """
        Compute integration depth (min hops from any primitive).

        Depth interpretation:
        - depth=1: Primitive itself
        - depth=2: Direct composite of primitives
        - depth=5: Mid-level abstraction
        - depth=10+: High-level meta-pattern

        Args:
            node_id: SubEntity ID

        Returns:
            Depth value (1 = primitive, higher = more abstract)
        """
        self.depth_computations += 1

        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})

        // Find all primitives (no inbound edges)
        MATCH (primitive:SubEntity)
        WHERE NOT (primitive)<-[:MEMBER_OF]-()

        // Shortest path from any primitive to target
        MATCH path = shortestPath((primitive)-[:MEMBER_OF*]->(target))

        // Return minimum path length
        WITH length(path) as pathLength
        RETURN min(pathLength) as integration_depth
        """

        try:
            result = self.graph.query(query)

            if result.result_set and result.result_set[0][0] is not None:
                return int(result.result_set[0][0])

            # If unreachable from primitives, treat as primitive itself
            return 1

        except Exception as e:
            print(f"[IntegrationMetrics] Depth computation failed for {node_id}: {e}")
            return 1

    def compute_integration_breadth(self, node_id: str) -> int:
        """
        Compute integration breadth (distinct communities connected).

        Breadth interpretation:
        - breadth=1: Specialist (all neighbors in same community)
        - breadth=3: Moderate integrator (bridges 3 communities)
        - breadth=7+: Major integration hub (cross-domain connector)

        Args:
            node_id: SubEntity ID

        Returns:
            Number of distinct communities connected
        """
        self.breadth_computations += 1

        # Lazy-load community assignments
        if self.communities is None or self._communities_stale():
            self.communities = self._run_community_detection()

        if not self.communities:
            return 0

        # Get neighbors (both inbound and outbound MEMBER_OF)
        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})

        // Inbound edges (children)
        OPTIONAL MATCH (target)<-[:MEMBER_OF]-(child)

        // Outbound edges (parents)
        OPTIONAL MATCH (target)-[:MEMBER_OF]->(parent)

        // Collect all neighbor IDs
        WITH collect(DISTINCT child.id) + collect(DISTINCT parent.id) as neighbor_ids
        RETURN neighbor_ids
        """

        try:
            result = self.graph.query(query)

            if not result.result_set or not result.result_set[0][0]:
                return 0

            neighbor_ids = [nid for nid in result.result_set[0][0] if nid]

            # Map neighbors to communities
            neighbor_communities = [
                self.communities[nid]
                for nid in neighbor_ids
                if nid in self.communities
            ]

            # Count distinct communities
            return len(set(neighbor_communities))

        except Exception as e:
            print(f"[IntegrationMetrics] Breadth computation failed for {node_id}: {e}")
            return 0

    def compute_closeness_centrality(self, node_id: str) -> float:
        """
        Compute closeness centrality (inverse avg hop-distance).

        Closeness interpretation:
        - High closeness (0.8-1.0) = Central (close to everything)
        - Low closeness (0.0-0.3) = Peripheral (far from most nodes)

        Args:
            node_id: SubEntity ID

        Returns:
            Closeness value (0-1, higher = more central)
        """
        self.closeness_computations += 1

        query = f"""
        MATCH (target:SubEntity {{id: '{node_id}'}})

        // Find shortest paths to all other nodes
        MATCH path = shortestPath((target)-[:MEMBER_OF*]-(other:SubEntity))
        WHERE other.id <> target.id

        // Compute average distance
        WITH length(path) as distance
        WITH count(*) as reachableNodes, sum(distance) as totalDistance

        // Closeness = (N-1) / Σdistance
        RETURN (reachableNodes * 1.0 / totalDistance) as closeness
        """

        try:
            result = self.graph.query(query)

            if result.result_set and result.result_set[0][0] is not None:
                return float(result.result_set[0][0])

            return 0.0

        except Exception as e:
            print(f"[IntegrationMetrics] Closeness computation failed for {node_id}: {e}")
            return 0.0

    def compute_all_metrics(self, node_id: str) -> Dict[str, Any]:
        """
        Compute all integration metrics for a node.

        Returns:
            {
                'integration_depth': int,
                'integration_breadth': int,
                'closeness_centrality': float,
                'interpretation': str
            }
        """
        depth = self.compute_integration_depth(node_id)
        breadth = self.compute_integration_breadth(node_id)
        closeness = self.compute_closeness_centrality(node_id)

        return {
            'integration_depth': depth,
            'integration_breadth': breadth,
            'closeness_centrality': round(closeness, 4),
            'interpretation': self._interpret_metrics(depth, breadth)
        }

    def compute_population_distribution(self) -> Dict[str, Any]:
        """
        Compute depth/breadth distribution across all SubEntities.

        Returns:
            {
                'depth_distribution': {range: count},
                'breadth_distribution': {range: count},
                'mean_depth': float,
                'mean_breadth': float,
                'primitive_count': int
            }
        """
        # Get all SubEntity IDs
        query = "MATCH (s:SubEntity) RETURN s.id as id"

        try:
            result = self.graph.query(query)
            node_ids = [row[0] for row in result.result_set]

            if not node_ids:
                return {
                    'depth_distribution': {},
                    'breadth_distribution': {},
                    'mean_depth': 0.0,
                    'mean_breadth': 0.0,
                    'primitive_count': 0
                }

            # Compute metrics for all nodes
            depths = []
            breadths = []

            for node_id in node_ids:
                depth = self.compute_integration_depth(node_id)
                breadth = self.compute_integration_breadth(node_id)
                depths.append(depth)
                breadths.append(breadth)

            # Bin distributions
            depth_bins = {'1-2': 0, '3-5': 0, '6-8': 0, '9+': 0}
            for d in depths:
                if d <= 2:
                    depth_bins['1-2'] += 1
                elif d <= 5:
                    depth_bins['3-5'] += 1
                elif d <= 8:
                    depth_bins['6-8'] += 1
                else:
                    depth_bins['9+'] += 1

            breadth_bins = {'1-2': 0, '3-5': 0, '6+': 0}
            for b in breadths:
                if b <= 2:
                    breadth_bins['1-2'] += 1
                elif b <= 5:
                    breadth_bins['3-5'] += 1
                else:
                    breadth_bins['6+'] += 1

            # Count primitives
            primitives = self.identify_primitives()

            return {
                'depth_distribution': depth_bins,
                'breadth_distribution': breadth_bins,
                'mean_depth': round(float(np.mean(depths)), 2),
                'mean_breadth': round(float(np.mean(breadths)), 2),
                'primitive_count': len(primitives)
            }

        except Exception as e:
            print(f"[IntegrationMetrics] Population distribution failed: {e}")
            return {
                'depth_distribution': {},
                'breadth_distribution': {},
                'mean_depth': 0.0,
                'mean_breadth': 0.0,
                'primitive_count': 0
            }

    def emit_telemetry(
        self,
        node_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate telemetry event for integration metrics.

        Args:
            node_id: Node ID
            metrics: Computed metrics dict

        Returns:
            Telemetry event dict
        """
        # Get node details
        query = f"""
        MATCH (n:SubEntity {{id: '{node_id}'}})
        RETURN n.name as name
        """

        try:
            result = self.graph.query(query)
            node_name = "unknown"
            if result.result_set:
                node_name = result.result_set[0][0] or result.result_set[0][1] or node_id
        except:
            node_name = node_id

        return {
            'type': 'integration_metrics.node',
            'timestamp': time.time(),
            'node_id': node_id,
            'node_name': node_name,
            'metrics': metrics
        }

    def _run_community_detection(self) -> Dict[str, int]:
        """
        Run Louvain community detection.

        Returns:
            {node_id: community_id}
        """
        if not self.config.use_louvain:
            return self._fallback_community_detection()

        try:
            query = """
            CALL algo.louvain.stream('SubEntity', 'MEMBER_OF')
            YIELD nodeId, community
            RETURN nodeId, community
            """

            result = self.graph.query(query)
            communities = {row[0]: int(row[1]) for row in result.result_set}
            self.communities_timestamp = time.time()

            return communities

        except Exception as e:
            print(f"[IntegrationMetrics] Louvain not available, using fallback: {e}")
            return self._fallback_community_detection()

    def _fallback_community_detection(self) -> Dict[str, int]:
        """
        Fallback community detection using simple connected components.

        Returns:
            {node_id: community_id}
        """
        query = "MATCH (s:SubEntity) RETURN s.id as id"

        try:
            result = self.graph.query(query)
            nodes = [row[0] for row in result.result_set]

            # Simple: Assign all to community 0
            # (Real implementation would do BFS/DFS for connected components)
            self.communities_timestamp = time.time()
            return {node_id: 0 for node_id in nodes}

        except Exception as e:
            print(f"[IntegrationMetrics] Fallback community detection failed: {e}")
            return {}

    def _communities_stale(self) -> bool:
        """Check if community assignments are stale."""
        return (time.time() - self.communities_timestamp) > self.config.cache_ttl

    def _interpret_metrics(self, depth: int, breadth: int) -> str:
        """
        Interpret depth/breadth into human-readable category.

        Returns:
            Category string
        """
        if depth <= 2 and breadth <= 2:
            return "primitive_specialist"
        elif depth <= 2 and breadth > 4:
            return "foundational_integrator"
        elif depth > 6 and breadth <= 2:
            return "abstract_specialist"
        elif depth > 6 and breadth > 4:
            return "meta_integrator"
        else:
            return "mid_level_pattern"

    def get_telemetry_stats(self) -> Dict[str, Any]:
        """Get analyzer telemetry stats."""
        return {
            'depth_computations': self.depth_computations,
            'breadth_computations': self.breadth_computations,
            'closeness_computations': self.closeness_computations,
            'communities_loaded': self.communities is not None,
            'community_count': len(set(self.communities.values())) if self.communities else 0
        }
