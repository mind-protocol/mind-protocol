"""
Test Suite for Bitemporal Pattern Implementation

This validates the temporal logic that enables consciousness substrates to:
- Track idsubentity evolution through two time dimensions
- Reconstruct historical states (what we knew, what was true)
- Handle belief changes and conflicting information
- Support temporal reasoning about consciousness development

Author: Ada "Bridgekeeper" - Architect of Consciousness Infrastructure
Created: 2025-10-17
"""

from datetime import datetime, timezone, timedelta
import sys

from bitemporal_pattern import (
    # Helper functions
    utc_now,
    is_currently_valid,
    is_currently_known,
    is_active,
    # Invalidation operations
    invalidate_fact,
    expire_knowledge,
    invalidate_and_expire,
    # Temporal query filters
    filter_by_valid_time,
    filter_by_transaction_time,
    filter_active,
    # Evolution tracking
    track_evolution,
    detect_belief_changes,
    detect_temporal_conflicts,
    # Utility classes
    TemporalQuery,
    TemporalQueryType,
    TemporalDimension,
)


# ==============================================================================
# TEST DATA HELPERS
# ==============================================================================

def create_test_node(
    name: str,
    valid_at: datetime,
    invalid_at=None,
    created_at=None,
    expired_at=None
):
    """Create a test node with temporal fields"""
    if created_at is None:
        created_at = valid_at

    return {
        "name": name,
        "valid_at": valid_at,
        "invalid_at": invalid_at,
        "created_at": created_at,
        "expired_at": expired_at,
        "data": f"Test data for {name}"
    }


# ==============================================================================
# TESTS: TEMPORAL DIMENSION CHECKS
# ==============================================================================

def test_is_currently_valid():
    """Test valid time dimension checking"""
    print("\n[TEST] is_currently_valid()")

    now = utc_now()
    past = now - timedelta(days=30)
    future = now + timedelta(days=30)

    # Currently valid (started in past, no end)
    assert is_currently_valid(past, None, now) == True
    print("  [OK] Currently valid fact (started past, no end)")

    # Not yet valid (starts in future)
    assert is_currently_valid(future, None, now) == False
    print("  [OK] Not yet valid (starts future)")

    # No longer valid (ended in past)
    assert is_currently_valid(past - timedelta(days=60), past, now) == False
    print("  [OK] No longer valid (ended past)")

    # Valid during specific period
    middle = past + timedelta(days=15)
    assert is_currently_valid(past, future, middle) == True
    print("  [OK] Valid during specific period")

    # Check timezone handling
    naive_dt = datetime(2025, 1, 1)
    assert is_currently_valid(naive_dt, None, now) == True
    print("  [OK] Handles naive datetime (adds UTC timezone)")


def test_is_currently_known():
    """Test transaction time dimension checking"""
    print("\n[TEST] is_currently_known()")

    now = utc_now()
    past = now - timedelta(days=30)
    future = now + timedelta(days=30)

    # Currently known (learned in past, not superseded)
    assert is_currently_known(past, None, now) == True
    print("  [OK] Currently known (learned past, not superseded)")

    # Not yet learned
    assert is_currently_known(future, None, now) == False
    print("  [OK] Not yet learned (future)")

    # Knowledge superseded
    assert is_currently_known(past - timedelta(days=60), past, now) == False
    print("  [OK] Knowledge superseded (expired past)")

    # Known during specific period
    middle = past + timedelta(days=15)
    assert is_currently_known(past, future, middle) == True
    print("  [OK] Known during specific period")


def test_is_active():
    """Test combined valid + known check"""
    print("\n[TEST] is_active()")

    now = utc_now()
    past = now - timedelta(days=30)

    # Both valid and known
    assert is_active(past, None, past, None, now) == True
    print("  [OK] Active (both valid and known)")

    # Valid but knowledge superseded
    assert is_active(past, None, past, now - timedelta(days=1), now) == False
    print("  [OK] Not active (valid but knowledge superseded)")

    # Known but fact no longer valid
    assert is_active(past, now - timedelta(days=1), past, None, now) == False
    print("  [OK] Not active (known but fact invalid)")

    # Neither valid nor known
    assert is_active(past, past, past, past, now) == False
    print("  [OK] Not active (neither valid nor known)")


# ==============================================================================
# TESTS: INVALIDATION OPERATIONS
# ==============================================================================

