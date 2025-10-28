"""
Signals Collector Service - Autonomy Phase-A P3.1

Collects ambient signals from environment and converts them into membrane.inject
envelopes for the consciousness bus:
- Console errors (from dashboard/frontend)
- Screenshots (evidence capture)
- Log anomalies (future: from service logs)

Features:
- Deduplication (hash-based, 60s window)
- Rate limiting (per-type cooldowns)
- Disk backlog (replayed automatically when the membrane is reachable again)
- Direct publish to the membrane WebSocket (no intermediate HTTP service)

Created: 2025-10-25 by Atlas (Infrastructure Engineer)
Spec: Phase-A Autonomy - P3 Signals Collector MVP
"""

from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import time
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Optional

try:
    from websockets.sync.client import connect as ws_connect  # type: ignore
except ImportError:  # pragma: no cover - dependency not installed
    ws_connect = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration
APP_NAME = "signals_collector"
PORT = 8010
HEARTBEAT = Path(f".heartbeats/{APP_NAME}.heartbeat")
HEARTBEAT.parent.mkdir(exist_ok=True)

# Disk backlog for resilience
BACKLOG_DIR = Path(".signals/backlog")
BACKLOG_DIR.mkdir(parents=True, exist_ok=True)

# Deduplication cache (signal_hash -> timestamp)
dedup_cache: Dict[str, float] = {}
DEDUP_WINDOW_SEC = 60.0  # 60 second dedup window

# Rate limiting (signal_type -> last_sent_timestamp)
rate_limit_cache: Dict[str, float] = {}
RATE_LIMITS = {
    "console_error": 5.0,
    "screenshot": 10.0,
    "log_anomaly": 15.0,
}

# Membrane WebSocket endpoint
WS_ENDPOINT = "ws://127.0.0.1:8000/api/ws"
DEFAULT_CITIZEN_ID = os.getenv("SIGNALS_DEFAULT_CITIZEN", "consciousness-infrastructure_mind-protocol_felix")

app = FastAPI(title="Signals Collector", version="1.0")


class ConsoleErrorSignal(BaseModel):
    error_message: str
    stack_trace: Optional[str] = None
    url: Optional[str] = None


class ScreenshotSignal(BaseModel):
    screenshot_path: str
    context: Optional[str] = None


def heartbeat_loop():
    import threading
    def _loop():
        while True:
            try:
                HEARTBEAT.write_text(str(int(time.time())))
            except Exception:
                pass
            try:
                flush_backlog()
            except Exception as exc:
                logger.debug(f"[SignalsCollector] Backlog flush skipped: {exc}")
            time.sleep(5)
    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()


def compute_signal_hash(signal_type: str, content: str) -> str:
    payload = f"{signal_type}:{content}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def is_duplicate(signal_hash: str) -> bool:
    now = time.time()
    expired = [h for h, ts in dedup_cache.items() if now - ts > DEDUP_WINDOW_SEC]
    for h in expired:
        del dedup_cache[h]
    if signal_hash in dedup_cache:
        return True
    dedup_cache[signal_hash] = now
    return False


def is_rate_limited(signal_type: str) -> bool:
    if signal_type not in RATE_LIMITS:
        return False
    cooldown = RATE_LIMITS[signal_type]
    now = time.time()
    last_sent = rate_limit_cache.get(signal_type, 0)
    if now - last_sent < cooldown:
        return True
    rate_limit_cache[signal_type] = now
    return False


def write_to_backlog(envelope: dict):
    try:
        metadata = envelope.get("metadata", {})
        filename = f"stimulus_{int(time.time()*1000)}_{metadata.get('stimulus_id', 'unknown')}.json"
        filepath = BACKLOG_DIR / filename
        filepath.write_text(json.dumps(envelope, indent=2))
        logger.info(f"[Backlog] Wrote: {filename}")
    except Exception as e:
        logger.error(f"[Backlog] Failed: {e}")


