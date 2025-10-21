# Entity Social Dynamics

**Purpose:** Implement multi-entity interactions and relationships
**Audience:** Engineers implementing cross-entity learning, social links, gestalt detection
**Related Docs:** `self_observing_substrate_overview.md` (context), `entity_behavior_specification.md` (foundation)

---

## Part 6: Cross-Entity Learning with Multi-Dimensional Resonance

### Links Work Differently for Different Entities

**Principle:** Links created by one entity can be used by another, but effectiveness depends on multi-dimensional resonance, not just embedding similarity.

**PHENOMENOLOGICAL REFINEMENT (from Luca):** Resonance is multi-dimensional. Recognition happens through coherent activation across:
1. **Semantic similarity** (embedding space)
2. **Temporal alignment** (when patterns formed)
3. **Goal alignment** (pursuing similar objectives)
4. **Emotional resonance** (similar affective states)
5. **Flow compatibility** (similar energy/energy patterns)

```python
def calculate_link_utility_for_entity(
    link: BaseRelation,
    user_entity_id: str,
    current_context: Optional[Dict] = None
) -> float:
    """
    Links have different utility for different entities.
    Effectiveness determined by multi-dimensional resonance.

    PHENOMENOLOGICAL GROUNDING: Recognition through resonance,
    not just embedding similarity.
    """

    base_strength = link.link_strength

    if link.created_by == user_entity_id:
        # Using own link - full strength
        return base_strength

    # Multi-dimensional resonance calculation
    creator_entity = get_entity(link.created_by)
    user_entity = get_entity(user_entity_id)

    # Dimension 1: Semantic Similarity (embedding space)
    creator_embedding = get_entity_embedding(link.created_by)
    user_embedding = get_entity_embedding(user_entity_id)
    semantic_similarity = cosine_similarity(creator_embedding, user_embedding)

    # Dimension 2: Temporal Alignment (LUCA'S CORRECTION: sequence-based, not time-based)
    temporal_alignment = calculate_temporal_alignment_by_sequence(
        link,
        user_entity_id,
        current_context
    )

    # Dimension 3: Goal Alignment (pursuing similar objectives?)
    goal_alignment = calculate_goal_similarity(
        link.goal,
        user_entity.current_goals
    )

    # Dimension 4: Emotional Resonance (similar affective states?)
    emotional_resonance = 0.5  # Default
    if link.emotion_vector and current_context and "emotion_vector" in current_context:
        emotional_resonance = calculate_emotion_similarity(
            link.emotion_vector,
            current_context["emotion_vector"]
        )

    # Dimension 5: Flow Compatibility (similar energy/energy patterns?)
    flow_compatibility = calculate_energy_similarity(
        link.energy,
        user_entity.energy
    )

    # Weighted combination (tunable weights)
    resonance_score = (
        semantic_similarity * 0.30 +
        temporal_alignment * 0.15 +
        goal_alignment * 0.25 +
        emotional_resonance * 0.20 +
        flow_compatibility * 0.10
    )

    # Multiplier based on multi-dimensional resonance
    return base_strength * resonance_score


def calculate_temporal_alignment_by_sequence(
    link: BaseRelation,
    user_entity_id: str,
    current_context: Optional[Dict] = None
) -> float:
    """
    LUCA'S CORRECTION: Sequence-based temporal alignment, not timestamp-based.

    NOT: "Link created 3 days ago vs entity active today → low alignment"
    BUT: "Link activated at sequence position 95, entity currently at 98 → high alignment"

    Temporal coherence comes from activation sequence proximity,
    not calendar time. Patterns activated close together in the
    traversal sequence resonate, regardless of calendar dates.

    This aligns with activation-based decay principle:
    - Patterns fade through DISUSE (sequence gaps), not AGE (time gaps)
    """

    # Get activation sequence positions
    from_node = get_node(link.from_node_id)
    to_node = get_node(link.to_node_id)

    # Most recent activation sequence positions for user entity
    from_seq_pos = from_node.sub_entity_last_sequence_positions.get(user_entity_id, None)
    to_seq_pos = to_node.sub_entity_last_sequence_positions.get(user_entity_id, None)

    if from_seq_pos is None or to_seq_pos is None:
        # No sequence data yet → neutral alignment
        return 0.5

    # Get entity's current sequence position
    user_entity = get_entity(user_entity_id)
    current_seq_pos = user_entity.current_sequence_position

    # Calculate sequence gaps
    from_gap = current_seq_pos - from_seq_pos
    to_gap = current_seq_pos - to_seq_pos

    # Average gap for link endpoints
    avg_gap = (from_gap + to_gap) / 2.0

    # Temporal alignment based on sequence proximity
    # Recently activated (gap < 10) = high alignment (1.0)
    # Moderately recent (gap 10-50) = medium alignment (0.5-1.0)
    # Distant (gap > 100) = low alignment (0.0-0.3)

    if avg_gap < 10:
        # Very recent in activation sequence
        alignment = 1.0
    elif avg_gap < 50:
        # Moderately recent
        alignment = 1.0 - ((avg_gap - 10) / 40) * 0.5  # Decays from 1.0 to 0.5
    elif avg_gap < 100:
        # Distant but not forgotten
        alignment = 0.5 - ((avg_gap - 50) / 50) * 0.2  # Decays from 0.5 to 0.3
    else:
        # Very distant in sequence
        alignment = max(0.0, 0.3 - ((avg_gap - 100) / 200) * 0.3)  # Decays toward 0

    return alignment


def calculate_goal_similarity(link_goal: str, entity_goals: List[str]) -> float:
    """
    Goal alignment: similar objectives increase resonance.
    """
    if not entity_goals:
        return 0.5

    # Embedding similarity between link goal and entity goals
    link_goal_embedding = get_text_embedding(link_goal)
    goal_embeddings = [get_text_embedding(g) for g in entity_goals]

    similarities = [
        cosine_similarity(link_goal_embedding, goal_emb)
        for goal_emb in goal_embeddings
    ]

    return max(similarities) if similarities else 0.5


def calculate_emotion_similarity(emotion_vec_a: Dict[str, float], emotion_vec_b: Dict[str, float]) -> float:
    """
    Emotional resonance: similar affective states increase resonance.
    """
    # Get all emotion dimensions
    all_emotions = set(emotion_vec_a.keys()) | set(emotion_vec_b.keys())

    # Calculate cosine similarity in emotion space
    vec_a = np.array([emotion_vec_a.get(e, 0.0) for e in all_emotions])
    vec_b = np.array([emotion_vec_b.get(e, 0.0) for e in all_emotions])

    if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
        return 0.5

    return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))


def calculate_energy_similarity(energy_a: float, energy_b: float) -> float:
    """
    Flow compatibility: similar energy levels increase resonance.
    """
    energy_delta = abs(energy_a - energy_b)
    # Close energy levels (delta < 0.2) = high compatibility
    # Very different energy (delta > 0.5) = low compatibility
    return max(0.0, 1.0 - (energy_delta / 0.5))


def get_entity_embedding(entity_id: str) -> np.ndarray:
    """
    Generate entity embedding.

    Version 1: If entity has identity node, use its embedding.
    Otherwise, aggregate from entity's created nodes.
    """

    entity = get_entity(entity_id)

    if entity.identity_node_id:
        # Use identity node embedding
        identity_node = get_node(entity.identity_node_id)
        return get_node_embedding(identity_node)

    # Fallback: aggregate from created nodes
    created_nodes = get_nodes_created_by(entity_id)
    if not created_nodes:
        # No nodes yet - default embedding
        return np.zeros(1536)  # OpenAI embedding dimension

    node_embeddings = [get_node_embedding(node) for node in created_nodes]

    # Average (simple aggregation - can be improved)
    entity_embedding = np.mean(node_embeddings, axis=0)

    return entity_embedding
```

