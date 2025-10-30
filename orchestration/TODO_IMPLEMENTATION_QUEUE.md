# Implementation Queue - Orchestration Layer

**Purpose:** Track specs ready for implementation but not yet prioritized

**Last Updated:** 2025-10-22

---

## High Priority (Next Sprint)

*Empty - focus on emotion system GraphCanvas integration*

---

## Medium Priority (Future)

### Identity Conflict Resolution
**Spec:** `docs/specs/v2/emotion/identity_conflict_resolution.md` (if exists) or related mechanism
**Status:** 📋 Marked for later implementation
**Complexity:** Medium-High
**Dependencies:**
- Emotion system (✅ complete)
- Entity layer (✅ complete)
- Identity tracking mechanisms

**Estimated Effort:** 1-2 days
**Assigned:** TBD
**Priority Reason:** Marked by Nicolas for future implementation

**What it likely involves:**
- Detecting when multiple subentities have conflicting goals/identities
- Resolution mechanisms (consensus, priority-based, complementarity-driven)
- Observability for identity coherence vs fragmentation

**Blocked by:** Nothing - can be implemented when prioritized

---

## Low Priority (Backlog)

*Add items as specs are completed*

---

## Notes

- Items move to "High Priority" when dependencies complete AND team capacity available
- Each item should have: Spec location, complexity estimate, dependencies, effort estimate
- Mark blockers explicitly (technical debt, missing specs, capacity constraints)

---

**Process:**
1. Spec completes → Add to this queue with assessment
2. Team reviews queue in planning sessions
3. Items move to "High Priority" when ready
4. Implementation → Update SCRIPT_MAP.md → Remove from queue
