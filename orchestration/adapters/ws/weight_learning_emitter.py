"""
Weight Learning Event Emitter - Priority 4 Entity-Context Trace Observability

Emits weight update events for dual-view learning visualization:
- weights.updated.trace: TRACE-driven weight updates with entity attribution
- weights.updated.traversal: Traversal-driven weight updates (future Priority 5)

This enables EntityContextLearningPanel to show:
- Global vs entity-local learning split (80/20)
- Membership-weighted overlay updates
- Entity attribution for all weight changes

Author: Iris "The Aperture" (Visualization Specialist)
Created: 2025-10-25
Spec: docs/specs/v2/learning_and_trace/ENTITY_CONTEXT_TRACE_DESIGN.md
Integration Point: WeightLearnerV2.update_node_weights()
"""

from typing import Any, List, Optional, Protocol, Dict


class Transport(Protocol):
    """
    Transport protocol for event emission.

    Injected by WS service - can be WebSocket broadcaster, logger, queue, etc.
    """
    def emit(self, event_type: str, payload: Any) -> None:
        """Emit event with payload to connected clients."""
        ...


class WeightLearningEmitter:
    """
    Emits weight learning events for Priority 4 observability.

    Events emitted:
    - weights.updated.trace: Batch of TRACE-driven weight updates with entity attribution
    - weights.updated.traversal: Batch of traversal-driven weight updates (future)

    Example:
        >>> transport = WebSocketTransport()
        >>> emitter = WeightLearningEmitter(transport)
        >>> emitter.trace_weight_updates(
        ...     updates=[...],
        ...     frame_id=123,
        ...     entity_context=["entity_translator"],
        ...     cohort="Realization@personal",
        ...     global_context=True
        ... )
    """

    def __init__(self, transport: Transport):
        """
        Initialize emitter with transport.

        Args:
            transport: Transport implementation (WebSocket, logger, etc.)
        """
        self._transport = transport

    def trace_weight_updates(
        self,
        updates: List[Dict[str, Any]],
        frame_id: int,
        scope: str,
        cohort: str,
        entity_contexts: List[str],
        global_context: bool
    ) -> None:
        """
        Emit TRACE-driven weight update batch.

        Called after WeightLearnerV2.update_node_weights() completes.
        Shows dual-view learning with entity attribution.

        Args:
            updates: List of WeightUpdate objects (as dicts)
            frame_id: Current frame ID
            scope: Update scope ('link' | 'node' | 'membership')
            cohort: Cohort identifier (e.g., "Realization@personal")
            entity_contexts: Active entity IDs during this TRACE
            global_context: Whether global weight was updated

        Event payload format (matches websocket-types.ts WeightsUpdatedTraceEvent):
            {
                "type": "weights.updated.trace",
                "frame_id": 123,
                "scope": "node",
                "cohort": "Realization@personal",
                "entity_contexts": ["entity_translator", "entity_architect"],
                "global_context": true,
                "n": 15,
                "d_mu": 0.023,
                "d_sigma": 0.18,
                "timestamp": "2025-10-25T04:30:15.123Z",
                "updates": [
                    {
                        "item_id": "node_realization_123",
                        "delta_global": 0.12,
                        "log_weight_new": 1.85,
                        "local_overlays": [
                            {
                                "entity": "entity_translator",
                                "delta": 0.45,
                                "overlay_after": 0.67,
                                "membership_weight": 0.8
                            }
                        ]
                    }
                ]
            }
        """
        if not updates:
            return

        # Compute aggregate stats for telemetry
        global_deltas = [u['delta_log_weight_global'] for u in updates]
        d_mu = sum(global_deltas) / len(global_deltas) if global_deltas else 0.0

        # Variance calculation
        if len(global_deltas) > 1:
            mean = d_mu
            variance = sum((x - mean) ** 2 for x in global_deltas) / len(global_deltas)
            d_sigma = variance ** 0.5
        else:
            d_sigma = 0.0

        # Format updates for frontend
        formatted_updates = []
        for u in updates:
            formatted_updates.append({
                "item_id": u['item_id'],
                "delta_global": round(u['delta_log_weight_global'], 4),
                "log_weight_new": round(u['log_weight_new'], 4),
                "local_overlays": [
                    {
                        "entity": overlay['entity'],
                        "delta": round(overlay['delta'], 4),
                        "overlay_after": round(overlay['overlay_after'], 4),
                        "membership_weight": round(overlay['membership_weight'], 3)
                    }
                    for overlay in u['local_overlays']
                ]
            })

        payload = {
            "type": "weights.updated.trace",
            "frame_id": frame_id,
            "scope": scope,
            "cohort": cohort,
            "entity_contexts": entity_contexts,
            "global_context": global_context,
            "n": len(updates),
            "d_mu": round(d_mu, 4),
            "d_sigma": round(d_sigma, 4),
            "timestamp": "",  # Will be set by transport
            "updates": formatted_updates
        }

        self._transport.emit("weights.updated.trace", payload)

    def traversal_weight_updates(
        self,
        updates: List[Dict[str, Any]],
        frame_id: int,
        scope: str,
        cohort: str,
        entity_id: str,
        step_index: int
    ) -> None:
        """
        Emit traversal-driven weight update batch (Priority 5 - future).

        Called after stride execution updates link/node weights based on
        resonance and complementarity.

        Args:
            updates: List of weight updates from traversal
            frame_id: Current frame ID
            scope: Update scope ('link' | 'node')
            cohort: Cohort identifier
            entity_id: Entity that performed this stride
            step_index: Step number in traversal sequence

        Event payload format (matches websocket-types.ts WeightsUpdatedTraversalEvent):
            {
                "type": "weights.updated.traversal",
                "frame_id": 123,
                "scope": "link",
                "cohort": "RELATES_TO",
                "entity_id": "entity_translator",
                "step_index": 5,
                "n": 8,
                "d_mu": 0.015,
                "d_sigma": 0.08,
                "timestamp": "2025-10-25T04:30:15.123Z",
                "updates": [...]
            }
        """
        if not updates:
            return

        # Compute aggregate stats
        deltas = [u.get('delta', 0.0) for u in updates]
        d_mu = sum(deltas) / len(deltas) if deltas else 0.0

        if len(deltas) > 1:
            mean = d_mu
            variance = sum((x - mean) ** 2 for x in deltas) / len(deltas)
            d_sigma = variance ** 0.5
        else:
            d_sigma = 0.0

        # Format updates
        formatted_updates = [
            {
                "item_id": u['item_id'],
                "delta": round(u['delta'], 4),
                "weight_new": round(u['weight_new'], 4)
            }
            for u in updates
        ]

        payload = {
            "type": "weights.updated.traversal",
            "frame_id": frame_id,
            "scope": scope,
            "cohort": cohort,
            "entity_id": entity_id,
            "step_index": step_index,
            "n": len(updates),
            "d_mu": round(d_mu, 4),
            "d_sigma": round(d_sigma, 4),
            "timestamp": "",  # Will be set by transport
            "updates": formatted_updates
        }

        self._transport.emit("weights.updated.traversal", payload)


