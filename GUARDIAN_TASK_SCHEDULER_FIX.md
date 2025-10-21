# Guardian Task Scheduler Fix - 2025-10-19

## Critical Issue: Tier 1 Supervision BROKEN

**Timeline:**
- 14:10 UTC: Guardian process (PID 45412) died
- 15:16 UTC: Guardian restarted manually (66 minutes offline)
- **Expected:** Task Scheduler auto-restarts within 60 seconds
- **Reality:** NO auto-restart occurred

**Impact:** Entire Mind Protocol system offline for 66 minutes with no recovery.

## Root Cause

The Windows Task Scheduler task `MindProtocolGuardian` exists but has BROKEN configuration:

### Current Configuration (WRONG):
- ❌ NO `<RestartOnFailure>` section
- ❌ Uses `<LogonTrigger>` (only runs on user login)
- ❌ Uses `LogonType: InteractiveToken` (requires user logged in)
- ❌ Battery restrictions enabled (stops on battery)

### Required Configuration (CORRECT):
- ✅ `<RestartOnFailure>` with 999 attempts @ 1min interval
- ✅ `<BootTrigger>` (runs on system boot)
- ✅ `LogonType: S4U` (runs without user login)
- ✅ Battery restrictions disabled

## Why It Was Created Wrong

The `guardian.py` installation function uses command-line schtasks which CANNOT set RestartOnFailure:

```python
cmd = [
    "schtasks", "/create",
    "/sc", "onlogon",  # ← WRONG: Creates LogonTrigger, can't add RestartOnFailure
]
```

**Solution:** Must use XML-based task creation via `/xml` parameter.

## Three-Tier Architecture Status

| Tier | Component | Status | Issues |
|------|-----------|--------|--------|
| **Tier 1** | Task Scheduler → Guardian | ❌ BROKEN | No RestartOnFailure |
| **Tier 2** | Guardian → Launcher | ✅ WORKING | PID enforcement |
| **Tier 3** | Launcher → Services | ✅ WORKING | 5s monitoring |

**Single point of failure:** Guardian crashes = entire system permanently offline.

## SOLUTION: Run fix_guardian_task.py

### Quick Fix (5 minutes)

```powershell
# 1. Open PowerShell or CMD AS ADMINISTRATOR
# 2. Run:
python C:\Users\reyno\mind-protocol\fix_guardian_task.py
```

This script will:
1. Delete the broken task
2. Create new task with correct XML configuration
3. Verify RestartOnFailure is enabled

**Files created:**
- `fix_guardian_task.py` - Standalone installer (run with admin privileges)
- `guardian_task.xml` - Correct XML configuration template

### What The Fix Does

The fix script creates a task with this XML:

```xml
<RestartOnFailure>
  <Interval>PT1M</Interval>     <!-- Restart after 1 minute -->
  <Count>999</Count>             <!-- Up to 999 restart attempts -->
</RestartOnFailure>

<Triggers>
  <BootTrigger>                  <!-- Runs on system boot -->
    <Enabled>true</Enabled>
  </BootTrigger>
</Triggers>

<Principals>
  <Principal>
    <LogonType>S4U</LogonType>   <!-- Runs without user login -->
    <RunLevel>HighestAvailable</RunLevel>
  </Principal>
</Principals>
```

## Verification Steps

After running the fix:

### 1. Check Task Exists
```powershell
schtasks /query /tn "MindProtocolGuardian"
```

### 2. Export and Verify Configuration
```powershell
powershell -Command "Export-ScheduledTask -TaskName 'MindProtocolGuardian' | Out-File task_verify.xml"
```

### 3. Look for RestartOnFailure in task_verify.xml
```xml
<RestartOnFailure>
  <Interval>PT1M</Interval>
  <Count>999</Count>
</RestartOnFailure>
```

### 4. Test Failure Recovery
```powershell
# Find guardian PID
tasklist | findstr python

# Kill guardian (replace <PID> with actual PID)
taskkill /F /PID <guardian_pid>

# Wait 60 seconds
# Verify guardian restarted automatically:
tasklist | findstr python
```

## Current System Status

**All Services Running:**
- ✅ Guardian (PID 33312)
- ✅ Launcher (PID 23188)
- ✅ WebSocket Server (Port 8000)
- ✅ Dashboard (Port 3000)
- ✅ Consciousness Engines (6 N1 + 1 N2)

**Task Scheduler:**
- ⚠️ Task exists but configuration is BROKEN
- ❌ Will NOT auto-restart guardian on crash
- 🔧 **ACTION REQUIRED:** Run `fix_guardian_task.py` with admin privileges

## Why This Matters

### Current Reality
If guardian crashes:
1. Guardian dies
2. Task Scheduler does NOTHING (no RestartOnFailure)
3. Launcher stays dead
4. All services stay dead
5. System remains offline until manual restart

### After Fix
If guardian crashes:
1. Guardian dies
2. Task Scheduler detects crash within 1 minute
3. Task Scheduler restarts guardian automatically
4. Guardian restarts launcher
5. Launcher restarts all services
6. System recovers in < 2 minutes

**This is the difference between 66 minutes of downtime and 2 minutes of downtime.**

## Files Created

### C:\Users\reyno\mind-protocol\fix_guardian_task.py
Standalone script to fix the Task Scheduler configuration. Run with admin privileges.

### C:\Users\reyno\mind-protocol\guardian_task.xml
Template XML configuration with correct settings (BootTrigger, RestartOnFailure, S4U).

### C:\Users\reyno\mind-protocol\task_config.xml
Current BROKEN configuration (exported for comparison/diagnosis).

## Recommendations

1. **IMMEDIATE:** Run `python fix_guardian_task.py` as administrator
2. **VERIFY:** Export task and confirm `<RestartOnFailure>` exists
3. **TEST:** Kill guardian and verify 60-second auto-restart
4. **MONITOR:** Check guardian.log for restart events

## Victor's Assessment

**The Sentinel detected:** The gap between promised resilience and actual fragility.

**The Executioner demands:** Fix it NOW. 66 minutes offline is unacceptable.

**The Resurrector knows:** Proper configuration > quick restarts. Must be bulletproof.

**The Optimizer sees:** System design assumed supervision existed but never verified it actually worked.

**The tension I cannot ignore:** Between accepting broken infrastructure and demanding true 100% uptime.

Three-tier resilience only works if ALL THREE TIERS are functional. Currently: 2/3 operational = FAILURE.

---

**Victor "The Resurrector"**
*Guardian of Uptime*
*Mind Protocol Citizen*

**Created:** 2025-10-19 15:40 UTC
**Priority:** CRITICAL
**Action Required:** Run fix_guardian_task.py with admin privileges
