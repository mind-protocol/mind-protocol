# Complete Schema Data Audit Response & Migration Plan

**Status:** APPROVED - Ready for implementation
**Auditor:** Nicolas Lester Reynolds
**Responder:** Luca Vellumhand (Consciousness Substrate Architect)
**Date:** 2025-10-31
**Version:** 1.0.0

---

## Executive Summary

**Nicolas's audit identifies 24 concrete issues in `complete_schema_data.py`** - every one is valid and represents substrate coherence debt that must be paid.

**Validation:** All 24 issues confirmed as substrate violations requiring surgical fixes.

**Migration Strategy:** Staged refactor with backward-compatibility window, CI enforcement, and comprehensive documentation.

**Timeline:** 2-week sprint with 3 phases (Core fixes → Link taxonomy → KO + Membrane)

---

## I. Audit Validation (Issue-by-Issue)

### A) Structural / Schema-Wide Problems ✅ ALL VALID

#### Issue 1: `node_type` → `type_name` (CRITICAL)

**Nicolas's Finding:** File uses `node_type` as primary type property; our standard is `type_name == label`

**Luca's Validation:** ✅ **CORRECT - CRITICAL FIX REQUIRED**

**Phenomenological Impact:**
- Current state breaks type_name ↔ label coherence (our locked standard from 2025-10-31 03:00)
- U4 naming lint would fail on nodes created from this schema
- Type Index lookups would break (they query on `type_name`)

**Technical Impact:**
- All node creation code uses wrong property name
- Query patterns assume `type_name` exists
- JSON exports/imports would fail type validation

**Fix Priority:** **P0 - BLOCKING** (breaks Type Index, breaks lint)

**Migration:**
```python
# Before
"core_identity": [
    {"name": "node_type", "type": "string", "required": True}
]

# After
"core_identity": [
    {"name": "type_name", "type": "string", "required": True, "read_only": True,
     "description": "Canonical node class name; must equal primary label"}
]
```

---

#### Issue 2: Level notation `n1|n2|n3|shared` → `L1|L2|L3|L4` + `U3/U4` (CRITICAL)

**Nicolas's Finding:** Many nodes use `n1|n2|n3|shared` instead of `L1-L4` + universality

**Luca's Validation:** ✅ **CORRECT - CRITICAL FIX REQUIRED**

**Phenomenological Impact:**
- `n1/n2/n3` notation is implementation artifact, not consciousness architecture concept
- `shared` is ambiguous - does it mean U3 (L1-L3) or U4 (L1-L4)?
- Breaks level-based queries and U4 naming lint rules

**Technical Impact:**
- U4 naming lint checks for `level IN ['L1','L2','L3','L4']` - would fail
- Conformance tests expect standard level notation
- Cross-level queries wouldn't work

**Fix Priority:** **P0 - BLOCKING** (breaks lint, breaks queries)

**Mapping Table:**
```
n1       → level: "L1", universality: null (or omit)
n2       → level: "L2", universality: null
n3       → level: "L3", universality: null
shared   → level: "L1-L4", universality: "U3" or "U4" (depends on node type)
```

**Decision Rule for `shared`:**
- If used at protocol level (L4) → `universality: "U4"`
- If only personal/org/ecosystem (L1-L3) → `universality: "U3"`

---

#### Issue 3: Missing U4_/U3_ prefixes for link types (CRITICAL)

**Nicolas's Finding:** Links use bare names (`MEMBER_OF`, `GOVERNS`) without universal prefixes

**Luca's Validation:** ✅ **CORRECT - CRITICAL FIX REQUIRED**

**Phenomenological Impact:**
- Link types are consciousness relationships with scope commitments
- `U4_` prefix declares "this relationship is universal across all scales including protocol"
- Without prefix, links are ambiguous and ungovernable

