# Priority 0: COACTIVATES_WITH Tracking - Verification Checklist

**Author:** Atlas (Infrastructure Engineer)
**Date:** 2025-10-26
**Status:** Implementation complete, ready for verification

---

## Prerequisites

Before running verification:

1. **Start MPSv3 Supervisor:**
   ```bash
   python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml
   ```

2. **Verify FalkorDB is running:**
   ```bash
   # Should see FalkorDB on port 6379
   netstat -an | grep 6379
   ```

3. **Verify consciousness engines are running:**
   ```bash
   # Should see ws_api on port 8000
   netstat -an | grep 8000
   ```

---

## Verification Steps

### Step 1: Setup Indexes

```bash
cd C:\Users\reyno\mind-protocol
python orchestration/scripts/setup_coactivation_indexes.py
```

**Expected output:**
```
============================================================
FalkorDB Index Setup - COACTIVATES_WITH Tracking
============================================================
Setting up indexes for graph: citizen_felix
Creating index on SubEntity.id...
  ✓ Index created: SubEntity.id
Creating index on COACTIVATES_WITH.last_ts...
  ✓ Index created: COACTIVATES_WITH.last_ts
Index setup complete

[... same for all citizens ...]

============================================================
Index setup complete for all citizens
============================================================
```

**If indexes already exist:**
```
  ✓ Index already exists: SubEntity.id
```

**If relationship indexes not supported:**
```
  ⚠ Relationship indexes not supported by this FalkorDB version
    Time-based queries may be slower without this index
```

---

### Step 2: Run Acceptance Tests

```bash
python orchestration/scripts/test_coactivation_tracking.py
```

**Expected output:**
```
Starting COACTIVATES_WITH Tracking Acceptance Tests

============================================================
Test 1: On-change WM Detection
============================================================
Frame 1: (frozenset({'entity_A', 'entity_B'}), (500.0, 500.0))
  Expected: EMIT (first frame)
Frame 2: (frozenset({'entity_A', 'entity_B'}), (500.0, 500.0))
  Set changed: False
  Share drift: 0.000000
  Expected: NO EMIT (drift=0.000000 < 0.1)
Frame 3: (frozenset({'entity_A', 'entity_C'}), (500.0, 500.0))
  Set changed: True
  Expected: EMIT (set changed)
Frame 4: (frozenset({'entity_A', 'entity_B'}), (100.0, 900.0))
  Set changed: False
  Share drift: 0.176777
  Expected: EMIT (drift=0.176777 > 0.1)
✅ Test 1 PASSED: On-change detection works correctly

============================================================
Test 2: COACTIVATES_WITH Edge Upsert
============================================================
Clearing test graph...
Updating co-activation edges for: ['entity_A', 'entity_B', 'entity_C']
Querying created edges...
  Edges created: 3
  Expected: 3 edges (A-B, A-C, B-C)
  Edge properties: {both_ema: 0.1, either_ema: 0.1, u_jaccard: 1.0, ...}
  both_ema after first update: 0.100000
  Expected: ~0.1 (α * 1.0)
✅ Test 2 PASSED: Edge upsert works correctly

============================================================
Test 3: U-metric Convergence
============================================================
Clearing test graph...
Simulating 20 frames with constant co-occurrence: ['entity_A', 'entity_B']
After 20 frames:
  both_ema: 0.878423
  either_ema: 0.878423
  u_jaccard: 1.000000
  Expected: both_ema ≈ 0.878, u_jaccard ≈ 1.0
✅ Test 3 PASSED: U-metric converges correctly

============================================================
Test 4: Batched Update Performance
============================================================
Testing batch update with 7 entities
  Expected edges: 7 * 6 / 2 = 21
  Edges created: 21
  Update time: 45.23ms
  Expected: <100ms
✅ Test 4 PASSED: Batched updates perform efficiently

============================================================
✅ ALL TESTS PASSED
============================================================
Priority 0 COACTIVATES_WITH tracking is operational.
On-change detection and U-metric updates are working correctly.
```

---

### Step 3: Verify Live System Integration

Once consciousness engines are running:

**3.1: Monitor WM Events**

Open WebSocket monitor (if available) or check logs:
```bash
tail -f orchestration/consciousness_engine.log | grep "WM Coactivation"
```

**Expected logs:**
```
[WM Coactivation] Updated 21 COACTIVATES_WITH edges for citizen_felix
[WM Coactivation] Updated 28 COACTIVATES_WITH edges for citizen_ada
```

