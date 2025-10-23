"""
Type definitions and enums for consciousness engine core.

Author: Felix (Engineer)
Created: 2025-10-19
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class NodeType(Enum):
    """Node types in consciousness graph."""
    # Core consciousness types
    MEMORY = "Memory"
    REALIZATION = "Realization"
    CONCEPT = "Concept"
    PRINCIPLE = "Principle"
    MECHANISM = "Mechanism"

    # Multi-scale consciousness (Phase 7)
    SUBENTITY = "Subentity"

    # Subentity types
    AI_AGENT = "AI_Agent"
    HUMAN = "Human"

    # Task types
    TASK = "Task"
    GOAL = "Goal"

    # Pattern types
    PATTERN = "Pattern"
    ANTI_PATTERN = "Anti_Pattern"

    # Add more as needed from COMPLETE_TYPE_REFERENCE.md


class LinkType(Enum):
    """Link types in consciousness graph."""
    # Core relationships
    ENABLES = "ENABLES"
    BLOCKS = "BLOCKS"
    REQUIRES = "REQUIRES"
    CONTAINS = "CONTAINS"
    INSTANCE_OF = "INSTANCE_OF"

    # Multi-scale consciousness (Phase 7)
    BELONGS_TO = "BELONGS_TO"  # Node -> Subentity membership
    RELATES_TO = "RELATES_TO"  # Subentity -> Subentity boundary

    # Energy flow
    DIFFUSES_TO = "DIFFUSES_TO"
    SUPPRESS = "SUPPRESS"  # Inhibition is link-based, not value-based

    # Temporal
    SUPERSEDES = "SUPERSEDES"
    EVOLVES_INTO = "EVOLVES_INTO"

    # Add more as needed from COMPLETE_TYPE_REFERENCE.md


# Type aliases for clarity
EntityID = str
NodeID = str
EnergyDict = Dict[EntityID, float]
Timestamp = datetime