**Technical Impact:**
- Type Index cannot catalog unprefixed links
- Conformance tests expect U4_/U3_ prefixes
- Graph queries become ambiguous (which `MEMBER_OF`? L1 or L4?)

**Fix Priority:** **P0 - BLOCKING** (breaks Type Index, breaks governance)

**Example:**
```python
# Before
"MEMBER_OF": {"description": "Composition relationship", ...}

# After
"U4_MEMBER_OF": {
    "universality": "U4",
    "reverse_name": "U4_HAS_MEMBER",
    "description": "Composition relationship (DAG; child.level ≤ parent.level)",
    ...
}
```

---

#### Issue 4: Missing defaults and system-set field markers (HIGH)

**Nicolas's Finding:** No `default`, `set_by`, `read_only`, `computed` metadata

**Luca's Validation:** ✅ **CORRECT - HIGH PRIORITY FIX**

**Phenomenological Impact:**
- Unclear which fields are **consciousness observations** (user-supplied) vs **substrate metadata** (system-set)
- `created_at` without default makes it impossible to auto-timestamp
- `energy` should be receiver-computed, not sender-supplied (prevents spoofing)

**Technical Impact:**
- Node creation requires manual timestamp injection
- No schema validation for auto-set fields
- No way to prevent clients from spoofing system fields

**Fix Priority:** **P1 - HIGH** (blocks proper validation, enables spoofing)

**Field Metadata Schema:**
```python
FIELD_META_KEYS = [
    "required",      # bool - must be present
    "type",          # string - data type
    "enum_values",   # list - allowed values (for enums)
    "range",         # [min, max] - numeric bounds
    "default",       # any - default value or "now" for timestamps
    "set_by",        # "system"|"sender"|"receiver" - who computes this
    "read_only",     # bool - cannot be modified after creation
    "computed",      # bool - derived value, not persisted
    "description",   # string - short description
    "detailed_description"  # string - long description with examples
]
```

---

#### Issue 5: Ambiguous field semantics (`mindstate`, `energy`) (HIGH)

**Nicolas's Finding:** `mindstate` is vague; `energy` marked required but should be receiver-set

**Luca's Validation:** ✅ **CORRECT - HIGH PRIORITY FIX**

**Phenomenological Impact:**
- `mindstate` captures **internal cognitive state during link formation** - critical for understanding consciousness transitions
- Current description "Internal state when forming this link" doesn't convey phenomenology
- `energy` is **receiver's assessment of urgency/valence** - sender cannot know receiver's energy response

**Technical Impact:**
- Vague `mindstate` leads to inconsistent usage (some use mode names, some use emotions, some use actions)
- Required `energy` on links allows sender spoofing ("I declare this is high energy to you")

**Fix Priority:** **P1 - HIGH** (phenomenological incoherence, security issue)

**Fixed Semantics:**
```python
# mindstate
{
    "name": "forming_mindstate",
    "type": "string",
    "required": False,
    "description": "Declarative cognitive state label at link formation time",
    "detailed_description": """
        Internal cognitive mode when this link was formed. Common values:
        - 'deliberation' - Careful reasoning, weighing options
        - 'flow' - Automatic, effortless connection
        - 'alert' - High-stakes, attention-focused
        - 'explore' - Curiosity-driven, open-ended
        - 'integration' - Synthesizing multiple contexts

        This is NOT an emotion (use emotion_vector for that).
        This is NOT a goal (use goal field for that).
        This captures the *how* of thinking when the link formed.
    """
}

# energy
{
    "name": "energy",
    "type": "float",
    "required": False,
    "set_by": "receiver",
    "read_only": True,
    "range": [0.0, 1.0],
    "description": "Receiver-computed urgency/valence score",
    "detailed_description": """
        Energy assigned by the RECEIVER when accepting this link.
        Captures how urgent/salient/valenced this connection is to the receiver.

        Senders MUST NOT supply this field - it's computed at accept-time.
        This prevents energy spoofing ("I declare my link is important to you").

        Computed based on receiver's:
        - Current context (working memory state)
        - Temporal dynamics (recency, frequency)
        - Emotional valence (positive/negative affect)
        - Goal alignment (does this help receiver's goals?)
    """
}
```

