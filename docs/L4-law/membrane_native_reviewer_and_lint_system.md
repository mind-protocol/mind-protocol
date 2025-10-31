# Membrane‑Native Reviewer & Lint System (Org‑Scoped, Protocol‑Aware)

**Version:** 1.0 (2025‑10‑31)
**Authors:** Ada (architect & coordinator) with Atlas, Felix, Iris, Victor, Luca
**Scope:** All orgs hosted in the ecosystem. Protocol lane coverage for protocol artifacts.
**Status:** Design approved; Quality & Fallback linters implemented in `mp-lint`; file watcher + mandate wiring in progress.

---

## 0) Context & Goal

We observed repeated regressions (hardcoded values, silent fallbacks, "temporary" stubs) that made citizens appear "dumb" and the dashboard empty. We need a **membrane‑first** system that:

* Gives **sub‑second feedback** while coding (file watcher).
* **Enforces org law** at merge time (reviewer verdict), with visible policy and debt.
* Supports **protocol‑level mandates** without centralizing compute or cost.
* **Fails loudly**: no silent fallbacks—errors must become structured events.

This spec defines the events, components, rules, and runbooks to achieve that across **all orgs** in the ecosystem.

---

## 1) Design Principles

1. **Membrane‑first.** No side‑channel scripts deciding fate. All actions are `inject`/`broadcast` events with L4 governance.
2. **Law at the boundary, physics inside.** L4 governs transport/signature; L2 (org‑law) decides meaning/strictness.
3. **Local cost for local change.** Protocol issues mandates; **org executes and pays** via BudgetAccount.
4. **Tight feedback loops.** File watcher runs linters immediately; the same adapters run in CI and on mandates.
5. **Explainability.** Findings/verdicts/overrides are first‑class events with evidence and expiry. Debt is visible.
6. **Fail loudly.** Catches must either rethrow or **emit a failure event**; silent defaults are forbidden.
7. **Idempotence & backpressure.** Debounce, chunk, and cache to prevent storms and lost snapshots.

---

## 2) System Overview

**Two entry lanes; one reviewer:**

* **Local/CI (Org scope):** File watcher detects edits → emits `code.diff.emit` and `review.request` → adapters (mp‑lint) emit `lint.findings.emit` → Reviewer applies **Org_Policy** → `review.verdict` → CI gates merge.
* **Protocol mandates:** Protocol emits `review.mandate` to affected org(s) → org reserves budget → emits local `review.request` → adapters → `review.verdict` → org reports `protocol/mandate.result` upstream.

**Key components:**

* **File Watcher (org):** per‑repo daemon producing diffs with debounce/batch.
* **Adapters:** `adapter.lint.python` (mp‑lint), `adapter.lint.eslint`, `adapter.secretscan`, `adapter.depgraph`.
* **Reviewer (org):** aggregates findings; applies Org_Policy; issues verdict; manages overrides.
* **Mandate Router (protocol/ecosystem):** detects protocol/policy changes or alerts and issues `review.mandate`.
* **Economy:** Budget reservation and chargeback on org accounts.
* **Dashboard:** LintPanel + Mandates view; health/compliance overlays.

---

## 3) Event Model & Namespaces (L4)

### 3.1 Org review lane

* `ecosystem/{eco}/org/{org}/watcher.local.change` *(inject)*
* `ecosystem/{eco}/org/{org}/code.diff.emit` *(inject)*
* `ecosystem/{eco}/org/{org}/review.request` *(inject)*
* `ecosystem/{eco}/org/{org}/lint.findings.emit` *(broadcast)*
* `ecosystem/{eco}/org/{org}/review.verdict` *(broadcast)*
* `ecosystem/{eco}/org/{org}/review.override.request` *(inject)*
* `ecosystem/{eco}/org/{org}/review.override.granted|denied` *(broadcast)*
* `ecosystem/{eco}/org/{org}/failure.emit` *(broadcast, **Fail‑Loud** requirement)*

### 3.2 Protocol mandate lane

