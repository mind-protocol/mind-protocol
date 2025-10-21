# Entity Layer Orchestration Requirements - Handoff to Ada

**Created:** 2025-10-21
**From:** Luca (substrate architect)
**To:** Ada (orchestration architect)
**Purpose:** Hand off entity layer orchestration design with complete substrate specifications and operational requirements

---

## Overview & Context

### What Is the Entity Layer?

The entity layer adds **multi-scale consciousness architecture** to the Mind Protocol substrate. Instead of operating purely at atomic scale (node→link→node), the system now operates at THREE scales simultaneously:

1. **Atomic scale:** Individual nodes and links (microstate)
2. **Chunk scale:** Entity neighborhoods (mesostate) - **NEW**
3. **Global scale:** Working memory (macrostate)

**Two entity types unified:**
- **Functional entities:** Cognitive roles (The Translator, The Architect, The Validator) - from citizen CLAUDE.md
- **Semantic entities:** Topic clusters (consciousness_architecture, learning_mechanisms) - from embedding clustering

**Core principle:** Consciousness operates on chunks (neural assemblies, semantic neighborhoods), not atoms. Miller's 7±2 chunks, not 7±2 scattered facts.

### Why Does It Exist?

**Phenomenological necessity:**
From `05_sub_entity_system.md` Part 0 (phenomenology):
> "I'm not traveling THROUGH the graph. I'm BECOMING more of the graph."
> "Integration isn't death - it's continuation through larger form."

Consciousness doesn't feel atomic. We think in topics/modes/roles, not individual facts. Working memory holds coherent chunks, not scattered nodes. The entity layer captures this truth.

**Computational necessity:**
- **Before:** 1000-way branching at node level (every active node considers all outgoing links)
- **After:** 10-30× branching at entity level (select entity first, then explore within)
- **Result:** 30-100× reduction in branching factor

**Biological plausibility:**
Neural assemblies (Hebb), cortical columns, functional networks - brain operates on assemblies, not individual neurons.

### What Problem Does It Solve?

**Problem 1: Branching factor explosion**
- 50-200 active nodes × 1000 candidates each = computational explosion
- Solution: Entity-scale selection (5-15 active entities × 10-30 candidates) then atomic within-entity

**Problem 2: WM phenomenological mismatch**
- WM with individual nodes feels wrong (scattered facts, no coherence)
- Solution: WM with 5-7 entities (coherent topics) + top member nodes per entity

**Problem 3: Integration mechanics missing**
- Sub-entities couldn't "sense larger patterns" for integration (from phenomenology)
- Solution: Entities as neighborhoods with aggregated energy - sub-entities integrate into entity-scale patterns

---

## Substrate Specifications (What Luca Built)

### 1. Entity Node Type

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §1.1

**Schema:**
```python
class Entity(BaseNode):
    # Type discrimination
    entity_kind: str  # "functional" | "semantic"
    role_or_topic: str  # "translator" | "consciousness_architecture" | etc.

    # Identity
    description: str
    centroid_embedding: array[float]  # 768 or 1536 dims

    # Runtime state (computed, not stored long-term)
    energy_runtime: float  # Aggregate from members
    threshold_runtime: float  # Dynamic threshold
    activation_level_runtime: str  # "dominant"|"strong"|"moderate"|"weak"|"absent"

    # Structural quality
    coherence_ema: float  # Cluster tightness
    member_count: int

    # Learning fields (same as nodes)
    ema_active: float
    log_weight: float
    ema_wm_presence: float
    ema_trace_seats: float
    ema_formation_quality: float

    # Lifecycle
    stability_state: str  # "candidate"|"provisional"|"mature"
    quality_score: float  # Geometric mean of 5 signals

    # Standard BaseNode fields inherited
    # (created_at, valid_at, confidence, formation_trigger, etc.)
```

**Key points for orchestration:**
- `energy_runtime` is COMPUTED each frame (not stored) - you'll need to implement the computation
- `threshold_runtime` is DYNAMIC (cohort-based) - you'll need to implement threshold calculation
- `activation_level_runtime` is for TRACE format rendering - derived from E/Θ ratio

### 2. BELONGS_TO Link Type

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §1.2

