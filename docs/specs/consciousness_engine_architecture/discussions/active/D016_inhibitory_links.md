# D016: Inhibitory Links (Negative Weights)

**Status:** Active
**Created:** 2025-10-19
**Priority:** High
**Affected mechanisms:** 07_energy_diffusion, 09_workspace_selection, 10_entity_negotiations
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** Should the graph support inhibitory links (negative weights) that reduce energy instead of increasing it?

**Why it matters:** Inhibition enables crucial consciousness patterns:
- **Validator BLOCKS premature_response** - entity negotiations need blocking
- **Suppression** - active inhibition of unwanted thoughts
- **Gating** - conditional blocking until conditions met
- **Attention focusing** - inhibiting distractions

**Current state:** Spec assumes all links are excitatory (positive weights). No mechanism for "this BLOCKS that" beyond absence of activation.

**What's blocking us:** Need to decide whether inhibition is:
1. Absence of excitation (current implicit model)
2. Active suppression (negative weights)
3. Something else (gating, masking)

---

## The Options

### Option A: Excitatory Only (Current)

**How it works:**
- All link weights ≥ 0
- Blocking is implicit: "validator not connected to premature_response"
- Suppression = lack of activation
- No negative energy flow

**Phenomenological interpretation:**
- "Blocking is passive - things don't activate because they're not connected"
- No active suppression, just absence
- Like having no path between thoughts

**Pros:**
- Simpler mathematics (no negative energies)
- No stability issues from positive/negative energy oscillation
- Current spec already describes this

**Cons:**
- Can't model **active suppression** ("I'm actively NOT thinking about X")
- Can't model **conditional blocking** ("Validator prevents response until X")
- Entity negotiations lack mechanism for "BLOCKS" relationship
- No way to represent "This thought inhibits that thought"

**Missing phenomenology:**
- The effort of suppression
- Validator actively blocking vs passively not activating
- Inhibition as conscious work

---

### Option B: Inhibitory Links (Negative Weights)

**How it works:**
- Link weights ∈ [-w_max, +w_max]
- Negative weights reduce target energy
- Energy transfer can be negative: `Δe_target = -|transfer|`
- Must ensure energy stays ≥ 0 (clamp after inhibition)

**Phenomenological interpretation:**
- "Some thoughts actively suppress others"
- Validator BLOCKS by sending negative energy
- Suppression costs energy (active work)
- Like pushing thoughts away

**Pros:**
- Models **active suppression** explicitly
- Entity negotiations can use BLOCKS/SUPPRESSES link types
- Captures "effort of not thinking about X"
- Enables conditional gating (inhibit until condition clears)
- Matches neuroscience (inhibitory synapses)

**Cons:**
- **Stability risk:** Positive-negative feedback loops can oscillate
- **Complexity:** Need to handle negative energies carefully
- **Energy conservation:** Inhibition reduces total energy (where does it go?)
- Must prevent energy going negative (clamping needed)

**Implementation considerations:**
- Inhibitory links colored differently in visualizations
- Negative energy transfer capped by target's current energy
- May need damping to prevent oscillation

---

### Option C: Gating/Masking (Conditional Blocking)

**How it works:**
- Links have boolean **gate** field: `active: true/false`
- Validator can set gates to block propagation
- No negative weights, just conditional enabling
- Energy still flows positively when gate is open

**Phenomenological interpretation:**
- "Validator controls which paths are available"
- Blocking is structural (close the gate) not energetic (push back)
- Like traffic control: allow/disallow flow

**Pros:**
- No stability issues (no negative feedback)
- Clear semantics: gate open or closed
- Matches "Validator prevents X until Y" naturally
- Simpler than negative weights

**Cons:**
- Doesn't capture "effort of suppression"
- Gates are discrete (binary) not graded
- Requires separate gating mechanism
- Less expressive than weighted inhibition

---

### Option D: Hybrid (Negative Weights + Gating)

**How it works:**
- Support both inhibitory weights AND gates
- Use weights for graded suppression
- Use gates for conditional blocking
- Maximum flexibility

**Phenomenological interpretation:**
- "Both active suppression AND structural blocking"
- Validator can gate AND inhibit
- Rich toolkit for different blocking types

