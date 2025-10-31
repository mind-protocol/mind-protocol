# L4 Schema Registry - Protocol Subsystem Specification

**Status:** PROPOSED - Awaiting Luca (substrate architect) review
**Author:** Nicolas (via Ada coordination)
**Date:** 2025-10-31
**Version:** 0.1.0 (draft)

---

## What it is (one sentence)

**L4 Schema Registry = an authoritative U4 Subentity that publishes versioned schemas, policies, and signature suites which the membrane must honor at accept-time.**

---

## Core Principle

Treat the schema registry as **law about messages**: the membrane enforces whatever the L4 registry declares valid. This elevates schema from internal tooling to protocol-level governance.

---

## Nodes (all are `universality="U4"` and `level="L4"`)

### Registry Root

**`U4_Subentity(entity_kind="functional", role_or_topic="schema-registry")`**

- `subsystem_id: "schema-registry"`
- `name: "L4 Schema Registry"`
- `scope: "protocol"`
- Links: `GOVERNS` everything below

### Schema Management

**`U4_Schema_Bundle`** (logical release)

- `semver` (string) - Semantic version (e.g., "1.2.0")
- `uri` (string) - URI to bundle (e.g., "l4://schemas/bundle/1.2.0")
- `hash` (string) - Content hash for integrity
- `status` (enum) - `draft | active | deprecated | yanked`
- Links:
  - `PUBLISHES_SCHEMA` → `U4_Event_Schema | U4_Envelope_Schema | U4_Type_Index | U4_Topic_Namespace`
  - `SUPERSEDES` → older `U4_Schema_Bundle`
  - `DEPRECATES` → deprecated `U4_Schema_Bundle`

**`U4_Event_Schema`** (event payload schema)

- `schema_uri` (string) - URI to JSON Schema
- `version` (string) - Schema version
- `hash` (string) - Schema content hash
- `compat` (array) - Compatible semver ranges
- Links:
  - `MAPS_TO_TOPIC` → `U4_Topic_Namespace`
  - `REQUIRES_SIG` → `U4_Signature_Suite`
  - `GOVERNED_BY` ← `U4_Subentity(schema-registry)`

**`U4_Envelope_Schema`** (envelope wrapper schema)

- Same fields as `U4_Event_Schema`
- Links: Same as `U4_Event_Schema`

**`U4_Topic_Namespace`** (topic categorization)

- `name` (string) - Topic pattern (e.g., `identity.*`, `economy.*`, `mission.*`)
- Links: `GOVERNED_BY` ← registry

**`U4_Type_Index`** (catalog for U3/U4 types)

- `type_name` (string) - e.g., `U4_Event`, `U3_Pattern`
- `schema_ref` (string) - e.g., `l4://types/U4/Event@v1`
- `universality` (enum) - `U3 | U4`
- Links:
  - `PUBLISHES_SCHEMA` → the JSON Schema
  - `ALIASES` ↔ legacy type names (for migration support)

### Signature & Security

**`U4_Signature_Suite`** (signature requirements)

- `suite_id` (string) - Unique identifier
- `algo` (string) - Algorithm (e.g., `ed25519`, `secp256k1`)
- `hash_algos` (array) - Supported hash algorithms
- Links: `CERTIFIES_CONFORMANCE` ← `U4_Conformance_Suite`

### Governance

**`U4_Governance_Policy`** (protocol policy)

- `policy_id` (string) - Policy identifier (e.g., "CPS-1")
- `uri` (string) - Pointer to policy document
- `hash` (string) - Policy content hash
- Links: `GOVERNS` → topics/schemas

### Conformance Testing

**`U4_Conformance_Suite`** (test suite definition)

- `semver` (string) - Suite version
- `cases` (array) - Test case definitions
- Links: `CERTIFIES_CONFORMANCE` → targets being tested

**`U4_Conformance_Result`** (test execution result)

- `subject_ref` (string) - What was tested
- `pass_rate` (float) - Percentage passed (0.0-1.0)
- `timestamp` (datetime) - When test ran
- `proof_uri` (string) - Link to detailed results
- Links: `EVIDENCED_BY` → `Attestation`

> **Universal Headers:** All nodes carry `visibility`, `commitments[]`, `proof_uri`, and bitemporal fields per universal type specification.

