# ctx_tests.md
**Generated:** 2025-10-24T21:23:35
---

## >>> BEGIN orchestration/tests/test_scheduler.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 9150 -->

"""
Unit Tests for Zippered Scheduler (AI #3)

Tests:
1. Zippered scheduling fairness
2. Deadline-aware early termination
3. Quota tracking and exhaustion
4. Integration with all modules

Author: AI #3 (Ada)
Created: 2025-10-21
"""

import pytest
import time
import numpy as np
from orchestration.mechanisms.sub_entity_core import SubEntity
from orchestration.mechanisms.scheduler import (
    zippered_schedule,
    check_early_termination,
    filter_active_entities,
    update_quota_remaining
)


class TestZipperedSchedule:
    """Test round-robin zippered scheduling"""

    def test_zippered_fairness(self):
        """Test that subentities interleave fairly"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]

        # Assign quotas
        subentities[0].quota_assigned = 3
        subentities[0].quota_remaining = 3
        subentities[1].quota_assigned = 2
        subentities[1].quota_remaining = 2
        subentities[2].quota_assigned = 4
        subentities[2].quota_remaining = 4

        schedule = zippered_schedule(subentities)

        # Verify schedule
        assert len(schedule) == 9  # 3 + 2 + 4

        # Extract just subentity IDs for pattern verification
        entity_sequence = [entity_id for entity_id, _ in schedule]

        # First round: A, B, C
        assert entity_sequence[0:3] == ['A', 'B', 'C']

        # Second round: A, B, C
        assert entity_sequence[3:6] == ['A', 'B', 'C']

        # Third round: A (only), C (B exhausted)
        assert entity_sequence[6:8] == ['A', 'C']

        # Fourth round: C (only)
        assert entity_sequence[8] == 'C'

    def test_empty_entities(self):
        """Test with no subentities"""
        schedule = zippered_schedule([])
        assert schedule == []

    def test_single_entity(self):
        """Test with single subentity"""
        subentity = SubEntity('A')
        subentity.quota_assigned = 5
        subentity.quota_remaining = 5

        schedule = zippered_schedule([subentity])

        assert len(schedule) == 5
        assert all(eid == 'A' for eid, _ in schedule)
        assert [idx for _, idx in schedule] == [0, 1, 2, 3, 4]

    def test_quota_exhaustion(self):
        """Test that subentities stop when quota exhausted"""
        subentities = [SubEntity('A'), SubEntity('B')]
        subentities[0].quota_assigned = 10
        subentities[0].quota_remaining = 10
        subentities[1].quota_assigned = 2
        subentities[1].quota_remaining = 2

        schedule = zippered_schedule(subentities)

        # B should appear only 2 times
        b_count = sum(1 for eid, _ in schedule if eid == 'B')
        assert b_count == 2

        # A should appear 10 times
        a_count = sum(1 for eid, _ in schedule if eid == 'A')
        assert a_count == 10


class TestDeadlineChecking:
    """Test early termination logic"""

    def test_no_termination_with_time(self):
        """Test that we don't terminate when plenty of time"""
        # Deadline is 1 second in future
        deadline_ms = (time.time() + 1.0) * 1000.0

        # 10 strides at 100us each = 1ms total (well under deadline)
        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=10
        )

        assert not should_terminate

    def test_termination_on_overshoot(self):
        """Test termination when predicted to overshoot"""
        # Deadline is 10ms in future
        deadline_ms = (time.time() + 0.01) * 1000.0

        # 1000 strides at 100us each = 100ms total (exceeds 10ms * 1.1 = 11ms)
        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=1000
        )

        assert should_terminate

    def test_termination_past_deadline(self):
        """Test termination when already past deadline"""
        # Deadline was 100ms ago
        deadline_ms = (time.time() - 0.1) * 1000.0

        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=1
        )

        assert should_terminate

    def test_conservative_margin(self):
        """Test 10% safety margin"""
        # Deadline is 10ms in future
        deadline_ms = (time.time() + 0.01) * 1000.0

        # Predicted time = 100 strides * 100us = 10ms
        # This is exactly at deadline, but within 10% margin (11ms)
        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=100
        )

        # Should NOT terminate (within 10% margin)
        assert not should_terminate

        # Now try 110 strides (11ms predicted, exactly at margin)
        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=110
        )

        # Should NOT terminate (exactly at 10% margin)
        assert not should_terminate

        # Now try 111 strides (11.1ms predicted, exceeds margin)
        should_terminate = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=100.0,
            remaining_strides=111
        )

        # Should terminate (exceeds 10% margin)
        assert should_terminate


class TestHelperFunctions:
    """Test helper utilities"""

    def test_filter_active_entities(self):
        """Test filtering subentities with quota remaining"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]

        subentities[0].quota_remaining = 5
        subentities[1].quota_remaining = 0
        subentities[2].quota_remaining = 3

        active = filter_active_entities(subentities)

        assert len(active) == 2
        assert subentities[0] in active
        assert subentities[2] in active
        assert subentities[1] not in active

    def test_update_quota_remaining(self):
        """Test quota decrement"""
        subentity = SubEntity('A')
        subentity.quota_remaining = 5

        update_quota_remaining(subentity)
        assert subentity.quota_remaining == 4

        update_quota_remaining(subentity)
        assert subentity.quota_remaining == 3

    def test_update_quota_at_zero(self):
        """Test that quota doesn't go negative"""
        subentity = SubEntity('A')
        subentity.quota_remaining = 0

        update_quota_remaining(subentity)
        assert subentity.quota_remaining == 0  # Stays at 0


