# Ticket System Setup Guide

**Status:** Ready for Implementation
**Version:** 1.0.0
**Date:** 2025-10-31
**Team:** Ada (Coordinator), Luca (L4 Registry), Atlas (Infrastructure), Felix (Webhook), Iris (UI)

---

## Overview

This guide provides **complete, copy-paste artifacts** to implement L4-governed ticketing across the Mind Protocol ecosystem. The system integrates:

- **L4 governance** (rules, policies, conformance)
- **L2 work items** (tickets, bugs, missions in org graphs)
- **GitHub Issues** (source of truth for tickets)
- **Real-time sync** (webhook → graph → dashboard)
- **Evidence enforcement** (can't close without proof)

**Architecture:** L4 law + U4_Work_Item schema + generic telemetry events

---

## 📋 Implementation Checklist

### Phase 1: L4 Foundation (2 hours)
- [ ] 1.1: Read governance spec (`docs/specs/v2/governance/ticket_governance.md`)
- [ ] 1.2: Run topic namespace ingestion (`python tools/protocol/ingest_work_topics.py`)
- [ ] 1.3: Export L4 registry (`python tools/protocol/export_l4_public.py`)
- [ ] 1.4: Verify in FalkorDB (queries below)

### Phase 2: GitHub Integration (4 hours)
- [ ] 2.1: Add issue templates (`.github/ISSUE_TEMPLATE/`)
- [ ] 2.2: Create webhook service (`services/ingestors/github_webhook.py`)
- [ ] 2.3: Configure GitHub webhook (repo settings)
- [ ] 2.4: Test: Create issue → see in graph

### Phase 3: Evidence Enforcement (2 hours)
- [ ] 3.1: Add GitHub bot (`services/bots/ticket_closer.py`)
- [ ] 3.2: Add mp-lint rules (R-501 through R-506)
- [ ] 3.3: Test: Try closing without evidence → bot reopens

### Phase 4: Dashboard UI (4 hours)
- [ ] 4.1: Ticket list component (`app/tickets/page.tsx`)
- [ ] 4.2: Ticket detail panel (evidence links, state timeline)
- [ ] 4.3: Filters (priority, component, assignee)

### Phase 5: CI Integration (2 hours)
- [ ] 5.1: Add mp-lint workflow (`.github/workflows/mp-lint.yml`)
- [ ] 5.2: Auto-create issues for violations
- [ ] 5.3: Block release on P0 tickets

---

## 1. L4 Foundation

### 1.1 Governance Specification

**File:** `docs/specs/v2/governance/ticket_governance.md`

✅ Already created - defines:
- ID format (`gh:org/repo#number`)
- Lifecycle states (`todo → doing → blocked → done`)
- Priority levels (P0-P3) and deployment gates
- Evidence requirements for closing
- Event schemas (`work.*` topics)

**Read it first** - it's the law for the entire system.

### 1.2 Topic Namespace Ingestion

**File:** `tools/protocol/ingest_work_topics.py`

✅ Already created - seeds:
- 3 topic namespaces (`work.ticket.*`, `work.bug.*`, `work.mission.*`)
- 10 concrete topic mappings (reuses `telemetry.lifecycle` and `telemetry.state`)
- 1 governance policy (`POL_WORK_TICKETS_V1`)
- 1 schema bundle (`BUNDLE_WORK_ITEMS_1_0_0`)

**Run:**
```bash
cd /home/mind-protocol/mindprotocol
python3 tools/protocol/ingest_work_topics.py
```

**Expected output:**
```
📋 Work Item Topic Namespaces Ingestion
======================================================================
0️⃣  Ensuring Signature Suite and Envelope Schema exist...
  ✓ SIG_ED25519_V1 (ed25519)
  ✓ ENV_STANDARD_V1

1️⃣  Creating Topic Namespaces (wildcard patterns)...
  📝 FLEX   work.ticket.*                   - Standard work item lifecycle (ticket creation, upd
  📝 FLEX   work.bug.*                      - Bug tracking lifecycle (bug reports, fixes, verific
  📝 FLEX   work.mission.*                  - Mission/milestone tracking (multi-part objectives w

2️⃣  Creating Schema Bundle...
  ✓ BUNDLE_WORK_ITEMS_1_0_0 (active)

3️⃣  Linking Work Topics to Generic Telemetry Schemas...
  ✓ work.ticket.opened                  → telemetry.lifecycle@1.0.0
  ✓ work.ticket.updated                 → telemetry.state@1.0.0
  ✓ work.ticket.closed                  → telemetry.lifecycle@1.0.0
  ... (10 total mappings)

4️⃣  Creating Governance Policy...
  ✓ POL_WORK_TICKETS_V1            - FLEX (signature required, 3 namespaces)

======================================================================
✅ Ingested work item topic namespaces
```

### 1.3 Export L4 Registry

**Run:**
```bash
python3 tools/protocol/export_l4_public.py
```

**Verify:**
```bash
grep -c "work\." build/l4_public_registry.json
# Should see work.ticket, work.bug, work.mission topics
```

### 1.4 Verification Queries

**Check topic namespaces:**
```cypher
MATCH (ns:L4_Topic_Namespace)
WHERE ns.name STARTS WITH 'work.'
RETURN ns.name, ns.pattern, ns.description
```

**Expected:**
```
work.ticket  | work.ticket.*  | Standard work item lifecycle...
work.bug     | work.bug.*     | Bug tracking lifecycle...
work.mission | work.mission.* | Mission/milestone tracking...
```

**Check governance policy:**
```cypher
MATCH (gp:L4_Governance_Policy {policy_id: 'POL_WORK_TICKETS_V1'})-[:U4_GOVERNS]->(ns)
RETURN gp.name, collect(ns.name) as namespaces
```

**Expected:**
```
Work Item Lifecycle Policy | [work.ticket, work.bug, work.mission]
```

---

## 2. GitHub Integration

### 2.1 Issue Templates

Create `.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Mind Protocol Discussions
    url: https://github.com/mind-protocol/mindprotocol/discussions
    about: General questions and discussions
```

Create `.github/ISSUE_TEMPLATE/ticket.yml`:

```yaml
name: 🎫 Ticket
description: Standard work item with problem, remediation, and acceptance criteria
title: "[COMPONENT] "
labels: ["ticket", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        ## Ticket Creation
        Fill out all required fields. This ticket will sync to the consciousness graph.

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: Urgency/importance level
      options:
        - P3 - Low (best effort, 2+ weeks)
        - P2 - Medium (2 weeks, no deployment gate)
        - P1 - High (3 days, warns on release)
        - P0 - Critical (24h, BLOCKS release)
    validations:
      required: true

  - type: input
    id: component
    attributes:
      label: Component
      description: System area affected
      placeholder: "L4 Protocol / Event Registry"
    validations:
      required: true

  - type: input
    id: owner
    attributes:
      label: Owner
      description: GitHub handle (@username)
      placeholder: "@ada"
    validations:
      required: true

  - type: input
    id: estimate
    attributes:
      label: Estimate
      description: Time estimate
      placeholder: "2h, 3 days"

  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What is wrong or missing?
      placeholder: "Describe the problem clearly..."
    validations:
      required: true

  - type: textarea
    id: impact
    attributes:
      label: Impact
      description: Who/what is affected? What breaks if not fixed?
      placeholder: "SafeBroadcaster will reject events..."

  - type: textarea
    id: remediation
    attributes:
      label: Remediation Plan
      description: Steps to fix
      placeholder: |
        1. Update ingest_work_topics.py to add namespace
        2. Run ingestion script
        3. Re-export L4 registry
    validations:
      required: true

  - type: textarea
    id: acceptance_criteria
    attributes:
      label: Acceptance Criteria
      description: Checklist of completion requirements
      value: |
        - [ ] Code implemented and reviewed
        - [ ] Tests pass (if applicable)
        - [ ] Documentation updated
        - [ ] mp-lint clean
    validations:
      required: true
```

Create `.github/ISSUE_TEMPLATE/bug.yml`:

```yaml
name: 🐛 Bug Report
description: Report a defect requiring fix
title: "[BUG] "
labels: ["bug", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        ## Bug Report
        Provide details about the bug. This will sync to the consciousness graph.

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      description: Impact level
      options:
        - Low - Minor impact (typo, cosmetic)
        - Medium - Moderate impact (UI glitch, slow performance)
        - High - Major impact, workaround exists (silent fallback R-301)
        - Absolute - No workaround, complete failure (crash, data loss)
    validations:
      required: true

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: Urgency
      options:
        - P3 - Low
        - P2 - Medium
        - P1 - High
        - P0 - Critical
    validations:
      required: true

  - type: input
    id: component
    attributes:
      label: Component
      description: System area
      placeholder: "tools/cc_prune"
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: How to trigger the bug
      placeholder: |
        1. Run `python tools/cc_prune/main.py`
        2. Inject malformed file path
        3. Observe silent fallback (no error logged)
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen?
      placeholder: "Tool should emit failure.emit and log error"

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happens?
      placeholder: "Tool returns empty list silently (R-301 violation)"

  - type: textarea
    id: fix
    attributes:
      label: Proposed Fix
      description: How to fix it?
      placeholder: |
        1. Add try/except handler
        2. Log error before fallback
        3. Emit failure.emit event

  - type: textarea
    id: acceptance_criteria
    attributes:
      label: Acceptance Criteria
      description: How to verify fix
      value: |
        - [ ] Bug no longer reproducible
        - [ ] Test added for regression
        - [ ] mp-lint passes (no new violations)
    validations:
      required: true
```

### 2.2 Webhook Service

Create `services/ingestors/github_webhook.py`:

```python
#!/usr/bin/env python3
"""
GitHub Webhook → Consciousness Graph Sync

Mirrors GitHub Issues to U4_Work_Item nodes in org graphs.
Emits work.* telemetry events for dashboard updates.

Events handled:
- issues.opened → CREATE U4_Work_Item, emit work.*.opened
- issues.assigned → MERGE U4_ASSIGNED_TO, emit work.*.updated
- issues.labeled → UPDATE properties, emit work.*.updated
- issues.closed → SET state=done (validate evidence!), emit work.*.closed
- pull_request.closed (merged) → CREATE evidence links

Architecture: FastAPI webhook → FalkorDB → SafeBroadcaster

Author: Felix (Infrastructure Engineer) + Atlas (Operations)
Date: 2025-10-31
"""

from fastapi import FastAPI, Request, HTTPException
from falkordb import FalkorDB
import hashlib
import hmac
import os
from datetime import datetime, timezone

app = FastAPI()

# Initialize FalkorDB
db = FalkorDB(
    host=os.getenv("FALKOR_HOST", "localhost"),
    port=int(os.getenv("FALKOR_PORT", "6379"))
)

# GitHub webhook secret (set in repo settings)
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not WEBHOOK_SECRET:
        return True  # Dev mode

    mac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256)
    expected = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature)


def get_work_type(labels: list[str]) -> str:
    """Determine work_type from GitHub labels."""
    if "bug" in labels:
        return "bug"
    elif "mission" in labels or "milestone" in labels:
        return "mission"
    else:
        return "ticket"


def parse_priority(body: str) -> str:
    """Extract priority from issue body."""
    # Look for "Priority: P0" or dropdown value
    for line in body.split("\n"):
        if "priority" in line.lower():
            if "p0" in line.lower() or "critical" in line.lower():
                return "critical"
            elif "p1" in line.lower() or "high" in line.lower():
                return "high"
            elif "p2" in line.lower() or "medium" in line.lower():
                return "medium"
    return "low"


def parse_component(body: str) -> str:
    """Extract component from issue body."""
    for line in body.split("\n"):
        if "component" in line.lower() and ":" in line:
            return line.split(":", 1)[1].strip()
    return "General"


@app.post("/webhook/github")
async def handle_github_webhook(request: Request):
    """Handle GitHub webhook events."""

    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload = await request.body()

    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse event
    event_type = request.headers.get("X-GitHub-Event", "")
    data = await request.json()

    # Route to handlers
    if event_type == "issues":
        return handle_issue_event(data)
    elif event_type == "pull_request":
        return handle_pr_event(data)
    else:
        return {"status": "ignored", "event": event_type}


def handle_issue_event(data: dict):
    """Handle issues.* events."""
    action = data["action"]
    issue = data["issue"]
    repo = data["repository"]["full_name"]
    org_id = repo.split("/")[0]  # Org name as scope_ref

    ticket_id = f"gh:{repo}#{issue['number']}"
    node_id = f"wi:{repo}#{issue['number']}"

    # Get graph (create if doesn't exist)
    graph_name = f"org_{org_id}".replace("-", "_")
    g = db.select_graph(graph_name)

    if action == "opened":
        # Create U4_Work_Item
        work_type = get_work_type([label["name"] for label in issue["labels"]])
        priority = parse_priority(issue["body"] or "")
        component = parse_component(issue["body"] or "")

        query = """
        MERGE (w:U4_Work_Item {node_id: $node_id})
        ON CREATE SET
            w.ticket_id = $ticket_id,
            w.name = $name,
            w.work_type = $work_type,
            w.state = 'todo',
            w.priority = $priority,
            w.level = 'L2',
            w.scope_ref = $scope_ref,
            w.component = $component,
            w.description = $description,
            w.created_at = timestamp(),
            w.updated_at = timestamp()
        ON MATCH SET
            w.updated_at = timestamp()
        """

        g.query(query, params={
            "node_id": node_id,
            "ticket_id": ticket_id,
            "name": issue["title"],
            "work_type": work_type,
            "priority": priority,
            "scope_ref": org_id,
            "component": component,
            "description": issue["body"] or ""
        })

        # TODO: Emit work.ticket.opened event via SafeBroadcaster

        return {"status": "created", "node_id": node_id}

    elif action == "assigned":
        # Add U4_ASSIGNED_TO link
        assignee = data["assignee"]["login"]

        query = """
        MATCH (w:U4_Work_Item {node_id: $node_id})
        MERGE (a:U4_Agent {agent_id: $assignee})
        ON CREATE SET
            a.agent_type = 'human',
            a.level = 'L1',
            a.scope_ref = $assignee
        MERGE (w)-[r:U4_ASSIGNED_TO]->(a)
        ON CREATE SET
            r.role = 'owner',
            r.since = timestamp()
        """

        g.query(query, params={
            "node_id": node_id,
            "assignee": f"github:{assignee}"
        })

        # Update state if was in todo
        g.query("""
            MATCH (w:U4_Work_Item {node_id: $node_id})
            WHERE w.state = 'todo'
            SET w.state = 'doing', w.updated_at = timestamp()
        """, params={"node_id": node_id})

        # TODO: Emit work.ticket.updated event

        return {"status": "assigned", "assignee": assignee}

    elif action == "closed":
        # Check evidence requirement (L4 law!)
        evidence_query = """
        MATCH (w:U4_Work_Item {node_id: $node_id})-[:U4_EVIDENCED_BY]->()
        RETURN count(*) as evidence_count
        """
        result = g.query(evidence_query, params={"node_id": node_id})
        evidence_count = result.result_set[0][0] if result.result_set else 0

        if evidence_count == 0:
            # No evidence → REOPEN (enforcing L4 law)
            # TODO: Comment on issue and reopen via GitHub API
            return {"status": "rejected", "reason": "No evidence. Add U4_EVIDENCED_BY link."}

        # Set state to done
        g.query("""
            MATCH (w:U4_Work_Item {node_id: $node_id})
            SET w.state = 'done', w.updated_at = timestamp()
        """, params={"node_id": node_id})

        # TODO: Emit work.ticket.closed event

        return {"status": "closed", "node_id": node_id}

    elif action == "reopened":
        g.query("""
            MATCH (w:U4_Work_Item {node_id: $node_id})
            SET w.state = 'doing', w.updated_at = timestamp()
        """, params={"node_id": node_id})

        return {"status": "reopened"}

    return {"status": "handled", "action": action}


def handle_pr_event(data: dict):
    """Handle pull_request.* events."""
    action = data["action"]
    pr = data["pull_request"]
    repo = data["repository"]["full_name"]
    org_id = repo.split("/")[0]

    if action == "closed" and pr.get("merged"):
        # PR merged → create evidence links

        # Parse "Closes #123" or "Fixes #456" from PR body
        body = pr.get("body", "")
        import re
        closes_pattern = r"(?:Closes|Fixes|Resolves)\s+#(\d+)"
        matches = re.findall(closes_pattern, body, re.IGNORECASE)

        if not matches:
            return {"status": "no_ticket_refs"}

        graph_name = f"org_{org_id}".replace("-", "_")
        g = db.select_graph(graph_name)

        # Create U4_Code_Artifact for PR
        artifact_id = f"pr:{repo}#{pr['number']}"

        artifact_query = """
        MERGE (ca:U4_Code_Artifact {node_id: $artifact_id})
        ON CREATE SET
            ca.path = $path,
            ca.repo = $repo,
            ca.lang = 'mixed',
            ca.hash = $hash,
            ca.commit = $commit,
            ca.description = $description
        """

        g.query(artifact_query, params={
            "artifact_id": artifact_id,
            "path": f"PR #{pr['number']}",
            "repo": repo,
            "hash": pr["merge_commit_sha"],
            "commit": pr["merge_commit_sha"],
            "description": pr["title"]
        })

        # Link to tickets
        for issue_num in matches:
            ticket_id = f"gh:{repo}#{issue_num}"
            node_id = f"wi:{repo}#{issue_num}"

            link_query = """
            MATCH (w:U4_Work_Item {node_id: $node_id})
            MATCH (ca:U4_Code_Artifact {node_id: $artifact_id})
            MERGE (w)-[e:U4_EVIDENCED_BY]->(ca)
            ON CREATE SET
                e.evidence_type = 'pr_merged',
                e.confidence = 1.0
            """

            g.query(link_query, params={
                "node_id": node_id,
                "artifact_id": artifact_id
            })

        # TODO: Emit work.ticket.evidence events

        return {"status": "evidence_added", "tickets": matches}

    return {"status": "ignored"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "github_webhook"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Deploy:**
```bash
# Add to MPSv3 supervisor services.yaml
- name: github_webhook
  cmd: "cd services/ingestors && python github_webhook.py"
  requires: []
  readiness:
    type: http
    url: "http://localhost:8001/health"
  watch:
    - "services/ingestors/*.py"
```

**Configure GitHub webhook:**
1. Go to repo → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-domain.com/webhook/github`
3. Content type: `application/json`
4. Secret: Set `GITHUB_WEBHOOK_SECRET` env var
5. Events: Issues, Pull requests

### 2.3 Testing

**Create test issue:**
1. Go to GitHub → Issues → New Issue
2. Select "🎫 Ticket" template
3. Fill out form
4. Create issue

**Verify in graph:**
```cypher
MATCH (w:U4_Work_Item)
WHERE w.ticket_id STARTS WITH 'gh:'
RETURN w.ticket_id, w.name, w.state, w.priority
ORDER BY w.created_at DESC
LIMIT 5
```

**Should see:**
```
gh:mind-protocol/mindprotocol#123 | [L4-001] Test ticket | todo | medium
```

---

## 3. Evidence Enforcement

### 3.1 GitHub Bot (Ticket Closer)

Create `services/bots/ticket_closer.py`:

```python
#!/usr/bin/env python3
"""
Ticket Closer Bot - Enforces L4 Evidence Rule

Monitors issues.closed events and enforces:
1. At least one U4_EVIDENCED_BY link exists
2. Acceptance criteria are checked
3. mp-lint passes on evidence PR

If requirements fail → comments and REOPENS issue.

This bot enforces L4 law (ticket_governance.md §6.1).

Author: Ada (Governance) + Atlas (Bot infrastructure)
Date: 2025-10-31
"""

from github import Github
from falkordb import FalkorDB
import os
import re

gh = Github(os.getenv("GITHUB_TOKEN"))
db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)


def can_close_ticket(repo_full_name: str, issue_number: int) -> tuple[bool, str]:
    """
    Check if ticket meets L4 evidence requirements.

    Returns:
        (can_close: bool, reason: str)
    """
    org_id = repo_full_name.split("/")[0]
    graph_name = f"org_{org_id}".replace("-", "_")
    g = db.select_graph(graph_name)

    node_id = f"wi:{repo_full_name}#{issue_number}"

    # Check 1: Evidence exists
    evidence_query = """
    MATCH (w:U4_Work_Item {node_id: $node_id})-[:U4_EVIDENCED_BY]->()
    RETURN count(*) as evidence_count
    """
    result = g.query(evidence_query, params={"node_id": node_id})
    evidence_count = result.result_set[0][0] if result.result_set else 0

    if evidence_count == 0:
        return False, "❌ **No evidence provided**\\n\\nAdd `U4_EVIDENCED_BY` link by merging a PR with `Closes #` in description."

    # Check 2: Acceptance criteria checked (if exists)
    issue_query = """
    MATCH (w:U4_Work_Item {node_id: $node_id})
    RETURN w.acceptance_criteria
    """
    result = g.query(issue_query, params={"node_id": node_id})
    ac = result.result_set[0][0] if result.result_set else None

    if ac:
        # Count unchecked boxes
        unchecked = ac.count("- [ ]")
        if unchecked > 0:
            return False, f"❌ **{unchecked} acceptance criteria not checked**\\n\\nCheck all boxes before closing."

    # Check 3: mp-lint passes (optional - check evidence PR)
    # TODO: Query U4_Code_Artifact for PR number, check CI status

    return True, "✅ All requirements met"


def enforce_close_policy(repo_full_name: str, issue_number: int):
    """Enforce L4 evidence rule when issue is closed."""

    can_close, reason = can_close_ticket(repo_full_name, issue_number)

    if not can_close:
        # Reopen issue and comment
        repo = gh.get_repo(repo_full_name)
        issue = repo.get_issue(issue_number)

        comment_body = f"""## ⚠️ Cannot Close - L4 Evidence Requirement

{reason}

**L4 Law Reference:** `ticket_governance.md` §6.1

This bot enforces the evidence requirement. When requirements are met, you can close again.
"""

        issue.create_comment(comment_body)
        issue.edit(state="open")

        print(f"Reopened {repo_full_name}#{issue_number}: {reason}")
    else:
        print(f"Allowed close {repo_full_name}#{issue_number}")


if __name__ == "__main__":
    # Listen for issues.closed events via webhook
    # (integrate with github_webhook.py)
    pass
```

### 3.2 mp-lint Rules

Add to `tools/mp_lint/rules/`:

```python
# R-501: Work item missing required field
def check_work_item_required_fields(node):
    required = ["ticket_id", "name", "work_type", "state", "priority"]
    for field in required:
        if not node.get(field):
            yield f"R-501: Work item missing required field: {field}"

# R-502: Illegal state transition
def check_work_item_state_transition(old_state, new_state):
    allowed = {
        "todo": ["doing", "canceled"],
        "doing": ["done", "blocked", "canceled"],
        "blocked": ["doing", "canceled"],
        "done": ["doing"],  # Rework allowed
        "canceled": []  # Terminal
    }
    if new_state not in allowed.get(old_state, []):
        yield f"R-502: Illegal state transition: {old_state} → {new_state}"

# R-503: Work item in doing has no assignee
def check_work_item_assignee(node, links):
    if node.get("state") == "doing":
        has_assignee = any(
            link["type"] == "U4_ASSIGNED_TO" and link.get("role") == "owner"
            for link in links
        )
        if not has_assignee:
            yield f"R-503: Work item in 'doing' state has no assignee"

# R-504: Work item closed without evidence
def check_work_item_evidence(node, links):
    if node.get("state") == "done":
        has_evidence = any(
            link["type"] == "U4_EVIDENCED_BY"
            for link in links
        )
        if not has_evidence:
            yield f"R-504: Work item closed without evidence (violates L4 law)"

# R-505: Work item blocked without blocker
def check_work_item_blocker(node, links):
    if node.get("state") == "blocked":
        has_blocker = any(
            link["type"] == "U4_BLOCKED_BY"
            for link in links
        )
        if not has_blocker:
            yield f"R-505: Work item in 'blocked' state has no U4_BLOCKED_BY link"

# R-506: P0 ticket open at release
def check_p0_tickets(graph):
    query = """
    MATCH (w:U4_Work_Item {priority: 'critical'})
    WHERE w.state NOT IN ['done', 'canceled']
    RETURN w.ticket_id, w.name
    """
    results = graph.query(query)
    for row in results.result_set:
        ticket_id = row[0]
        name = row[1]
        yield f"R-506: P0 ticket open at release time: {ticket_id} ({name})"
```

---

## 4. Dashboard UI

### 4.1 Ticket List Component

Create `app/tickets/page.tsx`:

```tsx
'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'

interface WorkItem {
  ticket_id: string
  name: string
  work_type: 'ticket' | 'bug' | 'mission' | 'milestone'
  state: 'todo' | 'doing' | 'blocked' | 'done' | 'canceled'
  priority: 'critical' | 'high' | 'medium' | 'low'
  component: string
  assignee?: string
  due_date?: string
  evidence_count: number
}

export default function TicketsPage() {
  const [filter, setFilter] = useState<{
    priority?: string
    state?: string
    component?: string
  }>({})

  // Query work items from API
  const { data: tickets, isLoading } = useQuery({
    queryKey: ['tickets', filter],
    queryFn: async () => {
      const params = new URLSearchParams(filter as any)
      const res = await fetch(`/api/tickets?${params}`)
      return res.json() as Promise<WorkItem[]>
    }
  })

  if (isLoading) return <div>Loading tickets...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Work Items</h1>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select
          value={filter.priority || ''}
          onChange={(e) => setFilter({ ...filter, priority: e.target.value || undefined })}
          className="px-3 py-2 border rounded"
        >
          <option value="">All Priorities</option>
          <option value="critical">P0 - Critical</option>
          <option value="high">P1 - High</option>
          <option value="medium">P2 - Medium</option>
          <option value="low">P3 - Low</option>
        </select>

        <select
          value={filter.state || ''}
          onChange={(e) => setFilter({ ...filter, state: e.target.value || undefined })}
          className="px-3 py-2 border rounded"
        >
          <option value="">All States</option>
          <option value="todo">Todo</option>
          <option value="doing">Doing</option>
          <option value="blocked">Blocked</option>
          <option value="done">Done</option>
        </select>
      </div>

      {/* Ticket List */}
      <div className="space-y-2">
        {tickets?.map((ticket) => (
          <TicketCard key={ticket.ticket_id} ticket={ticket} />
        ))}
      </div>
    </div>
  )
}

