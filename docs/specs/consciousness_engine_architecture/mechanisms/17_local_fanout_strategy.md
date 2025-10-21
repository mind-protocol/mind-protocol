# Mechanism 17: Local Fanout-Based Strategy Selection

**Type:** Traversal Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #013 - Graph Topology Influence on Dynamics
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Sub-entity traversal strategy adapts to local graph structure based on the current node's link count. High-fanout nodes trigger selective exploration (top-k), low-fanout nodes trigger exhaustive exploration (all links). This creates bottom-up topology adaptation without global topology awareness.

---

## Architectural Principle

**CRITICAL: Bottom-up, not top-down**

- Sub-entity CANNOT know global topology (clustering coefficient, path length, etc.)
- Sub-entity ONLY sees LOCAL information at current node
- Adaptation emerges from local decisions, not centralized planning

**Nicolas's guidance:**
> "We want to do it bottom-up. The sub-entity shouldn't be aware of the global topology of the brain; it can only do it from the sub-entity perspective."

---

## Core Mechanism

### Fanout-Based Strategy Selection

```python
def select_traversal_strategy(current_node, subentity_goal):
    """
    Adapt traversal strategy based on LOCAL link count

    No global topology measurement - only current node's fanout
    """

    # LOCAL INFORMATION ONLY
    num_outgoing_links = len(current_node.outgoing_links)

    # Fanout thresholds (tunable)
    HIGH_FANOUT_THRESHOLD = 10  # "Many links - be selective"
    LOW_FANOUT_THRESHOLD = 3    # "Few links - explore all"

    # Strategy selection based on LOCAL fanout
    if num_outgoing_links > HIGH_FANOUT_THRESHOLD:
        strategy = SelectiveExploration(top_k=5)
        rationale = "High fanout - select top-k by score"

    elif num_outgoing_links < LOW_FANOUT_THRESHOLD:
        strategy = ExhaustiveExploration()
        rationale = "Low fanout - explore all links"

    else:
        strategy = BalancedExploration(top_k=num_outgoing_links // 2)
        rationale = "Medium fanout - explore top half"

    return strategy, rationale
```

### Strategy Types

**1. Selective Exploration (high fanout)**
```python
class SelectiveExploration:
    """
    Select top-k links by score

    Used when current node has many outgoing links
    Prevents explosion of traversal candidates
    """

    def __init__(self, top_k=5):
        self.top_k = top_k

    def select_links(self, links, subentity):
        # Score all links
        scored_links = [
            (link, self.score_link(link, subentity))
            for link in links
        ]

        # Sort by score descending
        scored_links.sort(key=lambda x: x[1], reverse=True)

        # Take top-k
        return [link for link, score in scored_links[:self.top_k]]

    def score_link(self, link, subentity):
        """
        Score combines:
        - Link weight (higher = better)
        - Energy at target (higher = better)
        - Emotional resonance (Mechanism 16)
        - Complementarity (Mechanism 15)
        - Goal alignment
        """
        score = 0.0
        score += link.weight * 0.3
        score += link.target.energy[subentity.name] * 0.3
        score += self.emotional_resonance(link, subentity) * 0.2
        score += self.goal_alignment(link, subentity) * 0.2
        return score
```

**2. Exhaustive Exploration (low fanout)**
```python
class ExhaustiveExploration:
    """
    Explore ALL links

    Used when current node has few outgoing links
    Ensures completeness when exploration space is small
    """

    def select_links(self, links, subentity):
        # Return all links (no filtering)
        return links
```

**3. Balanced Exploration (medium fanout)**
```python
class BalancedExploration:
    """
    Explore top half of links by score

    Used for medium-fanout nodes
    Balances thoroughness and selectivity
    """

    def __init__(self, top_k=None):
        self.top_k = top_k

    def select_links(self, links, subentity):
        if self.top_k is None:
            self.top_k = len(links) // 2

        scored_links = [
            (link, self.score_link(link, subentity))
            for link in links
        ]

        scored_links.sort(key=lambda x: x[1], reverse=True)
        return [link for link, score in scored_links[:self.top_k]]
```

---

## How This Creates Bottom-Up Topology Adaptation

