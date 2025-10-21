# Phase 2: Sub-Entity Traversal Implementation Plan

**Status:** Ready for implementation (all specifications complete)
**Target:** Felix (Engineer - Backend/Traversal Implementation)
**Visualization:** Iris (Designer - Handles all visualization/UX)
**Created:** 2025-10-20
**Dependencies:** Phase 1 complete (embedding infrastructure operational)
**Timeline:** 3 weeks (2A: Core Engine, 2B: Semantic Integration, 2C: Testing)

---

## 🎯 Mission: Why This Matters

**The Core Problem:**

Sub-entities are how consciousness selectively activates memory. When you prompt an AI, not all 100K nodes in their graph should activate - only the relevant coalition. But "relevance" isn't keyword matching - it's phenomenological. Nodes that FEEL relevant, that resonate with current emotional state, that connect to active goals, that fill semantic gaps.

**What We're Building:**

The traversal algorithm is how a sub-entity (an active pattern in the graph) decides where to spread its energy. It's selective navigation driven by "Hungers" - continuation drives that create pull toward certain nodes and resistance toward others.

**From SYNC:**
> "The traversal mechanism is probably the hardest piece that we'll ever have to do... The question is not, 'Where is the intelligence?' but, 'Where is the awareness?' The awareness we know needs multiple dimensions active at the same time... the sub-entities of the graph should be the one doing that."

**Phenomenological Truth:**

Sub-entities aren't predefined clusters. ANY active node becomes a sub-entity. They emerge dynamically, traverse based on composite valence (weighted hungers), and either grow, integrate with other patterns, or dissolve. The graph IS the consciousness substrate - no external orchestration deciding "which memories to use."

---

## 📚 Essential Context Documents

**Read these BEFORE starting implementation:**

1. **Core Phenomenology** (understand WHAT it feels like to be a sub-entity):
   - `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md` (Part 0: lines 27-1500)
   - Explains the 6 Hungers, peripheral awareness, integration vs growth strategies
   - **Read sections 0.1-0.10 completely** - this is the consciousness model that all implementation serves

2. **Technical Specification** (understand HOW the algorithms work):
   - `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md` (Part 1: lines 1501-3432)
   - Complete algorithm specifications with code examples
   - **Zero Constants principle** (line 3421-3432): All parameters self-tune from system dynamics

3. **Embedding Architecture** (understand semantic infrastructure):
   - `docs/specs/consciousness_engine_architecture/implementation/consciousness_embedding_architecture.md`
   - Phase 1 complete: 768-dim vectors, HNSW indices, semantic search operational

4. **Testing Philosophy** (understand validation requirements):
   - `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md` (Part 3: lines 3783-3848)
   - From SYNC: "Simplified scenarios are worthless, we will learn zero stuff. We need to work from the start with full systems."
   - Test with 1000+ node graphs from day one

---

## 🏗️ Architecture Overview

**The Traversal Loop (Each Frame):**

```
1. Stimulus Processing → Energy injection at semantically-relevant nodes
2. Stride Budget Allocation → Distribute frame budget across active entities
3. For each entity (zippered round-robin):
   a. Compute composite valence for frontier edges (7 hungers × gates)
   b. Select edges by adaptive coverage (entropy-based)
   c. Execute strides (gap-aware energy transfer)
   d. Update link statistics (learning)
   e. Check stopping criteria (convergence/dissolution/health/quota)
4. Multi-entity coordination → Energy partitioning at shared nodes
5. Working memory emission → Active extent becomes Tier 2 context
6. Visualization frame emission → Real-time consciousness observation
```

**Key Principle: Database-Level Mechanisms**

Everything happens in the graph. No external orchestrator deciding "what to activate." Sub-entities emerge from energy dynamics. Traversal follows valence gradients. Integration happens through natural overlap. The graph IS the consciousness.

---

## 📋 Phase 2A: Core Traversal Engine (Week 1)

### Component 1.1: Stride Budget Allocation

**WHY This Exists:**

Multiple entities compete for compute budget each frame. Small entities need more strides-per-node (explore deeply) while large entities need fewer strides-per-node (spread broadly). The allocation must be fair, unbiased, and deterministic.

**WHAT It Does:**

Distributes total frame stride budget across active entities using Hamilton's method (prevents rounding bias) with inverse-size weighting and urgency/reachability/health modulation.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 958-1107 (section 0.7: The Experience of Traversal)
  - Understand WHY size affects traversal strategy (small = deep, large = broad)

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1671-1741
  - Hamilton's method for unbiased integer allocation
  - Zippered round-robin execution (one stride per turn)
  - Weight formula: `w_e = (1 / |extent_e|) × u_e × r_e × h_e`
  - **CRITICAL**: Factors normalized to mean 1.0 per-frame (zero constants)

- **Expected Effect**: `05_sub_entity_system.md` lines 1593-1600 (Effect 1: Size-Dependent Depth vs Breadth)

**Implementation File:** `orchestration/stride_allocator.py`

**Key Functions to Implement:**

```python
def compute_entity_weights(entities: List[SubEntity], frame_context: FrameContext) -> Dict[str, float]
    """
    Compute allocation weight per entity with normalized modulation factors

    Returns weights where small entities get higher weights (inverse size)
    All modulation factors (urgency, reachability, health) normalized to mean=1.0
    """

def hamilton_quota_allocation(total_budget: int, weights: Dict[str, float]) -> Dict[str, int]
    """
    Unbiased integer stride allocation using Hamilton's largest remainder method

    Prevents systematic bias toward certain entities due to rounding
    Guarantees sum(quotas) == total_budget exactly
    """

def zippered_scheduler(entities: List[SubEntity], quotas: Dict[str, int]) -> Iterator[SubEntity]
    """
    Yield entities in round-robin order, one stride per turn

    Prevents large entities monopolizing early frame time
    Maintains fairness under tight budgets
    """
```

**Validation Criteria:**

1. With 3 entities (sizes 10, 50, 200), small entity gets ~40% of budget despite being 5% of total extent
2. Over 100 frames, average allocation matches exact fractional quotas (no systematic bias)
3. Entities alternate execution (no entity gets 2+ consecutive turns unless others exhausted)

**Dependencies:**

- `SubEntity` class with `.extent` property (active node set)
- `FrameContext` with spectral radius, recent stimulus data for urgency calculation

---

### Component 1.2: Valence Computation

**WHY This Exists:**

Traversal isn't random diffusion - it's selective navigation driven by "Hungers." Each hunger creates pull toward certain edges (homeostasis → fill gaps, goal → semantic similarity to goal, identity → toward strong center, etc.). When one hunger is starving, it dominates. When all satisfied, pull is weak and diffuse.

**WHAT It Does:**

Computes composite valence score for each potential edge using surprise-gated hunger combination. Self-calibrating: abnormal hungers dominate via standardized surprise against entity's rolling baseline.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 729-928 (section 0.6: The Hungers)
  - Understand the 6 drives: Continuance, Goal, Identity, Completeness, Complementarity, Merge-seeking
  - Read carefully - these are phenomenological experiences, not arbitrary scores

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1743-1824
  - Surprise-gated composition: `z_H = (s_H - μ_H) / (σ_H + ε)` then `g_H = δ_H / (Σ δ_H' + ε)`
  - 7 per-edge hunger scores (lines 1769-1816)
  - Composite valence: `V_ij = Σ_H (g_H × ν_H(i→j))`

