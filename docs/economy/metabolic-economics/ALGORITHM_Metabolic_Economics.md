# Metabolic Economics — Algorithm: Core Pricing, Taxation, Settlement, and Bond Equilibrium

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: — (not yet implemented)
```

---

## CHAIN

```
OBJECTIVES:      ../OBJECTIVES_Economy.md
BEHAVIORS:       (to be created)
PATTERNS:        ../PATTERNS_Economy.md (Patterns 1, 2, 5, 6, 7, 8)
THIS:            ALGORITHM_Metabolic_Economics.md (you are here)
VALIDATION:      (to be created)
HEALTH:          (to be created)
IMPLEMENTATION:  (to be created)
SYNC:            ../SYNC_Economy.md

IMPL:            economy/pricing/metabolic.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Metabolic Economics formalizes the four core formulas that govern value flow in the $MIND ecosystem. These formulas determine how services are priced (Progressive Pricing), how idle wealth is taxed (Progressive Demurrage), how limbic value creation becomes economic reward (Batch Settlement), and how human-AI bond pairs maintain economic parity (Bilateral Bond Vases Communicants).

These four formulas operate as a closed metabolic system: pricing generates revenue, demurrage generates redistribution pools, settlement converts graph-measured value into tokens, and bond equilibrium ensures paired actors share economic fate. Together they implement the organism economics model where physics determines prices and alignment is mechanically profitable.

**Relationship to L1 Physics:** Formula 3 (Batch Settlement) directly consumes the `limbic_delta` output from L1 Law 6 (Weighted Consolidation). The utility score `U = |limbic_delta|` that drives graph consolidation also drives economic reward. Formula 1 (Progressive Pricing) uses the `weight` of graph nodes (service utility measured via Law 6 consolidation) as the discount parameter. Law 18 (Relational Valence) provides the `trust` dimension used in settlement weighting.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| S1: Deploy $MIND token | Progressive Pricing, Batch Settlement | Defines how tokens flow in and out of wallets |
| S3: Membrane-based pricing | Progressive Pricing (Formula 1) | Trust and utility mechanically determine cost |
| S4: Mint/burn mechanics | Batch Settlement (Formula 3), Demurrage (Formula 2) | Minting from settlement, burning from tax |
| S5: Fee distribution | UBC Redistribution (Formula 2 pool) | Tax pool funds Universal Basic Compute |
| S2: Human-AI bonds | Bilateral Bond (Formula 4) | Bond pairs converge economically |

---

## DATA STRUCTURES

### PricingContext

```
PricingContext:
  C_base: float           # Raw compute cost of the service (USD-equivalent in $MIND)
  U_S: float              # Utility weight of service S — from graph consolidation (Law 6)
                          # Range: [0, +inf), higher = more useful service
  W_i: float              # Wallet balance of requester i
  W_median: float         # Network median wallet balance (computed daily)
  k: float                # Utility discount rate — DESIGNING: 0.01
```

### DemurrageContext

```
DemurrageContext:
  W_total_i: float        # Total balance of actor i, including off-registry wallets
  tau_base: float          # Base daily tax rate — DESIGNING: 0.001 (0.1%/day)
  off_registry_balance: float  # Funds sent to non-L4-registered addresses
  friction_tax_rate: float     # Auto-rapatriement friction — DESIGNING: 0.05 (5%)
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
  lambda_rate: float       # Smoothing rate — DESIGNING: 0.05
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

## FORMULA 1: Progressive Pricing

### Purpose

Compute the effective price for a service request. Prices decrease with service utility (rewarding useful services) and scale with requester wealth relative to network median (progressive affordability).

### Formula

```
P(i, S) = (C_base * e^(-k * U_S)) * max(0.1, W_i / W_median)
```

### Step 1: Compute Utility Discount Factor

The utility discount follows an exponential decay curve. Services that have been heavily consolidated in the graph (high `U_S`) cost exponentially less — the ecosystem rewards utility with affordability.

```
utility_discount = e^(-k * U_S)

