"""
Telemetry Bus - Decimated Event Streaming for Dashboard Observability

ARCHITECTURAL PRINCIPLE: Infrastructure Bridge Between Engine + Dashboard

The consciousness engine emits events every tick (~100 Hz for some citizens).
The dashboard needs manageable updates (~10 Hz) without blocking the engine.

TelemetryBus provides:
- Non-blocking append() for engine (no awaits in tick path)
- Batched flush at 10 Hz via WebSocket
- Ring buffer with backpressure (drop oldest when full)
- Memory safety (capped batch size)

Author: Atlas (Infrastructure)
Spec: Nicolas (Mind Protocol)
Created: 2025-10-25
Purpose: Make consciousness processing observable without degrading performance
"""

from collections import deque
import time
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TelemetryBus:
    """
    Batched telemetry event bus with decimation to 10 Hz.

    Engines append events (non-blocking), bus flushes batches
    at manageable rate to prevent overwhelming WebSocket clients.

    Example Usage:
        >>> bus = TelemetryBus(broadcaster=my_broadcaster, fps=10)
        >>> bus.append({"type": "node.flip", "id": "n1", "E_post": 0.8})
        >>> await bus.flush_if_due()  # Sends batch if 100ms elapsed
    """

    def __init__(
        self,
        broadcaster: Optional[Any] = None,
        fps: int = 10,
        max_items: int = 2000
    ):
        """
        Initialize telemetry bus.

        Args:
            broadcaster: ConsciousnessStateBroadcaster instance
            fps: Flush frequency in Hz (default: 10 Hz = 100ms period)
            max_items: Ring buffer capacity (default: 2000 events)
        """
        self.buf = deque(maxlen=max_items)
        self.last_flush = 0.0
        self.period = 1.0 / fps  # 10 Hz = 0.1s period
        self.broadcaster = broadcaster
        self.fps = fps
        self.max_items = max_items

        # Stats for monitoring
        self.total_appended = 0
        self.total_flushed = 0
        self.last_flush_size = 0

        logger.info(f"[TelemetryBus] Initialized: {fps} Hz flush, {max_items} event capacity")

    def append(self, event: Dict[str, Any]):
        """
        Append event to buffer (ultra cheap, no awaits).

        Called from consciousness tick path - must be non-blocking.
        If buffer full, oldest events drop (ring buffer behavior).

        Args:
            event: Event dict with 'type' and event-specific data
        """
        self.buf.append(event)
        self.total_appended += 1

    async def flush_if_due(self):
        """
        Flush batch if period elapsed (10 Hz decimation).

        Broadcasts all buffered events as individual events
        (frontend normalizer handles both individual and batched).

        Called at frame end - only awaits if flush is due.
        """
        now = time.time()
        if now - self.last_flush < self.period:
            return  # Not due yet, skip

        # Capture batch and clear buffer
        batch = list(self.buf)
        self.buf.clear()

        if not batch:
            self.last_flush = now
            return  # Nothing to flush

        if not self.broadcaster or not self.broadcaster.is_available():
            # No broadcaster available - drop events
            logger.debug(f"[TelemetryBus] Dropping {len(batch)} events (no broadcaster)")
            self.last_flush = now
            return

        # Broadcast each event individually (frontend expects this)
        try:
            for event in batch:
                event_type = event.get("type", "unknown")
                await self.broadcaster.broadcast_event(event_type, event)

            self.total_flushed += len(batch)
            self.last_flush_size = len(batch)
            logger.debug(f"[TelemetryBus] Flushed {len(batch)} events ({self.total_flushed} total)")

        except Exception as e:
            logger.error(f"[TelemetryBus] Flush failed: {e}")

        self.last_flush = now

    def get_stats(self) -> Dict[str, Any]:
        """
        Get telemetry bus statistics.

        Returns:
            Dict with appended count, flushed count, buffer size, etc.
        """
        return {
            "fps": self.fps,
            "max_items": self.max_items,
            "current_buffer_size": len(self.buf),
            "total_appended": self.total_appended,
            "total_flushed": self.total_flushed,
            "last_flush_size": self.last_flush_size,
            "time_since_last_flush": time.time() - self.last_flush
        }
