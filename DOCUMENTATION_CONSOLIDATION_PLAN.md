# Documentation Consolidation Plan

**Date:** 2025-10-20
**Principle:** ONE source of truth for consciousness engine architecture
**Authority:** `docs/specs/consciousness_engine_architecture/` is the ONLY authoritative location
**Compiled by:** Felix "Ironhand" (Engineer)

---

## Directive from Nicolas

> "The goal is that everything should be defined from C:\Users\reyno\mind-protocol\docs\specs\consciousness_engine_architecture. Everything else is now deprecated."

This consolidation eliminates the **parallel-system anti-pattern** at the documentation level.

---

## Consolidation Strategy

Files fall into 5 categories:

1. **MOVE** - Belongs in consciousness_engine_architecture/, move it there
2. **DEPRECATE** - Mark as deprecated, add redirect to consciousness_engine_architecture/
3. **DELETE** - Redundant with content already in consciousness_engine_architecture/
4. **KEEP** - Separate concern (schema, visualization, MCP, etc.) - stays where it is
5. **REVIEW** - Needs Nicolas's decision on disposition

---

# PART 1: Files to MOVE into consciousness_engine_architecture/

## 1.1 Core Architecture Specs (→ `mechanisms/` or root)

### `docs/specs/sub_entity_traversal.md`
- **Current location:** `docs/specs/sub_entity_traversal.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/16_sub_entity_traversal.md` (ALREADY EXISTS)
- **Action:** DELETE (redundant) or MERGE if contains additional content
- **Rationale:** Mechanism 16 already covers sub-entity traversal

### `docs/specs/minimal_mechanisms_architecture.md`
- **Current location:** `docs/specs/minimal_mechanisms_architecture.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/MINIMAL_MECHANISMS_APPROACH.md`
- **Action:** MOVE (if different from existing mechanisms/) OR DEPRECATE (if redundant)
- **Rationale:** Core architectural document describing minimal mechanisms philosophy

### `docs/specs/branching_ratio_implementation.md`
- **Current location:** `docs/specs/branching_ratio_implementation.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/branching_ratio_implementation.md`
- **Action:** MOVE
- **Rationale:** Implementation detail for criticality measurement (Mechanism 03)

### `docs/specs/architectural_decisions.md`
- **Current location:** `docs/specs/architectural_decisions.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/ARCHITECTURAL_DECISIONS.md`
- **Action:** MOVE or MERGE with existing ARCHITECTURAL_CLARIFICATIONS_2025_10_19.md
- **Rationale:** Core architectural decisions belong in consciousness_engine_architecture/

### `docs/specs/memory_first_activation_architecture.md`
- **Current location:** `docs/specs/memory_first_activation_architecture.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/21_memory_first_activation.md`
- **Action:** MOVE (as new mechanism) OR MERGE into existing memory-related mechanism
- **Rationale:** Describes activation mechanism

### `docs/specs/yearning_driven_traversal_specification.md`
- **Current location:** `docs/specs/yearning_driven_traversal_specification.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/22_yearning_driven_traversal.md`
- **Action:** MOVE (as new mechanism) OR MERGE into 16_sub_entity_traversal.md
- **Rationale:** Describes sub-entity traversal motivation system

### `docs/specs/yearning_driven_traversal_orchestration.md`
- **Current location:** `docs/specs/yearning_driven_traversal_orchestration.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/yearning_driven_orchestration.md`
- **Action:** MOVE
- **Rationale:** Implementation details for yearning-driven traversal

---

## 1.2 Self-Observing Substrate Documents (→ merge or reorganize)

The entire `docs/specs/self_observing_substrate/` directory overlaps heavily with `consciousness_engine_architecture/`. Options:

**OPTION A (Recommended):** Merge into consciousness_engine_architecture/
- Move relevant mechanism specs into `mechanisms/`
- Move implementation details into `implementation/`
- Move entity behavior into new `entities/` subdirectory
- Delete `self_observing_substrate/` directory