---

## Links (U4 unless noted)

- **`U4_GOVERNS`** - `Subentity(registry) → {Schema_Bundle|Policy|Topic_Namespace|Type_Index}`
- **`U4_PUBLISHES_SCHEMA`** - `Schema_Bundle|Type_Index → {Event_Schema|Envelope_Schema|JSON_Schema}`
- **`U4_MAPS_TO_TOPIC`** - `Event_Schema|Envelope_Schema → Topic_Namespace`
- **`U4_REQUIRES_SIG`** - `Event_Schema|Envelope_Schema → Signature_Suite`
- **`U4_CERTIFIES_CONFORMANCE`** - `Conformance_Suite → {Signature_Suite|Schema_Bundle|Topic_Namespace}`
- **`U4_SUPERSEDES`** - `Schema_Bundle → Schema_Bundle` (linear or DAG)
- **`U4_DEPRECATES`** - `Schema_Bundle → Schema_Bundle`
- **`U4_ALIASES`** - `Type_Index ↔ Type_Index` (for legacy names, symmetric)
- **`U4_EVIDENCED_BY`** - `Any → Attestation`

---

## Runtime Invariants (Membrane Enforcement)

### 1. Accept-Time Resolution
Any inbound envelope **must** declare `schema_uri@version`. The validator resolves it from L4; cache ok, but cache entries must be **anchored to the bundle hash**.

### 2. Topic Legality
`MAPS_TO_TOPIC` must exist for the schema used; else reject.

### 3. Signature Profile
Envelope must satisfy the `REQUIRES_SIG` for its schema; else reject.

### 4. Policy Binding
If a topic has a governing `Governance_Policy` (e.g., CPS for compute), the inject must meet it (e.g., $MIND settlement fields present and valid); else reject.

### 5. Conformance Gates
A schema version marked `yanked` fails validation unless a per-policy override exists for replay.

---

## Lifecycle Events (all U4_Event)

- `registry.schema.published` → `Schema_Bundle`
- `registry.schema.deprecated` / `registry.schema.yanked`
- `registry.type.indexed` (new/updated U3|U4 type)
- `policy.amended` → `Governance_Policy`
- `suite.released` / `suite.result.recorded`

Each carries an **attestation_ref** to a SEA snapshot (so high-stakes registry updates are verifiable) and emits **commitments** for public proof without leaking private reviewer notes.

---

## Public vs Private (Record-Public / Field-Private Rule)

### Public Read-Replica Exposes:

- Registry subentity header
- Bundle headers (id, semver, status, hash)
- Schema **URIs and text** (schemas should be public)
- Topic namespaces, signature suite IDs
- Policy headers (id, hash), not necessarily full prose if sensitive
- Conformance suite headers + aggregate pass rates

### Governance-Only:

- Reviewer identities/PII
- Draft notes
- Private test fixtures
- Internal deliberation records

---

## Minimal Queries (Sanity & Ops)

### List active event schemas with topics and sig suites

```cypher
MATCH (b:U4_Schema_Bundle {status:"active"})-[:PUBLISHES_SCHEMA]->(s:U4_Event_Schema)
OPTIONAL MATCH (s)-[:MAPS_TO_TOPIC]->(t:U4_Topic_Namespace)
OPTIONAL MATCH (s)-[:REQUIRES_SIG]->(sig:U4_Signature_Suite)
RETURN s.schema_uri, s.version, t.name AS topic, sig.suite_id;
```

### What governs compute payment?

```cypher
MATCH (p:U4_Governance_Policy {policy_id:"CPS-1"})-[:GOVERNS]->(t:U4_Topic_Namespace)
RETURN p.policy_id, collect(t.name) AS topics;
```

### Which bundles are deprecated and superseded by what?

```cypher
MATCH (old:U4_Schema_Bundle {status:"deprecated"})-[:SUPERSEDES]->(new:U4_Schema_Bundle)
RETURN old.semver, new.semver, new.hash;
```

### Conformance health

```cypher
MATCH (r:U4_Conformance_Result)-[:EVIDENCED_BY]->(a:Attestation)
RETURN r.subject_ref, r.pass_rate, r.ts, a.attestation_id
ORDER BY r.ts DESC LIMIT 20;
```

---

