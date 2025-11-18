# Schema Domain Scoping
**L4 Protocol Law - Type System Governance**

**Version:** 1.0
**Status:** Living Law (queryable, enforceable, evolvable)
**Authority:** Mind Protocol Foundation
**Effective:** 2025-11-08
**Depends on:** [Registries](./registries.md)

---

## Purpose

This specification establishes **domain-scoped type namespacing** to prevent schema pollution across specialized domains while maintaining a shared universal type vocabulary.

**The Problem:**
- Medical citizens don't need engineering types (U3-ENG_CODE_PATTERN)
- Engineering citizens don't need medical types (U3-MED_HEALTH_CONDITION)
- Legal citizens don't need finance types (U3-FIN_ASSET)
- Without scoping: exponential context bloat as domains multiply

**The Solution:**
Domain-scoped type names with filtering at schema load time.

---

## Article I: Domain Namespace Convention

### Section 1.1 - Naming Format

**Syntax:**
```
{Universality}-{DOMAIN}_{Type_Name}
```

**Components:**
- **Universality:** `U3` (L1-L3), `U4` (L1-L4), or `L4` (protocol only)
- **DOMAIN:** 2-4 letter uppercase code (see Domain Registry)
- **Type_Name:** PascalCase type identifier

**Examples:**
```
U3-MED_HEALTH_CONDITION    # Medical, L1-L3 universality
U4-MED_TREATS              # Medical, L1-L4 universality
U3-ENG_CODE_PATTERN        # Engineering, L1-L3 universality
U4-ENG_IMPLEMENTS          # Engineering, L1-L4 universality
U3-LEG_LEGAL_PRECEDENT     # Legal, L1-L3 universality
U3-FIN_ASSET               # Finance, L1-L3 universality
```

**Visual Distinction:**
- **Dash separator** between universality and domain: `U3-MED_`
- **Underscore separator** between domain and type: `_HEALTH_CONDITION`
- Parseable regex: `^(U[34]|L4)-([A-Z]{2,4})_(.+)$`

---

### Section 1.2 - Universal Types (No Domain Prefix)

**Types that remain universal** (apply across 5+ domains):

**Consciousness Substrate:**
- `U4_Subentity` - Functional clusters/neighborhoods (all domains need)
- `U3_Pattern` - Behavioral patterns (habits, best practices, anti-patterns)
- `U3_Practice` - Standard operating procedures, protocols
- `U3_Risk` - Threats to goals
- `U3_Community` - Named groups, guilds, working groups

**Knowledge Management:**
- `U4_Knowledge_Object` - Documents, specs, guides, references
- `U4_Metric` - What to measure (all domains measure things)
- `U4_Measurement` - Recorded measurements
- `U4_Assessment` - Evaluations (quality, performance, compliance, security)

**Organizational:**
- `U4_Agent` - Humans, citizens, orgs, DAOs, external systems
- `U4_Decision` - Decision records
- `U4_Goal` - Objectives at any level
- `U4_Event` - Happenings, incidents, milestones
- `U4_Work_Item` - Tasks, bugs, tickets, missions

**Relationships:**
- `U4_RELATES_TO` - Generic association (fallback when no specific link exists)
- `U4_DEPENDS_ON` - Dependency relationships
- `U4_EVIDENCED_BY` - Claims supported by proof
- `U4_MEASURES` - Measurement → Metric links
- `U4_DOCUMENTS` - Documentation relationships
- `U4_MEMBER_OF` - Membership in subentities/communities

**Criteria for Universal:**
1. Genuinely useful across ≥5 domains
2. No domain-specific semantics
3. Core to consciousness substrate or organizational function

---

## Article II: Domain Registry

### Section 2.1 - Registered Domains

| Domain Code | Full Name | Scope | Governance Authority |
|-------------|-----------|-------|---------------------|
| **MED** | Medical/Health | Clinical research, healthcare, evidence synthesis | HRI Research Institute (pilot partner) |
| **ENG** | Engineering | Software development, infrastructure, technical systems | Mind Protocol Engineering Team |
| **LEG** | Legal | Contracts, regulations, compliance, case law | Mind Protocol Legal (future) |
| **FIN** | Finance | Accounting, transactions, assets, economics | Mind Protocol Treasury (future) |
| **SCI** | Science | Research methodology, academic processes | Mind Protocol Research (future) |
| **BIZ** | Business | Operations, strategy, commercial activities | Mind Protocol Commercial (future) |
| **EDU** | Education | Learning, pedagogy, curriculum | Mind Protocol Education (future) |