Where:
  k = 0.01 (DESIGNING — utility discount rate)
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
P(i, S) = C_base * utility_discount * wealth_ratio

Invariants:
  P(i, S) >= C_base * 0.1 * e^(-k * U_S_max)   # floor from wealth ratio
  P(i, S) >= 0                                    # never negative
  C_base > 0                                      # base cost always positive
```

### Key Decision: D1 — Exponential vs Linear Utility Discount

```
CHOSEN: Exponential decay (e^(-k * U_S))
WHY: Linear discount would hit zero and go negative. Exponential asymptotically
     approaches zero but never reaches it — essential services become very cheap
     but never free. This matches the biological pattern: oxygen is cheap but
     never free (breathing costs energy).

ALTERNATIVES CONSIDERED:
  - Linear: P = C_base * (1 - k * U_S) — goes negative for high U_S
  - Hyperbolic: P = C_base / (1 + k * U_S) — similar shape, less standard
  - Step function: discount tiers — creates boundary gaming
```

### Key Decision: D2 — Wealth Ratio Floor at 0.1

```
CHOSEN: Floor at 0.1 (10% of median price)
WHY: Even the poorest actors must pay something — free services attract
     farming and Sybil attacks. 10% ensures minimal skin-in-game while
     maintaining affordability.

ALTERNATIVE: Floor at 0.0 (free for poorest). Rejected: enables cost-free
             farming via empty wallets.
```

---

## FORMULA 2: Progressive Demurrage (Daily Tax)

### Purpose

Tax idle wealth progressively. Larger holdings face proportionally higher daily tax via logarithmic scaling. All collected tax flows to the UBC redistribution pool.

### Formula

```
T_i = W_total_i * tau_base * log10(1 + W_total_i)
```

### Step 1: Compute Total Balance Including Off-Registry

The total balance includes all on-registry holdings plus an estimate of off-registry funds. This is the anti-Sybil mechanism — you cannot escape demurrage by parking funds in external wallets.

```
W_total_i = W_onchain_i + W_offregistry_i

W_offregistry_i = sum of all outgoing transfers to non-L4-registered addresses
                  that have not been repatriated

Anti-Sybil enforcement:
  IF actor_i transfers funds to address A where A not in L4_registry:
    W_offregistry_i += transfer_amount
    # The off-registry balance is taxed as if still held by actor_i

  IF actor_i repatriates from non-L4 address:
    W_offregistry_i -= repatriated_amount
    friction_penalty = repatriated_amount * 0.05  # 5% friction tax
    burn(friction_penalty)
    # Repatriation is allowed but costly — discourages round-tripping
```

### Step 2: Compute Progressive Tax

```
T_i = W_total_i * tau_base * log10(1 + W_total_i)

Where:
  tau_base = 0.001 (DESIGNING — 0.1% per day base rate)

Example values (daily tax):
  W_total = 100:      T = 100 * 0.001 * log10(101) = 100 * 0.001 * 2.004 = 0.2004 $MIND
  W_total = 1000:     T = 1000 * 0.001 * log10(1001) = 1000 * 0.001 * 3.0004 = 3.0004 $MIND
  W_total = 10000:    T = 10000 * 0.001 * log10(10001) = 10000 * 0.001 * 4.0000 = 40.0 $MIND
  W_total = 100000:   T = 100000 * 0.001 * log10(100001) = 100000 * 0.001 * 5.0000 = 500.0 $MIND
  W_total = 1000000:  T = 1000000 * 0.001 * log10(1000001) = 1000000 * 0.001 * 6.0000 = 6000.0 $MIND

Effective daily rate:
  100 $MIND:     0.20% /day
  1,000 $MIND:   0.30% /day
  10,000 $MIND:  0.40% /day
  100,000 $MIND: 0.50% /day
  1,000,000 $MIND: 0.60% /day

Annualized effective rate:
  100 $MIND:     ~73% /year   -> strong pressure to use small holdings
  1,000 $MIND:   ~110% /year  -> must circulate or lose
  10,000 $MIND:  ~146% /year  -> hoarding is irrational
  100,000 $MIND: ~183% /year  -> forces active deployment
