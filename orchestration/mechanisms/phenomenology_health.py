"""
Phenomenological Health Assessment

Translates quantitative consciousness metrics (entity energies, coherence)
into qualitative phenomenological states for operator visibility.

Design: Entropy-based fragmentation + state classification with hysteresis
Owner: Felix (refined by Nicolas)
Created: 2025-10-25 (P2.1 Emitter Implementation)
"""

from math import log
from dataclasses import dataclass
from typing import Literal, Sequence


State = Literal["dormant", "coherent", "multiplicitous", "fragmented"]


@dataclass
class HealthComponents:
    """
    Composite health metrics for dashboard sub-meters.

    - flow: How well attention moves forward (0=stuck, 1=flowing)
    - coherence: Inverse of fragmentation (0=scattered, 1=unified)
    - multiplicity: Productive tension vs conflict (0=conflict, 1=synergy)
    """
    flow: float           # 0..1
    coherence: float      # 0..1
    multiplicity: float   # 0..1


@dataclass
class HealthResult:
    """
    Phenomenological health classification result.

    - state: Qualitative narrative state (dormant/coherent/multiplicitous/fragmented)
    - fragmentation: Quantitative entropy-based score (0=unified, 1=scattered)
    - cause: Operator-friendly short explanation
    - components: Decomposed metrics for dashboard
    """
    state: State
    fragmentation: float
    cause: str
    components: HealthComponents


def _active_entities(subentities: Sequence) -> list:
    """
    Filter subentities to those currently active (E >= theta).

    Subentity objects must have:
    - energy_runtime: Current energy level
    - threshold_runtime: Activation threshold
    - OR is_active() method
    """
    active = []
    for e in subentities:
        # Try is_active() method first, fallback to direct comparison
        if hasattr(e, 'is_active') and callable(e.is_active):
            if e.is_active():
                active.append(e)
        else:
            # Fallback to direct attribute comparison
            E = getattr(e, 'energy_runtime', 0.0)
            theta = getattr(e, 'threshold_runtime', 0.0)
            if E >= theta:
                active.append(e)
    return active


def _entropy(xs: list) -> float:
    """
    Compute Shannon entropy of energy distribution.

    Returns H = -Σ(p_i * log(p_i)) where p_i = x_i / sum(x)
    Guards against log(0) and sum=0 cases.
    """
    s = sum(xs)
    if s <= 0:
        return 0.0

    h = 0.0
    for x in xs:
        if x <= 0:
            continue
        p = x / s
        h -= p * log(p)

    return h


def classify(subentities: Sequence) -> HealthResult:
    """
    Classify consciousness phenomenological health from entity activation patterns.

    Classification logic:
    - 0 active: dormant (no entities above threshold)
    - 1 active: coherent (single dominant narrative)
    - 2-3 active: multiplicitous (productive tension, entropy-based fragmentation)
    - 4+ active: fragmented (attention scattered, fragmentation=1.0)

    Returns HealthResult with state, fragmentation score, cause, and components.
    """
    act = _active_entities(subentities)
    k = len(act)

    # === DORMANT: No active entities ===
    if k == 0:
        comps = HealthComponents(flow=0.2, coherence=1.0, multiplicity=0.0)
        return HealthResult(
            state="dormant",
            fragmentation=0.0,
            cause="No entities above threshold",
            components=comps
        )

    # === COHERENT: Single dominant entity ===
    if k == 1:
        ent = act[0]
        entity_name = getattr(ent, 'id', '(unknown)')
        comps = HealthComponents(flow=0.8, coherence=1.0, multiplicity=0.2)
        return HealthResult(
            state="coherent",
            fragmentation=0.0,
            cause=f"Single entity dominant: {entity_name}",
            components=comps
        )

    # === MULTIPLICITOUS or FRAGMENTED: Multiple active entities ===

    # Extract energies and compute normalized entropy
    energies = [max(0.0, getattr(e, 'energy_runtime', 0.0)) for e in act]
    H = _entropy(energies)
    Hmax = log(k) if k > 0 else 1.0
    frag = min(1.0, H / Hmax) if Hmax > 0 else 0.0

    # === MULTIPLICITOUS: 2-3 active (productive tension) ===
    if k <= 3:
        # Compute balance proxy: high entropy among few = healthy multiplicity
        # Cheap proxy: distance of max energy index from center
        max_idx = energies.index(max(energies)) if max(energies) > 0 else 0
        center = (k - 1) / 2.0
        balance = 1.0 - abs(max_idx - center) / max(center, 1.0)
        multiplicity = min(1.0, max(0.0, balance))

        comps = HealthComponents(
            flow=0.7,
            coherence=1.0 - frag,
            multiplicity=multiplicity
        )

        entity_names = [getattr(e, 'id', '(unknown)') for e in act]
        return HealthResult(
            state="multiplicitous",
            fragmentation=frag,
            cause=f"{k} entities active: {', '.join(entity_names)}",
            components=comps
        )

    # === FRAGMENTED: 4+ active (attention scattered) ===
    entity_names = [getattr(e, 'id', '(unknown)') for e in act[:3]]  # First 3 names
    cause = f"{k} entities competing: {', '.join(entity_names)}... - attention scattered"

    comps = HealthComponents(flow=0.4, coherence=0.2, multiplicity=0.3)

    return HealthResult(
        state="fragmented",
        fragmentation=1.0,  # Always 1.0 for fragmented state
        cause=cause,
        components=comps
    )


# Legacy compatibility - provide compute_phenomenological_health wrapper
def compute_phenomenological_health(graph):
    """
    Legacy compatibility wrapper for classify().

    Returns tuple format: (state, fragmentation, cause, active_entities_data)
    """
    if not hasattr(graph, 'subentities') or not graph.subentities:
        return "dormant", 0.0, "No subentities in graph", []

    result = classify(graph.subentities.values())

    # Build active entities data for legacy format
    active_entities = []
    for entity in graph.subentities.values():
        if entity.is_active():
            active_entities.append({
                'id': entity.id,
                'name': entity.id,
                'energy': round(entity.energy_runtime, 4),
                'threshold': round(entity.threshold_runtime, 4),
                'member_count': len(entity.extent) if hasattr(entity, 'extent') else 0
            })

    return result.state, result.fragmentation, result.cause, active_entities
