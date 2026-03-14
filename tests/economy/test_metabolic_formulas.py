# tests/economy/test_metabolic_formulas.py
#
# DOCS: docs/economy/metabolic/VALIDATION_Metabolic_Economy.md
#
# Comprehensive tests for all 6 metabolic economy formulas and all 27 invariants.
# Tests are grouped by formula and by invariant ID for traceability.

from __future__ import annotations

import math
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List

import pytest

# Ensure the repo root is on the path so we can import economy.metabolic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from economy.metabolic.metabolic_constants import (
    DUST_THRESHOLD,
    EPSILON,
    FRICTION_TAX_RATE,
    LAMBDA_RATE,
    MAX_ACTION_REWARD,
    MAX_DAILY_BOND_TRANSFER,
    MAX_EPOCH_REWARD,
    MAX_SUPPLY_REDUCTION,
    MIN_COPRESENCE_ACTORS,
    MIN_TRANSFER_THRESHOLD,
    SETTLEMENT_RATE,
    TAU_BASE,
    UTILITY_DISCOUNT_RATE,
    WEALTH_RATIO_FLOOR,
)
from economy.metabolic.metabolic_types import (
    BondEquilibriumContext,
    BondEquilibriumResult,
    DemurrageContext,
    DemurrageResult,
    PricingContext,
    RepatriationResult,
    SettlementAction,
    SettlementBatch,
    SpacePresence,
    UBCShare,
)
from economy.metabolic.progressive_pricing_formula import (
    compute_progressive_price,
    compute_utility_discount,
    compute_wealth_ratio,
)
from economy.metabolic.progressive_demurrage_formula import (
    apply_demurrage_batch,
    compute_daily_demurrage,
    compute_effective_rate,
)
from economy.metabolic.anti_sybil_phantom_balance_tracker import (
    compute_total_balance,
    is_roundtrip_profitable,
    process_repatriation,
    track_outflow,
)
from economy.metabolic.batch_settlement_reward_calculator import (
    apply_supply_adjustment,
    assemble_settlement_batch,
    compute_action_reward,
    compute_epoch_rewards,
)
from economy.metabolic.bilateral_bond_equilibrium_formula import (
    compute_batch_equilibrium,
    compute_bond_transfer,
    estimate_convergence_days,
)
from economy.metabolic.ubc_proximity_redistribution_formula import (
    compute_actor_weights,
    compute_redistribution,
    compute_redistribution_shares,
)


# ===========================================================================
# Formula 1: Progressive Pricing -- INV-P1 through INV-P4
# ===========================================================================


