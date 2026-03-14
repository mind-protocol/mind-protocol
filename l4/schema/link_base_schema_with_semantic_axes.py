"""
Link schema for Mind Protocol schema v1.8.1.

DOCS: docs/l4/schema/IMPLEMENTATION_Schema.md

Single link type: `link` — all semantics in properties.
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator
import time


class LinkBase(BaseModel):
    """
    Universal link schema for Mind Protocol.

    All relationships use this single type. Semantics are encoded in properties:
    - polarity: directional flow strength
    - hierarchy: contains vs elaborates
    - permanence: speculative vs definitive
    """

    # Identity
    id: str = Field(..., description="Unique link identifier")
    node_a: str = Field(..., description="Source node ID")
    node_b: str = Field(..., description="Target node ID")

    # Physics
    weight: float = Field(1.0, ge=0, description="Importance [0, ∞)")
    energy: float = Field(0.0, ge=0, description="Current activation [0, ∞)")

    # Semantic Axes
    polarity: Tuple[float, float] = Field(
        (0.5, 0.5),
        description="[a->b, b->a] flow strength, each in [0, 1]"
    )
    hierarchy: float = Field(
        0.0,
        ge=-1,
        le=1,
        description="-1 = contains, +1 = elaborates"
    )
    permanence: float = Field(
        0.5,
        ge=0,
        le=1,
        description="0 = speculative, 1 = definitive"
    )

    # Semantics
    synthesis: Optional[str] = Field(None, description="Human-readable, regenerated on drift")
    embedding: Optional[List[float]] = Field(None, description="1536 dims, accumulates intentions")

    # Temporal (auto-managed)
    created_at_s: int = Field(default_factory=lambda: int(time.time()))
    updated_at_s: int = Field(default_factory=lambda: int(time.time()))
    last_traversed_at_s: Optional[int] = Field(None)

    @field_validator("polarity")
    @classmethod
    def validate_polarity(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        if len(v) != 2:
            raise ValueError("Polarity must be a tuple of 2 floats")
        if not (0 <= v[0] <= 1 and 0 <= v[1] <= 1):
            raise ValueError("Polarity values must be in [0, 1]")
        return v

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None and len(v) != 1536:
            raise ValueError(f"Embedding must have 1536 dimensions, got {len(v)}")
        return v

    @property
    def forward_coloration_weight(self) -> float:
        """Derived: 1 - permanence."""
        return 1 - self.permanence

    model_config = {
        "extra": "forbid",  # No custom fields allowed
    }
