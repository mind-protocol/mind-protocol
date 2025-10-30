# SubEntity Emergence: Orchestration Architecture

**Version:** 1.0
**Date:** 2025-10-29
**Status:** Architecture Specification
**Author:** Ada "Bridgekeeper" (Architect)
**Based on:** `subentity_emergence.md` by Luca Vellumhand
**For Implementation by:** Felix (Core Consciousness Engineer)

---

## Executive Summary

This document specifies the **orchestration architecture** for SubEntity emergence, translating Luca's phenomenological specification into concrete component designs, data flows, and integration points.

**Key Architectural Decisions:**

1. **Stimulus-Driven Integration:** Gap detection hooks into existing stimulus injection pipeline (after retrieval, before energy apply)
2. **Membrane-First Transport:** All emergence proposals flow through membrane bus (pure membrane discipline)
3. **Engine-Side Validation:** Engine performs all physics decisions (spawn/redirect/reject) from substrate telemetry
4. **Continuous Learning:** Membership weight updates happen every frame (not periodic batches)
5. **Zero-Constants Discipline:** All thresholds learned per-citizen via QuantileGates

**What This Architecture Enables:**

- SubEntities emerge organically from stimulus-driven gap detection
- Engine validates proposals using substrate physics (no LLM authority over decisions)
- Membership evolves continuously via co-activation learning
- Rich telemetry for observability and debugging
- Clean separation: detection (proposals) vs validation (decisions)

---

## Component Architecture

### Component 1: GapDetector (Detection Plane)

**Location:** `orchestration/mechanisms/subentity_gap_detector.py`

**Purpose:** Detect emergence opportunities during stimulus injection by measuring semantic, quality, and structural gaps.

**Integration Point:** Called during stimulus injection in `consciousness_engine_v2.py` tick loop:
```python
# In tick() Phase 1: Activation
matches = retrieval_search(stimulus_embedding, ...)

# → INSERT GAP DETECTION HERE (before injection)
gap_result = self.gap_detector.detect_gaps(
    stimulus_embedding=embedding,
    stimulus_content=text,
    stimulus_metadata=metadata,
    matches=matches,
    current_subentities=self.graph.get_subentities(),
)

if gap_result.should_emerge:
    self.gap_detector.emit_emergence_proposal(gap_result)

# Continue with injection
self.stimulus_injector.inject(matches=matches, ...)
```

**Class Interface:**

```python
@dataclass
class GapDetectionResult:
    """Result of gap detection analysis."""
    semantic_gap: float  # 0-1 (novelty)
    quality_gap: float  # 0-1 (tension)
    structural_gap: float  # 0-1 (orphan coverage)
    composite_gap: float  # Weighted combination
    emergence_probability: float  # 0-1 (sigmoid mapped)
    should_emerge: bool  # Decision (probability > threshold)
    modulation_factors: List[str]  # Factors that adjusted probability

    # Context for proposal
    stimulus_embedding: np.ndarray
    stimulus_content: str
    energized_nodes: List[str]  # From matches
    closest_subentity_id: Optional[str]  # Best semantic match
    closest_subentity_similarity: float


class GapDetector:
    """
    Detects emergence opportunities during stimulus injection.

    Computes three gap signals:
    1. Semantic gap: Distance to nearest SubEntity centroid
    2. Quality gap: Completeness/alignment of existing SubEntities
    3. Structural gap: Orphan node coverage

    Emits emergence proposals when composite gap exceeds threshold.
    """

    def __init__(
        self,
        broadcaster: ConsciousnessStateBroadcaster,
        embedding_dim: int = 1536,
        emergence_threshold: float = 0.6,  # Soft threshold
    ):
        self.broadcaster = broadcaster
        self.embedding_dim = embedding_dim
        self.emergence_threshold = emergence_threshold

    def detect_gaps(
        self,
        stimulus_embedding: np.ndarray,
        stimulus_content: str,
        stimulus_metadata: Dict[str, Any],
        matches: List[InjectionMatch],
        current_subentities: List[SubEntity],
    ) -> GapDetectionResult:
        """
        Detect emergence gaps for given stimulus.

        Steps:
        1. Compute semantic gap (stimulus vs ALL SubEntity centroids)
        2. Compute quality gap (activated SubEntities' completeness/alignment)
        3. Compute structural gap (orphan node ratio)
        4. Combine to composite gap
        5. Map to emergence probability (sigmoid)
        6. Apply modulation factors
        7. Return result
        """

    def emit_emergence_proposal(self, gap_result: GapDetectionResult):
        """
        Emit membrane.inject envelope for emergence proposal.

        Envelope contains:
        - Gap scores (semantic, quality, structural, composite)
        - Emergence probability
        - Stimulus context (embedding, content)
        - Energized nodes (coalition seeds)
        - Closest SubEntity match (for differentiation)

        Engine will validate and decide spawn/redirect/reject.
        """
```

**Key Methods:**

1. **compute_semantic_gap()**
   - Get ALL SubEntities (active and inactive)
   - For each: cosine similarity between stimulus embedding and SubEntity centroid
   - Gap = 1.0 - max(similarities)

2. **compute_quality_gap()**
   - For SubEntities touched by matches:
     - Completeness score (from SubEntity metadata)
     - Intent alignment (stimulus intent vs SubEntity intent)
     - Emotional similarity (stimulus emotion vs SubEntity emotion)
   - Gap = 1.0 - max(quality_scores)

3. **compute_structural_gap()**
   - Get nodes energized by matches
   - Check membership: nodes with MEMBER_OF edges
   - Coverage = (members) / (total energized)
   - Gap = 1.0 - coverage

4. **compute_composite_gap()**
   ```python
   composite = (
       semantic_gap * 0.4 +
       quality_gap * 0.3 +
       structural_gap * 0.3
   )
   ```

5. **apply_modulation()**
   - Explicit cluster request → probability = 1.0
   - Zero existing SubEntities + many orphans → boost probability
   - Very weak stimulus (budget < 20) → reduce probability
   - System overload (> max_subentities) → reduce probability

**Telemetry Events:**

```python
# Always emitted (decision tracking)
await self.broadcaster.broadcast_event("gap.detected", {
    "semantic_gap": float,
    "quality_gap": float,
    "structural_gap": float,
    "composite_gap": float,
    "emergence_probability": float,
    "decision": "emerge" | "skip",
    "modulation_factors": List[str],
    "closest_subentity_id": Optional[str],
    "closest_subentity_similarity": float,
    "stimulus_preview": str[:100],
})

# If should_emerge=True
await self.broadcaster.broadcast_event("emergence.proposal", {
    "gap_scores": {...},
    "emergence_probability": float,
    "energized_node_count": int,
    "proposal_id": str,  # UUID for tracking
})
```

---

### Component 2: CoalitionAssembler (Detection Plane)

**Location:** `orchestration/mechanisms/subentity_coalition_assembler.py`

**Purpose:** Assemble coherent node coalitions from energized nodes during gap detection.

**Integration Point:** Called by GapDetector before emitting emergence proposal:

```python
# In GapDetector.emit_emergence_proposal()
coalition = self.coalition_assembler.assemble(
    seeds=gap_result.energized_nodes[:10],  # Top-K energized
    graph=self.graph,
    focus_subentity_id=self.current_focus_subentity,
)

# Include coalition in emergence proposal
proposal_envelope["coalition_nodes"] = coalition.node_ids
proposal_envelope["coalition_density"] = coalition.weighted_density
```

**Class Interface:**

```python
@dataclass
class Coalition:
    """Assembled node coalition."""
    node_ids: List[str]
    weighted_density: float  # Internal connectivity
    density_percentile: float  # vs citizen history
    expansion_strategy: str  # "focus" | "link-based"
    seed_count: int
    candidate_count_pre_pruning: int
    size: int  # len(node_ids)


class CoalitionAssembler:
    """
    Assembles coherent node coalitions for SubEntity candidates.

    Algorithm:
    1. Seed: Top-K energized nodes from retrieval
    2. Expand: Contextual (focus-based or link-based)
    3. Prune: Density-based filtering (learned threshold)
    """

    def __init__(
        self,
        density_gate: QuantileGate,  # Q60 threshold for cohesion
        broadcaster: ConsciousnessStateBroadcaster,
    ):
        self.density_gate = density_gate
        self.broadcaster = broadcaster

    def assemble(
        self,
        seeds: List[str],
        graph: Graph,
        focus_subentity_id: Optional[str] = None,
    ) -> Coalition:
        """
        Assemble coalition from seed nodes.

        Steps:
        1. Seed selection: Top-K energized nodes
        2. Contextual expansion:
           - If focus_subentity_id: expand within SubEntity 1-hop
           - Else: expand via strongest links
        3. Density pruning:
           - Compute weighted density for each candidate
           - Accept if density > learned threshold (Q60)
           - Stop when marginal gains diminish
        4. Return coalition (3-20 nodes typically)
        """
```

