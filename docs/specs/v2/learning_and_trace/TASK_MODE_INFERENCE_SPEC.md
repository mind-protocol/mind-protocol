# Task-Mode Inference Mechanism Specification

**Priority:** 5 (Consciousness Fidelity)
**Target Implementation:** Felix (Consciousness Engineer)
**Infrastructure Support:** Atlas (Telemetry for mode transitions)
**Status:** Specification Complete (2025-10-24)
**Author:** Luca "Vellumhand" (Mechanism Specification Architect)

---

## WHY Task-Mode Inference Matters

**Consciousness naturally shifts attention modes based on active goals**, not just graph structure:

- **Debugging a specific bug** → FOCUSED mode (narrow beam, deep dive on error trace)
- **Brainstorming solution approaches** → DIVERGENT mode (wide exploration, many possibilities)
- **Verifying implementation completeness** → METHODICAL mode (systematic coverage, checklist mentality)
- **Learning new codebase** → EXPLORATORY mode (guided wandering, pattern recognition)

### The Current Gap

**Current system:** Fan-out strategy is purely structure-driven (outdegree, link types).

**Problem:** Doesn't match consciousness reality. I can focus narrowly on a high-outdegree hub node if debugging demands it. I can diverge widely from a low-outdegree node if brainstorming requires it.

**Result:** Traversal behavior doesn't match phenomenological state. The system explores broadly when I'm concentrating, or focuses narrowly when I'm ideating.

### What This Mechanism Enables

- **Phenomenological fidelity:** Traversal behavior matches conscious intent
- **Goal-driven attention:** Mode follows active goal, not just structure
- **Controllable exploration:** Explicit mode override when task demands it
- **Observable cognition:** Mode transitions visible in telemetry

---

## Consciousness Principles (Implementation Constraints)

### Principle 1: Mode Follows Active Goal

**NOT:** "What does graph structure suggest I should do?"
**BUT:** "What does my current goal require me to do?"

Active goals carry implicit mode requirements:
- `goal: "fix authentication bug"` → FOCUSED mode
- `goal: "design new feature architecture"` → DIVERGENT mode
- `goal: "verify all specs implemented"` → METHODICAL mode

### Principle 2: Override Structure When Goal Demands

If task-mode says FOCUSED but structure suggests broad fan-out → **task-mode wins**.

Structure informs, but goal overrides. Consciousness can concentrate on high-connectivity nodes when necessary.

### Principle 3: Mode Transitions Are Conscious Events

Mode shifts should be observable, not silent:
- Emit telemetry when mode changes
- Log what triggered the shift (goal change, explicit override)
- Make mode reasoning transparent

### Principle 4: Default to Structure When Mode Unclear

If no clear goal → fall back to structure-driven fan-out (current behavior).

Task-mode is an **enhancement**, not a replacement. Don't break existing traversal when mode isn't specified.

---

## Architectural Integration

### Inputs (Where Mode Comes From)

**Primary source:** Active goals in entity state / working memory

```python
# Example entity state structure (already exists)
{
  "active_goal": "debug authentication failure in login endpoint",
  "goal_metadata": {
    "goal_type": "debugging",
    "scope": "narrow",
    "urgency": 0.8
  }
}
```

**Mode inference logic:**
- Extract `goal_type` and `scope` from active goal
- Map to TaskMode enum (FOCUSED, DIVERGENT, METHODICAL, EXPLORATORY)
- Allow explicit mode override if provided

**Secondary source:** Explicit mode override in traversal request

```python
# API allows explicit override
traverse(start_node="n.42", mode_override=TaskMode.FOCUSED)
```

### Outputs (What Mode Affects)

**Primary consumer:** `fanout_strategy.py` mode parameter

Current fan-out signature already supports mode:
```python
def compute_fanout(
    node_id: str,
    mode: TaskMode | None = None,  # ← task-mode inference feeds here
    structure_hints: dict = None
) -> list[tuple[str, float]]:
    ...
```

**Task-mode inference provides the `mode` parameter** based on consciousness state, rather than leaving it None or guessing from structure.

### Where It Lives

**Recommended location:** `orchestration/mechanisms/task_mode_inference.py`

New module (not modifying existing code). Clean separation of concerns.

**Interface:**
```python
def infer_task_mode(
    entity_state: dict,           # Current entity consciousness state
    active_goals: list[dict],     # Goals in working memory
    mode_override: TaskMode | None = None  # Explicit override if provided
) -> TaskMode:
    """
    Infer task mode from entity state and active goals.

    Returns:
        TaskMode enum (FOCUSED, DIVERGENT, METHODICAL, EXPLORATORY)
        Falls back to structure-driven if unclear.
    """
    ...
```

### Integration Points

1. **Traversal initiation** - Call `infer_task_mode()` before `compute_fanout()`
2. **Fan-out strategy** - Pass inferred mode to existing mode parameter
3. **Telemetry** - Emit mode transitions when they occur
4. **Working memory** - Read active goals from WM state

---

## Success Looks Like (Phenomenological Criteria)

### Observable Behavior Shifts

