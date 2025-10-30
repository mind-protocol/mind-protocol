"""
SubEntity Membership Weight Learner - Continuous Membership Refinement

Learns membership boundaries through co-activation observation:
- Tracks which nodes consistently co-activate with SubEntity
- Prunes weak members (low co-activation)
- Admits strong non-members (high co-activation)

Integrates with schema_map.py weighted membership for health metrics.

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §4.3
"""

import time
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

from orchestration.mechanisms.quantile_gate import QuantileGate, QuantileConfig, ComparisonMode


@dataclass
class MembershipObservation:
    """Record of node co-activation with SubEntity"""
    node_id: str
    subentity_id: str
    timestamp: float
    co_activation_strength: float       # 0-1, how strongly activated together
    energy_correlation: float           # Correlation of energy levels


@dataclass
class MembershipAdjustment:
    """Proposed membership change"""
    subentity_id: str
    node_id: str
    action: str                         # "prune" or "admit"
    reason: str
    current_weight: float
    proposed_weight: float
    confidence: float                   # 0-1
    timestamp: float = field(default_factory=time.time)


@dataclass
class MembershipLearnerConfig:
    """Configuration for membership learning"""
    # Observation window
    observation_window_frames: int = 1000   # How many frames to track

    # Co-activation thresholds
    min_coactivation_for_admit: float = 0.70   # Q70 of co-activation distribution
    max_coactivation_for_prune: float = 0.30   # Q30 of co-activation distribution

    # Learning rate
    weight_update_rate: float = 0.1            # How fast to adjust weights

    # Adjustment thresholds
    min_observations: int = 30                 # Need this many observations before adjusting
    adjustment_cooldown_frames: int = 100      # Wait this long between adjustments

    # Gate configuration
    min_samples_for_gates: int = 50
    history_window: int = 2000


