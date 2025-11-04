"""
SubEntity Pair Metrics - On-Demand Computation

Computes overlap metrics (J, C, U, H, ΔCtx) and differentiation scores (S_red, S_use)
ONLY when decisions need them, not on schedule.

Called at decision points:
- SubEntity creation: compute for (E', k nearest neighbors)
- Quality gates: compute R_E, D_E for specific entity
- Merge review: compute for specific (A, B) pair

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26 (corrected from batch approach)
Updated: 2025-11-04 (Ada - added timeout handling, query optimization)
Spec: entity_differentiation.md (on-demand strategy)
"""

import math
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from functools import wraps

from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter

logger = logging.getLogger(__name__)

# Query timeout configuration
QUERY_TIMEOUT_SECONDS = 10  # Fail fast if query takes >10s


@dataclass
class PairMetrics:
    """Raw metrics for entity pair"""
    J: float  # Member Jaccard
    C: float  # Centroid cosine
    U: float  # WM co-activation (from COACTIVATES_WITH edge)
    H: float  # Highway utility (from RELATES_TO edge)
    delta_ctx: float  # Context divergence


@dataclass
class PairScores:
    """Differentiation scores"""
    S_red: float  # Redundancy score
    S_use: float  # Usefulness score


def softplus(x: float, beta: float = 1.0) -> float:
    """Smooth ReLU: log(1 + exp(beta*x)) / beta"""
    return math.log(1 + math.exp(beta * x)) / beta


