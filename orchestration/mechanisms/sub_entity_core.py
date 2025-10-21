"""
Sub-Entity Core Data Structures

Provides the foundational classes for sub-entity traversal:
- SubEntity: Main entity class with extent, frontier, energy tracking
- EntityExtentCentroid: O(1) online centroid + semantic dispersion
- ROITracker: Rolling ROI statistics (Q1/Q3/IQR for convergence)
- QuantileTracker: General rolling quantiles for integration/size tracking

Author: AI #1
Created: 2025-10-20
Dependencies: numpy
Zero-Constants: All thresholds derived from rolling statistics
"""

import numpy as np
from typing import Set, Dict, Optional
from collections import deque


class EntityExtentCentroid:
    """
    Online centroid + dispersion tracking for semantic diversity measurement.

    O(1) updates as nodes activate/deactivate (not O(m²) pairwise).
    Dispersion = mean(1 - cos(node_embedding, centroid))

    Low dispersion → narrow semantic extent → completeness hunger activates
    High dispersion → broad semantic extent → completeness satisfied
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Initialize empty centroid.

        Args:
            embedding_dim: Embedding dimension (default 768 for all-mpnet-base-v2)
        """
        self.n = 0
        self.centroid = np.zeros(embedding_dim)
        self.dispersion = 0.0
        self.active_embeddings = []  # For dispersion recomputation

    def add_node(self, embedding: np.ndarray):
        """
        Node became active - update centroid incrementally.

        Args:
            embedding: Node embedding vector (768-dim)
        """
        if self.n == 0:
            self.centroid = embedding.copy()
            self.n = 1
            self.active_embeddings = [embedding]
            self.dispersion = 0.0
        else:
            # Incremental centroid update: C_new = (n*C_old + e) / (n+1)
            self.centroid = ((self.n * self.centroid) + embedding) / (self.n + 1)
            self.n += 1
            self.active_embeddings.append(embedding)

            # Renormalize centroid to unit length for cosine distance
            norm = np.linalg.norm(self.centroid)
            if norm > 1e-9:
                self.centroid = self.centroid / norm

            # Recompute dispersion: mean(1 - cos(e, centroid))
            self._update_dispersion()

    def remove_node(self, embedding: np.ndarray):
        """
        Node deactivated - update centroid.

        Args:
            embedding: Node embedding vector (768-dim)
        """
        if self.n == 0:
            return

        if self.n == 1:
            # Last node removed - reset to empty
            self.centroid = np.zeros_like(self.centroid)
            self.n = 0
            self.active_embeddings = []
            self.dispersion = 0.0
        else:
            # Remove from active list
            self.active_embeddings = [e for e in self.active_embeddings
                                     if not np.allclose(e, embedding)]
            self.n = len(self.active_embeddings)

            # Recompute centroid from scratch (safer than decremental)
            if self.n > 0:
                self.centroid = np.mean(self.active_embeddings, axis=0)
                norm = np.linalg.norm(self.centroid)
                if norm > 1e-9:
                    self.centroid = self.centroid / norm
                self._update_dispersion()
            else:
                self.centroid = np.zeros_like(self.centroid)
                self.dispersion = 0.0

    def distance_to(self, embedding: np.ndarray) -> float:
        """
        Compute semantic distance from target to current extent centroid.

        Used for completeness hunger: favor nodes distant from current extent.

        Args:
            embedding: Target node embedding

        Returns:
            Distance score (1 - cosine similarity)
        """
        if self.n == 0:
            return 1.0  # Maximum distance from empty extent

        # Cosine similarity: cos(θ) = (a·b) / (||a|| ||b||)
        # Embeddings are already normalized, centroid is normalized
        norm_emb = np.linalg.norm(embedding)
        norm_cent = np.linalg.norm(self.centroid)

        if norm_emb < 1e-9 or norm_cent < 1e-9:
            return 1.0  # Degenerate case

        cos_sim = np.dot(embedding, self.centroid) / (norm_emb * norm_cent)
        cos_sim = np.clip(cos_sim, -1.0, 1.0)  # Numerical stability

        # Distance = 1 - cosine similarity (range [0, 2])
        # 0 = identical direction, 1 = orthogonal, 2 = opposite
        return 1.0 - cos_sim

    def _update_dispersion(self):
        """
        Internal: Recompute dispersion from active embeddings.

        Dispersion = mean(1 - cos(e, centroid)) across active nodes
        """
        if self.n == 0:
            self.dispersion = 0.0
            return

        distances = [self.distance_to(e) for e in self.active_embeddings]
        self.dispersion = np.mean(distances) if distances else 0.0


