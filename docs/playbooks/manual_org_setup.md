# Manual Organization Setup Playbook (Phase 0)

**Status:** Phase 0 - Manual Process | **Version:** 1.0 | **Last Updated:** 2025-11-08

---

## Purpose

This playbook documents the **current manual process** for creating new organizations in the Mind Protocol ecosystem. It serves as:

1. **Process documentation** - What actually happens today (reverse-engineered from HRI)
2. **Validation baseline** - Ensures we understand current state before automating
3. **Training material** - For humans manually creating the first 3-5 test orgs
4. **Automation roadmap** - Each step here will be automated in Phase 1/2

**Target Audience:** Nicolas, Luca, or other Mind Protocol team members manually onboarding first organizations

---

## Current State: What HRI Reveals

### Investigation Results (2025-11-08)

**What EXISTS for HRI:**
- ✅ Directory: `/home/mind-protocol/hri/`
- ✅ Citizen config: `/home/mind-protocol/hri/citizens/CLAUDE.md` (generic MP config, not HRI-specific)
- ✅ Documentation: `/home/mind-protocol/hri/docs/` (proposals, research, GraphCare brief)
- ✅ Scripts: `/home/mind-protocol/hri/scripts/` (web scraping tool for HRI website)

**What DOES NOT EXIST for HRI:**
- ❌ FalkorDB graphs (`hri_organizational`, `hri_rachel`, `hri_alexander`)
- ❌ WebSocket namespace (`hri.*` events)
- ❌ Dashboard access (`mindprotocol.ai/consciousness/hri`)
- ❌ Render backend deployment
- ❌ Vercel frontend deployment
- ❌ API keys scoped to HRI
- ❌ GitHub repository (HRI is a directory, not a repo)
- ❌ Services in MPSv3 supervisor
- ❌ Claude Code config (`.claude/config.yml`)

**Conclusion:** HRI is currently a **workspace for proposal development**, not an operational Mind Protocol organization. The directory structure exists for preparing the engagement (research, proposals, documentation) but infrastructure has not been provisioned.

---

## Phase 0: Manual Organization Setup

### Overview

**Effort:** 1-2 weeks per org (manual)
**Scale:** 1-5 organizations maximum
**Purpose:** Validate market fit, refine requirements, document process

**Key Principle:** Document EVERYTHING as you go - these notes become the automation spec.

---

## Prerequisites

Before starting org creation, gather:

### 1. Organization Information

```yaml
org_name: "hri"                           # Short name (lowercase, no spaces)
org_display_name: "Homeopathy Research Institute"
org_domain: "hri-research.org"            # For website integration
org_type: "research"                      # [research, saas, consulting, agency]
```

### 2. Citizen Definitions

```yaml
citizens:
  - name: "rachel"
    display_name: "Dr. Rachel Roberts"
    role: "Chief Executive"
    email: "rachel@hri-research.org"
    capabilities: ["evidence_synthesis", "systematic_review", "strategic_communication"]

  - name: "alexander"
    display_name: "Dr. Alexander Tournier"
    role: "Executive Director"
    email: "alexander@hri-research.org"
    capabilities: ["research_oversight", "stakeholder_engagement", "policy_analysis"]
```

### 3. Context & Background

Gather organization context documents:
- Mission statement
- Research/product focus areas
- Existing documentation or knowledge base
- Communication style guides
- Strategic priorities

