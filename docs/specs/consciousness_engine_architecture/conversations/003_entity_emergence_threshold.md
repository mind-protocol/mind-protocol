# [Discussion #003]: Entity Emergence Threshold

**Status:** 🔴 Blocking
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Critical

**Affected Files:**
- `mechanisms/07_entity_emergence.md` (primary - add threshold calculation)
- `emergence/entity_formation_patterns.md` (how emergence plays out)
- `phenomenology/entity_activation_experience.md` (observable behavior)

**Related Discussions:**
- #010 - Entity competition model (affects how energy accumulates in clusters)
- #009 - Workspace capacity (how many entities can fit in consciousness)

---

## Problem Statement

**What's the issue?**

The specification states: "Entity emerges when cluster energy > threshold"

**But never defines what that threshold value is.**

Current entity detection pseudocode:
```python
def detect_emergent_entities(graph):
    clusters = cluster_by_dominant_entity(graph)
    for cluster in clusters:
        total_energy = sum(
            node.energy[cluster.entity]
            for node in cluster.nodes
        )
        if total_energy > entity_emergence_threshold:  # ← WHAT VALUE?
            create_entity(cluster)
```

**Why does this matter?**

This threshold determines system behavior:
- **Threshold too high** → 0 entities emerge (silent system)
- **Threshold realistic** → 3-5 entities emerge (intended behavior)
- **Threshold too low** → 50+ entities emerge (fragmentation chaos)

**Missing specification:**
- Is it an absolute value (e.g., 1.0)?
- Relative to total graph energy?
- Relative to other clusters (top-N)?
- Per-entity specific thresholds?
- Dynamic based on graph size?

**Context:**

Discovered as **specification gap** during architectural analysis. The spec describes entity emergence mechanism but leaves the critical threshold parameter undefined.

**Impact:** Cannot implement Phase 3 (Entity Emergence) without this decision.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

The threshold determines which activation clusters cross into "entity" status. Too permissive = fragmentation (many weak entities). Too restrictive = silence (no entities despite activation).

**Key trade-off:** Absolute vs relative thresholds

**Option A: Absolute Threshold**
```python
entity_emergence_threshold = 1.0  # Fixed value

if cluster.total_energy > 1.0:
    entity_emerges()
```

**Pros:**
- Simple, predictable
- Easy to reason about
- Consistent across sessions

**Cons:**
- Doesn't scale with graph size (100-node graph vs 10K-node graph)
- Doesn't adapt to current activation level (quiet vs energized system)
- Requires manual tuning

---

**Option B: Relative Threshold (Recommended)**
```python
def calculate_emergence_threshold(graph):
    """
    Dynamic threshold based on energy distribution
    Auto-scales with graph size and activation level
    """
    # Get all cluster energies
    cluster_energies = [
        sum(node.energy[entity] for node in cluster.nodes)
        for cluster in all_clusters(graph)
    ]

    # Threshold = median + 2 standard deviations
    # This captures top ~5-10% of clusters
    median = statistics.median(cluster_energies)
    std = statistics.stdev(cluster_energies)

    threshold = median + 2 * std

    return threshold
```

**Pros:**
- Auto-scales with graph size (100 nodes or 10K nodes)
- Adapts to activation level (quiet session vs energized discussion)
- Consistently gives ~5-10% of clusters emerging (realistic entity count)
- No manual tuning required

**Cons:**
- Less predictable (threshold changes dynamically)
- Might oscillate if energy distribution shifts rapidly
- Harder to reason about

---

**Option C: Top-N Clusters**
```python
def select_emergent_entities(graph, max_entities=5):
    """
    Only top N highest-energy clusters become entities
    """
    clusters = sorted(
        all_clusters(graph),
        key=lambda c: c.total_energy,
        reverse=True
    )

    return clusters[:max_entities]
```

