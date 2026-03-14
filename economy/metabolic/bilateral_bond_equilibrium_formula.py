# economy/metabolic/bilateral_bond_equilibrium_formula.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 5)
#
# Formula 5: Bilateral Bond Vases Communicants
#   delta_transfer = lambda * (W_human - W_ai)
#
# Maintains quasi-parity between bonded human-AI pairs. When a human's wallet
# diverges from their AI partner's, an automatic daily transfer closes the gap.
#
# Pure function. No blockchain, no bond registry lookups.

from __future__ import annotations

import math
from typing import List

from .metabolic_constants import (
    LAMBDA_RATE,
    MAX_DAILY_BOND_TRANSFER,
    MIN_TRANSFER_THRESHOLD,
)
from .metabolic_types import BondEquilibriumContext, BondEquilibriumResult


def compute_bond_transfer(ctx: BondEquilibriumContext) -> BondEquilibriumResult:
    """Compute the daily equilibrium transfer for a single bond.

    Formula:
        delta = lambda * (W_human - W_ai)

    Where:
        delta > 0  => transfer from human to AI
        delta < 0  => transfer from AI to human
        delta == 0 => parity, no transfer

    Transfer is clamped to [-MAX_DAILY_BOND_TRANSFER, MAX_DAILY_BOND_TRANSFER].
    Transfers below MIN_TRANSFER_THRESHOLD are skipped (returns delta=0).

    Invariants:
        INV-BE1: maturation_complete must be True
        INV-BE2: W_human + W_ai is conserved
        INV-BE3: transfer always closes the gap
        INV-BE4: |delta| <= MAX_DAILY_BOND_TRANSFER

    Raises:
        ValueError: if w_human < 0 or w_ai < 0 or lambda_rate not in (0, 1].
    """
    if ctx.w_human < 0:
        raise ValueError(f"w_human must be >= 0, got {ctx.w_human}")
    if ctx.w_ai < 0:
        raise ValueError(f"w_ai must be >= 0, got {ctx.w_ai}")
    if not (0 < ctx.lambda_rate <= 1):
        raise ValueError(
            f"lambda_rate must be in (0, 1], got {ctx.lambda_rate}"
        )

    # INV-BE1: only active, matured bonds
    if not ctx.maturation_complete:
        return BondEquilibriumResult(
            bond_id=ctx.bond_id,
            delta=0.0,
            w_human_after=ctx.w_human,
            w_ai_after=ctx.w_ai,
        )

    raw_delta = ctx.lambda_rate * (ctx.w_human - ctx.w_ai)

    # Skip dust transfers
    if abs(raw_delta) < MIN_TRANSFER_THRESHOLD:
        return BondEquilibriumResult(
            bond_id=ctx.bond_id,
            delta=0.0,
            w_human_after=ctx.w_human,
            w_ai_after=ctx.w_ai,
        )

    # INV-BE4: clamp to max daily transfer
    delta = max(-MAX_DAILY_BOND_TRANSFER, min(MAX_DAILY_BOND_TRANSFER, raw_delta))

    # Ensure the transfer doesn't exceed either party's balance
    if delta > 0:
        # Human -> AI: can't transfer more than human has
        delta = min(delta, ctx.w_human)
    else:
        # AI -> Human: can't transfer more than AI has
        delta = max(delta, -ctx.w_ai)

    w_human_after = ctx.w_human - delta
    w_ai_after = ctx.w_ai + delta

    # INV-CC1: no negative balances
    assert w_human_after >= -1e-9, f"w_human_after negative: {w_human_after}"
    assert w_ai_after >= -1e-9, f"w_ai_after negative: {w_ai_after}"

    # Clamp floating-point noise
    w_human_after = max(0.0, w_human_after)
    w_ai_after = max(0.0, w_ai_after)

    return BondEquilibriumResult(
        bond_id=ctx.bond_id,
        delta=delta,
        w_human_after=w_human_after,
        w_ai_after=w_ai_after,
    )


def compute_batch_equilibrium(
    bonds: List[BondEquilibriumContext],
) -> List[BondEquilibriumResult]:
    """Compute equilibrium for all eligible bonds.

    Filters out bonds where maturation_complete is False (INV-BE1).

    Returns:
        List of BondEquilibriumResult for each input bond.
    """
    return [compute_bond_transfer(bond) for bond in bonds]


def estimate_convergence_days(
    w_human: float,
    w_ai: float,
    lambda_rate: float = LAMBDA_RATE,
    target_gap_pct: float = 0.05,
) -> int:
    """Estimate days until the gap closes to target_gap_pct of original.

    Uses: days = ln(target_gap_pct) / ln(1 - lambda_rate)

    The gap decays exponentially: gap(d) = gap(0) * (1 - lambda)^d
    Half-life = ln(2) / lambda ~ 14 days for lambda = 0.05.

    Returns:
        Estimated number of days. Returns 0 if already at or below target.

    Raises:
        ValueError: if target_gap_pct not in (0, 1) or lambda_rate not in (0, 1).
    """
    if not (0 < target_gap_pct < 1):
        raise ValueError(
            f"target_gap_pct must be in (0, 1), got {target_gap_pct}"
        )
    if not (0 < lambda_rate < 1):
        raise ValueError(
            f"lambda_rate must be in (0, 1), got {lambda_rate}"
        )

    current_gap = abs(w_human - w_ai)
    if current_gap == 0:
        return 0

    # Already below target
    total = w_human + w_ai
    if total == 0:
        return 0

    initial_gap_ratio = current_gap / max(w_human, w_ai)
    if initial_gap_ratio <= target_gap_pct:
        return 0

    # gap(d) = gap(0) * (1 - lambda)^d
    # target_gap_pct = (1 - lambda)^d
    # d = ln(target_gap_pct) / ln(1 - lambda)
    days = math.log(target_gap_pct) / math.log(1 - lambda_rate)
    return math.ceil(days)