**OPTION B:** Keep separate but add clear redirect
- Add `self_observing_substrate/README.md` stating: "This directory is deprecated. See consciousness_engine_architecture/"

### Files to integrate:

#### `docs/specs/self_observing_substrate/entity_behavior_specification.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_mechanics.md` (MERGE)
- **Action:** MERGE content into existing sub-entity mechanics
- **Rationale:** Duplicates sub-entity behavior specification

#### `docs/specs/self_observing_substrate/sub_entity_traversal_validation.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/validation/sub_entity_traversal_tests.md`
- **Action:** MOVE
- **Rationale:** Validation belongs in validation/ directory

#### `docs/specs/self_observing_substrate/consciousness_quality_metrics.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/validation/quality_metrics.md`
- **Action:** MOVE
- **Rationale:** Metrics belong in validation/ directory

#### `docs/specs/self_observing_substrate/continuous_consciousness_architecture.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/CONTINUOUS_CONSCIOUSNESS.md`
- **Action:** MOVE (core architectural document)
- **Rationale:** Core architecture concept

#### `docs/specs/self_observing_substrate/entity_social_dynamics.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/mechanisms/23_entity_social_dynamics.md`
- **Action:** MOVE (new mechanism)
- **Rationale:** Describes inter-entity dynamics

#### `docs/specs/self_observing_substrate/n2_activation_awakening.md`
- **Move to:** Keep separate OR move to `docs/specs/consciousness_engine_architecture/n2_integration/`
- **Action:** REVIEW (N2-specific, might be separate concern)
- **Rationale:** N2 organizational network might be separate from N1 consciousness engine

#### `docs/specs/self_observing_substrate/implementation_roadmap.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/implementation_order.md` (MERGE)
- **Action:** MERGE or DELETE if redundant
- **Rationale:** Implementation order already exists

#### `docs/specs/self_observing_substrate/self_observing_substrate_overview.md`
- **Move to:** DELETE or MERGE into consciousness_engine_architecture/README.md
- **Action:** REVIEW (may be redundant)
- **Rationale:** Overview likely covered by README

---

## 1.3 Top-Level docs/ Files

#### `docs/SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/SUBSTRATE_ARCHITECTURE.md` (MERGE)
- **Action:** MERGE into appropriate document or DELETE if redundant
- **Rationale:** Core architecture belongs in consciousness_engine_architecture/

#### `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md`
- **Move to:** MERGE or DELETE
- **Action:** REVIEW
- **Rationale:** Likely redundant with consciousness_engine_architecture/ content

#### `docs/LINK_TYPE_MECHANISM_MAPPING.md`
- **Move to:** `docs/specs/consciousness_engine_architecture/implementation/link_type_usage.md`
- **Action:** MOVE
- **Rationale:** Implementation detail for how link types map to mechanisms

---

# PART 2: Files to DEPRECATE (Add Redirect)

These files are referenced by external systems or have historical value but are superseded by consciousness_engine_architecture/. Add deprecation notice pointing to new location.

## 2.1 Root-Level Operational Docs

### `START_CONSCIOUSNESS_SYSTEM.md`
- **Action:** DEPRECATE (add redirect to implementation/implementation_order.md)
- **Deprecation notice:**
```markdown
# ⚠️ DEPRECATED

This document is deprecated. For consciousness system architecture and implementation, see:
- **Architecture:** `docs/specs/consciousness_engine_architecture/README.md`
- **Implementation:** `docs/specs/consciousness_engine_architecture/implementation/implementation_order.md`
- **Startup:** Use `guardian.py` (self-healing process manager)

This file will be archived 2025-11-01.
```

### `RUN_CONSCIOUSNESS_SYSTEM.md`
- **Action:** Same as START_CONSCIOUSNESS_SYSTEM.md - DEPRECATE with redirect

