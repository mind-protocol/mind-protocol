# economy/token/constants.py
#
# DOCS: docs/economy/token/SPL_TOKEN_2022_SPECS.md
#
# Constants for $MIND Token 2022 implementation.
# CRITICAL: These values must be set correctly BEFORE token creation.
# Extensions cannot be added after mint initialization.

from enum import Enum

# =============================================================================
# PROGRAM IDs
# =============================================================================

# CRITICAL: Use Token 2022, not legacy SPL Token
TOKEN_2022_PROGRAM_ID = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
TOKEN_PROGRAM_ID_LEGACY = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Don't use

# Metaplex Token Metadata (for additional metadata if needed)
METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"

# Our transfer hook program (deployed BEFORE token creation)
TRANSFER_HOOK_PROGRAM_ID = "325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD"


# =============================================================================
# TOKEN PROPERTIES
# =============================================================================

TOKEN_NAME = "MIND"
TOKEN_SYMBOL = "MIND"
TOKEN_DECIMALS = 9  # Solana standard
TOKEN_URI = "https://mind-protocol.org/token-metadata.json"


# =============================================================================
# TRANSFER FEE CONFIG
# =============================================================================

# Basis points (1 bp = 0.01%)
TRANSFER_FEE_BASIS_POINTS = 100  # 1% baseline protocol fee
TRANSFER_FEE_MAX = 1_000_000_000  # 1 $MIND max fee per transfer (in smallest units)

# Note: Layer-based fees (1-5%) will be handled by TransferHook program
# TransferFee extension provides 1% baseline
# TransferHook calculates additional layer fee


# =============================================================================
# MINT CONDITIONS (from tokenomics v1.1)
# =============================================================================

class MintCondition(Enum):
    """Defined conditions that trigger minting."""
    CITIZEN_REGISTRATION = "M1"  # 10,000 $MIND
    BOND_CREATION = "M2"         # 10% of stake
    UTILITY_DELIVERY = "M3"      # utility_ema × rate (cap 1000/day)
    ORG_FORMATION = "M4"         # 50,000 $MIND


MINT_AMOUNTS = {
    MintCondition.CITIZEN_REGISTRATION: 10_000,
    MintCondition.BOND_CREATION: 0.10,  # Rate
    MintCondition.UTILITY_DELIVERY: 1000,  # Daily cap
    MintCondition.ORG_FORMATION: 50_000,
}


# =============================================================================
# BURN CONDITIONS (from tokenomics v1.1)
# =============================================================================

class BurnCondition(Enum):
    """Defined conditions that trigger burning."""
    MEMBRANE_FEE = "B1"           # 1-5% (layer-based)
    COMPUTE_CONSUMPTION = "B2"    # cost × 10%
    DORMANCY_DECAY = "B3"         # 1%/week after 30 days
    EARLY_WITHDRAWAL = "B4"       # Up to 20%
    DEREGISTRATION = "B5"         # 50% of balance


BURN_RATES = {
    BurnCondition.MEMBRANE_FEE: {"min": 0.01, "max": 0.05},
    BurnCondition.COMPUTE_CONSUMPTION: 0.10,
    BurnCondition.DORMANCY_DECAY: {"grace_days": 30, "weekly_rate": 0.01},
    BurnCondition.EARLY_WITHDRAWAL: {"maturation_days": 180, "penalty_rate": 0.20},
    BurnCondition.DEREGISTRATION: 0.50,
}


# =============================================================================
# DEVNET DEPLOYMENT (2025-01-06)
# =============================================================================

DEVNET_TOKEN_MINT = "BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa"
DEVNET_MINT_AUTHORITY = "CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg"
DEVNET_TRANSFER_HOOK = TRANSFER_HOOK_PROGRAM_ID  # Same program on devnet


# =============================================================================
# AUTHORITIES
# =============================================================================

# Initial: Single wallet (devnet)
# Long-term: Multi-sig (mainnet)

class AuthorityRole(Enum):
    """Authority roles for token governance."""
    MINT = "mint"                    # Can mint new tokens
    FREEZE = "freeze"                # Can freeze accounts (DISABLED - null)
    TRANSFER_FEE = "transfer_fee"    # Can change fee %
    WITHDRAW_FEE = "withdraw_fee"    # Can collect withheld fees
    TRANSFER_HOOK = "transfer_hook"  # Can change hook program
    METADATA = "metadata"            # Can update metadata
    MINT_CLOSE = "mint_close"        # Can close the mint


# Devnet authorities (mint authority = deployer wallet)
AUTHORITIES = {
    AuthorityRole.MINT: DEVNET_MINT_AUTHORITY,
    AuthorityRole.FREEZE: None,  # IMPORTANT: Keep null for censorship resistance
    AuthorityRole.TRANSFER_FEE: DEVNET_MINT_AUTHORITY,
    AuthorityRole.WITHDRAW_FEE: DEVNET_MINT_AUTHORITY,
    AuthorityRole.TRANSFER_HOOK: DEVNET_MINT_AUTHORITY,
    AuthorityRole.METADATA: DEVNET_MINT_AUTHORITY,
    AuthorityRole.MINT_CLOSE: DEVNET_MINT_AUTHORITY,
}


# =============================================================================
# EXTENSIONS TO ACTIVATE
# =============================================================================

# These extensions MUST be activated at token creation
# Cannot be added later!

EXTENSIONS_TO_ACTIVATE = [
    "TransferFeeConfig",     # For membrane fees
    "TransferHook",          # For custom logic
    "MetadataPointer",       # Points to on-chain metadata
    "TokenMetadata",         # Stores name, symbol, uri
    "MintCloseAuthority",    # Option to close mint
]

# Extensions we explicitly DO NOT activate
EXTENSIONS_NOT_TO_USE = [
    "PermanentDelegate",     # Too much centralized power
    "NonTransferable",       # We want transfers
    "DefaultAccountState",   # No freeze by default
    "ConfidentialTransfer",  # Transparency OK
    "InterestBearing",       # Not our model
]


# =============================================================================
# RPC ENDPOINTS
# =============================================================================

RPC_ENDPOINTS = {
    "devnet": "https://api.devnet.solana.com",
    "testnet": "https://api.testnet.solana.com",
    "mainnet-beta": "https://api.mainnet-beta.solana.com",
    "mainnet": "https://api.mainnet-beta.solana.com",
}


# =============================================================================
# VALIDATION
# =============================================================================

def validate_configuration():
    """
    Validate that configuration is ready for deployment.
    Returns (is_valid, list of issues).
    """
    issues = []

    if TRANSFER_HOOK_PROGRAM_ID is None:
        issues.append("TRANSFER_HOOK_PROGRAM_ID not set - deploy hook program first")

    if AUTHORITIES[AuthorityRole.MINT] is None:
        issues.append("Mint authority not configured")

    if AUTHORITIES[AuthorityRole.FREEZE] is not None:
        issues.append("Freeze authority should be null for censorship resistance")

    # Check URI is hosted
    if not TOKEN_URI or TOKEN_URI.startswith("https://example"):
        issues.append("TOKEN_URI not configured - host metadata JSON first")

    return (len(issues) == 0, issues)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def to_smallest_units(amount: float) -> int:
    """Convert token amount to smallest units (with decimals)."""
    return int(amount * (10 ** TOKEN_DECIMALS))


def from_smallest_units(amount: int) -> float:
    """Convert from smallest units to token amount."""
    return amount / (10 ** TOKEN_DECIMALS)
