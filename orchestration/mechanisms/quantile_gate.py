"""
QuantileGate - Adaptive Threshold Mechanism

Foundation for zero-constants discipline in SubEntity emergence.
Maintains quantile-based thresholds that evolve with substrate behavior.

Key Principle: No hardcoded thresholds. All gates learned per-citizen from history.

Author: Felix (Core Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/subentity_layer/subentity_emergence_orchestration.md §2.1
"""

import time
from collections import deque
from typing import Optional, Dict, List, Literal
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class GateStatus(str, Enum):
    """Gate evaluation result"""
    PASS = "pass"      # Value passes gate
    FAIL = "fail"      # Value fails gate
    UNKNOWN = "unknown"  # Not enough history to judge


class ComparisonMode(str, Enum):
    """How to compare value against quantile"""
    ABOVE = "above"      # value > threshold (e.g., quality must exceed Q70)
    BELOW = "below"      # value < threshold (e.g., error must be below Q30)
    BETWEEN = "between"  # Q_low <= value <= Q_high (e.g., density in normal range)
    OUTSIDE = "outside"  # value < Q_low OR value > Q_high (e.g., anomaly detection)


@dataclass
class QuantileConfig:
    """Configuration for a quantile gate"""
    metric_name: str                    # e.g., "coalition_density"
    quantile_level: float              # e.g., 0.70 for Q70
    comparison_mode: ComparisonMode
    min_samples: int = 30              # Minimum history before gate activates
    window_size: int = 1000            # Maximum samples to retain
    quantile_level_high: Optional[float] = None  # For BETWEEN/OUTSIDE modes


@dataclass
class GateResult:
    """Result of gate evaluation"""
    status: GateStatus
    value: float
    threshold: Optional[float]         # Computed threshold
    percentile: Optional[float]        # Where value falls in distribution
    message: str                       # Human-readable explanation


