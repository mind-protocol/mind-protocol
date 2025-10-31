#!/usr/bin/env python3
"""
Tests for Spreading Activation (Phase 2)

Tests pure activation functions in consciousness/engine/domain/activation.py

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Phase: Migration Phase 2 - Spreading Activation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from consciousness.engine.domain.activation import (
    select_active_nodes,
    compute_frontier,
    compute_neighbors,
    compute_n_hop_neighbors,
    compute_activation_distances,
    filter_by_activation_strength,
    compute_activation_statistics,
)


# === Mock Objects for Testing ===


class MockLink:
    """Mock link for testing."""
    def __init__(self, source, target):
        self.source = source
        self.target = target


class MockNode:
    """Mock node for testing."""
    def __init__(self, node_id: str, energy: float):
        self.id = node_id
        self.E = energy
        self.outgoing_links = []
        self.incoming_links = []

    def add_outgoing(self, target):
        """Add outgoing link to target node."""
        link = MockLink(self, target)
        self.outgoing_links.append(link)
        target.incoming_links.append(link)


class MockGraph:
    """Mock graph for testing."""
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.id] = node

    def connect(self, source_id, target_id):
        """Create link from source to target."""
        source = self.nodes[source_id]
        target = self.nodes[target_id]
        source.add_outgoing(target)


# === Tests ===


def test_select_active_nodes():
    """Test active node selection by threshold."""
    print("=== Test: select_active_nodes() ===")

    graph = MockGraph()
    graph.add_node(MockNode("a", 0.8))  # Active
    graph.add_node(MockNode("b", 0.3))  # Inactive
    graph.add_node(MockNode("c", 0.6))  # Active
    graph.add_node(MockNode("d", 0.5))  # Active (exactly at threshold)

    active = select_active_nodes(graph, threshold=0.5)

    assert "a" in active
    assert "b" not in active
    assert "c" in active
    assert "d" in active
    assert len(active) == 3

    print(f"✅ Active nodes: {sorted(active)} (expected: a, c, d)")
    print()


def test_compute_frontier():
    """Test frontier computation (1-hop neighbors of active)."""
    print("=== Test: compute_frontier() ===")

    # Create graph:  a → b → c
    #                ↓
    #                d
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.9))  # Active
    graph.add_node(MockNode("b", 0.2))  # Inactive (frontier)
    graph.add_node(MockNode("c", 0.1))  # Inactive
    graph.add_node(MockNode("d", 0.3))  # Inactive (frontier)

    graph.connect("a", "b")
    graph.connect("a", "d")
    graph.connect("b", "c")

    active = {"a"}
    frontier = compute_frontier(graph, active, exclude_active=True)

    assert "b" in frontier
    assert "d" in frontier
    assert "a" not in frontier  # Excluded (already active)
    assert "c" not in frontier  # 2 hops away
    assert len(frontier) == 2

    print(f"✅ Frontier: {sorted(frontier)} (expected: b, d)")
    print()


def test_compute_neighbors():
    """Test direct neighbor computation."""
    print("=== Test: compute_neighbors() ===")

    # Create graph:  a → b → c
    #                ↓
    #                d
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.5))
    graph.add_node(MockNode("b", 0.5))
    graph.add_node(MockNode("c", 0.5))
    graph.add_node(MockNode("d", 0.5))

    graph.connect("a", "b")
    graph.connect("a", "d")
    graph.connect("b", "c")

    # Outgoing neighbors of a
    neighbors_a = compute_neighbors(graph, "a", direction="outgoing")
    assert neighbors_a == {"b", "d"}

    # Incoming neighbors of b
    neighbors_b_in = compute_neighbors(graph, "b", direction="incoming")
    assert neighbors_b_in == {"a"}

    # Both directions for b
    neighbors_b_both = compute_neighbors(graph, "b", direction="both")
    assert neighbors_b_both == {"a", "c"}

    print("✅ compute_neighbors() works correctly")
    print(f"   a→: {sorted(neighbors_a)}")
    print(f"   →b: {sorted(neighbors_b_in)}")
    print(f"   b↔: {sorted(neighbors_b_both)}")
    print()


def test_compute_n_hop_neighbors():
    """Test n-hop neighbor computation (BFS)."""
    print("=== Test: compute_n_hop_neighbors() ===")

    # Create graph:  a → b → c → d
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.5))
    graph.add_node(MockNode("b", 0.5))
    graph.add_node(MockNode("c", 0.5))
    graph.add_node(MockNode("d", 0.5))

    graph.connect("a", "b")
    graph.connect("b", "c")
    graph.connect("c", "d")

    hops = compute_n_hop_neighbors(graph, "a", max_hops=3)

    assert hops[0] == {"a"}
    assert hops[1] == {"b"}
    assert hops[2] == {"c"}
    assert hops[3] == {"d"}

    print("✅ N-hop neighbors computed correctly")
    print(f"   0-hop: {sorted(hops[0])}")
    print(f"   1-hop: {sorted(hops[1])}")
    print(f"   2-hop: {sorted(hops[2])}")
    print(f"   3-hop: {sorted(hops[3])}")
    print()


def test_compute_activation_distances():
    """Test minimum distance computation from active set."""
    print("=== Test: compute_activation_distances() ===")

    # Create graph:  a → b → c → d
    #                ↓
    #                e
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.9))  # Active
    graph.add_node(MockNode("b", 0.2))
    graph.add_node(MockNode("c", 0.1))
    graph.add_node(MockNode("d", 0.1))
    graph.add_node(MockNode("e", 0.2))

    graph.connect("a", "b")
    graph.connect("b", "c")
    graph.connect("c", "d")
    graph.connect("a", "e")

    active = {"a"}
    distances = compute_activation_distances(graph, active, max_distance=3)

    assert distances["a"] == 0  # Active
    assert distances["b"] == 1  # 1-hop
    assert distances["e"] == 1  # 1-hop (other branch)
    assert distances["c"] == 2  # 2-hop
    assert distances["d"] == 3  # 3-hop

    print("✅ Activation distances computed correctly")
    print(f"   Distances: {distances}")
    print()


def test_filter_by_activation_strength():
    """Test filtering nodes by activation strength."""
    print("=== Test: filter_by_activation_strength() ===")

    # Create graph:  a(0.9) → b(0.6) → c(0.3)
    #                ↓
    #                d(0.7)
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.9))  # Active
    graph.add_node(MockNode("b", 0.6))  # Strong, 1-hop
    graph.add_node(MockNode("c", 0.3))  # Weak, 2-hop
    graph.add_node(MockNode("d", 0.7))  # Strong, 1-hop

    graph.connect("a", "b")
    graph.connect("b", "c")
    graph.connect("a", "d")

    candidates = {"b", "c", "d"}
    active = {"a"}

    # Filter: min_energy=0.5, max_distance=1
    strong = filter_by_activation_strength(
        graph,
        candidates,
        min_energy=0.5,
        max_distance_from_active=1,
        active_nodes=active
    )

    assert "b" in strong  # Energy 0.6, distance 1 ✓
    assert "d" in strong  # Energy 0.7, distance 1 ✓
    assert "c" not in strong  # Energy 0.3 (too low) ✗
    assert len(strong) == 2

    print(f"✅ Strong nodes: {sorted(strong)} (expected: b, d)")
    print()


def test_compute_activation_statistics():
    """Test comprehensive activation statistics."""
    print("=== Test: compute_activation_statistics() ===")

    # Create graph with clear active/frontier structure
    graph = MockGraph()
    graph.add_node(MockNode("a", 0.9))  # Active
    graph.add_node(MockNode("b", 0.8))  # Active
    graph.add_node(MockNode("c", 0.3))  # Frontier
    graph.add_node(MockNode("d", 0.2))  # Frontier
    graph.add_node(MockNode("e", 0.1))  # Inactive (2-hop)

    graph.connect("a", "c")
    graph.connect("b", "d")
    graph.connect("c", "e")

    stats = compute_activation_statistics(graph, threshold=0.5)

    assert stats["active_count"] == 2  # a, b
    assert stats["frontier_count"] == 2  # c, d
    assert stats["total_nodes"] == 5
    assert stats["activation_ratio"] == 2 / 5  # 0.4
    assert stats["frontier_to_active_ratio"] == 2 / 2  # 1.0

    print("✅ Activation statistics:")
    print(f"   Active: {stats['active_count']}/{stats['total_nodes']}")
    print(f"   Frontier: {stats['frontier_count']}")
    print(f"   Activation ratio: {stats['activation_ratio']:.2f}")
    print(f"   Frontier/Active: {stats['frontier_to_active_ratio']:.2f}")
    print()


def test_empty_graph():
    """Test functions handle empty graph gracefully."""
    print("=== Test: Empty Graph Handling ===")

    graph = MockGraph()

    active = select_active_nodes(graph)
    assert len(active) == 0

    frontier = compute_frontier(graph, set())
    assert len(frontier) == 0

    neighbors = compute_neighbors(graph, "nonexistent")
    assert len(neighbors) == 0

    distances = compute_activation_distances(graph, set())
    assert len(distances) == 0

    print("✅ Empty graph handled gracefully")
    print()


def run_all_tests():
    """Run all activation tests."""
    print("=" * 70)
    print("SPREADING ACTIVATION TESTS - Phase 2")
    print("=" * 70)
    print()

    tests = [
        test_select_active_nodes,
        test_compute_frontier,
        test_compute_neighbors,
        test_compute_n_hop_neighbors,
        test_compute_activation_distances,
        test_filter_by_activation_strength,
        test_compute_activation_statistics,
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