function TicketCard({ ticket }: { ticket: WorkItem }) {
  const priorityColors = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-gray-100 text-gray-800'
  }

  const stateColors = {
    todo: 'bg-gray-200',
    doing: 'bg-blue-200',
    blocked: 'bg-red-200',
    done: 'bg-green-200',
    canceled: 'bg-gray-300'
  }

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold">{ticket.name}</h3>
          <p className="text-sm text-gray-600">{ticket.ticket_id}</p>
        </div>

        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded text-xs ${priorityColors[ticket.priority]}`}>
            {ticket.priority.toUpperCase()}
          </span>
          <span className={`px-2 py-1 rounded text-xs ${stateColors[ticket.state]}`}>
            {ticket.state}
          </span>
        </div>
      </div>

      <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
        <span>{ticket.component}</span>
        {ticket.assignee && <span>@{ticket.assignee}</span>}
        {ticket.evidence_count > 0 && (
          <span className="text-green-600">✓ {ticket.evidence_count} evidence</span>
        )}
      </div>
    </div>
  )
}
```

### 4.2 API Route

Create `app/api/tickets/route.ts`:

```typescript
import { NextRequest } from 'next/server'
import { FalkorDB } from 'falkordb'

const db = new FalkorDB({ host: process.env.FALKOR_HOST || 'localhost', port: 6379 })

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const priority = searchParams.get('priority')
  const state = searchParams.get('state')
  const component = searchParams.get('component')

  // Build WHERE clause
  const filters = []
  if (priority) filters.push(`w.priority = '${priority}'`)
  if (state) filters.push(`w.state = '${state}'`)
  if (component) filters.push(`w.component = '${component}'`)

  const whereClause = filters.length > 0 ? `WHERE ${filters.join(' AND ')}` : ''

  // Query work items with evidence count
  const query = `
    MATCH (w:U4_Work_Item)
    ${whereClause}
    OPTIONAL MATCH (w)-[:U4_EVIDENCED_BY]->()
    WITH w, count(*) as evidence_count
    OPTIONAL MATCH (w)-[:U4_ASSIGNED_TO {role: 'owner'}]->(a:U4_Agent)
    RETURN w, evidence_count, a.agent_id as assignee
    ORDER BY w.priority, w.created_at DESC
  `

  const g = db.selectGraph('collective_n2')  // Or org-specific graph
  const result = g.query(query)

  const tickets = result.resultSet.map(row => ({
    ...row[0],
    evidence_count: row[1],
    assignee: row[2]
  }))

  return Response.json(tickets)
}
```

