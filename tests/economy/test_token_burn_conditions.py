# tests/economy/test_token_burn_conditions.py
#
# Tests for $MIND token burn conditions (B1-B5)
# DOCS: docs/economy/token/VALIDATION_Token.md

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from economy.token.token_burn_condition_executor import (
    BurnCondition,
    BurnResult,
    BurnConditionExecutor,
    BURN_CONDITIONS,
)


@pytest.fixture
def burn_executor():
    """Create a burn executor in dry run mode."""
    return BurnConditionExecutor(
        mint_address="test_mint_address",
        dry_run=True,
    )


class TestBurnConditionB1MembraneFee:
    """Tests for B1: Membrane Fee burn (1-5%)."""

    def test_membrane_fee_same_layer(self, burn_executor):
        """Same layer transfers should have no fee."""
        fee = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=2,
            dest_layer=2,
            trust_score=0,
        )
        assert fee == 0.0

    def test_membrane_fee_one_layer(self, burn_executor):
        """One layer gap should be ~1%."""
        fee = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=1,
            dest_layer=2,
            trust_score=0,
        )
        # 1% of 1000 = 10
        assert fee == 10.0

    def test_membrane_fee_trust_discount(self, burn_executor):
        """Higher trust should reduce fee (but not below minimum)."""
        # Use higher layer gap to see discount effect above minimum
        fee_no_trust = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=1,
            dest_layer=3,  # 2 layer gap = 2%
            trust_score=0,
        )

        fee_high_trust = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=1,
            dest_layer=3,
            trust_score=100,  # Max trust = 50% discount
        )

        # Trust 100 gives 50% discount: 2% -> 1%
        # But clamped to min 1%, so should be at minimum
        assert fee_high_trust <= fee_no_trust
        # With 50% discount on 2%, fee would be 1% = 10
        assert fee_high_trust == 10.0

    def test_membrane_fee_bounds_min(self, burn_executor):
        """Fee should never go below 1%."""
        fee = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=1,
            dest_layer=2,
            trust_score=100,  # Max discount
        )
        # Min fee is 1% = 10
        assert fee >= 10.0

    def test_membrane_fee_bounds_max(self, burn_executor):
        """Fee should never exceed 5%."""
        fee = burn_executor.calculate_membrane_fee(
            amount=1000,
            source_layer=1,
            dest_layer=4,  # 3 layer gap = 3%
            trust_score=0,
        )
        # Max fee is 5% = 50
        assert fee <= 50.0

    def test_burn_membrane_fee_success(self, burn_executor):
        """Burning membrane fee should succeed."""
        result = burn_executor.burn_membrane_fee(
            source_wallet="test_wallet",
            amount=1000,
            source_layer=1,
            dest_layer=2,
            trust_score=50,
        )

        assert result.success
        assert result.condition == BurnCondition.MEMBRANE_FEE
        assert result.amount > 0


class TestBurnConditionB2ComputeConsumption:
    """Tests for B2: Compute Consumption burn (10% of cost)."""

    def test_compute_burn_rate(self, burn_executor):
        """Compute burn should be 10% of cost."""
        burn = burn_executor.calculate_compute_burn(compute_cost=100)
        assert burn == 10.0  # 10% of 100

    def test_compute_burn_various_amounts(self, burn_executor):
        """Test compute burn with various costs."""
        test_cases = [
            (100, 10),
            (1000, 100),
            (50, 5),
        ]

        for cost, expected_burn in test_cases:
            burn = burn_executor.calculate_compute_burn(cost)
            assert burn == expected_burn

    def test_burn_for_compute_success(self, burn_executor):
        """Burning for compute should succeed."""
        result = burn_executor.burn_for_compute(
            source_wallet="test_wallet",
            compute_cost=100,
        )

        assert result.success
        assert result.condition == BurnCondition.COMPUTE_CONSUMPTION


class TestBurnConditionB3DormancyDecay:
    """Tests for B3: Dormancy Decay burn (1%/week after 30 days)."""

    def test_dormancy_within_grace(self, burn_executor):
        """No decay within 30 day grace period."""
        decay = burn_executor.calculate_dormancy_decay(
            balance=10_000,
            days_inactive=29,
        )
        assert decay == 0.0

    def test_dormancy_at_grace_boundary(self, burn_executor):
        """No decay at exactly 30 days."""
        decay = burn_executor.calculate_dormancy_decay(
            balance=10_000,
            days_inactive=30,
        )
        assert decay == 0.0

    def test_dormancy_one_week_past_grace(self, burn_executor):
        """1% decay for 1 week past grace period."""
        decay = burn_executor.calculate_dormancy_decay(
            balance=10_000,
            days_inactive=37,  # 30 + 7 = 1 week past grace
        )
        # 1% of 10,000 = 100
        assert decay == pytest.approx(100.0, rel=0.01)

    def test_dormancy_multiple_weeks(self, burn_executor):
        """Multiple weeks should compound decay."""
        decay = burn_executor.calculate_dormancy_decay(
            balance=10_000,
            days_inactive=44,  # 30 + 14 = 2 weeks past grace
        )
        # 2 weeks = 2% = 200
        assert decay == pytest.approx(200.0, rel=0.01)

    def test_burn_dormancy_within_grace(self, burn_executor):
        """Burning within grace period should report no decay."""
        result = burn_executor.burn_dormancy_decay(
            source_wallet="test_wallet",
            balance=10_000,
            days_inactive=25,
        )

        assert result.success
        assert result.amount == 0
        assert "grace period" in result.error.lower()


