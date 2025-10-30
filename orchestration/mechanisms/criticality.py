"""
Self-Organized Criticality Controller

Implements spectral radius (ρ) control to maintain edge-of-chaos dynamics.

Mechanism:
- Estimate ρ of effective propagation operator T = (1-δ)[(1-α)I + αP^T]
- Use P-controller (or PID) to adjust δ toward target ρ ≈ 1.0
- Optional dual-lever mode also tunes α

Observability:
- rho.global: Authoritative ρ estimate (power iteration, sampled)
- rho.proxy.branching: Cheap proxy (branching ratio, every frame)
- rho.var.window: Variance over rolling window
- safety_state: subcritical | critical | supercritical

Integration:
- Called once per frame before Phase 2 (Redistribution)
- Updates δ (and optionally α) in DiffusionContext
- Emits criticality metrics via event stream

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/foundations/criticality.md
"""

import numpy as np
import scipy.sparse as sp
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SafetyState(Enum):
    """Criticality safety classification."""
    DYING = "dying"              # ρ < 0.5, network collapsing
    SUBCRITICAL = "subcritical"  # 0.5 ≤ ρ < 0.8, below target
    CRITICAL = "critical"         # 0.8 ≤ ρ < 1.2, healthy zone
    SUPERCRITICAL = "supercritical"  # ρ ≥ 1.2, runaway


class CriticalityMode(Enum):
    """
    PR-E.7: Criticality Modes - Rich phenomenological classification combining ρ and C.

    Combines quantity (ρ) and quality (C) for richer state understanding.

    Modes:
    - SUBCRITICAL: ρ < 0.9, brain fog, ideas don't spread
    - FLOW: 0.9 ≤ ρ ≤ 1.1 and C ≥ 0.7, optimal coherent exploration
    - GENERATIVE_OVERFLOW: ρ > 1.1 and C ≥ 0.7, creative overflow with many good threads
    - CHAOTIC_RACING: ρ > 1.1 and C < 0.4, scattered, anxious, incoherent jumps
    - MIXED: ρ ∈ [0.9, 1.1] and C < 0.7, or ρ > 1.1 and 0.4 ≤ C < 0.7
    """
    SUBCRITICAL = "subcritical"             # ρ < 0.9
    FLOW = "flow"                           # 0.9 ≤ ρ ≤ 1.1, C ≥ 0.7
    GENERATIVE_OVERFLOW = "generative_overflow"  # ρ > 1.1, C ≥ 0.7
    CHAOTIC_RACING = "chaotic_racing"       # ρ > 1.1, C < 0.4
    MIXED = "mixed"                         # Other combinations


@dataclass
class CriticalityMetrics:
    """Output metrics from criticality controller."""
    rho_global: float              # Authoritative ρ estimate
    rho_proxy_branching: float     # Cheap branching ratio proxy
    rho_var_window: float          # Variance over window
    safety_state: SafetyState      # Classification
    delta_before: float            # δ before adjustment
    delta_after: float             # δ after adjustment
    alpha_before: float            # α before adjustment
    alpha_after: float             # α after adjustment
    controller_output: float       # Δδ from controller
    oscillation_index: float       # Sign change frequency


@dataclass
class ControllerConfig:
    """Configuration for criticality controller."""
    # Target parameters
    rho_target: float = 1.0        # Target spectral radius
    rho_tolerance: float = 0.1     # Acceptable deviation (±)

    # P-controller gains
    k_p: float = 0.05              # Proportional gain for δ adjustment

    # PID controller (optional, set to enable)
    enable_pid: bool = False
    k_i: float = 0.01              # Integral gain
    k_d: float = 0.02              # Derivative gain

    # Dual-lever (optional, set to enable)
    enable_dual_lever: bool = False
    k_alpha: float = 0.02          # Gain for α adjustment (opposite to δ)

    # Safety limits
    delta_min: float = 0.001       # Minimum decay (prevent zero)
    delta_max: float = 0.20        # Maximum decay (prevent over-damping)
    alpha_min: float = 0.05        # Minimum diffusion share
    alpha_max: float = 0.30        # Maximum diffusion share

    # Estimation parameters
    sample_rho_every_n_frames: int = 5  # Power iteration frequency
    power_iter_max_iters: int = 10      # Max iterations for convergence
    power_iter_tolerance: float = 1e-4  # Convergence threshold

    # Rolling window for variance tracking
    window_size: int = 20          # Frames to track for oscillation detection

    # Anti-windup (PID integral term)
    integral_max: float = 1.0


