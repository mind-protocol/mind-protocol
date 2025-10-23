"""
Mechanism 13: Bitemporal Tracking - Pure Functions with Immutable Versions

BITEMPORAL ARCHITECTURE V2:
Two independent timelines track consciousness evolution + version chains:

1. Reality Timeline (valid_at, invalidated_at):
   - When did this node/link become TRUE in reality?
   - When did it become FALSE in reality?

2. Knowledge Timeline (created_at, expired_at):
   - When did WE LEARN about this node/link?
   - When did we learn it's no longer valid?

3. Version Chain (vid, supersedes, superseded_by):
   - vid: Immutable version identifier
   - supersedes: Previous version vid
   - superseded_by: Next version vid (set when superseded)

Why All Three Matter:
- "Nicolas created Mind Protocol in 2023" (reality: valid_at)
- "I learned about this on 2025-10-19" (knowledge: created_at)
- "I updated my understanding on 2025-10-22" (version: new vid, supersedes old vid)

Queries:
- What was true on date X? (reality timeline)
- What did we know on date X? (knowledge timeline)
- What version was current on date X? (version chain)
- How has our understanding evolved? (version history)

Immutable Version Semantics:
- Each version has unique vid (never mutated)
- Corrections create NEW version with supersedes link
- Old version gets invalidated_at + expired_at + superseded_by

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - Added version chain semantics per v2 spec
Spec: foundations/bitemporal_tracking.md
"""

from datetime import datetime
from typing import Optional, Union, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from orchestration.core.node import Node
    from orchestration.core.link import Link

# Type alias for objects with bitemporal fields
BitemporalObject = Union['Node', 'Link']


# --- Reality Timeline Queries ---

def is_currently_valid(obj: BitemporalObject, at_time: Optional[datetime] = None) -> bool:
    """
    Check if object is valid at given time (reality timeline).

    An object is valid if:
    - valid_at <= at_time
    - invalidated_at is None OR invalidated_at > at_time

    Args:
        obj: Node or Link to check
        at_time: Time to check (defaults to now)

    Returns:
        True if object valid at given time

    Example:
        >>> node = Node(id="n1", valid_at=datetime(2025, 1, 1), ...)
        >>> is_currently_valid(node, datetime(2025, 6, 1))
        True
        >>> node.invalidated_at = datetime(2025, 5, 1)
        >>> is_currently_valid(node, datetime(2025, 6, 1))
        False
    """
    if at_time is None:
        at_time = datetime.now()

    # Must have become valid by at_time
    if obj.valid_at > at_time:
        return False

    # Must not be invalidated before at_time
    if obj.invalidated_at is not None and obj.invalidated_at <= at_time:
        return False

    return True


def invalidate(obj: BitemporalObject, invalidated_at: Optional[datetime] = None) -> None:
    """
    Mark object as no longer valid in reality.

    Args:
        obj: Node or Link to invalidate
        invalidated_at: When it became invalid (defaults to now)

    Example:
        >>> node = Node(id="n1", valid_at=datetime(2025, 1, 1), ...)
        >>> invalidate(node, datetime(2025, 6, 1))
        >>> node.invalidated_at
        datetime(2025, 6, 1)
    """
    if invalidated_at is None:
        invalidated_at = datetime.now()

    obj.invalidated_at = invalidated_at


# --- Knowledge Timeline Queries ---

def is_currently_known(obj: BitemporalObject, at_time: Optional[datetime] = None) -> bool:
    """
    Check if object is known at given time (knowledge timeline).

    An object is known if:
    - created_at <= at_time
    - expired_at is None OR expired_at > at_time

    Args:
        obj: Node or Link to check
        at_time: Time to check (defaults to now)

    Returns:
        True if object known at given time

    Example:
        >>> node = Node(id="n1", created_at=datetime(2025, 1, 1), ...)
        >>> is_currently_known(node, datetime(2025, 6, 1))
        True
        >>> node.expired_at = datetime(2025, 5, 1)
        >>> is_currently_known(node, datetime(2025, 6, 1))
        False
    """
    if at_time is None:
        at_time = datetime.now()

    # Must have been created by at_time
    if obj.created_at > at_time:
        return False

    # Must not be expired before at_time
    if obj.expired_at is not None and obj.expired_at <= at_time:
        return False

    return True