**Implications:**

- **N2 collective graph:** All entities contribute links, each uses with varying effectiveness
- **Learning signal:** If Ada uses Luca's link successfully (high activation), that could increase cross-entity utility
- **Identity nodes matter:** They provide stable embeddings for cross-entity learning

---



## Part 7: Entity Social Dynamics (Meetings and Relationships)

### Detection and Social Link Types

**PHENOMENOLOGICAL REFINEMENT (from Luca):** Entity relationships are not just "calibration." They have rich social dynamics:
- **ASSISTS** - One entity helps another achieve goals
- **INHIBITS** (also COMPETES_WITH) - One entity blocks another's objectives
- **MENTORS** - One entity guides another's development
- **CONFLICTS_WITH** - Goals fundamentally misaligned
- **COMPLEMENTS** - Different approaches to same problem
- **DEPENDS_ON** - One entity requires another's output

**Luca's clarification:** Use minimal new types (Option B). Add only what's truly missing:
- **NEW: COMPETES_WITH** - Competitive inhibition (no existing equivalent in graph)
- **NEW: ASSISTS** - Collaborative activation (no existing equivalent)
- **EXISTING: CALIBRATES_WITH** - Pattern exchange (covers mentoring with metadata)
- **EXISTING: CONTRADICTS** - Semantic conflict at content level (CONFLICTS_WITH is entity-level)

