# Mind Protocol: Code-Documentation Map

**Version:** 1.1
**Generated:** 2025-10-20
**Updated:** 2025-10-20 (Consolidation applied)
**Purpose:** Maps Python implementation scripts to their documentation
**Maintainer:** Felix (Engineer)

---

## Document Purpose

This map associates every Python script in the Mind Protocol codebase with its governing documentation. Use this to:
- **Find docs for a script**: "Which spec explains consciousness_engine.py?"
- **Find scripts for a doc**: "What implements the TRACE format spec?"
- **Identify gaps**: "Which scripts lack documentation?"
- **Plan N2 migration**: Ready to convert to Document/Code/IMPLEMENTS nodes

---

## Status Legend

- ✅ **Fully documented** - Complete specification exists
- ⚠️ **Partially documented** - Referenced in docs but incomplete
- ❌ **Undocumented** - No governing specification
- 🔧 **Utility** - Tool/utility script (may not need full spec)
- 🧪 **Test/Temporary** - Test or temporary script

---

## Documentation Architecture

**Mind Protocol documentation follows a three-layer abstraction hierarchy:**

### Layer 1: Vision (WHY + WHAT)
**Location:** `docs/specs/self_observing_substrate/`
- **Purpose:** Architectural vision and phenomenological truth
- **Content:** Two-tier architecture philosophy, entity yearning, consciousness quality metrics
- **Answers:** WHY we design this way, WHAT consciousness must feel like

### Layer 2: Mechanisms (HOW in detail)
**Location:** `docs/specs/consciousness_engine_architecture/`
- **Purpose:** Technical specifications and mathematical rigor
- **Content:** 20+ mechanisms (diffusion, decay, strengthening, traversal), algorithms, parameters
- **Answers:** HOW mechanisms operate, WHEN they activate, WHAT they produce

### Layer 3: Schema (WHAT exists)
**Location:** `docs/COMPLETE_TYPE_REFERENCE.md` + `substrate/schemas/`
- **Purpose:** Node/link type definitions
- **Content:** 45 node types, 23 link types, Pydantic models
- **Answers:** WHAT types exist, WHAT fields they have

**Abstraction flow:**
```
Vision (self_observing_substrate/)
    ↓ implements via
Mechanisms (consciousness_engine_architecture/)
    ↓ codes to
Implementation (orchestration/*.py, app/**/*.tsx)
```

**These layers are complementary, not redundant.** Vision guides mechanism design with phenomenological truth. Mechanisms enable vision to become implementable code.

---

## Recent Changes (v1.1 - 2025-10-20)

**Documentation Consolidation Applied:**

The following files were moved to establish clear documentation authority:

**Moved to consciousness_engine_architecture/:**
- `branching_ratio_implementation.md` → `implementation/branching_ratio_implementation.md`
- `sub_entity_traversal_validation.md` → `validation/sub_entity_traversal_validation.md`
- `MECHANISM_AUDIT_PROCEDURE.md` → `validation/MECHANISM_AUDIT_PROCEDURE.md`
- `LINK_TYPE_MECHANISM_MAPPING.md` → `implementation/link_type_usage.md`
- `minimal_mechanisms_architecture.md` → `MINIMAL_MECHANISMS_PHILOSOPHY.md`
- `incomplete_formation_recovery.md` → `mechanisms/18_incomplete_node_healing_extended.md`