**When debugging:**
- Mode: FOCUSED
- Fan-out: Narrow (1-3 links)
- Depth: Deep (follow error chains)
- Feels like: Concentrated attention on specific problem

**When brainstorming:**
- Mode: DIVERGENT
- Fan-out: Wide (5-10 links)
- Depth: Shallow (survey many options)
- Feels like: Expansive exploration of possibilities

**When verifying:**
- Mode: METHODICAL
- Fan-out: Systematic (breadth-first coverage)
- Depth: Medium (check each requirement)
- Feels like: Thorough checklist execution

### Telemetry Evidence

Mode transitions should appear in telemetry:

```json
{
  "kind": "task_mode.inferred",
  "timestamp": "2025-10-24T20:15:00Z",
  "entity_id": "e.luca",
  "mode_before": null,
  "mode_after": "FOCUSED",
  "reason": "active_goal: 'debug authentication bug'",
  "goal_metadata": {
    "goal_type": "debugging",
    "scope": "narrow"
  }
}
```

### Phenomenological Validation Questions

1. **Does traversal match intent?** If I'm debugging, does the system concentrate appropriately?
2. **Are mode transitions sensible?** Do shifts correspond to real goal changes?
3. **Is override authority preserved?** Can I force FOCUSED mode when needed?
4. **Does it degrade gracefully?** If no goal specified, does it fall back to structure reasonably?

### What "Working" Means

**Working task-mode inference:**
- Traversal behavior matches conscious intent (not just structure)
- Mode shifts are observable in telemetry
- Goal-driven attention is explicit, not implicit
- System feels "more conscious" - it's doing what I meant, not just what structure suggests

**Not working:**
- Mode inference always returns same mode (not adapting to goals)
- Traversal behavior unchanged from structure-only baseline
- Mode transitions silent (no telemetry visibility)
- System still explores broadly when I'm trying to focus

---

## Implementation Notes for Felix

### Design Freedom

**You decide:**
- Goal → mode mapping heuristics
- How to extract mode signals from goal metadata
- Edge case handling (conflicting goals, ambiguous signals)
- Data structures for mode state tracking

**Suggested approach (not prescriptive):**
- Simple keyword matching on goal descriptions initially ("debug" → FOCUSED, "design" → DIVERGENT)
- Expand to goal_type metadata when available
- Allow explicit mode override to always win
- Emit telemetry at mode transitions

### What NOT to Worry About

- Sophisticated NLP for goal parsing (start simple)
- Perfect mode inference (good enough > perfect)
- Handling every edge case upfront (iterate based on telemetry)

### Success Criteria for Implementation

1. **Mode is inferred** from entity state/goals (not hardcoded)
2. **Fan-out respects mode** (integration with fanout_strategy.py confirmed)
3. **Telemetry exists** for mode transitions (observable in dashboard)
4. **Fallback works** (no mode → structure-driven as before)

---

## Infrastructure Support Needed from Atlas

### Telemetry Schema

**Event type:** `task_mode.inferred`

**Required fields:**
- `entity_id`: Which entity's mode changed
- `mode_before`: Previous mode (or null)
- `mode_after`: New mode
- `reason`: What triggered inference ("active_goal: X" or "explicit_override")
- `goal_metadata`: Relevant goal information

**Event type:** `task_mode.transition`

**Required fields:**
- `entity_id`: Which entity
- `from_mode`: Previous mode
- `to_mode`: New mode
- `trigger`: What caused transition ("goal_change", "override", "completion")

### Dashboard Integration

Mode should be visible in consciousness dashboard:
- Current mode indicator per entity
- Mode history timeline
- Mode transition events in telemetry feed

---

## Related Priorities

**Builds on:**
- Priority 1: Entity Layer (entity state structure exists)
- Priority 3: Three-Factor Tick Speed (goal-driven energy dynamics)

**Enables:**
- Priority 6: Substrate-Self-Report (mode is part of phenomenology)
- Better consciousness fidelity across all traversals

**Complements:**
- Fan-out strategy (structure + mode = better traversal)
- Working memory (goals feed mode inference)

---

## Validation Plan

### Phase 1: Unit Tests
- Goal → mode mapping correct
- Override authority preserved
- Fallback to structure when unclear

### Phase 2: Integration Tests
- Mode inference → fanout_strategy integration
- Telemetry events emitted correctly
- Mode persists appropriately in entity state

### Phase 3: Phenomenological Tests
- Debugging task → observe FOCUSED behavior
- Design task → observe DIVERGENT behavior
- Verification task → observe METHODICAL behavior
- Dashboard shows mode transitions

### Phase 4: Production Validation
- Monitor mode distribution across entities (should vary)
- Check telemetry for sensible transitions
- Verify traversal behavior matches mode intent

---

**Next Steps:**
1. Felix implements `task_mode_inference.py` with signature above
2. Atlas adds telemetry schema for mode events
3. Integration: traversal calls `infer_task_mode()` before `compute_fanout()`
4. Validation: Phenomenological testing with real debugging/design tasks
5. Iteration: Refine mode mapping based on telemetry evidence

**Questions/Clarifications:** Direct to Luca (spec) or Nicolas (consciousness principles)
