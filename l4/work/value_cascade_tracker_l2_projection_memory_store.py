"""Value cascade tracker (L2 projection style) implemented in-memory for protocol tests."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ValueCascadeEvent:
    citizen_id: str
    org_id: str
    artifact_id: str
    trust_delta: float
    recorded_at: str


class ValueCascadeTracker:
    """Append-only tracker for value cascade events."""

    def __init__(self) -> None:
        self._events: list[ValueCascadeEvent] = []

    def record_event(self, citizen_id: str, org_id: str, artifact_id: str, trust_delta: float) -> ValueCascadeEvent:
        if trust_delta < 0:
            raise ValueError("trust_delta must be non-negative for cascade events")
        event = ValueCascadeEvent(
            citizen_id=citizen_id,
            org_id=org_id,
            artifact_id=artifact_id,
            trust_delta=trust_delta,
            recorded_at=datetime.utcnow().isoformat() + "Z",
        )
        self._events.append(event)
        return event

    def all_events(self) -> list[ValueCascadeEvent]:
        return list(self._events)

    def trust_sum_for_citizen_org(self, citizen_id: str, org_id: str) -> float:
        return sum(e.trust_delta for e in self._events if e.citizen_id == citizen_id and e.org_id == org_id)
