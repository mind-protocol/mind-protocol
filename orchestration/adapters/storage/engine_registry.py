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
