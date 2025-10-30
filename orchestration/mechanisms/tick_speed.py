"""
Tick Speed Regulation - Three-Factor Adaptive Scheduling (PR-B)

Implements three-factor adaptive tick scheduling:
- Factor 1 (Stimulus): Fast ticks during active stimulation
- Factor 2 (Activation): Fast ticks during high internal energy (autonomous momentum)
- Factor 3 (Arousal): Arousal floor prevents slow ticks during anxious/excited states
- Physics dt capping to prevent blow-ups
- Optional EMA smoothing to reduce oscillation

Three-Factor Minimum:
  interval_next = min(interval_stimulus, interval_activation, interval_arousal)
  Fastest factor wins - enables rumination, arousal modulation

Architecture:
- Stimulus tracking: Record arrival times
- Activation tracking: Sum total active energy across graph
- Arousal tracking: Mean arousal from active entities
- Interval calculation: Three-factor minimum with bounds
- dt capping: Prevent over-integration after long sleep
- EMA smoothing: Dampen rapid changes
- Reason tracking: Which factor determined interval (observability)

Author: Felix (Engineer)
Created: 2025-10-22
Updated: 2025-10-24 - PR-B: Three-factor tick speed (activation + arousal)
Spec: docs/specs/v2/runtime_engine/tick_speed.md
"""

import time
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING
import logging
import numpy as np

if TYPE_CHECKING:
    from orchestration.core.graph import Graph

logger = logging.getLogger(__name__)


# === Three-Factor Computation Functions (PR-B) ===

def compute_interval_activation(
    graph: 'Graph',
    active_entities: List[str],
    min_interval_ms: float = 100.0,
    max_interval_s: float = 60.0,
    activation_threshold: float = 0.3
) -> float:
    """
    Compute tick interval from internal activation level (PR-B Factor 2).

    High internal activation → fast ticks (enables autonomous momentum).
    Allows rumination, generative overflow without external stimuli.

    Algorithm:
    1. Sum total active energy across all nodes and active entities
    2. Map activation to interval (inverse relationship)
       - High activation (>10.0) → min_interval (fast)
       - Low activation (<1.0) → max_interval (slow)
       - Middle range → log-space interpolation

    Args:
        graph: Consciousness graph
        active_entities: List of entity IDs to check
        min_interval_ms: Minimum interval (fastest rate)
        max_interval_s: Maximum interval (slowest rate)
        activation_threshold: Energy threshold for "active" nodes

    Returns:
        Interval in seconds based on activation level

    Example:
        >>> # High internal energy (ruminating)
        >>> interval = compute_interval_activation(graph, ["felix"], 100, 60, 0.3)
        >>> # interval ≈ 0.1s (fast ticks continue after stimulus)
        >>>
        >>> # Low internal energy (dormant)
        >>> interval = compute_interval_activation(graph, ["felix"], 100, 60, 0.3)
        >>> # interval ≈ 60s (slow ticks)
    """
    # Sum total active energy across graph and entities
    total_active_energy = 0.0

    for node in graph.nodes.values():
        node_energy = node.E  # Total energy across all entities
        if node_energy > activation_threshold:
            total_active_energy += node_energy

    # Map activation to interval (inverse relationship)
    # High activation → short interval (fast ticks)
    # Low activation → long interval (slow ticks)

    min_interval_s = min_interval_ms / 1000.0

    if total_active_energy > 10.0:
        # High activation → minimum interval (fast)
        return min_interval_s
    elif total_active_energy < 1.0:
        # Low activation → maximum interval (slow)
        return max_interval_s
    else:
        # Linear interpolation in log space
        log_energy = np.log10(total_active_energy)
        log_min = np.log10(1.0)
        log_max = np.log10(10.0)

        t = (log_energy - log_min) / (log_max - log_min)  # [0, 1]

        # Invert: high energy → short interval
        interval = max_interval_s * (1 - t) + min_interval_s * t

        return interval