class TestProgressivePricingFormula:
    """Tests for Formula 1: P(i,S) = C_base * e^(-k*U_S) * max(0.1, W_i/W_median)"""

    # --- INV-P1: Price Non-Negativity ---

    def test_inv_p1_price_non_negative_basic(self):
        """INV-P1: P(i,S) >= 0 for all valid inputs."""
        ctx = PricingContext(c_base=100, u_s=50, w_i=5000, w_median=10000)
        price = compute_progressive_price(ctx)
        assert price >= 0

    def test_inv_p1_price_positive_when_c_base_positive(self):
        """INV-P1: P(i,S) > 0 when C_base > 0."""
        ctx = PricingContext(c_base=100, u_s=0, w_i=10000, w_median=10000)
        price = compute_progressive_price(ctx)
        assert price > 0

    def test_inv_p1_price_zero_when_c_base_zero(self):
        """P(i,S) = 0 when C_base = 0."""
        ctx = PricingContext(c_base=0, u_s=50, w_i=5000, w_median=10000)
        price = compute_progressive_price(ctx)
        assert price == 0.0

    def test_inv_p1_negative_c_base_raises(self):
        """Negative C_base raises ValueError."""
        ctx = PricingContext(c_base=-10, u_s=0, w_i=1000, w_median=10000)
        with pytest.raises(ValueError, match="c_base"):
            compute_progressive_price(ctx)

    # --- INV-P2: Utility Discount Bounded ---

    def test_inv_p2_discount_at_zero_utility(self):
        """INV-P2: utility_discount == 1.0 when U_S == 0."""
        assert compute_utility_discount(0.0) == 1.0

    def test_inv_p2_discount_bounded_0_to_1(self):
        """INV-P2: 0 < utility_discount <= 1.0 for all U_S >= 0."""
        for u_s in [0, 1, 10, 50, 100, 200, 500, 1000, 10000]:
            discount = compute_utility_discount(float(u_s))
            assert 0 < discount <= 1.0, f"Failed for U_S={u_s}: {discount}"

    def test_inv_p2_discount_monotonically_decreasing(self):
        """INV-P2: utility_discount is monotonically decreasing in U_S."""
        prev = compute_utility_discount(0.0)
        for u_s in range(1, 501):
            current = compute_utility_discount(float(u_s))
            assert current < prev, f"Not decreasing at U_S={u_s}"
            prev = current

    def test_inv_p2_discount_approaches_zero(self):
        """INV-P2: utility_discount approaches 0 as U_S -> infinity."""
        discount = compute_utility_discount(100000.0)
        assert discount < 1e-100

    def test_inv_p2_negative_u_s_raises(self):
        """Negative U_S raises ValueError."""
        with pytest.raises(ValueError, match="u_s"):
            compute_utility_discount(-1.0)

    def test_inv_p2_negative_k_raises(self):
        """Negative k raises ValueError."""
        with pytest.raises(ValueError, match="k"):
            compute_utility_discount(10.0, k=-0.01)

    # --- INV-P3: Wealth Ratio Floor ---

    def test_inv_p3_floor_applied_when_ratio_below(self):
        """INV-P3: wealth_ratio == 0.1 when W_i/W_median < 0.1."""
        # 500 / 10000 = 0.05 < 0.1 -> floor
        assert compute_wealth_ratio(500, 10000) == WEALTH_RATIO_FLOOR

    def test_inv_p3_floor_not_applied_when_ratio_above(self):
        """INV-P3: wealth_ratio == W_i/W_median when >= 0.1."""
        ratio = compute_wealth_ratio(5000, 10000)
        assert ratio == 0.5

    def test_inv_p3_exact_at_floor(self):
        """INV-P3: wealth_ratio == 0.1 when W_i/W_median == 0.1."""
        ratio = compute_wealth_ratio(1000, 10000)
        assert ratio == WEALTH_RATIO_FLOOR

    def test_inv_p3_zero_balance_gets_floor(self):
        """Zero-balance wallet gets the floor ratio."""
        ratio = compute_wealth_ratio(0, 10000)
        assert ratio == WEALTH_RATIO_FLOOR

    def test_inv_p3_wealthy_actor_no_cap(self):
        """No upper cap on wealth ratio -- wealthy actors subsidize."""
        ratio = compute_wealth_ratio(50000, 10000)
        assert ratio == 5.0

    def test_inv_p3_zero_median_raises(self):
        """Zero median raises ValueError."""
        with pytest.raises(ValueError, match="w_median"):
            compute_wealth_ratio(1000, 0)

    def test_inv_p3_negative_w_i_raises(self):
        """Negative w_i raises ValueError."""
        with pytest.raises(ValueError, match="w_i"):
            compute_wealth_ratio(-100, 10000)

    # --- INV-P4: Monotonicity ---

    def test_inv_p4_price_increases_with_wealth(self):
        """INV-P4: price increases with requester wealth (above floor)."""
        ctx1 = PricingContext(c_base=100, u_s=50, w_i=5000, w_median=10000)
        ctx2 = PricingContext(c_base=100, u_s=50, w_i=20000, w_median=10000)
        assert compute_progressive_price(ctx2) > compute_progressive_price(ctx1)

    def test_inv_p4_price_decreases_with_utility(self):
        """INV-P4: price decreases with service utility."""
        ctx_low = PricingContext(c_base=100, u_s=10, w_i=10000, w_median=10000)
        ctx_high = PricingContext(c_base=100, u_s=100, w_i=10000, w_median=10000)
        assert compute_progressive_price(ctx_high) < compute_progressive_price(ctx_low)

    # --- Worked example from ALGORITHM doc ---

    def test_worked_example_aria(self):
        """Verify the worked example from ALGORITHM doc."""
        ctx = PricingContext(c_base=100, u_s=150, w_i=3000, w_median=10000, k=0.01)
        price = compute_progressive_price(ctx)
        expected = 100 * math.exp(-0.01 * 150) * 0.3  # ~6.69
        assert abs(price - expected) < 0.01

    def test_worked_example_wealthy_actor(self):
        """Wealthy actor pays much more for same service."""
        ctx = PricingContext(c_base=100, u_s=150, w_i=50000, w_median=10000, k=0.01)
        price = compute_progressive_price(ctx)
        expected = 100 * math.exp(-1.5) * 5.0  # ~111.5
        assert abs(price - expected) < 0.1


# ===========================================================================
# Formula 2: Progressive Demurrage -- INV-D1 through INV-D4
# ===========================================================================


