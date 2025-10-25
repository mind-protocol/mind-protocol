"""
Phenomenological Health Assessment

Translates quantitative consciousness metrics (entity energies, coherence)
into qualitative phenomenological states for operator visibility.

Owner: Felix
Created: 2025-10-25 (P2.1 Emitter Implementation)
"""

import math
from typing import Dict, Tuple, List, Optional
from orchestration.core.graph import Graph


def compute_phenomenological_health(graph: Graph) -> Tuple[str, float, str, List[Dict]]:
    """
    Assess phenomenological health state from entity activation patterns.

    Returns qualitative state (coherent/multiplicitous/fragmented/dormant)
    based on number of active entities and energy distribution.

    Args:
        graph: Consciousness graph with subentities

    Returns:
        Tuple of (narrative_state, fragmentation_score, cause, active_entities_data)

        - narrative_state: "coherent" | "multiplicitous" | "fragmented" | "dormant"
        - fragmentation_score: 0.0 (coherent) to 1.0 (fragmented)
        - cause: Human-readable explanation
        - active_entities_data: List of dicts with entity details

    Phenomenological Classification:
    - Dormant: No entities active (E < theta)
    - Coherent: Single entity dominant, clear narrative
    - Multiplicitous: 2-3 entities active, productive tension
    - Fragmented: 4+ entities competing, attention scattered
    """

    # Handle missing subentities gracefully
    if not hasattr(graph, 'subentities') or not graph.subentities:
        return "dormant", 0.0, "No subentities in graph", []

    # Identify active entities (E >= theta)
    active_entities = []
    for entity in graph.subentities.values():
        if entity.is_active():
            active_entities.append({
                'id': entity.id,
                'name': entity.role_or_topic if hasattr(entity, 'role_or_topic') else entity.id,
                'energy': round(entity.energy_runtime, 4),
                'threshold': round(entity.threshold_runtime, 4),
                'member_count': len(entity.extent) if hasattr(entity, 'extent') else 0
            })

    num_active = len(active_entities)

    # === Classification Logic ===

    # DORMANT: No active entities
    if num_active == 0:
        return "dormant", 0.0, "No entities above activation threshold", []

    # COHERENT: Single dominant entity
    if num_active == 1:
        dominant = active_entities[0]
        cause = f"Single entity dominant: {dominant['name']} (E={dominant['energy']:.3f})"
        return "coherent", 0.0, cause, active_entities

    # MULTIPLICITOUS or FRAGMENTED: Multiple active entities
    # Compute energy entropy as fragmentation metric
    energies = [e['energy'] for e in active_entities]
    total_E = sum(energies)

    # Shannon entropy of energy distribution
    if total_E > 0:
        entropy = 0.0
        for E in energies:
            if E > 0:
                p = E / total_E
                entropy -= p * math.log(p)

        # Normalize by maximum possible entropy (uniform distribution)
        max_entropy = math.log(num_active) if num_active > 1 else 1.0
        fragmentation_score = entropy / max_entropy if max_entropy > 0 else 0.0
    else:
        fragmentation_score = 0.0

    # MULTIPLICITOUS: 2-3 active entities (productive tension)
    if num_active <= 3:
        entity_names = [e['name'] for e in active_entities]
        cause = f"{num_active} entities active: {', '.join(entity_names)} (entropy={fragmentation_score:.2f})"
        return "multiplicitous", fragmentation_score, cause, active_entities

    # FRAGMENTED: 4+ active entities (attention scattered)
    entity_names = [e['name'] for e in active_entities]
    cause = f"{num_active} entities competing: {', '.join(entity_names[:3])}... - attention scattered"
    return "fragmented", fragmentation_score, cause, active_entities


def compute_coherence_fragmentation(graph: Graph) -> Optional[float]:
    """
    Compute global coherence score from entity coherence EMAs.

    Returns weighted average of entity coherence values, or None if unavailable.

    Args:
        graph: Consciousness graph with subentities

    Returns:
        Global coherence score (0.0 to 1.0), or None if no coherence data
    """

    if not hasattr(graph, 'subentities') or not graph.subentities:
        return None

    coherence_values = []
    weights = []

    for entity in graph.subentities.values():
        if hasattr(entity, 'coherence_ema') and entity.coherence_ema is not None:
            coherence_values.append(entity.coherence_ema)
            # Weight by entity energy (more active entities contribute more)
            weights.append(entity.energy_runtime)

    if not coherence_values:
        return None

    total_weight = sum(weights)
    if total_weight == 0:
        return None

    # Weighted average
    global_coherence = sum(c * w for c, w in zip(coherence_values, weights)) / total_weight
    return round(global_coherence, 4)
