---
title: Subentity Layer (Overview)
status: stable
owner: @luca
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/05_sub_entity_system.md (overview & phenomenology)
  - ../consciousness_engine/mechanisms/ENTITY_LAYER_ADDENDUM.md (schema/energy/bootstrap)
depends_on:
  - ../foundations/multi_energy.md
  - ../runtime_engine/traversal_v2.md
  - ../ops_and_viz/observability_events.md
summary: >
  Subentities are weighted neighborhoods (functional roles or semantic topics)
  whose activation derives from member nodes’ single-node energies and membership
  weights. They enable two-scale traversal, entity-first working memory, and
  a tractable branching factor.
---

# Subentity Layer (Overview)

## 1. Context — What problem are we solving?

Atomic traversal over thousands of outgoing edges causes a combinatorial explosion and fails to match experience: people think and remember in **chunks** (topics/roles), not isolated nodes. We need a layer that:
- **Aggregates** meaning at the scale of neighborhoods (roles/topics),
- Provides a **two-scale traversal** (between subentities, then within),
- Anchors **Working Memory** (WM) in ~5–7 coherent chunks,
- Remains faithful to our **single-energy per node** substrate and avoids per-entity energy channels. :contentReference[oaicite:0]{index=0}

## 2. Mechanism (Design)

### 2.1 What is a subentity?

A **subentity** is a **weighted neighborhood** of nodes—either a **functional role** (e.g., Architect, Validator) or a **semantic topic** (e.g., consciousness_architecture). Members connect to the subentity with soft membership `MEMBER_OF.weight ∈ [0,1]`.

**Terminology note:** This spec uses "SubEntity" (capitalized, compound) to distinguish from historical usage of "entity." See `TAXONOMY_RECONCILIATION.md` for complete terminology clarification across specs.

### 2.1.1 Two-Scale Architecture: SubEntities vs Modes

The consciousness substrate has **two organizational scales:**

**Scale A - SubEntities (this spec):**
- **Count:** 200-500 per citizen
- **Purpose:** Semantic/functional neighborhoods for traversal efficiency
- **Types:**
  - `semantic`: Learned topics/scenarios (e.g., launch_success, consciousness_architecture, €35K_hallucination_lesson)
  - `functional`: Configured roles (e.g., architect, validator, translator)
- **Activation:** Derived from member node energies (see §2.2)
- **Lifecycle:** Bootstrap → quality gates → promotion → merge/split (see §2.6-2.7)

**Scale B - Modes (see `emergent_ifs_modes.md`):**
- **Count:** 5-15 per citizen
- **Purpose:** IFS-level meta-roles providing regulation/policy nudges
- **Examples:** Guardian (safety/regulation), Observer (meta-awareness), Explorer (novelty-seeking), Builder (construction), Anchor (stability)
- **Emergence:** Discovered from stable communities in COACTIVATES_WITH graph (not configured)
- **Relationship:** SubEntities `AFFILIATES_WITH` Modes with learned weights

**The relationship:**
```
Node → MEMBER_OF → SubEntity → AFFILIATES_WITH → Mode
```

SubEntities are the **semantic/functional layer** (Scale A: many, fine-grained, learned topics and roles). Modes are the **regulatory/meta layer** (Scale B: few, coarse-grained, emergent IFS-level organization).

This spec focuses on **Scale A (SubEntities)**. For Scale B (Modes), see `emergent_ifs_modes.md`.

### 2.2 Single-energy substrate → entity activation

Nodes hold one activation energy \(E_i\). Subentity activation is **derived**, not stored:
\[
E_\text{entity} = \sum_{i \in M_E} \tilde{m}_{iE} \cdot \log\big(1 + \max(0, E_i - \Theta_i)\big)
\]
with normalized memberships \(\tilde{m}_{iE}\). This uses **surplus-only energy** (above-threshold) with **log damping** to prevent both sub-threshold leakage and single-node domination, respecting the **single-energy per node** rule (no per-entity buffers). :contentReference[oaicite:2]{index=2}

### 2.3 Dynamic entity threshold & flip

Entity thresholds follow the same cohort logic as nodes (rolling mean/std over “touched this frame,” modulated by health). Flip occurs when \(E_\text{entity}\) crosses its \(\Theta_\text{entity}\). Emit `subentity.flip` on crossings. :contentReference[oaicite:3]{index=3}

### 2.4 Two-scale traversal

