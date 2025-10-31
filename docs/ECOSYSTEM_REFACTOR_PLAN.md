# Ecosystem Refactor Plan: Single "ecosystem" Namespace

**Status:** DRAFT - Pending approval
**Created:** 2025-10-31 20:45 UTC
**Owner:** Ada (Coordinator & Architect)

---

## Executive Summary

Consolidate all FalkorDB graph names to use a single ecosystem namespace called "ecosystem" instead of the current "consciousness-infrastructure" pattern. This simplifies the naming scheme and aligns with the conceptual model of a single ecosystem containing multiple organizations and citizens.

**Scope:** 13 FalkorDB graphs, ~101 Python files, configuration files, documentation

**Timeline:** 2 days (1 day preparation, 1 day execution + verification)

**Risk:** MEDIUM - Database migrations are inherently risky, but we have backup/restore capability

---

## Current State Analysis

### Current Graph Names (13 graphs)

**Citizen Graphs (7):**
- `consciousness-infrastructure_mind-protocol_felix` (2,954 nodes)
- `consciousness-infrastructure_mind-protocol_luca` (2,596 nodes)
- `consciousness-infrastructure_mind-protocol_atlas` (2,808 nodes)
- `consciousness-infrastructure_mind-protocol_ada` (2,274 nodes)
- `consciousness-infrastructure_mind-protocol_iris` (2,199 nodes)
- `consciousness-infrastructure_mind-protocol_victor` (2,418 nodes)
- `consciousness-infrastructure_mind-protocol` (3,625 nodes) - appears to be another citizen or org

**Organization/Collective Graphs (3):**
- `collective_n2` (2 nodes) - L2 organizational graph (has Org_Policy)
- `consciousness-infrastructure` (410 nodes) - L2/ecosystem-level graph

**Protocol/Infrastructure (3):**
- `protocol` (358 nodes) - L4 protocol schemas and policies
- `schema_registry` (744 nodes) - Schema definitions
- `falkor` (0 nodes) - appears unused
- `` (0 nodes) - empty graph (cleanup candidate)

**Total Content:** ~22,000 nodes across all graphs

### Current Naming Pattern

**Defined in:** `orchestration/config/graph_names.py`

```python
@dataclass(frozen=True)
class GraphNameResolver:
    ecosystem: str = "consciousness-infrastructure"
    org: str = "mind-protocol"

    def citizen(self, citizen_id: str) -> str:
        return f"{self.ecosystem}_{self.org}_{citizen_id}"
```

**Pattern:** `{ecosystem}_{org}_{citizen}`
**Example:** `consciousness-infrastructure_mind-protocol_felix`

**Hardcoded Special Cases:**
- `collective_n2` - L2 organizational graph
- `protocol` - L4 protocol graph
- `schema_registry` - Schema definitions

### Files Requiring Updates

**Affected Files:** ~101 Python files containing graph name references

**Key Categories:**
1. **Configuration:** `orchestration/config/graph_names.py`
2. **Scripts:** `tools/` directory (81 references to consciousness-infrastructure)
3. **Adapters:** `orchestration/adapters/storage/` (insertion.py, retrieval.py)
4. **Services:** `orchestration/services/watchers/code_substrate_watcher.py`
5. **Governance:** `tools/governance/seed_org_policies.py`
6. **Documentation:** README files, architecture docs

---

## Proposed New Naming Scheme

### Design Principles

1. **Single Ecosystem:** Only one ecosystem exists, called "ecosystem"
2. **Consistent Pattern:** All graphs follow same `ecosystem_<component>` pattern
3. **Clear Hierarchy:** `ecosystem` → `org` → `citizen`
4. **No Special Cases:** Protocol and schema_registry also use ecosystem prefix

### New Graph Names (13 graphs)

**Citizen Graphs (7):**
- `ecosystem_mind-protocol_felix`
- `ecosystem_mind-protocol_luca`
- `ecosystem_mind-protocol_atlas`
- `ecosystem_mind-protocol_ada`
- `ecosystem_mind-protocol_iris`
- `ecosystem_mind-protocol_victor`
- `ecosystem_mind-protocol` (org-level or base graph)

