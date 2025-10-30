"""
E.6: Coherence Metric - Measures Quality of Activation Spread

Coherence C ∈ [0,1] distinguishes productive flow from chaotic thrashing.
Combines frontier similarity (continuity) and stride relatedness (semantic coherence).

Formula: C = α_frontier · C_frontier + α_stride · C_stride

Where:
- C_frontier: cosine similarity of active frontier centroids (frame-to-frame)
- C_stride: mean relatedness of executed strides (link weights + semantic alignment)

Interpretation:
- C > 0.7: Coherent exploration, smooth flow
- C 0.4-0.7: Mixed quality, some jumps
- C < 0.4: Fragmented, chaotic, thrashing

Author: Felix - 2025-10-23
Status: Production-ready (PR-E)
"""

from typing import List, Optional, Dict, Any
import numpy as np
from collections import deque
from dataclasses import dataclass

from orchestration.core.settings import settings


@dataclass
class CoherenceState:
    """
    Rolling state for coherence computation.

    Tracks previous frame's frontier and recent stride metrics
    for windowed smoothing.
    """
    # Previous frame frontier centroid (for C_frontier)
    prev_frontier_centroid: Optional[np.ndarray] = None

    # Rolling window of C values for smoothing
    coherence_history: deque = None

    # Stride relatedness values from current frame
    stride_relatedness_scores: List[float] = None

    def __post_init__(self):
        if self.coherence_history is None:
            self.coherence_history = deque(maxlen=settings.COHERENCE_SMOOTHING_WINDOW)
        if self.stride_relatedness_scores is None:
            self.stride_relatedness_scores = []


def compute_frontier_similarity(
    current_frontier_nodes: List[Any],
    prev_frontier_centroid: Optional[np.ndarray]
) -> float:
    """
    Compute C_frontier: similarity of active frontier to previous frame.

    Args:
        current_frontier_nodes: Currently active frontier nodes (with embeddings)
        prev_frontier_centroid: Centroid of previous frame's frontier

    Returns:
        C_frontier ∈ [0, 1]: Cosine similarity (shifted to [0,1])
    """
    if not current_frontier_nodes:
        return 0.0

    # Extract embeddings from nodes
    embeddings = []
    for node in current_frontier_nodes:
        if hasattr(node, 'embedding') and node.embedding is not None:
            embeddings.append(node.embedding)

    if not embeddings:
        return 0.0

    # Compute current centroid
    current_centroid = np.mean(embeddings, axis=0)

    # If no previous centroid, return neutral (0.5)
    if prev_frontier_centroid is None:
        return 0.5

    # Cosine similarity
    norm_curr = np.linalg.norm(current_centroid)
    norm_prev = np.linalg.norm(prev_frontier_centroid)

    if norm_curr < 1e-8 or norm_prev < 1e-8:
        return 0.5  # Neutral if either is zero

    cos_sim = np.dot(current_centroid, prev_frontier_centroid) / (norm_curr * norm_prev)

    # Shift from [-1, 1] to [0, 1]
    c_frontier = (cos_sim + 1.0) / 2.0

    return float(np.clip(c_frontier, 0.0, 1.0))


def compute_stride_relatedness(stride_relatedness_scores: List[float]) -> float:
    """
    Compute C_stride: mean relatedness of executed strides.

    Args:
        stride_relatedness_scores: Relatedness scores from strides
                                   (based on link weights and semantic alignment)

    Returns:
        C_stride ∈ [0, 1]: Mean relatedness
    """
    if not stride_relatedness_scores:
        return 0.0

    return float(np.mean(stride_relatedness_scores))


