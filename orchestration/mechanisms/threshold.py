"""
Mechanism 16 Part 1: Adaptive Activation Threshold

ARCHITECTURAL PRINCIPLE: Nodes Become Subentities via Threshold Crossing

"Every time a node reaches the threshold of activation from a sensory input,
it becomes a sub-entity." - Nicolas

Core Truth (CORRECTED 2025-10-20):
- NOT pre-defined subentities (Translator, Architect) - those are CLUSTERS of micro-subentities
- ANY node crossing activation threshold becomes its own sub-entity
- Subentity name = node name (simple one-to-one mapping)
- Thousands of simultaneous micro-subentities (normal and expected)
- Threshold is DYNAMIC - depends on system criticality (active nodes/links)
- NO MIN THRESHOLD, NO MAX THRESHOLD - unbounded adaptation

Threshold Architecture:
- PRIMARY: Criticality-driven (more active nodes/links = higher threshold)
- SECONDARY: Base noise floor (prevents false activations from noise)

Formula:
    theta_{i,k} = BASE_THRESHOLD * (1 + CRITICALITY_FACTOR * num_active / num_total)

    where:
    - BASE_THRESHOLD: Starting threshold (much higher than 0.1)
    - CRITICALITY_FACTOR: How much criticality raises threshold
    - num_active: Number of currently active nodes
    - num_total: Total nodes in graph

This creates adaptive behavior:
- Low activity (few nodes active): Lower threshold, easy to activate new nodes
- High activity (many nodes active): Higher threshold, harder to activate more
- Prevents runaway activation while allowing exploration when quiet

Activation test:
    node_is_active = (e_{i,k} >= theta_{i,k})

Soft activation (recommended):
    a_{i,k} = sigmoid(beta * (e_{i,k} - theta_{i,k}))

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-20 - Made threshold criticality-driven, removed bounds
Spec: Based on Nicolas's architectural corrections 2025-10-20
"""

import numpy as np
from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass
from collections import deque

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.types import EntityID

from orchestration.core.settings import settings
from orchestration.core.telemetry import emit_affective_threshold

# --- Configuration ---

BASE_THRESHOLD_DEFAULT: float = 1.0  # Base activation threshold (way higher than 0.1)
CRITICALITY_FACTOR_DEFAULT: float = 2.0  # How much criticality multiplies threshold
KAPPA_DEFAULT: float = 10.0  # Soft activation sharpness


@dataclass
class NoiseStatistics:
    """
    Noise floor statistics for threshold calculation.

    Tracked via Exponential Moving Average (EMA) when node is quiet.

    Args:
        mu: Noise floor (mean energy when quiet)
        sigma: Noise variability (std dev when quiet)
        sample_count: Number of samples collected
    """
    mu: float = 0.02
    sigma: float = 0.01
    sample_count: int = 0


@dataclass
class ThresholdContext:
    """
    Configuration for adaptive threshold calculation.

    Args:
        base_threshold: Starting threshold value. Default 1.0.
        criticality_factor: How much criticality multiplies threshold. Default 2.0.
        kappa: Soft activation sharpness. Default 10.0.
        num_active: Number of currently active nodes (computed dynamically)
        num_total: Total number of nodes in graph
    """
    base_threshold: float = BASE_THRESHOLD_DEFAULT
    criticality_factor: float = CRITICALITY_FACTOR_DEFAULT
    kappa: float = KAPPA_DEFAULT
    num_active: int = 0
    num_total: int = 1


# --- Threshold Calculation ---

def compute_base_threshold(
    mu: float,
    sigma: float,
    z_alpha: float
) -> float:
    """
    Compute base statistical threshold.

    Formula: theta_base = mu + z_alpha * sigma

    This is the MINIMUM threshold - sets false-positive rate.

    Args:
        mu: Noise floor (mean energy when quiet)
        sigma: Noise variability (std dev when quiet)
        z_alpha: Z-score (e.g., 1.28 for alpha=10%)

    Returns:
        Base threshold

    Example:
        >>> mu, sigma = 0.02, 0.01
        >>> theta_base = compute_base_threshold(mu, sigma, 1.28)
        >>> print(f"Base threshold: {theta_base:.3f}")
        Base threshold: 0.033  # mu + 1.28*sigma
    """
    return mu + z_alpha * sigma


