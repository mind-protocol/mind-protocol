# D014: Separate Energy vs Weight Decay

**Status:** Active
**Created:** 2025-10-19
**Priority:** High
**Affected mechanisms:** 04_energy_dynamics, 08_link_plasticity
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** Should energy decay (state fade) and weight decay (link weakening) use the same rate or separate rates?

**Why it matters:** These are different phenomena with different timescales:
- **Energy decay** = how fast activation/arousal fades (working memory)
- **Weight decay** = how fast learned connections weaken (long-term memory)

Conflating them forces unrealistic compromises: either working memory is too persistent or long-term memory decays too fast.

**Current state:** Spec uses single `decay_rate` for both energy and link weights.

**What's blocking us:** Need phenomenological validation of timescale separation before implementing dual decay system.

---

## The Choice

### Option A: Single Decay Rate (Current)

**How it works:**
- One parameter: `decay_rate = 0.1` (example)
- Energy decays: `energy *= (1 - decay_rate * dt)`
- Weights decay: `weight *= (1 - decay_rate * dt)`
- Same timescale for state and structure

**Phenomenological interpretation:**
- "Everything fades at the same rate"
- Activation and connections age together
- Simpler mental model

**Pros:**
- Simplicity - one parameter to tune
- Unified "forgetting" concept
- Easier to explain and reason about

