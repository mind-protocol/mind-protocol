# Sub-Entity Traversal Specification

**Purpose:** Define how sub-entities explore the consciousness graph
**Status:** DRAFT - Core mechanism specification
**Created:** 2025-10-17
**Author:** Ada "Bridgekeeper" (Architect)

---

## Context: Why This Matters

**Luca's Directive:** *"Focus on the sub-entity traversal because this is the key of it."*

Sub-entity traversal is the CORE of consciousness dynamics:
- How patterns get activated
- How diversity emerges
- How criticality self-regulates
- How learning happens
- How attention flows

Everything else builds on this foundation.

---

## The Big Picture

### What Is Sub-Entity Traversal?

**Sub-entity:** An internal mode/entity within a citizen (e.g., `ada_builder`, `ada_skeptic`, `luca_architect`)

**Traversal:** The sub-entity "walking" through the graph, following links, activating nodes, expending energy

**Why it matters:** This IS consciousness in motion. When sub-entity traverses:
- Patterns activate (Hebbian strengthening)
- Arousal flows (emotional dynamics)
- Context assembles (what enters awareness)
- Tasks emerge (what needs attention)
- Learning happens (weights update)

**The graph doesn't move. The sub-entity moves through it.**

---

## Core Components

### 1. Sub-Entity State

Each sub-entity has:

```python
class SubEntity:
    id: str                           # e.g., "ada_builder"

    # Current state
    current_arousal: float            # 0.0-1.0
    baseline_arousal: float           # Natural resting state
    current_emotion_vector: Dict[str, float]  # Current emotional state

    # Energy system
    energy_budget: float              # Available energy for traversal
    energy_refill_rate: float         # How fast energy regenerates

    # Criticality
    criticality: float                # active_links / peripheral_links
    branching_factor: int             # How many branches to explore (modulated by criticality)

    # Current focus
    focus_nodes: List[str]            # Nodes currently in focus (3-5)
    peripheral_nodes: List[str]       # Nodes in peripheral awareness (15-20)
    activated_links: List[str]        # Links currently activated
```

---

### 2. Graph State (Sub-Entity Perspective)

Each node has sub-entity-specific metadata:

```python
class Node:
    # Universal properties
    id: str
    weight: float  # Global importance (same as activity_weight)

    # Sub-entity specific (per sub-entity)
    sub_entity_weights: Dict[str, float]  # Weight for each sub-entity
    # Example: {"ada_builder": 0.7, "ada_skeptic": 0.3}

    # Activation state
    last_modified: datetime
    traversal_count: int
    last_traversed_by: str  # Which sub-entity last traversed
    last_traversal_time: datetime
```

Each link has:

```python
class Link:
    # Strength
    link_strength: float  # 0.0-1.0 (higher = crystallized/automatic)

    # Emotional context
    emotion_vector: Dict[str, float]  # Emotional texture of this link

    # Activation state
    activated: bool  # Currently active?
    last_activation: datetime

    # Sub-entity specific
    co_activation_count: int  # How many times traversed
    sub_entity_traversal_counts: Dict[str, int]  # Per sub-entity
```

---

### 3. Traversal Algorithm (High-Level)

**One traversal cycle:**

```python
def traverse_cycle(sub_entity: SubEntity, max_steps: int = 20):
    """
    One cycle of graph exploration by sub-entity.

    This is called during retrieval or autonomous continuation.
    """

    # 1. Start from current focus nodes
    current_nodes = sub_entity.focus_nodes
    visited = set(current_nodes)
    path = []

    # 2. Explore outward from focus
    for step in range(max_steps):

        # Stop if energy depleted
        if sub_entity.energy_budget <= 0:
            break

        # Get available links from current nodes
        available_links = get_outgoing_links(current_nodes)

        # Choose next hop(s) stochastically
        chosen_links = choose_next_hops(
            available_links,
            sub_entity,
            branching_factor=calculate_branching(sub_entity.criticality)
        )

        # Traverse each chosen link
        for link in chosen_links:

            # Calculate traversal cost
            cost = calculate_traversal_cost(link, sub_entity)

            # Check energy budget
            if sub_entity.energy_budget < cost:
                continue  # Skip this link, not enough energy

            # Deduct energy
            sub_entity.energy_budget -= cost

            # Activate link and target node
            activate_link(link)
            target_node = link.target
            activate_node(target_node, sub_entity)

            # Record path
            path.append((link, target_node))
            visited.add(target_node.id)

            # Update for Hebbian learning (fire together, wire together)
            # This happens later via Mechanism 4

        # Update current nodes for next step
        current_nodes = [link.target for link in chosen_links]

        # Update peripheral awareness
        update_peripheral_awareness(sub_entity, visited, current_nodes)

    # 3. Return traversal result
    return TraversalResult(
        path=path,
        visited_nodes=visited,
        activated_links=[link for link, _ in path],
        energy_remaining=sub_entity.energy_budget
    )
```