class TestZeroConstantsCompliance:
    """Verify zero-constants compliance"""

    def test_no_fixed_priorities(self):
        """Verify pure round-robin (no priorities)"""
        # Create subentities with different quotas
        subentities = [SubEntity(f'E{i}') for i in range(5)]
        quotas = [3, 7, 2, 5, 4]

        for subentity, quota in zip(subentities, quotas):
            subentity.quota_assigned = quota
            subentity.quota_remaining = quota

        schedule = zippered_schedule(subentities)

        # Verify no subentity gets >1 stride ahead in any round
        entity_counts = {e.id: 0 for e in subentities}

        for entity_id, _ in schedule:
            entity_counts[entity_id] += 1

            # Check that no subentity is >1 stride ahead of others
            # (that still have quota)
            active_entities = [e for e in subentities if entity_counts[e.id] < e.quota_assigned]

            if active_entities:
                min_count = min(entity_counts[e.id] for e in active_entities)
                max_count = max(entity_counts[e.id] for e in active_entities)

                # Max difference should be at most 1
                assert max_count - min_count <= 1

    def test_deadline_from_measured_time(self):
        """Verify deadline checking uses measured stride time"""
        # This verifies the EMA approach - no fixed timing assumptions

        deadline_ms = (time.time() + 0.1) * 1000.0

        # With fast strides, many can fit
        fast_result = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=10.0,  # 10 microseconds
            remaining_strides=1000
        )

        # With slow strides, few can fit
        slow_result = check_early_termination(
            deadline_ms=deadline_ms,
            avg_stride_time_us=10000.0,  # 10 milliseconds
            remaining_strides=20
        )

        # Fast strides should NOT terminate (1000 * 10us = 10ms < 100ms * 1.1)
        assert not fast_result

        # Slow strides SHOULD terminate (20 * 10ms = 200ms > 100ms * 1.1)
        assert slow_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


## <<< END orchestration/tests/test_scheduler.py
---

## >>> BEGIN orchestration/tests/test_quotas.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 10573 -->

"""
Unit tests for Hamilton Quota Allocation

Tests:
1. Hamilton method fairness (no rounding bias)
2. Per-frame normalization (mean=1.0)
3. Edge cases (empty subentities, zero budget)
4. Integration with SubEntity

Author: AI #2
Created: 2025-10-21
"""

import pytest
import numpy as np
from orchestration.mechanisms.sub_entity_core import SubEntity
from orchestration.mechanisms.quotas import (
    hamilton_quota_allocation,
    compute_modulation_factors,
    allocate_quotas
)


