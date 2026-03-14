# economy/metabolic/metabolic_constants.py
#
# DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md (Constants Summary)
#
# Single source of truth for all tunable metabolic economy constants.
# Every formula module imports from here. All constants are DESIGNING status
# and will be calibrated via simulation.
#
# Env-override pattern: same as economy/token/constants.py -- each constant
# can be overridden via environment variable prefixed with MIND_METABOLIC_.

from __future__ import annotations

import os


def _env_float(name: str, default: float) -> float:
    """Read a float from environment, falling back to *default*."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (ValueError, TypeError):
        return default


def _env_int(name: str, default: int) -> int:
    """Read an int from environment, falling back to *default*."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


# =============================================================================
# Formula 1: Progressive Pricing
# P(i, S) = C_base * e^(-k * U_S) * max(WEALTH_RATIO_FLOOR, W_i / W_median)
# =============================================================================

UTILITY_DISCOUNT_RATE: float = _env_float("MIND_METABOLIC_UTILITY_DISCOUNT_RATE", 0.01)
"""k -- utility discount rate, per unit U_S. DESIGNING."""

WEALTH_RATIO_FLOOR: float = _env_float("MIND_METABOLIC_WEALTH_RATIO_FLOOR", 0.1)
"""Minimum wealth ratio (10%). Prevents free services for empty wallets."""


# =============================================================================
# Formula 2: Progressive Demurrage
# T_i = W_total * TAU_BASE * log10(1 + W_total)
# =============================================================================

TAU_BASE: float = _env_float("MIND_METABOLIC_TAU_BASE", 0.001)
"""Base daily tax rate (0.1%/day). DESIGNING -- may need reduction after simulation."""

DUST_THRESHOLD: float = _env_float("MIND_METABOLIC_DUST_THRESHOLD", 1.0)
"""Skip accounts below this balance ($MIND)."""


# =============================================================================
# Formula 3: Anti-Sybil Auto-Repatriation
# Friction = amount * FRICTION_TAX_RATE (burned)
# =============================================================================

FRICTION_TAX_RATE: float = _env_float("MIND_METABOLIC_FRICTION_TAX_RATE", 0.05)
"""5% repatriation friction. Permanently burned on repatriation."""


# =============================================================================
# Formula 4: Batch Settlement
# reward = limbic_delta * trust(Y->X) * weight(thing) * SETTLEMENT_RATE
# =============================================================================

SETTLEMENT_RATE: float = _env_float("MIND_METABOLIC_SETTLEMENT_RATE", 10.0)
"""$MIND per unit limbic_delta. DESIGNING."""

MAX_ACTION_REWARD: float = _env_float("MIND_METABOLIC_MAX_ACTION_REWARD", 1000.0)
"""Cap per single action reward ($MIND)."""

MAX_EPOCH_REWARD: float = _env_float("MIND_METABOLIC_MAX_EPOCH_REWARD", 5000.0)
"""Cap per actor per 6-hour settlement epoch ($MIND)."""

SETTLEMENT_FREQUENCY_HOURS: int = _env_int("MIND_METABOLIC_SETTLEMENT_FREQUENCY_HOURS", 6)
"""Hours between settlement epochs."""

MAX_SUPPLY_REDUCTION: float = _env_float("MIND_METABOLIC_MAX_SUPPLY_REDUCTION", 0.5)
"""Maximum settlement reduction when supply exceeds target (50%)."""


# =============================================================================
# Formula 5: Bilateral Bond Equilibrium
# delta_transfer = LAMBDA_RATE * (W_human - W_ai)
# =============================================================================

LAMBDA_RATE: float = _env_float("MIND_METABOLIC_LAMBDA_RATE", 0.05)
"""Daily smoothing rate. Half-life = ln(2) / lambda ~ 14 days."""

MIN_TRANSFER_THRESHOLD: float = _env_float("MIND_METABOLIC_MIN_TRANSFER_THRESHOLD", 1.0)
"""Skip dust transfers below this amount ($MIND)."""

MAX_DAILY_BOND_TRANSFER: float = _env_float("MIND_METABOLIC_MAX_DAILY_BOND_TRANSFER", 500.0)
"""Cap daily bond equilibrium transfer ($MIND)."""

BOND_MATURATION_DAYS: int = _env_int("MIND_METABOLIC_BOND_MATURATION_DAYS", 180)
"""Days before bond equilibrium activates (6 months)."""


# =============================================================================
# Formula 6: UBC Topological Activity Redistribution
# activity = log10(1 + Σ(moment weights))
# weight = activity × (num_actors - 1)
# =============================================================================

MIN_COPRESENCE_ACTORS: int = _env_int("MIND_METABOLIC_MIN_COPRESENCE_ACTORS", 3)
"""Minimum actors in a Space for redistribution to apply (>=3)."""


# =============================================================================
# Cross-cutting
# =============================================================================

EPSILON: float = 1e-9
"""Floating-point comparison tolerance."""