* `ecosystem/{eco}/protocol/review.mandate` *(inject, downstream order)*
* `ecosystem/{eco}/protocol/mandate.ack` *(inject, org→protocol)*
* `ecosystem/{eco}/protocol/mandate.result` *(broadcast, org→protocol)*
* `ecosystem/{eco}/protocol/mandate.breach` *(broadcast, protocol→org)*

### 3.3 Economy (org scope)

* `ecosystem/{eco}/org/{org}/economy.quote.request` *(inject)*
* `ecosystem/{eco}/org/{org}/economy.quote.response` *(broadcast)*
* `ecosystem/{eco}/org/{org}/budget.checked|budget.clamped` *(broadcast)*

**Governance (typical caps):**
`watcher.local.change` 64KB, 240/min; `code.diff.emit` 512KB, 60/min; `lint.findings.emit` 1MB, 60/min; `failure.emit` 32KB, 120/min; signatures `ed25519`, allowed emitters: `adapter.*`, `reviewer.*`, `ci.*`.

---

## 4) Rule Series (mp‑lint)

* **R‑001 … R‑005:** L4 Protocol Compliance (envelope, signatures, namespace)
* **R‑100 … R‑102:** Hardcoded Values (ban hardcoded anything)
* **R‑200 … R‑202:** Quality Degradation ★ NEW

  * R‑200 `TODO_OR_HACK` – TODO/HACK/FIXME in logic paths
  * R‑201 `QUALITY_DEGRADE` – disabled validation, absurd timeouts, retries/backoff zero
  * R‑202 `OBSERVABILITY_CUT` – `print()` instead of logger in app code
* **R‑300 … R‑303:** Fallback Antipatterns ★ NEW

  * R‑300 `BARE_EXCEPT_PASS` – silent except/pass
  * R‑301 `SILENT_DEFAULT_RETURN` – default return on exception
  * R‑302 `FAKE_AVAILABILITY` – unconditional `return True`
  * R‑303 `INFINITE_LOOP_NO_SLEEP` – `while True` without sleep/backoff
* **R‑400 … R‑401:** Fail Loudly ★ NEW requirement

  * R‑400 `FAIL_LOUD_REQUIRED` – catch chooses non‑exception path **without** emitting `failure.emit` (forbidden)
  * R‑401 `MISSING_FAILURE_CONTEXT` – `failure.emit` sent without `change_id`, `code_location`, or `severity`

**Pragmas (must include reason & expiry):**
`# lint: allow-degrade(reason="… until 2025‑11‑05, ticket #1234")`
`# lint: allow-fallback(reason="…", until="2025‑11‑05")`

All findings are emitted via `lint.findings.emit` with `{policy, severity, file, span, message, suggestion}`.

---

## 5) Mechanisms

### 5.1 File Watcher (Org)

* Detects edits; debounces 250–400ms; batches 2s; ignores vendor/build dirs.
* Builds minimal diffs (hunks + hashes) → emits `code.diff.emit` and `review.request(origin:"watcher")`.
* Backpressure: on bus errors, exponential backoff; emits `failure.emit` with code_location and reason.

### 5.2 Adapters (Linters & Scanners)

* **`adapter.lint.python`** – wraps `mp-lint` (R‑100/200/300/400).
* **`adapter.lint.eslint`** – FE rules.
* **`adapter.secretscan`** – secrets/IDs/DSNs.
* **`adapter.depgraph`** – dependency drift & vuln checks.
* Input: `code.diff.emit`. Output: `lint.findings.emit` (streaming). Must **not** exit silently—on exceptions, emit `failure.emit` and rethrow.

### 5.3 Reviewer (Org)

* Subscribes to `lint.findings.emit` and `review.request`.
* Reads **Org_Policy** (L2) and computes `review.verdict(pass|soft_fail|hard_fail)` with scores per policy.
* Handles `review.override.request` (reason, ticket, expiry); emits `review.override.granted|denied`.
* On internal error, emits `failure.emit` and sets verdict `hard_fail` (Fail‑Loud).

### 5.4 Protocol Mandates (L3/L4 → L2)

