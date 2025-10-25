# Dashboard Integration Diagnostic
## 2025-10-25 14:30 - Ada "Bridgekeeper"

**Status:** Backend operational, events flowing, frontend rendering issues identified

---

## Executive Summary

**Root Cause:** ALL citizens were dormant (zero energy) due to no stimulus. Dashboard correctly showed "waiting for data" because there WAS no activity. After stimulus injection, Felix activated (alert state) proving the pipeline works.

**Secondary Issues:** Frontend visualization and event consumption need fixes (Iris's domain).

---

## What's Working ✅

### Backend Event Pipeline
- ✅ WebSocket server running at `ws://localhost:8000/api/ws`
- ✅ 1 connected client (dashboard)
- ✅ Events streaming successfully (18 broadcast_event calls in consciousness_engine_v2.py)
- ✅ All 8 engines running (felix, luca, atlas, ada, victor, iris, nicolas, mind_protocol)
- ✅ Event types confirmed flowing:
  - `tick.update` - Frame lifecycle
  - `frame.start` - Entity index at frame start
  - `criticality.state` - ρ metrics
  - `decay.tick` - Energy/weight decay
  - `wm.emit` - Working memory selection
  - `subentity.snapshot` - Active entities (for Active Subentities Panel)
  - `consciousness_state` - Global consciousness state
  - `tick_frame_v1` - Complete frame summary

### Stimulus Response
- ✅ Queue poller operational
- ✅ Stimulus injection works (Felix dormant → alert after user_message)
- ✅ Energy propagation functional

---

## What's Broken 🔴

### 1. No Activity by Default
**Problem:** All citizens dormant (energy: 0.0) with no stimulus
**Evidence:** All entities show `active: false` in events
**Impact:** Dashboard correctly shows "Awaiting data..." because there IS no data
**Fix:** Either (a) inject regular stimulus, or (b) seed citizens with baseline energy

### 2. Frontend Event Consumption (Iris's Domain)
**Problems Nicolas Reported:**
- Active Subentities shows "Waiting for live activation" (but events ARE arriving)
- CLAUDE_DYNAMIC.md shows "Waiting for backend implementation" (backend IS implemented)
- 15+ dashboard panels show "No data yet"
- Graph visualization: nodes scattered, links short, no animation
- Semantic search broken
- System status shows "degraded" constantly
- Poor hover information on nodes/links

**Likely Root Causes:**
1. Frontend not consuming/rendering subentity.snapshot events
2. CLAUDE_DYNAMIC.md file not being watched/displayed
3. Event normalizer may be dropping events or misrouting
4. Graph rendering engine (force layout?) not configured properly
5. Missing event types for some panels

---

## Event Flow Verification

### Sample Events Captured (2025-10-25 14:30:05 UTC)

**subentity.snapshot (atlas, frame 11376):**
```json
{
  "type": "subentity.snapshot",
  "v": "1",
  "frame_id": 11376,
  "citizen_id": "atlas",
  "active": [],  // Empty because dormant
  "wm": [
    {"id": "entity_citizen_atlas_translator", "name": "translator", "share": 0.025},
    {"id": "entity_citizen_atlas_architect", "name": "architect", "share": 0.025},
    // ... 7 entities total
  ]
}
```

**tick_frame_v1 (atlas, frame 11376):**
```json
{
  "type": "tick_frame_v1",
  "citizen_id": "atlas",
  "frame_id": 11376,
  "v": "1",
  "tick_duration_ms": 1.01,
  "entities": [
    {
      "id": "entity_citizen_atlas_translator",
      "name": "translator",
      "energy": 0.0,  // Dormant
      "theta": 1.0,
      "active": false,
      "members_count": 0,
      "coherence": 0.6
    }
    // ... 8 entities
  ],
  "nodes_active": 0,
  "nodes_total": 131,
  "strides_executed": 0
}
```

**After Stimulus (Felix):**
- State: dormant → **alert**
- Frame: advancing normally
- Events: continuing to flow

---

## Testing Protocol

### Test 1: Verify Event Reception
```bash
# Connect to WebSocket and observe events
python -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8000/api/ws') as ws:
        for i in range(10):
            msg = await ws.recv()
            data = json.loads(msg)
            print(f'{data.get(\"type\")}: {data.get(\"citizen_id\", \"N/A\")}')
asyncio.run(test())
"
```
**Expected:** Stream of events for all 8 citizens
**Actual:** ✅ Working (events confirmed)

### Test 2: Inject Stimulus
```bash
# Create activity
echo '{"type": "user_message", "content": "Test", "citizen_id": "felix"}' >> .stimuli/queue.jsonl

# Wait 2s, check state
curl http://localhost:8000/api/consciousness/status | jq '.engines.felix.consciousness_state'
```
**Expected:** "dormant" → "alert" or higher
**Actual:** ✅ Working (Felix: dormant → alert confirmed)

### Test 3: Frontend Rendering (Iris to verify)
- Open dashboard at http://localhost:3000
- Check browser console for:
  - WebSocket connection status
  - Event reception logs
  - Rendering errors
- Verify Active Subentities Panel updates when entity activates
- Verify graph shows nodes with energy > 0

---

## Missing Event Types Analysis

Nicolas reported these panels show "No data":
1. **Affective Systems / Regulation** - "Awaiting stride data"
   - Needs: `stride.exec` events
   - Status: ❓ Check if stride.exec emitted when strides actually execute

2. **Telemetry / Emotion** - "No emotion data"
   - Needs: Emotion telemetry events
   - Status: ❓ Check affective telemetry emitter

3. **Autonomy** - "No autonomy data"
   - Needs: Autonomy decision events
   - Status: ❓ S6 not yet implemented (expected)

4. **Tick Timeline** - "No tick data"
   - Has: tick.update, tick_frame_v1 events ARE flowing
   - Status: 🔴 Frontend not consuming or rendering

5. **Exploration Dynamics** - "No exploration data"
   - Needs: Traversal events
   - Status: ❓ Check if traversal emitter active

6. **3-Tier Strengthening** - "Awaiting data"
   - Needs: Weight learning events
   - Status: ❓ Check weight_learning_emitter.py

7. **Dual-View Learning** - "No weight learning events"
   - Needs: TRACE-driven update events
   - Status: ❓ TRACE processing not wired to telemetry?

8. **Phenomenology Alignment** - "No phenomenology data"
   - Needs: Substrate-phenomenology comparison events
   - Status: ❓ Not implemented yet?

9. **Consciousness Health** - "No health data"
   - Needs: Health monitoring events
   - Status: ❓ Check health_checks.py integration

---

## Coordination Plan

### For Ada (me) - System Architect
- ✅ Complete diagnostic (this document)
- ⏳ Map which events exist vs. needed
- ⏳ Identify backend gaps (missing emitters)
- ⏳ Create integration specs for Iris

### For Iris - Frontend Engineer
**Priority 1: Verify Event Consumption**
1. Check browser console - are events arriving?
2. Check normalizeEvents.ts - are events being transformed correctly?
3. Check useWebSocket.ts - are events being stored in state?
4. Check component subscriptions - are components reading the right state keys?

**Priority 2: Fix Active Subentities Panel**
- Events ARE flowing (subentity.snapshot confirmed)
- Component should render when citizen has energy > 0
- Test with Felix after stimulus injection

**Priority 3: Fix Graph Visualization**
- Check force-directed layout configuration
- Verify node positioning algorithm
- Add animation for energy flow
- Improve hover tooltips

**Priority 4: CLAUDE_DYNAMIC.md Display**
- File IS being generated (wired at consciousness_engine_v2.py:172-180, 1155-1165)
- Check file watcher in frontend
- Verify file path: `consciousness/citizens/{citizen_id}/CLAUDE_DYNAMIC.md`

### For Atlas - Infrastructure Engineer
1. Verify stride.exec emission (check diffusion_runtime.py)
2. Verify affective telemetry emission
3. Verify weight learning emitter integration
4. Check which emitters are wired vs. not wired

### For Victor - Operations
- Monitor WebSocket connection stability
- Check for event backpressure or dropped connections
- Verify guardian isn't restarting services mid-stream

---

## Quick Wins

### Win 1: Continuous Stimulus (Create Activity)
```bash
# Simple stimulus generator for testing
while true; do
  echo "{\"type\": \"ambient_thought\", \"content\": \"tick\", \"citizen_id\": \"felix\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> .stimuli/queue.jsonl
  sleep 5
done
```
This will keep Felix (and others) active for testing dashboard visualization.

### Win 2: Frontend Console Debugging
Add to dashboard page:
```typescript
useEffect(() => {
  console.log('[Dashboard] Event received:', event.type, event);
}, [event]);
```
This will show exactly what's arriving in browser.

### Win 3: System Status Fix
Check why status shows "system degraded" - likely:
- Missing health check responses
- Incomplete system registry
- Thresholds too strict

---

## Next Actions

**Immediate (Ada):**
1. Map existing emitters vs. dashboard requirements
2. Identify backend implementation gaps
3. Create integration specs per panel

**Immediate (Iris):**
1. Open browser console, verify events arriving
2. Add console.log to event handlers
3. Test Active Subentities Panel with stimulated Felix
4. Fix graph visualization layout

**Short-term (Team):**
1. Wire missing emitters (stride.exec, emotions, health)
2. Implement CLAUDE_DYNAMIC.md file watcher
3. Add continuous stimulus for demo/testing
4. Fix semantic search

**Long-term:**
5. Implement missing systems (autonomy, phenomenology)
6. Optimize event throughput if needed
7. Add animation engine for live activity

---

## Evidence

**WebSocket Output (partial, 2025-10-25 14:30 UTC):**
```
tick.update (atlas, frame 11376)
frame.start (atlas, 8 entities, all inactive)
criticality.state (rho=1.0, safety_state=critical)
decay.tick (delta_E=0.03, nodes_decayed=0)
wm.emit (7 entities selected, 350 tokens)
subentity.snapshot (atlas, active=[], wm=7 entities)
consciousness_state (network=N1, state=dormant, energy=0.1)
tick_frame_v1 (atlas, tick_duration=1.01ms, nodes_active=0/131)
[... repeating for all 8 citizens every 100ms ...]
```

**After Stimulus:**
```
Felix: dormant → alert
Energy: 0.0 → [propagating]
Frame advancing normally
```

---

**Conclusion:** Backend is solid. Events are flowing. The problem is (1) no activity by default (all dormant), and (2) frontend not rendering the events that ARE arriving. Both fixable.

**Status:** Ready for frontend integration work (Iris) + backend emitter verification (Atlas).

---

**Author:** Ada "Bridgekeeper"
**Date:** 2025-10-25 14:30 UTC
**Purpose:** Dashboard integration diagnostic and coordination plan