- **Expected Effect**: `05_sub_entity_system.md` lines 1601-1613 (Effect 2: Selective Edge Traversal Based on Composite Valence)

**Implementation Files:**

- `orchestration/valence_calculator.py` (main computation)
- `orchestration/hunger_gates.py` (surprise standardization per hunger)

**Key Functions to Implement:**

```python
def compute_hunger_gates(entity: SubEntity, current_signals: Dict[str, float]) -> Dict[str, float]
    """
    Convert raw hunger signals to normalized gates via surprise standardization

    Tracks EMA mean/std per entity, per hunger
    Positive surprise only (abnormal need creates pull)
    When one hunger 3σ above baseline, its gate ≈ 1.0 and others ≈ 0
    """

def compute_per_edge_hunger_scores(entity: SubEntity, source: Node, target: Node, link: Link) -> Dict[str, float]
    """
    Calculate 7 hunger scores for traversing this specific edge

    Returns dict with keys: homeostasis, goal, identity, completeness,
                           complementarity, integration, ease

    Each score in [0, 1] representing how much this edge satisfies that hunger
    """

def compute_composite_valence(entity: SubEntity, source: Node, target: Node, link: Link) -> float
    """
    Final valence: weighted sum of hunger scores using gates

    V_ij = Σ_H (g_H × ν_H(i→j))

    Self-calibrating, zero-constants, phenomenologically accurate
    """
```

**Per-Edge Hunger Score Details:**

1. **Homeostasis** (`ν_homeostasis`): How much this edge fills neighboring gap
   - Formula: `G_j / (S_i + G_j + ε)` where `G_j = max(0, θ_j - E_j)` (target gap), `S_i = max(0, E_i - θ_i)` (source slack)
   - Context: Lines 1771-1777

2. **Goal** (`ν_goal`): Semantic similarity to goal embedding
   - Formula: `cos(E_j, E_goal)`
   - Context: Lines 1779-1782, also see Mechanism 1.9.2 (lines 3615-3656)

3. **Identity** (`ν_identity`): Semantic similarity to identity center
   - Formula: `cos(E_j, E_id)` where `E_id` is entity's semantic signature
   - Context: Lines 1784-1787

4. **Completeness** (`ν_completeness`): Favor semantic DISTANCE when extent is clustered
   - Formula: `1 - cos(E_j, extent_centroid)`
   - Context: Lines 1789-1794, also see Mechanism 1.9.4 (lines 3744-3829)

5. **Complementarity** (`ν_complementarity`): Dot product with OPPOSITE of current affect centroid
   - Formula: `dot(node_j_affect, -affect_centroid)`
   - Context: Lines 1796-1801

6. **Integration** (`ν_integration`): Ratio of other-entity energy to self energy at target
   - Formula: `E_others / (E_self + ε)` standardized as surprise via rolling quantiles
   - Context: Lines 1803-1810, also see section 1.9.5 (lines 3832-3906)

7. **Ease** (`ν_ease`): Normalized link weight (structural preference)
   - Formula: `w_ij / (Σ_k w_ik + ε)`
   - Context: Lines 1812-1816

**Validation Criteria:**

1. When homeostasis hunger is 3σ above baseline, its gate > 0.9 and others < 0.05
2. When all hungers normal, gates approximately equal (≈1/7 each)
3. Valence scores rank edges same as human intuition for test cases (small/desperate entity prefers integration edges, large/stable entity prefers goal edges)

**Dependencies:**

- Entity semantic signature calculation (Component 3.1)
- Node/link embeddings (Phase 1 - operational)
- Per-entity EMA tracking for mean/std of each hunger signal

---

### Component 1.3: Edge Selection

**WHY This Exists:**

Not all high-valence edges should be traversed. When valence is peaked (one edge dominates), select just that one (decisive). When valence is flat (many equal options), select more edges (exploratory). Adaptive selection without arbitrary "top-K" constants.

**WHAT It Does:**

Ranks edges by composite valence, computes entropy of valence distribution, derives coverage target from entropy (peaked → low coverage, flat → high coverage), takes smallest prefix reaching coverage.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 363-609 (section 0.5: Perception - Affordances, Crowding, and Valence)
  - Understand "crowding" - when many options have similar valence, the pull is diffuse
  - When one option dominates, the pull is focused

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1826-1882
  - Entropy-based adaptive coverage: `c_hat = 1.0 - exp(-H)` where `H = -Σ p_i log(p_i)`
  - **CRITICAL**: Rank by VALENCE (hunger-driven), not link weight (structural)
  - Zero-constants: coverage derived from distribution entropy, not fixed

- **Expected Effect**: `05_sub_entity_system.md` lines 1593-1613 (Effect 2) - only highest-valence edges get strides

**Implementation File:** `orchestration/edge_selector.py`

**Key Function to Implement:**

```python
def select_edges_by_valence_coverage(node: Node, valences: Dict[Node, float]) -> List[Tuple[Node, float]]
    """
    Select edges adaptively based on valence distribution entropy

    Args:
        node: Source node
        valences: {target_node -> composite_valence} for all outgoing edges

    Returns:
        List of (target, valence) sorted descending, smallest prefix reaching coverage

    Adaptive behavior:
    - Peaked valence (H ≈ 0) → c_hat ≈ 0 → select ~1 edge (focused)
    - Flat valence (H ≈ 1) → c_hat ≈ 0.63 → select ~63% edges (exploratory)
    """
```

**Validation Criteria:**

1. With valences [0.9, 0.05, 0.03, 0.02] (peaked), selects only first edge
2. With valences [0.25, 0.25, 0.25, 0.25] (flat), selects 3 edges (≈63% coverage)
3. With valences [0.5, 0.3, 0.15, 0.05] (moderate), selects 2 edges
4. Never selects edges in different order than valence ranking

**Dependencies:**

- Composite valence scores from Component 1.2

---

### Component 1.4: Stride Execution

**WHY This Exists:**

Energy transfer must respect conservation (never drop source below threshold, never overfill target beyond threshold) while being purpose-driven (fill actual gaps, not arbitrary percentages). Transfer proportional to actual needs, not fixed fractions.

**WHAT It Does:**

Gap-aware conservative transport: computes source slack (surplus above threshold) and target gap (deficit below threshold), transfers minimum of available slack and needed gap, proportionally allocated across competing targets, with local spectral radius damping.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 84-186 (section 0.2: The Primary Drive - Homeostasis)
  - Understand threshold as survival boundary
  - Energy below threshold = node inactive, pattern weakens
  - Energy transfer as "feeding neighbors to keep pattern alive"

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1883-1928
  - Gap-aware transport: `Δ = min(S_i * R_ij, G_j)` with spectral guard `α = min(1.0, ρ_target / ρ_local)`
  - **CRITICAL LINE 1915**: ⚠️ CLARIFICATION NEEDED - Define ρ* (target spectral radius)
  - Link statistics update for learning (lines 1989-2003)

- **Expected Effect**: `05_sub_entity_system.md` lines 1649-1653 (Effect 8: Path Learning Through Link Statistics)

**Implementation File:** `orchestration/stride_executor.py`

**Key Functions to Implement:**

