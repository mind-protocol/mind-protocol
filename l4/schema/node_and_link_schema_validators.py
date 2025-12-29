"""
Schema validation for Mind Protocol.

DOCS: docs/l4/schema/IMPLEMENTATION_Schema.md
"""

from typing import List, Optional, Union
from dataclasses import dataclass
from pydantic import ValidationError

from .node_type_enum_and_base_pydantic_models import NodeBase, NodeType, MomentBase
from .link_base_schema_with_semantic_axes import LinkBase


@dataclass
class ValidationResult:
    """Result of a validation check."""

    is_valid: bool
    errors: List[str]

    @classmethod
    def success(cls) -> "ValidationResult":
        return cls(is_valid=True, errors=[])

    @classmethod
    def failure(cls, errors: List[str]) -> "ValidationResult":
        return cls(is_valid=False, errors=errors)


def validate_node(data: dict) -> ValidationResult:
    """
    Validate node data against schema.

    Returns ValidationResult with errors if invalid.
    """
    errors = []

    # Check node_type
    node_type = data.get("node_type")
    if node_type is None:
        errors.append("Missing required field: node_type")
        return ValidationResult.failure(errors)

    # Validate against appropriate model
    try:
        if node_type == NodeType.MOMENT or node_type == "moment":
            MomentBase(**data)
        else:
            NodeBase(**data)
    except ValidationError as e:
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            errors.append(f"{loc}: {error['msg']}")

    if errors:
        return ValidationResult.failure(errors)
    return ValidationResult.success()


def validate_link(data: dict) -> ValidationResult:
    """
    Validate link data against schema.

    Returns ValidationResult with errors if invalid.
    """
    errors = []

    try:
        LinkBase(**data)
    except ValidationError as e:
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            errors.append(f"{loc}: {error['msg']}")

    if errors:
        return ValidationResult.failure(errors)
    return ValidationResult.success()


def validate_graph(nodes: List[dict], links: List[dict]) -> List[ValidationResult]:
    """
    Validate entire graph.

    Returns list of ValidationResults for each node and link.
    """
    results = []

    # Collect node IDs for reference validation
    node_ids = set()
    for node in nodes:
        result = validate_node(node)
        results.append(result)
        if result.is_valid:
            node_ids.add(node.get("id"))

    # Validate links
    for link in links:
        result = validate_link(link)

        # Check reference integrity
        if result.is_valid:
            node_a = link.get("node_a")
            node_b = link.get("node_b")
            ref_errors = []

            if node_a not in node_ids:
                ref_errors.append(f"Invalid reference: node_a '{node_a}' not found")
            if node_b not in node_ids:
                ref_errors.append(f"Invalid reference: node_b '{node_b}' not found")

            if ref_errors:
                result = ValidationResult.failure(ref_errors)

        results.append(result)

    return results


def check_invariants(nodes: List[dict], links: List[dict]) -> List[str]:
    """
    Check schema invariants.

    Returns list of violated invariants.
    """
    violations = []

    # Invariant: Only moments can branch (have multiple outgoing links to same type)
    # This is enforced by graph operations, not schema

    # Invariant: All floats in specified ranges
    for node in nodes:
        if node.get("weight", 0) < 0:
            violations.append(f"Node {node.get('id')}: weight < 0")
        if node.get("energy", 0) < 0:
            violations.append(f"Node {node.get('id')}: energy < 0")

    for link in links:
        if link.get("weight", 0) < 0:
            violations.append(f"Link {link.get('id')}: weight < 0")
        if link.get("energy", 0) < 0:
            violations.append(f"Link {link.get('id')}: energy < 0")

        hierarchy = link.get("hierarchy", 0)
        if not (-1 <= hierarchy <= 1):
            violations.append(f"Link {link.get('id')}: hierarchy out of range")

        permanence = link.get("permanence", 0.5)
        if not (0 <= permanence <= 1):
            violations.append(f"Link {link.get('id')}: permanence out of range")

    return violations
