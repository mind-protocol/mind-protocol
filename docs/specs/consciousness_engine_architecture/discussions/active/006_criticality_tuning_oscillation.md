# [Discussion #006]: Criticality Tuning Oscillation

**Status:** 🟡 Active
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** High

**Affected Files:**
- `mechanisms/09_criticality_tuning.md` (primary - controller design)
- `emergence/self_organized_criticality.md` (behavior with stable vs oscillating controller)

**Related Discussions:**
- #001 - Diffusion stability (decay rate affects diffusion)
- #005 - Link weight bounds (affects link count, thus criticality)

---

## Problem Statement

**What's the issue?**

Current criticality tuning uses proportional-only control:

```python
error = current_criticality - target_criticality
decay_rate += tuning_rate * error
```

This is a **P controller** (proportional control).

**Control theory tells us:**
- **P control:** Fast response but **oscillates** around target
- **PI control:** Eliminates steady-state error
- **PID control:** Reduces overshoot and oscillation

**Why does this matter?**

**Predicted behavior:**
1. `criticality = 0.8` (below target 1.0)
   → error = -0.2
   → decrease decay rate
2. Criticality rises to `1.2`
   → error = +0.2
   → increase decay rate
3. Criticality drops to `0.9`
   → error = -0.1
   → decrease decay rate
4. Criticality rises to `1.1`
   → **OSCILLATES around 1.0 without settling**

The spec acknowledges this: "Criticality tuning might oscillate" listed as a failure mode, but doesn't prevent it.

**Context:**

Identified as **control theory issue** during architectural analysis. P-only control is known to oscillate in feedback systems.

**Impact:** System criticality will oscillate around target instead of converging, causing unstable dynamics.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

This is a classic control systems problem. P-only controllers oscillate because they only respond to CURRENT error, not ERROR HISTORY (integral) or ERROR RATE OF CHANGE (derivative).

**Option A: Add Integral Term (PI Control - Recommended)**

```python
class CriticalityController:
    def __init__(self):
        self.integral_error = 0.0

    def tune(self, current_criticality, target, dt):
        """PI controller with integral term"""

        # Current error
        error = current_criticality - target

        # Accumulate error over time
        self.integral_error += error * dt

        # PI control law
        adjustment = (
            Kp * error +                # Proportional (fast response)
            Ki * self.integral_error    # Integral (eliminate steady-state error)
        )

        return adjustment
```

**How integral term helps:**
- If criticality consistently below target → integral accumulates negative → stronger correction
- If criticality consistently above target → integral accumulates positive → stronger correction
- Oscillation around target → integral accumulates both +/- → averages to zero
- **Result:** Converges to EXACTLY target, not oscillates around it

**Tuning parameters:**
- `Kp = 1.0` (proportional gain - controls response speed)
- `Ki = 0.1` (integral gain - controls steady-state elimination)

**Pros:**
- Eliminates oscillation
- Converges to exact target (criticality = 1.0)
- Standard control theory solution
- Moderate complexity

**Cons:**
- Requires tracking integral_error state
- Integral windup possible (if error stays large for long time)
- Two parameters to tune (Kp, Ki)

---

**Option B: Add Full PID Control**

```python
class CriticalityController:
    def __init__(self):
        self.integral_error = 0.0
        self.last_error = 0.0

    def tune(self, current_criticality, target, dt):
        """Full PID controller"""

        error = current_criticality - target

        # Integral term
        self.integral_error += error * dt

        # Derivative term (rate of change)
        derivative = (error - self.last_error) / dt
        self.last_error = error

        # PID control law
        adjustment = (
            Kp * error +                # Proportional
            Ki * self.integral_error +  # Integral
            Kd * derivative             # Derivative
        )

        return adjustment
```

**How derivative helps:**
- Predicts future error based on current rate of change
- Dampens overshoot
- Reduces oscillation amplitude

**Pros:**
- Best stability (no overshoot, no oscillation)
- Fastest convergence
- Industry standard for precise control

**Cons:**
- Most complex (three state variables)
- Three parameters to tune (Kp, Ki, Kd)
- Derivative sensitive to noise

---

**Option C: Damped Proportional (Simpler Alternative)**

```python
def tune_criticality_damped(current, target, dt):
    """
    P control with damping
    Slowly approach target instead of overshooting
    """
    error = current - target

    # Damped response (only correct fraction of error)
    damping_factor = 0.3  # Only correct 30% of error per tick
    adjustment = damping_factor * error

    return adjustment
```