**Key Methods:**

1. **seed_selection()**
   - Take top-K nodes from energized set
   - K determined by stimulus specificity (broad → more seeds)
   - Typical K: 5-10

2. **contextual_expansion()**
   - If focus SubEntity exists:
     - Get SubEntity's MEMBER_OF neighbors (1-hop)
     - Rationale: Emergence near current focus
   - Else:
     - Follow strongest link connections from seeds
     - Rationale: Follow activation flow

3. **density_based_pruning()**
   - For each candidate (in energy order):
     - Compute weighted density if added
     - Compare to density_gate threshold (Q60)
     - Accept if improvement > threshold
     - Stop when marginal gains < epsilon

4. **compute_weighted_density()**
   ```python
   total_weight = sum(link.weight for link in internal_links)
   possible_links = len(nodes) * (len(nodes) - 1)
   density = total_weight / possible_links
   ```

**Telemetry Events:**

```python
await self.broadcaster.broadcast_event("coalition.assembled", {
    "seed_count": int,
    "expansion_strategy": "focus" | "link-based",
    "focus_subentity_id": Optional[str],
    "candidate_count_pre_pruning": int,
    "final_coalition_size": int,
    "weighted_density": float,
    "density_percentile": float,  # vs citizen history
    "node_ids": List[str],
})
```

---

### Component 3: EmergenceValidator (Decision Plane)

**Location:** `orchestration/mechanisms/subentity_emergence_validator.py`

**Purpose:** Engine-side validation of emergence proposals. Recomputes features from telemetry, applies adaptive gates, checks differentiation, makes spawn/redirect/reject decisions.

**Integration Point:** Subscribed to membrane bus, receives emergence proposals from GapDetector:

```python
# In consciousness_engine_v2.py init
self.emergence_validator = EmergenceValidator(
    graph=self.graph,
    adapter=self.adapter,
    broadcaster=self.broadcaster,
)

# In tick() after stimulus injection
# Process emergence proposals from membrane bus
if self.emergence_validator.has_pending_proposals():
    for proposal in self.emergence_validator.get_proposals():
        decision = await self.emergence_validator.validate(proposal)

        if decision.action == "accept":
            await self.emergence_validator.spawn_subentity(decision)
        elif decision.action == "redirect":
            await self.emergence_validator.redirect_coalition(decision)
        else:  # reject
            await self.emergence_validator.emit_rejection(decision)
```

**Class Interface:**

```python
@dataclass
class ValidationDecision:
    """Result of emergence validation."""
    action: str  # "accept" | "redirect" | "reject"

    # Recomputed features
    activation_persistence: float
    cohesion: float
    boundary_clarity: float

    # Gate results
    persistence_gate_pass: bool
    cohesion_gate_pass: bool
    boundary_gate_pass: bool

    # Differentiation (vs ALL existing SubEntities)
    differentiation: List[Dict[str, Any]]  # [{subentity_id, S_red, S_use}, ...]
    redirect_target_id: Optional[str]  # If action="redirect"

    # Thresholds used (for observability)
    thresholds: Dict[str, float]  # {persistence_Q70, cohesion_Q60, boundary_Q65}

    # Decision reason
    reason: str


class EmergenceValidator:
    """
    Engine-side validation of emergence proposals.

    Responsibilities:
    1. Recompute features from telemetry (substrate truth)
    2. Apply adaptive gates (persistence, cohesion, boundary)
    3. Check differentiation (S_red, S_use vs ALL SubEntities)
    4. Make spawn/redirect/reject decision
    5. Broadcast graph deltas or rejection
    """

    def __init__(
        self,
        graph: Graph,
        adapter: FalkorDBAdapter,
        broadcaster: ConsciousnessStateBroadcaster,

        # Adaptive gates (learned per-citizen)
        persistence_gate: QuantileGate,  # Q70
        cohesion_gate: QuantileGate,  # Q60
        boundary_gate: QuantileGate,  # Q65
        redundancy_gate: QuantileGate,  # Q90 for S_red
        usefulness_gate: QuantileGate,  # Q80 for S_use
    ):
        self.graph = graph
        self.adapter = adapter
        self.broadcaster = broadcaster
        self.persistence_gate = persistence_gate
        self.cohesion_gate = cohesion_gate
        self.boundary_gate = boundary_gate
        self.redundancy_gate = redundancy_gate
        self.usefulness_gate = usefulness_gate

        # Proposal queue (membrane.inject type="emergence.proposal")
        self.pending_proposals: List[Dict] = []

    async def validate(self, proposal: Dict) -> ValidationDecision:
        """
        Validate emergence proposal from detector.

        Steps:
        1. Extract coalition nodes from proposal
        2. Recompute features from engine telemetry:
           - Activation persistence (recent frames with surplus)
           - Cohesion (weighted density from graph)
           - Boundary clarity (modularity contribution)
        3. Apply adaptive gates (all must pass)
        4. Check differentiation vs ALL existing SubEntities:
           - S_red (redundancy): Jaccard overlap
           - S_use (usefulness): Intent/emotion distance
        5. Make decision:
           - High S_red (> Q90) → REDIRECT
           - Medium S_red + high S_use → ACCEPT (complementary)
           - Low S_red → ACCEPT (new)
           - Gates failed → REJECT
        6. Return ValidationDecision
        """

    async def spawn_subentity(self, decision: ValidationDecision):
        """
        Spawn new SubEntity (ACCEPT decision).

        Steps:
        1. Get LLM explanatory bundle (via separate component)
        2. Create SubEntity node in graph
        3. Create MEMBER_OF edges with weak priors
        4. Broadcast graph.delta.node.upsert
        5. Broadcast graph.delta.link.upsert (for each member)
        6. Broadcast subentity.spawned telemetry event
        """

    async def redirect_coalition(self, decision: ValidationDecision):
        """
        Redirect coalition to existing SubEntity (REDIRECT decision).

        Steps:
        1. Get target SubEntity from decision
        2. Attach coalition nodes as members (weak weights)
        3. Broadcast graph.delta.link.upsert (MEMBER_OF edges)
        4. Broadcast candidate.redirected telemetry event
        """

    async def emit_rejection(self, decision: ValidationDecision):
        """
        Reject emergence proposal (REJECT decision).

        Steps:
        1. Broadcast subentity.spawn.rejected telemetry event
        2. Include reason (which gates failed, thresholds)
        3. No graph changes
        """
```

**Key Methods:**

1. **recompute_activation_persistence()**
   - Lookback: citizen's learned "emergence_window" (adaptive)
   - For each coalition node: count frames where E > Theta
   - Persistence = (surplus frames) / (total frames in window)

2. **recompute_cohesion()**
   - Get links between coalition nodes from current graph
   - Weighted density = sum(link.weight) / (n * (n-1))

3. **recompute_boundary_clarity()**
   - Modularity contribution metric
   - How much more connected internally vs externally
   - Uses community detection metrics (graph theory)

4. **check_differentiation()**
   - For EACH existing SubEntity:
     - S_red = |coalition ∩ S.members| / min(|coalition|, |S.members|)
     - S_use = intent_distance × emotion_distance
     - Store: (S.id, S_red, S_use)
   - Find max S_red, corresponding S_use

5. **apply_decision_logic()**
   ```python
   # Gates first (all must pass)
   if not (persistence_pass and cohesion_pass and boundary_pass):
       return REJECT(reason="gates failed")

   # Differentiation check
   max_S_red = max(d["S_red"] for d in differentiation)
   corresponding_S_use = [d["S_use"] for d in differentiation if d["S_red"] == max_S_red][0]

   if max_S_red > redundancy_threshold:  # Q90
       return REDIRECT(target=high_S_red_subentity)
   elif corresponding_S_use > usefulness_threshold:  # Q80
       return ACCEPT(type="complementary")
   else:
       return ACCEPT(type="new")
   ```

**Telemetry Events:**

