"""
Metastability Tracker - Co-Activation Pattern Monitoring

Tracks persistent co-activation patterns WITHOUT creating Mode entities.
Follows spec: "Modes remain ephemeral views only" - no ontology, just metrics.

Metastability criterion: Coalition persists for sustained window (85%+ overlap).

Use cases:
- Telemetry/dashboard: "Currently in flow state" (derived label)
- Monitoring: Track stable coalitions for insight
- Decision point: IF we later need Mode detection, this provides evidence

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence.md §Appendix: Modes as Ephemeral Views
"""

import time
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from collections import deque
import numpy as np


@dataclass
class ActivationSnapshot:
    """Snapshot of SubEntity activation at one frame."""
    frame_id: int
    timestamp: float
    active_subentities: Set[str]           # SubEntities with E > threshold
    activation_scores: Dict[str, float]     # SubEntity ID → activation score
    dominant_subentity: Optional[str] = None  # Highest activation

    def __post_init__(self):
        """Compute dominant SubEntity if not provided."""
        if self.dominant_subentity is None and self.activation_scores:
            self.dominant_subentity = max(
                self.activation_scores.keys(),
                key=lambda k: self.activation_scores[k]
            )


@dataclass
class CoactivationPattern:
    """
    Ephemeral co-activation pattern (NOT persisted as entity).

    Tracks stability of SubEntity coalition over time.
    Used for telemetry/monitoring, not control.
    """
    coalition: Set[str]                    # SubEntity IDs in pattern
    first_detected_frame: int
    first_detected_timestamp: float
    duration_frames: int = 0
    stability_score: float = 0.0           # 0-1, how stable coalition is
    last_seen_frame: int = 0
    last_seen_timestamp: float = 0.0

    # Optional human-readable label (weak, derived)
    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for telemetry events."""
        return {
            'coalition': list(self.coalition),
            'first_detected_frame': self.first_detected_frame,
            'duration_frames': self.duration_frames,
            'stability_score': round(self.stability_score, 3),
            'label': self.label or "unlabeled"
        }


@dataclass
class MetastabilityConfig:
    """Configuration for metastability tracking."""
    window_size: int = 10                  # Frames to track for stability
    stability_threshold: float = 0.85      # Jaccard similarity threshold for "stable"
    min_duration: int = 5                  # Minimum frames to count as pattern
    max_tracked_patterns: int = 20         # Memory limit


class MetastabilityTracker:
    """
    Tracks co-activation patterns WITHOUT creating Mode entities.

    Analyzes recent activation patterns to identify metastable coalitions.
    Emits telemetry events, not graph nodes.
    """

    def __init__(self, config: Optional[MetastabilityConfig] = None):
        self.config = config or MetastabilityConfig()

        # Rolling window of activation snapshots
        self.history: deque[ActivationSnapshot] = deque(
            maxlen=self.config.window_size
        )

        # Currently tracked persistent patterns (ephemeral, not stored)
        self.tracked_patterns: List[CoactivationPattern] = []

        # Telemetry
        self.frames_observed: int = 0
        self.patterns_detected: int = 0

    def observe_frame(
        self,
        frame_id: int,
        active_subentities: Set[str],
        activation_scores: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Observe current frame and update pattern tracking.

        Args:
            frame_id: Current frame number
            active_subentities: Set of SubEntity IDs with E > threshold
            activation_scores: Dict of SubEntity ID → activation score

        Returns:
            Optional dict with detected pattern info (for telemetry)
        """
        self.frames_observed += 1

        # Create snapshot
        snapshot = ActivationSnapshot(
            frame_id=frame_id,
            timestamp=time.time(),
            active_subentities=active_subentities,
            activation_scores=activation_scores
        )

        # Add to history
        self.history.append(snapshot)

        # Analyze for persistent patterns (if we have enough history)
        if len(self.history) >= self.config.min_duration:
            return self._analyze_stability()

        return None

    def _analyze_stability(self) -> Optional[Dict[str, Any]]:
        """
        Analyze recent history for metastable coalitions.

        Metastability: Coalition persists for sustained window with high overlap.

        Returns:
            Pattern info if stable pattern detected, None otherwise
        """
        if len(self.history) < 2:
            return None

        # Get active sets from window
        active_sets = [snapshot.active_subentities for snapshot in self.history]

        # Check if coalition is stable (high overlap across window)
        stability = self._compute_stability(active_sets)

        if stability >= self.config.stability_threshold:
            # Stable coalition detected
            coalition = set.intersection(*active_sets)  # Common members

            if not coalition:
                # No common members - not a true coalition
                return None

            # Check if this is a new pattern or continuation
            pattern = self._find_or_create_pattern(coalition)

            # Update pattern
            pattern.duration_frames = len(self.history)
            pattern.stability_score = stability
            pattern.last_seen_frame = self.history[-1].frame_id
            pattern.last_seen_timestamp = self.history[-1].timestamp

            return {
                'event': 'metastable_pattern_detected',
                'coalition': list(coalition),
                'duration_frames': pattern.duration_frames,
                'stability_score': round(stability, 3),
                'dominant': self.history[-1].dominant_subentity,
                'label': self._generate_label(coalition)
            }

        return None

    def _compute_stability(self, active_sets: List[Set[str]]) -> float:
        """
        Compute stability of coalition across window.

        Uses average Jaccard similarity between consecutive frames.
        High similarity = stable coalition.

        Returns:
            Stability score (0-1)
        """
        if len(active_sets) < 2:
            return 0.0

        similarities = []
        for i in range(len(active_sets) - 1):
            set_a = active_sets[i]
            set_b = active_sets[i + 1]

            if not set_a or not set_b:
                similarities.append(0.0)
                continue

            # Jaccard similarity
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            similarity = intersection / union if union > 0 else 0.0
            similarities.append(similarity)

        return float(np.mean(similarities))

    def _find_or_create_pattern(self, coalition: Set[str]) -> CoactivationPattern:
        """
        Find existing pattern for coalition or create new one.

        Returns:
            CoactivationPattern (ephemeral, not stored as entity)
        """
        # Check if coalition matches existing tracked pattern
        for pattern in self.tracked_patterns:
            overlap = len(coalition & pattern.coalition)
            total = len(coalition | pattern.coalition)
            similarity = overlap / total if total > 0 else 0.0

            if similarity >= 0.85:
                # Close enough - same pattern
                return pattern

        # New pattern - create
        pattern = CoactivationPattern(
            coalition=coalition,
            first_detected_frame=self.history[0].frame_id,
            first_detected_timestamp=self.history[0].timestamp,
            last_seen_frame=self.history[-1].frame_id,
            last_seen_timestamp=self.history[-1].timestamp
        )

        self.tracked_patterns.append(pattern)
        self.patterns_detected += 1

        # Enforce memory limit
        if len(self.tracked_patterns) > self.config.max_tracked_patterns:
            # Remove oldest pattern
            self.tracked_patterns.pop(0)

        return pattern

    def _generate_label(self, coalition: Set[str]) -> str:
        """
        Generate optional human-readable label for pattern.

        WEAK LABELING - for telemetry only, not ontology.
        """
        if not coalition:
            return "empty_coalition"

        # Simple heuristic: use dominant SubEntity name
        # (In real system, could use more sophisticated labeling)
        if len(coalition) == 1:
            return f"{list(coalition)[0]}_dominant"
        else:
            return f"coalition_{len(coalition)}entities"

    def compute_current_mode(
        self,
        active_subentities: Set[str],
        activation_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compute ephemeral "mode" label for current frame.

        This is for telemetry/dashboards ONLY - not a Mode entity.

        Returns:
            Dict with current activation pattern summary
        """
        dominant = None
        if activation_scores:
            dominant = max(activation_scores.keys(), key=lambda k: activation_scores[k])

        return {
            'timestamp': time.time(),
            'active_subentities': list(active_subentities),
            'dominant': dominant,
            'label': self._generate_label(active_subentities),
            'energy_distribution': {
                se_id: round(score, 3)
                for se_id, score in activation_scores.items()
            }
        }

    def get_persistent_patterns(
        self,
        min_duration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get currently tracked persistent patterns.

        Returns:
            List of pattern dicts (for telemetry/monitoring)
        """
        min_dur = min_duration or self.config.min_duration

        return [
            pattern.to_dict()
            for pattern in self.tracked_patterns
            if pattern.duration_frames >= min_dur
        ]

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data for monitoring."""
        return {
            'frames_observed': self.frames_observed,
            'patterns_detected': self.patterns_detected,
            'currently_tracked_patterns': len(self.tracked_patterns),
            'history_size': len(self.history),
            'persistent_patterns': self.get_persistent_patterns()
        }

    def clear_expired_patterns(self, current_frame: int, ttl_frames: int = 100):
        """
        Remove patterns that haven't been seen recently.

        TTL (time-to-live) prevents accumulation of stale patterns.
        """
        self.tracked_patterns = [
            p for p in self.tracked_patterns
            if current_frame - p.last_seen_frame < ttl_frames
        ]