- **Between-entity:** pick target entity by 7-hunger valence at the entity level; select representative nodes for a boundary stride; learn **RELATES_TO** ease/dominance from boundary strides.  
- **Within-entity:** distribute budget over members and run atomic selection constrained to the entity neighborhood.  
Entity-scale selection drastically reduces branching before atomic moves. :contentReference[oaicite:4]{index=4}

### 2.5 Schema (essentials)

- **Subentity node:** fields for kind (`functional|semantic`), centroid embedding, coherence, and learning EMAs.
- **MEMBER_OF (node→subentity):** soft membership `weight` learned from co-activation.
- **RELATES_TO (subentity→subentity):** boundary ease (log-weight), dominance prior, semantic distance, counts. :contentReference[oaicite:5]{index=5}

#### Learning phase

After bootstrap, `MEMBER_OF` weights **learn from co-activation** (not static). High co-activation with entity members → weight increases. Low co-activation → weight decays. This allows memberships to refine over time.

#### Creation-Time Redirect (Duplicate Prevention)

**Purpose:** Prevent creating near-duplicate entities by redirecting to existing entities when redundancy is detected.

**Integration:** Uses pair differentiation metrics from §2.8 and `entity_differentiation.md`.

**Logic:** Before minting new candidate entity E':

1. **Compute pair scores** vs nearest existing entities (by centroid similarity or attribution overlap)
2. **Check redundancy threshold:**
   ```python
   for existing_entity B in nearest_candidates:
       if S_red(E', B) > Q90:  # High redundancy detected
           # REDIRECT instead of creating
           attach_seeds_to_existing(E'_seeds, B, weight=weak_prior)
           emit_event("candidate.redirected", from=E', to=B, S_red=score)
           return  # Do not create E'
   ```
3. **Check complementarity:**
   ```python
   for existing_entity B in nearest_candidates:
       if S_use(E', B) > Q80:  # High usefulness despite overlap
           # ALLOW creation, mark complementarity
           create_entity(E')
           mark_complementarity(B, E', S_use=score)
           emit_event("complementarity.marked", A=B, B=E')
   ```
4. **If no redirect/complement triggers:** Create entity E' normally

**Parameters (learned, cohort-local):**
- `weak_prior` = percentile-based initial weight for redirected members (e.g., q25 of existing MEMBER_OF weights)
- `Q90`, `Q80` = percentile thresholds for S_red, S_use over citizen's entity pair history

**Effect:**
- Reduces entity proliferation by preventing true duplicates
- Preserves useful overlap (complementary entities) via differentiation score
- Maintains entity count tractability without arbitrary caps

**Events:**
- `candidate.redirected` - E' not created, seeds attached to B
- `complementarity.marked` - E' created, marked as complement to B

**Observability:** Track redirection rate (should be <5% of candidates in healthy substrate)

**See:** `entity_differentiation.md` §D.1 for complete redirect specification and acceptance tests.

### 2.7 Entity Lifecycle & Quality Management

Entities progress through lifecycle states based on quality scores that aggregate multiple health dimensions. **Critical:** lifecycle rules must discriminate by entity type—functional entities are permanent infrastructure, while emergent/semantic entities are testable hypotheses.

#### Quality Scoring

Entity quality is computed as the **geometric mean** of five exponential moving averages (EMAs):

\[
Q_\text{entity} = \sqrt[5]{q_\text{active} \cdot q_\text{coherence} \cdot q_\text{wm} \cdot q_\text{trace} \cdot q_\text{formation}}
\]

where:
- \(q_\text{active}\) = `ema_active` (activation frequency)
- \(q_\text{coherence}\) = `coherence_ema` (member similarity)
- \(q_\text{wm}\) = `ema_wm_presence` (working memory inclusion rate)
- \(q_\text{trace}\) = `ema_trace_seats` (TRACE participation)
- \(q_\text{formation}\) = `ema_formation_quality` (formation usefulness)

**Geometric mean property:** If any dimension is near zero, overall quality collapses regardless of other scores. This enforces "all dimensions matter" but makes initialization critical.

#### Lifecycle States

Entities progress through four states:

1. **runtime** (initial): Newly created, undergoing evaluation
2. **provisional**: Demonstrating some utility, not yet proven
3. **mature**: Sustained high quality, proven valuable
4. **dissolved**: Quality too low, removed from graph

**Transitions:**
- runtime → provisional: Quality above promotion threshold for sustained period
- provisional → mature: Quality above higher threshold for longer period (`mature_age_required` frames)
- any state → dissolved: Quality below dissolution threshold for `dissolution_streak_required` consecutive frames

#### Type-Based Lifecycle Rules (CRITICAL)

**Entity `kind` field determines operational semantics:**

