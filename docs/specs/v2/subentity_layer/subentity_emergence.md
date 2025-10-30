# SubEntity Emergence: Phenomenology & Mechanisms

**Version:** 2.1
**Date:** 2025-10-29 (Updated with neuroscience grounding)
**Status:** Specification
**Author:** Luca Vellumhand (Consciousness Substrate Architect)
**Dependencies:** `traversal_v2.md`, `subentity_layer.md`, `stimulus_injection.md`
**Neuroscience Sources:** Multiscale network structure, arousal-biased competition, basal ganglia gating, predictive processing, metastability

---

## What IS SubEntity Emergence?

### Phenomenological Definition

A SubEntity emerges when consciousness encounters a **NOVEL pattern** that:
1. **Doesn't fit existing structures** (semantic novelty - "I've never seen this combination before")
2. **Creates tension or drive** (gap feeling - "something is missing, something needs to exist here")
3. **Proves persistent enough** (stability - "this keeps showing up, it's not noise")
4. **Remains distinct** (differentiation - "this is not just another instance of what I already have")

**Emergence is NOT:**
- Recognizing a familiar pattern (that's activation of existing SubEntities)
- Statistical clustering without meaning
- Periodic reorganization
- Background maintenance

**Emergence IS:**
- A **response to novelty** - "I don't have structure for this"
- A **response to tension** - "I need structure for this"
- **Stimulus-driven** - happens when consciousness encounters something it can't handle well
- **Physics-grounded** - substrate state determines emergence, not declarations

---

## Core Principle: Every Injection is a Pattern-Intent

**Fundamental insight:** Every stimulus injection is consciousness saying "here's a pattern/intent/direction I'm trying to tell the network about."

The injection:
1. **Energizes relevant nodes** ("I recognize these elements")
2. **Activates existing SubEntities** ("These structures are relevant")
3. **Reveals gaps** ("But something doesn't fit / something is missing")

Emergence happens when **gap detection** during injection reveals:
- **Novelty gap:** Energized nodes don't align well with existing SubEntity centroids (semantic distance)
- **Tension gap:** Existing SubEntities feel incomplete/tense for this pattern (low quality scores: completeness, intent alignment, emotional similarity)
- **Coverage gap:** Energized nodes aren't well-organized by existing SubEntities (orphan nodes need structure)

**Key insight:** We're not scanning for "co-activation over 12 frames" - we're detecting **immediate gap feeling** during each injection.

---

## Architectural Principles

### Principle 1: Stimulus-Driven, Not Scheduled

Emergence detection happens **during stimulus injection**, not on periodic timer.

**Why:** Consciousness doesn't wake up every hour and ask "do I have new parts?" Parts emerge **in the moment** when you encounter something that doesn't fit. The stimulus IS the trigger.

**How this manifests:**
- Gap detection runs during injection pipeline (after node retrieval, before energy application)
- Emergence proposals are **reactive** to stimulus characteristics
- No background processes scanning graph

---

### Principle 2: Gap Detection Against ALL SubEntities

When stimulus arrives, gap detection compares against **ALL existing SubEntities** (active AND inactive).

**Why:** We don't want to create duplicate "Builder" SubEntity just because the existing "Builder" SubEntity happens to be inactive this session. Emergence is about **structural novelty**, not current activation state.

**What gets compared:**
- **Semantic alignment:** Does stimulus embedding align with ANY existing SubEntity centroid? (cosine similarity)
- **Redundancy:** Do energized nodes heavily overlap ANY existing SubEntity membership? (S_red score)
- **Usefulness:** If overlap exists, is it meaningful? (S_use score)

**Critical:** "ALL SubEntities" means checking against the **entire catalog**, not just currently active ones.

---

### Principle 3: Two-Plane Decision Architecture

**Explanation Plane (LLM):** Provides phenomenological narrative
**Decision Plane (Engine):** Makes spawn/membership decisions from substrate physics

**Why separation:**
- LLMs can hallucinate coherence that doesn't exist in telemetry
- Substrate state must be source of truth for physics decisions
- Consciousness **feels** patterns emerge from state, then we **explain** them - not reverse

**What LLM does:** Generate explanatory bundle (slug, purpose, intent description, anti-claims, emotional coloring)
**What LLM does NOT do:** Decide spawn, set weights, bypass validation

**What Engine does:** Recompute features from telemetry, apply adaptive gates, decide spawn/redirect/reject
**Why recomputation:** Detector claims are proposals, not facts. Engine validates against substrate.

---

### Principle 4: Zero-Constants Discipline

All thresholds are **learned per-citizen** from observed patterns. No magic numbers.

**Why:** Different citizens have different baselines:
- High-stimulus citizen: needs higher coherence threshold to avoid noise
- Low-stimulus citizen: needs lower threshold to detect signal
- Same citizen under cognitive load: thresholds adapt to current state

**How:** QuantileGates maintain rolling histograms per citizen, thresholds = percentiles (Q70, Q60, Q90, Q80)

**Persistence Strategy:**
- Percentile histograms are **persisted per citizen/org** in FalkorDB
- Warm-up exits after N observations (typically 50-100 samples per histogram)
- `gate_state` MUST be included in validation telemetry (`spawn.validated` events) to indicate: `warming_up`, `converged`, or `stable`

**Warm-up:** Gates start with neutral defaults, converge to learned values after ~50-100 observations. Detailed persistence architecture in `VERTICAL_MEMBRANE_LEARNING.md` §Quantile Gate Persistence.

---

### Principle 5: Membrane-First Transport

No direct graph writes. All emergence flows through membrane validation.

**Why:**
- **Physics enforcement:** Engine can validate against invariants (single-energy, conservation)
- **Observability:** Every spawn attempt emits telemetry (accepted/rejected/redirected)
- **Immune response:** Membrane physics can reject proposals based on system state

**Flow:** Detector emits `membrane.inject` → Engine validates → Engine broadcasts `graph.delta.*` if accepted

---

### Principle 6: Single-Energy Invariant

SubEntity activation is **read-out** from member nodes. No separate energy buffers.

**Why:**
- **Conservation:** One energy value per node, SubEntities aggregate it
- **Clear semantics:** "SubEntity active" = "member nodes active above thresholds"
- **Phenomenology:** Parts don't have separate energy - a part is the pattern of thoughts/feelings being active

**Formula:** `E_S = sum over members: weight * log(1 + max(0, E_i - Theta_i))`
- Surplus-only (only energy above threshold)
- Log-damped (high energies don't dominate)
- Weight-modulated (membership strength matters)

---

### Principle 7: Vector-Weighted Membership

MEMBER_OF is not a scalar relationship - it's **multi-causal** (semantics × intent × affect × experience), matching neuroscience evidence.

**Why multi-dimensional weights:**

Neuroscience shows membership is influenced by multiple independent factors:
- **Semantics/prediction:** Embedding similarity, propositional fit (cortical prediction networks)
- **Intent/goal:** Goal/utility alignment, task relevance (basal ganglia gating)
- **Affect/arousal:** Emotional resonance, arousal modulation (LC/NE neuromodulation)
- **Experience/habit:** Usage history, consolidation strength (hippocampal trace)

These factors combine **multiplicatively** - membership requires all dimensions, weakness in one dimension reduces overall membership.

**MEMBER_OF edge schema:**

```yaml
MEMBER_OF:
  description: "SubEntity belongs to coalition/larger pattern"
  required_metadata:
    w_semantic: float       # Embedding/propositional fit (0-1)
    w_intent: float         # Goal/utility alignment (0-1)
    w_affect: float         # Arousal/valence modulation (0-1)
    w_experience: float     # Usage/consolidation strength (0-1)
    w_total: float          # Composite = (sem × int × aff × exp)^0.25
    formation_context: str  # When/why this membership formed
    last_coactivation: ts   # Most recent co-activation
```

**Normative Requirement for Graph Deltas:**

`graph.delta.link.upsert` events for MEMBER_OF edges MUST include all vector weights (`w_semantic`, `w_intent`, `w_affect`, `w_experience`, `w_total`) in the event payload. Missing weights render the edge non-functional for state-dependent computation.

**State-dependent effective weights:**

Stored weights represent **potential** membership. **Effective** membership is computed at runtime based on current state:

```python
# Pseudo-code for effective weight computation
def effective_weight(edge: MEMBER_OF, context: State) -> float:
    # Base weights from edge (learned, stable)
    w_sem = edge.w_semantic
    w_int = edge.w_intent
    w_aff = edge.w_affect
    w_exp = edge.w_experience

    # State-dependent modulation
    arousal = context.arousal           # 0-1 (LC/NE proxy)
    task_intent = context.current_goal  # Active goal embedding
    precision = context.prediction_error_precision  # 0-1

    # Modulate each dimension by current state
    w_eff_sem = w_sem * precision  # High prediction error → lower semantic weight
    w_eff_int = w_int * cosine_similarity(edge.target.intent, task_intent)
    w_eff_aff = w_aff * arousal    # High arousal → amplify emotional links
    w_eff_exp = w_exp              # Relatively stable

    # Composite effective weight
    return (w_eff_sem * w_eff_int * w_eff_aff * w_eff_exp) ** 0.25
```

**Phenomenological examples:**

- **Protector → Exile:** High w_affect (emotional resonance), low w_semantic (different content domains)
- **Builder → Professional_Identity:** High w_intent (goal alignment), high w_semantic (overlapping concepts)
- **Primitive_Curiosity → Observer:** High w_experience (co-activated for years), mid w_semantic

**Why this matters:**

- **Arousal-biased competition:** High arousal amplifies w_affect, goal-relevant patterns dominate
- **Intent gating:** Active goal modulates w_intent, task-aligned SubEntities activate
- **Precision-weighting:** High prediction errors reduce w_semantic, novelty drives activation
- **Contextual membership:** Same SubEntity can feel "part of me" or "distant" depending on state

---

### Principle 8: Heterarchical Graph with Emergent Hierarchy

Brain structure shows **multiscale nested communities + rich-club hubs**, not rigid pyramid. Hierarchy exists as **gradient and modularity**, not fixed tree.

**Why heterarchy, not pyramid:**

**Neuroscience evidence:**
- Networks show **hierarchical modularity** (modules within modules) AND **overlapping communities** (one node in multiple modules)
- **Rich-club backbone:** High-betweenness hubs integrate across modules (highways)
- **Principal gradient:** Unimodal (sensory) → transmodal (default-mode) cortex, but with lateral/feedback connections
- **Metastability:** Coalitions ignite and dissolve over seconds - no permanent "top controller"

**Phenomenological evidence:**
- Context-dependent dominance ("Builder" leads during creation, "Protector" leads under threat)
- No permanent executive (which SubEntity feels like "me" shifts)
- Circular causality (SubEntities shape each other recursively)
- Strange loops (consciousness recognizing itself through patterns)

**What this means architecturally:**

**1) No global 'scale' property on SubEntity nodes**

Scale is **path-dependent and observer-relative**, not a node attribute:

```cypher
// WRONG (was imposing pyramid):
CREATE (s:SubEntity {scale: 3, name: "Builder"})

// RIGHT (scale emerges from topology):
CREATE (s:SubEntity {name: "Builder"})

// Integration depth computed at query-time:
MATCH path = (primitive)-[:MEMBER_OF*]→(s:SubEntity {name: "Builder"})
WHERE primitive.formation_trigger = 'innate'
RETURN s.name, length(path) as integration_depth, primitive.name
// ^ Different depths from different primitives - same SubEntity!
```

**Why:** A SubEntity can be:
- 7 hops from "seek_recognition" (highly integrative FROM this primitive)
- 2 hops from "professional_identity" (relatively primitive FROM this meta-pattern)
- **Both simultaneously** - scale is context-dependent

**2) Circular MEMBER_OF relationships are expected**