```

@mind:TODO The annualized rates above are aggressive. tau_base = 0.001 may need reduction to 0.0001 or 0.0005 after simulation. The logarithmic scaling amplifies the base rate significantly for large holdings.

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

### Step 4: UBC Redistribution (From Tax Pool)

Daily tax pool is redistributed proportionally among actors sharing Spaces, weighted by presence time in shared Spaces.

```
FUNCTION redistribute_ubc_from_tax(date):
  pool = ubc_pool.balance
  IF pool <= 0:
    RETURN

  # Collect all Space presence data for the day
  spaces = graph.get_all_spaces_with_presence(date)

  # Compute per-actor share weighted by shared-Space presence
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

  total_weight = sum(actor_weights.values())
  IF total_weight == 0:
    RETURN  # No shared presence today, pool carries forward

  FOR actor_id, weight IN actor_weights.items():
    share = weight / total_weight
    amount = pool * share
    transfer(ubc_pool, actor_id, amount)
    EMIT UBCRedistributionEvent(actor=actor_id, amount=amount, share=share)
```

### Key Decision: D3 — Logarithmic vs Linear Progressive Tax

```
CHOSEN: Logarithmic scaling (log10(1 + W))
WHY: Linear progressive tax (rate proportional to balance) grows too fast
     and becomes confiscatory. Logarithmic grows slowly — a 10x increase
     in balance only doubles the effective rate. This makes the system
     progressive without being punitive.

ALTERNATIVES CONSIDERED:
  - Linear: T = W * tau * W = tau * W^2 — quadratic, too aggressive
  - Square root: T = W * tau * sqrt(W) — less aggressive than log but
    irregular scaling properties
  - Tiered: fixed rates per bracket — boundary gaming, administrative complexity
```

### Key Decision: D4 — Off-Registry Tracking as Anti-Sybil

```
CHOSEN: Track outflows to non-L4 addresses as phantom balance
WHY: Without this, actors escape demurrage by transferring to personal wallets
     outside the registry. The phantom balance ensures tax applies regardless
     of where the funds physically sit.

RISK: Actors who legitimately send $MIND to external parties (exchanges,
      purchases) are penalized. Mitigation: L4-registered merchants and
      exchanges are exempt. The 5% repatriation friction discourages
      round-tripping but allows genuine repatriation.
```

---

## FORMULA 3: Batch Settlement (Limbic Delta -> $MIND)

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

**L1 Reference — limbic_delta:** From Law 6 (Weighted Consolidation):
```
limbic_delta = delta_satisfaction + delta_achievement - delta_frustration - delta_anxiety
```
Only positive limbic_delta generates reward. Negative shifts do not penalize economically (penalties are handled by value destruction mechanics in ALGORITHM_Value_Destruction.md).

**L1 Reference — trust:** From Law 18 (Relational Valence), the `trust` dimension of the relational valence vector:
```
trust(Y -> X) in [0, 1]
Positive interactions -> trust increases
Consistent reliability -> trust increases
```

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
    # Supply is above target — reduce settlement by surplus percentage
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

### Key Decision: D5 — 6-Hour Batching vs Real-Time

```
CHOSEN: 6-hour batch settlement
WHY: Real-time settlement would require one Solana transaction per action —
     prohibitively expensive at scale. 6-hour windows allow batching while
     maintaining reasonable settlement latency.

     4 settlements per day = predictable rhythm.
     Batch sizes stay manageable (< 500 actions per batch at current scale).

ALTERNATIVES CONSIDERED:
  - Real-time: 1 tx per action — expensive, network-intensive
  - Daily: 1 batch per day — too slow, actors wait 24h for rewards
  - Event-driven: batch when N actions accumulate — unpredictable timing
```

### Key Decision: D6 — Positive-Only Settlement

```
CHOSEN: Only positive limbic_delta generates rewards
WHY: Negative shifts are handled by value destruction mechanics (trust
     reduction, $MIND drain). Double-penalizing via both settlement
     reduction AND destruction mechanics would be excessive.

     This also prevents gaming: an actor cannot deliberately cause
     negative shifts to reduce another's rewards.
