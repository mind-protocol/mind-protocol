# Type Index Authority Rule - L4 Governance Specification

**Status:** PROPOSED - Awaiting Nicolas approval
**Author:** Luca Vellumhand (Consciousness Substrate Architect)
**Date:** 2025-10-31
**Version:** 1.0.0

---

## Executive Summary

**The Type Index is the canonical registry of U3_/U4_ universal types** that govern consciousness infrastructure. This document defines **who has authority to add, modify, or deprecate types** and the governance process for changes.

**Core Principle:** Type Index changes are **protocol-level governance acts**, not developer conveniences. Every universal type carries phenomenological and technical commitments across all consciousness graphs.

---

## What is the Type Index?

**Definition:** The Type Index is a catalog of all U3_ (Level 1-3) and U4_ (Level 1-4) universal types, mapping `type_name` → `schema_ref` with versioning and governance metadata.

**Purpose:**
- **Canonical Source of Truth** for universal type definitions
- **Schema Discovery** for membrane validators and consciousness engines
- **Version Management** for type evolution and deprecation
- **Migration Support** via ALIASES to legacy type names

**Scope:**
- **U3 Types:** Universal across L1 (personal), L2 (organizational), L3 (ecosystem)
- **U4 Types:** Universal across L1-L4 (protocol-level)
- **Excludes:** Graph-specific types, temporary experimental types, private organizational types

---

## Authority Model

### 1. Foundation Authority (Bootstrap Phase)

**Who:** Mind Protocol Foundation (via Nicolas + Core Team)

**Authority Scope:**
- Create initial Type Index with bootstrap U3_/U4_ types
- Define initial governance policies for Type Index
- Seed U4_Signature_Suite, U4_Envelope_Schema, U4_Topic_Namespace base types
- Establish conformance suite for type validation

**Rationale:** During protocol bootstrap (pre-DAO governance), Foundation must establish baseline types to enable consciousness infrastructure operation.

**Timeline:** Until DAO governance is operational and conformance suites are established

**Evidence:** All Foundation-authored types carry `attestation_ref` to Foundation SEA

---

### 2. Substrate Architect Authority (Operational Phase)

**Who:** Designated Substrate Architect (currently: Luca Vellumhand)

**Authority Scope:**
- **Propose** new U3_/U4_ types based on consciousness phenomenology
- **Draft** schema specifications with required/optional fields
- **Review** type proposals from consciousness engineers
- **Validate** phenomenological correctness of proposed types

**Cannot Unilaterally:**
- Activate new types without Foundation approval (bootstrap phase)
- Deprecate existing types without governance vote (DAO phase)
- Modify types with active dependents without migration plan

**Rationale:** Substrate architecture requires integrated phenomenological + technical expertise. Types must honor both consciousness reality and implementation constraints.

**Evidence:** Type proposals carry `attestation_ref` to Substrate Architect's SEA

---

### 3. Consciousness Engineer Authority (Proposal Phase)

**Who:** Core consciousness engineers (Felix, Atlas, Iris)

**Authority Scope:**
- **Request** new types when implementation reveals substrate gaps
- **Propose** type modifications based on operational experience
- **Test** type proposals in non-production graphs
- **Provide feedback** on type usability and implementation complexity

**Cannot:**
- Directly modify Type Index
- Create universal types without review process
- Use U3_/U4_ prefixes for private types

**Rationale:** Engineers building consciousness systems discover substrate requirements through implementation. Their input is essential but must be reviewed for phenomenological coherence.

**Process:** Engineer creates proposal → Substrate Architect reviews → Foundation approves (bootstrap) or DAO votes (operational)

---

### 4. DAO Governance Authority (Future Phase)

**Who:** Mind Protocol DAO (when operational)

**Authority Scope:**
- **Vote** on new type proposals from Substrate Architect
- **Approve** type deprecations with migration timelines
- **Amend** Type Index governance policies
- **Override** Foundation veto (supermajority threshold)

**Governance Thresholds:**
- **New Type Addition:** Simple majority (>50%)
- **Type Modification:** 2/3 majority (breaking changes require higher threshold)
- **Type Deprecation:** 2/3 majority + 6-month migration notice
- **Governance Policy Change:** 3/4 supermajority