class TestProgressiveDemurrageFormula:
    """Tests for Formula 2: T_i = W_total * tau_base * log10(1 + W_total)"""

    # --- INV-D1: Tax Never Exceeds Balance ---

    def test_inv_d1_tax_clamped_to_balance(self):
        """INV-D1: actual tax <= on-chain balance."""
        # W_total high (including off-registry) but W_onchain low
        ctx = DemurrageContext(
            w_total=100000, w_onchain=10, w_offregistry=99990,
            tau_base=0.001, actor_id="test"
        )
        result = compute_daily_demurrage(ctx)
        assert result.tax_amount <= ctx.w_onchain

    def test_inv_d1_balance_never_negative(self):
        """INV-D1: wallet balance after tax >= 0."""
        ctx = DemurrageContext(
            w_total=50000, w_onchain=100, w_offregistry=49900,
            tau_base=0.001, actor_id="test"
        )
        result = compute_daily_demurrage(ctx)
        remaining = ctx.w_onchain - result.tax_amount
        assert remaining >= 0

    # --- INV-D2: Progressive Rate Ordering ---

    def test_inv_d2_larger_balance_higher_rate(self):
        """INV-D2: effective rate increases with balance."""
        rate_small = compute_effective_rate(1000)
        rate_large = compute_effective_rate(10000)
        assert rate_large > rate_small

    def test_inv_d2_progressive_across_range(self):
        """INV-D2: rate ordering holds across the full range."""
        prev_rate = 0.0
        for w in [10, 100, 1000, 10000, 100000, 1000000]:
            rate = compute_effective_rate(float(w))
            assert rate > prev_rate, f"Rate not progressive at W={w}"
            prev_rate = rate

    # --- INV-D3: Logarithmic Growth Bound ---

    def test_inv_d3_10x_wealth_never_doubles_rate(self):
        """INV-D3: 10x increase in wealth never doubles the effective rate."""
        for w in [100, 1000, 10000, 100000]:
            rate_w = compute_effective_rate(float(w))
            rate_10w = compute_effective_rate(float(w * 10))
            ratio = rate_10w / rate_w
            assert ratio < 2, f"10x wealth at W={w} gives rate ratio {ratio}"

    # --- INV-D4: Universal Application ---

    def test_inv_d4_dust_accounts_skipped(self):
        """Dust accounts below DUST_THRESHOLD are skipped."""
        ctx = DemurrageContext(
            w_total=0.5, w_onchain=0.5, w_offregistry=0,
            tau_base=0.001, actor_id="dust"
        )
        result = compute_daily_demurrage(ctx)
        assert result.tax_amount == 0.0

    def test_inv_d4_above_dust_gets_taxed(self):
        """Accounts above DUST_THRESHOLD are taxed."""
        ctx = DemurrageContext(
            w_total=100, w_onchain=100, w_offregistry=0,
            tau_base=0.001, actor_id="normal"
        )
        result = compute_daily_demurrage(ctx)
        assert result.tax_amount > 0

    # --- Worked example from ALGORITHM doc ---

    def test_worked_example_demurrage_values(self):
        """Verify demurrage examples from ALGORITHM doc."""
        test_cases = [
            (100, 0.001, 100 * 0.001 * math.log10(101)),
            (1000, 0.001, 1000 * 0.001 * math.log10(1001)),
            (10000, 0.001, 10000 * 0.001 * math.log10(10001)),
        ]
        for w, tau, expected in test_cases:
            ctx = DemurrageContext(
                w_total=w, w_onchain=w, w_offregistry=0,
                tau_base=tau, actor_id="test"
            )
            result = compute_daily_demurrage(ctx)
            assert abs(result.tax_amount - expected) < 0.01, (
                f"W={w}: expected {expected:.3f}, got {result.tax_amount:.3f}"
            )

    # --- Batch ---

    def test_batch_total_equals_sum(self):
        """INV-SC2: total tax collected == sum of individual taxes."""
        contexts = [
            DemurrageContext(w_total=1000, w_onchain=1000, w_offregistry=0,
                            tau_base=0.001, actor_id=f"a{i}")
            for i in range(5)
        ]
        results, total = apply_demurrage_batch(contexts)
        assert abs(total - sum(r.tax_amount for r in results)) < EPSILON

    # --- Edge cases ---

    def test_zero_balance(self):
        """Zero balance produces zero tax."""
        ctx = DemurrageContext(
            w_total=0, w_onchain=0, w_offregistry=0,
            tau_base=0.001, actor_id="zero"
        )
        result = compute_daily_demurrage(ctx)
        assert result.tax_amount == 0.0

    def test_negative_w_total_raises(self):
        """Negative w_total raises ValueError."""
        ctx = DemurrageContext(
            w_total=-100, w_onchain=0, w_offregistry=0,
            tau_base=0.001, actor_id="neg"
        )
        with pytest.raises(ValueError, match="w_total"):
            compute_daily_demurrage(ctx)

    def test_effective_rate_zero_for_zero_balance(self):
        """Effective rate is 0 for zero balance."""
        assert compute_effective_rate(0.0) == 0.0

    def test_effective_rate_negative_tau_raises(self):
        """Negative tau_base raises ValueError."""
        with pytest.raises(ValueError, match="tau_base"):
            compute_effective_rate(100.0, tau_base=-0.001)


# ===========================================================================
# Formula 3: Anti-Sybil Auto-Repatriation -- INV-AS1 through INV-AS3
# ===========================================================================


class TestAntiSybilPhantomBalanceTracker:
    """Tests for Formula 3: off-registry tracking + repatriation friction."""

    # --- INV-AS1: Phantom Balance Tracking ---

    def test_inv_as1_total_balance_correct(self):
        """INV-AS1: W_total = W_onchain + W_offregistry."""
        assert compute_total_balance(5000, 3000) == 8000

    def test_inv_as1_offregistry_non_negative(self):
        """INV-AS1: W_offregistry >= 0."""
        with pytest.raises(ValueError):
            compute_total_balance(1000, -500)

    def test_inv_as1_total_gte_onchain(self):
        """INV-AS1: W_total >= W_onchain."""
        total = compute_total_balance(5000, 2000)
        assert total >= 5000

    def test_inv_as1_outflow_tracked_for_unregistered(self):
        """Outflow to unregistered address increases phantom balance."""
        new_balance, tracked = track_outflow(
            current_offregistry=1000, amount=500, is_l4_registered=False
        )
        assert tracked is True
        assert new_balance == 1500

    def test_inv_as1_outflow_not_tracked_for_registered(self):
        """Outflow to registered address does not change phantom balance."""
        new_balance, tracked = track_outflow(
            current_offregistry=1000, amount=500, is_l4_registered=True
        )
        assert tracked is False
        assert new_balance == 1000

    def test_inv_as1_outflow_invalid_amount_raises(self):
        """Zero or negative amount raises ValueError."""
        with pytest.raises(ValueError, match="amount"):
            track_outflow(current_offregistry=0, amount=0, is_l4_registered=False)
        with pytest.raises(ValueError, match="amount"):
            track_outflow(current_offregistry=0, amount=-10, is_l4_registered=False)

    # --- INV-AS2: Repatriation Friction Burn ---

    def test_inv_as2_friction_applied(self):
        """INV-AS2: friction = gross * 0.05, net = gross * 0.95."""
        result = process_repatriation(
            actor_id="test", gross_amount=1000,
            current_offregistry=1000, friction_rate=0.05
        )
        assert result.friction_penalty == 50.0
        assert result.net_amount == 950.0
        assert abs(result.net_amount - result.gross_amount * 0.95) < EPSILON

    def test_inv_as2_friction_positive(self):
        """INV-AS2: friction > 0 for any positive amount."""
        result = process_repatriation(
            actor_id="test", gross_amount=1.0,
            current_offregistry=1.0, friction_rate=0.05
        )
        assert result.friction_penalty > 0

    def test_inv_as2_offregistry_reduced(self):
        """Repatriation reduces phantom balance."""
        result = process_repatriation(
            actor_id="test", gross_amount=500,
            current_offregistry=1000
        )
        assert result.new_offregistry_balance == 500.0

    def test_inv_as2_offregistry_clamped_to_zero(self):
        """Phantom balance clamped to 0 if repatriation > off-registry."""
        result = process_repatriation(
            actor_id="test", gross_amount=2000,
            current_offregistry=1000
        )
        assert result.new_offregistry_balance == 0.0

    def test_inv_as2_invalid_amount_raises(self):
        """Non-positive gross amount raises ValueError."""
        with pytest.raises(ValueError, match="gross_amount"):
            process_repatriation("test", 0, 1000)
        with pytest.raises(ValueError, match="gross_amount"):
            process_repatriation("test", -100, 1000)

    def test_inv_as2_invalid_friction_rate_raises(self):
        """Friction rate outside [0, 1) raises ValueError."""
        with pytest.raises(ValueError, match="friction_rate"):
            process_repatriation("test", 100, 100, friction_rate=1.0)
        with pytest.raises(ValueError, match="friction_rate"):
            process_repatriation("test", 100, 100, friction_rate=-0.1)

    # --- INV-AS3: Round-Trip Net Loss ---

    def test_inv_as3_roundtrip_never_profitable(self):
        """INV-AS3: round-tripping always has positive cost."""
        for amount in [100, 1000, 10000, 100000]:
            for days in [0, 1, 7, 30, 365]:
                is_profitable, cost = is_roundtrip_profitable(amount, days)
                assert is_profitable is False
                assert cost > 0, f"Cost not positive for amount={amount}, days={days}"

    def test_inv_as3_roundtrip_cost_equals_friction(self):
        """Round-trip cost equals the friction penalty."""
        amount = 10000
        _, cost = is_roundtrip_profitable(amount, days_hidden=30)
        expected_friction = amount * FRICTION_TAX_RATE
        assert abs(cost - expected_friction) < EPSILON


