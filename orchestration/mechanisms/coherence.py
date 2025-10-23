"""
Coherence Metric (E.6) - Measures quality of activation spread.

PR-E.6: Coherence Metric

Problem:
  ρ (spectral radius) measures QUANTITY of activation spread but not QUALITY.
  High ρ can mean either productive exploration or chaotic thrashing.
  We need a second axis to distinguish flow from fragmentation.

Mechanism:
  Compute Coherence C ∈ [0,1] measuring quality of activation spread:

  C = α_frontier * C_frontier + α_stride * C_stride

  where:
  - C_frontier = similarity of active frontier to previous frame (cosine of embedding centroids)
  - C_stride = mean relatedness of executed strides (link weights × semantic alignment)
  - Default weights: α_frontier = 0.6, α_stride = 0.4

Interpretation:
  - High C (> 0.7): Coherent exploration, related concepts, smooth traversal
  - Medium C (0.4-0.7): Mixed quality, some jumps but some continuity
  - Low C (< 0.4): Fragmented, incoherent jumps, thrashing

Status:
  OPTIONAL enrichment, behind COHERENCE_METRIC_ENABLED flag (default: false)

Author: Felix - 2025-10-23
Spec: docs/specs/v2/foundations/criticality.md (section 2.1)
"""

import logging
import numpy as np
from typing import List, Dict, Set, Optional, Tuple
from collections import deque
from dataclasses import dataclass

from orchestration.core.node import Node
from orchestration.core.link import Link
from orchestration.core.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class CoherenceState:
    """Current coherence measurement."""

    C: float  # Combined coherence [0, 1]
    C_frontier: float  # Frontier similarity [0, 1]
    C_stride: float  # Stride relatedness [0, 1]

    # Diagnostics
    frontier_size: int
    strides_executed: int
    smoothed: bool  # Whether this is smoothed over window


