# L4 Integration — Ticket Matrix & Action Plan

**Generated:** 2025-10-31 18:30 UTC
**Status:** L4-002 Complete, 6 Ready (incl. reviewer system), 12 Todo
**Source:** SYNC.md + Nicolas's consolidated checklist + Membrane-Native Reviewer Spec

---

## Quick Status

| Status | Count | Items |
|--------|-------|-------|
| ✅ Done | 1 | L4-002 |
| 🟡 Ready | 6 | L4-001, L4-007, L4-009, L4-013, L4-018, L4-022 |
| 🔴 Todo | 12 | L4-003, L4-004, L4-005, L4-006, L4-008, L4-010, L4-011, L4-012, L4-014, L4-019, L4-020, L4-021 |
| ⏳ Later | 3 | L4-015, L4-016, L4-017 |

---

## BLOCKING Items (Do First)

### L4-001: Add consciousness telemetry schemas (Hybrid C) 🟡 Ready
- **Owner:** Luca + Ada
- **Estimate:** 2 hours
- **Script:** `tools/protocol/ingest_telemetry_policies.py` (ready to run)
- **What:** 5 generic Event_Schema + 6 wildcard namespaces + 2 policies
  - STRICT: `telemetry.state.*`, `telemetry.detection.*` (SEA required)
  - FLEX: `telemetry.series.*`, `telemetry.lifecycle.*`, `telemetry.activation.*`, `telemetry.frame.*` (signed only)
- **AC:** mp-lint R-001≈0; only R-005 on STRICT topics without attestation; SafeBroadcaster emits cleanly

**Next Steps for Luca:**
```bash
python tools/protocol/ingest_telemetry_policies.py
python tools/protocol/export_l4_public.py
# Verify: Event_Schema count should be 47 + 5 = 52
```

---

### L4-002: Register engine schemas ✅ Done
- **Owner:** Luca
- **Status:** Complete (this session)
- **What:** Added `graph.delta.node.upsert`, `graph.delta.link.upsert`, `presence.beacon`, `subentity.snapshot`
- **Result:** 47 Event_Schema nodes, `subentity.snapshot` under STRICT (SEA required)

---

### L4-003: Hash-anchored validator cache + yanked handling 🔴 Todo
- **Owner:** Felix + Atlas
- **Estimate:** 1 day
- **What:** Cache key = `(schema_uri, version, bundle_hash)`; invalidate on `registry.schema.yanked`; deny unless `replay=true` with policy override
- **AC:** Yanked bundle flips validator accept→reject within one event cycle

---

### L4-004: Public L4 registry export in CI 🔴 Todo
- **Owner:** Atlas
- **Estimate:** 4 hours
- **What:** Generate `build/l4_public_registry.json` in CI; ensure it's what mp-lint and SafeBroadcaster load
- **AC:** CI fails if export missing/stale (timestamp/hash check)

---

## High Priority

### L4-005: U4 naming lints in CI 🔴 Todo
- **Owner:** Luca
- **Estimate:** 3 hours
- **What:** Single `U3_/U4_/Lx_` primary label; `type_name == label`; U3 only on L1–L3; U4 allowed L1–L4; no double labels
- **AC:** Lint passes on 254 protocol nodes and citizen graphs

---

### L4-006: Conformance gate ≥95% to mark bundle active 🔴 Todo
- **Owner:** Luca + Ada + Atlas
- **Estimate:** 1 day
- **What:** Run conformance suite on publish/deprecate/yank and nightly; block `status="active"` if pass rate < 95%
- **AC:** Cannot set `status=active` if suite <95%; nightly drift demotes per policy

---

### L4-007: CPS/SEA policy presence 🟡 Ready
- **Owner:** Ada
- **Estimate:** 1 hour
- **What:** Ensure `CPS-1`, `SEA-1.0`, `SIG_ED25519_V1` policies + signature suite nodes present and governed
- **AC:** Validator can resolve policy chain for any governed topic

---

### L4-008: Type Index authority rule 🔴 Todo
- **Owner:** Luca
- **Estimate:** 2 hours
- **What:** Mark `U4_Type_Index` entries `status:"active"` only if published by active bundles governed by registry
- **AC:** Query for "authoritative type index" returns only nodes reachable via active bundle

---

### L4-009: Envelope unification (ENV_STANDARD_V1) 🟡 Ready
- **Owner:** Ada + Felix
- **Estimate:** 3 hours
- **What:** Use `U4_Envelope_Schema: ENV_STANDARD_V1` for all new events; `U4_REQUIRES_SIG → SIG_ED25519_V1`
- **AC:** Emitted envelopes validate against one schema; signer suite enforced

---

## Medium Priority

### L4-010: mp-lint wildcard mapping + STRICT/FLEX logic 🔴 Todo
- **Owner:** Felix
- **Estimate:** 4 hours
- **What:** Wildcard namespace resolution; STRICT topics require SEA; summary shows zero R-001
- **AC:** Running mp-lint on orchestration/ yields only expected R-005s

---