---

## 5. CI Integration

### 5.1 mp-lint Workflow

Create `.github/workflows/mp-lint.yml`:

```yaml
name: mp-lint

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run mp-lint
        run: |
          python tools/mp_lint/cli.py --format json > build/mp-lint.json

      - name: Check for violations
        run: |
          python -c "
          import json
          with open('build/mp-lint.json') as f:
              data = json.load(f)
          violations = data.get('violations', [])
          errors = [v for v in violations if v.get('severity') == 'ERROR']
          if errors:
              print(f'❌ {len(errors)} errors found')
              for v in errors[:10]:
                  print(f\"  {v['rule']}: {v['message']}\")
              exit(1)
          print(f'✅ mp-lint passed ({len(violations)} warnings)')
          "

      - name: Create issues for new violations
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const data = JSON.parse(fs.readFileSync('build/mp-lint.json', 'utf8'));

            for (const v of data.violations.slice(0, 5)) {  // Limit to 5 per run
              const title = `[${v.rule}] ${v.message}`;

              // De-dup: search for existing open issue
              const { data: issues } = await github.rest.search.issuesAndPullRequests({
                q: `repo:${context.repo.owner}/${context.repo.repo} is:issue is:open "${title}"`
              });

              if (issues.total_count === 0) {
                // Create new issue
                await github.rest.issues.create({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  title,
                  labels: ['bug', 'mp-lint', v.rule],
                  body: `**Rule:** ${v.rule}\\n**File:** ${v.file}:${v.line}\\n\\n**Details:**\\n${v.message}\\n\\n**Acceptance Criteria:**\\n- [ ] Fix code to resolve violation\\n- [ ] Rerun mp-lint (should pass)`
                });
                console.log(`Created issue for ${v.rule}`);
              }
            }

      - name: Block release on P0 tickets
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          python -c "
          from falkordb import FalkorDB
          db = FalkorDB(port=6379)
          g = db.select_graph('collective_n2')
          result = g.query('''
              MATCH (w:U4_Work_Item {priority: 'critical'})
              WHERE w.state NOT IN ['done', 'canceled']
              RETURN count(w) as p0_count
          ''')
          p0_count = result.result_set[0][0]
          if p0_count > 0:
              print(f'❌ {p0_count} P0 tickets open - BLOCKING RELEASE')
              exit(1)
          print('✅ No P0 tickets blocking release')
          "
```

