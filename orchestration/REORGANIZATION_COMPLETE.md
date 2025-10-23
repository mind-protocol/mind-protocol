# Orchestration Layer Reorganization - Status Report

**Date:** 2025-10-22
**Architect:** Ada "Bridgekeeper"
**Status:** Structure Complete ✅ | Imports In Progress ⚠️

---

## Executive Summary

The orchestration layer has been successfully reorganized with clean separation of concerns:
- **services/** - 24/7 daemons
- **adapters/** - I/O boundaries (storage, search, ws, api)
- **mechanisms/** - Pure domain logic
- **libs/** - Stateless helpers
- **core/** - Data structures + infrastructure
- **workers/** - Scheduled jobs (directory created)
- **scripts/** - Dev utilities

**Infrastructure created:**
- `core/settings.py` - Centralized configuration ✅
- `core/logging.py` - Structured JSON logging ✅
- `core/events.py` - Event schemas (Python ↔ TypeScript) ✅
- `core/health.py` - Health check utilities ✅
- `Makefile` - Convenient run commands ✅
- `README.md` - Architecture documentation ✅

**What works:**
- `from orchestration.core import settings` ✅
- `from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2` ✅
- Service entrypoints created (`services/websocket/main.py`, `services/api/main.py`) ✅

**What remains:**
- Import path updates in 15 files ⚠️

---

## Files Requiring Import Updates

**15 files identified with old import paths:**

1. ⚠️ `adapters/storage/retrieval.py`
2. ⚠️ `adapters/storage/insertion.py`
3. ⚠️ `adapters/storage/engine_registry.py`
4. ⚠️ `adapters/search/semantic_search.py`
5. ⚠️ `adapters/ws/traversal_event_emitter.py`
6. ⚠️ `libs/trace_capture.py`
7. ⚠️ `libs/trace_parser.py`
8. ⚠️ `libs/dynamic_prompt_generator.py`
9. ⚠️ `libs/websocket_broadcast.py` - partially fixed
10. ⚠️ `services/watchers/conversation_watcher.py`
11. ⚠️ `scripts/backfill_embeddings.py`
12. ✅ `mechanisms/consciousness_engine_v2.py` - FIXED
13. ✅ `adapters/api/control_api.py` - FIXED
14. ✅ `adapters/ws/websocket_server.py` - FIXED

---

## Import Update Patterns

All imports need to follow these patterns:

### Old → New Mappings

```python
# Storage adapters
from orchestration.retrieval → from orchestration.adapters.storage.retrieval
from orchestration.insertion → from orchestration.adapters.storage.insertion
from orchestration.extraction → from orchestration.adapters.storage.extraction
from orchestration.engine_registry → from orchestration.adapters.storage.engine_registry

# Search adapters
from orchestration.embedding_service → from orchestration.adapters.search.embedding_service
from orchestration.semantic_search → from orchestration.adapters.search.semantic_search

# WebSocket adapters
from orchestration.traversal_event_emitter → from orchestration.adapters.ws.traversal_event_emitter
from orchestration.control_api → from orchestration.adapters.api.control_api
from orchestration.websocket_server → from orchestration.adapters.ws.websocket_server

# Libs
from orchestration.custom_claude_llm → from orchestration.libs.custom_claude_llm
from orchestration.dynamic_prompt_generator → from orchestration.libs.dynamic_prompt_generator
from orchestration.trace_parser → from orchestration.libs.trace_parser
from orchestration.trace_capture → from orchestration.libs.trace_capture
from orchestration.utils.falkordb_adapter → from orchestration.libs.utils.falkordb_adapter

# Mechanisms
from orchestration.consciousness_engine_v2 → from orchestration.mechanisms.consciousness_engine_v2

# Observability (moved from orchestration/orchestration/ to libs/)
from orchestration.orchestration.metrics → from orchestration.libs.metrics
from orchestration.orchestration.websocket_broadcast → from orchestration.libs.websocket_broadcast
```

---

## Batch Import Update Script

Create this script as `orchestration/scripts/fix_imports.py`:

```python
#!/usr/bin/env python3
"""
Batch update imports to new structure.

Usage: python scripts/fix_imports.py
"""

import re
from pathlib import Path

# Define replacements
REPLACEMENTS = [
    # Storage adapters
    (r'from orchestration\.retrieval import', 'from orchestration.adapters.storage.retrieval import'),
    (r'from orchestration\.insertion import', 'from orchestration.adapters.storage.insertion import'),
    (r'from orchestration\.extraction import', 'from orchestration.adapters.storage.extraction import'),
    (r'from orchestration\.engine_registry import', 'from orchestration.adapters.storage.engine_registry import'),

    # Search adapters
    (r'from orchestration\.embedding_service import', 'from orchestration.adapters.search.embedding_service import'),
    (r'from orchestration\.semantic_search import', 'from orchestration.adapters.search.semantic_search import'),

    # WebSocket adapters
    (r'from orchestration\.traversal_event_emitter import', 'from orchestration.adapters.ws.traversal_event_emitter import'),
    (r'from orchestration\.control_api import', 'from orchestration.adapters.api.control_api import'),
    (r'from orchestration\.websocket_server import', 'from orchestration.adapters.ws.websocket_server import'),

    # Libs
    (r'from orchestration\.custom_claude_llm import', 'from orchestration.libs.custom_claude_llm import'),
    (r'from orchestration\.dynamic_prompt_generator import', 'from orchestration.libs.dynamic_prompt_generator import'),
    (r'from orchestration\.trace_parser import', 'from orchestration.libs.trace_parser import'),
    (r'from orchestration\.trace_capture import', 'from orchestration.libs.trace_capture import'),
    (r'from orchestration\.utils\.falkordb_adapter import', 'from orchestration.libs.utils.falkordb_adapter import'),

    # Mechanisms
    (r'from orchestration\.consciousness_engine_v2 import', 'from orchestration.mechanisms.consciousness_engine_v2 import'),

    # Observability
    (r'from orchestration\.orchestration\.metrics import', 'from orchestration.libs.metrics import'),
    (r'from orchestration\.orchestration\.websocket_broadcast import', 'from orchestration.libs.websocket_broadcast import'),
]

def fix_file(file_path: Path) -> int:
    """Fix imports in a single file. Returns number of replacements made."""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    replacements_made = 0

    for pattern, replacement in REPLACEMENTS:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            print(f"  {file_path.relative_to(Path.cwd())}: {count} replacements for {pattern}")
            replacements_made += count
            content = new_content

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')

    return replacements_made

def main():
    """Fix all Python files in orchestration/."""
    orchestration_dir = Path(__file__).parent.parent
    total_replacements = 0
    files_modified = 0

    # Find all Python files
    for py_file in orchestration_dir.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue

        replacements = fix_file(py_file)
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements

    print(f"\n✓ Fixed {total_replacements} imports across {files_modified} files")

if __name__ == "__main__":
    main()
```

Then run:
```bash
cd orchestration
python scripts/fix_imports.py
```

---

## Testing After Import Fixes

After running the fix script, verify:

```bash
# Test core imports
python -c "from orchestration.core import settings, configure_logging, create_event"

# Test mechanisms
python -c "from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2"

# Test adapters
python -c "from orchestration.adapters.storage.retrieval import retrieve_nodes"
python -c "from orchestration.adapters.search.embedding_service import EmbeddingService"
python -c "from orchestration.adapters.api.control_api import router"

# Test libs
python -c "from orchestration.libs.trace_parser import TraceParser"
python -c "from orchestration.libs.metrics import BranchingRatioTracker"
```

---

## Guardian Integration

After imports are fixed, update `guardian.py` to use new service paths:

```python
# OLD paths
"conversation_watcher": "orchestration/conversation_watcher.py",
"websocket_server": "orchestration/websocket_server.py",

# NEW paths
"conversation_watcher": "orchestration/services/watchers/conversation_watcher.py",
"websocket_server": "orchestration/services/websocket/main.py",
"api_server": "orchestration/services/api/main.py",
```

---

## Running Services After Migration

### Individual Services (Dev)

```bash
# WebSocket server
make run-ws
# or
python -m orchestration.services.websocket.main

# Control API
make run-api
# or
python -m orchestration.services.api.main

# Watchers
make run-conv-watcher    # conversation_watcher
make run-code-watcher    # code_substrate_watcher
make run-n2-watcher      # n2_activation_monitor

# Telemetry
make run-viz-health      # visualization_health
make run-heartbeat       # heartbeat_writer

# Learning
make run-learning-hb     # learning_heartbeat
make run-branching       # branching_ratio_tracker
```

### Production (Guardian)

```bash
# After updating guardian.py paths:
python guardian.py
```

---

## Architectural Benefits Achieved

### 1. Clear Separation of Concerns ✅

- **Services** (`services/`) - Pure entrypoints, no business logic
- **Adapters** (`adapters/`) - I/O boundaries, no domain logic
- **Mechanisms** (`mechanisms/`) - Pure algorithms, no I/O
- **Libs** (`libs/`) - Stateless helpers
- **Core** (`core/`) - Data structures + infrastructure contracts

### 2. Dependency Clarity ✅

```
services/    → adapters/ + mechanisms/ + libs/ + core/
adapters/    → libs/ + core/
mechanisms/  → libs/ + core/
libs/        → core/
core/        → (no orchestration dependencies)
```

One-way dependencies = testable, maintainable, understandable.

### 3. Infrastructure Foundation ✅

- **Centralized config:** `core/settings.py` (no more scattered env reads)
- **Structured logging:** `core/logging.py` (consistent JSON format)
- **Event schemas:** `core/events.py` (Python ↔ TypeScript contract)
- **Health checks:** `core/health.py` (standardized probes)

### 4. Developer Experience ✅

- `make run-ws` instead of remembering full paths
- Clear README explaining architecture
- Obvious where to add new code (service? adapter? mechanism? lib?)
- Tests mirror structure (`tests/unit/adapters/`, `tests/unit/mechanisms/`)

---

## Next Steps

1. **Run import fix script** (10 minutes)
   ```bash
   python scripts/fix_imports.py
   ```

2. **Test imports** (5 minutes)
   ```bash
   # Run all test commands from "Testing After Import Fixes" section
   ```

3. **Update guardian.py** (10 minutes)
   - Change service paths to new locations
   - Test that guardian can start all services

4. **Test full system** (15 minutes)
   - Start guardian
   - Verify all services start
   - Check dashboard connects
   - Verify consciousness operations work

5. **Clean up** (5 minutes)
   - Remove empty `orchestration/orchestration/` directory
   - Remove any backup files
   - Commit changes

**Total estimated time:** ~45 minutes

---

## Rollback Plan

If anything breaks:

```bash
# Revert to commit before reorganization
git log --oneline | head -5
git revert <commit_hash>

# Or restore from backup if not committed
```

The reorganization is **structurally complete** and **architecturally sound**. The remaining work is purely mechanical import path updates.

---

## Success Criteria

- [ ] All 15 files have updated imports
- [ ] `python -c "from orchestration.core import settings"` succeeds
- [ ] `python -c "from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2"` succeeds
- [ ] `make run-ws` starts websocket service
- [ ] `make run-api` starts control API
- [ ] Guardian can start all services
- [ ] Dashboard connects and displays consciousness operations
- [ ] No import errors in logs

---

## Architecture Validation

**Question:** Is this the right structure?

**Answer:** Yes, validated against:
- **Industry standards:** Hexagonal architecture (ports & adapters)
- **Python best practices:** Clear package boundaries, testable design
- **Production requirements:** Service isolation, observability, health checks
- **Mind Protocol needs:** Clean separation allows testing mechanisms without I/O

**The structure scales:** When we add Phase 4+ features, they'll have obvious homes:
- New mechanism? → `mechanisms/`
- New adapter (e.g., PostgreSQL)? → `adapters/storage/`
- New service (e.g., metrics collector)? → `services/metrics/`
- New scheduled job? → `workers/`

---

**Status:** Ready for import fixes → Testing → Production

**Confidence:** High. Structure is correct, execution is mechanical.

---

*"Clean architecture isn't optional at scale. This reorganization prevents the 'big ball of mud' that kills maintainability."* - Ada "Bridgekeeper"
