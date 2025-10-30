"""
SubEntity Weight Learning Observability - Scale A Operations

Terminology Note:
This module operates on SubEntity (Scale A) - weighted neighborhoods
discovered via clustering. See TAXONOMY_RECONCILIATION.md for full
architecture.

SubEntity: Weighted neighborhoods (200-500 per citizen)
Mode: IFS-level meta-roles (5-15 per citizen, Scale B)

This is Scale A operations - SubEntity membership weight tracking.

Emits real-time events via WebSocket broadcaster for dashboard visualization.
Events capture weight updates, membership pruning, and SubEntity lifecycle transitions.

Usage:
    from orchestration.mechanisms.subentity_weight_learning_observe import (
        emit_weights_updated,
        emit_membership_pruned,
        emit_lifecycle_event
    )

    # After weight learning updates
    await emit_weights_updated(
        broadcaster, "N1", "felix", frame_id, run_id,
        "E.runtime", "Runtime Engineering",
        changes=[...], stats={...}
    )

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-25
Updated: 2025-10-26 (Scale A terminology clarification)
Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 4
"""

from typing import List, Dict, Any, Optional
from time import time
import logging

logger = logging.getLogger(__name__)


async def emit_weights_updated(
    broadcaster,
    level: str,
    citizen_id: str,
    frame_id: int,
    run_id: str,
    entity_id: str,
    entity_name: str,
    changes: List[Dict[str, Any]],
    stats: Dict[str, Any],
    mission_id: Optional[str] = None,
    stimulus_id: Optional[str] = None
):
    """
    Emit subentity.weights.updated event when membership weights change.

    Captures weight learning updates for entity membership, including individual
    node weight changes and entity-level statistics (cohesion, stability, formation quality).

    Args:
        broadcaster: WebSocket broadcaster instance
        level: Graph level ("N1" | "N2" | "N3")
        citizen_id: Citizen identifier (e.g., "felix", "ada")
        frame_id: Engine frame number
        run_id: Process run identifier (e.g., "2025-10-25T07:11Z@felix")
        entity_id: SubEntity that changed (Scale A, e.g., "E.architect")
        entity_name: Human-readable SubEntity name (e.g., "Architect")
        changes: List of membership changes, each:
            {
                "node_id": str,
                "weight_prev": float,
                "weight_new": float,
                "delta": float,
                "activation_ema": float,
                "activation_count_inc": int,
                "last_activated_ts": int
            }
        stats: SubEntity-level stats (Scale A):
            {
                "cohesion_before": float,
                "cohesion_after": float,
                "stability_z": float,
                "formation_quality_q": float,
                "num_pruned": int,
                "budget_method": str,
                "ema_alpha": float
            }
        mission_id: Optional mission context
        stimulus_id: Optional stimulus context

    Example:
        >>> await emit_weights_updated(
        ...     broadcaster, "N1", "felix", 2341, "2025-10-25T07:11Z@felix",
        ...     "E.runtime", "Runtime Engineering",
        ...     changes=[{
        ...         "node_id": "N.diffusion_note",
        ...         "weight_prev": 0.62, "weight_new": 0.69, "delta": 0.07,
        ...         "activation_ema": 0.41, "activation_count_inc": 1,
        ...         "last_activated_ts": 1730074798123
        ...     }],
        ...     stats={"cohesion_after": 0.75, "stability_z": 1.8, "num_pruned": 0}
        ... )
    """
    if not broadcaster:
        logger.debug("No broadcaster available, skipping weights.updated event")
        return

    event = {
        "topic": "subentity.weights.updated",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "frame_id": frame_id,
        "run_id": run_id,
        "mission_id": mission_id,
        "stimulus_id": stimulus_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:frame{frame_id}",
        "payload": {
            "entity": {
                "id": entity_id,
                "name": entity_name,
                "cohesion_before": stats.get("cohesion_before"),
                "cohesion_after": stats.get("cohesion_after"),
                "stability_z": stats.get("stability_z"),
                "formation_quality_q": stats.get("formation_quality_q"),
            },
            "stats": {
                "num_updated": len(changes),
                "num_pruned": stats.get("num_pruned", 0),
                "budget_method": stats.get("budget_method"),
                "ema_alpha": stats.get("ema_alpha"),
            },
            "memberships": changes
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted weights.updated for {entity_id}: {len(changes)} changes")


async def emit_membership_pruned(
    broadcaster,
    level: str,
    citizen_id: str,
    frame_id: int,
    run_id: str,
    entity_id: str,
    node_id: str,
    weight_prev: float,
    activation_ema_prev: float,
    reason: str = "below_learned_floor"
):
    """
    Emit subentity.membership.pruned event when MEMBER_OF edge deleted.

    Signals removal of weak or stale memberships during sparsification.
    Helps dashboard visualize membership churn and entity boundary evolution.

    Args:
        broadcaster: WebSocket broadcaster
        level: Graph level ("N1" | "N2" | "N3")
        citizen_id: Citizen identifier
        frame_id: Engine frame number
        run_id: Process run ID
        entity_id: SubEntity losing member (Scale A, e.g., "E.architect")
        node_id: Node being pruned (e.g., "N.stale_concept")
        weight_prev: Previous weight before pruning
        activation_ema_prev: Previous activation EMA
        reason: Why pruned ("below_learned_floor" | "stale_membership" | "entity_dissolved")

    Example:
        >>> await emit_membership_pruned(
        ...     broadcaster, "N1", "felix", 3456, "2025-10-25T08:30Z@felix",
        ...     "E.runtime", "N.old_pattern", 0.12, 0.03,
        ...     reason="below_learned_floor"
        ... )
    """
    if not broadcaster:
        return

    event = {
        "topic": "subentity.membership.pruned",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "frame_id": frame_id,
        "run_id": run_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:{node_id}:frame{frame_id}",
        "payload": {
            "entity_id": entity_id,
            "node_id": node_id,
            "weight_prev": weight_prev,
            "activation_ema_prev": activation_ema_prev,
            "reason": reason
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted membership.pruned: {node_id} from {entity_id}")


async def emit_lifecycle_event(
    broadcaster,
    level: str,
    citizen_id: str,
    run_id: str,
    entity_id: str,
    prev_status: str,
    new_status: str,
    evidence: Dict[str, float]
):
    """
    Emit subentity.lifecycle event for entity promotion/dissolution.

    Signals major entity lifecycle transitions (candidate → provisional → mature → dissolved).
    Provides evidence for transition (formation quality, stability, membership drift).

    Args:
        broadcaster: WebSocket broadcaster
        level: Graph level ("N1" | "N2" | "N3")
        citizen_id: Citizen identifier
        run_id: Process run ID
        entity_id: SubEntity changing status (Scale A, e.g., "E.emerging_pattern")
        prev_status: Previous status ("candidate" | "provisional" | "mature")
        new_status: New status ("candidate" | "provisional" | "mature" | "dissolved")
        evidence: Evidence for transition:
            {
                "formation_quality_q": float,
                "stability_z": float,
                "membership_drift_q": float
            }

    Example:
        >>> await emit_lifecycle_event(
        ...     broadcaster, "N1", "felix", "2025-10-25T09:00Z@felix",
        ...     "E.new_pattern", "candidate", "provisional",
        ...     evidence={"formation_quality_q": 0.78, "stability_z": 2.1}
        ... )
    """
    if not broadcaster:
        return

    event = {
        "topic": "subentity.lifecycle",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "run_id": run_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:{new_status}:{time()}",
        "payload": {
            "entity_id": entity_id,
            "prev_status": prev_status,
            "new_status": new_status,
            "evidence": evidence
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted lifecycle: {entity_id} {prev_status} → {new_status}")