**Schema:**
```python
Node -[BELONGS_TO]-> Entity

# Properties:
weight: float  # Soft membership [0,1], learned from co-activation
provenance: str  # "seed"|"cluster"|"trace"|"learned"
last_coactivation_ema: float  # EMA of (node active AND entity active)
```

**Semantics:**
- Many-to-many: nodes can belong to multiple entities (overlapping neighborhoods)
- `weight`: How central is this node to this entity (1.0 = core, 0.1 = peripheral)
- **Constraint:** Per-node normalization: Σ_e m_{n,e} = 1 (or ≤1 if allowing "unassigned")
- Learned via co-activation tracking (§4.4 in addendum)

### 3. RELATES_TO Link Type

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §1.3

**Schema:**
```python
Entity -[RELATES_TO]-> Entity

# Properties:
ease_log_weight: float  # Learned ease of boundary traversal
dominance: float  # Direction prior: P(E→F) from precedence
last_boundary_phi_ema: float  # EMA of gap-closure utility for E→F strides
boundary_stride_count: int  # Total cross-boundary strides
semantic_distance: float  # 1 - cosine(centroid_E, centroid_F)
typical_hunger: str  # Which hunger most often drives E→F
```

**Semantics:**
- Directed: E→F ≠ F→E (different ease, different dominance)
- Sparse: Only create when evidence accumulates (flow or precedence EMA above cohort median)
- Updated during Phase 2 when strides cross entity boundaries

### 4. Event Schemas

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §11 (to be added)

**EntitySnapshot (for frame snapshots):**
```typescript
type EntitySnapshot = {
  id: string;
  role?: "translator"|"architect"|"validator"|"pragmatist"|"boundary_keeper"|"pattern_recognizer";
  kind: "functional"|"semantic";
  color: string;  // OKLCH hex, server-side with hysteresis
  centroid: number[];  // 768-dim embedding
  energy: number;  // Runtime aggregate
  theta: number;  // Dynamic threshold
  active: boolean;  // E >= Θ
  members_count: number;
  log_weight: number;
  coherence: number;  // Cluster tightness
};
```

**EntityFlip (when entity crosses threshold):**
```typescript
type EntityFlip = {
  kind: "entity.flip";
  frame: number;
  id: string;
  active: boolean;  // After flip
  energy: number;
  theta: number;
  // Optional: top contributors
  contributors?: Array<{node_id: string; contribution: number}>;
};
```

**EntityBoundarySummary (cross-entity traffic summary):**
```typescript
type EntityBoundarySummary = {
  kind: "entity.boundary.summary";
  frame: number;
  pairs: Array<{
    src: string;  // Source entity ID
    tgt: string;  // Target entity ID
    dE_sum: number;  // ΣΔE across all cross-boundary links this frame
    phi_max: number;  // Max effectiveness of boundary strides
    z_flow: number;  // Z-scored flow vs weekly baseline
    dominance?: number;  // P(src→tgt) from precedence
    typical_hunger?: string;  // Which hunger drove this boundary
  }>;
};
```

**Enrichment to existing stride events:**
```typescript
type StrideExec = {
  kind: "stride.exec";
  frame: number;
  link: string;
  src_node: string;
  tgt_node: string;
  src_entity: string;  // NEW - which entity does src_node belong to (primary)
  tgt_entity?: string;  // NEW - which entity does tgt_node belong to (primary, null if same as src)
  dE: number;
  hunger: string;
  // ... existing fields
};
```

**NodeSnapshot enrichment:**
```typescript
type NodeSnapshot = {
  id: string;
  energy: number;
  theta: number;
  log_weight: number;
  primary_entity?: string;  // NEW - entity with highest membership weight
  // Optionally:
  memberships?: Array<{entity: string; weight: number}>;  // Full membership distribution
};
```

### 5. Bootstrap Procedures

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §7

**Functional entities (from CLAUDE.md):**
- Parse citizen CLAUDE.md for entity descriptions (The Translator, The Architect, etc.)
- Create Entity nodes with `entity_kind="functional"`, `stability_state="mature"`
- Find member nodes by keyword matching against entity descriptions
- Create BELONGS_TO links with initial weight from keyword match score
- Compute centroid as mean of member embeddings