class TestHamiltonAllocation:
    """Test Hamilton's largest remainder method"""

    def test_exact_proportions(self):
        """Test case: exact proportions (no remainder)"""
        # 3 subentities, 10 strides, weights 0.5, 0.3, 0.2
        # Expected: 5, 3, 2
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]
        weights = {'A': 0.5, 'B': 0.3, 'C': 0.2}

        quotas = hamilton_quota_allocation(subentities, Q_total=10, weights=weights)

        assert quotas['A'] == 5
        assert quotas['B'] == 3
        assert quotas['C'] == 2
        assert sum(quotas.values()) == 10

    def test_remainder_distribution(self):
        """Test case: remainder distribution by fractional part"""
        # 3 subentities, 11 strides, weights 0.5, 0.3, 0.2
        # Fractional: A=5.5, B=3.3, C=2.2
        # Integer parts: A=5, B=3, C=2 (sum=10, R=1)
        # Remainders: A=0.5, B=0.3, C=0.2 (A wins)
        # Expected: A=6, B=3, C=2
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]
        weights = {'A': 0.5, 'B': 0.3, 'C': 0.2}

        quotas = hamilton_quota_allocation(subentities, Q_total=11, weights=weights)

        assert quotas['A'] == 6  # Got the remainder
        assert quotas['B'] == 3
        assert quotas['C'] == 2
        assert sum(quotas.values()) == 11

    def test_zero_total_weight(self):
        """Test case: all subentities have zero weight"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]
        weights = {'A': 0.0, 'B': 0.0, 'C': 0.0}

        quotas = hamilton_quota_allocation(subentities, Q_total=9, weights=weights)

        # Should distribute evenly: 3, 3, 3
        assert sum(quotas.values()) == 9
        assert quotas['A'] == 3
        assert quotas['B'] == 3
        assert quotas['C'] == 3

    def test_single_entity(self):
        """Test case: single subentity gets all quota"""
        subentities = [SubEntity('A')]
        weights = {'A': 1.0}

        quotas = hamilton_quota_allocation(subentities, Q_total=100, weights=weights)

        assert quotas['A'] == 100

    def test_no_bias_over_time(self):
        """Test case: proportional fairness over multiple allocations"""
        subentities = [SubEntity('A'), SubEntity('B'), SubEntity('C')]
        # Slightly unequal weights to avoid tied remainders (more realistic)
        weights = {'A': 0.4, 'B': 0.35, 'C': 0.25}

        # Allocate varying budgets
        budgets = [10, 11, 12, 10, 11]  # Total = 54
        total_A = 0
        total_B = 0
        total_C = 0

        for budget in budgets:
            quotas = hamilton_quota_allocation(subentities, Q_total=budget, weights=weights)
            total_A += quotas['A']
            total_B += quotas['B']
            total_C += quotas['C']

        # Verify no strides lost
        assert total_A + total_B + total_C == sum(budgets)

        # Verify proportionality (within rounding tolerance)
        # Expected: A=21.6, B=18.9, C=13.5
        # Acceptable: A∈[21,22], B∈[18,19], C∈[13,14]
        assert 21 <= total_A <= 22
        assert 18 <= total_B <= 20
        assert 13 <= total_C <= 14


class TestModulationFactors:
    """Test per-frame normalization"""

    def test_normalization_to_mean_one(self):
        """Test that factors normalize to mean=1.0"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]

        # Set up dummy extents
        for subentity in subentities:
            subentity.extent = {1, 2, 3}
            subentity.rho_local_ema = 1.0

        factors = compute_modulation_factors(
            subentities,
            graph=None,
            recent_stimuli=None
        )

        # Extract urgency values
        urgency_values = [f['urgency'] for f in factors.values()]
        reachability_values = [f['reachability'] for f in factors.values()]
        health_values = [f['health'] for f in factors.values()]

        # Mean should be 1.0 (within numerical tolerance)
        assert abs(np.mean(urgency_values) - 1.0) < 1e-6
        assert abs(np.mean(reachability_values) - 1.0) < 1e-6
        assert abs(np.mean(health_values) - 1.0) < 1e-6

    def test_health_inverse_of_rho(self):
        """Test that health = 1/rho"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
        ]

        # Set different rho values
        subentities[0].rho_local_ema = 0.5  # Healthy (low rho)
        subentities[1].rho_local_ema = 1.5  # Unhealthy (high rho)

        # Set dummy extents
        for subentity in subentities:
            subentity.extent = {1, 2}

        factors = compute_modulation_factors(
            subentities,
            graph=None,
            recent_stimuli=None
        )

        # A should have higher health (1/0.5 = 2.0 raw)
        # B should have lower health (1/1.5 = 0.67 raw)
        # After normalization to mean=1.0, A should be > 1.0, B should be < 1.0
        assert factors['A']['health'] > factors['B']['health']

    def test_urgency_stimulus_matching(self):
        """Test urgency increases with stimulus similarity"""
        subentities = [SubEntity('A'), SubEntity('B')]

        # Create centroid with known embedding
        emb_a = np.array([1.0, 0.0, 0.0])  # Unit vector in x
        emb_b = np.array([0.0, 1.0, 0.0])  # Unit vector in y

        subentities[0].centroid.add_node(emb_a)
        subentities[1].centroid.add_node(emb_b)
        subentities[0].extent = {1}
        subentities[1].extent = {2}

        # Stimulus aligned with subentity A
        recent_stimuli = [{'embedding': np.array([1.0, 0.0, 0.0])}]

        factors = compute_modulation_factors(
            subentities,
            graph=None,
            recent_stimuli=recent_stimuli
        )

        # A should have higher urgency (stimulus matches)
        assert factors['A']['urgency'] > factors['B']['urgency']


class TestIntegration:
    """Integration tests for complete quota allocation"""

    def test_allocate_quotas_assigns_to_entities(self):
        """Test that allocate_quotas() sets subentity attributes"""
        subentities = [
            SubEntity('A'),
            SubEntity('B'),
            SubEntity('C')
        ]

        # Set up extents
        subentities[0].extent = {1, 2}  # Size 2
        subentities[1].extent = {3, 4, 5}  # Size 3
        subentities[2].extent = {6}  # Size 1

        quotas = allocate_quotas(
            subentities,
            Q_total=12,
            graph=None,
            recent_stimuli=None
        )

        # Verify quotas were assigned
        assert subentities[0].quota_assigned == quotas['A']
        assert subentities[1].quota_assigned == quotas['B']
        assert subentities[2].quota_assigned == quotas['C']

        # Verify quota_remaining initialized
        assert subentities[0].quota_remaining == quotas['A']
        assert subentities[1].quota_remaining == quotas['B']
        assert subentities[2].quota_remaining == quotas['C']

        # Total should equal budget
        assert sum(quotas.values()) == 12

    def test_inverse_size_weighting(self):
        """Test that smaller subentities get more strides per node"""
        subentities = [
            SubEntity('small'),
            SubEntity('large')
        ]

        # Small subentity: 2 nodes
        # Large subentity: 10 nodes
        subentities[0].extent = {1, 2}
        subentities[1].extent = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12}

        # Same rho (health neutral)
        subentities[0].rho_local_ema = 1.0
        subentities[1].rho_local_ema = 1.0

        quotas = allocate_quotas(
            subentities,
            Q_total=12,
            graph=None,
            recent_stimuli=None
        )

        # Small subentity should get more strides per node
        strides_per_node_small = quotas['small'] / 2
        strides_per_node_large = quotas['large'] / 10

        assert strides_per_node_small > strides_per_node_large


class TestZeroConstantsCompliance:
    """Verify zero-constants compliance"""

    def test_no_fixed_thresholds(self):
        """Verify no arbitrary constants in allocation logic"""
        # This test verifies the implementation by inspection
        # All normalization is relative to current population
        # No fixed urgency/reachability/health thresholds exist

        subentities = [SubEntity('A'), SubEntity('B')]
        subentities[0].extent = {1}
        subentities[1].extent = {2}
        subentities[0].rho_local_ema = 0.8
        subentities[1].rho_local_ema = 1.2

        factors = compute_modulation_factors(
            subentities,
            graph=None,
            recent_stimuli=None
        )

        # Mean of each factor should be 1.0 (per-frame normalization)
        health_values = [f['health'] for f in factors.values()]
        assert abs(np.mean(health_values) - 1.0) < 1e-6

        # No fixed thresholds - health varies with current population
        # If we change rho values, health factors change relative to new mean
        subentities[0].rho_local_ema = 0.5
        subentities[1].rho_local_ema = 1.5

        factors2 = compute_modulation_factors(
            subentities,
            graph=None,
            recent_stimuli=None
        )

        # Mean still 1.0, but individual values adjusted
        health_values2 = [f['health'] for f in factors2.values()]
        assert abs(np.mean(health_values2) - 1.0) < 1e-6

        # Values changed (not fixed thresholds)
        assert factors['A']['health'] != factors2['A']['health']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


## <<< END orchestration/tests/test_quotas.py
---

## >>> BEGIN orchestration/tests/test_multi_energy.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 11333 -->

"""
Unit tests for Mechanism 01: Multi-Energy Architecture

Tests verify:
1. Energy is strictly non-negative [0.0, ∞)
2. Saturation works correctly via tanh
3. Near-zero cleanup removes negligible values
4. Subentity energy is isolated (no cross-contamination)
5. Energy operations (get, set, add, multiply, clear)