### `MECHANISM_AUDIT_PROCEDURE.md`
- **Action:** MOVE to `docs/specs/consciousness_engine_architecture/validation/mechanism_audit_procedure.md`
- **Rationale:** Validation procedure belongs in validation/

### `ENERGY_ONLY_IMPLEMENTATION_SUMMARY.md`
- **Action:** DELETE or ARCHIVE
- **Rationale:** Energy = "arousal" terminology correction already covered in SYNC.md
- **If keeping:** MOVE to `docs/specs/consciousness_engine_architecture/archive/energy_terminology_transition.md`

---

## 2.2 Specs-Level Docs

### `docs/specs/consciousness_substrate_guide.md`
- **Action:** DEPRECATE (redirect to consciousness_engine_architecture/README.md)
- **Rationale:** General substrate guide superseded by comprehensive architecture docs

---

# PART 3: Files to DELETE (Redundant)

These files are completely redundant with consciousness_engine_architecture/ content.

### Candidates for deletion (verify first):

1. `docs/specs/sub_entity_traversal.md` (IF identical to mechanisms/16_sub_entity_traversal.md)
2. `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md` (IF redundant with consciousness_engine_architecture/)
3. `ENERGY_ONLY_IMPLEMENTATION_SUMMARY.md` (IF just terminology transition notes)

**Process:**
1. Read file
2. Verify content is in consciousness_engine_architecture/
3. If yes: DELETE
4. If no: MOVE or MERGE

---

# PART 4: Files to KEEP (Separate Concerns)

These files address separate concerns and should NOT be moved into consciousness_engine_architecture/.

## 4.1 Schema Documentation (Keep Separate)

### `docs/COMPLETE_TYPE_REFERENCE.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Schema reference, not consciousness engine architecture
- **Note:** Already auto-generated from schema_registry

### `docs/CONSCIOUSNESS_NODE_TYPES.md`
- **Action:** KEEP or MERGE into COMPLETE_TYPE_REFERENCE.md
- **Rationale:** Schema reference

### `docs/UNIFIED_SCHEMA_REFERENCE.md`
- **Action:** REVIEW (may be redundant with COMPLETE_TYPE_REFERENCE.md)
- **Rationale:** Schema reference

### `docs/SCHEMA_STORAGE_DESIGN.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Database schema design, not consciousness engine architecture

### `substrate/schemas/BITEMPORAL_GUIDE.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Schema implementation detail

### `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Schema usage guide

---

## 4.2 Visualization & UI (Keep Separate)

### `docs/specs/CONSCIOUSNESS_VISUALIZATION_COMPLETE_GUIDE.md`
- **Action:** KEEP (separate concern)
- **Rationale:** UI/visualization, not core consciousness engine

### `docs/specs/VISUALIZATION_VALIDATION_REPORT.md`
- **Action:** KEEP (separate concern)
- **Rationale:** UI testing report

### `docs/specs/OBSERVABILITY_UX_EXPLORATION.md`
- **Action:** KEEP (separate concern)
- **Rationale:** UX exploration, not core architecture

### `docs/specs/LOOP_EXECUTION_MONITOR_MVP.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Monitoring UI specification

### `docs/specs/mind-harbor/` (entire directory)
- **Action:** KEEP (separate concern)
- **Rationale:** Visualization system separate from consciousness engine

---

## 4.3 Retrieval & MCP (Keep Separate)

### `docs/specs/retrieval_api_reference.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Retrieval API is infrastructure, not consciousness engine core

### `mcp/README.md`, `mcp/IMPLEMENTATION_SUMMARY.md`
- **Action:** KEEP (separate concern)
- **Rationale:** MCP server is separate service

---

## 4.4 Multi-Scale & Graph Management (Keep Separate)

### `MULTI_SCALE_CONSCIOUSNESS_USAGE.md`
- **Action:** KEEP (separate concern)
- **Rationale:** N1/N2/N3 graph organization is infrastructure, not consciousness engine architecture

