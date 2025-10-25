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
from dataclasses import dataclass
from orchestration.core.entity_context_extensions import effective_log_weight_link

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.link import Link
    from orchestration.mechanisms.strengthening import LearningController


@dataclass
class CostBreakdown:
    """
    Forensic trail for link cost computation.

    Enables attribution tracking - understanding exactly why a link was chosen.
    All intermediate values preserved for observability.

    Fields:
        total_cost: Final cost after all modulations (lower = better)
        ease: exp(log_weight) - structural ease of traversal
        ease_cost: 1/ease - cost from link strength
        goal_affinity: cos(target.emb, goal.emb) - alignment with goal
        res_mult: Resonance multiplier from emotion gates (1.0 = neutral)
        res_score: Resonance alignment score (cosine similarity)
        comp_mult: Complementarity multiplier from emotion gates (1.0 = neutral)
        emotion_mult: Combined emotion multiplier (res_mult * comp_mult)
        base_cost: Cost before emotion modulation (ease_cost - goal_affinity)
        reason: Human-readable explanation of why this link was chosen
    """
    total_cost: float
    ease: float
    ease_cost: float
    goal_affinity: float
    res_mult: float
    res_score: float
    comp_mult: float
    emotion_mult: float
    base_cost: float
    reason: str


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
    __slots__ = ("delta_E", "active", "shadow", "stride_relatedness_scores", "current_frontier_nodes")

    def __init__(self):
        """Initialize empty runtime accumulator."""
        self.delta_E: Dict[str, float] = {}
        self.active: Set[str] = set()
        self.shadow: Set[str] = set()

        # Coherence tracking (E.6) - collected during stride execution
        self.stride_relatedness_scores: List[float] = []
        self.current_frontier_nodes: List[Any] = []

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
    enable_link_emotion: bool = True,
    current_entity_id: Optional[str] = None,
    emitter: Optional[Any] = None
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
        cost = base_cost * emotion_mult
        - base_cost = (1/ease) - goal_affinity
        - ease = exp(log_weight)
        - goal_affinity = cos(target.embedding, goal_embedding)
        - emotion_mult = resonance_mult * complementarity_mult (when EMOTION_GATES_ENABLED)

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
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

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

    # Collect emotion deltas for emitter
    node_emotion_deltas = []
    link_emotion_deltas = []

    # === E.6: Collect current frontier nodes for coherence metric ===
    if settings.COHERENCE_METRIC_ENABLED:
        rt.current_frontier_nodes = [graph.nodes[nid] for nid in rt.active if nid in graph.nodes]
        rt.stride_relatedness_scores = []  # Reset for this tick

    # Iterate over active nodes
    for src_id in list(rt.active):
        node = graph.nodes.get(src_id)
        if not node:
            continue

        E_src = node.E
        if E_src <= 0.0:
            continue

        # Construct emotion context for gate computation
        emotion_context = None
        if hasattr(node, 'emotion_vector') and node.emotion_vector is not None:
            emotion_magnitude = np.linalg.norm(node.emotion_vector)
            emotion_context = {
                'entity_affect': node.emotion_vector,  # Use node's emotion as current affect
                'intensity': emotion_magnitude,
                'context_gate': 1.0  # Neutral context (TODO: infer from task mode)
            }

        # Select best outgoing edge using cost computation (K=1 for now)
        # Link selection is entity-aware when current_entity_id provided (Priority 4)
        result = _select_best_outgoing_link(node, goal_embedding=goal_embedding, emotion_context=emotion_context, current_entity_id=current_entity_id)
        if not result:
            continue

        best_link, cost_breakdown = result

        # === E.6: Collect stride relatedness for coherence metric ===
        if settings.COHERENCE_METRIC_ENABLED:
            from orchestration.mechanisms.coherence_metric import assess_stride_relatedness
            relatedness = assess_stride_relatedness(node, best_link.target, best_link)
            rt.stride_relatedness_scores.append(relatedness)

        # Compute ease from effective weight: f(w) = exp(effective_log_weight)
        # Uses entity-specific overlay when current_entity_id provided (Priority 4)
        # Falls back to global log_weight when entity_id is None
        if current_entity_id:
            log_w = effective_log_weight_link(best_link, current_entity_id)
        else:
            log_w = best_link.log_weight
        ease = math.exp(log_w)

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

        # Collect node emotion delta for target node (if it has an emotion vector)
        if emitter is not None and hasattr(best_link.target, 'emotion_vector') and best_link.target.emotion_vector is not None:
            if random.random() <= sample_rate:
                from orchestration.adapters.ws.traversal_event_emitter import EmotionDelta
                node_emotion = best_link.target.emotion_vector
                magnitude = float(np.linalg.norm(node_emotion))
                top_axes = [
                    ("valence", float(node_emotion[0])),
                    ("arousal", float(node_emotion[1]) if len(node_emotion) > 1 else 0.0)
                ]
                node_emotion_deltas.append(EmotionDelta(
                    id=best_link.target.id,
                    mag=magnitude,
                    top_axes=top_axes
                ))

        # Compute link emotion (Phase 1: interpolation) and collect for emission
        if enable_link_emotion:
            link_emotion = _compute_link_emotion(best_link, delta_E)
            if link_emotion is not None:
                # Update link's emotion vector
                best_link.emotion_vector = link_emotion

                # Collect delta for batch emission via emitter
                if emitter is not None and random.random() <= sample_rate:
                    from orchestration.adapters.ws.traversal_event_emitter import EmotionDelta
                    magnitude = float(np.linalg.norm(link_emotion))
                    top_axes = [
                        ("valence", float(link_emotion[0])),
                        ("arousal", float(link_emotion[1]) if len(link_emotion) > 1 else 0.0)
                    ]
                    link_emotion_deltas.append(EmotionDelta(
                        id=best_link.id,
                        mag=magnitude,
                        top_axes=top_axes
                    ))

        # Strengthen link (Hebbian learning - integrated with diffusion)
        if enable_strengthening and learning_controller is not None:
            from orchestration.mechanisms.strengthening import strengthen_during_stride
            strengthen_during_stride(
                best_link,
                delta_E,
                learning_controller,
                broadcaster=broadcaster,  # P2.1.3: Pass for tier.link.strengthened emission
                entity_context=[current_entity_id] if current_entity_id else None,
                citizen_id=runtime.graph_name if hasattr(runtime, 'graph_name') else "",
                frame_id=getattr(graph, 'frame_id', None)
            )

        # Learn RELATES_TO from boundary strides (spec: subentity_layer.md §2.5)
        # Detect if this stride crosses an entity boundary
        if hasattr(graph, 'subentities') and graph.subentities:
            from orchestration.core.types import LinkType

            # Find which entities the source and target nodes belong to
            source_entities = []
            target_entities = []

            # Check source node's BELONGS_TO links
            for link in node.outgoing_links:
                if link.link_type == LinkType.MEMBER_OF:
                    source_entities.append(link.target)

            # Check target node's BELONGS_TO links
            for link in best_link.target.outgoing_links:
                if link.link_type == LinkType.MEMBER_OF:
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

        # Emit stride.exec event with forensic trail (sampled for performance)
        if broadcaster is not None and random.random() < sample_rate:
            # Get threshold value (phi) for forensic trail
            phi = getattr(node, 'theta', 0.0)

            stride_data = {
                'src_node': src_id,
                'dst_node': best_link.target.id,
                'link_id': best_link.id,
                # Forensic trail fields
                'phi': round(phi, 4),  # Threshold
                'ease': round(cost_breakdown.ease, 4),
                'ease_cost': round(cost_breakdown.ease_cost, 4),
                'goal_affinity': round(cost_breakdown.goal_affinity, 4),
                'res_mult': round(cost_breakdown.res_mult, 4),
                'res_score': round(cost_breakdown.res_score, 4),
                'comp_mult': round(cost_breakdown.comp_mult, 4),
                'emotion_mult': round(cost_breakdown.emotion_mult, 4),
                'base_cost': round(cost_breakdown.base_cost, 4),
                'total_cost': round(cost_breakdown.total_cost, 4),
                'reason': cost_breakdown.reason,
                # Energy transfer
                'delta_E': round(delta_E, 6),
                'stickiness': round(stickiness, 4),
                'retained_delta_E': round(retained_delta_E, 6),
                # Metadata
                'chosen': True  # This link was selected (lowest cost)
            }

            # Emit via broadcaster
            broadcaster.stride_exec(stride_data)

    # Emit collected emotion deltas via emitter (batch emission)
    if emitter is not None:
        if node_emotion_deltas:
            emitter.node_emotion_update(node_emotion_deltas)
        if link_emotion_deltas:
            emitter.link_emotion_update(link_emotion_deltas)

    return strides_executed