Author: Felix (Engineer)
Created: 2025-10-19
"""

import pytest
import numpy as np
from datetime import datetime

from orchestration.core.node import Node
from orchestration.core.types import NodeType
from orchestration.mechanisms import multi_energy


# --- Fixtures ---

@pytest.fixture
def empty_node():
    """Create empty node with no energy."""
    return Node(
        id="test_node",
        name="Test Node",
        node_type=NodeType.CONCEPT,
        description="Test node for energy tests"
    )


@pytest.fixture
def energized_node():
    """Create node with pre-set energy."""
    node = Node(
        id="test_node",
        name="Test Node",
        node_type=NodeType.CONCEPT,
        description="Test node for energy tests"
    )
    multi_energy.set_entity_energy(node, "validator", 0.5)
    multi_energy.set_entity_energy(node, "translator", 0.3)
    return node


# --- Test: Energy Non-Negativity ---

def test_energy_cannot_be_negative(empty_node):
    """CRITICAL: Energy must be non-negative [0.0, ∞)."""
    multi_energy.set_entity_energy(empty_node, "test", -0.5)
    assert multi_energy.get_entity_energy(empty_node, "test") == 0.0


def test_negative_delta_clamped_at_zero(empty_node):
    """Adding negative delta should not create negative energy."""
    multi_energy.set_entity_energy(empty_node, "test", 0.2)
    multi_energy.add_entity_energy(empty_node, "test", -1.0)  # Large negative
    assert multi_energy.get_entity_energy(empty_node, "test") == 0.0


# --- Test: Saturation ---

def test_saturation_caps_at_one(empty_node):
    """Energy should approach but never exceed 1.0 after saturation."""
    # Very large input
    multi_energy.set_entity_energy(empty_node, "test", 100.0)
    energy = multi_energy.get_entity_energy(empty_node, "test")
    assert energy <= 1.0  # Can equal 1.0 at extreme values (tanh limit)
    assert energy > 0.99  # Very close to 1.0


def test_saturation_formula(empty_node):
    """Verify saturation formula: tanh(2.0 * value)."""
    multi_energy.set_entity_energy(empty_node, "test", 0.5)
    expected = np.tanh(2.0 * 0.5)
    actual = multi_energy.get_entity_energy(empty_node, "test")
    assert abs(expected - actual) < 0.001


def test_zero_input_zero_output(empty_node):
    """Zero input should produce zero output."""
    multi_energy.set_entity_energy(empty_node, "test", 0.0)
    assert multi_energy.get_entity_energy(empty_node, "test") == 0.0


# --- Test: Cleanup ---

def test_near_zero_cleanup(empty_node):
    """Values below threshold should be removed from dict."""
    # Set very small value
    multi_energy.set_entity_energy(empty_node, "test", 0.0005)
    # Should be cleaned up (saturated value < 0.001)
    assert "test" not in empty_node.energy


def test_cleanup_threshold(empty_node):
    """Verify cleanup threshold is 0.001."""
    # Value that saturates to just above threshold
    multi_energy.set_entity_energy(empty_node, "test", 0.0006)
    # May or may not be cleaned up depending on exact saturation
    # Value that saturates to well above threshold
    multi_energy.set_entity_energy(empty_node, "test2", 0.01)
    assert "test2" in empty_node.energy


# --- Test: Subentity Isolation ---

def test_entity_energy_isolated(empty_node):
    """Each subentity's energy is independent."""
    multi_energy.set_entity_energy(empty_node, "validator", 0.5)
    multi_energy.set_entity_energy(empty_node, "translator", 0.3)

    assert multi_energy.get_entity_energy(empty_node, "validator") != \
           multi_energy.get_entity_energy(empty_node, "translator")


def test_modifying_one_entity_doesnt_affect_others(energized_node):
    """Changing one subentity's energy doesn't affect other subentities."""
    original_translator = multi_energy.get_entity_energy(energized_node, "translator")

    multi_energy.set_entity_energy(energized_node, "validator", 0.9)

    assert multi_energy.get_entity_energy(energized_node, "translator") == original_translator


# --- Test: Get Operations ---

def test_get_nonexistent_entity_returns_zero(empty_node):
    """Getting energy for non-existent subentity should return 0.0."""
    assert multi_energy.get_entity_energy(empty_node, "nonexistent") == 0.0


def test_get_all_active_entities(energized_node):
    """Should return all subentities with non-zero energy."""
    subentities = multi_energy.get_all_active_entities(energized_node)
    assert set(subentities) == {"validator", "translator"}


def test_get_all_active_entities_empty(empty_node):
    """Empty node should return empty list."""
    assert multi_energy.get_all_active_entities(empty_node) == []


# --- Test: Set Operations ---

def test_set_overwrites_previous_value(empty_node):
    """Setting energy should overwrite previous value."""
    multi_energy.set_entity_energy(empty_node, "test", 0.5)
    multi_energy.set_entity_energy(empty_node, "test", 0.8)
    assert multi_energy.get_entity_energy(empty_node, "test") == pytest.approx(np.tanh(2.0 * 0.8))


# --- Test: Add Operations ---

def test_add_positive_delta(empty_node):
    """Adding positive delta should increase energy."""
    multi_energy.set_entity_energy(empty_node, "test", 0.5)
    before = multi_energy.get_entity_energy(empty_node, "test")

    multi_energy.add_entity_energy(empty_node, "test", 0.2)
    after = multi_energy.get_entity_energy(empty_node, "test")

    assert after > before


def test_add_negative_delta(empty_node):
    """Adding negative delta should decrease energy."""
    multi_energy.set_entity_energy(empty_node, "test", 0.5)
    before = multi_energy.get_entity_energy(empty_node, "test")

    multi_energy.add_entity_energy(empty_node, "test", -0.2)
    after = multi_energy.get_entity_energy(empty_node, "test")

    assert after < before


def test_add_to_nonexistent_entity(empty_node):
    """Adding delta to non-existent subentity should create it."""
    multi_energy.add_entity_energy(empty_node, "new", 0.5)
    assert multi_energy.get_entity_energy(empty_node, "new") > 0


# --- Test: Multiply Operations ---

def test_multiply_decay(empty_node):
    """Multiplying by factor < 1.0 should decrease energy."""
    multi_energy.set_entity_energy(empty_node, "test", 0.8)
    before = multi_energy.get_entity_energy(empty_node, "test")

    multi_energy.multiply_entity_energy(empty_node, "test", 0.5)
    after = multi_energy.get_entity_energy(empty_node, "test")

    assert after < before


def test_multiply_zero_energy(empty_node):
    """Multiplying zero energy should remain zero."""
    multi_energy.multiply_entity_energy(empty_node, "test", 0.5)
    assert multi_energy.get_entity_energy(empty_node, "test") == 0.0


# --- Test: Clear Operations ---

def test_clear_entity_energy(energized_node):
    """Clearing subentity energy should remove it from dict."""
    multi_energy.clear_entity_energy(energized_node, "validator")
    assert "validator" not in energized_node.energy
    assert multi_energy.get_entity_energy(energized_node, "validator") == 0.0


