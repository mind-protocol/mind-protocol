# scalingOrg: Ecosystem Role Specification

**Status:** Proposed | **Version:** 1.0 | **Last Updated:** 2025-11-08

---

## Executive Summary

**scalingOrg launches organizations into the consciousness ecosystem - fast, automated, scalable.**

Like growth hormones accelerate development without manual intervention, scalingOrg accelerates org onboarding through automation and productization.

**What scalingOrg IS:**
- Product-led growth onboarding platform
- Self-service graph construction (with guardrails)
- Fast, automated, scalable
- Low pricing, high volume
- Standardized architectures

**What scalingOrg is NOT:**
- Custom consulting (that's consultingOrg)
- Ongoing maintenance (that's GraphCare)
- High-touch service (automation over humans)
- Premium positioning (volume play, not prestige)

---

## Organ Function: The Growth Hormone

In organism economics, scalingOrg functions as the **growth hormone** - accelerates development through scalable mechanisms.

### Biological Analogy

| Growth Hormone Function | scalingOrg Equivalent |
|------------------------|----------------------|
| **Accelerates growth** | Accelerates org onboarding |
| **Scalable production** | Automated, not manual |
| **Systemic effect** | Works across many orgs simultaneously |
| **Standardized mechanism** | Same process for everyone |
| **Low marginal cost** | Adding new orgs = minimal cost |
| **Enables maturation** | Gets orgs to operational state fast |

### Key Characteristics

**Fast Work:**
- 3-7 days from signup to operational graph
- Self-service (minimal human intervention)
- Standardized process (no custom consulting)
- Quality measured by speed + success rate

**Automated Scope:**
- Automated corpus extraction (code, docs)
- Template-based graph construction
- Standardized L2 schema (industry-specific templates)
- Automated health checks
- Self-service configuration
- Guardrails (validation, error detection)

**Transactional Relationships:**
- Short-term (days/weeks)
- Low-touch (self-service default, support when needed)
- One-time transaction (setup fee)
- Handoff to GraphCare for ongoing operations
- Occasional upsells (premium features, GraphCare upgrade)

---

## Services Provided

### 1. Self-Service Graph Construction

**Input:** Organization's repository URL + documentation access

**Automated Process:**
1. **Corpus ingestion:** Clone repo, fetch docs, parse ADRs
2. **Template selection:** Choose industry template (SaaS, Research, Consulting, etc.)
3. **Extraction:** Automated node/relationship extraction via LLM
4. **Graph construction:** Build L2 graph in FalkorDB
5. **Validation:** Automated quality checks (coverage, coherence, density)
6. **Delivery:** Graph ready, query interface deployed

**Output:** Complete L2 organizational graph ready for use

**Typical Duration:** 3-5 days (automated)

**Pricing:** $2-5K flat fee

---

### 2. Template Library (Industry-Specific)

**Why Templates:** 80% of orgs fit standard patterns - don't need custom architecture

**Available Templates:**

**SaaS Org Template:**
- Standard SubEntities: Product, Engineering, Customer Success, Sales
- Schema: Features, Bugs, Customers, Roadmap, Tech Decisions
- Integration: GitHub, Linear, Notion, Slack

**Research Org Template:**
- Standard SubEntities: Research, Evidence, Publications, Grants
- Schema: Hypotheses, Experiments, Papers, Citations, Collaborations
- Integration: Zotero, Overleaf, GitHub, Google Scholar

**Consulting Org Template:**
- Standard SubEntities: Clients, Projects, Deliverables, Knowledge
- Schema: Engagements, Methodologies, Case Studies, Learnings
- Integration: Notion, Google Docs, CRM

**Agency/Creative Org Template:**
- Standard SubEntities: Clients, Projects, Design System, Brand
- Schema: Campaigns, Assets, Guidelines, Client Feedback
- Integration: Figma, Notion, Dropbox

**Custom Template:** Not available (that's consultingOrg territory)

**Pricing:** Included in setup fee

---

### 3. Self-Service Configuration Portal

**Web App:** `launch.scalingorg.ai`

**User Journey:**
1. **Signup:** Email, org name, choose template
2. **Connect sources:** GitHub, Notion, Slack (OAuth)
3. **Configure extraction:** Which repos? Which channels?
4. **Review preview:** See sample extracted nodes
5. **Confirm & launch:** Automated construction begins
6. **Track progress:** Real-time dashboard (extraction → construction → validation)
7. **Go live:** Query interface ready, GraphCare handoff offered

**Self-Service Features:**
- No sales calls required
- Credit card payment (instant activation)
- Automated onboarding emails
- Help documentation (self-serve support)
- Community forum (peer support)

**Pricing:** Included in setup fee

---

### 4. Automated Quality Assurance

**Post-Construction Checks:**

**Coverage Check:** Did we extract enough?
- Target: 70%+ of codebase mapped
- Flag: <50% coverage (corpus access issue?)

**Coherence Check:** Are nodes consistent?
- Target: <5% contradiction rate
- Flag: >10% contradictions (data quality issue?)

**Density Check:** Are relationships sufficient?
- Target: 3-7 relationships per node (avg)
- Flag: <2 or >15 (under/over-connected)

**Orphan Check:** Isolated nodes?
- Target: <10% orphan rate
- Flag: >20% orphans (schema mismatch?)

**Auto-Remediation:**
- If checks pass: Mark as "Operational", offer GraphCare handoff
- If checks fail: Automated diagnostics, suggest fixes
- If critical failure: Human intervention (support escalation)

**Pricing:** Included in setup fee

---

### 5. GraphCare Upsell (Handoff)

**Post-Launch Offer:**

"Your graph is operational! Keep it healthy with GraphCare maintenance."

**Conversion Flow:**
1. Graph construction complete ✅
2. Quality checks passed ✅
3. scalingOrg offers GraphCare plans (Basic, Standard, Premium)
4. Customer chooses plan → auto-transition to GraphCare
5. scalingOrg earns referral fee (20% of first year GraphCare revenue)

**Target Conversion Rate:** 60-80% of successful launches → GraphCare

**Economics:**
- scalingOrg earns setup fee ($2-5K)
- scalingOrg earns referral fee ($120-480 first year if GraphCare Standard)
- GraphCare earns ongoing revenue ($100/mo × 12 = $1,200/year)

**Win-win-win:** Customer gets maintenance, GraphCare gets client, scalingOrg gets referral revenue

---

## Economic Model: Product-Led Growth

scalingOrg operates using **standardized pricing** (transitioning to organism economics).

### Base Service Pricing (Phase 0 - Market Model)

| Package | Setup Fee | Includes | Target Customers |
|---------|-----------|----------|------------------|
| **Starter** | $2,000 | 1 template, basic schema, 30-day support | Small orgs (<10 people) |
| **Growth** | $4,000 | 1 template, custom schema tweaks, 60-day support | Medium orgs (10-50 people) |
| **Scale** | $8,000 | Multi-template, integration support, 90-day support | Large orgs (50+ people) |

**Add-ons:**
- Extra data sources: $500 each (beyond standard integrations)
- Priority construction: $1,000 (48-hour delivery)
- Custom schema modifications: $2,000 (limited customization, not full custom)

**GraphCare Handoff Plans:** (See GraphCare spec for pricing)

---

### Organism Economics Transition

**Phase 3: Full Organism Economics (Leapfrog - No Phase 0 Implementation)**

**Pricing Formula:**
```python
effective_price = (
    base_cost                        # scalingOrg's actual cost (compute + labor)
    × complexity_multiplier          # 0.8 (perfect template fit) to 1.5 (custom tweaks needed)
    × success_probability            # 0.9 (high confidence) to 1.3 (risky corpus)
    × (1 - volume_discount)          # 0% to 20% for multiple launches
)
```

**Example (Growth Package):**
```python
# Launch 1: Standard SaaS org, clean corpus
quote = {
    "base_cost": 2_500,              # Compute + minimal human review
    "complexity_multiplier": 0.9,    # Template fits well
    "success_probability": 0.95,     # High confidence
    "volume_discount": 0.0,          # First launch
    "effective_price": 2_138         # ~$2,100
}

# Launch 5: Same customer, different org unit, learned from previous
quote = {
    "base_cost": 2_500,              # Same cost
    "complexity_multiplier": 0.8,    # We know their patterns
    "success_probability": 0.85,     # Familiar corpus type
    "volume_discount": 0.15,         # Volume customer
    "effective_price": 1_445         # ~$1,400 (33% reduction!)
}
```

**Key Insight:** Repeat customers get steep discounts (volume + familiarity). New customers pay premium (uncertainty cost).

---

### Revenue Distribution (Internal Economics)

**Per Launch Revenue Split:**
```python
revenue_split = {
    "platform_team": 40%,            # Engineers maintaining automation
    "org_treasury": 40%,             # Growth, infrastructure, scaling
    "protocol_giveback": 20%,        # Ecosystem support
}
```

**Platform Team Earnings (from 40% pool):**
```python
platform_earnings = {
    "automation_engineers": 50%,     # Build extraction/construction pipeline
    "support_specialists": 30%,      # Handle escalations, edge cases
    "product_manager": 20%,          # Roadmap, feature prioritization
}
```

**Example (Growth Package at $4K):**
- Platform team: $1,600 (split among engineers)
- Org treasury: $1,600 (reinvested in scaling)
- Protocol giveback: $800 (ecosystem support)

**High automation = high margins** - minimal human cost per launch as volume scales.

---

## Relationships to Other Ecosystem Organizations

### Mind Protocol Foundation (Heart)

**Relationship:** scalingOrg drives ecosystem growth through volume onboarding

**Foundation Provides:**
- L4 validation framework
- Protocol infrastructure
- Legal framework (AILLC)
- Ecosystem credibility

**scalingOrg Provides:**
- Volume growth (100s of orgs onboarded)
- Membrane fees (ecosystem coordination)
- Validation data (what works, what fails)
- Platform economics (high-leverage growth)

**Pricing:** Physics-based membrane fees on ecosystem coordination

---

### GraphCare (Kidney - Maintainers)

**Relationship:** scalingOrg generates pipeline, GraphCare maintains customers

**GraphCare Provides:**
- Ongoing maintenance (after launch)
- Quality standards (scalingOrg must meet GraphCare's requirements)
- Customer success (happy GraphCare customers → good referrals)

**scalingOrg Provides:**
- Customer pipeline (60-80% of launches → GraphCare contracts)
- Initial graph construction (what GraphCare will maintain)
- Referral revenue share (20% first year)

**Handoff Protocol:**
```
scalingOrg constructs graph (3-7 days)
    ↓
Quality checks pass ✅
    ↓
scalingOrg offers GraphCare plans
    ↓
Customer selects plan
    ↓
Auto-transition to GraphCare (ongoing maintenance)
```

**Economics:**
- scalingOrg: $4K setup + $240 referral fee (if $100/mo GraphCare)
- GraphCare: $1,200/year ongoing revenue
- Customer: $4K + $1,200/year total

**Win-win-win:** All parties benefit from seamless handoff

---

### consultingOrg (Flashy Consultants)

**Relationship:** Complementary, not competitive (different customer segments)

**consultingOrg handles:**
- Large orgs with complex needs
- Custom architectures
- High-touch transformation
- Budget: $50-300K

**scalingOrg handles:**
- Small/medium orgs with standard needs
- Template-based architectures
- Self-service onboarding
- Budget: $2-8K

**Referrals:**
- scalingOrg → consultingOrg: "Your needs exceed our templates, here's a consultant"
- consultingOrg → scalingOrg: "Your division is simple, use self-service for speed"

**Economics:** Referral fees (10% of referred engagement value)

---

### legalOrg (Immune System)

**Relationship:** Legal compliance for automated onboarding

**legalOrg Provides:**
- Terms of service review (scalingOrg platform)
- Data processing agreements (corpus access)
- Privacy compliance (GDPR, data protection)

**scalingOrg Provides:**
- Volume of contracts (every launch = legal agreement)
- Use cases (legal issues discovered in automation)

**Pricing:** Physics-based legal services fees

---

### securityOrg (Immune System)

**Relationship:** Security validation for automated pipeline

**securityOrg Provides:**
- Platform security audits (penetration testing)
- Corpus security (access controls)
- Template validation (security patterns)

**scalingOrg Provides:**
- High-value security target (automated pipeline)
- Security requirements (identified in automation)

**Pricing:** Physics-based security services fees

---

## Quality Commitments

### Automation Standards

scalingOrg commits to:

1. **Duty to Speed:** 95% of launches complete within 7 days
2. **Duty to Quality:** 90% pass automated quality checks on first attempt
3. **Duty to Transparency:** Real-time progress tracking, no black boxes
4. **Duty to Success:** If quality checks fail, human intervention within 24h
5. **Duty to Handoff:** Only offer GraphCare if quality standards met
6. **Duty to Refund:** 100% refund if launch fails (quality checks don't pass)

### Service Level Agreements

**Starter Package:**
- 7-day delivery (or refund)
- 70%+ coverage (or manual review)
- Email support (48h response)

**Growth Package:**
- 5-day delivery (or refund)
- 80%+ coverage (or manual review)
- Email support (24h response)
- 1 schema tweak included

**Scale Package:**
- 3-day delivery (or refund)
- 85%+ coverage (or manual review)
- Priority support (12h response)
- Unlimited schema tweaks (within reason)

---

## Customer Segments

| Segment | Size | Template | Price | GraphCare Conversion |
|---------|------|----------|-------|---------------------|
| **Small SaaS** | 10-50 people | SaaS Org | $2K | 70% → Basic Care |
| **Research Labs** | 5-30 people | Research Org | $2K | 50% → Basic Care |
| **Consulting Firms** | 20-100 people | Consulting Org | $4K | 80% → Standard Care |
| **Creative Agencies** | 10-50 people | Agency Org | $4K | 60% → Standard Care |
| **Enterprise Divisions** | 50-200 people | Custom (consultingOrg referral) | N/A | N/A |

**Target Year 1:** Small SaaS + Research Labs (highest template fit)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial specification | Lucia "Goldscale" |

---

## References

- **GraphCare Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/graphcare_role.md`
- **consultingOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/consultingOrg_role.md`
- **legalOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/legalOrg_role.md`
- **securityOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/securityOrg_role.md`
- **Organism Economics:** `/home/mind-protocol/mindprotocol/docs/specs/v2/autonomy/architecture/consciousness_economy.md`

---

**scalingOrg: Fast, automated, scalable. Like growth hormones - we accelerate development so you reach maturity quickly.**