class CoherenceTracker:
    """
    Tracks coherence metric C ∈ [0,1] measuring quality of activation spread.

    Stateful tracker that maintains:
    - Previous frame's active frontier (embeddings)
    - Recent stride history
    - Rolling window for smoothing

    Usage:
        tracker = CoherenceTracker()
        tracker.enable()  # Turn on coherence tracking

        # Each frame:
        C_state = tracker.update(
            active_nodes=active_nodes_this_frame,
            executed_strides=[(link, semantic_similarity), ...]
        )

        if C_state.C < 0.4:
            logger.warning("Fragmented, incoherent traversal detected")
    """

    def __init__(self):
        """Initialize coherence tracker."""

        # Feature flag
        self.enabled = False

        # Configuration (read from settings)
        self.alpha_frontier = getattr(settings, 'COHERENCE_ALPHA_FRONTIER', 0.6)
        self.alpha_stride = getattr(settings, 'COHERENCE_ALPHA_STRIDE', 0.4)
        self.smoothing_window = getattr(settings, 'COHERENCE_SMOOTHING_WINDOW', 5)

        # State tracking
        self.previous_frontier: Optional[np.ndarray] = None  # Centroid of previous active nodes
        self.previous_frontier_size: int = 0

        # Rolling window for smoothing
        self.coherence_history: deque = deque(maxlen=self.smoothing_window)

        # Diagnostics
        self.frame_count = 0

        logger.info(
            f"[CoherenceTracker] Initialized with "
            f"α_frontier={self.alpha_frontier}, α_stride={self.alpha_stride}, "
            f"window={self.smoothing_window}"
        )

    def enable(self):
        """Enable coherence tracking (PR-E.6)."""
        self.enabled = True
        logger.info("[CoherenceTracker] Coherence metric ENABLED")

    def disable(self):
        """Disable coherence tracking."""
        self.enabled = False
        logger.info("[CoherenceTracker] Coherence metric DISABLED")

    def update(
        self,
        active_nodes: List[Node],
        executed_strides: List[Tuple[Link, float]]
    ) -> Optional[CoherenceState]:
        """
        Update coherence metric for current frame.

        Args:
            active_nodes: Nodes above threshold this frame
            executed_strides: List of (link, semantic_similarity) tuples for executed strides

        Returns:
            CoherenceState if enabled, None otherwise
        """
        if not self.enabled:
            return None

        self.frame_count += 1

        # Compute C_frontier (similarity to previous frame's frontier)
        C_frontier, current_centroid = self._compute_frontier_coherence(active_nodes)

        # Compute C_stride (mean relatedness of executed strides)
        C_stride = self._compute_stride_coherence(executed_strides)

        # Combine: C = α_frontier * C_frontier + α_stride * C_stride
        C_raw = self.alpha_frontier * C_frontier + self.alpha_stride * C_stride

        # Add to rolling window
        self.coherence_history.append(C_raw)

        # Smoothed coherence (mean of window)
        C_smoothed = np.mean(list(self.coherence_history))

        # Update state for next frame
        self.previous_frontier = current_centroid
        self.previous_frontier_size = len(active_nodes)

        # Create state
        state = CoherenceState(
            C=C_smoothed,
            C_frontier=C_frontier,
            C_stride=C_stride,
            frontier_size=len(active_nodes),
            strides_executed=len(executed_strides),
            smoothed=len(self.coherence_history) >= self.smoothing_window
        )

        # Log diagnostics
        if self.frame_count % 10 == 0 or C_smoothed < 0.4 or C_smoothed > 0.9:
            logger.debug(
                f"[Coherence] Frame {self.frame_count}: C={C_smoothed:.3f} "
                f"(C_frontier={C_frontier:.3f}, C_stride={C_stride:.3f}), "
                f"frontier_size={len(active_nodes)}, strides={len(executed_strides)}"
            )

        if C_smoothed < 0.4:
            logger.warning(
                f"[Coherence] LOW COHERENCE DETECTED: C={C_smoothed:.3f} - "
                f"fragmented, incoherent traversal"
            )
        elif C_smoothed > 0.7:
            logger.debug(
                f"[Coherence] HIGH COHERENCE: C={C_smoothed:.3f} - "
                f"smooth, related exploration"
            )

        return state

    def _compute_frontier_coherence(
        self,
        active_nodes: List[Node]
    ) -> Tuple[float, Optional[np.ndarray]]:
        """
        Compute C_frontier = cosine similarity of active frontier to previous frame.

        Returns:
            (C_frontier, current_centroid)
        """
        if not active_nodes:
            return 0.0, None

        # Collect embeddings from active nodes
        embeddings = []
        for node in active_nodes:
            if hasattr(node, 'embedding') and node.embedding is not None:
                embeddings.append(node.embedding)

        if not embeddings:
            # No embeddings available
            return 0.0, None

        # Compute centroid of current frontier
        current_centroid = np.mean(embeddings, axis=0)

        # First frame: no previous frontier to compare
        if self.previous_frontier is None:
            return 1.0, current_centroid  # Perfect coherence (no comparison yet)

        # Compute cosine similarity: cos(prev, curr) ∈ [-1, 1]
        # Normalize to [0, 1] where 0 = opposite, 0.5 = orthogonal, 1 = aligned
        cosine_sim = np.dot(self.previous_frontier, current_centroid) / (
            np.linalg.norm(self.previous_frontier) * np.linalg.norm(current_centroid) + 1e-10
        )

        # Map [-1, 1] → [0, 1]
        # cos = 1 → C = 1 (perfect alignment)
        # cos = 0 → C = 0.5 (orthogonal)
        # cos = -1 → C = 0 (opposite)
        C_frontier = (cosine_sim + 1.0) / 2.0

        return C_frontier, current_centroid

    def _compute_stride_coherence(
        self,
        executed_strides: List[Tuple[Link, float]]
    ) -> float:
        """
        Compute C_stride = mean relatedness of executed strides.

        Relatedness combines:
        - Link log_weight (learned importance)
        - Semantic similarity (if available)

        Args:
            executed_strides: List of (link, semantic_similarity) tuples

        Returns:
            C_stride ∈ [0, 1]
        """
        if not executed_strides:
            return 0.5  # Neutral if no strides

        relatedness_scores = []

        for link, semantic_sim in executed_strides:
            # Base relatedness from link weight
            # log_weight ∈ [-inf, 0], exp(log_weight) ∈ [0, 1]
            weight_score = np.exp(link.log_weight) if hasattr(link, 'log_weight') else 0.5

            # Combine with semantic similarity (if available)
            if semantic_sim is not None and semantic_sim >= 0:
                # Weighted average: 60% weight, 40% semantic
                combined = 0.6 * weight_score + 0.4 * semantic_sim
            else:
                combined = weight_score

            relatedness_scores.append(combined)

        # Mean relatedness across all strides
        C_stride = np.mean(relatedness_scores)

        return float(C_stride)

    def get_state(self) -> Optional[CoherenceState]:
        """
        Get current coherence state (last computed value).

        Returns:
            Most recent CoherenceState or None if no data
        """
        if not self.enabled or len(self.coherence_history) == 0:
            return None

        C_smoothed = np.mean(list(self.coherence_history))

        return CoherenceState(
            C=C_smoothed,
            C_frontier=0.0,  # Not available from history
            C_stride=0.0,  # Not available from history
            frontier_size=self.previous_frontier_size,
            strides_executed=0,
            smoothed=len(self.coherence_history) >= self.smoothing_window
        )

    def reset(self):
        """Reset tracker state (e.g., after major context switch)."""
        self.previous_frontier = None
        self.previous_frontier_size = 0
        self.coherence_history.clear()
        self.frame_count = 0
        logger.info("[CoherenceTracker] State reset")