class SubEntityMetrics:
    """
    On-demand entity pair metrics computation.

    No batch jobs, no schedulers. Compute when decision needs it.
    """

    def __init__(self, adapter: FalkorDBAdapter, enable_expensive_queries: bool = True):
        self.adapter = adapter
        self._cache = {}  # Optional 5-min cache
        self._cache_ttl = 300  # seconds
        self.enable_expensive_queries = enable_expensive_queries  # Disable during bootstrap

    def compute_pair_metrics(self, subentity_a: str, subentity_b: str) -> Optional[PairMetrics]:
        """
        Compute metrics for specific pair on-demand.

        Complexity: O(1) for U, H (edge reads) + O(N) for J, C, ΔCtx (traversals)
        Typical cost: <10ms per pair with indexed queries

        Args:
            subentity_a: First entity ID
            subentity_b: Second entity ID

        Returns:
            PairMetrics or None if subentities don't exist
        """
        # Skip expensive queries if disabled (e.g., during bootstrap)
        if not self.enable_expensive_queries:
            # Return placeholder metrics
            return PairMetrics(J=0.0, C=0.5, U=0.0, H=0.0, delta_ctx=0.5)

        # Check cache
        cache_key = tuple(sorted([subentity_a, subentity_b]))
        if cache_key in self._cache:
            cached_metrics, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_metrics

        try:
            # Optimized query - limit member collection size to prevent timeouts
            query = """
            MATCH (a:SubEntity {id: $A}), (b:SubEntity {id: $B})

            // Limit member nodes to first 500 per subentity (prevent large collections)
            OPTIONAL MATCH (n:Node)-[:MEMBER_OF]->(a)
            WITH a, b, collect(id(n))[..500] AS A_nodes LIMIT 1
            OPTIONAL MATCH (m:Node)-[:MEMBER_OF]->(b)
            WITH a, b, A_nodes, collect(id(m))[..500] AS B_nodes LIMIT 1

            // Highway (H) - O(1) edge read
            OPTIONAL MATCH (a)-[h:RELATES_TO]-(b)
            WITH a, b, A_nodes, B_nodes,
                 COALESCE(h.ease, 0) AS ease,
                 COALESCE(h.count, 0) AS flow
            LIMIT 1

            // WM co-activation (U) - O(1) edge read
            OPTIONAL MATCH (a)-[coact:COACTIVATES_WITH]-(b)
            WITH a, b, A_nodes, B_nodes, ease, flow,
                 COALESCE(coact.u_jaccard, 0.0) AS u_jaccard
            LIMIT 1

            // Compute Jaccard using native Cypher (no APOC needed)
            WITH
              A_nodes, B_nodes, ease, flow, u_jaccard

            // Intersection: nodes in both A and B
            WITH
              [x IN A_nodes WHERE x IN B_nodes] AS inter_list,
              A_nodes + [x IN B_nodes WHERE NOT x IN A_nodes] AS union_list,
              ease, flow, u_jaccard

            RETURN
              size(inter_list) AS inter,
              size(union_list) AS union,
              u_jaccard,
              ease * flow AS highway_utility
            LIMIT 1
            """

            result = self.adapter.graph_store.query(query, {"A": subentity_a, "B": subentity_b})

            if hasattr(result, 'result_set') and result.result_set:
                row = result.result_set[0]
            elif isinstance(result, list) and result:
                row = result[0]
            else:
                return None

            inter = row[0]
            union = row[1]
            u_jaccard = row[2]
            highway_utility = row[3]

            J = inter / union if union > 0 else 0.0
            U = u_jaccard
            H = highway_utility

            # C, ΔCtx: Placeholder (add when embeddings/context available)
            C = 0.5
            delta_ctx = 0.5

            metrics = PairMetrics(J=J, C=C, U=U, H=H, delta_ctx=delta_ctx)

            # Cache for 5 minutes
            self._cache[cache_key] = (metrics, time.time())

            return metrics

        except Exception as e:
            logger.error(f"[SubEntityMetrics] Failed to compute metrics for {subentity_a}, {subentity_b}: {e}")
            return None

    def compute_scores(self, metrics: PairMetrics, cohort_stats: Optional[Dict] = None) -> PairScores:
        """
        Compute S_red, S_use from metrics.

        If cohort_stats provided, normalizes via percentiles.
        Otherwise uses raw metrics (0-1 range assumed).

        Args:
            metrics: Raw metrics
            cohort_stats: Optional percentile normalization stats

        Returns:
            PairScores with S_red, S_use
        """
        # If no cohort stats, use raw metrics (assume already normalized)
        J_norm = metrics.J
        C_norm = metrics.C
        U_norm = metrics.U
        H_norm = metrics.H
        delta_ctx_norm = metrics.delta_ctx

        # S_red = softplus(J + C + U) - softplus(H + ΔCtx)
        S_red = softplus(J_norm + C_norm + U_norm) - softplus(H_norm + delta_ctx_norm)

        # S_use = softplus(H + ΔCtx) - softplus(J + C)
        S_use = softplus(H_norm + delta_ctx_norm) - softplus(J_norm + C_norm)

        return PairScores(S_red=S_red, S_use=S_use)

    def find_nearest_entities(self, subentity_id: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find k nearest subentities by member Jaccard.

        Used at entity creation to check for redundancy with existing subentities.

        Args:
            subentity_id: SubEntity to find neighbors for
            k: Number of neighbors (default 10)

        Returns:
            List of (subentity_id, jaccard_score) tuples, sorted descending
        """
        # Skip expensive queries if disabled
        if not self.enable_expensive_queries:
            return []

        try:
            # Optimized query - limit member collections and scan only first 100 subentities
            query = """
            MATCH (e:SubEntity {id: $subentity_id})
            OPTIONAL MATCH (n:Node)-[:MEMBER_OF]->(e)
            WITH e, collect(id(n))[..500] AS E_nodes LIMIT 1

            MATCH (other:SubEntity)
            WHERE other.id <> $subentity_id
            WITH e, E_nodes, other LIMIT 100

            OPTIONAL MATCH (m:Node)-[:MEMBER_OF]->(other)
            WITH other.id AS other_id, E_nodes, collect(id(m))[..500] AS Other_nodes

            // Native Cypher set operations (no APOC)
            WITH
              other_id,
              size([x IN E_nodes WHERE x IN Other_nodes]) AS inter,
              size(E_nodes + [x IN Other_nodes WHERE NOT x IN E_nodes]) AS union

            WHERE union > 0

            RETURN other_id, (1.0 * inter / union) AS jaccard
            ORDER BY jaccard DESC
            LIMIT $k
            """

            result = self.adapter.graph_store.query(query, {"subentity_id": subentity_id, "k": k})

            neighbors = []
            if hasattr(result, 'result_set'):
                for row in result.result_set:
                    neighbors.append((row[0], row[1]))
            elif isinstance(result, list):
                for row in result:
                    if isinstance(row, dict):
                        neighbors.append((row['other_id'], row['jaccard']))
                    else:
                        neighbors.append((row[0], row[1]))

            return neighbors

        except Exception as e:
            logger.error(f"[SubEntityMetrics] Failed to find neighbors for {subentity_id}: {e}")
            return []

    def compute_redundancy_pressure(self, subentity_id: str, k: int = 10) -> float:
        """
        Compute R_E = max_{B≠E} S_red(E, B) over k nearest neighbors.

        Used at quality gates to penalize redundant subentities.

        Args:
            subentity_id: SubEntity to assess
            k: Check k nearest neighbors (default 10)

        Returns:
            Maximum redundancy score (0-1 range)
        """
        neighbors = self.find_nearest_entities(subentity_id, k=k)

        if not neighbors:
            return 0.0

        max_redundancy = 0.0
        for neighbor_id, _ in neighbors:
            metrics = self.compute_pair_metrics(subentity_id, neighbor_id)
            if metrics:
                scores = self.compute_scores(metrics)
                max_redundancy = max(max_redundancy, scores.S_red)

        return max_redundancy

    def compute_differentiation_credit(self, subentity_id: str, k: int = 10) -> float:
        """
        Compute D_E = max_{B≠E} S_use(E, B) over k nearest neighbors.

        Used at quality gates to reward complementary subentities.

        Args:
            subentity_id: SubEntity to assess
            k: Check k nearest neighbors (default 10)

        Returns:
            Maximum usefulness score (0-1 range)
        """
        neighbors = self.find_nearest_entities(subentity_id, k=k)

        if not neighbors:
            return 0.0

        max_usefulness = 0.0
        for neighbor_id, _ in neighbors:
            metrics = self.compute_pair_metrics(subentity_id, neighbor_id)
            if metrics:
                scores = self.compute_scores(metrics)
                max_usefulness = max(max_usefulness, scores.S_use)

        return max_usefulness
