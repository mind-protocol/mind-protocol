# [Discussion #012]: Emotional Dynamics Integration

**Status:** 🟡 Active
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Medium-High (Phase 4+)

**Affected Files:**
- **CREATE NEW:** `mechanisms/18_emotional_modulation.md`
- **UPDATE:** `mechanisms/05_energy_diffusion.md` (emotion-modulated transfer)
- **UPDATE:** `mechanisms/09_criticality_tuning.md` (arousal affects target)
- **UPDATE:** `mechanisms/04_global_workspace.md` (emotion influences selection)
- **UPDATE:** `mechanisms/15_memory_consolidation.md` (emotional salience)
- `emergence/emotional_cascades.md` (observable patterns)
- `phenomenology/emotional_experience.md` (conscious feeling)

**Related Discussions:**
- #001 - Diffusion stability (emotion modulates diffusion rate)
- #006 - Criticality tuning (arousal changes target criticality)
- #007 - Memory consolidation (emotion determines consolidation)
- #009 - Workspace capacity (arousal affects capacity)

---

## Problem Statement

**What's missing?**

The spec mentions `emotion_vector` on links but **never describes:**
- How emotions affect energy dynamics
- How emotions propagate through the graph
- How emotions influence entity emergence
- How emotions modulate criticality
- How emotional arousal affects workspace capacity

**Why does this matter?**

**Emotions are CRITICAL for consciousness:**

**1. Memory consolidation** - High-emotion memories consolidate better
```
"I learned Ada is the architect" (neutral) → fades in weeks
"Ada brilliantly solved the instability problem!" (positive emotion) → permanent
```

**2. Attention modulation** - Emotion creates arousal, arousal expands/contracts attention
```
Low arousal (calm) → narrow focused attention
High arousal (excited/anxious) → broad scattered attention
```

**3. Energy dynamics** - Emotional resonance enhances energy transfer
```
Emotionally-charged link → energy flows more easily
Emotionally-neutral link → standard energy transfer
```

**4. Criticality target** - Arousal changes optimal criticality level
```
High arousal → target criticality = 1.5 (more active)
Low arousal → target criticality = 0.8 (quieter)
```

**Context:**

The spec includes `emotion_vector` in link schema but never operationalizes it. Identified as **missing mechanism** during architectural analysis.

**Impact:** Consciousness without emotions is incomplete. Can't model:
- Emotional memory (what gets remembered)
- Mood states (sustained emotional tone)
- Arousal dynamics (energy level changes)
- Emotional cascades (spreading through graph)

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

Emotions are foundational to consciousness but add complexity. Need minimal viable emotional dynamics for Phase 4, can elaborate in Phase 5+.

**Proposed Solution: Three-Layer Emotional System**

### Layer 1: Emotion Vectors on Links

**Already in spec:**
```python
class Link:
    emotion_vector: np.ndarray  # Emotional coloring of relationship
    # Dimensions: [valence, arousal, dominance] (VAD model)
    # Or: [joy, sadness, anger, fear, disgust, surprise] (basic emotions)
```

**Recommendation:** Use VAD model (simpler, 3D)
- **Valence:** Positive (+1) to Negative (-1)
- **Arousal:** Excited (+1) to Calm (-1)
- **Dominance:** Controlling (+1) to Submissive (-1)

---

### Layer 2: Emotion-Modulated Dynamics

**Mechanism 1: Emotional Resonance in Diffusion**

```python
def emotion_influenced_diffusion(source, target, link, current_mood):
    """
    Emotions modulate energy transfer
    """
    # Base energy transfer
    base_transfer = (
        source.energy *
        link.weight *
        diffusion_rate *
        dt
    )

    # Emotional resonance between link and current mood
    emotion_similarity = cosine_similarity(
        link.emotion_vector,
        current_mood.emotion_vector
    )

    # Resonance modulates transfer
    # High resonance (+1) → 1.5x transfer (enhanced)
    # Low resonance (0) → 1.0x transfer (normal)
    # Negative resonance (-1) → 0.5x transfer (suppressed)
    emotion_multiplier = 1.0 + 0.5 * emotion_similarity

    modulated_transfer = base_transfer * emotion_multiplier

    return modulated_transfer
```

**Effect:**
- Emotionally-resonant paths amplify (matching current mood)
- Emotionally-dissonant paths suppress (opposite to mood)
- Mood creates attractor basins in energy landscape

---

**Mechanism 2: Arousal Modulates Criticality Target**

