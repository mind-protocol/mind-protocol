"""
Endpoint registration and management for Mind Protocol.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

Endpoints are WebSocket URLs for org communication.
Stored as thing nodes with type="endpoint".
"""

from typing import Optional
from dataclasses import dataclass
import re

from ..schema import ThingNode


# WebSocket URL pattern
WS_URL_PATTERN = re.compile(r'^wss?://[^\s/$.?#].[^\s]*$')


@dataclass
class EndpointValidationResult:
    """Result of endpoint URL validation."""

    is_valid: bool
    error: Optional[str] = None

    @classmethod
    def success(cls) -> "EndpointValidationResult":
        return cls(is_valid=True)

    @classmethod
    def failure(cls, error: str) -> "EndpointValidationResult":
        return cls(is_valid=False, error=error)


def validate_endpoint_url(url: str) -> EndpointValidationResult:
    """
    Validate endpoint URL.

    Requirements:
    - Must be wss:// (secure WebSocket)
    - Must be valid URL format
    """
    if not url:
        return EndpointValidationResult.failure("Endpoint URL is required")

    if not url.startswith("wss://"):
        return EndpointValidationResult.failure(
            "Endpoint must use secure WebSocket (wss://)"
        )

    if not WS_URL_PATTERN.match(url):
        return EndpointValidationResult.failure(
            "Invalid WebSocket URL format"
        )

    return EndpointValidationResult.success()


def create_endpoint_node(
    org_id: str,
    url: str,
    endpoint_id: Optional[str] = None,
) -> ThingNode:
    """
    Create endpoint thing node.

    Validates URL before creating.
    Raises ValueError if URL is invalid.
    """
    validation = validate_endpoint_url(url)
    if not validation.is_valid:
        raise ValueError(validation.error)

    eid = endpoint_id or f"{org_id}_endpoint"

    return ThingNode(
        id=eid,
        name=f"Endpoint {org_id}",
        type="endpoint",
        synthesis=f"WebSocket endpoint for org {org_id}",
        content=url,
        uri=url,
    )


def update_endpoint_url(
    endpoint_node: ThingNode,
    new_url: str,
) -> ThingNode:
    """
    Update endpoint URL.

    Returns new node with updated URL.
    Validates URL before updating.
    """
    validation = validate_endpoint_url(new_url)
    if not validation.is_valid:
        raise ValueError(validation.error)

    # Create new node with updated values
    return ThingNode(
        id=endpoint_node.id,
        name=endpoint_node.name,
        type="endpoint",
        synthesis=endpoint_node.synthesis,
        content=new_url,
        uri=new_url,
    )
