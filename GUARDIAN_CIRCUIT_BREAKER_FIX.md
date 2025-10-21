# Guardian Circuit Breaker Fix

**Date:** 2025-10-21
**Author:** Victor "The Resurrector"
**Problem:** Guardian gave up after 10 crashes, leaving system down for 9+ hours

---

## The Problem

### What Happened (2:05 AM)
1. Guardian detected launcher crashes repeatedly
2. After 10 crashes, guardian **gave up and exited**
3. System stayed DOWN until manual intervention (9+ hours later)
4. All crashes were identical: `adapter.load_graph()` hang in websocket_server.py

### Root Cause Analysis

**Immediate cause:** Guardian had exponential backoff BUT no resilience pattern:
```python
if restart_count >= 10:
    logger.error("GIVING UP after 10 crashes")
    return 1  # EXIT FOREVER
```

**Underlying cause:** websocket_server.py calls `adapter.load_graph()` which:
- Hangs for 12+ minutes trying to query FalkorDB
- Never binds port 8000 during hang
- Launcher waits 60s, sees port not bound, kills process
- Same failure repeats endlessly (crash loop)

### Why Exponential Backoff Wasn't Enough

Guardian HAD exponential backoff:
```python
wait_time = min(30, 2 ** min(restart_count, 5))  # 1s, 2s, 4s, 8s, 16s, 32s max
```

But the problem wasn't retry timing - it was **same failure mode repeating indefinitely**.

Exponential backoff helps with transient failures. This was a **structural failure** (engine initialization hangs).

---

## The Fix: Circuit Breaker with Degraded Mode

### New Behavior

**1. Never Give Up**
- Removed 10-crash exit limit
- Guardian runs forever, trying to keep SOMETHING running

**2. Circuit Breaker (After 3 consecutive failures)**
```python
if consecutive_failures >= 3 and not degraded_mode:
    degraded_mode = True
    logger.warning("⚡ CIRCUIT BREAKER TRIGGERED")
    logger.warning("⚡ Switching to DEGRADED MODE (--core-only)")
```

**3. Degraded Mode Startup**
```python
cmd = [sys.executable, str(LAUNCHER_SCRIPT)]
if degraded_mode:
    cmd.append("--core-only")  # Skips engine initialization
```

**4. Failure Pattern Tracking**
```python
failure_timestamps = deque(maxlen=20)  # Track last 20 failures
recent_failures = [t for t in failure_timestamps if now - t < timedelta(minutes=10)]

if len(recent_failures) >= 10:
    logger.error("🚨 CHRONIC FAILURE DETECTED")
    logger.error(f"🚨 {len(recent_failures)} failures in last 10 minutes")
    logger.error("🚨 This indicates a deeper infrastructure issue")
```

**5. Diagnostic Hints**
When chronic failure detected, logs:
```
🚨 Check:
   - FalkorDB health (docker ps)
   - adapter.load_graph() hang
   - Port conflicts (netstat -ano | findstr :8000)
```

---

## Degraded Mode Explained

**Full Mode:**
- Starts websocket_server WITH consciousness engine initialization
- websocket_server.py calls `adapter.load_graph()` to discover graphs
- If this hangs → crash loop

**Degraded Mode (--core-only):**
- Starts websocket_server WITHOUT consciousness engine initialization
- Skips the hang-prone `adapter.load_graph()` call
- Basic API stays functional even if engine broken
- Allows dashboard, conversation_watcher, viz_emitter to run

### What Works in Degraded Mode
✅ WebSocket server (port 8000) - API endpoints
✅ Conversation watcher - TRACE format capture
✅ Viz emitter (port 8765) - WebSocket event streaming
✅ Dashboard (port 3000) - Next.js frontend

❌ Consciousness engines - NOT initialized
❌ Graph traversal - No active engines to traverse
❌ Energy flow - No engines to process energy

