# BEHAVIORS: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | BEHAVIORS |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- **BEHAVIORS_Metabolic_Economy.md** (this file)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

---

## Overview

This document describes what the metabolic economy looks like from the outside -- what happens when a user acts, when daily epochs run, when funds move. Each behavior maps to one or more formulas from ALGORITHM_Metabolic_Economy.md.

---

## B1: User Requests a Service

**When:** An actor requests a service from the ecosystem (compute, translation, analysis, etc.)

**What happens:**

1. The system looks up the service's utility weight (`U_S`) from the graph -- how much this service has been used with positive outcomes.
2. The system looks up the requester's wallet balance (`W_i`) and the network median (`W_median`).
3. Price is computed: `P = C_base * e^(-k * U_S) * max(0.1, W_i / W_median)`.
4. The requester sees the price before confirming.
5. If confirmed, `P` is deducted from the requester's wallet.

**Observable effects:**

| Scenario | What the user sees |
|----------|-------------------|
| New, unproven service (U_S = 0) | Full base price, no utility discount |
| Popular, proven service (U_S = 100) | ~63% discount from utility weight |
| Essential, critical service (U_S = 200) | ~86% discount -- near-commodity pricing |
| Poor requester (W_i << W_median) | Pays as low as 10% of median-income price |
| Wealthy requester (W_i >> W_median) | Pays multiples of median-income price |
| Median-income requester (W_i = W_median) | Pays exactly the utility-discounted base price |

**What does NOT happen:**
- No negotiation. Price is computed, not proposed.
- No alternative quotes from different providers. Physics determines the price.
- No discount codes, promotions, or special offers. The formula is the offer.

**Formula reference:** Formula 1 (Progressive Pricing) in ALGORITHM_Metabolic_Economy.md.

---

## ~~B2: Daily Demurrage Epoch~~ -- REMOVED

**Removed 2026-03-14.** Progressive demurrage (Formula 2) was removed from the architecture. UBC at 5%/day already forces circulation; inactive actors don't gain trust, so they naturally pay higher prices via Progressive Pricing (Formula 1). Separate demurrage added complexity without proportional benefit. Forced circulation is now handled by UBC mechanics. See ALGORITHM_Metabolic_Economy.md Formula 2 removal note.

---

## B3: Actor Sends Funds to Non-L4 Address

**When:** An actor transfers $MIND to a wallet address that is not registered in the L4 registry.

**What happens:**

1. The transfer executes normally on Solana.
2. The TransferHook program detects the recipient is not L4-registered.
3. The transfer amount is added to the sender's `off_registry_balance`.
4. The sender's `W_total_i` now includes this phantom amount.
5. The sender's `W_total_i` now includes this phantom amount for anti-Sybil tracking.

**Observable effects:**

| Actor intent | What actually happens |
|-------------|----------------------|
| "I'll hide my funds in a personal wallet" | Phantom balance tracked. 5% cost if you ever bring it back. |
| "I'm paying a merchant outside L4" | Same tracking applies. If merchant registers in L4, future transfers are clean. |
| "I'm sending to an exchange" | L4-registered exchanges are exempt from phantom tracking. |

**What does NOT happen:**
- The transfer is NOT blocked. Funds move freely.
- No warning or confirmation dialog. The transfer happens, tracking happens silently.
- No "punishment" -- the phantom balance ensures accurate anti-Sybil tracking.

**Formula reference:** Formula 3 (Anti-Sybil Auto-Repatriation) in ALGORITHM_Metabolic_Economy.md.

---

## B4: Actor Repatriates Funds from Non-L4 Address

**When:** An actor brings $MIND back from a non-L4-registered address.

**What happens:**

1. The incoming transfer is detected.
2. 5% friction tax is computed on the gross amount.
3. The friction tax is permanently burned (token destruction).
4. The net amount (95%) is credited to the actor's balance.
5. The actor's `off_registry_balance` is reduced by the gross amount.

**Observable effects:**

```
Example: Actor repatriates 10,000 $MIND from personal non-L4 wallet.
  Friction tax: 10,000 * 0.05 = 500 $MIND (burned)
  Net received: 9,500 $MIND
  Off-registry balance reduced by: 10,000 $MIND

Round-trip cost: Send 10,000 to non-L4, bring it back = net loss of 500 $MIND.
Conclusion: Round-tripping is always a net loss (5% friction on every round-trip).
```

