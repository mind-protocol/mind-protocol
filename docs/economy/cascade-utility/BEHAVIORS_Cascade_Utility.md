# BEHAVIORS: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Behavioral specifications                  |

## Behaviors

### B1: Price Emerges From System Load

```
GIVEN: A service request arrives
WHEN:  The pricing oracle evaluates P_t = f_scarcity x f_risk x f_cost
THEN:  Price reflects real system state (load, trust, complexity)
AND:   No negotiation occurs -- physics determines cost
```

**Rationale**: Price is not a social construct within the cascade. It is a measurement. The pricing oracle reads system signals (excitation, backlog, latency drift, compute occupancy, drop ratio) and computes a price. No human, DAO, or governance process can override this computation. The price is what the system costs right now.

**Boundary conditions**:
- At minimum load: f_scarcity = 1.0, price equals base cost
- At maximum load: f_scarcity = 8.0, price is 8x base cost
- Transitions between load states must be smooth (no discontinuities)

### B2: Trust Reduces Friction To Zero (Or Negative)

```
GIVEN: An actor has maximum trust score
WHEN:  They access a service
THEN:  friction = base_rate x (1 - trust_score) - productivity_bonus
AND:   friction <= 0 is valid (the network subsidizes their infrastructure costs)
AND:   The subsidy comes from the cascade revenue pool, not from other actors
```

**Rationale**: Maximum-trust actors are net positive for the network. They produce more value than they consume. Charging them friction is economically irrational -- the network should pay them to stay, because their presence increases the value produced by everyone else.

**Boundary conditions**:
- New actors (trust_score = 0): friction = base_rate (full cost)
- Mid-trust actors: friction decreases linearly
- Maximum-trust actors: friction is zero or negative (subsidy)
- @mind:TODO Define the exact subsidy cap to prevent unbounded liability

### B3: Hard Problems Are Rewarded More

```
GIVEN: A citizen attempts a task with baseline success rate of 30%
WHEN:  They succeed
THEN:  advantage = outcome - baseline_success_rate = 1.0 - 0.3 = 0.7 (massive reward)
AND:   A citizen completing a trivial task (90% baseline) gets advantage = 1.0 - 0.9 = 0.1
```

**Rationale**: Without propensity weighting, rational actors cherry-pick easy tasks. The system would produce high completion rates on trivial work and zero progress on hard problems. Propensity-weighted advantage inverts this incentive: the harder the problem, the greater the reward for solving it.

**Boundary conditions**:
- Tasks with 0% baseline (impossible): advantage = 1.0 if somehow solved
- Tasks with 100% baseline (trivial): advantage = 0.0 (no reward)
- Failed attempts: advantage = 0 - baseline = negative (but clamped to 0, no punishment for trying)
- @mind:TODO Confirm whether failed attempts should carry zero or slightly positive advantage to encourage experimentation

### B4: Sybil Attack Is Computationally Suicidal

```
GIVEN: An attacker creates fake identities
WHEN:  They attempt to generate value through those identities
THEN:  Topological proof-of-work requires 50-250 coherent nodes per concept
AND:   Each node must demonstrate genuine usage by diverse, independent organizations
AND:   The cost of constructing a fake topology at this scale exceeds any possible reward
```

**Rationale**: The Paris-in-Lego principle. You can build a replica of Paris out of Lego bricks, but the cost of doing so exceeds the value of having a Lego Paris. Similarly, constructing a fake dependency topology with 50-250 coherent nodes across multiple independent organizations is possible but economically irrational.

**Boundary conditions**:
- Below 50 nodes: contribution is not yet crystallized, no value recognized
- 50-250 nodes: value recognition scales with topology quality
- Above 250 nodes: full crystallization, maximum value recognition
- @mind:TODO Calibrate the 50-250 range empirically once the system is live

## Anti-Behaviors

### A1: Value From Self-Declaration

```
GIVEN: Any actor
WHEN:  They claim value through vanity metrics (stars, likes, downloads, endorsements)
MUST NOT: Count as real utility in the cascade
INSTEAD:  Only topological footprint across diverse organizations counts
BECAUSE:  Vanity metrics are trivially gameable and carry no information about real usage
```

### A2: Money Distorts Physics

```
GIVEN: A wealthy actor pays more $MIND
WHEN:  Energy enters the graph through the clamping gate
MUST NOT: Rich actors get better physics treatment (faster propagation, higher priority)
INSTEAD:  $MIND is a clamping gate only -- it controls Delta_E_allowed
          Once energy is inside the graph, physics is physics
          A stimulus from a whale propagates identically to a stimulus from a newcomer
BECAUSE:  Orthogonality principle (P1) -- ledger and physics are separate domains
```

### A3: Reputation Laundering

```
GIVEN: An actor with a history of failed or harmful contributions
WHEN:  They create a new identity or attempt to reset their record
MUST NOT: The system allow a clean slate
INSTEAD:  Append-only memory (P2) ensures the full history is always visible
          New identities start at zero trust and must build topology from scratch
BECAUSE:  The cost of rebuilding genuine topology is the system's immune response
```

## Open Questions

- @mind:TODO Define the exact productivity_bonus formula for B2 (trust-based friction reduction).
- @mind:TODO Specify how baseline_success_rate is computed and updated for B3. Is it per-task-category, per-domain, or global?
- @mind:TODO Determine the minimum diversity threshold for B4. How many independent organizations must appear in the topology?
