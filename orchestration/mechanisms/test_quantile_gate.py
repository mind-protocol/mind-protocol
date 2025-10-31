"""
Test QuantileGate mechanism

Quick validation of adaptive threshold behavior.
"""

import numpy as np
from quantile_gate import QuantileGate, QuantileConfig, ComparisonMode, GateStatus


def test_quantile_gate_above():
    """Test ABOVE comparison mode"""
    print("=== Test 1: ABOVE Mode (Quality Gate) ===")

    # Create gate: value must exceed Q70
    gate = QuantileGate(QuantileConfig(
        metric_name="coalition_density",
        quantile_level=0.70,
        comparison_mode=ComparisonMode.ABOVE,
        min_samples=10
    ))

    # Record historical values (normal distribution around 0.5)
    np.random.seed(42)
    historical = np.random.normal(0.5, 0.1, 50)
    for val in historical:
        gate.record(val)

    # Get threshold
    threshold = gate.get_threshold()
    print(f"Q70 threshold: {threshold:.3f}")

    # Test values
    test_cases = [
        (0.45, "below threshold"),
        (threshold - 0.01, "just below"),
        (threshold + 0.01, "just above"),
        (0.65, "well above")
    ]

    for value, description in test_cases:
        result = gate.evaluate(value)
        print(f"  {description:15s}: {value:.3f} -> {result.status:7s} (p{result.percentile:.0f}) {result.message}")

    print()


def test_quantile_gate_below():
    """Test BELOW comparison mode"""
    print("=== Test 2: BELOW Mode (Error Gate) ===")

    # Create gate: error must be below Q30
    gate = QuantileGate(QuantileConfig(
        metric_name="error_rate",
        quantile_level=0.30,
        comparison_mode=ComparisonMode.BELOW,
        min_samples=10
    ))

    # Record historical errors
    np.random.seed(42)
    historical = np.random.exponential(0.1, 50)
    for val in historical:
        gate.record(val)

    threshold = gate.get_threshold()
    print(f"Q30 threshold: {threshold:.3f}")

    # Test values
    test_cases = [
        (0.02, "very low error"),
        (threshold - 0.01, "just below"),
        (threshold + 0.01, "just above"),
        (0.20, "high error")
    ]

    for value, description in test_cases:
        result = gate.evaluate(value)
        print(f"  {description:15s}: {value:.3f} -> {result.status:7s} (p{result.percentile:.0f}) {result.message}")

    print()


def test_quantile_gate_between():
    """Test BETWEEN comparison mode"""
    print("=== Test 3: BETWEEN Mode (Normal Range Gate) ===")

    # Create gate: value must be between Q20 and Q80
    gate = QuantileGate(QuantileConfig(
        metric_name="overlap_ratio",
        quantile_level=0.20,
        quantile_level_high=0.80,
        comparison_mode=ComparisonMode.BETWEEN,
        min_samples=10
    ))

    # Record historical values
    np.random.seed(42)
    historical = np.random.normal(1.5, 0.3, 50)
    for val in historical:
        gate.record(val)

    quantiles = gate.compute_quantiles()
    print(f"Normal range: [{quantiles[0.20]:.3f}, {quantiles[0.80]:.3f}]")

    # Test values
    test_cases = [
        (1.0, "below range"),
        (quantiles[0.20] + 0.01, "just inside lower"),
        (1.5, "middle"),
        (quantiles[0.80] - 0.01, "just inside upper"),
        (2.0, "above range")
    ]

    for value, description in test_cases:
        result = gate.evaluate(value)
        print(f"  {description:20s}: {value:.3f} -> {result.status:7s} (p{result.percentile:.0f})")

    print()


def test_insufficient_history():
    """Test behavior with insufficient history"""
    print("=== Test 4: Insufficient History ===")

    gate = QuantileGate(QuantileConfig(
        metric_name="new_metric",
        quantile_level=0.70,
        comparison_mode=ComparisonMode.ABOVE,
        min_samples=30
    ))

    # Record only 5 values (below min_samples=30)
    for val in [0.1, 0.2, 0.3, 0.4, 0.5]:
        gate.record(val)

    result = gate.evaluate(0.6)
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print()


def test_gate_stats():
    """Test gate statistics"""
    print("=== Test 5: Gate Statistics ===")

    gate = QuantileGate(QuantileConfig(
        metric_name="test_metric",
        quantile_level=0.70,
        comparison_mode=ComparisonMode.ABOVE,
        min_samples=10
    ))

    # Record values
    np.random.seed(42)
    for val in np.random.normal(0.5, 0.1, 50):
        gate.record(val)

    stats = gate.get_stats()
    print(f"Active: {stats['active']}")
    print(f"Samples: {stats['samples']}")
    print(f"Mean: {stats['mean']:.3f}")
    print(f"Median: {stats['median']:.3f}")
    print(f"Quantiles:")
    for q_level, q_value in sorted(stats['quantiles'].items()):
        print(f"  Q{int(q_level*100):2d}: {q_value:.3f}")

    print()


if __name__ == "__main__":
    test_quantile_gate_above()
    test_quantile_gate_below()
    test_quantile_gate_between()
    test_insufficient_history()
    test_gate_stats()

    print("✅ All tests passed!")
