"""
Telemetry infrastructure for Mind Protocol affective coupling.

Provides event emission with:
- Sampling (configurable rate to reduce overhead)
- Buffering (batch events before emission)
- Validation (ensure events match schemas)
- Feature flag control (enable/disable cleanly)

Author: Felix - 2025-10-23
PR-A: Instrumentation (Telemetry Foundation)
"""

import time
import random
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import asdict
import logging

from .settings import settings
from .events import (
    BaseEvent,
    EventType,
    create_event,
    # Affective coupling events
    AffectiveThresholdEvent,
    AffectiveMemoryEvent,
    CoherencePersistenceEvent,
    MultiPatternResponseEvent,
    IdentityMultiplicityEvent,
    ConsolidationEvent,
    DecayResistanceEvent,
    StickinessEvent,
    AffectivePrimingEvent,
    CoherenceMetricEvent,
    CriticalityModeEvent,
)

logger = logging.getLogger(__name__)


class TelemetryBuffer:
    """
    Buffer for high-frequency events with automatic flushing.

    Provides:
    - Size-based flushing (when buffer reaches max size)
    - Time-based flushing (when interval elapsed)
    - Manual flushing (on demand)
    """

    def __init__(
        self,
        max_size: int = 1000,
        flush_interval_s: float = 5.0,
        flush_callback=None
    ):
        """
        Initialize telemetry buffer.

        Args:
            max_size: Maximum events before auto-flush
            flush_interval_s: Seconds between auto-flushes
            flush_callback: Function to call on flush (receives list of events)
        """
        self.max_size = max_size
        self.flush_interval_s = flush_interval_s
        self.flush_callback = flush_callback

        self.buffer: deque = deque(maxlen=max_size)
        self.last_flush_time = time.time()

        # Statistics
        self.total_events_received = 0
        self.total_events_flushed = 0
        self.flush_count = 0

    def add(self, event: BaseEvent):
        """
        Add event to buffer.

        May trigger auto-flush if conditions met.

        Args:
            event: Event to buffer
        """
        self.buffer.append(event)
        self.total_events_received += 1

        # Check flush conditions
        if len(self.buffer) >= self.max_size:
            self.flush(reason="size_limit")
        elif time.time() - self.last_flush_time >= self.flush_interval_s:
            self.flush(reason="time_limit")

    def flush(self, reason: str = "manual"):
        """
        Flush buffered events.

        Args:
            reason: Why flush triggered (size_limit/time_limit/manual)
        """
        if not self.buffer:
            return

        events_to_flush = list(self.buffer)
        self.buffer.clear()

        # Emit events
        if self.flush_callback:
            try:
                self.flush_callback(events_to_flush)
            except Exception as e:
                logger.error(f"[Telemetry] Flush callback error: {e}")

        # Update stats
        self.total_events_flushed += len(events_to_flush)
        self.flush_count += 1
        self.last_flush_time = time.time()

        logger.debug(
            f"[Telemetry] Flushed {len(events_to_flush)} events (reason={reason})"
        )

    def get_stats(self) -> dict:
        """Get buffer statistics."""
        return {
            "total_events_received": self.total_events_received,
            "total_events_flushed": self.total_events_flushed,
            "flush_count": self.flush_count,
            "current_buffer_size": len(self.buffer),
            "max_buffer_size": self.max_size,
        }


