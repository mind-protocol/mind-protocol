"""
Entity data structure - multi-scale consciousness neighborhoods.

ARCHITECTURAL PRINCIPLE: Entities are neighborhoods with activation state.

Two types:
- Functional entities: Cognitive roles (The Translator, The Architect)
- Semantic entities: Topic clusters (consciousness_architecture, learning_mechanisms)

Both are chunks with aggregate energy, dynamic thresholds, and lifecycle management.

Biological plausibility: Brain operates on neural assemblies, cortical columns,
not individual neurons.

Phenomenological match: Working memory holds 7±2 chunks (Miller's law), not atoms.
Attention focuses on topics, not scattered facts.

Computational benefit: Entity-to-entity transitions reduce branching factor 30-100×
before drilling to nodes.

Author: Felix (Engineer)
Created: 2025-10-21
Architecture: Phase 7 - Multi-Scale Consciousness (Entity Layer)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import numpy as np

from .types import NodeType

if TYPE_CHECKING:
    from .node import Node
    from .link import Link


@dataclass
class Entity:
    """
    Multi-scale consciousness neighborhood (functional role or semantic topic).

    This is a PURE DATA STRUCTURE for entity state.
    All behavior is delegated to orchestration.mechanisms.*

    Entity Types:
        entity_kind="functional" - Cognitive roles (The Translator, etc.)
        entity_kind="semantic" - Topic clusters (consciousness_architecture, etc.)

    Lifecycle States:
        "candidate" - Runtime aggregate, not persisted
        "provisional" - Persisted but mutable (can merge/split)
        "mature" - Stable, sustained high quality

    Runtime State (computed from members each frame):
        energy_runtime - Aggregate member energy
        threshold_runtime - Dynamic activation threshold
        activation_level_runtime - "dominant"|"strong"|"moderate"|"weak"|"absent"
    """

    # Identity
    id: str
    entity_kind: str  # "functional" | "semantic"
    role_or_topic: str  # "translator" | "consciousness_architecture" | etc.
    description: str

    # Semantic representation
    centroid_embedding: Optional[np.ndarray] = None  # 768 or 1536 dims

    # Runtime state (computed from members, not persisted)
    energy_runtime: float = 0.0
    threshold_runtime: float = 1.0
    activation_level_runtime: str = "absent"

    # Structural quality
    coherence_ema: float = 0.0  # How tight is this cluster
    member_count: int = 0

    # Learning Infrastructure (same as nodes)
    ema_active: float = 0.0  # EMA of "was entity active this frame"
    log_weight: float = 0.0  # Long-run importance
    ema_wm_presence: float = 0.0  # EMA of working memory selection
    ema_trace_seats: float = 0.0  # EMA of TRACE reinforcement
    ema_formation_quality: float = 0.0  # EMA of formation quality

    # Lifecycle state
    stability_state: str = "candidate"  # "candidate"|"provisional"|"mature"
    quality_score: float = 0.0  # Geometric mean of 5 quality signals
    last_quality_update: Optional[datetime] = None

    # Quality tracking (for promotion/dissolution)
    frames_since_creation: int = 0
    high_quality_streak: int = 0
    low_quality_streak: int = 0

    # Provenance
    created_from: str = "unknown"  # "role_seed"|"semantic_clustering"|"co_activation"|"trace_formation"

    # Bitemporal tracking (same as nodes)
    valid_at: datetime = field(default_factory=datetime.now)
    invalidated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    expired_at: Optional[datetime] = None

    # Consciousness metadata (same as nodes)
    confidence: float = 1.0
    formation_trigger: str = "systematic_analysis"

    # Provenance (same as nodes)
    created_by: str = "unknown"
    substrate: str = "organizational"
    scope: str = "organizational"  # personal/organizational/ecosystem

    # Last update timestamp (for adaptive learning)
    last_update_timestamp: Optional[datetime] = None

    # Graph structure (populated by Graph container)
    # Members: accessed via BELONGS_TO links (Node -> Entity)
    # Boundaries: accessed via RELATES_TO links (Entity -> Entity)
    outgoing_links: List['Link'] = field(default_factory=list)
    incoming_links: List['Link'] = field(default_factory=list)

    # Metadata
    properties: dict = field(default_factory=dict)

    # --- Helper Methods ---

    def get_members(self) -> List['Node']:
        """
        Get all nodes that belong to this entity.

        Returns nodes connected via BELONGS_TO links.
        """
        from .types import LinkType
        return [link.source for link in self.incoming_links
                if link.link_type == LinkType.BELONGS_TO]

    def get_related_entities(self) -> List['Entity']:
        """
        Get all entities this entity relates to.

        Returns entities connected via outgoing RELATES_TO links.
        """
        from .types import LinkType
        return [link.target for link in self.outgoing_links
                if link.link_type == LinkType.RELATES_TO]

    def is_active(self) -> bool:
        """Check if entity is currently active (above threshold)."""
        return self.energy_runtime >= self.threshold_runtime

    def is_flipping(self, previous_energy: float) -> bool:
        """
        Check if entity is crossing threshold (flip event).

        Args:
            previous_energy: Energy value from previous frame

        Returns:
            True if crossing threshold this frame
        """
        return (self.energy_runtime >= self.threshold_runtime and
                previous_energy < self.threshold_runtime)

    def is_candidate(self) -> bool:
        """Check if entity is in candidate state (not persisted)."""
        return self.stability_state == "candidate"

    def is_provisional(self) -> bool:
        """Check if entity is in provisional state (persisted but mutable)."""
        return self.stability_state == "provisional"

    def is_mature(self) -> bool:
        """Check if entity is in mature state (stable)."""
        return self.stability_state == "mature"

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (f"Entity(id={self.id!r}, kind={self.entity_kind}, "
                f"role_or_topic={self.role_or_topic!r}, "
                f"stability={self.stability_state}, "
                f"members={self.member_count}, "
                f"energy={self.energy_runtime:.2f}, "
                f"threshold={self.threshold_runtime:.2f})")

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)