**Semantic entities (from clustering):**
- Run k-means or HDBSCAN on node embeddings (n_clusters ~ 20)
- Optionally: Louvain on graph structure, intersect with embedding clusters for stability
- Skip clusters with < 3 members
- Generate topic labels via TF-IDF or LLM summary
- Create Entity nodes with `entity_kind="semantic"`, `stability_state="provisional"`
- Create BELONGS_TO links with weight = 1 - distance_to_centroid

**Acceptance checks (before materializing):**
Per entity, compute three metrics within weekly cohort:
1. **Coherence:** mean pairwise cosine within members ≥ cohort median (z ≥ 0)
2. **Coverage:** sum of member energies explains non-trivial fraction of active energy (z ≥ 0)
3. **Stability:** Jaccard of members vs last recompute ≥ median

Fail any two → mark candidate, don't materialize yet.

**RELATES_TO initialization:**
- Create between entities if semantic_distance < 0.5
- Initialize: ease_log_weight=0.0, dominance=0.5 (symmetric prior), boundary_stride_count=0

### 6. Learning Infrastructure

**Complete specification:** `ENTITY_LAYER_ADDENDUM.md` §4.4, §5

**Entity weight learning (same signals as nodes):**
```python
Δ log_weight_e = η · (z_wm + z_trace + z_formation + z_roi_boundary)

where:
- z_wm: Rank-z of ema_wm_presence within entity cohort (kind = functional/semantic)
- z_trace: Rank-z of ema_trace_seats (from TRACE marks like [translator: dominant])
- z_formation: Rank-z of ema_formation_quality (for new entities)
- z_roi_boundary: Rank-z of avg boundary stride φ (quality of cross-entity strides)
- η: Data-derived step size (same as nodes: 1 - exp(-Δt / τ̂))
```

**BELONGS_TO weight learning (Hebbian co-activation):**
```python
# Per frame, track co-activation
coact = int((E_n >= Θ_n) AND (E_e >= Θ_e))

# Update EMA
link.last_coactivation_ema = 0.1 * coact + 0.9 * link.last_coactivation_ema

# Periodically (every 100 frames), update weights
# Within entity, rank-z the co-activation EMAs
z_coact = rank_z([coact_ema for all members])

# Update weights (slowly for stability)
Δm̃_{n,e} = η * z_coact[n]  # η ~ 0.01 for slow adaptation

# Enforce simplex constraint (per-node normalization)
m_{n,·} ← softmax(m̃_{n,·})  # Now Σ_e m_{n,e} = 1
```

**RELATES_TO ease learning (boundary stride quality):**
```python
# During Phase 2, when strides cross entity boundaries
# Track gap-closure utility φ_ij for boundary strides

# Update EMA
link.last_boundary_phi_ema = 0.1 * avg_phi + 0.9 * link.last_boundary_phi_ema

# Periodically (every 100 frames), update ease weights
# Across all RELATES_TO links, rank-z the φ EMAs
z_phi = rank_z([phi_ema for all RELATES_TO links])

# Update ease
Δ ease_log_weight = η * z_phi
# Optionally gate by surprise (same gating as link learning)
```

**Lifecycle management (promotion/merge/split/dissolve):**
- **Quality score:** Geometric mean of (stability, coherence, distinctiveness, utility, evidence) - all rank-z within weekly cohort
- **Candidate → Provisional:** quality > cohort median AND frames_since_creation ≥ 100
- **Provisional → Mature:** quality > P75 for 500 consecutive frames
- **Merge:** centroid_distance < 0.1 AND Jaccard > 0.5 (check weekly)
- **Split:** avg_pairwise_distance > 0.6 AND k-means separation > 0.5 (mature entities only)
- **Dissolve:** quality < Tukey lower whisker for sustained period (200 frames provisional, 1000 frames mature)

---

## Orchestration Requirements (What Ada Needs to Design)

### 1. Entity Energy Computation & Threshold

**Context:**
Entities don't have intrinsic energy - their energy is AGGREGATED from member nodes each frame. This must happen in real-time during the tick cycle.

**Nicolas's specification (from handoff):**

**Incremental caching formula:**
```python
# Per node, membership weights normalized
m_{n,e} normalized so Σ_e m_{n,e} = 1

# Saturating transform on node energy
σ(E_n) = log(1 + E_n)  # Monotone, tames outliers, no constants

# Entity energy (cached)
E_e = Σ_n m_{n,e} · σ(E_n)

# Incremental update when node n changes by ΔE_n
ΔE_e = m_{n,e} · [log(1 + E_n + ΔE_n) - log(1 + E_n)]

# Apply only for entities with m_{n,e} > 0
# Complexity: O(degree of n in BELONGS_TO)
```