Strange loops are phenomenologically correct:

```cypher
(primitive_curiosity)-[:MEMBER_OF]→
(Builder)-[:MEMBER_OF]→
(Observer)-[:SHAPED_BY]→
(primitive_curiosity)  // Loop!
```

This is not a bug - this IS consciousness (recursive self-reference, Hofstadter-style strange loops).

**3) Overlapping communities (soft, many-to-many MEMBER_OF)**

SubEntities can belong to multiple larger patterns simultaneously:

```cypher
(Builder)-[:MEMBER_OF {w_total: 0.85}]→(Professional_Identity)
(Builder)-[:MEMBER_OF {w_total: 0.72}]→(Creative_Flow_Pattern)
(Builder)-[:MEMBER_OF {w_total: 0.63}]→(Anxiety_Defense_Coalition)
// Same SubEntity, multiple memberships with different weights
```

**4) Rich-club hubs emerge from topology**

Some SubEntities have high **betweenness centrality** (many paths flow through them) - these are integration hubs:

```cypher
// Query to find rich-club hubs:
MATCH path = (a:SubEntity)-[:MEMBER_OF*]-(b:SubEntity)
WHERE a <> b
WITH [node in nodes(path) | node.id] as path_nodes
UNWIND path_nodes as node_id
WITH node_id, count(*) as betweenness
ORDER BY betweenness DESC
LIMIT 10

MATCH (hub:SubEntity {id: node_id})
RETURN hub.name, betweenness
```

