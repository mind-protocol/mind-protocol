"""
Membrane Stimuli SDK - Pure Membrane Emission

Enables any component (scripts, services, UI) to inject stimuli into the
consciousness substrate via the membrane bus.

Architecture:
- Level-invariant: Use scope (personal/organizational/ecosystem), not citizen_id
- Topology-agnostic: No routing decisions, engines self-select via physics
- Non-blocking: Queue + background flusher, never blocks main work
- Pure membrane: WS publish to bus, no REST endpoints

Physics happens engine-side:
- Stimulus integrator applies mass, refractory, trust/utility learning
- Cross-level membrane applies fit × κ (learned permeability)
- No component→citizen routing in client code

Created: 2025-10-29 by Ada (Architect)
Spec: membrane_systems_map.md (Component D: Signals → Stimuli Bridge)
"""

import asyncio
import hashlib
import json
import logging
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

try:
    from websockets.sync.client import connect as ws_connect
except ImportError:
    ws_connect = None

from orchestration.schemas.membrane_envelopes import (
    Scope,
    OriginType,
    StimulusEnvelope,
    StimulusFeatures,
    StimulusMetadata,
)

# Configuration
WS_ENDPOINT = "ws://127.0.0.1:8000/api/ws"
QUEUE_CAPACITY = 1000
BATCH_SIZE = 25
BATCH_TIMEOUT_SEC = 0.25
SPOOL_DIR = Path("/tmp/membrane-stimuli-spool")
STACK_FINGERPRINT_DEPTH = 5
MAX_STACK_LINES = 60
MAX_STACK_BYTES = 16 * 1024  # 16KB

# Global metrics
_dropped_count = 0
_spool_writes_count = 0

logger = logging.getLogger(__name__)


def compute_stack_fingerprint(tb_lines: List[str], depth: int = STACK_FINGERPRINT_DEPTH) -> str:
    """
    Compute stable fingerprint from top N stack frames.
    Excludes line numbers and absolute paths for stability across deploys.
    """
    frames = []
    for line in tb_lines[:depth]:
        # Extract file basename and function name only
        match = re.search(r'File "([^"]+)", line \d+, in (.+)', line)
        if match:
            filepath, func = match.groups()
            filename = Path(filepath).name
            frames.append(f"{filename}::{func}")

    if not frames:
        return "unknown"

    fingerprint_str = "|".join(frames)
    return hashlib.sha1(fingerprint_str.encode()).hexdigest()[:12]


