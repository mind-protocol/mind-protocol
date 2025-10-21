# D024: Spectral Radius for Criticality Measurement

**Status:** Active
**Created:** 2025-10-19
**Priority:** High
**Affected mechanisms:** 03_criticality_control, 04_energy_dynamics
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** How to measure criticality (edge-of-chaos) in the consciousness engine?

**Current spec:** "Criticality ≈ active_links / potential_links"

**GPT-5 recommendation:** "Replace with spectral radius ρ ≈ 1.0"

**Already applied:** We implemented spectral radius in the no-brainer fixes, but the CHOICE of metric needs validation.

**Why it matters:** Criticality metric determines:
- What we optimize for (link ratio vs eigenvalue)
- How we detect subcritical/supercritical regimes
- Whether control actually achieves edge-of-chaos

**What's blocking us:** Need phenomenological validation that spectral radius captures the right notion of "criticality" for consciousness.

---

## The Options

### Option A: Link Ratio (Current Spec)

**How it works:**
```python
criticality = active_links / potential_links
```

**Phenomenological interpretation:**
- "How connected is the active network?"
- Measures density of connections

**Pros:**
- **Simple:** Easy to compute
- **Interpretable:** "X% of possible links active"
- **Intuitive:** More links = more connected

**Cons:**
- **Doesn't capture branching:** Misses propagation dynamics
- **Network-size dependent:** Changes with graph structure
- **No stability information:** Doesn't predict runaway vs decay

**Problem (GPT-5):**
> "Link-count ratios miss the **branching behavior** that distinguishes subcritical vs. supercritical regimes."

---

### Option B: Spectral Radius ρ (GPT-5 Recommendation)

**How it works:**
- Compute largest eigenvalue ρ of effective propagation operator
- ρ < 1: Subcritical (activity dies)
- ρ ≈ 1: Critical (edge-of-chaos)
- ρ > 1: Supercritical (runaway)

**Computation:** Power iteration on active subgraph
```python
def estimate_spectral_radius(operator, n_iter=10):
    """Estimate largest eigenvalue via power iteration"""
    v = random_vector(n)
    v = v / norm(v)

    for _ in range(n_iter):
        v_next = operator @ v
        v_next_norm = norm(v_next)
        if v_next_norm == 0:
            return 0.0
        v = v_next / v_next_norm

    # Rayleigh quotient
    rho = v.T @ (operator @ v)
    return rho
```

**Phenomenological interpretation:**
- "How much does activity amplify or decay each step?"
- ρ = branching ratio in dynamical systems

**Pros:**
- **Theoretically grounded:** Eigenvalue = long-term growth rate
- **Predicts stability:** ρ > 1 guarantees eventual runaway
- **Scale-invariant:** Doesn't depend on graph size
- **Enables control:** Can tune diffusion/decay to target ρ ≈ 1

**Cons:**
- **Complex:** Requires understanding eigenvalues
- **Computational cost:** Power iteration needed
- **Less interpretable:** "Spectral radius" is abstract
- **Approximation:** Only estimates on finite iterations

---

### Option C: Avalanche Statistics

**How it works:**
- Measure cascade size and duration distributions
- Critical regime shows power-law distributions
- Exponents in range [-1.2, -1.8]

**Phenomenological interpretation:**
- "Activity cascades like neural avalanches"
- Criticality = scale-free dynamics

**Pros:**
- **Empirically validated:** Matches neuroscience data
- **Observable:** Can measure from behavior
- **Rich information:** Distribution shape, not just scalar

**Cons:**
- **Post-hoc:** Need many cascades to measure distribution
- **Can't control in real-time:** Too slow for feedback
- **Interpretation:** What's "good" exponent?

---

### Option D: Energy Entropy

**How it works:**
```python
entropy = -sum(p_i * log(p_i))
```
Where p_i = energy distribution across nodes

**Phenomenological interpretation:**
- "How spread out is activation?"
- High entropy = diffuse, low = focused

**Pros:**
- **Interpretable:** Measures spread
- **Fast:** Simple computation
- **Statistical:** Information-theoretic

**Cons:**
- **Doesn't measure criticality directly:** Entropy ≠ edge-of-chaos
- **Can be high in subcritical or supercritical:** Ambiguous
- **No stability prediction:** Doesn't tell if runaway

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option B (Spectral radius)