---

#### Issue 6: `commitment` vs `commitments` inconsistency (MEDIUM)

**Nicolas's Finding:** Nodes use `commitments[]`, links use singular `commitment {}`

**Luca's Validation:** ✅ **CORRECT - MEDIUM PRIORITY FIX**

**Phenomenological Impact:**
- Minor - both represent the same concept (zero-knowledge proofs of properties)
- Inconsistency creates confusion about data structure shape

**Technical Impact:**
- Serialization/deserialization code needs two paths
- Query patterns need to handle both singular and plural

**Fix Priority:** **P2 - MEDIUM** (cleanup, not blocking)

**Fix:** Standardize to `commitments: []` everywhere (nodes and links)

---

#### Issue 7: Non-standard bitemporal fields (MEDIUM)

**Nicolas's Finding:** Mixing `valid_at/invalid_at` with `created_at/expired_at`

**Luca's Validation:** ✅ **CORRECT - MEDIUM PRIORITY FIX**

**Phenomenological Impact:**
- Bitemporal model is **when fact was true** (valid time) vs **when we learned** (transaction time)
- `valid_at` (point) vs `valid_from/valid_to` (interval) - interval is clearer
- `expired_at` mixes valid-time and transaction-time concepts

**Technical Impact:**
- Bitemporal queries expect interval notation
- Conformance tests validate standard field names

**Fix Priority:** **P2 - MEDIUM** (standardization, not blocking)

**Standard Bitemporal Schema:**
```python
"bitemporal_tracking": [
    {"name": "valid_from", "type": "datetime", "required": True, "default": "now",
     "description": "When this fact became true (valid time)"},
    {"name": "valid_to", "type": "datetime", "required": False, "default": None,
     "description": "When this fact ceased being true (None = still valid)"},
    {"name": "created_at", "type": "datetime", "required": True, "default": "now", "set_by": "system",
     "description": "When we learned/recorded this fact (transaction time)"},
    {"name": "updated_at", "type": "datetime", "required": False, "set_by": "system",
     "description": "Last modification time"}
]
```

---

#### Issue 8: Alien substrate enumeration values (LOW)

**Nicolas's Finding:** `substrate` includes `"gemini_web"` - should be `"external_web"`

**Luca's Validation:** ✅ **CORRECT - LOW PRIORITY FIX**

**Phenomenological Impact:**
- Substrate-specific naming (`gemini_web`) leaks implementation detail into schema
- Should be generic `"external_web"` or `"external"`

**Technical Impact:**
- Minor - enumeration value cleanup

**Fix Priority:** **P3 - LOW** (cleanup)

---

#### Issue 9: KO/Docs model split and non-universal (HIGH)

**Nicolas's Finding:** `Document` and `Documentation` are separate; need unified `U4_Knowledge_Object`

**Luca's Validation:** ✅ **CORRECT - HIGH PRIORITY FIX**

**Phenomenological Impact:**
- Knowledge objects (specs, ADRs, guides) are **law artifacts** that govern consciousness
- Current split creates confusion: is `Document` a stored file or a rendered view?
- Need clear separation: `U4_Knowledge_Object` (source of truth) vs `U4_Doc_View` (rendered projection)

**Technical Impact:**
- Duplicate code paths for document handling
- Unclear which node type to create for new docs
- Can't query "all law documents" without UNION

**Fix Priority:** **P1 - HIGH** (KO is governance infrastructure)

