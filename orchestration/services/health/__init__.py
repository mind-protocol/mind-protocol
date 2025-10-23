"""
Health monitoring and self-test system.

Provides fail-loud observability per operational resilience requirements.
"""

from .health_checks import (
    HealthStatus,
    HealthCheckResult,
    ServiceHealthChecker,
    StartupSelfTests,
    create_health_check_summary
)
from .safe_mode import (
    SafeModeController,
    TripwireType,
    TripwireViolation,
    get_safe_mode_controller
)

__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "ServiceHealthChecker",
    "StartupSelfTests",
    "create_health_check_summary",
    "SafeModeController",
    "TripwireType",
    "TripwireViolation",
    "get_safe_mode_controller"
]