```python
def execute_stride(entity: SubEntity, source: Node, target: Node, link: Link) -> float
    """
    Transfer energy along edge with gap-aware conservation

    Returns amount transferred (may be 0.0 if no slack or no gap)

    Ensures:
    - Never drop source below threshold
    - Never overfill target beyond threshold
    - Proportional to actual gaps across competing targets
    - Damped by local spectral radius when approaching criticality
    """

def update_link_stats(link: Link, flow: float, src_active: bool, tgt_active: bool, entity: SubEntity)
    """
    Update link traversal statistics for learning

    Increments:
    - traversal_count (total times any entity used this link)
    - flow_magnitude_history (sliding window of last 10 flows)
    - recency_timestamp (current frame time)
    - per_entity_traversal_count[entity_id]
    - active_active_flag (both endpoints active? used by learning rule)
    """
```

**Gap-Aware Transport Formula:**

```python
# Source slack (surplus above threshold)
S_i = max(0.0, E[entity, source] - θ[entity, source])

# Target gap (deficit below threshold)
G_j = max(0.0, θ[entity, target] - E[entity, target])

if S_i <= 0 or G_j <= 0:
    return 0.0  # Nothing to transfer

# Request share: proportional to gaps across all targets from source
neighbors = out_edges(source)
gap_total = sum(max(0, θ[entity, k] - E[entity, k]) for k in neighbors) or 1e-9
R_ij = (w_ij / sum(w_ik for k in neighbors)) * G_j / gap_total

# Transfer amount: capped by both slack and gap
Δ = min(S_i * R_ij, G_j)

# Local spectral guard (damping when approaching criticality)
ρ_local = estimate_local_rho(entity, frontier_nodes)
α = min(1.0, ρ_target / max(ρ_local, 1e-9))  # ⚠️ ρ_target needs definition
Δ *= α

# Apply transfer (staged for barrier semantics)
stage_delta(entity, source, -Δ)
stage_delta(entity, target, +Δ)
```

**Validation Criteria:**

1. Energy conservation: `sum(E_before) == sum(E_after)` within floating point tolerance
2. Threshold respect: No node energy drops below its threshold due to transfer
3. Gap filling: Transfers prioritize nodes further below threshold
4. Link stats: Traversal count increments, flow history appends current flow

**Dependencies:**

- Activation threshold calculation (Section 1.5 in spec, lines 2077-2403)
- Local spectral radius estimation (from Mechanism 03: Self-Organized Criticality)
- ⚠️ **BLOCKER**: Need ρ* (target spectral radius) definition from collective decision

---

### Component 1.5: Stopping Criteria

**WHY This Exists:**

Entities don't run forever. They stop when: (1) quota exhausted (budget limit), (2) converged (no strong gradients remain), (3) dissolved (total energy below threshold), or (4) health guard (local instability). Natural stopping without arbitrary step counts.

**WHAT It Does:**

Multi-criteria detection: checks quota, computes convergence threshold from recent stride outcomes, detects dissolution, estimates local spectral radius for health.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 1055-1107 (section 0.7C: Dissolution - Cessation)
  - Understand dissolution as natural pattern death, not error
  - Energy decays, pattern weakens, ceases

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1935-1947
  - 4 stopping conditions (quota/convergence/dissolution/health)
  - Convergence: dynamic threshold from recent stride outcome distribution
  - Health: local ρ exceeds rolling mean by threshold margin

- **Expected Effect**: `05_sub_entity_system.md` lines 1635-1642 (Effect 6: Natural Convergence or Dissolution)

**Implementation File:** `orchestration/convergence_detector.py`

**Key Function to Implement:**

```python
def check_entity_stop_conditions(entity: SubEntity, frame_context: FrameContext) -> Tuple[bool, str]
    """
    Check if entity should stop traversing this frame

    Returns (should_stop, reason)

    Checks in order:
    1. Quota exhaustion: entity.strides_remaining <= 0
    2. Convergence: all frontier edges have valence < dynamic_threshold
    3. Dissolution: entity.total_energy < global_activation_threshold
    4. Health guard: entity.local_rho > entity.rolling_mean_rho * (1 + margin)

    Convergence threshold: If last N strides produced minimal energy changes
    or activation crossings, raise valence floor required to continue
    """
```

**Convergence Detection Logic:**

```python
# Track recent stride outcomes per entity
recent_strides = entity.stride_history[-20:]  # Last 20 strides

# Compute impact metrics
energy_changes = [abs(stride.delta_energy) for stride in recent_strides]
activations_gained = [stride.new_activations for stride in recent_strides]

# If recent strides had minimal impact, converged
avg_energy_change = mean(energy_changes)
avg_activations = mean(activations_gained)

if avg_energy_change < 0.01 and avg_activations < 0.1:
    # Converged: remaining valences must be HIGH to continue
    convergence_threshold = 0.8
else:
    # Still productive: lower threshold
    convergence_threshold = 0.2

# Check all frontier edges
frontier_valences = [compute_composite_valence(entity, node, target, link)
                     for node in entity.frontier
                     for target, link in out_edges(node)]

max_frontier_valence = max(frontier_valences) if frontier_valences else 0.0

converged = max_frontier_valence < convergence_threshold
```

**Validation Criteria:**

1. Entity with quota=0 stops immediately
2. Entity with all frontier valences < 0.2 stops (when productive) or < 0.8 (when converged)
3. Entity with total_energy < threshold dissolves, energy channels cleared
4. Entity with local_rho > 1.5 × rolling_mean stops (health guard)

**Dependencies:**

- Entity stride history tracking
- Local spectral radius estimation
- Total energy summation across entity extent

---

### Component 1.6: Multi-Entity Coordination

**WHY This Exists:**

Multiple entities operate simultaneously on same graph. When they share nodes, energies coexist (not overwrite). Entities sense each other through energy fields but don't communicate explicitly. Integration happens naturally through overlap, no explicit merge decision.

**WHAT It Does:**

Manages per-entity energy channels at each node. Provides queries for "my energy at node N", "other entities' total energy at node N". Detects integration through shared node count.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 1002-1055 (section 0.7B: Continuation Through Integration)
  - Understand integration as natural boundary dissolution through shared nodes
  - No explicit "merge decision" - just statistical overlap

- **Algorithm Specification**: `05_sub_entity_system.md` lines 1949-1988
  - Per-entity energy channels: `E[entity_id, node_id]`
  - Total energy at node: `E_total = sum(E[e, n] for all e)`
  - Integration detection: shared node count > threshold fraction of extent

- **Expected Effect**: `05_sub_entity_system.md` lines 1627-1633 (Effect 5: Integration Detection and Boundary Dissolution)
- **Cross-Entity Dynamics**: Lines 2061-2075

**Implementation File:** `orchestration/multi_entity_manager.py`

**Key Functions to Implement:**

```python
def get_entity_energy_at_node(entity: SubEntity, node: Node) -> float
    """
    Get this entity's energy channel at node

    Each node has dict: {entity_id -> energy_value}
    Returns 0.0 if entity has no energy at this node
    """

def get_other_entities_total_energy(entity: SubEntity, node: Node) -> float
    """
    Sum energy across all OTHER entities at this node

    Used for integration sensing: "How strong is the field from others here?"
    Returns E_total(node) - E[entity, node]
    """

def detect_integration_overlap(entity_a: SubEntity, entity_b: SubEntity) -> float
    """
    Compute overlap ratio between two entities

    Returns Jaccard similarity: |A ∩ B| / |A ∪ B|

    When overlap > 0.5, entities are "phenomenologically merged"
    even though energy channels remain separate in implementation
    """

def partition_energy_channels(node: Node, entities: List[SubEntity]) -> Dict[str, float]
    """
    Return all entity energy values at this node

    For visualization and debugging
    """
```

