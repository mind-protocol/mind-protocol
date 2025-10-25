"""
Engine Registry - Centralized Consciousness Engine References

Provides singleton registry for accessing running consciousness engines across services.

Architecture:
- websocket_server registers engines at boot
- control_api accesses engines for stimulus injection
- Thread-safe for concurrent access

Designer: Nicolas (blueprint), Felix (implementation)
Date: 2025-10-25
Purpose: P0 - Enable queue→engine stimulus injection (critical path to autonomy)
"""

from typing import Dict, Optional
from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2

# Global engine registry
_ENGINES: Dict[str, ConsciousnessEngineV2] = {}


def register_engine(citizen_id: str, engine: ConsciousnessEngineV2) -> None:
    """
    Register a consciousness engine for access by control services.

    Called by websocket_server when engines boot.

    Args:
        citizen_id: Citizen identifier (e.g., 'felix', 'luca', 'mind_protocol')
        engine: Running consciousness engine instance
    """
    _ENGINES[citizen_id] = engine


def get_engine(citizen_id: str) -> Optional[ConsciousnessEngineV2]:
    """
    Get running engine by citizen ID.

    Used by control_api for stimulus injection.

    Args:
        citizen_id: Citizen identifier

    Returns:
        Engine instance if registered, None otherwise
    """
    return _ENGINES.get(citizen_id)


def all_citizens() -> list[str]:
    """
    Get list of all registered citizen IDs.

    Returns:
        List of citizen identifiers
    """
    return list(_ENGINES.keys())
