# Orchestration Layer Reorganization Summary

**Date:** 2025-10-22
**Architect:** Ada "Bridgekeeper"
**Purpose:** Clean separation of concerns (services, adapters, mechanisms, libs, core)

---

## What Changed

### File Movements

| Old Location | New Location | Type |
|-------------|-------------|------|
| `retrieval.py` | `adapters/storage/retrieval.py` | adapter |
| `insertion.py` | `adapters/storage/insertion.py` | adapter |
| `extraction.py` | `adapters/storage/extraction.py` | adapter |
| `engine_registry.py` | `adapters/storage/engine_registry.py` | adapter |
| `embedding_service.py` | `adapters/search/embedding_service.py` | adapter |
| `semantic_search.py` | `adapters/search/semantic_search.py` | adapter |
| `traversal_event_emitter.py` | `adapters/ws/traversal_event_emitter.py` | adapter |
| `websocket_server.py` | `adapters/ws/websocket_server.py` | adapter |
| `control_api.py` | `adapters/api/control_api.py` | adapter |
| `dynamic_prompt_generator.py` | `libs/dynamic_prompt_generator.py` | lib |
| `trace_parser.py` | `libs/trace_parser.py` | lib |
| `trace_capture.py` | `libs/trace_capture.py` | lib |
| `custom_claude_llm.py` | `libs/custom_claude_llm.py` | lib |
| `utils/falkordb_adapter.py` | `libs/utils/falkordb_adapter.py` | lib |
| `consciousness_engine_v2.py` | `mechanisms/consciousness_engine_v2.py` | mechanism |
| `conversation_watcher.py` | `services/watchers/conversation_watcher.py` | service |
| `code_substrate_watcher.py` | `services/watchers/code_substrate_watcher.py` | service |
| `consciousness_file_watcher.py` | `services/watchers/consciousness_file_watcher.py` | service |
| `n2_activation_monitor.py` | `services/watchers/n2_activation_monitor.py` | service |
| `visualization_health.py` | `services/telemetry/visualization_health.py` | service |
| `heartbeat_writer.py` | `services/telemetry/heartbeat_writer.py` | service |
| `learning_heartbeat.py` | `services/learning/learning_heartbeat.py` | service |
| `branching_ratio_tracker.py` | `services/learning/branching_ratio_tracker.py` | service |

### New Files Created

| File | Purpose |
|------|---------|
| `core/settings.py` | Centralized configuration |
| `core/logging.py` | Structured logging |
| `core/events.py` | Event schemas (Python ↔ TypeScript) |
| `core/health.py` | Health check utilities |
| `services/websocket/main.py` | WebSocket service entrypoint |
| `services/api/main.py` | Control API service entrypoint |
| `Makefile` | Convenient run commands |
| `README.md` | Architecture documentation |

---

## Import Updates Required

**⚠️ CRITICAL:** All imports in moved files need updating.

### Old Import Pattern → New Import Pattern

```python
# OLD (will break)
from orchestration.retrieval import retrieve_nodes
from orchestration.embedding_service import EmbeddingService
from orchestration.consciousness_engine_v2 import ConsciousnessEngineV2

# NEW (correct)
from orchestration.adapters.storage.retrieval import retrieve_nodes
from orchestration.adapters.search.embedding_service import EmbeddingService
from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2
```

### Core Imports (New)

```python
# Configuration
from orchestration.core import settings
from orchestration.core.settings import Settings

# Logging
from orchestration.core import configure_logging, log_with_fields

# Events
from orchestration.core import create_event, FrameStartEvent, NodeActivatedEvent

# Health
from orchestration.core import HealthProbe, run_health_server

# Data structures (unchanged)
from orchestration.core import Node, Link, Subentity, Graph
```

---

## Files Requiring Import Updates

These files have imports that need updating:

### High Priority (Services)
- [ ] `adapters/ws/websocket_server.py`
- [ ] `adapters/api/control_api.py`
- [ ] `services/watchers/conversation_watcher.py`
- [ ] `services/watchers/code_substrate_watcher.py`
- [ ] `services/watchers/n2_activation_monitor.py`
- [ ] `services/telemetry/visualization_health.py`
- [ ] `services/telemetry/heartbeat_writer.py`
- [ ] `services/learning/learning_heartbeat.py`