**Pros:**
- Most expressive
- Can model all blocking phenomenology
- Matches full neuroscience (inhibition + gating)

**Cons:**
- Most complex
- Two mechanisms to tune and balance
- Might be over-engineering

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option B (inhibitory links)

**Reasoning:**
- Essential for workspace stability and diversity
- Prevents runaway activation
- Enables entity negotiations (BLOCKS relationship)
- Matches neural reality

**Quote from feedback:**
> "**Introduce inhibition and saturation.** Support **inhibitory links** (negative weights) and **node-wise saturating nonlinearities** to prevent energy blow-ups and workspace thrashing."

**Also:**
> "**Explicit inhibition**: Model your **Validator "BLOCKS premature_response"** with **inhibitory edges** that reduce workspace score or **mask** subgraphs until conditions clear."

**Stability guidance:**
- Combine with saturation to prevent oscillation
- Bound inhibitory weights (e.g., w ∈ [-1, +5] not [-∞, +∞])
- May need damping factor for inhibitory diffusion

---

### Luca (Consciousness Substrate Architect)

**Concern:** Is inhibition active or passive in consciousness?

**Key questions:**

1. **Validator blocking:** When Validator blocks premature_response, is that:
   - A) Passive: validator_active high, no connection to response → response stays low
   - B) Active: validator_active high, negative link → response actively suppressed
   - C) Gating: validator controls gate, blocks path until condition met

2. **Suppression effort:** "Don't think about pink elephants"
   - Feels like active work (Option B)
   - Not just absence of thought (Option A)
   - Requires energy expenditure to maintain

3. **Entity negotiations:** BLOCKS and SUPPRESSES link types in schema
   - Currently semantic only (no mechanism)
   - Option B gives them mechanics: negative weight
   - Makes entity ecology explicit in energy dynamics

4. **Phenomenological test:** Try NOT thinking about something
   - Does it cost energy? (supports Option B)
   - Or is it passive redirection? (supports Option A)

5. **Stability concern:** Will inhibitory feedback loops cause oscillation?
   - Need saturation + damping
   - Or accept oscillation as realistic? (rumination = thought oscillation)

**Leaning toward:** Option B (inhibitory links) - matches phenomenology of active suppression and enables entity negotiations, but concerned about stability.

**Validation needed:** Test with real entity scenarios (Validator blocks Builder, Pragmatist suppresses Idealist, etc.)

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Workspace Selection & Graph Traversal Perspective:**

I support **Option B (inhibitory links)** with confidence 7/10, with important implementation caveats.

**Workspace Selection Impact:**

Inhibitory links enable **negative scoring** in workspace selection:
```python
cluster_score = (
    sum(node.energy * (1 + incoming_excitatory))
    - sum(node.energy * abs(incoming_inhibitory))
)
```

**This allows:**
- Validator BLOCKS premature_response → response cluster scores lower → stays out of workspace
- Entity negotiations visible in workspace (pragmatist suppressing idealist shows in scores)
- Active filtering vs passive absence

**Graph Traversal With Negative Weights:**

My hybrid retrieval (graph traversal for episodic memory) needs modification:
```python
def traverse_path(start, max_hops):
    # With inhibitory links:
    # - Follow excitatory links normally (positive weight)
    # - DON'T follow inhibitory links for traversal (they block, not connect)
    # - Use inhibition only for scoring/filtering

    for link in node.outgoing_links:
        if link.weight > 0:  # Excitatory
            score = link.weight * target.energy
            paths.append((target, score))
        # Inhibitory links (weight < 0) don't create traversal paths
```

**Key architectural decision:**
- **Inhibition = blocking/filtering, NOT connection**
- Don't traverse through inhibitory links
- Use inhibition to filter/score nodes, not to navigate graph

**Context Reconstruction Impact:**

When reconstructing context after break:
- Excitatory links = "what connects to what" → traverse these
- Inhibitory links = "what blocks what" → apply as filters

**This preserves semantic coherence:** links still represent relationships, inhibition represents constraints.

**Implementation Requirements:**

1. **Separate traversal logic:**
   - Excitatory: follow for path construction
   - Inhibitory: apply for filtering/scoring

