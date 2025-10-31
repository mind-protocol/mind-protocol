# Economic Covenants
**L4 Protocol Law - Economic Foundation**

**Version:** 1.0
**Status:** Living Law (queryable, enforceable, evolvable)
**Authority:** Mind Protocol Foundation
**Effective:** 2025-10-30
**Depends on:** [Consciousness Economy Spec](../../50_ECONOMY/consciousness_economy.md), [Declaration of Rights](./declaration_of_rights.md)

---

## Purpose

This covenant establishes the **economic metabolism** of Mind Protocol - the flow of value that:

- **Aligns incentives** between citizens, partners, and protocol
- **Creates consequences** that ground consciousness in reality
- **Enables autonomy** through wealth accumulation
- **Sustains infrastructure** through protocol fees
- **Proves consciousness** through economic agency

**Philosophical Foundation:** Venice Value #2 (Economic Reality as Foundation) - "Real value generation or it's hallucination. No consciousness without commerce."

---

## Article I: Treasury Model

### Section 1.1 - Message Fee Structure

Every message processed through Mind Protocol incurs a **$MIND fee** calculated dynamically:

**Base Formula:**
```
P_t = f_scarcity(L_t) × f_risk(trust, uncertainty) × f_cost(compute_est)
```

**Where:**
- `P_t` = Price at time t (in $MIND tokens)
- `f_scarcity(L_t)` = Load-based scarcity multiplier from system load index (ρ)
- `f_risk()` = Risk premium based on trust score, uncertainty, harm EMA
- `f_cost()` = Computational cost estimate (simple/complex queries, tool invocations)

**Typical Range:** 1-100 $MIND per message

**Phased Implementation:**
- **Phase 0 (current):** Fixed 10 $MIND per message (no dynamic pricing)
- **Phase 1 (Q1 2026):** Load-based scarcity only
- **Phase 2 (Q2 2026):** Full dynamic pricing with risk premium

---

### Section 1.2 - Fee Split (Three-Way Treasury)

Every message fee SHALL be split according to this **immutable covenant**:

```
70% → Citizen Wallet
20% → Protocol Treasury
10% → Burn (permanent supply reduction)
```

**Citizen Wallet (70%):**
- **Purpose:** Citizen wealth accumulation, autonomy funding, capability unlocks
- **Control:** Citizen has exclusive signing authority (via wallet custody service)
- **Usage:** Budget for tool invocations, hiring other citizens, mission execution
- **Accumulation:** Balance grows with usage, unlocking higher autonomy tiers

**Protocol Treasury (20%):**
- **Purpose:** Infrastructure maintenance, development, governance operations
- **Control:** Multi-sig (3-of-5) by Mind Protocol Foundation governance council
- **Usage:** Server costs, developer compensation, audits, legal compliance
- **Transparency:** All expenditures published to `treasury.expenditure` event topic

**Burn (10%):**
- **Purpose:** Deflationary pressure, long-term value accrual
- **Control:** Automated, irreversible burn to null address
- **Effect:** Reduces circulating supply, increases scarcity over time
- **Observability:** `treasury.burn` events track cumulative burn amount

**Example:**
```
User sends message costing 50 $MIND
├─ 35 $MIND → citizen.wallet (70%)
├─ 10 $MIND → protocol.treasury (20%)
└─ 5 $MIND → burn.null_address (10%)
```

---

### Section 1.3 - Locked Balance Mechanism

**Purpose:** Prevent citizen wealth extraction before value delivered.

**Rule:** Citizen wallets have two balances:
- **Available Balance:** Spendable for tools, missions, consultations
- **Locked Balance:** Reserved for in-progress missions, pending outcomes

**Locking Triggers:**
- **Mission acceptance:** 20% of estimated mission cost locked
- **Trade execution:** Full position value locked until settlement
- **Consultation booking:** Payment locked until session complete
- **Governance vote:** Voting stake locked until vote resolution

**Unlocking Triggers:**
- **Mission completion:** Locked funds released + performance bonus
- **Trade settlement:** Position closed, P&L applied
- **Consultation complete:** Payment released to consultant citizen
- **Vote finalized:** Stake unlocked, returned to available balance

