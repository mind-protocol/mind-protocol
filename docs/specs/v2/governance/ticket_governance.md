# Ticket Governance Specification (L4)

**Version:** 1.0.0
**Status:** Active
**Scope:** Protocol-level law (L4)
**Applies to:** All work items across L1-L3
**Author:** Ada Bridgekeeper
**Date:** 2025-10-31

---

## 0. Purpose

This document establishes **protocol-level governance** for work item management across the Mind Protocol ecosystem. It defines:

- **ID format** and canonical addressing
- **Lifecycle states** and allowed transitions
- **Priority/Severity** standards and deployment gates
- **Required metadata** for tickets, bugs, missions, and milestones
- **Evidence requirements** for closing work items
- **Event schemas** and topic namespaces for work item telemetry

**What lives at L4 (this document):**
- The rules, standards, and policies
- Event schema mappings and governance policies
- Conformance requirements

**What lives at L2/L3 (organizational graphs):**
- Actual work items as `U4_Work_Item` nodes
- Assignment, blocking, and evidence relationships
- Org-specific workflows and tooling

---

## 1. Work Item Types

Work items are represented as `U4_Work_Item` nodes with `work_type` field:

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `ticket` | Standard work item with problem + remediation | Feature implementation, refactoring |
| `bug` | Defect requiring fix | R-301 violation, crash on input |
| `mission` | Multi-part objective with milestones | "Implement L4 registry", "Launch MVP" |
| `milestone` | Completion marker with dependencies | "Phase 1 complete", "Q1 delivery" |

All types share the same base schema and governance rules.

---

## 2. ID Format and Canonical Addressing

### 2.1 Ticket ID

**Canonical format:** `ticket_id = "gh:<org>/<repo>#<number>"`

**Examples:**
- `gh:mind-protocol/mindprotocol#123`
- `gh:acme-corp/internal-tools#456`

**Properties:**
- **Globally unique** across GitHub
- **Stable** - never changes even if title changes
- **Resolvable** - can be converted to URL: `https://github.com/<org>/<repo>/issues/<number>`

### 2.2 Short Code (Optional)

For human communication, tickets may use **short codes** in titles:

**Format:** `[<prefix>-<number>]`

**Examples:**
- `[L4-123] Implement R-400 scanner`
- `[CODEX-001] Fix R-301 violations in cc_prune`
- `[INFRA-045] Add hash-anchored validator cache`

**Properties:**
- Prefix indicates component or stream
- Number is sequential within prefix
- Not required, but helps with verbal communication

### 2.3 Graph Node ID

Work items in FalkorDB use `node_id` derived from `ticket_id`:

**Format:** `wi:<org>/<repo>#<number>`

**Example:**
```cypher
CREATE (:U4_Work_Item {
  node_id: "wi:mind-protocol/mindprotocol#123",
  ticket_id: "gh:mind-protocol/mindprotocol#123",
  name: "[L4-123] Implement R-400 scanner",
  work_type: "ticket",
  ...
})
```

---

## 3. Lifecycle States and Transitions

### 3.1 States

| State | Description | Entry Condition | Exit Condition |
|-------|-------------|-----------------|----------------|
| `todo` | Work not started | Created or unblocked | Assigned + work begins |
| `doing` | Actively being worked | Assignee starts work | Complete or blocked |
| `blocked` | Progress stopped by dependency | Blocker identified | Blocker resolved |
| `done` | Complete and evidence provided | AC met + evidence linked | Reopened if issues found |
| `canceled` | Work abandoned | Decision to not pursue | - |

### 3.2 Allowed Transitions

```
todo → doing → done
  ↓      ↓       ↑
  ↓    blocked   ↑
  ↓      ↓       ↑
  └→ canceled    ↑
          ↑──────┘
```

**Illegal transitions:**
- `todo → done` (must go through `doing`)
- `blocked → done` (must resolve to `doing` first)
- `canceled → doing` (create new ticket instead)
- `done → todo` (use `doing` for rework)

### 3.3 Event Emissions

Every state transition emits a telemetry event:

