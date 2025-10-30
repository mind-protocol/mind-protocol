"""
Auto-Resolve Missing Endpoint (ARM)

When a link references a non-existent node ID, automatically search for candidates
using vector similarity + string matching. Don't let bad IDs kill the flow.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


def parse_node_id(node_id: str) -> Tuple[Optional[str], str]:
    """
    Parse node_id into (label_guess, slug)
    
    Examples:
        "mechanism:comprehensive_health_check" -> ("Mechanism", "comprehensive_health_check")
        "invalid_format" -> (None, "invalid_format")
    """
    match = re.match(r'^([A-Za-z0-9_]+):(.*)$', node_id)
    if not match:
        return None, node_id
    
    label_prefix, slug = match.groups()
    
    # Normalize label: capitalize, handle underscores
    label_guess = label_prefix.replace('_', ' ').title().replace(' ', '_')
    
    return label_guess, slug


def slug_to_query_text(slug: str) -> str:
    """
    Convert slug to query text for embedding
    
    Examples:
        "comprehensive_health_check_algorithm" -> "comprehensive health check algorithm"
        "ACIDTransactionSpec" -> "ACID Transaction Spec"
    """
    # Replace underscores and hyphens with spaces
    text = slug.replace('_', ' ').replace('-', ' ')
    
    # Split camelCase: "ACIDTransaction" -> "ACID Transaction"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add synonyms
    text = text.replace(' algorithm', ' algorithm method')
    text = text.replace(' spec', ' spec specification')
    
    return text.lower()


def auto_resolve_missing_endpoint(
    graph: Any,
    missing_id: str,
    other_id: Optional[str] = None,
    edge_type: Optional[str] = None,
    embedding_service: Any = None,
    k_per_label: int = 10
) -> Dict[str, Any]:
    """
    Auto-resolve a missing node ID by searching for candidates
    
    Args:
        graph: GraphWrapper instance
        missing_id: The node ID that doesn't exist (e.g., "mechanism:health_check")
        other_id: The other endpoint of the edge (for context)
        edge_type: The edge type (for optional hints)
        embedding_service: EmbeddingService for vector search
        k_per_label: Top K candidates per label
    
    Returns:
        {
            'missing_id': str,
            'label_guess': Optional[str],
            'query_text': str,
            'candidates': List[{
                'id': str,
                'label': str,
                'name': str,
                'score_vector': float,
                'score_string': float,
                'score_combined': float,
                'props': dict
            }],
            'action': 'arm_search'
        }
    """
    logger.info(f"[ARM] Auto-resolving missing node: {missing_id}")
    
    # Step 1: Parse & normalize
    label_guess, slug = parse_node_id(missing_id)
    query_text = slug_to_query_text(slug)
    
    # Add edge type hints for better context
    if edge_type in ['MEASURES', 'REFUTES', 'JUSTIFIES']:
        query_text += ' measurement metric evidence'
    
    logger.info(f"[ARM] Parsed: label={label_guess}, slug={slug}, query={query_text}")
    
    # Step 2: Get query embedding
    if embedding_service is None:
        from embedding import get_embedding_service
        embedding_service = get_embedding_service()
    
    query_vec = embedding_service.embed([query_text])[0]
    
    # Step 3: Vector search across labels
    candidates = []
    labels_to_search = []
    
    # If we have a label guess, search it first
    if label_guess:
        labels_to_search.append(label_guess)
    
    # Also search all common labels
    common_labels = ['Principle', 'Best_Practice', 'Mechanism', 'Behavior', 'Process', 'Metric']
    for label in common_labels:
        if label != label_guess:
            labels_to_search.append(label)
    
    seen_ids = set()
    
    for label in labels_to_search:
        try:
            # Use FalkorDB vector search
            result = graph.r.query(f"""
                CALL db.idx.vector.queryNodes('{label}', 'content_embedding', {k_per_label}, vecf32($query_vec))
                YIELD node, score
                RETURN node.id AS id, labels(node)[0] AS label, properties(node) AS props, score
            """, {'query_vec': query_vec.tolist()})
            
            for row in result.result_set:
                node_id = row[0]
                if node_id in seen_ids:
                    continue
                seen_ids.add(node_id)
                
                node_label = row[1]
                props = row[2]
                score_cos = float(row[3]) if row[3] else 0.0
                
                # Step 4: String similarity
                name = props.get('name', '')
                aliases = props.get('aliases', [])
                if isinstance(aliases, str):
                    aliases = [aliases]
                
                # Token set ratio against name and aliases
                lex_scores = [fuzz.token_set_ratio(query_text, name.lower()) / 100.0]
                for alias in aliases:
                    lex_scores.append(fuzz.token_set_ratio(query_text, str(alias).lower()) / 100.0)
                
                score_string = max(lex_scores) if lex_scores else 0.0
                
                # Combined score: 70% vector, 30% string
                score_combined = 0.7 * score_cos + 0.3 * score_string
                
                candidates.append({
                    'id': node_id,
                    'label': node_label,
                    'name': name,
                    'score_vector': score_cos,
                    'score_string': score_string,
                    'score_combined': score_combined,
                    'props': props
                })
        
        except Exception as e:
            logger.warning(f"[ARM] Failed to search label {label}: {e}")
            continue
    
    # Sort by combined score
    candidates.sort(key=lambda x: x['score_combined'], reverse=True)
    
    # Take top 5
    candidates = candidates[:5]
    
    logger.info(f"[ARM] Found {len(candidates)} candidates for {missing_id}")
    for i, cand in enumerate(candidates[:3]):
        logger.info(f"  {i+1}. {cand['id']} (score={cand['score_combined']:.3f}, vector={cand['score_vector']:.3f}, string={cand['score_string']:.3f})")
    
    return {
        'missing_id': missing_id,
        'label_guess': label_guess,
        'query_text': query_text,
        'candidates': candidates,
        'action': 'arm_search'
    }
