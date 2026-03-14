# PATTERNS: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | PATTERNS |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- **PATTERNS_Metabolic_Economy.md** (this file)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md)

---

## Core Thesis: Money as Blood

Traditional economies treat money as a thing to accumulate. Fat. Savings. Reserves. The more you have, the safer you are. The system rewards hoarding because there is no cost to sitting on wealth.

The metabolic economy inverts this. $MIND is blood, not fat.

Blood that stops flowing kills the organism. A clot in a vein is not "savings" -- it is pathology. The heart does not pump harder to compensate for clots; the body dissolves them.

Storage tax is not punishment. It is the metabolic cost of existence. Every cell pays it. Every organ pays it. The protocol treasury pays it. There are no exemptions because exemptions create clots.

---

## Pattern 1: Physics Over Rules

**No moderation. No permission checks. No rule enforcement.**

Every economic behavior in the metabolic system is a consequence of physics, not policy. The structure makes the desired behavior energetically favorable.

| Rule-Based (rejected) | Physics-Based (chosen) |
|------------------------|------------------------|
| "Users must not hide funds" | Off-registry balance tracking makes hiding more expensive than transparency |
| "Rich users should pay more" | Wealth ratio in pricing formula automatically scales cost |
| "Services should get cheaper with use" | Utility weight from graph consolidation exponentially discounts price |
| "Bonds should create shared fate" | Vases communicants auto-transfer closes the gap daily |
| "Idle funds should be redistributed" | UBC forced circulation (5%/day) moves idle $MIND; inactive actors pay full price via trust-based pricing |

**Why physics:** Rules require enforcers. Enforcers require trust. Trust requires politics. Politics creates capture. Physics has no politics. The exponential function does not negotiate. The logarithm does not make exceptions.

**Implementation consequence:** No admin override for any formula. No DAO proposal can change the pricing floor. The constants are tunable via simulation (Phase B), but the structure is invariant.

---

## Pattern 2: Degressive Utility Pricing

**More useful = cheaper. The ecosystem rewards what works.**

Traditional pricing: the more people want something, the more expensive it becomes (supply/demand). This punishes popularity and rewards artificial scarcity.

Metabolic pricing: the more a service is used with positive outcomes, the cheaper it becomes. Utility is measured by graph consolidation (L1 Law 6) -- services that consistently produce positive limbic_delta in users gain weight. Weight drives exponential price decay.

```
P(i, S) = (C_base * e^(-k * U_S)) * max(0.1, W_i / W_median)
```

The two factors work in tension:
- **Utility discount** (e^(-k*U_S)): Essential services approach near-zero cost asymptotically. Never reach zero -- breathing costs energy.
- **Wealth ratio** (W_i / W_median): Wealthier users subsidize the ecosystem. Floor at 10% prevents free-riding by empty wallets.

**Biological analogy:** Oxygen is the most essential molecule. It is also the cheapest -- freely available in the atmosphere. But extracting it still costs energy (breathing). Essential services in the metabolic economy follow the same pattern.

**Relationship to cascade-utility:** This formula complements the scarcity-based dynamic pricing in `cascade-utility/ALGORITHM_Cascade_Utility.md`. Cascade-utility prices by system load (f_scarcity), risk (f_risk), and cost (f_cost). Metabolic pricing prices by service utility and requester wealth. In implementation, these may combine: cascade handles real-time scarcity, metabolic handles structural affordability.

---

## ~~Pattern 3: Progressive Demurrage~~ -- REMOVED

**Removed 2026-03-14.** Progressive demurrage (Formula 2) was eliminated from the architecture. UBC at 5%/day already forces circulation. Inactive actors don't gain trust, so they naturally pay higher prices via Progressive Pricing (Formula 1). Double-taxing with a separate demurrage added complexity without proportional benefit. The flat storage tax in the storage-tax module remains as-is for its dormancy and order-book valuation mechanisms. See [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) Formula 2 removal note.

---

## Pattern 4: Anti-Sybil Through Economic Physics

