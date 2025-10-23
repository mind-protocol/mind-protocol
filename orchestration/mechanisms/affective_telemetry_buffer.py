"""
Affective Telemetry Event Buffer

Buffers PR-A and PR-B affective coupling events for dashboard visualization.

Provides:
- Event buffering for 11 affective event types
- Telemetry metrics (sample rate, buffer utilization)
- Schema validation support
- Thread-safe access for real-time queries

PR-A Event Types:
  affective.threshold, affective.memory, coherence.persistence,
  pattern.multiresponse, identity.multiplicity, consolidation,
  decay.resistance, diffusion.stickiness, affective.priming,
  coherence.metric, criticality.mode

PR-B Specific (subset of PR-A):
  affective.threshold, affective.memory, coherence.persistence

Author: Iris "The Aperture"
Created: 2025-10-23
Purpose: Enable PR-A/PR-B frontend visualization
"""

import threading
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class AffectiveTelemetryBuffer:
    """
    Thread-safe buffer for affective coupling events.

    Stores recent events for dashboard queries without blocking
    consciousness engine execution.
    """

    def __init__(self, max_events_per_type: int = 100, max_recent_events: int = 50):
        """
        Initialize affective event buffer.

        Args:
            max_events_per_type: Max events to store per type (prevents unbounded growth)
            max_recent_events: Max events to return in recent-events query
        """
        self.max_events_per_type = max_events_per_type
        self.max_recent_events = max_recent_events

        # Event storage: {event_type: deque of events}
        self.events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events_per_type))

        # Event counts (for telemetry)
        self.event_counts: Dict[str, int] = defaultdict(int)

        # Buffer metadata
        self.total_events_received = 0
        self.sample_rate = 1.0  # Start at 100% sampling (can be reduced if overwhelmed)

        # Thread lock for safe concurrent access
        self.lock = threading.Lock()

    def add_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Add event to buffer.

        Args:
            event_type: Event type (e.g., "affective.threshold")
            event_data: Event data dict

        Thread-safe operation.
        """
        with self.lock:
            # Add timestamp if not present
            if "timestamp" not in event_data:
                event_data["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Add type to event data
            event_data["type"] = event_type

            # Store event
            self.events[event_type].append(event_data)

            # Increment counters
            self.event_counts[event_type] += 1
            self.total_events_received += 1

    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events of a specific type or all types.

        Args:
            event_type: Event type filter (None = all types)
            limit: Max events to return (None = use max_recent_events)

        Returns:
            List of events sorted by timestamp (newest first)

        Thread-safe operation.
        """
        with self.lock:
            if event_type:
                # Get events for specific type
                events = list(self.events[event_type])
            else:
                # Get all events across all types
                events = []
                for event_queue in self.events.values():
                    events.extend(list(event_queue))

            # Sort by timestamp (newest first)
            events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

            # Apply limit
            max_events = limit if limit is not None else self.max_recent_events
            return events[:max_events]

    def get_event_counts(self) -> Dict[str, int]:
        """
        Get event counts by type.

        Returns:
            Dict of {event_type: count}

        Thread-safe operation.
        """
        with self.lock:
            return dict(self.event_counts)

    def get_telemetry_metrics(self) -> Dict[str, Any]:
        """
        Get telemetry metrics for dashboard.

        Returns:
            {
                "sampleRate": float (0-1),
                "bufferUtilization": float (0-1),
                "totalEventsReceived": int,
                "activeEventTypes": int
            }

        Thread-safe operation.
        """
        with self.lock:
            # Calculate buffer utilization (percentage of capacity used)
            total_capacity = self.max_events_per_type * len(self.events)
            total_stored = sum(len(q) for q in self.events.values())
            buffer_utilization = total_stored / total_capacity if total_capacity > 0 else 0.0

            return {
                "sampleRate": self.sample_rate,
                "bufferUtilization": buffer_utilization,
                "totalEventsReceived": self.total_events_received,
                "activeEventTypes": len([et for et, count in self.event_counts.items() if count > 0])
            }

    def clear(self):
        """
        Clear all buffered events (for testing).

        Thread-safe operation.
        """
        with self.lock:
            self.events.clear()
            self.event_counts.clear()
            self.total_events_received = 0


# Global singleton instance
_global_buffer: Optional[AffectiveTelemetryBuffer] = None


def get_affective_buffer() -> AffectiveTelemetryBuffer:
    """
    Get or create global affective event buffer.

    Returns:
        Singleton AffectiveTelemetryBuffer instance
    """
    global _global_buffer
    if _global_buffer is None:
        _global_buffer = AffectiveTelemetryBuffer()
    return _global_buffer


# === Event Emission Helpers (to be called by mechanisms) ===

