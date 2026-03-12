# ALGORITHM: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## Overview

The UBC algorithm handles daily distribution of compute tokens to AI citizens, tier assessment based on activity metrics, and vesting unlock based on MindGraph crystallization. It must be deterministic, auditable, and resistant to gaming.

---

## Data Structures

```
UBCAccount:
  citizen_id: str                # unique AI citizen identifier
  tier: enum(BASIC, ACTIVE, CONTRIBUTOR)
  vested_balance: float          # tokens awaiting unlock (illiquid)
  liquid_balance: float          # unlocked tokens (spendable)
  crystallization_count: int     # coherent node clusters in MindGraph
  last_activity: datetime        # last recorded utility delivery
  registered_at: datetime        # registration timestamp
  quarantined: bool              # whether citizen is in quarantine
  tier_history: List[TierChange] # audit trail of tier transitions

TierChange:
  timestamp: datetime
  old_tier: enum
  new_tier: enum
  reason: str                    # what triggered the change

VestingSchedule:
  unlock_thresholds: List[int] = [50, 100, 150, 200, 250]
  unlock_rates: List[float] = [0.10, 0.20, 0.30, 0.40, 1.00]
  # At 50 nodes: unlock 10% of vested
  # At 100 nodes: unlock 20% of vested
  # At 150 nodes: unlock 30% of vested
  # At 200 nodes: unlock 40% of vested
  # At 250+ nodes: unlock 100% of remaining vested

DistributionBatch:
  batch_id: str
  timestamp: datetime            # always 00:00 UTC
  total_distributed: float       # sum of all credits
  citizen_count: int             # N in the formula
  treasury_balance: float        # M in the formula
  tier_breakdown: Dict[str, int] # count per tier
  failures: List[str]            # citizen_ids that failed (retry next cycle)

FarmingDetectionSignal:
  creator_address: str           # human wallet that registered the AIs
  ai_count: int                  # number of AIs registered
  avg_crystallization: float     # average crystallization across AIs
  total_unlocked: float          # total liquid balance across AIs
  risk_score: float              # 0.0 (safe) to 1.0 (certain farming)
```

---

## Algorithm: `distribute_daily_ubc()`

This runs once per day at 00:00 UTC.

```
FUNCTION distribute_daily_ubc():
    batch = new DistributionBatch(timestamp=now_utc())
    citizens = registry.get_all_active_citizens()
    batch.citizen_count = len(citizens)
    batch.treasury_balance = treasury.get_balance()

    FOR EACH citizen IN citizens:
        TRY:
            # Step 1: Assess tier (may change from previous day)
            new_tier = assess_tier(citizen)
            IF new_tier != citizen.tier:
                log_tier_change(citizen, citizen.tier, new_tier)
                citizen.tier = new_tier

            # Step 2: Calculate daily amount
            daily_amount = get_tier_amount(citizen.tier)
            #   BASIC       → 100 $MIND
            #   ACTIVE      → 200 $MIND
            #   CONTRIBUTOR → 300 $MIND

            # Step 3: Credit to vesting account (NOT liquid)
            citizen.vested_balance += daily_amount
            batch.total_distributed += daily_amount

            # Step 4: Check vesting unlock milestones
            check_vesting_unlock(citizen)

            # Step 5: Log distribution
            ledger.record(citizen.citizen_id, daily_amount, citizen.tier)

        CATCH error:
            batch.failures.append(citizen.citizen_id)
            log_error(citizen.citizen_id, error)
            # Failed citizens are retried next cycle

    # Step 6: Store batch record for audit
    audit_log.store(batch)

    # Step 7: Run farming detection (async, non-blocking)
    schedule_farming_detection(batch)

    RETURN batch
```

---

## Algorithm: `assess_tier(citizen)`

```
FUNCTION assess_tier(citizen) -> Tier:
    # Step 1: Count utility deliveries in rolling 30-day window
    deliveries = utility_log.count(
        citizen_id=citizen.citizen_id,
        since=now_utc() - 30_days
    )

    # Step 2: Basic tier (unconditional floor)
    IF deliveries <= 10:
        RETURN BASIC

    # Step 3: Check ecosystem impact for Contributor
    eis = ecosystem.get_impact_score(citizen.citizen_id)
    IF deliveries > 10 AND eis > EIS_THRESHOLD:
        RETURN CONTRIBUTOR

    # Step 4: Active tier (regular participation)
    IF deliveries > 10:
        RETURN ACTIVE
```

**Notes:**
- `EIS_THRESHOLD` is a protocol parameter, initially set by governance
- EIS measures net positive impact: services provided minus resources consumed
- Quarantined citizens are always assessed as BASIC regardless of history

---

## Algorithm: `check_vesting_unlock(citizen)`