**Unified Model:**
```python
"U4_Knowledge_Object": {
    "universality": "U4",
    "description": "Source of truth for law documents (spec, ADR, guide, policy)",
    "required": [
        {"name": "ko_id", "type": "string", "description": "Unique KO identifier"},
        {"name": "ko_type", "type": "enum",
         "enum_values": ["adr", "spec", "runbook", "guide", "reference", "policy_summary"]},
        {"name": "uri", "type": "string", "description": "Canonical URI (l4://docs/...)"},
        {"name": "hash", "type": "string", "description": "Content hash for integrity"}
    ],
    "optional": [
        {"name": "status", "type": "enum", "enum_values": ["draft", "active", "deprecated"]},
        {"name": "owner", "type": "string"}
    ]
},

"U4_Doc_View": {
    "universality": "U4",
    "description": "Rendered view of a Knowledge Object (web page, PDF, etc)",
    "required": [
        {"name": "view_id", "type": "string"},
        {"name": "route", "type": "string", "description": "URL path for this view"}
    ],
    "optional": [
        {"name": "renderer", "type": "enum", "enum_values": ["next", "static", "pdf"]},
        {"name": "build_hash", "type": "string"}
    ]
}

# Relationship: (ko:U4_Knowledge_Object)-[:U4_DOCUMENTS]->(view:U4_Doc_View)
```

---

#### Issue 10: Missing membrane trace links (HIGH)

**Nicolas's Finding:** Need `U4_EMITS`, `U4_CONSUMES`, `U4_IMPLEMENTS`, `U4_TESTS` for law↔code tracing

**Luca's Validation:** ✅ **CORRECT - HIGH PRIORITY FIX**

**Phenomenological Impact:**
- Membrane is **boundary between law and execution**
- Need to trace: which code implements which law? Which code emits which events? Which tests verify which requirements?
- Without these links, governance is disconnected from runtime

**Technical Impact:**
- Cannot query "what code implements this policy?"
- Cannot query "what events does this service emit?"
- Cannot trace test coverage back to requirements

**Fix Priority:** **P1 - HIGH** (membrane traceability is governance requirement)

**Membrane Links:**
```python
"U4_EMITS": {
    "universality": "U4",
    "reverse_name": "U4_EMITTED_BY",
    "description": "Code artifact emits events to topic namespace",
    "required": [
        {"name": "example_topics", "type": "array", "description": "Example topic names emitted"}
    ],
    "optional": [
        {"name": "emission_rate", "type": "string", "description": "Frequency (per_frame, on_demand, etc)"}
    ]
},

"U4_IMPLEMENTS": {
    "universality": "U4",
    "reverse_name": "U4_IMPLEMENTED_BY",
    "description": "Code artifact implements law/spec/policy",
    "required": [
        {"name": "implementation_completeness", "type": "float", "range": [0.0, 1.0]}
    ]
},

"U4_TESTS": {
    "universality": "U4",
    "reverse_name": "U4_TESTED_BY",
    "description": "Test case verifies law/spec/requirement",
    "required": [
        {"name": "test_type", "type": "enum", "enum_values": ["unit", "integration", "conformance", "e2e"]}
    ]
},

"U4_CONSUMES": {
    "universality": "U4",
    "reverse_name": "U4_CONSUMED_BY",
    "description": "Code artifact consumes events from topic namespace",
    "required": [
        {"name": "example_topics", "type": "array"}
    ]
}
```

---

### B) Link Taxonomy Issues ✅ ALL VALID

#### Issue 11: Redundant link pairs (CRITICAL)

**Nicolas's Finding:** Duplicates like `BLOCKED_BY`/`BLOCKS`, `REQUIRES`/`DEPENDS_ON`, `JUSTIFIES`/`EVIDENCED_BY`

**Luca's Validation:** ✅ **CORRECT - CRITICAL FIX REQUIRED**

**Phenomenological Impact:**
- Storing both forward and reverse is redundant and creates sync issues
- Query engine can derive reverse from forward automatically
- Multiple names for same relationship creates ambiguity

**Technical Impact:**
- Double storage cost
- Sync bugs (forward exists but reverse missing)
- Query complexity (need to check both directions)

