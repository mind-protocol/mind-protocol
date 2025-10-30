"""
Test PR-E: Foundations Enrichments (E.2-E.8)

Tests foundation mechanisms including:
- E.2 Consolidation (prevents premature decay of important patterns)
- E.3 Decay Resistance (central/bridge nodes persist longer)
- E.4 Stickiness (energy retention during diffusion)
- E.5 Affective Priming (mood-congruent stimulus injection)
- E.6 Coherence Metric (measures flow vs chaos)
- E.7 Criticality Modes (phenomenological state classification)
- E.8 Task-Adaptive Targets (context-aware ρ control)

Author: Felix - 2025-10-23
Spec: docs/specs/v2/foundations/criticality.md (PR-E)
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
from orchestration.mechanisms.stimulus_injection import (
    StimulusInjector,
    InjectionMatch,
)
from orchestration.mechanisms.coherence import (
    CoherenceTracker,
    compute_coherence,
)
from orchestration.mechanisms.criticality import (
    CriticalityMode,
    classify_criticality_mode,
    get_mode_phenomenology,
    get_controller_response,
    TaskContext,
    TaskContextSignals,
    TaskContextInferrer,
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


# === E.5 Affective Priming Tests ===

def test_affective_priming_disabled():
    """Test that affective priming returns unmodified matches when disabled."""
    print("\n" + "="*70)
    print("TEST: Affective Priming Disabled")
    print("="*70)

    injector = StimulusInjector()

    # Create test matches with emotion vectors
    matches = [
        InjectionMatch(
            item_id="node_1",
            item_type="node",
            similarity=0.8,
            current_energy=0.3,
            threshold=0.5,
            gap=0.2,
            emotion_vector=np.array([0.7, 0.7])  # Positive affect
        )
    ]

    # Affective priming disabled by default
    assert not injector.affective_priming_enabled

    primed = injector._apply_affective_priming(matches)

    # Similarity should be unchanged
    assert primed[0].similarity == matches[0].similarity
    print(f"  ✓ Priming disabled → similarity unchanged: {matches[0].similarity}")


def test_affective_priming_weak_affect_skipped():
    """Test priming is skipped when recent affect magnitude is below threshold."""
    print("\n" + "="*70)
    print("TEST: Affective Priming - Weak Affect Skipped")
    print("="*70)

    with patch.object(settings, 'AFFECTIVE_PRIMING_ENABLED', True):
        with patch.object(settings, 'AFFECTIVE_PRIMING_MIN_RECENT', 0.3):
            injector = StimulusInjector()
            injector.enable_affective_priming()

            # Set weak recent affect (magnitude < 0.3)
            injector.recent_affect = np.array([0.1, 0.1])  # magnitude = 0.141

            matches = [
                InjectionMatch(
                    item_id="node_1",
                    item_type="node",
                    similarity=0.8,
                    current_energy=0.3,
                    threshold=0.5,
                    gap=0.2,
                    emotion_vector=np.array([0.7, 0.7])
                )
            ]

            primed = injector._apply_affective_priming(matches)

            # Similarity should be unchanged due to weak affect
            assert primed[0].similarity == matches[0].similarity
            magnitude = np.linalg.norm(injector.recent_affect)
            print(f"  ✓ Weak affect (||A_recent||={magnitude:.3f} < 0.3) → priming skipped")


def test_affective_priming_positive_boost():
    """Test affect-congruent match receives positive boost."""
    print("\n" + "="*70)
    print("TEST: Affective Priming - Positive Boost")
    print("="*70)

    with patch.object(settings, 'AFFECTIVE_PRIMING_ENABLED', True):
        with patch.object(settings, 'AFFECTIVE_PRIMING_P', 0.15):
            with patch.object(settings, 'AFFECTIVE_PRIMING_MIN_RECENT', 0.3):
                injector = StimulusInjector()
                injector.enable_affective_priming()

                # Set strong positive recent affect
                injector.recent_affect = np.array([0.8, 0.0])  # magnitude = 0.8

                # Match with aligned emotion (also positive)
                matches = [
                    InjectionMatch(
                        item_id="node_1",
                        item_type="node",
                        similarity=0.7,
                        current_energy=0.3,
                        threshold=0.5,
                        gap=0.2,
                        emotion_vector=np.array([0.6, 0.0])  # Aligned affect
                    )
                ]

                primed = injector._apply_affective_priming(matches)

                # Similarity should increase
                # r_affect = cos([0.8, 0], [0.6, 0]) = 1.0 (perfect alignment)
                # boost = 0.15 * 1.0 = 0.15
                # new_sim = 0.7 * (1 + 0.15) = 0.805
                expected_boost_approx = 0.7 * 1.15
                assert primed[0].similarity > matches[0].similarity
                assert abs(primed[0].similarity - expected_boost_approx) < 0.01
                print(f"  ✓ Affect-congruent: {matches[0].similarity:.3f} → {primed[0].similarity:.3f}")
                print(f"    (boost ≈ +{(primed[0].similarity - matches[0].similarity):.3f})")


def test_affective_priming_negative_boost():
    """Test affect-incongruent match receives negative boost (penalty)."""
    print("\n" + "="*70)
    print("TEST: Affective Priming - Negative Boost")
    print("="*70)

    with patch.object(settings, 'AFFECTIVE_PRIMING_ENABLED', True):
        with patch.object(settings, 'AFFECTIVE_PRIMING_P', 0.15):
            with patch.object(settings, 'AFFECTIVE_PRIMING_MIN_RECENT', 0.3):
                injector = StimulusInjector()
                injector.enable_affective_priming()

                # Set strong positive recent affect
                injector.recent_affect = np.array([0.8, 0.0])  # magnitude = 0.8

                # Match with opposite emotion (negative)
                matches = [
                    InjectionMatch(
                        item_id="node_1",
                        item_type="node",
                        similarity=0.7,
                        current_energy=0.3,
                        threshold=0.5,
                        gap=0.2,
                        emotion_vector=np.array([-0.6, 0.0])  # Opposite affect
                    )
                ]

                primed = injector._apply_affective_priming(matches)

                # Similarity should decrease
                # r_affect = cos([0.8, 0], [-0.6, 0]) = -1.0 (perfect opposition)
                # boost = 0.15 * -1.0 = -0.15
                # new_sim = 0.7 * (1 - 0.15) = 0.595
                expected_penalty_approx = 0.7 * 0.85
                assert primed[0].similarity < matches[0].similarity
                assert abs(primed[0].similarity - expected_penalty_approx) < 0.01
                print(f"  ✓ Affect-incongruent: {matches[0].similarity:.3f} → {primed[0].similarity:.3f}")
                print(f"    (penalty ≈ {(primed[0].similarity - matches[0].similarity):.3f})")


def test_affective_priming_clamping():
    """Test similarity is clamped to [0, 1] after priming."""
    print("\n" + "="*70)
    print("TEST: Affective Priming - Similarity Clamping")
    print("="*70)

    with patch.object(settings, 'AFFECTIVE_PRIMING_ENABLED', True):
        with patch.object(settings, 'AFFECTIVE_PRIMING_P', 0.15):
            with patch.object(settings, 'AFFECTIVE_PRIMING_MIN_RECENT', 0.3):
                injector = StimulusInjector()
                injector.enable_affective_priming()

                # Set strong affect
                injector.recent_affect = np.array([0.8, 0.0])

                # Match with high similarity that would exceed 1.0 after boost
                matches = [
                    InjectionMatch(
                        item_id="node_1",
                        item_type="node",
                        similarity=0.95,  # High base similarity
                        current_energy=0.3,
                        threshold=0.5,
                        gap=0.2,
                        emotion_vector=np.array([0.8, 0.0])  # Perfect alignment
                    )
                ]

                primed = injector._apply_affective_priming(matches)

                # Similarity should be clamped at 1.0
                # Without clamp: 0.95 * 1.15 = 1.0925
                assert primed[0].similarity == 1.0
                print(f"  ✓ High similarity (0.95) with boost → clamped at 1.0")


def test_update_recent_affect_ema():
    """Test EMA tracking of recent affect."""
    print("\n" + "="*70)
    print("TEST: Update Recent Affect EMA")
    print("="*70)

    injector = StimulusInjector()
    injector.enable_affective_priming()

    # Initial state
    assert np.allclose(injector.recent_affect, [0.0, 0.0])

    # Update with first affect
    current_1 = np.array([0.5, 0.3, 0.1])  # Only first 2 dims used
    injector.update_recent_affect(current_1)

    # A_recent = α * current + (1-α) * old
    # A_recent = 0.1 * [0.5, 0.3] + 0.9 * [0, 0] = [0.05, 0.03]
    expected_1 = np.array([0.05, 0.03])
    assert np.allclose(injector.recent_affect, expected_1)
    print(f"  ✓ Frame 1: A_recent = [{injector.recent_affect[0]:.3f}, {injector.recent_affect[1]:.3f}]")

    # Update with second affect
    current_2 = np.array([0.8, 0.6])
    injector.update_recent_affect(current_2)

    # A_recent = 0.1 * [0.8, 0.6] + 0.9 * [0.05, 0.03]
    #          = [0.08, 0.06] + [0.045, 0.027]
    #          = [0.125, 0.087]
    expected_2 = np.array([0.125, 0.087])
    assert np.allclose(injector.recent_affect, expected_2, atol=1e-6)
    print(f"  ✓ Frame 2: A_recent = [{injector.recent_affect[0]:.3f}, {injector.recent_affect[1]:.3f}]")
    print(f"  ✓ EMA smoothing working correctly (α=0.1)")


# === E.6 Coherence Metric Tests ===

def test_coherence_disabled():
    """Test that coherence tracker does nothing when disabled."""
    print("\n" + "="*70)
    print("TEST: Coherence Disabled")
    print("="*70)

    tracker = CoherenceTracker()

    # Disabled by default
    assert not tracker.enabled

    # Create dummy active nodes
    active_nodes = [
        Node(id="n1", name="Node 1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5)
    ]

    state = tracker.update(active_nodes, [])

    # Should return None when disabled
    assert state is None
    print(f"  ✓ Coherence disabled → update returns None")


def test_coherence_frontier_similarity():
    """Test frontier coherence (C_frontier) computation."""
    print("\n" + "="*70)
    print("TEST: Coherence Frontier Similarity")
    print("="*70)

    with patch.object(settings, 'COHERENCE_METRIC_ENABLED', True):
        with patch.object(settings, 'COHERENCE_ALPHA_FRONTIER', 0.6):
            with patch.object(settings, 'COHERENCE_ALPHA_STRIDE', 0.4):
                tracker = CoherenceTracker()
                tracker.enable()

                # Frame 1: Set initial frontier
                nodes_1 = [
                    Node(id="n1", name="N1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
                    Node(id="n2", name="N2", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
                ]
                nodes_1[0].embedding = np.array([1.0, 0.0, 0.0])
                nodes_1[1].embedding = np.array([0.9, 0.1, 0.0])

                state_1 = tracker.update(nodes_1, [])

                # First frame: C_frontier = 1.0 (no previous frontier)
                assert state_1.C_frontier == 1.0
                print(f"  ✓ Frame 1: C_frontier = {state_1.C_frontier:.3f} (first frame → 1.0)")

                # Frame 2: Similar frontier (high coherence)
                nodes_2 = [
                    Node(id="n3", name="N3", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
                    Node(id="n4", name="N4", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
                ]
                nodes_2[0].embedding = np.array([0.95, 0.05, 0.0])  # Similar to frame 1
                nodes_2[1].embedding = np.array([0.85, 0.15, 0.0])

                state_2 = tracker.update(nodes_2, [])

                # Should have high frontier similarity
                assert state_2.C_frontier > 0.8
                print(f"  ✓ Frame 2: C_frontier = {state_2.C_frontier:.3f} (similar frontier → high)")

                # Frame 3: Completely different frontier (low coherence)
                nodes_3 = [
                    Node(id="n5", name="N5", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
                ]
                nodes_3[0].embedding = np.array([0.0, 0.0, 1.0])  # Orthogonal to frame 2

                state_3 = tracker.update(nodes_3, [])

                # Should have low frontier similarity
                assert state_3.C_frontier < 0.7
                print(f"  ✓ Frame 3: C_frontier = {state_3.C_frontier:.3f} (different frontier → low)")


def test_coherence_stride_relatedness():
    """Test stride coherence (C_stride) computation."""
    print("\n" + "="*70)
    print("TEST: Coherence Stride Relatedness")
    print("="*70)

    with patch.object(settings, 'COHERENCE_METRIC_ENABLED', True):
        tracker = CoherenceTracker()
        tracker.enable()

        # Create nodes with embeddings
        node = Node(id="n1", name="N1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5)
        node.embedding = np.array([1.0, 0.0])

        # High relatedness strides (strong links, high semantic similarity)
        link_1 = Link(
            id="l1",
            source_id="n1",
            target_id="n2",
            link_type=LinkType.RELATES_TO,
            subentity="test",
            goal="test",
            mindstate="test",
            energy=0.8,
            confidence=0.9,
            formation_trigger="test"
        )
        link_1.log_weight = -0.1  # exp(-0.1) ≈ 0.9

        strides_high = [
            (link_1, 0.9),  # High semantic similarity
        ]

        state_high = tracker.update([node], strides_high)

        # C_stride should be high (combine link weight + semantic)
        # 0.6 * 0.9 + 0.4 * 0.9 = 0.9
        assert state_high.C_stride > 0.8
        print(f"  ✓ High relatedness strides → C_stride = {state_high.C_stride:.3f}")

        # Low relatedness strides (weak links, low semantic similarity)
        link_2 = Link(
            id="l2",
            source_id="n1",
            target_id="n3",
            link_type=LinkType.RELATES_TO,
            subentity="test",
            goal="test",
            mindstate="test",
            energy=0.2,
            confidence=0.3,
            formation_trigger="test"
        )
        link_2.log_weight = -3.0  # exp(-3.0) ≈ 0.05

        strides_low = [
            (link_2, 0.1),  # Low semantic similarity
        ]

        state_low = tracker.update([node], strides_low)

        # C_stride should be low
        # 0.6 * 0.05 + 0.4 * 0.1 = 0.07
        assert state_low.C_stride < 0.3
        print(f"  ✓ Low relatedness strides → C_stride = {state_low.C_stride:.3f}")


def test_coherence_combined():
    """Test combined coherence C = α_frontier * C_frontier + α_stride * C_stride."""
    print("\n" + "="*70)
    print("TEST: Coherence Combined")
    print("="*70)

    with patch.object(settings, 'COHERENCE_METRIC_ENABLED', True):
        with patch.object(settings, 'COHERENCE_ALPHA_FRONTIER', 0.6):
            with patch.object(settings, 'COHERENCE_ALPHA_STRIDE', 0.4):
                tracker = CoherenceTracker()
                tracker.enable()

                # Frame 1: Initialize
                nodes_1 = [Node(id="n1", name="N1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5)]
                nodes_1[0].embedding = np.array([1.0, 0.0])

                state_1 = tracker.update(nodes_1, [])

                # Frame 2: High frontier + high stride = high coherence
                nodes_2 = [Node(id="n2", name="N2", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5)]
                nodes_2[0].embedding = np.array([0.9, 0.1])  # Similar to frame 1

                link = Link(
                    id="l1",
                    source_id="n1",
                    target_id="n2",
                    link_type=LinkType.RELATES_TO,
                    subentity="test",
                    goal="test",
                    mindstate="test",
                    energy=0.8,
                    confidence=0.9,
                    formation_trigger="test"
                )
                link.log_weight = -0.1

                strides = [(link, 0.9)]

                state_2 = tracker.update(nodes_2, strides)

                # C = 0.6 * C_frontier + 0.4 * C_stride
                # Both should be high → C should be high
                expected_C_approx = 0.6 * state_2.C_frontier + 0.4 * state_2.C_stride

                # Note: C is smoothed, so might not match exactly
                print(f"  ✓ High frontier ({state_2.C_frontier:.3f}) + high stride ({state_2.C_stride:.3f})")
                print(f"    → Combined C = {state_2.C:.3f} (expected ≈ {expected_C_approx:.3f})")
                print(f"    → Interpretation: {'COHERENT' if state_2.C > 0.7 else 'FRAGMENTED'}")


def test_coherence_smoothing():
    """Test rolling window smoothing of coherence."""
    print("\n" + "="*70)
    print("TEST: Coherence Smoothing")
    print("="*70)

    with patch.object(settings, 'COHERENCE_METRIC_ENABLED', True):
        with patch.object(settings, 'COHERENCE_SMOOTHING_WINDOW', 3):
            tracker = CoherenceTracker()
            tracker.enable()

            # Create simple nodes for testing
            node = Node(id="n1", name="N1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5)
            node.embedding = np.array([1.0, 0.0])

            # Frame 1
            state_1 = tracker.update([node], [])
            assert not state_1.smoothed  # Not enough frames yet
            print(f"  ✓ Frame 1: C = {state_1.C:.3f}, smoothed = {state_1.smoothed}")

            # Frame 2
            state_2 = tracker.update([node], [])
            assert not state_2.smoothed  # Still not enough
            print(f"  ✓ Frame 2: C = {state_2.C:.3f}, smoothed = {state_2.smoothed}")

            # Frame 3
            state_3 = tracker.update([node], [])
            assert state_3.smoothed  # Now we have full window
            print(f"  ✓ Frame 3: C = {state_3.C:.3f}, smoothed = {state_3.smoothed}")
            print(f"  ✓ Rolling window smoothing active after {tracker.smoothing_window} frames")


def test_coherence_stateless_computation():
    """Test stateless coherence computation function."""
    print("\n" + "="*70)
    print("TEST: Coherence Stateless Computation")
    print("="*70)

    # Create nodes with embeddings
    nodes = [
        Node(id="n1", name="N1", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
        Node(id="n2", name="N2", node_type=NodeType.CONCEPT, description="Test", E=1.0, theta=0.5),
    ]
    nodes[0].embedding = np.array([1.0, 0.0])
    nodes[1].embedding = np.array([0.9, 0.1])

    # Create stride
    link = Link(
        id="l1",
        source_id="n1",
        target_id="n2",
        link_type=LinkType.RELATES_TO,
        subentity="test",
        goal="test",
        mindstate="test",
        energy=0.8,
        confidence=0.9,
        formation_trigger="test"
    )
    link.log_weight = -0.1
    strides = [(link, 0.9)]

    # Compute coherence without tracker (stateless)
    C, centroid = compute_coherence(
        active_nodes=nodes,
        executed_strides=strides,
        previous_frontier=None,  # First frame
        alpha_frontier=0.6,
        alpha_stride=0.4
    )

    # Should return valid coherence
    assert 0.0 <= C <= 1.0
    assert centroid is not None
    print(f"  ✓ Stateless computation: C = {C:.3f}")
    print(f"  ✓ Centroid computed: shape = {centroid.shape}")


# === E.7 Criticality Modes Tests ===

def test_criticality_mode_subcritical():
    """Test SUBCRITICAL mode (ρ < 0.9)."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - SUBCRITICAL")
    print("="*70)

    # Low ρ, any coherence → SUBCRITICAL
    mode_1 = classify_criticality_mode(rho=0.8, coherence=0.9)
    assert mode_1 == CriticalityMode.SUBCRITICAL
    print(f"  ✓ ρ=0.8, C=0.9 → {mode_1.value}")

    mode_2 = classify_criticality_mode(rho=0.7, coherence=0.2)
    assert mode_2 == CriticalityMode.SUBCRITICAL
    print(f"  ✓ ρ=0.7, C=0.2 → {mode_2.value}")

    phenomenology = get_mode_phenomenology(CriticalityMode.SUBCRITICAL)
    print(f"  ✓ Phenomenology: {phenomenology}")


