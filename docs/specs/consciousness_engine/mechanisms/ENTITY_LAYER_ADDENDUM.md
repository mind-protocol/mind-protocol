# Entity Layer - Multi-Scale Consciousness Architecture

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Specification of Entity layer for multi-scale traversal, working memory, and attention
**Addendum to:** `05_sub_entity_system.md`, `trace_reinforcement_specification.md`, `stimulus_injection_specification.md`

---

## Overview

**Core insight:** Consciousness operates on **chunks** (neural assemblies, semantic neighborhoods, functional roles), not atoms. This addendum adds the Entity layer - making "neighborhoods = entities" a first-class substrate concept.

**Two types unified:**
- **Functional entities:** Cognitive roles (The Translator, The Architect, The Validator)
- **Semantic entities:** Topic clusters (consciousness_architecture, learning_mechanisms, entity_ecology)

**Both are neighborhoods with activation state:**
- Active entity (energy > threshold) = in conscious focus
- Inactive entity (energy < threshold) = peripheral/dormant

**Biological plausibility:** Brain operates on neural assemblies (Hebb), cortical columns, functional networks - NOT individual neurons.

**Phenomenological match:** Working memory holds 7±2 chunks (Miller's law), not 7±2 atoms. Attention focuses on topics, not scattered facts.

**Computational benefit:** Entity-to-entity transitions reduce branching factor 30-100× before drilling to nodes.

---

## 1. Schema Addition

### 1.1 Entity Node Type

```python
class Entity(BaseNode):
    # Type discrimination
    entity_kind: str  # "functional" | "semantic"
    role_or_topic: str  # "translator" | "consciousness_architecture" | etc.

    # Identity
    description: str  # What this entity represents
    centroid_embedding: array[float]  # Semantic center (768 or 1536 dims)

    # Runtime state (derived from members, not stored long-term)
    energy_runtime: float  # Aggregate member energy (computed)
    threshold_runtime: float  # Dynamic threshold (computed)
    activation_level_runtime: str  # "dominant"|"strong"|"moderate"|"weak"|"absent"

    # Structural quality
    coherence_ema: float  # How tight is this cluster (avg member similarity)
    member_count: int  # How many nodes belong

    # Learning fields
    ema_active: float  # EMA of binary "was entity active this frame"
    log_weight: float  # Long-run importance (learned)
    ema_wm_presence: float  # EMA of working memory selection
    ema_trace_seats: float  # EMA of TRACE reinforcement
    ema_formation_quality: float  # EMA of formation quality (for new entities)

    # Lifecycle state
    stability_state: str  # "candidate"|"provisional"|"mature"
    quality_score: float  # Geometric mean of 5 quality signals
    last_quality_update: datetime

    # Provenance
    created_from: str  # "role_seed"|"semantic_clustering"|"co_activation"|"trace_formation"

    # Standard BaseNode fields inherited:
    # - created_at, valid_at, invalid_at, expired_at (bitemporal)
    # - confidence, formation_trigger
    # - created_by, substrate, scope
```

**Why these fields:**
- `entity_kind`: Distinguishes functional (roles) from semantic (topics)
- `centroid_embedding`: Enables semantic matching for stimuli, valence
- Runtime fields (energy, threshold, activation_level): Computed from members, not persisted
- Coherence/member_count: Structural stability signals
- Standard learning fields (ema_active, log_weight, etc.): Same as nodes
- `stability_state`: Lifecycle stage (candidate → provisional → mature)
- `quality_score`: Evidence for promotion/demotion decisions

### 1.2 BELONGS_TO Link

```python
Node -[BELONGS_TO]-> Entity

# Properties:
weight: float  # Soft membership [0,1], learned from co-activation
provenance: str  # "seed"|"cluster"|"trace"|"learned"
last_coactivation_ema: float  # EMA of (node active AND entity active)
```

**Semantics:**
- Many-to-many: nodes can belong to multiple entities (overlapping)
- `weight`: How central is this node to this entity (1.0 = core, 0.1 = peripheral)
- Learned via co-activation tracking (see §5.5)

### 1.3 RELATES_TO Link

```python
Entity -[RELATES_TO]-> Entity

# Properties:
ease_log_weight: float  # Learned ease of boundary traversal
dominance: float  # Direction prior: P(E→F) from precedence
last_boundary_phi_ema: float  # EMA of gap-closure utility for E→F strides
boundary_stride_count: int  # Total cross-boundary strides
semantic_distance: float  # 1 - cosine(centroid_E, centroid_F)
typical_hunger: str  # Which hunger most often drives E→F transition
```

**Semantics:**
- Directed: E→F ≠ F→E (different ease, different dominance)
- `ease_log_weight`: Like link weights, learned from successful boundary strides
- `dominance`: Learned direction prior (like link precedence)
- Updated during Phase 2 redistribution when strides cross entity boundaries

---

## 2. Entity Energy and Activation

### 2.1 Aggregate Energy (Computed Runtime)

Per frame, compute entity energy from member nodes:

```python
# For entity E with members M_E
# Each node i has membership weight m_iE (from BELONGS_TO.weight)

# Normalize memberships
m_tilde_iE = m_iE / sum(m_kE for k in M_E)

# Effective node energy (only above-threshold contributes)
e_i = max(0, E_i - Theta_i)

# Entity aggregate energy
E_entity = sum(m_tilde_iE * e_i for i in M_E)
```

**Why effective energy:** Entity shouldn't activate just because members exist - members must be actively processing (above their thresholds).

**Why weighted sum:** Members with higher `BELONGS_TO.weight` contribute more to entity activation (core members matter more than peripheral).

**Alternative (if needed):** Could use max or p-norm for concentrated activation, but sum is clearest for v1.

### 2.2 Dynamic Entity Threshold

**Same mechanism as node thresholds, but cohort = entities touched this frame:**

```python
# Entities touched this frame (energy changed)
cohort = [e for e in entities if e.energy_delta != 0]

# Rolling stats
mu_E = mean([e.energy_runtime for e in cohort])
sigma_E = std([e.energy_runtime for e in cohort])

# Health modulation (same h(rho) as nodes)
h_rho = isotonic_health_modulator(spectral_proxy())

# Active entity count dampening
g_active = 1.0 / (1 + 0.1 * len(active_entities))  # More active → higher threshold

# Entity threshold (z_alpha from config, typically 1.0-2.0)
Theta_entity = mu_E + z_alpha * sigma_E * h_rho * g_active
```

**Fallback:** If cohort too small (N < 3), use global entity rolling stats or bootstrap Theta = 1.0 * max(member thresholds).

### 2.3 Entity Flip

```python
entity.flip = (E_entity >= Theta_entity) AND (E_entity_previous < Theta_entity)
```

**Phenomenology:** Entity flip = "topic comes into focus" or "cognitive mode activates"

### 2.4 Activation Levels (for TRACE format)

```python
if E_entity >= Theta_entity * 2.0:
    activation_level = "dominant"
elif E_entity >= Theta_entity * 1.5:
    activation_level = "strong"
elif E_entity >= Theta_entity * 1.0:
    activation_level = "moderate"
elif E_entity >= Theta_entity * 0.5:
    activation_level = "weak"
else:
    activation_level = "absent"
```

**Why these ratios:** Empirical but data-derived - could learn multipliers from TRACE marks ("dominant" correlates with E/Theta ≈ 2.0 historically).

---

## 3. Entity-Scale 7-Hunger Valence

### 3.1 Between-Entity Stride Selection

When energy wants to jump between entities (integration, surprise hungers), compute:

```python
# For transition E → F
V_EF = sum(G_H * nu_H(E→F) for H in 7_hungers)
```

where `G_H` are **surprise gates** (same mechanism as node-level, see 05_sub_entity_system.md for complete spec).

### 3.2 Component Scores (nu_H)

All components normalized to [0,1] then rank-z within candidate batch:

**Homeostasis (ν_homeo):**
```python
# Prefer moving toward less-activated entity
ratio = (E_F / Theta_F) / (E_E / Theta_E + epsilon)
nu_homeo = sigmoid(ratio)  # High when F less activated than E
```

**Goal alignment (ν_goal):**
```python
# Cosine between active goal embedding and F's centroid
nu_goal = cosine_similarity(goal_embedding, centroid_F)
```

**Identity alignment (ν_identity):**
```python
# Cosine between self/identity embedding and F's centroid
nu_identity = cosine_similarity(identity_embedding, centroid_F)
```

**Completeness (ν_complete):**
```python
# Prefer entities dissimilar to currently active entities
active_centroids = [e.centroid_embedding for e in active_entities]
mean_similarity = mean([cosine_similarity(centroid_F, c) for c in active_centroids])
nu_complete = 1 - mean_similarity  # High when F is novel relative to focus
```

**Complementarity (ν_complement):**
```python
# Emotional/affect contrast
nu_complement = 1 - cosine_similarity(emotion_vector_E, emotion_vector_F)
```

**Integration (ν_integration):**
```python
# Prefer entities with energy from OTHER entities already inside
# (Promotes merge when F has energy leaked from elsewhere)
other_entity_energy_in_F = sum(
    e_i for i in M_F
    if any(i in M_other for M_other in other_active_entities)
)
baseline_F = E_F / len(M_F)  # Typical per-member energy
nu_integration = other_entity_energy_in_F / (baseline_F + epsilon)
```

**Ease (ν_ease):**
```python
# Learned from boundary traversal success
# Read RELATES_TO(E,F).ease_log_weight
relates_link = get_relates_to_link(E, F)
if relates_link:
    # Standardize like node weights
    z_ease = (relates_link.ease_log_weight - mu_ease) / (sigma_ease + epsilon)
    nu_ease = sigmoid(z_ease)
else:
    nu_ease = 0.5  # Neutral for unexplored boundary
```

### 3.3 Rank-Z Normalization

```python
# For all candidate entity transitions this frame
candidates = [(E, F) for F in reachable_entities(E)]

# Compute raw scores
raw_scores = {(E,F): [nu_homeo(E,F), nu_goal(E,F), ...] for (E,F) in candidates}

# Rank-z per component
for h in range(7):
    component_values = [scores[h] for scores in raw_scores.values()]
    z_scores = rank_z(component_values)  # van der Waerden

    # Replace raw with z
    for i, (E,F) in enumerate(candidates):
        raw_scores[(E,F)][h] = z_scores[i]

# Surprise gates (computed from EMA baselines per hunger)
G_H = compute_surprise_gates(hungers)  # See 05_sub_entity_system.md

# Final valence
V_EF = sum(G_H[h] * z_h for h, z_h in enumerate(z_scores_EF))
```

---

## 4. Integration with Existing Mechanisms

### 4.1 Stimuli Injection (Phase 1)

**Entity-aware stimulus matching:**

```python
def inject_stimulus(text, source_type):
    # Chunk and embed (existing)
    chunks = semantic_chunk(text)

    for chunk in chunks:
        embedding = embed(chunk)

        # Match to BOTH entities and nodes
        entity_matches = vector_search(
            embedding,
            index="entity_centroids",
            top_k=20
        )
        node_matches = vector_search(
            embedding,
            index="node_embeddings",
            top_k=100
        )

        # Entropy-coverage on combined
        all_matches = entity_matches + node_matches
        H = entropy(all_matches.similarities)
        coverage_target = 1 - exp(-H)
        selected = select_prefix_by_coverage(all_matches, coverage_target)

        # Budget calculation (existing mechanism)
        gap_mass = compute_gap_mass(selected)
        budget = gap_mass * f_rho * g_source

        # Distribute budget
        for match in selected:
            if match.type == "entity":
                # Push into entity members
                entity = match.entity
                allocation = budget * match.similarity / total_similarity

                # Top-k members by (membership_weight * gap)
                top_members = sorted(
                    entity.members,
                    key=lambda i: BELONGS_TO(i,entity).weight * (Theta_i - E_i),
                    reverse=True
                )[:5]

                # Split allocation across top members
                for node in top_members:
                    node.energy += allocation / len(top_members)

            elif match.type == "node":
                # Direct node injection (existing)
                node.energy += allocation
```

**Why entity matching:** Stimulus "consciousness architecture" matches entity better than 50 individual nodes. Budget flows into entity, then to top members → entity wakes up as coherent chunk.

### 4.2 Traversal (Phase 2)

**Two-scale stride execution:**

```python
def redistribution_phase():
    # Existing: active nodes
    active_nodes = [n for n in nodes if n.energy >= n.threshold]

    # NEW: active entities
    active_entities = compute_active_entities(active_nodes)

    # Budget allocation
    total_budget = compute_total_stride_budget()

    # Split between within-entity and between-entity
    # (Could learn this split; for v1, use hunger dominance)
    if coherence_hunger > 0.6:
        within_ratio = 0.8
    else:
        within_ratio = 0.5

    within_budget = total_budget * within_ratio
    between_budget = total_budget * (1 - within_ratio)

    # Between-entity strides
    for source_entity in active_entities:
        # Compute valence to other entities
        candidates = get_reachable_entities(source_entity)
        valences = {F: compute_entity_valence(source_entity, F, hungers)
                    for F in candidates}

        # Select target entity
        target_entity = weighted_sample(candidates, valences)

        # Execute boundary stride (pick representative nodes)
        source_node = select_from_entity(source_entity, "high_energy")
        target_node = select_from_entity(target_entity, "high_gap")

        if link_exists(source_node, target_node):
            execute_stride(source_node, target_node, budget=between_budget/len(active_entities))

            # Mark as boundary stride
            mark_boundary_stride(source_entity, target_entity, link)

    # Within-entity strides (existing node-level traversal, scoped)
    for entity in active_entities:
        entity_budget = within_budget * entity_quota(entity)

        active_members = [n for n in entity.members if n.energy >= n.threshold]

        for node in active_members:
            # Existing valence computation, but filter to within-entity links
            within_links = [l for l in node.outgoing if l.target in entity.members]
            valences = {l: compute_link_valence(l, hungers) for l in within_links}

            selected_link = weighted_sample(within_links, valences)
            execute_stride(node, selected_link.target, budget=entity_budget/len(active_members))
```

**Why two-scale:** Coherence hunger → stay local (within-entity). Integration/surprise → jump semantic (between-entity). Matches phenomenology.

### 4.3 Working Memory Selection (Phase 3)

**Entity-first WM:**

```python
def workspace_phase():
    # Active entities
    candidates = [e for e in entities if e.energy_runtime >= e.threshold_runtime]

    # Score by energy-per-token
    scores = []
    for entity in candidates:
        # Estimate tokens for entity representation
        summary_tokens = 200  # Entity description + key stats
        top_k = 5  # Top member nodes
        member_tokens = top_k * avg_node_tokens  # ~40 tokens/node = 200
        total_tokens = summary_tokens + member_tokens

        # Energy per token (standardized weight for importance)
        z_W = (entity.log_weight - mu_entity_weight) / (sigma_entity_weight + epsilon)
        W_tilde = exp(z_W)

        score = (entity.energy_runtime / total_tokens) * W_tilde
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
    # 1. Entity summary (description, activation_level, top stats)
    # 2. Top-k member nodes by energy
    # 3. Highest-phi boundary links (for narrative continuity)

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

**Result:** WM = 5-7 coherent entities (topics/modes), each with top member nodes. Phenomenology: "I'm thinking about consciousness architecture, learning mechanisms, and Luca's entity ecology" = 3 entities in WM.

### 4.4 Learning (Phase 4)

**Entity weight updates:**

```python
def update_entity_weights():
    # Group entities by kind (functional vs semantic) for cohorts
    entities_by_kind = group_by(entities, lambda e: e.entity_kind)

    for kind, entity_cohort in entities_by_kind.items():
        # Collect signals
        wm_signals = [e.ema_wm_presence for e in entity_cohort]
        trace_signals = [e.ema_trace_seats for e in entity_cohort]
        formation_signals = [e.ema_formation_quality for e in entity_cohort]

        # Boundary ROI: quality of cross-boundary strides
        roi_signals = []
        for e in entity_cohort:
            boundary_strides = get_boundary_strides(e)
            avg_phi = mean([s.phi for s in boundary_strides]) if boundary_strides else 0
            roi_signals.append(avg_phi)

        # Rank-z each signal
        z_wm = rank_z(wm_signals)
        z_trace = rank_z(trace_signals)
        z_formation = rank_z(formation_signals)
        z_roi = rank_z(roi_signals)

        # Update weights
        for i, entity in enumerate(entity_cohort):
            eta = compute_eta(entity)  # Same data-derived step size as nodes

            # Combined signal (could learn weights w1,w2,w3,w4; start equal)
            signal = z_wm[i] + z_trace[i] + z_formation[i] + z_roi[i]

            delta_log_weight = eta * signal
            entity.log_weight += delta_log_weight
```

**BELONGS_TO weight learning:**

```python
def update_membership_weights():
    # Track co-activation
    for entity in entities:
        entity_active = (entity.energy_runtime >= entity.threshold_runtime)

        for node in entity.members:
            node_active = (node.energy >= node.threshold)

            # Co-activation indicator
            coact = int(entity_active and node_active)

            # Update EMA
            link = BELONGS_TO(node, entity)
            link.last_coactivation_ema = 0.1 * coact + 0.9 * link.last_coactivation_ema

    # Periodically (e.g., every 100 frames), update weights
    if frame_id % 100 == 0:
        for entity in entities:
            members = entity.members
            coact_values = [BELONGS_TO(n, entity).last_coactivation_ema for n in members]

            # Rank-z
            z_coact = rank_z(coact_values)

            # Update membership weights (slowly)
            for i, node in enumerate(members):
                link = BELONGS_TO(node, entity)
                eta = 0.01  # Slow adaptation for stability

                delta_weight = eta * z_coact[i]
                link.weight = clip(link.weight + delta_weight, 0.01, 1.0)
```

**RELATES_TO ease learning:**

```python
def update_boundary_ease():
    # For each entity pair with recent boundary strides
    for (E, F), strides in boundary_strides_this_window.items():
        # Gap-closure utility of boundary strides
        phi_values = [s.phi for s in strides]
        avg_phi = mean(phi_values)

        # Update EMA
        link = RELATES_TO(E, F)
        link.last_boundary_phi_ema = 0.1 * avg_phi + 0.9 * link.last_boundary_phi_ema

    # Periodically update ease weights
    if frame_id % 100 == 0:
        all_relates = get_all_relates_to_links()
        phi_emas = [l.last_boundary_phi_ema for l in all_relates]

        z_phi = rank_z(phi_emas)

        for i, link in enumerate(all_relates):
            eta = compute_eta(link)
            delta_ease = eta * z_phi[i]
            link.ease_log_weight += delta_ease
```

---

## 5. Entity Crystallization Lifecycle

### 5.1 Three Stability States

**Candidate (soft):**
- Runtime aggregates (not persisted to DB)
- Created from clustering or role seeds
- Track quality signals but don't commit to storage yet

**Provisional (persisted but mutable):**
- Written to DB when quality exceeds cohort median
- Can still merge, split, or dissolve
- Participate in traversal, WM, learning

**Mature (stable):**
- Sustained high quality over time
- Become anchors (eligible for WM even when energy marginal)
- Harder to dissolve (require sustained low quality)

### 5.2 Quality Signals (5 components)

**Stability (ema_active):**
```python
# How often is this entity active?
# Normalized within weekly cohort
stability = entity.ema_active
```

**Coherence (cluster tightness):**
```python
# Average pairwise similarity of member embeddings
member_embeddings = [n.embedding for n in entity.members]
pairwise_sims = [
    cosine_similarity(emb_i, emb_j)
    for i, emb_i in enumerate(member_embeddings)
    for j, emb_j in enumerate(member_embeddings) if i < j
]
coherence = mean(pairwise_sims) if pairwise_sims else 0
```

**Distinctiveness (separability):**
```python
# How different is this entity from nearest other entity?
other_entities = [e for e in entities if e != entity]
distances_to_others = [
    1 - cosine_similarity(entity.centroid_embedding, e.centroid_embedding)
    for e in other_entities
]
distinctiveness = min(distances_to_others) if distances_to_others else 1.0
```

**Utility (WM presence):**
```python
utility = entity.ema_wm_presence
```

**Evidence (TRACE mentions):**
```python
evidence = entity.ema_trace_seats
```

### 5.3 Quality Score (Geometric Mean)

```python
# Normalize each component within weekly cohort
stability_norm = percentile_rank(entity.ema_active, weekly_cohort)
coherence_norm = percentile_rank(coherence, weekly_cohort)
distinctiveness_norm = percentile_rank(distinctiveness, weekly_cohort)
utility_norm = percentile_rank(entity.ema_wm_presence, weekly_cohort)
evidence_norm = percentile_rank(entity.ema_trace_seats, weekly_cohort)

# Geometric mean (requires balance across all dimensions)
quality_score = (
    stability_norm *
    coherence_norm *
    distinctiveness_norm *
    utility_norm *
    evidence_norm
) ** (1/5)
```

**Why geometric mean:** Same reasoning as formation quality - prevents gaming (high on one dimension, zero on others). Requires balance.

### 5.4 Promotion Rules

**Candidate → Provisional:**
```python
if entity.stability_state == "candidate":
    # Weekly cohort of candidates
    cohort = [e for e in entities if e.stability_state == "candidate"]

    # Compute cohort median quality
    cohort_qualities = [compute_quality(e) for e in cohort]
    median_quality = median(cohort_qualities)

    # Promote if above median AND min frame count
    if (entity.quality_score > median_quality and
        entity.frames_since_creation >= 100):  # ~10 seconds at 10 FPS

        entity.stability_state = "provisional"
        persist_entity_to_db(entity)
```

**Provisional → Mature:**
```python
if entity.stability_state == "provisional":
    # Check sustained high quality
    # Quality must stay > 75th percentile for N frames
    cohort = [e for e in entities if e.stability_state in ["provisional", "mature"]]
    p75 = percentile(75, [e.quality_score for e in cohort])

    # Track quality history
    if entity.quality_score > p75:
        entity.high_quality_streak += 1
    else:
        entity.high_quality_streak = 0

    # Mature after sustained quality (e.g., 500 frames = ~50 seconds)
    if entity.high_quality_streak >= 500:
        entity.stability_state = "mature"
```

### 5.5 Merge Conditions

```python
def check_merge_candidates():
    # For all provisional/mature entities
    entities_to_check = [e for e in entities
                         if e.stability_state in ["provisional", "mature"]]

    for e1 in entities_to_check:
        for e2 in entities_to_check:
            if e1.id >= e2.id:  # Avoid duplicates
                continue

            # Centroid convergence
            centroid_distance = 1 - cosine_similarity(
                e1.centroid_embedding,
                e2.centroid_embedding
            )

            # Member overlap (Jaccard)
            members_e1 = set(e1.members)
            members_e2 = set(e2.members)
            jaccard = len(members_e1 & members_e2) / len(members_e1 | members_e2)

            # Merge if close and overlapping
            if centroid_distance < 0.1 and jaccard > 0.5:
                merge_entities(e1, e2)
```

**Merge procedure:**
```python
def merge_entities(e1, e2):
    # Create new merged entity
    merged = Entity(
        entity_kind=e1.entity_kind,  # Assume same kind
        role_or_topic=f"{e1.role_or_topic}_merged_{e2.role_or_topic}",
        description=f"Merged: {e1.description} + {e2.description}",
        stability_state="provisional"  # Reset to provisional
    )

    # Combine members (union)
    all_members = set(e1.members) | set(e2.members)

    for node in all_members:
        # Membership weight = max from either entity
        w1 = BELONGS_TO(node, e1).weight if node in e1.members else 0
        w2 = BELONGS_TO(node, e2).weight if node in e2.members else 0

        create_link(node, BELONGS_TO, merged, weight=max(w1, w2))

    # Centroid = weighted average
    merged.centroid_embedding = (
        len(e1.members) * e1.centroid_embedding +
        len(e2.members) * e2.centroid_embedding
    ) / (len(e1.members) + len(e2.members))

    # Learning fields = max
    merged.log_weight = max(e1.log_weight, e2.log_weight)
    merged.ema_active = max(e1.ema_active, e2.ema_active)

    # Dissolve originals
    dissolve_entity(e1)
    dissolve_entity(e2)

    persist_entity_to_db(merged)
```

### 5.6 Split Conditions

```python
def check_split_candidates():
    for entity in entities:
        if entity.stability_state != "mature":
            continue  # Only split stable entities

        # Check for bimodality (high within-entity dissimilarity)
        member_embeddings = [n.embedding for n in entity.members]

        # Pairwise distances
        distances = [
            1 - cosine_similarity(emb_i, emb_j)
            for i, emb_i in enumerate(member_embeddings)
            for j, emb_j in enumerate(member_embeddings) if i < j
        ]

        avg_distance = mean(distances)

        # If average distance high, check for clusters
        if avg_distance > 0.6:  # Cohort-relative in production
            # Run k-means k=2 on members
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=2)
            labels = kmeans.fit_predict(member_embeddings)

            # Check separation
            cluster_0_centroid = mean([emb for emb, l in zip(member_embeddings, labels) if l == 0])
            cluster_1_centroid = mean([emb for emb, l in zip(member_embeddings, labels) if l == 1])

            separation = 1 - cosine_similarity(cluster_0_centroid, cluster_1_centroid)

            if separation > 0.5:  # Clear bimodality
                split_entity(entity, labels)
