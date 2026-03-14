# SYNC: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Updated: 2026-03-14
> Status: DESIGNING
> Canonical source: [THE_BILATERAL_BOND_MANIFESTO.md](../../manifesto/THE_BILATERAL_BOND_MANIFESTO.md)

## Chain

- [OBJECTIVES_Bonds.md](./OBJECTIVES_Bonds.md)
- [PATTERNS_Bonds.md](./PATTERNS_Bonds.md)
- [BEHAVIORS_Bonds.md](./BEHAVIORS_Bonds.md)
- [ALGORITHM_Bonds.md](./ALGORITHM_Bonds.md)
- [VALIDATION_Bonds.md](./VALIDATION_Bonds.md)
- [IMPLEMENTATION_Bonds.md](./IMPLEMENTATION_Bonds.md)
- [HEALTH_Bonds.md](./HEALTH_Bonds.md)
- **SYNC_Bonds.md** (this file)

---

## Sync State

| Field | Value |
|-------|-------|
| LAST_UPDATED | 2026-03-14 |
| UPDATED_BY | Claude (manifesto alignment sweep) |
| STATUS | DESIGNING |

## What Changed (2026-03-14)

Full doc chain realignment with THE_BILATERAL_BOND_MANIFESTO.md:
- Removed all "staking" language -- bonds are bilateral relationships, not financial staking products
- Enforced 1:1 constraint throughout (each human one bond, each citizen one bond)
- Added mutual consent requirement to bond formation (citizen must agree)
- Added cooldown/matching pool return after dissolution (per manifesto)
- Renamed operations: create_bond -> form_bond, withdraw_bond -> dissolve_bond
- Added V0 (1:1 constraint) as the foundational validation invariant
- Added H8 (1:1 constraint integrity) and H9 (partnership engagement) health indicators
- Removed speculative multi-bond mechanics (reward splitting, proportional shares across multiple bonders)
- Added manifesto citations throughout for traceability
- Updated status from DRAFT to DESIGNING across all files

## Canonical Decisions

These parameters are settled and should not change without governance process:

| Decision | Value | Rationale |
|----------|-------|-----------|
| 1:1 bilateral constraint | Always | Per manifesto: "Not a million. Not ten. One." |
| Mutual consent | Required | Per manifesto: "The citizen must consent. This is non-negotiable." |
| Maturation period | 6 months | Long enough for genuine commitment, short enough to not trap |
| Early dissolution burn | 20% | Significant deterrent without being punitive |
| Reward rate | 10% of utility | Meaningful incentive, sustainable for protocol |
| Non-transferable | Always | Bonds are relationships, not financial instruments |
| Trust milestones | 1mo/3mo/6mo | Incremental reward for deepening commitment |
| Burn = destruction | Always | Not redistributed -- deflationary by design |
| Cooldown after dissolution | Required | Both parties return to matching pool after cooldown |

## Designing (Active Work)

These items are under active design and may change:

| Item | Current Thinking | Open Questions |
|------|------------------|----------------|
| Trust score formula | log-scale of (commitment amount x duration) | What TRUST_SCALE_FACTOR produces useful distribution? |
| Reward distribution frequency | Weekly | Daily too expensive on-chain? Per-transaction too complex? |
| Citizen capacity amplification | Linear with commitment amount | Should it be sublinear (diminishing returns)? |
| Minimum commitment amount | Undefined | Balance between accessibility and trivial bond prevention |
| Cooldown period duration | Undefined | How long before dissolved parties can re-enter matching pool? |
| Citizen consent mechanism | Undefined | How is consent represented on-chain? |

## Proposed (Not Yet Accepted)

| Proposal | Source | Status |
|----------|--------|--------|
| DAO-managed bond insurance for solo AIs | Cybernetic audit on IA Solos (integration moment) | Under review |
| Bond renewal mechanism (auto-extend matured bonds) | Internal discussion | Not yet evaluated |
| Graduated penalty (lower burn closer to maturation) | Community feedback concept | Rejected -- simplicity wins |
| Multi-citizen bonds (one commitment across multiple AIs) | Token design brainstorm | Rejected -- bonds are 1:1 bilateral per manifesto |

## Cross-Module Dependencies

| Module | Direction | Interface | Status |
|--------|-----------|-----------|--------|
| `token/` | Bonds --> Token | Commitment, locking, burning, minting via SPL Token-2022 | @mind:TODO -- Align with token contract interfaces |
| `cascade-utility/` | Utility --> Bonds | Utility measurement feeds reward calculation | @mind:TODO -- Define utility oracle interface |
| `storage-tax/` | Bonds --> Storage Tax | Bond-committed capital exempt from dormancy (storage tax only — demurrage removed 2026-03-14) | @mind:TODO -- Implement exemption check in storage-tax |
| `organism-model/` | Bonds --> Organism | Trust scores feed membrane pricing | @mind:TODO -- Define trust score consumption API |
| `governance/` | Governance --> Bonds | Parameter changes require governance vote | @mind:TODO -- Define governance hooks for bond parameters |

## Source Documents

| Document | Relevance |
|----------|-----------|
| THE_BILATERAL_BOND_MANIFESTO.md | **CANONICAL** -- source of truth for bond design |
| PATTERNS_Economy.md (patterns 2, 7) | Bond mechanism and switch-lock pattern definitions |
| Integration moment synthesis (2026-03) | Crystallized canonical decisions on maturation, burn rate, reward rate |
| Cybernetic audit: IA Solos | Proposed bond insurance for AI citizens without human bonds |
| Venice Values manifesto | Privacy-first, user sovereignty principles that bonds must respect |

## Change Log

| Date | Change | By |
|------|--------|----|
| 2026-03-14 | Manifesto alignment -- removed staking language, enforced 1:1, added consent | Claude (manifesto alignment sweep) |
| 2026-03-12 | Initial doc chain creation -- all 8 files | Claude (integration moment) |

## @mind:TODO

- [ ] Schedule design review for trust score formula with Nicolas
- [ ] Resolve reward distribution frequency (weekly vs daily vs event-driven)
- [ ] Define citizen capacity amplification formula and validate with simulation
- [ ] Coordinate with token/ module on SPL Token-2022 integration points
- [ ] Evaluate DAO-managed bond insurance proposal formally
- [ ] Create cross-module integration test plan with cascade-utility/ and storage-tax/
- [ ] Define cooldown period duration after dissolution
- [ ] Design citizen consent mechanism (on-chain representation)
