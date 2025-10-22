# Stimulus Injection Specification

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Complete specification of how stimuli inject activation energy into consciousness substrate

---

## Overview

**Critical principle:** Energy enters the system ONLY through stimuli (reality contact). TRACE adjusts weights, stimuli inject energy.

**Pipeline:**
```
Stimulus text → Chunk & embed → Entropy-coverage search → Budget calculation →
Entity channel selection → Direction-aware distribution → Energy injection (ΔE)
```

**Zero constants:** All scaling factors are data-derived (health modulation, source impact, direction priors).

---

## 1. Stimulus Processing

### 1.1 Input Sources

**Stimulus taxonomy** (extensible):

| Source Type | Description | Examples |
|------------|-------------|----------|
| `user_message` | Direct user input | Questions, commands, observations |
| `tool_result.error` | Tool execution errors | Stack traces, validation failures |
| `tool_result.success` | Tool execution success | File contents, search results, API responses |
| `doc_read` | Documentation loaded | Spec files, architecture docs |
| `doc_write` | Documentation created | New specs, generated docs |
| `code_change` | Code modifications detected | Git diffs, file edits |
| `test_failure` | Test execution failures | Pytest output, assertion errors |
| `system_timer` | Periodic ticks | Maintenance cycles, health checks |
| `log_event` | System log messages | Guardian logs, service status |
| `context_peripheral` | Peripheral awareness | S5/S6 context chunks |
| `org_event` | Organizational events | Meetings, decisions, announcements |

**Extension:** Add new types as needed. Each type learns independent impact gate g(source) from weekly flip yields.

**Why granular:** `tool_result.error` likely more valuable than `tool_result.success` - errors point to problems needing attention. Splitting allows learning this difference.

### 1.2 Semantic Chunking

**Purpose:** Break stimulus into semantically coherent units for targeted injection.

**Algorithm:**

```python
def semantic_chunk(text: str) -> List[Chunk]:
    # Preserve structural boundaries
    chunks = []

    # Code blocks (fenced or indented)
    code_blocks = extract_code_blocks(text)

    # Error blocks (stack traces, JSON errors)
    error_blocks = extract_error_patterns(text)

    # Remaining prose (semantic similarity-based)
    prose = remove_blocks(text, code_blocks + error_blocks)
    prose_chunks = sentence_window_chunking(
        prose,
        window_size=3,  # sentences
        overlap=1
    )

    return code_blocks + error_blocks + prose_chunks
```

**Why preserve structure:** Code blocks have different semantics than prose. Stack traces point to specific nodes. Chunking respects this.

### 1.3 Embedding

**Per chunk:**

```python
embedding = embed_model.encode(chunk.text)
```

**Model:** Same embedding model used for node/link semantic indices (consistency critical).

**Dimensionality:** Typically 768 or 1536 dimensions (model-dependent).

---

## 2. Entropy-Coverage Search

### 2.1 Purpose

Replace fixed top-K retrieval with **adaptive coverage** based on query specificity.

**Why:** Specific queries ("What is Hamilton apportionment?") should retrieve few highly relevant nodes. Broad queries ("Tell me about the architecture") should retrieve many diverse nodes.

### 2.2 Vector Search

**Per chunk embedding:**

```python
# Search node semantic index
node_matches = vector_index.search(
    embedding,
    top_k=100,  # Over-retrieve
    filters={"scope": relevant_scopes}
)

# Search link semantic index (optional, for link-based injection)
link_matches = vector_index.search(
    embedding,
    top_k=50,
    index="link_semantics"
)
```

**Result:** Similarity scores {s_1, s_2, ..., s_N} where s_i ∈ [0,1] (cosine similarity).

### 2.3 Entropy Calculation

Treat similarities as unnormalized probabilities:

```python
p_k = s_k / Σ_i s_i  # Normalize to probabilities

H = -Σ_k p_k · log(p_k)  # Shannon entropy
```

**Interpretation:**
- **Low entropy** (H→0): One dominant match, query is specific
- **High entropy** (H→log(N)): Many similar matches, query is broad

### 2.4 Coverage Target

```python
ĉ = 1 - exp(-H)
```

**Properties:**
- H=0 → ĉ=0 (one perfect match suffices)
- H=2 → ĉ≈0.86 (need 86% coverage)
- H=4 → ĉ≈0.98 (need 98% coverage, very broad)

**Why exponential:** Natural connection between entropy (information content) and coverage need.

### 2.5 Prefix Selection

```python
# Sort by similarity descending
sorted_matches = sort(matches, key=lambda m: m.similarity, reverse=True)

# Accumulate mass until coverage target reached
selected = []
cumulative_mass = 0.0

for match in sorted_matches:
    selected.append(match)
    cumulative_mass += match.similarity / Σ s_i

    if cumulative_mass >= ĉ:
        break

return selected  # Variable size, data-derived
```

**Result:** Anywhere from 1 match (specific query) to 50+ matches (broad query), no fixed K.

---

## 3. Budget Calculation

### 3.1 Core Formula

```python
B = gap_mass × f(ρ) × g(source)
```

where:
- **gap_mass:** Sum of threshold gaps weighted by match quality
- **f(ρ):** Health modulation based on spectral radius proxy
- **g(source):** Source-type impact gate

**No magic numbers.** All factors are data-derived or cohort-normalized.

### 3.2 Gap Mass

```python
gap_mass = Σ_{m ∈ selected} s_m · max(0, Θ_m - E_m)
```

where:
- s_m: similarity score of match m
- Θ_m: activation threshold of matched node
- E_m: current energy of matched node

**Interpretation:** Total "activation deficit" weighted by relevance. High gap × high similarity = urgent injection target.

### 3.3 Health Modulation f(ρ)

**Purpose:** Dampen injection when system is supercritical (too much activation), boost when subcritical (too little).

#### 3.3.1 Spectral Radius Proxy

Full spectral radius computation is O(N³), too expensive per frame. Use proxy:

```python
ρ_proxy = max_degree × avg_weight / N
```

where:
- max_degree: Maximum node degree (outgoing links)
- avg_weight: Average link weight (exp(log_weight))
- N: Active node count this frame

**Interpretation:** Rough upper bound on spectral radius. Cheap to compute.

#### 3.3.2 Frame Quality Signal

**Components per frame t:**

**1. Flip yield:**
```python
yield_t = num_flips_t / budget_spent_t
```
Normalized within rolling week via rank-to-[0,1].

**2. Activation entropy:**
```python
# Distribution of active nodes across types/communities
p_g = count_active(group_g) / total_active
H_t = -Σ_g p_g · log(p_g)

# Normalize to [0,1] via rolling week min/max
h_t = (H_t - H_min) / (H_max - H_min + ε)
```

**3. Overflow penalty:**
```python
# Fraction of frames hitting hard limits
overflow_t = count(overflow_frames) / window_size
o_t = 1 - overflow_t  # Convert to quality (low overflow = high quality)
```

**Composite quality (geometric mean):**
```python
quality_t = (ŷ_t · ĥ_t · ô_t)^(1/3)
```

where ŷ_t, ĥ_t, ô_t are the rank-normalized components.

**Why geometric mean:** Requires balance across all dimensions (yield AND entropy AND low overflow) - same reasoning as formation quality. Prevents systems that are productive but unstable or stable but dead.

#### 3.3.3 Isotonic Regression

**Training data:** Collect pairs (ρ_proxy_t, quality_t) over rolling horizon (e.g., last 1000 frames, ~2 hours at 10 FPS).

**Fit:** Learn monotone **non-increasing** mapping f such that f(ρ) predicts quality.

```python
from sklearn.isotonic import IsotonicRegression

iso_reg = IsotonicRegression(increasing=False)
iso_reg.fit(ρ_history, quality_history)

# At runtime
f_ρ = iso_reg.predict([ρ_current])[0]
```

