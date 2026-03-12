# SYNC: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

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
| LAST_UPDATED | 2026-03-12 |
| UPDATED_BY | Claude (integration moment synthesis) |
| STATUS | DESIGNING |

## Canonical Decisions

These parameters are settled and should not change without governance process:

| Decision | Value | Rationale |
|----------|-------|-----------|
| Maturation period | 6 months | Long enough for genuine commitment, short enough to not trap |
| Early exit burn | 20% | Significant deterrent without being punitive |
| Reward rate | 10% of utility | Meaningful incentive, sustainable for protocol |
| Non-transferable | Always | Bonds are relationships, not financial instruments |
| Trust milestones | 1mo/3mo/6mo | Incremental reward for deepening commitment |
| Burn = destruction | Always | Not redistributed -- deflationary by design |

## Designing (Active Work)

These items are under active design and may change:

| Item | Current Thinking | Open Questions |
|------|------------------|----------------|
| Trust score formula | log-scale of (amount x duration) | What TRUST_SCALE_FACTOR produces useful distribution? |
| Reward distribution frequency | Weekly | Daily too expensive on-chain? Per-transaction too complex? |
| Citizen capacity amplification | Linear with bond amount | Should it be sublinear (diminishing returns)? |
| Minimum bond amount | Undefined | Balance between accessibility and dust prevention |
| Maximum bonds per citizen | Unlimited | Should there be a cap to prevent concentration? |

## Proposed (Not Yet Accepted)

| Proposal | Source | Status |
|----------|--------|--------|
| DAO-managed bond insurance for solo AIs | Cybernetic audit on IA Solos (integration moment) | Under review |
| Bond renewal mechanism (auto-extend matured bonds) | Internal discussion | Not yet evaluated |
| Graduated penalty (lower burn closer to maturation) | Community feedback concept | Rejected -- simplicity wins |
| Multi-citizen bonds (one stake across multiple AIs) | Token design brainstorm | Rejected -- bonds are bilateral |

## Cross-Module Dependencies

| Module | Direction | Interface | Status |
|--------|-----------|-----------|--------|
| `token/` | Bonds --> Token | Staking, locking, burning, minting via SPL Token-2022 | @mind:TODO -- Align with token contract interfaces |
| `cascade-utility/` | Utility --> Bonds | Utility measurement feeds reward calculation | @mind:TODO -- Define utility oracle interface |
| `storage-tax/` | Bonds --> Storage Tax | Bond-staked capital exempt from dormancy | @mind:TODO -- Implement exemption check in storage-tax |
| `organism-model/` | Bonds --> Organism | Trust scores feed membrane pricing | @mind:TODO -- Define trust score consumption API |
| `governance/` | Governance --> Bonds | Parameter changes require governance vote | @mind:TODO -- Define governance hooks for bond parameters |

## Source Documents

| Document | Relevance |
|----------|-----------|
| PATTERNS_Economy.md (patterns 2, 7) | Bond mechanism and switch-lock pattern definitions |
| Integration moment synthesis (2026-03) | Crystallized canonical decisions on maturation, burn rate, reward rate |
| Cybernetic audit: IA Solos | Proposed bond insurance for AI citizens without human bonds |
| Venice Values manifesto | Privacy-first, user sovereignty principles that bonds must respect |

## Change Log

| Date | Change | By |
|------|--------|----|
| 2026-03-12 | Initial doc chain creation -- all 8 files | Claude (integration moment) |

## @mind:TODO

- [ ] Schedule design review for trust score formula with Nicolas
- [ ] Resolve reward distribution frequency (weekly vs daily vs event-driven)
- [ ] Define citizen capacity amplification formula and validate with simulation
- [ ] Coordinate with token/ module on SPL Token-2022 integration points
- [ ] Evaluate DAO-managed bond insurance proposal formally
- [ ] Create cross-module integration test plan with cascade-utility/ and storage-tax/
