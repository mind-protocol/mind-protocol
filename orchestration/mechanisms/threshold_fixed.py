"""
Mechanism 16 Part 1: Adaptive Activation Threshold

ARCHITECTURAL PRINCIPLE: Nodes Become Subentities via Threshold Crossing

"Every time a node reaches the threshold of activation from a sensory input,
it becomes a subentity." - Nicolas

Core Truth:
- NOT pre-defined subentities (Translator, Architect) - those are CLUSTERS of micro-subentities
- ANY node crossing activation threshold becomes its own subentity
- Subentity name = node name (simple one-to-one mapping)
- Thousands of simultaneous micro-subentities (normal and expected)
- Threshold is ADAPTIVE - derived from signal detection theory, modulated by system state

Layered Threshold Architecture:
1. Base Statistical (REQUIRED): Control false-positive rate via noise statistics
2. Criticality Modulation (OPTIONAL): Dampen when supercritical (Á > 1)
3. Load Modulation (OPTIONAL): Shed activations when over-budget
4. Goal Alignment (OPTIONAL): Lower threshold for goal-relevant nodes
5. Mood Alignment (OPTIONAL): Lower threshold for mood-congruent nodes
6. Episodic Prior (OPTIONAL): Lower threshold for recently-accessed nodes

Formula:
    ¸_{i,k} = (¼_{i,k} + z_± * Ã_{i,k})                    [BASE]
              × (1 + »_Á * max(0, Á - 1))                    [Criticality guard]
              × (1 + »_load * max(0, ”load))                 [Load shedding]
              × (1 - »_g * sim_{i,g})                        [Goal alignment]
              × (1 - »_m * mood_align_i)                     [Mood alignment]
              × (1 - »_a * anchor_i)                         [Episodic prior]

Activation test:
    node_is_active = (e_{i,k} >= ¸_{i,k})

Soft activation (recommended):
    a_{i,k} = sigmoid(º * (e_{i,k} - ¸_{i,k}))

Author: Felix (Engineer)
Created: 2025-10-19
Spec: Mechanism 16 Part 1 - Adaptive Activation Threshold
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

Z_ALPHA_DEFAULT: float = 1.28  # Z-score for 10% false-positive rate
KAPPA_DEFAULT: float = 10.0  # Soft activation sharpness
LAMBDA_RHO_DEFAULT: float = 0.5  # Criticality modulation strength
LAMBDA_LOAD_DEFAULT: float = 0.3  # Load modulation strength


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
        z_alpha: Z-score for false-positive tolerance. Default 1.28 (±=10%).
        kappa: Soft activation sharpness. Default 10.0.
        lambda_rho: Criticality modulation strength. Default 0.5.
        lambda_load: Load modulation strength. Default 0.3.
        spectral_radius: Current Á (criticality measure). Default None.
        load_delta: Relative compute overload (cost_used/budget - 1). Default 0.0.
    """
    z_alpha: float = Z_ALPHA_DEFAULT
    kappa: float = KAPPA_DEFAULT
    lambda_rho: float = LAMBDA_RHO_DEFAULT
    lambda_load: float = LAMBDA_LOAD_DEFAULT
    spectral_radius: Optional[float] = None
    load_delta: float = 0.0


# --- Threshold Calculation ---

def compute_base_threshold(
    mu: float,
    sigma: float,
    z_alpha: float
) -> float:
    """
    Compute base statistical threshold.

    Formula: ¸_base = ¼ + z_± * Ã

    This is the MINIMUM threshold - sets false-positive rate.

    Args:
        mu: Noise floor (mean energy when quiet)
        sigma: Noise variability (std dev when quiet)
        z_alpha: Z-score (e.g., 1.28 for ±=10%)

    Returns:
        Base threshold

    Example:
        >>> mu, sigma = 0.02, 0.01
        >>> theta_base = compute_base_threshold(mu, sigma, 1.28)
        >>> print(f"Base threshold: {theta_base:.3f}")
        Base threshold: 0.033  # ¼ + 1.28*Ã
    """
    return mu + z_alpha * sigma


