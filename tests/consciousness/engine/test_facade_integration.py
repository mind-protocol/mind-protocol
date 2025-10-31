#!/usr/bin/env python3
"""
Integration tests for Engine Facade with Legacy ConsciousnessEngineV2

Tests:
  1. Facade initialization with legacy engine
  2. Snapshot generation from legacy engine state
  3. Plan tick with scheduler decision
  4. Intent dispatch through GraphPort
  5. Fallback behavior when facade unavailable
  6. Backward compatibility

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Purpose: Verify PR #2 facade integration doesn't break existing engine
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock
from typing import Any, Mapping, Sequence

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from consciousness.engine import (
    Engine as EngineFacade,
    EngineConfig,
    EngineState,
    GraphPort,
    TelemetryPort
)
from consciousness.engine.domain.state import build_engine_state, NodeActivation
from consciousness.engine.services.scheduler import plan_next_tick, SchedulerDecision


def create_mock_legacy_engine(entity_id="test_citizen", energy=50.0, tick_count=5):
    """Helper to create properly mocked legacy engine."""
    legacy_engine = type('LegacyEngine', (), {})()
    legacy_engine.tick_count = tick_count
    legacy_engine.last_tick_time = datetime.now()

    # Mock node
    node = type('Node', (), {})()
    node.id = "test_node"
    node.E = energy
    node.is_active = lambda: energy > 0.5

    # Mock graph
    mock_graph = type('Graph', (), {})()
    mock_graph.nodes = {"test_node": node}
    legacy_engine.graph = mock_graph

    # Mock config with REAL values (not Mock objects)
    config = type('Config', (), {})()
    config.entity_id = entity_id
    config.tick_interval_ms = 100.0
    config.max_energy = 100.0
    legacy_engine.config = config

    return legacy_engine


def test_engine_config_from_legacy():
    """Test EngineConfig can be created from legacy engine config."""
    print("=== Test 1: EngineConfig.from_legacy() ===")

    # Mock legacy config with proper values (not Mock objects)
    legacy_config = type('LegacyConfig', (), {})()
    legacy_config.entity_id = "test_citizen"
    legacy_config.tick_interval_ms = 150.0
    legacy_config.max_energy = 200.0

    # Convert to facade config
    facade_config = EngineConfig.from_legacy(legacy_config)

    assert facade_config.entity_id == "test_citizen"
    assert facade_config.tick_interval_ms == 150.0
    assert facade_config.max_energy == 200.0

    print("✅ EngineConfig.from_legacy() works correctly")
    print(f"   Config: entity_id={facade_config.entity_id}, interval={facade_config.tick_interval_ms}ms")
    print()


def test_engine_config_from_none():
    """Test EngineConfig handles None legacy config (fallback)."""
    print("=== Test 2: EngineConfig.from_legacy(None) ===")

    # None should give default config
    facade_config = EngineConfig.from_legacy(None)

    assert facade_config.entity_id == "consciousness_engine"  # Default
    assert facade_config.tick_interval_ms == 100.0  # Default
    assert facade_config.max_energy == 100.0  # Default

    print("✅ EngineConfig.from_legacy(None) uses defaults")
    print(f"   Config: entity_id={facade_config.entity_id}")
    print()


def test_build_engine_state():
    """Test build_engine_state creates immutable snapshot."""
    print("=== Test 3: build_engine_state() ===")

    # Mock graph with nodes
    mock_graph = Mock()

    # Create mock nodes with energy
    node1 = Mock()
    node1.id = "node_1"
    node1.E = 75.0
    node1.is_active = lambda: True

    node2 = Mock()
    node2.id = "node_2"
    node2.E = 25.0
    node2.is_active = lambda: False

    mock_graph.nodes = {"node_1": node1, "node_2": node2}

    # Mock config
    config = EngineConfig(entity_id="test", max_energy=100.0)

    # Build state
    now = datetime.now()
    state = build_engine_state(
        graph=mock_graph,
        tick_count=10,
        last_tick_time=now,
        observed_at=now,
        config=config,
        branching_state={"branching_ratio": 0.75}
    )

    assert isinstance(state, EngineState)
    assert state.entity_id == "test"
    assert state.tick == 10
    assert state.total_nodes == 2
    assert state.active_nodes == 1
    assert state.global_energy == 50.0  # Average of 75 and 25
    assert state.branching_ratio == 0.75
    assert len(state.nodes) == 2

    # Verify immutability
    assert isinstance(state.nodes, tuple)
    assert isinstance(state.nodes[0], NodeActivation)

    print("✅ build_engine_state() creates correct immutable snapshot")
    print(f"   State: {state.total_nodes} nodes, {state.active_nodes} active, energy={state.global_energy:.1f}")
    print()


def test_scheduler_decision():
    """Test plan_next_tick generates correct intents."""
    print("=== Test 4: plan_next_tick() Scheduler ===")

    # Create state with HIGH energy (should trigger alert)
    state = EngineState(
        entity_id="test",
        tick=5,
        tick_interval_ms=100.0,
        total_nodes=10,
        active_nodes=8,
        global_energy=90.0,
        normalized_energy=0.90,  # Above 0.85 threshold
        last_tick_time=datetime.now(),
        observed_at=datetime.now(),
        branching_ratio=0.8,
        nodes=tuple()
    )

    # Plan tick
    decision = plan_next_tick(state)

    assert isinstance(decision, SchedulerDecision)
    assert decision.state == state
    assert len(decision.intents) == 1  # Should have high energy alert

    intent = decision.intents[0]
    assert intent["type"] == "telemetry.emit"
    assert intent["payload"]["event"] == "engine.alert.high_energy"
    assert intent["payload"]["data"]["normalized_energy"] == 0.90

    print("✅ plan_next_tick() generates high energy alert")
    print(f"   Intent: {intent['payload']['event']}")
    print()

    # Test LOW energy (no alert)
    state_low = EngineState(
        entity_id="test",
        tick=5,
        tick_interval_ms=100.0,
        total_nodes=10,
        active_nodes=2,
        global_energy=30.0,
        normalized_energy=0.30,  # Below threshold
        last_tick_time=datetime.now(),
        observed_at=datetime.now(),
        branching_ratio=0.3,
        nodes=tuple()
    )

    decision_low = plan_next_tick(state_low)
    assert len(decision_low.intents) == 0  # No alerts

    print("✅ plan_next_tick() with low energy produces no alerts")
    print()


def test_facade_snapshot():
    """Test Engine.snapshot() reads legacy engine state."""
    print("=== Test 5: Engine.snapshot() ===")

    # Use helper to create properly mocked legacy engine
    legacy_engine = create_mock_legacy_engine(entity_id="test_citizen", energy=60.0, tick_count=15)

    # Create facade
    facade = EngineFacade(legacy_engine)

    # Take snapshot
    snapshot = facade.snapshot()

    assert isinstance(snapshot, EngineState)
    assert snapshot.entity_id == "test_citizen"
    assert snapshot.tick == 15
    assert snapshot.total_nodes == 1
    assert snapshot.active_nodes == 1
    assert snapshot.global_energy == 60.0

    print("✅ Engine.snapshot() reads legacy engine state correctly")
    print(f"   Snapshot: tick={snapshot.tick}, energy={snapshot.global_energy}")
    print()


def test_facade_plan_tick():
    """Test Engine.plan_tick() generates decisions."""
    print("=== Test 6: Engine.plan_tick() ===")

    # Use helper to create properly mocked legacy engine with HIGH energy
    legacy_engine = create_mock_legacy_engine(entity_id="test", energy=95.0, tick_count=5)

    # Create facade
    facade = EngineFacade(legacy_engine)

    # Plan tick
    decision = facade.plan_tick()

    assert isinstance(decision, SchedulerDecision)
    assert decision.state.tick == 5
    assert len(decision.intents) == 1  # High energy alert
    assert decision.intents[0]["type"] == "telemetry.emit"

    # Verify last_decision is saved
    assert facade.last_decision == decision

    print("✅ Engine.plan_tick() generates scheduler decisions")
    print(f"   Decision: {len(decision.intents)} intents")
    print()


def test_facade_dispatch_intents():
    """Test Engine.dispatch_intents() routes to GraphPort."""
    print("=== Test 7: Engine.dispatch_intents() ===")

    # Mock legacy engine
    legacy_engine = Mock()

    # Mock GraphPort
    mock_graph_port = Mock(spec=GraphPort)
    mock_graph_port.persist = Mock()

    # Create facade with graph port
    config = EngineConfig(entity_id="test_citizen")
    facade = EngineFacade(legacy_engine, graph_port=mock_graph_port, config=config)

    # Create intents
    intents = [
        {
            "type": "graph.upsert",
            "payload": {
                "entity_id": "test_citizen",
                "rows": [{"id": "node1", "E": 75.0}]
            }
        },
        {
            "type": "telemetry.emit",  # Should be ignored
            "payload": {"event": "test"}
        }
    ]

    # Dispatch
    facade.dispatch_intents(intents)

    # Verify GraphPort.persist was called with graph.upsert intents only
    mock_graph_port.persist.assert_called_once()
    call_args = mock_graph_port.persist.call_args
    assert call_args[0][0] == "test_citizen"  # entity_id
    assert len(call_args[0][1]) == 1  # Only 1 graph.upsert intent
    assert call_args[0][1][0]["type"] == "graph.upsert"

    print("✅ Engine.dispatch_intents() routes graph intents to GraphPort")
    print(f"   Dispatched 1 graph intent (filtered out 1 telemetry)")
    print()


def test_facade_without_graph_port():
    """Test Engine.dispatch_intents() with no GraphPort (graceful fallback)."""
    print("=== Test 8: Facade without GraphPort (Fallback) ===")

    legacy_engine = create_mock_legacy_engine()

    # Facade without graph_port
    facade = EngineFacade(legacy_engine, graph_port=None)

    intents = [{"type": "graph.upsert", "payload": {}}]

    # Should not crash
    try:
        facade.dispatch_intents(intents)
        print("✅ Engine.dispatch_intents() gracefully handles missing GraphPort")
    except Exception as e:
        print(f"❌ FAILED: dispatch_intents crashed without graph_port: {e}")
        raise

    print()


def test_facade_telemetry_port():
    """Test Engine.plan_tick() publishes telemetry via TelemetryPort."""
    print("=== Test 9: Facade with TelemetryPort ===")

    # Use helper to create properly mocked legacy engine with HIGH energy
    legacy_engine = create_mock_legacy_engine(entity_id="test", energy=92.0, tick_count=10)

    # Mock TelemetryPort
    mock_telemetry = Mock(spec=TelemetryPort)
    mock_telemetry.publish = Mock()

    # Create facade with telemetry
    facade = EngineFacade(legacy_engine, telemetry=mock_telemetry)

    # Plan tick (should emit high energy alert)
    decision = facade.plan_tick()

    # Verify telemetry was published
    mock_telemetry.publish.assert_called_once()
    call_args = mock_telemetry.publish.call_args
    assert call_args[0][0] == "engine.alert.high_energy"
    assert "normalized_energy" in call_args[0][1]

    print("✅ Engine.plan_tick() publishes telemetry via TelemetryPort")
    print(f"   Published: {call_args[0][0]}")
    print()


def test_facade_error_resilience():
    """Test facade handles broken legacy engine gracefully."""
    print("=== Test 10: Facade Error Resilience ===")

    # Use helper to create properly mocked legacy engine
    legacy_engine = create_mock_legacy_engine(entity_id="test", energy=50.0, tick_count=5)

    # Add broken branching_tracker
    legacy_engine.branching_tracker = Mock()
    legacy_engine.branching_tracker.measure_cycle = Mock(side_effect=Exception("Broken tracker"))

    # Facade should handle exception gracefully
    facade = EngineFacade(legacy_engine)

    try:
        snapshot = facade.snapshot()
        assert snapshot.branching_ratio is None  # Should be None if tracker fails
        print("✅ Facade handles broken branching_tracker gracefully")
        print(f"   Snapshot: tick={snapshot.tick}, branching_ratio={snapshot.branching_ratio}")
    except Exception as e:
        print(f"❌ FAILED: Facade didn't handle exception: {e}")
        raise

    print()


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("FACADE INTEGRATION TESTS - PR #2 Review")
    print("=" * 70)
    print()

    tests = [
        test_engine_config_from_legacy,
        test_engine_config_from_none,
        test_build_engine_state,
        test_scheduler_decision,
        test_facade_snapshot,
        test_facade_plan_tick,
        test_facade_dispatch_intents,
        test_facade_without_graph_port,
        test_facade_telemetry_port,
        test_facade_error_resilience,
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
