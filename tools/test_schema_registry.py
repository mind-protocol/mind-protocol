#!/usr/bin/env python3
"""
Quick test to verify SchemaRegistry implementation.
Tests schema loading, validation, and error cases.
"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.libs.schema_registry import SchemaRegistry, get_schema_registry


def test_schema_registry():
    print("🧪 Testing SchemaRegistry Implementation\n")

    # Test 1: Load registry
    print("📥 Test 1: Load registry")
    registry = SchemaRegistry()
    stats = registry.get_stats()

    print(f"   Loaded: {stats['loaded']}")
    print(f"   Schemas: {stats['schema_count']}")
    print(f"   Namespaces: {stats['namespace_count']}")
    print(f"   Policies: {stats['policy_count']}")
    print(f"   Exported at: {stats['exported_at']}")
    print(f"   Graph hash: {stats['graph_hash'][:16]}...")

    if not stats['loaded']:
        print("   ❌ Registry failed to load")
        return False

    print("   ✅ Registry loaded\n")

    # Test 2: Get existing schema
    print("📖 Test 2: Get existing schema (docs.catalog.emit)")
    schema = registry.get_schema("docs.catalog.emit")

    if schema:
        print(f"   ✅ Schema found:")
        print(f"      - Name: {schema['name']}")
        print(f"      - Direction: {schema['direction']}")
        print(f"      - Topic pattern: {schema['topic_pattern']}")
        print(f"      - Maps to: {schema.get('maps_to_topic', 'N/A')}")
    else:
        print("   ❌ Schema not found")
        return False

    print()

    # Test 3: Validate valid event
    print("✅ Test 3: Validate valid event (docs.catalog.emit)")
    result = registry.validate_event("docs.catalog.emit", {"test": "data"})

    print(f"   Valid: {result.valid}")
    if not result.valid:
        print(f"   ❌ Validation failed: {result.rule_code} - {result.error}")
        return False
    else:
        print(f"   ✅ Validation passed")

    print()

    # Test 4: Validate unknown event (R-001 violation)
    print("❌ Test 4: Validate unknown event (should fail R-001)")
    result = registry.validate_event("unknown.event", {"test": "data"})

    print(f"   Valid: {result.valid}")
    if result.valid:
        print("   ❌ Should have failed validation")
        return False
    else:
        print(f"   ✅ Validation failed correctly:")
        print(f"      - Rule: {result.rule_code}")
        print(f"      - Error: {result.error}")

    print()

    # Test 5: Get singleton
    print("🔄 Test 5: Get singleton registry")
    singleton = get_schema_registry()
    singleton_stats = singleton.get_stats()

    print(f"   Loaded: {singleton_stats['loaded']}")
    print(f"   Schemas: {singleton_stats['schema_count']}")

    if singleton_stats['schema_count'] != stats['schema_count']:
        print("   ❌ Singleton has different schema count")
        return False
    else:
        print("   ✅ Singleton working correctly")

    print()

    # Test 6: Quick validation (without payload)
    print("⚡ Test 6: Quick validation (docs.page.upsert)")
    result = registry.validate_event_basic("docs.page.upsert")

    print(f"   Valid: {result.valid}")
    if not result.valid:
        print(f"   ❌ Quick validation failed: {result.error}")
        return False
    else:
        print(f"   ✅ Quick validation passed")

    print()
    print("✅ All SchemaRegistry tests passed!")
    print()
    print("📊 Summary:")
    print(f"   ✓ Registry loading working")
    print(f"   ✓ Schema lookup working ({stats['schema_count']} schemas)")
    print(f"   ✓ Validation working (R-001 enforcement)")
    print(f"   ✓ Singleton pattern working")
    print(f"   ✓ Quick validation working")
    print()
    print("🚀 SchemaRegistry ready for SafeBroadcaster integration!")

    return True


if __name__ == "__main__":
    success = test_schema_registry()
    sys.exit(0 if success else 1)
