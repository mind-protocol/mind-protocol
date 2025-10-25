"""
Entity Post-Bootstrap Initialization

Runs after EntityBootstrap to prepare entities for runtime:
1. Normalize memberships per node (Σ weights ≤ 1)
2. Compute entity centroids from member embeddings
3. Compute entity colors from centroids (OKLCH)
4. Initialize entity thresholds from current energies
5. Warm entity cache for first wm.emit

This ensures non-empty entity selection on frame #1.

Author: Claude Code "Syntax"
Created: 2025-10-24
Architecture: Phase 7.2 - Entity Layer Activation
"""

import logging
import numpy as np
from typing import Dict, List
from datetime import datetime

from orchestration.core import Graph, Subentity, Node, LinkType

logger = logging.getLogger(__name__)


def run_post_bootstrap_initialization(graph: Graph) -> Dict[str, any]:
    """
    Run all post-bootstrap initialization steps.

    Args:
        graph: Graph with bootstrapped entities

    Returns:
        Dict with initialization statistics
    """
    logger.info(f"[PostBootstrap] Starting initialization for {graph.id}...")

    stats = {
        "nodes_normalized": 0,
        "entities_with_centroids": 0,
        "entities_with_colors": 0,
        "entities_with_thresholds": 0,
        "cache_warmed": False
    }

    # Step 1: Normalize memberships per node
    stats["nodes_normalized"] = normalize_node_memberships(graph)

    # Step 2: Compute entity centroids
    stats["entities_with_centroids"] = compute_entity_centroids(graph)

    # Step 3: Compute entity colors from centroids
    stats["entities_with_colors"] = compute_entity_colors(graph)

    # Step 4: Initialize entity thresholds
    stats["entities_with_thresholds"] = initialize_entity_thresholds(graph)

    # Step 5: Warm entity cache
    stats["cache_warmed"] = warm_entity_cache(graph)

    logger.info(f"[PostBootstrap] Complete: {stats}")

    return stats


def normalize_node_memberships(graph: Graph) -> int:
    """
    Normalize BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") weights per node so Σ weights ≤ 1.

    Args:
        graph: Graph to normalize

    Returns:
        Number of nodes normalized
    """
    normalized_count = 0

    for node in graph.nodes.values():
        # Get all BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links from this node
        belongs_to_links = [
            link for link in node.outgoing_links
            if link.link_type == LinkType.MEMBER_OF
        ]

        if not belongs_to_links:
            continue

        # Sum current weights
        total_weight = sum(link.weight for link in belongs_to_links)

        if total_weight > 1.0:
            # Normalize to sum = 1.0
            for link in belongs_to_links:
                link.weight = link.weight / total_weight
            normalized_count += 1

    logger.debug(f"  Normalized memberships for {normalized_count} nodes")
    return normalized_count


def compute_entity_centroids(graph: Graph) -> int:
    """
    Compute centroid embeddings for entities from member nodes.

    centroid(E) = (Σ m[n,E] * embed(n)) / Σ m[n,E]

    Args:
        graph: Graph with entities

    Returns:
        Number of entities with computed centroids
    """
    computed_count = 0

    for entity in graph.subentities.values():
        # Get member nodes via BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") links
        member_data = []

        for link in entity.incoming_links:
            if link.link_type != LinkType.MEMBER_OF:
                continue

            node = link.source
            if not isinstance(node, Node):
                continue

            # Check if node has embedding
            if hasattr(node, 'embedding') and node.embedding is not None:
                weight = link.weight
                embedding = node.embedding
                member_data.append((weight, embedding))

        if not member_data:
            logger.debug(f"  Entity {entity.id} has no members with embeddings")
            continue

        # Compute weighted centroid
        weights = np.array([w for w, _ in member_data])
        embeddings = np.array([e for _, e in member_data])

        total_weight = weights.sum()
        if total_weight == 0:
            continue

        centroid = (weights[:, np.newaxis] * embeddings).sum(axis=0) / total_weight

        entity.centroid_embedding = centroid
        computed_count += 1

    logger.debug(f"  Computed centroids for {computed_count} entities")
    return computed_count


def compute_entity_colors(graph: Graph) -> int:
    """
    Compute entity colors from centroid embeddings using OKLCH.

    For now, use simple hashing until OKLCH implementation available.

    Args:
        graph: Graph with entity centroids

    Returns:
        Number of entities with computed colors
    """
    colored_count = 0

    for entity in graph.subentities.values():
        if entity.centroid_embedding is None:
            continue

        # Simple hash-based color generation from centroid
        # TODO: Replace with proper OKLCH conversion
        centroid_hash = hash(tuple(entity.centroid_embedding[:3]))
        hue = (centroid_hash % 360)

        # Store as HSL for now (compatible with current viz)
        entity.color = f"hsl({hue}, 70%, 60%)"
        colored_count += 1

    logger.debug(f"  Computed colors for {colored_count} entities")
    return colored_count


def initialize_entity_thresholds(graph: Graph) -> int:
    """
    Initialize entity thresholds from current entity energies.

    Uses bootstrap baseline: θ = E * 0.3 (will be refined by dynamic thresholds)

    Args:
        graph: Graph with entities

    Returns:
        Number of entities with initialized thresholds
    """
    initialized_count = 0

    for entity in graph.subentities.values():
        # Compute initial entity energy from member nodes
        entity_energy = 0.0

        for link in entity.incoming_links:
            if link.link_type != LinkType.MEMBER_OF:
                continue

            node = link.source
            if not isinstance(node, Node):
                continue

            # Weighted node energy contribution (surplus-only with log damping)
            weight = link.weight
            node_surplus = max(0.0, node.E - node.theta)  # Surplus energy only
            entity_energy += weight * np.log1p(node_surplus)  # Log damping prevents single-node domination

        # Set initial runtime values
        entity.energy_runtime = entity_energy
        entity.threshold_runtime = max(0.1, entity_energy * 0.3)  # Bootstrap baseline
        entity.activation_level_runtime = "active" if entity_energy >= entity.threshold_runtime else "dormant"

        initialized_count += 1

    logger.debug(f"  Initialized thresholds for {initialized_count} entities")
    return initialized_count


def warm_entity_cache(graph: Graph) -> bool:
    """
    Warm entity cache for first wm.emit.

    For now, just verify we have active entities ready.
    Future: Pre-compute entity scores for WM selection.

    Args:
        graph: Graph with initialized entities

    Returns:
        True if cache warmed successfully
    """
    active_entities = [
        e for e in graph.subentities.values()
        if e.energy_runtime >= e.threshold_runtime
    ]

    logger.debug(f"  Entity cache warmed: {len(active_entities)} active entities ready")

    return len(active_entities) > 0