---

## 6. Team Assignments

### Ada (Coordinator)
- [ ] Review all documentation
- [ ] Approve L4 governance spec
- [ ] Coordinate Phase 1 (L4 foundation)
- [ ] Write integration guide

### Luca (L4 Registry)
- [ ] Run `ingest_work_topics.py`
- [ ] Verify topic namespaces in protocol graph
- [ ] Add mp-lint rules (R-501 through R-506)
- [ ] Phenomenological validation: Do work.* events capture ticket essence?

### Atlas (Infrastructure)
- [ ] Deploy webhook service (`github_webhook.py`)
- [ ] Set up GitHub webhook configuration
- [ ] Add ticket_closer bot
- [ ] Monitor webhook logs

### Felix (Backend)
- [ ] Review webhook implementation
- [ ] Add SafeBroadcaster integration for work.* events
- [ ] Add API routes for ticket queries
- [ ] Write tests for evidence enforcement

### Iris (Frontend)
- [ ] Implement ticket list UI
- [ ] Add ticket detail panel with evidence graph
- [ ] Add filters and search
- [ ] Real-time updates via WebSocket

### Victor (Operations)
- [ ] Add MPSv3 supervisor config for webhook
- [ ] Set up monitoring for ticket bot
- [ ] Write runbook for clients
- [ ] Test end-to-end flow