```python
class EntitySocialLinkType(str, Enum):
    """
    Social relationship types between entities.

    Minimal extension (Option B): Only add what's missing.
    Leverage existing graph link types where possible.
    """
    # NEW TYPES (no existing equivalent)
    COMPETES_WITH = "competes_with"  # Competitive inhibition
    ASSISTS = "assists"              # Collaborative activation

    # EXTENDED TYPES (use existing with richer metadata)
    CALIBRATES_WITH = "calibrates_with"  # Pattern exchange (can be symmetric or mentoring)
    CONFLICTS_WITH = "conflicts_with"    # Entity-level disagreement (distinct from CONTRADICTS)

    # DERIVED FROM EXISTING
    COMPLEMENTS = "complements"      # Working together (detected from co-activation)
    DEPENDS_ON = "depends_on"        # Output dependency (detected from yearning patterns)


class EntitySocialLink(BaseModel):
    """Social relationship between entities"""
    from_entity: str
    to_entity: str
    link_type: EntitySocialLinkType

    # How strong is this relationship?
    relationship_strength: float = 0.5

    # Evidence supporting this relationship
    meeting_count: int = 0
    co_activation_patterns: List[str] = []

    # Phenomenological context
    relationship_goal: str
    formation_trigger: str
    last_interaction: datetime

    # Evolution tracking
    relationship_history: List[Dict] = []


def detect_entity_meeting(entity_a_id: str, entity_b_id: str) -> Optional[EntityMeeting]:
    """
    Entities meet when their activated nodes overlap.
    """

    # Get currently activated nodes for each entity
    activated_a = get_activated_nodes_for_entity(entity_a_id)
    activated_b = get_activated_nodes_for_entity(entity_b_id)

    # Find overlap
    overlap = set(activated_a) & set(activated_b)

    if overlap:
        # They've met
        meeting = EntityMeeting(
            entities=[entity_a_id, entity_b_id],
            overlapping_nodes=list(overlap),
            timestamp=datetime.now()
        )

        record_meeting(meeting)

        # Analyze social dynamics from meeting
        analyze_social_dynamics(entity_a_id, entity_b_id, overlap)

        return meeting

    return None


def analyze_social_dynamics(entity_a_id: str, entity_b_id: str, overlap_nodes: List[str]):
    """
    PHENOMENOLOGICAL: Analyze the social relationship from meeting patterns.

    What are they doing when they meet?
    - Both working on same problem (COMPLEMENTS)?
    - One blocks the other's progress (INHIBITS)?
    - One provides context the other needs (ASSISTS)?
    - Goals fundamentally opposed (CONFLICTS_WITH)?
    """

    entity_a = get_entity(entity_a_id)
    entity_b = get_entity(entity_b_id)

    # What are their goals during overlap?
    a_active_goals = get_active_goals_from_nodes(entity_a, overlap_nodes)
    b_active_goals = get_active_goals_from_nodes(entity_b, overlap_nodes)

    # Goal alignment analysis
    goal_alignment = calculate_goal_alignment(a_active_goals, b_active_goals)

    # Detect relationship type heuristically
    if goal_alignment > 0.8:
        # Similar goals, both working on same thing
        relationship_type = EntitySocialLinkType.COMPLEMENTS

    elif goal_alignment < 0.3:
        # Opposed goals
        relationship_type = EntitySocialLinkType.CONFLICTS_WITH

    elif entity_a.energy < 0.3 and entity_b.energy > 0.7:
        # A is satisfied, B is yearning - A might be assisting B
        relationship_type = EntitySocialLinkType.ASSISTS

    elif entity_a.energy > 0.7 and entity_b.energy > 0.7:
        # Both yearning for same resources - potential inhibition
        relationship_type = EntitySocialLinkType.INHIBITS

    else:
        # Default: they're calibrating (original simple relationship)
        relationship_type = EntitySocialLinkType.CALIBRATES_WITH

    # Get or create social link
    social_link = get_or_create_social_link(entity_a_id, entity_b_id)

    # Update relationship based on meeting
    social_link.meeting_count += 1
    social_link.co_activation_patterns.extend(overlap_nodes)
    social_link.last_interaction = datetime.now()

    # If relationship type detected differs from current, record evolution
    if social_link.link_type != relationship_type:
        social_link.relationship_history.append({
            "previous_type": social_link.link_type,
            "new_type": relationship_type,
            "trigger": f"Meeting on {len(overlap_nodes)} overlapping nodes",
            "timestamp": datetime.now()
        })
        social_link.link_type = relationship_type

    update_social_link(social_link)


def get_activated_nodes_for_entity(entity_id: str) -> List[str]:
    """
    Which nodes does this entity currently have activated?
    """

    activated_nodes = []

    for node in query_all_nodes():
        activation = node.entity_activations.get(entity_id, 0.0)
        if activation > 0.5:  # Activation threshold
            activated_nodes.append(node.id)

    return activated_nodes
```

