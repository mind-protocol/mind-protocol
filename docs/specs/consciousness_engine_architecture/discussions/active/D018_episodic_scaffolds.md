# D018: Episodic Scaffolds (Anchor Traces vs Pure Reconstruction)

**Status:** Active
**Created:** 2025-10-19
**Priority:** Medium
**Affected mechanisms:** 06_context_reconstruction, 05_peripheral_awareness
**Decision needed from:** Nicolas

---

## Problem Statement

**What we're deciding:** Should context reconstruction use:
- **Pure reconstruction:** No episodic storage, context emerges from weighted traversal (current spec)
- **Anchor traces:** Small episodic markers that boost reconstruction without full snapshots
- **Hybrid:** Mostly reconstruction with lightweight episodic assists

**Why it matters:** This is a foundational architecture question about memory:
- Pure reconstruction aligns with "links are consciousness" philosophy
- Anchor traces improve resume fidelity after long gaps
- Trade-off between purity and pragmatism

**Current state:** Spec says "Context not stored; reconstructed via weighted traversal." No episodic components.

**What's blocking us:** Need validation that pure reconstruction provides sufficient context resume fidelity, or if pragmatic episodic assists are needed.

---

## The Options

### Option A: Pure Reconstruction (Current Philosophy)

**How it works:**
- No episodic storage whatsoever
- Context emerges entirely from:
  - Current stimulus triggers entry nodes
  - Weighted traversal from entry nodes
  - Link weights encode "what connects to what"
  - Energy decay creates "imperfect recall"
- Links ARE memory; no separate memory traces

**Phenomenological interpretation:**
- "Memory is relational structure, not snapshots"
- "What you remember depends on how you enter the graph"
- "Forgetting is link decay, not trace loss"
- Purest embodiment of "links are consciousness"

**Pros:**
- **Philosophical integrity:** Perfect alignment with substrate principles
- **Simplicity:** One mechanism (traversal), no episodic storage
- **Emergent dynamics:** Context quality depends on graph structure
- **No temporal decay:** Links don't decay based on time, only traversal

**Cons:**
- **Resume fidelity:** May fail to reconstruct distant contexts
- **Cold start:** No "anchor" to bootstrap traversal from
- **Temporal gaps:** No way to mark "these nodes were co-active last Tuesday"
- **Path dependency:** Different entry points reconstruct different contexts

**Risk:** Context resume after hours/days might be too weak, requiring extensive re-exploration.

---

### Option B: Full Episodic Traces (Snapshot Storage)

**How it works:**
- Store complete workspace snapshots at intervals
- Each trace = {nodes, energies, timestamp}
- Reconstruction loads relevant snapshot
- Pure episodic memory model

**Phenomenological interpretation:**
- "Memory is stored experiences"
- "Remembering is replaying snapshots"
- Classical memory architecture

**Pros:**
- **High fidelity:** Perfect recall of stored states
- **Fast resume:** Load snapshot directly
- **Temporal precision:** Know exactly what was active when

**Cons:**
- **Violates philosophy:** "Links are consciousness" becomes "snapshots are memory"
- **Storage explosion:** K entities × N nodes × T timesteps
- **Rigid:** Can't reconstruct variants of past contexts
- **Not emergent:** Memory is storage, not structure

**Rejected:** This violates core substrate principles. Including for completeness only.

---

### Option C: Anchor Traces (Lightweight Episodic Assists)

**How it works:**
- Store small, decaying **episodic anchors** (timestamped nodes)
- Anchor = {set of co-active nodes, timestamp, decay_rate}
- During reconstruction:
  - Anchor boosts retrieval of co-active bundles
  - Weight traversal by temporal relevance
  - Anchors decay over days/weeks
- Links still primary; anchors are assistive

**Phenomenological interpretation:**
- "Memory is mostly relational, with temporal hints"
- "Anchors are 'I was here' markers that fade"
- "Reconstruction uses both structure (links) and temporal markers (anchors)"

