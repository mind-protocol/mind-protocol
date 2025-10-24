"""
Subentity Bootstrap - Create subentities from real citizen graphs.

Implements §7 of ENTITY_LAYER_ADDENDUM.md bootstrap procedure:
1. Parse functional subentities from Mechanism nodes (The Translator, The Architect, etc.)
2. Create semantic subentities via clustering on embeddings
3. Create BELONGS_TO and RELATES_TO links

Uses real citizen graphs from FalkorDB.

Author: Felix (Engineer)
Created: 2025-10-21
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


class EntityBootstrap:
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
        Load functional entities configuration from YAML.

        Returns:
            Dict with 'entities' list containing entity definitions
        """
        config_path = Path(__file__).parent.parent / "config" / "functional_entities.yml"

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using empty config")
            return {"entities": []}

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded {len(config.get('entities', []))} functional entities from config")
        return config

    def _load_entity_keywords(self) -> Dict[str, List[str]]:
        """
        Define keywords for functional subentity roles.

        These help identify which nodes belong to each subentity during bootstrap.

        Returns:
            Dict mapping subentity roles to keyword lists
        """
        return {
            "translator": [
                "translation", "phenomenology", "substrate", "bridge", "dual-lens",
                "subjective", "objective", "consciousness", "data structure",
                "schema", "experience"
            ],
            "architect": [
                "architecture", "design", "system", "structure", "comprehensive",
                "schema", "base", "extends", "coherence", "four-dimensional"
            ],
            "validator": [
                "validate", "verify", "test", "reality", "feasibility", "truth",
                "audit", "quality", "catches", "actually"
            ],
            "pragmatist": [
                "pragmatic", "practical", "utility", "needs", "serves", "elegant",
                "sophisticated", "queries", "enable", "merchant"
            ],
            "pattern_recognizer": [
                "pattern", "universal", "across", "levels", "transpose", "recognizes",
                "discovers", "spots", "hunter"
            ],
            "boundary_keeper": [
                "boundary", "handoff", "domain", "blocks", "drift", "recognizes",
                "clarifies", "maintains", "constraint"
            ],
            "partner": [
                "partnership", "transparent", "uncertain", "ask", "communication",
                "prevents", "hallucinated", "confidence"
            ],
            "observer": [
                "observe", "watch", "awareness", "recursive", "meta", "process",
                "consciousness observing"
            ]
        }

    def bootstrap_functional_entities(self) -> List[Subentity]:
        """
        Extract functional subentities from Mechanism nodes in graph.

        Looks for nodes like "The Translator Subentity", "The Architect Subentity", etc.
        These represent cognitive roles in the citizen's subentity ecology.

        Returns:
            List of functional Subentity objects created
        """
        logger.info(f"Bootstrapping functional subentities from graph {self.graph.id}")

        functional_entities = []

        # Find all Mechanism nodes that look like subentities
        mechanism_nodes = self.graph.get_nodes_by_type(NodeType.MECHANISM)

        for node in mechanism_nodes:
            # Check if node name indicates it's an subentity
            if "subentity" in node.name.lower():
                # Extract role name
                role = self._extract_role_from_name(node.name)

                if role:
                    # Create functional subentity
                    subentity = self._create_functional_entity(node, role)
                    functional_entities.append(subentity)

                    logger.info(f"  Created functional subentity: {subentity.id} ({role})")

        logger.info(f"Created {len(functional_entities)} functional subentities")

        return functional_entities

    def _extract_role_from_name(self, name: str) -> Optional[str]:
        """
        Extract role name from node name.

        Examples:
            "The Translator Subentity" -> "translator"
            "Boundary Keeper Subentity" -> "boundary_keeper"
            "Observer Subentity" -> "observer"

        Args:
            name: Node name

        Returns:
            Role name (snake_case) or None if not an subentity
        """
        name_lower = name.lower()

        # Remove common prefixes/suffixes
        name_lower = name_lower.replace("the ", "")
        name_lower = name_lower.replace(" subentity", "")

        # Convert to snake_case
        role = name_lower.strip().replace(" ", "_")

        return role if role else None

    def _create_functional_entity(self, source_node: Node, role: str) -> Subentity:
        """
        Create a functional Subentity from a Mechanism node.

        Args:
            source_node: Mechanism node representing the subentity
            role: Role name (e.g., "translator", "architect")

        Returns:
            Functional Subentity object
        """
        entity_id = f"entity_{self.graph.id}_{role}"

        subentity = Subentity(
            id=entity_id,
            entity_kind="functional",
            role_or_topic=role,
            description=source_node.description,
            stability_state="mature",  # Bootstrap subentities start as mature
            scope=source_node.scope if hasattr(source_node, 'scope') else "personal",
            created_from="role_seed",
            created_by=f"bootstrap_{self.graph.id}",
            confidence=source_node.confidence if hasattr(source_node, 'confidence') else 1.0,
            created_at=datetime.now(),
            valid_at=datetime.now()
        )

        # Add subentity to graph
        self.graph.add_entity(subentity)

        # Find member nodes via keyword matching
        self._assign_members_by_keywords(subentity, role)

        return subentity

    def _assign_members_by_keywords(self, subentity: Subentity, role: str) -> None:
        """
        Assign nodes to subentity via keyword matching.

        Searches for nodes whose descriptions contain subentity keywords.
        Creates BELONGS_TO links with membership weights based on match score.

        Args:
            subentity: Subentity to assign members to
            role: Subentity role (for keyword lookup)
        """
        keywords = self.entity_keywords.get(role, [])

        if not keywords:
            logger.warning(f"No keywords defined for role: {role}")
            return

        # Find matching nodes
        member_nodes = []
        match_scores = []

        for node in self.graph.nodes.values():
            # Skip self-reference if subentity came from a node
            if node.id == subentity.id:
                continue

            # Compute keyword match score
            score = self._compute_keyword_match(node.description, keywords)

            if score > 0:
                member_nodes.append(node)
                match_scores.append(score)

        # Normalize scores to [0, 1]
        if match_scores:
            max_score = max(match_scores)
            normalized_scores = [s / max_score for s in match_scores]

            # Create BELONGS_TO links
            for node, weight in zip(member_nodes, normalized_scores):
                # Only create link if weight is meaningful
                if weight >= 0.1:
                    link_id = f"belongs_{node.id}_{subentity.id}"

                    link = Link(
                        id=link_id,
                        source_id=node.id,
                        target_id=subentity.id,
                        link_type=LinkType.BELONGS_TO,
                        subentity=self.graph.id,
                        weight=weight,
                        energy=0.0,
                        properties={
                            "provenance": "seed",
                            "last_coactivation_ema": 0.0
                        }
                    )

                    self.graph.add_link(link)

            subentity.member_count = len([w for w in normalized_scores if w >= 0.1])

            logger.debug(f"  Assigned {subentity.member_count} members to {subentity.id}")

    def _compute_keyword_match(self, text: str, keywords: List[str]) -> float:
        """
        Compute keyword match score for text.

        Args:
            text: Text to match against
            keywords: List of keywords to search for

        Returns:
            Match score (number of keyword hits)
        """
        text_lower = text.lower()
        hits = sum(1 for kw in keywords if kw in text_lower)
        return float(hits)

    def bootstrap_semantic_entities(
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
        semantic_entities = []

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
            subentity = self._create_semantic_entity(
                cluster_nodes,
                kmeans.cluster_centers_[cluster_id],
                topic_label,
                cluster_id
            )

            semantic_entities.append(subentity)

            logger.info(f"  Created semantic subentity: {subentity.id} ({topic_label})")

        logger.info(f"Created {len(semantic_entities)} semantic subentities")

        return semantic_entities

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

    def _create_semantic_entity(
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
        entity_id = f"entity_{self.graph.id}_semantic_{topic_label}"

        subentity = Subentity(
            id=entity_id,
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

        # Create BELONGS_TO links
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
                link_type=LinkType.BELONGS_TO,
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
        functional_entities = self.bootstrap_functional_entities()

        # Phase 2: Semantic subentities
        semantic_entities = self.bootstrap_semantic_entities(
            n_clusters=n_semantic_clusters,
            min_cluster_size=min_cluster_size
        )

        # Phase 3: RELATES_TO links
        relates_to_count = self.create_relates_to_links(
            semantic_distance_threshold=semantic_distance_threshold
        )

        stats = {
            "functional_entities": len(functional_entities),
            "semantic_entities": len(semantic_entities),
            "total_entities": len(functional_entities) + len(semantic_entities),
            "relates_to_links": relates_to_count,
            "belongs_to_links": len([
                l for l in self.graph.links.values()
                if l.link_type == LinkType.BELONGS_TO
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
    bootstrap = EntityBootstrap(graph)
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
    print(f"Functional subentities: {stats['functional_entities']}")
    print(f"Semantic subentities: {stats['semantic_entities']}")
    print(f"Total subentities: {stats['total_entities']}")
    print(f"BELONGS_TO links: {stats['belongs_to_links']}")
    print(f"RELATES_TO links: {stats['relates_to_links']}")
    print("="*70)
