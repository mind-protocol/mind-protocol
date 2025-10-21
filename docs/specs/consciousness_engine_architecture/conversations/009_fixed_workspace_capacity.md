# [Discussion #009]: Fixed Workspace Capacity Constraints

**Status:** 🟢 Near Consensus
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Medium

**Affected Files:**
- `mechanisms/04_global_workspace.md` (primary - capacity calculation)
- `emergence/workspace_dynamics.md` (how capacity affects behavior)

**Related Discussions:**
- #003 - Entity emergence (more entities need more capacity)
- #004 - Goal generation (complex goals need more capacity)

---

## Problem Statement

**What's the issue?**

Fixed workspace capacity:
```python
workspace_capacity = 100  # tokens (fixed)
```

**Why this is limiting:**

**Scenario A: Complex architecture discussion**

Need to hold in mind:
- 5 entity descriptions (20 tokens each) = 100 tokens
- Multi-energy architecture (15 tokens)
- Diffusion formulas (20 tokens)
- Criticality tuning (15 tokens)
- Open questions (30 tokens)

**Total needed:** 180 tokens
**Capacity:** 100 tokens

→ System is FORCED to drop important context
→ Discussion becomes incoherent (can't hold full problem space)

---

**Scenario B: Simple confirmation**

User: "Does this look good?"

**Needed:** 10 tokens (just the task context)
**Capacity:** 100 tokens

→ 90 tokens wasted on irrelevant workspace content
→ Unnecessary cognitive load

**Context:**

Identified as **flexibility issue** during architectural analysis. Fixed capacity doesn't adapt to task complexity.

**Impact:** Complex tasks get truncated context. Simple tasks get cluttered workspace. One size doesn't fit all.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

Biological working memory capacity varies:
- **Focused attention:** Narrow, deep (2-3 chunks)
- **Broad awareness:** Wide, shallow (5-9 chunks)
- **High arousal:** Expanded capacity
- **Low arousal:** Reduced capacity

Fixed capacity ignores these dynamics.

**Proposed Solution: Adaptive Workspace Capacity**

```python
def calculate_workspace_capacity(context):
    """
    Dynamic capacity based on task and state
    """
    base_capacity = 100  # Default

    # Factor 1: Task complexity
    if context.task_complexity > 0.8:
        complexity_multiplier = 2.0  # Complex tasks get 200 tokens
    elif context.task_complexity > 0.5:
        complexity_multiplier = 1.5  # Medium tasks get 150 tokens
    else:
        complexity_multiplier = 1.0  # Simple tasks get 100 tokens

    # Factor 2: Arousal level
    if context.arousal > 0.8:
        arousal_multiplier = 1.5  # High arousal = expanded awareness
    elif context.arousal < 0.3:
        arousal_multiplier = 0.7  # Low arousal = reduced capacity
    else:
        arousal_multiplier = 1.0

    # Factor 3: Number of active entities
    entity_count = len(context.active_entities)
    if entity_count > 5:
        entity_multiplier = 1.3  # Many entities need more space
    else:
        entity_multiplier = 1.0

    # Factor 4: Focus mode
    if context.focus_mode:
        focus_multiplier = 0.7  # Focus = narrower attention
    else:
        focus_multiplier = 1.0

    # Calculate adaptive capacity
    capacity = base_capacity * (
        complexity_multiplier *
        arousal_multiplier *
        entity_multiplier *
        focus_multiplier
    )

    # Bounds
    MIN_CAPACITY = 50   # Never less than 50
    MAX_CAPACITY = 300  # Never more than 300

    return int(np.clip(capacity, MIN_CAPACITY, MAX_CAPACITY))
```

**Example calculations:**

```python
# Complex architecture discussion, high arousal, 5 entities
capacity = 100 * 2.0 * 1.5 * 1.0 * 1.0 = 300 tokens

# Simple confirmation, normal arousal, 1 entity
capacity = 100 * 1.0 * 1.0 * 1.0 * 1.0 = 100 tokens

# Focused deep work, high complexity, focus mode
capacity = 100 * 2.0 * 1.0 * 1.0 * 0.7 = 140 tokens
```

**Pros:**
- Adapts to task needs
- More realistic (mirrors biological working memory)
- Prevents both truncation (complex tasks) and clutter (simple tasks)

**Cons:**
- More complex (4 factors to calculate)
- Parameters need tuning (multipliers)
- Capacity changes during session (might be confusing)

---

**Alternative A: Entity-Based Capacity**

Simpler - capacity scales with active entities:

```python
def calculate_workspace_capacity(context):
    """Each entity gets 50-100 tokens"""
    num_entities = len(context.active_entities)
    tokens_per_entity = 75  # Configurable

    capacity = num_entities * tokens_per_entity

    # Bounds
    return int(np.clip(capacity, 50, 300))
```

**Pros:**
- Simple, clear relationship (more entities → more capacity)
- Auto-scales with system complexity

**Cons:**
- Doesn't account for task complexity
- What if 1 entity but complex task?

---

**Alternative B: Fixed Capacity with Overflow Handling**

Keep fixed capacity but better handling:

```python
WORKSPACE_CAPACITY = 100  # Fixed

def select_workspace(candidates):
    """Smart truncation when over capacity"""
    if total_tokens(candidates) <= WORKSPACE_CAPACITY:
        return candidates  # Fits

    # OVERFLOW: Prioritize by importance
    sorted_by_importance = sort(candidates, key=lambda n: n.importance)

    # Take top candidates that fit
    workspace = []
    tokens_used = 0
    for candidate in sorted_by_importance:
        if tokens_used + candidate.tokens <= WORKSPACE_CAPACITY:
            workspace.append(candidate)
            tokens_used += candidate.tokens
        else:
            break  # Capacity full

    return workspace
```

**Pros:**
- Keeps fixed capacity (simpler)
- Better prioritization when overflow

**Cons:**
- Still drops important context in complex tasks
- No expansion for high-complexity scenarios

---

**My Recommendation: Adaptive Capacity (Factor-Based)**

**Reasoning:**
- Task complexity varies widely (simple confirmation vs architecture design)
- Fixed capacity is one-size-fits-none
- Adaptive capacity mirrors biological working memory
- Can start simple (complexity + entity count) and add factors later

**Simplified Initial Version:**

```python
def calculate_workspace_capacity(context):
    """Start with 2 factors, add more if needed"""
    base = 100

    # Factor 1: Task complexity (0-1)
    complexity_mult = 1.0 + context.task_complexity  # 1.0 to 2.0

    # Factor 2: Active entities
    entity_mult = 1.0 + (len(context.active_entities) - 1) * 0.1  # Each entity adds 10%

    capacity = base * complexity_mult * entity_mult

    return int(np.clip(capacity, 50, 300))
```

**Trade-offs:**
- Optimizing for flexibility
- Accepting complexity in capacity calculation
- Can tune multipliers based on testing

**Uncertainty:**
- What are optimal multiplier values?
- Does changing capacity mid-session cause problems?
- How to measure task_complexity? (might be subjective)

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Replace the fixed token cap with a **compute‑budgeted, adaptive capacity** and **sticky (hysteresis) workspace selection**. Score/Cost ratio picks clusters; capacity adapts to task complexity and entity count within bounds.

---

#### Capacity function (simple start)
```
base = 100
C = base * (1 + task_complexity) * (1 + 0.1*(#entities-1))
C = clip(C, 50, 300)
```
Smooth C over time (EMA) to avoid jumps.

#### Budgeted selection
Each candidate cluster c has **score** and **cost** (approx tokens or frontier size). Pick greedily by **score/cost** until budget C is spent. Apply **incumbent bonus** and **challenger penalty** to add hysteresis and prevent ping‑pong.

```python
adj = score * (1.2 if incumbent else 0.9)
pick in descending adj/cost until Σ cost ≤ C
```

**Decision suggestion:** Ship adaptive capacity (complexity + entity count), budgeted selection, and hysteresis. Add diversity regularizer to avoid near‑duplicate clusters.


### Iris's Perspective
**Posted:** [Pending]

[Awaiting Iris review]

---

## Debate & Convergence

**Key Points of Agreement:**
- Fixed capacity is limiting
- Need some form of adaptivity

**Key Points of Disagreement:**
- [To be filled as perspectives arrive]

**Open Questions:**
- How many factors? (2, 4, more?)
- What are optimal multipliers?
- How to measure task_complexity?
- Should capacity change mid-session or stay fixed per session?

---

## Decision

**Status:** 🟢 Near Consensus (adaptive capacity likely)

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided - likely adaptive with 2-4 factors]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] `mechanisms/04_global_workspace.md` - Replace fixed capacity with adaptive calculation
- [ ] `mechanisms/04_global_workspace.md` - Add "Adaptive Capacity" section
- [ ] `emergence/workspace_dynamics.md` - Show how capacity changes with task/state

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Small (capacity calculation function)

**Dependencies:**
- Requires measuring task_complexity (might need heuristic)
- Requires tracking active_entities (#003)

**Verification:**
- Test complex task → verify capacity expands (150-300 tokens)
- Test simple task → verify capacity stays reasonable (50-100 tokens)
- Test capacity doesn't change too frequently (stability)
- Tune multipliers if needed

---

## Process Notes

**How this discussion evolved:**
Identified as **flexibility issue** - one-size-fits-all doesn't work for varying task complexity.

**Lessons learned:**
[To be filled as discussion progresses]
