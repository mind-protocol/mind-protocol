"""
Mechanism 09: Link Strengthening - Bounded Hebbian Learning

ARCHITECTURAL PRINCIPLE: "Cells that fire together, wire together" (Hebb)

Links strengthen when both endpoints have high energy simultaneously,
BUT ONLY when nodes are NOT already active (CORRECTED 2025-10-20).

"Link strengthening only happens when both nodes are not active. Because there
is going to be a lot of back-end force of energy between active nodes, this
should not change. It's only when you're adding something new that the
strengthening should happen." - Nicolas

Formula:
    delta_w = learning_rate * source_energy * target_energy * (1 - w/w_max)

Why Only When Inactive:
- Active nodes already have strong energy flow - strengthening them creates rich-get-richer runaway
- Strengthening should reinforce NEW patterns forming, not existing active patterns
- Prevents link weight inflation during sustained activation

Learning occurs:
- When both nodes have energy but are below activation threshold
- Proportional to activation product (correlation)
- With saturation bounds (min_weight, max_weight)

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-20 - Inverted condition to strengthen only when NOT active
Spec: Based on Nicolas's corrections 2025-10-20
"""

from typing import Dict, Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.link import Link
    from orchestration.core.node import Node
    from orchestration.core.types import EntityID

# --- Configuration ---

LEARNING_RATE_DEFAULT: float = 0.02  # Strengthening rate
MIN_WEIGHT: float = 0.0  # Minimum link weight
MAX_WEIGHT: float = 1.0  # Maximum link weight
ACTIVATION_THRESHOLD: float = 0.3  # Minimum energy for learning


@dataclass
class StrengtheningContext:
    """
    Configuration for link strengthening tick.

    Args:
        learning_rate: Rate of weight change per tick. Default 0.02.
        min_weight: Minimum link weight bound. Default 0.0.
        max_weight: Maximum link weight bound. Default 1.0.
        activation_threshold: Minimum energy to trigger learning. Default 0.3.
        active_nodes_only: If True, only strengthen links in workspace. Default False.
    """
    learning_rate: float = LEARNING_RATE_DEFAULT
    min_weight: float = MIN_WEIGHT
    max_weight: float = MAX_WEIGHT
    activation_threshold: float = ACTIVATION_THRESHOLD
    active_nodes_only: bool = False


# --- Strengthening Operations ---

def strengthen_link(
    link: 'Link',
    source_energy: float,
    target_energy: float,
    learning_rate: float,
    max_weight: float
) -> float:
    """
    Apply Hebbian strengthening to link.

    Formula: delta_w = learning_rate * source_energy * target_energy * (1 - w/w_max)

    The (1 - w/w_max) term provides saturation:
    - Weak links: Large updates
    - Strong links: Small updates (diminishing returns)
    - At max_weight: No updates (fully saturated)

    Args:
        link: Link to strengthen
        source_energy: Energy at source node
        target_energy: Energy at target node
        learning_rate: Strengthening rate
        max_weight: Maximum weight bound

    Returns:
        New weight after strengthening

    Example:
        >>> link = Link(source=n1, target=n2, weight=0.5)
        >>> new_weight = strengthen_link(link, 0.8, 0.7, 0.02, 1.0)
        >>> # Weight increased based on correlation
    """
    current_weight = link.weight

    # Hebbian update with saturation
    correlation = source_energy * target_energy
    saturation_factor = 1 - (current_weight / max_weight)
    delta_weight = learning_rate * correlation * saturation_factor

    # Apply update
    new_weight = current_weight + delta_weight

    # Clamp to max_weight
    new_weight = min(new_weight, max_weight)

    return new_weight