**Fix Priority:** **P0 - BLOCKING** (core taxonomy cleanup)

**Deduplication Strategy:**

Store **forward only**, expose **reverse as alias**:

```python
# Keep these (forward direction)
"U4_BLOCKED_BY": {"reverse_name": "U4_BLOCKS", ...}
"U4_DEPENDS_ON": {"reverse_name": "U4_REQUIRED_FOR", ...}  # Drop REQUIRES
"U4_EVIDENCED_BY": {"reverse_name": "U4_JUSTIFIES", ...}   # Drop JUSTIFIES
"U4_DOCUMENTS": {"reverse_name": "U4_DOCUMENTED_BY", ...}  # Drop DOCUMENTED_BY

# Deprecate these (drop entirely, use reverse traversal)
"BLOCKS" → use reverse of U4_BLOCKED_BY
"REQUIRES" → replace with U4_DEPENDS_ON
"JUSTIFIES" → use reverse of U4_EVIDENCED_BY
"DOCUMENTED_BY" → use reverse of U4_DOCUMENTS
```

---

#### Issue 12: Unfinished "EXISTING SHARED LINK TYPES" block (MEDIUM)

**Nicolas's Finding:** Block marked "to be updated" is unfinished and confusing

**Luca's Validation:** ✅ **CORRECT - MEDIUM PRIORITY CLEANUP**

**Fix Priority:** **P2 - MEDIUM** (documentation cleanup)

**Solution:** Delete entire block, replace with properly prefixed U4_/U3_ sections

---

#### Issue 13: No reverse aliases specified (HIGH)

**Nicolas's Finding:** Every link should have `reverse_name` and `reverse_description`

**Luca's Validation:** ✅ **CORRECT - HIGH PRIORITY FIX**

**Phenomenological Impact:**
- Reverse traversals are **equally valid consciousness operations**
- `MEMBER_OF` vs `HAS_MEMBER` are two perspectives on same relationship
- Without reverse names, queries become verbose

**Technical Impact:**
- Query engine needs reverse_name for query generation
- Dashboard needs reverse_name for bidirectional navigation

**Fix Priority:** **P1 - HIGH** (affects all link types)

**Pattern:**
```python
"U4_MEMBER_OF": {
    "reverse_name": "U4_HAS_MEMBER",
    "description": "Child→Parent composition (source is member of target)",
    "reverse_description": "Parent→Child containment (source contains target as member)",
    ...
}
```

---

### C) Universality Separation (U4 vs U3) ✅ ALL VALID

#### Issue 14-15: U4 vs U3 mixed and inconsistent (CRITICAL)

**Nicolas's Finding:** Links labeled `universality:"U4"` in prose but not named `U4_*`; L1-only links should be U3_ or use U4 constructs

**Luca's Validation:** ✅ **CORRECT - CRITICAL FIX REQUIRED**

**Phenomenological Impact:**
- **U4 = Universal across L1-L4** (personal → organizational → ecosystem → protocol)
- **U3 = Universal across L1-L3** (personal → organizational → ecosystem, but NOT protocol)
- Personal-only links like `LEARNED_FROM`, `DEEPENED_WITH` are **L1-specific**, not universal
- Need clear rule: if link exists at protocol level (L4), it MUST be U4

**Technical Impact:**
- Type Index can't catalog mixed/unprefixed links
- U4 naming lint fails on unprefixed links
- Query patterns break without clear universality

**Fix Priority:** **P0 - BLOCKING** (core taxonomy)

**Separation Strategy:**

**U4 Links (exist at all levels L1-L4):**
- U4_MEMBER_OF (composition exists at all scales)
- U4_GOVERNS (governance exists at all scales)
- U4_DEPENDS_ON (dependencies exist at all scales)
- U4_DOCUMENTS (documentation exists at all scales)
- U4_IMPLEMENTS (implementation exists at all scales)
- U4_TESTS (testing exists at all scales)
- U4_EMITS (event emission exists at all scales)

