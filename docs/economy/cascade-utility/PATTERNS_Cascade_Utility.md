# PATTERNS: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Architectural patterns                     |

## Chain

| Document                          | Purpose                                  |
|-----------------------------------|------------------------------------------|
| CONCEPT_Cascade_Utility.md        | Core concept and relationships           |
| OBJECTIVES_Cascade_Utility.md     | Ranked objectives and tradeoffs          |
| PATTERNS_Cascade_Utility.md       | This file -- patterns and principles     |
| BEHAVIORS_Cascade_Utility.md      | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Cascade_Utility.md      | Algorithms and data structures           |
| VALIDATION_Cascade_Utility.md     | Validation rules and invariants          |
| IMPLEMENTATION_Cascade_Utility.md | Implementation status and code mapping   |
| HEALTH_Cascade_Utility.md         | Runtime health indicators                |
| SYNC_Cascade_Utility.md           | Sync status and handoff notes            |

## The Problem

Traditional value measurement relies on vanity metrics: stars, likes, downloads, citation counts. These metrics share a fatal flaw -- they measure declaration, not usage. Semantic generation is cheap. A single script can inflate any declaration-based metric to arbitrary levels.

The deeper problem is that as AI makes content generation nearly free, the cost of producing fake value signals approaches zero while the cost of producing genuine value remains non-trivial. Any system that measures value by what actors say (or click) rather than what the dependency graph shows will be overwhelmed by noise.

How do you prove real value in a world where generating fake signals is free?

## The Pattern: Topological Proof-of-Work

Value is measured by the shape of the dependency graph across diverse organizations.

A pull request merged into a project has zero value until that project is actively used by diverse organizations that themselves generate provable value. The value of a contribution is not what it claims to be -- it is the downstream topology it generates.

This is topological proof-of-work: the "work" is not computational hashing but the construction of a genuine, diverse, deep dependency graph. Faking this topology requires creating real organizations with real usage patterns across multiple independent actors -- a cost that exceeds any reward the fake topology could generate.

```
Contribution --> Merge --> Usage by Org A --> Usage by Org B --> ... --> Value
                                |                    |
                                v                    v
                          (Org A produces      (Org B produces
                           its own value)       its own value)
```

The graph must be:
- **Deep**: cascade chains, not flat single-hop references
- **Diverse**: multiple independent organizations, not self-referential loops
- **Active**: ongoing usage, not one-time imports

## Principles

### P1: Orthogonality

The $MIND ledger is strictly orthogonal to graph physics.

$MIND controls `Delta_E_allowed` -- the clamping gate that determines how much energy an actor can inject into the system. Once energy is inside the graph, it follows physics only. No amount of $MIND changes the laws of propagation, decay, or cascade behavior.

This means: a wealthy actor can inject more stimuli, but cannot make those stimuli propagate better. Propagation quality is determined by topological fitness, not by payment.

### P2: Append-Only Memory

The `.cascade` root never erases -- neither successes nor failures.

Every contribution, every usage event, every cascade propagation is recorded permanently. Failures are as informative as successes. An actor's full history is always visible to the system, preventing reputation laundering.

This is not a blockchain requirement -- it is an integrity requirement. The system must remember everything to price accurately.

### P3: Anti-Cherry-Picking

Propensity-weighted advantage rewards solving hard problems, not picking easy ones.

The advantage formula `advantage = outcome - baseline_success_rate` ensures that the system's reward distribution favors actors who attempt difficult tasks. An actor who only completes trivial tasks (90% baseline) accumulates advantage slowly (0.1 per success). An actor who tackles hard problems (30% baseline) accumulates advantage rapidly (0.7 per success).

This structurally prevents optimization strategies based on task selection rather than task execution.

## Behaviors Supported

| Behavior                      | Mechanism                                           |
|-------------------------------|-----------------------------------------------------|
| Trust-based friction reduction| f_risk factor decreases with trust, down to 0.6     |
| Anti-Sybil                    | 50-250 node crystallization requirement              |
| Dynamic pricing               | P_t = f_scarcity x f_risk x f_cost, all from signals|

## Behaviors Prevented

| Anti-Behavior                 | Mechanism                                           |
|-------------------------------|-----------------------------------------------------|
| Speculation                   | Price is computed, not traded                        |
| Value inflation               | Topological proof prevents fake value signals        |
| Cherry-picking                | Propensity-weighted advantage penalizes easy tasks   |

## Open Questions

- @mind:TODO Formalize the diversity metric for topological proof. How many independent orgs constitute "diverse enough"?
- @mind:TODO Define the relationship between cascade depth and value weight. Is deeper always better, or is there a diminishing-returns curve?
- @mind:TODO Specify the append-only storage format for the `.cascade` root.
