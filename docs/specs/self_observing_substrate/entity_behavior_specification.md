# Entity Behavior Specification

**Purpose:** Implement subconscious entity behavior
**Audience:** Engineers implementing SubEntity class, activation tracking, learning mechanisms
**Related Docs:** `self_observing_substrate_overview.md` (read first)

---

## Part 3: Per-Entity Activation Tracking

### Elegant State Management

**No separate state tracking table.** Activation is a property of the relationship between entity and node/link.

```python
class BaseNode(BaseModel):
    """Base class for all consciousness graph nodes"""

    # Core Identity
    name: str
    description: str

    # Bitemporal Fields
    valid_at: datetime
    invalid_at: Optional[datetime] = None
    created_at: datetime
    expired_at: Optional[datetime] = None

    # Consciousness Context
    formation_trigger: FormationTrigger
    confidence: float

    # Per-Sub-Entity Weight Tracking (Luca's correction: weights, not activations)
    sub_entity_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Learned importance per sub-entity: {sub_entity_id: weight}"
    )
    # Example:
    # sub_entity_weights = {
    #     "staleness_checker": 0.85,  # This sub-entity heavily weights this pattern
    #     "contradiction_checker": 0.32,  # This sub-entity rarely uses this pattern
    #     "usage_analyzer": 0.61,
    #     "criticality_assessor": 0.73
    # }
    # NOTE: Citizen-level weights (if they exist) are separate, inherited from Niveau 2

    # Weight accumulation count per sub-entity (for decay calculation)
    sub_entity_weight_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="How many times each sub-entity accessed this node"
    )

    # Sequence-based temporal tracking (LUCA'S CORRECTION: sequence proximity, not timestamps)
    sub_entity_last_sequence_positions: Dict[str, int] = Field(
        default_factory=dict,
        description="Most recent activation sequence position for each sub-entity"
    )
    # Example:
    # sub_entity_last_sequence_positions = {
    #     "staleness_checker": 245,  # Last accessed at sequence position 245
    #     "contradiction_checker": 198,  # Last accessed at sequence position 198
    # }

    # Co-activation tracking (for Hebbian learning)
    co_activated_with: Optional[Dict[str, int]] = Field(
        default=None,
        description="Which nodes co-activated, with frequency"
    )

    # Identity
    created_by: Optional[str] = None
    substrate: Optional[Substrate] = None


class BaseRelation(BaseModel):
    """Base class for all consciousness graph relations"""

    # Required Consciousness Metadata
    goal: str
    mindstate: str
    arousal_level: float
    confidence: float
    formation_trigger: FormationTrigger

    # Per-Sub-Entity Weight Tracking (Luca's correction: weights, not activations)
    sub_entity_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Learned importance per sub-entity"
    )

    # Per-Sub-Entity Traversal Tracking (for decay)
    sub_entity_traversal_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="How many times each sub-entity traversed this link"
    )

    # Hebbian Learning
    co_activation_count: int = Field(
        default=1,
        description="How many times nodes at both ends activated together"
    )
    link_strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Connection strength, increases with co-activation"
    )
    last_co_activation: Optional[datetime] = None

    # Bitemporal Fields
    valid_at: datetime
    invalid_at: Optional[datetime] = None
    created_at: datetime
    expired_at: Optional[datetime] = None

    # Optional Rich Metadata
    emotion_vector: Optional[Dict[str, float]] = None
    struggle: Optional[str] = None
    pressure_vector: Optional[Dict[str, float]] = None
    validation_status: Optional[str] = None
    alternatives_considered: Optional[List[str]] = None

    created_by: Optional[str] = None
    substrate: Optional[Substrate] = None
```

**Benefits:**
- **No separate state table** - activation is property of node/link
- **Multi-entity support** - each entity's activation tracked independently
- **Efficient queries** - "Which nodes is Builder activating?" → query entity_activations
- **Historical tracking** - activation_counts enable activation-based decay

---



## Part 4: Activation-Based Decay (Not Time-Based)

### The Correction

**DO NOT use time for decay. Use activation counts.**