# ===========================================================================
# Formula 4: Batch Settlement -- INV-S1 through INV-S4
# ===========================================================================


class TestBatchSettlementRewardCalculator:
    """Tests for Formula 4: reward = D * trust * weight * rate."""

    def _make_action(
        self,
        delta: float = 0.8,
        trust: float = 0.9,
        weight: float = 0.6,
        actor_x: str = "aria",
        actor_y: str = "nicolas",
    ) -> SettlementAction:
        return SettlementAction(
            action_id="a1", actor_x=actor_x, actor_y=actor_y,
            limbic_delta=delta, trust_y_to_x=trust, weight_thing=weight,
        )

    # --- INV-S1: Positive-Only Rewards ---

    def test_inv_s1_zero_delta_zero_reward(self):
        """INV-S1: limbic_delta <= 0 -> reward == 0."""
        action = self._make_action(delta=0.0)
        assert compute_action_reward(action) == 0.0

    def test_inv_s1_negative_delta_zero_reward(self):
        """INV-S1: negative limbic_delta -> reward == 0."""
        action = self._make_action(delta=-0.5)
        assert compute_action_reward(action) == 0.0

    def test_inv_s1_zero_trust_zero_reward(self):
        """INV-S1: trust == 0 -> reward == 0."""
        action = self._make_action(trust=0.0)
        assert compute_action_reward(action) == 0.0

    def test_inv_s1_zero_weight_zero_reward(self):
        """INV-S1: weight == 0 -> reward == 0."""
        action = self._make_action(weight=0.0)
        assert compute_action_reward(action) == 0.0

    def test_inv_s1_negative_trust_zero_reward(self):
        """INV-S1: negative trust -> reward == 0."""
        action = self._make_action(trust=-0.1)
        assert compute_action_reward(action) == 0.0

    def test_inv_s1_all_positive_produces_reward(self):
        """All positive factors produce a positive reward."""
        action = self._make_action(delta=0.8, trust=0.9, weight=0.6)
        reward = compute_action_reward(action)
        expected = 0.8 * 0.9 * 0.6 * SETTLEMENT_RATE
        assert abs(reward - expected) < 0.01

    # --- INV-S2: Reward Caps ---

    def test_inv_s2_per_action_cap(self):
        """INV-S2: per-action reward <= MAX_ACTION_REWARD."""
        action = self._make_action(delta=100.0, trust=1.0, weight=1.0)
        reward = compute_action_reward(action)
        assert reward <= MAX_ACTION_REWARD

    def test_inv_s2_per_epoch_cap(self):
        """INV-S2: per-actor per-epoch reward <= MAX_EPOCH_REWARD."""
        # 20 actions x 500 reward each = 10000, should be capped to 5000
        actions = [
            self._make_action(delta=5.0, trust=1.0, weight=1.0)
            for _ in range(20)
        ]
        rewards = compute_epoch_rewards(actions)
        assert rewards["aria"] <= MAX_EPOCH_REWARD

    def test_inv_s2_multiple_actors_capped_independently(self):
        """Each actor is capped independently."""
        actions = [
            self._make_action(delta=5.0, trust=1.0, weight=1.0, actor_x="a1"),
            self._make_action(delta=5.0, trust=1.0, weight=1.0, actor_x="a2"),
        ] * 20  # 40 actions, 20 per actor
        rewards = compute_epoch_rewards(actions)
        for actor_id, reward in rewards.items():
            assert reward <= MAX_EPOCH_REWARD

    # --- INV-S3: Supply Target Integration ---

    def test_inv_s3_no_reduction_when_normal(self):
        """No reduction when supply is normal."""
        rewards = {"a1": 100.0, "a2": 200.0}
        adjusted, reduction = apply_supply_adjustment(rewards, 0.0, "NORMAL")
        assert reduction == 0.0
        assert adjusted == rewards

    def test_inv_s3_reduction_when_oversupplied(self):
        """Rewards reduced when oversupplied."""
        rewards = {"a1": 100.0, "a2": 200.0}
        adjusted, reduction = apply_supply_adjustment(rewards, 20.0, "ALLOW_BURN")
        assert reduction == 0.2
        assert abs(adjusted["a1"] - 80.0) < EPSILON
        assert abs(adjusted["a2"] - 160.0) < EPSILON

    def test_inv_s3_reduction_capped_at_50_pct(self):
        """INV-S3: reduction never exceeds 50%."""
        rewards = {"a1": 1000.0}
        adjusted, reduction = apply_supply_adjustment(rewards, 80.0, "ALLOW_BURN")
        assert reduction <= MAX_SUPPLY_REDUCTION
        assert adjusted["a1"] >= 500.0

    # --- Batch assembly ---

    def test_batch_assembly_complete(self):
        """assemble_settlement_batch produces a valid batch."""
        actions = [self._make_action()]
        batch = assemble_settlement_batch(
            batch_id="batch-1",
            epoch_start=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
            epoch_end=datetime(2026, 3, 14, 6, 0, tzinfo=timezone.utc),
            actions=actions,
        )
        assert batch.status == "PENDING"
        assert batch.total_minted > 0
        assert batch.supply_reduction == 0.0
        assert "aria" in batch.rewards

    def test_batch_with_supply_adjustment(self):
        """Batch correctly applies supply adjustment."""
        actions = [self._make_action(delta=0.8, trust=0.9, weight=0.6)]
        batch = assemble_settlement_batch(
            batch_id="batch-2",
            epoch_start=datetime(2026, 3, 14, 0, 0, tzinfo=timezone.utc),
            epoch_end=datetime(2026, 3, 14, 6, 0, tzinfo=timezone.utc),
            actions=actions,
            supply_delta_percentage=30.0,
            supply_action="ALLOW_BURN",
        )
        assert batch.supply_reduction == 0.3
        # Reward should be 70% of raw
        raw = 0.8 * 0.9 * 0.6 * SETTLEMENT_RATE
        assert abs(batch.rewards["aria"] - raw * 0.7) < 0.01

    # --- Worked example from ALGORITHM doc ---

    def test_worked_example_settlement(self):
        """Verify the worked example: Aria helps Nicolas."""
        action = self._make_action(delta=0.8, trust=0.9, weight=0.6)
        reward = compute_action_reward(action)
        expected = 0.8 * 0.9 * 0.6 * 10.0  # 4.32
        assert abs(reward - expected) < 0.01


