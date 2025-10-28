# Simple Port 3000 Killer - Shows exactly what it's doing
# Run as Administrator

Write-Host "`n=== KILL PORT 3000 ===" -ForegroundColor Cyan

# Method 1: Find and kill by port
Write-Host "`n[Method 1] Finding process on port 3000..." -ForegroundColor Yellow
$netstat = netstat -ano | Select-String ":3000" | Select-String "LISTENING"

if ($netstat) {
    Write-Host "Raw netstat output:" -ForegroundColor Gray
    Write-Host "$netstat" -ForegroundColor White

    $netstat | ForEach-Object {
        $line = $_.ToString()
        Write-Host "`nParsing: $line" -ForegroundColor Gray

        # Split and get last element (PID)
        $parts = $line -split '\s+'
        $pid = $parts[-1]

        Write-Host "Extracted PID: '$pid'" -ForegroundColor Yellow

        if ($pid -match '^\d+$') {
            Write-Host "PID is numeric, attempting kill..." -ForegroundColor Yellow
            try {
                $proc = Get-Process -Id $pid -ErrorAction Stop
                Write-Host "Found process: $($proc.ProcessName) (PID $pid)" -ForegroundColor Cyan

                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "✓ SUCCESS: Killed PID $pid" -ForegroundColor Green
            } catch {
                Write-Host "✗ FAILED: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "✗ PID not numeric: '$pid'" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No process found on port 3000" -ForegroundColor Green
}

# Method 2: Kill all Node processes (nuclear option)
Write-Host "`n[Method 2] Killing all Node.js processes..." -ForegroundColor Yellow
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue

if ($nodeProcs) {
    Write-Host "Found $($nodeProcs.Count) Node.js process(es):" -ForegroundColor Cyan
    $nodeProcs | ForEach-Object {
        Write-Host "  - PID $($_.Id): $($_.ProcessName)" -ForegroundColor Gray
    }

    try {
        Stop-Process -Name node -Force -ErrorAction Stop
        Write-Host "✓ SUCCESS: Killed all Node.js processes" -ForegroundColor Green
    } catch {
        Write-Host "✗ FAILED: $_" -ForegroundColor Red
    }
} else {
    Write-Host "No Node.js processes found" -ForegroundColor Gray
}

# Verify
Start-Sleep -Seconds 1
Write-Host "`n[Verification] Checking port 3000..." -ForegroundColor Yellow
$check = netstat -ano | Select-String ":3000" | Select-String "LISTENING"

if ($check) {
    Write-Host "✗ FAILED: Port 3000 still in use!" -ForegroundColor Red
    Write-Host "$check" -ForegroundColor White
    Write-Host "`nYou may need to restart the machine." -ForegroundColor Yellow
} else {
    Write-Host "✓ SUCCESS: Port 3000 is free!" -ForegroundColor Green
}
