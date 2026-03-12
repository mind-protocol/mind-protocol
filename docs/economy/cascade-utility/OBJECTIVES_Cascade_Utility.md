# OBJECTIVES: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Objectives & constraints                   |

## Primary Objectives (Ranked)

### O1: Make Cooperation Structurally More Profitable Than Extraction

The system must be designed so that an actor maximizing their own reward will naturally cooperate rather than extract. This is not a moral constraint -- it is an economic one. The pricing formula, the propensity-weighted advantage, and the topological proof-of-work all converge to make genuine contribution the lowest-cost strategy.

### O2: Prevent Cherry-Picking of Easy Tasks

Actors must not be able to optimize their reward by selecting only trivial tasks. The propensity-weighted advantage formula ensures that completing a task with a 30% baseline success rate yields an advantage of 0.7, while completing a task with a 90% baseline yields only 0.1. The system rewards difficulty, not volume.

### O3: Resist Sybil Attacks Through Topological Proof-of-Work

Fake identities must be computationally suicidal to maintain. The topological proof-of-work requires 50-250 coherent nodes per concept to crystallize value. Constructing a fake topology of that scale and diversity costs more than the reward it could produce.

### O4: Dynamic Pricing Responsive to Real System Load

Prices must reflect the actual state of the system -- load, trust, complexity -- not speculation or negotiation. The pricing oracle computes price from measurable signals. No human sets prices. No market makes them. Physics determines cost.

## Non-Objectives

These are explicitly out of scope for cascade-utility:

| Non-Objective              | Rationale                                                        |
|----------------------------|------------------------------------------------------------------|
| Market-making              | The cascade is not a trading venue. Price emerges from physics.  |
| Speculation enablement     | $MIND is a clamping gate, not a speculative asset within the graph. |
| Manual price setting       | No administrator, DAO vote, or governance action sets prices.    |

## Tradeoffs

| When...                                          | Choose...       | Accept...                                      |
|--------------------------------------------------|-----------------|-------------------------------------------------|
| Simplicity conflicts with anti-gaming            | Anti-gaming     | Additional system complexity                    |
| Throughput conflicts with verification            | Verification    | Higher latency for value recognition            |
| User experience conflicts with Sybil resistance  | Sybil resistance| Longer onboarding for new actors                |

The guiding principle: accept complexity to preserve integrity. A simple system that can be gamed is worse than a complex system that cannot.

## Success Signals

| Signal                                                  | Target                                    |
|---------------------------------------------------------|-------------------------------------------|
| Sybil attacks successful at scale                       | Zero                                      |
| Friction for maximum-trust actors                       | Approaching zero (or negative with subsidy)|
| Price stability during transient load spikes            | Within 1.0x-8.0x range, smooth curve      |
| Cherry-picking ratio (easy/hard task completion)        | Converging toward natural task distribution|
| Time from contribution to value recognition             | Monotonically decreasing as trust builds   |

## Open Questions

- @mind:TODO Define quantitative thresholds for each success signal. What exact cherry-picking ratio is acceptable?
- @mind:TODO Determine how objective priorities should shift as the system matures (early network vs. established network).