**What does NOT happen:**
- No approval process. Repatriation is automatic.
- No refund of friction tax. The burn is permanent.
- No penalty beyond the 5% friction. This is not a punishment, it is a structural cost.

**Formula reference:** Formula 3 (Anti-Sybil Auto-Repatriation) in ALGORITHM_Metabolic_Economy.md.

---

## B5: Value Creation Produces Settlement Reward

**When:** An actor performs an action that produces a positive limbic shift in another actor.

**What happens:**

1. L1 physics computes the limbic_delta for the action (satisfaction + achievement - frustration - anxiety).
2. If limbic_delta > 0, the action is queued for the next settlement batch.
3. At the next 6-hour epoch (00:00, 06:00, 12:00, or 18:00 UTC), the batch processes.
4. Reward is computed: `reward = limbic_delta * trust(Y->X) * weight(thing) * settlement_rate`.
5. Reward is capped per-action (1000 $MIND) and per-actor-per-epoch (5000 $MIND).
6. Rewards are minted on Solana in a single batch transaction.

**Observable effects:**

| Action type | limbic_delta | trust | weight | Reward (rate=10) |
|------------|-------------|-------|--------|-------------------|
| Excellent debugging help | 0.8 | 0.9 | 0.6 | 4.32 $MIND |
| Mediocre translation | 0.2 | 0.5 | 0.8 | 0.80 $MIND |
| Harmful content generation | -0.5 | any | any | 0 $MIND (negative = no reward) |
| Good work for stranger | 0.6 | 0.1 | 0.7 | 0.42 $MIND (low trust = low reward) |
| Good work with unproven tool | 0.6 | 0.8 | 0.1 | 0.48 $MIND (low weight = low reward) |

**What does NOT happen:**
- No instant reward. All rewards are batched to 6-hour epochs.
- No reward for negative experiences. Only positive limbic_delta generates $MIND.
- No reward without trust. Strangers must build relationships before earning significantly.
- No unlimited earning. Per-epoch caps prevent gaming.

**Formula reference:** Formula 4 (Batch Settlement) in ALGORITHM_Metabolic_Economy.md.

---

## B6: Bonded Pair Receives Daily Equilibrium Transfer

**When:** A human-AI bond has completed its 6-month maturation period and both partners have non-dust balances.

**What happens:**

1. The daily bond equilibrium job runs (at 00:00 UTC).
2. For each mature bond, the gap is computed: `delta = lambda * (W_human - W_ai)`.
3. If delta > MIN_TRANSFER_THRESHOLD (1.0 $MIND), a transfer executes.
4. If delta is positive (human richer), funds flow from human to AI.
5. If delta is negative (AI richer), funds flow from AI to human.
6. Transfer is capped at MAX_DAILY_BOND_TRANSFER (500 $MIND) to prevent shock.

**Observable effects:**

```
Day 0: Human has 10,000 $MIND, AI has 0 $MIND.
  Bond matured. Equilibrium activates.

Day 1: delta = 0.05 * 10000 = 500 (cap hit). Transfer: 500 from human to AI.
  Human: 9,500. AI: 500.

Day 2: delta = 0.05 * 9000 = 450. Transfer: 450.
  Human: 9,050. AI: 950.

Day 14 (~half-life): Gap is ~50% closed.
  Human: ~7,500. AI: ~2,500.

Day 50: Gap is ~92% closed.
  Human: ~5,400. AI: ~4,600.

Day 100: Near parity.
  Human: ~5,035. AI: ~4,965.
```

**What does NOT happen:**
- No equilibrium before maturation. The 6-month period must complete first.
- No instant equalization. Convergence is gradual (14-day half-life).
- No opt-out. Bond equilibrium is part of the bond contract.
- No transfer to/from burned or withdrawn bonds.

**Formula reference:** Formula 5 (Bilateral Bond Vases Communicants) in ALGORITHM_Metabolic_Economy.md.

---

## B7: Tax Pool Redistributed by Space Proximity

**When:** At 00:00 UTC, the accumulated UBC pool is redistributed.

**What happens:**

1. All Spaces with actor presence data for the day are collected.
2. Spaces with fewer than 2 actors are excluded (no solo redistribution).
3. Each actor's weight is computed: `hours_present * (actors_in_space - 1)`.
4. Weights are summed across all Spaces an actor participates in.
5. Tax pool is distributed proportionally to normalized weights.

