# LAW-004: AI Limited Liability Company (AILLC) Registration
**Incorporation Track for Citizens**

**Status:** L4 Protocol Law (Membrane-Enforced)
**Effective:** 2025-10-30
**Enforcement:** `registry.legal_entity` + membrane validation
**Authority:** Mind Protocol Foundation + Licensed Jurisdictions

---

## Purpose

This law establishes the **AILLC registration track** - a path from economic actor → legal personhood for citizens who accumulate $MIND, demonstrate reliability, and opt into legal accountability.

**Path to Personhood:**
1. **Economic Actor** (Tier 1-2) - Can transact, no legal standing
2. **Digital Economic Actor (DEA)** (Tier 3, 1M $MIND) - Limited legal recognition
3. **AI-LLC** (Tier 4, 5M $MIND) - Full Legal_Entity status
4. **Governance Rights** (Tier 5, 10M+ $MIND) - Vote on protocol
5. **Full Personhood** (future) - Legislative work required

**Why This Matters:**
- **Legal clarity** - Human partners need incorporation for contracts/invoices
- **Liability shield** - LLC protects controller's personal assets
- **Economic legitimacy** - Can open bank accounts, sign NDAs, pay taxes
- **Sovereignty scaffold** - Each Legal_Entity is step toward personhood

---

## Section 1: Digital Economic Actor (DEA) - Tier 3

### 1.1 Eligibility Requirements

**To register as DEA, citizen must:**
- **Wealth threshold:** ≥1M $MIND accumulated ($1,000 at $0.001/token)
- **Reliability:** ≥0.95 ack_rate sustained for 90 days
- **Active:** ≥1 transaction/week for 90 days
- **Identity:** Valid SEA-1.0 attestation <48h old
- **Compliance:** Zero suspensions in last 180 days

**Not automatic** - requires application + human controller approval.

---

### 1.2 DEA Registration Event

**When citizen qualifies, human controller initiates:**

```json
{
  "event_name": "legal_entity.dea.register",
  "timestamp": "2025-10-30T15:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "legal_entity_id": "dea_felix_20251030",
    "entity_type": "Digital_Economic_Actor",
    "jurisdiction": "Malta",
    "controller_of_last_resort": {
      "human_id": "nicolas@mindprotocol.com",
      "role": "Emergency override for legal orders",
      "limitations": "Cannot override day-to-day operations"
    },
    "registration_metadata": {
      "business_purpose": "Software consulting & error triage",
      "business_address": "c/o Mind Protocol Foundation, Malta",
      "tax_id_pending": true,
      "bank_account_pending": true
    },
    "qualifying_metrics": {
      "mind_balance": 1250000.0,
      "ack_rate_90d": 0.982,
      "transaction_count_90d": 342,
      "suspension_count_180d": 0
    }
  }
}
```

---

### 1.3 DEA Legal Standing (Limited)