def _compute_link_cost(
    link: 'Link',
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None,
    current_entity_id: Optional[str] = None
) -> CostBreakdown:
    """
    Compute traversal cost for link with full forensic trail (lower cost = better).

    Cost components (spec: traversal_v2.md §3.4):
    - Ease cost: 1/exp(effective_log_weight) - harder to traverse weak links (entity-aware, Priority 4)
    - Goal affinity: -cos(link.target.embedding, goal) - prefer goal-aligned targets
    - Emotion gates: resonance/complementarity multipliers (modulate base cost)

    Args:
        link: Link to evaluate
        goal_embedding: Optional goal vector for affinity computation
        emotion_context: Optional emotion state dict with:
            - entity_affect: np.ndarray - current entity affect vector
            - context_gate: float - context modulation (0-2, focus vs recovery)
            - intensity: float - affect magnitude
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

    Returns:
        CostBreakdown with total_cost and all intermediate values for observability

    Example:
        >>> breakdown = _compute_link_cost(link, goal_embedding=goal_vec, current_entity_id="entity_translator")
        >>> # Strong link (log_weight=0.7) aligned with goal → low cost
        >>> # breakdown.ease = 2.0, breakdown.goal_affinity = 0.8, breakdown.total_cost = 0.2
    """
    import numpy as np
    from orchestration.core.settings import settings

    # 1. Ease cost: 1/exp(effective_log_weight) - entity-aware (Priority 4)
    #    Strong links (log_weight >> 0) have low ease cost
    #    Weak links (log_weight << 0) have high ease cost
    #    Uses entity-specific overlays when current_entity_id provided
    if current_entity_id:
        log_w = effective_log_weight_link(link, current_entity_id)
    else:
        log_w = link.log_weight
    ease = math.exp(log_w)
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

    # 3. Emotion gates (resonance + complementarity)
    #    Modulate base cost multiplicatively per specs:
    #    - emotion_complementarity.md - regulation via opposites
    #    - emotion_weighted_traversal.md - coherence via similarity
    emotion_mult = 1.0  # Neutral default
    res_mult = 1.0  # Neutral (no resonance modulation)
    res_score = 0.0  # No alignment
    comp_mult = 1.0  # Neutral (no complementarity modulation)

    if settings.EMOTION_GATES_ENABLED and emotion_context:
        entity_affect = emotion_context.get('entity_affect')
        link_emotion = getattr(link, 'emotion_vector', None)

        if entity_affect is not None and link_emotion is not None:
            from orchestration.mechanisms.emotion_coloring import (
                resonance_multiplier,
                complementarity_multiplier
            )

            # Resonance gate (coherence - prefer emotionally aligned paths)
            # r > 0 (aligned) → m_res < 1 (attractive, easier)
            # r < 0 (clash) → m_res > 1 (repulsive, harder)
            res_mult, res_score = resonance_multiplier(entity_affect, link_emotion)

            # Complementarity gate (regulation - prefer opposite affect for balance)
            # High opposition → lower multiplier → lower cost (regulatory pull)
            intensity_gate = emotion_context.get('intensity', np.linalg.norm(entity_affect))
            context_gate = emotion_context.get('context_gate', 1.0)  # 0-2 scale
            comp_mult = complementarity_multiplier(
                entity_affect,
                link_emotion,
                intensity_gate=np.clip(intensity_gate, 0.0, 1.0),
                context_gate=context_gate
            )

            # Combine gates multiplicatively (per spec: order doesn't matter)
            emotion_mult = res_mult * comp_mult

    # Total cost: base cost modulated by emotion gates
    base_cost = ease_cost - goal_affinity
    total_cost = base_cost * emotion_mult

    # Generate human-readable reason for why this link was chosen
    reason_parts = []
    if ease > 1.5:
        reason_parts.append(f"strong_link(ease={ease:.2f})")
    elif ease < 0.5:
        reason_parts.append(f"weak_link(ease={ease:.2f})")

    if goal_affinity > 0.5:
        reason_parts.append(f"goal_aligned(aff={goal_affinity:.2f})")
    elif goal_affinity < -0.5:
        reason_parts.append(f"goal_opposed(aff={goal_affinity:.2f})")

    if res_mult < 0.9:
        reason_parts.append(f"resonance_attract(r={res_score:.2f})")
    elif res_mult > 1.1:
        reason_parts.append(f"resonance_repel(r={res_score:.2f})")

    if comp_mult < 0.9:
        reason_parts.append(f"regulation_pull")

    reason = " + ".join(reason_parts) if reason_parts else "neutral"

    # Return full breakdown for forensic trail
    return CostBreakdown(
        total_cost=total_cost,
        ease=ease,
        ease_cost=ease_cost,
        goal_affinity=goal_affinity,
        res_mult=res_mult,
        res_score=res_score,
        comp_mult=comp_mult,
        emotion_mult=emotion_mult,
        base_cost=base_cost,
        reason=reason
    )