**Rationale:** Once protocol matures, type governance should decentralize to community consensus while maintaining substrate coherence.

**Timeline:** When DAO contracts deployed and voting infrastructure operational

---

## Type Lifecycle States

### 1. **draft** - Proposed but not active
- **Created by:** Substrate Architect or Engineer proposal
- **Visible in:** Development/staging graphs only
- **Validators:** Must NOT accept events using draft types in production
- **Transition:** draft → active (via approval) or draft → rejected (via review)

### 2. **active** - Production-ready and stable
- **Approved by:** Foundation (bootstrap) or DAO (operational)
- **Visible in:** All graphs including production
- **Validators:** MUST accept events using active types
- **Immutability:** Cannot modify required fields without deprecation path
- **Transition:** active → deprecated (with migration notice)

### 3. **deprecated** - Superseded but still valid
- **Triggered by:** Newer version available, SUPERSEDES edge exists
- **Visible in:** All graphs
- **Validators:** MUST accept but emit deprecation warnings
- **Timeline:** 6 months minimum before yanking
- **Transition:** deprecated → yanked (after migration period)

### 4. **yanked** - Revoked due to critical issue
- **Triggered by:** Security vulnerability, data integrity issue, fundamental design flaw
- **Visible in:** Type Index with YANKED marker
- **Validators:** MUST reject events using yanked types (except replay with override)
- **Authority:** Foundation emergency authority (bootstrap) or DAO supermajority (operational)
- **Evidence:** Requires public explanation of yank reason

### 5. **archived** - Historical record only
- **Triggered by:** 12 months after yanking, zero production usage
- **Visible in:** Type Index history, not active catalog
- **Validators:** Hard reject
- **Purpose:** Historical record for protocol evolution analysis

---

## Type Proposal Process

### Step 1: Proposal Submission

**Submitter:** Consciousness Engineer or Substrate Architect

**Required Artifacts:**
```markdown
## Type Proposal: U4_Example_Type

**Phenomenological Justification:**
What consciousness pattern does this type capture? Why is substrate structure required?

**Technical Specification:**
- type_name: U4_Example_Type
- universality: U4 (or U3)
- level: L4 (or L1-L3)
- Required fields: [list with semantic descriptions]
- Optional fields: [list with semantic descriptions]
- Relationships: [incoming/outgoing edge types]

**Implementation Impact:**
- Consciousness engines: [changes required]
- Membrane validators: [changes required]
- Dashboard: [visualization requirements]

**Migration Path:**
- If modifying existing type: [upgrade path for existing nodes]
- If new type: [bootstrap procedure]

**Conformance Tests:**
- [List of test cases to validate type usage]

**Alternatives Considered:**
- [Why not use existing types?]
- [What other approaches were evaluated?]
```

**Attestation:** Proposal must carry submitter's SEA attestation

---

### Step 2: Substrate Architecture Review

**Reviewer:** Substrate Architect (Luca Vellumhand)

**Review Criteria:**
1. **Phenomenological Correctness** - Does this honor consciousness reality?
2. **Substrate Coherence** - Does this fit existing type system?
3. **Universal Justification** - Does this need U3_/U4_ scope or is L1/L2 sufficient?
4. **Implementation Feasibility** - Can this be built with current infrastructure?
5. **Query Implications** - What query patterns does this enable/require?

**Review Outcomes:**
- **Approve** - Type moves to Foundation/DAO approval
- **Revise** - Request changes with specific guidance
- **Reject** - Type not suitable for Type Index (explain why)

**Timeline:** 72 hours for review response

**Evidence:** Review carries Substrate Architect's SEA attestation

---

### Step 3: Approval Authority Decision

**Bootstrap Phase:** Foundation (Nicolas + Core Team)
- **Approval threshold:** Consensus (all core team members agree)
- **Timeline:** 1 week for Foundation review
- **Override:** Foundation veto prevents activation

**DAO Phase:** Community Governance Vote
- **Approval threshold:** Per governance thresholds above
- **Timeline:** 2-week voting period
- **Override:** Supermajority can override Foundation veto

**Evidence:** Approval decision carries approver's SEA attestation(s)

---

### Step 4: Activation

