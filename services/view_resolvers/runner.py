"""
L2 View Resolvers - Main Runner (org boundary)

Membrane-native view resolver:
- Subscribes to docs.view.request events
- Validates CPS-1 quotes before compute
- Executes Select → Project → Render pipeline
- Emits docs.view.result or failure.emit
- Never crosses org boundary (L2 only)

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta, timezone
import traceback

from .selectors import get_selector
from .projectors import project, render
from .schemas import PRICING_MIND, get_price

logger = logging.getLogger(__name__)


# ============================================================================
# Simple Cache (digest-keyed)
# ============================================================================

class ViewCache:
    """Simple in-memory cache keyed by (view_type, format, params, path) + ko_digest"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[tuple, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def get(self, key: tuple) -> Optional[Dict[str, Any]]:
        """Get cached view if not expired"""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        cached_at = datetime.fromisoformat(entry.get("cached_at", "2020-01-01T00:00:00+00:00"))
        age = (datetime.now(timezone.utc) - cached_at).total_seconds()

        if age > self._ttl:
            del self._cache[key]
            return None

        return entry

    def set(self, key: tuple, value: Dict[str, Any]):
        """Cache view with timestamp"""
        value["cached_at"] = datetime.now(timezone.utc).isoformat()
        self._cache[key] = value

    def invalidate(self, pattern: str):
        """Invalidate cache keys matching pattern (e.g., 'architecture:/')"""
        # Simple prefix matching for now
        to_delete = [k for k in self._cache.keys() if pattern in str(k)]
        for k in to_delete:
            del self._cache[k]
        logger.info(f"[ViewCache] Invalidated {len(to_delete)} keys matching '{pattern}'")


# ============================================================================
# Simple Economy Stub (CPS-1 quote validation)
# ============================================================================

class EconomyStub:
    """
    Stub for CPS-1 economy integration.

    For now: validates quote_id format and checks pricing.
    Future: integrate with full services/economy/runtime.py
    """

    def __init__(self):
        self._quotes: Dict[str, Dict[str, Any]] = {}

    def validate_quote(self, quote_id: str, work: str, format: str) -> bool:
        """Verify quote_id is valid and not expired"""
        if not quote_id or not quote_id.startswith("q-"):
            logger.warning(f"[Economy] Invalid quote_id format: {quote_id}")
            return False

        # For stub: accept all well-formed quote_ids
        # Real implementation would check against economy service
        return True

    def debit(self, quote_id: str):
        """Settle quote (no-op for stub)"""
        logger.info(f"[Economy] Debit quote_id={quote_id} (stub: no-op)")
        # Future: call economy runtime to actually debit


# ============================================================================
# Main View Resolver (L2)
# ============================================================================