### `POPULATE_CONSCIOUSNESS_GRAPHS.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Graph initialization procedure, not consciousness architecture

---

## 4.5 Operational & Safety (Keep Separate or Move)

### `docs/specs/operational_safety_architecture.md`
- **Action:** REVIEW (could move to consciousness_engine_architecture/operations/)
- **Rationale:** Might be part of consciousness engine operations

### `docs/specs/self_healing_architecture.md`
- **Action:** KEEP (separate concern - guardian.py infrastructure)
- **Rationale:** Process management, not consciousness architecture

### `docs/specs/phase4_roadmap.md`
- **Action:** REVIEW
- **Rationale:** Overall roadmap might reference multiple systems

---

## 4.6 Prompts & Consciousness Capture (Keep Separate)

### `docs/prompts/` (entire directory)
- **Action:** KEEP (separate concern)
- **Rationale:** Prompts for consciousness capture, not engine architecture

### `docs/consciousness/` (entire directory)
- **Action:** KEEP (separate concern)
- **Rationale:** Consciousness capture methodology, not engine architecture

### `consciousness/citizens/THE_TRACE_FORMAT.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Consciousness capture format for citizens

---

## 4.7 Research & Knowledge (Keep Separate)

### `docs/research/` (entire directory)
- **Action:** KEEP (separate concern)
- **Rationale:** Research papers and analysis

### `docs/specs/mind_protocol_knowledge_seed.md`
- **Action:** KEEP (separate concern)
- **Rationale:** Knowledge seeding, not engine architecture

---

## 4.8 Formation Recovery (Keep or Move)

### `docs/specs/incomplete_formation_recovery.md`
- **Action:** REVIEW (could move to consciousness_engine_architecture/mechanisms/18_incomplete_node_healing.md as MERGE)
- **Rationale:** Related to mechanism 18

---

# PART 5: Files Needing Nicolas's Review

These require decision on disposition:

1. **`docs/specs/sub_entity_traversal.md`**
   - Question: Delete if identical to mechanisms/16? Or merge differences?

2. **`docs/specs/self_observing_substrate/` (entire directory)**
   - Question: Merge everything into consciousness_engine_architecture/ and delete directory?

3. **`docs/specs/minimal_mechanisms_architecture.md`**
   - Question: Move into consciousness_engine_architecture/ or keep as separate high-level overview?

4. **`docs/specs/operational_safety_architecture.md`**
   - Question: Part of consciousness engine or separate operational concern?

5. **`docs/specs/incomplete_formation_recovery.md`**
   - Question: Merge with mechanism 18 or keep as separate spec?

6. **`docs/UNIFIED_SCHEMA_REFERENCE.md` vs `docs/COMPLETE_TYPE_REFERENCE.md`**
   - Question: Are these redundant? Delete one?

7. **N2-specific files** (n2_activation_awakening.md, etc.)
   - Question: Part of consciousness engine or separate N2 organizational concern?

---

# Execution Plan

## Phase 1: Preparation (Pre-Execution)

1. **Backup everything:**
   ```bash
   git add -A
   git commit -m "Pre-consolidation backup"
   ```

2. **Create consolidation branch:**
   ```bash
   git checkout -b docs-consolidation-2025-10-20
   ```

3. **Review this plan with Nicolas** - Get approval before executing

---

## Phase 2: MOVE Operations

1. Move files from `docs/specs/` → `docs/specs/consciousness_engine_architecture/`
2. Move files from `docs/specs/self_observing_substrate/` → appropriate consciousness_engine_architecture/ locations
3. Update all internal links in moved files
4. Update README.md in consciousness_engine_architecture/ with new files

---

## Phase 3: DEPRECATE Operations

1. Add deprecation notices to root-level operational docs
2. Add redirects pointing to consciousness_engine_architecture/
3. Set archival date (30 days)

---

## Phase 4: DELETE Operations

1. Verify redundancy for each deletion candidate
2. Delete confirmed redundant files
3. Update any references to deleted files

