"""
Mode Community Detector - Multi-Resolution Community Detection for IFS Modes

Implements Steps 2-4 of emergent IFS modes:
- Step 2: Community detection using multi-resolution Leiden algorithm
- Step 3: Score communities for mode quality (cohesion, boundary, affect, procedural, persistence)
- Step 4: Create Mode nodes and AFFILIATES_WITH edges

Builds on role graph from RoleGraphBuilder to detect stable functional coalitions.

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: docs/specs/v2/subentity/emergent_ifs_modes.md §Steps 2-4
"""

import numpy as np
import logging
import json
import uuid
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial.distance import jensenshannon
from scipy.stats import rankdata

logger = logging.getLogger(__name__)


@dataclass
class CommunityCandidate:
    """Scored community candidate for mode creation."""
    member_indices: List[int]  # Indices into entity_ids array
    member_ids: List[str]  # SubEntity IDs
    q_mode: float  # Mode quality score [0, 1]
    cohesion: float  # Internal co-activation strength
    boundary_clarity: float  # Modularity contribution
    affect_consistency: float  # Affect homogeneity
    procedural_consistency: float  # Tool/outcome similarity
    persistence: float  # Stability over time


@dataclass
class ModeSignature:
    """Aggregated signature for a Mode."""
    arousal: float  # Mean arousal across members
    valence: float  # Mean valence across members
    tool_distribution: Dict[str, float]  # Aggregated tool usage
    outcome_distribution: Dict[str, float]  # Aggregated outcomes
    self_talk: str  # Canonical description