def build_membrane_envelope(
    *,
    signal_type: str,
    content: str,
    severity: float,
    origin: str,
    stimulus_id: Optional[str] = None,
    timestamp_ms: Optional[int] = None,
    dedupe_key: Optional[str] = None,
    channel: Optional[str] = None,
    citizen_id: Optional[str] = None,
    metadata_extra: Optional[dict] = None,
    features_extra: Optional[dict] = None,
) -> dict:
    timestamp_ms = timestamp_ms or int(time.time() * 1000)
    stimulus_id = stimulus_id or f"signal_{signal_type}_{timestamp_ms}"
    dedupe_key = dedupe_key or compute_signal_hash(signal_type, content)

    envelope = {
        "type": "membrane.inject",
        "citizen_id": citizen_id or DEFAULT_CITIZEN_ID,
        "channel": channel or f"signals.{signal_type}",
        "content": content,
        "severity": severity,
        "features_raw": {
            "urgency": severity,
            "novelty": 0.25,
            "trust": 0.6,
        },
        "metadata": {
            "stimulus_id": stimulus_id,
            "origin": origin,
            "timestamp_ms": timestamp_ms,
            "signal_type": signal_type,
            "dedupe_key": dedupe_key,
            "origin_chain_depth": 0,
            "origin_chain": [origin],
        },
    }

    if features_extra:
        envelope["features_raw"].update(features_extra)

    if metadata_extra:
        extra = {**metadata_extra}
        # Preserve canonical fields from overrides unless explicitly changed
        extra.pop("stimulus_id", None)
        extra.pop("timestamp_ms", None)
        extra.pop("origin_chain_depth", None)
        extra.pop("origin_chain", None)
        extra.pop("signal_type", None)
        extra.pop("dedupe_key", None)
        envelope["metadata"].update(extra)

    return envelope


def ensure_membrane_envelope(payload: dict) -> dict:
    """
    Upgrade legacy backlog payloads (stimulus dicts) to membrane.inject envelopes.
    """
    if payload.get("type") == "membrane.inject":
        return payload

    signal_type = payload.get("signal_type", "console_error")
    content = payload.get("content") or payload.get("text") or ""
    severity = float(payload.get("severity", 0.3))
    origin = payload.get("origin") or payload.get("metadata", {}).get("origin") or "signals_collector"
    timestamp_ms = payload.get("timestamp_ms")
    stimulus_id = payload.get("stimulus_id")
    metadata_extra = payload.get("metadata") or {}
    features_extra = payload.get("features_raw") or {}
    channel = payload.get("channel")
    citizen_id = payload.get("citizen_id")

    dedupe_key = metadata_extra.get("dedupe_key")
    if not dedupe_key:
        dedupe_key = compute_signal_hash(signal_type, content)

    return build_membrane_envelope(
        signal_type=signal_type,
        content=content,
        severity=severity,
        origin=origin,
        stimulus_id=stimulus_id,
        timestamp_ms=timestamp_ms,
        dedupe_key=dedupe_key,
        channel=channel,
        citizen_id=citizen_id,
        metadata_extra=metadata_extra,
        features_extra=features_extra,
    )


def send_envelope_over_ws(envelope: dict) -> bool:
    """
    Publish envelope over the membrane WebSocket.
    Opens a short-lived connection per send for resilience.
    """
    if ws_connect is None:
        logger.error("[SignalsCollector] websockets package unavailable; cannot publish membrane.inject")
        return False

    try:
        with ws_connect(WS_ENDPOINT, open_timeout=2, close_timeout=1) as ws:
            ws.send(json.dumps(envelope))
        logger.info("[SignalsCollector] Published membrane.inject sid=%s channel=%s",
                    envelope.get("metadata", {}).get("stimulus_id"),
                    envelope.get("channel"))
        return True
    except Exception as exc:
        logger.warning(f"[SignalsCollector] WebSocket publish failed: {exc}")
        return False


def flush_backlog():
    """
    Retry any envelopes that were previously backlogged.
    Processes files oldest-first to preserve ordering semantics.
    """
    for backlog_file in sorted(BACKLOG_DIR.glob("stimulus_*.json")):
        try:
            raw_payload = json.loads(backlog_file.read_text())
            envelope = ensure_membrane_envelope(raw_payload)
        except Exception as exc:
            logger.error(f"[Backlog] Corrupt entry {backlog_file.name}: {exc}")
            backlog_file.unlink(missing_ok=True)
            continue

        if send_envelope_over_ws(envelope):
            backlog_file.unlink(missing_ok=True)
        else:
            # Preserve ordering: stop once a publish fails
            break


