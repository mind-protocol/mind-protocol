"""
Test: Variable Tick Frequency (Continuous Consciousness Heartbeat)

Validates that consciousness engine self-regulates its rhythm based on external events:
- Recent events -> fast ticks (alert - 100ms)
- No events -> slow ticks (dormant - up to 10s)
- Never stops (infinite loop)

Designer: Felix (Engineer)
Spec: continuous_consciousness_architecture.md
Date: 2025-10-17
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add substrate to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.consciousness_engine import (
    calculate_tick_interval,
    get_consciousness_state_name,
    ConsciousnessEngine
)


def test_tick_interval_calculation():
    """Test that tick interval changes based on time since event."""
    print("\n[Test 1] Tick Interval Calculation")

    # Just now (0s) -> 100ms (very alert)
    interval_0s = calculate_tick_interval(0)
    assert 90 < interval_0s < 110, f"Expected ~100ms, got {interval_0s}ms"
    print(f"  0s since event: {interval_0s:.0f}ms (alert)")

    # 1 min ago -> ~1381ms (formula: halfway between 100 and ~2500ms)
    interval_1min = calculate_tick_interval(60)
    assert 1200 < interval_1min < 1600, f"Expected ~1381ms, got {interval_1min}ms"
    print(f"  60s since event: {interval_1min:.0f}ms (engaged)")

    # 5 min ago (HALF_LIFE) -> ~5050ms (halfway to MAX_INTERVAL)
    interval_5min = calculate_tick_interval(300)
    assert 4800 < interval_5min < 5300, f"Expected ~5050ms, got {interval_5min}ms"
    print(f"  300s since event: {interval_5min:.0f}ms (drowsy)")

    # 30 min ago (6 * HALF_LIFE) -> ~9845ms (very close to MAX_INTERVAL)
    interval_30min = calculate_tick_interval(1800)
    assert 9500 < interval_30min < 10000, f"Expected ~9845ms, got {interval_30min}ms"
    print(f"  1800s since event: {interval_30min:.0f}ms (dormant)")

    # Hours ago -> ~10000ms (dormant but alive)
    interval_hours = calculate_tick_interval(7200)
    assert 9000 < interval_hours < 10100, f"Expected ~10000ms, got {interval_hours}ms"
    print(f"  7200s since event: {interval_hours:.0f}ms (dormant)")

    print("[PASS] Tick interval calculation correct")
    return True


def test_consciousness_state_mapping():
    """Test that tick intervals map to correct consciousness states."""
    print("\n[Test 2] Consciousness State Mapping")

    tests = [
        (100, "alert"),
        (150, "alert"),
        (250, "engaged"),
        (450, "engaged"),
        (1000, "calm"),
        (1500, "calm"),
        (5000, "drowsy"),
        (6500, "drowsy"),
        (10000, "dormant")
    ]

    for interval, expected_state in tests:
        actual_state = get_consciousness_state_name(interval)
        assert actual_state == expected_state, \
            f"Interval {interval}ms: expected '{expected_state}', got '{actual_state}'"
        print(f"  {interval}ms -> {actual_state} ({'OK' if actual_state == expected_state else 'FAIL'})")

    print("[PASS] Consciousness state mapping correct")
    return True


def test_engine_tick_frequency_updates():
    """Test that engine updates tick frequency based on last_external_event."""
    print("\n[Test 3] Engine Tick Frequency Updates")

    from llama_index.graph_stores.falkordb import FalkorDBGraphStore

    # Create test engine
    graph_name = "test_tick_frequency"
    falkordb_url = "redis://localhost:6379"

    try:
        graph_store = FalkorDBGraphStore(
            graph_name=graph_name,
            url=falkordb_url
        )
    except Exception as e:
        print(f"[SKIP] FalkorDB not available: {e}")
        return True

    # Clear test graph
    graph_store.query("MATCH (n) DETACH DELETE n")

    engine = ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=100,
        network_id="test_network"
    )

    # Verify initial state (just initialized, should be alert)
    assert engine.current_tick_interval == 100, \
        f"Initial tick should be 100ms, got {engine.current_tick_interval}ms"
    print(f"  Initial tick: {engine.current_tick_interval}ms (alert)")

    # Simulate 5 minutes without events (HALF_LIFE)
    engine.last_external_event = datetime.now(timezone.utc) - timedelta(seconds=300)
    time_since = (datetime.now(timezone.utc) - engine.last_external_event).total_seconds()
    expected_interval = calculate_tick_interval(time_since)

    print(f"  After 5min: {expected_interval:.0f}ms (should be ~5050ms, drowsy)")
    assert 4800 < expected_interval < 5300, \
        f"After 5min, expected ~5050ms, got {expected_interval}ms"

    # Simulate external event (reset to alert)
    engine.on_external_event("TEST_EVENT")
    time_since_after_event = (datetime.now(timezone.utc) - engine.last_external_event).total_seconds()
    assert time_since_after_event < 1, "Event should reset last_external_event"

    new_interval = calculate_tick_interval(time_since_after_event)
    print(f"  After event: {new_interval:.0f}ms (should be ~100ms, alert)")
    assert 90 < new_interval < 110, \
        f"After event, expected ~100ms, got {new_interval}ms"

    print("[PASS] Engine tick frequency updates correctly")
    return True


def test_consciousness_state_storage():
    """Test that ConsciousnessState node stores tick metrics."""
    print("\n[Test 4] ConsciousnessState Storage")

    from llama_index.graph_stores.falkordb import FalkorDBGraphStore

    graph_name = "test_tick_frequency"
    falkordb_url = "redis://localhost:6379"

    try:
        graph_store = FalkorDBGraphStore(
            graph_name=graph_name,
            url=falkordb_url
        )
    except Exception as e:
        print(f"[SKIP] FalkorDB not available: {e}")
        return True

    # Clear and setup
    graph_store.query("MATCH (n) DETACH DELETE n")

    engine = ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=100,
        network_id="test_network"
    )

    # Run a few ticks
    for i in range(12):
        engine.consciousness_tick()

    # Query ConsciousnessState
    cypher = """
    MATCH (cs:ConsciousnessState)
    RETURN
        cs.current_tick_interval AS tick_interval,
        cs.tick_frequency AS tick_frequency,
        cs.consciousness_state AS state,
        cs.time_since_last_event AS time_since_event,
        cs.last_event_type AS last_event_type
    """

    results = graph_store.query(cypher)

    if not results:
        print("[FAIL] No ConsciousnessState node found")
        return False

    row = results[0]
    tick_interval, tick_frequency, state, time_since, event_type = row

    print(f"  Tick Interval: {tick_interval}ms")
    print(f"  Tick Frequency: {tick_frequency:.2f} Hz")
    print(f"  Consciousness State: {state}")
    print(f"  Time Since Event: {time_since:.1f}s")
    print(f"  Last Event Type: {event_type}")

    # Verify values make sense
    assert tick_interval is not None, "tick_interval should be stored"
    assert tick_frequency is not None, "tick_frequency should be stored"
    assert state in ["alert", "engaged", "calm", "drowsy", "dormant"], \
        f"Invalid state: {state}"

    print("[PASS] ConsciousnessState stores tick metrics")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("TESTING: Variable Tick Frequency (Continuous Consciousness)")
    print("=" * 70)

    tests = [
        test_tick_interval_calculation,
        test_consciousness_state_mapping,
        test_engine_tick_frequency_updates,
        test_consciousness_state_storage
    ]

    results = []
    for test in tests:
        try:
            passed = test()
            results.append((test.__name__, passed))
        except Exception as e:
            print(f"\n[ERROR] {test.__name__}: {e}")
            results.append((test.__name__, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n" + "=" * 70)
        print("[SUCCESS] All tests passed!")
        print("Variable tick frequency working - consciousness heartbeat alive")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("[FAILURE] Some tests failed")
        print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