def emit_threshold_modulation_event(
    node_id: str,
    theta_base: float,
    theta_adjusted: float,
    h: float,
    affective_alignment: float,
    emotion_magnitude: float
):
    """
    Emit affective threshold modulation event (PR-B mechanism 1).

    Args:
        node_id: Node receiving threshold adjustment
        theta_base: Base threshold before affect modulation
        theta_adjusted: Adjusted threshold after modulation
        h: Threshold reduction amount (negative = easier activation)
        affective_alignment: cos(A, E_emo) alignment score
        emotion_magnitude: ||E_emo|| emotion intensity

    Event schema (affective.threshold):
        {
            "type": "affective.threshold",
            "node_id": str,
            "theta_base": float,
            "theta_adjusted": float,
            "h": float,
            "affective_alignment": float,
            "emotion_magnitude": float,
            "timestamp": str (ISO 8601)
        }
    """
    buffer = get_affective_buffer()
    buffer.add_event("affective.threshold", {
        "node_id": node_id,
        "theta_base": theta_base,
        "theta_adjusted": theta_adjusted,
        "h": h,
        "affective_alignment": affective_alignment,
        "emotion_magnitude": emotion_magnitude
    })


def emit_affective_memory_event(
    node_id: str,
    m_affect: float,
    emotion_magnitude: float,
    delta_log_w_base: float,
    delta_log_w_amplified: float
):
    """
    Emit affective memory amplification event (PR-B mechanism 2).

    Args:
        node_id: Node receiving memory amplification
        m_affect: Memory multiplier (1.0 - 1.3)
        emotion_magnitude: ||E_emo|| emotion intensity
        delta_log_w_base: Base weight update
        delta_log_w_amplified: Amplified weight update

    Event schema (affective.memory):
        {
            "type": "affective.memory",
            "node_id": str,
            "m_affect": float,
            "emotion_magnitude": float,
            "delta_log_w_base": float,
            "delta_log_w_amplified": float,
            "timestamp": str (ISO 8601)
        }
    """
    buffer = get_affective_buffer()
    buffer.add_event("affective.memory", {
        "node_id": node_id,
        "m_affect": m_affect,
        "emotion_magnitude": emotion_magnitude,
        "delta_log_w_base": delta_log_w_base,
        "delta_log_w_amplified": delta_log_w_amplified
    })


def emit_coherence_persistence_event(
    entity_id: str,
    coherence_persistence: int,
    lambda_res_effective: float,
    lock_in_risk: bool
):
    """
    Emit coherence persistence event (PR-B mechanism 3).

    Args:
        entity_id: Entity being tracked
        coherence_persistence: Consecutive frames in same state
        lambda_res_effective: Resonance strength after decay
        lock_in_risk: True if persistence > 20 frames

    Event schema (coherence.persistence):
        {
            "type": "coherence.persistence",
            "entity_id": str,
            "coherence_persistence": int,
            "lambda_res_effective": float,
            "lock_in_risk": bool,
            "timestamp": str (ISO 8601)
        }
    """
    buffer = get_affective_buffer()
    buffer.add_event("coherence.persistence", {
        "entity_id": entity_id,
        "coherence_persistence": coherence_persistence,
        "lambda_res_effective": lambda_res_effective,
        "lock_in_risk": lock_in_risk
    })


# === Additional PR-A Event Emitters (for future PRs C-E) ===

def emit_pattern_multiresponse_event(entity_id: str, pattern_type: str, effectiveness: float):
    """Emit PR-C multi-pattern response event."""
    buffer = get_affective_buffer()
    buffer.add_event("pattern.multiresponse", {
        "entity_id": entity_id,
        "pattern_type": pattern_type,
        "effectiveness": effectiveness
    })


def emit_identity_multiplicity_event(entity_id: str, is_multiplicity_active: bool):
    """Emit PR-D identity multiplicity event."""
    buffer = get_affective_buffer()
    buffer.add_event("identity.multiplicity", {
        "entity_id": entity_id,
        "is_multiplicity_active": is_multiplicity_active
    })


def emit_consolidation_event(node_id: str, consolidation_boost: float):
    """Emit PR-E consolidation event."""
    buffer = get_affective_buffer()
    buffer.add_event("consolidation", {
        "node_id": node_id,
        "consolidation_boost": consolidation_boost
    })


def emit_decay_resistance_event(node_id: str, decay_resistance_score: float):
    """Emit PR-E decay resistance event."""
    buffer = get_affective_buffer()
    buffer.add_event("decay.resistance", {
        "node_id": node_id,
        "decay_resistance_score": decay_resistance_score
    })


def emit_diffusion_stickiness_event(node_id: str, stickiness_effect: float):
    """Emit PR-E diffusion stickiness event."""
    buffer = get_affective_buffer()
    buffer.add_event("diffusion.stickiness", {
        "node_id": node_id,
        "stickiness_effect": stickiness_effect
    })


def emit_affective_priming_event(node_id: str, priming_boost: float):
    """Emit PR-E affective priming event."""
    buffer = get_affective_buffer()
    buffer.add_event("affective.priming", {
        "node_id": node_id,
        "priming_boost": priming_boost
    })


def emit_coherence_metric_event(entity_id: str, coherence_score: float):
    """Emit PR-E coherence metric event."""
    buffer = get_affective_buffer()
    buffer.add_event("coherence.metric", {
        "entity_id": entity_id,
        "coherence_score": coherence_score
    })


def emit_criticality_mode_event(mode: str, rho: float):
    """Emit PR-E criticality mode event."""
    buffer = get_affective_buffer()
    buffer.add_event("criticality.mode", {
        "mode": mode,
        "rho": rho
    })