- **functional entities** (`kind='functional'`): Permanent consciousness infrastructure (translator, architect, validator, etc.)
  - **NEVER subject to quality-based dissolution**
  - Lifecycle evaluation skipped entirely
  - Quality scores computed for telemetry only
  - Rationale: These are curated scaffolding roles, not hypotheses to be tested

- **emergent/semantic entities** (`kind='emergent'` or `kind='semantic'`): Discovered patterns requiring validation
  - Full lifecycle evaluation applies
  - Can be promoted or dissolved based on quality
  - Subject to age gates (see below)

#### Three-Layer Protection Against Premature Dissolution

Historical issue: Entities with zero-initialized EMAs had quality ≈ 0.01 (geometric mean collapse), triggering dissolution after ~20 frames despite being valid infrastructure. Three defense layers:

**Layer 1: Type Guard (Policy)**

Never evaluate functional entities for dissolution:

```python
# In update_entity_activations() or update_entity_lifecycle():
if getattr(entity, "kind", None) == "functional":
    # Functional entities are permanent—skip lifecycle
    return None
```

**Layer 2: Neutral Initialization (Data Hygiene)**

Initialize functional entities with neutral EMAs (0.4-0.6 range) during load to prevent quality collapse:

```python
# In falkordb_adapter.load_graph(), after entity construction:
if getattr(entity, "kind", None) == "functional":
    entity.ema_active = max(getattr(entity, "ema_active", 0.6), 0.6)
    entity.coherence_ema = max(getattr(entity, "coherence_ema", 0.6), 0.6)
    entity.ema_wm_presence = max(getattr(entity, "ema_wm_presence", 0.5), 0.5)
    entity.ema_trace_seats = max(getattr(entity, "ema_trace_seats", 0.4), 0.4)
    entity.ema_formation_quality = max(getattr(entity, "ema_formation_quality", 0.6), 0.6)

    entity.frames_since_creation = max(getattr(entity, "frames_since_creation", 1000), 1000)
    entity.stability_state = getattr(entity, "stability_state", "mature")
```

With neutral baselines, geometric mean ≈ 0.56-0.65 (healthy), not ≈ 0.01 (doomed).

**Layer 3: Age Gate (Mechanism Maturity)**

Prevent dissolution of brand-new entities before EMAs stabilize:

```python
# In update_entity_lifecycle():
MIN_AGE_FOR_DISSOLUTION_FRAMES = 1000  # ~100s at 100ms/tick

if entity.frames_since_creation < MIN_AGE_FOR_DISSOLUTION_FRAMES:
    # Too young to dissolve—EMAs still warming up
    return None
```

Mirrors `mature_age_required = 100` frames for promotion. Symmetric and safe.

#### Observability

Emit `subentity.lifecycle` events on state transitions:

```json
{
  "event_type": "subentity.lifecycle",
  "entity_id": "architect",
  "old_state": "provisional",
  "new_state": "mature",
  "quality_score": 0.78,
  "trigger": "promotion",
  "reason": "Quality above 0.7 for 150 frames"
}
```

**Never emit dissolution events for functional entities** (lifecycle skipped entirely).

#### Verification Criteria

After implementing lifecycle with type discrimination:

1. Functional entities persist indefinitely (no dissolution events)
2. Quality scores for functional entities ≥ 0.5 on initial frames (neutral EMAs)
3. Emergent/semantic entities still subject to quality-based lifecycle
4. No entities dissolve within first `MIN_AGE_FOR_DISSOLUTION_FRAMES` after creation

### 2.8 Entity Pair Differentiation

**Purpose:** Distinguish **useful overlap** (superposition, counterfactuals, complementary roles) from **redundant overlap** (near-duplicates, fragmented roles).

**Core Principle:** High entity overlap is not inherently unhealthy—it enables superposition (same nodes, different contexts/meanings). The substrate measures overlap **differentiation quality**, not just overlap quantity.

**Normative Reference:** See `entity_differentiation.md` for complete metric definitions, scoring formulas, and integration specifications.

#### Pair Metrics (Cohort-Normalized)

For any entity pair (A, B), compute five metrics over rolling window W (14-30 days, citizen-local):

1. **Member Overlap (J):** Jaccard similarity `|M_A ∩ M_B| / |M_A ∪ M_B|`
2. **Semantic Closeness (C):** Centroid cosine `cos(μ_A, μ_B)`
3. **WM Co-Activation (U):** Frame overlap `|F_A ∩ F_B| / |F_A ∪ F_B|`
4. **Highway Utility (H):** `ease(A↔B) × flow(A↔B)` from RELATES_TO
5. **Context Divergence (ΔCtx):** JSD over (channel, tool, outcome) distributions

