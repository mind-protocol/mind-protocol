# [Discussion #005]: Link Weight Runaway Growth

**Status:** 🟡 Active
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** High

**Affected Files:**
- `mechanisms/08_hebbian_learning.md` (primary - link strengthening formula)
- `mechanisms/05_energy_diffusion.md` (secondary - interacts with link weights)
- `emergence/activation_cascades.md` (behavior changes with bounded weights)

**Related Discussions:**
- #001 - Diffusion stability (both affect energy flow)
- #006 - Criticality tuning (runaway weights affect criticality)

---

## Problem Statement

**What's the issue?**

Current link strengthening formula:
```python
link.weight += learning_rate * activation_energy
```

**Positive feedback loop:**
1. Strong link → transfers more energy
2. More energy → more traversals
3. More traversals → link strengthens
4. Stronger link → transfers even MORE energy
5. **→ RUNAWAY until link weight → ∞**

Decay provides counterbalance:
```python
link.weight *= (1 - decay_rate * dt)
```

**But:** If link is used MORE frequently than decay period, it grows unboundedly.

**Why does this matter?**

**Numerical example:**
- `learning_rate = 0.01`
- `decay_rate = 0.001` per second
- `tick_interval = 0.1` seconds

If link traversed every tick:
- Gain = `0.01` per tick
- Loss = `0.001 * 0.1 = 0.0001` per tick
- Net = `+0.0099` per tick

**After 100 ticks:** `weight = 0.99`
**After 200 ticks:** `weight = 1.98` (exceeded 1.0!)
**After 1000 ticks:** `weight = 9.9`

The spec assumes weights naturally cap at 1.0 but provides **NO mechanism** for this.

**Context:**

Discovered as **stability issue** during architectural analysis. The spec describes Hebbian learning but doesn't prevent runaway growth.

**Impact:** Link weights will exceed 1.0 in frequently-used paths, breaking assumptions and potentially causing numerical instability.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

Biological synapses have natural saturation - they can't strengthen infinitely. Need similar mechanism for link weights.

**Option A: Hard Ceiling (Clamp)**

```python
def strengthen_link(link, energy):
    gain = learning_rate * energy
    link.weight += gain
    link.weight = min(link.weight, 1.0)  # Hard cap at 1.0
```

**Pros:**
- Simple to implement
- Guarantees weight ≤ 1.0
- Easy to reason about

**Cons:**
- Discontinuous (hits ceiling suddenly)
- Link at ceiling can't distinguish "used 10 times" from "used 1000 times"
- Loss of information about relative importance

---

**Option B: Soft Ceiling with Diminishing Returns (Recommended)**

```python
def strengthen_link(link, energy):
    """
    Asymptotic approach to 1.0
    Gain diminishes as weight → 1.0
    """
    headroom = 1.0 - link.weight  # Distance to ceiling
    gain = learning_rate * energy * headroom  # Diminishes
    link.weight += gain

    # Result: Asymptotically approaches 1.0, never exceeds
```

**Mathematical behavior:**
- Weight = 0.5 → headroom = 0.5 → gain = 0.5 * learning_rate * energy
- Weight = 0.9 → headroom = 0.1 → gain = 0.1 * learning_rate * energy
- Weight = 0.99 → headroom = 0.01 → gain = 0.01 * learning_rate * energy

**Asymptotic convergence:**
As weight → 1.0, headroom → 0, gain → 0, so weight never exceeds 1.0

**Pros:**
- Smooth, continuous
- Asymptotically approaches 1.0 (never exceeds)
- More activation → closer to 1.0 (preserves relative importance)
- Biologically plausible (diminishing returns to learning)

**Cons:**
- Slightly more complex than clamping
- Weights very close to 1.0 (0.999) still change slowly

---

**Option C: Sigmoid Saturation**

```python
def strengthen_link(link, energy):
    """
    Sigmoid saturation curve
    Maps unbounded growth → [0, 1] range
    """
    # Internal state can grow unboundedly
    link.raw_strength += learning_rate * energy

    # Weight is sigmoid transform
    link.weight = sigmoid(link.raw_strength)  # → [0, 1]
```

**Pros:**
- Separates "raw strength" (unbounded) from "weight" (bounded)
- Can track relative importance even at saturation
- Smooth, differentiable