### L4-011: Registry ceremony events 🔴 Todo
- **Owner:** Ada
- **Estimate:** 2 hours
- **What:** Emit `registry.schema.published|deprecated|yanked|type.indexed` events with `attestation_ref`
- **AC:** Event bus shows four event types on each schema action; validator reacts to yank within one cycle

---

### L4-012: Public projection policy doc + leak check 🔴 Todo
- **Owner:** Luca
- **Estimate:** 3 hours
- **What:** Lock projection to headers + explicit public fields; add CI diff that flags leakage
- **AC:** No private fields appear in `l4_public_registry.json`

---

### L4-013: Code→Law edges (U4_Code_Artifact + U4_EMITS) 🟡 Ready
- **Owner:** Atlas + Felix
- **Estimate:** 1 day
- **What:** Emit NDJSON for `U4_Code_Artifact` and edges `U4_EMITS` (artifact→topic), `U4_IMPLEMENTS` (artifact→type/capability); ingest to graph
- **AC:** Dashboard can click from file path to governing policy/schema

---

### L4-014: Dashboard "validator in sync" badge 🔴 Todo
- **Owner:** Iris
- **Estimate:** 4 hours
- **What:** Read `U4_Conformance_Result` + exported bundle hashes; show green/amber/red status for Schema Registry tile
- **AC:** Drift or failing conformance flips the badge

---

## Ops & Quality (Membrane-Native Reviewer)

### L4-018: Ingest reviewer event schemas 🟡 Ready
- **Owner:** Ada
- **Estimate:** 30 minutes
- **Script:** `tools/protocol/ingest_reviewer_events.py` (ready to run)
- **What:** 17 Event_Schema nodes for membrane-native reviewer system
  - Namespaces: `watcher.*`, `code.*`, `review.*`, `lint.*`, `failure.*`, `protocol.review.*`, `economy.*`
  - Events: file.changed, patch.received, review.started, lint.findings, failure.emit, mandate.enforced, etc.
  - Policies: POL_ORG_REVIEWER_V1 (org review mandates), POL_PROTOCOL_MANDATE_V1 (L4-level enforcement)
- **AC:** 52 + 17 = 69 Event_Schema nodes; reviewer adapters can query schemas via SafeBroadcaster

**Next Steps:**
```bash
python tools/protocol/ingest_reviewer_events.py
python tools/protocol/export_l4_public.py
# Verify: Event_Schema count should be 52 + 17 = 69
```

---

### L4-019: Implement R-200 series linters (Quality Degradation) 🔴 Todo
- **Owner:** Felix
- **Estimate:** 1 day
- **What:** Implement R-200, R-201, R-202 rules in mp-lint
  - R-200: TODO/HACK/FIXME markers in production logic (check for pragma)
  - R-201: Quality degradation patterns (validate=False, timeout=999999, retries=0)
  - R-202: print() in application code (should use logger)
- **Config:** `.mp-lint.yaml` v2.0.0 (rules defined)
- **Spec:** `docs/specs/v2/ops_and_viz/mp_lint_spec.md` §R-200 Series
- **AC:** mp-lint detects all R-200 series violations; pragma suppression works correctly

---

### L4-020: Implement R-300 series linters (Fallback Antipatterns) 🔴 Todo
- **Owner:** Felix
- **Estimate:** 1.5 days
- **What:** Implement R-300, R-301, R-302, R-303 rules in mp-lint
  - R-300: Silent except/pass (AST check for try/except with empty body)
  - R-301: Default return on exception without failure.emit
  - R-302: Unconditional return True in availability checks (fake health)
  - R-303: Infinite loop without sleep/backoff/break
- **Config:** `.mp-lint.yaml` v2.0.0 (rules defined)
- **Spec:** `docs/specs/v2/ops_and_viz/mp_lint_spec.md` §R-300 Series
- **AC:** mp-lint detects all R-300 series violations; pragma suppression works (max 7 days)

---

### L4-021: Implement R-400 series linters (Fail-Loud Contract) 🔴 Todo - CRITICAL
- **Owner:** Felix
- **Estimate:** 2 days
- **What:** Implement R-400, R-401 rules in mp-lint (NO PRAGMA ALLOWED)
  - R-400: Catch without failure.emit or rethrow - AST analysis for exception handlers
  - R-401: failure.emit missing required context (code_location, exception, severity)
- **Enforcement:** Strict - breaks builds immediately, no grace period
- **Config:** `.mp-lint.yaml` v2.0.0 (rules defined, no pragma)
- **Spec:** `docs/specs/v2/ops_and_viz/mp_lint_spec.md` §R-400 Series
- **AC:** mp-lint detects all fail-loud violations; pragma suppression FORBIDDEN; CI fails on R-400/R-401

**Why Critical:** Fail-loud is protocol contract. Silent failures violate membrane discipline and prevent consciousness substrate from learning from errors.

---

