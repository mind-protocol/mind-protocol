"""
Duplicate Node Merging - Single-Energy + Bitemporal

Mechanism for detecting and merging semantically duplicate nodes while preserving
history, telemetry, and observability.

ARCHITECTURAL PRINCIPLES:
- Single-energy substrate: E remains scalar, never per-entity
- Bitemporal tracking: Preserves version history via supersession
- Conservative consolidation: Energy is ephemeral, don't invent it
- Auditable: Full merge history and before/after metrics

Algorithm:
1. Detect candidates (type match + similarity)
2. Select canonical (age → connectivity → weight)
3. Consolidate: E, memberships, links, names
4. Record bitemporally with supersession chain

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/learning_and_trace/duplicate_node_merging.md
"""

import math
import logging
from typing import Dict, List, Set, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.node import Node
    from orchestration.core.link import Link

from orchestration.mechanisms.bitemporal import supersede, create_new_version

logger = logging.getLogger(__name__)


# === Data Classes ===

@dataclass
class SimilarityScore:
    """
    Explainable similarity score between two nodes.

    Used for duplicate detection with full scorecard for audit.
    """
    type_match: bool              # Same node type
    name_similarity: float        # Normalized name similarity [0, 1]
    embedding_similarity: float   # Cosine similarity [0, 1] (future)
    metadata_overlap: float       # Shared provenance/scope [0, 1]

    # Overall score
    overall: float                # Weighted combination

    # Explainability
    reason: str                   # Why these are similar


@dataclass
class MergeMetrics:
    """
    Complete merge metrics for observability.

    Emitted as `node.merge` event per spec §6.
    """
    # Identity
    kept_node_id: str             # Canonical node ID
    absorbed_node_ids: List[str]  # Absorbed node IDs
    merge_timestamp: datetime     # When merge occurred

    # Scores
    similarity_scores: Dict[str, float]  # Pairwise similarity scores

    # Before state
    before_degree: Dict[str, int]       # Degree of each node before
    before_zW: Dict[str, float]         # Standardized weight before
    before_energy: Dict[str, float]     # Energy before

    # After state
    after_degree: int             # Degree after merge
    after_zW: float               # Standardized weight after
    after_energy: float           # Energy after

    # Consolidation stats
    links_redirected: int         # Links redirected to canonical
    parallel_links_merged: int    # Parallel links consolidated
    aliases_added: List[str]      # Aliases added to canonical

    # Reason
    merge_reason: str             # Why merge was performed


# === Detection ===

def compute_name_similarity(name_a: str, name_b: str) -> float:
    """
    Compute normalized name similarity.

    Uses simple character-based similarity for now.
    Future: Could use Levenshtein, Jaro-Winkler, etc.

    Args:
        name_a: First node name
        name_b: Second node name

    Returns:
        Similarity score [0, 1]

    Example:
        >>> compute_name_similarity("context_reconstruction", "context_reconstruction_v2")
        0.88
    """
    # Normalize
    a = name_a.lower().strip()
    b = name_b.lower().strip()

    if a == b:
        return 1.0

    # Simple character overlap (Jaccard)
    set_a = set(a)
    set_b = set(b)

    intersection = len(set_a & set_b)
    union = len(set_a | set_b)

    if union == 0:
        return 0.0

    return intersection / union


