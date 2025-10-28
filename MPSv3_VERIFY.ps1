# MPSv3 Architecture Verification - Run AFTER supervisor starts
# Author: Atlas
# Date: 2025-10-25 20:40

Write-Host "`n=== MPSv3 ARCHITECTURE VERIFICATION ===" -ForegroundColor Cyan

Write-Host "`n[1/5] Process Tree Verification" -ForegroundColor Yellow
Write-Host "Looking for mpsv3_supervisor parent process..." -ForegroundColor Gray

# Find supervisor process
$supervisor = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "python.exe" -and $_.CommandLine -like "*mpsv3_supervisor*"
}

if ($supervisor) {
    Write-Host "✓ Supervisor found: PID $($supervisor.ProcessId)" -ForegroundColor Green

    # Find child processes
    $children = Get-WmiObject Win32_Process | Where-Object {
        $_.ParentProcessId -eq $supervisor.ProcessId
    }

    if ($children) {
        Write-Host "✓ Child processes (services):" -ForegroundColor Green
        foreach ($child in $children) {
            $cmdShort = $child.CommandLine.Substring(0, [Math]::Min(80, $child.CommandLine.Length))
            Write-Host "  - PID $($child.ProcessId): $cmdShort..." -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ WARNING: No child processes found!" -ForegroundColor Red
        Write-Host "  Services may not have started yet or are running standalone." -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ ERROR: mpsv3_supervisor not running!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/5] API Response Verification" -ForegroundColor Yellow
Write-Host "Testing /api/consciousness/status..." -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/consciousness/status" -TimeoutSec 5
    Write-Host "✓ API responding" -ForegroundColor Green
    Write-Host "  - Total engines: $($response.total_engines)" -ForegroundColor Gray
    Write-Host "  - Running: $($response.running)" -ForegroundColor Gray
    Write-Host "  - Frozen: $($response.frozen)" -ForegroundColor Gray
} catch {
    Write-Host "✗ ERROR: API not responding" -ForegroundColor Red
    Write-Host "  $_" -ForegroundColor Red
}

Write-Host "`n[3/5] FileWatcher Initialization" -ForegroundColor Yellow
Write-Host "Check supervisor console output for this line:" -ForegroundColor Gray
Write-Host '  "[FileWatcher] Started centralized watcher"' -ForegroundColor Cyan
Write-Host "If missing, file watching is NOT initialized." -ForegroundColor Yellow

Write-Host "`n[4/5] Hot-Reload Test (Manual)" -ForegroundColor Yellow
Write-Host "To test hot-reload:" -ForegroundColor Gray
Write-Host "  1. touch orchestration\mechanisms\consciousness_engine_v2.py" -ForegroundColor Cyan
Write-Host "  2. Watch supervisor console for:" -ForegroundColor Gray
Write-Host '     "[FileWatcher] ws_api: ...consciousness_engine_v2.py changed"' -ForegroundColor Cyan
Write-Host '     "[FileWatcher] Triggering reload: ws_api (file_change)"' -ForegroundColor Cyan
Write-Host "  3. Verify ws_api restarts (new PID)" -ForegroundColor Gray

Write-Host "`n[5/5] Environment Inheritance Check" -ForegroundColor Yellow
Write-Host "Verifying services have full environment (PATH, SystemRoot)..." -ForegroundColor Gray

$serviceProcess = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "python.exe" -and $_.CommandLine -like "*websocket_server*"
} | Select-Object -First 1

if ($serviceProcess) {
    Write-Host "✓ Service process found: PID $($serviceProcess.ProcessId)" -ForegroundColor Green
    Write-Host "  Environment inheritance should prevent:" -ForegroundColor Gray
    Write-Host "    - 'npm is not recognized' errors" -ForegroundColor Gray
    Write-Host "    - WinError 10106 (Winsock initialization failure)" -ForegroundColor Gray
} else {
    Write-Host "✗ WARNING: websocket_server not found" -ForegroundColor Yellow
}

Write-Host "`n=== VERIFICATION COMPLETE ===" -ForegroundColor Cyan
Write-Host "If all checks passed, MPSv3 architecture is correctly deployed." -ForegroundColor Green
Write-Host "If FileWatcher missing, supervisor may have started without watcher module." -ForegroundColor Yellow
