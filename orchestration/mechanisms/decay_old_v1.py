"""
Mechanism 08: Energy Decay - Exponential Forgetting

ARCHITECTURAL PRINCIPLE: Type-Dependent Exponential Decay

Energy decays exponentially over time. Decay rate depends on node type:
- Memory nodes: Slow decay (long-term storage)
- Task nodes: Fast decay (temporal immediacy)
- Concept nodes: Medium decay (semantic stability)

Formula:
    e_new = e * exp(-decay_rate * duration)

Why Exponential (NOT linear):
- Biological realism: Neural activation decays exponentially
- Time-scale invariance: Same relative decay at any scale
- Continuous: Smooth transitions, no hard cutoffs

Decay prevents:
- Stale activations accumulating
- Graph saturation
- Runaway energy inflation

Author: Felix (Engineer)
Created: 2025-10-19
Spec: Phase 2 Mechanisms - Energy Decay
"""

import numpy as np
import math
from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.types import EntityID, NodeType

# --- Configuration ---

# Decay rates by node type (per second)
DECAY_RATES: Dict[str, float] = {
    "Memory": 0.01,        # Slow decay (half-life ~69 seconds)
    "Episodic_Memory": 0.005,  # Very slow (half-life ~138 seconds)
    "Concept": 0.02,       # Medium decay (half-life ~35 seconds)
    "Task": 0.1,           # Fast decay (half-life ~7 seconds)
    "Goal": 0.01,          # Slow (persistent goals)
    "Event": 0.05,         # Medium-fast (temporal relevance fades)
    "Person": 0.01,        # Slow (relationships persist)
    "Document": 0.015,     # Slow-medium
    "Mechanism": 0.02,     # Medium
    "Principle": 0.01,     # Slow (foundational knowledge)
    "Realization": 0.03,   # Medium (insights fade if not reinforced)
    "Default": 0.02        # Fallback for unlisted types
}

MINIMUM_ENERGY_THRESHOLD: float = 0.001  # Remove subentities below this threshold


@dataclass
class DecayContext:
    """
    Configuration for decay tick.

    Args:
        duration: Time duration for this tick (seconds). Default 0.1 (100ms).
        decay_rates: Optional override for decay rates by node type.
        min_threshold: Minimum energy before removal. Default 0.001.
    """
    duration: float = 0.1
    decay_rates: Optional[Dict[str, float]] = None
    min_threshold: float = MINIMUM_ENERGY_THRESHOLD


# --- Decay Operations ---

def get_decay_rate_for_type(node_type: str, decay_rates: Optional[Dict[str, float]] = None) -> float:
    """
    Get decay rate for node type.

    Args:
        node_type: Node type string (e.g., "Memory", "Task")
        decay_rates: Optional custom decay rates dict

    Returns:
        Decay rate (per second)

    Example:
        >>> get_decay_rate_for_type("Memory")
        0.01  # Slow decay
        >>> get_decay_rate_for_type("Task")
        0.1  # Fast decay
    """
    rates = decay_rates if decay_rates is not None else DECAY_RATES
    return rates.get(node_type, rates.get("Default", 0.02))


def decay_node_energy(
    node: 'Node',
    subentity: 'EntityID',
    duration: float,
    decay_rates: Optional[Dict[str, float]] = None
) -> float:
    """
    Apply exponential decay to subentity energy on node.

    Formula: e_new = e * exp(-decay_rate * duration)

    Args:
        node: Node to decay
        subentity: Subentity to decay energy for
        duration: Time duration (seconds)
        decay_rates: Optional custom decay rates

    Returns:
        New energy value after decay

    Example:
        >>> node = Node(...)
        >>> node.set_entity_energy("translator", 1.0)
        >>> new_energy = decay_node_energy(node, "translator", duration=1.0)
        >>> # Energy decayed based on node type
    """
    current_energy = node.get_entity_energy(subentity)

    if current_energy < 1e-10:
        return 0.0

    # Get type-specific decay rate
    decay_rate = get_decay_rate_for_type(node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type), decay_rates)

    # Exponential decay
    decay_factor = math.exp(-decay_rate * duration)
    new_energy = current_energy * decay_factor

    # Apply via node method (handles saturation and cleanup)
    node.set_entity_energy(subentity, new_energy)

    return new_energy


def decay_tick(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: Optional[DecayContext] = None
) -> Dict[str, float]:
    """
    Execute one tick of energy decay for subentity across entire graph.

    Applies type-dependent exponential decay to all nodes.

    Args:
        graph: Graph with nodes
        subentity: Subentity to decay energy for
        ctx: Decay configuration (defaults if None)

    Returns:
        Metrics dict with:
        - nodes_decayed: Number of nodes with energy decay applied
        - total_energy_before: Total energy before decay
        - total_energy_after: Total energy after decay
        - energy_lost: Total energy removed by decay

    Example:
        >>> graph = Graph()
        >>> # ... populate graph ...
        >>> ctx = DecayContext(duration=0.1)
        >>> metrics = decay_tick(graph, "translator", ctx)
        >>> print(f"Energy lost: {metrics['energy_lost']:.3f}")
    """
    if ctx is None:
        ctx = DecayContext()

    nodes_decayed = 0
    total_before = 0.0
    total_after = 0.0

    for node in graph.nodes.values():
        energy_before = node.get_entity_energy(subentity)

        if energy_before > 1e-10:
            total_before += energy_before

            # Apply decay
            energy_after = decay_node_energy(
                node,
                subentity,
                ctx.duration,
                ctx.decay_rates
            )

            total_after += energy_after
            nodes_decayed += 1

    energy_lost = total_before - total_after

    return {
        "nodes_decayed": nodes_decayed,
        "total_energy_before": total_before,
        "total_energy_after": total_after,
        "energy_lost": energy_lost
    }


def compute_half_life(decay_rate: float) -> float:
    """
    Compute half-life from decay rate.

    Half-life: Time for energy to decay to 50%

    Formula: t_half = ln(2) / decay_rate

    Args:
        decay_rate: Decay rate (per second)

    Returns:
        Half-life (seconds)

    Example:
        >>> decay_rate = 0.01  # Memory nodes
        >>> half_life = compute_half_life(decay_rate)
        >>> print(f"Memory half-life: {half_life:.1f} seconds")
        Memory half-life: 69.3 seconds
    """
    return math.log(2) / decay_rate