def compute_similarity(node_a: 'Node', node_b: 'Node') -> SimilarityScore:
    """
    Compute similarity score between two nodes.

    Checks:
    - Type match (required)
    - Name similarity (high weight)
    - Embedding similarity (future - requires embedding service)
    - Metadata overlap (provenance, scope)

    Args:
        node_a: First node
        node_b: Second node

    Returns:
        SimilarityScore with explainability

    Example:
        >>> score = compute_similarity(node1, node2)
        >>> if score.overall > 0.85:
        ...     print(f"High similarity: {score.reason}")
    """
    # Type match (required)
    type_match = node_a.node_type == node_b.node_type
    if not type_match:
        return SimilarityScore(
            type_match=False,
            name_similarity=0.0,
            embedding_similarity=0.0,
            metadata_overlap=0.0,
            overall=0.0,
            reason="Type mismatch"
        )

    # Name similarity
    name_sim = compute_name_similarity(node_a.name, node_b.name)

    # Embedding similarity (TODO: requires embedding service)
    embedding_sim = 0.0  # Placeholder

    # Metadata overlap (scope, created_by)
    metadata_sim = 0.0
    if node_a.scope == node_b.scope:
        metadata_sim += 0.5
    if node_a.properties.get("created_by") == node_b.properties.get("created_by"):
        metadata_sim += 0.5

    # Weighted combination
    # High weight on name similarity (most reliable signal)
    overall = (
        0.6 * name_sim +
        0.2 * embedding_sim +  # Low weight until implemented
        0.2 * metadata_sim
    )

    # Reason
    if overall > 0.85:
        reason = f"High similarity (name={name_sim:.2f}, meta={metadata_sim:.2f})"
    elif overall > 0.70:
        reason = f"Moderate similarity (name={name_sim:.2f})"
    else:
        reason = f"Low similarity (name={name_sim:.2f})"

    return SimilarityScore(
        type_match=True,
        name_similarity=name_sim,
        embedding_similarity=embedding_sim,
        metadata_overlap=metadata_sim,
        overall=overall,
        reason=reason
    )


def find_duplicate_candidates(
    graph: 'Graph',
    node: 'Node',
    threshold: float = 0.85
) -> List[Tuple['Node', SimilarityScore]]:
    """
    Find duplicate candidates for a given node.

    Returns nodes with similarity above threshold, sorted by similarity.

    Args:
        graph: Consciousness graph
        node: Node to find duplicates for
        threshold: Minimum similarity threshold [0, 1]

    Returns:
        List of (candidate_node, score) sorted by similarity (descending)

    Example:
        >>> candidates = find_duplicate_candidates(graph, my_node, threshold=0.85)
        >>> if candidates:
        ...     best_match, score = candidates[0]
        ...     print(f"Best match: {best_match.name} (score={score.overall:.2f})")
    """
    candidates = []

    for other_node in graph.nodes.values():
        # Skip self
        if other_node.id == node.id:
            continue

        # Compute similarity
        score = compute_similarity(node, other_node)

        # Above threshold?
        if score.overall >= threshold:
            candidates.append((other_node, score))

    # Sort by similarity (descending)
    candidates.sort(key=lambda x: x[1].overall, reverse=True)

    return candidates


# === Canonical Selection ===

def select_canonical(nodes: List['Node']) -> 'Node':
    """
    Select canonical node from duplicate candidates.

    Tiebreaker order (spec §2.2):
    1. Age (oldest = created_at)
    2. Connectivity (highest degree)
    3. Standardized weight (highest z-score)

    Prefer the object with the richest lineage.

    Args:
        nodes: List of duplicate candidates

    Returns:
        Canonical node (the one to keep)

    Example:
        >>> canonical = select_canonical([node1, node2, node3])
        >>> print(f"Keeping: {canonical.name}")
    """
    if not nodes:
        raise ValueError("Cannot select canonical from empty list")

    if len(nodes) == 1:
        return nodes[0]

    # Tiebreaker 1: Age (oldest)
    oldest_time = min(n.created_at for n in nodes)
    oldest_nodes = [n for n in nodes if n.created_at == oldest_time]

    if len(oldest_nodes) == 1:
        return oldest_nodes[0]

    # Tiebreaker 2: Connectivity (highest degree)
    max_degree = max(
        len(n.outgoing_links) + len(n.incoming_links)
        for n in oldest_nodes
    )
    high_degree_nodes = [
        n for n in oldest_nodes
        if len(n.outgoing_links) + len(n.incoming_links) == max_degree
    ]

    if len(high_degree_nodes) == 1:
        return high_degree_nodes[0]

    # Tiebreaker 3: Weight (highest log_weight as proxy for z-score)
    max_weight = max(n.log_weight for n in high_degree_nodes)
    return next(n for n in high_degree_nodes if n.log_weight == max_weight)


# === Energy Consolidation (Single-Energy Substrate) ===