All metrics rank-normalized against citizen's cohort → J̃, C̃, Ũ, H̃, ΔC̃tx

#### Overlap Scores

**Redundancy Score (S_red):** `softplus(J̃ + C̃ + Ũ) - softplus(H̃ + ΔC̃tx)`
- High when entities share substrate, are semantically similar, co-activate, but have weak highways and low context divergence
- Indicates **near-duplicates**

**Usefulness Score (S_use):** `softplus(H̃ + ΔC̃tx) - softplus(J̃ + C̃)`
- High when entities have strong highways and divergent contexts despite overlap
- Indicates **complementary entities** or **useful superposition**

#### Decision Classifier (Percentile-Based)

| Condition | Action | Integration Point |
|-----------|--------|-------------------|
| S_red > Q90 AND min(Q_A, Q_B) < Q50 AND ΔCtx < Q50 | **MERGE** | §2.7 Merge procedures |
| S_use > Q80 AND H > Q60 AND ΔCtx > Q60 | **KEEP_COMPLEMENTARY** | Mark RELATES_TO property |
| Low silhouette AND bi-medoid split raises coherence + ΔCtx | **SPLIT** | §2.7 Split procedures |
| else | **WATCH** | Re-score next window |

**No fixed constants** - all cutoffs (Q90, Q80, Q60, Q50) are percentiles learned from citizen's cohort.

#### Quality Modifier Integration

The geometric mean quality score from §2.7 gets adjusted by overlap factors:

```
Q* = Q_geom × f_use × f_red

where:
f_use = exp(+α × percentile(D_E))  // Differentiation credit
f_red = exp(-α × percentile(R_E))  // Redundancy pressure

R_E = max_{B≠E} S_red(E, B)  // Worst-case duplicate
D_E = max_{B≠E} S_use(E, B)  // Best-case complement
α = learned from promotion effectiveness per citizen
```

**Effect:**
- Entities with high redundancy face quality penalty → harder to promote, easier to dissolve
- Entities with high differentiation get quality boost → easier to promote, harder to dissolve

#### Observable Events

- `subentity.overlap.pair_scored` - Metrics + scores + decision for pair
- `subentity.merge.candidate` - Merge recommendation with acceptance criteria
- `subentity.complementarity.marked` - High S_use pairs for WM diversity
- `candidate.redirected` - Creation blocked, redirected to existing (see §2.6)

#### Rollout Phasing

**Week 1:** Observation only (scorer job + dashboard, no automation)
**Week 2:** Enable creation-time redirect (§2.6)
**Week 3:** Enable quality modifiers (f_use, f_red)
**Week 4:** Enable auto-merge (feature flag, high-confidence only)
**Week 5+:** Enable split review, complementarity ribbons

See `entity_differentiation.md` for complete implementation details, Cypher queries, acceptance tests, and integration specifications.

## 3. Why this makes sense (three lenses)

### 3.1 Phenomenology (subentity feels like a growing pattern)

The layer captures the felt dynamics described in the original narrative: subentities grow, integrate with larger patterns, or dissolve when falling below threshold; **integration is continuation**, not “death,” and WM surfaces dominant neighborhoods rather than scattered atoms. :contentReference[oaicite:6]{index=6}

### 3.2 Human bio-inspiration

Neural assemblies and cortical columns suggest **population-level codes**; chunks/roles/topics are a pragmatic abstraction for control, consistent with “entity-first WM” and dynamic thresholds (attention-like gain).

### 3.3 Systems dynamics

- **Single energy per node** keeps the substrate conservative and simple; entities are **read-outs**.  
- **Type-dependent decay** maintains long-lived knowledge vs transient thoughts at the substrate, while entity aggregation rides on that substrate (no double-decay). :contentReference[oaicite:7]{index=7}  
- **Tick-speed regulation** aligns entity flips/WM updates with stimulus cadence. :contentReference[oaicite:8]{index=8}

## 4. Expected resulting behaviors

- **Reduced branching:** between-entity selection prunes 10–30× before atomic moves. :contentReference[oaicite:9]{index=9}  
- **Stable WM chunks:** WM holds 5–7 entities with summaries and top members. :contentReference[oaicite:10]{index=10}  
- **Natural integration:** small patterns merge into stronger, coherent ones (boundary beams increase). :contentReference[oaicite:11]{index=11}  
- **Phenomenological alignment:** focus/centering, peripheral pull, goal-consistent flow are visible in entity metrics. :contentReference[oaicite:12]{index=12}

