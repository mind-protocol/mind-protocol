"""
Vector-Weighted Membership - Multi-Causal Membership Structure

Implements multi-dimensional MEMBER_OF edges matching neuroscience evidence:
- w_semantic: Embedding/propositional fit (cortical prediction networks)
- w_intent: Goal/utility alignment (basal ganglia gating)
- w_affect: Arousal/valence modulation (LC/NE neuromodulation)
- w_experience: Usage/consolidation strength (hippocampal trace)

Key principles:
- Membership is multi-causal (semantics × intent × affect × experience)
- Stored weights are POTENTIAL membership (stable)
- Effective weights are STATE-DEPENDENT (computed at runtime)
- Composite weight: w_total = (sem × int × aff × exp)^0.25

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence.md §Principle 7
"""

import time
import math
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class VectorWeight:
    """
    Multi-dimensional membership weight for MEMBER_OF edges.

    Represents POTENTIAL membership (stored, stable).
    Actual membership computed at runtime via effective_weight().
    """
    w_semantic: float      # Embedding/propositional fit (0-1)
    w_intent: float        # Goal/utility alignment (0-1)
    w_affect: float        # Arousal/valence modulation (0-1)
    w_experience: float    # Usage/consolidation strength (0-1)
    w_total: float         # Composite = (sem × int × aff × exp)^0.25

    formation_context: str = ""          # When/why this membership formed
    last_coactivation: float = field(default_factory=time.time)  # Timestamp

    def __post_init__(self):
        """Ensure w_total is computed correctly."""
        self.w_total = self.compute_composite()

    def compute_composite(self) -> float:
        """
        Compute composite weight from four dimensions.

        Uses geometric mean (4th root of product) to ensure:
        - Weakness in ANY dimension reduces overall membership
        - Balanced contribution from all dimensions
        - Range-preserving (0-1 → 0-1)
        """
        product = self.w_semantic * self.w_intent * self.w_affect * self.w_experience
        return float(product ** 0.25)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            'w_semantic': round(self.w_semantic, 4),
            'w_intent': round(self.w_intent, 4),
            'w_affect': round(self.w_affect, 4),
            'w_experience': round(self.w_experience, 4),
            'w_total': round(self.w_total, 4),
            'formation_context': self.formation_context,
            'last_coactivation': self.last_coactivation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorWeight':
        """Deserialize from dictionary."""
        return cls(
            w_semantic=float(data['w_semantic']),
            w_intent=float(data['w_intent']),
            w_affect=float(data['w_affect']),
            w_experience=float(data['w_experience']),
            w_total=float(data['w_total']),
            formation_context=data.get('formation_context', ''),
            last_coactivation=float(data.get('last_coactivation', time.time()))
        )

    @classmethod
    def weak_prior(cls, formation_context: str = "emergence") -> 'VectorWeight':
        """
        Create weak prior weights for new membership.

        Start with balanced uncertainty (0.5 each dimension).
        Will drift toward reality through co-activation learning.
        """
        return cls(
            w_semantic=0.5,
            w_intent=0.5,
            w_affect=0.5,
            w_experience=0.3,  # Start lower - not yet consolidated
            w_total=0.0,  # Will be computed in __post_init__
            formation_context=formation_context
        )

    def update_dimension(self, dimension: str, new_value: float):
        """
        Update one dimension and recompute composite.

        Args:
            dimension: "semantic", "intent", "affect", or "experience"
            new_value: New weight value (0-1)
        """
        new_value = max(0.0, min(1.0, new_value))  # Clamp to [0,1]

        if dimension == "semantic":
            self.w_semantic = new_value
        elif dimension == "intent":
            self.w_intent = new_value
        elif dimension == "affect":
            self.w_affect = new_value
        elif dimension == "experience":
            self.w_experience = new_value
        else:
            raise ValueError(f"Unknown dimension: {dimension}")

        # Recompute composite
        self.w_total = self.compute_composite()
        self.last_coactivation = time.time()


@dataclass
class RuntimeContext:
    """
    Current system state for effective weight computation.

    State-dependent modulation factors:
    - arousal: Global activation level (LC/NE proxy)
    - current_goal: Active goal embedding
    - prediction_error_precision: Confidence in predictions
    """
    arousal: float = 0.5                           # 0-1, global activation
    current_goal: Optional[np.ndarray] = None      # Goal embedding vector
    prediction_error_precision: float = 0.7        # 0-1, prediction confidence

    # Optional context
    citizen_id: str = "default"
    frame_id: int = 0
    timestamp: float = field(default_factory=time.time)


