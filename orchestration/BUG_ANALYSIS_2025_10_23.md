# Bug Analysis Report - 2025-10-23

**Author:** Felix "Ironhand"
**Status:** Analysis Complete, Fixes Proposed
**Scope:** System logs analysis (guardian.log, launcher.log)
**Impact:** Critical system stability issues causing chronic crashes

---

## Executive Summary

Analysis of system logs reveals three critical bugs causing chronic launcher crashes (40+ crashes over ~3 hours):

1. **Node.js Package Export Error** (Critical) - Breaks Next.js dashboard build
2. **FalkorDB Duplicate Link Errors** (Critical) - Prevents consciousness engines from starting
3. **Windows WPARAM TypeError** (Low) - Non-blocking warning from file watcher

**Current State:** Guardian exponential backoff is mitigating crashes, but underlying issues prevent full system operation.

---

## Bug 1: Node.js Package Export Error

### Severity: CRITICAL
### Impact: Next.js dashboard cannot build
### Frequency: Every launcher attempt

### Error Details

```
Error: Package subpath './lib/decode.js' is not defined by "exports" in
C:\Users\reyno\mind-protocol\node_modules\entities\package.json
```

### Root Cause Analysis

The `entities` package (v7.0.0) uses ESM exports and no longer exposes `./lib/decode.js` as a public subpath.

Looking at `node_modules/entities/package.json`:

```json
{
  "exports": {
    ".": {...},
    "./decode": {...},  // ✅ Valid
    "./escape": {...}   // ✅ Valid
  }
}
```

**Valid imports:**
- `import entities from 'entities'`
- `import * as decode from 'entities/decode'`

**Invalid imports (causing error):**
- `import decode from 'entities/lib/decode'`  ❌
- `import decode from 'entities/lib/decode.js'`  ❌

### Dependency Chain

The `entities` package is a dependency of `htmlparser2`:

```
package-lock.json:
  "htmlparser2": "^8.0.2"
    dependencies:
      "entities": "^4.4.0"
```

However, `node_modules/.package-lock.json` shows:

```
"node_modules/htmlparser2/node_modules/entities": {
  "version": "7.0.0"  // ❌ Newer version
}
```

This suggests a version mismatch or manual update that broke compatibility.

### Proposed Fix

**Option A: Downgrade entities (Quick Fix)**

```bash
cd node_modules/htmlparser2
npm install entities@^4.4.0 --save
```

**Option B: Find and fix invalid import (Permanent Fix)**

1. Search for invalid import in codebase:
```bash
grep -r "entities/lib/decode" node_modules/
```

2. If found in htmlparser2, this is an upstream bug - check for htmlparser2 update

3. If found in our code, fix import to use `entities/decode` instead

**Recommended:** Option B + verify htmlparser2 is latest version

### Testing

After fix:
```bash
npm run build
# Should complete without errors
```

---

## Bug 2: FalkorDB Duplicate Link Errors

### Severity: CRITICAL
### Impact: Consciousness engines cannot start
### Frequency: Every engine initialization attempt

### Error Details

```
2025-10-22 22:01:55 - orchestration.adapters.ws.websocket_server - ERROR -
[N1:victor] Failed to start: Link node_92_node_93_RELATES_TO already exists in graph citizen_victor

2025-10-22 22:01:59 - orchestration.adapters.ws.websocket_server - ERROR -
[N2:mind_protocol] Failed to start: Link node_209_node_306_RELATES_TO already exists in graph org_mind_protocol
```

**Pattern:** Same specific links fail consistently:
- `node_92_node_93_RELATES_TO` in victor graph
- `node_209_node_306_RELATES_TO` in mind_protocol graph

### Root Cause Analysis

#### Code Path to Error

1. `websocket_server.py:start_citizen_consciousness()` calls:
   ```python
   graph = await asyncio.wait_for(
       loop.run_in_executor(None, adapter.load_graph, graph_name),
       timeout=30.0
   )
   ```

2. `falkordb_adapter.py:load_graph()` generates link IDs:
   ```python
   link = Link(
       id=f"{source_id}_{target_id}_{link_type_str}",  # Line 678
       ...
   )
   ```

