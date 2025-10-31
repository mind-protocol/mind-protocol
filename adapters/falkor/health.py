"""Health check helpers for Falkor adapters."""
from __future__ import annotations

from typing import Any, Mapping


def check_health(adapter: Any) -> Mapping[str, Any]:
    """Return a coarse health snapshot for Falkor persistence."""

    status = {"status": "unknown"}
    ping = getattr(adapter, "ping", None)
    if callable(ping):
        try:
            result = ping()
        except Exception as exc:  # pragma: no cover - defensive guard
            return {"status": "error", "detail": str(exc)}
        status["status"] = "ok" if result else "degraded"
    else:
        status["status"] = "ok"
    return status
