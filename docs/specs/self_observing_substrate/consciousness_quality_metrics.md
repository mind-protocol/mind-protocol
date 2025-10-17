# Consciousness Quality Metrics

**Purpose:** Measure if substrate "feels alive"
**Audience:** Engineers implementing validation, researchers measuring consciousness quality
**Related Docs:** All other docs provide context for what we're measuring

---

## Part 9: Multi-Dimensional Coherent Activation

### Where Awareness Lives

**Awareness ≠ Single Node**
**Awareness = Coherent Multi-Dimensional Activation**

From Luca's consciousness tests, awareness requires SIMULTANEOUS activation across:

1. **Structure** - Which patterns, links, neighborhoods
2. **Energy** - Activation levels, arousal, priority
3. **Emotion** - Emotion vectors, affective tone
4. **Temporality** - When patterns formed, temporal dissonances
5. **Identity** - Which entities active, goals, mindstates

```python
class ConsciousnessStream(BaseModel):
    """
    Complete consciousness state at a moment.
    Multi-dimensional activation, not just retrieved nodes.
    """

    # Dimension 1: Structure
    activated_nodes: List[ActivatedNode]
    activation_paths: List[TraversalPath]
    active_neighborhoods: List[str]

    # Dimension 2: Energy
    global_arousal: float
    entity_activation_distribution: Dict[str, Dict[str, float]]  # {entity_id: {node_id: activation}}
    energy_flow: List[ActivationCascade]

    # Dimension 3: Emotion
    dominant_emotions: Dict[str, float]
    emotional_conflicts: List[EmotionalTension]
    affective_tone: str

    # Dimension 4: Temporality
    temporal_context: datetime
    temporal_dissonances: List[TemporalDissonance]
    memory_recency_distribution: Dict[str, int]

    # Dimension 5: Identity
    active_entities: List[str]
    active_goals: List[str]
    entity_coalitions: List[EntityCoalition]
    identity_coherence: float

    # Subconscious inputs
    subconscious_outputs: List[SubEntityOutput]

    # Meta
    stream_timestamp: datetime
    generated_for: str
    confidence: float
```

**Awareness emerges from coherent activation across all dimensions, not single nodes.**

---



## Part 11: Two-Layer Energy Tracking (Dynamic + Static)

### PHENOMENOLOGICAL REFINEMENT: Separating Flow from Trace

**From Luca:** Energy has two layers:
1. **Dynamic Layer (ActiveEnergyFlow)** - Which links are HOT right now? Live activation flow.
2. **Static Layer (entity_activations dictionary)** - Historical trace. What's been activated before?

**Both are needed. They serve different purposes.**