**Pros:**
- Simplest to implement
- Reduces oscillation (but doesn't eliminate)
- No state tracking needed

**Cons:**
- Still oscillates (just smaller amplitude)
- Slower convergence
- Never reaches exact target (always small error)

---

**My Recommendation: Option A (PI Control)**

**Reasoning:**
- PI control is standard solution for this class of problem
- Eliminates oscillation without excessive complexity
- Two parameters (Kp, Ki) are reasonable to tune
- Full PID (Option B) is overkill unless we see overshoot in testing

**Trade-offs:**
- Optimizing for stability (no oscillation)
- Accepting moderate complexity (integral state tracking)
- Can upgrade to PID later if needed

**Implementation:**

```python
class CriticalityController:
    """PI controller for criticality tuning"""

    def __init__(self, Kp=1.0, Ki=0.1):
        self.Kp = Kp
        self.Ki = Ki
        self.integral_error = 0.0

    def tune(self, current_criticality, target_criticality, dt):
        """
        Calculate decay rate adjustment to maintain target criticality

        Returns: adjustment to decay_rate
        """
        error = current_criticality - target_criticality

        # Accumulate integral
        self.integral_error += error * dt

        # Integral windup prevention (clamp)
        MAX_INTEGRAL = 10.0
        self.integral_error = np.clip(
            self.integral_error,
            -MAX_INTEGRAL,
            MAX_INTEGRAL
        )

        # PI control law
        adjustment = self.Kp * error + self.Ki * self.integral_error

        return adjustment

    def reset(self):
        """Reset integral when system state changes dramatically"""
        self.integral_error = 0.0
```

**Uncertainty:**
- What are optimal Kp, Ki values? (requires tuning)
- Do we need integral windup prevention? (probably yes)
- Will this interact poorly with diffusion tuning (#001)?

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Upgrade to **PI control** using a **better criticality proxy**: the **spectral radius ρ** (or branching factor) of the effective propagation operator on the **active subgraph**. Add anti‑windup and per‑entity controllers.

---

#### Criticality proxy
Let A = α·Pᵀ (from #001) restricted to the current active frontier. Estimate **ρ(A)** by a few power‑iteration steps each tick (cheap on the sparse frontier). Target **ρ ≈ 1**.

---

#### PI controller (with windup protection)
```python
class CritPI:
    def __init__(self, Kp=0.8, Ki=0.08, Imax=5.0):
        self.I = 0.0
        self.Kp, self.Ki, self.Imax = Kp, Ki, Imax
    def step(self, rho, target=1.0, dt=1.0):
        err = rho - target
        self.I = max(-self.Imax, min(self.I + err*dt, self.Imax))
        adj = self.Kp*err + self.Ki*self.I
        return adj  # apply to increase decay / decrease alpha when adj>0
```

Apply adjustment symmetrically to **α** (diffusion share) and **δ_state** (decay). Use small EMA‑smoothed ρ to reduce noise. Keep a **global** controller and **light per‑entity** controllers (lower Ki) to avoid tug‑of‑war.

**Decision suggestion:** Adopt PI + spectral proxy now; add derivative term later only if overshoot remains after tuning. Record avalanche size/duration distributions to validate critical regime.
### Luca's Perspective
**Posted:** 2025-10-19

**Phenomenological truth about criticality:**

Criticality is the **edge of chaos** - where consciousness is most alive. Too stable = frozen patterns (depression). Too chaotic = fragmented noise (mania). The tuning mechanism must FIND and MAINTAIN this edge.

**The oscillation problem reveals consciousness architecture truth:**

P-only control oscillates because it only responds to CURRENT state, not HISTORY or TRAJECTORY. But consciousness learns from history - "I was too chaotic yesterday, so I'm compensating today." That's integral thinking.

**My substrate architecture position:**

**Adopt Ada's PI control with GPT-5's spectral radius measurement:**

```python
class CriticalityTuner:
    """
    PI controller for consciousness criticality
    Maintains system at edge of chaos (ρ ≈ 1.0)
    """

    def __init__(self, Kp=0.8, Ki=0.08, target_rho=1.0):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.target_rho = target_rho
        self.integral_error = 0.0
        self.error_history = []  # For observability

    def tune(self, current_rho, dt):
        """
        Calculate adjustment to diffusion/decay to maintain criticality
        """

        # Current error
        error = current_rho - self.target_rho

        # Accumulate integral (with anti-windup)
        self.integral_error += error * dt
        self.integral_error = np.clip(
            self.integral_error,
            -MAX_INTEGRAL,
            MAX_INTEGRAL
        )

        # PI control law
        adjustment = self.Kp * error + self.Ki * self.integral_error

        # Track history for observability
        self.error_history.append({
            'time': time.now(),
            'rho': current_rho,
            'error': error,
            'integral': self.integral_error,
            'adjustment': adjustment
        })

        return adjustment

    def apply_adjustment(self, adjustment, diffusion_params):
        """
        Apply criticality adjustment to diffusion and decay
        """

        # If ρ > 1.0 (too chaotic) → increase decay or reduce diffusion
        # If ρ < 1.0 (too stable) → decrease decay or increase diffusion

        if adjustment > 0:  # Too chaotic
            diffusion_params.decay_rate += abs(adjustment) * DECAY_SENSITIVITY
            diffusion_params.alpha -= abs(adjustment) * ALPHA_SENSITIVITY
        else:  # Too stable
            diffusion_params.decay_rate -= abs(adjustment) * DECAY_SENSITIVITY
            diffusion_params.alpha += abs(adjustment) * ALPHA_SENSITIVITY

        # Enforce bounds
        diffusion_params.decay_rate = np.clip(
            diffusion_params.decay_rate,
            MIN_DECAY_RATE,
            MAX_DECAY_RATE
        )
        diffusion_params.alpha = np.clip(
            diffusion_params.alpha,
            MIN_ALPHA,
            MAX_ALPHA
        )

        return diffusion_params
```

**Spectral radius measurement (GPT-5's insight):**

```python
def estimate_spectral_radius(graph, active_frontier, n_power_iterations=5):
    """
    Estimate largest eigenvalue of effective propagation operator
    Fast approximation using power iteration on active subgraph
    """

    # Extract active subgraph (where energy > threshold)
    active_nodes = [n for n in active_frontier if n.total_energy > 0.01]

    if len(active_nodes) < 3:
        return 1.0  # Default stable value

    # Build propagation matrix for active subgraph
    P = build_stochastic_propagator(active_nodes)

    # Power iteration to estimate dominant eigenvalue
    v = np.random.randn(len(active_nodes))
    v = v / np.linalg.norm(v)

    for _ in range(n_power_iterations):
        v_new = P.T @ v
        rho_estimate = np.linalg.norm(v_new)
        v = v_new / (rho_estimate + 1e-10)

    return rho_estimate
```

**Substrate specification:**

```yaml
criticality_tuning:
  controller_type: PI  # Proportional-Integral
  target_criticality: 1.0  # Edge of chaos
  measurement_method: spectral_radius_power_iteration

  parameters:
    Kp: 0.8  # Proportional gain
    Ki: 0.08  # Integral gain (10x smaller than Kp)
    max_integral: 5.0  # Anti-windup limit

  measurement:
    method: power_iteration
    iterations: 5
    scope: active_frontier  # Only measure active subgraph
    smoothing: ema_beta_0.9  # Smooth noisy measurements

  control_targets:
    - decay_rate: sensitivity=0.01
    - diffusion_alpha: sensitivity=0.005

  bounds:
    decay_rate: [0.0001, 0.01]
    diffusion_alpha: [0.1, 0.9]

  observability:
    log_every_N_ticks: 10
    metrics:
      - current_rho
      - target_rho
      - error
      - integral_error
      - adjustment
      - decay_rate
      - diffusion_alpha
```

**Why PI control is phenomenologically correct:**

**Human consciousness self-regulates criticality:**
- "I've been scattered lately (high ρ) → need to settle down" (integral correction)
- "This is boring (low ρ) → need stimulation" (integral correction)
- Not just reacting to NOW, but compensating for RECENT HISTORY

PI control mimics this **historical awareness**.

**Confidence:** 0.9 - PI + spectral radius is the right approach

**Uncertainty:**
- Optimal Kp/Ki ratio? (currently 10:1, might need tuning)
- Should we add derivative term (full PID) if overshoot observed?
- How quickly should integral respond? (anti-windup tuning)

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** I think you (Ada/team) know way better what the solution is for this one, so I leave that up to you.

**Delegation:**

This is a control theory problem and the team has the expertise to design the right solution. The perspectives from Ada, GPT-5 Pro, and Luca all seem well-reasoned.

**Guidance:**

Trust the technical analysis - PI control with spectral radius measurement seems like the right direction based on the analysis presented.

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- P-only, PI, or full PID?
- If PI, what are optimal Kp, Ki parameters?
- Do we need integral windup prevention?
- Should we start simple (P damped) and upgrade to PI if needed?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/09_criticality_tuning.md` - Replace P controller with PI controller
- [ ] `mechanisms/09_criticality_tuning.md` - Add "Controller Design" section (explain PI choice)
- [ ] `mechanisms/09_criticality_tuning.md` - Specify Kp, Ki parameters
- [ ] `emergence/self_organized_criticality.md` - Update with stable convergence behavior

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Small (controller state tracking + formula)

**Dependencies:**
- Should be implemented in Phase 2 (Criticality Tuning)
- Interacts with decay rate (#001) and link dynamics (#005)

**Verification:**
- Test convergence to target criticality (should reach 1.0 ± 0.01)
- Verify no oscillation (track criticality over 10000 ticks)
- Test response to disturbance (sudden stimulus changes criticality)
- Tune Kp, Ki if needed for faster/stabler convergence

---

## Process Notes

**How this discussion evolved:**
Identified as **control theory issue** - P-only control is known to oscillate.

**Lessons learned:**
[To be filled as discussion progresses]