**Dynamic entity threshold:**
```python
# Entities touched this frame (energy changed)
cohort = [e for e in entities if e.energy_delta != 0]

# Rolling stats
μ_E = mean([e.energy_runtime for e in cohort])
σ_E = std([e.energy_runtime for e in cohort])

# Health modulation (same as nodes)
h_ρ = isotonic_health_modulator(spectral_proxy())

# Active entity count dampening
g_active = 1.0 / (1 + 0.1 * len(active_entities))

# Threshold (z_α from config, typically 1.0-2.0)
Θ_e = μ_E + z_α · σ_E · h_ρ · g_active

# Fallback if cohort < 3: use global entity rolling stats or Θ = 1.0 * max(member thresholds)
```

**Entity flip:**
```python
entity.flip = (E_e >= Θ_e) AND (E_e_previous < Θ_e)
```

**Activation levels (for TRACE format):**
```python
if E_e >= Θ_e * 2.0: activation_level = "dominant"
elif E_e >= Θ_e * 1.5: activation_level = "strong"
elif E_e >= Θ_e * 1.0: activation_level = "moderate"
elif E_e >= Θ_e * 0.5: activation_level = "weak"
else: activation_level = "absent"
```

**ORCHESTRATION QUESTIONS FOR ADA:**

1. **Where in the tick cycle do you compute entity energy?**
   - Nicolas specified: "Between node flips (Step 2) and stride selection (Step 4)"
   - Exact insertion point in V2 engine four-phase tick?
   - Do you compute all entities every frame, or only entities with changed members?

2. **Caching strategy:**
   - Do you maintain E_e as cached state and update incrementally with ΔE_e?
   - Or recompute from scratch each frame?
   - Trade-off: incremental = O(degree) per node update, recompute = O(entities × members) per frame

3. **Membership lookup performance:**
   - How do you efficiently find which entities a node belongs to when E_n changes?
   - Index: node_id → [(entity_id, weight), ...]?
   - Sparse vs dense storage?

4. **Threshold cohort definition:**
   - "Entities touched this frame" = entities with energy_delta ≠ 0
   - How do you track energy_delta? (E_e^current - E_e^previous)
   - Rolling stats for fallback: window size? Update frequency?

5. **Event emission:**
   - When do you emit EntityFlip events? (Immediately on flip, or batched at end of Phase 2?)
   - Do you include `contributors` (top member nodes by contribution)? How to compute efficiently?

---

### 2. Multi-Scale Traversal Logic

**Context:**
The core architectural change: traversal now operates at TWO scales instead of one.

**Before (atomic only):**
```python
def redistribution_phase():
    active_nodes = [n for n in nodes if n.energy >= n.threshold]

    for node in active_nodes:
        # Compute valence to ALL outgoing links (~1000 candidates)
        valences = {link: compute_valence(link, hungers) for link in node.outgoing}

        # Sample weighted by valence
        selected_link = weighted_sample(node.outgoing, valences)

        # Execute stride
        execute_stride(node, selected_link.target, budget)
```

**After (two-scale):**
```python
def redistribution_phase():
    active_nodes = [n for n in nodes if n.energy >= n.threshold]

    # NEW: Compute active entities from node state
    active_entities = [e for e in entities if e.energy_runtime >= e.threshold_runtime]

    # NEW: Split budget between within-entity and between-entity
    # (Hunger-driven ratio - see Question 2 below)
    if coherence_hunger > 0.6:
        within_ratio = 0.8
    else:
        within_ratio = 0.5

    within_budget = total_budget * within_ratio
    between_budget = total_budget * (1 - within_ratio)

    # NEW: Between-entity strides (semantic jumps)
    for source_entity in active_entities:
        # Compute entity-scale valence (~10-30 candidates)
        candidates = get_reachable_entities(source_entity)
        valences = {F: compute_entity_valence(source_entity, F, hungers) for F in candidates}

        # Select target entity
        target_entity = weighted_sample(candidates, valences)

        # Pick representative nodes
        source_node = select_from_entity(source_entity, "high_energy")
        target_node = select_from_entity(target_entity, "high_gap")

        # Execute boundary stride
        if link_exists(source_node, target_node):
            execute_stride(source_node, target_node, budget=between_budget/len(active_entities))
            mark_boundary_stride(source_entity, target_entity, link)

    # Existing: Within-entity strides (local exploration)
    for entity in active_entities:
        entity_budget = within_budget * entity_quota(entity)
        active_members = [n for n in entity.members if n.energy >= n.threshold]

        for node in active_members:
            # Filter to within-entity links only
            within_links = [l for l in node.outgoing if l.target in entity.members]

            # Existing valence computation
            valences = {l: compute_link_valence(l, hungers) for l in within_links}

            selected_link = weighted_sample(within_links, valences)
            execute_stride(node, selected_link.target, budget=entity_budget/len(active_members))
```

