"""
Hamilton Quota Allocation with Per-Frame Normalization

Implements fair stride budget distribution across entities using:
- Inverse-size weighting (small entities get more strides per node)
- Modulation factors (urgency, reachability, health)
- Hamilton's largest remainder method (unbiased integer allocation)
- Per-frame normalization (zero-constants compliance)

Author: AI #2
Created: 2025-10-20
Dependencies: sub_entity_core
Zero-Constants: All factors normalized to mean=1.0 per-frame
"""

from typing import List, Dict
from orchestration.mechanisms.sub_entity_core import SubEntity


def compute_modulation_factors(
    entities: List[SubEntity],
    graph,
    recent_stimuli
) -> Dict[str, Dict[str, float]]:
    """
    Compute urgency, reachability, health factors for each entity.

    All factors normalized to mean=1.0 across current active entities.

    Args:
        entities: Active sub-entities this frame
        graph: Graph object
        recent_stimuli: Recent stimulus history (list of dicts with 'embedding' key)

    Returns:
        Dict[entity_id -> {urgency, reachability, health}]
    """
    import numpy as np

    if not entities:
        return {}

    N = len(entities)
    factors = {}

    # === URGENCY: Cosine similarity to recent stimuli ===
    urgency_raw = {}
    for entity in entities:
        if not recent_stimuli or entity.centroid.n == 0:
            # No stimuli or empty extent → neutral urgency
            urgency_raw[entity.id] = 1.0
        else:
            # Max cosine similarity to recent stimuli
            max_sim = 0.0
            for stimulus in recent_stimuli:
                if 'embedding' in stimulus:
                    stim_emb = stimulus['embedding']
                    # Cosine similarity = 1 - distance
                    distance = entity.centroid.distance_to(stim_emb)
                    similarity = max(0.0, 1.0 - distance)  # Clamp to [0,1]
                    max_sim = max(max_sim, similarity)
            urgency_raw[entity.id] = max_sim

    # === REACHABILITY: Inverse distance to high-energy workspace nodes ===
    # Heuristic: Distance from extent centroid to workspace centroid
    # (Simplified version - full version would track actual workspace)
    reachability_raw = {}
    for entity in entities:
        if entity.centroid.n == 0:
            reachability_raw[entity.id] = 1.0
        else:
            # For Phase 1: assume all entities equally reachable
            # Phase 2+: Implement actual workspace distance
            reachability_raw[entity.id] = 1.0

    # === HEALTH: Inverse of local spectral radius ===
    health_raw = {}
    for entity in entities:
        # Lower rho = healthier = higher health factor
        # rho near 1.0 = edge of criticality (neutral health)
        # rho > 1.0 = unstable (low health)
        # rho < 1.0 = stable (high health)
        rho = entity.rho_local_ema
        if rho > 0.0:
            health_raw[entity.id] = 1.0 / rho
        else:
            health_raw[entity.id] = 1.0  # Degenerate case

    # === NORMALIZATION: Mean = 1.0 per factor ===
    def normalize_to_mean_one(raw_values: Dict[str, float]) -> Dict[str, float]:
        """Normalize so mean across entities = 1.0"""
        values = list(raw_values.values())
        if not values:
            return raw_values

        mean_val = np.mean(values)
        if mean_val <= 1e-9:
            # All values near zero - return uniform
            return {eid: 1.0 for eid in raw_values.keys()}

        return {eid: v / mean_val for eid, v in raw_values.items()}

    urgency_norm = normalize_to_mean_one(urgency_raw)
    reachability_norm = normalize_to_mean_one(reachability_raw)
    health_norm = normalize_to_mean_one(health_raw)

    # === OPTIONAL SHRINKAGE (commented out for Phase 1) ===
    # N_0 = N  # Shrinkage prior
    # urgency_shrunk = {eid: (N * u + N_0) / (N + N_0)
    #                   for eid, u in urgency_norm.items()}

    # === COMBINE FACTORS ===
    for entity in entities:
        factors[entity.id] = {
            'urgency': urgency_norm[entity.id],
            'reachability': reachability_norm[entity.id],
            'health': health_norm[entity.id]
        }

    return factors


