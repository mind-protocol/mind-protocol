# FalkorDB Automated Backup Script
# Run this daily or before major operations

$BackupRoot = "C:\mind-protocol-backups"
$DateStamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupDir = "$BackupRoot\$DateStamp"

Write-Host "[Backup] Starting FalkorDB backup..." -ForegroundColor Cyan

# Create backup directory
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# Trigger Redis SAVE
Write-Host "[Backup] Triggering Redis SAVE..." -ForegroundColor Yellow
wsl sudo docker exec mind_protocol_falkordb redis-cli SAVE

# Copy dump.rdb
Write-Host "[Backup] Copying dump.rdb..." -ForegroundColor Yellow
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/dump.rdb /mnt/c/mind-protocol-backups/$DateStamp/dump.rdb

# Copy appendonly.aof if it exists
Write-Host "[Backup] Copying appendonly.aof (if exists)..." -ForegroundColor Yellow
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/appendonly.aof /mnt/c/mind-protocol-backups/$DateStamp/appendonly.aof 2>$null

# Verify backup
$DumpFile = Get-Item "$BackupDir\dump.rdb" -ErrorAction SilentlyContinue
if ($DumpFile) {
    $SizeMB = [math]::Round($DumpFile.Length / 1MB, 2)
    Write-Host "[Backup] ✓ Success: $BackupDir" -ForegroundColor Green
    Write-Host "[Backup]   - dump.rdb: $SizeMB MB" -ForegroundColor Green
} else {
    Write-Host "[Backup] ✗ Failed: dump.rdb not found" -ForegroundColor Red
    exit 1
}

# Cleanup old backups (keep last 7 days)
Write-Host "[Backup] Cleaning up backups older than 7 days..." -ForegroundColor Yellow
Get-ChildItem $BackupRoot -Directory | 
    Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-7) } |
    ForEach-Object {
        Write-Host "[Backup]   - Removing $($_.Name)" -ForegroundColor Gray
        Remove-Item $_.FullName -Recurse -Force
    }

Write-Host "[Backup] Complete!" -ForegroundColor Green
