"""
Source Impact Gate g(source) - Flip Yield Learning for Different Stimulus Types

Implements adaptive source gating based on historical flip yield:
- Tracks flips/budget ratio per source type
- Rank-normalizes to [0.5, 1.5] range
- Prevents silencing any source (minimum 0.5x budget)

Designer: Felix "Ironhand"
Date: 2025-10-21
Reference: stimulus_injection_specification.md §3.4
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class SourceObservation:
    """Single frame observation for a source type."""
    source_type: str
    num_flips: int
    budget_spent: float
    flip_yield: float  # flips / budget
    timestamp: float


class SourceImpactGate:
    """
    Learns and applies source-type based budget modulation.

    Tracks:
    - Flip yield per source type: flips / budget
    - Rolling window per source (default 1 week = 604800 seconds)
    - Rank normalization to [0.5, 1.5]

    Returns:
    - g(source) ∈ [0.5, 1.5] (rank-normalized)
    """

    def __init__(
        self,
        window_seconds: float = 604800.0,  # 1 week default
        min_samples: int = 50
    ):
        """
        Initialize source impact gate.

        Args:
            window_seconds: Rolling window duration in seconds
            min_samples: Minimum samples per source before modulation
        """
        self.window_seconds = window_seconds
        self.min_samples = min_samples

        # Per-source observations: source_type -> deque of observations
        self.observations: Dict[str, deque] = defaultdict(
            lambda: deque()
        )

        logger.info(
            f"[SourceImpactGate] Initialized "
            f"(window={window_seconds/3600:.1f}h, min_samples={min_samples})"
        )

    def add_observation(
        self,
        source_type: str,
        num_flips: int,
        budget_spent: float,
        timestamp: Optional[float] = None
    ):
        """
        Record frame observation for a source type.

        Args:
            source_type: Type of stimulus source
            num_flips: Number of threshold crossings this frame
            budget_spent: Energy budget used this frame
            timestamp: Frame timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        # Compute flip yield
        flip_yield = num_flips / (budget_spent + 1e-6)

        # Create observation
        obs = SourceObservation(
            source_type=source_type,
            num_flips=num_flips,
            budget_spent=budget_spent,
            flip_yield=flip_yield,
            timestamp=timestamp
        )

        # Add to source-specific window
        self.observations[source_type].append(obs)

        # Prune old observations outside window
        self._prune_window(source_type, timestamp)

        logger.debug(
            f"[SourceImpactGate] Recorded {source_type}: "
            f"flips={num_flips}, budget={budget_spent:.2f}, "
            f"yield={flip_yield:.3f}"
        )

    def _prune_window(self, source_type: str, current_time: float):
        """Remove observations outside rolling window."""
        window = self.observations[source_type]
        cutoff_time = current_time - self.window_seconds

        # Remove old observations from left
        while window and window[0].timestamp < cutoff_time:
            window.popleft()

    def _rank_normalize(self, values: list, target_value: float) -> float:
        """
        Rank-normalize target_value within cohort to [0.5, 1.5].

        Args:
            values: Cohort of values
            target_value: Value to normalize

        Returns:
            Normalized value ∈ [0.5, 1.5]
        """
        if len(values) < 2:
            return 1.0  # Neutral

        # Rank position
        rank = sum(1 for v in values if v <= target_value)

        # Rank to [0, 1]
        rank_frac = rank / len(values)

        # Map to [0.5, 1.5]
        normalized = 0.5 + rank_frac * 1.0

        return normalized

    def modulate(self, source_type: str) -> float:
        """
        Apply source impact modulation to budget.

        Args:
            source_type: Type of stimulus source

        Returns:
            Modulation factor g(source) ∈ [0.5, 1.5]
        """
        # Bootstrap: neutral until sufficient data
        source_obs = self.observations.get(source_type, deque())

        if len(source_obs) < self.min_samples:
            logger.debug(
                f"[SourceImpactGate] {source_type}: bootstrap mode "
                f"({len(source_obs)}/{self.min_samples} samples)"
            )
            return 1.0

        # Get recent flip yields for this source
        source_yields = [obs.flip_yield for obs in source_obs]

        # Get recent flip yields across ALL sources (cohort)
        all_yields = []
        for obs_list in self.observations.values():
            all_yields.extend([obs.flip_yield for obs in obs_list])

        if len(all_yields) < 2:
            return 1.0

        # Average yield for this source
        avg_source_yield = np.mean(source_yields)

        # Rank-normalize this source's average yield within all-source cohort
        g_source = self._rank_normalize(all_yields, avg_source_yield)

        # Safety clamp (should already be in range but defensive)
        g_source = np.clip(g_source, 0.5, 1.5)

        logger.debug(
            f"[SourceImpactGate] {source_type}: "
            f"avg_yield={avg_source_yield:.3f}, "
            f"g(source)={g_source:.3f}"
        )

        return float(g_source)

    def get_stats(self) -> dict:
        """Get current gate statistics."""
        stats = {}

        for source_type, obs_list in self.observations.items():
            if len(obs_list) > 0:
                yields = [obs.flip_yield for obs in obs_list]
                stats[source_type] = {
                    "observations": len(obs_list),
                    "avg_yield": float(np.mean(yields)),
                    "min_yield": float(np.min(yields)),
                    "max_yield": float(np.max(yields)),
                    "current_modulation": self.modulate(source_type)
                }

        return stats