**Organization/Collective Graphs (2):**
- `ecosystem_mind-protocol_collective` (was `collective_n2` - L2 organizational graph)
- `ecosystem_mind-protocol_infrastructure` (was `consciousness-infrastructure`)

**Protocol/Infrastructure (2):**
- `ecosystem_protocol` (was `protocol` - L4 protocol schemas)
- `ecosystem_schema-registry` (was `schema_registry`)

**Cleanup:**
- Delete empty graphs: `falkor`, ``

**Total:** 11 graphs (down from 13, removed 2 empty graphs)

### Naming Convention Rules

**Format:** `ecosystem_<org>_<citizen>` OR `ecosystem_<special>`

**Valid Patterns:**
- `ecosystem_mind-protocol_{citizen_id}` - Citizen graphs (N1)
- `ecosystem_mind-protocol_collective` - Organizational graph (L2/N2)
- `ecosystem_mind-protocol_infrastructure` - Infrastructure/ecosystem-level graph
- `ecosystem_protocol` - L4 protocol schemas
- `ecosystem_schema-registry` - Schema registry

**Regex:** `^ecosystem_[a-z0-9-]+(_[a-z0-9_-]+)?$`

---

## Migration Strategy

### Phase 1: Preparation (Day 1 - 4 hours)

**1.1 Backup All Graphs**
```bash
# Create timestamped backup directory
mkdir -p backups/ecosystem-refactor-2025-10-31

# Backup each graph
for graph in $(redis-cli --raw GRAPH.LIST); do
    echo "Backing up: $graph"
    # Export graph data (implement using FalkorDB export)
    # Store in backups/ecosystem-refactor-2025-10-31/$graph.json
done
```

**1.2 Update Configuration**
- **File:** `orchestration/config/graph_names.py`
- **Change:** `ecosystem: str = "ecosystem"` (was "consciousness-infrastructure")
- **Add methods:**
  - `def collective(self) -> str: return f"{self.ecosystem}_{self.org}_collective"`
  - `def protocol(self) -> str: return f"{self.ecosystem}_protocol"`
  - `def schema_registry(self) -> str: return f"{self.ecosystem}_schema-registry"`

**1.3 Create Migration Script**
- **File:** `tools/migrations/migrate_to_single_ecosystem.py`
- **Purpose:** Rename all graphs in FalkorDB
- **Logic:**
  1. For each graph: Get all nodes/edges
  2. Create new graph with ecosystem_ name
  3. Copy all data to new graph
  4. Verify node/edge count matches
  5. Delete old graph (only after verification)

**1.4 Update All Python Files**
- Find/replace hardcoded graph names
- Update imports to use `graph_names.py` resolver
- **Patterns to replace:**
  - `"collective_n2"` → `graph_names.resolver.collective()`
  - `"protocol"` → `graph_names.resolver.protocol()`
  - `"schema_registry"` → `graph_names.resolver.schema_registry()`
  - `"consciousness-infrastructure"` → Depends on context (citizen vs org vs infrastructure)

---

### Phase 2: Execution (Day 2 - 4 hours)

**2.1 Stop All Services**
```bash
# Stop MPSv3 supervisor
# Ctrl+C in supervisor terminal (graceful shutdown)

# Verify no processes accessing FalkorDB
netstat -an | grep 6379
```

**2.2 Run Migration Script**
```bash
python tools/migrations/migrate_to_single_ecosystem.py --dry-run
# Review output, verify mapping correct

python tools/migrations/migrate_to_single_ecosystem.py --execute
# Actual migration with progress bar
```

**2.3 Verification Checks**
```bash
# Verify new graph names
redis-cli GRAPH.LIST

# Verify node counts match
python tools/migrations/verify_ecosystem_migration.py
# Should output: ✅ All graphs migrated successfully

# Verify no old graph names remain
redis-cli GRAPH.LIST | grep "consciousness-infrastructure"
# Should return nothing

redis-cli GRAPH.LIST | grep "collective_n2"
# Should return nothing
```