**Pros:**
- Guarantees exactly N entities (predictable)
- Simple to implement
- Prevents fragmentation (can't exceed N)

**Cons:**
- Arbitrary cap (why 5? why not 7?)
- Forces entities even if energy is low (might get weak entities)
- Doesn't allow for "no entities active" state (dormancy)

---

**Option D: Hybrid - Relative with Floor/Ceiling**
```python
def calculate_emergence_threshold(graph):
    """
    Relative threshold with bounds
    """
    cluster_energies = get_all_cluster_energies(graph)

    # Relative threshold (median + 2σ)
    relative = median(cluster_energies) + 2 * std(cluster_energies)

    # Enforce bounds
    MIN_THRESHOLD = 0.5  # Must have at least this much energy
    MAX_ENTITIES = 10    # Cap to prevent fragmentation

    # Apply floor
    threshold = max(relative, MIN_THRESHOLD)

    # If this would create too many entities, raise threshold
    candidates = [c for c in cluster_energies if c > threshold]
    if len(candidates) > MAX_ENTITIES:
        # Raise threshold to get exactly MAX_ENTITIES
        threshold = sorted(cluster_energies, reverse=True)[MAX_ENTITIES]

    return threshold
```

**Pros:**
- Combines adaptability (relative) with safety (bounds)
- Prevents both fragmentation and inappropriate silence
- Realistic entity counts (3-10)

**Cons:**
- Most complex to implement
- Multiple parameters to tune (MIN, MAX)

---

**My Recommendation: Option B (Relative) for Phase 3, Option D (Hybrid) for Phase 4+**

**Reasoning:**
- Start simple (relative threshold auto-scales)
- Test if oscillation or fragmentation occurs
- Add bounds (Option D) if needed in Phase 4

**Trade-offs:**
- Optimizing for adaptability (auto-scaling)
- Sacrificing predictability (dynamic threshold)
- Can add safety bounds later if problems emerge

**Uncertainty:**
- Will relative threshold oscillate in practice?
- Is median + 2σ the right statistical cutoff? (Could be median + 1σ or + 3σ)
- How does this interact with entity competition model (#010)?

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Use a **relative, smoothed threshold** with safety bounds and **hysteresis**. Make emergence depend on **(energy × coherence)**, not energy alone, and couple it (lightly) to #010 once that decision lands.

---

#### Algorithm
1) Compute per‑cluster:
```
E = Σ_i e_i,      Q = coherence(cluster) ∈ [0,1],    S = E · Q
```
2) Build distribution of S across active clusters this tick.  
3) **Threshold τ** = median(S) + 2·stdev(S) over an **EMA‑smoothed** window (e.g., β=0.9).  
4) **Bounds:** τ ← max(τ, τ_min) and cap candidates to **MAX_ENTITIES** by lifting τ to the S at rank MAX_ENTITIES if needed.  
5) **Hysteresis:** Existing entities remain active down to **0.9·τ**; new ones require **1.1·τ** to avoid flicker.

```python
τ_raw = median(S) + 2*std(S)
τ = max(τ_raw, τ_min)
cands = [c for c in clusters if S[c] > τ]
if len(cands) > MAX_ENTITIES:
    τ = sorted([S[c] for c in clusters], reverse=True)[MAX_ENTITIES-1]
```

---

#### Notes
- **Coherence** can combine intra‑density, boundary sparsity, and semantic tightness; start with density×semantic.
- Smooth τ with EMA to prevent rapid swings under perturbations.
- Report both **entities emerged** and **near‑misses** (S within 10% of τ) for debugging.

**Decision suggestion:** Adopt the hybrid threshold with hysteresis and a cap (MAX_ENTITIES≈10). Revisit coupling to #010 after entity‑competition decision.


### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

## Debate & Convergence

**Key Points of Agreement:**
- [To be filled as perspectives arrive]

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- Absolute, relative, top-N, or hybrid threshold?
- If relative, what statistical measure? (median + 2σ, other?)
- Do we need floor/ceiling bounds?
- How does this interact with entity competition (#010)?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/07_entity_emergence.md` - Add "Emergence Threshold Calculation" section
- [ ] `mechanisms/07_entity_emergence.md` - Specify chosen algorithm (absolute/relative/hybrid)
- [ ] `emergence/entity_formation_patterns.md` - Update examples with realistic thresholds
- [ ] `phenomenology/entity_activation_experience.md` - Describe what triggers emergence

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Small (once decision made - just threshold calculation)

**Dependencies:**
- Depends on entity competition model (#010) - affects cluster energy accumulation
- Might affect workspace capacity (#009) - how many entities fit in consciousness

**Verification:**
- Test with small graph (100 nodes) - verify 3-5 entities emerge
- Test with large graph (10K nodes) - verify still 3-5 entities (not 500)
- Test with quiet system (low energy) - verify entities don't emerge inappropriately
- Test with energized system (high energy) - verify multiple entities emerge

---

## Process Notes

**How this discussion evolved:**
Identified as **specification gap** - mechanism described but critical parameter undefined.

**Lessons learned:**
[To be filled as discussion progresses]