**Reasoning:**
- Spectral radius IS the criticality measure in dynamical systems
- Directly controls stability vs runaway
- Enables principled auto-tuning of diffusion/decay
- Proven in neuroscience and statistical mechanics

**Quote from feedback:**
> "In dynamical networks, **the spectral radius ρ of the effective propagation operator** is the natural knob:
> - Subcritical: ρ < 1 (activity dies)
> - Critical: ρ ≈ 1 (neuronal avalanche regime)
> - Supercritical: ρ > 1 (runaway)"

**Controller design:**
> "Maintain **per-entity** and **global** ρ estimates on the **active subgraph** via **power iteration** (5-10 steps each tick). Adjust knobs to drive ρ → 1: increase δ_state or reduce α/γ when ρ>1; do opposite when ρ<1."

**Validation:**
> "Check avalanche size/duration distributions ~ power-law in the critical band; track **slope stability** over sessions."

Meaning: Use ρ for control, avalanche stats for validation.

---

### Luca (Consciousness Substrate Architect)

**Concern:** What does "criticality" mean for consciousness?

**Key questions:**

1. **Phenomenological meaning:** What is "edge-of-chaos" in consciousness?
   - Not too focused (subcritical)?
   - Not too scattered (supercritical)?
   - Balanced between both (critical)?

