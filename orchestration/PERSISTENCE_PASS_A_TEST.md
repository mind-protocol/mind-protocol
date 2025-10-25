# Persistence Pass A - Manual Verification Test

**Status:** Ready for testing
**Author:** Atlas
**Date:** 2025-10-25

## What Was Implemented (Pass A)

✅ **State Variables** - Dirty tracking, intervals, telemetry (with env config)
✅ **`_persist_dirty_if_due()`** - Periodic flush with thread pool execution
✅ **`persist_to_database(force=True)`** - Manual flush using bulk persist
✅ **Manual API endpoint** - `POST /api/citizen/{id}/persist`
❌ **Auto-flush** - NOT ENABLED (requires Pass B)

**Feature Flag:** `MP_PERSIST_ENABLED=0` (default OFF for Pass A)

---

## Test 1: Manual Flush (No Auto-Flush)

**Purpose:** Verify persistence mechanism works before wiring into tick loop

### Prerequisites

1. Engines are running with consciousness state (nodes with energy)
2. FalkorDB is running (`redis-cli` → `GRAPH.LIST`)
3. Schema migration completed (all nodes have `id` field)

### Test Steps

**Step 1: Verify baseline (before persist)**

```bash
# Check current DB state for felix
redis-cli
127.0.0.1:6379> GRAPH.QUERY citizen_felix "MATCH (n) WHERE n.E IS NOT NULL RETURN count(n)"
```

Expected: Small number (or 0 if never persisted runtime values)

**Step 2: Trigger manual flush**

```bash
curl -X POST http://localhost:8000/api/citizen/felix/persist
```

Expected response:
```json
{
  "status": "persisted",
  "citizen_id": "felix",
  "nodes_persisted": 483,
  "elapsed_ms": 45.2
}
```

**Step 3: Verify DB updated**

```bash
redis-cli
127.0.0.1:6379> GRAPH.QUERY citizen_felix "MATCH (n) WHERE n.E IS NOT NULL RETURN count(n)"
```

Expected: 483 nodes (or whatever `nodes_persisted` returned)

**Step 4: Spot-check values**

```cypher
GRAPH.QUERY citizen_felix "MATCH (n) WHERE n.E IS NOT NULL RETURN n.name, n.E, n.theta LIMIT 5"
```

Expected: E and theta values in range [0, 100]

**Step 5: Check logs**

```bash
tail -f orchestration/logs/consciousness_engine_v2.log
```

Look for:
- `[ConsciousnessEngineV2] Force persisting all nodes`
- `[ConsciousnessEngineV2] Persisted <N>/<M> nodes`

---

## Test 2: Thread Pool Non-Blocking

**Purpose:** Verify persistence doesn't block tick loop

### Test Steps

1. Call manual persist endpoint during active processing
2. Monitor tick latency in engine logs
3. Verify no tick duration spikes

Expected: Tick continues normally, persist runs in background thread

---

## Test 3: Runtime Fields (Not Init Fields)

**Purpose:** Verify we're persisting `energy_runtime`, not `node.E` init values

### Test Steps

**Step 1: Inject stimulus to change energy**

```bash
# (This will be tested in Pass B when auto-flush wired)
# For now, verify manual persist captures current runtime state
```

**Step 2: Check nodes with energy > 0**

```cypher
GRAPH.QUERY citizen_felix "MATCH (n) WHERE n.E > 0 RETURN n.name, n.E ORDER BY n.E DESC LIMIT 10"
```

Expected: Nodes with non-zero energy

---

## Test 4: Error Handling

**Purpose:** Verify graceful failure if DB unavailable

### Test Steps

**Step 1: Stop FalkorDB**

```bash
# Stop Redis/FalkorDB temporarily
```

**Step 2: Trigger persist**

```bash
curl -X POST http://localhost:8000/api/citizen/felix/persist
```

Expected: HTTP 500 with clear error message

**Step 3: Check logs**

```bash
tail -f orchestration/logs/consciousness_engine_v2.log
```

Look for: `[ConsciousnessEngineV2] Force persist failed: <error>`

**Step 4: Restart FalkorDB and retry**

Expected: Persist succeeds after DB available again

---

## Test 5: Bulk Persist Performance

**Purpose:** Verify bulk persist is fast enough for periodic flush

### Test Steps

**Step 1: Flush all nodes for felix (483 nodes)**

```bash
time curl -X POST http://localhost:8000/api/citizen/felix/persist
```

Expected: `elapsed_ms` < 100ms (thread pool execution should be fast)

**Step 2: Try larger graph (luca: 399 nodes)**

```bash
time curl -X POST http://localhost:8000/api/citizen/luca/persist
```

Expected: Similar performance (bulk UNWIND should scale well)

---

## Success Criteria

Pass A is verified when:

- ✅ Manual flush endpoint returns 200 OK
- ✅ FalkorDB shows updated E/theta values after flush
- ✅ Tick loop continues without blocking during persist
- ✅ Runtime values (energy_runtime, threshold_runtime) are persisted, not init values
- ✅ Error handling is graceful (no crashes on DB failure)
- ✅ Bulk persist completes in <100ms for ~500 nodes

---

## Pass B Preview (Not Implemented Yet)

After Pass A verification, Pass B will add:

1. Mark nodes dirty after energy changes (in tick loop)
2. Call `_persist_dirty_if_due()` at tick end
3. Enable auto-flush with `MP_PERSIST_ENABLED=1`
4. Add telemetry tracking (batch sizes, failures, timing)
5. Test end-to-end: Stimulus → Energy change → Auto-persist → Restart → State preserved

---

## Troubleshooting

**"No nodes persisted"**
- Check: Are engines running? (`/api/consciousness/status`)
- Check: Do nodes have runtime energy? (engines might be dormant)

**"Elapsed_ms too high"**
- Check: Is FalkorDB on same machine? (network latency)
- Check: Are indexes created? (`CREATE INDEX FOR (n:Node) ON (n.id)`)

**"Values not updating in DB"**
- Check: Schema migration completed? (all nodes have `id` field)
- Check: Dual-path MATCH working? (test with sample rows)

**"Thread pool errors"**
- Check: Event loop running? (engines must be async context)
- Check: Adapter accessible? (not None)

---

## Next Steps After Pass A Verified

1. Document Pass A results in SYNC.md
2. Implement Pass B (mark dirty + auto-flush)
3. Run end-to-end acceptance tests
4. Enable persistence in production (`MP_PERSIST_ENABLED=1`)
