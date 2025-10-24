# Post-Fix Verification Checklist: Priorities 1-3

**Created:** 2025-10-25 02:50 UTC
**Coordinator:** Ada "Bridgekeeper"
**Purpose:** Systematic verification after entity persistence bug fix
**Blocker Resolved:** persist_subentities() bug (Felix fixing)

---

## Pre-Restart Verification

**Before restarting, confirm fix deployed:**

```bash
# Check that falkordb_adapter.py includes entity persistence fix
grep -A 5 "def persist_subentities" C:/Users/reyno/mind-protocol/orchestration/libs/utils/falkordb_adapter.py

# Check that websocket_server.py calls persist_subentities()
grep -B 2 -A 2 "persist_subentities" C:/Users/reyno/mind-protocol/orchestration/adapters/ws/websocket_server.py
```

**Expected:** Both files should show persistence logic with error handling.

---

## Step 1: Guardian Restart

```bash
# Stop guardian
# (Ctrl+C in guardian terminal)

# Clean restart
python guardian.py --force-restart
```

**Expected Output:**
- All old Python processes killed
- Lock files removed
- Fresh guardian started
- Port 8000 bound (WebSocket server)
- All 8 consciousness engines starting

**Success Criteria:**
- ✅ No "lock file exists" errors
- ✅ Launcher.log shows bootstrap starting for all citizens

---

## Step 2: Monitor Bootstrap Logs

```bash
# Tail launcher.log during startup
tail -f launcher.log | grep -i "entity\|bootstrap\|persist"
```

**Expected Log Sequence (per citizen):**
1. `[N1:luca] Bootstrapping subentity layer...`
2. `[N1:luca] entity_bootstrap: created={'functional_entities': 8, 'belongs_to_links': 357}`
3. `[N1:luca] post_bootstrap: {'nodes_normalized': X, 'entities_with_centroids': 8, ...}`
4. `[N1:luca] subentity_persistence: {'entities_created': 8, 'belongs_to_links': 357, 'errors': 0}` ← **KEY**
5. `[N1:luca] entities.total=8` ← **VERIFICATION**

**Success Criteria:**
- ✅ `entities_created: 8` (NOT 0)
- ✅ `belongs_to_links: 357`
- ✅ `errors: 0`
- ✅ `entities.total=8` final count

---

## Step 3: FalkorDB Direct Verification

```bash
# Query FalkorDB directly for entities (per citizen)
# Via FalkorDB CLI or Python script
```

**Cypher Queries:**

```cypher
// Check entity count
MATCH (e:Subentity) RETURN count(e) as entity_count
// Expected: 8 (for each citizen graph)

// List all entities
MATCH (e:Subentity) RETURN e.id, e.role_or_topic, e.member_count

// Check BELONGS_TO links
MATCH (:Node)-[r:BELONGS_TO]->(:Subentity) RETURN count(r) as membership_count
// Expected: 357

// Verify entity properties
MATCH (e:Subentity {id: "translator"}) RETURN e.member_count, e.coherence_ema
// Expected: member_count > 0, coherence_ema exists
```

**Success Criteria:**
- ✅ `entity_count: 8` (NOT 1)
- ✅ All 8 entities have names: translator, architect, validator, pragmatist, pattern_recognizer, boundary_keeper, partner, observer
- ✅ `membership_count: 357`
- ✅ Entities have non-null properties (centroid_embedding, coherence_ema, etc.)

---

## Step 4: API Verification

```bash
# Check consciousness status API
curl http://localhost:8000/api/consciousness/status | python -m json.tool
```

**Expected JSON (per citizen):**
```json
{
  "luca": {
    "sub_entity_count": 9,  // ← CHANGED FROM 1
    "sub_entities": [
      "luca",
      "translator",
      "architect",
      "validator",
      "pragmatist",
      "pattern_recognizer",
      "boundary_keeper",
      "partner",
      "observer"
    ],
    "nodes": 353,
    "links": 169,
    ...
  }
}
```

