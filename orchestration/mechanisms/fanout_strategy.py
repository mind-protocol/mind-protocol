"""
Fanout Strategy - Local bottom-up topology adaptation

Implements adaptive candidate pruning based on outdegree:
- High fanout (d > 10): Selective (top-k=5)
- Medium fanout (3 <= d <= 10): Balanced (top-k=d/2)
- Low fanout (d < 3): Exhaustive (all edges)

With optional WM pressure modulation and top-K energy splitting.

Architecture:
- Strategy selection: Based on local outdegree only (no global topology)
- Candidate pruning: Pre-filter by quick heuristic (weight) before cost computation
- WM adaptation: Reduce top-k under working memory pressure
- Top-K split: Optional softmax energy distribution across K best links

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/runtime_engine/fanout_strategy.md
"""

import math
from enum import Enum
from typing import List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.link import Link


@dataclass
class FanoutConfig:
    """
    Configuration for fanout strategy selection.

    Attributes:
        fanout_low: Low fanout threshold. Default 3.
        fanout_high: High fanout threshold. Default 10.
        selective_topk: K for selective strategy (high fanout). Default 5.
        topk_split_enabled: Enable top-K energy distribution. Default False.
        topk_split_k: K for energy splitting. Default 3.
        topk_split_temperature: Softmax temperature. Default 1.0.
        wm_pressure_enabled: Enable WM pressure modulation. Default True.
        wm_pressure_threshold: WM headroom threshold (0-1). Default 0.2 (20%).
        wm_pressure_reduction: Reduction factor under pressure. Default 0.6 (40% cut).
        min_topk: Floor on top_k to prevent over-pruning. Default 2.
    """
    fanout_low: int = 3
    fanout_high: int = 10
    selective_topk: int = 5
    topk_split_enabled: bool = False
    topk_split_k: int = 3
    topk_split_temperature: float = 1.0
    wm_pressure_enabled: bool = True
    wm_pressure_threshold: float = 0.2
    wm_pressure_reduction: float = 0.6
    min_topk: int = 2


class FanoutStrategy(Enum):
    """
    Fanout strategy types.

    SELECTIVE: High fanout nodes (hubs) - prune to small top-k
    BALANCED: Medium fanout - prune to ~50% of edges
    EXHAUSTIVE: Low fanout - evaluate all edges
    """
    SELECTIVE = "selective"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"


