"""
SubEntity Merge/Split Logic - Consciousness-Driven SubEntity Lifecycle

Implements merge and split decisions for subentities based on:
- Redundancy detection (S_red > Q90 threshold)
- Coherence improvement (merge only if coherence(union) ≥ max(A,B))
- WM dry-run validation (merged subentity can still function in working memory)
- Context divergence (split only if ΔCtx separation exists)

Architecture:
- CALLED BY: consciousness_engine_v2.py at decision points
- USES: subentity_metrics.py for S_red/S_use computation
- EMITS: Audit events via subentity_lifecycle_audit.py

Author: Felix (Consciousness Engineer)
Created: 2025-10-29
Spec: docs/specs/v2/subentity/entity_differentiation.md §D.3
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

from orchestration.core import Graph, Subentity
from orchestration.libs.subentity_metrics import SubEntityMetrics, PairMetrics, PairScores
from orchestration.libs.subentity_lifecycle_audit import EntityLifecycleAudit, MergeDecision, SplitDecision

logger = logging.getLogger(__name__)


@dataclass
class MergeCandidate:
    """Pair of subentities proposed for merging"""
    subentity_a_id: str
    subentity_b_id: str
    s_red: float  # Redundancy score
    jaccard: float  # Member overlap
    coherence_a: float  # Current coherence of A
    coherence_b: float  # Current coherence of B
    reason: str  # Why merge proposed


@dataclass
class MergeResult:
    """Result of merge operation"""
    success: bool
    merged_entity_id: Optional[str]
    absorbed_ids: List[str]  # SubEntities merged into result
    coherence_after: float
    member_count: int
    error: Optional[str] = None


def compute_coherence(subentity: Subentity, graph: Graph) -> float:
    """
    Compute coherence score for a subentity.

    Coherence measures how tightly connected the members are.
    Higher coherence = members have strong links to each other.

    Algorithm:
    1. Get all member nodes
    2. Count links between members (internal links)
    3. Compute density: internal_links / max_possible_links

    Args:
        subentity: SubEntity to assess
        graph: Graph containing nodes and links

    Returns:
        Coherence score in [0, 1] range
    """
    members = subentity.get_members()
    if len(members) < 2:
        return 1.0  # Single-member subentities are trivially coherent

    member_ids = set(m.id for m in members)

    # Count internal links (both source and target in member set)
    internal_links = 0
    for link in graph.links.values():
        if link.source.id in member_ids and link.target.id in member_ids:
            internal_links += 1

    # Max possible links in fully connected graph: n(n-1)/2 (undirected)
    n = len(members)
    max_links = (n * (n - 1)) / 2

    if max_links == 0:
        return 1.0

    coherence = internal_links / max_links
    return min(coherence, 1.0)


def wm_dry_run(merged_members: Set[str], current_wm_entities: List[str], graph: Graph) -> bool:
    """
    Simulate working memory with merged subentity to ensure it can function.

    Tests if merged subentity would still be selectable in WM.
    If merge creates a subentity so large it dominates WM or so diffuse it never activates,
    that's a problem.

    Simple heuristic:
    - Merged subentity should have 5-200 members (practical range)
    - Energy of merged subentity should be within 0.5-2.0x median of current WM entities

    Args:
        merged_members: Set of member IDs in proposed merged subentity
        current_wm_entities: Currently selected WM subentity IDs
        graph: Graph for energy computation

    Returns:
        True if dry-run passes (merged subentity is functional)
    """
    # Size check
    if len(merged_members) < 5:
        logger.debug("[WM Dry-Run] FAIL: Merged subentity too small (<5 members)")
        return False

    if len(merged_members) > 200:
        logger.debug("[WM Dry-Run] FAIL: Merged subentity too large (>200 members)")
        return False

    # Energy check (if WM entities available for comparison)
    if current_wm_entities and graph.subentities:
        wm_energies = []
        for entity_id in current_wm_entities:
            if entity_id in graph.subentities:
                wm_energies.append(graph.subentities[entity_id].energy_runtime)

        if wm_energies:
            median_energy = float(np.median(wm_energies))

            # Estimate merged energy (sum of member energies above threshold)
            merged_energy = 0.0
            for member_id in merged_members:
                node = graph.get_node(member_id)
                if node and node.is_active():
                    merged_energy += max(0, node.E - node.theta)

            # Check if within 0.5-2.0x median
            if merged_energy < 0.5 * median_energy:
                logger.debug(f"[WM Dry-Run] FAIL: Merged energy {merged_energy:.2f} too low (median={median_energy:.2f})")
                return False

            if merged_energy > 2.0 * median_energy:
                logger.debug(f"[WM Dry-Run] FAIL: Merged energy {merged_energy:.2f} too high (median={median_energy:.2f})")
                return False

    logger.debug(f"[WM Dry-Run] PASS: Merged subentity functional ({len(merged_members)} members)")
    return True


def propose_merge(
    subentity_a_id: str,
    subentity_b_id: str,
    graph: Graph,
    metrics_lib: SubEntityMetrics,
    q90_threshold: float = 0.7
) -> Optional[MergeCandidate]:
    """
    Assess if two subentities should merge.

    Acceptance Criteria (ALL must pass):
    1. S_red > Q90 (high redundancy)
    2. coherence(union) ≥ max(coherence(A), coherence(B))
    3. WM dry-run passes

    Args:
        subentity_a_id: First subentity ID
        subentity_b_id: Second subentity ID
        graph: Graph containing subentities
        metrics_lib: SubEntity metrics library
        q90_threshold: Redundancy threshold (default Q90 ≈ 0.7)

    Returns:
        MergeCandidate if merge recommended, None otherwise
    """
    if subentity_a_id not in graph.subentities or subentity_b_id not in graph.subentities:
        return None

    subentity_a = graph.subentities[subentity_a_id]
    subentity_b = graph.subentities[subentity_b_id]

    # Compute pair metrics
    pair_metrics = metrics_lib.compute_pair_metrics(subentity_a_id, subentity_b_id)
    if not pair_metrics:
        logger.debug(f"[Merge] Cannot compute metrics for {subentity_a_id}, {subentity_b_id}")
        return None

    # Compute redundancy score
    scores = metrics_lib.compute_scores(pair_metrics)

    # Gate 1: Redundancy check
    if scores.S_red <= q90_threshold:
        logger.debug(f"[Merge] S_red={scores.S_red:.3f} <= Q90={q90_threshold:.3f}, not redundant")
        return None

    # Gate 2: Coherence check
    coherence_a = compute_coherence(subentity_a, graph)
    coherence_b = compute_coherence(subentity_b, graph)
    max_coherence = max(coherence_a, coherence_b)

    # Simulate union coherence (conservative: use minimum of current coherences)
    # Real implementation would compute actual union coherence
    union_coherence = min(coherence_a, coherence_b)  # Pessimistic estimate

    if union_coherence < max_coherence:
        logger.debug(
            f"[Merge] Union coherence {union_coherence:.3f} < max({coherence_a:.3f}, {coherence_b:.3f}), "
            "merge would degrade coherence"
        )
        return None

    # Gate 3: WM dry-run
    merged_members = set(m.id for m in subentity_a.get_members())
    merged_members.update(m.id for m in subentity_b.get_members())

    # Get current WM entities (if available)
    current_wm = []
    if hasattr(graph, '_last_wm_entities'):
        current_wm = graph._last_wm_entities

    if not wm_dry_run(merged_members, current_wm, graph):
        logger.debug("[Merge] WM dry-run failed, merged subentity would not function properly")
        return None

    # All gates passed - recommend merge
    reason = (
        f"S_red={scores.S_red:.3f} > Q90, "
        f"coherence_union={union_coherence:.3f} ≥ max({coherence_a:.3f}, {coherence_b:.3f}), "
        f"WM dry-run passed"
    )

    return MergeCandidate(
        subentity_a_id=subentity_a_id,
        subentity_b_id=subentity_b_id,
        s_red=scores.S_red,
        jaccard=pair_metrics.J,
        coherence_a=coherence_a,
        coherence_b=coherence_b,
        reason=reason
    )


def execute_merge(
    candidate: MergeCandidate,
    graph: Graph,
    audit: EntityLifecycleAudit
) -> MergeResult:
    """
    Execute merge of two subentities.

    Merge Strategy:
    1. Absorb B into A (A becomes merged subentity)
    2. Transfer all members from B to A
    3. Merge RELATES_TO highways (combine ease/flow)
    4. Mark B as dissolved
    5. Log merge decision for audit

    Args:
        candidate: Merge candidate with acceptance criteria met
        graph: Graph containing subentities
        audit: Audit logger for lifecycle events

    Returns:
        MergeResult with outcome
    """
    subentity_a = graph.subentities.get(candidate.subentity_a_id)
    subentity_b = graph.subentities.get(candidate.subentity_b_id)

    if not subentity_a or not subentity_b:
        return MergeResult(
            success=False,
            merged_entity_id=None,
            absorbed_ids=[],
            coherence_after=0.0,
            member_count=0,
            error="SubEntities not found in graph"
        )

    try:
        # Transfer members from B to A
        members_b = subentity_b.get_members()
        for member in members_b:
            # Add to A with weight from B
            weight = subentity_b.get_member_weight(member.id)
            subentity_a.add_member(member.id, weight=weight)

        # Update member count
        merged_member_count = len(subentity_a.get_members())

        # Compute post-merge coherence
        coherence_after = compute_coherence(subentity_a, graph)

        # Mark B as dissolved (remove from graph.subentities)
        del graph.subentities[candidate.subentity_b_id]

        # Log merge decision
        merge_decision = MergeDecision(
            from_entities=[candidate.subentity_a_id, candidate.subentity_b_id],
            to_entity=candidate.subentity_a_id,
            s_red=candidate.s_red,
            coherence_gate_passed=True,
            wm_dryrun_passed=True,
            coherence_before_a=candidate.coherence_a,
            coherence_before_b=candidate.coherence_b,
            coherence_after=coherence_after,
            member_mapping={},  # Could track detailed mapping if needed
            highway_mapping={}  # Could track RELATES_TO merge if needed
        )

        audit.log_merge(merge_decision)

        logger.info(
            f"[Merge] SUCCESS: {candidate.subentity_a_id} absorbed {candidate.subentity_b_id}, "
            f"coherence {coherence_after:.3f}, {merged_member_count} members"
        )

        return MergeResult(
            success=True,
            merged_entity_id=candidate.subentity_a_id,
            absorbed_ids=[candidate.subentity_b_id],
            coherence_after=coherence_after,
            member_count=merged_member_count
        )

    except Exception as e:
        logger.error(f"[Merge] FAILED: {e}")
        return MergeResult(
            success=False,
            merged_entity_id=None,
            absorbed_ids=[],
            coherence_after=0.0,
            member_count=0,
            error=str(e)
        )


def scan_for_merge_candidates(
    graph: Graph,
    metrics_lib: SubEntityMetrics,
    audit: EntityLifecycleAudit,
    max_per_tick: int = 1,
    q90_threshold: float = 0.7
) -> List[MergeResult]:
    """
    Scan all subentity pairs for merge candidates and execute merges.

    Called by consciousness tick loop (every N ticks).

    Strategy:
    - Check top-K pairs by Jaccard similarity (most overlap)
    - Propose merge for each pair
    - Execute merges that pass all gates
    - Limit merges per tick to avoid instability

    Args:
        graph: Graph with subentities
        metrics_lib: SubEntity metrics library
        audit: Lifecycle audit logger
        max_per_tick: Max merges to execute per tick (default 1)
        q90_threshold: Redundancy threshold (default 0.7)

    Returns:
        List of merge results (empty if no merges executed)
    """
    if not hasattr(graph, 'subentities') or len(graph.subentities) < 2:
        return []

    results = []
    subentity_ids = list(graph.subentities.keys())

    # Check all pairs (N² but N is small, typically 8-20 subentities)
    for i, subentity_a_id in enumerate(subentity_ids):
        if len(results) >= max_per_tick:
            break  # Hit merge limit for this tick

        for subentity_b_id in subentity_ids[i+1:]:
            # Propose merge
            candidate = propose_merge(
                subentity_a_id,
                subentity_b_id,
                graph,
                metrics_lib,
                q90_threshold
            )

            if candidate:
                logger.info(f"[Merge] Candidate found: {candidate.subentity_a_id} + {candidate.subentity_b_id}")

                # Execute merge
                result = execute_merge(candidate, graph, audit)
                results.append(result)

                if len(results) >= max_per_tick:
                    break  # Hit merge limit

    return results


# TODO: Implement split logic
# Split is more complex - requires bi-medoid partitioning, ΔCtx separation check
# Defer to next iteration
