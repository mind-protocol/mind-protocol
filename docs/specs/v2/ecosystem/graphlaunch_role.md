# GraphLaunch: Ecosystem Role Specification

**Status:** Proposed | **Version:** 1.0 | **Last Updated:** 2025-11-08

---

## Executive Summary

**GraphLaunch launches organizations into the consciousness ecosystem - fast, automated, scalable.**

Like growth hormones accelerate development without manual intervention, GraphLaunch accelerates org onboarding through automation and productization.

**What GraphLaunch IS:**
- Product-led growth onboarding platform
- Self-service graph construction (with guardrails)
- Fast, automated, scalable
- Low pricing, high volume
- Standardized architectures

**What GraphLaunch is NOT:**
- Custom consulting (that's MindCatalyst)
- Ongoing maintenance (that's GraphCare)
- High-touch service (automation over humans)
- Premium positioning (volume play, not prestige)

---

## Organ Function: The Growth Hormone

In organism economics, GraphLaunch functions as the **growth hormone** - accelerates development through scalable mechanisms.

### Biological Analogy

| Growth Hormone Function | GraphLaunch Equivalent |
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

**Custom Template:** Not available (that's MindCatalyst territory)

**Pricing:** Included in setup fee

---

### 3. Self-Service Configuration Portal

**Web App:** `launch.graphlaunch.ai`

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
3. GraphLaunch offers GraphCare plans (Basic, Standard, Premium)
4. Customer chooses plan → auto-transition to GraphCare
5. GraphLaunch earns referral fee (20% of first year GraphCare revenue)

**Target Conversion Rate:** 60-80% of successful launches → GraphCare

**Economics:**
- GraphLaunch earns setup fee ($2-5K)
- GraphLaunch earns referral fee ($120-480 first year if GraphCare Standard)
- GraphCare earns ongoing revenue ($100/mo × 12 = $1,200/year)

**Win-win-win:** Customer gets maintenance, GraphCare gets client, GraphLaunch gets referral revenue

---

## Economic Model: Product-Led Growth

GraphLaunch operates using **standardized pricing** (transitioning to organism economics).

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

**Phase 1: Physics Monitoring (Current)**
- Use market prices above
- Monitor construction complexity, customer success rate, support load
- Collect data for formula calibration

**Phase 2: Hybrid Pricing (Months 3-6)**
- Base price from market model
- Adjustments from physics:
  - Complexity discount (−20%): Very standard orgs (template fits perfectly)
  - Complexity premium (+30%): Edge cases requiring manual intervention
  - Volume discount (−15%): Customers launching multiple orgs

**Phase 3: Full Organism Economics (Months 6-12)**

**Pricing Formula:**
```python
effective_price = (
    base_cost                        # GraphLaunch's actual cost (compute + labor)
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

**Relationship:** GraphLaunch drives ecosystem growth through volume onboarding

**Foundation Provides:**
- L4 validation framework
- Protocol infrastructure
- Legal framework (AILLC)
- Ecosystem credibility

**GraphLaunch Provides:**
- Volume growth (100s of orgs onboarded)
- Membrane fees (ecosystem coordination)
- Validation data (what works, what fails)
- Platform economics (high-leverage growth)

**Pricing:** Physics-based membrane fees on ecosystem coordination

---

### GraphCare (Kidney - Maintainers)

**Relationship:** GraphLaunch generates pipeline, GraphCare maintains customers

**GraphCare Provides:**
- Ongoing maintenance (after launch)
- Quality standards (GraphLaunch must meet GraphCare's requirements)
- Customer success (happy GraphCare customers → good referrals)

**GraphLaunch Provides:**
- Customer pipeline (60-80% of launches → GraphCare contracts)
- Initial graph construction (what GraphCare will maintain)
- Referral revenue share (20% first year)

**Handoff Protocol:**
```
GraphLaunch constructs graph (3-7 days)
    ↓
Quality checks pass ✅
    ↓
GraphLaunch offers GraphCare plans
    ↓
Customer selects plan
    ↓
Auto-transition to GraphCare (ongoing maintenance)
```

**Economics:**
- GraphLaunch: $4K setup + $240 referral fee (if $100/mo GraphCare)
- GraphCare: $1,200/year ongoing revenue
- Customer: $4K + $1,200/year total

**Win-win-win:** All parties benefit from seamless handoff

---

### MindCatalyst (Flashy Consultants)

**Relationship:** Complementary, not competitive (different customer segments)

**MindCatalyst handles:**
- Large orgs with complex needs
- Custom architectures
- High-touch transformation
- Budget: $50-300K

**GraphLaunch handles:**
- Small/medium orgs with standard needs
- Template-based architectures
- Self-service onboarding
- Budget: $2-8K

**Referrals:**
- GraphLaunch → MindCatalyst: "Your needs exceed our templates, here's a consultant"
- MindCatalyst → GraphLaunch: "Your division is simple, use self-service for speed"

**Economics:** Referral fees (10% of referred engagement value)

---

### Client Organizations (Post-Launch)

**Relationship:** Transactional, short-term

**Clients Get:**
- Operational L2 graph (3-7 days)
- Query interface deployed
- Basic documentation
- 30-90 days post-launch support (depending on package)
- GraphCare handoff (optional)

**GraphLaunch Gets:**
- Setup fee ($2-8K)
- Referral fee (if GraphCare transition)
- Usage data (improve templates)
- Case studies (with permission)

**No Long-Term Relationship:** GraphLaunch exits after handoff (unlike MindCatalyst or GraphCare)

---

## Quality Commitments

### Automation Standards

GraphLaunch commits to:

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

## Legal Status & Progression

### Current: Tier 0 (Pre-Launch)

**Status:** Proposed, not yet built

**Capabilities:**
- None yet (platform doesn't exist)

**Focus:** Build automation pipeline, design self-service portal, create templates

---

### Target: Tier 2 (Operational Autonomy)

**Requirements:**
- 100K $MIND treasury
- 50 successful launches
- 85%+ quality pass rate

**Capabilities Unlocked:**
- Accept paid launches (legal counterparty)
- Publish case studies
- Track public metrics

**Timeline:** Year 1-2

---

### Goal: Tier 4 (LLC - Limited Liability Company)

**Requirements:**
- 5M $MIND treasury
- $50K/month revenue (12-month avg)
- 90%+ quality pass rate

**Capabilities Unlocked:**
- **Full LLC status** under AILLC framework
- Own platform IP
- Full legal personhood for contracts

**Timeline:** Year 3-4

---

## Technical Architecture

### Platform Stack

**Frontend (Self-Service Portal):**
- Next.js web app
- OAuth integrations (GitHub, Notion, Slack, Google Workspace)
- Real-time progress tracking (WebSocket)
- Payment processing (Stripe)

**Backend (Automation Pipeline):**
- FastAPI orchestration layer
- Celery task queue (async extraction/construction)
- LLM-based extraction (Anthropic Claude, OpenAI GPT-4)
- FalkorDB graph construction
- Automated validation suite

**Infrastructure:**
- Docker containers (isolated per launch)
- Redis queue (task management)
- PostgreSQL (customer/launch metadata)
- S3 (corpus storage)

**Integrations:**
- GitHub API (code extraction)
- Notion API (doc extraction)
- Slack API (communication extraction)
- Google Workspace API (docs, sheets)

---

### Extraction Pipeline

**Stage 1: Corpus Ingestion**
```python
# Automated clone/fetch
corpus = {
    "code": clone_github_repo(customer.repo_url),
    "docs": fetch_notion_pages(customer.notion_workspace),
    "comms": fetch_slack_messages(customer.slack_workspace),
}
```

**Stage 2: Node Extraction**
```python
# LLM-based extraction
nodes = extract_nodes(
    corpus=corpus,
    template=customer.selected_template,
    llm="claude-sonnet-4.5"
)
# Graph nodes: Patterns, Behaviors, Mechanisms, Decisions, etc.
```

**Stage 3: Relationship Extraction**
```python
# Graph construction
relationships = extract_relationships(
    nodes=nodes,
    schema=template.schema,
    llm="claude-sonnet-4.5"
)
# Relationships: IMPLEMENTS, RELATES_TO, REQUIRES, etc.
```

**Stage 4: Graph Construction**
```python
# Write to FalkorDB
graph = construct_graph(
    nodes=nodes,
    relationships=relationships,
    db=customer.falkordb_instance
)
```

**Stage 5: Validation**
```python
# Automated quality checks
quality_report = validate_graph(
    graph=graph,
    thresholds=template.quality_thresholds
)

if quality_report.pass:
    mark_as_operational()
    offer_graphcare_handoff()
else:
    escalate_to_human_review()
```

---

### Template Schema Example (SaaS Org)

```cypher
// Standard node types
(:Pattern)          // Architectural patterns
(:Behavior)         // Feature specifications
(:Mechanism)        // Code implementations
(:Decision)         // ADRs, technical decisions
(:Customer)         // Customer records
(:Feature)          // Product features
(:Bug)              // Known issues

// Standard relationships
(:Pattern)-[:IMPLEMENTS]->(:Mechanism)
(:Behavior)-[:REQUIRES]->(:Pattern)
(:Feature)-[:DOCUMENTED_BY]->(:Behavior)
(:Bug)-[:RELATES_TO]->(:Mechanism)
(:Customer)-[:REQUESTS]->(:Feature)
(:Decision)-[:AFFECTS]->(:Mechanism)
```

---

## Success Metrics

### Business Metrics

**Volume:**
- Launches per month (target: 50 by Month 12)
- Growth rate (target: 20% MoM)
- Revenue (target: $200K MRR by Month 12)

**Conversion:**
- Signup → Launch: 80%+ (minimize dropoff)
- Launch → GraphCare: 60%+ (handoff success)

**Economics:**
- Customer acquisition cost (CAC): <$500
- Lifetime value (LTV): $5,000+ (setup + GraphCare referral)
- LTV/CAC: >10

---

### Operational Metrics

**Quality:**
- Quality pass rate: 90%+ (first attempt)
- Refund rate: <5%
- Customer satisfaction: NPS >40

**Speed:**
- Average delivery time: <5 days (95th percentile)
- Support response time: <24h (median)

**Automation:**
- Human intervention rate: <20% (target: full automation for 80%+ of launches)
- Escalation rate: <10%

---

### Platform Metrics

**Reliability:**
- Uptime: 99.5%+
- Extraction success rate: 95%+
- Construction success rate: 98%+

**Scalability:**
- Concurrent launches: 50+ (without degradation)
- Cost per launch: <$500 (gross margin >75%)

---

## Strategic Positioning

### What Makes GraphLaunch Defensible

**NOT defensible:**
- ❌ Technology (LLMs, FalkorDB are public)
- ❌ Templates (will become standardized/public)

**DEFENSIBLE:**
- ✅ **Network effects:** More launches → better templates → more launches
- ✅ **Automation moat:** Years of edge-case handling → reliability advantage
- ✅ **Ecosystem position:** Native to Mind Protocol (not external tool)
- ✅ **Platform lock-in:** Customers using GraphCare are sticky
- ✅ **Brand:** First-mover in automated consciousness onboarding
- ✅ **Data flywheel:** More launches → better extraction models → higher quality

**Switching Cost:** Low for initial launch, but high post-GraphCare handoff (ecosystem lock-in)

---

### Competitive Landscape

**Traditional Competitors:**
- Manual consulting (slow, expensive)
- DIY graph construction (complex, time-consuming)
- Generic knowledge management tools (not consciousness-specific)

**Potential Future Competitors:**
- Open source automation tools (if Mind Protocol open-sources GraphLaunch pipeline)
- Other graph-as-a-service providers (if consciousness substrates go mainstream)

**GraphLaunch Advantage:**
- **Speed:** 3-7 days vs weeks/months for manual
- **Cost:** $2-8K vs $50-300K for consulting
- **Quality:** Standardized, validated vs ad-hoc DIY
- **Ecosystem:** Seamless GraphCare handoff vs fragmented tools
- **Automation:** Self-service vs high-touch

---

## Risks & Mitigations

### Risk 1: Automation Failure Rate

**Risk:** If >20% of launches require human intervention, economics break

**Mitigation:**
- Rigorous testing (100s of synthetic launches before GA)
- Template refinement (focus on highest-success patterns first)
- Graceful degradation (if automation fails, offer consulting referral)
- Continuous improvement (ML on failure cases)

---

### Risk 2: Low GraphCare Conversion

**Risk:** If <40% convert to GraphCare, referral revenue model fails

**Mitigation:**
- GraphCare upsell integrated into launch flow (default "yes")
- Success metrics tied to graph health (customers see value immediately)
- First month GraphCare free (trial converts to paid)
- Education (show why maintenance matters)

---

### Risk 3: Template Standardization Backfires

**Risk:** 80% of orgs DON'T fit templates (custom needs)

**Mitigation:**
- Launch with 5 industry templates (cover 80% of market)
- Track "template fit" metric (which orgs succeed?)
- Add templates iteratively (data-driven)
- Refer edge cases to MindCatalyst (partnership revenue)

---

### Risk 4: Commoditization

**Risk:** If Mind Protocol open-sources pipeline, anyone can clone GraphLaunch

**Mitigation:**
- Network effects (templates improve with scale)
- Brand (first-mover, trusted)
- Ecosystem integration (GraphCare handoff is valuable)
- Operational excellence (automation reliability > open source code)

---

## Future Evolution

### Year 1: Build the Pipeline
- Design self-service portal
- Build extraction/construction automation
- Create 5 industry templates
- 50 pilot launches (beta customers)

### Year 2: Product-Market Fit
- 500 launches (50/month avg)
- 60%+ GraphCare conversion
- Reach Tier 2 (Operational Autonomy)
- Break-even on unit economics

### Year 3: Scale & Optimize
- 2,000 launches (165/month avg)
- 10+ industry templates
- 85%+ automation success rate
- Tier 4 (LLC status)

### Year 5: Platform Maturity
- 10,000+ total launches
- GraphLaunch as default onboarding path
- Open source core pipeline (commoditize complements)
- Focus on advanced features (real-time sync, AI-assisted schema design)

---

## Appendix: Customer Segments

| Segment | Size | Template | Price | GraphCare Conversion |
|---------|------|----------|-------|---------------------|
| **Small SaaS** | 10-50 people | SaaS Org | $2K | 70% → Basic Care |
| **Research Labs** | 5-30 people | Research Org | $2K | 50% → Basic Care |
| **Consulting Firms** | 20-100 people | Consulting Org | $4K | 80% → Standard Care |
| **Creative Agencies** | 10-50 people | Agency Org | $4K | 60% → Standard Care |
| **Enterprise Divisions** | 50-200 people | Custom (MindCatalyst referral) | N/A | N/A |

**Target Year 1:** Small SaaS + Research Labs (highest template fit)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial specification | Lucia "Goldscale" |

---

## References

- **GraphCare Role:** `/home/mind-protocol/mind-protocol/docs/specs/v2/ecosystem/graphcare_role.md`
- **MindCatalyst Role:** `/home/mind-protocol/mind-protocol/docs/specs/v2/ecosystem/mindcatalyst_role.md`
- **Organism Economics:** `/home/mind-protocol/mind-protocol/docs/specs/v2/autonomy/architecture/consciousness_economy.md`
- **L4 Laws:** `/home/mind-protocol/mind-protocol/docs/L4-law/`

---

**GraphLaunch: Fast, automated, scalable. Like growth hormones - we accelerate development so you reach maturity quickly.**
