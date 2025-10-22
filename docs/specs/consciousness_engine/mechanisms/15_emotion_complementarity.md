# Mechanism 15: Emotion Complementarity

**Type:** Traversal Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #012 - Emotional Dynamics Integration
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Sub-entities experiencing strong emotions are drawn toward nodes colored with complementary (opposite) emotions. Fear seeks security, sadness seeks joy, anger seeks peace. This creates emotion-driven traversal that naturally moves toward emotional regulation.

---

## Core Mechanism

### Complementarity Matching

When a sub-entity is deciding which link to traverse, it calculates complementarity between its current emotion and each potential target node's emotional coloring:

```python
def calculate_complementarity_attraction(subentity_emotion, node_emotion):
    """
    Calculate attraction based on emotional complementarity

    Complementary emotions ATTRACT:
    - Fear (-1 on fear_security axis) attracts Security (+1 on fear_security axis)
    - Sadness (-1 on joy_sadness axis) attracts Joy (+1 on joy_sadness axis)

    Returns: float [0.0, 1.0] - attraction strength
    """

    # Complementarity = opposite sign on each emotion axis
    complementarity_vector = -subentity_emotion.as_vector() * node_emotion.as_vector()

    # Sum positive complementarity (negative values mean same-sign = not complementary)
    complementarity_score = np.sum(np.maximum(complementarity_vector, 0))

    # Normalize to [0, 1]
    max_possible = len(subentity_emotion.as_vector())  # All axes fully complementary
    normalized_complementarity = complementarity_score / max_possible

    return normalized_complementarity
```

### Complementarity Axes

**Each emotion dimension has a complementary opposite:**

| Sub-entity Emotion | Seeks Nodes Colored With |
|-------------------|-------------------------|
| Fear (< 0 on fear_security) | Security (> 0 on fear_security) |
| Security (> 0 on fear_security) | Mild fear (< 0, for alertness) |
| Sadness (< 0 on joy_sadness) | Joy (> 0 on joy_sadness) |
| Joy (> 0 on joy_sadness) | Contentment (neutral) |
| Anger (< 0 on anger_peace) | Peace (> 0 on anger_peace) |
| Peace (> 0 on anger_peace) | Engagement (< 0, for activation) |
| Boredom (< 0 on curiosity_boredom) | Curiosity (> 0 on curiosity_boredom) |
| Curiosity (> 0 on curiosity_boredom) | Integration (neutral) |

---

## Integration with Traversal Cost

Complementarity modulates link traversal cost:

```python
def calculate_traversal_cost_with_complementarity(
    link,
    subentity,
    base_cost,
    complementarity_weight=0.3
):
    """
    Complementary emotions reduce traversal cost

    High complementarity = easier to traverse (lower cost)
    Low complementarity = harder to traverse (higher cost)
    """

    # Get target node's emotional coloring
    target_emotion = link.target.emotion_vector

    # Calculate complementarity attraction
    complementarity = calculate_complementarity_attraction(
        subentity.current_emotion,
        target_emotion
    )

    # Reduce cost for complementary emotions
    cost_multiplier = 1.0 - (complementarity * complementarity_weight)

    return base_cost * cost_multiplier
```

**Effect:**
- Complementarity weight = 0.3 means up to 30% cost reduction
- Sub-entity experiencing fear finds security-colored nodes easier to reach
- Creates natural emotional regulation through graph traversal

---

## Complementarity vs Similarity

**Two different emotional effects:**

1. **Complementarity (this mechanism):**
   - Opposite emotions attract
   - Fear → seeks Security
   - Purpose: Emotional regulation, seeking balance

2. **Similarity (Mechanism 16):**
   - Similar emotions attract
   - Fear → resonates with fear-colored nodes
   - Purpose: Emotional coherence, context maintenance

**Both operate simultaneously:**
- Similarity creates emotional momentum (stay in emotional context)
- Complementarity creates emotional regulation (move toward balance)
- Trade-off controlled by respective weights

---

## Phenomenological Grounding

**This mechanism captures:**

- **Emotional regulation** - when anxious, we seek calming contexts
- **Complementary needs** - sadness seeks joy, anger seeks peace
- **Emotional intelligence** - recognizing what we need emotionally
- **Therapeutic movement** - moving toward what heals, not just what's familiar

**Real-world analogy:**
When stressed, you're drawn to peaceful environments. When sad, you seek uplifting content. When bored, you seek novelty. The graph structure enables this natural emotional navigation.

---

## Complementarity Strength Modulation

**Complementarity attraction strength varies by:**

1. **Emotional intensity**
   - Strong emotions → strong complementarity seeking
   - Mild emotions → weaker complementarity pull

```python
def modulate_complementarity_by_intensity(subentity_emotion):
    """Stronger emotions seek complementarity more actively"""
    emotional_intensity = subentity_emotion.magnitude()
    return emotional_intensity  # [0, 1] multiplier
```

2. **Sub-entity type**
   - Some sub-entities (e.g., Validator) might resist complementarity seeking
   - Others (e.g., Healing entity) might amplify it

3. **Context**
   - During focused work: suppress complementarity (stay in emotional state)
   - During recovery: amplify complementarity (seek regulation)

---

## Integration Points

**Interacts with:**
- **Mechanism 14** (Emotion Coloring) - requires nodes to have emotional coloring
- **Mechanism 16** (Emotion-Weighted Traversal) - complementarity affects traversal cost
- **Mechanism 05** (Sub-entity Mechanics) - sub-entity decides where to traverse
- **Mechanism 17** (Local Fanout Strategy) - complementarity influences link selection

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `complementarity_weight` | 0.3 | [0.0, 1.0] | How much complementarity reduces traversal cost |
| `intensity_modulation` | 1.0 | [0.5, 2.0] | How much emotional intensity amplifies complementarity seeking |
| `min_emotion_for_complementarity` | 0.1 | [0.0, 0.5] | Threshold below which complementarity doesn't activate |

---

## Implementation Notes

**For Felix:**
- Complementarity calculated during link selection in `choose_next_link()`
- Vector operations (numpy dot products)
- Complementarity modifies `traversal_cost` before comparison
- Works alongside similarity-based attraction (both modify cost)

**Performance:**
- O(1) per link evaluation (vector dot product)
- No additional graph traversal needed

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Sub-entity with high fear preferentially traverses security-colored nodes
2. ✅ Complementarity strength scales with emotional intensity
3. ✅ Complementary emotions reduce traversal cost (measurable in logs)
4. ✅ Emotional regulation emerges (sub-entities naturally move toward balance)
5. ✅ Complementarity and similarity can coexist (not mutually exclusive)

---

## Edge Cases

**What if node has no emotional coloring?**
- Complementarity = 0 (neutral, no cost reduction)
- Sub-entity treats as emotionally-neutral option

**What if sub-entity has no current emotion?**
- Complementarity = 0 for all links
- Traversal falls back to energy/weight-based selection

**What if emotions are orthogonal (fear + joy)?**
- Complementarity calculated per-axis
- Partial complementarity possible (complementary on some axes, not others)

---

**Status:** Ready for implementation
**Next Steps:** Implement alongside Mechanism 14 (Coloring) and Mechanism 16 (Weighted Traversal)
