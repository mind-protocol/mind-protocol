"""
Mechanisms package - pure mechanism implementations.

Each mechanism is implemented as isolated, testable pure functions.
Mechanisms operate on core data structures (Node, Link, Graph) but
don't depend on services or orchestration.

Available Mechanisms:
- multi_energy: M01 - Multi-subentity energy storage and manipulation
- bitemporal: M13 - Temporal tracking and queries
- diffusion: M07 - Row-stochastic conservative energy redistribution
- decay: M08 - Exponential forgetting with type-dependent rates
- strengthening: M09 - Bounded Hebbian link learning
- threshold: M16 Part 1 - Adaptive activation threshold
- criticality: M03 - Self-organized criticality (spectral radius control)
- context_reconstruction: M02 - Emergent pattern reconstruction
- incomplete_node_healing: M18 - Schema validation and eligibility filtering
- tick_speed: M10 - Stimulus-adaptive scheduling with dt capping

Author: Felix (Engineer)
Created: 2025-10-19
Architecture: Phase 1+2 Clean Break
"""

from . import multi_energy
from . import bitemporal
# Note: diffusion is split into diffusion_runtime and diffusion_matrix_archive
from . import decay
from . import strengthening
from . import threshold
from . import criticality
from . import context_reconstruction
from . import incomplete_node_healing
from . import tick_speed
from . import relationship_classification

__all__ = ['multi_energy', 'bitemporal', 'decay', 'strengthening', 'threshold', 'criticality', 'context_reconstruction', 'incomplete_node_healing', 'tick_speed', 'relationship_classification']