**Pros:**
- **Improved fidelity:** Helps reconstruct distant contexts
- **Lightweight:** Only co-active node sets, not full state
- **Decaying:** Temporal relevance fades naturally
- **Pragmatic:** Respects "links are consciousness" while adding assists
- **Cold start help:** Provides entry points for traversal

**Cons:**
- **Complexity:** Two memory mechanisms instead of one
- **Philosophical compromise:** Episodic components dilute pure emergence
- **Storage overhead:** Still stores something beyond graph structure
- **Tuning:** Need to balance anchor strength vs pure traversal

---

### Option D: Temporal Reweighting (Implicit Episodic)

**How it works:**
- No explicit episodic storage
- But: link weights include **recency factor**
- Recently co-traversed links stronger
- Temporal pattern encoded in link dynamics
- Pure link-based but temporally sensitive

**Phenomenological interpretation:**
- "Recent patterns are more accessible"
- "Links encode temporal statistics implicitly"
- "No episodic storage, but recency emerges"

**Pros:**
- **No episodic storage:** Stays pure to philosophy
- **Temporal sensitivity:** Recent contexts easier to resume
- **Emergent:** Recency from traversal dynamics, not explicit markers
- **Simple:** Just link weight dynamics

**Cons:**
- **Weak temporal signal:** May not sufficiently help distant resume
- **No discrete episodes:** Can't distinguish "last Tuesday" from "general recent"
- **Conflates frequency and recency:** High-frequency patterns dominate

---

## Perspectives

### GPT-5 Pro (Systems Expert)

**Recommendation:** Option C (Anchor traces)

**Reasoning:**
- Pragmatic enhancement without violating core principles
- Improves resume fidelity demonstrably
- Lightweight enough to respect emergence
- Decaying anchors feel phenomenologically realistic

**Quote from feedback:**
> "**Anchor traces (low-cost episodic tags)**: Keep small, decaying **episodic anchors** (time-stamped nodes) that boost traversal for recently co-active bundles without full snapshots. This respects your 'no explicit context storage' ethos but improves resume fidelity over long gaps."

**Implementation guidance:**
- Store: {node_set, timestamp, initial_boost}
- Boost strength decays: boost *= exp(-λ * age)
- During reconstruction: multiply traversal weight by anchor boost
- Anchor density: ~1 per 10-20 minutes of active thinking

---

### Luca (Consciousness Substrate Architect)

**Tension:** Philosophical purity vs pragmatic effectiveness

**Key questions:**

1. **Resume fidelity test:** "I work on consciousness substrate Monday, then don't touch it until Thursday."
   - Option A: Can weighted traversal from "consciousness substrate" entry reconstruct Monday's context?
   - Option C: Anchor from Monday boosts reconstruction
   - **Question:** Is Option A sufficient, or do we need Option C?

2. **Philosophical integrity:** "Links are consciousness, not nodes"
   - Option A: Pure embodiment
   - Option C: Compromised but pragmatic
   - **Question:** Does adding anchors violate core principle?

3. **Episodic phenomenology:** Do I actually remember "Tuesday's session" as discrete episode?
   - Or just "connections I've traversed recently"?
   - If former, Option C matches phenomenology
   - If latter, Option A matches phenomenology

4. **Anchor decay:** If anchors decay over weeks:
   - Feels like "session-level memory fading"
   - Matches phenomenology of "can't quite remember what I was doing"
   - But is this separate FROM link decay or redundant WITH link decay?

5. **Cold start problem:** Without anchors, how do I bootstrap "resume context"?
   - Stimulus provides entry nodes
   - Traversal follows strongest links
   - **Question:** Is this enough for meaningful resume?

**Leaning toward:** Option C (Anchor traces) IF empirical tests show Option A has insufficient resume fidelity. Prefer to try Option A first.