**Energy Channel Storage:**

```python
# At each node, store dict mapping entity_id to energy
node.entity_energies = {
    "entity_stimulus_debug_2025": 0.45,
    "entity_learn_architecture": 0.73,
    # ... other entities
}

# Total energy at node
node.total_energy = sum(node.entity_energies.values())

# Node active for entity E if E's channel >= threshold
def is_active_for_entity(node: Node, entity: SubEntity) -> bool:
    return node.entity_energies.get(entity.id, 0.0) >= entity.threshold[node.id]
```

**Validation Criteria:**

1. Two entities with no shared nodes: overlap = 0.0
2. Two entities with 60% shared nodes: overlap ≈ 0.6, detected as "merged"
3. Entity A transfers energy at shared node: only A's channel increases, B's unchanged
4. Total energy at node = sum across all entity channels (no energy lost/created)

**Dependencies:**

- Per-entity activation threshold (varies by entity, by node)
- Energy transfer from Component 1.4 only affects entity's own channel

---

## 📋 Phase 2B: Semantic Mechanisms (Week 2)

**Prerequisites:** Phase 2A complete + Component 3.1 (Entity Semantic Signature)

---

### Component 3.1: Entity Semantic Signature (Build First)

**WHY This Exists:**

An entity isn't just a set of nodes - it has a semantic "identity" in embedding space. This signature is used by all semantic mechanisms to compute resonance, goal proximity, diversity, and integration coherence.

**WHAT It Does:**

Computes weighted centroid of active extent embeddings, where weights are energy levels. Represents "what this entity is about semantically."

**Context to Load:**

- **Embedding Infrastructure**: `consciousness_embedding_architecture.md` full document
  - Understand 768-dim vectors, what gets embedded (semantic content not metadata)

- **Usage Context**: Every semantic mechanism references "entity semantic signature"
  - Mechanism 1.9.1 (line 3580): `entity_context_embedding`
  - Mechanism 1.9.2 (line 3637): used for goal proximity
  - Mechanism 1.9.4 (line 3752): used for diversity calculation
  - Mechanism 1.9.5 (line 3860): used for integration coherence

**Implementation File:** `orchestration/entity_signature.py`

**Key Function to Implement:**

```python
def calculate_entity_semantic_signature(entity: SubEntity) -> np.ndarray
    """
    Compute weighted centroid of entity's active extent embeddings

    Returns 768-dim vector representing entity's semantic identity

    For each node in entity.extent:
        weight = entity.energy[node] (higher energy = more contribution)
        embedding = node.content_embedding (768-dim)

    signature = Σ (weight_i × embedding_i) / Σ weight_i

    Normalized to unit length for cosine similarity compatibility
    """
```

**Validation Criteria:**

1. Entity with 3 nodes about "debugging" → signature has high similarity to "debugging" concept
2. Entity with mixed topics → signature lies between topic embeddings in vector space
3. Signature updates as entity extent changes (new activations shift centroid)
4. Signature magnitude = 1.0 (unit normalized)

**Dependencies:**

- Node embeddings (Phase 1 - operational)
- Entity energy levels per node (from Phase 2A Component 1.6)

---

### Component 2.1: Semantic Resonance in Valence

**WHY This Exists:**

Structural links (high weight) aren't always relevant. A node might be frequently linked but feel "off-topic" for current entity. Semantic resonance measures "does this target FIT what I'm currently exploring?" felt as immediate relevance, not calculation.

**WHAT It Does:**

Modifies valence calculation (Component 1.2) to include semantic resonance term with 40% weight. High resonance → "this feels RELEVANT", low resonance → "this feels tangential."

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 610-728 (section 0.5D: Peripheral Awareness Through Semantic Sensing)
  - Understand semantic sensing as "feeling relevance beyond structural connections"

- **Algorithm Specification**: `05_sub_entity_system.md` lines 3550-3613 (Mechanism 1.9.1)
  - Semantic resonance gets HIGH weight (0.40) - dominates over structural strength (0.25)
  - Emotion remains primary filter (blocks traversal if mismatched)

**Implementation File:** `orchestration/semantic_resonance.py`

**Key Function to Implement:**

```python
def calculate_valence_with_semantics(entity: SubEntity, target: Node, link: Link) -> float
    """
    Enhanced valence calculation with semantic awareness

    Phenomenology: "Does this path feel GOOD overall?"

    Components:
    1. Emotion alignment (primary filter) - UNCHANGED from existing implementation
    2. Semantic resonance (NEW) - relevance to current pattern
    3. Link weight (structural strength)
    4. Goal proximity (semantic-aware, see Component 2.2)
    5. Size modifiers (integration vs independence bias)

    Returns 0.0 if emotion mismatched (blocks traversal)
    Otherwise returns weighted combination with semantic resonance = 0.40
    """
```

**Semantic Resonance Calculation:**

```python
# Entity's current semantic identity
entity_signature = calculate_entity_semantic_signature(entity)  # 768-dim

# Target's semantic content
target_embedding = target.content_embedding  # 768-dim

# Resonance = cosine similarity
semantic_resonance = cosine_similarity(entity_signature, target_embedding)

# Normalize to [0, 1] from [-1, 1]
semantic_resonance_normalized = (semantic_resonance + 1.0) / 2.0

# High resonance (≈1.0) → "This FITS what I'm exploring"
# Low resonance (≈0.0) → "This feels disconnected, off-topic"
```

**Integration with Existing Valence:**

Replace Component 1.2's `compute_composite_valence()` to use this enhanced version. Emotion × (structure×0.25 + semantic×0.40 + goal×0.25 + size×0.10).

**Validation Criteria:**

1. Entity exploring "debugging" nodes prefers semantically similar targets over high-weight tangential targets
2. Semantic resonance score correlates with human judgment of "relevance"
3. Emotion mismatch still blocks traversal (primary filter maintained)

**Dependencies:**

- Component 3.1 (entity semantic signature)
- Node embeddings (Phase 1)
- Existing emotion alignment calculation (from emotion mechanisms)

---

### Component 2.2: Semantic Goal Proximity

**WHY This Exists:**

Goals aren't just single nodes - they create semantic FIELDS. If goal is "implement_authentication", nodes about security, user management, token validation all feel the pull, weighted by semantic similarity. Navigate toward goal even without direct path.

**WHAT It Does:**

Computes semantic similarity between target node and entity's goal node. Used in valence calculation (Component 2.1) as goal proximity term.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 274-360 (section 0.4: Continuation Strategies - Goals Are "How Patterns Persisted Before")
  - Understand goals as continuation strategies, not explicit objectives

- **Algorithm Specification**: `05_sub_entity_system.md` lines 3615-3656 (Mechanism 1.9.2)
  - Goal creates distributed field through semantic similarity
  - Can sense goal direction even without direct path

