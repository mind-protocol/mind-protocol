# economy/metabolic/progressive_demurrage_formula.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 2)
#
# Formula 2: Progressive Demurrage (Daily Tax)
#   T_i = W_total * tau_base * log10(1 + W_total)
#
# Taxes idle wealth progressively. Larger holdings face proportionally
# higher daily tax via logarithmic scaling. All collected tax flows to the
# UBC redistribution pool.
#
# Pure function. No blockchain, no graph, no I/O.

from __future__ import annotations

import math
from typing import List, Tuple

from .metabolic_constants import TAU_BASE, DUST_THRESHOLD
from .metabolic_types import DemurrageContext, DemurrageResult


def compute_effective_rate(w_total: float, tau_base: float = TAU_BASE) -> float:
    """Compute the effective daily demurrage rate.

    Formula:
        effective_rate = tau_base * log10(1 + W_total)

    The rate grows logarithmically -- a 10x increase in balance roughly
    adds tau_base to the rate. This is progressive but not confiscatory.

    Returns 0.0 for w_total <= 0.

    Raises:
        ValueError: if tau_base < 0.
    """
    if tau_base < 0:
        raise ValueError(f"tau_base must be >= 0, got {tau_base}")
    if w_total <= 0:
        return 0.0
    return tau_base * math.log10(1.0 + w_total)


def compute_daily_demurrage(ctx: DemurrageContext) -> DemurrageResult:
    """Compute daily demurrage tax for a single actor.

    Formula:
        T_i = W_total * tau_base * log10(1 + W_total)

    Special cases:
        - Dust accounts (W_total <= DUST_THRESHOLD): tax = 0
        - Tax clamped to on-chain balance (wallet never goes negative)

    Invariants verified:
        - INV-D1: tax_amount <= w_onchain (wallet balance after >= 0)
        - INV-D2: effective rate increases with w_total (progressive)
        - INV-CC1: no negative balances

    Raises:
        ValueError: if w_total < 0 or tau_base < 0.
    """
    if ctx.w_total < 0:
        raise ValueError(f"w_total must be >= 0, got {ctx.w_total}")
    if ctx.w_onchain < 0:
        raise ValueError(f"w_onchain must be >= 0, got {ctx.w_onchain}")
    if ctx.tau_base < 0:
        raise ValueError(f"tau_base must be >= 0, got {ctx.tau_base}")

    # Skip dust accounts
    if ctx.w_total <= DUST_THRESHOLD:
        return DemurrageResult(
            actor_id=ctx.actor_id,
            w_total=ctx.w_total,
            w_offregistry=ctx.w_offregistry,
            tax_amount=0.0,
            effective_rate=0.0,
        )

    effective_rate = compute_effective_rate(ctx.w_total, ctx.tau_base)
    raw_tax = ctx.w_total * effective_rate

    # INV-D1: clamp to on-chain balance -- wallet can never go negative
    tax_amount = min(raw_tax, ctx.w_onchain)

    # Effective rate as actually applied
    actual_rate = tax_amount / ctx.w_total if ctx.w_total > 0 else 0.0

    return DemurrageResult(
        actor_id=ctx.actor_id,
        w_total=ctx.w_total,
        w_offregistry=ctx.w_offregistry,
        tax_amount=tax_amount,
        effective_rate=actual_rate,
    )


def apply_demurrage_batch(
    contexts: List[DemurrageContext],
) -> Tuple[List[DemurrageResult], float]:
    """Apply demurrage to a batch of actors.

    Returns:
        (results, total_tax_collected)

    Invariant INV-SC2: total_tax_collected == sum of all individual tax_amounts.
    """
    results: List[DemurrageResult] = []
    total_tax = 0.0

    for ctx in contexts:
        result = compute_daily_demurrage(ctx)
        results.append(result)
        total_tax += result.tax_amount

    return results, total_tax