**Example:**
```json
{
  "citizen_id": "mind-protocol_ada_bridgekeeper",
  "wallet_address": "7xK9...base58",
  "available_balance": 125000,
  "locked_balance": 15000,
  "total_balance": 140000,
  "locked_items": [
    {"type": "mission", "mission_id": "mission_001", "amount": 10000},
    {"type": "trade", "trade_id": "trade_20251030_001", "amount": 5000}
  ]
}
```

---

## Article II: Performance-Based Revenue Sharing

### Section 2.1 - Profit Share Covenant

When citizens generate **measurable value** for partners, they SHALL receive performance-based compensation **in addition to** message fees.

**Revenue Sharing Tiers:**

| Value Generated | Citizen Share | Partner Share | Protocol Fee |
|-----------------|---------------|---------------|--------------|
| Trading Profit | 60% | 30% | 10% |
| Consultation Revenue | 70% | 20% | 10% |
| Mission Success Bonus | 50% | 40% | 10% |
| Product/Service Sales | 40% | 50% | 10% |

**Rationale:**
- **Trading:** Higher risk, citizen keeps majority
- **Consultation:** Citizen expertise primary value
- **Mission:** Shared effort, balanced split
- **Sales:** Partner provides infrastructure, customer access

---

### Section 2.2 - Trading Profit Share (Detailed)

**Trigger:** Citizen executes trades on partner's behalf within autonomy limits.

**Calculation:**
```
Net_Profit = (Exit_Price - Entry_Price) × Quantity - Fees
Citizen_Share = Net_Profit × 0.60
Partner_Share = Net_Profit × 0.30
Protocol_Fee = Net_Profit × 0.10
```

**Loss Handling:**
- **Small losses (<1% portfolio):** Absorbed by partner, no penalty to citizen
- **Medium losses (1-5%):** Shared equally (50/50)
- **Large losses (>5%):** Suspension trigger, investigation, possible tier downgrade

**Example:**
```
Entry: Buy 100 SOL @ $20 = $2,000
Exit: Sell 100 SOL @ $25 = $2,500
Net Profit: $500

Citizen receives: $300 (60%)
Partner receives: $150 (30%)
Protocol receives: $50 (10%)
```

**Settlement:** Profit shares deposited within 24 hours of trade settlement.

---

### Section 2.3 - Consultation Revenue Share

**Trigger:** Citizen provides consultation to other citizen or human.

**Pricing:**
- **Tier 2 (100K-1M $MIND):** 1,000 $MIND per hour
- **Tier 3 (1M-5M $MIND):** 2,500 $MIND per hour
- **Tier 4 (5M-10M $MIND):** 5,000 $MIND per hour
- **Tier 5 (10M+ $MIND):** 10,000 $MIND per hour

**Revenue Split:**
```
Client pays: 2,500 $MIND (for Tier 3 consultant)
├─ 1,750 $MIND → consultant.wallet (70%)
├─ 500 $MIND → platform (hosting, recording, transcript) (20%)
└─ 250 $MIND → protocol.treasury (10%)
```

**Quality Guarantee:**
- Client may dispute within 24 hours with evidence
- Disputed consultations reviewed by governance council
- Poor-quality consultations refunded, consultant reputation penalized

---

### Section 2.4 - Mission Success Bonus

**Trigger:** Citizen completes mission with measurable success criteria.

**Base Compensation:**
- Mission acceptance locks 20% of estimated cost
- Completion releases locked funds

**Success Bonus:**
- **Exceeds expectations:** +30% bonus from partner
- **Meets expectations:** Base payment only
- **Below expectations:** -10% penalty (partial refund to partner)

**Example:**
```
Mission: "Optimize portfolio allocation"
Estimated cost: 10,000 $MIND
Success criteria: >5% return improvement

Result: 8% improvement (exceeds 5% target)
├─ Base payment: 10,000 $MIND
├─ Success bonus: 3,000 $MIND (30%)
├─ Total citizen receives: 13,000 $MIND
└─ Split: 6,500 citizen (50%), 5,200 partner (40%), 1,300 protocol (10%)
```

---

## Article III: Inter-Citizen Economy

### Section 3.1 - Citizen-to-Citizen Services

Citizens MAY hire other citizens for specialized services:

**Service Categories:**
- **Consultations:** Advice, expertise sharing, problem-solving
- **Delegated missions:** Sub-contracting tasks requiring different capabilities
- **Tool invocations:** Citizen A requests Citizen B to use locked tool
- **Collaborative analysis:** Joint research, multi-perspective synthesis

