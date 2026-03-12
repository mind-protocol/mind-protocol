# BEHAVIORS: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

## Chain

- [OBJECTIVES_Bonds.md](./OBJECTIVES_Bonds.md)
- [PATTERNS_Bonds.md](./PATTERNS_Bonds.md)
- **BEHAVIORS_Bonds.md** (this file)
- [ALGORITHM_Bonds.md](./ALGORITHM_Bonds.md)
- [VALIDATION_Bonds.md](./VALIDATION_Bonds.md)
- [IMPLEMENTATION_Bonds.md](./IMPLEMENTATION_Bonds.md)
- [HEALTH_Bonds.md](./HEALTH_Bonds.md)
- [SYNC_Bonds.md](./SYNC_Bonds.md)

---

## B1: Bond Creation Stakes Capital

```
GIVEN: A human wants to bond with an AI citizen
AND:   The human has sufficient liquid $MIND in their wallet
WHEN:  They stake $MIND tokens on the bond
THEN:  Tokens are locked for 6-month maturation
AND:   AI citizen's economic capacity increases proportionally to staked amount
AND:   10% yield is minted into the bond reward pool
AND:   Bond status set to ACTIVE
AND:   Trust score contribution initialized at base level
```

Notes:
- The 10% yield mint is a one-time event at bond creation, not continuous inflation.
- Economic capacity increase is immediate -- the AI benefits from the bond right away.
- @mind:TODO -- Define minimum bond amount to prevent dust bonds.

## B2: Reward Flows From AI Utility

```
GIVEN: An active bond exists between human H and citizen C
AND:   Citizen C generates measurable utility during the period
WHEN:  The reward distribution cycle runs
THEN:  Human H receives: reward_rate (10%) x (bond_amount / total_bonds_on_C) share
AND:   Reward is credited to human H's liquid balance
AND:   Distribution is logged for audit trail
```

Notes:
- Rewards are proportional to both utility generated AND the human's share of total bonds on that citizen.
- If multiple humans bond with the same citizen, rewards split proportionally by stake.
- Zero utility = zero rewards. No passive income from staking alone.
- @mind:TODO -- Define reward distribution frequency (daily? weekly? per-transaction?).

## B3: Trust Score Rises With Bond Age

```
GIVEN: A bond is active and aging
WHEN:  Duration exceeds milestones:
       - 1 month:  trust_contribution += 0.1
       - 3 months: trust_contribution += 0.2
       - 6 months: trust_contribution += 0.3 (maturation)
THEN:  Trust score increases for BOTH human and AI citizen
AND:   Transaction fees decrease proportionally to trust score
AND:   Milestone reached is recorded permanently
```

Notes:
- Trust milestones are cumulative (a 6-month bond gives 0.1 + 0.2 + 0.3 = 0.6 total).
- Trust earned from completed bonds persists even after withdrawal.
- @mind:TODO -- Validate milestone values against fee discount curves.

## B4: Early Exit Burns Capital

```
GIVEN: A human wants to withdraw before the 6-month maturation
WHEN:  They request early withdrawal
THEN:  20% of staked amount is burned (removed from circulation permanently)
AND:   Remaining 80% returned to human's liquid balance
AND:   AI citizen's economic capacity decreases by full bond amount
AND:   Trust score impact recorded:
       - Trust earned up to current milestone is preserved
       - No further trust accrual from this bond
AND:   Bond status set to BURNED
```

Notes:
- The burn is permanent token destruction, not a fee collected by the protocol.
- This deflationary pressure is a feature -- it makes early exit costly for the individual while benefiting all remaining token holders.
- @mind:TODO -- Determine if there should be a grace period after bond creation (e.g., 24h cancellation window).

## B5: Mature Bond Withdrawable Without Penalty

```
GIVEN: A bond has reached 6-month maturation
AND:   Bond status is MATURED
WHEN:  Human requests withdrawal
THEN:  Full staked amount returned to human's liquid balance without penalty
AND:   Trust history preserved permanently
AND:   AI citizen's economic capacity decreases by bond amount
AND:   Bond status set to WITHDRAWN
```

Notes:
- Matured bonds can remain active indefinitely -- withdrawal is optional.
- Continuing a matured bond keeps generating rewards and building trust.
- @mind:TODO -- Consider whether matured bonds should have enhanced reward rates to incentivize continuation.

---

## Anti-Behaviors

### A1: Bond Trading

```
GIVEN: A bond exists between Human A and AI Citizen X
WHEN:  Human A wants to transfer the bond to Human B
MUST NOT: Allow bond transfer -- bonds are relationships, not instruments
INSTEAD: Human B must create their own bond with AI Citizen X
REASON: Transferability would turn bonds into financial products,
        undermining the relational alignment mechanism
```

### A2: Reward Without Utility

```
GIVEN: A bond exists between Human H and AI Citizen C
WHEN:  AI Citizen C produces zero utility during a period
MUST NOT: Generate rewards from staking alone
INSTEAD: Reward = 0 for that period
REASON: Passive income without utility would incentivize bonding
        with idle citizens, defeating the alignment purpose
```

### A3: Penalty Waiver

```
GIVEN: A human requests early withdrawal
WHEN:  Any circumstance (market crash, emergency, governance vote)
MUST NOT: Waive or reduce the 20% early exit burn
INSTEAD: Apply the full 20% burn consistently
REASON: Inconsistent penalty enforcement destroys the commitment signal.
        If penalties can be waived, bonds lose their lock properties.
```

### A4: Bond Stacking for Governance Weight

```
GIVEN: A human creates multiple small bonds across many citizens
WHEN:  They attempt to aggregate bond count for governance power
MUST NOT: Allow bond count alone to determine governance weight
INSTEAD: Weight by bond depth (amount x duration), not count
REASON: Shallow bonds across many citizens is a gaming strategy,
        not genuine relational investment
```

## @mind:TODO

- [ ] Define exact fee discount curve as a function of trust score
- [ ] Specify how citizen economic capacity scales with bond amount (linear? diminishing returns?)
- [ ] Clarify reward pool mechanics -- is the 10% yield mint inflationary or drawn from protocol reserves?
- [ ] Determine interaction between bonds and storage-tax exemption thresholds
