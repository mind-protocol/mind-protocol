"""Intent planning services for the engine façade."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Tuple

from consciousness.engine.domain.state import EngineState
from libs.law import implements


@dataclass(frozen=True)
class SchedulerDecision:
    """Result from planning a tick transition."""

    state: EngineState
    intents: Tuple[Mapping[str, Any], ...]


@implements("Mechanism:ENGINE_SCHEDULER", "Suite:GODFILE-1.0/A2")
def plan_next_tick(
    state: EngineState,
    stimuli: Optional[Sequence[Mapping[str, Any]]] = None,
    *,
    high_energy_threshold: float = 0.85,
) -> SchedulerDecision:
    """Plan intents for the next engine tick."""

    del stimuli  # Reserved for future stimulus-driven branching
    intents = []
    if state.normalized_energy >= high_energy_threshold:
        intents.append(
            {
                "type": "telemetry.emit",
                "payload": {
                    "event": "engine.alert.high_energy",
                    "data": {
                        "entity_id": state.entity_id,
                        "tick": state.tick,
                        "normalized_energy": state.normalized_energy,
                        "global_energy": state.global_energy,
                    },
                },
            }
        )

    return SchedulerDecision(state=state, intents=tuple(intents))
