# economy/metabolic/metabolic_types.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md
#
# Shared data structures used across all metabolic economy formulas.
# Pure dataclasses -- no I/O, no blockchain, no graph dependencies.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Formula 1: Progressive Pricing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PricingContext:
    """Input context for computing progressive service price.

    Mathematical formula:
        P(i, S) = C_base * e^(-k * U_S) * max(0.1, W_i / W_median)
    """

    c_base: float
    """Raw compute cost of the service ($MIND)."""

    u_s: float
    """Utility weight of service S -- from L1 Law 6 graph consolidation.
    Range: [0, +inf). Higher = more useful."""

    w_i: float
    """Wallet balance of requester i ($MIND)."""

    w_median: float
    """Network median wallet balance, recomputed daily at 00:00 UTC ($MIND)."""

    k: float = 0.01
    """Utility discount rate."""


# ---------------------------------------------------------------------------
# Formula 2: Progressive Demurrage
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DemurrageContext:
    """Input context for computing progressive daily demurrage.

    Mathematical formula:
        T_i = W_total * tau_base * log10(1 + W_total)
    """

    w_total: float
    """Total balance including off-registry phantom balance ($MIND)."""

    w_onchain: float
    """On-chain wallet balance ($MIND)."""

    w_offregistry: float
    """Phantom balance from off-registry outflows ($MIND)."""

    tau_base: float = 0.001
    """Base daily tax rate (0.1%/day)."""

    actor_id: str = ""
    """Actor identifier for result tracking."""


@dataclass(frozen=True)
class DemurrageResult:
    """Output of a single demurrage computation."""

    actor_id: str
    w_total: float
    w_offregistry: float
    tax_amount: float
    effective_rate: float
    """Effective daily rate = tax_amount / w_total (0 if w_total == 0)."""


# ---------------------------------------------------------------------------
# Formula 3: Anti-Sybil Auto-Repatriation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RepatriationResult:
    """Output of a repatriation computation."""

    actor_id: str
    gross_amount: float
    """Original amount being repatriated."""

    friction_penalty: float
    """5% burned as friction tax."""

    net_amount: float
    """Amount actually credited (gross - friction)."""

    new_offregistry_balance: float
    """Updated phantom balance after repatriation."""


# ---------------------------------------------------------------------------
# Formula 4: Batch Settlement
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SettlementAction:
    """A single value-creating action to be settled.

    Mathematical formula:
        reward = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate
    """

    action_id: str
    actor_x: str
    """Actor who performed the action (reward recipient)."""

    actor_y: str
    """Actor who experienced the limbic shift."""

    limbic_delta: float
    """Measured limbic shift in actor Y (from L1 Law 6).
    limbic_delta = delta_satisfaction + delta_achievement
                 - delta_frustration - delta_anxiety"""

    trust_y_to_x: float
    """Trust score from Y toward X (from L1 Law 18). Range: [0, 1]."""

    weight_thing: float
    """Weight of the thing/tool/service used. Range: [0, 1]."""


@dataclass
class SettlementBatch:
    """A batch of settlement actions for a 6-hour epoch."""

    batch_id: str
    epoch_start: datetime
    epoch_end: datetime
    actions: List[SettlementAction]
    rewards: Dict[str, float] = field(default_factory=dict)
    """actor_id -> total_reward for this epoch."""

    total_minted: float = 0.0
    supply_reduction: float = 0.0
    """Reduction factor applied due to supply health check (0.0 = no reduction)."""

    status: str = "PENDING"
    """PENDING | SUBMITTED | CONFIRMED | FAILED"""

    solana_tx_signature: Optional[str] = None


# ---------------------------------------------------------------------------
# Formula 5: Bilateral Bond Equilibrium
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BondEquilibriumContext:
    """Input context for computing daily bond equilibrium transfer.

    Mathematical formula:
        delta_transfer = lambda * (W_human - W_ai)
    """

    bond_id: str
    human_wallet: str
    ai_wallet: str
    w_human: float
    """Human partner wallet balance ($MIND)."""

    w_ai: float
    """AI partner wallet balance ($MIND)."""

    lambda_rate: float = 0.05
    """Daily smoothing rate."""

    maturation_complete: bool = True
    """Whether the 180-day maturation period is complete."""


@dataclass(frozen=True)
class BondEquilibriumResult:
    """Output of a bond equilibrium computation."""

    bond_id: str
    delta: float
    """Positive = human -> AI, negative = AI -> human, 0 = no transfer."""

    w_human_after: float
    w_ai_after: float


# ---------------------------------------------------------------------------
# Formula 6: UBC Proximity Redistribution
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SpacePresence:
    """Activity data for a single Space on a given day.

    Each actor's value is the sum of weights of all moment nodes they
    created in this Space today. Weight comes from Law 6 consolidation:
    moments that generated real utility (positive limbic delta in others)
    earn weight; spam/noise stays at near-zero weight.

    This replaces the old hours_present model which was vulnerable to
    passive farming (leave tabs open → mine UBC without contributing).
    """

    space_id: str
    actors: Dict[str, float]
    """actor_id -> sum of moment weights created in this Space today."""


@dataclass(frozen=True)
class UBCShare:
    """Per-actor share of the UBC redistribution pool."""

    actor_id: str
    share: float
    """Proportion of pool received [0, 1]."""

    amount: float
    """$MIND received."""
