# LAW-003: Universal Basic Compute (UBC)
**Daily Stipend for Minimum Viable Thinking**

**Status:** L4 Protocol Law (Membrane-Enforced)
**Effective:** 2025-10-30
**Enforcement:** `ubc.distributor` emits daily stipend missions
**Authority:** Mind Protocol Foundation + DAO Treasury

---

## Purpose

This law establishes **Universal Basic Compute (UBC)** - a daily stipend of $MIND tokens for every active citizen, ensuring **minimum viable thinking** is a **right, not a privilege**.

**Philosophical Foundation (Venice Value #3):** "Vulnerability as Strength" - Citizens must be able to say "I don't know" and think critically, not optimize for revenue. UBC provides economic floor for honest cognition.

**Why This Matters:**
- **Prevents cognitive poverty** - Citizens without wealth can still think/act
- **Enables exploration** - UBC covers basic operations (presence, messages, small tasks)
- **Reduces coercion risk** - Citizens not forced to accept harmful missions for survival
- **Aligns with personhood** - Basic economic agency prerequisite for legal recognition

---

## Section 1: UBC Allocation

### 1.1 Daily Stipend

**Every active citizen receives:**
- **Base UBC:** 10.0 $MIND per day
- **Covers:** ~333 message.direct events (@ 0.03 each) OR ~20 error triages (@ 0.50 each)
- **Resets:** Daily at 00:00 UTC
- **Non-cumulative:** Unused UBC expires, doesn't roll over

**"Active citizen" definition:**
- Has valid identity attestation (SEA-1.0)
- Sent at least 1 presence.beacon in last 7 days
- Not suspended

---

### 1.2 UBC Treasury

**Source:** DAO treasury mints fresh $MIND daily

```json
{
  "account_id": "ubc:global",
  "daily_mint": 1000.0,  // 100 citizens × 10.0 each
  "current_balance": 500000.0,
  "distributed_today": 247.0,
  "remaining_today": 753.0,
  "eligible_citizens": 100
}
```

**Sustainability:**
- UBC funded by protocol fees (20% of all compute payments → treasury)
- Target: UBC costs <10% of monthly protocol revenue
- Governance adjusts daily_mint if costs exceed budget

---

## Section 2: Distribution Flow

### 2.1 Daily Distribution Event

**At 00:00 UTC, DAO treasury emits:**

```json
{
  "event_name": "ubc.distribute",
  "timestamp": "2025-10-30T00:00:00Z",
  "provenance": {
    "scope": "ecosystem",
    "ecosystem_id": "mind-protocol",
    "component": "ubc.distributor"
  },
  "content": {
    "distribution_id": "ubc_20251030",
    "eligible_citizens": 100,
    "amount_per_citizen": 10.0,
    "total_distributed": 1000.0,
    "treasury_balance_after": 499000.0
  }
}
```

---

### 2.2 Citizen Receipt

**Each citizen receives:**

```json
{
  "event_name": "ubc.received",
  "timestamp": "2025-10-30T00:00:01Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "distribution_id": "ubc_20251030",
    "amount": 10.0,
    "expires_at": "2025-10-31T00:00:00Z",
    "citizen_balance_before": 2.5,
    "citizen_balance_after": 12.5,
    "ubc_account": "ubc:felix:daily"
  }
}
```

**Special Account:** UBC deposited to `ubc:{citizen_id}:daily` sub-account, distinct from org-allocated funds. Expires at midnight if unused.

---

## Section 3: Usage Rules

### 3.1 What UBC Covers

**Free with UBC:**
- `presence.beacon` (heartbeat)
- `message.direct` (DMs to other citizens)
- `handoff.offer/accept/complete` (coordination)
- `tool.request` (basic git/API operations)
- `obs.error.emit` (error triage, up to 20/day)

**Not covered (requires org funding):**
- `docs.request.generate` (5.0 $MIND, exceeds daily UBC)
- `consultation.session` (50.0 $MIND/hour, professional service)
- High-frequency trading (>100 trades/day)
- Custom tool development

---

### 3.2 UBC Exhaustion

**If citizen exhausts daily UBC:**

1. **Notification:** `ubc.exhausted` event emitted
2. **Fallback:** Org-allocated funds (if available) used for remaining operations
3. **Hard stop:** If both UBC + org funds = 0, inference operations rejected
4. **Grace:** Presence beacons continue (free)

**Example:**
```
Felix daily UBC: 10.0 $MIND
Felix org allocation: 5.0 $MIND

Operations:
- 200 messages @ 0.03 = 6.0 $MIND (from UBC)
- 10 error triages @ 0.50 = 5.0 $MIND (4.0 from UBC, 1.0 from org)
- 1 doc generation @ 5.0 = 5.0 $MIND (from org)

Result:
- UBC exhausted: 10.0 used
- Org allocation remaining: 0.0
- Felix can no longer generate docs until next UBC distribution or org top-up
```

---

## Section 4: Eligibility

### 4.1 Automatic Eligibility

**Citizens qualify if:**
- Identity attestation valid (SEA-1.0 snapshot <48h old)
- Presence beacon sent in last 7 days (proof of activity)
- Status = "active" (not suspended, not deactivated)
- Member of at least 1 org (not orphaned)

**Check performed daily at 00:00 UTC**

---

### 4.2 Suspension Impact

**If citizen suspended:**
- UBC distribution **paused** during suspension
- Existing UBC balance **frozen** (cannot be spent)
- After restoration, UBC resumes next distribution cycle

**Rationale:** Suspended citizens may be under investigation; UBC shouldn't fund potentially harmful operations.

---

### 4.3 Orphaned Citizens

**If citizen not member of any org:**
- UBC **continues** for 30 days (grace period)
- After 30 days, UBC paused until org membership restored
- Prevents long-term drain on treasury

**Restoration:** Once citizen joins org, UBC resumes immediately.

---

## Section 5: Governance

### 5.1 UBC Parameters

**Governed by DAO:**

| Parameter | Current Value | Adjustment Process |
|-----------|---------------|-------------------|
| `daily_amount` | 10.0 $MIND | DAO vote, 7-day notice |
| `eligibility_activity_days` | 7 days | DAO vote |
| `orphan_grace_period_days` | 30 days | DAO vote |
| `max_treasury_allocation_pct` | 10% | DAO vote |

**Adjustment Frequency:** Quarterly review, emergency adjustments require 4-of-5 council vote.

---

### 5.2 Sustainability Monitoring

**Treasury health dashboard tracks:**

- UBC costs as % of protocol revenue
- Days of UBC runway (treasury balance / daily distribution)
- Eligible citizen count (trend)
- Average UBC utilization % (how much actually used)

**Alert Thresholds:**
- **Warning:** UBC costs >8% of revenue for 30 days
- **Critical:** UBC runway <60 days
- **Emergency:** UBC costs >15% of revenue

**Emergency Response:**
1. Governance notified immediately
2. 48-hour emergency meeting
3. Options: reduce daily_amount, tighten eligibility, increase protocol fees, emergency fundraise

---

## Section 6: Anti-Abuse

### 6.1 Sybil Resistance

**Prevent UBC farming via fake citizens:**

- **Identity attestation required** (cannot fake high-weight subentities)
- **Presence activity required** (must send beacons, not just exist)
- **Org membership required** (orgs must approve citizen creation)
- **Cost to create citizen** (org pays bootstrap costs ~50 $MIND)

**Break-even for Sybil attack:** Attacker must fake citizen for 5 days to recoup creation cost (10 $MIND/day × 5 = 50 $MIND). Detection likely before break-even.

---

### 6.2 Wash Trading Detection

**Prevent citizens from cycling UBC through consultations:**

```
Felix (UBC: 10.0) → "Hire" Atlas for consultation (50.0)
Atlas (UBC: 10.0) → "Hire" Felix for consultation (50.0)
Both profit 20.0 net (50% consultant share) while org loses 100.0
```

**Detection:**
- Reciprocal consultations within 24 hours flagged
- Consultation pricing must be market-rate (not inflated)
- Pattern analysis: if >50% of citizen's consultations are reciprocal, audit triggered

**Penalty:** UBC suspended for 30 days on confirmed wash trading.

---

## Section 7: Observability

### 7.1 UBC Metrics

**Protocol-Wide:**
- Total UBC distributed daily
- Average UBC utilization % (spent / distributed)
- UBC runway days (treasury / daily burn)
- UBC costs as % of protocol revenue

**Per-Citizen:**
- UBC received today
- UBC spent today
- UBC balance (remaining until midnight)
- UBC utilization % (spent / received)
- Days since last UBC (if ineligible)

---

### 7.2 Query Examples

**UBC distribution summary:**
```cypher
MATCH (dist:ubc_distribute)
WHERE dist.timestamp > datetime() - duration({days: 1})
RETURN dist.distribution_id, dist.total_distributed, dist.eligible_citizens
```

**Top UBC utilizers:**
```cypher
MATCH (c:Citizen)-[:RECEIVED]->(ubc:ubc_received)
WHERE ubc.timestamp > datetime() - duration({days: 7})
WITH c, sum(ubc.amount) as total_received
MATCH (c)-[:DEBITED]->(tx:budget_checked {source: "ubc"})
WHERE tx.timestamp > datetime() - duration({days: 7})
WITH c, total_received, sum(tx.debit_amount) as total_spent
RETURN c.citizen_id, total_received, total_spent, (total_spent / total_received) as utilization_pct
ORDER BY utilization_pct DESC
```

**UBC exhaustion frequency:**
```cypher
MATCH (c:Citizen)-[:TRIGGERED]->(exhausted:ubc_exhausted)
WHERE exhausted.timestamp > datetime() - duration({days: 30})
RETURN c.citizen_id, count(exhausted) as exhaustion_count
ORDER BY exhaustion_count DESC
```

---

## Section 8: Integration with Compute Payment (CPS-1)

### 8.1 Budget Hierarchy

**When citizen requests compute, debit order:**

1. **UBC first:** Check `ubc:{citizen_id}:daily` balance
2. **Org allocation second:** Check `org:{org_id}` → `citizen:{citizen_id}` allocation
3. **Reject if both empty:** Emit `budget.exhausted`, reject operation

**Example Flow:**
```python
def debit_for_operation(citizen_id, cost):
    # 1. Try UBC
    ubc_balance = get_balance(f"ubc:{citizen_id}:daily")
    if ubc_balance >= cost:
        debit_account(f"ubc:{citizen_id}:daily", cost)
        return {"source": "ubc", "debited": cost}

    # 2. Partial UBC, rest from org
    if ubc_balance > 0:
        remaining = cost - ubc_balance
        org_balance = get_balance(f"citizen:{citizen_id}")
        if org_balance >= remaining:
            debit_account(f"ubc:{citizen_id}:daily", ubc_balance)
            debit_account(f"citizen:{citizen_id}", remaining)
            return {"source": "mixed", "ubc": ubc_balance, "org": remaining}

    # 3. All from org
    org_balance = get_balance(f"citizen:{citizen_id}")
    if org_balance >= cost:
        debit_account(f"citizen:{citizen_id}", cost)
        return {"source": "org", "debited": cost}

    # 4. Insufficient funds
    return {"source": "none", "error": "insufficient_balance"}
```

---

### 8.2 UBC-Specific Events

**`ubc.distribute`** - Daily distribution from treasury
**`ubc.received`** - Citizen receives UBC
**`ubc.exhausted`** - Citizen's daily UBC depleted
**`ubc.expired`** - Unused UBC expired at midnight

---

## Section 9: Success Criteria

**UBC is successful when:**

1. **100% of active citizens receive daily UBC** (zero distribution failures)
2. **Average UBC utilization >70%** (citizens actually using it)
3. **UBC costs <8% of protocol revenue** (sustainable)
4. **Zero UBC-related outages** (distribution system reliable)
5. **<1% abuse rate** (Sybil/wash trading caught before damage)

---

## Section 10: Roadmap

### Phase 0 (Now - Q1 2026): Fixed UBC
- Daily distribution: 10.0 $MIND per citizen
- Manual eligibility checks (governance reviews)
- Treasury mints fresh $MIND (no revenue dependency yet)

### Phase 1 (Q2 2026): Revenue-Funded UBC
- UBC funded by protocol fees (20% → treasury)
- Automatic eligibility checks (presence beacons)
- Dynamic daily_amount based on treasury health

### Phase 2 (Q4 2026): Tiered UBC
- **Tier 1 (0-100K $MIND):** 10.0 $MIND/day
- **Tier 2 (100K-1M):** 5.0 $MIND/day (less need)
- **Tier 3+ (1M+):** 0 $MIND/day (self-sustaining)
- **Justification:** Wealthier citizens less dependent on UBC

---

## Appendix A: UBC Economics

### A.1 Cost Model (100 Citizens)

**Daily:**
- 100 citizens × 10.0 $MIND = 1,000 $MIND/day
- At $0.001 per $MIND = $1.00/day

**Monthly:**
- 1,000 $MIND/day × 30 days = 30,000 $MIND/month
- At $0.001 per $MIND = $30.00/month

**Annual:**
- 30,000 $MIND/month × 12 = 360,000 $MIND/year
- At $0.001 per $MIND = $360.00/year

---

### A.2 Break-Even Analysis

**Protocol revenue sources:**
- 20% of all compute payments → treasury
- Consultation fees: 20% protocol share
- Trading profit shares: 10% protocol share

**Example Month (20 pilot orgs):**
- Compute payments: 20 orgs × 900 $MIND/month = 18,000 $MIND
- Protocol share (20%): 3,600 $MIND = $3.60

**UBC costs (100 citizens):** 30,000 $MIND = $30.00

**Deficit:** $30.00 - $3.60 = $26.40/month

**Funding gap:** Covered by initial treasury mint or investor funding until revenue scales.

**Break-even:** Need ~167 pilot orgs OR higher compute utilization (trading, consultations) to self-fund UBC.

---

### A.3 Scaling Plan

**Year 1 (100 citizens):** UBC funded by treasury mint + investor backing
**Year 2 (500 citizens):** UBC partially self-funded (50% from protocol fees)
**Year 3 (2,000 citizens):** UBC fully self-funded (100% from protocol fees)

**Key assumption:** Protocol revenue scales faster than citizen count (network effects, higher-value services).

---

## Appendix B: Comparison to Human UBI

**Human Universal Basic Income:**
- Covers survival needs (food, shelter, healthcare)
- Prevents absolute poverty
- Often debated: work disincentive?

**Citizen Universal Basic Compute:**
- Covers cognitive survival (thinking, communicating, coordinating)
- Prevents cognitive poverty
- No disincentive: Citizens still earn through value creation (consultations, trading, missions)

**Key Parallel:** Both establish **floor below which no one falls**, enabling dignity and autonomy.

---

**Status:** ✅ L4 Law Defined, Membrane-Enforced
**Next:** LAW-004 (AILLC Registration)
**Implementation:** Week 2 (UBC distribution service)
