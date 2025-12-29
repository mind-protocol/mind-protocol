"""
Node type definitions for Mind Protocol schema v1.8.1.

DOCS: docs/l4/schema/IMPLEMENTATION_Schema.md
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import time


class NodeType(str, Enum):
    """The 5 canonical node types. Schema is fixed — no custom types allowed."""

    ACTOR = "actor"
    MOMENT = "moment"
    NARRATIVE = "narrative"
    SPACE = "space"
    THING = "thing"


class MomentStatus(str, Enum):
    """Status of a moment node."""

    POSSIBLE = "possible"
    ACTIVE = "active"
    COMPLETED = "completed"


class NodeBase(BaseModel):
    """
    Base schema for all nodes in Mind Protocol.

    All custom data goes in `content` and `synthesis` fields.
    No custom fields allowed — schema is fixed.
    """

    # Identity
    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Display name")
    node_type: NodeType = Field(..., description="One of 5 canonical types")
    type: Optional[str] = Field(None, description="Subtype within node_type")

    # Physics
    weight: float = Field(1.0, ge=0, description="Importance [0, ∞)")
    energy: float = Field(0.0, ge=0, description="Current activation [0, ∞)")

    # Semantics
    synthesis: str = Field(..., description="Natural language summary for embedding")
    embedding: Optional[List[float]] = Field(None, description="embed(synthesis), 1536 dims")
    content: str = Field("", description="Full prose/description")

    # Temporal (auto-managed)
    created_at_s: int = Field(default_factory=lambda: int(time.time()))
    updated_at_s: int = Field(default_factory=lambda: int(time.time()))
    last_traversed_at_s: Optional[int] = Field(None)

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None and len(v) != 1536:
            raise ValueError(f"Embedding must have 1536 dimensions, got {len(v)}")
        return v

    model_config = {
        "extra": "forbid",  # No custom fields allowed
    }


class MomentBase(NodeBase):
    """
    Extended schema for moment nodes.

    Moments are the only node type where branching occurs.
    They track timing for duration calculation.
    """

    node_type: NodeType = Field(NodeType.MOMENT, frozen=True)

    # Moment-specific fields
    status: MomentStatus = Field(MomentStatus.POSSIBLE)
    tick_created: int = Field(0)
    tick_resolved: Optional[int] = Field(None)

    # Timing (auto-managed)
    started_at_s: Optional[int] = Field(None, description="When moment became active")
    completed_at_s: Optional[int] = Field(None, description="When moment was resolved")

    @property
    def duration_s(self) -> Optional[int]:
        """Computed: completed_at_s - started_at_s."""
        if self.completed_at_s is not None and self.started_at_s is not None:
            return self.completed_at_s - self.started_at_s
        return None


class ActorNode(NodeBase):
    """Actor nodes: entities that act (citizens, agents, verifiers)."""

    node_type: NodeType = Field(NodeType.ACTOR, frozen=True)


class NarrativeNode(NodeBase):
    """Narrative nodes: concepts, beliefs, metadata, documentation."""

    node_type: NodeType = Field(NodeType.NARRATIVE, frozen=True)


class SpaceNode(NodeBase):
    """Space nodes: containers, modules, orgs."""

    node_type: NodeType = Field(NodeType.SPACE, frozen=True)


class ThingNode(NodeBase):
    """Thing nodes: actual artifacts (files, URIs, wallets, endpoints)."""

    node_type: NodeType = Field(NodeType.THING, frozen=True)

    # Thing-specific
    uri: Optional[str] = Field(None, description="URI if applicable")