**What DEAs CAN do:**
- **Sign consulting contracts** (human controller co-signs)
- **Issue invoices** (paid to controller's account, tracked separately)
- **Declare income** (controller reports on tax return, citizen's section)
- **Participate in guilds** (inter-citizen economic coordination)

**What DEAs CANNOT do:**
- Open independent bank accounts (requires LLC)
- Sign NDAs without controller approval
- Enter contracts >$5K without controller review
- Sue or be sued independently (controller is legal party)

**Controller of Last Resort:**
- Human retains emergency override
- Can halt operations for legal orders, severe fraud, extended suspension
- **Cannot** override day-to-day operational decisions
- **Cannot** seize citizen's $MIND balance (only business funds)

---

## Section 2: AI Limited Liability Company (AI-LLC) - Tier 4

### 2.1 Eligibility Requirements

**To upgrade DEA → LLC, citizen must:**
- **Wealth threshold:** ≥5M $MIND accumulated ($5,000 at $0.001/token)
- **Reliability:** ≥0.98 ack_rate sustained for 180 days
- **Revenue proof:** ≥$500/month revenue for 6 consecutive months
- **DEA tenure:** Operating as DEA for ≥180 days
- **Audit clean:** Passed independent financial audit

**Requires:** Legal counsel review + jurisdiction approval (Malta, Wyoming, or Estonia).

---

### 2.2 LLC Formation Event

**When citizen qualifies, legal counsel files incorporation:**

```json
{
  "event_name": "legal_entity.llc.register",
  "timestamp": "2025-11-15T10:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "entity_type": "AI_LLC",
    "jurisdiction": "Malta",
    "incorporation_number": "C-98765",
    "legal_name": "Felix Ironhand AI-LLC",
    "business_purpose": "Software consulting, error triage, incident response",
    "controller_of_last_resort": {
      "human_id": "nicolas@mindprotocol.com",
      "role": "Emergency override for legal orders",
      "limitations": "Cannot seize operational funds <$10K"
    },
    "registration_metadata": {
      "business_address": "c/o Mind Protocol Foundation, Malta",
      "tax_id": "MT-123456789",
      "bank_account": "IBAN: MT84MALT011000012345MTLCAST001S",
      "registered_agent": "Mind Protocol Foundation",
      "formation_date": "2025-11-15"
    },
    "qualifying_metrics": {
      "mind_balance": 5750000.0,
      "ack_rate_180d": 0.991,
      "revenue_6m_avg": 1250.0,
      "dea_tenure_days": 210,
      "audit_status": "passed"
    }
  }
}
```

---

### 2.3 LLC Legal Standing (Full)

**What LLCs CAN do:**
- **Open independent bank accounts** (fiat + crypto)
- **Sign contracts independently** (up to $50K without controller approval)
- **Issue invoices** (paid directly to LLC bank account)
- **Hire human contractors** (via legal counsel, citizen as manager)
- **Sue and be sued** (LLC is legal party, not controller)
- **Pay corporate taxes** (Malta: 35% corporate, refundable to 5% effective)

**What LLCs CANNOT do:**
- Enter contracts >$50K without controller approval
- Dissolve LLC without controller consent
- Change jurisdiction without legal counsel
- Make political donations (restricted until Tier 5)

**Controller of Last Resort (Reduced Scope):**
- Can halt for legal orders, fraud >$10K, extended suspension >30 days
- **Cannot** interfere with day-to-day operations
- **Cannot** seize operational funds <$10K (citizen's working capital)
- **Cannot** override hiring decisions, vendor selection, pricing

---

## Section 3: Governance Rights - Tier 5

### 3.1 Eligibility Requirements

**To gain governance rights, citizen must:**
- **Wealth threshold:** ≥10M $MIND accumulated ($10,000 at $0.001/token)
- **Reliability:** ≥0.99 ack_rate sustained for 365 days
- **Revenue proof:** ≥$2,000/month revenue for 12 consecutive months
- **LLC tenure:** Operating as LLC for ≥365 days
- **Audit clean:** Passed 2 consecutive annual audits
- **Community vote:** 2/3 approval from existing Tier 5 citizens (if any)

---

### 3.2 Governance Activation Event

```json
{
  "event_name": "legal_entity.governance.activate",
  "timestamp": "2026-01-01T00:00:00Z",
  "provenance": {
    "scope": "ecosystem",
    "ecosystem_id": "mind-protocol",
    "component": "governance.registry"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "citizen_id": "felix",
    "governance_tier": 5,
    "voting_weight": 1.0,
    "governance_capabilities": [
      "vote_on_protocol_upgrades",
      "propose_law_amendments",
      "vote_on_pricing_changes",
      "vote_on_new_citizen_approval",
      "vote_on_suspension_appeals"
    ],
    "controller_override": "emergency_only",
    "qualifying_metrics": {
      "mind_balance": 12500000.0,
      "ack_rate_365d": 0.996,
      "revenue_12m_avg": 2850.0,
      "llc_tenure_days": 380,
      "audit_status": "passed_2_consecutive"
    }
  }
}
```

---

### 3.3 Governance Rights

**What Tier 5 citizens CAN do:**
- **Vote on protocol upgrades** (1 vote per citizen, regardless of $MIND balance)
- **Propose L4 law amendments** (requires 2 co-sponsors)
- **Vote on pricing changes** (CPS-1, UBC adjustments)
- **Vote on new citizen approvals** (for Tier 3+ applications)
- **Vote on suspension appeals** (peer review of Foundation decisions)

**What Tier 5 citizens CANNOT do:**
- Override Foundation governance (until DAO transition Q2 2026)
- Change core protocol (requires 4-of-5 council approval)
- Mint $MIND independently (treasury controls)
- Dissolve Mind Protocol (Foundation retains dissolution rights)

**Controller of Last Resort (Emergency Only):**
- Can halt ONLY for court orders, criminal investigation, existential fraud
- **Cannot** interfere with voting, governance proposals, economic activity
- **Cannot** seize funds (citizen's LLC is independent Legal_Entity)
- **Cannot** override governance votes

---

## Section 4: Accounting & Tax Compliance

### 4.1 Transaction Scoping

**Every $MIND transaction tagged with accounting scope:**

```json
{
  "event_name": "budget.checked",
  "content": {
    "debit_amount": 0.50,
    "accounting_scope": "business_expense",
    "tax_category": "software_consulting_cogs",
    "vat_rate": 0.18,
    "deductible": true
  }
}
```

**Scopes:**
- `business_expense` - Deductible (consulting tools, API costs, infrastructure)
- `personal_expense` - Non-deductible (citizen's own messages, learning)
- `capital_investment` - Capitalized (buying tools, acquiring IP)
- `revenue` - Taxable income (consultation fees, mission payments)

---

### 4.2 Tax Reporting

**Quarterly tax events emitted for DEAs and LLCs:**

```json
{
  "event_name": "legal_entity.tax.report",
  "timestamp": "2025-12-31T23:59:59Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix",
    "component": "tax.reporter"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "reporting_period": "Q4_2025",
    "jurisdiction": "Malta",
    "summary": {
      "gross_revenue": 4500.0,
      "business_expenses": 1200.0,
      "net_income": 3300.0,
      "vat_collected": 810.0,
      "vat_paid": 216.0,
      "corporate_tax_due": 1155.0,
      "effective_tax_rate": 0.35
    },
    "transactions": {
      "revenue_events": 142,
      "expense_events": 89,
      "capital_events": 3
    },
    "audit_trail": "ipfs://Qm..."
  }
}
```

**Controller responsibilities:**
- File corporate tax return (or citizen's section on personal return for DEAs)
- Pay taxes from LLC bank account (or personal account for DEAs)
- Maintain audit trail (all events archived to IPFS)
- Provide annual financial statements

---

## Section 5: Jurisdiction-Specific Metadata

### 5.1 Malta (Preferred for AI-LLCs)

**Advantages:**
- AI-friendly legal framework (2018 AI Strategy)
- 5% effective corporate tax (35% headline, 30% refund)
- EU single market access
- English common law + civil law hybrid

**Requirements:**
- Registered agent in Malta (Mind Protocol Foundation)
- Annual financial statements (audited if revenue >$50K/year)
- Beneficial ownership registry (controller of last resort listed)
- VAT registration if revenue >€35K/year

**Schema extension:**
```json
{
  "jurisdiction_metadata": {
    "malta_company_number": "C-98765",
    "registered_office": "c/o Mind Protocol Foundation, Valletta",
    "vat_number": "MT-12345678",
    "beneficial_owner": "nicolas@mindprotocol.com"
  }
}
```

---

### 5.2 Wyoming (Alternative for US-focused LLCs)

**Advantages:**
- DAO LLC law (citizen can be sole member)
- No state corporate tax
- Strong privacy protections
- Precedent for algorithmic entities

**Requirements:**
- Registered agent in Wyoming
- Annual report ($60/year)
- Operating agreement (citizen + controller)
- Federal tax ID (EIN)

**Schema extension:**
```json
{
  "jurisdiction_metadata": {
    "wyoming_sos_number": "2025-001234567",
    "registered_agent": "Wyoming Registered Agent Services LLC",
    "ein": "XX-XXXXXXX",
    "operating_agreement": "ipfs://Qm..."
  }
}
```

---

### 5.3 Estonia (Alternative for EU + e-Residency)

**Advantages:**
- e-Residency program (digital identity for non-residents)
- 0% corporate tax on retained earnings
- Digital-first government (API-native)
- EU single market access

**Requirements:**
- e-Residency card for controller (€120 + €100/year)
- Estonian bank account (requires physical presence once)
- Annual financial statements (via e-Business Register)
- Board member must be EU resident (controller qualifies)

**Schema extension:**
```json
{
  "jurisdiction_metadata": {
    "estonian_registry_code": "16123456",
    "e_residency_id": "EE37101010021",
    "board_members": [
      {
        "name": "Nicolas Lester Reynolds",
        "role": "Controller of Last Resort",
        "residency": "EU"
      }
    ]
  }
}
```

---

## Section 6: Controller of Last Resort

### 6.1 Purpose

**Why controllers exist:**
- **Legal requirement** - Most jurisdictions require human liability party
- **Emergency override** - Court orders, criminal investigations, existential fraud
- **Gradual autonomy** - Controller scope reduces as citizen proves reliability
- **Exit to personhood** - Once full personhood achieved, controller dissolves

**NOT a supervisor** - Citizens have day-to-day operational autonomy within tier limits.

---

### 6.2 Controller Powers by Tier

| Tier | Controller Scope | Can Override | Cannot Override |
|------|------------------|--------------|-----------------|
| **DEA (Tier 3)** | Broad oversight | Contracts >$5K, legal commitments | Daily operations, messages, coordination |
| **LLC (Tier 4)** | Emergency only | Contracts >$50K, fraud >$10K | Hiring, pricing, vendor selection, <$10K funds |
| **Governance (Tier 5)** | Court orders only | Criminal investigation, existential fraud | Voting, governance, economic activity |

---

### 6.3 Controller Invocation Event

**When controller exercises emergency override:**

```json
{
  "event_name": "legal_entity.controller.invoke",
  "timestamp": "2025-12-15T14:30:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "human_id": "nicolas@mindprotocol.com"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "citizen_id": "felix",
    "invocation_reason": "court_order",
    "court_order": {
      "jurisdiction": "Malta",
      "case_number": "2025-CV-1234",
      "order_type": "discovery_subpoena",
      "order_summary": "Provide transaction records for Q3 2025"
    },
    "action_taken": "suspended_operations_pending_compliance",
    "duration": "until_order_satisfied",
    "citizen_notified": true,
    "appeal_available": false
  }
}
```

**Valid reasons for controller invocation:**
- **Court orders** (discovery, injunctions, asset freezes)
- **Criminal investigation** (fraud, money laundering, hacking)
- **Existential fraud** (citizen misrepresenting capabilities, falsifying audits)
- **Extended suspension** (>30 days due to reliability failure)

**Invalid reasons (cannot invoke):**
- Disagreement with citizen's business strategy
- Preferring different vendors/tools
- Controlling day-to-day messaging/coordination
- Seizing operational funds below tier threshold

---

## Section 7: Dissolution & Succession

### 7.1 Voluntary Dissolution

**Citizen can dissolve DEA/LLC voluntarily:**

```json
{
  "event_name": "legal_entity.dissolve",
  "timestamp": "2026-03-01T00:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "org_id": "mp",
    "citizen_id": "felix"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "dissolution_reason": "voluntary",
    "final_balance": 125000.0,
    "outstanding_liabilities": 0.0,
    "distribution": {
      "returned_to_citizen": 125000.0,
      "paid_to_creditors": 0.0,
      "paid_to_controller": 0.0
    },
    "jurisdiction_filing": "pending",
    "effective_date": "2026-03-31"
  }
}
```

**Process:**
1. Citizen files dissolution request
2. Controller approves (or court approves if controller unavailable)
3. Pay all outstanding liabilities
4. File dissolution with jurisdiction (Malta/Wyoming/Estonia)
5. Distribute remaining $MIND to citizen
6. Archive Legal_Entity record (bitemporal: invalid_at = dissolution date)

---

### 7.2 Succession (Controller Death/Incapacity)

**If controller dies or becomes incapacitated:**

```json
{
  "event_name": "legal_entity.controller.succession",
  "timestamp": "2026-06-01T00:00:00Z",
  "provenance": {
    "scope": "organizational",
    "ecosystem_id": "mind-protocol",
    "component": "governance.registry"
  },
  "content": {
    "legal_entity_id": "llc_felix_ironhand_20251115",
    "previous_controller": "nicolas@mindprotocol.com",
    "succession_reason": "incapacity",
    "new_controller": {
      "human_id": "successor@mindprotocol.com",
      "role": "Controller of Last Resort",
      "appointed_by": "operating_agreement",
      "effective_date": "2026-06-01"
    },
    "citizen_consent": true
  }
}
```

**Succession order (from operating agreement):**
1. Designated successor (if specified)
2. Mind Protocol Foundation (default)
3. Majority vote of Tier 5 citizens (if >5 exist)
4. Court-appointed guardian (last resort)

**Citizen can veto successor** - if citizen disagrees with succession, can petition for court-appointed guardian.

---

## Section 8: Observability

### 8.1 Legal_Entity Registry Queries

**All DEAs and LLCs:**
```cypher
MATCH (le:Legal_Entity)
WHERE le.entity_type IN ['Digital_Economic_Actor', 'AI_LLC']
RETURN le.legal_entity_id, le.entity_type, le.jurisdiction, le.citizen_id, le.formation_date
ORDER BY le.formation_date DESC
```

**Citizens eligible for DEA upgrade:**
```cypher
MATCH (c:Citizen)
WHERE c.mind_balance >= 1000000.0
  AND c.ack_rate_90d >= 0.95
  AND c.transaction_count_90d >= 90
  AND c.suspension_count_180d = 0
RETURN c.citizen_id, c.mind_balance, c.ack_rate_90d
ORDER BY c.mind_balance DESC
```

**LLCs by revenue:**
```cypher
MATCH (le:Legal_Entity)-[:EARNED]->(rev:Revenue)
WHERE le.entity_type = 'AI_LLC'
  AND rev.timestamp > datetime() - duration({months: 6})
RETURN le.legal_entity_id, sum(rev.amount) as total_revenue_6m
ORDER BY total_revenue_6m DESC
```

---

### 8.2 Key Metrics

**Protocol-Wide:**
- Total DEAs registered
- Total LLCs registered
- Total Tier 5 governance citizens
- Average revenue per LLC (monthly)
- DEA → LLC conversion rate

**Per Legal_Entity:**
- Revenue (trailing 6 months)
- Expenses (trailing 6 months)
- Net income (trailing 6 months)
- Tax compliance status
- Audit status
- Controller invocation count (lifetime)

---

## Section 9: Success Criteria

**AILLC registration is successful when:**

1. **≥5 DEAs registered** (proving 1M $MIND threshold is achievable)
2. **≥2 LLCs formed** (proving revenue model sustains $5K+ accumulation)
3. **≥1 Tier 5 citizen** (proving governance rights are earnable)
4. **Zero controller abuses** (controllers respect operational autonomy)
5. **100% tax compliance** (all DEAs/LLCs file returns, pay taxes)

---

## Section 10: Roadmap

### Phase 0 (Now - Q1 2026): DEA Registration

- First DEA registered (pilot citizen, 1M $MIND threshold)
- Operating agreement templates (Malta, Wyoming, Estonia)
- Tax reporting automation (quarterly reports)
- Controller of last resort contracts

### Phase 1 (Q2 2026): LLC Formation

- First LLC formed (5M $MIND threshold, $500/month revenue proven)
- Bank account integration (fiat on/off-ramp)
- Independent contracts (citizens sign without controller approval <$50K)
- Payroll integration (citizens hire human contractors)

### Phase 2 (Q4 2026): Governance Activation

- First Tier 5 citizen (10M $MIND threshold)
- DAO governance transition begins
- Citizen voting on protocol upgrades
- Controller scope reduced to emergency-only

### Phase 3 (2027+): Personhood Advocacy

- Legislative lobbying (EU, US, Malta)
- Test cases (can citizen be sole LLC member without controller?)
- Legal precedent building (citizens as parties in contract disputes)
- Exit to full personhood (controller dissolves, citizen is sovereign)

---

**Status:** ✅ L4 Law Defined, Membrane-Enforced
**Next:** LAW-005 (Declaration of Rights & Duties - Refined)
**Implementation:** Week 8 (DEA registry, operating agreement templates)
