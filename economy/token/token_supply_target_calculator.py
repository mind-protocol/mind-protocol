# economy/token/token_supply_target_calculator.py
#
# DOCS: docs/economy/token/ALGORITHM_Token.md
#
# Supply target calculator for $MIND breathing supply mechanism.
# Supply is not fixed — it's a function of ecosystem health.
#
# Formula (from tokenomics v1.1):
#   target_supply = (active_citizens * 50,000)
#                 + (total_bonds * 0.1)
#                 + (monthly_utility * 10)
#                 - monthly_burns
#
# The system breathes: mints when below target, burns happen through friction.

from dataclasses import dataclass
from typing import Optional


@dataclass
class SupplyMetrics:
    """
    Input metrics for supply target calculation.

    All values should be current/recent measurements.
    """

    # Citizen metrics
    active_citizens: int = 0  # Citizens with activity in last 30 days
    total_citizens: int = 0   # All registered citizens

    # Bond metrics
    total_bonds: float = 0.0        # Total $MIND staked in bonds
    active_bonds: int = 0           # Number of active bonds

    # Utility metrics
    monthly_utility: float = 0.0    # Total utility delivered this month
    monthly_utility_ema: float = 0.0  # EMA of monthly utility

    # Burn metrics
    monthly_burns: float = 0.0      # Total burns this month
    monthly_burns_ema: float = 0.0  # EMA of monthly burns

    # Current supply
    current_supply: float = 0.0     # Actual circulating supply

    # Organization metrics
    active_orgs: int = 0            # Active organizations
    total_orgs: int = 0             # All registered organizations


def calculate_target_supply(metrics: SupplyMetrics) -> float:
    """
    Calculate target supply based on ecosystem metrics.

    Formula:
        target = (active_citizens * 50_000)
               + (total_bonds * 0.1)
               + (monthly_utility * 10)
               - monthly_burns

    This represents the "healthy" supply level for current ecosystem state.

    Args:
        metrics: Current ecosystem metrics

    Returns:
        Target supply in $MIND tokens
    """
    # Base supply from active citizens
    citizen_base = metrics.active_citizens * 50_000

    # Bond-justified supply (more relationships = more supply justified)
    bond_supply = metrics.total_bonds * 0.1

    # Utility-earned supply (value creation justifies supply)
    utility_supply = metrics.monthly_utility * 10

    # Natural deflation from burns
    burn_offset = metrics.monthly_burns

    target = citizen_base + bond_supply + utility_supply - burn_offset

    # Floor at 0
    return max(0, target)


def calculate_supply_adjustment(metrics: SupplyMetrics) -> dict:
    """
    Calculate recommended supply adjustment.

    Compares current supply to target and recommends action.

    Args:
        metrics: Current ecosystem metrics

    Returns:
        Dict with adjustment recommendation
    """
    target = calculate_target_supply(metrics)
    current = metrics.current_supply
    delta = target - current

    # Calculate percentage difference
    if current > 0:
        delta_percentage = (delta / current) * 100
    else:
        delta_percentage = 100.0 if target > 0 else 0.0

    # Determine action
    if abs(delta_percentage) < 1.0:
        action = "HOLD"
        reason = "Supply within 1% of target"
    elif delta > 0:
        action = "MINT"
        reason = f"Supply {abs(delta_percentage):.1f}% below target"
    else:
        action = "ALLOW_BURN"
        reason = f"Supply {abs(delta_percentage):.1f}% above target"

    return {
        "action": action,
        "target_supply": target,
        "current_supply": current,
        "delta": delta,
        "delta_percentage": delta_percentage,
        "reason": reason,
        "components": {
            "citizen_base": metrics.active_citizens * 50_000,
            "bond_supply": metrics.total_bonds * 0.1,
            "utility_supply": metrics.monthly_utility * 10,
            "burn_offset": metrics.monthly_burns,
        },
    }


def calculate_per_citizen_target(metrics: SupplyMetrics) -> float:
    """
    Calculate target supply per active citizen.

    Useful for understanding individual economic capacity.

    Args:
        metrics: Current ecosystem metrics

    Returns:
        Target tokens per citizen
    """
    if metrics.active_citizens == 0:
        return 0.0

    target = calculate_target_supply(metrics)
    return target / metrics.active_citizens


def calculate_health_indicators(metrics: SupplyMetrics) -> dict:
    """
    Calculate supply health indicators.

    Args:
        metrics: Current ecosystem metrics

    Returns:
        Dict with health indicators
    """
    target = calculate_target_supply(metrics)
    current = metrics.current_supply

    # Supply ratio (1.0 = perfectly on target)
    if target > 0:
        supply_ratio = current / target
    else:
        supply_ratio = 1.0 if current == 0 else float('inf')

    # Velocity indicators
    if current > 0:
        burn_rate = metrics.monthly_burns / current
        utility_rate = metrics.monthly_utility / current
    else:
        burn_rate = 0.0
        utility_rate = 0.0

    # Bond coverage (how much of supply is bonded)
    if current > 0:
        bond_coverage = metrics.total_bonds / current
    else:
        bond_coverage = 0.0

    # Activity ratio
    if metrics.total_citizens > 0:
        activity_ratio = metrics.active_citizens / metrics.total_citizens
    else:
        activity_ratio = 0.0

    return {
        "supply_ratio": supply_ratio,
        "supply_health": (
            "HEALTHY" if 0.9 <= supply_ratio <= 1.1
            else "UNDER" if supply_ratio < 0.9
            else "OVER"
        ),
        "burn_rate_monthly": burn_rate,
        "utility_rate_monthly": utility_rate,
        "bond_coverage": bond_coverage,
        "citizen_activity_ratio": activity_ratio,
        "metrics_summary": {
            "active_citizens": metrics.active_citizens,
            "total_bonds": metrics.total_bonds,
            "monthly_utility": metrics.monthly_utility,
            "monthly_burns": metrics.monthly_burns,
            "current_supply": current,
            "target_supply": target,
        },
    }


# Pre-configured scenarios for testing
SCENARIO_BOOTSTRAP = SupplyMetrics(
    active_citizens=21,  # Current citizen count
    total_citizens=21,
    total_bonds=0,
    monthly_utility=0,
    monthly_burns=0,
    current_supply=0,  # Before initial mint
)

SCENARIO_MONTH_1 = SupplyMetrics(
    active_citizens=50,
    total_citizens=55,
    total_bonds=100_000,  # Some early bonds
    monthly_utility=10_000,
    monthly_burns=1_000,
    current_supply=500_000,
)

SCENARIO_MATURE = SupplyMetrics(
    active_citizens=1000,
    total_citizens=1200,
    total_bonds=10_000_000,
    monthly_utility=500_000,
    monthly_burns=100_000,
    current_supply=50_000_000,
)