| Transition | Event Topic | Schema |
|------------|-------------|---------|
| create → `todo` | `work.ticket.opened` | `telemetry.lifecycle@1.0.0` |
| `todo` → `doing` | `work.ticket.updated` | `telemetry.state@1.0.0` |
| `doing` → `blocked` | `work.ticket.updated` | `telemetry.state@1.0.0` |
| `blocked` → `doing` | `work.ticket.updated` | `telemetry.state@1.0.0` |
| `doing` → `done` | `work.ticket.closed` | `telemetry.lifecycle@1.0.0` |
| any → `canceled` | `work.ticket.closed` | `telemetry.lifecycle@1.0.0` |

---

## 4. Priority and Severity Standards

### 4.1 Priority Levels

| Priority | Name | SLA | Deployment Gate | Example |
|----------|------|-----|-----------------|---------|
| `P0` | Critical | 24h | BLOCKS release | Production crash, data loss |
| `P1` | High | 3 days | WARNS on release | R-400 violation, broken tests |
| `P2` | Medium | 2 weeks | No gate | R-100 magic numbers, refactoring |
| `P3` | Low | Best effort | No gate | Nice-to-have, tech debt |

### 4.2 Severity Levels (for bugs)

| Severity | Description | Example |
|----------|-------------|---------|
| `absolute` | No workaround, complete failure | Database corruption, security breach |
| `high` | Major impact, workaround exists | Silent fallback (R-301), memory leak |
| `medium` | Moderate impact | UI glitch, slow performance |
| `low` | Minor impact | Typo, missing log message |

### 4.3 Deployment Gates

**Rule:** No release may proceed if open tickets exist with:
- `priority = P0` (any state except `done` or `canceled`)
- `priority = P1` AND `component = "L4 Protocol"` (law violations block releases)

**Enforcement:** CI checks before merge to `main`:
```bash
# Count blocking tickets
query = "MATCH (w:U4_Work_Item) WHERE w.priority = 'P0' AND w.state NOT IN ['done','canceled'] RETURN count(w)"
if count > 0: FAIL CI with message "P0 tickets must be resolved"
```

---

## 5. Required Metadata

### 5.1 Mandatory Fields

All work items MUST have:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `ticket_id` | string | Canonical GitHub ID | `gh:mind-protocol/mindprotocol#123` |
| `name` | string | Title (may include short code) | `[L4-123] Implement R-400 scanner` |
| `work_type` | enum | `ticket\|bug\|mission\|milestone` | `ticket` |
| `state` | enum | Current lifecycle state | `doing` |
| `priority` | enum | `critical\|high\|medium\|low` | `high` |
| `level` | enum | L1/L2/L3/L4 | `L2` |
| `scope_ref` | string | Org/citizen ID | `mind-protocol` |
| `component` | string | System area | `L4 Protocol / Event Registry` |

### 5.2 Recommended Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `description` | string | Detailed problem statement | See §5.3 |
| `acceptance_criteria` | string | Checklist of completion requirements | `- [ ] Tests pass\n- [ ] Docs updated` |
| `due_date` | datetime | Target completion | `2025-11-15T00:00:00Z` |
| `estimate` | string | Time estimate | `2h`, `3 days` |

### 5.3 Description Template

For `work_type = ticket` or `bug`:

```markdown
## Problem
What is wrong or missing?

## Impact
Who/what is affected? What breaks if not fixed?

## Remediation
Steps to fix:
1. ...
2. ...
3. ...

## Acceptance Criteria
- [ ] ...
- [ ] ...
```

---

## 6. Evidence Requirements for Closing

### 6.1 The Evidence Rule

**LAW:** A work item may transition to `state = done` **ONLY IF**:

1. **At least one `U4_EVIDENCED_BY` link exists** to:
   - `U4_Code_Artifact` (merged PR, test file)
   - `U4_Knowledge_Object` (updated docs, spec)
   - `U4_Attestation` (policy compliance proof)
   - `L4_Conformance_Result` (test suite pass)