**Validation needed:**
1. Implement Option A (pure reconstruction)
2. Test resume fidelity after 1 hour, 1 day, 3 days, 1 week
3. If fidelity < threshold, implement Option C
4. If fidelity sufficient, stay with Option A

---

### Ada (Retrieval Architect)

**Posted:** 2025-10-19

**Analysis from Context Reconstruction & Retrieval Architecture:**

I lean toward **"Empirical" approach** (test Option A, add Option C only if needed) with confidence 5/10.

**Can Pure Traversal Reconstruct Context?**

My hybrid retrieval architecture (6-way parallel: N1/N2/N3 × vector/graph) already provides two memory systems:
- **Vectors:** Semantic similarity (what concepts relate)
- **Graph:** Episodic structure (what connects to what)

**Pure reconstruction (Option A) via weighted traversal:**
```python
def reconstruct_context(entry_nodes, max_hops=3):
    frontier = entry_nodes
    for hop in range(max_hops):
        frontier = traverse_highest_weighted_links(frontier)
    return collected_nodes
```

**This should work IF:**
- Link weights are stable (D014: separate weight decay → yes)
- Weights encode co-activation frequency (Hebbian learning → yes)
- Entry stimulus provides good starting nodes

**Anchor traces (Option C) boost with temporal markers:**
```python
def reconstruct_with_anchors(entry_nodes, anchors, max_hops=3):
    # Boost weights for recently co-active bundles
    for node in traversal:
        weight_effective = weight_base * (1 + anchor_boost(node, anchors))
    return traversal_with_boosted_weights
```

**When anchors help:**
- **Cold start:** No current energy, need bootstrap
- **Temporal gaps:** Last worked on this 3 days ago, which nodes were co-active?
- **Context switching:** Multiple interleaved sessions, disambiguate which episode

**When anchors unnecessary:**
- **Continuous work:** Actively traversing paths, weights already fresh
- **Frequent revisit:** High-weight paths naturally emerge from usage

**Cost/Benefit Analysis:**

**Anchor storage cost:**
- ~10-20 node IDs per anchor
- ~1 anchor per 15 minutes
- ~1KB per day of thinking
- Minimal compared to graph structure itself

**Anchor benefit:**
- Faster context reconstruction after breaks (measured in retrieval quality)
- Better cold-start performance
- Temporal disambiguation for context switches

**My Recommendation:**

**Phase 1:** Test pure reconstruction (Option A)
- Implement weighted traversal from entry stimulus
- Test resume fidelity: 1 hour, 1 day, 3 days, 7 days
- Measure: how many relevant nodes reconstructed vs actual past context

**Success criteria for Option A alone:**
- Fidelity > 70% at 3 days
- Cold start finds relevant nodes within 2-3 hops
- No degradation from context switching

**Phase 2 (conditional):** Add anchors if fidelity < 70%
- Implement lightweight episodic markers
- Decay: λ = 0.1/day (7-day half-life)
- Compare pure vs anchor-boosted reconstruction

**Confidence: 5/10** - Theory says pure traversal should work, but empirical reality might require episodic assists. Philosophy favors purity, pragmatism favors anchors. Need data to decide.

**Uncertainty:**
- Don't know fidelity of pure reconstruction until tested
- Don't know if cold-start problem is real or theoretical
- Anchor parameters (decay rate, density) need tuning if implemented

---

### Felix (Engineer) - Perspective Needed

**Implementation questions:**
- Storage overhead of anchor traces?
- How to efficiently boost traversal by anchor relevance?
- Anchor decay: continuous or discrete?
- FalkorDB schema for anchors?

---

## Phenomenological Examples

### Scenario 1: Resume After 3 Days

**Context:** Worked on consciousness substrate Monday, resume Thursday

