"""Health dashboard primitives for citizen-work module signals."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkHealthSnapshot:
    open_positions: int
    filled_positions: int
    timeout_calls: int
    successful_calls: int
    unemployed_lumina_prime: int
    citizens_on_vacation: int


@dataclass(frozen=True)
class WorkHealthReport:
    fill_rate: float
    call_success_rate: float
    unemployment_pressure: float
    vacation_coverage: float
    status: str


def build_work_health_report(snapshot: WorkHealthSnapshot) -> WorkHealthReport:
    total_positions = snapshot.open_positions + snapshot.filled_positions
    fill_rate = (snapshot.filled_positions / total_positions) if total_positions > 0 else 1.0

    total_calls = snapshot.timeout_calls + snapshot.successful_calls
    call_success_rate = (snapshot.successful_calls / total_calls) if total_calls > 0 else 1.0

    employment_base = snapshot.unemployed_lumina_prime + snapshot.filled_positions
    unemployment_pressure = (
        snapshot.unemployed_lumina_prime / employment_base if employment_base > 0 else 0.0
    )

    active_population = snapshot.citizens_on_vacation + snapshot.filled_positions
    vacation_coverage = (
        snapshot.citizens_on_vacation / active_population if active_population > 0 else 0.0
    )

    if fill_rate < 0.4 or call_success_rate < 0.4:
        status = "critical"
    elif fill_rate < 0.7 or call_success_rate < 0.7:
        status = "warning"
    else:
        status = "healthy"

    return WorkHealthReport(
        fill_rate=fill_rate,
        call_success_rate=call_success_rate,
        unemployment_pressure=unemployment_pressure,
        vacation_coverage=vacation_coverage,
        status=status,
    )