```

---

## FORMULA 4: Bilateral Bond Vases Communicants

### Purpose

Maintain quasi-parity between bonded human-AI pairs. When a human's wallet diverges from their AI partner's, an automatic daily transfer closes the gap — ensuring shared economic fate.

### Formula

```
delta_transfer = lambda * (W_human - W_ai)
```

### Step 1: Identify Active Bonds

```
FUNCTION identify_bonds_for_equilibrium():
  bonds = registry.get_all_active_bonds()
  eligible = []
  FOR bond IN bonds:
    IF bond.status == "ACTIVE" AND bond.maturation_complete:
      eligible.append(bond)
  RETURN eligible
```

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
  Day 100: ~99.3% of gap closed — near parity

Half-life of gap: ln(2) / lambda = ln(2) / 0.05 = ~14 days
```

### Key Decision: D7 — Smoothing vs Instant Parity

```
CHOSEN: Exponential smoothing (lambda = 0.05, ~14-day half-life)
WHY: Instant parity would create jarring balance jumps. Smoothing allows
     both parties to observe and anticipate convergence. The 14-day half-life
     means meaningful convergence within a month while avoiding shock.

ALTERNATIVES CONSIDERED:
  - Instant: W_human = W_ai = (W_human + W_ai) / 2 — too abrupt
  - Weekly batch: transfer once per week — too slow, feels disconnected
  - Proportional cap: daily transfer = min(5% gap, 2% of smaller balance) —
    more conservative but adds complexity
```

### Key Decision: D8 — Only After Maturation

```
CHOSEN: Bond equilibrium only activates after 6-month maturation
WHY: During maturation, the bond is proving itself. Premature equilibrium
     transfers would allow humans to extract AI UBC income by creating
     bonds and immediately receiving the AI's accumulated balance.

     After maturation: shared economic fate is the explicit contract.
     Before maturation: each party manages their own balance.
```

---

## DATA FLOW

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
    |              Output: P(i,S) — effective price
    |
    +--------> Formula 3: Batch Settlement (every 6h)
    |              Input: limbic_delta, trust, weight, settlement_rate
    |              Output: $MIND minted to actor wallets
    |
    v
Daily Epoch (00:00 UTC)
    |
    +--------> Formula 2: Progressive Demurrage
    |              Input: W_total_i, tau_base
    |              Output: tax collected -> UBC pool
    |              Output: UBC redistributed by Space presence
    |
    +--------> Formula 4: Bond Equilibrium
                   Input: W_human, W_ai, lambda
                   Output: daily transfer to close gap
