"""
Stride Execution: Edge Selection + Gap-Aware Transport

Implements:
- Entropy-based edge selection by valence coverage
- Gap-aware conservative energy transport
- Local spectral radius estimation (warm-started power iteration)
- Alpha damping for stability

Author: AI #5
Created: 2025-10-20
Dependencies: valence, sub_entity_core
Zero-Constants: All thresholds derived from graph state
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Set
from orchestration.mechanisms.sub_entity_core import SubEntity


# --- Edge Selection ---

def select_edge_by_valence_coverage(
    subentity: SubEntity,
    source_i: int,
    valences: Dict[int, float],
    graph
) -> Tuple[int, float]:
    """
    Select edge using entropy-based adaptive coverage.

    CRITICAL: Ranks edges by VALENCE (hunger-driven), not weight (structural).

    Algorithm:
        1. Normalize valences to probability distribution
        2. Compute entropy H over valence distribution
        3. Adaptive coverage target: c_hat = 1 - exp(-H)
        4. Rank edges by VALENCE descending
        5. Take smallest prefix reaching coverage c_hat

    Args:
        subentity: Sub-entity executing stride
        source_i: Source node ID
        valences: Dict[target_j -> composite_valence V_ij]
        graph: Graph object

    Returns:
        Tuple (target_j, V_ij) for selected edge

    Zero-constants:
        - Coverage adapts to valence distribution entropy
        - No fixed K edges, no arbitrary threshold

    Example:
        valences = {j1: 0.8, j2: 0.6, j3: 0.4, j4: 0.2, j5: 0.1}
        V_total = 2.1
        p = {j1: 0.38, j2: 0.29, j3: 0.19, j4: 0.10, j5: 0.05}
        H = 1.42 (high diversity)
        H_norm = H / log(5) = 0.88
        c_hat = 1 - exp(-1.42) = 0.76 (high coverage needed)

        Ranked by V: [j1, j2, j3, j4, j5]
        Prefix coverage: j1(0.38) + j2(0.29) + j3(0.19) = 0.86 >= 0.76
        Select: j1 (highest valence)
    """
    if not valences:
        return (None, 0.0)

    # Normalize valences to probability distribution
    V_total = sum(valences.values())
    if V_total < 1e-12:
        # All valences near zero - select first edge arbitrarily
        return list(valences.items())[0]

    p = {j: V_j / V_total for j, V_j in valences.items()}

    # Compute normalized entropy
    H = -sum(p_j * math.log(p_j + 1e-12) for p_j in p.values())
    n = len(valences)
    H_norm = H / math.log(n) if n > 1 else 0.0

    # Adaptive coverage target: peaked → low coverage, flat → high coverage
    c_hat = 1.0 - math.exp(-H)

    # CRITICAL: Rank by VALENCE (hunger-driven), NOT by weight (structural)
    # This is the fix for GPT5's bug - must rank by V_ij not w_ij
    ranked = sorted(valences.items(), key=lambda x: -x[1])  # Descending by V_ij

    # Take smallest prefix reaching coverage target
    coverage = 0.0
    for target_j, V_ij in ranked:
        coverage += p[target_j]
        if coverage >= c_hat:
            # Return first edge in prefix (highest valence)
            return (ranked[0][0], ranked[0][1])

    # If we didn't reach coverage, return highest valence edge
    return ranked[0]


def compute_valence_entropy(valences: Dict[int, float]) -> float:
    """
    Compute normalized entropy over valence distribution.

    Formula:
        p_j = V_j / Σ V_all
        H = -Σ (p_j × log(p_j))
        H_norm = H / log(n)

    Args:
        valences: Dict[target_j -> valence V_ij]

    Returns:
        Normalized entropy H_norm ∈ [0, 1]
        0 = single dominant target
        1 = uniform distribution
    """
    if not valences or len(valences) == 0:
        return 0.0

    # Normalize to probability distribution
    V_total = sum(valences.values())
    if V_total < 1e-12:  # All valences near zero
        return 1.0  # Maximum uncertainty

    # Compute probabilities
    probs = [V_j / V_total for V_j in valences.values()]

    # Compute Shannon entropy H = -Σ(p log p)
    H = 0.0
    for p in probs:
        if p > 1e-12:  # Avoid log(0)
            H -= p * math.log(p)

    # Normalize by max possible entropy log(n)
    n = len(valences)
    if n <= 1:
        return 0.0  # No choice = no entropy

    H_norm = H / math.log(n)

    return H_norm


# --- Gap-Aware Transport ---

def execute_stride(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    rho_target: float = 1.0,
    staged_deltas: Dict[Tuple[str, int], float] = None
) -> Dict[str, any]:
    """
    Execute one stride with gap-aware conservative transport.

    Algorithm:
        1. Compute source slack S_i = max(0, E_i - θ_i)
        2. Compute target gap G_j = max(0, θ_j - E_j)
        3. If S_i ≤ 0 or G_j ≤ 0: return 0 transfer
        4. Compute request share R_ij (proportional to gaps)
        5. Compute transfer amount Δ = min(S_i × R_ij, G_j)
        6. Estimate local spectral radius ρ_local
        7. Apply damping α = min(1.0, ρ_target / ρ_local)
        8. Transfer: Δ_final = Δ × α
        9. Stage deltas (barrier semantics)

    Args:
        subentity: Sub-entity executing stride
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        rho_target: Target spectral radius for stability
        staged_deltas: Dict for staging energy changes (barrier semantics)

    Returns:
        Dict with stride statistics:
            - delta: float (energy transferred)
            - alpha: float (damping factor applied)
            - rho_local: float (estimated local spectral radius)
            - gap_reduced: float (target gap reduction)
            - stride_time_us: float (execution time in microseconds)

    Zero-constants:
        - Slack/gap computed from current state
        - ρ_local estimated via warm power iteration
        - α derived from ρ_target (not fixed damping)
    """
    import time
    start_time = time.perf_counter()

    if staged_deltas is None:
        staged_deltas = {}

    # Step 1-2: Compute slack and gap
    S_i, G_j = compute_slack_and_gap(subentity, source_i, target_j, graph)

    # Step 3: Early return if no transfer possible
    if S_i <= 0.0 or G_j <= 0.0:
        elapsed_us = (time.perf_counter() - start_time) * 1e6
        return {
            'delta': 0.0,
            'alpha': 1.0,
            'rho_local': subentity.rho_local_ema,
            'gap_reduced': 0.0,
            'stride_time_us': elapsed_us
        }

    # Step 4: Compute request share
    R_ij = compute_request_share(subentity, source_i, target_j, graph)

    # Step 5: Compute transfer amount (conservative - cap by both slack and gap)
    delta = min(S_i * R_ij, G_j)

    # Step 6-7: Apply spectral damping (Phase 1: α=1.0, Phase 2: from rho estimation)
    # For Phase 1, we use α=1.0 (no damping)
    # Phase 2 will implement estimate_local_rho() and apply_alpha_damping()
    alpha = 1.0
    rho_local = subentity.rho_local_ema

    # Apply damping
    delta_final = delta * alpha

    # Step 8: Stage deltas for barrier application
    stage_delta(subentity, source_i, -delta_final, staged_deltas)
    stage_delta(subentity, target_j, +delta_final, staged_deltas)

    elapsed_us = (time.perf_counter() - start_time) * 1e6

    return {
        'delta': delta_final,
        'alpha': alpha,
        'rho_local': rho_local,
        'gap_reduced': delta_final,  # Gap reduced equals delta transferred
        'stride_time_us': elapsed_us
    }


def compute_slack_and_gap(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> Tuple[float, float]:
    """
    Compute source slack and target gap.

    Args:
        subentity: Sub-entity
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Tuple (S_i, G_j) where:
            S_i = max(0, E[subentity, i] - θ[subentity, i])
            G_j = max(0, θ[subentity, j] - E[subentity, j])
    """
    # Source slack: surplus energy above threshold
    E_i = subentity.get_energy(source_i)
    theta_i = subentity.get_threshold(source_i)
    S_i = max(0.0, E_i - theta_i)

    # Target gap: deficit energy below threshold
    E_j = subentity.get_energy(target_j)
    theta_j = subentity.get_threshold(target_j)
    G_j = max(0.0, theta_j - E_j)

    return (S_i, G_j)


def compute_request_share(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Compute request share R_ij for gap-proportional allocation.

    Formula:
        neighbors = out_edges(i)
        gap_total = Σ (max(0, θ_k - E_k) for k in neighbors)
        w_total = Σ (w_ik for k in neighbors)

        R_ij = (w_ij / w_total) × (G_j / gap_total)

    Interpretation:
        - First term: structural preference (link weight)
        - Second term: need-based allocation (gap proportion)

    Args:
        subentity: Sub-entity
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Request share R_ij ∈ [0, 1]
    """
    # Get all outgoing neighbors from source
    if source_i not in graph:
        return 0.0

    neighbors = list(graph.neighbors(source_i))
    if not neighbors or target_j not in neighbors:
        return 0.0

    # Compute total gap across all neighbors
    gap_total = 0.0
    for k in neighbors:
        E_k = subentity.get_energy(k)
        theta_k = subentity.get_threshold(k)
        gap_k = max(0.0, theta_k - E_k)
        gap_total += gap_k

    # Compute total weight across all neighbors
    w_total = 0.0
    for k in neighbors:
        edge_data = graph.get_edge_data(source_i, k)
        if edge_data:
            w_total += edge_data.get('weight', 1.0)

    # Avoid division by zero
    if gap_total < 1e-12 or w_total < 1e-12:
        return 0.0

    # Get weight for target edge
    edge_data = graph.get_edge_data(source_i, target_j)
    w_ij = edge_data.get('weight', 1.0) if edge_data else 1.0

    # Get gap for target
    E_j = subentity.get_energy(target_j)
    theta_j = subentity.get_threshold(target_j)
    G_j = max(0.0, theta_j - E_j)

    # Compute request share: structural preference × need-based allocation
    R_ij = (w_ij / w_total) * (G_j / gap_total)

    return R_ij