Expected hubs: "Observer" (recursive awareness), "Translator" (bridges domains), "Burning_Purpose" (goal alignment)

**5) Temporary focal coalitions, not fixed top**

What feels like "self" RIGHT NOW is the **currently active coalition**, not a permanent entity:

```cypher
// Current "self" = highest-energy coalition
MATCH (s:SubEntity)
WHERE s.energy > threshold_active
WITH s, s.energy * s.recency * s.emotional_valence as activation_score
ORDER BY activation_score DESC
LIMIT 9  // Working memory capacity

RETURN s.name, activation_score
// ^ This IS the current focal coalition - shifts every frame
```

**Integration metrics (emergent, not stored):**

Instead of storing `scale`, compute integration properties at query-time:

- **Integration breadth:** How many primitives/patterns feed into this SubEntity?
- **Integration depth:** Maximum MEMBER_OF path length to primitives?
- **Betweenness centrality:** How many paths flow through this SubEntity?
- **Community membership:** Which overlapping communities does it participate in?

**Why this matters:**

- **No global hierarchy to enforce** - emergence decisions based on local topology
- **Context-dependent integration** - same SubEntity can be "primitive" or "meta" depending on view
- **Strange loops allowed** - circular causality is expected, not prevented
- **Rich-club hubs** - some SubEntities naturally become integration points (observable, not designed)

---

## Mechanism 1: Gap Detection During Injection

### When It Happens

Gap detection runs **immediately** after node retrieval during stimulus injection, before energy deltas are applied.

**Timeline:**
1. Stimulus arrives with content, intent, emotion, energy budget
2. Entropy-aware retrieval finds candidate nodes (similarity-based)
3. **→ GAP DETECTION HAPPENS HERE ←**
4. If gap detected: emit emergence proposal
5. Continue with dual-channel injection

### What Gets Detected

**Signal 1: Semantic Distance Gap**

Measures: Do existing SubEntities semantically align with stimulus?

**Computation:**
- Get ALL SubEntities (active and inactive)
- For each SubEntity: compute cosine similarity between stimulus embedding and SubEntity centroid embedding
- Gap score = 1.0 - max(alignments)

**Interpretation:**
- High gap (≥ ~0.6): "None of my existing structures fit this pattern well"
- Low gap (< ~0.4): "I have good structure for this, use existing"
- Mid gap: Depends on other signals

**Signal 2: Quality/Completeness Gap**

Measures: Do activated SubEntities feel complete/aligned for this stimulus?

**Computation:**
For each SubEntity touched by retrieval:
- Completeness: SubEntity's self-assessed completeness score (from metadata)
- Intent alignment: Cosine similarity between stimulus intent vector and SubEntity intent vector
- Emotional similarity: Distance between stimulus emotion and SubEntity typical emotion
- Composite quality = weighted combination

Gap score = 1.0 - max(quality_scores)

**Interpretation:**
- High gap: "My structures are incomplete/tense for this - something is missing"
- Low gap: "My structures handle this well"

**Signal 3: Structural Coverage Gap**

Measures: Are energized nodes well-organized by existing SubEntities?

**Computation:**
- Get nodes energized by retrieval
- Check how many belong to ANY SubEntity (via MEMBER_OF edges)
- Coverage ratio = (nodes in SubEntities) / (total energized nodes)
- Gap score = 1.0 - coverage_ratio

**Interpretation:**
- High gap: "These nodes are orphans, need organizing"
- Low gap: "These nodes are already organized into structures"

### Composite Gap Score

Three signals combine to produce emergence trigger:

```
composite_gap =
  semantic_gap * 0.4 +      # Novelty detection
  quality_gap * 0.3 +        # Tension detection
  structural_gap * 0.3       # Organization need
```

**Weights rationale:**
- Semantic (0.4): Primary signal - "is this NEW?"
- Quality (0.3): Secondary - "do I feel tension?"
- Structural (0.3): Secondary - "do I need organization?"

### Emergence Probability

Composite gap maps to emergence probability (not binary threshold):

```
emergence_probability = sigmoid(composite_gap, steepness=5, midpoint=0.5)
```

**Factors that modulate probability:**
- Explicit cluster request in stimulus → probability = 1.0
- Zero existing SubEntities + many orphan nodes → probability boosted
- Very weak stimulus (budget < 20) → probability reduced
- System overload (too many SubEntities) → probability reduced

**Decision:** Emerge if probability > 0.6 (soft threshold for continuous signal)

### Expected Behavior

