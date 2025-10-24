"""
Node data structure - single-energy + bitemporal tracking.

ARCHITECTURAL PRINCIPLE: Core is pure data, delegates to mechanisms.

This Node class is a data container with delegation methods.
All logic lives in orchestration.mechanisms.*

Energy Architecture (V2 - Single Energy):
- Strictly non-negative [0.0, ∞)
- Single scalar E per node (not per-entity)
- Entity differentiation via membership and selection, not energy buffers
- Inhibition via SUPPRESS link type, NOT negative energy

Bitemporal Architecture (V2 - Immutable Versions):
- Reality timeline: valid_at, invalidated_at
- Knowledge timeline: created_at, expired_at
- Version tracking: vid (immutable), supersedes/superseded_by (version chain)

Author: Felix (Engineer)
Created: 2025-10-19
Updated: 2025-10-22 - Added version tracking (vid, supersedes, superseded_by)
Architecture: V2 Stride-Based Diffusion - foundations/diffusion.md
Spec: foundations/bitemporal_tracking.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING
import uuid

from .types import NodeType, EnergyDict, EntityID

if TYPE_CHECKING:
    from .link import Link


@dataclass
class Node:
    """
    Core node structure with single-energy + bitemporal tracking.

    This is a PURE DATA STRUCTURE. All behavior is delegated to:
    - orchestration.mechanisms.diffusion (stride-based energy transfer)
    - orchestration.mechanisms.decay (exponential forgetting)
    - orchestration.mechanisms.bitemporal (M13)

    Energy Storage (V2 Single-Energy):
        E: float - Activation energy (non-negative scalar)
        theta: float - Activation threshold (adaptive)
        Entity differentiation via membership, not per-entity buffers

    Bitemporal Tracking (M13):
        valid_at: When this node became true in reality
        invalidated_at: When this node became false in reality
        created_at: When we learned about this node
        expired_at: When we learned it's no longer valid

    Graph Structure:
        outgoing_links: Links where this node is source
        incoming_links: Links where this node is target
    """

    # Identity
    id: str  # Logical entity id (stable across versions)
    name: str
    node_type: NodeType
    description: str

    # Version tracking (V2 Bitemporal - Immutable Versions)
    vid: str = field(default_factory=lambda: f"v_{uuid.uuid4().hex[:12]}")  # Version id (immutable)
    supersedes: Optional[str] = None  # Previous version vid
    superseded_by: Optional[str] = None  # Next version vid (set when superseded)

    # Single-energy storage (V2)
    # CRITICAL: Energy is strictly non-negative [0.0, ∞)
    # Inhibition is implemented via SUPPRESS link type, not negative values
    E: float = 0.0  # Activation energy (single scalar, not per-entity)

    # Bitemporal tracking (M13) - Reality timeline
    valid_at: datetime = field(default_factory=datetime.now)
    invalidated_at: Optional[datetime] = None

    # Bitemporal tracking (M13) - Knowledge timeline
    created_at: datetime = field(default_factory=datetime.now)
    expired_at: Optional[datetime] = None

    # Graph structure (populated by Graph container)
    outgoing_links: List['Link'] = field(default_factory=list)
    incoming_links: List['Link'] = field(default_factory=list)

    # Metadata
    properties: Dict[str, any] = field(default_factory=dict)

    # Emotion metadata (separate from activation - affects cost only)
    emotion_vector: Optional[any] = None  # 2D affect vector [valence, arousal]

    # Learning Infrastructure (Phase 1-4: Consciousness Learning)
    # Long-run attractor strength in log space
    log_weight: float = 0.0
    # Entity-specific weight overlays (Priority 4: Entity Context Tracking)
    # Sparse dict: {entity_id: delta}
    # Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
    # Updated by TRACE marks with entity_context (80% local, 20% global)
    log_weight_overlays: Dict[str, float] = field(default_factory=dict)
    # Exponential moving average of TRACE reinforcement seats
    ema_trace_seats: float = 0.0
    # Exponential moving average of working memory selection frequency
    ema_wm_presence: float = 0.0
    # Exponential moving average of formation quality
    ema_formation_quality: float = 0.0
    # Timestamp of most recent non-zero weight update (for adaptive learning rate)
    last_update_timestamp: Optional[datetime] = None
    # Node scope for cohort grouping (personal/organizational/ecosystem)
    scope: str = "personal"
    # Threshold for activation (adaptive, computed from μ + z·σ)
    theta: float = 0.1

    # --- Energy Methods (V2 Single-Energy) ---

    def is_active(self) -> bool:
        """
        Is this node currently active?

        Per V2 spec (foundations/diffusion.md):
            Active = E >= theta (activation threshold)

        Returns:
            True if E >= theta
        """
        return self.E >= self.theta

    def add_energy(self, delta: float) -> None:
        """
        Add energy delta to this node (used by diffusion staging).

        Args:
            delta: Energy change (can be positive or negative)

        Side effects:
            Updates self.E, clamped to [0.0, ∞)
        """
        self.E = max(0.0, self.E + delta)

    def is_currently_valid(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if node is valid at given time (reality timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_valid()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if node valid at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_valid
        return is_currently_valid(self, at_time)

    def is_currently_known(self, at_time: Optional[datetime] = None) -> bool:
        """
        Check if node is known at given time (knowledge timeline).

        Delegates to: orchestration.mechanisms.bitemporal.is_currently_known()

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if node known at given time
        """
        from orchestration.mechanisms.bitemporal import is_currently_known
        return is_currently_known(self, at_time)

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"Node(id={self.id!r}, name={self.name!r}, type={self.node_type.value}, E={self.E:.3f}, theta={self.theta:.3f})"

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)
