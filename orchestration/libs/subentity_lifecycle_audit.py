"""
SubEntity Lifecycle Audit Log

Tracks all merge/split/redirect decisions with full provenance.
Enables analysis, rollback, debugging of entity evolution.

NOT a batch system - writes decisions synchronously when they occur.
NOT comprehensive history - stores decisions, not every state change.

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: entity_differentiation.md §E (observable events)
"""

import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

logger = logging.getLogger(__name__)


@dataclass
class MergeDecision:
    """Audit record for entity merge"""
    timestamp: int
    citizen_id: str
    from_entities: List[str]  # [A, B] being merged
    to_entity: str  # M created

    # Decision metrics
    S_red: float  # Redundancy score that justified merge
    coherence_before_A: float
    coherence_before_B: float
    coherence_after_M: float

    # Acceptance criteria
    passed_redundancy_gate: bool  # S_red > Q90
    passed_coherence_gate: bool  # coherence(M) >= max(A, B)
    passed_wm_dryrun: bool  # WM selection works with M

    # Provenance
    triggered_by: str  # "manual_review" | "quality_gate" | "maintenance"
    decision_maker: str  # "felix" | "ada" | etc

    # Rollback support
    member_mapping: Dict[str, str]  # {node_id: from_entity} for undo
    highway_mapping: List[Dict]  # Original RELATES_TO edges


@dataclass
class SplitDecision:
    """Audit record for entity split"""
    timestamp: int
    citizen_id: str
    from_entity: str  # E being split
    to_entities: List[str]  # [M1, M2] created

    # Decision metrics
    coherence_before: float
    coherence_M1: float
    coherence_M2: float
    silhouette_before: float
    delta_ctx_M1_M2: float  # Context divergence between splits

    # Acceptance criteria
    passed_coherence_gain: bool  # Both M1, M2 > E
    passed_separation_gate: bool  # ΔCtx(M1, M2) > threshold

    # Partition details
    cluster_1_nodes: List[str]
    cluster_2_nodes: List[str]
    partition_method: str  # "bi_medoid" | "modularity" | etc

    # Provenance
    triggered_by: str
    decision_maker: str


@dataclass
class RedirectDecision:
    """Audit record for candidate redirection at creation"""
    timestamp: int
    citizen_id: str
    from_candidate: str  # E' that wasn't created
    to_entity: str  # B that absorbed seeds

    # Decision metrics
    S_red: float  # Redundancy score that justified redirect
    seed_members: List[str]  # Nodes that were redirected
    weight_init: float  # Weak prior applied to redirected members

    # Acceptance criteria
    passed_redundancy_gate: bool  # S_red > Q90

    # Provenance
    triggered_by: str  # Usually "entity_creation"
    decision_maker: str


