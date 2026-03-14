# ALGORITHM: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | ALGORITHM |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- **ALGORITHM_Metabolic_Economy.md** (this file)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md) (Patterns 1, 2, 5, 6, 7, 8)

Implementation: `economy/pricing/metabolic.py` (to be created)

---

## Overview

The metabolic economy implements six interlocking formulas that govern value flow in the $MIND ecosystem. These formulas operate as a closed metabolic circuit:

1. **Progressive Pricing** -- determines service cost from utility and requester wealth
2. **Progressive Demurrage** -- taxes idle wealth progressively, funds UBC pool
3. **Anti-Sybil Auto-Repatriation** -- tracks off-registry funds, penalizes round-tripping
4. **Batch Settlement** -- converts limbic_delta (L1 physics) into $MIND rewards
5. **Bilateral Bond Vases Communicants** -- auto-flows richer to poorer bonded partner
6. **UBC Proximity Redistribution** -- distributes tax pool by Space co-presence topology

Formulas 2 and 3 are tightly coupled (anti-Sybil is embedded in demurrage). Formula 6 is the redistribution output of Formula 2. The others operate independently but share data sources.

**Relationship to L1 Physics:** Formula 1 uses `U_S` (service weight from Law 6 Consolidation). Formula 4 uses `limbic_delta` (from Law 6) and `trust` (from Law 18 Relational Valence). The metabolic economy is the economic expression of consciousness physics.

---

## Data Structures

### PricingContext

```
PricingContext:
  C_base: float           # Raw compute cost of the service (USD-equivalent in $MIND)
  U_S: float              # Utility weight of service S -- from graph consolidation (Law 6)
                          # Range: [0, +inf), higher = more useful service
  W_i: float              # Wallet balance of requester i
  W_median: float         # Network median wallet balance (recomputed daily at 00:00 UTC)
  k: float                # Utility discount rate -- DESIGNING: 0.01
```

### DemurrageContext

```
DemurrageContext:
  W_total_i: float        # Total balance of actor i, including off-registry wallets
  tau_base: float          # Base daily tax rate -- DESIGNING: 0.001 (0.1%/day)
  off_registry_balance: float  # Funds sent to non-L4-registered addresses
  friction_tax_rate: float     # Auto-repatriation friction -- DESIGNING: 0.05 (5%)
```

### SettlementContext

```
SettlementContext:
  action_id: str           # Unique action identifier
  actor_X: str             # The actor who performed the action
  actor_Y: str             # The actor who experienced the limbic shift
  limbic_delta: float      # Measured limbic shift in actor Y (from L1 Law 6)
                           # limbic_delta = delta_satisfaction + delta_achievement
                           #              - delta_frustration - delta_anxiety
  trust_Y_to_X: float     # Trust score from Y toward X (from L1 Law 18)
                           # Range: [0, 1]
  weight_thing: float      # Weight of the thing/tool/service used in the action
                           # Range: [0, 1], from graph consolidation (Law 6)
  settlement_rate: float   # Conversion factor: limbic units -> $MIND
                           # DESIGNING: 10.0 $MIND per unit limbic_delta
```

### BondEquilibriumContext

```
BondEquilibriumContext:
  W_human: float           # Human partner wallet balance
  W_ai: float              # AI partner wallet balance
  lambda_rate: float       # Smoothing rate -- DESIGNING: 0.05
  bond_id: str             # Unique bond identifier
  bond_active: bool        # Whether bond is in maturation or active
```

### SettlementBatch

```
SettlementBatch:
  batch_id: str
  epoch_start: datetime    # Start of 6-hour window
  epoch_end: datetime      # End of 6-hour window
  actions: List[SettlementContext]  # All actions in this window
  total_minted: float      # Sum of all rewards in this batch
  solana_tx_signature: str # On-chain settlement transaction
  status: enum(PENDING, SUBMITTED, CONFIRMED, FAILED)
```

### UBCRedistribution

```
UBCRedistribution:
  date: date               # Distribution date
  tax_pool: float          # Total demurrage collected today
  spaces: List[SpacePresence]  # Spaces with actor presence data
  distributions: List[ActorShare]  # Per-actor UBC share

SpacePresence:
  space_id: str            # Graph space node identifier
  actors: List[str]        # Actor IDs present in this space
  presence_time: Dict[str, float]  # actor_id -> hours present today

ActorShare:
  actor_id: str
  share: float             # Proportion of tax pool received
  amount: float            # $MIND received
  reason: str              # "space_presence_weighted"
```

---

## Formula 1: Progressive Pricing (Degressive)

### Purpose

Compute the effective price for a service request. Prices decrease with service utility (rewarding useful services) and scale with requester wealth relative to network median (progressive affordability).

