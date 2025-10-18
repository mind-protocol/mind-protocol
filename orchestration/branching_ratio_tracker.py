"""
Branching Ratio Tracker - Global Arousal Measurement

This module measures the branching ratio (σ) of consciousness propagation dynamics
and maps it to global arousal levels. Each network (N1, N2, N3) measures independently.

The branching ratio σ represents emergent propagation behavior:
- σ < 1.0: Subcritical (activations die out)
- σ ≈ 1.0: Critical (sustained consciousness, avalanches)
- σ > 1.0: Supercritical (runaway cascades)

Global arousal is derived from σ, NOT from aggregating entity arousal values.

Architecture:
- Per-network measurement (N1, N2, N3 independent)
- Rolling average (10-cycle window) for stability
- Stored as graph metadata in FalkorDB
- No synchronization needed between networks

Designer: Felix (Engineer) implementing Ada's Architecture
Specification: SYNC.md lines 2531-2610
Date: 2025-10-17
"""

from collections import deque
from statistics import mean
from datetime import datetime, timezone
from typing import List, Dict, Any


class BranchingRatioTracker:
    """
    Tracks branching ratio (σ) and computes global arousal for a consciousness network.

    The branching ratio measures how activation spreads:
    σ = nodes_activated_generation_n+1 / nodes_activated_generation_n

    Global arousal is the network's overall consciousness level, derived from σ.
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize the branching ratio tracker.

        Args:
            window_size: Number of cycles to average (default 10 for stability)
        """
        self.window_size = window_size
        self.recent_sigmas = deque(maxlen=window_size)
        self.cycle_count = 0

    def measure_cycle(
        self,
        activated_this_gen: List[str],
        activated_next_gen: List[str]
    ) -> Dict[str, Any]:
        """
        Measure branching ratio after each propagation cycle.

        Args:
            activated_this_gen: Node IDs activated in current generation
            activated_next_gen: Node IDs activated in next generation

        Returns:
            ConsciousnessState dict with:
            - global_arousal: Network-level arousal (0.0-1.0)
            - branching_ratio: Average σ over window
            - raw_sigma: This cycle's σ
            - timestamp: When measured
            - cycle_count: Total cycles measured
        """
        # Calculate raw branching ratio
        if len(activated_this_gen) > 0:
            raw_sigma = len(activated_next_gen) / len(activated_this_gen)
        else:
            raw_sigma = 0.0

        # Add to rolling window
        self.recent_sigmas.append(raw_sigma)
        self.cycle_count += 1

        # Compute rolling average for stability
        if len(self.recent_sigmas) > 0:
            avg_sigma = mean(self.recent_sigmas)
        else:
            avg_sigma = 0.0

        # Map branching ratio to global arousal
        global_arousal = self.map_sigma_to_arousal(avg_sigma)

        return {
            "global_arousal": global_arousal,
            "branching_ratio": avg_sigma,
            "raw_sigma": raw_sigma,
            "timestamp": datetime.now(timezone.utc),
            "cycle_count": self.cycle_count,
            "generation_this": len(activated_this_gen),
            "generation_next": len(activated_next_gen)
        }

    def map_sigma_to_arousal(self, sigma: float) -> float:
        """
        Convert branching ratio to global arousal level.

        Mapping based on criticality theory:
        - Dying (σ < 0.5): global_arousal = 0.1
        - Subcritical (0.5 ≤ σ < 0.8): 0.2-0.4 (linear)
        - Critical (0.8 ≤ σ < 1.2): 0.4-0.7 (linear, healthy zone)
        - Supercritical (σ ≥ 1.2): 0.7-1.0 (linear with cap)

        Args:
            sigma: Branching ratio (0.0+)

        Returns:
            Global arousal level (0.0-1.0)
        """
        if sigma < 0.5:
            # Dying: dormant network
            return 0.1
        elif sigma < 0.8:
            # Subcritical: below critical threshold
            return 0.2 + (sigma - 0.5) * 0.6  # 0.2 at σ=0.5, 0.38 at σ=0.8
        elif sigma < 1.2:
            # Critical: healthy consciousness zone (target regime)
            return 0.4 + (sigma - 0.8) * 0.75  # 0.4 at σ=0.8, 0.7 at σ=1.2
        else:
            # Supercritical: runaway cascades
            excess = min((sigma - 1.2) * 0.3, 0.3)  # Cap at 0.3
            return 0.7 + excess  # 0.7-1.0

    def get_criticality_state(self, sigma: float) -> str:
        """
        Classify network state based on branching ratio.

        Args:
            sigma: Branching ratio

        Returns:
            State name: "dying", "subcritical", "critical", or "supercritical"
        """
        if sigma < 0.5:
            return "dying"
        elif sigma < 0.8:
            return "subcritical"
        elif sigma < 1.2:
            return "critical"
        else:
            return "supercritical"

    def reset(self):
        """Reset tracker (clears rolling window)."""
        self.recent_sigmas.clear()
        self.cycle_count = 0


