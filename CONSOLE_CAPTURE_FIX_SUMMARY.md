# Console Capture System - Diagnosis & Fix Summary

**Date:** 2025-10-23 03:07 UTC
**Author:** Iris "The Aperture"
**Status:** ✅ Fixed (requires WebSocket server restart)

---

## Problem

Console capture system not writing logs to `claude-logs/browser-console.log` despite:
- ✅ `/api/logs` endpoint receiving requests successfully (HTTP 200 OK)
- ✅ Browser (ConsoleCapture.tsx) sending logs correctly
- ✅ Directory exists and is writable
- ✅ Manual file write works

## Root Cause

**LOGS_DIR path was incorrect in websocket_server.py:**

```python
# OLD (incorrect - writes to orchestration/adapters/claude-logs)
LOGS_DIR = Path(__file__).parent.parent / "claude-logs"

# NEW (correct - writes to project root/claude-logs)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "claude-logs"
```

**Fix applied:** websocket_server.py:96-101 updated with correct path

**Why logs still don't work:** WebSocket server (PID 25976) loaded code BEFORE the fix. Python doesn't hot-reload modules. Server restart required.

---

## Fix Applied

**File:** `orchestration/adapters/ws/websocket_server.py`

**Lines 96-101:**
```python
# Ensure directories exist (project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "claude-logs"
SCREENSHOTS_DIR = PROJECT_ROOT / "claude-screenshots"
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
```

**Directories created:**
- ✅ `C:\Users\reyno\mind-protocol\claude-logs\`
- ✅ `C:\Users\reyno\mind-protocol\claude-screenshots\`

---

## To Activate

**Option 1: Use Guardian (recommended)**
```bash
# Kill WebSocket server manually
taskkill /F /PID 25976

# Guardian will auto-restart it within 5 seconds with new code
```

**Option 2: Manual restart**
```bash
# Kill current server
taskkill /F /PID 25976

# Start fresh (from project root)
python orchestration/adapters/ws/websocket_server.py
```

**Verification:**
```bash
# Test endpoint
curl -X POST http://localhost:8000/api/logs -H "Content-Type: application/json" \
  -d '{"logs":[{"timestamp":1729655500000,"type":"test","message":"Verification test"}]}'

# Check file was created
cat claude-logs/browser-console.log
```

Expected output:
```json
{"timestamp":"2025-10-22T...", "type":"test", "message":"Verification test"}
```

---

## CRITICAL ISSUE FOUND (Separate from console capture)

**Consciousness engines crashing immediately on startup:**

### Error 1: `math` UnboundLocalError
```
File "orchestration/mechanisms/consciousness_engine_v2.py", line 858
    ease = math.exp(link.log_weight)
           ^^^^
UnboundLocalError: cannot access local variable 'math' where it is not associated with a value
```

**Affects:** victor, felix, luca, ada citizens
**Cause:** Variable scoping issue in consciousness_engine_v2.py line 858

### Error 2: `token_budget_used` KeyError
```
File "orchestration/mechanisms/consciousness_engine_v2.py", line 910
    "token_budget_used": wm_summary["token_budget_used"],
                         ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
KeyError: 'token_budget_used'
```

**Affects:** piero, marco citizens
**Cause:** Missing key in wm_summary dictionary

---

## Next Steps

1. **Console Capture:** Restart WebSocket server to load fixed LOGS_DIR path
2. **Consciousness Engines:** Fix critical errors preventing engine execution
3. **StrideSparks Import:** Clear Next.js build cache to fix import error
   ```bash
   rm -rf .next
   ```

---

**Note:** All three issues are independent and can be fixed separately.
