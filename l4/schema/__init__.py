"""
L4 Schema module for Mind Protocol.

DOCS: docs/l4/schema/IMPLEMENTATION_Schema.md

Exports:
- Node types and models
- Link schema
- Validation functions
- Version tracking
"""

from .node_type_enum_and_base_pydantic_models import (
    NodeType,
    MomentStatus,
    NodeBase,
    MomentBase,
    ActorNode,
    NarrativeNode,
    SpaceNode,
    ThingNode,
)

from .link_base_schema_with_semantic_axes import LinkBase

from .node_and_link_schema_validators import (
    ValidationResult,
    validate_node,
    validate_link,
    validate_graph,
    check_invariants,
)

from .schema_version_tracker_and_compatibility import (
    SCHEMA_VERSION,
    PROTOCOL_VERSION,
    VersionCompatibility,
    VersionInfo,
    check_version_compatibility,
    get_schema_version,
    get_protocol_version,
)

__all__ = [
    # Node types
    "NodeType",
    "MomentStatus",
    "NodeBase",
    "MomentBase",
    "ActorNode",
    "NarrativeNode",
    "SpaceNode",
    "ThingNode",
    # Link
    "LinkBase",
    # Validation
    "ValidationResult",
    "validate_node",
    "validate_link",
    "validate_graph",
    "check_invariants",
    # Versions
    "SCHEMA_VERSION",
    "PROTOCOL_VERSION",
    "VersionCompatibility",
    "VersionInfo",
    "check_version_compatibility",
    "get_schema_version",
    "get_protocol_version",
]
