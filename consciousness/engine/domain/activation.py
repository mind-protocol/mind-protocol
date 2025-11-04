# -*- coding: utf-8 -*-
"""
Spreading Activation - Pure activation spread functions for consciousness

This module provides pure spreading activation algorithms for the facade architecture:
- Active node selection (threshold-based)
- Frontier computation (activation wave)
- Neighbor discovery (1-hop, n-hop)
- Activation wave propagation

Design:
  - Pure functions (read-only, no mutations)
  - No external dependencies (standalone)
  - Testable, composable, predictable

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Phase: Migration Phase 2 - Spreading Activation
"""

from typing import Set, Dict, List, Tuple, Any
import math

from consciousness.engine.constants import DEFAULT_ACTIVATION_THRESHOLD, DEFAULT_MAX_DISTANCE

__all__ = [
    "select_active_nodes",
    "compute_frontier",
    "compute_neighbors",
    "compute_n_hop_neighbors",
    "compute_activation_distances",
    "filter_by_activation_strength",
]


# === Active Node Selection ===


def select_active_nodes(
    graph: Any,
    threshold: float = DEFAULT_ACTIVATION_THRESHOLD
) -> Set[str]:
    """
    Select nodes with energy above activation threshold.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes (expects nodes dict with .E attribute)
        threshold: Minimum energy for activation (default: 0.5)

    Returns:
        Set of node IDs that are active (E >= threshold)

    Example:
        >>> active = select_active_nodes(graph, threshold=0.5)
        >>> print(f"Active nodes: {len(active)}")
        Active nodes: 15
    """
    return {
        node.id for node in graph.nodes.values()
        if node.E >= threshold
    }


# === Frontier Computation ===


def compute_frontier(
    graph: Any,
    active_nodes: Set[str],
    exclude_active: bool = True
) -> Set[str]:
    """
    Compute activation frontier (1-hop neighbors of active nodes).

    Pure function: Read-only, no mutations.

    The frontier represents the "wave" of spreading activation -
    nodes that are one step away from currently active nodes.

    Args:
        graph: Graph with nodes and links
        active_nodes: Set of currently active node IDs
        exclude_active: If True, remove active nodes from frontier (default: True)

    Returns:
        Set of node IDs in the activation frontier

    Example:
        >>> active = select_active_nodes(graph)
        >>> frontier = compute_frontier(graph, active)
        >>> print(f"Frontier size: {len(frontier)}")
        Frontier size: 47
    """
    frontier = set()

    for node_id in active_nodes:
        node = graph.nodes.get(node_id)
        if node:
            # Add all outgoing neighbors
            for link in node.outgoing_links:
                frontier.add(link.target.id)

    if exclude_active:
        # Remove already-active nodes (shadow = frontier - active)
        frontier -= active_nodes

    return frontier


# === Neighbor Discovery ===


def compute_neighbors(
    graph: Any,
    node_id: str,
    direction: str = "outgoing"
) -> Set[str]:
    """
    Compute direct neighbors (1-hop) of a node.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes and links
        node_id: Source node ID
        direction: "outgoing", "incoming", or "both" (default: "outgoing")

    Returns:
        Set of neighbor node IDs

    Example:
        >>> neighbors = compute_neighbors(graph, "memory_123", direction="both")
        >>> print(f"Neighbors: {len(neighbors)}")
        Neighbors: 8
    """
    node = graph.nodes.get(node_id)
    if not node:
        return set()

    neighbors = set()

    if direction in ["outgoing", "both"]:
        for link in node.outgoing_links:
            neighbors.add(link.target.id)

    if direction in ["incoming", "both"]:
        for link in node.incoming_links:
            neighbors.add(link.source.id)

    return neighbors


def compute_n_hop_neighbors(
    graph: Any,
    start_node_id: str,
    max_hops: int = 2,
    direction: str = "outgoing"
) -> Dict[int, Set[str]]:
    """
    Compute neighbors at multiple hop distances (BFS).

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes and links
        start_node_id: Starting node ID
        max_hops: Maximum number of hops (default: 2)
        direction: "outgoing", "incoming", or "both" (default: "outgoing")

    Returns:
        Dict mapping hop distance to set of node IDs at that distance
        {0: {start_node}, 1: {1-hop neighbors}, 2: {2-hop neighbors}, ...}

    Example:
        >>> hops = compute_n_hop_neighbors(graph, "memory_123", max_hops=3)
        >>> print(f"1-hop: {len(hops[1])}, 2-hop: {len(hops[2])}")
        1-hop: 8, 2-hop: 35
    """
    visited = {start_node_id}
    current_frontier = {start_node_id}
    result = {0: {start_node_id}}

    for hop in range(1, max_hops + 1):
        next_frontier = set()

        for node_id in current_frontier:
            neighbors = compute_neighbors(graph, node_id, direction)

            # Only add unvisited neighbors
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    next_frontier.add(neighbor_id)
                    visited.add(neighbor_id)

        result[hop] = next_frontier
        current_frontier = next_frontier

        # Stop if no more nodes to explore
        if not current_frontier:
            break

    return result


