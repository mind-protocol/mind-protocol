# FalkorDB Restore Script
# Usage: .\restore_falkordb.ps1 -BackupDate "2025-10-26_1430"

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupDate
)

$BackupRoot = "C:\mind-protocol-backups"
$BackupDir = "$BackupRoot\$BackupDate"
$DumpFile = "$BackupDir\dump.rdb"

Write-Host "[Restore] Starting FalkorDB restore from $BackupDate..." -ForegroundColor Cyan

# Verify backup exists
if (-not (Test-Path $DumpFile)) {
    Write-Host "[Restore] ✗ Error: Backup not found at $DumpFile" -ForegroundColor Red
    Write-Host "[Restore] Available backups:" -ForegroundColor Yellow
    Get-ChildItem $BackupRoot -Directory | Select-Object Name
    exit 1
}

$SizeMB = [math]::Round((Get-Item $DumpFile).Length / 1MB, 2)
Write-Host "[Restore] Found backup: $SizeMB MB" -ForegroundColor Green

# Confirm
Write-Host "[Restore] WARNING: This will replace current FalkorDB data!" -ForegroundColor Red
Write-Host "[Restore] Press Ctrl+C to abort, or Enter to continue..." -ForegroundColor Yellow
Read-Host

# Stop FalkorDB container
Write-Host "[Restore] Stopping FalkorDB container..." -ForegroundColor Yellow
wsl sudo docker stop mind_protocol_falkordb

# Copy backup into container
Write-Host "[Restore] Copying backup file..." -ForegroundColor Yellow
wsl sudo docker cp /mnt/c/mind-protocol-backups/$BackupDate/dump.rdb mind_protocol_falkordb:/var/lib/falkordb/data/dump.rdb

# Fix permissions
Write-Host "[Restore] Fixing permissions..." -ForegroundColor Yellow
wsl sudo docker exec mind_protocol_falkordb chown redis:redis /var/lib/falkordb/data/dump.rdb

# Restart container
Write-Host "[Restore] Restarting FalkorDB..." -ForegroundColor Yellow
wsl sudo docker start mind_protocol_falkordb

# Wait for startup
Start-Sleep -Seconds 5

# Verify
Write-Host "[Restore] Verifying graphs..." -ForegroundColor Yellow
wsl sudo docker exec -it mind_protocol_falkordb redis-cli GRAPH.LIST

Write-Host "[Restore] ✓ Restore complete!" -ForegroundColor Green
