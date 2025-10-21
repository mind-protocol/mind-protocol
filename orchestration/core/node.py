"""
Node data structure - combines multi-energy + bitemporal tracking.

ARCHITECTURAL PRINCIPLE: Core is pure data, delegates to mechanisms.

This Node class is a data container with delegation methods.
All logic lives in orchestration.mechanisms.*

Energy Architecture:
- Strictly non-negative [0.0, ∞)
- Inhibition via SUPPRESS link type, NOT negative energy
- Multi-dimensional: Dict[entity_id, energy_value]

Bitemporal Architecture:
- Reality timeline: valid_at, invalidated_at
- Knowledge timeline: created_at, expired_at

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1 Clean Break - Mechanism 01 + 13
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from .types import NodeType, EnergyDict, EntityID

if TYPE_CHECKING:
    from .link import Link


@dataclass
class Node:
    """
    Core node structure combining multi-energy + bitemporal tracking.

    This is a PURE DATA STRUCTURE. All behavior is delegated to:
    - orchestration.mechanisms.multi_energy (M01)
    - orchestration.mechanisms.bitemporal (M13)

    Energy Storage (M01):
        energy: Dict[entity_id, float] - Non-negative values only
        Each entity has independent energy on this node

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
    id: str
    name: str
    node_type: NodeType
    description: str

    # Multi-energy storage (M01)
    # CRITICAL: Energy is strictly non-negative [0.0, ∞)
    # Inhibition is implemented via SUPPRESS link type, not negative values
    energy: EnergyDict = field(default_factory=dict)

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

    # Learning Infrastructure (Phase 1-4: Consciousness Learning)
    # Long-run attractor strength in log space
    log_weight: float = 0.0
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
    # Threshold for activation (computed adaptively)
    threshold: float = 0.1

    # --- Delegation Methods (call mechanisms, don't implement) ---

    def get_entity_energy(self, entity: EntityID) -> float:
        """
        Get energy for entity on this node.

        Delegates to: orchestration.mechanisms.multi_energy.get_entity_energy()

        Args:
            entity: Entity identifier

        Returns:
            Energy value (>= 0.0), or 0.0 if entity not present
        """
        from orchestration.mechanisms.multi_energy import get_entity_energy
        return get_entity_energy(self, entity)

    def set_entity_energy(self, entity: EntityID, value: float) -> None:
        """
        Set energy for entity on this node.

        Delegates to: orchestration.mechanisms.multi_energy.set_entity_energy()

        CRITICAL: Value will be clamped to non-negative and saturated.

        Args:
            entity: Entity identifier
            value: Energy value (will be clamped to >= 0.0, saturated via tanh)
        """
        from orchestration.mechanisms.multi_energy import set_entity_energy
        set_entity_energy(self, entity, value)

    def increment_entity_energy(self, entity: EntityID, delta: float) -> None:
        """
        Add energy delta to entity on this node.

        Delegates to: orchestration.mechanisms.multi_energy.add_entity_energy()

        Can be positive (add energy) or negative (remove energy).
        Result will be clamped to non-negative and saturated.

        Args:
            entity: Entity identifier
            delta: Energy change (positive = add, negative = subtract)
        """
        from orchestration.mechanisms.multi_energy import add_entity_energy
        add_entity_energy(self, entity, delta)

    def get_total_energy(self) -> float:
        """
        Get TOTAL energy across all entities on this node.

        This is the canonical energy for sub-entity activation detection.
        Per spec: Sub-Entity = ANY node where total_energy >= threshold

        Delegates to: orchestration.mechanisms.multi_energy.get_total_energy()

        Returns:
            Sum of energy across all entity keys
        """
        from orchestration.mechanisms.multi_energy import get_total_energy
        return get_total_energy(self)

    def is_active(self) -> bool:
        """
        Is this node currently an active sub-entity?

        Per spec (05_sub_entity_system.md:1514-1522):
            Sub-Entity = ANY Active Node
            is_sub_entity(node) = total_energy >= threshold

        Returns:
            True if total_energy >= threshold
        """
        return self.get_total_energy() >= self.threshold

    def get_all_active_entities(self) -> List[EntityID]:
        """
        Get all entities with non-zero energy on this node.

        Delegates to: orchestration.mechanisms.multi_energy.get_all_active_entities()

        Returns:
            List of entity IDs with energy > 0
        """
        from orchestration.mechanisms.multi_energy import get_all_active_entities
        return get_all_active_entities(self)

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
        active_entities = len(self.energy)
        return f"Node(id={self.id!r}, name={self.name!r}, type={self.node_type.value}, entities={active_entities})"

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)