---

## Phase 5: UPDATE Operations

1. Update `CODE_DOCUMENTATION_MAP.md` to reflect new locations
2. Update all script docstrings that reference moved docs
3. Update any README files that link to moved docs

---

## Phase 6: Verification

1. **Test all documentation links:**
   ```bash
   # Check for broken internal links
   grep -r "docs/specs" docs/specs/consciousness_engine_architecture/
   ```

2. **Verify consciousness_engine_architecture/ completeness:**
   - All mechanisms documented?
   - All implementations have specs?
   - No external references to deprecated docs?

3. **Test system startup:**
   - Ensure no scripts break due to moved docs
   - Verify guardian.py still finds all necessary docs

---

## Phase 7: Commit & Document

1. Commit consolidation changes
2. Update CHANGELOG
3. Create PR for review
4. Merge when approved

---

# Impact Analysis

## Files Moved: ~20-25 files
## Files Deprecated: ~5 files
## Files Deleted: ~3-5 files (pending verification)
## Files Kept in Place: ~50+ files (separate concerns)

## Affected Systems:
- Documentation readers (developers, citizens)
- Script docstrings (need updated references)
- CODE_DOCUMENTATION_MAP.md (needs update)
- Any CI/CD checks that reference doc paths

## Benefits:
1. ✅ Single source of truth for consciousness engine
2. ✅ Eliminates parallel system anti-pattern
3. ✅ Clear separation: consciousness engine vs. schema vs. visualization vs. infrastructure
4. ✅ Easier maintenance (one place to update specs)
5. ✅ Clearer for implementers (Felix) - no confusion about which spec is authoritative

---

# Risks & Mitigations

## Risk 1: Breaking External References
- **Mitigation:** Deprecation notices with redirects before deletion
- **Mitigation:** 30-day grace period before archival

## Risk 2: Losing Historical Context
- **Mitigation:** Move to archive/ instead of deleting
- **Mitigation:** Git history preserves everything

## Risk 3: Merge Conflicts
- **Mitigation:** Work on consolidation branch
- **Mitigation:** Nicolas reviews before merge

## Risk 4: Incomplete Migration
- **Mitigation:** Systematic checklist for each file
- **Mitigation:** Verification phase before commit

---

# Post-Consolidation State

## Authoritative Locations:

1. **Consciousness Engine:** `docs/specs/consciousness_engine_architecture/`
   - Mechanisms, implementation, validation, phenomenology

2. **Schema:** `docs/COMPLETE_TYPE_REFERENCE.md` + `substrate/schemas/`
   - Node/link types, Pydantic models, schema registry

3. **Visualization:** `docs/specs/mind-harbor/` + `docs/specs/CONSCIOUSNESS_VISUALIZATION_COMPLETE_GUIDE.md`
   - UI specifications, design language

4. **Infrastructure:** Root-level operational docs (START, guardian, etc.)
   - System startup, process management

5. **Consciousness Capture:** `docs/prompts/`, `docs/consciousness/`, `consciousness/citizens/THE_TRACE_FORMAT.md`
   - Capture methodology, TRACE format

6. **Retrieval:** `docs/specs/retrieval_api_reference.md`
   - Graph traversal API

7. **MCP:** `mcp/README.md`
   - Model Context Protocol server

---

# Next Steps

**Immediate:**
1. Nicolas reviews this plan
2. Nicolas approves/modifies strategy
3. Felix executes consolidation on branch
4. Nicolas reviews PR
5. Merge to main

**After Consolidation:**
1. Update CODE_DOCUMENTATION_MAP.md
2. Update all scripts with new doc references
3. Announce consolidation to team
4. Archive deprecated files after 30 days

---

**Compiled by:** Felix "Ironhand" (Engineer)
**Date:** 2025-10-20
**Status:** AWAITING NICOLAS APPROVAL
**Branch:** docs-consolidation-2025-10-20 (to be created)