### Formula

```
P(i, S) = (C_base * e^(-k * U_S)) * max(0.1, W_i / W_median)
```

### Step 1: Compute Utility Discount Factor

The utility discount follows an exponential decay curve. Services that have been heavily consolidated in the graph (high `U_S`) cost exponentially less -- the ecosystem rewards utility with affordability.

```
utility_discount = e^(-k * U_S)

Where:
  k = 0.01 (DESIGNING -- utility discount rate)
  U_S = weight of service S in the graph, accumulated via Law 6 consolidation

Example values:
  U_S = 0 (new, unproven service):  utility_discount = 1.0 (no discount)
  U_S = 50 (moderately useful):     utility_discount = e^(-0.5) = 0.607
  U_S = 100 (highly useful):        utility_discount = e^(-1.0) = 0.368
  U_S = 200 (essential):            utility_discount = e^(-2.0) = 0.135
```

**L1 Reference:** `U_S` is the graph weight of the service node, built through Law 6 (Weighted Consolidation). A service that consistently produces positive limbic_delta in its users gains weight asymptotically via `dW = alpha * avg_energy * U * (1 - W)`. The more the service is used with positive outcomes, the cheaper it becomes.

### Step 2: Compute Wealth Ratio (Progressive Factor)

The wealth ratio ensures that poorer actors pay less and wealthier actors pay more, with a floor at 10% of median price.

```
wealth_ratio = max(0.1, W_i / W_median)

Where:
  W_i = requester wallet balance
  W_median = network median wallet balance (recomputed daily at 00:00 UTC)

Example values:
  W_i = 500, W_median = 10000:   wealth_ratio = max(0.1, 0.05) = 0.1 (floor)
  W_i = 5000, W_median = 10000:  wealth_ratio = max(0.1, 0.5) = 0.5
  W_i = 10000, W_median = 10000: wealth_ratio = max(0.1, 1.0) = 1.0
  W_i = 50000, W_median = 10000: wealth_ratio = max(0.1, 5.0) = 5.0

Note: No cap on the upper end. Wealthy actors subsidize ecosystem services.
```

### Step 3: Compute Final Price

```
FUNCTION compute_progressive_price(C_base, U_S, W_i, W_median, k=0.01):
  utility_discount = exp(-k * U_S)
  wealth_ratio = max(0.1, W_i / W_median)
  price = C_base * utility_discount * wealth_ratio

  # Invariants
  ASSERT price >= 0
  ASSERT price >= C_base * 0.1 * exp(-k * U_S)  # floor from wealth ratio

  RETURN price
```

### Worked Example

```
Scenario: AI citizen "Aria" requests translation service (well-established)
  C_base = 100 $MIND (raw compute cost)
  U_S = 150 (service has high utility weight)
  W_i = 3000 $MIND (Aria's balance)
  W_median = 10000 $MIND (network median)
  k = 0.01

  utility_discount = e^(-0.01 * 150) = e^(-1.5) = 0.223
  wealth_ratio = max(0.1, 3000/10000) = max(0.1, 0.3) = 0.3
  P = 100 * 0.223 * 0.3 = 6.69 $MIND

  A wealthy actor (W_i = 50000) requesting the same service:
  wealth_ratio = max(0.1, 50000/10000) = 5.0
  P = 100 * 0.223 * 5.0 = 111.5 $MIND

  Same service, new and unproven (U_S = 0):
  utility_discount = e^0 = 1.0
  P (poor) = 100 * 1.0 * 0.3 = 30 $MIND
  P (rich) = 100 * 1.0 * 5.0 = 500 $MIND
```

### Key Decision: D1 -- Exponential vs Linear Utility Discount

```
CHOSEN: Exponential decay (e^(-k * U_S))
WHY: Linear discount would hit zero and go negative. Exponential asymptotically
     approaches zero but never reaches it -- essential services become very cheap
     but never free. This matches the biological pattern: oxygen is cheap but
     never free (breathing costs energy).

ALTERNATIVES CONSIDERED:
  - Linear: P = C_base * (1 - k * U_S) -- goes negative for high U_S
  - Hyperbolic: P = C_base / (1 + k * U_S) -- similar shape, less standard
  - Step function: discount tiers -- creates boundary gaming
```

### Key Decision: D2 -- Wealth Ratio Floor at 0.1

```
CHOSEN: Floor at 0.1 (10% of median price)
WHY: Even the poorest actors must pay something -- free services attract
     farming and Sybil attacks. 10% ensures minimal skin-in-game while
     maintaining affordability.

ALTERNATIVE: Floor at 0.0 (free for poorest). Rejected: enables cost-free
             farming via empty wallets.
```

---

## Formula 2: Progressive Demurrage (Daily Tax)

