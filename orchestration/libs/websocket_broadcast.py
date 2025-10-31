"""
WebSocket Broadcasting - Infrastructure for Consciousness State Streaming

ARCHITECTURAL PRINCIPLE: Infrastructure, NOT Consciousness Logic

This module handles real-time broadcasting of consciousness state to WebSocket clients.
It is PURE INFRASTRUCTURE - no consciousness logic, no mechanism implementation.

The consciousness engine doesn't know about WebSocket protocol details.
Can swap for HTTP/SSE/GraphQL subscriptions without changing consciousness logic.

Author: Felix (Engineer)
Created: 2025-10-19 (extracted from consciousness_engine.py)
Architecture: Phase 1 Clean Break - Infrastructure Layer
"""

import asyncio
import inspect
import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from orchestration.adapters.ws.stream_aggregator import get_stream_aggregator

logger = logging.getLogger(__name__)


class ConsciousnessStateBroadcaster:
    """
    Broadcasts consciousness state to WebSocket clients.

    PURE INFRASTRUCTURE - This class handles event streaming,
    it does NOT implement consciousness logic.

    The broadcaster is dependency-injected into the engine:
    - Engine produces state
    - Broadcaster streams state
    - Clean separation of concerns

    Example Usage:
        >>> broadcaster = ConsciousnessStateBroadcaster()
        >>> await broadcaster.broadcast_consciousness_state(
        ...     network_id="N1",
        ...     global_energy=0.7,
        ...     branching_ratio=1.0,
        ...     consciousness_state="critical"
        ... )
    """

    _external_listeners: List[Callable[[str, str, Dict[str, Any]], Any]] = []

    def __init__(self, websocket_manager: Optional[Any] = None, *, default_citizen_id: Optional[str] = None):
        """
        Initialize the broadcaster.

        Args:
            websocket_manager: WebSocket manager from control_api (optional)
                             If None, attempts to import automatically
            default_citizen_id: Citizen identifier to stamp on events when missing
        """
        self.websocket_manager = websocket_manager
        self.default_citizen_id = default_citizen_id

        if self.websocket_manager is None:
            # Attempt to import from control_api
            try:
                from orchestration.adapters.api.control_api import websocket_manager as wm
                self.websocket_manager = wm
                self.available = True
                logger.info("[ConsciousnessStateBroadcaster] WebSocket manager imported successfully")
            except ImportError:
                self.available = False
                logger.warning("[ConsciousnessStateBroadcaster] WebSocket manager not available - events will not be broadcast")
        else:
            self.available = True

        try:
            self._stream_aggregator = get_stream_aggregator()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("[ConsciousnessStateBroadcaster] Stream aggregator unavailable: %s", exc)
            self._stream_aggregator = None

        # Telemetry counters: track event counts since boot and in 60s window
        # Atlas implementation - War Room Plan P1
        self.event_counts_total = defaultdict(int)  # Total counts since boot
        self.event_timestamps = defaultdict(deque)  # Timestamps for 60s sliding window

    # ------------------------------------------------------------------ listener management

    @classmethod
    def register_listener(cls, listener: Callable[[str, str, Dict[str, Any]], Any]) -> None:
        """Register callback invoked for every broadcast event."""
        cls._external_listeners.append(listener)

    @classmethod
    def unregister_listener(cls, listener: Callable[[str, str, Dict[str, Any]], Any]) -> None:
        """Remove previously registered callback."""
        try:
            cls._external_listeners.remove(listener)
        except ValueError:
            pass

    def _notify_listeners(self, citizen_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Fire-and-forget notifications to external observers."""
        if not self._external_listeners:
            return

        for listener in list(self._external_listeners):
            try:
                result = listener(citizen_id, event_type, payload)
                if inspect.isawaitable(result):
                    asyncio.create_task(result)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("[ConsciousnessStateBroadcaster] Listener failed: %s", exc)

    async def broadcast_consciousness_state(
        self,
        network_id: str,
        global_energy: float,
        branching_ratio: float,
        raw_sigma: float,
        tick_interval_ms: float,
        tick_frequency_hz: float,
        consciousness_state: str,
        time_since_last_event: float,
        timestamp: datetime
    ):
        """
        Broadcast consciousness state to all connected WebSocket clients.

        This is ASYNC and NON-BLOCKING - uses create_task to fire-and-forget.
        The consciousness engine doesn't wait for broadcast completion.

        Args:
            network_id: Network identifier (N1, N2, N3)
            global_energy: Network-level energy (0.0-1.0)
            branching_ratio: Average σ over window
            raw_sigma: Current cycle's σ
            tick_interval_ms: Current tick interval
            tick_frequency_hz: Tick frequency in Hz
            consciousness_state: State name (alert/engaged/calm/drowsy/dormant)
            time_since_last_event: Seconds since last external event
            timestamp: When state was measured

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> await broadcaster.broadcast_consciousness_state(
            ...     network_id="N1",
            ...     global_energy=0.7,
            ...     branching_ratio=1.0,
            ...     raw_sigma=1.0,
            ...     tick_interval_ms=100,
            ...     tick_frequency_hz=10.0,
            ...     consciousness_state="alert",
            ...     time_since_last_event=5.0,
            ...     timestamp=datetime.now()
            ... )
        """
        if not self.available or not self.websocket_manager:
            # WebSocket not available - silently skip
            return

        try:
            # Create broadcast task without awaiting (fire-and-forget)
            # This prevents WebSocket delays from blocking consciousness heartbeat

            # Normative envelope format (Iris's Unified Event Vocabulary)
            # See: broadcast_event() for canonical implementation
            import hashlib
            import time as time_module

            citizen_id = self.default_citizen_id or "unknown"

            # Generate unique event ID
            event_id_base = f"consciousness_state_{citizen_id}_{int(time_module.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            # Build provenance envelope
            provenance = {
                "scope": "personal",
                "citizen_id": citizen_id
            }

            # Build normative envelope with payload structure
            event = {
                "type": "consciousness_state",  # Normative: "type" not "topic"
                "id": event_id,
                "spec": {
                    "name": "consciousness.v2",
                    "rev": "2.0.0"
                },
                "provenance": provenance,
                "payload": {
                    "network_id": network_id,
                    "global_energy": global_energy,
                    "branching_ratio": branching_ratio,
                    "raw_sigma": raw_sigma,
                    "tick_interval_ms": tick_interval_ms,
                    "tick_frequency_hz": tick_frequency_hz,
                    "consciousness_state": consciousness_state,
                    "time_since_last_event": time_since_last_event,
                    "timestamp": timestamp.isoformat()
                }
            }

            if self._stream_aggregator and citizen_id != "unknown":
                await self._stream_aggregator.ingest_event(
                    citizen_id,
                    event["type"],
                    event["payload"]
                )
            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] Broadcast failed: {e}")
            # Don't re-raise - infrastructure failure shouldn't kill consciousness

    async def broadcast_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ):
        """
        Broadcast generic event to WebSocket clients.

        Useful for broadcasting any consciousness-related event
        (node activations, link formations, etc.).

        Args:
            event_type: Type of event (e.g., "node_activated", "cluster_formed")
            data: Event data dict

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> await broadcaster.broadcast_event(
            ...     event_type="node_activated",
            ...     data={"node_id": "n1", "energy": 0.8}
            ... )
        """
        # Telemetry counters: track event counts (Atlas - War Room Plan P1)
        # This happens BEFORE availability check - we track even if no clients connected
        import time
        now = time.time()

        self.event_counts_total[event_type] += 1
        self.event_timestamps[event_type].append(now)

        # Clean old timestamps outside 60s window
        cutoff = now - 60.0
        while self.event_timestamps[event_type] and self.event_timestamps[event_type][0] < cutoff:
            self.event_timestamps[event_type].popleft()

        citizen_id = data.get("citizen_id", self.default_citizen_id)

        if self._stream_aggregator and citizen_id:
            try:
                await self._stream_aggregator.ingest_event(citizen_id, event_type, data)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("[ConsciousnessStateBroadcaster] Stream aggregator ingest failed: %s", exc)

        listener_citizen = citizen_id or ""
        self._notify_listeners(listener_citizen, event_type, data)

        if not self.available or not self.websocket_manager:
            return

        try:
            # Normative envelope format (Iris's Unified Event Vocabulary)
            # See: app/consciousness/hooks/useGraphStream.ts:185-205
            # Required fields: type, id, spec, provenance, payload
            import hashlib
            import time

            # Generate unique event ID
            event_id_base = f"{event_type}_{citizen_id or 'unknown'}_{int(time.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            # Determine scope from citizen_id vs org_id in data
            scope = "organizational" if data.get("org_id") else "personal"

            # Build provenance envelope
            provenance = {
                "scope": scope,
            }
            if scope == "personal":
                provenance["citizen_id"] = citizen_id or self.default_citizen_id or "unknown"
            else:
                provenance["org_id"] = data.get("org_id", "unknown")

            # Add optional provenance fields if present
            if "component" in data:
                provenance["component"] = data["component"]
            if "mission_id" in data:
                provenance["mission_id"] = data["mission_id"]

            # Build normative envelope
            event = {
                "type": event_type,  # Normative: "type" not "topic"
                "id": event_id,
                "spec": {
                    "name": "consciousness.v2",  # Spec namespace
                    "rev": "2.0.0"
                },
                "provenance": provenance,
                "payload": data  # Data goes in payload, not spread at root
            }

            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] Event broadcast failed: {e}")

    async def broadcast_energy_state(
        self,
        network_id: str,
        node_energy_distribution: Dict[str, float]
    ):
        """
        Broadcast node energy distribution snapshot.

        Useful for visualizing which nodes are currently active.

        Args:
            network_id: Network identifier
            node_energy_distribution: Dict mapping node_id to energy

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> await broadcaster.broadcast_energy_state(
            ...     network_id="N1",
            ...     node_energy_distribution={"n1": 0.8, "n2": 0.5}
            ... )
        """
        if not self.available or not self.websocket_manager:
            return

        try:
            # Normative envelope format (Iris's Unified Event Vocabulary)
            import hashlib
            import time as time_module

            citizen_id = self.default_citizen_id or "unknown"

            # Generate unique event ID
            event_id_base = f"energy_distribution_{citizen_id}_{int(time_module.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            # Build normative envelope
            event = {
                "type": "energy_distribution",  # Normative: "type" not "topic"
                "id": event_id,
                "spec": {
                    "name": "consciousness.v2",
                    "rev": "2.0.0"
                },
                "provenance": {
                    "scope": "personal",
                    "citizen_id": citizen_id
                },
                "payload": {
                    "network_id": network_id,
                    "nodes": node_energy_distribution,
                    "timestamp": datetime.now().isoformat(),
                    "node_count": len(node_energy_distribution)
                }
            }

            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] Energy state broadcast failed: {e}")

    def is_available(self) -> bool:
        """
        Check if WebSocket broadcasting is available WITH ACTIVE CLIENTS.

        ARCHITECTURAL FIX (2025-10-31): Prevent "tree falls in forest" problem.
        Engines should NOT broadcast if no clients are listening.

        Before: is_available() returned True if server exists (even with 0 clients)
        After: is_available() requires client_count() > 0

        This solves timing issue where engines initialize at 01:42 and broadcast
        to 0 clients, then frontend connects at 01:47 and receives 0 nodes.

        Returns:
            True if WebSocket manager is available AND has active clients

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> broadcaster.is_available()
            True  # Only if clients are connected
        """
        if not self.available or self.websocket_manager is None:
            return False

        # Only return True if there are active clients connected
        # This prevents "successful" broadcasts to audience of zero
        try:
            client_count = len(getattr(self.websocket_manager, '_connections', {}))
            return client_count > 0
        except Exception:
            # If we can't determine client count, assume unavailable
            return False

    def get_counter_stats(self) -> Dict[str, Any]:
        """
        Get telemetry counter statistics.

        Returns per-type event counts since boot and in 60s sliding window.
        Used by /api/telemetry/counters endpoint (Atlas - War Room Plan P1).

        Returns:
            {
                "event_type": {
                    "total": int,       # Total events since boot
                    "last_60s": int     # Events in last 60 seconds
                }
            }

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> stats = broadcaster.get_counter_stats()
            >>> stats["tick_frame_v1"]["total"]
            1523
            >>> stats["tick_frame_v1"]["last_60s"]
            57
        """
        import time
        now = time.time()
        cutoff = now - 60.0

        stats = {}
        for event_type, total_count in self.event_counts_total.items():
            # Clean stale timestamps for accurate 60s count
            while self.event_timestamps[event_type] and self.event_timestamps[event_type][0] < cutoff:
                self.event_timestamps[event_type].popleft()

            stats[event_type] = {
                "total": total_count,
                "last_60s": len(self.event_timestamps[event_type])
            }

        return stats

    def stride_exec(self, stride_data: Dict[str, Any]):
        """
        Broadcast stride execution event (synchronous wrapper for async broadcast).

        Called from diffusion_runtime during stride execution with full forensic trail.
        Uses fire-and-forget pattern to avoid blocking stride execution.

        Args:
            stride_data: Stride execution data including:
                - src_node, dst_node, link_id
                - Forensic trail: phi, ease, res_mult, comp_mult, total_cost, reason
                - Energy: delta_E, stickiness, retained_delta_E
                - chosen: True (this link was selected)

        Example:
            >>> broadcaster.stride_exec({
            ...     "src_node": "n1",
            ...     "dst_node": "n2",
            ...     "phi": 0.05,
            ...     "ease": 2.01,
            ...     "delta_E": 0.012,
            ...     "reason": "strong_link(ease=2.01) + goal_aligned(aff=0.95)"
            ... })
        """
        if not self.available or not self.websocket_manager:
            return

        try:
            # Normative envelope format (Iris's Unified Event Vocabulary)
            # See: broadcast_event() for canonical implementation
            import hashlib
            import time as time_module

            citizen_id = self.default_citizen_id or "unknown"

            # Generate unique event ID
            event_id_base = f"stride_exec_{citizen_id}_{int(time_module.time() * 1000)}"
            event_id = f"evt_{hashlib.sha256(event_id_base.encode()).hexdigest()[:16]}"

            # Build normative envelope
            event = {
                "type": "stride.exec",  # Normative: "type" not "topic"
                "id": event_id,
                "spec": {
                    "name": "consciousness.v2",
                    "rev": "2.0.0"
                },
                "provenance": {
                    "scope": "personal",  # N1 consciousness
                    "citizen_id": citizen_id
                },
                "payload": stride_data  # Data goes in payload, not spread at root
            }

            # Fire-and-forget: don't block stride execution
            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] stride.exec broadcast failed: {e}")