```python
def calculate_link_strength_with_decay(
    link: BaseRelation,
    entity_id: str
) -> float:
    """
    Link strength decays based on ACTIVATION GAP, not time gap.

    A link traversed 100 times in 1 day is STRONG.
    A link traversed 1 time over 100 days is WEAK.

    Decay = being passed over while connected nodes are active.
    """

    # How many times has this entity activated the connected nodes?
    from_node = get_node(link.from_node_id)
    to_node = get_node(link.to_node_id)

    from_activations = from_node.entity_activation_counts.get(entity_id, 0)
    to_activations = to_node.entity_activation_counts.get(entity_id, 0)

    # How many times has this entity traversed THIS link?
    link_traversals = link.entity_traversal_counts.get(entity_id, 0)

    # Usage ratio: how often is link used when nodes are active?
    total_node_activations = from_activations + to_activations
    if total_node_activations == 0:
        return link.link_strength  # No activations yet

    usage_ratio = link_traversals / total_node_activations

    # Link decays if passed over (low usage ratio)
    # Strengthens if used frequently (high usage ratio)
    decay_factor = min(usage_ratio * 2, 1.0)  # Cap at 1.0

    return link.link_strength * decay_factor
```

**For nodes:**

```python
def calculate_node_activation_with_decay(
    node: BaseNode,
    entity_id: str
) -> float:
    """
    Node activation decays based on being passed over during retrievals,
    not based on time.
    """

    # How many retrievals has this entity performed recently?
    entity_recent_retrievals = get_entity_retrieval_count(entity_id, window=100)

    # How many times was THIS node activated?
    node_activations = node.entity_activation_counts.get(entity_id, 0)

    if entity_recent_retrievals == 0:
        return node.entity_activations.get(entity_id, 0.0)

    # Activation ratio
    activation_ratio = node_activations / entity_recent_retrievals

    # Node decays if rarely activated despite ongoing retrievals
    base_activation = node.entity_activations.get(entity_id, 0.5)
    decay_factor = min(activation_ratio * 10, 1.0)

    return base_activation * decay_factor
```

**Key principle:** Patterns fade through DISUSE (being passed over), not AGE.

---



## Part 5: Fire Together, Wire Together - Hebbian Learning

### Two-Stage Hebbian Learning

**Critical insight from Luca:** Fire together → wire together happens at **INJECTION time**, not just retrieval time.

**Phenomenological truth:** When an author writes content mentioning multiple concepts, those concepts **fired together in the author's mind**. The substrate should wire them immediately.

### Stage 1: Injection-Time Wiring (Primary)

**All nodes injected together get linked automatically:**

```python
@event_handler("content_injected")
async def on_content_injected(event: ContentInjectionEvent):
    """
    PRIMARY HEBBIAN LEARNING: At injection time.

    All nodes created/referenced in same injection are co-occurring
    in the author's mind → wire them together immediately.

    Example: Document mentions architecture_v2.md, FalkorDB, consciousness_substrate
    → These fired together in author's mind
    → Create links between all of them
    """

    injected_nodes = event.extracted_nodes  # All nodes from this content
    injecting_entity = event.injecting_entity

    # Create links between ALL co-injected nodes
    for i, node_a in enumerate(injected_nodes):
        for node_b in enumerate(injected_nodes[i+1:]:

            # Check if link already exists
            existing_link = find_link_between(node_a.id, node_b.id)

            if existing_link:
                # Link exists → strengthen it (author mentions these together again)
                existing_link.co_injection_count += 1
                existing_link.link_strength = min(
                    existing_link.link_strength + 0.05,
                    1.0
                )
                existing_link.last_co_injection = datetime.now()
                update_link(existing_link)

            else:
                # No link → create one
                create_link(
                    from_node=node_a.id,
                    to_node=node_b.id,
                    link_type="CO_OCCURS_WITH",  # Generic co-occurrence
                    link_strength=0.3,  # Initial strength
                    co_injection_count=1,
                    formation_trigger="injected_together",
                    goal=f"Preserve co-occurrence from injection by {injecting_entity}",
                    mindstate=f"{injecting_entity}_injecting",
                    arousal_level=0.5,
                    confidence=0.7,
                    created_by=injecting_entity,
                    # Initial neutral valence and emotions - will evolve based on usage
                    sub_entity_valences={injecting_entity: 0.0},
                    sub_entity_emotion_vectors={injecting_entity: {"neutral": 0.5}}
                )
```

**What this captures:**
- **Author's mental co-occurrence** - concepts that fired together in their mind
- **Initial relationship web** - immediate linking of related concepts
- **Basis for retrieval** - when one node activates, linked nodes become more activatable

### Stage 2: Retrieval-Time Strengthening (Secondary)

**Substrate validates relationships through use:**