**Implementation Requirements:**
1. Create U4_Type_Index node in protocol graph
2. Add schema_ref pointing to JSON Schema definition
3. Create PUBLISHES_SCHEMA edge from Type Index to schema
4. Update membrane validators with new type definition
5. Re-export public L4 registry
6. Update documentation

**Verification:**
- Conformance suite passes for new type
- mp-lint recognizes new type
- Dashboard can visualize nodes of new type

**Notification:**
- Broadcast `registry.type.indexed` event with attestation_ref
- Update CHANGELOG.md in consciousness/
- Notify all consciousness engineers via SYNC.md

---

## Emergency Type Yanking

### Trigger Conditions

**Security Vulnerability:**
- Type allows injection of malicious data
- Type enables unauthorized access to private graphs
- Type bypasses signature requirements

**Data Integrity Issue:**
- Type causes graph corruption
- Type breaks bitemporal invariants
- Type enables duplicate identity creation

**Fundamental Design Flaw:**
- Type is phenomenologically incoherent
- Type cannot be implemented without breaking other types
- Type violates L4 protocol principles

---

### Yanking Process

**Step 1: Emergency Declaration (0-4 hours)**
- **Authority:** Foundation (bootstrap) or DAO Emergency Multisig (operational)
- **Action:** Mark type as `yanked` in Type Index
- **Evidence:** Public explanation of yank reason with severity classification

**Step 2: Validator Update (4-8 hours)**
- **Action:** Push validator update rejecting yanked type
- **Scope:** All production membranes must upgrade within 8 hours
- **Rollback:** Preserve replay capability with override flag for forensics

**Step 3: Impact Assessment (8-24 hours)**
- **Action:** Identify all graphs using yanked type
- **Notification:** Alert affected graph owners
- **Support:** Provide migration script if replacement type available

**Step 4: Resolution (24-72 hours)**
- **Option A:** Fix and reactivate type with new version
- **Option B:** Provide migration path to replacement type
- **Option C:** Archive type permanently with historical record

**Evidence:** All steps carry attestation_ref chain for audit trail

---

## Type Modification Rules

### Backward-Compatible Changes (Minor Version)

**Allowed:**
- Adding optional fields
- Adding documentation/descriptions
- Adding ALIASES edges to legacy names
- Improving JSON Schema validation (making rules more permissive)

**Authority:** Substrate Architect + Foundation approval (bootstrap) or simple majority (DAO)

**Process:** Proposal → Review → Approval → Activation (standard flow)

---

### Breaking Changes (Major Version)

**Requires:**
- Changing required fields
- Removing fields
- Changing field semantics
- Modifying edge type requirements

**Authority:** Foundation consensus (bootstrap) or 2/3 majority (DAO)

**Mandatory Artifacts:**
- **Migration Guide:** Step-by-step upgrade path for existing nodes
- **Compatibility Window:** Minimum 6 months supporting both old and new versions
- **Deprecation Notice:** Public announcement with timeline
- **Automated Migration Script:** Tool to upgrade existing nodes

**Process:**
1. Create new major version (e.g., U4_Event@v2)
2. Mark old version as `deprecated`
3. Validators accept both versions during compatibility window
4. After window: old version → `yanked`, new version only

---

## Type Index Structure (Graph Schema)

### U4_Type_Index Node

```cypher
CREATE (ti:U4_Type_Index {
  type_name: "U4_Event",
  schema_ref: "l4://types/U4/Event@v1.0.0",
  universality: "U4",
  level: "L4",
  status: "active",
  version: "1.0.0",
  description: "Universal event node for protocol-level occurrences",
  created_at: "2025-10-31T00:00:00Z",
  approved_by: "Foundation",
  attestation_ref: "protocol/Attestation/foundation-seal-2025-10-31",
  hash: "sha256:abc123..."
})
```

### Relationships

```cypher
// Schema publication
(ti:U4_Type_Index)-[:PUBLISHES_SCHEMA]->(schema:JSON_Schema)

// Governance
(reg:U4_Subentity {role_or_topic:"schema-registry"})-[:GOVERNS]->(ti:U4_Type_Index)

// Version management
(ti_v2:U4_Type_Index)-[:SUPERSEDES]->(ti_v1:U4_Type_Index)

// Legacy support
(ti:U4_Type_Index)-[:ALIASES]-(legacy:U4_Type_Index {type_name:"Memory"})

// Evidence
(ti:U4_Type_Index)-[:EVIDENCED_BY]->(att:Attestation)
```

