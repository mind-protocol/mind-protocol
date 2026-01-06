# tests/economy/test_token_mint_conditions.py
#
# Tests for $MIND token mint conditions (M1-M4)
# DOCS: docs/economy/token/VALIDATION_Token.md

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from economy.token.spl_token_mint_authority_controller import (
    MintCondition,
    MintResult,
    MintAuthorityController,
    MINT_CONDITIONS,
)


@pytest.fixture
def mint_controller():
    """Create a mint controller in dry run mode."""
    return MintAuthorityController(
        mint_address="test_mint_address",
        dry_run=True,
    )


class TestMintConditionM1CitizenRegistration:
    """Tests for M1: Citizen Registration mint (10,000 $MIND)."""

    def test_citizen_registration_amount(self, mint_controller):
        """Citizen registration should mint exactly 10,000 $MIND."""
        result = mint_controller.mint_for_citizen_registration(
            citizen_wallet="test_wallet",
            citizen_id="citizen_001",
        )

        assert result.success
        assert result.condition == MintCondition.CITIZEN_REGISTRATION
        # 10,000 $MIND with 9 decimals = 10,000 * 10^9
        assert result.amount == 10_000 * (10 ** 9)

    def test_citizen_registration_generates_tx(self, mint_controller):
        """Successful mint should have transaction signature."""
        result = mint_controller.mint_for_citizen_registration(
            citizen_wallet="test_wallet",
            citizen_id="citizen_002",
        )

        assert result.success
        assert result.tx_signature is not None
        assert len(result.tx_signature) > 0

    def test_citizen_registration_records_recipient(self, mint_controller):
        """Result should record the recipient wallet."""
        wallet = "recipient_wallet_123"
        result = mint_controller.mint_for_citizen_registration(
            citizen_wallet=wallet,
            citizen_id="citizen_003",
        )

        assert result.recipient == wallet


class TestMintConditionM2BondCreation:
    """Tests for M2: Bond Creation mint (10% of stake)."""

    def test_bond_creation_rate(self, mint_controller):
        """Bond creation should mint 10% of stake amount."""
        stake_amount = 50_000
        result = mint_controller.mint_for_bond_creation(
            recipient_wallet="test_wallet",
            stake_amount=stake_amount,
            bond_id="bond_001",
        )

        assert result.success
        assert result.condition == MintCondition.BOND_CREATION
        # 10% of 50,000 = 5,000 with 9 decimals
        expected = int(stake_amount * 0.10 * (10 ** 9))
        assert result.amount == expected

    def test_bond_creation_various_amounts(self, mint_controller):
        """Test bond creation with various stake amounts."""
        test_cases = [
            (10_000, 1_000),    # 10% of 10K = 1K
            (100_000, 10_000),  # 10% of 100K = 10K
            (1_000, 100),      # 10% of 1K = 100
        ]

        for stake, expected_mint in test_cases:
            result = mint_controller.mint_for_bond_creation(
                recipient_wallet="test_wallet",
                stake_amount=stake,
                bond_id=f"bond_{stake}",
            )

            assert result.success
            assert result.amount == int(expected_mint * (10 ** 9))


class TestMintConditionM3UtilityDelivery:
    """Tests for M3: Utility Delivery mint (capped at 1000/day)."""

    def test_utility_delivery_normal(self, mint_controller):
        """Normal utility delivery should mint based on EMA."""
        result = mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id="citizen_001",
            utility_ema=500,
            rate=1.0,
        )

        assert result.success
        assert result.condition == MintCondition.UTILITY_DELIVERY
        assert result.amount == 500 * (10 ** 9)

    def test_utility_delivery_daily_cap(self, mint_controller):
        """Utility delivery should be capped at 1000/day per citizen."""
        citizen_id = "citizen_cap_test"

        # First mint: 800 (under cap)
        result1 = mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id=citizen_id,
            utility_ema=800,
        )
        assert result1.success
        assert result1.amount == 800 * (10 ** 9)

        # Second mint: should be capped at 200 (1000 - 800)
        result2 = mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id=citizen_id,
            utility_ema=500,  # Wants 500 but only 200 available
        )
        assert result2.success
        assert result2.amount == 200 * (10 ** 9)

        # Third mint: should fail (cap reached)
        result3 = mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id=citizen_id,
            utility_ema=100,
        )
        assert not result3.success
        assert "cap reached" in result3.error.lower()

    def test_utility_delivery_rate_multiplier(self, mint_controller):
        """Utility delivery should respect rate multiplier."""
        result = mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id="citizen_rate",
            utility_ema=100,
            rate=2.0,  # 2x multiplier
        )

        assert result.success
        assert result.amount == 200 * (10 ** 9)  # 100 * 2.0

    def test_utility_delivery_remaining_cap(self, mint_controller):
        """get_daily_mint_remaining should track cap correctly."""
        citizen_id = "citizen_remaining"

        # Initially full cap available
        remaining = mint_controller.get_daily_mint_remaining(citizen_id)
        assert remaining == 1000

        # After minting 400
        mint_controller.mint_for_utility_delivery(
            citizen_wallet="test_wallet",
            citizen_id=citizen_id,
            utility_ema=400,
        )
        remaining = mint_controller.get_daily_mint_remaining(citizen_id)
        assert remaining == 600


class TestMintConditionM4OrgFormation:
    """Tests for M4: Organization Formation mint (50,000 $MIND)."""

    def test_org_formation_amount(self, mint_controller):
        """Org formation should mint exactly 50,000 $MIND."""
        result = mint_controller.mint_for_org_formation(
            org_wallet="org_wallet",
            org_id="org_001",
        )

        assert result.success
        assert result.condition == MintCondition.ORG_FORMATION
        # 50,000 $MIND with 9 decimals
        assert result.amount == 50_000 * (10 ** 9)


class TestMintConditionConstants:
    """Tests for mint condition constants."""

    def test_all_conditions_have_config(self):
        """All mint conditions should have configuration."""
        for condition in MintCondition:
            assert condition in MINT_CONDITIONS
            assert "description" in MINT_CONDITIONS[condition]

    def test_citizen_registration_config(self):
        """M1 should have correct base amount."""
        config = MINT_CONDITIONS[MintCondition.CITIZEN_REGISTRATION]
        assert config["base_amount"] == 10_000

    def test_bond_creation_config(self):
        """M2 should have correct rate."""
        config = MINT_CONDITIONS[MintCondition.BOND_CREATION]
        assert config["rate"] == 0.10

    def test_utility_delivery_config(self):
        """M3 should have correct daily cap."""
        config = MINT_CONDITIONS[MintCondition.UTILITY_DELIVERY]
        assert config["daily_cap"] == 1000

    def test_org_formation_config(self):
        """M4 should have correct base amount."""
        config = MINT_CONDITIONS[MintCondition.ORG_FORMATION]
        assert config["base_amount"] == 50_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