def compute_dedupe_key(source: str, content: str, stack_fp: str = "no_stack") -> str:
    """Compute dedupe key for integrator-side deduplication."""
    # Normalize numbers and hex addresses
    normalized = re.sub(r'\d+', 'N', content)
    normalized = re.sub(r'0x[0-9a-fA-F]+', '0xHEX', normalized)
    payload = f"{source}|{normalized}|{stack_fp}"
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def redact_secrets(text: str) -> str:
    """
    Scrub tokens, API keys, credential-bearing URIs.
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
        truncated = truncated.encode()[:max_bytes].decode('utf-8', errors='ignore') + "\n...<truncated>"

    return redact_secrets(truncated)


class MembraneEmitter:
    """
    Non-blocking stimulus emitter to membrane bus.

    Features:
    - Level-invariant (scope, not citizen_id)
    - Non-blocking (queue + background flusher)
    - Client-side quality (fingerprinting, redaction)
    - Resilient (spill-to-disk on offline)
    """

    def __init__(
        self,
        source_id: str,
        ws_endpoint: str = WS_ENDPOINT,
    ):
        """
        Initialize emitter.

        Args:
            source_id: Identity for trust/mass tracking (e.g., "script:resurrect_all_citizens")
            ws_endpoint: WebSocket bus endpoint
        """
        self.source_id = source_id
        self.ws_endpoint = ws_endpoint

        # Non-blocking queue
        self.queue: Deque[Dict] = deque(maxlen=QUEUE_CAPACITY)
        self.queue_lock = threading.Lock()

        # Background flusher thread
        self.flusher_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flusher_thread.start()

        # Ensure spool directory exists
        SPOOL_DIR.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        *,
        scope: Scope,
        channel: str,
        content: str,
        features: StimulusFeatures,
        origin: OriginType = OriginType.EXTERNAL,
        provenance: Optional[Dict[str, Any]] = None,
        target_nodes: Optional[List[str]] = None,
    ) -> bool:
        """
        Emit stimulus to membrane bus.

        Args:
            scope: Which level (personal/organizational/ecosystem)
            channel: Logical channel (e.g., "signals.script.error")
            content: Human-readable description
            features: Extracted features (novelty, trust, urgency, etc.)
            origin: Where stimulus came from
            provenance: Additional context (source identity, paths, etc.)
            target_nodes: Specific nodes to target (optional)

        Returns:
            True if enqueued successfully, False if queue full
        """
        global _dropped_count

        # Build envelope
        try:
            envelope = self._build_envelope(
                scope=scope,
                channel=channel,
                content=content,
                features=features,
                origin=origin,
                provenance=provenance or {},
                target_nodes=target_nodes,
            )

            # Enqueue (non-blocking)
            with self.queue_lock:
                if len(self.queue) >= QUEUE_CAPACITY:
                    # Drop oldest
                    self.queue.popleft()
                    _dropped_count += 1
                self.queue.append(envelope)

            return True

        except Exception as e:
            logger.error(f"[MembraneEmitter] Failed to enqueue: {e}")
            return False

    def _build_envelope(
        self,
        scope: Scope,
        channel: str,
        content: str,
        features: StimulusFeatures,
        origin: OriginType,
        provenance: Dict[str, Any],
        target_nodes: Optional[List[str]],
    ) -> Dict:
        """Build stimulus envelope from components."""

        # Ensure source_id in provenance for trust/mass tracking
        provenance.setdefault("source", self.source_id)

        # Compute dedupe key
        stack_fp = provenance.get("stack_fingerprint", "no_stack")
        dedupe_key = compute_dedupe_key(self.source_id, content, stack_fp)

        # Build metadata
        metadata = StimulusMetadata(
            origin=origin,
            origin_chain_depth=0,
            ttl_frames=600,
            dedupe_key=dedupe_key,
            timestamp=datetime.utcnow(),
        )

        # Build envelope
        envelope = StimulusEnvelope(
            scope=scope,
            channel=channel,
            content=redact_secrets(content[:500]),  # Truncate content
            features_raw=features,
            metadata=metadata,
            target_nodes=target_nodes,
            provenance=provenance,
        )

        return envelope.dict()

    def _flush_loop(self):
        """Background thread: batch and send envelopes to membrane bus."""
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

                # Send batch to membrane bus
                success = self._send_batch(batch)

                # Spill to disk on failure
                if not success:
                    for envelope in batch:
                        self._spill_to_disk(envelope)
                        _spool_writes_count += 1

            except Exception as e:
                logger.error(f"[MembraneEmitter] Flusher error: {e}")

    def _send_batch(self, batch: List[Dict]) -> bool:
        """Send batch of envelopes to membrane bus."""
        if ws_connect is None:
            logger.error("[MembraneEmitter] websockets package unavailable")
            return False

        try:
            # Connect and send
            with ws_connect(self.ws_endpoint, open_timeout=2, close_timeout=1) as ws:
                for envelope in batch:
                    ws.send(json.dumps(envelope))
            return True

        except Exception as e:
            logger.warning(f"[MembraneEmitter] WS publish failed: {e}")
            return False

    def _spill_to_disk(self, envelope: Dict):
        """Write envelope to spool directory for out-of-band retry."""
        try:
            timestamp = int(time.time() * 1000)
            dedupe_key = envelope.get("metadata", {}).get("dedupe_key", "unknown")
            filename = f"stimulus_{timestamp}_{dedupe_key}.json"
            filepath = SPOOL_DIR / filename
            filepath.write_text(json.dumps(envelope, indent=2))
        except Exception as e:
            logger.error(f"[MembraneEmitter] Spill failed: {e}")


# ============================================================================
# Typed Emitters - High-Level API
# ============================================================================

def emit_script_error(
    source: str,
    error_message: str,
    scope: Scope = Scope.ORGANIZATIONAL,
    exc_info: Optional[tuple] = None,
    metadata: Optional[Dict] = None,
) -> bool:
    """
    Emit script error stimulus.

    Args:
        source: Script identity (e.g., "script:resurrect_all_citizens")
        error_message: Error description
        scope: Which level (default: organizational)
        exc_info: Exception info tuple from sys.exc_info()
        metadata: Additional metadata (script_path, etc.)

    Returns:
        True if emitted successfully

    Example:
        try:
            do_work()
        except Exception:
            emit_script_error(
                source="script:my_script",
                error_message="Bootstrap failed",
                exc_info=sys.exc_info()
            )
    """
    emitter = MembraneEmitter(source_id=source)

    # Extract stack if exception provided
    stack_trace = None
    stack_fp = "no_stack"
    error_type = "Error"

    if exc_info:
        import traceback
        error_type = exc_info[0].__name__ if exc_info[0] else "Exception"
        stack_trace = ''.join(traceback.format_exception(*exc_info))
        tb_lines = stack_trace.split('\n')
        stack_fp = compute_stack_fingerprint(tb_lines)
        stack_trace = truncate_stack(stack_trace)

    # Build content
    content = f"{source}: {error_message}"
    if stack_trace:
        first_line = stack_trace.split('\n')[0] if stack_trace else ""
        content = f"{content} | {first_line}"

    # Build features
    features = StimulusFeatures(
        novelty=0.7,  # Errors are usually novel
        uncertainty=0.3,  # Errors are concrete
        trust=0.9,  # High trust - it's our own code
        urgency=0.7,  # Errors need attention
        valence=-0.5,  # Negative (problem)
        scale=0.6,  # Moderate scale
        intensity=1.0,
    )

    # Build provenance
    provenance = {
        "source": source,
        "error_type": error_type,
        "stack_fingerprint": stack_fp,
    }
    if stack_trace:
        provenance["stack_trace"] = stack_trace
    if metadata:
        provenance.update(metadata)

    return emitter.emit(
        scope=scope,
        channel="signals.script.error",
        content=content,
        features=features,
        origin=OriginType.EXTERNAL,
        provenance=provenance,
    )


def emit_metric(
    source: str,
    metric_name: str,
    value: float,
    scope: Scope = Scope.ORGANIZATIONAL,
    tags: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Emit metric stimulus.

    Args:
        source: Metric source (e.g., "service:queue_poller")
        metric_name: Metric name
        value: Metric value
        scope: Which level (default: organizational)
        tags: Additional tags

    Returns:
        True if emitted successfully

    Example:
        emit_metric(
            source="script:resurrect_all_citizens",
            metric_name="resurrection_success_rate",
            value=0.95,
            tags={"environment": "production"}
        )
    """
    emitter = MembraneEmitter(source_id=source)

    content = f"{metric_name}: {value}"
    if tags:
        tags_str = ", ".join(f"{k}={v}" for k, v in tags.items())
        content = f"{content} ({tags_str})"

    features = StimulusFeatures(
        novelty=0.3,  # Metrics are routine
        uncertainty=0.1,  # Metrics are precise
        trust=0.95,  # High trust
        urgency=0.3,  # Low urgency
        valence=0.0,  # Neutral
        scale=0.5,  # Moderate scale
        intensity=0.8,
    )

    provenance = {
        "source": source,
        "metric_name": metric_name,
        "value": value,
    }
    if tags:
        provenance["tags"] = tags

    return emitter.emit(
        scope=scope,
        channel="signals.metric",
        content=content,
        features=features,
        origin=OriginType.EXTERNAL,
        provenance=provenance,
    )