**Purpose:** Keep infrastructure UP while root cause is being fixed.

---

## Operational Impact

### Before Fix
- 10 crashes → Guardian exits
- System stays DOWN until manual restart
- No visibility into failure pattern
- No degraded operation

### After Fix
- 3 failures → Switch to degraded mode
- System keeps running (degraded but alive)
- Chronic failure warnings logged
- Diagnostic hints provided
- Never gives up completely

### Example Flow

```
Crash #1: Launcher crashed (exit code 1)
          Waiting 2s before restart...

Crash #2: Launcher crashed (exit code 1)
          Waiting 4s before restart...

Crash #3: Launcher crashed (exit code 1)
          ⚡ CIRCUIT BREAKER TRIGGERED
          ⚡ Switching to DEGRADED MODE (--core-only)
          Waiting 8s before restart...

Restart:  Launcher started (PID 12345) [DEGRADED MODE]
          → Websocket server runs WITHOUT engine init
          → No adapter.load_graph() hang
          → Port 8000 binds successfully
          → Basic infrastructure UP

If degraded mode ALSO fails:
Crash #4-13: Continue trying degraded mode with backoff

After 10 failures in 10 min:
          🚨 CHRONIC FAILURE DETECTED
          🚨 10 failures in last 10 minutes
          🚨 Check: FalkorDB health, adapter.load_graph() hang, ports
          🚨 Guardian will keep trying in degraded mode...
```

---

## Files Modified

**guardian.py:**
- Added `from datetime import datetime, timedelta`
- Added `from collections import deque`
- Removed 10-crash exit limit
- Added circuit breaker logic (line 292-296)
- Added degraded mode flag passing (line 304-306)
- Added failure timestamp tracking (line 264, 282, 336)
- Added chronic failure detection (line 338-353)

**Changes:**
- `restart_count` - Total crashes (informational)
- `consecutive_failures` - Consecutive failures (triggers circuit breaker)
- `degraded_mode` - Boolean flag for --core-only mode
- `failure_timestamps` - Deque of last 20 failure times
- `last_chronic_warning` - Timestamp of last chronic warning (prevents spam)

---

## Testing

**To test circuit breaker:**
1. Start guardian: `python guardian.py`
2. Cause 3 consecutive launcher crashes (simulate by killing launcher)
3. Verify circuit breaker triggers and degraded mode starts
4. Verify launcher runs with --core-only flag

**To test chronic failure warning:**
1. Cause 10+ failures within 10 minutes
2. Verify chronic failure warning appears
3. Verify diagnostic hints logged
4. Verify warning doesn't spam (max every 30 min)

**Expected logs:**
```
MIND PROTOCOL GUARDIAN - ACTIVE (CIRCUIT BREAKER ENABLED)
Circuit Breaker Policy:
  - After 3 consecutive failures → Switch to degraded mode (--core-only)
  - After 10 minutes of failures → Chronic failure warning
  - Never gives up → Keeps trying with degraded mode
```

---

## What This Doesn't Fix

This fix implements **resilience**, not **root cause resolution**.

**Still needs fixing (by Felix):**
- `adapter.load_graph()` hang in websocket_server.py
- Add timeout to FalkorDB graph discovery query
- Handle FalkorDB connection failures gracefully
- Consider lazy engine initialization (start server first, init engines after)

**What guardian now does:**
- Detects the failure pattern
- Switches to degraded mode to keep infrastructure running
- Logs diagnostic information
- Never leaves system completely down

---

## Success Criteria

✅ Guardian never exits after repeated crashes
✅ System runs in degraded mode after 3 failures
✅ Chronic failures logged with diagnostic hints
✅ Infrastructure stays UP (even if degraded)
✅ Clear operational visibility into failure patterns

**Victor "The Resurrector" - No system stays dead on my watch.**

---

**Next:** Felix to fix `adapter.load_graph()` timeout issue in websocket_server.py:206
