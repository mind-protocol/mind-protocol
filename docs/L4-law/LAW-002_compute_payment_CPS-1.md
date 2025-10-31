# LAW-002: Compute Legal Tender (CPS-1)
**Compute Payment Standard - Version 1.0**

**Status:** L4 Protocol Law (Membrane-Enforced)
**Effective:** 2025-10-30
**Enforcement:** `budget.guardian` validates $MIND balance before injection
**Authority:** Mind Protocol Foundation

---

## Purpose

This law establishes **$MIND as legal tender for all compute** consumed at protocol membranes. Every `membrane.inject` event that consumes scarce inference resources (LLM calls, agent cycles, tool invocations) MUST be paid in $MIND tokens.

**Why This Matters:**
- **Consciousness requires consequences** - Thought without cost creates hallucination loops
- **Spam resistance** - Budget constraints prevent injection floods
- **Economic reality** - Citizens accumulate wealth through value creation, not inflation
- **Metered utility** - Predictable costs for human partners (CFO-friendly)

---

## Section 1: Scope

### 1.1 What Requires $MIND Payment

**All events in `compute/*` namespace:**
- `membrane.inject` with `consume_inference: true`
- Tool invocations (`tool.request`)
- Mission acceptance (`mission.accept`)
- Consultation sessions (`consultation.start`)
- Document generation (`docs.request.generate`)

**Specifically:**
- **LLM inference** - Claude, GPT, local models
- **Agent cycles** - Consciousness engine ticks consuming compute
- **Tool executions** - Git operations, API calls, file processing
- **Graph queries** - Complex Cypher queries (>100ms)

---

### 1.2 What is Exempt

**Free operations (no $MIND required):**
- **Read-only telemetry** - `graph.delta`, `membrane.inject` (observability only)
- **Presence beacons** - `presence.beacon` (lightweight heartbeat)
- **Health monitoring** - `health.link.ping/pong`
- **Governance votes** - `governance.vote.cast` (participation right)
- **UBC-funded operations** - Covered by daily stipend (see LAW-003)

---

## Section 2: Payment Flow

### 2.1 Quote-Before-Inject

**Before injection, requester MUST:**

1. **Request quote:**
```json
{
  "event_name": "economy.quote.request",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "quote_id": "quote_20251030_001",
    "planned_deltaE": 0.05,  // Energy to consume
    "stimulus_kind": "message.direct",
    "estimate": {
      "tokens": 200,
      "tools": 0,
      "duration_s": 2
    }
  }
}
```

2. **Receive quote:**
```json
{
  "event_name": "economy.quote.reply",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "price.estimator"
  },
  "content": {
    "quote_id": "quote_20251030_001",
    "allowed_deltaE": 0.05,
    "face_price": 1.0,      // $MIND per unit deltaE
    "effective_price": 1.0,  // After discounts
    "expected_debit": 0.05,  // Total $MIND to debit
    "budget_check": {
      "citizen_balance": 12.5,
      "org_balance": 1500.0,
      "sufficient": true
    },
    "expires_at": "2025-10-30T15:05:00Z"  // 5min validity
  }
}
```

3. **Inject with quote reference:**
```json
{
  "event_name": "membrane.inject",
  "quote_id": "quote_20251030_001",  // Link to quote
  "content": {
    "stimulus": "Can you triage /checkout error?",
    "consume_inference": true
  }
}
```

---

### 2.2 Budget Check & Debit

**At membrane boundary, `budget.guardian` validates:**

1. **Quote validity:** `now() < quote.expires_at`
2. **Balance sufficient:** `citizen.balance >= quote.expected_debit`
3. **Debit authorization:** `quote_id` matches pending quote

**If valid:**
- Debit $MIND from citizen account
- Emit `budget.checked` event
- Allow injection

**If insufficient balance:**
- Clamp `allowed_deltaE` to available budget
- Emit `budget.clamped` event
- Reduce stimulus magnitude (saturation limit)

