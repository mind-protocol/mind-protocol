"""
Mechanism: Energy & Weight Decay (Dual-Clock Forgetting)

ARCHITECTURAL PRINCIPLE: Two-Timescale Forgetting with Criticality Coupling

Implements BOTH:
1. Activation decay: E_i ← λ_E^Δt × E_i (fast, per-tick)
2. Weight decay: W ← λ_W^Δt × W (slow, periodic)

WHY TWO CLOCKS:
- Fast activation decay: vivid → vague → gone (hours)
- Slow weight decay: core ideas persist for weeks
- Prevents: structure erasure (same decay) or stickiness (no decay)

CONTROLLER COUPLING:
- Criticality controller adjusts effective δ_E within bounds
- Weight decay operates INDEPENDENTLY on slower horizons
- Never tie weight decay to ρ (different timescales)

SINGLE-ENERGY MODEL:
- Operates on node.E (total activation scalar), NOT per-entity buffers
- Type-dependent multipliers from settings.py
- Floor bounds prevent over-decay

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/decay.md
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from collections import defaultdict

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link
    from orchestration.core.types import NodeType

from orchestration.core.settings import settings


# === Data Classes ===

@dataclass
class DecayMetrics:
    """
    Complete decay metrics for observability.

    Emitted as `decay.tick` event per spec §6.
    """
    # Activation decay
    delta_E: float                          # Effective activation decay rate used
    nodes_decayed: int                      # Nodes with activation decay
    total_energy_before: float              # Energy before decay
    total_energy_after: float               # Energy after decay
    energy_lost: float                      # Energy removed by decay

    # Weight decay
    delta_W: float                          # Effective weight decay rate used
    nodes_weight_decayed: int               # Nodes with weight decay
    links_weight_decayed: int               # Links with weight decay

    # Half-life estimates per type
    half_lives_activation: Dict[str, float] # Type → half-life (seconds)
    half_lives_weight: Dict[str, float]     # Type → half-life (seconds)

    # Histograms
    energy_histogram: Dict[str, List[float]]  # Type → energy distribution
    weight_histogram: Dict[str, List[float]]  # Type → weight distribution

    # AUC tracking
    auc_activation_window: float            # Area under curve (activation)


@dataclass
class DecayContext:
    """
    Configuration for decay tick.

    Args:
        dt: Time duration for this tick (seconds). Default 1.0.
        effective_delta_E: Criticality-adjusted activation decay. If None, uses base from settings.
        apply_weight_decay: Whether to apply weight decay this tick. Default False (periodic).
        compute_histograms: Whether to compute expensive histograms. Default False (sampled).
    """
    dt: float = 1.0
    effective_delta_E: Optional[float] = None
    apply_weight_decay: bool = False
    compute_histograms: bool = False


# === Helper Functions ===

def compute_half_life(decay_rate: float) -> float:
    """
    Compute half-life from decay rate.

    Formula: t_half = ln(2) / decay_rate

    Args:
        decay_rate: Decay rate per second

    Returns:
        Half-life (seconds)
    """
    if decay_rate <= 0:
        return float('inf')
    return math.log(2) / decay_rate


def get_activation_decay_rate(node_type: str) -> float:
    """
    Get activation decay rate for node type.

    Formula: rate = EMACT_DECAY_BASE × multiplier[type]

    Args:
        node_type: Node type string

    Returns:
        Decay rate (per second)
    """
    multiplier = settings.EMACT_DECAY_MULTIPLIERS.get(node_type, 1.0)
    return settings.EMACT_DECAY_BASE * multiplier


def get_weight_decay_rate(node_type: str) -> float:
    """
    Get weight decay rate for node type.

    Formula: rate = WEIGHT_DECAY_BASE × multiplier[type]

    Args:
        node_type: Node type string

    Returns:
        Decay rate (per second)
    """
    multiplier = settings.WEIGHT_DECAY_MULTIPLIERS.get(node_type, 1.0)
    return settings.WEIGHT_DECAY_BASE * multiplier


# === Activation Decay ===

def decay_node_activation(
    node: 'Node',
    dt: float,
    effective_delta: Optional[float] = None,
    graph: Optional['Graph'] = None
) -> Tuple[float, float]:
    """
    Apply exponential decay to node activation energy (single E_i).

    Formula: E_i ← λ^Δt × E_i, where λ = exp(-rate)

    With controller coupling:
    - If effective_delta provided: use it (criticality-adjusted)
    - Otherwise: use type-dependent base rate

    With PR-E enrichments (optional, behind feature flags):
    - Consolidation: (λ^Δt)^c_total slows decay for important patterns
    - Resistance: λ^(Δt/r_i) extends half-life for central/bridge nodes

    Args:
        node: Node to decay
        dt: Time duration (seconds)
        effective_delta: Optional criticality-adjusted decay rate
        graph: Optional graph (for consolidation/resistance computation)

    Returns:
        Tuple of (energy_before, energy_after)
    """
    energy_before = node.E  # Single-energy architecture

    if energy_before < settings.ENERGY_FLOOR:
        # Already at floor, skip
        return (energy_before, energy_before)

    # Determine decay rate
    if effective_delta is not None:
        # Use criticality-adjusted rate (bounded)
        decay_rate = np.clip(
            effective_delta,
            settings.EMACT_DECAY_MIN,
            settings.EMACT_DECAY_MAX
        )
    else:
        # Use type-dependent base rate
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        decay_rate = get_activation_decay_rate(node_type)

    # === PR-E: Apply Decay Resistance (E.3) ===
    # Resistance divides the decay rate (extends half-life)
    if graph is not None:
        r_i = compute_decay_resistance(node, graph)
        effective_rate = decay_rate / r_i
    else:
        effective_rate = decay_rate

    # Compute base decay factor
    decay_factor = math.exp(-effective_rate * dt)

    # === PR-E: Apply Consolidation (E.2) ===
    # Consolidation powers the decay factor (brings it closer to 1, slowing decay)
    if graph is not None:
        c_total = compute_consolidation_factor(node, graph)
        if c_total > 0.0:
            # Raise to power: (λ^Δt)^c_total
            # When c_total < 1, this brings decay_factor closer to 1 (slower decay)
            decay_factor = decay_factor ** c_total

    energy_after = energy_before * decay_factor

    # Apply floor
    energy_after = max(energy_after, settings.ENERGY_FLOOR)

    # Write back
    node.E = energy_after  # Single-energy architecture

    return (energy_before, energy_after)


def activation_decay_tick(
    graph: 'Graph',
    dt: float,
    effective_delta: Optional[float] = None
) -> Tuple[int, float, float]:
    """
    Apply activation decay to all nodes in graph.

    Args:
        graph: Graph with nodes
        dt: Time duration (seconds)
        effective_delta: Optional criticality-adjusted decay rate

    Returns:
        Tuple of (nodes_decayed, total_energy_before, total_energy_after)
    """
    nodes_decayed = 0
    total_before = 0.0
    total_after = 0.0

    for node in graph.nodes.values():
        # Pass graph for consolidation/resistance computation (PR-E)
        before, after = decay_node_activation(node, dt, effective_delta, graph)

        if before > settings.ENERGY_FLOOR:
            total_before += before
            total_after += after
            nodes_decayed += 1

    return (nodes_decayed, total_before, total_after)


# === Weight Decay ===

def decay_node_weight(node: 'Node', dt: float) -> Tuple[float, float]:
    """
    Apply exponential decay to node weight (log scale).

    Formula: log_W ← log_W - (rate × dt)
    Equivalent to: W ← W × exp(-rate × dt)

    Args:
        node: Node to decay weight
        dt: Time duration (seconds)

    Returns:
        Tuple of (log_weight_before, log_weight_after)
    """
    log_weight_before = node.log_weight

    # Get type-dependent weight decay rate
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    decay_rate = get_weight_decay_rate(node_type)

    # Apply decay (log space: subtract)
    log_weight_after = log_weight_before - (decay_rate * dt)

    # Apply floor
    log_weight_after = max(log_weight_after, settings.WEIGHT_FLOOR)

    # Write back
    node.log_weight = log_weight_after

    return (log_weight_before, log_weight_after)


def decay_link_weight(link: 'Link', dt: float) -> Tuple[float, float]:
    """
    Apply exponential decay to link weight (log scale).

    Args:
        link: Link to decay weight
        dt: Time duration (seconds)

    Returns:
        Tuple of (log_weight_before, log_weight_after)
    """
    log_weight_before = link.log_weight

    # Get type-dependent weight decay rate (use link type)
    link_type = link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type)
    decay_rate = get_weight_decay_rate(link_type)

    # Apply decay
    log_weight_after = log_weight_before - (decay_rate * dt)

    # Apply floor
    log_weight_after = max(log_weight_after, settings.WEIGHT_FLOOR)

    # Write back
    link.log_weight = log_weight_after

    return (log_weight_before, log_weight_after)


def weight_decay_tick(graph: 'Graph', dt: float) -> Tuple[int, int]:
    """
    Apply weight decay to all nodes and links in graph.

    NOTE: This runs on SLOW cadence (not every tick).
    Typical: once per minute vs activation decay every tick.

    Args:
        graph: Graph with nodes and links
        dt: Time duration (seconds)

    Returns:
        Tuple of (nodes_decayed, links_decayed)
    """
    nodes_decayed = 0
    links_decayed = 0

    # Decay node weights
    for node in graph.nodes.values():
        decay_node_weight(node, dt)
        nodes_decayed += 1

    # Decay link weights
    for link in graph.links.values():
        decay_link_weight(link, dt)
        links_decayed += 1

    return (nodes_decayed, links_decayed)


# === Metrics & Observability ===

def compute_half_life_estimates(graph: 'Graph', weight_mode: bool = False) -> Dict[str, float]:
    """
    Compute half-life estimates per node type.

    Args:
        graph: Graph with nodes
        weight_mode: If True, compute weight decay half-lives; else activation

    Returns:
        Dict of type → half-life (seconds)
    """
    half_lives = {}

    # Get unique types
    types_seen = set()
    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        types_seen.add(node_type)

    # Compute half-life for each type
    for node_type in types_seen:
        if weight_mode:
            decay_rate = get_weight_decay_rate(node_type)
        else:
            decay_rate = get_activation_decay_rate(node_type)

        half_lives[node_type] = compute_half_life(decay_rate)

    return half_lives


def compute_energy_histogram(graph: 'Graph') -> Dict[str, List[float]]:
    """
    Compute energy distribution per node type.

    Returns:
        Dict of type → list of energy values
    """
    histogram = defaultdict(list)

    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        histogram[node_type].append(node.E)  # Single-energy architecture

    return dict(histogram)


def compute_weight_histogram(graph: 'Graph') -> Dict[str, List[float]]:
    """
    Compute weight distribution per node type.

    Returns:
        Dict of type → list of log_weight values
    """
    histogram = defaultdict(list)

    for node in graph.nodes.values():
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        histogram[node_type].append(node.log_weight)

    return dict(histogram)


# === Main Decay Tick ===

def decay_tick(graph: 'Graph', ctx: Optional[DecayContext] = None) -> DecayMetrics:
    """
    Execute one tick of decay (activation and optionally weight).

    Implements dual-clock forgetting per spec §2:
    - Activation decay: fast, per-tick, criticality-coupled
    - Weight decay: slow, periodic, independent

    Args:
        graph: Graph with nodes and links
        ctx: Decay configuration (defaults if None)

    Returns:
        DecayMetrics with comprehensive observability
    """
    if ctx is None:
        ctx = DecayContext()

    # === Activation Decay (always) ===
    nodes_decayed, total_before, total_after = activation_decay_tick(
        graph, ctx.dt, ctx.effective_delta_E
    )

    energy_lost = total_before - total_after

    # Determine effective delta used
    if ctx.effective_delta_E is not None:
        delta_E = ctx.effective_delta_E
    else:
        delta_E = settings.EMACT_DECAY_BASE  # Base rate

    # === Weight Decay (conditional) ===
    if ctx.apply_weight_decay:
        nodes_weight_decayed, links_weight_decayed = weight_decay_tick(graph, ctx.dt)
        delta_W = settings.WEIGHT_DECAY_BASE
    else:
        nodes_weight_decayed = 0
        links_weight_decayed = 0
        delta_W = 0.0

    # === Half-Life Estimates ===
    half_lives_activation = compute_half_life_estimates(graph, weight_mode=False)
    half_lives_weight = compute_half_life_estimates(graph, weight_mode=True)

    # === Histograms (expensive, sampled) ===
    if ctx.compute_histograms:
        energy_histogram = compute_energy_histogram(graph)
        weight_histogram = compute_weight_histogram(graph)
    else:
        energy_histogram = {}
        weight_histogram = {}

    # === AUC Activation (simplified: total energy) ===
    auc_activation_window = total_after

    return DecayMetrics(
        delta_E=delta_E,
        nodes_decayed=nodes_decayed,
        total_energy_before=total_before,
        total_energy_after=total_after,
        energy_lost=energy_lost,
        delta_W=delta_W,
        nodes_weight_decayed=nodes_weight_decayed,
        links_weight_decayed=links_weight_decayed,
        half_lives_activation=half_lives_activation,
        half_lives_weight=half_lives_weight,
        energy_histogram=energy_histogram,
        weight_histogram=weight_histogram,
        auc_activation_window=auc_activation_window
    )


# === PR-E: Foundations Enrichments ===

# E.2 Consolidation (prevents premature decay of important patterns)

def compute_consolidation_factor(node: 'Node', graph: 'Graph') -> float:
    """
    Compute consolidation factor c_total for this node.

    Consolidation slows decay for important patterns via:
    - c_retrieval: Node used in goal-serving (high WM presence)
    - c_affect: High emotional magnitude (||E_emo|| > 0.7)
    - c_goal: Unresolved goal link to active goal

    Formula: c_total = min(c_max, c_retrieval + c_affect + c_goal)

    Applied as: E_i ← (λ^Δt)^c_total × E_i

    Args:
        node: Node to compute consolidation for
        graph: Graph (for checking goal links)

    Returns:
        Consolidation factor ∈ [0, c_max]
    """
    from orchestration.core.settings import settings

    if not settings.CONSOLIDATION_ENABLED:
        return 0.0

    c_total = 0.0

    # c_retrieval: High WM presence indicates retrieval usage
    # Use ema_wm_presence as proxy for retrieval
    if hasattr(node, 'ema_wm_presence'):
        c_retrieval = settings.CONSOLIDATION_RETRIEVAL_BOOST * node.ema_wm_presence
        c_total += c_retrieval

    # c_affect: High emotional magnitude
    if hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
        emotion_magnitude = float(np.linalg.norm(node.emotion_vector))
        if emotion_magnitude > 0.7:  # High-affect threshold
            c_affect = settings.CONSOLIDATION_AFFECT_BOOST * (emotion_magnitude - 0.7) / 0.3
            c_total += np.clip(c_affect, 0.0, settings.CONSOLIDATION_AFFECT_BOOST)

    # c_goal: Unresolved goal link to active goal
    from orchestration.core.types import LinkType
    if hasattr(graph, 'nodes'):
        for link in node.outgoing_links:
            if link.link_type == LinkType.RELATES_TO and hasattr(link.target, 'node_type'):
                target_type = link.target.node_type.value if hasattr(link.target.node_type, 'value') else str(link.target.node_type)
                if target_type in ['Goal', 'Personal_Goal']:
                    # Check if goal is active
                    if link.target.is_active():
                        c_total += settings.CONSOLIDATION_GOAL_BOOST
                        break  # Only count once

    # Cap at max
    c_total = min(c_total, settings.CONSOLIDATION_MAX_FACTOR)

    return c_total


# E.3 Decay Resistance (central/bridge nodes persist longer)

def compute_decay_resistance(node: 'Node', graph: 'Graph') -> float:
    """
    Compute decay resistance factor r_i for this node.

    Resistance extends half-life for important structural nodes via:
    - r_deg: High centrality (degree-based)
    - r_bridge: Cross-entity bridges (multi-entity membership)
    - r_type: Type-based importance (Memory, Principle persist longer)

    Formula: r_i = min(r_max, r_deg · r_bridge · r_type)

    Applied as: E_i ← (λ^Δt / r_i) × E_i

    Args:
        node: Node to compute resistance for
        graph: Graph (for checking entity membership)

    Returns:
        Resistance factor ∈ [1.0, r_max]
    """
    from orchestration.core.settings import settings

    if not settings.DECAY_RESISTANCE_ENABLED:
        return 1.0  # No resistance

    # r_deg: Centrality-based resistance
    degree = len(node.outgoing_links) + len(node.incoming_links)
    r_deg = 1.0 + 0.1 * math.tanh(degree / 20.0)

    # r_bridge: Cross-entity bridge resistance
    # Count how many entities this node belongs to
    from orchestration.core.types import LinkType
    entity_count = 0
    if hasattr(graph, 'subentities'):
        for link in node.outgoing_links:
            if link.link_type == LinkType.MEMBER_OF:
                entity_count += 1

    if entity_count > 1:
        r_bridge = 1.0 + 0.15 * min(1.0, (entity_count - 1) / 5.0)
    else:
        r_bridge = 1.0

    # r_type: Type-based resistance
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    type_resistance_map = {
        "Memory": 1.2,
        "Episodic_Memory": 1.25,
        "Principle": 1.15,
        "Personal_Value": 1.15,
        "Task": 1.0,
        "Event": 1.0,
    }
    r_type = type_resistance_map.get(node_type, 1.0)

    # Combine
    r_i = r_deg * r_bridge * r_type

    # Cap at max
    r_i = min(r_i, settings.DECAY_RESISTANCE_MAX_FACTOR)

    return r_i
