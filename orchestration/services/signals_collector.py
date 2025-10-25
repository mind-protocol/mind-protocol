"""
Signals Collector Service - Autonomy Phase-A P3.1

Collects ambient signals from environment and converts to stimulus envelopes:
- Console errors (from dashboard/frontend)
- Screenshots (evidence capture)  
- Log anomalies (future: from service logs)

Features:
- Deduplication (hash-based, 60s window)
- Rate limiting (per-type cooldowns)
- Disk backlog (resilience when :8001 down)
- Auto-forward to stimulus_injection_service (:8001)

Created: 2025-10-25 by Atlas (Infrastructure Engineer)
Spec: Phase-A Autonomy - P3 Signals Collector MVP
"""

from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
import uvicorn
import time
import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional

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

# Stimulus injection service endpoint
STIMULUS_SERVICE_URL = "http://localhost:8001/inject"

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


def write_to_backlog(stimulus: dict):
    try:
        filename = f"stimulus_{int(time.time()*1000)}_{stimulus.get('stimulus_id', 'unknown')}.json"
        filepath = BACKLOG_DIR / filename
        filepath.write_text(json.dumps(stimulus, indent=2))
        logger.info(f"[Backlog] Wrote: {filename}")
    except Exception as e:
        logger.error(f"[Backlog] Failed: {e}")


def forward_to_stimulus_service(stimulus: dict) -> bool:
    try:
        response = requests.post(STIMULUS_SERVICE_URL, json=stimulus, timeout=2.0)
        if response.status_code == 200:
            logger.info(f"[Forward] OK - stimulus_id={stimulus.get('stimulus_id')}")
            return True
        else:
            logger.warning(f"[Forward] Failed ({response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        logger.warning("[Forward] Connection refused (:8001 down)")
        return False
    except Exception as e:
        logger.error(f"[Forward] Error: {e}")
        return False


def process_signal(signal_type: str, content: str, severity: float, origin: str = "signals_collector") -> dict:
    signal_hash = compute_signal_hash(signal_type, content)
    if is_duplicate(signal_hash):
        logger.debug(f"[Dedupe] Already seen (hash={signal_hash})")
        return {"status": "deduplicated", "hash": signal_hash}
    if is_rate_limited(signal_type):
        logger.debug(f"[RateLimit] {signal_type} cooling down")
        return {"status": "rate_limited", "type": signal_type}
    stimulus = {
        "stimulus_id": f"signal_{signal_type}_{int(time.time()*1000)}",
        "timestamp_ms": int(time.time() * 1000),
        "citizen_id": "felix",
        "text": content,
        "severity": severity,
        "origin": origin,
        "signal_type": signal_type
    }
    forwarded = forward_to_stimulus_service(stimulus)
    if not forwarded:
        write_to_backlog(stimulus)
        return {"status": "backlogged", "stimulus_id": stimulus["stimulus_id"]}
    return {"status": "forwarded", "stimulus_id": stimulus["stimulus_id"]}


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
    result = process_signal(signal_type="console_error", content=content, severity=severity, origin="dashboard_console")
    return result


@app.post("/screenshot")
def collect_screenshot(signal: ScreenshotSignal = Body(...)):
    screenshot_path = Path(signal.screenshot_path)
    if not screenshot_path.exists():
        raise HTTPException(status_code=400, detail=f"Screenshot not found: {signal.screenshot_path}")
    content = f"Screenshot: {screenshot_path.name}"
    if signal.context:
        content = f"{content} | Context: {signal.context}"
    result = process_signal(signal_type="screenshot", content=content, severity=0.5, origin="screenshot_capture")
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
            stimulus = json.loads(filepath.read_text())
            if forward_to_stimulus_service(stimulus):
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