def expire(obj: BitemporalObject, expired_at: Optional[datetime] = None) -> None:
    """
    Mark object as no longer part of our knowledge.

    This doesn't mean it's invalid in reality - just that we no longer
    consider it part of our current understanding.

    Args:
        obj: Node or Link to expire
        expired_at: When it expired from knowledge (defaults to now)

    Example:
        >>> node = Node(id="n1", created_at=datetime(2025, 1, 1), ...)
        >>> expire(node, datetime(2025, 6, 1))
        >>> node.expired_at
        datetime(2025, 6, 1)
    """
    if expired_at is None:
        expired_at = datetime.now()

    obj.expired_at = expired_at


# --- Supersession (V2 with Version Chains) ---

def supersede(old_obj: BitemporalObject, new_obj: BitemporalObject) -> None:
    """
    Mark old object as superseded by new object (V2 with version chains).

    V2 Semantics (per foundations/bitemporal_tracking.md):
    1. Close reality timeline: old_obj.invalidated_at = new_obj.valid_at
    2. Close knowledge timeline: old_obj.expired_at = new_obj.created_at
    3. Link versions: old_obj.superseded_by = new_obj.vid
    4. Link versions: new_obj.supersedes = old_obj.vid

    This creates immutable version chain with clean temporal handoff
    on BOTH timelines.

    Args:
        old_obj: Object being superseded
        new_obj: Object superseding it

    Example:
        >>> old_node = Node(id="context_reconstruction", vid="v_abc123",
        ...                 valid_at=datetime(2025, 1, 1), ...)
        >>> new_node = Node(id="context_reconstruction", vid="v_def456",
        ...                 valid_at=datetime(2025, 6, 1), ...)
        >>> supersede(old_node, new_node)
        >>> old_node.invalidated_at
        datetime(2025, 6, 1)
        >>> old_node.expired_at
        datetime(2025, 6, 1)  # Assuming new_node.created_at = valid_at
        >>> old_node.superseded_by
        'v_def456'
        >>> new_node.supersedes
        'v_abc123'
    """
    # Close reality timeline (old version no longer valid)
    old_obj.invalidated_at = new_obj.valid_at

    # Close knowledge timeline (old version no longer current belief)
    old_obj.expired_at = new_obj.created_at

    # Link version chain (bidirectional pointers)
    old_obj.superseded_by = new_obj.vid
    new_obj.supersedes = old_obj.vid


# --- Temporal Range Queries ---

def was_valid_during(obj: BitemporalObject, start: datetime, end: datetime) -> bool:
    """
    Check if object was valid at ANY point during time range.

    Args:
        obj: Node or Link to check
        start: Range start time
        end: Range end time

    Returns:
        True if object valid during any part of range

    Example:
        >>> node = Node(id="n1", valid_at=datetime(2025, 3, 1),
        ...             invalidated_at=datetime(2025, 5, 1), ...)
        >>> was_valid_during(node, datetime(2025, 4, 1), datetime(2025, 6, 1))
        True
        >>> was_valid_during(node, datetime(2025, 6, 1), datetime(2025, 7, 1))
        False
    """
    # Object's validity range
    obj_start = obj.valid_at
    obj_end = obj.invalidated_at if obj.invalidated_at else datetime.max

    # Ranges overlap if start of one is before end of other
    return obj_start < end and start < obj_end


