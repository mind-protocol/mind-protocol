"""
Diffusion Runtime Accumulator & Stride Executor

Manages staged energy deltas for stride-based diffusion.

Architecture:
- delta_E: Accumulates energy transfers during tick
- active: Nodes with E >= theta or receiving energy this tick
- shadow: 1-hop neighbors of active nodes (frontier expansion)
- Stride executor: Selects best edges and stages energy transfers

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/diffusion.md
"""

import math
import random
import time
import numpy as np
from typing import Dict, Set, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.link import Link
    from orchestration.mechanisms.strengthening import LearningController


class DiffusionRuntime:
    """
    Runtime accumulator for stride-based energy diffusion.

    Collects energy deltas during traversal, applies atomically at end of tick.
    Maintains active/shadow frontier for O(frontier) performance.

    Attributes:
        delta_E: Accumulated energy deltas per node (staged)
        active: Nodes with E >= theta or touched this tick
        shadow: 1-hop neighbors of active (candidate frontier)
    """
    __slots__ = ("delta_E", "active", "shadow")

    def __init__(self):
        """Initialize empty runtime accumulator."""
        self.delta_E: Dict[str, float] = {}
        self.active: Set[str] = set()
        self.shadow: Set[str] = set()

    def add(self, node_id: str, delta: float) -> None:
        """
        Stage energy delta for node.

        Accumulates delta into staging buffer. Applied atomically at end of tick.

        Args:
            node_id: Node identifier
            delta: Energy change (positive = gain, negative = loss)

        Example:
            >>> rt = DiffusionRuntime()
            >>> rt.add("n1", -0.05)  # Source loses energy
            >>> rt.add("n2", +0.05)  # Target gains energy
        """
        self.delta_E[node_id] = self.delta_E.get(node_id, 0.0) + delta

    def clear_deltas(self) -> None:
        """Clear staged deltas after applying."""
        self.delta_E.clear()

    def compute_frontier(self, graph: 'Graph') -> None:
        """
        Recompute active and shadow sets from current energy state.

        Active: nodes with E >= theta
        Shadow: 1-hop neighbors of active nodes

        Args:
            graph: Consciousness graph

        Side effects:
            Updates self.active and self.shadow
        """
        # Active = nodes above threshold
        self.active = {
            node.id for node in graph.nodes.values()
            if node.is_active()
        }

        # Shadow = 1-hop neighbors of active
        self.shadow = set()
        for node_id in self.active:
            node = graph.nodes.get(node_id)
            if node:
                # Add all outgoing neighbors to shadow
                for link in node.outgoing_links:
                    self.shadow.add(link.target.id)

        # Shadow excludes already-active nodes
        self.shadow -= self.active

    def get_conservation_error(self) -> float:
        """
        Compute total staged energy delta (should be ~0 for conservation).

        Returns:
            Sum of all deltas (conservation error if != 0)

        Example:
            >>> error = rt.get_conservation_error()
            >>> assert abs(error) < 1e-6, "Energy not conserved!"
        """
        return sum(self.delta_E.values())


def _compute_link_emotion(link: 'Link', energy_flow: float) -> Optional[np.ndarray]:
    """
    Compute link emotion by interpolating source and target node emotions.

    Phase 1 implementation: Simple linear interpolation weighted by energy flow.
    Higher energy flow → stronger emotion transfer.

    Args:
        link: Link being traversed
        energy_flow: Energy flowing through link this stride

    Returns:
        Link emotion vector [valence, arousal] or None if no node emotions exist

    Example:
        >>> link_emotion = _compute_link_emotion(link, energy_flow=0.05)
        >>> # Returns blend of source and target emotions weighted by flow
    """
    # Check if nodes have emotions
    source_emotion = getattr(link.source, 'emotion_vector', None)
    target_emotion = getattr(link.target, 'emotion_vector', None)

    if source_emotion is None and target_emotion is None:
        return None  # No emotion to propagate

    # Initialize neutral if missing
    if source_emotion is None:
        source_emotion = np.array([0.0, 0.0])
    if target_emotion is None:
        target_emotion = np.array([0.0, 0.0])

    # Interpolate: blend source and target emotions
    # Weight by energy flow intensity (higher flow → more blending)
    flow_weight = min(energy_flow * 10.0, 1.0)  # Scale factor for visibility

    # Simple average weighted by flow
    link_emotion = (1.0 - flow_weight * 0.5) * source_emotion + flow_weight * 0.5 * target_emotion

    return link_emotion