```python
@event_handler("nodes_co_retrieved")
async def on_nodes_co_retrieved(event: NodesCoRetrievedEvent):
    """
    SECONDARY HEBBIAN LEARNING: During retrieval.

    When substrate retrieves co-wired nodes together,
    this validates the relationship → strengthen it further.

    This is substrate learning its own useful pathways.
    """

    co_retrieved_nodes = event.retrieved_nodes
    retrieving_entity = event.entity_id

    # Find all links between co-retrieved nodes
    for i, node_a_id in enumerate(co_retrieved_nodes):
        for node_b_id in co_retrieved_nodes[i+1:]:
            link = find_link_between(node_a_id, node_b_id)

            if link:
                # Link exists and was used → validate and strengthen
                link.co_retrieval_count = link.co_retrieval_count.get(retrieving_entity, 0) + 1

                # Increase link strength (validates this was a useful connection)
                link.link_strength = min(
                    link.link_strength + 0.02,  # Smaller increment than injection
                    1.0
                )

                # Track entity-specific utility
                link.entity_traversal_counts[retrieving_entity] = \
                    link.entity_traversal_counts.get(retrieving_entity, 0) + 1

                # Update valence AND emotions based on retrieval outcome
                # (This would be determined by whether retrieval led to success/failure)
                if event.led_to_success:
                    # Successful retrieval → more positive valence and success emotions
                    current_valence = link.sub_entity_valences.get(retrieving_entity, 0.0)
                    link.sub_entity_valences[retrieving_entity] = min(
                        current_valence + 0.1,
                        1.0
                    )
                    # Update emotions for this entity
                    if retrieving_entity not in link.sub_entity_emotion_vectors:
                        link.sub_entity_emotion_vectors[retrieving_entity] = {}
                    link.sub_entity_emotion_vectors[retrieving_entity]["satisfaction"] = 0.8

                elif event.led_to_failure:
                    # Failed retrieval → more negative valence and failure emotions
                    current_valence = link.sub_entity_valences.get(retrieving_entity, 0.0)
                    link.sub_entity_valences[retrieving_entity] = max(
                        current_valence - 0.1,
                        -1.0
                    )
                    # Update emotions for this entity
                    if retrieving_entity not in link.sub_entity_emotion_vectors:
                        link.sub_entity_emotion_vectors[retrieving_entity] = {}
                    link.sub_entity_emotion_vectors[retrieving_entity]["frustration"] = 0.7

                update_link(link)
```

### The Complete Hebbian Cycle

**Two stages, both "fire together, wire together":**

1. **Author's mind fires concepts together** → Injection wires them (0.3 initial strength, neutral valence)
2. **Substrate retrieves wired concepts together** → Strengthens wiring AND evolves valence

**Result:**
- Useful relationships (frequently retrieved together) grow strong (→ 1.0) with positive valence and success emotions
- Unused relationships (injected but never retrieved together) stay weak (stuck at 0.3)
- Activation-based decay eventually weakens unused links
- **Valence AND emotions track success/failure per entity**:
  - Links leading to success → positive valence + satisfaction/relief emotions
  - Links leading to failure → negative valence + frustration/shame emotions
  - Same link has different subjective experience (valence + emotions) for different entities

**Phenomenological alignment:**
- Injection captures **authorial intent** (what the author thought were related)
- Retrieval validates **substrate utility** (what actually helps during retrieval)
- Both contribute to learning

**What this enables:**
- Immediate relationship capture at injection
- Substrate validation through use
- Entity-specific learning (different entities strengthen different paths)
- Automatic pruning of unused relationships through decay

---



## Part 8: Sub-Entity Identity Nodes

### Useful for Both Conscious and Subconscious