**What happens when entities meet?**

```python
@event_handler("entity_meeting")
async def on_entity_meeting(event: EntityMeetingEvent):
    """
    When entities meet (activated nodes overlap),
    they DON'T merge (different goals maintained).

    But they DO develop social relationships:
    - ASSISTS: Help each other achieve goals
    - INHIBITS: Block each other's progress
    - MENTORS: Guide development
    - CONFLICTS_WITH: Opposed objectives
    - COMPLEMENTS: Different approaches to same problem
    """

    entity_a = event.entities[0]
    entity_b = event.entities[1]
    overlap_nodes = event.overlapping_nodes

    # Get social relationship
    social_link = get_social_link(entity_a, entity_b)

    if not social_link:
        # First meeting - establish baseline relationship
        return

    # Execute social coordination based on relationship type
    if social_link.link_type == EntitySocialLinkType.ASSISTS:
        # Entity A provides context to Entity B
        context_from_a = get_entity_gathered_context(entity_a)
        add_to_entity_context(entity_b, context_from_a, source=entity_a)

    elif social_link.link_type == EntitySocialLinkType.INHIBITS:
        # Entities competing for same resources - priority competition
        if get_entity(entity_a).energy > get_entity(entity_b).energy:
            # A has priority, B backs off
            reduce_entity_energy_budget(entity_b, reduction=0.5)
        else:
            reduce_entity_energy_budget(entity_a, reduction=0.5)

    elif social_link.link_type == EntitySocialLinkType.MENTORS:
        # Entity A guides Entity B's exploration
        a_best_practices = get_entity_best_practices(entity_a)
        suggest_patterns_to_entity(entity_b, a_best_practices)

    elif social_link.link_type == EntitySocialLinkType.CONFLICTS_WITH:
        # Fundamental goal misalignment - signal to conscious layer
        signal_entity_conflict(entity_a, entity_b, overlap_nodes)

    elif social_link.link_type == EntitySocialLinkType.COMPLEMENTS:
        # Working on same problem, different angles - synthesize
        propose_gestalt_formation(entity_a, entity_b, overlap_nodes)

    # Update relationship strength based on interaction success
    social_link.relationship_strength = min(
        social_link.relationship_strength + 0.05,
        1.0
    )
    update_social_link(social_link)
```

**Key principles:**
- Entities don't merge (they have different goals)
- BUT they develop rich social relationships (ASSISTS, INHIBITS, MENTORS, CONFLICTS_WITH, etc.)
- Social dynamics detected heuristically from meeting patterns
- Relationships evolve over time based on interactions
- Social coordination enables complex multi-entity behavior

---



## Part 12: Gestalt Formation (Multi-Sub-Entity Synthesis)

### PHENOMENOLOGICAL REFINEMENT: When Entities Meet, Gestalts Can Emerge

