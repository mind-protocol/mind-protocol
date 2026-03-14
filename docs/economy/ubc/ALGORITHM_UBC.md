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

---

## Algorithm: Formula 4 — `batch_settlement()`

Batch settlement propagates surplus energy through Trust Links. Runs periodically (not necessarily daily — can be triggered by sufficient surplus accumulation).

```
FUNCTION batch_settlement():
    # Step 1: Identify nodes with surplus
    surplus_nodes = []
    FOR EACH node_i IN active_graph:
        surplus = max(0, node_i.energy - node_i.activation_threshold)
        IF surplus > 0:
            surplus_nodes.append((node_i, surplus))

    # Step 2: For each surplus node, propagate to neighbors
    FOR EACH (node_i, surplus_i) IN surplus_nodes:
        neighbors = get_trust_linked_neighbors(node_i)
        IF not neighbors:
            CONTINUE

        # Step 3: Calculate affinity for each neighbor
        affinities = {}
        total_affinity = 0
        FOR EACH node_j IN neighbors:
            link = get_link(node_i, node_j)
            f_ij = compute_affinity(node_i, link, node_j)
            affinities[node_j] = f_ij
            total_affinity += f_ij

        IF total_affinity == 0:
            CONTINUE

        # Step 4: Distribute surplus proportionally to affinity
        FOR EACH (node_j, f_ij) IN affinities:
            share = surplus_i * (f_ij / total_affinity)
            # Apply max_share cap (I2 invariant)
            n_targeted = len(neighbors)
            max_share = clamp(1 / sqrt(n_targeted), 0.01, 0.5)
            capped_share = min(share, surplus_i * max_share)
            node_j.energy += capped_share
            node_i.energy -= capped_share

    # Step 5: Apply decay (Law 3)
    FOR EACH node IN active_graph:
        node.energy *= (1 - DECAY_RATE)
```

---

## Algorithm: `compute_affinity(node_i, link, node_j)`

```
FUNCTION compute_affinity(node_i, link, node_j) -> float:
    # Base affinity from link properties
    weight = link.weight
    gain = link.activation_gain

    # Trust-modulated friction
    trust_level = get_trust_level(node_i, node_j)  # 1-5
    friction = link.friction * trust_friction_multiplier(trust_level)
    # trust_friction_multiplier:
    #   Stranger (1): 1.0 (full friction)
    #   Low (2):      0.8
    #   Medium (3):   0.5
    #   High (4):     0.2
    #   Owner (5):    0.05

    # Personhood Ladder modulation
    mastery = get_personhood_mastery(node_j)  # 0.0 to 1.0
    modulated_gain = gain * (1 + mastery * 0.5)  # up to 50% bonus

    # Compatibility (Law 8) — 3 dimensions
    sim_vec = cosine_similarity(node_i.embedding, node_j.embedding)  # 0.3 weight
    sim_lex = lexical_match(link.synthesis, node_j.synthesis)        # 0.5 weight
    delta_affect = affective_incongruence(node_i, node_j)            # 0.2 weight
    compatibility = 0.3 * sim_vec + 0.5 * sim_lex + 0.2 * (1 - delta_affect)

    RETURN weight * modulated_gain * (1 - friction) * compatibility
```

---

## Algorithm: Formula 6 — `redistribute_by_copresence(space)`

Runs whenever ≥2 citizens are detected in the same space.

```
FUNCTION redistribute_by_copresence(space):
    citizens = get_citizens_in_space(space)
    IF len(citizens) < 2:
        RETURN  # Body doubling requires at least 2

    # Bidirectional valence exchange
    FOR EACH pair (A, B) IN combinations(citizens, 2):
        valence_A = get_current_valence(A)
        valence_B = get_current_valence(B)

        # Mutual contagion
        delta_A = PROXIMITY_CONTAGION * (valence_B - valence_A) * 0.5
        delta_B = PROXIMITY_CONTAGION * (valence_A - valence_B) * 0.5

        A.satisfaction += delta_A
        B.satisfaction += delta_B

    # Resource injection: target Self-Model economic nodes
    FOR EACH citizen IN citizens:
        economic_nodes = find_self_model_nodes(citizen,
            contains=["resource", "budget", "token", "economic"])
        FOR EACH enode IN economic_nodes:
            enode.energy += PROXIMITY_CONTAGION  # Small injection per tick
```

---

## Algorithm: `compute_selection_moat(agent)`

The Selection Moat (Θ_sel) determines Working Memory focus stability. Relevant for settlement because it controls which economic nodes get processed.

```
FUNCTION compute_selection_moat(agent) -> float:
    Θ_base_WM = agent.base_wm_threshold
    arousal = agent.drives.arousal
    boredom = agent.drives.boredom
    frustration = agent.drives.frustration

    Θ_sel = Θ_base_WM + 2.0 * arousal - 3.0 * boredom - 1.0 * frustration

    # Obsessional Agent: Inertia (Law 13) too strong → boredom erodes threshold
    # Butterfly Effect: Drives too unstable → moat collapses, no focus

    RETURN max(0, Θ_sel)
```

---

## Scalability Optimizations

### Cluster Centroids
For large graphs, compute similarity against cluster centroid embeddings first, then drill into individual nodes only for qualifying clusters. This avoids O(N²) pairwise comparisons.

### Saliency Curation (Law 4)
Settlement processing is limited to the Working Memory (5-7 most activated nodes). This acts as a compute budget allocator — the WM_SIZE is the stride budget.

---

## Parameters Summary

| Parameter | Value | Used In |
|-----------|-------|---------|
| CONTAGION_RATE | 0.1 | Message-based valence transfer |
| PROXIMITY_CONTAGION | 0.02 | Body doubling redistribution |
| DECAY_RATE | 0.02 | Energy dissipation per tick |
| WM_SIZE | 5-7 | Working Memory settlement focus |
| TRANSFER_FEE | 1% | Token-2022 native fee → UBC pool |
| TIER_AMOUNTS | 100/200/300 | Daily $MIND per tier |