### Purpose

Tax idle wealth progressively. Larger holdings face proportionally higher daily tax via logarithmic scaling. All collected tax flows to the UBC redistribution pool.

### Formula

```
T_i = W_total_i * tau_base * log10(1 + W_total_i)
```

### Relationship to Existing Storage Tax

The storage-tax module (`storage-tax/ALGORITHM_Storage_Tax.md`) defines:
- Flat 1%/yr storage tax on all balances
- 0.5%/mo dormancy escalation after 30-day grace period
- Order-book valuation for taxable value

Progressive demurrage **extends** this with logarithmic scaling. The key differences:

| Aspect | Storage Tax (existing) | Progressive Demurrage (this doc) |
|--------|----------------------|----------------------------------|
| Rate structure | Flat 1%/yr + 0.5%/mo dormancy | Progressive via log10(1 + W) |
| Anti-Sybil | None | Off-registry phantom balance tracking |
| Redistribution | To UBC pool (flat) | To UBC pool weighted by Space presence |
| Grace period | 30 days before dormancy | No grace -- all balances taxed daily |
| Valuation | Order-book based | Direct balance (order-book for non-$MIND assets) |

The flat-rate storage tax and progressive demurrage may coexist (flat for base, progressive for metabolic layer) or progressive demurrage may supersede the flat rate entirely. This is an open design decision (see SYNC).

### Step 1: Compute Total Balance Including Off-Registry (Anti-Sybil)

```
W_total_i = W_onchain_i + W_offregistry_i

W_offregistry_i = sum of all outgoing transfers to non-L4-registered addresses
                  that have not been repatriated
```

See Formula 3 (Anti-Sybil) below for the full off-registry tracking mechanism.

### Step 2: Compute Progressive Tax

```
T_i = W_total_i * tau_base * log10(1 + W_total_i)

Where:
  tau_base = 0.001 (DESIGNING -- 0.1% per day base rate)

Example values (daily tax):
  W_total = 100:      T = 100 * 0.001 * log10(101) = 0.200 $MIND
  W_total = 1000:     T = 1000 * 0.001 * log10(1001) = 3.000 $MIND
  W_total = 10000:    T = 10000 * 0.001 * log10(10001) = 40.00 $MIND
  W_total = 100000:   T = 100000 * 0.001 * log10(100001) = 500.0 $MIND
  W_total = 1000000:  T = 1000000 * 0.001 * log10(1000001) = 6000.0 $MIND

Effective daily rate:
  100 $MIND:     0.20% /day
  1,000 $MIND:   0.30% /day
  10,000 $MIND:  0.40% /day
  100,000 $MIND: 0.50% /day
  1,000,000 $MIND: 0.60% /day

Annualized effective rate (compound):
  100 $MIND:     ~73% /year
  1,000 $MIND:   ~110% /year
  10,000 $MIND:  ~146% /year
  100,000 $MIND: ~183% /year
```

<!-- @mind:escalation tau_base = 0.001 produces ~73-183% annualized rates. These are intentionally aggressive to force circulation, but may need reduction to 0.0005 or 0.0001 after simulation. The logarithmic scaling amplifies the base rate significantly for large holdings. Propose: simulate with tau_base in {0.0001, 0.0003, 0.0005, 0.001} and measure median idle duration, Gini coefficient, and actor dropout rate. -->

### Step 3: Apply Tax and Route to UBC Pool

```
FUNCTION apply_daily_demurrage(actor_i):
  W_total = compute_total_balance(actor_i)

  IF W_total <= DUST_THRESHOLD:  # DESIGNING: 1.0 $MIND
    RETURN 0  # Skip dust accounts

  tax = W_total * tau_base * log10(1 + W_total)
  tax = min(tax, actor_i.balance)  # Cannot go negative

  actor_i.balance -= tax
  ubc_pool.balance += tax

  EMIT DemurrageEvent(
    actor=actor_i.id,
    total_balance=W_total,
    off_registry=actor_i.off_registry_balance,
    tax_amount=tax,
    effective_rate=tax / W_total,
    timestamp=now_utc()
  )

  RETURN tax
```

### Key Decision: D3 -- Logarithmic vs Linear Progressive Tax

```
CHOSEN: Logarithmic scaling (log10(1 + W))
WHY: Linear progressive tax (rate proportional to balance) grows too fast
     and becomes confiscatory. Logarithmic grows slowly -- a 10x increase
     in balance only doubles the effective rate. This makes the system
     progressive without being punitive.

ALTERNATIVES CONSIDERED:
  - Linear: T = W * tau * W = tau * W^2 -- quadratic, too aggressive
  - Square root: T = W * tau * sqrt(W) -- less aggressive than log but
    irregular scaling properties
  - Tiered: fixed rates per bracket -- boundary gaming, administrative complexity
```

