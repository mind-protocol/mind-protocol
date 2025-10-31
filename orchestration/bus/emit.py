# orchestration/bus/emit.py
from typing import Any, Dict
from datetime import datetime
import uuid, logging

logger = logging.getLogger("failure")

def emit_failure(*, component: str, reason: str, detail: str, span: Dict[str, Any] | None = None):
    # If membrane is up, inject the real event; otherwise, log loudly.
    # Minimal inline version (you can replace with the real bus.inject):
    payload = {
        "type": "failure.emit",
        "provenance": {"ecosystem_id": "mindnet", "org_id": "mind-protocol", "component": component},
        "content": {"reason": reason, "detail": detail, "span": span or {}, "ts": datetime.utcnow().isoformat(), "id": uuid.uuid4().hex}
    }
    try:
        # bus.inject(payload)   # uncomment when bus is guaranteed
        logger.error("FAILURE_EMIT %s", payload)  # loud fallback
    except Exception as e:
        logger.critical("FAILURE_EMIT_LOST %s (emit error: %s)", payload, e)