def compute_adaptive_threshold(
    node: 'Node',
    subentity: 'EntityID',
    ctx: ThresholdContext,
    active_affect: Optional[np.ndarray] = None,
    citizen_id: str = "",
    frame_id: Optional[str] = None
) -> float:
    """
    Compute adaptive threshold for node-subentity pair.

    Threshold driven by system criticality (number of active nodes).
    Optionally modulated by affective coupling (PR-B).

    Formula:
        theta_base = BASE_THRESHOLD * (1 + CRITICALITY_FACTOR * (num_active / num_total))
        theta_adjusted = theta_base - h  (if affective coupling enabled)

    Where h is the affective threshold reduction (bounded [0, λ_aff]).

    More active nodes = higher threshold = harder to activate more nodes.
    This prevents runaway activation.

    Args:
        node: Node to compute threshold for
        subentity: Subentity identifier
        ctx: Threshold configuration with criticality state
        active_affect: Current affective state vector (optional, for PR-B)
        citizen_id: Citizen ID for telemetry
        frame_id: Frame ID for telemetry

    Returns:
        Adaptive threshold value (unbounded - no min/max)

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     criticality_factor=2.0,
        ...     num_active=10,
        ...     num_total=100
        ... )
        >>> theta = compute_adaptive_threshold(node, "translator", ctx)
        >>> # theta = 1.0 * (1 + 2.0 * (10/100)) = 1.0 * 1.2 = 1.2
    """
    # Compute criticality ratio
    if ctx.num_total > 0:
        criticality_ratio = ctx.num_active / ctx.num_total
    else:
        criticality_ratio = 0.0

    # Apply criticality-driven threshold
    theta_base = ctx.base_threshold * (1.0 + ctx.criticality_factor * criticality_ratio)

    # Apply affective modulation if enabled (PR-B)
    h = 0.0
    theta_adjusted = theta_base

    if settings.AFFECTIVE_THRESHOLD_ENABLED and node is not None:
        # Get node emotion vector (if it has one)
        node_emotion = getattr(node, 'emotion_vector', None)

        if node_emotion is not None and active_affect is not None:
            h = compute_affective_threshold_reduction(
                active_affect=active_affect,
                node_emotion=node_emotion,
                node_id=node.id if node else "",
                citizen_id=citizen_id,
                frame_id=frame_id
            )
            theta_adjusted = theta_base - h

            # Emit telemetry event
            if settings.AFFECTIVE_TELEMETRY_ENABLED and h > 0.0:
                A_magnitude = float(np.linalg.norm(active_affect))
                E_magnitude = float(np.linalg.norm(node_emotion))
                dot_product = float(np.dot(active_affect, node_emotion))
                affective_alignment = dot_product / (A_magnitude * E_magnitude) if A_magnitude > 0 and E_magnitude > 0 else 0.0

                emit_affective_threshold(
                    citizen_id=citizen_id,
                    frame_id=frame_id or "",
                    node_id=node.id if node else "",
                    theta_base=theta_base,
                    theta_adjusted=theta_adjusted,
                    h=h,
                    affective_alignment=affective_alignment,
                    emotion_magnitude=E_magnitude
                )

    return theta_adjusted


def soft_activation(
    energy: float,
    threshold: float,
    kappa: float = KAPPA_DEFAULT
) -> float:
    """
    Compute soft activation using sigmoid.

    Formula: a = 1 / (1 + exp(-kappa * (e - theta)))

    Smooth transition around threshold:
    - e << theta: a ~= 0
    - e = theta: a = 0.5
    - e >> theta: a ~= 1

    Args:
        energy: Node energy
        threshold: Activation threshold
        kappa: Sharpness parameter (higher = steeper sigmoid)

    Returns:
        Soft activation value [0, 1]

    Example:
        >>> energy, threshold = 0.05, 0.03
        >>> a = soft_activation(energy, threshold, kappa=10.0)
        >>> print(f"Activation: {a:.3f}")
        Activation: 0.881  # Smoothly above threshold
    """
    return 1.0 / (1.0 + np.exp(-kappa * (energy - threshold)))