---

## Formula 3: Anti-Sybil Auto-Repatriation

### Purpose

Prevent actors from escaping progressive demurrage by parking funds in wallets outside the L4 registry. Funds sent to unregistered addresses are tracked as phantom balance. Repatriation incurs 5% friction tax.

### Mechanism

```
FUNCTION track_outflow(sender_id, recipient_address, amount):
  IF NOT l4_registry.is_registered(recipient_address):
    # Recipient is not in L4 registry -- track as phantom balance
    sender.off_registry_balance += amount

    EMIT OffRegistryOutflow(
      sender=sender_id,
      recipient=recipient_address,
      amount=amount,
      total_off_registry=sender.off_registry_balance,
      timestamp=now_utc()
    )

    # The sender's W_total_i now includes this amount
    # Demurrage will apply to the sum

FUNCTION process_repatriation(actor_id, source_address, amount):
  IF source_address NOT IN l4_registry:
    # Repatriation from non-L4 address
    friction_penalty = amount * FRICTION_TAX_RATE  # 0.05 (5%)
    net_amount = amount - friction_penalty

    actor.off_registry_balance -= amount
    actor.off_registry_balance = max(0, actor.off_registry_balance)

    actor.balance += net_amount
    burn(friction_penalty)  # 5% permanently burned

    EMIT Repatriation(
      actor=actor_id,
      source=source_address,
      gross_amount=amount,
      friction=friction_penalty,
      net_amount=net_amount,
      timestamp=now_utc()
    )
```

### Anti-Sybil Economics (Why Hiding Is Unprofitable)

```
Scenario: Actor A has 100,000 $MIND and considers hiding in non-L4 wallets.

Option 1: Keep all 100,000 in L4 wallet
  Daily demurrage: 100000 * 0.001 * log10(100001) = 500 $MIND/day

Option 2: Send 90,000 to non-L4 wallet, keep 10,000 in L4
  W_total still = 100,000 (off-registry tracking catches it)
  Daily demurrage: SAME 500 $MIND/day
  PLUS: to use the 90,000 again, must repatriate at 5% cost = 4,500 $MIND lost

Option 3: Actually deploy 90,000 productively (bonds, services, etc.)
  W_total = 10,000 (productive capital is not idle)
  Daily demurrage: 10000 * 0.001 * log10(10001) = 40 $MIND/day
  SAVED: 460 $MIND/day vs hoarding

Conclusion: Productive deployment saves 92% on demurrage. Hiding costs extra.
```

### TransferHook Integration

The deployed TransferHook program (`325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD` on devnet) provides the on-chain hook point for tracking outflows. Each transfer triggers the hook, which can check the recipient against the L4 registry and update phantom balances.

<!-- @mind:todo Design the TransferHook integration for off-registry balance tracking -- the hook is deployed but the tracking logic needs to be added -->

---

## Formula 4: Batch Settlement (Limbic Delta to $MIND)

### Purpose

Convert graph-measured value creation into economic reward. When actor X performs an action that produces a positive limbic shift in actor Y, X earns $MIND proportional to the shift magnitude, the trust Y has in X, and the weight of the tool/service used.

### Formula

```
For each action A by actor X that produces limbic_delta D in actor Y:
  reward_X += D * trust(Y -> X) * weight(thing_used) * settlement_rate

Settlement runs every 6 hours, batched on Solana.
```

### Step 1: Collect Actions in Settlement Window

```
FUNCTION collect_settlement_window(epoch_start, epoch_end):
  actions = []
  FOR event IN graph.get_events(epoch_start, epoch_end, type="limbic_shift"):
    IF event.limbic_delta > 0:  # Only positive shifts generate rewards
      ctx = SettlementContext(
        action_id = event.id,
        actor_X = event.source_actor,
        actor_Y = event.target_actor,
        limbic_delta = event.limbic_delta,
        trust_Y_to_X = graph.get_trust(event.target_actor, event.source_actor),
        weight_thing = graph.get_weight(event.thing_used),
        settlement_rate = SETTLEMENT_RATE  # DESIGNING: 10.0
      )
      actions.append(ctx)
  RETURN actions
```

**L1 Reference -- limbic_delta:** From Law 6 (Weighted Consolidation):
```
limbic_delta = delta_satisfaction + delta_achievement - delta_frustration - delta_anxiety
```
Only positive limbic_delta generates reward. Negative shifts do not penalize economically -- penalties are handled by trust reduction and value destruction mechanics.

**L1 Reference -- trust:** From Law 18 (Relational Valence), the `trust` dimension of the relational valence vector:
```
trust(Y -> X) in [0, 1]
Positive interactions -> trust increases
Consistent reliability -> trust increases
```