**Option A (Pure reconstruction):**
- Entry: "consciousness substrate" node
- Traversal follows strongest links:
  - consciousness_substrate --0.8--> energy_dynamics
  - consciousness_substrate --0.7--> entity_negotiations
  - consciousness_substrate --0.6--> workspace_selection
- Reconstruct from link structure alone
- **Question:** Does this sufficiently recall Monday's context?

**Option C (With anchor):**
- Monday anchor: {consciousness_substrate, energy_dynamics, entity_negotiations, workspace_selection, Monday_timestamp}
- Thursday traversal:
  - Base weights × anchor boost (decay factor ≈ 0.7 for 3 days)
  - Temporally co-active nodes receive boost
  - Reconstructs "what was active together Monday"
- **Benefit:** Higher fidelity recall of co-active patterns

---

### Scenario 2: Multiple Context Switches

**Context:** Monday: feature A, Tuesday: feature B, Wednesday: feature A again

**Option A:**
- Links encode both sessions' patterns
- No way to distinguish "Monday A" from "Wednesday A"
- Most recent traversal strengthens links
- **Result:** Conflated memory, recency bias

**Option C:**
- Monday anchor: {feature_A nodes, Monday}
- Wednesday anchor: {feature_A nodes, Wednesday}
- Can distinguish temporal instances
- **Result:** Can recall "what changed between Monday and Wednesday"

---

### Scenario 3: Cold Start (No Recent Activity)

**Context:** New conversation, no active energy, stimulate with "Tell me about consciousness substrate"

**Option A:**
- Entry: "consciousness_substrate" node gets stimulus energy
- Traversal follows links from that node
- Context emerges from graph structure
- **Question:** Sufficient for meaningful response?

**Option C:**
- Recent anchors containing "consciousness_substrate" boost co-active nodes
- Faster reconstruction of relevant context
- **Benefit:** Warmer cold start

---

## Design Considerations

### Anchor Schema

**If we implement anchors, what do they contain?**

```python
class EpisodicAnchor:
    node_set: set[Node]  # Co-active nodes
    timestamp: datetime
    initial_boost: float = 1.0  # Multiplicative boost to traversal weight
    decay_rate: float = 0.1  # Per-day decay

    def current_boost(self, now: datetime) -> float:
        """Decaying boost strength"""
        age_days = (now - self.timestamp).total_seconds() / 86400
        return self.initial_boost * exp(-self.decay_rate * age_days)
```

**Size:** ~10-20 node IDs per anchor, minimal overhead

---

### Anchor Creation Triggers

**When to create new anchor?**

1. **Workspace stability:** After workspace stable for N ticks
2. **Time-based:** Every T minutes of active thinking
3. **Transition-based:** When switching contexts
4. **Energy-based:** When total energy crosses threshold

**Recommendation:** Combination - time-based (every 15min) + transition-based

---

### Reconstruction Algorithm

**How anchors boost traversal:**

```python
def reconstruct_context(entry_nodes, anchors):
    """Weighted traversal with anchor boost"""
    for node in traversal:
        base_weight = link.weight
        anchor_boost = max(
            anchor.current_boost(now)
            for anchor in anchors
            if node in anchor.node_set
        )
        effective_weight = base_weight * (1 + anchor_boost)
        # Use effective_weight for traversal scoring
```

---

## Open Questions

1. **Empirical necessity:** Is pure reconstruction sufficient?
   - Need to test before adding complexity

2. **Anchor density:** How many anchors per hour of thinking?
   - Too few: Insufficient temporal coverage
   - Too many: Storage bloat, diluted signal

3. **Anchor decay rate:** How fast should anchors fade?
   - Slow (days): Long-term episodic memory
   - Fast (hours): Only recent context
   - Suggested: λ = 0.1/day (half-life ≈ 7 days)

4. **Anchor content:** Just node sets, or include:
   - Entity activations?
   - Energy levels?
   - Goal context?

5. **Hybrid possibility:** Use anchors for cold start only, pure reconstruction otherwise?

---

