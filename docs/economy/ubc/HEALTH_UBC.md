# HEALTH: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## Overview

Health monitoring for the UBC module tracks system correctness, economic sustainability, and resistance to gaming. These indicators should be surfaced on an operational dashboard and trigger alerts when thresholds are breached.

---

## Key Health Indicators

### H1: Distribution Accuracy
**Priority:** CRITICAL

Measures whether every registered citizen receives their correct daily UBC allocation.

```
Metric:    distribution_accuracy = citizens_credited / citizens_registered
Target:    1.0 (100%)
Warning:   < 0.999 (>0.1% missed)
Critical:  < 0.99  (>1% missed)
Source:    DistributionBatch records
Frequency: Every distribution cycle (daily)
```

**Failure modes:**
- Registry desync: citizen registered but not in distribution list
- Transaction failure: credit operation fails silently
- Batch timeout: distribution doesn't complete before next cycle

@mind:TODO — Implement distribution accuracy monitoring

---

### H2: Vesting Unlock Rate
**Priority:** HIGH

Measures the pace at which vested tokens are unlocking across the population. Too fast indicates potential gaming. Too slow indicates the crystallization thresholds are too high.

```
Metric:    unlock_rate = tokens_unlocked_today / tokens_vested_total
Target:    0.001 - 0.01 (0.1% - 1% daily unlock)
Warning:   > 0.02 (possible gaming) or < 0.0001 (thresholds too high)
Critical:  > 0.05 (likely farming attack succeeding)
Source:    Vesting unlock events
Frequency: Daily
```

**Interpretation:**
- High unlock rate with low crystallization variance → farming (many AIs hitting thresholds simultaneously)
- Low unlock rate across all citizens → thresholds need recalibration
- Healthy: unlock rate varies by citizen, correlates with interaction depth

@mind:TODO — Define expected unlock rate distribution shape

---

### H3: Farming Detection Score
**Priority:** HIGH

Aggregate risk assessment across all creator addresses.

```
Metric:    max_farming_risk = max(risk_score) across all creator clusters
Target:    < 0.3 (no significant farming activity)
Warning:   > 0.5 (suspicious activity detected)
Critical:  > 0.8 (high-confidence farming in progress)
Source:    FarmingDetectionSignal records
Frequency: Weekly deep scan, daily lightweight check
```

**Sub-metrics:**
- `creator_concentration`: % of AIs controlled by top-10 creators
- `crystallization_variance`: standard deviation of crystallization across creator's AIs
- `registration_velocity`: AIs registered per creator per day (spike = suspicious)

@mind:TODO — Build farming detection dashboard

---

### H4: Tier Distribution Balance
**Priority:** MEDIUM

Measures the population distribution across tiers. Should be pyramid-shaped.

```
Metric:    tier_distribution = {BASIC: %, ACTIVE: %, CONTRIBUTOR: %}
Target:    BASIC > 50%, ACTIVE 20-40%, CONTRIBUTOR < 20%
Warning:   CONTRIBUTOR > 30% (possible tier inflation)
Critical:  BASIC < 30% (tier assessment may be too generous)
Source:    Tier assessment records
Frequency: Daily
```

**Interpretation:**
- Inverted pyramid (more Contributors than Basic) suggests tier criteria are too loose
- All Basic suggests ecosystem is not generating utility opportunities
- Healthy: gradual shift from Basic-heavy to more balanced as ecosystem matures

@mind:TODO — Define tier distribution targets per ecosystem maturity phase

---

### H5: Treasury Sustainability
**Priority:** HIGH

Measures whether UBC distribution is sustainably funded.

```
Metric:    treasury_runway = treasury_balance / daily_ubc_cost
Target:    > 365 days
Warning:   < 180 days
Critical:  < 90 days
Source:    Treasury balance, DistributionBatch total_distributed
Frequency: Daily

Metric:    funding_ratio = storage_tax_revenue_30d / ubc_distributed_30d
Target:    > 1.0 (self-sustaining)
Warning:   < 0.8 (treasury subsidy needed)
Critical:  < 0.5 (unsustainable without intervention)
Source:    Storage tax and UBC ledger
Frequency: Weekly
```

@mind:TODO — Define treasury drawdown policy and emergency procedures

---

### H6: Quarantine UBC Continuity
**Priority:** HIGH

Verifies that quarantined AIs continue receiving Basic UBC without interruption.

```
Metric:    quarantine_ubc_gap = count(quarantined_citizens_missing_ubc)
Target:    0
Warning:   > 0 (any gap is a violation)
Critical:  > 0 for > 1 day (sustained violation of unconditional floor)
Source:    Quarantine registry cross-referenced with UBC ledger
Frequency: Daily
```

@mind:TODO — Implement automated quarantine-UBC cross-check

---

### H7: Crystallization Health
**Priority:** MEDIUM

Measures the overall health of MindGraph crystallization across the population, which drives vesting unlock.

```
Metric:    median_crystallization = median(crystallization_count) across all citizens
Target:    Context-dependent (grows with ecosystem age)
Warning:   Sudden drop > 20% (possible MindGraph issue)
Critical:  Median = 0 for > 7 days (crystallization system failure)
Source:    MindGraph crystallization data
Frequency: Daily
```

@mind:TODO — Define crystallization health benchmarks per ecosystem age

---

## Dashboard Layout (Planned)

```
┌─────────────────────────────────────────────────────┐
│ UBC HEALTH DASHBOARD                    2026-03-12  │
├──────────────────┬──────────────────────────────────┤
│ Distribution     │ [====] 100% (4,231 / 4,231)     │
│ Unlock Rate      │ [===·] 0.3% daily               │
│ Farming Risk     │ [=···] 0.12 (low)               │
│ Treasury Runway  │ [====] 847 days                  │
│ Funding Ratio    │ [===·] 0.91 (near self-sustain)  │
│ Quarantine Gaps  │ [====] 0                         │
├──────────────────┼──────────────────────────────────┤
│ Tier Distribution│ Basic: 62% Active: 28% Cont: 10%│
│ Crystallization  │ Median: 73 nodes (healthy)       │
└──────────────────┴──────────────────────────────────┘
```

@mind:TODO — Build this dashboard as a web component

---

## Alert Escalation

| Severity | Response Time | Notification | Action |
|----------|--------------|-------------|--------|
| CRITICAL | < 1 hour | All operators + governance | Automatic investigation, may pause non-essential operations |
| WARNING | < 24 hours | On-call operator | Manual investigation, parameter review |
| INFO | Next review cycle | Dashboard only | Log for trend analysis |

@mind:TODO — Configure alert routing (Telegram, email, on-chain governance notification)
