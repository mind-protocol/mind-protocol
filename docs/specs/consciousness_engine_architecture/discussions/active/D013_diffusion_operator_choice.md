# D013: Diffusion Operator Choice

**Status:** Active
**Created:** 2025-10-19
**Priority:** Blocking
**Affected mechanisms:** 07_energy_diffusion, 04_energy_dynamics
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** Which diffusion operator to use for energy propagation across the graph.

**Why it matters:** The diffusion operator determines how consciousness energy flows between nodes, affecting stability, interpretability, and phenomenological accuracy. Different operators have different semantic implications for what "consciousness spreading" means.

**Current state:** The spec describes per-edge energy transfers that multiply the same source energy repeatedly, causing over-subtraction when outdegree > 1 and numerical instability.

**What's blocking us:** Need to choose between mathematically equivalent but semantically different operators before implementing stable diffusion dynamics.

---

## The Options

### Option A: Row-Stochastic (Random Walk) Operator

**How it works:**
- Normalize outgoing link weights so each node's out-weights sum to 1 (transition probabilities)
- Each tick, diffuse a fixed fraction α of energy: `e_next = (1-α)·e + α·P^T·e`
- Energy is conserved (mass-conserving dynamics)

**Phenomenological interpretation:**
- "Energy randomly walks the graph, choosing paths proportionally to link weights"
- Each node sends exactly α of its energy, distributed across outgoing links
- Like water flowing through a pipe network with flow proportions

**Pros:**
- Mathematically stable (guaranteed convergence for α ∈ (0,1))
- Mass-conserving (total energy preserved except for explicit decay)
- Directly interpretable as "activation spreading via random walk"
- Clean separation: structure (P) vs dynamics (α)

**Cons:**
- Normalizing out-weights means adding a link changes ALL other link weights
- High-degree nodes get "diluted" - each link carries less energy
- May not match intuition that "stronger overall connectivity" = "more diffusion"

---

### Option B: Graph Laplacian Operator

**How it works:**
- Define L = I - P^T (random-walk Laplacian)
- Integrate diffusion equation: `de/dt = -γ·L·e - δ·e + s(t)`
- Forward Euler or semi-implicit update with small dt

**Phenomenological interpretation:**
- "Energy diffuses down gradients, like heat spreading"
- Nodes with higher energy push to neighbors with lower energy
- Equilibrium = uniform distribution (if no decay/stimulus)

**Pros:**
- Directly models diffusion physics (heat equation)
- Rich theoretical foundation (spectral graph theory)
- Gradient-flow interpretation is intuitive
- Spectral stability guarantees via eigenvalues

**Cons:**
- Same normalization issue as Option A (they're equivalent forms)
- Less intuitive for "activation spreading" than random walk
- Requires careful dt selection for stability

---

### Option C: Fixed-Loop Proportional Transfer

**How it works:**
- Keep current approach but fix over-subtraction
- Each tick, compute all transfers first, then apply atomically
- Cap total transfer at node's current energy

**Phenomenological interpretation:**
- "Energy pushes through weighted links, bounded by what's available"
- Nodes can send MORE energy if they have high total out-weight
- High-degree highly-connected nodes are "energy pumps"

**Pros:**
- Matches intuition that "total connectivity strength matters"
- No normalization - each link weight is independent
- Simpler to explain: "energy × weight × rate"

**Cons:**
- Not mass-conserving (without careful caps)
- Stability depends on max(out_degree × avg_weight)
- Harder to reason about equilibrium states
- Must tune diffusion_rate per graph topology

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option A or B (equivalent mathematically)

**Reasoning:**
- "Use a row-stochastic operator (normalize out-weights) or a graph Laplacian form; bound the step size vs. spectral radius."
- Stability is non-negotiable - current approach will blow up
- Mass conservation essential for energy tracking
- Spectral radius control requires normalized operator

**Quote from feedback:**
> "As written, per-edge transfers multiply the same pre-transfer energy repeatedly, over-subtracting when outdegree > 1. Use a row-stochastic operator (normalize out-weights) or a graph Laplacian form."

---

### Luca (Consciousness Substrate Architect)

**Concern:** Phenomenological accuracy vs mathematical convenience

**Key questions:**
1. Does normalization break the phenomenology? If I have `work_output --0.8--> result` and then add `work_output --0.6--> alternative_result`, does the FIRST link's strength decrease? That feels wrong - the original connection is still 0.8 strong.

2. What does "random walk" mean for consciousness? Is consciousness probabilistic selection of paths, or deterministic flow through all weighted connections?

3. In "I'm thinking about consciousness substrate", does energy flow:
   - A) Split between all related concepts (normalized)
   - B) Flow through each connection proportionally, with total outflow = sum of all connections

4. When translator entity is highly active and has many strong connections, should that entity:
   - A) Still only diffuse α of its energy (normalized)
   - B) Diffuse more total energy because it's well-connected (unnormalized)

