"""
L2 Logger - Production-Grade Script Error Injection to Consciousness Substrate

Sends ERROR/CRITICAL logs from orchestration scripts to signals_collector for
injection into the L2 graph via membrane.inject envelopes.

Features:
- Graph-aware attribution (scripts know their own node IDs)
- Non-blocking emission (queue + background flusher, never blocks main flow)
- Client-side fingerprinting (stable dedup across restarts)
- Redaction & size limits (secrets scrubbed, stacks truncated)
- Resilient spill-to-disk on offline collector

Usage:
    from orchestration.libs.l2_logger import setup_l2_logger

    logger = setup_l2_logger(
        script_name="resurrect_all_citizens",
        script_path="orchestration/scripts/resurrect_all_citizens.py"
    )

    logger.error("Bootstrap failed for citizen %s", citizen_id)
    # → Injected to L2 graph with graph-aware attribution

Created: 2025-10-29 by Ada (Architect)
Spec: Phase-A Autonomy - L2 Logging Harmonization
"""

import logging
import hashlib
import json
import re
import threading
import time
import traceback as tb_module
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Configuration
COLLECTOR_URL = "http://127.0.0.1:8010"
QUEUE_CAPACITY = 1000
BATCH_SIZE = 25
BATCH_TIMEOUT_SEC = 0.25
SPOOL_DIR = Path("/tmp/l2-logs-spool")
STACK_FINGERPRINT_DEPTH = 5
MAX_STACK_LINES = 60
MAX_STACK_BYTES = 16 * 1024  # 16KB
MAX_BODY_BYTES = 64 * 1024   # 64KB

# Severity → Urgency mapping
SEVERITY_URGENCY_MAP = {
    logging.DEBUG: ("info", 0.1),
    logging.INFO: ("info", 0.2),
    logging.WARNING: ("warn", 0.4),
    logging.ERROR: ("error", 0.7),
    logging.CRITICAL: ("critical", 0.95),
}

# Global metrics
_dropped_logs_count = 0
_spool_writes_count = 0


def normalize_path_component(s: str) -> str:
    """Convert path to graph node ID component (replace / with _)."""
    return s.replace("/", "_").replace(".", "_")


def compute_stack_fingerprint(tb_lines: List[str], depth: int = STACK_FINGERPRINT_DEPTH) -> str:
    """
    Compute stable fingerprint from top N stack frames.
    Excludes line numbers and absolute paths for stability across deploys.
    """
    frames = []
    for line in tb_lines[:depth]:
        # Extract file basename and function name only
        # Skip line numbers (they change with code edits)
        match = re.search(r'File "([^"]+)", line \d+, in (.+)', line)
        if match:
            filepath, func = match.groups()
            filename = Path(filepath).name
            frames.append(f"{filename}::{func}")

    if not frames:
        return "unknown"

    fingerprint_str = "|".join(frames)
    return hashlib.sha1(fingerprint_str.encode()).hexdigest()[:12]


def compute_dedupe_key(script_name: str, error_type: str, message: str, stack_fp: str) -> str:
    """Compute dedupe key for collector-side deduplication."""
    normalized_msg = re.sub(r'\d+', 'N', message)  # Normalize numbers
    normalized_msg = re.sub(r'0x[0-9a-fA-F]+', '0xHEX', normalized_msg)  # Normalize hex addresses
    payload = f"{script_name}|{error_type}|{normalized_msg}|{stack_fp}"
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def redact_secrets(text: str) -> str:
    """
    Scrub tokens, API keys, credential-bearing URIs.
    Patterns: "token": "...", Authorization: Bearer ..., passwords, etc.
    """
    patterns = [
        (r'("token"\s*:\s*")[^"]+(")', r'\1<REDACTED>\2'),
        (r'("api_key"\s*:\s*")[^"]+(")', r'\1<REDACTED>\2'),
        (r'("password"\s*:\s*")[^"]+(")', r'\1<REDACTED>\2'),
        (r'(Authorization:\s*Bearer\s+)\S+', r'\1<REDACTED>'),
        (r'(https?://[^:@]+:[^@]+@)', r'\1<REDACTED>:<REDACTED>@'),
    ]
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def truncate_stack(stack_trace: str, max_lines: int = MAX_STACK_LINES, max_bytes: int = MAX_STACK_BYTES) -> str:
    """Truncate stack trace to first N lines or M bytes."""
    lines = stack_trace.split('\n')
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["...<truncated>"]

    truncated = '\n'.join(lines)
    if len(truncated.encode()) > max_bytes:
        # Byte-truncate with marker
        truncated = truncated.encode()[:max_bytes].decode('utf-8', errors='ignore') + "\n...<truncated>"

    return redact_secrets(truncated)