class CriticalityController:
    """
    Self-organized criticality controller using spectral radius feedback.

    Maintains system near ρ ≈ 1.0 (edge of chaos) by adjusting decay δ.

    Example:
        >>> config = ControllerConfig(k_p=0.05, enable_pid=False)
        >>> controller = CriticalityController(config)
        >>>
        >>> # Each frame:
        >>> metrics = controller.update(
        ...     P=transition_matrix,
        ...     current_delta=0.03,
        ...     current_alpha=0.1,
        ...     branching_ratio=1.2  # From BranchingRatioTracker
        ... )
        >>>
        >>> # Apply adjusted parameters
        >>> diffusion_ctx.delta = metrics.delta_after
        >>> diffusion_ctx.alpha = metrics.alpha_after
    """

    def __init__(self, config: Optional[ControllerConfig] = None):
        """
        Initialize criticality controller.

        Args:
            config: Controller configuration (defaults if None)
        """
        self.config = config or ControllerConfig()

        # State tracking
        self.frame_count = 0
        self.rho_history: deque = deque(maxlen=self.config.window_size)
        self.error_history: deque = deque(maxlen=self.config.window_size)

        # PID state
        self.integral_error = 0.0
        self.last_error = 0.0

        # Last known ρ (for frames when we don't sample)
        self.last_rho_global = 1.0

    def update(
        self,
        P: sp.csr_matrix,
        current_delta: float,
        current_alpha: float,
        branching_ratio: float,
        force_sample: bool = False
    ) -> CriticalityMetrics:
        """
        Update criticality controller for current frame.

        Args:
            P: Transition matrix (row-stochastic, N x N sparse)
            current_delta: Current decay factor
            current_alpha: Current diffusion share
            branching_ratio: Branching ratio from BranchingRatioTracker (cheap proxy)
            force_sample: Force power iteration this frame (default False)

        Returns:
            CriticalityMetrics with adjusted parameters and diagnostics
        """
        self.frame_count += 1

        # === Step 1: Estimate ρ ===
        # Use power iteration (sampled) for authoritative ρ
        should_sample = (
            force_sample or
            self.frame_count % self.config.sample_rho_every_n_frames == 0
        )

        matrix_degenerate = (
            P is None
            or (hasattr(P, "shape") and (P.shape[0] == 0 or P.shape[1] == 0))
            or (hasattr(P, "nnz") and getattr(P, "nnz") == 0)
        )
        rho_valid = not matrix_degenerate

        if rho_valid and should_sample:
            # Compute effective operator T = (1-δ)[(1-α)I + αP^T]
            rho_global = self._estimate_rho_power_iteration(
                P, current_delta, current_alpha
            )
            if not np.isfinite(rho_global):
                rho_valid = False
        elif not rho_valid:
            rho_global = self.config.rho_target
        else:
            # Use cached value between samples
            rho_global = self.last_rho_global

        if not rho_valid:
            rho_global = self.config.rho_target

        if rho_valid and should_sample:
            self.last_rho_global = rho_global
        elif not rho_valid:
            self.last_rho_global = rho_global

        # Track branching ratio as cheap proxy (every frame)
        rho_proxy_branching = branching_ratio

        # Add to history
        self.rho_history.append(rho_global)

        # Compute variance over window
        if len(self.rho_history) > 1:
            rho_var_window = float(np.var(list(self.rho_history)))
        else:
            rho_var_window = 0.0

        # === TRIPWIRE: Criticality Bounds ===
        # Check if ρ is within stable edge-of-chaos range
        # Tripwire triggers Safe Mode after 10 consecutive violations
        try:
            from orchestration.services.health.safe_mode import (
                get_safe_mode_controller, TripwireType
            )
            from orchestration.core.settings import settings

            safe_mode = get_safe_mode_controller()
            upper_bound = settings.TRIPWIRE_CRITICALITY_UPPER  # 1.3
            lower_bound = settings.TRIPWIRE_CRITICALITY_LOWER  # 0.7

            if rho_valid:
                if rho_global > upper_bound:
                    safe_mode.record_violation(
                        tripwire_type=TripwireType.CRITICALITY,
                        value=rho_global,
                        threshold=upper_bound,
                        message=f"Criticality too high (chaotic): ?={rho_global:.3f} > {upper_bound}"
                    )
                elif rho_global < lower_bound:
                    safe_mode.record_violation(
                        tripwire_type=TripwireType.CRITICALITY,
                        value=rho_global,
                        threshold=lower_bound,
                        message=f"Criticality too low (dying): ?={rho_global:.3f} < {lower_bound}"
                    )
                else:
                    safe_mode.record_compliance(TripwireType.CRITICALITY)
            else:
                safe_mode.record_compliance(TripwireType.CRITICALITY)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[TRIPWIRE] Criticality check failed: {e}")


        # === Step 2: Compute Control Error ===
        error = (rho_global - self.config.rho_target) if rho_valid else 0.0
        self.error_history.append(error)

        # === Step 3: Controller Output ===
        if not rho_valid:
            delta_adjustment = 0.0
        elif self.config.enable_pid:
            # PID controller
            delta_adjustment = self._compute_pid_output(error)
        else:
            # Simple P-controller
            delta_adjustment = self.config.k_p * error

        # === Step 4: Apply Adjustments ===
        # Adjust δ (primary lever)
        delta_new = current_delta + delta_adjustment
        delta_new = np.clip(delta_new, self.config.delta_min, self.config.delta_max)

        # Optionally adjust α (dual-lever mode)
        if self.config.enable_dual_lever:
            # Move α opposite to δ for faster convergence
            alpha_adjustment = -self.config.k_alpha * error
            alpha_new = current_alpha + alpha_adjustment
            alpha_new = np.clip(alpha_new, self.config.alpha_min, self.config.alpha_max)
        else:
            alpha_new = current_alpha

        # === Step 5: Classify Safety State ===
        safety_state = self._classify_safety_state(rho_global)

        # === Step 6: Compute Oscillation Index ===
        oscillation_index = self._compute_oscillation_index()

        # Update PID state
        self.last_error = error

        return CriticalityMetrics(
            rho_global=rho_global,
            rho_proxy_branching=rho_proxy_branching,
            rho_var_window=rho_var_window,
            safety_state=safety_state,
            delta_before=current_delta,
            delta_after=delta_new,
            alpha_before=current_alpha,
            alpha_after=alpha_new,
            controller_output=delta_adjustment,
            oscillation_index=oscillation_index
        )

    def _estimate_rho_power_iteration(
        self,
        P: sp.csr_matrix,
        delta: float,
        alpha: float
    ) -> float:
        """
        Estimate spectral radius using power iteration.

        Effective operator: T = (1-δ)[(1-α)I + αP^T]

        Power iteration finds dominant eigenvalue by repeatedly applying T:
        - Start with random vector v
        - Iterate: v_new = T @ v, normalize
        - λ_max ≈ ||T @ v|| / ||v|| when converged

        Args:
            P: Transition matrix (row-stochastic)
            delta: Decay factor
            alpha: Diffusion share

        Returns:
            ρ (spectral radius estimate)
        """
        # Handle None or empty matrix
        if P is None or (hasattr(P, 'size') and P.size == 0):
            return 0.0

        N = P.shape[0]
        if N == 0:
            return 0.0

        # Initialize with random vector
        v = np.random.rand(N)
        v = v / np.linalg.norm(v)

        # Power iteration
        for _ in range(self.config.power_iter_max_iters):
            # Apply effective operator T
            # T @ v = (1-δ)[(1-α)v + α(P^T @ v)]
            P_T_v = P.T.dot(v)
            T_v = (1 - delta) * ((1 - alpha) * v + alpha * P_T_v)

            # Estimate eigenvalue
            eigenvalue = np.dot(v, T_v)

            # Normalize
            norm = np.linalg.norm(T_v)
            if norm < 1e-10:
                # Converged to zero (subcritical collapse)
                return 0.0

            v_new = T_v / norm

            # Check convergence
            if np.linalg.norm(v_new - v) < self.config.power_iter_tolerance:
                break

            v = v_new

        # Final eigenvalue estimate
        rho = np.abs(eigenvalue)
        return float(rho)

    def _compute_pid_output(self, error: float) -> float:
        """
        Compute PID controller output.

        PID formula: u = k_p*e + k_i*∫e + k_d*de/dt

        Args:
            error: Current error (ρ - ρ_target)

        Returns:
            Control output (Δδ)
        """
        # Proportional term
        P_term = self.config.k_p * error

        # Integral term (with anti-windup)
        self.integral_error += error
        self.integral_error = np.clip(
            self.integral_error,
            -self.config.integral_max,
            self.config.integral_max
        )
        I_term = self.config.k_i * self.integral_error

        # Derivative term
        D_term = self.config.k_d * (error - self.last_error)

        return P_term + I_term + D_term

    def _classify_safety_state(self, rho: float) -> SafetyState:
        """
        Classify criticality safety state.

        Args:
            rho: Spectral radius

        Returns:
            SafetyState enum
        """
        if rho < 0.5:
            return SafetyState.DYING
        elif rho < 0.8:
            return SafetyState.SUBCRITICAL
        elif rho < 1.2:
            return SafetyState.CRITICAL
        else:
            return SafetyState.SUPERCRITICAL

    def _compute_oscillation_index(self) -> float:
        """
        Compute oscillation index (sign change frequency).

        High oscillation indicates controller instability.

        Returns:
            Oscillation index (0.0-1.0)
        """
        if len(self.error_history) < 2:
            return 0.0

        # Count sign changes
        sign_changes = 0
        for i in range(1, len(self.error_history)):
            if np.sign(self.error_history[i]) != np.sign(self.error_history[i-1]):
                sign_changes += 1

        # Normalize by window size
        return sign_changes / (len(self.error_history) - 1)

    def reset(self):
        """Reset controller state (for graph structure changes)."""
        self.rho_history.clear()
        self.error_history.clear()
        self.integral_error = 0.0
        self.last_error = 0.0
        self.last_rho_global = 1.0
        self.frame_count = 0


