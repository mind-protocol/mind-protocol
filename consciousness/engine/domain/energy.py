# -*- coding: utf-8 -*-
"""
Energy Dynamics - Pure energy calculation functions for consciousness

This module provides pure energy dynamics functions for the facade architecture:
- Energy clamping and normalization
- Energy statistics and metrics
- Activation thresholds
- Energy state snapshots

Design:
  - Pure functions (no I/O, no side effects on graph)
  - No external dependencies (standalone)
  - Testable, composable, predictable

NOTE: Decay and strengthening mechanisms remain in orchestration/mechanisms/
      (already pure and well-tested). This module provides facade-level helpers.

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Phase: Migration Phase 1 - Energy Dynamics
"""

from typing import Dict, Any
import math

# Re-export for facade API
__all__ = [
    # Facade helpers
    "clamp_energy",
    "normalize_energy",
    "compute_total_energy",
    "compute_active_nodes",
    "compute_average_energy",
    "apply_energy_delta",
    "compute_energy_ratio",
    "compute_energy_statistics",
]


# === Facade Helper Functions ===


def clamp_energy(energy: float, min_energy: float = 0.0, max_energy: float = 100.0) -> float:
    """
    Clamp energy value to valid range.

    Pure function: No side effects.

    Args:
        energy: Energy value to clamp
        min_energy: Minimum allowed energy (default: 0.0)
        max_energy: Maximum allowed energy (default: 100.0)

    Returns:
        Clamped energy value

    Example:
        >>> clamp_energy(150.0, 0.0, 100.0)
        100.0
        >>> clamp_energy(-10.0, 0.0, 100.0)
        0.0
    """
    return max(min_energy, min(max_energy, energy))


def normalize_energy(energy: float, max_energy: float = 100.0) -> float:
    """
    Normalize energy to [0, 1] range.

    Pure function: No side effects.

    Args:
        energy: Energy value to normalize
        max_energy: Maximum energy for normalization (default: 100.0)

    Returns:
        Normalized energy ∈ [0, 1]

    Example:
        >>> normalize_energy(50.0, 100.0)
        0.5
        >>> normalize_energy(100.0, 100.0)
        1.0
    """
    if max_energy <= 0:
        return 0.0
    return energy / max_energy


def compute_total_energy(graph: 'Graph') -> float:
    """
    Compute total activation energy across all nodes.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes

    Returns:
        Sum of all node energies

    Example:
        >>> graph = Graph()
        >>> graph.add_node(Node(id="a", E=50.0))
        >>> graph.add_node(Node(id="b", E=30.0))
        >>> compute_total_energy(graph)
        80.0
    """
    return sum(node.E for node in graph.nodes.values())


def compute_active_nodes(graph: 'Graph', threshold: float = 0.5) -> int:
    """
    Count number of active nodes (E > threshold).

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes
        threshold: Energy threshold for considering node "active" (default: 0.5)

    Returns:
        Number of nodes with E > threshold

    Example:
        >>> graph = Graph()
        >>> graph.add_node(Node(id="a", E=50.0))
        >>> graph.add_node(Node(id="b", E=0.3))
        >>> compute_active_nodes(graph, threshold=0.5)
        1
    """
    return sum(1 for node in graph.nodes.values() if node.E > threshold)


def compute_average_energy(graph: 'Graph') -> float:
    """
    Compute average activation energy across all nodes.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes

    Returns:
        Average energy (0.0 if no nodes)

    Example:
        >>> graph = Graph()
        >>> graph.add_node(Node(id="a", E=50.0))
        >>> graph.add_node(Node(id="b", E=30.0))
        >>> compute_average_energy(graph)
        40.0
    """
    if not graph.nodes:
        return 0.0
    return compute_total_energy(graph) / len(graph.nodes)


def apply_energy_delta(
    current_energy: float,
    delta: float,
    min_energy: float = 0.0,
    max_energy: float = 100.0
) -> float:
    """
    Apply energy delta and clamp to valid range.

    Pure function: No side effects.

    Args:
        current_energy: Current energy value
        delta: Energy change (positive = increase, negative = decrease)
        min_energy: Minimum allowed energy (default: 0.0)
        max_energy: Maximum allowed energy (default: 100.0)

    Returns:
        New energy after applying delta and clamping

    Example:
        >>> apply_energy_delta(50.0, 60.0, 0.0, 100.0)
        100.0  # Clamped at max
        >>> apply_energy_delta(50.0, -60.0, 0.0, 100.0)
        0.0  # Clamped at min
        >>> apply_energy_delta(50.0, 20.0, 0.0, 100.0)
        70.0
    """
    new_energy = current_energy + delta
    return clamp_energy(new_energy, min_energy, max_energy)


def compute_energy_ratio(
    current_energy: float,
    max_energy: float = 100.0
) -> float:
    """
    Compute energy as ratio of maximum (normalized to [0, 1]).

    Alias for normalize_energy() with more descriptive name.

    Pure function: No side effects.

    Args:
        current_energy: Current energy value
        max_energy: Maximum energy (default: 100.0)

    Returns:
        Energy ratio ∈ [0, 1]
    """
    return normalize_energy(current_energy, max_energy)


# === Energy State Snapshots ===


def compute_energy_statistics(graph: 'Graph', max_energy: float = 100.0) -> Dict[str, float]:
    """
    Compute comprehensive energy statistics for graph.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes
        max_energy: Maximum energy for normalization (default: 100.0)

    Returns:
        Dict with statistics:
        - total_energy: Sum of all node energies
        - average_energy: Mean energy across nodes
        - normalized_energy: Average energy as ratio of max
        - active_nodes: Count of nodes with E > 0.5
        - total_nodes: Total node count
        - max_node_energy: Highest single node energy
        - min_node_energy: Lowest single node energy

    Example:
        >>> stats = compute_energy_statistics(graph)
        >>> stats['total_energy']
        250.0
        >>> stats['active_nodes']
        15
    """
    if not graph.nodes:
        return {
            "total_energy": 0.0,
            "average_energy": 0.0,
            "normalized_energy": 0.0,
            "active_nodes": 0,
            "total_nodes": 0,
            "max_node_energy": 0.0,
            "min_node_energy": 0.0,
        }

    energies = [node.E for node in graph.nodes.values()]
    total = sum(energies)
    average = total / len(energies)
    normalized = normalize_energy(average, max_energy)
    active = compute_active_nodes(graph, threshold=0.5)

    return {
        "total_energy": total,
        "average_energy": average,
        "normalized_energy": normalized,
        "active_nodes": active,
        "total_nodes": len(graph.nodes),
        "max_node_energy": max(energies),
        "min_node_energy": min(energies),
    }