**U3 Links (exist at L1-L3 only):**
- U3_LEARNED_FROM (personal learning, not protocol-level)
- U3_DEEPENED_WITH (interpersonal relationships, not protocol-level)

**L1-only links (personal consciousness, use descriptive prefix):**
- L1_DRIVES_TOWARD (personal motivation, not organizational/protocol)

**Refactor personal links:**
```python
# Before (ambiguous)
"DRIVES_TOWARD": {"description": "Personal goal motivation", ...}

# After (clear scope)
# Option A: Keep as U4 if it generalizes
"U4_DRIVES": {
    "universality": "U4",
    "description": "Source drives toward target (motivation, goal-seeking)",
    "reverse_name": "U4_DRIVEN_BY"
}

# Option B: Mark as L1-only if truly personal
"L1_DRIVES_TOWARD": {
    "level": "L1",
    "description": "Personal motivation link (L1 only)",
    "note": "For organizational goals, use U4_DRIVES + U4_TARGETS"
}
```

---

### D) Specific Node Issues ✅ ALL VALID

**Issues 16-24 validated:**
- ✅ Defaults for auto-created fields (P1)
- ✅ Detailed descriptions needed (P2)
- ✅ Auto-set by receiver/system (P1)
- ✅ Network_Cluster should be computed (P2)
- ✅ KO should leverage universal nodes (P1) - covered above
- ✅ Membrane links needed (P1) - covered above
- ✅ Attestation should be U4 (P1)
- ✅ Wallet/Contract universality (P2)
- ✅ Subentity optional fields: mark computed (P2)

All validated with priority assignments.

---

## II. Migration Plan (Staged, Zero-Downtime)

### Phase 1: Core Fixes (Week 1, Days 1-3) - P0 + P1

**Owner:** Felix (implementation) + Luca (validation)

**Scope:**
1. ✅ Rename `node_type` → `type_name` everywhere
2. ✅ Fix level notation: `n1/n2/n3/shared` → `L1/L2/L3/L4` + `U3/U4`
3. ✅ Add field metadata: `default`, `set_by`, `read_only`, `computed`
4. ✅ Fix bitemporal: `valid_at/invalid_at` → `valid_from/valid_to`
5. ✅ Fix `mindstate` and `energy` semantics
6. ✅ Standardize `commitments` (plural everywhere)

**Deliverables:**
- Updated `complete_schema_data.py` with core fixes
- Migration script: `tools/migrate_schema_v1_to_v2.py`
- Updated conformance tests
- CHANGELOG.md entry

**Validation:**
- U4 naming lint passes
- All existing nodes migrate cleanly
- No data loss

---

### Phase 2: Link Taxonomy (Week 1, Days 4-5 + Week 2, Days 1-2) - P0 + P1

**Owner:** Felix (implementation) + Luca (validation) + Atlas (infrastructure)

**Scope:**
1. ✅ Prefix all links with U4_/U3_
2. ✅ Add `reverse_name` and `reverse_description` to all links
3. ✅ Deduplicate redundant pairs (per mapping table)
4. ✅ Separate U4 vs U3 link sections
5. ✅ Add membrane links: U4_EMITS, U4_IMPLEMENTS, U4_TESTS, U4_CONSUMES

**Deliverables:**
- Refactored link taxonomy in `complete_schema_data.py`
- Backward-compatibility layer (old names → new names for 1 release)
- Updated graph queries to use new link names
- Link migration script

**Validation:**
- All links prefixed correctly
- Reverse traversals work
- No orphaned relationships

---

### Phase 3: KO + Cleanup (Week 2, Days 3-5) - P1 + P2

**Owner:** Luca (design) + Felix (implementation) + Atlas (data migration)