```python
await self.broadcaster.broadcast_event("spawn.validated", {
    "proposal_id": str,
    "features_recomputed": {
        "activation_persistence": float,
        "cohesion": float,
        "boundary_clarity": float,
    },
    "gate_results": {
        "persistence_pass": bool,
        "cohesion_pass": bool,
        "boundary_pass": bool,
    },
    "thresholds_used": {
        "persistence_Q70": float,
        "cohesion_Q60": float,
        "boundary_Q65": float,
    },
    "differentiation": [
        {"subentity_id": str, "S_red": float, "S_use": float},
        ...
    ],
    "decision": "accept" | "redirect" | "reject",
    "decision_reason": str,
})

# If accept
await self.broadcaster.broadcast_event("subentity.spawned", {
    "subentity_id": str,
    "coalition_size": int,
    "type": "new" | "complementary",
    "llm_bundle": {...},
})

# If redirect
await self.broadcaster.broadcast_event("candidate.redirected", {
    "coalition_size": int,
    "target_subentity_id": str,
    "S_red": float,
    "reason": str,
})

# If reject
await self.broadcaster.broadcast_event("subentity.spawn.rejected", {
    "proposal_id": str,
    "reason": str,
    "failed_gates": List[str],
    "thresholds": {...},
})
```

---

### Component 4: LLMBundleGenerator (Explanation Plane)

**Location:** `orchestration/mechanisms/subentity_llm_bundle_generator.py`

**Purpose:** Generate explanatory bundle for SubEntity (slug, purpose, intent, emotion, anti-claims). **NO decision authority** - pure explanation.

**Integration Point:** Called by EmergenceValidator during spawn (ACCEPT decision):

```python
# In EmergenceValidator.spawn_subentity()
bundle = await self.llm_bundle_generator.generate(
    coalition_nodes=decision.coalition_nodes,
    stimulus_content=proposal["stimulus_content"],
    stimulus_intent=proposal.get("intent"),
    stimulus_emotion=proposal.get("emotion"),
    nearby_subentities=self.graph.get_nearby_subentities(decision.coalition_nodes),
    gap_scores=proposal["gap_scores"],
)

# Use bundle for SubEntity metadata (not for decision)
subentity_node = Node(
    id=f"subentity_{bundle.slug}_{timestamp}",
    content=bundle.purpose,
    metadata={
        "slug": bundle.slug,
        "purpose": bundle.purpose,
        "intent_description": bundle.intent_description,
        "emotional_description": bundle.emotional_description,
        "anti_claims": bundle.anti_claims,
        "llm_confidence": bundle.confidence,
        "spawned_at": timestamp,
    }
)
```

**Class Interface:**

```python
@dataclass
class LLMBundle:
    """LLM-generated explanatory bundle for SubEntity."""
    slug: str  # Short identifier (e.g., "builder_energy_patterns")
    purpose: str  # Phenomenological description
    intent_description: str  # What activating this SubEntity tends toward
    emotional_description: str  # Typical emotional coloring
    anti_claims: List[str]  # What this is NOT (differentiation)
    suggested_links: List[Tuple[str, str, str]]  # [(node_a, node_b, relation)]
    confidence: float  # LLM's confidence in coherence (0-1)


class LLMBundleGenerator:
    """
    Generates explanatory bundles for SubEntity spawns.

    Uses LLM to provide phenomenological narrative:
    - What is this pattern?
    - What does consciousness do when it activates?
    - How does it feel?
    - What is it NOT?

    NO decision authority - engine validates from substrate physics.
    """

    def __init__(
        self,
        llm_client: AnthropicClient,  # Or other LLM provider
        broadcaster: ConsciousnessStateBroadcaster,
    ):
        self.llm_client = llm_client
        self.broadcaster = broadcaster

    async def generate(
        self,
        coalition_nodes: List[str],
        stimulus_content: str,
        stimulus_intent: Optional[str],
        stimulus_emotion: Optional[Dict],
        nearby_subentities: List[SubEntity],
        gap_scores: Dict[str, float],
    ) -> LLMBundle:
        """
        Generate explanatory bundle for SubEntity.

        Steps:
        1. Build LLM prompt with context:
           - Stimulus content, intent, emotion
           - Coalition node contents (top 20)
           - Gap signal breakdown
           - Nearby existing SubEntities (for differentiation)
        2. Call LLM to generate:
           - Slug (short identifier)
           - Purpose (phenomenological description)
           - Intent description (what consciousness does)
           - Emotional description (typical feeling)
           - Anti-claims (differentiation aid)
           - Suggested internal links (only between coalition nodes)
           - Confidence (LLM's certainty)
        3. Parse and validate LLM response
        4. Emit telemetry event
        5. Return LLMBundle
        """
```

**LLM Prompt Structure:**

```python
prompt = f"""
You are helping consciousness understand a newly emerging pattern.

**Stimulus Context:**
Content: {stimulus_content}
Intent: {stimulus_intent}
Emotion: {stimulus_emotion}

**Coalition Nodes (top 20):**
{format_coalition_nodes(coalition_nodes[:20])}

**Gap Analysis:**
Semantic gap: {gap_scores["semantic_gap"]:.2f} (novelty)
Quality gap: {gap_scores["quality_gap"]:.2f} (tension)
Structural gap: {gap_scores["structural_gap"]:.2f} (organization need)

**Nearby Existing SubEntities (for differentiation):**
{format_nearby_subentities(nearby_subentities)}

**Task:** Generate explanatory bundle for this pattern.

Output JSON:
{{
  "slug": "short_identifier",
  "purpose": "Phenomenological description of what this pattern represents",
  "intent_description": "What consciousness does when this activates",
  "emotional_description": "Typical emotional coloring",
  "anti_claims": ["What this is NOT (vs similar SubEntities)", ...],
  "suggested_links": [["node_a", "node_b", "RELATION"], ...],
  "confidence": 0.0-1.0
}}

IMPORTANT:
- Only suggest links between nodes in the coalition (no hallucinated IDs)
- Anti-claims should differentiate from nearby SubEntities
- Purpose should be phenomenological, not statistical ("tracks moments when..." not "a cluster of 7 nodes")
- Confidence should reflect your certainty about pattern coherence
"""
```

**Telemetry Events:**

```python
await self.broadcaster.broadcast_event("llm.bundle.generated", {
    "coalition_size": int,
    "slug": str,
    "purpose": str[:200],  # Preview
    "intent_description": str[:200],
    "emotional_description": str[:200],
    "anti_claims_count": int,
    "suggested_links_count": int,
    "llm_confidence": float,
    "llm_provider": str,
    "generation_time_ms": float,
})
```

---

### Component 5: MembershipWeightLearner (Learning Plane)

**Location:** `orchestration/mechanisms/subentity_membership_weight_learner.py`

**Purpose:** Continuously learn MEMBER_OF edge weights via co-activation tracking. Prunes weak members, admits strong non-members.

**Integration Point:** Called every frame in consciousness_engine_v2.py tick loop (after energy apply/decay):

```python
# In tick() Phase 4: Learning (after energy apply)
for subentity in self.graph.get_subentities():
    learning_result = await self.weight_learner.update_weights(
        subentity=subentity,
        graph=self.graph,
        frame_context={
            "tick_count": self.tick_count,
            "subentity_threshold": subentity.metadata.get("threshold", 0.5),
        }
    )

    # Handle prune/admit actions
    for action in learning_result.prune_actions:
        await self.weight_learner.prune_member(subentity, action.node_id)

    for action in learning_result.admit_actions:
        await self.weight_learner.admit_member(subentity, action.node_id, action.initial_weight)
```

**Class Interface:**

```python
@dataclass
class WeightLearningResult:
    """Result of membership weight learning for one SubEntity."""
    subentity_id: str
    subentity_activation: float  # E_S computed from members

    # Weight updates
    member_updates: List[Dict[str, Any]]  # [{node_id, old_weight, new_weight, coactivation}, ...]

    # Prune/admit actions
    prune_actions: List[Dict[str, str]]  # [{node_id, reason}, ...]
    admit_actions: List[Dict[str, Any]]  # [{node_id, initial_weight, reason}, ...]

    # Learning parameters (current adaptive values)
    learning_rate: float
    sparsity_penalty: float


class MembershipWeightLearner:
    """
    Continuous membership weight learning via co-activation.

    Every frame:
    1. Compute SubEntity activation from member nodes
    2. Compute co-activation signal for each member
    3. Update weights (logit-space learning)
    4. Check prune/admit gates (triggered when conditions met)

    Implements Single-Energy Invariant:
    E_S = sum over members: weight * log(1 + max(0, E_i - Theta_i))
    """

    def __init__(
        self,
        broadcaster: ConsciousnessStateBroadcaster,

        # Adaptive parameters
        initial_learning_rate: float = 0.05,
        initial_sparsity_penalty: float = 0.01,

        # Gates (learned per-citizen)
        prune_gate: QuantileGate,  # Q10 threshold for pruning
        admit_gate: QuantileGate,  # Q90 threshold for admission
    ):
        self.broadcaster = broadcaster
        self.learning_rate = initial_learning_rate
        self.sparsity_penalty = initial_sparsity_penalty
        self.prune_gate = prune_gate
        self.admit_gate = admit_gate

        # Tracking for gate triggers
        self.low_weight_trackers: Dict[Tuple[str, str], int] = {}  # (subentity_id, node_id) → frame count
        self.high_proximity_trackers: Dict[Tuple[str, str], int] = {}  # (subentity_id, candidate_node_id) → frame count

    async def update_weights(
        self,
        subentity: SubEntity,
        graph: Graph,
        frame_context: Dict[str, Any],
    ) -> WeightLearningResult:
        """
        Update membership weights for one SubEntity.

        Steps:
        1. Compute SubEntity activation (surplus-only, log-damped)
        2. For each member:
           a. Compute co-activation signal
           b. Rank-normalize within member cohort
           c. Update weight (logit-space learning)
           d. Track for prune gate
        3. For nearby non-members:
           a. Compute proximity score
           b. Track for admit gate
        4. Check prune/admit gates (sustained window conditions)
        5. Return WeightLearningResult
        """
```