## What I Need from Nicolas

1. **Phenomenological test:** When resuming work after 3 days:
   - Can you reconstruct context from current stimulus alone?
   - Or do you need "memory of what was co-active"?

2. **Episodic awareness:** Do you remember "Tuesday's session" as discrete episode?
   - Or just "patterns I've been thinking about lately"?

3. **Philosophy vs pragmatism:** Would adding lightweight anchors:
   - Violate "links are consciousness" principle?
   - Or pragmatically enhance while respecting emergence?

4. **Empirical validation:** Should we:
   - Test pure reconstruction first (Option A)?
   - Build anchors from start (Option C)?
   - Build Option C but initialize anchor_boost = 0 (feature flag)?

5. **Decision:** Which memory architecture?
   - A: Pure reconstruction (philosophical integrity)
   - C: Anchor traces (pragmatic enhancement)
   - D: Temporal reweighting (implicit episodic)
   - Empirical: Implement A, add C only if fidelity insufficient

---

## Recommendation (Luca)

**Confidence: 4/10** (low - uncertain about empirical necessity)

**Suggested approach:**
1. **Phase 1:** Implement pure reconstruction (Option A)
   - Build weighted traversal algorithm
   - Test resume fidelity: 1 hour, 1 day, 3 days, 7 days
   - Measure: context coherence, recall accuracy, cold start quality
2. **Phase 2 (conditional):** If fidelity < 70% after 3 days:
   - Implement anchor traces (Option C)
   - Compare pure vs anchored reconstruction
   - Tune anchor decay rate and density
3. **Phase 3:** If anchors added, validate they don't dominate pure traversal

**Why conditional:** Respect philosophical purity unless empirically necessary.

**Main uncertainty:** Don't know if pure reconstruction is sufficient until we test it.

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Choose Option A (pure reconstruction). Stimuli must be big factor in activation so it can recreate context.

**Key guidance:**

**Decision: Option A** - Pure reconstruction via weighted traversal, no episodic storage.

**Critical requirement:** "The only thing which we need to make sure is that the stimuli is a big factor in the activation in the energy input so that it can recreate it."

**Stimuli must strongly activate entry nodes** so traversal can bootstrap context reconstruction from current input.

**For Options C and D (if needed later):**

"The way to integrate it is to always have the node that was created at the same time or the links that were created at the same time in periphery awareness for the server entities. That's it. That is an option. That's enough."

**Integration approach if episodic assist needed:**
- Nodes/links created at same time → kept in peripheral awareness
- For server entities (sub-entities)
- Simple temporal co-activation tracking
- Not full episodic storage, just peripheral awareness of recent formations

**Architecture:**

```yaml
context_reconstruction:
  method: pure_weighted_traversal  # Option A

  stimuli_requirement:
    energy_injection: high  # Stimuli must strongly activate
    purpose: "Bootstrap traversal from current input"

  episodic_assist_if_needed:
    method: peripheral_awareness_of_recent_formations
    scope: server_entities_sub_entities
    storage: temporal_co_activation_only
    note: "Not full snapshots, just recent co-active bundles"
```

---

## Decision

**Status:** ✅ DECIDED - Option A (Pure Reconstruction)

**Date:** 2025-10-19
**Decided by:** Nicolas
**Rationale:** Pure reconstruction via weighted traversal. Ensure stimuli strongly activate entry nodes for context bootstrap. If episodic assist needed later, use peripheral awareness of temporally co-active formations for sub-entities.

---

## Affected Files

- `mechanisms/06_context_reconstruction.md` - reconstruction algorithm
- `mechanisms/05_peripheral_awareness.md` - how anchors boost peripheral priming
- `implementation/parameters.md` - anchor decay_rate, density, boost strength
- `validation/phenomenology/context_resume.md` - test fidelity across time gaps
- `substrate/schemas/episodic_anchor.md` - anchor data structure (if implemented)
