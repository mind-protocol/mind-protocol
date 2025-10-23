"""
Subentity Relationship Classification - Embedding-based collaborator/rival detection

Implements v2 spec for relationship classification:
- Embedding generation from member nodes
- Cosine similarity-based classification (collaborator vs rival)
- Energy modulation by relationship + link polarity
- Link polarity mapping (positive/negative/neutral)

Designer: Felix - 2025-10-23
Reference: docs/specs/v2/subentity_layer/relationship_classification.md
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RelationshipConfig:
    """Configuration for relationship classification."""
    collaborator_threshold: float = 0.7  # Similarity above = collaborators
    positive_link_boost: float = 0.5  # Max boost for collaborators on positive links
    positive_link_reduce: float = 0.3  # Max reduction for rivals on positive links
    negative_link_boost: float = 0.3  # Max boost for rivals on negative links
    negative_link_reduce: float = 0.4  # Max reduction for collaborators on negative links


# Link type polarity mapping
LINK_TYPE_POLARITY: Dict[str, str] = {
    # Positive (collaborative)
    "ENABLES": "positive",
    "RELATES_TO": "positive",
    "SUPPORTS": "positive",
    "COLLABORATES_WITH": "positive",
    "IMPLEMENTS": "positive",
    "EXTENDS": "positive",
    "CONTRIBUTES_TO": "positive",
    "DOCUMENTS": "positive",
    "DOCUMENTED_BY": "positive",
    "JUSTIFIES": "positive",
    "LEARNED_FROM": "positive",
    "DEEPENED_WITH": "positive",
    "ACTIVATES": "positive",
    "DRIVES_TOWARD": "positive",

    # Negative (competitive)
    "BLOCKS": "negative",
    "CONFLICTS_WITH": "negative",
    "CONTRADICTS": "negative",
    "SUPPRESSES": "negative",
    "THREATENS": "negative",
    "REFUTES": "negative",
    "TRIGGERED_BY": "negative",  # Reactive, can be competitive

    # Neutral (no modulation)
    "TEMPORAL_SEQUENCE": "neutral",
    "REFERENCES": "neutral",
    "REQUIRES": "neutral",
    "MEASURES": "neutral",
    "SUPERSEDES": "neutral",
    "ASSIGNED_TO": "neutral",
    "CREATES": "neutral",
}


def get_link_polarity(link_type: str) -> str:
    """
    Get polarity of link type.

    Args:
        link_type: Link type name

    Returns:
        "positive", "negative", or "neutral"
    """
    return LINK_TYPE_POLARITY.get(link_type, "neutral")


def generate_subentity_embedding(
    member_nodes: List,
    embedding_getter=None
) -> np.ndarray:
    """
    Generate subentity embedding from member node embeddings.

    Uses simple averaging strategy (can be enhanced with activity weighting).

    Args:
        member_nodes: List of Node objects belonging to subentity
        embedding_getter: Optional function to get embedding from node
                         (defaults to node.properties.get('embedding'))

    Returns:
        Normalized embedding vector (unit length)
    """
    if not member_nodes:
        # Empty subentity - return zero vector
        logger.warning("[RelationshipClassification] Empty member list, returning zero embedding")
        return np.zeros(768)  # Default dimension

    # Collect node embeddings
    node_embeddings = []

    for node in member_nodes:
        if embedding_getter:
            emb = embedding_getter(node)
        else:
            # Default: try to get from node properties
            emb = node.properties.get('embedding')

        if emb is not None:
            node_embeddings.append(emb)

    if not node_embeddings:
        # No embeddings available
        logger.warning(
            f"[RelationshipClassification] No embeddings found for {len(member_nodes)} members"
        )
        return np.zeros(768)

    # Average embeddings
    centroid = np.mean(node_embeddings, axis=0)

    # Normalize to unit length
    norm = np.linalg.norm(centroid)
    if norm > 1e-8:
        centroid = centroid / norm

    logger.debug(
        f"[RelationshipClassification] Generated embedding from {len(node_embeddings)} nodes"
    )

    return centroid


def generate_activity_weighted_embedding(
    member_nodes: List,
    embedding_getter=None,
    energy_getter=None
) -> np.ndarray:
    """
    Generate subentity embedding weighted by node activation.

    Nodes with higher energy contribute more to the embedding.

    Args:
        member_nodes: List of Node objects
        embedding_getter: Function to get embedding from node
        energy_getter: Function to get energy from node

    Returns:
        Normalized embedding vector
    """
    if not member_nodes:
        return np.zeros(768)

    weighted_embeddings = []
    total_energy = 0.0

    for node in member_nodes:
        # Get embedding
        if embedding_getter:
            emb = embedding_getter(node)
        else:
            emb = node.properties.get('embedding')

        if emb is None:
            continue

        # Get energy
        if energy_getter:
            energy = energy_getter(node)
        else:
            energy = getattr(node, 'energy_runtime', 0.0)

        weighted_embeddings.append(emb * energy)
        total_energy += energy

    if not weighted_embeddings or total_energy < 1e-8:
        # Fall back to simple averaging
        return generate_subentity_embedding(member_nodes, embedding_getter)

    # Sum weighted embeddings
    centroid = np.sum(weighted_embeddings, axis=0) / total_energy

    # Normalize
    norm = np.linalg.norm(centroid)
    if norm > 1e-8:
        centroid = centroid / norm

    logger.debug(
        f"[RelationshipClassification] Generated activity-weighted embedding "
        f"(total_energy={total_energy:.2f})"
    )

    return centroid


def classify_relationship(
    entity_a_embedding: np.ndarray,
    entity_b_embedding: np.ndarray,
    config: Optional[RelationshipConfig] = None
) -> str:
    """
    Classify relationship between two subentities.

    Uses cosine similarity of embeddings:
    - High similarity (> threshold) → "collaborator"
    - Low similarity (≤ threshold) → "rival"

    Args:
        entity_a_embedding: Embedding vector for entity A
        entity_b_embedding: Embedding vector for entity B
        config: Configuration (defaults to RelationshipConfig())

    Returns:
        "collaborator" or "rival"
    """
    if config is None:
        config = RelationshipConfig()

    # Cosine similarity (embeddings should already be normalized)
    similarity = float(np.dot(entity_a_embedding, entity_b_embedding))

    if similarity > config.collaborator_threshold:
        return "collaborator"
    else:
        return "rival"


def get_relationship_strength(
    entity_a_embedding: np.ndarray,
    entity_b_embedding: np.ndarray
) -> float:
    """
    Compute relationship strength from embedding similarity.

    Args:
        entity_a_embedding: Embedding vector for entity A
        entity_b_embedding: Embedding vector for entity B

    Returns:
        Strength in [0, 1] where:
        - 1.0: Perfect alignment (identical)
        - 0.5: Neutral (orthogonal)
        - 0.0: Opposite (maximally different)
    """
    # Cosine similarity in [-1, 1]
    similarity = float(np.dot(entity_a_embedding, entity_b_embedding))

    # Map to [0, 1]
    strength = (similarity + 1.0) / 2.0

    return strength


def modulate_energy_flow_positive_link(
    entity_a_embedding: np.ndarray,
    entity_b_embedding: np.ndarray,
    config: Optional[RelationshipConfig] = None
) -> float:
    """
    Compute energy multiplier for positive links.

    Positive links (ENABLES, RELATES_TO, etc.):
    - Collaborators: boost energy flow
    - Rivals: reduce energy flow

    Args:
        entity_a_embedding: Source subentity embedding
        entity_b_embedding: Target subentity embedding
        config: Configuration

    Returns:
        Energy multiplier (typically [0.7, 1.5])
    """
    if config is None:
        config = RelationshipConfig()

    relationship = classify_relationship(entity_a_embedding, entity_b_embedding, config)
    strength = get_relationship_strength(entity_a_embedding, entity_b_embedding)

    if relationship == "collaborator":
        # Boost energy flow to collaborators
        # Max: 1 + (0.5 * 1.0) = 1.5x for perfect collaborators
        multiplier = 1.0 + (config.positive_link_boost * strength)
    else:
        # Reduce energy flow to rivals
        # Min: 1 - (0.3 * (1 - 0)) = 0.7x for maximum rivals
        multiplier = 1.0 - (config.positive_link_reduce * (1.0 - strength))

    logger.debug(
        f"[RelationshipClassification] Positive link: {relationship}, "
        f"strength={strength:.2f}, multiplier={multiplier:.2f}"
    )

    return multiplier


def modulate_energy_flow_negative_link(
    entity_a_embedding: np.ndarray,
    entity_b_embedding: np.ndarray,
    config: Optional[RelationshipConfig] = None
) -> float:
    """
    Compute energy multiplier for negative links.

    Negative links (BLOCKS, SUPPRESSES, etc.):
    - Collaborators: reduce energy flow (blocking ally = bad)
    - Rivals: boost energy flow (blocking rival = good)

    Args:
        entity_a_embedding: Source subentity embedding
        entity_b_embedding: Target subentity embedding
        config: Configuration

    Returns:
        Energy multiplier (typically [0.6, 1.3])
    """
    if config is None:
        config = RelationshipConfig()

    relationship = classify_relationship(entity_a_embedding, entity_b_embedding, config)
    strength = get_relationship_strength(entity_a_embedding, entity_b_embedding)

    if relationship == "collaborator":
        # Reduce energy flow (blocking collaborator is bad)
        # Min: 1 - (0.4 * 1.0) = 0.6x for perfect collaborators
        multiplier = 1.0 - (config.negative_link_reduce * strength)
    else:
        # Boost energy flow (blocking rival is good)
        # Max: 1 + (0.3 * (1 - 0)) = 1.3x for maximum rivals
        multiplier = 1.0 + (config.negative_link_boost * (1.0 - strength))

    logger.debug(
        f"[RelationshipClassification] Negative link: {relationship}, "
        f"strength={strength:.2f}, multiplier={multiplier:.2f}"
    )

    return multiplier


def compute_energy_multiplier(
    link_type: str,
    entity_a_embedding: np.ndarray,
    entity_b_embedding: np.ndarray,
    config: Optional[RelationshipConfig] = None
) -> float:
    """
    Compute energy flow multiplier based on link type and relationship.

    This is the main integration point for energy diffusion.

    Args:
        link_type: Type of link between subentities
        entity_a_embedding: Source subentity embedding
        entity_b_embedding: Target subentity embedding
        config: Configuration

    Returns:
        Energy multiplier to apply to base transfer
    """
    polarity = get_link_polarity(link_type)

    if polarity == "positive":
        return modulate_energy_flow_positive_link(
            entity_a_embedding,
            entity_b_embedding,
            config
        )
    elif polarity == "negative":
        return modulate_energy_flow_negative_link(
            entity_a_embedding,
            entity_b_embedding,
            config
        )
    else:
        # Neutral - no modulation
        return 1.0


class RelationshipClassifier:
    """
    Stateful relationship classifier with caching.

    Caches:
    - Subentity embeddings (regenerate periodically)
    - Relationship classifications per pair
    """

    def __init__(self, config: Optional[RelationshipConfig] = None):
        """Initialize classifier with configuration."""
        self.config = config or RelationshipConfig()

        # Embedding cache: subentity_id -> embedding
        self.embedding_cache: Dict[str, np.ndarray] = {}

        # Relationship cache: (entity_a_id, entity_b_id) -> classification
        self.relationship_cache: Dict[Tuple[str, str], str] = {}

        logger.info(
            f"[RelationshipClassifier] Initialized "
            f"(threshold={self.config.collaborator_threshold})"
        )

    def update_subentity_embedding(
        self,
        subentity_id: str,
        embedding: np.ndarray
    ):
        """
        Update cached embedding for a subentity.

        Args:
            subentity_id: Subentity identifier
            embedding: New embedding vector
        """
        self.embedding_cache[subentity_id] = embedding

        # Invalidate relationship cache entries involving this subentity
        keys_to_remove = [
            key for key in self.relationship_cache.keys()
            if key[0] == subentity_id or key[1] == subentity_id
        ]
        for key in keys_to_remove:
            del self.relationship_cache[key]

        logger.debug(
            f"[RelationshipClassifier] Updated embedding for {subentity_id}, "
            f"invalidated {len(keys_to_remove)} relationship cache entries"
        )

    def get_or_compute_relationship(
        self,
        entity_a_id: str,
        entity_b_id: str
    ) -> str:
        """
        Get cached relationship or compute from embeddings.

        Args:
            entity_a_id: First subentity ID
            entity_b_id: Second subentity ID

        Returns:
            "collaborator" or "rival"
        """
        # Check cache
        cache_key = (entity_a_id, entity_b_id)
        if cache_key in self.relationship_cache:
            return self.relationship_cache[cache_key]

        # Compute from embeddings
        emb_a = self.embedding_cache.get(entity_a_id)
        emb_b = self.embedding_cache.get(entity_b_id)

        if emb_a is None or emb_b is None:
            logger.warning(
                f"[RelationshipClassifier] Missing embeddings for "
                f"{entity_a_id}/{entity_b_id}, defaulting to 'rival'"
            )
            return "rival"

        relationship = classify_relationship(emb_a, emb_b, self.config)

        # Cache result
        self.relationship_cache[cache_key] = relationship

        return relationship

    def compute_multiplier(
        self,
        link_type: str,
        entity_a_id: str,
        entity_b_id: str
    ) -> float:
        """
        Compute energy multiplier for link between subentities.

        Args:
            link_type: Type of link
            entity_a_id: Source subentity ID
            entity_b_id: Target subentity ID

        Returns:
            Energy multiplier
        """
        emb_a = self.embedding_cache.get(entity_a_id)
        emb_b = self.embedding_cache.get(entity_b_id)

        if emb_a is None or emb_b is None:
            # No embeddings - neutral modulation
            return 1.0

        return compute_energy_multiplier(link_type, emb_a, emb_b, self.config)

    def get_stats(self) -> dict:
        """Get classifier statistics."""
        return {
            "embeddings_cached": len(self.embedding_cache),
            "relationships_cached": len(self.relationship_cache),
            "config": {
                "collaborator_threshold": self.config.collaborator_threshold,
                "positive_link_boost": self.config.positive_link_boost,
                "positive_link_reduce": self.config.positive_link_reduce,
                "negative_link_boost": self.config.negative_link_boost,
                "negative_link_reduce": self.config.negative_link_reduce
            }
        }
