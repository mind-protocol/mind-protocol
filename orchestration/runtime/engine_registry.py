"""
Engine Registry - Centralized Engine References

Provides centralized access to running consciousness engines for control API
and other services that need to interact with engines.

Architecture:
- Module-scope dict stores engine references
- Engines register themselves at bootstrap
- Control API retrieves engines by citizen_id for stimulus injection
- Thread-safe through asyncio (all access from async contexts)

Author: Iris "The Aperture"
Context: P0 ambient signal integration (queue → control API → engine)
Date: 2025-10-25
"""

from typing import Dict, Optional

# Import moved to TYPE_CHECKING to avoid circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2

# Module-scope engine registry
_ENGINES: Dict[str, 'ConsciousnessEngineV2'] = {}


def register_engine(citizen_id: str, engine: 'ConsciousnessEngineV2') -> None:
    """
    Register a consciousness engine.

    Called during engine bootstrap in websocket_server or launcher.

    Args:
        citizen_id: Unique identifier for this citizen (e.g., "felix", "iris")
        engine: ConsciousnessEngineV2 instance
    """
    _ENGINES[citizen_id] = engine


def get_engine(citizen_id: str) -> Optional['ConsciousnessEngineV2']:
    """
    Retrieve a consciousness engine by citizen ID.

    Used by control API to route stimulus injections to specific engines.

    Args:
        citizen_id: Citizen identifier

    Returns:
        ConsciousnessEngineV2 instance if registered, None otherwise
    """
    return _ENGINES.get(citizen_id)


def all_citizens() -> list[str]:
    """
    Get list of all registered citizen IDs.

    Returns:
        List of citizen_id strings for all running engines
    """
    return list(_ENGINES.keys())


def unregister_engine(citizen_id: str) -> None:
    """
    Remove engine from registry (cleanup on shutdown).

    Args:
        citizen_id: Citizen to unregister
    """
    _ENGINES.pop(citizen_id, None)


# === Control Functions for ICE (Pause/Resume/Speed) ===


def pause_citizen(citizen_id: str) -> dict:
    """Freeze specific citizen's consciousness (tick_multiplier = 1e9)."""
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = 1e9
    return {
        "status": "paused",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def resume_citizen(citizen_id: str) -> dict:
    """Resume specific citizen's consciousness (tick_multiplier = 1.0)."""
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = 1.0
    return {
        "status": "resumed",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def set_citizen_speed(citizen_id: str, multiplier: float) -> dict:
    """Set consciousness speed multiplier for specific citizen."""
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = multiplier
    return {
        "status": "speed_set",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def pause_all() -> dict:
    """Pause all registered consciousness engines."""
    paused = []
    for citizen_id in all_citizens():
        result = pause_citizen(citizen_id)
        if result["status"] == "paused":
            paused.append(citizen_id)

    return {
        "status": "all_paused",
        "count": len(paused),
        "paused_citizens": paused
    }


def resume_all() -> dict:
    """Resume all registered consciousness engines."""
    resumed = []
    for citizen_id in all_citizens():
        result = resume_citizen(citizen_id)
        if result["status"] == "resumed":
            resumed.append(citizen_id)

    return {
        "status": "all_resumed",
        "count": len(resumed),
        "resumed_citizens": resumed
    }


def get_system_status() -> dict:
    """Get status of all consciousness engines."""
    engines = {}
    frozen = 0
    running = 0
    slow_motion = 0

    for citizen_id in all_citizens():
        engine = get_engine(citizen_id)
        if engine:
            status = engine.get_status()
            engines[citizen_id] = status

            # Categorize by running state
            if status.get("tick_multiplier", 1.0) >= 1e9:
                frozen += 1
            elif status.get("tick_multiplier", 1.0) > 1.0:
                slow_motion += 1
            else:
                running += 1

    return {
        "total_engines": len(engines),
        "frozen": frozen,
        "running": running,
        "slow_motion": slow_motion,
        "engines": engines
    }


# Backward compatibility exports
CONSCIOUSNESS_ENGINES = _ENGINES
CONSCIOUSNESS_TASKS = _ENGINES


def get_all_engines() -> Dict[str, 'ConsciousnessEngineV2']:
    """Get all registered engines (backward compatibility)."""
    return _ENGINES.copy()
