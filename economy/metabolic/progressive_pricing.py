# economy/metabolic/progressive_pricing.py
#
# Trust-Based Progressive Pricing
#
# Formula: price = C_base * max(MIN_PRICE_RATIO, e^(-DISCOUNT_RATE * trust_score))
#
# The price of a service depends ONLY on the requester's trust_score.
# Trust score already encodes duration, history, and reputation.
#
# Pure function. No blockchain, no graph, no I/O.

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DISCOUNT_RATE: float = 3.0
"""Exponential discount steepness. Higher = steeper trust discount."""

MIN_PRICE_RATIO: float = 0.05
"""Floor ratio (5%). Price never drops below 5% of C_base."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_progressive_price(c_base: float, trust_score: float) -> float:
    """Compute the trust-discounted price for a service request.

    Formula:
        discount = e^(-DISCOUNT_RATE * trust_score)
        price = c_base * max(MIN_PRICE_RATIO, discount)

    Args:
        c_base: Raw compute cost of the service ($MIND). Must be > 0.
        trust_score: Requester's trust score. Must be in [0, 1].

    Returns:
        The discounted price ($MIND). Always > 0.

    Raises:
        ValueError: If c_base <= 0 or trust_score outside [0, 1].
    """
    if c_base <= 0:
        raise ValueError(f"c_base must be > 0, got {c_base}")
    if trust_score < 0 or trust_score > 1:
        raise ValueError(
            f"trust_score must be in [0, 1], got {trust_score}"
        )

    discount = math.exp(-DISCOUNT_RATE * trust_score)
    price = c_base * max(MIN_PRICE_RATIO, discount)

    return price
