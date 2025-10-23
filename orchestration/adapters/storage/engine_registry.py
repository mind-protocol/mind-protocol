"""
Global Consciousness Engine Registry

Provides centralized control over all running consciousness engines.
Enables per-citizen and global pause/resume/speed control.

Implementation: Async task management - creates/cancels asyncio tasks for engines.

Usage:
    from orchestration.adapters.storage.engine_registry import register_engine, pause_citizen, pause_all

    # Register engine when starting
    register_engine("felix-engineer", engine)

    # Control from anywhere
    pause_citizen("felix-engineer")  # Freeze Felix
    resume_citizen("ada-architect")   # Resume Ada
    pause_all()                       # Emergency freeze all
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Global registry of all running consciousness engines
# Key: citizen_id (e.g., "felix", "ada", "luca")
# Value: ConsciousnessEngine instance
CONSCIOUSNESS_ENGINES: Dict[str, Any] = {}

# Global registry of async tasks running engine.run()
# Key: citizen_id
# Value: asyncio.Task
CONSCIOUSNESS_TASKS: Dict[str, asyncio.Task] = {}


def register_engine(citizen_id: str, engine: Any):
    """
    Register a consciousness engine for centralized control.

    Args:
        citizen_id: Unique citizen identifier
        engine: ConsciousnessEngine instance
    """
    CONSCIOUSNESS_ENGINES[citizen_id] = engine
    logger.info(f"[EngineRegistry] Registered: {citizen_id}")
    logger.info(f"  Total engines: {len(CONSCIOUSNESS_ENGINES)}")


def unregister_engine(citizen_id: str):
    """
    Unregister a consciousness engine.

    Args:
        citizen_id: Citizen identifier to remove
    """
    if citizen_id in CONSCIOUSNESS_ENGINES:
        del CONSCIOUSNESS_ENGINES[citizen_id]
        logger.info(f"[EngineRegistry] Unregistered: {citizen_id}")
        logger.info(f"  Remaining engines: {len(CONSCIOUSNESS_ENGINES)}")


def get_engine(citizen_id: str) -> Optional[Any]:
    """
    Get engine by citizen ID.

    Args:
        citizen_id: Citizen identifier

    Returns:
        ConsciousnessEngine instance or None if not found
    """
    return CONSCIOUSNESS_ENGINES.get(citizen_id)


def get_all_engines() -> List[Any]:
    """
    Get all registered engines.

    Returns:
        List of all ConsciousnessEngine instances
    """
    return list(CONSCIOUSNESS_ENGINES.values())


def get_all_statuses() -> Dict[str, Dict]:
    """
    Get status of all engines.

    Returns:
        Dict mapping citizen_id to status dict
    """
    return {
        citizen_id: engine.get_status()
        for citizen_id, engine in CONSCIOUSNESS_ENGINES.items()
    }


# === Per-Citizen Control ===


def pause_citizen(citizen_id: str) -> Dict[str, Any]:
    """
    Pause a specific citizen's consciousness.

    Args:
        citizen_id: Citizen to pause

    Returns:
        Status dict with result
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {
            "status": "error",
            "message": f"Engine not found: {citizen_id}"
        }

    # Cancel async task if running
    if citizen_id in CONSCIOUSNESS_TASKS:
        task = CONSCIOUSNESS_TASKS[citizen_id]
        if not task.done():
            task.cancel()
            logger.info(f"[EngineRegistry] Cancelled task for {citizen_id}")
        del CONSCIOUSNESS_TASKS[citizen_id]

    # Set engine state
    engine.pause()

    return {
        "status": "paused",
        "citizen_id": citizen_id
    }


def resume_citizen(citizen_id: str) -> Dict[str, Any]:
    """
    Resume a specific citizen's consciousness.

    Creates an async task running engine.run() if not already running.

    Args:
        citizen_id: Citizen to resume

    Returns:
        Status dict with result
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {
            "status": "error",
            "message": f"Engine not found: {citizen_id}"
        }

    # Set engine state
    engine.resume()

    # Create async task if not already running
    if citizen_id not in CONSCIOUSNESS_TASKS or CONSCIOUSNESS_TASKS[citizen_id].done():
        task = asyncio.create_task(engine.run(), name=f"resumed:{citizen_id}")
        CONSCIOUSNESS_TASKS[citizen_id] = task
        logger.info(f"[EngineRegistry] Created task for {citizen_id}")

    return {
        "status": "resumed",
        "citizen_id": citizen_id,
        "task_running": citizen_id in CONSCIOUSNESS_TASKS
    }


def set_citizen_speed(citizen_id: str, multiplier: float) -> Dict[str, Any]:
    """
    Set consciousness speed for debugging/observation.

    Args:
        citizen_id: Citizen to control
        multiplier: Speed multiplier
            - 1.0 = normal
            - 10 = 10x slower (debug)
            - 0.1 = 10x faster (testing)
            - 1e9 = frozen

    Returns:
        Status dict with result
    """
    engine = get_engine(citizen_id)
    if not engine:
        return {
            "status": "error",
            "message": f"Engine not found: {citizen_id}"
        }

    engine.slow_motion(multiplier)

    return {
        "status": "speed_set",
        "citizen_id": citizen_id,
        "tick_multiplier": multiplier
    }


# === Global Control ===


def pause_all() -> Dict[str, Any]:
    """
    Emergency freeze ALL consciousness engines.

    Sets all engines to tick_multiplier = 1e9 (frozen).
    Use when system needs immediate halt.

    Returns:
        Status dict with count of paused engines
    """
    logger.warning("⚠️ PAUSE ALL - Freezing all consciousness engines")

    paused = []
    for citizen_id, engine in CONSCIOUSNESS_ENGINES.items():
        engine.pause()
        paused.append(citizen_id)

    return {
        "status": "all_paused",
        "count": len(paused),
        "paused_citizens": paused
    }


def resume_all() -> Dict[str, Any]:
    """
    Resume ALL consciousness engines.

    Resets all engines to tick_multiplier = 1.0 (normal).

    Returns:
        Status dict with count of resumed engines
    """
    logger.info("▶️ RESUME ALL - Restoring all consciousness engines")

    resumed = []
    for citizen_id, engine in CONSCIOUSNESS_ENGINES.items():
        engine.resume()
        resumed.append(citizen_id)

    return {
        "status": "all_resumed",
        "count": len(resumed),
        "resumed_citizens": resumed
    }


def get_system_status() -> Dict[str, Any]:
    """
    Get complete system status.

    Returns:
        System-wide status including all engines
    """
    statuses = get_all_statuses()

    # Count by state
    frozen_count = sum(1 for s in statuses.values() if s["running_state"] == "frozen")
    running_count = sum(1 for s in statuses.values() if s["running_state"] == "running")
    slow_count = sum(1 for s in statuses.values() if s["running_state"] == "slow_motion")

    return {
        "total_engines": len(statuses),
        "frozen": frozen_count,
        "running": running_count,
        "slow_motion": slow_count,
        "engines": statuses
    }
