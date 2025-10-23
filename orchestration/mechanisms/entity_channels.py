"""
Subentity Channel Selection - Multi-Subentity Budget Distribution

Implements subentity-aware energy routing for shared graphs:
- Subentity affinity (cosine similarity with subentity embeddings)
- Subentity recent success (flip share × gap closure share)
- Combined scoring with rank-z normalization
- Softmax proportions for budget allocation

Designer: Felix "Ironhand"
Date: 2025-10-21
Reference: stimulus_injection_specification.md §3.6
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class EntityObservation:
    """Single frame observation for subentity performance."""
    entity_id: str
    num_flips: int
    gap_closed: float  # Sum of (new_energy - threshold) for flips
    timestamp: float


class EntityChannelSelector:
    """
    Selects subentity channels for multi-subentity graphs.

    Tracks:
    - Subentity affinity (stimulus embedding × subentity embedding)
    - Subentity recent success (flips × gap closure)
    - Combined rank-z scoring
    - Softmax proportions for budget split

    Returns:
    - Per-subentity budget proportions π_e
    """

    def __init__(
        self,
        window_size: int = 100,
        min_samples: int = 20
    ):
        """
        Initialize subentity channel selector.

        Args:
            window_size: Rolling window for subentity observations
            min_samples: Minimum samples per subentity before modulation
        """
        self.window_size = window_size
        self.min_samples = min_samples

        # Per-subentity observations: entity_id -> deque
        self.observations: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

        # Subentity embeddings cache (entity_id -> embedding)
        self.entity_embeddings: Dict[str, np.ndarray] = {}

        logger.info(
            f"[EntityChannelSelector] Initialized "
            f"(window_size={window_size}, min_samples={min_samples})"
        )

    def set_entity_embedding(self, entity_id: str, embedding: np.ndarray):
        """
        Set or update subentity embedding.

        Args:
            entity_id: Subentity identifier
            embedding: Subentity embedding vector
        """
        self.entity_embeddings[entity_id] = embedding
        logger.debug(f"[EntityChannelSelector] Updated embedding for {entity_id}")

    def add_observation(
        self,
        entity_id: str,
        num_flips: int,
        gap_closed: float,
        timestamp: float
    ):
        """
        Record subentity performance observation.

        Args:
            entity_id: Subentity identifier
            num_flips: Number of flips this subentity caused
            gap_closed: Total gap closed (sum of new_energy - threshold)
            timestamp: Observation timestamp
        """
        obs = EntityObservation(
            entity_id=entity_id,
            num_flips=num_flips,
            gap_closed=gap_closed,
            timestamp=timestamp
        )

        self.observations[entity_id].append(obs)

        logger.debug(
            f"[EntityChannelSelector] Recorded {entity_id}: "
            f"flips={num_flips}, gap_closed={gap_closed:.2f}"
        )

    def _compute_affinity(
        self,
        stimulus_embedding: np.ndarray,
        entity_ids: List[str]
    ) -> Dict[str, float]:
        """
        Compute subentity affinity scores (cosine similarity).

        Args:
            stimulus_embedding: Current stimulus embedding
            entity_ids: List of subentity IDs to score

        Returns:
            Dict mapping entity_id -> affinity score
        """
        affinities = {}

        # Normalize stimulus
        stim_norm = stimulus_embedding / (np.linalg.norm(stimulus_embedding) + 1e-8)

        for entity_id in entity_ids:
            if entity_id not in self.entity_embeddings:
                # No embedding - neutral affinity
                affinities[entity_id] = 0.0
                continue

            # Compute cosine similarity
            entity_emb = self.entity_embeddings[entity_id]
            entity_norm = entity_emb / (np.linalg.norm(entity_emb) + 1e-8)

            affinity = float(np.dot(stim_norm, entity_norm))
            affinities[entity_id] = affinity

        return affinities

    def _compute_recent_success(
        self,
        entity_ids: List[str]
    ) -> Dict[str, float]:
        """
        Compute subentity recent success scores.

        Success = flip_share × gap_closure_share

        Args:
            entity_ids: List of subentity IDs to score

        Returns:
            Dict mapping entity_id -> success score
        """
        # Collect recent observations across all subentities
        total_flips = 0
        total_gap_closed = 0.0
        entity_flips = defaultdict(int)
        entity_gaps = defaultdict(float)

        for entity_id in entity_ids:
            obs_list = self.observations.get(entity_id, deque())

            for obs in obs_list:
                entity_flips[entity_id] += obs.num_flips
                entity_gaps[entity_id] += obs.gap_closed
                total_flips += obs.num_flips
                total_gap_closed += obs.gap_closed

        # Compute success scores
        success_scores = {}

        for entity_id in entity_ids:
            if total_flips == 0 or total_gap_closed == 0:
                # No data - neutral score
                success_scores[entity_id] = 0.0
                continue

            flip_share = entity_flips[entity_id] / total_flips
            gap_share = entity_gaps[entity_id] / total_gap_closed

            # Geometric mean
            success = np.sqrt(flip_share * gap_share)
            success_scores[entity_id] = float(success)

        return success_scores

    def _rank_z_normalize(
        self,
        scores: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Rank-z normalize scores.

        Converts ranks to z-scores for balanced weighting.

        Args:
            scores: Dict of entity_id -> score

        Returns:
            Dict of entity_id -> z-score
        """
        if len(scores) < 2:
            # Single subentity - neutral
            return {k: 0.0 for k in scores.keys()}

        # Get values in order
        entity_ids = list(scores.keys())
        values = [scores[eid] for eid in entity_ids]

        # Compute ranks
        ranks = []
        for val in values:
            rank = sum(1 for v in values if v <= val)
            ranks.append(rank)

        # Convert ranks to [0, 1]
        rank_fracs = [r / len(values) for r in ranks]

        # Convert to z-scores (inverse normal CDF approximation)
        # Simple approximation: z ≈ 2 × (rank_frac - 0.5)
        z_scores = {}
        for eid, rank_frac in zip(entity_ids, rank_fracs):
            z = 2.0 * (rank_frac - 0.5)
            z_scores[eid] = z

        return z_scores

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Apply softmax to scores to get proportions.

        Args:
            scores: Dict of entity_id -> score

        Returns:
            Dict of entity_id -> proportion (sum = 1.0)
        """
        if not scores:
            return {}

        entity_ids = list(scores.keys())
        values = np.array([scores[eid] for eid in entity_ids])

        # Softmax with numerical stability
        exp_values = np.exp(values - np.max(values))
        proportions = exp_values / np.sum(exp_values)

        return {
            eid: float(prop)
            for eid, prop in zip(entity_ids, proportions)
        }

    def select_channels(
        self,
        stimulus_embedding: np.ndarray,
        entity_ids: List[str]
    ) -> Dict[str, float]:
        """
        Select subentity channels and compute budget proportions.

        Args:
            stimulus_embedding: Current stimulus embedding
            entity_ids: List of active subentity IDs

        Returns:
            Dict mapping entity_id -> budget proportion π_e
        """
        # Bootstrap: equal split until sufficient data
        if not any(
            len(self.observations.get(eid, deque())) >= self.min_samples
            for eid in entity_ids
        ):
            logger.debug(
                f"[EntityChannelSelector] Bootstrap mode - equal split"
            )
            equal_prop = 1.0 / len(entity_ids)
            return {eid: equal_prop for eid in entity_ids}

        # Compute affinity scores
        affinities = self._compute_affinity(stimulus_embedding, entity_ids)

        # Compute recent success scores
        successes = self._compute_recent_success(entity_ids)

        # Rank-z normalize both
        affinity_z = self._rank_z_normalize(affinities)
        success_z = self._rank_z_normalize(successes)

        # Combine scores (simple average)
        combined = {
            eid: (affinity_z[eid] + success_z[eid]) / 2.0
            for eid in entity_ids
        }

        # Softmax to get proportions
        proportions = self._softmax(combined)

        logger.debug(
            f"[EntityChannelSelector] Channel selection: "
            f"{', '.join(f'{eid}={prop:.2f}' for eid, prop in proportions.items())}"
        )

        return proportions

    def get_stats(self) -> dict:
        """Get current selector statistics."""
        stats = {}

        for entity_id, obs_list in self.observations.items():
            if len(obs_list) > 0:
                flips = [obs.num_flips for obs in obs_list]
                gaps = [obs.gap_closed for obs in obs_list]

                stats[entity_id] = {
                    "observations": len(obs_list),
                    "total_flips": sum(flips),
                    "total_gap_closed": float(np.sum(gaps)),
                    "avg_flips": float(np.mean(flips)),
                    "has_embedding": entity_id in self.entity_embeddings
                }

        return stats