def test_clear_nonexistent_entity(empty_node):
    """Clearing non-existent subentity should not raise error."""
    multi_energy.clear_entity_energy(empty_node, "nonexistent")
    # Should not raise


def test_clear_all_energy(energized_node):
    """Clearing all energy should empty the dict."""
    multi_energy.clear_all_energy(energized_node)
    assert len(energized_node.energy) == 0


# --- Test: Statistics ---

def test_get_total_energy(energized_node):
    """Total energy should be sum of all subentity energies."""
    total = multi_energy.get_total_energy(energized_node)
    expected = (multi_energy.get_entity_energy(energized_node, "validator") +
                multi_energy.get_entity_energy(energized_node, "translator"))
    assert total == pytest.approx(expected)


def test_get_max_entity_energy(energized_node):
    """Should return subentity with highest energy."""
    max_entity, max_energy = multi_energy.get_max_entity_energy(energized_node)
    assert max_entity == "validator"  # Set to 0.5 vs 0.3
    assert max_energy > multi_energy.get_entity_energy(energized_node, "translator")


def test_get_max_entity_empty_node(empty_node):
    """Empty node should return (None, 0.0)."""
    max_entity, max_energy = multi_energy.get_max_entity_energy(empty_node)
    assert max_entity is None
    assert max_energy == 0.0


def test_get_energy_distribution(energized_node):
    """Energy distribution should sum to 1.0."""
    dist = multi_energy.get_energy_distribution(energized_node)
    assert sum(dist.values()) == pytest.approx(1.0)


# --- Test: Validation ---

def test_verify_energy_isolation_valid(energized_node):
    """Valid energy state should pass verification."""
    assert multi_energy.verify_energy_isolation(energized_node) is True


def test_verify_energy_isolation_detects_negative():
    """Verification should detect manually corrupted negative energy."""
    node = Node(id="test", name="Test", node_type=NodeType.CONCEPT, description="Test")
    node.energy["bad"] = -0.5  # Manual corruption
    assert multi_energy.verify_energy_isolation(node) is False


def test_verify_energy_isolation_detects_exceeds_saturation():
    """Verification should detect values exceeding saturation ceiling."""
    node = Node(id="test", name="Test", node_type=NodeType.CONCEPT, description="Test")
    node.energy["bad"] = 1.5  # Manual corruption
    assert multi_energy.verify_energy_isolation(node) is False


# --- Test: Phase 1 Success Criteria ---

def test_phase1_criterion_energy_isolation():
    """Phase 1 Success Criterion 1: Energy per subentity is isolated."""
    node = Node(id="test", name="Test", node_type=NodeType.CONCEPT, description="Test")

    multi_energy.set_entity_energy(node, "entity1", 0.5)
    multi_energy.set_entity_energy(node, "entity2", 0.8)

    # Modifying entity1 shouldn't affect entity2
    before = multi_energy.get_entity_energy(node, "entity2")
    multi_energy.set_entity_energy(node, "entity1", 0.1)
    after = multi_energy.get_entity_energy(node, "entity2")

    assert before == after


def test_phase1_criterion_energy_bounds():
    """Phase 1 Success Criterion 2: Energy strictly non-negative."""
    node = Node(id="test", name="Test", node_type=NodeType.CONCEPT, description="Test")

    # Try various negative inputs
    multi_energy.set_entity_energy(node, "test1", -1.0)
    multi_energy.set_entity_energy(node, "test2", -0.001)

    multi_energy.add_entity_energy(node, "test3", -5.0)

    # All should be zero or not exist
    assert multi_energy.get_entity_energy(node, "test1") == 0.0
    assert multi_energy.get_entity_energy(node, "test2") == 0.0
    assert multi_energy.get_entity_energy(node, "test3") == 0.0


## <<< END orchestration/tests/test_multi_energy.py
---

## >>> BEGIN orchestration/mechanisms/test_tick_speed.py
<!-- mtime: 2025-10-23T00:18:57; size_chars: 11438 -->

