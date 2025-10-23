"""
Traversal Event Emitter - Emotion and Stride Observability

Thin interface for emitting per-stride and per-node emotion deltas.
Actual transport (WebSocket, logs, etc.) is injected by the WS service.

This keeps emotion observability separate from coarse consciousness state
(which goes through ConsciousnessStateBroadcaster).

Author: Felix (Engineer)
Created: 2025-10-22
Spec: emotion_coloring.md §7 (Observability)
Supersedes: Previous polling-based implementation
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Protocol, Sequence, Tuple


@dataclass
class EmotionDelta:
    """
    Emotion update delta for a single node or link.

    Args:
        id: Node or link ID
        mag: Magnitude of emotion vector after update ||E_emo||
        top_axes: Top K emotion axes with values, e.g. [("joy", 0.42), ("peace", 0.18)]
    """
    id: str
    mag: float
    top_axes: Sequence[Tuple[str, float]]


class Transport(Protocol):
    """
    Transport protocol for event emission.

    Injected by WS service - can be WebSocket broadcaster, logger, queue, etc.
    """
    def emit(self, event_type: str, payload: Any) -> None:
        """Emit event with payload to connected clients."""
        ...


class TraversalEventEmitter:
    """
    Emits traversal and emotion events for observability.

    Events emitted:
    - node.emotion.update: Sampled emotion deltas for nodes
    - link.emotion.update: Sampled emotion deltas for links
    - stride.exec: Stride execution with comp/res attribution

    Example:
        >>> transport = WebSocketTransport()
        >>> emitter = TraversalEventEmitter(transport)
        >>> emitter.node_emotion_update([
        ...     EmotionDelta(id="node_123", mag=0.65, top_axes=[("joy", 0.42)])
        ... ])
    """

    def __init__(self, transport: Transport):
        """
        Initialize emitter with transport.

        Args:
            transport: Transport implementation (WebSocket, logger, etc.)
        """
        self._transport = transport

    def node_emotion_update(self, deltas: Iterable[EmotionDelta]) -> None:
        """
        Emit batched node emotion updates.

        Emits deltas-only (not full state) for efficiency.
        Called after color_element() updates node emotion metadata.

        Args:
            deltas: Iterable of EmotionDelta objects

        Event payload format:
            {
                "v": "2",
                "frame_id": tick_count,
                "updates": [
                    {"id": "node_123", "mag": 0.65, "top_axes": [["joy", 0.42]]},
                    ...
                ],
                "t_ms": timestamp
            }
        """
        delta_list = list(deltas)
        if not delta_list:
            return

        payload = [
            {
                "id": d.id,
                "mag": round(d.mag, 4),
                "top_axes": [[axis, round(val, 3)] for axis, val in d.top_axes]
            }
            for d in delta_list
        ]

        self._transport.emit("node.emotion.update", payload)

    def link_emotion_update(self, deltas: Iterable[EmotionDelta]) -> None:
        """
        Emit batched link emotion updates.

        Same format as node_emotion_update but for links.
        Called after color_element() updates link emotion metadata during stride.

        Args:
            deltas: Iterable of EmotionDelta objects
        """
        delta_list = list(deltas)
        if not delta_list:
            return

        payload = [
            {
                "id": d.id,
                "mag": round(d.mag, 4),
                "top_axes": [[axis, round(val, 3)] for axis, val in d.top_axes]
            }
            for d in delta_list
        ]

        self._transport.emit("link.emotion.update", payload)

    def stride_exec(self, data: Mapping[str, Any]) -> None:
        """
        Emit stride execution event with attribution.

        Enriched with comp/res multipliers so UI can show why this edge was chosen.

        Args:
            data: Stride execution data with attribution

        Expected fields in data:
            - src_node: Source node ID
            - dst_node: Destination node ID
            - resonance: Cosine similarity between entity affect and link emotion
            - res_mult: Resonance cost multiplier applied
            - comp_score: Complementarity score (opposite affect attraction)
            - comp_mult: Complementarity cost multiplier applied
            - cost: Final cost after gates
            - chosen: Whether this edge was selected
        """
        self._transport.emit("stride.exec", data)


class NoOpTransport:
    """
    No-op transport for testing or when observability is disabled.

    Example:
        >>> emitter = TraversalEventEmitter(NoOpTransport())
        >>> emitter.node_emotion_update([...])  # No-op, no errors
    """
    def emit(self, event_type: str, payload: Any) -> None:
        """Do nothing."""
        pass
