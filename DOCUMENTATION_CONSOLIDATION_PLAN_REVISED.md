# Documentation Consolidation Plan - REVISED

**Date:** 2025-10-20
**Revision:** 2.0 (Conservative approach)
**Principle:** ONE source of truth per abstraction level
**Authority:** `docs/specs/consciousness_engine_architecture/` for mechanisms, `docs/specs/self_observing_substrate/` for vision
**Compiled by:** Felix "Ironhand" (Engineer)

---

## Key Insight from Nicolas's Feedback

**self_observing_substrate/ ≠ consciousness_engine_architecture/**

They serve **different abstraction levels**:

| Directory | Purpose | Abstraction |
|-----------|---------|-------------|
| `self_observing_substrate/` | **Architectural vision** - WHY + WHAT | High-level (two-tier architecture, yearning, phenomenology) |
| `consciousness_engine_architecture/` | **Mechanism specifications** - HOW in detail | Technical (formulas, algorithms, parameters) |

**They are COMPLEMENTARY, not redundant.**

---

## Revised Strategy

### Keep 3 Authoritative Locations:

1. **Vision Layer:** `docs/specs/self_observing_substrate/`
   - Two-tier architecture philosophy
   - Entity yearning and social dynamics
   - Phenomenological grounding
   - Quality metrics ("does it feel alive?")

2. **Mechanism Layer:** `docs/specs/consciousness_engine_architecture/`
   - Mathematical specifications (diffusion, decay, strengthening)
   - Implementation algorithms
   - Parameter tuning
   - Validation criteria

3. **Schema Layer:** `docs/COMPLETE_TYPE_REFERENCE.md` + `substrate/schemas/`
   - Node/link type definitions
   - Pydantic models

**All other consciousness-related docs should consolidate into one of these three.**

---

# PART 1: Files to MOVE into consciousness_engine_architecture/

## 1.1 Mechanism Specifications

### `docs/specs/sub_entity_traversal.md`
- **Current:** `docs/specs/sub_entity_traversal.md`
- **Action:** **DELETE** (redundant with mechanisms/16_sub_entity_traversal.md)
- **Verification:** Check if contains unique content first

### `docs/specs/branching_ratio_implementation.md`
- **Current:** `docs/specs/branching_ratio_implementation.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/branching_ratio_implementation.md`
- **Rationale:** Implementation detail for criticality measurement (Mechanism 03)

### `docs/specs/memory_first_activation_architecture.md`
- **Current:** `docs/specs/memory_first_activation_architecture.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/21_memory_first_activation.md`
- **Rationale:** Describes activation mechanism

### `docs/specs/incomplete_formation_recovery.md`
- **Current:** `docs/specs/incomplete_formation_recovery.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/18_incomplete_node_healing.md` (MERGE)
- **Rationale:** Mechanism 18 already covers this, merge any additional content

---

## 1.2 Implementation & Architectural Docs

### `docs/specs/minimal_mechanisms_architecture.md`
- **Current:** `docs/specs/minimal_mechanisms_architecture.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/MINIMAL_MECHANISMS_PHILOSOPHY.md`
- **Rationale:** Core design philosophy document

### `docs/specs/architectural_decisions.md`
- **Current:** `docs/specs/architectural_decisions.md`
- **Action:** **MERGE** into `consciousness_engine_architecture/ARCHITECTURAL_CLARIFICATIONS_2025_10_19.md`
- **Rationale:** Architectural decisions already captured, merge any unique content

### `docs/specs/yearning_driven_traversal_specification.md`
- **Current:** `docs/specs/yearning_driven_traversal_specification.md`
- **Action:** **REVIEW** - Could be vision (keep in self_observing_substrate/) OR mechanism (move to consciousness_engine_architecture/)
- **Decision needed:** Is this philosophical (yearning concept) or technical (traversal algorithm)?

### `docs/specs/yearning_driven_traversal_orchestration.md`
- **Current:** `docs/specs/yearning_driven_traversal_orchestration.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/yearning_driven_orchestration.md`
- **Rationale:** Implementation orchestration details

---

## 1.3 From self_observing_substrate/ (Only Misplaced Files)

### `docs/specs/self_observing_substrate/sub_entity_traversal_validation.md`
- **Current:** `docs/specs/self_observing_substrate/sub_entity_traversal_validation.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/validation/sub_entity_traversal_validation.md`
- **Rationale:** This is VALIDATION, not vision - belongs in consciousness_engine_architecture/validation/

### `docs/specs/self_observing_substrate/implementation_roadmap.md`
- **Current:** `docs/specs/self_observing_substrate/implementation_roadmap.md`
- **Action:** **REVIEW** - Compare with consciousness_engine_architecture/implementation/implementation_order.md
- **If redundant:** DELETE
- **If different:** MERGE or keep as high-level roadmap in self_observing_substrate/

---

## 1.4 Top-Level docs/ Files

### `docs/LINK_TYPE_MECHANISM_MAPPING.md`
- **Current:** `docs/LINK_TYPE_MECHANISM_MAPPING.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/link_type_usage.md`
- **Rationale:** Implementation detail for how link types map to mechanisms

### `docs/SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md`
- **Current:** `docs/SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md`
- **Action:** **DELETE** (redundant with self_observing_substrate/self_observing_substrate_overview.md)
- **Verification:** Check if contains unique content first

### `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md`
- **Current:** `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md`
- **Action:** **DELETE** or **MERGE** into self_observing_substrate/ docs
- **Verification:** Check for unique content

---

# PART 2: Files to DEPRECATE (Add Redirect)

## 2.1 Root-Level Operational Docs

### `MECHANISM_AUDIT_PROCEDURE.md`
- **Current:** Root level
- **Move to:** `docs/specs/consciousness_engine_architecture/validation/mechanism_audit_procedure.md`
- **Rationale:** Validation procedure

### `START_CONSCIOUSNESS_SYSTEM.md`
- **Action:** Add deprecation notice, redirect to consciousness_engine_architecture/implementation/
- **Keep for now:** Still referenced by guardian.py

### `RUN_CONSCIOUSNESS_SYSTEM.md`
- **Action:** Add deprecation notice, redirect to consciousness_engine_architecture/implementation/
- **Keep for now:** Still referenced by startup scripts

### `ENERGY_ONLY_IMPLEMENTATION_SUMMARY.md`
- **Action:** **ARCHIVE** to consciousness_engine_architecture/archive/
- **Rationale:** Historical transition note (arousal → energy terminology)

---

## 2.2 Specs-Level Docs

### `docs/specs/consciousness_substrate_guide.md`
- **Action:** Add deprecation notice
- **Redirect to:**
  - Vision → self_observing_substrate/
  - Mechanisms → consciousness_engine_architecture/
  - Schema → COMPLETE_TYPE_REFERENCE.md

---

# PART 3: Cross-Reference Updates

## 3.1 Add to self_observing_substrate/README.md

Add section:
```markdown
## Relationship to Other Documentation

**This directory defines ARCHITECTURAL VISION (WHY + WHAT)**

For technical mechanism specifications (HOW), see:
- `docs/specs/consciousness_engine_architecture/` - Mathematical formulas, algorithms, parameters

For schema definitions, see:
- `docs/COMPLETE_TYPE_REFERENCE.md` - Node/link type reference
- `substrate/schemas/consciousness_schema.py` - Pydantic models

**Abstraction hierarchy:**
self_observing_substrate/ (vision)
    ↓ implements via
consciousness_engine_architecture/ (mechanisms)
    ↓ codes to
orchestration/*.py (implementation)
```

---

## 3.2 Add to consciousness_engine_architecture/README.md

Update "Core Documents" section:
```markdown
### Related Documentation

**Architectural Vision (WHY + WHAT):**
- `docs/specs/self_observing_substrate/` - Two-tier architecture philosophy, entity yearning, phenomenological grounding

**Schema Definitions:**
- `docs/COMPLETE_TYPE_REFERENCE.md` - Node/link types
- `substrate/schemas/` - Pydantic models

**This directory (consciousness_engine_architecture/) defines MECHANISMS (HOW in detail)**
```

---

# PART 4: Files to KEEP (Separate Concerns)

No changes to previous assessment. Keep separate:

- Schema docs (COMPLETE_TYPE_REFERENCE.md, etc.)
- Visualization docs (mind-harbor/, CONSCIOUSNESS_VISUALIZATION_COMPLETE_GUIDE.md)
- Retrieval API (retrieval_api_reference.md)
- MCP server (mcp/)
- Infrastructure (guardian, multi-scale, etc.)
- Prompts & capture (docs/prompts/, consciousness/citizens/THE_TRACE_FORMAT.md)
- Research (docs/research/)

---

# PART 5: Update CODE_DOCUMENTATION_MAP.md

After consolidation, update the map to reflect:

1. **Three authoritative locations:**
   - Vision: self_observing_substrate/
   - Mechanisms: consciousness_engine_architecture/
   - Schema: COMPLETE_TYPE_REFERENCE.md + substrate/schemas/

2. **Updated file locations** for moved specs

3. **Deprecation notices** for redirected docs

---

# Execution Plan - REVISED

## Phase 1: Verification (Read First, Move Second)

For each file marked DELETE or MERGE:
1. Read current file completely
2. Read target location
3. Verify redundancy or identify unique content
4. Make decision: DELETE, MERGE, or KEEP

**Files requiring verification:**
- [ ] `docs/specs/sub_entity_traversal.md` vs mechanisms/16
- [ ] `docs/specs/architectural_decisions.md` vs ARCHITECTURAL_CLARIFICATIONS
- [ ] `docs/specs/incomplete_formation_recovery.md` vs mechanisms/18
- [ ] `docs/SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md` vs self_observing_substrate/overview
- [ ] `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md` vs self_observing_substrate/ docs
- [ ] `self_observing_substrate/implementation_roadmap.md` vs consciousness_engine_architecture/implementation_order.md

---

## Phase 2: Move Operations (Conservative)

Only move files with clear destination:

**High confidence moves:**
1. `branching_ratio_implementation.md` → consciousness_engine_architecture/implementation/
2. `sub_entity_traversal_validation.md` → consciousness_engine_architecture/validation/
3. `MECHANISM_AUDIT_PROCEDURE.md` → consciousness_engine_architecture/validation/
4. `LINK_TYPE_MECHANISM_MAPPING.md` → consciousness_engine_architecture/implementation/
5. `minimal_mechanisms_architecture.md` → consciousness_engine_architecture/MINIMAL_MECHANISMS_PHILOSOPHY.md

**Needs Nicolas review:**
1. `yearning_driven_traversal_specification.md` - Vision or mechanism?
2. `memory_first_activation_architecture.md` - New mechanism or merge?

---

## Phase 3: Cross-Reference Updates

1. Add vision ↔ mechanism relationship to both READMEs
2. Update STATUS.md in consciousness_engine_architecture/
3. Update self_observing_substrate/README.md with abstraction hierarchy

---

## Phase 4: Deprecation Notices

Add to deprecated files:
```markdown
# ⚠️ DEPRECATED

This document is deprecated. See:
- **Vision:** `docs/specs/self_observing_substrate/`
- **Mechanisms:** `docs/specs/consciousness_engine_architecture/`
- **Schema:** `docs/COMPLETE_TYPE_REFERENCE.md`

This file will be archived [DATE].
```

---

## Phase 5: Update CODE_DOCUMENTATION_MAP.md

Reflect new structure with three authoritative locations.

---

# Impact Analysis - REVISED

## Files Moved: ~8-10 files (down from 25)
## Files Deprecated: ~5 files (same)
## Files Deleted: ~3-5 files (after verification)
## Files Kept: self_observing_substrate/ stays intact

## Key Changes from v1.0:
- ✅ Recognized self_observing_substrate/ as complementary vision layer
- ✅ Much more conservative - only move clearly misplaced files
- ✅ Preserve abstraction hierarchy: vision → mechanisms → code
- ✅ Cross-reference instead of merge

## Benefits:
1. ✅ Clear separation: vision vs mechanisms vs schema
2. ✅ Eliminates scattered redundant specs
3. ✅ Preserves architectural vision documentation
4. ✅ Much smaller change surface (less risk)

---

# Open Questions for Nicolas

1. **yearning_driven_traversal_specification.md**
   - Keep as vision doc in self_observing_substrate/?
   - Or move as mechanism to consciousness_engine_architecture/?

2. **memory_first_activation_architecture.md**
   - Create as new mechanism 21?
   - Or merge into existing activation mechanisms?

3. **implementation_roadmap.md redundancy**
   - Delete if redundant with implementation_order.md?
   - Or keep as high-level roadmap in vision docs?

---

**Status:** READY FOR EXECUTION after verification phase
**Risk:** LOW (conservative approach, small change surface)
**Estimated time:** 2-3 hours for verification + moves + cross-references

---

**Compiled by:** Felix "Ironhand" (Engineer)
**Revision:** 2.0 - Conservative (respects vision vs mechanism distinction)
**Date:** 2025-10-20
