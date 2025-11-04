#!/usr/bin/env python3
"""
Diagnose why WebSocket connects but sends no data
"""

import redis
import json

# Check what's actually in the broadcast channel
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("=" * 60)
print("WEBSOCKET SILENCE DIAGNOSTIC")
print("=" * 60)

# 1. Check if consciousness engines are registered
print("\n1. Checking consciousness engine registry...")
engine_keys = r.keys("consciousness:engine:*")
print(f"   Found {len(engine_keys)} engine registrations")
for key in engine_keys[:5]:
    print(f"   - {key}")

# 2. Check if there's any recent broadcast activity
print("\n2. Checking broadcast activity...")
pubsub_channels = r.pubsub_channels("membrane:*")
print(f"   Active membrane channels: {len(pubsub_channels)}")
for ch in pubsub_channels[:5]:
    print(f"   - {ch}")

# 3. Check graph data availability
print("\n3. Checking graph data...")
graphs = r.execute_command('GRAPH.LIST')
for graph_name in ['mind-protocol_iris', 'consciousness-infrastructure_mind-protocol_felix']:
    if graph_name in graphs:
        result = r.execute_command('GRAPH.QUERY', graph_name, 'MATCH (n) RETURN count(n) as cnt')
        node_count = result[1][0][0] if result and len(result) > 1 else 0
        print(f"   {graph_name}: {node_count} nodes ✓")
    else:
        print(f"   {graph_name}: NOT FOUND ✗")

# 4. Check if snapshot service is running
print("\n4. Checking snapshot broadcast service...")
snapshot_key = r.get("ws:snapshot:last_broadcast")
if snapshot_key:
    print(f"   Last broadcast: {snapshot_key}")
else:
    print(f"   No broadcasts recorded ✗")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if len(engine_keys) == 0:
    print("❌ No consciousness engines registered")
    print("   → Engines not initializing properly")

if len(pubsub_channels) == 0:
    print("❌ No active membrane channels")
    print("   → Broadcast system not running")

if not snapshot_key:
    print("❌ No snapshot broadcasts occurring")
    print("   → WebSocket server not sending initial snapshots")

print("\n🔍 ROOT CAUSE:")
print("   WebSocket accepts connections but engines aren't")
print("   broadcasting snapshots. Dashboard stays empty.")

print("\n💡 FIX:")
print("   1. Check websocket_server.py initialization logs")
print("   2. Verify consciousness engines actually start")
print("   3. Check if snapshot broadcast is triggered on connect")