def estimate_rho_from_branching_ratio(branching_ratio: float) -> float:
    """
    Estimate spectral radius from branching ratio (cheap proxy).

    This is NOT as accurate as power iteration but useful for:
    - Per-frame monitoring (when power iteration is too expensive)
    - Quick health checks

    Heuristic mapping based on empirical observations:
    - B ≈ ρ for well-connected graphs
    - B tends to underestimate ρ in sparse graphs

    Args:
        branching_ratio: σ = activated_next / activated_this

    Returns:
        ρ estimate (proxy)
    """
    # Simple linear approximation
    # Could be refined with graph-specific calibration
    return branching_ratio


def compute_threshold_multiplier(safety_state: SafetyState) -> float:
    """
    Compute small threshold multiplier based on safety state.

    Per spec: "We still allow a small threshold multiplier f_ρ to gently
    tighten/loosen activation checks during excursions; the primary lever
    remains δ."

    Args:
        safety_state: Current criticality state

    Returns:
        Threshold multiplier (typically 0.9-1.1)
    """
    if safety_state == SafetyState.DYING:
        return 0.85  # Lower thresholds to encourage activation
    elif safety_state == SafetyState.SUBCRITICAL:
        return 0.95
    elif safety_state == SafetyState.CRITICAL:
        return 1.0   # Healthy zone, no adjustment
    elif safety_state == SafetyState.SUPERCRITICAL:
        return 1.1   # Raise thresholds to dampen runaway
    else:
        return 1.0