def consolidate_energy(
    canonical: 'Node',
    absorbed: List['Node'],
    is_quiescent: bool = True,
    saturation_cap: float = 10.0
) -> float:
    """
    Consolidate energy from absorbed nodes to canonical.

    Per spec §2.3 (single-energy substrate):
    - Quiescent: E_canon = max(E_a, E_b, ...) [safe default]
    - Live: E_canon = saturate(E_a + E_b + ...) [capped sum]

    Energy is EPHEMERAL - the merge should NOT invent energy.

    Args:
        canonical: Canonical node (will be modified)
        absorbed: Absorbed nodes
        is_quiescent: Are all nodes below threshold? (default True = safe)
        saturation_cap: Maximum energy to prevent spikes

    Returns:
        Consolidated energy value

    Example:
        >>> # Safe quiescent merge
        >>> E_result = consolidate_energy(canonical, [dup1, dup2], is_quiescent=True)
        >>>
        >>> # Live merge with saturation
        >>> E_result = consolidate_energy(canonical, [dup1, dup2], is_quiescent=False, saturation_cap=5.0)
    """
    all_energies = [canonical.E] + [node.E for node in absorbed]

    if is_quiescent:
        # Safe: Take maximum (no invention)
        E_consolidated = max(all_energies)
    else:
        # Live: Saturated sum (prevent spikes)
        E_sum = sum(all_energies)
        E_consolidated = min(E_sum, saturation_cap)

    # Write to canonical
    canonical.E = E_consolidated

    return E_consolidated


def consolidate_memberships(
    canonical: 'Node',
    absorbed: List['Node']
) -> Dict[str, float]:
    """
    Consolidate entity memberships using max aggregation.

    Per spec §2.3: m_canon(S) = max(m_a(S), m_b(S))

    NOTE: This is a placeholder until we implement the membership system.
    Current node model doesn't have explicit memberships yet (future feature).

    Args:
        canonical: Canonical node (will be modified)
        absorbed: Absorbed nodes

    Returns:
        Dict of entity_id -> membership_score

    Example:
        >>> memberships = consolidate_memberships(canonical, [dup1, dup2])
        >>> print(f"Entity memberships: {memberships}")
    """
    # TODO: Implement when membership system exists
    # For now, just return empty dict
    logger.debug("Membership consolidation: Not yet implemented (future feature)")
    return {}


# === Link Consolidation ===

def redirect_links(
    graph: 'Graph',
    canonical: 'Node',
    absorbed: List['Node']
) -> Tuple[int, int]:
    """
    Redirect all links from absorbed nodes to canonical.

    Process:
    1. Redirect incoming links: target = canonical
    2. Redirect outgoing links: source = canonical
    3. Merge parallel links (same source + target + type)
    4. Update graph structure

    Args:
        graph: Consciousness graph
        canonical: Canonical node
        absorbed: Absorbed nodes

    Returns:
        Tuple of (links_redirected, parallel_links_merged)

    Example:
        >>> redirected, merged = redirect_links(graph, canonical, [dup1, dup2])
        >>> print(f"Redirected {redirected} links, merged {merged} parallels")
    """
    links_redirected = 0
    parallel_links_merged = 0

    # Track canonical's existing links for parallel detection
    canonical_outgoing = {
        (link.target.id, link.link_type): link
        for link in canonical.outgoing_links
    }
    canonical_incoming = {
        (link.source.id, link.link_type): link
        for link in canonical.incoming_links
    }

    for absorbed_node in absorbed:
        # Redirect outgoing links
        for link in list(absorbed_node.outgoing_links):
            key = (link.target.id, link.link_type)

            if key in canonical_outgoing:
                # Parallel link exists - merge telemetry
                existing = canonical_outgoing[key]
                merge_link_telemetry(existing, link)

                # Remove absorbed link
                graph.remove_link(link.id)
                parallel_links_merged += 1
            else:
                # No parallel - redirect source
                link.source_id = canonical.id
                link.source = canonical

                # Update references
                absorbed_node.outgoing_links.remove(link)
                canonical.outgoing_links.append(link)
                canonical_outgoing[key] = link

                links_redirected += 1

        # Redirect incoming links
        for link in list(absorbed_node.incoming_links):
            key = (link.source.id, link.link_type)

            if key in canonical_incoming:
                # Parallel link exists - merge telemetry
                existing = canonical_incoming[key]
                merge_link_telemetry(existing, link)

                # Remove absorbed link
                graph.remove_link(link.id)
                parallel_links_merged += 1
            else:
                # No parallel - redirect target
                link.target_id = canonical.id
                link.target = canonical

                # Update references
                absorbed_node.incoming_links.remove(link)
                canonical.incoming_links.append(link)
                canonical_incoming[key] = link

                links_redirected += 1

    return (links_redirected, parallel_links_merged)


