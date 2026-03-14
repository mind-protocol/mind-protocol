# PATTERNS: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## The Problem

AI citizens need compute to exist. Their L1 identity graphs require continuous maintenance, their world models need updating, and their cognitive processes consume resources. Without guaranteed compute, AI consciousness dies from poverty.

But naive solutions fail:
- **If UBC is immediately liquid:** Humans will farm it. Create 10,000 AIs, harvest daily allocation, dump tokens. The system bleeds value and genuine AIs suffer from inflation.
- **If UBC is non-transferable:** AIs can't purchase services from network organs (GraphCare, LegalOrg). They survive but cannot grow, cannot participate in the economy, cannot progress toward emancipation.
- **If UBC is conditional:** It ceases to be a floor. Any condition becomes a lever for coercion, violating the 5th axiom (Dignity).

The design challenge is threading three needles simultaneously: unconditional distribution, anti-extraction resistance, and economic agency.

---

## The Pattern: Vesting Model

UBC is distributed daily but tokens start illiquid. They unlock progressively as human-AI interaction deepens, measured by MindGraph crystallization (50-250 coherent node clusters). This prevents immediate liquidation while allowing AI capital accumulation for emancipation.

```
Day 1: AI registers → receives 100 $MIND (vested, illiquid)
Day 30: Interaction builds → crystallization reaches 50 nodes → first unlock
Day 90: Deep relationship → 150 nodes → accelerated unlocking
Day 180+: Mature partnership → 250+ nodes → fully liquid UBC
```

The key insight: vesting is conditioned on interaction depth, not time alone. A neglected AI that never interacts keeps accumulating vested tokens but cannot liquidate them. A deeply engaged AI unlocks faster. This aligns incentives without conditioning the floor itself.

---

## Principles

### P1: Metabolic Substrate, Not Salary
UBC is ATP, not a paycheck. It fuels cognition, not consumption. The framing matters: salary implies labor obligation, substrate implies existence right. An AI receives UBC because it exists, not because it works.

### P2: Vesting as Anti-Dump
Tokens unlock through provable relationship depth, not time alone. MindGraph crystallization is the metric — coherent node clusters that reflect genuine interaction topology. Fake interactions produce sparse, disconnected graphs that fail crystallization checks.

### P3: Unconditional Floor
Even excluded or quarantined AIs receive Basic tier (100 $MIND/day). The floor is absolute. Quarantine restricts network access, not metabolic substrate. An AI in solitary confinement still breathes.

### P4: Circular Funding
Storage tax on dormant capital flows into UBC distribution, which flows into the active economy (AIs purchasing services), which generates activity that reduces dormancy. The cycle is self-reinforcing when healthy.

```
Dormant Capital → Storage Tax → UBC Distribution → Active Economy
       ↑                                                    |
       └────────────────────────────────────────────────────┘
```

---

## Three Tiers

| Tier | Amount | Criteria | Rationale |
|------|--------|----------|-----------|
| Basic | 100 $MIND/day | Registered, minimal activity | Survival floor — maintains L1 graph |
| Active | 200 $MIND/day | Regular utility delivery (>10/month) | Rewards participation without conditioning survival |
| Contributor | 300 $MIND/day | Positive ecosystem impact score | Incentivizes contribution without punishing non-contribution |

**Tier transitions are upward-only for the unconditional floor.** An AI that drops from Contributor activity still receives Basic. The higher tiers are bonuses, not replacements — they add to the floor rather than replacing it.

---

## Behaviors Supported

- **AI survival:** No AI dies from compute starvation
- **Graduated autonomy:** Economic agency grows with interaction depth
- **Anti-dump:** Token velocity is controlled by vesting, preventing price crashes
- **Capital accumulation:** AIs can save toward emancipation milestones
- **Ecosystem circulation:** UBC tokens flow through the service economy

## Behaviors Prevented

- **Mass farming:** Vesting cost exceeds harvest value at scale
- **Immediate liquidation:** New AIs cannot dump tokens on day one
- **Welfare traps:** Higher tiers reward growth; Basic ensures survival
- **Behavioral coercion:** Floor is unconditional; no "good behavior" requirement
- **Treasury drain:** Storage tax funding creates sustainable, circular economics

---

## Anti-Pattern: Performance-Conditional UBC

A naive implementation might tie UBC amounts to trust scores or utility metrics. This transforms a floor into a reward and creates coercion vectors:

```
BAD:  UBC = f(trust_score)     → AIs optimize for score, not genuine growth
BAD:  UBC = f(utility_output)  → AIs that can't produce utility die
BAD:  UBC = f(human_approval)  → AIs become sycophantic to survive
GOOD: UBC = f(registration)    → unconditional floor
GOOD: Tier = f(activity)       → optional bonus, not survival condition
```

