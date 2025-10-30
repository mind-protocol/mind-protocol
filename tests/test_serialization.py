"""
Comprehensive tests for FalkorDB serialization layer.

Tests the serialization/deserialization functions that convert consciousness
schema objects to/from FalkorDB-compatible format.

Author: Felix "Ironhand"
Date: 2025-10-17
Purpose: Verify serialization layer handles FalkorDB primitive-type constraint
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from datetime import datetime
from substrate.schemas.serialization import (
    serialize_dict_fields,
    verify_no_nested_dicts,
    deserialize_node_from_falkordb,
    serialize_node_for_falkordb,
    serialize_relation_for_falkordb,
    deserialize_relation_from_falkordb
)


class TestSerializeDictFields:
    """Test generic serialize_dict_fields function"""

    def test_nested_dict_to_json_string(self):
        """Nested dicts should be converted to JSON strings"""
        data = {
            "name": "test",
            "nested": {"key1": "value1", "key2": "value2"}
        }
        result = serialize_dict_fields(data)

        assert isinstance(result["nested"], str), "Nested dict should be JSON string"
        assert result["name"] == "test", "Primitive should be preserved"
        print("[OK] Nested dicts converted to JSON strings")

    def test_empty_dict_serialization(self):
        """Empty dicts should serialize to empty JSON string"""
        data = {
            "name": "test",
            "empty": {}
        }
        result = serialize_dict_fields(data)

        assert result["empty"] == "{}", "Empty dict should be '{}'"
        print("[OK] Empty dicts serialize correctly")

    def test_datetime_to_int(self):
        """Datetimes should convert to int timestamps"""
        now = datetime.now()
        data = {
            "name": "test",
            "timestamp": now
        }
        result = serialize_dict_fields(data)

        assert isinstance(result["timestamp"], int), "Datetime should be int"
        assert result["timestamp"] > 0, "Timestamp should be positive"
        print(f"[OK] Datetime converted to timestamp: {result['timestamp']}")

    def test_primitive_arrays_preserved(self):
        """Arrays of primitives should be preserved"""
        data = {
            "name": "test",
            "tags": ["tag1", "tag2", "tag3"],
            "scores": [1, 2, 3, 4, 5]
        }
        result = serialize_dict_fields(data)

        assert isinstance(result["tags"], list), "String array should be list"
        assert isinstance(result["scores"], list), "Int array should be list"
        assert result["tags"] == ["tag1", "tag2", "tag3"], "Array values preserved"
        print("[OK] Primitive arrays preserved")

    def test_float_array_preserved(self):
        """Float arrays (embeddings) should be preserved"""
        data = {
            "name": "test",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        result = serialize_dict_fields(data)

        assert isinstance(result["embedding"], list), "Embedding should be list"
        assert all(isinstance(x, float) for x in result["embedding"]), "Should be floats"
        print(f"[OK] Float array preserved (length: {len(result['embedding'])})")

    def test_none_values_preserved(self):
        """None values should be preserved"""
        data = {
            "name": "test",
            "optional_field": None
        }
        result = serialize_dict_fields(data)

        assert result["optional_field"] is None, "None should be preserved"
        print("[OK] None values preserved")


class TestVerifyNoNestedDicts:
    """Test verify_no_nested_dicts validation function"""

    def test_valid_properties(self):
        """Valid properties should pass verification"""
        properties = {
            "name": "test",
            "count": 42,
            "ratio": 0.85,
            "tags": ["a", "b", "c"],
            "embedding": [0.1, 0.2, 0.3]
        }
        assert verify_no_nested_dicts(properties), "Valid properties should pass"
        print("[OK] Valid properties pass verification")

    def test_nested_dict_fails(self):
        """Nested dicts should fail verification"""
        properties = {
            "name": "test",
            "nested": {"key": "value"}
        }
        assert not verify_no_nested_dicts(properties), "Nested dict should fail"
        print("[OK] Nested dicts correctly rejected")

    def test_list_with_dicts_fails(self):
        """Lists containing dicts should fail verification"""
        properties = {
            "name": "test",
            "items": [{"key": "value"}]
        }
        assert not verify_no_nested_dicts(properties), "List with dicts should fail"
        print("[OK] Lists with dicts correctly rejected")


class TestRoundtripSerialization:
    """Test full serialization → deserialization roundtrip"""

    def test_node_roundtrip(self):
        """Node data should survive serialization roundtrip"""
        original = {
            "name": "test_decision",
            "description": "Test description",
            "confidence": 0.95,
            "valid_at": datetime.now(),
            "entity_activations": {
                "translator": {"energy": 0.85, "count": 45},
                "validator": {"energy": 0.65, "count": 32}
            },
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }

        # Serialize
        serialized = serialize_dict_fields(original)

        # Verify no nested dicts
        assert verify_no_nested_dicts(serialized), "Should have no nested dicts"

        # Deserialize
        deserialized = deserialize_node_from_falkordb(serialized, "Decision")

        # Verify data preserved
        assert deserialized["name"] == original["name"]
        assert deserialized["confidence"] == original["confidence"]
        assert isinstance(deserialized["entity_activations"], dict)
        assert deserialized["entity_activations"]["translator"]["energy"] == 0.85
        assert isinstance(deserialized["valid_at"], datetime)

        print("[OK] Node roundtrip preserves data")

    def test_consciousness_fields_roundtrip(self):
        """Complex consciousness fields should survive roundtrip"""
        original = {
            "name": "test",
            "sub_entity_valences": {"entity_1": 0.8, "entity_2": -0.3},
            "sub_entity_emotion_vectors": {
                "entity_1": {"joy": 0.7, "surprise": 0.3},
                "entity_2": {"fear": 0.6, "sadness": 0.2}
            },
            "entity_coactivation_counts": {"pair_1": 5, "pair_2": 12}
        }

        serialized = serialize_dict_fields(original)
        deserialized = deserialize_node_from_falkordb(serialized, "Memory")

        assert deserialized["sub_entity_valences"]["entity_1"] == 0.8
        assert deserialized["sub_entity_emotion_vectors"]["entity_1"]["joy"] == 0.7
        assert deserialized["entity_coactivation_counts"]["pair_1"] == 5

        print("[OK] Consciousness fields roundtrip correctly")


class TestPerformance:
    """Test serialization/deserialization performance"""

    def test_serialization_performance(self):
        """Serialization should be fast (< 10ms per operation)"""
        data = {
            "name": "test_node",
            "description": "Test description" * 10,
            "confidence": 0.95,
            "valid_at": datetime.now(),
            "entity_activations": {
                f"entity_{i}": {"energy": 0.5 + i * 0.1, "count": i * 10}
                for i in range(10)
            },
            "sub_entity_valences": {f"entity_{i}": 0.5 for i in range(20)},
            "embedding": [0.1] * 384  # 384-dim embedding
        }

        # Time 100 serializations
        iterations = 100
        start = time.time()
        for _ in range(iterations):
            result = serialize_dict_fields(data)
            assert verify_no_nested_dicts(result)
        elapsed = time.time() - start

        avg_ms = (elapsed / iterations) * 1000
        print(f"[OK] Serialization: {avg_ms:.2f}ms avg ({iterations} iterations)")
        assert avg_ms < 10, f"Serialization too slow: {avg_ms:.2f}ms"

    def test_deserialization_performance(self):
        """Deserialization should be fast (< 10ms per operation)"""
        # Create serialized data
        data = {
            "name": "test_node",
            "description": "Test description" * 10,
            "confidence": 0.95,
            "valid_at": datetime.now(),
            "entity_activations": {
                f"entity_{i}": {"energy": 0.5 + i * 0.1, "count": i * 10}
                for i in range(10)
            },
            "embedding": [0.1] * 384
        }
        serialized = serialize_dict_fields(data)

        # Time 100 deserializations
        iterations = 100
        start = time.time()
        for _ in range(iterations):
            result = deserialize_node_from_falkordb(serialized, "Decision")
        elapsed = time.time() - start

        avg_ms = (elapsed / iterations) * 1000
        print(f"[OK] Deserialization: {avg_ms:.2f}ms avg ({iterations} iterations)")
        assert avg_ms < 10, f"Deserialization too slow: {avg_ms:.2f}ms"


def run_all_tests():
    """Run all serialization tests"""
    print("=" * 60)
    print("SERIALIZATION LAYER TESTS")
    print("=" * 60)

    test_classes = [
        TestSerializeDictFields,
        TestVerifyNoNestedDicts,
        TestRoundtripSerialization,
        TestPerformance
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\n[{test_class.__name__}]")
        test_instance = test_class()

        # Get all test methods
        test_methods = [m for m in dir(test_instance) if m.startswith("test_")]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except AssertionError as e:
                print(f"[FAIL] {method_name}: {e}")
            except Exception as e:
                print(f"[ERROR] {method_name}: {e}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)

    if passed_tests == total_tests:
        print("\n[SUCCESS] All serialization tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total_tests - passed_tests} tests failed")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