def merge_link_telemetry(existing: 'Link', absorbed: 'Link') -> None:
    """
    Merge telemetry from absorbed link into existing link.

    Per spec §2.3: Combine telemetry and keep the larger log_weight
    (or average in standardized space).

    For EMAs, use weighted combination based on link weights.

    Args:
        existing: Link to keep (will be modified)
        absorbed: Link to merge in (telemetry only)

    Example:
        >>> merge_link_telemetry(existing_link, absorbed_link)
        >>> print(f"Merged link weight: {existing_link.log_weight:.3f}")
    """
    # Weight: Take maximum log_weight (strongest signal)
    if absorbed.log_weight > existing.log_weight:
        existing.log_weight = absorbed.log_weight

    # TODO: Merge EMAs with weighted combination
    # This requires EMA fields on Link (future feature)

    logger.debug(f"Merged link telemetry: kept={existing.id}, absorbed={absorbed.id}")


# === Name Consolidation ===

def consolidate_names(
    canonical: 'Node',
    absorbed: List['Node']
) -> List[str]:
    """
    Consolidate names: keep canonical name, store others as aliases.

    Per spec §2.3: Keep canonical name, store others in aliases[] for retrieval.

    Args:
        canonical: Canonical node (will be modified)
        absorbed: Absorbed nodes

    Returns:
        List of aliases added

    Example:
        >>> aliases = consolidate_names(canonical, [dup1, dup2])
        >>> print(f"Added aliases: {aliases}")
    """
    # Get or create aliases list
    if "aliases" not in canonical.properties:
        canonical.properties["aliases"] = []

    aliases = canonical.properties["aliases"]
    aliases_added = []

    # Add absorbed names as aliases
    for node in absorbed:
        if node.name != canonical.name and node.name not in aliases:
            aliases.append(node.name)
            aliases_added.append(node.name)

    canonical.properties["aliases"] = aliases

    return aliases_added


# === Merge Execution ===

def merge_nodes(
    graph: 'Graph',
    canonical: 'Node',
    absorbed: List['Node'],
    reason: str = "Semantic duplicate detected",
    is_quiescent: bool = True
) -> MergeMetrics:
    """
    Execute complete node merge with bitemporal tracking.

    Process (per spec §2):
    1. Consolidate energy (single-energy substrate)
    2. Consolidate memberships (future)
    3. Redirect links
    4. Consolidate names (aliases)
    5. Record bitemporal lineage (supersession)
    6. Remove absorbed nodes
    7. Return metrics

    Args:
        graph: Consciousness graph
        canonical: Canonical node to keep
        absorbed: Nodes to merge in
        reason: Why merge is being performed
        is_quiescent: Are nodes below threshold? (affects energy)

    Returns:
        MergeMetrics with full observability

    Example:
        >>> metrics = merge_nodes(graph, canonical, [dup1, dup2], "High similarity")
        >>> print(f"Merged {len(absorbed)} nodes into {canonical.name}")
        >>> print(f"Redirected {metrics.links_redirected} links")
    """
    logger.info(f"Merging nodes: canonical={canonical.id}, absorbed={[n.id for n in absorbed]}")

    # Capture before state
    before_degree = {
        node.id: len(node.outgoing_links) + len(node.incoming_links)
        for node in [canonical] + absorbed
    }
    before_zW = {
        node.id: node.log_weight  # Using log_weight as proxy for z-score
        for node in [canonical] + absorbed
    }
    before_energy = {
        node.id: node.E
        for node in [canonical] + absorbed
    }

    # 1. Consolidate energy (single-energy substrate)
    E_after = consolidate_energy(canonical, absorbed, is_quiescent=is_quiescent)

    # 2. Consolidate memberships (future)
    consolidate_memberships(canonical, absorbed)

    # 3. Redirect links
    links_redirected, parallel_merged = redirect_links(graph, canonical, absorbed)

    # 4. Consolidate names
    aliases_added = consolidate_names(canonical, absorbed)

    # 5. Record bitemporal lineage
    # Create new version of canonical that supersedes all absorbed
    canonical_new = create_new_version(canonical)

    # Mark absorbed nodes as superseded
    for absorbed_node in absorbed:
        supersede(absorbed_node, canonical_new)

    # Update graph with new canonical version
    # (In practice, we'd update the canonical in-place but track version chain)
    # For now, just update metadata
    canonical.vid = canonical_new.vid
    canonical.supersedes = canonical_new.supersedes
    if "merge_history" not in canonical.properties:
        canonical.properties["merge_history"] = []
    canonical.properties["merge_history"].append({
        "absorbed_ids": [n.id for n in absorbed],
        "absorbed_vids": [n.vid for n in absorbed],
        "merge_timestamp": datetime.now().isoformat(),
        "reason": reason
    })

    # 6. Remove absorbed nodes from graph
    for absorbed_node in absorbed:
        graph.remove_node(absorbed_node.id)

    # After state
    after_degree = len(canonical.outgoing_links) + len(canonical.incoming_links)
    after_zW = canonical.log_weight
    after_energy = canonical.E

    # Build metrics
    metrics = MergeMetrics(
        kept_node_id=canonical.id,
        absorbed_node_ids=[n.id for n in absorbed],
        merge_timestamp=datetime.now(),
        similarity_scores={},  # Filled by caller
        before_degree=before_degree,
        before_zW=before_zW,
        before_energy=before_energy,
        after_degree=after_degree,
        after_zW=after_zW,
        after_energy=after_energy,
        links_redirected=links_redirected,
        parallel_links_merged=parallel_merged,
        aliases_added=aliases_added,
        merge_reason=reason
    )

    logger.info(f"Merge complete: {metrics.links_redirected} links redirected, {metrics.parallel_links_merged} parallels merged")

    return metrics


