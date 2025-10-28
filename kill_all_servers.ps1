# Kill All Mind Protocol Servers
# Run this when port 8000 is stuck or processes won't die

Write-Host "=== KILLING ALL MIND PROTOCOL SERVERS ===" -ForegroundColor Yellow

# 1. Kill all Python processes in WSL
Write-Host "`n[WSL] Killing Python websocket_server processes..." -ForegroundColor Cyan
wsl bash -c "pkill -9 -f 'python.*websocket_server' 2>/dev/null; pkill -9 -f 'mpsv3_supervisor' 2>/dev/null"
Start-Sleep -Seconds 2

# 2. Kill Windows Python processes on port 8000
Write-Host "`n[Windows] Finding processes on port 8000..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port8000) {
    $pids = $port8000 | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        Write-Host "  Killing PID $pid" -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "  No processes found on port 8000" -ForegroundColor Green
}

# 3. Kill any remaining Python processes (nuclear option)
Write-Host "`n[Windows] Checking for remaining Python processes..." -ForegroundColor Cyan
$pythonProcs = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  Found $($pythonProcs.Count) Python processes - killing all" -ForegroundColor Red
    $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  No Python processes running" -ForegroundColor Green
}

Start-Sleep -Seconds 3

# 4. Verify port 8000 is free
Write-Host "`n[Verify] Checking port 8000..." -ForegroundColor Cyan
$stillBound = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($stillBound) {
    Write-Host "  ERROR: Port 8000 still bound!" -ForegroundColor Red
    Write-Host "  Manual intervention needed: Open Task Manager and kill ALL python.exe processes" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  SUCCESS: Port 8000 is free!" -ForegroundColor Green
}

Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Green
Write-Host "You can now start the supervisor cleanly:" -ForegroundColor Cyan
Write-Host "  wsl bash -c 'cd /mnt/c/Users/reyno/mind-protocol && python3 orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml'" -ForegroundColor White