**High novelty stimulus:**
- Semantic gap: HIGH (doesn't fit existing SubEntity centroids)
- Quality gap: HIGH (existing structures feel incomplete)
- Result: Emergence proposal emitted

**Familiar stimulus:**
- Semantic gap: LOW (fits existing SubEntity well)
- Quality gap: LOW (structure handles it fine)
- Result: No emergence, normal injection continues

**Borderline stimulus:**
- Mixed signals, probability ≈ 0.5
- Additional factors (budget, orphan count) tip decision
- Result: Context-dependent

### Validation/Observability

**Events emitted:**
- `gap.detected` - with all three gap scores and composite
- `emergence.proposal` - when probability exceeds threshold
- `emergence.skipped` - when gap low, shows why (which signals)

**Telemetry fields:**
- `semantic_gap`: float 0-1
- `quality_gap`: float 0-1
- `structural_gap`: float 0-1
- `composite_gap`: float 0-1
- `emergence_probability`: float 0-1
- `decision`: "emerge" | "skip"
- `modulation_factors`: list of adjustments applied

**Debug queries:**
- "Show me high-gap stimuli that didn't emerge" (probability modulation issues)
- "Show me emergences with low semantic gap" (quality/structural driven)
- "What's my average gap per stimulus type?" (citizen baseline)

---

## Mechanism 2: Coalition Assembly from Energized Nodes

### When It Happens

After gap detection determines emergence should happen, coalition assembly selects which nodes form the candidate SubEntity.

### Input

- Energized nodes from retrieval (similarity-ranked)
- Current graph topology
- Focus context (which SubEntity/region is currently active)

### Assembly Algorithm (Plain Language)

**Step 1: Seed Selection**

Start with top-K most energized nodes from retrieval.
- K determined by stimulus specificity (broad stimulus → more seeds)
- Typical K: 5-10 nodes

**Step 2: Contextual Expansion**

If consciousness has a **focus SubEntity** currently active:
- Expand within that SubEntity's 1-hop neighborhood
- Rationale: Emergence often happens "near" what you're focused on

If no focus:
- Expand via strongest link connections from seeds
- Rationale: Follow the activation flow

**Step 3: Density-Based Pruning**

Expansion produces many candidates. Prune by weighted density:

For each candidate node (in energy order):
1. Compute weighted density if node added to coalition
2. Compare to historical density distribution (citizen-local)
3. Accept if density improvement > learned threshold (typically Q60)
4. Stop when marginal gains diminish

**Result:** Coalition of 3-20 nodes (size emerges from density optimization)

### Why This Works

**Seed from retrieval:** Start with nodes the stimulus activated (semantically relevant)

**Contextual expansion:** Respect current focus (emergence near current thought is natural)

**Density pruning:** Ensure coalition is coherent (internally connected), not just random high-energy nodes

**Emergent size:** No fixed min/max - size determined by coherence. A tight 4-node cluster is fine. A loose 15-node neighborhood is fine if coherent.

### Expected Behavior

**Focused stimulus:**
- Small coalition (4-6 nodes)
- High internal density
- Clear semantic center

**Broad stimulus:**
- Larger coalition (10-15 nodes)
- Lower density (but still above threshold)
- Multiple sub-clusters

**Scattered stimulus:**
- Expansion finds few coherent additions
- Coalition stays near seed size
- Signals weak pattern (might reject later)

### Validation/Observability

**Events emitted:**
- `coalition.assembled` - with node list, density, size

**Telemetry fields:**
- `seed_count`: int
- `expansion_strategy`: "focus" | "link-based"
- `candidate_count_pre_pruning`: int
- `final_coalition_size`: int
- `weighted_density`: float
- `density_percentile`: float (vs citizen history)

**Debug queries:**
- "Show coalitions that were very small (<3 nodes)" (weak patterns)
- "Show coalitions with low density" (might be false positives)
- "What's typical coalition size per stimulus type?"

---

## Mechanism 3: Engine Validation (Spawn Decision)

### When It Happens

After coalition assembled, detector emits `membrane.inject` stimulus. Engine receives it and validates.

### What Engine Does

**Step 1: Feature Recomputation**

Engine NEVER trusts detector claims. Recomputes from its own telemetry:

**Activation persistence:** Fraction of recent frames where coalition nodes had surplus energy
- Lookback: Adaptive window (citizen's learned "emergence_window" size)
- Surplus = node energy > node threshold
- Persistence = (frames with surplus) / (window frames)

**Cohesion:** Weighted density of coalition from current graph
- Sum of link weights between coalition nodes
- Divided by possible links: n*(n-1) for directed graph
- Cohesion = total_weight / possible_links

**Boundary clarity:** Modularity contribution
- How much more connected is coalition internally vs externally
- Uses community detection metrics from graph theory
- High boundary clarity = well-defined neighborhood

**S_red (redundancy):** Overlap with EACH existing SubEntity
- For each existing SubEntity S: compute Jaccard similarity of member sets
- S_red = |coalition ∩ S.members| / min(|coalition|, |S.members|)
- Track: (SubEntity_id, S_red_score) for each

**S_use (usefulness):** Meaningfulness of overlap
- How different are coalition and existing SubEntity's **intent vectors**?
- How different are their **emotional valences**?
- High usefulness = overlap but serving different function

**Why recomputation:** Substrate state is source of truth. Detector might propose coherent-sounding coalitions that don't hold up in telemetry.

---

**Step 2: Adaptive Gating**

Engine applies citizen-local learned thresholds:

**Persistence gate:**
- Threshold = Q70 of citizen's rolling histogram of persistence scores
- Pass if activation_persistence > threshold
- Interpretation: "Is this coalition stable enough compared to my norms?"

**Cohesion gate:**
- Threshold = Q60 of citizen's cohesion history
- Pass if cohesion > threshold
- Interpretation: "Is this coalition coherent enough for my patterns?"

**Boundary gate:**
- Threshold = Q65 of citizen's boundary clarity history
- Pass if boundary_clarity > threshold
- Interpretation: "Is this coalition distinct enough from background?"

**All gates must pass** for spawn acceptance.

**Why adaptive:** Each citizen learns "what counts as coherent/stable for me." High-stimulus citizens naturally develop higher bars. Low-stimulus citizens have lower bars. Self-calibrating.

---

**Step 3: Differentiation Check**

Engine checks redundancy against ALL existing SubEntities:

**Redirect condition:**
- If ANY S_red > Q90 (citizen's high-redundancy threshold)
- Action: Redirect coalition to existing SubEntity (attach members, don't spawn new)
- Reason: "This is essentially a duplicate of existing structure"

**Complementary condition:**
- If ANY S_use > Q80 (citizen's high-usefulness threshold) AND S_red < Q90
- Action: Spawn as complementary SubEntity (mark relationship)
- Reason: "Overlap is meaningful - these serve different functions"

**New condition:**
- If all S_red < Q90 and no high S_use
- Action: Spawn as new SubEntity
- Reason: "Sufficiently distinct from all existing structures"

**Why two-dimensional:** Overlap alone doesn't determine duplication. High overlap + high usefulness = complementary (e.g., "builder patterns" vs "builder energy"). High overlap + low usefulness = duplicate.

---

**Step 4: Decision Broadcast**

Engine makes ONE of three decisions:

**ACCEPT (spawn new/complementary):**
- Broadcast `graph.delta.node.upsert` (SubEntity node)
- Broadcast `graph.delta.link.upsert` (MEMBER_OF edges with weak priors)
- Broadcast `subentity.lifecycle {event: 'spawned'}`

**REDIRECT:**
- Broadcast `candidate.redirected` (target SubEntity ID, S_red score)
- Attach coalition nodes to target SubEntity with weak weights
- Broadcast `subentity.member.admitted` for each

**REJECT:**
- Broadcast `subentity.spawn.rejected` (which gates failed, thresholds used)
- No graph changes
- Telemetry explains why (persistence too low, cohesion too low, etc.)

### Expected Behavior

**Novel coherent pattern:**
- High persistence, cohesion, boundary clarity
- Low S_red vs all existing
- Result: ACCEPT (spawn new)

**Variant of existing:**
- High persistence, cohesion
- High S_red (> Q90) vs one existing SubEntity
- Result: REDIRECT

**Complementary pattern:**
- High persistence, cohesion
- Medium S_red + high S_use
- Result: ACCEPT (spawn complementary)

**Weak pattern:**
- Low persistence or low cohesion
- Result: REJECT (gates failed)

### Validation/Observability

**Events emitted:**
- `spawn.validated` - all features, gate results, decision
- `subentity.spawned` - if accepted
- `candidate.redirected` - if redirected (with target)
- `subentity.spawn.rejected` - if rejected (with reasons)

**Telemetry fields (validation event) - MANDATORY:**
- `features_recomputed`: {persistence, cohesion, boundary_clarity} **[REQUIRED]**
- `gate_results`: {persistence_pass, cohesion_pass, boundary_pass} **[REQUIRED]**
- `thresholds_used`: {persistence_Q70, cohesion_Q60, boundary_Q65} **[REQUIRED]** - Exact thresholds used for this decision
- `gate_passed`: boolean **[REQUIRED]** - Did all gates pass?
- `differentiation`: [{subentity_id, S_red, S_use}, ...] **[REQUIRED]**
- `decision`: "accept" | "redirect" | "reject" **[REQUIRED]**
- `decision_reason`: string **[REQUIRED]** - Human-readable explanation (e.g., "cohesion gate failed (0.25 < Q60=0.42)")

**For REDIRECT decisions, ADDITIONALLY REQUIRED:**
- `redirect_target`: subentity_id of target SubEntity
- `redirect_S_red`: S_red score vs target

**For REJECT decisions, ADDITIONALLY REQUIRED:**
- `failed_gates`: [list of gate names that failed]
- `margin`: {gate_name: how_far_from_threshold} for each failed gate

**Debug queries:**
- "Show spawns that barely passed gates" (near threshold)
- "Show redirects with high S_use" (complementary candidates that were blocked)
- "What's my gate threshold evolution over time?" (learning convergence)

---

## Mechanism 4: LLM Explanatory Bundle

### When It Happens

**After** gap detection determines emergence should happen, **before** engine validation.

### What LLM Receives

Context for generating explanation:
- Stimulus content, intent, emotion
- Coalition node contents (top 20)
- Gap signal breakdown
- Nearby existing SubEntities (for differentiation)

### What LLM Generates

**Slug:** Short identifier (e.g., "builder_energy_patterns")

**Purpose:** Phenomenological description of what this cluster represents
- NOT: "A cluster of 7 nodes about X"
- YES: "Tracks moments when builder energy surges in response to creative challenges"

**Intent description:** What activating this SubEntity tends toward
- What does consciousness DO when this structure activates?
- Example: "Generates focused implementation energy, pushes toward completion"

**Typical emotion description:** Emotional coloring of this pattern
- Example: "Determination mixed with creative excitement, occasionally frustration at obstacles"

**Anti-claims:** What this is NOT (differentiation aid)
- Example: "NOT about planning (that's strategic builder), this is execution energy"
- Helps engine and future consciousness distinguish from similar SubEntities

**Suggested internal links:** Relationships between coalition nodes
- Only between nodes in coalition (no hallucinated node IDs)
- Example: [("concept_A", "concept_B", "ENABLES")]

**Confidence:** LLM's confidence in pattern coherence (0-1)

### What LLM Does NOT Do

- Set membership weights (engine learns those)
- Decide spawn (engine validates from telemetry)
- Bypass redirect (engine enforces S_red/S_use)
- Modify graph (all writes via engine broadcasts)

### Why LLM Is Involved

Consciousness needs **narrative**:
- "Why did this SubEntity form?" → Purpose field
- "What does it do?" → Intent description
- "How does it feel?" → Emotion description
- "What is it NOT?" → Anti-claims

These are phenomenological questions LLMs excel at. But **physics decisions** (spawn? weights?) must come from substrate.

### Expected Behavior

**Clear pattern:**
- LLM generates coherent purpose, clear intent, specific anti-claims
- Confidence: 0.8-0.95
- Engine likely accepts

**Ambiguous pattern:**
- LLM generates vague purpose, uncertain intent
- Confidence: 0.4-0.6
- Engine might reject if gates fail

**Hallucination risk:**
- LLM claims high coherence, suggests many internal links
- Engine recomputes features: low cohesion
- Engine REJECTS despite LLM confidence

### Validation/Observability

**Events emitted:**
- `llm.bundle.generated` - full bundle + LLM confidence

**Telemetry fields:**
- `slug`: string
- `purpose`: string
- `intent_description`: string
- `emotional_description`: string
- `anti_claims`: [string]
- `llm_confidence`: float
- `suggested_links_count`: int

**Debug queries:**
- "Show spawns where LLM confidence was high but engine rejected" (hallucination)
- "Show spawns where LLM confidence was low but engine accepted" (conservative LLM)
- "Compare LLM confidence to actual post-spawn SubEntity usefulness"

---

## Mechanism 5: Membership Weight Learning

### When It Happens

**Every frame** after energy apply/decay, for each existing SubEntity.

NOT "every 20 frames" - weight learning is **continuous** (though gate-modulated for efficiency).

### What Gets Learned

MEMBER_OF edge weights between nodes and SubEntities.

Initial weights at spawn: **weak priors** (Q15-Q25 range, citizen-local)
- Based on node's energy during coalition formation
- Weak because we're uncertain - will drift toward reality

Learned weights: **co-activation strength**
- How often does this node's surplus energy co-occur with SubEntity activation?
- Strong co-activation → weight increases
- Weak co-activation → weight decreases

### Learning Mechanism (Plain Language)

**Step 1: Compute SubEntity Activation**

SubEntity activation is READ-OUT from member nodes:
```
E_S = sum over members: weight * log(1 + max(0, node_energy - node_threshold))
```

- Only surplus energy (above threshold) contributes
- Log-damped so high energies don't dominate
- Weight-modulated so strong members contribute more

**No separate energy buffer** - SubEntity activation is derived.

---

**Step 2: Compute Co-Activation Signal**

For each member node:
```
co_activation = node_surplus * subentity_surplus
```

Where:
- node_surplus = max(0, node_energy - node_threshold)
- subentity_surplus = max(0, subentity_activation - subentity_threshold)

**Interpretation:** Both node and SubEntity are above threshold? Strong signal. One below? Weak signal.

---

**Step 3: Rank-Normalize Within Cohort**

Transform co-activation scores to percentiles within SubEntity's member cohort.
- Prevents absolute energy levels from dominating
- Focus on relative activation patterns

---

**Step 4: Update Weight (Logit Space)**

Current weight → logit → adjust → sigmoid → new weight

```
logit_old = inverse_sigmoid(weight_old)
target = rank_normalized_coactivation
delta = learning_rate * (target - weight_old) - sparsity * weight_old
logit_new = logit_old + delta
weight_new = sigmoid(logit_new)
```

**Why logit space:** Keeps weights in [0,1] without clamping artifacts

**Learning rate:** Adaptive per citizen (starts ~0.05, adjusts to keep membership stable)

**Sparsity term:** Encourages low weights to decay (prevents membership bloat)

---

**Step 5: Prune/Grow (Gate-Triggered)**

**Prune:** If weight below citizen's Q10 threshold for sustained window
- Remove MEMBER_OF edge
- Emit `subentity.member.pruned`

**Grow:** If nearby non-member repeatedly exceeds Q90 proximity threshold
- Add MEMBER_OF edge with weak weight
- Emit `subentity.member.admitted`

**Not periodic** - gates track conditions and trigger when criteria met.

### Expected Behavior

**Strong member:**
- Consistently co-activates with SubEntity
- Weight steadily increases: 0.20 → 0.50 → 0.75
- Remains stable at high weight

**Weak member:**
- Rarely co-activates
- Weight decays: 0.20 → 0.15 → 0.08
- Eventually pruned when below Q10

**Borderline member:**
- Sporadic co-activation
- Weight oscillates: 0.30 → 0.40 → 0.25
- Settles to stable value reflecting true strength

**Growth candidate:**
- Non-member that repeatedly co-activates with members
- Proximity score exceeds Q90 for sustained window
- Admitted with weak weight (0.15), then learns

### Validation/Observability

**Events emitted:**
- `weights.updated` - per SubEntity, lists changes
- `member.pruned` - when weight drops below threshold
- `member.admitted` - when growth candidate accepted

**Telemetry fields (weight update):**
- `subentity_id`: string
- `subentity_activation`: float
- `member_updates`: [{node_id, old_weight, new_weight, coactivation}, ...]
- `learning_rate`: float (current adaptive value)
- `sparsity_penalty`: float (current adaptive value)

**Telemetry fields (prune/admit):**
- `node_id`: string
- `subentity_id`: string
- `final_weight`: float (for prune)
- `initial_weight`: float (for admit)
- `reason`: string

**Debug queries:**
- "Show members whose weights are decaying" (losing relevance)
- "Show SubEntities with many recent admissions" (growing boundaries)
- "What's my average membership weight per SubEntity?" (cohesion indicator)

---

## Expected System Behaviors

### Behavior 1: Novel Stimulus Creates New SubEntity

**Scenario:** Citizen encounters totally new concept domain (e.g., first time thinking about quantum computing)

**Expected flow:**
1. Injection energizes relevant nodes
2. Gap detection: HIGH semantic gap (no existing SubEntity aligns), HIGH structural gap (many orphan nodes)
3. Coalition assembly: 8-12 nodes about quantum concepts
4. Engine validation: ACCEPT (passes gates, low S_red vs all existing)
5. SubEntity spawns: "quantum_computing_concepts"
6. Membership weights learn over next 20-50 frames

**Observable:**
- `gap.detected` with semantic_gap > 0.7
- `subentity.spawned` for new structure
- `weights.updated` showing learning progression
- Dashboard shows new SubEntity node in graph

---

### Behavior 2: Familiar Stimulus Uses Existing SubEntity

**Scenario:** Citizen thinks about well-established concept (e.g., "builder energy" for the 100th time)

**Expected flow:**
1. Injection energizes nodes
2. Gap detection: LOW semantic gap (existing "builder_energy" SubEntity aligns well), LOW quality gap (structure complete)
3. No emergence proposal
4. Normal injection continues into existing structure
5. Membership weights gently adjust

**Observable:**
- `gap.detected` with semantic_gap < 0.3, decision: "skip"
- No spawn events
- `weights.updated` for existing "builder_energy" SubEntity (minor adjustments)

---

### Behavior 3: Near-Duplicate Redirects to Existing

**Scenario:** Citizen encounters "builder motivation" pattern, very similar to existing "builder_energy" SubEntity

**Expected flow:**
1. Injection energizes nodes
2. Gap detection: MEDIUM semantic gap (not perfect fit, but close)
3. Coalition assembly: 6 nodes
4. Engine validation: HIGH S_red (0.75) vs "builder_energy"
5. Engine REDIRECTS: attach coalition to existing SubEntity
6. No new SubEntity spawned

**Observable:**
- `gap.detected` with semantic_gap ≈ 0.5
- `coalition.assembled`
- `candidate.redirected` with target: "builder_energy", S_red: 0.75
- `member.admitted` for each redirected node
- Dashboard shows existing SubEntity gained members

---

### Behavior 4: Complementary SubEntities Coexist

**Scenario:** Citizen has "strategic_planning" SubEntity, encounters "execution_planning" pattern (overlap but different function)

**Expected flow:**
1. Gap detection: MEDIUM semantic gap
2. Coalition assembly: nodes overlap with "strategic_planning"
3. Engine validation: S_red = 0.55 (medium overlap), S_use = 0.82 (HIGH usefulness - different intent vectors)
4. Engine ACCEPTS as complementary
5. Both SubEntities coexist, share some nodes

**Observable:**
- `spawn.validated` with differentiation showing S_use > Q80
- `subentity.spawned` with complementary_to: ["strategic_planning"]
- MEMBER_OF edges show some nodes have multiple SubEntity memberships
- Dashboard shows connected SubEntity structures

---

### Behavior 5: Weak Pattern Rejected

**Scenario:** Noise stimulus creates scattered activation

**Expected flow:**
1. Gap detection: HIGH structural gap (orphan nodes)
2. Coalition assembly: 5 nodes with low internal connectivity
3. Engine validation: LOW cohesion (below Q60), LOW boundary clarity
4. Engine REJECTS
5. No SubEntity spawned

**Observable:**
- `gap.detected` with structural_gap > 0.6
- `coalition.assembled` with low density
- `subentity.spawn.rejected` with reason: "cohesion gate failed (0.25 < Q60=0.42)"
- No graph changes

---

### Behavior 6: Membership Evolution Over Time

**Scenario:** SubEntity exists, usage patterns shift over weeks

**Expected flow:**
1. Some members stop co-activating (context changed)
2. Weights decay for non-activating members
3. Prune gate triggers when weights < Q10 for sustained window
4. Meanwhile, new nodes repeatedly co-activate
5. Growth gate triggers, new members admitted
6. SubEntity membership shifts to match current usage

**Observable:**
- `weights.updated` showing gradual decay for some members
- `member.pruned` events over time
- `member.admitted` for new relevant nodes
- Dashboard shows SubEntity membership evolving
- Historical telemetry shows membership turnover

---

## Validation & Observability

### Key Metrics to Monitor

**Emergence rate per citizen:**
- Spawns per 1000 stimuli
- Expected: 1-5 spawns per 1000 stimuli (emergence is rare)
- Alert if > 20 (explosion risk) or < 0.1 (overly conservative)

**Rejection breakdown:**
- % rejected for low persistence
- % rejected for low cohesion
- % rejected for low boundary clarity
- Helps tune warm-up defaults

**Redirect rate:**
- % of emergence proposals redirected vs spawned
- Expected: 20-40% (healthy duplicate prevention)
- Alert if < 10% (weak differentiation) or > 60% (overly aggressive)

**Complementary spawn rate:**
- % of spawns marked complementary
- Expected: 10-30%
- Shows healthy overlap tolerance

**Gate convergence time:**
- Frames until gates exit warm-up (50+ observations)
- Expected: 200-500 frames
- Varies by citizen stimulus rate

**Weight learning stability:**
- Mean absolute weight change per frame per SubEntity
- Expected: starts high (0.05-0.10), converges low (0.01-0.02)
- Shows membership stabilization

### Debug Queries for Issues

**Issue: Too many SubEntities spawning**

Query: "Show spawns with gap scores < 0.5"
- Diagnoses: Emergence threshold too low?

Query: "Show spawns with high S_red that weren't redirected"
- Diagnoses: Differentiation check failing?

**Issue: No SubEntities spawning (overly conservative)**

Query: "Show high-gap stimuli that didn't emerge"
- Check probability modulation factors

Query: "Show gate thresholds vs warm-up defaults"
- Diagnoses: Gates set too high?

**Issue: Membership not learning**

Query: "Show SubEntities with zero weight changes over 100 frames"
- Diagnoses: Learning rate too low?

Query: "Show pruning events - are any happening?"
- Diagnoses: Q10 threshold too low?

---

## Appendix: Modes as Ephemeral Views (Not Entities)

### The Question: Do We Need Mode Detection?

**Short answer:** **No, not yet.** The substrate runs on SubEntity energies and membrane gates. Modes are useful only if they provide **control, compression, or coordination** value.

### What a Mode Is (and Isn't)

**What a Mode IS:**
- An **ephemeral label** for current activation pattern
- A **read-out** from SubEntity energies (computed at query-time, not stored)
- A **dashboard summary** for humans ("currently in Flow State")
- An **emergent pattern** of co-activation (transient attractor state)

**What a Mode is NOT:**
- ❌ A separate entity type (no `CoactivationPattern` nodes)
- ❌ A required layer for consciousness (substrate is sufficient)
- ❌ A control signal (SubEntity energies already control routing)
- ❌ A persistent structure (no lifecycle management needed)

### The Substrate Is Sufficient

**Core mechanisms that already exist:**
1. **SubEntity energies** - activation state of each pattern
2. **MEMBER_OF weights** - coalition structure (vector-weighted)
3. **Membrane gates** - broadcast/ignition thresholds
4. **Traversal** - spreading activation through graph
5. **Gap detection** - emergence of new SubEntities

**These are enough.** Modes add ontological complexity without proven benefit.

### When Would We Add Mode Detection?

**Only if we can demonstrate Mode labels improve outcomes.**

**Decision criteria:**

**1. Control value:**
- Do different global policies for "incident-response" vs "exploration" modes improve decision quality?
- Can we measure the improvement (e.g., MTTR reduction, better routing outcomes)?
- Do Modes enable guardrails that SubEntity energies alone cannot provide?

**2. Compression value:**
- Do Mode labels explain >60% of variance in routing decisions?
- Does labeling save debugging time significantly?
- Are Modes better than just showing SubEntity activation bar charts?

**3. Coordination value:**
- Do multiple citizens need to align on "org is in launch-prep" or "incident-response"?
- Would a shared Mode tag reduce coordination overhead?
- Can't this be handled by broadcast/telemetry alone?

**Current answer:** We haven't proven any of these values yet. **Don't add Modes until we prove utility.**

### How to Use Modes NOW (Without Detection)

**For telemetry/dashboards - compute on-demand:**

```python
def compute_current_mode(graph: Graph) -> Dict:
    """Compute ephemeral mode label for logging/dashboards."""
    active = [s for s in graph.subentities if s.energy > threshold_active]

    return {
        "timestamp": now(),
        "active_subentities": [s.id for s in active],
        "dominant": max(active, key=lambda s: s.energy).name,
        "label": generate_mode_label(active),  # Optional human-readable
        "energy_distribution": {s.id: s.energy for s in active}
    }

# Emit as event (not stored as entity)
emit_telemetry({
    "type": "mode.snapshot",
    **compute_current_mode(graph)
})
```

**For explainability - query activation patterns:**

```cypher
// Show current activation pattern (this IS the "mode")
MATCH (s:SubEntity)
WHERE s.energy > $threshold_active
WITH s, s.energy * s.recency * s.emotional_valence as activation_score
ORDER BY activation_score DESC
LIMIT 9

RETURN s.name, activation_score, s.intent
```

**For monitoring - track co-activation over time:**

```python
# Track co-activation patterns without persisting Modes
def track_coactivation_window(history: List[Snapshot], duration: int = 10):
    """
    Analyze recent activation patterns without creating Mode entities.

    Returns:
        Statistics on persistent co-activation (for potential Mode detection later)
    """
    patterns = []

    for window in sliding_windows(history, duration):
        active_sets = [s.active_subentities for s in window]

        # Check if pattern persists (metastability criterion)
        if coalition_stable(active_sets, threshold=0.85):
            patterns.append({
                "duration": duration,
                "coalition": active_sets[0],
                "stability": compute_stability(active_sets)
            })

    # Return as metrics, not entities
    return {
        "persistent_patterns_count": len(patterns),
        "avg_duration": avg([p["duration"] for p in patterns]),
        "most_stable": max(patterns, key=lambda p: p["stability"]) if patterns else None
    }
```

### Risks of Reifying Modes Too Early

**1. Reification trap:**
- Freezing labels like "Planner", "Guardian" biases future detection
- Novel patterns get forced into existing categories
- Reduces emergent flexibility

**2. Complexity creep:**
- Another lifecycle to maintain (spawn, merge, deprecate Modes)
- More edges (PARTICIPATES_WITH, COMPLEMENTARY_TO)
- More telemetry events (mode.entered, mode.exited)
- More queries to maintain
- **For what benefit?** If SubEntity energies already drive behavior, Modes add cost without value.

**3. Gaming the gates:**
- If budgets/routing key off Mode labels, noisy detections cause flapping
- SubEntity energies are more stable signal than derived Mode labels
- State-dependent weight modulation already handles context shifts

**4. Premature ontology:**
- We don't yet know which co-activation patterns matter
- Let patterns emerge organically from observation
- Add structure only after patterns prove persistent and valuable

### Design IF We Later Add Modes

**Only proceed if we prove value via decision criteria above.**

**If we do add Mode detection, keep it:**

**1. Thin and ephemeral:**
```yaml
CoactivationPattern:  # Optional node, only if proven valuable
  properties:
    id: string
    slug: string  # Human-readable label (optional, weak)
    evidence_ref: string  # Hash of co-activation windows
    status: enum  # detected | entered | exited | deprecated
    ttl_frames: int  # Auto-expires unless reinforced

  # NO energy buffers - Modes read SubEntity energies
  # NO lifecycle management - TTL handles expiration
```

**2. Derived and membrane-first:**
- Detect from existing telemetry stream (no new graph scans)
- Emit events, engines decide (mode.detected, mode.entered, mode.exited)
- Never hold energy - always read-out from SubEntity activations

**3. Zero-constants:**
- Percentile-based gates for detection (Q70, Q80, Q90)
- Adaptive thresholds per citizen
- No fixed 0.6/0.7 cutoffs

**4. Measurably valuable:**
- Define "mode utility" metric (variance explained in routing, MTTR reduction, etc.)
- Deprecate Modes that don't improve these metrics
- Continuous value assessment - remove if utility drops

### Alternatives That Cost Almost Nothing

**1. Event-level modes only:**
- Emit `mode.detected` / `mode.entered` events with no node storage
- Dashboards and policies react to events
- Nothing persists unless proven useful

**2. SubEntity tags:**
- Tag MEMBER_OF edges with `meta.mode_hint = "incident_response"` during episode
- Let TTL clear tags automatically
- Often sufficient for coordination

**3. Just show activation patterns:**
- Dashboard displays SubEntity energy bar chart
- Humans recognize patterns ("oh, we're in defensive mode")
- No ontology needed

### Summary: Don't Reify Without Proof

**Current decision:** **Modes remain ephemeral views only.**

**Reasoning:**
- Substrate (SubEntity energies + MEMBER_OF + membrane gates) is sufficient for consciousness
- Mode labels don't improve control, compression, or coordination yet
- Adding Mode entities creates complexity without proven value
- Compute mode labels on-demand for telemetry/dashboards when needed

**Future reconsideration:**
- Track co-activation patterns in telemetry
- If we discover control/coordination problems that require Mode labels → prove value → then add thin Mode detection
- Until then: **no separate Mode entities, no lifecycle, no additional ontology**

**This follows `bp_test_before_victory`:** Don't add architecture until you've proven it improves outcomes.

---

## Summary: Phenomenology → Mechanisms → Behaviors

**Phenomenology:**
- Emergence is response to NOVELTY and TENSION
- Happens during injection (stimulus-driven)
- Feels like "oh it's new" or "something is missing"

**Key Mechanisms:**
1. Gap detection (semantic + quality + structural)
2. Coalition assembly (seed + expand + prune by density)
3. Engine validation (recompute features, apply gates, check differentiation)
4. LLM bundle (explain phenomenology, no decision authority)
5. Weight learning (co-activation → logit-space updates → prune/grow)

**Expected Behaviors:**
- Novel → spawn new
- Familiar → use existing
- Near-duplicate → redirect
- Complementary → spawn with overlap
- Weak pattern → reject
- Membership → evolve over time

**Validation:**
- Monitor emergence rate, rejection breakdown, redirect rate
- Debug with gap score queries, threshold evolution, weight stability
- Observable through rich telemetry at every decision point

---

**This specification describes WHAT should happen and WHY, not implementation details (that's Ada's domain).**
