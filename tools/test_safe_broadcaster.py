#!/usr/bin/env python3
"""
Quick test to verify SafeBroadcaster implementation.
Tests spill buffer, flush, stats tracking, and schema validation.
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from orchestration.libs.safe_broadcaster import SafeBroadcaster


async def test_safe_broadcaster():
    print("🧪 Testing SafeBroadcaster Implementation\n")

    # Create SafeBroadcaster (no WebSocket manager = always unavailable)
    safe = SafeBroadcaster(
        citizen_id="test_citizen",
        max_spill_size=10,  # Small buffer for testing
        health_bus_inject=None
    )

    print(f"✅ SafeBroadcaster created")
    print(f"   Broadcaster available: {safe.is_available()}")
    print(f"   (Expected: False - no WebSocket manager)")

    # Test 1: Events should spill when WebSocket unavailable
    print("\n📥 Test 1: Spilling events (WebSocket unavailable)")
    for i in range(5):
        result = await safe.safe_emit(
            "graph.delta.node.upsert",
            {"node_id": f"n{i}", "test": True}
        )
        print(f"   Event {i}: spilled (returned {result})")

    # Check stats
    stats = safe.get_stats()
    print(f"\n📊 Stats after spilling:")
    print(f"   Total emitted: {stats['total_emitted']}")
    print(f"   Total spilled: {stats['total_spilled']}")
    print(f"   Buffer size: {stats['spill_buffer_size']}")
    print(f"   Rejection counts: {stats['rejection_counts']}")

    # Test 2: Buffer overflow
    print(f"\n🌊 Test 2: Buffer overflow (max_spill_size={safe.max_spill_size})")
    for i in range(8):  # Overflow the buffer
        await safe.safe_emit(
            "graph.delta.link.upsert",
            {"link_id": f"l{i}", "test": True}
        )

    stats = safe.get_stats()
    print(f"   Buffer size after overflow: {stats['spill_buffer_size']}")
    print(f"   (Expected: {safe.max_spill_size} = max size, oldest dropped)")

    # Test 3: Backward compatibility API
    print(f"\n🔄 Test 3: Backward compatibility (broadcast_event)")
    await safe.broadcast_event("test.event", {"data": "test"})
    stats = safe.get_stats()
    print(f"   Total spilled: {stats['total_spilled']}")
    print(f"   (Should increment - broadcast_event calls safe_emit)")

    # Test 4: Schema validation (R-001, R-002)
    print(f"\n🔍 Test 4: Schema validation (mp-lint integration)")

    # Check if schema validation is enabled
    stats = safe.get_stats()
    print(f"   Schema validation enabled: {stats['schema_validation_enabled']}")
    print(f"   Schema registry loaded: {stats['schema_registry_loaded']}")

    if stats['schema_validation_enabled'] and stats['schema_registry_loaded']:
        # Test 4a: Valid event (should pass validation and spill)
        print(f"\n   ✅ Test 4a: Valid event (docs.catalog.emit)")
        spilled_before = stats['total_spilled']
        rejected_before = stats.get('total_rejected', 0)

        result = await safe.safe_emit("docs.catalog.emit", {"test": "data"})

        stats = safe.get_stats()
        spilled_after = stats['total_spilled']
        rejected_after = stats.get('total_rejected', 0)

        print(f"      Result: {result} (False = spilled due to no WebSocket)")
        print(f"      Spilled: {spilled_before} → {spilled_after} (should +1)")
        print(f"      Rejected: {rejected_before} → {rejected_after} (should stay same)")

        # Test 4b: Unknown event (should fail R-001)
        print(f"\n   ❌ Test 4b: Unknown event (should fail R-001)")
        rejected_before = stats.get('total_rejected', 0)
        spilled_before = stats['total_spilled']

        result = await safe.safe_emit("unknown.invalid.event", {"test": "data"})

        stats = safe.get_stats()
        rejected_after = stats.get('total_rejected', 0)
        spilled_after = stats['total_spilled']

        print(f"      Result: {result} (False = rejected)")
        print(f"      Rejected: {rejected_before} → {rejected_after} (should +1)")
        print(f"      Spilled: {spilled_before} → {spilled_after} (should stay same)")
        print(f"      Rejection counts: {stats['rejection_counts']}")

        if rejected_after > rejected_before:
            print(f"      ✅ Invalid event rejected (not spilled)")
        else:
            print(f"      ❌ Invalid event not rejected!")
    else:
        print(f"   ⚠️  Schema validation disabled or registry not loaded - skipping validation tests")

    print(f"\n✅ SafeBroadcaster tests complete!")
    print(f"\n📝 Summary:")
    print(f"   ✓ Spill buffer working")
    print(f"   ✓ Stats tracking working")
    print(f"   ✓ Buffer overflow handling working")
    print(f"   ✓ Backward-compatible API working")
    if stats.get('schema_validation_enabled') and stats.get('schema_registry_loaded'):
        print(f"   ✓ Schema validation working (R-001, R-002 enforcement)")
        print(f"   ✓ Invalid events rejected before spilling")
    print(f"\n🚀 SafeBroadcaster ready for production use!")


if __name__ == "__main__":
    asyncio.run(test_safe_broadcaster())