# Convenience function for standalone usage
def compute_coherence(
    active_nodes: List[Node],
    executed_strides: List[Tuple[Link, float]],
    previous_frontier: Optional[np.ndarray] = None,
    alpha_frontier: float = 0.6,
    alpha_stride: float = 0.4
) -> Tuple[float, Optional[np.ndarray]]:
    """
    Stateless coherence computation (for testing or one-off measurement).

    Args:
        active_nodes: Nodes above threshold this frame
        executed_strides: List of (link, semantic_similarity) tuples
        previous_frontier: Previous frame's frontier centroid (None for first frame)
        alpha_frontier: Weight for frontier similarity (default 0.6)
        alpha_stride: Weight for stride relatedness (default 0.4)

    Returns:
        (C, current_centroid) where C ∈ [0,1] is coherence score
    """
    # Compute frontier coherence
    if not active_nodes:
        return 0.0, None

    embeddings = [node.embedding for node in active_nodes if hasattr(node, 'embedding') and node.embedding is not None]

    if not embeddings:
        return 0.0, None

    current_centroid = np.mean(embeddings, axis=0)

    if previous_frontier is None:
        C_frontier = 1.0  # First frame
    else:
        cosine_sim = np.dot(previous_frontier, current_centroid) / (
            np.linalg.norm(previous_frontier) * np.linalg.norm(current_centroid) + 1e-10
        )
        C_frontier = (cosine_sim + 1.0) / 2.0

    # Compute stride coherence
    if not executed_strides:
        C_stride = 0.5
    else:
        relatedness_scores = []
        for link, semantic_sim in executed_strides:
            weight_score = np.exp(link.log_weight) if hasattr(link, 'log_weight') else 0.5
            if semantic_sim is not None and semantic_sim >= 0:
                combined = 0.6 * weight_score + 0.4 * semantic_sim
            else:
                combined = weight_score
            relatedness_scores.append(combined)
        C_stride = np.mean(relatedness_scores)

    # Combine
    C = alpha_frontier * C_frontier + alpha_stride * C_stride

    return C, current_centroid