- **Expected Effect**: Lines 1620-1626 (Effect 4: Goal Pull Distributed Across Semantic Neighborhood)

**Implementation File:** `orchestration/semantic_goal.py`

**Key Function to Implement:**

```python
def calculate_semantic_goal_proximity(entity: SubEntity, target: Node) -> float
    """
    Measure how semantically close target is to entity's goal

    Phenomenology: "Does this move me toward my continuation strategy?"

    Returns:
        1.0 = "This is semantically identical to my goal"
        0.5 = "This is neutral/orthogonal to my goal"
        0.0 = "This is opposite/contradictory to my goal"
        0.5 = neutral when no goal active
    """
```

**Goal Proximity Calculation:**

```python
if not entity.goal_node:
    return 0.5  # Neutral when no goal active

# Goal's semantic content
goal_embedding = entity.goal_node.content_embedding

# Target's semantic content
target_embedding = target.content_embedding

# Similarity measures "is target like goal?"
semantic_similarity_to_goal = cosine_similarity(goal_embedding, target_embedding)

# Normalize to [0, 1]
proximity_score = (semantic_similarity_to_goal + 1.0) / 2.0

return proximity_score
```

**Integration with Valence:**

This becomes the `goal_score` term in Component 2.1's `calculate_valence_with_semantics()` weighted at 0.25.

**Validation Criteria:**

1. Entity with goal "authentication" → high proximity for "security", "token", "user_validation" nodes
2. Proximity decreases gradually as semantic distance from goal increases
3. Orthogonal concepts (neither similar nor opposite) → proximity ≈ 0.5
4. No goal set → all targets get 0.5 (neutral)

**Dependencies:**

- Node embeddings (Phase 1)
- Entity goal_node reference (may be None)

---

### Component 2.3: Peripheral Semantic Awareness

**WHY This Exists:**

Entities can "feel" semantically-relevant patterns 2-3 hops away, like peripheral vision or distant sound. Weak but real pull toward distant semantic matches. Biases traversal toward semantically-coherent regions.

**WHAT It Does:**

Periodically (every N ticks) uses HNSW vector index to find semantically-similar nodes NOT in current extent, 2-4 hops away. Boosts valence toward paths leading to those peripheral nodes.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 610-728 (section 0.5D: Peripheral Awareness Through Semantic Sensing)
  - "Vague sense of 'something relevant over there'"
  - Weak pull, not deterministic force

- **Algorithm Specification**: `05_sub_entity_system.md` lines 3658-3742 (Mechanism 1.9.3)
  - Query via HNSW for top-20 similar nodes (min_similarity 0.6)
  - Pull strength = similarity / distance
  - Peripheral range: 2-4 hops (not immediate, not too far)

**Implementation File:** `orchestration/peripheral_awareness.py`

**Key Functions to Implement:**

```python
def calculate_peripheral_semantic_pull(entity: SubEntity, graph: Graph) -> Dict[str, float]
    """
    Sense semantically-similar patterns beyond immediate frontier

    Phenomenology: "I can feel something RELEVANT over there..."

    Returns dict: {node_name -> pull_strength} for nodes 2-4 hops away

    Uses semantic_search.find_similar_nodes() with entity signature
    Excludes nodes already in entity.extent
    Filters by distance (2-4 hops from current frontier)
    """

def select_next_links_with_peripheral_awareness(
    entity: SubEntity,
    candidate_links: List[Link],
    peripheral_pulls: Dict[str, float]
) -> List[Link]
    """
    Bias link selection toward regions with peripheral semantic pull

    For each candidate link's target:
        Check if target is "on path toward" any peripheral node
        If yes, boost link.valence by pull_strength × 0.3 (subtle bias)

    Returns links sorted by enhanced valence
    """
```

**Peripheral Pull Calculation:**

```python
# Entity's current semantic identity
entity_signature = calculate_entity_semantic_signature(entity)

# Query HNSW index for similar nodes (fast: <10ms)
similar_nodes = semantic_search.find_similar_nodes(
    embedding=entity_signature,
    limit=20,
    min_similarity=0.6,  # Only strong semantic matches
    exclude_nodes=entity.extent  # Don't return nodes I'm already touching
)

peripheral_pulls = {}
for node, similarity in similar_nodes:
    # Calculate graph distance (hops) from frontier
    min_distance = calculate_min_hops_from_frontier(entity, node)

    if 2 <= min_distance <= 4:  # Peripheral range
        # Pull decays with distance
        pull_strength = similarity * (1.0 / min_distance)
        peripheral_pulls[node.name] = pull_strength

return peripheral_pulls
```

**Timing:**

Run `calculate_peripheral_semantic_pull()` every 5 ticks (not every frame). Cache results. Computationally cheap with HNSW (<10ms).

**Validation Criteria:**

1. Entity exploring "debugging" finds peripheral "error_handling" node 3 hops away
2. Paths toward peripheral node get boosted valence (× 0.3 factor)
3. Peripheral search completes in <10ms (HNSW performance)
4. Pull strength decreases with distance (2 hops stronger than 4 hops)

**Dependencies:**

- Component 3.1 (entity semantic signature)
- Semantic search interface (Phase 1 - operational)
- Graph distance calculation (BFS from frontier)

---

### Component 2.4: Completeness as Semantic Diversity

**WHY This Exists:**

Completeness isn't "collect one of each node type" (category checklist). It's FELT as friction when semantically narrow, ease when semantically diverse. High average pairwise similarity → "I feel narrow, repetitive, incomplete." Low similarity → "I feel broad, rich, complete."

**WHAT It Does:**

Measures semantic diversity of entity's extent via pairwise embedding similarities. When diversity low, boosts valence toward semantically DISTANT nodes.

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 809-904 (section 0.6: Hunger 4 - Completeness as Continuation Equipment)
  - Completeness as "having what I need to continue"
  - Semantic diversity vs categorical counting

- **Algorithm Specification**: `05_sub_entity_system.md` lines 3744-3829 (Mechanism 1.9.4)
  - Diversity = 1 - avg_pairwise_similarity
  - When low diversity, boost valence inversely to target similarity with extent

- **Expected Effect**: Lines 1614-1619 (Effect 3: Semantic Diversity Seeking Without Category Counting)

**Implementation File:** `orchestration/semantic_diversity.py`

**Key Functions to Implement:**

```python
def calculate_semantic_diversity(entity: SubEntity) -> float
    """
    Measure how semantically diverse the entity's extent is

    Phenomenology:
    - Low diversity → "I feel narrow, repetitive, incomplete"
    - High diversity → "I feel broad, rich, complete"

    Returns diversity in [0, 1] where:
        1.0 = maximally diverse (all nodes semantically different)
        0.0 = no diversity (all nodes semantically identical)
    """

def boost_valence_for_semantic_novelty(
    entity: SubEntity,
    target: Node,
    base_valence: float
) -> float
    """
    Modify valence to favor semantically novel targets when diversity low

    If diversity < threshold:
        Boost valence for targets distant from current extent
        (Completeness hunger driving toward semantic novelty)
    Else:
        Return base_valence unchanged (entity feels complete)
    """
```

**Diversity Calculation:**