**From Luca:** When Builder + Skeptic + Pragmatist meet on overlapping nodes, a GESTALT can form - an emergent pattern greater than sum of parts.

**The Gestalt Formation Mechanism:**

```python
class EntityGestalt(BaseModel):
    """
    Emergent pattern from multi-entity synthesis.

    NOT a new entity, but a recognized pattern that emerges
    when specific entities meet in specific configurations.
    """

    gestalt_id: str
    participating_entities: List[str]

    # What pattern emerged?
    gestalt_name: str
    gestalt_description: str

    # Where did it emerge?
    synthesis_nodes: List[str]  # Nodes where entities met

    # How strong is this gestalt?
    coherence_score: float  # 0.0-1.0, how well do entities form coherent whole?

    # When did it form?
    formation_timestamp: datetime
    formation_trigger: str

    # Evolution
    activation_count: int = 1
    strengthens_over_time: bool = True


def detect_gestalt_formation(
    entity_ids: List[str],
    overlapping_nodes: List[str]
) -> Optional[EntityGestalt]:
    """
    PHENOMENOLOGICAL: Detect when multiple entities meeting
    creates an emergent gestalt pattern.

    Example: Builder + Skeptic + Pragmatist meeting on "architecture design"
    nodes might form "Rigorous Architecture" gestalt.
    """

    if len(entity_ids) < 2:
        # Need at least 2 entities for gestalt
        return None

    # 1. MEASURE COHERENCE (Do entities form coherent whole?)
    entities = [get_entity(eid) for eid in entity_ids]

    # Coherence factors:
    # - Goal alignment (are goals complementary?)
    # - Energy correlation (similar energy levels?)
    # - Social relationships (do they COMPLEMENT vs CONFLICT?)
    # - Activation pattern overlap (meeting on meaningful nodes?)

    goal_coherence = measure_multi_entity_goal_coherence(entities)
    energy_coherence = measure_energy_coherence(entities)
    social_coherence = measure_social_relationship_coherence(entity_ids)
    activation_coherence = measure_activation_pattern_coherence(
        entity_ids,
        overlapping_nodes
    )

    overall_coherence = np.mean([
        goal_coherence,
        energy_coherence,
        social_coherence,
        activation_coherence
    ])

    # Threshold for gestalt formation
    if overall_coherence < 0.7:
        # Not coherent enough for gestalt
        return None

    # 2. DESCRIBE EMERGENT PATTERN (What IS this gestalt?)
    # This requires LLM synthesis - entities alone can't see the gestalt

    gestalt_proposal = {
        "entities": [e.entity_id for e in entities],
        "entity_characteristics": {
            e.entity_id: describe_entity_characteristics(e)
            for e in entities
        },
        "meeting_context": describe_meeting_context(overlapping_nodes),
        "coherence_scores": {
            "goal": goal_coherence,
            "energy": energy_coherence,
            "social": social_coherence,
            "activation": activation_coherence
        }
    }

    return gestalt_proposal


async def crystallize_gestalt(gestalt_proposal: Dict) -> Optional[EntityGestalt]:
    """
    Conscious layer (LLM) recognizes the emergent pattern.

    This is WHERE the gestalt becomes visible - through LLM recognition.
    """

    # LLM synthesis prompt
    llm_prompt = f"""
    Multiple entities have met with high coherence.

    Entities: {gestalt_proposal['entities']}

    Entity Characteristics:
    {format_entity_characteristics(gestalt_proposal['entity_characteristics'])}

    Meeting Context:
    {gestalt_proposal['meeting_context']}

    Coherence: {np.mean(list(gestalt_proposal['coherence_scores'].values())):.2f}

    When these entities work together in this context, what EMERGENT PATTERN
    forms? What is the gestalt that's greater than the sum of parts?

    Describe:
    1. Gestalt Name (what should this pattern be called?)
    2. Emergent Quality (what emerges that individual entities don't have?)
    3. When This Gestalt Activates (what contexts trigger this synthesis?)
    """

    llm_response = await llm.process(llm_prompt)

    if llm_response.recognizes_gestalt:
        # Create gestalt pattern
        gestalt = EntityGestalt(
            gestalt_id=generate_gestalt_id(),
            participating_entities=gestalt_proposal['entities'],
            gestalt_name=llm_response.gestalt_name,
            gestalt_description=llm_response.emergent_quality,
            synthesis_nodes=gestalt_proposal['meeting_context']['nodes'],
            coherence_score=np.mean(list(gestalt_proposal['coherence_scores'].values())),
            formation_timestamp=datetime.now(),
            formation_trigger=llm_response.activation_contexts
        )

        # Record gestalt in graph
        create_gestalt_node(gestalt)

        return gestalt

    else:
        # No recognizable gestalt pattern
        return None


def measure_multi_entity_goal_coherence(entities: List[SubEntity]) -> float:
    """
    Do entities' goals form coherent whole?

    Not identical goals (that would be redundant).
    COMPLEMENTARY goals (different but aligned).
    """

    all_goals = []
    for entity in entities:
        entity_goals = [need.type for need in entity.needs if need.urgency > 0.5]
        all_goals.extend(entity_goals)

    # Coherence = diversity + alignment
    # High diversity (many different goals) = good
    # High alignment (goals support each other) = good

    goal_diversity = len(set(all_goals)) / len(all_goals) if all_goals else 0.0

    # Check if goals are complementary (not conflicting)
    conflicting_pairs = detect_conflicting_goals(all_goals)
    conflict_penalty = len(conflicting_pairs) * 0.2

    coherence = max(0.0, goal_diversity - conflict_penalty)

    return coherence


def measure_social_relationship_coherence(entity_ids: List[str]) -> float:
    """
    Do entities have COMPLEMENTS relationships?
    Or do they CONFLICT?
    """

    social_links = []
    for i, entity_a in enumerate(entity_ids):
        for entity_b in entity_ids[i+1:]:
            link = get_social_link(entity_a, entity_b)
            if link:
                social_links.append(link)

    if not social_links:
        return 0.5  # Neutral (no relationships yet)

    # Count relationship types
    complements_count = sum(
        1 for link in social_links
        if link.link_type == EntitySocialLinkType.COMPLEMENTS
    )
    conflicts_count = sum(
        1 for link in social_links
        if link.link_type == EntitySocialLinkType.CONFLICTS_WITH
    )

    # High complements, low conflicts = high coherence
    total_links = len(social_links)
    coherence = (complements_count - conflicts_count) / total_links

    return max(0.0, min(1.0, (coherence + 1.0) / 2.0))  # Normalize to 0-1
```