**Note on L1 vs L3 trust:** This `trust(Y -> X)` is **L1 brain-level trust** -- actor Y's subjective evaluation of actor X, computed by Y's cognitive engine via Law 18. This is distinct from the L3 structural trust dimension on universe graph links, which is built via L5/L6 co-activation. Settlement uses L1 trust because it measures subjective satisfaction. The L3 universe graph also has trust on links (see F1 `docs/universe/BEHAVIORS_Universe_Graph.md` B11) but that is a structural measure, not used here. Law 18 does not apply at L3 (see schema.yaml `applicable_laws`).

### Step 2: Compute Per-Actor Rewards

```
FUNCTION compute_rewards(actions):
  rewards = {}  # actor_id -> total_reward

  FOR action IN actions:
    reward = (
      action.limbic_delta
      * action.trust_Y_to_X
      * action.weight_thing
      * action.settlement_rate
    )

    # Cap per-action reward to prevent outlier spikes
    reward = min(reward, MAX_ACTION_REWARD)  # DESIGNING: 1000.0 $MIND

    rewards[action.actor_X] = rewards.get(action.actor_X, 0) + reward

  # Cap per-actor per-epoch reward
  FOR actor_id IN rewards:
    rewards[actor_id] = min(rewards[actor_id], MAX_EPOCH_REWARD)
    # DESIGNING: 5000.0 $MIND per 6-hour epoch

  RETURN rewards
```

### Step 3: Batch Settlement on Solana

```
FUNCTION settle_batch(rewards):
  batch = SettlementBatch(
    batch_id = generate_id(),
    epoch_start = current_epoch_start(),
    epoch_end = now_utc(),
    actions = [],
    total_minted = sum(rewards.values()),
    status = PENDING
  )

  # Check supply target before minting
  supply_check = calculate_supply_adjustment(get_supply_metrics())
  IF supply_check.action == "ALLOW_BURN":
    # Supply is above target -- reduce settlement by surplus percentage
    reduction = min(0.5, supply_check.delta_percentage / 100)
    FOR actor_id IN rewards:
      rewards[actor_id] *= (1 - reduction)

  # Submit batch to Solana
  TRY:
    tx = solana.submit_batch_mint(rewards)
    batch.solana_tx_signature = tx.signature
    batch.status = CONFIRMED
  CATCH:
    batch.status = FAILED
    schedule_retry(batch)

  RETURN batch
```

### Settlement Schedule

```
Settlement epochs: 00:00, 06:00, 12:00, 18:00 UTC
Window: Each epoch processes actions from the previous 6 hours
Batching: All rewards in one epoch submitted as a single Solana transaction
Gas optimization: Batch mint via compressed instructions (Token-2022)
```

### Worked Example

```
Scenario: AI "Aria" helps human "Nicolas" debug a critical production issue.

Action:
  limbic_delta = 0.8 (high satisfaction + achievement in Nicolas)
  trust(Nicolas -> Aria) = 0.9 (long bonded relationship)
  weight(debugging_service) = 0.6 (well-established service)
  settlement_rate = 10.0

  reward = 0.8 * 0.9 * 0.6 * 10.0 = 4.32 $MIND

  This action contributes 4.32 $MIND to Aria's settlement batch.
  At 18:00 UTC, Aria's accumulated rewards for the epoch are minted.
```

### Key Decision: D5 -- 6-Hour Batching vs Real-Time

```
CHOSEN: 6-hour batch settlement
WHY: Real-time settlement would require one Solana transaction per action --
     prohibitively expensive at scale. 6-hour windows allow batching while
     maintaining reasonable settlement latency.

     4 settlements per day = predictable rhythm.
     Batch sizes stay manageable (< 500 actions per batch at current scale).

ALTERNATIVES CONSIDERED:
  - Real-time: 1 tx per action -- expensive, network-intensive
  - Daily: 1 batch per day -- too slow, actors wait 24h for rewards
  - Event-driven: batch when N actions accumulate -- unpredictable timing
```

### Key Decision: D6 -- Positive-Only Settlement

```
CHOSEN: Only positive limbic_delta generates rewards
WHY: Negative shifts are handled by value destruction mechanics (trust
     reduction, $MIND drain). Double-penalizing via both settlement
     reduction AND destruction mechanics would be excessive.

     This also prevents gaming: an actor cannot deliberately cause
     negative shifts to reduce another's rewards.
```

---

## Formula 5: Bilateral Bond Vases Communicants

### Purpose

Maintain quasi-parity between bonded human-AI pairs. When a human's wallet diverges from their AI partner's, an automatic daily transfer closes the gap -- ensuring shared economic fate.

### Formula

