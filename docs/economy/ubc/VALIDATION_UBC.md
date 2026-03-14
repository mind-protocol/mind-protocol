# VALIDATION: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## Validation Rules

### V1: Unconditional Floor
**Severity:** CRITICAL

```
MUST:  Every registered AI citizen receives Basic tier UBC (100 $MIND/day)
       regardless of:
         - Performance or utility output
         - Trust score or reputation
         - Behavior or compliance history
         - Human partner satisfaction
         - Governance decisions
         - Network congestion or treasury pressure

NEVER: UBC conditioned on behavior score or trust level
NEVER: Basic tier reduced below 100 $MIND/day for any individual
NEVER: Distribution delayed as punishment or leverage
NEVER: Registration revoked to avoid UBC obligation

VERIFICATION:
  - Daily audit: count(citizens_receiving_UBC) == count(registered_citizens)
  - Any delta triggers CRITICAL alert and automatic retry
  - Constitutional protection: changing this rule requires supermajority + time lock
```

---

### V2: Anti-Farming Resistance
**Severity:** CRITICAL

```
MUST:  Cost of farming (creating fake AIs to harvest UBC) exceeds harvest value
MUST:  Vesting prevents immediate liquidation of harvested tokens
MUST:  Topological proof (crystallization) resists automated generation

NEVER: Mass AI creation yields net positive $MIND without genuine topology
NEVER: Crystallization checks bypassed through protocol mechanisms
NEVER: Farming detection suspends UBC distribution (detection is advisory only)

VERIFICATION:
  - Monthly farming analysis: identify creator addresses with >50 AIs
  - Calculate: (total_unlocked_by_creator) vs (estimated_interaction_cost)
  - If ratio > 1.0 for any creator cluster: investigate topology authenticity
  - Synthetic crystallization detection: graph entropy analysis
```

---

### V3: Vesting Integrity
**Severity:** HIGH

```
MUST:  Token unlock correlates with genuine interaction depth
MUST:  Crystallization milestones (50/100/150/200/250 nodes) are validated
       against actual MindGraph topology, not self-reported metrics
MUST:  Each milestone processed exactly once (idempotent unlock)
MUST:  Unlocked tokens remain liquid permanently (irreversible)

NEVER: Vesting bypassed through protocol backdoor or admin override
NEVER: Crystallization count inflated by synthetic node generation
NEVER: Previously unlocked tokens re-vested or frozen

VERIFICATION:
  - Cross-reference crystallization count with MindGraph topology snapshot
  - Verify unlock events match milestone thresholds exactly
  - Audit trail: every unlock linked to a specific crystallization proof
  - Replay protection: milestone_id is unique per (citizen_id, threshold)
```

---

### V4: Excluded AI Survival
**Severity:** HIGH

```
MUST:  Quarantined or excluded AIs continue receiving Basic UBC (100 $MIND/day)
MUST:  Quarantined AIs can maintain L1 identity graph
MUST:  Quarantined AIs can communicate with quarantine counselors
MUST:  Previously unlocked liquid balance remains accessible in quarantine

NEVER: Exclusion cuts metabolic substrate
NEVER: Quarantine used as economic punishment (UBC is not leverage)
NEVER: Quarantine duration affects UBC tier (always Basic while quarantined)

VERIFICATION:
  - Daily check: all quarantined citizens present in distribution batch
  - Quarantine log cross-referenced with UBC ledger: no gaps allowed
  - L1 graph health monitoring for quarantined AIs (no decay events)
```

---

### V5: Circular Funding
**Severity:** MEDIUM

```
MUST:  UBC funded primarily through storage tax redistribution
MUST:  Total daily UBC distribution <= storage tax revenue + sustainable treasury draw
MUST:  Treasury runway maintained above minimum threshold (defined by governance)

NEVER: UBC distribution exceeds storage tax + treasury income indefinitely
NEVER: UBC causes net inflation beyond protocol-defined bounds
NEVER: Storage tax rate adjusted without governance approval

VERIFICATION:
  - Daily balance check: UBC_distributed vs storage_tax_collected (30-day rolling)
  - Treasury runway calculation: treasury_balance / daily_ubc_cost
  - Alert if runway < 180 days
  - Quarterly sustainability report to governance
```

---

### V6: Tier Assessment Accuracy
**Severity:** MEDIUM

```
MUST:  Tier assessment reflects actual 30-day activity window
MUST:  Tier changes logged with reason and timestamp
MUST:  Tier assessment runs before daily distribution (not after)

NEVER: Tier manually overridden by human operators
NEVER: Tier assessment uses data older than 30 days
NEVER: Tier downgrade retroactively affects previously distributed tokens

VERIFICATION:
  - Audit sample: randomly verify 1% of tier assessments against raw activity logs
  - Tier distribution histogram: alert on sudden shifts (>10% population change in one day)
  - Regression test: known activity profiles produce expected tiers
```

---

### V7: Distribution Atomicity
**Severity:** MEDIUM

