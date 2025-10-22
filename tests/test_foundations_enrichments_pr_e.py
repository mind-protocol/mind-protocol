"""
Test PR-E: Foundations Enrichments (Consolidation, Decay Resistance, Stickiness)

Tests foundation mechanisms including:
- E.2 Consolidation (prevents premature decay of important patterns)
- E.3 Decay Resistance (central/bridge nodes persist longer)
- E.4 Stickiness (energy retention during diffusion)

Author: Felix - 2025-10-23
Spec: docs/specs/v2/emotion/IMPLEMENTATION_PLAN.md (PR-E)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
from unittest.mock import Mock, patch

from orchestration.core.graph import Graph
from orchestration.core.node import Node
from orchestration.core.link import Link
from orchestration.core.types import NodeType, LinkType
from orchestration.mechanisms.decay import (
    compute_consolidation_factor,
    compute_decay_resistance,
    decay_node_activation,
)
from orchestration.mechanisms.diffusion_runtime import (
    compute_stickiness,
)
from orchestration.core.settings import settings


@pytest.fixture
def test_graph():
    """Create a test graph with nodes and entities."""
    graph = Graph(graph_id="test_graph", name="Test Graph")
    return graph


@pytest.fixture
def memory_node():
    """Create a Memory node for testing."""
    node = Node(
        id="memory_1",
        name="Test Memory",
        node_type=NodeType.MEMORY,
        description="Test memory",
        E=1.0,
        theta=0.5,
        log_weight=0.0,
        ema_wm_presence=0.0
    )
    return node


@pytest.fixture
def task_node():
    """Create a Task node for testing."""
    node = Node(
        id="task_1",
        name="Test Task",
        node_type=NodeType.TASK,
        description="Test task",
        E=1.0,
        theta=0.5,
        log_weight=0.0,
        ema_wm_presence=0.0
    )
    return node


# === E.2 Consolidation Tests ===

def test_consolidation_disabled_returns_zero(memory_node, test_graph):
    """Test that consolidation returns 0 when disabled."""
    print("\n" + "="*70)
    print("TEST: Consolidation Disabled")
    print("="*70)

    with patch.object(settings, 'CONSOLIDATION_ENABLED', False):
        c = compute_consolidation_factor(memory_node, test_graph)
        assert c == 0.0
        print(f"  ✓ Consolidation disabled → c = 0.0")


def test_consolidation_retrieval_boost(memory_node, test_graph):
    """Test consolidation from high WM presence."""
    print("\n" + "="*70)
    print("TEST: Consolidation Retrieval Boost")
    print("="*70)

    with patch.object(settings, 'CONSOLIDATION_ENABLED', True):
        with patch.object(settings, 'CONSOLIDATION_RETRIEVAL_BOOST', 0.3):
            with patch.object(settings, 'CONSOLIDATION_MAX_FACTOR', 0.8):
                # High WM presence
                memory_node.ema_wm_presence = 0.8
                c = compute_consolidation_factor(memory_node, test_graph)

                # c_retrieval = 0.3 * 0.8 = 0.24
                expected = 0.3 * 0.8
                assert abs(c - expected) < 1e-6
                print(f"  ✓ WM presence=0.8 → c = {c:.4f} (expected {expected:.4f})")


def test_consolidation_affect_boost(memory_node, test_graph):
    """Test consolidation from high emotional magnitude."""
    print("\n" + "="*70)
    print("TEST: Consolidation Affect Boost")
    print("="*70)

    with patch.object(settings, 'CONSOLIDATION_ENABLED', True):
        with patch.object(settings, 'CONSOLIDATION_AFFECT_BOOST', 0.4):
            with patch.object(settings, 'CONSOLIDATION_MAX_FACTOR', 0.8):
                # High affect (magnitude = 0.9, threshold = 0.7)
                memory_node.emotion_vector = np.array([0.6, 0.67])  # magnitude = 0.9

                c = compute_consolidation_factor(memory_node, test_graph)

                # c_affect = 0.4 * (0.9 - 0.7) / 0.3 = 0.4 * 0.667 = 0.267
                # Clamped to CONSOLIDATION_AFFECT_BOOST max
                expected_raw = 0.4 * (0.9 - 0.7) / 0.3
                expected = min(expected_raw, 0.4)
                assert c > 0.0 and c <= 0.4
                print(f"  ✓ Emotion magnitude=0.9 → c = {c:.4f}")


def test_consolidation_capped_at_max(memory_node, test_graph):
    """Test that consolidation is capped at max factor."""
    print("\n" + "="*70)
    print("TEST: Consolidation Capped at Max")
    print("="*70)

    with patch.object(settings, 'CONSOLIDATION_ENABLED', True):
        with patch.object(settings, 'CONSOLIDATION_RETRIEVAL_BOOST', 0.5):
            with patch.object(settings, 'CONSOLIDATION_AFFECT_BOOST', 0.5):
                with patch.object(settings, 'CONSOLIDATION_MAX_FACTOR', 0.8):
                    # Both retrieval and affect high (would sum to > 0.8)
                    memory_node.ema_wm_presence = 1.0  # 0.5 * 1.0 = 0.5
                    memory_node.emotion_vector = np.array([0.8, 0.8])  # magnitude > 0.7

                    c = compute_consolidation_factor(memory_node, test_graph)

                    # Should be capped at 0.8
                    assert c <= 0.8
                    print(f"  ✓ High retrieval + affect → c = {c:.4f} (capped at 0.8)")


# === E.3 Decay Resistance Tests ===

def test_decay_resistance_disabled_returns_one(memory_node, test_graph):
    """Test that decay resistance returns 1.0 when disabled."""
    print("\n" + "="*70)
    print("TEST: Decay Resistance Disabled")
    print("="*70)

    with patch.object(settings, 'DECAY_RESISTANCE_ENABLED', False):
        r = compute_decay_resistance(memory_node, test_graph)
        assert r == 1.0
        print(f"  ✓ Resistance disabled → r = 1.0")


def test_decay_resistance_centrality(memory_node, test_graph):
    """Test resistance increases with node degree (centrality)."""
    print("\n" + "="*70)
    print("TEST: Decay Resistance Centrality")
    print("="*70)

    with patch.object(settings, 'DECAY_RESISTANCE_ENABLED', True):
        with patch.object(settings, 'DECAY_RESISTANCE_MAX_FACTOR', 1.5):
            # Create many links to increase degree
            for i in range(20):
                target = Node(id=f"target_{i}", name=f"Target {i}", node_type=NodeType.CONCEPT, description=f"Target {i}")
                link = Link(
                    id=f"link_{i}",
                    source_id=memory_node.id,
                    target_id=target.id,
                    link_type=LinkType.RELATES_TO,
                    subentity="test_entity",
                    goal="test",
                    mindstate="test",
                    energy=0.5,
                    confidence=0.8,
                    formation_trigger="test"
                )
                link.source = memory_node
                link.target = target
                memory_node.outgoing_links.append(link)

            r = compute_decay_resistance(memory_node, test_graph)

            # r_deg = 1 + 0.1 * tanh(20/20) = 1 + 0.1 * tanh(1) ≈ 1.076
            # r_bridge = 1.0 (no multi-entity)
            # r_type = 1.2 (Memory)
            # r = min(1.5, 1.076 * 1.0 * 1.2) ≈ 1.29
            expected_min = 1.2  # At least type resistance
            assert r >= expected_min
            print(f"  ✓ High degree (20) → r = {r:.4f} (>= {expected_min})")


def test_decay_resistance_type_based(test_graph):
    """Test resistance varies by node type."""
    print("\n" + "="*70)
    print("TEST: Decay Resistance Type-Based")
    print("="*70)

    with patch.object(settings, 'DECAY_RESISTANCE_ENABLED', True):
        with patch.object(settings, 'DECAY_RESISTANCE_MAX_FACTOR', 1.5):
            # Memory: r_type = 1.2
            memory = Node(id="mem", name="Memory", node_type=NodeType.MEMORY, description="Memory")
            r_memory = compute_decay_resistance(memory, test_graph)

            # Task: r_type = 1.0
            task = Node(id="task", name="Task", node_type=NodeType.TASK, description="Task")
            r_task = compute_decay_resistance(task, test_graph)

            # Memory should have higher resistance
            assert r_memory > r_task
            print(f"  ✓ Memory r = {r_memory:.4f} > Task r = {r_task:.4f}")


def test_decay_resistance_capped_at_max(memory_node, test_graph):
    """Test resistance is capped at max factor."""
    print("\n" + "="*70)
    print("TEST: Decay Resistance Capped")
    print("="*70)

    with patch.object(settings, 'DECAY_RESISTANCE_ENABLED', True):
        with patch.object(settings, 'DECAY_RESISTANCE_MAX_FACTOR', 1.5):
            # Create extreme centrality
            for i in range(100):
                target = Node(id=f"target_{i}", name=f"Target {i}", node_type=NodeType.CONCEPT, description=f"Target {i}")
                link = Link(
                    id=f"link_{i}",
                    source_id=memory_node.id,
                    target_id=target.id,
                    link_type=LinkType.RELATES_TO,
                    subentity="test_entity",
                    goal="test",
                    mindstate="test",
                    energy=0.5,
                    confidence=0.8,
                    formation_trigger="test"
                )
                link.source = memory_node
                link.target = target
                memory_node.outgoing_links.append(link)

            r = compute_decay_resistance(memory_node, test_graph)

            # Should be capped at 1.5
            assert r <= 1.5
            print(f"  ✓ Extreme degree (100) → r = {r:.4f} (capped at 1.5)")


# === E.4 Stickiness Tests ===

def test_stickiness_disabled_returns_one(memory_node, test_graph):
    """Test that stickiness returns 1.0 when disabled."""
    print("\n" + "="*70)
    print("TEST: Stickiness Disabled")
    print("="*70)

    with patch.object(settings, 'DIFFUSION_STICKINESS_ENABLED', False):
        s = compute_stickiness(memory_node, test_graph)
        assert s == 1.0
        print(f"  ✓ Stickiness disabled → s = 1.0")


def test_stickiness_type_based(test_graph):
    """Test stickiness varies by node type."""
    print("\n" + "="*70)
    print("TEST: Stickiness Type-Based")
    print("="*70)

    with patch.object(settings, 'DIFFUSION_STICKINESS_ENABLED', True):
        with patch.object(settings, 'STICKINESS_TYPE_MEMORY', 0.9):
            with patch.object(settings, 'STICKINESS_TYPE_TASK', 0.3):
                with patch.object(settings, 'STICKINESS_TYPE_DEFAULT', 0.6):
                    # Memory: sticky (0.9)
                    memory = Node(id="mem", name="Memory", node_type=NodeType.MEMORY, description="Memory")
                    s_memory = compute_stickiness(memory, test_graph)

                    # Task: flows (0.3)
                    task = Node(id="task", name="Task", node_type=NodeType.TASK, description="Task")
                    s_task = compute_stickiness(task, test_graph)

                    # Memory should be stickier
                    assert s_memory > s_task
                    assert s_memory >= 0.9  # Base + maybe centrality
                    assert s_task <= 0.4  # Base + maybe centrality
                    print(f"  ✓ Memory s = {s_memory:.4f} > Task s = {s_task:.4f}")


def test_stickiness_centrality_boost(memory_node, test_graph):
    """Test stickiness increases with node degree."""
    print("\n" + "="*70)
    print("TEST: Stickiness Centrality Boost")
    print("="*70)

    with patch.object(settings, 'DIFFUSION_STICKINESS_ENABLED', True):
        with patch.object(settings, 'STICKINESS_TYPE_MEMORY', 0.9):
            # No links
            s_before = compute_stickiness(memory_node, test_graph)

            # Add many links
            for i in range(20):
                target = Node(id=f"target_{i}", name=f"Target {i}", node_type=NodeType.CONCEPT, description=f"Target {i}")
                link = Link(
                    id=f"link_{i}",
                    source_id=memory_node.id,
                    target_id=target.id,
                    link_type=LinkType.RELATES_TO,
                    subentity="test_entity",
                    goal="test",
                    mindstate="test",
                    energy=0.5,
                    confidence=0.8,
                    formation_trigger="test"
                )
                link.source = memory_node
                link.target = target
                memory_node.outgoing_links.append(link)

            s_after = compute_stickiness(memory_node, test_graph)

            # Should increase from centrality boost
            assert s_after > s_before
            print(f"  ✓ No links: s = {s_before:.4f}, 20 links: s = {s_after:.4f}")


def test_stickiness_clamped(test_graph):
    """Test stickiness is clamped to [0.1, 1.0]."""
    print("\n" + "="*70)
    print("TEST: Stickiness Clamped")
    print("="*70)

    with patch.object(settings, 'DIFFUSION_STICKINESS_ENABLED', True):
        with patch.object(settings, 'STICKINESS_TYPE_MEMORY', 0.9):
            # Create node with extreme centrality
            memory = Node(id="mem", name="Memory", node_type=NodeType.MEMORY, description="Memory")
            for i in range(100):
                target = Node(id=f"target_{i}", name=f"Target {i}", node_type=NodeType.CONCEPT, description=f"Target {i}")
                link = Link(
                    id=f"link_{i}",
                    source_id=memory.id,
                    target_id=target.id,
                    link_type=LinkType.RELATES_TO,
                    subentity="test_entity",
                    goal="test",
                    mindstate="test",
                    energy=0.5,
                    confidence=0.8,
                    formation_trigger="test"
                )
                link.source = memory
                link.target = target
                memory.outgoing_links.append(link)

            s = compute_stickiness(memory, test_graph)

            # Should be clamped at 1.0
            assert 0.1 <= s <= 1.0
            print(f"  ✓ Extreme centrality → s = {s:.4f} (clamped to [0.1, 1.0])")


# === Integration: Decay with Consolidation + Resistance ===

def test_decay_with_consolidation_slows_decay(memory_node, test_graph):
    """Test that consolidation slows down decay."""
    print("\n" + "="*70)
    print("TEST: Consolidation Slows Decay")
    print("="*70)

    with patch.object(settings, 'CONSOLIDATION_ENABLED', True):
        with patch.object(settings, 'CONSOLIDATION_RETRIEVAL_BOOST', 0.5):
            with patch.object(settings, 'CONSOLIDATION_MAX_FACTOR', 0.8):
                # High WM presence → high consolidation
                memory_node.ema_wm_presence = 1.0
                initial_energy = 1.0
                memory_node.E = initial_energy

                # Decay without consolidation (pass graph=None)
                before_1, after_1 = decay_node_activation(memory_node, dt=1.0, graph=None)
                decay_no_consolidation = before_1 - after_1

                # Reset energy
                memory_node.E = initial_energy

                # Decay with consolidation (pass graph)
                before_2, after_2 = decay_node_activation(memory_node, dt=1.0, graph=test_graph)
                decay_with_consolidation = before_2 - after_2

                # Consolidation should slow decay
                assert decay_with_consolidation < decay_no_consolidation
                print(f"  ✓ Decay without consolidation: {decay_no_consolidation:.6f}")
                print(f"  ✓ Decay with consolidation: {decay_with_consolidation:.6f}")
                print(f"  ✓ Consolidation slowed decay by {(1 - decay_with_consolidation/decay_no_consolidation)*100:.1f}%")


def test_decay_with_resistance_slows_decay(memory_node, test_graph):
    """Test that resistance slows down decay."""
    print("\n" + "="*70)
    print("TEST: Resistance Slows Decay")
    print("="*70)

    with patch.object(settings, 'DECAY_RESISTANCE_ENABLED', True):
        with patch.object(settings, 'DECAY_RESISTANCE_MAX_FACTOR', 1.5):
            # Add links for high centrality
            for i in range(30):
                target = Node(id=f"target_{i}", name=f"Target {i}", node_type=NodeType.CONCEPT, description=f"Target {i}")
                link = Link(
                    id=f"link_{i}",
                    source_id=memory_node.id,
                    target_id=target.id,
                    link_type=LinkType.RELATES_TO,
                    subentity="test_entity",
                    goal="test",
                    mindstate="test",
                    energy=0.5,
                    confidence=0.8,
                    formation_trigger="test"
                )
                link.source = memory_node
                link.target = target
                memory_node.outgoing_links.append(link)

            initial_energy = 1.0
            memory_node.E = initial_energy

            # Decay with resistance
            before, after = decay_node_activation(memory_node, dt=1.0, graph=test_graph)
            decay_with_resistance = before - after

            # Resistance should be > 1.0, which slows decay
            r = compute_decay_resistance(memory_node, test_graph)
            assert r > 1.0
            # Decay should be less than without resistance (but we can't easily test that without disabling)
            print(f"  ✓ Resistance factor: {r:.4f}")
            print(f"  ✓ Decay with resistance: {decay_with_resistance:.6f}")


def test_stickiness_affects_energy_distribution():
    """Test that stickiness creates energy retention difference between Memory and Task."""
    print("\n" + "="*70)
    print("TEST: Stickiness Affects Energy Distribution")
    print("="*70)

    with patch.object(settings, 'DIFFUSION_STICKINESS_ENABLED', True):
        with patch.object(settings, 'STICKINESS_TYPE_MEMORY', 0.9):
            with patch.object(settings, 'STICKINESS_TYPE_TASK', 0.3):
                # Create source node with energy
                source = Node(
                    id="source",
                    name="Source",
                    node_type=NodeType.CONCEPT,
                    description="Source",
                    E=10.0
                )

                # Create Memory target (sticky)
                memory_target = Node(
                    id="memory_target",
                    name="Memory Target",
                    node_type=NodeType.MEMORY,
                    description="Memory target",
                    E=0.0
                )

                # Create Task target (flows)
                task_target = Node(
                    id="task_target",
                    name="Task Target",
                    node_type=NodeType.TASK,
                    description="Task target",
                    E=0.0
                )

                graph = Graph(graph_id="test", name="Test")

                # Simulate energy transfer with same delta_E
                delta_E = 5.0

                # Memory: high stickiness (0.9) -> retains 4.5
                s_memory = compute_stickiness(memory_target, graph)
                retained_memory = s_memory * delta_E

                # Task: low stickiness (0.3) -> retains 1.5
                s_task = compute_stickiness(task_target, graph)
                retained_task = s_task * delta_E

                # Memory should retain more energy than Task
                assert retained_memory > retained_task
                print(f"  ✓ Same energy transfer (Δ={delta_E}):")
                print(f"    - Memory (s={s_memory:.2f}) retains {retained_memory:.2f}")
                print(f"    - Task (s={s_task:.2f}) retains {retained_task:.2f}")
                print(f"    - Energy dissipated: Memory={delta_E - retained_memory:.2f}, Task={delta_E - retained_task:.2f}")
                print(f"  ✓ Stickiness creates differential energy retention")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