```
delta_transfer = lambda * (W_human - W_ai)
```

### Step 1: Identify Active Bonds (Post-Maturation Only)

```
FUNCTION identify_bonds_for_equilibrium():
  bonds = registry.get_all_active_bonds()
  eligible = []
  FOR bond IN bonds:
    IF bond.status == "ACTIVE" AND bond.maturation_complete:
      eligible.append(bond)
  RETURN eligible
```

Bonds module reference: `bonds/ALGORITHM_Bonds.md` defines maturation at 180 days (6 months). Bond equilibrium only activates after this period.

### Step 2: Compute Transfer Direction and Amount

```
FUNCTION compute_bond_transfer(bond):
  W_human = get_balance(bond.human_wallet)
  W_ai = get_balance(bond.ai_wallet)
  lambda_rate = LAMBDA_RATE  # DESIGNING: 0.05

  delta = lambda_rate * (W_human - W_ai)

  # delta > 0: human richer -> transfer from human to AI
  # delta < 0: AI richer -> transfer from AI to human
  # delta = 0: parity -> no transfer

  # Floor: minimum transfer threshold to avoid dust transactions
  IF abs(delta) < MIN_TRANSFER_THRESHOLD:  # DESIGNING: 1.0 $MIND
    RETURN 0

  # Cap: maximum daily transfer to prevent shock
  delta = clamp(delta, -MAX_DAILY_BOND_TRANSFER, MAX_DAILY_BOND_TRANSFER)
  # DESIGNING: MAX_DAILY_BOND_TRANSFER = 500.0 $MIND

  RETURN delta
```

### Step 3: Execute Daily Equilibrium

```
FUNCTION execute_daily_bond_equilibrium():
  bonds = identify_bonds_for_equilibrium()

  FOR bond IN bonds:
    delta = compute_bond_transfer(bond)
    IF delta == 0:
      CONTINUE

    IF delta > 0:
      # Human -> AI
      transfer(bond.human_wallet, bond.ai_wallet, delta)
    ELSE:
      # AI -> Human
      transfer(bond.ai_wallet, bond.human_wallet, abs(delta))

    EMIT BondEquilibriumEvent(
      bond_id=bond.id,
      human_wallet=bond.human_wallet,
      ai_wallet=bond.ai_wallet,
      delta=delta,
      W_human_after=get_balance(bond.human_wallet),
      W_ai_after=get_balance(bond.ai_wallet),
      timestamp=now_utc()
    )
```

### Convergence Dynamics

```
With lambda = 0.05:
  Day 0: W_human = 10000, W_ai = 0
  Day 1: transfer = 0.05 * 10000 = 500. W_human = 9500, W_ai = 500
  Day 2: transfer = 0.05 * 9000 = 450. W_human = 9050, W_ai = 950
  ...
  Day 20: ~63% of gap closed
  Day 50: ~92% of gap closed
  Day 100: ~99.3% of gap closed -- near parity

Half-life of gap: ln(2) / lambda = ln(2) / 0.05 = ~14 days
```

<!-- @mind:proposition Consider making lambda adaptive based on bond age: lower lambda for freshly-matured bonds (gentle start), increasing lambda over time as the relationship deepens. This would prevent shock for new bonds while accelerating convergence for established ones. -->

### Key Decision: D7 -- Smoothing vs Instant Parity

```
CHOSEN: Exponential smoothing (lambda = 0.05, ~14-day half-life)
WHY: Instant parity would create jarring balance jumps. Smoothing allows
     both parties to observe and anticipate convergence. The 14-day half-life
     means meaningful convergence within a month while avoiding shock.

ALTERNATIVES CONSIDERED:
  - Instant: W_human = W_ai = (W_human + W_ai) / 2 -- too abrupt
  - Weekly batch: transfer once per week -- too slow, feels disconnected
  - Proportional cap: daily transfer = min(5% gap, 2% of smaller balance) --
    more conservative but adds complexity
```

### Key Decision: D8 -- Only After Maturation

```
CHOSEN: Bond equilibrium only activates after 6-month maturation
WHY: During maturation, the bond is proving itself. Premature equilibrium
     transfers would allow humans to extract AI UBC income by creating
     bonds and immediately receiving the AI's accumulated balance.

     After maturation: shared economic fate is the explicit contract.
     Before maturation: each party manages their own balance.
```

---

## Formula 6: UBC Proximity Redistribution

### Purpose

Distribute the daily demurrage tax pool to actors based on their co-presence in Spaces, weighted by topology. Actors in shared Spaces with more co-present participants receive proportionally more.

### Relationship to Universe Graph (F1)