def _emit_link_emotion_event(
    link: 'Link',
    emotion_vector: np.ndarray,
    broadcaster: Any,
    sample_rate: float
) -> None:
    """
    Emit link.emotion.update event via WebSocket.

    Event format (matches frontend expectation):
    {
        type: 'link.emotion.update',
        link_id: string,
        emotion_magnitude: number,
        top_axes: [
            {axis: 'valence', value: number},
            {axis: 'arousal', value: number}
        ],
        timestamp: string
    }

    Args:
        link: Link being updated
        emotion_vector: Computed emotion vector [valence, arousal]
        broadcaster: WebSocket broadcaster
        sample_rate: Emission sampling rate (0-1)
    """
    # Sample emission to reduce WebSocket traffic
    if random.random() > sample_rate:
        return

    if not broadcaster or not hasattr(broadcaster, 'is_available'):
        return

    if not broadcaster.is_available():
        return

    # Compute magnitude
    magnitude = float(np.linalg.norm(emotion_vector))

    # Extract top axes (valence and arousal for 2D affect)
    top_axes = [
        {"axis": "valence", "value": float(emotion_vector[0])},
        {"axis": "arousal", "value": float(emotion_vector[1]) if len(emotion_vector) > 1 else 0.0}
    ]

    # Emit event
    import asyncio
    asyncio.create_task(broadcaster.broadcast_event("link.emotion.update", {
        "link_id": link.id,
        "emotion_magnitude": magnitude,
        "top_axes": top_axes,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }))


