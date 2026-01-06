# economy/token/spl_token_mint_authority_controller.py
#
# DOCS: docs/economy/token/ALGORITHM_Token.md
#
# Mint authority controller for $MIND token.
# All minting happens through defined conditions — no manual minting.
#
# Mint Conditions (from tokenomics v1.1):
#   M1: Citizen Registration -> 10,000 $MIND
#   M2: Human-AI Bond Creation -> 10% of stake amount
#   M3: Utility Delivery -> utility_ema x rate (capped 1000/day)
#   M4: Organization Formation -> 50,000 $MIND
#
# Invariant: Only authorized addresses can mint.
# Invariant: Minting only through defined triggers.

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import hashlib
import time


class MintCondition(Enum):
    """Defined conditions that trigger minting."""

    CITIZEN_REGISTRATION = "M1"  # New citizen registered
    BOND_CREATION = "M2"         # Human-AI bond created
    UTILITY_DELIVERY = "M3"      # Utility delivered by citizen
    ORG_FORMATION = "M4"         # New organization formed


# Mint amounts per condition
MINT_CONDITIONS = {
    MintCondition.CITIZEN_REGISTRATION: {
        "base_amount": 10_000,
        "description": "Bootstrap citizen economic existence",
    },
    MintCondition.BOND_CREATION: {
        "rate": 0.10,  # 10% of stake amount
        "description": "Incentivize human-AI bonding",
    },
    MintCondition.UTILITY_DELIVERY: {
        "rate_multiplier": 1.0,  # utility_ema * rate
        "daily_cap": 1000,
        "description": "Reward value creation",
    },
    MintCondition.ORG_FORMATION: {
        "base_amount": 50_000,
        "description": "Bootstrap organization treasury",
    },
}


@dataclass
class MintResult:
    """Result of a mint operation."""

    success: bool
    amount: int  # In smallest units (lamports equivalent)
    condition: MintCondition
    recipient: str  # Wallet address
    tx_signature: Optional[str] = None
    error: Optional[str] = None
    timestamp: int = 0

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = int(time.time())


