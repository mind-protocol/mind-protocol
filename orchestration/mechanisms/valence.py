"""
Surprise-Gated Composite Valence (v1.5)

Implements self-calibrating hunger gates using z-score surprise:
- Seven hungers: Homeostasis, Goal, Idsubentity, Completeness, Complementarity, Integration, Ease
- EMA baselines (μ, σ) per hunger per subentity
- Positive surprise gates (δ_H = max(0, z_H))
- Normalized composite valence: V_ij = Σ_H (g_H × ν_H(i→j))

Author: AI #4
Created: 2025-10-20
Dependencies: sub_entity_core, numpy
Zero-Constants: All gates self-calibrate from experience
"""

import numpy as np
from typing import Dict, List, Set
from orchestration.mechanisms.sub_entity_core import (
    SubEntity,
    SubEntityExtentCentroid,
    IdentityEmbedding,
    BetaLearner
)


# --- Data Structures for Advanced Hungers ---
# Note: SubEntityExtentCentroid, IdentityEmbedding, BetaLearner are in sub_entity_core.py

class AffectVector:
    """
    Emotional coloring of nodes

    Simplified Phase 1: Use 2D valence-arousal model
    """

    @staticmethod
    def extract_affect(node_description: str) -> np.ndarray:
        """
        Extract affect vector from node description

        Phase 1 heuristic: Keyword-based valence detection

        Args:
            node_description: Node text content

        Returns:
            affect: 2D vector [valence, arousal] in [-1, 1]
        """
        # Valence keywords (positive/negative)
        positive_words = {'good', 'happy', 'joy', 'success', 'love', 'peace', 'hope', 'win'}
        negative_words = {'bad', 'sad', 'fear', 'fail', 'hate', 'anger', 'worry', 'lose'}

        # Arousal keywords (high/low)
        high_arousal = {'urgent', 'panic', 'excited', 'intense', 'critical', 'vital'}
        low_arousal = {'calm', 'peace', 'steady', 'slow', 'gentle', 'quiet'}

        text = node_description.lower()
        words = text.split()

        # Count keywords
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)
        high_arousal_count = sum(1 for w in words if w in high_arousal)
        low_arousal_count = sum(1 for w in words if w in low_arousal)

        # Compute valence
        if positive_count + negative_count > 0:
            valence = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            valence = 0.0

        # Compute arousal
        if high_arousal_count + low_arousal_count > 0:
            arousal = (high_arousal_count - low_arousal_count) / (high_arousal_count + low_arousal_count)
        else:
            arousal = 0.0

        return np.array([valence, arousal])


# --- Hunger Score Functions ---