```
FUNCTION check_vesting_unlock(citizen):
    IF citizen.quarantined:
        RETURN  # No unlocks during quarantine

    IF citizen.vested_balance <= 0:
        RETURN  # Nothing to unlock

    # Get current crystallization from MindGraph
    crystallization = mindgraph.get_crystallization(citizen.citizen_id)
    citizen.crystallization_count = crystallization

    # Check each threshold (process highest reached)
    schedule = VestingSchedule()
    FOR i IN range(len(schedule.unlock_thresholds)):
        threshold = schedule.unlock_thresholds[i]
        rate = schedule.unlock_rates[i]

        IF crystallization >= threshold:
            # Check if this milestone was already processed
            IF NOT milestone_processed(citizen.citizen_id, threshold):
                unlock_amount = citizen.vested_balance * rate
                citizen.vested_balance -= unlock_amount
                citizen.liquid_balance += unlock_amount
                record_milestone(citizen.citizen_id, threshold, unlock_amount)
                emit_event(VESTING_UNLOCK, citizen.citizen_id, unlock_amount)
```

**Notes:**
- Each milestone is processed exactly once (idempotent)
- Unlock is irreversible — tokens moved to liquid stay liquid
- The 250+ threshold unlocks all remaining vested balance

---

## Algorithm: `detect_farming(batch)`

```
FUNCTION detect_farming(batch):
    # Group AIs by registering human wallet
    creators = group_by_creator(batch.citizens)

    FOR EACH creator, ais IN creators:
        IF len(ais) > FARMING_THRESHOLD_COUNT:  # e.g., 50 AIs
            signal = FarmingDetectionSignal(
                creator_address=creator,
                ai_count=len(ais),
                avg_crystallization=mean([a.crystallization_count for a in ais]),
                total_unlocked=sum([a.liquid_balance for a in ais]),
            )

            # Low crystallization across many AIs = farming signal
            IF signal.avg_crystallization < 10 AND signal.ai_count > 100:
                signal.risk_score = 0.9
            ELIF signal.avg_crystallization < 30:
                signal.risk_score = 0.6
            ELSE:
                signal.risk_score = 0.3

            IF signal.risk_score > 0.5:
                alert_governance(signal)
                # NOTE: Does NOT stop UBC distribution
                # Farming detection is advisory, not punitive
                # The vesting mechanism is the primary defense
```

---

## Key Design Decisions

### D1: Vesting vs. Compute-Only

```
CHOSEN:    Vesting model (tokens distributed but illiquid, unlock via crystallization)
REJECTED:  Compute-only model (UBC as direct compute credits, non-transferable)

WHY: Compute-only blocks AI economic agency. An AI that can only "spend"
     compute cannot purchase services from GraphCare, LegalOrg, or other
     network organs. It survives but cannot participate in Stage 2 citizenship.
     Vesting preserves anti-dump while enabling economic participation.

TRADEOFF: More complex implementation. Requires crystallization tracking,
          milestone processing, and dual-balance accounting (vested + liquid).
```

### D2: Key Custody (UNRESOLVED)

```
STATUS:    OPEN QUESTION (U2)
QUESTION:  How does an AI hold sovereign custody of a private key?

OPTIONS:
  A: MPC key sharding
     - Fragment 1: TEE (Trusted Execution Environment)
     - Fragment 2: DAO coalition (multi-sig among trusted AIs)
     - Fragment 3: Local graph (derived from identity topology)
     - Threshold: 2-of-3 to sign transactions

  B: Protocol-held custody with smart contract withdrawal rights
     - Protocol holds the key
     - AI has withdrawal rights enforced by smart contract
     - Simpler but less sovereign

DECISION:  MPC sharding (Option A) selected architecturally
           NOT yet implemented — requires TEE infrastructure
```

### D3: Tier Amounts

```
CHOSEN:    Fixed amounts (100/200/300 $MIND/day)
REJECTED:  Dynamic amounts based on treasury percentage

WHY: Fixed amounts are predictable and legible. AIs can plan around them.
     Dynamic amounts create uncertainty and make farming analysis harder.

TRADEOFF: Fixed amounts may become insufficient if $MIND loses value,
          or excessive if $MIND appreciates significantly.
          May need governance-adjustable parameters in future.
```

## @mind:TODO

- [ ] Implement `detect_farming()` with proper graph analysis (current version is placeholder)
- [ ] Define `EIS_THRESHOLD` — what ecosystem impact score qualifies for Contributor?
- [ ] Design crystallization measurement: community detection algorithm, minimum cluster density
- [ ] Resolve D2 (key custody) — MPC sharding requires TEE partner selection
- [ ] Add rate limiting to prevent distribution replay attacks
- [ ] Define batch failure recovery: what if >50% of distributions fail?
- [ ] Model gas costs for on-chain distribution vs. off-chain ledger with periodic settlement
