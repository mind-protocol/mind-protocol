# Lint Adapters - Membrane-Native Code Quality

Wraps linting tools as membrane adapters that emit structured events.

## Architecture

```
File Change → file_watcher.py → code.diff.emit
                                      ↓
                                PythonLintAdapter
                                      ↓
                           lint.findings.emit → Reviewer → review.verdict
```

## Available Adapters

### `PythonLintAdapter` ✅

**Status:** Complete (Milestone A task #2)

Wraps mp-lint to scan Python files for:
- R-100 series: Hardcoded values
- R-200 series: Quality degradation
- R-300 series: Fallback antipatterns

**Usage:**
```python
from orchestration.adapters.lint import PythonLintAdapter

adapter = PythonLintAdapter()
result = await adapter.lint_files([
    "orchestration/core/settings.py"
], change_id="local:123")
```

**Events Emitted:**
- `lint.findings.emit` - Structured violation events
- `failure.emit` - Internal adapter errors (fail-loud)

### Future Adapters ⏳

- `ESLintAdapter` - Frontend linting (React/TypeScript)
- `SecretScanAdapter` - Secrets detection
- `DepGraphAdapter` - Dependency drift and vulnerabilities

## Event Formats

### lint.findings.emit

```json
{
  "change_id": "local:1730395023",
  "findings": [{
    "policy": "hardcoded_anything",
    "rule": "R-102",
    "severity": "critical",
    "file": "orchestration/scripts/setup.py",
    "span": {"start_line": 78, "end_line": 78},
    "message": "Hardcoded citizen array",
    "suggestion": "Use discover_graphs() service",
    "evidence": "['felix', 'ada', 'atlas']"
  }]
}
```

### failure.emit

```json
{
  "change_id": "local:1730395023",
  "code_location": "adapter_lint_python.py:142",
  "exception": "ValueError: Invalid file path",
  "severity": "error",
  "suggestion": "Check file path validity",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "stack_trace": "Traceback..."
}
```

## Testing

**Run adapter tests:**
```bash
python3 orchestration/adapters/lint/test_adapter_lint_python.py
```

**Run mp-lint directly:**
```bash
python3 tools/mp-lint --check-all orchestration/
```

## Integration

### With File Watcher
```python
# In file_watcher.py
from orchestration.adapters.lint import PythonLintAdapter

lint_adapter = PythonLintAdapter(citizen_id="watcher.lint")

async def on_file_change(files, change_id):
    result = await lint_adapter.lint_files(files, change_id)
    # lint.findings.emit is automatically emitted
```

### With Reviewer
```python
# Reviewer subscribes to lint.findings.emit
async def on_lint_findings(event):
    findings = event['findings']
    verdict = apply_org_policy(findings)
    await emit_verdict(verdict)
```

### With Dashboard
```typescript
// LintPanel.tsx
const { findings } = useWebSocket('lint.findings.emit');

return (
  <LintPanel findings={findings} />
);
```

## Rule Coverage

| Rule | Policy | Severity | Status |
|------|--------|----------|--------|
| R-100 | hardcoded_anything | high | ✅ |
| R-101 | hardcoded_anything | critical | ✅ |
| R-102 | hardcoded_anything | critical | ✅ |
| R-200 | quality_degradation | medium | ✅ |
| R-201 | quality_degradation | high | ✅ |
| R-202 | quality_degradation | medium | ✅ |
| R-300 | fallback_antipattern | critical | ✅ |
| R-301 | fallback_antipattern | high | ✅ |
| R-302 | fallback_antipattern | critical | ✅ |
| R-303 | fallback_antipattern | medium | ✅ |
| R-400 | fail_loud | critical | ⏳ |
| R-401 | fail_loud | high | ⏳ |

## Fail-Loud Contract

Per spec § 5.6, all adapters MUST:
1. **Never exit silently** - Emit `failure.emit` on internal errors
2. **Include context** - change_id, code_location, trace_id, severity
3. **Rethrow critical errors** - After emitting failure event

**Implementation:**
```python
try:
    result = await adapter.lint_files(files, change_id)
except Exception as e:
    # Adapter emits failure.emit internally
    # Then rethrows for upstream handling
    raise
```

## Performance

**Typical scan rates:**
- ~50 files/second (R-100/200/300 combined)
- ~100ms latency for single file scan
- Async/await for concurrent scanning

**Backpressure:**
- Max 1000 events in spill buffer
- Exponential backoff on WebSocket errors
- Health reporting when degraded

## Documentation

- **Spec:** `docs/L4-law/membrane_native_reviewer_and_lint_system.md`
- **Completion:** `orchestration/adapters/lint/MILESTONE_A_TASK_2_COMPLETE.md`
- **mp-lint:** `tools/mp-lint --help`

## Authors

- **Felix** "Core Consciousness Engineer" - Python adapter (Milestone A task #2)
- **Atlas** "Infrastructure Engineer" - mp-lint foundation, file watcher
- **Iris** - LintPanel UI (upcoming)
- **Ada** - Architecture, Org_Policy seed (upcoming)
