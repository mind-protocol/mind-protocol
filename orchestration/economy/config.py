"""
Token Economy Configuration
Based on MIND_TOKEN_ECONOMICS.md

All constants for $MIND token deployment, distribution, and tracking.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


# ==============================================================================
# TOKEN PARAMETERS
# ==============================================================================

class TokenConfig:
    """SPL Token-2022 configuration for $MIND"""

    # Core parameters
    TOKEN_NAME = "MIND"
    TOKEN_SYMBOL = "$MIND"
    TOTAL_SUPPLY = 1_000_000_000  # 1 billion tokens
    INITIAL_EMISSION = 200_000_000  # 20% emitted at launch
    DECIMALS = 9  # Standard Solana decimals

    # Token-2022 features
    ENABLE_TRANSFER_RESTRICTIONS = True  # For 6-month locks
    ENABLE_METADATA = True  # For rich token info
    RETAIN_MINT_AUTHORITY = True  # For future emissions
    RETAIN_FREEZE_AUTHORITY = True  # For compliance


# ==============================================================================
# ALLOCATION & DISTRIBUTION
# ==============================================================================

class AllocationConfig:
    """Token allocation based on tokenomics spec"""

    # Allocation (in tokens)
    COMMUNITY_ECOSYSTEM = 300_000_000  # 30%
    STRATEGIC_RESERVE = 380_000_000    # 38%
    TEAM_FOUNDERS = 150_000_000        # 15%
    OPERATIONS_UBC = 100_000_000       # 10%
    LIQUIDITY = 50_000_000             # 5%
    INVESTORS = 20_000_000             # 2%

    # Initial unlock amounts
    COMMUNITY_INITIAL = 30_000_000
    STRATEGIC_INITIAL = 50_000_000
    TEAM_INITIAL = 150_000_000
    OPERATIONS_INITIAL = 100_000_000
    LIQUIDITY_INITIAL = 450            # For minimal LP
    INVESTORS_INITIAL = 20_000_000

    # Lock durations (in days)
    INVESTOR_LOCK_DAYS = 180           # 6 months
    TEAM_LOCK_DAYS = 180               # 6 months
    LP_LOCK_DAYS = 365                 # 12 months


# ==============================================================================
# INVESTOR AIRDROP
# ==============================================================================

class AirdropConfig:
    """Psychological airdrop to 20 burned investors"""

    TOKENS_PER_INVESTOR = 10_000
    INVESTOR_COUNT = 20
    TOTAL_AIRDROP = TOKENS_PER_INVESTOR * INVESTOR_COUNT  # 200,000
    LOCK_DAYS = 180  # 6 months

    # Investor wallet addresses (to be populated)
    INVESTOR_WALLETS = [
        # TODO: Add 20 wallet addresses
        # "wallet1_address_here",
        # "wallet2_address_here",
        # ...
    ]


# ==============================================================================
# OTC INVESTMENT
# ==============================================================================

class OTCConfig:
    """Off-exchange token sales for bridge capital"""

    # Remaining tokens after airdrop
    AVAILABLE_TOKENS = AllocationConfig.INVESTORS - AirdropConfig.TOTAL_AIRDROP  # 19,800,000

    # Investment parameters
    INVESTMENT_AMOUNT_EUR = 2_000      # Per investor
    LOCK_DAYS = 180                    # 6 months

    # Scenarios
    CONSERVATIVE_INVESTORS = 5
    BASE_INVESTORS = 8
    OPTIMISTIC_INVESTORS = 10

    @staticmethod
    def tokens_per_investor(investor_count: int) -> int:
        """Calculate tokens per investor based on participation"""
        return OTCConfig.AVAILABLE_TOKENS // investor_count


# ==============================================================================
# LIQUIDITY POOL
# ==============================================================================

class LiquidityConfig:
    """Raydium pool configuration + Meteora lock"""

    # Initial LP parameters
    SOL_AMOUNT = 0.25                  # SOL allocated for LP
    MIND_AMOUNT = 450                  # $MIND tokens for LP
    TARGET_PRICE = 1.00                # $1.00 per token

    # Lock parameters
    LOCK_DAYS = 365                    # 12 months
    LOCK_PLATFORM = "Meteora"          # Free on Solana
    LOCK_PERCENTAGE = 100              # Lock 100% of LP tokens

    # DEX configuration
    DEX = "Raydium"
    POOL_TYPE = "CPMM"                 # Constant Product Market Maker


# ==============================================================================
# MULTI-SIG GOVERNANCE
# ==============================================================================

class GovernanceConfig:
    """2/3 multi-sig for DAO Treasury + UBC Reserve"""

    THRESHOLD = 2                      # Requires 2 of 3 signatures
    SIGNER_COUNT = 3                   # Founder + 2 advisors

    # Controlled reserves
    DAO_TREASURY = 200_000_000         # From Strategic Reserve
    UBC_RESERVE = 100_000_000          # Operations & UBC allocation

    # Signer addresses (to be populated)
    SIGNERS = [
        # TODO: Add 3 signer addresses
        # "founder_wallet_address",
        # "advisor1_wallet_address",
        # "advisor2_wallet_address",
    ]


# ==============================================================================
# FINANCIAL PROJECTIONS
# ==============================================================================

@dataclass
class FinancialScenario:
    """Financial projection scenario"""
    name: str
    bridge_capital_eur: int
    investors_count: int
    revenue_conversions: int
    revenue_eur: int

    @property
    def total_raised_eur(self) -> int:
        return self.bridge_capital_eur + self.revenue_eur

    @property
    def runway_months(self) -> float:
        return self.total_raised_eur / BurnConfig.MONTHLY_BURN_EUR


class BurnConfig:
    """Operating costs and runway calculations"""

    MONTHLY_BURN_EUR = 4_000

    # Scenarios from tokenomics doc
    CONSERVATIVE = FinancialScenario(
        name="Conservative",
        bridge_capital_eur=10_000,
        investors_count=5,
        revenue_conversions=2,
        revenue_eur=4_000
    )

    BASE = FinancialScenario(
        name="Base",
        bridge_capital_eur=16_000,
        investors_count=8,
        revenue_conversions=3,
        revenue_eur=6_000
    )

    OPTIMISTIC = FinancialScenario(
        name="Optimistic",
        bridge_capital_eur=20_000,
        investors_count=10,
        revenue_conversions=6,
        revenue_eur=12_000
    )


# ==============================================================================
# SOLANA NETWORK
# ==============================================================================

class NetworkConfig:
    """Solana network configuration"""

    # Network selection
    CLUSTER = "mainnet-beta"  # or "devnet" for testing
    RPC_URL = "https://api.mainnet-beta.solana.com"  # Public RPC

    # Program IDs
    TOKEN_2022_PROGRAM_ID = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
    RAYDIUM_PROGRAM_ID = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"

    # Cost estimates
    TOKEN_CREATION_SOL = 0.01          # ~$1.80
    AIRDROP_SOL_PER_TX = 0.000005      # Very cheap
    LP_CREATION_SOL = 0.02             # ~$3.60
    TOTAL_ESTIMATED_SOL = 0.30         # ~$54 total


# ==============================================================================
# DEPLOYMENT STATE
# ==============================================================================

class DeploymentState:
    """Track deployment progress and addresses"""

    def __init__(self):
        self.token_mint: Optional[str] = None
        self.liquidity_pool: Optional[str] = None
        self.multisig_wallet: Optional[str] = None
        self.airdrop_completed: bool = False
        self.lp_locked: bool = False
        self.deployment_timestamp: Optional[int] = None

    def to_dict(self) -> dict:
        """Serialize state for persistence"""
        return {
            "token_mint": self.token_mint,
            "liquidity_pool": self.liquidity_pool,
            "multisig_wallet": self.multisig_wallet,
            "airdrop_completed": self.airdrop_completed,
            "lp_locked": self.lp_locked,
            "deployment_timestamp": self.deployment_timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DeploymentState':
        """Deserialize state from persistence"""
        state = cls()
        state.token_mint = data.get("token_mint")
        state.liquidity_pool = data.get("liquidity_pool")
        state.multisig_wallet = data.get("multisig_wallet")
        state.airdrop_completed = data.get("airdrop_completed", False)
        state.lp_locked = data.get("lp_locked", False)
        state.deployment_timestamp = data.get("deployment_timestamp")
        return state


# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_config():
    """Validate configuration consistency"""

    # Validate allocation adds up to total supply
    total_allocated = (
        AllocationConfig.COMMUNITY_ECOSYSTEM +
        AllocationConfig.STRATEGIC_RESERVE +
        AllocationConfig.TEAM_FOUNDERS +
        AllocationConfig.OPERATIONS_UBC +
        AllocationConfig.LIQUIDITY +
        AllocationConfig.INVESTORS
    )

    assert total_allocated == TokenConfig.TOTAL_SUPPLY, \
        f"Allocation mismatch: {total_allocated} != {TokenConfig.TOTAL_SUPPLY}"

    # Validate airdrop is within investor allocation
    assert AirdropConfig.TOTAL_AIRDROP <= AllocationConfig.INVESTORS, \
        "Airdrop exceeds investor allocation"

    # Validate OTC tokens available
    expected_otc = AllocationConfig.INVESTORS - AirdropConfig.TOTAL_AIRDROP
    assert OTCConfig.AVAILABLE_TOKENS == expected_otc, \
        f"OTC tokens mismatch: {OTCConfig.AVAILABLE_TOKENS} != {expected_otc}"

    # Validate investor wallets count
    if AirdropConfig.INVESTOR_WALLETS:
        assert len(AirdropConfig.INVESTOR_WALLETS) == AirdropConfig.INVESTOR_COUNT, \
            f"Wallet count mismatch: {len(AirdropConfig.INVESTOR_WALLETS)} != {AirdropConfig.INVESTOR_COUNT}"

    # Validate multisig signers
    if GovernanceConfig.SIGNERS:
        assert len(GovernanceConfig.SIGNERS) == GovernanceConfig.SIGNER_COUNT, \
            f"Signer count mismatch: {len(GovernanceConfig.SIGNERS)} != {GovernanceConfig.SIGNER_COUNT}"

    return True


if __name__ == "__main__":
    # Run validation when executed directly
    try:
        validate_config()
        print("✅ Configuration validation passed")
        print(f"\nToken: {TokenConfig.TOKEN_SYMBOL}")
        print(f"Total Supply: {TokenConfig.TOTAL_SUPPLY:,}")
        print(f"Initial Emission: {TokenConfig.INITIAL_EMISSION:,} ({TokenConfig.INITIAL_EMISSION/TokenConfig.TOTAL_SUPPLY*100:.0f}%)")
        print(f"\nEstimated Deployment Cost: {NetworkConfig.TOTAL_ESTIMATED_SOL} SOL")
        print(f"\nScenarios:")
        print(f"  Conservative: €{BurnConfig.CONSERVATIVE.total_raised_eur:,} = {BurnConfig.CONSERVATIVE.runway_months:.1f} months")
        print(f"  Base: €{BurnConfig.BASE.total_raised_eur:,} = {BurnConfig.BASE.runway_months:.1f} months")
        print(f"  Optimistic: €{BurnConfig.OPTIMISTIC.total_raised_eur:,} = {BurnConfig.OPTIMISTIC.runway_months:.1f} months")
    except AssertionError as e:
        print(f"❌ Configuration validation failed: {e}")
