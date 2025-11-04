# Graph Migration: Simple Rename

Drop `consciousness-infrastructure_` prefix from all graph names.

## Changes

**Renames:**
- `consciousness-infrastructure_mind-protocol_felix` → `mind-protocol_felix`
- `consciousness-infrastructure_mind-protocol_luca` → `mind-protocol_luca`
- `consciousness-infrastructure_mind-protocol_atlas` → `mind-protocol_atlas`
- `consciousness-infrastructure_mind-protocol_ada` → `mind-protocol_ada`
- `consciousness-infrastructure_mind-protocol_iris` → `mind-protocol_iris`
- `consciousness-infrastructure_mind-protocol_victor` → `mind-protocol_victor`
- `consciousness-infrastructure_mind-protocol` → `mind-protocol`
- `collective_n2` → `mind-protocol_collective`

**Stays same:**
- `protocol` (L4 schemas)
- `schema_registry`

**Deletes:**
- `falkor` (empty)
- `` (empty)
- `consciousness-infrastructure` (false infrastructure)

## Run Migration

```bash
# Stop services first
# Ctrl+C in supervisor terminal

# Run migration
python tools/migrations/migrate_graphs_simple.py
# Type 'yes' to confirm

# Restart services
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml
```

## Code Changes

Already updated:
- ✅ `orchestration/config/graph_names.py` - Dropped ecosystem prefix
- ✅ `tools/governance/seed_org_policies.py` - Uses `mind-protocol_collective`
- ✅ `orchestration/services/watchers/code_substrate_watcher.py` - Uses `mind-protocol_collective`

## Verification

```bash
# Check new graph names
redis-cli GRAPH.LIST

# Should see:
# - mind-protocol_felix
# - mind-protocol_luca
# - mind-protocol_atlas
# - mind-protocol_ada
# - mind-protocol_iris
# - mind-protocol_victor
# - mind-protocol
# - mind-protocol_collective
# - protocol
# - schema_registry

# Should NOT see:
# - consciousness-infrastructure*
# - collective_n2
# - falkor
```

Done.