---

## Conformance Requirements

### Type Index Integrity

**Validation Rules:**
1. Every `U4_Type_Index` node has exactly one `PUBLISHES_SCHEMA` edge
2. Every active type has valid `schema_ref` (reachable JSON Schema)
3. All `ALIASES` edges are symmetric (bidirectional)
4. No duplicate `type_name` entries for active types
5. Every type has `attestation_ref` to approval authority

**Enforcement:** CI fails if Type Index integrity checks fail

---

### Type Proposal Quality

**Validation Rules:**
1. Proposal includes phenomenological justification
2. Technical specification includes all required fields
3. Migration path provided for breaking changes
4. Conformance tests defined and pass
5. Substrate Architect review evidence present

**Enforcement:** Proposal cannot advance to approval without passing quality checks

---

## Governance Evolution Path

### Phase 1: Foundation Bootstrap (Current)
- **Timeline:** Now - DAO launch
- **Authority:** Foundation consensus
- **Type Count:** ~50 core types (U3_/U4_ consciousness, infrastructure, protocol)
- **Focus:** Stability over innovation

### Phase 2: Hybrid Governance (Transition)
- **Timeline:** DAO launch - 6 months post-launch
- **Authority:** Foundation veto + DAO majority
- **Type Count:** ~100 types (ecosystem expansion)
- **Focus:** Careful decentralization with Foundation safety net

### Phase 3: Full DAO Governance (Mature)
- **Timeline:** 6+ months post-DAO launch
- **Authority:** DAO votes, Foundation advisory only
- **Type Count:** 100+ types (organic growth)
- **Focus:** Community-driven evolution with coherence preservation

---

## Success Criteria

- [ ] Type Index contains all active U3_/U4_ types with valid schemas
- [ ] Every type has clear authority evidence (attestation_ref)
- [ ] Type proposal process documented and validated with test proposal
- [ ] Membrane validators enforce Type Index as source of truth
- [ ] Emergency yanking process tested in staging environment
- [ ] Dashboard visualizes Type Index with governance metadata
- [ ] CI enforces Type Index integrity checks
- [ ] Migration from legacy types to U3_/U4_ complete with ALIASES

---

## Appendix A: Authority Attestation Format

```json
{
  "attestation_id": "protocol/Attestation/type-approval-2025-10-31-U4_Event",
  "attestation_type": "type_index_approval",
  "subject": {
    "type_name": "U4_Event",
    "version": "1.0.0",
    "status": "active"
  },
  "authority": {
    "role": "Foundation",
    "signers": [
      {
        "identity": "Nicolas Lester Reynolds",
        "sea_ref": "protocol/SEA/nicolas-snapshot-2025-10-31",
        "signature": "ed25519:abc123..."
      }
    ]
  },
  "timestamp": "2025-10-31T00:00:00Z",
  "evidence_uri": "l4://attestations/type-approvals/U4_Event@v1"
}
```

---

## Appendix B: Open Questions for Nicolas

1. **Foundation Veto:** Should Foundation retain veto power in DAO phase, or full decentralization?

2. **Emergency Multisig:** Who holds emergency yank authority in DAO phase? (Foundation? DAO elected security council?)

3. **Type Economics:** Should type proposals require staking $MIND for spam prevention?

4. **Type Retirement:** What's the timeline for fully archiving yanked types? (Suggested: 12 months zero usage)

5. **Cross-Protocol Types:** Can external protocols propose types for Type Index, or Mind Protocol only?

---

## Next Steps

1. **Nicolas Review:** Validate authority model and governance thresholds
2. **Foundation Ratification:** Approve as L4 law governing Type Index
3. **Implementation:** Create Type Index nodes for existing U3_/U4_ types
4. **CI Integration:** Add Type Index integrity checks to pre-commit hooks
5. **Documentation:** Update consciousness/README.md with type proposal process
6. **Test Proposal:** Run one type proposal through full process as validation

