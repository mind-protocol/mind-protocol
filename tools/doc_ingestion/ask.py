#!/usr/bin/env python3
"""
mp.sh ask - Generic semantic graph traversal for question answering

Usage Examples (context + intent + problem + ask format):

  "I'm implementing entity persistence for the consciousness substrate.
   I need to ensure subentities reload correctly after restart without losing graph structure.
   Current approach uses FalkorDB MERGE but restart shows empty entity counts.
   What are the proven patterns for reliable graph persistence with validation?"

  "Working on dashboard WebSocket integration to show real-time telemetry.
   Goal is to display consciousness dynamics as they happen for debugging.
   Dashboard connects but shows 'No data yet' even when engines are active.
   What's the complete flow from engine events to dashboard updates?"

  "Setting up document ingestion pipeline to build knowledge graph from specs.
   Want to extract semantic clusters that agents can traverse for task planning.
   Current LLM extracts nodes but produces thin edges without required metadata.
   How do we enforce rich link metadata during automated extraction?"

Algorithm:
0. Build contextual query embedding (thread + system context)
1. Candidate discovery across ALL node labels (K=5 per label)
2. Generic beam search exploration (B=4, T=9 steps)
3. Select best path and hydrate fully
4. Emit as logical sequence: node → links → node → ...

Output: Single JSON object with query, context_used, cluster (ordered sequence), notes
"""

import sys
import os
import json
import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from falkordb import FalkorDB
from sentence_transformers import SentenceTransformer
from orchestration.config.graph_names import resolver


# ============================================================================
# CONSTANTS (defaults baked in, overridable via env)
# ============================================================================

W = 6  # turns for thread summary
K_SENTENCES = 2  # sentences for MMR
MMR_LAMBDA = 0.7  # diversity parameter
K_PER_LABEL = 5  # candidates per label
N_INITIAL = 6  # initial nodes for beam
BEAM_WIDTH = int(os.environ.get('ASK_BEAM_WIDTH', '4'))
MAX_STEPS = int(os.environ.get('ASK_MAX_STEPS', '9'))
MARGINAL_GAIN_THRESHOLD = 0.01  # 1% minimum improvement


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PathState:
    """Represents a partial path in beam search"""
    nodes: List[str]  # node IDs in path order
    edges: List[Tuple[str, str, str]]  # (source_id, edge_type, target_id)
    score: float  # geometric mean path score
    last_step_type: str  # 'node' or 'links'
    depth: int  # number of steps taken


# ============================================================================
# EMBEDDING & SIMILARITY
# ============================================================================