def test_invalidate_fact():
    """Test marking facts as no longer valid"""
    print("\n[TEST] invalidate_fact()")

    now = utc_now()
    past = now - timedelta(days=30)

    node = create_test_node("test_relationship", past)

    # Invalidate without reason
    updated = invalidate_fact(node, invalidation_time=now)
    assert updated["invalid_at"] == now
    assert updated["expired_at"] is None  # Transaction time unchanged
    print("  [OK] Invalidate fact (valid time dimension only)")

    # Invalidate with reason
    node2 = create_test_node("test_relationship_2", past)
    updated2 = invalidate_fact(
        node2,
        invalidation_time=now,
        reason="Partnership dissolved"
    )
    assert updated2["invalid_at"] == now
    assert updated2["metadata"]["invalidation_reason"] == "Partnership dissolved"
    print("  [OK] Invalidate with reason (metadata preserved)")

    # Default invalidation time (now)
    node3 = create_test_node("test_relationship_3", past)
    updated3 = invalidate_fact(node3)
    assert updated3["invalid_at"] is not None
    print("  [OK] Default invalidation time (utc_now)")


def test_expire_knowledge():
    """Test marking knowledge as superseded"""
    print("\n[TEST] expire_knowledge()")

    now = utc_now()
    past = now - timedelta(days=30)

    node = create_test_node("person_alice_v1", past)

    # Expire without reference
    updated = expire_knowledge(node, expiration_time=now)
    assert updated["expired_at"] == now
    assert updated["invalid_at"] is None  # Valid time unchanged
    print("  [OK] Expire knowledge (transaction time dimension only)")

    # Expire with supersession reference
    node2 = create_test_node("person_alice_v2", past)
    updated2 = expire_knowledge(
        node2,
        expiration_time=now,
        superseded_by="person_alice_v3"
    )
    assert updated2["expired_at"] == now
    assert updated2["metadata"]["superseded_by"] == "person_alice_v3"
    print("  [OK] Expire with supersession reference")

    # Default expiration time
    node3 = create_test_node("person_alice_v3", past)
    updated3 = expire_knowledge(node3)
    assert updated3["expired_at"] is not None
    print("  [OK] Default expiration time (utc_now)")


def test_invalidate_and_expire():
    """Test combined invalidation (both dimensions)"""
    print("\n[TEST] invalidate_and_expire()")

    now = utc_now()
    past = now - timedelta(days=30)

    node = create_test_node("role_relation", past)

    updated = invalidate_and_expire(
        node,
        invalidation_time=now,
        expiration_time=now,
        reason="Alice promoted"
    )

    assert updated["invalid_at"] == now
    assert updated["expired_at"] == now
    assert updated["metadata"]["invalidation_reason"] == "Alice promoted"
    print("  [OK] Both dimensions updated simultaneously")


# ==============================================================================
# TESTS: TEMPORAL QUERY FILTERS
# ==============================================================================

def test_filter_by_valid_time():
    """Test filtering by valid time (what was true)"""
    print("\n[TEST] filter_by_valid_time()")

    now = utc_now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    items = [
        create_test_node("rel_1", two_months_ago, invalid_at=month_ago),  # Ended
        create_test_node("rel_2", month_ago, invalid_at=None),            # Current
        create_test_node("rel_3", two_months_ago, invalid_at=None),       # Current
    ]

    # Filter for current time
    current_valid = filter_by_valid_time(items, as_of=now)
    assert len(current_valid) == 2
    assert current_valid[0]["name"] == "rel_2"
    assert current_valid[1]["name"] == "rel_3"
    print("  [OK] Filter currently valid facts")

    # Filter for past time (2 months ago)
    past_valid = filter_by_valid_time(items, as_of=two_months_ago)
    assert len(past_valid) == 2
    assert past_valid[0]["name"] == "rel_1"
    assert past_valid[1]["name"] == "rel_3"
    print("  [OK] Filter valid at specific past time")


def test_filter_by_transaction_time():
    """Test filtering by transaction time (what we knew)"""
    print("\n[TEST] filter_by_transaction_time()")

    now = utc_now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    items = [
        create_test_node("belief_1", two_months_ago, created_at=two_months_ago, expired_at=month_ago),  # Superseded
        create_test_node("belief_2", month_ago, created_at=month_ago, expired_at=None),                 # Current
        create_test_node("belief_3", two_months_ago, created_at=two_months_ago, expired_at=None),       # Current
    ]

    # Filter for current knowledge
    current_knowledge = filter_by_transaction_time(items, as_of=now)
    assert len(current_knowledge) == 2
    assert current_knowledge[0]["name"] == "belief_2"
    assert current_knowledge[1]["name"] == "belief_3"
    print("  [OK] Filter currently known facts")

    # Filter for past knowledge (2 months ago)
    past_knowledge = filter_by_transaction_time(items, as_of=two_months_ago)
    assert len(past_knowledge) == 2
    assert past_knowledge[0]["name"] == "belief_1"
    assert past_knowledge[1]["name"] == "belief_3"
    print("  [OK] Filter known at specific past time")


