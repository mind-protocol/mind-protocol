# tests/economy/test_token_supply_calculations.py
#
# Tests for $MIND token supply calculations
# DOCS: docs/economy/token/VALIDATION_Token.md

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from economy.token.token_supply_target_calculator import (
    SupplyMetrics,
    calculate_target_supply,
    calculate_supply_adjustment,
    calculate_per_citizen_target,
    calculate_health_indicators,
    SCENARIO_BOOTSTRAP,
    SCENARIO_MONTH_1,
    SCENARIO_MATURE,
)


class TestTargetSupplyCalculation:
    """Tests for target supply formula."""

    def test_target_supply_formula(self):
        """Target supply should follow the formula correctly."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
        )

        target = calculate_target_supply(metrics)

        # Manual calculation:
        # citizens: 50 * 50,000 = 2,500,000
        # bonds: 100,000 * 0.1 = 10,000
        # utility: 10,000 * 10 = 100,000
        # burns: -1,000
        # Total: 2,609,000
        expected = 2_500_000 + 10_000 + 100_000 - 1_000
        assert target == expected

    def test_target_supply_zero_citizens(self):
        """Zero citizens should give zero target."""
        metrics = SupplyMetrics(
            active_citizens=0,
            total_bonds=0,
            monthly_utility=0,
            monthly_burns=0,
        )

        target = calculate_target_supply(metrics)
        assert target == 0

    def test_target_supply_floor_at_zero(self):
        """Target supply should never go negative."""
        metrics = SupplyMetrics(
            active_citizens=1,
            total_bonds=0,
            monthly_utility=0,
            monthly_burns=1_000_000,  # Huge burns
        )

        target = calculate_target_supply(metrics)
        assert target >= 0

    def test_scenario_bootstrap(self):
        """Bootstrap scenario (21 citizens) should calculate correctly."""
        target = calculate_target_supply(SCENARIO_BOOTSTRAP)

        # 21 * 50,000 = 1,050,000
        assert target == 1_050_000

    def test_scenario_month_1(self):
        """Month 1 scenario should calculate correctly."""
        target = calculate_target_supply(SCENARIO_MONTH_1)

        # 50 * 50,000 + 100,000 * 0.1 + 10,000 * 10 - 1,000
        # = 2,500,000 + 10,000 + 100,000 - 1,000
        # = 2,609,000
        expected = 2_500_000 + 10_000 + 100_000 - 1_000
        assert target == expected


class TestSupplyAdjustment:
    """Tests for supply adjustment recommendations."""

    def test_adjustment_hold_when_close(self):
        """Should recommend HOLD when within 1% of target."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_609_000,  # Exactly on target
        )

        adjustment = calculate_supply_adjustment(metrics)

        assert adjustment["action"] == "HOLD"
        assert abs(adjustment["delta_percentage"]) < 1.0

    def test_adjustment_mint_when_under(self):
        """Should recommend MINT when significantly below target."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_000_000,  # Below target
        )

        adjustment = calculate_supply_adjustment(metrics)

        assert adjustment["action"] == "MINT"
        assert adjustment["delta"] > 0

    def test_adjustment_allow_burn_when_over(self):
        """Should recommend ALLOW_BURN when significantly above target."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=3_000_000,  # Above target
        )

        adjustment = calculate_supply_adjustment(metrics)

        assert adjustment["action"] == "ALLOW_BURN"
        assert adjustment["delta"] < 0

    def test_adjustment_includes_components(self):
        """Adjustment should include component breakdown."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_500_000,
        )

        adjustment = calculate_supply_adjustment(metrics)

        assert "components" in adjustment
        assert adjustment["components"]["citizen_base"] == 50 * 50_000
        assert adjustment["components"]["bond_supply"] == 100_000 * 0.1
        assert adjustment["components"]["utility_supply"] == 10_000 * 10
        assert adjustment["components"]["burn_offset"] == 1_000


class TestPerCitizenTarget:
    """Tests for per-citizen target calculation."""

    def test_per_citizen_with_citizens(self):
        """Per-citizen target should divide correctly."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
        )

        per_citizen = calculate_per_citizen_target(metrics)

        target = calculate_target_supply(metrics)
        expected = target / 50
        assert per_citizen == expected

    def test_per_citizen_zero_citizens(self):
        """Per-citizen with zero citizens should be zero."""
        metrics = SupplyMetrics(
            active_citizens=0,
        )

        per_citizen = calculate_per_citizen_target(metrics)
        assert per_citizen == 0


class TestHealthIndicators:
    """Tests for supply health indicators."""

    def test_health_healthy_ratio(self):
        """Supply ratio near 1.0 should be HEALTHY."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_609_000,  # Exactly on target
        )

        health = calculate_health_indicators(metrics)

        assert health["supply_health"] == "HEALTHY"
        assert 0.9 <= health["supply_ratio"] <= 1.1

    def test_health_under_ratio(self):
        """Supply ratio < 0.9 should be UNDER."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_000_000,  # Below target
        )

        health = calculate_health_indicators(metrics)

        assert health["supply_health"] == "UNDER"
        assert health["supply_ratio"] < 0.9

    def test_health_over_ratio(self):
        """Supply ratio > 1.1 should be OVER."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=3_500_000,  # Well above target
        )

        health = calculate_health_indicators(metrics)

        assert health["supply_health"] == "OVER"
        assert health["supply_ratio"] > 1.1

    def test_health_includes_rates(self):
        """Health should include various rate indicators."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_citizens=60,
            total_bonds=100_000,
            monthly_utility=10_000,
            monthly_burns=1_000,
            current_supply=2_609_000,
        )

        health = calculate_health_indicators(metrics)

        assert "burn_rate_monthly" in health
        assert "bond_coverage" in health
        assert "citizen_activity_ratio" in health

    def test_activity_ratio(self):
        """Activity ratio should be active/total."""
        metrics = SupplyMetrics(
            active_citizens=50,
            total_citizens=100,
            current_supply=1_000_000,
        )

        health = calculate_health_indicators(metrics)

        assert health["citizen_activity_ratio"] == 0.5


class TestSupplyMetricsDataclass:
    """Tests for SupplyMetrics dataclass."""

    def test_default_values(self):
        """Defaults should be zero."""
        metrics = SupplyMetrics()

        assert metrics.active_citizens == 0
        assert metrics.total_bonds == 0
        assert metrics.monthly_utility == 0
        assert metrics.monthly_burns == 0
        assert metrics.current_supply == 0

    def test_all_fields_settable(self):
        """All fields should be settable."""
        metrics = SupplyMetrics(
            active_citizens=100,
            total_citizens=120,
            total_bonds=500_000,
            active_bonds=150,
            monthly_utility=50_000,
            monthly_utility_ema=45_000,
            monthly_burns=5_000,
            monthly_burns_ema=4_500,
            current_supply=10_000_000,
            active_orgs=10,
            total_orgs=12,
        )

        assert metrics.active_citizens == 100
        assert metrics.total_orgs == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
