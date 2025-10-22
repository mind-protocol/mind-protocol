"""
Test PR-D: Identity Multiplicity (Outcome-Based Detection)

Tests outcome-based multiplicity detection including:
- Task progress tracking over rolling window
- Energy efficiency tracking
- Identity flip detection and counting
- Mode assessment (productive vs conflict vs monitoring)
- Feature flag control
- Event emission

Author: Felix - 2025-10-23
Spec: docs/specs/v2/emotion/IMPLEMENTATION_PLAN.md (PR-D)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from orchestration.core.graph import Graph
from orchestration.core.subentity import Subentity
from orchestration.core.node import Node
from orchestration.core.types import NodeType
from orchestration.mechanisms.entity_activation import (
    track_task_progress,
    track_energy_efficiency,
    track_identity_flips,
    assess_multiplicity_mode,
)
from orchestration.core.settings import settings


@pytest.fixture
def test_entity():
    """Create a test subentity."""
    entity = Subentity(
        id="test_entity",
        entity_kind="functional",
        role_or_topic="test_role",
        description="Test entity for multiplicity tracking",
        energy_runtime=1.0,
        threshold_runtime=0.5,
        coherence_ema=0.8,
        member_count=10,
        task_progress_rate=0.0,
        energy_efficiency=0.0,
        identity_flip_count=0,
        properties={}
    )
    return entity


@pytest.fixture
def test_graph():
    """Create a test graph."""
    graph = Graph(graph_id="test_graph", name="Test Graph")
    return graph


def test_track_task_progress(test_entity):
    """Test that task progress tracking updates correctly with EMA."""
    print("\n" + "="*70)
    print("TEST: Task Progress Tracking")
    print("="*70)

    # Enable feature
    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        # Initial state
        assert test_entity.task_progress_rate == 0.0

        # Track progress: 5 goals in 10 frames = 0.5 rate
        track_task_progress(test_entity, goals_achieved=5, frames_elapsed=10)

        # EMA update: α * 0.5 + (1-α) * 0.0 = 0.1 * 0.5 = 0.05
        assert abs(test_entity.task_progress_rate - 0.05) < 1e-6
        print(f"  ✓ After 5 goals/10 frames: progress_rate = {test_entity.task_progress_rate:.4f}")

        # Track more progress: 8 goals in 10 frames = 0.8 rate
        track_task_progress(test_entity, goals_achieved=8, frames_elapsed=10)

        # EMA update: 0.1 * 0.8 + 0.9 * 0.05 = 0.08 + 0.045 = 0.125
        expected = 0.1 * 0.8 + 0.9 * 0.05
        assert abs(test_entity.task_progress_rate - expected) < 1e-6
        print(f"  ✓ After 8 goals/10 frames: progress_rate = {test_entity.task_progress_rate:.4f}")

        print(f"  ✓ Task progress tracking updates with EMA correctly")


def test_track_energy_efficiency(test_entity):
    """Test that energy efficiency tracking updates correctly."""
    print("\n" + "="*70)
    print("TEST: Energy Efficiency Tracking")
    print("="*70)

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        # Initial state
        assert test_entity.energy_efficiency == 0.0

        # Track efficiency: 5 work / 10 energy = 0.5 efficiency
        track_energy_efficiency(test_entity, work_output=5.0, total_energy_spent=10.0)

        # EMA update: 0.1 * 0.5 + 0.9 * 0.0 = 0.05
        assert abs(test_entity.energy_efficiency - 0.05) < 1e-6
        print(f"  ✓ After 5 work/10 energy: efficiency = {test_entity.energy_efficiency:.4f}")

        # Track more efficiency: 8 work / 10 energy = 0.8 efficiency
        track_energy_efficiency(test_entity, work_output=8.0, total_energy_spent=10.0)

        # EMA update: 0.1 * 0.8 + 0.9 * 0.05 = 0.08 + 0.045 = 0.125
        expected = 0.1 * 0.8 + 0.9 * 0.05
        assert abs(test_entity.energy_efficiency - expected) < 1e-6
        print(f"  ✓ After 8 work/10 energy: efficiency = {test_entity.energy_efficiency:.4f}")

        print(f"  ✓ Energy efficiency tracking updates with EMA correctly")


def test_track_identity_flips(test_entity, test_graph):
    """Test that identity flip detection works correctly."""
    print("\n" + "="*70)
    print("TEST: Identity Flip Detection")
    print("="*70)

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        with patch.object(settings, 'MULTIPLICITY_WINDOW_FRAMES', 20):
            # Initial state
            assert test_entity.identity_flip_count == 0
            assert 'previous_dominant_identity' not in test_entity.properties

            # First call - no previous identity, no flip
            track_identity_flips(test_entity, "entity_a", test_graph)
            assert test_entity.identity_flip_count == 0
            assert test_entity.properties['previous_dominant_identity'] == "entity_a"
            print(f"  ✓ First call: no flip, stored entity_a")

            # Same identity - no flip
            track_identity_flips(test_entity, "entity_a", test_graph)
            assert test_entity.identity_flip_count == 0
            print(f"  ✓ Same identity: no flip")

            # Different identity - flip detected
            track_identity_flips(test_entity, "entity_b", test_graph)
            assert test_entity.identity_flip_count == 1
            assert test_entity.properties['previous_dominant_identity'] == "entity_b"
            print(f"  ✓ Different identity: flip detected, count = 1")

            # Another flip
            track_identity_flips(test_entity, "entity_c", test_graph)
            # Second flip: count increments to 2
            # No decay applied because we flipped this frame
            assert test_entity.identity_flip_count == 2
            print(f"  ✓ Another flip: count = 2")

            # No flip this time - decay should apply
            track_identity_flips(test_entity, "entity_c", test_graph)  # Same identity
            # Decay applied: int(2 * (1 - 1/20)) = int(2 * 0.95) = int(1.9) = 1
            assert test_entity.identity_flip_count == 1
            print(f"  ✓ No flip: decay applied, count = 1")

            print(f"  ✓ Identity flip tracking with rolling window decay works")


def test_assess_multiplicity_mode_monitoring(test_entity):
    """Test mode assessment returns 'monitoring' with single identity."""
    print("\n" + "="*70)
    print("TEST: Multiplicity Mode - Monitoring (Single Identity)")
    print("="*70)

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        # Single identity active
        mode = assess_multiplicity_mode(test_entity, num_active_identities=1)
        assert mode == "monitoring"
        print(f"  ✓ Single identity (1) → mode = 'monitoring'")

        # Zero identities active
        mode = assess_multiplicity_mode(test_entity, num_active_identities=0)
        assert mode == "monitoring"
        print(f"  ✓ No identities (0) → mode = 'monitoring'")

        print(f"  ✓ Monitoring mode assessment correct")


def test_assess_multiplicity_mode_productive(test_entity):
    """Test mode assessment returns 'productive' with good outcomes."""
    print("\n" + "="*70)
    print("TEST: Multiplicity Mode - Productive (Good Outcomes)")
    print("="*70)

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        with patch.object(settings, 'PROGRESS_THRESHOLD', 0.3):
            with patch.object(settings, 'EFFICIENCY_THRESHOLD', 0.5):
                with patch.object(settings, 'FLIP_THRESHOLD', 5):
                    # Set good outcomes
                    test_entity.task_progress_rate = 0.6  # Above threshold
                    test_entity.energy_efficiency = 0.7  # Above threshold
                    test_entity.identity_flip_count = 3  # Below threshold

                    # Multiple identities active
                    mode = assess_multiplicity_mode(test_entity, num_active_identities=3)
                    assert mode == "productive"
                    print(f"  ✓ Good outcomes (progress=0.6, efficiency=0.7, flips=3) → 'productive'")

                    # Even with high flips, if other metrics good → productive
                    test_entity.identity_flip_count = 8  # Above flip threshold
                    mode = assess_multiplicity_mode(test_entity, num_active_identities=3)
                    assert mode == "productive"  # Still productive because progress and efficiency good
                    print(f"  ✓ High flips but good outcomes → still 'productive'")

                    print(f"  ✓ Productive mode assessment correct")


def test_assess_multiplicity_mode_conflict(test_entity):
    """Test mode assessment returns 'conflict' with poor outcomes."""
    print("\n" + "="*70)
    print("TEST: Multiplicity Mode - Conflict (Poor Outcomes)")
    print("="*70)

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        with patch.object(settings, 'PROGRESS_THRESHOLD', 0.3):
            with patch.object(settings, 'EFFICIENCY_THRESHOLD', 0.5):
                with patch.object(settings, 'FLIP_THRESHOLD', 5):
                    # Set poor outcomes (ALL thresholds violated)
                    test_entity.task_progress_rate = 0.2  # Below threshold
                    test_entity.energy_efficiency = 0.3  # Below threshold
                    test_entity.identity_flip_count = 8  # Above threshold

                    # Multiple identities active
                    mode = assess_multiplicity_mode(test_entity, num_active_identities=3)
                    assert mode == "conflict"
                    print(f"  ✓ Poor outcomes (progress=0.2, efficiency=0.3, flips=8) → 'conflict'")

                    # If any metric is good, NOT conflict
                    test_entity.task_progress_rate = 0.6  # Above threshold now
                    mode = assess_multiplicity_mode(test_entity, num_active_identities=3)
                    assert mode == "productive"  # Not all thresholds violated
                    print(f"  ✓ One metric good → 'productive' (not conflict)")

                    print(f"  ✓ Conflict mode assessment correct")


def test_feature_flag_disables_tracking(test_entity, test_graph):
    """Test that feature flag cleanly disables all tracking."""
    print("\n" + "="*70)
    print("TEST: Feature Flag Disables Tracking")
    print("="*70)

    # Disable feature
    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', False):
        # Track progress - should be no-op
        initial_progress = test_entity.task_progress_rate
        track_task_progress(test_entity, goals_achieved=10, frames_elapsed=10)
        assert test_entity.task_progress_rate == initial_progress
        print(f"  ✓ track_task_progress is no-op when disabled")

        # Track efficiency - should be no-op
        initial_efficiency = test_entity.energy_efficiency
        track_energy_efficiency(test_entity, work_output=10.0, total_energy_spent=10.0)
        assert test_entity.energy_efficiency == initial_efficiency
        print(f"  ✓ track_energy_efficiency is no-op when disabled")

        # Track flips - should be no-op
        initial_flips = test_entity.identity_flip_count
        track_identity_flips(test_entity, "entity_a", test_graph)
        assert test_entity.identity_flip_count == initial_flips
        print(f"  ✓ track_identity_flips is no-op when disabled")

        # Assessment should return "monitoring"
        mode = assess_multiplicity_mode(test_entity, num_active_identities=5)
        assert mode == "monitoring"
        print(f"  ✓ assess_multiplicity_mode returns 'monitoring' when disabled")

        print(f"  ✓ Feature flag cleanly disables all tracking")


def test_rolling_window_metrics():
    """Test that metrics use rolling window correctly."""
    print("\n" + "="*70)
    print("TEST: Rolling Window Metrics")
    print("="*70)

    entity = Subentity(
        id="test_entity",
        entity_kind="functional",
        role_or_topic="test_role",
        description="Test entity",
        task_progress_rate=0.0,
        energy_efficiency=0.0,
        identity_flip_count=0,
        properties={}
    )

    with patch.object(settings, 'IDENTITY_MULTIPLICITY_ENABLED', True):
        with patch.object(settings, 'MULTIPLICITY_WINDOW_FRAMES', 10):
            # Simulate 20 frames of tracking
            for i in range(20):
                # Varying progress
                goals = 5 if i % 2 == 0 else 3
                track_task_progress(entity, goals_achieved=goals, frames_elapsed=1)

                # Varying efficiency
                work = 8.0 if i % 2 == 0 else 4.0
                track_energy_efficiency(entity, work_output=work, total_energy_spent=10.0)

            # Metrics should have converged to steady state via EMA
            assert entity.task_progress_rate > 0.0
            assert entity.energy_efficiency > 0.0
            print(f"  ✓ After 20 frames: progress_rate = {entity.task_progress_rate:.4f}")
            print(f"  ✓ After 20 frames: energy_efficiency = {entity.energy_efficiency:.4f}")

            # Old values should be mostly forgotten (EMA decay)
            # Recent high values should dominate
            recent_progress = entity.task_progress_rate
            for i in range(10):
                track_task_progress(entity, goals_achieved=10, frames_elapsed=1)  # High progress

            assert entity.task_progress_rate > recent_progress
            print(f"  ✓ Recent high values dominate: progress_rate = {entity.task_progress_rate:.4f}")

            print(f"  ✓ Rolling window metrics work correctly with EMA")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
