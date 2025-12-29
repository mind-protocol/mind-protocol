"""
Org registration CRUD operations for Mind Protocol.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

Orgs are organizations that group citizens and own endpoints.
Stored as space nodes with type="org", properties as linked nodes.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..schema import SpaceNode, NarrativeNode, ThingNode, LinkBase


@dataclass
class OrgRegistration:
    """
    Input model for org registration.

    This is NOT a graph node - it's API input validation.
    The graph stores SpaceNode + linked property nodes.
    """

    name: str
    wallet: str  # Solana address - required for orgs
    endpoint_url: str  # WebSocket URL (wss://)
    jwt_public_key: str  # Public key for JWT verification


@dataclass
class OrgRecord:
    """
    Output model for org queries.

    Aggregates org space node with its linked properties.
    """

    id: str
    name: str
    wallet: str
    endpoint_url: str
    status: str  # "active", "pending", "suspended"
    registered_at: str  # ISO timestamp
    citizen_count: int = 0
    verification_status: str = "unverified"  # computed from links


def generate_org_id() -> str:
    """Generate unique org ID."""
    return f"org_{uuid.uuid4().hex[:12]}"


def create_org_nodes(
    registration: OrgRegistration,
    org_id: Optional[str] = None,
) -> tuple:
    """
    Create graph nodes for an org.

    Returns:
        (org_node, property_nodes, links)

    The caller is responsible for persisting to graph.
    """
    oid = org_id or generate_org_id()
    now_iso = datetime.utcnow().isoformat() + "Z"

    # Main org space node
    org_node = SpaceNode(
        id=oid,
        name=registration.name,
        type="org",
        synthesis=f"Organization {registration.name} at {registration.endpoint_url}",
        content=f"Registered org with wallet {registration.wallet}",
    )

    property_nodes = []
    links = []

    # Name property (narrative)
    name_node = NarrativeNode(
        id=f"{oid}_name",
        name=registration.name,
        type="name",
        synthesis=f"Name of org {oid}",
        content=registration.name,
    )
    property_nodes.append(name_node)
    links.append(LinkBase(
        id=f"{oid}_has_name",
        node_a=oid,
        node_b=name_node.id,
        hierarchy=1.0,
        permanence=1.0,
    ))

    # Status (narrative) - starts as pending
    status_node = NarrativeNode(
        id=f"{oid}_status",
        name="pending",
        type="status",
        synthesis=f"Status of org {oid}: pending",
        content="pending",
    )
    property_nodes.append(status_node)
    links.append(LinkBase(
        id=f"{oid}_has_status",
        node_a=oid,
        node_b=status_node.id,
        hierarchy=1.0,
        permanence=0.5,
    ))

    # Registered date (narrative)
    date_node = NarrativeNode(
        id=f"{oid}_registered",
        name=now_iso,
        type="registered_date",
        synthesis=f"Org {oid} registered at {now_iso}",
        content=now_iso,
    )
    property_nodes.append(date_node)
    links.append(LinkBase(
        id=f"{oid}_has_registered",
        node_a=oid,
        node_b=date_node.id,
        hierarchy=1.0,
        permanence=1.0,
    ))

    # Wallet (thing) - required for orgs
    wallet_node = ThingNode(
        id=f"{oid}_wallet",
        name=f"Wallet {registration.wallet[:8]}...",
        type="wallet",
        synthesis=f"Solana wallet for org {oid}",
        content=registration.wallet,
        uri=f"solana:{registration.wallet}",
    )
    property_nodes.append(wallet_node)
    links.append(LinkBase(
        id=f"{oid}_has_wallet",
        node_a=oid,
        node_b=wallet_node.id,
        hierarchy=1.0,
        permanence=0.9,
    ))

    # Endpoint (thing) - required for orgs
    endpoint_node = ThingNode(
        id=f"{oid}_endpoint",
        name=f"Endpoint {oid}",
        type="endpoint",
        synthesis=f"WebSocket endpoint for org {oid}",
        content=registration.endpoint_url,
        uri=registration.endpoint_url,
    )
    property_nodes.append(endpoint_node)
    links.append(LinkBase(
        id=f"{oid}_has_endpoint",
        node_a=oid,
        node_b=endpoint_node.id,
        hierarchy=1.0,
        permanence=0.8,
    ))

    # JWT public key (thing) - required, not public
    key_node = ThingNode(
        id=f"{oid}_jwt_key",
        name=f"JWT Key {oid}",
        type="jwt_public_key",
        synthesis=f"JWT verification key for org {oid}",
        content=registration.jwt_public_key,
    )
    property_nodes.append(key_node)
    links.append(LinkBase(
        id=f"{oid}_has_jwt_key",
        node_a=oid,
        node_b=key_node.id,
        hierarchy=1.0,
        permanence=0.7,
    ))

    return org_node, property_nodes, links


def org_to_record(
    org_node: SpaceNode,
    property_nodes: List,
    links: List[LinkBase],
    citizen_count: int = 0,
) -> OrgRecord:
    """
    Convert graph nodes back to OrgRecord.

    Used for API responses.
    """
    name = org_node.name
    wallet = ""
    endpoint_url = ""
    status = "pending"
    registered_at = ""

    for node in property_nodes:
        if hasattr(node, 'type'):
            if node.type == "wallet":
                wallet = node.content
            elif node.type == "endpoint":
                endpoint_url = node.content
            elif node.type == "status":
                status = node.content
            elif node.type == "registered_date":
                registered_at = node.content

    # Compute verification status from links
    verification_status = "unverified"
    for link in links:
        if link.node_b == org_node.id:
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

    return OrgRecord(
        id=org_node.id,
        name=name,
        wallet=wallet,
        endpoint_url=endpoint_url,
        status=status,
        registered_at=registered_at,
        citizen_count=citizen_count,
        verification_status=verification_status,
    )
