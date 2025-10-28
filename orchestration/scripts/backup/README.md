# Mind Protocol Backup System

Backup and restore scripts for Mind Protocol infrastructure.

## Quick Reference

### Backup Commands

```powershell
# From project root (C:\Users\reyno\mind-protocol)

# Quick FalkorDB backup (1-5 MB, ~10 seconds)
.\orchestration\scripts\backup\backup_falkordb.ps1

# Full system backup (includes contexts, configs, queues)
.\orchestration\scripts\backup\backup_full.ps1
```

### Restore Commands

```powershell
# Interactive restore (shows menu of available backups)
.\orchestration\scripts\backup\restore_falkordb.ps1

# Direct restore
.\orchestration\scripts\backup\restore_falkordb.ps1 -BackupDate "2025-10-26_1430"
```

## Backup Contents

### FalkorDB Backup (`backup_falkordb.ps1`)
- `dump.rdb` - Redis database snapshot with all graphs
- `appendonly.aof` - Append-only file (if exists)
- Stored in: `backups/falkordb/YYYY-MM-DD_HHmm/`
- Retention: 7 days (auto-cleanup)

### Full Backup (`backup_full.ps1`)
- FalkorDB data (dump.rdb, appendonly.aof)
- Citizen contexts from `consciousness/citizens/`
- Configuration files (.env, services.yaml, docker-compose.yml)
- Queues and signals (.stimuli/, .signals/)
- Backup manifest with metadata
- Stored in: `backups/full/YYYY-MM-DD_HHmm/`
- Retention: Last 5 backups (auto-cleanup)

## When to Backup

### Before Major Operations
- Schema migrations: `backup_falkordb.ps1`
- System updates: `backup_full.ps1`
- Production deployments: `backup_full.ps1`
- Testing destructive operations: `backup_full.ps1`

### Automated Schedule (Recommended)
- Daily: `backup_falkordb.ps1` at 2 AM
- Weekly: `backup_full.ps1` every Sunday at 3 AM
- Before launches: Manual `backup_full.ps1`

## Setting Up Automated Backups

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 2 AM)
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Users\reyno\mind-protocol\orchestration\scripts\backup\backup_falkordb.ps1"`
   - Start in: `C:\Users\reyno\mind-protocol`

## Backup Verification

Each backup includes verification:
- File size checks
- Graph count validation (FalkorDB)
- Manifest with metadata
- Automatic cleanup of old backups

## Restore Process

1. Stop Mind Protocol supervisor (Ctrl+C)
2. Run restore script
3. Script stops FalkorDB, copies data, restarts
4. Verification shows graphs loaded
5. Restart Mind Protocol supervisor

## Backup Locations

```
mind-protocol/
├── backups/
│   ├── falkordb/          # Quick FalkorDB backups
│   │   ├── 2025-10-26_1430/
│   │   │   ├── dump.rdb
│   │   │   └── appendonly.aof
│   │   └── ...
│   └── full/              # Complete system backups
│       ├── 2025-10-26_1500/
│       │   ├── falkordb/
│       │   ├── consciousness/
│       │   ├── config/
│       │   ├── queues/
│       │   └── manifest.json
│       └── ...
```

## Troubleshooting

### "No connection could be made"
FalkorDB container isn't running. Start it:
```powershell
wsl sudo docker start mind_protocol_falkordb
```

### "Backup not found"
Check available backups:
```powershell
Get-ChildItem .\backups\falkordb -Directory | Select-Object Name
```

### Restore shows 0 graphs
The backup may have been empty. Verify backup file size:
```powershell
Get-Item .\backups\falkordb\YYYY-MM-DD_HHmm\dump.rdb | Select Length
```

## Notes

- Backups are stored locally in the project directory
- For production: Copy backups to external storage
- WSL Docker container must be running for backups
- Restore requires stopping the FalkorDB container
- All scripts use relative paths from project root