class SubEntityMembershipWeightLearner:
    """
    Learns and refines SubEntity membership boundaries.

    Observes co-activation patterns and proposes membership adjustments:
    - Prune: Remove nodes with weak co-activation
    - Admit: Add nodes with strong co-activation

    Integration:
    - Called every frame in consciousness_engine_v2.py (after energy apply)
    - Emits membership.adjust events via membrane bus
    - Connects to schema_map.py for health metrics integration
    """

    def __init__(self, config: Optional[MembershipLearnerConfig] = None):
        self.config = config or MembershipLearnerConfig()

        # Track co-activation history
        # subentity_id -> node_id -> [observations]
        self.coactivation_history: Dict[str, Dict[str, List[MembershipObservation]]] = defaultdict(lambda: defaultdict(list))

        # Track when last adjustment was made (for cooldown)
        # subentity_id -> node_id -> last_adjustment_frame
        self.last_adjustment: Dict[str, Dict[str, int]] = defaultdict(dict)

        # Current frame counter
        self.current_frame: int = 0

        # Quantile gates for adaptive thresholds
        self.admit_gate = QuantileGate(QuantileConfig(
            metric_name="coactivation_strength",
            quantile_level=0.70,
            comparison_mode=ComparisonMode.ABOVE,  # Must exceed Q70 to admit
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        self.prune_gate = QuantileGate(QuantileConfig(
            metric_name="coactivation_strength",
            quantile_level=0.30,
            comparison_mode=ComparisonMode.BELOW,  # Must be below Q30 to prune
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        ))

        # Telemetry
        self.observations_recorded: int = 0
        self.adjustments_proposed: Dict[str, int] = {
            'prune': 0,
            'admit': 0
        }

    def observe_frame(
        self,
        frame_state: Dict[str, Any]
    ) -> List[MembershipAdjustment]:
        """
        Observe current frame and propose membership adjustments.

        Args:
            frame_state: Current consciousness frame with:
                - subentities: Dict[subentity_id, {energy, active_nodes}]
                - nodes: Dict[node_id, {energy, activation}]

        Returns:
            List of proposed membership adjustments
        """
        self.current_frame += 1

        # Record observations for this frame
        self._record_observations(frame_state)

        # Propose adjustments based on accumulated observations
        adjustments = self._propose_adjustments(frame_state)

        return adjustments

    def _record_observations(
        self,
        frame_state: Dict[str, Any]
    ):
        """Record co-activation observations for current frame"""
        subentities = frame_state.get('subentities', {})
        nodes = frame_state.get('nodes', {})

        for subentity_id, subentity_state in subentities.items():
            subentity_energy = subentity_state.get('energy', 0.0)
            subentity_active = subentity_energy > 0.5  # Threshold for "active"

            if not subentity_active:
                continue  # Skip inactive SubEntities

            # Get member nodes
            member_node_ids = set(subentity_state.get('member_nodes', []))

            # Get all nodes in frame
            for node_id, node_state in nodes.items():
                node_energy = node_state.get('energy', 0.0)
                node_active = node_energy > 0.5

                # Compute co-activation strength
                if subentity_active and node_active:
                    # Both active - strong co-activation
                    coactivation_strength = min(subentity_energy, node_energy)
                else:
                    # Not co-active
                    coactivation_strength = 0.0

                # Compute energy correlation (how similar are energy levels?)
                energy_correlation = 1.0 - abs(subentity_energy - node_energy)

                # Record observation
                observation = MembershipObservation(
                    node_id=node_id,
                    subentity_id=subentity_id,
                    timestamp=time.time(),
                    co_activation_strength=coactivation_strength,
                    energy_correlation=energy_correlation
                )

                self.coactivation_history[subentity_id][node_id].append(observation)

                # Trim history to window size
                history = self.coactivation_history[subentity_id][node_id]
                if len(history) > self.config.observation_window_frames:
                    self.coactivation_history[subentity_id][node_id] = history[-self.config.observation_window_frames:]

                self.observations_recorded += 1

    def _propose_adjustments(
        self,
        frame_state: Dict[str, Any]
    ) -> List[MembershipAdjustment]:
        """Propose membership adjustments based on observation history"""
        adjustments = []
        subentities = frame_state.get('subentities', {})

        for subentity_id, subentity_state in subentities.items():
            current_members = set(subentity_state.get('member_nodes', []))

            # Check each node's co-activation history
            for node_id, observations in self.coactivation_history[subentity_id].items():
                if len(observations) < self.config.min_observations:
                    continue  # Not enough history

                # Check cooldown
                last_adj_frame = self.last_adjustment[subentity_id].get(node_id, 0)
                if self.current_frame - last_adj_frame < self.config.adjustment_cooldown_frames:
                    continue  # Still in cooldown

                # Compute average co-activation
                coactivations = [obs.co_activation_strength for obs in observations]
                avg_coactivation = float(np.mean(coactivations))

                # Record for gate learning
                self.admit_gate.record(avg_coactivation)
                self.prune_gate.record(avg_coactivation)

                is_member = node_id in current_members

                # Case 1: Current member with weak co-activation → PRUNE
                if is_member:
                    prune_result = self.prune_gate.evaluate(avg_coactivation)
                    if prune_result.status.value == "pass":  # Below Q30 = weak
                        adjustment = MembershipAdjustment(
                            subentity_id=subentity_id,
                            node_id=node_id,
                            action="prune",
                            reason=f"Weak co-activation: {avg_coactivation:.3f} (Q30 gate passed)",
                            current_weight=1.0,  # Current member
                            proposed_weight=avg_coactivation,  # Lower weight
                            confidence=prune_result.percentile / 100 if prune_result.percentile else 0.5
                        )
                        adjustments.append(adjustment)
                        self.adjustments_proposed['prune'] += 1
                        self.last_adjustment[subentity_id][node_id] = self.current_frame

                # Case 2: Non-member with strong co-activation → ADMIT
                else:
                    admit_result = self.admit_gate.evaluate(avg_coactivation)
                    if admit_result.status.value == "pass":  # Above Q70 = strong
                        adjustment = MembershipAdjustment(
                            subentity_id=subentity_id,
                            node_id=node_id,
                            action="admit",
                            reason=f"Strong co-activation: {avg_coactivation:.3f} (Q70 gate passed)",
                            current_weight=0.0,  # Non-member
                            proposed_weight=avg_coactivation,  # Higher weight
                            confidence=admit_result.percentile / 100 if admit_result.percentile else 0.5
                        )
                        adjustments.append(adjustment)
                        self.adjustments_proposed['admit'] += 1
                        self.last_adjustment[subentity_id][node_id] = self.current_frame

        return adjustments

    def get_coactivation_stats(
        self,
        subentity_id: str,
        node_id: str
    ) -> Optional[Dict[str, float]]:
        """Get co-activation statistics for node-SubEntity pair"""
        observations = self.coactivation_history.get(subentity_id, {}).get(node_id, [])

        if not observations:
            return None

        coactivations = [obs.co_activation_strength for obs in observations]
        correlations = [obs.energy_correlation for obs in observations]

        return {
            'observation_count': len(observations),
            'mean_coactivation': float(np.mean(coactivations)),
            'std_coactivation': float(np.std(coactivations)),
            'mean_correlation': float(np.mean(correlations)),
            'recent_coactivation': coactivations[-10:] if len(coactivations) >= 10 else coactivations
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring"""
        return {
            'current_frame': self.current_frame,
            'observations_recorded': self.observations_recorded,
            'adjustments_proposed': dict(self.adjustments_proposed),
            'admit_gate': self.admit_gate.get_stats(),
            'prune_gate': self.prune_gate.get_stats(),
            'tracked_subentities': len(self.coactivation_history),
            'total_node_pairs': sum(len(nodes) for nodes in self.coactivation_history.values())
        }