def compute_coherence_metric(
    current_frontier_nodes: List[Any],
    stride_relatedness_scores: List[float],
    state: CoherenceState
) -> Dict[str, Any]:
    """
    Compute coherence metric C combining frontier similarity and stride relatedness.

    Args:
        current_frontier_nodes: Active frontier nodes (with embeddings)
        stride_relatedness_scores: Relatedness of executed strides
        state: Coherence state (tracks history for smoothing)

    Returns:
        Dict with:
            - coherence: Overall C value (smoothed over window)
            - coherence_raw: Current frame C (before smoothing)
            - c_frontier: Frontier similarity component
            - c_stride: Stride relatedness component
            - interpretation: "coherent" | "mixed" | "fragmented"
    """
    if not settings.COHERENCE_METRIC_ENABLED:
        return {
            'coherence': 0.5,
            'coherence_raw': 0.5,
            'c_frontier': 0.5,
            'c_stride': 0.5,
            'interpretation': 'disabled'
        }

    # Compute components
    c_frontier = compute_frontier_similarity(
        current_frontier_nodes,
        state.prev_frontier_centroid
    )

    c_stride = compute_stride_relatedness(stride_relatedness_scores)

    # Weighted combination
    alpha_f = settings.COHERENCE_ALPHA_FRONTIER
    alpha_s = settings.COHERENCE_ALPHA_STRIDE

    c_raw = alpha_f * c_frontier + alpha_s * c_stride
    c_raw = float(np.clip(c_raw, 0.0, 1.0))

    # Add to history for smoothing
    state.coherence_history.append(c_raw)

    # Smoothed coherence (rolling average)
    c_smoothed = float(np.mean(state.coherence_history))

    # Interpretation
    if c_smoothed > 0.7:
        interpretation = "coherent"
    elif c_smoothed > 0.4:
        interpretation = "mixed"
    else:
        interpretation = "fragmented"

    # Update state for next frame
    if current_frontier_nodes:
        embeddings = [
            node.embedding for node in current_frontier_nodes
            if hasattr(node, 'embedding') and node.embedding is not None
        ]
        if embeddings:
            state.prev_frontier_centroid = np.mean(embeddings, axis=0)

    return {
        'coherence': c_smoothed,
        'coherence_raw': c_raw,
        'c_frontier': c_frontier,
        'c_stride': c_stride,
        'interpretation': interpretation,
        'window_size': len(state.coherence_history)
    }


def assess_stride_relatedness(
    source_node: Any,
    target_node: Any,
    link: Any
) -> float:
    """
    Assess relatedness of a single stride (for C_stride computation).

    Combines:
    - Link weight (learned strength)
    - Semantic alignment (embedding similarity)

    Args:
        source_node: Source node of stride
        target_node: Target node of stride
        link: Link being traversed

    Returns:
        Relatedness score ∈ [0, 1]
    """
    # Component 1: Link strength (from log_weight)
    # log_weight typically in [-2, 0], convert to [0, 1]
    if hasattr(link, 'log_weight'):
        log_weight = float(link.log_weight)
        # Map [-2, 0] -> [0, 1]
        weight_score = np.clip((log_weight + 2.0) / 2.0, 0.0, 1.0)
    else:
        weight_score = 0.5  # Neutral if no weight

    # Component 2: Semantic alignment (embedding similarity)
    semantic_score = 0.5  # Default neutral

    if (hasattr(source_node, 'embedding') and source_node.embedding is not None and
        hasattr(target_node, 'embedding') and target_node.embedding is not None):

        source_emb = source_node.embedding
        target_emb = target_node.embedding

        norm_s = np.linalg.norm(source_emb)
        norm_t = np.linalg.norm(target_emb)

        if norm_s > 1e-8 and norm_t > 1e-8:
            cos_sim = np.dot(source_emb, target_emb) / (norm_s * norm_t)
            # Shift from [-1, 1] to [0, 1]
            semantic_score = (cos_sim + 1.0) / 2.0

    # Combine (equal weights)
    relatedness = 0.5 * weight_score + 0.5 * semantic_score

    return float(np.clip(relatedness, 0.0, 1.0))


def emit_coherence_telemetry(
    coherence_result: Dict[str, Any],
    frame_id: int,
    citizen_id: str
) -> Dict[str, Any]:
    """
    Create telemetry event for coherence metric.

    Args:
        coherence_result: Result from compute_coherence_metric()
        frame_id: Current frame/tick number
        citizen_id: Citizen identifier

    Returns:
        Telemetry event dict
    """
    return {
        'event': 'coherence.metric',
        'citizen_id': citizen_id,
        'frame_id': frame_id,
        'coherence': round(coherence_result['coherence'], 4),
        'coherence_raw': round(coherence_result['coherence_raw'], 4),
        'c_frontier': round(coherence_result['c_frontier'], 4),
        'c_stride': round(coherence_result['c_stride'], 4),
        'interpretation': coherence_result['interpretation'],
        'window_size': coherence_result['window_size'],
        'config': {
            'alpha_frontier': settings.COHERENCE_ALPHA_FRONTIER,
            'alpha_stride': settings.COHERENCE_ALPHA_STRIDE,
            'smoothing_window': settings.COHERENCE_SMOOTHING_WINDOW
        }
    }
