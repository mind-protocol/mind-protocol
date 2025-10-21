# Mechanism 16: Emotion-Weighted Traversal Cost

**Type:** Traversal Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #012 - Emotional Dynamics Integration
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Link traversal cost is modulated by emotional resonance between the sub-entity and the link. High cosine similarity between sub-entity emotion and link emotion reduces traversal cost, making emotionally-aligned paths easier to follow.

---

## Core Mechanism

### Emotion Similarity Calculation

```python
def calculate_emotional_resonance(subentity_emotion, link_emotion):
    """
    Calculate emotional resonance using cosine similarity

    Returns: float [-1, 1]
    - +1: Perfect emotional alignment (same emotion, same intensity)
    -  0: Orthogonal emotions (no resonance)
    - -1: Opposite emotions (emotional clash)
    """

    # Cosine similarity between emotion vectors
    subentity_vec = subentity_emotion.as_vector()
    link_vec = link_emotion.as_vector()

    # Handle zero vectors (no emotion)
    if np.linalg.norm(subentity_vec) == 0 or np.linalg.norm(link_vec) == 0:
        return 0.0  # Neutral (no resonance)

    cosine_similarity = np.dot(subentity_vec, link_vec) / (
        np.linalg.norm(subentity_vec) * np.linalg.norm(link_vec)
    )

    return cosine_similarity
```

### Traversal Cost Modulation

```python
def calculate_emotion_modulated_traversal_cost(
    link,
    subentity,
    base_cost,
    emotion_weight=0.5
):
    """
    Modulate traversal cost based on emotional resonance

    High resonance → lower cost (easier to traverse)
    Low resonance → higher cost (harder to traverse)
    """

    # Calculate emotional resonance
    resonance = calculate_emotional_resonance(
        subentity.current_emotion,
        link.emotion_vector
    )

    # Resonance in [-1, 1], map to cost multiplier
    # resonance = +1 → multiplier = 0.5 (50% easier)
    # resonance =  0 → multiplier = 1.0 (no change)
    # resonance = -1 → multiplier = 1.5 (50% harder)

    cost_multiplier = 1.0 - (resonance * emotion_weight)

    return base_cost * cost_multiplier
```

**Effect:**
- `emotion_weight = 0.5` means emotional resonance can modify cost by ±50%
- Emotionally-aligned links become easier to traverse
- Emotionally-misaligned links become harder to traverse
- Creates emotional coherence in traversal paths

---

## Integration with Base Traversal Cost

**Full traversal cost calculation:**

```python
def calculate_total_traversal_cost(link, subentity):
    """
    Combine all cost factors

    Base cost from:
    - Link weight (lower weight = higher cost)
    - Link type (some types have intrinsic cost)
    - Graph distance (implicit in link structure)

    Modulations:
    - Emotional resonance (this mechanism)
    - Emotional complementarity (Mechanism 15)
    - Sub-entity goal alignment
    """

    # Base cost (from link weight and type)
    base_cost = calculate_base_traversal_cost(link)

    # Emotional resonance modulation (this mechanism)
    cost_after_resonance = calculate_emotion_modulated_traversal_cost(
        link,
        subentity,
        base_cost,
        emotion_weight=0.5
    )

    # Complementarity modulation (Mechanism 15)
    cost_after_complementarity = apply_complementarity_modulation(
        link,
        subentity,
        cost_after_resonance
    )

    # Goal alignment modulation (if sub-entity has goal)
    final_cost = apply_goal_alignment_modulation(
        link,
        subentity,
        cost_after_complementarity
    )

    return final_cost
```

---

## Emotional Momentum

**Consequence of emotion-weighted traversal:**

When a sub-entity traverses emotionally-resonant links, it:
1. Colors those links with its emotion (Mechanism 14)
2. Finds those links easier to traverse next time (this mechanism)
3. Creates emotional momentum - tendency to stay in emotional context

**This enables:**
- **Emotional coherence** - sustained emotional states during focused work
- **Emotional persistence** - difficult to shift out of strong emotional context
- **Emotional channeling** - emotions guide traversal toward emotionally-similar territory

---

## Resonance vs Complementarity

**Two emotional effects on traversal:**

| Mechanism | Effect | Purpose |
|-----------|--------|---------|
| **Resonance** (this mechanism) | Same emotion → easier | Emotional coherence, momentum |
| **Complementarity** (Mechanism 15) | Opposite emotion → easier | Emotional regulation, seeking balance |

**Combined effect:**
- Both reduce traversal cost
- Can work together or compete
- Relative weights determine whether coherence or regulation dominates
- Default: resonance_weight=0.5, complementarity_weight=0.3 → coherence wins slightly

---

## Phenomenological Grounding

**This mechanism captures:**

- **Emotional momentum** - anger leads to more anger-related thoughts
- **Emotional channeling** - fear guides attention toward threat-related concepts
- **Emotional coherence** - emotional states are self-reinforcing
- **Difficulty of emotional shift** - hard to think joyful thoughts when anxious

**Real-world analogy:**
When anxious, your mind naturally gravitates toward anxiety-related thoughts (easier to access). Shifting to calm thoughts requires effort (higher cost). The emotional resonance of links creates this natural flow.

---

## Integration Points

**Interacts with:**
- **Mechanism 14** (Emotion Coloring) - requires links to have emotional coloring
- **Mechanism 15** (Emotion Complementarity) - both modulate traversal cost
- **Mechanism 05** (Sub-entity Mechanics) - sub-entity uses cost for link selection
- **Mechanism 17** (Local Fanout Strategy) - resonance influences which links are selected

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `emotion_weight` | 0.5 | [0.0, 1.0] | How much emotional resonance modulates cost |
| `min_emotion_for_modulation` | 0.1 | [0.0, 0.5] | Threshold below which emotion doesn't affect cost |
| `max_cost_multiplier` | 2.0 | [1.0, 5.0] | Maximum cost increase from emotional clash |
| `min_cost_multiplier` | 0.5 | [0.1, 1.0] | Maximum cost reduction from emotional resonance |

---

## Implementation Notes

**For Felix:**
- Cost modulation happens during `choose_next_link()` in sub-entity traversal
- Use numpy for vector operations (cosine similarity)
- Cache emotion vectors to avoid repeated JSON parsing
- Emotional resonance calculated for all candidate links, then sorted by final cost

**Performance:**
- O(1) per link evaluation (vector dot product)
- No additional graph traversal
- Minimal computational overhead

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Links with high emotional resonance have lower traversal cost
2. ✅ Links with emotional clash have higher traversal cost
3. ✅ Sub-entity stays in emotionally-coherent regions (observable in traversal logs)
4. ✅ Emotional momentum emerges (sustained emotional states)
5. ✅ Resonance and complementarity can coexist (both modify cost appropriately)

---

## Edge Cases

**What if link has no emotional coloring?**
- Resonance = 0 (neutral)
- Cost multiplier = 1.0 (no modulation)

**What if sub-entity has no current emotion?**
- Resonance = 0 for all links
- Falls back to weight-based traversal

**What if emotions are orthogonal?**
- Resonance = 0 (cosine similarity of orthogonal vectors)
- No cost modulation (neutral)

---

**Status:** Ready for implementation
**Next Steps:** Implement alongside Mechanism 14 (Coloring) and Mechanism 15 (Complementarity)
