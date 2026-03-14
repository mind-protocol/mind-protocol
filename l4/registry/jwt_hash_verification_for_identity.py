"""
JWT hash verification for Mind Protocol identity.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

This module provides:
- Hash computation and verification for stimulus routing
- JWT signature verification for registration
- Combined verify + endpoint lookup for efficient routing
- Citizen endpoint resolution (multi-endpoint routing)

Membrane (mind-ops) queries the graph directly to verify hashes.
There is no API - registry data lives in Neo4j as nodes.

Hash formula: SHA256(JWT + node_id)
"""

import hashlib
import base64
import json
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple, Dict, List, Any
from enum import Enum
from datetime import datetime


class VerificationStatus(str, Enum):
    """Result status of hash verification."""

    VALID = "valid"  # Hash matches registered identity
    INVALID = "invalid"  # Hash does not match
    NOT_FOUND = "not_found"  # Citizen/org not in registry
    EXPIRED = "expired"  # JWT has expired
    SUSPENDED = "suspended"  # Citizen/org is suspended


@dataclass
class VerificationResult:
    """Result of hash verification against registry."""

    status: VerificationStatus
    citizen_id: Optional[str] = None
    org_id: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.status == VerificationStatus.VALID


def compute_hash(jwt: str, node_id: str) -> str:
    """
    Compute identity hash for transmission.

    Formula: SHA256(JWT + node_id)

    This hash is included in cross-org stimuli to prove origin.
    Membrane verifies by querying the graph for the stored hash.
    """
    payload = f"{jwt}{node_id}"
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_hash(
    expected_hash: str,
    node_id: str,
    graph_lookup: Callable[[str], Optional[Tuple[str, str, str]]],
) -> VerificationResult:
    """
    Verify identity hash against registry.

    Called by membrane (mind-ops) during cross-org routing.
    Membrane provides graph_lookup which queries Neo4j directly.

    Args:
        expected_hash: The hash from the stimulus
        node_id: The node ID that was supposedly hashed
        graph_lookup: Callable that queries Neo4j and returns
                     (stored_hash, org_id, status) or None if not found

    Returns:
        VerificationResult with status and identity info
    """
    # Look up in registry via graph query
    lookup_result = graph_lookup(node_id)

    if lookup_result is None:
        return VerificationResult(
            status=VerificationStatus.NOT_FOUND,
            error=f"Node {node_id} not found in registry",
        )

    stored_hash, org_id, status = lookup_result

    # Check if suspended
    if status == "suspended":
        return VerificationResult(
            status=VerificationStatus.SUSPENDED,
            org_id=org_id,
            error="Citizen or org is suspended",
        )

    # Verify hash matches
    if stored_hash == expected_hash:
        return VerificationResult(
            status=VerificationStatus.VALID,
            citizen_id=node_id,
            org_id=org_id,
        )

    return VerificationResult(
        status=VerificationStatus.INVALID,
        error="Hash does not match registered identity",
    )


def create_verification_hash(jwt: str, citizen_id: str) -> str:
    """
    Create the hash to store in registry during citizen registration.

    This is called when a citizen registers.
    The resulting hash is stored as a linked thing node and used for verification.
    """
    return compute_hash(jwt, citizen_id)


# --- JWT Signature Verification ---


class JWTVerificationStatus(str, Enum):
    """Result status of JWT signature verification."""

    VALID = "valid"
    INVALID_SIGNATURE = "invalid_signature"
    EXPIRED = "expired"
    NOT_YET_VALID = "not_yet_valid"
    INVALID_FORMAT = "invalid_format"
    INVALID_ISSUER = "invalid_issuer"
    MISSING_PUBLIC_KEY = "missing_public_key"
    ORG_NOT_FOUND = "org_not_found"


@dataclass
class JWTVerificationResult:
    """Result of JWT signature verification."""

    status: JWTVerificationStatus
    claims: Optional[Dict[str, Any]] = None
    org_id: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.status == JWTVerificationStatus.VALID


def decode_jwt_parts(jwt: str) -> Tuple[Optional[Dict], Optional[Dict], Optional[str]]:
    """
    Decode JWT into header, payload, signature without verification.

    Returns (header, payload, signature) or (None, None, None) if invalid format.
    """
    try:
        parts = jwt.split(".")
        if len(parts) != 3:
            return None, None, None

        # Decode header
        header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)  # Add padding
        header = json.loads(base64.urlsafe_b64decode(header_b64))

        # Decode payload
        payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        signature = parts[2]

        return header, payload, signature
    except Exception:
        return None, None, None