class EmbeddingService:
    """Handle text embedding and similarity"""

    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.dims = 768

    def embed(self, text: str) -> np.ndarray:
        """Embed text to vector"""
        return self.model.encode(text, normalize_embeddings=True)

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Compute cosine similarity (vectors already normalized)"""
        return float(np.dot(v1, v2))


# ============================================================================
# CONTEXT BUILDING
# ============================================================================

def build_contextual_query(question: str, embedding_service: EmbeddingService) -> Tuple[np.ndarray, Dict[str, str]]:
    """
    Build contextual query embedding with thread and system summaries

    Returns: (query_vector, context_dict)
    """
    # Thread summary: For now, placeholder (would need conversation history)
    # In real implementation, this would use last W=6 turns + MMR selection
    thread_summary = "Conversation context not available in standalone mode"

    # System summary: Core Mind Protocol rules (no caching - computed fresh each time)
    system_summary = "no Documents; rich link meta; no invented IDs; quality non-regression"

    # Compose query text
    query_text = f"{question} | ctx: {thread_summary} | sys: {system_summary}"

    # Embed
    query_vector = embedding_service.embed(query_text)

    context_used = {
        "thread_summary": thread_summary,
        "system_summary": system_summary
    }

    return query_vector, context_used


# ============================================================================
# CANDIDATE DISCOVERY
# ============================================================================

def discover_candidates(
    graph: Any,
    query_vector: np.ndarray,
    k_per_label: int = K_PER_LABEL
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Discover candidates across ALL node labels using vector search

    Returns: {label: [{id, labels, props, score_cos}, ...]}
    """
    # Get all labels dynamically
    labels_result = graph.query("CALL db.labels() YIELD label RETURN collect(label) AS labels")
    all_labels = labels_result.result_set[0][0] if labels_result.result_set else []

    candidates = {}

    for label in all_labels:
        # Skip schema-related labels
        if label in ['NodeTypeSchema', 'LinkTypeSchema', 'FieldSchema']:
            continue

        try:
            # Vector search for this label
            # Try content_embedding first (newer schema), fall back to embedding
            query = f"""
            CALL db.idx.vector.queryNodes('{label}', 'content_embedding', {k_per_label}, vecf32($query_vec))
            YIELD node, score
            RETURN node.id AS id, labels(node) AS labels, properties(node) AS props, score
            """

            result = graph.query(query, params={'query_vec': query_vector.tolist()})

            label_candidates = []
            for record in result.result_set:
                node_data = {
                    'id': record[0],
                    'labels': record[1],
                    'props': record[2],
                    'score_cos': record[3]
                }
                # Remove embedding from props (too large)
                if 'embedding' in node_data['props']:
                    del node_data['props']['embedding']

                label_candidates.append(node_data)

            if label_candidates:
                candidates[label] = label_candidates

        except Exception as e:
            # Label might not have vector index - skip silently
            continue

    return candidates