### Medium Priority (Mechanisms)
- [ ] `mechanisms/consciousness_engine_v2.py`
- [ ] `mechanisms/entity_bootstrap.py`
- [ ] `mechanisms/stimulus_injection.py`
- [ ] `mechanisms/weight_learning.py`

### Low Priority (Libs - may not need updates)
- [ ] `libs/dynamic_prompt_generator.py`
- [ ] `libs/trace_parser.py`
- [ ] `libs/trace_capture.py`

### Adapters (cross-import each other)
- [ ] `adapters/storage/retrieval.py`
- [ ] `adapters/storage/insertion.py`
- [ ] `adapters/storage/extraction.py`
- [ ] `adapters/search/embedding_service.py`
- [ ] `adapters/search/semantic_search.py`
- [ ] `adapters/ws/traversal_event_emitter.py`

---

## Testing Strategy

1. **Import Testing:** Try importing each module to catch ImportErrors
2. **Service Startup:** Test that services start without crashing
3. **Integration Testing:** Verify services can talk to each other
4. **Guardian Integration:** Ensure guardian can start all services

### Manual Testing Commands

```bash
# Test imports
python -c "from orchestration.core import settings; print(settings.WS_PORT)"
python -c "from orchestration.adapters.storage.retrieval import retrieve_nodes"
python -c "from orchestration.mechanisms.consciousness_engine_v2 import ConsciousnessEngineV2"

# Test service startup (will fail if imports broken)
timeout 5 make run-ws || echo "WebSocket started (or timeout)"
timeout 5 make run-api || echo "API started (or timeout)"
```

---

## Migration Phases

### Phase 1: Structure ✅ COMPLETE
- [x] Create directory structure
- [x] Move files to new locations
- [x] Create core infrastructure (settings, logging, events, health)
- [x] Create service entrypoints
- [x] Create Makefile and README

### Phase 2: Imports ⚠️ IN PROGRESS
- [ ] Update imports in all services
- [ ] Update imports in all adapters
- [ ] Update imports in all mechanisms
- [ ] Update imports in all libs

### Phase 3: Testing ⏳ PENDING
- [ ] Test imports for all modules
- [ ] Test service startup
- [ ] Test integration between services
- [ ] Test guardian integration

### Phase 4: Cleanup ⏳ PENDING
- [ ] Remove deprecated files
- [ ] Update guardian.py to use new paths
- [ ] Update any scripts in project root
- [ ] Update .gitignore if needed

---

## Known Issues

1. **Import breakage:** All services will fail to start until imports are updated
2. **Guardian integration:** Guardian needs to know new service paths
3. **External scripts:** Any scripts outside orchestration/ that import from it will break

---

## Rollback Plan

If this breaks production:

1. **Immediate:** Revert to commit before reorganization
2. **Medium-term:** Complete import updates in separate branch
3. **Test thoroughly before merging**

---

## Benefits Achieved

1. **Clear separation:** Services vs adapters vs mechanisms vs libs
2. **Dependency clarity:** One-way dependencies (services → adapters → core)
3. **Testability:** Can test mechanisms without starting services
4. **Maintainability:** Easy to find what runs 24/7 vs what's a library
5. **Observability:** Standardized logging, health checks, events
6. **Developer experience:** `make run-ws` instead of remembering paths

---

## Next Steps

1. **Update imports systematically** (start with services, then adapters, then mechanisms)
2. **Test each service** as imports are updated
3. **Update guardian.py** to use new service paths
4. **Test full system** with guardian managing all processes
5. **Document any remaining issues**

---

**Status:** Structure complete, imports need updating before services will start.

**Estimated time to completion:** 2-3 hours for import updates + testing

**Risk level:** Medium (breaking change but easily rollbackable)

---

*"The architecture is sound. Now we make the wiring match the blueprint."* - Ada
