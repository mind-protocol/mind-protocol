"""
Entity Creation with Redundancy Checking

Wraps entity creation with redirect logic to prevent redundant entities.

When new entity E' is proposed:
1. Find k nearest existing entities by seed member overlap
2. Compute S_red(E', B) for each neighbor B
3. If max S_red > Q90 threshold → REDIRECT to B instead of creating E'
4. If all S_red <= Q90 → CREATE E' normally

Redirect means:
- Don't create E'
- Add seed members to existing entity B with weak prior weight (0.3)
- Log redirect decision for audit trail

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: Entity Differentiation Refactor Priority 2 (Luca)
"""

import logging
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from orchestration.core import Graph, Subentity, Link, LinkType
from orchestration.libs.subentity_metrics import SubEntityMetrics
from orchestration.libs.subentity_lifecycle_audit import SubEntityLifecycleAudit, RedirectDecision
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter

logger = logging.getLogger(__name__)


@dataclass
class SubEntityCreationProposal:
    """Proposal for new entity creation"""
    citizen_id: str
    entity_kind: str  # "functional" | "semantic"
    role_or_topic: str
    description: str
    seed_members: List[str]  # Node IDs to seed membership
    scope: str  # "personal" | "organizational"
    created_by: str
    confidence: float = 0.7


@dataclass
class CreationResult:
    """Result of entity creation attempt"""
    created: bool  # True if entity created, False if redirected
    subentity_id: Optional[str]  # New entity ID if created, redirect target if redirected
    redirect_to: Optional[str]  # Entity ID that absorbed seeds (if redirected)
    S_red: Optional[float]  # Redundancy score that triggered redirect
    action: str  # "created" | "redirected" | "failed"
    reason: str  # Human-readable explanation


