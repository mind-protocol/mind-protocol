# PATTERNS -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | PATTERNS |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Chain

| File | Purpose |
|------|---------|
| [OBJECTIVES_Storage_Tax.md](./OBJECTIVES_Storage_Tax.md) | Why this module exists |
| [PATTERNS_Storage_Tax.md](./PATTERNS_Storage_Tax.md) | Core patterns and principles (this file) |
| [BEHAVIORS_Storage_Tax.md](./BEHAVIORS_Storage_Tax.md) | Expected and forbidden behaviors |
| [ALGORITHM_Storage_Tax.md](./ALGORITHM_Storage_Tax.md) | Computation logic and data structures |
| [VALIDATION_Storage_Tax.md](./VALIDATION_Storage_Tax.md) | Invariants and constraints |
| [IMPLEMENTATION_Storage_Tax.md](./IMPLEMENTATION_Storage_Tax.md) | Code-level details |
| [HEALTH_Storage_Tax.md](./HEALTH_Storage_Tax.md) | Monitoring and diagnostics |
| [SYNC_Storage_Tax.md](./SYNC_Storage_Tax.md) | Cross-module synchronization state |

---

## The Problem

Traditional economics rewards accumulation. A dollar sitting in a vault for ten years is worth a dollar plus interest -- the system pays you for stillness. This is pathological.

**An organ hoarding blood kills the entire organism.** A thrombosis is not a savings account; it is a clot that starves downstream tissue. The financial equivalent is dormant capital: wealth that produces nothing for the ecosystem while its holder collects rent from scarcity alone.

In Sebastien Deschaux's formulation: *"In physics, energy that doesn't move produces nothing. Stored wealth that doesn't circulate is work sequestered from society."*

The result in traditional systems:
- Top 1% holds 30%+ of capital, most of it idle
- Velocity of money decreases as wealth concentrates
- Productive actors (builders, creators, workers) subsidize the stillness of rentiers
- Speculation via accumulate-wait-dump destabilizes markets

## The Pattern

**Tax storage, not movement.** Two complementary mechanisms:

### 1. Storage Tax (continuous)
- **Rate**: 1% per year on all idle balances
- **Computed**: Daily (idle_balance x 0.01 / 365)
- **Applies to**: Any token balance with no outgoing transaction in 30+ days
- **Destination**: UBC redistribution pool

### 2. Dormancy Decay (escalating)
- **Rate**: Additional 0.5% per month
- **Trigger**: 30-day grace period of zero outgoing transactions
- **Stacks with**: Storage tax (they are additive)
- **Destination**: UBC redistribution pool

### Combined Effect

| Actor Profile | Annual Yield | Effective After Tax | Loss to Tax |
|---------------|-------------|---------------------|-------------|
| Rentier (passive, 1.5%/yr) | 1.5% | ~0.5% (then negative with dormancy) | 66%+ |
| Moderate trader (8%/yr) | 8.0% | ~7.0% | 12.5% |
| Entrepreneur (20%/yr, active) | 20.0% | ~19.0% | 5% |
| Active builder (continuous flow) | N/A | 0% tax (never idle) | 0% |

**Same tax, radically different incentive.** The storage tax is flat, but its effective burden is inversely proportional to activity. This is by design.

## Principles

### P1: Biological Metabolism
Energy (blood, ATP, glucose) must circulate. Static reserves are pathological. The human body stores fat but actively metabolizes it; it does not hoard glucose in a vault. The storage tax is the metabolic rate of the economy -- it ensures reserves are converted to work.

### P2: Tax Immobility, Not Movement
Transaction friction is variable and can even be negative for trusted actors (see cascade-utility). Storage tax is universal. This inverts the traditional model where movement is taxed (sales tax, capital gains) and storage is subsidized (interest, appreciation).

### P3: Order-Book Valuation
Assets are valued on committed liquidity (staked order book), NOT last trade price. This prevents tax gaming via price manipulation.

```python
order_book_value = sum(
    order.amount * order.price
    for order in open_orders
    if order.is_staked and order.side == 'buy'
) / total_supply_held

# Stake requirement: min 10% of order value as collateral
# Orders must execute automatically on match (no bluffing)
taxable_value = order_book_value  # NOT last_trade_price
```

@mind:TODO -- Define edge cases: what happens when order book is thin? Fallback valuation method needed.

### P4: Circular Economy
Storage tax revenue flows to UBC distribution, which flows to active participants, who spend it in the economy, where it generates activity that reduces future storage tax liability. The circle closes.

```
Dormant Capital --[tax]--> UBC Pool --[distribute]--> Active Citizens
     ^                                                      |
     |                                                      |
     +------ [spend / invest / build] <--------------------+
```

## Behaviors Supported

- Capital circulation (money moves, economy lives)
- UBC funding (dormant capital funds universal compute)
- Anti-speculation (hoarding is a losing strategy)
- Productive investment (builders pay effectively zero tax)

## Behaviors Prevented

- Hoarding (mathematically irrational beyond 30 days)
- Price manipulation via last-trade gaming (order-book valuation)
- Dead capital (every token must justify its stillness)
- Rentier extraction (passive yield becomes negative)

## Dependencies

| Module | Relationship | Why |
|--------|-------------|-----|
| ubc/ | Storage tax funds UBC | Tax revenue is the primary funding source for Universal Basic Compute distribution |
| cascade-utility/ | Complementary friction model | Trust scores affect transaction friction; storage tax handles the immobility side |
| token/ | Implementation substrate | Tax mechanics built on SPL token operations (Token-2022 transfer hooks) |

@mind:TODO -- Clarify interaction with staking mechanisms in token/ module. Staked tokens may need different treatment than idle tokens.
@mind:TODO -- Determine if cascade-utility trust score should modulate storage tax rate (e.g., high-trust actors get longer grace period).