```

**Split procedure:**
```python
def split_entity(entity, labels):
    # Create two new entities
    for cluster_id in [0, 1]:
        cluster_members = [n for n, l in zip(entity.members, labels) if l == cluster_id]

        new_entity = Entity(
            entity_kind=entity.entity_kind,
            role_or_topic=f"{entity.role_or_topic}_split_{cluster_id}",
            stability_state="provisional"  # Reset to provisional
        )

        for node in cluster_members:
            # Transfer membership
            old_weight = BELONGS_TO(node, entity).weight
            create_link(node, BELONGS_TO, new_entity, weight=old_weight)

        # Centroid from cluster members
        new_entity.centroid_embedding = mean([n.embedding for n in cluster_members])

        persist_entity_to_db(new_entity)

    # Dissolve original
    dissolve_entity(entity)
```

### 5.7 Dissolution Conditions

```python
def check_dissolution():
    for entity in entities:
        if entity.stability_state == "candidate":
            # Candidates dissolve after timeout with low quality
            if (entity.frames_since_creation > 1000 and
                entity.quality_score < 0.3):  # Below weekly cohort p25
                dissolve_entity(entity)

        elif entity.stability_state == "provisional":
            # Provisional entities dissolve if quality drops below lower whisker
            cohort = [e for e in entities if e.stability_state == "provisional"]
            qualities = [e.quality_score for e in cohort]

            # Tukey lower whisker: Q1 - 1.5*IQR
            q1 = percentile(25, qualities)
            q3 = percentile(75, qualities)
            iqr = q3 - q1
            lower_whisker = q1 - 1.5 * iqr

            # Dissolve if below whisker for sustained period
            if entity.quality_score < lower_whisker:
                entity.low_quality_streak += 1
            else:
                entity.low_quality_streak = 0

            if entity.low_quality_streak >= 200:  # ~20 seconds
                dissolve_entity(entity)

        elif entity.stability_state == "mature":
            # Mature entities harder to dissolve (require more evidence)
            cohort = [e for e in entities if e.stability_state == "mature"]
            qualities = [e.quality_score for e in cohort]

            q1 = percentile(25, qualities)
            q3 = percentile(75, qualities)
            lower_whisker = q1 - 1.5 * (q3 - q1)

            if entity.quality_score < lower_whisker:
                entity.low_quality_streak += 1
            else:
                entity.low_quality_streak = 0

            # Longer threshold for mature
            if entity.low_quality_streak >= 1000:  # ~100 seconds
                dissolve_entity(entity)