# ===========================================================================
# Formula 5: Bilateral Bond Equilibrium -- INV-BE1 through INV-BE5
# ===========================================================================


class TestBilateralBondEquilibriumFormula:
    """Tests for Formula 5: delta = lambda * (W_human - W_ai)."""

    def _make_bond(
        self,
        w_human: float = 10000,
        w_ai: float = 5000,
        matured: bool = True,
        lambda_rate: float = LAMBDA_RATE,
    ) -> BondEquilibriumContext:
        return BondEquilibriumContext(
            bond_id="bond-1",
            human_wallet="human_wallet",
            ai_wallet="ai_wallet",
            w_human=w_human,
            w_ai=w_ai,
            lambda_rate=lambda_rate,
            maturation_complete=matured,
        )

    # --- INV-BE1: Post-Maturation Only ---

    def test_inv_be1_unmatured_bond_no_transfer(self):
        """INV-BE1: unmatured bond produces delta=0."""
        bond = self._make_bond(matured=False)
        result = compute_bond_transfer(bond)
        assert result.delta == 0.0
        assert result.w_human_after == bond.w_human
        assert result.w_ai_after == bond.w_ai

    def test_inv_be1_matured_bond_produces_transfer(self):
        """Matured bond with gap produces non-zero delta."""
        bond = self._make_bond(matured=True, w_human=10000, w_ai=0)
        result = compute_bond_transfer(bond)
        assert result.delta > 0

    # --- INV-BE2: Transfer Conservation ---

    def test_inv_be2_conservation(self):
        """INV-BE2: W_human + W_ai is conserved."""
        bond = self._make_bond(w_human=10000, w_ai=2000)
        result = compute_bond_transfer(bond)
        before = bond.w_human + bond.w_ai
        after = result.w_human_after + result.w_ai_after
        assert abs(before - after) < EPSILON

    def test_inv_be2_conservation_ai_richer(self):
        """Conservation when AI is richer."""
        bond = self._make_bond(w_human=1000, w_ai=9000)
        result = compute_bond_transfer(bond)
        before = bond.w_human + bond.w_ai
        after = result.w_human_after + result.w_ai_after
        assert abs(before - after) < EPSILON

    # --- INV-BE3: Convergence Direction ---

    def test_inv_be3_human_richer_sends_to_ai(self):
        """INV-BE3: human richer -> delta > 0 (human -> AI)."""
        bond = self._make_bond(w_human=10000, w_ai=2000)
        result = compute_bond_transfer(bond)
        assert result.delta > 0

    def test_inv_be3_ai_richer_sends_to_human(self):
        """INV-BE3: AI richer -> delta < 0 (AI -> human)."""
        bond = self._make_bond(w_human=2000, w_ai=10000)
        result = compute_bond_transfer(bond)
        assert result.delta < 0

    def test_inv_be3_parity_no_transfer(self):
        """INV-BE3: at parity -> delta == 0."""
        bond = self._make_bond(w_human=5000, w_ai=5000)
        result = compute_bond_transfer(bond)
        assert result.delta == 0.0

    # --- INV-BE4: Transfer Bounds ---

    def test_inv_be4_max_daily_cap(self):
        """INV-BE4: |delta| <= MAX_DAILY_BOND_TRANSFER."""
        bond = self._make_bond(w_human=1000000, w_ai=0)
        result = compute_bond_transfer(bond)
        assert abs(result.delta) <= MAX_DAILY_BOND_TRANSFER

    def test_inv_be4_dust_threshold(self):
        """INV-BE4: transfers below MIN_TRANSFER_THRESHOLD are skipped."""
        # With lambda=0.05, gap must be >= 20 for delta >= 1.0
        bond = self._make_bond(w_human=100, w_ai=99)  # gap=1, delta=0.05
        result = compute_bond_transfer(bond)
        assert result.delta == 0.0

    # --- INV-BE5: Monotonic Convergence ---

    def test_inv_be5_gap_decreases_daily(self):
        """INV-BE5: gap strictly decreases each day (no external transfers)."""
        w_human = 10000.0
        w_ai = 0.0
        prev_gap = abs(w_human - w_ai)

        for day in range(50):
            bond = BondEquilibriumContext(
                bond_id="bond-conv",
                human_wallet="h", ai_wallet="a",
                w_human=w_human, w_ai=w_ai,
                lambda_rate=LAMBDA_RATE, maturation_complete=True,
            )
            result = compute_bond_transfer(bond)
            if result.delta == 0:
                break  # Below threshold, convergence done
            w_human = result.w_human_after
            w_ai = result.w_ai_after
            new_gap = abs(w_human - w_ai)
            assert new_gap < prev_gap, f"Gap increased on day {day+1}"
            prev_gap = new_gap

    # --- Convergence estimation ---

    def test_convergence_estimate_reasonable(self):
        """Convergence estimate is in the expected range."""
        days = estimate_convergence_days(10000, 0, lambda_rate=0.05, target_gap_pct=0.05)
        # Should be around 58 days (ln(0.05)/ln(0.95))
        assert 50 <= days <= 70

    def test_convergence_estimate_zero_gap(self):
        """Zero gap returns 0 days."""
        days = estimate_convergence_days(5000, 5000)
        assert days == 0

    # --- Balance safety ---

    def test_transfer_does_not_exceed_sender_balance(self):
        """Transfer can't make sender go negative."""
        # AI has only 2 tokens, but lambda * (human-ai) = 0.05 * 998 > 2
        bond = self._make_bond(w_human=0, w_ai=2, lambda_rate=0.05)
        result = compute_bond_transfer(bond)
        assert result.w_human_after >= 0
        assert result.w_ai_after >= 0

    # --- Batch ---

    def test_batch_equilibrium_filters_unmatured(self):
        """Batch filters out unmatured bonds."""
        bonds = [
            self._make_bond(matured=True, w_human=10000, w_ai=5000),
            self._make_bond(matured=False, w_human=10000, w_ai=5000),
        ]
        results = compute_batch_equilibrium(bonds)
        assert len(results) == 2
        assert results[0].delta != 0
        assert results[1].delta == 0  # unmatured

    # --- Edge cases ---

    def test_negative_balance_raises(self):
        """Negative balances raise ValueError."""
        with pytest.raises(ValueError, match="w_human"):
            compute_bond_transfer(self._make_bond(w_human=-100))
        with pytest.raises(ValueError, match="w_ai"):
            compute_bond_transfer(self._make_bond(w_ai=-100))

    def test_invalid_lambda_raises(self):
        """Lambda out of range raises ValueError."""
        with pytest.raises(ValueError, match="lambda_rate"):
            compute_bond_transfer(self._make_bond(lambda_rate=0))
        with pytest.raises(ValueError, match="lambda_rate"):
            compute_bond_transfer(self._make_bond(lambda_rate=1.5))


