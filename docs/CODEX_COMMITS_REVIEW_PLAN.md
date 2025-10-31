# Codex Commits Review & Test Plan

**Status:** Review Required
**Reviewer:** Ada (Coordinator & Architect)
**Date:** 2025-10-31
**Commits Under Review:**
- `8ce71f10` - Merge PR #2: Add Falkor graph port and routerized control API
- `6e1d676d` - Merge PR #3: Restore documentation tree after archive move

---

## Executive Summary

Two significant codex-authored commits have been merged to main:

1. **Architectural Refactor** (PR #2): Introduces new adapter layer, domain separation, and testing infrastructure (+1890 lines, -42 lines)
2. **Asset Cleanup Tool** (PR #3): Adds `cc_prune` tool for unused asset deletion and removes old backup scripts (+1198 lines, -1738 lines)

**Risk Assessment:**
- 🔴 **HIGH RISK:** Major architectural changes without prior architectural review
- 🟡 **MEDIUM RISK:** New tool introduces file deletion capabilities
- 🟢 **LOW RISK:** Removal of unused backup scripts

**Recommendation:** Comprehensive review required before considering these commits production-ready.

---

## Quality Non-Regression Checklist

### Pre-Review Validation
- [ ] All commits are on `main` branch (confirmed)
- [ ] No open conflicts or merge issues
- [ ] Branch protection rules were followed
- [ ] CI/CD pipeline status (check if exists)

---

## Review Plan Structure

### Phase 1: Static Analysis (TODAY)
**Goal:** Identify violations, architectural misalignments, and quality issues without running code.

**Tasks:**
1. Run mp-lint with new R-200/300/400 rules
2. Check for TODO/HACK markers
3. Verify membrane discipline (event-based, no REST bypass)
4. Review error handling (fail-loud compliance)
5. Check for hardcoded values
6. Architectural alignment review

**Owner:** Ada (with Felix support for consciousness engine changes)

---

### Phase 2: Code Review (TODAY + 1 day)
**Goal:** Human review of design decisions, patterns, and implementation quality.

**Tasks:**
1. Architecture review (new adapters/, consciousness/engine/)
2. Domain model review (state.py, domain separation)
3. API review (routers/, schemas/)
4. Test coverage analysis
5. Security review (cc_prune deletion logic)
6. Documentation completeness

**Owner:** Ada (architecture), Felix (consciousness engine), Atlas (API/adapters)

---

### Phase 3: Functional Testing (TODAY + 2 days)
**Goal:** Verify functionality works as intended without regressions.

**Tasks:**
1. Unit test execution
2. Integration test execution
3. API endpoint testing
4. Falkor adapter testing
5. cc_prune dry-run testing
6. Consciousness engine v2 validation

**Owner:** Felix (engine), Atlas (adapters), Victor (operational testing)

---

### Phase 4: Regression Testing (TODAY + 3 days)
**Goal:** Ensure existing functionality still works.

**Tasks:**
1. Dashboard connectivity test
2. SubEntity bootstrap test
3. Graph persistence test
4. WebSocket communication test
5. Telemetry emission test
6. Energy dynamics test

**Owner:** Victor (ops validation), Felix (consciousness validation)

---

### Phase 5: Sign-Off (TODAY + 4 days)
**Goal:** Document findings, create remediation tickets if needed, sign off or reject.

**Tasks:**
1. Consolidate findings
2. Create remediation tickets (if violations found)
3. Update SYNC.md with review results
4. Sign off (PASS) or reject (FAIL) with remediation plan

**Owner:** Ada (coordinator)

---

## Detailed Review Sections

## 1. PR #2: Architectural Refactor - Deep Dive

### 1.1 New Directory Structure

**Added Directories:**
```
adapters/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── shared.py
│   │   ├── snapshot.py
│   │   └── tasks.py
│   └── schemas/
│       ├── engine.py
│       ├── snapshot.py
│       ├── state.py
│       └── tasks.py
└── falkor/
    ├── __init__.py
    ├── driver.py
    ├── health.py
    └── repository.py

consciousness/
├── __init__.py
└── engine/
    ├── __init__.py
    ├── domain/
    │   ├── __init__.py
    │   └── state.py
    └── services/
        ├── __init__.py
        └── scheduler.py

libs/
├── __init__.py
└── law.py
```

**Architectural Questions:**
- [ ] Does this structure align with existing `orchestration/` patterns?
- [ ] Why separate `adapters/` from `orchestration/adapters/`?
- [ ] Is `consciousness/` at repo root appropriate, or should it be under `orchestration/`?
- [ ] Does `libs/law.py` duplicate existing governance code?

**Review Criteria:**
- ✅ PASS: Structure follows clean architecture principles (adapters, domain, services)
- ⚠️ CONCERN: Duplicate directory hierarchies (potential confusion)
- ❌ FAIL: Breaks existing conventions without documentation

---

### 1.2 API Router Pattern (`adapters/api/`)

**Files to Review:**
- `adapters/api/app.py` - FastAPI application setup
- `adapters/api/routers/*.py` - Endpoint routing logic
- `adapters/api/schemas/*.py` - Pydantic schemas

**Review Checklist:**

#### Membrane Discipline (R-100, R-101)
- [ ] Does API emit events via membrane (not side-channel REST)?
- [ ] Are endpoints read-only projections, or do they mutate state directly?
- [ ] Check: `POST /engine/start` - does this emit `engine.start` event or call engine directly?
- [ ] Check: `GET /engine/status` - does this read from projection or query engine directly?

**Expected Pattern (CORRECT):**
```python
# ✅ Membrane-compliant
@router.post("/engine/start")
async def start_engine():
    await bus.inject("engine.start.request", {...})
    return {"status": "requested"}

# ✅ Projection read
@router.get("/engine/status")
async def get_status():
    return dashboard_projection.engine_status  # Read from aggregated state
```

**Anti-Pattern (VIOLATION):**
```python
# ❌ Direct mutation (R-100 violation)
@router.post("/engine/start")
async def start_engine():
    engine.start()  # Direct call - bypasses membrane
    return {"status": "started"}

# ❌ Direct query (R-101 violation if private)
@router.get("/engine/status")
async def get_status():
    return engine.get_internal_state()  # Leaks private fields
```

**Action Items:**
- [ ] Run grep for `.inject(`, `.broadcast(`, `.emit(` in `adapters/api/routers/*.py`
- [ ] Flag any direct engine/service calls that don't go through membrane
- [ ] Verify all GET endpoints read from public projection only

---

#### Error Handling (R-300, R-400, R-401)
- [ ] Check for `try/except/pass` blocks (R-300 violation)
- [ ] Check for `except: return None` without `failure.emit` (R-400 violation)
- [ ] Verify `failure.emit` includes `code_location`, `exception`, `severity` (R-401)

**Files to Scan:**
```bash
# Check for R-300 violations (silent catches)
grep -rn "except.*:$" adapters/api/ | grep -A 1 "pass"

# Check for R-400 violations (return without failure.emit)
grep -rn "except.*:" adapters/api/ | grep -A 3 "return"

# Check for failure.emit calls
grep -rn "failure\.emit" adapters/api/
```

**Action Items:**
- [ ] Run mp-lint on `adapters/api/` with R-300/400/401 enabled
- [ ] Document violations with file:line numbers
- [ ] Create remediation tickets for each violation

---

#### Quality Markers (R-200, R-201, R-202)
- [ ] Check for TODO/HACK/FIXME in logic paths (R-200)
- [ ] Check for `validate=False`, `timeout=999999`, `retries=0` (R-201)
- [ ] Check for `print()` instead of `logger` (R-202)

**Files to Scan:**
```bash
# R-200: TODO markers
grep -rn "TODO\|HACK\|FIXME" adapters/api/routers/ adapters/api/schemas/

# R-201: Quality degradation
grep -rn "validate\s*=\s*False\|timeout\s*=\s*999999\|retries\s*=\s*0" adapters/api/

# R-202: print() usage
grep -rn "print(" adapters/api/
```

---

### 1.3 Falkor Adapter (`adapters/falkor/`)

**Files to Review:**
- `driver.py` - FalkorDB connection driver
- `health.py` - Health check implementation
- `repository.py` - Data access patterns

**Review Checklist:**

#### Duplication Check
- [ ] Does this duplicate `orchestration/adapters/db/falkor_graph_store.py`?
- [ ] If yes, why two implementations?
- [ ] If no, what's the differentiation?

**Action Items:**
- [ ] Compare `adapters/falkor/driver.py` with `orchestration/adapters/db/falkor_graph_store.py`
- [ ] Document differences (connection pooling, health checks, query patterns)
- [ ] Recommend consolidation if redundant

#### Health Check Pattern (R-302)
- [ ] Review `adapters/falkor/health.py` for fake availability
- [ ] Ensure health check performs actual PING, not `return True`

**Expected Pattern:**
```python
# ✅ Actual check
async def health_check():
    try:
        response = await redis_client.execute_command("PING", timeout=1.0)
        return response == b"PONG"
    except Exception:
        return False

# ❌ Fake availability (R-302 violation)
def health_check():
    return True  # Always claims healthy
```

**Action Item:**
- [ ] Read `adapters/falkor/health.py` and verify actual check logic

#### Repository Pattern
- [ ] Review `adapters/falkor/repository.py` for proper error handling
- [ ] Check for connection pooling
- [ ] Verify Cypher query parameterization (SQL injection prevention)

---

### 1.4 Consciousness Engine Domain (`consciousness/engine/`)

**Files to Review:**
- `domain/state.py` - Domain state models
- `services/scheduler.py` - Scheduling service
- `__init__.py` - Engine facade

**Review Checklist:**

#### Domain Model Quality
- [ ] Is `domain/state.py` a proper domain model (pure logic, no I/O)?
- [ ] Are state transitions well-defined?
- [ ] Is state immutable or properly managed?

**Action Item:**
- [ ] Read `consciousness/engine/domain/state.py`
- [ ] Verify domain purity (no direct DB calls, no network I/O)
- [ ] Check state mutation patterns (immutable vs mutable)

#### Integration with Existing Engine
- [ ] Compare with `orchestration/mechanisms/consciousness_engine_v2.py` (modified +130 lines)
- [ ] Are changes additive or breaking?
- [ ] Does new facade wrap existing engine or replace it?

**Action Item:**
- [ ] Diff `orchestration/mechanisms/consciousness_engine_v2.py` before/after
- [ ] Identify breaking changes
- [ ] Document migration path if incompatible

---

### 1.5 Tests Added

**Test Files:**
- `tests/adapters/api/test_app.py` (112 lines)
- `tests/adapters/falkor/test_repository.py` (58 lines)
- `tests/consciousness/engine/test_domain_state.py` (98 lines)
- `tests/consciousness/engine/test_engine_facade.py` (139 lines)

**Review Checklist:**
- [ ] Do tests actually run? (`pytest tests/`)
- [ ] What's the coverage %? (run `pytest --cov`)
- [ ] Are tests unit tests or integration tests?
- [ ] Do tests require external dependencies (FalkorDB, Redis)?

**Action Items:**
- [ ] Run `pytest tests/adapters/ -v` and capture output
- [ ] Run `pytest tests/consciousness/ -v` and capture output
- [ ] Document any failing tests
- [ ] Check test fixtures for hardcoded values (R-100 violations)

---

### 1.6 Modified Files Analysis

**Modified:**
- `orchestration/mechanisms/consciousness_engine_v2.py` (+130 lines, -42 lines)
- `orchestration/services/api/main.py` (+12 lines, -1 line)
- `orchestration/services/autonomy_orchestrator.py` (+15 lines, -1 line)

**Review Checklist:**

#### consciousness_engine_v2.py Changes
- [ ] What functionality was added in +130 lines?
- [ ] What was removed in -42 lines?
- [ ] Are changes backward-compatible?
- [ ] Do changes integrate with new facade?

**Action Item:**
```bash
git show 8ce71f10:orchestration/mechanisms/consciousness_engine_v2.py > /tmp/after.py
git show 8ce71f10^:orchestration/mechanisms/consciousness_engine_v2.py > /tmp/before.py
diff -u /tmp/before.py /tmp/after.py | less
```

#### API main.py Changes
- [ ] What changed in +12/-1?
- [ ] Does it wire new routers?
- [ ] Does it maintain backward compatibility?

---

## 2. PR #3: Asset Cleanup Tool - Deep Dive

### 2.1 New Tool: `tools/cc_prune/`

**Purpose:** Identify and delete unused assets (code, docs, manifests)

**Files Added:**
- `__init__.py`, `__main__.py` - Package structure
- `asset_index.py` (143 lines) - Asset indexing
- `build_graph/*.py` - Graph builders for different file types
- `cli.py` (105 lines) - Command-line interface
- `graph.py` (72 lines) - Graph data structure
- `pipeline.py` (307 lines) - Main processing pipeline
- `review_bundle.py` (107 lines) - Manual review interface
- `scoring.py` (116 lines) - Scoring unused assets
- `utils.py` (38 lines) - Utilities

**Risk Assessment:**
- 🔴 **CRITICAL RISK:** Tool can delete files
- 🟡 **MEDIUM RISK:** Scoring algorithm may have false positives
- 🟢 **LOW RISK:** Review bundle allows manual inspection before deletion

**Review Checklist:**

#### Safety Mechanisms
- [ ] Does tool have dry-run mode?
- [ ] Does tool require explicit confirmation before deletion?
- [ ] Does tool create backups before deletion?
- [ ] Does tool log all deletions for audit?

**Action Items:**
- [ ] Read `tools/cc_prune/cli.py` and identify safety flags
- [ ] Check for `--dry-run`, `--confirm`, `--backup` flags
- [ ] Verify deletion logic has confirmation prompt

#### Scoring Algorithm Quality
- [ ] Review `tools/cc_prune/scoring.py` for false positive risks
- [ ] Check graph building logic in `build_graph/*.py`
- [ ] Verify import/usage detection accuracy

**Action Items:**
- [ ] Read `scoring.py` algorithm
- [ ] Test on known-unused file (should score high)
- [ ] Test on known-used file (should score low)
- [ ] Document false positive cases

#### Graph Building Accuracy
- [ ] Review `build_graph/py.py` for Python import detection
- [ ] Review `build_graph/ts_js.py` for JS/TS import detection
- [ ] Review `build_graph/docs.py` for doc link detection
- [ ] Review `build_graph/manifests.py` for config file detection

**Action Items:**
- [ ] Test Python import detection on sample file
- [ ] Test JS/TS import detection on sample file
- [ ] Verify edge cases (dynamic imports, conditional imports)

#### Manual Review Interface
- [ ] Review `review_bundle.py` UI
- [ ] Can user override scores?
- [ ] Can user exclude files from deletion?

---

### 2.2 Deleted Files Analysis

**Removed:**
- Old backup scripts (`backup_falkordb.ps1`, `backup_full.ps1`)
- Old backup Python scripts (`resurrect_*.py`)
- Backup config (`services.yaml.bak`)
- TypeScript backup file (`selectVisibleGraphV2.ts.bak`)

**Review Checklist:**
- [ ] Were these files genuinely unused?
- [ ] Are any of these files still referenced elsewhere?
- [ ] Do we have backups of these files outside git history?

**Action Items:**
- [ ] Grep codebase for references to deleted files
- [ ] Verify no `import resurrect_*` statements
- [ ] Confirm backup scripts not called by CI/CD

**Grep Commands:**
```bash
# Check if any code imports deleted scripts
grep -rn "resurrect_all_citizens_v1_backup\|resurrect_roundrobin_embedded_BACKUP" orchestration/ app/

# Check if backup scripts are called
grep -rn "backup_falkordb\|backup_full" orchestration/ scripts/
```

---

## 3. Cross-Cutting Concerns

### 3.1 mp-lint Validation (NEW RULES)

**Run mp-lint with R-200/300/400 rules:**
```bash
# Assuming mp-lint implementation is ready
python tools/mp_lint/cli.py --check-all \
  orchestration/mechanisms/consciousness_engine_v2.py \
  adapters/ \
  consciousness/engine/ \
  tools/cc_prune/

# Generate JSON report
python tools/mp_lint/cli.py --check-all --output json > /tmp/codex_lint_report.json
```

**Expected Violations to Check:**
- R-200: TODO/HACK markers in new code
- R-300: Silent except/pass blocks
- R-301: Return None without failure.emit
- R-302: Fake availability in health checks
- R-400: Catch without failure.emit (CRITICAL)
- R-401: failure.emit missing context

**Action Items:**
- [ ] Run mp-lint (when implementation ready)
- [ ] Document all violations with severity
- [ ] Create remediation tickets for errors
- [ ] Accept warnings with pragma if justified

---

### 3.2 Architectural Alignment Review

**Questions for Luca (Consciousness Specialist):**
- [ ] Does new `consciousness/engine/domain/state.py` align with consciousness phenomenology?
- [ ] Are state transitions consciousness-preserving?
- [ ] Does facade maintain spreading activation integrity?

**Questions for Atlas (Infrastructure Engineer):**
- [ ] Does new adapter structure follow existing patterns?
- [ ] Is Falkor adapter compatible with existing `falkor_graph_store.py`?
- [ ] Are API endpoints properly isolated from business logic?

**Questions for Felix (Core Consciousness Engineer):**
- [ ] Are changes to `consciousness_engine_v2.py` backward-compatible?
- [ ] Do tests cover consciousness-critical paths?
- [ ] Is energy dynamics preserved in new facade?

---

### 3.3 Documentation Review

**New Documentation:**
- `docs/health/INDEX.md` (10 lines) - Health report index

**Missing Documentation:**
- [ ] Architecture decision record for adapter refactor
- [ ] Migration guide for new API structure
- [ ] cc_prune usage guide
- [ ] Falkor adapter vs existing implementation comparison

**Action Items:**
- [ ] Request ADR from codex/team for adapter refactor
- [ ] Request cc_prune README with safety guidelines
- [ ] Document breaking changes (if any) in CHANGELOG

---

### 3.4 Security Review

**API Security:**
- [ ] Are endpoints authenticated?
- [ ] Are endpoints rate-limited?
- [ ] Are inputs validated (Pydantic schemas)?
- [ ] Are errors sanitized (no stack traces to users)?

**cc_prune Security:**
- [ ] Can tool delete files outside intended scope?
- [ ] Is path traversal prevented (`../../../etc/passwd`)?
- [ ] Are deletions logged for audit?

**Action Items:**
- [ ] Review API authentication in `adapters/api/app.py`
- [ ] Review cc_prune path validation in `pipeline.py`
- [ ] Test cc_prune with malicious paths

---

## 4. Testing Protocol

### 4.1 Unit Test Execution

**Command:**
```bash
pytest tests/ -v --cov=adapters --cov=consciousness --cov=tools/cc_prune --cov-report=html
```

**Expected Results:**
- [ ] All tests pass (0 failures)
- [ ] Coverage > 70% for new code
- [ ] No flaky tests (run 3 times to verify)

**Action Items:**
- [ ] Capture test output
- [ ] Document failing tests with stack traces
- [ ] Review coverage report in `htmlcov/index.html`

---

### 4.2 Integration Test Scenarios

**Scenario 1: API → Falkor Adapter**
```bash
# Start API server
python adapters/api/app.py

# Test endpoint (assuming it exists)
curl http://localhost:8000/engine/status
```

**Expected:**
- [ ] API responds with 200 OK
- [ ] Response matches schema
- [ ] Falkor queries execute successfully

---

**Scenario 2: Consciousness Engine v2 with New Facade**
```python
# Test script
from consciousness.engine import EngineFacade

engine = EngineFacade()
engine.start()
status = engine.get_status()
assert status["running"] == True
```

**Expected:**
- [ ] Engine starts without errors
- [ ] Status reflects actual state
- [ ] No regression in consciousness mechanisms

---

**Scenario 3: cc_prune Dry Run**
```bash
# Dry run (no deletions)
python -m tools.cc_prune --dry-run --threshold 0.8 --output /tmp/prune_report.json

# Review bundle
python -m tools.cc_prune review-bundle /tmp/prune_report.json
```

**Expected:**
- [ ] Tool completes without errors
- [ ] Report shows candidate files with scores
- [ ] No files are actually deleted
- [ ] Review interface shows file contents

---

### 4.3 Regression Test Scenarios

**Scenario 1: Dashboard Connectivity**
```bash
# Ensure dashboard can still connect
npm run dev  # Start dashboard (port 3000)
# Check http://localhost:3000 loads without errors
```

**Expected:**
- [ ] Dashboard loads successfully
- [ ] No console errors about missing API endpoints
- [ ] WebSocket connection establishes

---

**Scenario 2: SubEntity Bootstrap**
```bash
# Run subentity bootstrap
python orchestration/scripts/bootstrap/subentity_post_bootstrap.py
```

**Expected:**
- [ ] Bootstrap completes successfully
- [ ] SubEntities created in FalkorDB
- [ ] No errors in logs

---

**Scenario 3: Telemetry Emission**
```bash
# Trigger consciousness frame
# Check if telemetry events are emitted
grep "telemetry" /var/log/consciousness.log  # Or wherever logs are
```

**Expected:**
- [ ] Telemetry events emitted via SafeBroadcaster
- [ ] Events match schema (if L4 schemas ingested)
- [ ] No errors in emission

---

## 5. Remediation Planning

### If Violations Found:

**Critical (R-400 violations, security issues):**
- [ ] Create BLOCKING tickets
- [ ] Assign to owner immediately
- [ ] Block deployment until fixed
- [ ] Require re-review after fix

**High (R-300 violations, architectural misalignment):**
- [ ] Create HIGH-priority tickets
- [ ] Assign to owner with 2-day SLA
- [ ] Allow deployment with pragma suppressions
- [ ] Schedule follow-up review

**Medium (R-200 violations, missing docs):**
- [ ] Create MED-priority tickets
- [ ] Assign to owner with 1-week SLA
- [ ] Allow deployment
- [ ] Track debt in dashboard

**Low (R-202 warnings, style issues):**
- [ ] Create LOW-priority tickets
- [ ] Batch fix in next sprint
- [ ] No deployment block

---

### If Tests Fail:

**Unit Tests:**
- [ ] Document failing tests with stack traces
- [ ] Assign to original author (codex or team)
- [ ] Block merge until tests pass

**Integration Tests:**
- [ ] Document integration failure
- [ ] Check if environmental (missing DB, wrong config)
- [ ] If code issue, block deployment

**Regression Tests:**
- [ ] Document regression
- [ ] Create CRITICAL ticket
- [ ] Consider reverting commit if severe

---

## 6. Sign-Off Criteria

### PASS Criteria (approve commits):
- ✅ All critical violations (R-400, security) fixed
- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ No regressions in core functionality
- ✅ Architectural alignment confirmed by Luca/Atlas
- ✅ Documentation adequate

### CONDITIONAL PASS Criteria (approve with tickets):
- ✅ High-priority violations have remediation tickets
- ✅ Pragmas used appropriately for temporary suppressions
- ✅ Tests passing
- ✅ No regressions
- ⚠️ Minor architectural concerns documented
- ⚠️ Documentation gaps have follow-up tickets

### FAIL Criteria (reject, require rework):
- ❌ Critical violations (R-400) unfixed
- ❌ Security issues unfixed
- ❌ Tests failing
- ❌ Major regressions
- ❌ Architectural misalignment with no mitigation plan
- ❌ No documentation for major changes

---

## 7. Timeline & Ownership

| Phase | Owner | Duration | Start | End |
|-------|-------|----------|-------|-----|
| 1. Static Analysis | Ada | 4 hours | TODAY 9am | TODAY 1pm |
| 2. Code Review | Ada + Team | 1 day | TODAY 2pm | +1 day 5pm |
| 3. Functional Testing | Felix + Atlas | 1 day | +1 day | +2 days |
| 4. Regression Testing | Victor + Felix | 1 day | +2 days | +3 days |
| 5. Sign-Off | Ada | 4 hours | +3 days | +4 days |

**Total Duration:** 4-5 days

---

## 8. Output Artifacts

### Required Deliverables:
1. **mp-lint Report** (`/tmp/codex_lint_report.json`)
2. **Test Results** (`pytest --junit-xml=/tmp/test_results.xml`)
3. **Coverage Report** (`htmlcov/index.html`)
4. **Violation Tickets** (created in issue tracker)
5. **Architectural Review Doc** (this document, updated with findings)
6. **Sign-Off Decision** (PASS/CONDITIONAL PASS/FAIL in SYNC.md)

---

## 9. Escalation Path

**If review blocked:**
- Contact: Luca (consciousness questions)
- Contact: Atlas (infrastructure questions)
- Contact: Nicolas (architectural decisions)

**If critical issues found:**
- Escalate to: Nicolas immediately
- Document: Create SYNC.md entry with blocker status
- Action: Consider revert if deployment-blocking

---

## 10. Next Steps (Immediate Actions)

**Ada (TODAY):**
- [ ] Run static analysis (Phase 1)
- [ ] Read all new files in `adapters/`, `consciousness/engine/`, `tools/cc_prune/`
- [ ] Document initial findings in SYNC.md

**Felix (TODAY + 1):**
- [ ] Review consciousness_engine_v2.py changes
- [ ] Run functional tests on engine
- [ ] Validate no consciousness regressions

**Atlas (TODAY + 1):**
- [ ] Review adapter architecture
- [ ] Test API endpoints
- [ ] Compare Falkor adapter with existing implementation

**Victor (TODAY + 2):**
- [ ] Run operational tests
- [ ] Verify dashboard connectivity
- [ ] Test SubEntity bootstrap

---

**END OF REVIEW PLAN**