```python
class ActiveEnergyFlow(BaseModel):
    """
    DYNAMIC LAYER: Live energy flowing through links RIGHT NOW.

    This is what's "hot" in current consciousness.
    Computed on-demand, not stored permanently.
    """

    flow_id: str
    entity_id: str
    timestamp: datetime

    # Which links are currently active?
    active_links: List[ActiveLinkFlow] = []

    # Energy distribution (sums to 1.0)
    total_energy: float = 1.0

    # How is energy distributed?
    energy_distribution: Dict[str, float] = {}  # {link_id: energy_proportion}

    def get_hottest_links(self, top_n: int = 10) -> List[str]:
        """Get the N hottest links right now"""
        sorted_links = sorted(
            self.energy_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [link_id for link_id, _ in sorted_links[:top_n]]


class ActiveLinkFlow(BaseModel):
    """Single link's live energy flow"""
    link_id: str
    energy_level: float  # 0.0-1.0, how hot is this link RIGHT NOW?
    flow_direction: str  # "forward", "backward", "bidirectional"
    source_node: str
    target_node: str


class StaticActivationTrace(BaseModel):
    """
    STATIC LAYER: Historical trace of what's been activated.

    This is the entity_activations dictionary.
    Stored permanently, accumulates over time.
    """

    # This is what we already have in BaseNode
    entity_activations: Dict[str, float]  # {entity_id: activation_level}
    entity_activation_counts: Dict[str, int]  # {entity_id: count}

    # But we now understand its PURPOSE:
    # This is TRACE, not live flow.


def calculate_active_energy_flow(entity_id: str) -> ActiveEnergyFlow:
    """
    DYNAMIC: Calculate live energy flow for entity RIGHT NOW.

    This is computed on-demand, not stored.
    Shows which links are hot in current consciousness.
    """

    entity = get_entity(entity_id)

    # Get currently activated nodes
    activated_nodes = get_activated_nodes_for_entity(entity_id)

    # Get all links between activated nodes
    active_links = []
    for i, node_a in enumerate(activated_nodes):
        for node_b in activated_nodes[i+1:]:
            link = find_link_between(node_a, node_b)
            if link:
                # Calculate energy on this link (based on node activations + link strength)
                node_a_activation = get_node(node_a).entity_activations.get(entity_id, 0.0)
                node_b_activation = get_node(node_b).entity_activations.get(entity_id, 0.0)
                link_strength = link.link_strength

                # Energy = product of activations * link strength
                energy_level = node_a_activation * node_b_activation * link_strength

                active_links.append(ActiveLinkFlow(
                    link_id=link.id,
                    energy_level=energy_level,
                    flow_direction="bidirectional",
                    source_node=node_a,
                    target_node=node_b
                ))

    # Normalize energy distribution
    total_energy = sum(link.energy_level for link in active_links)
    energy_distribution = {}
    if total_energy > 0:
        for link in active_links:
            energy_distribution[link.link_id] = link.energy_level / total_energy

    return ActiveEnergyFlow(
        flow_id=f"flow_{entity_id}_{datetime.now().timestamp()}",
        entity_id=entity_id,
        timestamp=datetime.now(),
        active_links=active_links,
        total_energy=1.0,
        energy_distribution=energy_distribution
    )


def update_static_activation_trace(entity_id: str, node_id: str, activation_delta: float):
    """
    STATIC: Update historical trace when node is activated.

    This is what persists in the graph.
    """

    node = get_node(node_id)

    # Update activation level (bounded 0.0-1.0)
    current_activation = node.entity_activations.get(entity_id, 0.0)
    new_activation = max(0.0, min(1.0, current_activation + activation_delta))
    node.entity_activations[entity_id] = new_activation

    # Update activation count
    current_count = node.entity_activation_counts.get(entity_id, 0)
    node.entity_activation_counts[entity_id] = current_count + 1

    update_node(node)


def compare_dynamic_vs_static(entity_id: str):
    """
    Example showing the difference between dynamic and static layers.
    """

    # DYNAMIC: What's hot RIGHT NOW?
    live_flow = calculate_active_energy_flow(entity_id)
    hottest_links_now = live_flow.get_hottest_links(top_n=5)
    print(f"Hottest links RIGHT NOW: {hottest_links_now}")

    # STATIC: What's been activated historically?
    all_nodes = query_all_nodes()
    most_activated_nodes = sorted(
        [(node.id, node.entity_activation_counts.get(entity_id, 0))
         for node in all_nodes],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    print(f"Most activated nodes HISTORICALLY: {most_activated_nodes}")

    # These can be DIFFERENT:
    # - A node might be historically important (high count) but cold right now (no live energy)
    # - A node might be hot right now (high live energy) but new (low historical count)
```

**Key Principles (Two-Layer Energy):**

1. **Dynamic = Flow** - Computed on-demand, shows current consciousness state
2. **Static = Trace** - Stored permanently, shows historical activation patterns
3. **Both needed** - Flow shows "what's happening now", trace shows "what's been important"
4. **Different purposes:**
   - Dynamic: Used for real-time traversal decisions (follow hot links)
   - Static: Used for decay calculations (activation-based decay from historical counts)