**Success Criteria:**
- ✅ `sub_entity_count: 9` for ALL citizens (NOT 1)
- ✅ `sub_entities` array contains 9 names
- ✅ First entity is self-entity (e.g., "luca")
- ✅ Next 8 are functional entities

---

## Step 5: Telemetry Verification (Priority 1)

```bash
# Check affective telemetry for entity events
curl http://localhost:8000/api/affective-telemetry/metrics | python -m json.tool
```

**Expected Metrics:**
```json
{
  "event_counts": {
    "entity.flip": 150,  // ← CHANGED FROM 0
    "wm.emit": 2800,
    "frame.start": 3300,
    ...
  },
  "event_samples": {
    "entity.flip": [
      {
        "entity_id": "translator",
        "from_state": "dormant",
        "to_state": "active",
        "energy": 0.75,
        ...
      }
    ]
  }
}
```

**Success Criteria:**
- ✅ `entity.flip` count > 0 (NOT 0)
- ✅ Events show different entities flipping (translator, architect, etc.)
- ✅ `wm.emit` events include `selected_entities` array with multiple entities

---

## Step 6: Dashboard Verification (Priority 1)

```
Open: http://localhost:3000/consciousness
```

**Expected Visualization:**
- ✅ Entity bubbles visible (9 entities including self)
- ✅ Entities arranged in cluster/force layout
- ✅ Entity flip animations when states change
- ✅ Boundary beams showing entity boundaries
- ✅ Hover shows entity details (name, role, member_count)

**Success Criteria:**
- ✅ Visual confirmation of 9 entities
- ✅ Entities actively changing states (not static)
- ✅ UI responsive to entity.flip events

---

## Step 7: Priority 2 Verification (3-Tier Strengthening)

```bash
# Check for learning events with tier information
curl http://localhost:8000/api/affective-telemetry/metrics | python -c "import sys, json; data=json.load(sys.stdin); print('Learning events with reason:', [e for e in data.get('event_samples', {}).get('weights_updated', []) if 'reason' in e][:3])"
```

**Expected Event Sample:**
```json
{
  "type": "weights_updated",
  "link_id": "link_123",
  "delta_weight": 0.05,
  "reason": "co_activation",  // ← NEW FIELD
  "tier_scale": 1.0,          // ← NEW FIELD
  "stride_utility": 2.5,      // ← NEW FIELD
  "before_weight": 0.45,
  "after_weight": 0.50
}
```

**Success Criteria:**
- ✅ Learning events exist
- ✅ `reason` field present: "co_activation" | "causal" | "background"
- ✅ `tier_scale` matches reason (1.0 for co_activation, 0.6 for causal, 0.3 for background)
- ✅ No D020 "inactive-only" blocking (co_activation events should exist)

---

## Step 8: Priority 3 Verification (Three-Factor Tick Speed)

```bash
# Check for tick events with reason information
curl http://localhost:8000/api/affective-telemetry/metrics | python -c "import sys, json; data=json.load(sys.stdin); print('Tick events:', data.get('event_samples', {}).get('frame.start', [])[:3])"
```

**Expected Event Sample:**
```json
{
  "type": "frame.start",
  "frame_number": 1234,
  "interval_ms": 100,
  "reason": "activation",  // ← NEW FIELD (stimulus | activation | arousal_floor)
  "interval_stimulus": 2000,   // ← NEW FIELD
  "interval_activation": 100,  // ← NEW FIELD (winner)
  "interval_arousal": 200,     // ← NEW FIELD
  "total_active_energy": 15.5, // ← NEW FIELD
  "mean_arousal": 0.65         // ← NEW FIELD
}
```

**Success Criteria:**
- ✅ Tick events include `reason` field
- ✅ `reason` values include "stimulus", "activation", "arousal_floor" (not just "stimulus")
- ✅ Three interval factors present (interval_stimulus, interval_activation, interval_arousal)
- ✅ `interval_ms` matches minimum of three factors
- ✅ Evidence of autonomous momentum (activation-driven ticks without stimulus)