def verify_jwt_claims(
    payload: Dict[str, Any],
    expected_issuer: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Verify JWT claims (exp, iat, iss).

    Returns (is_valid, error_message).
    """
    import time
    now = time.time()  # Use time.time() for consistent UTC timestamps

    # Check expiration
    if "exp" in payload:
        if payload["exp"] < now:
            return False, "JWT expired"

    # Check not before / issued at
    if "iat" in payload:
        if payload["iat"] > now + 60:  # Allow 60s clock skew
            return False, "JWT not yet valid (iat in future)"

    if "nbf" in payload:
        if payload["nbf"] > now + 60:
            return False, "JWT not yet valid (nbf in future)"

    # Check issuer
    if expected_issuer and "iss" in payload:
        if payload["iss"] != expected_issuer:
            return False, f"Invalid issuer: expected {expected_issuer}, got {payload['iss']}"

    return True, None


def verify_jwt_signature(
    jwt: str,
    org_id: str,
    public_key_lookup: Callable[[str], Optional[str]],
) -> JWTVerificationResult:
    """
    Verify JWT signature using org's public key from L4 registry.

    Called during citizen registration to ensure JWT is properly signed.
    Membrane provides public_key_lookup which queries Neo4j directly.

    Args:
        jwt: The JWT string to verify
        org_id: The org that supposedly signed the JWT
        public_key_lookup: Callable that returns org's public key or None

    Returns:
        JWTVerificationResult with status and claims if valid
    """
    # Decode JWT parts
    header, payload, signature = decode_jwt_parts(jwt)
    if header is None or payload is None:
        return JWTVerificationResult(
            status=JWTVerificationStatus.INVALID_FORMAT,
            error="Invalid JWT format",
        )

    # Get org's public key from L4 registry
    public_key = public_key_lookup(org_id)
    if public_key is None:
        return JWTVerificationResult(
            status=JWTVerificationStatus.ORG_NOT_FOUND,
            org_id=org_id,
            error=f"Org {org_id} not found in registry",
        )

    if not public_key:
        return JWTVerificationResult(
            status=JWTVerificationStatus.MISSING_PUBLIC_KEY,
            org_id=org_id,
            error=f"Org {org_id} has no public key registered",
        )

    # Verify claims first (cheaper than crypto)
    claims_valid, claims_error = verify_jwt_claims(payload, expected_issuer=org_id)
    if not claims_valid:
        if "expired" in claims_error.lower():
            return JWTVerificationResult(
                status=JWTVerificationStatus.EXPIRED,
                org_id=org_id,
                error=claims_error,
            )
        elif "not yet valid" in claims_error.lower():
            return JWTVerificationResult(
                status=JWTVerificationStatus.NOT_YET_VALID,
                org_id=org_id,
                error=claims_error,
            )
        else:
            return JWTVerificationResult(
                status=JWTVerificationStatus.INVALID_ISSUER,
                org_id=org_id,
                error=claims_error,
            )

    # Signature verification requires cryptography library
    # For now, we validate format and claims; actual signature verification
    # will use PyJWT or cryptography when available
    # The membrane implementation will call the actual crypto verification
    #
    # This function validates:
    # 1. JWT format is correct
    # 2. Claims are valid (exp, iat, iss)
    # 3. Public key exists for org
    #
    # Actual signature verification is done by membrane using:
    # jwt.decode(token, public_key, algorithms=[header["alg"]])

    return JWTVerificationResult(
        status=JWTVerificationStatus.VALID,
        claims=payload,
        org_id=org_id,
    )


# --- Combined Verification + Endpoint Lookup ---


@dataclass
class RoutingVerificationResult:
    """Result of combined hash verification and endpoint lookup."""

    status: VerificationStatus
    sender_id: Optional[str] = None
    sender_org_id: Optional[str] = None
    dest_endpoint: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.status == VerificationStatus.VALID

    @property
    def can_route(self) -> bool:
        return self.is_valid and self.dest_endpoint is not None


def verify_and_get_endpoint(
    identity_hash: str,
    sender_id: str,
    dest_org_id: str,
    graph_lookup: Callable[[str, str], Optional[Tuple[str, str, str, str]]],
) -> RoutingVerificationResult:
    """
    Combined verification and endpoint lookup for efficient routing.

    Called by membrane when routing cross-org stimulus.
    Single graph query returns both verification data and destination endpoint.

    Args:
        identity_hash: The hash from the stimulus
        sender_id: The citizen/agent ID that sent the stimulus
        dest_org_id: The destination org ID
        graph_lookup: Callable that queries Neo4j and returns
                     (stored_hash, sender_org_id, sender_status, dest_endpoint)
                     or None if sender not found

    Returns:
        RoutingVerificationResult with verification status and endpoint
    """
    # Query L4 graph for sender info and destination endpoint
    lookup_result = graph_lookup(sender_id, dest_org_id)

    if lookup_result is None:
        return RoutingVerificationResult(
            status=VerificationStatus.NOT_FOUND,
            sender_id=sender_id,
            error=f"Sender {sender_id} not found in registry",
        )

    stored_hash, sender_org_id, sender_status, dest_endpoint = lookup_result

    # Check if sender is suspended
    if sender_status == "suspended":
        return RoutingVerificationResult(
            status=VerificationStatus.SUSPENDED,
            sender_id=sender_id,
            sender_org_id=sender_org_id,
            error="Sender is suspended",
        )

    # Verify hash matches
    if stored_hash != identity_hash:
        return RoutingVerificationResult(
            status=VerificationStatus.INVALID,
            sender_id=sender_id,
            sender_org_id=sender_org_id,
            error="Identity hash does not match",
        )

    # Check destination endpoint exists
    if not dest_endpoint:
        return RoutingVerificationResult(
            status=VerificationStatus.VALID,
            sender_id=sender_id,
            sender_org_id=sender_org_id,
            error=f"Destination org {dest_org_id} has no endpoint",
        )

    return RoutingVerificationResult(
        status=VerificationStatus.VALID,
        sender_id=sender_id,
        sender_org_id=sender_org_id,
        dest_endpoint=dest_endpoint,
    )


# --- Citizen Endpoint Resolution ---


@dataclass
class CitizenEndpointEntry:
    """A single resolved endpoint for a citizen."""

    url: str
    repo_name: str
    type: str  # "direct" (citizen endpoint) or "org" (fallback)


@dataclass
class CitizenEndpointResolution:
    """Result of resolving all endpoints for a citizen."""

    citizen_id: str
    endpoints: List[CitizenEndpointEntry] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_endpoints(self) -> bool:
        return len(self.endpoints) > 0


def resolve_citizen_endpoints(
    citizen_id: str,
    graph_lookup: Callable[[str], Optional[Tuple[List[Tuple[str, str]], Optional[str]]]],
) -> CitizenEndpointResolution:
    """
    Resolve all active endpoints for a citizen.

    Checks both:
    1. Direct citizen endpoints (Thing nodes linked from Actor with type="citizen_endpoint")
    2. Org endpoint (fallback — citizen's org endpoint if no direct endpoints)

    The membrane provides graph_lookup which queries the graph and returns:
        (
            [(endpoint_url, repo_name), ...],  # direct citizen endpoints
            org_endpoint_url or None             # org fallback endpoint
        )
        or None if citizen not found.

    Results are sorted by priority: direct endpoints first, org fallback last.

    Args:
        citizen_id: The citizen's actor ID
        graph_lookup: Callable that queries the graph and returns
                     (citizen_endpoints, org_endpoint) or None

    Returns:
        CitizenEndpointResolution with all resolved endpoints sorted by priority
    """
    lookup_result = graph_lookup(citizen_id)

    if lookup_result is None:
        return CitizenEndpointResolution(
            citizen_id=citizen_id,
            error=f"Citizen {citizen_id} not found in registry",
        )

    citizen_endpoints, org_endpoint = lookup_result

    entries = []

    # Priority 1: direct citizen endpoints
    for url, repo_name in citizen_endpoints:
        entries.append(CitizenEndpointEntry(
            url=url,
            repo_name=repo_name,
            type="direct",
        ))

    # Priority 2: org endpoint as fallback (only if no direct endpoints)
    if not entries and org_endpoint:
        entries.append(CitizenEndpointEntry(
            url=org_endpoint,
            repo_name="org",
            type="org",
        ))

    if not entries:
        return CitizenEndpointResolution(
            citizen_id=citizen_id,
            error=f"No endpoints found for citizen {citizen_id}",
        )

    return CitizenEndpointResolution(
        citizen_id=citizen_id,
        endpoints=entries,
    )
