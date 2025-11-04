"""
L4 Protocol Envelopes - Typed Membrane Contracts

These are protocol-level artifacts shared across all layers.
Both L2 (org compute) and L3 (ecosystem surface) reference these schemas.

Envelope Types:
- docs_view: Docs-as-views request/result/invalidation
- economy: CPS-1 quote request/response/debit
- failure: Fail-loud error reporting (R-400/R-401)

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

from .docs_view import (
    DocsViewRequest,
    DocsViewResult,
    DocsViewInvalidated,
    PRICING_MIND,
    get_price
)

from .economy import (
    EconomyQuoteRequest,
    EconomyQuoteResponse,
    EconomyDebit
)

from .failure import FailureEmit

__all__ = [
    # Docs View
    "DocsViewRequest",
    "DocsViewResult",
    "DocsViewInvalidated",
    "PRICING_MIND",
    "get_price",

    # Economy
    "EconomyQuoteRequest",
    "EconomyQuoteResponse",
    "EconomyDebit",

    # Failure
    "FailureEmit",
]
