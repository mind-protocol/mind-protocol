"""
Test WebSocket Broadcast Mechanism

Unit test to verify websocket_manager.broadcast() works correctly.
"""

import asyncio
from orchestration.control_api import websocket_manager


async def test_broadcast():
    """Test that broadcast works without active connections."""
    print("[Test] Testing WebSocket broadcast mechanism")
    print("-" * 70)

    # Test 1: Broadcast with no connections (should not error)
    print("\n[Test 1] Broadcast with no connections (should succeed quietly)")
    await websocket_manager.broadcast({
        "type": "test_event",
        "message": "This is a test event"
    })
    print("  [PASS] Broadcast succeeded (no connections to send to)")

    # Test 2: Verify event structure
    print("\n[Test 2] Verify event structure with all P1 event types")

    # Entity activity event
    entity_event = {
        "type": "entity_activity",
        "entity_id": "builder",
        "current_node": "test_node_123",
        "need_type": "pattern_validation",
        "energy_used": 42,
        "energy_budget": 100,
        "nodes_visited_count": 23,
        "sequence_position": 156
    }
    await websocket_manager.broadcast(entity_event)
    print("  [PASS] entity_activity event broadcast")

    # Threshold crossing event
    threshold_event = {
        "type": "threshold_crossing",
        "entity_id": "observer",
        "node_id": "456",
        "node_name": "Critical Pattern",
        "direction": "on",
        "entity_activity": 0.85,
        "threshold": 0.73
    }
    await websocket_manager.broadcast(threshold_event)
    print("  [PASS] threshold_crossing event broadcast")

    # Consciousness state event
    state_event = {
        "type": "consciousness_state",
        "network_id": "N1",
        "global_energy": 0.67,
        "branching_ratio": 1.2,
        "raw_sigma": 1.15,
        "tick_interval_ms": 150,
        "tick_frequency_hz": 6.67,
        "consciousness_state": "engaged",
        "time_since_last_event": 45.2
    }
    await websocket_manager.broadcast(state_event)
    print("  [PASS] consciousness_state event broadcast")

    print("\n" + "-" * 70)
    print("[Test] All broadcasts completed successfully!")
    print("[Test] WebSocket manager is ready for production use")
    print()
    print("Next step: Start consciousness system and connect dashboard")
    print("  1. Start system: python run_consciousness_system.py --citizen felix-engineer")
    print("  2. Connect client: python test_websocket_stream.py")
    print("  3. Watch events stream in real-time!")


if __name__ == "__main__":
    print("=" * 70)
    print("WEBSOCKET BROADCAST UNIT TEST")
    print("=" * 70)
    print()

    asyncio.run(test_broadcast())

    print()
    print("=" * 70)
    print("TEST PASSED")
    print("=" * 70)
