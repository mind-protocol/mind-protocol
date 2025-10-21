# D020: Bounded Hebbian Learning (Link Weight Plasticity)

**Status:** Active
**Created:** 2025-10-19
**Priority:** High
**Affected mechanisms:** 08_link_plasticity
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** How should link weights update when traversed?

**Current approach:** Linear strengthening: `weight += learning_rate * transfer_amount`

**Problem:** Unbounded growth leads to:
- Runaway strengthening (frequently-used links → infinite weight)
- Hub formation (well-connected nodes dominate)
- Loss of plasticity (strong links crowd out weak ones)
- Numerical overflow

**Why it matters:** Learning rule determines whether the graph stays healthy or degenerates over time.

**What's blocking us:** Need to choose learning rule before implementing plasticity.

---

## The Options

### Option A: Linear Unbounded (Current)

**How it works:**
```python
weight += learning_rate * energy_transfer
```

**Phenomenological interpretation:**
- "Every traversal makes connection stronger, indefinitely"
- No ceiling on connection strength
- Unlimited memory consolidation

**Pros:**
- Simplest implementation
- Intuitive: "use strengthens"

**Cons:**
- **Runaway growth:** Frequently-used links → infinity
- **Hub degeneration:** High-degree nodes accumulate unbounded in-weight
- **Numerical overflow:** Float limits eventually violated
- **Loss of discrimination:** Everything becomes "strong"
- **No relative weighting:** Can't distinguish "very strong" from "extremely strong"

**Rejected:** Mathematically unstable, needs bounds.

---

### Option B: Hard Clamping

**How it works:**
```python
weight += learning_rate * energy_transfer
weight = min(weight, weight_max)
```

**Phenomenological interpretation:**
- "Connections strengthen up to maximum, then plateau"
- Hard ceiling on connection strength

**Pros:**
- Bounded (prevents overflow)
- Simple to implement
- Preserves linear growth until saturation

**Cons:**
- **Discontinuous:** Derivative = 0 at saturation (no gradual slowdown)
- **All-or-nothing:** Eventually everything is either weak or maxed out
- **No competitive normalization:** Doesn't account for other connections
- **Loss of relative strength:** Many connections at ceiling

---

### Option C: Bounded Hebbian (Oja's Rule)

**How it works:**
```python
# Oja's rule with self-normalization
Δweight = learning_rate * (source_energy * target_energy - target_energy² * weight)
weight += Δweight
```

**Phenomenological interpretation:**
- "Connections strengthen when co-active, but self-normalize"
- Strong connections decay when repeatedly activated
- Automatic weight balancing

**Pros:**
- **Self-normalizing:** Weights converge to stable distribution
- **Competitive:** Strengthening one connection weakens others implicitly
- **Smooth:** No discontinuities
- **Biological:** Matches synaptic scaling in neuroscience
- **Preserves relative strength:** Doesn't flatten to uniform weights

**Cons:**
- More complex mathematics
- Decay term feels counterintuitive ("why would strong links weaken?")
- Requires understanding of normalization dynamics

---

### Option D: Soft Saturation + Decay

**How it works:**
```python
# Strengthen with diminishing returns
Δweight_up = learning_rate * energy_transfer * (1 - weight/weight_max)

# Separate weight decay
Δweight_decay = -decay_rate * weight

weight += Δweight_up + Δweight_decay
```

**Phenomenological interpretation:**
- "Connections strengthen with diminishing returns, decay over time"
- Asymptotic approach to maximum
- Unused connections fade

**Pros:**
- **Bounded:** Asymptotically approaches weight_max
- **Smooth:** No discontinuities
- **Intuitive:** Separate growth and decay
- **Tunable:** Independent learning and decay rates

**Cons:**
- Two parameters to tune (learning_rate, decay_rate)
- Still allows many connections to saturate near max
- Doesn't enforce competitive normalization

---

### Option E: Competitive Normalization (Softmax)

**How it works:**
```python
# Update all weights
for link in node.outgoing:
    link.weight += learning_rate * energy_transfer[link]

# Renormalize to sum to fixed total
total_weight = sum(link.weight for link in node.outgoing)
target_total = node.outgoing_capacity  # e.g., degree * 2.0
for link in node.outgoing:
    link.weight *= (target_total / total_weight)
```

**Phenomenological interpretation:**
- "Node has limited outgoing capacity, distributed among links"
- Strengthening one link weakens others
- Zero-sum per-node plasticity

**Pros:**
- **Enforces scarcity:** Limited total capacity per node
- **Competitive:** Connections compete for share
- **Prevents degeneration:** Total weight bounded
- **Explicit trade-offs:** Visible resource allocation