class QuantileGate:
    """
    Adaptive threshold gate based on historical quantiles.

    Maintains sliding window of metric values and computes quantiles.
    Gates become active once min_samples collected.

    Examples:
        # Quality gate: coalition density must exceed Q70 of historical densities
        density_gate = QuantileGate(QuantileConfig(
            metric_name="coalition_density",
            quantile_level=0.70,
            comparison_mode=ComparisonMode.ABOVE,
            min_samples=30
        ))

        # Track historical values
        for density in historical_densities:
            density_gate.record(density)

        # Evaluate new value
        result = density_gate.evaluate(new_density)
        if result.status == GateStatus.PASS:
            print(f"Coalition density {new_density} exceeds Q70 threshold {result.threshold}")
    """

    def __init__(self, config: QuantileConfig):
        self.config = config
        self.history: deque = deque(maxlen=config.window_size)
        self.last_quantiles: Dict[float, float] = {}  # Cache computed quantiles

    def record(self, value: float, timestamp: Optional[float] = None):
        """
        Record a new metric value.

        Args:
            value: Metric value to record
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        self.history.append({
            'value': value,
            'timestamp': timestamp
        })

        # Invalidate quantile cache
        self.last_quantiles = {}

    def compute_quantiles(self) -> Dict[float, float]:
        """
        Compute standard quantiles from history.

        Returns:
            Dict mapping quantile level (0.10, 0.20, ..., 0.95) to value
        """
        if len(self.history) < self.config.min_samples:
            return {}

        values = [entry['value'] for entry in self.history]

        quantile_levels = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
        quantiles = np.percentile(values, [q * 100 for q in quantile_levels])

        self.last_quantiles = dict(zip(quantile_levels, quantiles))
        return self.last_quantiles

    def get_threshold(self) -> Optional[float]:
        """
        Get current threshold value based on quantile level.

        Returns:
            Threshold value, or None if not enough history
        """
        if not self.last_quantiles:
            self.compute_quantiles()

        return self.last_quantiles.get(self.config.quantile_level)

    def get_percentile(self, value: float) -> Optional[float]:
        """
        Compute percentile rank of value in current distribution.

        Args:
            value: Value to rank

        Returns:
            Percentile (0-100), or None if not enough history
        """
        if len(self.history) < self.config.min_samples:
            return None

        values = [entry['value'] for entry in self.history]
        sorted_values = sorted(values)

        # Find position in sorted list
        position = np.searchsorted(sorted_values, value)
        percentile = (position / len(sorted_values)) * 100

        return float(percentile)

    def evaluate(self, value: float) -> GateResult:
        """
        Evaluate whether value passes the gate.

        Args:
            value: Value to evaluate

        Returns:
            GateResult with status (PASS/FAIL/UNKNOWN)
        """
        # Check if gate is active (enough history)
        if len(self.history) < self.config.min_samples:
            return GateResult(
                status=GateStatus.UNKNOWN,
                value=value,
                threshold=None,
                percentile=None,
                message=f"Not enough history ({len(self.history)}/{self.config.min_samples} samples)"
            )

        # Compute threshold
        threshold = self.get_threshold()
        if threshold is None:
            return GateResult(
                status=GateStatus.UNKNOWN,
                value=value,
                threshold=None,
                percentile=None,
                message="Failed to compute threshold"
            )

        # Get percentile rank
        percentile = self.get_percentile(value)

        # Evaluate based on comparison mode
        if self.config.comparison_mode == ComparisonMode.ABOVE:
            passed = value > threshold
            message = f"{self.config.metric_name}={value:.3f} {'>' if passed else '<='} Q{int(self.config.quantile_level*100)}={threshold:.3f}"

        elif self.config.comparison_mode == ComparisonMode.BELOW:
            passed = value < threshold
            message = f"{self.config.metric_name}={value:.3f} {'<' if passed else '>='} Q{int(self.config.quantile_level*100)}={threshold:.3f}"

        elif self.config.comparison_mode == ComparisonMode.BETWEEN:
            if self.config.quantile_level_high is None:
                raise ValueError("BETWEEN mode requires quantile_level_high")

            threshold_high = self.last_quantiles.get(self.config.quantile_level_high)
            if threshold_high is None:
                self.compute_quantiles()
                threshold_high = self.last_quantiles.get(self.config.quantile_level_high)

            passed = threshold <= value <= threshold_high
            message = f"Q{int(self.config.quantile_level*100)}={threshold:.3f} {'<=' if passed else '>'} {self.config.metric_name}={value:.3f} {'<=' if passed else '>'} Q{int(self.config.quantile_level_high*100)}={threshold_high:.3f}"

        elif self.config.comparison_mode == ComparisonMode.OUTSIDE:
            if self.config.quantile_level_high is None:
                raise ValueError("OUTSIDE mode requires quantile_level_high")

            threshold_high = self.last_quantiles.get(self.config.quantile_level_high)
            if threshold_high is None:
                self.compute_quantiles()
                threshold_high = self.last_quantiles.get(self.config.quantile_level_high)

            passed = value < threshold or value > threshold_high
            message = f"{self.config.metric_name}={value:.3f} {'outside' if passed else 'inside'} [Q{int(self.config.quantile_level*100)}={threshold:.3f}, Q{int(self.config.quantile_level_high*100)}={threshold_high:.3f}]"

        else:
            raise ValueError(f"Unknown comparison mode: {self.config.comparison_mode}")

        return GateResult(
            status=GateStatus.PASS if passed else GateStatus.FAIL,
            value=value,
            threshold=threshold,
            percentile=percentile,
            message=message
        )

    def get_stats(self) -> Dict:
        """Get statistics about gate state"""
        if len(self.history) < self.config.min_samples:
            return {
                'active': False,
                'samples': len(self.history),
                'min_samples': self.config.min_samples
            }

        values = [entry['value'] for entry in self.history]

        return {
            'active': True,
            'samples': len(self.history),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'quantiles': self.last_quantiles if self.last_quantiles else self.compute_quantiles()
        }


class QuantileGateSet:
    """
    Collection of quantile gates for emergence validation.

    Manages multiple gates for different metrics, provides batch evaluation,
    and tracks overall pass/fail status.
    """

    def __init__(self):
        self.gates: Dict[str, QuantileGate] = {}

    def add_gate(self, gate: QuantileGate):
        """Add a gate to the set"""
        self.gates[gate.config.metric_name] = gate

    def create_gate(
        self,
        metric_name: str,
        quantile_level: float,
        comparison_mode: ComparisonMode,
        min_samples: int = 30,
        window_size: int = 1000,
        quantile_level_high: Optional[float] = None
    ) -> QuantileGate:
        """Create and add a new gate"""
        config = QuantileConfig(
            metric_name=metric_name,
            quantile_level=quantile_level,
            comparison_mode=comparison_mode,
            min_samples=min_samples,
            window_size=window_size,
            quantile_level_high=quantile_level_high
        )
        gate = QuantileGate(config)
        self.add_gate(gate)
        return gate

    def record_all(self, metrics: Dict[str, float], timestamp: Optional[float] = None):
        """Record values for all gates"""
        for metric_name, value in metrics.items():
            if metric_name in self.gates:
                self.gates[metric_name].record(value, timestamp)

    def evaluate_all(self, metrics: Dict[str, float]) -> Dict[str, GateResult]:
        """Evaluate all gates and return results"""
        results = {}
        for metric_name, value in metrics.items():
            if metric_name in self.gates:
                results[metric_name] = self.gates[metric_name].evaluate(value)
        return results

    def all_pass(self, metrics: Dict[str, float]) -> bool:
        """Check if all gates pass (excluding UNKNOWN)"""
        results = self.evaluate_all(metrics)
        for result in results.values():
            if result.status == GateStatus.FAIL:
                return False
        return True

    def get_failed_gates(self, metrics: Dict[str, float]) -> List[str]:
        """Get list of gate names that failed"""
        results = self.evaluate_all(metrics)
        return [
            name for name, result in results.items()
            if result.status == GateStatus.FAIL
        ]

    def get_summary(self, metrics: Dict[str, float]) -> Dict:
        """Get summary of gate evaluation"""
        results = self.evaluate_all(metrics)

        passed = sum(1 for r in results.values() if r.status == GateStatus.PASS)
        failed = sum(1 for r in results.values() if r.status == GateStatus.FAIL)
        unknown = sum(1 for r in results.values() if r.status == GateStatus.UNKNOWN)

        return {
            'total_gates': len(results),
            'passed': passed,
            'failed': failed,
            'unknown': unknown,
            'all_pass': failed == 0,
            'results': {name: result.message for name, result in results.items()}
        }

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all gates"""
        return {
            name: gate.get_stats()
            for name, gate in self.gates.items()
        }
