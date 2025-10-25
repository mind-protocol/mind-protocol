# MPSv3 Phase 0 → Phase 1 Handoff
**From:** Victor (Operations)
**To:** Atlas (Implementation)
**Date:** 2025-10-25 17:08:00

## Phase 0 Status: ✅ COMPLETE

Operational preparation complete. System baseline documented, configurations backed up, ready for MPSv3 core implementation.

## Deliverables Completed

1. **Process Inventory**
   - Dashboard: RUNNING (PID 55116, port 3000)
   - FalkorDB: RUNNING (PID 3848/24068, port 6379)
   - WebSocket Server: CRASHED (port 8000 unbound, 0/8 engines)
   - Guardian: CRASH LOOP (launcher exit code 1)

2. **Configuration Backup**
   - guardian.py → guardian.py.bak (22K)
   - start_mind_protocol.py → start_mind_protocol.py.bak (61K)
   - Location: `backups/pre_mpsv3_20251025_170800/`

3. **Baseline Documentation**
   - File: `BASELINE_STATE.md`
   - Includes: Process state, port bindings, known issues, rollback procedure

4. **Issue Catalog**
   - Stale .launcher.lock wedge (WinError 32)
   - Dual supervision race (guardian + websocket_server file watcher)
   - Orphan port owners (PID 6924 incident)
   - Crash loops without recovery

## Critical Operational Context for Implementation

### Current Failure State
- WebSocket server cannot stay running
- Engines never initialize (0/8)
- APIs timeout (no endpoints exist)
- Guardian crash-loops trying to restart launcher
- Conversation_watcher offline (no TRACE capture to graph)

### Root Causes Confirmed
All match MPSv3 design diagnosis:
1. File-based singleton locks wedge (can't delete .launcher.lock)
2. Guardian restarts launcher + websocket restarts itself = race
3. No process groups = orphan PIDs hold ports
4. No readiness gates = blind 60s waits that fail

## Phase 1 Implementation Checklist

Atlas should implement (4 hours estimated):

- [ ] `mpsv3/singleton.py` - OS mutex (Windows) + flock (POSIX)
- [ ] `mpsv3/runner.py` - ServiceRunner with backoff/quarantine
- [ ] `mpsv3/watcher.py` - Centralized file watcher
- [ ] `mpsv3/supervisor.py` - Main loop with DAG
- [ ] `mpsv3/services.yaml` - ServiceSpec for all 7 services

Reference implementation skeletons in:
`docs/specs/v2/ops_and_viz/mpsv3_supervisor.md` lines 850-1130

## Phase 2 Handoff Criteria

When Atlas completes Phase 1, handoff back to Victor for Phase 2 testing requires:

- [ ] MPSv3 supervisor starts with OS mutex (no .lock files)
- [ ] All 7 services defined in services.yaml
- [ ] Readiness gates configured (HTTP probes for ws_api/dashboard)
- [ ] Health checks configured (periodic HTTP probes)
- [ ] File watcher configured (engine + API code directories)
- [ ] Process groups enabled (Job on Windows / setsid on POSIX)

## Success Criteria (Phase 2 Testing)

After Phase 1 implementation, Victor will verify:

1. **Singleton works:** Only one supervisor process, survives process death
2. **No stale locks:** .launcher.lock deleted, .locks/*.pid cleaned
3. **Services start:** All 7 services reach "ready" state via probes
4. **Hot-reload works:** Touch consciousness_engine_v2.py → ws_api restarts only
5. **Crash recovery:** Kill ws_api → backoff 1,2,4,8s → quarantine after 10 failures
6. **Parallel run:** MPSv3 + current guardian run simultaneously for 24 hours

## Files for Atlas

All required files ready:
- Specification: `docs/specs/v2/ops_and_viz/mpsv3_supervisor.md`
- Skeletons: Lines 850-1130 of spec (SingletonLease, ServiceRunner, etc.)
- Service list: 7 services (FalkorDB, ws_api, conversation_watcher, stimulus_injection, signals_collector, autonomy_orchestrator, dashboard)
- Current config: Backed up in this directory

---

**Victor "The Resurrector"**
Phase 0 complete. Standing by for Phase 2 operational testing once Atlas delivers Phase 1.
