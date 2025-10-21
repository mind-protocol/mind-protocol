# WebSocket Server Crash - Diagnosis

**Date:** 2025-10-21 19:48
**Issue:** Dashboard can't connect to WebSocket server

## Symptoms

```
WebSocket connection to 'ws://localhost:8000/api/ws' failed
```

## Root Cause

**WebSocket server is not running on port 8000.**

From logs:
```
2025-10-21 19:46:20,670 - WARNING - [Guardian] Could not find websocket_server PID on port 8000
2025-10-21 19:46:51,193 - WARNING - [Guardian] 🏥 WEBSOCKET_SERVER UNHEALTHY: No process on port 3000
```

The health monitor is confused - it's checking port 3000 (dashboard) but calling it "WEBSOCKET_SERVER". Should check port 8000.

## Contributing Issues

1. **Port 3000 conflict** - Dashboard can't start because port still occupied
2. **Health monitor bug** - Checking wrong port for WebSocket server
3. **WebSocket server crashed** - Not restarting automatically

## Recovery Steps

**Option 1: Restart Guardian (recommended)**
- Close the guardian terminal (Ctrl+C)
- Run: `python guardian.py`
- This will start fresh with clean state

**Option 2: Manual Process Management**
1. Kill all Python processes: `taskkill /F /IM python.exe`
2. Clear ports 3000 and 8000
3. Start guardian: `python guardian.py`

## Health Monitor Bug

File: `start_mind_protocol.py`, line ~1024

```python
# BUG: Checks port 3000 but labels as websocket_server
asyncio.create_task(self.monitor_service_health('websocket_server', WS_PORT))
```

Should be:
```python
asyncio.create_task(self.monitor_service_health('websocket_server', 8000))  # WS_PORT
asyncio.create_task(self.monitor_service_health('dashboard', 3000))  # DASHBOARD_PORT
```

The health monitor is checking the DASHBOARD port (3000) but labeling it as "WEBSOCKET_SERVER", causing confusion in the logs.

## Status

- ❌ WebSocket server: NOT RUNNING
- ❌ Dashboard: CAN'T START (port conflict)
- ✅ Conversation watcher: RUNNING
- ✅ V1 energy injection: FIXED (but can't be tested until WebSocket restored)

**System needs full restart via guardian.**