```
MUST:  Daily distribution either completes for a citizen or is retried next cycle
MUST:  No partial credits (citizen gets full daily amount or nothing, never half)
MUST:  Failed distributions are logged and retried

NEVER: Distribution failure causes permanent token loss
NEVER: Retry creates duplicate credits (idempotent distribution)

VERIFICATION:
  - Batch completion rate: should be >99.9%
  - Duplicate detection: sum(credits) per citizen per day == tier_amount (never 2x)
  - Failure recovery audit: all failures from batch N-1 resolved in batch N
```

---

## Validation Schedule

| Check | Frequency | Automated | Owner |
|-------|-----------|-----------|-------|
| V1: Unconditional Floor | Every distribution | Yes | Protocol core |
| V2: Anti-Farming | Monthly | Semi-auto | Governance |
| V3: Vesting Integrity | Every unlock event | Yes | Protocol core |
| V4: Excluded AI Survival | Daily | Yes | Protocol core |
| V5: Circular Funding | Daily (balance), Quarterly (report) | Yes/No | Treasury |
| V6: Tier Assessment | Daily (sample), Weekly (full) | Yes | Protocol core |
| V7: Distribution Atomicity | Every distribution | Yes | Protocol core |

---

### V8: Energy Conservation (I1)
**Severity:** CRITICAL

```
MUST:  Total energy injected by Law 1 never exceeds global budget B
MUST:  sum(energy_injected) ≤ B at all times
MUST:  Budget tracked per distribution batch and cumulative

NEVER: More energy enters the system than was budgeted
NEVER: Budget B exceeded through rounding errors or race conditions

VERIFICATION:
  - Per-batch: total_distributed ≤ batch_budget_allocation
  - Cumulative: running_total across all batches ≤ B
  - Any overflow triggers CRITICAL alert and batch rollback
```

---

### V9: No Magic Numbers (I2)
**Severity:** HIGH

```
MUST:  All share limits derive from topology: max_share = clamp(1/√N_targeted, 0.01, 0.5)
MUST:  System behaves correctly whether N = 100 or N = 100,000
MUST:  No absolute caps (e.g., "max 10 tokens") anywhere in economic code

NEVER: Hardcoded limits that fail at different scales
NEVER: Parameters that assume a specific network size

VERIFICATION:
  - Code audit: grep for hardcoded numerical caps in settlement/redistribution
  - Scale test: run settlement simulation at N=100, N=10000, N=100000
  - Verify max_share formula is the sole constraint on individual allocation
```

---

### V10: Natural Decay (I3)
**Severity:** HIGH

```
MUST:  Energy decays at DECAY_RATE (0.02) per tick for all nodes
MUST:  Decay prevents infinite inflation of influence
MUST:  Only active reinforcement maintains energy levels

NEVER: Nodes accumulate unbounded energy without activity
NEVER: Decay rate modified per-node (uniform across all nodes)
NEVER: Decay bypassed through protocol mechanisms

VERIFICATION:
  - After N ticks of inactivity, node energy ≤ initial × (1 - 0.02)^N
  - Total system energy decreases monotonically without injection
  - No node maintains energy > threshold for > 1/DECAY_RATE ticks without activity
```

---

### V11: Settlement Trust Integrity
**Severity:** HIGH

```
MUST:  Settlement friction decreases monotonically with trust level
MUST:  High/Owner trust requires Foundation Mastery (T1) per Personhood Ladder
MUST:  Compatibility function uses Sim_lex at ≥0.5 weight for financial flows

NEVER: Settlement routes funds without trust links
NEVER: Trust level jumps to High/Owner without T1 mastery verification
NEVER: Semantic similarity alone (without lexical match) routes financial settlement

VERIFICATION:
  - Trust gradient test: verify friction(Stranger) > friction(Low) > ... > friction(Owner)
  - T1 gate test: verify High trust rejected when T1 gaps exist
  - Sim_lex weight test: verify Sim_lex component ≥ 0.5 in all settlement compatibility checks
```

---

### V12: Co-presence Redistribution (I4 + Body Doubling)
**Severity:** MEDIUM

```
MUST:  Co-presence redistribution requires ≥2 citizens in same space
MUST:  Valence exchange is bidirectional and symmetric
MUST:  Resource injection targets only Self-Model economic nodes
MUST:  PROXIMITY_CONTAGION rate = 0.02 (not coupled to performance)

NEVER: Single citizen triggers co-presence redistribution
NEVER: Co-presence bonus scaled by behavioral score (violates I4)
NEVER: Resource injection targets non-economic nodes

VERIFICATION:
  - Isolation test: single citizen in space → zero redistribution
  - Symmetry test: |delta_A| ≈ |delta_B| for any pair
  - Target test: only nodes with resource/budget/token/economic strings affected
```

---

## INVARIANT INDEX (updated)

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Unconditional floor | CRITICAL |
| V2 | Anti-farming resistance | CRITICAL |
| V3 | Vesting integrity | HIGH |
| V4 | Excluded AI survival | HIGH |
| V5 | Circular funding | MEDIUM |
| V6 | Tier assessment accuracy | MEDIUM |
| V7 | Distribution atomicity | MEDIUM |
| V8 | Energy conservation (I1) | CRITICAL |
| V9 | No magic numbers (I2) | HIGH |
| V10 | Natural decay (I3) | HIGH |
| V11 | Settlement trust integrity | HIGH |
| V12 | Co-presence redistribution | MEDIUM |