class IdentityEmbedding:
    """
    Tracks entity's identity center via EMA of active nodes.

    Identity = "Who am I?" = Semantic center of what I've explored
    Different from centroid (current extent) - this is historical identity
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Initialize identity tracker.

        Args:
            embedding_dim: Embedding dimension (default 768)
        """
        self.identity_embedding = np.zeros(embedding_dim)
        self.initialized = False
        self.ema_weight = 0.95  # Slow drift (identity is stable)
        self.embedding_dim = embedding_dim

    def update(self, active_nodes: Set[int], graph):
        """
        Update identity embedding from current active nodes.

        Args:
            active_nodes: Set of currently active node IDs
            graph: Consciousness graph
        """
        if len(active_nodes) == 0:
            return

        # Compute centroid of current active nodes
        embeddings = [graph.nodes[nid]['embedding'] for nid in active_nodes
                     if nid in graph.nodes and 'embedding' in graph.nodes[nid]]

        if len(embeddings) == 0:
            return

        current_centroid = np.mean(embeddings, axis=0)

        # Normalize
        norm = np.linalg.norm(current_centroid)
        if norm > 1e-9:
            current_centroid = current_centroid / norm

        if not self.initialized:
            # First update: Bootstrap identity from current extent
            self.identity_embedding = current_centroid
            self.initialized = True
        else:
            # EMA update: Slow drift toward new experiences
            self.identity_embedding = (
                self.ema_weight * self.identity_embedding +
                (1 - self.ema_weight) * current_centroid
            )

            # Renormalize
            norm = np.linalg.norm(self.identity_embedding)
            if norm > 1e-9:
                self.identity_embedding = self.identity_embedding / norm

    def coherence_with(self, embedding: np.ndarray) -> float:
        """
        Measure coherence between target and identity.

        Args:
            embedding: Target embedding (768-dim)

        Returns:
            coherence: Cosine similarity with identity [0, 1]
        """
        if not self.initialized:
            return 0.5  # Neutral before identity forms

        # Normalize embedding
        norm_emb = np.linalg.norm(embedding)
        if norm_emb < 1e-9:
            return 0.5

        embedding_norm = embedding / norm_emb

        similarity = np.dot(embedding_norm, self.identity_embedding)
        return max(0.0, similarity)


