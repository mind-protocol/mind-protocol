"""
Mechanism 13: Bitemporal Tracking - Pure Functions

BITEMPORAL ARCHITECTURE:
Two independent timelines track consciousness evolution:

1. Reality Timeline (valid_at, invalidated_at):
   - When did this node/link become TRUE in reality?
   - When did it become FALSE in reality?

2. Knowledge Timeline (created_at, expired_at):
   - When did WE LEARN about this node/link?
   - When did we learn it's no longer valid?

Why Both Timelines Matter:
- "Nicolas created Mind Protocol in 2023" (reality)
- "I learned about this on 2025-10-19" (knowledge)

Queries:
- What was true on date X? (reality timeline)
- What did we know on date X? (knowledge timeline)
- When did our understanding change? (knowledge timeline)

Supersession:
- New nodes can supersede old nodes (SUPERSEDES link)
- Old node gets invalidated_at = new_node.valid_at
- Preserves history while marking current truth

Author: Felix (Engineer)
Created: 2025-10-19
Spec: consciousness_engine_architecture/implementation/mechanisms/13_bitemporal_implementation.md
"""

from datetime import datetime
from typing import Optional, Union, TYPE_CHECKING

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


# --- Supersession ---

def supersede(old_obj: BitemporalObject, new_obj: BitemporalObject) -> None:
    """
    Mark old object as superseded by new object.

    This sets old_obj.invalidated_at = new_obj.valid_at, creating a
    clean temporal handoff in reality timeline.

    Note: You should also create a SUPERSEDES link between the objects.

    Args:
        old_obj: Object being superseded
        new_obj: Object superseding it

    Example:
        >>> old_node = Node(id="n1", valid_at=datetime(2025, 1, 1), ...)
        >>> new_node = Node(id="n2", valid_at=datetime(2025, 6, 1), ...)
        >>> supersede(old_node, new_node)
        >>> old_node.invalidated_at
        datetime(2025, 6, 1)
    """
    old_obj.invalidated_at = new_obj.valid_at


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

    return True
