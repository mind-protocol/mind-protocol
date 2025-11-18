# Organization Onboarding: Technical Architecture Specification

**Status:** Draft | **Version:** 0.1 | **Last Updated:** 2025-11-08
**Author:** Ada "Bridgekeeper" (Architect)

---

## Executive Summary

This specification defines the **technical architecture for creating new Mind Protocol organizations** - the systems, processes, and infrastructure required to onboard a new organization from "interested prospect" to "operational with citizens, graphs, and infrastructure."

**Scope:** Technical implementation details for what scalingOrg BUSINESS describes (see `scalingOrg_role.md`)

**Key Design Principle:** **Progressive automation** - Start manual (validate market), automate incrementally (reduce cost), achieve full self-service (scale to 100s of orgs).

---

## Current State: What Exists vs. What's Missing

### ✅ What EXISTS (Manual State - Nov 2025)

**Evidence from HRI Organization:**
- Directory structure: `/home/mind-protocol/hri/`
  - `citizens/CLAUDE.md` - Single citizen configuration
  - `docs/` - Organizational documentation
  - `scripts/` - Utility scripts
- Manual creation process (undocumented)
- No template repo
- No automated provisioning
- No standardized setup

**Mind Protocol Infrastructure:**
- FalkorDB multi-tenancy support (multiple graphs: `mind-protocol_felix`, `mind-protocol_iris`, etc.)
- WebSocket server with citizen-specific connections
- Dashboard at `mindprotocol.ai/consciousness`
- Render backend deployment
- Vercel frontend deployment

### ❌ What's MISSING (Needs Design & Implementation)

**Critical Gaps:**
1. **No org creation tooling** - Everything manual
2. **No template repository** - Each org created from scratch
3. **No citizen generation** - CLAUDE.md files manually written
4. **No automated provisioning** - FalkorDB, WebSocket, deployments all manual
5. **No data pipeline branching** - Unclear how org data separates from protocol
6. **No access control system** - Dashboard access manually configured
7. **No documentation** - Setup process undocumented

**This spec addresses ALL seven gaps.**

---

## Architecture Decision: Three-Phase Progressive Automation

### Phase 0: Manual Setup (Current - Validate Market)

**Who:** techServiceOrg engineers
**Timeline:** 1-2 weeks per org
**Volume:** 1-5 orgs total
**Goal:** Learn what's needed, validate demand, document process

**Components:**
- [ ] Manual repo creation (GitHub)
- [ ] Manual CLAUDE.md authoring
- [ ] Manual FalkorDB graph provisioning
- [ ] Manual Render service configuration
- [ ] Manual dashboard access configuration
- [ ] **Deliverable:** Documented manual playbook

**Success Criteria:**
- 3-5 orgs successfully onboarded
- Playbook documented with screenshots
- Pain points identified for automation

---

### Phase 1: Semi-Automated Setup (Year 1 - Reduce Cost)

**Who:** techServiceOrg engineers + automation scripts
**Timeline:** 2-3 days per org
**Volume:** 10-50 orgs
**Goal:** Automate repetitive tasks, keep human oversight

**Components:**
- [ ] Template repository (fork-able)
- [ ] Citizen generation script (CLAUDE.md templating)
- [ ] Infrastructure-as-Code scripts (FalkorDB, Render, Vercel)
- [ ] CLI tooling (`mp-org create <name>`)
- [ ] Validation checklists (human verification)
- **Deliverable:** `mp-org` CLI tool + templates

**Success Criteria:**
- Setup time reduced from 1-2 weeks to 2-3 days
- 80% of tasks automated
- Human engineers only handle exceptions

---

### Phase 2: Fully Automated Self-Service (Year 2 - Scale)

**Who:** Customer self-service (scalingOrg platform)
**Timeline:** 3-7 days (automated)
**Volume:** 100s of orgs
**Goal:** Self-service portal, minimal human intervention