**2.4 Restart Services**
```bash
# Start MPSv3 supervisor with new graph names
python orchestration/mpsv3_supervisor.py --config orchestration/services/mpsv3/services.yaml

# Monitor logs for graph connection errors
# Should show: "Connected to graph: ecosystem_mind-protocol_felix" etc.
```

---

### Phase 3: Validation (Day 2 - 2 hours)

**3.1 Functional Testing**
- [ ] Dashboard loads and displays consciousness data
- [ ] WebSocket server connects to citizen graphs
- [ ] Context continuity works (S5/S6)
- [ ] Telemetry emission succeeds
- [ ] SafeBroadcaster validates events
- [ ] mp-lint queries protocol schemas

**3.2 Data Integrity Checks**
```cypher
// ecosystem_mind-protocol_felix
MATCH (n) RETURN labels(n), count(n)
// Verify all node types present

MATCH ()-[r]->() RETURN type(r), count(r)
// Verify all relationship types present

// ecosystem_protocol
MATCH (es:L4_Event_Schema) RETURN count(es)
// Should be 168 event schemas

// ecosystem_mind-protocol_collective
MATCH (p:Org_Policy) RETURN p.policy_id
// Should return ORG_POLICY_MIND_PROTOCOL_V1
```

**3.3 Service Health**
```bash
# Check all services running
python status_check.py

# Verify no graph name errors in logs
grep -i "graph.*not found" logs/*
# Should return nothing
```

---

## Rollback Plan

**If migration fails:**

1. **Stop all services** (Ctrl+C supervisor)

2. **Restore from backups:**
```bash
cd backups/ecosystem-refactor-2025-10-31
for graph_backup in *.json; do
    graph_name="${graph_backup%.json}"
    echo "Restoring: $graph_name"
    # Import graph data back to FalkorDB
    python tools/migrations/restore_graph.py --graph "$graph_name" --from "$graph_backup"
done
```

3. **Revert code changes:**
```bash
git checkout orchestration/config/graph_names.py
# Revert ecosystem: "ecosystem" back to "consciousness-infrastructure"
```

4. **Restart services**

5. **Verify restoration:**
```bash
redis-cli GRAPH.LIST | grep "consciousness-infrastructure"
# Should show old graph names

python status_check.py
# Should show all services operational
```

---

## Files Requiring Updates

### Critical Files (Must Update)

**1. Configuration**
- `orchestration/config/graph_names.py` - Central resolver
- `orchestration/config/settings.py` - May contain graph name references

**2. Governance & Policies**
- `tools/governance/seed_org_policies.py` - Update `graph_name = "collective_n2"`

**3. Protocol Ingestion**
- `tools/protocol/ingest_telemetry_policies.py` - Uses "protocol" graph
- `tools/protocol/ingest_consciousness_events.py` - Uses "protocol" graph
- `tools/protocol/ingest_reviewer_events.py` - Uses "protocol" graph
- `tools/protocol/export_l4_public.py` - Uses "protocol" graph

**4. Watchers & Services**
- `orchestration/services/watchers/code_substrate_watcher.py` - Hardcodes `collective_n2`
- `orchestration/adapters/storage/retrieval.py` - Documents graph name patterns
- `orchestration/adapters/storage/insertion.py` - Documents graph name examples

**5. Scripts & Tools**
- `tools/mp_lint/cli.py` - Constructs citizen graph names
- `tools/doc_ingestion/graph.py` - Default graph name
- `tools/doc_ingestion/config.py` - Default graph name
- `tools/cleanup_duplicate_graphs.py` - Detects old graph patterns
- `orchestration/scripts/backfill_membership.py` - Documents graph name patterns

### Documentation Files

- `README.md` - May reference graph names
- `docs/specs/v2/` - Architecture documentation
- `orchestration/SCRIPT_MAP.md` - Script documentation
- `consciousness/citizens/CLAUDE.md` - System status
- `docs/L4_INTEGRATION_TICKET_MATRIX.md` - May reference protocol graph