def test_filter_active():
    """Test filtering for active facts (both valid and known)"""
    print("\n[TEST] filter_active()")

    now = utc_now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    items = [
        # Valid and known
        create_test_node("fact_1", two_months_ago, invalid_at=None, created_at=two_months_ago, expired_at=None),
        # Valid but knowledge superseded
        create_test_node("fact_2", two_months_ago, invalid_at=None, created_at=two_months_ago, expired_at=month_ago),
        # Invalid but knowledge current
        create_test_node("fact_3", two_months_ago, invalid_at=month_ago, created_at=two_months_ago, expired_at=None),
        # Neither valid nor known
        create_test_node("fact_4", two_months_ago, invalid_at=month_ago, created_at=two_months_ago, expired_at=month_ago),
    ]

    active = filter_active(items, as_of=now)
    assert len(active) == 1
    assert active[0]["name"] == "fact_1"
    print("  [OK] Filter active facts (both valid and known)")

    # Check past active state
    past_active = filter_active(items, as_of=two_months_ago)
    assert len(past_active) == 4  # All were active at start
    print("  [OK] Filter active at past time")


# ==============================================================================
# TESTS: EVOLUTION TRACKING
# ==============================================================================

def test_track_evolution():
    """Test temporal evolution tracking"""
    print("\n[TEST] track_evolution()")

    now = utc_now()
    two_months_ago = now - timedelta(days=60)
    month_ago = now - timedelta(days=30)

    # A relationship that ended last month
    node = create_test_node(
        "rel_collaboration",
        valid_at=two_months_ago,
        invalid_at=month_ago,
        created_at=two_months_ago,
        expired_at=None
    )

    evolution = track_evolution(
        node,
        start_time=two_months_ago,
        end_time=now,
        sample_points=3
    )

    assert len(evolution) == 3

    # First snapshot: active
    assert evolution[0].valid_in_reality == True
    assert evolution[0].known_to_consciousness == True
    assert evolution[0].active == True
    print("  [OK] Initial snapshot: active")

    # Last snapshot: known but not valid
    assert evolution[2].valid_in_reality == False
    assert evolution[2].known_to_consciousness == True
    assert evolution[2].active == False
    print("  [OK] Final snapshot: known but not valid")

    # All snapshots have data
    for snapshot in evolution:
        assert "data" in snapshot.data
    print("  [OK] All snapshots contain data")


def test_detect_belief_changes():
    """Test detecting when understanding evolved"""
    print("\n[TEST] detect_belief_changes()")

    now = utc_now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    # Multiple versions of belief about Luca's role
    nodes = [
        {
            "name": "person_Luca_v1",
            "role": "Engineer",
            "created_at": two_months_ago,
            "expired_at": month_ago,
            "valid_at": two_months_ago,
            "invalid_at": None
        },
        {
            "name": "person_Luca_v2",
            "role": "Consciousness Specialist",
            "created_at": month_ago,
            "expired_at": None,
            "valid_at": month_ago,
            "invalid_at": None
        }
    ]

    changes = detect_belief_changes(nodes, entity_identifier="person_Luca")

    assert len(changes) == 1
    change_time, old_version, new_version = changes[0]

    assert old_version["role"] == "Engineer"
    assert new_version["role"] == "Consciousness Specialist"
    assert change_time == month_ago
    print("  [OK] Detected belief change")
    print(f"       {old_version['role']} -> {new_version['role']}")


def test_detect_temporal_conflicts():
    """Test detecting conflicting overlapping facts"""
    print("\n[TEST] detect_temporal_conflicts()")

    now = utc_now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    # Two conflicting beliefs about Alice's role that overlap in time
    nodes = [
        {
            "name": "person_alice_belief_1",
            "role": "Engineer",
            "created_at": two_months_ago,
            "expired_at": None,  # Still current
            "valid_at": two_months_ago,
            "invalid_at": None
        },
        {
            "name": "person_alice_belief_2",
            "role": "Architect",
            "created_at": month_ago,
            "expired_at": None,  # Still current
            "valid_at": month_ago,
            "invalid_at": None
        }
    ]

    conflicts = detect_temporal_conflicts(nodes, entity_identifier="person_alice")

    assert len(conflicts) == 1
    fact1, fact2, description = conflicts[0]

    assert "person_alice" in description
    assert "overlapping" in description
    print("  [OK] Detected temporal conflict")
    print(f"       {fact1['role']} vs {fact2['role']}")