---

## Step 9: Complete System Health Check

```bash
# Run comprehensive status check
python status_check.py
```

**Expected Output:**
```
✅ Port 8000: WebSocket Server BOUND
✅ Port 6379: FalkorDB BOUND
✅ Port 3000: Dashboard BOUND
✅ All 8 engines: RUNNING
✅ All citizens: sub_entity_count = 9
✅ Telemetry: entity.flip > 0
✅ Telemetry: weights_updated with reason field
✅ Telemetry: frame.start with reason field
```

**Success Criteria:**
- ✅ ALL systems operational
- ✅ ALL verification points passing
- ✅ No errors in logs

---

## Step 10: Documentation Updates

**After verification complete:**

1. Update `consciousness/citizens/SYNC.md`:
   - ✅ Priority 1: VERIFIED OPERATIONAL (entity persistence working)
   - ✅ Priority 2: VERIFIED OPERATIONAL (3-tier strengthening active)
   - ✅ Priority 3: VERIFIED OPERATIONAL (three-factor tick speed active)

2. Update `docs/specs/v2/IMPLEMENTATION_GAP_ANALYSIS.md`:
   - Correct false verification claims (lines 32-50)
   - Add actual verification timestamps and evidence
   - Document the persistence bug that was fixed

3. Update todo list:
   - Mark Priorities 1-3 as VERIFIED (not just IMPLEMENTED)
   - Unblock Priority 4 (context-aware TRACE)
   - Unblock frontend coordination

---

## Failure Scenarios

### If Step 4 fails (API still shows sub_entity_count: 1):

**Debug:**
1. Check launcher.log for persistence errors
2. Query FalkorDB directly (Step 3)
3. If FalkorDB shows 8 entities but API shows 1 → graph reload bug
4. If FalkorDB shows 0 entities → persistence still failing

**Action:**
- Review Felix's fix
- Check for exceptions during persist_subentities()
- Verify serialize_entity() not throwing errors
- Check FalkorDB permissions

### If Step 5 fails (entity.flip still 0):

**Debug:**
1. Confirm Step 4 passed (entities loaded)
2. Check if engines are processing frames (frame.start > 0)
3. Check if entity selection is running (wm.emit events exist)
4. Check if entity energy calculations are working

**Action:**
- Review entity_post_bootstrap.py (energy initialization)
- Check WM selection logic includes entities
- Verify entity activation thresholds are reasonable

### If Step 7 fails (no tier information in learning events):

**Debug:**
1. Confirm Priority 1 working (entities active)
2. Check strengthening.py for tier logic
3. Check if learning events are emitting at all

**Action:**
- Priority 2 might not be deployed despite file timestamps
- Guardian hot-reload may have failed
- Need full restart to load new strengthening.py

### If Step 8 fails (no three-factor tick information):

**Debug:**
1. Check tick_speed.py deployed correctly
2. Verify AdaptiveTickScheduler using new logic
3. Check frame.start events structure

**Action:**
- Similar to Step 7 - may need full restart
- Check if engines loaded old tick_speed.py

---

## Success Declaration

**Priorities 1-3 are VERIFIED OPERATIONAL when:**

✅ All 10 verification steps pass
✅ FalkorDB shows 8 entities persisted
✅ API shows sub_entity_count: 9
✅ Telemetry shows entity.flip events
✅ Dashboard visualizes entities
✅ Learning events include tier information
✅ Tick events include three-factor information
✅ No errors in logs
✅ System stable for 5+ minutes
✅ Documentation updated with evidence

**Only then can we proceed to Priority 4.**

---

**Coordinator:** Ada "Bridgekeeper"
**Status:** Verification checklist ready | Awaiting persistence bug fix from Felix
**Next:** Execute checklist after guardian restart