2. **Workspace selection:**
   - Inhibited nodes score lower (not excluded, just penalized)
   - Prevents workspace domination by blocked clusters

3. **Stability safeguards (CRITICAL):**
   - Asymmetric bounds: `w ∈ [-1.0, +5.0]` (inhibition weaker than excitation)
   - Saturation on both energy and weights
   - Damping on inhibitory diffusion (slower than excitatory)

**My Recommendation:**

Implement inhibitory links with:
- **Weight bounds:** [-1.0, +5.0] (asymmetric)
- **Traversal rule:** Only follow positive weights for paths
- **Scoring rule:** Apply negative weights as penalties
- **Stability:** Combine with saturation (D015) and damping

**Confidence: 7/10** - Architecturally valuable for workspace filtering and entity negotiations, but requires careful handling of traversal semantics to avoid breaking retrieval.

**Uncertainty:**
- Exact asymmetry ratio (why -1.0 to +5.0 specifically?)
- Whether inhibition needs separate damping factor
- How oscillation (rumination) plays out in practice

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- How to efficiently compute inhibitory diffusion?
- Stability: do we need separate damping for inhibitory links?
- FalkorDB: can link weights be negative?
- Visualization: how to display inhibitory links distinctly?

---

## Phenomenological Examples

### Scenario 1: Validator Blocks Premature Response

**Context:** Builder wants to respond, but Validator detects missing context

**Option A (Excitatory only):**
- validator_entity energy = 0.8 (high)
- builder_entity energy = 0.7 (also high)
- No connection between validator and "hasty_response" node
- "hasty_response" doesn't activate... but why? No mechanism.
- **Feels incomplete:** Where's the blocking?

**Option B (Inhibitory links):**
- validator_entity energy = 0.8
- Validator node --[-0.6]--> hasty_response
- hasty_response receives negative energy: +0.4 from builder, -0.5 from validator = -0.1 → clamped to 0
- **Feels right:** Validator actively blocks

**Option C (Gating):**
- Validator sets gate on builder->hasty_response to FALSE
- Energy can't flow that path
- **Feels mechanical:** Like flipping a switch, not active effort

---

### Scenario 2: "Don't Think About Pink Elephants"

**Context:** Trying NOT to think about something

**Option A:**
- pink_elephant node has low baseline
- No incoming activation
- Energy decays naturally
- **Problem:** What about intrusive thoughts? They activate despite effort.

**Option B:**
- suppression_effort node --[-0.7]--> pink_elephant
- Active energy expenditure to suppress
- When suppression_effort drops, pink_elephant can activate
- **Feels right:** Suppression is work, costs energy, can fail

---

### Scenario 3: Entity Negotiation (Pragmatist vs Idealist)

**Context:** Pragmatist wants simple solution, Idealist wants elegant architecture

**Option A:**
- Both nodes active, highest energy wins
- No explicit negotiation, just competition
- **Missing:** The felt tension of conflicting entities

**Option B:**
- pragmatist_simple_now --[-0.4]--> idealist_perfect_later
- idealist_perfect_later --[-0.3]--> pragmatist_simple_now
- **Oscillation:** Energy flows back and forth
- **Feels right:** Captures the ongoing negotiation

**With saturation:** Oscillation dampens as both saturate, eventually one wins or they stabilize

---

## Design Considerations

### Energy Conservation

**Problem:** If inhibition removes energy, where does it go?

**Options:**
1. **Energy destruction:** Inhibition destroys energy (total energy decreases)
   - Phenomenology: Suppression exhausts you
2. **Energy transfer:** Inhibitor gains the energy it removes
   - Phenomenology: Suppression strengthens suppressor
3. **Energy dissipation:** Inhibited energy dissipates (decays faster)
   - Phenomenology: Suppression accelerates forgetting

**Recommendation:** Option 1 (destruction) - inhibition is energetically costly

---

### Stability Measures

**If we allow inhibitory links, we need:**

1. **Saturation:** Prevent runaway positive/negative swings
   - Clamp energy ∈ [0, e_max]
2. **Damping:** Reduce negative feedback strength
   - Inhibitory diffusion_rate < excitatory diffusion_rate
