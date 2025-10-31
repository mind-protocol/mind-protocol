# -*- coding: utf-8 -*-
"""
Tests for Frame Loop Orchestration

Tests the FrameOrchestrator service that coordinates consciousness frames.

Author: Felix "Core Consciousness Engineer" + Ada "Bridgekeeper"
Created: 2025-10-31
Phase: Migration Phase 3 - Frame Loop Orchestration
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

# Add parent to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from consciousness.engine.services.frame_loop import (
    FrameOrchestrator,
    FrameResult,
    Stimulus,
)
from consciousness.engine.domain.state import EngineState, NodeActivation


# === Test Fixtures ===


@dataclass
class MockNode:
    """Mock node for testing."""
    id: str
    E: float  # Energy
    outgoing_links: list
    incoming_links: list

    def is_active(self) -> bool:
        return self.E >= 0.5


@dataclass
class MockLink:
    """Mock link for testing."""
    source: 'MockNode'
    target: 'MockNode'
    weight: float = 1.0


@dataclass
class MockGraph:
    """Mock graph for testing."""
    nodes: dict  # node_id -> MockNode


@dataclass
class MockConfig:
    """Mock config for testing."""
    entity_id: str = "test_engine"
    tick_interval_ms: float = 100.0
    max_energy: float = 100.0


def create_test_graph(num_nodes: int = 10, active_ratio: float = 0.5) -> MockGraph:
    """Create a test graph with specified properties."""
    nodes = {}

    for i in range(num_nodes):
        # Make some nodes active (E >= 0.5), others inactive
        energy = 0.7 if i < int(num_nodes * active_ratio) else 0.3
        node = MockNode(
            id=f"node_{i}",
            E=energy,
            outgoing_links=[],
            incoming_links=[]
        )
        nodes[node.id] = node

    # Create some links between nodes
    for i in range(num_nodes - 1):
        source = nodes[f"node_{i}"]
        target = nodes[f"node_{i+1}"]
        link = MockLink(source=source, target=target)
        source.outgoing_links.append(link)
        target.incoming_links.append(link)

    return MockGraph(nodes=nodes)


def create_test_state(graph: MockGraph, tick_count: int = 0) -> EngineState:
    """Create a test EngineState from a mock graph."""
    config = MockConfig()

    # Project nodes to NodeActivation
    nodes = []
    total_energy = 0.0
    active_count = 0

    for node in graph.nodes.values():
        energy = node.E
        normalized = energy / config.max_energy
        active = node.is_active()

        nodes.append(NodeActivation(
            node_id=node.id,
            energy=energy,
            normalized_energy=normalized,
            active=active
        ))

        total_energy += energy
        if active:
            active_count += 1

    # Handle empty graph to avoid division by zero
    num_nodes = len(graph.nodes)
    normalized_energy = total_energy / (config.max_energy * num_nodes) if num_nodes > 0 else 0.0

    return EngineState(
        entity_id=config.entity_id,
        tick=tick_count,
        tick_interval_ms=config.tick_interval_ms,
        total_nodes=num_nodes,
        active_nodes=active_count,
        global_energy=total_energy,
        normalized_energy=normalized_energy,
        last_tick_time=datetime.now(),
        observed_at=datetime.now(),
        branching_ratio=None,
        nodes=tuple(nodes),
    )


# Add graph attribute to state for frame execution
class StateWithGraph(EngineState):
    """Extended state with graph attribute for testing."""
    def __init__(self, *args, graph=None, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(self, 'graph', graph)


# === Tests ===


def test_frame_execution_basic():
    """Test basic frame execution."""
    # Setup
    graph = create_test_graph(num_nodes=10, active_ratio=0.5)
    state = create_test_state(graph, tick_count=0)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    orchestrator = FrameOrchestrator(graph_port=graph_port, entity_id="test")

    # Execute
    result = orchestrator.execute_frame(
        state,
        stimuli=None,
        emit_telemetry=False,
        persist_state=False
    )

    # Verify
    assert isinstance(result, FrameResult)
    assert result.state.tick == state.tick + 1  # Tick incremented
    assert len(result.active_nodes) == 5  # 50% of 10 nodes
    assert result.total_energy > 0
    assert result.average_energy > 0
    assert result.telemetry_emitted is False
    assert result.persistence_saved is False


def test_state_transitions_immutable():
    """Test that state transitions are immutable."""
    # Setup
    graph = create_test_graph(num_nodes=5)
    state = create_test_state(graph, tick_count=10)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    orchestrator = FrameOrchestrator(graph_port=graph_port)

    # Execute
    result = orchestrator.execute_frame(state, emit_telemetry=False)

    # Verify immutability
    assert state.tick == 10  # Original unchanged
    assert result.state.tick == 11  # New state incremented
    assert id(state) != id(result.state)  # Different objects


def test_telemetry_emitted():
    """Test that telemetry is emitted when enabled."""
    # Setup
    graph = create_test_graph(num_nodes=10)
    state = create_test_state(graph, tick_count=5)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    telemetry_port = Mock()
    orchestrator = FrameOrchestrator(
        graph_port=graph_port,
        telemetry_port=telemetry_port
    )

    # Execute
    result = orchestrator.execute_frame(
        state,
        emit_telemetry=True,
        persist_state=False
    )

    # Verify telemetry
    assert result.telemetry_emitted is True
    telemetry_port.publish.assert_called_once()

    call_args = telemetry_port.publish.call_args
    event_name = call_args[0][0]
    payload = call_args[0][1]

    assert event_name == "engine.frame.complete"
    assert "frame" in payload
    assert "tick_count" in payload
    assert "active_nodes" in payload
    assert payload["tick_count"] == 6  # tick + 1


def test_persistence_saved():
    """Test that state is persisted when enabled."""
    # Setup
    graph = create_test_graph(num_nodes=10)
    state = create_test_state(graph, tick_count=3)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    persistence_port = Mock()
    orchestrator = FrameOrchestrator(
        graph_port=graph_port,
        persistence_port=persistence_port,
        entity_id="test_entity"
    )

    # Execute
    result = orchestrator.execute_frame(
        state,
        emit_telemetry=False,
        persist_state=True
    )

    # Verify persistence
    assert result.persistence_saved is True
    persistence_port.save_state.assert_called_once()

    call_args = persistence_port.save_state.call_args
    entity_id = call_args[0][0]
    saved_state = call_args[0][1]

    assert entity_id == "test_entity"
    assert saved_state.tick == 4  # New state


def test_activation_threshold():
    """Test that activation threshold affects active node count."""
    # Setup
    graph = create_test_graph(num_nodes=10, active_ratio=0.5)
    state = create_test_state(graph, tick_count=0)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    orchestrator = FrameOrchestrator(graph_port=graph_port)

    # Execute with different thresholds
    result_low = orchestrator.execute_frame(
        state,
        activation_threshold=0.1,  # Low threshold
        emit_telemetry=False
    )

    result_high = orchestrator.execute_frame(
        state,
        activation_threshold=0.9,  # High threshold
        emit_telemetry=False
    )

    # Verify threshold affects selection
    assert len(result_low.active_nodes) >= len(result_high.active_nodes)


def test_multiple_frames():
    """Test executing multiple frames sequentially."""
    # Setup
    graph = create_test_graph(num_nodes=10)
    state = create_test_state(graph, tick_count=0)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    orchestrator = FrameOrchestrator(graph_port=graph_port)

    # Execute multiple frames
    result = orchestrator.execute_frames(
        state,
        num_frames=5,
        emit_telemetry=False,
        persist_every_n=0
    )

    # Verify tick progression
    assert result.state.tick == 5  # 0 + 5 frames


def test_periodic_persistence():
    """Test periodic state persistence."""
    # Setup
    graph = create_test_graph(num_nodes=10)
    state = create_test_state(graph, tick_count=0)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    persistence_port = Mock()
    orchestrator = FrameOrchestrator(
        graph_port=graph_port,
        persistence_port=persistence_port
    )

    # Execute 10 frames with persistence every 3
    result = orchestrator.execute_frames(
        state,
        num_frames=10,
        emit_telemetry=False,
        persist_every_n=3
    )

    # Verify persistence called at frames 3, 6, 9 (3 times)
    assert persistence_port.save_state.call_count == 3


def test_empty_graph():
    """Test frame execution with empty graph."""
    # Setup
    graph = MockGraph(nodes={})
    state = create_test_state(graph, tick_count=0)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    orchestrator = FrameOrchestrator(graph_port=graph_port)

    # Execute
    result = orchestrator.execute_frame(state, emit_telemetry=False)

    # Verify graceful handling
    assert len(result.active_nodes) == 0
    assert len(result.frontier_nodes) == 0
    assert result.total_energy == 0.0
    assert result.average_energy == 0.0


def test_frame_counter():
    """Test internal frame counter."""
    # Setup
    graph = create_test_graph(num_nodes=5)
    state = create_test_state(graph)
    state = StateWithGraph(**state.__dict__, graph=graph)

    graph_port = Mock()
    telemetry_port = Mock()
    orchestrator = FrameOrchestrator(
        graph_port=graph_port,
        telemetry_port=telemetry_port
    )

    # Execute multiple frames
    orchestrator.execute_frame(state, emit_telemetry=True)
    orchestrator.execute_frame(state, emit_telemetry=True)
    orchestrator.execute_frame(state, emit_telemetry=True)

    # Check frame counter in telemetry
    last_call = telemetry_port.publish.call_args_list[-1]
    payload = last_call[0][1]
    assert payload["frame"] == 3

    # Reset and verify
    orchestrator.reset_frame_count()
    orchestrator.execute_frame(state, emit_telemetry=True)

    last_call = telemetry_port.publish.call_args_list[-1]
    payload = last_call[0][1]
    assert payload["frame"] == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