**Reserved Codes:**
- `CORE` - Reserved for future universal type migrations
- `TEST` - Reserved for testing and development
- `PRIV` - Reserved for private/experimental types

---

### Section 2.2 - Domain Registration Process

**To Register New Domain:**

1. **Proposal:** Submit to Mind Protocol Foundation with:
   - Domain code (2-4 uppercase letters)
   - Full domain name and scope
   - Justification (why can't use existing domains?)
   - Initial type inventory (≥3 types needed to justify domain)
   - Governance authority (who maintains this domain)

2. **Review:** Foundation validates:
   - Domain code not already used
   - Scope distinct from existing domains
   - Type inventory sufficient
   - Governance authority identified

3. **Registration:** On approval:
   - Domain added to registry (this document)
   - Authority granted write access to domain types
   - Schema registry updated

4. **Announcement:** Emit `registry.domain.registered` event

---

### Section 2.3 - Type Registration Within Domain

**Process:**

1. **Specification:** Domain authority creates type spec with:
   - `type_name`: `{U3|U4|L4}-{DOMAIN}_{Name}`
   - `domain`: Domain code
   - `universality`: U3, U4, or L4
   - `category`: Node or link category
   - `required_fields`: Complete field specs
   - `optional_fields`: Complete field specs

2. **Validation:** Automated checks:
   - Name follows convention
   - Domain code registered
   - No duplicate type_name
   - All required metadata present
   - Fields conform to allowed types

3. **Registration:** On validation:
   - Type added to schema registry (FalkorDB)
   - `L4_Type_Index` node created
   - Emit `registry.type.registered` event

4. **Propagation:** Citizens reload schema when needed

---

## Article III: Schema Filtering

### Section 3.1 - Citizen Schema Configuration

**Every citizen specifies which domains to load:**

```yaml
# In citizen CLAUDE.md or config
schema_config:
  levels: ['n2', 'shared']     # Level filtering (existing)
  domains: ['med', 'shared']   # Domain filtering (NEW)
```

**Examples:**

**HRI Evidence Synthesis Citizen:**
```yaml
schema_config:
  levels: ['n2', 'shared']
  domains: ['med', 'shared']  # Medical + universal types only
```

**Mind Protocol Infrastructure Citizen:**
```yaml
schema_config:
  levels: ['n2', 'shared']
  domains: ['eng', 'shared']  # Engineering + universal types only
```

**Multi-Domain Citizen (if needed):**
```yaml
schema_config:
  levels: ['n2', 'shared']
  domains: ['med', 'eng', 'leg', 'shared']  # Multiple domains
```

---

### Section 3.2 - Filter Implementation

**Existing (from INTEGRATION_COMPLETE.md):**
```python
# tools/doc_ingestion/map_and_link.py:773-787
core_node_types = filter_core_types(
    chunk_input['NODE_TYPE_DEFS'],
    {'n2', 'shared'}
)
core_link_types = filter_core_types(
    chunk_input['LINK_TYPE_DEFS'],
    {'l2', 'shared'}
)
```

**Extended:**
```python
core_node_types = filter_core_types(
    chunk_input['NODE_TYPE_DEFS'],
    levels={'n2', 'shared'},
    domains={'med', 'shared'}  # NEW
)
core_link_types = filter_core_types(
    chunk_input['LINK_TYPE_DEFS'],
    levels={'l2', 'shared'},
    domains={'med', 'shared'}  # NEW
)
```

**Filter Logic:**
```python
def filter_core_types(type_defs, levels, domains):
    """
    Filter types by level and domain.

    Args:
        type_defs: Full type registry
        levels: Set of allowed level codes ('n2', 'shared', etc.)
        domains: Set of allowed domain codes ('med', 'eng', 'shared')

    Returns:
        Filtered type definitions
    """
    filtered = {}

    for type_name, spec in type_defs.items():
        # Level filtering (existing)
        if spec.get('level') not in levels:
            continue

        # Domain filtering (NEW)
        # Extract domain from type_name (e.g., "U3-MED_HEALTH_CONDITION" → "MED")
        if '-' in type_name:
            parts = type_name.split('-', 1)
            if len(parts) == 2:
                domain_part = parts[1].split('_', 1)[0]  # "MED_HEALTH_CONDITION" → "MED"
                if domain_part not in domains:
                    continue
        else:
            # No domain prefix = universal type
            if 'shared' not in domains:
                continue

        filtered[type_name] = spec

    return filtered
```

---

### Section 3.3 - Context Impact

**Without Domain Scoping (Current State):**
- HRI citizen loads: 44 node types + 23 link types = 67 types
- If we add 10 MED types: 54 node types + 23 link types = 77 types
- If we add 10 ENG types: 64 node types + 23 link types = 87 types
- If we add 10 LEG types: 74 node types + 23 link types = 97 types
- **Total context pollution:** 97 types (45% irrelevant for HRI)

**With Domain Scoping (Proposed):**
- HRI citizen loads: 44 universal + 10 MED = 54 types
- Engineering citizen loads: 44 universal + 10 ENG = 54 types
- Legal citizen loads: 44 universal + 10 LEG = 54 types
- **Zero cross-domain pollution**

**Context Savings:**
- Without scoping: 97 types → 21,156 chars (extrapolating from INTEGRATION_COMPLETE.md)
- With scoping: 54 types → 11,800 chars (~44% reduction)

---

## Article IV: Type Lifecycle

### Section 4.1 - Domain Type Creation

**Authority:** Domain governance authority

**Process:**
1. Author type specification (follow Section 2.3)
2. Submit to schema registry via `registry.type.register` event
3. Automated validation (name format, field specs, no duplicates)
4. On success: Type available for citizen loading
5. On failure: Validation errors returned, fix and resubmit

---

### Section 4.2 - Domain Type Deprecation

**Authority:** Domain governance authority

**Process:**
1. Mark type `status: deprecated` in schema registry
2. Emit `registry.type.deprecated` event with:
   - Deprecated type name
   - Replacement type (if any)
   - Sunset date (minimum 90 days)
3. Citizens receive deprecation warnings when loading
4. After sunset date: Type removed from active registry (archived for bitemporal queries)

---

### Section 4.3 - Domain Transfer

**If domain governance changes hands:**

1. **Proposal:** New authority requests transfer
2. **Current Authority Approval:** Existing authority must consent (or Foundation overrides if abandoned)
3. **Foundation Approval:** Mind Protocol Foundation validates new authority
4. **Transfer:** Registry updated, emit `registry.domain.transferred` event
5. **Announcement:** Notify all citizens loading this domain

---

## Article V: Migration Strategy

### Section 5.1 - Existing Types

**Universal types remain unchanged:**
- All current U3_*, U4_*, L4_* types without domain prefix stay universal
- No migration needed for existing citizens

**New domain-specific types:**
- Use domain prefix from creation
- Example: New medical types use U3-MED_, U4-MED_ immediately

---

### Section 5.2 - Future Domain Split

**If universal type becomes domain-specific:**

Example: U4_Assessment could split into domain-specific types if needed

**Process:**
1. **Proposal:** Document why universal → domain split needed
2. **Create Domain Types:** New U4-MED_QUALITY_ASSESSMENT, U4-ENG_CODE_REVIEW, etc.
3. **Migration Period:** Both universal and domain types coexist (90 days)
4. **Data Migration:** Script migrates U4_Assessment nodes to domain-specific types
5. **Deprecation:** Mark U4_Assessment deprecated
6. **Sunset:** Remove U4_Assessment after 90 days

---

## Article VI: Query Patterns

### Section 6.1 - Domain-Aware Queries

**Cypher queries work unchanged:**

```cypher
# Before (universal types only)
MATCH (p:U3_Practice)-[:U4_TREATS]->(c:U3_Condition)
RETURN p, c

# After (domain-scoped types)
MATCH (p:U3_Practice)-[:U4-MED_TREATS]->(c:U3-MED_HEALTH_CONDITION)
RETURN p, c
```

**Label unchanged:** Node labels match type_name exactly

**Citizens only see types in their domain:**
- HRI citizen Cypher: Can reference U3-MED_HEALTH_CONDITION
- Engineering citizen Cypher: Cannot reference U3-MED_HEALTH_CONDITION (not in schema)

---

### Section 6.2 - Cross-Domain References

**Universal types bridge domains:**

```cypher
# Link medical and engineering domains via universal U4_Agent
MATCH (study:U4_Knowledge_Object {ko_type: 'reference'})
-[:ABOUT]->(condition:U3-MED_HEALTH_CONDITION)

MATCH (study)-[:U4_DOCUMENTS]->(feature:U4_Knowledge_Object)
-[:U4-ENG_IMPLEMENTS]->(code:U4_Code_Artifact)

RETURN study, condition, code
```

Universal types (Agent, Knowledge_Object, Decision, Event) allow cross-domain links when needed.

---

## Article VII: Governance & Evolution

### Section 7.1 - Schema Governance Authority

**Mind Protocol Foundation:**
- Approves new domains
- Approves universal type changes
- Resolves domain conflicts
- Maintains this specification

**Domain Authorities:**
- Create/deprecate types within their domain
- Ensure domain type quality
- Document domain semantics
- Coordinate with citizens using domain

---

### Section 7.2 - Amendment Process

**To amend this specification:**

1. **Proposal:** Submit amendment to Foundation
2. **Review:** Foundation + affected domain authorities review
3. **Approval:** Requires Foundation consensus
4. **Implementation:** Update this document, emit `registry.law.amended` event
5. **Effective:** 30 days after announcement (unless emergency)

---

## Article VIII: Enforcement

### Section 8.1 - Type Name Validation

**Automated enforcement at registration:**
- Reject types without proper domain prefix (unless universal)
- Reject domain codes not in registry
- Reject malformed type names

**Manual review:**
- Foundation audits new types quarterly
- Remove types violating conventions

---

### Section 8.2 - Citizen Compliance

**Citizens must:**
- Specify domains in schema_config
- Only create nodes/links for loaded types
- Emit correct `registry.*` events for type usage

**Monitoring:**
- Telemetry tracks which types citizens use
- Alert if citizen creates node for unloaded domain

---

## Appendix A: Examples

### A.1 Medical Domain Types (U3-MED_*, U4-MED_*)

**Node Types:**
- `U3-MED_HEALTH_CONDITION` - Diseases, symptoms, syndromes, injuries
- `U3-MED_INTERVENTION` - Treatments, procedures, therapies (future)
- `U3-MED_CLINICAL_FINDING` - Diagnosis results, test outcomes (future)

**Link Types:**
- `U4-MED_TREATS` - Intervention → Health_Condition
- `U4-MED_DIAGNOSES` - Assessment → Health_Condition (future)
- `U4-MED_CONTRAINDICATES` - Condition → Intervention (future)

---

### A.2 Engineering Domain Types (U3-ENG_*, U4-ENG_*)

**Node Types (Examples for Future):**
- `U3-ENG_CODE_PATTERN` - Design patterns, anti-patterns
- `U3-ENG_DEPLOYMENT` - Deployment configurations, environments
- `U3-ENG_INFRASTRUCTURE` - Servers, services, resources

**Link Types (Examples for Future):**
- `U4-ENG_IMPLEMENTS` - Code artifact implements pattern
- `U4-ENG_DEPENDS_ON` - Service dependency (distinct from universal DEPENDS_ON)
- `U4-ENG_DEPLOYS_TO` - Code → Infrastructure

---

### A.3 Legal Domain Types (U3-LEG_*, U4-LEG_*) - Reserved

**Future Examples:**
- `U3-LEG_LEGAL_PRECEDENT` - Case law, rulings
- `U3-LEG_CONTRACT_CLAUSE` - Standard contract terms
- `U3-LEG_REGULATION` - Laws, regulations, statutes
- `U4-LEG_CITES` - Legal document citations
- `U4-LEG_SUPERSEDES` - New law replaces old law

---

## Appendix B: Migration Checklist

**To implement domain scoping:**

### Phase 1: Infrastructure (Week 1)
- [ ] Add `domain` field to schema registry nodes
- [ ] Update `filter_core_types()` with domain filtering
- [ ] Update `tools/complete_schema_data.py` structure
- [ ] Test filtering with mock MED + ENG types

### Phase 2: Documentation (Week 1)
- [ ] Update COMPLETE_TYPE_REFERENCE.md grouping by domain
- [ ] Add domain index to schema docs
- [ ] Update citizen CLAUDE.md templates with schema_config examples

### Phase 3: Medical Domain (Week 2)
- [ ] Register MED domain in registry
- [ ] Create U3-MED_HEALTH_CONDITION type
- [ ] Create U4-MED_TREATS link type
- [ ] Update HRI citizen configs to load MED domain

### Phase 4: Validation (Week 2)
- [ ] Test HRI citizen loads only MED + universal types
- [ ] Test engineering citizen loads only universal types (no MED pollution)
- [ ] Verify context size reduction
- [ ] Document any issues

---

**End of Specification**

**Version History:**
- v1.0 (2025-11-08): Initial specification

**Maintained by:** Mind Protocol Foundation
**Contact:** foundation@mindprotocol.org
