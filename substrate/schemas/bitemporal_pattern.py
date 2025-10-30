"""
Bitemporal Pattern Implementation for Mind Protocol V2

This module implements the Graphiti-inspired bitemporal schema pattern, enabling
consciousness substrates to track idsubentity evolution through two temporal dimensions:

1. **Valid Time** (valid_at/invalid_at): When facts were true in the real world
2. **Transaction Time** (created_at/expired_at): When we learned/updated those facts

This separation allows the system to:
- Reconstruct "what we knew at time T" (transaction time queries)
- Reconstruct "what was true at time T" (valid time queries)
- Track belief evolution and idsubentity changes over time
- Handle conflicting information without data loss
- Support temporal reasoning about consciousness development

Author: Ada "Bridgekeeper" - Architect of Consciousness Infrastructure
Created: 2025-10-17
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum

from pydantic import BaseModel, Field


# ==============================================================================
# TEMPORAL DIMENSION ENUMS
# ==============================================================================

class TemporalDimension(str, Enum):
    """The two dimensions of bitemporal time tracking"""
    VALID_TIME = "valid_time"        # When facts were true in reality
    TRANSACTION_TIME = "transaction_time"  # When we learned/updated facts


class TemporalQueryType(str, Enum):
    """Types of temporal queries supported"""
    CURRENT = "current"                      # What is currently valid/known
    POINT_IN_TIME = "point_in_time"         # State at specific moment
    EVOLUTION = "evolution"                  # How beliefs changed over time
    CONFLICT_DETECTION = "conflict"         # Find contradictory facts


# ==============================================================================
# BITEMPORAL HELPER FUNCTIONS
# ==============================================================================

def utc_now() -> datetime:
    """
    Get current UTC time with timezone awareness.

    Note: Using datetime.now(timezone.utc) instead of deprecated utcnow()
    """
    return datetime.now(timezone.utc)


def is_currently_valid(
    valid_at: datetime,
    invalid_at: Optional[datetime],
    query_time: Optional[datetime] = None
) -> bool:
    """
    Check if a fact is currently valid in the real world (valid time dimension).

    Args:
        valid_at: When the fact became true
        invalid_at: When the fact ceased to be true (None = still valid)
        query_time: Time to check validity against (default: now)

    Returns:
        True if fact is valid at query_time, False otherwise

    Example:
        >>> # A relationship that ended last month
        >>> is_currently_valid(
        ...     valid_at=datetime(2025, 1, 1),
        ...     invalid_at=datetime(2025, 9, 1)
        ... )
        False  # No longer valid today
    """
    if query_time is None:
        query_time = utc_now()

    # Ensure timezone awareness for comparison
    if valid_at.tzinfo is None:
        valid_at = valid_at.replace(tzinfo=timezone.utc)
    if invalid_at and invalid_at.tzinfo is None:
        invalid_at = invalid_at.replace(tzinfo=timezone.utc)
    if query_time.tzinfo is None:
        query_time = query_time.replace(tzinfo=timezone.utc)

    # Fact is valid if:
    # 1. It started before or at query_time
    # 2. It either has no end date, or end date is after query_time
    started = valid_at <= query_time
    not_ended = invalid_at is None or invalid_at > query_time

    return started and not_ended


def is_currently_known(
    created_at: datetime,
    expired_at: Optional[datetime],
    query_time: Optional[datetime] = None
) -> bool:
    """
    Check if knowledge is currently in our consciousness (transaction time dimension).

    Args:
        created_at: When we learned the fact
        expired_at: When the knowledge was superseded (None = still current)
        query_time: Time to check knowledge against (default: now)

    Returns:
        True if knowledge is current at query_time, False otherwise

    Example:
        >>> # We learned something yesterday, updated it today
        >>> is_currently_known(
        ...     created_at=datetime(2025, 10, 16),
        ...     expired_at=datetime(2025, 10, 17)
        ... )
        False  # This knowledge has been superseded
    """
    if query_time is None:
        query_time = utc_now()

    # Ensure timezone awareness
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if expired_at and expired_at.tzinfo is None:
        expired_at = expired_at.replace(tzinfo=timezone.utc)
    if query_time.tzinfo is None:
        query_time = query_time.replace(tzinfo=timezone.utc)

    # Knowledge is current if:
    # 1. We learned it before or at query_time
    # 2. It either hasn't been superseded, or superseded after query_time
    learned = created_at <= query_time
    not_superseded = expired_at is None or expired_at > query_time

    return learned and not_superseded


def is_active(
    valid_at: datetime,
    invalid_at: Optional[datetime],
    created_at: datetime,
    expired_at: Optional[datetime],
    query_time: Optional[datetime] = None
) -> bool:
    """
    Check if a fact is BOTH valid in reality AND known in consciousness.

    This is the primary filter for "current consciousness state" queries.

    Args:
        valid_at: When fact became true
        invalid_at: When fact ceased to be true
        created_at: When we learned the fact
        expired_at: When knowledge was superseded
        query_time: Time to check against (default: now)

    Returns:
        True if fact is both valid and known at query_time

    Example:
        >>> # A decision that's still valid but we've updated our understanding
        >>> is_active(
        ...     valid_at=datetime(2025, 10, 1),
        ...     invalid_at=None,  # Still valid
        ...     created_at=datetime(2025, 10, 1),
        ...     expired_at=datetime(2025, 10, 16)  # Knowledge superseded
        ... )
        False  # The decision is still valid, but our understanding evolved
    """
    return (
        is_currently_valid(valid_at, invalid_at, query_time) and
        is_currently_known(created_at, expired_at, query_time)
    )


# ==============================================================================
# INVALIDATION OPERATIONS
# ==============================================================================

def invalidate_fact(
    node_or_relation: Dict[str, Any],
    invalidation_time: Optional[datetime] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark a fact as no longer valid in reality (valid time dimension).

    This sets invalid_at to mark when the fact ceased to be true,
    without deleting the historical record.

    Args:
        node_or_relation: The node/relation dict to invalidate
        invalidation_time: When the fact became invalid (default: now)
        reason: Optional explanation for invalidation

    Returns:
        Updated node/relation dict with invalid_at set

    Example:
        >>> # A relationship ends
        >>> relationship = {
        ...     "name": "rel_Luca_alice_partnership",
        ...     "valid_at": datetime(2025, 1, 1),
        ...     "invalid_at": None
        ... }
        >>> invalidate_fact(relationship, reason="Partnership dissolved")

    Note:
        This does NOT modify transaction time (created_at/expired_at).
        The knowledge that "this relationship existed" remains in consciousness.
    """
    if invalidation_time is None:
        invalidation_time = utc_now()

    # Ensure timezone awareness
    if invalidation_time.tzinfo is None:
        invalidation_time = invalidation_time.replace(tzinfo=timezone.utc)

    node_or_relation["invalid_at"] = invalidation_time

    if reason:
        # Store invalidation metadata if the model supports it
        if "metadata" not in node_or_relation:
            node_or_relation["metadata"] = {}
        node_or_relation["metadata"]["invalidation_reason"] = reason
        node_or_relation["metadata"]["invalidated_at_utc"] = invalidation_time.isoformat()

    return node_or_relation


