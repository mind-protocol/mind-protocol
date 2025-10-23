"""
Two-Scale Traversal - Entity → Atomic Selection

ARCHITECTURAL PRINCIPLE: Traversal operates at two scales to reduce branching.

Phase 1 Implementation (shipped):
- Between-entity: Score entities by 5 hungers, pick next entity, select representative nodes
- Within-entity: Existing atomic stride selection constrained to entity members
- Budget split: Softmax over entity hungers determines entity allocation

This is the DEFAULT architecture (TWO_SCALE_ENABLED=true).

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/subentity_layer/subentity_layer.md §2.4
Status: STABLE (Phase 1 shipped, Phase 2 gated by flags)
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.subentity import Subentity
    from orchestration.core.node import Node


# === Phase 1: Slim Hunger Set ===

@dataclass
class EntityHungerScores:
    """
    Hunger scores for entity selection (Phase 1: 5 hungers).

    Each hunger ∈ [0, 1] represents motivation to activate this entity.
    Higher score = more attractive.
    """
    entity_id: str
    goal_fit: float  # Alignment with current goal embedding
    integration: float  # Semantic distance (novelty/complementarity)
    completeness: float  # How much of entity is already active
    ease: float  # Boundary precedence from RELATES_TO
    novelty: float  # Unexplored entity (low ema_active)
    total_score: float  # Softmax-weighted combination


def compute_goal_fit(
    entity: 'Subentity',
    goal_embedding: Optional[np.ndarray]
) -> float:
    """
    Compute goal alignment hunger (higher = more aligned).

    Uses cosine similarity between entity centroid and goal embedding.

    Args:
        entity: Candidate entity
        goal_embedding: Current goal vector

    Returns:
        Goal fit score ∈ [0, 1]
    """
    if goal_embedding is None or entity.centroid_embedding is None:
        return 0.5  # Neutral

    norm_goal = np.linalg.norm(goal_embedding)
    norm_entity = np.linalg.norm(entity.centroid_embedding)

    if norm_goal < 1e-9 or norm_entity < 1e-9:
        return 0.5

    cos_sim = np.dot(goal_embedding, entity.centroid_embedding) / (norm_goal * norm_entity)

    # Map [-1, 1] → [0, 1]
    return (cos_sim + 1.0) / 2.0


def compute_integration_hunger(
    current_entity: 'Subentity',
    candidate_entity: 'Subentity'
) -> float:
    """
    Compute integration hunger (semantic distance).

    Higher distance = more integration potential (novelty/complementarity).

    Args:
        current_entity: Entity we're currently in
        candidate_entity: Entity we're considering

    Returns:
        Integration score ∈ [0, 1] (higher = more distant/novel)
    """
    if (current_entity.centroid_embedding is None or
        candidate_entity.centroid_embedding is None):
        return 0.5  # Neutral

    norm_curr = np.linalg.norm(current_entity.centroid_embedding)
    norm_cand = np.linalg.norm(candidate_entity.centroid_embedding)

    if norm_curr < 1e-9 or norm_cand < 1e-9:
        return 0.5

    cos_sim = np.dot(current_entity.centroid_embedding, candidate_entity.centroid_embedding) / (norm_curr * norm_cand)

    # Distance = 1 - similarity (higher distance = more integration)
    return 1.0 - ((cos_sim + 1.0) / 2.0)


def compute_completeness_hunger(entity: 'Subentity') -> float:
    """
    Compute completeness hunger (how much already active).

    Lower completeness = more room to explore.

    Args:
        entity: Candidate entity

    Returns:
        Completeness score ∈ [0, 1] (higher = more incomplete)
    """
    if entity.member_count == 0:
        return 0.0

    # Get active members (E >= theta)
    from orchestration.core.types import LinkType
    active_count = sum(
        1 for link in entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO and link.source.is_active()
    )

    completeness_ratio = active_count / entity.member_count

    # Invert: high incompleteness = high hunger
    return 1.0 - completeness_ratio


def compute_ease_hunger(
    current_entity: 'Subentity',
    candidate_entity: 'Subentity',
    graph: 'Graph'
) -> float:
    """
    Compute ease hunger (boundary precedence from RELATES_TO).

    Strong RELATES_TO link = easy to traverse = high hunger.

    Args:
        current_entity: Entity we're currently in
        candidate_entity: Entity we're considering
        graph: Graph containing RELATES_TO links

    Returns:
        Ease score ∈ [0, 1]
    """
    from orchestration.core.types import LinkType

    # Find RELATES_TO link
    for link in current_entity.outgoing_links:
        if (link.link_type == LinkType.RELATES_TO and
            link.target.id == candidate_entity.id):
            # Found link - convert log_weight to ease
            ease = math.exp(link.log_weight)
            # Normalize to [0, 1] (assuming log_weight ∈ [-5, 2])
            normalized = (ease - 0.007) / (7.4 - 0.007)  # exp(-5) to exp(2)
            return np.clip(normalized, 0.0, 1.0)

    # No link = neutral ease
    return 0.5


def compute_novelty_hunger(entity: 'Subentity') -> float:
    """
    Compute novelty hunger (unexplored entity).

    Low ema_active = high novelty = high hunger.

    Args:
        entity: Candidate entity

    Returns:
        Novelty score ∈ [0, 1]
    """
    # Invert ema_active: low activation history = high novelty
    return 1.0 - entity.ema_active


def score_entity_hungers(
    current_entity: Optional['Subentity'],
    candidate_entity: 'Subentity',
    goal_embedding: Optional[np.ndarray],
    graph: 'Graph',
    hunger_weights: Optional[Dict[str, float]] = None
) -> EntityHungerScores:
    """
    Score candidate entity across all hungers (Phase 1: 5 hungers).

    Args:
        current_entity: Entity we're currently in (None if first selection)
        candidate_entity: Entity to score
        goal_embedding: Current goal vector
        graph: Graph containing entities and links
        hunger_weights: Optional weights for each hunger (default: uniform)

    Returns:
        EntityHungerScores with individual and total scores
    """
    if hunger_weights is None:
        hunger_weights = {
            "goal_fit": 0.25,
            "integration": 0.20,
            "completeness": 0.20,
            "ease": 0.20,
            "novelty": 0.15
        }

    # Compute individual hungers
    goal_fit = compute_goal_fit(candidate_entity, goal_embedding)

    integration = 0.5  # Default if no current entity
    if current_entity:
        integration = compute_integration_hunger(current_entity, candidate_entity)

    completeness = compute_completeness_hunger(candidate_entity)

    ease = 0.5  # Default if no current entity
    if current_entity:
        ease = compute_ease_hunger(current_entity, candidate_entity, graph)

    novelty = compute_novelty_hunger(candidate_entity)

    # Weighted total
    total_score = (
        hunger_weights["goal_fit"] * goal_fit +
        hunger_weights["integration"] * integration +
        hunger_weights["completeness"] * completeness +
        hunger_weights["ease"] * ease +
        hunger_weights["novelty"] * novelty
    )

    return EntityHungerScores(
        entity_id=candidate_entity.id,
        goal_fit=goal_fit,
        integration=integration,
        completeness=completeness,
        ease=ease,
        novelty=novelty,
        total_score=total_score
    )


def choose_next_entity(
    current_entity: Optional['Subentity'],
    active_entities: List['Subentity'],
    goal_embedding: Optional[np.ndarray],
    graph: 'Graph',
    hunger_weights: Optional[Dict[str, float]] = None
) -> Tuple[Optional['Subentity'], Optional[EntityHungerScores]]:
    """
    Choose next entity to expand using hunger-based scoring (Phase 1).

    Algorithm:
    1. Score all active entities (or all entities if no current)
    2. Apply softmax to get distribution
    3. Sample from distribution (deterministic: argmax for now)

    Args:
        current_entity: Current entity (None if first selection)
        active_entities: Entities above threshold
        goal_embedding: Current goal vector
        graph: Graph containing entities
        hunger_weights: Optional hunger weights

    Returns:
        Tuple of (selected_entity, scores) or (None, None) if no candidates
    """
    if not active_entities:
        return (None, None)

    # Score all candidates
    scored = [
        (entity, score_entity_hungers(current_entity, entity, goal_embedding, graph, hunger_weights))
        for entity in active_entities
        if entity != current_entity  # Don't select current entity
    ]

    if not scored:
        return (None, None)

    # Sort by total score (deterministic argmax for Phase 1)
    scored.sort(key=lambda x: x[1].total_score, reverse=True)

    # TODO Phase 2: Sample from softmax distribution instead of argmax
    best_entity, best_scores = scored[0]

    return (best_entity, best_scores)


def select_representative_nodes(
    source_entity: 'Subentity',
    target_entity: 'Subentity'
) -> Tuple[Optional['Node'], Optional['Node']]:
    """
    Select representative nodes for boundary stride (Phase 1 strategy).

    Strategy:
    - Source: Highest-E active member (E >= theta)
    - Target: Member with largest (gap-to-theta) × ease

    Args:
        source_entity: Entity energy flows from
        target_entity: Entity energy flows to

    Returns:
        Tuple of (source_node, target_node) or (None, None) if no valid pair
    """
    from orchestration.core.types import LinkType

    # Get source members (active only)
    source_members = [
        link.source for link in source_entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO and link.source.is_active()
    ]

    if not source_members:
        return (None, None)

    # Source: max E_i
    source_node = max(source_members, key=lambda n: n.E)

    # Get target members
    target_members = [
        link.source for link in target_entity.incoming_links
        if link.link_type == LinkType.BELONGS_TO
    ]

    if not target_members:
        return (None, None)

    # Target: max (gap × ease)
    # Gap = theta - E (how much room to fill)
    # Ease = average incoming link weight
    def score_target(node):
        gap = max(0.0, node.theta - node.E)

        # Ease: average exp(log_weight) of incoming links
        if not node.incoming_links:
            ease = 1.0
        else:
            ease = sum(math.exp(link.log_weight) for link in node.incoming_links) / len(node.incoming_links)

        return gap * ease

    target_node = max(target_members, key=score_target)

    return (source_node, target_node)


def split_stride_budget_by_entity(
    entity_scores: List[EntityHungerScores],
    total_budget: int
) -> Dict[str, int]:
    """
    Split stride budget across entities using softmax over hunger scores.

    Args:
        entity_scores: List of scored entities
        total_budget: Total strides available this frame

    Returns:
        Dict of entity_id → stride_budget
    """
    if not entity_scores:
        return {}

    # Softmax over total scores
    scores = np.array([s.total_score for s in entity_scores])
    exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
    softmax = exp_scores / exp_scores.sum()

    # Allocate budget proportionally
    budget_allocation = {}
    remaining_budget = total_budget

    for i, entity_score in enumerate(entity_scores):
        allocated = int(softmax[i] * total_budget)
        budget_allocation[entity_score.entity_id] = allocated
        remaining_budget -= allocated

    # Distribute remainder to highest-scored entity
    if remaining_budget > 0 and entity_scores:
        top_entity = max(entity_scores, key=lambda s: s.total_score)
        budget_allocation[top_entity.entity_id] += remaining_budget

    return budget_allocation


# === PR-B: Coherence Persistence Tracking ===

def update_coherence_persistence(
    entity: 'Subentity',
    current_affect: Optional[np.ndarray]
) -> None:
    """
    Update coherence persistence counter (PR-B: Emotion Couplings).

    Tracks consecutive frames where affect remains similar (coherence lock-in risk).
    Increments counter when cos(A_curr, A_prev) > threshold.
    Resets counter when affect changes significantly.

    Args:
        entity: Subentity to update
        current_affect: Current affective state vector

    Side effects:
        - Updates entity.coherence_persistence (increments or resets)
        - Updates entity.prev_affect_for_coherence (stores current)
    """
    from orchestration.core.settings import settings

    # Feature flag check
    if not settings.RES_DIMINISH_ENABLED:
        return

    # Guard: need current affect
    if current_affect is None or len(current_affect) == 0:
        entity.coherence_persistence = 0
        entity.prev_affect_for_coherence = None
        return

    # First frame: store affect, no persistence yet
    if entity.prev_affect_for_coherence is None:
        entity.prev_affect_for_coherence = current_affect.copy()
        entity.coherence_persistence = 0
        return

    # Compute cosine similarity with previous affect
    curr_norm = np.linalg.norm(current_affect)
    prev_norm = np.linalg.norm(entity.prev_affect_for_coherence)

    if curr_norm < 1e-6 or prev_norm < 1e-6:
        # Affect too weak, reset
        entity.coherence_persistence = 0
        entity.prev_affect_for_coherence = current_affect.copy()
        return

    dot_product = np.dot(current_affect, entity.prev_affect_for_coherence)
    cos_similarity = dot_product / (curr_norm * prev_norm)

    # Check if still coherent (same affective state)
    if cos_similarity > settings.COHERENCE_SIMILARITY_THRESHOLD:
        # Same state: increment persistence counter
        entity.coherence_persistence += 1
    else:
        # State changed: reset counter
        entity.coherence_persistence = 0

    # Store current affect for next frame
    entity.prev_affect_for_coherence = current_affect.copy()


def compute_effective_lambda_res(
    entity: 'Subentity',
    base_lambda_res: float = 0.5
) -> float:
    """
    Compute effective resonance strength with coherence diminishing returns (PR-B).

    After P frames of coherence persistence, resonance strength decays exponentially
    to prevent lock-in (rumination, obsession, spiral).

    Formula:
        λ_res_effective = λ_res * exp(-γ * max(0, persistence - P))

    Where:
        - λ_res = base resonance strength (default 0.5)
        - γ = COHERENCE_DECAY_RATE (default 0.05)
        - P = COHERENCE_PERSISTENCE_THRESHOLD (default 20 frames)
        - persistence = consecutive frames in same affective state

    Returns λ_res when disabled or below threshold (no decay).

    Args:
        entity: Subentity with coherence persistence tracking
        base_lambda_res: Base resonance strength (default 0.5)

    Returns:
        Effective resonance strength (decayed if persistence > P)

    Example:
        >>> entity.coherence_persistence = 25  # 5 frames over threshold
        >>> lambda_res_eff = compute_effective_lambda_res(entity, 0.5)
        >>> # lambda_res_eff = 0.5 * exp(-0.05 * 5) = 0.5 * 0.78 = 0.39
        >>> # 22% reduction (diminishing returns kicking in)
    """
    from orchestration.core.settings import settings
    from orchestration.core.telemetry import get_emitter

    # Feature flag check
    if not settings.RES_DIMINISH_ENABLED:
        return base_lambda_res

    # Compute excess persistence (frames beyond threshold)
    P = settings.COHERENCE_PERSISTENCE_THRESHOLD
    excess = max(0, entity.coherence_persistence - P)

    if excess == 0:
        # Below threshold: no decay
        lambda_res_effective = base_lambda_res
        lock_in_risk = False
    else:
        # Above threshold: exponential decay
        gamma = settings.COHERENCE_DECAY_RATE
        decay_factor = np.exp(-gamma * excess)
        lambda_res_effective = base_lambda_res * decay_factor
        lock_in_risk = (entity.coherence_persistence > P + 10)  # Warning at P+10

    # Emit telemetry event
    if settings.AFFECTIVE_TELEMETRY_ENABLED:
        emitter = get_emitter()
        emitter.emit_affective_event(
            "coherence_persistence",
            citizen_id="unknown",  # Will be set by caller
            frame_id=None,  # Will be set by caller
            entity_id=entity.id,
            coherence_persistence=entity.coherence_persistence,
            lambda_res_effective=float(lambda_res_effective),
            lock_in_risk=lock_in_risk
        )

    return float(lambda_res_effective)


# === PR-C: Multi-Pattern Affective Response ===

def compute_regulation_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float
) -> float:
    """
    Compute regulation pattern score (PR-C: Multi-Pattern Response).

    Regulation pattern: Intentional dampening of emotional response.
    Works when control capacity is high.

    Formula:
        score_reg = control_capacity * (1 - tanh(||A||))

    High control + low affect → high regulation score
    (System has capacity to regulate)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]

    Returns:
        Regulation pattern score [0, 1]

    Example:
        >>> A = np.array([0.2, 0.0, 0.0])  # Weak affect
        >>> score = compute_regulation_pattern(A, 0.5, 0.8)
        >>> # High control, low affect → good regulation opportunity
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Regulation score: high control × low affect
    # tanh(||A||) → [0, 1], so (1 - tanh(||A||)) → [1, 0]
    # More affect → harder to regulate
    regulation_potential = 1.0 - np.tanh(A_magnitude)
    score = control_capacity * regulation_potential

    return float(np.clip(score, 0.0, 1.0))


