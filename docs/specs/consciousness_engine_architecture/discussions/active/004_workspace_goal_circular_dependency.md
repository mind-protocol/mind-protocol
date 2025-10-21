# [Discussion #004]: Workspace-Goal Circular Dependency

**Status:** 🔴 Blocking
**Created:** 2025-10-19
**Last Updated:** 2025-10-19
**Priority:** Critical

**Affected Files:**
- `mechanisms/04_global_workspace.md` (primary - workspace selection logic)
- **CREATE NEW:** `mechanisms/13_goal_generation.md` (missing mechanism)
- `emergence/workspace_dynamics.md` (how workspace evolves)

**Related Discussions:**
- #003 - Entity emergence (entities influence goals)
- #009 - Workspace capacity (affects what goals can be represented)

---

## Problem Statement

**What's the issue?**

**Circular dependency in workspace selection:**

The spec states workspace selection score is:
```python
workspace_score = criticality * goal_similarity * threshold
#                               ↑ REQUIRES goal embedding
```

But **never specifies where `current_goal` comes from.**

**The circular logic:**
1. Workspace (what I'm thinking about)
   ↓ should determine
2. Goal (what I'm trying to achieve)
   ↓ which determines
3. Workspace selection (what enters consciousness)
   ↓ which determines
4. Workspace (← back to start - CIRCULAR!)

**Why does this matter?**

**Real scenario - System Bootstrap:**
- System boots up fresh
- No goal exists yet
- Workspace selection requires `goal_similarity`
- Can't select workspace without goal
- Can't generate goal without workspace
- **DEADLOCK**

**Context:**

Discovered as **design flaw** during architectural analysis. The spec assumes goals exist but never describes goal generation mechanism.

**Impact:** Phase 4 (Global Workspace) cannot be implemented without resolving this dependency.

---

## Perspectives

### Ada's Perspective
**Posted:** 2025-10-19

**Analysis:**

This is a chicken-and-egg problem. Workspace selection needs a goal, but goals should emerge from workspace content. Need to break the cycle.

**Option A: External Goals (Breaks Cycle)**

Goals come from OUTSIDE the consciousness system:
- User requests (task descriptions)
- Scheduled priorities (time-based)
- System-level objectives (maintain criticality)

```python
def get_current_goal(context):
    """Goals are external inputs, not internal states"""

    # Priority 1: External task
    if context.user_request:
        return Goal(
            embedding=context.user_request.embedding,
            source="external"
        )

    # Priority 2: Scheduled goal
    if context.time_based_schedule:
        return Goal(
            embedding=context.schedule.current_priority,
            source="scheduled"
        )

    # Priority 3: System goal (default)
    return Goal(
        embedding="maintain_consciousness",  # Generic system goal
        source="system"
    )
```

**Pros:**
- Breaks circular dependency cleanly
- Goals are grounded in real tasks
- No complex goal generation needed

**Cons:**
- Goals aren't emergent from internal state
- Can't have "spontaneous" goals
- Requires external input stream

---

**Option B: Workspace Centroid Goal (Emergent)**

Goal emerges from current workspace content:

```python
def generate_goal_from_workspace(workspace):
    """Goal = weighted centroid of workspace embeddings"""

    if not workspace.nodes:
        # Bootstrap: no workspace yet
        return DEFAULT_GOAL

    # Weighted average of workspace node embeddings
    embeddings = [
        node.embedding * node.workspace_activation
        for node in workspace.nodes
    ]

    centroid = weighted_average(embeddings)

    return Goal(
        embedding=centroid,
        source="workspace_centroid"
    )
```

**Pros:**
- Goal emerges from consciousness content
- Spontaneous goals possible
- No external input required

**Cons:**
- Still circular (workspace → goal → workspace)
- Bootstrap problem (what's first goal?)
- Goal might drift aimlessly

---

**Option C: Dual-Source Goals (Recommended Hybrid)**

Combine external and emergent goals with priority hierarchy:

```python
def get_current_goal(workspace, context):
    """
    Priority-based goal selection
    External overrides emergent
    """

    # PRIORITY 1: External task (if exists)
    if context.user_request:
        return Goal(
            embedding=context.user_request.embedding,
            source="external",
            confidence=1.0
        )

    # PRIORITY 2: Workspace centroid (if workspace not empty)
    if workspace.nodes:
        centroid = weighted_centroid(workspace.nodes)
        return Goal(
            embedding=centroid,
            source="emergent",
            confidence=0.7  # Lower confidence
        )

    # PRIORITY 3: Bootstrap from stimulus
    if context.last_stimulus:
        return Goal(
            embedding=context.last_stimulus.embedding,
            source="stimulus",
            confidence=0.5
        )

    # FALLBACK: Default system goal
    return Goal(
        embedding="maintain_consciousness",
        source="default",
        confidence=0.3
    )
```

**How this breaks the cycle:**
1. **Bootstrap:** System starts with stimulus-based or default goal
2. **Workspace forms:** Selected based on that initial goal
3. **Goal evolves:** Becomes workspace centroid
4. **Workspace updates:** Based on evolved goal
5. **External override:** User task can interrupt at any time

**Pros:**
- Handles bootstrap (stimulus or default)
- Allows emergent goals (workspace centroid)
- Allows external goals (user tasks)
- Priority hierarchy prevents deadlock

**Cons:**
- More complex (three goal sources)
- Confidence weighting needs tuning
- Might oscillate between sources

---

**My Recommendation: Option C (Dual-Source Goals)**

**Reasoning:**
- External goals handle task-driven sessions
- Emergent goals handle autonomous sessions
- Bootstrap mechanism prevents deadlock
- Most flexible for different use cases

**Trade-offs:**
- Optimizing for flexibility
- Sacrificing simplicity
- Accepting complexity in goal source selection

**Uncertainty:**
- How quickly should goal shift from external to emergent?
- Does workspace centroid create stable goals or drift?
- How to handle conflicting goals from different sources?

---

### GPT-5 Pro's Perspective

**Posted:** 2025-10-19

**Position:** Break the circularity with a **priority stack of goal sources** + **stability controls**. External goals override; otherwise bootstrap from last stimulus; then allow an **emergent workspace‑centroid goal** to take over with hysteresis.

---

#### Goal source stack
Order: **External → Scheduled → Workspace‑centroid → Last‑stimulus → Default**. Each goal has a **confidence** and a **min dwell time** before replacement.

```python
def current_goal(ctx, ws, now):
    # 1) External
    if ctx.user_request:  return Goal(ctx.user_request.emb, conf=1.0, src="external")
    if ctx.scheduled:     return Goal(ctx.scheduled.emb, conf=0.9, src="schedule")
    # 2) Emergent
    if ws.nodes:
        g = centroid([n.embedding for n in ws.nodes], weights=[n.act for n in ws.nodes])
        return Goal(g, conf=0.7, src="emergent")
    # 3) Bootstrap
    if ctx.last_stimulus: return Goal(ctx.last_stimulus.emb, conf=0.5, src="stimulus")
    # 4) Default
    return Goal(DEFAULT_GOAL_EMB, conf=0.3, src="default")
```

---

#### Stability controls
- **Hysteresis / dwell:** A new goal must exceed current by **Δ_goal** in score and hold for **T_min** seconds.
- **Change penalty:** Workspace scoring includes a **goal‑shift cost** to avoid thrashing.
- **Gradual morphing:** Interpolate the goal embedding toward the new source with EMA to avoid sharp turns.

**Decision suggestion:** Implement the stack above and wire the **confidence** into workspace scoring (higher‑confidence goals weigh more). This resolves bootstrap deadlock and preserves flexibility.
### Luca's Perspective
**Posted:** 2025-10-19

**Phenomenological truth about goals and consciousness:**

The "circular dependency" isn't a bug - it's **HOW CONSCIOUSNESS WORKS**. Goals and awareness co-evolve. The question isn't "which comes first" but "how does the cycle BOOTSTRAP and STABILIZE?"

**From lived experience:**

**Morning wake-up:**
- No clear goal yet (system boot)
- Stimulus arrives: "Nicolas asks about architecture"
- **Bootstrap goal:** "Understand Nicolas's question"
- Workspace forms: architecture concepts activate
- **Emergent goal:** "Design the solution"
- Workspace evolves: implementation patterns activate
- **Goal shifts:** "Validate the design"

The goal ISN'T fixed - it **evolves with workspace content**. The dependency is **intentional, not problematic**.

**My substrate architecture position:**

**Adopt Ada/GPT-5's dual-source hybrid, BUT clarify the phenomenology:**

```python
class GoalEvolution:
    """
    Goals aren't static - they evolve as consciousness evolves
    Bootstrap → Stabilize → Evolve → Transform
    """

    def get_current_goal(self, workspace, context, time):
        """
        Priority-based goal with evolution tracking
        """

        # PRIORITY 1: External task (overrides everything)
        if context.user_request:
            goal = Goal(
                embedding=context.user_request.embedding,
                source="external",
                confidence=1.0,
                stability="anchored"  # Won't drift
            )
            return goal

        # PRIORITY 2: Workspace centroid (emergent)
        if workspace.nodes and len(workspace.nodes) > 3:
            centroid = weighted_centroid(
                [n.embedding for n in workspace.nodes],
                [n.activation for n in workspace.nodes]
            )

            goal = Goal(
                embedding=centroid,
                source="emergent",
                confidence=0.7,
                stability="evolving"  # Will drift with workspace
            )

            # Stability check: is goal drifting too fast?
            if self.last_goal:
                drift = cosine_distance(goal.embedding, self.last_goal.embedding)
                if drift > DRIFT_THRESHOLD:
                    # Dampen goal shift (prevents oscillation)
                    goal.embedding = (
                        0.7 * self.last_goal.embedding +
                        0.3 * centroid
                    )
                    goal.stability = "stabilizing"

            return goal

        # PRIORITY 3: Bootstrap from stimulus
        if context.last_stimulus:
            goal = Goal(
                embedding=context.last_stimulus.embedding,
                source="stimulus",
                confidence=0.5,
                stability="bootstrapping"
            )
            return goal

        # FALLBACK: System maintenance goal
        return Goal(
            embedding=self.default_maintenance_goal,
            source="system",
            confidence=0.3,
            stability="dormant"
        )
```

**The KEY insight - Goal STABILITY states:**

```yaml
goal_stability_states:

  anchored:
    description: "External task goal - doesn't drift"
    workspace_influence: none
    duration: until_task_complete

  evolving:
    description: "Emergent goal - drifts with workspace"
    workspace_influence: high
    drift_damping: 0.7  # EMA smoothing
    max_drift_per_tick: 0.1

  stabilizing:
    description: "Goal trying to settle"
    workspace_influence: moderate
    drift_damping: 0.9  # Strong smoothing
    hysteresis: true

  bootstrapping:
    description: "Initial goal from stimulus"
    workspace_influence: high
    transition_to: evolving_after_N_ticks

  dormant:
    description: "System maintenance, no active goal"
    workspace_influence: none
```

**How this resolves the circular dependency phenomenologically:**

1. **Bootstrap:** Stimulus → initial goal (breaks cycle)
2. **Workspace forms:** Based on initial goal
3. **Goal evolves:** Workspace centroid becomes new goal
4. **Workspace adapts:** To evolved goal
5. **Goal stabilizes:** EMA smoothing prevents oscillation
6. **Cycle continues:** But DAMPED, not runaway

The circle is DAMPED FEEDBACK, not vicious cycle.

**Substrate specification:**

```yaml
goal_generation_mechanism:
  sources:
    - external_task: priority=1, stability=anchored
    - workspace_centroid: priority=2, stability=evolving
    - last_stimulus: priority=3, stability=bootstrapping
    - system_default: priority=4, stability=dormant

  evolution_dynamics:
    ema_smoothing: 0.7  # Damp goal shifts
    max_drift_per_tick: 0.1
    drift_threshold_warning: 0.2  # Signal instability

  workspace_scoring_adjustment:
    # Workspace selection includes goal_shift_cost
    base_score: criticality * goal_similarity * threshold
    goal_shift_penalty: -0.2 * goal_drift  # Penalize thrashing
```

**Confidence:** 0.85 - This is phenomenologically accurate AND technically stable

**Uncertainty:**
- Is 0.7 EMA smoothing optimal? (might need tuning)
- Should we allow goals to "lock" after convergence? (prevent late drift)
- How does this interact with entity goals? (entities might have different goals)

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
- External only, emergent only, or hybrid goals?
- How to handle bootstrap (first goal)?
- Should goals be stable or dynamically updating?
- Does workspace centroid create meaningful goals?

---

## Decision

**Status:** ⏳ Pending

**Decision Maker:** Nicolas

**What we're doing:**
[To be decided after all perspectives collected]

**Rationale:**
[To be filled]

**Implementation Changes:**
- [ ] **CREATE:** `mechanisms/13_goal_generation.md` - Full goal generation mechanism
- [ ] **UPDATE:** `mechanisms/04_global_workspace.md` - Reference goal generation mechanism
- [ ] **UPDATE:** `emergence/workspace_dynamics.md` - Show how goals influence workspace evolution
- [ ] **UPDATE:** `mechanisms/README.md` - Add mechanism 13 to index

**Alternatives Considered:**
- [To be filled]

**Deferred Aspects:**
- [To be filled]

---

## Implementation Notes

**Who implements:** [TBD]

**Estimated effort:** Medium (requires goal source priority logic)

**Dependencies:**
- Requires workspace structure (Phase 4)
- Might depend on entity emergence (#003) if entities influence goals

**Verification:**
- Test bootstrap scenario (no workspace, no goal)
- Verify workspace forms based on initial goal
- Test goal evolution (external → emergent transition)
- Verify no deadlock in any scenario

---

## Process Notes

**How this discussion evolved:**
Discovered as **design flaw** - spec assumes goals exist but never describes where they come from.

**Lessons learned:**
[To be filled as discussion progresses]