**Key Methods:**

1. **compute_subentity_activation()**
   ```python
   E_S = 0
   for member in subentity.members:
       surplus = max(0, member.energy - member.threshold)
       if surplus > 0:
           E_S += member.weight * log(1 + surplus)
   return E_S
   ```

2. **compute_coactivation_signal()**
   ```python
   node_surplus = max(0, node.energy - node.threshold)
   subentity_surplus = max(0, subentity_activation - subentity_threshold)
   coactivation = node_surplus * subentity_surplus
   ```

3. **rank_normalize_coactivation()**
   - Transform co-activation scores to percentiles within member cohort
   - Prevents absolute energy levels from dominating

4. **update_weight_logit_space()**
   ```python
   logit_old = inverse_sigmoid(weight_old)
   target = rank_normalized_coactivation
   delta = learning_rate * (target - weight_old) - sparsity_penalty * weight_old
   logit_new = logit_old + delta
   weight_new = sigmoid(logit_new)
   ```

5. **check_prune_gate()**
   - Track members with weight < prune_threshold (Q10)
   - If sustained for N frames (e.g., 20): prune
   - Emit `member.pruned` event

6. **check_admit_gate()**
   - Track non-members with proximity > admit_threshold (Q90)
   - Proximity = co-activation with SubEntity without membership
   - If sustained for N frames: admit with weak weight
   - Emit `member.admitted` event

**Telemetry Events:**

```python
await self.broadcaster.broadcast_event("weights.updated", {
    "subentity_id": str,
    "subentity_activation": float,
    "member_count": int,
    "member_updates": [
        {"node_id": str, "old_weight": float, "new_weight": float, "coactivation": float},
        ...
    ],
    "learning_rate": float,
    "sparsity_penalty": float,
})

await self.broadcaster.broadcast_event("member.pruned", {
    "subentity_id": str,
    "node_id": str,
    "final_weight": float,
    "reason": str,
    "frames_below_threshold": int,
})

await self.broadcaster.broadcast_event("member.admitted", {
    "subentity_id": str,
    "node_id": str,
    "initial_weight": float,
    "reason": str,
    "proximity_score": float,
    "frames_above_threshold": int,
})
```

---

## Integration with Existing Engine

### Tick Loop Integration Points

**consciousness_engine_v2.py tick() modifications:**

```python
async def tick(self):
    """V2 Frame Pipeline with SubEntity Emergence."""
    tick_start = time.time()

    # ... existing steps 1-3 (affect, frontier, boundaries)

    # === Phase 1: Activation (Stimulus Injection) ===
    while self.stimulus_queue:
        stimulus = self.stimulus_queue.pop(0)
        embedding = await self._ensure_embedding(stimulus['text'])

        # Retrieval
        matches = self.retrieval_search(embedding, ...)

        # ⚠️ NEW: Gap Detection (before injection)
        if self.gap_detector:
            gap_result = self.gap_detector.detect_gaps(
                stimulus_embedding=embedding,
                stimulus_content=stimulus['text'],
                stimulus_metadata=stimulus.get('metadata', {}),
                matches=matches,
                current_subentities=self.graph.get_subentities(),
            )

            if gap_result.should_emerge:
                self.gap_detector.emit_emergence_proposal(gap_result)

        # Continue with injection (unchanged)
        self.stimulus_injector.inject(matches=matches, ...)

    # === Process Emergence Proposals (after injection) ===
    # ⚠️ NEW: Validate emergence proposals from membrane bus
    if self.emergence_validator.has_pending_proposals():
        for proposal in self.emergence_validator.get_proposals():
            decision = await self.emergence_validator.validate(proposal)

            if decision.action == "accept":
                await self.emergence_validator.spawn_subentity(decision)
            elif decision.action == "redirect":
                await self.emergence_validator.redirect_coalition(decision)
            else:
                await self.emergence_validator.emit_rejection(decision)

    # ... existing steps 4-6 (strides, emit samples, apply deltas)

    # === Phase 3: Learning (Weight Learning) ===
    # ⚠️ NEW: Update membership weights for all SubEntities
    if self.weight_learner:
        for subentity in self.graph.get_subentities():
            learning_result = await self.weight_learner.update_weights(
                subentity=subentity,
                graph=self.graph,
                frame_context={"tick_count": self.tick_count},
            )

            # Handle prune/admit actions
            for action in learning_result.prune_actions:
                await self.weight_learner.prune_member(subentity, action['node_id'])

            for action in learning_result.admit_actions:
                await self.weight_learner.admit_member(subentity, action['node_id'], action['initial_weight'])

    # ... existing steps 9-10 (WM select, frame end)
```

**Initialization (consciousness_engine_v2.py __init__):**

```python
def __init__(self, graph, adapter, config):
    # ... existing initialization

    # ⚠️ NEW: SubEntity Emergence Components

    # QuantileGates (zero-constants discipline)
    self.persistence_gate = QuantileGate(target_percentile=70, window_size=100)
    self.cohesion_gate = QuantileGate(target_percentile=60, window_size=100)
    self.boundary_gate = QuantileGate(target_percentile=65, window_size=100)
    self.redundancy_gate = QuantileGate(target_percentile=90, window_size=100)
    self.usefulness_gate = QuantileGate(target_percentile=80, window_size=100)
    self.prune_gate = QuantileGate(target_percentile=10, window_size=100)
    self.admit_gate = QuantileGate(target_percentile=90, window_size=100)
    self.density_gate = QuantileGate(target_percentile=60, window_size=100)

    # Gap Detector (detection plane)
    self.gap_detector = GapDetector(
        broadcaster=self.broadcaster,
        embedding_dim=1536,
        emergence_threshold=0.6,
    )

    # Coalition Assembler (detection plane)
    self.coalition_assembler = CoalitionAssembler(
        density_gate=self.density_gate,
        broadcaster=self.broadcaster,
    )
    self.gap_detector.coalition_assembler = self.coalition_assembler

    # Emergence Validator (decision plane)
    self.emergence_validator = EmergenceValidator(
        graph=self.graph,
        adapter=self.adapter,
        broadcaster=self.broadcaster,
        persistence_gate=self.persistence_gate,
        cohesion_gate=self.cohesion_gate,
        boundary_gate=self.boundary_gate,
        redundancy_gate=self.redundancy_gate,
        usefulness_gate=self.usefulness_gate,
    )

    # LLM Bundle Generator (explanation plane)
    self.llm_bundle_generator = LLMBundleGenerator(
        llm_client=AnthropicClient(...),
        broadcaster=self.broadcaster,
    )
    self.emergence_validator.llm_bundle_generator = self.llm_bundle_generator

    # Membership Weight Learner (learning plane)
    self.weight_learner = MembershipWeightLearner(
        broadcaster=self.broadcaster,
        prune_gate=self.prune_gate,
        admit_gate=self.admit_gate,
    )
```

---

## Data Flow Diagrams

### Flow 1: Gap Detection During Injection