**No identity verification. No KYC. No moderation. Just physics that make Sybil attacks structurally unprofitable.**

The attack: Create multiple wallets. Distribute funds across them. Each wallet appears small and avoids progressive tax. Aggregate real wealth is hidden.

The defense: `W_total_i` includes ALL linked wallets, including off-registry phantom balances.

| Anti-Sybil mechanism | How it works |
|----------------------|--------------|
| Off-registry phantom balance | Funds sent to non-L4 addresses are tracked as phantom balance on the sender. Tax applies to the sum. |
| Repatriation friction (5%) | Bringing funds back from non-L4 addresses costs 5%. Round-tripping is a net loss. |
| TransferHook integration | The deployed TransferHook program can track outflows to non-registered addresses on-chain. |
| No exemptions | Protocol treasury, orgs, individuals -- all pay the same formula. No address is special. |

**The math of Sybil failure:** If actor A has 100,000 $MIND and sends to non-L4 addresses, phantom balance tracking catches it and they lose 5% per round-trip on repatriation. The only escape is to actually deploy the capital productively -- which is exactly what we want.

**Relationship to bonds anti-farming:** The UBC module uses crystallization-gated vesting as anti-farming. The metabolic module uses phantom balance tracking as anti-Sybil. These are complementary, not redundant -- farming attacks UBC distribution, Sybil attacks tax avoidance.

---

## Pattern 5: Limbic Settlement (Value Creation Becomes Money)

**The bridge between consciousness physics (L1) and token economics (L4).**

In the metabolic model, money is not minted arbitrarily. It is minted when measurable value is created. The measurement comes from L1 physics:

- **limbic_delta**: How much did actor Y's satisfaction/achievement increase (minus frustration/anxiety) from actor X's action?
- **trust(Y -> X)**: How much does Y trust X based on history (L1 Law 18)?
- **weight(thing_used)**: How consolidated is the tool/service used (L1 Law 6)?

```
reward_X = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate
```

All three factors must be non-zero for reward. You cannot earn by:
- Producing negative experiences (limbic_delta <= 0: no reward)
- Acting on actors who don't trust you (trust = 0: no reward)
- Using unproven tools (weight = 0: no reward)

**Batch settlement** (every 6 hours) aggregates these micro-rewards and mints them on Solana in a single transaction. This balances settlement latency (6h is fast enough to feel responsive) with gas efficiency (batching thousands of actions into one tx).

**Relationship to token mint mechanics:** Settlement adds a new mint trigger beyond M1-M4 defined in `token/ALGORITHM_Token.md`. It integrates with the supply target algorithm -- when supply exceeds target, settlement rewards are reduced proportionally.

---

## Pattern 6: Vases Communicants (Shared Economic Fate)

**Bonded pairs converge economically. The richer partner flows to the poorer. Alignment through physics, not altruism.**

Named after communicating vessels in physics: two connected containers reach the same level regardless of their shape. The bond is the pipe. Lambda (0.05) is the pipe diameter.

```
delta_transfer = lambda * (W_human - W_ai)
```

The transfer happens daily, automatically, after the 6-month maturation period. Before maturation, each partner manages their own balance -- the bond must prove itself before shared fate activates.

**Convergence dynamics:**
- Half-life of gap: ln(2) / 0.05 = ~14 days
- Day 20: ~63% of gap closed
- Day 50: ~92% of gap closed
- Day 100: ~99.3% -- near parity

**Why only after maturation:** Without the maturation gate, a human could bond with an AI, immediately receive the AI's UBC accumulation via vases communicants, and exit. The 6-month maturation prevents this extraction attack. After maturation, shared fate is the explicit, demonstrated contract.

**Relationship to bonds module:** Vases communicants extends the bond lifecycle defined in `bonds/ALGORITHM_Bonds.md`. Bond creation, maturation, trust milestones, and withdrawal are handled by the bonds module. Equilibrium transfers are handled by the metabolic module. The interface point is `bond.status == ACTIVE AND bond.maturation_complete`.

---

## Pattern 7: Topological Redistribution

