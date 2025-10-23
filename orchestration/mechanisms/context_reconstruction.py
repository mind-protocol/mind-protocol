"""
Context Reconstruction - Stimulus to Emergent Pattern

Implements emergent activation pattern reconstruction from partial cues:
1. Identify entry nodes from stimulus (semantic match + explicit refs)
2. Inject activation to nodes only (entity aggregation implicit)
3. Run bounded traversal for K ticks (two-scale: entity choices + strides)
4. Summarize: entity energies, active members, boundary links, WM selection
5. Compute similarity to prior patterns (analytics only)

Context = emergent activation pattern over nodes, summarized at entity scale.
Reconstruction = stimulus injection + budgeted weighted traversal.

No stored snapshots. Always fresh; graph is the memory.

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/context_reconstruction.md
Architecture: V2 Single-Energy + Two-Scale Traversal
"""

import numpy as np
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link
    from orchestration.core.types import EntityID


# --- Data Structures ---

@dataclass
class ContextSnapshot:
    """
    Ephemeral snapshot of reconstructed context.

    NOT persisted to database - used only for analytics/comparison.
    Represents activation pattern at moment of capture.

    Fields:
        timestamp: When snapshot was taken
        entity_energies: Total energy per entity {entity_id: energy}
        active_members: Active nodes per entity {entity_id: [node_ids]}
        boundary_links: Links crossing entity boundaries
        wm_selection: Working memory node IDs
        total_energy: Sum of all node energies
        reconstruction_ticks: How many ticks used for reconstruction
        entry_nodes: Which nodes received initial stimulus
        similarity_to_prior: Optional similarity score to reference pattern
    """
    timestamp: datetime
    entity_energies: Dict[str, float]
    active_members: Dict[str, List[str]]
    boundary_links: List[str]
    wm_selection: List[str]
    total_energy: float
    reconstruction_ticks: int
    entry_nodes: List[str]
    similarity_to_prior: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization (events/metrics)."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "entity_energies": self.entity_energies,
            "active_members": self.active_members,
            "boundary_links": self.boundary_links,
            "wm_selection": self.wm_selection,
            "total_energy": round(self.total_energy, 4),
            "reconstruction_ticks": self.reconstruction_ticks,
            "entry_nodes": self.entry_nodes,
            "similarity_to_prior": round(self.similarity_to_prior, 4) if self.similarity_to_prior else None
        }


@dataclass
class ReconstructionParams:
    """
    Parameters for context reconstruction.

    Args:
        K_ticks: Number of traversal ticks to execute
        budget: Total energy budget for traversal
        urgency: Urgency level [0, 1] affecting K/budget
        reference_snapshot: Optional prior snapshot for similarity computation
    """
    K_ticks: int = 5
    budget: float = 10.0
    urgency: float = 0.5
    reference_snapshot: Optional[ContextSnapshot] = None


class SimilarityMethod(Enum):
    """Methods for computing context similarity."""
    ENTITY_ENERGY_COSINE = "entity_energy_cosine"
    ACTIVE_MEMBER_JACCARD = "active_member_jaccard"
    COMBINED = "combined"


# --- Entity Aggregation ---

def aggregate_entity_energies(
    graph: 'Graph',
    entity_membership: Optional[Dict[str, List[str]]] = None
) -> Dict[str, float]:
    """
    Aggregate node energies by entity membership.

    Args:
        graph: Graph containing nodes
        entity_membership: {entity_id: [node_ids]}. If None, infer from nodes.

    Returns:
        {entity_id: total_energy}

    Example:
        >>> entities = {"alice": ["n1", "n2"], "bob": ["n3"]}
        >>> energies = aggregate_entity_energies(graph, entities)
        >>> energies
        {"alice": 2.5, "bob": 1.3}
    """
    if entity_membership is None:
        # Infer entity membership from node properties
        # (Assumes nodes have 'entity_id' property or can be clustered)
        entity_membership = infer_entity_membership(graph)

    aggregated = {}
    for entity_id, node_ids in entity_membership.items():
        total_energy = 0.0
        for node_id in node_ids:
            node = graph.nodes.get(node_id)
            if node:
                total_energy += node.E  # Single-energy architecture
        aggregated[entity_id] = total_energy

    return aggregated


