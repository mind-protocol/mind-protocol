"""Position schema and graph-node construction for L4 work module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from l4.schema import ThingNode, NarrativeNode, LinkBase

POSITION_ALLOWED_STATUSES = {"open", "matching", "offered", "filled", "closed", "dormant"}


@dataclass(frozen=True)
class PositionRegistration:
    """Input payload for creating a position."""

    org_id: str
    title: str
    requirements: str
    expectations: str
    fill_count: int = 1
    status: str = "open"


@dataclass(frozen=True)
class PositionRecord:
    """Read model for position state."""

    id: str
    org_id: str
    title: str
    requirements: str
    expectations: str
    fill_count: int
    status: str
    created_at: str


def generate_position_id() -> str:
    return f"position_{uuid.uuid4().hex[:12]}"


def validate_position_registration(registration: PositionRegistration) -> None:
    if not registration.org_id.strip():
        raise ValueError("org_id is required")
    if not registration.title.strip():
        raise ValueError("title is required")
    if not registration.requirements.strip():
        raise ValueError("requirements is required")
    if not registration.expectations.strip():
        raise ValueError("expectations is required")
    if registration.fill_count < 1:
        raise ValueError("fill_count must be >= 1")
    if registration.status not in POSITION_ALLOWED_STATUSES:
        raise ValueError(f"invalid status: {registration.status}")


def create_position_nodes(
    registration: PositionRegistration,
    position_id: Optional[str] = None,
) -> tuple[ThingNode, list[NarrativeNode], list[LinkBase], PositionRecord]:
    """Create L4 graph nodes for a position and return a record projection."""
    validate_position_registration(registration)

    pid = position_id or generate_position_id()
    created_at = datetime.utcnow().isoformat() + "Z"

    position_node = ThingNode(
        id=pid,
        name=registration.title,
        type="position",
        synthesis=f"Open role in {registration.org_id}: {registration.title}",
        content=f"requirements={registration.requirements}\nexpectations={registration.expectations}",
        uri=f"mind:position:{pid}",
    )

    property_nodes = [
        NarrativeNode(
            id=f"{pid}_requirements",
            name="requirements",
            type="requirements",
            synthesis=f"Requirements for position {pid}",
            content=registration.requirements,
        ),
        NarrativeNode(
            id=f"{pid}_expectations",
            name="expectations",
            type="expectations",
            synthesis=f"Expectations for position {pid}",
            content=registration.expectations,
        ),
        NarrativeNode(
            id=f"{pid}_status",
            name=registration.status,
            type="status",
            synthesis=f"Status for position {pid}: {registration.status}",
            content=registration.status,
        ),
        NarrativeNode(
            id=f"{pid}_fill_count",
            name=str(registration.fill_count),
            type="fill_count",
            synthesis=f"Fill count for position {pid}: {registration.fill_count}",
            content=str(registration.fill_count),
        ),
    ]

    links = [
        LinkBase(
            id=f"{pid}_property_{node.type}",
            node_a=pid,
            node_b=node.id,
            hierarchy=1.0,
            permanence=0.9 if node.type == "status" else 1.0,
        )
        for node in property_nodes
    ]

    record = PositionRecord(
        id=pid,
        org_id=registration.org_id,
        title=registration.title,
        requirements=registration.requirements,
        expectations=registration.expectations,
        fill_count=registration.fill_count,
        status=registration.status,
        created_at=created_at,
    )

    return position_node, property_nodes, links, record