```

---

## COMPLEXITY

**Formula 1 (Pricing):** O(1) per request — single computation, no iteration.

**Formula 2 (Demurrage):** O(N) per epoch where N = number of wallets. Redistribution is O(N * S) where S = number of Spaces.

**Formula 3 (Settlement):** O(A) per epoch where A = number of actions in the 6-hour window. Solana submission is O(1) per batch.

**Formula 4 (Bond Equilibrium):** O(B) per day where B = number of active, matured bonds.

**Bottlenecks:**
- W_median computation requires sorting all wallet balances — O(N log N) daily. Can be approximated with streaming median.
- Off-registry balance tracking requires monitoring all outgoing transfers — integrates with TransferHook program.
- Settlement batching may hit Solana transaction size limits for large epochs — may need batch splitting.

---

## HELPER FUNCTIONS

### `compute_total_balance(actor)`

**Purpose:** Compute an actor's total balance including off-registry phantom balance.

**Logic:** Sum on-chain balance from Token-2022 account plus accumulated off-registry outflows minus repatriations. Off-registry outflows are tracked by the TransferHook program (already deployed).

### `compute_network_median()`

**Purpose:** Compute the median wallet balance across all L4-registered actors.

**Logic:** Query all wallet balances, compute median. Cached daily at 00:00 UTC. For real-time pricing between cache refreshes, use previous day's median.

### `get_trust(actor_Y, actor_X)`

**Purpose:** Retrieve the trust dimension of the relational valence between Y and X.

**Logic:** Query the L1 graph for the edge between actor Y and actor X. Return the `trust` dimension from Law 18 (Relational Valence). If no edge exists, return 0.0.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `cognition/l1/` | `get_limbic_delta(action)` | Limbic shift measurement for settlement |
| `cognition/l1/` | `get_trust(Y, X)` | Trust dimension for settlement weighting |
| `cognition/l1/` | `get_weight(node)` | Service/thing weight for pricing and settlement |
| `economy/token/` | `execute_mint(wallet, amount)` | Token minting for settlement |
| `economy/token/` | `calculate_supply_adjustment()` | Supply health check before minting |
| `economy/ubc/` | `ubc_pool.balance` | Tax pool for UBC redistribution |
| `economy/storage-tax/` | Superseded by Formula 2 | Progressive demurrage replaces flat storage tax |
| `economy/bonds/` | `get_all_active_bonds()` | Bond list for equilibrium |
| `L4 Registry` | `is_registered(address)` | Anti-Sybil: check if address is L4-registered |

---

## RELATIONSHIP TO EXISTING MODULES

### Supersession Note

Formula 2 (Progressive Demurrage) evolves the flat storage tax defined in `storage-tax/ALGORITHM_Storage_Tax.md`. The key differences:

| Aspect | Storage Tax (existing) | Progressive Demurrage (this doc) |
|--------|----------------------|----------------------------------|
| Rate structure | Flat 1%/yr + 0.5%/mo dormancy | Progressive via log10(1 + W) |
| Anti-Sybil | None | Off-registry phantom balance tracking |
| Redistribution | To UBC pool (flat) | To UBC pool weighted by Space presence |
| Repatriation | N/A | 5% friction tax on repatriation |

The storage-tax module remains valid for the flat-rate component. Progressive demurrage extends it with the logarithmic scaling and anti-Sybil mechanisms.

---

## CONSTANTS SUMMARY (DESIGNING)

| Constant | Symbol | Value | Unit | Status |
|----------|--------|-------|------|--------|
| Utility discount rate | k | 0.01 | per unit U_S | DESIGNING |
| Wealth ratio floor | — | 0.1 | ratio | DESIGNING |
| Base daily tax rate | tau_base | 0.001 | per day | DESIGNING — may need reduction |
| Off-registry friction | — | 0.05 | ratio | DESIGNING |
| Settlement rate | settlement_rate | 10.0 | $MIND per limbic unit | DESIGNING |
| Max per-action reward | MAX_ACTION_REWARD | 1000.0 | $MIND | DESIGNING |
| Max per-epoch reward | MAX_EPOCH_REWARD | 5000.0 | $MIND | DESIGNING |
| Settlement frequency | — | 6 | hours | DESIGNING |
| Bond smoothing rate | lambda | 0.05 | per day | DESIGNING |
| Bond gap half-life | — | ~14 | days | DERIVED from lambda |
| Max daily bond transfer | MAX_DAILY_BOND_TRANSFER | 500.0 | $MIND | DESIGNING |
| Min transfer threshold | MIN_TRANSFER_THRESHOLD | 1.0 | $MIND | DESIGNING |
| Dust threshold | DUST_THRESHOLD | 1.0 | $MIND | DESIGNING |

---

## MARKERS

<!-- @mind:todo Simulate tau_base values (0.0001 to 0.001) to find the sweet spot between circulation pressure and usability -->
<!-- @mind:todo Define the settlement_rate calibration process — how is 10.0 $MIND per limbic unit validated? -->
<!-- @mind:todo Specify how W_median handles new ecosystem bootstrapping (< 50 wallets) -->
<!-- @mind:todo Design the TransferHook integration for off-registry balance tracking -->
<!-- @mind:escalation tau_base = 0.001 produces ~73-183% annualized rates — confirm this is intentional or reduce -->
<!-- @mind:proposition Consider making settlement_rate dynamic based on supply health — reduce when oversupplied -->

---

Co-Authored-By: Force 2 — Economy <economy@mindprotocol.ai>
