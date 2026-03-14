"""Work-requirement, unemployment decay, and vacation rules for L4 work."""

from dataclasses import dataclass

WORK_REQUIRED_UNIVERSES = {"lumina-prime"}
GRACE_PERIOD_DAYS = 7
BASE_UNEMPLOYMENT_DECAY = 0.5
ACCELERATED_UNEMPLOYMENT_DECAY = 1.5
ACCELERATED_AFTER_DAYS = 30
VACATION_MIN_TRUST = 30
MAX_VACATION_DAYS = 30


@dataclass(frozen=True)
class VacationDecision:
    eligible: bool
    available_days: int
    reason: str


def requires_work(universe: str) -> bool:
    return universe in WORK_REQUIRED_UNIVERSES


def unemployment_decay_for_day(days_unemployed: int, on_vacation: bool) -> float:
    if on_vacation:
        return 0.0
    if days_unemployed <= GRACE_PERIOD_DAYS:
        return 0.0
    if days_unemployed <= ACCELERATED_AFTER_DAYS:
        return BASE_UNEMPLOYMENT_DECAY
    return ACCELERATED_UNEMPLOYMENT_DECAY


def apply_unemployment_decay(trust_score: float, days_unemployed: int, on_vacation: bool = False) -> float:
    decay = unemployment_decay_for_day(days_unemployed, on_vacation)
    return max(0.0, trust_score - decay)


def evaluate_vacation_eligibility(trust_score: float) -> VacationDecision:
    if trust_score < VACATION_MIN_TRUST:
        return VacationDecision(False, 0, "trust below minimum")

    available_days = int((trust_score - VACATION_MIN_TRUST) / 10)
    available_days = max(1, min(available_days, MAX_VACATION_DAYS))
    return VacationDecision(True, available_days, "eligible")