# === High-Level API ===

def find_and_merge_duplicates(
    graph: 'Graph',
    threshold: float = 0.85,
    max_merges_per_run: int = 10
) -> List[MergeMetrics]:
    """
    Find and merge duplicate nodes in graph.

    High-level API for periodic duplicate detection and merging.

    Process:
    1. Scan all nodes for duplicates
    2. Group duplicates by canonical
    3. Merge groups (up to max_merges_per_run)
    4. Return metrics

    Args:
        graph: Consciousness graph
        threshold: Similarity threshold [0, 1]
        max_merges_per_run: Maximum merges per run (rate limiting)

    Returns:
        List of MergeMetrics for all merges performed

    Example:
        >>> metrics = find_and_merge_duplicates(graph, threshold=0.85)
        >>> print(f"Performed {len(metrics)} merges")
        >>> for m in metrics:
        ...     print(f"  {m.kept_node_id}: absorbed {len(m.absorbed_node_ids)} nodes")
    """
    all_metrics = []
    merges_performed = 0

    # Track processed nodes to avoid duplicate work
    processed = set()

    for node in list(graph.nodes.values()):
        if merges_performed >= max_merges_per_run:
            logger.info(f"Reached max merges per run: {max_merges_per_run}")
            break

        if node.id in processed:
            continue

        # Find duplicates
        candidates = find_duplicate_candidates(graph, node, threshold=threshold)

        if not candidates:
            continue

        # Group: node + all candidates
        duplicate_group = [node] + [c[0] for c in candidates]

        # Select canonical
        canonical = select_canonical(duplicate_group)
        absorbed = [n for n in duplicate_group if n.id != canonical.id]

        if not absorbed:
            continue

        # Check if quiescent (all below threshold)
        is_quiescent = all(n.E < n.theta for n in duplicate_group)

        # Merge
        metrics = merge_nodes(
            graph, canonical, absorbed,
            reason=f"Automatic merge (similarity >= {threshold:.2f})",
            is_quiescent=is_quiescent
        )

        # Add similarity scores to metrics
        for candidate, score in candidates:
            metrics.similarity_scores[candidate.id] = score.overall

        all_metrics.append(metrics)
        merges_performed += 1

        # Mark all as processed
        processed.update(n.id for n in duplicate_group)

        logger.info(f"Merged {len(absorbed)} nodes into {canonical.id}")

    return all_metrics
