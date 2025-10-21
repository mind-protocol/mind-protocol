"""
Health Modulation f(ρ) - Isotonic Regression for Spectral Radius-Based Budget Control

Implements adaptive budget scaling based on system health:
- Subcritical (too little activation) → boost budget (f > 1)
- Supercritical (too much activation) → dampen budget (f < 1)

Uses isotonic regression to learn monotone non-increasing mapping from
spectral radius proxy to frame quality.

Designer: Felix "Ironhand"
Date: 2025-10-21
Reference: stimulus_injection_specification.md §3.3
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class FrameObservation:
    """Single frame observation for health learning."""
    rho_proxy: float  # Spectral radius proxy
    yield_score: float  # Flip yield (normalized)
    entropy_score: float  # Activation entropy (normalized)
    overflow_score: float  # 1 - overflow_rate (normalized)
    quality: float  # Geometric mean of above
    timestamp: float


class HealthModulator:
    """
    Learns and applies health-based budget modulation.

    Tracks:
    - Spectral radius proxy ρ = max_degree × avg_weight / N
    - Frame quality q = (yield × entropy × low_overflow)^(1/3)
    - Isotonic regression f: ρ → q (monotone non-increasing)

    Returns:
    - f(ρ) ∈ [0.5, 1.5] clamped (safety bounds)
    """

    def __init__(self, history_size: int = 1000, min_samples: int = 200):
        """
        Initialize health modulator.

        Args:
            history_size: Rolling window size for observations
            min_samples: Minimum samples before enabling modulation
        """
        self.history_size = history_size
        self.min_samples = min_samples

        # Rolling history
        self.observations = deque(maxlen=history_size)

        # Isotonic regression model (lazy-loaded)
        self.iso_model = None
        self.model_trained_at = 0  # Sample count when last trained

        # Rolling cohort statistics for normalization
        self.yield_window = deque(maxlen=history_size)
        self.entropy_window = deque(maxlen=history_size)
        self.overflow_window = deque(maxlen=history_size)

        logger.info(f"[HealthModulator] Initialized (min_samples={min_samples}, history={history_size})")

    def compute_rho_proxy(
        self,
        max_degree: int,
        avg_weight: float,
        active_node_count: int
    ) -> float:
        """
        Compute spectral radius proxy.

        Formula: ρ = max_degree × avg_weight / N

        Args:
            max_degree: Maximum node outgoing degree
            avg_weight: Average link weight (exp(log_weight))
            active_node_count: Number of active nodes this frame

        Returns:
            Spectral radius proxy (rough upper bound)
        """
        if active_node_count == 0:
            return 0.0

        rho = (max_degree * avg_weight) / active_node_count

        return rho

    def add_observation(
        self,
        rho_proxy: float,
        num_flips: int,
        budget_spent: float,
        activation_entropy: float,
        overflow_occurred: bool,
        timestamp: float
    ):
        """
        Record frame observation for learning.

        Args:
            rho_proxy: Spectral radius proxy this frame
            num_flips: Number of threshold crossings
            budget_spent: Energy budget injected
            activation_entropy: Shannon entropy of active node distribution
            overflow_occurred: Whether hard limits were hit
            timestamp: Frame timestamp
        """

        # Compute raw scores
        flip_yield = num_flips / (budget_spent + 1e-6)  # Avoid div by zero
        overflow_penalty = 0.0 if overflow_occurred else 1.0

        # Add to rolling windows
        self.yield_window.append(flip_yield)
        self.entropy_window.append(activation_entropy)
        self.overflow_window.append(overflow_penalty)

        # Rank-normalize within cohort
        yield_norm = self._rank_normalize(flip_yield, self.yield_window)
        entropy_norm = self._rank_normalize(activation_entropy, self.entropy_window)
        overflow_norm = self._rank_normalize(overflow_penalty, self.overflow_window)

        # Geometric mean (requires balance)
        quality = (yield_norm * entropy_norm * overflow_norm) ** (1/3)

        # Create observation
        obs = FrameObservation(
            rho_proxy=rho_proxy,
            yield_score=yield_norm,
            entropy_score=entropy_norm,
            overflow_score=overflow_norm,
            quality=quality,
            timestamp=timestamp
        )

        self.observations.append(obs)

        # Retrain model periodically (every 50 samples)
        if len(self.observations) >= self.min_samples and len(self.observations) % 50 == 0:
            self._train_model()

    def _rank_normalize(self, value: float, cohort: deque) -> float:
        """
        Rank-normalize value within cohort to [0, 1].

        Args:
            value: Value to normalize
            cohort: Rolling window of recent values

        Returns:
            Normalized value ∈ [0, 1]
        """
        if len(cohort) < 2:
            return 0.5  # Neutral

        cohort_list = list(cohort)
        rank = sum(1 for v in cohort_list if v <= value)

        # Rank to [0, 1]
        normalized = rank / len(cohort_list)

        return normalized

    def _train_model(self):
        """
        Train isotonic regression model on observations.

        Learns monotone non-increasing f: ρ → quality.
        """
        try:
            from sklearn.isotonic import IsotonicRegression
        except ImportError:
            logger.warning("[HealthModulator] sklearn not available, health modulation disabled")
            return

        if len(self.observations) < self.min_samples:
            return

        # Extract training data
        rho_values = np.array([obs.rho_proxy for obs in self.observations])
        quality_values = np.array([obs.quality for obs in self.observations])

        # Fit monotone non-increasing mapping
        self.iso_model = IsotonicRegression(increasing=False)
        self.iso_model.fit(rho_values, quality_values)

        self.model_trained_at = len(self.observations)

        logger.info(
            f"[HealthModulator] Model trained on {len(self.observations)} samples "
            f"(ρ range: [{rho_values.min():.3f}, {rho_values.max():.3f}])"
        )

    def modulate(self, rho_proxy: float) -> float:
        """
        Apply health modulation to budget.

        Args:
            rho_proxy: Current spectral radius proxy

        Returns:
            Modulation factor f(ρ) ∈ [0.5, 1.5]
        """
        # Bootstrap: neutral until sufficient data
        if self.iso_model is None or len(self.observations) < self.min_samples:
            return 1.0

        # Predict quality from ρ
        try:
            predicted_quality = self.iso_model.predict([rho_proxy])[0]
        except Exception as e:
            logger.warning(f"[HealthModulator] Prediction failed: {e}")
            return 1.0

        # Map quality to modulation factor
        # High quality (system healthy) → f ≈ 1.0
        # Low quality (system struggling) → f < 1.0 or f > 1.0 depending on cause

        # Simple mapping: use predicted quality directly as factor
        # Quality ∈ [0, 1], want f ∈ [0.5, 1.5]
        # Linear map: f = 0.5 + quality × 1.0

        f_rho = 0.5 + predicted_quality * 1.0

        # Safety clamp
        f_rho = np.clip(f_rho, 0.5, 1.5)

        return float(f_rho)

    def get_stats(self) -> dict:
        """Get current modulator statistics."""
        return {
            "observations": len(self.observations),
            "model_trained": self.iso_model is not None,
            "model_trained_at": self.model_trained_at,
            "min_samples_reached": len(self.observations) >= self.min_samples,
            "current_rho_range": (
                min(obs.rho_proxy for obs in self.observations) if self.observations else 0,
                max(obs.rho_proxy for obs in self.observations) if self.observations else 0
            )
        }