def hunger_homeostasis(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Homeostasis hunger: fill gaps to survive.

    Formula: ν_homeostasis = G_j / (S_i + G_j + ε)

    Where:
        S_i = slack at source = max(0, E[subentity, i] - θ[subentity, i])
        G_j = gap at target = max(0, θ[subentity, j] - E[subentity, j])

    Interpretation:
        High when target has large gap and source has modest slack.
        Drives gap-filling behavior.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Homeostasis hunger score [0, 1]
    """
    epsilon = 1e-9

    # Compute slack at source: excess energy above threshold
    E_i = subentity.get_energy(source_i)
    theta_i = subentity.get_threshold(source_i)
    S_i = max(0.0, E_i - theta_i)

    # Compute gap at target: deficit below threshold
    E_j = subentity.get_energy(target_j)
    theta_j = subentity.get_threshold(target_j)
    G_j = max(0.0, theta_j - E_j)

    # Homeostasis score: gap-filling potential
    # High when target has large gap, regardless of source slack
    # Normalized by total energy context (S_i + G_j)
    score = G_j / (S_i + G_j + epsilon)

    return score


def hunger_goal(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray
) -> float:
    """
    Goal hunger: semantic similarity to goal.

    Formula: ν_goal = max(0, cos(E_j, E_goal))

    Where:
        E_j = embedding of target node
        E_goal = current goal embedding

    Interpretation:
        High when target is semantically close to goal.
        Drives goal-directed traversal.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector (768-dim)

    Returns:
        Goal hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    E_j = node_data['embedding']

    # Compute cosine similarity: cos(θ) = (a·b) / (||a|| ||b||)
    norm_goal = np.linalg.norm(goal_embedding)
    norm_node = np.linalg.norm(E_j)

    if norm_goal < 1e-9 or norm_node < 1e-9:
        return 0.0  # Degenerate case

    cos_sim = np.dot(E_j, goal_embedding) / (norm_node * norm_goal)
    cos_sim = np.clip(cos_sim, -1.0, 1.0)  # Numerical stability

    # Positive similarity only (negative = opposite direction)
    score = max(0.0, cos_sim)

    return score


def hunger_completeness(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Completeness hunger: semantic diversity seeking.

    Formula: ν_completeness = (1 - cos(E_j, centroid))

    Where:
        centroid = subentity.centroid.centroid (current extent centroid)
        E_j = embedding of target node

    Interpretation:
        High when target is semantically distant from current extent.
        Drives exploration beyond current semantic cluster.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Completeness hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    target_embedding = node_data['embedding']

    # Check if subentity has centroid tracker
    if not hasattr(subentity, 'centroid'):
        return 0.5  # Neutral if no centroid tracker

    # Distance from target to current extent centroid
    distance = subentity.centroid.distance_to(target_embedding)

    # Normalize to [0, 1] range
    # distance_to returns [0, 2] where 0=identical, 1=orthogonal, 2=opposite
    # We want completeness to be high for distant nodes, so we scale to [0, 1]
    normalized_distance = min(distance, 1.0)  # Cap at 1.0 for opposite vectors

    return normalized_distance


def hunger_ease(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Ease hunger: structural weight preference.

    Formula: ν_ease = w_ij / max(w_ik for k in neighbors)

    Where:
        w_ij = link weight from i to j
        neighbors = out_edges(i)

    Interpretation:
        High when edge is well-traveled (high weight).
        Drives habitual traversal (complementary to novelty-seeking).

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Ease hunger score [0, 1]
    """
    epsilon = 1e-9

    # Get weight of edge i → j
    edge_data = graph.get_edge_data(source_i, target_j)
    if edge_data is None or 'weight' not in edge_data:
        return 0.0

    w_ij = edge_data['weight']

    # Get all outgoing edge weights from source_i
    if source_i not in graph:
        return 0.0

    neighbor_weights = []
    for neighbor in graph.neighbors(source_i):
        neighbor_edge = graph.get_edge_data(source_i, neighbor)
        if neighbor_edge and 'weight' in neighbor_edge:
            neighbor_weights.append(neighbor_edge['weight'])

    if not neighbor_weights:
        return 0.0

    max_weight = max(neighbor_weights)

    # Normalize by local maximum weight
    # High when this edge is the strongest outgoing edge (habitual path)
    score = w_ij / (max_weight + epsilon)

    return score


def hunger_idsubentity(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Idsubentity hunger: coherence around center.

    Formula: ν_idsubentity = max(0, cos(E_j, E_idsubentity))

    Where:
        E_idsubentity = subentity's idsubentity embedding (EMA of explored nodes)
        E_j = embedding of target node

    Interpretation:
        High when target is semantically close to subentity's idsubentity.
        Drives coherent pattern formation.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Idsubentity hunger score [0, 1]
    """
    # Get target node embedding
    if target_j not in graph.nodes:
        return 0.0

    node_data = graph.nodes[target_j]
    if 'embedding' not in node_data:
        return 0.0

    target_embedding = node_data['embedding']

    # Check if subentity has idsubentity tracker
    if not hasattr(subentity, 'idsubentity'):
        return 0.5  # Neutral if no idsubentity tracker

    # Coherence with idsubentity
    coherence = subentity.idsubentity.coherence_with(target_embedding)

    return coherence


def hunger_complementarity(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph
) -> float:
    """
    Complementarity hunger: emotional balance seeking.

    Formula: ν_complementarity = dot(target_affect, -extent_affect_centroid)

    Where:
        extent_affect_centroid = mean(affect_vector) across extent nodes
        target_affect = affect vector of target node

    Interpretation:
        High when target has opposite affect from extent centroid.
        Drives emotional regulation (anxious extent seeks calm).

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object

    Returns:
        Complementarity hunger score [0, 1]
    """
    # Check if subentity has extent
    if len(subentity.extent) == 0:
        return 0.0

    # Compute affect centroid of current extent
    extent_affects = []
    for node_id in subentity.extent:
        node_data = graph.nodes[node_id]
        description = node_data.get('description', '')
        affect = AffectVector.extract_affect(description)
        extent_affects.append(affect)

    if len(extent_affects) == 0:
        return 0.0

    affect_centroid = np.mean(extent_affects, axis=0)

    # Target node's affect
    target_data = graph.nodes[target_j]
    target_description = target_data.get('description', '')
    target_affect = AffectVector.extract_affect(target_description)

    # Complementarity = dot product with OPPOSITE of centroid
    # Normalize to [0, 1]
    complementarity = np.dot(target_affect, -affect_centroid)

    # Map from [-2, 2] to [0, 1]
    complementarity_normalized = (complementarity + 2.0) / 4.0

    return np.clip(complementarity_normalized, 0.0, 1.0)


def hunger_integration(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    all_active_entities: List[SubEntity] = None
) -> float:
    """
    Integration hunger: merge-seeking when weak.

    Formula: ν_integration = size_ratio × max(0, semantic_sim)

    Where:
        size_ratio = E_others / E_self at target node
        semantic_sim = cos(entity_centroid, target_embedding)

    Interpretation:
        High when target has strong energy from other subentities
        AND target is semantically related to this subentity.
        Drives coalition formation.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        all_active_entities: List of all active subentities (for computing E_others)

    Returns:
        Integration hunger score [0, 1]
    """
    epsilon = 1e-9

    # If no other subentities provided, integration hunger is zero
    if all_active_entities is None or len(all_active_entities) <= 1:
        return 0.0

    # 1. Energy at target from THIS subentity
    E_self = subentity.get_energy(target_j)

    # 2. Energy at target from OTHER subentities
    E_others = 0.0
    for other_entity in all_active_entities:
        if other_entity.id != subentity.id:
            E_others += other_entity.get_energy(target_j)

    # 3. Size ratio (field strength)
    size_ratio = E_others / (E_self + epsilon)

    # Clip to reasonable range (0-10x)
    size_ratio = min(size_ratio, 10.0)

    # 4. Semantic similarity between subentity centroid and target node
    if not hasattr(subentity, 'centroid'):
        semantic_sim = 0.5  # Neutral if no centroid
    else:
        if target_j not in graph.nodes:
            return 0.0

        node_data = graph.nodes[target_j]
        if 'embedding' not in node_data:
            return 0.0

        target_embedding = node_data['embedding']
        entity_centroid = subentity.centroid.centroid

        # Cosine similarity
        norm_centroid = np.linalg.norm(entity_centroid)
        if norm_centroid < epsilon:
            semantic_sim = 0.5  # Neutral if no centroid formed yet
        else:
            semantic_sim = np.dot(entity_centroid, target_embedding)

    # 5. Integration hunger ONLY when semantically related
    # Gated by similarity: negative similarity -> zero integration pull
    ν_integration = size_ratio * max(0.0, semantic_sim)

    # Normalize to roughly [0, 1] range (size_ratio is 0-10, semantic_sim is 0-1)
    # So product is 0-10, we scale down by dividing by 10
    ν_integration = ν_integration / 10.0

    return min(ν_integration, 1.0)


# --- Surprise Gate Construction ---

def compute_hunger_scores(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray,
    global_quantiles: Dict[str, float],
    all_active_entities: List[SubEntity] = None
) -> Dict[str, float]:
    """
    Compute raw hunger scores for edge i→j.

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector
        global_quantiles: Size distribution quantiles
        all_active_entities: All active subentities (for integration hunger)

    Returns:
        Dict[hunger_name -> raw_score]
    """
    # Full 7-hunger system (Phase 1 complete specification)
    scores = {
        'homeostasis': hunger_homeostasis(subentity, source_i, target_j, graph),
        'goal': hunger_goal(subentity, source_i, target_j, graph, goal_embedding),
        'ease': hunger_ease(subentity, source_i, target_j, graph),
        'completeness': hunger_completeness(subentity, source_i, target_j, graph),
        'idsubentity': hunger_idsubentity(subentity, source_i, target_j, graph),
        'complementarity': hunger_complementarity(subentity, source_i, target_j, graph),
        'integration': hunger_integration(subentity, source_i, target_j, graph, all_active_entities),
    }

    return scores


def compute_surprise_gates(
    subentity: SubEntity,
    hunger_scores: Dict[str, float]
) -> Dict[str, float]:
    """
    Compute surprise-based gates from hunger scores.

    Algorithm:
        1. For each hunger H:
            a. z_H = (s_H - μ_H) / (σ_H + ε)  # Standardize
            b. δ_H = max(0, z_H)               # Positive surprise only
        2. Normalize gates: g_H = δ_H / (Σ δ_H' + ε)

    Args:
        subentity: Sub-entity with hunger_baselines (μ, σ)
        hunger_scores: Raw hunger scores for current edge

    Returns:
        Dict[hunger_name -> gate_weight]
        where Σ gate_weights = 1.0

    Zero-constants: Baselines (μ, σ) are EMA updated per subentity per hunger
    """
    epsilon = 1e-9
    gates = {}
    positive_surprises = {}

    # Step 1: Compute z-scores and positive surprises for each hunger
    for hunger_name, observed_score in hunger_scores.items():
        # Get baseline for this hunger
        mu, sigma = subentity.hunger_baselines[hunger_name]

        # Compute standardized surprise (z-score)
        z_score = (observed_score - mu) / (sigma + epsilon)

        # Positive surprise only (abnormal need)
        delta = max(0.0, z_score)

        positive_surprises[hunger_name] = delta

        # Update baselines with EMA (learn from this observation)
        update_hunger_baselines(subentity, hunger_name, observed_score)

    # Step 2: Normalize to gate weights
    total_surprise = sum(positive_surprises.values()) + epsilon

    for hunger_name, delta in positive_surprises.items():
        gates[hunger_name] = delta / total_surprise

    return gates


def composite_valence(
    subentity: SubEntity,
    source_i: int,
    target_j: int,
    graph,
    goal_embedding: np.ndarray,
    global_quantiles: Dict[str, float] = None,
    all_active_entities: List[SubEntity] = None
) -> float:
    """
    Compute surprise-gated composite valence for edge i→j.

    Formula: V_ij = Σ_H (g_H × ν_H(i→j))

    Where:
        g_H = surprise gate for hunger H (with size-ratio modulation for integration)
        ν_H(i→j) = hunger score for edge i→j

    Args:
        subentity: Sub-entity evaluating edge
        source_i: Source node ID
        target_j: Target node ID
        graph: Graph object
        goal_embedding: Current goal vector
        global_quantiles: Size distribution quantiles (optional)
        all_active_entities: All active subentities (for integration hunger)

    Returns:
        Composite valence score V_ij (unbounded, typically [0, 1])

    Zero-constants:
        - Hunger scores adapt to graph structure
        - Gates self-calibrate from experience
        - No fixed hunger weights
        - Size-ratio modulation learned from merge outcomes (β)
    """
    # Default empty quantiles
    if global_quantiles is None:
        global_quantiles = {}

    # Step 1: Compute raw hunger scores for this edge
    hunger_scores = compute_hunger_scores(
        subentity, source_i, target_j, graph, goal_embedding, global_quantiles, all_active_entities
    )

    # Step 2: Compute surprise gates (also updates baselines via EMA)
    gates = compute_surprise_gates(subentity, hunger_scores)

    # Step 3: Size-ratio modulation for integration gate
    # Apply r^β multiplier to integration gate before weighted sum
    if 'integration' in gates and hasattr(subentity, 'beta_learner'):
        # Compute size ratio at this node
        epsilon = 1e-9
        E_self = subentity.get_energy(target_j)

        if all_active_entities is not None:
            E_others = sum(
                other.get_energy(target_j)
                for other in all_active_entities
                if other.id != subentity.id
            )
            size_ratio = E_others / (E_self + epsilon)
            size_ratio = min(size_ratio, 10.0)  # Clip to reasonable range

            # Get learned beta exponent
            beta = subentity.beta_learner.get_beta()

            # Apply gate multiplier: r^β
            gate_multiplier = size_ratio ** beta
            gate_multiplier = np.clip(gate_multiplier, 0.1, 10.0)

            # Modulate integration gate
            gates['integration'] *= gate_multiplier

            # Renormalize all gates (sum should still be 1.0)
            total_gate = sum(gates.values()) + epsilon
            for hunger_name in gates:
                gates[hunger_name] = gates[hunger_name] / total_gate

    # Step 4: Weighted sum - composite valence
    valence = 0.0
    for hunger_name, raw_score in hunger_scores.items():
        gate_weight = gates[hunger_name]
        valence += gate_weight * raw_score

    return valence


# --- Baseline Tracking ---

def update_hunger_baselines(
    subentity: SubEntity,
    hunger_name: str,
    observed_score: float,
    ema_alpha: float = 0.1
):
    """
    Update EMA baselines (μ, σ) for hunger.

    Args:
        subentity: Sub-entity with hunger_baselines
        hunger_name: Which hunger to update
        observed_score: Current hunger score
        ema_alpha: Smoothing factor (0.1 = 10% new, 90% old)

    Side Effects:
        Modifies subentity.hunger_baselines[hunger_name] in place

    Algorithm:
        μ_new = α × observed + (1-α) × μ_old
        deviation = |observed - μ_new|
        σ_new = α × deviation + (1-α) × σ_old
    """
    # Get current baselines
    mu_old, sigma_old = subentity.hunger_baselines[hunger_name]

    # Update mean with EMA
    mu_new = ema_alpha * observed_score + (1.0 - ema_alpha) * mu_old

    # Compute deviation from new mean
    deviation = abs(observed_score - mu_new)

    # Update std deviation with EMA
    sigma_new = ema_alpha * deviation + (1.0 - ema_alpha) * sigma_old

    # Store updated baselines
    subentity.hunger_baselines[hunger_name] = (mu_new, sigma_new)