class ViewResolver:
    """
    L2 View Resolver - computes inside org boundary

    Responsibilities:
    - Subscribe to docs.view.request events
    - Validate CPS-1 quotes
    - Execute Cypher queries (Phase A: Select)
    - Project to view-models (Phase B: Project)
    - Render to format (Phase C: Render)
    - Emit docs.view.result or failure.emit
    - Cache by ko_digest
    """

    def __init__(
        self,
        bus: Any,  # Membrane bus for inject/broadcast
        graph: Any,  # FalkorDB adapter (query method)
        economy: Optional[EconomyStub] = None,
        cache: Optional[ViewCache] = None
    ):
        self.bus = bus
        self.graph = graph
        self.economy = economy or EconomyStub()
        self.cache = cache or ViewCache(ttl_seconds=300)

        logger.info("[ViewResolver] Initialized (L2 org boundary)")

    def on_docs_view_request(self, envelope: Dict[str, Any]):
        """
        Handle docs.view.request event

        Flow:
        1. Validate CPS-1 quote
        2. Check cache (by ko_digest)
        3. If miss: Select → Project → Render
        4. Cache result, debit quote
        5. Emit docs.view.result
        6. On error: emit failure.emit + error result
        """
        c = envelope.get("content", {})
        request_id = c.get("request_id", "unknown")

        # Build cache key
        key = (
            c.get("view_type"),
            c.get("format"),
            tuple(sorted(c.get("params", {}).items())),
            c.get("scope", {}).get("path", "/")
        )

        try:
            # Step 1: CPS-1 quote validation
            quote_id = c.get("quote_id")
            if not self.economy.validate_quote(quote_id, work="docs.view", format=c.get("format")):
                self._emit_failure(
                    code_location="runner.py:validate_quote",
                    exception="Missing or invalid quote_id",
                    severity="error",
                    suggestion="Request quote via economy.quote.request first",
                    trace_id=request_id
                )
                self._emit_result_error(request_id, "E_QUOTE", "Quote validation failed")
                return

            # Step 2: Check cache
            hit = self.cache.get(key)
            if hit:
                logger.info(f"[ViewResolver] Cache hit for {key}")
                self._emit_result_ok(request_id, hit)
                return

            # Step 3: Execute pipeline
            logger.info(f"[ViewResolver] Cache miss, computing view: {c.get('view_type')}")

            rows = self._select(c)
            vm = self._project(c["view_type"], rows)
            rendered = render(vm, c["format"])

            payload = {
                "request_id": request_id,
                "status": "ok",
                "format": c["format"],
                "view_type": c["view_type"],
                "view_model": rendered,
                "provenance": {
                    "ko_digest": vm["provenance"]["ko_digest"],
                    "selectors": [self._selector_text(c)],
                    "evidence_nodes": []  # Future: extract from rows
                },
                "cache": {"ttl_sec": 300}
            }

            # Step 4: Cache + debit
            self.cache.set(key, payload)
            self.economy.debit(quote_id)

            # Step 5: Emit result
            self._emit_result_ok(request_id, payload)

        except Exception as e:
            # Step 6: Fail-loud (R-400/R-401 compliance)
            logger.error(f"[ViewResolver] Error computing view: {e}", exc_info=True)

            self._emit_failure(
                code_location="runner.py:on_docs_view_request",
                exception=repr(e),
                severity="error",
                suggestion="Check selector parameters and graph schema",
                trace_id=request_id
            )

            self._emit_result_error(
                request_id,
                "E_RESOLVER",
                f"View computation failed: {str(e)}"
            )

    def on_graph_delta(self, envelope: Dict[str, Any]):
        """
        Handle graph.delta.* events for cache invalidation

        Future: implement surgical invalidation via ko_digest matching
        For now: invalidate by view_type
        """
        # Extract affected view types from graph delta
        # Simple heuristic: invalidate all for now
        logger.info("[ViewResolver] graph.delta.* received, invalidating cache")
        self.cache.invalidate("architecture")
        self.cache.invalidate("api")
        self.cache.invalidate("coverage")

        # Emit invalidation broadcast
        self.bus.broadcast("docs.view.invalidated", {
            "content": {
                "reasons": ["graph.delta.node.upsert"],
                "affects": ["architecture:*", "api:*", "coverage:*", "index:*"]
            }
        })

    # ========================================================================
    # Pipeline Phases
    # ========================================================================

    def _select(self, content: Dict[str, Any]) -> list:
        """Phase A: Execute Cypher selector"""
        view_type = content["view_type"]
        selector = get_selector(view_type)

        # Build params from scope
        scope = content.get("scope", {})
        params = {
            "scope_org": scope.get("org"),
            "scope_path": scope.get("path", "/"),
            **content.get("params", {})
        }

        return self.graph.query(selector, params=params)

    def _project(self, view_type: str, rows: list) -> Dict[str, Any]:
        """Phase B: Project to view-model"""
        return project(view_type, rows)

    def _selector_text(self, content: Dict[str, Any]) -> str:
        """Get selector text for provenance"""
        return get_selector(content["view_type"])

    # ========================================================================
    # Event Emission (membrane bus)
    # ========================================================================

    def _emit_result_ok(self, request_id: str, payload: Dict[str, Any]):
        """Emit successful docs.view.result"""
        self.bus.broadcast("docs.view.result", {"content": payload})
        logger.info(f"[ViewResolver] Emitted docs.view.result (ok) for request_id={request_id}")

    def _emit_result_error(self, request_id: str, error_code: str, message: str):
        """Emit error docs.view.result"""
        self.bus.broadcast("docs.view.result", {
            "content": {
                "request_id": request_id,
                "status": "error",
                "error": {
                    "message": message,
                    "code": error_code
                }
            }
        })
        logger.error(f"[ViewResolver] Emitted docs.view.result (error) for request_id={request_id}: {message}")

    def _emit_failure(
        self,
        code_location: str,
        exception: str,
        severity: str,
        suggestion: str,
        trace_id: Optional[str] = None
    ):
        """Emit failure.emit (R-400/R-401 compliance)"""
        self.bus.broadcast("failure.emit", {
            "content": {
                "code_location": code_location,
                "exception": exception,
                "severity": severity,
                "suggestion": suggestion,
                "trace_id": trace_id
            }
        })
        logger.warning(f"[ViewResolver] Emitted failure.emit: {code_location} - {exception}")
