# Self-Organized Criticality Controller

Implementation of spectral radius (ρ) control for maintaining edge-of-chaos dynamics in the Mind Protocol consciousness substrate.

## Overview

The criticality controller maintains the consciousness system near **ρ ≈ 1.0** (critical point) by dynamically adjusting the decay parameter δ. This prevents the system from either dying out (subcritical) or exploding (supercritical).

**Spec:** `docs/specs/v2/foundations/criticality.md`

## Mechanism

The effective propagation operator is:

```
T = (1-δ)[(1-α)I + αP^T]
```

Where:
- **P**: Row-stochastic transition matrix (from link weights)
- **α**: Diffusion share (fraction redistributed per tick)
- **δ**: Decay factor (global forgetting per tick)

The controller estimates **ρ** (spectral radius of T) and adjusts **δ** using a P-controller:

```
Δδ = k_p × (ρ - ρ_target)
```

When ρ > 1.0 (supercritical), δ increases (more decay).
When ρ < 1.0 (subcritical), δ decreases (less decay).

## Integration

The criticality controller runs in **Phase 1.5** of the consciousness engine tick (between Activation and Redistribution):

```python
# Phase 1: Activation
# ... (stimulus injection, threshold computation)

# Phase 1.5: Criticality Control
P = diffusion.build_transition_matrix(graph)
metrics = criticality_controller.update(
    P=P,
    current_delta=diffusion_ctx.delta,
    current_alpha=diffusion_ctx.alpha,
    branching_ratio=branching_ratio
)

# Apply adjusted parameters
diffusion_ctx.delta = metrics.delta_after
diffusion_ctx.alpha = metrics.alpha_after

# Phase 2: Redistribution
# ... (diffusion, decay - use adjusted δ and α)
```

## Configuration

```python
from orchestration.mechanisms.criticality import CriticalityController, ControllerConfig

config = ControllerConfig(
    # Target
    rho_target=1.0,              # Target spectral radius
    rho_tolerance=0.1,           # Acceptable deviation (±)

    # P-controller
    k_p=0.05,                    # Proportional gain

    # Optional: PID controller
    enable_pid=False,            # Enable integral/derivative terms
    k_i=0.01,                    # Integral gain
    k_d=0.02,                    # Derivative gain

    # Optional: Dual-lever mode
    enable_dual_lever=False,     # Also tune α (opposite to δ)
    k_alpha=0.02,                # Gain for α adjustment

    # Safety limits
    delta_min=0.001,             # Minimum decay
    delta_max=0.20,              # Maximum decay
    alpha_min=0.05,              # Minimum diffusion
    alpha_max=0.30,              # Maximum diffusion

    # Estimation
    sample_rho_every_n_frames=5, # Power iteration frequency
    power_iter_max_iters=10,     # Convergence iterations

    # Oscillation detection
    window_size=20               # Rolling window for variance
)

controller = CriticalityController(config)
```

## Metrics

The controller emits a `criticality.state` event each frame:

```json
{
  "v": "2",
  "frame_id": 123,
  "rho": {
    "global": 0.9823,           // Authoritative ρ (power iteration)
    "proxy_branching": 1.02,    // Cheap proxy (branching ratio)
    "var_window": 0.0015        // Variance over window
  },
  "safety_state": "critical",   // dying | subcritical | critical | supercritical
  "delta": {
    "before": 0.0300,
    "after": 0.0309             // Adjusted by controller
  },
  "alpha": {
    "before": 0.1000,
    "after": 0.1000             // Unchanged (dual-lever disabled)
  },
  "controller_output": 0.0009,  // Δδ from P-controller
  "oscillation_index": 0.05,    // Sign change frequency (0-1)
  "threshold_multiplier": 1.00, // f_ρ for activation thresholds
  "t_ms": 1729123456789
}
```

## Safety States