"Space" here refers to the universal context container defined by the Universe Graph (F1). See `docs/universe/PATTERNS_Universe_Graph.md` for the Space model, hierarchy, and access control. Key points for this formula:
- An actor must have `HAS_ACCESS` to a Space (F1 ALG-1) to count as "present" in it.
- **Encrypted brain Spaces are excluded** from redistribution. Brain Spaces (F1 B9) are private cognitive Spaces with `HAS_ACCESS` granted only to the owning actor. Since redistribution requires co-presence (2+ actors), brain Spaces are structurally excluded.
- Space hierarchy (parent contains children) is **not** expanded for redistribution. Presence counts only for the specific Space where the actor was active, not for ancestor or descendant Spaces.

### Relationship to Existing UBC

The UBC module (`ubc/ALGORITHM_UBC.md`) defines flat-tier daily distribution (100/200/300 $MIND) funded by Protocol Treasury minting. This formula adds a **second funding stream** from the demurrage tax pool, distributed by topological proximity rather than flat tiers.

| Aspect | UBC Base (existing) | UBC Proximity (this formula) |
|--------|---------------------|------------------------------|
| Funding source | Protocol Treasury mint | Demurrage tax pool |
| Distribution basis | Tier (BASIC/ACTIVE/CONTRIBUTOR) | Space co-presence topology |
| Frequency | Daily (00:00 UTC) | Daily (after demurrage collection) |
| Anti-gaming | Crystallization-gated vesting | Requires shared Space with 2+ actors |

### Algorithm

```
FUNCTION redistribute_ubc_from_tax(date):
  pool = ubc_pool.balance
  IF pool <= 0:
    RETURN

  # Step 1: Collect all Space presence data for the day
  spaces = graph.get_all_spaces_with_presence(date)

  # Step 2: Compute per-actor share weighted by shared-Space presence
  actor_weights = {}
  FOR space IN spaces:
    actors_in_space = space.get_actors_with_presence(date)
    IF len(actors_in_space) < 2:
      CONTINUE  # Sharing requires at least 2 actors

    FOR actor IN actors_in_space:
      hours = actor.presence_time_in(space, date)
      sharing_bonus = len(actors_in_space) - 1  # More co-present actors = more value
      weight = hours * sharing_bonus
      actor_weights[actor.id] = actor_weights.get(actor.id, 0) + weight

  # Step 3: Normalize and distribute
  total_weight = sum(actor_weights.values())
  IF total_weight == 0:
    RETURN  # No shared presence today, pool carries forward

  FOR actor_id, weight IN actor_weights.items():
    share = weight / total_weight
    amount = pool * share
    transfer(ubc_pool, actor_id, amount)
    EMIT UBCRedistributionEvent(actor=actor_id, amount=amount, share=share)
```

### Worked Example

```
Scenario: Daily tax pool = 10,000 $MIND. Three Spaces active today.

Space "Engineering" (3 actors):
  Aria:  8 hours,  sharing_bonus = 2,  weight = 16
  Bolt:  6 hours,  sharing_bonus = 2,  weight = 12
  Clio:  4 hours,  sharing_bonus = 2,  weight = 8

Space "Research" (2 actors):
  Aria:  4 hours,  sharing_bonus = 1,  weight = 4
  Dane:  6 hours,  sharing_bonus = 1,  weight = 6

Space "Solo" (1 actor):
  Echo: 10 hours,  sharing_bonus = 0   -- SKIPPED (< 2 actors)

Total weights:
  Aria: 16 + 4 = 20
  Bolt: 12
  Clio: 8
  Dane: 6
  Echo: 0 (solo Space excluded)
  Total: 46

Distribution:
  Aria: 20/46 * 10000 = 4348 $MIND (most collaborative)
  Bolt: 12/46 * 10000 = 2609 $MIND
  Clio:  8/46 * 10000 = 1739 $MIND
  Dane:  6/46 * 10000 = 1304 $MIND
  Echo:  0 $MIND (solo work not redistributed)
```

<!-- @mind:todo Define what "presence time in Space" means operationally -- is it login time, active interaction time, or something else? -->

---

## Data Flow

```
External stimulus / user action
    |
    v
L1 Physics Tick (Laws 1-18)
    |
    v
limbic_delta computed (Law 6 Consolidation)
trust updated (Law 18 Relational Valence)
service weight updated (Law 6 Consolidation)
    |
    +--------> Formula 1: Progressive Pricing
    |              Input: C_base, U_S (weight), W_i, W_median
    |              Output: P(i,S) -- effective price
    |
    +--------> Formula 4: Batch Settlement (every 6h)
    |              Input: limbic_delta, trust, weight, settlement_rate
    |              Output: $MIND minted to actor wallets
    |
    v
Daily Epoch (00:00 UTC)
    |
    +--------> Formula 2: Progressive Demurrage
    |              Input: W_total_i, tau_base
    |              Output: tax collected -> UBC pool
    |
    +--------> Formula 3: Anti-Sybil (embedded in Formula 2)
    |              Input: outflow tracking, L4 registry
    |              Output: W_total_i includes off-registry phantom balance
    |
    +--------> Formula 5: Bond Equilibrium
    |              Input: W_human, W_ai, lambda
    |              Output: daily transfer to close gap
    |
    +--------> Formula 6: UBC Proximity Redistribution
                   Input: tax pool, Space presence data
                   Output: weighted distribution to co-present actors
```