def was_known_during(obj: BitemporalObject, start: datetime, end: datetime) -> bool:
    """
    Check if object was known at ANY point during time range.

    Args:
        obj: Node or Link to check
        start: Range start time
        end: Range end time

    Returns:
        True if object known during any part of range

    Example:
        >>> node = Node(id="n1", created_at=datetime(2025, 3, 1),
        ...             expired_at=datetime(2025, 5, 1), ...)
        >>> was_known_during(node, datetime(2025, 4, 1), datetime(2025, 6, 1))
        True
        >>> was_known_during(node, datetime(2025, 6, 1), datetime(2025, 7, 1))
        False
    """
    # Object's knowledge range
    obj_start = obj.created_at
    obj_end = obj.expired_at if obj.expired_at else datetime.max

    # Ranges overlap if start of one is before end of other
    return obj_start < end and start < obj_end


# --- Temporal Distance ---

def time_since_creation(obj: BitemporalObject, reference: Optional[datetime] = None) -> float:
    """
    Get time elapsed since object creation (knowledge timeline).

    Args:
        obj: Node or Link to check
        reference: Reference time (defaults to now)

    Returns:
        Seconds since creation

    Example:
        >>> node = Node(id="n1", created_at=datetime(2025, 1, 1), ...)
        >>> time_since_creation(node, datetime(2025, 1, 2))
        86400.0  # 1 day in seconds
    """
    if reference is None:
        reference = datetime.now()

    delta = reference - obj.created_at
    return delta.total_seconds()


def time_since_valid(obj: BitemporalObject, reference: Optional[datetime] = None) -> float:
    """
    Get time elapsed since object became valid (reality timeline).

    Args:
        obj: Node or Link to check
        reference: Reference time (defaults to now)

    Returns:
        Seconds since became valid

    Example:
        >>> node = Node(id="n1", valid_at=datetime(2025, 1, 1), ...)
        >>> time_since_valid(node, datetime(2025, 1, 2))
        86400.0  # 1 day in seconds
    """
    if reference is None:
        reference = datetime.now()

    delta = reference - obj.valid_at
    return delta.total_seconds()


# --- Validation ---

def verify_bitemporal_consistency(obj: BitemporalObject) -> bool:
    """
    Verify that bitemporal fields are logically consistent.

    Checks:
    - valid_at <= invalidated_at (if invalidated)
    - created_at <= expired_at (if expired)
    - Version chain consistency (if part of chain)

    Args:
        obj: Node or Link to validate

    Returns:
        True if temporally consistent, False otherwise

    Example:
        >>> node = Node(id="n1", valid_at=datetime(2025, 1, 1),
        ...             invalidated_at=datetime(2024, 12, 1), ...)
        >>> verify_bitemporal_consistency(node)
        False  # Invalidated before valid
    """
    # Reality timeline consistency
    if obj.invalidated_at is not None:
        if obj.valid_at > obj.invalidated_at:
            return False  # Became invalid before valid

    # Knowledge timeline consistency
    if obj.expired_at is not None:
        if obj.created_at > obj.expired_at:
            return False  # Expired before created

    # Version chain consistency
    if obj.superseded_by is not None:
        # If superseded, both timelines should be closed
        if obj.invalidated_at is None or obj.expired_at is None:
            return False  # Superseded but timeline not closed

    return True


# --- Version Chain Helpers (V2) ---

def create_new_version(obj: BitemporalObject, **changes) -> BitemporalObject:
    """
    Create a new version of an object with changes applied.

    Creates a new version with:
    - New vid (auto-generated)
    - supersedes = old_obj.vid
    - Same id (logical entity)
    - Changed fields applied
    - New created_at (knowledge timeline)
    - Same or updated valid_at (reality timeline)

    Args:
        obj: Object to create new version from
        **changes: Fields to change in new version

    Returns:
        New version object (does NOT modify original)

    Example:
        >>> old_node = Node(id="context_reconstruction", vid="v_abc123", ...)
        >>> new_node = create_new_version(old_node, description="Updated understanding")
        >>> new_node.vid != old_node.vid
        True
        >>> new_node.supersedes
        'v_abc123'
        >>> new_node.id
        'context_reconstruction'  # Same logical id
    """
    from copy import deepcopy

    # Create copy
    new_obj = deepcopy(obj)

    # Generate new vid
    new_obj.vid = f"v_{uuid.uuid4().hex[:12]}"

    # Link to previous version
    new_obj.supersedes = obj.vid
    new_obj.superseded_by = None  # Not superseded yet

    # Update knowledge timeline (we just learned this)
    # Ensure new version's created_at is strictly after original
    new_created_at = datetime.now()
    if new_created_at <= obj.created_at:
        # Add 1 microsecond to ensure strict ordering
        from datetime import timedelta
        new_created_at = obj.created_at + timedelta(microseconds=1)
    new_obj.created_at = new_created_at
    new_obj.expired_at = None  # Not expired yet

    # Apply changes
    for key, value in changes.items():
        if hasattr(new_obj, key):
            setattr(new_obj, key, value)

    return new_obj


