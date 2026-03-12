# SYNC -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | SYNC |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Synchronization State

| Key | Value |
|-----|-------|
| LAST_UPDATED | 2026-03-12 |
| UPDATED_BY | Claude (integration moment synthesis) |
| STATUS | DESIGNING |

## Canonical Decisions

These are settled and should not be revisited without explicit governance process:

| Decision | Value | Settled Date |
|----------|-------|-------------|
| Annual storage tax rate | 1% per year | 2026-01-30 |
| Dormancy decay rate | 0.5% per month | 2026-01-30 |
| Grace period before dormancy | 30 days | 2026-01-30 |
| Valuation method | Staked order-book depth (not last-trade) | 2026-01-30 |
| Minimum stake ratio for orders | 10% of order value | 2026-01-30 |
| Tax destination | UBC redistribution pool | 2026-01-30 |
| Exemptions | None (universal application) | 2026-01-30 |
| Computation frequency | Daily (1 epoch = 1 day) | 2026-03-12 |

## Currently Designing

Active design work in progress:

| Topic | Status | Blocking |
|-------|--------|----------|
| Order-book valuation implementation | Researching DEX integration options | IMPLEMENTATION |
| Grace period detection algorithm | Pseudocode complete, needs Token-2022 feasibility check | IMPLEMENTATION |
| Per-token-batch idle tracking | FIFO vs LIFO vs weighted average undecided | ALGORITHM, BEHAVIORS |
| Epoch execution architecture | On-chain vs off-chain vs hybrid undecided | IMPLEMENTATION |
| Dust threshold | Value not yet defined | ALGORITHM |

@mind:TODO -- Resolve per-token-batch tracking method. FIFO is simplest and most intuitive but may be expensive to compute on-chain.

## Proposed (Not Yet Designing)

Ideas captured but not yet in active design:

| Topic | Source | Notes |
|-------|--------|-------|
| Dynamic tax rate indexed on ecosystem health | Integration moment, 2026-03-12 | Rate adjusts based on velocity, dormancy ratio |
| Trust-score modulated grace period | Cross-module discussion | High cascade-utility score = longer grace |
| Graduated dormancy (0.5% -> 1% -> 2% over time) | Nicolas, brainstorm | Escalating pressure on chronic hoarders |
| Tax holiday for new wallets (first 90 days) | Onboarding concern | Reduces friction for new participants |
| Negative storage tax (rewards for optimal velocity) | Sebastien Deschaux | Paying actors who maintain ideal circulation rate |

@mind:TODO -- Prioritize proposed items for next design cycle.

## Source Material

| Source | Date | Contribution |
|--------|------|-------------|
| PATTERNS_Economy.md (parent area) | 2026-01-30 | Sebastien Deschaux's original formulation of storage tax as metabolic rate |
| Integration moment audits | 2026-03 | Cross-session validation of tax mechanics, identification of gaming vectors |
| Token-2022 documentation | Ongoing | Transfer hook feasibility for activity tracking |

## Cross-Module Sync Points

| Module | Sync Status | Last Verified | Notes |
|--------|-------------|---------------|-------|
| ubc/ | IN SYNC | 2026-03-12 | Storage tax as primary UBC funding source -- agreed |
| cascade-utility/ | NEEDS SYNC | -- | Trust score interaction with grace period not yet discussed |
| token/ | NEEDS SYNC | -- | Token-2022 transfer hook feasibility not yet confirmed |
| governance/ | NOT STARTED | -- | Rate governability question unresolved |

@mind:TODO -- Schedule sync with cascade-utility/ module owner on trust-score interaction.
@mind:TODO -- Schedule sync with token/ module owner on Token-2022 transfer hook capabilities and limitations.