def compute_interval_arousal(
    active_entities: List[str],
    entity_affect_getter,  # Callable that gets affect for entity_id
    min_interval_ms: float = 100.0,
    max_interval_s: float = 60.0,
    arousal_floor_enabled: bool = True
) -> float:
    """
    Compute interval floor from affect arousal (PR-B Factor 3).

    High arousal → prevents very slow ticks (anxiety/excitement keeps mind active).
    Provides arousal floor that prevents dormancy during emotional states.

    Algorithm:
    1. Get arousal magnitude for each active entity
    2. Compute mean arousal
    3. Map arousal to interval floor
       - High arousal (>0.7) → 2x min_interval (prevents slow ticks)
       - Low arousal (<0.3) → max_interval (no constraint)
       - Middle range → linear interpolation

    Args:
        active_entities: List of entity IDs to check
        entity_affect_getter: Function that returns affect vector for entity_id
        min_interval_ms: Minimum interval (fastest rate)
        max_interval_s: Maximum interval (slowest rate)
        arousal_floor_enabled: Whether to apply arousal floor

    Returns:
        Interval floor in seconds based on arousal level

    Example:
        >>> # High arousal (anxious/excited)
        >>> interval = compute_interval_arousal(["felix"], get_affect, 100, 60, True)
        >>> # interval ≈ 0.2s (2x minimum - prevents very slow ticks)
        >>>
        >>> # Low arousal (calm)
        >>> interval = compute_interval_arousal(["felix"], get_affect, 100, 60, True)
        >>> # interval ≈ 60s (no constraint)
    """
    if not arousal_floor_enabled:
        return max_interval_s  # No floor constraint

    # Compute mean arousal across active entities
    arousals = []

    for entity_id in active_entities:
        try:
            affect = entity_affect_getter(entity_id)  # Should return numpy array or None
            if affect is not None and len(affect) > 0:
                arousal = float(np.linalg.norm(affect))  # Magnitude as arousal proxy
                arousals.append(arousal)
        except Exception:
            # If affect getter fails, skip this entity
            continue

    if not arousals:
        # No arousal data → no constraint
        return max_interval_s

    mean_arousal = np.mean(arousals)

    # Map arousal to interval floor
    # High arousal → short floor (prevents slow ticks)
    # Low arousal → no floor constraint

    min_interval_s = min_interval_ms / 1000.0
    arousal_floor = min_interval_s * 2  # 2x minimum

    if mean_arousal > 0.7:
        # High arousal → arousal floor (still fast)
        return arousal_floor
    elif mean_arousal < 0.3:
        # Low arousal → no constraint
        return max_interval_s
    else:
        # Linear interpolation
        t = (mean_arousal - 0.3) / (0.7 - 0.3)
        floor = max_interval_s * (1 - t) + arousal_floor * t
        return floor


@dataclass
class TickSpeedConfig:
    """
    Configuration for adaptive tick speed regulation.

    Attributes:
        min_interval_ms: Minimum tick interval (fastest rate). Default 100ms (10 Hz).
        max_interval_s: Maximum tick interval (slowest rate). Default 60s (1/min).
        dt_cap_s: Maximum physics integration step. Default 5.0s.
        ema_beta: EMA smoothing factor (0=no smoothing, 1=no memory). Default 0.3.
        enable_ema: Whether to apply EMA smoothing. Default True.
    """
    min_interval_ms: float = 100.0  # 10 Hz max
    max_interval_s: float = 60.0    # 1/min min
    dt_cap_s: float = 5.0           # Cap physics dt
    ema_beta: float = 0.3           # Smoothing factor
    enable_ema: bool = True         # EMA toggle