# ============================================================================
# PR-E.7: Criticality Modes (Rich Phenomenological Classification)
# ============================================================================

def classify_criticality_mode(rho: float, coherence: Optional[float] = None) -> CriticalityMode:
    """
    PR-E.7: Classify system state into phenomenological modes based on (ρ, C).

    Combines quantity (ρ) and quality (C) for richer state understanding beyond
    simple safety states.

    Classification Rules:
    - SUBCRITICAL: ρ < 0.9 (any C) - Brain fog, ideas don't spread
    - FLOW: 0.9 ≤ ρ ≤ 1.1 and C ≥ 0.7 - Optimal: coherent exploration
    - GENERATIVE_OVERFLOW: ρ > 1.1 and C ≥ 0.7 - Creative overflow, many good threads
    - CHAOTIC_RACING: ρ > 1.1 and C < 0.4 - Scattered, anxious, incoherent jumps
    - MIXED: Other combinations (in-between states)

    Args:
        rho: Spectral radius (quantity of activation spread)
        coherence: Coherence metric C ∈ [0,1] (quality of activation spread)
                   If None, falls back to ρ-only classification

    Returns:
        CriticalityMode classification

    Examples:
        >>> classify_criticality_mode(0.8)  # Low ρ
        CriticalityMode.SUBCRITICAL

        >>> classify_criticality_mode(1.0, 0.8)  # Balanced, high quality
        CriticalityMode.FLOW

        >>> classify_criticality_mode(1.2, 0.8)  # High ρ, high quality
        CriticalityMode.GENERATIVE_OVERFLOW

        >>> classify_criticality_mode(1.3, 0.2)  # High ρ, low quality
        CriticalityMode.CHAOTIC_RACING
    """
    # If no coherence available, fall back to ρ-only classification
    if coherence is None:
        if rho < 0.9:
            return CriticalityMode.SUBCRITICAL
        elif 0.9 <= rho <= 1.1:
            return CriticalityMode.MIXED  # Can't determine without C
        else:  # rho > 1.1
            return CriticalityMode.MIXED  # Can't distinguish overflow vs chaos without C

    # Full (ρ, C) classification
    if rho < 0.9:
        # Subcritical regardless of coherence
        return CriticalityMode.SUBCRITICAL

    elif 0.9 <= rho <= 1.1:
        # Critical range - distinguish by coherence
        if coherence >= 0.7:
            return CriticalityMode.FLOW  # Optimal state
        else:
            return CriticalityMode.MIXED  # Sub-optimal quality

    else:  # rho > 1.1
        # Supercritical - distinguish overflow from chaos
        if coherence >= 0.7:
            return CriticalityMode.GENERATIVE_OVERFLOW  # High quality overflow
        elif coherence < 0.4:
            return CriticalityMode.CHAOTIC_RACING  # Low quality thrashing
        else:  # 0.4 ≤ coherence < 0.7
            return CriticalityMode.MIXED  # Transitional state


