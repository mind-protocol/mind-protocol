"""
Mechanism 07: Energy Diffusion - Row-Stochastic Conservative Redistribution

ARCHITECTURAL PRINCIPLE: Conservative Diffusion (M16 Part 2)

Energy redistribution using row-stochastic transition matrix.
Source nodes lose energy, neighbors gain exactly that mass.

Why Conservative (NOT activation spread):
- Stability: Copying ("source keeps, target gains") inflates total energy -> runaway oscillations
- Control theory: Row-stochastic operator makes spectral radius -> control predictable
- Phenomenology preserved: Persistence via (1-alpha) retention, not energy invention

Algorithm:
    1. Build P from W (row-stochastic: rows sum to 1)
    2. Compute incoming = alpha * P^T @ E  (conservative redistribution)
    3. Apply: e_new = (1-delta) * [(1-alpha)*e + incoming] + s
    4. Clamp and saturate

Key Properties:
- Energy conserved except decay (-delta) and stimuli (+s)
- Redistribution is zero-sum
- rho (spectral radius) controls criticality

Author: Felix (Engineer)
Created: 2025-10-19
Spec: mechanism 16 Part 2 - Energy Redistribution Tick
"""

import numpy as np
import scipy.sparse as sp
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.types import EntityID

# --- Configuration ---

ALPHA_DEFAULT: float = 0.1  # Redistribution share (fraction redistributed per tick)
DELTA_DEFAULT: float = 0.03  # State decay per tick (global forgetting)
SELF_LOOP_WEIGHT: float = 0.0  # Default self-loop (0 = no explicit self-retention)


@dataclass
class DiffusionContext:
    """
    Configuration for diffusion tick.

    Args:
        alpha: Redistribution share (0 < alpha <= 1). Fraction of energy redistributed. Default 0.1.
        delta: State decay per tick (0 <= delta < 1). Global forgetting rate. Default 0.03.
        stimuli: External energy injection (optional). Dict[node_id, energy_delta].
    """
    alpha: float = ALPHA_DEFAULT
    delta: float = DELTA_DEFAULT
    stimuli: Optional[Dict[str, float]] = None


# --- Transition Matrix Construction ---

def build_transition_matrix(graph: 'Graph') -> sp.csr_matrix:
    """
    Build row-stochastic transition matrix P from graph weights.

    Row-stochastic means: rows sum to 1 (each source distributes 100% across targets)

    Process:
    1. Extract weight matrix W from graph links
    2. Normalize each row: P[i,j] = W[i,j] / sum_j W[i,j]
    3. Isolated nodes get self-loop: P[i,i] = 1 (retain all energy)

    Args:
        graph: Graph with nodes and weighted links

    Returns:
        P: Row-stochastic transition matrix (N x N, sparse)

    Example:
        >>> graph = Graph()
        >>> graph.add_node(...)
        >>> graph.add_link(source="n1", target="n2", weight=0.8)
        >>> P = build_transition_matrix(graph)
        >>> # P[n1, n2] = 0.8 / sum(weights from n1) -> 1.0 if only link
    """
    N = len(graph.nodes)
    node_to_idx = {node.id: i for i, node in enumerate(graph.nodes.values())}

    # Build sparse weight matrix W
    rows, cols, weights = [], [], []

    for link in graph.links.values():
        source_idx = node_to_idx[link.source.id]
        target_idx = node_to_idx[link.target.id]
        rows.append(source_idx)
        cols.append(target_idx)
        weights.append(link.weight)

    W = sp.csr_matrix((weights, (rows, cols)), shape=(N, N))

    # Normalize rows to sum to 1
    row_sums = np.array(W.sum(axis=1)).flatten()

    # Build row-stochastic P
    P_data = []
    P_rows = []
    P_cols = []

    for i in range(N):
        if row_sums[i] > 0:
            # Normal case: distribute energy across neighbors
            # Get all j where W[i,j] > 0
            row_start = W.indptr[i]
            row_end = W.indptr[i + 1]
            for j_idx in range(row_start, row_end):
                j = W.indices[j_idx]
                weight = W.data[j_idx]
                normalized_weight = weight / row_sums[i]
                P_rows.append(i)
                P_cols.append(j)
                P_data.append(normalized_weight)
        else:
            # Isolated node: self-loop (retain all energy)
            P_rows.append(i)
            P_cols.append(i)
            P_data.append(1.0)

    P = sp.csr_matrix((P_data, (P_rows, P_cols)), shape=(N, N))

    return P


