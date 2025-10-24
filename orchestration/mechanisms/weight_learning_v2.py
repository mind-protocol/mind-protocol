"""
Weight Learning V2 - Entity-context-aware TRACE reinforcement.

Implements dual-view weight architecture (Priority 4):
- Global weights: Updated by 20% of TRACE signal
- Entity overlays: Updated by 80% of TRACE signal (membership-weighted)
- Effective weight = global + overlay@E (computed at read-time)

Designer: Felix "Ironhand" - 2025-10-25
Reference: Nicolas's Priority 4 architecture guide
"""

import numpy as np
from scipy.stats import rankdata, norm
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WeightUpdate:
    """Result of weight learning update with entity attribution."""
    item_id: str
    item_type: str  # node type or link type
    scope: str

    # EMA updates
    ema_trace_seats_new: float
    ema_formation_quality_new: Optional[float]

    # Z-scores
    z_rein: float
    z_form: Optional[float]

    # Weight changes
    delta_log_weight_global: float
    log_weight_new: float

    # Entity-specific overlays
    local_overlays: List[Dict[str, Any]]  # [{"entity": "e1", "delta": 0.11}, ...]

    # Metadata
    cohort_size: int
    learning_rate: float


class WeightLearnerV2:
    """
    Entity-context-aware TRACE weight learning.

    Implements dual-view architecture:
    - 20% of signal → global weight (cross-entity learning)
    - 80% of signal → entity overlays (context-specific learning)

    Membership weights modulate local reinforcement strength.
    """

    def __init__(
        self,
        alpha: float = 0.1,
        min_cohort_size: int = 3,
        alpha_local: float = 0.8,
        alpha_global: float = 0.2,
        overlay_cap: float = 2.0
    ):
        """
        Initialize weight learner with entity context support.

        Args:
            alpha: EMA decay rate (default 0.1 = recent 10 TRACEs)
            min_cohort_size: Minimum cohort size for z-score computation
            alpha_local: Fraction of signal to entity overlays (default 0.8)
            alpha_global: Fraction of signal to global weight (default 0.2)
            overlay_cap: Maximum absolute overlay value (prevents runaway)
        """
        self.alpha = alpha
        self.min_cohort_size = min_cohort_size
        self.alpha_local = alpha_local
        self.alpha_global = alpha_global
        self.overlay_cap = overlay_cap

        # Cohort baselines for read-time standardization
        self.baselines = {}  # {(type, scope): (μ, σ)}

        logger.info(
            f"[WeightLearnerV2] Initialized with α={alpha}, "
            f"local={alpha_local:.1f}, global={alpha_global:.1f}"
        )

    def update_node_weights(
        self,
        nodes: List[Dict[str, Any]],
        reinforcement_seats: Dict[str, int],
        formations: List[Dict[str, Any]],
        entity_context: Optional[List[str]] = None
    ) -> List[WeightUpdate]:
        """
        Update node weights from TRACE signals with entity context.

        Args:
            nodes: Current node states from graph
            reinforcement_seats: {node_id: seats} from Hamilton apportionment
            formations: Node formations with quality metrics
            entity_context: Active entity IDs during this TRACE (from WM or explicit)

        Returns:
            List of WeightUpdate results with entity attribution
        """
        updates = []

        # Build cohorts by (type, scope)
        cohorts = self._build_cohorts(nodes)

        # Get membership weights for context entities
        membership_weights = self._get_membership_weights(nodes, entity_context or [])

        # Process reinforcement signals
        for node in nodes:
            node_id = node.get('name')
            if not node_id:
                continue

            # Get reinforcement seats (0 if not mentioned)
            delta_seats = reinforcement_seats.get(node_id, 0)

            # Get formation quality (None if not formed this TRACE)
            formation = next((f for f in formations if f['fields'].get('name') == node_id), None)
            formation_quality = formation['quality'] if formation else None

            # Update EMAs
            ema_trace_seats_old = float(node.get('ema_trace_seats') or 0.0)
            ema_formation_quality_old = float(node.get('ema_formation_quality') or 0.0)

            ema_trace_seats_new = self.alpha * delta_seats + (1 - self.alpha) * ema_trace_seats_old

            if formation_quality is not None:
                ema_formation_quality_new = self.alpha * formation_quality + (1 - self.alpha) * ema_formation_quality_old
            else:
                ema_formation_quality_new = ema_formation_quality_old

            # Compute cohort z-scores
            node_type = node.get('node_type', 'unknown')
            scope = node.get('scope', 'personal')
            cohort_key = (node_type, scope)

            z_rein, z_form, cohort_size = self._compute_z_scores(
                node_id,
                ema_trace_seats_new,
                ema_formation_quality_new if formation_quality is not None else None,
                cohorts.get(cohort_key, [])
            )

            # Compute adaptive learning rate
            last_update_ts = node.get('last_update_timestamp')
            last_update = None
            if last_update_ts is not None:
                # Convert timestamp (milliseconds) to datetime
                last_update = datetime.fromtimestamp(last_update_ts / 1000)
            eta = self._compute_learning_rate(last_update)

            # Total signal strength
            z_total = z_rein + (z_form if z_form is not None else 0)

            # === DUAL-VIEW UPDATE (Priority 4) ===

            # 1. Global weight update (20% of signal)
            delta_log_weight_global = self.alpha_global * eta * z_total
            log_weight_old = float(node.get('log_weight') or 0.0)
            log_weight_new = log_weight_old + delta_log_weight_global

            # 2. Entity overlay updates (80% of signal, membership-weighted)
            local_overlays = []
            if entity_context and delta_seats != 0:
                for entity_id in entity_context:
                    # Get membership weight for this node-entity pair
                    membership_weight = membership_weights.get(node_id, {}).get(entity_id, 0.0)

                    if membership_weight > 0.0:
                        # Local delta scaled by membership
                        delta_overlay = self.alpha_local * eta * z_total * membership_weight

                        # Clamp overlay to prevent runaway
                        overlay_old = node.get('log_weight_overlays', {}).get(entity_id, 0.0)
                        overlay_new = np.clip(
                            overlay_old + delta_overlay,
                            -self.overlay_cap,
                            self.overlay_cap
                        )

                        local_overlays.append({
                            "entity": entity_id,
                            "delta": float(delta_overlay),
                            "overlay_before": float(overlay_old),
                            "overlay_after": float(overlay_new),
                            "membership_weight": float(membership_weight)
                        })

            # Create update result
            update = WeightUpdate(
                item_id=node_id,
                item_type=node_type,
                scope=scope,
                ema_trace_seats_new=ema_trace_seats_new,
                ema_formation_quality_new=ema_formation_quality_new,
                z_rein=z_rein,
                z_form=z_form,
                delta_log_weight_global=delta_log_weight_global,
                log_weight_new=log_weight_new,
                local_overlays=local_overlays,
                cohort_size=cohort_size,
                learning_rate=eta
            )

            updates.append(update)

            # Logging
            if local_overlays:
                overlays_str = ", ".join([f"{o['entity']}: {o['delta']:+.3f}" for o in local_overlays])
                logger.debug(
                    f"[WeightLearnerV2] Node {node_id}: "
                    f"global={delta_log_weight_global:+.3f}, "
                    f"overlays=[{overlays_str}]"
                )

        logger.info(f"[WeightLearnerV2] Updated {len(updates)} node weights with entity context")
        return updates

    def _get_membership_weights(
        self,
        nodes: List[Dict[str, Any]],
        entity_context: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Extract membership weights for nodes in entity context.

        Args:
            nodes: Node states
            entity_context: Active entity IDs

        Returns:
            Dict[node_id, Dict[entity_id, membership_weight]]
        """
        membership_weights = {}

        for node in nodes:
            node_id = node.get('name')
            if not node_id:
                continue

            # Get BELONGS_TO memberships from node
            # (Assumes memberships stored in node.properties or similar)
            # TODO: Get from graph.get_links_by_type(BELONGS_TO) filtered by node_id
            memberships = node.get('memberships', {})  # {entity_id: weight}

            # Filter to active entity context
            context_memberships = {
                entity_id: weight
                for entity_id, weight in memberships.items()
                if entity_id in entity_context and weight > 0.0
            }

            if context_memberships:
                membership_weights[node_id] = context_memberships

        return membership_weights

    def _build_cohorts(self, items: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict]]:
        """Group items by (type, scope) for rank-z normalization."""
        cohorts = {}
        for item in items:
            item_type = item.get('node_type') or item.get('link_type', 'unknown')
            scope = item.get('scope', 'personal')
            key = (item_type, scope)

            if key not in cohorts:
                cohorts[key] = []
            cohorts[key].append(item)

        return cohorts

    def _compute_z_scores(
        self,
        item_id: str,
        ema_trace: float,
        ema_quality: Optional[float],
        cohort: List[Dict]
    ) -> Tuple[float, Optional[float], int]:
        """Compute rank-based z-scores within cohort."""
        if len(cohort) < self.min_cohort_size:
            # Fallback: use raw EMAs as z-scores
            z_rein = ema_trace / 10.0  # Normalize roughly
            z_form = (ema_quality / 1.0) if ema_quality is not None else None
            return z_rein, z_form, len(cohort)

        # Extract EMAs for cohort
        trace_values = [float(item.get('ema_trace_seats', 0.0)) for item in cohort]
        quality_values = [float(item.get('ema_formation_quality', 0.0)) for item in cohort] if ema_quality is not None else None

        # Rank-based z-scores (van der Waerden)
        ranks_trace = rankdata(trace_values, method='average')
        z_rein = norm.ppf(ranks_trace / (len(trace_values) + 1))

        # Find this item's position
        item_idx = next((i for i, item in enumerate(cohort) if item.get('name') == item_id), 0)
        z_rein_item = z_rein[item_idx]

        z_form_item = None
        if ema_quality is not None and quality_values:
            ranks_quality = rankdata(quality_values, method='average')
            z_form = norm.ppf(ranks_quality / (len(quality_values) + 1))
            z_form_item = z_form[item_idx]

        return float(z_rein_item), float(z_form_item) if z_form_item is not None else None, len(cohort)

    def _compute_learning_rate(self, last_update: Optional[datetime]) -> float:
        """Adaptive learning rate: η = 1 - exp(-Δt / τ)"""
        if last_update is None:
            return 1.0  # First update

        delta_t = (datetime.now() - last_update).total_seconds()
        tau = 86400.0  # 1 day half-life
        eta = 1.0 - np.exp(-delta_t / tau)
        return float(np.clip(eta, 0.01, 1.0))

    # Similar update_link_weights() method would follow same pattern
    # (Omitted for brevity - same dual-view logic applies)