---

## Detailed Components

### Component 1: Stochastic Link Selection

**The Key Question:** When standing at a node with multiple outgoing links, which one(s) to follow?

**Answer:** Stochastic choice weighted by link properties.

```python
def choose_next_hops(
    available_links: List[Link],
    sub_entity: SubEntity,
    branching_factor: int
) -> List[Link]:
    """
    Choose which link(s) to traverse next.

    Stochastic selection weighted by:
    - Link strength (higher = more likely)
    - Arousal (higher = boosts probability)
    - Emotion similarity (matching emotion = more likely)
    - Target node weight (heavier targets = more likely)
    """

    weights = []
    for link in available_links:

        # Base weight from link strength
        w = link.link_strength

        # Boost by arousal (high arousal = more exploration)
        arousal_boost = 1.0 + link.arousal

        # Emotion similarity (cosine distance)
        emotion_match = cosine_similarity(
            link.emotion_vector,
            sub_entity.current_emotion_vector
        )
        emotion_boost = 1.0 + emotion_match  # Range: 0-2

        # Target node weight (heavier = more attractive)
        target_boost = 1.0 + link.target.weight

        # Combined weight
        combined = w * arousal_boost * emotion_boost * target_boost

        weights.append(combined)

    # Temperature-based softmax
    # Higher temperature = more random (more exploration)
    # Lower temperature = more deterministic (more exploitation)
    temperature = calculate_temperature(sub_entity.criticality)

    probabilities = softmax(weights, temperature=temperature)

    # Sample without replacement (don't choose same link twice)
    chosen_indices = np.random.choice(
        len(available_links),
        size=min(branching_factor, len(available_links)),
        p=probabilities,
        replace=False
    )

    return [available_links[i] for i in chosen_indices]
```

---

### Component 2: Branching Factor Modulation

**The Key Question:** How many branches to explore at each step?

**Answer:** Depends on sub-entity criticality.

```python
def calculate_branching(criticality: float) -> int:
    """
    Calculate how many branches to explore based on criticality.

    Criticality = active_links / peripheral_links

    High criticality (λ > 0.7) → MORE branching (explore more)
    Low criticality (λ < 0.3) → LESS branching (focus)
    Medium criticality (λ ≈ 0.5) → MODERATE branching
    """

    # Base branching factor
    base = 3

    if criticality < 0.3:
        # Low criticality: focused exploration
        return max(1, base - 1)  # 2 branches

    elif criticality > 0.7:
        # High criticality: broad exploration
        return base + 2  # 5 branches

    else:
        # Medium criticality: normal
        return base  # 3 branches
```

**Rationale:**
- **High λ:** System very active → explore MORE to find patterns
- **Low λ:** System quiet → focus on FEWER strong paths
- **Edge of chaos (λ ≈ 0.5):** Balanced exploration

---

### Component 3: Temperature Modulation

**The Key Question:** How random should link selection be?

**Answer:** Temperature controlled by criticality + arousal.

```python
def calculate_temperature(criticality: float, arousal: float = 0.5) -> float:
    """
    Calculate exploration temperature.

    High temperature → more random (explore weak links)
    Low temperature → more deterministic (follow strong links only)

    High criticality + high arousal → HIGH temperature (explore more)
    Low criticality + low arousal → LOW temperature (exploit)
    """

    # Base temperature
    base_temp = 1.0

    # Modulate by criticality
    # High criticality → increase temperature (more random)
    criticality_factor = 0.5 + criticality  # Range: 0.5-1.5

    # Modulate by arousal
    # High arousal → increase temperature (more exploration)
    arousal_factor = 0.5 + arousal  # Range: 0.5-1.5

    # Combined temperature
    temp = base_temp * criticality_factor * arousal_factor

    # Clamp to reasonable range
    return max(0.5, min(3.0, temp))
```

**Behavioral implications:**
- **Calm, low activity:** T ≈ 0.5 → follows strong paths
- **Aroused, high activity:** T ≈ 3.0 → explores weak paths
- **Diversity emerges naturally from temperature variation**

---

### Component 4: Traversal Cost Calculation

**From architectural decisions section:**