class L2LogHandler(logging.Handler):
    """
    Non-blocking log handler that sends ERROR/CRITICAL logs to signals_collector.

    Features:
    - Graph-aware attribution (citizen_id = code_substrate_...)
    - Non-blocking queue + background flusher
    - Client-side fingerprinting & redaction
    - Spill-to-disk on collector offline
    """

    def __init__(
        self,
        script_name: str,
        script_path: str,
        collector_url: str = COLLECTOR_URL,
        level: int = logging.ERROR
    ):
        super().__init__(level=level)
        self.script_name = script_name
        self.script_path = script_path
        self.collector_url = collector_url

        # Generate graph-aware citizen_id
        # Example: orchestration/scripts/resurrect_all_citizens.py
        #       → code_substrate_orchestration_scripts_resurrect_all_citizens_py
        path_component = normalize_path_component(script_path)
        self.citizen_id = f"code_substrate_{path_component}"

        # Non-blocking queue
        self.queue: deque = deque(maxlen=QUEUE_CAPACITY)
        self.queue_lock = threading.Lock()

        # Background flusher thread
        self.flusher_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flusher_thread.start()

        # Ensure spool directory exists
        SPOOL_DIR.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord):
        """Enqueue log record for background emission."""
        global _dropped_logs_count

        try:
            # Build envelope
            envelope = self._build_envelope(record)

            # Enqueue (non-blocking)
            with self.queue_lock:
                if len(self.queue) >= QUEUE_CAPACITY:
                    # Drop oldest
                    self.queue.popleft()
                    _dropped_logs_count += 1
                self.queue.append(envelope)

        except Exception:
            # Never let logging break the script
            self.handleError(record)

    def _build_envelope(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Build membrane.inject envelope from log record."""
        # Extract severity and urgency
        severity_str, urgency = SEVERITY_URGENCY_MAP.get(record.levelno, ("error", 0.7))

        # Extract stack trace if exception
        stack_trace = None
        stack_fingerprint = "no_stack"
        error_type = "LogError"

        if record.exc_info:
            error_type = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            stack_trace = ''.join(tb_module.format_exception(*record.exc_info))
            tb_lines = stack_trace.split('\n')
            stack_fingerprint = compute_stack_fingerprint(tb_lines)
            stack_trace = truncate_stack(stack_trace)

        # Compute dedupe key
        message = record.getMessage()
        dedupe_key = compute_dedupe_key(self.script_name, error_type, message, stack_fingerprint)

        # Build content
        content = f"{self.script_name}: {message}"
        if stack_trace:
            # Include first line of stack in content for visibility
            first_line = stack_trace.split('\n')[0] if stack_trace else ""
            content = f"{content} | {first_line}"

        # Build envelope
        timestamp_ms = int(time.time() * 1000)
        stimulus_id = f"script_log_{self.script_name}_{timestamp_ms}_{dedupe_key[:8]}"

        envelope = {
            "type": "membrane.inject",
            "citizen_id": self.citizen_id,
            "channel": f"signals.script.{self.script_name}",
            "content": redact_secrets(content[:500]),  # Truncate content
            "severity": severity_str,
            "features_raw": {
                "urgency": urgency,
                "novelty": 0.25,
                "trust": 0.9,  # High trust - it's our own code
            },
            "metadata": {
                "stimulus_id": stimulus_id,
                "origin": "script_logger",
                "timestamp_ms": timestamp_ms,
                "signal_type": "script_error",
                "dedupe_key": dedupe_key,
                "stack_fingerprint": stack_fingerprint,
                "script_name": self.script_name,
                "script_path": self.script_path,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "level": record.levelname,
                "error_type": error_type,
            }
        }

        # Add stack trace if present
        if stack_trace:
            envelope["metadata"]["stack_trace"] = stack_trace

        return envelope

    def _flush_loop(self):
        """Background thread: batch and send envelopes to collector."""
        global _spool_writes_count

        while True:
            try:
                # Wait for batch size or timeout
                time.sleep(BATCH_TIMEOUT_SEC)

                # Collect batch
                batch = []
                with self.queue_lock:
                    while len(batch) < BATCH_SIZE and len(self.queue) > 0:
                        batch.append(self.queue.popleft())

                if not batch:
                    continue

                # Send batch to collector
                success = self._send_batch(batch)

                # Spill to disk on failure
                if not success:
                    for envelope in batch:
                        self._spill_to_disk(envelope)
                        _spool_writes_count += 1

            except Exception as e:
                # Log to stderr, never break the flusher
                print(f"[L2Logger] Flusher error: {e}", file=__import__('sys').stderr)

    def _send_batch(self, batch: List[Dict]) -> bool:
        """Send batch of envelopes to collector."""
        try:
            # Send to /ingest endpoint (accepts full membrane.inject envelopes)
            for envelope in batch:
                resp = requests.post(
                    f"{self.collector_url}/ingest",
                    json=envelope,
                    timeout=2.0
                )
                if resp.status_code >= 500:
                    return False
            return True
        except Exception:
            return False

    def _spill_to_disk(self, envelope: Dict):
        """Write envelope to spool directory for out-of-band retry."""
        try:
            filename = f"{envelope['metadata']['stimulus_id']}.json"
            filepath = SPOOL_DIR / filename
            filepath.write_text(json.dumps(envelope, indent=2))
        except Exception as e:
            print(f"[L2Logger] Spill failed: {e}", file=__import__('sys').stderr)


def setup_l2_logger(
    script_name: str,
    script_path: str,
    level: int = logging.INFO,
    console_level: int = logging.INFO,
    l2_level: int = logging.ERROR
) -> logging.Logger:
    """
    Setup logger that logs to console AND sends errors to L2 graph.

    Args:
        script_name: Short script name (e.g., "resurrect_all_citizens")
        script_path: Relative path from project root (e.g., "orchestration/scripts/resurrect_all_citizens.py")
        level: Overall logger level
        console_level: Console handler level
        l2_level: L2 handler level (only ERROR+ sent to graph)

    Returns:
        Logger instance with both console and L2 handlers

    Example:
        logger = setup_l2_logger(
            script_name="resurrect_all_citizens",
            script_path="orchestration/scripts/resurrect_all_citizens.py"
        )
        logger.info("Starting resurrection...")  # Console only
        logger.error("Bootstrap failed")  # Console + L2 graph
    """
    logger = logging.getLogger(script_name)
    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to root

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(console_handler)

    # L2 handler (non-blocking, graph-aware)
    l2_handler = L2LogHandler(
        script_name=script_name,
        script_path=script_path,
        level=l2_level
    )
    logger.addHandler(l2_handler)

    return logger


def get_metrics() -> Dict[str, int]:
    """Get L2 logger metrics."""
    return {
        "dropped_logs": _dropped_logs_count,
        "spool_writes": _spool_writes_count,
    }
