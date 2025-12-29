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
)

__all__ = [
    # Citizen
    "CitizenRegistration",
    "CitizenRecord",
    "generate_citizen_id",
    "hash_jwt",
    "create_citizen_nodes",
    "citizen_to_record",
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
]