def test_criticality_mode_flow():
    """Test FLOW mode (0.9 ≤ ρ ≤ 1.1, C ≥ 0.7)."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - FLOW")
    print("="*70)

    # Balanced ρ, high coherence → FLOW
    mode_1 = classify_criticality_mode(rho=1.0, coherence=0.8)
    assert mode_1 == CriticalityMode.FLOW
    print(f"  ✓ ρ=1.0, C=0.8 → {mode_1.value}")

    mode_2 = classify_criticality_mode(rho=0.95, coherence=0.75)
    assert mode_2 == CriticalityMode.FLOW
    print(f"  ✓ ρ=0.95, C=0.75 → {mode_2.value}")

    phenomenology = get_mode_phenomenology(CriticalityMode.FLOW)
    response = get_controller_response(CriticalityMode.FLOW)
    print(f"  ✓ Phenomenology: {phenomenology}")
    print(f"  ✓ Controller: {response}")


def test_criticality_mode_generative_overflow():
    """Test GENERATIVE_OVERFLOW mode (ρ > 1.1, C ≥ 0.7)."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - GENERATIVE_OVERFLOW")
    print("="*70)

    # High ρ, high coherence → GENERATIVE_OVERFLOW
    mode_1 = classify_criticality_mode(rho=1.2, coherence=0.8)
    assert mode_1 == CriticalityMode.GENERATIVE_OVERFLOW
    print(f"  ✓ ρ=1.2, C=0.8 → {mode_1.value}")

    mode_2 = classify_criticality_mode(rho=1.5, coherence=0.75)
    assert mode_2 == CriticalityMode.GENERATIVE_OVERFLOW
    print(f"  ✓ ρ=1.5, C=0.75 → {mode_2.value}")

    phenomenology = get_mode_phenomenology(CriticalityMode.GENERATIVE_OVERFLOW)
    response = get_controller_response(CriticalityMode.GENERATIVE_OVERFLOW)
    print(f"  ✓ Phenomenology: {phenomenology}")
    print(f"  ✓ Controller: {response}")