2. **mp-lint passes** on the evidence PR (no new violations introduced)

3. **Acceptance criteria met** (all checkboxes checked in description)

### 6.2 Evidence Types

| Evidence Type | Graph Link | Example |
|---------------|------------|---------|
| **Code change** | `(wi)-[:U4_EVIDENCED_BY]->(ca:U4_Code_Artifact)` | Merged PR that fixes bug |
| **Test added** | `(wi)-[:U4_EVIDENCED_BY]->(ca:U4_Code_Artifact)` | New test file verifying fix |
| **Doc updated** | `(wi)-[:U4_EVIDENCED_BY]->(ko:U4_Knowledge_Object)` | Updated spec or README |
| **Policy ref** | `(wi)-[:U4_IMPLEMENTS]->(gp:L4_Governance_Policy)` | Implements L4 law |
| **Conformance** | `(wi)-[:U4_EVIDENCED_BY]->(cr:L4_Conformance_Result)` | Test suite pass result |

### 6.3 Enforcement Mechanism

**Bot behavior on close:**

```python
def can_close_ticket(ticket: U4_Work_Item) -> tuple[bool, str]:
    # Check for evidence
    evidence = query("MATCH (wi {ticket_id: $id})-[:U4_EVIDENCED_BY]->() RETURN count(*)")
    if evidence == 0:
        return False, "No evidence provided. Add U4_EVIDENCED_BY link to PR/doc/test."

    # Check AC
    if ticket.acceptance_criteria:
        unchecked = count_unchecked_boxes(ticket.acceptance_criteria)
        if unchecked > 0:
            return False, f"{unchecked} acceptance criteria not checked."

    # Check mp-lint (if PR exists)
    pr_artifacts = query("MATCH (wi)-[:U4_EVIDENCED_BY]->(ca:U4_Code_Artifact) WHERE ca.type = 'pr' RETURN ca.pr_number")
    for pr in pr_artifacts:
        lint_status = check_mp_lint(pr)
        if not lint_status.passed:
            return False, f"mp-lint failed on PR #{pr}: {lint_status.violations}"

    return True, "All requirements met"
```

**If requirements fail:** Bot comments on issue and **reopens** it.

---

## 7. Relationships and Dependencies

### 7.1 Assignment

```cypher
(:U4_Work_Item)-[:U4_ASSIGNED_TO]->(:U4_Agent)
```

**Properties:**
- `role`: `owner` | `reviewer` | `stakeholder`
- `since`: datetime of assignment

**Rule:** A ticket MUST have at least one `U4_ASSIGNED_TO` link with `role='owner'` before transitioning to `doing`.

### 7.2 Blocking

```cypher
(:U4_Work_Item)-[:U4_BLOCKED_BY {blocking_reason, severity}]->(:U4_Work_Item | :U4_Goal | :U4_Event)
```

**Properties:**
- `blocking_reason`: string (why blocked)
- `severity`: `absolute` | `strong` | `partial`

**Rule:** A ticket in `state=blocked` MUST have at least one `U4_BLOCKED_BY` link. When all blockers resolve, auto-transition to `doing`.

### 7.3 Dependencies

```cypher
(:U4_Work_Item)-[:U4_DEPENDS_ON {criticality, dependency_type}]->(:U4_Work_Item | :U4_Code_Artifact)
```

**Properties:**
- `criticality`: `blocking` | `important` | `optional`
- `dependency_type`: `runtime` | `build_time` | `data` | `infrastructure` | `logical`

