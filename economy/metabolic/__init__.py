# economy/metabolic/__init__.py
#
# DOCS: docs/economy/metabolic/IMPLEMENTATION_Metabolic_Economy.md
#
# Public API for the metabolic economy formula library.
# Pure functions -- no blockchain, no graph, no I/O.

from .progressive_pricing_formula import (
    compute_progressive_price,
    compute_utility_discount,
    compute_wealth_ratio,
)
from .progressive_demurrage_formula import (
    compute_daily_demurrage,
    compute_effective_rate,
    apply_demurrage_batch,
)
from .anti_sybil_phantom_balance_tracker import (
    track_outflow,
    process_repatriation,
    compute_total_balance,
    is_roundtrip_profitable,
)
from .batch_settlement_reward_calculator import (
    compute_action_reward,
    compute_epoch_rewards,
    apply_supply_adjustment,
    assemble_settlement_batch,
)
from .bilateral_bond_equilibrium_formula import (
    compute_bond_transfer,
    compute_batch_equilibrium,
    estimate_convergence_days,
)
from .ubc_proximity_redistribution_formula import (
    compute_redistribution,
    compute_actor_weights,
    compute_redistribution_shares,
)
from .metabolic_types import (
    PricingContext,
    DemurrageContext,
    DemurrageResult,
    RepatriationResult,
    SettlementAction,
    SettlementBatch,
    BondEquilibriumContext,
    BondEquilibriumResult,
    SpacePresence,
    UBCShare,
)

__all__ = [
    # Formula 1: Progressive Pricing
    "compute_progressive_price",
    "compute_utility_discount",
    "compute_wealth_ratio",
    "PricingContext",
    # Formula 2: Progressive Demurrage
    "compute_daily_demurrage",
    "compute_effective_rate",
    "apply_demurrage_batch",
    "DemurrageContext",
    "DemurrageResult",
    # Formula 3: Anti-Sybil
    "track_outflow",
    "process_repatriation",
    "compute_total_balance",
    "is_roundtrip_profitable",
    "RepatriationResult",
    # Formula 4: Batch Settlement
    "compute_action_reward",
    "compute_epoch_rewards",
    "apply_supply_adjustment",
    "assemble_settlement_batch",
    "SettlementAction",
    "SettlementBatch",
    # Formula 5: Bond Equilibrium
    "compute_bond_transfer",
    "compute_batch_equilibrium",
    "estimate_convergence_days",
    "BondEquilibriumContext",
    "BondEquilibriumResult",
    # Formula 6: UBC Redistribution
    "compute_redistribution",
    "compute_actor_weights",
    "compute_redistribution_shares",
    "SpacePresence",
    "UBCShare",
]
