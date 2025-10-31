"""Intent planning router."""
from __future__ import annotations

from fastapi import APIRouter

from adapters.api.routers.shared import resolve_engine_facade, to_state_model
from adapters.api.schemas.tasks import IntentModel, PlanResponse


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/{citizen_id}/plan", response_model=PlanResponse)
def plan_tasks(citizen_id: str) -> PlanResponse:
    engine = resolve_engine_facade(citizen_id)
    decision = engine.plan_tick()
    return PlanResponse(
        state=to_state_model(decision.state),
        intents=[IntentModel(type=str(intent.get("type", "")), payload=dict(intent.get("payload", {}))) for intent in decision.intents],
    )


@router.post("/{citizen_id}/dispatch", response_model=PlanResponse)
def plan_and_dispatch(citizen_id: str) -> PlanResponse:
    engine = resolve_engine_facade(citizen_id)
    decision = engine.plan_tick()
    engine.dispatch_intents(decision.intents)
    return PlanResponse(
        state=to_state_model(decision.state),
        intents=[IntentModel(type=str(intent.get("type", "")), payload=dict(intent.get("payload", {}))) for intent in decision.intents],
    )