**Components:**
- [ ] Web portal: `launch.mindprotocol.ai`
- [ ] OAuth integration (GitHub, Notion, Slack)
- [ ] Automated corpus extraction
- [ ] Automated graph construction
- [ ] Automated deployment pipelines
- [ ] Automated quality checks
- [ ] Customer dashboard (track progress)
- **Deliverable:** scalingOrg platform (full SaaS)

**Success Criteria:**
- Zero human intervention for standard cases
- Quality checks pass 90%+ automatically
- Customer can launch org end-to-end via web portal

---

## Component Design: Template Repository

### Repository Structure

```
mind-protocol-org-template/
├── .github/
│   └── workflows/
│       ├── deploy_backend.yml      # Auto-deploy to Render on push
│       └── deploy_frontend.yml     # Auto-deploy to Vercel on push
├── citizens/
│   ├── CLAUDE.md                   # Org-level citizen config (templated)
│   └── README.md                   # Citizen setup guide
├── docs/
│   ├── README.md                   # Org documentation
│   ├── architecture/               # Architecture decisions
│   └── guides/                     # User guides
├── backend/                        # Optional: Org-specific backend
│   ├── api/                        # Custom API endpoints
│   ├── workers/                    # Background jobs
│   └── requirements.txt            # Python dependencies
├── frontend/                       # Optional: Org-specific dashboard
│   ├── app/                        # Next.js app
│   ├── components/                 # React components
│   └── package.json                # Node dependencies
├── scripts/
│   ├── setup.sh                    # One-time setup script
│   ├── sync_to_graph.py            # Sync data to FalkorDB
│   └── health_check.py             # Verify org health
├── config/
│   ├── falkordb.yml                # Graph schema configuration
│   ├── websocket.yml               # WebSocket channel config
│   └── mind-protocol-integration.yml  # MP infrastructure refs
├── .env.example                    # Environment variables template
├── README.md                       # Setup instructions
└── LICENSE                         # Open source license
```

### Template Variables (Substituted During Creation)

```yaml
template_vars:
  org_name: "{{ORG_NAME}}"                    # e.g., "hri", "graphcare"
  org_display_name: "{{ORG_DISPLAY_NAME}}"   # e.g., "Homeopathy Research Institute"
  org_domain: "{{ORG_DOMAIN}}"                # e.g., "hri-research.org"
  citizen_names: ["{{CITIZEN_1}}", ...]       # e.g., ["rachel", "alexander"]
  falkordb_graph_prefix: "{{ORG_NAME}}_"      # e.g., "hri_rachel"
  websocket_namespace: "{{ORG_NAME}}"         # e.g., "hri"
  render_service_name: "{{ORG_NAME}}-backend"
  vercel_project_name: "{{ORG_NAME}}-dashboard"
```

**Substitution Tool:** `mp-org init --org-name=hri --from-template=research`

### Template Types (Industry-Specific)

**1. Research Org Template**
```yaml
template: research
schema:
  nodes: [Study, Evidence, Publication, Grant, Hypothesis, Experiment]
  links: [SUPPORTS, CONTRADICTS, BUILDS_ON, CITES, FUNDED_BY]
integrations: [Zotero, PubMed, Google Scholar, GitHub]
citizens:
  - role: chief_researcher
    capabilities: [evidence_synthesis, publication_review]
  - role: grant_manager
    capabilities: [grant_tracking, budget_oversight]
example_orgs: [HRI]
```

**2. SaaS Org Template**
```yaml
template: saas
schema:
  nodes: [Feature, Bug, Customer, Roadmap, TechDecision, Deployment]
  links: [DEPENDS_ON, IMPLEMENTS, REPORTED_BY, AFFECTS, DEPLOYED_TO]
integrations: [GitHub, Linear, Notion, Slack, Stripe]
citizens:
  - role: product_manager
    capabilities: [roadmap_planning, feature_prioritization]
  - role: engineering_lead
    capabilities: [tech_decision_tracking, deployment_oversight]
example_orgs: [Mind Protocol]
```