def get_mode_phenomenology(mode: CriticalityMode) -> str:
    """
    Get phenomenological description of a criticality mode.

    Args:
        mode: Criticality mode

    Returns:
        Human-readable description of the mode's phenomenology
    """
    descriptions = {
        CriticalityMode.SUBCRITICAL: "Brain fog, ideas don't spread, sluggish thinking",
        CriticalityMode.FLOW: "Optimal: coherent exploration, productive thinking, in the zone",
        CriticalityMode.GENERATIVE_OVERFLOW: "Creative overflow with many good threads, abundant but manageable",
        CriticalityMode.CHAOTIC_RACING: "Scattered, anxious, incoherent jumps, racing thoughts",
        CriticalityMode.MIXED: "Transitional or mixed state, neither clearly productive nor clearly problematic",
    }
    return descriptions.get(mode, "Unknown mode")


def get_controller_response(mode: CriticalityMode) -> str:
    """
    Get recommended controller response for a criticality mode.

    Args:
        mode: Criticality mode

    Returns:
        Recommended controller action
    """
    responses = {
        CriticalityMode.SUBCRITICAL: "Reduce δ (decay), increase α (diffusion) slightly to encourage spread",
        CriticalityMode.FLOW: "Maintain current parameters - optimal state",
        CriticalityMode.GENERATIVE_OVERFLOW: "Slight δ increase, monitor for transition to chaos",
        CriticalityMode.CHAOTIC_RACING: "Aggressive δ increase + small threshold multiplier to dampen chaos",
        CriticalityMode.MIXED: "Gradual adjustment toward nearest stable mode (FLOW or SUBCRITICAL)",
    }
    return responses.get(mode, "No specific action")


