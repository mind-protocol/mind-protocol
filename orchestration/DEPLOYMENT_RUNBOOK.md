# Mind Protocol Deployment Runbook

**Document Version:** 1.0
**Last Updated:** 2025-10-29
**Author:** Atlas (Infrastructure Engineer)
**Purpose:** Step-by-step procedures for deploying, verifying, and rolling back Mind Protocol services

---

## Overview

This runbook provides operational procedures for Mind Protocol deployment. Use this for:
- ✅ **Initial deployment** - First-time setup in new environment
- ✅ **Service restarts** - Restarting services after code changes
- ✅ **Rollback procedures** - Reverting to last known good state
- ✅ **Troubleshooting** - Diagnosing deployment failures

**Target Audience:** Infrastructure engineers, DevOps, operators deploying Mind Protocol

---

## Pre-Deployment Checklist

**Before deploying, verify ALL items below. Do not proceed if any item fails.**

### Environment Verification

```bash
# 1. Verify Docker is running
docker ps
# Expected: Docker responds with container list (may be empty)

# 2. Verify Python version
python --version
# Expected: Python 3.9+ (e.g., "Python 3.10.12")

# 3. Verify Node.js version
node --version
# Expected: Node.js 18+ (e.g., "v18.17.0")

# 4. Verify working directory
pwd
# Expected: /home/mind-protocol/mindprotocol (or your installation path)
```

### Dependency Verification

```bash
# 5. Verify Python dependencies installed
python -c "import falkordb, websockets, fastapi, redis; print('Python dependencies OK')"
# Expected: "Python dependencies OK"

# 6. Verify Node.js dependencies installed
npm list next react --depth=0
# Expected: Shows next@X.X.X and react@X.X.X versions

# 7. Verify FalkorDB Docker image exists
docker images falkordb/falkordb
# Expected: Shows falkordb/falkordb image (may need to pull if missing)
```

### Configuration Verification

```bash
# 8. Verify services.yaml exists
ls -l orchestration/services/mpsv3/services.yaml
# Expected: Shows file exists

# 9. Check environment variables (optional economy vars)
echo "WS_PORT=${WS_PORT:-not set}"
echo "DASHBOARD_PORT=${DASHBOARD_PORT:-not set}"
echo "MIND_MINT_ADDRESS=${MIND_MINT_ADDRESS:-not set (optional)}"
echo "HELIUS_API_KEY=${HELIUS_API_KEY:-not set (optional)}"
# Expected: Core vars use defaults from services.yaml, economy vars optional

# 10. Verify no port conflicts
lsof -i :6379 -i :8000 -i :3000
# Expected: Either no output (ports free) OR only FalkorDB on 6379 if already running
```

**STOP HERE if any verification fails. Resolve issues before proceeding.**

---

## Deployment Procedure

### Phase 1: Infrastructure Setup

**Objective:** Start core infrastructure (Docker containers, database)

```bash
# Step 1: Create FalkorDB container (if doesn't exist)
docker ps -a | grep mind_protocol_falkordb || \
docker run -d \
  --name mind_protocol_falkordb \
  -p 6379:6379 \
  --restart unless-stopped \
  falkordb/falkordb:latest

# Step 2: Verify FalkorDB is healthy
timeout 30 bash -c 'until redis-cli ping > /dev/null 2>&1; do sleep 1; done'
redis-cli ping
# Expected: PONG

# Step 3: Verify FalkorDB modules loaded
redis-cli MODULE LIST | grep -E "graph|vectorset"
# Expected: Shows "graph" and "vectorset" modules

# Step 4: Check FalkorDB logs for errors
docker logs --tail 50 mind_protocol_falkordb | grep -i error
# Expected: No critical errors (warnings OK)
```

**Validation Checkpoint 1:**
- [ ] FalkorDB container running (docker ps shows "Up" status)
- [ ] FalkorDB responds to ping
- [ ] FalkorDB modules loaded (graph + vectorset)
- [ ] No critical errors in logs

**If validation fails:** Review "Troubleshooting - Infrastructure Issues" section below.

---

### Phase 2: Start MPSv3 Supervisor

**Objective:** Start service orchestration system

```bash
# Step 5: Navigate to project root
cd /home/mind-protocol/mindprotocol

# Step 6: Start MPSv3 supervisor
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml

# Expected output (within 60 seconds):
# [MPSv3] Starting service: falkordb
# [MPSv3] Service falkordb ready (tcp://127.0.0.1:6379)
# [MPSv3] Starting service: ws_api
# [MPSv3] Service ws_api ready (http://127.0.0.1:8000/healthz)
# [MPSv3] Starting service: dashboard
# [MPSv3] Service dashboard ready (http://127.0.0.1:3000)
# [MPSv3] All services operational
```