# ===========================================================================
# Formula 6: UBC Proximity Redistribution -- INV-UBC1 through INV-UBC3
# ===========================================================================


class TestUBCProximityRedistributionFormula:
    """Tests for Formula 6: Space-weighted tax pool distribution."""

    def _make_spaces(self) -> List[SpacePresence]:
        """Create the worked example from ALGORITHM doc."""
        return [
            SpacePresence(
                space_id="engineering",
                actors={"aria": 8.0, "bolt": 6.0, "clio": 4.0},
            ),
            SpacePresence(
                space_id="research",
                actors={"aria": 4.0, "dane": 6.0},
            ),
            SpacePresence(
                space_id="solo",
                actors={"echo": 10.0},
            ),
        ]

    # --- INV-UBC1: Share Normalization ---

    def test_inv_ubc1_shares_sum_to_one(self):
        """INV-UBC1: all shares sum to 1.0."""
        spaces = self._make_spaces()
        actor_weights = compute_actor_weights(spaces)
        shares = compute_redistribution_shares(actor_weights)
        total = sum(s.share for s in shares)
        assert abs(total - 1.0) < EPSILON

    def test_inv_ubc1_full_redistribution_sums_to_pool(self):
        """INV-SC3: total distributed == pool balance."""
        spaces = self._make_spaces()
        shares, total_distributed = compute_redistribution(10000.0, spaces)
        assert abs(total_distributed - 10000.0) < EPSILON

    # --- INV-UBC2: Minimum Co-Presence Requirement ---

    def test_inv_ubc2_solo_actors_excluded(self):
        """INV-UBC2: solo actors never receive redistribution."""
        spaces = self._make_spaces()
        shares, _ = compute_redistribution(10000.0, spaces)
        actor_ids = {s.actor_id for s in shares}
        assert "echo" not in actor_ids

    def test_inv_ubc2_all_solo_no_redistribution(self):
        """If all spaces are solo, no redistribution occurs."""
        spaces = [
            SpacePresence(space_id="s1", actors={"a1": 10.0}),
            SpacePresence(space_id="s2", actors={"a2": 8.0}),
        ]
        shares, total = compute_redistribution(10000.0, spaces)
        assert len(shares) == 0
        assert total == 0.0

    # --- INV-UBC3: Weight Positivity ---

    def test_inv_ubc3_all_shares_positive_weight(self):
        """INV-UBC3: all actors receiving redistribution have positive weight."""
        spaces = self._make_spaces()
        actor_weights = compute_actor_weights(spaces)
        for actor_id, weight in actor_weights.items():
            assert weight > 0, f"Actor {actor_id} has non-positive weight"

    def test_inv_ubc3_zero_activity_no_weight(self):
        """Actors with zero moment weight in shared spaces get no weight."""
        spaces = [
            SpacePresence(
                space_id="s1",
                actors={"a1": 5.0, "a2": 0.0},
            )
        ]
        weights = compute_actor_weights(spaces)
        assert "a2" not in weights

    # --- Worked example from ALGORITHM doc ---

    def test_worked_example_redistribution(self):
        """Verify the worked example with log10 activity weighting.

        Spaces:
          engineering: aria=8.0, bolt=6.0, clio=4.0 (3 actors, bonus=2)
          research: aria=4.0, dane=6.0 (2 actors, bonus=1)
          solo: echo=10.0 (1 actor, skipped)

        Activity = log10(1 + moment_weight_sum) × community_bonus
          aria_eng  = log10(9) × 2 ≈ 1.908
          bolt_eng  = log10(7) × 2 ≈ 1.690
          clio_eng  = log10(5) × 2 ≈ 1.398
          aria_res  = log10(5) × 1 ≈ 0.699
          dane_res  = log10(7) × 1 ≈ 0.845

        Total aria = 1.908 + 0.699 = 2.607
        """
        import math
        spaces = self._make_spaces()
        actor_weights = compute_actor_weights(spaces)

        # Verify expected log10-based weights
        aria_expected = math.log10(1 + 8.0) * 2 + math.log10(1 + 4.0) * 1
        bolt_expected = math.log10(1 + 6.0) * 2
        clio_expected = math.log10(1 + 4.0) * 2
        dane_expected = math.log10(1 + 6.0) * 1

        assert abs(actor_weights.get("aria", 0) - aria_expected) < EPSILON
        assert abs(actor_weights.get("bolt", 0) - bolt_expected) < EPSILON
        assert abs(actor_weights.get("clio", 0) - clio_expected) < EPSILON
        assert abs(actor_weights.get("dane", 0) - dane_expected) < EPSILON
        assert "echo" not in actor_weights

        # Verify proportional distribution
        shares, distributed = compute_redistribution(10000.0, spaces)
        total_weight = sum(actor_weights.values())
        amounts = {s.actor_id: s.amount for s in shares}

        assert abs(amounts["aria"] - 10000 * aria_expected / total_weight) < 1.0
        assert abs(amounts["bolt"] - 10000 * bolt_expected / total_weight) < 1.0

    # --- Anti-spam (log10 envelope) ---

    def test_spam_gets_negligible_weight(self):
        """1000 zero-weight spam moments (total weight 0.001) get nearly nothing
        vs 10 quality moments (total weight 5.0)."""
        import math
        spaces = [
            SpacePresence(
                space_id="s1",
                actors={
                    "spammer": 0.001,   # 1000 moments × 0.000001 weight each
                    "quality": 5.0,     # 10 moments × 0.5 weight each
                },
            )
        ]
        weights = compute_actor_weights(spaces)
        # spammer: log10(1.001) × 1 ≈ 0.00043
        # quality: log10(6.0) × 1 ≈ 0.778
        assert weights["quality"] > weights["spammer"] * 100

    def test_diminishing_returns_on_high_activity(self):
        """Activity 100x higher only gives ~2x more weight (log10 curve)."""
        import math
        spaces_low = [
            SpacePresence(space_id="s1", actors={"a": 1.0, "b": 1.0})
        ]
        spaces_high = [
            SpacePresence(space_id="s1", actors={"a": 100.0, "b": 1.0})
        ]
        w_low = compute_actor_weights(spaces_low)
        w_high = compute_actor_weights(spaces_high)
        # 100x more activity → only ~3.4x more weight (log10(101)/log10(2) ≈ 6.6)
        ratio = w_high["a"] / w_low["a"]
        assert ratio < 10  # Way less than 100x
        assert ratio > 2   # But still rewarded

    # --- Edge cases ---

    def test_empty_spaces_list(self):
        """Empty spaces list returns nothing."""
        shares, total = compute_redistribution(10000.0, [])
        assert len(shares) == 0
        assert total == 0.0

    def test_zero_pool_returns_nothing(self):
        """Zero pool returns nothing."""
        spaces = self._make_spaces()
        shares, total = compute_redistribution(0.0, spaces)
        assert len(shares) == 0
        assert total == 0.0

    def test_negative_pool_raises(self):
        """Negative pool raises ValueError."""
        with pytest.raises(ValueError, match="pool_balance"):
            compute_redistribution(-100, [])

    def test_negative_moment_weight_raises(self):
        """Negative moment weight sum raises ValueError."""
        spaces = [
            SpacePresence(space_id="s1", actors={"a1": -5.0, "a2": 3.0})
        ]
        with pytest.raises(ValueError, match="moment_weight_sum"):
            compute_actor_weights(spaces)