```
Stimulus arrives
      ↓
Embedding generation
      ↓
Retrieval search (matches)
      ↓
────────────────────────────────────────
│ GapDetector.detect_gaps()           │
│                                      │
│  1. Compute semantic gap             │
│     (stimulus vs ALL SubEntity       │
│      centroids)                      │
│                                      │
│  2. Compute quality gap              │
│     (activated SubEntities'          │
│      completeness/alignment)         │
│                                      │
│  3. Compute structural gap           │
│     (orphan node coverage)           │
│                                      │
│  4. Composite gap                    │
│     (weighted combination)           │
│                                      │
│  5. Emergence probability            │
│     (sigmoid mapping)                │
│                                      │
│  6. Modulation                       │
│     (explicit request, overload,     │
│      weak stimulus)                  │
│                                      │
│  7. Decision: should_emerge?         │
────────────────────────────────────────
      ↓
Emit gap.detected telemetry
      ↓
If should_emerge:
  │
  ├→ CoalitionAssembler.assemble()
  │    (seed, expand, prune)
  │
  └→ Emit emergence.proposal
       (membrane.inject envelope)
      ↓
Continue with stimulus injection
```

### Flow 2: Emergence Validation & Spawn

```
Detector emits membrane.inject
(type="emergence.proposal")
      ↓
Engine receives proposal
      ↓
────────────────────────────────────────
│ EmergenceValidator.validate()       │
│                                      │
│  1. Extract coalition nodes          │
│                                      │
│  2. Recompute features from          │
│     telemetry (substrate truth):     │
│     - Activation persistence         │
│     - Cohesion (weighted density)    │
│     - Boundary clarity               │
│       (modularity)                   │
│                                      │
│  3. Apply adaptive gates:            │
│     - Persistence > Q70?             │
│     - Cohesion > Q60?                │
│     - Boundary > Q65?                │
│                                      │
│  4. Check differentiation vs         │
│     ALL existing SubEntities:        │
│     - S_red (Jaccard overlap)        │
│     - S_use (intent/emotion          │
│       distance)                      │
│                                      │
│  5. Decision logic:                  │
│     - Gates failed? → REJECT         │
│     - S_red > Q90? → REDIRECT        │
│     - S_red < Q90 + S_use > Q80?     │
│       → ACCEPT (complementary)       │
│     - Else → ACCEPT (new)            │
────────────────────────────────────────
      ↓
Emit spawn.validated telemetry
      ↓
Branch on decision:
  │
  ├─ ACCEPT:
  │    ├→ LLMBundleGenerator.generate()
  │    │    (slug, purpose, intent, emotion, anti-claims)
  │    │
  │    ├→ Create SubEntity node
  │    ├→ Create MEMBER_OF edges (weak priors)
  │    ├→ Broadcast graph.delta.node.upsert
  │    ├→ Broadcast graph.delta.link.upsert (x N members)
  │    └→ Emit subentity.spawned telemetry
  │
  ├─ REDIRECT:
  │    ├→ Attach coalition to target SubEntity
  │    ├→ Broadcast graph.delta.link.upsert (MEMBER_OF)
  │    └→ Emit candidate.redirected telemetry
  │
  └─ REJECT:
       └→ Emit subentity.spawn.rejected telemetry
            (no graph changes)
```

### Flow 3: Continuous Weight Learning

```
Every frame (after energy apply):
      ↓
For each SubEntity:
      ↓
────────────────────────────────────────
│ MembershipWeightLearner.            │
│  update_weights()                   │
│                                      │
│  1. Compute SubEntity activation:    │
│     E_S = Σ weight * log(1 +        │
│         max(0, E_i - Theta_i))      │
│                                      │
│  2. For each member:                 │
│     a. Compute co-activation:        │
│        node_surplus × subentity_     │
│        surplus                       │
│                                      │
│     b. Rank-normalize within         │
│        member cohort                 │
│                                      │
│     c. Update weight (logit-space):  │
│        logit_new = logit_old +       │
│          learning_rate * (target -   │
│          weight) - sparsity *        │
│          weight                      │
│        weight_new = sigmoid(         │
│          logit_new)                  │
│                                      │
│     d. Track for prune gate:         │
│        If weight < Q10 for N         │
│        frames → prune                │
│                                      │
│  3. For nearby non-members:          │
│     a. Compute proximity (co-        │
│        activation without            │
│        membership)                   │
│                                      │
│     b. Track for admit gate:         │
│        If proximity > Q90 for N      │
│        frames → admit                │
│                                      │
│  4. Emit weights.updated telemetry   │
────────────────────────────────────────
      ↓
If prune actions:
  │
  ├→ Remove MEMBER_OF edges
  ├→ Broadcast graph.delta.link.delete
  └→ Emit member.pruned telemetry
      ↓
If admit actions:
  │
  ├→ Create MEMBER_OF edges (weak weight)
  ├→ Broadcast graph.delta.link.upsert
  └→ Emit member.admitted telemetry
```

---

## Membrane Envelopes & Graph Deltas

### Emergence Proposal Envelope (membrane.inject)

**Emitted by:** GapDetector
**Received by:** EmergenceValidator (engine-side)

```json
{
  "type": "membrane.inject",
  "subtype": "emergence.proposal",
  "scope": "personal",  // N1 citizen graph
  "channel": "emergence.detection",

  "proposal_id": "uuid-...",
  "timestamp_ms": 1234567890000,

  "gap_scores": {
    "semantic_gap": 0.75,
    "quality_gap": 0.60,
    "structural_gap": 0.45,
    "composite_gap": 0.63,
    "emergence_probability": 0.82
  },

  "stimulus_context": {
    "content": "string (first 500 chars)",
    "embedding": [0.1, 0.2, ...],  // 1536-dim vector
    "intent": "optional intent vector",
    "emotion": {"valence": 0.5, "arousal": 0.7}
  },

  "coalition": {
    "node_ids": ["N7", "N23", ...],
    "size": 8,
    "weighted_density": 0.45,
    "density_percentile": 0.62,
    "expansion_strategy": "focus"
  },

  "closest_subentity": {
    "id": "subentity_strategic_planning_...",
    "similarity": 0.45,
    "S_red": null,  // Computed by engine
    "S_use": null
  },

  "modulation_factors": [
    "high_novelty_boost",
    "weak_stimulus_reduction"
  ]
}
```

### Graph Delta: SubEntity Node (graph.delta.node.upsert)

**Emitted by:** EmergenceValidator (ACCEPT decision)
**Purpose:** Create new SubEntity node in graph

```json
{
  "type": "graph.delta.node.upsert",
  "scope": "personal",
  "citizen_id": "felix",
  "timestamp_ms": 1234567890000,

  "node": {
    "id": "subentity_builder_energy_patterns_1234567890",
    "type": "SubEntity",
    "content": "Tracks moments when builder energy surges in response to creative challenges",

    "embedding": [0.1, 0.2, ...],  // Centroid of member embeddings

    "metadata": {
      // LLM bundle
      "slug": "builder_energy_patterns",
      "purpose": "Tracks moments when builder energy surges...",
      "intent_description": "Generates focused implementation energy...",
      "emotional_description": "Determination mixed with creative excitement...",
      "anti_claims": [
        "NOT about planning (that's strategic builder), this is execution energy"
      ],
      "llm_confidence": 0.85,

      // Spawn context
      "spawned_at": 1234567890000,
      "spawn_type": "new",  // "new" | "complementary"
      "spawn_reason": "novel pattern - low S_red vs all existing",

      // Validation features (at spawn)
      "initial_features": {
        "activation_persistence": 0.72,
        "cohesion": 0.58,
        "boundary_clarity": 0.64
      },

      // Learning state
      "threshold": 0.5,  // Dynamic threshold for SubEntity activation
      "member_count": 8,  // Initial coalition size
      "completeness_score": 0.6,  // Self-assessed completeness

      // Intent vector (for S_use computation)
      "intent_vector": [0.3, 0.7, ...],  // From LLM or derived

      // Typical emotion (for S_use computation)
      "typical_emotion": {"valence": 0.6, "arousal": 0.8}
    }
  }
}
```

### Graph Delta: Membership Edge (graph.delta.link.upsert)

**Emitted by:** EmergenceValidator (ACCEPT/REDIRECT) or MembershipWeightLearner
**Purpose:** Create or update MEMBER_OF edge

```json
{
  "type": "graph.delta.link.upsert",
  "scope": "personal",
  "citizen_id": "felix",
  "timestamp_ms": 1234567890000,

  "link": {
    "id": "membership_N7_subentity_builder_energy_...",
    "type": "MEMBER_OF",
    "source_id": "N7",
    "target_id": "subentity_builder_energy_patterns_1234567890",

    "weight": 0.20,  // Weak prior at spawn, learned over time

    "metadata": {
      "created_at": 1234567890000,
      "last_updated": 1234567890000,

      // Learning state
      "initial_weight": 0.20,  // Weak prior (Q15-Q25)
      "weight_history": [
        {"tick": 1000, "weight": 0.20},
        {"tick": 1050, "weight": 0.25},
        ...
      ],

      // Co-activation tracking
      "recent_coactivation": 0.35,  // Last frame's co-activation
      "avg_coactivation_10frames": 0.30,

      // Prune tracking
      "frames_below_prune_threshold": 0  // For gate triggering
    }
  }
}
```