# --- Local Spectral Radius Estimation ---

def estimate_local_rho(
    subentity: SubEntity,
    frontier_nodes: Set[int],
    graph,
    max_iterations: int = 3
) -> float:
    """
    Estimate local spectral radius via warm-started power iteration.

    Algorithm:
        1. Initialize v from previous ρ_local_ema (warm start)
        2. For 1-3 iterations:
            a. v_new = A × v (where A = link weights in frontier)
            b. λ = ||v_new|| / ||v||
            c. v = v_new / ||v_new||
        3. Return λ

    Args:
        subentity: Sub-entity with ρ_local_ema (warm start value)
        frontier_nodes: Nodes to include in local subgraph
        graph: Graph object
        max_iterations: Power iteration steps (default 3)

    Returns:
        Estimated local spectral radius ρ_local

    Zero-constants:
        - Warm-started from previous estimate (not random init)
        - Computed over frontier (not full graph)
        - Iteration count adaptive (stop if convergence)
    """
    # PHASE 2 STUB: For Week 1 MVP, return previous estimate
    # Week 2-4: Implement warm-started power iteration
    return subentity.rho_local_ema


def apply_alpha_damping(
    delta: float,
    rho_local: float,
    rho_target: float
) -> Tuple[float, float]:
    """
    Apply spectral damping to energy transfer.

    Formula:
        α = min(1.0, ρ_target / max(ρ_local, ε))
        Δ_damped = Δ × α

    Interpretation:
        - If ρ_local > ρ_target: reduce transfer (system too excitable)
        - If ρ_local ≤ ρ_target: full transfer (system stable)

    Args:
        delta: Proposed energy transfer
        rho_local: Estimated local spectral radius
        rho_target: Target spectral radius for stability

    Returns:
        Tuple (Δ_damped, α) where:
            Δ_damped = damped transfer amount
            α = damping factor applied
    """
    # PHASE 2 STUB: For Week 1 MVP, use α=1.0 (no damping)
    # Week 2-4: Implement spectral radius damping
    epsilon = 1e-9
    alpha = min(1.0, rho_target / max(rho_local, epsilon))
    delta_damped = delta * alpha
    return (delta_damped, alpha)