**NOT expected (indicates on-change detection working):**
```
[WM Coactivation] Updated ... (every single frame)
```

**3.2: Query COACTIVATES_WITH Edges**

Using FalkorDB CLI or Cypher query:
```cypher
// Check edge count per citizen
MATCH ()-[r:COACTIVATES_WITH]->()
RETURN count(r) AS edge_count
```

**Expected:** ~20-50 edges per citizen graph (depends on SubEntity count)

**3.3: Verify U-Metric Values**

```cypher
// Check U-metric distribution
MATCH ()-[r:COACTIVATES_WITH]->()
RETURN
  min(r.u_jaccard) AS min_u,
  avg(r.u_jaccard) AS avg_u,
  max(r.u_jaccard) AS max_u,
  count(r) AS edge_count
```

**Expected:**
- min_u: ~0.1 - 0.3 (rarely co-occurring pairs)
- avg_u: ~0.5 - 0.7 (moderate co-occurrence)
- max_u: ~0.9 - 1.0 (frequently co-occurring pairs)

**3.4: Check On-Change Emission Rate**

Monitor wm.selected event frequency vs frame rate:
```bash
# Count wm.selected events per minute
grep "wm.selected" websocket_logs.txt | wc -l
```

**Expected:** ~30% of frame count (e.g., 20 events/min if 60 frames/min)

---

## Troubleshooting

### Issue: "Error connecting to localhost:6379"

**Solution:**
- FalkorDB not running
- Start MPSv3 supervisor: `python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml`
- Or manually start FalkorDB: `docker-compose up -d falkordb`

### Issue: "Index already exists" error fails test

**Solution:**
- Indexes were created previously - this is OK
- Script handles this gracefully
- Verify with: `SHOW INDEXES` in FalkorDB CLI

### Issue: Test 2/3/4 fail with "no edges created"

**Solution:**
- Check FalkorDB connection
- Verify test graph can be created: `MATCH (n) RETURN count(n)` on test_coactivation
- Check adapter.run_write() isn't raising exceptions silently

### Issue: U-metric not converging (Test 3)

**Solution:**
- Check α parameter is 0.1 (not 0.01 or 1.0)
- Verify EMA formula: `new = α * signal + (1-α) * old`
- After 20 frames with α=0.1, expect ~0.878 convergence

### Issue: Slow batch updates (Test 4 >100ms)

**Solution:**
- Create SubEntity.id index: `CREATE INDEX subentity_id IF NOT EXISTS FOR (e:SubEntity) ON (e.id)`
- Check FalkorDB performance (CPU, memory)
- Verify UNWIND batch size is reasonable (21-49 edges typical)

---

## Success Criteria

**All tests pass:**
- ✅ Test 1: On-change detection distinguishes set changes and share drift
- ✅ Test 2: Edges created with correct properties
- ✅ Test 3: U-metric converges to expected values
- ✅ Test 4: Batched updates complete in <100ms

**Live system:**
- ✅ wm.selected events emit on ~30% of frames (on-change)
- ✅ COACTIVATES_WITH edges accumulate over time
- ✅ U-metric values reflect co-occurrence patterns
- ✅ No performance degradation in consciousness engine

**Database state:**
- ✅ ~20-50 COACTIVATES_WITH edges per citizen graph
- ✅ Edges have both_ema, either_ema, u_jaccard fields populated
- ✅ u_jaccard values in [0, 1] range
- ✅ SubEntity.id index exists and is used

---

## Next Actions After Verification

Once all verification steps pass:

1. **Document results** in SYNC.md
2. **Update PRIORITY0_COACTIVATES_WITH_COMPLETE.md** with test results
3. **Notify team** that Priority 0 is verified and ready for Priority 1
4. **Begin Priority 1:** Differentiation algorithm implementation

---

## Files to Check

**Implementation:**
- `orchestration/libs/utils/falkordb_adapter.py` - Async methods added
- `orchestration/mechanisms/consciousness_engine_v2.py` - On-change detection integrated

**Testing:**
- `orchestration/scripts/setup_coactivation_indexes.py` - Index setup
- `orchestration/scripts/test_coactivation_tracking.py` - Acceptance tests

**Documentation:**
- `orchestration/PRIORITY0_COACTIVATES_WITH_COMPLETE.md` - Implementation summary
- `orchestration/PRIORITY0_VERIFICATION_CHECKLIST.md` - This file

---

**Status:** Ready for verification when services are running
