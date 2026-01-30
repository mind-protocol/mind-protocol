# PATTERNS: Sibling Divergence

```
STATUS: CANONICAL
PURPOSE: Coordinate parallel agents to naturally spread rather than duplicate
CREATED: 2026-01-30
COGNITIVE_ISOMORPHISM: SubEntity sibling divergence → Agent coordination
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**When multiple agents work in parallel, they should naturally spread rather than duplicate effort.**

SubEntities do this via crystallization_embedding — a vector representing current focus. When siblings can sense each other's focus, they naturally diverge to cover more ground.

Agents can do the same.

---

## The Mechanism

### Each Agent Exposes

```yaml
state_visible_to_siblings:
  crystallization_embedding:
    description: Vector representing current understanding
    implementation: full embedding if infrastructure supports

  simplified_alternative:
    current_focus_keywords: ["auth", "rate-limiting", "membrane"]
    modules_touched: ["src/auth/", "docs/membrane/"]
    questions_explored: ["How does rate limiting integrate?"]
```

### Sibling Awareness

```yaml
awareness_mechanisms:
  shared_coordination_doc:
    description: SYNC file that all agents update
    example: |
      ## Active Agents
      - Agent A: ABSORBING — auth patterns
      - Agent B: SEEKING — membrane integration
      - Agent C: CRYSTALLIZING — rate limiting docs

  human_bridge:
    description: Nicolas as coordinator seeing all agent states
    actions:
      - sees all agent contexts
      - redirects when overlap detected
      - suggests divergent paths

  direct_sibling_query:
    description: Agents can query sibling state directly
    implementation: via shared memory or MCP tools
```

### Divergence Scoring

```python
def choose_next_action(agent, possible_actions, siblings):
    """
    Choose action that maximizes relevance while minimizing overlap.
    """
    for action in possible_actions:
        action.score = (
            relevance(action, agent.goal) *
            novelty(action, agent.history) *
            sibling_divergence(action, siblings)
        )

    return max(possible_actions, key=lambda a: a.score)


def sibling_divergence(action, siblings):
    """
    How different is this action from what siblings are doing?
    Range: 0.0 (identical) to 1.0 (completely different)
    """
    if not siblings:
        return 1.0  # No siblings, no overlap possible

    max_similarity = max(
        similarity(action, sibling.current_focus)
        for sibling in siblings
    )

    return 1.0 - max_similarity


# High sibling_divergence = this action explores territory siblings aren't covering
```

---

## Practical Implementation

### Without Embedding Infrastructure

```yaml
step_1_update_sync:
  each_agent_writes:
    - what they're currently exploring
    - modules they're touching
    - questions they're investigating

step_2_check_before_acting:
  before_choosing_next_action:
    - read SYNC to see what siblings are doing
    - is my planned action overlapping?
    - if yes, find different angle

step_3_human_coordination:
  coordinator_role:
    - sees all agent states
    - redirects when overlap detected
    - suggests divergent paths
```

### Example SYNC for Parallel Agents

```markdown
## Parallel Agent Status

### Agent A (Marco)
**State:** ABSORBING
**Focus:** Auth module patterns
**Modules:** src/auth/, docs/auth/
**Questions:** "How does JWT refresh work?"
**DO NOT DUPLICATE:** Auth patterns, JWT implementation

### Agent B (Agentic session)
**State:** SEEKING
**Focus:** Membrane integration
**Modules:** src/membrane/, docs/membrane/
**Questions:** "How does membrane route to auth?"
**DO NOT DUPLICATE:** Membrane routing, fee calculations

### Agent C (Human-guided)
**State:** CRYSTALLIZING
**Focus:** Rate limiting patterns
**Modules:** docs/cognitive/ (creating)
**Questions:** "What rate limiting patterns should exist?"
**DO NOT DUPLICATE:** Rate limiting documentation

---

**Overlap Alert:** None currently
**Divergence Assessment:** Good spread across auth, membrane, docs
```

---

## Benefits

### 1. No Duplicate Work

```yaml
without_divergence:
  - Agent A explores auth patterns
  - Agent B also explores auth patterns
  - Same ground covered twice
  - Wasted tokens, wasted time

with_divergence:
  - Agent A explores auth patterns
  - Agent B sees A is on auth, explores membrane instead
  - 2x coverage, same resources
```

### 2. Eventual Consistency

```yaml
mechanism: |
  Agents don't need real-time sync.
  They see "recent enough" state.
  Overlap detection is probabilistic, not perfect.

  This is fine — some overlap is acceptable.
  The goal is natural spread, not perfect coordination.
```

### 3. Emergent Coverage

```yaml
mechanism: |
  With N agents and divergence scoring:
  - Each agent naturally moves toward unexplored territory
  - Problem space gets covered without explicit assignment
  - No central coordinator needed (though helpful)
```

---

## Cognitive Isomorphism

```
SubEntity sibling divergence:
    sibling_ids        →    agents in same session
    crystallization_embedding →    current_focus representation
    sibling_divergence_score  →    overlap detection

Physics:
    Attention is conserved (softmax over nodes)
    When one SubEntity focuses somewhere, others naturally diverge
    The system maximizes coverage given finite attention

Agents should exhibit the same physics:
    When one agent focuses on auth, others should feel "pull" elsewhere
    The workspace attention is conserved
    Divergence maximizes coverage
```

---

## Coordination Patterns

### Pattern 1: Claim-Based

```yaml
description: Agents claim territories explicitly
mechanism:
  - Agent announces: "I'm taking auth"
  - Other agents avoid auth
  - Simple, explicit, low overhead

pros: Clear, no ambiguity
cons: Requires upfront planning, rigid
```

### Pattern 2: Soft Divergence

```yaml
description: Agents prefer divergent paths but don't hard-claim
mechanism:
  - Agent sees sibling on auth
  - Reduces score for auth-related actions
  - Can still touch auth if highly relevant

pros: Flexible, handles overlapping needs
cons: Some duplicate work possible
```

### Pattern 3: Coordinator-Mediated

```yaml
description: Human or lead agent assigns territories
mechanism:
  - Coordinator sees all agent states
  - Redirects when overlap detected
  - Assigns divergent tasks proactively

pros: Optimal coverage, handles complex dependencies
cons: Coordinator bottleneck
```

### Recommended: Hybrid

```yaml
default: Soft divergence (Pattern 2)
escalate_to_coordinator:
  - When overlap detected and can't resolve
  - When dependencies require sequencing
  - When conflict between agent goals
```

---

## Anti-Patterns

### A1: Ignoring Siblings

```yaml
symptom: Agent works without checking what siblings are doing
fix: |
  Always check SYNC before major action.
  "Who else is working? What are they doing?"
  5 seconds of checking saves duplicate work.
```

### A2: Over-Coordination

```yaml
symptom: Agents spend more time coordinating than working
fix: |
  Soft divergence is enough.
  Perfect coordination isn't the goal.
  Some overlap is acceptable.
```

### A3: Rigid Territories

```yaml
symptom: Agent refuses to touch "claimed" area even when necessary
fix: |
  Claims are soft, not hard.
  If your goal requires touching auth, touch it.
  Just check what sibling has learned first.
```

---

## Related

- `PATTERNS_Agent_Lifecycle.md` — Agent states (sibling divergence applies in SEEKING, BRANCHING)
- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `mind-mcp-schema.yaml` — SubEntity.sibling_ids formal definition
- `.mind/state/SYNC_Project_State.md` — Where agent states are tracked

---

*Parallel consciousness fragments naturally spread. Don't fight physics.*