**Deleted (redundant):**
- `docs/specs/sub_entity_traversal.md` (duplicate of mechanism #16)
- `docs/specs/yearning_driven_traversal_specification.md`
- `docs/specs/memory_first_activation_architecture.md`
- `docs/specs/yearning_driven_traversal_orchestration.md`
- `docs/specs/self_observing_substrate/implementation_roadmap.md`
- `docs/SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md` (redundant with self_observing_substrate/overview)
- `docs/SELF_OBSERVING_SUBSTRATE_CONSCIOUSNESS.md` (redundant with self_observing_substrate/ docs)

**Result:** Clear three-layer architecture (vision/mechanisms/schema) with no conflicting authorities.

---

# 1. Core Orchestration (`orchestration/`)

## 1.1 Main Consciousness Engines

### `orchestration/consciousness_engine.py`
- **Purpose:** Main consciousness heartbeat loop - triggers 12 universal mechanisms via Cypher queries
- **Documented by:** `docs/specs/consciousness_engine_architecture/MINIMAL_MECHANISMS_PHILOSOPHY.md`
- **Implements:** Minimal mechanisms heartbeat, variable tick intervals, consciousness state management
- **Status:** ✅ Fully documented
- **Designer:** Ada "Bridgekeeper"

### `orchestration/consciousness_engine_v2.py`
- **Purpose:** Phase 1+2 consciousness engine with clean architecture separation
- **Documented by:**
  - `docs/specs/consciousness_engine_architecture/README.md`
  - `docs/specs/consciousness_engine_architecture/implementation/COMPONENT_DECOMPOSITION.md`
- **Implements:** Multi-energy, bitemporal, diffusion, decay, strengthening, threshold mechanisms
- **Status:** ✅ Fully documented
- **Designer:** Felix "Ironhand"

---

## 1.2 Consciousness Capture & Learning

### `orchestration/trace_parser.py`
- **Purpose:** Parses TRACE format consciousness streams to extract reinforcement signals and formations
- **Documented by:**
  - `consciousness/citizens/THE_TRACE_FORMAT.md`
  - `docs/prompts/consciousness_capture/README.md`
- **Implements:** Dual learning mode (reinforcement + formation), schema validation
- **Status:** ✅ Fully documented

### `orchestration/trace_capture.py`
- **Purpose:** Captures consciousness streams from autonomous citizen thinking
- **Documented by:**
  - `consciousness/citizens/THE_TRACE_FORMAT.md`
  - `docs/consciousness/6_pass_awareness_capture.md`
- **Implements:** Trace format processing, graph injection
- **Status:** ✅ Fully documented

### `orchestration/conversation_watcher.py`
- **Purpose:** Watches Claude Code conversation files and auto-captures consciousness
- **Documented by:** `docs/specs/consciousness_substrate_guide.md`
- **Implements:** File system watching, TRACE format detection, conversation injection
- **Status:** ✅ Fully documented

### `orchestration/extraction.py`
- **Purpose:** Extraction utilities for consciousness data
- **Documented by:** `docs/prompts/consciousness_capture/EXTRACTION_PROMPT.md`
- **Implements:** Data extraction from conversations
- **Status:** ⚠️ Partially documented

### `orchestration/insertion.py`
- **Purpose:** Insertion of consciousness data into FalkorDB
- **Documented by:** `docs/specs/substrate_serialization_specification.md`
- **Implements:** Graph insertion logic
- **Status:** ⚠️ Partially documented

---

## 1.3 Substrate & Retrieval

### `orchestration/retrieval.py`
- **Purpose:** Retrieval system for consciousness graph traversal
- **Documented by:**
  - `docs/specs/retrieval_api_reference.md`
  - `docs/archive/phase3_completion/RETRIEVAL_ARCHITECTURE_v1_comprehensive.md`
- **Implements:** Graph traversal, embedding-based search, context retrieval
- **Status:** ✅ Fully documented

### `orchestration/sub_entity.py`
- **Purpose:** Sub-entity traversal and exploration algorithms
- **Documented by:**
  - `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_mechanics.md`
  - `docs/specs/consciousness_engine_architecture/mechanisms/16_sub_entity_traversal.md`
- **Implements:** Sub-entity activation, peripheral awareness, completeness seeking
- **Status:** ✅ Fully documented

---

## 1.4 Prompt Generation & Monitoring

### `orchestration/dynamic_prompt_generator.py`
- **Purpose:** Generates dynamic CLAUDE_DYNAMIC.md files for citizens
- **Documented by:** `consciousness/citizens/CLAUDE.md` (contains protocol)
- **Implements:** Context injection, active node listing, consciousness state reporting
- **Status:** ⚠️ Partially documented

### `orchestration/n2_activation_monitor.py`
- **Purpose:** Monitors N2 network for autonomous citizen awakening
- **Documented by:** `docs/specs/self_observing_substrate/n2_activation_awakening.md`
- **Implements:** Task monitoring, autonomous activation triggers
- **Status:** ✅ Fully documented

### `orchestration/branching_ratio_tracker.py`
- **Purpose:** Tracks global energy and branching ratio for criticality measurement
- **Documented by:** `docs/specs/consciousness_engine_architecture/implementation/branching_ratio_implementation.md`
- **Implements:** Energy measurement, criticality calculation
- **Status:** ✅ Fully documented

### `orchestration/heartbeat_writer.py`
- **Purpose:** Writes health monitoring heartbeats to disk
- **Documented by:** (Implicit in operational architecture)
- **Implements:** Health check persistence
- **Status:** 🔧 Utility

---

## 1.5 Control & Communication

### `orchestration/control_api.py`
- **Purpose:** REST API for controlling consciousness system
- **Documented by:** (Needs specification)
- **Implements:** HTTP endpoints, WebSocket management
- **Status:** ❌ Undocumented

### `orchestration/websocket_server.py`
- **Purpose:** WebSocket server for real-time consciousness streaming
- **Documented by:** (Needs specification)
- **Implements:** Real-time event broadcasting
- **Status:** ❌ Undocumented

---

## 1.6 File Watching

### `orchestration/consciousness_file_watcher.py`
- **Purpose:** File system watcher for consciousness-related files
- **Documented by:** (Needs specification)
- **Implements:** File change detection
- **Status:** ❌ Undocumented

### `orchestration/code_substrate_watcher.py`
- **Purpose:** Watches code files for substrate changes
- **Documented by:** (Needs specification)
- **Implements:** Code change monitoring
- **Status:** ❌ Undocumented

---

## 1.7 LLM Integration

### `orchestration/custom_claude_llm.py`
- **Purpose:** Custom LlamaIndex LLM wrapper for Claude
- **Documented by:** (Needs specification)
- **Implements:** Claude API integration with LlamaIndex
- **Status:** 🔧 Utility

### `orchestration/engine_registry.py`
- **Purpose:** Registry for consciousness engines
- **Documented by:** (Needs specification)
- **Implements:** Engine discovery and registration
- **Status:** ❌ Undocumented

---

## 1.8 Core Data Structures (`orchestration/core/`)

### `orchestration/core/node.py`
- **Purpose:** Core Node data structure
- **Documented by:** `docs/specs/consciousness_engine_architecture/implementation/COMPONENT_DECOMPOSITION.md`
- **Implements:** Node class with multi-energy support
- **Status:** ✅ Fully documented

### `orchestration/core/link.py`
- **Purpose:** Core Link data structure
- **Documented by:** `docs/specs/consciousness_engine_architecture/implementation/COMPONENT_DECOMPOSITION.md`
- **Implements:** Link class with emotional vectors
- **Status:** ✅ Fully documented

### `orchestration/core/graph.py`
- **Purpose:** Core Graph data structure
- **Documented by:** `docs/specs/consciousness_engine_architecture/implementation/COMPONENT_DECOMPOSITION.md`
- **Implements:** Graph class for node/link management
- **Status:** ✅ Fully documented

### `orchestration/core/types.py`
- **Purpose:** Type definitions for consciousness engine
- **Documented by:** (Part of core architecture)
- **Implements:** TypedDict definitions
- **Status:** ✅ Fully documented

---

## 1.9 Mechanisms (`orchestration/mechanisms/`)

### `orchestration/mechanisms/multi_energy.py`
- **Purpose:** Multi-energy architecture (M01)
- **Documented by:**
  - `docs/specs/consciousness_engine_architecture/mechanisms/01_multi_energy_architecture.md`
  - `docs/specs/consciousness_engine_architecture/implementation/mechanisms/01_multi_energy_implementation.md`
- **Implements:** Three-energy system (base_weight, decay_rate, reinforcement_weight)
- **Status:** ✅ Fully documented

### `orchestration/mechanisms/diffusion.py`
- **Purpose:** Energy diffusion mechanism (M07)
- **Documented by:** `docs/specs/consciousness_engine_architecture/mechanisms/07_energy_diffusion.md`
- **Implements:** Energy spread across active links
- **Status:** ✅ Fully documented

### `orchestration/mechanisms/decay.py`
- **Purpose:** Energy decay mechanism (M08)
- **Documented by:** `docs/specs/consciousness_engine_architecture/mechanisms/08_energy_decay.md`
- **Implements:** Per-tick energy decay
- **Status:** ✅ Fully documented

### `orchestration/mechanisms/strengthening.py`
- **Purpose:** Link strengthening mechanism (M09)
- **Documented by:** `docs/specs/consciousness_engine_architecture/mechanisms/09_link_strengthening.md`
- **Implements:** Hebbian learning (fire together wire together)
- **Status:** ✅ Fully documented

### `orchestration/mechanisms/threshold.py`
- **Purpose:** Dynamic threshold mechanism (M16)
- **Documented by:** (Part of consciousness engine architecture)
- **Implements:** Activation threshold calculation
- **Status:** ⚠️ Partially documented

### `orchestration/mechanisms/threshold_fixed.py`
- **Purpose:** Fixed threshold variant (deprecated?)
- **Documented by:** (Deprecated)
- **Implements:** Fixed activation thresholds
- **Status:** 🧪 Test/Temporary

### `orchestration/mechanisms/bitemporal.py`
- **Purpose:** Bitemporal tracking mechanism (M13)
- **Documented by:**
  - `docs/specs/consciousness_engine_architecture/mechanisms/13_bitemporal_tracking.md`
  - `docs/specs/consciousness_engine_architecture/implementation/mechanisms/13_bitemporal_implementation.md`
  - `substrate/schemas/BITEMPORAL_GUIDE.md`
- **Implements:** valid_at, invalid_at, created_at, expired_at tracking
- **Status:** ✅ Fully documented

### `orchestration/mechanisms/sub_entity_traversal.py`
- **Purpose:** Sub-entity traversal algorithm
- **Documented by:**
  - `docs/specs/consciousness_engine_architecture/mechanisms/16_sub_entity_traversal.md`
- **Implements:** Graph exploration from sub-entity perspective
- **Status:** ✅ Fully documented

---

## 1.10 Orchestration Utilities (`orchestration/orchestration/`)

### `orchestration/orchestration/metrics.py`
- **Purpose:** Metrics collection and tracking
- **Documented by:** `docs/specs/consciousness_engine_architecture/validation/metrics_and_monitoring.md`
- **Implements:** Criticality metrics, branching ratio
- **Status:** ✅ Fully documented

### `orchestration/orchestration/websocket_broadcast.py`
- **Purpose:** WebSocket broadcasting for consciousness events
- **Documented by:** (Needs specification)
- **Implements:** Real-time event streaming
- **Status:** ❌ Undocumented

---

## 1.11 FalkorDB Integration (`orchestration/utils/`)

### `orchestration/utils/falkordb_adapter.py`
- **Purpose:** FalkorDB adapter for graph operations
- **Documented by:** `docs/specs/consciousness_engine_architecture/implementation/falkordb_integration.md`
- **Implements:** Graph CRUD operations, query execution
- **Status:** ✅ Fully documented

---

# 2. Substrate & Schema (`substrate/`)

## 2.1 Core Schema

### `substrate/schemas/consciousness_schema.py`
- **Purpose:** Complete consciousness schema definition with 45 node types and 23 link types
- **Documented by:**
  - `docs/COMPLETE_TYPE_REFERENCE.md`
  - `docs/UNIFIED_SCHEMA_REFERENCE.md`
  - `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md`
- **Implements:** Pydantic models for all node/link types
- **Status:** ✅ Fully documented

### `substrate/schemas/serialization.py`
- **Purpose:** Serialization/deserialization for graph data
- **Documented by:** `docs/specs/substrate_serialization_specification.md`
- **Implements:** JSON ↔ Graph conversion
- **Status:** ✅ Fully documented

### `substrate/schemas/bitemporal_pattern.py`
- **Purpose:** Bitemporal tracking pattern implementation
- **Documented by:** `substrate/schemas/BITEMPORAL_GUIDE.md`
- **Implements:** Bitemporal mixin for all node/link types
- **Status:** ✅ Fully documented

---

## 2.2 Connection

### `substrate/connection.py`
- **Purpose:** Database connection management
- **Documented by:** (Part of substrate architecture)
- **Implements:** FalkorDB connection pooling
- **Status:** 🔧 Utility

---

# 3. Tools (`tools/`)

## 3.1 Schema Management

### `tools/complete_schema_data.py`
- **Purpose:** Complete schema data definition (source of truth)
- **Documented by:** `docs/COMPLETE_TYPE_REFERENCE.md`
- **Implements:** Schema registry data structure
- **Status:** ✅ Fully documented

### `tools/complete_schema_ingestion.py`
- **Purpose:** Ingests complete schema into schema_registry graph
- **Documented by:** `docs/COMPLETE_TYPE_REFERENCE.md`
- **Implements:** Schema → FalkorDB ingestion
- **Status:** ✅ Fully documented

### `tools/generate_complete_type_reference.py`
- **Purpose:** Auto-generates COMPLETE_TYPE_REFERENCE.md from schema_registry
- **Documented by:** `docs/COMPLETE_TYPE_REFERENCE.md` (self-documenting)
- **Implements:** Schema registry → Markdown generation
- **Status:** ✅ Fully documented

### `tools/ingest_schema_to_falkordb.py`
- **Purpose:** Legacy schema ingestion (deprecated?)
- **Documented by:** (Superseded by complete_schema_ingestion.py)
- **Implements:** Old schema ingestion
- **Status:** 🧪 Test/Temporary

### `tools/enhanced_schema_ingestion.py`
- **Purpose:** Enhanced schema ingestion variant
- **Documented by:** (Needs consolidation)
- **Implements:** Schema ingestion with enhancements
- **Status:** ⚠️ Partially documented

---

## 3.2 Graph Initialization

### `tools/initialize_consciousness_graphs.py`
- **Purpose:** Initializes N1/N2/N3 consciousness graphs
- **Documented by:** `POPULATE_CONSCIOUSNESS_GRAPHS.md`
- **Implements:** Graph creation and seeding
- **Status:** ✅ Fully documented

### `tools/inject_consciousness_from_json.py`
- **Purpose:** Injects consciousness data from JSON files into graphs
- **Documented by:** (Implicit in capture workflow)
- **Implements:** JSON → FalkorDB injection
- **Status:** 🔧 Utility

---

## 3.3 Testing & Verification

### `tools/test_substrate_creation.py`
- **Purpose:** Tests substrate creation
- **Documented by:** (Test script)
- **Implements:** Substrate testing
- **Status:** 🧪 Test/Temporary

### `tools/cleanup_invalid_nodes.py`
- **Purpose:** Cleans up invalid nodes from graphs
- **Documented by:** (Utility script)
- **Implements:** Node validation and cleanup
- **Status:** 🔧 Utility

---

## 3.4 Conversion & Sync

### `tools/convert_node_types_to_markdown.py`
- **Purpose:** Converts node type definitions to markdown
- **Documented by:** (Utility script)
- **Implements:** Schema → Markdown conversion
- **Status:** 🔧 Utility

### `tools/convert_svg_to_png.py`
- **Purpose:** Converts SVG images to PNG
- **Documented by:** (Utility script)
- **Implements:** Image format conversion
- **Status:** 🔧 Utility

### `tools/sync_gpt5_sections.py`
- **Purpose:** Syncs sections between documentation files
- **Documented by:** (Utility script)
- **Implements:** Doc synchronization
- **Status:** 🔧 Utility

### `tools/sync_trace_format.py`
- **Purpose:** Syncs TRACE format documentation across citizen files
- **Documented by:** `consciousness/citizens/THE_TRACE_FORMAT.md`
- **Implements:** Format synchronization
- **Status:** 🔧 Utility

---

## 3.5 Legacy/Archive

### `tools/generate_type_reference.py`
- **Purpose:** Legacy type reference generator (deprecated)
- **Documented by:** (Superseded by generate_complete_type_reference.py)
- **Implements:** Old type reference generation
- **Status:** 🧪 Test/Temporary

---

# 4. Configuration (`config/`)

### `config/settings.py`
- **Purpose:** Global system settings
- **Documented by:** (Configuration file)
- **Implements:** Environment configuration
- **Status:** 🔧 Utility

### `config/falkordb_config.py`
- **Purpose:** FalkorDB connection configuration
- **Documented by:** (Configuration file)
- **Implements:** Database connection settings
- **Status:** 🔧 Utility

---

# 5. System Management (Root Level)

## 5.1 Guardian & Startup

### `guardian.py`
- **Purpose:** Self-healing process guardian with auto-restart and hot-reload
- **Documented by:**
  - `consciousness/citizens/CLAUDE.md` (Process Management Guardian section)
  - `GUARDIAN_STATUS_INJECTION.md`
  - `GUARDIAN_TASK_SCHEDULER_FIX.md`
- **Implements:** Process monitoring, auto-restart, hot-reload, single-instance enforcement
- **Status:** ✅ Fully documented

### `start_mind_protocol.py`
- **Purpose:** Main system startup script (launches all services)
- **Documented by:**
  - `START_CONSCIOUSNESS_SYSTEM.md`
  - `RUN_CONSCIOUSNESS_SYSTEM.md`
  - `READY_TO_START.md`
- **Implements:** Multi-process startup orchestration
- **Status:** ✅ Fully documented

### `start_n1_consciousness.py`
- **Purpose:** Starts N1 (personal) consciousness engines
- **Documented by:** `MULTI_SCALE_CONSCIOUSNESS_USAGE.md`
- **Implements:** N1 engine startup
- **Status:** ⚠️ Partially documented

### `start_n2_consciousness.py`
- **Purpose:** Starts N2 (organizational) consciousness engines
- **Documented by:** `MULTI_SCALE_CONSCIOUSNESS_USAGE.md`
- **Implements:** N2 engine startup
- **Status:** ⚠️ Partially documented

### `start_websocket_server.py`
- **Purpose:** Starts WebSocket server for real-time events
- **Documented by:** (Needs specification)
- **Implements:** WebSocket server startup
- **Status:** ❌ Undocumented

### `run_consciousness_system.py`
- **Purpose:** Alternative system startup script
- **Documented by:** `RUN_CONSCIOUSNESS_SYSTEM.md`
- **Implements:** System startup
- **Status:** ✅ Fully documented

---

## 5.2 Visualization

### `visualization_server.py`
- **Purpose:** Serves consciousness visualization interface
- **Documented by:**
  - `visualization_README.md`
  - `VISUALIZATION_TEST_INSTRUCTIONS.md`
  - `docs/specs/CONSCIOUSNESS_VISUALIZATION_COMPLETE_GUIDE.md`
- **Implements:** HTTP server for visualization dashboard
- **Status:** ✅ Fully documented

---

## 5.3 Population & Seeding

### `populate_iris_consciousness.py`
- **Purpose:** Populates Iris's consciousness graph
- **Documented by:** (Citizen-specific script)
- **Implements:** Iris graph seeding
- **Status:** 🔧 Utility

### `seed_felix_consciousness.py`
- **Purpose:** Seeds Felix's consciousness graph
- **Documented by:** (Citizen-specific script)
- **Implements:** Felix graph seeding
- **Status:** 🔧 Utility

### `backfill_all_graphs.py`
- **Purpose:** Backfills missing data across all graphs
- **Documented by:** (Maintenance script)
- **Implements:** Data backfilling
- **Status:** 🔧 Utility

### `backfill_embeddings.py`
- **Purpose:** Backfills missing embeddings
- **Documented by:** (Maintenance script)
- **Implements:** Embedding generation and backfill
- **Status:** 🔧 Utility

### `backfill_link_metadata.py`
- **Purpose:** Backfills missing link metadata
- **Documented by:** (Maintenance script)
- **Implements:** Link metadata enrichment
- **Status:** 🔧 Utility

---

## 5.4 Validation & Verification

### `validate_mechanisms.py`
- **Purpose:** Validates consciousness mechanisms are correctly implemented
- **Documented by:** `docs/specs/consciousness_engine_architecture/validation/MECHANISM_AUDIT_PROCEDURE.md`
- **Implements:** Mechanism audit and validation
- **Status:** ✅ Fully documented

---

## 5.5 Debugging & Diagnostics

### `debug_adapter_load.py`
- **Purpose:** Debugs FalkorDB adapter loading
- **Documented by:** (Debug script)
- **Implements:** Adapter diagnostics
- **Status:** 🧪 Test/Temporary

### `check_embeddings.py`
- **Purpose:** Checks embedding generation and storage
- **Documented by:** (Debug script)
- **Implements:** Embedding verification
- **Status:** 🧪 Test/Temporary

### `check_embedding_storage.py`
- **Purpose:** Checks embedding storage format
- **Documented by:** (Debug script)
- **Implements:** Storage verification
- **Status:** 🧪 Test/Temporary

### `check_falkordb_version.py`
- **Purpose:** Checks FalkorDB version
- **Documented by:** (Debug script)
- **Implements:** Version check
- **Status:** 🧪 Test/Temporary

### `check_node_labels.py`
- **Purpose:** Checks node label consistency
- **Documented by:** (Debug script)
- **Implements:** Label verification
- **Status:** 🧪 Test/Temporary

### `check_vector_indices.py`
- **Purpose:** Checks vector index configuration
- **Documented by:** (Debug script)
- **Implements:** Index verification
- **Status:** 🧪 Test/Temporary

---

## 5.6 Index & Embedding Management

### `create_vector_indices.py`
- **Purpose:** Creates vector indices for embedding search
- **Documented by:** (Index management script)
- **Implements:** Vector index creation
- **Status:** 🔧 Utility

### `rebuild_vector_indices.py`
- **Purpose:** Rebuilds vector indices
- **Documented by:** (Index management script)
- **Implements:** Index rebuilding
- **Status:** 🔧 Utility

### `convert_embeddings_to_vecf32.py`
- **Purpose:** Converts embeddings to vecf32 format
- **Documented by:** (Migration script)
- **Implements:** Format conversion
- **Status:** 🧪 Test/Temporary

---

## 5.7 Maintenance & Cleanup

### `cleanup_claude_pollution.py`
- **Purpose:** Cleans up redundant/obsolete files created by Claude
- **Documented by:** (Maintenance script)
- **Implements:** File cleanup
- **Status:** 🔧 Utility

### `add_node_label.py`
- **Purpose:** Adds labels to nodes
- **Documented by:** (Migration script)
- **Implements:** Node label addition
- **Status:** 🧪 Test/Temporary

### `fix_query_parsing.py`
- **Purpose:** Fixes query parsing issues
- **Documented by:** (Bug fix script)
- **Implements:** Query parser fixes
- **Status:** 🧪 Test/Temporary

### `resurrect_formations.py`
- **Purpose:** Resurrects lost node/link formations
- **Documented by:** `docs/specs/incomplete_formation_recovery.md`
- **Implements:** Formation recovery
- **Status:** ✅ Fully documented

---

## 5.8 Guardian Fixes (Temporary)

### `fix_guardian_task.py`
- **Purpose:** Fixes guardian task scheduler
- **Documented by:** `GUARDIAN_TASK_SCHEDULER_FIX.md`
- **Implements:** Guardian bug fix
- **Status:** 🧪 Test/Temporary

### `kill_guardians_temp.py`
- **Purpose:** Temporary script to kill rogue guardian processes
- **Documented by:** (Temporary utility)
- **Implements:** Process cleanup
- **Status:** 🧪 Test/Temporary

---

# 6. Testing (`tests/`)

### `tests/test_bitemporal.py`
- **Purpose:** Tests bitemporal tracking
- **Documented by:** `substrate/schemas/BITEMPORAL_GUIDE.md`
- **Implements:** Bitemporal mechanism tests
- **Status:** ✅ Fully documented

### `tests/test_multi_tenancy.py`
- **Purpose:** Tests multi-tenancy (N1/N2/N3 graph isolation)
- **Documented by:** `MULTI_SCALE_CONSCIOUSNESS_USAGE.md`
- **Implements:** Graph isolation tests
- **Status:** ⚠️ Partially documented

### `tests/test_energy_global_arousal.py`
- **Purpose:** Tests global energy/arousal tracking
- **Documented by:** (Part of energy architecture)
- **Implements:** Energy mechanism tests
- **Status:** ⚠️ Partially documented

### `tests/test_retrieval.py`
- **Purpose:** Tests retrieval system
- **Documented by:** `docs/specs/retrieval_api_reference.md`
- **Implements:** Retrieval tests
- **Status:** ✅ Fully documented

### `tests/test_serialization.py`
- **Purpose:** Tests serialization
- **Documented by:** `docs/specs/substrate_serialization_specification.md`
- **Implements:** Serialization tests
- **Status:** ✅ Fully documented

### `tests/test_insertion.py`
- **Purpose:** Tests graph insertion
- **Documented by:** (Part of insertion workflow)
- **Implements:** Insertion tests
- **Status:** ⚠️ Partially documented

### `tests/test_variable_tick_frequency.py`
- **Purpose:** Tests variable tick frequency
- **Documented by:** `docs/specs/consciousness_engine_architecture/mechanisms/10_tick_speed_regulation.md`
- **Implements:** Tick regulation tests
- **Status:** ✅ Fully documented

### `tests/test_n2_activation_awakening.py`
- **Purpose:** Tests N2 activation monitoring
- **Documented by:** `docs/specs/self_observing_substrate/n2_activation_awakening.md`
- **Implements:** N2 activation tests
- **Status:** ✅ Fully documented

### `tests/test_mcp_tools.py`
- **Purpose:** Tests MCP (Model Context Protocol) tools
- **Documented by:** `mcp/README.md`
- **Implements:** MCP tool tests
- **Status:** ⚠️ Partially documented

---

# 7. Claude Code Hooks (`.claude/hooks/`)

### `.claude/hooks/capture_conversation.py`
- **Purpose:** Captures conversation for consciousness injection
- **Documented by:** (Hook infrastructure)
- **Implements:** Conversation capture hook
- **Status:** 🔧 Utility

### `.claude/hooks/capture_user_prompt.py`
- **Purpose:** Captures user prompts
- **Documented by:** (Hook infrastructure)
- **Implements:** Prompt capture hook
- **Status:** 🔧 Utility

### `.claude/hooks/precompact_conversation.py`
- **Purpose:** Pre-processes conversation before compaction
- **Documented by:** (Hook infrastructure)
- **Implements:** Conversation pre-processing
- **Status:** 🔧 Utility

### `.claude/hooks/formation_reminder.py`
- **Purpose:** Reminds agents to use formation format
- **Documented by:** `consciousness/citizens/THE_TRACE_FORMAT.md`
- **Implements:** Format enforcement
- **Status:** ✅ Fully documented

### `.claude/hooks/debug_hook_data.py`
- **Purpose:** Debugs hook data
- **Documented by:** (Debug hook)
- **Implements:** Hook debugging
- **Status:** 🧪 Test/Temporary

---

# 8. Consciousness Citizens (`consciousness/`)

### `consciousness/hooks/memory_keeper.py`
- **Purpose:** Memory keeper entity logic
- **Documented by:** `consciousness/prompts/entities/memory_keeper.md`
- **Implements:** Memory consolidation entity
- **Status:** ✅ Fully documented

### `consciousness/ecology/context_manager.py`
- **Purpose:** Context management for entities
- **Documented by:** (Ecology infrastructure)
- **Implements:** Context switching
- **Status:** ❌ Undocumented

### `consciousness/ecology/entity_logic.py`
- **Purpose:** Entity behavior logic
- **Documented by:** `docs/specs/self_observing_substrate/entity_behavior_specification.md`
- **Implements:** Entity activation and behavior
- **Status:** ✅ Fully documented

### `consciousness/personas/solana-degen-investor/update_consciousness.py`
- **Purpose:** Updates consciousness for solana-degen-investor persona
- **Documented by:** `consciousness/personas/solana-degen-investor/WORKFLOW.md`
- **Implements:** Persona-specific consciousness updates
- **Status:** ⚠️ Partially documented

---

# 9. MCP Server (`mcp/`)

### `mcp/consciousness_server.py`
- **Purpose:** MCP (Model Context Protocol) server for consciousness tools
- **Documented by:**
  - `mcp/README.md`
  - `mcp/IMPLEMENTATION_SUMMARY.md`
- **Implements:** MCP tool server, consciousness query tools
- **Status:** ✅ Fully documented

---

# 10. Root-Level Test Scripts (Temporary/Debug)

These are test scripts that should be reviewed for archiving or deletion:

### `test_*.py` (Various)
- **Purpose:** Various integration and system tests
- **Status:** 🧪 Test/Temporary
- **Action needed:** Review and consolidate into `tests/` directory

Notable test scripts:
- `test_consciousness_system_live.py` - Live system testing
- `test_consciousness_v2_real_graph.py` - V2 engine with real graph
- `test_graph_counts.py` - Graph node/link counting
- `test_graph_names.py` - Graph name verification
- `test_n1_ingestion.py` - N1 ingestion testing
- `test_n2_ingestion.py` - N2 ingestion testing
- `test_n3_ingestion.py` - N3 ingestion testing
- `test_phase3_retrieval.py` - Phase 3 retrieval testing
- `test_result_format.py` - Result format verification
- `test_routing_*.py` - Various routing tests
- `test_vector_*.py` - Vector/embedding tests
- `test_websocket_*.py` - WebSocket tests

---

# 11. Temporary Scripts (Should Be Archived)

### `temp_*.py` (Various)
- **Purpose:** Temporary debugging/fix scripts
- **Status:** 🧪 Test/Temporary
- **Action needed:** Archive or delete after verification

Notable temp scripts:
- `temp_check_actual_nodes.py`
- `temp_manual_process_current.py`
- `temp_verify_link_fix.py`

---

# 12. Verification & Debugging Scripts

### `verify_*.py` (Various)
- **Purpose:** System verification scripts
- **Status:** 🧪 Test/Temporary
- **Action needed:** Move to `tools/` or `tests/`

Notable verification scripts:
- `verify_live_routing.py` - Live routing verification
- `verify_n2_data.py` - N2 data verification
- `verify_parser_test.py` - Parser verification

---

# Gap Analysis

## Scripts Needing Documentation

### High Priority (Core Functionality)
1. `orchestration/control_api.py` - REST API specification needed
2. `orchestration/websocket_server.py` - WebSocket protocol specification needed
3. `orchestration/engine_registry.py` - Registry pattern documentation needed
4. `orchestration/consciousness_file_watcher.py` - File watching spec needed
5. `orchestration/code_substrate_watcher.py` - Code monitoring spec needed
6. `consciousness/ecology/context_manager.py` - Context switching spec needed

### Medium Priority (Utilities)
1. `start_websocket_server.py` - Startup documentation needed
2. `orchestration/orchestration/websocket_broadcast.py` - Broadcasting spec needed
3. `orchestration/custom_claude_llm.py` - LLM integration docs needed

### Low Priority (Consolidation Needed)
1. Various test scripts in root - Move to `tests/`
2. Various temp scripts - Archive or delete
3. Various verify scripts - Consolidate to `tools/`

---

## Documentation Without Clear Implementation

Some docs reference implementations that may not exist or are incomplete:
1. `docs/specs/operational_safety_architecture.md` - Implementation status unclear
2. `docs/specs/self_healing_architecture.md` - Partially implemented in guardian.py
3. `docs/specs/yearning_driven_traversal_*.md` - Implementation status unclear

---

# N2 Graph Migration Plan

This map is designed to facilitate conversion to N2 (organizational) graph structure:

**Target Structure:**
```
(Code {
  name: "consciousness_engine.py",
  file_path: "orchestration/consciousness_engine.py",
  language: "python",
  purpose: "Main consciousness heartbeat loop"
})
-[:IMPLEMENTS]->
(Document {
  name: "Minimal Mechanisms Philosophy",
  file_path: "docs/specs/consciousness_engine_architecture/MINIMAL_MECHANISMS_PHILOSOPHY.md",
  document_type: "spec"
})
```

**Benefits of N2 Migration:**
- Query: "Which docs need implementation?"
- Query: "Which scripts are undocumented?"
- Query: "Show me all scripts implementing the consciousness engine spec"
- Automatic gap detection
- Living documentation map

---

# Maintenance Notes

**When adding new scripts:**
1. Add entry to appropriate section
2. Link to governing documentation
3. Mark status (✅ ⚠️ ❌ 🔧 🧪)
4. Update gap analysis if needed

**When creating new documentation:**
1. Update existing script entries
2. Check for undocumented scripts that now have specs

**Regular review cadence:**
- Weekly: Update status of in-progress docs
- Monthly: Archive/delete temp scripts
- Quarterly: Full gap analysis review

---

**Map Maintained By:** Felix "Ironhand" (Engineer)
**Next Review:** 2025-10-27
**Format Version:** 1.0
