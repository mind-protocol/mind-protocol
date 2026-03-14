"""
L4 Registry module for Mind Protocol.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

The registry is the source of truth for identity in the protocol.
Membrane (mind-ops) calls these APIs for registration and verification.

Exports:
- Citizen registration (models and CRUD)
- Org registration (models and CRUD)
- Endpoint management
- Hash verification (API for membrane)
"""

# Citizen registration
from .citizen_registration_crud_operations import (
    CitizenRegistration,
    CitizenRecord,
    generate_citizen_id,
    hash_jwt,
    create_citizen_nodes,
    citizen_to_record,
    # Citizen endpoints
    add_citizen_endpoint,
    remove_citizen_endpoint,
    get_citizen_endpoints,
)

# Org registration
from .org_registration_crud_operations import (
    OrgRegistration,
    OrgRecord,
    generate_org_id,
    create_org_nodes,
    org_to_record,
)

# Endpoint management
from .endpoint_registration_and_management import (
    EndpointValidationResult,
    validate_endpoint_url,
    create_endpoint_node,
    update_endpoint_url,
    # Citizen endpoint node creation
    create_citizen_endpoint_node,
)

# Hash verification (used by membrane via graph queries)
from .jwt_hash_verification_for_identity import (
    VerificationStatus,
    VerificationResult,
    compute_hash,
    verify_hash,
    create_verification_hash,
    # JWT signature verification
    JWTVerificationStatus,
    JWTVerificationResult,
    decode_jwt_parts,
    verify_jwt_claims,
    verify_jwt_signature,
    # Combined routing verification
    RoutingVerificationResult,
    verify_and_get_endpoint,
    # Citizen endpoint resolution
    CitizenEndpointEntry,
    CitizenEndpointResolution,
    resolve_citizen_endpoints,
)

__all__ = [
    # Citizen
    "CitizenRegistration",
    "CitizenRecord",
    "generate_citizen_id",
    "hash_jwt",
    "create_citizen_nodes",
    "citizen_to_record",
    # Citizen endpoints
    "add_citizen_endpoint",
    "remove_citizen_endpoint",
    "get_citizen_endpoints",
    # Org
    "OrgRegistration",
    "OrgRecord",
    "generate_org_id",
    "create_org_nodes",
    "org_to_record",
    # Endpoint
    "EndpointValidationResult",
    "validate_endpoint_url",
    "create_endpoint_node",
    "update_endpoint_url",
    "create_citizen_endpoint_node",
    # Hash verification
    "VerificationStatus",
    "VerificationResult",
    "compute_hash",
    "verify_hash",
    "create_verification_hash",
    # JWT signature verification
    "JWTVerificationStatus",
    "JWTVerificationResult",
    "decode_jwt_parts",
    "verify_jwt_claims",
    "verify_jwt_signature",
    # Combined routing verification
    "RoutingVerificationResult",
    "verify_and_get_endpoint",
    # Citizen endpoint resolution
    "CitizenEndpointEntry",
    "CitizenEndpointResolution",
    "resolve_citizen_endpoints",
]