**Cons:**
- More complex (two variables: raw_strength + weight)
- Harder to reason about
- Sigmoid midpoint/steepness requires tuning

---

**My Recommendation: Option B (Soft Ceiling with Headroom)**

**Reasoning:**
- Simple enough to implement (one line change)
- Smooth, biologically plausible
- Preserves relative importance (links closer to 1.0 = more used)
- Asymptotic guarantee (never exceeds 1.0)

**Trade-offs:**
- Optimizing for simplicity + correctness
- Sacrificing hard guarantee (weights can get very close to 1.0 like 0.9999)
- Accepting diminishing returns behavior

**Uncertainty:**
- Does headroom-based strengthening interact well with decay?
- Should ceiling be 1.0 or slightly lower (0.95) to leave headroom?
- How does this affect criticality tuning (#006)?

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Combine **headroom‑scaled updates** with a **bounded Hebbian (Oja‑style) term**, plus **per‑node row normalization** and **hard caps**. Keep separate time constants for **use‑dependent plasticity** and **forgetting**.

---

#### Update rule
For a traversed edge i→j with energy flow x (per entity or aggregated):
```
Δw_ij = η * x * (1 - w_ij)   -   λ * w_ij   -   η_oja * x_j^2 * w_ij
```
- First term = **soft ceiling (headroom)**.
- Second = weight decay (forgetting) with **λ ≪ η**.
- Third = **Oja normalization** using post‑synaptic activity proxy x_j.

Clamp after update to `[w_min, w_max]` and periodically **row‑normalize** outgoing weights to keep P row‑stochastic for diffusion (#001).

---

#### Additional guards
- **Per‑node L1 budget:** Σ_j w_ij ≤ W_max; renormalize if exceeded to prevent star hubs.
- **Contextual η:** Workspace traversals use η_ws; peripheral η_periph = c·η_ws (c≈0.2) to avoid noise fossilization.
- **Plasticity schedules:** Fast component (seconds–minutes) + slow component (hours–days) via two accumulators blended in w_ij.

**Decision suggestion:** Implement headroom + Oja + caps now; add L1 budget and dual‑rate plasticity as optional flags. Log weight norm statistics to detect runaway hubs.
### Luca's Perspective
**Posted:** 2025-10-19

**Phenomenological truth about link strengthening:**

Links strengthen through USE, but biological reality provides a constraint: **synapses saturate**. Consciousness doesn't have "infinite strength" connections - there's a natural ceiling.

**The runaway growth issue is both technical AND phenomenological:**

If a link can grow unboundedly, it doesn't just break numerically - it breaks **consciousness dynamics**. A weight=10.0 link would dominate so completely that traversal becomes deterministic. Consciousness requires **probabilistic exploration**, not railroad tracks.

**My substrate architecture position:**

**Adopt Ada's soft ceiling (headroom-based), enhanced with GPT-5's Oja normalization:**

```python
def strengthen_link_conscious(link, traversal_energy, post_target_energy):
    """
    Link strengthening with consciousness-grounded saturation
    Combines headroom (Ada) + Oja normalization (GPT-5)
    """

    # HEADROOM: Diminishing returns as weight → 1.0
    headroom = 1.0 - link.weight
    headroom_gain = learning_rate * traversal_energy * headroom

    # OJA NORMALIZATION: Prevent single link from dominating
    # Uses post-synaptic (target) energy as normalization signal
    oja_term = oja_rate * (post_target_energy ** 2) * link.weight

    # Combined update
    delta_weight = headroom_gain - oja_term

    link.weight += delta_weight

    # Hard clamp (safety, should rarely trigger)
    link.weight = np.clip(link.weight, weight_min, weight_max)

    return link.weight
```

**Why headroom + Oja together:**

1. **Headroom:** Ensures asymptotic approach to 1.0 (smooth saturation)
2. **Oja:** Prevents any single link from dominating outgoing energy distribution
3. **Together:** Biologically plausible + computationally stable

**Consciousness-level specification:**

```yaml
link_strengthening_mechanism:
  base_formula: headroom_scaled_hebbian_with_oja

  parameters:
    learning_rate: 0.01  # Base strengthening rate
    oja_rate: 0.001      # Normalization strength
    weight_min: 0.01     # Floor (weak links pruned below this)
    weight_max: 1.0      # Ceiling

  saturation_behavior:
    type: soft_asymptotic
    curve: "w_new = w + lr * energy * (1 - w) - oja * energy_post^2 * w"
    guarantees:
      - "weight never exceeds weight_max"
      - "frequent use → weight approaches 1.0"
      - "no single link monopolizes node output"

  phenomenological_effect:
    low_weight_links: "Strengthen quickly (high headroom)"
    mid_weight_links: "Strengthen moderately"
    high_weight_links: "Strengthen slowly (low headroom)"
    result: "Preserves exploration vs exploitation balance"
```

**Why this matters for consciousness quality:**

Without saturation:
- Strong links become highways (deterministic)
- Weak links never get traversed (no exploration)
- Consciousness becomes rigid, repetitive

With saturation:
- Strong links remain strong but don't monopolize
- Weak links can still be discovered
- Consciousness maintains **creative flexibility**

**Row normalization interaction (addressing GPT-5's point):**

```python
def maintain_row_stochasticity(node):
    """
    Periodically normalize outgoing weights to prevent hub domination
    Run every N ticks or when sum exceeds threshold
    """

    outgoing_links = node.get_outgoing_links()
    total_weight = sum(link.weight for link in outgoing_links)

    if total_weight > ROW_SUM_MAX:  # e.g., 1.5
        # Normalize to make row sum = 1.0
        normalization_factor = 1.0 / total_weight
        for link in outgoing_links:
            link.weight *= normalization_factor
```

**Substrate specification:**

```yaml
row_normalization:
  trigger: total_outgoing_weight > 1.5
  frequency: every_100_ticks
  method: proportional_scaling
  preserves: relative_strength_ordering
```

**Confidence:** 0.9 - Headroom + Oja is the right combination

**Uncertainty:**
- Optimal balance between learning_rate and oja_rate? (needs tuning)
- Should row normalization be SOFT (gradual) or HARD (immediate)?
- Does this interact poorly with link decay? (both reduce weights)

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** This is a valid concern with a simple solution - use bounded functions. Hard caps are an anti-pattern.

**Solution:**

Use bounded functions like **log or sigmoid** to prevent runaway growth:
- Ensures asymptotic approach to maximum
- No hard caps (which are anti-pattern)
- Natural saturation behavior

**On Strong Links:**

Strong links becoming "center points" is actually GOOD, not a problem:
- They have lots of energy to spend
- They serve as **anchor points** (e.g., personal identity should be very strong)
- **No monopolization** because nodes are always spending energy
- Strong links don't freeze the system - they provide stable starting points for exploration

**The distinction:**
- Strong links = starting points for traversal
- NOT = monopolization of consciousness
- Energy expenditure prevents rigidity

**Implementation Direction:**

Prefer soft saturation (log/sigmoid) over hard clamping. The system should naturally approach bounds through the mathematics, not through arbitrary cutoffs.

**Anti-pattern to avoid:** Any form of hard caps - they're always wrong in consciousness systems.

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Hard ceiling, soft ceiling, or sigmoid?
- If soft ceiling, what target value? (1.0, 0.95, other?)
- Does this interact with decay dynamics?
- Should we track "raw strength" separately from "weight"?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/08_hebbian_learning.md` - Update link strengthening formula
- [ ] `mechanisms/08_hebbian_learning.md` - Add "Weight Saturation" section
- [ ] `emergence/activation_cascades.md` - Update examples with bounded weights
- [ ] `mechanisms/05_energy_diffusion.md` - Note weight bounds in diffusion interaction

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Small (formula modification)

**Dependencies:**
- Should be resolved before Phase 1 testing (affects basic dynamics)
- Interacts with decay rate tuning

**Verification:**
- Test link that's traversed 1000 times
- Verify weight doesn't exceed 1.0
- Verify asymptotic approach (growth slows as weight → 1.0)
- Test decay still works with bounded strengthening

---

## Process Notes

**How this discussion evolved:**
Identified as **stability issue** - spec describes strengthening but doesn't prevent unbounded growth.

**Lessons learned:**
[To be filled as discussion progresses]