# ============================================================================
# PR-E.8: Task-Adaptive ρ Targets (Context-Aware Control)
# ============================================================================

class TaskContext(Enum):
    """
    PR-E.8: Task context classification for adaptive ρ targeting.

    Different tasks benefit from different criticality levels:
    - EXPLORE: Slightly supercritical to encourage wide activation spread
    - IMPLEMENT: Balanced critical for focused but adaptable work
    - CONSOLIDATE: Subcritical to favor settling and memory formation
    - REST: Low activation for recovery and cleanup
    - UNKNOWN: Default when context unclear
    """
    EXPLORE = "explore"
    IMPLEMENT = "implement"
    CONSOLIDATE = "consolidate"
    REST = "rest"
    UNKNOWN = "unknown"


@dataclass
class TaskContextSignals:
    """Signals used for task context inference."""
    # Goal type signals
    exploration_goals_active: int = 0
    implementation_tasks_active: int = 0
    memory_formation_active: bool = False

    # Entity activity signals
    active_entity_count: int = 0
    entity_diversity: float = 0.0  # Ratio of unique entity types

    # Flip rate (node threshold crossings)
    recent_flip_rate: float = 0.0  # Flips per frame, averaged

    # Working memory stability
    wm_stable_frames: int = 0  # Frames with same WM composition

    # Low activation period
    low_rho_frames: int = 0  # Consecutive frames with ρ < 0.9