class TelemetryEmitter:
    """
    Main telemetry emission system.

    Features:
    - Feature flag control (respects AFFECTIVE_TELEMETRY_ENABLED)
    - Sampling (reduces overhead for high-frequency events)
    - Buffering (batches events before emission)
    - Validation (ensures events match schemas)
    """

    def __init__(self):
        """Initialize telemetry emitter."""
        self.enabled = settings.AFFECTIVE_TELEMETRY_ENABLED
        self.sample_rate = settings.TELEMETRY_SAMPLE_RATE

        # Buffer with callback (currently just logs, will connect to websocket later)
        self.buffer = TelemetryBuffer(
            max_size=settings.TELEMETRY_BUFFER_SIZE,
            flush_interval_s=settings.TELEMETRY_FLUSH_INTERVAL_S,
            flush_callback=self._emit_batch
        )

        # Statistics
        self.event_counts: Dict[EventType, int] = {}
        self.sampled_out_count = 0

        logger.info(
            f"[Telemetry] Initialized "
            f"(enabled={self.enabled}, sample_rate={self.sample_rate})"
        )

    def emit_affective_event(
        self,
        event_type: EventType,
        citizen_id: str = "unknown",
        frame_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Emit an affective coupling event.

        Args:
            event_type: Type of event
            citizen_id: Citizen generating event
            frame_id: Current frame ID
            **kwargs: Event-specific fields

        Returns:
            True if event was emitted (or buffered), False if skipped
        """
        # Feature flag check
        if not self.enabled:
            return False

        # Sampling check
        if self.sample_rate < 1.0:
            if random.random() > self.sample_rate:
                self.sampled_out_count += 1
                return False

        # Create event
        try:
            event = create_event(
                event_type=event_type,
                citizen_id=citizen_id,
                frame_id=frame_id,
                **kwargs
            )
        except Exception as e:
            logger.error(f"[Telemetry] Event creation error ({event_type}): {e}")
            return False

        # Validate event
        if not self._validate_event(event):
            logger.warning(f"[Telemetry] Event validation failed: {event_type}")
            return False

        # Buffer event
        self.buffer.add(event)

        # Update counts
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1

        return True

    def _validate_event(self, event: BaseEvent) -> bool:
        """
        Validate event matches expected schema.

        Args:
            event: Event to validate

        Returns:
            True if valid
        """
        try:
            # Check required fields exist
            if not event.event_type:
                return False
            if not event.timestamp:
                return False

            # Convert to dict (will raise if invalid)
            event_dict = event.to_dict()

            # Check dict is not empty
            if not event_dict:
                return False

            return True
        except Exception as e:
            logger.error(f"[Telemetry] Validation error: {e}")
            return False

    def _emit_batch(self, events: List[BaseEvent]):
        """
        Emit a batch of events.

        Routes events to affective telemetry buffer for API consumption.

        Args:
            events: Events to emit
        """
        # Import here to avoid circular dependency
        from orchestration.mechanisms.affective_telemetry_buffer import get_affective_buffer

        buffer = get_affective_buffer()

        # Route each event to buffer
        for event in events:
            try:
                event_dict = event.to_dict()
                event_type = event_dict.get("event_type", "unknown")

                # Convert event_type format from "affective_threshold" to "affective.threshold"
                event_type_dotted = event_type.replace("_", ".", 1)

                # Add to buffer (will add timestamp automatically if not present)
                buffer.add_event(event_type_dotted, event_dict)

            except Exception as e:
                logger.error(f"[Telemetry] Failed to route event to buffer: {e}")

        logger.debug(
            f"[Telemetry] Routed {len(events)} events to affective buffer "
            f"(types: {[e.event_type for e in events[:5]]}...)"
        )

    def flush(self):
        """Manually flush buffered events."""
        self.buffer.flush(reason="manual")

    def get_stats(self) -> dict:
        """Get emitter statistics."""
        buffer_stats = self.buffer.get_stats()

        return {
            "enabled": self.enabled,
            "sample_rate": self.sample_rate,
            "event_counts_by_type": self.event_counts,
            "sampled_out_count": self.sampled_out_count,
            "buffer": buffer_stats,
        }


# Singleton instance
_emitter: Optional[TelemetryEmitter] = None


def get_emitter() -> TelemetryEmitter:
    """Get or create singleton telemetry emitter."""
    global _emitter
    if _emitter is None:
        _emitter = TelemetryEmitter()
    return _emitter


# === Convenience Functions ===

def emit_affective_threshold(
    citizen_id: str,
    frame_id: str,
    node_id: str,
    theta_base: float,
    theta_adjusted: float,
    h: float,
    affective_alignment: float,
    emotion_magnitude: float
):
    """Emit affective threshold event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "affective_threshold",
        citizen_id=citizen_id,
        frame_id=frame_id,
        node_id=node_id,
        theta_base=theta_base,
        theta_adjusted=theta_adjusted,
        h=h,
        affective_alignment=affective_alignment,
        emotion_magnitude=emotion_magnitude
    )


def emit_affective_memory(
    citizen_id: str,
    frame_id: str,
    node_id: str,
    m_affect: float,
    emotion_magnitude: float,
    delta_log_w_base: float,
    delta_log_w_amplified: float
):
    """Emit affective memory event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "affective_memory",
        citizen_id=citizen_id,
        frame_id=frame_id,
        node_id=node_id,
        m_affect=m_affect,
        emotion_magnitude=emotion_magnitude,
        delta_log_w_base=delta_log_w_base,
        delta_log_w_amplified=delta_log_w_amplified
    )


def emit_coherence_persistence(
    citizen_id: str,
    frame_id: str,
    entity_id: str,
    coherence_persistence: int,
    lambda_res_effective: float,
    lock_in_risk: bool
):
    """Emit coherence persistence event (PR-B)."""
    emitter = get_emitter()
    return emitter.emit_affective_event(
        "coherence_persistence",
        citizen_id=citizen_id,
        frame_id=frame_id,
        entity_id=entity_id,
        coherence_persistence=coherence_persistence,
        lambda_res_effective=lambda_res_effective,
        lock_in_risk=lock_in_risk
    )


# Additional convenience functions for other event types would go here
# (PR-C, PR-D, PR-E events)


def flush_telemetry():
    """Manually flush all buffered telemetry events."""
    emitter = get_emitter()
    emitter.flush()


def get_telemetry_stats() -> dict:
    """Get telemetry system statistics."""
    emitter = get_emitter()
    return emitter.get_stats()