## Conformance Checks for Ingestion (Ada/Luca Acceptance)

### Schema Integrity:
- Every `U4_Event_Schema` has exactly one `MAPS_TO_TOPIC`
- Every `U4_Envelope_Schema` has `REQUIRES_SIG`
- All inbound topics referenced by schemas exist as `U4_Topic_Namespace`

### Bundle State:
- All `active` bundles are reachable from the registry subentity via `GOVERNS / PUBLISHES_SCHEMA`
- No `yanked` bundle appears in the validator cache snapshot

### Type Registry:
- Type index is bijective for current U3/U4 types (`type_name` ↔ `schema_ref`)
- All `ALIASES` edges are symmetric

### Governance:
- Every governed topic has at least one policy
- Policy hashes match document content

---

## Migration (from existing `schema_registry` graph)

### Phase 1: Promote Registry Root
1. **Promote** current registry root to `U4_Subentity(entity_kind="functional", role_or_topic="schema-registry")`
2. Set `scope: "protocol"`, `level: "L4"`, `universality: "U4"`

### Phase 2: Schema Versioning
3. **Wrap** existing schema versions as `U4_Schema_Bundle` nodes
4. Attach `PUBLISHES_SCHEMA` edges to current schemas

### Phase 3: Topic Normalization
5. **Normalize** topics as `U4_Topic_Namespace` nodes
6. Connect with `MAPS_TO_TOPIC` edges

### Phase 4: Type Index
7. **Introduce** `U4_Type_Index` nodes for U3/U4 types
8. Add `ALIASES` edges to legacy type names (Memory → U4_Event, etc.)

### Phase 5: Signature Profiles
9. **Lift** signature profiles to `U4_Signature_Suite` nodes
10. Add `REQUIRES_SIG` edges

### Phase 6: Governance
11. **Move** governance docs to `U4_Governance_Policy` nodes
12. Connect via `GOVERNS` edges

### Phase 7: Conformance
13. **Backfill** `U4_Conformance_Suite/Result` from CI runs (even stub passes for now)

> **No tokenomics touched.** This is a graph-only change with membrane payoffs: deterministic validation, better public proofs, and cleaner UI.

---

## UI Affordance (Dashboard)

Render L4 as a **gallery of U4 Subentities**:
- `schema-registry` (this spec)
- `SEA` (Identity & Attestation)
- `CPS` (Compute Payment)
- `UBC` (Universal Basic Compute)
- `RGS` (Registries)
- `AGL` (Autonomy Gates)

Clicking **Schema Registry** shows:
- Bundles → Schemas → Topics → Sig Suites
- Green "Validator in sync ✅ / drift ❌" badge sourced from `U4_Conformance_Result`
- Timeline of `registry.*` events

---

## Open Questions for Luca

1. **Storage Model:** Should `U4_Schema_Bundle`, `U4_Event_Schema`, etc. be new node types in `complete_schema_data.py`, or should we reuse existing universal types with type-specific metadata?

2. **Schema Text Storage:** Where do we store actual JSON Schema text? In node properties (large text fields), or as separate documents with URIs?

3. **Cache Semantics:** What's the membrane's cache invalidation strategy when a bundle is yanked or deprecated?

4. **Type Index Bootstrap:** Should the type index be auto-generated from `complete_schema_data.py`, or manually curated?

5. **Conformance Triggers:** Should conformance tests run on every schema change, or on-demand?

6. **Privacy Model:** Which fields on `U4_Governance_Policy` should be commitment-only vs fully private?

---

## Next Steps

1. **Luca Review:** Schema architect validates substrate design, answers open questions
2. **Nicolas Approval:** Confirm this aligns with protocol vision and L4 law model
3. **Prototype:** Create seed data for one subsystem (schema-registry) as proof of concept
4. **Membrane Integration:** Update membrane validator to query L4 registry at accept-time
5. **Dashboard:** Add L4 subsystem gallery view

---

## Success Criteria

- [ ] All U4_Event schemas discoverable via L4 queries
- [ ] Membrane rejects events with invalid schema references
- [ ] Dashboard shows schema registry as protocol subsystem
- [ ] Public graph replica exposes schema metadata without governance data
- [ ] Type index provides migration path from legacy to universal types
- [ ] Conformance results visible in dashboard with green/red badges