**Service Start Order (Enforced by Dependency Graph):**
1. `falkordb` (no dependencies)
2. `ws_api` (requires falkordb)
3. `dashboard`, `conversation_watcher`, `signals_collector`, `autonomy_orchestrator` (all require ws_api)

**Expected Timeline:**
- FalkorDB ready: 5-10 seconds (container already running, just health check)
- ws_api ready: 20-40 seconds (imports, graph initialization, engine bootstrap)
- Dashboard ready: 30-60 seconds (Next.js compilation, page rendering)
- Watchers ready: 5-10 seconds each (after ws_api)

**Validation Checkpoint 2:**
- [ ] MPSv3 supervisor started without errors
- [ ] All services show "ready" status
- [ ] No service restart loops (check for repeated "restarting" messages)
- [ ] Supervisor logs show "All services operational"

**If validation fails:** Review "Troubleshooting - Service Start Issues" section below.

---

### Phase 3: Health Verification

**Objective:** Verify all services responding correctly

Run these commands in a **separate terminal** (leave supervisor running in original terminal):

```bash
# Step 7: Verify FalkorDB health
redis-cli ping
# Expected: PONG

# Step 8: Verify WebSocket server health
curl http://localhost:8000/healthz?selftest=1
# Expected: {"status":"healthy", ...}

# Step 9: Verify dashboard loading
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Step 10: Verify WebSocket server API endpoints
curl http://localhost:8000/api/consciousness/status | python -m json.tool
# Expected: JSON with citizen data (e.g., {"ada": {...}, "felix": {...}})

# Step 11: Check consciousness engine ticks
curl http://localhost:8000/api/consciousness/status | grep -o '"ticks":[0-9]*' | head -3
# Expected: Shows tick counts for citizens (should be increasing)

# Step 12: Verify economy runtime activated (if configured)
curl http://localhost:8000/api/economy/snapshot/autonomy 2>&1
# Expected: JSON with economy data OR 404 if not configured (both OK)
```

**Validation Checkpoint 3:**
- [ ] FalkorDB responds to Redis commands
- [ ] WebSocket server /healthz returns healthy
- [ ] Dashboard returns HTTP 200
- [ ] Consciousness status API returns citizen data
- [ ] Tick counts are non-zero (engines processing)
- [ ] Economy API responds (or 404 if not configured)

**If validation fails:** Review "Troubleshooting - Health Check Failures" section below.

---

### Phase 4: Functional Smoke Tests

**Objective:** Verify core functionality works end-to-end

```bash
# Step 13: Test FalkorDB graph queries
redis-cli GRAPH.QUERY consciousness-infrastructure_ada \
  "MATCH (n:Node) RETURN count(n) AS node_count"
# Expected: Returns node count (may be 0 for fresh deployment, >0 for existing data)

# Step 14: Test consciousness engine initialization
curl http://localhost:8000/api/consciousness/status | \
  python -c "import sys, json; data=json.load(sys.stdin); print('Engines:', ', '.join(data.keys()))"
# Expected: "Engines: ada, atlas, felix, iris, luca, victor" (or subset if selective bootstrap)

# Step 15: Test dashboard loads in browser (manual check)
echo "Open http://localhost:3000 in browser and verify:"
echo "  - Page loads without errors"
echo "  - Consciousness visualization renders"
echo "  - Citizen list shows status"
echo "  - No console errors in browser DevTools"
# Expected: Dashboard functional, no console errors

# Step 16: Test hot-reload (if MP_HOT_RELOAD=1)
touch orchestration/core/node.py
sleep 5
curl http://localhost:8000/healthz
# Expected: Service restarted gracefully, /healthz still returns healthy
```

**Validation Checkpoint 4:**
- [ ] FalkorDB accepts graph queries
- [ ] Consciousness engines initialized for all citizens
- [ ] Dashboard loads and renders correctly
- [ ] No browser console errors
- [ ] Hot-reload works (if enabled)

**If validation fails:** Review "Troubleshooting - Functional Issues" section below.

---

### Phase 5: Deployment Complete

**Objective:** Document successful deployment

```bash
# Step 17: Record deployment timestamp
date '+%Y-%m-%d %H:%M:%S' > .deployment_timestamp
cat .deployment_timestamp

# Step 18: Save service status snapshot
curl http://localhost:8000/api/consciousness/status > .deployment_status.json
echo "Deployment status saved to .deployment_status.json"

# Step 19: Check for warnings in logs
docker logs mind_protocol_falkordb --since 5m 2>&1 | grep -i warning
# Review warnings, determine if action needed

# Step 20: Monitor for stability (next 5 minutes)
echo "Deployment complete. Monitor supervisor logs for next 5 minutes."
echo "Watch for:"
echo "  - Service restart loops (repeated 'restarting' messages)"
echo "  - Error messages in logs"
echo "  - Memory/CPU spikes (use htop or docker stats)"
```