# ============================================================================
# SCORING
# ============================================================================

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to range, handling string inputs"""
    # Convert string to float if needed (graph stores some fields as strings)
    if isinstance(value, str):
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.5  # Default fallback
    return max(min_val, min(max_val, value))


def node_score(node_props: Dict[str, Any], cosine_score: float) -> float:
    """
    Node score = cos(v_q, v_n) × confidence × base_weight
    """
    cos_clamped = clamp(cosine_score)
    confidence = clamp(node_props.get('confidence', 0.5))
    base_weight = clamp(node_props.get('base_weight', 0.5))

    return cos_clamped * confidence * base_weight


def edge_score(edge_props: Dict[str, Any]) -> float:
    """
    Edge score = confidence × energy
    """
    confidence = clamp(edge_props.get('confidence', 0.5))
    energy = clamp(edge_props.get('energy', 0.5))

    return confidence * energy


def path_score(node_scores: List[float], edge_scores: List[float]) -> float:
    """
    Path score = geometric mean of all node + edge scores
    S_path = exp( (Σ ln s_node + Σ ln s_edge) / (N + E) )
    """
    all_scores = node_scores + edge_scores
    if not all_scores:
        return 0.0

    # Add small epsilon to avoid log(0)
    epsilon = 1e-10
    log_sum = sum(math.log(max(s, epsilon)) for s in all_scores)

    return math.exp(log_sum / len(all_scores))


# ============================================================================
# BEAM SEARCH
# ============================================================================

def beam_search(
    graph: Any,
    initial_nodes: List[Dict[str, Any]],
    query_vector: np.ndarray,
    beam_width: int = BEAM_WIDTH,
    max_steps: int = MAX_STEPS
) -> PathState:
    """
    Generic beam search exploration

    Algorithm:
    - Start with top N nodes by relevance
    - Alternate: node → outgoing/incoming edges → nodes those edges touch
    - Score paths using geometric mean
    - De-dup nodes within path (no cycles)
    - Stop when reaching max steps or marginal gain < 1%

    Returns: Best path found
    """
    # Initialize beam with top N initial nodes
    beam: List[PathState] = []

    for node_data in initial_nodes[:N_INITIAL]:
        node_id = node_data['id']
        score = node_score(node_data['props'], node_data['score_cos'])

        beam.append(PathState(
            nodes=[node_id],
            edges=[],
            score=score,
            last_step_type='node',
            depth=1
        ))

    # Sort beam by score
    beam.sort(key=lambda s: s.score, reverse=True)
    beam = beam[:beam_width]

    # Track best score for marginal gain check
    best_score = beam[0].score if beam else 0.0

    # Beam search loop
    for step in range(max_steps):
        new_beam = []

        for state in beam:
            if state.last_step_type == 'node':
                # Expand from node to edges
                last_node = state.nodes[-1]

                # Query outgoing AND incoming edges
                edge_query = """
                MATCH (n {id: $node_id})-[r]-(m)
                RETURN type(r) AS rel_type, startNode(r).id AS source_id,
                       endNode(r).id AS target_id, properties(r) AS props,
                       properties(m) AS target_props, m.id AS target_id_check
                LIMIT 20
                """

                result = graph.query(edge_query, params={'node_id': last_node})

                for record in result.result_set:
                    rel_type = record[0]
                    source_id = record[1]
                    target_id = record[2]
                    edge_props = record[3]
                    target_props = record[4]

                    # Skip if target already in path (avoid cycles)
                    if target_id in state.nodes:
                        continue

                    # Create new state with edge added
                    new_edges = state.edges + [(source_id, rel_type, target_id)]

                    # Calculate new score (add edge score to geometric mean)
                    e_score = edge_score(edge_props)
                    # Recompute path score with new edge
                    # Simplified: multiply current by edge score ratio
                    new_score = state.score * (e_score ** (1.0 / (len(state.nodes) + len(new_edges))))

                    new_beam.append(PathState(
                        nodes=state.nodes.copy(),
                        edges=new_edges,
                        score=new_score,
                        last_step_type='links',
                        depth=state.depth + 1
                    ))

            else:  # last_step_type == 'links'
                # Expand from links to target node
                if not state.edges:
                    continue

                last_edge = state.edges[-1]
                target_id = last_edge[2]

                # Query target node properties
                node_query = """
                MATCH (n {id: $node_id})
                RETURN properties(n) AS props, n.embedding AS embedding
                """
                result = graph.query(node_query, params={'node_id': target_id})

                if not result.result_set:
                    continue

                node_props = result.result_set[0][0]
                node_embedding = result.result_set[0][1]

                # Calculate cosine similarity
                if node_embedding:
                    cos_sim = np.dot(query_vector, np.array(node_embedding))
                else:
                    cos_sim = 0.5  # fallback

                # Add node to path
                new_nodes = state.nodes + [target_id]
                n_score = node_score(node_props, cos_sim)

                # Recompute path score
                new_score = state.score * (n_score ** (1.0 / len(new_nodes)))

                new_beam.append(PathState(
                    nodes=new_nodes,
                    edges=state.edges.copy(),
                    score=new_score,
                    last_step_type='node',
                    depth=state.depth + 1
                ))

        if not new_beam:
            break

        # Sort and keep top beam_width
        new_beam.sort(key=lambda s: s.score, reverse=True)
        beam = new_beam[:beam_width]

        # Check marginal gain
        new_best_score = beam[0].score
        marginal_gain = (new_best_score - best_score) / (best_score + 1e-10)

        if marginal_gain < MARGINAL_GAIN_THRESHOLD:
            break

        best_score = new_best_score

    # Return best path
    return beam[0] if beam else PathState([], [], 0.0, 'node', 0)


# ============================================================================
# HYDRATION & SERIALIZATION
# ============================================================================

def hydrate_and_serialize(graph: Any, path: PathState) -> List[Dict[str, Any]]:
    """
    Hydrate full path and serialize as: node → links → node → ...

    Include all props (universal + type-specific), excluding ops timestamps and embeddings
    Include full link props + meta
    """
    if not path.nodes:
        return []

    # Batch query to get all nodes and edges in path
    node_ids = path.nodes

    # Get all nodes
    nodes_query = """
    MATCH (n)
    WHERE n.id IN $ids
    RETURN n.id AS id, labels(n) AS labels, properties(n) AS props
    """
    nodes_result = graph.query(nodes_query, params={'ids': node_ids})

    nodes_by_id = {}
    for record in nodes_result.result_set:
        node_id = record[0]
        labels = record[1]
        props = record[2].copy()

        # Remove operational timestamps and embeddings
        for key in ['created_at', 'updated_at', 'expired_at', 'invalid_at', 'embedding', 'content_embedding', 'embeddable_text']:
            props.pop(key, None)

        nodes_by_id[node_id] = {
            'type': 'node',
            'labels': labels,
            'id': node_id,
            'props': props
        }

    # Get all edges in path
    edges_by_source = defaultdict(list)
    for source_id, rel_type, target_id in path.edges:
        edge_query = """
        MATCH (s {id: $source_id})-[r:$rel_type]->(t {id: $target_id})
        RETURN type(r) AS rel_type, properties(r) AS props
        LIMIT 1
        """
        # Note: Cypher doesn't allow parameterized relationship types in simple form
        # Need to use dynamic query
        edge_query_dynamic = f"""
        MATCH (s {{id: $source_id}})-[r:`{rel_type}`]->(t {{id: $target_id}})
        RETURN type(r) AS rel_type, properties(r) AS props
        LIMIT 1
        """

        result = graph.query(edge_query_dynamic, params={'source_id': source_id, 'target_id': target_id})

        if result.result_set:
            rel_type_actual = result.result_set[0][0]
            props = result.result_set[0][1].copy()

            # Remove operational timestamps
            for key in ['created_at', 'updated_at', 'expired_at', 'invalid_at']:
                props.pop(key, None)

            edges_by_source[source_id].append({
                'rel_type': rel_type_actual,
                'source': source_id,
                'target': target_id,
                'props': props
            })

    # Serialize as sequence: node → links → node → ...
    cluster = []
    for i, node_id in enumerate(path.nodes):
        # Add node
        if node_id in nodes_by_id:
            cluster.append(nodes_by_id[node_id])

        # Add links from this node (if not last node)
        if i < len(path.nodes) - 1:
            if node_id in edges_by_source:
                cluster.append({
                    'type': 'links',
                    'items': edges_by_source[node_id]
                })

    return cluster


# ============================================================================
# MAIN
# ============================================================================

def ask(question: str) -> Dict[str, Any]:
    """
    Execute the ask algorithm

    Returns: JSON-serializable result dict
    """
    # Initialize services
    embedding_service = EmbeddingService()
    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph(resolver.org_base())

    # 0. Build contextual query embedding
    query_vector, context_used = build_contextual_query(question, embedding_service)

    # 1. Candidate discovery across ALL node labels
    candidates = discover_candidates(graph, query_vector)

    # Flatten candidates for initial beam (top N globally by score)
    all_candidates = []
    for label, label_cands in candidates.items():
        all_candidates.extend(label_cands)

    # Sort by cosine score (relevance)
    all_candidates.sort(key=lambda c: c['score_cos'], reverse=True)

    if not all_candidates:
        return {
            'query': question,
            'context_used': context_used,
            'cluster': [],
            'notes': 'No candidates found'
        }

    # 2. Generic beam search exploration
    best_path = beam_search(graph, all_candidates, query_vector)

    # 3. Select best path and hydrate fully
    cluster = hydrate_and_serialize(graph, best_path)

    # 4. Emit result
    return {
        'query': question,
        'context_used': context_used,
        'cluster': cluster,
        'notes': f'Top path score: {best_path.score:.4f}, depth: {best_path.depth}'
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ask.py \"<question>\"", file=sys.stderr)
        sys.exit(1)

    question = ' '.join(sys.argv[1:])

    try:
        result = ask(question)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'query': question
        }, indent=2), file=sys.stderr)
        sys.exit(1)
