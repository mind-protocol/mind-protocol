# Mechanism 14: Emotion Coloring During Traversal

**Type:** Consciousness Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #012 - Emotional Dynamics Integration
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Sub-entities color nodes and links with their current emotional state as they traverse the graph. This creates emotional traces that persist after traversal, enabling emotional memory and context reconstruction.

---

## Core Mechanism

### Coloring Process

When a sub-entity traverses a node or link, it adds its current emotional state to that element's emotion vector:

```python
def propagate_emotion_during_traversal(node_or_link, subentity):
    """
    Color graph elements with sub-entity's current emotion

    Emotional coloring is ADDITIVE and PERSISTENT:
    - Each traversal adds to existing emotion_vector
    - Emotions accumulate over multiple traversals
    - Decay removes old emotional traces gradually
    """

    # Calculate coloring strength based on sub-entity state
    coloring_strength = calculate_coloring_strength(subentity)

    # Add sub-entity's emotion to element's emotion vector
    node_or_link.emotion_vector += (subentity.current_emotion * coloring_strength)

    # Normalize to prevent unbounded growth
    node_or_link.emotion_vector = normalize_emotion_vector(
        node_or_link.emotion_vector,
        max_magnitude=1.0
    )
```

### Coloring Strength Factors

**Coloring strength depends on:**
- **Traversal duration** - longer time on node → stronger coloring
- **Sub-entity energy** - higher energy → stronger coloring
- **Attention level** - focused attention → stronger coloring
- **Emotional intensity** - stronger emotions color more

```python
def calculate_coloring_strength(subentity):
    """
    Determine how strongly sub-entity colors the graph

    Returns: float [0.0, 1.0]
    """
    base_strength = 0.1  # Base coloring rate

    strength = base_strength
    strength *= subentity.energy  # Energy modulation
    strength *= subentity.attention_level  # Attention modulation
    strength *= norm(subentity.current_emotion)  # Emotional intensity

    return np.clip(strength, 0.0, 1.0)
```

---

## Emotion Vector Representation

**Format:** Normalized vector in emotion space

```python
class EmotionVector:
    """
    Multi-dimensional emotion representation

    Each dimension represents a core emotion:
    - Fear/Security axis
    - Joy/Sadness axis
    - Anger/Peace axis
    - Curiosity/Boredom axis
    - etc.
    """

    def __init__(self):
        self.fear_security = 0.0      # [-1, 1]: -1=fear, +1=security
        self.joy_sadness = 0.0        # [-1, 1]: -1=sadness, +1=joy
        self.anger_peace = 0.0        # [-1, 1]: -1=anger, +1=peace
        self.curiosity_boredom = 0.0  # [-1, 1]: -1=boredom, +1=curiosity

    def as_vector(self):
        """Return as numpy array for mathematical operations"""
        return np.array([
            self.fear_security,
            self.joy_sadness,
            self.anger_peace,
            self.curiosity_boredom
        ])

    def magnitude(self):
        """Emotional intensity (not directional)"""
        return np.linalg.norm(self.as_vector())
```

---

## Persistence and Decay

**Emotional traces persist but decay over time:**

```python
def decay_emotion_vectors(graph, dt, emotion_decay_rate=0.01):
    """
    Emotional coloring fades over time

    Decay is slower than energy decay - emotions "stick" longer
    """
    for node in graph.nodes:
        node.emotion_vector *= (1 - emotion_decay_rate * dt)

    for link in graph.links:
        link.emotion_vector *= (1 - emotion_decay_rate * dt)
```

**Decay rate considerations:**
- Slower than energy decay (emotions linger after activation fades)
- Type-dependent (Memory nodes retain emotional color longer)
- Can vary by emotion dimension (fear might persist longer than joy)

---

## Use Cases

### 1. Emotional Memory
Nodes visited during emotional states retain that emotional signature. When later activated, they bring back associated emotions.

### 2. Emotional Context Reconstruction
Sub-entities can detect emotional patterns in recently-traversed regions, reconstructing the emotional context of previous work.

### 3. Emotion-Based Clustering
Nodes with similar emotional coloring cluster together, creating emotionally-coherent regions of the graph.

### 4. Emotional Priming
Traversing emotionally-colored nodes primes sub-entity's emotional state, creating emotional momentum.

---

## Integration Points

**Interacts with:**
- **Mechanism 16** (Emotion-Weighted Traversal) - emotional coloring affects future traversal costs
- **Mechanism 15** (Emotion Complementarity) - seeking opposite-emotion nodes
- **Mechanism 19** (Type-Dependent Decay) - emotion decay varies by node type
- **Mechanism 05** (Sub-entity Mechanics) - coloring happens during traversal

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `base_coloring_strength` | 0.1 | [0.0, 1.0] | Base rate of emotional coloring |
| `emotion_decay_rate` | 0.01/hour | [0.0, 0.1] | How fast emotional coloring fades |
| `max_emotion_magnitude` | 1.0 | [0.5, 2.0] | Maximum emotional intensity |
| `energy_modulation` | 1.0 | [0.5, 2.0] | How much energy affects coloring |
| `attention_modulation` | 1.0 | [0.5, 2.0] | How much attention affects coloring |

---

## Phenomenological Grounding

**This mechanism captures:**
- **Emotional memory** - places/concepts retain emotional associations
- **Emotional residue** - feelings linger after events that caused them
- **Context-dependent emotion** - returning to a context brings back its emotional tone
- **Emotional momentum** - emotions build as you traverse emotionally-charged territory

**Real-world analogy:**
Like how a room where you had an argument retains an uncomfortable feeling even days later, or how revisiting a place where you were happy brings back traces of that joy.

---

## Implementation Notes

**For Felix:**
- Emotion vectors stored as JSON in node/link metadata
- Coloring happens during `traverse_link()` and `process_node()` calls
- Decay applied during tick update loop
- Use numpy for vector operations (efficient)

**Performance:**
- Minimal overhead (single vector addition per traversal)
- Decay is O(nodes + links) per tick (already doing energy decay)

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Nodes traversed during high-emotion states have higher emotion magnitude
2. ✅ Emotional coloring fades over time without re-traversal
3. ✅ Different sub-entities can color same nodes with different emotions (additive)
4. ✅ Emotion vectors remain normalized (don't grow unbounded)
5. ✅ Emotional coloring affects future traversal costs (via Mechanism 16)

---

**Status:** Ready for implementation
**Next Steps:** Implement alongside Mechanism 15 (Complementarity) and Mechanism 16 (Weighted Traversal)