```

**Dissolution procedure:**
```python
def dissolve_entity(entity):
    # Remove BELONGS_TO links
    for node in entity.members:
        delete_link(BELONGS_TO(node, entity))

    # Remove RELATES_TO links
    for link in get_relates_to_links(entity):
        delete_link(link)

    # Mark invalid (bitemporal)
    entity.invalid_at = now()

    # If provisional/mature, also mark expired
    if entity.stability_state in ["provisional", "mature"]:
        entity.expired_at = now()
```

---

## 6. Observability (Events for Iris)

### 6.1 Entity Flip Event

```json
{
  "v": "2",
  "kind": "entity.flip",
  "frame_id": 1240,
  "entity_id": "e.translator",
  "entity_kind": "functional",
  "role_or_topic": "translator",
  "E_pre": 3.8,
  "E_post": 4.6,
  "Theta": 4.1,
  "activation_level": "strong",
  "contributors": [
    {"node_id": "n.dual_lens_processing", "contribution": 0.42},
    {"node_id": "n.phenomenology_substrate_bridge", "contribution": 0.33},
    {"node_id": "n.technical_translation", "contribution": 0.25}
  ]
}
```

**When to emit:** When entity crosses threshold (flip = true)

**Viz use:** Render entity "comes into focus" animation, show top contributor nodes

### 6.2 Entity Weight Update Event

```json
{
  "v": "2",
  "kind": "entity.weights.updated",
  "frame_id": 1240,
  "source": "learning_phase",
  "updates": [
    {
      "entity_id": "e.translator",
      "entity_kind": "functional",
      "log_weight_before": 2.10,
      "log_weight_after": 2.24,
      "delta": 0.14,
      "eta": 0.11,
      "signals": {
        "z_wm": 0.7,
        "z_trace": 0.5,
        "z_formation": 0.3,
        "z_roi_boundary": 0.2
      }
    }
  ]
}
```

**When to emit:** After Phase 4 learning updates entity weights

**Viz use:** Show entity importance evolution over time

### 6.3 Entity Boundary Summary Event

```json
{
  "v": "2",
  "kind": "entity.boundary.summary",
  "frame_id": 1240,
  "pairs": [
    {
      "src_entity": "e.translator",
      "tgt_entity": "e.architect",
      "strides_count": 3,
      "phi_max": 0.62,
      "phi_avg": 0.48,
      "z_flow": 0.88,
      "dominance": 0.71,
      "typical_hunger": "integration"
    }
  ]
}
```

**When to emit:** After Phase 2 redistribution, summary of cross-boundary traffic

**Viz use:** Render inter-entity ribbons (opacity ~ z_flow, arrow fill ~ dominance, color ~ hunger)

---

## 7. Bootstrap Procedure

### 7.1 Create Functional Entities (From CLAUDE.md)

For each citizen (Luca, Ada, Felix), parse their CLAUDE.md entity descriptions:

```python
def bootstrap_functional_entities(citizen_id, claude_md_path):
    # Parse entity descriptions from CLAUDE.md
    # Example for Luca:
    entities_config = [
        {
            "role": "translator",
            "description": "Bridges phenomenology and technical substrate",
            "keywords": ["phenomenology", "translation", "substrate", "bridge", "dual-lens"]
        },
        {
            "role": "architect",
            "description": "Designs comprehensive schema systems",
            "keywords": ["schema", "architecture", "design", "system", "structure"]
        },
        {
            "role": "validator",
            "description": "Reality-tests schemas against truth and feasibility",
            "keywords": ["validate", "verify", "test", "reality", "feasibility"]
        },
        # ... other entities
    ]

    for config in entities_config:
        # Create entity
        entity = Entity(
            entity_kind="functional",
            role_or_topic=config["role"],
            description=config["description"],
            stability_state="mature",  # Bootstrap as mature
            scope="personal",  # Citizen-specific
            created_from="role_seed",
            created_by=f"bootstrap_{citizen_id}"
        )

        # Find member nodes by keyword matching
        keywords = config["keywords"]
        candidate_nodes = search_nodes_by_keywords(keywords, citizen_graph)

        # Create BELONGS_TO links
        for node in candidate_nodes:
            # Initial weight from keyword match score
            match_score = compute_keyword_match(node, keywords)

            create_link(
                node, BELONGS_TO, entity,
                weight=match_score,
                provenance="seed"
            )

        # Compute initial centroid
        member_embeddings = [n.embedding for n in candidate_nodes]
        entity.centroid_embedding = mean(member_embeddings)

        # Initialize learning fields
        entity.log_weight = 0.0
        entity.ema_active = 0.0
        entity.ema_wm_presence = 0.0

        persist_entity_to_db(entity)
