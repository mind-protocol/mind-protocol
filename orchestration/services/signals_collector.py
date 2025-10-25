"""
Signals Collector Service - Operational signals → consciousness stimuli bridge

Purpose: Normalize operational signals (logs, console errors, screenshots, drift)
         into StimulusEnvelope format for L2 consciousness processing.

Features:
- Deduplication (5-minute rolling window)
- Rate limiting (token bucket per bucket)
- Priority scoring (quantile gates)
- Forward to Stimulus Injection service (@8001)
- Backlog queue for resilience

Created: 2025-10-25 by Atlas
Spec: docs/specs/v2/autonomy/SIGNALS_TO_STIMULI_BRIDGE.md v1.1
"""

from fastapi import FastAPI, UploadFile, HTTPException, Body
import httpx
import time
import hashlib
import asyncio
import os
import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service metadata
APP_NAME = "signals_collector"
VERSION = "1.0"
HEARTBEAT_PATH = ".heartbeats/signals_collector.heartbeat"

# Configuration
INJECTOR_URL = os.getenv("INJECTOR_URL", "http://localhost:8001")
DEDUPE_WINDOW_SEC = int(os.getenv("DEDUPE_WINDOW_SEC", "300"))  # 5 minutes
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "2"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
SIGNALS_COLLECTOR_PORT = int(os.getenv("SIGNALS_COLLECTOR_PORT", "8003"))

# FastAPI app
app = FastAPI(title="Signals Collector", version=VERSION)

# State
recent_digests: Dict[str, Tuple[float, int]] = {}  # digest → (first_seen_ts, count)
stats = {
    "ingested": 0,
    "deduplicated": 0,
    "rate_limited": 0,
    "injections_failed": 0
}
start_time = time.time()


# === Rate Limiter ===

class RateLimiter:
    """
    Token bucket rate limiter per bucket key.

    Refills tokens continuously based on configured rate.
    Prevents signal storms from overwhelming downstream services.
    """

    def __init__(self, rate_per_min: int = 10):
        self.rate_per_min = rate_per_min
        self.buckets: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": rate_per_min, "last_refill": time.time()}
        )

    def allow(self, bucket: str) -> bool:
        """
        Check if request allowed for bucket.

        Args:
            bucket: Rate limit bucket key (e.g., "console:TypeError")

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        b = self.buckets[bucket]

        # Refill tokens based on elapsed time
        elapsed = now - b["last_refill"]
        tokens_to_add = elapsed * (self.rate_per_min / 60.0)
        b["tokens"] = min(self.rate_per_min, b["tokens"] + tokens_to_add)
        b["last_refill"] = now

        if b["tokens"] >= 1.0:
            b["tokens"] -= 1.0
            return True
        return False


rate_limiter = RateLimiter(rate_per_min=RATE_LIMIT_PER_MIN)


# === Deduplication ===

def dedupe(content: str, stack: str = "") -> Tuple[bool, str]:
    """
    Deduplicate signals based on content + stack digest.

    Uses 5-minute rolling window to collapse repeated signals.

    Args:
        content: Signal message
        stack: Stack trace (optional)

    Returns:
        (is_duplicate, digest_key)
    """
    digest_input = content + stack
    digest = hashlib.sha256(digest_input.encode()).hexdigest()[:16]

    now = time.time()

    if digest in recent_digests:
        first_seen, count = recent_digests[digest]
        if now - first_seen < DEDUPE_WINDOW_SEC:
            # Still within window - increment count
            recent_digests[digest] = (first_seen, count + 1)
            return True, digest

    # New or expired - reset
    recent_digests[digest] = (now, 1)
    return False, digest


# === Digest Cleanup (Background Task) ===

async def cleanup_digests():
    """
    Background task to remove expired digests from memory.
    Runs every 60 seconds.
    """
    while True:
        await asyncio.sleep(60)

        now = time.time()
        expired = [
            digest for digest, (first_seen, _) in recent_digests.items()
            if now - first_seen >= DEDUPE_WINDOW_SEC
        ]

        for digest in expired:
            del recent_digests[digest]

        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired digests")


# === Forward to Injector ===

async def forward_to_injector(envelope: dict) -> dict:
    """
    Forward StimulusEnvelope to Stimulus Injection service.

    Args:
        envelope: StimulusEnvelope dict

    Returns:
        Injector response

    Raises:
        HTTPException if injection fails
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{INJECTOR_URL}/inject", json=envelope)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        stats["injections_failed"] += 1
        logger.error(f"Failed to forward to injector: {e}")
        # TODO: Add to backlog queue for resilience
        raise HTTPException(status_code=502, detail=f"Injection failed: {str(e)}")


# === HTTP Endpoints ===

