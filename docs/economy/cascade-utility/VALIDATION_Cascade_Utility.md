# VALIDATION: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Validation rules and invariants            |

## Validation Rules

### V1: Ledger-Physics Orthogonality [CRITICAL]

The $MIND ledger must never influence energy behavior inside the graph.

```
MUST:    $MIND controls only Delta_E_allowed (the clamping gate)
         Once energy enters the graph, propagation follows physics only
         Two stimuli with identical properties propagate identically
         regardless of how much $MIND the sender holds

NEVER:   Rich actors get different physics treatment
         $MIND balance influences propagation speed, priority, or reach
         Payment tier creates quality-of-service differentiation inside the graph

TEST:    Inject two identical stimuli from actors with 1x and 1000x $MIND balance
         Verify identical propagation paths, timing, and cascade depth
         Any divergence = orthogonality violation
```

@mind:TODO Implement the orthogonality test as an automated invariant check in CI.

### V2: Anti-Sybil Resistance [CRITICAL]

The cost of faking topology must always exceed the reward from fake identities.

```
MUST:    Topological proof-of-work requires 50-250 coherent nodes per concept
         Nodes must span multiple independent organizations
         Graph must have depth >= MIN_CASCADE_DEPTH (not flat)
         Diversity score must exceed DIVERSITY_THRESHOLD

NEVER:   Flat or shallow graphs accepted as proof of value
         Single-organization clusters count as diverse
         Inactive nodes count toward the coherent node total

TEST:    Simulate a Sybil attack with N fake identities
         Compute the cost of constructing a valid topology proof
         Verify cost > maximum possible reward from the fake topology
         At every tested scale (10, 100, 1000, 10000 identities), cost must exceed reward
```

@mind:TODO Define the cost model for Sybil simulation. Include compute, time, and coordination costs.

### V3: Anti-Cherry-Picking [HIGH]

The propensity-weighted advantage must make hard tasks more rewarding than easy tasks.

```
MUST:    advantage(hard_task_success) > advantage(easy_task_success)
         For baseline 0.3: advantage = 0.7
         For baseline 0.9: advantage = 0.1
         Ratio of rewards reflects ratio of difficulty

NEVER:   System optimizes for easy-task completion rates
         Aggregate metrics (total tasks completed) used as success measure
         Actors who only do easy tasks accumulate rewards faster than hard-task solvers

TEST:    Simulate two actors over 100 tasks:
           Actor A: completes only easy tasks (baseline 0.9), 95% success rate
           Actor B: completes only hard tasks (baseline 0.3), 40% success rate
         Verify: Actor B's cumulative advantage > Actor A's cumulative advantage
           Actor A: 95 * 0.1 = 9.5
           Actor B: 40 * 0.7 = 28.0
         Actor B earns ~3x more despite lower success rate
```

### V4: Price Stability Under Load [HIGH]

The f_scarcity factor must adjust smoothly and remain bounded.

```
MUST:    f_scarcity range is [1.0, 8.0] -- never below 1.0, never above 8.0
         Transitions between load states are smooth (sigmoid, no steps)
         Price at minimum load = base cost (f_scarcity = 1.0)
         Price at maximum load = 8x base cost (f_scarcity = 8.0)

NEVER:   Price spikes exceed 8x during transient load
         Price oscillates rapidly between high and low values
         Price drops below base cost (f_scarcity < 1.0)

TEST:    Simulate a load spike from 0% to 100% in 1 second
         Verify f_scarcity transitions smoothly (no discontinuity > 0.5 per tick)
         Simulate load oscillation (50%->100%->50% in 10 seconds)
         Verify no price oscillation amplification
```

@mind:TODO Define the maximum acceptable rate of change for f_scarcity (d(f_scarcity)/dt limit).

### V5: Cascade Chain Limits [MEDIUM]

Energy cascades must be bounded to prevent runaway amplification.

```
MUST:    Maximum 5 consecutive energy cascades before a stabilization pause
         Stabilization pause allows the system to re-evaluate load indicators
         After pause, cascading may resume if conditions permit

NEVER:   Unbounded cascade chains
         Cascade depth exceeds 5 without a stabilization checkpoint
         A single stimulus triggers more than 5^N downstream effects (exponential blowup)

TEST:    Inject a stimulus designed to maximize cascade depth
         Verify the system enforces the 5-cascade limit
         Verify the stabilization pause occurs
         Verify system remains responsive during the pause
```

@mind:TODO Determine if the cascade limit of 5 is optimal. Run sensitivity analysis with limits of 3, 5, 7, 10.

### V6: Reserve-and-Settle Accuracy [MEDIUM]

The cost prediction must converge toward accuracy over time.

```
MUST:    Predicted cost (f_cost) and actual cost converge
         Mean absolute error of predictions decreases over time
         Overpayment is refunded promptly (within one settlement cycle)
         Underpayment is collected without penalty (first N occurrences)

NEVER:   Systematic over- or under-prediction bias
         Settlement delay exceeds one cycle
         Users punished for prediction errors by the system

TEST:    Over 1000 requests, compute mean prediction error
         Verify error is < 20% of actual cost after initial learning period
         Verify zero systematic bias (mean signed error ~ 0)
```

@mind:TODO Define the settlement cycle duration. Candidate: per-request immediate settlement.

### V7: Append-Only Integrity [HIGH]

The `.cascade` root must never lose data.

```
MUST:    All contributions, usage events, and cascade propagations are recorded
         Failures are recorded alongside successes
         No mechanism exists to delete, edit, or overwrite historical records
         Full history is available for pricing and trust computation

NEVER:   Records deleted or modified after creation
         Reputation laundering via history reset
         Partial histories used for trust computation

TEST:    Attempt to delete a record via every available API
         Verify all attempts fail or are logged as violations
         Verify that trust computations use the complete history
```

@mind:TODO Design the append-only storage backend. Candidates: append-only log, Merkle tree, content-addressed store.

## Invariant Summary

| ID  | Rule                          | Priority | Automated | Status      |
|-----|-------------------------------|----------|-----------|-------------|
| V1  | Ledger-Physics Orthogonality  | CRITICAL | No        | @mind:TODO  |
| V2  | Anti-Sybil Resistance         | CRITICAL | No        | @mind:TODO  |
| V3  | Anti-Cherry-Picking           | HIGH     | No        | @mind:TODO  |
| V4  | Price Stability Under Load    | HIGH     | No        | @mind:TODO  |
| V5  | Cascade Chain Limits          | MEDIUM   | No        | @mind:TODO  |
| V6  | Reserve-and-Settle Accuracy   | MEDIUM   | No        | @mind:TODO  |
| V7  | Append-Only Integrity         | HIGH     | No        | @mind:TODO  |
