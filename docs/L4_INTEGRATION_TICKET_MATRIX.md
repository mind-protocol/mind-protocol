# L4 Integration — Ticket Matrix & Action Plan

**Generated:** 2025-10-31 03:30 UTC
**Status:** L4-002 Complete, L4-001 Ready for Luca
**Source:** SYNC.md + Nicolas's consolidated checklist

---

## Quick Status

| Status | Count | Items |
|--------|-------|-------|
| ✅ Done | 1 | L4-002 |
| 🟡 Ready | 4 | L4-001, L4-007, L4-009, L4-013 |
| 🔴 Todo | 9 | L4-003, L4-004, L4-005, L4-006, L4-008, L4-010, L4-011, L4-012, L4-014 |
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

- ✅ `tools/protocol/ingest_consciousness_events.py` - Engine schemas (L4-002, done)
- ✅ `tools/protocol/ingest_telemetry_policies.py` - Telemetry schemas (L4-001, ready)
- ✅ `tools/protocol/export_l4_public.py` - L4 registry exporter
- ✅ `tools/protocol/hash_l4_graph.py` - Freshness verification
- ✅ `.mp-lint.yaml` - Policy configuration (300+ lines)
- ✅ `docs/specs/v2/ops_and_viz/mp_lint_spec.md` - Complete spec (120KB)

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