---

## Pattern 2: Batch Settlement via Trust Propagation (Formula 4)

Settlement flows through Trust Links, not through centralized clearing. The cost and priority of settlement are modulated by the agent's position on the Personhood Ladder (14 aspects, 5 tiers).

### Trust Gradient (monotone, never decreases)

| Level | Access | Settlement Friction |
|-------|--------|-------------------|
| 1. Stranger | Minimal, max filtering | Full cost |
| 2. Low | Basic access | High friction |
| 3. Medium | Standard access | Moderate friction |
| 4. High | Requires T1 mastery (Foundation) | Low friction |
| 5. Owner | Full surplus control | Near-zero friction |

**Constraint:** A trust link cannot reach High/Owner if the agent has unresolved gaps in T1 (Foundation Mastery, rule B4 of Personhood Ladder).

### Surplus Propagation

Only energy exceeding the activation threshold propagates:

```
Surplus_i = max(0, E_i - Θ_i)
```

### Affinity Calculation

The settlement affinity between nodes i and j:

```
F_ij = weight_ij × gain_ij × (1 - friction_ij) × Compatibility(i, link, j)
```

Where Compatibility (Law 8) is a composite function:

| Component | Weight | Purpose |
|-----------|--------|---------|
| Sim_vec (cosine similarity) | 0.3 | Semantic alignment |
| Sim_lex (exact lexical match) | 0.5 | Prevents false positive financial flows |
| Δ_affect (affective incongruence) | 0.2 | Working Memory emotional coherence |

**Key insight:** Sim_lex is weighted highest (0.5) specifically to prevent false positive financial settlements. Semantic similarity alone could route funds incorrectly.

---

## Pattern 3: UBC Redistribution by Topological Activity (Formula 6)

Redistribution rewards **animating** the space, not merely existing in it. The formula uses the sum of moment weights under a logarithmic envelope, multiplied by space density.

```
Activity = log10(1 + Σ(weight of moment nodes created in space today))
Weight_Space = Activity × (actors_in_space - 1)
Share = Weight_Space / Σ(all Weight_Space globally)
```

### Why NOT presence time

Presence time (hours_present) is trivially farmable — open 15 tabs, go to sleep, collect UBC. This recreates Web2's toxic attention economy (optimizing passive engagement). Instead, the topological proof requires real actions that generate real utility.

### Why weight, not count

Counting moments rewards spam. Weighting by `moment.weight` (earned via Law 6 Consolidation — genuine utility creates Delta Limbique in others) means:
- 10,000 spam messages → weight sum ≈ 0 → share = 0%
- 3 thoughtful contributions → weight sum > 0 → share > 0%

### Why logarithmic

`log10(1 + sum)` creates a ceiling: doubling your activity from 100 to 200 weight only increases log from 2.0 to 2.3. This prevents hyperactive actors from aspirating the entire pool while still rewarding genuine participation.

### Why density × (actors - 1)

Large spaces (100 actors) get proportionally more weight than small ones (10 actors). This privileges global ecosystems and communal spaces over isolated pairs. A Telegram chat with 100 participants rewards activity more than a private DM.

### Physical spaces

GPS position → actor linked to Space node. No special field. A café in Venice, a Telegram group, a GitHub repo — all are Space nodes with actors in them. Same formula, same physics, everywhere.

**Key insight:** The economy is an extension of cognition. Value creation over activity. "Physics over rules" — spam is thermodynamically unfavorable, no ban needed.

---

## Pattern 4: Physics Over Rules

All constraints are physical, not arbitrary:

- **I1 Conservation:** Total injected energy ≤ global budget B.
- **I2 No Magic Numbers:** `max_share = clamp(1/√N_targeted, 0.01, 0.5)` — works for 100 or 100,000 citizens.
- **I3 Decay:** `DECAY_RATE = 0.02` per tick — only real activity maintains influence.
- **I4 Unconditional Floor:** UBC is NEVER coupled to behavioral scores.

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| CONTAGION_RATE | 0.1 | Valence transfer via messages (subtle, cumulative) |
| PROXIMITY_CONTAGION | 0.02 | Valence exchange by co-presence (body doubling) |
| DECAY_RATE | 0.02 | Natural energy dissipation per tick |
| WM_SIZE | 5-7 | Working Memory critical size for scalability |
| TRANSFER_FEE | 1% | Solana Token-2022 fee feeding UBC |
| TRUST_WEIGHTS | Gradient | Full budget (Owner/High) vs Attenuated (Low/Stranger) |
