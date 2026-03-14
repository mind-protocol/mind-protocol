# economy/metabolic/ubc_proximity_redistribution_formula.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 6)
#
# Formula 6: UBC Proximity Redistribution (v2 — activity-based)
#
#   activity   = log10(1 + Σ(weight of moments actor created in Space))
#   community  = num_actors_in_space - 1
#   weight     = activity × community
#   share      = weight / total_weight
#   amount     = pool × share
#
# Distributes the UBC pool to actors based on REAL ACTIVITY in shared
# Spaces, not passive presence. Actors are paid for animating spaces,
# not for leaving tabs open.
#
# Anti-spam: log10 envelope prevents linear farming. 1000 zero-weight
# spam moments contribute log10(1 + ~0) ≈ 0. Only consolidated moments
# (with weight from Law 6) count.
#
# Anti-farming: hours_present is GONE. Only moment weights matter.
# No moments = no redistribution, regardless of connection time.
#
# Pure function. No graph queries, no blockchain.

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .metabolic_constants import MIN_COPRESENCE_ACTORS, EPSILON
from .metabolic_types import SpacePresence, UBCShare


def compute_actor_weights(
    spaces: List[SpacePresence],
    min_actors: int = MIN_COPRESENCE_ACTORS,
) -> Dict[str, float]:
    """Compute per-actor redistribution weights from Space activity data.

    For each Space with >= min_actors actors:
        activity = log10(1 + sum_of_moment_weights)
        community_bonus = num_actors_in_space - 1
        weight += activity × community_bonus

    The log10 envelope:
    - Prevents linear spam farming (1000 spam moments ≈ 0 weight)
    - Provides diminishing returns (first quality moments matter most)
    - log10(1 + 0) = 0: zero activity = zero weight
    - log10(1 + 1) ≈ 0.30: moderate activity
    - log10(1 + 10) ≈ 1.04: high activity
    - log10(1 + 100) ≈ 2.00: very high (but only 2x the moderate case)

    The community_bonus (num_actors - 1) privileges larger spaces:
    a Space with 100 actors gets 99x multiplier vs 2x for a pair.

    Invariant INV-UBC2: solo actors never receive redistribution.
    Invariant INV-UBC3: weight > 0 requires moment_weight_sum > 0
                        and community_bonus >= 1.

    Raises:
        ValueError: if any moment_weight_sum is negative.
    """
    actor_weights: Dict[str, float] = {}

    for space in spaces:
        num_actors = len(space.actors)
        if num_actors < min_actors:
            continue  # Skip solo and empty spaces

        community_bonus = num_actors - 1

        for actor_id, moment_weight_sum in space.actors.items():
            if moment_weight_sum < 0:
                raise ValueError(
                    f"moment_weight_sum must be >= 0, got {moment_weight_sum} "
                    f"for actor {actor_id} in space {space.space_id}"
                )
            if moment_weight_sum == 0:
                continue  # No real activity, no weight

            # Log envelope: diminishing returns, anti-spam
            activity = math.log10(1.0 + moment_weight_sum)
            weight = activity * community_bonus
            actor_weights[actor_id] = actor_weights.get(actor_id, 0.0) + weight

    return actor_weights


def compute_redistribution_shares(
    actor_weights: Dict[str, float],
) -> List[UBCShare]:
    """Normalize weights to shares summing to 1.0.

    Returns list of UBCShare with amount=0 (pool size applied later).

    Invariant INV-UBC1: sum(shares) == 1.0 (within EPSILON).

    Returns empty list if total_weight is zero.
    """
    total_weight = sum(actor_weights.values())
    if total_weight <= 0:
        return []

    shares: List[UBCShare] = []
    for actor_id, weight in actor_weights.items():
        share = weight / total_weight
        shares.append(UBCShare(actor_id=actor_id, share=share, amount=0.0))

    return shares


def compute_redistribution(
    pool_balance: float,
    spaces: List[SpacePresence],
    min_actors: int = MIN_COPRESENCE_ACTORS,
) -> Tuple[List[UBCShare], float]:
    """Full redistribution: weights -> shares -> amounts.

    Invariants:
        INV-SC3: total_distributed == pool_balance (when redistribution occurs)
        INV-UBC1: sum(shares) == 1.0

    If no shared activity exists, returns ([], 0.0) -- pool carries forward.

    Raises:
        ValueError: if pool_balance < 0.
    """
    if pool_balance < 0:
        raise ValueError(f"pool_balance must be >= 0, got {pool_balance}")
    if pool_balance == 0:
        return [], 0.0

    actor_weights = compute_actor_weights(spaces, min_actors)
    if not actor_weights:
        # No activity in shared spaces today -- pool carries forward
        return [], 0.0

    total_weight = sum(actor_weights.values())
    if total_weight <= 0:
        return [], 0.0

    shares: List[UBCShare] = []
    total_distributed = 0.0

    for actor_id, weight in actor_weights.items():
        share = weight / total_weight
        amount = pool_balance * share
        shares.append(UBCShare(actor_id=actor_id, share=share, amount=amount))
        total_distributed += amount

    # Correct rounding error: assign remainder to first share
    rounding_error = pool_balance - total_distributed
    if shares and abs(rounding_error) > 0:
        first = shares[0]
        shares[0] = UBCShare(
            actor_id=first.actor_id,
            share=first.share,
            amount=first.amount + rounding_error,
        )
        total_distributed = pool_balance

    return shares, total_distributed