def strengthen_tick(
    graph: 'Graph',
    entity: 'EntityID',
    ctx: Optional[StrengtheningContext] = None,
    active_nodes: Optional[List['Node']] = None
) -> Dict[str, any]:
    """
    Execute one tick of Hebbian link strengthening for entity.

    Strengthens links where both endpoints have high energy.

    Algorithm:
    1. For each link in graph (or just active_nodes if specified)
    2. Get source and target energy for entity
    3. If both above threshold, strengthen link
    4. Clamp weight to [min_weight, max_weight]

    Args:
        graph: Graph with nodes and links
        entity: Entity to strengthen links for
        ctx: Strengthening configuration (defaults if None)
        active_nodes: Optional list of active nodes (if ctx.active_nodes_only=True)

    Returns:
        Metrics dict with:
        - links_strengthened: Number of links updated
        - total_weight_increase: Sum of all weight deltas
        - average_weight_increase: Mean weight delta (if any links strengthened)

    Example:
        >>> graph = Graph()
        >>> # ... populate graph ...
        >>> ctx = StrengtheningContext(learning_rate=0.02, activation_threshold=0.3)
        >>> metrics = strengthen_tick(graph, "translator", ctx)
        >>> print(f"Links strengthened: {metrics['links_strengthened']}")
    """
    if ctx is None:
        ctx = StrengtheningContext()

    links_strengthened = 0
    total_weight_increase = 0.0

    # Determine which links to process
    if ctx.active_nodes_only and active_nodes is not None:
        # Only strengthen links within active workspace
        active_node_ids = {node.id for node in active_nodes}
        links_to_process = [
            link for link in graph.links.values()
            if link.source.id in active_node_ids and link.target.id in active_node_ids
        ]
    else:
        # Strengthen all links in graph
        links_to_process = list(graph.links.values())

    for link in links_to_process:
        # Get energies
        source_energy = link.source.get_entity_energy(entity)
        target_energy = link.target.get_entity_energy(entity)

        # Check if both BELOW threshold (not active) but have some energy
        # Strengthening only happens when adding NEW patterns, not reinforcing active ones
        if (source_energy < ctx.activation_threshold and
            target_energy < ctx.activation_threshold and
            source_energy > 0.01 and
            target_energy > 0.01):
            # Strengthen link
            old_weight = link.weight
            new_weight = strengthen_link(
                link,
                source_energy,
                target_energy,
                ctx.learning_rate,
                ctx.max_weight
            )

            # Apply update
            link.weight = new_weight

            # Clamp to bounds
            link.weight = max(ctx.min_weight, min(link.weight, ctx.max_weight))

            # Track metrics
            weight_increase = link.weight - old_weight
            if weight_increase > 1e-10:
                links_strengthened += 1
                total_weight_increase += weight_increase

    average_weight_increase = (
        total_weight_increase / links_strengthened
        if links_strengthened > 0
        else 0.0
    )

    return {
        "links_strengthened": links_strengthened,
        "total_weight_increase": total_weight_increase,
        "average_weight_increase": average_weight_increase
    }


def weaken_link(
    link: 'Link',
    decay_rate: float,
    min_weight: float
) -> float:
    """
    Apply decay to link weight (forgetting).

    Optional mechanism for link weakening over time.
    Use sparingly - most forgetting happens via energy decay, not weight decay.

    Formula: w_new = w * exp(-decay_rate)

    Args:
        link: Link to weaken
        decay_rate: Weakening rate (exponential)
        min_weight: Minimum weight bound

    Returns:
        New weight after weakening

    Example:
        >>> link = Link(source=n1, target=n2, weight=0.8)
        >>> new_weight = weaken_link(link, decay_rate=0.01, min_weight=0.0)
        >>> # Weight decreased slightly
    """
    import math

    current_weight = link.weight
    new_weight = current_weight * math.exp(-decay_rate)

    # Clamp to min_weight
    new_weight = max(new_weight, min_weight)

    return new_weight


def compute_link_entropy(graph: 'Graph') -> float:
    """
    Compute Shannon entropy of link weight distribution.

    Measures diversity of connection strengths:
    - High entropy: Many links with similar weights (uniform)
    - Low entropy: Few strong links dominate (sparse)

    Args:
        graph: Graph with weighted links

    Returns:
        Entropy (nats)

    Example:
        >>> entropy = compute_link_entropy(graph)
        >>> print(f"Link diversity: {entropy:.3f} nats")
    """
    import numpy as np

    if len(graph.links) == 0:
        return 0.0

    weights = np.array([link.weight for link in graph.links.values()])
    total = weights.sum()

    if total < 1e-10:
        return 0.0

    # Normalize to probability distribution
    P = weights / total

    # Compute Shannon entropy
    P_nonzero = P[P > 1e-10]
    entropy = -np.sum(P_nonzero * np.log(P_nonzero))

    return float(entropy)
