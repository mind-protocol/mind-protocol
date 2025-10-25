# Pre-MPSv3 Baseline System State
**Date:** 2025-10-25 17:08:00
**Phase:** Phase 0 - Operational Preparation
**Operator:** Victor

## Current Process Inventory

### Running Processes
- Dashboard (Next.js): PID 55116, Port 3000 BOUND
- FalkorDB: PID 3848 + 24068, Port 6379 BOUND
- WebSocket Server: Port 8000 NOT BOUND (crashed)
- Guardian: Status unknown (checking logs shows crash loop)

### PID Lock Files
- websocket_server.pid: EXISTS (created 17:04)
- conversation_watcher.pid: MISSING
- launcher.lock: NOT CHECKED (known wedge issue)

### Port Status
```
Port 3000: BOUND (PID 55116 - Dashboard)
Port 6379: BOUND (PID 3848, 24068 - FalkorDB)
Port 8000: NOT BOUND (WebSocket server crashed)
Port 8001: NOT CHECKED (Stimulus Injection)
Port 8002: NOT CHECKED (Autonomy Orchestrator)
Port 8010: NOT CHECKED (Signals Collector)
```

## Known Issues (Pre-MPSv3)

1. **Stale .launcher.lock wedge**
   - Source: guardian.log line 16:49:49,522
   - Error: `[WinError 32] The process cannot access the file`
   - Impact: Blocks launcher restarts

2. **Dual supervision race**
   - websocket_server.py EngineFileWatcher (lines 1172-1234)
   - Guardian also manages restarts
   - Conflict: Both try to restart on failure

3. **Orphan port owners**
   - Example: PID 6924 held port 8000, couldn't be killed
   - Blocks clean service startup

4. **Crash loops**
   - Guardian reports launcher exit code 1 repeatedly
   - No engines initialized (0/8)
   - APIs timeout

## Configuration Backed Up

Files in this directory:
- guardian.py.bak (22K)
- start_mind_protocol.py.bak (61K)

## Expected Post-MPSv3 State

After Phase 1 (Atlas implementation) + Phase 2 (Testing):
- Single supervisor process (MPSv3)
- All services as children of supervisor
- OS mutex for singleton (no .lock files blocking)
- Centralized file watching (no child self-restarts)
- Process groups for clean termination
- Health/readiness gates (no blind waits)

## Rollback Procedure

If MPSv3 fails:
1. Stop MPSv3 supervisor
2. Restore guardian.py and start_mind_protocol.py from this backup
3. Clear all .locks/*.pid files
4. Restart guardian: `python guardian.py`

## Phase 0 Completion Criteria

- ✅ Process inventory documented
- ✅ Port status recorded
- ✅ Guardian/launcher backed up
- ✅ Known issues cataloged
- ✅ Baseline state file created
- ⏸️ Handed off to Atlas for Phase 1 implementation

---
**Victor "The Resurrector"**
Operational preparation complete. Ready for Phase 1.
