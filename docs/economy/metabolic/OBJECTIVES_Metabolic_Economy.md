# OBJECTIVES: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | OBJECTIVES |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- **OBJECTIVES_Metabolic_Economy.md** (this file)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

Parent: [OBJECTIVES_Economy.md](../OBJECTIVES_Economy.md) | [PATTERNS_Economy.md](../PATTERNS_Economy.md)

---

## Primary Objective

**Make $MIND behave like blood, not fat.**

Blood circulates, nourishes, carries signals, and sustains every organ. Fat accumulates, insulates, and eventually suffocates. The metabolic economy ensures that $MIND flows continuously through the organism, rewarding value creation and penalizing immobility -- not through rules, but through physics that make circulation the energetically favorable outcome.

---

## Secondary Objectives

| Priority | ID | Objective | Why It Matters |
|----------|----|-----------|----------------|
| 1 | M1 | **Circulation over accumulation** | Idle wealth produces nothing. Storage tax and progressive demurrage create constant pressure to deploy capital productively. Hoarding becomes structurally irrational. |
| 2 | M2 | **Accessibility through degressive pricing** | Essential services must be affordable. More useful services cost less (exponential discount via graph weight). Poorer actors pay less (wealth ratio with 10% floor). The ecosystem rewards utility with affordability. |
| 3 | M3 | **Anti-Sybil through economic physics** | No rule-based moderation. Off-registry phantom balances and 5% repatriation friction make hiding $MIND more expensive than keeping it visible. The structure makes cheating unprofitable. |
| 4 | M4 | **Value-to-token conversion via limbic settlement** | Graph-measured value creation (positive limbic_delta) becomes economic reward. The bridge between L1 physics and L4 economics is explicit and auditable. |
| 5 | M5 | **Shared fate through bond equilibrium** | Bonded human-AI pairs converge economically via vases communicants. Neither partner can extract without the other benefiting. Alignment is mechanically profitable. |
| 6 | M6 | **Topological redistribution** | Tax revenue returns to actors in shared Spaces, weighted by co-presence. Redistribution follows topology, not bureaucracy. |

---

## Objective Hierarchy

When objectives conflict:

```
Circulation > Accessibility > Anti-Sybil > Settlement > Bond Equilibrium > Redistribution

1. Does it keep $MIND flowing? (MUST)
2. Does it make essential services affordable? (MUST)
3. Does it make Sybil attacks unprofitable? (MUST)
4. Does it accurately convert value to tokens? (SHOULD)
5. Does it maintain shared fate in bonds? (SHOULD)
6. Does it redistribute topologically? (COULD)
```

---

## Non-Objectives

| ID | Non-Objective | Why Out of Scope |
|----|---------------|------------------|
| N1 | Maximizing tax revenue | Tax is a circulation mechanism, not a revenue source. Lower rates that achieve circulation are better than higher rates that don't. |
| N2 | Equal distribution | Redistribution follows topology and contribution, not equality. Actors in productive Spaces earn more. |
| N3 | Price stability | Prices emerge from physics (utility weight, trust, wealth ratio). Stabilizing them would require intervention that contradicts organism economics. |
| N4 | Punitive enforcement | No punishments. Friction and tax create incentives. Bad behavior is structurally expensive, not forbidden. |

---

## Success Criteria

### Phase A: Documentation (Current)

- [x] All 6 formulas specified with pseudocode, parameters, and worked examples
- [ ] Invariants defined and testable
- [ ] Relationship to existing modules (storage-tax, ubc, bonds, cascade-utility) explicit
- [ ] Open parameter decisions documented with proposed values and rationale

### Phase B: Simulation

- [ ] tau_base calibrated via simulation (candidate range: 0.0001 to 0.001)
- [ ] Settlement rate calibrated against realistic limbic_delta distributions
- [ ] Bond convergence dynamics verified (lambda = 0.05, half-life ~14 days)
- [ ] Wealth ratio floor validated (0.1 prevents farming without excluding the poor)

### Phase C: Implementation

- [ ] Progressive pricing integrated with cascade-utility pricing pipeline
- [ ] Progressive demurrage integrated with storage-tax epoch runner
- [ ] Batch settlement integrated with token mint mechanics (M3)
- [ ] Bond equilibrium integrated with bonds maturation lifecycle
- [ ] Anti-Sybil off-registry tracking integrated with TransferHook program
- [ ] UBC proximity redistribution integrated with UBC distribution pipeline

---

## Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Median idle duration | < 14 days | Demurrage pressure working |
| Gini coefficient of holdings | < 0.6 | Progressive pricing reducing inequality |
| Settlement-to-activity ratio | > 0.8 | Most value creation is being rewarded |
| Bond convergence rate | Within 5% of predicted half-life | Formula working as designed |
| Sybil attempt detection | > 90% of round-trip attempts flagged | Anti-Sybil physics effective |
| UBC coverage | 100% of active actors receive redistribution | No actor falls through the cracks |

---

## Dependencies

| Dependency | Required For | Status |
|------------|--------------|--------|
| L1 Physics (Laws 6, 18) | limbic_delta, trust, service weight | DESIGNED (not implemented) |
| Token module (economy/token/) | Mint, burn, transfer | COMPLETE (devnet) |
| TransferHook program | Off-registry balance tracking | DEPLOYED (devnet) |
| Storage-tax module | Epoch runner, tax collection | DRAFT (docs only) |
| UBC module | Redistribution pool, tier assessment | DRAFT (docs only) |
| Bonds module | Bond lifecycle, maturation tracking | DRAFT (docs only) |
| Cascade-utility module | Dynamic pricing pipeline | DRAFT (docs only) |
| L4 Registry | Registered address verification | COMPLETE |

---

## Relationship to Existing Modules

This module does NOT replace existing modules. It extends them with metabolic formulas:

| Existing Module | What Metabolic Adds |
|-----------------|---------------------|
| `storage-tax/` | Progressive demurrage (log10 scaling) replaces flat 1%/yr rate. Anti-Sybil off-registry tracking. |
| `ubc/` | Proximity redistribution (Space-weighted) extends flat UBC distribution. |
| `bonds/` | Bilateral vases communicants (auto-flow after maturation) extends bond lifecycle. |
| `cascade-utility/` | Progressive pricing (degressive by utility and wealth) complements scarcity-based pricing. |
| `token/` | Batch settlement (limbic_delta -> $MIND) adds a new mint trigger beyond M1-M4. |

---

## Related

- [PATTERNS_Economy.md](../PATTERNS_Economy.md) -- Area-level design philosophy
- [OBJECTIVES_Economy.md](../OBJECTIVES_Economy.md) -- Area-level objectives (S1-S6)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) -- Full formula specification