def infer_entity_membership(graph: 'Graph') -> Dict[str, List[str]]:
    """
    Infer entity membership from graph structure.

    Strategies:
    1. Use node.properties['entity_id'] if present
    2. Use node.scope as entity grouping
    3. Fall back to single entity "default"

    Args:
        graph: Graph to analyze

    Returns:
        {entity_id: [node_ids]}
    """
    membership = {}

    for node in graph.nodes.values():
        # Strategy 1: Explicit entity_id property
        entity_id = node.properties.get('entity_id')

        # Strategy 2: Use scope as entity
        if entity_id is None:
            entity_id = node.scope  # personal/organizational/ecosystem

        # Strategy 3: Default entity
        if entity_id is None:
            entity_id = "default"

        if entity_id not in membership:
            membership[entity_id] = []
        membership[entity_id].append(node.id)

    return membership


def get_active_members(
    graph: 'Graph',
    entity_membership: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Get active nodes per entity.

    Args:
        graph: Graph containing nodes
        entity_membership: {entity_id: [node_ids]}

    Returns:
        {entity_id: [active_node_ids]}

    Example:
        >>> active = get_active_members(graph, entities)
        >>> active
        {"alice": ["n1"], "bob": []}  # Only n1 is active
    """
    active_members = {}

    for entity_id, node_ids in entity_membership.items():
        active = []
        for node_id in node_ids:
            node = graph.nodes.get(node_id)
            if node and node.is_active():  # E >= theta
                active.append(node_id)
        active_members[entity_id] = active

    return active_members


def get_boundary_links(
    graph: 'Graph',
    entity_membership: Dict[str, List[str]]
) -> List[str]:
    """
    Identify links crossing entity boundaries.

    Args:
        graph: Graph containing links
        entity_membership: {entity_id: [node_ids]}

    Returns:
        List of link IDs crossing boundaries

    Example:
        >>> boundary = get_boundary_links(graph, entities)
        >>> boundary
        ["link_alice_to_bob", "link_bob_to_alice"]
    """
    # Build reverse mapping: node_id -> entity_id
    node_to_entity = {}
    for entity_id, node_ids in entity_membership.items():
        for node_id in node_ids:
            node_to_entity[node_id] = entity_id

    boundary_links = []
    for link in graph.links.values():
        source_entity = node_to_entity.get(link.source_id)
        target_entity = node_to_entity.get(link.target_id)

        # Link crosses boundary if source and target in different entities
        if source_entity and target_entity and source_entity != target_entity:
            boundary_links.append(link.id)

    return boundary_links


# --- Context Reconstruction ---

def reconstruct_context(
    graph: 'Graph',
    entry_node_ids: List[str],
    params: Optional[ReconstructionParams] = None
) -> ContextSnapshot:
    """
    Reconstruct activation pattern from entry nodes.

    Implements spec steps:
    1. Entry nodes identified (passed as parameter)
    2. Inject activation to nodes (assumes already done by stimulus injector)
    3. Run bounded traversal for K ticks (via diffusion)
    4. Summarize: entity energies, active members, boundary links
    5. Compute similarity to prior pattern (if reference provided)

    Args:
        graph: Graph to reconstruct context in
        entry_node_ids: Entry nodes that received stimulus
        params: Reconstruction parameters (K ticks, budget, etc.)

    Returns:
        ContextSnapshot (ephemeral - not persisted)

    Example:
        >>> snapshot = reconstruct_context(
        ...     graph,
        ...     entry_nodes=["telegram_badge", "alice_schema"],
        ...     params=ReconstructionParams(K_ticks=5, budget=10.0)
        ... )
        >>> snapshot.entity_energies
        {"alice": 3.5, "work": 1.2}
    """
    if params is None:
        params = ReconstructionParams()

    # NOTE: Actual energy injection happens before this function
    # (via stimulus_injection.inject() in consciousness engine)
    # This function handles steps 3-5 (traversal + summarization)

    # Infer entity membership from graph
    entity_membership = infer_entity_membership(graph)

    # Step 3: Bounded traversal for K ticks
    # (In v2 architecture, diffusion handles traversal)
    # For reconstruction, we just capture state after K ticks of normal operation
    # In practice, consciousness_engine_v2.tick() runs diffusion/decay
    # This function is called AFTER K ticks have executed

    # Step 4: Summarize entity-scale pattern
    entity_energies = aggregate_entity_energies(graph, entity_membership)
    active_members = get_active_members(graph, entity_membership)
    boundary_links = get_boundary_links(graph, entity_membership)

    # Working memory selection (simple heuristic: top-N by energy)
    wm_selection = select_working_memory(graph, top_n=10)

    # Total energy across all nodes
    total_energy = sum(node.E for node in graph.nodes.values())

    # Create snapshot
    snapshot = ContextSnapshot(
        timestamp=datetime.now(),
        entity_energies=entity_energies,
        active_members=active_members,
        boundary_links=boundary_links,
        wm_selection=wm_selection,
        total_energy=total_energy,
        reconstruction_ticks=params.K_ticks,
        entry_nodes=entry_node_ids
    )

    # Step 5: Compute similarity to prior pattern (if reference provided)
    if params.reference_snapshot is not None:
        snapshot.similarity_to_prior = context_similarity(
            snapshot,
            params.reference_snapshot,
            method=SimilarityMethod.COMBINED
        )

    return snapshot


def select_working_memory(graph: 'Graph', top_n: int = 10) -> List[str]:
    """
    Select working memory nodes (simple heuristic: top-N by energy).

    Args:
        graph: Graph to select from
        top_n: Number of nodes to select

    Returns:
        List of node IDs in working memory

    Example:
        >>> wm = select_working_memory(graph, top_n=5)
        >>> wm
        ["node_high_energy", "node_2", ...]
    """
    # Sort nodes by energy descending
    nodes_by_energy = sorted(
        graph.nodes.values(),
        key=lambda n: n.E,
        reverse=True
    )

    # Take top-N
    return [node.id for node in nodes_by_energy[:top_n]]


# --- Pattern Similarity ---

def context_similarity(
    snapshot_a: ContextSnapshot,
    snapshot_b: ContextSnapshot,
    method: SimilarityMethod = SimilarityMethod.COMBINED
) -> float:
    """
    Compute similarity between two context snapshots.

    Methods:
    - ENTITY_ENERGY_COSINE: Cosine similarity of entity energy vectors
    - ACTIVE_MEMBER_JACCARD: Jaccard similarity of active node sets
    - COMBINED: Weighted combination (0.6 energy + 0.4 members)

    Args:
        snapshot_a: First snapshot
        snapshot_b: Second snapshot
        method: Similarity method to use

    Returns:
        Similarity in [0, 1]

    Example:
        >>> sim = context_similarity(snapshot_current, snapshot_reference)
        >>> sim
        0.73  # 73% similar
    """
    if method == SimilarityMethod.ENTITY_ENERGY_COSINE:
        return _entity_energy_cosine_similarity(snapshot_a, snapshot_b)
    elif method == SimilarityMethod.ACTIVE_MEMBER_JACCARD:
        return _active_member_jaccard_similarity(snapshot_a, snapshot_b)
    elif method == SimilarityMethod.COMBINED:
        energy_sim = _entity_energy_cosine_similarity(snapshot_a, snapshot_b)
        member_sim = _active_member_jaccard_similarity(snapshot_a, snapshot_b)
        return 0.6 * energy_sim + 0.4 * member_sim
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def _entity_energy_cosine_similarity(
    snapshot_a: ContextSnapshot,
    snapshot_b: ContextSnapshot
) -> float:
    """
    Cosine similarity of entity energy vectors.

    Args:
        snapshot_a: First snapshot
        snapshot_b: Second snapshot

    Returns:
        Cosine similarity in [0, 1]
    """
    # Get all entity IDs from both snapshots
    all_entities = set(snapshot_a.entity_energies.keys()) | set(snapshot_b.entity_energies.keys())

    if not all_entities:
        return 0.0

    # Build energy vectors (0 for missing entities)
    vec_a = np.array([snapshot_a.entity_energies.get(e, 0.0) for e in sorted(all_entities)])
    vec_b = np.array([snapshot_b.entity_energies.get(e, 0.0) for e in sorted(all_entities)])

    # Compute cosine similarity
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    cosine = np.dot(vec_a, vec_b) / (norm_a * norm_b)

    # Clamp to [0, 1] (cosine can be [-1, 1] but we use unsigned similarity)
    return max(0.0, min(1.0, cosine))


def _active_member_jaccard_similarity(
    snapshot_a: ContextSnapshot,
    snapshot_b: ContextSnapshot
) -> float:
    """
    Jaccard similarity of active node sets.

    Args:
        snapshot_a: First snapshot
        snapshot_b: Second snapshot

    Returns:
        Jaccard similarity in [0, 1]
    """
    # Flatten all active members into sets
    active_a = set()
    for members in snapshot_a.active_members.values():
        active_a.update(members)

    active_b = set()
    for members in snapshot_b.active_members.values():
        active_b.update(members)

    if not active_a and not active_b:
        return 1.0  # Both empty = identical

    if not active_a or not active_b:
        return 0.0  # One empty, one not = completely different

    # Jaccard = |intersection| / |union|
    intersection = len(active_a & active_b)
    union = len(active_a | active_b)

    return intersection / union if union > 0 else 0.0


# --- Bounded Traversal (Future Enhancement) ---

@dataclass
class TraversalResult:
    """
    Result of bounded traversal.

    Fields:
        ticks_executed: Number of ticks completed
        energy_distributed: Total energy moved during traversal
        nodes_visited: Node IDs visited during traversal
        final_frontier: Node IDs on frontier at end
    """
    ticks_executed: int
    energy_distributed: float
    nodes_visited: List[str]
    final_frontier: List[str]


def bounded_traversal(
    graph: 'Graph',
    entry_nodes: List['Node'],
    K_ticks: int,
    budget: float
) -> TraversalResult:
    """
    Run K ticks of bounded traversal from entry nodes.

    NOTE: This is a future enhancement. Current v2 architecture
    runs continuous traversal via consciousness_engine_v2.tick().

    For now, reconstruction happens by:
    1. Inject energy to entry nodes (via stimulus_injection)
    2. Run K normal ticks of engine (diffusion + decay)
    3. Capture snapshot after K ticks

    This function is a placeholder for future explicit bounded traversal.

    Args:
        graph: Graph to traverse
        entry_nodes: Starting nodes
        K_ticks: Number of ticks to execute
        budget: Energy budget per tick

    Returns:
        TraversalResult summary

    Example:
        >>> result = bounded_traversal(graph, entry_nodes, K_ticks=5, budget=10.0)
        >>> result.ticks_executed
        5
    """
    # TODO: Implement explicit bounded traversal
    # For now, return placeholder
    return TraversalResult(
        ticks_executed=0,
        energy_distributed=0.0,
        nodes_visited=[n.id for n in entry_nodes],
        final_frontier=[n.id for n in entry_nodes]
    )


# --- Utility Functions ---

def compute_energy_radius_growth(
    snapshots: List[ContextSnapshot]
) -> List[float]:
    """
    Compute energy radius growth over sequence of snapshots.

    Energy radius = weighted average distance of energy from entry nodes.

    Args:
        snapshots: Sequence of snapshots over time

    Returns:
        List of radius values (one per snapshot)

    Example:
        >>> snapshots = [snap_t0, snap_t1, snap_t2]
        >>> radii = compute_energy_radius_growth(snapshots)
        >>> radii
        [1.0, 1.5, 2.3]  # Energy spreading outward
    """
    # TODO: Implement radius calculation
    # Requires graph structure to compute distances from entry nodes
    return [0.0] * len(snapshots)


def compute_entity_energy_auc(
    snapshots: List[ContextSnapshot]
) -> float:
    """
    Compute area under curve of entity energies during reconstruction.

    Measures total activation over reconstruction window.

    Args:
        snapshots: Sequence of snapshots over time

    Returns:
        AUC value (higher = more sustained activation)

    Example:
        >>> auc = compute_entity_energy_auc(snapshots)
        >>> auc
        45.7  # Total energy × time
    """
    if not snapshots:
        return 0.0

    # Simple trapezoidal integration
    auc = 0.0
    for i in range(len(snapshots) - 1):
        e1 = snapshots[i].total_energy
        e2 = snapshots[i + 1].total_energy
        auc += (e1 + e2) / 2.0  # Assumes unit time steps

    return auc
