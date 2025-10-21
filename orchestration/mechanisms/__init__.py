"""
Mechanisms package - pure mechanism implementations.

Each mechanism is implemented as isolated, testable pure functions.
Mechanisms operate on core data structures (Node, Link, Graph) but
don't depend on services or orchestration.

Available Mechanisms:
- multi_energy: M01 - Multi-entity energy storage and manipulation
- bitemporal: M13 - Temporal tracking and queries
- diffusion: M07 - Row-stochastic conservative energy redistribution
- decay: M08 - Exponential forgetting with type-dependent rates
- strengthening: M09 - Bounded Hebbian link learning
- threshold: M16 Part 1 - Adaptive activation threshold

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1+2 Clean Break
"""

from . import multi_energy
from . import bitemporal
from . import diffusion
from . import decay
from . import strengthening
from . import threshold

__all__ = ['multi_energy', 'bitemporal', 'diffusion', 'decay', 'strengthening', 'threshold']
