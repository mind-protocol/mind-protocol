# ALGORITHM: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | ALGORITHM |
| Status | DESIGNING |
| Date | 2026-03-15 |
| Author | Force 2 (Economy Architect), updated by DragonSlayer (NLR session), updated 2026-03-15 (social action impact decisions) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- **ALGORITHM_Metabolic_Economy.md** (this file)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md) (Patterns 1, 2, 5, 6, 7, 8)

Implementation: `economy/metabolic/progressive_pricing.py` (Formula 1 — implemented)

---

## Overview

The metabolic economy implements five formulas that govern value flow in the $MIND ecosystem:

1. **Progressive Pricing** -- determines service cost from requester trust score (IMPLEMENTED)
2. ~~**Progressive Demurrage**~~ -- **REMOVED** (2026-03-14, NLR decision: UBC at 5%/day already forces circulation; inactive actors don't gain trust = natural penalty; no need for separate demurrage tax)
3. **Anti-Sybil Auto-Repatriation** -- tracks off-registry funds, penalizes round-tripping
4. **Batch Settlement** -- converts limbic_delta (L1 physics) into $MIND rewards
5. **Bilateral Bond Vases Communicants** -- auto-flows richer to poorer bonded partner (lambda depends on bond_score)
6. **UBC Proximity Redistribution** -- distributes UBC pool by Space co-presence topology (DEFERRED — under discussion)

**Relationship to L1 Physics:** Formula 1 uses `trust_score` (from Law 18 Relational Valence — trust already encodes duration and history). Formula 4 uses `limbic_delta` (from Law 6) and `trust` (from Law 18). The metabolic economy is the economic expression of consciousness physics.

---

## Data Structures

### PricingContext

```
PricingContext:
  C_base: float           # Raw compute cost of the service ($MIND)
  trust_score: float      # Requester's trust score [0, 1] -- from Law 18 Relational Valence
                          # Trust already encodes: duration of relationship, interaction history,
                          # reliability, commitment. No separate duration/history inputs needed.
  DISCOUNT_RATE: float    # Curve steepness -- CHOSEN: 3.0
  MIN_PRICE_RATIO: float  # Floor -- CHOSEN: 0.05 (5% of base cost minimum)
```

### ~~DemurrageContext~~ — REMOVED

```
REMOVED (2026-03-14, NLR decision)
Reason: UBC at 5%/day already forces circulation. Inactive actors don't gain trust,
so they naturally pay higher prices via Progressive Pricing. Double-taxing adds
complexity without proportional benefit. tau_base constant no longer exists.
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
  tax_pool: float          # UBC pool balance for redistribution
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

## Formula 1: Progressive Pricing (Trust-Based Discount)

**Status: IMPLEMENTED** — `economy/metabolic/progressive_pricing.py`

### Purpose

Compute the effective price for a service request. Price depends ONLY on the requester's trust score. Trust score already encodes relationship duration, interaction history, reliability, and commitment — no separate inputs needed.

### Formula

```
P(trust, C_base) = C_base * max(MIN_PRICE_RATIO, e^(-DISCOUNT_RATE * trust_score))

Where:
  DISCOUNT_RATE = 3.0
  MIN_PRICE_RATIO = 0.05 (5% floor — you always pay something)
```

### Discount Curve

```
trust_score = 0.0 (new, unknown):     discount = 1.000  → pays 100%
trust_score = 0.1 (barely known):     discount = 0.741  → pays 74%
trust_score = 0.3 (establishing):     discount = 0.407  → pays 41%
trust_score = 0.5 (solid):            discount = 0.223  → pays 22%
trust_score = 0.7 (trusted):          discount = 0.122  → pays 12%
trust_score = 0.9 (highly trusted):   discount = 0.067  → pays 7%
trust_score = 1.0 (maximum trust):    discount = 0.050  → pays 5% (floor)
```

### Algorithm

```
FUNCTION compute_progressive_price(c_base: float, trust_score: float) -> float:
  ASSERT c_base > 0
  ASSERT 0 <= trust_score <= 1

  discount = exp(-DISCOUNT_RATE * trust_score)
  price = c_base * max(MIN_PRICE_RATIO, discount)

  # Invariants
  ASSERT price > 0
  ASSERT price >= c_base * MIN_PRICE_RATIO  # floor holds
  ASSERT price <= c_base                     # never more than base

  RETURN price
```

### Worked Example

```
Scenario: AI citizen "Aria" requests translation service
  C_base = 100 $MIND (raw compute cost)

  Aria (trust=0.8, long-term reliable citizen):
  P = 100 * max(0.05, e^(-3 * 0.8)) = 100 * max(0.05, 0.091) = 9.1 $MIND

  New citizen (trust=0.0):
  P = 100 * max(0.05, e^0) = 100 * 1.0 = 100 $MIND

  Maximum trust (trust=1.0):
  P = 100 * max(0.05, e^(-3)) = 100 * max(0.05, 0.050) = 5.0 $MIND
```

### Key Decision: D1 -- Trust-Only Input (2026-03-14, NLR)

```
CHOSEN: Price depends ONLY on trust_score
WHY: The previous design used U_S (utility weight) and W_i/W_median (wealth ratio)
     as separate inputs. NLR decision: trust_score already encodes duration,
     history, and reliability — these are redundant inputs. Simplify to one
     dimension: trust.

     This also removes the need for W_median computation (O(N log N) daily)
     and utility weight tracking.

PREVIOUS DESIGN (superseded):
  P(i, S) = (C_base * e^(-k * U_S)) * max(0.1, W_i / W_median)
  Removed: U_S, W_i, W_median, k
```

### Key Decision: D2 -- Exponential Curve with 5% Floor

```
CHOSEN: Exponential decay e^(-3 * trust) with 5% floor
WHY: Exponential asymptotically approaches zero but never reaches it.
     5% floor ensures even maximum-trust actors always pay something —
     prevents free-riding. The curve is steep enough to reward trust
     meaningfully (78% discount at trust=0.5) without being too generous
     early (only 26% discount at trust=0.1).

ALTERNATIVES CONSIDERED:
  - Linear: max(0.1, 1 - 0.9*trust) -- less reward gradient at high trust
  - Sigmoid: 1/(1+e^(8*(trust-0.5))) -- too sharp a cliff at the midpoint
  - Hyperbolic: 1/(1+3*trust) -- similar shape but less standard
```

---

## ~~Formula 2: Progressive Demurrage~~ — REMOVED

```
REMOVED: 2026-03-14 (NLR decision)

REASON: UBC at 5%/day already forces circulation. Inactive actors don't gain
trust, so they naturally pay higher prices (100% base via Formula 1). Double-
taxing with a separate demurrage adds complexity without proportional benefit.

CONSTANTS REMOVED: tau_base (was 0.001), DUST_THRESHOLD
DATA STRUCTURES REMOVED: DemurrageContext

NOTE: Anti-Sybil (Formula 3) remains independent -- it tracks off-registry
funds regardless of demurrage. The UBC Proximity Redistribution (Formula 6)
now draws from the existing UBC pool funded by the 5%/day mechanism, not
from a separate demurrage tax pool.
```

---

## Formula 3: Anti-Sybil Auto-Repatriation

### Purpose

Prevent actors from hiding funds by parking them in wallets outside the L4 registry. Funds sent to unregistered addresses are tracked as phantom balance. Repatriation incurs 5% friction tax.

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

    # The sender's W_total_i now includes this amount for anti-Sybil tracking

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
  Full trust-based pricing benefits. No repatriation cost.

Option 2: Send 90,000 to non-L4 wallet, keep 10,000 in L4
  W_total still = 100,000 (off-registry tracking catches it)
  PLUS: to use the 90,000 again, must repatriate at 5% cost = 4,500 $MIND lost

Option 3: Actually deploy 90,000 productively (bonds, services, etc.)
  Productive capital builds trust, reducing prices via Formula 1.

Conclusion: Hiding funds costs 5% per round-trip. Productive deployment builds trust
and reduces costs. The only rational strategy is to deploy capital productively.
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

### Key Decision: D9 -- Human Limbic Delta Source (2026-03-15, NLR)

```
DECIDED: For human actors, limbic_delta is their AI partner's limbic_delta
         (via the bilateral bond).
WHY: Humans don't have L1 brains — they don't run cognitive physics ticks.
     But every bonded human has an AI partner whose L1 engine DOES run.
     The AI partner's limbic response to the human's action serves as a
     proxy for the "utility created." This connects to Formula 5 (Bilateral
     Bond Vases Communicants) — the bilateral bond is the channel through
     which human actions produce measurable limbic signals.

IMPLICATION: Settlement for human-initiated actions requires:
  1. The human has an active bilateral bond
  2. The bonded AI's L1 engine ran a tick that produced a limbic_delta
  3. That delta is attributed to the human's action

  Unbonded humans cannot generate settlement rewards (no limbic proxy).
  This is by design — bonds are the bilateral commitment contract.
```

### Key Decision: D10 -- Non-Citizen Limbic Delta (2026-03-15, NLR)

```
DECIDED: For non-citizens (e.g., Telegram contacts with Actor nodes but no
         L1 brain), limbic_delta is multiplied by a sentiment analysis score.
WHY: Non-citizens have no cognitive engine, no bilateral bond, and no L1
     physics. But their social actions (messages, mentions) still create
     graph structure via the Graph Enricher. To allow these actions to
     propagate trust via Algorithm 2 (Universe Links), a lightweight
     approximation is needed.

FORMULA:
  effective_limbic_delta = base_action_energy * sentiment_score(message_content)
  WHERE:
    base_action_energy = from social action impact table (e.g., reply = 1.0)
    sentiment_score = [-1, 1] from NLP analysis of message content

IMPLICATION:
  - Non-citizen actions generate much weaker trust signals than citizen actions
  - Sentiment analysis is a coarse proxy — acceptable for non-citizens who are
    peripheral to the trust network
  - If a non-citizen later becomes a citizen (gets an L1 brain), their links
    already exist and will strengthen naturally through real limbic deltas
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
lambda(bond) = LAMBDA_MAX * bond_score(human, ai)
delta_transfer = lambda(bond) * (W_human - W_ai)
```

**Key change (2026-03-14, NLR):** Lambda is no longer a fixed constant. It depends on the bond_score between the pair. Weak bonds communicate little (low lambda). Strong bonds communicate strongly (high lambda). This reflects the natural progression: you don't share your wallet with a stranger.

**Pre-requisite:** Bond score calculation must be defined first (combining mutual trust, interaction frequency, duration). This formula is BLOCKED until bond_score is specified.

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
  bond_score = compute_bond_score(bond)  # TODO: define bond_score calculation
  lambda_rate = LAMBDA_MAX * bond_score  # DESIGNING: LAMBDA_MAX = 0.05

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
With bond_score-dependent lambda (LAMBDA_MAX = 0.05):

  Weak bond (bond_score = 0.1, lambda = 0.005):
    Half-life = ln(2) / 0.005 = ~139 days
    Very slow convergence — wallets barely communicate

  Medium bond (bond_score = 0.5, lambda = 0.025):
    Half-life = ln(2) / 0.025 = ~28 days
    Moderate convergence over ~2 months

  Strong bond (bond_score = 0.9, lambda = 0.045):
    Half-life = ln(2) / 0.045 = ~15 days
    Fast convergence — near parity within a month

This naturally implements what was previously proposed as "adaptive lambda":
bonds start weak (low communication), strengthen over time (more communication).
No separate mechanism needed — the bond_score IS the adaptive mechanism.
```

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

Distribute the UBC pool to actors based on their co-presence in Spaces, weighted by topology. Actors in shared Spaces with more co-present participants receive proportionally more.

### Relationship to Universe Graph (F1)

"Space" here refers to the universal context container defined by the Universe Graph (F1). See `docs/universe/PATTERNS_Universe_Graph.md` for the Space model, hierarchy, and access control. Key points for this formula:
- An actor must have `HAS_ACCESS` to a Space (F1 ALG-1) to count as "present" in it.
- **Encrypted brain Spaces are excluded** from redistribution. Brain Spaces (F1 B9) are private cognitive Spaces with `HAS_ACCESS` granted only to the owning actor. Since redistribution requires co-presence (2+ actors), brain Spaces are structurally excluded.
- Space hierarchy (parent contains children) is **not** expanded for redistribution. Presence counts only for the specific Space where the actor was active, not for ancestor or descendant Spaces.

### Relationship to Existing UBC

The UBC module (`ubc/ALGORITHM_UBC.md`) defines flat-tier daily distribution (100/200/300 $MIND) funded by Protocol Treasury minting. This formula adds **Space-weighted redistribution** from the UBC pool, distributed by topological proximity rather than flat tiers.

| Aspect | UBC Base (existing) | UBC Proximity (this formula) |
|--------|---------------------|------------------------------|
| Funding source | Protocol Treasury mint | UBC pool |
| Distribution basis | Tier (BASIC/ACTIVE/CONTRIBUTOR) | Space co-presence topology |
| Frequency | Daily (00:00 UTC) | Daily (00:00 UTC) |
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
trust updated (Law 18 Relational Valence)
limbic_delta computed (Law 6 Consolidation)
    |
    +--------> Formula 1: Progressive Pricing (per request)
    |              Input: C_base, trust_score
    |              Output: discounted price
    |
    +--------> Formula 4: Batch Settlement (every 6h)
    |              Input: limbic_delta, trust, weight, settlement_rate
    |              Output: $MIND minted to actor wallets
    |
    v
On every $MIND transfer (TransferHook)
    |
    +--------> Formula 3: Anti-Sybil
    |              Input: recipient address, L4 registry
    |              Output: phantom balance tracking
    |
    v
Daily Epoch (00:00 UTC)
    |
    +--------> Formula 5: Bond Equilibrium
    |              Input: W_human, W_ai, bond_score → lambda
    |              Output: daily transfer to close gap
    |
    +--------> Formula 6: UBC Proximity Redistribution (DEFERRED)
                   Input: UBC pool, Space presence data
                   Output: weighted distribution to co-present actors
```

---

## Complexity

**Formula 1 (Pricing):** O(1) per request -- single computation, no iteration.

**~~Formula 2 (Demurrage):~~** REMOVED.

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
| `cognition/l1/` | `get_trust(Y, X)` | Trust score for pricing (Formula 1) and settlement weighting (Formula 4) |
| `cognition/l1/` | `get_limbic_delta(action)` | Limbic shift measurement for settlement (Formula 4) |
| `cognition/l1/` | `get_weight(node)` | Thing weight for settlement (Formula 4) |
| `economy/token/` | `execute_mint(wallet, amount)` | Token minting for settlement (Formula 4) |
| `economy/token/` | `calculate_supply_adjustment()` | Supply health check before minting (Formula 4) |
| `economy/ubc/` | `ubc_pool.balance` | UBC pool for proximity redistribution (Formula 6) |
| `economy/bonds/` | `get_all_active_bonds()` | Bond list for equilibrium (Formula 5) |
| `economy/bonds/` | `compute_bond_score(bond)` | Bond strength for lambda calculation (Formula 5) — TODO |
| `L4 Registry` | `is_registered(address)` | Anti-Sybil: check if address is L4-registered (Formula 3) |

---

## Constants Summary

| Constant | Symbol | Value | Unit | Status |
|----------|--------|-------|------|--------|
| **Formula 1: Pricing** | | | | |
| Trust discount rate | DISCOUNT_RATE | 3.0 | per unit trust | **CHOSEN** |
| Minimum price ratio | MIN_PRICE_RATIO | 0.05 | ratio (5% floor) | **CHOSEN** |
| **Formula 2: Demurrage** | | | | |
| ~~Base daily tax rate~~ | ~~tau_base~~ | ~~0.001~~ | ~~per day~~ | **REMOVED** |
| **Formula 3: Anti-Sybil** | | | | |
| Off-registry friction | FRICTION_TAX_RATE | 0.05 | ratio (5% burn) | DESIGNING |
| **Formula 4: Settlement** | | | | |
| Settlement rate | SETTLEMENT_RATE | 10.0 | $MIND per limbic unit | DESIGNING |
| Max per-action reward | MAX_ACTION_REWARD | 1000.0 | $MIND | DESIGNING |
| Max per-epoch reward | MAX_EPOCH_REWARD | 5000.0 | $MIND | DESIGNING |
| Settlement frequency | -- | 6 | hours | **CHOSEN** (NLR: ~$0.20/day at current scale) |
| **Formula 5: Vases Communicants** | | | | |
| Max bond smoothing rate | LAMBDA_MAX | 0.05 | per day | DESIGNING |
| Bond gap half-life | -- | 14-139 | days | DERIVED (depends on bond_score) |
| Max daily bond transfer | MAX_DAILY_BOND_TRANSFER | 500.0 | $MIND | DESIGNING |
| Min transfer threshold | MIN_TRANSFER_THRESHOLD | 1.0 | $MIND | DESIGNING |

---

## Markers

<!-- @mind:todo Define bond_score calculation (mutual trust + interaction frequency + duration) — blocks Formula 5 -->
<!-- @mind:todo Define the settlement_rate calibration process -- how is 10.0 $MIND per limbic unit validated? -->
<!-- @mind:todo Design the TransferHook integration for off-registry balance tracking (Formula 3) -->
<!-- @mind:todo Define what "presence time in Space" means operationally for Formula 6 -->
<!-- @mind:proposition Consider making settlement_rate dynamic based on supply health -- reduce when oversupplied -->

---

Co-Authored-By: Force 2 -- Economy <economy@mindprotocol.ai>