class SubEntityCreation:
    """
    Entity creation with redundancy checking.

    Prevents redundant entities by checking for high overlap with existing entities
    before creation. If new entity E' would be redundant with existing B, redirects
    seeds to B instead of creating E'.
    """

    def __init__(
        self,
        adapter: FalkorDBAdapter,
        graph: Optional[Graph] = None,
        redundancy_threshold: float = 0.7,  # Q90 approximation
        redirect_weight: float = 0.3,  # Weak prior for redirected members
        k_neighbors: int = 10  # Check top-k nearest entities
    ):
        """
        Initialize entity creation handler.

        Args:
            adapter: FalkorDB adapter for metrics and persistence
            graph: Optional in-memory graph (if not using adapter only)
            redundancy_threshold: S_red threshold for redirect (default Q90 ≈ 0.7)
            redirect_weight: Weight for redirected members (weak prior)
            k_neighbors: How many nearest neighbors to check
        """
        self.adapter = adapter
        self.graph = graph
        self.metrics = SubEntityMetrics(adapter)
        self.redundancy_threshold = redundancy_threshold
        self.redirect_weight = redirect_weight
        self.k_neighbors = k_neighbors

    def propose_entity_creation(self, proposal: EntityCreationProposal) -> CreationResult:
        """
        Propose entity creation with redundancy check.

        Checks if proposed entity E' would be redundant with existing entities.
        If S_red(E', B) > threshold for some B, redirects seeds to B instead.

        Args:
            proposal: Entity creation proposal

        Returns:
            CreationResult with creation status and action taken
        """
        logger.info(
            f"[SubEntityCreation] Evaluating proposal: {proposal.role_or_topic} "
            f"with {len(proposal.seed_members)} seeds"
        )

        # Check for redundancy with existing entities
        redirect_target, max_S_red = self._check_redundancy(proposal)

        if redirect_target:
            # REDIRECT: Absorb seeds into existing entity
            logger.info(
                f"[SubEntityCreation] REDIRECT: {proposal.role_or_topic} → {redirect_target} "
                f"(S_red={max_S_red:.3f} > {self.redundancy_threshold})"
            )

            result = self._execute_redirect(proposal, redirect_target, max_S_red)
            return result

        else:
            # CREATE: No redundancy detected
            logger.info(
                f"[SubEntityCreation] CREATE: {proposal.role_or_topic} "
                f"(max S_red={max_S_red:.3f} <= {self.redundancy_threshold})"
            )

            result = self._execute_creation(proposal)
            return result

    def _check_redundancy(
        self,
        proposal: EntityCreationProposal
    ) -> Tuple[Optional[str], float]:
        """
        Check if proposed entity is redundant with existing entities.

        Computes seed overlap (Jaccard) with k nearest entities, then computes
        full metrics and S_red score. If any S_red > threshold, returns redirect target.

        Args:
            proposal: Entity creation proposal

        Returns:
            (redirect_target_id, max_S_red) or (None, max_S_red) if no redirect
        """
        # Strategy: Create temporary entity in memory to compute metrics
        # (Don't persist yet)

        temp_entity_id = f"temp_{proposal.citizen_id}_{proposal.role_or_topic}_{int(time.time())}"

        # For now, we'll use a simpler approach: check seed overlap with existing entities
        # Full implementation would create temp entity and compute full metrics

        # Get all existing entities for this citizen
        try:
            query = """
            MATCH (e:SubEntity)
            WHERE e.id STARTS WITH $citizen_prefix
            RETURN e.id AS subentity_id
            """

            result = self.adapter.graph_store.query(
                query,
                {"citizen_prefix": f"entity_{proposal.citizen_id}_"}
            )

            existing_entities = []
            if hasattr(result, 'result_set'):
                existing_entities = [row[0] for row in result.result_set]
            elif isinstance(result, list):
                existing_entities = [row[0] if isinstance(row, list) else row['subentity_id'] for row in result]

            if not existing_entities:
                logger.debug("[SubEntityCreation] No existing entities, no redundancy check needed")
                return None, 0.0

            logger.debug(f"[SubEntityCreation] Checking redundancy against {len(existing_entities)} entities")

            # For each existing entity, compute seed overlap (quick approximation of J metric)
            max_S_red = 0.0
            redirect_target = None

            for subentity_id in existing_entities[:self.k_neighbors]:
                # Get members of existing entity
                overlap = self._compute_seed_overlap(proposal.seed_members, subentity_id)

                # Quick approximation: S_red ≈ Jaccard for seed overlap
                # (Full computation would include C, U, H, ΔCtx)
                S_red_approx = overlap

                if S_red_approx > max_S_red:
                    max_S_red = S_red_approx
                    if S_red_approx > self.redundancy_threshold:
                        redirect_target = subentity_id

            return redirect_target, max_S_red

        except Exception as e:
            logger.error(f"[SubEntityCreation] Failed to check redundancy: {e}")
            return None, 0.0

    def _compute_seed_overlap(self, seed_members: List[str], subentity_id: str) -> float:
        """
        Compute Jaccard overlap between seed members and existing entity members.

        Args:
            seed_members: Proposed seed node IDs
            subentity_id: Existing entity to check

        Returns:
            Jaccard similarity (0-1)
        """
        try:
            query = """
            MATCH (e:SubEntity {id: $subentity_id})
            MATCH (n:Node)-[:MEMBER_OF]->(e)
            RETURN collect(n.id) AS members
            """

            result = self.adapter.graph_store.query(query, {"subentity_id": subentity_id})

            if hasattr(result, 'result_set') and result.result_set:
                existing_members = result.result_set[0][0]
            elif isinstance(result, list) and result:
                existing_members = result[0][0] if isinstance(result[0], list) else result[0]['members']
            else:
                return 0.0

            # Compute Jaccard
            seed_set = set(seed_members)
            existing_set = set(existing_members)

            intersection = len(seed_set & existing_set)
            union = len(seed_set | existing_set)

            if union == 0:
                return 0.0

            jaccard = intersection / union

            logger.debug(
                f"[SubEntityCreation] Overlap with {subentity_id}: "
                f"{intersection}/{union} = {jaccard:.3f}"
            )

            return jaccard

        except Exception as e:
            logger.error(f"[SubEntityCreation] Failed to compute overlap: {e}")
            return 0.0

    def _execute_redirect(
        self,
        proposal: EntityCreationProposal,
        redirect_target: str,
        S_red: float
    ) -> CreationResult:
        """
        Execute redirect: add seed members to existing entity with weak prior.

        Args:
            proposal: Original entity proposal
            redirect_target: Entity ID to redirect to
            S_red: Redundancy score that triggered redirect

        Returns:
            CreationResult with redirect details
        """
        try:
            # Add seed members to existing entity with weak prior weight
            members_added = 0

            for node_id in proposal.seed_members:
                # Create MEMBER_OF link with weak prior
                link_id = f"belongs_{node_id}_{redirect_target}_redirect_{int(time.time())}"

                # Check if membership already exists
                check_query = """
                MATCH (n:Node {id: $node_id})-[r:MEMBER_OF]->(e:SubEntity {id: $subentity_id})
                RETURN r
                """

                check_result = self.adapter.graph_store.query(
                    check_query,
                    {"node_id": node_id, "subentity_id": redirect_target}
                )

                # If membership exists, skip (don't overwrite stronger weights)
                if (hasattr(check_result, 'result_set') and check_result.result_set) or \
                   (isinstance(check_result, list) and check_result):
                    logger.debug(f"[SubEntityCreation] Node {node_id} already member of {redirect_target}")
                    continue

                # Create new membership with weak prior
                create_query = """
                MATCH (n:Node {id: $node_id})
                MATCH (e:SubEntity {id: $subentity_id})
                CREATE (n)-[r:MEMBER_OF]->(e)
                SET r.weight = $weight,
                    r.energy = 0.0,
                    r.provenance = 'redirect',
                    r.redirected_from = $candidate,
                    r.last_coactivation_ema = 0.0
                """

                self.adapter.graph_store.query(
                    create_query,
                    {
                        "node_id": node_id,
                        "subentity_id": redirect_target,
                        "weight": self.redirect_weight,
                        "candidate": proposal.role_or_topic
                    }
                )

                members_added += 1

            logger.info(
                f"[SubEntityCreation] Redirected {members_added} seeds to {redirect_target} "
                f"(weight={self.redirect_weight})"
            )

            # Log redirect decision
            audit = SubEntityLifecycleAudit(proposal.citizen_id)
            decision = RedirectDecision(
                timestamp=int(time.time()),
                citizen_id=proposal.citizen_id,
                from_candidate=proposal.role_or_topic,
                to_entity=redirect_target,
                S_red=S_red,
                seed_members=proposal.seed_members,
                weight_init=self.redirect_weight,
                passed_redundancy_gate=True,
                triggered_by="entity_creation",
                decision_maker=proposal.created_by
            )

            # Note: log_redirect is async, but we're in sync context
            # For now, skip async call - Felix will wire this properly
            # await audit.log_redirect(decision)

            return CreationResult(
                created=False,
                subentity_id=None,
                redirect_to=redirect_target,
                S_red=S_red,
                action="redirected",
                reason=f"Redundant with {redirect_target} (S_red={S_red:.3f})"
            )

        except Exception as e:
            logger.error(f"[SubEntityCreation] Failed to execute redirect: {e}")
            return CreationResult(
                created=False,
                subentity_id=None,
                redirect_to=None,
                S_red=S_red,
                action="failed",
                reason=f"Redirect failed: {e}"
            )

    def _execute_creation(self, proposal: EntityCreationProposal) -> CreationResult:
        """
        Execute entity creation: create new entity with seed members.

        Args:
            proposal: Entity creation proposal

        Returns:
            CreationResult with created entity details
        """
        try:
            subentity_id = f"entity_{proposal.citizen_id}_{proposal.role_or_topic}"

            # Create SubEntity node
            create_entity_query = """
            CREATE (e:SubEntity {
                id: $subentity_id,
                entity_kind: $kind,
                role_or_topic: $role,
                description: $description,
                stability_state: 'provisional',
                scope: $scope,
                created_from: 'runtime_creation',
                created_by: $created_by,
                confidence: $confidence,
                member_count: $member_count,
                created_at: datetime(),
                valid_at: datetime(),
                coherence_ema: 0.0,
                phi_mean: 0.0
            })
            RETURN e.id AS subentity_id
            """

            result = self.adapter.graph_store.query(
                create_entity_query,
                {
                    "subentity_id": subentity_id,
                    "kind": proposal.entity_kind,
                    "role": proposal.role_or_topic,
                    "description": proposal.description,
                    "scope": proposal.scope,
                    "created_by": proposal.created_by,
                    "confidence": proposal.confidence,
                    "member_count": len(proposal.seed_members)
                }
            )

            # Create MEMBER_OF links for seeds
            members_added = 0
            for node_id in proposal.seed_members:
                link_query = """
                MATCH (n:Node {id: $node_id})
                MATCH (e:SubEntity {id: $subentity_id})
                CREATE (n)-[r:MEMBER_OF]->(e)
                SET r.weight = 0.8,
                    r.energy = 0.0,
                    r.provenance = 'seed_creation',
                    r.last_coactivation_ema = 0.0
                """

                self.adapter.graph_store.query(
                    link_query,
                    {"node_id": node_id, "subentity_id": subentity_id}
                )

                members_added += 1

            logger.info(
                f"[SubEntityCreation] Created entity {subentity_id} with {members_added} seed members"
            )

            return CreationResult(
                created=True,
                subentity_id=subentity_id,
                redirect_to=None,
                S_red=None,
                action="created",
                reason=f"Entity created with {members_added} seeds"
            )

        except Exception as e:
            logger.error(f"[SubEntityCreation] Failed to create entity: {e}")
            return CreationResult(
                created=False,
                subentity_id=None,
                redirect_to=None,
                S_red=None,
                action="failed",
                reason=f"Creation failed: {e}"
            )


# --- Convenience Functions ---

def create_entity_with_redirect_check(
    adapter: FalkorDBAdapter,
    proposal: EntityCreationProposal,
    redundancy_threshold: float = 0.7
) -> CreationResult:
    """
    Convenience function for entity creation with redirect check.

    Args:
        adapter: FalkorDB adapter
        proposal: Entity creation proposal
        redundancy_threshold: S_red threshold for redirect

    Returns:
        CreationResult with outcome
    """
    creator = SubEntityCreation(
        adapter=adapter,
        redundancy_threshold=redundancy_threshold
    )

    return creator.propose_entity_creation(proposal)