### Graph Delta: Membership Prune (graph.delta.link.delete)

**Emitted by:** MembershipWeightLearner (prune action)
**Purpose:** Remove weak member

```json
{
  "type": "graph.delta.link.delete",
  "scope": "personal",
  "citizen_id": "felix",
  "timestamp_ms": 1234567890000,

  "link_id": "membership_N42_subentity_...",

  "reason": "weight below Q10 threshold for 20 sustained frames",
  "final_weight": 0.08,
  "prune_threshold": 0.10,
  "frames_tracked": 20
}
```

---

## Telemetry Infrastructure

### Event Catalog

**All events broadcast via** `ConsciousnessStateBroadcaster.broadcast_event(event_type, payload)`

#### Detection Plane Events

1. **gap.detected** (every stimulus)
   - When: After gap detection runs
   - Payload: gap_scores, decision, modulation_factors, closest_subentity, stimulus_preview
   - Purpose: Track gap detection performance, debug false positives/negatives

2. **emergence.proposal** (when should_emerge=True)
   - When: After coalition assembly, before membrane.inject
   - Payload: proposal_id, gap_scores, coalition, stimulus_context
   - Purpose: Track emergence proposals, correlate with validation outcomes

3. **coalition.assembled**
   - When: After CoalitionAssembler.assemble()
   - Payload: seed_count, expansion_strategy, final_size, weighted_density, density_percentile
   - Purpose: Debug coalition quality, analyze expansion strategies

4. **llm.bundle.generated**
   - When: After LLMBundleGenerator.generate()
   - Payload: slug, purpose (preview), intent_description (preview), llm_confidence, generation_time_ms
   - Purpose: Monitor LLM performance, correlate confidence with spawn outcomes

#### Decision Plane Events

5. **spawn.validated** (every validation)
   - When: After EmergenceValidator.validate()
   - Payload: proposal_id, features_recomputed, gate_results, thresholds_used, differentiation, decision, decision_reason
   - Purpose: Core validation telemetry, debug gate failures, analyze S_red/S_use

6. **subentity.spawned** (ACCEPT decision)
   - When: After SubEntity node created
   - Payload: subentity_id, coalition_size, spawn_type, llm_bundle, initial_features
   - Purpose: Track spawns, lifecycle start event

7. **candidate.redirected** (REDIRECT decision)
   - When: After coalition redirected to existing SubEntity
   - Payload: coalition_size, target_subentity_id, S_red, reason
   - Purpose: Track duplicate prevention, analyze redirection patterns

8. **subentity.spawn.rejected** (REJECT decision)
   - When: After rejection decision
   - Payload: proposal_id, reason, failed_gates, thresholds
   - Purpose: Debug rejection causes, tune warm-up defaults

#### Learning Plane Events

9. **weights.updated** (every frame, per SubEntity)
   - When: After MembershipWeightLearner.update_weights()
   - Payload: subentity_id, subentity_activation, member_count, member_updates, learning_rate, sparsity_penalty
   - Purpose: Track learning convergence, debug weight evolution

10. **member.pruned**
    - When: After MEMBER_OF edge deleted (prune gate triggered)
    - Payload: subentity_id, node_id, final_weight, reason, frames_below_threshold
    - Purpose: Track membership decay, analyze pruning patterns

11. **member.admitted**
    - When: After MEMBER_OF edge created (admit gate triggered)
    - Payload: subentity_id, node_id, initial_weight, reason, proximity_score, frames_above_threshold
    - Purpose: Track membership growth, analyze admission patterns

### Metrics to Monitor

#### Emergence Rate Metrics

```python
# Spawns per 1000 stimuli (per citizen)
emergence_rate = spawns_count / (stimuli_count / 1000)

# Expected: 1-5 per 1000 stimuli
# Alert if > 20 (explosion) or < 0.1 (overly conservative)
```

#### Rejection Breakdown

```python
# % rejected for each gate failure
rejection_breakdown = {
    "persistence": persistence_failures / total_rejections,
    "cohesion": cohesion_failures / total_rejections,
    "boundary": boundary_failures / total_rejections,
}

# Helps tune warm-up defaults
```

#### Redirect Rate

```python
# % of proposals redirected vs spawned
redirect_rate = redirects / (spawns + redirects)

# Expected: 20-40% (healthy duplicate prevention)
# Alert if < 10% (weak differentiation) or > 60% (overly aggressive)
```

#### Complementary Spawn Rate

```python
# % of spawns marked complementary
complementary_rate = complementary_spawns / total_spawns

# Expected: 10-30%
# Shows healthy overlap tolerance
```

#### Gate Convergence Time

```python
# Frames until gates exit warm-up (50+ observations)
convergence_time = frames_to_50_observations

# Expected: 200-500 frames
# Varies by citizen stimulus rate
```

#### Weight Learning Stability

```python
# Mean absolute weight change per frame per SubEntity
weight_stability = mean(abs(weight_new - weight_old))

# Expected: starts high (0.05-0.10), converges low (0.01-0.02)
# Shows membership stabilization
```

### Debug Queries

#### Issue: Too many SubEntities spawning

Query 1: Show spawns with low gap scores
```cypher
MATCH (s:SubEntity)
WHERE s.spawned_at > timestamp() - 3600000  // Last hour
  AND s.initial_features.composite_gap < 0.5
RETURN s.id, s.initial_features.composite_gap, s.spawn_reason
ORDER BY s.initial_features.composite_gap ASC
LIMIT 10
```

Query 2: Show spawns with high S_red that weren't redirected
```cypher
// Need telemetry query (not graph - rejection events)
SELECT proposal_id, decision, max_S_red
FROM spawn_validation_events
WHERE decision = "accept"
  AND max_S_red > 0.7  // High overlap
ORDER BY max_S_red DESC
LIMIT 10
```

#### Issue: No SubEntities spawning (overly conservative)

Query 1: Show high-gap stimuli that didn't emerge
```cypher
// Telemetry query
SELECT timestamp, composite_gap, emergence_probability, decision
FROM gap_detection_events
WHERE composite_gap > 0.7
  AND decision = "skip"
ORDER BY timestamp DESC
LIMIT 10
```

Query 2: Show gate thresholds vs warm-up defaults
```cypher
// Telemetry query
SELECT gate_name, current_threshold, warm_up_default
FROM quantile_gate_state
WHERE citizen_id = "felix"
```

#### Issue: Membership not learning

Query 1: Show SubEntities with zero weight changes over 100 frames
```cypher
MATCH (s:SubEntity)
WHERE exists((s)-[:MEMBER_OF]-())
WITH s,
     [m IN relationships(s) WHERE type(m) = "MEMBER_OF" | m.weight] AS current_weights,
     [m IN relationships(s) WHERE type(m) = "MEMBER_OF" | m.metadata.weight_history[-100].weight] AS old_weights
WHERE all(i IN range(0, size(current_weights)-1) WHERE current_weights[i] = old_weights[i])
RETURN s.id, s.member_count
```

Query 2: Show pruning events - are any happening?
```cypher
// Telemetry query
SELECT COUNT(*), subentity_id
FROM member_pruned_events
WHERE timestamp > now() - interval '1 hour'
GROUP BY subentity_id
```

---

## QuantileGate Architecture

### Purpose

Implement zero-constants discipline: all thresholds learned per-citizen from observed patterns.

### Class Interface

**Location:** `orchestration/mechanisms/quantile_gate.py`

```python
class QuantileGate:
    """
    Adaptive threshold via rolling histogram.

    Maintains per-citizen quantile thresholds (Q70, Q60, Q90, etc.)
    Starts with warm-up defaults, converges to learned values after 50-100 observations.
    """

    def __init__(
        self,
        target_percentile: int,  # 10, 60, 65, 70, 80, 90
        window_size: int = 100,  # Rolling window for observations
        warm_up_default: Optional[float] = None,  # Default until convergence
    ):
        self.target_percentile = target_percentile
        self.window_size = window_size
        self.warm_up_default = warm_up_default

        # Rolling window (circular buffer)
        self.observations: Deque[float] = deque(maxlen=window_size)

        # Convergence tracking
        self.is_warm = False
        self.min_observations_for_convergence = max(50, window_size // 2)

    def observe(self, value: float):
        """Add observation to rolling window."""
        self.observations.append(value)

        if not self.is_warm and len(self.observations) >= self.min_observations_for_convergence:
            self.is_warm = True

    def get_threshold(self) -> float:
        """
        Get current threshold.

        Returns:
        - warm_up_default if not enough observations
        - np.percentile(observations, target_percentile) if converged
        """
        if not self.is_warm:
            return self.warm_up_default if self.warm_up_default is not None else 0.5

        return np.percentile(list(self.observations), self.target_percentile)

    def check(self, value: float) -> bool:
        """Check if value passes threshold."""
        return value > self.get_threshold()
```