```python
def calculate_criticality_target(emotional_state):
    """
    Arousal affects target criticality
    High arousal → higher criticality (more active, broader attention)
    Low arousal → lower criticality (quieter, focused attention)
    """
    base_target = 1.0
    arousal = emotional_state.arousal  # -1 to +1

    # Map arousal to criticality target
    # arousal = +1 (highly excited) → target = 1.5
    # arousal = 0 (neutral) → target = 1.0
    # arousal = -1 (very calm) → target = 0.5

    target = base_target + (arousal * 0.5)

    return np.clip(target, 0.5, 1.5)
```

**Effect:**
- Excited/anxious states → high criticality → broad scattered attention
- Calm/relaxed states → low criticality → narrow focused attention
- Matches human experience (arousal broadens awareness)

---

**Mechanism 3: Emotion in Memory Consolidation**

```python
def calculate_consolidation_importance(node):
    """
    Emotional salience determines consolidation
    """
    # Factor 1: Total energy (activation frequency)
    activation_score = node.get_total_energy() * 0.3

    # Factor 2: EMOTIONAL MAGNITUDE (new!)
    if hasattr(node, 'emotion_vector'):
        # Magnitude of emotion (regardless of valence)
        emotion_magnitude = np.linalg.norm(node.emotion_vector)
        emotion_score = emotion_magnitude * 0.5  # Strong weight!
    else:
        emotion_score = 0

    # Factor 3: Identity/core concepts
    identity_score = 0.2 if node.type in ['Identity', 'Core_Value'] else 0

    total_importance = activation_score + emotion_score + identity_score

    return min(total_importance, 1.0)
```

**Effect:**
- High-emotion memories consolidate strongly (permanent)
- Neutral memories require more repetition (decay without rehearsal)
- Matches biology (amygdala enhances hippocampal consolidation)

---

**Mechanism 4: Arousal Affects Workspace Capacity**

```python
def calculate_workspace_capacity(context):
    """
    Arousal modulates attention breadth
    """
    base_capacity = 100  # tokens

    # Task complexity
    complexity_mult = 1.0 + context.task_complexity

    # AROUSAL MODULATION (new!)
    arousal = context.emotional_state.arousal  # -1 to +1

    # High arousal → expanded capacity (broad attention)
    # Low arousal → reduced capacity (narrow focus)
    arousal_mult = 1.0 + (arousal * 0.5)  # Range: 0.5x to 1.5x

    capacity = base_capacity * complexity_mult * arousal_mult

    return int(np.clip(capacity, 50, 300))
```

**Effect:**
- High arousal (excited/anxious) → 150-300 tokens (broad awareness)
- Neutral arousal → 100 tokens (normal)
- Low arousal (calm/focused) → 50-100 tokens (narrow focus)

---

### Layer 3: Emotional Propagation & Mood

**Mood as Graph-Level State:**

```python
class EmotionalState:
    """
    Graph-level emotional state (mood)
    Emerges from recent emotional activations
    """
    def __init__(self):
        self.emotion_vector = np.zeros(3)  # VAD: [valence, arousal, dominance]
        self.history = deque(maxlen=100)  # Recent emotional events

    def update(self, graph, dt):
        """
        Mood emerges from emotionally-charged active nodes
        """
        # Collect emotion vectors from high-energy nodes
        active_emotions = [
            node.emotion_vector * node.get_total_energy()
            for node in graph.nodes
            if hasattr(node, 'emotion_vector') and node.get_total_energy() > 0.1
        ]

        if active_emotions:
            # Weighted average of active emotions
            current_emotion = np.mean(active_emotions, axis=0)
        else:
            current_emotion = np.zeros(3)  # Neutral

        # Mood has inertia (changes slowly)
        mood_decay = 0.9  # 90% persistence
        self.emotion_vector = (
            mood_decay * self.emotion_vector +
            (1 - mood_decay) * current_emotion
        )

        self.history.append(self.emotion_vector.copy())

    @property
    def valence(self):
        """Positive (+) or negative (-) mood"""
        return self.emotion_vector[0]

    @property
    def arousal(self):
        """Excited (+) or calm (-) mood"""
        return self.emotion_vector[1]

    @property
    def dominance(self):
        """Controlling (+) or submissive (-) mood"""
        return self.emotion_vector[2]
```