class AdaptiveTickScheduler:
    """
    Three-factor adaptive tick scheduler with dt capping (PR-B).

    Implements the three-factor tick speed regulation mechanism:
    1. Track time since last stimulus (Factor 1)
    2. Compute activation-driven interval (Factor 2 - autonomous momentum)
    3. Compute arousal-driven floor (Factor 3 - emotion modulation)
    4. interval_next = min(all three factors) - fastest wins
    5. Optional EMA smoothing
    6. Cap physics dt to prevent blow-ups
    7. Track reason (which factor determined interval)

    Example:
        >>> config = TickSpeedConfig(min_interval_ms=100, max_interval_s=60)
        >>> scheduler = AdaptiveTickScheduler(config, graph, ["felix"])
        >>>
        >>> # On stimulus arrival
        >>> scheduler.on_stimulus()
        >>>
        >>> # Before each tick
        >>> interval_next, reason, details = scheduler.compute_next_interval()
        >>> dt_used, was_capped = scheduler.compute_dt(interval_next)
        >>>
        >>> # Execute tick with dt_used
        >>> await tick(dt=dt_used)
        >>>
        >>> # Sleep until next tick
        >>> await asyncio.sleep(interval_next)
    """

    def __init__(
        self,
        config: TickSpeedConfig,
        graph: Optional['Graph'] = None,
        active_entities: Optional[List[str]] = None,
        entity_affect_getter = None
    ):
        """
        Initialize three-factor adaptive tick scheduler.

        Args:
            config: Tick speed configuration
            graph: Consciousness graph (for activation tracking)
            active_entities: List of active entity IDs (for activation/arousal)
            entity_affect_getter: Function that returns affect vector for entity_id
        """
        self.config = config
        self.graph = graph
        self.active_entities = active_entities or []
        self.entity_affect_getter = entity_affect_getter

        # Stimulus tracking
        self.last_stimulus_time: Optional[float] = None

        # Tick timing
        self.last_tick_time: float = time.time()

        # EMA state
        self.interval_prev: float = config.min_interval_ms / 1000.0

        # Three-factor state (for diagnostics)
        self.last_interval_stimulus: Optional[float] = None
        self.last_interval_activation: Optional[float] = None
        self.last_interval_arousal: Optional[float] = None
        self.last_reason: Optional[str] = None

        logger.info(f"[TickSpeed] Initialized three-factor scheduler: "
                   f"min={config.min_interval_ms}ms, max={config.max_interval_s}s, "
                   f"dt_cap={config.dt_cap_s}s, entities={len(self.active_entities)}")

    def on_stimulus(self) -> None:
        """
        Record stimulus arrival time.

        Call this when a stimulus arrives (user message, external event, etc.).
        Updates last_stimulus_time to current time.

        Side effects:
            Updates self.last_stimulus_time

        Example:
            >>> scheduler.on_stimulus()  # Stimulus just arrived
            >>> interval = scheduler.compute_next_interval()
            >>> # interval will be near min_interval
        """
        self.last_stimulus_time = time.time()
        logger.debug(f"[TickSpeed] Stimulus recorded at {self.last_stimulus_time:.3f}")

    def compute_next_interval(self) -> tuple[float, str, dict]:
        """
        Compute next tick interval using three-factor minimum (PR-B).

        Algorithm:
        1. Compute interval_stimulus (Factor 1): time_since_last_stimulus
        2. Compute interval_activation (Factor 2): from total active energy
        3. Compute interval_arousal (Factor 3): from mean arousal
        4. interval_next = min(all three) - fastest factor wins
        5. Determine reason (which factor won)
        6. Optional EMA smoothing to reduce oscillation

        Returns:
            Tuple of (interval, reason, details):
            - interval: Next tick interval in seconds
            - reason: "stimulus" | "activation" | "arousal_floor"
            - details: Dict with all three intervals + diagnostics

        Example:
            >>> scheduler.on_stimulus()
            >>> interval, reason, details = scheduler.compute_next_interval()
            >>> # reason="stimulus" (just received input)
            >>> # interval ≈ 0.1s
            >>>
            >>> # High internal energy, no recent stimulus
            >>> interval, reason, details = scheduler.compute_next_interval()
            >>> # reason="activation" (autonomous momentum)
            >>> # interval ≈ 0.15s (ruminating)
        """
        now = time.time()

        # Factor 1: Stimulus-driven interval
        if self.last_stimulus_time is None:
            # No stimulus yet - dormant mode
            interval_stimulus_raw = self.config.max_interval_s
        else:
            # Time since last stimulus
            time_since_stimulus = now - self.last_stimulus_time
            interval_stimulus_raw = time_since_stimulus

        # Clamp stimulus interval to bounds
        interval_stimulus = max(
            self.config.min_interval_ms / 1000.0,  # min (convert ms to s)
            min(interval_stimulus_raw, self.config.max_interval_s)  # max
        )

        # Factor 2: Activation-driven interval (autonomous momentum)
        if self.graph and self.active_entities:
            interval_activation = compute_interval_activation(
                self.graph,
                self.active_entities,
                self.config.min_interval_ms,
                self.config.max_interval_s
            )
        else:
            # No graph/entities → no activation factor
            interval_activation = self.config.max_interval_s

        # Factor 3: Arousal-driven floor (emotion modulation)
        if self.active_entities and self.entity_affect_getter:
            interval_arousal = compute_interval_arousal(
                self.active_entities,
                self.entity_affect_getter,
                self.config.min_interval_ms,
                self.config.max_interval_s
            )
        else:
            # No affect data → no arousal factor
            interval_arousal = self.config.max_interval_s

        # Three-factor minimum: Fastest factor wins
        interval_candidates = {
            'stimulus': interval_stimulus,
            'activation': interval_activation,
            'arousal_floor': interval_arousal
        }

        interval_min = min(interval_candidates.values())
        reason = min(interval_candidates, key=interval_candidates.get)

        # Store for diagnostics
        self.last_interval_stimulus = interval_stimulus
        self.last_interval_activation = interval_activation
        self.last_interval_arousal = interval_arousal
        self.last_reason = reason

        # Optional EMA smoothing
        if self.config.enable_ema:
            # ema_t = β·v_t + (1-β)·ema_{t-1}
            interval_smoothed = (
                self.config.ema_beta * interval_min +
                (1 - self.config.ema_beta) * self.interval_prev
            )
            self.interval_prev = interval_smoothed
            final_interval = interval_smoothed
        else:
            final_interval = interval_min

        # Build details dict for observability
        details = {
            'interval_stimulus': interval_stimulus,
            'interval_activation': interval_activation,
            'interval_arousal': interval_arousal,
            'interval_min': interval_min,
            'interval_smoothed': final_interval if self.config.enable_ema else None,
            'reason': reason
        }

        logger.debug(f"[TickSpeed] Three-factor: stimulus={interval_stimulus:.3f}s, "
                    f"activation={interval_activation:.3f}s, arousal={interval_arousal:.3f}s "
                    f"→ {reason}={final_interval:.3f}s")

        return final_interval, reason, details

    def compute_dt(self, interval: float) -> tuple[float, bool]:
        """
        Compute physics dt with capping.

        Algorithm (spec §2.2):
        dt_used = min(interval, dt_cap)

        This prevents "first tick after long sleep" from over-integrating
        diffusion/decay by limiting physics integration step.

        Args:
            interval: Wall-clock interval (from compute_next_interval)

        Returns:
            Tuple of (dt_used, was_capped)
            - dt_used: Physics integration time step (seconds)
            - was_capped: True if dt < interval (dt was capped)

        Example:
            >>> # After short interval
            >>> dt, capped = scheduler.compute_dt(0.5)
            >>> # dt=0.5, capped=False (under cap)
            >>>
            >>> # After long dormancy
            >>> dt, capped = scheduler.compute_dt(120.0)
            >>> # dt=5.0, capped=True (hit dt_cap)
        """
        dt_used = min(interval, self.config.dt_cap_s)
        was_capped = dt_used < interval

        if was_capped:
            logger.debug(f"[TickSpeed] dt capped: interval={interval:.3f}s → dt={dt_used:.3f}s")
        else:
            logger.debug(f"[TickSpeed] dt uncapped: {dt_used:.3f}s")

        return dt_used, was_capped

    def get_diagnostics(self) -> dict:
        """
        Get scheduler diagnostics for observability (three-factor).

        Returns:
            Dictionary with diagnostic fields:
            - last_stimulus_time: When last stimulus arrived (None if never)
            - time_since_stimulus: Seconds since last stimulus (None if never)
            - interval_prev: Previous EMA-smoothed interval
            - three_factor_state: Last computed three-factor intervals
            - last_reason: Which factor determined last interval
            - config: Current configuration

        Example:
            >>> diag = scheduler.get_diagnostics()
            >>> print(f"Reason: {diag['last_reason']}")
            >>> print(f"Activation interval: {diag['three_factor_state']['activation']:.2f}s")
        """
        now = time.time()

        return {
            'last_stimulus_time': self.last_stimulus_time,
            'time_since_stimulus': now - self.last_stimulus_time if self.last_stimulus_time else None,
            'interval_prev': self.interval_prev,
            'three_factor_state': {
                'stimulus': self.last_interval_stimulus,
                'activation': self.last_interval_activation,
                'arousal_floor': self.last_interval_arousal
            },
            'last_reason': self.last_reason,
            'config': {
                'min_interval_ms': self.config.min_interval_ms,
                'max_interval_s': self.config.max_interval_s,
                'dt_cap_s': self.config.dt_cap_s,
                'ema_beta': self.config.ema_beta,
                'enable_ema': self.config.enable_ema
            }
        }