def compute_adaptive_threshold(
    node: 'Node',
    subentity: 'EntityID',
    noise_stats: NoiseStatistics,
    ctx: ThresholdContext
) -> float:
    """
    Compute adaptive threshold for node-subentity pair.

    Applies layered modulation on top of base statistical threshold.

    Args:
        node: Node to compute threshold for
        subentity: Subentity identifier
        noise_stats: Noise statistics for this node-subentity pair
        ctx: Threshold configuration with modulation parameters

    Returns:
        Adaptive threshold value

    Example:
        >>> node = Node(...)
        >>> noise_stats = NoiseStatistics(mu=0.02, sigma=0.01)
        >>> ctx = ThresholdContext(spectral_radius=1.2, load_delta=0.1)
        >>> theta = compute_adaptive_threshold(node, "translator", noise_stats, ctx)
        >>> # Threshold raised due to supercritical state (Á=1.2 > 1)
    """
    # Layer 1: Base statistical threshold
    theta_base = compute_base_threshold(noise_stats.mu, noise_stats.sigma, ctx.z_alpha)

    # Layer 2: Criticality modulation (dampen when supercritical)
    criticality_factor = 1.0
    if ctx.spectral_radius is not None and ctx.spectral_radius > 1.0:
        criticality_factor = 1 + ctx.lambda_rho * (ctx.spectral_radius - 1.0)

    # Layer 3: Load modulation (shed activations when over-budget)
    load_factor = 1.0
    if ctx.load_delta > 0.0:
        load_factor = 1 + ctx.lambda_load * ctx.load_delta

    # Apply modulation
    theta_adaptive = theta_base * criticality_factor * load_factor

    return theta_adaptive


def soft_activation(
    energy: float,
    threshold: float,
    kappa: float = KAPPA_DEFAULT
) -> float:
    """
    Compute soft activation using sigmoid.

    Formula: a = 1 / (1 + exp(-º * (e - ¸)))

    Smooth transition around threshold:
    - e << ¸: a H 0
    - e = ¸: a = 0.5
    - e >> ¸: a H 1

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
    Tracks noise statistics for node-subentity pairs using EMA.

    Maintains rolling statistics (¼, Ã) for threshold calculation.
    """

    def __init__(self, ema_alpha: float = 0.1):
        """
        Initialize noise tracker.

        Args:
            ema_alpha: EMA smoothing factor (0 < ± < 1). Default 0.1.
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

        # Update EMA for ¼ (mean)
        if stats.sample_count == 0:
            stats.mu = energy
        else:
            stats.mu = self.ema_alpha * energy + (1 - self.ema_alpha) * stats.mu

        # Update EMA for Ã (std dev) - using squared deviation
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
    noise_tracker: NoiseTracker,
    ctx: ThresholdContext
) -> Dict[str, bool]:
    """
    Compute hard activation mask for all nodes.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        noise_tracker: Noise statistics tracker
        ctx: Threshold configuration

    Returns:
        Dict mapping node_id to activation bool

    Example:
        >>> mask = compute_activation_mask(graph, "translator", tracker, ctx)
        >>> active_count = sum(mask.values())
        >>> print(f"Active nodes: {active_count}/{len(graph.nodes)}")
    """
    mask = {}

    for node in graph.nodes:
        energy = node.get_entity_energy(subentity)
        noise_stats = noise_tracker.get_stats(node.id, subentity)
        threshold = compute_adaptive_threshold(node, subentity, noise_stats, ctx)

        mask[node.id] = hard_activation(energy, threshold)

    return mask


def compute_activation_values(
    graph: 'Graph',
    subentity: 'EntityID',
    noise_tracker: NoiseTracker,
    ctx: ThresholdContext
) -> Dict[str, float]:
    """
    Compute soft activation values for all nodes.

    Args:
        graph: Graph with nodes
        subentity: Subentity to compute activations for
        noise_tracker: Noise statistics tracker
        ctx: Threshold configuration

    Returns:
        Dict mapping node_id to soft activation [0, 1]

    Example:
        >>> activations = compute_activation_values(graph, "translator", tracker, ctx)
        >>> print(f"Average activation: {np.mean(list(activations.values())):.3f}")
    """
    activations = {}

    for node in graph.nodes:
        energy = node.get_entity_energy(subentity)
        noise_stats = noise_tracker.get_stats(node.id, subentity)
        threshold = compute_adaptive_threshold(node, subentity, noise_stats, ctx)

        activations[node.id] = soft_activation(energy, threshold, ctx.kappa)

    return activations