**Validation Checkpoint 5:**
- [ ] Deployment timestamp recorded
- [ ] Service status snapshot saved
- [ ] Warnings reviewed and documented
- [ ] System stable for 5+ minutes
- [ ] No service restarts after initial startup

**Deployment Complete ✅**

---

## Post-Deployment Verification

**Run these checks 30 minutes after deployment to verify stability:**

```bash
# Check 1: Services still running
curl http://localhost:8000/healthz
# Expected: {"status":"healthy"}

# Check 2: Tick counts increasing (engines processing)
curl http://localhost:8000/api/consciousness/status | grep -o '"ticks":[0-9]*' | head -3
# Compare to counts from Phase 3 - should be higher

# Check 3: No error accumulation in logs
docker logs mind_protocol_falkordb --since 30m 2>&1 | grep -i error | wc -l
# Expected: Low count (<10), review if high

# Check 4: Memory usage stable
docker stats mind_protocol_falkordb --no-stream --format "{{.MemUsage}}"
# Expected: Memory not continuously increasing

# Check 5: Dashboard still responsive
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK
```

**If any check fails:** Proceed to rollback procedure immediately.

---

## Rollback Procedure

**Use this procedure if deployment fails or instability detected.**

### Scenario A: Service Won't Start (Pre-Production)

**Problem:** MPSv3 supervisor fails to start services, repeated errors in logs

**Solution:** Stop supervisor, revert code, restart

```bash
# Step 1: Stop MPSv3 supervisor
# In supervisor terminal: Press Ctrl+C
# Wait for graceful shutdown (up to 30 seconds)

# Step 2: Revert code changes (if recent git commits)
git log --oneline -5  # Review recent commits
git reset --hard HEAD~1  # Revert last commit (adjust ~N for multiple commits)

# Step 3: Verify code reverted
git log --oneline -1  # Should show previous commit

# Step 4: Restart deployment from Phase 2
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml
```

---

### Scenario B: Service Running But Unstable (Post-Production)

**Problem:** Services started but showing errors, restart loops, or degraded performance

**Solution:** Graceful downgrade to last known good state

```bash
# Step 1: Stop MPSv3 supervisor gracefully
# In supervisor terminal: Press Ctrl+C

# Step 2: Restore last known good deployment
git log --oneline -10  # Find last known good commit
git reset --hard <commit-hash>  # Replace with actual commit hash

# Step 3: Verify deployment timestamp
cat .deployment_timestamp  # Shows timestamp of last successful deployment

# Step 4: Clean any corrupted state (if necessary)
# WARNING: This clears graph data - only use if corruption suspected
# docker stop mind_protocol_falkordb
# docker rm mind_protocol_falkordb
# docker run -d --name mind_protocol_falkordb -p 6379:6379 falkordb/falkordb:latest

# Step 5: Restart deployment from Phase 1
# Follow full deployment procedure from beginning
```

---

### Scenario C: Complete System Failure

**Problem:** Nothing working, manual recovery required

**Solution:** Nuclear option - clean slate restart

```bash
# Step 1: Stop all services
pkill -f mpsv3_supervisor
pkill -f websocket_server
pkill -f "npm run dev"

# Step 2: Stop and remove containers
docker stop mind_protocol_falkordb
docker rm mind_protocol_falkordb

# Step 3: Clean any lock files
rm -f .locks/*.pid

# Step 4: Verify ports freed
lsof -i :6379 -i :8000 -i :3000
# Expected: No output (all ports free)

# Step 5: Restore code to last known good state
git reset --hard <last-known-good-commit>

# Step 6: Full redeployment from Phase 1
# Follow complete deployment procedure
```

---

## Troubleshooting

### Infrastructure Issues

**Problem:** FalkorDB won't start or respond

```bash
# Diagnosis
docker logs mind_protocol_falkordb --tail 100
docker inspect mind_protocol_falkordb | grep -A 10 "State"

# Common causes:
# 1. Port 6379 already in use
lsof -i :6379  # Check what's using port
# Solution: Stop conflicting process or use different port

# 2. Docker daemon not running
docker ps
# Solution: Start Docker daemon (sudo systemctl start docker)

# 3. Container crashed
docker ps -a | grep mind_protocol_falkordb
# Solution: Check logs, remove and recreate container
```

---

### Service Start Issues

**Problem:** ws_api fails to start or times out