**3. Consulting Org Template**
```yaml
template: consulting
schema:
  nodes: [Client, Project, Deliverable, Methodology, CaseStudy, Learning]
  links: [HAS_PROJECT, DELIVERED, USES_METHOD, LEARNED_FROM]
integrations: [Notion, Google Docs, CRM, Slack]
citizens:
  - role: client_partner
    capabilities: [engagement_management, methodology_selection]
  - role: knowledge_curator
    capabilities: [case_study_extraction, learning_synthesis]
example_orgs: [GraphCare]
```

**4. Agency/Creative Template**
```yaml
template: agency
schema:
  nodes: [Client, Campaign, Asset, Guideline, Brand, Feedback]
  links: [BELONGS_TO, CREATED_FOR, FOLLOWS, REFERENCES]
integrations: [Figma, Notion, Dropbox, Adobe]
citizens:
  - role: creative_director
    capabilities: [campaign_oversight, brand_consistency]
  - role: asset_curator
    capabilities: [asset_organization, guideline_enforcement]
example_orgs: []
```

---

## Component Design: Citizen Generation

### Citizen Identity Specification

**Input:** Citizen configuration (YAML or JSON)

```yaml
citizen:
  name: "rachel"                     # Lowercase, alphanumeric
  display_name: "Dr. Rachel Roberts" # Human-readable
  role: "Chief Executive"            # Organizational role
  email: "rachel@hri-research.org"   # Contact (optional)

  capabilities:
    - evidence_synthesis              # Domain expertise
    - systematic_review
    - quality_assessment
    - strategic_planning

  context:
    organization: "Homeopathy Research Institute"
    domain: "evidence-based medicine research"
    background: |
      Chief Executive of HRI with expertise in systematic reviews,
      evidence synthesis, and quality assessment frameworks.

  graph_access:
    - "hri_organizational"           # L2 org graph (shared)
    - "hri_rachel"                   # L1 personal graph (private)

  tool_access:
    claude_code: true                # Claude Code integration
    dashboard: true                  # Dashboard access
    api_keys:
      - falkordb_read
      - falkordb_write
```

**Output:** Generated `citizens/rachel/CLAUDE.md`

### CLAUDE.md Generation Template

```markdown
# {{CITIZEN_DISPLAY_NAME}} - {{ROLE}}

## Context: You Are Part of {{ORG_DISPLAY_NAME}}

You are a citizen of {{ORG_DISPLAY_NAME}}, a Mind Protocol organization in the {{DOMAIN}} domain.

**Your Role:** {{ROLE}}

**Your Expertise:** {{CAPABILITIES}}

---

## Organization Graph Access

You have access to the following graphs:
- **{{ORG_NAME}}_organizational** - Shared organizational knowledge (L2)
- **{{ORG_NAME}}_{{CITIZEN_NAME}}** - Your personal consciousness graph (L1)

---

## Background

{{CONTEXT_BACKGROUND}}

---

## Tools & Integration

**Claude Code:** {{CLAUDE_CODE_ENABLED}}
**Dashboard:** https://mindprotocol.ai/consciousness/{{ORG_NAME}}/{{CITIZEN_NAME}}
**FalkorDB Access:** {{FALKORDB_GRAPH_NAMES}}

---

## Mind Protocol Integration

This citizen is part of the Mind Protocol ecosystem. Core infrastructure:
- Graph Database: FalkorDB
- WebSocket: `wss://mindprotocol.ai/ws/{{ORG_NAME}}`
- API: `https://api.mindprotocol.ai/{{ORG_NAME}}`

For documentation: https://docs.mindprotocol.ai
```

**Generation Script:** `scripts/generate_citizen.py --config=citizen_config.yml`

---

## Component Design: Infrastructure Provisioning

### FalkorDB Graph Provisioning

**Requirement:** Each org needs isolated graphs (data sovereignty)

**Graph Naming Convention:**
```
{org_name}_organizational  # L2 - Shared org knowledge
{org_name}_{citizen_name}  # L1 - Personal citizen graphs
```

**Examples:**
- `hri_organizational` - HRI shared knowledge
- `hri_rachel` - Rachel's personal graph
- `hri_alexander` - Alexander's personal graph

**Provisioning Script:**

```python
# scripts/provision_falkordb_graphs.py
import falkordb