def select_strategy(
    outdegree: int,
    wm_headroom: Optional[float] = None,
    config: Optional[FanoutConfig] = None
) -> Tuple[FanoutStrategy, int]:
    """
    Select fanout strategy based on outdegree and WM pressure.

    Algorithm (spec §2.1):
    - High fanout (d > τ_high): Selective(top_k = k_high)
    - Medium (τ_low ≤ d ≤ τ_high): Balanced(top_k = round(d/2))
    - Low (d < τ_low): Exhaustive()
    - WM pressure: if headroom < threshold, reduce top_k by reduction factor

    Args:
        outdegree: Number of outgoing edges from node
        wm_headroom: Optional WM headroom (0-1, where 1=completely free)
        config: Fanout configuration (defaults if None)

    Returns:
        Tuple of (strategy, top_k)

    Example:
        >>> # High fanout node
        >>> strategy, k = select_strategy(outdegree=50)
        >>> # Returns (SELECTIVE, 5)
        >>>
        >>> # Medium fanout
        >>> strategy, k = select_strategy(outdegree=6)
        >>> # Returns (BALANCED, 3)
        >>>
        >>> # Low fanout
        >>> strategy, k = select_strategy(outdegree=2)
        >>> # Returns (EXHAUSTIVE, 2)
        >>>
        >>> # With WM pressure
        >>> strategy, k = select_strategy(outdegree=50, wm_headroom=0.1)
        >>> # Returns (SELECTIVE, 3) - reduced from 5 due to pressure
    """
    if config is None:
        config = FanoutConfig()

    # Base strategy from outdegree
    if outdegree > config.fanout_high:
        strategy = FanoutStrategy.SELECTIVE
        top_k = config.selective_topk
    elif outdegree >= config.fanout_low:
        strategy = FanoutStrategy.BALANCED
        top_k = max(1, outdegree // 2)
    else:
        strategy = FanoutStrategy.EXHAUSTIVE
        top_k = outdegree

    # WM pressure modulation (spec §2.1)
    if config.wm_pressure_enabled and wm_headroom is not None:
        if wm_headroom < config.wm_pressure_threshold:
            # Reduce top_k under pressure
            top_k = int(top_k * config.wm_pressure_reduction)
            top_k = max(config.min_topk, top_k)  # Floor to prevent over-pruning

    return strategy, top_k


def reduce_candidates(
    edges: List['Link'],
    strategy: FanoutStrategy,
    top_k: int
) -> List['Link']:
    """
    Prune edges based on fanout strategy.

    Uses quick heuristic (link log_weight) for pre-filtering.
    Full cost computation happens on reduced set.

    Algorithm (spec §2.1):
    - EXHAUSTIVE: Return all edges
    - SELECTIVE/BALANCED: Sort by log_weight, take top_k

    Args:
        edges: All outgoing edges from node
        strategy: Selected fanout strategy
        top_k: Number of candidates to keep

    Returns:
        Pruned edge list

    Example:
        >>> # Hub with 100 edges, selective strategy
        >>> pruned = reduce_candidates(edges, FanoutStrategy.SELECTIVE, top_k=5)
        >>> len(pruned)  # 5 (top by weight)
        >>>
        >>> # Low fanout, exhaustive
        >>> pruned = reduce_candidates(edges, FanoutStrategy.EXHAUSTIVE, top_k=2)
        >>> len(pruned)  # 2 (all edges)
    """
    if strategy == FanoutStrategy.EXHAUSTIVE:
        return edges

    if len(edges) <= top_k:
        # Already small enough
        return edges

    # Sort by log_weight (quick heuristic, not full cost)
    # Higher weight = stronger attractor = lower cost
    sorted_edges = sorted(edges, key=lambda e: e.log_weight, reverse=True)

    # Take top_k
    return sorted_edges[:top_k]


def compute_top_k_split(
    edges_with_costs: List[Tuple['Link', float]],
    k: int,
    temperature: float = 1.0
) -> List[Tuple['Link', float]]:
    """
    Compute top-K energy split using softmax over costs.

    Optional feature (spec §2.3) for distributing energy across K best edges
    instead of sending all to single best edge.

    Algorithm:
    π_k = softmax(-c_k / T)
    Returns (link, π_k) pairs where sum(π_k) = 1.0

    Args:
        edges_with_costs: List of (link, cost) tuples
        k: Number of edges to split across
        temperature: Softmax temperature (higher = more uniform)

    Returns:
        List of (link, energy_fraction) tuples

    Example:
        >>> edges_costs = [(link1, 0.5), (link2, 1.0), (link3, 1.5)]
        >>> split = compute_top_k_split(edges_costs, k=2, temperature=1.0)
        >>> # Returns [(link1, 0.73), (link2, 0.27)] - fractions sum to 1.0
    """
    if k <= 0:
        return []

    # Sort by cost (ascending)
    sorted_items = sorted(edges_with_costs, key=lambda x: x[1])

    # Take top-k (lowest cost)
    top_k_items = sorted_items[:k]

    if len(top_k_items) == 0:
        return []

    # Softmax over -cost/T
    # (negative because lower cost = better, higher probability)
    logits = [-cost / temperature for _, cost in top_k_items]

    # Compute softmax
    max_logit = max(logits)
    exp_logits = [math.exp(l - max_logit) for l in logits]  # Numerical stability
    sum_exp = sum(exp_logits)

    if sum_exp == 0:
        # Fallback: uniform distribution
        uniform_prob = 1.0 / len(top_k_items)
        return [(link, uniform_prob) for link, _ in top_k_items]

    probs = [e / sum_exp for e in exp_logits]

    return [(link, prob) for (link, _), prob in zip(top_k_items, probs)]


def get_prune_rate(
    original_count: int,
    pruned_count: int
) -> float:
    """
    Compute prune rate for observability.

    Args:
        original_count: Number of edges before pruning
        pruned_count: Number of edges after pruning

    Returns:
        Prune rate (0-1, where 1 = 100% pruned)

    Example:
        >>> rate = get_prune_rate(100, 5)
        >>> # 0.95 (95% pruned)
    """
    if original_count == 0:
        return 0.0

    return (original_count - pruned_count) / original_count


def get_diagnostics(
    outdegree: int,
    strategy: FanoutStrategy,
    top_k: int,
    wm_headroom: Optional[float] = None,
    prune_rate: Optional[float] = None
) -> dict:
    """
    Get fanout diagnostics for observability.

    Returns:
        Dictionary with diagnostic fields

    Example:
        >>> diag = get_diagnostics(
        ...     outdegree=50,
        ...     strategy=FanoutStrategy.SELECTIVE,
        ...     top_k=5,
        ...     prune_rate=0.9
        ... )
        >>> print(diag)
        {
            'outdegree': 50,
            'strategy': 'selective',
            'top_k': 5,
            'wm_headroom': None,
            'prune_rate': 0.9
        }
    """
    return {
        'outdegree': outdegree,
        'strategy': strategy.value,
        'top_k': top_k,
        'wm_headroom': wm_headroom,
        'prune_rate': prune_rate
    }