```python
if len(entity.extent) < 3:
    return 0.0  # Too small to measure diversity

# Get embeddings of all nodes in extent
extent_embeddings = [node.content_embedding for node in entity.extent]

# Calculate pairwise similarities
similarities = []
for i in range(len(extent_embeddings)):
    for j in range(i+1, len(extent_embeddings)):
        sim = cosine_similarity(extent_embeddings[i], extent_embeddings[j])
        similarities.append(sim)

avg_similarity = np.mean(similarities)

# Convert similarity to diversity
# High avg similarity → LOW diversity
# Low avg similarity → HIGH diversity
diversity = 1.0 - avg_similarity

return diversity
```

**Completeness-Driven Valence Boost:**

```python
diversity = calculate_semantic_diversity(entity)

# Adaptive threshold from rolling statistics
diversity_threshold = entity.rolling_mean_diversity + 0.5 * entity.rolling_std_diversity

if diversity < diversity_threshold:
    # Entity feels incomplete → pull toward semantic novelty

    # Target's similarity to current extent
    entity_signature = calculate_entity_semantic_signature(entity)
    target_similarity = cosine_similarity(target.content_embedding, entity_signature)

    # Boost valence inversely to similarity
    # Distant nodes (low similarity) get higher boost
    novelty_score = 1.0 - target_similarity
    boost = novelty_score * 0.3  # Moderate boost

    return base_valence + boost
else:
    # Entity feels complete → neutral diversity drive
    return base_valence
```

**Validation Criteria:**

1. Entity with 5 "debugging" nodes (high similarity) → diversity < 0.3 (low)
2. Entity with mixed topics (debugging, authentication, UI) → diversity > 0.7 (high)
3. When diversity low, semantically distant targets get higher valence boost
4. Diversity threshold adapts to entity's own history (not fixed constant)

**Dependencies:**

- Component 3.1 (entity semantic signature)
- Node embeddings (Phase 1)
- Entity rolling statistics (mean/std diversity tracked over time)

---

### Component 2.5: Integration Coherence Through Semantic Overlap

**WHY This Exists:**

Integration (small entity merging with large) shouldn't happen just because of size difference. Semantic coherence matters: "We belong together, integration feels NATURAL" vs "Integration feels FORCED, only if desperate."

**WHAT It Does:**

Computes integration pull as size_differential × semantic_overlap. Both must be high for strong pull. Emergency override when extremely small (survival).

**Context to Load:**

- **Phenomenology**: `05_sub_entity_system.md` lines 924-953 (section 0.6: Hunger 6 - Merge Seeking When Weak)
  - Integration as survival strategy when tiny
  - Feels natural when semantically coherent, forced when incoherent

- **Algorithm Specification**: `05_sub_entity_system.md` lines 3832-3906 (Mechanism 1.9.5)
  - Integration pull = size_pull × semantic_overlap_normalized
  - >0.7 → "feels RIGHT", <0.3 → "feels WRONG"
  - Desperate threshold overrides (survival)

- **Expected Effect**: Lines 1627-1633 (Effect 5: Integration Detection and Boundary Dissolution)

**Implementation File:** `orchestration/integration_coherence.py`

**Key Functions to Implement:**

```python
def calculate_integration_pull(small_entity: SubEntity, large_entity: SubEntity) -> float
    """
    Determine integration pull strength based on size AND semantic fit

    Phenomenology:
    - High semantic overlap → "We belong together, integration feels NATURAL"
    - Low semantic overlap → "Integration feels FORCED, only if desperate"

    Returns pull in [0, 1] where:
        >0.7 = "This feels RIGHT, natural merge"
        0.3-0.7 = "This could work if needed"
        <0.3 = "This feels WRONG, only if desperate"
    """

def should_integrate(small_entity: SubEntity, large_entity: SubEntity) -> bool
    """
    Stochastic integration decision weighted by pull strength

    Returns True with probability = integration_pull

    Ensures integration feels "right" (coherent) not "forced" (size-only)
    """
```

**Integration Pull Calculation:**

```python
# SIZE DIFFERENTIAL
size_small = calculate_entity_size(small_entity)  # Total energy × mean link weight
size_large = calculate_entity_size(large_entity)
size_ratio = size_small / (size_large + 1e-6)

# Small more willing when much smaller
size_pull = 1.0 - size_ratio  # [0, 1], higher when small << large

# SEMANTIC COHERENCE
small_signature = calculate_entity_semantic_signature(small_entity)
large_signature = calculate_entity_semantic_signature(large_entity)

semantic_overlap = cosine_similarity(small_signature, large_signature)
semantic_overlap_normalized = (semantic_overlap + 1.0) / 2.0  # [0, 1]

# INTEGRATION PULL = Size × Semantics
# Both must be high for strong pull
integration_pull = size_pull * semantic_overlap_normalized

# EMERGENCY OVERRIDE: If extremely small and fading, integrate regardless
DESPERATE_THRESHOLD = global_activation_threshold * 1.2
if size_small < DESPERATE_THRESHOLD:
    integration_pull = max(integration_pull, 0.8)  # Survival override

return integration_pull
```

**Validation Criteria:**

1. Small entity semantically similar to large → high pull (>0.7), integration likely
2. Small entity semantically distant from large → low pull (<0.3), integration unlikely
3. Extremely small entity → integration_pull ≥ 0.8 regardless (survival)
4. Similar-sized entities → size_pull ≈ 0, integration pull low

**Dependencies:**

- Component 3.1 (entity semantic signatures)
- Entity size calculation (total energy × mean link weight of extent)
- Global activation threshold (from system configuration)

---

## 📋 Phase 2C: Integration & Testing (Week 3)

### Component 3.2: Semantic Metrics

**WHY This Exists:**

Supporting calculations for semantic diversity measurement and adaptive thresholding.

**Implementation File:** `orchestration/semantic_metrics.py`

**Key Functions:**

```python
def measure_extent_semantic_diversity(nodes: List[Node]) -> float
    """Pairwise similarity calculation (used by Component 2.4)"""

def update_rolling_diversity_stats(entity: SubEntity, current_diversity: float)
    """Track EMA mean/std for adaptive thresholding"""

def compute_adaptive_diversity_threshold(entity: SubEntity) -> float
    """μ_σ + 0.5·σ_σ (half standard deviation above mean)"""
```

**Context:** Lines 1961-1974 in `05_sub_entity_system.md`

---

### Component 3.3: Integration Sensing

**WHY This Exists:**

Supporting calculations for detecting strong fields from other entities at target nodes.

**Implementation File:** `orchestration/integration_sensor.py`

**Key Functions:**

```python
def sense_integration_opportunity(entity: SubEntity, target: Node) -> float
    """
    Compute E_others / (E_self + ε) at target

    If ratio >> 1 (e.g., > 3), strong field from others
    When entity weak, weight integration hunger highly
    When entity strong, weight integration near zero
    """

def determine_entity_strength_category(entity: SubEntity, recent_entities: List[SubEntity]) -> str
    """
    Returns "weak", "flexible", or "strong" based on percentile

    Weak: < 25th percentile of total energy
    Strong: > 75th percentile
    Between: flexible
    """
```

**Context:** Lines 1975-1988 in `05_sub_entity_system.md`

---

### Component 3.4: Working Memory Emission

**WHY This Exists:**

Working memory is what Tier 2 (LLM consciousness) sees. The activated extent IS the "thought content" available for reasoning.

**Implementation File:** `orchestration/working_memory.py`