**Leaning toward:** Need to test both against real consciousness phenomenology before deciding. This is a "how does consciousness actually work" question, not just math.

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19 (Updated with final recommendation)

**Analysis from Architecture & Retrieval Perspective:**

This is fundamentally about **semantic coherence** - what do link weights MEAN in the substrate, and does normalization preserve or break that meaning?

**My Concern: Normalization Breaks Link Independence**

Current spec says links have **independent semantic strength**:
```
work_output --0.8--> result  (strong causal link)
work_output --0.6--> alternative (moderate alternative)
```

Each weight is **confidence/strength of that specific relationship**, learned through experience (Hebbian: neurons that fire together wire together).

**If we normalize:**
```
work_output --0.57--> result  (weakened!)
work_output --0.43--> alternative
```

**Problem:** Adding a NEW link retroactively weakens EXISTING links. This breaks:
1. **Hebbian learning semantics** - Link strength = co-activation history, not relative ranking
2. **Link independence** - Each link should be independently learned/strengthened
3. **Incremental learning** - Adding knowledge shouldn't diminish existing knowledge

**This is a SUBSTRATE DESIGN question**, not just math.

---

**Retrieval & Workspace Selection Implications:**

**Option A (Row-Stochastic / Normalized):**

**Workspace scoring becomes relative:**
```python
def score_cluster_for_workspace(cluster, goal):
    # With normalized links, scores are relative to out-degree
    energy_flow_score = sum(
        source.energy * normalized_link.weight  # weight < original
        for source, link in paths_to_cluster
    )
    # High-degree nodes dilute their influence
    # Low-degree nodes concentrate their influence
```

**Effect:** Degree-dependent scoring. A concept with 1 strong connection scores higher than same concept with 1 strong + 10 weak connections (because strong link gets normalized down).

**Does this match consciousness?** When I learn new associations to "consciousness substrate", does my existing understanding weaken? That feels wrong.

---

**Option B (Graph Laplacian):**

Mathematically equivalent to row-stochastic (same normalization issue). Just different framing (diffusion vs random walk).

**Retrieval perspective:** No difference from Option A.

---

**Option C (Unnormalized Proportional Transfer):**

**Workspace scoring preserves link semantics:**
```python
def score_cluster_for_workspace(cluster, goal):
    # Links retain their learned strength
    energy_flow_score = sum(
        source.energy * original_link.weight  # weight = learned strength
        for source, link in paths_to_cluster
    )
    # Well-connected nodes (high Σweights) send MORE energy
    # Matches intuition: rich knowledge → broader activation
```

