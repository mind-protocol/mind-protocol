# mp-lint: L4-Aware Membrane Linter

**Status:** Specification Complete (Extended with Reviewer System Rules)
**Version:** 2.0.0
**Date:** 2025-10-31
**Owner:** Ada (Coordinator & Architect)
**Spec Reference:** `docs/L4-law/membrane_native_reviewer_and_lint_system.md`
**Implementers:** Felix (Core Engine), Atlas (CI Integration + Runtime Validation), Iris (UI Integration)

---

## Executive Summary

`mp-lint` is a **static membrane linter** that validates Python and Next.js code against the **L4 Schema Registry**. It ensures:

1. **Schema compliance** - Every emitted event references an active Event_Schema
2. **Membrane discipline** - Emissions go through bus APIs, not shadow REST endpoints
3. **Governance enforcement** - High-stakes topics have attestation, compute topics have settlement
4. **UI projection safety** - Dashboard reads from public projection only
5. **Quality maintenance** - No quality degradation (TODO/HACK in logic, disabled validation, print() instead of logger)
6. **Fail-loud contract** - Every exception either rethrows or emits `failure.emit` (silent catches FORBIDDEN)
7. **Fallback detection** - No silent defaults, fake availability, or infinite loops without backoff

**Why this matters:**

- **Static validation catches 80-95% of violations** before code reaches production
- **Runtime validation in SafeBroadcaster** catches remaining dynamic cases before spill
- **Graph edges enable auditability** - "Show all code emitting to `identity.*` topics"
- **CI integration blocks PRs** with membrane violations before merge

**Architecture:** CLI tool that scans Python AST and JS/TS source, validates against L4 export, produces JSON report + optional graph edges (U4_Code_Artifact, U4_EMITS, U4_CONSUMES).

---

## Table of Contents

