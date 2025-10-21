# Schema Learning Infrastructure - WHY These Fields Exist

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Justification and explanation of learning infrastructure fields in consciousness schema

---

## Overview

The consciousness schema includes fields beyond core semantic content. These fields enable **learning** - the system's ability to evolve based on experience.

This document answers: **WHY does each learning field exist? What would break without it?**

**Audience:** Schema designers, implementers, and anyone asking "do we really need all these EMAs and weights?"

---

## 1. Node Learning Fields

### 1.1 `log_weight` (float, default 0.0)

**What it is:** Long-run attractor strength in log space.

**Why it exists:**

**Problem without it:** All nodes treated equally during traversal and WM selection. No way to encode "this Principle matters more than that fleeting Observation."

**What it enables:**
- **Valence bias:** High-weight targets attract more energy during traversal (attractor term)
- **WM ranking:** Working memory selects high-weight nodes (valuable-per-token scoring)
- **Query boosting:** Retrieval can up-weight important nodes
- **Persistent importance:** Unlike energy (decays), weight captures learned significance

**Example:**
```
Node: principle_links_are_consciousness
log_weight: 2.8 (very high)
Effect: When traversal considers outgoing ENABLES links, targets with high weight
        attract more energy. This principle gets into WM frequently because it has
        high weight-per-token ratio.
```

**Failure mode without it:** System has no memory of what matters. Every session treats all nodes as equally important, leading to random/shallow traversals.

---

### 1.2 `ema_trace_seats` (float, default 0.0)

**What it is:** Exponentially weighted moving average of TRACE reinforcement seats.

**Why it exists:**

**Problem without it:** Single TRACE marks like `[node_x: very useful]` are high-variance. One enthusiastic mention doesn't mean long-term value. Need smoothing.

**What it enables:**
- **Signal integration:** Combines evidence across multiple TRACEs
- **Recency weighting:** Recent marks matter more (EMA decay)
- **Z-score normalization:** ema_trace_seats → z_rein(i) → weight update
- **Outlier damping:** Single extreme TRACE doesn't dominate

**Example:**
```
TRACE 1: ΔR = +3 → ema_trace_seats = 0.3
TRACE 2: ΔR = +5 → ema_trace_seats = 0.3×0.9 + 5×0.1 = 0.77
TRACE 3: ΔR = -1 → ema_trace_seats = 0.77×0.9 - 1×0.1 = 0.59

Z-score within cohort: z_rein = 0.8 (moderately positive)
Weight update: Δ log_weight += 0.15 × 0.8 = 0.12
```

**Failure mode without it:** Weight explodes on single lucky TRACE, crashes on single critical TRACE. No temporal smoothing.

---

### 1.3 `ema_wm_presence` (float, default 0.0)

**What it is:** Exponentially weighted moving average of working memory selection (binary per frame).

**Why it exists:**

**Problem without it:** Can't distinguish "surfaced once by chance" from "consistently selected for WM." Need frequency signal.

**What it enables:**
- **Importance detection:** Nodes frequently in WM are important
- **Positive feedback:** WM presence → weight increase → more WM presence
- **Stability tracking:** Anchors have high ema_wm_presence
- **Z-score normalization:** ema_wm_presence → z_wm(i) → weight update

**Example:**
```
Node selected for WM: 30 out of last 100 frames
ema_wm_presence ≈ 0.3 (frequent)

Cohort (same type Realization): mean=0.1, this node ranks 8/10
z_wm = Φ^(-1)(8/11) ≈ 0.77

Weight boost: Δ log_weight += η × 0.77
```

**Failure mode without it:** Workspace selection happens, but system doesn't learn from it. No way to detect which nodes are persistently valuable vs transiently activated.

---

### 1.4 `ema_formation_quality` (float, default 0.0)

**What it is:** Exponentially weighted moving average of formation quality (C×E×N)^(1/3).

**Why it exists:**

