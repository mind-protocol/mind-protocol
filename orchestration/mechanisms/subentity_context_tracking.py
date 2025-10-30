"""
SubEntity Context Tracking - Affect EMAs and Context Distributions

Terminology Note:
This module operates on SubEntity (Scale A) - weighted neighborhoods
discovered via clustering. See TAXONOMY_RECONCILIATION.md for full
architecture.

SubEntity: Weighted neighborhoods (200-500 per citizen)
Mode: IFS-level meta-roles (5-15 per citizen, Scale B)

This is Scale A operations - SubEntity-level context tracking.

Tracks per-SubEntity contextual metadata required for emergent IFS modes:
1. Affect EMAs (arousal, valence)
2. Context distributions (tools, channels, outcomes)

These enable mode signature computation and community detection.

Phase 1 Implementation (Blocking for Emergent IFS Modes)

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Updated: 2025-10-26 (Scale A terminology clarification)
Spec: docs/specs/v2/subentity/emergent_ifs_modes.md (Inputs - All Exist)
"""

import logging
import numpy as np
from typing import Dict, List, Optional, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from orchestration.core.graph import Graph
    from orchestration.core.subentity import Subentity

logger = logging.getLogger(__name__)


class SubEntityContextTracker:
    """
    Tracks affect EMAs and context distributions per SubEntity.

    Updates from frame events when SubEntities are active in working memory.
    """

    def __init__(self, alpha_affect: float = 0.1, alpha_context: float = 0.05):
        """
        Initialize SubEntity context tracker.

        Args:
            alpha_affect: EMA decay for affect (window ~20 frames)
            alpha_context: EMA decay for context distributions (window ~40 frames)
        """
        self.alpha_affect = alpha_affect
        self.alpha_context = alpha_context

        # Frame-level tracking
        self.frame_count = 0

        logger.info(
            f"[SubEntityContextTracker] Initialized with "
            f"alpha_affect={alpha_affect}, alpha_context={alpha_context}"
        )

    def update_affect_emas(
        self,
        subentity: 'Subentity',
        arousal: float,
        valence: float
    ):
        """
        Update SubEntity affect EMAs from current frame.

        Args:
            subentity: SubEntity to update
            arousal: Current arousal [0, 1]
            valence: Current valence [-1, 1]
        """
        # EMA update: new_value = α * current + (1-α) * old_value
        subentity.arousal_ema = (
            self.alpha_affect * arousal +
            (1 - self.alpha_affect) * subentity.arousal_ema
        )
        subentity.valence_ema = (
            self.alpha_affect * valence +
            (1 - self.alpha_affect) * subentity.valence_ema
        )
        subentity.affect_sample_count += 1

        logger.debug(
            f"[SubEntityContextTracker] Updated affect for {subentity.id}: "
            f"arousal_ema={subentity.arousal_ema:.3f}, "
            f"valence_ema={subentity.valence_ema:.3f}, "
            f"samples={subentity.affect_sample_count}"
        )

    def update_tool_usage(
        self,
        subentity: 'Subentity',
        tool_name: str
    ):
        """
        Increment tool usage count for SubEntity.

        Args:
            subentity: SubEntity to update
            tool_name: Name of tool used (e.g., "Read", "Write", "Bash")
        """
        if tool_name not in subentity.tool_usage_counts:
            subentity.tool_usage_counts[tool_name] = 0

        subentity.tool_usage_counts[tool_name] += 1

        logger.debug(
            f"[SubEntityContextTracker] Incremented tool usage for {subentity.id}: "
            f"{tool_name} count={subentity.tool_usage_counts[tool_name]}"
        )

    def update_channel_usage(
        self,
        subentity: 'Subentity',
        channel: str
    ):
        """
        Increment channel usage count for SubEntity.

        Args:
            subentity: SubEntity to update
            channel: Stimulus channel (e.g., "user_message", "code_change", "time_trigger")
        """
        if channel not in subentity.channel_usage_counts:
            subentity.channel_usage_counts[channel] = 0

        subentity.channel_usage_counts[channel] += 1

        logger.debug(
            f"[SubEntityContextTracker] Incremented channel usage for {subentity.id}: "
            f"{channel} count={subentity.channel_usage_counts[channel]}"
        )

    def update_outcome_distribution(
        self,
        subentity: 'Subentity',
        outcome: str
    ):
        """
        Update outcome distribution EMA for SubEntity.

        Args:
            subentity: SubEntity to update
            outcome: Outcome classification ("very_useful", "useful", "somewhat_useful",
                    "not_useful", "misleading")
        """
        # Normalize outcome distribution to sum to 1.0
        # New sample: outcome gets +1, all others get 0
        for key in subentity.outcome_distribution:
            if key == outcome:
                # EMA update with new observation = 1.0
                subentity.outcome_distribution[key] = (
                    self.alpha_context * 1.0 +
                    (1 - self.alpha_context) * subentity.outcome_distribution[key]
                )
            else:
                # EMA update with new observation = 0.0
                subentity.outcome_distribution[key] = (
                    self.alpha_context * 0.0 +
                    (1 - self.alpha_context) * subentity.outcome_distribution[key]
                )

        # Re-normalize to sum to 1.0 (prevent drift from floating point errors)
        total = sum(subentity.outcome_distribution.values())
        if total > 0:
            for key in subentity.outcome_distribution:
                subentity.outcome_distribution[key] /= total

        logger.debug(
            f"[SubEntityContextTracker] Updated outcome distribution for {subentity.id}: "
            f"{outcome} -> {subentity.outcome_distribution}"
        )

    def update_from_wm_frame(
        self,
        graph: 'Graph',
        active_subentities: List[str],
        frame_affect: Optional[np.ndarray] = None,
        frame_tool: Optional[str] = None,
        frame_channel: Optional[str] = None,
        frame_outcome: Optional[str] = None
    ):
        """
        Update context tracking for all active SubEntities in working memory.

        Args:
            graph: Consciousness graph containing SubEntities
            active_subentities: List of SubEntity IDs active in working memory this frame
            frame_affect: Frame affect vector [arousal, valence] (optional)
            frame_tool: Tool used this frame (optional)
            frame_channel: Stimulus channel this frame (optional)
            frame_outcome: Outcome classification this frame (optional)
        """
        self.frame_count += 1

        if not active_subentities:
            logger.debug(
                f"[SubEntityContextTracker] Frame {self.frame_count}: "
                "No active SubEntities, skipping update"
            )
            return

        # Update affect for all active SubEntities
        if frame_affect is not None and len(frame_affect) == 2:
            arousal = float(frame_affect[0])
            valence = float(frame_affect[1])

            # Clip to valid ranges
            arousal = max(0.0, min(1.0, arousal))
            valence = max(-1.0, min(1.0, valence))

            for subentity_id in active_subentities:
                subentity = graph.subentities.get(subentity_id)
                if subentity:
                    self.update_affect_emas(subentity, arousal, valence)

        # Update tool usage for all active SubEntities
        if frame_tool:
            for subentity_id in active_subentities:
                subentity = graph.subentities.get(subentity_id)
                if subentity:
                    self.update_tool_usage(subentity, frame_tool)

        # Update channel usage for all active SubEntities
        if frame_channel:
            for subentity_id in active_subentities:
                subentity = graph.subentities.get(subentity_id)
                if subentity:
                    self.update_channel_usage(subentity, frame_channel)

        # Update outcome distribution for all active SubEntities
        if frame_outcome:
            for subentity_id in active_subentities:
                subentity = graph.subentities.get(subentity_id)
                if subentity:
                    self.update_outcome_distribution(subentity, frame_outcome)

        logger.debug(
            f"[SubEntityContextTracker] Frame {self.frame_count}: "
            f"Updated {len(active_subentities)} SubEntities "
            f"(affect={frame_affect is not None}, tool={frame_tool}, "
            f"channel={frame_channel}, outcome={frame_outcome})"
        )

    def get_affect_signature(self, subentity: 'Subentity') -> Dict[str, float]:
        """
        Get affect signature for SubEntity (for mode signature computation).

        Returns:
            Dict with "arousal" and "valence" keys
        """
        return {
            "arousal": float(subentity.arousal_ema),
            "valence": float(subentity.valence_ema)
        }

    def get_tool_distribution(self, subentity: 'Subentity') -> Dict[str, float]:
        """
        Get tool usage distribution for SubEntity (normalized to probabilities).

        Returns:
            Dict mapping tool_name -> probability
        """
        total = sum(subentity.tool_usage_counts.values())
        if total == 0:
            return {}

        return {
            tool: count / total
            for tool, count in subentity.tool_usage_counts.items()
        }

    def get_channel_distribution(self, subentity: 'Subentity') -> Dict[str, float]:
        """
        Get channel usage distribution for SubEntity (normalized to probabilities).

        Returns:
            Dict mapping channel -> probability
        """
        total = sum(subentity.channel_usage_counts.values())
        if total == 0:
            return {}

        return {
            channel: count / total
            for channel, count in subentity.channel_usage_counts.items()
        }

    def get_outcome_distribution(self, subentity: 'Subentity') -> Dict[str, float]:
        """
        Get outcome distribution for SubEntity (already normalized EMA).

        Returns:
            Dict mapping outcome -> probability
        """
        return dict(subentity.outcome_distribution)

    def compute_affect_similarity(
        self,
        subentity_a: 'Subentity',
        subentity_b: 'Subentity'
    ) -> float:
        """
        Compute affect similarity between two SubEntities.

        Used for mode community detection (emergent_ifs_modes.md Step 1).

        Returns:
            Similarity score [0, 1] where 1 = identical affect
        """
        # Euclidean distance in [arousal, valence] space
        arousal_diff = abs(subentity_a.arousal_ema - subentity_b.arousal_ema)
        valence_diff = abs(subentity_a.valence_ema - subentity_b.valence_ema)

        # Max distance = sqrt(1^2 + 2^2) = sqrt(5) ≈ 2.236
        # (arousal [0,1], valence [-1,1])
        distance = np.sqrt(arousal_diff**2 + valence_diff**2)
        max_distance = np.sqrt(1.0**2 + 2.0**2)

        # Convert to similarity
        similarity = 1.0 - (distance / max_distance)

        return float(similarity)

    def compute_tool_overlap(
        self,
        subentity_a: 'Subentity',
        subentity_b: 'Subentity'
    ) -> float:
        """
        Compute tool usage overlap between two SubEntities using Jensen-Shannon Divergence.

        Used for mode community detection (emergent_ifs_modes.md Step 1).

        Returns:
            Overlap score [0, 1] where 1 = identical tool distributions
        """
        dist_a = self.get_tool_distribution(subentity_a)
        dist_b = self.get_tool_distribution(subentity_b)

        if not dist_a or not dist_b:
            return 0.0  # No overlap if either has no tool usage

        # Get all tools from both distributions
        all_tools = set(dist_a.keys()) | set(dist_b.keys())

        # Build probability vectors
        p = np.array([dist_a.get(tool, 0.0) for tool in all_tools])
        q = np.array([dist_b.get(tool, 0.0) for tool in all_tools])

        # Jensen-Shannon Divergence
        m = 0.5 * (p + q)

        def kl_div(p, q):
            """KL divergence, handling zeros."""
            result = 0.0
            for pi, qi in zip(p, q):
                if pi > 0 and qi > 0:
                    result += pi * np.log(pi / qi)
            return result

        jsd = 0.5 * kl_div(p, m) + 0.5 * kl_div(q, m)

        # Convert JSD [0, log(2)] to similarity [0, 1]
        # JSD=0 → similarity=1, JSD=log(2) → similarity=0
        similarity = 1.0 - (jsd / np.log(2.0))

        return float(np.clip(similarity, 0.0, 1.0))