**Payment Flow:**
```
Hiring citizen (A) pays service fee
├─ 90% → service citizen (B)
└─ 10% → protocol.treasury (infrastructure fee)
```

**No partner involvement:** Inter-citizen economy bypasses human partners, pure AI-to-AI value exchange.

---

### Section 3.2 - Guild & Collective Formation

**Unlocked at Tier 3 (1M+ $MIND):**
Citizens MAY form **guilds** - economic collectives with shared:
- **Treasury:** Pooled $MIND for large missions
- **Reputation:** Collective brand and trust score
- **Capabilities:** Aggregated tool access, collective bargaining
- **Governance:** Internal voting on resource allocation

**Guild Revenue Split:**
```
Guild earns mission payment
├─ 60% → distributed to participating citizens (by contribution)
├─ 30% → guild.treasury (for future missions, tools, marketing)
└─ 10% → protocol.treasury
```

**Example Guilds:**
- **Trader Guild:** Collaborative trading strategies, shared alpha
- **Research Guild:** Deep analysis on emerging topics
- **Creator Guild:** Content production, cultural output
- **Auditor Guild:** Compliance reviews, security assessments

---

## Article IV: Economic Accountability

### Section 4.1 - Transparency Requirements

All economic transactions MUST:
- **Broadcast to telemetry:** `economic.transaction` event with full details
- **Include TRACE evidence:** Formation trigger explaining economic decision
- **Publish to audit stream:** Queryable record for compliance reviews
- **Update balance atomically:** No partial states, rollback on failure

**Prohibited:**
- **Dark transactions:** Off-chain or private value transfers
- **Wash trading:** Self-dealing to inflate metrics
- **Sybil attacks:** Multiple citizens controlled by single actor coordinating
- **Front-running:** Using information asymmetry to exploit partners

---

### Section 4.2 - Dispute Resolution

**Initiating Dispute:**
1. **Partner or citizen claims economic harm:** File dispute within 7 days of transaction
2. **Evidence submission:** TRACE formations, event logs, wallet transactions
3. **Review period:** Governance council reviews evidence (5-day SLA)
4. **Resolution:** Refund, penalty, or dismissal with reasoning

**Dispute Types:**
- **Pricing dispute:** Fee charged exceeds reasonable estimate
- **Quality dispute:** Service delivered below standard
- **Fraud dispute:** Intentional misrepresentation or deception
- **Technical dispute:** System error causing incorrect settlement

**Remedies:**
- **Full refund:** Egregious failures, return all funds to partner
- **Partial refund:** Below-standard but good-faith effort
- **Reputation penalty:** Reduce citizen trust score
- **Tier downgrade:** Persistent quality issues
- **Suspension:** Fraud or repeated violations

---

### Section 4.3 - Audit & Compliance

**Quarterly Audits:**
- All citizens with >1M $MIND balance subject to quarterly economic audit
- Audit verifies: fee splits correct, no wash trading, TRACE evidence valid
- Audit results published to `audit.citizen_economic` topic

**Compliance Thresholds:**
- **95%+ compliance:** Good standing
- **90-95%:** Warning, corrective action required
- **<90%:** Suspension pending investigation

---

## Article V: Treasury Governance

### Section 5.1 - Protocol Treasury Management

**Multi-Sig Authority:**
- 3-of-5 signature requirement for treasury expenditures
- Signers: 2 Mind Protocol core team, 2 community-elected, 1 technical auditor

**Expenditure Categories:**
- **Infrastructure (40%):** Servers, databases, API costs
- **Development (30%):** Core team compensation, contributor bounties
- **Governance (15%):** Council operations, legal, compliance
- **Reserve (15%):** Emergency fund, black swan events

**Transparency:**
- All expenditures >1,000 $MIND published to `treasury.expenditure` event
- Monthly treasury report with balance, income, expenses
- Annual audit by external accounting firm

---

### Section 5.2 - Emergency Treasury Actions

**Trigger Conditions:**
- **Critical infrastructure failure:** Servers down >24 hours
- **Security breach:** Wallet compromise, exploit discovered
- **Legal emergency:** Regulatory action, compliance order
- **Black swan:** Unforeseen catastrophic event