# --- Diffusion Tick ---

def diffusion_tick(
    graph: 'Graph',
    subentity: 'EntityID',
    ctx: Optional[DiffusionContext] = None
) -> None:
    """
    Execute one tick of conservative energy diffusion for subentity.

    Algorithm:
        1. Extract current energy vector E
        2. Build transition matrix P (if not cached)
        3. Compute incoming = alpha * P^T @ E
        4. Apply: e_new = (1-delta) * [(1-alpha)*e + incoming] + s
        5. Write back to graph nodes with saturation

    Energy flows from high to low through weighted links.
    Total energy changes ONLY by decay (-delta) and stimuli (+s).

    Args:
        graph: Graph with nodes and links
        subentity: Subentity to diffuse energy for
        ctx: Diffusion configuration (defaults if None)

    Example:
        >>> graph = Graph()
        >>> # ... populate graph ...
        >>> ctx = DiffusionContext(alpha=0.1, delta=0.03)
        >>> diffusion_tick(graph, "translator", ctx)
        >>> # Energy redistributed conservatively
    """
    if ctx is None:
        ctx = DiffusionContext()

    N = len(graph.nodes)
    if N == 0:
        return

    # 1. Extract current energy vector E
    E = np.zeros(N)
    node_to_idx = {node.id: i for i, node in enumerate(graph.nodes.values())}

    for i, node in enumerate(graph.nodes.values()):
        E[i] = node.get_entity_energy(subentity)

    # 2. Build transition matrix P
    P = build_transition_matrix(graph)
    P_T = P.transpose()  # For efficient incoming drive computation

    # 3. Compute incoming drive (conservative redistribution)
    incoming = ctx.alpha * P_T.dot(E)

    # 4. Apply update: e_new = (1-delta) * [(1-alpha)*e + incoming] + s
    E_new = (1 - ctx.delta) * ((1 - ctx.alpha) * E + incoming)

    # 5. Apply external stimuli (if provided)
    if ctx.stimuli:
        for node_id, stimulus_delta in ctx.stimuli.items():
            if node_id in node_to_idx:
                idx = node_to_idx[node_id]
                E_new[idx] += stimulus_delta

    # 6. Write back with saturation
    for i, node in enumerate(graph.nodes.values()):
        node.set_entity_energy(subentity, E_new[i])


# --- Helper Functions ---

def get_spectral_radius(P: sp.csr_matrix) -> float:
    """
    Compute spectral radius rho of transition matrix P.

    rho = largest eigenvalue magnitude

    Criticality indicator:
    - rho < 1: Subcritical (activations die out)
    - rho ~= 1: Critical (sustained consciousness)
    - rho > 1: Supercritical (runaway cascades)

    Args:
        P: Row-stochastic transition matrix

    Returns:
        rho (spectral radius)

    Example:
        >>> P = build_transition_matrix(graph)
        >>> rho = get_spectral_radius(P)
        >>> print(f"Criticality: rho={rho:.3f}")
    """
    # Compute largest eigenvalue (k=1, which='LM' = largest magnitude)
    eigenvalues = sp.linalg.eigs(P, k=1, which='LM', return_eigenvectors=False)
    rho = np.abs(eigenvalues[0])
    return float(rho)


def compute_energy_entropy(E: np.ndarray) -> float:
    """
    Compute Shannon entropy of energy distribution.

    Measures diversity of activation:
    - High entropy: Many nodes active with similar energy
    - Low entropy: Few nodes dominate

    Args:
        E: Energy vector (N,)

    Returns:
        Entropy (nats)

    Example:
        >>> E = np.array([0.5, 0.3, 0.2])
        >>> entropy = compute_energy_entropy(E)
        >>> print(f"Diversity: {entropy:.3f} nats")
    """
    # Normalize to probability distribution
    total = E.sum()
    if total < 1e-10:
        return 0.0

    P = E / total

    # Compute Shannon entropy: H = -sum p_i * log(p_i)
    # Filter out zeros (0 * log(0) = 0 by convention)
    P_nonzero = P[P > 1e-10]
    entropy = -np.sum(P_nonzero * np.log(P_nonzero))

    return float(entropy)