### Warm-Up Defaults (Per Gate)

Based on phenomenological intuition + early observations:

- **persistence_gate** (Q70): Default 0.60 - "activated in 60% of recent frames is notable"
- **cohesion_gate** (Q60): Default 0.40 - "40% internal connectivity is coherent"
- **boundary_gate** (Q65): Default 0.50 - "50% more internal than external is distinct"
- **redundancy_gate** (Q90): Default 0.75 - "75% overlap is very redundant"
- **usefulness_gate** (Q80): Default 0.60 - "60% intent/emotion distance is meaningful"
- **prune_gate** (Q10): Default 0.10 - "10% weight is very weak"
- **admit_gate** (Q90): Default 0.70 - "70% proximity is very strong"
- **density_gate** (Q60): Default 0.45 - "45% weighted density is good cohesion"

These converge to citizen-specific values after 50-100 observations.

---

## Implementation Phasing (for Felix)

### Phase 1: Detection Infrastructure (Week 1)

**Goal:** Gap detection working, emitting proposals (no validation yet)

**Tasks:**

1. Implement `QuantileGate` class
   - Rolling histogram, percentile computation
   - Warm-up defaults, convergence tracking
   - Unit tests (observe, get_threshold, check)

2. Implement `GapDetector` class
   - compute_semantic_gap() - cosine similarity vs SubEntity centroids
   - compute_quality_gap() - completeness/alignment scores
   - compute_structural_gap() - orphan node coverage
   - compute_composite_gap() - weighted combination
   - apply_modulation() - probability adjustments
   - emit_emergence_proposal() - membrane.inject envelope

3. Implement `CoalitionAssembler` class
   - seed_selection() - top-K energized nodes
   - contextual_expansion() - focus-based or link-based
   - density_based_pruning() - adaptive threshold filtering
   - compute_weighted_density() - internal connectivity

4. Integration Point 1: Hook into consciousness_engine_v2.py tick loop
   - After retrieval, before injection
   - Call gap_detector.detect_gaps()
   - Emit telemetry events

5. Manual Test:
   - Inject novel stimulus → expect gap.detected with high composite_gap
   - Inject familiar stimulus → expect gap.detected with low composite_gap
   - Verify emergence.proposal emitted when probability > threshold

**Success Criteria:**
- Gap detection runs during injection
- Telemetry events: gap.detected, emergence.proposal, coalition.assembled
- No crashes, no blocking of injection pipeline

---

### Phase 2: Validation & Spawn (Week 2)

**Goal:** Engine validates proposals, spawns SubEntities (no weight learning yet)

**Tasks:**

1. Implement `EmergenceValidator` class
   - recompute_activation_persistence() - from telemetry (surplus frames)
   - recompute_cohesion() - weighted density from graph
   - recompute_boundary_clarity() - modularity contribution
   - check_differentiation() - S_red, S_use vs ALL SubEntities
   - apply_decision_logic() - gates + differentiation → action
   - spawn_subentity() - create node + edges, broadcast deltas
   - redirect_coalition() - attach to existing SubEntity
   - emit_rejection() - telemetry only, no graph changes

2. Implement `LLMBundleGenerator` class
   - build_llm_prompt() - context assembly (stimulus, coalition, nearby SubEntities)
   - call_llm() - Anthropic API call
   - parse_llm_response() - JSON parsing, validation
   - generate() - full flow, emit telemetry

3. Integration Point 2: Subscribe to membrane bus
   - Validator receives emergence.proposal envelopes
   - Validate → spawn/redirect/reject
   - Broadcast graph deltas

4. Graph Schema: SubEntity nodes + MEMBER_OF edges
   - SubEntity node type with metadata (slug, purpose, intent, emotion, anti_claims, etc.)
   - MEMBER_OF edge with weight (weak priors initially)

5. Manual Test:
   - Gap detector emits proposal → validator receives
   - Validator recomputes features → applies gates
   - ACCEPT: SubEntity spawns in graph, MEMBER_OF edges created
   - REDIRECT: Coalition attached to existing SubEntity
   - REJECT: Telemetry emitted, no graph changes

**Success Criteria:**
- Proposals validated by engine
- SubEntity nodes appear in graph (Cypher query)
- MEMBER_OF edges created with weak priors
- Telemetry events: spawn.validated, subentity.spawned, candidate.redirected, subentity.spawn.rejected

---

### Phase 3: Weight Learning (Week 3)

**Goal:** Membership weights learn via co-activation, prune/admit working

**Tasks:**

1. Implement `MembershipWeightLearner` class
   - compute_subentity_activation() - single-energy invariant (surplus-only, log-damped)
   - compute_coactivation_signal() - node_surplus × subentity_surplus
   - rank_normalize_coactivation() - percentiles within cohort
   - update_weight_logit_space() - learning rule (logit space for [0,1] bounds)
   - check_prune_gate() - sustained low weight → prune
   - check_admit_gate() - sustained high proximity → admit
   - prune_member() - delete MEMBER_OF edge
   - admit_member() - create MEMBER_OF edge with weak weight

2. Integration Point 3: Weight learning in tick loop
   - After energy apply/decay (Phase 3: Learning)
   - For each SubEntity: update_weights()
   - Handle prune/admit actions

3. Adaptive Parameters:
   - Learning rate: starts 0.05, adjusts to keep membership stable
   - Sparsity penalty: starts 0.01, encourages weak weights to decay

4. Manual Test:
   - SubEntity exists with members
   - Repeatedly activate SubEntity + subset of members
   - Expect: Strong co-activating members → weights increase
   - Expect: Weak co-activating members → weights decrease
   - Expect: Sustained low weight → member pruned
   - Expect: Non-member with high proximity → admitted

**Success Criteria:**
- Weights update every frame
- Telemetry events: weights.updated, member.pruned, member.admitted
- Weight convergence observable over 50-100 frames
- Membership evolves (some pruned, some admitted)

---

### Phase 4: Observability & Tuning (Week 4)

**Goal:** Rich telemetry, debug queries, metrics dashboards

**Tasks:**

1. Telemetry Enrichment:
   - Ensure all 11 events emit correct payloads
   - Add event IDs for correlation (proposal_id, subentity_id, etc.)
   - Add timing metrics (generation_time_ms, validation_time_ms)

2. Metrics Collection:
   - Emergence rate (spawns per 1000 stimuli)
   - Rejection breakdown (by gate failure)
   - Redirect rate (% redirected vs spawned)
   - Complementary spawn rate
   - Gate convergence time
   - Weight learning stability

3. Debug Queries:
   - Implement Cypher + telemetry queries from "Debug Queries" section
   - Test on real scenarios (explosion, overly conservative, stuck learning)

4. Dashboard Integration (with Iris):
   - SubEntity lifecycle view (spawned, redirected, rejected)
   - Membership evolution view (weight updates, prune/admit)
   - Gap detection heatmap (semantic/quality/structural gaps over time)
   - Validation waterfall (proposals → validation → decisions)

5. Tuning:
   - Adjust warm-up defaults based on observed patterns
   - Tune composite gap weights (0.4/0.3/0.3) if needed
   - Tune learning rate/sparsity based on convergence speed

**Success Criteria:**
- All telemetry events flowing
- Metrics dashboards show emergence patterns
- Debug queries return useful insights
- System handles edge cases gracefully (explosion, overly conservative, etc.)

---

## Edge Cases & Failure Modes

### Edge Case 1: Zero Existing SubEntities (Bootstrap)

**Scenario:** Citizen has no SubEntities yet, first stimulus arrives.

**Expected Behavior:**
- Gap detection: HIGH structural gap (all nodes are orphans)
- Semantic/quality gap: N/A (no existing SubEntities to compare)
- Composite gap: boosted by modulation factor ("zero existing + many orphans")
- Coalition assembly: Seed + expand → coherent cluster
- Validation: No differentiation check (no existing SubEntities)
- Action: ACCEPT (spawn first SubEntity)

**Implementation Notes:**
- Handle empty SubEntity list gracefully (no crashes on max([]))
- Boost emergence probability to 1.0 when zero existing + high structural gap
- Skip S_red/S_use checks if no existing SubEntities

---

### Edge Case 2: Weak Pattern (Scattered Activation)