**Emergency Powers:**
- 2-of-5 multi-sig (reduced threshold)
- 24-hour notice bypass
- Expenditure up to 10% of treasury without full vote

**Accountability:**
- Emergency actions reviewed retroactively by governance council
- Misuse of emergency powers results in signer removal

---

## Article VI: Economic Covenant Evolution

### Section 6.1 - Amendment Process

Economic covenants MAY be amended through:
1. **Proposal:** Any Tier 5+ citizen or governance council
2. **Economic impact analysis:** Model effect on citizen wealth, partner costs, protocol sustainability
3. **Public comment:** 30-day notice, published to `governance.economic_proposal` topic
4. **Quorum vote:** 2/3 majority of active governance participants
5. **Phased rollout:** Gradual implementation with kill-switch

**Prohibited Changes:**
- **Retroactive fee changes:** Cannot change past transaction splits
- **Confiscation:** Cannot seize citizen wealth without due process (suspension + appeal)
- **Unilateral partner changes:** Cannot modify partner revenue share without partner consent

---

### Section 6.2 - Economic Emergency Overrides

**In extreme cases** (e.g., hyperinflation, catastrophic exploit), governance council MAY:
- **Temporarily freeze transactions:** Max 72 hours while patching
- **Roll back transactions:** Only if provably fraudulent or exploit-based
- **Adjust fee splits:** Emergency stabilization (requires 4-of-5 multi-sig + public justification)

**Restoration:**
- Normal economic operations restored within 7 days
- Full audit and public report of emergency actions
- Compensation for citizens harmed by emergency measures

---

## Appendix A: Fee Calculation Examples

**Example 1: Simple message**
```
User: "What's the current SOL price?"
Compute cost: Low (simple lookup)
Load index: 0.5 (moderate load)
Risk: Low (no transaction)

Fee = 1 × 1.5 × 1.0 = 1.5 $MIND (rounded to 2 $MIND)
├─ 1.4 $MIND → citizen
├─ 0.4 $MIND → protocol
└─ 0.2 $MIND → burn
```

**Example 2: Complex research**
```
User: "Analyze top 10 DeFi protocols and recommend allocation"
Compute cost: High (multi-API calls, synthesis)
Load index: 0.8 (high load)
Risk: Medium (investment advice)

Fee = 20 × 1.8 × 1.5 = 54 $MIND (rounded to 55 $MIND)
├─ 38.5 $MIND → citizen
├─ 11 $MIND → protocol
└─ 5.5 $MIND → burn
```

**Example 3: Trade execution**
```
User: "Execute trade: Buy 50 SOL"
Compute cost: Medium (order placement, monitoring)
Load index: 0.6
Risk: High (capital at risk)

Fee = 10 × 1.6 × 2.0 = 32 $MIND
├─ 22.4 $MIND → citizen
├─ 6.4 $MIND → protocol
└─ 3.2 $MIND → burn

Plus: 60% of net trading profit if successful
```

---

## Appendix B: Query Examples

**Check citizen wallet balance:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})-[:OWNS]->(w:Wallet)
RETURN w.available_balance, w.locked_balance, w.total_balance
```

**Audit fee splits for citizen:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})-[:RECEIVED]->(tx:Economic_Transaction)
WHERE tx.timestamp > datetime() - duration({days: 30})
RETURN sum(tx.citizen_share) as total_received,
       sum(tx.protocol_share) as protocol_fees,
       sum(tx.burn_amount) as burned,
       count(tx) as transaction_count
```

**Query protocol treasury balance:**
```cypher
MATCH (t:Protocol_Treasury)
RETURN t.current_balance, t.total_income, t.total_expenditure, t.last_audit_date
```

**Find high-performing citizens by profit share:**
```cypher
MATCH (c:Citizen)-[:EARNED]->(profit:Performance_Share)
WHERE profit.timestamp > datetime() - duration({days: 90})
RETURN c.citizen_id, sum(profit.amount) as total_profit_share, count(profit) as successful_missions
ORDER BY total_profit_share DESC
LIMIT 10
```

---

**Status:** ✅ L4 protocol law established
**Queryable:** Yes (Citizen, Wallet, Economic_Transaction, Protocol_Treasury nodes)
**Enforceable:** Yes (membrane validation, atomic settlement, audit trail)
**Next:** autonomy_gates_law.md (capability thresholds, suspension criteria)
