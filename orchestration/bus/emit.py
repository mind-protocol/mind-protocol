# orchestration/bus/emit.py
"""Failure emission helpers for fail-loud contract."""

from datetime import datetime
import logging
import uuid
from typing import Any, Dict

logger = logging.getLogger("failure")


def emit_failure(*, component: str, reason: str, detail: str, span: Dict[str, Any] | None = None) -> None:
    """Emit a failure event or, at minimum, log loudly."""

    payload = {
        "type": "failure.emit",
        "provenance": {
            "ecosystem_id": "mindnet",
            "org_id": "mind-protocol",
            "component": component,
        },
        "content": {
            "reason": reason,
            "detail": detail,
            "span": span or {},
            "ts": datetime.utcnow().isoformat(),
            "id": uuid.uuid4().hex,
        },
    }

    try:
        # TODO: integrate real bus once membrane is stable.
        logger.error("FAILURE_EMIT %s", payload)
    except Exception as err:  # pragma: no cover - defensive
        logger.critical("FAILURE_EMIT_LOST %s (emit error: %s)", payload, err)