# === Activation Distance & Strength ===


def compute_activation_distances(
    graph: Any,
    active_nodes: Set[str],
    max_distance: int = DEFAULT_MAX_DISTANCE
) -> Dict[str, int]:
    """
    Compute minimum distance from each node to nearest active node.

    Pure function: Read-only, no mutations.

    Uses BFS from all active nodes simultaneously to find shortest
    paths. Useful for activation attenuation (closer = stronger).

    Args:
        graph: Graph with nodes and links
        active_nodes: Set of currently active node IDs
        max_distance: Maximum distance to compute (default: 3)

    Returns:
        Dict mapping node ID to minimum distance from active set
        Active nodes have distance 0, 1-hop neighbors have distance 1, etc.

    Example:
        >>> active = select_active_nodes(graph)
        >>> distances = compute_activation_distances(graph, active, max_distance=3)
        >>> nearby = {nid for nid, d in distances.items() if d <= 2}
        >>> print(f"Nodes within 2 hops: {len(nearby)}")
        Nodes within 2 hops: 89
    """
    # Initialize: active nodes have distance 0
    distances = {node_id: 0 for node_id in active_nodes}
    current_frontier = set(active_nodes)

    for distance in range(1, max_distance + 1):
        next_frontier = set()

        for node_id in current_frontier:
            neighbors = compute_neighbors(graph, node_id, direction="outgoing")

            for neighbor_id in neighbors:
                # Only assign distance if not yet visited
                if neighbor_id not in distances:
                    distances[neighbor_id] = distance
                    next_frontier.add(neighbor_id)

        current_frontier = next_frontier

        # Stop if no more nodes to explore
        if not current_frontier:
            break

    return distances


def filter_by_activation_strength(
    graph: Any,
    nodes: Set[str],
    min_energy: float = DEFAULT_ACTIVATION_THRESHOLD,
    max_distance_from_active: int = 2,
    active_nodes: Set[str] = None
) -> Set[str]:
    """
    Filter nodes by activation strength criteria.

    Pure function: Read-only, no mutations.

    Combines energy threshold and distance from active set to
    select nodes with strong activation potential.

    Args:
        graph: Graph with nodes
        nodes: Set of candidate node IDs to filter
        min_energy: Minimum energy threshold (default: 0.5)
        max_distance_from_active: Maximum hops from active set (default: 2)
        active_nodes: Set of active node IDs (computed if None)

    Returns:
        Filtered set of node IDs meeting criteria

    Example:
        >>> candidates = compute_frontier(graph, active)
        >>> strong = filter_by_activation_strength(
        ...     graph, candidates,
        ...     min_energy=0.3,
        ...     max_distance_from_active=1
        ... )
        >>> print(f"Strong frontier nodes: {len(strong)}")
        Strong frontier nodes: 23
    """
    # Compute active nodes if not provided
    if active_nodes is None:
        active_nodes = select_active_nodes(graph, threshold=min_energy)

    # Compute distances from active set
    distances = compute_activation_distances(graph, active_nodes, max_distance=max_distance_from_active)

    # Filter by energy and distance
    filtered = set()
    for node_id in nodes:
        node = graph.nodes.get(node_id)
        if node and node.E >= min_energy:
            # Check distance (nodes not in distances dict are too far)
            if node_id in distances and distances[node_id] <= max_distance_from_active:
                filtered.add(node_id)

    return filtered


# === Activation Wave Statistics ===


def compute_activation_statistics(
    graph: Any,
    threshold: float = DEFAULT_ACTIVATION_THRESHOLD
) -> Dict[str, Any]:
    """
    Compute comprehensive activation statistics for graph.

    Pure function: Read-only, no mutations.

    Args:
        graph: Graph with nodes
        threshold: Energy threshold for activation (default: 0.5)

    Returns:
        Dict with statistics:
        - active_nodes: Set of active node IDs
        - active_count: Number of active nodes
        - frontier: Set of frontier node IDs
        - frontier_count: Size of frontier
        - activation_ratio: Fraction of nodes that are active
        - frontier_to_active_ratio: Frontier size / active size

    Example:
        >>> stats = compute_activation_statistics(graph)
        >>> print(f"Active: {stats['active_count']}, Frontier: {stats['frontier_count']}")
        Active: 47, Frontier: 89
    """
    active = select_active_nodes(graph, threshold)
    frontier = compute_frontier(graph, active, exclude_active=True)

    total_nodes = len(graph.nodes)
    activation_ratio = len(active) / total_nodes if total_nodes > 0 else 0.0
    frontier_to_active = len(frontier) / len(active) if len(active) > 0 else 0.0

    return {
        "active_nodes": active,
        "active_count": len(active),
        "frontier": frontier,
        "frontier_count": len(frontier),
        "total_nodes": total_nodes,
        "activation_ratio": activation_ratio,
        "frontier_to_active_ratio": frontier_to_active,
    }
