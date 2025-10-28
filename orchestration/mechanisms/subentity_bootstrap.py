"""
Subentity Bootstrap - Create subentities from config and graph data.

Config-Driven Bootstrap (2025-10-24 Architecture Correction):
1. Load functional SubEntities from config/functional_subentities.yml (NOT Mechanism nodes)
2. Seed memberships via keyword matching against node name/description
3. Create semantic SubEntities via clustering on embeddings (when available)
4. Create MEMBER_OF and RELATES_TO links

Key insight: Functional SubEntities (The Translator, The Architect, etc.) are
cognitive modes/patterns, not algorithms. They bootstrap from configuration
with keyword-based membership seeding, not from Mechanism seed nodes.

Uses real citizen graphs from FalkorDB.

Author: Felix (Engineer)
Created: 2025-10-21
Updated: 2025-10-24 - Config-driven functional SubEntities (no Mechanism dependency)
Architecture: Phase 7.2 - Multi-Scale Consciousness Bootstrap
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict

from orchestration.core import Node, Subentity, Link, Graph, NodeType, LinkType
from orchestration.core.types import EntityID
import yaml
import math
from pathlib import Path

logger = logging.getLogger(__name__)


class SubEntityBootstrap:
    """
    Bootstrap subentity layer from existing citizen graphs.

    Two-phase approach:
    1. Functional subentities: Extract from Mechanism nodes (subentity ecology)
    2. Semantic subentities: Cluster nodes by embedding similarity
    """

    def __init__(self, graph: Graph):
        """
        Initialize bootstrap for a citizen graph.

        Args:
            graph: Citizen graph to bootstrap subentities from
        """
        self.graph = graph
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """
        Load functional SubEntities configuration from YAML.

        Returns:
            Dict with 'entities' list containing entity definitions
        """
        config_path = Path(__file__).parent.parent / "config" / "functional_subentities.yml"

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using empty config")
            return {"entities": []}

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded {len(config.get('entities', []))} functional SubEntities from config")
        return config


    def bootstrap_functional_subentities(self) -> List[Subentity]:
        """
        Create functional subentities from configuration (not Mechanism nodes).

        Loads entities from config/functional_subentities.yml, creates Entity nodes,
        seeds memberships via keyword matching against node name/description.

        Returns:
            List of functional Subentity objects created
        """
        logger.info(f"Bootstrapping functional subentities from config for graph {self.graph.id}")

        functional_subentities = []
        entities_config = self.config.get("entities", [])

        if not entities_config:
            logger.warning("No entities defined in config, skipping functional bootstrap")
            return functional_subentities

        for subentity_def in entities_config:
            key = subentity_def.get("key")
            if not key:
                logger.warning(f"Entity missing 'key' field, skipping: {subentity_def}")
                continue

            # Create or get existing entity (idempotent)
            subentity = self._upsert_functional_subentity(subentity_def)
            functional_subentities.append(subentity)

            # Seed memberships via keyword matching
            members_created = self._seed_memberships_from_keywords(subentity, subentity_def)

            logger.info(f"  Created functional subentity: {subentity.id} ({key}) with {members_created} members")

        logger.info(f"Created {len(functional_subentities)} functional subentities")

        return functional_subentities

    def _upsert_functional_subentity(self, subentity_def: dict) -> Subentity:
        """
        Create or retrieve functional SubEntity from config definition.

        Args:
            subentity_def: Entity definition from YAML config

        Returns:
            Subentity object (created or existing)
        """
        key = subentity_def["key"]
        subentity_id = f"entity_{self.graph.id}_{key}"

        # Check if entity already exists
        existing = self.graph.get_entity(subentity_id)
        if existing:
            logger.debug(f"  Entity {subentity_id} already exists, reusing")
            return existing

        # Create new entity
        subentity = Subentity(
            id=subentity_id,
            entity_kind=subentity_def.get("kind", "functional"),
            role_or_topic=key,
            description=subentity_def.get("description", ""),
            stability_state="mature",  # Config-driven entities start mature
            scope="personal",  # Functional SubEntities are personal (citizen-specific)
            created_from="config_bootstrap",
            created_by=f"bootstrap_{self.graph.id}",
            confidence=1.0,  # Config-defined = high confidence
            created_at=datetime.now(),
            valid_at=datetime.now()
        )

        # Add to graph
        self.graph.add_entity(subentity)

        return subentity

    def _seed_memberships_from_keywords(self, subentity: Subentity, subentity_def: dict) -> int:
        """
        Seed MEMBER_OF memberships via keyword matching.

        Scores each node by keyword hits in name+description, converts to weight
        via squash function, creates MEMBER_OF links.

        Args:
            subentity: Entity to seed memberships for
            subentity_def: Entity definition with 'keywords' dict

        Returns:
            Number of memberships created
        """
        keywords_config = subentity_def.get("keywords", {})
        keywords = keywords_config.get("any", [])

        if not keywords:
            logger.warning(f"No keywords defined for entity {subentity.id}")
            return 0

        # Content-bearing node types for membership
        # Using actual NodeType enum values (some types from schema don't exist in enum yet)
        content_types = [
            NodeType.CONCEPT,
            NodeType.REALIZATION,
            NodeType.PATTERN,  # Covers Personal_Pattern
            NodeType.PRINCIPLE,
            NodeType.ANTI_PATTERN,
            NodeType.MEMORY,
            NodeType.GOAL  # Covers Personal_Goal
        ]

        # Compute keyword scores for all nodes
        hits = []
        for node in self.graph.nodes.values():
            # Filter to content types
            try:
                if node.node_type not in content_types:
                    continue
            except:
                # If node_type is string or invalid, skip
                continue

            # Compute keyword score
            text = (node.name + " " + node.description).lower()
            score = self._keyword_score(text, keywords)

            if score > 0:
                hits.append((node, score))

        if not hits:
            logger.debug(f"  No keyword matches found for entity {subentity.id}")
            return 0

        # Convert scores to membership weights via squash function
        # Then create MEMBER_OF links
        memberships_created = 0
        for node, score in hits:
            weight = self._squash(score)

            # Only create meaningful memberships (threshold 0.1)
            if weight >= 0.1:
                link_id = f"belongs_{node.id}_{subentity.id}"

                link = Link(
                    id=link_id,
                    source_id=node.id,
                    target_id=subentity.id,
                    link_type=LinkType.MEMBER_OF,
                    subentity=self.graph.id,
                    weight=weight,
                    energy=0.0,
                    properties={
                        "provenance": "config_bootstrap_keyword",
                        "keyword_score": score,
                        "last_coactivation_ema": 0.0
                    }
                )

                self.graph.add_link(link)
                memberships_created += 1

        # Update member count
        subentity.member_count = memberships_created

        logger.debug(f"  Seeded {memberships_created} memberships for entity {subentity.id}")
        return memberships_created

    def _keyword_score(self, text: str, keywords: List[str]) -> float:
        """
        Compute simple keyword match score.

        Args:
            text: Node text (name + description)
            keywords: List of keywords to match

        Returns:
            Score = count of keyword hits
        """
        return float(sum(1 for kw in keywords if kw in text))

    def _squash(self, score: float) -> float:
        """
        Convert keyword score to membership weight via monotone squash.

        Uses: w = 1 - exp(-score)
        This gives: score=0 → w=0, score=1 → w=0.63, score=3 → w=0.95

        Args:
            score: Keyword hit count

        Returns:
            Membership weight in [0, 1]
        """
        return 1.0 - math.exp(-score)

    def bootstrap_semantic_subentities(
        self,
        n_clusters: int = 10,
        min_cluster_size: int = 3
    ) -> List[Subentity]:
        """
        Create semantic subentities via clustering.

        Groups nodes by embedding similarity, creating topic-based subentities.

        Args:
            n_clusters: Number of clusters to create
            min_cluster_size: Minimum nodes per cluster

        Returns:
            List of semantic Subentity objects created
        """
        logger.info(f"Bootstrapping semantic subentities from graph {self.graph.id}")

        # Get all nodes with embeddings
        nodes_with_embeddings = []
        embeddings = []

        for node in self.graph.nodes.values():
            if hasattr(node, 'embedding') and node.embedding is not None:
                nodes_with_embeddings.append(node)
                embeddings.append(node.embedding)

        if len(nodes_with_embeddings) < min_cluster_size:
            logger.warning(
                f"Not enough nodes with embeddings ({len(nodes_with_embeddings)}) "
                f"for semantic clustering"
            )
            return []

        logger.info(f"  Clustering {len(nodes_with_embeddings)} nodes")

        # Cluster nodes (using k-means for now)
        from sklearn.cluster import KMeans

        embeddings_array = np.array(embeddings)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings_array)

        # Create subentity per cluster
        semantic_subentities = []

        for cluster_id in range(n_clusters):
            cluster_nodes = [
                node for node, label in zip(nodes_with_embeddings, labels)
                if label == cluster_id
            ]

            if len(cluster_nodes) < min_cluster_size:
                logger.debug(f"  Skipping cluster {cluster_id} (only {len(cluster_nodes)} nodes)")
                continue

            # Generate topic label
            topic_label = self._generate_topic_label(cluster_nodes, cluster_id)

            # Create semantic subentity
            subentity = self._create_semantic_subentity(
                cluster_nodes,
                kmeans.cluster_centers_[cluster_id],
                topic_label,
                cluster_id
            )

            semantic_subentities.append(subentity)

            logger.info(f"  Created semantic subentity: {subentity.id} ({topic_label})")

        logger.info(f"Created {len(semantic_subentities)} semantic subentities")

        return semantic_subentities

    def _generate_topic_label(self, nodes: List[Node], cluster_id: int) -> str:
        """
        Generate topic label for cluster.

        Uses simple TF-IDF on node descriptions to extract top terms.

        Args:
            nodes: Nodes in cluster
            cluster_id: Cluster identifier

        Returns:
            Topic label (snake_case)
        """
        # Extract descriptions
        descriptions = [n.description for n in nodes if n.description]

        if not descriptions:
            return f"topic_{cluster_id}"

        # Simple keyword extraction (TF-IDF would be better but requires sklearn)
        # For now, just use most common words
        from collections import Counter
        import re

        # Tokenize
        words = []
        for desc in descriptions:
            # Extract words (alphanumeric only)
            tokens = re.findall(r'\b\w+\b', desc.lower())
            words.extend(tokens)

        # Count frequencies
        word_counts = Counter(words)

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
                      'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}

        filtered_counts = {
            w: c for w, c in word_counts.items()
            if w not in stop_words and len(w) > 3
        }

        # Get top 3 words
        top_words = [w for w, c in sorted(
            filtered_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]]

        if top_words:
            return "_".join(top_words)
        else:
            return f"topic_{cluster_id}"

    def _create_semantic_subentity(
        self,
        member_nodes: List[Node],
        centroid: np.ndarray,
        topic_label: str,
        cluster_id: int
    ) -> Subentity:
        """
        Create a semantic Subentity from clustered nodes.

        Args:
            member_nodes: Nodes in this cluster
            centroid: Cluster centroid embedding
            topic_label: Generated topic label
            cluster_id: Cluster identifier

        Returns:
            Semantic Subentity object
        """
        subentity_id = f"entity_{self.graph.id}_semantic_{topic_label}"

        subentity = Subentity(
            id=subentity_id,
            entity_kind="semantic",
            role_or_topic=topic_label,
            description=f"Semantic cluster: {topic_label} ({len(member_nodes)} nodes)",
            centroid_embedding=centroid,
            stability_state="provisional",  # Semantic subentities start provisional
            scope="organizational",  # Semantic topics are shared
            created_from="semantic_clustering",
            created_by=f"bootstrap_{self.graph.id}",
            confidence=0.7,  # Lower confidence for auto-generated
            member_count=len(member_nodes),
            created_at=datetime.now(),
            valid_at=datetime.now()
        )

        # Add subentity to graph
        self.graph.add_entity(subentity)

        # Create MEMBER_OF links
        for node in member_nodes:
            # Compute distance to centroid
            if hasattr(node, 'embedding') and node.embedding is not None:
                distance = 1 - self._cosine_similarity(node.embedding, centroid)
                weight = 1.0 - distance  # Closer = higher weight
            else:
                weight = 0.5  # Default weight for nodes without embeddings

            link_id = f"belongs_{node.id}_{subentity.id}"

            link = Link(
                id=link_id,
                source_id=node.id,
                target_id=subentity.id,
                link_type=LinkType.MEMBER_OF,
                subentity=self.graph.id,
                weight=max(0.1, weight),  # Ensure minimum weight
                energy=0.0,
                properties={
                    "provenance": "cluster",
                    "last_coactivation_ema": 0.0
                }
            )

            self.graph.add_link(link)

        return subentity

    def create_relates_to_links(self, semantic_distance_threshold: float = 0.5) -> int:
        """
        Create RELATES_TO links between subentities.

        Connects subentities that are semantically close (cosine similarity).

        Args:
            semantic_distance_threshold: Maximum distance for link creation

        Returns:
            Number of RELATES_TO links created
        """
        logger.info(f"Creating RELATES_TO links for graph {self.graph.id}")

        links_created = 0

        subentities = list(self.graph.subentities.values())

        for i, entity_a in enumerate(subentities):
            for entity_b in subentities[i+1:]:
                # Skip if no centroids
                if entity_a.centroid_embedding is None or entity_b.centroid_embedding is None:
                    continue

                # Compute semantic distance
                distance = 1 - self._cosine_similarity(
                    entity_a.centroid_embedding,
                    entity_b.centroid_embedding
                )

                # Create link if close enough
                if distance < semantic_distance_threshold:
                    # Create bidirectional links (E→F and F→E)
                    for source, target in [(entity_a, entity_b), (entity_b, entity_a)]:
                        link_id = f"relates_{source.id}_{target.id}"

                        link = Link(
                            id=link_id,
                            source_id=source.id,
                            target_id=target.id,
                            link_type=LinkType.RELATES_TO,
                            subentity=self.graph.id,
                            weight=1.0,
                            energy=0.0,
                            properties={
                                "ease_log_weight": 0.0,  # Neutral initial ease
                                "dominance": 0.5,  # Symmetric initial prior
                                "semantic_distance": distance,
                                "boundary_stride_count": 0,
                                "last_boundary_phi_ema": 0.0,
                                "typical_hunger": "unknown"
                            }
                        )

                        self.graph.add_link(link)
                        links_created += 1

        logger.info(f"Created {links_created} RELATES_TO links")

        return links_created

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity [0, 1]
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def run_complete_bootstrap(
        self,
        n_semantic_clusters: int = 10,
        min_cluster_size: int = 3,
        semantic_distance_threshold: float = 0.5
    ) -> Dict[str, int]:
        """
        Run complete bootstrap procedure.

        1. Create functional subentities from Mechanism nodes
        2. Create semantic subentities via clustering
        3. Create RELATES_TO links between subentities

        Args:
            n_semantic_clusters: Number of semantic clusters
            min_cluster_size: Minimum nodes per cluster
            semantic_distance_threshold: Max distance for RELATES_TO links

        Returns:
            Dict with bootstrap statistics
        """
        logger.info(f"Starting complete subentity bootstrap for graph {self.graph.id}")

        # Phase 1: Functional subentities
        functional_subentities = self.bootstrap_functional_subentities()

        # Phase 2: Semantic subentities
        semantic_subentities = self.bootstrap_semantic_subentities(
            n_clusters=n_semantic_clusters,
            min_cluster_size=min_cluster_size
        )

        # Phase 3: RELATES_TO links
        relates_to_count = self.create_relates_to_links(
            semantic_distance_threshold=semantic_distance_threshold
        )

        stats = {
            "functional_subentities": len(functional_subentities),
            "semantic_subentities": len(semantic_subentities),
            "total_entities": len(functional_subentities) + len(semantic_subentities),
            "relates_to_links": relates_to_count,
            "member_of_links": len([
                l for l in self.graph.links.values()
                if l.link_type == LinkType.MEMBER_OF
            ])
        }

        logger.info(f"Bootstrap complete for {self.graph.id}: {stats}")

        return stats


# --- Standalone Bootstrap Script ---

def bootstrap_citizen_graph(graph_id: str) -> Dict[str, int]:
    """
    Bootstrap subentities for a specific citizen graph.

    Args:
        graph_id: Graph identifier (e.g., "citizen_luca")

    Returns:
        Dict with bootstrap statistics
    """
    # TODO: Load graph from FalkorDB
    # For now, create empty graph for testing
    from orchestration.core import Graph

    graph = Graph(graph_id=graph_id, name=f"Graph {graph_id}")

    # Run bootstrap
    bootstrap = SubEntityBootstrap(graph)
    stats = bootstrap.run_complete_bootstrap()

    # TODO: Persist subentities to FalkorDB

    return stats


if __name__ == "__main__":
    # Bootstrap example citizen
    logging.basicConfig(level=logging.INFO)

    stats = bootstrap_citizen_graph("citizen_luca")

    print("\n" + "="*70)
    print("SUBENTITY BOOTSTRAP COMPLETE")
    print("="*70)
    print(f"Functional subentities: {stats['functional_subentities']}")
    print(f"Semantic subentities: {stats['semantic_subentities']}")
    print(f"Total subentities: {stats['total_entities']}")
    print(f"MEMBER_OF links: {stats['member_of_links']}")
    print(f"RELATES_TO links: {stats['relates_to_links']}")
    print("="*70)
