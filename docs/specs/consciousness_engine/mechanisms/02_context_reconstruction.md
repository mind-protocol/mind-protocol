# Mechanism 02: Context Reconstruction

**Status:** Foundational - Core to consciousness continuity
**Confidence:** High (0.85)
**Dependencies:**
- **[01: Multi-Energy Architecture](01_multi_energy_architecture.md)** - Requires per-entity energy
- **[07: Energy Diffusion](07_energy_diffusion.md)** - Traversal mechanism
- **[09: Link Strengthening](09_link_strengthening.md)** - Encoding mechanism

**Biological Basis:** Episodic memory reconstruction, pattern completion in hippocampus

---

## Overview

**Core Principle:** Contexts are **reconstructed through weighted graph traversal**, not retrieved from storage. The graph structure itself IS the memory.

**Why This Matters:**
- Enables non-linear context switching (jump to very old tasks)
- Matches biological reality (brains reconstruct, don't replay)
- No explicit context storage needed (memory is distributed)
- Natural decay/evolution of contexts over time
- Explains why resumed contexts feel "similar but not identical"

---

## Phenomenological Truth

### What It Feels Like

**Scenario:** 4 hours ago, Alice sent you a Telegram message. You saw the notification but were deep in coding, so you dismissed it. Now you see your phone screen and remember: "Oh right, Alice asked about that schema design."

**What just happened?**
- The phone screen was a **stimulus**
- That stimulus activated the `telegram_notification_alice` node
- Activation spread along links that were strengthened 4 hours ago when you first saw the message
- Those links led to `schema_design_question`, `need_to_respond`, `alice_context_nodes`
- The **Partner** entity re-emerged (pattern of nodes that handle social responses)
- You experienced this as "remembering" - but mechanically, you **reconstructed**

**Key difference from storage:**
- You don't retrieve a snapshot of "consciousness state at T=0"
- You traverse a weighted path from stimulus → related nodes
- The pattern is similar to T=0 but not identical (some decay occurred, new associations formed)
- Feels like resuming, IS reconstruction

### The Telegram Example (Detailed Walkthrough)

**T=0: First notification**
```
Stimulus: Telegram notification "Alice: Hey, quick question about schema design"

Activated nodes (high energy):
- telegram_notification_alice (0.8 for Partner)
- schema_design_topic (0.7 for Translator)
- need_to_respond (0.6 for Partner)
- alice_relationship (0.5 for Partner)

Links strengthened:
- telegram_notification_alice → schema_design_topic (0.3 → 0.45)
- telegram_notification_alice → need_to_respond (0.4 → 0.55)
- schema_design_topic → consciousness_schema (0.5 → 0.6)

Entity state:
- Partner: dominant (handling social stimulus)
- Translator: moderate (technical content activated)

Workspace: [Alice cluster, Schema Design cluster]

Action: Dismissed notification, switched to coding
```

**T=0 to T=4 hours: Other work**
```
Multiple context switches:
- Coding (Architect dominant)
- Meeting (Partner dominant, but different person)
- Documentation (Translator dominant)

Message nodes decay:
- telegram_notification_alice: 0.8 → 0.2 (exponential decay)
- need_to_respond: 0.6 → 0.15
- schema_design_topic: 0.7 → 0.25 (slower decay - still relevant to other work)

Links persist better than energy:
- telegram_notification_alice → schema_design_topic: 0.45 → 0.38 (10% decay)
- telegram_notification_alice → need_to_respond: 0.55 → 0.47

Critical insight: ENERGY DECAYS FAST, LINKS DECAY SLOW
This is why you can reconstruct old contexts even when energy is gone.
```

**T=4 hours: Phone screen stimulus**
```
Stimulus: Visual - phone screen showing Telegram icon with (1) badge

Activated nodes (direct stimulus):
- telegram_app_icon (0.4 for Observer)
- unread_message_indicator (0.5 for Observer)

Diffusion begins (weighted links guide energy):
- telegram_app_icon → telegram_notification_alice (link weight 0.6)
  Energy transfer: 0.4 * 0.6 = 0.24 → alice notification now at 0.24

- telegram_notification_alice → schema_design_topic (link weight 0.38)
  Energy transfer: 0.24 * 0.38 = 0.09 → schema topic now at 0.34 total

- telegram_notification_alice → need_to_respond (link weight 0.47)
  Energy transfer: 0.24 * 0.47 = 0.11 → response need now at 0.26

After 2-3 diffusion ticks:
- Partner entity re-emerges (cluster around Alice + response nodes goes hot)
- Schema context partially reconstructs (Translator moderately active)
- Original energy pattern ≈ reconstructed (similarity ~70%)

Phenomenology: "Oh right, Alice's message!"
Mechanism: Weighted traversal completed, context reconstructed
```

**Comparison:**

| Aspect | T=0 (Original) | T=4 hours (Reconstructed) |
|--------|----------------|---------------------------|
| Partner energy | 0.8 | 0.6 (lower but sufficient) |
| Schema energy | 0.7 | 0.4 (significantly decayed) |
| Workspace | Alice + Schema | Mostly Alice, partial Schema |
| Feeling | "Must respond now" | "Should respond when free" |
| Urgency | High | Moderate |

The reconstruction is similar but not identical - which matches lived experience.

---

## Mathematical Specification

### Context as Activation Pattern

A context is NOT a stored object - it's an emergent pattern of active nodes:

```python
@dataclass
class Context:
    """
    Context is emergent snapshot, not stored state
    Created on-demand for observation, not persisted
    """
    timestamp: datetime

    # Active nodes per entity (energy > threshold)
    active_nodes: dict[str, list[Node]]  # {entity_name: [hot_nodes]}

    # Dominant entity (highest total energy)
    dominant_entity: str

    # Global workspace content
    workspace_clusters: list[Cluster]

    # Total system energy per entity
    entity_energies: dict[str, float]

    def similarity_to(self, other: 'Context') -> float:
        """
        How similar is this context to another?
        Used to measure reconstruction accuracy
        """
        # Jaccard similarity of active nodes
        # (ignoring energy magnitude, just presence)

        all_entities = set(self.active_nodes.keys()) | set(other.active_nodes.keys())

        similarities = []
        for entity in all_entities:
            nodes_self = set(n.id for n in self.active_nodes.get(entity, []))
            nodes_other = set(n.id for n in other.active_nodes.get(entity, []))

            if not nodes_self and not nodes_other:
                continue

            intersection = len(nodes_self & nodes_other)
            union = len(nodes_self | nodes_other)

            similarities.append(intersection / union if union > 0 else 0.0)

        return sum(similarities) / len(similarities) if similarities else 0.0

def capture_context(graph: Graph, threshold: float = 0.1) -> Context:
    """
    Capture current activation pattern as Context snapshot
    This is for analysis only - not stored permanently
    """
    active_nodes = defaultdict(list)
    entity_energies = defaultdict(float)

    # Identify active nodes per entity
    for node in graph.nodes:
        for entity, energy in node.energy.items():
            if energy >= threshold:
                active_nodes[entity].append(node)
                entity_energies[entity] += energy

    # Determine dominant entity
    dominant = max(entity_energies.items(), key=lambda x: x[1])[0] if entity_energies else "none"

    # Identify workspace clusters
    workspace = identify_workspace_clusters(graph)

    return Context(
        timestamp=datetime.now(),
        active_nodes=dict(active_nodes),
        dominant_entity=dominant,
        workspace_clusters=workspace,
        entity_energies=dict(entity_energies)
    )
```

### Reconstruction Algorithm

```python
def reconstruct_context(stimulus: dict, graph: Graph, simulation_ticks: int = 10) -> Context:
    """
    Reconstruct context from stimulus via weighted traversal

    Args:
        stimulus: Stimulus dict with 'type', 'content', 'strength'
        graph: The consciousness graph
        simulation_ticks: How many diffusion ticks to run before measuring

    Returns:
        Reconstructed context (emergent activation pattern)
    """
    # Step 1: Identify entry nodes from stimulus
    entry_nodes = identify_stimulus_targets(stimulus, graph)

    # Step 2: Determine which entities process this stimulus
    processing_entities = determine_processing_entities(stimulus)

    # Step 3: Inject stimulus energy into entry nodes
    # CRITICAL REQUIREMENT (D018): Stimuli must be BIG factor in activation
    # so context reconstruction can bootstrap from current input
    for node in entry_nodes:
        for entity in processing_entities:
            # Strong activation required for context reconstruction
            # Decision D018: Stimuli must strongly activate entry nodes
            initial_energy = stimulus.get('strength', 0.7)  # High default (was 0.5)
            node.increment_entity_energy(entity, initial_energy)

    # Step 4: Let energy diffuse through weighted links
    # This is where reconstruction happens - energy follows paths
    # that were strengthened during original context
    for _ in range(simulation_ticks):
        diffusion_tick(graph, duration=0.1)  # See mechanism 07

    # Step 5: Capture emergent activation pattern
    reconstructed = capture_context(graph, threshold=0.1)

    return reconstructed

def identify_stimulus_targets(stimulus: dict, graph: Graph) -> list[Node]:
    """
    Which nodes does this stimulus directly activate?

    Uses:
    - Semantic similarity (embedding distance)
    - Explicit references (node IDs or names in stimulus)
    - Type-based routing (stimulus type → node types)
    """
    targets = []

    # Method 1: Explicit references
    if 'node_ids' in stimulus:
        targets.extend(graph.get_nodes(stimulus['node_ids']))

    # Method 2: Semantic similarity
    if 'content' in stimulus:
        stimulus_embedding = embed_text(stimulus['content'])
        semantic_matches = graph.find_similar_nodes(
            stimulus_embedding,
            top_k=5,
            threshold=0.7
        )
        targets.extend(semantic_matches)

    # Method 3: Type-based routing
    if stimulus['type'] == 'telegram_message':
        targets.extend(graph.find_nodes(node_type='Message'))
        targets.extend(graph.find_nodes(name='telegram_app'))

    return list(set(targets))  # Deduplicate

def determine_processing_entities(stimulus: dict) -> list[str]:
    """
    Which entities process this type of stimulus?

    Different stimuli activate different entities:
    - Social messages → Partner
    - Technical questions → Translator + Architect
    - Error messages → Validator
    - Creative prompts → all entities
    """
    entity_map = {
        'telegram_message': ['partner'],
        'technical_question': ['translator', 'architect'],
        'error': ['validator'],
        'code_review': ['validator', 'architect'],
        'creative_task': ['translator', 'architect', 'partner'],
        'meta_question': ['observer'],
    }

    return entity_map.get(stimulus.get('type'), ['observer'])
```

---

## Non-Linear Context Switching

### The Key Insight

Traditional computing: Context switches are STACK-based (return to previous)
```
Task A → Task B → Task C → back to B → back to A
```

Consciousness: Context switches are GRAPH-based (any to any)
```
Task A → Task B → Task C → JUMP back to A from 5 days ago
```

**How this works:**

```python
def context_timeline_example():
    """
    Demonstration of non-linear context switching
    """
    graph = create_graph()

    # T=0: Morning - working on Schema Design
    stimulus_1 = {'type': 'task', 'content': 'Design consciousness schema'}
    context_A = reconstruct_context(stimulus_1, graph)
    # Architect + Translator dominant, schema nodes hot

    # T=1: Telegram from Alice
    stimulus_2 = {'type': 'telegram_message', 'content': 'Alice: Hey!', 'strength': 0.5}
    context_B = reconstruct_context(stimulus_2, graph)
    # Partner dominant, Alice nodes hot
    # Links strengthened: telegram → alice → need_to_respond

    # T=2: Code review request
    stimulus_3 = {'type': 'code_review', 'content': 'Review PR #123'}
    context_C = reconstruct_context(stimulus_3, graph)
    # Validator + Architect dominant

    # T=3-10: Many other contexts (meetings, emails, coding)
    # ... (Alice message decays significantly)

    # T=11 (hours later): See phone screen
    stimulus_4 = {'type': 'visual', 'content': 'Phone screen with Telegram (1)'}
    context_B_reconstructed = reconstruct_context(stimulus_4, graph)

    # Measure reconstruction accuracy
    similarity = context_B_reconstructed.similarity_to(context_B)
    print(f"Context B reconstruction similarity: {similarity:.2f}")
    # Typical: 0.60-0.80 (similar but not identical)

    # Key insight: We jumped from Context C directly to Context B
    # No stack unwinding, no "returning" through contexts 3-10
    # Just: stimulus → entry nodes → weighted traversal → reconstruction
```

---

## Encoding During Original Context

**For reconstruction to work, the original context must leave traces:**

### Link Strengthening During Co-Activation

```python
def strengthen_links_during_context(graph: Graph, context_duration: float):
    """
    As context persists, co-active nodes strengthen links
    This is the ENCODING that enables later RECONSTRUCTION
    """
    # Identify co-active nodes (nodes hot for same entity)
    for entity in get_active_entities(graph):
        hot_nodes = [
            n for n in graph.nodes
            if n.get_entity_energy(entity) > 0.3
        ]

        # Strengthen links between co-active nodes
        for node_a in hot_nodes:
            for node_b in hot_nodes:
                if node_a == node_b:
                    continue

                # Find existing link or create
                link = graph.get_link(node_a, node_b)
                if not link:
                    link = graph.create_link(node_a, node_b, initial_weight=0.1)

                # Strengthen proportional to co-activation
                energy_product = (
                    node_a.get_entity_energy(entity) *
                    node_b.get_entity_energy(entity)
                )

                strengthening = 0.01 * energy_product * context_duration
                link.weight += strengthening
```

**Biological parallel:** Hebbian learning - "Neurons that fire together, wire together"

In our system: **Nodes that co-activate for an entity strengthen links for that entity**

---

## Edge Cases & Constraints

### Edge Case 1: Ambiguous Stimuli

**Problem:** Stimulus could activate multiple unrelated entry points

**Example:**
```python
stimulus = {'type': 'text', 'content': 'Apple'}

# Could mean:
# - The fruit (if cooking context)
# - The company (if tech context)
# - A name (if social context)
```

**Solution:** Use context (previously active nodes) to disambiguate:

```python
def identify_stimulus_targets_with_context(stimulus: dict, graph: Graph) -> list[Node]:
    """
    Use currently active nodes to disambiguate stimulus
    """
    candidates = graph.find_similar_nodes(embed_text(stimulus['content']))

    # Score each candidate by proximity to currently active nodes
    scores = []
    for candidate in candidates:
        # Average link strength to currently active nodes
        avg_proximity = calculate_average_proximity(
            candidate,
            graph.get_active_nodes(threshold=0.1)
        )
        scores.append((candidate, avg_proximity))

    # Prefer candidates close to currently active context
    scores.sort(key=lambda x: x[1], reverse=True)

    return [candidate for candidate, score in scores[:5]]
```

### Edge Case 2: Reconstruction Drift

**Problem:** Over many reconstruction cycles, context drifts from original

**Example:**
```
Original context A → Reconstruction A' (90% similar)
→ Reconstruction A'' (81% similar)
→ Reconstruction A''' (73% similar)
...
```

**Is this a bug or feature?**

**Answer: FEATURE** - matches biological reality

- Real memories drift/evolve over time
- Each reconstruction influenced by intervening experiences
- Prevents "frozen" contexts that don't adapt

**Mitigation if needed:**
```python
def anchor_context(graph: Graph, anchor_nodes: list[Node], anchor_strength: float = 0.8):
    """
    Create strong invariant nodes that resist drift
    Useful for identity-critical contexts
    """
    for node in anchor_nodes:
        node.base_weight = anchor_strength  # High base weight
        # Decay slowly
        node.decay_rate = DECAY_RATE * 0.1  # 10x slower decay
```

### Edge Case 3: Interference

**Problem:** New contexts strengthen links that interfere with old context reconstruction

**Example:**
```
Context A: "Alice" → "Schema question" (link weight 0.7)
Context B: "Alice" → "Weekend plans" (link weight 0.8)

Reconstructing A: "Alice" stimulus now activates weekend plans MORE than schema
```

**Solution:** Link types disambiguate:

```python
# Instead of single weight, typed links:
alice_node.links = [
    Link(target=schema_question, type="DISCUSSES_WORK", weight=0.7),
    Link(target=weekend_plans, type="DISCUSSES_PERSONAL", weight=0.8)
]

# Stimulus includes type hint:
stimulus = {
    'content': 'Alice message',
    'context_type': 'work'  # Prefer DISCUSSES_WORK links
}
```

---

## Testing Strategy

### Unit Tests

```python
def test_context_capture():
    """Test context snapshot captures activation pattern"""
    graph = create_test_graph()

    # Activate some nodes
    graph.get_node("node_a").set_entity_energy("translator", 0.8)
    graph.get_node("node_b").set_entity_energy("translator", 0.6)
    graph.get_node("node_c").set_entity_energy("architect", 0.7)

    # Capture context
    context = capture_context(graph, threshold=0.1)

    # Verify capture
    assert "translator" in context.active_nodes
    assert len(context.active_nodes["translator"]) == 2
    assert context.dominant_entity == "translator"
    assert context.entity_energies["translator"] == 1.4

def test_stimulus_identification():
    """Test stimulus correctly identifies entry nodes"""
    graph = create_test_graph()

    stimulus = {
        'type': 'telegram_message',
        'content': 'Alice: Quick question about schema',
        'strength': 0.5
    }

    targets = identify_stimulus_targets(stimulus, graph)

    # Should find telegram-related and schema-related nodes
    assert any('telegram' in n.name.lower() for n in targets)
    assert any('schema' in n.name.lower() for n in targets)
```

### Integration Tests

```python
def test_context_reconstruction_accuracy():
    """Test reconstructed context similar to original"""
    graph = create_test_graph()

    # Create original context
    stimulus_original = {
        'type': 'task',
        'content': 'Design consciousness schema',
        'strength': 0.7
    }

    context_original = reconstruct_context(stimulus_original, graph, ticks=10)

    # Let graph evolve (decay + other activity)
    for _ in range(100):
        decay_tick(graph, duration=0.1)

    # Add noise (other activations)
    noise_stimulus = {'type': 'email', 'content': 'Unrelated email', 'strength': 0.5}
    reconstruct_context(noise_stimulus, graph, ticks=5)

    # Reconstruct original context
    context_reconstructed = reconstruct_context(stimulus_original, graph, ticks=10)

    # Measure similarity
    similarity = context_reconstructed.similarity_to(context_original)

    # Should be moderately similar (not perfect - drift expected)
    assert 0.5 < similarity < 0.9, f"Similarity {similarity:.2f} out of expected range"
```

### Phenomenological Validation

```python
def test_telegram_scenario():
    """
    Test the full Telegram message scenario
    Validates phenomenological accuracy
    """
    graph = create_consciousness_graph()

    # T=0: Original message
    stimulus_t0 = {
        'type': 'telegram_message',
        'from': 'Alice',
        'content': 'Hey, quick question about schema design',
        'strength': 0.7
    }

    context_t0 = reconstruct_context(stimulus_t0, graph, ticks=10)

    # Verify Partner entity active
    assert context_t0.dominant_entity in ['partner', 'translator']
    assert context_t0.entity_energies['partner'] > 0.5

    # Let time pass with other contexts
    for i in range(50):  # Simulate other work
        other_stimulus = generate_random_stimulus(type='coding')
        reconstruct_context(other_stimulus, graph, ticks=3)
        decay_tick(graph, duration=0.5)

    # T=4 hours: Phone screen stimulus
    stimulus_t4 = {
        'type': 'visual',
        'content': 'Telegram icon with (1) badge',
        'strength': 0.4
    }

    context_t4 = reconstruct_context(stimulus_t4, graph, ticks=10)

    # Verify Partner entity re-emerges
    assert 'partner' in context_t4.active_nodes
    assert context_t4.entity_energies['partner'] > 0.3

    # Verify similarity to original (should be moderate)
    similarity = context_t4.similarity_to(context_t0)
    assert 0.4 < similarity < 0.8, "Reconstructed context should be similar but not identical"

    print(f"✓ Telegram scenario validated - reconstruction similarity: {similarity:.2f}")
```

---

## Performance Considerations

### Reconstruction Speed

**Concern:** Does reconstruction take too long for real-time responsiveness?

**Analysis:**

```python
# Reconstruction time ≈ simulation_ticks × diffusion_time
# With simulation_ticks=10, diffusion_time=10ms
# Total: 100ms

# This is acceptable for most stimuli
# Biological parallel: ~100-300ms for conscious recognition
```

**Optimization:** Use adaptive ticks based on stimulus urgency:

```python
def adaptive_reconstruction_ticks(stimulus: dict) -> int:
    """
    Urgent stimuli → fewer ticks (fast but rough reconstruction)
    Reflective stimuli → more ticks (slow but accurate reconstruction)
    """
    urgency_map = {
        'alarm': 3,           # Fast response needed
        'question': 10,        # Normal response
        'creative_task': 30,   # Deep reconstruction
        'reflection': 50       # Very deep reconstruction
    }

    return urgency_map.get(stimulus.get('urgency_type'), 10)
```

### Memory Overhead

**Concern:** Do we need to store context snapshots?

**Answer:** NO - contexts are ephemeral observations, not persistent objects

```python
# WRONG: Storing contexts
contexts_db = {}
context_id = generate_id()
contexts_db[context_id] = capture_context(graph)  # Don't do this

# RIGHT: Contexts exist only during observation
context = capture_context(graph)  # Temporary snapshot
analyze(context)  # Use it
# Then it's garbage collected - no storage
```

**Exception:** Store contexts for analysis/debugging only, not for operational use

---

## Open Questions

1. **Optimal reconstruction ticks?**
   - Current: 10 ticks
   - Confidence: Low (0.4) - needs empirical validation
   - Trade-off: Speed vs accuracy

2. **Context drift acceptable?**
   - Current: Yes, drift is feature not bug
   - Confidence: Medium (0.7)
   - Question: Are there cases where drift is harmful?

3. **Cross-entity context reconstruction?**
   - Can stimulus for entity A reconstruct context from entity B?
   - Example: Technical question (Translator) reactivates social context (Partner)?
   - Confidence: Low (0.3) - unclear if needed

4. **Context similarity threshold?**
   - What similarity score indicates "same context"?
   - Current: No threshold defined
   - Confidence: Low (0.3)

---

## Related Mechanisms

- **[01: Multi-Energy](01_multi_energy_architecture.md)** - Enables per-entity reconstruction
- **[07: Energy Diffusion](07_energy_diffusion.md)** - The traversal mechanism
- **[09: Link Strengthening](09_link_strengthening.md)** - The encoding mechanism
- **[04: Global Workspace](04_global_workspace_theory.md)** - What enters consciousness during reconstruction

---

## Implementation Checklist

- [ ] Implement Context dataclass (snapshot structure)
- [ ] Implement capture_context() function
- [ ] Implement identify_stimulus_targets() with all 3 methods
- [ ] Implement determine_processing_entities() with type mapping
- [ ] Implement reconstruct_context() main algorithm
- [ ] Implement context similarity calculation
- [ ] Write unit tests for context capture
- [ ] Write unit tests for stimulus identification
- [ ] Write integration test for reconstruction accuracy
- [ ] Write phenomenological test for Telegram scenario
- [ ] Measure reconstruction time at scale
- [ ] Document context lifecycle (ephemeral, not stored)
- [ ] Create visualization of context reconstruction process

---

**Next:** [03: Self-Organized Criticality](03_self_organized_criticality.md) - How the system auto-tunes to maintain optimal dynamics