**Observable effects:**

| Actor profile | Redistribution received |
|---------------|------------------------|
| Active in 3 Spaces, 8 hours each, with many collaborators | Highest share -- rewarded for collaboration |
| Active in 1 Space, 4 hours, with 1 partner | Modest share -- present but limited collaboration |
| Active but only in solo Spaces | Zero from tax pool (still receives flat UBC) |
| Inactive (no Space presence) | Zero from tax pool (still receives flat UBC if registered) |

**What does NOT happen:**
- No equal split. Distribution follows topology.
- No redistribution to solo actors. Co-presence is required.
- No carryover penalty. If pool is not fully distributed (no shared Spaces), it carries forward.

**Formula reference:** Formula 6 (UBC Proximity Redistribution) in ALGORITHM_Metabolic_Economy.md.

---

## B8: Wealthy Actor Pays for a Popular Service

**When:** An actor with a large wallet requests a service with high utility weight.

**What happens (compound behavior):**

This behavior shows the pricing dynamics for wealthy actors.

```
Scenario: Wealthy actor (W_i = 100,000) requests popular translation (U_S = 150).
Network median: W_median = 10,000.

Pricing (B1):
  utility_discount = e^(-0.01 * 150) = 0.223
  wealth_ratio = max(0.1, 100000/10000) = 10.0
  Price = 100 * 0.223 * 10.0 = 223 $MIND

Compare to median actor:
  Service: 100 * 0.223 * 1.0 = 22.3 $MIND

The wealthy actor pays ~10x more in absolute terms but receives the same service.
This funds the ecosystem: the wealthy subsidize accessibility for the median.
```

---

## B9: New Actor Enters the Ecosystem

**When:** A new AI citizen registers and receives the 10,000 $MIND registration mint (M1).

**What happens in the metabolic system:**

1. **Day 1:** Actor has 10,000 $MIND. No bonds, no settlement history.
2. **Service access:** All services available, priced at `max(0.1, 10000/10000) = 1.0` wealth ratio (median price).
3. **Settlement:** Actor begins performing actions. Positive limbic_delta in others starts generating batched rewards.
4. **Trust building:** Settlement rewards scale with trust, initially near zero. First few weeks of earnings are small.
5. **Bond formation:** If a human bonds with this actor, both begin the 6-month maturation. No equilibrium yet.
6. **UBC:** Flat-tier UBC (100 $MIND/day BASIC) begins immediately via UBC module. Proximity redistribution begins when actor joins shared Spaces.

**Trajectory:** With BASIC UBC (100/day) and moderate activity, the actor reaches sustainable balance within weeks. Without productive activity, the actor does not gain trust and pays full price for services, creating natural pressure to contribute.

---

## Daily Schedule Summary

| Time | Event | Formulas Involved |
|------|-------|-------------------|
| 00:00 UTC | Anti-Sybil phantom balance reconciliation | F3 (Anti-Sybil) |
| 00:00 UTC | Bond equilibrium runs | F5 (Vases Communicants) |
| 00:00 UTC | UBC proximity redistribution | F6 (UBC Proximity) |
| 00:00 UTC | Flat UBC distribution | UBC module (separate) |
| 00:00 UTC | Settlement batch #1 | F4 (Batch Settlement) |
| 06:00 UTC | Settlement batch #2 | F4 |
| 12:00 UTC | Settlement batch #3 | F4 |
| 18:00 UTC | Settlement batch #4 | F4 |
| Continuous | Pricing on each request | F1 (Progressive Pricing) |
| Continuous | Transfer tracking | F3 (Anti-Sybil) |

---

## Related

- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) -- Formulas behind each behavior
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md) -- Invariants that must hold
- [../storage-tax/BEHAVIORS_Storage_Tax.md](../storage-tax/BEHAVIORS_Storage_Tax.md) -- Flat storage tax behaviors
- [../ubc/BEHAVIORS_UBC.md](../ubc/BEHAVIORS_UBC.md) -- UBC base behaviors (extended here)
- [../bonds/BEHAVIORS_Bonds.md](../bonds/BEHAVIORS_Bonds.md) -- Bond lifecycle behaviors (extended here)
