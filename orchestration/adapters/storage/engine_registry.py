"""
Engine Registry - Centralized access to consciousness engines

Provides a singleton registry for ConsciousnessEngineV2 instances,
allowing both websocket_server (at boot) and control_api (for injection)
to access the same engine references.

Usage:
    # At engine startup (websocket_server.py):
    from orchestration.adapters.storage.engine_registry import register_engine
    register_engine(engine.config.entity_id, engine)

    # From control API:
    from orchestration.adapters.storage.engine_registry import get_engine
    engine = get_engine("victor")
    if engine:
        await engine.inject_stimulus_async(...)

Author: Victor "The Resurrector" (Infrastructure)
Date: 2025-10-25
"""

from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# Global registry: citizen_id -> ConsciousnessEngineV2 instance
_ENGINES: Dict[str, 'ConsciousnessEngineV2'] = {}

# Task registry: citizen_id -> asyncio.Task (for lifecycle management)
CONSCIOUSNESS_TASKS: Dict[str, 'asyncio.Task'] = {}

# Legacy alias for backward compatibility
CONSCIOUSNESS_ENGINES = _ENGINES  # Legacy name used by websocket_server


def register_engine(citizen_id: str, engine: 'ConsciousnessEngineV2') -> None:
    """
    Register a consciousness engine in the global registry.

    Args:
        citizen_id: Unique citizen identifier (e.g., "victor", "luca")
        engine: ConsciousnessEngineV2 instance

    Note:
        Overwrites existing registration for the same citizen_id.
        This is intentional for hot-reload scenarios.
    """
    if citizen_id in _ENGINES:
        logger.warning(f"[EngineRegistry] Overwriting existing engine for {citizen_id}")

    _ENGINES[citizen_id] = engine
    logger.info(f"[EngineRegistry] Registered engine: {citizen_id}")


def get_engine(citizen_id: str) -> Optional['ConsciousnessEngineV2']:
    """
    Retrieve a consciousness engine from the registry.

    Args:
        citizen_id: Unique citizen identifier

    Returns:
        ConsciousnessEngineV2 instance if registered, None otherwise
    """
    return _ENGINES.get(citizen_id)


def all_citizens() -> List[str]:
    """
    Get list of all registered citizen IDs.

    Returns:
        List of citizen identifiers currently in registry
    """
    return list(_ENGINES.keys())


def get_all_engines() -> Dict[str, 'ConsciousnessEngineV2']:
    """
    Get all registered engines (for backward compatibility).

    Returns:
        Dict mapping citizen_id to ConsciousnessEngineV2 instance
    """
    return _ENGINES.copy()


def unregister_engine(citizen_id: str) -> bool:
    """
    Remove an engine from the registry.

    Args:
        citizen_id: Unique citizen identifier

    Returns:
        True if engine was removed, False if not found
    """
    if citizen_id in _ENGINES:
        del _ENGINES[citizen_id]
        logger.info(f"[EngineRegistry] Unregistered engine: {citizen_id}")
        return True
    return False


def clear_registry() -> int:
    """
    Remove all engines from registry (for testing/shutdown).

    Returns:
        Number of engines removed
    """
    count = len(_ENGINES)
    _ENGINES.clear()
    logger.info(f"[EngineRegistry] Cleared {count} engines from registry")
    return count


# === Control Functions for ICE (Pause/Resume/Speed) ===


def pause_citizen(citizen_id: str) -> dict:
    """
    Freeze specific citizen's consciousness (tick_multiplier = 1e9).

    Args:
        citizen_id: Citizen identifier

    Returns:
        Status dict with citizen_id, status, tick_multiplier
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = 1e9
    logger.info(f"[EngineRegistry] Paused {citizen_id}")

    return {
        "status": "paused",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def resume_citizen(citizen_id: str) -> dict:
    """
    Resume specific citizen's consciousness (tick_multiplier = 1.0).

    Args:
        citizen_id: Citizen identifier

    Returns:
        Status dict with citizen_id, status, tick_multiplier
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = 1.0
    logger.info(f"[EngineRegistry] Resumed {citizen_id}")

    return {
        "status": "resumed",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def set_citizen_speed(citizen_id: str, multiplier: float) -> dict:
    """
    Set consciousness speed multiplier for specific citizen.

    Args:
        citizen_id: Citizen identifier
        multiplier: Speed multiplier (1.0 = normal, >1 = slower, <1 = faster, 1e9 = frozen)

    Returns:
        Status dict with citizen_id, status, tick_multiplier
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {"status": "error", "message": f"Engine not found: {citizen_id}"}

    engine.tick_multiplier = multiplier
    logger.info(f"[EngineRegistry] Set speed for {citizen_id}: {multiplier}x")

    return {
        "status": "speed_set",
        "citizen_id": citizen_id,
        "tick_multiplier": engine.tick_multiplier
    }


def pause_all() -> dict:
    """
    Pause all registered consciousness engines.

    Returns:
        Status dict with count and list of paused citizens
    """
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
    """
    Resume all registered consciousness engines.

    Returns:
        Status dict with count and list of resumed citizens
    """
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
    """
    Get status of all consciousness engines.

    Returns:
        System-wide status with engine details
    """
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