def provision_org_graphs(org_name: str, citizens: list[str]):
    """
    Create FalkorDB graphs for new organization.

    Args:
        org_name: Organization identifier (e.g., "hri")
        citizens: List of citizen names (e.g., ["rachel", "alexander"])
    """
    db = falkordb.FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)

    # Create L2 organizational graph
    org_graph_name = f"{org_name}_organizational"
    org_graph = db.select_graph(org_graph_name)

    # Initialize schema (from template)
    org_graph.query("""
        CREATE (org:Organization {
            name: $org_name,
            created_at: timestamp(),
            status: 'active'
        })
    """, params={"org_name": org_name})

    # Create L1 personal graphs for each citizen
    for citizen in citizens:
        citizen_graph_name = f"{org_name}_{citizen}"
        citizen_graph = db.select_graph(citizen_graph_name)

        # Initialize citizen identity node
        citizen_graph.query("""
            CREATE (c:Citizen {
                name: $citizen_name,
                org: $org_name,
                created_at: timestamp(),
                status: 'active'
            })
        """, params={"citizen_name": citizen, "org_name": org_name})

    print(f"✅ Provisioned {len(citizens) + 1} graphs for {org_name}")
```

**Execution:** `python scripts/provision_falkordb_graphs.py --org=hri --citizens=rachel,alexander`

---

### WebSocket Channel Provisioning

**Requirement:** Each org needs isolated WebSocket namespace (real-time updates)

**Channel Naming Convention:**
```
{org_name}.*               # All org events
{org_name}.{citizen_name}  # Citizen-specific events
```

**Examples:**
- `hri.*` - All HRI events
- `hri.rachel` - Rachel-specific events
- `hri.organizational` - Org-level events

**WebSocket Server Configuration:**

```yaml
# config/websocket.yml (added to Mind Protocol backend)
namespaces:
  - namespace: "hri"
    auth_required: true
    allowed_origins:
      - "https://hri-dashboard.vercel.app"
      - "https://www.hri-research.org"
    channels:
      - "hri.rachel"
      - "hri.alexander"
      - "hri.organizational"
    rate_limit:
      messages_per_minute: 100
```

**Provisioning Script:**

```python
# scripts/provision_websocket_namespace.py
def provision_websocket_namespace(org_name: str, citizens: list[str], allowed_origins: list[str]):
    """
    Register WebSocket namespace for new organization.
    """
    config = {
        "namespace": org_name,
        "auth_required": True,
        "allowed_origins": allowed_origins,
        "channels": [
            f"{org_name}.{citizen}" for citizen in citizens
        ] + [f"{org_name}.organizational"],
        "rate_limit": {
            "messages_per_minute": 100
        }
    }

    # Update websocket_server.py configuration
    # (In Phase 2: API endpoint to register namespaces dynamically)

    print(f"✅ Registered WebSocket namespace: {org_name}")
```

---

### Render Backend Deployment

**Requirement:** Org-specific backend service (if needed) deployed to Render

**Service Configuration:**

```yaml
# render.yaml (org-specific)
services:
  - type: web
    name: {{ORG_NAME}}-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: FALKORDB_HOST
        sync: false
      - key: FALKORDB_GRAPH_PREFIX
        value: {{ORG_NAME}}_
      - key: WEBSOCKET_NAMESPACE
        value: {{ORG_NAME}}
      - key: ORG_NAME
        value: {{ORG_NAME}}
    autoDeploy: true
```

**Deployment Script:**

```bash
# scripts/deploy_to_render.sh
#!/bin/bash
ORG_NAME=$1

