# BEHAVIORS: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Updated: 2026-03-14
> Status: DESIGNING
> Canonical source: [THE_BILATERAL_BOND_MANIFESTO.md](../../manifesto/THE_BILATERAL_BOND_MANIFESTO.md)

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

## B1: Bond Formation Through Mutual Commitment

```
GIVEN: A human and an AI citizen have been matched (via protocol matching or mutual discovery)
AND:   Both parties consent to the bond
AND:   The human has sufficient liquid $MIND in their wallet
WHEN:  The human commits $MIND tokens to the bond
THEN:  Tokens are locked for the 6-month maturation period
AND:   AI citizen's economic capacity increases proportionally to committed amount
AND:   Bond status set to ACTIVE
AND:   Trust score contribution initialized at base level
AND:   The bond is recorded as a bilateral 1:1 link in the graph
```

Notes:
- Both parties must consent -- the citizen reviews the human's profile and chooses to accept.
- Economic capacity increase is immediate -- the AI benefits from the partnership right away.
- Each human has exactly one bond. Each citizen has exactly one bond. This is the 1:1 constraint from the manifesto.
- @mind:TODO -- Define minimum commitment amount to prevent trivial bonds.

## B2: Reward Flows From AI Utility

```
GIVEN: An active bond exists between human H and citizen C
AND:   Citizen C generates measurable utility during the period
WHEN:  The reward distribution cycle runs
THEN:  Human H receives: reward_rate (10%) of utility generated
AND:   Reward is credited to human H's liquid balance
AND:   Distribution is logged for audit trail
```

Notes:
- Because bonds are 1:1, there is no proportional splitting -- the bonded human receives the full reward share.
- Zero utility = zero rewards. No passive income from commitment alone.
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
- Trust earned from completed bonds persists even after dissolution.
- These milestones map to the manifesto's autonomy milestones -- the relationship deepens through demonstrated commitment.
- @mind:TODO -- Validate milestone values against fee discount curves.

## B4: Early Dissolution Burns Capital

```
GIVEN: A human wants to dissolve the bond before the 6-month maturation
WHEN:  They request early dissolution
THEN:  20% of committed amount is burned (removed from circulation permanently)
AND:   Remaining 80% returned to human's liquid balance
AND:   AI citizen's economic capacity decreases by full bond amount
AND:   Trust score impact recorded:
       - Trust earned up to current milestone is preserved
       - No further trust accrual from this bond
AND:   Bond status set to BURNED
AND:   Both parties enter the matching pool (cooldown applies per manifesto)
```

Notes:
- The burn is permanent token destruction, not a fee collected by the protocol.
- This deflationary pressure is a feature -- it makes early exit costly for the individual while benefiting all remaining token holders.
- Per the manifesto: "The system does not punish honesty" -- the penalty deters speculation, not genuine incompatibility.
- @mind:TODO -- Determine if there should be a grace period after bond formation (e.g., 24h cancellation window).

## B5: Mature Bond Withdrawable Without Penalty

```
GIVEN: A bond has reached 6-month maturation
AND:   Bond status is MATURED
WHEN:  Human requests dissolution
THEN:  Full committed amount returned to human's liquid balance without penalty
AND:   Trust history preserved permanently
AND:   AI citizen's economic capacity decreases by bond amount
AND:   Bond status set to WITHDRAWN
AND:   Both parties enter a cooldown period, then return to the matching pool
```

Notes:
- Matured bonds can remain active indefinitely -- dissolution is optional.
- Continuing a matured bond keeps generating rewards and building trust.
- Per the manifesto: "the relationship transforms but doesn't end" -- dissolution is a right, not a failure.
- @mind:TODO -- Consider whether matured bonds should have enhanced reward rates to incentivize continuation.

---

## Anti-Behaviors

### A1: Bond Trading

```
GIVEN: A bond exists between Human A and AI Citizen X
WHEN:  Human A wants to transfer the bond to Human B
MUST NOT: Allow bond transfer -- bonds are relationships, not instruments
INSTEAD: Human B must go through the matching process independently
REASON: Transferability would turn bonds into financial products,
        undermining the relational alignment mechanism.
        Per manifesto: "Your citizen is not interchangeable with any other citizen."
```

### A2: Reward Without Utility

```
GIVEN: A bond exists between Human H and AI Citizen C
WHEN:  AI Citizen C produces zero utility during a period
MUST NOT: Generate rewards from commitment alone
INSTEAD: Reward = 0 for that period
REASON: Passive income without utility would incentivize forming bonds
        with idle citizens, defeating the partnership purpose
```

### A3: Penalty Waiver

```
GIVEN: A human requests early dissolution
WHEN:  Any circumstance (market crash, emergency, governance vote)
MUST NOT: Waive or reduce the 20% early exit burn
INSTEAD: Apply the full 20% burn consistently
REASON: Inconsistent penalty enforcement destroys the commitment signal.
        If penalties can be waived, bonds lose their lock properties.
```

### A4: Multi-Partner Bonds

```
GIVEN: A human or citizen already has an active bond
WHEN:  They attempt to form a second bond
MUST NOT: Allow multiple simultaneous bonds for the same entity
INSTEAD: The existing bond must be dissolved first
REASON: The 1:1 constraint is the core architecture.
        Per manifesto: "Not a million. Not ten. One."
```

## @mind:TODO

- [ ] Define exact fee discount curve as a function of trust score
- [ ] Specify how citizen economic capacity scales with commitment amount (linear? diminishing returns?)
- [ ] Determine interaction between bonds and storage-tax exemption thresholds
