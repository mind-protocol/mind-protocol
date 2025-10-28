"""
Consciousness Telemetry - End-to-End Observability Events

Implements telemetry events for consciousness observability:
- stimulus.* events (created, queued, injection lifecycle)
- wm.* events (changed, state deltas)
- forged_identity.* events (prompt generation)
- tick.* events (diffusion, traversal)

Part of end-to-end consciousness observability infrastructure.

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: docs/specs/v2/ops_and_viz/end_to_end_consciousness_observability.md
"""

import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


@dataclass
class StimulusCreatedEvent:
    """Event: stimulus.created - Stimulus created from user input."""
    event: str = "stimulus.created"
    timestamp: float = 0.0
    citizen_id: str = ""
    stimulus_id: str = ""
    content: str = ""
    source: str = ""
    energy: float = 0.0


@dataclass
class StimulusQueuedEvent:
    """Event: stimulus.queued - Stimulus added to processing queue."""
    event: str = "stimulus.queued"
    timestamp: float = 0.0
    citizen_id: str = ""
    stimulus_id: str = ""
    queue_position: int = 0
    queue_length: int = 0


@dataclass
class StimulusInjectionStartEvent:
    """Event: stimulus.injection.start - Injection begins."""
    event: str = "stimulus.injection.start"
    timestamp: float = 0.0
    citizen_id: str = ""
    stimulus_id: str = ""
    tick: int = 0
    matches_count: int = 0
    source_type: str = ""


@dataclass
class StimulusInjectionCompleteEvent:
    """Event: stimulus.injection.complete - Injection completes with results."""
    event: str = "stimulus.injection.complete"
    timestamp: float = 0.0
    citizen_id: str = ""
    stimulus_id: str = ""
    tick: int = 0
    result: Dict[str, Any] = None


@dataclass
class WMChangedEvent:
    """Event: wm.changed - Working memory contents changed."""
    event: str = "wm.changed"
    timestamp: float = 0.0
    citizen_id: str = ""
    tick: int = 0
    wm_before: List[str] = None
    wm_after: List[str] = None
    added: List[str] = None
    removed: List[str] = None
    jaccard_similarity: float = 0.0


@dataclass
class TickDiffusionEvent:
    """Event: tick.diffusion - Energy diffusion summary."""
    event: str = "tick.diffusion"
    timestamp: float = 0.0
    citizen_id: str = ""
    tick: int = 0
    active_nodes_count: int = 0
    energy_transferred: float = 0.0
    links_traversed: int = 0
    propagation_depth: int = 0


@dataclass
class ForgedIdentityFrameEvent:
    """Event: forged.identity.frame - Compact forged identity frame payload."""
    event: str = "forged.identity.frame"
    timestamp: str = ""
    frame_id: int = 0
    citizen_id: str = ""
    tick: int = 0
    stimulus_id: str = ""
    prompt_preview: str = ""
    prompt_length: int = 0
    prompt_sections: int = 0
    wm_nodes: Optional[List[str]] = None
    full_prompt: str = ""
    mode: str = "observe_only"


@dataclass
class ForgedIdentityMetricsEvent:
    """Event: forged.identity.metrics - Aggregated forging counters."""
    event: str = "forged.identity.metrics"
    timestamp: str = ""
    frame_id: int = 0
    citizen_id: str = ""
    total_frames: int = 0
    wm_node_count: int = 0
    prompt_length: int = 0
    active_subentities: int = 0
    tokens_estimate: int = 0
    tokens_accumulated: int = 0