def _select_best_outgoing_link(
    node,
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None,
    current_entity_id: Optional[str] = None
) -> Optional[tuple['Link', CostBreakdown]]:
    """
    Select best outgoing link from node (argmin cost) with full forensic trail.

    Uses cost computation with ease, goal affinity, and emotion gates.
    This is the V2 spec implementation (traversal_v2.md §3.4).
    Link selection is entity-aware when current_entity_id provided (Priority 4).

    Args:
        node: Source node
        goal_embedding: Optional goal vector for affinity-based selection
        emotion_context: Optional emotion state for gate computation
        current_entity_id: Optional entity ID for personalized weight computation (Priority 4)

    Returns:
        Tuple of (best_link, cost_breakdown), or None if no outgoing links

    Example:
        >>> result = _select_best_outgoing_link(node, goal_embedding=goal_vec, current_entity_id="entity_translator")
        >>> if result:
        >>>     best_link, breakdown = result
        >>>     print(f"Chosen link: {best_link.id}, reason: {breakdown.reason}")
    """
    if not node.outgoing_links:
        return None

    # Compute cost for each outgoing link (entity-aware when current_entity_id provided)
    link_costs = [
        (_compute_link_cost(link, goal_embedding, emotion_context, current_entity_id), link)
        for link in node.outgoing_links
    ]

    # Select link with minimum cost
    best_breakdown, best_link = min(link_costs, key=lambda x: x[0].total_cost)

    return (best_link, best_breakdown)


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
