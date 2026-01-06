# economy/token — $MIND SPL Token Infrastructure
#
# DOCS: docs/economy/token/IMPLEMENTATION_Token.md
#
# This module implements the $MIND token on Solana:
# - Mint authority control (mechanical minting only)
# - Burn condition evaluation and execution
# - Token metadata management (Metaplex)
# - Deployment script and configuration
# - Supply target calculation
#
# Core principle: All supply changes through mechanics, not manual control.

from .spl_token_mint_authority_controller import (
    MintCondition,
    MintResult,
    MintAuthorityController,
    MINT_CONDITIONS,
)

from .token_burn_condition_executor import (
    BurnCondition,
    BurnResult,
    BurnConditionExecutor,
    BURN_CONDITIONS,
)

from .metaplex_token_metadata_manager import (
    TokenMetadata,
    MetadataManager,
)

from .token_supply_target_calculator import (
    SupplyMetrics,
    calculate_target_supply,
    calculate_supply_adjustment,
    calculate_health_indicators,
)

from .solana_token_deployment_script import (
    DeploymentConfig,
    TokenDeployer,
)

__all__ = [
    # Mint
    "MintCondition",
    "MintResult",
    "MintAuthorityController",
    "MINT_CONDITIONS",
    # Burn
    "BurnCondition",
    "BurnResult",
    "BurnConditionExecutor",
    "BURN_CONDITIONS",
    # Metadata
    "TokenMetadata",
    "MetadataManager",
    # Supply
    "SupplyMetrics",
    "calculate_target_supply",
    "calculate_supply_adjustment",
    "calculate_health_indicators",
    # Deployment
    "DeploymentConfig",
    "TokenDeployer",
]
