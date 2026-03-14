"""
Stimulus compliance checking against L4 ecosystem laws.

DOCS: docs/l4/laws/ALGORITHM_Laws.md

Checks each stimulus against the laws that can be verified at runtime:
- L1: Schema compliance (all nodes/links pass validation)
- L2: Registered sender (sender_id exists in registry)
- L5: Hash-based identity (no raw JWT, valid hash)
- L7: Membrane fees (cross-org transactions pay >= 1%)

L3 (no direct DB access), L4 (membrane routing), L6 (receiver validates),
and L8 (WebSocket only) are enforced by architecture, not runtime code.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Tuple

from l4.schema import validate_node, validate_link
from .constants import MIN_FEE_RATE

# Matches a JWT embedded anywhere in text: three base64url segments
# separated by dots, where the first two start with eyJ (base64 for '{"').
_JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


@dataclass
class Stimulus:
    """
    A cross-org message subject to law compliance.

    Represents the payload that flows through the membrane between orgs.
    """

    sender_id: str
    identity_hash: str
    nodes: List[dict] = field(default_factory=list)
    links: List[dict] = field(default_factory=list)
    source_org: str = ""
    target_org: str = ""
    fee: float = 0.0
    value: float = 0.0


@dataclass
class ComplianceResult:
    """Result of checking a stimulus against ecosystem laws."""

    compliant: bool
    violations: List[str] = field(default_factory=list)


def check_stimulus_compliance(
    stimulus: Stimulus,
    sender_exists: Callable[[str], bool],
    verify_identity: Callable[[str, str], bool],
) -> ComplianceResult:
    """
    Check whether a stimulus complies with all enforceable laws.

    Args:
        stimulus: The cross-org stimulus to validate.
        sender_exists: Callable that returns True if sender_id is registered.
                       The membrane provides this by querying the L4 graph.
        verify_identity: Callable(identity_hash, sender_id) that returns True
                         if the hash matches the registered identity.
                         The membrane provides this via registry hash verification.

    Returns:
        ComplianceResult with list of violations (empty if compliant).
    """
    violations: List[str] = []

    # --- L1: Schema compliance ---
    for node in stimulus.nodes:
        result = validate_node(node)
        if not result.is_valid:
            for error in result.errors:
                violations.append(f"L1: Schema violation in node — {error}")

    for link in stimulus.links:
        result = validate_link(link)
        if not result.is_valid:
            for error in result.errors:
                violations.append(f"L1: Schema violation in link — {error}")

    # --- L2: Registered sender ---
    if not sender_exists(stimulus.sender_id):
        violations.append(f"L2: Sender '{stimulus.sender_id}' not registered")

    # --- L5: Hash-based identity ---
    # V5: No raw JWT in any serialized payload field
    _check_raw_jwt_exposure(stimulus, violations)

    # V6: Hash must match registered identity
    if not verify_identity(stimulus.identity_hash, stimulus.sender_id):
        violations.append("L5: Identity hash does not match registered identity")

    # --- L7: Membrane fees (only for cross-org) ---
    if stimulus.source_org != stimulus.target_org:
        min_fee = stimulus.value * MIN_FEE_RATE
        if stimulus.fee < min_fee:
            violations.append(
                f"L7: Fee {stimulus.fee} below minimum {min_fee} "
                f"({MIN_FEE_RATE:.0%} of {stimulus.value})"
            )

    return ComplianceResult(
        compliant=len(violations) == 0,
        violations=violations,
    )


def _check_raw_jwt_exposure(stimulus: Stimulus, violations: List[str]) -> None:
    """
    Detect raw JWT tokens in stimulus payload.

    JWTs have a recognizable 3-part base64 structure (header.payload.signature).
    We scan serialized node/link content for the pattern.
    """
    for node in stimulus.nodes:
        content = node.get("content", "")
        synthesis = node.get("synthesis", "")
        for field_value in (content, synthesis):
            if _looks_like_jwt(str(field_value)):
                violations.append(
                    f"L5: Raw JWT detected in node '{node.get('id', '?')}'"
                )
                return  # One violation is enough

    for link in stimulus.links:
        synthesis = link.get("synthesis", "")
        if _looks_like_jwt(str(synthesis)):
            violations.append("L5: Raw JWT detected in link payload")
            return


def _looks_like_jwt(text: str) -> bool:
    """
    Heuristic: detect a JWT anywhere in text.

    A JWT is three base64url segments separated by dots where the first two
    start with eyJ (base64url encoding of '{"'). We use a regex to find this
    pattern embedded within arbitrary surrounding text.
    """
    return _JWT_PATTERN.search(text) is not None
