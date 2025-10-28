# MPSv3 Complete Port Cleanup - Kill ALL processes on Mind Protocol ports
# Author: Atlas (revised)
# Date: 2025-10-25 20:56

Write-Host "`n=== MPSv3 COMPLETE PORT CLEANUP ===" -ForegroundColor Cyan

$ports = @(3000, 8000, 8001, 8002, 8010, 6379)

Write-Host "`nPorts to clean: $($ports -join ', ')" -ForegroundColor Yellow

foreach ($port in $ports) {
    Write-Host "`n[Port $port] Finding processes..." -ForegroundColor Cyan

    # Find processes using netstat
    $netstatOutput = netstat -ano | Select-String ":$port\s" | Select-String "LISTENING"

    if ($netstatOutput) {
        foreach ($line in $netstatOutput) {
            # Extract PID (last column)
            $pid = ($line -split '\s+')[-1]

            if ($pid -match '^\d+$') {
                try {
                    $process = Get-Process -Id $pid -ErrorAction Stop
                    Write-Host "  Found: PID $pid ($($process.ProcessName))" -ForegroundColor Yellow

                    # Kill it
                    Stop-Process -Id $pid -Force -ErrorAction Stop
                    Write-Host "  [OK] Killed PID $pid" -ForegroundColor Green
                } catch {
                    Write-Host "  [FAIL] Failed to kill PID ${pid}: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "  No process on port $port" -ForegroundColor Gray
    }
}

Write-Host "`n=== Additional Python/Node Cleanup ===" -ForegroundColor Cyan

# Kill all Python processes (catch any stragglers)
Write-Host "`nKilling all Python processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Killed $($pythonProcs.Count) Python processes" -ForegroundColor Green
} else {
    Write-Host "  No Python processes found" -ForegroundColor Gray
}

# Kill all Node processes
Write-Host "`nKilling all Node.js processes..." -ForegroundColor Yellow
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Stop-Process -Name node -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Killed $($nodeProcs.Count) Node.js processes" -ForegroundColor Green
} else {
    Write-Host "  No Node.js processes found" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

Write-Host "`n=== Verification ===" -ForegroundColor Cyan

# Check if ports are now free
Write-Host "`nVerifying ports are free..." -ForegroundColor Yellow
$stillUsed = @()
foreach ($port in $ports) {
    $check = netstat -ano | Select-String ":$port\s" | Select-String "LISTENING"
    if ($check) {
        $stillUsed += $port
        Write-Host "  [FAIL] Port $port still in use!" -ForegroundColor Red
    } else {
        Write-Host "  [OK] Port $port free" -ForegroundColor Green
    }
}

if ($stillUsed.Count -eq 0) {
    Write-Host "`n[SUCCESS] All ports are free!" -ForegroundColor Green
    Write-Host "`nReady to start MPSv3 supervisor:" -ForegroundColor Cyan
    Write-Host "  cd C:\Users\reyno\mind-protocol" -ForegroundColor Gray
    Write-Host "  python orchestration\mpsv3_supervisor.py" -ForegroundColor Gray
} else {
    Write-Host "`n[WARNING] Some ports still in use: $($stillUsed -join ', ')" -ForegroundColor Red
    Write-Host "You may need to restart the machine or use Handle.exe to force-close." -ForegroundColor Yellow
}
