# ALGORITHM -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | ALGORITHM |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Overview

Daily computation of storage tax on idle balances, with order-book valuation and UBC redistribution. The algorithm runs once per epoch (1 epoch = 1 day) and processes all wallets in the system.

## Data Structures

```
WalletState:
  address: str
  balance: float
  last_activity: datetime        # timestamp of last outgoing transaction
  idle_balance: float            # portion not moved in 30+ days
  taxable_value: float           # order-book valuation of held assets

TaxResult:
  storage_tax: float             # 1%/yr computed daily
  dormancy_decay: float          # 0.5%/mo after 30d grace
  total_deducted: float
  destination: str               # UBC redistribution pool address

OrderBookEntry:
  order_id: str
  side: str                      # 'buy' or 'sell'
  amount: float
  price: float
  is_staked: bool
  stake_amount: float            # collateral locked (min 10% of order value)
  auto_execute: bool             # must be true for valid staked orders

TaxEpoch:
  epoch_id: int
  date: date
  total_collected: float
  wallets_taxed: int
  wallets_exempt: int            # active wallets (not exempt by privilege -- by activity)
  ubc_pool_balance: float        # available for next distribution
```

@mind:TODO -- Define token-batch tracking structure for per-deposit idle detection (FIFO/LIFO decision pending).

## Algorithm: compute_daily_tax(wallet)

```
FUNCTION compute_daily_tax(wallet: WalletState) -> TaxResult:

  Step 1: Determine idle_balance
    days_since_activity = (now - wallet.last_activity).days
    IF days_since_activity < 30:
      idle_balance = 0  # within grace period, no dormancy
      # But annual storage tax still applies to full balance
      # @mind:TODO -- Decide: does annual 1% apply during grace period or only after?
    ELSE:
      idle_balance = wallet.balance  # entire balance is idle

  Step 2: Compute annual storage tax (daily portion)
    daily_rate = 0.01 / 365  # 1% annual, divided into daily increments
    storage_tax = wallet.balance * daily_rate
    # Note: applies to full balance, not just idle portion
    # Rationale: even "active" wallets holding excess reserves should feel pressure

  Step 3: Compute dormancy decay (if applicable)
    IF days_since_activity > 30:
      monthly_rate = 0.005  # 0.5% per month
      daily_dormancy_rate = monthly_rate / 30
      dormancy_decay = idle_balance * daily_dormancy_rate
    ELSE:
      dormancy_decay = 0

  Step 4: Compute total deduction
    total_deducted = storage_tax + dormancy_decay

  Step 5: Apply deduction
    IF total_deducted > wallet.balance:
      total_deducted = wallet.balance  # cannot go negative
    wallet.balance -= total_deducted
    ubc_pool.balance += total_deducted

  Step 6: Record audit trail
    EMIT TaxEvent(
      wallet=wallet.address,
      epoch=current_epoch,
      storage_tax=storage_tax,
      dormancy_decay=dormancy_decay,
      total_deducted=total_deducted,
      remaining_balance=wallet.balance,
      days_idle=days_since_activity,
      timestamp=now
    )

  RETURN TaxResult(storage_tax, dormancy_decay, total_deducted, UBC_POOL_ADDRESS)
```

## Algorithm: compute_order_book_value(asset)

```
FUNCTION compute_order_book_value(asset: str) -> float:

  Step 1: Fetch all open buy orders with valid stake
    staked_orders = [
      order for order in get_open_orders(asset)
      if order.is_staked
      and order.side == 'buy'
      and order.auto_execute == True
    ]

  Step 2: Verify stake ratio for each order
    valid_orders = []
    FOR order IN staked_orders:
      stake_ratio = order.stake_amount / (order.amount * order.price)
      IF stake_ratio >= 0.10:  # minimum 10% collateral
        valid_orders.append(order)
      ELSE:
        EMIT InvalidStakeWarning(order.order_id, stake_ratio)

  Step 3: Compute weighted value
    total_committed = sum(
      order.amount * order.price * (order.stake_amount / (order.amount * order.price))
      for order in valid_orders
    )

  Step 4: Normalize by supply held
    total_supply_held = get_total_supply_held(asset)
    IF total_supply_held == 0:
      RETURN 0  # no supply, no value

    order_book_value = total_committed / total_supply_held

  Step 5: Return taxable value
    RETURN order_book_value
```

@mind:TODO -- Define fallback valuation when order book is too thin (< N orders or < X% of supply represented).

## Algorithm: run_epoch(epoch_id)

```
FUNCTION run_epoch(epoch_id: int) -> TaxEpoch:

  Step 1: Get all wallets with non-zero balance
    wallets = get_all_wallets(min_balance=DUST_THRESHOLD)
    # @mind:TODO -- Define DUST_THRESHOLD (balances too small to tax meaningfully)

  Step 2: Compute tax for each wallet
    results = []
    FOR wallet IN wallets:
      result = compute_daily_tax(wallet)
      results.append(result)

  Step 3: Aggregate epoch results
    epoch = TaxEpoch(
      epoch_id=epoch_id,
      date=today(),
      total_collected=sum(r.total_deducted for r in results),
      wallets_taxed=count(r for r in results if r.total_deducted > 0),
      wallets_exempt=count(r for r in results if r.total_deducted == 0),
      ubc_pool_balance=get_ubc_pool_balance()
    )

  Step 4: Emit epoch summary
    EMIT EpochComplete(epoch)

  RETURN epoch
```

## Key Decisions

### D1: 1% Annual vs Higher Rate

```
CHOSEN: 1% annual + 0.5%/month dormancy
WHY: Gentle enough to not penalize short holds, severe enough to make
     long-term hoarding irrational.
     Combined effect over 1 year of total inactivity: ~7% (1% + 6x0.5%)
ALTERNATIVES CONSIDERED:
  - 2% annual: Too aggressive for new users holding while learning
  - 0.5% annual: Too gentle, insufficient UBC funding pressure
  - Flat 1% with no dormancy escalation: Doesn't differentiate
    short-term holders from chronic hoarders
```

### D2: Grace Period 30 Days

```
CHOSEN: 30-day grace before dormancy kicks in
WHY: Allows normal operational float without penalty.
     Short enough to prevent strategic "just-in-time" movement gaming.
ALTERNATIVES CONSIDERED:
  - 7 days: Too aggressive, penalizes normal usage patterns
  - 90 days: Too generous, allows quarterly "activity ping" gaming
  - Dynamic (based on wallet history): Too complex for initial implementation
```

### D3: Order-Book Valuation Over Last-Trade

```
CHOSEN: Staked order book depth for taxable value
WHY: Last-trade price is trivially manipulable via wash trading.
     Order-book with stake requirements makes manipulation expensive.
ALTERNATIVES CONSIDERED:
  - TWAP (time-weighted average price): Better than spot but still manipulable
  - Oracle-based: Centralization risk, single point of failure
  - Multi-source median: Complex, still relies on trade prices
```

### D4: Universal Application (No Exemptions)

```
CHOSEN: All wallets pay storage tax, including protocol treasury
WHY: Exemptions create political pressure and gaming incentives.
     Protocol treasury paying tax ensures it deploys capital productively.
ALTERNATIVES CONSIDERED:
  - Treasury exemption: Creates perverse incentive to park funds in treasury
  - Graduated rates by wallet size: Complexity, boundary gaming
  - DAO-voted exemptions: Political capture risk
```

@mind:TODO -- Decision needed: Should storage tax rate be governable (DAO vote) or fixed in protocol? Fixed prevents capture but reduces adaptability.