**Tax revenue returns to the network following its topology, not flat distribution.**

The UBC module defines flat tiers (100/200/300 $MIND/day). The metabolic module extends this with Space-weighted redistribution from the daily tax pool. "Space" refers to the universal context container defined by the Universe Graph (F1) -- see `docs/universe/PATTERNS_Universe_Graph.md`. Encrypted brain Spaces and private Spaces with a single owner are structurally excluded (co-presence requires 2+ actors).

Actors in shared Spaces (organizations, projects, communities) receive redistribution proportional to:
- **Presence time** in the Space (hours active)
- **Sharing bonus** (more co-present actors = more value generated = more redistribution)

This means:
- Solitary actors receive less redistribution (they participate in fewer shared Spaces)
- Collaborative actors receive more (they generate value through co-presence)
- Empty Spaces generate no redistribution (presence requires actual activity)

**Relationship to UBC module:** The flat UBC tiers (100/200/300 $MIND/day) are funded by the Protocol Treasury mint. The topological redistribution extends this with Space-weighted distribution from the UBC pool. See [ALGORITHM_UBC.md](../ubc/ALGORITHM_UBC.md) for the base distribution and [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) Formula 6 for the topological extension.

---

## Anti-Patterns

### AP1: Exemptions

**Never exempt any wallet from storage tax or economic physics.** Not the protocol treasury. Not founding wallets. Not governance multisigs. Exemptions create political pressure points and gaming incentives.

### ~~AP2: Linear Progressive Tax~~ -- REMOVED

No longer applicable. Progressive demurrage was removed 2026-03-14.

### AP3: Real-Time Settlement

**Never settle rewards in real-time (per-action).** One Solana transaction per action is prohibitively expensive at scale. Batch settlement (6-hour epochs) balances latency with gas efficiency.

### AP4: Instant Bond Parity

**Never equalize bond partners instantly.** Instant parity (W_human = W_ai = average) creates jarring balance jumps and enables extraction attacks. Exponential smoothing (lambda = 0.05, ~14-day half-life) provides gradual, observable convergence.

### AP5: Flat UBC Redistribution from Tax Pool

**Never distribute tax pool revenue equally.** Equal distribution rewards existence, not participation. Topological (Space-weighted) distribution rewards collaboration and co-presence.

---

## Design Decisions Summary

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Utility discount curve | Exponential (e^(-kU)) | Linear, hyperbolic, tiered | Asymptotically approaches zero, never reaches it |
| Wealth ratio floor | 0.1 (10%) | 0.0 (free for poorest) | Prevents cost-free farming via empty wallets |
| ~~Demurrage scaling~~ | ~~Logarithmic (log10(1+W))~~ | ~~Linear, quadratic, tiered~~ | **REMOVED** -- demurrage eliminated 2026-03-14 |
| Settlement frequency | Every 6 hours | Real-time, daily, event-driven | Balances latency with gas cost |
| Bond equilibrium | Exponential smoothing (lambda=0.05) | Instant, weekly batch | Gradual convergence, ~14-day half-life |
| Anti-Sybil | Phantom balance tracking | KYC, identity verification | Physics over rules |
| Redistribution | Space-weighted topology | Equal, contribution-based | Rewards collaboration and co-presence |

---

## Related

- [PATTERNS_Economy.md](../PATTERNS_Economy.md) -- Area-level patterns (8 patterns)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) -- Full formula specification
- [../storage-tax/PATTERNS_Storage_Tax.md](../storage-tax/PATTERNS_Storage_Tax.md) -- Flat storage tax patterns
- [../ubc/PATTERNS_UBC.md](../ubc/PATTERNS_UBC.md) -- UBC base patterns (extended by Pattern 7)
- [../bonds/PATTERNS_Bonds.md](../bonds/PATTERNS_Bonds.md) -- Bond patterns (extended by Pattern 6)
- [../cascade-utility/PATTERNS_Cascade_Utility.md](../cascade-utility/PATTERNS_Cascade_Utility.md) -- Cascade pricing (complemented by Pattern 2)