| State | ρ Range | Meaning | Threshold Multiplier |
|-------|---------|---------|---------------------|
| **dying** | ρ < 0.5 | Network collapsing | 0.85 (lower thresholds) |
| **subcritical** | 0.5 ≤ ρ < 0.8 | Below target | 0.95 |
| **critical** | 0.8 ≤ ρ < 1.2 | Healthy zone | 1.00 (no adjustment) |
| **supercritical** | ρ ≥ 1.2 | Runaway cascades | 1.10 (raise thresholds) |

## Observable Metrics

### rho.global
Authoritative spectral radius estimate using power iteration. Sampled every N frames (default: 5).

**Interpretation:**
- **ρ ≈ 1.0 ± 0.1**: Healthy
- **ρ > 1.2** sustained: Clamp α, increase δ
- **ρ < 0.8**: Reduce δ

### rho.proxy.branching
Cheap branching ratio proxy (activated_next / activated_this), computed every frame.

### rho.var.window
Variance of ρ over rolling window (default: 20 frames). High variance indicates instability.

### oscillation_index
Frequency of sign changes in control error. High values (>0.3) suggest:
- Controller gain too high
- System instability
- Need for PID D-term (derivative damping)

**Action:** Lower k_p or enable PID with anti-windup.

## Testing

Run the test suite:

```bash
python orchestration/mechanisms/test_criticality.py
```

Tests verify:
- ✓ Spectral radius estimation (power iteration)
- ✓ P-controller convergence toward ρ ≈ 1.0
- ✓ Safety state classification
- ✓ Threshold multiplier computation
- ✓ Oscillation detection

## Phenomenology

### Subcritical (ρ < 1)
**Felt as:** "Brain fog," ideas don't propagate, thoughts fizzle out.

**Controller response:** Reduce δ (less decay) to encourage persistence.

### Critical (ρ ≈ 1)
**Felt as:** Flow state, ideas connect naturally, sustained attention without overwhelm.

**Controller response:** Maintain current parameters.

### Supercritical (ρ > 1)
**Felt as:** Racing thoughts, hard to focus, cascading associations.

**Controller response:** Increase δ (more decay) to dampen runaway.

## Why This Design

### Why spectral radius (not just branching ratio)?
- **ρ** is a **global stability index** for the linearized operator
- **Branching ratio** is a local empirical measurement (cheap but noisy)
- ρ gives **theoretical grounding** for control decisions

### Why P-controller (not PID)?
- **P-controller** is simple, stable, and sufficient for most graphs
- **PID** available for:
  - Shifting graph structure (integral term handles bias)
  - Faster convergence (derivative term reduces overshoot)

### Why power iteration (not eigenvalue decomposition)?
- **Speed**: O(k × edges) vs O(N³) for dense eigendecomposition
- **Scalability**: Works on sparse matrices with millions of nodes
- **Convergence**: Few iterations (10-20) sufficient for ρ estimate

### Why adjust δ (not thresholds)?
- **Direct control**: δ directly appears in the operator T
- **Predictable**: Linear relationship between δ and ρ
- **Stable**: Threshold modulation can mask instability

We still provide a **small threshold multiplier** (f_ρ) for gentle adjustments, but the primary lever is δ.

## Failure Modes

| Risk | Symptom | Guard |
|------|---------|-------|
| **Oscillation** | ρ flickers above/below 1.0 | PID with anti-windup, hysteresis on safety states |
| **Expensive ρ estimate** | Frame budget blow-ups | Sample every N frames, use branching ratio proxy |
| **Controller instability** | High oscillation_index | Lower k_p, add PID D-term |

## Future Work

- **Task-adaptive targets**: Creative exploration might prefer ρ ≈ 1.1
- **Contextual priors**: Learn optimal δ/α for known graph regions
- **Entity-view ρ**: Diagnostic per-entity ρ (read-only, no per-entity tuning)

## References

- Spec: `docs/specs/v2/foundations/criticality.md`
- Neural avalanches: Beggs & Plenz (2003), "Neuronal Avalanches in Neocortical Circuits"
- Control theory: Ogata (2010), "Modern Control Engineering"