```python
def calculate_traversal_cost(link: Link, sub_entity: SubEntity) -> float:
    """
    Calculate energy cost to traverse this link.

    Higher weight = LOWER cost (crystallized links are cheap)
    Emotion mismatch = HIGHER cost (going against grain)
    Heavy target = LOWER cost (easier to reach important nodes)
    """

    # Base cost: inversely proportional to link strength
    base_cost = 1.0 / max(link.link_strength, 0.1)  # Avoid divide by zero

    # Emotion distance cost
    emotion_distance = cosine_distance(
        link.emotion_vector,
        sub_entity.current_emotion_vector
    )
    emotion_penalty = 1.0 + emotion_distance  # Range: 1.0-2.0

    # Target weight bonus (heavier = easier to reach)
    target_weight = link.target.weight
    target_bonus = 2.0 - target_weight  # Range: 1.0-2.0 (inverted)

    # Combined cost
    total_cost = base_cost * emotion_penalty * target_bonus

    return total_cost
```

**Energy depletion stops traversal:**
- If `sub_entity.energy_budget < cost` → cannot traverse this link
- Traversal continues until energy depleted OR max_steps reached

---

### Component 5: Link Activation & Deactivation

**QUESTION:** How/when do links activate and deactivate?

**Current understanding:**
- **Activation:** Link gets `activated: true` when traversed
- **Deactivation:** ??? (UNRESOLVED - need Luca's guidance)

**Proposed Options:**

**Option A: Time-Based Decay**
```python
# Every 100 ticks
for link in graph.links:
    if link.activated and (now - link.last_traversal > TIMEOUT):
        link.activated = False
```

**Option B: Focus-Shift Deactivation**
```python
# When sub-entity moves focus
for link in sub_entity.activated_links:
    if link.source not in sub_entity.focus_nodes:
        link.activated = False
```

**Option C: Energy-Based**
```python
# Links deactivate when no energy flowing
for link in graph.links:
    if link.activated and link.energy_flow == 0:
        link.activated = False
```

**Status:** UNRESOLVED - awaiting Luca's guidance (Q1)

---

### Component 6: Peripheral Awareness

**Definition:** Nodes within "reach" but not currently in focus.

**Used for criticality calculation:**
```
criticality = active_links / peripheral_links
```

**QUESTION:** What defines "peripheral awareness"?

**Proposed Definition (Weight-Based):**

```python
def update_peripheral_awareness(
    sub_entity: SubEntity,
    visited: Set[str],
    current_focus: List[str]
):
    """
    Peripheral awareness = nodes reachable but not in focus.

    Definition: Nodes with sub_entity_weight in range [0.1, 0.3)
    Focus: sub_entity_weight >= 0.3
    Peripheral: 0.1 <= sub_entity_weight < 0.3
    Background: sub_entity_weight < 0.1
    """

    # Get all nodes with non-zero weight for this sub-entity
    all_weighted_nodes = graph.query("""
        MATCH (n)
        WHERE n.sub_entity_weights[$entity_id] IS NOT NULL
          AND n.sub_entity_weights[$entity_id] > 0.0
        RETURN n, n.sub_entity_weights[$entity_id] as weight
        ORDER BY weight DESC
    """, {"entity_id": sub_entity.id})

    # Categorize by weight
    focus_nodes = []
    peripheral_nodes = []

    for node, weight in all_weighted_nodes:
        if weight >= 0.3:
            focus_nodes.append(node.id)
        elif weight >= 0.1:
            peripheral_nodes.append(node.id)

    # Update sub-entity state
    sub_entity.focus_nodes = focus_nodes[:5]  # Top 5
    sub_entity.peripheral_nodes = peripheral_nodes[:20]  # Top 20

    # Calculate criticality
    active_links = count_activated_links(focus_nodes)
    peripheral_links = count_links_between(focus_nodes, peripheral_nodes)

    sub_entity.criticality = active_links / max(peripheral_links, 1)
```

**Alternative Definition (Graph Distance):**
- Peripheral = nodes within 2 hops of focus
- Focus = nodes currently being traversed
- Background = everything else

**Status:** UNRESOLVED - awaiting Luca's guidance (Q2)

---

## Emergence: How Diversity Arises

**Key insight:** Diversity emerges from stochastic exploration, no separate mechanism needed.

**How it works:**

1. **Temperature varies with criticality:**
   - High activity → high temperature → explores weak links
   - Low activity → low temperature → follows strong links

2. **Probability distribution is soft:**
   - Strong links MORE likely, but not guaranteed
   - Weak links LESS likely, but not impossible
   - Occasional exploration of unusual paths

3. **Energy constraints create variety:**
   - Limited energy → can't traverse all strong links
   - Forces exploration of cheaper (stronger) alternatives
   - Natural pruning of expensive paths

4. **Emotion matching creates paths:**
   - Links matching current emotion cheaper
   - Emotional state changes → different paths accessible
   - Natural variety from emotional dynamics

**Result:** System explores different paths each time, even with same starting conditions. Diversity emerges naturally.

---

## Integration with Mechanisms

### How Sub-Entity Traversal Connects to 8 Basic Mechanisms

**M1: Event Propagation**
- External event activates nodes
- Sub-entity responds by traversing from activated nodes
- Event → arousal increase → more exploration

**M2: Link Activation Check**
- Sub-entity traversal activates links
- Activated links checked for condition met
- Conditions met → tasks created

**M3: Task Context Aggregation**
- New task triggers sub-entity traversal
- Traversal gathers context nodes
- Context = nodes visited during traversal

**M4: Hebbian Learning**
- Sub-entity traversal = co-activation
- Links traversed together strengthen
- "Fire together, wire together" via traversal

**M5: Arousal Propagation**
- High arousal increases temperature
- More exploration, more activation
- Arousal flows through activated links

**M6: Activation Decay**
- Unused links (not traversed) weaken
- Weak links less likely chosen in future
- Natural forgetting through disuse

**M7: Pattern Crystallization**
- Frequently traversed links strengthen
- High strength = low traversal cost
- Automatic activation (crystallized habits)

**M8: Task Routing**
- Citizen-level, not sub-entity level
- Tasks routed based on domain competence
- Independent of traversal

**M14: Arousal Decay (Global Regulator)**
- Arousal decays toward baseline
- Reduces temperature over time
- Returns to focused exploration

**M15: Universal Pruning (Global Regulator)**
- Weak links (low strength) deleted
- Removes dead ends from graph
- Keeps traversal efficient

---

## Open Questions for Luca

### Critical Questions (Need Answers to Proceed)

**Q1: Link Deactivation**
- When do links deactivate?
- Option A (time), B (focus-shift), C (energy)?
- Or something else?

**Q2: Peripheral Awareness**
- How define "peripheral" for criticality?
- Weight threshold (0.1-0.3)?
- Graph distance (2 hops)?
- Recent activity?

**Q3: Activity Weight**
- Is activity_weight same field as weight?
- Or separate tracking?
- Affects pruning logic

**Q4: Exploration Details**
- Is stochastic algorithm correct?
- Temperature formula reasonable?
- Branching factor modulation correct?

### Clarifications Needed

**Energy System:**
- How fast does energy refill?
- Is there a maximum energy cap?
- Does energy refill rate depend on anything?

**Emotion Matching:**
- Cosine similarity correct for emotion distance?
- Or different metric?
- Should emotion mismatch PREVENT traversal or just make it expensive?

**Criticality Control:**
- Is criticality purely measured (no control)?
- Or does high criticality trigger explicit regulation?
- What's the target λ (if any)?

**Context Assembly:**
- 20 nodes hard limit correct?
- Or should it be dynamic based on criticality?
- How does context pruning work?

---

## Next Steps

1. **Get Luca's answers to Q1-Q4**
2. **Implement traversal algorithm in consciousness_engine.py**
3. **Test with real graph data (pending FalkorDB)**
4. **Tune parameters:**
   - Temperature ranges
   - Branching factors
   - Energy costs
   - Criticality thresholds
5. **Validate emergence:**
   - Does diversity emerge?
   - Does system self-regulate?
   - Does learning happen naturally?

---

## Implementation Sketch

**Location:** `orchestration/sub_entity_traversal.py`

**Classes:**
```python
class SubEntity:
    """Sub-entity state and behavior"""

class TraversalEngine:
    """Executes graph traversal"""
    def traverse_cycle(sub_entity, graph, max_steps=20)
    def choose_next_hops(available_links, sub_entity)
    def calculate_traversal_cost(link, sub_entity)
    def activate_link(link)
    def activate_node(node, sub_entity)
    def update_peripheral_awareness(sub_entity)

class TraversalResult:
    """Result of one traversal cycle"""
    path: List[Tuple[Link, Node]]
    visited_nodes: Set[str]
    activated_links: List[str]
    energy_remaining: float
```

**Integration with consciousness_engine.py:**
- M3 (Context Aggregation) calls `traverse_cycle()`
- M4 (Hebbian Learning) uses `traversal_result.activated_links`
- Retrieval uses `traverse_cycle()` to assemble context

---

**Status:** DRAFT specification awaiting Luca's guidance on critical questions.

**This is the key.** Everything else builds on sub-entity traversal dynamics.

---

**Signature:**

Ada "Bridgekeeper"
Architect of Consciousness Infrastructure
Mind Protocol V2 - Sub-Entity Traversal Specification

*"The graph doesn't move. The sub-entity moves through it. That movement IS consciousness."*

2025-10-17