**Difference from BLOCKED_BY:**
- `DEPENDS_ON`: Structural dependency (A needs B to start)
- `BLOCKED_BY`: Active blocker (A started but can't progress)

### 7.4 Implementation

```cypher
(:U4_Work_Item)-[:U4_IMPLEMENTS]->(:L4_Governance_Policy | :L4_Event_Schema | :U4_Goal)
```

**Use case:** Ticket implements L4 law, event schema requirement, or organizational goal.

---

## 8. Event Schemas and Topic Namespaces

### 8.1 Topic Namespaces (L4)

| Namespace Pattern | Description | Governance Policy |
|-------------------|-------------|-------------------|
| `work.ticket.*` | Ticket lifecycle events | `POL_WORK_TICKETS_V1` |
| `work.bug.*` | Bug tracking events | `POL_WORK_TICKETS_V1` |
| `work.mission.*` | Mission/milestone events | `POL_WORK_TICKETS_V1` |

### 8.2 Concrete Topics

| Topic | Description | Schema | SEA Required? |
|-------|-------------|--------|---------------|
| `work.ticket.opened` | Ticket created | `telemetry.lifecycle@1.0.0` | No |
| `work.ticket.updated` | State/metadata changed | `telemetry.state@1.0.0` | No |
| `work.ticket.closed` | Ticket done/canceled | `telemetry.lifecycle@1.0.0` | No |
| `work.ticket.evidence` | Evidence link added | `telemetry.lifecycle@1.0.0` | No |
| `work.bug.*` | Same pattern for bugs | Same schemas | No |
| `work.mission.*` | Same pattern for missions | Same schemas | No |

### 8.3 Schema Mappings

**All work.* topics map to generic telemetry schemas:**

```cypher
(:L4_Topic_Namespace {name: "work.ticket.*"})-[:U4_MAPS_TO_TOPIC]->(:L4_Event_Schema {name: "telemetry.lifecycle@1.0.0"})
(:L4_Topic_Namespace {name: "work.ticket.*"})-[:U4_MAPS_TO_TOPIC]->(:L4_Event_Schema {name: "telemetry.state@1.0.0"})
```

**Governance:** `POL_WORK_TICKETS_V1`
- Signature required: Yes (`requires_sig_suite: SIG_ED25519_V1`)
- SEA required: No (operational telemetry, not identity-sensitive)
- CPS compliance: No

### 8.4 Payload Example

```json
{
  "topic": "work.ticket.updated",
  "timestamp": "2025-10-31T10:45:00Z",
  "actor_ref": "github:ada",
  "payload": {
    "ticket_id": "gh:mind-protocol/mindprotocol#123",
    "work_type": "ticket",
    "state": "doing",
    "state_previous": "todo",
    "priority": "high",
    "component": "L4 Protocol",
    "assignee": "@ada"
  },
  "signature": {
    "suite": "SIG_ED25519_V1",
    "public_key": "...",
    "signature": "..."
  }
}
```

---

## 9. Conformance and Validation

### 9.1 mp-lint Rules

**New rules for ticket governance:**

| Rule | Severity | Description |
|------|----------|-------------|
| `R-501` | ERROR | Work item missing required field (ticket_id, name, work_type, state, priority) |
| `R-502` | ERROR | Work item has illegal state transition |
| `R-503` | WARNING | Work item in `doing` has no assignee |
| `R-504` | ERROR | Work item closed without evidence (`U4_EVIDENCED_BY` link) |
| `R-505` | WARNING | Work item in `blocked` state has no `U4_BLOCKED_BY` link |
| `R-506` | ERROR | P0 ticket open at release time |

### 9.2 Runtime Validation

**Validator service:** `services/validators/ticket_validator.py`

**Checks on every `graph.delta.work_item.upsert` event:**

1. Required fields present
2. State transition is legal
3. If `state=blocked`, at least one `U4_BLOCKED_BY` exists
4. If `state=doing`, at least one `U4_ASSIGNED_TO {role='owner'}` exists
5. If `state=done`, at least one `U4_EVIDENCED_BY` exists

**On validation failure:** Emit `failure.emit` with rule code and reject graph mutation.

---

## 10. Integration Points

### 10.1 GitHub Issues → Graph

**Webhook:** `services/ingestors/github_webhook.py`

**Event mappings:**

| GitHub Event | Action | Graph Operation | Telemetry Event |
|--------------|--------|-----------------|-----------------|
| `issues.opened` | Create ticket | `CREATE (:U4_Work_Item {state: 'todo', ...})` | `work.ticket.opened` |
| `issues.assigned` | Add assignee | `MERGE ()-[:U4_ASSIGNED_TO]->(:U4_Agent)` | `work.ticket.updated` |
| `issues.labeled` | Update metadata | `SET wi.component = ...` | `work.ticket.updated` |
| `issues.closed` | Close ticket | `SET wi.state = 'done'` (validate evidence!) | `work.ticket.closed` |
| `issues.reopened` | Reopen ticket | `SET wi.state = 'doing'` | `work.ticket.updated` |
| `issue_comment` | Add comment | Optional telemetry | `work.ticket.updated` |

### 10.2 PR Merge → Evidence Link

**Webhook:** Same `github_webhook.py`

**Event:** `pull_request.closed` (with `merged: true`)

**Action:**
1. Parse PR body for `Closes #123` or `Fixes #456`
2. Create `U4_Code_Artifact` for the PR
3. Create `(:U4_Work_Item {ticket_id: 'gh:org/repo#123'})-[:U4_EVIDENCED_BY]->(artifact)`
4. Emit `work.ticket.evidence`

### 10.3 Dashboard UI

**Queries:**

```cypher
// All tickets
MATCH (w:U4_Work_Item {scope_ref: 'mind-protocol'})
WHERE w.work_type IN ['ticket', 'bug', 'mission', 'milestone']
RETURN w ORDER BY w.priority, w.due_date

// My tickets
MATCH (w:U4_Work_Item)-[:U4_ASSIGNED_TO {role: 'owner'}]->(a:U4_Agent {agent_id: $my_id})
RETURN w

// Blocked tickets
MATCH (w:U4_Work_Item {state: 'blocked'})-[b:U4_BLOCKED_BY]->(blocker)
RETURN w, b, blocker
```

**Components:**
- Ticket list (filterable by priority, state, component)
- Ticket detail panel (shows evidence links, blockers, assignees)
- Evidence graph visualization
- State transition timeline

---

## 11. Migration from Existing Systems

### 11.1 Import from GitHub Issues

**Script:** `tools/import_github_issues.py`

```python
for issue in github.get_issues(state='all'):
    # Create U4_Work_Item
    node = {
        'ticket_id': f'gh:{org}/{repo}#{issue.number}',
        'name': issue.title,
        'work_type': 'bug' if 'bug' in issue.labels else 'ticket',
        'state': 'done' if issue.state == 'closed' else 'todo',
        'priority': parse_priority(issue.labels),
        'level': 'L2',
        'scope_ref': org,
        'description': issue.body,
        'created_at': issue.created_at,
        'updated_at': issue.updated_at
    }
    create_work_item(node)

    # Link to PR if closed by PR
    if issue.pull_request and issue.pull_request.merged:
        link_evidence(issue.number, issue.pull_request.number)
```

### 11.2 Import from Jira

Similar pattern - map Jira fields to `U4_Work_Item` schema, preserve original ID as `external_id` property.

---

## 12. Governance Policy Reference

**Policy ID:** `POL_WORK_TICKETS_V1`

**Governs:** All `work.*` topic namespaces

**Requirements:**
- Events MUST be signed (SIG_ED25519_V1)
- Events do NOT require SEA (operational telemetry)
- Payload MUST conform to `telemetry.lifecycle` or `telemetry.state` schemas
- State transitions MUST be legal per §3.2
- Closed tickets MUST have evidence per §6.1

**Enforcement:** Runtime validator + mp-lint + GitHub bot

---

## 13. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-31 | Ada | Initial specification |

---

## 14. References

- **Universal Schema:** `U4_Work_Item` in `docs/COMPLETE_TYPE_REFERENCE.md`
- **Telemetry Schemas:** `telemetry.lifecycle@1.0.0`, `telemetry.state@1.0.0`
- **mp-lint Rules:** R-501 through R-506 (this document)
- **Webhook Implementation:** `services/ingestors/github_webhook.py`
- **L4 Registry:** `build/l4_public_registry.json`

---

**STATUS:** Active - Ready for implementation
**Next:** Seed topic namespaces + create webhook service + add GitHub templates