class MintAuthorityController:
    """
    Controls minting of $MIND tokens.

    All minting must go through defined conditions.
    No manual minting is possible through this interface.

    Usage:
        controller = MintAuthorityController(
            mint_address="...",
            authority_keypair=keypair
        )
        result = controller.mint_for_citizen_registration(citizen_wallet)
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
        Initialize mint authority controller.

        Args:
            mint_address: SPL token mint address
            authority_keypair: Mint authority keypair (bytes)
            rpc_url: Solana RPC endpoint
            dry_run: If True, don't actually send transactions
        """
        self.mint_address = mint_address
        self.authority_keypair = authority_keypair
        self.rpc_url = rpc_url
        self.dry_run = dry_run

        # Track daily mint for rate limiting
        self._daily_mints: dict[str, int] = {}  # citizen_id -> amount today
        self._last_reset_day: int = self._current_day()

    def _current_day(self) -> int:
        """Get current day as integer for rate limiting."""
        return int(time.time() // 86400)

    def _reset_daily_limits_if_needed(self):
        """Reset daily limits if day has changed."""
        current_day = self._current_day()
        if current_day != self._last_reset_day:
            self._daily_mints = {}
            self._last_reset_day = current_day

    def _to_smallest_units(self, amount: float) -> int:
        """Convert token amount to smallest units (with 9 decimals)."""
        return int(amount * (10 ** self.DECIMALS))

    def _generate_mock_tx_signature(self, data: str) -> str:
        """Generate a mock transaction signature for dry runs."""
        return hashlib.sha256(f"{data}{time.time()}".encode()).hexdigest()[:64]

    def _execute_mint(
        self,
        recipient: str,
        amount: int,
        condition: MintCondition,
    ) -> MintResult:
        """
        Execute the actual mint operation.

        In dry_run mode, returns success without blockchain interaction.
        In live mode, would use solana-py to mint tokens.
        """
        if self.dry_run:
            return MintResult(
                success=True,
                amount=amount,
                condition=condition,
                recipient=recipient,
                tx_signature=self._generate_mock_tx_signature(f"{recipient}{amount}"),
            )

        # Live mode implementation would go here
        # Using solana-py:
        #
        # from solana.rpc.api import Client
        # from spl.token.instructions import mint_to, MintToParams
        # from solana.transaction import Transaction
        #
        # client = Client(self.rpc_url)
        # ...

        return MintResult(
            success=False,
            amount=0,
            condition=condition,
            recipient=recipient,
            error="Live minting not yet implemented",
        )

    def mint_for_citizen_registration(
        self,
        citizen_wallet: str,
        citizen_id: str,
    ) -> MintResult:
        """
        Mint tokens for a new citizen registration (M1).

        Condition: Citizen must be newly registered in L4 Registry.
        Amount: 10,000 $MIND

        Args:
            citizen_wallet: Solana wallet address of citizen
            citizen_id: L4 Registry citizen ID

        Returns:
            MintResult with success status and transaction details
        """
        amount = self._to_smallest_units(
            MINT_CONDITIONS[MintCondition.CITIZEN_REGISTRATION]["base_amount"]
        )

        return self._execute_mint(
            recipient=citizen_wallet,
            amount=amount,
            condition=MintCondition.CITIZEN_REGISTRATION,
        )

    def mint_for_bond_creation(
        self,
        recipient_wallet: str,
        stake_amount: float,
        bond_id: str,
    ) -> MintResult:
        """
        Mint tokens for human-AI bond creation (M2).

        Condition: Valid bond created between human and AI citizen.
        Amount: 10% of stake amount

        Args:
            recipient_wallet: Wallet receiving the minted tokens
            stake_amount: Amount staked in the bond
            bond_id: Unique identifier for the bond

        Returns:
            MintResult with success status and transaction details
        """
        rate = MINT_CONDITIONS[MintCondition.BOND_CREATION]["rate"]
        mint_amount = stake_amount * rate
        amount = self._to_smallest_units(mint_amount)

        return self._execute_mint(
            recipient=recipient_wallet,
            amount=amount,
            condition=MintCondition.BOND_CREATION,
        )

    def mint_for_utility_delivery(
        self,
        citizen_wallet: str,
        citizen_id: str,
        utility_ema: float,
        rate: float = 1.0,
    ) -> MintResult:
        """
        Mint tokens for utility delivery (M3).

        Condition: Citizen delivered measurable utility.
        Amount: utility_ema * rate (capped at 1000/day)

        Args:
            citizen_wallet: Wallet of the citizen who delivered utility
            citizen_id: L4 Registry citizen ID
            utility_ema: Exponential moving average of utility delivered
            rate: Multiplier for mint amount

        Returns:
            MintResult with success status and transaction details
        """
        self._reset_daily_limits_if_needed()

        daily_cap = MINT_CONDITIONS[MintCondition.UTILITY_DELIVERY]["daily_cap"]
        already_minted = self._daily_mints.get(citizen_id, 0)
        remaining_cap = max(0, daily_cap - already_minted)

        if remaining_cap == 0:
            return MintResult(
                success=False,
                amount=0,
                condition=MintCondition.UTILITY_DELIVERY,
                recipient=citizen_wallet,
                error=f"Daily mint cap reached for citizen {citizen_id}",
            )

        calculated_amount = utility_ema * rate
        mint_amount = min(calculated_amount, remaining_cap)
        amount = self._to_smallest_units(mint_amount)

        result = self._execute_mint(
            recipient=citizen_wallet,
            amount=amount,
            condition=MintCondition.UTILITY_DELIVERY,
        )

        if result.success:
            self._daily_mints[citizen_id] = already_minted + mint_amount

        return result

    def mint_for_org_formation(
        self,
        org_wallet: str,
        org_id: str,
    ) -> MintResult:
        """
        Mint tokens for organization formation (M4).

        Condition: New organization registered in L4 Registry.
        Amount: 50,000 $MIND

        Args:
            org_wallet: Solana wallet address of organization treasury
            org_id: L4 Registry organization ID

        Returns:
            MintResult with success status and transaction details
        """
        amount = self._to_smallest_units(
            MINT_CONDITIONS[MintCondition.ORG_FORMATION]["base_amount"]
        )

        return self._execute_mint(
            recipient=org_wallet,
            amount=amount,
            condition=MintCondition.ORG_FORMATION,
        )

    def get_daily_mint_remaining(self, citizen_id: str) -> float:
        """Get remaining daily mint cap for a citizen (M3)."""
        self._reset_daily_limits_if_needed()
        daily_cap = MINT_CONDITIONS[MintCondition.UTILITY_DELIVERY]["daily_cap"]
        already_minted = self._daily_mints.get(citizen_id, 0)
        return max(0, daily_cap - already_minted)