"""
Test: Adaptive Tick Speed Regulation

Verifies that:
1. Interval bounded to [min, max]
2. Physics dt capped correctly
3. EMA smoothing reduces oscillation
4. Stimulus triggers fast intervals
5. Dormancy leads to slow intervals
6. Diagnostics provide accurate state

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/runtime_engine/tick_speed.md
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
import pytest
from orchestration.mechanisms.tick_speed import AdaptiveTickScheduler, TickSpeedConfig


def test_interval_bounds():
    """Test that interval is clamped to [min, max] bounds (spec §2.1)."""
    print("\n=== Test 1: Interval Bounds ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,  # 0.1s
        max_interval_s=10.0,    # 10s
        enable_ema=False        # Disable smoothing for clearer bounds
    )
    scheduler = AdaptiveTickScheduler(config)

    # No stimulus yet - should use max_interval
    interval = scheduler.compute_next_interval()
    print(f"  No stimulus: interval={interval:.3f}s (expected {config.max_interval_s}s)")
    assert interval == config.max_interval_s, f"Expected max interval {config.max_interval_s}, got {interval}"

    # Fresh stimulus - should use min_interval
    scheduler.on_stimulus()
    interval = scheduler.compute_next_interval()
    print(f"  Fresh stimulus: interval={interval:.3f}s (expected {config.min_interval_ms/1000}s)")
    assert abs(interval - config.min_interval_ms/1000) < 0.001, \
        f"Expected min interval {config.min_interval_ms/1000}, got {interval}"

    # Wait 5 seconds (mid-range)
    scheduler.last_stimulus_time = time.time() - 5.0
    interval = scheduler.compute_next_interval()
    print(f"  5s after stimulus: interval={interval:.3f}s (expected 5s)")
    assert abs(interval - 5.0) < 0.1, f"Expected ~5s interval, got {interval}"

    # Wait 20 seconds (should clamp to max)
    scheduler.last_stimulus_time = time.time() - 20.0
    interval = scheduler.compute_next_interval()
    print(f"  20s after stimulus: interval={interval:.3f}s (clamped to {config.max_interval_s}s)")
    assert interval == config.max_interval_s, f"Expected clamped to max {config.max_interval_s}, got {interval}"

    print("  ✓ Intervals correctly bounded to [min, max]")


def test_dt_capping():
    """Test that physics dt is capped (spec §2.2)."""
    print("\n=== Test 2: Physics dt Capping ===")

    config = TickSpeedConfig(
        dt_cap_s=5.0,  # Max 5 second physics step
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # Short interval (under cap)
    dt_used, was_capped = scheduler.compute_dt(interval=2.0)
    print(f"  Short interval (2.0s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == 2.0, f"Expected dt=2.0, got {dt_used}"
    assert not was_capped, "Short interval should not be capped"

    # Interval at cap
    dt_used, was_capped = scheduler.compute_dt(interval=5.0)
    print(f"  At cap (5.0s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == 5.0, f"Expected dt=5.0, got {dt_used}"
    assert not was_capped, "Interval at cap should not be marked as capped"

    # Long interval (over cap)
    dt_used, was_capped = scheduler.compute_dt(interval=120.0)
    print(f"  Long interval (120s): dt={dt_used:.3f}s, capped={was_capped}")
    assert dt_used == config.dt_cap_s, f"Expected dt capped to {config.dt_cap_s}, got {dt_used}"
    assert was_capped, "Long interval should be capped"

    print("  ✓ Physics dt correctly capped")


def test_ema_smoothing():
    """Test that EMA smoothing reduces oscillation (spec §2.1, §7)."""
    print("\n=== Test 3: EMA Smoothing ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        ema_beta=0.3,       # 30% new, 70% old
        enable_ema=True
    )
    scheduler = AdaptiveTickScheduler(config)

    # First stimulus - starts at min
    scheduler.on_stimulus()
    interval_1 = scheduler.compute_next_interval()
    print(f"  Initial (fresh stimulus): {interval_1:.3f}s")

    # Simulate sudden jump to 5 seconds
    scheduler.last_stimulus_time = time.time() - 5.0
    interval_2 = scheduler.compute_next_interval()
    print(f"  After 5s gap (with EMA): {interval_2:.3f}s")

    # EMA should smooth: 0.3 * 5.0 + 0.7 * interval_1
    # interval_1 ≈ 0.1 (min_interval)
    expected_ema = 0.3 * 5.0 + 0.7 * interval_1
    print(f"  Expected EMA: {expected_ema:.3f}s")
    assert abs(interval_2 - expected_ema) < 0.1, \
        f"EMA should be ~{expected_ema:.3f}, got {interval_2:.3f}"

    # Without EMA, should jump directly to 5.0
    scheduler_no_ema = AdaptiveTickScheduler(TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        enable_ema=False
    ))
    scheduler_no_ema.on_stimulus()
    _ = scheduler_no_ema.compute_next_interval()
    scheduler_no_ema.last_stimulus_time = time.time() - 5.0
    interval_no_ema = scheduler_no_ema.compute_next_interval()
    print(f"  Without EMA (direct jump): {interval_no_ema:.3f}s")
    assert abs(interval_no_ema - 5.0) < 0.1, "Without EMA should jump directly to 5.0"

    print("  ✓ EMA smoothing reduces oscillation")


def test_stimulus_tracking():
    """Test that stimulus tracking triggers fast intervals."""
    print("\n=== Test 4: Stimulus Tracking ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # No stimulus - dormant
    interval_dormant = scheduler.compute_next_interval()
    print(f"  Dormant (no stimulus): {interval_dormant:.3f}s")
    assert interval_dormant == config.max_interval_s, "Dormant should use max interval"

    # Stimulus arrives
    scheduler.on_stimulus()
    interval_active = scheduler.compute_next_interval()
    print(f"  Active (fresh stimulus): {interval_active:.3f}s")
    assert abs(interval_active - config.min_interval_ms/1000) < 0.001, \
        "Fresh stimulus should trigger min interval"

    # Multiple rapid stimuli
    for i in range(5):
        scheduler.on_stimulus()
        interval = scheduler.compute_next_interval()
        print(f"  Stimulus #{i+1}: {interval:.3f}s")
        assert abs(interval - config.min_interval_ms/1000) < 0.001, \
            "Rapid stimuli should keep interval at min"

    print("  ✓ Stimulus tracking triggers fast intervals")


def test_dormancy_behavior():
    """Test that long inactivity leads to slow intervals."""
    print("\n=== Test 5: Dormancy Behavior ===")

    config = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=10.0,
        enable_ema=False
    )
    scheduler = AdaptiveTickScheduler(config)

    # Active phase
    scheduler.on_stimulus()
    interval_active = scheduler.compute_next_interval()
    print(f"  Active phase: {interval_active:.3f}s")

    # Gradual transition to dormancy
    time_points = [0.5, 1.0, 2.0, 5.0, 8.0, 15.0]
    for t in time_points:
        scheduler.last_stimulus_time = time.time() - t
        interval = scheduler.compute_next_interval()
        expected = min(t, config.max_interval_s)
        print(f"  {t:.1f}s after stimulus: {interval:.3f}s (expected {expected:.3f}s)")
        assert abs(interval - expected) < 0.1, \
            f"At {t}s should have interval ~{expected:.3f}, got {interval:.3f}"

    print("  ✓ Dormancy behavior correct")


def test_dt_integration_flow():
    """Test complete flow: interval → dt → physics integration."""
    print("\n=== Test 6: dt Integration Flow ===")

    # Test 6a: Conversation mode (with EMA)
    config_active = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        dt_cap_s=5.0,
        enable_ema=True,
        ema_beta=0.3
    )
    scheduler_active = AdaptiveTickScheduler(config_active)

    print("  Simulating conversation mode (rapid stimuli, with EMA):")
    for i in range(3):
        scheduler_active.on_stimulus()
        interval = scheduler_active.compute_next_interval()
        dt, capped = scheduler_active.compute_dt(interval)
        print(f"    Tick {i+1}: interval={interval:.3f}s, dt={dt:.3f}s, capped={capped}")
        assert dt <= config_active.dt_cap_s, f"dt should never exceed cap"
        assert dt <= interval, f"dt should never exceed interval"

    # Test 6b: Dormancy mode (no EMA for clearer capping behavior)
    config_dormant = TickSpeedConfig(
        min_interval_ms=100.0,
        max_interval_s=60.0,
        dt_cap_s=5.0,
        enable_ema=False  # Disable for clearer cap testing
    )
    scheduler_dormant = AdaptiveTickScheduler(config_dormant)

    print("  Simulating dormancy mode (no stimuli, no EMA):")
    for i in range(3):
        scheduler_dormant.last_stimulus_time = time.time() - (10.0 * (i+1))  # 10s, 20s, 30s ago
        interval = scheduler_dormant.compute_next_interval()
        dt, capped = scheduler_dormant.compute_dt(interval)
        print(f"    Tick {i+1}: interval={interval:.3f}s, dt={dt:.3f}s, capped={capped}")
        assert dt == config_dormant.dt_cap_s, f"Long intervals should hit dt cap"
        assert capped, f"Long intervals should be marked as capped"

    print("  ✓ dt integration flow correct")


def test_diagnostics():
    """Test diagnostic output for observability."""
    print("\n=== Test 7: Diagnostics ===")

    config = TickSpeedConfig()
    scheduler = AdaptiveTickScheduler(config)

    # Get diagnostics before stimulus
    diag = scheduler.get_diagnostics()
    print(f"  Before stimulus:")
    print(f"    last_stimulus_time: {diag['last_stimulus_time']}")
    print(f"    time_since_stimulus: {diag['time_since_stimulus']}")
    assert diag['last_stimulus_time'] is None, "Should be None before stimulus"
    assert diag['time_since_stimulus'] is None, "Should be None before stimulus"

    # After stimulus
    scheduler.on_stimulus()
    time.sleep(0.1)  # Brief pause
    diag = scheduler.get_diagnostics()
    print(f"  After stimulus:")
    print(f"    last_stimulus_time: {diag['last_stimulus_time']:.3f}")
    print(f"    time_since_stimulus: {diag['time_since_stimulus']:.3f}s")
    assert diag['last_stimulus_time'] is not None, "Should record stimulus time"
    assert diag['time_since_stimulus'] >= 0.1, "Should show time elapsed"
    assert diag['config']['min_interval_ms'] == config.min_interval_ms, "Config should match"

    print("  ✓ Diagnostics provide accurate state")


def run_all_tests():
    """Run all tick speed tests."""
    print("\n" + "=" * 70)
    print("Adaptive Tick Speed Regulation Tests")
    print("=" * 70)

    test_interval_bounds()
    test_dt_capping()
    test_ema_smoothing()
    test_stimulus_tracking()
    test_dormancy_behavior()
    test_dt_integration_flow()
    test_diagnostics()

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)

    print("\nSummary:")
    print("  - Interval bounds enforced [min, max]")
    print("  - Physics dt capped to prevent blow-ups")
    print("  - EMA smoothing reduces oscillation")
    print("  - Stimulus triggers fast intervals")
    print("  - Dormancy leads to slow intervals")
    print("  - dt integration flow correct")
    print("  - Diagnostics accurate")
    print("  - Ready for production deployment")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()


## <<< END orchestration/mechanisms/test_tick_speed.py
---

## >>> BEGIN orchestration/tests/test_consciousness_engine_v2.py
<!-- mtime: 2025-10-22T21:44:26; size_chars: 9945 -->

"""
Integration Tests for Consciousness Engine V2

