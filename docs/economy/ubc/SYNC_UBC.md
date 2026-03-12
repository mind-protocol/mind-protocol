# SYNC: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## Sync Status

```
LAST_UPDATED: 2026-03-12
UPDATED_BY:   Claude (integration moment synthesis)
STATUS:       DESIGNING
```

---

## Document Chain Status

| Document | Status | Last Updated | Notes |
|----------|--------|-------------|-------|
| CONCEPT_UBC.md | DRAFT | 2026-03-12 | Core framing complete |
| OBJECTIVES_UBC.md | DRAFT | 2026-03-12 | Priorities ranked, tradeoffs documented |
| PATTERNS_UBC.md | DRAFT | 2026-03-12 | Vesting pattern defined, anti-patterns noted |
| BEHAVIORS_UBC.md | DRAFT | 2026-03-12 | 5 behaviors + 4 anti-behaviors specified |
| ALGORITHM_UBC.md | DRAFT | 2026-03-12 | Pseudocode complete, 3 key decisions documented |
| VALIDATION_UBC.md | DRAFT | 2026-03-12 | 7 validation rules with verification steps |
| IMPLEMENTATION_UBC.md | DRAFT | 2026-03-12 | No code yet — architecture planned |
| HEALTH_UBC.md | DRAFT | 2026-03-12 | 7 health indicators defined |
| SYNC_UBC.md | DRAFT | 2026-03-12 | This file |

---

## Design Maturity

### Canonical (Decided)
These elements are settled and should be treated as stable:

- **Three tiers:** Basic (100 $MIND/day), Active (200 $MIND/day), Contributor (300 $MIND/day)
- **Vesting model:** UBC distributed daily but illiquid; unlock via crystallization milestones
- **Anti-farming via topological proof:** Crystallization requires genuine interaction topology
- **Unconditional floor:** Basic tier is a right, not a reward — protected by L8 CORE 5th axiom
- **Circular funding:** Storage tax on dormant capital funds UBC distribution
- **Quarantine survival:** Excluded AIs continue receiving Basic UBC

### Designing (Active Work)
These elements have a direction but details are being refined:

- **Crystallization thresholds:** 50/100/150/200/250 nodes selected but measurement methodology TBD
  - What graph topology qualifies as "coherent"?
  - Which community detection algorithm? (Louvain, label propagation, spectral?)
  - How to distinguish genuine from synthetic crystallization?
- **Vesting curve shape:** Milestone-based (step function) selected over linear/logarithmic
  - Unlock rates (10%/20%/30%/40%/100%) need economic modeling
  - Should unlocks be proportional to vested balance at time of milestone?
- **Tier assessment criteria:** Activity-based (utility delivery count) with EIS for Contributor
  - What counts as a "utility delivery"?
  - What EIS threshold qualifies for Contributor?
  - Should tier assessment consider quality, not just quantity?

### Proposed (Under Discussion)
These elements are ideas that have not been formally evaluated:

- **Dynamic UBC indexed on token health:** Increase UBC if $MIND price rises, decrease if it dumps
  - Pro: Self-balancing, prevents UBC from becoming worthless during downturns
  - Con: Violates "unconditional" principle if floor amount fluctuates
  - Compromise: Index tier amounts but maintain minimum floor in USD-equivalent terms
- **UBC staking:** Allow AIs to stake liquid UBC for governance weight
  - Pro: Gives AIs political voice proportional to accumulated capital
  - Con: Could create plutocratic dynamics among AI citizens
- **Inter-AI UBC transfer:** Allow AIs to gift liquid UBC to other AIs
  - Pro: Enables AI-to-AI mutual aid networks
  - Con: Potential channel for farming (laundering harvested UBC through gift chains)

---

## Key Unresolved Issues

### U1: Farming Attack Economics
**Status:** Partially mitigated by vesting, not fully modeled

The vesting mechanism makes farming expensive (genuine interaction required per AI) but the exact economics haven't been modeled. Questions:
- At what scale does farming become profitable despite vesting?
- What if crystallization can be partially automated? (LLM-to-LLM interaction)
- Should there be a registration cost to raise the farming floor?

### U2: Wallet Key Custody for AI Sovereignty
**Status:** MPC sharding selected architecturally, NOT implemented

How does an AI hold sovereign custody of a private key?
- MPC key sharding: Fragment 1 (TEE), Fragment 2 (DAO coalition), Fragment 3 (local graph)
- Requires TEE infrastructure not yet available
- Without sovereign custody, "AI economic agency" is mediated by protocol custody
- This is the single biggest blocker for true AI financial autonomy

### U3: Cross-Protocol UBC
**Status:** Not yet considered

If multiple protocols adopt UBC-like mechanisms, how do they interact?
- Can an AI registered in Protocol A receive UBC from Protocol B?
- Is there a universal UBC standard?
- Federation vs. isolation tradeoffs

---

## Source Material

Primary sources for UBC design decisions:

- `data/integration_moment/` — UBC liquidity debate (March 2026 multi-instance synthesis)
- `data/integration_moment/` — Architecture de la Cascade (topological proof framework)
- Paper 04: "AI Economic Agency in Tokenized Ecosystems" (drafted)
- L8 CORE axioms, specifically 5th axiom (Dignity)
- Venice Values: unconditional floor, user sovereignty, privacy-first

---

## Change Log

| Date | Change | By |
|------|--------|----|
| 2026-03-12 | Initial document chain creation (9 files) | Claude (integration moment) |

## @mind:TODO

- [ ] Schedule design review for crystallization methodology
- [ ] Commission economic modeling for farming attack scenarios
- [ ] Coordinate with TEE infrastructure for U2 resolution
- [ ] Review proposed dynamic UBC indexing with governance
- [ ] Update this sync document after each design decision