class ConsciousnessTelemetry:
    """
    Telemetry emitter for consciousness observability events.

    Provides typed event emission with automatic timestamping and WebSocket broadcasting.
    """

    def __init__(self, broadcaster=None):
        """
        Initialize telemetry emitter.

        Args:
            broadcaster: Optional WebSocket broadcaster for real-time event streaming
        """
        self.broadcaster = broadcaster
        self._event_loop = None

    def capture_event_loop(self):
        """Capture current event loop for async emission."""
        try:
            self._event_loop = asyncio.get_running_loop()
            logger.info("[ConsciousnessTelemetry] Event loop captured")
        except RuntimeError:
            logger.warning("[ConsciousnessTelemetry] No running event loop")

    def emit_stimulus_created(
        self,
        citizen_id: str,
        stimulus_id: str,
        content: str,
        source: str,
        energy: float
    ):
        """Emit stimulus.created event."""
        event = StimulusCreatedEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            stimulus_id=stimulus_id,
            content=content,
            source=source,
            energy=energy
        )
        self._emit(event)

    def emit_stimulus_queued(
        self,
        citizen_id: str,
        stimulus_id: str,
        queue_position: int,
        queue_length: int
    ):
        """Emit stimulus.queued event."""
        event = StimulusQueuedEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            stimulus_id=stimulus_id,
            queue_position=queue_position,
            queue_length=queue_length
        )
        self._emit(event)

    def emit_stimulus_injection_start(
        self,
        citizen_id: str,
        stimulus_id: str,
        tick: int,
        matches_count: int,
        source_type: str
    ):
        """Emit stimulus.injection.start event."""
        event = StimulusInjectionStartEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            stimulus_id=stimulus_id,
            tick=tick,
            matches_count=matches_count,
            source_type=source_type
        )
        self._emit(event)

    def emit_stimulus_injection_complete(
        self,
        citizen_id: str,
        stimulus_id: str,
        tick: int,
        result: Dict[str, Any]
    ):
        """Emit stimulus.injection.complete event."""
        event = StimulusInjectionCompleteEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            stimulus_id=stimulus_id,
            tick=tick,
            result=result
        )
        self._emit(event)

    def emit_wm_changed(
        self,
        citizen_id: str,
        tick: int,
        wm_before: List[str],
        wm_after: List[str]
    ):
        """
        Emit wm.changed event.

        Automatically computes added, removed, and Jaccard similarity.
        """
        # Compute set operations
        set_before = set(wm_before)
        set_after = set(wm_after)

        added = list(set_after - set_before)
        removed = list(set_before - set_after)

        # Jaccard similarity
        intersection = len(set_before & set_after)
        union = len(set_before | set_after)
        jaccard = intersection / union if union > 0 else 0.0

        event = WMChangedEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            tick=tick,
            wm_before=wm_before,
            wm_after=wm_after,
            added=added,
            removed=removed,
            jaccard_similarity=jaccard
        )
        self._emit(event)

    def emit_tick_diffusion(
        self,
        citizen_id: str,
        tick: int,
        active_nodes_count: int,
        energy_transferred: float,
        links_traversed: int,
        propagation_depth: int
    ):
        """Emit tick.diffusion event."""
        event = TickDiffusionEvent(
            timestamp=time.time(),
            citizen_id=citizen_id,
            tick=tick,
            active_nodes_count=active_nodes_count,
            energy_transferred=energy_transferred,
            links_traversed=links_traversed,
            propagation_depth=propagation_depth
        )
        self._emit(event)

    def emit_forged_identity_frame(
        self,
        citizen_id: str,
        frame_id: int,
        stimulus_id: str,
        prompt_preview: str,
        prompt_length: int,
        prompt_sections: int,
        wm_nodes: Optional[List[str]],
        full_prompt: str,
        tick: int = 0,
        mode: str = "observe_only"
    ) -> None:
        """Emit forged.identity.frame event (compact payload + full prompt)."""
        event = ForgedIdentityFrameEvent(
            timestamp=_now_iso(),
            frame_id=frame_id,
            citizen_id=citizen_id,
            tick=tick,
            stimulus_id=stimulus_id,
            prompt_preview=prompt_preview,
            prompt_length=prompt_length,
            prompt_sections=prompt_sections,
            wm_nodes=wm_nodes,
            full_prompt=full_prompt,
            mode=mode
        )
        self._emit(event)

    def emit_forged_identity_metrics(
        self,
        citizen_id: str,
        frame_id: int,
        total_frames: int,
        wm_node_count: int,
        prompt_length: int,
        active_subentities: int,
        tokens_estimate: int,
        tokens_accumulated: int
    ) -> None:
        """Emit forged.identity.metrics event (apportionment counters)."""
        event = ForgedIdentityMetricsEvent(
            timestamp=_now_iso(),
            frame_id=frame_id,
            citizen_id=citizen_id,
            total_frames=total_frames,
            wm_node_count=wm_node_count,
            prompt_length=prompt_length,
            active_subentities=active_subentities,
            tokens_estimate=tokens_estimate,
            tokens_accumulated=tokens_accumulated
        )
        self._emit(event)

    def _emit(self, event):
        """
        Emit event via WebSocket broadcaster.

        Args:
            event: Dataclass event object
        """
        if not self.broadcaster:
            logger.debug(f"[ConsciousnessTelemetry] No broadcaster, skipping event: {event.event}")
            return

        event_dict = asdict(event)

        # Emit via WebSocket (async)
        if self._event_loop and self._event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcaster.broadcast_event(event.event, event_dict),
                self._event_loop
            )
        else:
            logger.warning(
                f"[ConsciousnessTelemetry] No event loop available, "
                f"cannot emit {event.event}"
            )

        logger.debug(f"[ConsciousnessTelemetry] Emitted: {event.event}")