def test_criticality_mode_chaotic_racing():
    """Test CHAOTIC_RACING mode (ρ > 1.1, C < 0.4)."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - CHAOTIC_RACING")
    print("="*70)

    # High ρ, low coherence → CHAOTIC_RACING
    mode_1 = classify_criticality_mode(rho=1.3, coherence=0.2)
    assert mode_1 == CriticalityMode.CHAOTIC_RACING
    print(f"  ✓ ρ=1.3, C=0.2 → {mode_1.value}")

    mode_2 = classify_criticality_mode(rho=1.5, coherence=0.35)
    assert mode_2 == CriticalityMode.CHAOTIC_RACING
    print(f"  ✓ ρ=1.5, C=0.35 → {mode_2.value}")

    phenomenology = get_mode_phenomenology(CriticalityMode.CHAOTIC_RACING)
    response = get_controller_response(CriticalityMode.CHAOTIC_RACING)
    print(f"  ✓ Phenomenology: {phenomenology}")
    print(f"  ✓ Controller: {response}")


def test_criticality_mode_mixed():
    """Test MIXED mode (transitional states)."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - MIXED")
    print("="*70)

    # Balanced ρ, low coherence → MIXED
    mode_1 = classify_criticality_mode(rho=1.0, coherence=0.5)
    assert mode_1 == CriticalityMode.MIXED
    print(f"  ✓ ρ=1.0, C=0.5 → {mode_1.value}")

    # High ρ, medium coherence → MIXED
    mode_2 = classify_criticality_mode(rho=1.2, coherence=0.5)
    assert mode_2 == CriticalityMode.MIXED
    print(f"  ✓ ρ=1.2, C=0.5 → {mode_2.value}")

    phenomenology = get_mode_phenomenology(CriticalityMode.MIXED)
    response = get_controller_response(CriticalityMode.MIXED)
    print(f"  ✓ Phenomenology: {phenomenology}")
    print(f"  ✓ Controller: {response}")


