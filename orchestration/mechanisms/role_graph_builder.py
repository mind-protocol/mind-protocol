"""
Role Graph Builder - Multi-Signal SubEntity Similarity

Builds weighted adjacency matrix for SubEntities using:
- U metric (WM co-activation from COACTIVATES_WITH edges)
- Highway ease (from RELATES_TO edges)
- Affect similarity (from arousal/valence EMAs)
- Tool/outcome overlap (from context distributions)

Foundation for emergent IFS modes community detection.

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: docs/specs/v2/subentity/emergent_ifs_modes.md §Step 1
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial.distance import jensenshannon
from scipy.stats import rankdata

logger = logging.getLogger(__name__)


@dataclass
class SubEntityFeatures:
    """Features extracted from SubEntity for role graph building."""
    id: str
    arousal_ema: float  # [0, 1]
    valence_ema: float  # [-1, 1]
    tool_distribution: Dict[str, float]  # {tool_name: probability}
    outcome_distribution: Dict[str, float]  # {outcome: probability}


@dataclass
class EdgeFeatures:
    """Features for SubEntity pair (from graph edges)."""
    u_jaccard: float  # WM co-activation [0, 1]
    ease: float  # Highway ease (0 if no highway)


class RoleGraphBuilder:
    """
    Builds weighted role graph over SubEntities.

    Role graph encodes "functional similarity" between SubEntities using
    multiple signals: co-activation, highway ease, affect similarity, tool overlap.

    Example:
        >>> builder = RoleGraphBuilder(graph_name="citizen_felix")
        >>> W, entity_ids = builder.build_role_graph()
        >>> # W is (n×n) adjacency matrix, entity_ids maps indices to SubEntity IDs
    """

    def __init__(self, graph_name: str):
        """
        Initialize role graph builder.

        Args:
            graph_name: FalkorDB graph name (e.g., "citizen_felix")
        """
        self.graph_name = graph_name

    def build_role_graph(
        self,
        min_u_threshold: float = 0.01,
        percentile_normalize: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Build weighted adjacency matrix for SubEntities.

        Weight formula (from spec):
            W_AB = U_AB × (1 + ease_AB) × (1 + affect_sim_AB) × (1 + tool_overlap_AB)

        All components are percentile-normalized (citizen-local) if percentile_normalize=True.

        Args:
            min_u_threshold: Minimum U (co-activation) to include edge (default 0.01)
            percentile_normalize: Apply percentile normalization to components (default True)

        Returns:
            Tuple of (W, entity_ids)
            - W: (n×n) symmetric adjacency matrix
            - entity_ids: List[str] mapping matrix indices to SubEntity IDs

        Example:
            >>> W, entities = builder.build_role_graph()
            >>> # W[i,j] = functional similarity between entities[i] and entities[j]
            >>> # W is symmetric: W[i,j] == W[j,i]
        """
        # Step 1: Load SubEntity features
        logger.info(f"[RoleGraph] Building role graph for {self.graph_name}")
        entities = self._load_subentity_features()
        n = len(entities)
        logger.info(f"[RoleGraph] Loaded {n} SubEntities")

        if n == 0:
            logger.warning(f"[RoleGraph] No SubEntities found in {self.graph_name}")
            return np.zeros((0, 0)), []

        # Build index mapping
        entity_ids = [e.id for e in entities]
        entity_map = {e.id: i for i, e in enumerate(entities)}

        # Step 2: Initialize adjacency matrix
        W = np.zeros((n, n))

        # Step 3: Compute raw component values for all pairs
        u_values = []
        ease_values = []
        affect_sim_values = []
        tool_overlap_values = []

        # Pre-compute all pairwise similarities (for percentile normalization)
        logger.info(f"[RoleGraph] Computing pairwise similarities for {n*(n-1)//2} pairs")

        for i in range(n):
            for j in range(i + 1, n):
                A = entities[i]
                B = entities[j]

                # U: WM co-activation
                u = self._get_u_metric(A.id, B.id)

                # Skip pairs with very low co-activation (noise reduction)
                if u < min_u_threshold:
                    continue

                # Ease: Highway strength
                ease = self._get_highway_ease(A.id, B.id)

                # Affect similarity
                affect_sim = self._compute_affect_similarity(A, B)

                # Tool/outcome overlap
                tool_overlap = self._compute_tool_overlap(A, B)

                # Store for percentile normalization
                u_values.append(u)
                ease_values.append(ease)
                affect_sim_values.append(affect_sim)
                tool_overlap_values.append(tool_overlap)

        logger.info(f"[RoleGraph] Found {len(u_values)} non-zero similarity pairs")

        if len(u_values) == 0:
            logger.warning(f"[RoleGraph] No SubEntity pairs with U > {min_u_threshold}")
            return np.zeros((n, n)), entity_ids

        # Step 4: Percentile normalize components (citizen-local)
        if percentile_normalize:
            logger.info(f"[RoleGraph] Applying percentile normalization")
            u_ranks = self._percentile_normalize(u_values)
            ease_ranks = self._percentile_normalize(ease_values)
            affect_ranks = self._percentile_normalize(affect_sim_values)
            tool_ranks = self._percentile_normalize(tool_overlap_values)
        else:
            # Use raw values (already in [0, 1] range)
            u_ranks = u_values
            ease_ranks = ease_values
            affect_ranks = affect_sim_values
            tool_ranks = tool_overlap_values

        # Step 5: Build weighted adjacency matrix
        logger.info(f"[RoleGraph] Building weighted adjacency matrix")
        pair_idx = 0

        for i in range(n):
            for j in range(i + 1, n):
                A = entities[i]
                B = entities[j]

                # U: WM co-activation
                u = self._get_u_metric(A.id, B.id)

                if u < min_u_threshold:
                    continue

                # Get normalized component values
                u_norm = u_ranks[pair_idx]
                ease_norm = ease_ranks[pair_idx]
                affect_norm = affect_ranks[pair_idx]
                tool_norm = tool_ranks[pair_idx]

                # Combine using spec formula
                # W_AB = U_AB × (1 + ease_AB) × (1 + affect_sim_AB) × (1 + tool_overlap_AB)
                weight = u_norm * (1 + ease_norm) * (1 + affect_norm) * (1 + tool_norm)

                # Symmetric assignment
                W[i, j] = weight
                W[j, i] = weight

                pair_idx += 1

        # Step 6: Compute statistics
        non_zero = np.count_nonzero(W)
        density = non_zero / (n * (n - 1))  # Exclude diagonal
        mean_weight = np.mean(W[W > 0]) if non_zero > 0 else 0.0

        logger.info(f"[RoleGraph] Graph built:")
        logger.info(f"  Nodes: {n}")
        logger.info(f"  Edges: {non_zero // 2}")  # Divide by 2 (symmetric)
        logger.info(f"  Density: {density:.3f}")
        logger.info(f"  Mean weight: {mean_weight:.3f}")

        return W, entity_ids

    def _load_subentity_features(self) -> List[SubEntityFeatures]:
        """
        Load SubEntity features from FalkorDB.

        Returns:
            List of SubEntityFeatures with affect EMAs and context distributions

        Raises:
            Exception if FalkorDB connection fails
        """
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Query SubEntities with all required features
        query = """
        MATCH (e:SubEntity)
        RETURN
            e.id AS id,
            e.arousal_ema AS arousal,
            e.valence_ema AS valence,
            e.tool_usage_counts AS tool_counts,
            e.outcome_distribution AS outcome_dist
        """

        result = graph.query(query)

        if not result or not result.result_set:
            return []

        entities = []
        for row in result.result_set:
            entity_id = row[0]
            arousal = float(row[1]) if row[1] is not None else 0.0
            valence = float(row[2]) if row[2] is not None else 0.0

            # Parse tool counts (JSON string)
            import json
            tool_counts = json.loads(row[3]) if row[3] else {}
            outcome_dist = json.loads(row[4]) if row[4] else {}

            # Normalize tool counts to distribution
            total_tools = sum(tool_counts.values()) if tool_counts else 0
            tool_dist = {}
            if total_tools > 0:
                tool_dist = {k: v / total_tools for k, v in tool_counts.items()}

            entities.append(SubEntityFeatures(
                id=entity_id,
                arousal_ema=arousal,
                valence_ema=valence,
                tool_distribution=tool_dist,
                outcome_distribution=outcome_dist
            ))

        return entities

    def _get_u_metric(self, entity_a: str, entity_b: str) -> float:
        """
        Get U metric (WM co-activation) from COACTIVATES_WITH edge.

        Args:
            entity_a: First SubEntity ID
            entity_b: Second SubEntity ID

        Returns:
            u_jaccard ∈ [0, 1], or 0.0 if no edge exists
        """
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Ensure A < B lexicographically (undirected edge semantics)
        A, B = (entity_a, entity_b) if entity_a < entity_b else (entity_b, entity_a)

        query = """
        MATCH (a:SubEntity {id: $A})-[r:COACTIVATES_WITH]->(b:SubEntity {id: $B})
        RETURN r.u_jaccard AS u
        """

        result = graph.query(query, {"A": A, "B": B})

        if result and result.result_set and len(result.result_set) > 0:
            u = result.result_set[0][0]
            return float(u) if u is not None else 0.0

        return 0.0

    def _get_highway_ease(self, entity_a: str, entity_b: str) -> float:
        """
        Get highway ease from RELATES_TO edge.

        Args:
            entity_a: First SubEntity ID
            entity_b: Second SubEntity ID

        Returns:
            ease ∈ [0, 1], or 0.0 if no highway exists
        """
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Try both directions (RELATES_TO can be directional)
        query = """
        MATCH (a:SubEntity {id: $A})-[r:RELATES_TO]-(b:SubEntity {id: $B})
        RETURN r.ease AS ease
        LIMIT 1
        """

        result = graph.query(query, {"A": entity_a, "B": entity_b})

        if result and result.result_set and len(result.result_set) > 0:
            ease = result.result_set[0][0]
            return float(ease) if ease is not None else 0.0

        return 0.0

    def _compute_affect_similarity(
        self,
        entity_a: SubEntityFeatures,
        entity_b: SubEntityFeatures
    ) -> float:
        """
        Compute affect similarity between two SubEntities.

        Formula from spec:
            affect_sim = 1 - |arousal_A - arousal_B| - |valence_A - valence_B|

        Clamped to [0, 1].

        Args:
            entity_a: First SubEntity features
            entity_b: Second SubEntity features

        Returns:
            Similarity ∈ [0, 1]
        """
        arousal_diff = abs(entity_a.arousal_ema - entity_b.arousal_ema)
        valence_diff = abs(entity_a.valence_ema - entity_b.valence_ema)

        similarity = 1.0 - arousal_diff - valence_diff

        return max(0.0, min(1.0, similarity))

    def _compute_tool_overlap(
        self,
        entity_a: SubEntityFeatures,
        entity_b: SubEntityFeatures
    ) -> float:
        """
        Compute tool/outcome distribution overlap using Jensen-Shannon divergence.

        Formula from spec:
            tool_overlap = 1 - JSD(tool_dist_A, tool_dist_B)

        Args:
            entity_a: First SubEntity features
            entity_b: Second SubEntity features

        Returns:
            Overlap ∈ [0, 1]
        """
        # Combine tool distributions from both entities to get all keys
        all_tools = set(entity_a.tool_distribution.keys()) | set(entity_b.tool_distribution.keys())

        if not all_tools:
            # No tool data for either entity
            return 0.5  # Neutral similarity

        # Build probability vectors (with smoothing for missing tools)
        smooth = 1e-10
        dist_a = np.array([entity_a.tool_distribution.get(tool, 0.0) + smooth for tool in sorted(all_tools)])
        dist_b = np.array([entity_b.tool_distribution.get(tool, 0.0) + smooth for tool in sorted(all_tools)])

        # Normalize
        dist_a = dist_a / dist_a.sum()
        dist_b = dist_b / dist_b.sum()

        # Jensen-Shannon divergence
        jsd = jensenshannon(dist_a, dist_b)

        # Convert to similarity (1 - JSD)
        overlap = 1.0 - jsd

        return max(0.0, min(1.0, overlap))

    def _percentile_normalize(self, values: List[float]) -> List[float]:
        """
        Percentile-normalize values to [0, 1] range (citizen-local).

        Args:
            values: List of raw values

        Returns:
            List of percentile ranks ∈ [0, 1]

        Example:
            >>> values = [0.1, 0.5, 0.3, 0.9]
            >>> normalized = self._percentile_normalize(values)
            >>> # normalized ≈ [0.0, 0.5, 0.25, 1.0]
        """
        if not values:
            return []

        # Use scipy.stats.rankdata with 'average' method
        # Returns ranks starting from 1
        ranks = rankdata(values, method='average')

        # Normalize to [0, 1]
        min_rank = 1.0
        max_rank = len(values)

        if max_rank == min_rank:
            # All values the same
            return [0.5] * len(values)

        normalized = [(r - min_rank) / (max_rank - min_rank) for r in ranks]

        return normalized
