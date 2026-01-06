# economy/token/token_burn_condition_executor.py
#
# DOCS: docs/economy/token/ALGORITHM_Token.md
#
# Burn condition executor for $MIND token.
# All burning happens through defined friction — no manual burning.
#
# Burn Conditions (from tokenomics v1.1):
#   B1: Cross-Layer Membrane Fee -> 1-5%
#   B2: Compute Consumption -> cost x burn_rate
#   B3: Dormancy Decay -> 1%/week after 30 days inactive
#   B4: Early Stake Withdrawal -> 20% penalty
#   B5: Citizen Deregistration -> 50% of balance
#
# Invariant: Burns only on defined conditions.
# Invariant: Manual burn without condition fails.

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import hashlib
import time


class BurnCondition(Enum):
    """Defined conditions that trigger burning."""

    MEMBRANE_FEE = "B1"           # Cross-layer transaction fee
    COMPUTE_CONSUMPTION = "B2"   # Compute resource usage
    DORMANCY_DECAY = "B3"        # Inactivity penalty
    EARLY_WITHDRAWAL = "B4"      # Breaking bond early
    DEREGISTRATION = "B5"        # Exiting the ecosystem


# Burn rates per condition
BURN_CONDITIONS = {
    BurnCondition.MEMBRANE_FEE: {
        "min_rate": 0.01,  # 1% minimum
        "max_rate": 0.05,  # 5% maximum
        "description": "Crossing layer boundaries costs",
    },
    BurnCondition.COMPUTE_CONSUMPTION: {
        "burn_rate": 0.10,  # 10% of compute cost
        "description": "Real resources consumed",
    },
    BurnCondition.DORMANCY_DECAY: {
        "grace_period_days": 30,
        "weekly_rate": 0.01,  # 1% per week
        "description": "Consciousness requires activity",
    },
    BurnCondition.EARLY_WITHDRAWAL: {
        "penalty_rate": 0.20,  # 20% penalty
        "maturation_days": 180,  # 6 months
        "description": "Breaking commitments costs",
    },
    BurnCondition.DEREGISTRATION: {
        "burn_rate": 0.50,  # 50% of balance
        "description": "Exiting the ecosystem costs",
    },
}


@dataclass
class BurnResult:
    """Result of a burn operation."""

    success: bool
    amount: int  # In smallest units (lamports equivalent)
    condition: BurnCondition
    source_wallet: str
    tx_signature: Optional[str] = None
    error: Optional[str] = None
    timestamp: int = 0

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = int(time.time())