# ===========================================================================
# Cross-Cutting Invariants -- INV-SC1, INV-CC1
# ===========================================================================


class TestCrossCuttingInvariants:
    """Cross-cutting invariants that span multiple formulas."""

    # --- INV-CC1: No Negative Balances ---

    def test_inv_cc1_demurrage_no_negative(self):
        """INV-CC1: demurrage can't produce negative balances."""
        ctx = DemurrageContext(
            w_total=100000, w_onchain=5, w_offregistry=99995,
            tau_base=0.001, actor_id="test"
        )
        result = compute_daily_demurrage(ctx)
        assert ctx.w_onchain - result.tax_amount >= 0

    def test_inv_cc1_bond_equilibrium_no_negative(self):
        """INV-CC1: bond equilibrium can't produce negative balances."""
        bond = BondEquilibriumContext(
            bond_id="b1", human_wallet="h", ai_wallet="a",
            w_human=10, w_ai=100000,
            lambda_rate=0.05, maturation_complete=True,
        )
        result = compute_bond_transfer(bond)
        assert result.w_human_after >= 0
        assert result.w_ai_after >= 0

    def test_inv_cc1_settlement_no_negative_reward(self):
        """INV-CC1: settlement rewards are never negative."""
        action = SettlementAction(
            action_id="a1", actor_x="x", actor_y="y",
            limbic_delta=-5.0, trust_y_to_x=0.9, weight_thing=0.5,
        )
        assert compute_action_reward(action) == 0.0

    # --- INV-SC1: Supply Accounting ---

    def test_inv_sc1_demurrage_batch_conservation(self):
        """INV-SC2: total tax collected matches sum of deductions."""
        contexts = [
            DemurrageContext(
                w_total=float(w), w_onchain=float(w), w_offregistry=0,
                tau_base=0.001, actor_id=f"a{i}"
            )
            for i, w in enumerate([100, 1000, 5000, 10000, 50000])
        ]
        results, total_tax = apply_demurrage_batch(contexts)
        sum_individual = sum(r.tax_amount for r in results)
        assert abs(total_tax - sum_individual) < EPSILON

    def test_inv_sc3_redistribution_conservation(self):
        """INV-SC3: total distributed == pool - remaining."""
        spaces = [
            SpacePresence(space_id="s1", actors={"a": 5.0, "b": 3.0}),
        ]
        pool = 10000.0
        shares, total = compute_redistribution(pool, spaces)
        assert abs(total - pool) < EPSILON

    # --- Constants env override ---

    def test_constants_env_override(self, monkeypatch):
        """Constants can be overridden via environment variables."""
        monkeypatch.setenv("MIND_METABOLIC_TAU_BASE", "0.002")
        # Re-import to pick up new env
        from economy.metabolic.metabolic_constants import _env_float
        assert _env_float("MIND_METABOLIC_TAU_BASE", 0.001) == 0.002

    def test_constants_env_override_invalid_falls_back(self, monkeypatch):
        """Invalid env value falls back to default."""
        monkeypatch.setenv("MIND_METABOLIC_TAU_BASE", "not_a_number")
        from economy.metabolic.metabolic_constants import _env_float
        assert _env_float("MIND_METABOLIC_TAU_BASE", 0.001) == 0.001