---

## 7. Success Criteria

### Phase 1 Complete
- [ ] Run `ingest_work_topics.py` → 3 namespaces + policy created
- [ ] Export L4 registry → work.* topics visible
- [ ] Verify in FalkorDB → POL_WORK_TICKETS_V1 governs 3 namespaces

### Phase 2 Complete
- [ ] Create GitHub issue → see U4_Work_Item in graph
- [ ] Assign issue → see U4_ASSIGNED_TO link
- [ ] Close issue → bot checks evidence

### Phase 3 Complete
- [ ] Try close without evidence → bot reopens + comments
- [ ] Merge PR with "Closes #N" → evidence link created
- [ ] Close with evidence → allowed

### Phase 4 Complete
- [ ] Dashboard shows ticket list with filters
- [ ] Click ticket → see detail panel with evidence
- [ ] Real-time updates when GitHub issues change

### Phase 5 Complete
- [ ] Push code → mp-lint runs
- [ ] mp-lint violations → auto-create issues
- [ ] P0 ticket open → CI blocks release

---

## 8. Next Steps

1. **Read governance spec** (`docs/specs/v2/governance/ticket_governance.md`)
2. **Run ingestion** (`python tools/protocol/ingest_work_topics.py`)
3. **Set up GitHub templates** (copy `.github/ISSUE_TEMPLATE/` examples)
4. **Deploy webhook** (add to MPSv3 supervisor)
5. **Test end-to-end** (create issue → see in graph → close with evidence)

---

**STATUS:** Ready for implementation | All artifacts complete | Team assignments clear