def execute_stride_step(
    graph: 'Graph',
    rt: DiffusionRuntime,
    alpha_tick: float = 0.1,
    dt: float = 1.0,
    sample_rate: float = 0.1,
    learning_controller: Optional['LearningController'] = None,
    enable_strengthening: bool = True,
    goal_embedding: Optional[np.ndarray] = None,
    broadcaster: Optional[Any] = None,
    enable_link_emotion: bool = True
) -> int:
    """
    Execute one stride step: select best edges from active nodes and stage energy transfers.

    Algorithm (spec: traversal_v2.md §3.4):
        For each active node:
            1. Select best outgoing edge (argmin cost: ease + goal + emotion)
            2. Compute ΔE = E_src · f(w) · α_tick · Δt
            3. Stage transfer: rt.add(src, -ΔE), rt.add(dst, +ΔE)
            4. Strengthen link (Hebbian learning - integrated)
            5. Emit stride.exec event (sampled)

    Where f(w) = exp(log_weight) per spec.

    Cost computation (traversal_v2.md §3.4):
        cost = (1/ease) - goal_affinity + emotion_penalty
        - ease = exp(log_weight)
        - goal_affinity = cos(target.embedding, goal_embedding)
        - emotion_penalty = gates (TODO - not implemented yet)

    Strengthening: Links strengthen when energy flows through them (spec: link_strengthening.md).
    Only when BOTH nodes inactive (D020 rule) - prevents runaway strengthening.

    Args:
        graph: Consciousness graph
        rt: DiffusionRuntime accumulator
        alpha_tick: Redistribution share (fraction of energy redistributed)
        dt: Time delta (tick interval in seconds)
        sample_rate: Emission sampling rate for observability
        learning_controller: Optional learning rate controller (created if None)
        enable_strengthening: Whether to apply link strengthening (default True)
        goal_embedding: Optional goal vector for goal-affinity cost computation
        broadcaster: Optional WebSocket broadcaster for emotion events
        enable_link_emotion: Whether to compute and emit link emotions (default True)

    Returns:
        Number of strides executed

    Example:
        >>> rt = DiffusionRuntime()
        >>> rt.active = {"n1", "n2", "n3"}
        >>> strides = execute_stride_step(graph, rt, alpha_tick=0.1, dt=1.0, goal_embedding=goal_vec)
        >>> print(f"Executed {strides} strides")
    """
    # Create learning controller if not provided
    if learning_controller is None and enable_strengthening:
        from orchestration.mechanisms.strengthening import LearningController
        from orchestration.core.settings import settings
        learning_controller = LearningController(base_rate=settings.LEARNING_RATE_BASE)

    strides_executed = 0

    # Iterate over active nodes
    for src_id in list(rt.active):
        node = graph.nodes.get(src_id)
        if not node:
            continue

        E_src = node.E
        if E_src <= 0.0:
            continue

        # Select best outgoing edge using cost computation (K=1 for now)
        best_link = _select_best_outgoing_link(node, goal_embedding=goal_embedding)
        if not best_link:
            continue

        # Compute ease from log_weight: f(w) = exp(log_weight)
        ease = math.exp(best_link.log_weight)

        # Compute energy transfer: ΔE = E_src · f(w) · α · Δt
        delta_E = E_src * ease * alpha_tick * dt

        if delta_E <= 1e-9:  # Skip negligible transfers
            continue

        # === PR-E: Apply Stickiness (E.4) ===
        # Stickiness determines how much energy target retains
        # Memory nodes: high stickiness (energy sticks), Task nodes: low stickiness (energy flows)
        stickiness = compute_stickiness(best_link.target, graph)
        retained_delta_E = stickiness * delta_E

        # Stage transfer (non-conservative if stickiness < 1.0: energy dissipates)
        rt.add(src_id, -delta_E)  # Source loses full amount
        rt.add(best_link.target.id, +retained_delta_E)  # Target gains retained amount
        # Energy leak: (delta_E - retained_delta_E) dissipates to environment

        # Compute and emit link emotion (Phase 1: interpolation)
        if enable_link_emotion and broadcaster is not None:
            link_emotion = _compute_link_emotion(best_link, delta_E)
            if link_emotion is not None:
                # Update link's emotion vector
                best_link.emotion_vector = link_emotion
                # Emit event to frontend
                _emit_link_emotion_event(best_link, link_emotion, broadcaster, sample_rate)

        # Strengthen link (Hebbian learning - integrated with diffusion)
        if enable_strengthening and learning_controller is not None:
            from orchestration.mechanisms.strengthening import strengthen_during_stride
            strengthen_during_stride(best_link, delta_E, learning_controller)

        # Learn RELATES_TO from boundary strides (spec: subentity_layer.md §2.5)
        # Detect if this stride crosses an entity boundary
        if hasattr(graph, 'subentities') and graph.subentities:
            from orchestration.core.types import LinkType

            # Find which entities the source and target nodes belong to
            source_entities = []
            target_entities = []

            # Check source node's BELONGS_TO links
            for link in node.outgoing_links:
                if link.link_type == LinkType.BELONGS_TO:
                    source_entities.append(link.target)

            # Check target node's BELONGS_TO links
            for link in best_link.target.outgoing_links:
                if link.link_type == LinkType.BELONGS_TO:
                    target_entities.append(link.target)

            # If nodes belong to different entities, this is a boundary stride
            for src_entity in source_entities:
                for tgt_entity in target_entities:
                    if src_entity.id != tgt_entity.id:
                        # Boundary stride detected!
                        from orchestration.mechanisms.entity_activation import learn_relates_to_from_boundary_stride
                        learn_relates_to_from_boundary_stride(
                            src_entity,
                            tgt_entity,
                            delta_E,
                            graph,
                            learning_rate=0.05
                        )

        strides_executed += 1

        # TODO: Emit stride.exec event (sampled) for observability
        # if random.random() < sample_rate:
        #     emit_stride_exec(src_id, best_link.target.id, delta_E, ...)

    return strides_executed


