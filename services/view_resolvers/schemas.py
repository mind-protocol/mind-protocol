"""
L2 View Resolvers - Event Schemas

Event structures for membrane-native docs-as-views.

Topics (org-scoped):
- ecosystem/{eco}/org/{org}/economy.quote.request|response
- ecosystem/{eco}/org/{org}/docs.view.request
- ecosystem/{eco}/org/{org}/docs.view.result
- ecosystem/{eco}/org/{org}/docs.view.invalidated
- ecosystem/{eco}/org/{org}/failure.emit

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# CPS-1 Economy Events
# ============================================================================

class EconomyQuoteRequest(BaseModel):
    """Request compute quote before injecting view request"""
    work: str = "docs.view"
    format: Literal["json", "mdx", "html"]
    estimate: Dict[str, Any] = Field(default_factory=dict)  # {rows: 800, render_pages: 1}
    request_id: str


class EconomyQuoteResponse(BaseModel):
    """Economy service response with quote_id and pricing"""
    request_id: str
    quote_id: str
    price: Dict[str, Any]  # {currency: "$MIND", amount: 0.05}
    expires_at: str  # ISO datetime
    budget_ok: bool


# ============================================================================
# Docs View Events
# ============================================================================

class DocsViewRequest(BaseModel):
    """Request a docs view (must include valid quote_id)"""
    request_id: str
    quote_id: str
    view_type: Literal["architecture", "api-reference", "coverage", "index"]
    format: Literal["json", "mdx", "html"]
    scope: Dict[str, str]  # {org: "scopelock", root: "repo://", path: "/"}
    params: Dict[str, Any] = Field(default_factory=dict)  # {depth: 2, cluster: true}


class DocsViewResult(BaseModel):
    """Resolver result (ok or error)"""
    request_id: str
    status: Literal["ok", "error"]
    format: str
    view_type: str
    view_model: Optional[Any] = None
    provenance: Optional[Dict[str, Any]] = None  # {ko_digest, selectors, evidence_nodes}
    cache: Optional[Dict[str, int]] = None  # {ttl_sec: 300}
    error: Optional[Dict[str, str]] = None  # {message, code} when status=error


class DocsViewInvalidated(BaseModel):
    """Targeted cache invalidation (emitted on graph changes)"""
    reasons: List[str]  # ["graph.delta.node.upsert", "lint.findings.emit"]
    affects: List[str]  # ["architecture:/", "api:/auth", "coverage:*"]


# ============================================================================
# Fail-Loud Event (R-400/R-401 compliance)
# ============================================================================

class FailureEmit(BaseModel):
    """Fail-loud error reporting (never swallow exceptions)"""
    code_location: str  # "services/view_resolvers/runner.py:88"
    exception: str  # repr(e)
    severity: Literal["error", "warning", "critical"]
    suggestion: str  # Helpful hint for fixing
    trace_id: Optional[str] = None


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