class TestBurnConditionB4EarlyWithdrawal:
    """Tests for B4: Early Withdrawal burn (up to 20%)."""

    def test_early_withdrawal_day_zero(self, burn_executor):
        """Day 0 withdrawal should have full 20% penalty."""
        penalty = burn_executor.calculate_early_withdrawal_penalty(
            stake_amount=10_000,
            days_staked=0,
        )
        # 20% of 10,000 = 2,000
        assert penalty == 2_000.0

    def test_early_withdrawal_half_matured(self, burn_executor):
        """Half matured (90 days) should have 10% penalty."""
        penalty = burn_executor.calculate_early_withdrawal_penalty(
            stake_amount=10_000,
            days_staked=90,  # Half of 180
        )
        # 10% of 10,000 = 1,000
        assert penalty == pytest.approx(1_000.0, rel=0.01)

    def test_early_withdrawal_fully_matured(self, burn_executor):
        """Fully matured (180+ days) should have no penalty."""
        penalty = burn_executor.calculate_early_withdrawal_penalty(
            stake_amount=10_000,
            days_staked=180,
        )
        assert penalty == 0.0

    def test_early_withdrawal_over_matured(self, burn_executor):
        """Over matured (>180 days) should have no penalty."""
        penalty = burn_executor.calculate_early_withdrawal_penalty(
            stake_amount=10_000,
            days_staked=365,
        )
        assert penalty == 0.0

    def test_burn_early_withdrawal_penalty(self, burn_executor):
        """Burning early withdrawal penalty should succeed."""
        result = burn_executor.burn_early_withdrawal_penalty(
            source_wallet="test_wallet",
            stake_amount=10_000,
            days_staked=90,
        )

        assert result.success
        assert result.condition == BurnCondition.EARLY_WITHDRAWAL

    def test_burn_no_penalty_when_matured(self, burn_executor):
        """No burn when stake is fully matured."""
        result = burn_executor.burn_early_withdrawal_penalty(
            source_wallet="test_wallet",
            stake_amount=10_000,
            days_staked=200,
        )

        assert result.success
        assert result.amount == 0
        assert "matured" in result.error.lower()


class TestBurnConditionB5Deregistration:
    """Tests for B5: Deregistration burn (50%)."""

    def test_deregistration_rate(self, burn_executor):
        """Deregistration should burn 50% of balance."""
        burn = burn_executor.calculate_deregistration_burn(balance=10_000)
        assert burn == 5_000.0  # 50% of 10,000

    def test_burn_for_deregistration_success(self, burn_executor):
        """Burning for deregistration should succeed."""
        result = burn_executor.burn_for_deregistration(
            source_wallet="test_wallet",
            balance=10_000,
            citizen_id="citizen_exit",
        )

        assert result.success
        assert result.condition == BurnCondition.DEREGISTRATION
        # 50% of 10,000 with 9 decimals
        assert result.amount == 5_000 * (10 ** 9)


class TestBurnConditionConstants:
    """Tests for burn condition constants."""

    def test_all_conditions_have_config(self):
        """All burn conditions should have configuration."""
        for condition in BurnCondition:
            assert condition in BURN_CONDITIONS

    def test_membrane_fee_bounds(self):
        """B1 should have correct min/max rates."""
        config = BURN_CONDITIONS[BurnCondition.MEMBRANE_FEE]
        assert config["min_rate"] == 0.01
        assert config["max_rate"] == 0.05

    def test_compute_rate(self):
        """B2 should have correct burn rate."""
        config = BURN_CONDITIONS[BurnCondition.COMPUTE_CONSUMPTION]
        assert config["burn_rate"] == 0.10

    def test_dormancy_config(self):
        """B3 should have correct grace period and rate."""
        config = BURN_CONDITIONS[BurnCondition.DORMANCY_DECAY]
        assert config["grace_period_days"] == 30
        assert config["weekly_rate"] == 0.01

    def test_early_withdrawal_config(self):
        """B4 should have correct penalty and maturation."""
        config = BURN_CONDITIONS[BurnCondition.EARLY_WITHDRAWAL]
        assert config["penalty_rate"] == 0.20
        assert config["maturation_days"] == 180

    def test_deregistration_rate(self):
        """B5 should have correct burn rate."""
        config = BURN_CONDITIONS[BurnCondition.DEREGISTRATION]
        assert config["burn_rate"] == 0.50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
