# economy/metabolic/progressive_pricing_formula.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 1)
#
# Formula 1: Progressive Pricing (Degressive)
#   P(i, S) = C_base * e^(-k * U_S) * max(0.1, W_i / W_median)
#
# Prices decrease with service utility (rewarding useful services) and scale
# with requester wealth relative to network median (progressive affordability).
#
# Pure function. No blockchain, no graph, no I/O.

from __future__ import annotations

import math

from .metabolic_constants import UTILITY_DISCOUNT_RATE, WEALTH_RATIO_FLOOR
from .metabolic_types import PricingContext


def compute_utility_discount(u_s: float, k: float = UTILITY_DISCOUNT_RATE) -> float:
    """Compute the exponential utility discount factor.

    Formula:
        utility_discount = e^(-k * U_S)

    Returns a value in (0, 1].
    - U_S = 0 (new service) -> 1.0 (no discount)
    - U_S -> inf            -> approaches 0 (maximum discount)

    Raises:
        ValueError: if u_s < 0 or k < 0.
    """
    if u_s < 0:
        raise ValueError(f"u_s must be >= 0, got {u_s}")
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    return math.exp(-k * u_s)


def compute_wealth_ratio(
    w_i: float,
    w_median: float,
    floor: float = WEALTH_RATIO_FLOOR,
) -> float:
    """Compute the wealth ratio with a minimum floor.

    Formula:
        wealth_ratio = max(floor, W_i / W_median)

    Returns a value >= floor (default 0.1).

    Raises:
        ValueError: if w_median <= 0 or floor < 0.
    """
    if w_median <= 0:
        raise ValueError(f"w_median must be > 0, got {w_median}")
    if floor < 0:
        raise ValueError(f"floor must be >= 0, got {floor}")
    if w_i < 0:
        raise ValueError(f"w_i must be >= 0, got {w_i}")
    return max(floor, w_i / w_median)


def compute_progressive_price(ctx: PricingContext) -> float:
    """Compute the effective price for a service request.

    Formula:
        P(i, S) = C_base * e^(-k * U_S) * max(WEALTH_RATIO_FLOOR, W_i / W_median)

    Invariants verified:
        - INV-P1: result >= 0; result > 0 when C_base > 0
        - INV-P2: 0 < utility_discount <= 1.0
        - INV-P3: wealth_ratio >= WEALTH_RATIO_FLOOR

    Raises:
        ValueError: if any input is out of valid range.
    """
    if ctx.c_base < 0:
        raise ValueError(f"c_base must be >= 0, got {ctx.c_base}")

    utility_discount = compute_utility_discount(ctx.u_s, ctx.k)
    wealth_ratio = compute_wealth_ratio(ctx.w_i, ctx.w_median)

    price = ctx.c_base * utility_discount * wealth_ratio

    # INV-P1: non-negativity (guaranteed by construction, but explicit)
    assert price >= 0, f"Price must be >= 0, got {price}"

    return price