class ModeCommunityDetector:
    """
    Detect and create IFS Modes from SubEntity role graph.

    Uses multi-resolution community detection to find stable functional coalitions,
    scores them for mode quality, and creates Mode nodes for high-quality candidates.

    Example:
        >>> detector = ModeCommunityDetector(graph_name="citizen_felix")
        >>> candidates = detector.detect_and_score_communities(W, entity_ids)
        >>> for candidate in candidates:
        >>>     if candidate.q_mode > threshold:
        >>>         mode_id = detector.create_mode(candidate)
    """

    def __init__(self, graph_name: str):
        """
        Initialize mode community detector.

        Args:
            graph_name: FalkorDB graph name (e.g., "citizen_felix")
        """
        self.graph_name = graph_name

    def detect_communities(
        self,
        W: np.ndarray,
        entity_ids: List[str],
        min_community_size: int = 3
    ) -> List[List[int]]:
        """
        Detect communities using multi-resolution Leiden algorithm.

        Sweeps resolution parameter from 0.01 to 10, finds knee in modularity curve,
        and verifies partition persistence against historical data.

        Args:
            W: (n×n) weighted adjacency matrix from role graph
            entity_ids: List of SubEntity IDs matching matrix indices
            min_community_size: Minimum members per community (default 3)

        Returns:
            List of communities (each is list of SubEntity indices)

        Example:
            >>> W, entity_ids = role_graph_builder.build_role_graph()
            >>> communities = detector.detect_communities(W, entity_ids)
            >>> # communities = [[0, 2, 5], [1, 3, 4, 6], [7, 8]]
        """
        try:
            import igraph as ig
        except ImportError:
            logger.error("[ModeCommunity] igraph library not installed")
            raise ImportError("Install igraph: pip install python-igraph")

        n = W.shape[0]

        if n < min_community_size:
            logger.warning(f"[ModeCommunity] Only {n} SubEntities, need ≥{min_community_size}")
            return []

        logger.info(f"[ModeCommunity] Detecting communities for {self.graph_name}")
        logger.info(f"  Graph size: {n} SubEntities")

        # Build igraph from adjacency matrix
        # Create edge list from non-zero entries
        edges = []
        weights = []

        for i in range(n):
            for j in range(i + 1, n):
                if W[i, j] > 0:
                    edges.append((i, j))
                    weights.append(W[i, j])

        logger.info(f"  Edges: {len(edges)}")

        if len(edges) == 0:
            logger.warning(f"[ModeCommunity] No edges in role graph")
            return []

        g = ig.Graph(n=n, edges=edges)
        g.es['weight'] = weights

        # Multi-resolution sweep
        resolutions = np.logspace(-2, 1, 20)  # 0.01 to 10
        modularity_scores = []
        partitions = []

        logger.info(f"[ModeCommunity] Running multi-resolution sweep (20 resolutions)")

        for gamma in resolutions:
            try:
                partition = g.community_leiden(
                    weights='weight',
                    resolution_parameter=gamma,
                    n_iterations=10
                )
                Q = partition.modularity
                modularity_scores.append(Q)
                partitions.append(partition)
            except Exception as e:
                logger.warning(f"[ModeCommunity] Leiden failed at γ={gamma:.3f}: {e}")
                modularity_scores.append(0.0)
                partitions.append(None)

        # Find knee in modularity curve
        knee_idx = self._find_knee(modularity_scores)
        best_partition = partitions[knee_idx]

        if best_partition is None:
            logger.error(f"[ModeCommunity] Best partition is None at knee_idx={knee_idx}")
            return []

        logger.info(f"  Knee resolution: γ={resolutions[knee_idx]:.3f}, Q={modularity_scores[knee_idx]:.3f}")

        # Check partition persistence against historical
        historical_partition = self._load_historical_partition()

        if historical_partition is not None:
            nmi = self._normalized_mutual_info(best_partition.membership, historical_partition)
            persistence_threshold = self._get_persistence_threshold()

            logger.info(f"  Partition persistence: NMI={nmi:.3f}, threshold={persistence_threshold:.3f}")

            if nmi < persistence_threshold:
                # Partition unstable, use more conservative resolution (fewer communities)
                logger.info(f"  Partition unstable, shifting to more conservative resolution")
                knee_idx = max(0, knee_idx - 5)
                best_partition = partitions[knee_idx]
                logger.info(f"  New resolution: γ={resolutions[knee_idx]:.3f}, Q={modularity_scores[knee_idx]:.3f}")

        # Convert partition to community list
        communities = []
        num_clusters = max(best_partition.membership) + 1

        for cluster_id in range(num_clusters):
            community = [i for i, c in enumerate(best_partition.membership) if c == cluster_id]

            if len(community) >= min_community_size:
                communities.append(community)
            else:
                logger.debug(f"  Skipping small community (size={len(community)})")

        logger.info(f"[ModeCommunity] Detected {len(communities)} communities")
        for i, comm in enumerate(communities):
            logger.info(f"  Community {i}: {len(comm)} members")

        # Save partition for future persistence checks
        self._save_historical_partition(best_partition.membership)

        return communities

    def score_community(
        self,
        community: List[int],
        W: np.ndarray,
        entity_ids: List[str]
    ) -> CommunityCandidate:
        """
        Score community for mode quality using 5 factors.

        Q_mode = GM(cohesion, boundary, affect, procedural, persistence)

        All factors are percentile-ranked within citizen for comparability.

        Args:
            community: List of SubEntity indices
            W: Adjacency matrix
            entity_ids: SubEntity IDs

        Returns:
            CommunityCandidate with Q_mode and component scores
        """
        member_ids = [entity_ids[i] for i in community]

        logger.info(f"[ModeCommunity] Scoring community: {len(community)} members")

        # 1. Cohesion: Average internal U (co-activation)
        cohesion = self._compute_cohesion(community, entity_ids)
        cohesion_percentile = self._percentile_rank(cohesion, self._get_all_cohesion_values())

        # 2. Boundary clarity: Modularity contribution
        boundary = self._compute_boundary_clarity(community, W)
        boundary_percentile = self._percentile_rank(boundary, self._get_all_boundary_values())

        # 3. Affect consistency: Low variance in arousal/valence
        affect_consistency = self._compute_affect_consistency(member_ids)
        affect_percentile = self._percentile_rank(affect_consistency, self._get_all_affect_consistencies())

        # 4. Procedural consistency: Low JSD for tool/outcome distributions
        procedural_consistency = self._compute_procedural_consistency(member_ids)
        procedural_percentile = self._percentile_rank(procedural_consistency, self._get_all_procedural_consistencies())

        # 5. Persistence: NMI with historical communities
        persistence = self._compute_persistence(community)
        persistence_percentile = self._percentile_rank(persistence, self._get_all_persistence_values())

        # Geometric mean
        q_mode = (
            cohesion_percentile *
            boundary_percentile *
            affect_percentile *
            procedural_percentile *
            persistence_percentile
        ) ** (1/5)

        logger.info(f"  Q_mode: {q_mode:.3f}")
        logger.info(f"    Cohesion: {cohesion_percentile:.3f} (raw: {cohesion:.3f})")
        logger.info(f"    Boundary: {boundary_percentile:.3f} (raw: {boundary:.3f})")
        logger.info(f"    Affect: {affect_percentile:.3f} (raw: {affect_consistency:.3f})")
        logger.info(f"    Procedural: {procedural_percentile:.3f} (raw: {procedural_consistency:.3f})")
        logger.info(f"    Persistence: {persistence_percentile:.3f} (raw: {persistence:.3f})")

        return CommunityCandidate(
            member_indices=community,
            member_ids=member_ids,
            q_mode=q_mode,
            cohesion=cohesion,
            boundary_clarity=boundary,
            affect_consistency=affect_consistency,
            procedural_consistency=procedural_consistency,
            persistence=persistence
        )

    def detect_and_score_communities(
        self,
        W: np.ndarray,
        entity_ids: List[str]
    ) -> List[CommunityCandidate]:
        """
        Detect communities and score all candidates.

        Convenience method combining detect_communities() and score_community().

        Args:
            W: Adjacency matrix from role graph
            entity_ids: SubEntity IDs

        Returns:
            List of scored CommunityCandidate objects
        """
        communities = self.detect_communities(W, entity_ids)

        candidates = []
        for i, community in enumerate(communities):
            logger.info(f"[ModeCommunity] Scoring community {i+1}/{len(communities)}")
            candidate = self.score_community(community, W, entity_ids)
            candidates.append(candidate)

        # Sort by Q_mode (best first)
        candidates.sort(key=lambda c: c.q_mode, reverse=True)

        return candidates

    def create_mode(
        self,
        candidate: CommunityCandidate,
        mode_threshold: Optional[float] = None
    ) -> Optional[str]:
        """
        Create Mode node and AFFILIATES_WITH edges if candidate exceeds threshold.

        Args:
            candidate: Scored community candidate
            mode_threshold: Q_mode threshold (default: learned Q80 or 0.6 cold start)

        Returns:
            mode_id if created, None if below threshold
        """
        if mode_threshold is None:
            mode_threshold = self._get_mode_threshold()

        if candidate.q_mode < mode_threshold:
            logger.info(f"[ModeCommunity] Candidate Q_mode={candidate.q_mode:.3f} < threshold={mode_threshold:.3f}, skipping")
            return None

        logger.info(f"[ModeCommunity] Creating Mode (Q_mode={candidate.q_mode:.3f})")

        # Compute mode signature
        signature = self._compute_mode_signature(candidate.member_ids)

        # Generate mode ID
        mode_id = f"{self.graph_name.replace('citizen_', '')}_mode_{uuid.uuid4().hex[:8]}"

        # Create Mode node in FalkorDB
        self._create_mode_node(mode_id, candidate, signature)

        # Create AFFILIATES_WITH edges
        self._create_affiliation_edges(mode_id, candidate)

        logger.info(f"  Created Mode: {mode_id}")
        logger.info(f"  Members: {len(candidate.member_ids)}")
        logger.info(f"  Signature: arousal={signature.arousal:.2f}, valence={signature.valence:.2f}")

        return mode_id

    # === Helper Methods: Community Detection ===

    def _find_knee(self, scores: List[float]) -> int:
        """Find knee/elbow in modularity curve using kneedle algorithm."""
        try:
            from kneed import KneeLocator
            x = np.arange(len(scores))
            kl = KneeLocator(x, scores, curve='concave', direction='increasing')
            return kl.knee if kl.knee is not None else len(scores) // 2
        except ImportError:
            logger.warning("[ModeCommunity] kneed library not installed, using midpoint")
            return len(scores) // 2
        except Exception as e:
            logger.warning(f"[ModeCommunity] Knee detection failed: {e}, using midpoint")
            return len(scores) // 2

    def _normalized_mutual_info(self, partition_a: List[int], partition_b: List[int]) -> float:
        """Compute Normalized Mutual Information between two partitions."""
        try:
            from sklearn.metrics import normalized_mutual_info_score
            return float(normalized_mutual_info_score(partition_a, partition_b))
        except ImportError:
            logger.warning("[ModeCommunity] sklearn not installed, cannot compute NMI")
            return 0.5  # Neutral
        except Exception as e:
            logger.warning(f"[ModeCommunity] NMI computation failed: {e}")
            return 0.5

    def _load_historical_partition(self) -> Optional[List[int]]:
        """Load partition from 1 week ago for persistence check."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Query for historical community memberships
        query = """
        MATCH (e:SubEntity)
        WHERE e.last_mode_assignment IS NOT NULL
        RETURN e.id AS entity_id, e.last_mode_assignment AS cluster_id
        ORDER BY e.id
        """

        try:
            result = graph.query(query)

            if not result or not result.result_set:
                return None

            # Build partition (cluster IDs for each SubEntity)
            partition = [row[1] for row in result.result_set]

            return partition if len(partition) > 0 else None

        except Exception as e:
            logger.debug(f"[ModeCommunity] No historical partition found: {e}")
            return None

    def _save_historical_partition(self, partition: List[int]) -> None:
        """Save current partition for future persistence checks."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Update SubEntities with cluster assignments
        query = """
        UNWIND $assignments AS a
        MATCH (e:SubEntity {id: a.entity_id})
        SET e.last_mode_assignment = a.cluster_id,
            e.last_partition_ts = datetime()
        """

        try:
            # Get entity IDs (need to load from graph for correct ordering)
            entities_query = "MATCH (e:SubEntity) RETURN e.id ORDER BY e.id"
            entities_result = graph.query(entities_query)

            if not entities_result or not entities_result.result_set:
                return

            entity_ids = [row[0] for row in entities_result.result_set]

            assignments = [
                {"entity_id": entity_ids[i], "cluster_id": cluster_id}
                for i, cluster_id in enumerate(partition)
                if i < len(entity_ids)
            ]

            graph.query(query, {"assignments": assignments})

            logger.debug(f"[ModeCommunity] Saved partition for {len(assignments)} SubEntities")

        except Exception as e:
            logger.warning(f"[ModeCommunity] Failed to save historical partition: {e}")

    def _get_persistence_threshold(self) -> float:
        """Get learned persistence threshold or default (boot contour: 0.6)."""
        # TODO: Load learned threshold from citizen config
        return 0.6  # Boot contour

    # === Helper Methods: Community Scoring ===

    def _compute_cohesion(self, community: List[int], entity_ids: List[str]) -> float:
        """Compute average internal U (co-activation) for community."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        member_ids = [entity_ids[i] for i in community]

        # Query internal COACTIVATES_WITH edges
        query = """
        UNWIND $members AS m1
        UNWIND $members AS m2
        MATCH (a:SubEntity {id: m1})-[r:COACTIVATES_WITH]-(b:SubEntity {id: m2})
        WHERE m1 < m2
        RETURN r.u_jaccard AS u
        """

        try:
            result = graph.query(query, {"members": member_ids})

            if not result or not result.result_set:
                return 0.0

            u_values = [float(row[0]) for row in result.result_set if row[0] is not None]

            return np.mean(u_values) if u_values else 0.0

        except Exception as e:
            logger.warning(f"[ModeCommunity] Cohesion computation failed: {e}")
            return 0.0

    def _compute_boundary_clarity(self, community: List[int], W: np.ndarray) -> float:
        """Compute modularity contribution (boundary clarity)."""
        n = W.shape[0]

        # Internal weight
        internal_weight = 0.0
        for i in community:
            for j in community:
                if i < j:
                    internal_weight += W[i, j]

        # Total weight
        total_weight = W.sum() / 2  # Divide by 2 (symmetric)

        if total_weight == 0:
            return 0.0

        # Expected internal weight
        degree_sum = sum(W[i, :].sum() for i in community)
        expected_internal = (degree_sum / (2 * total_weight)) ** 2

        # Modularity contribution
        boundary = (internal_weight / total_weight) - expected_internal

        return max(0.0, boundary)  # Clamp to [0, ∞)

    def _compute_affect_consistency(self, member_ids: List[str]) -> float:
        """Compute affect consistency (1 - variance in arousal/valence)."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Query affect EMAs
        query = """
        UNWIND $members AS m
        MATCH (e:SubEntity {id: m})
        RETURN e.arousal_ema AS arousal, e.valence_ema AS valence
        """

        try:
            result = graph.query(query, {"members": member_ids})

            if not result or not result.result_set:
                return 0.5  # Neutral

            arousals = [float(row[0]) for row in result.result_set if row[0] is not None]
            valences = [float(row[1]) for row in result.result_set if row[1] is not None]

            if not arousals or not valences:
                return 0.5

            arousal_var = np.var(arousals)
            valence_var = np.var(valences)

            # Invert: high consistency = low variance
            consistency = 1.0 - (arousal_var + valence_var) / 2.0

            return max(0.0, min(1.0, consistency))

        except Exception as e:
            logger.warning(f"[ModeCommunity] Affect consistency computation failed: {e}")
            return 0.5

    def _compute_procedural_consistency(self, member_ids: List[str]) -> float:
        """Compute procedural consistency (1 - mean JSD for tool distributions)."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Query tool distributions
        query = """
        UNWIND $members AS m
        MATCH (e:SubEntity {id: m})
        RETURN e.id AS id, e.tool_usage_counts AS tool_counts
        """

        try:
            result = graph.query(query, {"members": member_ids})

            if not result or not result.result_set:
                return 0.5  # Neutral

            # Parse tool distributions
            tool_dists = []
            for row in result.result_set:
                tool_counts_str = row[1]
                if tool_counts_str:
                    tool_counts = json.loads(tool_counts_str)
                    total = sum(tool_counts.values())
                    if total > 0:
                        tool_dist = {k: v / total for k, v in tool_counts.items()}
                        tool_dists.append(tool_dist)

            if len(tool_dists) < 2:
                return 0.5  # Need at least 2 for comparison

            # Compute mean tool distribution
            all_tools = set()
            for dist in tool_dists:
                all_tools.update(dist.keys())

            if not all_tools:
                return 0.5

            sorted_tools = sorted(all_tools)

            # Build vectors
            smooth = 1e-10
            vectors = []
            for dist in tool_dists:
                vec = np.array([dist.get(tool, 0.0) + smooth for tool in sorted_tools])
                vec = vec / vec.sum()
                vectors.append(vec)

            mean_dist = np.mean(vectors, axis=0)

            # Compute JSD from each distribution to mean
            jsds = [jensenshannon(vec, mean_dist) for vec in vectors]

            # Invert: high consistency = low divergence
            consistency = 1.0 - np.mean(jsds)

            return max(0.0, min(1.0, consistency))

        except Exception as e:
            logger.warning(f"[ModeCommunity] Procedural consistency computation failed: {e}")
            return 0.5

    def _compute_persistence(self, community: List[int]) -> float:
        """Compute NMI overlap with historical communities."""
        # For now, return neutral value (no historical data yet)
        # TODO: Implement historical community tracking and NMI computation
        return 0.5

    def _percentile_rank(self, value: float, cohort: List[float]) -> float:
        """Compute percentile rank of value within cohort."""
        if not cohort or len(cohort) == 1:
            return 0.5  # Neutral

        ranks = rankdata(cohort, method='average')
        value_rank = rankdata(cohort + [value], method='average')[-1]

        # Normalize to [0, 1]
        percentile = (value_rank - 1.0) / (len(cohort))

        return max(0.0, min(1.0, percentile))

    def _get_all_cohesion_values(self) -> List[float]:
        """Get historical cohesion values for percentile ranking."""
        # TODO: Load from historical mode quality tracking
        # For now, return default range
        return [0.1, 0.3, 0.5, 0.7, 0.9]

    def _get_all_boundary_values(self) -> List[float]:
        """Get historical boundary clarity values."""
        return [0.05, 0.1, 0.15, 0.2, 0.25]

    def _get_all_affect_consistencies(self) -> List[float]:
        """Get historical affect consistency values."""
        return [0.3, 0.5, 0.7, 0.85, 0.95]

    def _get_all_procedural_consistencies(self) -> List[float]:
        """Get historical procedural consistency values."""
        return [0.3, 0.5, 0.7, 0.85, 0.95]

    def _get_all_persistence_values(self) -> List[float]:
        """Get historical persistence (NMI) values."""
        return [0.2, 0.4, 0.6, 0.8, 0.95]

    # === Helper Methods: Mode Creation ===

    def _get_mode_threshold(self) -> float:
        """Get Q_mode threshold (learned Q80 or 0.6 cold start)."""
        # TODO: Load learned Q80 from historical mode qualities
        return 0.6  # Boot contour (cold start)

    def _compute_mode_signature(self, member_ids: List[str]) -> ModeSignature:
        """Compute aggregated signature for Mode."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Query member features
        query = """
        UNWIND $members AS m
        MATCH (e:SubEntity {id: m})
        RETURN
            e.arousal_ema AS arousal,
            e.valence_ema AS valence,
            e.tool_usage_counts AS tool_counts,
            e.outcome_distribution AS outcome_dist,
            e.id AS description
        """

        result = graph.query(query, {"members": member_ids})

        if not result or not result.result_set:
            # Return neutral signature
            return ModeSignature(
                arousal=0.5,
                valence=0.0,
                tool_distribution={},
                outcome_distribution={},
                self_talk="Unknown mode"
            )

        # Aggregate affect
        arousals = [float(row[0]) for row in result.result_set if row[0] is not None]
        valences = [float(row[1]) for row in result.result_set if row[1] is not None]

        mean_arousal = np.mean(arousals) if arousals else 0.5
        mean_valence = np.mean(valences) if valences else 0.0

        # Aggregate tool distributions
        all_tools = {}
        tool_count = 0

        for row in result.result_set:
            tool_counts_str = row[2]
            if tool_counts_str:
                tool_counts = json.loads(tool_counts_str)
                for tool, count in tool_counts.items():
                    all_tools[tool] = all_tools.get(tool, 0.0) + count
                tool_count += 1

        # Normalize
        total_tools = sum(all_tools.values())
        tool_dist = {k: v / total_tools for k, v in all_tools.items()} if total_tools > 0 else {}

        # Aggregate outcome distributions
        all_outcomes = {}
        outcome_count = 0

        for row in result.result_set:
            outcome_dist_str = row[3]
            if outcome_dist_str:
                outcome_dist = json.loads(outcome_dist_str)
                for outcome, prob in outcome_dist.items():
                    all_outcomes[outcome] = all_outcomes.get(outcome, 0.0) + prob
                outcome_count += 1

        # Normalize
        outcome_dist = {k: v / outcome_count for k, v in all_outcomes.items()} if outcome_count > 0 else {}

        # Select self_talk (first member's description for now)
        # TODO: Use embedding centroid to find most representative description
        self_talk = result.result_set[0][4] if result.result_set[0][4] else "Unknown mode"

        return ModeSignature(
            arousal=mean_arousal,
            valence=mean_valence,
            tool_distribution=tool_dist,
            outcome_distribution=outcome_dist,
            self_talk=self_talk
        )

    def _create_mode_node(
        self,
        mode_id: str,
        candidate: CommunityCandidate,
        signature: ModeSignature
    ) -> None:
        """Create Mode node in FalkorDB."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # Serialize signature
        signature_json = json.dumps({
            "affect": {"arousal": signature.arousal, "valence": signature.valence},
            "tools": signature.tool_distribution,
            "outcomes": signature.outcome_distribution,
            "self_talk": signature.self_talk
        })

        query = """
        CREATE (m:Mode {
            id: $mode_id,
            citizen_id: $citizen,
            level: 'IFS',
            status: 'candidate',
            signature: $signature,
            q_mode: $q_mode,
            cohesion: $cohesion,
            boundary_clarity: $boundary,
            affect_consistency: $affect,
            procedural_consistency: $procedural,
            persistence: $persistence,
            member_count: $member_count,
            created_at: datetime(),
            valid_at: datetime()
        })
        """

        graph.query(query, {
            "mode_id": mode_id,
            "citizen": self.graph_name.replace("citizen_", ""),
            "signature": signature_json,
            "q_mode": candidate.q_mode,
            "cohesion": candidate.cohesion,
            "boundary": candidate.boundary_clarity,
            "affect": candidate.affect_consistency,
            "procedural": candidate.procedural_consistency,
            "persistence": candidate.persistence,
            "member_count": len(candidate.member_ids)
        })

    def _create_affiliation_edges(
        self,
        mode_id: str,
        candidate: CommunityCandidate
    ) -> None:
        """Create AFFILIATES_WITH edges from SubEntities to Mode."""
        from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

        graph = get_falkordb_graph(self.graph_name)

        # For now, use uniform weights (centrality × WM share requires embeddings)
        # TODO: Implement medoid proximity and WM share EMA

        edges = []
        for entity_id in candidate.member_ids:
            edges.append({
                "entity_id": entity_id,
                "mode_id": mode_id,
                "weight": 1.0 / len(candidate.member_ids),  # Uniform for now
                "formation_trigger": "community_detection"
            })

        query = """
        UNWIND $edges AS e
        MATCH (subentity:SubEntity {id: e.entity_id})
        MATCH (mode:Mode {id: e.mode_id})
        CREATE (subentity)-[:AFFILIATES_WITH {
            weight: e.weight,
            formation_trigger: e.formation_trigger,
            created_at: datetime(),
            valid_at: datetime()
        }]->(mode)
        """

        graph.query(query, {"edges": edges})

        logger.debug(f"[ModeCommunity] Created {len(edges)} AFFILIATES_WITH edges")