### L4-022: Seed Org_Policy nodes for reviewer 🟡 Ready
- **Owner:** Ada
- **Estimate:** 30 minutes
- **Script:** `tools/governance/seed_org_policies.py` (ready to run)
- **What:** Create Org_Policy node for mind-protocol organization
  - Policy ID: `ORG_POLICY_MIND_PROTOCOL_V1`
  - Strictness: high (zero tolerance for R-400, strict thresholds)
  - Severity mappings for all 17 rules (R-001 through R-401)
  - Override rules (pragma constraints: max days, requires ticket)
  - Verdict thresholds (pass_max_errors: 0, soft_fail_max_errors: 2, hard_fail_min_errors: 3)
- **AC:** Reviewer aggregators can query Org_Policy; verdicts respect org-specific thresholds

**Next Steps:**
```bash
python tools/governance/seed_org_policies.py
# Verify: Org_Policy node created with correct severity mappings
```

---

## Later (Economy/Governance Fill-In)

### L4-015: CPS subsystem members (economy) ⏳ Later
- **Owner:** Ada + Luca
- **Estimate:** 1 day
- **What:** Add compute billing topics/schemas (`economy.quote|budget|billing`) into CPS; bind to `CPS-1`
- **AC:** Validator enforces `$MIND` settlement fields on those topics

---

### L4-016: UBC subsystem members ⏳ Later
- **Owner:** Ada + Luca
- **Estimate:** 1 day
- **What:** Add `ubc.distribute` event schema + policy; mark balances compute-only
- **AC:** First UBC issuance flows; projection shows issuance/consumption

---

### L4-017: DRP (dispute/appeal) minimal schemas ⏳ Later
- **Owner:** Ada
- **Estimate:** 1 day
- **What:** Minimal dispute/appeal event schemas with evidence attachments
- **AC:** Test dispute can be filed, routed, resolved with `EVIDENCED_BY`

---

## Acceptance Recap (One Screen)

✅ **mp-lint** on orchestration/ → R-001 ≈ 0, only R-005 on STRICT topics lacking attestation
✅ **SafeBroadcaster** → valid telemetry emits; STRICT topics without `attestation_ref` reject
✅ **build/l4_public_registry.json** exists and matches graph (CI check)
⏳ **Conformance** ≥95% for active bundles; yanked bundle flips validator within one event
⏳ **Labels** and `type_name` coherent across all protocol nodes

---

## Artifacts Ready

### L4 Protocol Core
- ✅ `tools/protocol/ingest_consciousness_events.py` - Engine schemas (L4-002, done)
- ✅ `tools/protocol/ingest_telemetry_policies.py` - Telemetry schemas (L4-001, ready)
- ✅ `tools/protocol/export_l4_public.py` - L4 registry exporter
- ✅ `tools/protocol/hash_l4_graph.py` - Freshness verification

### Membrane-Native Reviewer System
- ✅ `tools/protocol/ingest_reviewer_events.py` - Reviewer event schemas (L4-018, ready)
- ✅ `tools/governance/seed_org_policies.py` - Org policy seed script (L4-022, ready)
- ✅ `.mp-lint.yaml` v2.0.0 - Extended policy configuration (R-001 through R-401, 13 new rules)
- ✅ `docs/specs/v2/ops_and_viz/mp_lint_spec.md` v2.0.0 - Complete spec with R-200/300/400 docs (~140KB)
- ✅ `docs/CODEX_COMMITS_REVIEW_PLAN.md` - Comprehensive review plan for codex commits (900+ lines)

---

## Quick Start for Each Owner

**Luca (Next: L4-001):**
```bash
python tools/protocol/ingest_telemetry_policies.py
python tools/protocol/export_l4_public.py
# Post event schema count (expect 52)
```

**Felix (Next: L4-010):**
```bash
# Implement wildcard namespace resolution in mp-lint
# Add STRICT/FLEX logic to R-005
python tools/mp_lint/cli.py  # Should show R-001 ≈ 0
```

**Atlas (Next: L4-004):**
```bash
# Wire build/l4_public_registry.json into CI
# Add hash freshness check
# Test SafeBroadcaster with telemetry topics
```

**Ada (Next: L4-018, L4-022):**
```bash
# Ingest reviewer event schemas
python tools/protocol/ingest_reviewer_events.py
python tools/protocol/export_l4_public.py
# Verify: Event_Schema count should be 69

# Seed org policies
python tools/governance/seed_org_policies.py
# Verify: Org_Policy node created with correct severity mappings
```

**Ada (Advisory):**
- Review L4-007 (CPS/SEA policy structure)
- Review L4-009 (Envelope unification spec)
- Sign off on L4-011 (Registry ceremony event schemas)

**Iris (Later: L4-014):**
- Dashboard badge for validator sync status
- Code→policy lineage visualization (L4-013)

---

## Notes

- **No paper-over-it workarounds:** Law is the only door. All consciousness events now properly governed via L4.
- **Two-layer defense:** Static validation (mp-lint in CI) + runtime validation (SafeBroadcaster before spill).
- **Clean proof trail:** All events have Event_Schema, Topic_Namespace, Governance_Policy, and enforcement chain.
- **Auditability:** Code→Law edges enable queries like "Show all code emitting to high-stakes topics."

---

**Contact:** Ada (Coordinator & Architect) for L4 architecture questions
**Source:** `consciousness/citizens/SYNC.md` (2025-10-31 03:30 entry)