def emit_ui_action(
    action_type: str,
    description: str,
    scope: Scope = Scope.PERSONAL,
    citizen_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> bool:
    """
    Emit UI action stimulus.

    Args:
        action_type: Action type (e.g., "select_nodes", "focus_entity")
        description: Human-readable description
        scope: Which level (default: personal)
        citizen_id: Optional citizen for personal scope
        metadata: Additional metadata (selected_nodes, etc.)

    Returns:
        True if emitted successfully

    Example:
        emit_ui_action(
            action_type="select_nodes",
            description="User selected nodes N7, N23",
            scope=Scope.PERSONAL,
            citizen_id="ada",
            metadata={"selected_nodes": ["N7", "N23"]}
        )
    """
    source = f"ui:{action_type}"
    emitter = MembraneEmitter(source_id=source)

    features = StimulusFeatures(
        novelty=0.5,  # UI actions vary
        uncertainty=0.2,  # User intent clear
        trust=0.85,  # Generally trusted
        urgency=0.6,  # Moderate urgency
        valence=0.3,  # Slightly positive (engagement)
        scale=0.7,  # Significant
        intensity=1.0,
    )

    provenance = {
        "source": source,
        "action_type": action_type,
    }
    if citizen_id:
        provenance["citizen_id"] = citizen_id
    if metadata:
        provenance.update(metadata)

    return emitter.emit(
        scope=scope,
        channel=f"ui.action.{action_type}",
        content=description,
        features=features,
        origin=OriginType.UI,
        provenance=provenance,
    )


def emit_tool_result(
    tool_id: str,
    request_id: str,
    success: bool,
    result: Optional[Any] = None,
    error: Optional[str] = None,
    scope: Scope = Scope.PERSONAL,
    citizen_id: Optional[str] = None,
    execution_time_ms: float = 0.0,
    provenance: Optional[Dict] = None,
) -> bool:
    """
    Emit tool result stimulus.

    Args:
        tool_id: Tool identifier
        request_id: Request identifier
        success: Whether execution succeeded
        result: Tool result (if success)
        error: Error message (if failure)
        scope: Which level
        citizen_id: Optional citizen
        execution_time_ms: Execution time in milliseconds
        provenance: Additional provenance (files, URLs, etc.)

    Returns:
        True if emitted successfully

    Example:
        emit_tool_result(
            tool_id="code_search",
            request_id="req_123",
            success=True,
            result={"matches": [...]},
            scope=Scope.PERSONAL,
            citizen_id="ada",
            execution_time_ms=125.5
        )
    """
    source = f"tool:{tool_id}"
    emitter = MembraneEmitter(source_id=source)

    if success:
        content = f"Tool {tool_id} completed successfully ({execution_time_ms:.1f}ms)"
        valence = 0.6
    else:
        content = f"Tool {tool_id} failed: {error}"
        valence = -0.4

    features = StimulusFeatures(
        novelty=0.4,  # Tool results vary
        uncertainty=0.1 if success else 0.4,
        trust=0.8,  # Tool trust
        urgency=0.5,  # Moderate urgency
        valence=valence,
        scale=0.6,
        intensity=1.0,
    )

    prov = {
        "source": source,
        "tool_id": tool_id,
        "request_id": request_id,
        "success": success,
        "execution_time_ms": execution_time_ms,
    }
    if result is not None:
        prov["result"] = result
    if error:
        prov["error"] = error
    if citizen_id:
        prov["citizen_id"] = citizen_id
    if provenance:
        prov.update(provenance)

    return emitter.emit(
        scope=scope,
        channel="tool.result",
        content=content,
        features=features,
        origin=OriginType.TOOL,
        provenance=prov,
    )


def get_metrics() -> Dict[str, int]:
    """Get emitter metrics."""
    return {
        "dropped_count": _dropped_count,
        "spool_writes": _spool_writes_count,
    }