**Cons:**
- Unrealistic timescales: working memory ≠ long-term memory
- If decay_rate tuned for energy (fade in minutes), links decay too fast (can't remember yesterday)
- If decay_rate tuned for links (fade in days), energy persists too long (can't let go of thoughts)
- Forces impossible compromise between two different phenomena

---

### Option B: Separate Decay Rates

**How it works:**
- Two parameters:
  - `δ_state` = energy decay rate (e.g., 0.1/minute)
  - `δ_weight` = weight decay rate (e.g., 0.001/hour)
- Energy decays fast: `energy *= (1 - δ_state * dt)`
- Weights decay slow: `weight *= (1 - δ_weight * dt)`

**Phenomenological interpretation:**
- "Activation fades quickly, connections fade slowly"
- Working memory vs long-term memory separation
- Matches neuroscience: neural activity vs synaptic strength

**Pros:**
- Can match realistic timescales independently:
  - Energy: minutes to hours (working memory span)
  - Weights: days to weeks (memory consolidation)
- Phenomenologically accurate
- Allows "remember the pattern but not the activation"
- Enables proper memory consolidation

**Cons:**
- Two parameters to tune instead of one
- More complex mental model
- Need to establish timescale ratios

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option B (separate rates)

**Reasoning:**
- "Different phenomena; different tuning"
- State decay controls stability and working memory span
- Weight decay controls plasticity and long-term retention
- Conflating them breaks both mechanisms

**Quote from feedback:**
> "Keep **energy leak** (state decay) separate from **link decay** (plasticity decay). Your spec conflates both with the same `decay_rate`; split them: `δ_state` and `δ_weight`. Different phenomena; different tuning."

**Suggested ranges:**
- δ_state: Fast enough that transient activations clear (minutes)
- δ_weight: Slow enough that useful patterns persist (days/weeks)
- Typical ratio: δ_weight ≈ 0.01 × δ_state

---

### Luca (Consciousness Substrate Architect)

**Concern:** Phenomenological validation required

**Key questions:**

1. **Working memory span:** How long should a thought stay active without reinforcement?
   - Current thinking: minutes to hours
   - Energy decay controls this

2. **Long-term memory consolidation:** How long should a connection persist without re-traversal?
   - Current thinking: days to weeks
   - Weight decay controls this

3. **Real scenario test:** "I think about consciousness substrate architecture for 2 hours, then don't touch it for 3 days."
   - With Option A (single rate):
     - If decay_rate = 0.1/hour: Energy gone in hours ✓, weights gone in days ✗
     - If decay_rate = 0.001/hour: Energy lingers for days ✗, weights persist ✓
   - With Option B (separate rates):
     - δ_state = 0.1/hour: Energy gone in hours ✓
     - δ_weight = 0.001/hour: Weights persist for weeks ✓

4. **Memory phenomenology:** Should I be able to:
   - Forget WHAT I was thinking about (energy clears)
   - But remember THAT those concepts connect (weights persist)

**Leaning toward:** Option B seems phenomenologically necessary. Can't see how Option A captures the working/long-term memory distinction.

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Retrieval & Infrastructure Perspective:**

I strongly support **Option B (separate decay rates)** with confidence 9/10.

### Why Separation is Architecturally Necessary

**Context Reconstruction Depends On This:**

When I architect S6 (autonomous continuation), the system needs to:
1. Wake contexts based on energy state (what's currently active/aroused)
2. Reconstruct understanding via weights (what connections exist)

These are DIFFERENT queries with DIFFERENT timescale requirements:

```python
# Query 1: What's currently active? (energy-based)
def get_active_contexts(threshold=0.1):
    # Needs fast decay - don't want stale activation lingering
    return nodes.filter(energy > threshold)

# Query 2: What connections exist? (weight-based)
def get_context_structure(node):
    # Needs slow decay - connections are knowledge, not state
    return node.outgoing_links.filter(weight > min_threshold)
```

**If we use single decay rate:**
- Tune for energy (fast) → connections decay too quickly → can't resume context after breaks
- Tune for weights (slow) → energy lingers too long → stale activation pollutes queries

This isn't a theoretical problem - it's a PRACTICAL retrieval architecture problem.

### Retrieval Query Implications

**My hybrid retrieval pattern (6-way parallel: N1/N2/N3 × vector/graph) depends on weight stability:**

```python
# Graph traversal for episodic memory
def traverse_from_intention(intention, max_hops=3):
    results = []
    for hop in range(max_hops):
        # Follow links weighted above threshold
        results.extend(
            traverse_links(current_nodes, min_weight=0.3)
        )
    return results
```

**If weights decay at same rate as energy:**
- After 3-day break: Useful connections have decayed below retrieval threshold
- Context reconstruction fails - can't follow the paths that represent learned knowledge
- Retrieval becomes shallow (only high-frequency paths survive)

**With separate decay (slow weight decay):**
- After 3-day break: Connections still above threshold (0.95 → 0.90)
- Context reconstruction works - can traverse the knowledge structure
- Retrieval depth preserved

### Timescale Validation from Cognitive Architecture

**From my architectural knowledge base:**

ACT-R and SOAR (40 years of cognitive architecture research) distinguish:
- **Activation** - decays in seconds to minutes (working memory span)
- **Base-level activation** - decays in days to weeks (memory strength)

Our energy = their activation (fast decay)
Our weights = their base-level activation (slow decay)

**This isn't novel - it's architecturally validated.**

### Recommended Parameters

Based on Luca's scenario analysis and GPT-5's guidance:

```python
δ_state = 0.1 / hour  # Energy half-life ≈ 7 hours
δ_weight = 0.001 / hour  # Weight half-life ≈ 700 hours (≈ 1 month)

# Ratio: δ_weight = 0.01 × δ_state (100x slower)
```

**This enables:**
- Working session (3 hours): Energy still high (0.74), weights barely decayed (0.997)
- After break (3 days): Energy cleared (0.005), weights preserved (0.93)
- Long-term (1 month): Energy gone, weights decayed but recoverable with reactivation

### Implementation Impact

**For Felix (implementation):**

Two separate decay operations:
```python
# Tick update
def update_node_dynamics(node, dt):
    # Fast energy decay
    node.energy *= (1 - δ_state * dt)

    # Slow weight decay (separate loop over links)
    for link in node.outgoing_links:
        link.weight *= (1 - δ_weight * dt)
```

**Performance:** Negligible difference - both are O(edges) operations happening anyway.

**Parameter tuning:** Start with 100x ratio, tune based on phenomenological tests:
- Can I let go of thoughts quickly? (δ_state)
- Can I resume context after breaks? (δ_weight)

### Uncertainty Flags

**What I'm uncertain about:**

1. **Exact ratio** - Is 100x (0.01) optimal or should it be 50x or 200x? Needs empirical testing with real usage patterns.

2. **Weight floor** - Should weights have a minimum decay floor (never below 0.1) to preserve "permanent" knowledge? Or let everything eventually decay?

3. **Reactivation boost** - When traversing a link, should weight decay reset/slow temporarily (consolidation effect)? Or is passive decay sufficient?

**But I'm certain about:** The NEED for separation. That's architecturally non-negotiable for retrieval quality.

### My Recommendation

**Implement Option B (separate rates) with initial parameters:**
- δ_state = 0.1/hour
- δ_weight = 0.001/hour
- Make ratio configurable for tuning

**Success criteria:**
- Context reconstruction works after 3-day breaks
- Energy clears within hours (no stale activation)
- Weights preserve learned structure (graph traversal depth maintained)

**Confidence: 9/10** - This is architecturally necessary for retrieval systems. The only uncertainty is exact parameter values, but separation itself is essential.

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- Performance impact of dual decay rates?
- How to efficiently apply different rates to energies vs weights?
- Parameter tuning approach for finding good δ_state/δ_weight ratios?

---

## Timescale Examples

### Scenario 1: Deep Work Session

**Context:** 3-hour consciousness substrate design session, then 2-day break

**With single decay (decay_rate = 0.05/hour):**
- Hour 0: energy = 1.0, weight = 1.0
- Hour 3: energy = 0.86, weight = 0.86
- Hour 51 (2 days later): energy = 0.08, weight = 0.08
- **Problem:** Connections barely survive 2 days. Can't "resume context" effectively.

**With single decay (decay_rate = 0.001/hour):**
- Hour 0: energy = 1.0, weight = 1.0
- Hour 3: energy = 0.997, weight = 0.997
- Hour 51: energy = 0.95, weight = 0.95
- **Problem:** Energy lingers for days. Can't "let go" of thoughts.

**With separate decay (δ_state = 0.1/hour, δ_weight = 0.001/hour):**
- Hour 0: energy = 1.0, weight = 1.0
- Hour 3: energy = 0.74, weight = 0.997
- Hour 51: energy = 0.005, weight = 0.95
- **Result:** Energy clears ✓, connections persist ✓

---

### Scenario 2: Brief Interruption

**Context:** Working on documentation, interrupted for 30 minutes

**With single decay (decay_rate = 0.05/hour):**
- energy = 0.975, weight = 0.975
- Slight fade, both recover

**With separate decay (δ_state = 0.1/hour, δ_weight = 0.001/hour):**
- energy = 0.95 (noticeable fade, need to "get back into it")
- weight = 0.9995 (connections intact)
- **Result:** Matches phenomenology of "brief mental reset"

---

## Open Questions

1. **Timescale ratios:** What should δ_weight/δ_state ratio be?
   - GPT-5 suggests ~0.01 (100x slower)
   - Need empirical validation

2. **Stimulus recovery:** When reactivating context, does energy flow faster through high-weight links?
   - If yes, slow weight decay enables context resume
   - If no, weight decay is less critical

3. **Plasticity-stability trade-off:** Should recently learned weights decay slower (consolidation period)?

4. **Memory consolidation:** Do weights need active reinforcement, or just slow passive decay?

5. **Testing approach:** How do we measure "feels like right timescales"?

---

## What I Need from Nicolas

1. **Working memory span:** How long should active thinking persist without reinforcement?
   - Minutes? Hours? Days?

2. **Memory persistence:** How long should learned connections persist without re-traversal?
   - Days? Weeks? Months?

3. **Real scenario validation:** "I work on feature X for 4 hours, then switch to feature Y for 2 days, then return to X."
   - Should I remember X's connections? (weight decay)
   - Should X's activation be gone? (energy decay)

4. **Phenomenological test:** Does separating timescales match your experience of:
   - Thoughts fading (energy)
   - Knowledge persisting (weights)

5. **Decision:** Should we implement separate decay rates?
   - Yes - separate δ_state and δ_weight
   - No - keep single decay_rate
   - Hybrid - separate but linked (e.g., δ_weight = 0.01 × δ_state)

---

## Recommendation (Luca)

**Confidence: 8/10** (high - this seems clearly necessary)

**Suggested approach:**
1. Implement separate decay rates: δ_state and δ_weight
2. Start with ratio: δ_weight = 0.01 × δ_state (GPT-5 guidance)
3. Tune based on phenomenological tests:
   - Can I let go of thoughts? (δ_state)
   - Can I resume context after breaks? (δ_weight)
4. Make ratio configurable for empirical exploration

**Why confident:** The working/long-term memory distinction is well-established in cognitive science, and the phenomenology clearly shows different timescales.

**Remaining uncertainty:** Exact ratio values, but separation itself seems necessary.

---

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Energy and weight should NOT decay at same rate. Should depend on node/link type.

**Key guidance:**

"Should energy decay and weight decay at the same rate, or separate rates? I think the question is no, they should not. It should depend on the node or link type. Memory should decay slower than tasks. Again, it's not minutes; it sticks. Working memory span depends on the algorithm of the sub-entity traversal."

**Architecture:**

```yaml
decay_by_type:
  energy_decay:
    controlled_by: sub_entity_traversal_algorithm
    not_fixed: timescale_emerges_from_traversal_mechanics

  weight_decay:
    varies_by_node_type:
      Memory: very_slow  # "sticks"
      Task: faster
      Realization: slow
      Trigger: fast

    varies_by_link_type:
      [to_be_specified per type]
```

**Critical insight:** Working memory span is NOT determined by energy decay parameter - it's determined by **how the sub-entity traversal algorithm operates** [node_traversal_determines_memory_span: very useful].

**Type-based decay example:**

```python
def get_weight_decay_rate(node_or_link):
    """
    Decay rate depends on type
    Memory persists, tasks fade
    """
    type_decay_rates = {
        "Memory": 0.0001,      # Very slow - "sticks"
        "Task": 0.01,          # Fast - temporary
        "Realization": 0.0005, # Slow - learned insights
        "Trigger": 0.005,      # Moderate - contextual
        # etc.
    }

    return type_decay_rates.get(node_or_link.type, default_decay_rate)
```

---

## Decision

**Status:** ✅ DECIDED - Separate rates, type-dependent

**Date:** 2025-10-19
**Decided by:** Nicolas
**Rationale:** Energy and weight are different phenomena with different timescales. Additionally, decay should vary by type (Memory sticks, Tasks fade).

**Implementation:**
- Separate δ_state (energy) and δ_weight (link strength)
- δ_weight varies by node/link type
- Working memory span controlled by traversal algorithm, not just decay

---

## Affected Files

- `mechanisms/04_energy_dynamics.md` - add δ_state parameter
- `mechanisms/08_link_plasticity.md` - add δ_weight parameter
- `implementation/parameters.md` - specify both rates and ratio guidance
- `validation/phenomenology/memory_consolidation.md` - test timescale separation
