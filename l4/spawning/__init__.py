# DOCS: docs/citizen/spawning/IMPLEMENTATION_Spawning.md
"""Citizen spawning pipeline — intent-based creation with safety gates."""

from .citizen_spawning_pipeline_with_safety_gates import (
    SpawnRequest,
    ParentIntent,
    SpawnResult,
    SafetyResult,
    SeedBrain,
    spawn_citizen,
)

__all__ = [
    "SpawnRequest",
    "ParentIntent",
    "SpawnResult",
    "SafetyResult",
    "SeedBrain",
    "spawn_citizen",
]
