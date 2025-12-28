# BEHAVIORS: Membrane System

```
STATUS: V1 SPEC
PURPOSE: Observable effects of structured graph dialogues
```

---

## Doctor Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-DOC-1 | Doctor detects gap | Missing spec/coverage triggers skill load | G6 (dependency aware) |
| B-DOC-2 | Doctor queries graph | Calls graph API before deciding which protocol | G4 (context-rich) |
| B-DOC-3 | Doctor loads skill | Skill markdown loaded into agent context | G3 (workflow guided) |
| B-DOC-4 | Doctor selects protocol | Skill guides which protocol to run | G3 (workflow guided) |

---

## Skill Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-SKILL-1 | Skill provides domain knowledge | Agent understands context before answering | G4 (context-rich) |
| B-SKILL-2 | Skill maps situations to protocols | Clear guidance on which protocol when | G3 (workflow guided) |
| B-SKILL-3 | Skill shows patterns/anti-patterns | Agent avoids common mistakes | G5 (traceable) |
| B-SKILL-4 | Skill suggests queries | Agent knows what to look for | G4 (context-rich) |

---

## Protocol Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-PROT-1 | Protocol asks questions | Each `ask` step prompts agent | G2 (use-case oriented) |
| B-PROT-2 | Protocol queries graph | Each `query` step loads context | G4 (context-rich) |
| B-PROT-3 | Protocol branches | `branch` step routes based on condition | G6 (dependency aware) |
| B-PROT-4 | Protocol calls protocol | `call_protocol` step invokes sub-protocol | G6 (dependency aware) |
| B-PROT-5 | Protocol creates cluster | `create` step produces nodes + links | G1 (dense clusters) |

---

## Membrane Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-MEM-1 | Membrane loads protocol | YAML protocol loaded and parsed | G3 (workflow guided) |
| B-MEM-2 | Membrane validates input | Invalid input rejected with reason | G5 (traceable) |
| B-MEM-3 | Membrane allows enrichment | Agent can query graph mid-step | G4 (context-rich) |
| B-MEM-4 | Membrane manages call stack | Sub-protocols execute and return | G6 (dependency aware) |
| B-MEM-5 | Membrane commits cluster | All nodes/links created atomically | G1 (dense clusters) |
| B-MEM-6 | Membrane records moments | Every step creates moment with prose | G5 (traceable) |
| B-MEM-7 | Membrane reports summary | Completion returns structured output | G2 (use-case oriented) |

---

## Graph Output Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-GRAPH-1 | Cluster creation | Multiple nodes created in single operation | G1 (dense clusters) |
| B-GRAPH-2 | Cross-linking | Nodes linked to each other, not just container | G1 (dense clusters) |
| B-GRAPH-3 | Strength from answers | Link strength derived from agent input | G4 (context-rich) |
| B-GRAPH-4 | Moment trail | Every operation leaves moment with prose | G5 (traceable) |

---

## Session Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-SESS-1 | Session tracking | Session ID maintained across steps | G5 (traceable) |
| B-SESS-2 | Step sequencing | Steps execute in defined order | G3 (workflow guided) |
| B-SESS-3 | Context preservation | Earlier answers available in later steps | G4 (context-rich) |
| B-SESS-4 | Abort handling | Session can be aborted, no partial commits | G5 (traceable) |

---

## Error Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-ERR-1 | Validation failure | Clear error message, step repeats | G5 (traceable) |
| B-ERR-2 | Spawn depth exceeded | Membrane fails with depth error | G6 (dependency aware) |
| B-ERR-3 | Query failure | Graph error surfaces to agent | G4 (context-rich) |
| B-ERR-4 | Session timeout | Stale session cleaned up | G5 (traceable) |

---

## Behavior Matrix: Membrane × Output

| Membrane | Nodes Created | Links Created | Moments |
|----------|---------------|---------------|---------|
| explore_space | 1 (exploration) | 2 (expresses, about) | 1 |
| add_objectives | 1 + N + M | contains × all, supports × N, bounds × M | 1 |
| add_invariant | 2 (validation + moment) | contains, ensures × behaviors | 1 |
| add_health_coverage | 4 (health + 2 docks + moment) | contains × 3, attached_to × 2, verifies × validations | 1 |
| record_work | 1 + N + M (progress + escalations + goals) | expresses, about × affected + new nodes | 1 |
| investigate | 1-2 (investigation + optional) | expresses, about | 1 |
| resolve_blocker | 2 (rationale + resolution) | about × (escalation + affected), expresses | 1 |

---

## CHAIN

- **Prev:** PATTERNS_Membrane_System.md
- **Next:** ALGORITHM_Membrane_System.md
- **Validates:** VALIDATION_Membrane_System.md
