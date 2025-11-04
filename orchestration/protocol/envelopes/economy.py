"""
L4 Protocol Envelopes - Economy (CPS-1)

Protocol-level envelope schemas for economy/quota events.
These enforce the CPS-1 quote-before-inject discipline.

Topics:
- ecosystem/{eco}/org/{org}/economy.quote.request
- ecosystem/{eco}/org/{org}/economy.quote.response
- ecosystem/{eco}/org/{org}/economy.debit

Author: Mel "Bridgekeeper"
Date: 2025-11-04 (Promoted to L4 protocol artifacts)
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class EconomyQuoteRequest(BaseModel):
    """
    Request compute quote before injecting work request.

    Client/L3 sends this to economy service.
    """
    work: str  # "docs.view", "validation.assessment", etc.
    format: str  # "json", "mdx", "html"
    estimate: Dict[str, Any] = Field(default_factory=dict)  # {rows: 800, render_pages: 1}
    request_id: str
    org: str  # Org requesting the work


class EconomyQuoteResponse(BaseModel):
    """
    Economy service response with quote_id and pricing.

    Economy service broadcasts this with quote details.
    """
    request_id: str
    quote_id: str
    price: Dict[str, Any]  # {currency: "$MIND", amount: 0.05}
    expires_at: str  # ISO datetime
    budget_ok: bool  # False if org has insufficient budget
    org: str


class EconomyDebit(BaseModel):
    """
    Debit quote after work completed.

    L2 resolver sends this after successfully computing work.
    """
    quote_id: str
    actual_cost: float  # Actual $MIND consumed (may differ from estimate)
    work_completed: str  # "docs.view", etc.
    org: str