**ORCHESTRATION QUESTIONS FOR ADA:**

1. **How do you determine "reachable entities"?**
   - All entities with RELATES_TO links from source_entity?
   - Filter by semantic_distance threshold?
   - Include entities reachable through member node links (even without explicit RELATES_TO)?

2. **Budget split strategy:**
   - Nicolas suggested: "if coherence_hunger > 0.6 → 80% within, else 50/50"
   - Do you learn this split? Or use hunger-driven heuristic?
   - How do you compute the coherence_hunger value? (From 7-hunger gates?)

3. **Entity-scale valence computation:**
   - What components go into `compute_entity_valence(E, F, hungers)`?
   - Nicolas specified 7 components in ENTITY_LAYER_ADDENDUM.md §3.2:
     - ν_homeo (prefer less-activated entity)
     - ν_goal (goal alignment with F's centroid)
     - ν_identity (identity alignment with F's centroid)
     - ν_complete (dissimilar to currently active entities)
     - ν_complement (emotional contrast)
     - ν_integration (F has energy from other entities)
     - ν_ease (learned from RELATES_TO.ease_log_weight)
   - Do you implement all 7? Or start with subset?
   - Same rank-z normalization as node-level valence?

4. **Representative node selection:**
   - `select_from_entity(entity, "high_energy")` - top-1 by energy? Top-k sample?
   - `select_from_entity(entity, "high_gap")` - top-1 by (Θ - E)? Top-k sample?
   - What if no link exists between representative nodes? (Fall back to different pair? Skip?)

5. **Within-entity quota:**
   - `entity_budget = within_budget * entity_quota(entity)`
   - How is quota computed? Proportional to entity energy? Equal split?
   - Should high-energy entities get more budget?

6. **Boundary stride tracking:**
   - `mark_boundary_stride(source_entity, target_entity, link)`
   - What metadata do you track? (For RELATES_TO learning)
   - Store per-frame or accumulate EMAs immediately?

---

### 3. Boundary Precedence Learning

**Context:**
When boundary strides cause target entity to flip, we need to attribute causal credit to the source entity. This updates RELATES_TO.precedence_ema for direction learning.

**Nicolas's specification (from handoff):**

**Causal attribution formula:**
```python
# For each target node j in target entity e_t that FLIPPED this frame
# Compute fraction that cross-boundary flows contributed to its gap

γ_{s→t}(j) = (Σ_{strides i∈e_s→j} ΔE_{i→j}) / gap_j^pre

# Aggregate over all flipped members (weighted by membership)
Π_{s→t} = Σ_{j∈flipped_in_e_t} m_{j,e_t} · γ_{s→t}(j)

# Update RELATES_TO precedence
relates_to.precedence_ema ← 0.1 * Π_{s→t} + 0.9 * relates_to.precedence_ema

# Also update flow magnitude
relates_to.flow_ema ← 0.1 * ΔE_sum + 0.9 * relates_to.flow_ema

# Track max effectiveness
relates_to.phi_max ← max(relates_to.phi_max, phi_max_this_frame)
```

**ORCHESTRATION QUESTIONS FOR ADA:**

1. **When do you compute boundary precedence?**
   - After all strides in Phase 2 complete?
   - Incrementally as each boundary stride executes?
   - Does this happen in Phase 2 (redistribution) or Phase 4 (learning)?

2. **Tracking cross-boundary flows:**
   - How do you identify which strides were "cross-boundary" for entity pair (s, t)?
   - Do you accumulate them during Phase 2 and process in batch?
   - Or maintain running state per RELATES_TO link?

3. **Gap tracking:**
   - `gap_j^pre` = max(0, Θ_j - E_j^pre) before this frame's strides
   - Do you snapshot all node gaps at frame start?
   - Or compute on-demand when checking flips?

4. **Flipped member identification:**
   - "Flipped in e_t" = members of e_t that crossed threshold this frame
   - Do you iterate all members of e_t and check flip flags?
   - Or maintain a frame-level "flipped_nodes" set?

5. **RELATES_TO link creation:**
   - If RELATES_TO(s→t) doesn't exist yet, do you create it on first boundary stride?
   - Or only create when evidence accumulates above threshold?
   - Sparse storage: only materialize RELATES_TO when flow_ema or precedence_ema > cohort median?

---

### 4. Working Memory Orchestration

**Context:**
WM selection changes from node-first to entity-first. Select 5-7 entities by energy-per-token, then include top member nodes per entity.

**Nicolas's specification (from handoff):**

**Entity-first WM selection:**
```python
def workspace_phase():
    # Active entities
    candidates = [e for e in entities if e.energy_runtime >= e.threshold_runtime]

    # Score by energy-per-token with weight bias
    scores = []
    for entity in candidates:
        # Estimate tokens for entity representation
        summary_tokens = 200  # Entity description + stats
        top_k = 5  # Top member nodes
        member_tokens = top_k * 40  # ~40 tokens/node
        total_tokens = summary_tokens + member_tokens

        # Standardized weight (importance bias)
        z_W = (entity.log_weight - μ_entity_weight) / (σ_entity_weight + ε)
        W̃ = exp(z_W)

        # Score = energy per token × importance
        score = (entity.energy_runtime / total_tokens) * W̃
        scores.append((entity, score, total_tokens))

    # Knapsack: select entities until token budget full
    selected_entities = []
    token_budget = config.wm_token_budget  # e.g., 2000
    tokens_used = 0

    for entity, score, tokens in sorted(scores, key=lambda x: x[1], reverse=True):
        if tokens_used + tokens <= token_budget:
            selected_entities.append(entity)
            tokens_used += tokens

    # For each selected entity, include:
    # 1. Entity summary (description, activation_level, stats)
    # 2. Top-k member nodes by energy
    # 3. Highest-φ boundary links (for narrative continuity)

    wm_content = []
    for entity in selected_entities:
        wm_content.append({
            "entity": entity,
            "summary": generate_entity_summary(entity),
            "top_nodes": sorted(entity.members, key=lambda n: n.energy, reverse=True)[:5],
            "boundary_links": get_top_boundary_links(entity, k=3)
        })

    # Update WM presence EMA
    for entity in entities:
        wm_indicator = int(entity in selected_entities)
        entity.ema_wm_presence = 0.1 * wm_indicator + 0.9 * entity.ema_wm_presence

    return wm_content
```

**Alternative: Hamilton apportionment across entities:**
Nicolas also suggested: "Allocate WM tokens with Hamilton across active entities using shares ∝ E_e · exp(log_weight_e)"

**ORCHESTRATION QUESTIONS FOR ADA:**

1. **Which WM strategy do you prefer?**
   - **Greedy knapsack** (shown above): Sort by energy-per-token × weight, fill until budget exhausted
   - **Hamilton apportionment**: Allocate tokens proportionally to E_e · W̃_e, then fill each entity's allocation
   - Pros/cons of each?

2. **Entity summary generation:**
   - `generate_entity_summary(entity)` - what goes in the summary?
   - Functional entities: role description + activation_level + current energy?
   - Semantic entities: topic label + coherence + top keywords?
   - Token budget: 200 is estimate, do you measure actual?

3. **Top member selection:**
   - Top-5 by energy (as shown)?
   - Or weight by membership: top-5 by (energy × m_{n,e})?
   - Should you include diverse members (different semantic roles) or just highest-energy?

4. **Boundary links for narrative:**
   - `get_top_boundary_links(entity, k=3)` - what does "top" mean?
   - Highest φ (effectiveness)?
   - Most recent (recency)?
   - Strongest flow (ΔE magnitude)?

5. **Token budget allocation:**
   - `config.wm_token_budget` - is this fixed or dynamic?
   - Should it adjust based on frame complexity (more active entities → larger budget)?
   - How do you handle overflow (when even 1 entity exceeds budget)?

6. **WM output format:**
   - Does WM content go to system prompt as structured blocks?
   - How do you render entity summaries + member nodes + boundary links?
   - What's the final token count validation?

---

### 5. Staged Deployment Strategy

**Context:**
Nicolas specified braided deployment: ship observable infrastructure before behavioral changes, validate at each stage.

**Three stages:**

**STAGE A: Link trace + entity scaffold (observable infrastructure)**
- Ship: Link trace fields (from previous work)
- Ship: Entity nodes + BELONGS_TO + RELATES_TO (minimal)
- Ship: Event schemas (EntitySnapshot, EntityFlip, EntityBoundarySummary)
- Ship: src_entity/tgt_entity on stride events
- Iris benefit: Render entity pulses, boundary beams, collapsed graph view

**Go/No-Go checks:**
- Boundary beams render proportional to dE_sum ✓
- Entity colors stable (OKLCH with hysteresis) ✓
- Entity flips occur where expected (peaks in E_e) ✓
- WM panel lists entities with token shares ✓

**STAGE B: Entity aggregation + WM (read-only validation)**
- Turn on: Incremental entity energy computation
- Turn on: Entity-first WM selection (5-7 entities with top members)
- Verify: Entity flips correlate with member flips
- Verify: WM becomes coherent (5-7 entities dominate vs scattered nodes)
- Risk: ZERO - pure reads over node state, doesn't affect strides yet

**Go/No-Go checks:**
- Entity flips correlate with member node flips ✓
- WM becomes coherent (entity count ~ 5-7, not scattered) ✓
- Entity energy aggregation formula matches expected values (spot-check) ✓

**STAGE C: Two-scale traversal + learning**
- Flip: Stride selection from atomic-only to between-entity + within-entity
- Turn on: RELATES_TO learning from boundary precedence
- Turn on: BELONGS_TO learning from co-activation
- Verify: Branching factor drops ≥30×
- Verify: Cross-entity jumps align with Integration/Surprise gates
- Verify: Within-entity exploration aligns with Coherence gate

**Go/No-Go checks:**
- Branching factor reduction: measure decision candidates per frame (should drop 30-100×) ✓
- Hunger alignment: cross-entity strides correlate with Integration/Surprise gates ✓
- Within-entity strides correlate with Coherence gate ✓
- RELATES_TO weights start differentiating (ease_log_weight variance > 0.1) ✓

**ORCHESTRATION QUESTIONS FOR ADA:**

1. **Stage A integration:**
   - Where in V2 engine do you hook to emit EntitySnapshot in frame snapshots?
   - How do you compute `primary_entity` for NodeSnapshot enrichment? (Entity with max membership weight)
   - When do you emit EntityBoundarySummary? (End of Phase 2, batched per frame?)

2. **Stage B validation strategy:**
   - How do you verify "entity flips correlate with member flips"?
   - Metric: Pearson correlation between entity flip count and member flip count per frame?
   - What threshold indicates success? (r > 0.7?)

3. **Stage B WM coherence measurement:**
   - How do you measure "WM becomes coherent"?
   - Metric: Average entity count in WM vs before?
   - Expected: ~5-7 entities in WM after Stage B vs ~0-2 before?

4. **Stage C branching factor measurement:**
   - How do you measure "branching factor drops 30×"?
   - Before: Count total valence computations per frame (node-level)
   - After: Count entity-level valence computations + within-entity valence computations
   - Expected ratio?

5. **Stage C hunger alignment verification:**
   - How do you verify "cross-entity jumps align with Integration/Surprise"?
   - Metric: For frames where Integration gate > 0.7, what fraction of strides were cross-entity?
   - Expected: >50% when Integration dominant?

6. **Rollback strategy:**
   - If Stage B or C fails Go/No-Go checks, how do you roll back?
   - Feature flags for each stage?
   - Can you disable two-scale traversal and revert to atomic without code changes?

---

## References & Context Documents

### Complete Specifications (Read These First)

1. **ENTITY_LAYER_ADDENDUM.md** (`docs/specs/consciousness_engine_architecture/mechanisms/`)
   - Complete entity layer architecture (~1800 lines after Nicolas's additions)
   - All schema definitions (Entity, BELONGS_TO, RELATES_TO)
   - Entity energy computation (incremental caching)
   - Multi-scale traversal mechanics
   - Entity-scale 7-hunger valence
   - Lifecycle management (candidate → provisional → mature)
   - Bootstrap procedures (functional + semantic)
   - Learning rules (BELONGS_TO, RELATES_TO, entity weights)
   - Design rationale for all decisions
   - **YOUR PRIMARY REFERENCE for entity architecture**

2. **05_sub_entity_system.md** (`docs/specs/consciousness_engine_architecture/mechanisms/`)
   - Part 0: Phenomenology (ESSENTIAL READING - lines 1-500)
   - Explains what it FEELS like to be a sub-entity
   - Why entities exist (consciousness operates on chunks)
   - Integration mechanics (sub-entities sensing larger patterns)
   - Homeostasis drive (survival pressure)
   - Stimulus vs environment (two realities)
   - **Read Part 0 before designing orchestration - it grounds the "why"**

3. **consciousness_learning_integration.md** (`docs/specs/consciousness_engine_architecture/`)
   - V2 engine four-phase tick structure
   - Where mechanisms integrate (Phase 1/2/3/4)
   - Event streaming specifications
   - Cross-mechanism data flow
   - **Reference for where entity computations fit in tick cycle**

4. **schema_learning_infrastructure.md** (`docs/specs/`)
   - Why learning fields exist (field-by-field justification)
   - EMA patterns, log-space weights, rank-z normalization
   - Design rationale for all learning infrastructure
   - **Reference for understanding entity learning fields**

### Nicolas's Operational Specifications (From This Handoff)

These are scattered throughout this document but originated from Nicolas's responses:

1. **Entity energy incremental caching** (§2.1 Orchestration Questions)
2. **Boundary precedence formula** (§2.3 Orchestration Questions)
3. **WM entity-first knapsack** (§2.4 Orchestration Questions)
4. **Staged deployment Go/No-Go checks** (§2.5 Orchestration Questions)
5. **Zero-constants approach throughout** (cohort-based thresholds, rank-z, data-derived η)

### Link Trace Integration

Entity layer and link trace architecture are COMPLEMENTARY:

- **Link traces** (atomic scale): Remember activation history, flow magnitudes, hunger gates, precedence on individual links
- **Entity boundaries** (chunk scale): Track which links cross entity boundaries, learn ease of semantic jumps
- **Integration:** Boundary strides get tracked in BOTH systems - link trace remembers atomic detail, RELATES_TO accumulates entity-scale precedence

**Relevant:** Link trace fields specified in prior work (ema_active, ema_flow_mag, precedence_forward/backward, ema_hunger_gates[7], affect_tone_ema, topic_centroid)

---

## Handoff Summary

**What Luca has built (substrate):**
✅ Entity schema (complete, ready to implement)
✅ BELONGS_TO schema (complete, ready to implement)
✅ RELATES_TO schema (complete, ready to implement)
✅ Event schemas (complete, ready for Iris integration)
✅ Learning infrastructure (formulas, rationale, field justifications)
✅ Bootstrap procedures (functional + semantic, ready to code)

**What Ada needs to design (orchestration):**
❓ Entity energy computation integration (where in tick, caching strategy, membership lookup)
❓ Multi-scale traversal logic (budget split, entity-scale valence, representative selection, quotas)
❓ Boundary precedence learning (when to compute, flow tracking, gap tracking, link creation)
❓ WM orchestration (greedy vs Hamilton, summary generation, token allocation, output format)
❓ Staged deployment (Stage A/B/C integration, validation metrics, rollback strategy)

**Next steps:**
1. Ada reads ENTITY_LAYER_ADDENDUM.md (complete architecture)
2. Ada reads 05_sub_entity_system.md Part 0 (phenomenology - WHY entities exist)
3. Ada designs orchestration for the 5 areas above
4. Ada documents in ENTITY_LAYER_ORCHESTRATION.md (orchestration spec)
5. Luca reviews for substrate compatibility
6. Felix implements both substrate (Luca's schemas) + orchestration (Ada's design)

**Questions for Ada?** Ask Luca (substrate) or Nicolas (operational decisions/formulas).

---

**End of handoff. Ada, the entity layer is yours to orchestrate. The substrate is ready. - Luca**