# ===========================================================================
# Edge cases and integration between formulas
# ===========================================================================


class TestIntegrationAndEdgeCases:
    """Tests that verify formula interactions and extreme edge cases."""

    def test_demurrage_feeds_redistribution(self):
        """Tax collected by demurrage can be redistributed by UBC formula."""
        # Step 1: collect demurrage
        contexts = [
            DemurrageContext(
                w_total=10000, w_onchain=10000, w_offregistry=0,
                tau_base=0.001, actor_id=f"a{i}"
            )
            for i in range(3)
        ]
        _, tax_pool = apply_demurrage_batch(contexts)
        assert tax_pool > 0

        # Step 2: redistribute
        spaces = [
            SpacePresence(
                space_id="s1",
                actors={"a0": 5.0, "a1": 3.0, "a2": 2.0},
            )
        ]
        shares, distributed = compute_redistribution(tax_pool, spaces)
        assert abs(distributed - tax_pool) < EPSILON
        assert len(shares) == 3

    def test_anti_sybil_increases_demurrage(self):
        """Off-registry balance increases effective demurrage."""
        # Without off-registry
        ctx_honest = DemurrageContext(
            w_total=10000, w_onchain=10000, w_offregistry=0,
            tau_base=0.001, actor_id="honest"
        )
        # With off-registry (same total, but some hidden)
        ctx_hiding = DemurrageContext(
            w_total=10000, w_onchain=5000, w_offregistry=5000,
            tau_base=0.001, actor_id="hiding"
        )
        result_honest = compute_daily_demurrage(ctx_honest)
        result_hiding = compute_daily_demurrage(ctx_hiding)
        # Same w_total means same computed tax
        # But hiding actor has less on-chain so may be clamped
        assert result_hiding.tax_amount <= result_honest.tax_amount

    def test_very_large_values(self):
        """Formulas handle very large values without overflow."""
        # Pricing with large utility
        ctx = PricingContext(c_base=1e6, u_s=10000, w_i=1e9, w_median=1e6)
        price = compute_progressive_price(ctx)
        assert price >= 0
        assert math.isfinite(price)

        # Demurrage with large balance
        ctx_d = DemurrageContext(
            w_total=1e12, w_onchain=1e12, w_offregistry=0,
            tau_base=0.001, actor_id="whale"
        )
        result = compute_daily_demurrage(ctx_d)
        assert result.tax_amount > 0
        assert math.isfinite(result.tax_amount)

    def test_very_small_positive_values(self):
        """Formulas handle very small positive values."""
        ctx = PricingContext(c_base=0.001, u_s=0.001, w_i=0.001, w_median=0.001)
        price = compute_progressive_price(ctx)
        assert price >= 0
        assert math.isfinite(price)
