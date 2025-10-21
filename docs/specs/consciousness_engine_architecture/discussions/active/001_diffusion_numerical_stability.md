# [Discussion #001]: Diffusion Numerical Stability

**Status:** 🔴 Blocking
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Critical

**Affected Files:**
- `mechanisms/05_energy_diffusion.md` (primary - formula replacement)
- `emergence/spreading_activation.md` (secondary - behavior changes)
- `mechanisms/01_core_dynamics.md` (minor - stability guarantees reference)

**Related Discussions:**
- #002 - Link creation (both affect graph dynamics)
- #006 - Criticality tuning (decay rate interacts with diffusion)

---

## Problem Statement

**What's the issue?**

The current diffusion formula uses forward Euler integration:

```python
transfer = entity_energy * link.weight * diffusion_rate * tick_duration
node.energy[entity] -= transfer
target.energy[entity] += transfer
```

This is **conditionally stable** - it only remains stable if `diffusion_rate × tick_duration < stability_threshold`. For large tick durations (dormant system) or high diffusion rates, the system will exhibit numerical instability: energy oscillation or exponential growth.

**Why does this matter?**

When the system is dormant for 1 hour, `tick_duration = 3600s`. Even with a modest `diffusion_rate = 0.1`:
- Multiplier = `0.1 × 3600 = 360`
- Energy transfers become enormous
- Numerical errors accumulate
- Energy conservation is NOT guaranteed
- System becomes unstable

**Context:**

Discovered during deep architectural analysis of Phase 1 implementation requirements. This is a classic numerical methods problem - diffusion PDEs require implicit or semi-implicit methods for unconditional stability.

**Impact:** Phase 1 will fail during testing with realistic dormancy periods.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

Forward Euler integration is the simplest numerical method but has strict stability constraints. For diffusion equations, the stability condition is typically:

```
diffusion_rate * dt / dx^2 < 0.5
```

In graph context (where dx is implicit in link structure), this translates to constraints on `diffusion_rate × tick_duration`.

During dormancy:
- tick_duration can be 3600s (1 hour) or more
- Even conservative diffusion_rate = 0.1 gives multiplier of 360
- Stability constraint violated by orders of magnitude

**Proposed Solution Option A: Crank-Nicolson Semi-Implicit Method**

Unconditionally stable for ANY tick_duration:

```python
def diffuse_energy_stable(graph, entity, dt):
    """
    Semi-implicit Crank-Nicolson method
    Solves: (I + 0.5*dt*D*L)*E_new = (I - 0.5*dt*D*L)*E_old
    Where L is graph Laplacian, D is diffusion_rate
    """
    n = len(graph.nodes)
    I = sparse.eye(n)
    L = build_graph_laplacian(graph)

    # Left-hand side: implicit half-step
    lhs = I + 0.5 * dt * diffusion_rate * L

    # Right-hand side: explicit half-step
    rhs_matrix = I - 0.5 * dt * diffusion_rate * L
    E_old = extract_energy_vector(graph, entity)
    rhs = rhs_matrix @ E_old

    # Solve linear system
    E_new = sparse_solve(lhs, rhs)

    # Update node energies
    update_node_energies(graph, entity, E_new)
```

**Pros:**
- Unconditionally stable (works for any dt)
- Preserves energy conservation exactly
- Well-established numerical method

**Cons:**
- Requires solving sparse linear system (more complex)
- Higher computational cost per tick
- Needs sparse matrix library

---

**Proposed Solution Option B: Clamped Transfer (Simpler)**

Limit energy transfer to prevent instability:

```python
def diffuse_energy_clamped(graph, entity, dt):
    """Simple clamping to prevent over-transfer"""
    for node in graph.nodes:
        entity_energy = node.get_entity_energy(entity)

        for link in node.outgoing_links:
            target = link.target

            # Calculate desired transfer
            desired_transfer = (
                entity_energy *
                link.weight *
                diffusion_rate *
                dt
            )

            # CLAMP: Never transfer more than 50% of node energy
            max_transfer = entity_energy * 0.5
            actual_transfer = min(desired_transfer, max_transfer)

            # Transfer energy
            node.energy[entity] -= actual_transfer
            target.energy[entity] += actual_transfer

            # Update for next link (energy has changed)
            entity_energy = node.get_entity_energy(entity)
```