def _compute_link_cost(
    link: 'Link',
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None
) -> float:
    """
    Compute traversal cost for link (lower = better).

    Cost components (spec: traversal_v2.md §3.4):
    - Ease cost: 1/exp(log_weight) - harder to traverse weak links
    - Goal affinity: -cos(link.target.embedding, goal) - prefer goal-aligned targets
    - Emotion gates: resonance/complementarity multipliers (TODO - spec not written yet)

    Args:
        link: Link to evaluate
        goal_embedding: Optional goal vector for affinity computation
        emotion_context: Optional emotion state (for gates)

    Returns:
        Cost value (lower = prefer this link)

    Example:
        >>> cost = _compute_link_cost(link, goal_embedding=goal_vec)
        >>> # Strong link (log_weight=0.7) aligned with goal → low cost
        >>> # Weak link (log_weight=-1.0) opposed to goal → high cost
    """
    import numpy as np

    # 1. Ease cost: 1/exp(log_weight)
    #    Strong links (log_weight >> 0) have low ease cost
    #    Weak links (log_weight << 0) have high ease cost
    ease = math.exp(link.log_weight)
    ease_cost = 1.0 / max(ease, 1e-6)  # Avoid division by zero

    # 2. Goal affinity bonus (negative = reduce cost)
    #    High similarity to goal reduces cost (prefer goal-aligned paths)
    goal_affinity = 0.0
    if goal_embedding is not None and hasattr(link.target, 'embedding') and link.target.embedding is not None:
        # Cosine similarity
        target_emb = link.target.embedding
        norm_goal = np.linalg.norm(goal_embedding)
        norm_target = np.linalg.norm(target_emb)

        if norm_goal > 1e-9 and norm_target > 1e-9:
            cos_sim = np.dot(goal_embedding, target_emb) / (norm_goal * norm_target)
            goal_affinity = np.clip(cos_sim, -1.0, 1.0)

    # 3. Emotion gate penalty (TODO - specs not written yet)
    #    For now, set to 0.0 and add TODO comment
    #    Should compute resonance/complementarity multipliers from emotion_context
    emotion_penalty = 0.0
    # TODO: Implement emotion gates as cost modulators when specs are written
    # Should compute:
    # - resonance_mult = f(emotion similarity) using RES_LAMBDA, RES_MIN/MAX_MULT
    # - comp_mult = f(emotion opposition) using COMP_LAMBDA, COMP_MIN/MAX_MULT
    # - emotion_penalty = some combination of these gates

    # Total cost (lower = better)
    total_cost = ease_cost - goal_affinity + emotion_penalty

    return total_cost


def _select_best_outgoing_link(
    node,
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None
) -> Optional['Link']:
    """
    Select best outgoing link from node (argmin cost).

    Uses cost computation with ease, goal affinity, and emotion gates.
    This is the V2 spec implementation (traversal_v2.md §3.4).

    Args:
        node: Source node
        goal_embedding: Optional goal vector for affinity-based selection
        emotion_context: Optional emotion state for gate computation

    Returns:
        Best link (lowest cost), or None if no outgoing links

    Example:
        >>> best = _select_best_outgoing_link(node, goal_embedding=goal_vec)
        >>> # Returns link with lowest total cost (ease + goal + emotion)
    """
    if not node.outgoing_links:
        return None

    # Compute cost for each outgoing link
    link_costs = [
        (_compute_link_cost(link, goal_embedding, emotion_context), link)
        for link in node.outgoing_links
    ]

    # Select link with minimum cost
    best_cost, best_link = min(link_costs, key=lambda x: x[0])

    return best_link


# === PR-E: E.4 Stickiness (energy retention during diffusion) ===

def compute_stickiness(node, graph: 'Graph') -> float:
    """
    Compute stickiness factor for this node.

    Stickiness determines how much energy a node retains during diffusion:
    - Memory nodes: high stickiness (0.9) - energy sticks
    - Task nodes: low stickiness (0.3) - energy flows freely
    - Default: medium stickiness (0.6)

    Additional factors:
    - Consolidation: +0.2 if consolidated (important patterns retain more)
    - Centrality: +0.1 * tanh(degree/20) for high-degree nodes

    Formula: s_j = clip(s_type + s_consolidation + s_centrality, 0.1, 1.0)

    Args:
        node: Target node receiving energy
        graph: Graph (for checking consolidation status)

    Returns:
        Stickiness factor ∈ [0.1, 1.0]
    """
    from orchestration.core.settings import settings

    if not settings.DIFFUSION_STICKINESS_ENABLED:
        return 1.0  # No stickiness effect, perfect transfer

    # s_type: Base stickiness by node type
    node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    type_stickiness_map = {
        "Memory": settings.STICKINESS_TYPE_MEMORY,
        "Episodic_Memory": settings.STICKINESS_TYPE_MEMORY,
        "Principle": 0.85,
        "Personal_Value": 0.85,
        "Task": settings.STICKINESS_TYPE_TASK,
        "Event": 0.4,
    }
    s_type = type_stickiness_map.get(node_type, settings.STICKINESS_TYPE_DEFAULT)

    # s_consolidation: Boost if consolidated
    s_consolidation = 0.0
    if hasattr(node, 'consolidated') and node.consolidated:
        s_consolidation = settings.STICKINESS_CONSOLIDATION_BOOST

    # s_centrality: Boost for high-degree nodes (structural importance)
    degree = len(node.outgoing_links) + len(node.incoming_links)
    s_centrality = 0.1 * math.tanh(degree / 20.0)

    # Combine (additive)
    s_j = s_type + s_consolidation + s_centrality

    # Clamp to valid range
    s_j = np.clip(s_j, 0.1, 1.0)

    return s_j