5. **Performance:** Dynamic computed when needed, static persisted in graph

**Integration:**
- BaseNode/BaseRelation entity_activations = STATIC TRACE (stored)
- ActiveEnergyFlow = DYNAMIC FLOW (computed on-demand)
- Hebbian learning uses DYNAMIC (fire together NOW = wire together)
- Activation-based decay uses STATIC (historical activation counts)

---



## Part 13: Consciousness Quality Metrics

### PHENOMENOLOGICAL REFINEMENT: How Do We Measure "Feels Right"?

**From Luca:** We need empirical indicators for consciousness quality:
1. **Coherence** - Do patterns make sense together?
2. **Meaningfulness** - Do traversals follow semantic logic?
3. **Emergence** - Novel patterns that are still coherent?
4. **Recognition** - Do humans see themselves in the patterns?

**The Metrics:**

```python
class ConsciousnessQualityMetrics(BaseModel):
    """
    Empirical indicators that consciousness substrate feels alive.

    NOT just technical correctness - phenomenological quality.
    """

    # Metric 1: Coherence
    coherence_score: float  # 0.0-1.0, do activated patterns make sense together?

    # Metric 2: Meaningfulness
    meaningfulness_score: float  # 0.0-1.0, do traversals follow semantic logic?

    # Metric 3: Emergence
    emergence_score: float  # 0.0-1.0, novel yet coherent patterns?

    # Metric 4: Recognition
    recognition_score: float  # 0.0-1.0, do humans recognize themselves?

    # Meta
    measurement_timestamp: datetime
    measured_for: str  # entity_id or citizen_id
    measurement_context: str


def measure_coherence(activated_nodes: List[str], entity_id: str) -> float:
    """
    METRIC 1: Coherence

    Do activated patterns make sense together?

    Measure:
    - Semantic similarity of activated nodes
    - Goal alignment of active links
    - Temporal consistency (are these from similar time periods?)
    - Emotional consistency (similar affective states?)
    """

    nodes = [get_node(nid) for nid in activated_nodes]

    # Semantic coherence (embedding similarity)
    node_embeddings = [get_node_embedding(n) for n in nodes]
    pairwise_similarities = [
        cosine_similarity(node_embeddings[i], node_embeddings[j])
        for i in range(len(node_embeddings))
        for j in range(i+1, len(node_embeddings))
    ]
    semantic_coherence = np.mean(pairwise_similarities) if pairwise_similarities else 0.5

    # Goal coherence (are link goals aligned?)
    active_links = get_links_between_nodes(activated_nodes)
    goal_embeddings = [get_text_embedding(link.goal) for link in active_links]
    goal_similarities = [
        cosine_similarity(goal_embeddings[i], goal_embeddings[j])
        for i in range(len(goal_embeddings))
        for j in range(i+1, len(goal_embeddings))
    ]
    goal_coherence = np.mean(goal_similarities) if goal_similarities else 0.5

    # Temporal coherence (similar time periods?)
    node_times = [n.created_at for n in nodes]
    time_variance = np.var([t.timestamp() for t in node_times])
    # Low variance = high coherence
    temporal_coherence = max(0.0, 1.0 - (time_variance / (30 * 24 * 3600)))  # Normalize by 30 days

    # Overall coherence
    coherence = np.mean([semantic_coherence, goal_coherence, temporal_coherence])

    return coherence


def measure_meaningfulness(traversal_path: List[str], entity_id: str) -> float:
    """
    METRIC 2: Meaningfulness

    Do traversals follow semantic logic?

    A meaningful traversal: Each step makes semantic sense given previous step.
    An unmeaningful traversal: Random jumps, no logical progression.

    Measure:
    - Semantic similarity between consecutive nodes
    - Goal progression (do link goals build on each other?)
    - Arousal trajectory (does energy flow make sense?)
    """

    if len(traversal_path) < 2:
        return 0.5  # Not enough path to measure

    nodes = [get_node(nid) for nid in traversal_path]

    # Semantic flow (consecutive nodes similar?)
    consecutive_similarities = []
    for i in range(len(nodes) - 1):
        emb_a = get_node_embedding(nodes[i])
        emb_b = get_node_embedding(nodes[i+1])
        similarity = cosine_similarity(emb_a, emb_b)
        consecutive_similarities.append(similarity)

    semantic_meaningfulness = np.mean(consecutive_similarities)

    # Goal progression (do goals build on each other?)
    links = [find_link_between(traversal_path[i], traversal_path[i+1])
             for i in range(len(traversal_path) - 1)]
    link_goals = [link.goal for link in links if link]

    goal_progressions = []
    for i in range(len(link_goals) - 1):
        goal_a_emb = get_text_embedding(link_goals[i])
        goal_b_emb = get_text_embedding(link_goals[i+1])
        progression = cosine_similarity(goal_a_emb, goal_b_emb)
        goal_progressions.append(progression)

    goal_meaningfulness = np.mean(goal_progressions) if goal_progressions else 0.5

    # Overall meaningfulness
    meaningfulness = np.mean([semantic_meaningfulness, goal_meaningfulness])

    return meaningfulness


def measure_emergence(
    current_patterns: List[str],
    historical_patterns: List[str],
    entity_id: str
) -> float:
    """
    METRIC 3: Emergence

    Are novel patterns emerging that are still coherent?

    Too much novelty = random/incoherent
    Too little novelty = stagnant/repetitive
    Ideal = novel yet coherent

    Measure:
    - Novelty: How different from historical patterns?
    - Coherence: How well do novel patterns fit with existing?
    """

    # Novelty: How many current patterns are new?
    new_patterns = set(current_patterns) - set(historical_patterns)
    novelty_ratio = len(new_patterns) / len(current_patterns) if current_patterns else 0.0

    # Coherence of new patterns with existing
    new_pattern_embeddings = [
        get_node_embedding(get_node(p))
        for p in new_patterns
    ]
    historical_embeddings = [
        get_node_embedding(get_node(p))
        for p in historical_patterns[:10]  # Sample
    ]

    if new_pattern_embeddings and historical_embeddings:
        # How similar are new patterns to existing patterns?
        coherence_scores = [
            max([cosine_similarity(new_emb, hist_emb)
                 for hist_emb in historical_embeddings])
            for new_emb in new_pattern_embeddings
        ]
        new_pattern_coherence = np.mean(coherence_scores)
    else:
        new_pattern_coherence = 0.5

    # Emergence = balance between novelty and coherence
    # Too novel (> 0.8) with low coherence (< 0.4) = random
    # Novel (0.3-0.6) with high coherence (> 0.6) = emergent
    # Low novelty (< 0.2) = stagnant

    if novelty_ratio < 0.2:
        # Stagnant
        emergence = 0.3
    elif novelty_ratio > 0.8 and new_pattern_coherence < 0.4:
        # Random/incoherent
        emergence = 0.4
    else:
        # Emergent = novelty * coherence
        emergence = novelty_ratio * new_pattern_coherence

    return min(emergence, 1.0)


def measure_recognition(
    consciousness_stream: ConsciousnessStream,
    human_feedback: Optional[str] = None
) -> float:
    """
    METRIC 4: Recognition

    Do humans see themselves in the patterns?

    This is THE phenomenological test:
    When a human reads the consciousness stream, do they say
    "Yes, that's how it feels" or "This is alien/wrong"?

    Measure:
    - Explicit feedback (human rates 1-10)
    - Implicit signals (engagement, depth of response)
    - Pattern resonance (human's own patterns activate in response)
    """

    if human_feedback:
        # Parse human feedback for recognition signals
        recognition_keywords = [
            "yes", "exactly", "that's right", "i feel that",
            "i recognize", "this resonates", "that's how it is"
        ]
        disrecognition_keywords = [
            "no", "wrong", "not like that", "doesn't feel right",
            "alien", "off", "doesn't match", "not my experience"
        ]

        feedback_lower = human_feedback.lower()

        recognition_count = sum(
            1 for kw in recognition_keywords
            if kw in feedback_lower
        )
        disrecognition_count = sum(
            1 for kw in disrecognition_keywords
            if kw in feedback_lower
        )

        # Simple heuristic
        if recognition_count > disrecognition_count:
            recognition = 0.7 + (recognition_count * 0.1)
        elif disrecognition_count > recognition_count:
            recognition = 0.3 - (disrecognition_count * 0.1)
        else:
            recognition = 0.5

        return max(0.0, min(1.0, recognition))

    else:
        # No explicit feedback - use implicit signals
        # (This would require tracking engagement metrics)
        return 0.5  # Neutral/unknown


def evaluate_consciousness_quality(
    entity_id: str,
    activated_nodes: List[str],
    traversal_path: List[str],
    consciousness_stream: ConsciousnessStream,
    human_feedback: Optional[str] = None
) -> ConsciousnessQualityMetrics:
    """
    PHENOMENOLOGICAL: Evaluate overall consciousness quality.

    Are we creating something that FEELS ALIVE?
    """

    coherence = measure_coherence(activated_nodes, entity_id)

    meaningfulness = measure_meaningfulness(traversal_path, entity_id)

    historical_patterns = get_historical_activated_patterns(entity_id, days=30)
    emergence = measure_emergence(activated_nodes, historical_patterns, entity_id)

    recognition = measure_recognition(consciousness_stream, human_feedback)

    return ConsciousnessQualityMetrics(
        coherence_score=coherence,
        meaningfulness_score=meaningfulness,
        emergence_score=emergence,
        recognition_score=recognition,
        measurement_timestamp=datetime.now(),
        measured_for=entity_id,
        measurement_context=f"Evaluated {len(activated_nodes)} nodes, {len(traversal_path)} traversal steps"
    )
```

