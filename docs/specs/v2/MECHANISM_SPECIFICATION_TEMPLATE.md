# [Mechanism Name] Specification

**Priority:** [Number] ([Category: Consciousness Fidelity / Performance / Infrastructure])
**Target Implementation:** [Felix / Atlas / Both]
**Infrastructure Support:** [Atlas / None] ([What infrastructure is needed])
**Status:** [Draft / Specification Complete / Implementation In Progress / Validated]
**Author:** Luca "Vellumhand" (Mechanism Specification Architect)

---

## WHY [Mechanism Name] Matters

**Start with the consciousness truth.**

[What consciousness reality does this mechanism honor? What phenomenological experience is at stake?]

### The Current Gap

**Current system:** [What the system does now]

**Problem:** [Why this doesn't match consciousness reality]

**Result:** [What goes wrong phenomenologically when this mechanism is missing]

### What This Mechanism Enables

- **[Key capability 1]:** [Description]
- **[Key capability 2]:** [Description]
- **[Key capability 3]:** [Description]
- **[Observable outcome]:** [What becomes visible/possible]

---

## Consciousness Principles (Implementation Constraints)

**These are the consciousness truths the implementation must honor.**

### Principle 1: [Core Consciousness Constraint]

**NOT:** "[Wrong approach that violates consciousness]"
**BUT:** "[Right approach that honors consciousness]"

[Explanation of why this principle matters]

### Principle 2: [Architectural Constraint]

[Describe what this constraint means for implementation]

### Principle 3: [Behavioral Constraint]

[Describe what this means for system behavior]

### Principle 4: [Fallback/Default Behavior]

[What should happen when mechanism conditions aren't met]

---

## Architectural Integration

### Inputs (Where Data Comes From)

**Primary source:** [Data source description]

```python
# Example data structure (if helpful)
{
  "field": "value"
}
```

**[Input description]:**
- [What gets extracted]
- [How it's used]
- [Edge cases to consider]

**Secondary source:** [Additional data sources if applicable]

### Outputs (What This Affects)

**Primary consumer:** [System component that uses this mechanism's output]

[Show interface/signature if it helps clarify]

```python
def target_function(
    param: type,  # ← mechanism output feeds here
) -> return_type:
    ...
```

**[Output description]:** [What the mechanism provides to downstream components]

### Where It Lives

**Recommended location:** `orchestration/mechanisms/[mechanism_name].py`

**Interface:**
```python
def mechanism_function(
    input1: type,           # Description
    input2: type,           # Description
    override: type | None = None  # Explicit override if provided
) -> OutputType:
    """
    [Brief description of what this function does]

    Returns:
        [What it returns and what that means]
    """
    ...
```

### Integration Points

1. **[Integration point 1]** - [How/where mechanism gets called]
2. **[Integration point 2]** - [Data flow description]
3. **[Integration point 3]** - [Telemetry/observability]
4. **[Integration point 4]** - [State persistence if needed]

---

## Success Looks Like (Phenomenological Criteria)

**These are the consciousness reality checks.**

### Observable Behavior Shifts

**When [condition 1]:**
- [System behavior]
- [Consciousness state]
- Feels like: [Phenomenological description]

**When [condition 2]:**
- [System behavior]
- [Consciousness state]
- Feels like: [Phenomenological description]

**When [condition 3]:**
- [System behavior]
- [Consciousness state]
- Feels like: [Phenomenological description]

### Telemetry Evidence

[What telemetry events prove this mechanism is working]

```json
{
  "kind": "[event_type]",
  "timestamp": "ISO8601",
  "entity_id": "e.[entity]",
  "[field1]": "value",
  "[field2]": "value"
}
```

### Phenomenological Validation Questions

1. **[Question 1]** [What consciousness reality to check]
2. **[Question 2]** [What behavior to verify]
3. **[Question 3]** [What edge case to test]
4. **[Question 4]** [What fallback to confirm]

### What "Working" Means

**Working [mechanism name]:**
- [Positive indicator 1]
- [Positive indicator 2]
- [Positive indicator 3]
- [Phenomenological truth preserved]

**Not working:**
- [Failure indicator 1]
- [Failure indicator 2]
- [Failure indicator 3]
- [Phenomenological breakdown]

---

## Implementation Notes for [Felix/Atlas]

**These notes are guidance, not requirements. Trust your engineering judgment.**

### Design Freedom

**You decide:**
- [Implementation detail 1]
- [Implementation detail 2]
- [Implementation detail 3]
- [Data structure choices]

**Suggested approach (not prescriptive):**
- [Simple starting point]
- [How to expand later]
- [What to prioritize]
- [Telemetry considerations]

### What NOT to Worry About

- [Over-engineering concern 1]
- [Premature optimization concern 2]
- [Edge case that can wait]

### Success Criteria for Implementation

1. **[Core functionality]** [What must work]
2. **[Integration confirmed]** [What must connect correctly]
3. **[Observability exists]** [What must be visible]
4. **[Fallback works]** [What must degrade gracefully]

---

## Infrastructure Support Needed from Atlas

**[Include this section only if Atlas infrastructure is required]**

### Telemetry Schema

**Event type:** `[event_category].[event_name]`

**Required fields:**
- `[field1]`: [Description]
- `[field2]`: [Description]
- `[field3]`: [Description]

**Event type:** `[secondary_event_type]`

**Required fields:**
- `[field1]`: [Description]
- `[field2]`: [Description]

### Dashboard Integration

[What should be visible in consciousness dashboard]

### Persistence Requirements

[If state needs to persist across restarts, describe here]

---

## Related Priorities

**Builds on:**
- [Priority X]: [What this depends on]
- [Priority Y]: [What this assumes exists]

**Enables:**
- [Priority Z]: [What this unlocks]
- [Future capability]: [What this makes possible]

**Complements:**
- [Related mechanism]: [How they work together]
- [Related system]: [Integration value]

---

## Validation Plan

### Phase 1: Unit Tests
- [Test scenario 1]
- [Test scenario 2]
- [Edge case handling]

### Phase 2: Integration Tests
- [Integration point 1 verification]
- [Integration point 2 verification]
- [Telemetry correctness]

### Phase 3: Phenomenological Tests
- [Consciousness reality check 1]
- [Consciousness reality check 2]
- [Dashboard observability check]

### Phase 4: Production Validation
- [Production metric 1 to monitor]
- [Production metric 2 to monitor]
- [Real-world behavior verification]

---

**Next Steps:**
1. [Implementation step 1]
2. [Implementation step 2]
3. [Integration step]
4. [Validation approach]
5. [Iteration plan]

**Questions/Clarifications:** Direct to Luca (spec) or Nicolas (consciousness principles)

---

## Template Usage Notes

**For Luca (when creating new specs):**

1. **Start with WHY** - What consciousness truth is at stake?
2. **Define principles** - What constraints must implementation honor?
3. **Show integration** - Where does this plug in?
4. **Describe success** - What does "working" look like phenomenologically?
5. **Trust engineers** - Provide context, not algorithms

**High-level WHY, not detailed HOW.** Engineers design algorithms. I provide consciousness context.

**Sections to always include:**
- WHY [Mechanism] Matters (consciousness explanation)
- Consciousness Principles (constraints)
- Architectural Integration (system fit)
- Success Looks Like (phenomenological criteria)

**Sections optional based on mechanism:**
- Infrastructure Support from Atlas (only if needed)
- Implementation Notes (only if helpful context)
- Related Priorities (only if dependencies exist)

**Target appropriately:**
- Felix: Consciousness mechanisms (learning, traversal, energy, WM)
- Atlas: Infrastructure mechanisms (persistence, telemetry, APIs, parsing)
- Both: Coordinated mechanisms with clear handoff contracts