def hard_activation(
    energy: float,
    threshold: float
) -> bool:
    """
    Compute hard activation (binary).

    Args:
        energy: Node energy
        threshold: Activation threshold

    Returns:
        True if energy >= threshold, False otherwise

    Example:
        >>> hard_activation(0.05, 0.03)
        True
        >>> hard_activation(0.02, 0.03)
        False
    """
    return energy >= threshold


# --- Affective Coupling (PR-B) ---

def compute_affective_threshold_reduction(
    active_affect: Optional[np.ndarray],
    node_emotion: Optional[np.ndarray],
    node_id: str = "",
    citizen_id: str = "",
    frame_id: Optional[str] = None
) -> float:
    """
    Compute affective threshold reduction (PR-B: Emotion Couplings).

    Affect-congruent nodes get lower thresholds (easier to activate).
    This implements the bounded affect→threshold modulation.

    Formula:
        h = λ_aff · tanh(||A|| · cos(A, E_emo)) · clip(||E_emo||, 0, 1)

    Where:
        - λ_aff = AFFECTIVE_THRESHOLD_LAMBDA_FACTOR (default 0.08, ~8% reduction)
        - A = current affective state vector
        - E_emo = emotion vector on node
        - cos(A, E_emo) = cosine similarity (alignment)
        - ||·|| = L2 norm (magnitude)

    Returns positive h for aligned affect (reduces threshold).
    Returns 0 when disabled or when affect/emotion missing.

    Bounded: h ∈ [0, λ_aff] (max 8% threshold reduction by default)

    Args:
        active_affect: Current affective state vector (A)
        node_emotion: Emotion vector on node (E_emo)
        node_id: Node ID for telemetry
        citizen_id: Citizen ID for telemetry
        frame_id: Frame ID for telemetry

    Returns:
        Threshold reduction h (positive value)

    Example:
        >>> A = np.array([0.5, 0.5, 0.0])  # Moderate positive affect
        >>> E_emo = np.array([0.8, 0.6, 0.0])  # Node has positive emotion
        >>> h = compute_affective_threshold_reduction(A, E_emo, "node1", "felix", "frame_001")
        >>> # h ≈ 0.08 * tanh(0.707 * 0.98) * 1.0 ≈ 0.05 (5% reduction)
    """
    # Feature flag check
    if not settings.AFFECTIVE_THRESHOLD_ENABLED:
        return 0.0

    # Guard: need both affect and emotion vectors
    if active_affect is None or node_emotion is None:
        return 0.0

    if len(active_affect) == 0 or len(node_emotion) == 0:
        return 0.0

    # Compute magnitudes
    A_magnitude = float(np.linalg.norm(active_affect))
    E_magnitude = float(np.linalg.norm(node_emotion))

    # Guard: if either is zero, no modulation
    if A_magnitude < 1e-6 or E_magnitude < 1e-6:
        return 0.0

    # Compute cosine similarity (alignment)
    # cos(A, E_emo) = (A · E_emo) / (||A|| · ||E_emo||)
    dot_product = float(np.dot(active_affect, node_emotion))
    affective_alignment = dot_product / (A_magnitude * E_magnitude)

    # Clamp emotion magnitude to [0, 1]
    E_magnitude_clamped = min(max(E_magnitude, 0.0), 1.0)

    # Compute threshold reduction
    # h = λ_aff · tanh(||A|| · cos(A, E_emo)) · clip(||E_emo||, 0, 1)
    lambda_aff = settings.AFFECTIVE_THRESHOLD_LAMBDA_FACTOR
    inner_term = A_magnitude * affective_alignment
    h = lambda_aff * np.tanh(inner_term) * E_magnitude_clamped

    # h should be positive (we subtract it from threshold)
    # If alignment is negative (opposite affect), h becomes negative, which would RAISE threshold
    # Clamp h to [0, lambda_aff] to only allow reduction, not increase
    h = max(0.0, min(h, lambda_aff))

    # Emit telemetry event
    if settings.AFFECTIVE_TELEMETRY_ENABLED:
        # We don't know theta_base here, so we'll emit from the caller
        # Store values for caller to emit
        pass

    return float(h)