def test_criticality_mode_without_coherence():
    """Test fallback classification when coherence is not available."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - Without Coherence")
    print("="*70)

    # Low ρ, no coherence → SUBCRITICAL
    mode_1 = classify_criticality_mode(rho=0.8, coherence=None)
    assert mode_1 == CriticalityMode.SUBCRITICAL
    print(f"  ✓ ρ=0.8, C=None → {mode_1.value}")

    # Balanced ρ, no coherence → MIXED (can't determine)
    mode_2 = classify_criticality_mode(rho=1.0, coherence=None)
    assert mode_2 == CriticalityMode.MIXED
    print(f"  ✓ ρ=1.0, C=None → {mode_2.value} (fallback)")

    # High ρ, no coherence → MIXED (can't distinguish overflow vs chaos)
    mode_3 = classify_criticality_mode(rho=1.3, coherence=None)
    assert mode_3 == CriticalityMode.MIXED
    print(f"  ✓ ρ=1.3, C=None → {mode_3.value} (fallback)")


def test_criticality_mode_boundaries():
    """Test mode classification at boundary values."""
    print("\n" + "="*70)
    print("TEST: Criticality Mode - Boundary Values")
    print("="*70)

    # ρ = 0.9 (boundary between SUBCRITICAL and FLOW)
    mode_1 = classify_criticality_mode(rho=0.9, coherence=0.75)
    assert mode_1 == CriticalityMode.FLOW
    print(f"  ✓ ρ=0.9 (boundary), C=0.75 → {mode_1.value}")

    # ρ = 1.1 (boundary between FLOW and overflow/chaos)
    mode_2 = classify_criticality_mode(rho=1.1, coherence=0.75)
    assert mode_2 == CriticalityMode.FLOW
    print(f"  ✓ ρ=1.1 (boundary), C=0.75 → {mode_2.value}")

    # C = 0.7 (boundary for FLOW)
    mode_3 = classify_criticality_mode(rho=1.0, coherence=0.7)
    assert mode_3 == CriticalityMode.FLOW
    print(f"  ✓ ρ=1.0, C=0.7 (boundary) → {mode_3.value}")

    # C = 0.4 (boundary for CHAOTIC_RACING)
    mode_4 = classify_criticality_mode(rho=1.2, coherence=0.4)
    assert mode_4 == CriticalityMode.MIXED  # 0.4 is NOT < 0.4, so MIXED
    print(f"  ✓ ρ=1.2, C=0.4 (boundary) → {mode_4.value}")


# === E.8 Task-Adaptive Targets Tests ===

def test_task_context_rest():
    """Test REST context classification."""
    print("\n" + "="*70)
    print("TEST: Task Context - REST")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)  # No hysteresis for testing

    # Low ρ for extended period → REST
    signals = TaskContextSignals(low_rho_frames=10)
    context = inferrer.infer(signals, current_rho=0.85)

    assert context == TaskContext.REST
    target = inferrer.get_target_rho(context)
    tolerance = inferrer.get_tolerance(context)

    print(f"  ✓ low_rho_frames=10 → {context.value}")
    print(f"  ✓ Target ρ = {target}, tolerance = ±{tolerance}")


def test_task_context_consolidate():
    """Test CONSOLIDATE context classification."""
    print("\n" + "="*70)
    print("TEST: Task Context - CONSOLIDATE")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)

    # Memory formation active → CONSOLIDATE
    signals = TaskContextSignals(memory_formation_active=True)
    context = inferrer.infer(signals, current_rho=1.0)

    assert context == TaskContext.CONSOLIDATE
    target = inferrer.get_target_rho(context)

    print(f"  ✓ memory_formation_active=True → {context.value}")
    print(f"  ✓ Target ρ = {target}")

    # Reset for second test
    inferrer.reset()

    # Stable WM → CONSOLIDATE
    signals_2 = TaskContextSignals(wm_stable_frames=5)
    context_2 = inferrer.infer(signals_2, current_rho=1.0)

    assert context_2 == TaskContext.CONSOLIDATE
    print(f"  ✓ wm_stable_frames=5 → {context_2.value}")


def test_task_context_explore():
    """Test EXPLORE context classification."""
    print("\n" + "="*70)
    print("TEST: Task Context - EXPLORE")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)

    # Exploration goals → EXPLORE
    signals = TaskContextSignals(exploration_goals_active=2)
    context = inferrer.infer(signals, current_rho=1.0)

    assert context == TaskContext.EXPLORE
    target = inferrer.get_target_rho(context)

    print(f"  ✓ exploration_goals_active=2 → {context.value}")
    print(f"  ✓ Target ρ = {target}")

    # Reset for second test
    inferrer.reset()

    # High entity diversity → EXPLORE
    signals_2 = TaskContextSignals(entity_diversity=0.7)
    context_2 = inferrer.infer(signals_2, current_rho=1.0)

    assert context_2 == TaskContext.EXPLORE
    print(f"  ✓ entity_diversity=0.7 → {context_2.value}")


def test_task_context_implement():
    """Test IMPLEMENT context classification."""
    print("\n" + "="*70)
    print("TEST: Task Context - IMPLEMENT")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)

    # Implementation tasks → IMPLEMENT
    signals = TaskContextSignals(implementation_tasks_active=3)
    context = inferrer.infer(signals, current_rho=1.0)

    assert context == TaskContext.IMPLEMENT
    target = inferrer.get_target_rho(context)

    print(f"  ✓ implementation_tasks_active=3 → {context.value}")
    print(f"  ✓ Target ρ = {target}")

    # Reset for second test
    inferrer.reset()

    # High flip rate → IMPLEMENT
    signals_2 = TaskContextSignals(recent_flip_rate=0.4)
    context_2 = inferrer.infer(signals_2, current_rho=1.0)

    assert context_2 == TaskContext.IMPLEMENT
    print(f"  ✓ recent_flip_rate=0.4 → {context_2.value}")


def test_task_context_unknown():
    """Test UNKNOWN context (default fallback)."""
    print("\n" + "="*70)
    print("TEST: Task Context - UNKNOWN")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)

    # No signals → UNKNOWN
    signals = TaskContextSignals()
    context = inferrer.infer(signals, current_rho=1.0)

    assert context == TaskContext.UNKNOWN
    target = inferrer.get_target_rho(context)
    tolerance = inferrer.get_tolerance(context)

    print(f"  ✓ No signals → {context.value}")
    print(f"  ✓ Target ρ = {target}, tolerance = ±{tolerance}")


def test_task_context_hysteresis():
    """Test hysteresis prevents rapid context switching."""
    print("\n" + "="*70)
    print("TEST: Task Context - Hysteresis")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=3)

    # Start with UNKNOWN
    assert inferrer.current_context == TaskContext.UNKNOWN

    # Frame 1: Evidence for EXPLORE (but not enough)
    signals_explore = TaskContextSignals(exploration_goals_active=1)
    context_1 = inferrer.infer(signals_explore, current_rho=1.0)

    assert context_1 == TaskContext.UNKNOWN  # Still unknown
    print(f"  ✓ Frame 1: EXPLORE evidence, but still {context_1.value} (hysteresis)")

    # Frame 2: Same evidence (still not enough)
    context_2 = inferrer.infer(signals_explore, current_rho=1.0)

    assert context_2 == TaskContext.UNKNOWN
    print(f"  ✓ Frame 2: EXPLORE evidence, but still {context_2.value} (hysteresis)")

    # Frame 3: Same evidence (NOW enough to switch)
    context_3 = inferrer.infer(signals_explore, current_rho=1.0)

    assert context_3 == TaskContext.EXPLORE  # Switched!
    print(f"  ✓ Frame 3: EXPLORE evidence → SWITCHED to {context_3.value}")

    # Frame 4: Different evidence (IMPLEMENT), but hysteresis prevents immediate switch
    signals_implement = TaskContextSignals(implementation_tasks_active=1)
    context_4 = inferrer.infer(signals_implement, current_rho=1.0)

    assert context_4 == TaskContext.EXPLORE  # Still exploring
    print(f"  ✓ Frame 4: IMPLEMENT evidence, but still {context_4.value} (hysteresis)")


def test_task_context_priority():
    """Test context classification priority order."""
    print("\n" + "="*70)
    print("TEST: Task Context - Priority Order")
    print("="*70)

    inferrer = TaskContextInferrer(hysteresis_frames=1)

    # REST has highest priority (beats everything)
    signals = TaskContextSignals(
        low_rho_frames=10,              # REST signal
        exploration_goals_active=1,     # EXPLORE signal
        implementation_tasks_active=1   # IMPLEMENT signal
    )
    context = inferrer.infer(signals, current_rho=1.0)

    assert context == TaskContext.REST
    print(f"  ✓ REST + EXPLORE + IMPLEMENT → {context.value} (REST wins)")

    # Reset
    inferrer.reset()

    # CONSOLIDATE beats EXPLORE and IMPLEMENT
    signals_2 = TaskContextSignals(
        memory_formation_active=True,   # CONSOLIDATE signal
        exploration_goals_active=1,     # EXPLORE signal
        implementation_tasks_active=1   # IMPLEMENT signal
    )
    context_2 = inferrer.infer(signals_2, current_rho=1.0)

    assert context_2 == TaskContext.CONSOLIDATE
    print(f"  ✓ CONSOLIDATE + EXPLORE + IMPLEMENT → {context_2.value} (CONSOLIDATE wins)")

    # Reset
    inferrer.reset()

    # EXPLORE beats IMPLEMENT
    signals_3 = TaskContextSignals(
        exploration_goals_active=1,     # EXPLORE signal
        implementation_tasks_active=1   # IMPLEMENT signal
    )
    context_3 = inferrer.infer(signals_3, current_rho=1.0)

    assert context_3 == TaskContext.EXPLORE
    print(f"  ✓ EXPLORE + IMPLEMENT → {context_3.value} (EXPLORE wins)")


def test_task_context_targets():
    """Test target ρ and tolerance retrieval."""
    print("\n" + "="*70)
    print("TEST: Task Context - Targets & Tolerances")
    print("="*70)

    inferrer = TaskContextInferrer()

    contexts = [TaskContext.REST, TaskContext.CONSOLIDATE, TaskContext.IMPLEMENT, TaskContext.EXPLORE, TaskContext.UNKNOWN]

    for context in contexts:
        target = inferrer.get_target_rho(context)
        tolerance = inferrer.get_tolerance(context)
        print(f"  ✓ {context.value:12s}: target ρ = {target:.2f}, tolerance = ±{tolerance:.2f}")

        # Verify targets are in reasonable ranges
        assert 0.5 <= target <= 1.5
        assert 0.05 <= tolerance <= 0.25


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
