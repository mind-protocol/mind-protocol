# Complete Mind Protocol Backup
# Backs up: FalkorDB, citizen contexts, configs, and system state

$BackupRoot = "C:\mind-protocol-backups"
$DateStamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupDir = "$BackupRoot\full_$DateStamp"

Write-Host "`n=== Mind Protocol Full Backup ===" -ForegroundColor Cyan
Write-Host "Timestamp: $DateStamp" -ForegroundColor Gray
Write-Host "Destination: $BackupDir`n" -ForegroundColor Gray

# Create backup directory structure
New-Item -ItemType Directory -Path "$BackupDir\falkordb" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\consciousness" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\logs" -Force | Out-Null

# 1. Backup FalkorDB
Write-Host "[1/5] Backing up FalkorDB..." -ForegroundColor Yellow
wsl sudo docker exec mind_protocol_falkordb redis-cli SAVE 2>&1 | Out-Null
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/dump.rdb /mnt/c/mind-protocol-backups/full_$DateStamp/falkordb/dump.rdb 2>&1 | Out-Null
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/appendonly.aof /mnt/c/mind-protocol-backups/full_$DateStamp/falkordb/appendonly.aof 2>&1 | Out-Null

$DBSize = [math]::Round((Get-Item "$BackupDir\falkordb\dump.rdb").Length / 1MB, 2)
Write-Host "      ✓ FalkorDB: $DBSize MB" -ForegroundColor Green

# 2. Backup citizen contexts
Write-Host "[2/5] Backing up citizen contexts..." -ForegroundColor Yellow
Copy-Item -Path "C:\Users\reyno\mind-protocol\consciousness\citizens" -Destination "$BackupDir\consciousness\citizens" -Recurse -Force
$CitizenCount = (Get-ChildItem "$BackupDir\consciousness\citizens" -Directory).Count
Write-Host "      ✓ Citizens: $CitizenCount directories" -ForegroundColor Green

# 3. Backup configurations
Write-Host "[3/5] Backing up configurations..." -ForegroundColor Yellow
Copy-Item -Path "C:\Users\reyno\mind-protocol\.env" -Destination "$BackupDir\config\.env" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "C:\Users\reyno\mind-protocol\orchestration\services\mpsv3\services.yaml" -Destination "$BackupDir\config\services.yaml" -Force
Copy-Item -Path "C:\Users\reyno\mind-protocol\docker-compose.yml" -Destination "$BackupDir\config\docker-compose.yml" -Force
Write-Host "      ✓ Config files backed up" -ForegroundColor Green

# 4. Backup critical queues/signals
Write-Host "[4/5] Backing up queues and signals..." -ForegroundColor Yellow
if (Test-Path "C:\Users\reyno\mind-protocol\.stimuli") {
    Copy-Item -Path "C:\Users\reyno\mind-protocol\.stimuli" -Destination "$BackupDir\stimuli" -Recurse -Force
}
if (Test-Path "C:\Users\reyno\mind-protocol\.signals") {
    Copy-Item -Path "C:\Users\reyno\mind-protocol\.signals" -Destination "$BackupDir\signals" -Recurse -Force
}
Write-Host "      ✓ Queues backed up" -ForegroundColor Green

# 5. Create manifest
Write-Host "[5/5] Creating backup manifest..." -ForegroundColor Yellow
$Manifest = @{
    timestamp = $DateStamp
    backup_type = "full"
    falkordb_size_mb = $DBSize
    citizen_count = $CitizenCount
    system_info = @{
        hostname = $env:COMPUTERNAME
        os = [System.Environment]::OSVersion.VersionString
        mindprotocol_path = "C:\Users\reyno\mind-protocol"
    }
}
$Manifest | ConvertTo-Json -Depth 4 | Out-File "$BackupDir\manifest.json" -Encoding UTF8
Write-Host "      ✓ Manifest created" -ForegroundColor Green

# Summary
Write-Host "`n=== Backup Complete ===" -ForegroundColor Green
Write-Host "Location: $BackupDir" -ForegroundColor White
Write-Host "Size: $([math]::Round((Get-ChildItem $BackupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)) MB" -ForegroundColor White

# Cleanup old full backups (keep last 5)
Write-Host "`n[Cleanup] Keeping last 5 full backups..." -ForegroundColor Yellow
Get-ChildItem $BackupRoot -Directory -Filter "full_*" | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 5 |
    ForEach-Object {
        Write-Host "      - Removing $($_.Name)" -ForegroundColor Gray
        Remove-Item $_.FullName -Recurse -Force
    }

Write-Host "`n✓ Done!`n" -ForegroundColor Green