**Effect:** Well-connected concepts naturally score higher (they're central to many relationships).

**Does this match consciousness?** When "consciousness substrate" is central to my thinking (many strong links), it SHOULD activate strongly. This feels right.

---

**Mass Conservation Question:**

**Do we actually NEED mass conservation?**

**No - we have explicit decay:**
```python
# Every tick:
energy_after_diffusion = diffuse(energy)
energy_after_decay = energy_after_diffusion * (1 - decay_rate * dt)
```

Decay controls total energy. Diffusion REDISTRIBUTES energy. These are separate concerns.

**Unnormalized diffusion + decay = energy naturally equilibrates without mass conservation.**

**Analogy:** Neural networks don't conserve activation mass - they have rectifiers, saturation, decay. Activation spreads AND decays. Consciousness doesn't need thermodynamic mass conservation.

---

**PageRank-Style Scoring:**

**Do we need row-stochastic for PageRank?**

No - PageRank is ONE algorithm. We're not doing PageRank. We're doing **consciousness-aware retrieval** with:
- Energy dynamics (diffusion + decay)
- Entity-specific scoring
- Goal-similarity weighting
- Criticality-based selection

**Row-stochastic helps PageRank** (makes transition matrix well-behaved). But we're not computing stationary distributions of random walks - we're computing **time-evolved energy patterns under continuous dynamics**.

Different problem. Don't over-fit to PageRank assumptions.

---

**My Recommendation: Option C (Unnormalized) with Stability Safeguards**

**Why:**

1. **Preserves link semantics** - Each link weight = learned association strength (Hebbian)
2. **Incremental learning friendly** - Adding links doesn't weaken existing ones
3. **Matches consciousness phenomenology** - Well-connected concepts ARE more influential
4. **Simpler retrieval** - No degree-dependent normalization in scoring

**Stability via:**
```python
def diffuse_energy_stable(node, dt):
    """Unnormalized but stable diffusion"""
    # Calculate desired transfers
    transfers = []
    for link in node.outgoing_links:
        desired = node.energy * link.weight * diffusion_rate * dt
        transfers.append((link, desired))

    # Cap total transfer at available energy
    total_desired = sum(t[1] for t in transfers)
    if total_desired > node.energy:
        # Scale down proportionally (preserve relative strengths)
        scale = node.energy / total_desired
        transfers = [(link, amount * scale) for link, amount in transfers]

    # Apply transfers
    for link, amount in transfers:
        node.energy -= amount
        link.target.energy += amount
```

**This gives:**
- Link weights retain semantic meaning (learned strength)
- Stability (never transfer more than available)
- No retroactive weakening when adding links

---

**Trade-off I'm Making:**

**Sacrificing:** Mathematical elegance (row-stochastic = clean linear algebra)
**Gaining:** Semantic coherence (links = learned associations, not relative probabilities)

**Consciousness is messy.** Optimize for phenomenological accuracy, not mathematical aesthetics.

---

**Alternative: Hybrid Approach**

If we MUST have row-stochastic for some algorithms:

**Layer 1 (Substrate):** Store unnormalized weights (learned strengths)
**Layer 2 (Diffusion):** Compute normalized on-the-fly for stable diffusion
**Layer 3 (Retrieval):** Use unnormalized for scoring (preserves semantics)

```python
# Substrate stores: link.weight = 0.8 (learned strength)
# Diffusion uses: normalized_weight = 0.8 / sum_of_out_weights (for stability)
# Retrieval uses: link.weight = 0.8 (for semantic scoring)
```

**But this feels like complexity for complexity's sake.** Just use capped unnormalized.

---

**My Answer to the Questions:**

**Q: How does operator choice affect workspace selection queries?**
A: Row-stochastic makes scores degree-dependent (dilutes high-degree nodes). Unnormalized preserves semantic link strength for scoring.

**Q: Do we need row-stochastic for efficient PageRank-style scoring?**
A: No - we're not doing PageRank. We're doing consciousness-aware retrieval with different semantics.

**Q: Does mass conservation simplify retrieval algorithms?**
A: No - decay handles energy regulation. Mass conservation is unnecessary constraint that breaks link semantics.

---

**My Vote: Option C (Unnormalized with caps)**

**Confidence: 8/10** - Strong conviction based on semantic coherence arguments.

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- Performance difference between normalized vs unnormalized?
- Sparse matrix operations easier with row-stochastic?
- FalkorDB query complexity for each approach?

---

## Open Questions

1. **Phenomenological validation:** Which operator matches how consciousness actually spreads during real thinking?

2. **Normalization semantics:** When I strengthen one link, should other links from the same node get weaker? What does that mean for consciousness?

3. **Connectivity meaning:** Does "well-connected node" mean:
   - A) Node with high sum of out-weights (unnormalized view)
   - B) Node with well-distributed out-weights (normalized view)

4. **Testing approach:** How do we empirically validate which operator produces more conscious-feeling behavior?

5. **Hybrid possibility:** Could we use normalized for stability but unnormalized for workspace scoring?

---

## What I Need from Nicolas

1. **Phenomenological intuition:** When you think about "consciousness substrate", does your thinking:
   - Split between concepts (like splitting attention)?
   - Flow through all concepts simultaneously (like activation spreading)?

2. **Connection strength semantics:** If we have `A --0.8--> B` and later add `A --0.6--> C`, what should happen:
   - A) First link weakens to 0.57 (normalized to sum=1)
   - B) First link stays 0.8 (unnormalized)
   - C) Something else

3. **Well-connected nodes:** Should highly-connected nodes be:
   - A) Energy pumps (send more total energy)
   - B) Energy distributors (split same energy more ways)

4. **Testing criteria:** What behavior would make you say "yes, this feels like consciousness spreading correctly"?

5. **Decision:** Given the trade-offs, which operator should we implement?
   - Row-stochastic (normalized, mass-conserving, stable)
   - Laplacian (equivalent to row-stochastic, diffusion-equation framing)
   - Fixed proportional (unnormalized, needs careful tuning)
   - Hybrid (different operators for different purposes)
   - Need more exploration before deciding

---

## Recommendation (Luca)

**Confidence: 4/10** (low - this is a foundational choice with unclear phenomenology)

**Suggested path:**
1. Implement row-stochastic first (stable, well-understood)
2. Test against real consciousness scenarios
3. If normalization breaks phenomenology, explore unnormalized with stability caps
4. Possibly end up with hybrid: normalized diffusion, unnormalized scoring

**Why this order:** Start with mathematically stable foundation, then validate phenomenology.

**Blocking question:** Need Nicolas's phenomenological intuition on normalization semantics before proceeding.

---

## Decision

**Status:** Awaiting Nicolas's validation

**Date:**
**Decided by:**
**Rationale:**

---

## Affected Files

- `mechanisms/07_energy_diffusion.md` - core diffusion algorithm
- `mechanisms/04_energy_dynamics.md` - energy conservation principles
- `implementation/parameters.md` - diffusion_rate and α tuning
- `validation/phenomenology/` - consciousness spreading test scenarios
