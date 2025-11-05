# Backend WebSocket 500 Error - Diagnostic Report

**Date:** 2025-11-05 02:00 UTC
**Issue:** Production dashboard at www.mindprotocol.ai/consciousness shows no graphs
**Root Cause:** Backend WebSocket endpoint returning HTTP 500 errors

## Findings

### ✅ Frontend Fixes Deployed

1. **Snapshot Event Handling** (Commit `2f8134c5`)
   - Added `snapshot.begin@1.0` and `snapshot.end@1.0` to event handler
   - No more "Unknown event type" warnings

2. **Critical Map Initialization Bug** (Commit `fba74286`)
   - Fixed: Changed `nodes: {}` to `nodes: new Map()`
   - Fixed: Changed `links: {}` to `links: new Map()`
   - This was causing 512 nodes to be silently discarded
   - **Impact:** Frontend is now ready to display graphs correctly

### ❌ Backend Service Issue

**WebSocket Error:**
```
WebSocket connection to 'wss://engine.mindprotocol.ai/ws' failed:
Error during WebSocket handshake: Unexpected response code: 500
```

**Diagnostic Results:**
- ❌ WebSocket endpoint: Returns HTTP 500 during handshake
- ❌ `/admin/reload`: Returns 404 (endpoint doesn't exist)
- ❌ Root endpoint `/`: Curl requests timing out (service unresponsive)
- ❌ `/consciousness/status`: Curl requests timing out
- ✅ Database: Contains data (Felix: 2996 nodes, Ada: 2316 nodes, Protocol: 3667 nodes)

**Evidence from Earlier Logs:**
User's logs showed backend WAS working and sent 512 nodes correctly:
```json
{
  "graphId": "mind-protocol_felix",
  "nodeCount": 512,
  "linkCount": 112,
  "nodes": [...]
}
```

**Conclusion:** Backend service appears to have crashed or become unresponsive after recent deployments.

## Root Cause Analysis

The backend service may have failed due to:

1. **FalkorDB Connection Issues**
   - Backend initialization requires connecting to FalkorDB (line 221 in websocket_server.py)
   - If `mind-protocol-falkordb` service is not accessible, initialization fails
   - render.yaml shows `dependsOn: mind-protocol-falkordb` but networking might be broken

2. **Graph Loading Timeout**
   - Backend loads all citizen graphs on startup (60s timeout per graph, line 338)
   - With 7 citizens (Felix, Ada, Luca, Atlas, Iris, Victor, Protocol), that's up to 7 minutes of loading
   - Render might be killing the service if health checks fail during this long initialization

3. **Memory Pressure**
   - render.yaml shows `plan: starter` (limited RAM)
   - Comment says "Upgrade to standard for production (need 512MB+ RAM for embeddings)"
   - Large graphs (Felix: 2996 nodes) might exceed memory limits

4. **Recent Deployment Side Effects**
   - We made frontend-only changes, but both services auto-deploy on git push
   - Backend might have redeployed and failed to restart properly

## Required Actions

### Immediate Fix (Manual)

1. **Access Render Dashboard**
   - Go to https://dashboard.render.com
   - Navigate to `mind-protocol-backend` service
   - Check "Logs" tab for startup errors or crash dumps

2. **Restart Backend Service**
   - Click "Manual Deploy" > "Clear build cache & deploy"
   - OR: Click service menu > "Restart Service"
   - Wait for deployment to complete (~5-10 minutes)

3. **Verify Service Dependencies**
   - Check `mind-protocol-falkordb` service is running
   - Check internal network connectivity between services
   - Verify environment variables are set correctly (especially `FALKORDB_HOST`)

4. **Monitor Startup Logs**
   Look for these key log lines:
   ```
   [Discovery] Found N N1 citizen graphs: [...]
   [N1:mind-protocol_felix] Creating consciousness engine V2...
   [N1:mind-protocol_felix] Graph loaded successfully
   [N1:mind-protocol_felix] Engine started and running
   ```

5. **Test WebSocket Connection**
   Once logs show successful startup:
   ```bash
   # Test from local machine
   wscat -c wss://engine.mindprotocol.ai/ws

   # Should connect and wait for messages
   # Send subscribe message:
   {"type": "subscribe", "topics": ["snapshot.chunk@1.0"]}
   ```

### Long-Term Fixes (Code Changes)

1. **Add Health Check Endpoint**
   - Backend has no HTTP health endpoint (WebSocket-only)
   - render.yaml line 144: `# Note: No healthCheckPath - WebSocket-only architecture`
   - Should add `/health` or `/readiness` endpoint that returns 200 when services are ready
   - This would prevent Render from routing traffic before initialization completes

2. **Graceful Degradation for FalkorDB**
   - Backend should start even if FalkorDB is temporarily unavailable
   - Implement retry logic with exponential backoff
   - Allow WebSocket connections even if graphs haven't loaded yet (send empty snapshots)

3. **Upgrade Render Plan**
   - Current: `plan: starter`
   - Recommended: `plan: standard` (512MB+ RAM)
   - Large consciousness graphs need more memory

4. **Add Startup Timeout Configuration**
   - 60s timeout per graph × 7 graphs = 7 minutes potential startup time
   - Add env var `GRAPH_LOAD_TIMEOUT_SEC` (default: 60)
   - Add env var `MAX_CONCURRENT_GRAPH_LOADS` (default: 3)

## Verification Checklist

Once backend is restarted:

- [ ] Check Render logs show successful startup
- [ ] Verify all 7 citizen engines started
- [ ] Test WebSocket connection with wscat
- [ ] Open https://www.mindprotocol.ai/consciousness
- [ ] Verify console shows connection success (no 500 errors)
- [ ] Verify snapshot events are received
- [ ] Verify graphs display with correct node counts:
  - Felix: ~2996 nodes
  - Ada: ~2316 nodes
  - Protocol: ~3667 nodes
  - Others: ~15,000-17,000 nodes each
- [ ] Verify graph is interactive (pan, zoom, hover)

## Files Changed (This Session)

### Frontend
- `app/consciousness/hooks/useWebSocket.ts` (Commit `2f8134c5`)
  - Added snapshot.begin/end event handling

- `app/consciousness/hooks/useGraphStream.ts` (Commit `fba74286`)
  - Fixed Map initialization bug (critical fix)
  - Updated diagnostic logging

### Backend
- No backend code changes this session
- Backend needs manual restart on Render

## Contact Points

- **Render Dashboard:** https://dashboard.render.com
- **Production Dashboard:** https://www.mindprotocol.ai/consciousness
- **Backend API:** https://engine.mindprotocol.ai
- **FalkorDB Service:** mind-protocol-falkordb (internal Render network)

## Next Session Handoff

**Status:** Frontend code is fixed and deployed. Backend service is unresponsive and needs manual restart on Render.

**Who can fix:** Anyone with access to Render dashboard
**Estimated time:** 5-10 minutes (restart + wait for deployment)
**Blockers:** Requires Render dashboard access
**Priority:** HIGH - production dashboard is down