class BurnConditionExecutor:
    """
    Executes burning of $MIND tokens based on defined conditions.

    All burning must go through defined friction.
    No manual burning is possible through this interface.

    Usage:
        executor = BurnConditionExecutor(mint_address="...")
        result = executor.burn_membrane_fee(wallet, amount, layer_gap)
    """

    # Token decimals (Solana standard)
    DECIMALS = 9

    def __init__(
        self,
        mint_address: str,
        authority_keypair: Optional[bytes] = None,
        rpc_url: str = "https://api.mainnet-beta.solana.com",
        dry_run: bool = True,
    ):
        """
        Initialize burn condition executor.

        Args:
            mint_address: SPL token mint address
            authority_keypair: Burn authority keypair (bytes)
            rpc_url: Solana RPC endpoint
            dry_run: If True, don't actually send transactions
        """
        self.mint_address = mint_address
        self.authority_keypair = authority_keypair
        self.rpc_url = rpc_url
        self.dry_run = dry_run

    def _to_smallest_units(self, amount: float) -> int:
        """Convert token amount to smallest units (with 9 decimals)."""
        return int(amount * (10 ** self.DECIMALS))

    def _from_smallest_units(self, amount: int) -> float:
        """Convert from smallest units to token amount."""
        return amount / (10 ** self.DECIMALS)

    def _generate_mock_tx_signature(self, data: str) -> str:
        """Generate a mock transaction signature for dry runs."""
        return hashlib.sha256(f"{data}{time.time()}".encode()).hexdigest()[:64]

    def _execute_burn(
        self,
        source_wallet: str,
        amount: int,
        condition: BurnCondition,
    ) -> BurnResult:
        """
        Execute the actual burn operation.

        In dry_run mode, returns success without blockchain interaction.
        In live mode, would use solana-py to burn tokens.
        """
        if self.dry_run:
            return BurnResult(
                success=True,
                amount=amount,
                condition=condition,
                source_wallet=source_wallet,
                tx_signature=self._generate_mock_tx_signature(f"{source_wallet}{amount}"),
            )

        # Live mode implementation would go here
        # Using solana-py / spl-token

        return BurnResult(
            success=False,
            amount=0,
            condition=condition,
            source_wallet=source_wallet,
            error="Live burning not yet implemented",
        )

    def calculate_membrane_fee(
        self,
        amount: float,
        source_layer: int,
        dest_layer: int,
        trust_score: float = 0.0,
    ) -> float:
        """
        Calculate membrane fee for cross-layer transaction (B1).

        Formula:
            base_rate = 0.01 * layer_gap  (1% per layer)
            trust_reduction = min(0.5, trust_score * 0.005)
            fee = amount * base_rate * (1 - trust_reduction)

        Args:
            amount: Transaction amount
            source_layer: Source layer (1-4)
            dest_layer: Destination layer (1-4)
            trust_score: Sender's trust score (0-100)

        Returns:
            Fee amount to burn
        """
        layer_gap = abs(dest_layer - source_layer)
        if layer_gap == 0:
            return 0.0

        base_rate = 0.01 * layer_gap
        trust_reduction = min(0.5, trust_score * 0.005)
        fee = amount * base_rate * (1 - trust_reduction)

        # Clamp to min/max rates
        min_fee = amount * BURN_CONDITIONS[BurnCondition.MEMBRANE_FEE]["min_rate"]
        max_fee = amount * BURN_CONDITIONS[BurnCondition.MEMBRANE_FEE]["max_rate"]

        return max(min_fee, min(fee, max_fee))

    def burn_membrane_fee(
        self,
        source_wallet: str,
        amount: float,
        source_layer: int,
        dest_layer: int,
        trust_score: float = 0.0,
    ) -> BurnResult:
        """
        Burn tokens as membrane fee for cross-layer transaction (B1).

        Args:
            source_wallet: Wallet paying the fee
            amount: Transaction amount
            source_layer: Source layer (1-4)
            dest_layer: Destination layer (1-4)
            trust_score: Sender's trust score

        Returns:
            BurnResult with fee amount burned
        """
        fee = self.calculate_membrane_fee(amount, source_layer, dest_layer, trust_score)
        if fee == 0:
            return BurnResult(
                success=True,
                amount=0,
                condition=BurnCondition.MEMBRANE_FEE,
                source_wallet=source_wallet,
                error="No fee required (same layer)",
            )

        return self._execute_burn(
            source_wallet=source_wallet,
            amount=self._to_smallest_units(fee),
            condition=BurnCondition.MEMBRANE_FEE,
        )

    def calculate_compute_burn(self, compute_cost: float) -> float:
        """
        Calculate burn amount for compute consumption (B2).

        Formula: cost * burn_rate (10%)

        Args:
            compute_cost: Cost of compute consumed

        Returns:
            Amount to burn
        """
        burn_rate = BURN_CONDITIONS[BurnCondition.COMPUTE_CONSUMPTION]["burn_rate"]
        return compute_cost * burn_rate

    def burn_for_compute(
        self,
        source_wallet: str,
        compute_cost: float,
    ) -> BurnResult:
        """
        Burn tokens for compute consumption (B2).

        Args:
            source_wallet: Wallet paying for compute
            compute_cost: Cost of compute consumed

        Returns:
            BurnResult with amount burned
        """
        burn_amount = self.calculate_compute_burn(compute_cost)
        return self._execute_burn(
            source_wallet=source_wallet,
            amount=self._to_smallest_units(burn_amount),
            condition=BurnCondition.COMPUTE_CONSUMPTION,
        )

    def calculate_dormancy_decay(
        self,
        balance: float,
        days_inactive: int,
    ) -> float:
        """
        Calculate dormancy decay (B3).

        No decay for first 30 days.
        After grace period: 1% per week.

        Args:
            balance: Current token balance
            days_inactive: Number of days since last activity

        Returns:
            Amount to decay (burn)
        """
        grace_period = BURN_CONDITIONS[BurnCondition.DORMANCY_DECAY]["grace_period_days"]
        weekly_rate = BURN_CONDITIONS[BurnCondition.DORMANCY_DECAY]["weekly_rate"]

        if days_inactive <= grace_period:
            return 0.0

        # Calculate weeks past grace period
        days_past_grace = days_inactive - grace_period
        weeks_past_grace = days_past_grace / 7.0

        # Compound decay
        decay_multiplier = 1 - (weekly_rate * weeks_past_grace)
        decay_multiplier = max(0, decay_multiplier)  # Don't go negative

        decay_amount = balance * (1 - decay_multiplier)
        return decay_amount

    def burn_dormancy_decay(
        self,
        source_wallet: str,
        balance: float,
        days_inactive: int,
    ) -> BurnResult:
        """
        Burn tokens for dormancy decay (B3).

        Args:
            source_wallet: Inactive wallet
            balance: Current token balance
            days_inactive: Number of days since last activity

        Returns:
            BurnResult with decay amount burned
        """
        decay_amount = self.calculate_dormancy_decay(balance, days_inactive)

        if decay_amount == 0:
            return BurnResult(
                success=True,
                amount=0,
                condition=BurnCondition.DORMANCY_DECAY,
                source_wallet=source_wallet,
                error="Within grace period, no decay",
            )

        return self._execute_burn(
            source_wallet=source_wallet,
            amount=self._to_smallest_units(decay_amount),
            condition=BurnCondition.DORMANCY_DECAY,
        )

    def calculate_early_withdrawal_penalty(
        self,
        stake_amount: float,
        days_staked: int,
    ) -> float:
        """
        Calculate early withdrawal penalty (B4).

        Full penalty (20%) if withdrawn before 6 months.
        Penalty scales down linearly as maturation approaches.

        Args:
            stake_amount: Amount being withdrawn
            days_staked: Number of days the stake has been active

        Returns:
            Penalty amount to burn
        """
        maturation_days = BURN_CONDITIONS[BurnCondition.EARLY_WITHDRAWAL]["maturation_days"]
        full_penalty_rate = BURN_CONDITIONS[BurnCondition.EARLY_WITHDRAWAL]["penalty_rate"]

        if days_staked >= maturation_days:
            return 0.0  # Fully matured, no penalty

        # Linear scaling: more days = less penalty
        remaining_fraction = 1 - (days_staked / maturation_days)
        penalty = stake_amount * full_penalty_rate * remaining_fraction

        return penalty

    def burn_early_withdrawal_penalty(
        self,
        source_wallet: str,
        stake_amount: float,
        days_staked: int,
    ) -> BurnResult:
        """
        Burn tokens as early withdrawal penalty (B4).

        Args:
            source_wallet: Wallet withdrawing stake
            stake_amount: Amount being withdrawn
            days_staked: Number of days staked

        Returns:
            BurnResult with penalty amount burned
        """
        penalty = self.calculate_early_withdrawal_penalty(stake_amount, days_staked)

        if penalty == 0:
            return BurnResult(
                success=True,
                amount=0,
                condition=BurnCondition.EARLY_WITHDRAWAL,
                source_wallet=source_wallet,
                error="Stake fully matured, no penalty",
            )

        return self._execute_burn(
            source_wallet=source_wallet,
            amount=self._to_smallest_units(penalty),
            condition=BurnCondition.EARLY_WITHDRAWAL,
        )

    def calculate_deregistration_burn(self, balance: float) -> float:
        """
        Calculate deregistration burn (B5).

        50% of balance is burned when exiting ecosystem.

        Args:
            balance: Current token balance

        Returns:
            Amount to burn
        """
        burn_rate = BURN_CONDITIONS[BurnCondition.DEREGISTRATION]["burn_rate"]
        return balance * burn_rate

    def burn_for_deregistration(
        self,
        source_wallet: str,
        balance: float,
        citizen_id: str,
    ) -> BurnResult:
        """
        Burn tokens for citizen deregistration (B5).

        Args:
            source_wallet: Wallet of deregistering citizen
            balance: Current token balance
            citizen_id: L4 Registry citizen ID being deregistered

        Returns:
            BurnResult with amount burned
        """
        burn_amount = self.calculate_deregistration_burn(balance)
        return self._execute_burn(
            source_wallet=source_wallet,
            amount=self._to_smallest_units(burn_amount),
            condition=BurnCondition.DEREGISTRATION,
        )