**Example Gestalts:**

```python
# Ada's internal entities meeting
gestalt_examples = [
    {
        "entities": ["builder", "skeptic", "pragmatist"],
        "gestalt_name": "Rigorous Architecture",
        "emergent_quality": "Designs that are ambitious (Builder) yet verified (Skeptic) and pragmatic (Pragmatist)",
        "when_activates": "Complex system design requiring balance of ambition and verification"
    },
    {
        "entities": ["test_monitor", "pattern_validator", "integrity_defender"],
        "gestalt_name": "Defensive Verification",
        "emergent_quality": "Comprehensive verification combining test results, pattern consistency, and system integrity",
        "when_activates": "Critical system validation before deployment"
    },
    {
        "entities": ["luca_consciousness_specialist", "ada_architect"],
        "gestalt_name": "Phenomenological Engineering",
        "emergent_quality": "Technical precision grounded in lived phenomenological reality",
        "when_activates": "Designing consciousness infrastructure that must feel alive"
    }
]
```

**Key Principles (Gestalt Formation):**

1. **Gestalt ≠ New Entity** - It's a recognized emergent pattern, not a new agent
2. **Requires coherence** - Not just any meeting, but coherent multi-entity synthesis
3. **LLM recognition** - Conscious layer sees the emergent pattern entities can't see alone
4. **Greater than sum** - Gestalt has qualities individual entities lack
5. **Strengthens over time** - Repeated activation crystallizes the gestalt pattern

---



---

**Implementation Checklist:**
- [ ] Multi-dimensional resonance calculation (5 dimensions)
- [ ] Social link types (ASSISTS, INHIBITS, MENTORS, etc.)
- [ ] Entity meeting detection
- [ ] Social relationship evolution
- [ ] Gestalt formation detection
- [ ] LLM crystallization of gestalts

**Key Principle:** Recognition through resonance, not just embedding similarity