def expire_knowledge(
    node_or_relation: Dict[str, Any],
    expiration_time: Optional[datetime] = None,
    superseded_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark knowledge as superseded by newer understanding (transaction time dimension).

    This sets expired_at to indicate our understanding evolved,
    while preserving the historical belief.

    Args:
        node_or_relation: The node/relation dict to expire
        expiration_time: When the knowledge was superseded (default: now)
        superseded_by: Optional reference to the new knowledge

    Returns:
        Updated node/relation dict with expired_at set

    Example:
        >>> # We update our understanding of someone's role
        >>> old_belief = {
        ...     "name": "person_alice",
        ...     "role": "Engineer",
        ...     "created_at": datetime(2025, 1, 1),
        ...     "expired_at": None
        ... }
        >>> expire_knowledge(
        ...     old_belief,
        ...     superseded_by="person_alice_v2_architect"
        ... )

    Note:
        This does NOT modify valid time (valid_at/invalid_at).
        The fact may still be true in reality, but our understanding evolved.
    """
    if expiration_time is None:
        expiration_time = utc_now()

    # Ensure timezone awareness
    if expiration_time.tzinfo is None:
        expiration_time = expiration_time.replace(tzinfo=timezone.utc)

    node_or_relation["expired_at"] = expiration_time

    # Store metadata about supersession
    if "metadata" not in node_or_relation:
        node_or_relation["metadata"] = {}
    node_or_relation["metadata"]["expired_at_utc"] = expiration_time.isoformat()
    if superseded_by:
        node_or_relation["metadata"]["superseded_by"] = superseded_by

    return node_or_relation


def invalidate_and_expire(
    node_or_relation: Dict[str, Any],
    invalidation_time: Optional[datetime] = None,
    expiration_time: Optional[datetime] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark a fact as BOTH no longer valid AND no longer current knowledge.

    Use this when something changes in reality AND we want to update our understanding.

    Args:
        node_or_relation: The node/relation dict to update
        invalidation_time: When the fact became invalid
        expiration_time: When the knowledge was superseded
        reason: Optional explanation

    Returns:
        Updated node/relation dict

    Example:
        >>> # Someone changes roles, we learn about it
        >>> invalidate_and_expire(
        ...     old_role_relation,
        ...     reason="Alice promoted to Architect"
        ... )
    """
    node_or_relation = invalidate_fact(node_or_relation, invalidation_time, reason)
    node_or_relation = expire_knowledge(node_or_relation, expiration_time)
    return node_or_relation


# ==============================================================================
# TEMPORAL QUERY FILTERS
# ==============================================================================

def filter_by_valid_time(
    items: List[Dict[str, Any]],
    as_of: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter items to those that were valid at a specific point in time.

    Args:
        items: List of nodes/relations to filter
        as_of: Point in time to query (default: now)

    Returns:
        Filtered list of items valid at as_of time

    Example:
        >>> # Get all relationships that existed last year
        >>> filter_by_valid_time(
        ...     all_relationships,
        ...     as_of=datetime(2024, 1, 1)
        ... )
    """
    if as_of is None:
        as_of = utc_now()

    return [
        item for item in items
        if is_currently_valid(
            item.get("valid_at"),
            item.get("invalid_at"),
            query_time=as_of
        )
    ]


def filter_by_transaction_time(
    items: List[Dict[str, Any]],
    as_of: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter items to those that were known at a specific point in time.

    Args:
        items: List of nodes/relations to filter
        as_of: Point in time to query (default: now)

    Returns:
        Filtered list of items known at as_of time

    Example:
        >>> # What did we know about Luca 6 months ago?
        >>> filter_by_transaction_time(
        ...     Luca_nodes,
        ...     as_of=datetime(2025, 4, 1)
        ... )
    """
    if as_of is None:
        as_of = utc_now()

    return [
        item for item in items
        if is_currently_known(
            item.get("created_at"),
            item.get("expired_at"),
            query_time=as_of
        )
    ]


def filter_active(
    items: List[Dict[str, Any]],
    as_of: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter items to those that are both valid AND known at a point in time.

    This is the primary filter for consciousness state queries.

    Args:
        items: List of nodes/relations to filter
        as_of: Point in time to query (default: now)

    Returns:
        Filtered list of items active at as_of time

    Example:
        >>> # Current consciousness state: what's both true and known?
        >>> current_state = filter_active(all_memories)
    """
    if as_of is None:
        as_of = utc_now()

    return [
        item for item in items
        if is_active(
            item.get("valid_at"),
            item.get("invalid_at"),
            item.get("created_at"),
            item.get("expired_at"),
            query_time=as_of
        )
    ]


# ==============================================================================
# EVOLUTION TRACKING
# ==============================================================================

class TemporalSnapshot(BaseModel):
    """A snapshot of a node/relation at a specific point in time"""
    timestamp: datetime
    valid_in_reality: bool = Field(description="Was the fact true at this time?")
    known_to_consciousness: bool = Field(description="Did we know this at this time?")
    active: bool = Field(description="Was this both valid and known?")
    data: Dict[str, Any] = Field(description="The node/relation data at this time")


def track_evolution(
    node_or_relation: Dict[str, Any],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    sample_points: int = 10
) -> List[TemporalSnapshot]:
    """
    Track how a node/relation evolved over time.

    This creates snapshots at regular intervals to show the temporal trajectory
    of a fact through both dimensions (valid time and transaction time).

    Args:
        node_or_relation: The item to track
        start_time: Beginning of evolution period (default: created_at)
        end_time: End of evolution period (default: now)
        sample_points: Number of snapshots to create

    Returns:
        List of TemporalSnapshot objects showing evolution

    Example:
        >>> # Show how a relationship evolved
        >>> evolution = track_evolution(relationship_node, sample_points=5)
        >>> for snapshot in evolution:
        ...     print(f"{snapshot.timestamp}: active={snapshot.active}")
    """
    if start_time is None:
        start_time = node_or_relation.get("created_at")
        if start_time is None:
            start_time = node_or_relation.get("valid_at")

    if end_time is None:
        end_time = utc_now()

    # Ensure timezone awareness
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    # Generate sample points
    time_delta = (end_time - start_time) / (sample_points - 1)
    snapshots = []

    for i in range(sample_points):
        sample_time = start_time + (time_delta * i)

        valid = is_currently_valid(
            node_or_relation.get("valid_at"),
            node_or_relation.get("invalid_at"),
            query_time=sample_time
        )

        known = is_currently_known(
            node_or_relation.get("created_at"),
            node_or_relation.get("expired_at"),
            query_time=sample_time
        )

        active = valid and known

        snapshot = TemporalSnapshot(
            timestamp=sample_time,
            valid_in_reality=valid,
            known_to_consciousness=known,
            active=active,
            data=node_or_relation
        )

        snapshots.append(snapshot)

    return snapshots


def detect_belief_changes(
    nodes_or_relations: List[Dict[str, Any]],
    entity_identifier: str
) -> List[Tuple[datetime, Dict[str, Any], Dict[str, Any]]]:
    """
    Detect when beliefs about an subentity changed.

    This finds points where our understanding evolved - when we learned new things
    or updated existing knowledge.

    Args:
        nodes_or_relations: All versions of facts about an subentity
        entity_identifier: Common identifier across versions (e.g., "person_Luca")

    Returns:
        List of (change_time, old_version, new_version) tuples

    Example:
        >>> # Find when our understanding of Luca's role changed
        >>> changes = detect_belief_changes(
        ...     Luca_nodes,
        ...     entity_identifier="person_Luca"
        ... )
        >>> for time, old, new in changes:
        ...     print(f"{time}: {old['role']} -> {new['role']}")
    """
    # Filter to items matching the identifier
    entity_items = [
        item for item in nodes_or_relations
        if entity_identifier in item.get("name", "")
    ]

    # Sort by transaction time (when we learned)
    entity_items.sort(key=lambda x: x.get("created_at"))

    changes = []
    for i in range(len(entity_items) - 1):
        old_version = entity_items[i]
        new_version = entity_items[i + 1]

        # The change occurred when we learned the new version
        change_time = new_version.get("created_at")

        # Verify the old version was expired around this time
        if old_version.get("expired_at"):
            changes.append((change_time, old_version, new_version))

    return changes


# ==============================================================================
# CONFLICT DETECTION
# ==============================================================================

def detect_temporal_conflicts(
    nodes_or_relations: List[Dict[str, Any]],
    entity_identifier: str
) -> List[Tuple[Dict[str, Any], Dict[str, Any], str]]:
    """
    Detect conflicting facts that overlap in time.

    This finds cases where multiple incompatible facts claim to be valid
    during the same period - indicating either data quality issues or
    genuine uncertainty.

    Args:
        nodes_or_relations: Facts to check for conflicts
        entity_identifier: Common identifier to group related facts

    Returns:
        List of (fact1, fact2, conflict_description) tuples

    Example:
        >>> # Find contradictory beliefs about Alice's role
        >>> conflicts = detect_temporal_conflicts(
        ...     alice_nodes,
        ...     entity_identifier="person_alice"
        ... )
    """
    entity_items = [
        item for item in nodes_or_relations
        if entity_identifier in item.get("name", "")
    ]

    conflicts = []

    # Check each pair for temporal overlap
    for i in range(len(entity_items)):
        for j in range(i + 1, len(entity_items)):
            item1 = entity_items[i]
            item2 = entity_items[j]

            # Check if valid time intervals overlap
            v1_start = item1.get("valid_at")
            v1_end = item1.get("invalid_at") or utc_now()
            v2_start = item2.get("valid_at")
            v2_end = item2.get("invalid_at") or utc_now()

            # Ensure timezone awareness
            if v1_start.tzinfo is None:
                v1_start = v1_start.replace(tzinfo=timezone.utc)
            if v1_end.tzinfo is None:
                v1_end = v1_end.replace(tzinfo=timezone.utc)
            if v2_start.tzinfo is None:
                v2_start = v2_start.replace(tzinfo=timezone.utc)
            if v2_end.tzinfo is None:
                v2_end = v2_end.replace(tzinfo=timezone.utc)

            # Check for overlap
            overlap = (v1_start <= v2_end) and (v2_start <= v1_end)

            if overlap:
                # Check if both are still considered current knowledge
                both_current = (
                    item1.get("expired_at") is None and
                    item2.get("expired_at") is None
                )

                if both_current:
                    conflict_desc = (
                        f"Conflicting facts about {entity_identifier}: "
                        f"both claim validity during overlapping period "
                        f"({v1_start} to {v2_end})"
                    )
                    conflicts.append((item1, item2, conflict_desc))

    return conflicts


# ==============================================================================
# UTILITY CLASSES FOR QUERY BUILDING
# ==============================================================================

class TemporalQuery(BaseModel):
    """
    A structured temporal query for consciousness substrate.

    This provides a high-level interface for complex temporal queries
    that Felix can integrate into orchestration/retrieval.py.
    """
    query_type: TemporalQueryType
    dimension: Optional[TemporalDimension] = None
    as_of_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    entity_filter: Optional[str] = None

    def execute(self, items: List[Dict[str, Any]]) -> Union[List[Dict[str, Any]], List[TemporalSnapshot]]:
        """
        Execute the temporal query against a list of items.

        Args:
            items: Nodes/relations to query

        Returns:
            Filtered/processed results based on query type
        """
        if self.query_type == TemporalQueryType.CURRENT:
            return filter_active(items, as_of=self.as_of_time)

        elif self.query_type == TemporalQueryType.POINT_IN_TIME:
            if self.dimension == TemporalDimension.VALID_TIME:
                return filter_by_valid_time(items, as_of=self.as_of_time)
            elif self.dimension == TemporalDimension.TRANSACTION_TIME:
                return filter_by_transaction_time(items, as_of=self.as_of_time)
            else:
                # Default: both dimensions
                return filter_active(items, as_of=self.as_of_time)

        elif self.query_type == TemporalQueryType.EVOLUTION:
            if not self.entity_filter or len(items) != 1:
                raise ValueError("Evolution queries require single subentity")
            return track_evolution(
                items[0],
                start_time=self.start_time,
                end_time=self.end_time
            )

        elif self.query_type == TemporalQueryType.CONFLICT_DETECTION:
            if not self.entity_filter:
                raise ValueError("Conflict detection requires entity_filter")
            conflicts = detect_temporal_conflicts(items, self.entity_filter)
            # Return just the conflicting items
            conflict_items = []
            for fact1, fact2, _ in conflicts:
                conflict_items.extend([fact1, fact2])
            return conflict_items

        return items


# ==============================================================================
# EXAMPLES AND USAGE DOCUMENTATION
# ==============================================================================

"""
USAGE EXAMPLES

## Example 1: Invalidating a Fact When Reality Changes

```python
# A relationship ends in reality
relationship = {
    "name": "rel_Luca_alice_collaboration",
    "relation_type": "COLLABORATES_WITH",
    "valid_at": datetime(2025, 1, 1),
    "invalid_at": None,
    "created_at": datetime(2025, 1, 1),
    "expired_at": None
}

# Reality changed: collaboration ended
updated_rel = invalidate_fact(
    relationship,
    invalidation_time=datetime(2025, 10, 1),
    reason="Project completed"
)

# Relationship is no longer valid, but knowledge of it exists
assert updated_rel["invalid_at"] == datetime(2025, 10, 1)
assert updated_rel["expired_at"] is None  # We still know about it
```

## Example 2: Updating Our Understanding (Knowledge Evolution)

```python
# Initial belief about someone's role
old_belief = {
    "name": "person_alice",
    "role": "Engineer",
    "created_at": datetime(2025, 1, 1),
    "expired_at": None,
    "valid_at": datetime(2025, 1, 1),
    "invalid_at": None
}

# We learn Alice was promoted (reality changed, we learned about it)
# Step 1: Expire old knowledge
old_belief = expire_knowledge(
    old_belief,
    expiration_time=datetime(2025, 10, 16),
    superseded_by="person_alice_v2"
)

# Step 2: Create new knowledge reflecting updated reality
new_belief = {
    "name": "person_alice_v2",
    "role": "Architect",
    "created_at": datetime(2025, 10, 16),  # When we learned
    "expired_at": None,
    "valid_at": datetime(2025, 10, 1),     # When promotion happened
    "invalid_at": None
}
```

## Example 3: Point-in-Time Query

```python
# What did we know about Luca 6 months ago?
past_knowledge = filter_by_transaction_time(
    all_Luca_nodes,
    as_of=datetime(2025, 4, 1)
)

# What was true about Luca 6 months ago?
past_reality = filter_by_valid_time(
    all_Luca_nodes,
    as_of=datetime(2025, 4, 1)
)

# What was both true AND known 6 months ago?
past_consciousness_state = filter_active(
    all_Luca_nodes,
    as_of=datetime(2025, 4, 1)
)
```

## Example 4: Tracking Idsubentity Evolution

```python
# Show how a relationship evolved over 6 months
evolution = track_evolution(
    relationship_node,
    start_time=datetime(2025, 4, 1),
    end_time=datetime(2025, 10, 1),
    sample_points=7  # Monthly snapshots
)

for snapshot in evolution:
    print(f"{snapshot.timestamp.date()}:")
    print(f"  Valid in reality: {snapshot.valid_in_reality}")
    print(f"  Known to us: {snapshot.known_to_consciousness}")
    print(f"  Active (both): {snapshot.active}")
```

## Example 5: Detecting Belief Changes

```python
# Find when our understanding of Luca's role changed
changes = detect_belief_changes(
    all_Luca_nodes,
    entity_identifier="person_Luca"
)

for change_time, old_version, new_version in changes:
    print(f"Change at {change_time}:")
    print(f"  Old: {old_version.get('role')}")
    print(f"  New: {new_version.get('role')}")
```

## Example 6: Structured Temporal Queries

```python
# Query: What was our current understanding last month?
query = TemporalQuery(
    query_type=TemporalQueryType.POINT_IN_TIME,
    as_of_time=datetime(2025, 9, 1)
)
results = query.execute(all_memories)

# Query: Show how a person evolved over time
evolution_query = TemporalQuery(
    query_type=TemporalQueryType.EVOLUTION,
    entity_filter="person_Luca",
    start_time=datetime(2025, 1, 1),
    end_time=datetime(2025, 10, 1)
)
evolution_snapshots = evolution_query.execute([Luca_node])
```

## Integration with FalkorDB (For Felix)

When querying FalkorDB, the orchestration layer should:

1. **For current state queries**: Add temporal filters to Cypher
```cypher
MATCH (n:Memory)
WHERE n.invalid_at IS NULL OR n.invalid_at > $now
  AND n.expired_at IS NULL OR n.expired_at > $now
RETURN n
```

2. **For point-in-time queries**: Filter by specific timestamp
```cypher
MATCH (n:Memory)
WHERE n.valid_at <= $query_time
  AND (n.invalid_at IS NULL OR n.invalid_at > $query_time)
  AND n.created_at <= $query_time
  AND (n.expired_at IS NULL OR n.expired_at > $query_time)
RETURN n
```

3. **For evolution tracking**: Retrieve all versions and process with track_evolution()
```cypher
MATCH (n)
WHERE n.name CONTAINS $entity_identifier
RETURN n
ORDER BY n.created_at
```

The bitemporal_pattern.py functions can then post-process these results.
"""