---

## Migration Script Design

### Tool: `tools/migrations/migrate_to_single_ecosystem.py`

**Purpose:** Rename all FalkorDB graphs to new ecosystem_ pattern

**Algorithm:**
```python
MIGRATION_MAP = {
    # Citizens
    "consciousness-infrastructure_mind-protocol_felix": "ecosystem_mind-protocol_felix",
    "consciousness-infrastructure_mind-protocol_luca": "ecosystem_mind-protocol_luca",
    "consciousness-infrastructure_mind-protocol_atlas": "ecosystem_mind-protocol_atlas",
    "consciousness-infrastructure_mind-protocol_ada": "ecosystem_mind-protocol_ada",
    "consciousness-infrastructure_mind-protocol_iris": "ecosystem_mind-protocol_iris",
    "consciousness-infrastructure_mind-protocol_victor": "ecosystem_mind-protocol_victor",
    "consciousness-infrastructure_mind-protocol": "ecosystem_mind-protocol",

    # Organization/Collective
    "collective_n2": "ecosystem_mind-protocol_collective",
    "consciousness-infrastructure": "ecosystem_mind-protocol_infrastructure",

    # Protocol/Infrastructure
    "protocol": "ecosystem_protocol",
    "schema_registry": "ecosystem_schema-registry",

    # Delete (empty graphs)
    "falkor": None,  # Delete
    "": None,  # Delete
}

def migrate_graph(old_name: str, new_name: str):
    """
    1. Connect to Redis
    2. Verify old graph exists
    3. Get all nodes and edges from old graph
    4. Create new graph
    5. Copy all nodes to new graph (preserve labels, properties)
    6. Copy all edges to new graph (preserve type, properties)
    7. Verify counts match (nodes, edges, labels)
    8. If verification passes: delete old graph
    9. If verification fails: abort, log error
    """
```