class BetaLearner:
    """
    Learn beta exponent for integration gate from merge outcomes.

    Tracks:
    - Merge events (small -> large merges)
    - ROI impact of merges
    - Adjusts beta to maximize ROI from successful merges
    """

    def __init__(self):
        """Initialize beta learner with neutral beta=1.0"""
        self.beta = 1.0  # Start neutral
        self.merge_history = []  # Recent merge observations
        self.update_frequency = 50  # Update beta every 50 observations

    def observe_potential_merge(
        self,
        small_entity,
        large_entity,
        merged: bool,
        roi_before: float,
        roi_after: float
    ):
        """
        Record merge outcome for learning.

        Args:
            small_entity: Smaller entity involved
            large_entity: Larger entity involved
            merged: Whether entities actually merged (overlap > 50%)
            roi_before: Average ROI before potential merge
            roi_after: Average ROI after merge/no-merge
        """
        # Compute size ratio
        small_size = sum(small_entity.get_energy(n) for n in small_entity.extent)
        large_size = sum(large_entity.get_energy(n) for n in large_entity.extent)
        size_ratio = large_size / (small_size + 1e-9)

        # ROI impact
        roi_impact = roi_after - roi_before

        self.merge_history.append({
            'size_ratio': size_ratio,
            'merged': merged,
            'roi_impact': roi_impact,
            'small_size': small_size,
            'large_size': large_size
        })

        # Update beta periodically
        if len(self.merge_history) >= self.update_frequency:
            self._update_beta()
            self.merge_history = []

    def _update_beta(self):
        """
        Update beta based on merge outcomes.

        Strategy:
        - If merges (with current beta) improve ROI -> increase beta (more merge pressure)
        - If merges hurt ROI -> decrease beta (less merge pressure)
        """
        if len(self.merge_history) < 10:
            return  # Need more data

        # Separate successful vs unsuccessful merges
        successful_merges = [
            m for m in self.merge_history
            if m['merged'] and m['roi_impact'] > 0
        ]

        # Compute success rate
        total_merges = len([m for m in self.merge_history if m['merged']])
        if total_merges == 0:
            return  # No merges to learn from

        success_rate = len(successful_merges) / total_merges

        # Adjust beta based on success rate
        if success_rate > 0.7:
            # Merges are working well, increase beta (more merge pressure)
            self.beta *= 1.1
        elif success_rate < 0.3:
            # Merges are failing, decrease beta (less merge pressure)
            self.beta *= 0.9
        # else: 30-70% success rate -> keep beta stable

        # Clip to reasonable range
        self.beta = np.clip(self.beta, 0.5, 2.0)

    def get_beta(self) -> float:
        """Get current beta value"""
        return self.beta


class ROITracker:
    """
    Rolling ROI statistics for convergence detection.

    Maintains Q1, Q3, IQR over recent stride ROI values.
    Convergence criterion: predicted_roi < Q1 - 1.5*IQR (lower whisker)

    Zero-constants: Threshold adapts to THIS entity's performance baseline.
    """

    def __init__(self, window_size: int = 256):
        """
        Initialize ROI tracker.

        Args:
            window_size: Number of recent ROI values to track
        """
        self.window = deque(maxlen=window_size)

    def push(self, roi: float):
        """
        Record ROI from stride execution.

        Args:
            roi: gap_reduced / stride_time_us
        """
        self.window.append(roi)

    def lower_whisker(self) -> float:
        """
        Compute convergence threshold: Q1 - 1.5 * IQR

        Returns:
            Lower whisker value (stop when predicted ROI below this)
        """
        if len(self.window) < 4:
            # Insufficient data - no convergence threshold yet
            return float('-inf')

        data = np.array(list(self.window))
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        whisker = q1 - 1.5 * iqr
        return whisker


class QuantileTracker:
    """
    General rolling quantiles for integration/size distributions.

    Tracks E_others/E_self ratios and entity sizes to determine:
    - "Strong field" detection (ratio > Q75)
    - Strategy determination (size < Q25 = merge_seeking, > Q75 = independent)

    Zero-constants: Quantiles recomputed every frame from current population.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize quantile tracker.

        Args:
            window_size: Number of recent samples
        """
        self.window = deque(maxlen=window_size)

    def update(self, value: float):
        """
        Add sample to rolling distribution.

        Args:
            value: Observed ratio or size
        """
        self.window.append(value)

    def quantile(self, p: float) -> float:
        """
        Compute p-th quantile of current distribution.

        Args:
            p: Quantile level (0.25 for Q25, 0.75 for Q75)

        Returns:
            Quantile value
        """
        if len(self.window) == 0:
            return 0.0  # No data

        data = np.array(list(self.window))
        return np.percentile(data, p * 100)