```bash
# Diagnosis
# Check supervisor logs for error messages
# Common errors:
# - "Connection refused" → FalkorDB not ready
# - "Import error" → Missing Python dependencies
# - "Address already in use" → Port conflict

# Solution 1: Verify FalkorDB health
redis-cli ping

# Solution 2: Check for port conflicts
lsof -i :8000

# Solution 3: Test manual start (isolate issue)
cd /home/mind-protocol/mindprotocol
python -m orchestration.adapters.ws.websocket_server
# Review error messages directly
```

---

### Health Check Failures

**Problem:** /healthz returns errors or timeouts

```bash
# Diagnosis
curl -v http://localhost:8000/healthz?selftest=1

# Common causes:
# 1. FalkorDB connection failed
redis-cli ping  # Should return PONG

# 2. Consciousness engines not initialized
curl http://localhost:8000/api/consciousness/status
# Check if any engines show "not_initialized"

# 3. Economy runtime startup failed (warning only)
# Check supervisor logs for "Economy runtime failed to start"
# Solution: Review economy env vars (ECONOMY_REDIS_URL, etc.)
```

---

### Functional Issues

**Problem:** Dashboard loads but not working correctly

```bash
# Diagnosis
# 1. Check browser console for errors (F12 → Console tab)

# 2. Verify WebSocket connection
curl http://localhost:8000/api/consciousness/status
# If this works but dashboard broken → frontend issue

# 3. Check Next.js compilation
# In supervisor logs, search for dashboard compilation errors

# Solution: Restart dashboard service only
# In supervisor terminal: Ctrl+C to stop all
# Then restart (supervisor will rebuild dashboard)
```

---

## Monitoring and Maintenance

### Daily Health Checks

```bash
# Run this daily to verify system health
./orchestration/scripts/daily_health_check.sh

# Or manually:
curl http://localhost:8000/healthz
docker stats mind_protocol_falkordb --no-stream
df -h  # Check disk space
```

---

### Log Management

```bash
# View recent logs
docker logs mind_protocol_falkordb --since 1h

# Search for errors
docker logs mind_protocol_falkordb 2>&1 | grep -i error

# Monitor logs in real-time
docker logs -f mind_protocol_falkordb
```

---

### Performance Monitoring

```bash
# CPU/Memory usage
docker stats mind_protocol_falkordb --no-stream

# Disk usage
du -sh /var/lib/docker/volumes/  # Docker volumes
du -sh .  # Project directory

# Network connections
netstat -an | grep -E "6379|8000|3000"
```

---

## Appendix

### Environment Variable Reference

See `CONFIG_REQUIREMENTS.md` for complete environment variable documentation.

**Quick Reference:**

```bash
# Core Infrastructure
export WS_PORT=8000
export DASHBOARD_PORT=3000
export MP_PERSIST_ENABLED=1

# Economy Runtime (Optional)
export ECONOMY_REDIS_URL="redis://localhost:6379/0"
export MIND_MINT_ADDRESS="<your-mint-address>"
export HELIUS_API_KEY="<your-api-key>"
export UBC_TREASURY_WALLET="<treasury-address>"
export UBC_CITIZEN_WALLETS='{"ada":"<wallet>", "felix":"<wallet>"}'
```

---

### Service Dependency Graph

```
falkordb (Docker container)
  ↓
ws_api (WebSocket server + consciousness engines + economy runtime)
  ↓
├─ dashboard (Next.js frontend)
├─ conversation_watcher (Context capture)
├─ signals_collector (Telemetry)
└─ autonomy_orchestrator (Autonomy coordination)
```

**Restart Impact:**
- Restarting `falkordb` → Requires restarting ALL services
- Restarting `ws_api` → Requires restarting dashboard, watchers, collectors
- Restarting `dashboard` → No impact on other services

---

### Common Commands Quick Reference

```bash
# Start system
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml

# Stop system
# In supervisor terminal: Ctrl+C

# Check service health
curl http://localhost:8000/healthz

# View service status
curl http://localhost:8000/api/consciousness/status | python -m json.tool

# Restart single service (not recommended - use supervisor)
# Instead: Edit code, supervisor will auto-reload via hot-reload

# View logs
docker logs mind_protocol_falkordb --tail 50

# Check ports
lsof -i :6379 -i :8000 -i :3000
```

---

## Document Maintenance

**Update this document when:**
- Adding new services to system
- Changing deployment procedures
- Discovering new failure modes
- Adding monitoring tools
- Changing configuration requirements

**Version History:**
- 1.0 (2025-10-29): Initial deployment runbook

---

**Status:** Deployment procedures documented. Ready for staging deployment testing.

---

*Atlas - Infrastructure Engineer*
*"Deployment is not complete until rollback procedures are tested."*