class TaskContextInferrer:
    """
    PR-E.8: Infer task context from system signals with hysteresis.

    Prevents rapid switching by requiring N frames of consistent evidence
    before transitioning to a new context.

    Usage:
        inferrer = TaskContextInferrer(hysteresis_frames=5)

        # Each frame:
        signals = TaskContextSignals(
            exploration_goals_active=2,
            active_entity_count=5,
            ...
        )
        context = inferrer.infer(signals, current_rho=1.05)

        # Get adaptive target
        target_rho = inferrer.get_target_rho(context)
    """

    def __init__(self, hysteresis_frames: int = 5):
        """
        Initialize task context inferrer.

        Args:
            hysteresis_frames: Number of frames of consistent evidence required
                               before switching context
        """
        self.hysteresis_frames = hysteresis_frames

        # Current state
        self.current_context = TaskContext.UNKNOWN
        self.candidate_context = TaskContext.UNKNOWN
        self.candidate_frames = 0  # Frames supporting candidate

        # Load targets from settings (if available)
        try:
            from orchestration.core.settings import settings
            self.targets = getattr(settings, 'TASK_CONTEXT_TARGETS', {
                "explore": 1.10,
                "implement": 1.00,
                "consolidate": 0.95,
                "rest": 0.80,
                "unknown": 1.0
            })
            self.tolerances = getattr(settings, 'TASK_CONTEXT_TOLERANCES', {
                "explore": 0.15,
                "implement": 0.08,
                "consolidate": 0.10,
                "rest": 0.20,
                "unknown": 0.10
            })
        except ImportError:
            # Fallback defaults if settings unavailable
            self.targets = {
                "explore": 1.10,
                "implement": 1.00,
                "consolidate": 0.95,
                "rest": 0.80,
                "unknown": 1.0
            }
            self.tolerances = {
                "explore": 0.15,
                "implement": 0.08,
                "consolidate": 0.10,
                "rest": 0.20,
                "unknown": 0.10
            }

        logger.info(f"[TaskContextInferrer] Initialized with hysteresis={hysteresis_frames}")

    def infer(self, signals: TaskContextSignals, current_rho: float) -> TaskContext:
        """
        Infer task context from signals with hysteresis.

        Args:
            signals: System signals for context inference
            current_rho: Current spectral radius

        Returns:
            Inferred task context (stable via hysteresis)
        """
        # Infer candidate context from signals
        new_candidate = self._classify_context(signals, current_rho)

        # Hysteresis logic
        if new_candidate == self.candidate_context:
            # Same candidate as before - increment evidence
            self.candidate_frames += 1
        else:
            # New candidate - reset hysteresis counter
            self.candidate_context = new_candidate
            self.candidate_frames = 1

        # If we have enough evidence, switch to candidate
        if self.candidate_frames >= self.hysteresis_frames:
            if self.current_context != new_candidate:
                logger.info(
                    f"[TaskContext] Transition: {self.current_context.value} → {new_candidate.value} "
                    f"(after {self.candidate_frames} frames)"
                )
                self.current_context = new_candidate

        return self.current_context

    def _classify_context(self, signals: TaskContextSignals, current_rho: float) -> TaskContext:
        """
        Classify task context from signals (no hysteresis).

        Priority order (first match wins):
        1. REST - Low activation sustained
        2. CONSOLIDATE - Memory formation or stable WM
        3. EXPLORE - Exploration goals or high entity diversity
        4. IMPLEMENT - Implementation tasks or high flip rate
        5. UNKNOWN - Default fallback

        Args:
            signals: System signals
            current_rho: Current spectral radius

        Returns:
            Classified context
        """
        # 1. REST: Low activation for extended period
        if signals.low_rho_frames >= 10:  # ρ < 0.9 for 10+ frames
            return TaskContext.REST

        # 2. CONSOLIDATE: Memory formation or stable WM
        if signals.memory_formation_active or signals.wm_stable_frames >= 5:
            return TaskContext.CONSOLIDATE

        # 3. EXPLORE: Exploration goals or high entity diversity
        if signals.exploration_goals_active > 0 or signals.entity_diversity > 0.6:
            return TaskContext.EXPLORE

        # 4. IMPLEMENT: Implementation tasks or high flip rate
        if signals.implementation_tasks_active > 0 or signals.recent_flip_rate > 0.3:
            return TaskContext.IMPLEMENT

        # 5. Default fallback
        return TaskContext.UNKNOWN

    def get_target_rho(self, context: Optional[TaskContext] = None) -> float:
        """
        Get target ρ for a given context.

        Args:
            context: Task context (uses current if None)

        Returns:
            Target ρ value
        """
        if context is None:
            context = self.current_context

        return self.targets.get(context.value, 1.0)

    def get_tolerance(self, context: Optional[TaskContext] = None) -> float:
        """
        Get tolerance for a given context.

        Args:
            context: Task context (uses current if None)

        Returns:
            Tolerance (±ρ acceptable deviation)
        """
        if context is None:
            context = self.current_context

        return self.tolerances.get(context.value, 0.10)

    def reset(self):
        """Reset inferrer state (e.g., after major context switch)."""
        self.current_context = TaskContext.UNKNOWN
        self.candidate_context = TaskContext.UNKNOWN
        self.candidate_frames = 0
        logger.info("[TaskContextInferrer] State reset")
