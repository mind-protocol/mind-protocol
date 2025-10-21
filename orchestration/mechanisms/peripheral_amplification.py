"""
Peripheral Amplification - Z-Score Alignment with S5/S6 Context

Implements context-aware budget boosting:
- Measures cosine similarity between stimulus and S5/S6 context
- Computes z-score of alignment within recent stimuli cohort
- Amplifies budget for stimuli that align with current focus

Designer: Felix "Ironhand"
Date: 2025-10-21
Reference: stimulus_injection_specification.md §3.5
"""

import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class AlignmentObservation:
    """Single stimulus alignment observation."""
    stimulus_embedding: np.ndarray
    context_similarity: float  # Cosine sim with S5/S6
    timestamp: float


class PeripheralAmplifier:
    """
    Amplifies budget for stimuli aligned with current context.

    Tracks:
    - Cosine similarity between stimulus and S5/S6 context chunks
    - Rolling cohort of recent stimulus alignments
    - Z-score normalization within cohort

    Returns:
    - Amplification factor α = max(0, z_alignment)
    - Amplified budget: B × (1 + α)
    """

    def __init__(
        self,
        cohort_size: int = 100,
        min_cohort: int = 20
    ):
        """
        Initialize peripheral amplifier.

        Args:
            cohort_size: Rolling window size for alignment observations
            min_cohort: Minimum cohort size before amplification
        """
        self.cohort_size = cohort_size
        self.min_cohort = min_cohort

        # Rolling cohort of alignment observations
        self.alignments = deque(maxlen=cohort_size)

        logger.info(
            f"[PeripheralAmplifier] Initialized "
            f"(cohort_size={cohort_size}, min_cohort={min_cohort})"
        )

    def compute_context_similarity(
        self,
        stimulus_embedding: np.ndarray,
        context_embeddings: List[np.ndarray]
    ) -> float:
        """
        Compute max cosine similarity with S5/S6 context chunks.

        Args:
            stimulus_embedding: Embedding of current stimulus
            context_embeddings: List of S5/S6 context chunk embeddings

        Returns:
            Maximum cosine similarity across all context chunks
        """
        if not context_embeddings:
            return 0.0

        # Normalize stimulus embedding
        stim_norm = stimulus_embedding / (np.linalg.norm(stimulus_embedding) + 1e-8)

        # Compute cosine similarity with each context chunk
        similarities = []
        for ctx_emb in context_embeddings:
            ctx_norm = ctx_emb / (np.linalg.norm(ctx_emb) + 1e-8)
            sim = np.dot(stim_norm, ctx_norm)
            similarities.append(sim)

        # Return maximum alignment
        max_similarity = float(np.max(similarities))

        return max_similarity

    def add_observation(
        self,
        stimulus_embedding: np.ndarray,
        context_similarity: float,
        timestamp: float
    ):
        """
        Record stimulus alignment observation.

        Args:
            stimulus_embedding: Embedding of stimulus
            context_similarity: Cosine similarity with context
            timestamp: Observation timestamp
        """
        obs = AlignmentObservation(
            stimulus_embedding=stimulus_embedding,
            context_similarity=context_similarity,
            timestamp=timestamp
        )

        self.alignments.append(obs)

        logger.debug(
            f"[PeripheralAmplifier] Recorded alignment: "
            f"similarity={context_similarity:.3f}, "
            f"cohort_size={len(self.alignments)}"
        )

    def _compute_z_score(self, value: float, cohort_values: List[float]) -> float:
        """
        Compute z-score of value within cohort.

        Args:
            value: Value to normalize
            cohort_values: Cohort for normalization

        Returns:
            Z-score (standardized value)
        """
        if len(cohort_values) < 2:
            return 0.0

        mean = np.mean(cohort_values)
        std = np.std(cohort_values)

        # Avoid division by zero
        if std < 1e-8:
            return 0.0

        z_score = (value - mean) / std

        return float(z_score)

    def amplify(
        self,
        stimulus_embedding: np.ndarray,
        context_embeddings: Optional[List[np.ndarray]] = None,
        timestamp: Optional[float] = None
    ) -> float:
        """
        Compute amplification factor for budget.

        Args:
            stimulus_embedding: Embedding of current stimulus
            context_embeddings: S5/S6 context chunk embeddings (optional)
            timestamp: Current timestamp (optional)

        Returns:
            Amplification factor α ≥ 0
        """
        import time

        if timestamp is None:
            timestamp = time.time()

        # Bootstrap: no amplification until cohort established
        if len(self.alignments) < self.min_cohort:
            logger.debug(
                f"[PeripheralAmplifier] Bootstrap mode "
                f"({len(self.alignments)}/{self.min_cohort} samples)"
            )
            return 0.0

        # Compute context similarity for this stimulus
        if context_embeddings is None or len(context_embeddings) == 0:
            # No context available - neutral amplification
            return 0.0

        current_similarity = self.compute_context_similarity(
            stimulus_embedding,
            context_embeddings
        )

        # Get cohort similarities
        cohort_similarities = [obs.context_similarity for obs in self.alignments]

        # Compute z-score
        z_alignment = self._compute_z_score(current_similarity, cohort_similarities)

        # Amplification factor: α = max(0, z_alignment)
        alpha = max(0.0, z_alignment)

        # Record this observation for future cohort
        self.add_observation(stimulus_embedding, current_similarity, timestamp)

        logger.debug(
            f"[PeripheralAmplifier] Amplification: "
            f"similarity={current_similarity:.3f}, "
            f"z_score={z_alignment:.3f}, "
            f"α={alpha:.3f}"
        )

        return float(alpha)

    def get_stats(self) -> dict:
        """Get current amplifier statistics."""
        if not self.alignments:
            return {
                "observations": 0,
                "ready": False
            }

        similarities = [obs.context_similarity for obs in self.alignments]

        return {
            "observations": len(self.alignments),
            "ready": len(self.alignments) >= self.min_cohort,
            "avg_similarity": float(np.mean(similarities)),
            "std_similarity": float(np.std(similarities)),
            "min_similarity": float(np.min(similarities)),
            "max_similarity": float(np.max(similarities))
        }
