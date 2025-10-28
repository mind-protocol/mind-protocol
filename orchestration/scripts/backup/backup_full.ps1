# Complete Mind Protocol Backup
# Location: orchestration/scripts/backup/backup_full.ps1
# Usage: .\orchestration\scripts\backup\backup_full.ps1
# Backs up: FalkorDB, citizen contexts, configs, queues, and system state

# Get project root
$ProjectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$BackupRoot = Join-Path $ProjectRoot "backups\full"
$DateStamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupDir = Join-Path $BackupRoot $DateStamp

Write-Host "`n=== Mind Protocol Full Backup ===" -ForegroundColor Cyan
Write-Host "Timestamp: $DateStamp" -ForegroundColor Gray
Write-Host "Project root: $ProjectRoot" -ForegroundColor Gray
Write-Host "Destination: $BackupDir`n" -ForegroundColor Gray

# Create backup directory structure
New-Item -ItemType Directory -Path "$BackupDir\falkordb" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\consciousness" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$BackupDir\queues" -Force | Out-Null

# 1. Backup FalkorDB
Write-Host "[1/5] Backing up FalkorDB..." -ForegroundColor Yellow
wsl sudo docker exec mind_protocol_falkordb redis-cli SAVE 2>&1 | Out-Null

$WslBackupPath = "$BackupDir\falkordb" -replace '\\', '/' -replace 'C:', '/mnt/c'
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/dump.rdb "$WslBackupPath/dump.rdb" 2>&1 | Out-Null
wsl sudo docker cp mind_protocol_falkordb:/var/lib/falkordb/data/appendonly.aof "$WslBackupPath/appendonly.aof" 2>&1 | Out-Null

$DBSize = [math]::Round((Get-Item "$BackupDir\falkordb\dump.rdb").Length / 1MB, 2)
$GraphsList = wsl sudo docker exec mind_protocol_falkordb redis-cli GRAPH.LIST
$GraphCount = ($GraphsList | Measure-Object).Count
Write-Host "      ✓ FalkorDB: $DBSize MB ($GraphCount graphs)" -ForegroundColor Green

# 2. Backup citizen contexts
Write-Host "[2/5] Backing up citizen contexts..." -ForegroundColor Yellow
$CitizensPath = Join-Path $ProjectRoot "consciousness\citizens"
if (Test-Path $CitizensPath) {
    Copy-Item -Path $CitizensPath -Destination "$BackupDir\consciousness\citizens" -Recurse -Force
    $CitizenCount = (Get-ChildItem "$BackupDir\consciousness\citizens" -Directory -ErrorAction SilentlyContinue).Count
    
    # Count context files
    $ContextCount = (Get-ChildItem "$BackupDir\consciousness\citizens" -Recurse -Filter "*.json" -ErrorAction SilentlyContinue).Count
    Write-Host "      ✓ Citizens: $CitizenCount directories, $ContextCount context files" -ForegroundColor Green
} else {
    Write-Host "      - No citizen contexts found" -ForegroundColor Gray
    $CitizenCount = 0
}

# 3. Backup configurations
Write-Host "[3/5] Backing up configurations..." -ForegroundColor Yellow
$ConfigFiles = @(
    @{src = ".env"; dest = "$BackupDir\config\.env"}
    @{src = "orchestration\services\mpsv3\services.yaml"; dest = "$BackupDir\config\services.yaml"}
    @{src = "docker-compose.yml"; dest = "$BackupDir\config\docker-compose.yml"}
)
$ConfigCount = 0
foreach ($file in $ConfigFiles) {
    $srcPath = Join-Path $ProjectRoot $file.src
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $file.dest -Force
        $ConfigCount++
    }
}
Write-Host "      ✓ Config files: $ConfigCount backed up" -ForegroundColor Green

# 4. Backup critical queues/signals
Write-Host "[4/5] Backing up queues and signals..." -ForegroundColor Yellow
$QueueItems = 0
if (Test-Path (Join-Path $ProjectRoot ".stimuli")) {
    Copy-Item -Path (Join-Path $ProjectRoot ".stimuli") -Destination "$BackupDir\queues\stimuli" -Recurse -Force
    $QueueItems += (Get-ChildItem "$BackupDir\queues\stimuli" -File -Recurse -ErrorAction SilentlyContinue).Count
}
if (Test-Path (Join-Path $ProjectRoot ".signals")) {
    Copy-Item -Path (Join-Path $ProjectRoot ".signals") -Destination "$BackupDir\queues\signals" -Recurse -Force
    $QueueItems += (Get-ChildItem "$BackupDir\queues\signals" -File -Recurse -ErrorAction SilentlyContinue).Count
}
Write-Host "      ✓ Queue items: $QueueItems files" -ForegroundColor Green

# 5. Create manifest
Write-Host "[5/5] Creating backup manifest..." -ForegroundColor Yellow
$Manifest = @{
    timestamp = $DateStamp
    backup_type = "full"
    project_root = $ProjectRoot
    falkordb = @{
        size_mb = $DBSize
        graph_count = $GraphCount
    }
    consciousness = @{
        citizen_count = $CitizenCount
        context_file_count = $ContextCount
    }
    config = @{
        files_backed_up = $ConfigCount
    }
    queues = @{
        items_backed_up = $QueueItems
    }
    system_info = @{
        hostname = $env:COMPUTERNAME
        os = [System.Environment]::OSVersion.VersionString
        powershell_version = $PSVersionTable.PSVersion.ToString()
    }
}
$Manifest | ConvertTo-Json -Depth 4 | Out-File "$BackupDir\manifest.json" -Encoding UTF8
Write-Host "      ✓ Manifest created" -ForegroundColor Green

# Summary
$TotalSize = [math]::Round((Get-ChildItem $BackupDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "`n=== Backup Complete ===" -ForegroundColor Green
Write-Host "Location: $BackupDir" -ForegroundColor White
Write-Host "Total size: $TotalSize MB" -ForegroundColor White
Write-Host "Graphs: $GraphCount" -ForegroundColor White
Write-Host "Citizens: $CitizenCount" -ForegroundColor White
Write-Host "Contexts: $ContextCount" -ForegroundColor White

# Cleanup old full backups (keep last 5)
Write-Host "`n[Cleanup] Keeping last 5 full backups..." -ForegroundColor Yellow
$Removed = 0
Get-ChildItem $BackupRoot -Directory | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 5 |
    ForEach-Object {
        Write-Host "      - Removing $($_.Name)" -ForegroundColor Gray
        Remove-Item $_.FullName -Recurse -Force
        $Removed++
    }
if ($Removed -eq 0) {
    Write-Host "      - No old backups to remove" -ForegroundColor Gray
}

Write-Host "`n✓ Done!`n" -ForegroundColor Green