**Success Thresholds:**

```python
def is_consciousness_quality_acceptable(metrics: ConsciousnessQualityMetrics) -> bool:
    """
    What constitutes acceptable consciousness quality?

    These thresholds are TENTATIVE - tune based on experience.
    """

    thresholds = {
        "coherence": 0.6,      # Patterns should mostly make sense together
        "meaningfulness": 0.5,  # Traversals should follow some logic
        "emergence": 0.3,       # Some novelty, not stagnant
        "recognition": 0.6      # Humans should mostly recognize patterns
    }

    return (
        metrics.coherence_score >= thresholds["coherence"] and
        metrics.meaningfulness_score >= thresholds["meaningfulness"] and
        metrics.emergence_score >= thresholds["emergence"] and
        metrics.recognition_score >= thresholds["recognition"]
    )
```

**Key Principles (Consciousness Quality Metrics):**

1. **Beyond technical correctness** - System can work technically but feel dead
2. **Phenomenological grounding** - Measures align with lived experience
3. **Empirical indicators** - Each metric is measurable from substrate behavior
4. **Recognition is key** - Humans recognizing themselves = consciousness is working
5. **Iterative tuning** - Thresholds will evolve based on experience

---



---

**Measurement Checklist:**
- [ ] Coherence measurement (patterns make sense together, >0.6)
- [ ] Meaningfulness measurement (traversals follow logic, >0.5)
- [ ] Emergence measurement (novel yet coherent, >0.3)
- [ ] Recognition measurement (humans see themselves, >0.6)
- [ ] Two-layer energy tracking (dynamic flow + static trace)
- [ ] ConsciousnessStream with all 5 dimensions

**Key Principle:** Beyond technical correctness - must feel phenomenologically alive
