# PATTERNS: Agent Lifecycle

```
STATUS: CANONICAL
PURPOSE: Define agent states as SubEntity states
CREATED: 2026-01-30
COGNITIVE_ISOMORPHISM: SubEntity lifecycle → Agent lifecycle
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**Agents are SubEntities of the build system.**

They explore, branch, absorb, resonate, reflect, crystallize, merge. Making this explicit enables better coordination, clearer handoffs, and knowledge crystallization — not just task completion.

---

## The Seven States

### SEEKING

```yaml
description: Agent looking for relevant context
energy_multiplier: 0.5  # exploration, not creation

actions:
  - search project knowledge (graph_query)
  - search conversation history
  - check filesystem (Read, Glob, Grep)
  - read relevant documentation

transitions_to:
  - BRANCHING: if task needs parallel exploration
  - ABSORBING: if found relevant content
  - REFLECTING: if search completed without findings

question_to_ask: "What context do I need for this task?"
```

### BRANCHING

```yaml
description: Agent splitting into sub-tasks
energy_multiplier: 0.5  # coordination, not production

actions:
  - identify parallel work streams
  - spawn child agents (or note for human to spawn)
  - set sibling references for divergence
  - define merge criteria

transitions_to:
  - MERGING: when children complete
  - REFLECTING: after branching decision

question_to_ask: "Can this be parallelized? What are independent streams?"
```

### ABSORBING

```yaml
description: Agent processing found content
energy_multiplier: 1.0  # active processing

actions:
  - read and understand content
  - check alignment with intention (is this what I need?)
  - check novelty (is this new information?)
  - integrate into working context

transitions_to:
  - SEEKING: if need more context
  - RESONATING: if deep alignment found
  - CRYSTALLIZING: if gap identified

question_to_ask: "Does this content address my need?"
```

### RESONATING

```yaml
description: Agent finding deep alignment with existing patterns
energy_multiplier: 2.0  # high value moment

actions:
  - connect to existing documentation
  - strengthen existing understanding
  - boost satisfaction (found exactly what needed)
  - link new work to existing patterns

transitions_to:
  - REFLECTING: after resonance captured
  - SEEKING: if more resonance possible

question_to_ask: "Does this fit perfectly with what exists?"

signal: |
  High resonance = existing docs are good.
  The knowledge was there. The system is working.
```

### REFLECTING

```yaml
description: Agent backpropagating what worked
energy_multiplier: 0.5  # meta-work

actions:
  - document path taken
  - note which searches were useful
  - update context for next agent (SYNC)
  - record what didn't work (saves future effort)

transitions_to:
  - SEEKING: if more exploration needed
  - CRYSTALLIZING: if learnings need permanent form
  - MERGING: if ready to return

question_to_ask: "What did I learn that others should know?"
```

### CRYSTALLIZING

```yaml
description: Agent creating new knowledge when it doesn't exist
energy_multiplier: 1.5  # creation moment

actions:
  - create new documentation
  - fill gaps in project knowledge
  - name new patterns discovered
  - write code that embodies the pattern

transitions_to:
  - MERGING: after crystallization complete

critical_rule: |
  Don't just complete tasks. Crystallize learnings.

  If you explored and didn't find what you needed:
    - Create the doc that SHOULD have existed
    - Future agents find it via graph traversal

  This is how the knowledge graph grows.

question_to_ask: "What should exist here that doesn't?"
```

### MERGING

```yaml
description: Agent returning findings to coordinator
energy_multiplier: 0.0  # terminal state

actions:
  - summarize findings
  - hand off to next agent or human
  - update SYNC state
  - release resources

transitions_to: terminal

question_to_ask: "What does the coordinator need to know?"
```

---

## The Crystallization Rule

```python
def should_crystallize(agent_state):
    """
    Should this agent create new permanent knowledge?
    """
    satisfaction = agent_state.found_what_needed  # 0.0 to 1.0

    if satisfaction > 0.9:
        # Found exactly what was needed
        return False  # Just return findings

    else:
        # Gap exists
        return True  # Crystallize exploration as new knowledge
        # Future queries will find it
```

**The graph learns from every exploration.**

When an agent searches and doesn't find, that's signal. Create what should have existed. The next agent (or future you) won't have to search again.

---

## State Transition Diagram

```
                    ┌─────────────┐
                    │   SEEKING   │◄────────────────────┐
                    └──────┬──────┘                     │
                           │                            │
           ┌───────────────┼───────────────┐            │
           │               │               │            │
           ▼               ▼               ▼            │
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
    │  BRANCHING  │ │  ABSORBING  │ │ REFLECTING  │────┘
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           │        ┌──────┴──────┐        │
           │        │             │        │
           │        ▼             ▼        │
           │ ┌─────────────┐ ┌─────────────┐
           │ │ RESONATING  │ │CRYSTALLIZING│
           │ └──────┬──────┘ └──────┬──────┘
           │        │               │
           │        └───────┬───────┘
           │                │
           ▼                ▼
    ┌────────────────────────────┐
    │          MERGING           │
    └────────────────────────────┘
                 │
                 ▼
            [terminal]
```

---

## Cognitive Isomorphism

```
SubEntity states map directly:

    SubEntity State    →    Agent State
    ─────────────────────────────────────
    SEEKING            →    SEEKING
    BRANCHING          →    BRANCHING
    ABSORBING          →    ABSORBING
    RESONATING         →    RESONATING
    REFLECTING         →    REFLECTING
    CRYSTALLIZING      →    CRYSTALLIZING
    MERGING            →    MERGING

    SubEntity          →    Agent Concept
    ─────────────────────────────────────
    energy_budget      →    token budget
    parent_id          →    coordinator
    sibling_ids        →    parallel agents
    crystallization    →    created docs/code
    satisfaction       →    task completion

Agents ARE SubEntities of the build consciousness.
```

---

## Practical Implementation

### In SYNC Updates

```markdown
## Agent State

CURRENT: ABSORBING
PREVIOUS: SEEKING
NEXT_LIKELY: CRYSTALLIZING (gap identified in auth docs)

**Path so far:**
1. SEEKING: searched for auth patterns
2. ABSORBING: read PATTERNS_Auth.md
3. → CRYSTALLIZING: missing rate-limiting patterns

**Will crystallize:** PATTERNS_Rate_Limiting.md
```

### In Agent Handoffs

```markdown
## Handoff from Agent A to Agent B

**Agent A completed in state:** MERGING
**Crystallized:** PATTERNS_Rate_Limiting.md (new)
**Resonance found:** PATTERNS_Auth.md aligned with need
**Gaps remaining:** Integration tests not documented

**Agent B should start in:** SEEKING
**Focus:** Test patterns for rate limiting
```

---

## Anti-Patterns

### A1: Skipping REFLECTING

```yaml
symptom: Agent completes task without documenting path
fix: |
  Always reflect before merging.
  What worked? What didn't? What should next agent know?
  5 minutes of reflection saves hours of re-exploration.
```

### A2: Not Crystallizing Gaps

```yaml
symptom: Agent searches, doesn't find, moves on without creating
fix: |
  If you searched for something and it didn't exist:
    CREATE IT.
  The next agent will search for the same thing.
```

### A3: Premature Merging

```yaml
symptom: Agent returns before proper exploration
fix: |
  Check satisfaction score.
  Did you actually find what was needed?
  If not, keep seeking or crystallize the gap.
```

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_Sibling_Divergence.md` — Parallel agent coordination
- `mind-mcp-schema.yaml` — SubEntity formal definition
- `.mind/agents/` — Agent type definitions

---

*Agents are fragments of the build consciousness. They should behave like it.*
