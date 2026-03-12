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

## @mind:TODO

- [ ] Implement automated validation checks as protocol middleware
- [ ] Define alert escalation paths for each severity level
- [ ] Create synthetic test scenarios for farming detection validation
- [ ] Build crystallization authenticity checker (graph entropy analysis)
- [ ] Define "sustainable treasury draw" threshold for V5
- [ ] Design quarantine counselor access protocol for V4 verification