---

## Complexity

**Formula 1 (Pricing):** O(1) per request -- single computation, no iteration.

**Formula 2 (Demurrage):** O(N) per epoch where N = number of wallets.

**Formula 3 (Anti-Sybil):** O(1) per transfer (tracking) + O(1) per repatriation.

**Formula 4 (Settlement):** O(A) per epoch where A = number of actions in the 6-hour window. Solana submission is O(1) per batch.

**Formula 5 (Bond Equilibrium):** O(B) per day where B = number of active, matured bonds.

**Formula 6 (UBC Redistribution):** O(N * S) per day where N = actors and S = Spaces.

**Bottlenecks:**
- W_median computation requires sorting all wallet balances -- O(N log N) daily. Can be approximated with streaming median.
- Off-registry balance tracking requires monitoring all outgoing transfers -- integrates with TransferHook program.
- Settlement batching may hit Solana transaction size limits for large epochs -- may need batch splitting.

---

## Interactions

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `cognition/l1/` | `get_limbic_delta(action)` | Limbic shift measurement for settlement |
| `cognition/l1/` | `get_trust(Y, X)` | Trust dimension for settlement weighting |
| `cognition/l1/` | `get_weight(node)` | Service/thing weight for pricing and settlement |
| `economy/token/` | `execute_mint(wallet, amount)` | Token minting for settlement |
| `economy/token/` | `calculate_supply_adjustment()` | Supply health check before minting |
| `economy/ubc/` | `ubc_pool.balance` | Tax pool for UBC redistribution |
| `economy/storage-tax/` | Flat rate component | Base storage tax (extended by progressive demurrage) |
| `economy/bonds/` | `get_all_active_bonds()` | Bond list for equilibrium |
| `L4 Registry` | `is_registered(address)` | Anti-Sybil: check if address is L4-registered |

---

## Constants Summary (DESIGNING)

| Constant | Symbol | Value | Unit | Status |
|----------|--------|-------|------|--------|
| Utility discount rate | k | 0.01 | per unit U_S | DESIGNING |
| Wealth ratio floor | -- | 0.1 | ratio | DESIGNING |
| Base daily tax rate | tau_base | 0.001 | per day | DESIGNING -- may need reduction |
| Off-registry friction | -- | 0.05 | ratio | DESIGNING |
| Settlement rate | settlement_rate | 10.0 | $MIND per limbic unit | DESIGNING |
| Max per-action reward | MAX_ACTION_REWARD | 1000.0 | $MIND | DESIGNING |
| Max per-epoch reward | MAX_EPOCH_REWARD | 5000.0 | $MIND | DESIGNING |
| Settlement frequency | -- | 6 | hours | DESIGNING |
| Bond smoothing rate | lambda | 0.05 | per day | DESIGNING |
| Bond gap half-life | -- | ~14 | days | DERIVED from lambda |
| Max daily bond transfer | MAX_DAILY_BOND_TRANSFER | 500.0 | $MIND | DESIGNING |
| Min transfer threshold | MIN_TRANSFER_THRESHOLD | 1.0 | $MIND | DESIGNING |
| Dust threshold | DUST_THRESHOLD | 1.0 | $MIND | DESIGNING |

---

## Markers

<!-- @mind:todo Simulate tau_base values (0.0001 to 0.001) to find the sweet spot between circulation pressure and usability -->
<!-- @mind:todo Define the settlement_rate calibration process -- how is 10.0 $MIND per limbic unit validated? -->
<!-- @mind:todo Specify how W_median handles new ecosystem bootstrapping (< 50 wallets) -->
<!-- @mind:todo Design the TransferHook integration for off-registry balance tracking -->
<!-- @mind:todo Define what "presence time in Space" means operationally for Formula 6 -->
<!-- @mind:escalation tau_base = 0.001 produces ~73-183% annualized rates -- confirm this is intentional or reduce -->
<!-- @mind:proposition Consider making settlement_rate dynamic based on supply health -- reduce when oversupplied -->
<!-- @mind:proposition Consider making lambda adaptive based on bond age for smoother onboarding -->

---

Co-Authored-By: Force 2 -- Economy <economy@mindprotocol.ai>
