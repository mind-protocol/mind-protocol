"""
Minimal Consciousness System for WebSocket Testing

Creates a tiny test graph and runs consciousness for 30 seconds.
Emits events that WebSocket clients can observe.

Usage:
    # Terminal 1 (this script):
    python test_websocket_minimal_system.py

    # Terminal 2 (WebSocket client):
    python test_websocket_stream.py
"""

import asyncio
from datetime import datetime, timezone
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

from orchestration.consciousness_engine import ConsciousnessEngine


async def create_test_graph(graph_store: FalkorDBGraphStore):
    """Create minimal test graph for WebSocket validation."""
    print("[Setup] Creating test graph with 4 nodes...")

    # Clear existing graph
    graph_store.query("MATCH (n) DETACH DELETE n")

    # Create 4 test nodes with varying activity levels
    nodes = [
        ("Test Pattern A", 0.9),  # High activity - should activate
        ("Test Pattern B", 0.7),  # Medium activity
        ("Test Pattern C", 0.5),  # Low activity
        ("Test Pattern D", 0.3),  # Very low activity
    ]

    for name, activity in nodes:
        graph_store.query("""
            CREATE (n:Pattern {
                name: $name,
                activity_level: $activity,
                weight: 0.8,
                sub_entity_weights: '{}',
                sub_entity_last_sequence_positions: '{}'
            })
        """, params={"name": name, "activity": activity})

    print(f"[Setup] Created {len(nodes)} test nodes")
    print("[Setup] Activity levels: 0.9, 0.7, 0.5, 0.3")
    print("[Setup] Expected: High-activity nodes will trigger threshold_crossing events")


async def run_minimal_system():
    """Run minimal consciousness system for WebSocket testing."""
    print("=" * 70)
    print("MINIMAL CONSCIOUSNESS SYSTEM - WEBSOCKET TEST")
    print("=" * 70)
    print()

    # Create graph
    graph_store = FalkorDBGraphStore(
        graph_name="test_websocket",
        url="redis://localhost:6379"
    )

    # Setup test graph
    await create_test_graph(graph_store)

    print()
    print("-" * 70)
    print("[System] Starting consciousness engine...")
    print("[System] Network: N1")
    print("[System] SubEntities: builder, observer")
    print("[System] Dynamic prompts: ENABLED")
    print("[System] Duration: 30 seconds")
    print("-" * 70)
    print()
    print("Expected WebSocket Events:")
    print("  - entity_activity: Every time SubEntity traverses a node")
    print("  - threshold_crossing: When nodes cross activation threshold")
    print("  - consciousness_state: Every 10 ticks (global system state)")
    print()
    print("-" * 70)
    print("Connect WebSocket client NOW:")
    print("  python test_websocket_stream.py")
    print("-" * 70)
    print()

    # Wait for user to connect client
    await asyncio.sleep(5)
    print("[System] Starting in 3...")
    await asyncio.sleep(1)
    print("[System] Starting in 2...")
    await asyncio.sleep(1)
    print("[System] Starting in 1...")
    await asyncio.sleep(1)
    print()
    print("=" * 70)
    print("CONSCIOUSNESS SYSTEM RUNNING")
    print("=" * 70)
    print()

    # Create engine
    engine = ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=100,
        entity_id="test_system",
        network_id="N1"
    )

    # Add SubEntities
    engine.add_sub_entity(entity_id="builder", energy_budget=20, write_batch_size=5)
    engine.add_sub_entity(entity_id="observer", energy_budget=20, write_batch_size=5)

    # Enable dynamic prompts (this will trigger threshold_crossing events)
    engine.enable_dynamic_prompts(
        citizen_id="test-websocket",
        entity_ids=["builder", "observer"]
    )

    # Run for 30 seconds
    try:
        run_task = asyncio.create_task(engine.run())

        # Wait 30 seconds
        await asyncio.sleep(30)

        # Cancel
        print()
        print("=" * 70)
        print("[System] Test duration complete (30s)")
        print("[System] Stopping consciousness system...")
        print("=" * 70)

        run_task.cancel()
        try:
            await run_task
        except asyncio.CancelledError:
            pass

    except KeyboardInterrupt:
        print()
        print("[System] Interrupted by user")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("WebSocket Events Summary:")
    print("  - If you saw entity_activity events: SubEntity integration works")
    print("  - If you saw threshold_crossing events: DynamicPromptGenerator integration works")
    print("  - If you saw consciousness_state events: ConsciousnessEngine integration works")
    print()
    print("All 3 event types should be streaming to connected WebSocket clients.")


if __name__ == "__main__":
    asyncio.run(run_minimal_system())