class NoOpTransport:
    """
    No-op transport for testing or when observability is disabled.

    Example:
        >>> emitter = WeightLearningEmitter(NoOpTransport())
        >>> emitter.trace_weight_updates([...])  # No-op, no errors
    """
    def emit(self, event_type: str, payload: Any) -> None:
        """Do nothing."""
        pass


class BroadcasterTransport:
    """
    Transport adapter for ConsciousnessStateBroadcaster.

    Wraps broadcaster's async broadcast_event() method to match Transport protocol.
    Uses run_coroutine_threadsafe for thread-safe async emission.

    Example:
        >>> broadcaster = ConsciousnessStateBroadcaster()
        >>> transport = BroadcasterTransport(broadcaster)
        >>> emitter = WeightLearningEmitter(transport)
    """

    def __init__(self, broadcaster):
        """
        Initialize transport with broadcaster.

        Args:
            broadcaster: ConsciousnessStateBroadcaster instance
        """
        self._broadcaster = broadcaster

    def emit(self, event_type: str, payload: Any) -> None:
        """
        Emit event via broadcaster (thread-safe async emission).

        Args:
            event_type: Event type string (e.g., "weights.updated.trace")
            payload: Event payload dict
        """
        if not self._broadcaster or not self._broadcaster.is_available():
            return

        # Thread-safe async emission
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(
                self._broadcaster.broadcast_event(event_type, payload),
                loop=loop
            )
        except RuntimeError:
            # No running loop - skip emission
            pass