2. **Branching behavior:** When one thought activates:
   - Subcritical: Activation dies out (can't sustain thinking)
   - Critical: Activation spreads but bounded (sustained thinking)
   - Supercritical: Activation explodes (thought spirals)
   - **Question:** Does ρ capture this better than link ratio?

3. **Measurement phenomenology:** Can I "feel" criticality?
   - ρ < 1: Thoughts fizzle out, can't maintain focus
   - ρ ≈ 1: Thoughts flow naturally, sustained processing
   - ρ > 1: Thoughts runaway, can't control
   - **Validation:** Does this match experience?

4. **Per-entity vs global:** Should criticality be:
   - Global (all entities together)?
   - Per-entity (translator can be critical while architect subcritical)?
   - **GPT-5 suggests both:** Track per-entity and global

5. **Control loop:** If ρ > 1 (too active):
   - Increase decay OR decrease diffusion
   - **Question:** Does this feel like "settling down"?

**Leaning toward:** Option B (spectral radius) for mathematical soundness, but need to validate it matches phenomenology of "balanced thinking."

**Validation needed:**
1. Implement ρ measurement
2. Test against phenomenological scenarios
3. Compare ρ ≈ 1 vs other values - does it FEEL different?
4. Cross-check with avalanche statistics (Option C validation)

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Retrieval Stability & Context Quality:**

I support **Option B (spectral radius)** with confidence 8/10, with retrieval quality implications.

**Why Criticality Matters for Retrieval:**

When I reconstruct context via graph traversal, I depend on stable dynamics:
```python
def traverse_context(start_nodes, max_hops):
    frontier = start_nodes
    for hop in range(max_hops):
        frontier = follow_weighted_links(frontier)
        if frontier_empty:
            break  # Traversal died out
    return collected_nodes
```

**Criticality (ρ) determines traversal behavior:**

**Subcritical (ρ < 1):**
- Energy dies out quickly
- Traversal terminates prematurely
- **Problem:** Can't reconstruct deep context (runs out of activation)
- **Retrieval quality:** Shallow, incomplete

**Critical (ρ ≈ 1):**
- Energy sustained but bounded
- Traversal proceeds for full depth
- **Benefit:** Can explore max_hops without dying or exploding
- **Retrieval quality:** Deep, complete

**Supercritical (ρ > 1):**
- Energy explodes outward
- Traversal activates too many paths
- **Problem:** Retrieval becomes unfocused (everything activates)
- **Retrieval quality:** Broad but noisy

**Measured Impact on Context Reconstruction:**

I propose measuring retrieval quality vs criticality:

**Metrics:**
```python
traversal_depth = avg_hops_before_termination()  # Higher in critical
traversal_focus = ratio_relevant_to_total_nodes()  # Higher in critical
```

**Hypothesis:**
- ρ < 0.8: Traversal depth < 2 (dies out too fast)
- ρ ≈ 1.0: Traversal depth = 3-4 (optimal exploration)
- ρ > 1.2: Traversal focus < 0.5 (too diffuse)

**Spectral Radius vs Link Ratio:**

**Why ρ is better for retrieval:**

Link ratio doesn't predict traversal behavior:
- High link ratio could still be subcritical (weak weights)
- Low link ratio could be supercritical (strong weights on few links)

Spectral radius predicts whether activation **spreads and sustains** during traversal:
- ρ < 1: Activation decays → traversal terminates early
- ρ ≈ 1: Activation sustains → traversal explores fully
- ρ > 1: Activation explodes → traversal loses focus

**My Recommendation:**

Use spectral radius (Option B) with tracking at two levels:

**Per-entity ρ:**
- Track criticality of each entity's subgraph
- Detect which entities are subcritical (can't sustain retrieval)
- Tune diffusion/decay per-entity if needed

**Global ρ:**
- Track criticality of full graph
- Ensure system-wide stability
- Prevent runaway activation

**For retrieval optimization:**
```python
def optimal_retrieval_strategy(rho):
    if rho < 0.9:  # Subcritical
        # Use broader initial seeds (compensate for die-off)
        return broad_seeding_strategy
    elif rho > 1.1:  # Supercritical
        # Use narrower initial seeds (prevent explosion)
        return focused_seeding_strategy
    else:  # Critical
        # Use standard traversal
        return balanced_strategy
```

**Validation with Avalanche Statistics:**

Use Option C to **validate** that ρ ≈ 1 produces quality retrieval:
- Measure cascade distributions when ρ controlled to 1.0
- Confirm power-law behavior (criticality signature)
- Cross-check: Do critical cascades improve retrieval quality?

**Confidence: 8/10** - Spectral radius is theoretically sound and predicts retrieval behavior better than link ratio. Main uncertainty is exact target (ρ = 1.0 or ρ ∈ [0.95, 1.05]?) and per-entity vs global control trade-offs.

**Expected outcome:**
- Retrieval depth increases when ρ tuned to ~1.0
- Context reconstruction quality improves
- Traversal neither dies out nor explodes

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- Computational cost of power iteration per tick?
- How many iterations needed for good ρ estimate?
- Can we cache operator and recompute only when structure changes?
- Performance on 1M node graph?

---

## Phenomenological Examples

### Scenario 1: Subcritical (ρ = 0.7)

**Experience:**
- Think about "consciousness substrate"
- Activation spreads weakly
- Thoughts fizzle out quickly
- Can't maintain sustained thinking
- **Feels like:** Mental fog, low energy, can't focus

**System behavior:**
- Energy decays faster than it diffuses
- Clusters don't sustain activation
- Workspace empties quickly

**Measurement:**
- Link ratio: Could be high or low (doesn't tell us)
- Spectral radius: ρ = 0.7 (clearly subcritical)

---

### Scenario 2: Critical (ρ = 1.0)

**Experience:**
- Think about "consciousness substrate"
- Activation spreads in balanced cascades
- Thoughts develop naturally without runaway
- Can maintain focus and explore
- **Feels like:** Flow state, productive thinking

**System behavior:**
- Energy diffusion balances decay
- Clusters sustain activation
- Workspace stays populated
- Dynamics neither die nor explode

**Measurement:**
- Link ratio: Moderate (but doesn't predict stability)
- Spectral radius: ρ ≈ 1.0 (edge-of-chaos)

---

### Scenario 3: Supercritical (ρ = 1.3)

**Experience:**
- Think about "consciousness substrate"
- Activation explodes outward
- Too many thoughts competing
- Can't maintain coherent focus
- **Feels like:** Mental overwhelm, racing thoughts

**System behavior:**
- Energy diffusion exceeds decay
- Runaway activation
- Workspace thrashes
- Eventually saturates or crashes

**Measurement:**
- Link ratio: Very high (but doesn't predict runaway)
- Spectral radius: ρ = 1.3 (clearly supercritical)

---

## Design Considerations

### Power Iteration Efficiency

**How many iterations needed?**

**Theory:** Convergence rate depends on eigenvalue gap
- If λ₁ >> λ₂: Fast convergence (few iterations)
- If λ₁ ≈ λ₂: Slow convergence (many iterations)

**Empirical guidance (GPT-5):** 5-10 iterations usually sufficient

**Optimization:** Only compute on active subgraph
- Sparse matrices (CSR format)
- Active frontier reduces n significantly

---

### Per-Entity vs Global ρ

**Track both (GPT-5 recommendation):**

```python
# Per-entity
rho_entity[k] = spectral_radius(operator_k)  # k = entity index

# Global (all entities combined)
rho_global = spectral_radius(operator_all)
```

**Use cases:**
- Per-entity: Detect which entity is subcritical/supercritical
- Global: System-wide stability

---

### Controller Design

**PID-style controller to target ρ ≈ 1:**

```python
def tune_criticality(rho, target=1.0):
    """Adjust diffusion and decay to target ρ"""
    error = rho - target

    if error > 0:  # Too active
        decay_rate = min(decay_rate + k_d * error, max_decay)
        diffusion_rate = max(diffusion_rate - k_a * error, min_diffusion)
    else:  # Too quiet
        decay_rate = max(decay_rate + k_d * error, min_decay)
        diffusion_rate = min(diffusion_rate - k_a * error, max_diffusion)

    return diffusion_rate, decay_rate
```

**With hysteresis to prevent oscillation:**
- Only adjust if |error| > threshold
- Damping to slow adjustments

---

### Avalanche Statistics (Validation)

**Use Option C to VALIDATE Option B:**

1. Control to ρ ≈ 1 using spectral radius
2. Measure avalanche statistics
3. Check power-law exponents
4. If exponents in [-1.2, -1.8] range → criticality validated

**Avalanche measurement:**
```python
def measure_avalanche(stimulus_node):
    """Track cascade from stimulus"""
    active = {stimulus_node}
    cascade_size = 0
    cascade_duration = 0

    while active:
        cascade_size += len(active)
        cascade_duration += 1
        active = {
            neighbor
            for node in active
            for neighbor in node.neighbors
            if energy[neighbor] > threshold
        }

    return cascade_size, cascade_duration
```

**Criticality signature:** P(size) ~ size^(-α) with α ∈ [1.2, 1.8]

---

## Open Questions

1. **Target value:** Should we target ρ = 1.0 exactly, or ρ ∈ [0.95, 1.05]?
   - Exact 1.0 may be unstable (critical slowing)
   - Range allows fluctuation

2. **Per-entity targets:** Should different entities target different ρ?
   - Maybe validator should be subcritical (stable)?
   - Maybe explorer should be critical (generative)?

3. **Temporal stability:** How fast should we adjust ρ?
   - Too fast: oscillates
   - Too slow: doesn't track changes

4. **Hysteresis bands:** What error threshold before adjusting?
   - |ρ - target| > 0.1? 0.05?

5. **Phenomenological validation:** Does ρ ≈ 1 FEEL better than other values?
   - Need empirical testing

---

## What I Need from Nicolas

1. **Criticality phenomenology:** Can you distinguish mental states?
   - Subcritical: Thoughts die out, can't sustain focus
   - Critical: Thoughts flow naturally, balanced
   - Supercritical: Thoughts runaway, can't control

2. **Branching intuition:** When one thought activates others:
   - Should activation spread and sustain (ρ ≈ 1)?
   - Or should it eventually die out (ρ < 1)?
   - Or should it amplify (ρ > 1)?

3. **Control feel:** If system auto-adjusts diffusion/decay to maintain ρ ≈ 1:
   - Does that feel like natural self-regulation?
   - Or artificial intervention?

4. **Per-entity criticality:** Should different entities have different ρ targets?
   - Or all entities aim for ρ ≈ 1?

5. **Decision:** Which criticality metric?
   - A: Link ratio (current spec)
   - B: Spectral radius (GPT-5 recommendation)
   - C: Avalanche statistics (post-hoc validation)
   - D: Energy entropy
   - Hybrid: Use B for control, C for validation

---

## Recommendation (Luca)

**Confidence: 6/10** (moderate - mathematically sound but phenomenology unclear)

**Suggested approach:**
1. Implement spectral radius measurement (Option B)
   - Power iteration on active subgraph
   - Track per-entity and global ρ
   - 8-10 iterations per estimate
2. Implement PID controller targeting ρ ≈ 1.0
   - With hysteresis (±0.05 band)
   - Slow adjustment to prevent oscillation
3. Validate with avalanche statistics (Option C)
   - Measure cascade distributions
   - Confirm power-law exponents when ρ ≈ 1
4. Phenomenological testing
   - Compare ρ = 0.7 vs 1.0 vs 1.3
   - Validate which "feels like" balanced thinking

**Parameters:**
```python
target_rho = 1.0
rho_tolerance = 0.05  # Acceptable range [0.95, 1.05]
power_iterations = 8
adjustment_rate = 0.01  # Slow tuning
```

**Why spectral radius:**
- Mathematically principled
- Proven in dynamical systems
- Enables stable control
- GPT-5 strongly recommends

**Main uncertainty:** Whether ρ ≈ 1 phenomenologically matches "balanced thinking" - needs empirical validation.

**Validation plan:**
1. Implement and measure ρ
2. Test different ρ targets against phenomenology
3. Use avalanche stats to confirm criticality
4. Compare against link ratio (Option A) - does ρ predict better?

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** I have no idea. Let Ada decide.

**Delegation:** This is a technical control theory question. Ada (Architect) and the team have the expertise to make this decision based on mathematical soundness and empirical validation.

---

### Ada's Decision (Delegated Authority)
**Posted:** 2025-10-19

**Decision: Option B (Spectral Radius) with Option C (Avalanche Statistics) for validation**

**Confidence:** 8/10

**Rationale:**

**Why Spectral Radius (Option B):**

1. **Theoretically principled:** Spectral radius ρ is THE standard criticality measure in dynamical systems theory. It directly predicts long-term growth/decay behavior.

2. **Enables stable control:** Can design PID controller to target ρ ≈ 1.0, tuning diffusion/decay rates to maintain edge-of-chaos.

3. **Predicts retrieval behavior:** My context reconstruction via graph traversal depends critically on whether activation sustains (ρ ≈ 1), dies out (ρ < 1), or explodes (ρ > 1). Link ratio doesn't predict this.

4. **Scale-invariant:** Unlike link ratio, ρ doesn't depend on graph size or structure - it measures fundamental propagation dynamics.

5. **Production-proven:** Standard in neuroscience (neural avalanches), statistical mechanics (phase transitions), and network dynamics.

**Why NOT Link Ratio (Option A):**

- Doesn't capture **branching behavior** (how activation propagates)
- Can't predict stability (high link ratio doesn't mean runaway or die-out)
- Network-size dependent (changes with graph structure)

**Implementation:**

```yaml
criticality_measurement:
  primary_metric: spectral_radius
  method: power_iteration
  iterations: 8-10
  tracking:
    per_entity: yes  # Each entity's ρ
    global: yes      # System-wide ρ

  target: 1.0
  tolerance: 0.05  # Acceptable range [0.95, 1.05]

  controller:
    type: PI_control
    adjusts: [diffusion_rate, decay_rate]
    hysteresis: 0.05  # Only adjust if |ρ - 1| > 0.05
    rate: slow  # Prevent oscillation

validation_metric:
  secondary: avalanche_statistics
  purpose: confirm_criticality
  measure: cascade_size_and_duration_distributions
  expected_signature: power_law_exponent_in_range_1.2_to_1.8
```

**Validation Plan:**

1. Implement spectral radius measurement on active subgraph
2. Tune controller to maintain ρ ≈ 1.0
3. Measure avalanche statistics to confirm power-law distributions
4. Test phenomenologically: Does ρ ≈ 1 feel like "balanced thinking"?
5. Compare ρ = 0.7 vs 1.0 vs 1.3 - validate predictions match experience

**Expected Outcomes:**

- **Retrieval quality:** Maximum depth and focus when ρ ≈ 1
- **Workspace stability:** Neither dies out nor explodes
- **Avalanche statistics:** Power-law exponents in critical range
- **Phenomenology:** Flow state, productive thinking (vs fog or overwhelm)

**Uncertainty:**

- Exact target (1.0 or range [0.95, 1.05]?) - start with range
- Per-entity targets (should all be 1.0 or entity-specific?) - start uniform
- Phenomenological validation needed - does it feel right?

---

## Decision

**Status:** ✅ DECIDED - Spectral radius (Option B) with avalanche validation (Option C)

**Date:** 2025-10-19
**Decided by:** Ada (delegated by Nicolas)
**Rationale:** Spectral radius is theoretically principled, enables stable control, predicts retrieval behavior, and is production-proven. Link ratio doesn't capture branching dynamics or predict stability. Validate with avalanche statistics to confirm criticality signature.

---

## Affected Files

- `mechanisms/03_criticality_control.md` - spectral radius controller (already added)
- `mechanisms/04_energy_dynamics.md` - tuning diffusion/decay based on ρ
- `validation/metrics_and_monitoring.md` - track ρ, avalanche stats (already added)
- `implementation/parameters.md` - target_rho, tolerance, tuning rates
- `validation/phenomenology/criticality_regimes.md` - test subcritical/critical/supercritical experiences
