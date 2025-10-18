"""
Test WebSocket Operations Stream

Simple test client that connects to WebSocket endpoint and prints events.

Usage:
    python test_websocket_stream.py

Expected events:
- entity_activity: SubEntity exploration updates
- threshold_crossing: Node activation changes
- consciousness_state: Global system state updates
"""

import asyncio
import json
from datetime import datetime
import websockets


async def test_websocket_client():
    """Connect to WebSocket and listen for events."""
    uri = "ws://localhost:8000/api/ws"

    print(f"[WebSocket Test] Connecting to {uri}")
    print("[WebSocket Test] Listening for events...")
    print("-" * 70)

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[WebSocket Test] Connected successfully!")
            print("-" * 70)

            # Listen for events
            event_count = 0
            while True:
                try:
                    message = await websocket.recv()
                    event = json.loads(message)
                    event_count += 1

                    # Print event
                    event_type = event.get("type", "unknown")
                    timestamp = event.get("timestamp", "")

                    print(f"\n[Event #{event_count}] {event_type} at {timestamp}")

                    # Pretty print event data
                    if event_type == "entity_activity":
                        print(f"  Entity: {event.get('entity_id')}")
                        print(f"  Current node: {event.get('current_node')}")
                        print(f"  Energy: {event.get('energy_used')}/{event.get('energy_budget')}")
                        print(f"  Nodes visited: {event.get('nodes_visited_count')}")
                        print(f"  Need type: {event.get('need_type')}")

                    elif event_type == "threshold_crossing":
                        print(f"  Entity: {event.get('entity_id')}")
                        print(f"  Node: {event.get('node_name')} (ID: {event.get('node_id')})")
                        print(f"  Direction: {event.get('direction').upper()}")
                        print(f"  Activity: {event.get('entity_activity'):.2f} (threshold: {event.get('threshold'):.2f})")

                    elif event_type == "consciousness_state":
                        print(f"  Network: {event.get('network_id')}")
                        print(f"  State: {event.get('consciousness_state')}")
                        print(f"  Global arousal: {event.get('global_arousal'):.2f}")
                        print(f"  Branching ratio: {event.get('branching_ratio'):.2f}")
                        print(f"  Tick frequency: {event.get('tick_frequency_hz'):.2f} Hz")

                    else:
                        # Unknown event type - print full JSON
                        print(f"  Data: {json.dumps(event, indent=2)}")

                    print("-" * 70)

                except websockets.exceptions.ConnectionClosed:
                    print("\n[WebSocket Test] Connection closed by server")
                    break
                except json.JSONDecodeError as e:
                    print(f"\n[WebSocket Test] Failed to parse event: {e}")
                except KeyboardInterrupt:
                    print("\n[WebSocket Test] Interrupted by user")
                    break

    except ConnectionRefusedError:
        print(f"[WebSocket Test] ERROR: Could not connect to {uri}")
        print("[WebSocket Test] Make sure the FastAPI server is running")
        print("[WebSocket Test] Start with: uvicorn orchestration.control_api:router --reload")
    except Exception as e:
        print(f"[WebSocket Test] ERROR: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("WEBSOCKET OPERATIONS STREAM TEST")
    print("=" * 70)
    print()

    # Run client
    asyncio.run(test_websocket_client())

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
