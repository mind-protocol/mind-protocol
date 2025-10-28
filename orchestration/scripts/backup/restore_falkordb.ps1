# FalkorDB Restore Script
# Location: orchestration/scripts/backup/restore_falkordb.ps1
# Usage: .\orchestration\scripts\backup\restore_falkordb.ps1 -BackupDate "2025-10-26_1430"

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupDate
)

# Get project root
$ProjectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$BackupRoot = Join-Path $ProjectRoot "backups\falkordb"

Write-Host "`n=== FalkorDB Restore ===" -ForegroundColor Cyan

# If no date provided, show available backups and prompt
if (-not $BackupDate) {
    Write-Host "`nAvailable backups:" -ForegroundColor Yellow
    $Backups = Get-ChildItem $BackupRoot -Directory | Sort-Object Name -Descending
    
    if ($Backups.Count -eq 0) {
        Write-Host "No backups found in $BackupRoot" -ForegroundColor Red
        exit 1
    }
    
    for ($i = 0; $i -lt $Backups.Count; $i++) {
        $Backup = $Backups[$i]
        $DumpFile = Join-Path $Backup.FullName "dump.rdb"
        if (Test-Path $DumpFile) {
            $SizeMB = [math]::Round((Get-Item $DumpFile).Length / 1MB, 2)
            Write-Host "  [$i] $($Backup.Name) - $SizeMB MB" -ForegroundColor White
        }
    }
    
    Write-Host "`nEnter number to restore, or Ctrl+C to cancel:" -ForegroundColor Yellow
    $Selection = Read-Host "Selection"
    
    if ($Selection -match '^\d+$' -and [int]$Selection -lt $Backups.Count) {
        $BackupDate = $Backups[[int]$Selection].Name
    } else {
        Write-Host "Invalid selection" -ForegroundColor Red
        exit 1
    }
}

$BackupDir = Join-Path $BackupRoot $BackupDate
$DumpFile = Join-Path $BackupDir "dump.rdb"

# Verify backup exists
if (-not (Test-Path $DumpFile)) {
    Write-Host "[Restore] ✗ Error: Backup not found at $DumpFile" -ForegroundColor Red
    exit 1
}

$SizeMB = [math]::Round((Get-Item $DumpFile).Length / 1MB, 2)
Write-Host "[Restore] Selected backup: $BackupDate ($SizeMB MB)" -ForegroundColor Green

# Confirm
Write-Host "`n[Restore] WARNING: This will replace current FalkorDB data!" -ForegroundColor Red
Write-Host "[Restore] Current graphs will be lost!" -ForegroundColor Red
Write-Host "[Restore] Press Ctrl+C to abort, or Enter to continue..." -ForegroundColor Yellow
Read-Host

# Stop FalkorDB container
Write-Host "[Restore] Stopping FalkorDB container..." -ForegroundColor Yellow
wsl sudo docker stop mind_protocol_falkordb | Out-Null

# Copy backup into container
Write-Host "[Restore] Copying backup file..." -ForegroundColor Yellow
$WslDumpPath = $DumpFile -replace '\\', '/' -replace 'C:', '/mnt/c'
wsl sudo docker cp "$WslDumpPath" mind_protocol_falkordb:/var/lib/falkordb/data/dump.rdb

# Fix permissions
Write-Host "[Restore] Fixing permissions..." -ForegroundColor Yellow
wsl sudo docker exec mind_protocol_falkordb chown redis:redis /var/lib/falkordb/data/dump.rdb 2>$null

# Restart container
Write-Host "[Restore] Restarting FalkorDB..." -ForegroundColor Yellow
wsl sudo docker start mind_protocol_falkordb | Out-Null

# Wait for startup
Write-Host "[Restore] Waiting for database to load..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify
Write-Host "[Restore] Verifying graphs..." -ForegroundColor Yellow
$Graphs = wsl sudo docker exec mind_protocol_falkordb redis-cli GRAPH.LIST
$GraphCount = ($Graphs | Measure-Object).Count

Write-Host "`n[Restore] ✓ Restore complete!" -ForegroundColor Green
Write-Host "[Restore] Graphs loaded: $GraphCount" -ForegroundColor Green
Write-Host "`n$Graphs" -ForegroundColor Gray
