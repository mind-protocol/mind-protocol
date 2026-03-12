# VALIDATION -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | VALIDATION |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Invariants

### V1: Universal Application (CRITICAL)

```
MUST: Storage tax applies to ALL wallets -- no exceptions
NEVER: Admin wallets, treasury, or VIP accounts exempted
```

**Rationale**: The moment any wallet class is exempt, political pressure to expand exemptions follows. The protocol treasury paying tax on idle reserves is a feature: it forces productive deployment of protocol-owned capital.

**Test**: For every epoch, assert that `wallets_taxed + wallets_exempt == total_wallets_with_balance` and that `wallets_exempt` contains only wallets within the 30-day grace period (never wallets exempt by identity or role).

@mind:TODO -- Write formal property test: no wallet address appears in an exemption list.

### V2: Order-Book Integrity (CRITICAL)

```
MUST: Taxable value computed from staked order book only
NEVER: Last-trade price used for tax computation
```

**Rationale**: Last-trade price is trivially manipulable. Two colluding wallets can wash-trade at any price with near-zero cost. Order-book valuation with 10% stake requirement makes manipulation proportionally expensive.

**Test**: Assert that `compute_order_book_value()` never calls `get_last_trade_price()`. Assert that all orders included in valuation have `is_staked == True` and `stake_ratio >= 0.10`.

### V3: UBC Funding Sufficiency (HIGH)

```
MUST: Storage tax revenue covers at minimum Basic tier UBC for all citizens
NEVER: UBC distribution exceeds available tax + treasury funds
```

**Rationale**: The storage tax exists primarily to fund UBC. If tax revenue is insufficient, the system is either too lenient (rates too low) or too successful (not enough idle capital -- a good problem). The protocol must never distribute more than it collects plus treasury reserves.

**Test**: For every distribution epoch, assert `distribution_total <= ubc_pool_balance + treasury_reserve_allocated`. If `distribution_total > tax_revenue_trailing_30d`, emit alert for rate review.

@mind:TODO -- Define "Basic tier UBC" quantitatively. What is the minimum compute allocation per citizen per epoch?

### V4: Grace Period Honored (HIGH)

```
MUST: No dormancy penalty before 30 days of inactivity
NEVER: Active wallets penalized by storage tax dormancy component
```

**Rationale**: The grace period is a social contract: reasonable operational float is not penalized. Breaking this contract would punish normal usage patterns and erode trust.

**Test**: For every `TaxResult` where `dormancy_decay > 0`, assert `days_since_last_activity > 30`. For every wallet with `last_activity < 30 days ago`, assert `dormancy_decay == 0`.

### V5: Audit Trail (MEDIUM)

```
MUST: Every tax deduction recorded with timestamp, amount, source, destination
NEVER: Tax applied without traceable record
```

**Rationale**: Transparency is non-negotiable. Every participant must be able to verify exactly how much tax was deducted, when, and where it went. This is both a trust mechanism and a debugging tool.

**Test**: For every epoch, assert `count(TaxEvents) == wallets_taxed`. For every `TaxEvent`, assert all fields are non-null: `wallet`, `epoch`, `storage_tax`, `dormancy_decay`, `total_deducted`, `remaining_balance`, `timestamp`.

@mind:TODO -- Define retention policy for tax event history. On-chain permanent? Off-chain with merkle proof?

### V6: Balance Non-Negativity (CRITICAL)

```
MUST: Wallet balance never goes below zero after tax deduction
NEVER: Tax deduction exceeds current balance
```

**Rationale**: Arithmetic invariant. A wallet with 0.001 tokens cannot have 0.002 deducted. The tax computation must clamp to available balance.

**Test**: For every `TaxResult`, assert `total_deducted <= pre_tax_balance`. For every wallet post-epoch, assert `balance >= 0`.

### V7: Epoch Consistency (HIGH)

```
MUST: Each wallet is taxed exactly once per epoch
NEVER: Double-taxation within a single epoch or skipped wallets
```

**Rationale**: The daily computation must be idempotent within an epoch. Re-running the same epoch must produce identical results (or be rejected as already-processed).

**Test**: For every epoch, assert `count(distinct wallet in TaxEvents) == wallets_taxed`. Assert no duplicate `(wallet, epoch)` pairs in the event log.

@mind:TODO -- Define recovery procedure if epoch computation fails mid-way (partial application). Rollback? Resume?

### V8: Rate Bounds (MEDIUM)

```
MUST: Storage tax rate stays within [0.5%, 2.0%] annual
MUST: Dormancy rate stays within [0.25%, 1.0%] monthly
NEVER: Rates changed without governance process (if governable)
```

**Rationale**: Even if rates become governable, hard bounds prevent capture scenarios where a majority votes to zero out the tax (killing UBC funding) or spike it (confiscatory attack on minority holders).

@mind:TODO -- Confirm whether rates are fixed in protocol or governable with bounds. See ALGORITHM D-decision pending.