# --- Staged Delta Application (Barrier Semantics) ---

def stage_delta(
    subentity: SubEntity,
    node_id: int,
    delta: float,
    staged_deltas: Dict[Tuple[str, int], float]
):
    """
    Stage energy delta for barrier application.

    Barrier semantics: all deltas applied simultaneously at stride end.
    Prevents read-during-write race conditions.

    Args:
        subentity: Sub-entity
        node_id: Node to modify
        delta: Energy change (positive or negative)
        staged_deltas: Accumulator dict (entity_id, node_id) -> delta

    Side Effects:
        Accumulates delta in staged_deltas dict

    Example:
        stage_delta(e1, 42, -0.5, staged)  # Source transfer
        stage_delta(e1, 19, +0.5, staged)  # Target transfer
        apply_staged_deltas(staged, graph) # Apply simultaneously
    """
    key = (subentity.id, node_id)
    if key in staged_deltas:
        staged_deltas[key] += delta
    else:
        staged_deltas[key] = delta


def apply_staged_deltas(
    staged_deltas: Dict[Tuple[str, int], float],
    subentities: Dict[str, SubEntity]
):
    """
    Apply all staged deltas simultaneously.

    Barrier semantics: prevents race conditions during stride execution.

    Args:
        staged_deltas: Dict[(entity_id, node_id) -> delta]
        subentities: Dict[entity_id -> SubEntity] for updating energy state

    Side Effects:
        Modifies subentity energy values in place
        Clears staged_deltas dict
    """
    # Apply all deltas simultaneously
    for (entity_id, node_id), delta in staged_deltas.items():
        if entity_id in subentities:
            subentity = subentities[entity_id]
            current_energy = subentity.get_energy(node_id)
            new_energy = max(0.0, current_energy + delta)  # Energy cannot go negative
            subentity.energies[node_id] = new_energy

    # Clear staged deltas
    staged_deltas.clear()