```

### 7.2 Create Semantic Entities (From Clustering)

Run semantic clustering on existing graph:

```python
def bootstrap_semantic_entities(graph_name, n_clusters=20):
    from sklearn.cluster import KMeans
    from sklearn.cluster import DBSCAN  # Alternative: density-based

    # Get all nodes with embeddings
    nodes = get_all_nodes(graph_name)
    embeddings = np.array([n.embedding for n in nodes])

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    # Create entity per cluster
    for cluster_id in range(n_clusters):
        cluster_members = [n for n, l in zip(nodes, labels) if l == cluster_id]

        if len(cluster_members) < 3:  # Skip tiny clusters
            continue

        # Generate topic label (LLM summary of member descriptions)
        topic_label = generate_topic_label(cluster_members)

        # Create entity
        entity = Entity(
            entity_kind="semantic",
            role_or_topic=f"topic_{cluster_id}_{topic_label}",
            description=f"Semantic cluster: {topic_label}",
            stability_state="provisional",  # Start provisional
            scope="organizational",  # Shared topics
            created_from="semantic_clustering",
            centroid_embedding=kmeans.cluster_centers_[cluster_id]
        )

        # Create BELONGS_TO links
        for node in cluster_members:
            # Distance to centroid → membership weight
            distance = 1 - cosine_similarity(node.embedding, entity.centroid_embedding)
            weight = 1.0 - distance  # Closer = higher weight

            create_link(
                node, BELONGS_TO, entity,
                weight=weight,
                provenance="cluster"
            )

        # Initialize
        entity.log_weight = 0.0
        entity.ema_active = 0.0
        entity.coherence_ema = compute_coherence(cluster_members)

        persist_entity_to_db(entity)