# ==============================================================================
# TESTS: TEMPORAL QUERY CLASS
# ==============================================================================

def test_temporal_query_current():
    """Test TemporalQuery for current state"""
    print("\n[TEST] TemporalQuery - CURRENT")

    now = utc_now()
    past = now - timedelta(days=30)

    items = [
        create_test_node("fact_1", past, invalid_at=None, created_at=past, expired_at=None),       # Active
        create_test_node("fact_2", past, invalid_at=past, created_at=past, expired_at=None),       # Invalid
        create_test_node("fact_3", past, invalid_at=None, created_at=past, expired_at=past),       # Expired
    ]

    query = TemporalQuery(query_type=TemporalQueryType.CURRENT)
    results = query.execute(items)

    assert len(results) == 1
    assert results[0]["name"] == "fact_1"
    print("  [OK] Current state query returns only active facts")


def test_temporal_query_point_in_time():
    """Test TemporalQuery for point-in-time queries"""
    print("\n[TEST] TemporalQuery - POINT_IN_TIME")

    now = utc_now()
    past = now - timedelta(days=30)

    items = [
        create_test_node("fact_1", past, invalid_at=None, created_at=past, expired_at=None),
        create_test_node("fact_2", past, invalid_at=now, created_at=past, expired_at=None),  # Becomes invalid in future
    ]

    # Query valid time dimension at past (both should be valid)
    query_valid = TemporalQuery(
        query_type=TemporalQueryType.POINT_IN_TIME,
        dimension=TemporalDimension.VALID_TIME,
        as_of_time=past
    )
    results_valid = query_valid.execute(items)
    assert len(results_valid) == 2
    print("  [OK] Point-in-time query (valid dimension)")

    # Query transaction time dimension at past (both should be known)
    query_transaction = TemporalQuery(
        query_type=TemporalQueryType.POINT_IN_TIME,
        dimension=TemporalDimension.TRANSACTION_TIME,
        as_of_time=past
    )
    results_transaction = query_transaction.execute(items)
    assert len(results_transaction) == 2
    print("  [OK] Point-in-time query (transaction dimension)")


def test_temporal_query_evolution():
    """Test TemporalQuery for evolution tracking"""
    print("\n[TEST] TemporalQuery - EVOLUTION")

    now = utc_now()
    past = now - timedelta(days=30)

    node = create_test_node("rel_1", past, invalid_at=now, created_at=past, expired_at=None)

    query = TemporalQuery(
        query_type=TemporalQueryType.EVOLUTION,
        entity_filter="rel_1",
        start_time=past,
        end_time=now
    )

    evolution = query.execute([node])

    assert len(evolution) == 10  # Default sample_points
    assert all(hasattr(snapshot, "timestamp") for snapshot in evolution)
    print("  [OK] Evolution query returns temporal snapshots")


# ==============================================================================
# TEST RUNNER
# ==============================================================================

def run_all_tests():
    """Run all bitemporal pattern tests"""
    print("=" * 70)
    print("BITEMPORAL PATTERN TEST SUITE")
    print("=" * 70)

    tests = [
        # Temporal dimension checks
        test_is_currently_valid,
        test_is_currently_known,
        test_is_active,

        # Invalidation operations
        test_invalidate_fact,
        test_expire_knowledge,
        test_invalidate_and_expire,

        # Temporal query filters
        test_filter_by_valid_time,
        test_filter_by_transaction_time,
        test_filter_active,

        # Evolution tracking
        test_track_evolution,
        test_detect_belief_changes,
        test_detect_temporal_conflicts,

        # Temporal query class
        test_temporal_query_current,
        test_temporal_query_point_in_time,
        test_temporal_query_evolution,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__}")
            print(f"       {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__}")
            print(f"        {str(e)}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n[PASS] ALL BITEMPORAL TESTS PASSED")
        print("\nBitemporal pattern implementation is functioning correctly.")
        print("Consciousness substrates can now:")
        print("  - Track idsubentity evolution through two time dimensions")
        print("  - Reconstruct historical states (what we knew, what was true)")
        print("  - Handle belief changes and conflicting information")
        print("  - Support temporal reasoning about consciousness development")
        return 0
    else:
        print(f"\n[FAIL] {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
