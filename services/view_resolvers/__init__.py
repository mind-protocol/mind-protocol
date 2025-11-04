"""
L2 View Resolvers - Membrane-Native Docs-as-Views

L2 compute boundary for docs views:
- Executes Cypher queries against org graph
- Validates CPS-1 quotes before compute
- Emits results via membrane bus
- Fail-loud error handling (R-400/R-401)

Usage:
    from services.view_resolvers import ViewResolver

    resolver = ViewResolver(bus, graph, economy, cache)
    resolver.on_docs_view_request(envelope)

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

from .runner import ViewResolver, ViewCache, EconomyStub
from .selectors import get_selector, SELECTORS
from .projectors import project, render, ko_digest
from .schemas import (
    DocsViewRequest,
    DocsViewResult,
    DocsViewInvalidated,
    FailureEmit,
    PRICING_MIND,
    get_price
)

__all__ = [
    # Main resolver
    "ViewResolver",
    "ViewCache",
    "EconomyStub",

    # Selectors
    "get_selector",
    "SELECTORS",

    # Projectors
    "project",
    "render",
    "ko_digest",

    # Schemas
    "DocsViewRequest",
    "DocsViewResult",
    "DocsViewInvalidated",
    "FailureEmit",
    "PRICING_MIND",
    "get_price",
]