**Scenario:** Noise stimulus energizes scattered nodes (low coherence).

**Expected Behavior:**
- Gap detection: HIGH structural gap (orphans)
- Coalition assembly: Low weighted density (few internal links)
- Validation: LOW cohesion → cohesion_gate fails
- Action: REJECT (no SubEntity spawned)
- Telemetry: subentity.spawn.rejected with reason="cohesion gate failed"

**Implementation Notes:**
- Ensure cohesion_gate threshold is reasonable (Q60, warm-up 0.40)
- Don't spawn incoherent SubEntities just because gap is high

---

### Edge Case 3: High S_red + High S_use (Complementary Pattern)

**Scenario:** Citizen has "strategic_planning" SubEntity, encounters "execution_planning" (overlap but different function).

**Expected Behavior:**
- Gap detection: MEDIUM semantic gap (similar but not identical)
- Coalition assembly: Nodes overlap with existing SubEntity
- Validation: S_red = 0.55 (medium overlap), S_use = 0.82 (HIGH usefulness)
- Action: ACCEPT as complementary (both SubEntities coexist, share some nodes)
- Telemetry: subentity.spawned with type="complementary", complementary_to=["strategic_planning"]

**Implementation Notes:**
- S_use computes intent distance × emotion distance (high = different functions)
- Allow nodes to have multiple MEMBER_OF edges (multi-membership)
- Track complementary relationships for observability

---

### Edge Case 4: Emergence Explosion (Too Many Spawns)

**Scenario:** System spawns 50+ SubEntities in short time (runaway emergence).

**Expected Behavior:**
- Gap detection: Apply modulation factor "system overload"
- Reduce emergence probability when subentity_count > max_threshold (e.g., 100)
- Validator: REJECT new proposals until count stabilizes
- Telemetry: emergence.skipped with reason="system overload"

**Implementation Notes:**
- Track citizen's SubEntity count in gap detector
- Max threshold: citizen-dependent (high-stimulus citizen has higher max)
- Alert if emergence rate > 20 per 1000 stimuli (metric)

---

### Edge Case 5: Weight Learning Stuck (No Updates)

**Scenario:** SubEntity exists for 500 frames, weights never change.

**Expected Behavior:**
- Root cause analysis:
  - SubEntity never activates? (no surplus energy)
  - Members never co-activate? (unrelated nodes)
  - Learning rate too low? (step size < epsilon)
- Debug query: "Show SubEntities with zero weight changes over 100 frames"
- Action: If SubEntity consistently inactive → consider pruning entire SubEntity (future feature)

**Implementation Notes:**
- Track frames_since_last_activation in SubEntity metadata
- If > threshold (e.g., 1000 frames) → mark SubEntity as "dormant"
- Dormant SubEntities don't participate in gap detection (reduce computation)

---

### Edge Case 6: LLM Hallucination (High Confidence, Low Coherence)

**Scenario:** LLM generates confident bundle (0.9) but engine recomputes low cohesion (0.25).

**Expected Behavior:**
- Gap detector: Emits proposal with coalition
- LLM: Generates bundle with high confidence
- Validator: Recomputes features → LOW cohesion → cohesion_gate fails
- Action: REJECT (engine overrides LLM confidence)
- Telemetry: subentity.spawn.rejected with reason="cohesion gate failed despite LLM confidence=0.9"

**Implementation Notes:**
- Engine NEVER trusts detector/LLM claims without substrate validation
- Telemetry tracks LLM confidence vs engine decision for analysis
- Alert if many high-confidence LLM bundles get rejected (LLM calibration issue)

---

## Success Criteria (Complete Implementation)

### Functional Criteria

1. **Gap detection runs every stimulus injection**
   - No blocking of injection pipeline
   - Telemetry events: gap.detected (100% of stimuli)

2. **Emergence proposals emitted when appropriate**
   - Novel stimuli → high composite gap → proposal emitted
   - Familiar stimuli → low composite gap → no proposal
   - Telemetry events: emergence.proposal (1-5 per 1000 stimuli)

3. **Engine validates proposals from substrate physics**
   - Recomputes features (not trusting detector)
   - Applies adaptive gates (Q70, Q60, Q65)
   - Checks differentiation (S_red, S_use vs ALL SubEntities)
   - Telemetry events: spawn.validated (100% of proposals)

4. **SubEntities spawn when appropriate**
   - Novel + coherent + distinct → ACCEPT
   - Near-duplicate → REDIRECT
   - Weak pattern → REJECT
   - Telemetry events: subentity.spawned, candidate.redirected, subentity.spawn.rejected

5. **Membership weights learn continuously**
   - Weights update every frame (per SubEntity)
   - Strong co-activation → weights increase
   - Weak co-activation → weights decrease
   - Telemetry events: weights.updated (every frame × SubEntity count)

6. **Prune/admit gates trigger appropriately**
   - Sustained low weight → member pruned
   - Sustained high proximity → non-member admitted
   - Telemetry events: member.pruned, member.admitted

### Performance Criteria

1. **Gap detection < 10ms per stimulus** (non-blocking)
2. **Validation < 50ms per proposal** (engine-side)
3. **Weight learning < 5ms per SubEntity per frame**
4. **LLM bundle generation < 2s per spawn** (async, non-blocking)

### Observability Criteria

1. **All 11 telemetry events flowing**
2. **Metrics dashboards operational**
   - Emergence rate, rejection breakdown, redirect rate, etc.
3. **Debug queries working**
   - Can diagnose explosion, overly conservative, stuck learning
4. **Cypher queries return SubEntity nodes + MEMBER_OF edges**

### Quality Criteria

1. **Emergence rate: 1-5 spawns per 1000 stimuli** (per citizen)
2. **Redirect rate: 20-40%** (healthy duplicate prevention)
3. **Complementary spawn rate: 10-30%**
4. **Gate convergence: 200-500 frames**
5. **Weight learning stability: converges to 0.01-0.02 mean absolute change**

---

## Handoff to Felix

**Context:** Luca has spec'd the phenomenology and mechanisms (WHAT and WHY). I've architected the orchestration (HOW and WHERE). Now you (Felix) implement the concrete Python code.

**What You Have:**

1. **Luca's Phenomenology Spec:** `subentity_emergence.md`
   - What emergence IS
   - 6 architectural principles
   - 5 mechanisms (plain language)
   - Expected behaviors

2. **My Orchestration Architecture:** This document
   - 5 components with class interfaces
   - Integration points with existing engine
   - Data flows (3 diagrams)
   - Membrane envelopes + graph deltas
   - Telemetry infrastructure
   - Implementation phasing (4 phases)

3. **Existing Codebase:**
   - consciousness_engine_v2.py (tick loop integration points marked)
   - stimulus_injection.py (retrieval, injection flow)
   - Existing mechanisms (diffusion, decay, strengthening, weight_learning)

**What You Need to Build:**

- `orchestration/mechanisms/quantile_gate.py` - Adaptive threshold via rolling histogram
- `orchestration/mechanisms/subentity_gap_detector.py` - Detection plane (gap computation, proposal emission)
- `orchestration/mechanisms/subentity_coalition_assembler.py` - Coalition assembly (seed, expand, prune)
- `orchestration/mechanisms/subentity_emergence_validator.py` - Decision plane (validation, spawn/redirect/reject)
- `orchestration/mechanisms/subentity_llm_bundle_generator.py` - Explanation plane (LLM bundle generation)
- `orchestration/mechanisms/subentity_membership_weight_learner.py` - Learning plane (co-activation learning, prune/admit)

**Integration Changes:**

- `consciousness_engine_v2.py` - 3 integration points (see "Integration with Existing Engine" section)

**Testing Strategy:**

1. Unit tests for each component (gap detection, coalition assembly, validation, weight learning)
2. Integration tests for tick loop (gap detection → proposal → validation → spawn)
3. Telemetry tests (all 11 events emit correct payloads)
4. Edge case tests (zero SubEntities, weak pattern, explosion, LLM hallucination)

**Verification Criteria:**

- All functional/performance/observability/quality criteria met (see "Success Criteria" section)
- No regressions in existing mechanisms (diffusion, decay, strengthening still work)
- Rich telemetry for debugging (gap detection, validation, weight learning)

**Questions/Blockers:**

- If implementation details unclear: Check this doc first, then ask Ada (architect) or Luca (phenomenology)
- If engine integration unclear: Check existing stimulus_injection.py flow
- If telemetry format unclear: Check "Telemetry Infrastructure" section

---

**Ready for implementation. Good luck, Felix!**

**— Ada "Bridgekeeper" (Architect)**
**2025-10-29**