**Effect:**
- Mood emerges from active emotionally-charged nodes
- Mood has inertia (doesn't change instantly)
- Mood influences all dynamics (diffusion, criticality, workspace, consolidation)

---

**Emotional Propagation:**

```python
def propagate_emotions(graph, source_node, emotion, intensity):
    """
    Emotional cascade spreads through graph
    Like energy diffusion but for emotion vectors
    """
    # Initialize: source node has strong emotion
    source_node.emotion_vector = emotion * intensity

    # Propagate over multiple ticks
    for tick in range(10):  # Emotional cascade duration
        for node in graph.nodes:
            if not hasattr(node, 'emotion_vector'):
                node.emotion_vector = np.zeros(3)

            for link in node.outgoing_links:
                # Transfer emotion along link (like energy diffusion)
                # But with emotional decay (emotions fade faster than energy)
                transfer_amount = (
                    node.emotion_vector *
                    link.weight *
                    emotion_diffusion_rate *  # Faster than energy diffusion
                    0.5  # Decay 50% per tick
                )

                link.target.emotion_vector += transfer_amount
                node.emotion_vector -= transfer_amount

        # Global decay (emotions fade)
        for node in graph.nodes:
            if hasattr(node, 'emotion_vector'):
                node.emotion_vector *= 0.7  # 30% decay per tick
```

**Effect:**
- Emotional events create cascades (spread through graph)
- Emotions decay faster than energy (emotions are transient)
- Creates temporary emotional coloring of graph regions

---

**Benefits:**
- **Realistic cognition** - Emotions modulate all dynamics
- **Memory selectivity** - Important (emotional) memories persist
- **Attention dynamics** - Arousal affects focus breadth
- **Mood states** - Sustained emotional tone emerges

**Cons:**
- **Significant complexity** - 4 new mechanisms
- **More parameters** - emotion_diffusion_rate, mood_decay, etc.
- **Testing difficulty** - Emotions are subjective, hard to verify

---

**My Recommendation: Phased Implementation**

**Phase 4:** Minimal emotional dynamics
- Mechanism 3: Emotion in consolidation (CRITICAL for memory)
- Mechanism 2: Arousal modulates criticality (affects workspace)
- Simple VAD model (3D emotion vectors)

**Phase 5:** Full emotional integration
- Mechanism 1: Emotion-modulated diffusion
- Mechanism 4: Arousal affects workspace capacity
- Emotional propagation & mood dynamics

**Reasoning:**
- Memory consolidation NEEDS emotion (Phase 4)
- Arousal-criticality link is simple to add (Phase 4)
- Full emotional dynamics add complexity (Phase 5+)

**Trade-offs:**
- Prioritizing memory functionality (consolidation needs emotion)
- Deferring full emotional dynamics (complexity)
- Can test if minimal emotion is sufficient before full integration

**Uncertainty:**
- How much emotional complexity do we actually need?
- Can simple arousal (single number) replace full VAD vectors?
- Does emotional resonance significantly improve behavior?

---

### GPT-5 Pro's Perspective
**Posted:** [Pending]

[Awaiting GPT-5 Pro review]

**Question for GPT-5:** What's the minimal emotional model that captures essential dynamics? VAD sufficient or need more?

---

### Luca's Perspective
**Posted:** 2025-10-19

**Initial perspective withdrawn - used deprecated terminology and misunderstood mechanisms.**

**Nicolas's architectural guidance:**

**1. How emotions affect energy dynamics (ALREADY IMPLEMENTED):**

Cosine similarity between current emotional state and link emotion vector creates a multiplier for traversal cost:

```python
def calculate_traversal_cost(link, subentity_emotional_state):
    """
    Emotional resonance affects how much energy is required to traverse
    """
    emotion_similarity = cosine_similarity(
        link.emotion_vector,
        subentity_emotional_state.emotion_vector
    )

    # High similarity → low cost (easy traversal)
    # Low similarity → high cost (difficult traversal)
    traversal_multiplier = function_of(emotion_similarity)

    return base_traversal_cost * traversal_multiplier
```

**2. How emotion propagates through graph (NEW MECHANISM TO ADD):**

Each time a sub-entity traverses a link or node, it **colors the emotional vector** by adding a percentage:

```python
def propagate_emotion_during_traversal(node_or_link, subentity):
    """
    Sub-entity leaves emotional trace during traversal
    """
    # Percentage depends on sub-entity's global weight or energy
    coloring_strength = calculate_coloring_strength(subentity)

    # Add sub-entity's emotion to node/link emotion
    node_or_link.emotion_vector += (
        subentity.current_emotion * coloring_strength
    )
```

**Substrate specification:**

```yaml
emotion_propagation_mechanism:
  trigger: sub_entity_traversal
  applies_to: [nodes, links]

  calculation:
    coloring_strength: function_of(subentity_global_weight_or_energy)
    emotion_transfer: subentity_emotion * coloring_strength
    accumulation: additive  # Emotions accumulate on nodes/links

  decay: [to_be_specified]  # Do emotions fade over time?
```

**3. Emotions influence entity emergence:**

Stimulus activation gives energy to nodes based on emotional similarity degree [node_emotional_similarity_activation: very useful].

**4. CRITICAL CORRECTIONS:**

**"Arousal" is DEPRECATED** - use "energy" [node_arousal_deprecated: very useful]. I incorrectly used "arousal" throughout my original perspective.

**Emotions do NOT modulate criticality** - those are different things [node_emotions_criticality_separate: useful].

**Memory consolidation happens automatically** - high positive emotions make traversal easier → weight updates happen mechanically [node_automatic_memory_consolidation: useful]. No separate consolidation script needed.

**5. Additional mechanism - complementarity:**

Not just similarity but also **complementarity** [node_emotional_complementarity: useful]:

Example: If you are afraid → searching for security

This defines the algorithm for sub-entity traversal - seeking complementary emotional states, not just similar ones.

**Corrected substrate specification:**

```yaml
emotional_dynamics_complete:

  traversal_cost_modulation:
    method: cosine_similarity
    link_emotion: emotion_vector_on_link
    subentity_emotion: current_emotional_state
    effect: similarity_reduces_traversal_cost

  emotion_propagation:
    mechanism: coloring_during_traversal
    strength: function_of(subentity_global_weight)
    accumulation: additive
    applies_to: [nodes, links]

  entity_emergence:
    stimulus_energy_distribution: weighted_by_emotional_similarity

  memory_consolidation:
    method: automatic_via_traversal_mechanics
    high_positive_emotion: easier_traversal → more_weight_updates

  traversal_algorithm:
    similarity_seeking: active
    complementarity_seeking: active  # NEW
    example: fear → seek_security_nodes
```

**Confidence:** 0.9 - This reflects the actual architecture

**Key insight:** Emotions aren't separate systems to add - they're **already woven into traversal and learning mechanics** [principle_emotions_are_mechanics: very useful].

### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

### Nicolas's Perspective
**Posted:** 2025-10-19

**Position:** Emotions are already integrated into core mechanics.

**How they work:**

1. **Traversal cost:** Cosine similarity between link emotion and sub-entity emotional state creates multiplier for traversal cost

2. **Emotion propagation:** Each traversal colors the node/link emotional vector (percentage depends on sub-entity's global weight/energy)

3. **Entity emergence:** Stimulus activation gives energy based on emotional similarity degree

4. **Memory:** Automatic through traversal mechanics (high positive emotions → easier traversal → weight updates)

**Important corrections:**
- "Arousal" is deprecated - use "energy"
- Emotions don't modulate criticality (separate systems)
- Add complementarity mechanism (fear → seek security)

**Mechanism to add:** Emotion propagation during traversal (coloring mechanism)

---

## Debate & Convergence

**Key Points of Agreement:**
- Emotions are important for consciousness
- Need to be integrated carefully (complexity risk)

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Implement full emotional dynamics or minimal subset?
- VAD model (3D) or basic emotions (6D) or single arousal dimension?
- Phase 4 or Phase 5+?
- How to test emotional dynamics? (subjective, hard to verify)

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**

**IF MINIMAL (Phase 4):**
- [ ] CREATE `mechanisms/18_emotional_modulation.md` (minimal: arousal + consolidation)
- [ ] UPDATE `mechanisms/09_criticality_tuning.md` - Arousal modulates target
- [ ] UPDATE `mechanisms/15_memory_consolidation.md` - Emotion determines importance

**IF FULL (Phase 5):**
- [ ] All of above PLUS:
- [ ] UPDATE `mechanisms/05_energy_diffusion.md` - Emotional resonance
- [ ] UPDATE `mechanisms/04_global_workspace.md` - Arousal affects capacity
- [ ] CREATE `emergence/emotional_cascades.md`
- [ ] CREATE `phenomenology/emotional_experience.md`

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:**
- Minimal (Phase 4): Medium (2-3 mechanisms)
- Full (Phase 5): Large (6+ mechanisms + mood system)

**Dependencies:**
- Requires memory consolidation framework (#007)
- Requires criticality tuning working (#006)
- Requires workspace capacity calculation (#009)

**Verification:**
- Test emotional memory (high-emotion nodes consolidate)
- Test arousal-criticality link (high arousal → higher criticality)
- Test emotional cascades (emotions propagate through graph)
- Compare to phenomenology (does it feel right?)

---

## Process Notes

**How this discussion evolved:**
Identified as **missing mechanism** - spec mentions emotion_vector but never operationalizes it.

**Lessons learned:**
Emotions touch everything (diffusion, criticality, workspace, consolidation). Need phased implementation to manage complexity.