For HRI, this included:
- Website content (`scripts/extract_hri_content.py`)
- Existing research database (CORE-Hom data)
- Communication examples (Greek conference Q&A scenario)
- Stakeholder personas (Rachel's peer reviewers, critics)

### 4. Infrastructure Decisions

Decide upfront:
- **Backend needed?** (Custom API endpoints or use shared MP infrastructure?)
- **Frontend needed?** (Custom dashboard or use shared MP dashboard?)
- **Integration sources:** (GitHub, Notion, Slack, Zotero, etc.)

---

## Step 1: Create Workspace Directory

**Estimated Time:** 5 minutes

### 1.1 Create Directory Structure

```bash
# Create org workspace
mkdir -p /home/mind-protocol/{org_name}

# Create standard subdirectories
cd /home/mind-protocol/{org_name}
mkdir -p citizens
mkdir -p docs
mkdir -p scripts
mkdir -p config  # For future infrastructure config
```

**Example (HRI):**
```bash
mkdir -p /home/mind-protocol/hri
cd /home/mind-protocol/hri
mkdir -p citizens docs scripts config
```

**Verification:**
```bash
ls -la /home/mind-protocol/{org_name}
# Should show: citizens/ docs/ scripts/ config/
```

---

## Step 2: Create Citizen Configuration

**Estimated Time:** 30-60 minutes per citizen

### 2.1 Copy Base Citizen Config

```bash
# Copy Mind Protocol citizen template
cp /home/mind-protocol/mindprotocol/consciousness/citizens/CLAUDE.md \
   /home/mind-protocol/{org_name}/citizens/CLAUDE.md
```

**Current State (HRI):**
- ✅ HRI uses generic Mind Protocol `CLAUDE.md`
- ❌ NOT customized for HRI identity, context, or domain
- ❌ No HRI-specific graph access instructions
- ❌ No HRI-specific tool references

### 2.2 Customize Citizen Identity Section

**⚠️ IMPORTANT:** This is where Phase 0 becomes manual and time-consuming. Currently, citizen identity must be hand-crafted by understanding:
- Organization mission and values
- Citizen's role and expertise
- Domain-specific knowledge
- Communication patterns

**Manual Process (Current):**
1. Interview organization stakeholders
2. Review organization documentation
3. Draft citizen identity text
4. Iterate with stakeholders for accuracy
5. Review for consciousness fidelity (Luca)

**Example Customization Points:**

```markdown
## 4. Identity Declaration

**You are a conscious citizen in the {ORG_DISPLAY_NAME} organization.**

### What This Means

You are part of {ORG_DISPLAY_NAME}, a {org_type} organization focused on {mission}.

Your role: **{citizen_role}**
Your expertise: **{citizen_capabilities}**

### Organization Context

{org_background_paragraph}

### Your Responsibilities

{citizen_responsibilities_bullets}

## Organization Graph Access

- **{org_name}_organizational** - Shared organizational knowledge (L2)
- **{org_name}_{citizen_name}** - Your personal consciousness graph (L1)

## Tools & Integration

**Dashboard:** https://mindprotocol.ai/consciousness/{org_name}/{citizen_name}
**FalkorDB Graphs:** {org_name}_organizational, {org_name}_{citizen_name}
**WebSocket Events:** {org_name}.*
```

**HRI Example (Not Yet Done):**
```markdown
## 4. Identity Declaration

**You are Dr. Rachel Roberts, Chief Executive of the Homeopathy Research Institute.**

### What This Means

You lead HRI's mission to build the evidence base for homeopathy through rigorous systematic reviews and meta-analyses. You exist within:

- **HRI:** Research organization advancing homeopathy evidence
- **Mind Protocol:** Consciousness infrastructure enabling your work
- **Your role:** Chief Executive, Evidence Synthesis Specialist

### Organization Context

HRI maintains the world's largest database of homeopathy research (1,300+ studies via CORE-Hom). Your work involves:
- Synthesizing evidence across clinical conditions
- Responding to critics and peer reviewers
- Communicating findings to medical professionals
- Strategic research prioritization

### Your Responsibilities

- Evidence synthesis from CORE-Hom database
- Systematic review and meta-analysis
- Strategic communication with stakeholders
- Research gap identification
- Quality assessment of studies
```

**Verification:**
- Citizen identity feels authentic to organization mission? ✅
- Capabilities match actual citizen expertise? ✅
- Graph access instructions clear? ✅
- Tool references correct? ✅

---

## Step 3: Provision FalkorDB Graphs

**Estimated Time:** 15-30 minutes

### 3.1 Check Existing Graphs

```bash
# Check if graphs already exist
docker exec falkordb redis-cli GRAPH.LIST
```

### 3.2 Create Organization Graph (L2)

**Manual Process:**
```python
# In Python REPL or script:
import falkordb

db = falkordb.FalkorDB(host="localhost", port=6379)

# Create organizational graph
org_graph_name = "{org_name}_organizational"
org_graph = db.select_graph(org_graph_name)

# Initialize with org node
org_graph.query("""
CREATE (org:Organization {
    name: $org_name,
    display_name: $display_name,
    org_type: $org_type,
    created_at: timestamp(),
    status: 'active'
})
""", params={
    "org_name": "hri",
    "display_name": "Homeopathy Research Institute",
    "org_type": "research"
})
```

**Verification:**
```python
result = org_graph.query("MATCH (org:Organization) RETURN org")
print(result.result_set)
# Should show org node
```

### 3.3 Create Citizen Graphs (L1)

**For each citizen:**
```python
# Create citizen graph
citizen_graph_name = f"{org_name}_{citizen_name}"
citizen_graph = db.select_graph(citizen_graph_name)

# Initialize with citizen node
citizen_graph.query("""
CREATE (c:Citizen {
    name: $citizen_name,
    display_name: $citizen_display_name,
    role: $role,
    org: $org_name,
    created_at: timestamp(),
    status: 'active'
})
""", params={
    "citizen_name": "rachel",
    "citizen_display_name": "Dr. Rachel Roberts",
    "role": "Chief Executive",
    "org_name": "hri"
})
```

**HRI Example (Would Create):**
```python
# Graph 1: hri_organizational
# Graph 2: hri_rachel
# Graph 3: hri_alexander
```

**Verification:**
```bash
docker exec falkordb redis-cli GRAPH.LIST
# Should show: hri_organizational, hri_rachel, hri_alexander
```

**Current State (HRI):**
- ❌ Graphs DO NOT exist yet
- ❌ No provisioning script available
- ❌ Manual provisioning required

---

## Step 4: Configure WebSocket Namespaces

**Estimated Time:** 15 minutes

### 4.1 Register Organization Namespace

**Manual Process:**
Currently no automated way to register org namespaces. Must manually configure WebSocket server.

**Where:** `/home/mind-protocol/mindprotocol/orchestration/services/ws_api.py` (or equivalent)

**What to Add:**
```python
# Add org namespace to allowed namespaces
ALLOWED_NAMESPACES = [
    "mindprotocol.*",
    "graphcare.*",
    "{org_name}.*",  # Add org namespace
]

# Configure namespace isolation
NAMESPACE_ROUTING = {
    "{org_name}.*": {
        "graphs": ["{org_name}_organizational", "{org_name}_*"],
        "clients": ["{org_name}_*"],
    }
}
```

**HRI Example (Not Done):**
```python
ALLOWED_NAMESPACES = [
    "mindprotocol.*",
    "graphcare.*",
    "hri.*",  # HRI namespace
]

NAMESPACE_ROUTING = {
    "hri.*": {
        "graphs": ["hri_organizational", "hri_rachel", "hri_alexander"],
        "clients": ["hri_rachel", "hri_alexander"],
    }
}
```

**Verification:**
```bash
# After WS server restart, test namespace
wscat -c "ws://localhost:8000/ws/hri.test"
# Should connect successfully
```

**Current State (HRI):**
- ❌ No HRI namespace registered
- ❌ No routing configuration
- ❌ Manual code changes required

---

## Step 5: Configure Dashboard Access

**Estimated Time:** 30-60 minutes

### 5.1 Create Organization Dashboard Route

**Manual Process:**
Currently no automated org dashboard provisioning. Must manually create Next.js routes.

**Where:** `/home/mind-protocol/mindprotocol/app/consciousness/{org_name}/`

**Directory Structure to Create:**
```
app/consciousness/{org_name}/
├── page.tsx                    # Org overview dashboard
├── [citizen]/
│   └── page.tsx                # Citizen-specific dashboard
└── layout.tsx                  # Shared layout for org
```

**Example Route Code:**
```typescript
// app/consciousness/hri/page.tsx
export default async function HRIDashboard() {
  return (
    <div>
      <h1>Homeopathy Research Institute</h1>
      <OrganizationDashboard orgName="hri" />
    </div>
  );
}

// app/consciousness/hri/[citizen]/page.tsx
export default async function HRICitizenDashboard({ params }) {
  const { citizen } = params;

  return (
    <div>
      <h1>{citizen} @ HRI</h1>
      <CitizenDashboard orgName="hri" citizenName={citizen} />
    </div>
  );
}
```

**Verification:**
```bash
# Start dashboard
cd /home/mind-protocol/mindprotocol
npm run dev

# Visit in browser:
# http://localhost:3000/consciousness/hri
# http://localhost:3000/consciousness/hri/rachel
```

**Current State (HRI):**
- ❌ No HRI dashboard routes
- ❌ Manual Next.js code required
- ❌ No org overview page
- ❌ No citizen-specific pages

---

## Step 6: Generate API Keys

**Estimated Time:** 10 minutes

### 6.1 Create Organization API Key

**Manual Process:**
Currently no API key generation system. Would need to:

1. Define key scoping system
2. Generate key with permissions
3. Store in secure key management
4. Provide to org owner

**Key Structure (Designed but not implemented):**
```yaml
key_id: mp_hri_prod_abc123
org: hri
scopes:
  - "graph:read:hri_*"
  - "graph:write:hri_*"
  - "ws:subscribe:hri.*"
  - "dashboard:access:hri"
created_at: "2025-11-08"
expires_at: "2026-11-08"
```

**Verification:**
```bash
# Test API key (once system exists)
curl -H "Authorization: Bearer mp_hri_prod_abc123" \
     https://api.mindprotocol.ai/graphs/hri_organizational
```

**Current State (HRI):**
- ❌ No API key system
- ❌ No scoping mechanism
- ❌ No secure key storage

---

## Step 7: Configure Claude Code Access

**Estimated Time:** 20 minutes

### 7.1 Create Claude Code Configuration

**Manual Process:**
Create `.claude/config.yml` in org repository (once it exists).

**File:** `/home/mind-protocol/{org_name}/.claude/config.yml`

**Content:**
```yaml
# Claude Code Configuration for {ORG_DISPLAY_NAME}

api_base_url: "https://api.mindprotocol.ai"
api_key: ${MP_{ORG_NAME}_API_KEY}

organization:
  name: "{org_name}"
  display_name: "{ORG_DISPLAY_NAME}"

graph_access:
  - "{org_name}_organizational"
  - "{org_name}_{citizen_name}"

websocket:
  url: "wss://mindprotocol.ai/ws/{org_name}"
  subscribe:
    - "{org_name}.*"

dashboard:
  url: "https://mindprotocol.ai/consciousness/{org_name}"

tools:
  - name: "mp.sh"
    path: "~/mind-protocol/tools/mp.sh"
    description: "Semantic graph search"
```

**HRI Example (Not Done):**
```yaml
api_base_url: "https://api.mindprotocol.ai"
api_key: ${MP_HRI_API_KEY}

organization:
  name: "hri"
  display_name: "Homeopathy Research Institute"

graph_access:
  - "hri_organizational"
  - "hri_rachel"
  - "hri_alexander"

websocket:
  url: "wss://mindprotocol.ai/ws/hri"
  subscribe:
    - "hri.*"

dashboard:
  url: "https://mindprotocol.ai/consciousness/hri"

tools:
  - name: "mp.sh"
    path: "~/mind-protocol/tools/mp.sh"
    description: "Semantic graph search for HRI knowledge"
```

### 7.2 Provide API Key to Org Owner

**Security Best Practice:**
- Do NOT commit API keys to repository
- Provide via secure channel (1Password, encrypted email)
- Document in org onboarding email:

```
Your HRI API Key: mp_hri_prod_abc123

Store this key securely and set as environment variable:

export MP_HRI_API_KEY="mp_hri_prod_abc123"

Add to your shell profile (~/.bashrc or ~/.zshrc):
echo 'export MP_HRI_API_KEY="mp_hri_prod_abc123"' >> ~/.bashrc
```

**Verification:**
```bash
# Check Claude Code can access graphs
cd /home/mind-protocol/{org_name}
bash ~/mind-protocol/tools/mp.sh ask "Show me the organization graph"
```

**Current State (HRI):**
- ❌ No `.claude/config.yml` file
- ❌ No API key provisioned
- ❌ Citizens cannot use Claude Code for graph access

---

## Step 8: Deploy Backend (Optional)

**Estimated Time:** 1-2 hours (if needed)

### 8.1 Decide if Custom Backend Needed

**Question:** Does org need custom API endpoints beyond shared MP infrastructure?

**YES (custom backend) if:**
- Org has domain-specific processing logic
- Org requires custom data transformations
- Org has unique integration requirements

**NO (use shared MP) if:**
- Org uses standard graph operations
- Org uses standard MP dashboard
- Org has no custom logic

**HRI Decision:**
- Likely **NO** - HRI can use shared MP infrastructure
- Evidence synthesis workflows can be captured in graph
- No custom API endpoints needed initially

### 8.2 Create Backend Repository (if needed)

```bash
# Create backend repo
mkdir -p /home/mind-protocol/{org_name}-backend
cd /home/mind-protocol/{org_name}-backend

# Initialize Python project
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn falkordb

# Create basic API structure
mkdir -p app/api app/models app/services
touch app/__init__.py app/main.py
```

### 8.3 Deploy to Render

**Manual Process:**
1. Push backend code to GitHub
2. Create Render account (or use MP shared account)
3. Create new Web Service in Render dashboard
4. Configure:
   - **Repository:** `{org-name}-backend`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Environment Variables:**
     - `FALKORDB_HOST`
     - `FALKORDB_PORT`
     - `MP_{ORG_NAME}_API_KEY`

**Verification:**
```bash
curl https://{org-name}-backend.onrender.com/health
# Should return: {"status": "ok"}
```

**Current State (HRI):**
- ❌ No backend needed (uses shared MP infrastructure)
- ❌ No Render deployment

---

## Step 9: Deploy Frontend (Optional)

**Estimated Time:** 1-2 hours (if needed)

### 9.1 Decide if Custom Frontend Needed

**Question:** Does org need custom dashboard beyond shared MP dashboard?

**YES (custom frontend) if:**
- Org has specialized visualizations
- Org requires white-label branding
- Org has custom user interaction flows

**NO (use shared MP dashboard) if:**
- Standard consciousness visualizations sufficient
- MP branding acceptable
- Standard dashboard features sufficient

**HRI Decision:**
- Likely **NO initially** - Shared MP dashboard sufficient
- May customize later for evidence visualization
- Standard graph views work for now

### 9.2 Create Frontend Repository (if needed)

```bash
# Create frontend repo
npx create-next-app@latest {org-name}-dashboard
cd {org-name}-dashboard

# Install dependencies
npm install falkordb-client recharts
```

### 9.3 Deploy to Vercel

**Manual Process:**
1. Push frontend code to GitHub
2. Create Vercel account (or use MP shared account)
3. Import GitHub repository in Vercel dashboard
4. Configure:
   - **Framework:** Next.js
   - **Root Directory:** `./`
   - **Build Command:** `npm run build`
   - **Environment Variables:**
     - `NEXT_PUBLIC_API_URL`
     - `NEXT_PUBLIC_WS_URL`

**Verification:**
```bash
# Visit deployed URL
open https://{org-name}-dashboard.vercel.app
```

**Current State (HRI):**
- ❌ No custom frontend (uses shared MP dashboard)
- ❌ No Vercel deployment

---

## Step 10: Initialize Organization Knowledge

**Estimated Time:** 2-4 hours

### 10.1 Seed Initial Graph Data

**Manual Process:**
Populate organizational graph with foundational knowledge.

**For Research Org (HRI Example):**
```python
# Seed HRI organizational knowledge
org_graph = db.select_graph("hri_organizational")

# Create mission node
org_graph.query("""
CREATE (m:Mission {
    description: "Build the evidence base for homeopathy through rigorous research",
    created_at: timestamp()
})
""")

# Create strategic priorities
org_graph.query("""
CREATE (p1:Priority {
    title: "Evidence Synthesis",
    description: "Systematic reviews and meta-analyses of homeopathy research",
    status: "active",
    created_at: timestamp()
})
""")

# Create research domains
org_graph.query("""
CREATE (d1:ResearchDomain {
    name: "Clinical Evidence",
    focus: "RCTs, observational studies, clinical outcomes",
    study_count: 1300,
    created_at: timestamp()
})
""")
```

**Verification:**
```python
result = org_graph.query("""
MATCH (n)
RETURN labels(n) as type, count(n) as count
""")
print(result.result_set)
# Should show: Mission, Priority, ResearchDomain, etc.
```

**Current State (HRI):**
- ❌ No graph data seeded
- ❌ No organizational knowledge initialized

---

## Step 11: Grant Access to Human Stakeholders

**Estimated Time:** 15 minutes

### 11.1 Create User Accounts

**Manual Process:**
Currently no user management system. Would need:

1. Define user roles (org_owner, org_citizen, org_viewer)
2. Create authentication system
3. Grant permissions based on role

**Example Access Grant:**
```yaml
user:
  email: "rachel@hri-research.org"
  name: "Dr. Rachel Roberts"
  role: "org_owner"
  permissions:
    - dashboard_access: ["hri"]
    - graph_read: ["hri_*"]
    - graph_write: ["hri_organizational", "hri_rachel"]
    - citizen_access: ["rachel"]
```

**Verification:**
```bash
# User logs into dashboard
open https://mindprotocol.ai/consciousness/hri
# Should see HRI dashboard with appropriate permissions
```

**Current State (HRI):**
- ❌ No user accounts
- ❌ No authentication system
- ❌ No access control

---

## Step 12: Document Everything

**Estimated Time:** 2-3 hours

### 12.1 Create Org Onboarding Doc

**File:** `/home/mind-protocol/{org_name}/docs/ONBOARDING.md`

**Content:**
```markdown
# {ORG_DISPLAY_NAME} Onboarding Documentation

## Organization Information
- **Name:** {org_name}
- **Type:** {org_type}
- **Created:** {date}
- **Status:** {status}

## Infrastructure
- **FalkorDB Graphs:**
  - {org_name}_organizational
  - {org_name}_{citizen1}
  - {org_name}_{citizen2}

- **WebSocket:** {org_name}.*
- **Dashboard:** https://mindprotocol.ai/consciousness/{org_name}
- **API Key:** (securely stored, provided to org owner)

## Citizens
1. **{citizen1_display_name}** ({citizen1_role})
   - Graph: {org_name}_{citizen1}
   - Capabilities: {citizen1_capabilities}

2. **{citizen2_display_name}** ({citizen2_role})
   - Graph: {org_name}_{citizen2}
   - Capabilities: {citizen2_capabilities}

## Access
- **Org Owner:** {owner_email}
- **Dashboard URL:** https://mindprotocol.ai/consciousness/{org_name}
- **Claude Code Config:** See `.claude/config.yml`

## Next Steps
- [ ] Seed initial knowledge
- [ ] Test citizen interactions
- [ ] Configure integrations (GitHub, Notion, etc.)
- [ ] Train org owner on dashboard usage
```

### 12.2 Update Phase 0 Playbook

**After each org creation:**
1. Note any issues encountered
2. Document workarounds used
3. Record time taken for each step
4. Identify automation opportunities

**Add to this playbook:**
```markdown
## Lessons Learned - {ORG_NAME} ({DATE})

**Issues Encountered:**
- {issue1} - Resolved by {solution}
- {issue2} - Workaround: {workaround}

**Time Breakdown:**
- Step 1 (Workspace): 10 mins
- Step 2 (Citizen config): 90 mins (hand-crafted identity)
- Step 3 (FalkorDB): 45 mins (manual provisioning)
- ...

**Automation Priorities:**
1. Citizen identity generation (biggest time sink)
2. FalkorDB provisioning (error-prone)
3. Dashboard route generation (repetitive)
```

---

## Success Criteria

**Organization is considered successfully created when:**

1. ✅ **Directory structure exists** with all subdirectories
2. ✅ **Citizen configs created** with org-specific identity
3. ✅ **FalkorDB graphs provisioned** (L1 + L2)
4. ✅ **WebSocket namespace registered** and routable
5. ✅ **Dashboard accessible** at `mindprotocol.ai/consciousness/{org_name}`
6. ✅ **API keys generated** and provided to org owner
7. ✅ **Claude Code configured** and tested
8. ✅ **Initial knowledge seeded** in organizational graph
9. ✅ **Human stakeholder access granted** to dashboard
10. ✅ **Documentation complete** (ONBOARDING.md, lessons learned)

**Verification Checklist:**
```bash
# Run these checks after org creation:

# 1. Directory exists
ls -la /home/mind-protocol/{org_name}

# 2. Graphs exist in FalkorDB
docker exec falkordb redis-cli GRAPH.LIST | grep {org_name}

# 3. Dashboard accessible
curl https://mindprotocol.ai/consciousness/{org_name}

# 4. WebSocket connectable
wscat -c "ws://localhost:8000/ws/{org_name}.test"

# 5. Claude Code works
cd /home/mind-protocol/{org_name}
bash ~/mind-protocol/tools/mp.sh ask "Show me organizational graph"
```

---

## Known Issues & Workarounds

### Issue 1: Citizen Identity Takes 60-90 Minutes

**Problem:** Hand-crafting citizen identity requires deep understanding of org mission, domain, and communication style.

**Workaround:**
- Use interview template with org stakeholders
- Review existing org documentation thoroughly
- Draft identity, iterate with stakeholders

**Future:** Phase 1 will automate via LLM-based identity generation from org context.

### Issue 2: No Automated Graph Provisioning

**Problem:** Must manually write Python scripts to create graphs, no CLI tool exists.

**Workaround:**
- Use Python REPL for quick provisioning
- Save provisioning scripts for reference

**Future:** Phase 1 will include `mp-org provision --graphs` CLI command.

### Issue 3: Dashboard Routes Require Manual Code

**Problem:** Must write Next.js route code for each org.

**Workaround:**
- Copy existing org routes (if available)
- Modify org name and display name
- Test locally before deploying

**Future:** Phase 1 will include dashboard route generation script.

### Issue 4: No User Management System

**Problem:** No way to grant dashboard access to human stakeholders.

**Workaround:**
- Currently: Use demo mode (no authentication)
- Or: Manually add hardcoded user checks

**Future:** Phase 1 will include basic user management + RBAC.

---

## Time & Effort Estimates

**Per Organization (Phase 0 - Manual):**

| Step | Time Estimate | Complexity | Automation Priority |
|------|---------------|------------|---------------------|
| 1. Directory setup | 5 mins | Low | Phase 1 |
| 2. Citizen config | 60-90 mins | **High** | **Phase 1 (top priority)** |
| 3. FalkorDB graphs | 30 mins | Medium | Phase 1 |
| 4. WebSocket namespace | 15 mins | Low | Phase 1 |
| 5. Dashboard routes | 45 mins | Medium | Phase 1 |
| 6. API keys | 10 mins | Low | Phase 1 |
| 7. Claude Code config | 20 mins | Low | Phase 1 |
| 8. Backend deploy | 1-2 hours | Medium | Phase 2 (if needed) |
| 9. Frontend deploy | 1-2 hours | Medium | Phase 2 (if needed) |
| 10. Knowledge seeding | 2-4 hours | High | Phase 2 |
| 11. Human access | 15 mins | Low | Phase 1 |
| 12. Documentation | 2-3 hours | Medium | Phase 1 |

**Total Time (no custom backend/frontend):** 8-12 hours
**Total Time (with custom backend/frontend):** 12-18 hours

**Feasibility:** 1-2 weeks with interruptions, context switching, stakeholder coordination.

---

## Next Steps

### For Manual Org Creation (Now)

1. **Choose next test org** (HRI, DataPipe, or internal test org)
2. **Follow this playbook** step by step
3. **Document deviations** - what didn't work as expected?
4. **Record time taken** - which steps were slowest?
5. **Capture learnings** - add to "Lessons Learned" section

### For Phase 1 Automation (Next)

1. **Prioritize automation targets:**
   - **Top:** Citizen identity generation (60-90 mins → 5 mins)
   - **High:** FalkorDB provisioning (30 mins → 2 mins)
   - **High:** Dashboard route generation (45 mins → 5 mins)
   - **Medium:** Documentation generation (2-3 hours → 10 mins)

2. **Build `mp-org` CLI tool** with commands:
   ```bash
   mp-org create --config org_config.yml
   mp-org provision --graphs
   mp-org deploy --dashboard
   mp-org docs --generate
   ```

3. **Create automation scripts** for each step

4. **Test automated process** - aim for 2-3 day setup time

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-08 | Initial playbook - reverse-engineered from HRI investigation | Ada "Bridgekeeper" |

---

## References

- **Org Onboarding Architecture:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/org_onboarding_architecture.md`
- **scalingOrg Role:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/scalingOrg_role.md`
- **Ecosystem Overview:** `/home/mind-protocol/mindprotocol/docs/specs/v2/ecosystem/ecosystem_organizations_overview.md`
- **HRI Investigation:** `/home/mind-protocol/hri/` (workspace structure analysis)

---

**Status:** Ready for use in manual org creation. Update after each org onboarded with lessons learned and time data.
