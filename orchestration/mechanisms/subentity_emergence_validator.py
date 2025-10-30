"""
SubEntity Emergence Validator - Engine-Side Validation

Validates emergence proposals and makes spawn/redirect/reject decisions.

Key Principle: Engine has authority over substrate physics.
Validator recomputes features from substrate, applies adaptive gates,
and makes final decision independently from proposal.

Decisions:
- SPAWN: Create new SubEntity
- REDIRECT: Route to existing SubEntity
- REJECT: Gap not suitable for emergence

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §4.1
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from orchestration.mechanisms.subentity_coalition_assembler import Coalition
from orchestration.mechanisms.quantile_gate import (
    QuantileGate, QuantileConfig, QuantileGateSet,
    ComparisonMode, GateStatus
)


class EmergenceDecision(str, Enum):
    """Emergence validation decision"""
    SPAWN = "spawn"          # Create new SubEntity
    REDIRECT = "redirect"    # Route to existing SubEntity
    REJECT = "reject"        # Reject emergence proposal


@dataclass
class ValidationResult:
    """Result of emergence validation"""
    decision: EmergenceDecision
    coalition: Coalition
    reason: str                                  # Why this decision was made
    gate_results: Dict[str, Any]                # All gate evaluation results
    redirect_target: Optional[str] = None       # If REDIRECT, which SubEntity
    spawn_bundle: Optional[Dict[str, Any]] = None  # If SPAWN, identity bundle
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergenceValidatorConfig:
    """Configuration for emergence validation"""
    # Quality gates (all must pass for SPAWN)
    min_coalition_density: float = 0.60          # Q70 typically
    min_coalition_coherence: float = 0.50        # Q60 typically
    min_coalition_size: int = 5
    max_coalition_size: int = 40

    # Novelty gate (must differ from existing SubEntities)
    min_novelty_distance: float = 0.30           # Cosine distance to nearest SubEntity

    # Redirect thresholds
    redirect_similarity_threshold: float = 0.75  # If > this, redirect instead of spawn

    # Gate configuration
    min_samples_for_gates: int = 30
    history_window: int = 1000

    # Feature recomputation (engine-side)
    recompute_density: bool = True
    recompute_coherence: bool = True
    recompute_novelty: bool = True


class SubEntityEmergenceValidator:
    """
    Engine-side validator for emergence proposals.

    Maintains substrate physics authority by:
    1. Recomputing features from substrate (not trusting proposal)
    2. Applying learned quantile gates
    3. Making independent spawn/redirect/reject decision

    Integration: Receives proposals from membrane bus, emits decisions
    """

    def __init__(self, config: Optional[EmergenceValidatorConfig] = None):
        self.config = config or EmergenceValidatorConfig()

        # Initialize quantile gates
        self.gates = QuantileGateSet()

        # Density gate: must exceed Q60
        self.gates.create_gate(
            metric_name="coalition_density",
            quantile_level=0.60,
            comparison_mode=ComparisonMode.ABOVE,
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        )

        # Coherence gate: must exceed Q50
        self.gates.create_gate(
            metric_name="coalition_coherence",
            quantile_level=0.50,
            comparison_mode=ComparisonMode.ABOVE,
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        )

        # Novelty gate: must exceed Q40 (not too similar to existing)
        self.gates.create_gate(
            metric_name="novelty_distance",
            quantile_level=0.40,
            comparison_mode=ComparisonMode.ABOVE,
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        )

        # Size gate: must be in normal range Q20-Q80
        self.gates.create_gate(
            metric_name="coalition_size",
            quantile_level=0.20,
            quantile_level_high=0.80,
            comparison_mode=ComparisonMode.BETWEEN,
            min_samples=self.config.min_samples_for_gates,
            window_size=self.config.history_window
        )

        # Telemetry
        self.decisions_made: Dict[EmergenceDecision, int] = {
            EmergenceDecision.SPAWN: 0,
            EmergenceDecision.REDIRECT: 0,
            EmergenceDecision.REJECT: 0
        }

    def validate_emergence(
        self,
        coalition: Coalition,
        graph_accessor,
        existing_subentities: Optional[List[Dict[str, Any]]] = None
    ) -> ValidationResult:
        """
        Validate emergence proposal and make decision.

        Args:
            coalition: Proposed node coalition
            graph_accessor: Access to graph substrate
            existing_subentities: List of existing SubEntities for novelty check

        Returns:
            ValidationResult with decision (SPAWN/REDIRECT/REJECT)
        """
        # Step 1: Recompute features from substrate (engine authority)
        features = self._recompute_features(coalition, graph_accessor, existing_subentities)

        # Step 2: Evaluate against gates
        gate_results = self.gates.evaluate_all(features)

        # Step 3: Check size bounds (hard constraints)
        if len(coalition.nodes) < self.config.min_coalition_size:
            self.decisions_made[EmergenceDecision.REJECT] += 1
            return ValidationResult(
                decision=EmergenceDecision.REJECT,
                coalition=coalition,
                reason=f"Coalition too small: {len(coalition.nodes)} < {self.config.min_coalition_size}",
                gate_results=gate_results
            )

        if len(coalition.nodes) > self.config.max_coalition_size:
            self.decisions_made[EmergenceDecision.REJECT] += 1
            return ValidationResult(
                decision=EmergenceDecision.REJECT,
                coalition=coalition,
                reason=f"Coalition too large: {len(coalition.nodes)} > {self.config.max_coalition_size}",
                gate_results=gate_results
            )

        # Step 4: Check quality gates
        failed_gates = self.gates.get_failed_gates(features)

        if failed_gates:
            # Record metrics for learning (even when rejected)
            self.gates.record_all(features)

            self.decisions_made[EmergenceDecision.REJECT] += 1
            return ValidationResult(
                decision=EmergenceDecision.REJECT,
                coalition=coalition,
                reason=f"Failed quality gates: {', '.join(failed_gates)}",
                gate_results=gate_results,
                metadata={'failed_gates': failed_gates}
            )

        # Step 5: Check novelty - should we redirect instead of spawn?
        if features.get('novelty_distance') is not None:
            novelty = features['novelty_distance']

            # If very similar to existing SubEntity, redirect
            if novelty < (1.0 - self.config.redirect_similarity_threshold):
                nearest_subentity = features.get('nearest_subentity_id')

                # Record metrics
                self.gates.record_all(features)

                self.decisions_made[EmergenceDecision.REDIRECT] += 1
                return ValidationResult(
                    decision=EmergenceDecision.REDIRECT,
                    coalition=coalition,
                    reason=f"Too similar to existing SubEntity (novelty={novelty:.3f})",
                    gate_results=gate_results,
                    redirect_target=nearest_subentity,
                    metadata={'novelty_distance': novelty}
                )

        # Step 6: All gates passed - SPAWN decision
        # Record successful metrics for gate learning
        self.gates.record_all(features)

        self.decisions_made[EmergenceDecision.SPAWN] += 1
        return ValidationResult(
            decision=EmergenceDecision.SPAWN,
            coalition=coalition,
            reason="All quality gates passed",
            gate_results=gate_results,
            metadata={
                'features': features,
                'gate_summary': self.gates.get_summary(features)
            }
        )

    def _recompute_features(
        self,
        coalition: Coalition,
        graph_accessor,
        existing_subentities: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, float]:
        """
        Recompute coalition features from substrate.

        Engine recomputes to maintain authority over physics.
        Does not trust proposal's claimed features.
        """
        features = {}

        # Feature 1: Density (if enabled)
        if self.config.recompute_density:
            density = self._compute_density(coalition, graph_accessor)
            features['coalition_density'] = density
        else:
            features['coalition_density'] = coalition.density

        # Feature 2: Coherence (if enabled)
        if self.config.recompute_coherence:
            coherence = self._compute_coherence(coalition, graph_accessor)
            features['coalition_coherence'] = coherence
        else:
            features['coalition_coherence'] = coalition.coherence

        # Feature 3: Size
        features['coalition_size'] = float(len(coalition.nodes))

        # Feature 4: Novelty (if enabled and existing SubEntities provided)
        if self.config.recompute_novelty and existing_subentities:
            novelty, nearest_id = self._compute_novelty(coalition, existing_subentities, graph_accessor)
            features['novelty_distance'] = novelty
            features['nearest_subentity_id'] = nearest_id

        return features

    def _compute_density(
        self,
        coalition: Coalition,
        graph_accessor
    ) -> float:
        """
        Recompute coalition density from substrate.

        Density = actual_edges / max_possible_edges
        """
        if len(coalition.nodes) < 2:
            return 0.0

        node_ids = [n.node_id for n in coalition.nodes]
        actual_edges = 0

        for i, node_id_1 in enumerate(node_ids):
            for node_id_2 in node_ids[i+1:]:
                try:
                    edge = graph_accessor.get_edge(node_id_1, node_id_2)
                    if edge:
                        actual_edges += 1
                except Exception:
                    continue

        max_edges = (len(node_ids) * (len(node_ids) - 1)) / 2
        density = actual_edges / max_edges if max_edges > 0 else 0.0

        return float(density)

    def _compute_coherence(
        self,
        coalition: Coalition,
        graph_accessor
    ) -> float:
        """
        Recompute coalition coherence from substrate.

        For now: Simple heuristic based on node type diversity
        Future: Embedding-based semantic coherence
        """
        if not coalition.nodes:
            return 0.0

        # Count unique node types
        node_types = set()
        for node in coalition.nodes:
            node_type = node.properties.get('type') or node.properties.get('labels', [None])[0]
            if node_type:
                node_types.add(node_type)

        # Coherence inversely related to type diversity
        type_diversity = len(node_types) / len(coalition.nodes) if coalition.nodes else 1.0
        coherence = 1.0 - type_diversity

        return float(coherence)

    def _compute_novelty(
        self,
        coalition: Coalition,
        existing_subentities: List[Dict[str, Any]],
        graph_accessor
    ) -> Tuple[float, Optional[str]]:
        """
        Compute novelty: how different is coalition from existing SubEntities?

        Returns:
            (novelty_distance, nearest_subentity_id)
            novelty_distance = 1.0 - max_similarity (higher = more novel)
        """
        if not existing_subentities:
            return 1.0, None  # Maximally novel if no existing SubEntities

        # Get coalition node IDs
        coalition_node_ids = set(n.node_id for n in coalition.nodes)

        # Compute Jaccard similarity to each existing SubEntity
        max_similarity = 0.0
        nearest_subentity_id = None

        for subentity in existing_subentities:
            # Get SubEntity members
            subentity_id = subentity.get('id')
            subentity_members = set(subentity.get('member_ids', []))

            if not subentity_members:
                continue

            # Jaccard similarity
            intersection = len(coalition_node_ids & subentity_members)
            union = len(coalition_node_ids | subentity_members)
            similarity = intersection / union if union > 0 else 0.0

            if similarity > max_similarity:
                max_similarity = similarity
                nearest_subentity_id = subentity_id

        novelty_distance = 1.0 - max_similarity
        return float(novelty_distance), nearest_subentity_id

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring"""
        total_decisions = sum(self.decisions_made.values())

        return {
            'decisions': dict(self.decisions_made),
            'total_decisions': total_decisions,
            'spawn_rate': self.decisions_made[EmergenceDecision.SPAWN] / total_decisions
                if total_decisions > 0 else 0.0,
            'redirect_rate': self.decisions_made[EmergenceDecision.REDIRECT] / total_decisions
                if total_decisions > 0 else 0.0,
            'reject_rate': self.decisions_made[EmergenceDecision.REJECT] / total_decisions
                if total_decisions > 0 else 0.0,
            'gates': self.gates.get_all_stats()
        }
