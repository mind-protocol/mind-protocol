# ctx_runtime.md
**Generated:** 2025-10-24T21:13:06
---

## >>> BEGIN orchestration/tests/test_consciousness_engine_v2.py
<!-- mtime: 2025-10-22T21:44:26; size: 9945 -->

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