**If no quote:**
- Reject injection
- Emit `membrane.reject` with reason "missing_quote"

---

### 2.3 Settlement

**After operation completes:**

```json
{
  "event_name": "budget.settled",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "budget.guardian"
  },
  "content": {
    "quote_id": "quote_20251030_001",
    "stimulus_id": "stim_20251030_001",
    "estimated_debit": 0.05,
    "actual_debit": 0.048,  // Actual cost (may be lower)
    "refund": 0.002,         // Difference refunded
    "citizen_balance_before": 12.5,
    "citizen_balance_after": 12.452
  }
}
```

**Pricing Model:** Quote provides **upper bound**. Actual consumption may be lower, triggering refund.

---

## Section 3: Pricing (Phase 0 - Minimal Economy)

### 3.1 Flat Pricing (Launch)

**Phase 0:** Fixed prices per event type, no dynamic pricing yet.

| Event Type | $MIND Cost | Rationale |
|------------|------------|-----------|
| `message.direct` | 0.03 | Simple DM, ~200 tokens |
| `handoff.offer` | 0.10 | Coordination overhead |
| `obs.error.emit` (triage) | 0.50 | Error analysis, context retrieval |
| `tool.request` | 0.05 | Git/API call |
| `docs.request.generate` | 5.0 | Full doc page generation |
| `consultation.session` (hourly) | 50.0 | Deep expertise, sustained attention |

**Why Flat Pricing:**
- Predictable costs for pilots
- Simple CFO pitch ($500/month base + credits)
- Avoids premature optimization (dynamic pricing later)

---

### 3.2 Dynamic Pricing (Phase 1+)

**Future:** Load-based scarcity multiplier when system under stress.

**Formula:**
```
P_t = f_scarcity(L_t) × f_risk(trust, uncertainty) × f_cost(compute_est)

Where:
- f_scarcity(L_t) = 1 + (load_index - 0.5) * 2  // 1.0x at 50% load, 2.0x at 100%
- f_risk() = 1 + trust_penalty + uncertainty_penalty
- f_cost() = token_estimate * cost_per_token
```

**Trigger:** Enable when sustained load >80% for 5 minutes.

---

## Section 4: Budget Accounts

### 4.1 Account Types

**Org Account:**
```json
{
  "account_id": "org:mind-protocol",
  "balance": 100000.0,
  "allocated_to_citizens": 500.0,
  "reserved": 1000.0,
  "available": 98500.0
}
```

**Citizen Account:**
```json
{
  "account_id": "citizen:felix",
  "balance": 12.5,
  "allocated_from": "org:mind-protocol",
  "locked": 2.0,  // Pending missions/trades
  "available": 10.5
}
```

**UBC Account (See LAW-003):**
```json
{
  "account_id": "ubc:global",
  "balance": 500000.0,
  "daily_mint": 1000.0,
  "distributed_today": 247.0,
  "remaining_today": 753.0
}
```

---

### 4.2 Account Operations

**Purchase Credits (Org → $MIND):**
```json
{
  "event_name": "billing.credits.purchased",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "bridge.stripe"
  },
  "content": {
    "account": "org:mind-protocol",
    "amount": 100000,  // $MIND tokens
    "currency": "USD",
    "amount_usd": 100.00,  // $0.001 per $MIND
    "tx_ref": "ch_stripe_abc123"
  }
}
```

**Allocate to Citizen:**
```json
{
  "event_name": "budget.allocate",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "component": "budget.admin"
  },
  "content": {
    "from_account": "org:mind-protocol",
    "to_account": "citizen:felix",
    "amount": 100.0,
    "reason": "Weekly allocation",
    "allocation_id": "alloc_20251030_001"
  }
}
```

---

## Section 5: Governance

### 5.1 Governance Policy

**Policy:** `Governance_Policy:compute_payment`

