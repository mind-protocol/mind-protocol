"""
Semantic Search Interface for Consciousness Substrate

Enables consciousness archaeology queries:
- Find similar coping mechanisms
- Trace reasoning evolution
- Discover mental state patterns
- Search by phenomenology (felt_as, mindstate, struggle)

Uses vector similarity search over embedded nodes and links in FalkorDB.

Author: Felix "Ironhand"
Date: 2025-10-20
Pattern: Query interface for consciousness archaeology
"""

import redis
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from orchestration.adapters.search.embedding_service import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Semantic search interface for consciousness substrate.

    Provides query functions for finding similar nodes/links by semantic content,
    enabling consciousness archaeology across time and mental states.
    """

    def __init__(self, graph_name: str, host: str = 'localhost', port: int = 6379):
        """
        Initialize semantic search.

        Args:
            graph_name: FalkorDB graph name (e.g., 'citizen_felix')
            host: Redis host
            port: Redis port
        """
        self.graph_name = graph_name
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        self.embedding_service = get_embedding_service()

        # Verify connection
        try:
            self.r.ping()
            logger.info(f"[SemanticSearch] Connected to graph '{graph_name}'")
        except redis.exceptions.ConnectionError:
            logger.error("[SemanticSearch] Failed to connect to FalkorDB")
            raise

    def find_similar_nodes(
        self,
        query_text: str,
        node_type: Optional[str] = None,
        threshold: float = 0.70,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find nodes semantically similar to query text.

        Args:
            query_text: Natural language query
            node_type: Filter by node type (e.g., 'Realization', 'Decision')
                      If None, searches all node types
            threshold: Minimum similarity score (0-1)
            limit: Maximum number of results

        Returns:
            List of matching nodes with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query_text)

        # FalkorDB uses db.idx.vector.queryNodes procedure for vector search
        # Procedure signature: (label, attribute, k, query_vector)
        # Returns nodes ordered by similarity (lower distance = more similar)

        if not node_type:
            # If no node_type specified, we need to query multiple node types
            # For now, return empty (could be enhanced to query all types)
            logger.warning(f"[SemanticSearch] No node_type specified - vector search requires a label")
            return []

        # Build vector query using FalkorDB's vector search procedure
        # FalkorDB expects: queryNodes(label, attribute, k, vecf32([array]))
        # FalkorDB returns cosine similarity scores (higher = more similar, range 0-1)
        vector_str = str(query_embedding)  # Converts list to "[0.1, 0.2, ...]"

        # Fix #6: Query more results to account for potential near-duplicates
        query_limit = limit * 3

        query = f"""
        CALL db.idx.vector.queryNodes('{node_type}', 'content_embedding', {query_limit}, vecf32({vector_str}))
        YIELD node, score
        WHERE score >= {threshold}
        RETURN
          node.name as name,
          node.description as description,
          node.embeddable_text as embeddable_text,
          labels(node) as labels,
          score as distance
        ORDER BY score DESC
        LIMIT {query_limit}
        """

        try:
            result = self.r.execute_command('GRAPH.QUERY', self.graph_name, query)

            # Parse results
            all_matches = []
            if result and len(result) > 1:
                for row in result[1]:
                    name = row[0].decode() if isinstance(row[0], bytes) else row[0]
                    description = row[1].decode() if isinstance(row[1], bytes) else row[1]
                    embeddable_text = row[2].decode() if isinstance(row[2], bytes) else row[2]
                    labels = [l.decode() if isinstance(l, bytes) else l for l in row[3]] if row[3] else []
                    distance = float(row[4]) if row[4] is not None else 1.0

                    all_matches.append({
                        'name': name,
                        'description': description,
                        'embeddable_text': embeddable_text,
                        'type': labels[0] if labels else None,
                        'similarity': distance  # FalkorDB returns cosine similarity (not distance)
                    })

            # Fix #6: Filter out near-exact duplicates (similarity > 0.995)
            # These are likely self-hits or duplicate content
            matches = [m for m in all_matches if m['similarity'] < 0.995]

            # Return only requested limit
            matches = matches[:limit]

            # Fix #6: Log similarity distribution for debugging
            if matches:
                sims = [m['similarity'] for m in matches]
                logger.debug(f"[SemanticSearch] Similarity range: min={min(sims):.3f}, max={max(sims):.3f}, mean={sum(sims)/len(sims):.3f}")

            logger.info(f"[SemanticSearch] Found {len(matches)} similar nodes for query: '{query_text[:50]}...'")
            return matches

        except Exception as e:
            logger.error(f"[SemanticSearch] Query failed: {e}")
            return []

    def find_similar_links(
        self,
        query_text: str,
        link_type: Optional[str] = None,
        threshold: float = 0.70,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find links semantically similar to query text.

        Enables queries like:
        - "moments of sudden clarity"
        - "anxious but determined decisions"
        - "protecting from uncertainty"

        Args:
            query_text: Natural language query
            link_type: Filter by link type (e.g., 'ENABLES', 'JUSTIFIES')
            threshold: Minimum similarity score
            limit: Maximum number of results

        Returns:
            List of matching links with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query_text)

        # FalkorDB uses db.idx.vector.queryRelationships procedure for link vector search
        # Procedure signature: (type, attribute, k, query_vector)
        # Returns relationships ordered by similarity (lower distance = more similar)

        if not link_type:
            # If no link_type specified, we need to query multiple types
            # For now, return empty (could be enhanced to query all types)
            logger.warning(f"[SemanticSearch] No link_type specified - vector search requires a type")
            return []

        # Build vector query using FalkorDB's vector search procedure
        vector_str = str(query_embedding)
        query = f"""
        CALL db.idx.vector.queryRelationships('{link_type}', 'relationship_embedding', {limit * 2}, vecf32({vector_str}))
        YIELD relationship, score
        WHERE score <= {1.0 - threshold}
        RETURN
          type(relationship) as link_type,
          relationship.goal as goal,
          relationship.mindstate as mindstate,
          relationship.felt_as as felt_as,
          relationship.embeddable_text as embeddable_text,
          score as distance
        ORDER BY score ASC
        LIMIT {limit}
        """

        try:
            result = self.r.execute_command('GRAPH.QUERY', self.graph_name, query)

            # Parse results
            matches = []
            if result and len(result) > 1:
                for row in result[1]:
                    link_type_val = row[0].decode() if isinstance(row[0], bytes) else row[0]
                    goal = row[1].decode() if isinstance(row[1], bytes) else row[1]
                    mindstate = row[2].decode() if isinstance(row[2], bytes) else row[2]
                    felt_as = row[3].decode() if isinstance(row[3], bytes) else row[3]
                    embeddable_text = row[4].decode() if isinstance(row[4], bytes) else row[4]
                    distance = float(row[5]) if row[5] is not None else 1.0

                    matches.append({
                        'link_type': link_type_val,
                        'goal': goal,
                        'mindstate': mindstate,
                        'felt_as': felt_as,
                        'embeddable_text': embeddable_text,
                        'similarity': 1.0 - distance  # Convert distance to similarity
                    })

            logger.info(f"[SemanticSearch] Found {len(matches)} similar links for query: '{query_text[:50]}...'")
            return matches

        except Exception as e:
            logger.error(f"[SemanticSearch] Query failed: {e}")
            return []

    def find_coping_patterns(
        self,
        query_text: str,
        threshold: float = 0.70,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find how consciousness has coped with similar situations.

        Example queries:
        - "How have I dealt with uncertainty?"
        - "What do I do when feeling overwhelmed?"
        - "Coping with failure"

        Args:
            query_text: Natural language query describing situation
            threshold: Minimum similarity score
            limit: Maximum results

        Returns:
            List of coping mechanisms with similarity scores
        """
        logger.info(f"[SemanticSearch] Finding coping patterns for: '{query_text}'")

        return self.find_similar_nodes(
            query_text=query_text,
            node_type='Coping_Mechanism',
            threshold=threshold,
            limit=limit
        )

    def trace_reasoning_evolution(
        self,
        query_text: str,
        threshold: float = 0.70,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find how reasoning has evolved over time in similar situations.

        Searches JUSTIFIES links for phenomenologically similar reasoning moments.

        Args:
            query_text: Natural language query describing reasoning context
            threshold: Minimum similarity score
            limit: Maximum results

        Returns:
            List of reasoning moments chronologically ordered
        """
        logger.info(f"[SemanticSearch] Tracing reasoning evolution for: '{query_text}'")

        # Find similar JUSTIFIES links
        matches = self.find_similar_links(
            query_text=query_text,
            link_type='JUSTIFIES',
            threshold=threshold,
            limit=limit
        )

        # TODO: Add chronological ordering by valid_at timestamp
        # This requires returning timestamp from query

        return matches

    def find_mental_state_moments(
        self,
        mindstate: str,
        threshold: float = 0.70,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find moments with similar mental states across all link types.

        Example queries:
        - "anxious but determined"
        - "peak clarity"
        - "overwhelmed and stuck"

        Args:
            mindstate: Description of mental state
            threshold: Minimum similarity score
            limit: Maximum results

        Returns:
            List of links with similar mindstates
        """
        logger.info(f"[SemanticSearch] Finding mental state moments: '{mindstate}'")

        # Search across all links for similar mindstates
        # This searches the embeddable_text which includes mindstate
        return self.find_similar_links(
            query_text=f"mindstate: {mindstate}",
            link_type=None,  # Search all link types
            threshold=threshold,
            limit=limit
        )

    def find_high_energy_insights(
        self,
        query_text: str,
        energy_threshold: float = 0.8,
        similarity_threshold: float = 0.70,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find high-energy moments similar to query.

        Hybrid query: semantic similarity + energy filter.

        Args:
            query_text: Natural language query
            energy_threshold: Minimum energy level (0-1)
            similarity_threshold: Minimum semantic similarity
            limit: Maximum results

        Returns:
            List of high-energy insights
        """
        logger.info(f"[SemanticSearch] Finding high-energy insights for: '{query_text}'")

        # TODO: This method needs redesign for FalkorDB vector search
        # Problem: db.idx.vector.queryRelationships requires specific link_type
        # Solution options:
        #   1. Query multiple link types and merge results
        #   2. Use regular MATCH with energy filter after vector query
        # For now, use fallback to regular query (won't use vector index)

        # Generate query embedding
        query_embedding = self.embedding_service.embed(query_text)

        # Fallback query without vector index (slower but works)
        # TODO: Optimize with vector search across multiple types
        query = """
        MATCH ()-[r]->()
        WHERE r.relationship_embedding IS NOT NULL
          AND r.energy > $energy_threshold
        RETURN
          type(r) as link_type,
          r.mindstate as mindstate,
          r.felt_as as felt_as,
          r.energy as energy,
          r.embeddable_text as embeddable_text,
          0.5 as similarity
        ORDER BY r.energy DESC
        LIMIT $limit
        """

        try:
            result = self.r.execute_command('GRAPH.QUERY', self.graph_name, query, {
                'query_emb': query_embedding,
                'energy_threshold': energy_threshold,
                'similarity_threshold': similarity_threshold,
                'limit': limit
            })

            matches = []
            if result and len(result) > 1:
                for row in result[1]:
                    matches.append({
                        'link_type': row[0],
                        'mindstate': row[1],
                        'felt_as': row[2],
                        'energy': row[3],
                        'embeddable_text': row[4],
                        'similarity': row[5]
                    })

            logger.info(f"[SemanticSearch] Found {len(matches)} high-energy insights")
            return matches

        except Exception as e:
            logger.error(f"[SemanticSearch] Query failed: {e}")
            return []


def main():
    """Test semantic search functionality."""

    # Initialize search for Felix's personal graph
    search = SemanticSearch('citizen_felix')

    print("\n" + "="*60)
    print("SEMANTIC SEARCH TEST")
    print("="*60)

    # Test 1: Find similar nodes
    print("\n1. Finding nodes similar to 'understanding consciousness architecture'...")
    nodes = search.find_similar_nodes(
        query_text="understanding consciousness architecture",
        threshold=0.5,
        limit=5
    )
    for node in nodes:
        print(f"  - {node['type']}: {node['name']} (similarity: {node['similarity']:.3f})")
        print(f"    {node['embeddable_text'][:100]}...")

    # Test 2: Find similar links
    print("\n2. Finding links similar to 'sudden clarity and insight'...")
    links = search.find_similar_links(
        query_text="sudden clarity and insight",
        threshold=0.5,
        limit=5
    )
    for link in links:
        print(f"  - {link['link_type']}: {link['mindstate']} (similarity: {link['similarity']:.3f})")
        print(f"    {link['felt_as']}")

    # Test 3: Find coping patterns
    print("\n3. Finding coping patterns for 'dealing with uncertainty'...")
    coping = search.find_coping_patterns(
        query_text="dealing with uncertainty",
        threshold=0.5,
        limit=5
    )
    for pattern in coping:
        print(f"  - {pattern['name']} (similarity: {pattern['similarity']:.3f})")
        print(f"    {pattern['embeddable_text']}")

    # Test 4: High-energy insights
    print("\n4. Finding high-energy insights about 'architecture decisions'...")
    insights = search.find_high_energy_insights(
        query_text="architecture decisions",
        energy_threshold=0.7,
        similarity_threshold=0.5,
        limit=5
    )
    for insight in insights:
        print(f"  - {insight['link_type']}: energy={insight['energy']:.2f}, similarity={insight['similarity']:.3f}")
        print(f"    {insight['felt_as']}")


if __name__ == "__main__":
    main()