def get_version_history(
    objects: List[BitemporalObject],
    logical_id: str
) -> List[BitemporalObject]:
    """
    Get version history for a logical entity, ordered from oldest to newest.

    Args:
        objects: List of all objects (e.g., graph.nodes.values())
        logical_id: Logical entity id

    Returns:
        List of versions ordered by created_at (oldest first)

    Example:
        >>> versions = get_version_history(graph.nodes.values(), "context_reconstruction")
        >>> len(versions)
        3  # Three versions
        >>> versions[0].supersedes
        None  # First version
        >>> versions[-1].superseded_by
        None  # Latest version
    """
    # Filter to logical id
    versions = [obj for obj in objects if obj.id == logical_id]

    # Sort by created_at (knowledge timeline)
    versions.sort(key=lambda v: v.created_at)

    return versions


def get_current_version(
    objects: List[BitemporalObject],
    logical_id: str,
    as_of_knowledge: Optional[datetime] = None,
    as_of_reality: Optional[datetime] = None
) -> Optional[BitemporalObject]:
    """
    Get current version of a logical entity with optional as-of queries.

    Args:
        objects: List of all objects (e.g., graph.nodes.values())
        logical_id: Logical entity id
        as_of_knowledge: Time for knowledge timeline query (default: now)
        as_of_reality: Time for reality timeline query (default: now)

    Returns:
        Current version or None if not found

    Example:
        >>> # Get current version
        >>> current = get_current_version(graph.nodes.values(), "context_reconstruction")
        >>> current.superseded_by
        None  # Not superseded

        >>> # Time-travel query
        >>> past = get_current_version(
        ...     graph.nodes.values(),
        ...     "context_reconstruction",
        ...     as_of_knowledge=datetime(2025, 1, 1)
        ... )
    """
    # Get all versions
    versions = get_version_history(objects, logical_id)

    if not versions:
        return None

    # Filter by knowledge timeline
    if as_of_knowledge is not None:
        versions = [v for v in versions if is_currently_known(v, as_of_knowledge)]

    # Filter by reality timeline
    if as_of_reality is not None:
        versions = [v for v in versions if is_currently_valid(v, as_of_reality)]

    if not versions:
        return None

    # Return most recent version by knowledge timeline
    return max(versions, key=lambda v: v.created_at)


def is_latest_version(obj: BitemporalObject) -> bool:
    """
    Check if this is the latest version (not superseded).

    Args:
        obj: Object to check

    Returns:
        True if latest version (superseded_by is None)

    Example:
        >>> old_node = Node(id="n1", vid="v_1", superseded_by="v_2", ...)
        >>> is_latest_version(old_node)
        False
        >>> new_node = Node(id="n1", vid="v_2", superseded_by=None, ...)
        >>> is_latest_version(new_node)
        True
    """
    return obj.superseded_by is None


def count_versions(objects: List[BitemporalObject], logical_id: str) -> int:
    """
    Count versions for a logical entity (belief churn metric).

    Args:
        objects: List of all objects
        logical_id: Logical entity id

    Returns:
        Number of versions

    Example:
        >>> churn = count_versions(graph.nodes.values(), "context_reconstruction")
        >>> print(f"Belief churn: {churn} versions")
    """
    return len([obj for obj in objects if obj.id == logical_id])