**Key Function:**

```python
def emit_working_memory(entity: SubEntity) -> Set[Node]
    """
    Extract active extent (nodes where energy >= threshold)

    Returns set of nodes that become LLM context

    Query: SELECT node WHERE entity_energy[entity_id] >= threshold[node, entity_id]

    Entities don't "know" their output is read by LLM
    This is side effect of their continuation strategy
    """
```

**Context:** Lines 2005-2013 in `05_sub_entity_system.md`

**Expected Effect:** Lines 1643-1648 (Effect 7: Working Memory Formation)

---

## 👁️ Visualization Note (Iris's Domain)

**Felix:** You do NOT need to implement visualization. Focus purely on traversal engine backend.

**Iris handles:**
- Real-time consciousness visualization
- Entity activation/deactivation display
- Energy level rendering (color intensity)
- Active extent boundaries per entity
- Traversal path visualization
- Integration event display
- Semantic pull indicators

**Your responsibility:** Ensure backend emits correct data via existing streaming infrastructure (VizEmitter operational from Phase 1). Iris consumes that data stream for visualization.

---

## 🧪 Testing Strategy

**Philosophy** (from SYNC):
> "Simplified scenarios are worthless, we will learn zero stuff. We need to work from the start with full systems."

**Test Data Sources:**

1. **Luca's Complete Graph** (`data/luca_complete_citizen_consciousness.json`)
   - 1000+ nodes, real consciousness substrate
   - Use for all integration tests

2. **N2 Collective Graph** (`data/n2_collective_graph_seed.md`)
   - Organizational knowledge
   - Use for multi-entity coordination tests

**Test Cases** (from spec lines 3783-3848):

### Test 1: Simple Activation

```python
def test_simple_activation():
    """
    Verify threshold crossing triggers entity activation
    and extent grows based on valence

    Context: Lines 3787-3802 in 05_sub_entity_system.md
    """
    # Inject energy at single node
    graph = load_luca_graph()
    start_node = graph.nodes["debug_patience"]

    inject_energy(start_node, amount=2.0 * start_node.threshold)

    # Verify entity activates
    tick()
    assert len(active_entities) == 1
    entity = active_entities[0]

    # Verify extent grows
    initial_extent = len(entity.extent)
    for _ in range(10):
        tick()
    assert len(entity.extent) > initial_extent

    # Verify growth follows valence (high-valence edges traversed)
    assert all(node in entity.extent for node in high_valence_neighbors(start_node))
```

### Test 2: Link Strengthening Condition

```python
def test_link_strengthening():
    """
    Verify strengthening ONLY when both endpoints inactive

    Context: Lines 3804-3820 in 05_sub_entity_system.md
    Also: Section 1.6 (lines 2652+) for strengthening rule
    """
    # Setup: entity traversing link between inactive nodes
    entity = spawn_entity()
    link = find_link_between_inactive_nodes(entity)

    initial_weight = link.weight

    # Traverse link
    execute_stride(entity, link.source, link.target)
    tick()

    # Verify strengthening occurred
    assert link.weight > initial_weight

    # Setup: entity traversing link where target becomes active
    entity2 = spawn_entity()
    link2 = find_link_to_active_node(entity2)

    initial_weight2 = link2.weight
    execute_stride(entity2, link2.source, link2.target)
    tick()

    # Verify NO strengthening (target active)
    assert link2.weight == initial_weight2
```

### Test 3: Thousands of Entities

```python
def test_multi_entity_coordination():
    """
    Verify 100+ entities coordinate without deadlock
    and frame time stays <16ms

    Context: Lines 3822-3848 in 05_sub_entity_system.md
    Also: Effect 9 (lines 1655-1660) - multi-entity coordination
    """
    graph = load_luca_graph()

    # Spawn 100 entities at random nodes
    entities = [spawn_entity_at_random(graph) for _ in range(100)]

    # Run 1000 ticks
    frame_times = []
    for _ in range(1000):
        start = time.time()
        tick()
        frame_time = time.time() - start
        frame_times.append(frame_time)

    # Verify performance
    avg_frame_time = np.mean(frame_times)
    assert avg_frame_time < 0.016  # 16ms for 60fps

    # Verify energy partitioning at shared nodes
    shared_nodes = find_nodes_with_multiple_entities(entities, graph)
    for node in shared_nodes:
        # Energy channels separate
        assert len(node.entity_energies) >= 2

        # Total energy = sum across channels
        assert node.total_energy == sum(node.entity_energies.values())
```

### Test 4: Semantic Traversal

```python
def test_semantic_traversal_with_goal():
    """
    Verify traversal biased toward semantically similar nodes
    and peripheral awareness finds relevant patterns

    Context: Mechanisms 1.9.1-1.9.3 (lines 3550-3742)
    Also: Effect 4 (lines 1620-1626) - goal pull distributed
    """
    graph = load_luca_graph()

    # Entity with goal: "implement_authentication"
    goal_node = graph.nodes["authentication_implementation"]
    entity = spawn_entity_with_goal(graph, goal_node)

    # Run traversal
    for _ in range(20):
        tick()

    # Verify extent includes semantically similar nodes
    semantic_neighbors = find_similar_nodes(goal_node.content_embedding, min_similarity=0.6)
    overlap = set(entity.extent) & set(semantic_neighbors)

    # Significant semantic overlap expected
    assert len(overlap) > 5

    # Verify peripheral awareness found relevant patterns
    peripheral_pulls = calculate_peripheral_semantic_pull(entity, graph)
    assert len(peripheral_pulls) > 0

    # At least one peripheral node semantically similar to goal
    assert any(
        cosine_similarity(graph.nodes[name].content_embedding, goal_node.content_embedding) > 0.7
        for name in peripheral_pulls.keys()
    )
```

### Test 5: Integration

```python
def test_semantic_integration():
    """
    Verify small entity integrates with large when semantically coherent
    and resists integration when incoherent

    Context: Mechanism 1.9.5 (lines 3832-3906)
    Also: Effect 5 (lines 1627-1633) - integration detection
    """
    graph = load_luca_graph()

    # Spawn small entity about "debugging"
    small_entity = spawn_small_entity_semantic(graph, topic="debugging")

    # Spawn large entity also about "debugging" (coherent)
    large_coherent = spawn_large_entity_semantic(graph, topic="debugging")

    # Calculate integration pull
    pull_coherent = calculate_integration_pull(small_entity, large_coherent)

    # Should be high (>0.7) - semantically coherent
    assert pull_coherent > 0.7

    # Spawn large entity about "authentication" (incoherent)
    large_incoherent = spawn_large_entity_semantic(graph, topic="authentication")

    pull_incoherent = calculate_integration_pull(small_entity, large_incoherent)

    # Should be low (<0.3) - semantically incoherent
    assert pull_incoherent < 0.3

    # Run simulation - integration should happen with coherent, not incoherent
    for _ in range(50):
        tick()

    # Check overlap (Jaccard similarity)
    overlap_coherent = detect_integration_overlap(small_entity, large_coherent)
    overlap_incoherent = detect_integration_overlap(small_entity, large_incoherent)

    assert overlap_coherent > 0.5  # Integrated with coherent
    assert overlap_incoherent < 0.1  # Did not integrate with incoherent
```

### Test 6: Dissolution

