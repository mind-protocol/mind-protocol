# tests/economy/test_progressive_pricing.py
#
# Tests for trust-based progressive pricing formula.

from __future__ import annotations

import math
import sys
import os

import pytest

# Ensure the repo root is on the path so we can import economy.metabolic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from economy.metabolic.progressive_pricing import (
    DISCOUNT_RATE,
    MIN_PRICE_RATIO,
    compute_progressive_price,
)


class TestProgressivePricing:
    """Tests for: price = c_base * max(MIN_PRICE_RATIO, e^(-3 * trust_score))"""

    # --- Trust level price points ---

    def test_trust_zero_pays_full_price(self):
        """trust=0 -> discount = e^0 = 1.0 -> pays 100%."""
        price = compute_progressive_price(100.0, 0.0)
        assert price == 100.0

    def test_trust_half_pays_about_22_percent(self):
        """trust=0.5 -> discount = e^(-1.5) ~ 0.2231."""
        price = compute_progressive_price(100.0, 0.5)
        expected = 100.0 * math.exp(-1.5)  # ~22.31
        assert abs(price - expected) < 0.01

    def test_trust_0_9_pays_about_7_percent(self):
        """trust=0.9 -> discount = e^(-2.7) ~ 0.0672."""
        price = compute_progressive_price(100.0, 0.9)
        expected = 100.0 * math.exp(-2.7)  # ~6.72
        assert abs(price - expected) < 0.01

    def test_trust_1_0_pays_floor(self):
        """trust=1.0 -> discount = e^(-3) ~ 0.0498, floored to 0.05."""
        price = compute_progressive_price(100.0, 1.0)
        expected = 100.0 * MIN_PRICE_RATIO  # 5.0
        assert abs(price - expected) < 0.01

    # --- Input validation ---

    def test_c_base_zero_raises(self):
        """c_base=0 raises ValueError."""
        with pytest.raises(ValueError, match="c_base"):
            compute_progressive_price(0.0, 0.5)

    def test_c_base_negative_raises(self):
        """Negative c_base raises ValueError."""
        with pytest.raises(ValueError, match="c_base"):
            compute_progressive_price(-10.0, 0.5)

    def test_negative_trust_raises(self):
        """Negative trust_score raises ValueError."""
        with pytest.raises(ValueError, match="trust_score"):
            compute_progressive_price(100.0, -0.1)

    def test_trust_greater_than_one_raises(self):
        """trust_score > 1 raises ValueError."""
        with pytest.raises(ValueError, match="trust_score"):
            compute_progressive_price(100.0, 1.1)

    # --- Price is always positive ---

    def test_price_always_positive(self):
        """Price is always > 0 for valid inputs."""
        for trust in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0]:
            price = compute_progressive_price(100.0, trust)
            assert price > 0, f"Price not positive at trust={trust}"

    # --- Monotonically decreasing ---

    def test_monotonically_decreasing(self):
        """Higher trust -> lower price (monotonically decreasing)."""
        trust_values = [i / 100.0 for i in range(101)]  # 0.00 to 1.00
        prices = [compute_progressive_price(100.0, t) for t in trust_values]
        for i in range(1, len(prices)):
            assert prices[i] <= prices[i - 1], (
                f"Price increased from trust={trust_values[i-1]} to "
                f"trust={trust_values[i]}: {prices[i-1]} -> {prices[i]}"
            )

    # --- Constants sanity ---

    def test_discount_rate_is_3(self):
        """DISCOUNT_RATE should be 3.0."""
        assert DISCOUNT_RATE == 3.0

    def test_min_price_ratio_is_5_percent(self):
        """MIN_PRICE_RATIO should be 0.05."""
        assert MIN_PRICE_RATIO == 0.05
