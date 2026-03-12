# BEHAVIORS -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | BEHAVIORS |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Expected Behaviors

### B1: Idle Capital Decays

```
GIVEN: A wallet holds tokens with no outgoing transactions
WHEN: 30-day grace period expires
THEN: Dormancy decay begins at 0.5% per month
AND: Annual storage tax of 1% applies continuously
```

The combined effect ensures that purely idle capital loses approximately 7% in the first year (1% annual + 6 x 0.5% monthly dormancy after the initial 30-day grace). This rate makes passive holding a demonstrably losing strategy for any yield below ~7%.

@mind:TODO -- Model the exact decay curve including compounding effects (tax is computed on remaining balance, not original).

### B2: Active Capital Is Untaxed By Storage

```
GIVEN: A wallet transacts regularly (at least once per 30 days)
WHEN: Storage tax computation runs
THEN: Only truly idle portions are taxed
AND: Active capital flows freely
```

Activity is defined as any outgoing transaction. Receiving tokens does not reset the idle clock -- only sending demonstrates intentional circulation. The 30-day threshold is per-token-batch: tokens received on day 1 and not moved by day 31 become taxable, even if the wallet sent other tokens on day 15.

@mind:TODO -- Define "per-token-batch" tracking implementation. FIFO vs. LIFO vs. weighted average for determining which tokens are idle.

### B3: Rentier Strategy Becomes Irrational

```
GIVEN: An actor holds capital yielding 1.5% annually
WHEN: Storage tax (1%/yr) + dormancy (0.5%/mo after 30d) applies
THEN: Effective yield is deeply negative
AND: Rational strategy becomes: circulate or lose
```

The inflection point where storage tax exceeds yield depends on activity frequency:
- **Fully idle**: Break-even requires > 7% yield (storage + dormancy)
- **Monthly movement**: Break-even requires > 1% yield (storage only, no dormancy)
- **Weekly movement**: Effectively zero storage tax

This gradient is intentional: it does not require hyperactivity, just regular participation.

### B4: Revenue Funds UBC

```
GIVEN: Storage tax collects from dormant accounts
WHEN: Redistribution cycle runs
THEN: Collected tax flows to UBC distribution pool
AND: Most productive citizens (lowest friction) receive priority funding
```

The redistribution cycle runs daily, matching the daily tax computation. Tax collected in epoch N is available for UBC distribution in epoch N+1. This one-epoch delay prevents circular dependency (taxing and distributing in the same cycle).

@mind:TODO -- Define the redistribution priority algorithm. How does "most productive" map to cascade-utility trust scores?

### B5: Order Book Prevents Tax Gaming

```
GIVEN: An actor tries to inflate asset value to reduce effective tax rate
WHEN: They place fake orders without stake
THEN: Orders without stake are rejected
AND: Only committed liquidity (staked orders) counts for valuation
```

The stake requirement (minimum 10% of order value as collateral) ensures that order-book manipulation is costly. Staked orders must execute automatically on match -- no withdrawal, no bluffing. An actor who inflates the book with staked orders risks execution at those prices.

### B6: Grace Period Resets on Activity

```
GIVEN: A wallet has been idle for 25 days (approaching dormancy threshold)
WHEN: The wallet executes an outgoing transaction
THEN: The 30-day grace period resets to zero
AND: No dormancy decay accrues for the prior idle period
```

Note: The annual 1% storage tax still applies to the idle period (days 1-25), but the escalating dormancy decay (0.5%/mo) does not trigger because the grace period was not exceeded.

@mind:TODO -- Should "dust transactions" (trivially small amounts) count as activity resets? Define minimum transaction threshold to prevent gaming.

---

## Anti-Behaviors

### A1: Tax Movement

```
GIVEN: An active participant transacting frequently
WHEN: Tax computation runs
MUST NOT: Penalize transaction volume
INSTEAD: Only idle balances are taxed
```

This is the fundamental inversion from traditional tax systems. Movement is the healthy state; taxing it would penalize exactly the behavior the protocol wants to encourage. Transaction friction exists (see cascade-utility) but is separate from storage tax and can be negative for trusted actors.

### A2: Last-Trade Valuation

```
GIVEN: Asset valuation for tax purposes
WHEN: Computing taxable value
MUST NOT: Use last trade price (manipulable)
INSTEAD: Use staked order book depth
```

Last-trade price is trivially manipulable: two colluding wallets can wash-trade at any price. Order-book valuation with stake requirements makes manipulation expensive because the attacker must lock real capital as collateral.

### A3: Exempt Privileged Wallets

```
GIVEN: Treasury, admin, or VIP wallet accounts
WHEN: Storage tax computation runs
MUST NOT: Skip or reduce tax for any wallet class
INSTEAD: Apply identical rates universally
```

No exceptions. The protocol treasury itself pays storage tax on idle reserves, creating pressure for the protocol to deploy capital productively. This is not a bug; it is a feature.

### A4: Penalize Receiving

```
GIVEN: A wallet receives tokens from another wallet
WHEN: Determining activity status
MUST NOT: Count incoming transactions as "activity"
INSTEAD: Only outgoing transactions reset idle clock
```

Receiving is passive. An actor who receives airdrops, dividends, or transfers but never sends is still idle from the protocol's perspective. Only outgoing movement demonstrates intentional participation.

@mind:TODO -- Edge case: What about smart contract interactions that are technically "outgoing" but represent passive yield collection (e.g., claiming staking rewards)?