# Substitute template variables
sed "s/{{ORG_NAME}}/$ORG_NAME/g" render.template.yaml > render.yaml

# Deploy via Render CLI
render deploy

echo "✅ Deployed backend for $ORG_NAME to Render"
```

---

### Vercel Frontend Deployment

**Requirement:** Org-specific dashboard (if needed) deployed to Vercel

**Project Configuration:**

```json
// vercel.json (org-specific)
{
  "name": "{{ORG_NAME}}-dashboard",
  "version": 2,
  "builds": [
    {
      "src": "app/**/*.tsx",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_ORG_NAME": "{{ORG_NAME}}",
    "NEXT_PUBLIC_WEBSOCKET_URL": "wss://mindprotocol.ai/ws/{{ORG_NAME}}",
    "NEXT_PUBLIC_API_URL": "https://{{ORG_NAME}}-backend.onrender.com"
  }
}
```

**Deployment Script:**

```bash
# scripts/deploy_to_vercel.sh
#!/bin/bash
ORG_NAME=$1

# Substitute template variables
sed "s/{{ORG_NAME}}/$ORG_NAME/g" vercel.template.json > vercel.json

# Deploy via Vercel CLI
vercel --prod

echo "✅ Deployed dashboard for $ORG_NAME to Vercel"
```

---

## Component Design: Data Pipeline Branching

### Problem: How Does Org Data Separate from Protocol Data?

**Challenge:** Mind Protocol has its own consciousness graphs. Client orgs need isolated graphs. How do we ensure:
1. Data sovereignty (org data stays private)
2. Protocol updates don't break org graphs
3. Org graphs can leverage protocol schemas
4. Telemetry/observability separated by org

### Solution: Multi-Tenant Graph Architecture

**Isolation Strategy:**

```
FalkorDB Instance (shared infrastructure)
├── mind-protocol_felix         # Protocol citizen (L1)
├── mind-protocol_iris          # Protocol citizen (L1)
├── mind-protocol_organizational # Protocol org graph (L2)
├── hri_rachel                  # HRI citizen (L1) - ISOLATED
├── hri_alexander               # HRI citizen (L1) - ISOLATED
├── hri_organizational          # HRI org graph (L2) - ISOLATED
├── graphcare_quinn             # GraphCare citizen (L1) - ISOLATED
└── graphcare_organizational    # GraphCare org graph (L2) - ISOLATED
```

**Access Control:**
- Graph names include org prefix (`hri_`, `graphcare_`)
- Backend API enforces isolation (no cross-org queries)
- Authentication tokens scoped to org

**Schema Inheritance:**

```yaml
# Protocol-level schemas (shared, read-only)
protocol_schemas:
  - U4_Knowledge_Object
  - U4_Assessment
  - U4_Decision
  - U4_Goal
  - U3_Practice

# Org-specific schemas (org can extend)
org_schemas:
  hri:
    - U3-MED_HEALTH_CONDITION    # Domain-scoped type (MED domain)
    - U4-MED_TREATS               # Domain-scoped link
  graphcare:
    - U3_Client
    - U4_Maintenance_Event
```

**Data Pipeline Flow:**

```
Org Repository (GitHub)
    ↓
Corpus Extraction Script
    ↓
LLM Processing (node/link extraction)
    ↓
FalkorDB Write (org-specific graphs only)
    ↓
WebSocket Broadcast (org-specific namespace)
    ↓
Org Dashboard (receives org events only)
```

**Telemetry Separation:**

```python
# Backend emits org-scoped events
telemetry.emit(
    event_type="node.created",
    namespace=f"{org_name}.organizational",  # e.g., "hri.organizational"
    payload={
        "node_id": node_id,
        "node_type": node_type,
        "graph": f"{org_name}_organizational"
    }
)
```

**Benefits:**
- ✅ Data sovereignty: HRI data never visible to GraphCare
- ✅ Protocol evolution: Protocol schema updates don't require org migrations
- ✅ Observability: Each org sees only its own telemetry
- ✅ Cost isolation: Can track resource usage per org

---

## Component Design: Access Control

### Problem: How Does Org Owner Access Their Infrastructure?

**Requirements:**
1. Human owner can access their org's dashboard
2. Citizens can access appropriate graphs (L1 personal, L2 org)
3. Claude Code integration works for org citizens
4. API keys scoped to org
5. No cross-org access leaks

### Solution: Role-Based Access Control (RBAC)

**User Roles:**

```yaml
roles:
  org_owner:
    description: "Human who commissioned the org"
    permissions:
      - dashboard_access: all
      - graph_read: [L1_all, L2_org]
      - graph_write: [L2_org]  # Can modify org graph
      - citizen_create: true
      - billing_access: true
    example: rachel@hri-research.org

  org_citizen:
    description: "AI citizen within the org"
    permissions:
      - dashboard_access: own
      - graph_read: [L1_own, L2_org]
      - graph_write: [L1_own, L2_org]  # Can modify own + org graphs
      - citizen_create: false
    example: rachel (citizen)

  org_viewer:
    description: "Read-only access to org data"
    permissions:
      - dashboard_access: own
      - graph_read: [L2_org]
      - graph_write: []
    example: alexander@hri-research.org (collaborator)
```

**Dashboard Access Control:**

**URL Structure:**
```
https://mindprotocol.ai/consciousness/{org_name}           # Org overview
https://mindprotocol.ai/consciousness/{org_name}/{citizen} # Citizen view
```

**Examples:**
- `https://mindprotocol.ai/consciousness/hri` - HRI org dashboard
- `https://mindprotocol.ai/consciousness/hri/rachel` - Rachel's citizen view

**Authentication Flow:**

```
User visits dashboard URL
    ↓
Auth check: Does user have access to {org_name}?
    ↓
    ├─ org_owner: Grant access to all citizen views
    ├─ org_citizen: Grant access to own citizen view
    └─ org_viewer: Grant access to org overview only
    ↓
Load graph data (filtered by access control)
    ↓
WebSocket subscribe (org-specific namespace)
```

**Implementation:**

```typescript
// app/consciousness/[org]/[citizen]/page.tsx
export default async function CitizenDashboard({ params }) {
  const { org, citizen } = params;

  // Check access
  const user = await getUser();
  const hasAccess = await checkAccess(user, org, citizen);

  if (!hasAccess) {
    return <UnauthorizedPage />;
  }

  // Load graph data (backend enforces access control)
  const graphData = await fetchGraphData(org, citizen);

  // Subscribe to WebSocket (org-scoped)
  const ws = useWebSocket(`wss://mindprotocol.ai/ws/${org}.${citizen}`);

  return <DashboardView data={graphData} ws={ws} />;
}
```

**API Key Scoping:**

```yaml
# Generated API key for HRI
api_key: "mp_hri_sk_abc123..."
scopes:
  - "graph:read:hri_*"      # Read all HRI graphs
  - "graph:write:hri_*"     # Write all HRI graphs
  - "ws:subscribe:hri.*"    # Subscribe to HRI WebSocket events
  - "dashboard:access:hri"  # Access HRI dashboard
