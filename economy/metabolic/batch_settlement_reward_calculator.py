# economy/metabolic/batch_settlement_reward_calculator.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 4)
#
# Formula 4: Batch Settlement (Limbic Delta to $MIND)
#   reward = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate
#
# Converts graph-measured value creation into economic reward.
# Pure computation -- does not touch Solana. The settlement submitter
# (in mind-mcp) handles on-chain submission.

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .metabolic_constants import (
    MAX_ACTION_REWARD,
    MAX_EPOCH_REWARD,
    MAX_SUPPLY_REDUCTION,
    SETTLEMENT_RATE,
)
from .metabolic_types import SettlementAction, SettlementBatch


def compute_action_reward(
    action: SettlementAction,
    settlement_rate: float = SETTLEMENT_RATE,
) -> float:
    """Compute reward for a single action.

    Formula:
        reward = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate

    Returns 0 if any factor is <= 0 (INV-S1).
    Caps at MAX_ACTION_REWARD (INV-S2).

    Raises:
        ValueError: if settlement_rate < 0.
    """
    if settlement_rate < 0:
        raise ValueError(f"settlement_rate must be >= 0, got {settlement_rate}")

    # INV-S1: all factors must be positive for a reward
    if action.limbic_delta <= 0:
        return 0.0
    if action.trust_y_to_x <= 0:
        return 0.0
    if action.weight_thing <= 0:
        return 0.0

    raw_reward = (
        action.limbic_delta
        * action.trust_y_to_x
        * action.weight_thing
        * settlement_rate
    )

    # INV-S2: cap per-action reward
    return min(raw_reward, MAX_ACTION_REWARD)


def compute_epoch_rewards(
    actions: List[SettlementAction],
    settlement_rate: float = SETTLEMENT_RATE,
) -> Dict[str, float]:
    """Aggregate rewards per actor for an epoch.

    Caps per-actor total at MAX_EPOCH_REWARD (INV-S2).

    Returns:
        {actor_id: total_reward}
    """
    rewards: Dict[str, float] = {}

    for action in actions:
        reward = compute_action_reward(action, settlement_rate)
        if reward > 0:
            rewards[action.actor_x] = rewards.get(action.actor_x, 0.0) + reward

    # INV-S2: cap per-actor per-epoch reward
    for actor_id in rewards:
        rewards[actor_id] = min(rewards[actor_id], MAX_EPOCH_REWARD)

    return rewards


def apply_supply_adjustment(
    rewards: Dict[str, float],
    supply_delta_percentage: float,
    supply_action: str,
) -> Tuple[Dict[str, float], float]:
    """Reduce rewards when supply exceeds target.

    When supply_action is "ALLOW_BURN", settlement rewards are reduced
    proportionally to how far supply exceeds the target.

    INV-S3: reduction never exceeds MAX_SUPPLY_REDUCTION (50%).

    Args:
        rewards: actor_id -> reward mapping.
        supply_delta_percentage: how far supply deviates from target (%).
        supply_action: action from supply health check ("ALLOW_BURN", etc.).

    Returns:
        (adjusted_rewards, reduction_factor)
        reduction_factor is 0.0 when no reduction applied.
    """
    if supply_action != "ALLOW_BURN":
        return dict(rewards), 0.0

    # Reduction proportional to deviation, capped at MAX_SUPPLY_REDUCTION
    reduction = min(MAX_SUPPLY_REDUCTION, supply_delta_percentage / 100.0)
    reduction = max(0.0, reduction)  # Never negative

    multiplier = 1.0 - reduction
    adjusted = {actor: reward * multiplier for actor, reward in rewards.items()}

    return adjusted, reduction


def assemble_settlement_batch(
    batch_id: str,
    epoch_start: datetime,
    epoch_end: datetime,
    actions: List[SettlementAction],
    settlement_rate: float = SETTLEMENT_RATE,
    supply_delta_percentage: float = 0.0,
    supply_action: str = "NORMAL",
) -> SettlementBatch:
    """Full batch assembly: compute rewards, apply supply adjustment, package.

    Returns a SettlementBatch ready for Solana submission (status=PENDING).
    """
    raw_rewards = compute_epoch_rewards(actions, settlement_rate)
    adjusted_rewards, reduction = apply_supply_adjustment(
        raw_rewards, supply_delta_percentage, supply_action
    )

    total_minted = sum(adjusted_rewards.values())

    return SettlementBatch(
        batch_id=batch_id,
        epoch_start=epoch_start,
        epoch_end=epoch_end,
        actions=list(actions),
        rewards=adjusted_rewards,
        total_minted=total_minted,
        supply_reduction=reduction,
        status="PENDING",
        solana_tx_signature=None,
    )
