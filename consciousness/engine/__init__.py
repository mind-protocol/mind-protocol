"""Engine façade and ports for the consciousness system."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional, Protocol, Sequence

from consciousness.engine.constants import (
    DEFAULT_MAX_ENERGY,
    DEFAULT_TICK_INTERVAL_MS,
    ENGINE_TICK_EVENT,
    GRAPH_UPSERT_TYPE,
    TELEMETRY_EMIT_TYPE,
)
from consciousness.engine.domain.state import EngineState, build_engine_state
from consciousness.engine.services.scheduler import SchedulerDecision, plan_next_tick

# Phase 1: Energy dynamics
from consciousness.engine.domain import energy

# Phase 2: Spreading activation
from consciousness.engine.domain import activation

# Phase 3: Frame loop orchestration
from consciousness.engine.services.frame_loop import FrameOrchestrator, FrameResult, Stimulus

from libs.law import implements

logger = logging.getLogger(__name__)


class GraphPort(Protocol):
    """Port abstraction for graph persistence operations."""

    def load(self, entity_id: str) -> Any:
        """Load the graph for a given entity identifier."""

    def persist(self, entity_id: str, intents: Sequence[Mapping[str, Any]]) -> None:
        """Persist intents that mutate the graph for a given entity identifier."""


class TelemetryPort(Protocol):
    """Port abstraction for emitting telemetry events."""

    def publish(self, event: str, payload: Mapping[str, Any]) -> None:
        """Publish a telemetry payload under the provided event name."""


@dataclass(frozen=True)
class EngineConfig:
    """Configuration for the façade layer."""

    entity_id: str = "consciousness_engine"
    tick_interval_ms: float = DEFAULT_TICK_INTERVAL_MS
    max_energy: float = DEFAULT_MAX_ENERGY
    telemetry_event: str = ENGINE_TICK_EVENT

    @classmethod
    def from_legacy(cls, legacy_config: Any | None) -> "EngineConfig":
        """Create a façade configuration from the legacy engine config object."""

        if legacy_config is None:
            return cls()

        return cls(
            entity_id=getattr(legacy_config, "entity_id", cls.entity_id),
            tick_interval_ms=float(getattr(legacy_config, "tick_interval_ms", cls.tick_interval_ms)),
            max_energy=float(getattr(legacy_config, "max_energy", cls.max_energy)),
            telemetry_event=getattr(legacy_config, "telemetry_event", cls.telemetry_event),
        )


@implements("Mechanism:ENGINE_FACADE", "Suite:GODFILE-1.0/A2")
class Engine:
    """Façade that exposes pure transitions and intent planning for the legacy engine."""

    def __init__(
        self,
        legacy_engine: Any,
        *,
        telemetry: Optional[TelemetryPort] = None,
        graph_port: Optional[GraphPort] = None,
        config: Optional[EngineConfig] = None,
    ) -> None:
        self._legacy_engine = legacy_engine
        self.telemetry = telemetry
        self.graph_port = graph_port
        self.config = config or EngineConfig.from_legacy(getattr(legacy_engine, "config", None))
        self._last_decision: Optional[SchedulerDecision] = None

    def snapshot(
        self,
        *,
        now: Optional[datetime] = None,
        branching_state: Optional[Mapping[str, Any]] = None,
    ) -> EngineState:
        """Build a pure engine state snapshot."""

        observation_time = now or datetime.now()
        if branching_state is None:
            tracker = getattr(self._legacy_engine, "branching_tracker", None)
            tick_count = getattr(self._legacy_engine, "tick_count", 0)
            if tracker is not None and tick_count > 0:
                try:
                    branching_state = tracker.measure_cycle([], [])
                except Exception:  # pragma: no cover - defensive logging
                    logger.debug("Failed to measure branching state", exc_info=True)

        return build_engine_state(
            graph=getattr(self._legacy_engine, "graph"),
            tick_count=getattr(self._legacy_engine, "tick_count", 0),
            last_tick_time=getattr(self._legacy_engine, "last_tick_time", observation_time),
            observed_at=observation_time,
            config=self.config,
            branching_state=branching_state,
        )

    @implements("Mechanism:ENGINE_TICK", "Suite:GODFILE-1.0/A2")
    def plan_tick(
        self,
        stimuli: Optional[Sequence[Mapping[str, Any]]] = None,
        *,
        now: Optional[datetime] = None,
        branching_state: Optional[Mapping[str, Any]] = None,
    ) -> SchedulerDecision:
        """Plan intents for the next tick and optionally emit telemetry."""

        state = self.snapshot(now=now, branching_state=branching_state)
        decision = plan_next_tick(state, stimuli)
        if self.telemetry is not None:
            for intent in decision.intents:
                if intent.get("type") == TELEMETRY_EMIT_TYPE:
                    payload = intent.get("payload", {})
                    event = payload.get("event", self.config.telemetry_event)
                    data = payload.get("data", {})
                    try:
                        self.telemetry.publish(event, data)
                    except Exception:  # pragma: no cover - defensive logging
                        logger.debug("Telemetry publish failed", exc_info=True)
        self._last_decision = decision
        return decision

    @property
    def last_decision(self) -> Optional[SchedulerDecision]:
        """Return the most recent scheduler decision, if any."""

        return self._last_decision

    @implements("Mechanism:ENGINE_INTENT_DISPATCH", "Suite:GODFILE-1.0/A3")
    def dispatch_intents(self, intents: Sequence[Mapping[str, Any]]) -> None:
        """Send intents to the configured graph port when available."""

        if self.graph_port is None:
            return

        graph_intents = [intent for intent in intents if intent.get("type") == GRAPH_UPSERT_TYPE]
        if not graph_intents:
            return

        try:
            self.graph_port.persist(self.config.entity_id, graph_intents)
        except Exception:  # pragma: no cover - defensive logging
            logger.debug("Graph port dispatch failed", exc_info=True)


__all__ = [
    "Engine",
    "EngineConfig",
    "EngineState",
    "GraphPort",
    "SchedulerDecision",
    "TelemetryPort",
    # Phase 3: Frame orchestration
    "FrameOrchestrator",
    "FrameResult",
    "Stimulus",
]
