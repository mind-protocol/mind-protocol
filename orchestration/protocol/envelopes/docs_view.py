"""
L4 Protocol Envelopes - Docs-as-Views

Protocol-level envelope schemas for docs view events.
These are the typed contracts between L2 and L3 across the membrane bus.

Topics:
- ecosystem/{eco}/org/{org}/docs.view.request
- ecosystem/{eco}/org/{org}/docs.view.result
- ecosystem/{eco}/org/{org}/docs.view.invalidated

Author: Mel "Bridgekeeper"
Date: 2025-11-04 (Promoted to L4 protocol artifacts)
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field


class DocsViewRequest(BaseModel):
    """
    Request a docs view (must include valid quote_id for CPS-1).

    L3 injects this, L2 resolvers observe and compute.
    """
    request_id: str
    quote_id: str  # CPS-1 requirement (validated at L4 gate)
    view_type: Literal["architecture", "api-reference", "coverage", "index"]
    format: Literal["json", "mdx", "html"]
    scope: Dict[str, str]  # {org: "scopelock", root: "repo://", path: "/"}
    params: Dict[str, Any] = Field(default_factory=dict)  # {depth: 2, cluster: true}


class DocsViewResult(BaseModel):
    """
    Resolver result (ok or error).

    L2 resolvers broadcast this after computing view.
    """
    request_id: str
    status: Literal["ok", "error"]
    format: str
    view_type: str
    view_model: Optional[Any] = None
    provenance: Optional[Dict[str, Any]] = None  # {ko_digest, selectors, evidence_nodes}
    cache: Optional[Dict[str, int]] = None  # {ttl_sec: 300}
    error: Optional[Dict[str, str]] = None  # {message, code} when status=error


class DocsViewInvalidated(BaseModel):
    """
    Targeted cache invalidation (emitted on graph changes).

    L2 emits this when graph changes affect cached views.
    L3 observes and invalidates local caches.
    """
    reasons: List[str]  # ["graph.delta.node.upsert", "lint.findings.emit"]
    affects: List[str]  # ["architecture:/", "api:/auth", "coverage:*"]


# ============================================================================
# Pricing Constants (Phase-0 CPS-1)
# ============================================================================

PRICING_MIND = {
    "json": 0.05,  # "tool request"
    "mdx": 5.0,    # "doc generation" per page
    "html": 5.0    # "doc generation" per page
}


def get_price(format: str, pages: int = 1) -> float:
    """Get price in $MIND for view generation"""
    base_price = PRICING_MIND.get(format, 0.05)
    if format in ("mdx", "html"):
        return base_price * pages
    return base_price