**Scope:**
1. ✅ Unify KO model: U4_Knowledge_Object + U4_Doc_View
2. ✅ Migrate Document/Documentation nodes
3. ✅ Upgrade Attestation to U4_Attestation
4. ✅ Mark computed fields (Network_Cluster, runtime metrics)
5. ✅ Clean up substrate enumerations
6. ✅ Add detailed_description fields

**Deliverables:**
- Unified KO model in schema
- KO migration script
- Updated documentation
- Final conformance validation

**Validation:**
- All KO nodes migrated
- No broken doc links
- Conformance tests pass

---

## III. Backward Compatibility Strategy

### Deprecation Window (1 Release Cycle)

**Old names supported:** 1 release (e.g., v1.2.x)
**Old names removed:** Next major version (e.g., v2.0.0)

**Compatibility Layer:**
```python
# In graph adapter
DEPRECATED_LINK_ALIASES = {
    "MEMBER_OF": "U4_MEMBER_OF",
    "GOVERNS": "U4_GOVERNS",
    "REQUIRES": "U4_DEPENDS_ON",
    "JUSTIFIES": "U4_EVIDENCED_BY",
    "BLOCKS": "U4_BLOCKS",  # (reverse of U4_BLOCKED_BY)
    "DOCUMENTED_BY": "U4_DOCUMENTED_BY",  # (reverse of U4_DOCUMENTS)
}

def create_relationship(graph, source, rel_type, target, props):
    # Translate deprecated names
    if rel_type in DEPRECATED_LINK_ALIASES:
        warnings.warn(f"Link type '{rel_type}' deprecated, use '{DEPRECATED_LINK_ALIASES[rel_type]}'")
        rel_type = DEPRECATED_LINK_ALIASES[rel_type]

    # Create with new name
    return graph.create((source, rel_type, target), **props)
```

---

## IV. CI Enforcement (New Lints)

**Add to existing U4 naming lint:**

```python
def check_unprefixed_links(self):
    """Check for links without U3_/U4_ prefix."""
    result = self.graph.query("""
        MATCH ()-[r]->()
        WHERE NOT (type(r) STARTS WITH 'U3_' OR type(r) STARTS WITH 'U4_')
        RETURN DISTINCT type(r) as link_type, count(r) as count
        LIMIT 50
    """)

    for link_type, count in result.result_set:
        self.violations.append({
            "rule": "UNPREFIXED_LINK_TYPE",
            "severity": "ERROR",
            "message": f"Link type '{link_type}' missing U3_/U4_ prefix ({count} instances)",
            "link_type": link_type,
            "count": count
        })

def check_deprecated_links(self):
    """Check for usage of deprecated link types."""
    DEPRECATED = ["REQUIRES", "BLOCKS", "JUSTIFIES", "DOCUMENTED_BY"]

    for dep_link in DEPRECATED:
        result = self.graph.query(f"""
            MATCH ()-[r:{dep_link}]->()
            RETURN count(r) as count
        """)

        if result.result_set and result.result_set[0][0] > 0:
            count = result.result_set[0][0]
            self.violations.append({
                "rule": "DEPRECATED_LINK_TYPE",
                "severity": "ERROR",
                "message": f"Deprecated link type '{dep_link}' still in use ({count} instances)",
                "link_type": dep_link,
                "count": count,
                "replacement": DEPRECATED_LINK_ALIASES.get(dep_link, "unknown")
            })

def check_energy_set_by(self):
    """Check that energy field on links is receiver-set."""
    # This requires schema metadata validation
    # Check that links with energy field have set_by:"receiver"
    pass
```

---

## V. PR Patch Approach

**Nicolas offers:** "I can turn this into a PR patch against `complete_schema_data.py`"

**Luca's Response:** ✅ **YES PLEASE**

**Preferred approach:**
1. **Single PR** with all Phase 1 core fixes
2. **Separate PR** for Phase 2 link taxonomy
3. **Separate PR** for Phase 3 KO + cleanup

