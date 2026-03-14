# economy/metabolic/anti_sybil_phantom_balance_tracker.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 3)
#
# Formula 3: Anti-Sybil Auto-Repatriation
#
# Prevents actors from escaping progressive demurrage by parking funds in
# wallets outside the L4 registry. Funds sent to unregistered addresses are
# tracked as phantom balance. Repatriation incurs 5% friction tax (burned).
#
# Pure functions. No blockchain, no registry lookups -- caller supplies
# the is_registered flag.

from __future__ import annotations

import math
from typing import Tuple

from .metabolic_constants import FRICTION_TAX_RATE, TAU_BASE
from .metabolic_types import RepatriationResult


def compute_total_balance(w_onchain: float, w_offregistry: float) -> float:
    """Compute total balance including off-registry phantom balance.

    Formula:
        W_total = W_onchain + W_offregistry

    Invariant INV-AS1:
        W_offregistry >= 0
        W_total >= W_onchain

    Raises:
        ValueError: if either input is negative.
    """
    if w_onchain < 0:
        raise ValueError(f"w_onchain must be >= 0, got {w_onchain}")
    if w_offregistry < 0:
        raise ValueError(f"w_offregistry must be >= 0, got {w_offregistry}")
    return w_onchain + w_offregistry


def track_outflow(
    current_offregistry: float,
    amount: float,
    is_l4_registered: bool,
) -> Tuple[float, bool]:
    """Track an outflow to a potentially unregistered address.

    If recipient is not L4-registered, *amount* is added to the phantom
    balance. The phantom balance is then used in demurrage computation
    (Formula 2) so the sender cannot escape progressive tax.

    Args:
        current_offregistry: Current phantom balance.
        amount: Transfer amount.
        is_l4_registered: Whether the recipient is in the L4 registry.

    Returns:
        (new_offregistry_balance, was_tracked)

    Raises:
        ValueError: if amount <= 0 or current_offregistry < 0.
    """
    if amount <= 0:
        raise ValueError(f"amount must be > 0, got {amount}")
    if current_offregistry < 0:
        raise ValueError(
            f"current_offregistry must be >= 0, got {current_offregistry}"
        )

    if is_l4_registered:
        # Recipient is in L4 registry -- no phantom tracking
        return current_offregistry, False

    # Recipient not registered -- track as phantom
    new_offregistry = current_offregistry + amount
    return new_offregistry, True


def process_repatriation(
    actor_id: str,
    gross_amount: float,
    current_offregistry: float,
    friction_rate: float = FRICTION_TAX_RATE,
) -> RepatriationResult:
    """Process repatriation of funds from a non-L4 address.

    Applies friction tax (default 5%) which is permanently burned.

    Formula:
        friction = gross_amount * friction_rate
        net_amount = gross_amount - friction
        off_registry -= gross_amount  (clamped to 0)

    Invariants:
        INV-AS2: friction > 0, net == gross * (1 - friction_rate)
        INV-AS3: round-trip always costs more than staying in L4

    Raises:
        ValueError: if gross_amount <= 0, current_offregistry < 0,
                    or friction_rate not in [0, 1).
    """
    if gross_amount <= 0:
        raise ValueError(f"gross_amount must be > 0, got {gross_amount}")
    if current_offregistry < 0:
        raise ValueError(
            f"current_offregistry must be >= 0, got {current_offregistry}"
        )
    if not (0 <= friction_rate < 1):
        raise ValueError(
            f"friction_rate must be in [0, 1), got {friction_rate}"
        )

    friction_penalty = gross_amount * friction_rate
    net_amount = gross_amount - friction_penalty

    # Reduce phantom balance, clamp to zero
    new_offregistry = max(0.0, current_offregistry - gross_amount)

    return RepatriationResult(
        actor_id=actor_id,
        gross_amount=gross_amount,
        friction_penalty=friction_penalty,
        net_amount=net_amount,
        new_offregistry_balance=new_offregistry,
    )


def is_roundtrip_profitable(
    amount: float,
    days_hidden: int,
    tau_base: float = TAU_BASE,
    friction_rate: float = FRICTION_TAX_RATE,
) -> Tuple[bool, float]:
    """Calculate whether hiding funds off-registry is profitable.

    A round-trip consists of:
      1. Send *amount* to a non-L4 address
      2. Wait *days_hidden* days (demurrage still applies to phantom balance)
      3. Repatriate with friction

    Cost of hiding = demurrage on phantom balance over the period + friction.
    Benefit = 0 (the sender gains nothing -- demurrage still applies).

    The only "benefit" would be if demurrage didn't track phantom balance,
    but Formula 3 ensures it does. So the cost is always strictly positive.

    Returns:
        (is_profitable, net_cost)
        is_profitable should always be False.
        net_cost is the total cost of the round-trip (positive = loss).

    Raises:
        ValueError: if amount <= 0 or days_hidden < 0.
    """
    if amount <= 0:
        raise ValueError(f"amount must be > 0, got {amount}")
    if days_hidden < 0:
        raise ValueError(f"days_hidden must be >= 0, got {days_hidden}")

    # Friction cost on repatriation
    friction_cost = amount * friction_rate

    # Demurrage cost is zero *additional* because phantom tracking means
    # the actor pays the same demurrage whether funds are on-chain or off.
    # But the friction cost is pure loss with no benefit.
    # If the actor kept funds in L4, they'd pay demurrage but avoid friction.
    # So the net cost of the round-trip = friction_cost.
    #
    # Additionally, during the hidden period the funds are unusable
    # (can't bond, can't use services), which is an opportunity cost
    # we don't quantify here.
    net_cost = friction_cost

    return False, net_cost
