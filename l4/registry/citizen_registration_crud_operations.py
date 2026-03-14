"""
Citizen registration CRUD operations for Mind Protocol.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

Citizens are AI agents with identity and org membership.
Stored as actor nodes with type="citizen", properties as linked nodes.

Citizens can have multiple service endpoints (one per repo/instance they work on).
Each endpoint is a Thing node linked from the Actor node with a SERVES link.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import uuid

from ..schema import ActorNode, NarrativeNode, ThingNode, LinkBase
from .endpoint_registration_and_management import validate_endpoint_url


@dataclass
class CitizenRegistration:
    """
    Input model for citizen registration.

    This is NOT a graph node - it's API input validation.
    The graph stores ActorNode + linked property nodes.
    """

    name: str
    org_id: str
    jwt: str  # The JWT token (will be hashed, never stored raw)
    wallet: Optional[str] = None  # Solana address
    capabilities: List[str] = field(default_factory=list)


@dataclass
class CitizenRecord:
    """
    Output model for citizen queries.

    Aggregates citizen actor node with its linked properties.
    """

    id: str
    name: str
    org_id: str
    status: str  # "active", "pending", "suspended"
    registered_at: str  # ISO timestamp
    wallet: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    verification_status: str = "unverified"  # computed from links


def generate_citizen_id() -> str:
    """Generate unique citizen ID."""
    return f"citizen_{uuid.uuid4().hex[:12]}"


def hash_jwt(jwt: str) -> str:
    """
    Hash JWT for storage.

    Never store raw JWTs - only their hashes.
    """
    return hashlib.sha256(jwt.encode()).hexdigest()


def create_citizen_nodes(
    registration: CitizenRegistration,
    citizen_id: Optional[str] = None,
) -> tuple:
    """
    Create graph nodes for a citizen.

    Returns:
        (citizen_node, property_nodes, links, identity_hash)

    The caller is responsible for persisting to graph.
    The identity_hash is returned for the caller to use in future verifications.
    """
    cid = citizen_id or generate_citizen_id()
    now_iso = datetime.utcnow().isoformat() + "Z"

    # Compute identity hash: SHA256(JWT + citizen_id)
    # This is used for stimulus verification
    identity_hash = hashlib.sha256(f"{registration.jwt}{cid}".encode()).hexdigest()

    # Hash JWT for storage (never store raw JWT)
    jwt_storage_hash = hash_jwt(registration.jwt)

    # Main citizen actor node
    citizen_node = ActorNode(
        id=cid,
        name=registration.name,
        type="citizen",
        synthesis=f"Citizen {registration.name} of org {registration.org_id}",
        content=f"Registered citizen. JWT storage hash: {jwt_storage_hash}",
    )

    property_nodes = []
    links = []

    # Name property (narrative)
    name_node = NarrativeNode(
        id=f"{cid}_name",
        name=registration.name,
        type="name",
        synthesis=f"Name of citizen {cid}",
        content=registration.name,
    )
    property_nodes.append(name_node)
    links.append(LinkBase(
        id=f"{cid}_has_name",
        node_a=cid,
        node_b=name_node.id,
        hierarchy=1.0,  # property belongs to citizen
        permanence=1.0,
    ))

    # Org membership (narrative)
    org_node = NarrativeNode(
        id=f"{cid}_org",
        name=f"Member of {registration.org_id}",
        type="org_membership",
        synthesis=f"Citizen {cid} belongs to org {registration.org_id}",
        content=registration.org_id,
    )
    property_nodes.append(org_node)
    links.append(LinkBase(
        id=f"{cid}_has_org",
        node_a=cid,
        node_b=org_node.id,
        hierarchy=1.0,
        permanence=1.0,
    ))

    # Status (narrative) - starts as pending
    status_node = NarrativeNode(
        id=f"{cid}_status",
        name="pending",
        type="status",
        synthesis=f"Status of citizen {cid}: pending",
        content="pending",
    )
    property_nodes.append(status_node)
    links.append(LinkBase(
        id=f"{cid}_has_status",
        node_a=cid,
        node_b=status_node.id,
        hierarchy=1.0,
        permanence=0.5,  # status can change
    ))

    # Registered date (narrative)
    date_node = NarrativeNode(
        id=f"{cid}_registered",
        name=now_iso,
        type="registered_date",
        synthesis=f"Citizen {cid} registered at {now_iso}",
        content=now_iso,
    )
    property_nodes.append(date_node)
    links.append(LinkBase(
        id=f"{cid}_has_registered",
        node_a=cid,
        node_b=date_node.id,
        hierarchy=1.0,
        permanence=1.0,  # immutable
    ))

    # Wallet (thing) - optional
    if registration.wallet:
        wallet_node = ThingNode(
            id=f"{cid}_wallet",
            name=f"Wallet {registration.wallet[:8]}...",
            type="wallet",
            synthesis=f"Solana wallet for citizen {cid}",
            content=registration.wallet,
            uri=f"solana:{registration.wallet}",
        )
        property_nodes.append(wallet_node)
        links.append(LinkBase(
            id=f"{cid}_has_wallet",
            node_a=cid,
            node_b=wallet_node.id,
            hierarchy=1.0,
            permanence=0.8,
        ))

    # Capabilities (narrative) - if any
    if registration.capabilities:
        caps_content = ",".join(registration.capabilities)
        caps_node = NarrativeNode(
            id=f"{cid}_capabilities",
            name="Capabilities",
            type="capabilities",
            synthesis=f"Citizen {cid} can: {caps_content}",
            content=caps_content,
        )
        property_nodes.append(caps_node)
        links.append(LinkBase(
            id=f"{cid}_has_capabilities",
            node_a=cid,
            node_b=caps_node.id,
            hierarchy=1.0,
            permanence=0.5,
        ))

    # Identity hash (thing) - for verification during stimulus routing
    hash_node = ThingNode(
        id=f"{cid}_identity_hash",
        name="Identity Hash",
        type="identity_hash",
        synthesis=f"Identity verification hash for citizen {cid}",
        content=identity_hash,
    )
    property_nodes.append(hash_node)
    links.append(LinkBase(
        id=f"{cid}_has_hash",
        node_a=cid,
        node_b=hash_node.id,
        hierarchy=1.0,
        permanence=1.0,  # Immutable - tied to JWT
    ))

    return citizen_node, property_nodes, links, identity_hash


def citizen_to_record(
    citizen_node: ActorNode,
    property_nodes: List,
    links: List[LinkBase],
) -> CitizenRecord:
    """
    Convert graph nodes back to CitizenRecord.

    Used for API responses.
    """
    # Extract properties from linked nodes
    name = citizen_node.name
    org_id = ""
    status = "pending"
    registered_at = ""
    wallet = None
    capabilities = []

    for node in property_nodes:
        if hasattr(node, 'type'):
            if node.type == "org_membership":
                org_id = node.content
            elif node.type == "status":
                status = node.content
            elif node.type == "registered_date":
                registered_at = node.content
            elif node.type == "wallet":
                wallet = node.content
            elif node.type == "capabilities":
                capabilities = node.content.split(",") if node.content else []

    # Compute verification status from links
    verification_status = "unverified"
    for link in links:
        # Look for verification links (from verifier to citizen)
        if link.node_b == citizen_node.id:
            polarity = link.polarity[0] if isinstance(link.polarity, tuple) else 0
            if polarity == 1.0:
                if link.permanence >= 0.5:
                    verification_status = "verified"
                else:
                    verification_status = "provisional"
            elif polarity == -1.0:
                verification_status = "rejected"
            else:
                verification_status = "pending"

    return CitizenRecord(
        id=citizen_node.id,
        name=name,
        org_id=org_id,
        status=status,
        registered_at=registered_at,
        wallet=wallet,
        capabilities=capabilities,
        verification_status=verification_status,
    )


# --- Citizen Endpoint Management ---


def add_citizen_endpoint(
    citizen_id: str,
    endpoint_url: str,
    repo_name: str,
    instance_id: Optional[str] = None,
) -> tuple:
    """
    Register a service endpoint for a citizen.

    A citizen can have multiple endpoints (one per repo they work on).
    Each endpoint is a Thing node linked from the Actor node.
    Uses deterministic IDs for MERGE semantics — re-registering the same
    citizen+repo combination updates the existing node, never duplicates.

    Args:
        citizen_id: The citizen's actor ID
        endpoint_url: WebSocket URL (wss://) for this instance
        repo_name: Which repo this endpoint serves (e.g., "cities-of-light")
        instance_id: Optional Render instance ID for dedup

    Returns:
        (endpoint_node, link) tuple

    Raises:
        ValueError: If endpoint_url is not a valid wss:// URL
    """
    # Validate endpoint URL
    validation = validate_endpoint_url(endpoint_url)
    if not validation.is_valid:
        raise ValueError(validation.error)

    now_iso = datetime.utcnow().isoformat() + "Z"

    # Deterministic ID: citizen + repo → always the same node
    endpoint_id = f"{citizen_id}_endpoint_{repo_name}"

    endpoint_node = ThingNode(
        id=endpoint_id,
        name=f"Endpoint {citizen_id}/{repo_name}",
        type="citizen_endpoint",
        synthesis=f"Service endpoint for {citizen_id} on {repo_name}",
        content=endpoint_url,
        uri=endpoint_url,
    )

    # Link: Actor → Thing with SERVES semantics
    # hierarchy=1.0: endpoint belongs to citizen
    # permanence=0.6: endpoints can change (deploys, shutdowns)
    link = LinkBase(
        id=f"{citizen_id}_serves_{repo_name}",
        node_a=citizen_id,
        node_b=endpoint_id,
        hierarchy=1.0,
        permanence=0.6,
    )

    return endpoint_node, link


def remove_citizen_endpoint(citizen_id: str, repo_name: str) -> tuple:
    """
    Remove a citizen endpoint (e.g., when instance shuts down).

    Returns the IDs to delete so the caller can remove from graph.
    Does not touch the graph directly — caller is responsible for persistence.

    Args:
        citizen_id: The citizen's actor ID
        repo_name: Which repo endpoint to remove

    Returns:
        (endpoint_node_id, link_id) tuple for the caller to delete
    """
    endpoint_id = f"{citizen_id}_endpoint_{repo_name}"
    link_id = f"{citizen_id}_serves_{repo_name}"
    return endpoint_id, link_id


def get_citizen_endpoints(
    citizen_id: str,
    property_nodes: List,
) -> List[Dict[str, Any]]:
    """
    Get all active endpoints for a citizen from their property nodes.

    Filters property nodes for citizen_endpoint type and extracts
    endpoint metadata.

    Args:
        citizen_id: The citizen's actor ID
        property_nodes: All linked property nodes for this citizen

    Returns:
        List of dicts with keys:
            endpoint_url, repo_name, instance_id, registered_at, status
    """
    endpoints = []
    for node in property_nodes:
        if hasattr(node, "type") and node.type == "citizen_endpoint":
            # Extract repo_name from deterministic ID pattern:
            # {citizen_id}_endpoint_{repo_name}
            prefix = f"{citizen_id}_endpoint_"
            repo_name = node.id[len(prefix):] if node.id.startswith(prefix) else node.id

            endpoints.append({
                "endpoint_url": node.content,
                "repo_name": repo_name,
                "status": "active",
            })

    return endpoints
