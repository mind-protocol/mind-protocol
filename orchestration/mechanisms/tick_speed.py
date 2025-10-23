"""
Tick Speed Regulation - Stimulus-adaptive scheduling with dt capping

Implements adaptive tick scheduling:
- Fast ticks (100ms) during active stimulation
- Slow ticks (60s) during dormancy
- Physics dt capping to prevent blow-ups
- Optional EMA smoothing to reduce oscillation

Architecture:
- Stimulus tracking: Record arrival times
- Interval calculation: time_since_last_stimulus with bounds
- dt capping: Prevent over-integration after long sleep
- EMA smoothing: Dampen rapid changes

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/runtime_engine/tick_speed.md
"""

import time
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
    Stimulus-adaptive tick scheduler with dt capping.

    Implements the tick speed regulation mechanism (spec §2):
    1. Track time since last stimulus
    2. Compute interval = clamp(time_since_stimulus, min, max)
    3. Optional EMA smoothing
    4. Cap physics dt to prevent blow-ups

    Example:
        >>> config = TickSpeedConfig(min_interval_ms=100, max_interval_s=60)
        >>> scheduler = AdaptiveTickScheduler(config)
        >>>
        >>> # On stimulus arrival
        >>> scheduler.on_stimulus()
        >>>
        >>> # Before each tick
        >>> interval_next = scheduler.compute_next_interval()
        >>> dt_used, was_capped = scheduler.compute_dt(interval_next)
        >>>
        >>> # Execute tick with dt_used
        >>> await tick(dt=dt_used)
        >>>
        >>> # Sleep until next tick
        >>> await asyncio.sleep(interval_next)
    """

    def __init__(self, config: TickSpeedConfig):
        """
        Initialize adaptive tick scheduler.

        Args:
            config: Tick speed configuration
        """
        self.config = config

        # Stimulus tracking
        self.last_stimulus_time: Optional[float] = None

        # Tick timing
        self.last_tick_time: float = time.time()

        # EMA state
        self.interval_prev: float = config.min_interval_ms / 1000.0

        logger.info(f"[TickSpeed] Initialized with min={config.min_interval_ms}ms, "
                   f"max={config.max_interval_s}s, dt_cap={config.dt_cap_s}s")

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

    def compute_next_interval(self) -> float:
        """
        Compute next tick interval (wall-clock sleep duration).

        Algorithm (spec §2.1):
        1. If no stimulus yet, use max_interval (dormant)
        2. Else compute time_since_last_stimulus
        3. Clamp to [min_interval, max_interval]
        4. Optional EMA smoothing to reduce oscillation

        Returns:
            Interval in seconds (wall-clock sleep time)

        Example:
            >>> scheduler.on_stimulus()
            >>> interval = scheduler.compute_next_interval()
            >>> # Shortly after stimulus: interval ≈ 0.1s (min)
            >>>
            >>> # Wait 30 seconds without stimulus
            >>> time.sleep(30)
            >>> interval = scheduler.compute_next_interval()
            >>> # Long after stimulus: interval ≈ 30s (clamped to max)
        """
        now = time.time()

        if self.last_stimulus_time is None:
            # No stimulus yet - dormant mode
            interval_raw = self.config.max_interval_s
        else:
            # Time since last stimulus
            time_since_stimulus = now - self.last_stimulus_time
            interval_raw = time_since_stimulus

        # Clamp to bounds [min, max]
        interval_clamped = max(
            self.config.min_interval_ms / 1000.0,  # min (convert ms to s)
            min(interval_raw, self.config.max_interval_s)  # max
        )

        # Optional EMA smoothing
        if self.config.enable_ema:
            # ema_t = β·v_t + (1-β)·ema_{t-1}
            interval_smoothed = (
                self.config.ema_beta * interval_clamped +
                (1 - self.config.ema_beta) * self.interval_prev
            )
            self.interval_prev = interval_smoothed

            logger.debug(f"[TickSpeed] interval: raw={interval_raw:.3f}s, "
                        f"clamped={interval_clamped:.3f}s, "
                        f"smoothed={interval_smoothed:.3f}s")

            return interval_smoothed
        else:
            logger.debug(f"[TickSpeed] interval: raw={interval_raw:.3f}s, "
                        f"clamped={interval_clamped:.3f}s (no EMA)")

            return interval_clamped

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
        Get scheduler diagnostics for observability.

        Returns:
            Dictionary with diagnostic fields:
            - last_stimulus_time: When last stimulus arrived (None if never)
            - time_since_stimulus: Seconds since last stimulus (None if never)
            - interval_prev: Previous EMA-smoothed interval
            - config: Current configuration

        Example:
            >>> diag = scheduler.get_diagnostics()
            >>> print(f"Time since stimulus: {diag['time_since_stimulus']:.1f}s")
        """
        now = time.time()

        return {
            'last_stimulus_time': self.last_stimulus_time,
            'time_since_stimulus': now - self.last_stimulus_time if self.last_stimulus_time else None,
            'interval_prev': self.interval_prev,
            'config': {
                'min_interval_ms': self.config.min_interval_ms,
                'max_interval_s': self.config.max_interval_s,
                'dt_cap_s': self.config.dt_cap_s,
                'ema_beta': self.config.ema_beta,
                'enable_ema': self.config.enable_ema
            }
        }