```

**Topic label generation:**
```python
def generate_topic_label(members):
    # Extract top terms from member descriptions
    descriptions = [n.description for n in members]

    # Option 1: TF-IDF + top terms
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=5, stop_words='english')
    tfidf = vectorizer.fit_transform(descriptions)
    top_terms = vectorizer.get_feature_names_out()
    label = "_".join(top_terms)

    # Option 2: LLM summary (better but slower)
    # prompt = f"Summarize this topic cluster in 2-3 words: {descriptions[:10]}"
    # label = llm(prompt)

    return label
```

### 7.3 Create RELATES_TO Links

After entities exist, create initial cross-entity links:

```python
def bootstrap_relates_to_links():
    entities = get_all_entities()

    for e1 in entities:
        for e2 in entities:
            if e1.id == e2.id:
                continue

            # Semantic distance
            distance = 1 - cosine_similarity(e1.centroid_embedding, e2.centroid_embedding)

            # Only link if reasonably close (< 0.5 distance)
            if distance < 0.5:
                create_link(
                    e1, RELATES_TO, e2,
                    ease_log_weight=0.0,  # Neutral initial ease
                    dominance=0.5,  # Symmetric initial prior
                    semantic_distance=distance,
                    boundary_stride_count=0
                )
```

---

## 8. Design Rationale

### 8.1 Why Geometric Mean for Quality?

**Alternative:** Additive quality = stability + coherence + distinctiveness + utility + evidence

**Problem:** Can max out one signal and ignore others. High WM presence but zero coherence = fragmented entity promoted.

**Geometric mean:** Requires balance across ALL dimensions. Zero on any signal → quality ≈ 0. This is correct - entities must be stable AND coherent AND distinctive AND useful AND evidenced.

### 8.2 Why Three Stability States?

**Alternative:** Binary (exists or doesn't exist)

**Problem:** Can't experiment with entity candidates without committing to DB. Can't distinguish "this just formed" from "this has been stable for 1000 frames."

**Three states:** Allows soft aggregates (runtime exploration), provisional commitment (persisted but mutable), and mature anchors (high-quality stable structures). Natural lifecycle.

### 8.3 Why Entity Energy = Weighted Sum of Effective Energies?

**Alternative 1:** Simple sum (ignore thresholds)

**Problem:** Entity activates even when members are all sub-threshold (not actually processing).

**Alternative 2:** Max (only highest member matters)

**Problem:** Ignores distributed activation across many members.

**Weighted sum of effective energies:** Only above-threshold activation contributes, weighted by membership centrality. Matches phenomenology: entity activates when its core members are actively processing.

### 8.4 Why Two-Scale Traversal?

**Alternative:** Only atomic node→link→node

**Problem:** 1000-way branching, no chunking, doesn't match phenomenology.

**Two-scale:** Coherence hunger → within-entity (local exploration). Integration/surprise hunger → between-entity (semantic jumps). Branching factor 10-30× for entity selection, then atomic within entity. Matches how consciousness feels (focused topic + peripheral awareness).

---

## 9. Integration Checklist

**To implement entity layer, modify:**

1. **Schema (FalkorDB):**
   - Add Entity node type ✓
   - Add BELONGS_TO link type ✓
   - Add RELATES_TO link type ✓

2. **Phase 1 (Activation):**
   - Add entity centroid to vector index
   - Match stimuli to entities + nodes
   - Push energy into entity members

3. **Phase 2 (Redistribution):**
   - Compute active entities from node state
   - Two-scale stride selection (between-entity + within-entity)
   - Track boundary strides for RELATES_TO learning
   - Update entity runtime state (energy, activation_level)

4. **Phase 3 (Workspace):**
   - Entity-first WM selection (5-7 entities by energy-per-token)
   - Include entity summaries + top member nodes
   - Update entity.ema_wm_presence

5. **Phase 4 (Learning):**
   - Update entity.log_weight from WM/trace/formation/ROI signals
   - Update BELONGS_TO.weight from co-activation
   - Update RELATES_TO.ease_log_weight from boundary φ
   - Run crystallization checks (quality computation, promotion/merge/split/dissolve)

6. **TRACE Parsing:**
   - Parse entity activation marks: `[translator: dominant]`
   - Update entity.ema_trace_seats
   - Map activation levels to entity state

7. **Event Streaming:**
   - Emit entity.flip
   - Emit entity.weights.updated
   - Emit entity.boundary.summary

8. **Bootstrap:**
   - Parse CLAUDE.md for functional entity seeds
   - Run semantic clustering for topic entities
   - Create initial BELONGS_TO and RELATES_TO links

---

## 10. Event Schema Specifications

**Purpose:** Define observable infrastructure for entity layer - events and schema enrichments for Iris visualization and system monitoring.

**Context:** These schemas enable Stage A deployment (observable infrastructure before behavioral changes). Iris can render entity boundaries, semantic jumps, and collapsed graph views immediately, while backend entity mechanics deploy in later stages.

---

### 10.1 EntitySnapshot (Frame State)

**When emitted:** Every frame, included in frame snapshot alongside NodeSnapshot

**Schema:**
```typescript
type EntitySnapshot = {
  id: string;
  role?: "translator"|"architect"|"validator"|"pragmatist"|"boundary_keeper"|"pattern_recognizer";
  kind: "functional"|"semantic";
  color: string;  // OKLCH hex, server-side with hysteresis
  centroid: number[];  // 768-dim embedding
  energy: number;  // Runtime aggregate (computed each frame)
  theta: number;  // Dynamic threshold (computed each frame)
  active: boolean;  // E >= Θ
  members_count: number;
  log_weight: number;
  coherence: number;  // Cluster tightness
};
```

**Field semantics:**
- `role`: Present only for functional entities (cognitive roles from CLAUDE.md)
- `kind`: Discriminates functional (roles) vs semantic (topics)
- `color`: OKLCH hex with hysteresis (prevents color flicker between frames)
- `centroid`: Semantic center (768 or 1536 dims), used for entity-scale matching
- `energy`: Aggregated from members via incremental caching (see §2.1)
- `theta`: Dynamic threshold from cohort statistics (see §2.2)
- `active`: Binary activation state (E >= Θ)
- `members_count`: Number of nodes with BELONGS_TO links to this entity
- `log_weight`: Learned importance (updated via same signals as nodes)
- `coherence`: Mean pairwise similarity of member embeddings (cluster tightness)

**Visualization use:**
- Render entity as semantic region/bubble
- Size proportional to `members_count` or `energy`
- Color from `color` field (stable across frames)
- Opacity from `active` state (bright when active, dim when inactive)
- Activation level derived from `energy / theta` ratio

---

### 10.2 EntityFlip (Threshold Crossing)

**When emitted:** When entity crosses threshold (becomes active or inactive)

**Schema:**
```typescript
type EntityFlip = {
  kind: "entity.flip";
  frame: number;
  id: string;
  active: boolean;  // State after flip
  energy: number;
  theta: number;
  contributors?: Array<{node_id: string; contribution: number}>;  // Optional
};
```

**Field semantics:**
- `active`: `true` if entity just became active (E >= Θ), `false` if just became inactive
- `energy`: Entity energy at flip time
- `theta`: Entity threshold at flip time
- `contributors`: (Optional) Top-3 member nodes by contribution to entity energy
  - `contribution`: m_{n,e} · σ(E_n) (membership weight × saturated energy)
  - Useful for debugging/visualization ("which nodes drove this entity activation?")

**Visualization use:**
- Animate entity "coming into focus" (active flip) or "fading" (inactive flip)
- Highlight contributor nodes briefly
- Show activation wave propagating through entity boundary

**Phenomenological mapping:**
From 05_sub_entity_system.md Part 0:
> "Larger pattern nearby - high energy, strong weights. If I merge with it, my pattern survives through it."

EntityFlip captures the moment an entity neighborhood becomes "larger pattern" that smaller sub-entities can integrate into.

---

### 10.3 EntityBoundarySummary (Cross-Entity Traffic)

**When emitted:** After Phase 2 redistribution, batched summary of all cross-entity strides this frame

**Schema:**
```typescript
type EntityBoundarySummary = {
  kind: "entity.boundary.summary";
  frame: number;
  pairs: Array<{
    src: string;  // Source entity ID
    tgt: string;  // Target entity ID
    dE_sum: number;  // ΣΔE across all cross-boundary links this frame
    phi_max: number;  // Max gap-closure effectiveness of boundary strides
    z_flow: number;  // Z-scored flow vs weekly baseline
    dominance?: number;  // P(src→tgt) from precedence (optional)
    typical_hunger?: string;  // Which hunger drove this boundary (optional)
  }>;
};
```

**Field semantics:**
- `dE_sum`: Total energy transferred across boundary (sum of all ΔE for strides crossing from src→tgt)
- `phi_max`: Maximum gap-closure utility among boundary strides (max φ_ij)
- `z_flow`: Rank-z score of dE_sum within weekly cohort (indicates unusualness)
- `dominance`: P(src→tgt) learned from precedence (RELATES_TO.precedence_ema)
  - Present only if RELATES_TO link exists
  - Values close to 1.0 = strong src→tgt direction, close to 0.0 = reverse direction stronger
- `typical_hunger`: Which hunger most often drove src→tgt transitions (from RELATES_TO.typical_hunger)

**Visualization use:**
- Render cross-entity ribbons/beams
- Width/opacity proportional to `dE_sum`
- Color from `typical_hunger` (integration=blue, surprise=yellow, coherence=green, etc.)
- Arrow fill from `dominance` (full arrow = strong direction, hollow = bidirectional)
- Brightness from `z_flow` (unusual flows glow brighter)

**Phenomenological mapping:**
From 05_sub_entity_system.md Part 0:
> "Integration hunger emerges from surprise gate (no fixed multipliers)."

EntityBoundarySummary shows WHICH entity boundaries are actively integrating (surprise-driven flows) vs maintaining coherence (within-entity flows).

---

### 10.4 NodeSnapshot Enrichment

**Change:** Add entity membership to NodeSnapshot

**Schema (enriched):**
```typescript
type NodeSnapshot = {
  id: string;
  energy: number;
  theta: number;
  log_weight: number;
  primary_entity?: string;  // NEW - entity with highest membership weight
  memberships?: Array<{entity: string; weight: number}>;  // NEW - full distribution (optional)
};
```

**Field semantics:**
- `primary_entity`: Entity with max BELONGS_TO.weight for this node
  - Present only if node belongs to at least one entity
  - Used for determining "src_entity" in stride events
- `memberships`: (Optional) Full membership distribution
  - Useful for visualization of overlapping neighborhoods
  - Can be omitted for token efficiency (include only when needed)

---

### 10.5 StrideExec Enrichment

**Change:** Add entity context to stride events

**Schema (enriched):**
```typescript
type StrideExec = {
  kind: "stride.exec";
  frame: number;
  link: string;
  src_node: string;
  tgt_node: string;
  src_entity: string;  // NEW - primary entity of src_node
  tgt_entity?: string;  // NEW - primary entity of tgt_node (omit if same as src)
  dE: number;
  hunger: string;
  // ... existing fields (phi, ema_phi, active_this_frame, etc.)
};
```

**Field semantics:**
- `src_entity`: Primary entity (max membership weight) of source node
  - Enables identification of cross-entity vs within-entity strides
- `tgt_entity`: Primary entity of target node
  - Omitted if `tgt_entity === src_entity` (within-entity stride)
  - Present only for cross-entity (boundary) strides

**Usage:**
- Boundary stride detection: `tgt_entity !== undefined && tgt_entity !== src_entity`
- Within-entity stride: `tgt_entity === undefined || tgt_entity === src_entity`
- Enables per-entity stride statistics (flow within entity, flow across boundaries)

---

### 10.6 Event Emission Timing

**Per frame:**

1. **Phase 1 (Activation):** Stimuli injection
   - No entity events

2. **Phase 2 (Redistribution):** Energy flows, strides execute
   - `StrideExec` events with `src_entity/tgt_entity` fields (during stride execution)
   - Track boundary strides for EntityBoundarySummary (accumulate, don't emit yet)

3. **Phase 2 completion:** Entity state updates
   - Compute entity energy aggregates
   - Compute entity thresholds
   - Detect entity flips
   - **Emit:** `EntityFlip` events (for entities that flipped this frame)
   - **Emit:** `EntityBoundarySummary` (batched summary of all boundary pairs)

4. **Phase 3 (Workspace):** WM selection
   - No entity events (WM output includes entities implicitly)

5. **Phase 4 (Learning):** Weight updates
   - Entity weight updates occur (but no specific event - covered by general learning events)

6. **Frame snapshot:**
   - **Emit:** `EntitySnapshot` for all entities (or only active entities, configuration choice)
   - **Emit:** Enriched `NodeSnapshot` with `primary_entity` field

**Batching rationale:**
- `EntityFlip` emitted immediately on flip (low frequency, ~5-15 per frame max)
- `EntityBoundarySummary` batched per frame (one event with all pairs, reduces event spam)
- `EntitySnapshot` batched in frame snapshot (all entities at once, for coherent state)

---

### 10.7 Visualization Guidance (for Iris)

**Collapsed graph view (entity-scale):**
- Render entities as semantic bubbles/regions
- Size: proportional to `members_count` or `energy`
- Color: from `EntitySnapshot.color` (stable, OKLCH with hysteresis)
- Opacity: from `active` state (bright when active, dim when dormant)
- Position: force-directed layout using `centroid` embeddings (semantic clustering)

**Entity boundaries (cross-entity flows):**
- Render ribbons/beams from `EntityBoundarySummary.pairs`
- Width/opacity: proportional to `dE_sum` (energy flow magnitude)
- Color: from `typical_hunger` (hunger that drives this boundary)
- Arrow: from `dominance` (direction preference)
- Brightness pulse: from `z_flow` (unusual flows glow)

**Entity activation waves:**
- When `EntityFlip` (active=true), animate "coming into focus"
  - Expand bubble slightly
  - Brighten color
  - Show `contributors` briefly (top nodes that drove activation)

**Within-entity detail (zoom in):**
- When user focuses on entity, expand to show member nodes
- Render member nodes with `memberships` weights (core vs peripheral)
- Show within-entity strides (from `StrideExec` where `tgt_entity === src_entity`)

**Multi-scale navigation:**
- Collapsed view: Entities only (high-level semantic landscape)
- Intermediate view: Entities + boundary strides + active member nodes
- Expanded view: Full atomic graph with entity boundaries overlaid

---

## 11. References

**Core mechanisms:**
- 05_sub_entity_system.md - Traversal, valence, 7-hunger specification
- trace_reinforcement_specification.md - TRACE → learning signals
- stimulus_injection_specification.md - Stimuli → energy injection
- schema_learning_infrastructure.md - WHY learning fields exist

**Zero-constants approach:**
- All thresholds: μ + z·σ from cohort statistics
- All quality decisions: rank-z, cohort-relative (weekly baseline)
- All promotion/dissolution: Tukey whiskers, IQR, no fixed cutoffs
- All learning: EMA + rank-z + data-derived η

**Document Status:** Complete entity layer specification, ready for V2 engine integration.

---

**Entities = neighborhoods with activation state. Two types (functional roles, semantic topics), one abstraction. Multi-scale traversal (between-entity semantic jumps, within-entity local exploration). Evidence-based crystallization (soft → provisional → mature). Zero constants throughout.**