class SubEntity:
    """
    Main sub-entity class for traversal.

    Represents one active pattern traversing the graph, with:
    - Extent: nodes above threshold for this entity
    - Frontier: extent ∪ 1-hop neighbors
    - Energy channels: per-node energy tracking
    - Centroid: semantic diversity tracking
    - ROI: convergence detection

    Zero-constants: All behavior from rolling statistics and live state.
    """

    def __init__(self, entity_id: str, embedding_dim: int = 768):
        """
        Initialize sub-entity.

        Args:
            entity_id: Unique entity identifier
            embedding_dim: Embedding dimension
        """
        self.id = entity_id

        # Extent tracking
        self.extent: Set[int] = set()         # Node IDs above threshold
        self.frontier: Set[int] = set()       # Extent ∪ 1-hop

        # Energy tracking (views into graph state)
        self.energies: Dict[int, float] = {}  # E[entity_id, node_id]
        self.thresholds: Dict[int, float] = {}  # θ[entity_id, node_id]

        # Quota & convergence
        self.quota_assigned = 0
        self.quota_remaining = 0

        # ROI tracking for convergence
        self.roi_tracker = ROITracker(window_size=256)

        # Semantic diversity
        self.centroid = EntityExtentCentroid(embedding_dim)

        # Identity tracking
        self.identity = IdentityEmbedding(embedding_dim)

        # Beta learning for integration gate
        self.beta_learner = BetaLearner()

        # Local health
        self.rho_local_ema = 1.0  # EMA of local spectral radius

        # Hunger baselines (for surprise gates)
        self.hunger_baselines: Dict[str, tuple[float, float]] = {
            # hunger_name -> (μ, σ) EMA
            'homeostasis': (0.0, 1.0),
            'goal': (0.0, 1.0),
            'identity': (0.0, 1.0),
            'completeness': (0.0, 1.0),
            'complementarity': (0.0, 1.0),
            'integration': (0.0, 1.0),
            'ease': (0.0, 1.0),
        }

    def get_energy(self, node_id: int) -> float:
        """Get entity's energy at node."""
        return self.energies.get(node_id, 0.0)

    def get_threshold(self, node_id: int) -> float:
        """Get entity's threshold at node."""
        return self.thresholds.get(node_id, 0.1)

    def is_active(self, node_id: int) -> bool:
        """Check if node is above threshold for this entity."""
        return self.get_energy(node_id) >= self.get_threshold(node_id)

    def update_extent(self, graph):
        """
        Recompute extent and frontier from current energy state.

        Args:
            graph: Graph object with nodes and edges
        """
        old_extent = self.extent.copy()

        # Recompute extent: nodes above threshold
        new_extent = set()
        for node_id in graph.nodes:
            if self.is_active(node_id):
                new_extent.add(node_id)

        # Track centroid changes
        activated = new_extent - old_extent
        deactivated = old_extent - new_extent

        # Update centroid incrementally
        for node_id in deactivated:
            if node_id in graph.nodes and 'embedding' in graph.nodes[node_id]:
                self.centroid.remove_node(graph.nodes[node_id]['embedding'])

        for node_id in activated:
            if node_id in graph.nodes and 'embedding' in graph.nodes[node_id]:
                self.centroid.add_node(graph.nodes[node_id]['embedding'])

        self.extent = new_extent

        # Compute frontier: extent ∪ 1-hop neighbors
        frontier = self.extent.copy()
        for node_id in self.extent:
            if node_id in graph:
                # Add all outgoing neighbors
                for neighbor in graph.neighbors(node_id):
                    frontier.add(neighbor)

        self.frontier = frontier

    def compute_size(self, graph) -> float:
        """
        Compute entity size (total_energy × mean_link_weight).

        Used for strategy determination (merge_seeking vs independent).

        Args:
            graph: Graph object

        Returns:
            Entity size metric
        """
        if len(self.extent) == 0:
            return 0.0

        # Total energy in extent
        total_energy = sum(self.get_energy(node_id) for node_id in self.extent)

        # Mean link weight within extent (internal connectivity)
        link_weights = []
        for node_id in self.extent:
            if node_id in graph:
                for neighbor in graph.neighbors(node_id):
                    if neighbor in self.extent:
                        # Internal link
                        edge_data = graph.get_edge_data(node_id, neighbor)
                        if edge_data and 'weight' in edge_data:
                            link_weights.append(edge_data['weight'])

        if len(link_weights) == 0:
            # No internal links - use total energy only
            return total_energy

        mean_weight = np.mean(link_weights)

        # Size = total_energy × mean_internal_link_weight
        # High energy + strong internal links = large robust entity
        return total_energy * mean_weight