def compute_rumination_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    valence: float
) -> float:
    """
    Compute rumination pattern score (PR-C: Multi-Pattern Response).

    Rumination pattern: Intensification of negative affect.
    Occurs when valence negative and affect strong.

    Formula:
        score_rum = max(0, -valence) * tanh(||A||)

    Negative valence + strong affect → high rumination score
    (System spiraling into negative state)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        valence: Emotional valence [-1, 1] (negative = bad)

    Returns:
        Rumination pattern score [0, 1]

    Example:
        >>> A = np.array([1.0, 0.0, 0.0])  # Strong affect
        >>> score = compute_rumination_pattern(A, 0.8, -0.7)
        >>> # Negative valence + strong affect → rumination risk
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Rumination score: negative valence × strong affect
    # Only ruminate when valence < 0 (negative state)
    negative_intensity = max(0.0, -valence)
    affect_strength = np.tanh(A_magnitude)
    score = negative_intensity * affect_strength

    return float(np.clip(score, 0.0, 1.0))


def compute_distraction_pattern(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float
) -> float:
    """
    Compute distraction pattern score (PR-C: Multi-Pattern Response).

    Distraction pattern: Shift attention away from current affect.
    Works when regulation insufficient but some control remains.

    Formula:
        score_dist = (1 - control_capacity) * tanh(||A||) * max(0, -valence)

    Low control + strong negative affect → high distraction score
    (Can't regulate, need to redirect attention)

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]

    Returns:
        Distraction pattern score [0, 1]

    Example:
        >>> A = np.array([0.8, 0.0, 0.0])  # Strong affect
        >>> score = compute_distraction_pattern(A, 0.7, 0.3, -0.6)
        >>> # Low control + strong negative → distraction needed
    """
    A_magnitude = float(np.linalg.norm(active_affect))

    # Distraction score: low control × strong negative affect
    depletion = 1.0 - control_capacity  # Inverted control
    affect_strength = np.tanh(A_magnitude)
    negative_intensity = max(0.0, -valence)

    score = depletion * affect_strength * negative_intensity

    return float(np.clip(score, 0.0, 1.0))


def compute_pattern_scores(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float
) -> tuple[float, float, float]:
    """
    Compute all three pattern scores.

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]

    Returns:
        Tuple of (score_reg, score_rum, score_dist)
    """
    score_reg = compute_regulation_pattern(active_affect, emotion_magnitude, control_capacity)
    score_rum = compute_rumination_pattern(active_affect, emotion_magnitude, valence)
    score_dist = compute_distraction_pattern(active_affect, emotion_magnitude, control_capacity, valence)

    return (score_reg, score_rum, score_dist)


def compute_pattern_weights(
    scores: tuple[float, float, float],
    pattern_effectiveness: Dict[str, float]
) -> np.ndarray:
    """
    Compute pattern weights using softmax over scores × effectiveness.

    Weights sum to 1.0 and represent probability of selecting each pattern.

    Args:
        scores: Tuple of (score_reg, score_rum, score_dist)
        pattern_effectiveness: EMA effectiveness for each pattern

    Returns:
        Numpy array of weights [w_reg, w_rum, w_dist]

    Example:
        >>> scores = (0.8, 0.3, 0.2)
        >>> eff = {"regulation": 0.7, "rumination": 0.5, "distraction": 0.6}
        >>> weights = compute_pattern_weights(scores, eff)
        >>> # weights sum to 1.0, regulation dominant
    """
    score_reg, score_rum, score_dist = scores

    # Modulate scores by effectiveness
    eff_reg = pattern_effectiveness.get("regulation", 0.5)
    eff_rum = pattern_effectiveness.get("rumination", 0.5)
    eff_dist = pattern_effectiveness.get("distraction", 0.5)

    adjusted_scores = np.array([
        score_reg * eff_reg,
        score_rum * eff_rum,
        score_dist * eff_dist
    ])

    # Softmax (with numerical stability)
    exp_scores = np.exp(adjusted_scores - np.max(adjusted_scores))
    weights = exp_scores / exp_scores.sum()

    return weights


def compute_unified_multiplier(
    active_affect: np.ndarray,
    emotion_magnitude: float,
    control_capacity: float,
    valence: float,
    pattern_weights: np.ndarray
) -> float:
    """
    Compute unified affective multiplier using weighted pattern combination (PR-C).

    This REPLACES the simple m_affect from PR-B when PR-C is enabled.

    Formula:
        m_reg = 1 - λ_reg * tanh(||A||)  # Dampening
        m_rum = 1 + λ_rum * tanh(||A||) * max(0, -valence)  # Intensification
        m_dist = 1 - λ_dist * tanh(||A||) * (1 - control_capacity)  # Dampening via attention shift

        m_affect_unified = w_reg * m_reg + w_rum * m_rum + w_dist * m_dist

    Bounded by [M_AFFECT_MIN, M_AFFECT_MAX].

    Args:
        active_affect: Current affective state vector
        emotion_magnitude: Magnitude of emotion vector
        control_capacity: Available control capacity [0, 1]
        valence: Emotional valence [-1, 1]
        pattern_weights: Softmax weights [w_reg, w_rum, w_dist]

    Returns:
        Unified affective multiplier (clamped to bounds)
    """
    from orchestration.core.settings import settings

    A_magnitude = float(np.linalg.norm(active_affect))
    A_tanh = np.tanh(A_magnitude)

    # Compute individual pattern multipliers
    lambda_reg = settings.LAMBDA_REG
    lambda_rum = settings.LAMBDA_RUM
    lambda_dist = settings.LAMBDA_DIST

    # Regulation: dampens response (m < 1)
    m_reg = 1.0 - lambda_reg * A_tanh

    # Rumination: intensifies negative response (m > 1 when valence < 0)
    negative_intensity = max(0.0, -valence)
    m_rum = 1.0 + lambda_rum * A_tanh * negative_intensity

    # Distraction: dampens via attention shift (m < 1 when control low)
    depletion = 1.0 - control_capacity
    m_dist = 1.0 - lambda_dist * A_tanh * depletion

    # Weighted combination
    w_reg, w_rum, w_dist = pattern_weights
    m_affect_unified = w_reg * m_reg + w_rum * m_rum + w_dist * m_dist

    # Clamp to bounds
    m_min = settings.M_AFFECT_MIN
    m_max = settings.M_AFFECT_MAX
    m_affect_unified = np.clip(m_affect_unified, m_min, m_max)

    return float(m_affect_unified)


def apply_rumination_cap(
    entity: 'Subentity',
    selected_pattern: str,
    pattern_weights: np.ndarray
) -> np.ndarray:
    """
    Apply rumination cap: force weight to 0 after consecutive threshold.

    Safety mechanism to prevent indefinite rumination spirals.

    Args:
        entity: Subentity with rumination counter
        selected_pattern: Currently dominant pattern
        pattern_weights: Current weights [w_reg, w_rum, w_dist]

    Returns:
        Adjusted weights (rumination zeroed if cap exceeded)

    Side effects:
        - Updates entity.rumination_frames_consecutive
    """
    from orchestration.core.settings import settings

    if selected_pattern == "rumination":
        entity.rumination_frames_consecutive += 1
    else:
        entity.rumination_frames_consecutive = 0

    # Check if cap exceeded
    if entity.rumination_frames_consecutive >= settings.RUMINATION_CAP:
        # Force rumination weight to 0, renormalize
        adjusted_weights = pattern_weights.copy()
        adjusted_weights[1] = 0.0  # Zero out rumination (index 1)

        # Renormalize remaining weights
        total = adjusted_weights.sum()
        if total > 0:
            adjusted_weights = adjusted_weights / total
        else:
            # Fallback: equal weights for reg/dist
            adjusted_weights = np.array([0.5, 0.0, 0.5])

        return adjusted_weights

    return pattern_weights


def get_selected_pattern(pattern_weights: np.ndarray) -> str:
    """
    Get selected pattern name based on weights.

    Args:
        pattern_weights: Weights [w_reg, w_rum, w_dist]

    Returns:
        Pattern name ("regulation", "rumination", or "distraction")
    """
    max_idx = int(np.argmax(pattern_weights))
    pattern_names = ["regulation", "rumination", "distraction"]
    return pattern_names[max_idx]


def update_pattern_effectiveness(
    entity: 'Subentity',
    pattern_name: str,
    outcome_score: float
) -> None:
    """
    Update pattern effectiveness using EMA (PR-C: Pattern Learning).

    Effectiveness tracks how well each pattern achieves its goals:
    - Regulation: Did affect intensity decrease?
    - Rumination: Did it lead to spiraling (bad) or insight (good)?
    - Distraction: Did it enable recovery?

    Args:
        entity: Subentity with pattern_effectiveness dict
        pattern_name: Pattern to update ("regulation", "rumination", "distraction")
        outcome_score: Success score [0, 1] (1 = pattern worked well)

    Side effects:
        - Updates entity.pattern_effectiveness[pattern_name] via EMA
    """
    from orchestration.core.settings import settings

    alpha = settings.PATTERN_EFFECTIVENESS_EMA_ALPHA

    # Get current effectiveness
    current_eff = entity.pattern_effectiveness.get(pattern_name, 0.5)

    # Update via EMA
    # new_eff = alpha * outcome + (1 - alpha) * old_eff
    new_eff = alpha * outcome_score + (1.0 - alpha) * current_eff

    # Clamp to [0, 1]
    new_eff = np.clip(new_eff, 0.0, 1.0)

    # Store
    entity.pattern_effectiveness[pattern_name] = float(new_eff)


def compute_regulation_outcome(
    affect_before: np.ndarray,
    affect_after: np.ndarray
) -> float:
    """
    Compute regulation outcome score (did affect decrease?).

    Args:
        affect_before: Affect magnitude before regulation
        affect_after: Affect magnitude after regulation

    Returns:
        Outcome score [0, 1] (1 = successful dampening)
    """
    mag_before = float(np.linalg.norm(affect_before))
    mag_after = float(np.linalg.norm(affect_after))

    if mag_before < 1e-6:
        return 0.5  # Neutral if no affect to begin with

    # Compute reduction ratio
    reduction = (mag_before - mag_after) / mag_before

    # Map to [0, 1] range
    # reduction > 0 → dampened (good), < 0 → intensified (bad)
    outcome = 0.5 + 0.5 * np.tanh(reduction)

    return float(np.clip(outcome, 0.0, 1.0))


def compute_rumination_outcome(
    affect_magnitude: float,
    spiral_detected: bool,
    insight_gained: bool
) -> float:
    """
    Compute rumination outcome score.

    Rumination can be:
    - Bad: Spiraling without insight (low score)
    - Good: Deep processing leading to insight (high score)

    Args:
        affect_magnitude: Current affect strength
        spiral_detected: True if affect spiraling upward
        insight_gained: True if pattern led to insight/resolution

    Returns:
        Outcome score [0, 1]
    """
    if insight_gained:
        return 0.8  # Productive rumination

    if spiral_detected:
        return 0.2  # Unproductive spiral

    # Neutral: rumination without clear outcome
    return 0.5


def compute_distraction_outcome(
    recovery_enabled: bool,
    attention_shifted: bool
) -> float:
    """
    Compute distraction outcome score (did it enable recovery?).

    Args:
        recovery_enabled: True if affect decreased after distraction
        attention_shifted: True if attention successfully redirected

    Returns:
        Outcome score [0, 1]
    """
    if recovery_enabled and attention_shifted:
        return 0.9  # Successful distraction

    if recovery_enabled or attention_shifted:
        return 0.6  # Partial success

    return 0.3  # Distraction didn't help