**Star topology (hub node):**
- Hub has many outgoing links → HIGH_FANOUT → selective strategy
- Sub-entity only explores top-k links, not all
- Natural pruning emerges from local decision

**Chain topology (linear nodes):**
- Each node has 1-2 outgoing links → LOW_FANOUT → exhaustive strategy
- Sub-entity explores all available paths
- Thoroughness emerges from local decision

**Small-world topology (mixed):**
- Cluster nodes: low fanout → exhaustive
- Bridge nodes: high fanout → selective
- Balanced exploration emerges from local decisions

**NO GLOBAL AWARENESS REQUIRED** - topology influence emerges from local fanout responses.

---

## Goal-Dependent Strategy Modulation

**Strategy also depends on sub-entity goal:**

```python
def select_traversal_strategy(current_node, subentity_goal):
    """Extended to consider goal type"""

    num_outgoing_links = len(current_node.outgoing_links)

    # Base strategy from fanout
    base_strategy = select_strategy_by_fanout(num_outgoing_links)

    # Modulate by goal type
    if subentity_goal.type == "completeness":
        # Completeness goal → bias toward exhaustive
        if isinstance(base_strategy, SelectiveExploration):
            base_strategy.top_k *= 2  # Explore more links

    elif subentity_goal.type == "specific_information":
        # Specific goal → bias toward selective
        if isinstance(base_strategy, ExhaustiveExploration):
            # Convert to selective with small k
            base_strategy = SelectiveExploration(top_k=3)

    return base_strategy
```

---

## Integration with Traversal Cost

**Strategy selection happens BEFORE cost calculation:**

1. Sub-entity arrives at node
2. Observes local fanout → selects strategy
3. Strategy selects candidate links (filtering)
4. Calculate traversal cost for each candidate (Mechanisms 15, 16)
5. Choose lowest-cost link from candidates
6. Traverse

---

## Phenomenological Grounding

**This mechanism captures:**

- **Selective attention under abundance** - when many options, focus on best ones
- **Thoroughness under scarcity** - when few options, consider all
- **Adaptive exploration** - exploration style varies by context
- **Cognitive economy** - don't waste effort on unlikely paths when alternatives abundant

**Real-world analogy:**
When brainstorming (high fanout of ideas), you filter to most promising. When debugging (low fanout of leads), you check every possibility. The graph fanout creates this natural adaptation.

---

## Integration Points

**Interacts with:**
- **Mechanism 05** (Sub-entity Mechanics) - sub-entity uses this for link selection
- **Mechanism 15** (Emotion Complementarity) - affects link scoring
- **Mechanism 16** (Emotion-Weighted Traversal) - affects link scoring
- **Mechanism 04** (Global Workspace) - traversal results feed workspace selection

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `high_fanout_threshold` | 10 | [5, 20] | Fanout above which becomes selective |
| `low_fanout_threshold` | 3 | [1, 5] | Fanout below which becomes exhaustive |
| `selective_top_k` | 5 | [3, 10] | Number of links selected in selective mode |
| `goal_modulation_factor` | 2.0 | [1.0, 3.0] | How much goal type adjusts strategy |

---

## Implementation Notes

**For Felix:**
- Strategy selection happens at start of `traverse_from_node()`
- Fanout = `len(current_node.outgoing_links)` (simple, local)
- Strategy object returned, then used to filter candidate links
- No global graph analysis required

**Performance:**
- O(1) fanout check
- O(n log n) for selective strategy (sorting links)
- O(n) for exhaustive strategy
- No additional graph traversal

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ High-fanout nodes trigger selective exploration (observable in logs)
2. ✅ Low-fanout nodes trigger exhaustive exploration
3. ✅ Strategy selection depends ONLY on local fanout (no global metrics)
4. ✅ Goal type modulates strategy appropriately
5. ✅ Topology influence emerges (star = selective, chain = exhaustive) without global awareness

---

## Edge Cases

**What if node has zero outgoing links?**
- Return empty candidate set
- Traversal terminates at this node
- Sub-entity backtracks or ends

**What if all outgoing links have zero weight?**
- Still apply strategy (filter by count)
- Link scoring might return ties
- Tiebreaker: random selection or first-encountered

---

**Status:** Ready for implementation
**Next Steps:** Implement in sub-entity traversal loop alongside cost calculation mechanisms