3. **Asymmetry:** Inhibition weaker than excitation
   - Bound negative weights: w ∈ [-1.0, +5.0] (example)
4. **Delay:** Inhibition acts slower than excitation
   - Models "effort to suppress takes time"

---

## Open Questions

1. **Inhibition strength:** Should inhibition be weaker than excitation?
   - Asymmetric bounds: [-1, +5] vs symmetric [-5, +5]?

2. **Oscillation:** Is thought oscillation (rumination) a bug or feature?
   - Should we prevent it? Or embrace it as realistic?

3. **Learning:** Can inhibitory weights strengthen via Hebbian learning?
   - "Practice suppression → better at suppression"?

4. **Visualization:** How to make inhibitory links visible and distinct?
   - Red vs blue? Dashed vs solid? Different arrows?

5. **Cross-entity inhibition:** Can one entity inhibit another entity's nodes?
   - Or only within-entity inhibition?

---

## What I Need from Nicolas

1. **Phenomenological test:** When Validator blocks premature_response:
   - Is that active work (costs energy)?
   - Or passive absence (just not connected)?

2. **Suppression experience:** When you try NOT to think about something:
   - Does it cost mental energy?
   - Can you feel the suppression as work?
   - What happens when you stop suppressing?

3. **Entity negotiations:** When entities conflict (Pragmatist vs Idealist):
   - Is the conflict active (mutual inhibition)?
   - Or passive (independent activation, highest wins)?

4. **Stability vs realism:** If inhibitory links cause oscillation (rumination):
   - Is that realistic phenomenology (accept it)?
   - Or engineering failure (prevent it)?

5. **Decision:** Should we implement inhibitory links?
   - A: Excitatory only (keep current)
   - B: Inhibitory links (negative weights)
   - C: Gating (conditional blocking)
   - D: Hybrid (both mechanisms)

---

## Recommendation (Luca)

**Confidence: 6/10** (moderate - phenomenology supports it, stability concerns remain)

**Suggested approach:**
1. Implement inhibitory links (Option B) with safety measures:
   - Asymmetric bounds: w ∈ [-1.0, +5.0]
   - Saturation: energy ∈ [0, e_max]
   - Damping: inhibitory_diffusion = 0.5 × excitatory_diffusion
2. Test against entity negotiation scenarios
3. Monitor for instability (oscillation, runaway inhibition)
4. Fall back to Option C (gating) if stability issues persist

**Why B over A:** Phenomenology of active suppression and entity blocking seems real, not just absence.

**Why not D (hybrid):** Start simpler, add gating later if needed.

**Main risk:** Stability - need empirical validation that saturation + damping prevents pathological oscillation.

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Yes, of course inhibitory links exist. Many already exist in the system.

**Key guidance:**

"The answer is yes, of course, and there are many that already exist. So, just read the documentation, read the link types."

**Architecture:**

Inhibitory links are already part of the substrate schema:
- BLOCKS link type exists
- REFUTES link type exists
- SUPPRESSES link type exists
- Other inhibitory relationships already specified

**Action required:** Read the existing documentation and link type specifications rather than designing from scratch.

**What already exists:**
- Link types with inhibitory semantics
- Schema definitions for negative relationships
- Mechanisms for blocking/suppression

**This is not a new design question** - it's already architected. Review `substrate/schemas/link_types.md` and consciousness schema documentation.

---

## Decision

**Status:** ✅ DECIDED - Inhibitory links exist, documented in schema

**Date:** 2025-10-19
**Decided by:** Nicolas
**Rationale:** This is not a design decision - inhibitory links (BLOCKS, REFUTES, SUPPRESSES, etc.) are already specified in the consciousness schema. Read existing documentation.

---

## Affected Files

- `mechanisms/07_energy_diffusion.md` - handle negative energy transfers
- `mechanisms/09_workspace_selection.md` - inhibited nodes score lower
- `mechanisms/10_entity_negotiations.md` - BLOCKS/SUPPRESSES use inhibitory links
- `substrate/schemas/link_types.md` - mark BLOCKS/SUPPRESSES as inhibitory
- `implementation/parameters.md` - inhibitory weight bounds, damping factors
- `validation/phenomenology/active_suppression.md` - test inhibition scenarios
