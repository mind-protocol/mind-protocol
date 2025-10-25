"""
Queue Poller Service - Ambient Signals to Consciousness Injection

Drains .stimuli/queue.jsonl and injects stimuli into consciousness engines via control API.

Architecture:
- Reads .stimuli/queue.jsonl with atomic offset tracking
- POSTs to /api/engines/{citizen}/inject for each stimulus
- Handles backlog on API failures (writes to .signals/backlog/)
- Heartbeat every 5s for guardian monitoring
- Idempotent (offset-based, won't double-inject)

Author: Atlas (Infrastructure)
Blueprint: Nicolas
Date: 2025-10-25
Priority: P0 - Critical path to autonomy
"""

from pathlib import Path
import json
import time
import hashlib
import httpx
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
MIND_PROTOCOL_ROOT = Path(__file__).parent.parent.parent
QUEUE = MIND_PROTOCOL_ROOT / ".stimuli" / "queue.jsonl"
OFFSET = MIND_PROTOCOL_ROOT / ".stimuli" / "queue.offset"
BACKLOG_DIR = MIND_PROTOCOL_ROOT / ".signals" / "backlog"
HB = MIND_PROTOCOL_ROOT / ".heartbeats" / "queue_poller.heartbeat"

# Ensure directories exist
BACKLOG_DIR.mkdir(parents=True, exist_ok=True)
HB.parent.mkdir(parents=True, exist_ok=True)

# Control API endpoint
CONTROL_API_BASE = "http://127.0.0.1:8000"


def read_offset() -> int:
    """Read current queue offset (number of lines processed)."""
    try:
        return int(OFFSET.read_text(encoding='utf-8').strip())
    except (FileNotFoundError, ValueError):
        return 0


def write_offset(n: int):
    """Atomically write new offset."""
    tmp = Path(str(OFFSET) + ".tmp")
    tmp.write_text(str(n), encoding='utf-8')
    tmp.replace(OFFSET)


def flush_backlog(cli: httpx.Client):
    """
    Retry backlogged stimuli.

    Attempts to inject previously failed stimuli from .signals/backlog/
    If successful, deletes backlog file.
    """
    for p in sorted(BACKLOG_DIR.glob("*.json")):
        try:
            payload = json.loads(p.read_text(encoding='utf-8'))
            citizen = payload.pop('citizen_id', 'felix')

            r = cli.post(
                f"{CONTROL_API_BASE}/api/engines/{citizen}/inject",
                json=payload,
                timeout=5.0
            )

            if r.is_success:
                logger.info(f"[Backlog] Recovered sid={payload.get('stimulus_id')} citizen={citizen}")
                p.unlink()  # Success - remove from backlog
            else:
                logger.warning(f"[Backlog] Retry failed sid={payload.get('stimulus_id')}: HTTP {r.status_code}")
                break  # Stop trying, leave for next cycle

        except Exception as e:
            logger.error(f"[Backlog] Failed to process {p.name}: {e}")
            break  # Leave for next cycle


def poll_once():
    """
    Poll queue once and inject new stimuli.

    Reads queue.jsonl from last offset, injects each stimulus via control API,
    updates offset on success, backlogs on failure.
    """
    if not QUEUE.exists():
        return

    # Read all lines from queue
    try:
        lines = QUEUE.read_text(encoding='utf-8').splitlines()
    except Exception as e:
        logger.error(f"[QueuePoller] Failed to read queue: {e}")
        return

    idx = read_offset()
    if idx >= len(lines):
        return  # No new lines

    with httpx.Client(timeout=5.0) as cli:
        # First, try to flush any backlogged items
        flush_backlog(cli)

        # Process new lines
        while idx < len(lines):
            raw = lines[idx].strip()
            idx += 1

            if not raw:
                continue  # Skip empty lines

            try:
                # Parse stimulus envelope
                env = json.loads(raw)

                # Extract fields
                citizen = (env.get("citizen_id") or "felix").strip()
                text = (env.get("text") or "").strip()

                # Skip empty stimuli
                if not text:
                    logger.debug(f"[QueuePoller] Skipping empty stimulus at line {idx}")
                    continue

                # Build payload for control API
                payload = {
                    "stimulus_id": env.get("stimulus_id") or hashlib.md5(raw.encode()).hexdigest()[:16],
                    "text": text,
                    "severity": float(env.get("severity", 0.3)),
                    "origin": env.get("origin") or "external",
                    "timestamp_ms": env.get("timestamp_ms"),
                    "metadata": env.get("metadata") or {}
                }

                # Inject via control API
                r = cli.post(
                    f"{CONTROL_API_BASE}/api/engines/{citizen}/inject",
                    json=payload
                )

                if r.is_success:
                    logger.info(f"[QueuePoller] Injected sid={payload['stimulus_id']} citizen={citizen} len={len(text)}")
                else:
                    # API failure - backlog this stimulus
                    logger.warning(f"[QueuePoller] Injection failed sid={payload['stimulus_id']}: HTTP {r.status_code}")

                    backlog_file = BACKLOG_DIR / f"{payload['stimulus_id']}_{int(time.time())}.json"
                    backlog_file.write_text(
                        json.dumps({"citizen_id": citizen, **payload}),
                        encoding='utf-8'
                    )

                    logger.info(f"[QueuePoller] Backlogged sid={payload['stimulus_id']} for retry")

            except Exception as e:
                logger.error(f"[QueuePoller] Failed to process line {idx}: {e}")
                # Skip this line and continue

        # Update offset (mark all lines as processed, even failures are backlogged)
        write_offset(idx)


def heartbeat_loop():
    """
    Write heartbeat every 5s for guardian monitoring.

    Guardian will restart service if heartbeat stops updating.
    """
    while True:
        try:
            HB.write_text(str(int(time.time())), encoding='utf-8')
        except Exception as e:
            logger.error(f"[Heartbeat] Failed to write: {e}")

        time.sleep(5)


def main():
    """
    Main service loop.

    - Starts heartbeat thread
    - Polls queue every 1s
    - Runs forever under guardian supervision
    """
    logger.info("=" * 70)
    logger.info("QUEUE POLLER SERVICE - Starting")
    logger.info("=" * 70)
    logger.info(f"Queue: {QUEUE}")
    logger.info(f"Offset: {OFFSET}")
    logger.info(f"Backlog: {BACKLOG_DIR}")
    logger.info(f"Control API: {CONTROL_API_BASE}")
    logger.info(f"Heartbeat: {HB}")
    logger.info("=" * 70)

    # Start heartbeat thread
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    logger.info("[QueuePoller] Heartbeat thread started")

    # Main polling loop
    logger.info("[QueuePoller] Starting queue polling (1s interval)")

    while True:
        try:
            poll_once()
        except Exception as e:
            logger.error(f"[QueuePoller] Polling cycle failed: {e}")

        time.sleep(1)  # Poll every second


if __name__ == "__main__":
    main()