@app.post("/ingest/console")
async def ingest_console(msg: dict = Body(...)):
    """
    Ingest browser console error from Next.js beacon.

    Request body:
        {
            "message": "TypeError: Cannot read properties of undefined",
            "stack": "TypeError: ...\\n  at Component:45",
            "filename": "AutonomyIndicator.tsx",
            "lineno": 45,
            "colno": 12
        }

    Response:
        {
            "status": "injected" | "deduplicated",
            "stimulus_id": "uuid",
            "dedupe_key": "hash",
            "count": <int> (if deduplicated)
        }
    """
    content = msg.get("message", "Console error")
    stack = msg.get("stack", "")

    # Deduplicate
    deduped, digest = dedupe(content, stack)
    if deduped:
        stats["deduplicated"] += 1
        count = recent_digests[digest][1]
        logger.debug(f"Deduplicated console error (count={count}): {content[:50]}")
        return {
            "status": "deduplicated",
            "dedupe_key": digest,
            "count": count
        }

    # Rate limit
    if not rate_limiter.allow("console:error"):
        stats["rate_limited"] += 1
        logger.warning(f"Rate limited console error: {content[:50]}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Create StimulusEnvelope
    stimulus_id = hashlib.md5(f"{time.time()}:{content}".encode()).hexdigest()
    envelope = {
        "stimulus_id": stimulus_id,
        "timestamp_ms": int(time.time() * 1000),
        "scope": "organizational",
        "source_type": "console",
        "actor": "signals_collector",
        "content": content,
        "metadata": {
            "severity": "error",
            "service": "dashboard",
            "stack": stack,
            "filename": msg.get("filename"),
            "lineno": msg.get("lineno"),
            "colno": msg.get("colno"),
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": [],
            "dedupe_key": digest
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    # Forward to injector
    result = await forward_to_injector(envelope)
    stats["ingested"] += 1

    logger.info(f"Injected console error: {content[:50]}")

    return {
        "status": "injected",
        "stimulus_id": stimulus_id,
        "dedupe_key": digest
    }


@app.post("/ingest/log")
async def ingest_log(item: dict = Body(...)):
    """
    Ingest backend log error entry.

    Request body:
        {
            "title": "Service error in websocket_server",
            "level": "error" | "warn" | "info",
            "service": "websocket_server",
            "stack": "Traceback (most recent call last)...",
            "timestamp_ms": 1730074800000
        }

    Response: Same as /ingest/console
    """
    content = item.get("title", "Service error")
    stack = item.get("stack", "")

    # Deduplicate
    deduped, digest = dedupe(content, stack)
    if deduped:
        stats["deduplicated"] += 1
        count = recent_digests[digest][1]
        logger.debug(f"Deduplicated log error (count={count}): {content[:50]}")
        return {
            "status": "deduplicated",
            "dedupe_key": digest,
            "count": count
        }

    # Rate limit by service
    service = item.get("service", "unknown")
    bucket = f"log:{service}"
    if not rate_limiter.allow(bucket):
        stats["rate_limited"] += 1
        logger.warning(f"Rate limited log error from {service}: {content[:50]}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Create StimulusEnvelope
    stimulus_id = hashlib.md5(f"{time.time()}:{content}".encode()).hexdigest()
    envelope = {
        "stimulus_id": stimulus_id,
        "timestamp_ms": item.get("timestamp_ms", int(time.time() * 1000)),
        "scope": "organizational",
        "source_type": "error.log",
        "actor": "signals_collector",
        "content": content,
        "metadata": {
            "severity": item.get("level", "error"),
            "service": service,
            "stack": stack,
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": [],
            "dedupe_key": digest
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    # Forward to injector
    result = await forward_to_injector(envelope)
    stats["ingested"] += 1

    logger.info(f"Injected log error from {service}: {content[:50]}")

    return {
        "status": "injected",
        "stimulus_id": stimulus_id,
        "dedupe_key": digest
    }


@app.post("/ingest/screenshot")
async def ingest_screenshot(file: UploadFile):
    """
    Ingest screenshot upload for evidence attachment.

    Request: Multipart form data with 'file' field

    Response:
        {
            "status": "injected",
            "stimulus_id": "uuid",
            "screenshot_path": "data/evidence/timestamp_filename.png"
        }
    """
    timestamp = int(time.time() * 1000)
    safe_filename = file.filename or "screenshot.png"
    filename = f"{timestamp}_{safe_filename}"
    filepath = f"data/evidence/{filename}"

    # Ensure directory exists
    os.makedirs("data/evidence", exist_ok=True)

    # Write file to disk
    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save screenshot: {str(e)}")

    # Create StimulusEnvelope
    stimulus_id = hashlib.md5(f"{timestamp}:{safe_filename}".encode()).hexdigest()
    envelope = {
        "stimulus_id": stimulus_id,
        "timestamp_ms": timestamp,
        "scope": "organizational",
        "source_type": "screenshot",
        "actor": "signals_collector",
        "content": "Screenshot evidence",
        "metadata": {
            "severity": "info",
            "screenshot_path": filepath,
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": [],
            "sensitivity": "internal"  # Production safety: never route to N3
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    # Forward to injector
    result = await forward_to_injector(envelope)
    stats["ingested"] += 1

    logger.info(f"Injected screenshot: {filepath}")

    return {
        "status": "injected",
        "stimulus_id": stimulus_id,
        "screenshot_path": filepath
    }


@app.get("/health")
async def health():
    """
    Health check for guardian monitoring.

    Returns:
        {
            "status": "healthy",
            "uptime_seconds": <int>,
            "signals_ingested": <int>,
            "signals_deduplicated": <int>,
            "signals_rate_limited": <int>,
            "injections_failed": <int>
        }
    """
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time),
        "signals_ingested": stats["ingested"],
        "signals_deduplicated": stats["deduplicated"],
        "signals_rate_limited": stats["rate_limited"],
        "injections_failed": stats["injections_failed"]
    }


# === Heartbeat Writer (Background Task) ===

async def write_heartbeat():
    """
    Background task to write heartbeat file for guardian monitoring.
    Updates every 5 seconds.
    """
    while True:
        try:
            os.makedirs(".heartbeats", exist_ok=True)
            with open(HEARTBEAT_PATH, "w") as f:
                f.write(str(int(time.time() * 1000)))
        except Exception as e:
            logger.error(f"Failed to write heartbeat: {e}")

        await asyncio.sleep(5)


@app.on_event("startup")
async def startup():
    """Start background tasks on service startup."""
    asyncio.create_task(write_heartbeat())
    asyncio.create_task(cleanup_digests())
    logger.info(f"Signals Collector v{VERSION} started on port {SIGNALS_COLLECTOR_PORT}")
    logger.info(f"Forwarding to injector: {INJECTOR_URL}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SIGNALS_COLLECTOR_PORT)