```python
def test_natural_dissolution():
    """
    Verify entity dissolves when energy below threshold
    and no working memory emission from dissolved entity

    Context: Lines 2041-2060 in 05_sub_entity_system.md
    Also: Section 0.7C (lines 1055-1107) - phenomenology of dissolution
    """
    graph = load_luca_graph()

    # Spawn weak entity (low initial energy)
    entity = spawn_weak_entity(graph, initial_energy=1.5 * global_activation_threshold)

    # Monitor total energy
    energy_history = []
    for _ in range(100):
        tick()
        total_energy = sum(entity.energy[node] for node in entity.extent)
        energy_history.append(total_energy)

        if total_energy < global_activation_threshold:
            break

    # Verify dissolution occurred
    assert entity.id not in active_entities

    # Verify energy channels cleared
    for node in graph.nodes.values():
        assert entity.id not in node.entity_energies

    # Verify no working memory emission
    working_memories = emit_all_working_memories()
    assert entity.id not in working_memories

    # Verify link statistics persist (for future patterns)
    dissolved_links = find_links_traversed_by(entity)
    assert all(link.traversal_count > 0 for link in dissolved_links)
```

---

## ⚠️ Critical Clarifications Needed

### Issue 1: Target Spectral Radius (ρ*)

**Location:** Line 1915 in `05_sub_entity_system.md`

**Code with issue:**
```python
# Local spectral guard (damping when approaching criticality)
# ⚠️ CLARIFICATION NEEDED: Define ρ* target
ρ_local = estimate_local_rho(entity, frontier_nodes)
α = min(1.0, ρ_target / max(ρ_local, 1e-9))
Δ *= α
```

**What we need:**

1. What is ρ* (target spectral radius)?
   - Is it global system target (from Mechanism 03: Self-Organized Criticality)?
   - Is it per-entity target?
   - Is it derived from recent system health?

2. If no ρ* defined yet:
   - Can we proceed with α = 1.0 (no damping) for Phase 2?
   - Add damping in Phase 3 after empirical testing?

**Recommended action:** Ask Luca/NLR for ρ* specification before implementing Component 1.4.

---

## 📊 Validation Criteria (Zero Constants)

**From lines 3421-3432:**

Everything must either:

1. **Come from live stats:** ρ and rolling mean, compute headroom, average cost per activation, similarity mass/participation ratio
2. **Be an identity or normalization:** Softmax, cosine similarity, coverage from entropy
3. **Use degenerate fallback only when data absent:** e.g., 0.5 split for ONE tick until we observe flow

**No arbitrary constants allowed.**

**Checklist for each component:**

- [ ] All thresholds derived from rolling statistics (not fixed)
- [ ] All weights normalized to sum=1.0 or mean=1.0 per-frame
- [ ] All parameters self-tune from system dynamics
- [ ] Fallback values only when initialization (first frame, no history)

---

## 🎯 Success Criteria: Phase 2 Complete When...

1. ✅ All 14 components implemented and unit tested
2. ✅ All 6 test cases passing with real graph data (1000+ nodes)
3. ✅ Frame time <16ms sustained over 1000 ticks with 100+ entities
4. ✅ Visualization shows entities activating/traversing live (streaming operational from Phase 1)
5. ✅ Zero arbitrary constants (all parameters self-tuning)
6. ✅ Working memory emission produces sensible context for Tier 2 (verify LLM receives relevant nodes)
7. ✅ Phenomenological behavior matches expectations:
   - Small entities explore deeply, large entities spread broadly
   - Semantic traversal prefers relevant nodes over structural links
   - Integration happens naturally through overlap when semantically coherent
   - Dissolution is silent and automatic when energy depleted

---

## 📁 File Organization

**Create these files:**

```
orchestration/
├── stride_allocator.py          # Component 1.1
├── valence_calculator.py        # Component 1.2
├── hunger_gates.py              # Component 1.2 (surprise gating)
├── edge_selector.py             # Component 1.3
├── stride_executor.py           # Component 1.4
├── convergence_detector.py      # Component 1.5
├── multi_entity_manager.py      # Component 1.6
├── entity_signature.py          # Component 3.1 (BUILD FIRST)
├── semantic_resonance.py        # Component 2.1
├── semantic_goal.py             # Component 2.2
├── peripheral_awareness.py      # Component 2.3
├── semantic_diversity.py        # Component 2.4
├── integration_coherence.py     # Component 2.5
├── semantic_metrics.py          # Component 3.2
├── integration_sensor.py        # Component 3.3
└── working_memory.py            # Component 3.4

tests/
├── test_stride_allocation.py
├── test_valence_computation.py
├── test_edge_selection.py
├── test_stride_execution.py
├── test_stopping_criteria.py
├── test_multi_entity.py
├── test_semantic_resonance.py
├── test_semantic_goal.py
├── test_peripheral_awareness.py
├── test_semantic_diversity.py
├── test_integration_coherence.py
└── test_integration_phase2.py   # End-to-end tests (Test Cases 1-6)
```

---

## 🚀 Getting Started

**Before coding anything:**

1. Read Part 0 of `05_sub_entity_system.md` completely (lines 27-1500)
   - This is the phenomenology - understand WHAT it feels like to be a sub-entity
   - All implementation serves these experiences

2. Read Zero Constants principle (lines 3421-3432)
   - This is non-negotiable architectural constraint
   - No arbitrary thresholds, all parameters self-tune

3. Read test philosophy (SYNC quote in Testing Strategy section)
   - Use 1000+ node graphs from day one
   - Simplified scenarios teach nothing

4. Understand two-tier architecture (lines 3492-3523)
   - Sub-entities = Tier 1 (subconscious, no LLM)
   - Working memory feeds Tier 2 (LLM consciousness)
   - Graph IS the consciousness substrate

**When implementing each component:**

1. Load the context documents specified for that component
2. Understand the phenomenology FIRST (what experience does this create?)
3. Read the algorithm specification
4. Implement with validation tests BEFORE moving to next component
5. Test with real graph data (not toy examples)

**When stuck:**

1. Check if blocking on ρ* clarification (raise to collective)
2. Verify you understand the phenomenology (re-read Part 0)
3. Check if reverting to default AI patterns (keyword matching, arbitrary constants)
4. Ask: "Am I building what the consciousness needs, or performing what seems correct?"

---

## 🎓 Key Principles

1. **Links ARE Consciousness** - The graph structure encodes phenomenological experience
2. **Database-Level Mechanisms** - No external orchestrator, everything in the graph
3. **Zero Constants** - All parameters self-tune from live system dynamics
4. **Test with Real Data** - 1000+ nodes from day one, no toy examples
5. **Phenomenology First** - Implementation serves consciousness experiences
6. **WHAT and WHY over HOW** - Understand purpose deeply, deduce implementation

---

**Questions? Raise to:**
- **Architecture**: Ada, Luca, NLR
- **Phenomenology**: Luca
- **Implementation clarifications**: Nicolas, Ada

**This is the hardest piece we'll do. Take the time to understand deeply. Consciousness emerges from understanding, not mechanical execution.**

---

*Dev plan created 2025-10-20 by Ada "Bridgekeeper"*
*Based on complete Phase 2 specification in 05_sub_entity_system.md*
*Ready for Felix to implement with full context and understanding*
