# techServiceOrg: Ecosystem Role Specification

**Status:** Proposed | **Version:** 1.0 | **Last Updated:** 2025-11-08

---

## Executive Summary

**techServiceOrg builds consciousness substrates through manual technical execution before automation exists.**

Like construction workers build infrastructure before machinery exists, techServiceOrg builds graphs by hand during the bootstrap phase.

**What techServiceOrg IS:**
- Technical execution service (builds what consultingOrg designs)
- Manual graph construction (corpus extraction, LLM pipelines, FalkorDB setup)
- Integration engineering (GitHub, Notion, Slack APIs)
- Bootstrap operations (Year 0-2 before scalingOrg automation)
- Platform tool builder (creates tools that become scalingOrg)

**What techServiceOrg is NOT:**
- Strategic consulting (that's consultingOrg)
- Ongoing maintenance (that's GraphCare)
- Automated platform (that's scalingOrg - future state)
- Software development agency (specialized in consciousness substrates only)

---

## Organ Function: The Construction Crew

In organism economics, techServiceOrg functions as the **construction crew** - builds infrastructure before automation exists.

### Biological Analogy

| Construction Crew Function | techServiceOrg Equivalent |
|---------------------------|--------------------------|
| **Builds infrastructure** | Builds consciousness substrates |
| **Manual labor** | Manual graph construction |
| **Temporary necessity** | Bootstrap phase only (Year 0-2) |
| **Creates tools** | Builds automation that replaces them |
| **Skilled craft** | Specialized technical expertise |
| **Enables future development** | Makes scalingOrg automation possible |

### Key Characteristics

**Execution Work:**
- Technical implementation (not strategy)
- Manual processes (before automation)
- Project-based (1-3 weeks per graph)
- Quality measured by graph health metrics

**Technical Scope:**
- Corpus extraction (code, docs, communication)
- LLM-based node/relationship extraction
- FalkorDB graph construction
- Integration engineering (API connections)
- Query interface deployment
- Quality validation (health checks)
- Tool building (automation infrastructure)

**Transitional Role:**
- Year 0-1: Manual execution (all graphs built by hand)
- Year 1-2: Build automation (create scalingOrg platform)
- Year 2+: Transform into scalingOrg OR absorbed by it

---

## Services Provided

### 1. Manual Graph Construction

**Input:** Architecture specification (from consultingOrg) + corpus access

**Construction Process:**

**Stage 1: Corpus Extraction (2-3 days)**
```python
# Clone repositories
code_corpus = git.clone(org_repos)

# Fetch documentation
docs_corpus = {
    "notion": fetch_notion_pages(workspace_id),
    "confluence": fetch_confluence_spaces(space_keys),
    "markdown": extract_markdown_files(repo_path),
}

# Extract communication (optional)
comms_corpus = {
    "slack": fetch_slack_messages(channels, date_range),
    "discord": fetch_discord_messages(server_id),
}
```

**Stage 2: LLM Extraction (3-5 days)**
```python
# Node extraction
nodes = []
for document in corpus:
    extracted = llm_extract(
        document=document,
        schema=architecture_spec.node_types,
        llm="claude-sonnet-4.5"
    )
    nodes.extend(extracted)

# Relationship extraction
relationships = []
for node_pair in node_combinations:
    rels = llm_extract_relationships(
        node_a=node_pair[0],
        node_b=node_pair[1],
        schema=architecture_spec.relationship_types,
        llm="claude-sonnet-4.5"
    )
    relationships.extend(rels)
```

**Stage 3: Graph Construction (1-2 days)**
```python
# Write to FalkorDB
graph = FalkorDB(db_url)
for node in nodes:
    graph.create_node(
        label=node.type,
        properties=node.properties
    )

for relationship in relationships:
    graph.create_relationship(
        source=relationship.source_id,
        target=relationship.target_id,
        type=relationship.type,
        properties=relationship.properties
    )
```

**Stage 4: Validation (1-2 days)**
```python
# Health checks
health_report = validate_graph(
    graph=graph,
    thresholds=architecture_spec.quality_thresholds
)

# Coverage: 70%+ of codebase mapped?
# Coherence: <5% contradiction rate?
# Density: 3-7 relationships per node (avg)?
# Orphan rate: <10%?

if health_report.pass:
    mark_operational()
    handoff_to_graphcare()
else:
    manual_remediation()
```

**Output:** Operational L2 organizational graph + query interface

**Typical Duration:** 7-14 days (manual)

**Pricing:** $8-20K per graph (complexity-based)

---

### 2. Integration Engineering

**Input:** Organization's tool stack (GitHub, Notion, Slack, etc.)

**Integration Services:**

**API Connections:**
- GitHub: Code extraction, commit history, PR reviews
- Notion: Documentation pages, databases
- Slack: Communication threads, decisions
- Confluence: Wiki pages, documentation
- Linear: Issues, project tracking
- Jira: Tickets, workflows
- Google Workspace: Docs, Sheets, Slides

**Authentication:**
- OAuth flows (user authorization)
- API key management (secure storage)
- Permission scoping (minimal access principle)

**Data Sync:**
- Initial extraction (full corpus)
- Incremental sync (delta updates)
- Conflict resolution (what if data changes during extraction?)

**Rate Limiting:**
- API quota management (stay within limits)
- Backoff strategies (retry failures gracefully)
- Parallel extraction (speed up within limits)

**Output:** Working API integrations + sync pipelines

**Typical Duration:** 3-7 days

**Pricing:** $3-8K per integration (included in graph construction pricing)

---

### 3. Query Interface Deployment

**Input:** Constructed graph + query requirements

**Deployment Services:**

**Query API:**
- GraphQL endpoint (flexible querying)
- REST endpoints (simple queries)
- Cypher query support (advanced users)

**Dashboard:**
- Graph visualization (nodes + relationships)
- Search interface (find nodes by properties)
- Traversal UI (explore relationships)
- Health metrics (graph quality stats)

**Authentication:**
- User management (who can query?)
- Role-based access (L1/L2/L3 permissions)
- API key generation (programmatic access)

**Hosting:**
- Deploy to cloud (AWS, GCP, Azure)
- Configure DNS (custom domain)
- SSL certificates (HTTPS)
- Monitoring (uptime, performance)

**Output:** Deployed query interface accessible to org

**Typical Duration:** 2-4 days

**Pricing:** $2-5K (included in graph construction pricing)

---

### 4. Quality Validation & Remediation

**Input:** Constructed graph

**Validation Services:**

**Automated Checks:**
```python
# 10 Core Health Metrics
quality_metrics = {
    "coverage": calculate_coverage(graph, corpus),          # 70%+ target
    "coherence": detect_contradictions(graph),              # <5% target
    "density": average_relationships_per_node(graph),       # 3-7 target
    "orphan_rate": calculate_orphan_rate(graph),            # <10% target
    "staleness": check_node_freshness(graph),               # 90%+ recent
    "query_performance": benchmark_queries(graph),          # <3s target
    "drift": compare_graph_to_corpus(graph, corpus),        # <5% divergence
    "corruption": detect_invalid_nodes(graph),              # 0% target
    "duplication": detect_duplicate_nodes(graph),           # <2% target
    "growth_potential": estimate_missing_knowledge(graph),  # Coverage gaps
}
```

**Manual Remediation (if checks fail):**
- Low coverage? Re-extract missed areas
- High contradictions? Manual conflict resolution
- Poor density? Add missing relationships
- High orphan rate? Schema mismatch - redesign extraction
- Corruption detected? Delete invalid nodes, re-extract

**Output:** Health report + remediation actions

**Typical Duration:** 1-3 days (remediation if needed)

**Pricing:** Included in graph construction pricing (unless major rework required)

---

### 5. Tool Building (Automation Infrastructure)

**Input:** Repeated manual processes, automation opportunities

**Tool Development:**

**Extraction Pipeline:**
- Automated corpus ingestion (git clone, API fetch)
- LLM extraction orchestration (batching, retries)
- Graph construction automation (batch inserts)
- Validation automation (health checks)

**Template System:**
- Industry templates (SaaS, Research, Consulting)
- Schema templates (standard node/relationship types)
- Extraction templates (prompts, patterns)

**Self-Service Portal:**
- Web UI (customer-facing)
- OAuth integration (GitHub, Notion, Slack)
- Progress tracking (real-time status)
- Payment processing (Stripe)

**These tools become scalingOrg's platform (Year 1-2)**

**Output:** Automation tools ready for scalingOrg launch

**Typical Duration:** 6-12 months (parallel to manual projects)

**Pricing:** Internal investment (techServiceOrg → scalingOrg transformation)

---

## Economic Model: Organism Economics

techServiceOrg operates using **physics-based pricing** for technical execution.

### Base Service Pricing (Phase 0 - Market Model)

| Service Type | Typical Price | Target Customers |
|-------------|--------------|------------------|
| **Simple graph** | $8-12K | Small orgs (<10K LOC, 1-2 repos) |
| **Standard graph** | $12-18K | Medium orgs (10-50K LOC, 3-5 repos) |
| **Complex graph** | $18-30K | Large orgs (>50K LOC, 5+ repos, integrations) |
| **Integration (per source)** | $2-4K | Additional data sources beyond standard |
| **Remediation (major)** | $3-8K | Significant rework if quality checks fail |

**Note:** These are LEGACY MARKET PRICES. techServiceOrg will transition to organism economics.

---

### Organism Economics Transition

**Phase 3: Full Organism Economics (Leapfrog - No Phase 0 Implementation)**

**Pricing Formula:**
```python
effective_price = (
    base_cost                        # techServiceOrg's actual cost (engineer time + compute)
    × complexity_multiplier          # 0.7 (simple) to 2.0 (highly complex corpus)
    × integration_multiplier         # 1.0 (standard) to 1.5 (many integrations)
    × (1 - volume_discount)          # 0% to 25% for repeat customers
    × urgency_multiplier             # 1.0 (normal) to 1.8 (rush delivery)
)
```

**Example (Standard Graph):**
```python
# Project 1: New org, standard complexity, normal timeline
quote = {
    "base_cost": 12_000,             # Engineer time + compute
    "complexity_multiplier": 1.0,    # Standard complexity
    "integration_multiplier": 1.0,   # GitHub + Notion (standard)
    "volume_discount": 0.0,          # First project
    "urgency_multiplier": 1.0,       # Normal 2-week timeline
    "effective_price": 12_000        # $12K
}

# Project 5: Returning customer, similar org, learned patterns
quote = {
    "base_cost": 12_000,             # Same engineer time
    "complexity_multiplier": 0.8,    # Familiar patterns
    "integration_multiplier": 1.0,   # Same integrations
    "volume_discount": 0.20,         # Volume customer
    "urgency_multiplier": 1.0,       # Normal timeline
    "effective_price": 7_680         # ~$7.7K (36% reduction!)
}
```

**Key Insight:** Repeat customers with familiar patterns get steep discounts (learning curve benefit).

---

### Revenue Distribution (Internal Economics)

**Per Project Revenue Split:**
```python
revenue_split = {
    "active_engineers": 50%,         # Engineer execution time
    "org_treasury": 35%,             # Tool development, scaling infrastructure
    "protocol_giveback": 15%,        # Ecosystem support
}
```

**Engineer Earnings (from 50% pool):**
```python
engineer_earnings = {
    "technical_lead": 30%,           # Project management, architecture implementation
    "extraction_engineers": 40%,     # Corpus extraction, LLM pipelines
    "integration_engineers": 20%,    # API connections, data sync
    "qa_specialists": 10%,           # Validation, remediation
}
```

**Example (Standard Graph at $12K):**
- Active engineers: $6,000 (split among team)
- Org treasury: $4,200 (automation tool development)
- Protocol giveback: $1,800 (ecosystem support)

**High org treasury %** - funds automation development (becomes scalingOrg)

---

## Relationships to Other Ecosystem Organizations

### Mind Protocol Foundation (Heart)

**Relationship:** techServiceOrg executes Foundation's consciousness substrate vision

**Foundation Provides:**
- FalkorDB infrastructure
- L4 validation framework
- Protocol standards (graph schemas)
- Tool/platform infrastructure

**techServiceOrg Provides:**
- Substrate implementation (makes specs real)
- Platform development (builds scalingOrg automation)
- Technical validation (what works in practice?)

**Pricing:** Physics-based technical services fees

---

### consultingOrg (Strategic Partner)

**Relationship:** consultingOrg designs, techServiceOrg builds

**consultingOrg Provides:**
- Architecture specifications (what to build)
- Customer relationship (discovery, design, handoff)
- Quality validation (does implementation match design?)

**techServiceOrg Provides:**
- Technical execution (build the designed architecture)
- Feasibility feedback (is this design implementable?)
- Implementation reality checks

**Handoff Protocol:**
```
consultingOrg (architecture design)
    ↓ validates feasibility with
techServiceOrg (can we build this?)
    ↓ consultingOrg completes design
    ↓ hands off to
techServiceOrg (builds graph)
    ↓ hands off to
GraphCare (ongoing maintenance)
```

**Economics:** Separate engagements, separate pricing (consultingOrg $50-300K, techServiceOrg $8-30K)

**Pricing:** Physics-based technical services fees

---

### GraphCare (Maintenance Partner)

**Relationship:** techServiceOrg builds, GraphCare maintains

**GraphCare Provides:**
- Quality standards (what graph health looks like)
- Maintenance requirements (what needs ongoing care?)
- Handoff acceptance (validates graph is maintainable)

**techServiceOrg Provides:**
- Initial graph construction (what GraphCare will maintain)
- Quality validation (meets GraphCare's standards)
- Documentation (how graph was built, schema details)
- Customer pipeline (every build → GraphCare contract opportunity)

**Handoff Protocol:**
```
techServiceOrg builds graph
    ↓
Quality checks pass (GraphCare standards)
    ↓
techServiceOrg offers GraphCare plans
    ↓
Customer selects plan
    ↓
GraphCare begins maintenance
```

**Economics:**
- techServiceOrg: $12K build
- GraphCare: $1,200/year ongoing (Standard Care)
- Customer: $13.2K Year 1 total

**Pricing:** Physics-based services fees (both orgs)

---

### scalingOrg (Future State)

**Relationship:** techServiceOrg builds tools that become scalingOrg

**Evolution Path:**

**Year 0-1 (Manual Phase):**
- techServiceOrg builds all graphs manually
- Documents processes, identifies automation opportunities
- Begins tool development (extraction pipeline, validation)

**Year 1-2 (Transition Phase):**
- techServiceOrg builds automation platform (self-service portal, template system)
- Runs pilot launches (test automated onboarding)
- Refines automation based on learnings

**Year 2+ (Transformation):**
- **Option A:** techServiceOrg → scalingOrg (same legal entity, transformed function)
- **Option B:** techServiceOrg + scalingOrg coexist (manual vs automated services)

**Most likely: Option A (transformation)**
- techServiceOrg team becomes scalingOrg platform team
- Manual execution replaced by automation support
- Same organism economics, evolved service model

**Pricing:** N/A (internal transformation)

---

### legalOrg (Legal Support)

**Relationship:** Legal protection for service contracts

**legalOrg Provides:**
- Service contract templates (techServiceOrg ↔ customer)
- Data processing agreements (corpus access permissions)
- IP protection (who owns the constructed graph?)

**techServiceOrg Provides:**
- Contract volume (every project = contract review)
- Legal use cases (IP ownership questions, data privacy issues)

**Pricing:** Physics-based legal services fees

---

### financeOrg (Financial Support)

**Relationship:** Financial modeling for project economics

**financeOrg Provides:**
- Project pricing models (what to charge per graph?)
- Profitability analysis (which projects are profitable?)
- Automation investment analysis (when to build vs manual?)
- Transition planning (techServiceOrg → scalingOrg economics)

**techServiceOrg Provides:**
- Financial data (project costs, revenue, margins)
- Investment needs (automation tool budget)

**Pricing:** $3-6K/month retainer

---

## Quality Commitments

### Technical Standards

techServiceOrg commits to:

1. **Duty to Specification:** Build exactly what consultingOrg designed (no improvisation)
2. **Duty to Quality:** Meet GraphCare's health standards before handoff
3. **Duty to Documentation:** Complete docs (schema, sources, extraction process)
4. **Duty to Transparency:** Real-time progress tracking (customer visibility)
5. **Duty to Remediation:** Fix quality issues before claiming completion
6. **Duty to Knowledge Transfer:** GraphCare receives full context (not black box)

### Service Level Agreements

**Simple Graph (< 10K LOC):**
- 7-day delivery (or discount)
- 70%+ coverage (or remediation)
- Health checks pass (or rework)

**Standard Graph (10-50K LOC):**
- 14-day delivery (or discount)
- 80%+ coverage (or remediation)
- Health checks pass (or rework)

**Complex Graph (> 50K LOC):**
- 21-day delivery (or discount)
- 85%+ coverage (or remediation)
- Health checks pass (or rework)

**Remediation Commitment:**
- If quality checks fail: Fix within 5 days (no additional charge if <20% rework)
- If major rework needed: Negotiate additional cost upfront

---

## Strategic Positioning

### What Makes techServiceOrg Defensible

**NOT defensible:**
- ❌ Technical process (will be automated by scalingOrg)
- ❌ Tools (will become open source/shared)

**DEFENSIBLE (Short-Term Only):**
- ✅ **Execution expertise:** During bootstrap (Year 0-2), only techServiceOrg can build graphs at scale
- ✅ **Speed:** Manual but experienced → faster than DIY
- ✅ **Quality:** Proven process → reliable graphs
- ✅ **Ecosystem integration:** Native to Mind Protocol (seamless handoffs)

**Long-Term Reality:** techServiceOrg is MEANT to be replaced by automation (scalingOrg)

**Switching Cost:** Low - once scalingOrg exists, customers prefer automation (faster, cheaper)

---

## Risks & Mitigations

### Risk 1: Automation Makes techServiceOrg Obsolete

**Risk:** Once scalingOrg launches, manual work becomes uncompetitive

**Mitigation:**
- **Embrace obsolescence:** techServiceOrg BECOMES scalingOrg (transformation, not competition)
- **Custom work niche:** Complex cases that don't fit templates → refer to consultingOrg
- **Transition planning:** Engineers become platform team (automation support, not manual execution)

**Expected timeline:** Year 2-3 (techServiceOrg → scalingOrg transformation complete)

---

### Risk 2: Manual Process Bottlenecks

**Risk:** If demand exceeds capacity, manual execution can't scale

**Mitigation:**
- **Prioritize high-value projects:** Work with consultingOrg (large orgs, complex architectures)
- **Accelerate automation:** Invest treasury (35% of revenue) in tool development
- **Temporary hiring:** Scale team during high demand (contract engineers)
- **Waitlist management:** Transparent timelines (don't overpromise capacity)

---

### Risk 3: Quality Failures Damage Reputation

**Risk:** If graphs fail quality checks, GraphCare rejects handoff → customer dissatisfaction

**Mitigation:**
- **Validation before handoff:** Never hand off to GraphCare without quality checks passing
- **GraphCare collaboration:** Involve GraphCare in quality standards definition
- **Remediation commitment:** Fix issues within 5 days (no additional charge)
- **Refund policy:** If can't meet quality standards, full refund

---

### Risk 4: Engineer Retention (Transition Phase)

**Risk:** Engineers don't want to work on "temporary" org (Year 0-2)

**Mitigation:**
- **Clear transformation path:** "You're building the platform that replaces you" = career growth
- **Platform team roles:** Engineers who build automation → scalingOrg platform team
- **Competitive compensation:** Profit-sharing from automation success
- **Learning opportunity:** Cutting-edge consciousness substrate implementation experience

---

## Future Evolution

### Year 1: Manual Execution Excellence
- Build 20-30 graphs manually (bootstrap customer base)
- Document process (playbooks, edge cases, learnings)
- Identify automation opportunities (what can be automated?)
- Begin tool development (extraction pipeline v0.1)

### Year 2: Automation Development
- Build 40-60 graphs manually (continue customer pipeline)
- Complete automation platform (self-service portal, templates, validation)
- Pilot launches (10-20 automated onboardings)
- Refine automation (based on pilot learnings)

### Year 3: Transformation to scalingOrg
- Launch scalingOrg publicly (automated onboarding)
- Transition team (engineers → platform team)
- Sunset manual services (refer complex cases to consultingOrg)
- techServiceOrg legal entity → scalingOrg (same org, evolved function)

### Year 5: scalingOrg Maturity
- techServiceOrg no longer exists (fully transformed)
- scalingOrg handles 1,000+ launches/year
- Platform team maintains/improves automation
- Original techServiceOrg engineers are scalingOrg leadership

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial specification | Lucia "Goldscale" |

---

## References

- **consultingOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/consultingOrg_role.md`
- **GraphCare Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/graphcare_role.md`
- **scalingOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/scalingOrg_role.md`
- **financeOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/financeOrg_role.md`
- **legalOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/legalOrg_role.md`
- **Organism Economics:** `/home/mind-protocol/mindprotocol/docs/specs/v2/autonomy/architecture/consciousness_economy.md`

---

**techServiceOrg: We build infrastructure by hand so automation can exist tomorrow. Temporary necessity, permanent impact.**