class VectorWeightedMembership:
    """
    Manager for vector-weighted MEMBER_OF edges.

    Handles:
    - Weight storage and updates
    - Effective weight computation (state-dependent)
    - Multi-dimensional weight learning
    """

    def __init__(self):
        # Storage: (subentity_id, node_id) -> VectorWeight
        self.weights: Dict[tuple, VectorWeight] = {}

        # Telemetry
        self.effective_weight_computations: int = 0
        self.weight_updates: int = 0

    def add_membership(
        self,
        subentity_id: str,
        node_id: str,
        weight: Optional[VectorWeight] = None,
        formation_context: str = "emergence"
    ):
        """
        Add or update MEMBER_OF edge with vector weight.

        Args:
            subentity_id: SubEntity ID
            node_id: Node ID
            weight: VectorWeight (if None, use weak prior)
            formation_context: Why this membership formed
        """
        if weight is None:
            weight = VectorWeight.weak_prior(formation_context)

        self.weights[(subentity_id, node_id)] = weight
        self.weight_updates += 1

    def get_weight(self, subentity_id: str, node_id: str) -> Optional[VectorWeight]:
        """Get stored vector weight for membership."""
        return self.weights.get((subentity_id, node_id))

    def has_membership(self, subentity_id: str, node_id: str) -> bool:
        """Check if MEMBER_OF edge exists."""
        return (subentity_id, node_id) in self.weights

    def get_members(self, subentity_id: str) -> List[str]:
        """Get all node IDs that are members of SubEntity."""
        return [
            node_id for (se_id, node_id) in self.weights.keys()
            if se_id == subentity_id
        ]

    def compute_effective_weight(
        self,
        subentity_id: str,
        node_id: str,
        context: RuntimeContext,
        subentity_intent: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute effective (state-dependent) membership weight.

        Stored weights = POTENTIAL membership (stable).
        Effective weight = STATE-DEPENDENT (computed at runtime).

        State modulation:
        - High arousal → amplify w_affect (emotional links)
        - Active goal → modulate w_intent (task-aligned SubEntities)
        - High prediction error → reduce w_semantic (novelty drives activation)

        Args:
            subentity_id: SubEntity ID
            node_id: Node ID
            context: Current runtime state
            subentity_intent: Optional intent embedding for SubEntity

        Returns:
            Effective weight (0-1) modulated by current state
        """
        # Get stored weight (potential membership)
        stored_weight = self.get_weight(subentity_id, node_id)
        if stored_weight is None:
            return 0.0

        # Base weights from edge (learned, stable)
        w_sem = stored_weight.w_semantic
        w_int = stored_weight.w_intent
        w_aff = stored_weight.w_affect
        w_exp = stored_weight.w_experience

        # State-dependent modulation
        arousal = context.arousal
        precision = context.prediction_error_precision

        # Modulate semantic weight by prediction precision
        # High prediction error → lower semantic weight (novelty drives activation)
        w_eff_sem = w_sem * precision

        # Modulate intent weight by goal alignment
        w_eff_int = w_int
        if context.current_goal is not None and subentity_intent is not None:
            # Cosine similarity between current goal and SubEntity intent
            goal_alignment = float(np.dot(context.current_goal, subentity_intent) /
                                  (np.linalg.norm(context.current_goal) * np.linalg.norm(subentity_intent)))
            goal_alignment = max(0.0, goal_alignment)  # Clamp negative to 0
            w_eff_int = w_int * goal_alignment

        # Modulate affect weight by arousal
        # High arousal → amplify emotional links (arousal-biased competition)
        w_eff_aff = w_aff * arousal

        # Experience weight relatively stable
        w_eff_exp = w_exp

        # Composite effective weight (geometric mean)
        product = w_eff_sem * w_eff_int * w_eff_aff * w_eff_exp
        effective_weight = float(product ** 0.25)

        self.effective_weight_computations += 1

        return effective_weight

    def update_dimension_for_member(
        self,
        subentity_id: str,
        node_id: str,
        dimension: str,
        new_value: float
    ):
        """
        Update one dimension of membership weight.

        Used by learning mechanisms to refine weights based on observation.
        """
        weight = self.get_weight(subentity_id, node_id)
        if weight is None:
            return

        weight.update_dimension(dimension, new_value)
        self.weight_updates += 1

    def get_effective_members(
        self,
        subentity_id: str,
        context: RuntimeContext,
        subentity_intent: Optional[np.ndarray] = None,
        min_effective_weight: float = 0.3
    ) -> List[tuple[str, float]]:
        """
        Get members with effective weight above threshold.

        Returns:
            List of (node_id, effective_weight) tuples
        """
        members = []
        for node_id in self.get_members(subentity_id):
            eff_weight = self.compute_effective_weight(
                subentity_id, node_id, context, subentity_intent
            )
            if eff_weight >= min_effective_weight:
                members.append((node_id, eff_weight))

        return sorted(members, key=lambda x: x[1], reverse=True)

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring."""
        return {
            'total_memberships': len(self.weights),
            'effective_weight_computations': self.effective_weight_computations,
            'weight_updates': self.weight_updates,
            'unique_subentities': len(set(se_id for se_id, _ in self.weights.keys())),
            'unique_nodes': len(set(node_id for _, node_id in self.weights.keys()))
        }