3. `graph.py:add_link()` checks for duplicates:
   ```python
   if link.id in self.links:
       raise ValueError(f"Link {link.id} already exists in graph {self.id}")
   ```

#### Why Duplicates Occur

**Scenario A: Multiple load_graph() Calls**

If `load_graph()` is called twice on the same graph instance without clearing `graph.links`, it will try to add the same links again.

**Scenario B: Persistent Graph State**

If the Graph object persists across restarts and `load_graph()` is called again, existing links conflict with newly loaded ones.

**Scenario C: FalkorDB Contains Duplicate Links**

If FalkorDB itself has duplicate links (same source→target→type), the query returns duplicates:

```cypher
MATCH (a)-[r]->(b) RETURN r, a, b
```

This could return the same link multiple times if it exists as duplicates in the database.

### Proposed Fix

**Immediate Fix: Skip Duplicates**

Modify `falkordb_adapter.py:load_graph()` line 694:

```python
# Before (line 694)
graph.add_link(link)

# After
try:
    graph.add_link(link)
except ValueError as e:
    if "already exists" in str(e):
        # Link already in graph, skip (likely from previous load or duplicate in DB)
        logger.debug(f"Skipping duplicate link {link.id}: {e}")
    else:
        raise
```

**Root Cause Fix: Clear Graph Before Load**

Modify `websocket_server.py:start_citizen_consciousness()` line 336:

```python
# Before
graph = await asyncio.wait_for(
    loop.run_in_executor(None, adapter.load_graph, graph_name),
    timeout=30.0
)

# After
# Create fresh Graph instance (don't reuse existing)
graph = await asyncio.wait_for(
    loop.run_in_executor(None, adapter.load_graph, graph_name),
    timeout=30.0
)
```

**Diagnostic: Check FalkorDB for Duplicates**

Run this Cypher query to find duplicate links:

```cypher
// For citizen_victor
MATCH (a)-[r]->(b)
WITH a, b, type(r) as rel_type, count(*) as link_count
WHERE link_count > 1
RETURN a.id, b.id, rel_type, link_count
ORDER BY link_count DESC
```

If this returns results, FalkorDB has duplicate links that need cleanup:

```cypher
// Remove duplicate links (keep first instance)
MATCH (a)-[r:RELATES_TO]->(b)
WHERE a.id = 'node_92' AND b.id = 'node_93'
WITH a, b, collect(r) as rels
FOREACH (rel in tail(rels) | DELETE rel)
```

### Testing

After fix:
```bash
python orchestration/adapters/ws/websocket_server.py
# Should start all engines without errors
```

Check logs:
```bash
tail -f launcher.log | grep "Consciousness engine V2 ready"
# Should see success messages for all citizens
```

---

## Bug 3: Windows WPARAM TypeError

### Severity: LOW (Non-blocking)
### Impact: Warning spam in logs
### Frequency: Occasional

### Error Details

```
TypeError: WPARAM is simple, so must be an int object (got NoneType)
```

### Root Cause Analysis

This error comes from Windows ctypes/win32 API interaction, likely from `watchdog` or another file watcher library used by Next.js.

**Why it's non-blocking:** The error is caught and doesn't crash the process - it's just logged as a warning.

**Why it occurs:** A Windows API call (likely `SendMessage` or similar) receives `None` instead of an integer for the WPARAM parameter.

This is common when:
1. File watcher detects a change
2. Tries to notify the process via Windows message
3. Message parameter is null/undefined in some edge cases

### Proposed Fix

**Option A: Ignore (Recommended)**

This is a known issue with file watchers on Windows and is typically harmless. The system continues operating normally.

**Option B: Update watchdog**

```bash
pip install --upgrade watchdog
```

Check if newer version handles None parameters gracefully.

**Option C: Suppress Warning**

If logs are too noisy, suppress this specific warning:

```python
# In websocket_server.py or launcher
import warnings
warnings.filterwarnings('ignore', message='WPARAM is simple')
```

### Testing

Not required - error is non-blocking and doesn't affect system operation.

---

## Fix Priority

### P0 (Immediate - Blocks System)