def hamilton_quota_allocation(
    entities: List[SubEntity],
    Q_total: int,
    weights: Dict[str, float]
) -> Dict[str, int]:
    """
    Allocate integer quotas using Hamilton's largest remainder method.

    Prevents rounding bias that could systematically favor certain entities.

    Args:
        entities: Active sub-entities
        Q_total: Total stride budget for this frame
        weights: Per-entity allocation weights (already computed)

    Returns:
        Dict[entity_id -> quota_assigned]

    Algorithm:
        1. Compute fractional quotas: q_e_frac = Q_total × (w_e / Σw)
        2. Take integer parts: q_e_int = ⌊q_e_frac⌋
        3. Compute remainder: R = Q_total - Σq_e_int
        4. Sort entities by fractional remainder descending
        5. Give +1 to top R entities
    """
    import math

    # Edge case: no entities or no budget
    if not entities or Q_total <= 0:
        return {entity.id: 0 for entity in entities}

    # Step 1: Compute total weight
    total_weight = sum(weights.values())

    # Edge case: zero total weight (all entities empty)
    if total_weight <= 1e-9:
        # Distribute evenly
        base_quota = Q_total // len(entities)
        remainder = Q_total % len(entities)
        quotas = {entity.id: base_quota for entity in entities}
        # Give remainder to first R entities (arbitrary but fair)
        for i, entity in enumerate(entities):
            if i < remainder:
                quotas[entity.id] += 1
        return quotas

    # Step 2: Compute fractional quotas
    fractional_quotas = {}
    for entity in entities:
        w_e = weights.get(entity.id, 0.0)
        fractional_quotas[entity.id] = Q_total * (w_e / total_weight)

    # Step 3: Take integer parts
    integer_quotas = {eid: math.floor(fq) for eid, fq in fractional_quotas.items()}

    # Step 4: Compute remainder to distribute
    allocated = sum(integer_quotas.values())
    R = Q_total - allocated

    # Step 5: Sort entities by fractional remainder (descending)
    remainders = {}
    for eid, fq in fractional_quotas.items():
        remainders[eid] = fq - integer_quotas[eid]

    sorted_entities = sorted(
        entities,
        key=lambda e: remainders[e.id],
        reverse=True
    )

    # Step 6: Give +1 to top R entities
    final_quotas = integer_quotas.copy()
    for i in range(R):
        if i < len(sorted_entities):
            final_quotas[sorted_entities[i].id] += 1

    return final_quotas


def allocate_quotas(
    entities: List[SubEntity],
    Q_total: int,
    graph,
    recent_stimuli
) -> Dict[str, int]:
    """
    Main quota allocation function.

    Combines inverse-size weighting, modulation factors, and Hamilton allocation.

    Args:
        entities: Active sub-entities this frame
        Q_total: Total stride budget for this frame
        graph: Graph object
        recent_stimuli: Recent stimulus history

    Returns:
        Dict[entity_id -> quota_assigned]

    Formula:
        w_e = (1 / |extent_e|) × u_e × r_e × h_e
        where u, r, h are normalized to mean=1.0 per-frame
    """
    if not entities:
        return {}

    # Step 1: Compute inverse-size weights
    # Small entities get more strides per node (inverse proportion)
    inverse_size_weights = {}
    for entity in entities:
        extent_size = len(entity.extent)
        if extent_size > 0:
            inverse_size_weights[entity.id] = 1.0 / extent_size
        else:
            # Empty extent - assign minimal weight
            inverse_size_weights[entity.id] = 0.0

    # Step 2: Compute modulation factors
    factors = compute_modulation_factors(entities, graph, recent_stimuli)

    # Step 3: Combine into final weights
    # w_e = (1/|extent|) × u_e × r_e × h_e
    combined_weights = {}
    for entity in entities:
        inv_size = inverse_size_weights[entity.id]
        u_e = factors[entity.id]['urgency']
        r_e = factors[entity.id]['reachability']
        h_e = factors[entity.id]['health']

        combined_weights[entity.id] = inv_size * u_e * r_e * h_e

    # Step 4: Allocate quotas using Hamilton's method
    quotas = hamilton_quota_allocation(entities, Q_total, combined_weights)

    # Step 5: Assign quotas to entities
    for entity in entities:
        quota = quotas.get(entity.id, 0)
        entity.quota_assigned = quota
        entity.quota_remaining = quota

    return quotas