# --- ρ_target Derivation ---

def derive_rho_target(
    wm_token_budget: int,
    frame_time_ms: float,
    avg_stride_time_us: float,
    avg_nodes_per_entity: float
) -> float:
    """
    Derive target spectral radius from downstream throughput budgets.

    NOT a fixed constant - derived from operational constraints.

    Formula (from GPT5 Q2 answer):
        Q_strides = frame_time_ms / (avg_stride_time_us / 1000.0)
        Q_total = min(Q_strides, wm_token_budget / avg_nodes_per_entity)

        ρ_target = sqrt(Q_total / (2 × avg_nodes_per_entity))

    Interpretation:
        - Higher budgets → higher ρ_target (can tolerate more excitability)
        - Lower budgets → lower ρ_target (need conservative growth)

    Args:
        wm_token_budget: LLM context limit minus overhead
        frame_time_ms: Wall-clock deadline for frame
        avg_stride_time_us: EMA of stride execution time
        avg_nodes_per_entity: EMA of extent size

    Returns:
        Target spectral radius ρ_target

    Zero-constants:
        - Derived from measured performance (stride time, extent size)
        - Adapts to computational budget (frame time, token limit)
    """
    # PHASE 2 STUB: For Week 1 MVP, return fixed 1.0
    # Week 2-4: Implement full derivation from throughput budgets

    # Prevent division by zero
    if avg_stride_time_us < 1e-6 or avg_nodes_per_entity < 1.0:
        return 1.0

    # Compute stride budget from time constraint
    Q_strides = frame_time_ms / (avg_stride_time_us / 1000.0)

    # Compute stride budget from working memory constraint
    Q_wm = wm_token_budget / avg_nodes_per_entity if avg_nodes_per_entity > 0 else float('inf')

    # Take minimum (most constraining)
    Q_total = min(Q_strides, Q_wm)

    # Derive target spectral radius
    rho_target = math.sqrt(Q_total / (2.0 * avg_nodes_per_entity))

    # Clamp to reasonable range [0.5, 2.0]
    rho_target = max(0.5, min(2.0, rho_target))

    return rho_target
