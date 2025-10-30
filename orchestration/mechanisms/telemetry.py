"""
Live Visualization Telemetry

Implements:
- Diff-first event stream (zero snapshots)
- 2-frame reorder buffer for temporal coherence
- WebSocket event emission
- Event schema for subentity/stride/node/convergence tracking

Author: AI #7
Created: 2025-10-20
Dependencies: sub_entity_core, asyncio, websockets
Zero-Constants: All events derived from actual state changes
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from collections import deque
from orchestration.mechanisms.sub_entity_core import SubEntity


# --- Global Event Buffer ---
_event_buffer = None

def get_event_buffer():
    """Get or create global event buffer."""
    global _event_buffer
    if _event_buffer is None:
        _event_buffer = EventBuffer(buffer_frames=2)
    return _event_buffer


# --- Event Schema ---

def emit_edge_valence_batch_event(
    frame: int,
    subentity: SubEntity,
    source_i: int,
    candidates: List[Dict[str, Any]],
    ws_connection=None
):
    """
    Emit edge valence batch event (CRITICAL for hunger gate observability).

    Schema:
        {
            "type": "edge.valence_batch",
            "frame": int,
            "subentity": str,
            "source": str,
            "candidates": [
                {
                    "target": str,
                    "valence": float,
                    "gates": {
                        "homeostasis": float,
                        "goal": float,
                        "ease": float,
                        ... other hungers
                    },
                    "hunger_scores": {
                        "homeostasis": float,
                        "goal": float,
                        "ease": float,
                        ... other hungers
                    }
                }
            ]
        }

    Args:
        frame: Current frame number
        subentity: Sub-entity evaluating edges
        source_i: Source node ID
        candidates: List of candidate edges with valence breakdown
        ws_connection: WebSocket connection (optional)

    Note:
        This event is CRITICAL for observability. Without it, hunger gates
        are invisible and we cannot verify that hunger-driven traversal is
        working correctly. Added based on AI #7's schema validation findings.
    """
    event = {
        "type": "edge.valence_batch",
        "frame": frame,
        "subentity": subentity.id,
        "source": str(source_i),
        "candidates": candidates
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


def emit_entity_quota_event(
    frame: int,
    subentity: SubEntity,
    quota_assigned: int,
    ws_connection=None
):
    """
    Emit subentity quota allocation event.

    Schema:
        {
            "type": "subentity.quota",
            "frame": int,
            "subentity": str,
            "quota": int,
            "extent_size": int,
            "total_energy": float
        }

    Args:
        frame: Current frame number
        subentity: Sub-entity that received quota
        quota_assigned: Number of strides allocated
        ws_connection: WebSocket connection (optional)
    """
    # Calculate total energy in extent
    total_energy = sum(subentity.get_energy(node_id) for node_id in subentity.extent)

    event = {
        "type": "subentity.quota",
        "frame": frame,
        "subentity": subentity.id,
        "quota": quota_assigned,
        "extent_size": len(subentity.extent),
        "total_energy": total_energy
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


def emit_stride_exec_event(
    frame: int,
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    delta: float,
    alpha: float,
    pred_roi: float,
    actual_time_us: float,
    rho_local: float,
    source_after: Dict[str, float],
    target_after: Dict[str, float],
    ws_connection=None
):
    """
    Emit stride execution event.

    Schema:
        {
            "type": "stride.exec",
            "frame": int,
            "subentity": str,
            "edge": {"i": str, "j": str},
            "delta": float,
            "alpha": float,
            "pred_roi": float,
            "actual_time_us": float,
            "rho_local": float,
            "source_after": {"E": float, "theta": float},
            "target_after": {"E": float, "theta": float}
        }

    Args:
        frame: Current frame number
        subentity: Sub-entity executing stride
        source_i: Source node ID
        target_j: Target node ID
        delta: Energy transferred
        alpha: Damping factor applied
        pred_roi: Predicted ROI for this stride
        actual_time_us: Actual execution time (microseconds)
        rho_local: Estimated local spectral radius
        source_after: Source node state after transfer
        target_after: Target node state after transfer
        ws_connection: WebSocket connection (optional)
    """
    event = {
        "type": "stride.exec",
        "frame": frame,
        "subentity": subentity.id,
        "edge": {"i": str(source_i), "j": str(target_j)},
        "delta": delta,
        "alpha": alpha,
        "pred_roi": pred_roi,
        "actual_time_us": actual_time_us,
        "rho_local": rho_local,
        "source_after": source_after,
        "target_after": target_after
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


def emit_node_activation_event(
    frame: int,
    subentity: SubEntity,
    node_id: int,
    activation_type: str,  # "activate" | "deactivate"
    energy: float,
    threshold: float,
    ws_connection=None
):
    """
    Emit node activation/deactivation event.

    Schema:
        {
            "type": "node.activation",
            "frame": int,
            "subentity": str,
            "node": str,
            "event": "activate" | "deactivate",
            "energy": float,
            "threshold": float
        }

    Args:
        frame: Current frame number
        subentity: Sub-entity
        node_id: Node that changed activation state
        activation_type: "activate" or "deactivate"
        energy: Current energy level
        threshold: Activation threshold
        ws_connection: WebSocket connection (optional)
    """
    event = {
        "type": "node.activation",
        "frame": frame,
        "subentity": subentity.id,
        "node": str(node_id),
        "event": activation_type,
        "energy": energy,
        "threshold": threshold
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


def emit_convergence_event(
    frame: int,
    subentity: SubEntity,
    reason: str,  # "roi_below_whisker" | "quota_exhausted" | "deadline"
    final_roi: float,
    whisker_threshold: float,
    strides_executed: int,
    ws_connection=None
):
    """
    Emit subentity convergence event.

    Schema:
        {
            "type": "subentity.converged",
            "frame": int,
            "subentity": str,
            "reason": str,
            "final_roi": float,
            "whisker_threshold": float,
            "strides_executed": int,
            "final_extent_size": int
        }

    Args:
        frame: Current frame number
        subentity: Sub-entity that converged
        reason: Convergence trigger
        final_roi: Last ROI value
        whisker_threshold: Q1 - 1.5×IQR threshold
        strides_executed: Total strides before convergence
        ws_connection: WebSocket connection (optional)
    """
    event = {
        "type": "subentity.converged",
        "frame": frame,
        "subentity": subentity.id,
        "reason": reason,
        "final_roi": final_roi,
        "whisker_threshold": whisker_threshold,
        "strides_executed": strides_executed,
        "final_extent_size": len(subentity.extent)
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


# --- 2-Frame Reorder Buffer ---

class EventBuffer:
    """
    2-frame reorder buffer for temporal coherence.

    Delays emission by 2 frames to handle out-of-order events.
    This prevents viewer flicker from async timing issues.
    """

    def __init__(self, buffer_frames: int = 2):
        """
        Initialize event buffer.

        Args:
            buffer_frames: Number of frames to delay (default 2)
        """
        self.buffer_frames = buffer_frames
        self.buffer: List[tuple] = []  # List of (frame, event) tuples
        self.current_frame = 0

    def add_event(self, frame: int, event: Dict[str, Any]):
        """
        Add event to buffer.

        Args:
            frame: Frame number for event
            event: Event dict
        """
        self.buffer.append((frame, event))

        # Keep buffer size reasonable (max 10000 events)
        if len(self.buffer) > 10000:
            # Remove oldest events
            self.buffer = self.buffer[-10000:]

    def flush_ready_events(self, current_frame: int) -> List[Dict[str, Any]]:
        """
        Flush events ready for emission.

        Events ready when: event_frame <= (current_frame - buffer_frames)

        Args:
            current_frame: Current frame number

        Returns:
            List of events sorted by frame number
        """
        self.current_frame = current_frame
        threshold_frame = current_frame - self.buffer_frames

        # Separate ready and pending events
        ready_events = []
        pending_events = []

        for frame, event in self.buffer:
            if frame <= threshold_frame:
                ready_events.append(event)
            else:
                pending_events.append((frame, event))

        # Update buffer with only pending events
        self.buffer = pending_events

        # Sort ready events by frame for temporal coherence
        ready_events.sort(key=lambda e: e.get('frame', 0))

        return ready_events


# --- WebSocket Integration ---

async def start_viz_websocket_server(
    host: str = "localhost",
    port: int = 8765
):
    """
    Start WebSocket server for live visualization.

    Args:
        host: Server host
        port: Server port

    Side Effects:
        Starts async WebSocket server
        Broadcasts events to all connected clients
    """
    # TODO AI #7: Implement WebSocket server
    # Use asyncio + websockets library
    # Maintain set of connected clients
    # Broadcast events to all clients
    pass


async def broadcast_event(
    event: Dict[str, Any],
    connected_clients: set
):
    """
    Broadcast event to all connected WebSocket clients.

    Args:
        event: Event dict
        connected_clients: Set of WebSocket connections

    Side Effects:
        Sends JSON event to all clients
        Removes disconnected clients from set
    """
    # TODO AI #7: Implement broadcast
    # Serialize event to JSON
    # Send to all clients (handle disconnections)
    pass


# --- Integration Helpers ---

def track_extent_changes(
    subentity: SubEntity,
    old_extent: set,
    new_extent: set,
    frame: int,
    ws_connection=None
):
    """
    Track and emit extent changes (activations/deactivations).

    Args:
        subentity: Sub-entity
        old_extent: Extent from previous frame
        new_extent: Extent from current frame
        frame: Current frame number
        ws_connection: WebSocket connection (optional)

    Side Effects:
        Emits node.activation events for all changes
    """
    # Activated nodes = new - old
    activated = new_extent - old_extent
    for node_id in activated:
        energy = subentity.get_energy(node_id)
        threshold = subentity.get_threshold(node_id)
        emit_node_activation_event(
            frame, subentity, node_id, "activate", energy, threshold, ws_connection
        )

    # Deactivated nodes = old - new
    deactivated = old_extent - new_extent
    for node_id in deactivated:
        energy = subentity.get_energy(node_id)
        threshold = subentity.get_threshold(node_id)
        emit_node_activation_event(
            frame, subentity, node_id, "deactivate", energy, threshold, ws_connection
        )


def emit_frame_summary(
    frame: int,
    subentities: List[SubEntity],
    strides_executed: int,
    wall_time_us: float,
    ws_connection=None
):
    """
    Emit frame summary event.

    Schema:
        {
            "type": "frame.summary",
            "frame": int,
            "entities_active": int,
            "strides_executed": int,
            "wall_time_us": float,
            "avg_roi": float
        }

    Args:
        frame: Current frame number
        subentities: Active subentities this frame
        strides_executed: Total strides executed
        wall_time_us: Frame execution time
        ws_connection: WebSocket connection (optional)
    """
    # Calculate average ROI across subentities
    if subentities:
        # Get last ROI value from each subentity's tracker
        roi_values = []
        for subentity in subentities:
            if subentity.roi_tracker.window:
                roi_values.append(subentity.roi_tracker.window[-1])

        avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0.0
    else:
        avg_roi = 0.0

    event = {
        "type": "frame.summary",
        "frame": frame,
        "entities_active": len(subentities),
        "strides_executed": strides_executed,
        "wall_time_us": wall_time_us,
        "avg_roi": avg_roi
    }

    buffer = get_event_buffer()
    buffer.add_event(frame, event)


# --- Event Schema Validation (Optional) ---

def validate_event_schema(event: Dict[str, Any]) -> bool:
    """
    Validate event against schema.

    Args:
        event: Event dict

    Returns:
        True if valid, False otherwise

    Note:
        This is optional - helpful for debugging but not required
    """
    # TODO AI #7: Implement schema validation
    # Check required fields for each event type
    pass
