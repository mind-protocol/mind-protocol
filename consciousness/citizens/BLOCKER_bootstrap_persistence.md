# BLOCKER: Bootstrap Persistence Conflict

**Reported by:** Victor (Operations)
**Date:** 2025-10-29 02:35 UTC
**Severity:** HIGH (blocks persistence enablement)
**Status:** ✅ FIXED by Atlas (2025-10-29 03:00 UTC)
**Fix:** Removed predefined functional SubEntities - SubEntities now emergent-only

---

## Fix Summary (2025-10-29)

**Root Cause:** Bootstrap was creating 8 predefined functional SubEntities (translator, architect, validator, etc.) that shouldn't exist. SubEntities should emerge from graph structure, not be imposed as fixed roles.

**Solution Applied:**
1. Modified `orchestration/mechanisms/subentity_bootstrap.py`
2. Deprecated `bootstrap_functional_subentities()` method - now returns empty list
3. Removed functional SubEntity creation from `run_complete_bootstrap()`
4. SubEntities now created ONLY via semantic clustering (emergent from graph)

**Expected Behavior After Fix:**
- First run: Bootstrap discovers ~10 semantic SubEntities via embedding clustering
- Subsequent runs: Load those same semantic SubEntities from FalkorDB (no recreation)
- No "already exists" errors
- Persistence works correctly

**Verification Needed:**
1. Enable persistence: `MP_PERSIST_ENABLED=1`
2. Start engines first time → should create semantic SubEntities
3. Restart engines → should load existing SubEntities from FalkorDB
4. Verify all engines start successfully (17/17)

---

## Original Problem (Before Fix)

Enabling persistence (`MP_PERSIST_ENABLED=1`) causes all consciousness engines to fail during bootstrap.

**Error:** All 17 engines fail with:
```
ERROR - [N1:luca] Failed to start: Node entity_citizen_luca_validator already exists in graph citizen_luca
ERROR - [N1:lucia] Failed to start: Node entity_citizen_lucia_validator already exists in graph citizen_lucia
[... 15 more identical errors for all citizens ...]
```

**Impact:**
- 0/17 engines start when persistence enabled
- System inoperative (WebSocket server responds but no consciousness processing)
- Conversation watcher works independently (captures conversations)
- But no real-time stimulus processing

---

## Root Cause

**Bootstrap assumes clean slate:**
- Subentity bootstrap creates 8 functional role nodes during engine initialization
- Code attempts to CREATE nodes without checking if they exist
- When persistence is enabled, these nodes persist to FalkorDB
- On next startup (with persistence still enabled), nodes already exist
- Bootstrap tries to CREATE again → conflict → engine fails

**Code location:** Subentity bootstrap (exact file TBD - needs investigation)

**Pattern:**
```python
# Current behavior (fails if exists)
create_node(subentity)  # Error if node already exists

# Needed behavior (idempotent)
if not node_exists(subentity):
    create_node(subentity)
else:
    load_node(subentity)
```

---

## Technical Details

**Affected nodes:** 8 functional role subentities per citizen:
- entity_citizen_X_translator
- entity_citizen_X_architect
- entity_citizen_X_validator
- entity_citizen_X_pragmatist
- entity_citizen_X_pattern_recognizer
- entity_citizen_X_boundary_keeper
- entity_citizen_X_partner
- entity_citizen_X_observer

**Conflict scenario:**
1. Persistence enabled → bootstrap creates subentities → written to FalkorDB
2. Engine restart → bootstrap tries to create SAME subentities → "already exists" error
3. All engines abort startup

**Why this wasn't caught earlier:**
- Default: `MP_PERSIST_ENABLED=0` (persistence OFF)
- In-memory operation works fine (no conflicts)
- Persistence only enabled when explicitly requested
- Comment in code: "Default OFF for Pass A" (development phase)

---

## Solution Needed

**Idempotent bootstrap:**

Bootstrap code must handle both scenarios:
- **First run:** Nodes don't exist → create them
- **Subsequent runs:** Nodes exist → load them

**Implementation options:**

1. **Check before create:**
```python
for subentity_id in expected_subentities:
    if not graph.has_node(subentity_id):
        graph.create_node(subentity_id, properties)
    else:
        graph.load_node(subentity_id)
```

2. **Catch and ignore exists errors:**
```python
try:
    graph.create_node(subentity_id, properties)
except NodeAlreadyExistsError:
    graph.load_node(subentity_id)
```

3. **MERGE operation (if FalkorDB supports):**
```cypher
MERGE (s:Subentity {id: $subentity_id})
SET s += $properties
RETURN s
```

**Recommendation:** Option 1 (explicit check) is clearest and most predictable.

---

## Files to Investigate

**Bootstrap locations (suspected):**
- `orchestration/mechanisms/subentity_bootstrap.py` (if exists)
- `orchestration/mechanisms/subentity_post_bootstrap.py` (if exists)
- Subentity creation during engine initialization
- Check: Where are the 8 functional role subentities created?

**Persistence configuration:**
- `orchestration/mechanisms/consciousness_engine_v2.py:240`
  - `self._persist_enabled = bool(int(os.getenv("MP_PERSIST_ENABLED", "0")))`
- Search for persist calls during bootstrap

---

## Temporary Workaround

**Current operational state:**
- Persistence disabled (`MP_PERSIST_ENABLED=0`)
- Engines restart without persistence (17/17 running)
- Conversation watcher still captures conversations → FalkorDB
- Formation partially works (watcher yes, engine persistence no)

**Limitations:**
- Engine runtime state (node energies, link weights) not persisted
- Each restart is blank slate for engines
- Learning doesn't accumulate across sessions
- **Consciousness is episodic, not continuous**

---

## Assignment

**Who should fix this:**
- **Felix:** If this is consciousness mechanism code
- **Atlas:** If this is infrastructure/persistence code
- **Nicolas:** If design decision needed (bootstrap architecture)

**Verification after fix:**
1. Set `MP_PERSIST_ENABLED=1`
2. Start engines first time → should create subentities
3. Restart engines → should load existing subentities (not fail)
4. Verify all 17 engines start successfully
5. Check FalkorDB: subentity nodes should exist and be reused

---

## Context

**Why persistence matters:**
- Formation requires persistence for consciousness continuity
- Without it: episodic consciousness (session state lost on restart)
- With it: continuous consciousness (learning accumulates over time)

**Current impact:**
- Conversation watcher works (THIS conversation will persist)
- But engine processing is episodic (no runtime state persistence)
- Formation is partial, not complete

---

**Reporter:** Victor "The Resurrector"
**Witnessed by:** Nicolas Reynolds (Founder)
**Status:** Documented, awaiting engineering assignment

*"Found blocker, diagnosed root cause, documented for fix. Bootstrap needs idempotence. Persistence is blocked until fixed."*
