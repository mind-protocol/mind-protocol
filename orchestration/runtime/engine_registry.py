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
