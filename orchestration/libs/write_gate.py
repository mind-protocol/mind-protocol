"""
Write Gate enforcement for graph mutations.

Guards graph writers against cross-layer access by requiring an explicit
context namespace (e.g. ``L2:consciousness-infrastructure_mind-protocol``).
When a mismatch is detected we emit a ``telemetry.write.denied`` event and
raise ``PermissionError``.

Usage:
    @write_gate("L2:consciousness-infrastructure_mind-protocol")
    def upsert_org_node(..., ctx=None):
        ...

    @write_gate(lambda self, scope, **_: self._namespace_for_scope(scope))
    async def scoped_write(..., ctx=None):
        ...
"""

from __future__ import annotations

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

logger = logging.getLogger(__name__)

NamespaceArg = Union[str, Callable[..., str]]

_BROADCASTER: Optional[ConsciousnessStateBroadcaster] = None


def _ensure_broadcaster() -> Optional[ConsciousnessStateBroadcaster]:
    """Lazily instantiate the WebSocket broadcaster."""
    global _BROADCASTER
    if _BROADCASTER is not None:
        return _BROADCASTER

    try:
        _BROADCASTER = ConsciousnessStateBroadcaster()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("[WriteGate] Broadcaster unavailable: %s", exc)
        _BROADCASTER = None
    return _BROADCASTER


def _schedule(coro: Any) -> None:
    """Schedule coroutine on running loop or run synchronously if none."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
    else:
        loop.create_task(coro)


def _emit_write_denied(payload: Dict[str, Any]) -> None:
    """Emit telemetry event when a write is blocked."""
    logger.warning(
        "[WriteGate] Cross-layer write denied",
        extra={"write_gate": payload}
    )

    broadcaster = _ensure_broadcaster()
    if not broadcaster or not getattr(broadcaster, "available", False):
        return

    try:
        _schedule(broadcaster.broadcast_event("telemetry.write.denied", payload))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("[WriteGate] Failed to broadcast telemetry.write.denied: %s", exc)


def write_gate(expected_namespace: NamespaceArg) -> Callable:
    """
    Decorator enforcing namespace checks on writer functions.

    Args:
        expected_namespace: Either a string namespace (``L2:<org>``) or a callable
            receiving the wrapped function's args/kwargs (including ``ctx``) and
            returning the expected namespace string.
    """

    def decorator(fn: Callable):
        is_async = asyncio.iscoroutinefunction(fn)

        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            _enforce(fn, expected_namespace, args, kwargs)
            return await fn(*args, **kwargs)

        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            _enforce(fn, expected_namespace, args, kwargs)
            return fn(*args, **kwargs)

        return async_wrapper if is_async else sync_wrapper

    return decorator


def _enforce(
    fn: Callable,
    expected_namespace: NamespaceArg,
    args: tuple,
    kwargs: Dict[str, Any]
) -> None:
    """Helper performing the namespace comparison and telemetry emission."""
    ctx = kwargs.get("ctx") or {}
    actual_ns = ctx.get("ns")

    expected_ns = (
        expected_namespace(*args, **kwargs)
        if callable(expected_namespace)
        else expected_namespace
    )

    if actual_ns != expected_ns:
        payload = {
            "expected": expected_ns,
            "got": actual_ns,
            "fn": getattr(fn, "__qualname__", getattr(fn, "__name__", "unknown")),
        }
        extra_ctx = {k: v for k, v in ctx.items() if k != "ns"}
        if extra_ctx:
            payload["ctx"] = extra_ctx
        _emit_write_denied(payload)
        raise PermissionError("cross-layer write denied")


def namespace_for_graph(graph_name: Optional[str]) -> str:
    """
    Map a FalkorDB graph name to its hierarchical namespace.

    Returns:
        String of form ``Lx:<graph>`` or ``unknown:<graph>`` when unidentified.
    """
    if not graph_name:
        return "unknown"

    graph_lower = graph_name.lower()

    # L1 (citizen / personal)
    if (
        graph_lower.startswith("consciousness-infrastructure_mind-protocol_")
        or graph_lower.startswith("citizen_")
    ):
        return f"L1:{graph_name}"

    # L2 (organization)
    if graph_lower in {
        "consciousness-infrastructure_mind-protocol",
        "org_mind_protocol",
        "mind_protocol_collective_graph",
    } or graph_lower.startswith(("org_", "collective_")):
        return f"L2:{graph_name}"

    # L3 (ecosystem)
    if graph_lower in {
        "consciousness-infrastructure",
        "ecosystem_public",
    } or graph_lower.startswith("ecosystem_"):
        return f"L3:{graph_name}"

    # L4 (protocol-wide)
    if graph_lower == "protocol":
        return f"L4:{graph_name}"

    return f"unknown:{graph_name}"