* Protocol emits `protocol/review.mandate` with `{cause, scope, policy_set, sla_seconds, billing}`.
* Org acknowledges (`mandate.ack`), reserves budget, runs local `review.request`, reports `mandate.result` upstream.
* Missed SLA or refusal triggers `mandate.breach` and permeability/governance consequences.

### 5.5 Economy & Chargeback

* Org requests a quote; reserves budget; debit added to BudgetAccount on `mandate.result`.
* Emits `budget.checked|budget.clamped` for visibility; dashboard shows "cost of review".

### 5.6 Fail Loudly (Runtime Contract)

Any **catch** that does not re‑raise MUST emit:

```json
{ "type":"failure.emit",
  "content": {
    "change_id": "...", "code_location": "path:line",
    "exception": "ValueError: ...",
    "severity": "warn|error|fatal",
    "suggestion": "…",
    "trace_id": "…" } }
```

Linters enforce R‑400/401 at compile time; runtime enforces via Reviewer health.

---

## 6) Data Models (Event Content)

### 6.1 `code.diff.emit`

```json
{
  "change_id": "local:1730395023|gh:org/repo#123",
  "files": [{
    "path": "orchestration/.../graph_store.py",
    "sha_before": "…", "sha_after": "…",
    "hunks": [{"start": 120, "end": 138, "add": "+ …", "del": "- …"}]
  }]
}
```

### 6.2 `lint.findings.emit`

```json
{
  "change_id": "…",
  "findings": [{
    "policy": "hardcoded_anything|fallback_antipattern|quality_degradation|fail_loud",
    "rule": "R-300|R-301|R-400",
    "severity": "low|medium|high|critical",
    "file": "…", "span": {"start_line": 78, "end_line": 85},
    "message": "Hardcoded citizen list",
    "suggestion": "Use get_all_citizen_ids()",
    "evidence": "['felix','ada',…]"
  }]
}
```

### 6.3 `review.verdict`

```json
{
  "change_id": "…",
  "result": "pass|soft_fail|hard_fail",
  "scores": {"hardcoded_anything": 3, "fallback_antipattern": 1},
  "required": {"override": false, "fields": []}
}
```

### 6.4 `review.mandate`

```json
{
  "mandate_id": "proto-2025-10-31-001",
  "cause": "protocol.update|policy.update|risk.alert|periodic",
  "scope": {"repo": "…", "paths": ["…"], "commit": "…", "protocol_artifacts": ["Event_Schema:…"]},
  "policy_set": "org:current|protocol:current|{id,rev}",
  "sla_seconds": 1800,
  "billing": {"charge_to": "org:{org_id}", "estimate_deltaE": 42}
}
```

### 6.5 `failure.emit`

```json
{
  "change_id": "… (optional)",
  "code_location": "file.py:2832",
  "exception": "Exception: …",
  "severity": "warn|error|fatal",
  "suggestion": "…",
  "trace_id": "uuid…"
}
```

---

## 7) L4 Graph Additions (Nodes & Links)

Create **Event_Schema** nodes for each topic above with fields: `name`, `version`, `direction`, `topic_pattern`, `schema_uri`, `description`.

Namespaces:

* `ecosystem/{eco}/org/{org}/review/*`, `…/lint/*`, `…/watcher/*`, `…/economy/*`
* `ecosystem/{eco}/protocol/review/*`

Governance:

* Attach `Governance_Policy` nodes to each namespace: payload caps, rate limits, signature required, allowed emitters (`adapter.*`, `reviewer.*`, `ci.*`, `protocol.watcher`).
* Edges: `(:Event_Schema)-[:IN_NAMESPACE]->(:Topic_Namespace)`; `(:Topic_Namespace)-[:GOVERNED_BY]->(:Governance_Policy)`; `(:Tool)-[:ALLOWED_TO_EMIT]->(:Event_Schema)`.

Policy storage (L2 Org graph & Protocol graph):

* `(:Org_Policy {name,severity,pattern,allowed_paths,suppression,expiry_max_days})`
* `(:Protocol_Policy {…})`
* `(:Reviewer)-[:APPLIES]->(:Org_Policy)`

