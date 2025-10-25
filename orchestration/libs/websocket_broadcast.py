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

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict, deque

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

    def __init__(self, websocket_manager: Optional[Any] = None):
        """
        Initialize the broadcaster.

        Args:
            websocket_manager: WebSocket manager from control_api (optional)
                             If None, attempts to import automatically
        """
        self.websocket_manager = websocket_manager

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

        # Telemetry counters: track event counts since boot and in 60s window
        # Atlas implementation - War Room Plan P1
        self.event_counts_total = defaultdict(int)  # Total counts since boot
        self.event_timestamps = defaultdict(deque)  # Timestamps for 60s sliding window

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
            asyncio.create_task(self.websocket_manager.broadcast({
                "type": "consciousness_state",
                "network_id": network_id,
                "global_energy": global_energy,
                "branching_ratio": branching_ratio,
                "raw_sigma": raw_sigma,
                "tick_interval_ms": tick_interval_ms,
                "tick_frequency_hz": tick_frequency_hz,
                "consciousness_state": consciousness_state,
                "time_since_last_event": time_since_last_event,
                "timestamp": timestamp.isoformat()
            }))

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

        if not self.available or not self.websocket_manager:
            return

        try:
            event = {
                "type": event_type,
                "timestamp": datetime.now().isoformat(),
                **data
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
            event = {
                "type": "energy_distribution",
                "network_id": network_id,
                "nodes": node_energy_distribution,
                "timestamp": datetime.now().isoformat(),
                "node_count": len(node_energy_distribution)
            }

            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] Energy state broadcast failed: {e}")

    def is_available(self) -> bool:
        """
        Check if WebSocket broadcasting is available.

        Returns:
            True if WebSocket manager is available, False otherwise

        Example:
            >>> broadcaster = ConsciousnessStateBroadcaster()
            >>> broadcaster.is_available()
            True
        """
        return self.available and self.websocket_manager is not None

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
            event = {
                "type": "stride.exec",
                "timestamp": datetime.now().isoformat(),
                **stride_data
            }

            # Fire-and-forget: don't block stride execution
            asyncio.create_task(self.websocket_manager.broadcast(event))

        except Exception as e:
            logger.error(f"[ConsciousnessStateBroadcaster] stride.exec broadcast failed: {e}")
