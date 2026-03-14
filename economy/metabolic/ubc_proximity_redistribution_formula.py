# economy/metabolic/ubc_proximity_redistribution_formula.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 6)
#
# Formula 6: UBC Proximity Redistribution
#   weight_actor += hours_present * (num_co_actors - 1)
#   share_actor = weight_actor / total_weight
#   amount_actor = pool * share_actor
#
# Distributes the daily demurrage tax pool to actors based on their
# co-presence in Spaces, weighted by topology. Actors in shared Spaces
# with more co-present participants receive proportionally more.
#
# Pure function. No graph queries, no blockchain.

from __future__ import annotations

from typing import Dict, List, Tuple

from .metabolic_constants import MIN_COPRESENCE_ACTORS, EPSILON
from .metabolic_types import SpacePresence, UBCShare


def compute_actor_weights(
    spaces: List[SpacePresence],
    min_actors: int = MIN_COPRESENCE_ACTORS,
) -> Dict[str, float]:
    """Compute per-actor redistribution weights from Space presence data.

    For each Space with >= min_actors actors:
        weight_actor += hours_present * (num_actors_in_space - 1)

    The sharing_bonus (num_actors - 1) rewards spaces with more collaboration.
    Solo spaces (< min_actors) produce zero weight.

    Invariant INV-UBC2: solo actors never receive redistribution.
    Invariant INV-UBC3: weight > 0 requires hours > 0 and sharing_bonus >= 1.

    Raises:
        ValueError: if any hours_present is negative.
    """
    actor_weights: Dict[str, float] = {}

    for space in spaces:
        num_actors = len(space.actors)
        if num_actors < min_actors:
            continue  # Skip solo and empty spaces

        sharing_bonus = num_actors - 1

        for actor_id, hours in space.actors.items():
            if hours < 0:
                raise ValueError(
                    f"hours_present must be >= 0, got {hours} for "
                    f"actor {actor_id} in space {space.space_id}"
                )
            if hours == 0:
                continue  # No presence, no weight

            weight = hours * sharing_bonus
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

    If no shared presence exists, returns ([], 0.0) -- pool carries forward.

    Raises:
        ValueError: if pool_balance < 0.
    """
    if pool_balance < 0:
        raise ValueError(f"pool_balance must be >= 0, got {pool_balance}")
    if pool_balance == 0:
        return [], 0.0

    actor_weights = compute_actor_weights(spaces, min_actors)
    if not actor_weights:
        # No shared presence today -- pool carries forward
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
