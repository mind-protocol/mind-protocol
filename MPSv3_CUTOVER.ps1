# MPSv3 Surgical Cutover - Run in PowerShell as Admin
# Author: Atlas
# Date: 2025-10-25 20:40

Write-Host "`n=== STEP 1: Identify Mutex Holder and Standalone Services ===" -ForegroundColor Cyan

# Show all Python processes with command lines
Write-Host "`nPython processes:" -ForegroundColor Yellow
wmic process where "name='python.exe'" get ProcessId,CommandLine /format:list | Select-String "ProcessId|CommandLine"

Write-Host "`nLooking for specific services:" -ForegroundColor Yellow
$services = @("websocket_server", "conversation_watcher", "signals_collector", "stimulus_injection", "autonomy_orchestrator", "mpsv3_supervisor")
foreach ($svc in $services) {
    wmic process where "name='python.exe' and commandline like '%$svc%'" get ProcessId,CommandLine 2>$null
}

Write-Host "`n=== STEP 2: Kill All Python Processes (Clean Slate) ===" -ForegroundColor Cyan
Write-Host "This will kill all Python processes including any mutex holders." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to abort, or press Enter to continue..." -ForegroundColor Red
Read-Host

# Kill all python.exe processes
Write-Host "Killing all Python processes..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# Verify killed
$remaining = Get-Process python -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "WARNING: Some Python processes still running:" -ForegroundColor Red
    $remaining | Select-Object Id, ProcessName, StartTime
} else {
    Write-Host "SUCCESS: All Python processes killed." -ForegroundColor Green
}

Write-Host "`n=== STEP 3: Start MPSv3 Supervisor ===" -ForegroundColor Cyan
Write-Host "Starting supervisor from: C:\Users\reyno\mind-protocol" -ForegroundColor Yellow

cd C:\Users\reyno\mind-protocol

Write-Host "`nExpected output:" -ForegroundColor Yellow
Write-Host "  - [SingletonLease] Acquired Windows mutex: Global\MPSv3_Supervisor" -ForegroundColor Gray
Write-Host "  - [MPSv3] Loading services from ..." -ForegroundColor Gray
Write-Host "  - [MPSv3] Starting all services..." -ForegroundColor Gray
Write-Host "  - [FileWatcher] Started centralized watcher" -ForegroundColor Gray
Write-Host "  - [ws_api] Started Windows process group (PID ...)" -ForegroundColor Gray
Write-Host "`nStarting supervisor..." -ForegroundColor Yellow

python orchestration\mpsv3_supervisor.py

# If execution reaches here, supervisor exited
Write-Host "`n=== Supervisor Exited ===" -ForegroundColor Red