**Interpretation:**
- High ρ (supercritical) → low predicted quality → f(ρ) < 1 → dampen budget
- Low ρ (subcritical) → high predicted quality → f(ρ) > 1 → boost budget

**Bootstrap:** Until N ≥ 200 frames, set f(ρ) = 1.0 (neutral).

**Why isotonic:** Preserves monotonicity without assuming parametric form (no sigmoid tuning).

### 3.4 Source Impact Gate g(source)

**Purpose:** Let reality sources earn or lose influence based on observed effectiveness.

#### 3.4.1 Per-Source Flip Yield

Track per source type over rolling window (e.g., 1 week):

```python
# For each source type
yield_source = total_flips_from_source / total_budget_from_source
```

#### 3.4.2 Rank Normalization

Within the cohort of all source types active this week:

```python
g(source) = normalize(yield_source via rank-z to [0.5, 1.5])
```

**Why [0.5, 1.5] range:** Prevents source types from being completely silenced (min 0.5× budget) while allowing effective sources to get 1.5× boost.

**Bootstrap:** Until sufficient data (e.g., 50 frames with this source), set g(source) = 1.0.

#### 3.4.3 Example

| Source | Flip Yield | Rank | g(source) |
|--------|-----------|------|-----------|
| user_message | 0.15 | 8/10 | 1.3 |
| error_trace | 0.22 | 10/10 | 1.5 |
| system_timer | 0.03 | 2/10 | 0.6 |
| log_event | 0.01 | 1/10 | 0.5 |

Error traces earn highest impact (most flips per budget), log events lowest.

### 3.5 Final Budget

```python
B = gap_mass × f(ρ) × g(source)
```

**Example:**
- gap_mass = 15.0 (three matched nodes with gaps 3, 5, 7)
- f(ρ) = 0.9 (slightly supercritical, dampen)
- g(source) = 1.3 (user messages effective)
- B = 15.0 × 0.9 × 1.3 ≈ 17.6 energy units to distribute

---

## 4. Entity Channel Selection

### 4.1 Purpose

Distribute injection across active entities (coalitions) based on semantic affinity + recent success.

**Why entities:** Different coalitions have different hungers. Architect entity vs Validator entity respond differently to same stimulus.

### 4.2 Entity Affinity

Per active entity e:

```python
# Entity has a learned embedding (centroid of nodes it's activated)
affinity_e = cosine_similarity(stimulus_embedding, entity_embedding_e)
```

### 4.3 Entity Recent Success

Track per entity over last N frames:

```python
success_e = (flips_by_e / total_flips) · (gap_closure_by_e / total_gap_closure)
```

Geometric mean of flip share and gap-closure share.

### 4.4 Entity Channel Mix

```python
# Combine affinity and success (both rank-normalized)
z_affinity_e = rank_z(affinity_e, cohort=active_entities)
z_success_e = rank_z(success_e, cohort=active_entities)

score_e = z_affinity_e + z_success_e

# Softmax to get proportions
π_e = exp(score_e) / Σ_{e'} exp(score_e')
```

**Result:** Entity proportions sum to 1.0. High-affinity + high-success entities get larger share of budget.

### 4.5 Per-Entity Injection

```python
B_e = π_e · B  # Budget for entity e's channel

# Within entity channel, distribute B_e across matched nodes
# according to entity-specific valence/priority
```

**Implementation note:** This may require entity-aware valence computation (future extension). For now, can use single unified injection and log entity attribution for learning.

---

## 5. Direction-Aware Distribution

### 5.1 Node-Matched Injection

For each selected node m with gap G_m = max(0, Θ_m - E_m):

```python
# Proportional to similarity × gap
weight_m = s_m · G_m

ΔE_m = B · weight_m / Σ_k weight_k

# Respect gap cap
ΔE_m = min(ΔE_m, G_m)
```

**Result:** Energy distributed proportionally, but no node exceeds its threshold gap.

### 5.2 Link-Matched Injection

When a **link semantic match** is selected (optional advanced feature):

**Problem:** Links don't have activation energy (only nodes do). How to inject?

**Solution:** Split injection between source and target nodes using **direction prior**.

#### 5.2.1 Direction Prior Learning

Per link type (e.g., ENABLES, BLOCKS):

**Precedence tracking** (see consciousness_learning_integration.md Phase 2 and schema_learning_infrastructure.md §2.7.4 for implementation):

```python
# During each stride i→j where j flips
u_ij = min(ΔE_ij, G_j^pre)  # Effective contribution
π_ij = u_ij / (Σ_k→j u_kj + ε)  # Precedence share

# Accumulate over time (link.precedence_forward field)
link.precedence_forward += π_ij
```

**Note:** The `precedence_forward` and `precedence_backward` fields are part of the link activation & payload trace infrastructure. They accumulate causal credit every time a link participates in a flip, creating a learned prior for direction dominance.

**Bayesian direction learning with Beta prior:**

Maintain Beta distribution parameters per link type:

```python
# Initialize with symmetric prior
alpha_forward = beta_prior  # e.g., 1.0
beta_forward = beta_prior    # e.g., 1.0

# Update with causal precedence evidence
# When stride i→j causes j to flip:
alpha_forward += π_ij  # Causal contribution weight
# When stride j→i causes i to flip:
beta_forward += π_ji

# Expected direction probability
E[p_forward] = alpha_forward / (alpha_forward + beta_forward)
```

**Split allocation:**

```python
# Use expected value from Beta distribution
p_source = E[p_forward]
p_target = 1 - p_source

ΔE_source = p_source · ΔE_link_match
ΔE_target = p_target · ΔE_link_match
```

**Bootstrap:** With symmetric prior (α=β=1), E[p_forward] = 0.5 initially. As evidence accumulates, distribution narrows around learned direction.

**Why Beta prior:** Naturally handles uncertainty - wide distribution early (uncertain → near 50/50), narrow distribution with evidence (confident → asymmetric split). Bayesian update is simple and numerically stable.

**Link to payload trace:** The direction learning uses `link.precedence_forward` and `link.precedence_backward` accumulators (see schema_learning_infrastructure.md §2.7.4). These fields are updated every frame during Phase 2 redistribution and read here during Phase 1 stimulus injection for link-matched energy splits.

#### 5.2.2 Example

Link type: `ENABLES` (scope: organizational)

Historical data shows:
- ratio_flip = 0.7 (source causes target flip 70% of the time)
- ratio_flow = 0.8 (80% of flow goes source→target)
- dominance = √(0.7 × 0.8) ≈ 0.75

Within cohort of ENABLES links, this is rank 8/10:
- z_dom = Φ^(-1)(8/11) ≈ 0.77

Split:
- p_source = σ(0.77) ≈ 0.68
- p_target = 0.32

