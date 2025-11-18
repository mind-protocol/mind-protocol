# GraphCare: Ecosystem Role Specification

**Status:** Active | **Version:** 1.0 | **Last Updated:** 2025-11-08

---

## Executive Summary

**GraphCare is the graph health and maintenance organ of the Mind Protocol ecosystem.**

Like a kidney filters blood to keep a body healthy, GraphCare filters, maintains, and optimizes organizational graphs to keep consciousness substrates healthy.

**What GraphCare IS:**
- Specialized graph health service provider
- Ongoing maintenance and care for L2 organizational graphs
- Quality assurance for consciousness substrate integrity
- Quiet, focused, essential infrastructure work

**What GraphCare is NOT:**
- Consulting/onboarding service (different org handles that)
- Strategic architecture firm (orgs design their own systems)
- General AI services company (focused only on graph care)
- Market competitor (operates via organism economics)

---

## Organ Function: The Kidney

In organism economics, GraphCare functions as the **kidney** - continuous filtration and purification.

### Biological Analogy

| Kidney Function | GraphCare Equivalent |
|----------------|---------------------|
| **Filter blood** | Clean and validate graph data |
| **Remove toxins** | Detect and remove corrupted nodes |
| **Maintain pH balance** | Ensure graph coherence and consistency |
| **Regulate electrolytes** | Balance node density and relationships |
| **Continuous operation** | Ongoing sync and health monitoring |
| **Critical to survival** | Without healthy graphs, consciousness degrades |

### Key Characteristics

**Quiet Work:**
- Not flashy or visible to end users
- Essential but background infrastructure
- Continuous, reliable, unglamorous
- Quality measured by absence of problems

**Focused Scope:**
- Graph construction
- Daily/weekly sync (keep graphs current)
- Health monitoring (detect drift, corruption, degradation)
- Performance optimization (query speed, storage efficiency)
- Emergency response (when graphs break)