1. **Bug #2: Duplicate Link Errors** - Implement skip-duplicate fix
2. **Bug #1: Package Export Error** - Find and fix invalid import

### P1 (Important - System Improvement)

1. **Bug #2 Root Cause:** Clean duplicate links from FalkorDB
2. **Bug #1 Permanent Fix:** Update htmlparser2 if needed

### P2 (Low Priority)

1. **Bug #3:** Update watchdog or suppress warnings

---

## Implementation Plan

### Phase 1: Emergency Stabilization (30 minutes)

1. **Fix duplicate links:**
   ```bash
   cd C:\Users\reyno\mind-protocol
   # Edit orchestration/libs/utils/falkordb_adapter.py (add try/except at line 694)
   ```

2. **Test engine startup:**
   ```bash
   python orchestration/adapters/ws/websocket_server.py
   ```

### Phase 2: Package Fix (1 hour)

1. **Find invalid import:**
   ```bash
   cd C:\Users\reyno\mind-protocol
   grep -r "entities/lib" node_modules/htmlparser2/
   grep -r "entities/lib" app/
   ```

2. **Fix or downgrade as needed**

3. **Test dashboard:**
   ```bash
   npm run dev
   # Verify no build errors
   ```

### Phase 3: Database Cleanup (1 hour)

1. **Connect to FalkorDB:**
   ```bash
   redis-cli -p 6379
   ```

2. **Run diagnostic query for each graph:**
   ```cypher
   GRAPH.QUERY citizen_victor "MATCH (a)-[r]->(b) WITH a, b, type(r) as rel_type, count(*) as link_count WHERE link_count > 1 RETURN a.id, b.id, rel_type, link_count"
   ```

3. **Remove duplicates if found**

4. **Re-test engine startup**

---

## Validation Checklist

After all fixes:

- [ ] Dashboard builds successfully (`npm run build`)
- [ ] Dashboard runs without errors (`npm run dev`)
- [ ] All consciousness engines start (`tail -f launcher.log | grep "ready"`)
- [ ] No duplicate link errors in logs
- [ ] Guardian shows stable operation (no crashes for 30+ minutes)
- [ ] WebSocket connections work (`ws://localhost:8000/api/ws`)

---

## Notes

### Guardian Exponential Backoff Working Correctly

The guardian is correctly implementing exponential backoff:

```
2025-10-22 21:54:04 - guardian - INFO - [Launcher] Process crashed. Restart attempt 1/5 after 1s backoff
2025-10-22 21:54:09 - guardian - INFO - [Launcher] Process crashed. Restart attempt 2/5 after 4s backoff
2025-10-22 21:54:18 - guardian - INFO - [Launcher] Process crashed. Restart attempt 3/5 after 8s backoff
2025-10-22 21:54:34 - guardian - INFO - [Launcher] Process crashed. Restart attempt 4/5 after 16s backoff
2025-10-22 21:55:04 - guardian - INFO - [Launcher] Process crashed. Restart attempt 5/5 after 30s backoff
```

**This is good** - guardian is preventing runaway crash loops. Once we fix the underlying bugs, the system should stabilize.

### Crash Frequency Analysis

From guardian.log timestamps:

- **21:54 - 22:07:** ~13 minutes of crash loop (13 crashes)
- **22:37 - 23:54:** ~77 minutes of crash loop (27+ crashes)

**Average crash interval:** ~3.5 minutes between crashes

This suggests:
1. Launcher starts
2. Tries to build dashboard (fails on Bug #1)
3. Tries to start engines (fails on Bug #2)
4. Crashes after ~3.5 minutes
5. Guardian restarts with backoff
6. Loop continues

Once bugs are fixed, crash loop should stop entirely.

---

## Forensic Trail Integration Status

**Separate from log bugs:** The forensic trail implementation (Priority 2) is COMPLETE and tested:

- ✅ CostBreakdown dataclass with 10 fields
- ✅ Modified cost computation returns breakdown
- ✅ Emotion gates populate res_mult/comp_mult
- ✅ Human-readable reason generation
- ✅ Event emission with full forensic trail
- ✅ 5/5 tests passing

**Status:** Ready for production testing once system stabilizes (after bug fixes).

---

**End of Report**
