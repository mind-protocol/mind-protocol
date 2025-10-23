"""
Link data structure - bitemporal directed relationships.

ARCHITECTURAL PRINCIPLE: Links ARE consciousness.

Links represent relationships with rich metadata:
- Who created the link (subentity)
- Why it exists (goal, mindstate)
- How strong it is (weight, energy)
- When it was true (bitemporal tracking)
- Version history (immutable versions)

Special Link Types:
- SUPPRESS: Implements inhibition (link-based, not value-based)
- DIFFUSES_TO: Energy flow relationships
- ENABLES/BLOCKS: Causal relationships

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - Added version tracking (vid, supersedes, superseded_by)
Architecture: Phase 1 Clean Break - Mechanism 13
Spec: foundations/bitemporal_tracking.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING
import uuid

from .types import LinkType, EntityID

if TYPE_CHECKING:
    from .node import Node


@dataclass
class Link:
    """
    Directed link between nodes with bitemporal tracking.

    Links carry consciousness metadata:
    - source/target: Which nodes are connected
    - link_type: What kind of relationship
    - subentity: Which subentity created this link
    - weight: Relationship strength
    - energy: Current activation energy

    Bitemporal Tracking (M13):
        valid_at: When this relationship became true in reality
        invalidated_at: When this relationship became false in reality
        created_at: When we learned about this relationship
        expired_at: When we learned it's no longer valid
    """

    # Identity (required fields first)
    id: str  # Logical relationship id (stable across versions)
    source_id: str  # Source node ID
    target_id: str  # Target node ID
    link_type: LinkType
    subentity: EntityID  # Which subentity created/owns this link

    # Version tracking (V2 Bitemporal - Immutable Versions)
    vid: str = field(default_factory=lambda: f"v_{uuid.uuid4().hex[:12]}")  # Version id (immutable)
    supersedes: Optional[str] = None  # Previous version vid
    superseded_by: Optional[str] = None  # Next version vid (set when superseded)

    # Link metadata
    weight: float = 1.0  # Relationship strength (affects diffusion)
    energy: float = 0.0  # Current activation energy on link

    # Bitemporal tracking (M13) - Reality timeline
    valid_at: datetime = field(default_factory=datetime.now)
    invalidated_at: Optional[datetime] = None

    # Bitemporal tracking (M13) - Knowledge timeline
    created_at: datetime = field(default_factory=datetime.now)
    expired_at: Optional[datetime] = None

    # Consciousness metadata (from TRACE format)
    goal: Optional[str] = None  # Why this link exists
    mindstate: Optional[str] = None  # Internal state when forming
    formation_trigger: Optional[str] = None  # How discovered
    confidence: float = 1.0  # Certainty in this relationship

    # Type-specific properties
    properties: Dict[str, any] = field(default_factory=dict)

    # Learning Infrastructure (Phase 1-4: Consciousness Learning)
    # Long-run pathway strength in log space
    log_weight: float = 0.0
    # Exponential moving average of TRACE reinforcement seats for links
    ema_trace_seats: float = 0.0
    # Exponential moving average of gap-closure utility (recruitment effectiveness)
    ema_phi: float = 0.0
    # Causal credit accumulator for forward direction
    precedence_forward: float = 0.0
    # Causal credit accumulator for backward direction
    precedence_backward: float = 0.0
    # Timestamp of last update
    last_update_timestamp: Optional[datetime] = None
    # Link scope for cohort grouping
    scope: str = "organizational"
    # Exponential moving average of formation quality
    ema_formation_quality: float = 0.0

    # Reference to actual nodes (populated by Graph)
    source: Optional['Node'] = field(default=None, repr=False)
    target: Optional['Node'] = field(default=None, repr=False)

    # --- Delegation Methods ---

    def is_currently_valid(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if link is valid at given time (reality timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_valid()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if link valid at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_valid
        return is_currently_valid(self, at_time)

    def is_currently_known(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if link is known at given time (knowledge timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_known()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if link known at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_known
        return is_currently_known(self, at_time)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (f"Link(id={self.id!r}, {self.source_id} --[{self.link_type.value}]--> "
                f"{self.target_id}, subentity={self.subentity}, weight={self.weight:.2f})")

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)
