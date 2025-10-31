# -*- coding: utf-8 -*-
"""
Frame Loop Orchestration - Consciousness frame execution service

This module orchestrates complete consciousness frames by coordinating:
- Spreading activation computation
- Energy dynamics application
- State persistence
- Telemetry emission

Design:
  - Service layer (orchestrates domain logic + I/O)
  - Uses ports for I/O abstraction (GraphPort, TelemetryPort)
  - Uses pure domain functions from energy.py and activation.py
  - Returns immutable state transitions

Author: Felix "Core Consciousness Engineer" + Ada "Bridgekeeper"
Created: 2025-10-31
Phase: Migration Phase 3 - Frame Loop Orchestration
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Set

from consciousness.engine.constants import DEFAULT_ACTIVATION_THRESHOLD, ENGINE_FRAME_COMPLETE_EVENT
from consciousness.engine.domain.state import EngineState
from consciousness.engine.domain import energy, activation

logger = logging.getLogger(__name__)

__all__ = [
    "FrameOrchestrator",
    "FrameResult",
    "Stimulus",
]


# === Port Definitions ===


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


class PersistencePort(Protocol):
    """Port abstraction for state persistence."""

    def save_state(self, entity_id: str, state: EngineState) -> None:
        """Persist engine state for later recovery."""

    def load_state(self, entity_id: str) -> Optional[EngineState]:
        """Load previously persisted engine state."""


# === Data Structures ===


@dataclass(frozen=True)
class Stimulus:
    """External stimulus injected into consciousness."""

    content: str
    source: str = "external"
    priority: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        # Handle mutable default
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class FrameResult:
    """Result of executing one consciousness frame."""

    state: EngineState
    active_nodes: Set[str]
    frontier_nodes: Set[str]
    total_energy: float
    average_energy: float
    telemetry_emitted: bool = False
    persistence_saved: bool = False


# === Frame Orchestrator ===


class FrameOrchestrator:
    """
    Orchestrates consciousness frame execution.

    Coordinates pure domain logic (energy, activation) with infrastructure
    (graph, telemetry, persistence) to execute complete consciousness frames.

    Design:
      - Service layer (not pure - has I/O side effects)
      - Uses ports for I/O abstraction
      - Delegates to pure domain functions
      - Returns immutable state transitions
    """

    def __init__(
        self,
        *,
        graph_port: GraphPort,
        telemetry_port: Optional[TelemetryPort] = None,
        persistence_port: Optional[PersistencePort] = None,
        entity_id: str = "consciousness_engine",
    ) -> None:
        """
        Initialize frame orchestrator with ports.

        Args:
            graph_port: Port for graph persistence operations (required)
            telemetry_port: Port for telemetry emission (optional)
            persistence_port: Port for state persistence (optional)
            entity_id: Entity identifier for this consciousness engine
        """
        self.graph_port = graph_port
        self.telemetry_port = telemetry_port
        self.persistence_port = persistence_port
        self.entity_id = entity_id
        self._frame_count = 0

    def execute_frame(
        self,
        state: EngineState,
        stimuli: Optional[List[Stimulus]] = None,
        *,
        activation_threshold: float = 0.5,
        emit_telemetry: bool = True,
        persist_state: bool = False,
    ) -> FrameResult:
        """
        Execute one consciousness frame, return new state.

        Orchestrates:
        1. Compute spreading activation (using activation.py)
        2. Apply energy dynamics (using energy.py)
        3. Persist state (if enabled)
        4. Emit telemetry (if enabled)
        5. Return new immutable state

        Args:
            state: Current engine state (immutable)
            stimuli: Optional external stimuli to inject
            activation_threshold: Minimum energy for node activation (default: 0.5)
            emit_telemetry: Whether to emit telemetry events (default: True)
            persist_state: Whether to persist state (default: False)

        Returns:
            FrameResult with new state and frame statistics
        """
        self._frame_count += 1
        logger.debug(f"[FrameOrchestrator] Executing frame {self._frame_count}")

        # Get graph from state
        graph = state.graph

        # Step 1: Compute spreading activation
        active_nodes = activation.select_active_nodes(graph, threshold=activation_threshold)
        frontier_nodes = activation.compute_frontier(graph, active_nodes, exclude_active=True)

        logger.debug(
            f"[FrameOrchestrator] Activation computed: "
            f"{len(active_nodes)} active, {len(frontier_nodes)} frontier"
        )

        # Step 2: Compute energy dynamics
        total_e = energy.compute_total_energy(graph)
        avg_e = energy.compute_average_energy(graph)
        active_count = energy.compute_active_nodes(graph, threshold=activation_threshold)

        logger.debug(
            f"[FrameOrchestrator] Energy computed: "
            f"total={total_e:.2f}, avg={avg_e:.3f}, active_count={active_count}"
        )

        # Step 3: Create new state (immutable transition)
        # For now, we keep the same graph (mutations happen elsewhere)
        # In full migration, we'd compute energy deltas and return new graph state
        new_state = replace(
            state,
            tick=state.tick + 1,
        )

        # Preserve graph attribute if present (for test compatibility)
        if hasattr(state, 'graph'):
            object.__setattr__(new_state, 'graph', state.graph)

        # Step 4: Persist state (if enabled)
        persistence_saved = False
        if persist_state and self.persistence_port:
            try:
                self.persistence_port.save_state(self.entity_id, new_state)
                persistence_saved = True
                logger.debug("[FrameOrchestrator] State persisted")
            except Exception as e:
                logger.warning(f"[FrameOrchestrator] State persistence failed: {e}")

        # Step 5: Emit telemetry (if enabled)
        telemetry_emitted = False
        if emit_telemetry and self.telemetry_port:
            try:
                telemetry_payload = {
                    "frame": self._frame_count,
                    "tick_count": new_state.tick,
                    "active_nodes": len(active_nodes),
                    "frontier_nodes": len(frontier_nodes),
                    "total_energy": total_e,
                    "average_energy": avg_e,
                    "active_count": active_count,
                }
                self.telemetry_port.publish(ENGINE_FRAME_COMPLETE_EVENT, telemetry_payload)
                telemetry_emitted = True
                logger.debug("[FrameOrchestrator] Telemetry emitted")
            except Exception as e:
                logger.warning(f"[FrameOrchestrator] Telemetry emission failed: {e}")

        # Step 6: Return frame result with new state
        return FrameResult(
            state=new_state,
            active_nodes=active_nodes,
            frontier_nodes=frontier_nodes,
            total_energy=total_e,
            average_energy=avg_e,
            telemetry_emitted=telemetry_emitted,
            persistence_saved=persistence_saved,
        )

    def execute_frames(
        self,
        state: EngineState,
        num_frames: int,
        *,
        activation_threshold: float = 0.5,
        emit_telemetry: bool = True,
        persist_every_n: int = 0,
    ) -> FrameResult:
        """
        Execute multiple consciousness frames sequentially.

        Args:
            state: Initial engine state
            num_frames: Number of frames to execute
            activation_threshold: Minimum energy for activation
            emit_telemetry: Whether to emit telemetry per frame
            persist_every_n: Persist state every N frames (0 = never)

        Returns:
            FrameResult from final frame
        """
        current_state = state
        result = None

        for i in range(num_frames):
            persist_this_frame = (persist_every_n > 0 and (i + 1) % persist_every_n == 0)

            result = self.execute_frame(
                current_state,
                stimuli=None,
                activation_threshold=activation_threshold,
                emit_telemetry=emit_telemetry,
                persist_state=persist_this_frame,
            )

            current_state = result.state

        return result

    def reset_frame_count(self) -> None:
        """Reset internal frame counter (useful for testing)."""
        self._frame_count = 0