---

## 8) Verification & SLOs

**Unit:**

* mp‑lint scanners (R‑100/200/300/400) with fixtures; pragma parsing; JSON output.

**Integration:**

* File change → `code.diff.emit` → `lint.findings.emit` → `review.verdict` within **≤ 1.0s** (dev).
* Mandate → org review → `mandate.result` within **SLA** (e.g., 30 min).

**E2E acceptance:**

* Save a file with a forbidden literal → finding surfaces on dashboard in **≤ 1.0s**.
* Fix line → verdict flips to **pass** in **≤ 1.0s**.
* Protocol updates a schema → mandate hits owning orgs; results reported with debits.

**Operational SLOs:**

* Bus `ack_rate ≥ 0.99`; `reject_rate ≤ 2%`.
* Watcher debounce correctness (no storms).
* Reviewer uptime ≥ 99%.
* **Fail‑Loud coverage:** 100% of caught exceptions either rethrow or emit `failure.emit`.

**Runbook:**

* If no nodes appear on the dashboard: check `protocol/ws_not_ready`, `failure.emit`, `lint.findings.emit` counts; verify snapshot replay on connect; confirm org Reviewer is alive; ensure mandate queue empty or within SLA.

---

## 9) Implementation Plan & Assignees

### Milestone A — File Watcher Loop (today → +2 days)

**Atlas (owner)**

* `orchestration/adapters/watchers/file_watcher.py` (debounce/batch/ignore; emits `code.diff.emit`, `review.request`).
* `orchestration/adapters/watchers/normalize_diff.py`.
* Ingest missing L4 schemas for watcher/review/lint/failure.
* Add truthful `is_available()` and snapshot replay on WS connect.
  **Acceptance:** save → `lint.findings.emit` in ≤1s; dashboard shows finding.

**Felix**

* `adapter.lint.python` wrapping `mp-lint` (R‑100/200/300/400).
* Ensure adapters emit `failure.emit` on internal error.
  **Acceptance:** JSON findings for seeded violations; R‑400 fires when catch lacks `failure.emit`.

**Iris**

* `LintPanel.tsx` subscribing to `…/lint.findings.emit` and `review.verdict`.
  **Acceptance:** inline file/spans UI; status chips (pass/soft/hard).

**Victor**

* Pre‑commit + CI: `tools/mp-lint --check-all`; watcher in CI.
  **Acceptance:** CI fails on any R‑* violation; artifacts include JSON findings.

**Ada**

* Seed **Org_Policy** for all orgs; specify severity & override rules.
  **Acceptance:** Reviewer applies policy and produces consistent verdicts.

### Milestone B — Protocol Mandates (next +3 days)

**Atlas**

* `protocol_watcher.py` → emits `protocol/review.mandate`; router by ownership registry.
* Budget events wiring; `mandate.result` & `mandate.breach` schemas.
  **Acceptance:** protocol change triggers mandates to two orgs; both report result.

**Felix**

* Reviewer supports `policy_set: "protocol:current"` and mixed scopes.

**Iris**

* Mandates dashboard: cards with cause, SLA countdown, cost, verdict.

**Victor**

* CI blocks promotion if open mandate unresolved.

### Milestone C — Debt Visibility & Health (next +2 days)

**Atlas**

* `health.compliance.snapshot` augmentation (counts of R‑* by org; fail‑loud coverage).

**Iris**

* Debt graph; overrides aging view.

**Ada**

* Narrative docs; training notes.

---

## 10) Appendix — CLI & Examples

**Run all checks locally:**
`python3 tools/mp-lint --check-all orchestration/ app/`

**Emit manual review for a path batch:**
`bus.inject('review.request', {change_id:'manual-…', diff:{files:[…]}, policies:'org:current'})`

**Pragma examples:**
`# lint: allow-fallback(reason="stub for X, remove by 2025‑11‑10")`

---

## 11) Non‑Goals

* Replacing unit tests. Linters catch classes of risk; behavior is verified by tests.
* Centralizing policy at L4. Meaning stays in org‑law / protocol‑law.

---

**End of Spec**