class SubEntityLifecycleAudit:
    """
    Audit log for entity lifecycle decisions.

    Writes decisions synchronously to:
    1. JSON append-only log (for analysis/rollback)
    2. WebSocket events (for real-time dashboard)

    NOT a database - just append-only files per citizen.
    """

    def __init__(self, citizen_id: str, log_dir: str = "data/entity_audit"):
        self.citizen_id = citizen_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.merge_log = self.log_dir / f"{citizen_id}_merges.jsonl"
        self.split_log = self.log_dir / f"{citizen_id}_splits.jsonl"
        self.redirect_log = self.log_dir / f"{citizen_id}_redirects.jsonl"

        self.broadcaster = ConsciousnessStateBroadcaster()

    async def log_merge(self, decision: MergeDecision):
        """
        Log merge decision with full provenance.

        Writes to:
        - JSONL append-only log for audit trail
        - WebSocket event for dashboard

        Args:
            decision: MergeDecision with all acceptance criteria
        """
        try:
            # Write to append-only log
            with open(self.merge_log, 'a') as f:
                f.write(json.dumps(asdict(decision)) + '\n')

            logger.info(
                f"[Audit] MERGE: {decision.from_entities} → {decision.to_entity} "
                f"(S_red={decision.S_red:.3f}, coherence: "
                f"{decision.coherence_before_A:.3f}/{decision.coherence_before_B:.3f} → "
                f"{decision.coherence_after_M:.3f})"
            )

            # Emit WebSocket event (spec §E.2)
            await self.broadcaster.broadcast_event("subentity.merged", {
                "event_type": "subentity.merged",
                "timestamp": decision.timestamp,
                "citizen_id": decision.citizen_id,
                "from_entities": decision.from_entities,
                "to_entity": decision.to_entity,

                "acceptance_criteria": {
                    "S_red": decision.S_red,
                    "passed_redundancy_gate": decision.passed_redundancy_gate,
                    "passed_coherence_gate": decision.passed_coherence_gate,
                    "passed_wm_dryrun": decision.passed_wm_dryrun
                },

                "coherence": {
                    "before_A": decision.coherence_before_A,
                    "before_B": decision.coherence_before_B,
                    "after_M": decision.coherence_after_M,
                    "gained": decision.coherence_after_M - max(
                        decision.coherence_before_A,
                        decision.coherence_before_B
                    )
                },

                "provenance": {
                    "triggered_by": decision.triggered_by,
                    "decision_maker": decision.decision_maker
                }
            })

        except Exception as e:
            logger.error(f"[Audit] Failed to log merge: {e}")

    async def log_split(self, decision: SplitDecision):
        """
        Log split decision with partition details.

        Args:
            decision: SplitDecision with coherence gains and separation
        """
        try:
            # Write to append-only log
            with open(self.split_log, 'a') as f:
                f.write(json.dumps(asdict(decision)) + '\n')

            logger.info(
                f"[Audit] SPLIT: {decision.from_entity} → {decision.to_entities} "
                f"(coherence: {decision.coherence_before:.3f} → "
                f"{decision.coherence_M1:.3f}/{decision.coherence_M2:.3f}, "
                f"ΔCtx={decision.delta_ctx_M1_M2:.3f})"
            )

            # Emit WebSocket event (spec §E.5)
            await self.broadcaster.broadcast_event("subentity.split", {
                "event_type": "subentity.split",
                "timestamp": decision.timestamp,
                "citizen_id": decision.citizen_id,
                "from_entity": decision.from_entity,
                "to_entities": decision.to_entities,

                "acceptance_criteria": {
                    "passed_coherence_gain": decision.passed_coherence_gain,
                    "passed_separation_gate": decision.passed_separation_gate
                },

                "metrics": {
                    "coherence_before": decision.coherence_before,
                    "coherence_M1": decision.coherence_M1,
                    "coherence_M2": decision.coherence_M2,
                    "silhouette_before": decision.silhouette_before,
                    "delta_ctx_M1_M2": decision.delta_ctx_M1_M2
                },

                "partition": {
                    "cluster_1_size": len(decision.cluster_1_nodes),
                    "cluster_2_size": len(decision.cluster_2_nodes),
                    "method": decision.partition_method
                },

                "provenance": {
                    "triggered_by": decision.triggered_by,
                    "decision_maker": decision.decision_maker
                }
            })

        except Exception as e:
            logger.error(f"[Audit] Failed to log split: {e}")

    async def log_redirect(self, decision: RedirectDecision):
        """
        Log candidate redirection at entity creation.

        Args:
            decision: RedirectDecision with redundancy score and seeds
        """
        try:
            # Write to append-only log
            with open(self.redirect_log, 'a') as f:
                f.write(json.dumps(asdict(decision)) + '\n')

            logger.info(
                f"[Audit] REDIRECT: candidate {decision.from_candidate} → "
                f"{decision.to_entity} (S_red={decision.S_red:.3f}, "
                f"{len(decision.seed_members)} seeds)"
            )

            # Emit WebSocket event (spec §E.4)
            await self.broadcaster.broadcast_event("candidate.redirected", {
                "event_type": "candidate.redirected",
                "timestamp": decision.timestamp,
                "citizen_id": decision.citizen_id,
                "from_candidate": decision.from_candidate,
                "to_entity": decision.to_entity,

                "reason": "high_redundancy_at_creation",

                "metrics": {
                    "S_red": decision.S_red,
                    "seed_members": decision.seed_members,
                    "weight_init": decision.weight_init
                },

                "acceptance_criteria": {
                    "passed_redundancy_gate": decision.passed_redundancy_gate
                },

                "provenance": {
                    "triggered_by": decision.triggered_by,
                    "decision_maker": decision.decision_maker
                }
            })

        except Exception as e:
            logger.error(f"[Audit] Failed to log redirect: {e}")

    def get_merge_history(self, limit: int = 100) -> List[Dict]:
        """
        Read recent merge decisions from log.

        Args:
            limit: Maximum number of recent decisions to return

        Returns:
            List of merge decisions (most recent first)
        """
        if not self.merge_log.exists():
            return []

        try:
            decisions = []
            with open(self.merge_log, 'r') as f:
                for line in f:
                    decisions.append(json.loads(line))

            # Return most recent first
            return decisions[-limit:][::-1]

        except Exception as e:
            logger.error(f"[Audit] Failed to read merge history: {e}")
            return []

    def get_split_history(self, limit: int = 100) -> List[Dict]:
        """Read recent split decisions from log"""
        if not self.split_log.exists():
            return []

        try:
            decisions = []
            with open(self.split_log, 'r') as f:
                for line in f:
                    decisions.append(json.loads(line))

            return decisions[-limit:][::-1]

        except Exception as e:
            logger.error(f"[Audit] Failed to read split history: {e}")
            return []

    def get_redirect_history(self, limit: int = 100) -> List[Dict]:
        """Read recent redirect decisions from log"""
        if not self.redirect_log.exists():
            return []

        try:
            decisions = []
            with open(self.redirect_log, 'r') as f:
                for line in f:
                    decisions.append(json.loads(line))

            return decisions[-limit:][::-1]

        except Exception as e:
            logger.error(f"[Audit] Failed to read redirect history: {e}")
            return []

    def get_entity_provenance(self, subentity_id: str) -> Dict:
        """
        Get full provenance chain for an entity.

        Traces back through merges/splits to understand entity origin.

        Args:
            subentity_id: SubEntity to trace

        Returns:
            Dict with origin chain, parent subentities, decisions
        """
        # TODO: Implement provenance tracing by walking back through logs
        # For now, simple search
        provenance = {
            "subentity_id": subentity_id,
            "created_from_merge": [],
            "created_from_split": [],
            "absorbed_redirects": []
        }

        # Check if created by merge
        for merge in self.get_merge_history():
            if merge["to_entity"] == subentity_id:
                provenance["created_from_merge"].append(merge)

        # Check if created by split
        for split in self.get_split_history():
            if subentity_id in split["to_entities"]:
                provenance["created_from_split"].append(split)

        # Check if absorbed redirects
        for redirect in self.get_redirect_history():
            if redirect["to_entity"] == subentity_id:
                provenance["absorbed_redirects"].append(redirect)

        return provenance