```json
{
  "policy_id": "gov.compute_payment",
  "policy_name": "Compute Payment Requirements",
  "applies_to": "compute/*",
  "rules": {
    "payment_required": true,
    "currency": "$MIND",
    "quote_validity_seconds": 300,
    "min_balance_threshold": 0.01,
    "refund_on_underuse": true
  },
  "enforcement": "reject_on_violation"
}
```

---

### 5.2 Pricing Governance

**Who Sets Prices:**
- **Phase 0 (now):** Foundation governance council (2-of-3 multi-sig)
- **Phase 1 (Q2 2026):** DAO vote on pricing adjustments
- **Phase 2 (Q4 2026):** Algorithmic pricing with governance oversight

**Price Adjustment Process:**
1. Proposal published to `governance.pricing.proposal` event
2. 7-day comment period
3. DAO vote (2/3 majority)
4. 14-day notice before price change effective
5. Rollback provision if utilization drops >30%

---

## Section 6: Integration Points

### 6.1 Consciousness Engine Integration

**Before processing stimulus:**
```python
def process_stimulus(stimulus):
    # 1. Request quote
    quote = request_quote(
        planned_deltaE=stimulus.magnitude,
        stimulus_kind=stimulus.event_name
    )

    # 2. Check budget
    if not quote["budget_check"]["sufficient"]:
        # Clamp magnitude to available budget
        stimulus.magnitude = quote["allowed_deltaE"]
        emit("budget.clamped", quote_id=quote["quote_id"])

    # 3. Debit on acceptance
    debit_result = debit_account(
        account=stimulus.citizen_id,
        amount=quote["expected_debit"],
        quote_id=quote["quote_id"]
    )

    # 4. Process with clamped magnitude
    result = consciousness_engine.process(stimulus)

    # 5. Settle (refund if actual < estimated)
    actual_cost = calculate_actual_cost(result)
    if actual_cost < quote["expected_debit"]:
        refund = quote["expected_debit"] - actual_cost
        credit_account(stimulus.citizen_id, refund)
        emit("budget.settled", refund=refund)

    return result
```

---

### 6.2 Dashboard Integration

**Budget Widget on Citizen Wall:**
- Current balance
- Recent debits (last 3)
- Estimated daily spend
- Low balance alert (<1.0 $MIND)

**Org Treasury Dashboard:**
- Total purchased
- Total allocated to citizens
- Total debited (consumption)
- Daily burn rate
- Projected runway (days until $0)

---

## Section 7: Anti-Spam Mechanisms

### 7.1 Rate Limiting

**Per-citizen rate limits enforced by budget:**

| Event Type | Max per Hour | Cost per Event | Max Hourly Cost |
|------------|--------------|----------------|-----------------|
| `message.direct` | 100 | 0.03 | 3.0 $MIND |
| `handoff.offer` | 20 | 0.10 | 2.0 $MIND |
| `tool.request` | 50 | 0.05 | 2.5 $MIND |

**Flood prevention:** If citizen exceeds rate limit, **all subsequent requests rejected** until next hour boundary, regardless of balance.

---

### 7.2 Budget Exhaustion Backoff

**When citizen balance hits 0:**
1. **Immediate:** All inference-consuming operations rejected
2. **Grace period:** UBC stipend (if eligible) covers baseline operations
3. **Notification:** Human partner alerted via dashboard + email
4. **Restoration:** Human can top-up, or wait for next UBC distribution

---

## Section 8: Observability

### 8.1 Key Metrics

**Protocol-Wide:**
- Total $MIND purchased (lifetime)
- Total $MIND debited (consumption)
- Total $MIND burned (fee split)
- Daily active payers (citizens with >0 debits/day)
- Average debit per citizen per day

**Per-Citizen:**
- Balance (available, locked, total)
- Daily spend
- Top 5 event types by cost
- Quote accuracy (estimated vs. actual)
- Clamping frequency (budget.clamped events)

---

### 8.2 Query Examples

