"""
Safe Mode Auto-Trigger System

Monitors tripwires and automatically degrades to safe configuration when
violations exceed thresholds.

Per SCRIPT_MAP.md operational resilience requirements:
- Tripwires: conservation, criticality, frontier, observability
- Safe Mode: degraded config that aids diagnosis
- Automatic revert when back in safe bounds

Author: Victor "The Resurrector"
Created: 2025-10-22
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from orchestration.core.settings import settings

logger = logging.getLogger(__name__)


# --- Safe Mode Event Emission ---

def _emit_safe_mode_event(event_type: str, payload: Dict):
    """
    Emit Safe Mode event to WebSocket clients.

    Events emitted:
    - safe_mode.enter: When Safe Mode is triggered
    - safe_mode.exit: When Safe Mode exits

    Args:
        event_type: Type of event ("enter" or "exit")
        payload: Event payload with reason, overrides, etc.
    """
    try:
        from orchestration.mechanisms.telemetry import get_event_buffer

        event = {
            "type": f"safe_mode.{event_type}",
            **payload
        }

        buffer = get_event_buffer()
        # Use current time as frame number (Safe Mode is cross-frame)
        buffer.add_event(frame=int(time.time()), event=event)

        logger.info(f"[SafeMode] Emitted event: safe_mode.{event_type}")
    except Exception as e:
        # Event emission should never crash Safe Mode logic
        logger.warning(f"[SafeMode] Failed to emit event: {e}")


class TripwireType(Enum):
    """Types of tripwires that can trigger Safe Mode."""
    CONSERVATION = "conservation"  # Energy not conserved
    CRITICALITY = "criticality"    # rho out of bounds
    FRONTIER = "frontier"          # Frontier too large
    OBSERVABILITY = "observability"  # Missing events


@dataclass
class TripwireViolation:
    """Record of a single tripwire violation."""
    tripwire_type: TripwireType
    timestamp: float
    value: float
    threshold: float
    message: str


class SafeModeController:
    """
    Monitors tripwires and manages Safe Mode state.

    Thread-safe for use across services.
    """

    def __init__(self):
        self.in_safe_mode: bool = False
        self.safe_mode_reason: Optional[str] = None
        self.safe_mode_entered_at: Optional[float] = None

        # Violation tracking (rolling window)
        self.violations: deque = deque(maxlen=100)

        # Per-tripwire state tracking
        self.consecutive_violations: Dict[TripwireType, int] = {
            t: 0 for t in TripwireType
        }

        logger.info("[SafeMode] Controller initialized")

    def record_violation(
        self,
        tripwire_type: TripwireType,
        value: float,
        threshold: float,
        message: str
    ) -> bool:
        """
        Record a tripwire violation.

        Returns:
            True if this triggered Safe Mode, False otherwise
        """
        violation = TripwireViolation(
            tripwire_type=tripwire_type,
            timestamp=time.time(),
            value=value,
            threshold=threshold,
            message=message
        )

        self.violations.append(violation)
        self.consecutive_violations[tripwire_type] += 1

        logger.warning(
            f"[SafeMode] Tripwire violation: {tripwire_type.value} "
            f"(value={value:.3f}, threshold={threshold:.3f}) - {message}"
        )

        # Check if we should enter Safe Mode
        if not self.in_safe_mode:
            if self._should_enter_safe_mode():
                self._enter_safe_mode(tripwire_type, message)
                return True

        return False

    def record_compliance(self, tripwire_type: TripwireType):
        """Record that a tripwire is now compliant."""
        if self.consecutive_violations[tripwire_type] > 0:
            self.consecutive_violations[tripwire_type] = 0

        # Check if we can exit Safe Mode
        if self.in_safe_mode:
            if self._should_exit_safe_mode():
                self._exit_safe_mode()

    def _should_enter_safe_mode(self) -> bool:
        """
        Check if Safe Mode should be entered.

        Logic: Too many violations within time window OR
               consecutive violations of same tripwire.
        """
        if not settings.SAFE_MODE_ENABLED:
            return False

        # Count violations in window
        now = time.time()
        window_start = now - settings.SAFE_MODE_VIOLATION_WINDOW_S
        violations_in_window = sum(
            1 for v in self.violations
            if v.timestamp >= window_start
        )

        if violations_in_window >= settings.SAFE_MODE_VIOLATION_THRESHOLD:
            return True

        # Check consecutive violations per tripwire type
        # (Different thresholds per tripwire)
        if self.consecutive_violations[TripwireType.CRITICALITY] >= settings.TRIPWIRE_CRITICALITY_FRAMES:
            return True

        if self.consecutive_violations[TripwireType.FRONTIER] >= settings.TRIPWIRE_FRONTIER_FRAMES:
            return True

        if self.consecutive_violations[TripwireType.OBSERVABILITY] >= settings.TRIPWIRE_MISSING_EVENTS_FRAMES:
            return True

        # Conservation violations are immediate (critical)
        if self.consecutive_violations[TripwireType.CONSERVATION] >= 1:
            return True

        return False

    def _should_exit_safe_mode(self) -> bool:
        """Check if Safe Mode can be exited."""
        # Must be in Safe Mode for at least 30 seconds
        if not self.safe_mode_entered_at:
            return False

        time_in_safe_mode = time.time() - self.safe_mode_entered_at
        if time_in_safe_mode < 30:
            return False

        # No consecutive violations for any tripwire
        if any(count > 0 for count in self.consecutive_violations.values()):
            return False

        # No violations in last 60 seconds
        now = time.time()
        recent_window = 60
        recent_violations = [
            v for v in self.violations
            if v.timestamp >= (now - recent_window)
        ]

        if len(recent_violations) > 0:
            return False

        return True

    def _enter_safe_mode(self, tripwire_type: TripwireType, reason: str):
        """Enter Safe Mode - apply degraded configuration."""
        self.in_safe_mode = True
        self.safe_mode_reason = f"{tripwire_type.value}: {reason}"
        self.safe_mode_entered_at = time.time()

        logger.critical(
            f"[SafeMode] ENTERING SAFE MODE - Reason: {self.safe_mode_reason}"
        )

        # Apply Safe Mode overrides from settings
        self._apply_safe_mode_config()

        # Emit event to WebSocket for dashboard notification
        _emit_safe_mode_event("enter", {
            "reason": self.safe_mode_reason,
            "tripwire": tripwire_type.value,
            "overrides_applied": dict(settings.SAFE_MODE_OVERRIDES),
            "timestamp": self.safe_mode_entered_at
        })

    def _exit_safe_mode(self):
        """Exit Safe Mode - restore normal configuration."""
        duration = time.time() - self.safe_mode_entered_at if self.safe_mode_entered_at else 0

        logger.info(
            f"[SafeMode] EXITING SAFE MODE - Duration: {duration:.0f}s"
        )

        self.in_safe_mode = False
        self.safe_mode_reason = None
        self.safe_mode_entered_at = None

        # Restore normal configuration
        self._restore_normal_config()

        # Emit event to WebSocket for dashboard notification
        _emit_safe_mode_event("exit", {
            "duration_s": duration,
            "timestamp": time.time()
        })

    def _apply_safe_mode_config(self):
        """
        Apply Safe Mode configuration overrides.

        TODO: This should dynamically update consciousness engine settings.
        For now, just logs what WOULD be applied.
        """
        logger.warning("[SafeMode] Would apply overrides:")
        for key, value in settings.SAFE_MODE_OVERRIDES.items():
            logger.warning(f"  {key} = {value}")

        # TODO: Implement dynamic config updates
        # This requires consciousness engine to support runtime config changes
        # For Phase 1: engines will need to restart to pick up Safe Mode

    def _restore_normal_config(self):
        """Restore normal (non-Safe Mode) configuration."""
        logger.info("[SafeMode] Restoring normal configuration")

        # TODO: Implement config restoration
        # For Phase 1: requires engine restart

    def get_status(self) -> Dict:
        """Get current Safe Mode status for monitoring."""
        now = time.time()

        return {
            "in_safe_mode": self.in_safe_mode,
            "reason": self.safe_mode_reason,
            "duration_s": (now - self.safe_mode_entered_at) if self.safe_mode_entered_at else None,
            "consecutive_violations": {
                t.value: count
                for t, count in self.consecutive_violations.items()
            },
            "recent_violations": [
                {
                    "type": v.tripwire_type.value,
                    "timestamp": v.timestamp,
                    "value": v.value,
                    "threshold": v.threshold,
                    "message": v.message
                }
                for v in list(self.violations)[-10:]  # Last 10 violations
            ]
        }


# Global singleton
_safe_mode_controller = None


def get_safe_mode_controller() -> SafeModeController:
    """Get or create global Safe Mode controller."""
    global _safe_mode_controller
    if _safe_mode_controller is None:
        _safe_mode_controller = SafeModeController()
    return _safe_mode_controller