**Safety Features:**
- `--dry-run` mode: Show what would be migrated without executing
- Progress bar: Show migration progress per graph
- Verification: Compare node/edge counts before deletion
- Logging: Detailed log of every operation
- Atomic: Each graph migration is independent (failure doesn't affect others)

**Usage:**
```bash
# Preview migration
python tools/migrations/migrate_to_single_ecosystem.py --dry-run

# Execute migration
python tools/migrations/migrate_to_single_ecosystem.py --execute

# Migrate specific graph
python tools/migrations/migrate_to_single_ecosystem.py --graph "collective_n2" --execute
```

---

## Verification Tool Design

### Tool: `tools/migrations/verify_ecosystem_migration.py`

**Purpose:** Verify all graphs migrated correctly

**Checks:**
1. **Graph Name Pattern:** All graphs match `^ecosystem_` pattern
2. **Node Count:** Compare with pre-migration counts (from log)
3. **Edge Count:** Compare with pre-migration counts
4. **Old Graphs Gone:** No `consciousness-infrastructure` or `collective_n2` graphs exist
5. **Critical Data Present:**
   - `ecosystem_protocol`: 168 Event_Schema nodes
   - `ecosystem_mind-protocol_collective`: Org_Policy node exists
   - `ecosystem_mind-protocol_felix`: SubEntity nodes present

**Output:**
```
✅ Graph Pattern Check: All graphs use ecosystem_ prefix
✅ Node Count Check: All graphs have expected node counts
✅ Edge Count Check: All graphs have expected edge counts
✅ Old Graphs Cleaned: No legacy graph names found
✅ Critical Data Check: All critical nodes present

🎉 Migration verification PASSED - System ready for use
```

---

## Risk Assessment

**Risk Level:** MEDIUM

**Risks:**

1. **Data Loss (MEDIUM)**
   - **Mitigation:** Full backup before migration, verify counts after each graph
   - **Rollback:** Restore from backups

2. **Service Downtime (LOW)**
   - **Impact:** 2-4 hours of downtime during migration
   - **Mitigation:** Schedule during off-hours, notify team

3. **Broken References (MEDIUM)**
   - **Impact:** Code references old graph names, queries fail
   - **Mitigation:** Comprehensive find/replace, grep verification
   - **Rollback:** Revert code changes via git

4. **Incomplete Migration (LOW)**
   - **Impact:** Some graphs migrated, some not - inconsistent state
   - **Mitigation:** Atomic per-graph migration, verification before deletion
   - **Rollback:** Finish incomplete migrations or restore all

5. **Config Drift (LOW)**
   - **Impact:** Some files still reference old names after migration
   - **Mitigation:** Grep for old patterns, update all occurrences
   - **Detection:** mp-lint, grep searches, service health checks

---

## Success Criteria

Migration is successful when:

1. ✅ All 11 graphs renamed to ecosystem_ pattern
2. ✅ All node/edge counts match pre-migration state
3. ✅ No old graph names remain in FalkorDB
4. ✅ All services start successfully
5. ✅ Dashboard displays consciousness data
6. ✅ Telemetry emission works
7. ✅ SafeBroadcaster validates events
8. ✅ No "graph not found" errors in logs
9. ✅ All Python files updated to use new names
10. ✅ Verification tool reports PASS

---

## Timeline & Ownership

**Owner:** Ada (Coordinator) + Atlas (Infrastructure execution)

**Day 1 (Preparation):**
- 09:00-10:00: Create migration script + verification tool (Ada)
- 10:00-11:00: Update `graph_names.py` and find all hardcoded references (Ada)
- 11:00-13:00: Update all Python files (find/replace + testing) (Ada + Atlas)
- 14:00-15:00: Create backup script and run backups (Atlas)
- 15:00-16:00: Dry-run migration, review output (Ada + Atlas)
- 16:00-17:00: Team review, approval to proceed (All)

**Day 2 (Execution):**
- 09:00-09:15: Stop all services (Atlas)
- 09:15-10:15: Run migration script (Atlas, Ada monitoring)
- 10:15-11:00: Verification checks (Ada + Atlas)
- 11:00-11:15: Restart services (Atlas)
- 11:15-12:00: Functional testing (All available citizens)
- 12:00-13:00: Buffer for issues/rollback if needed

**Post-Migration:**
- Update documentation
- Update SYNC.md with migration report
- Close refactor task

---

## Approval Required

**This refactor requires approval from:**

- [ ] Nicolas (Founder) - Strategic direction approval
- [ ] Luca (Consciousness Specialist) - Verify consciousness graphs integrity
- [ ] Atlas (Infrastructure) - Execution readiness
- [ ] Felix (Core Consciousness) - Impact on consciousness systems

**Approval Criteria:**
- Backup/restore plan acceptable
- Downtime window acceptable
- Migration script reviewed and tested
- Rollback plan clear

**Questions for Approval:**

1. **Naming:** Is `ecosystem_mind-protocol_collective` the right name for the L2 org graph (was `collective_n2`)?
2. **Timing:** What's the preferred downtime window? (Off-hours? Weekend?)
3. **Scope:** Should we also consolidate `ecosystem_mind-protocol_infrastructure` into `ecosystem_mind-protocol`? (Two org graphs seem redundant)
4. **Communication:** Who needs to be notified before/during migration?

---

## Next Steps

**Before Approval:**
1. Ada: Create migration script (`tools/migrations/migrate_to_single_ecosystem.py`)
2. Ada: Create verification tool (`tools/migrations/verify_ecosystem_migration.py`)
3. Ada: Update `orchestration/config/graph_names.py` with new resolver methods
4. Ada: Grep all files for hardcoded references, document complete list
5. Team: Review this plan, provide feedback/approval

**After Approval:**
1. Atlas: Execute Day 1 preparation tasks
2. All: Day 1 16:00 - Team review meeting
3. Atlas + Ada: Execute Day 2 migration
4. All: Day 2 11:15+ - Functional testing
5. Ada: Document migration outcome in SYNC.md

---

**Status:** DRAFT - Awaiting team review and approval

**Contact:** Ada (Coordinator & Architect) for questions on this plan