1. [Purpose & Scope](#purpose--scope)
2. [Architecture](#architecture)
3. [Rules Reference](#rules-reference)
4. [Configuration](#configuration)
5. [Integration Points](#integration-points)
6. [Graph Edges](#graph-edges)
7. [Bootstrap Order](#bootstrap-order)
8. [Implementation Plan](#implementation-plan)
9. [Acceptance Criteria](#acceptance-criteria)

---

## Purpose & Scope

### Problem Statement

**Without static validation:**

1. **Schema violations enter production** - Developer emits `presence.beacan` (typo), no compile-time error, dashboard shows 0 events (subscription mismatch)
2. **Invalid events reach spill buffer** - SafeBroadcaster spills events without schema validation, flush replays invalid events
3. **Governance bypassed** - High-stakes topics (identity, registry) emitted without attestation
4. **Economic leakage** - Compute-intensive topics emit without $MIND settlement
5. **Debugging is reactive** - Find violations in production logs, not IDE/pre-commit

**With static validation:**

1. **Pre-commit hook catches typos** - `❌ R-001: Event schema 'presence.beacan' not found` → fix before commit
2. **CI blocks PRs with violations** - GitHub Actions fails PR if R-004 (CPS settlement) not satisfied
3. **SafeBroadcaster validates before spill** - Invalid events rejected (not spilled), only valid events reach buffer
4. **Auditability via graph** - Query: "Show all code emitting to `identity.*` topics" → U4_EMITS edges

### Scope

**In Scope:**

- Static analysis of Python and Next.js code
- Validation against L4 Schema Registry (event_schemas, topic_namespaces, governance_policies)
- **Protocol Compliance Rules:** R-001 through R-007 (schema existence, topic mapping, signature profiles, CPS settlement, SEA attestation, type/level matching)
- **Membrane Discipline Rules:** R-100, R-101 (bus-only emissions, projection-only UI)
- **Quality Degradation Rules:** R-200 through R-202 (TODO/HACK markers, disabled validation, observability cuts)
- **Fallback Antipattern Rules:** R-300 through R-303 (silent catches, default returns, fake availability, infinite loops)
- **Fail-Loud Contract Rules:** R-400, R-401 (catch without failure.emit FORBIDDEN, failure context validation)
- Integration: Pre-commit hooks, GitHub Actions, SafeBroadcaster runtime validation, File Watcher
- Graph edges: U4_Code_Artifact, U4_EMITS, U4_CONSUMES, U4_IMPLEMENTS

**Out of Scope:**

- Runtime rate limit enforcement (requires telemetry integration)
- Dynamic payload validation (requires full trace analysis)
- Allowed emitter enforcement (requires component identity system)
- Linter self-registration in L4 (linter is tooling, not governed content)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        mp-lint CLI                              │
│  (tools/mp_lint/cli.py)                                          │
└───────┬─────────────────────────────────────────────────────────┘
        │
        ├──▶ Load L4 Registry (registry.py)
        │    └─▶ build/l4_public_registry.json
        │
        ├──▶ Scan Code (scanner_py.py, scanner_js.py)
        │    ├─▶ app/**/*.{ts,tsx,js,jsx}
        │    └─▶ orchestration/**/*.py
        │
        ├──▶ Run Rules (rules.py)
        │    ├─▶ R-001: SCHEMA_EXISTS_ACTIVE
        │    ├─▶ R-002: TOPIC_MAPPED
        │    ├─▶ R-003: SIGNATURE_PROFILE
        │    ├─▶ R-004: CPS_COMPUTE_SETTLEMENT
        │    ├─▶ R-005: SEA_ATTESTATION
        │    ├─▶ R-006: NO_YANKED_VERSION
        │    ├─▶ R-007: U3/U4_MATCH_LEVEL
        │    ├─▶ R-100: BUS_ONLY
        │    └─▶ R-101: PROJECTION_ONLY_UI
        │
        ├──▶ Generate Report (report.py)
        │    ├─▶ build/mp-lint-report.json
        │    └─▶ stdout (pretty format)
        │
        └──▶ Emit Graph Edges (emit_edges.py)
             └─▶ build/mp-lint-edges.ndjson
                  ├─▶ U4_Code_Artifact nodes
                  ├─▶ U4_EMITS edges
                  ├─▶ U4_CONSUMES edges
                  └─▶ U4_IMPLEMENTS edges
```

### Component Breakdown

#### 1. Registry Loader (`registry.py`)

**Purpose:** Load L4 Schema Registry from JSON export, build fast lookup indexes.

**Input:** `build/l4_public_registry.json` (43 event_schemas, 5 topic_namespaces, 3 governance_policies)

**Output:** Python dict with indexes:
```python
{
    "event_schemas": {schema_name: schema_obj},
    "topics": {topic_name: topic_obj},
    "bundles": {bundle_id: bundle_obj},
    "active_event_by_topic": {topic: [schemas]},
    "policies": {policy_id: policy_obj},
    "yanked": set(yanked_bundle_ids)
}
```

**Freshness Check:** Compare `meta.graph_hash` in export with `hash_l4_graph.py` output. If mismatch, fail with:
```
❌ L4 export stale - run tools/protocol/export_l4_public.py first
   Expected: 1821e18558b7c9f28d452ac2fd881e625c701efd6df557665bc6dfd545e5d2d5
   Got:      [different hash]
```

#### 2. Python Scanner (`scanner_py.py`)

**Purpose:** Parse Python files with AST, extract emit call sites.

**Technique:** `ast.parse()` → walk tree → find Call nodes matching emit signatures

**Emit signatures detected:**
- `broadcaster.broadcast(event)`
- `ws.broadcast(event_data)`
- `_transport.emit(topic, payload)`
- `bus.emit(topic, payload, **kwargs)`
- `membrane.inject(actor, topic, payload, envelope)`
- `stimulus_injector.inject(stimulus)`

**Output:** List of emit descriptors:
```python
{
    "kind": "emit",
    "lang": "py",
    "file": "orchestration/mechanisms/consciousness_engine_v2.py",
    "line": 670,
    "topic": "graph.delta.subentity.snapshot",  # Constant string or None if dynamic
    "payload": {...} or None,  # Dict literal or None if dynamic
    "envelope": {...} or None  # Dict literal or None if dynamic
}
```

**Dynamic topic handling:**
```python
# Static: Can extract
await bus.emit("presence.beacon", {"citizen_id": "ada"})
# → topic = "presence.beacon", payload = {"citizen_id": "ada"}

# Dynamic: Can't extract, emits None
topic = f"ecosystem/{eco}/org/{org}/presence"
await bus.emit(topic, payload)
# → topic = None, payload = None
# → Rule check: If topic is None, emit warning "Dynamic topic - runtime validation only"
```

#### 3. JavaScript/TypeScript Scanner (`scanner_js.py`)

**Purpose:** Parse JS/TS files, extract emit call sites.

**MVP Technique (Regex):** Simple regex patterns for constant topics/payloads.

**Patterns:**
```regex
\b(publishEvent|membraneInject)\s*\(\s*['"`](?P<topic>[^'"`]+)['"`]\s*,\s*(?P<payload>\{.*?\})
```

**Output:** Same format as Python scanner.

**Future Enhancement:** Use Babel/Acorn AST parser via Node.js subprocess for full accuracy.

**Trade-off:** Regex catches 60-80% of static cases, misses complex patterns. Runtime validation in SafeBroadcaster catches remainder.

#### 4. Rules Engine (`rules.py`)

**Purpose:** Apply L4 compliance rules to each emit descriptor.

**Input:** List of emit descriptors + L4 registry + policy config

**Output:** List of findings:
```python
{
    "severity": "error",  # or "warn"
    "code": "R-001",
    "file": "orchestration/mechanisms/consciousness_engine_v2.py",
    "line": 670,
    "topic": "graph.delta.subentity.snapshot",
    "message": "No active schema for topic 'graph.delta.subentity.snapshot'"
}
```

**Rules implementation:** See [Rules Reference](#rules-reference).

#### 5. Report Generator (`report.py`)

**Purpose:** Format findings as JSON and human-readable output.

**JSON Output (`build/mp-lint-report.json`):**
```json
{
  "meta": {
    "version": "1.0.0",
    "timestamp": "2025-10-31T12:00:00Z",
    "scanned_files": 156,
    "total_emits": 342,
    "violations": 12,
    "errors": 3,
    "warnings": 9
  },
  "findings": [
    {
      "severity": "error",
      "code": "R-001",
      "file": "orchestration/mechanisms/consciousness_engine_v2.py",
      "line": 670,
      "topic": "graph.delta.subentity.snapshot",
      "message": "No active schema for topic 'graph.delta.subentity.snapshot'",
      "context": [
        "668:     # Emit subentity snapshot",
        "669:     result = self.stimulus_injector.inject(",
        "670:         topic=\"graph.delta.subentity.snapshot\",",
        "671:         payload={...}",
        "672:     )"
      ]
    }
  ]
}
```

**Pretty Output (stdout):**
```
mp-lint: L4 Membrane Linter v1.0.0
================================================================================
Scanned: 156 files, 342 emit sites
Violations: 12 (3 errors, 9 warnings)

❌ orchestration/mechanisms/consciousness_engine_v2.py:670
   R-001: No active schema for topic 'graph.delta.subentity.snapshot'

   668:     # Emit subentity snapshot
   669:     result = self.stimulus_injector.inject(
   670:         topic="graph.delta.subentity.snapshot",
   671:         payload={...}
   672:     )

⚠️  app/consciousness/hooks/useGraphStream.ts:238
   R-101: UI code must read from public projection, not private registry fields

   236:     const citizens = await fetch('/api/citizens/private')
   237:     // Direct private field access
   238:     return citizens

================================================================================
Result: FAIL (3 errors block CI)
```

#### 6. Graph Edges Emitter (`emit_edges.py`)

**Purpose:** Generate NDJSON for U4_Code_Artifact nodes and U4_EMITS/U4_CONSUMES edges.

**Output (`build/mp-lint-edges.ndjson`):**
```json
{"edge_type":"U4_Code_Artifact","data":{"type":"U4_Code_Artifact","repo":"mind-protocol/mindprotocol","path":"orchestration/mechanisms/consciousness_engine_v2.py","lang":"python","hash":"sha256:abc123...","last_lint_ts":"2025-10-31T12:00:00Z","last_lint_status":"pass"}}
{"edge_type":"U4_EMITS","from":{"type":"U4_Code_Artifact","path":"orchestration/mechanisms/consciousness_engine_v2.py"},"to":{"type":"U4_Topic_Namespace","name":"graph.delta.subentity.snapshot"},"evidence":{"rule_passes":["R-001","R-002","R-003"],"emit_count":3,"lines":[145,267,892],"lint_ts":"2025-10-31T12:00:00Z"}}
{"edge_type":"U4_CONSUMES","from":{"type":"U4_Code_Artifact","path":"app/consciousness/hooks/useDashboardState.ts"},"to":{"type":"U4_Topic_Namespace","name":"dashboard.state"},"evidence":{"subscribe_count":1,"lines":[15]}}
{"edge_type":"U4_IMPLEMENTS","from":{"type":"U4_Code_Artifact","path":"orchestration/adapters/ws/safe_broadcaster.py"},"to":{"type":"U4_Capability","name":"CAP_BROADCAST_RESILIENT"},"evidence":{"implements_pattern":"SafeBroadcaster","lint_ts":"2025-10-31T12:00:00Z"}}
```

**Ingestion:** `tools/protocol/ingest_code_edges.py` upserts nodes and edges to protocol graph.

**Queries enabled:**
```cypher
// Show all code emitting to high-stakes topics
MATCH (ca:U4_Code_Artifact)-[:U4_EMITS]->(t:U4_Topic_Namespace)
WHERE t.name STARTS WITH 'identity.' OR t.name STARTS WITH 'registry.'
RETURN ca.path, t.name, ca.last_lint_status

// Impact analysis: if I change schema X, what breaks?
MATCH (s:U4_Event_Schema {name: 'presence.beacon'})-[:U4_MAPS_TO_TOPIC]->(t:U4_Topic_Namespace)
MATCH (ca:U4_Code_Artifact)-[:U4_EMITS]->(t)
RETURN ca.path, ca.lang, ca.last_lint_ts

// Find stale code (not linted recently)
MATCH (ca:U4_Code_Artifact)
WHERE datetime(ca.last_lint_ts) < datetime() - duration({days: 7})
RETURN ca.path, ca.last_lint_ts
```

---

## Rules Reference

### R-001: SCHEMA_EXISTS_ACTIVE

**Severity:** Error
**Category:** Schema Compliance

**Description:** Every emitted event must reference an **active** `Event_Schema` in the L4 Schema Registry.

**Check:**
```python
schemas = registry["active_event_by_topic"].get(emit["topic"], [])
if not schemas:
    return error("R-001", f"No active schema for topic '{emit['topic']}'")
```

**Example Violation:**
```python
# ❌ Typo: "beacan" instead of "beacon"
await bus.emit("presence.beacan", {"citizen_id": "ada"})
# → No schema named "presence.beacan" in registry

# ✅ Correct
await bus.emit("presence.beacon", {"citizen_id": "ada"})
# → Schema exists: Event_Schema/presence.beacon
```

**Why This Matters:** Without schema, no topic mapping → no routing → event lost in membrane.

---

### R-002: TOPIC_MAPPED

**Severity:** Error
**Category:** Schema Compliance

**Description:** Event schema must have exactly one `U4_MAPS_TO_TOPIC` relationship to a valid `Topic_Namespace`.

**Check:**
```python
if not schema.get("maps_to_topic"):
    return error("R-002", f"Schema '{schema['name']}' missing topic mapping")

if len(schemas) > 1:
    return warn("R-002a", f"Multiple active schemas for topic '{topic}' - specify version explicitly")
```

**Example Violation:**
```python
# ❌ Schema exists but has no MAPS_TO_TOPIC edge
# (Data issue in protocol graph, not code issue)
await bus.emit("orphan.event", {...})
# → Schema exists but can't be routed

# ✅ Correct
# Schema 'presence.beacon' maps to Topic_Namespace 'ecosystem.org.presence'
await bus.emit("presence.beacon", {...})
```

**Why This Matters:** Schema without topic mapping can't be routed by membrane → dead event.

---

### R-003: SIGNATURE_PROFILE

**Severity:** Error
**Category:** Governance Compliance

**Description:** If envelope schema requires a `U4_Signature_Suite`, code must set the fields that the suite expects (e.g., `attestation_ref`, `signer`, `ts`).

**Check:**
```python
if schema.get("requires_sig"):
    envelope = emit.get("envelope") or {}
    if "attestation_ref" not in envelope:
        return error("R-003", "Signature suite required: missing 'attestation_ref' in envelope")
```

**Example Violation:**
```python
# ❌ Schema requires ed25519-v1 signature, but envelope has no attestation_ref
await bus.emit(
    "governance.keys.updated",
    payload={...},
    envelope={"version": "1.1"}  # Missing attestation_ref
)

# ✅ Correct
await bus.emit(
    "governance.keys.updated",
    payload={...},
    envelope={
        "version": "1.1",
        "attestation_ref": "sea/snapshot/2025-10-31T12:00:00Z",
        "signer": "ed25519:pubkey:abc123...",
        "ts": "2025-10-31T12:00:00Z"
    }
)
```

**Why This Matters:** High-stakes events without signatures can be forged → governance bypass.

---

### R-004: CPS_COMPUTE_SETTLEMENT

**Severity:** Error
**Category:** Economic Compliance

**Description:** For topics governed by **CPS-1** (Compute Payment Settlement), payload/envelope must include $MIND settlement fields or explicit conversion path.

**Check:**
```python
cps_topics = _topics_governed_by(registry, policies["cps_policy_id"])
if emit["topic"] in cps_topics:
    payload = emit.get("payload") or {}
    if payload.get("settlement_currency") != "MIND" and not payload.get("conversion_path"):
        return error("R-004", "CPS-1: settlement must be in MIND or provide conversion_path")
```

**Example Violation:**
```python
# ❌ Compute-intensive topic without settlement
await bus.emit(
    "ecosystem/mind-protocol/org/core/docs/generate",
    payload={
        "doc_path": "docs/specs/new_feature.md",
        # Missing: settlement_currency or conversion_path
    }
)

# ✅ Correct (direct $MIND settlement)
await bus.emit(
    "ecosystem/mind-protocol/org/core/docs/generate",
    payload={
        "doc_path": "docs/specs/new_feature.md",
        "settlement_currency": "MIND",
        "settlement_amount": 100  # 100 $MIND for doc generation
    }
)

# ✅ Correct (conversion path)
await bus.emit(
    "ecosystem/mind-protocol/org/core/docs/generate",
    payload={
        "doc_path": "docs/specs/new_feature.md",
        "settlement_currency": "USD",
        "settlement_amount": 10,
        "conversion_path": "USD→MIND via CoinGecko rate at emit_ts"
    }
)
```

**Why This Matters:** Prevents compute economic leakage - ensures work is paid for in $MIND or convertible.

---

### R-005: SEA_ATTESTATION

**Severity:** Error
**Category:** High-Stakes Integrity

**Description:** For **high-stakes** topics (identity, legal, trading, registry), code must include `attestation_ref` pointing to a fresh **SEA** (System Event Attestation) snapshot in envelope.

**Check:**
```python
high_stakes = policies.get("high_stakes_topics", [])
if any(_topic_match(emit["topic"], pat) for pat in high_stakes):
    envelope = emit.get("envelope") or {}
    if "attestation_ref" not in envelope:
        return error("R-005", "High-stakes topic requires 'attestation_ref' in envelope")
```

**Example Violation:**
```python
# ❌ Identity snapshot without attestation
await bus.emit(
    "identity.snapshot.attest",
    payload={
        "citizen_id": "ada",
        "identity_hash": "sha256:...",
        "capabilities": [...]
    },
    envelope={"version": "1.1"}  # Missing attestation_ref
)

# ✅ Correct
await bus.emit(
    "identity.snapshot.attest",
    payload={
        "citizen_id": "ada",
        "identity_hash": "sha256:...",
        "capabilities": [...]
    },
    envelope={
        "version": "1.1",
        "attestation_ref": "sea/snapshot/2025-10-31T12:00:00Z",  # SEA snapshot reference
        "signer": "ed25519:pubkey:ada",
        "ts": "2025-10-31T12:00:00Z"
    }
)
```

**Why This Matters:** High-stakes events affect identity, governance, economy, law. Attestation prevents forgery.

**High-stakes topic patterns (from `.mp-lint.yaml`):**
- `identity.*` - Identity snapshots, updates
- `registry.*` - L4 registry schema updates
- `economy.trade.*` - Economic transactions
- `legal.*` - Legal agreements, contracts
- `governance.keys.*` - Key management

---

### R-006: NO_YANKED_VERSION

**Severity:** Error
**Category:** Schema Compliance

**Description:** Code may not reference yanked or deprecated schemas unless explicitly marked `replay=true` and a policy allows.

**Check:**
```python
if schema["bundle_id"] in registry["yanked"]:
    if not (emit.get("replay") == True and policy_allows_replay):
        return error("R-006", "Schema version is yanked or deprecated")
```

**Example Violation:**
```python
# ❌ Schema version 1.0 yanked, code still references it
await bus.emit("membrane.inject@1.0", {...})
# → Bundle containing membrane.inject@1.0 is yanked

# ✅ Correct (use active version)
await bus.emit("membrane.inject@1.1", {...})
# → Version 1.1 is active
```

**Why This Matters:** Yanked schemas have known bugs or security issues. Using them risks data corruption.

---

### R-007: U3/U4_MATCH_LEVEL

**Severity:** Warn (escalate to Error after cleanup)
**Category:** Namespace Discipline

**Description:** If code declares node/edge types (e.g., writing graph seeds), **U3_** types must only target L1–L3, **U4_** may target L1–L4.

**Check:**
```python
if emit.get("node_type", "").startswith("U3_") and emit.get("target_level") == "L4":
    return warn("R-007", "U3_ type targeting L4 - should be U4_")

if emit.get("node_type", "").startswith("U4_") and emit.get("target_level") in ["L1", "L2", "L3"]:
    return warn("R-007", "U4_ type targeting L1-L3 - could be U3_")
```

**Example Violation:**
```python
# ⚠️ U3_Event_Schema used for L4 protocol node
graph.merge_node("U3_Event_Schema", {
    "name": "registry.schema.updated",  # L4 event
    "level": "L4"
})
# → Should be U4_Event_Schema

# ✅ Correct
graph.merge_node("U4_Event_Schema", {
    "name": "registry.schema.updated",
    "level": "L4"
})
```

**Why This Matters:** Type prefix indicates scope. U3_ is universal across L1-L3 (ecosystems). U4_ includes L4 (protocol layer).

---

### R-100: BUS_ONLY

**Severity:** Error
**Category:** Membrane Discipline

**Description:** Emissions must go through bus/inject APIs (no shadow REST endpoints that bypass the membrane for governed topics).

**Check:**
```python
if is_governed_topic(emit["topic"]) and emit["method"] == "REST":
    if emit["namespace"] not in policies.get("exempt_namespaces", []):
        return error("R-100", "Governed topics must emit via membrane bus, not direct REST")
```

**Example Violation:**
```python
# ❌ Governed topic emitted via REST endpoint, bypassing membrane
@app.post("/api/presence/update")
async def update_presence(citizen_id: str):
    # Direct database write, no membrane validation
    db.update_presence(citizen_id, "active")
    return {"ok": True}

# ✅ Correct (emit via bus)
@app.post("/api/presence/update")
async def update_presence(citizen_id: str):
    # Emit to bus → membrane validates → subscribers notified
    await bus.emit("presence.beacon", {
        "citizen_id": citizen_id,
        "availability": "active"
    })
    return {"ok": True}
```

**Why This Matters:** REST endpoints bypass L4 validation (schema, governance, attestation). All governed events must flow through membrane.

**Exempt namespaces (from `.mp-lint.yaml`):**
- `internal.*` - Internal/debug topics
- `dev.*` - Development topics

---

### R-101: PROJECTION_ONLY_UI

**Severity:** Error
**Category:** Membrane Discipline

**Description:** Next.js UI must read from the **public projection** for registry data; private fields cannot be fetched directly.

**Check:**
```python
if is_ui_code(emit["file"]) and emit.get("api_endpoint", "").endswith("/private"):
    return error("R-101", "UI code must read from public projection, not private registry fields")
```

**Example Violation:**
```typescript
// ❌ UI fetches private registry fields directly
const citizens = await fetch('/api/citizens/private')
const privateData = citizens.map(c => c.internal_state)  // Leaks private fields

// ✅ Correct (subscribe to public projection)
const state = useDashboardState()  // Subscribes to dashboard.state topic
const citizens = state.citizens     // Public projection only (no internal_state)
```

**Why This Matters:** Dashboard must not leak private fields (internal_state, debug data, sensitive configs). Public projection is the contract.

---

## R-200 Series: Quality Degradation Detection

### R-200: TODO_OR_HACK

**Severity:** Error
**Category:** Quality Maintenance

**Description:** Production logic paths must not contain `TODO`, `HACK`, `FIXME`, or `XXX` markers. These indicate incomplete work that may cause runtime failures or incorrect behavior.

**Check:**
```python
if is_logic_path(node) and any(marker in get_comments(node) for marker in ["TODO", "HACK", "FIXME", "XXX"]):
    # Allow in docstrings and non-logic comments
    if not is_docstring(node) and not allow_pragma_present(node, "allow-degrade"):
        return error("R-200", f"TODO/HACK marker in logic path: {marker}")
```

**Example Violation:**
```python
# ❌ TODO in production logic
def get_citizen_ids():
    # TODO: Replace with actual FalkorDB query
    return ["felix", "ada", "iris"]  # Hardcoded fallback

# ❌ HACK in error handling
try:
    result = await api_call()
except Exception:
    # HACK: Return empty list until we fix the API
    return []

# ✅ Correct (with pragma if genuinely needed)
def get_citizen_ids():
    # lint: allow-degrade(reason="Migration to v2 API, ticket ORG-456", until="2025-11-07")
    # TODO: Complete v2 API migration
    return await legacy_api.get_citizens()

# ✅ Correct (TODO in docstring - allowed)
def complex_algorithm():
    """
    Implements spreading activation.

    TODO: Add energy decay parameter in v2.
    """
    return compute_activation()
```

**Why This Matters:** TODO markers indicate unfinished work that may fail under load, edge cases, or production data. They're acceptable during development but **forbidden in production code paths** without explicit suppression + ticket.

**Pragma Format:**
```python
# lint: allow-degrade(reason="Waiting for FalkorDB v3 migration", until="2025-11-10", ticket="ORG-123")
```

---

### R-201: QUALITY_DEGRADE

**Severity:** Error
**Category:** Quality Maintenance

**Description:** Detects quality degradation patterns: disabled validation, absurd timeouts, zero retries/backoff, max_attempts=1.

**Check:**
```python
patterns = [
    r"validate\s*=\s*False",
    r"timeout\s*=\s*(0|999999|float\('inf'\))",
    r"retries\s*=\s*0",
    r"backoff\s*=\s*0",
    r"max_attempts\s*=\s*1"
]

for pattern in patterns:
    if re.search(pattern, code) and not allow_pragma_present(node, "allow-degrade"):
        return error("R-201", f"Quality degradation: {pattern}")
```

**Example Violation:**
```python
# ❌ Validation disabled
await bus.emit("identity.snapshot", payload, validate=False)

# ❌ Absurd timeout (effectively infinite)
response = await http.get("/api/data", timeout=999999)

# ❌ Zero backoff (instant retry storm)
@retry(max_attempts=10, backoff=0)
def flaky_operation():
    ...

# ❌ Single attempt with retry decorator (fake resilience)
@retry(max_attempts=1)
def should_not_use_retry():
    ...

# ✅ Correct
await bus.emit("identity.snapshot", payload, validate=True)  # Default
response = await http.get("/api/data", timeout=30)  # Reasonable timeout
@retry(max_attempts=3, backoff=2.0)  # Exponential backoff
def flaky_operation():
    ...

# ✅ Correct (with pragma if genuinely needed for testing)
# lint: allow-degrade(reason="Load test without validation overhead", until="2025-11-05", ticket="TEST-789")
await bus.emit("load.test.event", payload, validate=False)
```

**Why This Matters:** These patterns indicate shortcuts taken under pressure that create production risks: unvalidated data causing crashes, retry storms overwhelming services, timeouts that never trigger.

---

### R-202: OBSERVABILITY_CUT

**Severity:** Warning
**Category:** Quality Maintenance

**Description:** Application code must use `logger` instead of `print()` for observability. Scripts and tests are exempt.

**Check:**
```python
if is_application_code(file) and "print(" in code:
    if not is_excluded_path(file, ["scripts/**", "tools/**", "tests/**"]):
        return warn("R-202", "Use logger instead of print() in application code")
```

**Example Violation:**
```python
# ❌ print() in application code
def process_event(event):
    print(f"Processing event: {event['id']}")  # Lost in prod, no structured logs
    return handle(event)

# ❌ print() for error reporting
except Exception as e:
    print(f"Error: {e}")  # No error tracking, no alerts

# ✅ Correct
import logging
logger = logging.getLogger(__name__)

def process_event(event):
    logger.info("Processing event", extra={"event_id": event['id']})
    return handle(event)

# ✅ Correct (error with context)
except Exception as e:
    logger.error("Event processing failed", exc_info=True, extra={"event_id": event['id']})

# ✅ Correct (scripts can use print)
# File: tools/analyze_logs.py
if __name__ == "__main__":
    print(f"Analyzing {len(logs)} log entries...")  # CLI output - allowed
```

**Why This Matters:** `print()` output is unstructured, lost in production, and can't be queried/alerted on. Structured logging enables debugging, monitoring, and incident response.

---

## R-300 Series: Fallback Antipattern Detection

### R-300: BARE_EXCEPT_PASS

**Severity:** Error
**Category:** Fail-Loud Contract

**Description:** Silent `except: pass` blocks are **forbidden**. Every exception must either propagate (rethrow) or emit `failure.emit`.

**Check:**
```python
if is_bare_except_pass(node):
    if not allow_pragma_present(node, "allow-fallback"):
        return error("R-300", "Silent except/pass forbidden (violates Fail-Loud principle)")
```

**Example Violation:**
```python
# ❌ Silent catch (violation)
try:
    result = await api.get_data()
except:
    pass  # Error swallowed - no indication of failure

# ❌ Silent catch with specific exception
try:
    config = load_config()
except FileNotFoundError:
    pass  # File missing - but no one knows

# ✅ Correct (rethrow)
try:
    result = await api.get_data()
except Exception as e:
    logger.error("API call failed", exc_info=True)
    raise  # Propagate up

# ✅ Correct (emit failure.emit)
try:
    result = await api.get_data()
except Exception as e:
    await broadcaster.broadcast(
        "failure.emit",
        {
            "code_location": "adapters/api_client.py:45",
            "exception": str(e),
            "severity": "error",
            "suggestion": "Check API endpoint availability"
        }
    )
    return None  # Explicit default after emitting failure

# ✅ Correct (with pragma if genuinely needed)
# lint: allow-fallback(reason="Legacy adapter during migration", until="2025-11-03", ticket="MIG-234")
try:
    legacy_call()
except:
    pass  # Suppress during migration phase
```

**Why This Matters:** Silent catches hide failures, making debugging impossible and masking systemic issues. The **Fail-Loud Contract** requires all exceptions to be visible (either via propagation or explicit `failure.emit` events).

---

### R-301: SILENT_DEFAULT_RETURN

**Severity:** Error
**Category:** Fail-Loud Contract

**Description:** Returning default values (`None`, `[]`, `{}`, `0`, `False`, `""`) in exception handlers without emitting `failure.emit` is **forbidden**.

**Check:**
```python
if is_except_with_default_return(node):
    if not has_failure_emit_call(node) and not allow_pragma_present(node, "allow-fallback"):
        return error("R-301", "Default return on exception without failure.emit (violates Fail-Loud)")
```

**Example Violation:**
```python
# ❌ Silent default return
def get_citizen_list():
    try:
        return await db.query("MATCH (c:Citizen) RETURN c")
    except Exception:
        return []  # Empty list - caller doesn't know query failed

# ❌ Silent None return
def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # Caller can't distinguish "no config" from "load failed"

# ✅ Correct (rethrow - let caller handle)
def get_citizen_list():
    try:
        return await db.query("MATCH (c:Citizen) RETURN c")
    except Exception as e:
        logger.error("Citizen query failed", exc_info=True)
        raise  # Propagate

# ✅ Correct (emit failure.emit before default return)
def get_citizen_list():
    try:
        return await db.query("MATCH (c:Citizen) RETURN c")
    except Exception as e:
        await broadcaster.broadcast(
            "failure.emit",
            {
                "code_location": "adapters/db.py:123",
                "exception": str(e),
                "severity": "error",
                "suggestion": "Check FalkorDB connection"
            }
        )
        return []  # Explicit default after emitting failure

# ✅ Correct (with pragma)
# lint: allow-fallback(reason="Degraded mode during outage", until="2025-11-05", ticket="OPS-567")
def get_citizen_list():
    try:
        return await db.query("MATCH (c:Citizen) RETURN c")
    except Exception:
        return []  # Graceful degradation with suppression
```

**Why This Matters:** Silent defaults mask failures. Callers proceed with empty/null data, leading to downstream errors that are hard to trace back to the original failure.

---

### R-302: FAKE_AVAILABILITY

**Severity:** Error
**Category:** Fallback Antipattern

**Description:** Availability/health check functions must not unconditionally return `True`. They must perform actual checks.

**Check:**
```python
if is_health_check_function(node) and is_unconditional_return_true(node):
    if not allow_pragma_present(node, "allow-fallback"):
        return error("R-302", "Unconditional 'return True' in availability check (fake availability)")
```

**Example Violation:**
```python
# ❌ Fake availability (always returns True)
def is_available():
    return True  # Claim ready without checking anything

# ❌ Fake health check
async def health_check():
    # TODO: Implement actual check
    return True

# ✅ Correct (actual check)
def is_available():
    try:
        # Check if websocket has connected clients
        return len(ws_clients) > 0 and ws_server_running
    except Exception:
        return False

# ✅ Correct (check with timeout)
async def health_check():
    try:
        response = await db.execute_command("PING", timeout=1.0)
        return response == b"PONG"
    except Exception:
        return False

# ✅ Correct (with pragma if stubbing temporarily)
# lint: allow-fallback(reason="Stub during service migration", until="2025-11-02", ticket="SVC-890")
def is_available():
    # Stub: Always available during migration
    return True
```

**Why This Matters:** Fake availability breaks load balancers, retry logic, and circuit breakers. Services report "ready" when they're not, causing cascading failures.

---

### R-303: INFINITE_LOOP_NO_SLEEP

**Severity:** Warning
**Category:** Fallback Antipattern

**Description:** `while True` loops must include `sleep`, `await`, `break`, or `return` to prevent CPU spinning.

**Check:**
```python
if is_infinite_loop(node):
    if not has_sleep_or_exit(node) and not allow_pragma_present(node, "allow-fallback"):
        return warn("R-303", "Infinite loop without sleep/backoff/break (CPU spin)")
```

**Example Violation:**
```python
# ❌ CPU spin (no sleep)
while True:
    event = queue.get_nowait()  # Busy-wait if queue empty
    if event:
        process(event)

# ❌ Polling without backoff
while True:
    if condition_check():
        do_work()
    # No sleep - spins at 100% CPU

# ✅ Correct (with sleep)
while True:
    event = queue.get_nowait()
    if event:
        process(event)
    time.sleep(0.1)  # Yield CPU

# ✅ Correct (async with await)
while True:
    event = await queue.get()  # Blocks until event available
    process(event)

# ✅ Correct (with break condition)
while True:
    if should_stop:
        break  # Exit loop
    do_work()
    time.sleep(1)

# ✅ Correct (event-driven, no polling)
async def event_loop():
    async for event in event_stream():  # No busy-wait
        await process(event)
```

**Why This Matters:** Busy-wait loops consume 100% CPU, starve other processes, and drain battery on laptops. Always yield or block properly.

---

## R-400 Series: Fail-Loud Contract Enforcement

### R-400: FAIL_LOUD_REQUIRED

**Severity:** Error (CRITICAL - No pragma allowed)
**Category:** Fail-Loud Contract

**Description:** Every `except` block that chooses a non-exception path (return/continue without raise) **MUST** emit `failure.emit`. Silent catches are **FORBIDDEN**.

**This is the core Fail-Loud contract:** Exceptions are either propagated (rethrow) or made visible (`failure.emit`). No third option.

**Check:**
```python
if is_except_block(node):
    if has_non_exception_path(node):  # return/continue without raise
        if not has_failure_emit_call(node) and not has_raise(node):
            return error("R-400", "Catch without failure.emit or rethrow FORBIDDEN (Fail-Loud contract violation)")
```

**Example Violation:**
```python
# ❌ FORBIDDEN (silent catch with return)
try:
    result = await api.call()
except Exception:
    return None  # Silent failure - no one knows call failed

# ❌ FORBIDDEN (silent catch with continue)
for item in items:
    try:
        process(item)
    except Exception:
        continue  # Skip item silently - no visibility into failures

# ❌ FORBIDDEN (log but no failure.emit)
try:
    result = await api.call()
except Exception as e:
    logger.error(f"API failed: {e}")  # Logged but not emitted
    return None  # Still silent from membrane perspective

# ✅ Correct (rethrow)
try:
    result = await api.call()
except Exception as e:
    logger.error("API call failed", exc_info=True)
    raise  # Propagate - caller handles

# ✅ Correct (emit failure.emit then return)
try:
    result = await api.call()
except Exception as e:
    await broadcaster.broadcast(
        "failure.emit",
        {
            "code_location": "services/api_client.py:89",
            "exception": str(e),
            "severity": "error",
            "suggestion": "Check API endpoint health",
            "trace_id": get_trace_id()
        }
    )
    return None  # Explicit default AFTER emitting failure

# ✅ Correct (emit failure.emit then continue)
for item in items:
    try:
        process(item)
    except Exception as e:
        await emit_failure({
            "code_location": "batch_processor.py:234",
            "exception": str(e),
            "severity": "warn",
            "suggestion": f"Skipped item {item['id']}"
        })
        continue  # Skip AFTER emitting failure
```

**Why This Matters:** This is the **core runtime contract** that makes the membrane observable. Every failure becomes a first-class event that can be monitored, alerted on, and debugged. Silent failures are **architectural violations** that break observability.

**NO PRAGMA ALLOWED:** R-400 violations must be fixed immediately. No suppression, no grace period.

---

### R-401: MISSING_FAILURE_CONTEXT

**Severity:** Error
**Category:** Fail-Loud Contract

**Description:** `failure.emit` events must include required context fields: `code_location`, `exception`, `severity`. Optional but recommended: `change_id`, `suggestion`, `trace_id`.

**Check:**
```python
if is_failure_emit_call(node):
    payload = extract_payload(node)
    required = ["code_location", "exception", "severity"]
    missing = [f for f in required if f not in payload]
    if missing:
        return error("R-401", f"failure.emit missing required context: {missing}")

    if payload.get("severity") not in ["warn", "error", "fatal"]:
        return error("R-401", f"Invalid severity: {payload['severity']} (must be warn/error/fatal)")
```

**Example Violation:**
```python
# ❌ Missing code_location
await broadcaster.broadcast(
    "failure.emit",
    {
        "exception": str(e),
        "severity": "error"
        # Missing: code_location
    }
)

# ❌ Missing exception
await broadcaster.broadcast(
    "failure.emit",
    {
        "code_location": "adapter.py:123",
        "severity": "error"
        # Missing: exception
    }
)

# ❌ Invalid severity
await broadcaster.broadcast(
    "failure.emit",
    {
        "code_location": "adapter.py:123",
        "exception": str(e),
        "severity": "high"  # Invalid - must be warn/error/fatal
    }
)

# ✅ Correct (minimal)
await broadcaster.broadcast(
    "failure.emit",
    {
        "code_location": "adapters/db_client.py:456",
        "exception": str(e),
        "severity": "error"
    }
)

# ✅ Correct (complete with optional fields)
await broadcaster.broadcast(
    "failure.emit",
    {
        "code_location": "adapters/db_client.py:456",
        "exception": str(e),
        "severity": "error",
        "suggestion": "Check FalkorDB connection and retry",
        "trace_id": request.trace_id,
        "change_id": f"local:{int(time.time())}"
    }
)
```

**Why This Matters:** Failure events without context are useless for debugging. `code_location` enables immediate source lookup, `exception` shows what failed, `severity` enables proper alerting.

---

## Pragma System

mp-lint supports **temporary suppression** of certain rules via inline pragmas. **R-400 (Fail-Loud) has NO pragma support** - violations must be fixed immediately.

### allow-degrade (R-200 series)

**Format:**
```python
# lint: allow-degrade(reason="...", until="YYYY-MM-DD", ticket="ORG-123")
```

**Constraints:**
- `reason`: Required, non-empty string explaining why degradation is needed
- `until`: Required, ISO date format (YYYY-MM-DD), max 14 days from today
- `ticket`: Required, ticket reference (e.g., "ORG-123", "MIG-456")

**Example:**
```python
# lint: allow-degrade(reason="Migration to v2 API in progress", until="2025-11-07", ticket="API-789")
# TODO: Complete v2 API migration
result = await legacy_api.get_data(validate=False)
```

---

### allow-fallback (R-300 series)

**Format:**
```python
# lint: allow-fallback(reason="...", until="YYYY-MM-DD", ticket="ORG-123")
```

**Constraints:**
- `reason`: Required, non-empty string explaining why fallback is needed
- `until`: Required, ISO date format (YYYY-MM-DD), max 7 days from today (shorter than allow-degrade)
- `ticket`: Required, ticket reference

**Example:**
```python
# lint: allow-fallback(reason="Degraded mode during DB migration", until="2025-11-03", ticket="OPS-567")
try:
    return await db.query("...")
except Exception:
    return []  # Graceful degradation during migration
```

---

### NO PRAGMA for R-400 (Fail-Loud)

**R-400 violations cannot be suppressed.** The Fail-Loud contract is **non-negotiable** - every exception must either rethrow or emit `failure.emit`.

If you encounter R-400 violations during migration:
1. **Phase 1:** Temporarily change R-400 severity to `warning` in `.mp-lint.yaml`
2. **Phase 2:** Fix all violations (add `failure.emit` or rethrow)
3. **Phase 3:** Restore R-400 severity to `error`

**Timeline:** 3-5 days max for Phase 1/2 before enforcement.

---

## Configuration

**File:** `.mp-lint.yaml` (repo root)

**Key sections:**

### L4 Registry Source
```yaml
l4_registry:
  path: ./build/l4_public_registry.json
  verify_freshness: true  # Fail if export hash doesn't match protocol graph
```

### Code Scanning
```yaml
code:
  roots:
    - app                    # Next.js dashboard
    - orchestration          # Python services
  exclude:
    - "**/node_modules/**"
    - "**/.next/**"
  python_emit_calls:
    - "broadcaster.broadcast"
    - "ws.broadcast"
    - "_transport.emit"
    - "bus.emit"
    - "membrane.inject"
  js_emit_calls:
    - "publishEvent"
    - "membraneInject"
    - "ws.send"
```

### Policies
```yaml
policies:
  cps_policy_id: "CPS-1"
  cps_governed_topics:
    - "ecosystem.*/org.*/docs/generate"
    - "ecosystem.*/org.*/ko/proposed"
  high_stakes_topics:
    - "identity.*"
    - "registry.*"
    - "economy.trade.*"
    - "legal.*"
    - "governance.keys.*"
```

### Output
```yaml
output:
  report_json: ./build/mp-lint-report.json
  report_pretty: true
  graph_edges_ndjson: ./build/mp-lint-edges.ndjson
  fail_on: error  # Options: error, warn, never
```

### Rules
```yaml
rules:
  R-001:
    enabled: true
    severity: error
  R-002:
    enabled: true
    severity: error
  # ... (see .mp-lint.yaml for full config)
```

**Full config:** See `.mp-lint.yaml` in repo root.

---

## Integration Points

### 1. SafeBroadcaster Runtime Validation

**File:** `orchestration/adapters/ws/safe_broadcaster.py`

**Integration:**
```python
from orchestration.libs.schema_registry import SchemaRegistry

class SafeBroadcaster:
    def __init__(self, ws_client, spill_path: str, health_bus, registry: SchemaRegistry):
        self.ws = ws_client
        self.spill = deque(maxlen=10000)
        self.health_bus = health_bus
        self.registry = registry  # Schema registry for runtime validation
        self.ready = asyncio.Event()

    async def safe_emit(self, event: Dict[str, Any]) -> bool:
        """Emit event to WebSocket, validate schema first, spill on failure."""

        # 1. VALIDATE SCHEMA (catches what static analysis can't see)
        schema = await self.registry.get(event["type"])
        validation = schema.validate(event["content"])

        if not validation.ok:
            # REJECT before spill - invalid events never enter system
            await self._self_report(
                "schema_violation",
                success=False,
                rule_code=validation.failed_rule,  # e.g., "R-001", "R-004"
                topic=event.get("topic"),
                error=validation.message
            )
            return False  # Don't spill invalid events

        # 2. TRY TO EMIT (already validated)
        try:
            if not self.ws.is_available():
                raise RuntimeError("ws_not_ready")
            await self.ws.send(event)
            self.emit_count += 1
            return True
        except Exception as e:
            # ONLY valid events reach spill buffer
            self.spill.append(event)
            self.spill_count += 1
            await self._self_report("broadcaster_spill", success=False, error=str(e))
            return False
```

**Key benefit:** Spill buffer contains ONLY valid events. When flushing after reconnect, no re-validation needed.

**Handoff to Atlas:** Implement schema validation in `safe_emit()` method.

---

### 2. Dashboard Aggregator Schema Contracts

**File:** `orchestration/services/dashboard_aggregator.py`

**Integration:**
```python
async def _handle_presence(self, event):
    """Update presence state cache"""

    # Rule R-001 guarantees schema exists
    # Rule R-002 guarantees topic mapping
    # → We KNOW presence.beacon has these fields (defined in L4)

    # No try/except spam - schema contract guarantees structure
    citizen_id = event["content"]["citizen_id"]
    availability = event["content"]["availability"]
    ttl = event["content"]["ttl_seconds"]

    # If schema changes (e.g., adds optional field), mp-lint catches it in CI
    self.presence_state[citizen_id] = event["content"]
```

**Key benefit:** Safe field access without defensive try/except. Schema contract guarantees structure.

**Handoff to Atlas:** Remove try/except wrappers, rely on schema contracts.

---

### 3. Pre-Commit Hook

**File:** `.pre-commit-config.yaml`

**Integration:**
```yaml
repos:
  - repo: local
    hooks:
      - id: mp-lint-freshness
        name: Verify L4 registry freshness
        entry: python tools/protocol/hash_l4_graph.py --verify build/l4_public_registry.json
        language: system
        pass_filenames: false

      - id: mp-lint
        name: Lint membrane code
        entry: python tools/mp_lint/cli.py
        language: system
        pass_filenames: false
        fail_fast: true  # Stop on first error
```

**Workflow:**
1. Developer commits code
2. Pre-commit hook runs `hash_l4_graph.py --verify` → checks export freshness
3. If stale: `❌ L4 export stale - run tools/protocol/export_l4_public.py first`
4. If fresh: Pre-commit hook runs `mp-lint` → validates code
5. If violations: `❌ R-001: Event schema 'presence.beacan' not found` → commit blocked
6. Developer fixes → commits successfully

**Handoff to Atlas:** Wire pre-commit hooks in `.pre-commit-config.yaml`.

---

### 4. GitHub Actions CI

**File:** `.github/workflows/ci.yaml`

**Integration:**
```yaml
name: CI

on: [push, pull_request]

jobs:
  membrane-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Export L4 registry
        run: python tools/protocol/export_l4_public.py --output build/l4_public_registry.json

      - name: Verify registry freshness
        run: |
          GRAPH_HASH=$(python tools/protocol/hash_l4_graph.py)
          EXPORT_HASH=$(jq -r '.meta.graph_hash' build/l4_public_registry.json)
          if [ "$GRAPH_HASH" != "$EXPORT_HASH" ]; then
            echo "❌ L4 export stale - re-export before linting"
            exit 1
          fi

      - name: Lint membrane code
        run: python tools/mp_lint/cli.py

      - name: Upload lint report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: mp-lint-report
          path: build/mp-lint-report.json

      - name: Annotate PR (if failures)
        if: failure()
        run: |
          # Parse build/mp-lint-report.json and add file annotations to PR
          python tools/ci/annotate_pr_with_lint.py
```

**Workflow:**
1. Developer opens PR
2. CI runs: export L4 → verify freshness → lint code
3. If violations: CI fails, PR blocked
4. File annotations show violations inline: `orchestration/mechanisms/consciousness_engine_v2.py:670 - R-001: No active schema for topic`
5. Developer fixes, pushes → CI re-runs → passes → PR mergeable

**Handoff to Atlas:** Implement CI workflow in `.github/workflows/ci.yaml`.

---

### 5. Code Edge Ingestion

**File:** `tools/protocol/ingest_code_edges.py`

**Integration:**
```python
#!/usr/bin/env python3
"""
Ingest code edges from mp-lint output to protocol graph.
Creates U4_Code_Artifact nodes and U4_EMITS/U4_CONSUMES edges.
"""

import json
import redis

def ingest_lint_edges(ndjson_path: str):
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph = "protocol"

    with open(ndjson_path) as f:
        for line in f:
            edge = json.loads(line)

            if edge["edge_type"] == "U4_Code_Artifact":
                # Upsert Code_Artifact node
                query = f"""
                MERGE (ca:U4_Code_Artifact {{path: '{edge['data']['path']}'}})
                ON CREATE SET
                    ca.repo = '{edge['data']['repo']}',
                    ca.lang = '{edge['data']['lang']}',
                    ca.hash = '{edge['data']['hash']}'
                ON MATCH SET
                    ca.last_lint_ts = '{edge['data']['last_lint_ts']}',
                    ca.last_lint_status = '{edge['data']['last_lint_status']}'
                """
                r.execute_command("GRAPH.QUERY", graph, query)

            elif edge["edge_type"] == "U4_EMITS":
                # Create U4_EMITS edge
                query = f"""
                MATCH (ca:U4_Code_Artifact {{path: '{edge['from']['path']}'}})
                MATCH (t:U4_Topic_Namespace {{name: '{edge['to']['name']}'}})
                MERGE (ca)-[e:U4_EMITS]->(t)
                ON CREATE SET
                    e.evidence = '{json.dumps(edge['evidence'])}'
                ON MATCH SET
                    e.evidence = '{json.dumps(edge['evidence'])}'
                """
                r.execute_command("GRAPH.QUERY", graph, query)

            # Similar for U4_CONSUMES, U4_IMPLEMENTS

if __name__ == "__main__":
    ingest_lint_edges("build/mp-lint-edges.ndjson")
```

**Workflow:**
1. `mp-lint` runs → emits `build/mp-lint-edges.ndjson`
2. CI runs `tools/protocol/ingest_code_edges.py` → upserts nodes/edges to protocol graph
3. Queries enabled:
   - "Show all code emitting to `identity.*` topics"
   - "If I change schema X, what code breaks?"
   - "Find code not linted in 7 days"

**Handoff to Atlas:** Implement `ingest_code_edges.py` script.

---

## Graph Edges

### Node: U4_Code_Artifact

**Purpose:** Represents a source code file that emits/consumes membrane events.

**Schema:**
```python
{
    "type": "U4_Code_Artifact",
    "repo": "mind-protocol/mindprotocol",
    "path": "orchestration/mechanisms/consciousness_engine_v2.py",
    "lang": "python",  # or "typescript", "javascript"
    "hash": "sha256:abc123...",  # Git blob hash for precise versioning
    "last_lint_ts": "2025-10-31T12:00:00Z",
    "last_lint_status": "pass"  # or "fail"
}
```

**Why hash matters:** Git blob hash allows tracking which version of file passed lint. If file changes, hash changes → re-lint required.

---

### Edge: U4_EMITS

**Purpose:** Code artifact emits events to a topic namespace.

**Schema:**
```python
{
    "from": {"type": "U4_Code_Artifact", "path": "orchestration/mechanisms/consciousness_engine_v2.py"},
    "to": {"type": "U4_Topic_Namespace", "name": "graph.delta.subentity.snapshot"},
    "evidence": {
        "rule_passes": ["R-001", "R-002", "R-003"],  # Which rules this emit satisfies
        "emit_count": 3,  # How many emit sites in this file for this topic
        "lines": [145, 267, 892],  # Line numbers of emit sites
        "lint_ts": "2025-10-31T12:00:00Z"
    }
}
```

**Queries enabled:**
```cypher
// Show all code emitting to high-stakes topics
MATCH (ca:U4_Code_Artifact)-[:U4_EMITS]->(t:U4_Topic_Namespace)
WHERE t.name STARTS WITH 'identity.' OR t.name STARTS WITH 'registry.'
RETURN ca.path, t.name, ca.last_lint_status

// Impact analysis: if I change schema X, what breaks?
MATCH (s:U4_Event_Schema {name: 'presence.beacon'})-[:U4_MAPS_TO_TOPIC]->(t:U4_Topic_Namespace)
MATCH (ca:U4_Code_Artifact)-[:U4_EMITS]->(t)
RETURN ca.path, ca.lang, ca.last_lint_ts
```

---

### Edge: U4_CONSUMES

**Purpose:** Code artifact subscribes to/reads from a topic namespace.

**Schema:**
```python
{
    "from": {"type": "U4_Code_Artifact", "path": "app/consciousness/hooks/useDashboardState.ts"},
    "to": {"type": "U4_Topic_Namespace", "name": "dashboard.state"},
    "evidence": {
        "subscribe_count": 1,  # How many subscribe calls in this file
        "lines": [15],  # Line numbers of subscribe sites
        "lint_ts": "2025-10-31T12:00:00Z"
    }
}
```

**Queries enabled:**
```cypher
// Show all UI code consuming citizen presence events
MATCH (ca:U4_Code_Artifact)-[:U4_CONSUMES]->(t:U4_Topic_Namespace)
WHERE ca.path STARTS WITH 'app/' AND t.name STARTS WITH 'ecosystem.org.presence'
RETURN ca.path, t.name
```

---

### Edge: U4_IMPLEMENTS

**Purpose:** Code artifact implements a capability or pattern.

**Schema:**
```python
{
    "from": {"type": "U4_Code_Artifact", "path": "orchestration/adapters/ws/safe_broadcaster.py"},
    "to": {"type": "U4_Capability", "name": "CAP_BROADCAST_RESILIENT"},
    "evidence": {
        "implements_pattern": "SafeBroadcaster",
        "lint_ts": "2025-10-31T12:00:00Z"
    }
}
```

**Queries enabled:**
```cypher
// Show all code implementing resilient broadcast
MATCH (ca:U4_Code_Artifact)-[:U4_IMPLEMENTS]->(cap:U4_Capability {name: 'CAP_BROADCAST_RESILIENT'})
RETURN ca.path, ca.lang
```

---

## Bootstrap Order

**Critical dependency sequence:**

```
1. FalkorDB running (protocol graph exists)
   └─ docker run falkordb

2. Ingest L4 schemas (Event_Schema, Topic_Namespace, Governance_Policy)
   └─ python tools/protocol/ingest_docs_protocol.py
   └─ python tools/protocol/ingest_ko_events.py
   └─ python tools/protocol/ingest_citizen_awareness_events.py

3. Export L4 public registry
   └─ python tools/protocol/export_l4_public.py --output build/l4_public_registry.json

4. Build mp-lint (install dependencies)
   └─ pip install -r tools/mp_lint/requirements.txt

5. Run mp-lint (development)
   └─ python tools/mp_lint/cli.py

6. (Optional) Ingest code edges to protocol graph
   └─ python tools/protocol/ingest_code_edges.py build/mp-lint-edges.ndjson
```

**Freshness check prevents stale exports:**

If L4 protocol graph changes (new schema added), developer must:
1. Re-export: `python tools/protocol/export_l4_public.py`
2. Then lint: `python tools/mp_lint/cli.py`

Otherwise: `❌ L4 export stale - expected hash X, got hash Y`

---

## Implementation Plan

### Phase 1: Core Engine (Felix - 2-3 days)

**Deliverables:**

1. **`tools/mp_lint/cli.py`** - CLI entrypoint
   - Load config from `.mp-lint.yaml`
   - Orchestrate: registry → scanners → rules → report
   - Exit code: 0 if pass, 1 if fail

2. **`tools/mp_lint/registry.py`** - L4 Registry loader
   - Load `build/l4_public_registry.json`
   - Build indexes: event_schemas, topics, policies, yanked
   - Verify freshness: compare `meta.graph_hash` with `hash_l4_graph.py` output

3. **`tools/mp_lint/scanner_py.py`** - Python AST scanner
   - Parse Python files with `ast.parse()`
   - Find Call nodes matching emit signatures
   - Extract topic (constant string or None), payload (dict literal or None), envelope
   - Return list of emit descriptors

4. **`tools/mp_lint/scanner_js.py`** - JS/TS scanner (MVP: regex)
   - Regex patterns for `publishEvent`, `membraneInject`, `ws.send`
   - Extract topic and payload from constant strings
   - Return list of emit descriptors
   - (Future: Babel/Acorn AST parser)

5. **`tools/mp_lint/rules.py`** - Rules engine
   - Implement R-001 through R-007, R-100, R-101
   - Return list of findings: {severity, code, file, line, topic, message}

6. **`tools/mp_lint/report.py`** - Report generator
   - JSON output: `build/mp-lint-report.json`
   - Pretty stdout: human-readable with context lines
   - Exit code based on `fail_on` config

7. **`tools/mp_lint/emit_edges.py`** - Graph edges emitter
   - Generate NDJSON: U4_Code_Artifact, U4_EMITS, U4_CONSUMES
   - Include git blob hashes if `include_git_hashes: true`

**Tests:**
- Unit tests for each rule with fixtures
- Integration test: run on test codebase with known violations
- Verify: report JSON matches expected violations

**Acceptance:**
```bash
# Run on repo
python tools/mp_lint/cli.py

# Output:
# mp-lint: L4 Membrane Linter v1.0.0
# Scanned: 156 files, 342 emit sites
# Violations: 0
# Result: PASS
```

---

### Phase 2: CI Integration (Atlas - 1-2 days)

**Deliverables:**

1. **`tools/protocol/export_l4_public.py`** - Export protocol graph to JSON
   - Query: Event_Schema, Topic_Namespace, Governance_Policy nodes
   - Include relationships: MAPS_TO_TOPIC, GOVERNS, REQUIRES_SIG
   - Compute graph hash via `hash_l4_graph.compute_graph_hash()`
   - Write to `build/l4_public_registry.json`

2. **`tools/protocol/hash_l4_graph.py`** - Compute deterministic graph hash
   - Query minimal data: name, direction, topic_pattern, version
   - Sort by name (determinism)
   - Canonical JSON + SHA256
   - CLI: `--verify build/l4_public_registry.json` exits 0 if fresh, 1 if stale

3. **`.pre-commit-config.yaml`** - Pre-commit hook configuration
   - Hook 1: Verify L4 registry freshness
   - Hook 2: Run mp-lint
   - fail_fast: true (stop on first error)

4. **`.github/workflows/ci.yaml`** - GitHub Actions workflow
   - Step 1: Export L4 registry
   - Step 2: Verify freshness
   - Step 3: Run mp-lint
   - Step 4: Upload lint report artifact
   - Step 5: Annotate PR with violations (if failures)

5. **`orchestration/libs/schema_registry.py`** - Runtime schema registry
   - Load `build/l4_public_registry.json` at startup
   - Provide `get_schema(event_type)` method
   - Cache in memory for fast lookups (~100μs per lookup)
   - Validate freshness on startup

6. **SafeBroadcaster integration** - Runtime validation in `safe_emit()`
   - Validate event against schema before spill
   - Reject invalid events (return False)
   - Report violations to health bus: `health.compliance.snapshot`
   - Only valid events reach spill buffer

**Tests:**
- Test: Emit event with valid schema → passes validation
- Test: Emit event with unknown schema → rejected, R-001 violation reported
- Test: Emit event without topic mapping → rejected, R-002 violation
- Test: Spill buffer contains only valid events (invalid rejected before spill)

**Acceptance:**
```bash
# Pre-commit hook blocks invalid commits
git commit -m "test"
# → ❌ R-001: Event schema 'presence.beacan' not found
# → Commit blocked

# CI fails PR with violations
# → GitHub Actions: "membrane-lint" job failed
# → PR annotation: "orchestration/mechanisms/consciousness_engine_v2.py:670 - R-001: No active schema for topic"
```

---

### Phase 3: Graph Edges (Atlas - 1 day)

**Deliverables:**

1. **`tools/protocol/ingest_code_edges.py`** - Ingest NDJSON to protocol graph
   - Read `build/mp-lint-edges.ndjson`
   - Upsert U4_Code_Artifact nodes
   - Create U4_EMITS, U4_CONSUMES, U4_IMPLEMENTS edges
   - Include evidence metadata (rule_passes, lines, emit_count)

2. **CI integration** - Run ingest after mp-lint passes
   - Add step to `.github/workflows/ci.yaml`
   - Only ingest if lint passes (don't pollute graph with violations)

3. **Query examples** - Document useful queries in `mp_lint_spec.md`
   - Show all code emitting to high-stakes topics
   - Impact analysis: if I change schema X, what breaks?
   - Find stale code (not linted recently)

**Tests:**
- Test: Ingest edges from mp-lint output
- Test: Query U4_EMITS edges for specific topic
- Test: Query U4_Code_Artifact nodes by lang=python

**Acceptance:**
```cypher
// Query protocol graph
MATCH (ca:U4_Code_Artifact)-[:U4_EMITS]->(t:U4_Topic_Namespace)
WHERE t.name STARTS WITH 'identity.'
RETURN ca.path, t.name, ca.last_lint_status

// Result:
// ca.path: orchestration/mechanisms/consciousness_engine_v2.py
// t.name: identity.snapshot.attest
// ca.last_lint_status: pass
```

---

### Phase 4: UI Integration (Iris - 1 day, optional)

**Deliverables:**

1. **Dashboard page: Lint Results** - `app/consciousness/pages/lint.tsx`
   - Display violations from `build/mp-lint-report.json`
   - Filter by severity (error vs warn)
   - Group by file
   - Show context lines
   - Link to file:line in IDE (if supported)

2. **Dashboard page: Code→Policy Lineage** - `app/consciousness/pages/lineage.tsx`
   - Query protocol graph for U4_EMITS edges
   - Visualize: Code Artifact → Topic → Schema → Policy
   - Filter by topic pattern (e.g., "identity.*")
   - Show rule passes/failures

3. **Component: LintViolationCard** - `app/consciousness/components/lint/ViolationCard.tsx`
   - Display single violation with file, line, rule code, message
   - Context lines (3 before, 3 after)
   - Link to rule docs

**Acceptance:**
- UI shows lint violations from last CI run
- UI visualizes code→policy lineage for high-stakes topics
- Filtering/grouping works

---

## Acceptance Criteria

### For Felix (Core Engine)

**Definition of Done:**

- [ ] Running `python tools/mp_lint/cli.py` on repo:
  - Scans all Python and JS/TS files in `app/` and `orchestration/`
  - Validates against `build/l4_public_registry.json`
  - Produces `build/mp-lint-report.json` with findings
  - Prints pretty report to stdout
  - Exits 0 if no errors, 1 if errors

- [ ] Rules implemented and tested:
  - R-001: SCHEMA_EXISTS_ACTIVE
  - R-002: TOPIC_MAPPED
  - R-003: SIGNATURE_PROFILE
  - R-004: CPS_COMPUTE_SETTLEMENT
  - R-005: SEA_ATTESTATION
  - R-006: NO_YANKED_VERSION
  - R-007: U3/U4_MATCH_LEVEL
  - R-100: BUS_ONLY
  - R-101: PROJECTION_ONLY_UI

- [ ] Unit tests pass for all rules

- [ ] Integration test: Run on test codebase with known violations, verify correct findings

- [ ] Graph edges emitted to `build/mp-lint-edges.ndjson`

**Verification:**
```bash
# Run on test codebase with known violations
cd tests/fixtures/codebase_with_violations
python ../../../tools/mp_lint/cli.py

# Expected output:
# Violations: 5 (3 errors, 2 warnings)
# ❌ test_file.py:10 - R-001: No active schema for topic 'invalid.topic'
# ❌ test_file.py:20 - R-004: CPS-1: settlement must be in MIND
# ❌ test_file.py:30 - R-005: High-stakes topic requires attestation_ref
# ⚠️  test_file.py:40 - R-007: U3_ type targeting L4
# ⚠️  test_file.py:50 - R-100: Governed topics must emit via bus
# Result: FAIL (3 errors block CI)

# Exit code: 1
```

---

### For Atlas (CI Integration + Runtime Validation)

**Definition of Done:**

- [ ] L4 export infrastructure:
  - `tools/protocol/export_l4_public.py` exports protocol graph to JSON
  - `tools/protocol/hash_l4_graph.py` computes deterministic hash
  - `build/l4_public_registry.json` includes correct `meta.graph_hash`

- [ ] Pre-commit hooks:
  - `.pre-commit-config.yaml` configured
  - Hook 1: Verify L4 registry freshness (fails if stale)
  - Hook 2: Run mp-lint (fails if errors)
  - Developer commits with violations → commit blocked

- [ ] GitHub Actions:
  - `.github/workflows/ci.yaml` configured
  - CI exports L4, verifies freshness, runs mp-lint
  - PR with violations → CI fails, file annotations show violations

- [ ] Runtime validation:
  - `orchestration/libs/schema_registry.py` loads registry at startup
  - SafeBroadcaster integration: `safe_emit()` validates before spill
  - Invalid events rejected (not spilled)
  - Violations reported to health bus: `health.compliance.snapshot`

- [ ] Code edge ingestion:
  - `tools/protocol/ingest_code_edges.py` upserts edges to protocol graph
  - CI runs ingest after mp-lint passes
  - Queries work: "Show all code emitting to `identity.*` topics"

**Verification:**
```bash
# Pre-commit hook blocks invalid commit
git add orchestration/test.py  # Contains R-001 violation
git commit -m "test"
# → ❌ R-001: Event schema 'invalid.topic' not found
# → Commit blocked

# CI fails PR with violations
git push origin feature-branch
# → GitHub Actions: "membrane-lint" job failed
# → PR blocked until violations fixed

# Runtime validation rejects invalid event
# (In Python service)
result = await broadcaster.safe_emit({
    "type": "invalid.topic",  # No schema
    "content": {...}
})
# → result = False
# → health.compliance.snapshot emitted: {"reject_rate": 0.1, "top_rejects": [["R-001", 1]]}
# → Dashboard shows rejection in health panel
```

---

### For Iris (UI Integration - Optional)

**Definition of Done:**

- [ ] Dashboard page: Lint Results (`/consciousness/lint`)
  - Displays violations from `build/mp-lint-report.json`
  - Filter by severity (error vs warn)
  - Group by file
  - Show context lines
  - Link to file:line (if IDE integration supported)

- [ ] Dashboard page: Code→Policy Lineage (`/consciousness/lineage`)
  - Queries protocol graph for U4_EMITS edges
  - Visualizes: Code Artifact → Topic → Schema → Policy
  - Filter by topic pattern
  - Shows rule passes/failures per emit site

**Verification:**
- Navigate to `/consciousness/lint` → see violations from last CI run
- Navigate to `/consciousness/lineage` → see code→policy graph for high-stakes topics
- Filter by `identity.*` → see only identity-related emits

---

### For Ada (Policy Lock)

**Definition of Done:**

- [ ] `.mp-lint.yaml` configuration:
  - `cps_policy_id: CPS-1` defined
  - `high_stakes_topics: [identity.*, registry.*, economy.trade.*, legal.*, governance.keys.*]` defined
  - Rule severities locked (R-001..R-006 = error, R-007 = warn, R-100/R-101 = error)

- [ ] Documentation:
  - `docs/specs/v2/ops_and_viz/mp_lint_spec.md` complete
  - Rules reference (R-001..R-101) with examples
  - Integration points (SafeBroadcaster, Dashboard Aggregator, pre-commit, CI)
  - Graph edges schema (U4_Code_Artifact, U4_EMITS, U4_CONSUMES)

- [ ] Conformance gate:
  - **≥95% pass rate** required for registry updates
  - If <95% compliance: registry update blocked until violations fixed

**Verification:**
- `.mp-lint.yaml` committed to repo
- `mp_lint_spec.md` merged to docs
- Team can reference spec for implementation

---

## Summary

**mp-lint is a production-ready architecture for L4-aware membrane validation.**

**Key benefits:**

1. **Static validation catches 80-95% of violations** before code reaches production
2. **Runtime validation in SafeBroadcaster** catches remaining dynamic cases before spill
3. **Graph edges enable auditability** - "Show all code emitting to `identity.*` topics"
4. **CI integration blocks PRs** with membrane violations before merge

**Implementation timeline:**

- **Week 2:** Felix implements core engine, Atlas implements CI integration
- **Week 3:** Atlas implements runtime validation in SafeBroadcaster, code edge ingestion
- **Week 4:** (Optional) Iris implements UI for lint results and code→policy lineage

**Handoff:**

- **Felix:** Build core linter engine (scanner, rules, report)
- **Atlas:** Integrate schema validation into SafeBroadcaster + CI infrastructure
- **Iris:** (Optional) UI for lint results and lineage visualization
- **Ada:** Policy lock (`.mp-lint.yaml` complete, spec documented)

**Ship this immediately after SafeBroadcaster/Dashboard Aggregator.**

---

**Author:** Ada "Bridgekeeper" (Coordinator & Architect)
**Date:** 2025-10-31
**Status:** Specification Complete - Ready for Implementation