def process_signal(
    signal_type: str,
    content: str,
    severity: float,
    origin: str = "signals_collector",
    *,
    metadata_extra: Optional[dict] = None,
    features_extra: Optional[dict] = None,
    channel: Optional[str] = None,
    citizen_id: Optional[str] = None,
) -> dict:
    signal_hash = compute_signal_hash(signal_type, content)
    if is_duplicate(signal_hash):
        logger.debug(f"[Dedupe] Already seen (hash={signal_hash})")
        return {"status": "deduplicated", "hash": signal_hash}
    if is_rate_limited(signal_type):
        logger.debug(f"[RateLimit] {signal_type} cooling down")
        return {"status": "rate_limited", "type": signal_type}

    envelope = build_membrane_envelope(
        signal_type=signal_type,
        content=content,
        severity=severity,
        origin=origin,
        dedupe_key=signal_hash,
        metadata_extra=metadata_extra,
        features_extra=features_extra,
        channel=channel,
        citizen_id=citizen_id,
    )
    stimulus_id = envelope["metadata"]["stimulus_id"]

    flush_backlog()

    if send_envelope_over_ws(envelope):
        return {"status": "published", "stimulus_id": stimulus_id}

    write_to_backlog(envelope)
    return {"status": "backlogged", "stimulus_id": stimulus_id}


@app.on_event("startup")
def startup():
    heartbeat_loop()
    logger.info(f"[SignalsCollector] Started on port {PORT}")


@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME}


@app.post("/console")
def collect_console_error(signal: ConsoleErrorSignal = Body(...)):
    content = signal.error_message
    if signal.stack_trace:
        stack_first_line = signal.stack_trace.split('\\n')[0] if signal.stack_trace else ""
        content = f"{signal.error_message} | {stack_first_line}"
    severity = 0.7 if "TypeError" in signal.error_message or "ReferenceError" in signal.error_message else 0.6
    metadata = {}
    if signal.stack_trace:
        metadata["stack_trace"] = signal.stack_trace
    if signal.url:
        metadata["url"] = signal.url

    result = process_signal(
        signal_type="console_error",
        content=content,
        severity=severity,
        origin="dashboard_console",
        metadata_extra=metadata or None,
        channel="signals.console_error",
    )
    return result


@app.post("/screenshot")
def collect_screenshot(signal: ScreenshotSignal = Body(...)):
    screenshot_path = Path(signal.screenshot_path)
    if not screenshot_path.exists():
        raise HTTPException(status_code=400, detail=f"Screenshot not found: {signal.screenshot_path}")
    content = f"Screenshot: {screenshot_path.name}"
    if signal.context:
        content = f"{content} | Context: {signal.context}"

    metadata = {"screenshot_path": str(screenshot_path)}
    if signal.context:
        metadata["context"] = signal.context

    features = {
        "evidence": 1.0,
    }

    result = process_signal(
        signal_type="screenshot",
        content=content,
        severity=0.5,
        origin="screenshot_capture",
        metadata_extra=metadata,
        features_extra=features,
        channel="signals.screenshot",
    )
    return result


@app.get("/backlog/count")
def get_backlog_count():
    backlog_files = list(BACKLOG_DIR.glob("stimulus_*.json"))
    return {"count": len(backlog_files), "backlog_dir": str(BACKLOG_DIR)}


@app.post("/backlog/flush")
def flush_backlog():
    backlog_files = list(BACKLOG_DIR.glob("stimulus_*.json"))
    forwarded = 0
    failed = 0
    for filepath in backlog_files:
        try:
            payload = json.loads(filepath.read_text())
            envelope = ensure_membrane_envelope(payload)
            if send_envelope_over_ws(envelope):
                filepath.unlink()
                forwarded += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"[BacklogFlush] Error: {e}")
            failed += 1
    return {"forwarded": forwarded, "failed": failed, "remaining": failed}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