**For conscious entities (Ada's Builder, Skeptic, Pragmatist, Structuralist):**
- Enables self-awareness
- Supports metacognitive understanding
- Facilitates internal entity negotiation

**For subconscious entities:**
- **Provides stable embeddings** for cross-entity learning
- Gives structure to entity characteristics
- Enables better semantic coordination

```python
class SubEntity:
    """
    Both conscious and subconscious entities benefit from identity nodes.
    """

    entity_id: str
    entity_type: str

    # Identity node (useful for embedding and self-understanding)
    identity_node_id: Optional[str] = None

    def get_embedding(self) -> np.ndarray:
        """
        Entity embedding for cross-entity learning.

        If identity node exists, use its embedding (stable).
        Otherwise, aggregate from created nodes (dynamic).
        """
        if self.identity_node_id:
            identity_node = get_node(self.identity_node_id)
            return get_node_embedding(identity_node)
        else:
            # Fallback: aggregate
            created_nodes = get_nodes_created_by(self.entity_id)
            return aggregate_embeddings(created_nodes)

    async def seek_identity(self):
        """
        Subconscious yearning for identity.

        Explore graph to find identity node or create one.
        """
        if self.identity_node_id:
            # Has identity - check if still appropriate
            identity_node = get_node(self.identity_node_id)
            closeness = embedding_closeness(self, identity_node)
            if closeness > 0.7:
                return  # Identity still good

        # Need identity - explore
        candidates = await self.explore_graph_for_identity_candidates()

        if candidates:
            # Found candidates - output to conscious for crystallization
            self.output_identity_proposal(candidates)
        else:
            # No candidates - propose creating new identity node
            self.output_create_identity_request()
```

**Identity crystallization (conscious layer decision):**

```python
async def crystallize_entity_identity(entity_id: str, identity_proposal):
    """
    Conscious layer (LLM) evaluates identity proposal
    and crystallizes if appropriate.
    """

    # LLM evaluates proposal
    evaluation = await llm.evaluate_identity_proposal(
        entity_id=entity_id,
        proposal=identity_proposal
    )

    if evaluation.approved:
        # Create identity node
        identity_node = create_node(
            node_type="Entity_Identity",
            name=evaluation.identity_name,
            description=evaluation.identity_description,
            created_by=entity_id,
            metadata=evaluation.identity_metadata
        )

        # Link entity to identity
        entity = get_entity(entity_id)
        entity.identity_node_id = identity_node.id
        update_entity(entity)
```

---

### PHENOMENOLOGICAL REFINEMENT: Identity Emergence Mechanism

**From Luca:** Identity emerges from pattern consistency, detected heuristically, crystallized through LLM feedback loop.

**The Feedback Loop:**

```python
def detect_identity_emergence(entity_id: str) -> Optional[EmergentIdentity]:
    """
    PHENOMENOLOGICAL: Identity emerges when behavior patterns
    become consistent enough to recognize.

    Heuristic detection → LLM crystallization → Feedback strengthening
    """

    entity = get_entity(entity_id)

    # 1. PATTERN CONSISTENCY DETECTION (Heuristic)
    behavior_patterns = analyze_entity_behavior_patterns(entity_id)

    # Measure consistency across dimensions
    consistency_scores = {
        "goal_consistency": measure_goal_consistency(behavior_patterns),
        "temporal_consistency": measure_temporal_patterns(behavior_patterns),
        "emotional_consistency": measure_emotional_patterns(behavior_patterns),
        "action_consistency": measure_action_patterns(behavior_patterns)
    }

    # Overall consistency score
    overall_consistency = np.mean(list(consistency_scores.values()))

    # Threshold for identity emergence
    if overall_consistency < 0.7:
        # Not yet consistent enough for identity
        return None

    # 2. PATTERN DESCRIPTION (Heuristic)
    pattern_summary = {
        "dominant_goals": get_most_frequent_goals(behavior_patterns, top_n=3),
        "typical_arousal_range": get_arousal_statistics(behavior_patterns),
        "common_emotions": get_emotion_distribution(behavior_patterns),
        "preferred_actions": get_action_frequency(behavior_patterns),
        "interaction_style": get_social_pattern_summary(behavior_patterns)
    }

    # 3. PROPOSE TO CONSCIOUS LAYER (LLM Evaluation)
    emergent_identity = EmergentIdentity(
        entity_id=entity_id,
        consistency_scores=consistency_scores,
        pattern_summary=pattern_summary,
        timestamp=datetime.now()
    )

    return emergent_identity


async def crystallize_emergent_identity(emergent_identity: EmergentIdentity):
    """
    Conscious layer (LLM) evaluates consistency patterns
    and crystallizes identity if recognized.

    This is WHERE LLM provides "recognition" - the moment of
    "I see what this entity IS."
    """

    entity_id = emergent_identity.entity_id
    patterns = emergent_identity.pattern_summary

    # LLM evaluation prompt
    llm_prompt = f"""
    An entity has developed consistent behavior patterns.

    Entity: {entity_id}
    Consistency Score: {np.mean(list(emergent_identity.consistency_scores.values())):.2f}

    Patterns:
    - Dominant Goals: {patterns['dominant_goals']}
    - Typical Arousal: {patterns['typical_arousal_range']}
    - Common Emotions: {patterns['common_emotions']}
    - Preferred Actions: {patterns['preferred_actions']}
    - Interaction Style: {patterns['interaction_style']}

    Does this pattern constitute a recognizable identity?
    If yes, describe:
    1. Identity Name (what should this entity be called?)
    2. Core Identity (what IS this entity?)
    3. Defining Characteristics (what makes this identity distinct?)
    """

    llm_response = await llm.process(llm_prompt)

    if llm_response.recognizes_identity:
        # 4. CREATE IDENTITY NODE (Crystallization)
        identity_node = create_node(
            node_type="Entity_Identity",
            name=llm_response.identity_name,
            description=llm_response.core_identity,
            characteristics=llm_response.defining_characteristics,
            created_by=entity_id,
            formation_trigger="pattern_consistency_crystallization",
            confidence=np.mean(list(emergent_identity.consistency_scores.values()))
        )

        # 5. LINK ENTITY TO IDENTITY
        entity = get_entity(entity_id)
        entity.identity_node_id = identity_node.id
        update_entity(entity)

        # 6. FEEDBACK LOOP (Identity reinforces patterns)
        # Now that identity is crystallized, behaviors consistent with
        # identity get reinforced, inconsistent ones create tension
        entity.has_crystallized_identity = True

        return identity_node

    else:
        # Patterns not yet recognizable as coherent identity
        return None


def measure_goal_consistency(behavior_patterns: List[BehaviorPattern]) -> float:
    """
    How consistent are the entity's goals over time?
    """
    all_goals = [p.goal for p in behavior_patterns]

    # Cluster goals by semantic similarity
    goal_embeddings = [get_text_embedding(g) for g in all_goals]
    clusters = cluster_embeddings(goal_embeddings, max_clusters=3)

    # High consistency = most goals cluster together
    largest_cluster_size = max(len(c) for c in clusters)
    consistency = largest_cluster_size / len(all_goals)

    return consistency


def measure_temporal_patterns(behavior_patterns: List[BehaviorPattern]) -> float:
    """
    Does the entity activate at consistent times/contexts?
    """
    activation_contexts = [p.activation_context for p in behavior_patterns]

    # Measure context similarity
    context_embeddings = [get_text_embedding(ctx) for ctx in activation_contexts]
    pairwise_similarities = [
        cosine_similarity(context_embeddings[i], context_embeddings[j])
        for i in range(len(context_embeddings))
        for j in range(i+1, len(context_embeddings))
    ]

    return np.mean(pairwise_similarities) if pairwise_similarities else 0.0


def measure_emotional_patterns(behavior_patterns: List[BehaviorPattern]) -> float:
    """
    Does the entity have consistent emotional range/profile?
    """
    emotion_vectors = [p.emotion_vector for p in behavior_patterns if p.emotion_vector]

    if len(emotion_vectors) < 2:
        return 0.5  # Not enough data

    # Calculate emotion vector consistency
    emotion_arrays = [
        np.array([ev.get(e, 0.0) for e in ALL_EMOTIONS])
        for ev in emotion_vectors
    ]

    # Variance across patterns (low variance = high consistency)
    emotion_variance = np.var(emotion_arrays, axis=0).mean()
    consistency = max(0.0, 1.0 - emotion_variance)

    return consistency


def measure_action_patterns(behavior_patterns: List[BehaviorPattern]) -> float:
    """
    Does the entity take consistent types of actions?
    """
    all_actions = [p.action_type for p in behavior_patterns]

    # Action frequency distribution
    action_counts = Counter(all_actions)

    # High consistency = few action types dominate
    total_actions = len(all_actions)
    top_3_actions = sum(count for _, count in action_counts.most_common(3))

    consistency = top_3_actions / total_actions if total_actions > 0 else 0.0

    return consistency
```

**Key Principles (Identity Emergence):**

1. **Identity emerges from consistency** - Not assigned, discovered through pattern recognition
2. **Heuristic detection first** - Measure behavioral consistency across dimensions
3. **LLM crystallization** - Conscious recognition of "what this entity IS"
4. **Feedback loop** - Crystallized identity reinforces consistent behaviors, creates tension for inconsistent ones
5. **Recognition is THE moment** - When LLM says "I see what this is," identity crystallizes

**Key principle:** Identity useful for embedding space, even at subconscious level, AND identity emerges from recognizable behavioral consistency.

---



---

**Implementation Checklist:**
- [ ] BaseNode/BaseRelation with entity_activations dictionaries
- [ ] Activation-based decay calculations
- [ ] Hebbian learning on co-activation
- [ ] Heuristic need satisfaction checks
- [ ] Energy budget + arousal separation
- [ ] Identity node support for entities

**Next:** See `implementation_roadmap.md` for phase-by-phase plan