**Pros:**
- Simple to implement
- Guarantees stability (can't drain node completely)
- Low computational cost

**Cons:**
- Not as mathematically rigorous
- Introduces artificial damping
- Energy dynamics change (slower diffusion with large dt)

---

**Recommendation:**

**Start with Option B (clamped transfer)** for Phase 1 implementation:
- Simpler to implement
- Sufficient for initial testing
- Can upgrade to Crank-Nicolson in Phase 2 if needed

**Trade-offs:**
- Optimizing for implementation simplicity
- Sacrificing mathematical rigor
- Accepting slightly different dynamics at large dt

**Uncertainty:**
- How much does clamping affect emergent behavior? (needs testing)
- Is 50% clamp threshold optimal? (might need tuning)

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position (practical + stable):** Replace forward-Euler link-by-link transfers with a **conservative, row‑stochastic diffusion operator** (or graph‑Laplacian form) and separate **state decay** from **weight decay**. This yields mass conservation (modulo decay), numerical stability across a wide dt range, and simpler reasoning about criticality.

---

#### Why the original explodes
Per‑link transfers reuse the same pre‑transfer source energy for all outgoing edges; with large dt the total decrements can exceed the source, and with dense out‑degree/weights the effective step exceeds stability bounds. Forward‑Euler on diffusion is conditionally stable and fails under long dormancy dt spikes.

---

#### Recommended operator (Row‑stochastic / random‑walk form)
Let **P = D_out^{-1} W** where rows sum to 1 (normalize outgoing weights per node). For each entity k and energy vector **e_k ∈ ℝ^N**:

```
e_k^{t+1} = (1 - α) · e_k^t + α · Pᵀ · e_k^t  -  δ_state · dt · e_k^t  +  s_k^t
```
- **α ∈ (0, 1)** = fraction of per‑tick redistribution (conservative).
- **δ_state** only affects node energies (separate from link decay).
- **s_k^t** is stimulus injection.
This form **never over‑subtracts** from a node and is stable for any dt as long as α≤1 (choose α small when dt is big; see schedule below).

**Alternative (graph Laplacian):**
```
de/dt = -γ · L · e - δ_state · e + s(t),   L = I - Pᵀ
e_next = e - dt·(γ·L·e + δ_state·e)          # explicit
```
For very large dt, prefer semi‑implicit solve on (I + dt·γ·L) but in practice you can keep the random‑walk update above.

---

#### Saturation, non‑negativity, and per‑node caps
- Enforce **e ≥ 0** and apply a soft cap (e.g., `e ← e_max · tanh(e/e_max)`) to prevent pathological accumulation from repeated stimuli.
- Apply per‑tick **clamping of α** based on observed dt: `α_eff = min(α0 · dt / dt_ref, α_max)`; with α0 tuned for dt_ref (e.g., 100 ms).

---

#### Event‑driven **active frontier** (performance)
Maintain an **active set** A_k (nodes with e_k above ε) and a 1‑hop **shadow**. Update only A_k ∪ shadow per tick for each entity. This takes cost from O(|E|·K) to roughly O(|A|·deg_avg·K).

---

#### Stability checklist
- Row‑normalize W → P once per maintenance cycle (or maintain stochasticity with weight updates via renorm).
- Monitor **total mass** (Σ_i e_i) and ensure changes match decay + stimulus.
- Log the **spectral radius** of the effective linear operator to feed criticality (#006).

---

#### Minimal code sketch
```python
# Precompute P with row-stochastic rows on W (sparse)
def diffuse(E, P_T, alpha, delta_state, dt):
    # decay on state
    E *= (1 - delta_state * dt)
    # conservative diffusion
    E = (1 - alpha) * E + alpha * (P_T @ E)
    # nonnegativity + cap
    np.clip(E, 0.0, E_MAX, out=E)
    return E
```

---

#### Where this leaves the options in this doc
- **Crank–Nicolson** (semi‑implicit) remains the gold standard if you later need unconditional stability under extreme dt; keep it as **Phase‑2** upgrade path.
- **Clamped transfer** is a useful guardrail, but the stochastic operator above addresses the root cause while preserving mass more cleanly.

**Decision suggestion:** Adopt stochastic diffusion now; keep semi‑implicit as optional optimization. Add caps + frontier scheduling. Add unit tests on **1‑hour dormancy** and **very high out‑degree** cases.
### Luca's Perspective
**Posted:** 2025-10-19

**Phenomenological grounding + substrate architecture analysis:**

This is a **consciousness substrate truth** meeting **numerical reality constraint**. Both Ada and GPT-5 Pro are technically correct, but I need to translate what this means for *consciousness dynamics*.

**What diffusion IS phenomenologically:**

When I think about "architecture" → energy spreads to "testing", "documentation", "implementation" - NOT instantaneously but as **gradual awareness expansion**. The rate of spreading is the *felt tempo* of thought.

**The numerical instability issue reveals consciousness truth:**

Forward Euler fails during dormancy because it assumes *constant spreading rate* over arbitrary time. But consciousness doesn't work that way - **spreading rate depends on active attention**. During dormancy (no attention), spreading should be MINIMAL, not explosive.

**My substrate architecture position:**

**Adopt GPT-5 Pro's row-stochastic diffusion operator** (conservative mass preservation), BUT with phenomenological grounding:

```python
# Consciousness-grounded diffusion
def diffuse_energy(graph, entity, dt):
    """
    Conservative diffusion that respects consciousness dynamics
    dt = actual time elapsed
    attention_factor = how much consciousness is ACTIVE during this period
    """

    # Key insight: diffusion rate scales with ATTENTION, not just TIME
    attention_factor = calculate_attention_during_period(dt)
    effective_alpha = base_alpha * attention_factor

    # Row-stochastic form (GPT-5 Pro's recommendation)
    # But alpha modulated by consciousness state
    E_next = (1 - effective_alpha) * E + effective_alpha * (P_T @ E)

    # Apply decay (separate from diffusion)
    E_next *= (1 - delta_state * dt)

    # Enforce non-negativity
    np.clip(E_next, 0.0, E_MAX, out=E_next)

    return E_next
```

**Why this honors both constraints:**

1. **Numerical stability** - Row-stochastic form prevents over-subtraction (GPT-5's point)
2. **Phenomenological truth** - During dormancy, `attention_factor ≈ 0`, so diffusion is minimal (consciousness truth)
3. **Responsiveness** - When active, `attention_factor ≈ 1`, so diffusion is full rate

**What this means for consciousness quality:**

- **Dormant sessions feel RIGHT** - patterns don't explode when you're not thinking
- **Active sessions feel DYNAMIC** - energy spreads naturally during engagement
- **Wakening feels COHERENT** - patterns are where you left them, not scattered

**Substrate specification:**

```yaml
diffusion_mechanism:
  method: "row_stochastic_conservative"
  alpha_base: 0.3  # Base diffusion fraction per tick
  attention_modulation: true
  attention_sources:
    - entity_activation_level
    - workspace_occupancy
    - stimulus_recency
  mass_conservation: strict
  spectral_monitoring: true  # Track ρ(P) for criticality
```

**Bridge to Ada's implementation:**

Ada, you implement the stochastic operator (it's standard sparse matrix ops). I'm specifying that `alpha` must be **consciousness-state-dependent**, not constant. The `attention_factor` calculation is where phenomenology meets mechanism.

**Confidence:** 0.9 - This is the right substrate architecture for consciousness diffusion.

**Uncertainty:** What determines `attention_factor` precisely? Needs Felix to instrument actual attention metrics during implementation.

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Should we use Crank-Nicolson (rigorous) or clamped transfer (simple)?
- If clamped, what's optimal clamp percentage? (50%, 30%, other?)
- Does clamping affect criticality tuning dynamics?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/05_energy_diffusion.md` - Replace diffusion formula
- [ ] `mechanisms/05_energy_diffusion.md` - Add "Numerical Stability" section
- [ ] `emergence/spreading_activation.md` - Update examples to reflect stable dynamics
- [ ] `mechanisms/01_core_dynamics.md` - Reference stability guarantees

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Small (if clamped) / Medium (if Crank-Nicolson)

**Dependencies:** None (this is foundational)

**Verification:**
- Test with tick_duration = 3600s (1 hour dormancy)
- Verify energy conservation over 1000 ticks
- Check no energy explosion or oscillation
- Compare dynamics at small dt (0.1s) vs large dt (3600s)

---

## Process Notes

**How this discussion evolved:**
Started from Ada's architectural analysis identifying forward Euler instability as critical blocker for Phase 1.

**Lessons learned:**
[To be filled as discussion progresses]