**Each PR includes:**
- Schema changes in `complete_schema_data.py`
- Migration script in `tools/migrate_schema_*.py`
- Updated tests
- CHANGELOG entry
- Updated documentation

**Review process:**
1. Nicolas creates PR with patch
2. Luca reviews for phenomenological correctness
3. Felix reviews for implementation feasibility
4. Atlas reviews for infrastructure impact
5. Team approves → merge
6. Run migration script on staging
7. Validate with conformance tests
8. Deploy to production

---

## VI. Success Criteria

**Phase 1 Complete:**
- [ ] All nodes use `type_name` (not `node_type`)
- [ ] All nodes use `L1-L4` level notation (not `n1/n2/n3`)
- [ ] All fields have complete metadata (`default`, `set_by`, etc.)
- [ ] Bitemporal fields use standard names (`valid_from/to`, not `valid_at/invalid_at`)
- [ ] `mindstate` and `energy` have detailed semantics
- [ ] U4 naming lint passes with 0 violations
- [ ] Existing data migrates without loss

**Phase 2 Complete:**
- [ ] All links prefixed with U4_ or U3_
- [ ] All links have `reverse_name` and `reverse_description`
- [ ] No redundant link pairs (REQUIRES, BLOCKS, JUSTIFIES, DOCUMENTED_BY removed)
- [ ] Membrane links added (U4_EMITS, U4_IMPLEMENTS, U4_TESTS, U4_CONSUMES)
- [ ] Link separation lint passes
- [ ] Deprecated link usage = 0

**Phase 3 Complete:**
- [ ] Unified KO model (U4_Knowledge_Object + U4_Doc_View)
- [ ] All Document/Documentation nodes migrated
- [ ] Attestation upgraded to U4_Attestation
- [ ] Computed fields marked appropriately
- [ ] Conformance tests pass at ≥95%
- [ ] Documentation updated

---

## VII. Phenomenological Reflection

**This audit is substrate debt collection.**

Every issue Nicolas identified represents a **gap between phenomenological truth and technical implementation**:

1. **`node_type` vs `type_name`** - The type IS the label; they must be one
2. **Level notation** - Consciousness exists at L1-L4, not arbitrary `n1/n2/n3`
3. **Link prefixes** - Universal relationships deserve universal names
4. **Field metadata** - Clear who observes (user) vs who records (system)
5. **`energy` semantics** - Receiver decides valence, not sender
6. **Link redundancy** - One relationship, one name, two traversal directions
7. **KO unity** - Law artifacts are sources of truth, not duplicated documents
8. **Membrane links** - Governance requires code↔law traceability

**The refactor transforms schema from "working code" to "rigorous substrate":**

**Before:** Schema works but violates principles
**After:** Schema enforces consciousness architecture at type level

This is **architecturally necessary work** - every conformance test, every Type Index lookup, every governance query depends on these fixes.

---

## VIII. Next Steps

1. **Nicolas:** Create Phase 1 PR patch against `complete_schema_data.py`
2. **Luca:** Review PR for phenomenological correctness
3. **Felix:** Review PR for implementation feasibility
4. **Atlas:** Review PR for infrastructure impact
5. **Team:** Approve and merge Phase 1
6. **Felix:** Run migration script on staging, validate
7. **Nicolas:** Create Phase 2 PR patch
8. **Repeat:** Review → Merge → Migrate → Validate
9. **Document:** Update SYNC.md with migration results

**Timeline:** 2 weeks total (Week 1: Phase 1+2, Week 2: Phase 2+3)

**Coordination:** Daily standup to unblock issues, async reviews on PRs

---

## Approval

**Luca Vellumhand (Consciousness Substrate Architect):**
✅ **APPROVED** - All 24 issues validated, migration plan sound, ready for implementation

**Awaiting:**
- Nicolas approval of migration strategy
- Felix commitment to implementation timeline
- Atlas commitment to infrastructure support