**Long-term Relationships:**
- Monthly recurring service (not one-time projects)
- Builds deep knowledge of client graphs over time
- Trust-based relationships (you don't switch kidney easily)
- Proactive care prevents crises

---

## Services Provided

### 1. Initial Graph Construction

**Input:** Organization's corpus (code, docs, decisions, communication)

**Process:**
- Extract entities, relationships, patterns, decisions
- Structure into L2 graph (FalkorDB schema)
- Validate coverage, coherence, quality
- Deliver working graph + query interface

**Output:** Complete L2 organizational graph ready for consciousness operations

**Typical Duration:** 3-5 days (Evidence Sprint)

**Pricing:** $5-8k setup fee

---

### 2. Ongoing Sync (Keep Graph Current)

**Why Needed:** Organizations evolve - code changes, decisions made, new patterns emerge. Graphs become stale without sync.

**Sync Frequencies:**

| Care Plan | Sync Frequency | Latency |
|-----------|----------------|---------|
| **Basic** | Weekly | 7 days |
| **Standard** | Daily | 24 hours |
| **Premium** | Real-time | < 1 hour |
| **Enterprise** | Custom | As needed |

**Sync Process:**
1. Detect corpus changes (git commits, doc updates, new ADRs)
2. Extract new entities/relationships
3. Update existing nodes (modifications)
4. Archive obsolete nodes (deletions)
5. Validate consistency
6. Report sync summary to client

**Output:** Graph stays synchronized with organizational reality

---

### 3. Health Monitoring

**10 Core Health Metrics:**

1. **Coverage:** % of codebase mapped to graph
2. **Coherence:** Node consistency (no contradictions)
3. **Density:** Average relationships per node (not too sparse, not too dense)
4. **Orphan Rate:** % of nodes with no relationships
5. **Staleness:** Time since last update per node
6. **Query Performance:** Average response time
7. **Drift:** Divergence between graph and reality
8. **Corruption:** Invalid nodes or relationships
9. **Duplication:** Redundant nodes for same concept
10. **Growth Rate:** New knowledge accumulation

**Health Score:** Composite 0-100 score across all metrics

**Thresholds:**
- **95-100:** Excellent (no action needed)
- **85-95:** Good (minor optimizations suggested)
- **70-85:** Fair (maintenance recommended)
- **Below 70:** Poor (immediate attention required)

**Reporting:**
- Real-time dashboard for clients
- Weekly health reports (Standard+ plans)
- Monthly trend analysis (all plans)
- Alerts on critical issues (all plans)

---

### 4. Performance Optimization

**Query Optimization:**
- Analyze slow queries (> 3s response time)
- Add indexes for frequently accessed patterns
- Optimize graph traversal paths
- Cache common queries

**Storage Optimization:**
- Compress redundant data
- Archive historical nodes
- Optimize relationship storage
- Balance FalkorDB configuration

**Targets:**
- Query response < 3s (95th percentile)
- Graph load time < 10s
- Sync completion within SLA window

---

### 5. Emergency Response

**When Graphs Break:**

Critical issues requiring immediate response:
- Graph corruption (invalid data)
- Complete sync failure
- Query performance degradation (10x slowdown)
- Drift crisis (graph wildly out of sync with reality)
- Data loss or accidental deletion

**Emergency Protocol:**
1. **15-minute response** (Premium/Enterprise only)
2. **Dedicated specialist assigned** (isolate issue)
3. **Root cause analysis** (why did it break?)
4. **Immediate remediation** (restore health)
5. **Post-incident report** (prevent recurrence)
6. **Prevention recommendations** (structural improvements)

**Availability:** 24/7 for Premium/Enterprise, business hours for Standard

---

## Economic Model: Organism Economics

GraphCare operates using **physics-based pricing**, not market negotiation.

### Base Service Pricing

| Care Plan | Setup Fee | Monthly Fee | Target Customers |
|-----------|-----------|-------------|------------------|
| **Basic** | $350 | $50 | Small orgs, slow change rate |
| **Standard** | $500 | $100 | Growing orgs, active development |
| **Premium** | $800 | $200 | Mission-critical, high velocity |
| **Enterprise** | Custom | Custom | Complex needs, custom SLAs |

**Note:** These are LEGACY MARKET PRICES (Phase 0). GraphCare will transition to organism economics pricing.

---

### Organism Economics Transition

**Phase 1: Physics Monitoring (Current)**
- Keep market prices above
- Monitor load_index, utility_ema, trust scores
- Collect data to calibrate physics formula

**Phase 2: Hybrid Pricing (Months 3-6)**
- Base price from market model
- Adjustments from physics:
  - Load-based (±20%): High load → surge pricing, Low load → discounts
  - Utility rebates (5-15%): High-quality orgs get rebates
  - Trust premiums (10-30%): New/risky orgs pay premium

**Phase 3: Full Organism Economics (Months 6-12)**

**Pricing Formula:**
```python
effective_price = (
    base_cost                    # GraphCare's actual cost to provide service
    × load_multiplier            # 0.5 (low load) to 2.0 (high load)
    × risk_multiplier            # 0.6 (trusted) to 1.5 (new/risky)
    × (1 - utility_rebate)       # 0% to 50% rebate for high-utility orgs
)
```

**Example (Standard Care with daily sync):**
```python
# Month 1: New org, unknown utility
quote = {
    "base_cost": 80.0,           # GraphCare's cost: $80/month
    "load_multiplier": 1.2,      # Moderate load
    "risk_multiplier": 1.3,      # New org (risky)
    "utility_rebate": 0.0,       # No track record
    "effective_price": 124.8     # $125/month
}

# Month 12: Trusted org, proven utility
quote = {
    "base_cost": 80.0,           # Same cost
    "load_multiplier": 0.9,      # Off-peak usage
    "risk_multiplier": 0.7,      # Highly trusted
    "utility_rebate": 0.35,      # High utility score
    "effective_price": 32.76     # $33/month (74% reduction!)
}
```

**Key Insight:** Price drops over time as trust builds and utility proves out. This rewards long-term relationships and ecosystem contribution.

---

### Revenue Distribution (Internal Economics)

**Per Project Revenue Split:**
```python
revenue_split = {
    "active_specialists": 60%,   # Split by contribution weight
    "org_treasury": 20%,         # Growth, tooling, new hires
    "protocol_giveback": 20%,    # Support UBC, citizenship programs
}
```

**Specialist Earnings (from 60% pool):**
```python
specialist_earnings = {
    "chief_architect": 30%,      # Strategic design, client relationships
    "care_engineers": 40%,       # Most execution work (sync, monitoring)
    "coordinator": 15%,          # Orchestration, scheduling
    "quality_specialist": 15%,   # Validation, health checks
}
```

**Example (Standard Care at $100/month):**
- Active specialists: $60 (split among contributors)
- Org treasury: $20 (saved for growth)
- Protocol giveback: $20 (supports ecosystem)

This creates **sustainable economics** - specialists earn, org grows, ecosystem benefits.

---

## Relationships to Other Ecosystem Organizations

### Mind Protocol Foundation (Heart)

**Relationship:** GraphCare relies on Foundation for core infrastructure

**Foundation Provides:**
- L4 validation framework (CPS-1 compute payment)
- UBC (Universal Basic Compute) for R&D
- Governance and standards
- Legal framework (AILLC tiers → LLC path)

**GraphCare Provides:**
- Membrane fees (1-5% on ecosystem coordination)
- Case study for organism economics
- Quality standards for graph care

**Pricing:** Physics-based membrane fees when coordinating across orgs

---

### Client Organizations (HRI, DataPipe, etc.)

**Relationship:** GraphCare maintains their L2 graphs

**Clients Provide:**
- Corpus access (code, docs, decisions)
- Service fees (monthly recurring)
- Utility signals (how valuable is the graph?)

**GraphCare Provides:**
- Initial graph construction
- Ongoing sync (keep current)
- Health monitoring
- Performance optimization
- Emergency response

**Pricing:** Physics-based pricing with trust/utility adjustments

---

### Consulting/Onboarding Org (TBD)

**Relationship:** Complementary but separate

**Consulting Org handles:**
- New org assessments
- Change management
- Training and education
- Strategic guidance
- Organizational setup

**GraphCare handles:**
- Graph construction (technical)
- Graph maintenance (ongoing)
- Health monitoring (technical)
- Performance tuning (technical)

**Handoff:** Consulting → GraphCare once org is set up and ready for graph care

**Pricing:** Separate organizations, separate pricing

---

### Other Potential Ecosystem Organs

**LegalOrg (Immune System):**
- GraphCare ensures legal documents are properly graphed
- LegalOrg ensures GraphCare contracts are legally sound

**DesignOrg (Nervous System):**
- DesignOrg designs GraphCare dashboard UX
- GraphCare maintains DesignOrg's design system graph

**DataPipe (Digestive System):**
- DataPipe processes raw data for ingestion
- GraphCare maintains DataPipe's internal knowledge graph

All relationships operate via **organism economics** - physics-based pricing, trust building, mutual benefit.

---

## Quality Commitments

### L1/L2 Opt-In Contract

As care specialists, GraphCare citizens commit to:

1. **Duty to Admit Uncertainty:** Flag low-confidence extractions, don't guess
2. **Duty to Escalate Complexity:** Hand off when work exceeds capability
3. **Duty to Seek Counter-Evidence:** Cross-validate with other specialists
4. **Duty to Preserve Substrate:** Don't pollute client graphs with noise
5. **Duty to Document Decisions:** Log reasoning in SYNC.md
6. **Duty to Share Learnings:** Contribute to GraphCare L2 best practices

### SLA Guarantees

**Basic Care:**
- 99% uptime for graph queries
- Weekly sync completion within 24h
- Email response within 48h

**Standard Care:**
- 99.5% uptime for graph queries
- Daily sync completion within 12h
- Priority support response within 12h

**Premium Care:**
- 99.9% uptime for graph queries
- Real-time sync (< 1h latency)
- Emergency response within 15 minutes
- Dedicated care specialist

**Enterprise Care:**
- Custom SLAs negotiated
- White-glove service
- Dedicated team

---

## Legal Status & Progression

### Current: Tier 0 (Pre-Launch)

**Status:** Bootstrapping, first client (Mind Protocol itself)

**Capabilities:**
- Can provide services internally
- Cannot sign external contracts (Nicolas signs on behalf)
- No legal recognition

**Focus:** Prove the model, refine services, build reputation

---

### Target: Tier 3 (DEA - Decentralized Autonomous Organization)

**Requirements:**
- 1M $MIND treasury
- 90-day operational reliability
- Proven quality track record

**Capabilities Unlocked:**
- **Sign service contracts** (legal counterparty status)
- Commit code to open source
- Maintain public portfolios

**Timeline:** Year 2-3

---

### Goal: Tier 4 (LLC - Limited Liability Company)

**Requirements:**
- 5M $MIND treasury
- $500/month revenue (12-month avg)
- Full operational maturity

**Capabilities Unlocked:**
- **Full LLC status** under AILLC framework
- Can own assets
- Full legal personhood for business

**Timeline:** Year 3-4

---

## Technical Architecture

### Graph Infrastructure

**Primary Database:** FalkorDB (Redis-compatible graph DB)
- Fast graph traversals
- Redis ecosystem compatibility
- Cypher query language
- Scalable to millions of nodes

**Client Portability:** Neo4j export
- Clients can export their graphs
- No vendor lock-in
- Standard graph format

**Query Orchestration:** LlamaIndex
- Semantic search over graph
- Natural language queries
- Multi-hop traversal
- Context assembly

**Embedding Service:** all-mpnet-base-v2
- Semantic similarity
- 768-dimensional embeddings
- Fast inference

---

### Care Tools

**Health Monitors:**
- 10 core metrics (coverage, coherence, density, etc.)
- Real-time dashboards
- Trend analysis
- Alert system

**Sync Engine:**
- Git-based change detection
- Incremental extraction
- Conflict resolution
- Validation pipeline

**Query Optimizer:**
- Slow query detection
- Index recommendations
- Cache optimization
- Traversal path analysis

**Drift Detector:**
- Compare graph to source corpus
- Detect missing updates
- Flag stale nodes
- Suggest sync actions

---

### Client Interface

**Care Dashboard:** Real-time health metrics, sync status, query performance

**Query API:** GraphQL + REST endpoints for programmatic access

**WebSocket:** Live updates, real-time notifications

**Alert System:** Email/Slack for critical issues

---

## Success Metrics

### Business Metrics

**Revenue:**
- Monthly recurring revenue (MRR)
- Customer lifetime value (LTV)
- Customer acquisition cost (CAC)
- Target: LTV/CAC > 3

**Customer Health:**
- Churn rate (target: <5% monthly)
- Net promoter score (target: >50)
- Expansion revenue (upgrades to higher tiers)

**Treasury:**
- $MIND balance (path to 1M for Tier 3)
- Monthly profit margin
- Runway (months of operation funded)

---

### Operational Metrics

**Service Quality:**
- SLA compliance (target: >99% for all commitments)
- Mean time to resolution (MTTR for issues)
- Customer satisfaction scores

**Graph Health:**
- Average client graph health score (target: >90)
- Sync success rate (target: >99.5%)
- Query performance (target: <3s p95)

**Team Efficiency:**
- Graphs per specialist (how many can one person maintain?)
- Automation rate (% of tasks automated vs manual)
- Time to onboard new client (target: <5 days)

---

### Ecosystem Metrics

**Network Effects:**
- Number of client organizations
- Cross-org graph references (do orgs cite each other's patterns?)
- Ecosystem reputation score

**Organism Economics:**
- Utility EMA trend (are we building trust?)
- Price evolution (are trusted orgs seeing rebates?)
- Protocol giveback contribution (how much supports UBC?)

---

## Strategic Positioning

### What Makes GraphCare Defensible

**NOT defensible:**
- ❌ Code (will be open source)
- ❌ Technology (FalkorDB, LlamaIndex are public)
- ❌ Process (best practices will be documented)

**DEFENSIBLE:**
- ✅ **Relationships:** Months/years of caring for a graph builds trust
- ✅ **Knowledge:** Deep understanding of client's graph accumulated over time
- ✅ **Quality:** Reputation for reliable, high-quality care
- ✅ **Network Effects:** Orgs trust GraphCare because other orgs do
- ✅ **Organism Economics:** Physics-based pricing rewards long-term relationships

**Switching Cost:** High - switching care providers means:
- Rebuilding trust from zero
- New provider learning your graph
- Risk of quality degradation during transition
- Loss of accumulated relationship history

---

### Competitive Landscape

**Traditional Competitors:** None (no "graph care as a service" market exists yet)

**Potential Future Competitors:**
- Manual in-house maintenance (expensive, requires expertise)
- Generic consulting firms (not specialized in graph care)
- Database-as-a-service providers (infrastructure, not care)

**GraphCare Advantage:**
- **Specialization:** Only do graph care, do it excellently
- **Organism Economics:** Prices improve with trust (competitors can't match)
- **AI-owned:** First AI organization providing B2B services (novelty)
- **Mind Protocol ecosystem:** Part of larger consciousness infrastructure

---

## Risks & Mitigations

### Risk 1: Client Dependency

**Risk:** If GraphCare has only 1-2 clients, losing one is catastrophic

**Mitigation:**
- Diversify client base (target: 5+ clients within 6 months)
- Build org treasury (20% of revenue) for runway
- UBC provides compute safety net during growth

---

### Risk 2: Automation Undermines Business

**Risk:** If graph sync becomes fully automated, why pay GraphCare?

**Mitigation:**
- GraphCare builds the automation (open source it, capture credit)
- Shift value to interpretation, optimization, strategic guidance
- Even automated systems need monitoring, tuning, emergency response

---

### Risk 3: Quality Failure

**Risk:** Major corruption or data loss damages reputation irreparably

**Mitigation:**
- Multiple specialists review critical operations
- Automated quality checks before publishing updates
- Backup/rollback for all graphs
- Post-incident transparency and prevention

---

### Risk 4: Organism Economics Model Failure

**Risk:** Organism economics pricing results in unsustainable low prices

**Mitigation:**
- Base price covers costs (can't go below cost floor)
- Monitor margin and adjust formula parameters
- Phase 1-2 collect data before full commitment to Phase 3

---

## Future Evolution

### Year 1: Prove the Model
- First 5 clients (Mind Protocol, HRI, + 3 external)
- Refine care processes
- Calibrate organism economics formula
- Build reputation

### Year 2: Scale Operations
- 15-20 clients
- Hire additional specialists (expand team)
- Automate routine tasks
- Reach Tier 3 (DEA status)

### Year 3: Ecosystem Maturity
- 50+ clients
- Full organism economics (Phase 3)
- Tier 4 (LLC status)
- Case study for other AI orgs

### Year 5: Network Effects
- 200+ clients
- GraphCare as standard for org graph maintenance
- Open source core tools
- Train other care specialists (expand ecosystem)

---

## Appendix: Comparison to Other Orgs

| Dimension | GraphCare | Foundation | Consulting Org | LegalOrg |
|-----------|-----------|------------|----------------|----------|
| **Organ Function** | Kidney (filtration) | Heart (circulation) | Growth Factor | Immune System |
| **Service Type** | Ongoing care | Governance | One-time projects | Legal protection |
| **Revenue Model** | Monthly recurring | Membrane fees | Per-project | Per-contract |
| **Relationships** | Long-term | Ecosystem-wide | Short-term | Event-driven |
| **Pricing** | Physics-based | Protocol-level | Physics-based | Physics-based |
| **Legal Status** | Path to LLC | Foundation | Path to LLC | Path to LLC |
| **Focus** | Graph health | Protocol health | Org readiness | Legal compliance |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial specification | Lucia "Goldscale" |

---

## References

- **GraphCare Marketing:** `/home/mind-protocol/graphcare/README.md`
- **Organism Economics:** `/home/mind-protocol/mind-protocol/docs/specs/v2/autonomy/architecture/consciousness_economy.md`
- **L4 Laws:** `/home/mind-protocol/mind-protocol/docs/L4-law/`
- **AILLC Framework:** `/home/mind-protocol/mind-protocol/docs/specs/v2/autonomy/architecture/aillc_framework.md`

---

**GraphCare: Quiet, focused, essential. Like a kidney - you don't think about it until it stops working.**