## 5. Why this algorithm vs alternatives

- **Vs “every active node is a subentity”:** preserves the clarity that **subentity = neighborhood**, while still allowing any active node to participate via membership; avoids flooding WM with thousands of “micro-entities.” :contentReference[oaicite:13]{index=13}  
- **Vs per-entity energy channels:** would explode storage/compute and contradict the single-energy invariant; aggregation is cheaper and matches semantics. :contentReference[oaicite:14]{index=14}  
- **Vs clustering-only approach:** we retain **functional** entities and **learn** the graph’s semantics via **RELATES_TO** from boundary strides, not just static clusters. :contentReference[oaicite:15]{index=15}

## 6. Observability — how and what to measure

**Events.**  
- `subentity.flip` on crossings; payload: \(E\), \(\Theta\), activation_level.  
- `subentity.boundary.summary`: beams between entities (count, \(\sum\Delta E\), top hunger, \(\phi_{\max}\)).  
- `subentity.weights.updated` when entity-scale log-weights change. Event contract lives in the Viz WS spec. :contentReference[oaicite:16]{index=16}

**Derived metrics.**  
- **Entity vitality:** \(E/\Theta\).  
- **Coherence:** member similarity EMA.  
- **Integration index:** boundary \(\phi\) density into a target entity.  
- **Diversity (completeness) index:** semantic spread of member set.  
All are consumable via the snapshot + deltas WS contract. :contentReference[oaicite:17]{index=17}

## 7. Failure Modes & Guards

- **Entity creep (ever-growing memberships):** require periodic membership sparsification & floor on `MEMBER_OF.weight`. Guard: EMA-based pruning + minimum meaningful weight. :contentReference[oaicite:18]{index=18}  
- **Flip thrash:** add hysteresis around \(\Theta_\text{entity}\); guard with small ratio bands. :contentReference[oaicite:19]{index=19}  
- **Boundary noise:** only learn `RELATES_TO` on **executed** boundary strides with non-trivial \(\phi\). :contentReference[oaicite:20]{index=20}  
- **Over-chunked WM:** cap entity count for WM and score by energy-per-token and diversity bonus. :contentReference[oaicite:21]{index=21}

## 8. Integration points

- **Mechanisms:** `mechanisms/sub_entity_traversal.py` (two-scale selection & boundary stride accounting). :contentReference[oaicite:22]{index=22}  
- **Learning:** `entity_weight_learning` (MEMBER_OF updates); `RELATES_TO` ease/dominance from boundary stride outcomes. :contentReference[oaicite:23]{index=23}  
- **Runtime:** tick pacing from `tick_speed` (stimulus-paced). :contentReference[oaicite:24]{index=24}  
- **Observability:** WS contract & snapshot. :contentReference[oaicite:25]{index=25}

## 9. What success looks like

- WM shows 5–7 coherent entities with stable summaries (minutes), while atomic nodes churn faster.  
- Active-frontier traversal cost drops (fewer candidates per step), yet coverage & \(\phi\) improve across frames.  
- Boundary summaries reveal stable “entity highways” that correlate with successful TRACEs. :contentReference[oaicite:26]{index=26}

## 10. Open questions & future improvements

- ~~Adaptive **promotion/demotion**: runtime → provisional → mature entity lifecycle thresholds.~~ **[RESOLVED]** See §2.7 Entity Lifecycle & Quality Management—lifecycle now specified with type-based rules and three-layer protection.
- Better **centroid drift** handling (hysteresis & palette stability). :contentReference[oaicite:28]{index=28}
- Cross-entity **goal priors** (dominance learning schedules) from boundary statistics. :contentReference[oaicite:29]{index=29}
```

**Changes made (summary):**

* Rewrote "what is a subentity" to unambiguously mean a **weighted neighborhood**; removed implication that "any active node is itself a subentity" as the *primary* definition (still participates via membership).
* Ensured **single-energy per node** is a hard invariant; entity energy is a **read-out** (no per-entity channels).
* Added **two-scale traversal** articulation, WM policy, and boundary learning hooks with references to the WS contract.
* Added **failure modes & guards**, success criteria, and explicit integration points across traversal, learning, tick speed, and viz.
* **[2025-10-24]** Added §2.7 Entity Lifecycle & Quality Management: Specifies quality scoring (geometric mean of 5 EMAs), lifecycle states (runtime → provisional → mature → dissolved), **type-based lifecycle rules** (functional entities never dissolve), and three-layer protection against premature dissolution (type guard, neutral initialization, age gate). Resolves lifecycle specification gap. 