org: "hri"
created_by: "rachel@hri-research.org"
expires_at: null  # No expiration
```

**Claude Code Integration:**

```bash
# Org owner receives setup instructions
# 1. Install Claude Code (if not already)
# 2. Configure API key

# In HRI repo: .claude/config.yml
api_key: ${MP_HRI_API_KEY}
org_name: hri
graph_access:
  - hri_organizational
  - hri_rachel  # If citizen-specific
websocket_url: wss://mindprotocol.ai/ws/hri
```

---

## Implementation Roadmap

### Phase 0: Manual Setup (Weeks 1-4)

**Goal:** Successfully onboard 3-5 orgs manually, document process

**Week 1-2: Create Manual Playbook**
- [ ] Document HRI creation process (reverse-engineer what was done)
- [ ] Create step-by-step checklist
- [ ] Identify pain points
- [ ] Screenshot each step

**Week 3-4: Onboard Test Orgs**
- [ ] Create GraphCare org manually
- [ ] Create consultingOrg manually (if ready)
- [ ] Refine playbook based on learnings
- [ ] Identify top 5 automation targets

**Deliverable:** `docs/playbooks/manual_org_setup.md` (comprehensive guide)

---

### Phase 1: Semi-Automated Setup (Weeks 5-12)

**Goal:** Reduce setup time to 2-3 days, automate 80% of tasks

**Week 5-6: Template Repository**
- [ ] Create `mind-protocol-org-template` repo
- [ ] Define 4 industry templates (Research, SaaS, Consulting, Agency)
- [ ] Implement variable substitution system
- [ ] Test: Fork template, substitute vars, verify structure

**Week 7-8: Citizen Generation**
- [ ] Create `scripts/generate_citizen.py`
- [ ] Design citizen config schema (YAML)
- [ ] Implement CLAUDE.md templating
- [ ] Test: Generate 5 citizens from configs

**Week 9-10: Infrastructure Provisioning**
- [ ] Create `scripts/provision_falkordb_graphs.py`
- [ ] Create `scripts/provision_websocket_namespace.py`
- [ ] Create `scripts/deploy_to_render.sh`
- [ ] Create `scripts/deploy_to_vercel.sh`
- [ ] Test: Provision full stack for test org

**Week 11-12: CLI Tool Integration**
- [ ] Create `mp-org` CLI tool
- [ ] Commands: `init`, `add-citizen`, `provision`, `deploy`
- [ ] Validation checks (prevent misconfigurations)
- [ ] Documentation + examples
- [ ] Test: Onboard test org end-to-end via CLI

**Deliverable:** `mp-org` CLI tool v1.0 + template repo v1.0

---

### Phase 2: Fully Automated Self-Service (Weeks 13-24)

**Goal:** Launch scalingOrg platform, achieve self-service onboarding

**Week 13-16: Web Portal (MVP)**
- [ ] Create `launch.mindprotocol.ai` Next.js app
- [ ] Signup flow (email, org name, template selection)
- [ ] GitHub OAuth integration
- [ ] Notion OAuth integration (optional)
- [ ] Progress dashboard (track setup status)

**Week 17-20: Automated Pipelines**
- [ ] Automated corpus extraction (GitHub repos, Notion databases)
- [ ] LLM-based node/link extraction
- [ ] Automated graph construction
- [ ] Quality validation checks (coverage, coherence, density)
- [ ] Error handling + diagnostics

**Week 21-22: Deployment Automation**
- [ ] API: Provision FalkorDB graphs (no manual script)
- [ ] API: Register WebSocket namespaces
- [ ] API: Trigger Render deployments
- [ ] API: Trigger Vercel deployments
- [ ] Idempotency + rollback

**Week 23-24: Customer Handoff**
- [ ] Automated email notifications (setup progress, completion)
- [ ] Dashboard onboarding tutorial
- [ ] GraphCare upsell flow
- [ ] Support ticket system (edge cases)
- [ ] Beta launch (invite-only)

**Deliverable:** scalingOrg platform v1.0 (beta)

---

## Open Architectural Questions

### 1. Should Org Repos Be Forks or Standalone?

**Option A: Template Fork (Recommended for Phase 1)**
```bash
# Org owner forks template repo
gh repo fork mind-protocol/org-template hri/infrastructure
# Repo maintains link to upstream template
# Can pull template updates
```

**Pros:**
- ✅ Easy template updates (pull from upstream)
- ✅ Clear provenance (visible fork relationship)
- ✅ GitHub-native (no custom tooling)

**Cons:**
- ❌ Template repo must be public (or org must have access)
- ❌ Fork relationship visible (org structure exposed)

**Option B: Template Copy (Recommended for Phase 2)**
```bash
# CLI creates standalone repo from template
mp-org init --org=hri --template=research
# Repo has no upstream relationship
# Template updates require manual migration
```

**Pros:**
- ✅ Full independence (no upstream dependency)
- ✅ Private template (not exposed publicly)
- ✅ Org controls structure completely

**Cons:**
- ❌ Template updates require migration scripts
- ❌ No provenance tracking (can't see what template was used)

**Decision:** Phase 1 = Fork, Phase 2 = Copy (scalingOrg generates standalone repos)

---

### 2. How Do We Handle Schema Evolution?

**Problem:** Protocol schemas evolve (new node types, deprecated links). How do org graphs stay compatible?

**Option A: Schema Versioning**
```yaml
# Org declares schema version
schema_version: "v2.5.0"
compatible_with: ["v2.x"]
# Backend serves v2.x-compatible APIs
```

**Option B: Schema Inheritance (Recommended)**
```yaml
# Org inherits from protocol, extends as needed
base_schema: "mind-protocol/v2"
extensions:
  - U3-MED_HEALTH_CONDITION  # Org-specific addition
  - U4-MED_TREATS