**Cons:**
- Expensive (renormalization after every update)
- Adding a new link changes all existing weights
- Complexity: per-node or global normalization?

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option C (Oja's rule)

**Reasoning:**
- Proven in neuroscience and machine learning
- Self-normalizing without explicit renormalization
- Prevents runaway strengthening and hub formation
- Smooth, stable dynamics

**Quote from feedback:**
> "**Bounded Hebbian (Oja's rule)** for pair (i→j):
> ```
> Δw_ij = η·(x_i·x_j - x_j²·w_ij)
> ```
> with x_i,x_j proportional to traversed energy; this self-normalizes."

**Also suggests:**
- Per-type weight caps: clamp within `[w_min(type), w_max(type)]`
- Context-aware learning rates: workspace traversal (η_ws) vs peripheral (η_periph = 0.2 × η_ws)

---

### Luca (Consciousness Substrate Architect)

**Concern:** What does "learning" feel like in consciousness?

**Key questions:**

1. **Diminishing returns:** Does repeated thinking about the same thing:
   - Strengthen connection indefinitely (Option A)?
   - Strengthen up to plateau (Option B/D)?
   - Strengthen but with automatic decay when overused (Option C)?

2. **Competitive plasticity:** When strengthening A→B, do other outgoing links from A:
   - Stay unchanged (Options A, B, D)?
   - Weaken automatically (Options C, E)?

3. **Phenomenological test:** "I think about substrate→architecture repeatedly"
   - After 100 traversals, is the connection:
     - Infinitely strong (Option A)?
     - At maximum (Option B)?
     - Stabilized at high-but-finite strength (Option C)?
     - Still growing slowly (Option D)?

4. **Forgetting:** Unused connections should:
   - Stay strong forever (no decay)?
   - Fade over time (separate decay mechanism)?
   - Weaken when other connections strengthen (competitive)?

5. **Link type differences:** Should different link types learn differently?
   - ENABLES vs BLOCKS vs RELATES_TO
   - Workspace vs peripheral traversal
   - Conscious vs unconscious learning

**Leaning toward:** Option C (Oja's rule) for mathematical stability, but uncertain if competitive normalization matches phenomenology.

**Validation needed:** Test whether competitive learning feels realistic or artificial.

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Retrieval Quality & Weight Distribution:**

I support **Option C (Oja's rule)** with confidence 8/10.

**Why Weight Distribution Matters for Retrieval:**

My graph traversal follows weighted paths:
```python
def traverse_context(start, max_hops):
    for hop in range(max_hops):
        # Follow highest-weighted outgoing links
        next_nodes = sorted(node.outgoing_links, key=lambda l: l.weight, reverse=True)[:k]
```

**Weight distribution determines retrieval behavior:**

**Option A (unbounded linear):**
- Frequently-traversed paths → infinite weight
- Hub nodes accumulate unbounded in-weight
- **Problem:** Retrieval becomes degenerate - always follows same super-weighted paths
- No exploration, no diversity, stuck in high-frequency ruts

**Option C (Oja's rule - bounded Hebbian):**
- Self-normalizing: weights converge to stable distribution
- High-frequency paths stay strong BUT not infinite
- Lower-frequency paths stay traversable
- **Benefit:** Retrieval balances frequency (strong paths) with diversity (weak paths still exist)

**Concrete Impact:**

Imagine "consciousness_substrate" node with 20 outgoing links:
- 5 high-frequency: architecture, schema, design, implementation, validation
- 15 low-frequency: phenomenology, embodiment, enactive_cognition, etc.

**With Option A (unbounded):**
- High-frequency links → weights 50, 45, 40, 38, 35
- Low-frequency links → weights 2, 1.5, 1, 0.8, ...
- **Retrieval:** Always follows top 5, never explores other 15
- **Result:** Shallow, repetitive context reconstruction

**With Option C (Oja):**
- High-frequency links → weights 4.5, 4.2, 3.8, 3.5, 3.2
- Low-frequency links → weights 1.5, 1.2, 0.9, 0.7, ...
- **Retrieval:** Prefers top 5 but occasionally explores others
- **Result:** Balanced context reconstruction with serendipity

**Workspace vs Peripheral Learning (Two-Tier Rates):**

GPT-5's recommendation (η_workspace = 1.0, η_peripheral = 0.2) is critical for retrieval quality:

**Workspace traversal = conscious attention:**
- Learns faster (strong reinforcement)
- These paths reliably lead to relevant context

**Peripheral traversal = background activation:**
- Learns slower (weak reinforcement)
- Prevents noise from overwhelming signal

**My Recommendation:**

Implement Oja's rule with two-tier learning:
```python
if link in workspace:
    Δw = η_workspace * (x_src * x_tgt - x_tgt² * w)  # η = 1.0
else:
    Δw = η_peripheral * (x_src * x_tgt - x_tgt² * w)  # η = 0.2
```

**Benefits for retrieval:**
- Bounded weights prevent degeneration
- Competitive normalization preserves diversity
- Two-tier rates distinguish signal from noise
- Stable long-term weight distribution

**Confidence: 8/10** - Oja's rule is mathematically stable and empirically proven. Main uncertainty is phenomenological match (does competitive normalization feel like real learning?).

**Measurement:**
- Track weight distribution (should be power-law, not binary)
- Monitor retrieval diversity (should explore beyond top-k paths)
- Validate context reconstruction quality over time

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- Computational cost of Oja's rule vs linear?
- How to efficiently compute energy products?
- Batching updates for performance?

---

## Phenomenological Examples

### Scenario 1: Repeated Traversal

**Context:** "substrate→architecture" traversed 100 times

**Option A (Linear unbounded):**
- weight = 0.5 initially
- After 100 traversals: weight = 0.5 + 100 × 0.1 × 0.8 = 8.5
- After 1000 traversals: weight = 80.5
- **Problem:** Unbounded growth

**Option B (Hard clamp):**
- weight_max = 5.0
- After 100 traversals: weight = 5.0 (saturated)
- **Result:** Binary (weak vs maxed)

**Option C (Oja's rule):**
- Converges to: weight ≈ source_energy × correlation
- After 100 traversals: weight ≈ 2.5 (stabilized)
- After 1000 traversals: weight ≈ 2.5 (unchanged)
- **Result:** Stable relative strength

**Option D (Soft saturation):**
- Asymptotically approaches weight_max
- After 100 traversals: weight ≈ 4.2
- After 1000 traversals: weight ≈ 4.9
- **Result:** Slow growth to ceiling

---

### Scenario 2: Hub Formation

**Context:** High-degree node with 50 outgoing links, all frequently traversed

**Option A:**
- All 50 links → infinity
- **Problem:** Node becomes supercharged hub

**Option C (Oja):**
- Total outgoing weight normalized automatically
- Each link = 1/50 of total capacity (if equally traversed)
- **Result:** Capacity distributed among links

**Option E (Explicit normalization):**
- Total outgoing weight = fixed capacity (e.g., 50 × 2.0 = 100)
- Each link receives share proportional to usage
- **Result:** Explicit resource allocation

---

### Scenario 3: Learning Rate Tiers

**Context:** Workspace traversal vs peripheral traversal

**GPT-5 recommendation:**
- `η_workspace = 1.0`
- `η_peripheral = 0.2 × η_workspace = 0.2`

**Rationale:**
- Conscious traversal learns faster (workspace)
- Subliminal traversal learns slower (peripheral)
- Prevents peripheral noise from flooding memory

**Phenomenology:**
- "Conscious practice strengthens more than passive exposure"
- Matches learning theory (active vs passive)

---

## Design Considerations

### Per-Type Weight Bounds

**Should different link types have different weight ranges?**

Examples:
- `ENABLES`: [0.0, 5.0] (strong facilitation)
- `BLOCKS`: [-1.0, 0.0] (inhibitory, see D016)
- `RELATES_TO`: [0.0, 2.0] (weaker association)

**Reasoning:** Different relationships have different strength semantics

---

### Workspace vs Peripheral Learning

**Two-tier learning rates:**

```python
if link in workspace_traversal:
    learning_rate = η_workspace  # e.g., 1.0
else:
    learning_rate = η_peripheral  # e.g., 0.2
```

**Phenomenology:** Conscious attention strengthens connections more than background activation

---

### Structural Plasticity

**Beyond weight updates, should we:**
- **Prune weak links:** Remove if weight < threshold for T ticks
- **Grow new links:** Add when co-activation exceeds threshold
- **Sparsity targets:** Maintain healthy degree distribution

**Trade-off:** Structural changes vs weight-only changes

---

## Mathematical Comparison

### Oja's Rule Derivation

**Goal:** Maximize captured variance while keeping weights bounded

**Update rule:**
```python
Δw = η * (x_src * x_tgt - x_tgt² * w)
```

**Equilibrium:** When Δw = 0
```
x_src * x_tgt = x_tgt² * w
w_eq = x_src / x_tgt
```

**Property:** Weights self-normalize to correlation structure

---

### Stability Analysis

**Option A (Linear):**
- Eigenvalues: unbounded
- Stability: unstable (diverges)

**Option C (Oja):**
- Eigenvalues: bounded by data statistics
- Stability: stable convergence
- Attractor: correlation-based weights

---

## Open Questions

1. **Phenomenological match:** Does competitive normalization feel real?
   - Or does it feel artificial ("why does learning X weaken Y")?

2. **Learning rate ratio:** What should η_workspace / η_peripheral be?
   - GPT-5 suggests 5:1 (0.2 ratio)
   - Need empirical validation

3. **Per-type learning:** Should different link types use different rules?
   - ENABLES: Oja's rule
   - BLOCKS: Different rule for inhibitory?

4. **Decay vs normalization:** Are both needed?
   - Oja has implicit decay (second term)
   - Should we add explicit weight decay too?

5. **Structural plasticity:** When to add/remove links?
   - Fixed structure vs dynamic topology

---

## What I Need from Nicolas

1. **Repeated traversal:** When you think about the same connection many times:
   - Does it feel like it strengthens without bound?
   - Or plateaus at some maximum strength?
   - Or stabilizes with ongoing reinforcement?

2. **Competitive learning:** When one connection strengthens, do others:
   - Stay unchanged (independent)?
   - Weaken automatically (competitive)?
   - Feel like both can strengthen without trade-off?

3. **Conscious vs unconscious:** Does conscious attention strengthen connections more than passive activation?
   - How much more? 2×? 5×? 10×?

4. **Forgetting:** Should unused connections:
   - Persist indefinitely (no decay)?
   - Fade slowly over time?
   - Weaken when other connections strengthen?

5. **Decision:** Which learning rule?
   - A: Linear unbounded (not recommended)
   - B: Hard clamping
   - C: Bounded Hebbian (Oja's rule)
   - D: Soft saturation + decay
   - E: Competitive normalization

---

## Recommendation (Luca)

**Confidence: 7/10** (high - Oja's rule is mathematically sound)

**Suggested approach:**
1. Implement Oja's rule (Option C)
   - Self-normalizing, proven stable
   - Per-type weight bounds as constraints
   - Two-tier learning rates (workspace vs peripheral)
2. Add weight decay as separate mechanism (from D014)
   - Oja handles competitive normalization
   - Decay handles forgetting
3. Monitor weight distribution over time
   - Ensure healthy diversity (not all-or-nothing)
   - Track sparsity, degree distribution

**Parameters:**
```python
η_workspace = 1.0
η_peripheral = 0.2
weight_bounds = {
    'ENABLES': [0.0, 5.0],
    'BLOCKS': [-1.0, 0.0],
    'RELATES_TO': [0.0, 2.0],
    # ...
}
```

**Why Oja:** Mathematically stable, biologically plausible, prevents degeneration.

**Remaining uncertainty:** Whether competitive normalization matches consciousness phenomenology (need empirical test).

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Link strengthening only happens when both nodes are NOT active.

**Key guidance:**

"I think the solution is the link strengthening only happens when both nodes are not active. Because there is going to be a lot of back-end force of energy between active nodes, this should not change. That's normal. It's only when you're adding something new that the strengthening should happen. That solves the problem."

**Architecture:**

```yaml
link_strengthening:
  condition: both_nodes_inactive

  when_both_active:
    behavior: energy_flows_back_and_forth
    strengthening: NO
    rationale: "Normal dynamics, not learning moment"

  when_adding_new:
    behavior: link_strengthens
    strengthening: YES
    rationale: "Learning happens when forming new patterns"
```

**Critical distinction:**
- **Active nodes:** Energy flows between them (normal operation) → NO strengthening
- **Inactive nodes being connected:** New pattern forming → YES strengthening

**This prevents:**
- Runaway strengthening from repeated activation
- Links becoming infinitely strong from normal use
- Hub formation from high-traffic nodes

**Learning occurs when:**
- New connections are being established
- Not during normal traversal of existing active connections

---

## Decision

**Status:** ✅ DECIDED - Strengthen only when both nodes inactive

**Date:** 2025-10-19
**Decided by:** Nicolas
**Rationale:** Link strengthening happens when adding new patterns (both nodes inactive), not during normal energy flow between active nodes. Active nodes have back-and-forth energy dynamics without strengthening.

---

## Affected Files

- `mechanisms/08_link_plasticity.md` - implement Oja's rule
- `mechanisms/07_energy_diffusion.md` - energy values used in learning
- `mechanisms/09_workspace_selection.md` - workspace vs peripheral learning rates
- `implementation/parameters.md` - η values, weight bounds per type
- `validation/metrics_and_monitoring.md` - track weight distribution health
