"""
Metrics - Pure Observability for Consciousness Engine

ARCHITECTURAL PRINCIPLE: Observability, NOT Control

This module measures consciousness outcomes WITHOUT affecting behavior:
- Branching ratio (σ) - emergent propagation dynamics
- Global energy - network-level consciousness
- Criticality state - dying/subcritical/critical/supercritical

CRITICAL: Metrics are PURE MEASUREMENT:
- ✅ Measures OUTCOME (what happened)
- ❌ Does NOT control PROCESS (what should happen)
- ✅ No feedback loops to consciousness logic
- ❌ No modulation of mechanisms

The branching ratio σ represents emergent propagation behavior:
- σ < 1.0: Subcritical (activations die out)
- σ ≈ 1.0: Critical (sustained consciousness, avalanches)
- σ > 1.0: Supercritical (runaway cascades)

Global energy is derived from σ, NOT from aggregating entity energy values.

Architecture:
- Per-network measurement (N1, N2, N3 independent)
- Rolling average (10-cycle window) for stability
- Stored as graph metadata in FalkorDB
- No synchronization needed between networks

Author: Felix (Engineer)
Created: 2025-10-19 (extracted from branching_ratio_tracker.py)
Architecture: Phase 1 Clean Break - Observability Layer
"""

from collections import deque
from statistics import mean
from datetime import datetime, timezone
from typing import List, Dict, Any


class BranchingRatioTracker:
    """
    Tracks branching ratio (σ) and computes global energy for a consciousness network.

    PURE OBSERVABILITY - This class measures what happens, it does NOT control what happens.

    The branching ratio measures how activation spreads:
    σ = nodes_activated_generation_n+1 / nodes_activated_generation_n

    Global energy is the network's overall consciousness level, derived from σ.

    Example Usage:
        >>> tracker = BranchingRatioTracker(window_size=10)
        >>> state = tracker.measure_cycle(
        ...     activated_this_gen=["n1", "n2"],
        ...     activated_next_gen=["n3", "n4", "n5"]
        ... )
        >>> state["raw_sigma"]
        1.5  # Supercritical (3/2)
        >>> state["global_energy"]
        0.79  # High consciousness level
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize the branching ratio tracker.

        Args:
            window_size: Number of cycles to average (default 10 for stability)
        """
        self.window_size = window_size
        self.recent_sigmas: deque = deque(maxlen=window_size)
        self.cycle_count: int = 0

    def measure_cycle(
        self,
        activated_this_gen: List[str],
        activated_next_gen: List[str]
    ) -> Dict[str, Any]:
        """
        Measure branching ratio after each propagation cycle.

        This is PURE MEASUREMENT - it records what happened,
        it does NOT modify consciousness state or behavior.

        Args:
            activated_this_gen: Node IDs activated in current generation
            activated_next_gen: Node IDs activated in next generation

        Returns:
            ConsciousnessState dict with:
            - global_energy: Network-level energy (0.0-1.0)
            - branching_ratio: Average σ over window
            - raw_sigma: This cycle's σ
            - timestamp: When measured
            - cycle_count: Total cycles measured
            - generation_this: Count of nodes this generation
            - generation_next: Count of nodes next generation

        Example:
            >>> tracker = BranchingRatioTracker()
            >>> state = tracker.measure_cycle(["n1"], ["n2", "n3"])
            >>> state["raw_sigma"]
            2.0  # Supercritical
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

        # Map branching ratio to global energy
        global_energy = self.map_sigma_to_energy(avg_sigma)

        return {
            "global_energy": global_energy,
            "branching_ratio": avg_sigma,
            "raw_sigma": raw_sigma,
            "timestamp": datetime.now(timezone.utc),
            "cycle_count": self.cycle_count,
            "generation_this": len(activated_this_gen),
            "generation_next": len(activated_next_gen)
        }

    def map_sigma_to_energy(self, sigma: float) -> float:
        """
        Convert branching ratio to global energy level.

        Mapping based on criticality theory:
        - Dying (σ < 0.5): global_energy = 0.1
        - Subcritical (0.5 ≤ σ < 0.8): 0.2-0.4 (linear)
        - Critical (0.8 ≤ σ < 1.2): 0.4-0.7 (linear, healthy zone)
        - Supercritical (σ ≥ 1.2): 0.7-1.0 (linear with cap)

        Args:
            sigma: Branching ratio (0.0+)

        Returns:
            Global energy level (0.0-1.0)

        Example:
            >>> tracker = BranchingRatioTracker()
            >>> tracker.map_sigma_to_energy(1.0)
            0.55  # Critical zone
            >>> tracker.map_sigma_to_energy(0.3)
            0.1  # Dying
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

        Example:
            >>> tracker = BranchingRatioTracker()
            >>> tracker.get_criticality_state(1.0)
            'critical'
            >>> tracker.get_criticality_state(2.0)
            'supercritical'
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
        """
        Reset tracker (clears rolling window).

        Useful for starting fresh measurement after major graph changes.
        """
        self.recent_sigmas.clear()
        self.cycle_count = 0


# Convenience function for graph metadata storage
def create_consciousness_state(
    global_energy: float,
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
        global_energy: Network energy level (0.0-1.0)
        branching_ratio: Average σ over window
        raw_sigma: Current cycle's σ
        cycle_count: Total cycles measured
        generation_this: Nodes activated this generation
        generation_next: Nodes activated next generation

    Returns:
        ConsciousnessState dict ready for graph.set_metadata()

    Example:
        >>> state = create_consciousness_state(
        ...     global_energy=0.7,
        ...     branching_ratio=1.0,
        ...     raw_sigma=1.0,
        ...     cycle_count=100,
        ...     generation_this=10,
        ...     generation_next=10
        ... )
        >>> state["global_energy"]
        0.7
    """
    return {
        "global_energy": global_energy,
        "branching_ratio": branching_ratio,
        "raw_sigma": raw_sigma,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycle_count": cycle_count,
        "generation_this": generation_this,
        "generation_next": generation_next
    }