# --- Noise Statistics Tracking ---

class NoiseTracker:
    """
    Tracks noise statistics for node-subentity pairs using EMA.

    Maintains rolling statistics (mu, sigma) for threshold calculation.
    """

    def __init__(self, ema_alpha: float = 0.1):
        """
        Initialize noise tracker.

        Args:
            ema_alpha: EMA smoothing factor (0 < alpha < 1). Default 0.1.
        """
        self.ema_alpha = ema_alpha
        self.stats: Dict[str, NoiseStatistics] = {}  # Key: f"{node_id}_{subentity}"

    def _get_key(self, node_id: str, subentity: str) -> str:
        """Generate key for node-subentity pair."""
        return f"{node_id}_{subentity}"

    def get_stats(self, node_id: str, subentity: str) -> NoiseStatistics:
        """
        Get noise statistics for node-subentity pair.

        Returns:
            NoiseStatistics (creates default if not exists)
        """
        key = self._get_key(node_id, subentity)
        if key not in self.stats:
            self.stats[key] = NoiseStatistics()
        return self.stats[key]

    def update(self, node_id: str, subentity: str, energy: float, is_quiet: bool):
        """
        Update noise statistics with new energy sample.

        Only updates when node is "quiet" (no external stimuli).

        Args:
            node_id: Node identifier
            subentity: Subentity identifier
            energy: Current energy value
            is_quiet: True if node is quiet (suitable for noise sampling)
        """
        if not is_quiet:
            return

        stats = self.get_stats(node_id, subentity)

        # Update EMA for mu (mean)
        if stats.sample_count == 0:
            stats.mu = energy
        else:
            stats.mu = self.ema_alpha * energy + (1 - self.ema_alpha) * stats.mu

        # Update EMA for sigma (std dev) - using squared deviation
        if stats.sample_count == 0:
            stats.sigma = 0.01  # Initial guess
        else:
            deviation = abs(energy - stats.mu)
            stats.sigma = self.ema_alpha * deviation + (1 - self.ema_alpha) * stats.sigma

        stats.sample_count += 1


# --- Activation Computation ---

def compute_activation_mask(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, bool]:
    """
    Compute hard activation mask for all nodes.

    Threshold is same for all nodes (criticality-driven), so this is simple.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        ctx: Threshold configuration (with num_active, num_total set)

    Returns:
        Dict mapping node_id to activation bool

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     num_active=5,
        ...     num_total=50
        ... )
        >>> mask = compute_activation_mask(graph, "translator", ctx)
        >>> active_count = sum(mask.values())
        >>> print(f"Active nodes: {active_count}/{len(graph.nodes)}")
    """
    mask = {}

    # Compute threshold once (same for all nodes)
    threshold = compute_adaptive_threshold(None, subentity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(subentity)
        mask[node.id] = hard_activation(energy, threshold)

    return mask


def compute_activation_values(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, float]:
    """
    Compute soft activation values for all nodes.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        ctx: Threshold configuration (with num_active, num_total set)

    Returns:
        Dict mapping node_id to soft activation [0, 1]

    Example:
        >>> ctx = ThresholdContext(
        ...     base_threshold=1.0,
        ...     num_active=5,
        ...     num_total=50
        ... )
        >>> activations = compute_activation_values(graph, "translator", ctx)
        >>> print(f"Average activation: {np.mean(list(activations.values())):.3f}")
    """
    activations = {}

    # Compute threshold once (same for all nodes)
    threshold = compute_adaptive_threshold(None, subentity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(subentity)
        activations[node.id] = soft_activation(energy, threshold, ctx.kappa)

    return activations
