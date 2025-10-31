#!/usr/bin/env python3
"""
Tests for Energy Dynamics (Phase 1)

Tests pure energy calculation functions in consciousness/engine/domain/energy.py

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Phase: Migration Phase 1 - Energy Dynamics
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from consciousness.engine.domain.energy import (
    clamp_energy,
    normalize_energy,
    compute_total_energy,
    compute_active_nodes,
    compute_average_energy,
    apply_energy_delta,
    compute_energy_ratio,
    compute_energy_statistics,
)


# === Mock Objects for Testing ===


class MockNode:
    """Mock node for testing."""
    def __init__(self, node_id: str, energy: float):
        self.id = node_id
        self.E = energy
        self.energy_runtime = energy

    def is_active(self):
        return self.E > 0.5


class MockGraph:
    """Mock graph for testing."""
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.id] = node


# === Tests ===


def test_clamp_energy():
    """Test energy clamping to valid range."""
    print("=== Test: clamp_energy() ===")

    # Normal case
    assert clamp_energy(50.0, 0.0, 100.0) == 50.0

    # Clamp at max
    assert clamp_energy(150.0, 0.0, 100.0) == 100.0

    # Clamp at min
    assert clamp_energy(-10.0, 0.0, 100.0) == 0.0

    # Edge cases
    assert clamp_energy(0.0, 0.0, 100.0) == 0.0
    assert clamp_energy(100.0, 0.0, 100.0) == 100.0

    print("✅ clamp_energy() works correctly")
    print()


def test_normalize_energy():
    """Test energy normalization to [0, 1]."""
    print("=== Test: normalize_energy() ===")

    assert normalize_energy(0.0, 100.0) == 0.0
    assert normalize_energy(50.0, 100.0) == 0.5
    assert normalize_energy(100.0, 100.0) == 1.0
    assert normalize_energy(25.0, 100.0) == 0.25

    # Edge case: max_energy = 0
    assert normalize_energy(50.0, 0.0) == 0.0

    print("✅ normalize_energy() works correctly")
    print()


def test_compute_total_energy():
    """Test total energy computation across graph."""
    print("=== Test: compute_total_energy() ===")

    graph = MockGraph()
    graph.add_node(MockNode("a", 50.0))
    graph.add_node(MockNode("b", 30.0))
    graph.add_node(MockNode("c", 20.0))

    total = compute_total_energy(graph)
    assert total == 100.0

    print(f"✅ Total energy: {total} (expected: 100.0)")
    print()


def test_compute_active_nodes():
    """Test active node counting."""
    print("=== Test: compute_active_nodes() ===")

    graph = MockGraph()
    graph.add_node(MockNode("a", 50.0))   # Active (> 0.5)
    graph.add_node(MockNode("b", 0.3))    # Inactive
    graph.add_node(MockNode("c", 75.0))   # Active
    graph.add_node(MockNode("d", 0.6))    # Active

    active_count = compute_active_nodes(graph, threshold=0.5)
    assert active_count == 3

    print(f"✅ Active nodes: {active_count} (expected: 3)")
    print()


def test_compute_average_energy():
    """Test average energy computation."""
    print("=== Test: compute_average_energy() ===")

    graph = MockGraph()
    graph.add_node(MockNode("a", 50.0))
    graph.add_node(MockNode("b", 30.0))
    graph.add_node(MockNode("c", 40.0))

    average = compute_average_energy(graph)
    assert average == 40.0

    # Empty graph
    empty_graph = MockGraph()
    assert compute_average_energy(empty_graph) == 0.0

    print(f"✅ Average energy: {average} (expected: 40.0)")
    print()


def test_apply_energy_delta():
    """Test energy delta application with clamping."""
    print("=== Test: apply_energy_delta() ===")

    # Normal case
    assert apply_energy_delta(50.0, 20.0, 0.0, 100.0) == 70.0

    # Clamp at max
    assert apply_energy_delta(50.0, 60.0, 0.0, 100.0) == 100.0

    # Clamp at min
    assert apply_energy_delta(50.0, -60.0, 0.0, 100.0) == 0.0

    # Negative delta (decay)
    assert apply_energy_delta(50.0, -10.0, 0.0, 100.0) == 40.0

    print("✅ apply_energy_delta() works correctly")
    print()


def test_compute_energy_ratio():
    """Test energy ratio computation."""
    print("=== Test: compute_energy_ratio() ===")

    assert compute_energy_ratio(0.0, 100.0) == 0.0
    assert compute_energy_ratio(50.0, 100.0) == 0.5
    assert compute_energy_ratio(100.0, 100.0) == 1.0
    assert compute_energy_ratio(75.0, 100.0) == 0.75

    print("✅ compute_energy_ratio() works correctly")
    print()


def test_compute_energy_statistics():
    """Test comprehensive energy statistics."""
    print("=== Test: compute_energy_statistics() ===")

    graph = MockGraph()
    graph.add_node(MockNode("a", 50.0))
    graph.add_node(MockNode("b", 75.0))
    graph.add_node(MockNode("c", 25.0))
    graph.add_node(MockNode("d", 0.3))  # Inactive

    stats = compute_energy_statistics(graph, max_energy=100.0)

    assert stats["total_energy"] == 150.3
    assert stats["average_energy"] == 37.575
    assert stats["total_nodes"] == 4
    assert stats["active_nodes"] == 3  # a, b, c (> 0.5)
    assert stats["max_node_energy"] == 75.0
    assert stats["min_node_energy"] == 0.3

    print(f"✅ Energy statistics:")
    print(f"   Total: {stats['total_energy']}")
    print(f"   Average: {stats['average_energy']}")
    print(f"   Active: {stats['active_nodes']}/{stats['total_nodes']}")
    print(f"   Normalized: {stats['normalized_energy']:.3f}")
    print()


def test_empty_graph():
    """Test functions handle empty graph gracefully."""
    print("=== Test: Empty Graph Handling ===")

    graph = MockGraph()

    assert compute_total_energy(graph) == 0.0
    assert compute_average_energy(graph) == 0.0
    assert compute_active_nodes(graph) == 0

    stats = compute_energy_statistics(graph)
    assert stats["total_energy"] == 0.0
    assert stats["total_nodes"] == 0

    print("✅ Empty graph handled gracefully")
    print()


def run_all_tests():
    """Run all energy dynamics tests."""
    print("=" * 70)
    print("ENERGY DYNAMICS TESTS - Phase 1")
    print("=" * 70)
    print()

    tests = [
        test_clamp_energy,
        test_normalize_energy,
        test_compute_total_energy,
        test_compute_active_nodes,
        test_compute_average_energy,
        test_apply_energy_delta,
        test_compute_energy_ratio,
        test_compute_energy_statistics,
        test_empty_graph,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED:")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
