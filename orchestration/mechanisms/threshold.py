"""
Mechanism 16 Part 1: Adaptive Activation Threshold

ARCHITECTURAL PRINCIPLE: Nodes Become Entities via Threshold Crossing

"Every time a node reaches the threshold of activation from a sensory input,
it becomes a sub-entity." - Nicolas

Core Truth (CORRECTED 2025-10-20):
- NOT pre-defined entities (Translator, Architect) - those are CLUSTERS of micro-entities
- ANY node crossing activation threshold becomes its own sub-entity
- Entity name = node name (simple one-to-one mapping)
- Thousands of simultaneous micro-entities (normal and expected)
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
    entity: 'EntityID',
    ctx: ThresholdContext
) -> float:
    """
    Compute adaptive threshold for node-entity pair.

    Threshold driven by system criticality (number of active nodes).

    Formula:
        theta = BASE_THRESHOLD * (1 + CRITICALITY_FACTOR * (num_active / num_total))

    More active nodes = higher threshold = harder to activate more nodes.
    This prevents runaway activation.

    Args:
        node: Node to compute threshold for
        entity: Entity identifier
        ctx: Threshold configuration with criticality state

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
    theta = ctx.base_threshold * (1.0 + ctx.criticality_factor * criticality_ratio)

    return theta


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


# --- Noise Statistics Tracking ---

class NoiseTracker:
    """
    Tracks noise statistics for node-entity pairs using EMA.

    Maintains rolling statistics (mu, sigma) for threshold calculation.
    """

    def __init__(self, ema_alpha: float = 0.1):
        """
        Initialize noise tracker.

        Args:
            ema_alpha: EMA smoothing factor (0 < alpha < 1). Default 0.1.
        """
        self.ema_alpha = ema_alpha
        self.stats: Dict[str, NoiseStatistics] = {}  # Key: f"{node_id}_{entity}"

    def _get_key(self, node_id: str, entity: str) -> str:
        """Generate key for node-entity pair."""
        return f"{node_id}_{entity}"

    def get_stats(self, node_id: str, entity: str) -> NoiseStatistics:
        """
        Get noise statistics for node-entity pair.

        Returns:
            NoiseStatistics (creates default if not exists)
        """
        key = self._get_key(node_id, entity)
        if key not in self.stats:
            self.stats[key] = NoiseStatistics()
        return self.stats[key]

    def update(self, node_id: str, entity: str, energy: float, is_quiet: bool):
        """
        Update noise statistics with new energy sample.

        Only updates when node is "quiet" (no external stimuli).

        Args:
            node_id: Node identifier
            entity: Entity identifier
            energy: Current energy value
            is_quiet: True if node is quiet (suitable for noise sampling)
        """
        if not is_quiet:
            return

        stats = self.get_stats(node_id, entity)

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
    entity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, bool]:
    """
    Compute hard activation mask for all nodes.

    Threshold is same for all nodes (criticality-driven), so this is simple.

    Args:
        graph: Graph with nodes
        entity: Entity to compute activations for
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
    threshold = compute_adaptive_threshold(None, entity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(entity)
        mask[node.id] = hard_activation(energy, threshold)

    return mask


def compute_activation_values(
    graph: 'Graph',
    entity: 'EntityID',
    ctx: ThresholdContext
) -> Dict[str, float]:
    """
    Compute soft activation values for all nodes.

    Args:
        graph: Graph with nodes
        entity: Entity to compute activations for
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
    threshold = compute_adaptive_threshold(None, entity, ctx)

    for node in graph.nodes.values():
        energy = node.get_entity_energy(entity)
        activations[node.id] = soft_activation(energy, threshold, ctx.kappa)

    return activations