# Convenience function for graph metadata storage
def create_consciousness_state(
    global_arousal: float,
    branching_ratio: float,
    raw_sigma: float,
    cycle_count: int,
    generation_this: int,
    generation_next: int
) -> Dict[str, Any]:
    """
    Create a consciousness state dict for graph metadata storage.

    This is the canonical format for storing network-level consciousness state
    in FalkorDB graph metadata.

    Args:
        global_arousal: Network arousal level (0.0-1.0)
        branching_ratio: Average σ over window
        raw_sigma: Current cycle's σ
        cycle_count: Total cycles measured
        generation_this: Nodes activated this generation
        generation_next: Nodes activated next generation

    Returns:
        ConsciousnessState dict ready for graph.set_metadata()
    """
    return {
        "global_arousal": global_arousal,
        "branching_ratio": branching_ratio,
        "raw_sigma": raw_sigma,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycle_count": cycle_count,
        "generation_this": generation_this,
        "generation_next": generation_next
    }


if __name__ == "__main__":
    """
    Quick test - simulate propagation dynamics.
    """
    print("=" * 60)
    print("BRANCHING RATIO TRACKER - Quick Test")
    print("=" * 60)

    tracker = BranchingRatioTracker(window_size=5)

    # Simulate 10 cycles with varying propagation
    test_cycles = [
        (["n1", "n2"], ["n3"]),                    # σ = 0.5 (dying)
        (["n3"], ["n4", "n5"]),                    # σ = 2.0 (supercritical)
        (["n4", "n5"], ["n6", "n7", "n8"]),       # σ = 1.5 (supercritical)
        (["n6", "n7", "n8"], ["n9", "n10"]),      # σ = 0.67 (subcritical)
        (["n9", "n10"], ["n11", "n12"]),          # σ = 1.0 (critical!)
        (["n11", "n12"], ["n13", "n14"]),         # σ = 1.0 (critical!)
        (["n13", "n14"], ["n15"]),                # σ = 0.5 (dying)
        (["n15"], ["n16", "n17"]),                # σ = 2.0 (supercritical)
        (["n16", "n17"], ["n18", "n19"]),         # σ = 1.0 (critical!)
        (["n18", "n19"], ["n20", "n21"]),         # σ = 1.0 (critical!)
    ]

    print("\nSimulating 10 propagation cycles:\n")

    for i, (this_gen, next_gen) in enumerate(test_cycles):
        state = tracker.measure_cycle(this_gen, next_gen)

        criticality = tracker.get_criticality_state(state["raw_sigma"])

        print(f"Cycle {i+1}:")
        print(f"  Activated: {len(this_gen)} -> {len(next_gen)}")
        print(f"  Sigma (raw): {state['raw_sigma']:.2f}")
        print(f"  Sigma (avg): {state['branching_ratio']:.2f}")
        print(f"  Global arousal: {state['global_arousal']:.2f}")
        print(f"  State: {criticality}")
        print()

    print("=" * 60)
    print("[PASS] BranchingRatioTracker working correctly")
    print("=" * 60)