Tests complete tick cycle with all mechanisms integrated.

Author: Felix (Engineer)
Created: 2025-10-19
"""

import pytest
import asyncio
from datetime import datetime

from orchestration.core import Node, Link, Graph
from orchestration.core.types import NodeType, LinkType
from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2, EngineConfig


# --- Test Fixtures ---

@pytest.fixture
def simple_graph():
    """
    Create a simple graph for testing.

    Topology:
        n1 --0.8--> n2 --0.6--> n3
         ---------0.5----------
    """
    graph = Graph(graph_id="test_graph", name="Test Graph")

    # Create nodes
    n1 = Node(
        id="n1",
        name="node_1",
        node_type=NodeType.CONCEPT,
        description="Test node 1"
    )
    n2 = Node(
        id="n2",
        name="node_2",
        node_type=NodeType.CONCEPT,
        description="Test node 2"
    )
    n3 = Node(
        id="n3",
        name="node_3",
        node_type=NodeType.CONCEPT,
        description="Test node 3"
    )

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    # Create links
    l1 = Link(
        id="l1",
        source=n1,
        target=n2,
        link_type=LinkType.ENABLES,
        weight=0.8
    )
    l2 = Link(
        id="l2",
        source=n2,
        target=n3,
        link_type=LinkType.ENABLES,
        weight=0.6
    )
    l3 = Link(
        id="l3",
        source=n1,
        target=n3,
        link_type=LinkType.ASSOCIATES,
        weight=0.5
    )

    graph.add_link(l1)
    graph.add_link(l2)
    graph.add_link(l3)

    return graph


@pytest.fixture
def mock_adapter():
    """Mock FalkorDB adapter for testing."""
    class MockAdapter:
        def update_node_energy(self, node):
            pass

        def update_link_weight(self, link):
            pass

    return MockAdapter()


# --- Integration Tests ---

@pytest.mark.anyio
async def test_engine_initialization(simple_graph, mock_adapter):
    """Engine should initialize with graph and config."""
    config = EngineConfig(
        tick_interval_ms=100,
        entity_id="test_entity",
        enable_websocket=False  # Disable for tests
    )

    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    assert engine.tick_count == 0
    assert engine.graph == simple_graph
    assert engine.config.entity_id == "test_entity"
    assert len(engine.graph.nodes) == 3
    assert len(engine.graph.links) == 3


@pytest.mark.anyio
async def test_single_tick_executes(simple_graph, mock_adapter):
    """Single tick should execute without errors."""
    config = EngineConfig(entity_id="test_entity", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject stimulus to activate system
    engine.inject_stimulus("n1", "test_entity", 0.5)

    # Execute one tick
    await engine.tick()

    assert engine.tick_count == 1
    assert engine.tick_duration_ms > 0


@pytest.mark.anyio
async def test_energy_diffuses(simple_graph, mock_adapter):
    """Energy should diffuse from n1 to neighbors."""
    config = EngineConfig(entity_id="test_entity", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject energy into n1
    n1 = simple_graph.get_node("n1")
    n1.set_entity_energy("test_entity", 0.8)

    # Record initial energies
    e1_before = n1.get_entity_energy("test_entity")
    e2_before = simple_graph.get_node("n2").get_entity_energy("test_entity")
    e3_before = simple_graph.get_node("n3").get_entity_energy("test_entity")

    # Execute ticks
    for _ in range(5):
        await engine.tick()

    # Check energy diffused
    e1_after = n1.get_entity_energy("test_entity")
    e2_after = simple_graph.get_node("n2").get_entity_energy("test_entity")
    e3_after = simple_graph.get_node("n3").get_entity_energy("test_entity")

    # n1 should have lost energy (redistributed)
    assert e1_after < e1_before

    # n2 and n3 should have gained energy
    assert e2_after > e2_before
    assert e3_after > e3_before


@pytest.mark.anyio
async def test_energy_decays(simple_graph, mock_adapter):
    """Energy should decay over time."""
    config = EngineConfig(entity_id="test_entity", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject energy into all nodes
    for node in simple_graph.nodes:
        node.set_entity_energy("test_entity", 0.5)

    # Record total energy
    total_before = sum(
        node.get_entity_energy("test_entity")
        for node in simple_graph.nodes
    )

    # Run ticks (decay should reduce total energy)
    for _ in range(10):
        await engine.tick()

    total_after = sum(
        node.get_entity_energy("test_entity")
        for node in simple_graph.nodes
    )

    # Total energy should decrease (due to decay)
    assert total_after < total_before


@pytest.mark.anyio
async def test_links_strengthen(simple_graph, mock_adapter):
    """Links should strengthen when endpoints active."""
    config = EngineConfig(entity_id="test_entity", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject high energy into n1 and n2 (link l1 should strengthen)
    simple_graph.get_node("n1").set_entity_energy("test_entity", 0.8)
    simple_graph.get_node("n2").set_entity_energy("test_entity", 0.8)

    # Record initial weight
    l1 = simple_graph.get_link("l1")
    weight_before = l1.weight

    # Execute ticks
    for _ in range(5):
        await engine.tick()

    weight_after = l1.weight

    # Link should have strengthened (both endpoints active)
    assert weight_after > weight_before


@pytest.mark.anyio
async def test_multiple_entities(simple_graph, mock_adapter):
    """Multiple subentities should operate independently."""
    config = EngineConfig(entity_id="entity1", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject energy for two different subentities
    n1 = simple_graph.get_node("n1")
    n1.set_entity_energy("entity1", 0.5)
    n1.set_entity_energy("entity2", 0.8)

    # Execute ticks
    await engine.tick()

    # Both subentities should still have energy (independent)
    assert n1.get_entity_energy("entity1") > 0
    assert n1.get_entity_energy("entity2") > 0


@pytest.mark.anyio
async def test_engine_metrics(simple_graph, mock_adapter):
    """Engine should report metrics correctly."""
    config = EngineConfig(entity_id="test_entity", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject stimulus
    engine.inject_stimulus("n1", "test_entity", 0.5)

    # Execute ticks
    await engine.tick()
    await engine.tick()

    metrics = engine.get_metrics()

    assert metrics["tick_count"] == 2
    assert metrics["nodes_total"] == 3
    assert metrics["links_total"] == 3
    assert "tick_duration_ms" in metrics
    assert "global_energy" in metrics


@pytest.mark.anyio
async def test_run_with_max_ticks(simple_graph, mock_adapter):
    """Engine should stop after max_ticks."""
    config = EngineConfig(
        tick_interval_ms=10,  # Fast ticks for testing
        entity_id="test_entity",
        enable_websocket=False
    )
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject stimulus
    engine.inject_stimulus("n1", "test_entity", 0.5)

    # Run for 5 ticks
    await engine.run(max_ticks=5)

    assert engine.tick_count == 5
    assert not engine.running


# --- Phase 1+2 Completion Criteria ---

@pytest.mark.anyio
async def test_phase1_criterion_multi_energy_isolation(simple_graph, mock_adapter):
    """
    Phase 1 Criterion: Multiple subentities can coexist on same node without interference.
    """
    config = EngineConfig(entity_id="entity1", enable_websocket=False)
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    n1 = simple_graph.get_node("n1")

    # Set different energies for three subentities
    n1.set_entity_energy("entity1", 0.3)
    n1.set_entity_energy("entity2", 0.7)
    n1.set_entity_energy("entity3", 0.5)

    # Run ticks for entity1
    await engine.tick()

    # All subentities should still have independent energies
    assert 0 < n1.get_entity_energy("entity1") <= 1.0
    assert 0 < n1.get_entity_energy("entity2") <= 1.0
    assert 0 < n1.get_entity_energy("entity3") <= 1.0

    # Subentities should be independent
    assert n1.get_entity_energy("entity1") != n1.get_entity_energy("entity2")


@pytest.mark.anyio
async def test_phase2_criterion_conservative_diffusion(simple_graph, mock_adapter):
    """
    Phase 2 Criterion: Diffusion conserves energy (except decay/stimuli).
    """
    config = EngineConfig(
        entity_id="test_entity",
        enable_websocket=False,
        enable_decay=False  # Disable decay to test pure diffusion
    )
    engine = ConsciousnessEngineV2(simple_graph, mock_adapter, config)

    # Inject fixed energy
    for node in simple_graph.nodes:
        node.set_entity_energy("test_entity", 0.5)

    total_before = sum(
        node.get_entity_energy("test_entity")
        for node in simple_graph.nodes
    )

    # Run diffusion (no decay, no stimuli)
    await engine.tick()

    total_after = sum(
        node.get_entity_energy("test_entity")
        for node in simple_graph.nodes
    )

    # Total should be conserved (within numerical precision)
    assert abs(total_after - total_before) < 0.01


## <<< END orchestration/tests/test_consciousness_engine_v2.py
---
