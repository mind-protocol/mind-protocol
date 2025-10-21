"""
Weight Learning - TRACE signals → persistent weight updates

Implements the four-stage learning pipeline:
1. Parser signals (ΔR seats, formation quality)
2. EMA updates (smooth noisy signals)
3. Cohort z-scores (rank-based normalization)
4. Weight updates (additive learning in log space)

Designer: Felix "Ironhand" - 2025-10-21
Reference: docs/specs/consciousness_engine_architecture/mechanisms/trace_weight_learning.md
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
    """Result of weight learning update for single item."""
    item_id: str
    item_type: str  # node type or link type
    scope: str

    # EMA updates
    ema_trace_seats_new: float
    ema_formation_quality_new: Optional[float]

    # Z-scores
    z_rein: float
    z_form: Optional[float]

    # Weight change
    delta_log_weight: float
    log_weight_new: float

    # Metadata
    cohort_size: int
    learning_rate: float


class WeightLearner:
    """
    Implements TRACE-driven weight learning.

    Maintains cohort statistics for rank-based z-score normalization
    and applies adaptive learning rates.
    """

    def __init__(self, alpha: float = 0.1, min_cohort_size: int = 3):
        """
        Initialize weight learner.

        Args:
            alpha: EMA decay rate (default 0.1 = recent 10 TRACEs)
            min_cohort_size: Minimum cohort size for z-score computation
        """
        self.alpha = alpha
        self.min_cohort_size = min_cohort_size

        # Cohort baselines for read-time standardization
        self.baselines = {}  # {(type, scope): (μ, σ)}

        logger.info(f"[WeightLearner] Initialized with α={alpha}, min_cohort={min_cohort_size}")

    def update_node_weights(
        self,
        nodes: List[Dict[str, Any]],
        reinforcement_seats: Dict[str, int],
        formations: List[Dict[str, Any]]
    ) -> List[WeightUpdate]:
        """
        Update node weights from TRACE signals.

        Args:
            nodes: Current node states from graph
            reinforcement_seats: {node_id: seats} from Hamilton apportionment
            formations: Node formations with quality metrics

        Returns:
            List of WeightUpdate results
        """
        updates = []

        # Build cohorts by (type, scope)
        cohorts = self._build_cohorts(nodes)

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
            # CRITICAL: Convert to float to handle FalkorDB string/None returns
            ema_trace_seats_old = float(node.get('ema_trace_seats') or 0.0)
            ema_formation_quality_old = float(node.get('ema_formation_quality') or 0.0)

            # Reinforcement EMA update (always happens, even if delta=0)
            ema_trace_seats_new = self.alpha * delta_seats + (1 - self.alpha) * ema_trace_seats_old

            # Formation quality EMA update (only if formed)
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
            last_update = node.get('last_update_timestamp')
            eta = self._compute_learning_rate(last_update)

            # Weight update: Δ log_weight = η · (z_rein + z_form)
            # Note: z_R, z_F, z_wm come from traversal/WM, not TRACE
            z_total = z_rein + (z_form if z_form is not None else 0)
            delta_log_weight = eta * z_total

            # CRITICAL: Convert to float to handle FalkorDB string/None returns
            log_weight_old = float(node.get('log_weight') or 0.0)
            log_weight_new = log_weight_old + delta_log_weight

            # Create update result
            update = WeightUpdate(
                item_id=node_id,
                item_type=node_type,
                scope=scope,
                ema_trace_seats_new=ema_trace_seats_new,
                ema_formation_quality_new=ema_formation_quality_new if formation_quality is not None else ema_formation_quality_old,
                z_rein=z_rein,
                z_form=z_form,
                delta_log_weight=delta_log_weight,
                log_weight_new=log_weight_new,
                cohort_size=cohort_size,
                learning_rate=eta
            )

            updates.append(update)

            q_display = f"{formation_quality:.2f}" if formation_quality is not None else "N/A"
            z_form_display = f"{z_form:.2f}" if z_form is not None else "N/A"

            logger.debug(
                f"[WeightLearner] Node {node_id}: "
                f"ΔR={delta_seats}, z_rein={z_rein:.2f}, "
                f"q={q_display}, z_form={z_form_display}, "
                f"η={eta:.3f}, Δlog_weight={delta_log_weight:+.3f}"
            )

        logger.info(f"[WeightLearner] Updated {len(updates)} node weights")
        return updates

    def update_link_weights(
        self,
        links: List[Dict[str, Any]],
        reinforcement_seats: Dict[str, int],
        formations: List[Dict[str, Any]]
    ) -> List[WeightUpdate]:
        """
        Update link weights from TRACE signals.

        Args:
            links: Current link states from graph
            reinforcement_seats: {link_id: seats} from Hamilton apportionment
            formations: Link formations with quality metrics

        Returns:
            List of WeightUpdate results
        """
        updates = []

        # Build cohorts by (type, scope)
        cohorts = self._build_cohorts(links)

        # Process reinforcement signals
        for link in links:
            link_id = link.get('link_id') or link.get('name')
            if not link_id:
                continue

            # Get reinforcement seats (0 if not mentioned)
            delta_seats = reinforcement_seats.get(link_id, 0)

            # Get formation quality (None if not formed this TRACE)
            formation = next((f for f in formations if f.get('link_id') == link_id), None)
            formation_quality = formation.get('quality') if formation else None

            # Update EMAs
            # CRITICAL: Convert to float to handle FalkorDB string/None returns
            ema_trace_seats_old = float(link.get('ema_trace_seats') or 0.0)
            ema_formation_quality_old = float(link.get('ema_formation_quality') or 0.0)

            # Reinforcement EMA update
            ema_trace_seats_new = self.alpha * delta_seats + (1 - self.alpha) * ema_trace_seats_old

            # Formation quality EMA update (only if formed)
            if formation_quality is not None:
                ema_formation_quality_new = self.alpha * formation_quality + (1 - self.alpha) * ema_formation_quality_old
            else:
                ema_formation_quality_new = ema_formation_quality_old

            # Compute cohort z-scores
            link_type = link.get('link_type', 'unknown')
            scope = link.get('scope', 'organizational')
            cohort_key = (link_type, scope)

            z_rein, z_form, cohort_size = self._compute_z_scores(
                link_id,
                ema_trace_seats_new,
                ema_formation_quality_new if formation_quality is not None else None,
                cohorts.get(cohort_key, [])
            )

            # Compute adaptive learning rate
            last_update = link.get('last_update_timestamp')
            eta = self._compute_learning_rate(last_update)

            # Weight update: Δ log_weight = η · (z_rein + z_form)
            # Note: z_phi comes from traversal, not TRACE
            z_total = z_rein + (z_form if z_form is not None else 0)
            delta_log_weight = eta * z_total

            # CRITICAL: Convert to float to handle FalkorDB string/None returns
            log_weight_old = float(link.get('log_weight') or 0.0)
            log_weight_new = log_weight_old + delta_log_weight

            # Create update result
            update = WeightUpdate(
                item_id=link_id,
                item_type=link_type,
                scope=scope,
                ema_trace_seats_new=ema_trace_seats_new,
                ema_formation_quality_new=ema_formation_quality_new if formation_quality is not None else ema_formation_quality_old,
                z_rein=z_rein,
                z_form=z_form,
                delta_log_weight=delta_log_weight,
                log_weight_new=log_weight_new,
                cohort_size=cohort_size,
                learning_rate=eta
            )

            updates.append(update)

        logger.info(f"[WeightLearner] Updated {len(updates)} link weights")
        return updates

    def _build_cohorts(self, items: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict]]:
        """
        Build cohorts by (type, scope).

        Args:
            items: List of nodes or links

        Returns:
            Dict mapping (type, scope) to list of items in that cohort
        """
        cohorts = {}

        for item in items:
            item_type = item.get('node_type') or item.get('link_type', 'unknown')
            scope = item.get('scope', 'personal')
            cohort_key = (item_type, scope)

            if cohort_key not in cohorts:
                cohorts[cohort_key] = []

            cohorts[cohort_key].append(item)

        return cohorts

    def _compute_z_scores(
        self,
        item_id: str,
        ema_rein: float,
        ema_form: Optional[float],
        cohort: List[Dict[str, Any]]
    ) -> Tuple[float, Optional[float], int]:
        """
        Compute rank-based z-scores for reinforcement and formation.

        Uses van der Waerden rank-based z-score:
        z_i = Φ^(-1)(rank_i / (N+1))

        Args:
            item_id: Item being scored
            ema_rein: EMA of trace seats for this item
            ema_form: EMA of formation quality (None if not applicable)
            cohort: List of items in same (type, scope) cohort

        Returns:
            (z_rein, z_form, cohort_size)
        """
        cohort_size = len(cohort)

        # Need at least min_cohort_size for meaningful z-scores
        if cohort_size < self.min_cohort_size:
            logger.debug(f"[WeightLearner] Cohort too small ({cohort_size} < {self.min_cohort_size}), using raw EMAs")
            return ema_rein, ema_form, cohort_size

        # Extract EMA values from cohort
        # CRITICAL: Convert to float to handle FalkorDB string/None returns
        rein_values = [float(item.get('ema_trace_seats') or 0.0) for item in cohort]
        rein_values.append(ema_rein)  # Add current item

        # Compute ranks (1-based)
        ranks_rein = rankdata(rein_values, method='average')
        current_rank_rein = ranks_rein[-1]  # Last item is current

        # Van der Waerden z-score: Φ^(-1)(rank / (N+1))
        N = len(rein_values)
        z_rein = norm.ppf(current_rank_rein / (N + 1))

        # Formation quality z-score (if applicable)
        z_form = None
        if ema_form is not None:
            # CRITICAL: Convert to float to handle FalkorDB string/None returns
            form_values = [float(item.get('ema_formation_quality') or 0.0) for item in cohort]
            form_values.append(ema_form)

            ranks_form = rankdata(form_values, method='average')
            current_rank_form = ranks_form[-1]

            z_form = norm.ppf(current_rank_form / (len(form_values) + 1))

        z_form_display = f"{z_form:.2f}" if z_form is not None else "N/A"
        logger.debug(
            f"[WeightLearner] Item {item_id}: "
            f"cohort_size={cohort_size}, "
            f"rank_rein={current_rank_rein}/{N}, z_rein={z_rein:.2f}, "
            f"z_form={z_form_display}"
        )

        return z_rein, z_form, cohort_size

    def _compute_learning_rate(self, last_update: Optional[datetime]) -> float:
        """
        Compute adaptive learning rate η = 1 - exp(-Δt / τ̂).

        Args:
            last_update: Timestamp of last non-zero weight update

        Returns:
            Learning rate η ∈ [0, 1]
        """
        if last_update is None:
            # First update - use moderate learning rate
            return 0.15

        # Compute time since last update
        delta_t = (datetime.utcnow() - last_update).total_seconds()

        # Estimate τ̂ (typical inter-update interval)
        # For now, use fixed τ̂ = 1 hour = 3600 seconds
        # TODO: Learn τ̂ from actual inter-update intervals
        tau_hat = 3600.0

        # η = 1 - exp(-Δt / τ̂)
        eta = 1.0 - np.exp(-delta_t / tau_hat)

        # Clip to reasonable range
        eta = np.clip(eta, 0.01, 0.95)

        logger.debug(f"[WeightLearner] Δt={delta_t:.0f}s, τ̂={tau_hat:.0f}s, η={eta:.3f}")

        return eta

    def standardize_weight(
        self,
        log_weight: float,
        node_type: str,
        scope: str
    ) -> float:
        """
        Standardize log_weight for read-time comparisons.

        z_W = (log_weight - μ_T) / (σ_T + ε)

        Args:
            log_weight: Raw log weight
            node_type: Type for baseline lookup
            scope: Scope for baseline lookup

        Returns:
            Standardized weight z_W
        """
        cohort_key = (node_type, scope)

        if cohort_key not in self.baselines:
            # No baseline yet - return raw weight
            logger.debug(f"[WeightLearner] No baseline for {cohort_key}, using raw log_weight")
            return log_weight

        mu, sigma = self.baselines[cohort_key]
        epsilon = 1e-6

        z_W = (log_weight - mu) / (sigma + epsilon)

        return z_W

    def update_baselines(self, items: List[Dict[str, Any]]):
        """
        Update rolling baselines (μ_T, σ_T) for read-time standardization.

        Args:
            items: All nodes or links (to recompute baselines)
        """
        # Build cohorts
        cohorts = self._build_cohorts(items)

        # Compute μ and σ for each cohort
        for cohort_key, cohort_items in cohorts.items():
            if len(cohort_items) < 3:
                continue  # Need at least 3 items for meaningful statistics

            log_weights = [item.get('log_weight', 0.0) for item in cohort_items]

            mu = np.mean(log_weights)
            sigma = np.std(log_weights)

            self.baselines[cohort_key] = (mu, sigma)

            logger.debug(f"[WeightLearner] Baseline for {cohort_key}: μ={mu:.2f}, σ={sigma:.2f}")

        logger.info(f"[WeightLearner] Updated {len(self.baselines)} cohort baselines")