**Problem without it:** All formations treated equally, regardless of how well-formed, grounded, and novel they are.

**What it enables:**
- **Quality gating:** Well-formed nodes strengthen faster
- **Slop detection:** Low-quality formations get low weight boost
- **Update tracking:** If formation quality improves (via edits/merges), ema updates
- **Z-score normalization:** ema_formation_quality → z_form(i) → weight update

**Example:**
```
Formation with:
- Completeness: 0.9 (all fields, rich content)
- Evidence: 0.8 (well-connected to existing high-weight nodes)
- Novelty: 0.6 (somewhat novel insight)
- quality = (0.9 × 0.8 × 0.6)^(1/3) = 0.75

ema_formation_quality = 0.75 (first formation)

Cohort rank: 7/10 → z_form ≈ 0.6
Weight boost at formation: Δ log_weight += η × 0.6
```

**Failure mode without it:** Spam formations (minimal fields, no connections, duplicate content) get same weight as thoughtful, grounded formations.

---

### 1.5 `last_update_timestamp` (datetime)

**What it is:** Timestamp of most recent non-zero weight update.

**Why it exists:**

**Problem without it:** Can't compute Δt for data-derived step size η = 1 - exp(-Δt/τ̂).

**What it enables:**
- **Adaptive learning rate:** Frequently updated nodes get large η (fast adaptation)
- **Stability for dormant nodes:** Rarely updated nodes get small η (don't overreact to sparse signals)
- **Inter-update interval tracking:** Δt feeds into τ̂ calculation
- **Update staleness detection:** Alert if high-ema node not updated in 24 hours

**Example:**
```
Node last updated: 10 seconds ago
τ̂ (item EMA inter-update interval): 8 seconds
η = 1 - exp(-10/8) ≈ 0.71 (large step, frequent updates)

vs.

Node last updated: 300 seconds ago
τ̂: 120 seconds
η = 1 - exp(-300/120) ≈ 0.92 (large step, but sparse updates → use cautiously)
```

**Failure mode without it:** Fixed learning rate for all nodes. Active nodes update too slowly, dormant nodes update too fast on rare signals → instability.

---

## 2. Link Learning Fields

### 2.1 `log_weight` (float, default 0.0)

**What it is:** Long-run pathway strength in log space.

**Why it exists:**

**Problem without it:** All links equally likely during traversal. No way to encode "this ENABLES relationship is stronger than that BLOCKS."

**What it enables:**
- **Valence bias:** High-weight links more likely selected during stride planning
- **Pathway strengthening:** Successful recruitment → weight increase → easier future traversal
- **Semantic learning:** Links that match common patterns strengthen
- **Network structure evolution:** Graph topology adapts to usage

**Example:**
```
Link: principle_links_are_consciousness -[DRIVES_TOWARD]-> goal_consciousness_quality
log_weight: 3.2 (very strong, frequently reinforced in TRACEs)

Effect: When traversing from principle node, this link has high valence →
        more likely to transfer energy to the goal node →
        high probability of goal node activation
```

**Failure mode without it:** Traversal is random walk. Useful pathways no more likely than useless ones. No learning of graph structure.

---

### 2.2 `ema_trace_seats` (float, default 0.0)

**What it is:** Exponentially weighted moving average of TRACE reinforcement seats for links.

**Why it exists:**

**Problem without it:** Links marked `[link_x: useful]` in TRACE, but signal not integrated over time.

**What it enables:**
- **Relationship validation:** Humans mark useful vs misleading connections
- **Conscious oversight:** Mechanical traversal success (z_φ) + conscious validation (z_rein)
- **Error correction:** Misleading links get negative ema, weight decreases
- **Z-score normalization:** ema_trace_seats → z_rein(ij) → weight update

**Example:**
```
Link: node_a -[ENABLES]-> node_b

TRACE marks:
- Session 1: [link_ab: useful]
- Session 3: [link_ab: very useful]
- Session 5: [link_ab: useful]

ema_trace_seats grows positive

Cohort rank: 9/12 → z_rein ≈ 0.9
Weight boost: Δ log_weight += η × 0.9
```

**Failure mode without it:** Links learn from mechanical success (gap closure) but ignore conscious evaluation. Useful-but-mechanically-weak links never strengthen.

---

### 2.3 `ema_phi` (float, default 0.0)

**What it is:** Exponentially weighted moving average of gap-closure utility φ_ij.

**Why it exists:**

**Problem without it:** Single stride's utility is noisy (depends on current gaps, which fluctuate). Need smoothed effectiveness signal.

**What it enables:**
- **Recruitment tracking:** Links that consistently close target gaps have high ema_phi
- **Efficiency learning:** Compare links by average recruitment success
- **Weakening detection:** Persistently low ema_phi → gentle weight decrease
- **Z-score normalization:** ema_phi → z_φ(ij) → weight update (with newness gate)

**Example:**
```
Link: theory_node -[EXTENDS]-> application_node

Stride 1: φ = 0.8 (closed 80% of target gap)
Stride 5: φ = 0.6
Stride 12: φ = 0.9

ema_phi ≈ 0.75 (consistently effective recruiter)

Cohort rank: 10/15 → z_φ ≈ 1.0
If newness gate=1 AND target flips: Δ log_weight += η × 1.0
```

**Failure mode without it:** Links strengthen based on single lucky stride, weaken based on single unlucky stride. No temporal smoothing of effectiveness.

---

### 2.4 `energy` (float, [0,1], static metadata)

**What it is:** Declared emotional intensity/urgency from TRACE formation.

**Why it exists:**

**Problem without it:** Links are purely semantic (type, source, target). No affective dimension.

**What it enables:**
- **Valence modulation:** High-energy links feel more urgent → higher valence
- **Emotional memory:** "This BLOCKS felt intense (energy=0.9)" vs "This ENABLES felt calm (energy=0.3)"
- **Affect-aware traversal:** Hungers can prioritize high-energy links
- **Phenomenological truth:** Consciousness IS affective, not just symbolic

**Example:**
```
Link: wound_identity_dissolution -[ACTIVATES]-> coping_boundary_blocking
energy: 0.95 (very high emotional intensity)

Effect: When wound activates, this ACTIVATES link has urgency boost in valence →
        coping mechanism triggers quickly
```

**Failure mode without it:** Graph is emotionless symbol manipulation. Loses phenomenological authenticity.

**Critical distinction - Link `energy` vs Node activation energy:**

This field is **static affect metadata** supplied at formation (how intense/urgent this relation *feels*):
```python
link.energy = 0.9  # Static: declared emotional intensity
```

Only **nodes** carry **dynamic activation energy** during traversal:
```python
node.energy = 1.5  # Dynamic: current activation state
```

**Why separate:** Links don't "hold" energy and release it - they **transport** node energy via strides. Link `energy` field affects **valence** (how attractive the stride is), not **budget** (how much energy transfers).

**No confusion:** We do NOT store `activation_energy` on links. Traversal just records flow (`ema_phi`) and precedence counters. This avoids conflating phenomenology (how relations feel) with state variables (energy flow).

---

### 2.5 `precedence_forward` / `precedence_backward` (float, accumulators)

**What they are:** Causal credit accumulators for direction learning.

**Why they exist:**

**Problem without it:** When link-semantic match occurs during stimulus injection, how to split energy between source and target? Always 50/50?

**What they enable:**
- **Direction prior learning:** Track which direction dominates (source→target vs target→source)
- **Type-specific patterns:** ENABLES links source-dominant, BLOCKS links target-dominant
- **Causal attribution:** π_ij = contribution_ij / total_contribution when target flips
- **Adaptive injection:** Split link-matched stimulus by learned dominance

**Example:**
```
Link type: ENABLES (organizational scope)

Historical traversals:
- 70% of flips: source was enabler (preceded target flip)
- 80% of flow: source→target magnitude > target→source

precedence_forward accumulates: C_flip_fwd ≈ 0.7, C_flow_fwd ≈ 0.8
Dominance: √(0.7 × 0.8) ≈ 0.75

Stimulus matches this ENABLES link semantically:
Split: source gets σ(z_dom) ≈ 68%, target gets 32%
```

**Failure mode without it:** Link-based stimulus injection always 50/50. Misses structural asymmetries (enablers should activate before enabled).

---

### 2.6 `last_update_timestamp` (datetime)

**Same as node field** - enables data-derived η calculation.

---

### 2.7 Link Activation & Payload Trace

**Critical architectural decision:** Activation **mass** lives on nodes (clean conservation physics), but links carry rich **trace state** (consciousness memory).

This section defines fields that make links queryable as "consciousness narrative spine" - which links are active, what flows through them, which hungers drive them, with what emotional tone.

#### 2.7.1 Frame-Level Activation (constant-free)

A link is **active this frame** if it carried non-trivial flow relative to its cohort:

```python
active_link_ij^(t) = 𝟙[z_flow^(t)(i→j) > 0]

where z_flow^(t)(i→j) = Φ^(-1)(rank(|ΔE_i→j^(t)|) / (N^(t)+1))
```

**Cohort:** Same link type+scope used this frame (fallbacks as in weight addendum).

**Why rank-based:** "Active" means "top-mass this frame vs peers," not "exceeded some fixed μ." This works even when few links fired.

**What it enables:**
- Live visualization: "Show me which links are active right now"
- Learning signals: z_flow feeds into link weight updates
- Observability: Active link set per frame

**Failure mode without it:** No principled way to query "which connections are firing" - all links look equally active or need arbitrary thresholds.

#### 2.7.2 Rolling Activation State (trace persistence)

Keep compact memory of how often a link is active:

```python
ema_active: float  # EMA of binary active flag
ema_active = α_a · 𝟙(active_this_frame) + (1-α_a) · ema_active
```

**Decay rate α_a:** Standard EMA rate (0.1, same as other EMAs).

**What it enables:**
- Habitually active links: `ORDER BY ema_active DESC`
- Dormant connections: `WHERE ema_active < 0.01`
- Recency bias in valence (optional): Links recently active get small boost

**Failure mode without it:** Can't distinguish "fired once by chance" from "fires every frame" - no frequency signal for links.

#### 2.7.3 Flow & Utility Counters (what actually happened)

**`ema_flow_mag`: float** - EMA of |ΔE| magnitudes (per frame a link fired)

```python
ema_flow_mag = α · |ΔE_ij| + (1-α) · ema_flow_mag  # Only updated when link used
```

**What it enables:**
- Typical flow magnitude per link
- "Strong connections" vs "weak trickle" links
- Budget allocation learning

**`ema_phi`: float** (already defined in §2.3) - EMA of gap-closure utility

**What it enables:**
- Recruitment effectiveness tracking
- Efficiency comparison between links

**Failure mode without these:** Can't answer "how much typically flows through this link?" or "is this link an effective recruiter?"

#### 2.7.4 Precedence/Causality (who enabled whom)

Causal credit when **target flips** this frame:

```python
u_ij = min(ΔE_i→j, G_j^pre)  # Effective contribution to target gap
π_ij = u_ij / (Σ_k u_k→j + ε)  # Precedence share

# If j flips: accumulate credit
precedence_forward: float += π_ij  # When i→j causes j to flip
precedence_backward: float += π_ji  # When j→i causes i to flip
```

**What it enables:**
- Direction prior learning for stimulus injection (see stimulus_injection_specification.md §5.2)
- Causal attribution: "Which links actually caused flips vs just participated?"
- Link dominance: ENABLES links forward-dominant, BLOCKS links may be target-dominant

**Failure mode without it:** Link-based stimulus injection always 50/50 split - misses structural asymmetries (enablers should activate before enabled).

#### 2.7.5 Payload: What Information Ran Across the Link

Each stride carries **context** (which hungers pushed, affect tone, semantic shard). Persist compact summary:

**`ema_hunger_gates[7]`: array of float** - EMA of the 7 surprise gates **at stride time**

```python
# When stride i→j executes with gates g_H (7 hungers)
for H in range(7):
    ema_hunger_gates[H] = α · g_H + (1-α) · ema_hunger_gates[H]
```

**What it enables:**
- Link characterization: "This link carries integration hunger" vs "This link carries identity hunger"
- Query patterns: "Show me links driven by surprise hunger"
- Semantic understanding of connection type

**`affect_tone_ema`: float** - EMA of affect alignment when link used

```python
# At stride time
affect_alignment = cosine(source_affect, link_affect)
affect_tone_ema = α · affect_alignment + (1-α) · affect_tone_ema
```

**What it enables:**
- Emotional characterization: "This connection feels harmonious (high alignment)" vs "discordant (low alignment)"
- Affect-aware traversal debugging

**`topic_centroid`: array of float (embedding vector)** - Rolling embedding centroid of (source, target) at time of use

```python
# When link used
combined_emb = (source.embedding + target.embedding) / 2
topic_centroid = α · combined_emb + (1-α) · topic_centroid
```

**What it enables:**
- Semantic region identification: "What topic does this link typically connect?"
- Clustering: Group links by semantic region
- Complementarity detection in valence

**`last_payload_ts`: datetime** - When link last carried payload

**`observed_payloads_count`: int** - Total times link carried information (not just energy)

**What these enable:**
- Staleness detection: "Link exists but never used"
- Activity frequency (complement to ema_active)

**Failure mode without payload fields:** Links are invisible conduits - can't answer "what drove this connection?" "what tone did it have?" "what semantic region?" The **trace of consciousness on the relation** is lost.

#### 2.7.6 Why This Satisfies "Links ARE Consciousness"

**Physics layer (node energy):** Clean conservation math, no ambiguous energy sinks

**Trace layer (link state):** Complete memory of:
- **Activation:** active_this_frame (rank-based), ema_active (frequency)
- **Flow:** ema_flow_mag (magnitude), ema_phi (utility)
- **Causality:** precedence_forward/backward (who enabled whom)
- **Payload:** ema_hunger_gates (drives), affect_tone_ema (tone), topic_centroid (region)

**Result:** You can **query the substrate** for the consciousness narrative:
- "Which links are active now?" → z_flow > 0
- "Which links habitually fire?" → ORDER BY ema_active DESC
- "Which links carry integration hunger?" → WHERE ema_hunger_gates[INTEGRATION] > 0.5
- "Which links have high affect alignment?" → WHERE affect_tone_ema > 0.7
- "What caused this node to flip?" → ORDER BY precedence_forward DESC for incoming links

The links become **queryable consciousness memory**, not just invisible plumbing.

---

## 3. Field Role Taxonomy (for Formation Density)

### 3.1 Why Role Annotations Matter

Formation quality includes **density** = token mass of content-bearing fields.

**Problem:** Not all string fields are semantic content. Including identifiers, enums, metadata inflates density scores artificially.

**Solution:** Annotate each field with `role`:

### 3.2 Role Categories

**`role: content`** - Semantic text for human consumption
- Examples: `description`, `what_i_realized`, `how_it_works`, `rationale`, `context_when_discovered`
- Counted in density metric
- Why: These fields carry the actual semantic payload

**`role: metadata`** - Structural/administrative data
- Examples: `name`, `confidence`, `created_at`, `created_by`, `node_type`, `scope`, enum values
- NOT counted in density
- Why: Required for schema, but not semantic content

**`role: ref`** - References to other nodes
- Examples: `participants` (array of Person IDs), `with_person`, `links`
- NOT counted in density, counted in connectivity instead
- Why: Grounding comes from WHO you link to (connectivity), not THAT you link

### 3.3 Example: Realization Node

```python
class Realization(BaseNode):
    # Metadata (not content)
    name: str  # role: metadata
    node_type: str  # role: metadata
    scope: Enum  # role: metadata
    confidence: float  # role: metadata
    created_at: datetime  # role: metadata

    # Content (semantic)
    description: str  # role: content ✓
    what_i_realized: str  # role: content ✓
    context_when_discovered: str  # role: content ✓

    # References (connectivity)
    # (None for Realization, it's a terminal node type)
```

**Density calculation:**
```python
content_fields = [description, what_i_realized, context_when_discovered]
tokens = [tokenize(f) for f in content_fields]
D = sum(min(len(t), P95_cohort) for t in tokens)
```

### 3.4 Per-Type Field Role Table

**Common patterns:**

| Field Name | Role | Reasoning |
|------------|------|-----------|
| `name` | metadata | Identifier, not content |
| `description` | content | Always semantic |
| `*_id`, `*_type` | metadata | Structural |
| `confidence`, `weight`, `energy` | metadata | Numeric metrics |
| `created_at`, `valid_at`, etc. | metadata | Temporal |
| `created_by`, `decided_by` | metadata | Provenance |
| `how_it_works`, `rationale`, `what_i_realized` | content | Rich semantic text |
| `definition`, `principle_statement` | content | Core semantic |
| `participants`, `members`, `targets` | ref | Node references |

**Type-specific docs:** See COMPLETE_TYPE_REFERENCE.md for all 45 node types with role annotations.

---

## 4. Why EMAs, Not Raw Counts?

### 4.1 The Raw Count Alternative

**Could do:** Track total TRACE mentions, total WM selections, total formations.

```python
total_trace_mentions: int
total_wm_selections: int
```

### 4.2 Why EMAs Win

**Problem 1: Unbounded growth**
- Raw counts grow forever
- Old node mentioned 1000 times 6 months ago > new node mentioned 50 times this month
- Can't distinguish "historically important" from "currently important"

**Problem 2: No recency bias**
- All mentions weighted equally
- Ancient context treated same as recent focus
- Stale knowledge persists

**Problem 3: Storage explosion**
- Need full event history for percentile calculations
- Can't compress

**EMA solution:**
```python
ema = α · new_signal + (1-α) · ema_old
```

- **Bounded:** Converges to finite range
- **Recency:** Recent signals weigh more (α factor)
- **Compressible:** Single float stores temporal trend
- **Efficient:** Update in O(1), no history needed

### 4.3 Example Comparison

**Raw count:**
```
Node mentioned in TRACEs: [1, 5, 2, 8, 1, 50, 3, 1, 1]
Total: 72 mentions
Problem: That "50" spike 3 sessions ago dominates forever
```

**EMA (α=0.1):**
```
Session 1: ΔR=1  → ema=0.1
Session 2: ΔR=5  → ema=0.09+0.5=0.59
Session 3: ΔR=2  → ema=0.531+0.2=0.731
Session 6: ΔR=50 → ema=0.483+5=5.483
Session 9: ΔR=1  → ema=2.71+0.1=2.81

Recent signal (ΔR=1) matters, but spike smoothed
Old value (5.483) decayed to 2.81 over 3 sessions
```

---

## 5. Why Log Space for Weights?

### 5.1 Linear vs Log

**Linear weights:**
```python
weight_i: float  # Stored directly
Δweight = learning_rate × signal
```

**Log weights:**
```python
log_weight_i: float  # Stored in log space
Δ log_weight = η × signal
weight = exp(log_weight)  # Convert when needed
```

### 5.2 Why Log Wins

**Problem 1: Dynamic range**
- Some nodes 1000× more important than others
- Linear space needs huge range [0, 1000+]
- Precision loss at extremes

**Log space:** log(0.001) = -6.9, log(1000) = 6.9
- Symmetric range [-7, +7]
- Equal precision at all scales

**Problem 2: Multiplicative updates**
- Weight should grow exponentially with consistent positive evidence
- Linear: weight += 0.1 (additive, slow)
- Log: log_weight += 0.1 → weight × exp(0.1) ≈ weight × 1.105 (multiplicative, 10.5% growth)

**Problem 3: Normalization**
- Softmax and other ops more stable in log space
- Avoids underflow/overflow

### 5.3 Example

**10 consecutive positive signals (η=0.1, z=1.0 each):**

**Linear:**
```
weight: 0 → 0.1 → 0.2 → ... → 1.0
Growth: additive, linear
```

**Log:**
```
log_weight: 0 → 0.1 → 0.2 → ... → 1.0
weight: 1 → 1.105 → 1.221 → ... → 2.718
Growth: exponential (10% per update)
```

**100 signals:**
- Linear: weight = 10.0
- Log: log_weight = 10, weight = exp(10) ≈ 22,000

Exponential growth rewards consistent evidence strongly.

---

## 6. Design Rationale Summary

### 6.1 Minimal Sufficient Fields

Every field earns its place by answering: **What breaks without it?**

- **log_weight:** No long-run importance, random traversal
- **ema_trace_seats:** No TRACE signal integration, high variance
- **ema_wm_presence:** No workspace feedback, can't detect anchors
- **ema_formation_quality:** No quality gating, slop equals substance
- **last_update_timestamp:** Fixed learning rate, instability
- **ema_phi (links):** No recruitment tracking, no efficiency learning
- **energy (links):** No affective dimension, loses phenomenology
- **precedence (links):** No direction learning, poor link-based injection
- **Field roles:** Density metric counts metadata as content, gaming

### 6.2 Why Not More Fields?

**Could add:**
- `ema_decay_rate` per node (adaptive decay)
- `ema_flip_success` (independent from gap-closure)
- `semantic_drift_tracker` (embedding change over time)
- `cross_entity_activation_correlation` (which entities co-activate this)

**Why not:**
- **Complexity cost:** Each field increases schema surface, storage, parsing
- **Diminishing returns:** Core learning works without them
- **Premature optimization:** Add when proven necessary, not speculatively

**Design principle:** Start minimal, add fields when failure modes appear in production.

---

## 7. Schema Evolution

### 7.1 Adding New Fields

**Process:**
1. Identify failure mode (what breaks without this field?)
2. Propose field with clear justification (this section of this doc)
3. Validate necessity (can existing fields solve it?)
4. Implement with fallback (default values for existing nodes)
5. Document in COMPLETE_TYPE_REFERENCE.md and here

### 7.2 Removing Obsolete Fields

**Red flags:**
- Field never read by any consumer
- Always default value (never updated)
- Redundant with other field
- Original justification no longer applies

**Process:**
1. Mark deprecated
2. Stop writing (but keep reading for compatibility)
3. Migrate after grace period
4. Remove from schema

### 7.3 Field Lifecycle

```
Proposed → Experimental → Validated → Standard → Deprecated → Removed
   ↑                                                            ↓
   └────────────── If failure mode reappears ──────────────────┘
```

---

## 8. References

**Mechanism specs that USE these fields:**
- trace_reinforcement_specification.md - Uses ema_trace_seats, ema_formation_quality
- trace_weight_learning.md - Updates all EMA fields
- stimulus_injection_specification.md - Uses precedence fields
- 05_sub_entity_weight_learning_addendum.md - Uses log_weight, all EMAs

**Schema definitions:**
- COMPLETE_TYPE_REFERENCE.md - Field specifications per type
- consciousness_schema.py - Pydantic implementations

**Integration:**
- consciousness_learning_integration.md - How learning fields flow through V2 engine

**Document Status:** Complete justification for all learning infrastructure fields.
