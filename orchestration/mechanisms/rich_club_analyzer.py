"""
Rich-Club Hub Identification - Betweenness Centrality Analysis

Identifies rich-club hubs (SubEntities with high betweenness centrality) that act as
structural bridges connecting multiple communities in the heterarchical graph.

Betweenness centrality = number of shortest paths passing through a node.
High betweenness → critical integration hub → removing it fragments the network.

Uses sampled approximation (k random sources) for performance on large graphs.

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/rich_club_hub_identification.md
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from falkordb import Graph


@dataclass
class RichClubConfig:
    """Configuration for rich-club analysis."""
    sample_size: int = 500          # Number of source nodes to sample
    cache_ttl: int = 300            # Cache lifetime in seconds (5 minutes)
    percentile_threshold: float = 0.90  # Top 10% = hubs


class RichClubAnalyzer:
    """
    Identify rich-club hubs in SubEntity graph using betweenness centrality.

    Betweenness = #(shortest paths passing through node) / #(total sampled paths)

    Uses sampled approximation:
    - Sample k random source nodes
    - Compute shortest paths from each source to all targets
    - Count paths passing through each intermediate node
    - Normalize by sample size

    Complexity: O(k × n × m) where k=sample_size, n=nodes, m=avg path length
    """

    def __init__(
        self,
        graph: Graph,
        config: Optional[RichClubConfig] = None
    ):
        """
        Initialize rich-club analyzer.

        Args:
            graph: FalkorDB graph instance
            config: Analysis configuration
        """
        self.graph = graph
        self.config = config or RichClubConfig()

        # Cache: {node_id: (betweenness, timestamp)}
        self.betweenness_cache: Dict[str, Tuple[float, float]] = {}

        # Telemetry
        self.computations: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def compute_betweenness_all(
        self,
        force_recompute: bool = False
    ) -> Dict[str, float]:
        """
        Compute betweenness centrality for all SubEntities.

        Uses sampled approximation for performance.

        Args:
            force_recompute: Bypass cache and recompute

        Returns:
            {node_id: betweenness_score} normalized to [0, 1]
        """
        self.computations += 1

        # Check cache freshness
        if not force_recompute and self._is_cache_fresh():
            self.cache_hits += 1
            return {node_id: score for node_id, (score, _) in self.betweenness_cache.items()}

        self.cache_misses += 1

        # Cypher query: Sampled betweenness approximation
        query = f"""
        // Step 1: Sample k random source nodes
        MATCH (source:SubEntity)
        WITH source, rand() as r
        ORDER BY r
        LIMIT {self.config.sample_size}

        // Step 2: For each source, find shortest paths to all targets
        WITH collect(source) as sources
        UNWIND sources AS src
        MATCH path = shortestPath((src)-[:MEMBER_OF*]-(target:SubEntity))
        WHERE src.id <> target.id

        // Step 3: Extract intermediate nodes (excluding source and target)
        WITH src, target, path, nodes(path) as pathNodes
        UNWIND pathNodes[1..-1] AS intermediateNode
        WHERE intermediateNode.id <> src.id AND intermediateNode.id <> target.id

        // Step 4: Count paths through each intermediate node
        WITH intermediateNode.id as nodeId, count(*) as pathCount

        // Step 5: Normalize by sample size
        RETURN nodeId, pathCount, (pathCount * 1.0 / {self.config.sample_size}) as betweenness
        """

        try:
            result = self.graph.query(query)

            # Extract results
            betweenness_scores = {}
            timestamp = time.time()

            if result.result_set:
                for row in result.result_set:
                    node_id = row[0]  # nodeId
                    betweenness = float(row[2])  # betweenness (normalized)
                    betweenness_scores[node_id] = betweenness
                    self.betweenness_cache[node_id] = (betweenness, timestamp)

            return betweenness_scores

        except Exception as e:
            # Fallback: Return empty dict if query fails
            print(f"[RichClubAnalyzer] Betweenness computation failed: {e}")
            return {}

    def identify_rich_club_hubs(
        self,
        percentile: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """
        Identify top percentile of nodes by betweenness (rich-club hubs).

        Args:
            percentile: Threshold (0.90 = top 10%)

        Returns:
            [(node_id, betweenness), ...] sorted descending by betweenness
        """
        percentile = percentile or self.config.percentile_threshold

        # Compute betweenness for all nodes
        betweenness_scores = self.compute_betweenness_all()

        if not betweenness_scores:
            return []

        # Compute threshold
        scores = list(betweenness_scores.values())
        threshold = float(np.percentile(scores, percentile * 100))

        # Filter hubs above threshold
        hubs = [
            (node_id, score)
            for node_id, score in betweenness_scores.items()
            if score >= threshold
        ]

        # Sort descending by betweenness
        hubs.sort(key=lambda x: x[1], reverse=True)

        return hubs

    def get_hub_details(self, hub_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed info about a hub node.

        Returns:
            {
                'id': str,
                'name': str,
                'betweenness': float,
                'degree_in': int,
                'degree_out': int,
                'energy': float
            }
        """
        query = f"""
        MATCH (hub:SubEntity {{id: '{hub_id}'}})

        // Count inbound edges
        OPTIONAL MATCH (hub)<-[:MEMBER_OF]-(child)
        WITH hub, count(DISTINCT child) as degree_in

        // Count outbound edges
        OPTIONAL MATCH (hub)-[:MEMBER_OF]->(parent)
        WITH hub, degree_in, count(DISTINCT parent) as degree_out

        RETURN
            hub.id as id,
            hub.name as name,
            hub.role_or_topic as role,
            degree_in,
            degree_out,
            hub.energy_runtime as energy
        """

        try:
            result = self.graph.query(query)

            if not result.result_set:
                return None

            row = result.result_set[0]

            # Get betweenness from cache or compute
            betweenness = 0.0
            if hub_id in self.betweenness_cache:
                betweenness, _ = self.betweenness_cache[hub_id]
            else:
                # Compute for this node only
                all_scores = self.compute_betweenness_all()
                betweenness = all_scores.get(hub_id, 0.0)

            return {
                'id': row[0],
                'name': row[1] if row[1] else row[2],  # name or role
                'betweenness': round(betweenness, 4),
                'degree_in': row[3] or 0,
                'degree_out': row[4] or 0,
                'energy': float(row[5]) if row[5] else 0.0
            }

        except Exception as e:
            print(f"[RichClubAnalyzer] Failed to get hub details for {hub_id}: {e}")
            return None

    def detect_hub_at_risk(
        self,
        hub_id: str,
        energy_threshold: float = 0.2
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a critical hub is at risk (low energy).

        Args:
            hub_id: Hub node ID
            energy_threshold: Energy below this = at risk

        Returns:
            Risk alert dict if hub is critical and low energy, None otherwise
        """
        details = self.get_hub_details(hub_id)

        if not details:
            return None

        # Check if hub is critical (high betweenness)
        if details['betweenness'] < 0.5:
            return None  # Not critical enough

        # Check if energy is low
        if details['energy'] > energy_threshold:
            return None  # Energy is fine

        # Hub is at risk
        risk_level = "high" if details['energy'] < 0.1 else "medium"

        return {
            'type': 'rich_club.hub_at_risk',
            'timestamp': time.time(),
            'hub_id': hub_id,
            'hub_name': details['name'],
            'betweenness': details['betweenness'],
            'current_energy': details['energy'],
            'threshold_critical': energy_threshold,
            'risk_level': risk_level,
            'impact': f"Loss of this hub (betweenness={details['betweenness']:.2f}) would fragment the network"
        }

    def emit_telemetry(
        self,
        hubs: List[Tuple[str, float]],
        event_type: str = "rich_club.snapshot"
    ) -> Dict[str, Any]:
        """
        Generate telemetry event for rich-club snapshot.

        Args:
            hubs: List of (node_id, betweenness) tuples
            event_type: Event type string

        Returns:
            Telemetry event dict
        """
        if not hubs:
            mean_betweenness = 0.0
            max_betweenness = 0.0
        else:
            mean_betweenness = float(np.mean([score for _, score in hubs]))
            max_betweenness = float(max([score for _, score in hubs]))

        # Get details for top 10 hubs
        top_hubs = []
        for hub_id, score in hubs[:10]:
            details = self.get_hub_details(hub_id)
            if details:
                top_hubs.append({
                    'id': details['id'],
                    'name': details['name'],
                    'betweenness': round(score, 4),
                    'energy': details['energy']
                })

        return {
            'type': event_type,
            'timestamp': time.time(),
            'sample_size': self.config.sample_size,
            'hub_count': len(hubs),
            'top_hubs': top_hubs,
            'mean_betweenness': round(mean_betweenness, 4),
            'max_betweenness': round(max_betweenness, 4),
            'percentile_threshold': self.config.percentile_threshold
        }

    def invalidate_cache(self):
        """Invalidate cache after graph mutations."""
        self.betweenness_cache = {}

    def _is_cache_fresh(self) -> bool:
        """Check if cache is still fresh (within TTL)."""
        if not self.betweenness_cache:
            return False

        # Check if any cached value is still within TTL
        current_time = time.time()
        for _, timestamp in self.betweenness_cache.values():
            if (current_time - timestamp) < self.config.cache_ttl:
                return True

        return False

    def get_telemetry_stats(self) -> Dict[str, Any]:
        """Get analyzer telemetry stats."""
        return {
            'computations': self.computations,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_size': len(self.betweenness_cache),
            'cache_hit_rate': (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0.0
            )
        }