**Interpretation:** For ENABLES links, source node gets 68% of injection (it's the enabler, should activate first).

For BLOCKS links, this might reverse (target gets more because it's the blocked node that needs energy to overcome).

---

## 6. Peripheral Amplification

### 6.1 Purpose

**Peripheral context** (S5/S6 layers from context continuity architecture) provides sustained background awareness. If stimulus aligns with peripheral chunks, amplify injection.

### 6.2 Alignment Check

```python
# Peripheral chunks have embeddings
peripheral_embeddings = [embed(chunk) for chunk in peripheral_context]

# Max alignment with stimulus
max_alignment = max([
    cosine_similarity(stimulus_embedding, p_emb)
    for p_emb in peripheral_embeddings
])
```

### 6.3 Amplification Factor

```python
# Z-score alignment within recent stimuli cohort
z_alignment = rank_z(max_alignment, cohort=recent_stimuli)

# Amplification (data-derived, no constant)
α = max(0, z_alignment)  # Only amplify if above-average alignment

# Apply to budget
B_amplified = B · (1 + α)
```

**Example:**
- z_alignment = 1.5 (very high peripheral alignment)
- α = 1.5
- B_amplified = B × 2.5 (2.5× budget because peripheral context strongly supports)

**Why:** Stimuli that echo peripheral awareness represent sustained relevance, deserve stronger injection.

---

## 7. Complete Injection Algorithm

### 7.1 Pipeline

```python
def inject_stimulus(
    text: str,
    source_type: str,
    peripheral_context: List[str]
) -> InjectionResult:

    # 1. Chunk and embed
    chunks = semantic_chunk(text)
    embeddings = [embed(chunk) for chunk in chunks]

    results = []
    for embedding in embeddings:
        # 2. Entropy-coverage search
        matches = vector_search(embedding, top_k=100)
        H = entropy(matches.similarities)
        ĉ = 1 - exp(-H)
        selected = select_prefix_by_coverage(matches, ĉ)

        # 3. Budget calculation
        gap_mass = sum(s_m · max(0, Θ_m - E_m) for m in selected)
        f_ρ = health_modulation(spectral_radius_proxy())
        g_source = source_impact_gate(source_type)
        B = gap_mass × f_ρ × g_source

        # 4. Peripheral amplification
        z_align = peripheral_alignment(embedding, peripheral_context)
        B = B · (1 + max(0, z_align))

        # 5. Entity channel selection
        entity_mix = compute_entity_channels(embedding)

        # 6. Distribute budget
        for match in selected:
            if match.is_node:
                ΔE = distribute_to_node(B, match, selected)
                inject_energy(match.node_id, ΔE)

            elif match.is_link:
                p_src, p_tgt = direction_prior(match.link_type)
                ΔE_src = p_src · B · weight(match) / Σweight
                ΔE_tgt = p_tgt · B · weight(match) / Σweight
                inject_energy(match.source_id, ΔE_src)
                inject_energy(match.target_id, ΔE_tgt)

        results.append(InjectionResult(...))

    return aggregate(results)
```

### 7.2 Pseudocode with Full Detail

```python
# Per chunk
for chunk in chunks:
    emb = embed(chunk)

    # Search
    node_sims = search_nodes(emb)
    link_sims = search_links(emb)
    all_matches = node_sims + link_sims

    # Entropy coverage
    p = normalize(all_matches.similarities)
    H = -sum(p_i * log(p_i) for p_i in p)
    coverage_target = 1 - exp(-H)

    selected = []
    cumulative = 0
    for match in sort_desc(all_matches):
        selected.append(match)
        cumulative += match.similarity / sum(all_sims)
        if cumulative >= coverage_target:
            break

    # Budget
    gap_mass = 0
    for m in selected:
        if m.is_node:
            gap_mass += m.similarity * max(0, m.node.threshold - m.node.energy)

    rho = compute_spectral_proxy()
    f_rho = isotonic_health(rho)  # Bootstrap 1.0
    g_src = source_gate(source_type)  # Bootstrap 1.0

    B_base = gap_mass * f_rho * g_src

    # Peripheral amp
    z_align = peripheral_z(emb, peripheral_chunks)
    B = B_base * (1 + max(0, z_align))

    # Entity mix (future: per-entity budgets)
    # For now: unified distribution, log entity attribution

    # Distribute
    total_weight = sum(
        m.similarity * max(0, m.gap) for m in selected
    )

    for m in selected:
        if m.is_node:
            weight = m.similarity * max(0, m.gap)
            allocation = B * weight / total_weight
            delta_e = min(allocation, m.gap)  # Cap at gap
            m.node.energy += delta_e

        elif m.is_link:
            # Direction prior
            dom = link_dominance(m.link_type)
            z_dom = rank_z(dom, cohort=same_type_links)
            p_src = sigmoid(z_dom)
            p_tgt = 1 - p_src

            weight = m.similarity * max(0, (m.src.gap + m.tgt.gap)/2)
            allocation = B * weight / total_weight

            delta_src = min(p_src * allocation, m.src.gap)
            delta_tgt = min(p_tgt * allocation, m.tgt.gap)

            m.src.energy += delta_src
            m.tgt.energy += delta_tgt
```

---

## 8. Examples

### 8.1 Specific Query

**Stimulus:** "What is Hamilton apportionment?"

**Search results:**
- `node_hamilton_apportionment_spec`: similarity 0.95
- `node_reinforcement_learning`: similarity 0.42
- `node_formation_quality`: similarity 0.38

**Entropy:**
```python
p = [0.95/1.75, 0.42/1.75, 0.38/1.75] ≈ [0.54, 0.24, 0.22]
H = -(0.54·log(0.54) + 0.24·log(0.24) + 0.22·log(0.22)) ≈ 1.05
```

**Coverage:**
```python
ĉ = 1 - exp(-1.05) ≈ 0.65
```

**Selection:**
```python
cumulative: 0.54 (first node) < 0.65, continue
cumulative: 0.78 (second node) >= 0.65, STOP
```

**Selected:** 2 nodes (specific query, low K)

### 8.2 Broad Query

**Stimulus:** "Tell me about the consciousness architecture"

**Search results:** 50 nodes with similarities ranging [0.35, 0.68], fairly uniform distribution

**Entropy:**
```python
H ≈ 3.5 (many similar matches)
ĉ = 1 - exp(-3.5) ≈ 0.97
```

**Selection:** ~45 nodes (need 97% coverage, broad query, high K)

### 8.3 Budget Example

**Gap mass:** 15.0
**System state:** ρ_proxy = 0.8 (slightly high)
**Frame quality history:** Recent frames show quality ≈ 0.6 when ρ ≈ 0.8
**Isotonic fit:** f(0.8) ≈ 0.85 (mild dampening)
**Source:** user_message, g(user_message) = 1.2 (effective source)

**Budget:**
```python
B = 15.0 × 0.85 × 1.2 ≈ 15.3
```

**Distribution** (3 selected nodes with gaps 5, 7, 3):
```python
weights = [0.8×5, 0.6×7, 0.5×3] = [4.0, 4.2, 1.5]
total_weight = 9.7

ΔE_1 = 15.3 × 4.0/9.7 ≈ 6.3 > gap → ΔE_1 = 5.0 (capped)
ΔE_2 = 15.3 × 4.2/9.7 ≈ 6.6 (within gap)
ΔE_3 = 15.3 × 1.5/9.7 ≈ 2.4 (within gap)
```

**Actually injected:** 5.0 + 6.6 + 2.4 = 14.0 units (slightly under budget due to cap)

---

## 9. Observability

### 9.1 Events

**Per injection:**

```json
{
  "event": "stimulus.injected",
  "source_type": "user_message",
  "chunks": 3,
  "matches_selected": 12,
  "entropy": 2.3,
  "coverage_target": 0.90,
  "budget_base": 18.5,
  "health_factor": 0.92,
  "source_gate": 1.15,
  "peripheral_amp": 1.3,
  "budget_final": 25.6,
  "energy_injected": 24.2,
  "nodes_activated": 8,
  "flips": 5
}
```

### 9.2 Diagnostics

**Dashboard queries:**

- **Source effectiveness:** Rank source types by g(source) over time
- **Coverage distribution:** Histogram of K (selected matches per stimulus)
- **Budget efficiency:** Flips per unit budget by source type
- **Health tracking:** ρ_proxy and f(ρ) over time
- **Entity affinity:** Which entities respond to which stimulus types

**Alerts:**

- f(ρ) < 0.5 (severe dampening, system supercritical)
- f(ρ) > 2.0 (severe boosting, system dying)
- Coverage target > 0.99 consistently (queries too broad, need better chunking)
- g(source) < 0.5 for critical sources (reality contact weakening)

---

## 10. Design Rationale

### 10.1 Why Entropy Coverage?

**Problem:** Fixed top-K retrieval ignores query specificity.

**Alternative:** Dynamic threshold (similarity > 0.7).

**Why entropy wins:**
- Adapts to distribution shape (sharp peak vs broad plateau)
- No arbitrary threshold tuning
- Information-theoretic grounding (coverage proportional to uncertainty)

### 10.2 Why Geometric Mean for Frame Quality?

**Problem:** Additive quality allows trade-offs (high yield, zero entropy).

**Why geometric mean wins:**
- Requires balance across all dimensions (yield AND entropy AND low overflow)
- Same reasoning as formation quality (C×E×N)
- Prevents gaming

### 10.3 Why Direction Prior from Causal Precedence?

**Problem:** Could split link injection 50/50 always.

**Why learned prior wins:**
- ENABLES links: source should activate first (it enables the target)
- BLOCKS links: target should activate (it's being blocked, needs energy to overcome)
- Different semantics require different injection patterns
- Learning from traversal data grounds this in reality

### 10.4 Why Isotonic Regression for f(ρ)?

**Problem:** Could use hand-tuned sigmoid: f(ρ) = 1 / (1 + exp(k·(ρ - ρ_0))).

**Why isotonic wins:**
- No parameter tuning (k, ρ_0)
- Monotonicity guaranteed (no surprising reversals)
- Learns actual system behavior (not assumed functional form)

---

## 11. Integration with Learning

### 11.1 Separation of Concerns

**Stimuli:** Inject energy (ΔE to nodes)
**TRACE:** Adjust weights (Δ log_weight)
**Traversal:** Flow energy (via strides) + update weights (gap closure, flips)

**Never conflate:** Energy is transient activation, weight is persistent attractor strength.

### 11.2 Feedback Loops

**Positive loop:**
```
High-weight nodes → attract more energy (valence bias) →
more likely to activate → more WM presence → weight increases further
```

**Negative loop:**
```
Persistent activation → ρ increases → f(ρ) decreases →
budget dampens → less energy injected → system stabilizes
```

**Quality gate:**
```
Ineffective source → low flip yield → g(source) decreases →
less budget from that source → natural pruning
```

### 11.3 V2 Engine Integration

Stimulus injection runs in **Activation Phase** (phase 1 of 4):

```python
# V2 Engine Tick
def tick():
    # Phase 1: Activation
    for stimulus in new_stimuli:
        inject_stimulus(stimulus)  # This spec

    # Phase 2: Redistribution
    execute_strides()  # Uses current energy + weights

    # Phase 3: Workspace
    select_working_memory()  # Uses standardized weights

    # Phase 4: Learning
    apply_trace_signals()  # Updates weights from TRACE
```

---

## 12. Future Extensions

### 12.1 Multi-Modal Stimuli

Support images, audio, structured data:

```python
if stimulus.type == "image":
    embedding = vision_encoder(stimulus.pixels)
elif stimulus.type == "audio":
    embedding = audio_encoder(stimulus.waveform)
```

Same entropy-coverage search, different embedding space.

### 12.2 Stimulus Chaining

Track causal chains (stimulus A → activation → stimulus B):

```python
stimulus_lineage = {
    "parent_id": previous_stimulus_id,
    "chain_depth": 3
}
```

Amplify budget for stimuli at end of deep chains (sustained focus deserves more energy).

### 12.3 Adversarial Dampening

Detect and dampen adversarial/spam stimuli:

```python
if entropy(matches) < 0.1 and max_similarity > 0.99:
    # Exact duplicate of recent stimulus
    g_spam = 0.1  # Severe dampening
```

### 12.4 Entity-Specific Injection

Full entity channel separation:

```python
for entity in active_entities:
    B_entity = π_entity · B
    matches_entity = filter_by_entity_affinity(matches, entity)
    distribute_budget(B_entity, matches_entity, entity_valence)
```

Allows Architect entity to receive different nodes than Validator entity for same stimulus.

---

## 13. Multi-Source Stimuli: Inclusion Policy, Routing & Task Creation

### 13.1 Overview

**Core principle:** Stimuli are **externalizable events** that should update or direct the substrate **now**.

**Key innovation:** Most stimuli are **silent** - they shape consciousness (activation, WM bias, valence) without interrupting the LLM. Event-rich sources (Telegram, build errors, logs) flow continuously into the substrate as silent evidence, creating "gravity wells" that the next conscious turn naturally falls into.

**Two coupled planes:**
- **L1 (Personal, N1):** Silent stimuli update activation immediately but don't interrupt; accumulate evidence that biases next answer via WM/valence
- **L2 (Organizational, N2):** Auto-materialize tasks from events with idempotent templates; tasks surface only when WM selects them

**No spam, natural surfacing:** Heavy error bursts or message floods don't nag the LLM - they bias WM selection so the next response naturally addresses them.

---

### 13.2 Stimulus Categories

**Three focality levels:**

| Level | Meaning | Activation Impact | Interrupt? |
|-------|---------|-------------------|------------|
| **Focal** | Demands immediate consideration | Strong activation injection, high WM bias | Only if on interrupt allowlist |
| **Ambient** | Informs context, doesn't demand action | Moderate activation, peripheral amplifier | Never |
| **Background** | Telemetry only; escalates on anomaly | Minimal unless surprise spike | Never |

**Note:** "Focal" doesn't mean "interrupt" - most focal stimuli are **silent focal** (affect substrate immediately without prompt injection).

---

### 13.3 Source Inclusion Policy

**What creates stimuli, how they route, when they interrupt:**

| Source | L1 (Personal) Stimulus | L2 (Org) Task | Interrupt LLM? | Notes |
|--------|------------------------|---------------|----------------|-------|
| **User input** (message/voice/command) | **Focal** | None | **Yes** (conversational) | Primary driver; always interrupts |
| **Telegram DM** (inbound) | **Focal (silent)** + periphery amp | Create task "Reply to @X" | **No** (unless sender on allowlist) | Embed message text; idempotent by thread_id |
| **Tool result: success** | **Ambient** | None | No | Chunk outputs; metadata: tool, params, status |
| **Tool result: error** | **Focal (silent)** when anomaly | Create task "Investigate {tool} failure" | **No** (unless sev1/safety) | Aggregate by error signature |
| **Test failure / build error** | **Ambient** → **Focal (silent)** on spike | Create task "Fix failing tests" (attach logs) | **No** (unless human-safety) | Anomaly detection required |
| **Code commit** (self/team) | **Ambient** (diff summary) | Optional task "Review/changelog" if PR open | No | Chunk by hunks; structural |
| **Document read** | **Focal** when explicit open | None | No | Chunk by headings/sections |
| **Document written** | **Focal** on commit | Optional task if spec/decision doc | No | Embed diff + final; dedup by digest |
| **Calendar event** (soon) | **Focal (silent)** 10-30min before | Optional task "Prepare for meeting" | **Yes** if whitelisted | Bias toward prep nodes |
| **Org decision / ticket assigned** | **Ambient** in N1; **Focal** in N2 | Create task "Acknowledge/Plan" | No | Cross-scope coupling |
| **System logs** (non-error) | **Ambient** only | None | No | Escalate on z-surprise |
| **Agent response** (final) | **Ambient** → **Focal** if self-referential | None | No | **Final only** (avoid echo loops); dedup by digest |
| **Navigation/clicks** | **Ambient** | None | No | Treat as periphery amplifiers |
| **Ecosystem signals** (N3) | **Ambient** → **Focal** on watchlist match | Optional task if actionable | No | Watchlist-gated |

**Critical rules:**

1. **Agent output only when final** - Avoid infinite feedback loops from in-flight chain-of-thought
2. **Deduplication by content digest** - Don't re-process identical messages/errors within time window
3. **Anomaly-gated escalation** - Routine logs stay ambient; only surprise becomes focal
4. **Silent by default** - Only interrupt allowlist sources ping LLM mid-flow
5. **Cross-scope coupling** - N2 org events create ambient N1 stimuli if citizen is member/observer

---

### 13.4 Stimulus Envelope Schema

**Complete envelope structure:**

```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1739990123456,
  "scope": "personal|organizational|ecosystem",
  "source_type": "user_message|telegram|agent_response|doc_read|doc_write|code_commit|tool_result.success|tool_result.error|test_failure|build_error|calendar|org_event|ecosystem_event|log|nav",
  "actor": "luca|ada|felix|service-name|teammate-handle",
  "content": "text excerpt or canonical summary",
  "metadata": {
    "thread_id": "tg:123|gh:pr:456",
    "path": "repo/file.py",
    "url": "https://...",
    "tool": "pytest|build|search",
    "diff": true,
    "status": "ok|error|warn",
    "severity": "info|warn|error|critical",
    "digest": "sha256:abc123...",
    "signature": "error:TypeError:line:42",
    "count": 1
  },
  "focality_hint": "focal|ambient|background",
  "privacy": "public|internal|sensitive",
  "interrupt": false,
  "attachments": [
    {"type": "link", "ref": "tg:thread:123"},
    {"type": "file", "path": "logs/test_failures.txt"}
  ]
}
```

**Field semantics:**

- `stimulus_id`: Unique identifier for this stimulus instance
- `timestamp_ms`: When event occurred (Unix epoch milliseconds)
- `scope`: Which graph to route to (N1/N2/N3)
- `source_type`: Granular type for g(source) learning (per-source flip yield)
- `actor`: Who/what generated this event
- `content`: Text for embedding (chunked if large)
- `metadata.digest`: SHA-256 of normalized content (deduplication key)
- `metadata.signature`: Error/event signature for aggregation (e.g., stack trace hash)
- `metadata.count`: Aggregation counter (incremented for duplicate digests)
- `focality_hint`: Suggested level (can be overridden by anomaly detection)
- `interrupt`: Whether to inject into system prompt now (vs silent)
- `attachments`: Linked resources for task creation

---

### 13.5 Routing & Deduplication

#### 13.5.1 Scope Routing

**Primary routing:**
```python
def route_by_scope(envelope):
    if envelope.scope == "personal":
        target_graph = "citizen_luca"  # N1
    elif envelope.scope == "organizational":
        target_graph = "mind_protocol_collective_graph"  # N2
    elif envelope.scope == "ecosystem":
        target_graph = "ecosystem_public_graph"  # N3

    return target_graph
```

**Cross-scope coupling:**
```python
# N2 → N1 coupling (org events affecting citizens)
if envelope.scope == "organizational":
    affected_citizens = get_members_or_observers(envelope)

    for citizen in affected_citizens:
        # Create ambient N1 stimulus in citizen's graph
        coupled_stimulus = {
            **envelope,
            "scope": "personal",
            "focality_hint": "ambient",
            "source_type": f"{envelope.source_type}.coupled",
            "metadata": {**envelope.metadata, "coupled_from": "N2"}
        }

        # Attenuated gate (learned from usefulness)
        g_cross = source_gate(f"{envelope.source_type}.coupled")

        enqueue_stimulus(coupled_stimulus, gate=g_cross)
```

**Why coupling:** Org decisions (N2) should subtly bias affected citizens (N1) without overwhelming personal consciousness.

#### 13.5.2 Deduplication

**Digest-based deduplication:**

```python
def normalize_content(text: str) -> str:
    """Normalize for consistent hashing."""
    return re.sub(r'\s+', ' ', text.strip().lower())

def compute_digest(envelope) -> str:
    """SHA-256 of normalized content."""
    canonical = normalize_content(envelope.content)
    return hashlib.sha256(canonical.encode()).hexdigest()

# Deduplication window (e.g., 5 minutes)
recent_digests = {}  # {digest: (timestamp, count)}

def dedup_check(envelope):
    digest = compute_digest(envelope)
    now = time.time()

    if digest in recent_digests:
        last_seen, count = recent_digests[digest]

        if now - last_seen < 300:  # 5 minute window
            # Duplicate - increment counter
            recent_digests[digest] = (now, count + 1)
            envelope.metadata['count'] = count + 1

            # Update existing stimulus/task instead of creating new
            return "duplicate"

    # New stimulus
    recent_digests[digest] = (now, 1)
    return "new"
```

**Aggregation example:**
- First error: Create task "Investigate TypeError in module X"
- Same error 5min later: Increment task counter to "2 occurrences"
- Same error 10min later: Increment to "3 occurrences", maybe boost priority

---

### 13.6 Silent Stimuli & Natural Surfacing

#### 13.6.1 Silent Processing

**Silent stimuli affect substrate without interrupting:**

```python
def process_stimulus(envelope):
    # 1. Chunk and embed
    chunks = chunk_by_source_type(envelope)
    embeddings = [embed(chunk) for chunk in chunks]

    # 2. Match nodes/links
    matches = entropy_coverage_search(embeddings)

    # 3. Inject energy (affects activation immediately)
    inject_energy(matches, budget, silent=True)

    # 4. Update WM bias counters (affects next WM selection)
    for match in matches:
        wm_bias[match.node_id] += match.similarity * g_source

    # 5. Update hunger gate biases (affects next traversal)
    if envelope.source_type in ["test_failure", "build_error"]:
        hunger_bias["integration"] += 0.5
        hunger_bias["surprise"] += 0.3

    # NO system prompt injection unless envelope.interrupt == True
```

#### 13.6.2 WM Bias Mechanism

**How silent stimuli surface naturally:**

```python
def select_working_memory(nodes, token_budget):
    """
    Working memory selection with silent stimulus bias.

    Standard WM score: z(E/tok) + z(SlowSalience/tok)
    Biased WM score: standard + bias_from_silent_stimuli
    """

    for node in nodes:
        # Standard scoring
        energy_density = node.energy / node.token_cost
        salience_density = node.slow_salience / node.token_cost

        base_score = rank_z(energy_density) + rank_z(salience_density)

        # Bias from recent silent stimuli
        silent_bias = wm_bias.get(node.id, 0.0)

        # Decay bias over time (EWMA)
        wm_bias[node.id] *= 0.9

        # Final score
        node.wm_score = base_score + silent_bias

    # Knapsack selection with biased scores
    selected = knapsack_select(nodes, token_budget, key=lambda n: n.wm_score)

    return selected
```

**Result:** Nodes related to silent stimuli (Telegram messages, test failures) naturally rise to top of WM selection, appearing in next response without forced injection.

#### 13.6.3 Hunger Gate Biasing

**Silent stimuli adjust traversal direction:**

```python
# Example: Test failures bias toward Integration hunger
def update_hunger_gates_from_silent_stimuli():
    """
    Adjust 7-hunger gates based on accumulated silent evidence.
    """

    # Count recent silent stimuli by category
    test_failure_count = count_recent_stimuli("test_failure", window=300)
    telegram_count = count_recent_stimuli("telegram", window=300)
    org_event_count = count_recent_stimuli("org_event", window=300)

    # Compute z-surprise for each category
    z_test = rank_z(test_failure_count, cohort=historical_test_counts)
    z_telegram = rank_z(telegram_count, cohort=historical_telegram_counts)
    z_org = rank_z(org_event_count, cohort=historical_org_counts)

    # Bias hunger gates (additive to base hungers)
    hunger_bias = {
        "integration": max(0, z_test),  # Test failures → fix integration
        "surprise": max(0, z_test) * 0.5,
        "identity": max(0, z_telegram) * 0.3,  # Messages → identity/comm
        "belonging": max(0, z_org) * 0.4,  # Org events → belonging
        "control": max(0, z_org) * 0.2
    }

    return hunger_bias
```

**Effect:** Traversal naturally drifts toward nodes that address accumulated silent evidence (e.g., test infrastructure nodes when failures spike).

---

### 13.7 L2 Task Auto-Creation

#### 13.7.1 Task Template Schema

**Idempotent task creation:**

```python
@dataclass
class TaskTemplate:
    """Template for auto-created N2 tasks."""
    title: str
    description: str
    due_offset: str  # e.g., "now+30m", "now+2h", "eod"
    priority: str  # "derived" (learned) or explicit
    source_stimulus_id: str
    attachments: List[Dict[str, str]]
    routing: Dict[str, str]  # {"assignee": "citizen", "scope": "personal"}
    digest: str  # Idempotence key

    # Aggregation fields
    count: int = 1
    last_updated_ms: int = 0

def create_or_update_task(template: TaskTemplate):
    """
    Create task if new, update counter if duplicate.

    Prevents "50 error tasks" → creates one aggregate task.
    """

    # Check for existing task with same digest
    existing = query_graph(
        f"MATCH (t:Task {{digest: '{template.digest}'}}) RETURN t"
    )

    if existing:
        # Update existing task
        existing.count += 1
        existing.last_updated_ms = int(time.time() * 1000)
        existing.description = update_description_with_count(
            existing.description,
            existing.count
        )

        # Maybe boost priority if count is high
        if existing.count > 10:
            existing.priority = "high"

        update_node(existing)

        logger.info(f"[TaskCreation] Updated task {existing.id}: count={existing.count}")
    else:
        # Create new task node
        task_node = {
            "type": "Task",
            "name": sanitize_name(template.title),
            "description": template.description,
            "priority": template.priority,
            "due": compute_due_timestamp(template.due_offset),
            "source_stimulus": template.source_stimulus_id,
            "digest": template.digest,
            "count": 1,
            "status": "pending",
            "created_at": int(time.time() * 1000)
        }

        create_node(task_node, scope="organizational")

        # Create attachments as links
        for attachment in template.attachments:
            create_link(
                source=task_node.id,
                target=attachment["ref"],
                link_type="REFERENCES",
                scope="organizational"
            )

        logger.info(f"[TaskCreation] Created task: {template.title}")
```

#### 13.7.2 Task Templates by Source Type

**Telegram DM:**

```python
def telegram_task_template(envelope) -> TaskTemplate:
    """Task: Reply to Telegram message."""

    sender = envelope.metadata.get("sender", "unknown")
    thread_id = envelope.metadata.get("thread_id")

    # Digest by thread (not individual message)
    digest = hashlib.sha256(f"telegram:{thread_id}".encode()).hexdigest()

    return TaskTemplate(
        title=f"Reply to Telegram: @{sender}",
        description=f"Unread messages from @{sender} in thread {thread_id}.",
        due_offset="now+30m",
        priority="derived",  # Learn from completion latency
        source_stimulus_id=envelope.stimulus_id,
        attachments=[{"type": "link", "ref": f"tg:thread:{thread_id}"}],
        routing={"assignee": "citizen", "scope": "personal"},
        digest=digest
    )
```

**Test Failure:**

```python
def test_failure_task_template(envelope) -> TaskTemplate:
    """Task: Investigate failing tests."""

    signature = envelope.metadata.get("signature", "unknown")

    # Digest by error signature (aggregate similar failures)
    digest = hashlib.sha256(f"test_failure:{signature}".encode()).hexdigest()

    return TaskTemplate(
        title=f"Investigate failing tests: {signature}",
        description=f"Test failures in {envelope.metadata.get('path', 'unknown')}",
        due_offset="now+2h",
        priority="derived",
        source_stimulus_id=envelope.stimulus_id,
        attachments=[
            {"type": "link", "ref": f"log:test_failures:{envelope.stimulus_id}"},
            {"type": "file", "path": envelope.metadata.get("log_path", "")}
        ],
        routing={"assignee": "team", "scope": "organizational"},
        digest=digest
    )
```

**Calendar Event:**

```python
def calendar_task_template(envelope) -> TaskTemplate:
    """Task: Prepare for upcoming meeting."""

    event_id = envelope.metadata.get("event_id")

    digest = hashlib.sha256(f"calendar:{event_id}".encode()).hexdigest()

    return TaskTemplate(
        title=f"Prepare for: {envelope.metadata.get('title', 'Meeting')}",
        description=f"Meeting starts at {envelope.metadata.get('start_time')}",
        due_offset="now+10m",  # Shortly before meeting
        priority="high",
        source_stimulus_id=envelope.stimulus_id,
        attachments=[
            {"type": "link", "ref": f"calendar:event:{event_id}"}
        ],
        routing={"assignee": "citizen", "scope": "personal"},
        digest=digest
    )
```

#### 13.7.3 Task Surfacing

**Tasks surface through WM selection, not prompt injection:**

```python
# When selecting WM, include high-priority pending tasks
def select_working_memory_with_tasks(nodes, token_budget):
    """
    Standard WM selection + high-priority tasks.
    """

    # Standard WM selection
    selected_nodes = select_working_memory(nodes, token_budget * 0.9)

    # Query high-priority pending tasks
    pending_tasks = query_graph("""
        MATCH (t:Task {status: 'pending'})
        WHERE t.priority IN ['high', 'critical']
        OR t.due < $now + 600000  # Due within 10 min
        RETURN t
        ORDER BY t.priority DESC, t.due ASC
        LIMIT 5
    """)

    # Add tasks to WM if token budget allows
    task_tokens = sum(estimate_tokens(task) for task in pending_tasks)

    if task_tokens < token_budget * 0.1:
        selected_nodes.extend(pending_tasks)

    return selected_nodes
```

**Result:** Urgent tasks naturally appear in next response via WM selection.

---

### 13.8 Anomaly Detection & Escalation

#### 13.8.1 EWMA + MAD Tracking

**Per event type, track baseline and detect surprise:**

```python
@dataclass
class AnomalyTracker:
    """Tracks baseline and detects anomalies per event type."""

    event_type: str
    ewma: float = 0.0  # Exponentially weighted moving average
    mad: float = 0.0   # Mean absolute deviation
    alpha: float = 0.1  # EWMA decay rate

    # Rolling window for percentile calculation
    history: deque = field(default_factory=lambda: deque(maxlen=1000))

def update_anomaly_tracker(tracker: AnomalyTracker, value: float):
    """
    Update EWMA and MAD with new observation.
    """

    # Update EWMA
    tracker.ewma = tracker.alpha * value + (1 - tracker.alpha) * tracker.ewma

    # Update MAD (mean absolute deviation)
    deviation = abs(value - tracker.ewma)
    tracker.mad = tracker.alpha * deviation + (1 - tracker.alpha) * tracker.mad

    # Add to history
    tracker.history.append(value)

def compute_z_surprise(tracker: AnomalyTracker, value: float) -> float:
    """
    Compute z-score surprise using MAD (robust to outliers).
    """

    if tracker.mad < 1e-9:
        return 0.0  # No variance yet

    z = (value - tracker.ewma) / (tracker.mad + 1e-9)

    return z

def is_anomalous(tracker: AnomalyTracker, value: float, threshold_percentile: float = 0.90) -> bool:
    """
    Check if value exceeds learned threshold (e.g., weekly Q90).
    """

    z = compute_z_surprise(tracker, value)

    if len(tracker.history) < 50:
        # Not enough data - use fixed threshold
        return z > 3.0

    # Compute percentile threshold from history
    z_scores = [compute_z_surprise(tracker, v) for v in tracker.history]
    threshold = np.percentile(z_scores, threshold_percentile * 100)

    return z > threshold
```

#### 13.8.2 Escalation Logic

**Background → Focal when anomalous:**

```python
def process_stimulus_with_anomaly_check(envelope):
    """
    Check for anomaly; escalate focality if detected.
    """

    # Get tracker for this event type
    tracker = anomaly_trackers.get(envelope.source_type)

    if tracker is None:
        # Initialize tracker
        tracker = AnomalyTracker(event_type=envelope.source_type)
        anomaly_trackers[envelope.source_type] = tracker

    # Current event rate (events per minute)
    current_rate = count_events_last_minute(envelope.source_type)

    # Update tracker
    update_anomaly_tracker(tracker, current_rate)

    # Check for anomaly
    if is_anomalous(tracker, current_rate):
        # Escalate focality
        original_focality = envelope.focality_hint
        envelope.focality_hint = "focal"
        envelope.metadata["anomaly_detected"] = True
        envelope.metadata["z_surprise"] = compute_z_surprise(tracker, current_rate)

        logger.warning(
            f"[AnomalyDetection] Escalated {envelope.source_type}: "
            f"{original_focality} → focal (z={envelope.metadata['z_surprise']:.2f})"
        )

    # Process stimulus normally
    process_stimulus(envelope)
```

#### 13.8.3 Saturation Rule

**Create aggregate task when event rate exceeds baseline:**

```python
def check_saturation(envelope):
    """
    Create single aggregate task when event rate saturates.

    Example: >5× baseline errors within 10 minutes
    """

    tracker = anomaly_trackers.get(envelope.source_type)

    if tracker is None:
        return

    current_rate = count_events_last_minute(envelope.source_type)

    # Saturation threshold: 5× baseline
    if current_rate > 5 * tracker.ewma:
        # Check if aggregate task already exists
        digest = hashlib.sha256(f"saturation:{envelope.source_type}".encode()).hexdigest()

        existing_task = query_graph(f"MATCH (t:Task {{digest: '{digest}'}}) RETURN t")

        if not existing_task:
            # Create aggregate task
            task = TaskTemplate(
                title=f"Investigate {envelope.source_type} spike",
                description=f"Event rate: {current_rate:.1f}/min (baseline: {tracker.ewma:.1f}/min)",
                due_offset="now+15m",
                priority="high",
                source_stimulus_id=envelope.stimulus_id,
                attachments=[],
                routing={"assignee": "team", "scope": "organizational"},
                digest=digest
            )

            create_or_update_task(task)

            logger.warning(
                f"[Saturation] Created aggregate task for {envelope.source_type} spike"
            )
```

---

### 13.9 Interrupt Policy

#### 13.9.1 Interrupt Allowlist

**Only these sources interrupt LLM mid-flow:**

```python
# Configured per citizen
interrupt_allowlist = {
    "user_message": True,  # Always interrupt
    "telegram": ["mom", "alice"],  # Only specific senders
    "calendar": ["meeting_start"],  # Only imminent events
    "error": ["sev1", "human_safety"],  # Only critical errors
    "org_event": []  # Never interrupt for org events
}

def should_interrupt(envelope) -> bool:
    """
    Check if stimulus should interrupt LLM.
    """

    source_type = envelope.source_type

    if source_type not in interrupt_allowlist:
        return False

    config = interrupt_allowlist[source_type]

    if config is True:
        return True

    if isinstance(config, list):
        # Check specific conditions
        if source_type == "telegram":
            sender = envelope.metadata.get("sender")
            return sender in config

        if source_type == "error":
            severity = envelope.metadata.get("severity")
            return severity in config

        if source_type == "calendar":
            event_type = envelope.metadata.get("event_type")
            return event_type in config

    return False
```

#### 13.9.2 Interrupt vs Silent Injection

```python
def inject_stimulus_with_interrupt_policy(envelope):
    """
    Process stimulus; inject into system prompt only if interrupt allowed.
    """

    # Standard processing (energy injection, WM bias, hunger adjustment)
    result = process_stimulus(envelope)

    # Check interrupt policy
    if should_interrupt(envelope):
        # Inject into system prompt (interrupts LLM)
        inject_into_system_prompt(envelope)

        logger.info(f"[Interrupt] Injected {envelope.source_type} into system prompt")
    else:
        # Silent processing (affects next turn via WM)
        logger.debug(f"[Silent] Processed {envelope.source_type} silently")

    return result
```

---

### 13.10 Source-Specific Chunking

**Structural chunking per source type:**

```python
def chunk_by_source_type(envelope) -> List[str]:
    """
    Source-aware chunking (not generic semantic chunking).
    """

    source_type = envelope.source_type
    content = envelope.content

    if source_type in ["user_message", "telegram", "agent_response"]:
        # Paragraph-based chunking
        return chunk_paragraphs(content, max_tokens=512, overlap=50)

    elif source_type in ["doc_read", "doc_write"]:
        # Structure-based chunking (headings, sections)
        return chunk_by_structure(content, preserve_code_blocks=True)

    elif source_type == "code_commit":
        # Chunk by diff hunks
        return chunk_diff_hunks(content)

    elif source_type in ["test_failure", "build_error", "tool_result.error"]:
        # Chunk by error blocks (stack traces, messages)
        return chunk_error_blocks(content)

    elif source_type == "log":
        # Chunk by log entries (timestamp boundaries)
        return chunk_log_entries(content)

    else:
        # Fallback: generic semantic chunking
        return chunk_semantic(content, max_tokens=512, overlap=50)

def chunk_diff_hunks(diff_text: str) -> List[str]:
    """
    Chunk git diff by hunks with minimal context.
    """
    hunks = []
    current_hunk = []

    for line in diff_text.split('\n'):
        if line.startswith('@@'):
            # New hunk
            if current_hunk:
                hunks.append('\n'.join(current_hunk))
            current_hunk = [line]
        else:
            current_hunk.append(line)

    if current_hunk:
        hunks.append('\n'.join(current_hunk))

    return hunks

def chunk_error_blocks(error_text: str) -> List[str]:
    """
    Chunk error output by structural blocks (stack traces, messages).
    """
    # Detect stack trace boundaries
    blocks = []
    current_block = []

    for line in error_text.split('\n'):
        if re.match(r'^\s+File "', line):
            # Stack trace line
            current_block.append(line)
        elif re.match(r'^[A-Z][a-zA-Z]+Error:', line):
            # Error type line
            if current_block:
                blocks.append('\n'.join(current_block))
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        blocks.append('\n'.join(current_block))

    return blocks
```

---

### 13.11 Priority Queue & Flood Control

#### 13.11.1 Priority Queue Structure

```python
@dataclass
class StimulusQueueEntry:
    """Entry in stimulus processing queue."""

    envelope: Dict[str, Any]
    priority_score: float
    enqueued_at_ms: int

class StimulusPriorityQueue:
    """
    Time-budget processing queue.

    Prevents unbounded stimuli from overwhelming frame.
    """

    def __init__(self, max_queue_size: int = 1000):
        self.queue = []  # Heap-based priority queue
        self.max_queue_size = max_queue_size

    def enqueue(self, envelope: Dict[str, Any]):
        """
        Add stimulus to queue with priority score.

        Priority = anomaly_z * 2.0 + g(source) + recency_factor
        """

        # Compute priority score
        anomaly_z = envelope.get("metadata", {}).get("z_surprise", 0.0)
        g_source = source_gate(envelope["source_type"])
        recency_factor = 1.0 / (1.0 + (time.time() - envelope["timestamp_ms"] / 1000))

        priority = anomaly_z * 2.0 + g_source + recency_factor

        entry = StimulusQueueEntry(
            envelope=envelope,
            priority_score=priority,
            enqueued_at_ms=int(time.time() * 1000)
        )

        # Add to heap (max-heap via negative priority)
        heapq.heappush(self.queue, (-priority, entry))

        # Enforce max queue size
        if len(self.queue) > self.max_queue_size:
            # Drop lowest priority item
            heapq.heappop(self.queue)
            logger.warning("[StimulusQueue] Queue full, dropped lowest priority stimulus")

    def consume_by_time_budget(self, time_budget_ms: float) -> List[Dict[str, Any]]:
        """
        Pull stimuli from queue until time budget exhausted.

        Args:
            time_budget_ms: Available processing time this frame

        Returns:
            List of stimulus envelopes to process
        """

        consumed = []
        time_used = 0.0

        while self.queue and time_used < time_budget_ms:
            # Estimate processing time per stimulus (learned)
            avg_processing_time = 50.0  # ms (TODO: learn from history)

            if time_used + avg_processing_time > time_budget_ms:
                break

            # Pop highest priority
            _, entry = heapq.heappop(self.queue)
            consumed.append(entry.envelope)

            time_used += avg_processing_time

        logger.info(
            f"[StimulusQueue] Consumed {len(consumed)} stimuli "
            f"({time_used:.1f}ms / {time_budget_ms:.1f}ms budget)"
        )

        return consumed
```

#### 13.11.2 Frame Processing Loop

```python
def process_stimuli_this_frame(frame_time_budget_ms: float):
    """
    Process stimuli from queue within frame time budget.
    """

    # Pull stimuli by time budget
    stimuli = stimulus_queue.consume_by_time_budget(frame_time_budget_ms)

    for envelope in stimuli:
        # Deduplication check
        if dedup_check(envelope) == "duplicate":
            # Update existing task/stimulus
            continue

        # Anomaly detection
        process_stimulus_with_anomaly_check(envelope)

        # Task creation (if applicable)
        if template := task_template_for(envelope):
            create_or_update_task(template)

        # Saturation check
        check_saturation(envelope)

    # Surplus stays in queue for next frame
    if stimulus_queue.queue:
        logger.debug(
            f"[StimulusQueue] {len(stimulus_queue.queue)} stimuli remain queued"
        )
```

---

### 13.12 Complete Router Implementation

**Bringing it all together:**

```python
def route_stimulus(envelope: Dict[str, Any]):
    """
    Complete stimulus routing pipeline.

    1. Deduplication
    2. Scope routing
    3. Focality & gating (learned)
    4. Chunking & embedding
    5. Enqueue for processing
    6. Task creation (L2)
    """

    # 1. Deduplication
    digest = compute_digest(envelope)
    envelope["metadata"]["digest"] = digest

    if dedup_check(envelope) == "duplicate":
        logger.debug(f"[Router] Duplicate stimulus: {digest[:8]}")
        return

    # 2. Scope routing
    target_graph = route_by_scope(envelope)

    # 3. Source gating (learned)
    g_src = source_gate(envelope["source_type"])

    # 4. Anomaly score
    anomaly_z = compute_anomaly_z(envelope)

    # 5. Focality determination
    focal = (envelope.get("focality_hint") == "focal") or (anomaly_z > 0)

    # 6. Chunking by source type
    chunks = chunk_by_source_type(envelope)

    # 7. Embedding
    embeddings = [embed(chunk) for chunk in chunks]

    # 8. Enqueue for processing
    stimulus_queue.enqueue({
        "graph": target_graph,
        "embeds": embeddings,
        "source_gate": g_src,
        "focal": focal,
        "silent": not should_interrupt(envelope),
        "envelope": envelope
    })

    logger.info(
        f"[Router] Enqueued {envelope['source_type']}: "
        f"scope={envelope['scope']}, focal={focal}, silent={not should_interrupt(envelope)}"
    )

    # 9. L2 Task creation (if applicable)
    if envelope["scope"] == "organizational":
        if template := task_template_for(envelope):
            create_or_update_task(template)

    # 10. Cross-scope coupling (N2 → N1)
    if envelope["scope"] == "organizational":
        affected_citizens = get_members_or_observers(envelope)

        for citizen in affected_citizens:
            coupled_envelope = create_coupled_stimulus(envelope, citizen)
            route_stimulus(coupled_envelope)
```

---

### 13.13 Examples

#### 13.13.1 Telegram DM Flow

**Inbound message from @alice:**

```json
{
  "stimulus_id": "uuid-123",
  "timestamp_ms": 1739990123456,
  "scope": "personal",
  "source_type": "telegram",
  "actor": "alice",
  "content": "Hey, did you see the new design mockups?",
  "metadata": {
    "thread_id": "tg:456",
    "sender": "alice",
    "digest": "sha256:abc..."
  },
  "focality_hint": "focal",
  "privacy": "internal",
  "interrupt": false
}
```

**Processing:**

1. Router deduplicates by thread_id (first message in thread → new)
2. Scope routing: N1 personal graph
3. Source gate: g("telegram") = 1.2 (learned, effective source)
4. Focality: Focal (silent) - no interrupt unless alice on allowlist
5. Chunking: Single chunk (short message)
6. Embedding: 768-dim vector
7. Enqueue: silent=True, focal=True
8. L2 Task creation: "Reply to Telegram: @alice" (digest by thread)
9. **Next frame:** Energy injected into communication-related nodes
10. **Next user query:** WM bias boosts "telegram:alice" nodes → surfaces in response

**Result:** Alice's message doesn't interrupt current work, but naturally surfaces in next conscious turn.

#### 13.13.2 CI Test Failure Spike

**10 test failures in 5 minutes (normal: 1-2/hour):**

```json
{
  "stimulus_id": "uuid-456",
  "scope": "organizational",
  "source_type": "test_failure",
  "actor": "ci-service",
  "content": "TypeError: 'NoneType' object is not subscriptable at line 42",
  "metadata": {
    "path": "tests/test_retrieval.py",
    "signature": "TypeError:NoneType:line:42",
    "severity": "error",
    "digest": "sha256:def..."
  },
  "focality_hint": "ambient"
}
```

**Processing:**

1. Anomaly tracker detects spike: z_surprise = 4.2 (way above baseline)
2. Escalate focality: ambient → focal (silent)
3. Aggregate by signature: 10 failures → one task
4. Task creation: "Investigate failing tests (10 occurrences)"
5. Hunger gate bias: Integration +0.5, Surprise +0.3
6. **Next frame:** Integration-driven traversal toward test infrastructure nodes
7. **Next response:** WM naturally includes test health summary + aggregate task

**Result:** Spike surfaces without spam - one aggregate task, biased traversal.

---

### 13.14 Integration with Existing Pipeline

**Stimulus injection now has two entry points:**

1. **User input (conversational):** Immediate processing, always interrupts
   ```python
   envelope = create_user_message_stimulus(text)
   route_stimulus(envelope)
   ```

2. **Event sources (silent):** Queued processing, rarely interrupts
   ```python
   envelope = create_telegram_stimulus(message)
   route_stimulus(envelope)  # Silent by default
   ```

**Frame processing order:**

```python
def consciousness_frame():
    # Phase 0: Event ingestion (async, background)
    # Events → stimulus envelopes → priority queue

    # Phase 1: Stimulus processing (time-budgeted)
    time_budget = compute_frame_time_budget()
    process_stimuli_this_frame(time_budget)

    # Phase 2: Redistribution (traversal, strides)
    # Uses activation from Phase 1, hunger biases from silent stimuli

    # Phase 3: Working memory selection
    # Uses WM bias from silent stimuli

    # Phase 4: Learning (TRACE, weight updates)
```

---

## References

- trace_weight_learning.md - Separation: TRACE adjusts weights, stimuli inject energy
- 05_sub_entity_system.md - Valence uses weights to bias energy flow
- consciousness_learning_integration.md - V2 engine activation phase integration
- schema_learning_infrastructure.md - Node energy field vs link energy metadata

**Document Status:** Complete specification, ready for activation phase implementation.