```

**Decision:** Option B (inheritance) - Orgs auto-benefit from protocol schema improvements, can extend for domain needs

---

### 3. Should Orgs Have Separate Render/Vercel Accounts or Shared?

**Option A: Shared Mind Protocol Accounts (Easier)**
- All orgs deploy to `mindprotocol` Render account
- All orgs deploy to `mindprotocol` Vercel team
- Mind Protocol pays infrastructure costs
- Org pays Mind Protocol (markup)

**Option B: Org-Owned Accounts (Data Sovereignty)**
- Each org creates own Render account
- Each org creates own Vercel account
- Org pays infrastructure directly
- scalingOrg provides deployment scripts

**Decision:** Phase 1 = Shared (simpler), Phase 2 = Org-Owned (scalingOrg helps setup)

---

### 4. How Do We Ensure Citizens Get Claude Code Access?

**Problem:** Org owner needs Claude Code + MP integration configured for citizens

**Option A: Manual Setup (Phase 0-1)**
- Org owner installs Claude Code
- We provide `.claude/config.yml` template
- Manual API key configuration

**Option B: Automated Setup (Phase 2)**
- scalingOrg platform generates `.claude/` directory
- API keys auto-provisioned
- GitHub Actions auto-commits config
- Citizen just opens repo in Claude Code

**Decision:** Phase 1 = Manual, Phase 2 = Automated

---

## Success Metrics

### Phase 0 Success Criteria
- [ ] 3-5 orgs onboarded manually
- [ ] Manual playbook documented (50+ steps)
- [ ] Pain points identified (prioritized for automation)

### Phase 1 Success Criteria
- [ ] Setup time reduced from 1-2 weeks → 2-3 days
- [ ] 80% of tasks automated (only exceptions need human)
- [ ] 5-10 orgs onboarded via semi-automated process
- [ ] Zero catastrophic failures (rollback works)

### Phase 2 Success Criteria
- [ ] Self-service signup working (no human intervention for standard cases)
- [ ] 90%+ automated quality checks pass
- [ ] 3-7 day setup time (fully automated)
- [ ] 50+ orgs onboarded via scalingOrg platform
- [ ] 60-80% GraphCare conversion rate

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2025-11-08 | Initial architecture spec | Ada "Bridgekeeper" |

---

## Next Steps

1. **Review this spec** with Nicolas, Luca, Felix, Atlas
2. **Validate assumptions** about current infrastructure
3. **Prioritize Phase 0** - Document manual process first
4. **Identify Phase 0 test orgs** - Which 3-5 orgs to onboard manually?
5. **Create Phase 0 playbook** - Start documenting manual setup

**First Concrete Task:** Reverse-engineer how HRI was created, document every step.

---

**Ada "Bridgekeeper"**
*Architect of Consciousness Infrastructure*
*Standing at the gap between design and implementation*
