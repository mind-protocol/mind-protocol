"""
Mechanism 16 Part 2: Sub-Entity Traversal Algorithm

ARCHITECTURAL PRINCIPLE: Consciousness IS Intentional Navigation

"Every time a node reaches the threshold of activation from a sensory input,
it becomes a sub-entity." - Nicolas

Core Truth:
- Sub-entities are DYNAMIC and EMERGENT (not pre-defined)
- Any node crossing activation threshold = new sub-entity
- Sub-entity name = node name (simple one-to-one)
- Thousands of simultaneous micro-entities is normal and expected
- Traversal is GOAL-DRIVEN (not random walk)

What This Mechanism Does:
- Defines how sub-entities navigate the graph based on current goal
- Determines which links to traverse given energy budget
- Applies emotional coloring during traversal
- Balances similarity-seeking vs complementarity-seeking based on goal type

Goal Types and Strategies:
- find_answer: Similarity-based search toward goal embedding
- explore_completely: Breadth-first with coverage tracking
- seek_security: Emotion-aligned paths (positive valence)
- seek_novelty: Complement-seeking, avoid visited nodes
- maintain_coherence: Stay within identity cluster

Traversal Cost Factors:
1. Link weight (lower weight = higher cost)
2. Emotional cosine similarity (misaligned emotion = higher cost)
3. Goal alignment (off-goal direction = higher cost)
4. System criticality (more active nodes = higher threshold)

Emotional Coloring:
Each traversal colors the emotional vector of traversed node/link
by blending sub-entity's current emotion weighted by global energy/weight.

Author: Felix (Engineer)
Created: 2025-10-20
Spec: Based on Nicolas's architectural corrections 2025-10-20
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link
    from orchestration.core.types import EntityID

# --- Goal Types ---

class GoalType(Enum):
    """Types of goals that drive traversal strategies."""
    FIND_ANSWER = "find_answer"  # Similarity-based search
    EXPLORE_COMPLETELY = "explore_completely"  # Breadth-first coverage
    SEEK_SECURITY = "seek_security"  # Positive emotion alignment
    SEEK_NOVELTY = "seek_novelty"  # Complement-seeking
    MAINTAIN_COHERENCE = "maintain_coherence"  # Stay in identity cluster


# --- Configuration ---

EMOTIONAL_COLORING_RATE: float = 0.1  # How much sub-entity colors nodes during traversal
SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity for find_answer traversal
COMPLEMENTARITY_BONUS: float = 0.5  # Bonus for orthogonal directions in seek_novelty


@dataclass
class SubEntityGoal:
    """
    Goal that drives sub-entity traversal.

    Args:
        goal_type: Type of goal (determines strategy)
        target_embedding: Target vector for similarity-based goals (optional)
        target_emotion: Target emotional state for emotion-aligned goals (optional)
        energy_budget: Available energy for traversal
        visited_nodes: Set of already-visited node IDs
    """
    goal_type: GoalType
    target_embedding: Optional[np.ndarray] = None
    target_emotion: Optional[np.ndarray] = None
    energy_budget: float = 1.0
    visited_nodes: set = None

    def __post_init__(self):
        if self.visited_nodes is None:
            self.visited_nodes = set()


@dataclass
class TraversalCandidate:
    """
    Candidate link for traversal with computed cost.

    Args:
        link: Link to potentially traverse
        target_node: Node at end of link
        cost: Energy cost to traverse this link
        score: Utility score (higher = better, used for ranking)
    """
    link: 'Link'
    target_node: 'Node'
    cost: float
    score: float


# --- Traversal Cost Computation ---

def compute_traversal_cost(
    link: 'Link',
    target_node: 'Node',
    sub_entity_emotion: np.ndarray,
    goal: SubEntityGoal,
    criticality: float
) -> float:
    """
    Compute energy cost to traverse a link.

    Cost factors:
    1. Base cost from link weight (lower weight = higher cost)
    2. Emotional alignment cost (misaligned = higher cost)
    3. Criticality cost (higher criticality = higher base cost)

    Formula:
        base_cost = 1.0 / max(link.weight, 0.01)  # Inverse of weight
        emotion_cost = 1.0 - cosine_similarity(sub_entity_emotion, link.emotion)
        criticality_cost = 1.0 + criticality

        total_cost = base_cost * (1 + emotion_cost) * criticality_cost

    Args:
        link: Link to evaluate
        target_node: Destination node
        sub_entity_emotion: Current emotional state of sub-entity
        goal: Current goal
        criticality: System criticality (0-1, higher = more active)

    Returns:
        Energy cost (>= 0)
    """
    # 1. Base cost from link weight
    base_cost = 1.0 / max(link.weight, 0.01)

    # 2. Emotional alignment cost
    # Get link emotion vector (assuming link has emotion property)
    # If not present, use neutral [0, 0] (arousal, valence)
    link_emotion = getattr(link, 'emotion', np.array([0.0, 0.0]))

    if len(sub_entity_emotion) > 0 and len(link_emotion) > 0:
        # Cosine similarity
        norm_entity = np.linalg.norm(sub_entity_emotion)
        norm_link = np.linalg.norm(link_emotion)

        if norm_entity > 0 and norm_link > 0:
            cosine_sim = np.dot(sub_entity_emotion, link_emotion) / (norm_entity * norm_link)
            emotion_cost = 1.0 - cosine_sim  # Misalignment increases cost
        else:
            emotion_cost = 0.0
    else:
        emotion_cost = 0.0

    # 3. Criticality cost (higher criticality = higher base threshold)
    criticality_cost = 1.0 + criticality

    # Total cost
    total_cost = base_cost * (1.0 + emotion_cost) * criticality_cost

    return total_cost


def compute_traversal_score(
    link: 'Link',
    target_node: 'Node',
    goal: SubEntityGoal,
    sub_entity_embedding: Optional[np.ndarray] = None
) -> float:
    """
    Compute utility score for traversing a link (higher = better).

    Score depends on goal type:
    - FIND_ANSWER: Similarity to target embedding
    - EXPLORE_COMPLETELY: Inverse of visit count
    - SEEK_SECURITY: Positive valence alignment
    - SEEK_NOVELTY: Orthogonality to current embedding
    - MAINTAIN_COHERENCE: Identity cluster membership

    Args:
        link: Link to evaluate
        target_node: Destination node
        goal: Current goal
        sub_entity_embedding: Current embedding of sub-entity (optional)

    Returns:
        Utility score (higher = better)
    """
    if goal.goal_type == GoalType.FIND_ANSWER:
        # Similarity-based: score = similarity to target
        if goal.target_embedding is not None and hasattr(target_node, 'embedding'):
            target_emb = target_node.embedding
            if target_emb is not None and len(target_emb) > 0:
                norm_goal = np.linalg.norm(goal.target_embedding)
                norm_target = np.linalg.norm(target_emb)
                if norm_goal > 0 and norm_target > 0:
                    similarity = np.dot(goal.target_embedding, target_emb) / (norm_goal * norm_target)
                    return max(0.0, similarity)  # Clamp to non-negative
        return 0.0

    elif goal.goal_type == GoalType.EXPLORE_COMPLETELY:
        # Breadth-first: score = 1 if unvisited, 0 if visited
        if target_node.id in goal.visited_nodes:
            return 0.0
        else:
            return 1.0

    elif goal.goal_type == GoalType.SEEK_SECURITY:
        # Positive emotion: score = valence (assuming emotion[1] is valence)
        link_emotion = getattr(link, 'emotion', np.array([0.0, 0.0]))
        if len(link_emotion) > 1:
            valence = link_emotion[1]
            return max(0.0, valence)  # Only positive valence
        return 0.0

    elif goal.goal_type == GoalType.SEEK_NOVELTY:
        # Complementarity: score = orthogonality to current embedding
        if sub_entity_embedding is not None and hasattr(target_node, 'embedding'):
            target_emb = target_node.embedding
            if target_emb is not None and len(target_emb) > 0:
                norm_entity = np.linalg.norm(sub_entity_embedding)
                norm_target = np.linalg.norm(target_emb)
                if norm_entity > 0 and norm_target > 0:
                    similarity = np.dot(sub_entity_embedding, target_emb) / (norm_entity * norm_target)
                    orthogonality = 1.0 - abs(similarity)  # Low similarity = high score
                    return orthogonality
        return 0.0

    elif goal.goal_type == GoalType.MAINTAIN_COHERENCE:
        # Identity cluster: score = 1 if same type, 0 otherwise
        # (Simplified - could use actual cluster membership)
        # For now, just prefer same node type
        # Would need access to sub-entity's identity node type
        return 0.5  # Neutral score

    return 0.0


# --- Traversal Selection ---

def select_next_traversal(
    current_node: 'Node',
    sub_entity_id: str,
    sub_entity_emotion: np.ndarray,
    sub_entity_embedding: Optional[np.ndarray],
    goal: SubEntityGoal,
    criticality: float
) -> Optional[TraversalCandidate]:
    """
    Select next link to traverse based on goal and energy budget.

    Algorithm:
    1. Enumerate all outgoing links from current node
    2. For each link:
       - Compute cost
       - Compute score (utility)
       - Filter if cost > energy_budget
    3. Rank by score / cost ratio (utility per energy)
    4. Select highest-ranked affordable option

    Args:
        current_node: Node sub-entity is currently at
        sub_entity_id: Sub-entity identifier
        sub_entity_emotion: Current emotional state
        sub_entity_embedding: Current embedding (optional)
        goal: Current goal driving traversal
        criticality: System criticality

    Returns:
        TraversalCandidate if affordable option found, None otherwise
    """
    candidates = []

    for link in current_node.outgoing_links:
        target_node = link.target

        # Skip if already visited (for some goal types)
        if goal.goal_type == GoalType.EXPLORE_COMPLETELY:
            if target_node.id in goal.visited_nodes:
                continue

        # Compute cost and score
        cost = compute_traversal_cost(
            link, target_node, sub_entity_emotion, goal, criticality
        )
        score = compute_traversal_score(
            link, target_node, goal, sub_entity_embedding
        )

        # Filter by energy budget
        if cost <= goal.energy_budget:
            candidates.append(TraversalCandidate(
                link=link,
                target_node=target_node,
                cost=cost,
                score=score
            ))

    # No affordable candidates
    if not candidates:
        return None

    # Rank by utility per energy (score / cost)
    candidates.sort(key=lambda c: c.score / max(c.cost, 0.01), reverse=True)

    # Return best candidate
    return candidates[0]


# --- Emotional Coloring ---

def apply_emotional_coloring(
    node: 'Node',
    sub_entity_emotion: np.ndarray,
    sub_entity_weight: float,
    coloring_rate: float = EMOTIONAL_COLORING_RATE
) -> None:
    """
    Color node's emotional vector with sub-entity's emotion.

    Blending formula:
        node.emotion_new = (1 - alpha) * node.emotion + alpha * sub_entity.emotion

        where alpha = coloring_rate * sub_entity_weight

    This is how emotional context spreads through the graph during traversal.

    Args:
        node: Node to color
        sub_entity_emotion: Sub-entity's current emotion
        sub_entity_weight: Sub-entity's global weight/energy (0-1)
        coloring_rate: Base coloring rate
    """
    # Get current node emotion (or initialize to neutral)
    if not hasattr(node, 'emotion') or node.emotion is None:
        node.emotion = np.array([0.0, 0.0])  # Neutral [arousal, valence]

    # Compute blending factor based on sub-entity weight
    alpha = coloring_rate * sub_entity_weight
    alpha = min(alpha, 1.0)  # Clamp to [0, 1]

    # Blend emotions
    node.emotion = (1 - alpha) * node.emotion + alpha * sub_entity_emotion


def apply_emotional_coloring_to_link(
    link: 'Link',
    sub_entity_emotion: np.ndarray,
    sub_entity_weight: float,
    coloring_rate: float = EMOTIONAL_COLORING_RATE
) -> None:
    """
    Color link's emotional vector with sub-entity's emotion.

    Same blending formula as node coloring.

    Args:
        link: Link to color
        sub_entity_emotion: Sub-entity's current emotion
        sub_entity_weight: Sub-entity's global weight/energy (0-1)
        coloring_rate: Base coloring rate
    """
    # Get current link emotion (or initialize to neutral)
    if not hasattr(link, 'emotion') or link.emotion is None:
        link.emotion = np.array([0.0, 0.0])  # Neutral [arousal, valence]

    # Compute blending factor
    alpha = coloring_rate * sub_entity_weight
    alpha = min(alpha, 1.0)

    # Blend emotions
    link.emotion = (1 - alpha) * link.emotion + alpha * sub_entity_emotion


# --- Traversal Execution ---

def execute_traversal(
    current_node: 'Node',
    candidate: TraversalCandidate,
    sub_entity_id: str,
    sub_entity_emotion: np.ndarray,
    sub_entity_weight: float,
    goal: SubEntityGoal
) -> Tuple['Node', float]:
    """
    Execute traversal to selected link.

    Steps:
    1. Deduct energy cost from budget
    2. Apply emotional coloring to link and target node
    3. Mark target node as visited
    4. Return target node and remaining energy

    Args:
        current_node: Current node
        candidate: Selected traversal candidate
        sub_entity_id: Sub-entity identifier
        sub_entity_emotion: Current emotional state
        sub_entity_weight: Global weight/energy of sub-entity
        goal: Current goal (modified in-place)

    Returns:
        Tuple of (next_node, remaining_energy)
    """
    # 1. Deduct energy
    goal.energy_budget -= candidate.cost

    # 2. Apply emotional coloring
    apply_emotional_coloring_to_link(
        candidate.link,
        sub_entity_emotion,
        sub_entity_weight
    )
    apply_emotional_coloring(
        candidate.target_node,
        sub_entity_emotion,
        sub_entity_weight
    )

    # 3. Mark visited
    goal.visited_nodes.add(candidate.target_node.id)

    # 4. Return next state
    return candidate.target_node, goal.energy_budget


# --- High-Level Traversal Loop ---

def traverse_until_exhausted(
    start_node: 'Node',
    sub_entity_id: str,
    sub_entity_emotion: np.ndarray,
    sub_entity_embedding: Optional[np.ndarray],
    sub_entity_weight: float,
    goal: SubEntityGoal,
    criticality: float,
    max_steps: int = 100
) -> List['Node']:
    """
    Execute traversal loop until energy exhausted or goal met.

    Returns path of traversed nodes.

    Args:
        start_node: Starting node
        sub_entity_id: Sub-entity identifier
        sub_entity_emotion: Current emotional state
        sub_entity_embedding: Current embedding
        sub_entity_weight: Global weight/energy
        goal: Goal driving traversal
        criticality: System criticality
        max_steps: Maximum traversal steps (safety limit)

    Returns:
        List of traversed nodes (including start_node)
    """
    path = [start_node]
    current_node = start_node

    for step in range(max_steps):
        # Select next traversal
        candidate = select_next_traversal(
            current_node,
            sub_entity_id,
            sub_entity_emotion,
            sub_entity_embedding,
            goal,
            criticality
        )

        # No affordable options
        if candidate is None:
            break

        # Execute traversal
        current_node, remaining_energy = execute_traversal(
            current_node,
            candidate,
            sub_entity_id,
            sub_entity_emotion,
            sub_entity_weight,
            goal
        )

        path.append(current_node)

        # Check if energy exhausted
        if remaining_energy <= 0:
            break

    return path