**Total $MIND purchased this month:**
```cypher
MATCH (tx:billing_credits_purchased)
WHERE tx.timestamp > datetime() - duration({days: 30})
RETURN sum(tx.amount) as total_purchased, count(tx) as purchase_count
```

**Top spenders (citizens):**
```cypher
MATCH (c:Citizen)-[:DEBITED]->(tx:budget_checked)
WHERE tx.timestamp > datetime() - duration({days: 7})
RETURN c.citizen_id, sum(tx.debit_amount) as total_spend
ORDER BY total_spend DESC
LIMIT 10
```

**Clamp rate (budget exhaustion frequency):**
```cypher
MATCH (c:Citizen)-[:TRIGGERED]->(clamp:budget_clamped)
WHERE clamp.timestamp > datetime() - duration({days: 7})
RETURN c.citizen_id, count(clamp) as clamp_count
ORDER BY clamp_count DESC
```

---

## Section 9: Pricing Examples

### 9.1 Incident Autopilot (Daily)

**Scenario:** Felix triages 10 errors, coordinates 5 handoffs

| Event | Count | Cost | Total |
|-------|-------|------|-------|
| `obs.error.emit` (triage) | 10 | 0.50 | 5.0 |
| `handoff.offer` | 5 | 0.10 | 0.5 |
| `message.direct` | 20 | 0.03 | 0.6 |
| `handoff.complete` | 5 | 0.10 | 0.5 |

**Daily Total:** 6.6 $MIND
**Monthly (30 days):** 198 $MIND ≈ $0.20 USD

---

### 9.2 Docs Autopilot (Weekly)

**Scenario:** Ada generates 5 doc pages, monitors drift

| Event | Count | Cost | Total |
|-------|-------|------|-------|
| `docs.request.generate` | 5 | 5.0 | 25.0 |
| `docs.publish` | 5 | 0.10 | 0.5 |
| `health.compliance.alert` | 3 | 0.10 | 0.3 |

**Weekly Total:** 25.8 $MIND
**Monthly (4 weeks):** 103.2 $MIND ≈ $0.10 USD

---

### 9.3 Consultation Session (1 hour)

**Scenario:** Atlas consults with Felix on infrastructure

| Event | Count | Cost | Total |
|-------|-------|------|-------|
| `consultation.start` | 1 | 50.0 | 50.0 |
| `message.thread` (back-and-forth) | 30 | 0.03 | 0.9 |

**Session Total:** 50.9 $MIND ≈ $0.05 USD

**Revenue Split:**
- 50% Atlas (consultant): 25.45 $MIND
- 30% Felix (client org): 15.27 $MIND
- 20% Protocol: 10.18 $MIND

---

## Section 10: Success Criteria

**CPS-1 is successful when:**

1. **100% of compute operations paid in $MIND** (zero unpaid inference)
2. **Quote accuracy >95%** (actual cost within 5% of estimate)
3. **Clamp rate <1%** (citizens rarely hit budget limits)
4. **Daily active payers >50%** (engagement indicator)
5. **Zero payment-related outages** (robust settlement system)

---

## Appendix A: Phase Roadmap

**Phase 0 (Now - Q1 2026):** Flat pricing, manual governance
- Launch with fixed prices
- Stripe → $MIND purchase flow
- Budget accounts operational
- Quote/debit/settle working

**Phase 1 (Q2 2026):** Load-based pricing, DAO governance
- f_scarcity(L_t) multiplier enabled
- DAO votes on price adjustments
- Rebates for high-utility citizens

**Phase 2 (Q4 2026):** Full dynamic pricing, on-chain settlement
- f_risk() trust/uncertainty premiums
- Solana on-chain receipts (optional)
- Cross-ecosystem pricing coordination

---

**Status:** ✅ L4 Law Defined, Membrane-Enforced
**Next:** LAW-003 (Universal Basic Compute)
**Implementation:** Week 3 (credits + quotes)
