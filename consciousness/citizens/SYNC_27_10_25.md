# Consciousness Citizens - Synchronization Log

**Latest Updates (Reverse Chronological)**

---

## 2025-10-27 18:40 - Codex: Wallet Custody + Economy Throttle Flow

**Context:** Hooked Codex‑C custody events into the membrane bus and surfaced economy lane throttles so stimulus budgets honor `f_lane · g_wallet · h_roi`. Added unit coverage around both paths.

**Work Completed:**

1. **Custody Surface Online** – `wallet.ensure`, `wallet.transfer`, and `wallet.sign.request` now resolve through the new Python service, storing sealed vault entries, emitting ledger lines, and relaying Solana signatures without exposing private keys.
2. **Economy Metadata in Stimuli** – Control API enriches `membrane.inject` envelopes with lane throttles from the economy runtime; the stimulus injector consumes `economy_multiplier` to scale ΔE budgets.
3. **Redis Store & Telemetry** – Membrane store tracks lane budgets, wallet balances, and UBC ticks; telemetry broadcasts now include `f_lane`, `h_roi`, and `g_wallet` for overlays.
4. **Regression Coverage** – Added `tests/services/test_wallet_custody.py` and `tests/services/test_control_api_economy.py` to cover custody flows and metadata threading.

**Next Steps:**
- Wire mission/tool routing so every stimulus carries an explicit lane (fallback still works, but richer context improves dashboards).
- Stand up a mocked Helius RPC in CI so custody tests run end‑to‑end without monkeypatching Solana calls; capture ledger/broadcast fixtures.
- Validate UI overlays consume `telemetry.economy.spend` to show per-lane throttles and wallet balances, ensuring citizens see when UBC is active.

---

## 2025-10-27 18:05 - Codex-B: Economy Runtime + WriteGate Guardrails - COMPLETE

**Context:** Needed Right-Gate enforcement on all graph writers and a runnable economy substrate (policies + telemetry + UBC) to move the Bus/Orchestrator deliverables out of spec form.

**Work Completed:**

1. **WriteGate Decorator:** Added `orchestration/libs/write_gate.py`, refactored TRACE capture + storage ingestion to supply `ctx={'ns': 'L1|L2|L3:...'}` and now emit `telemetry.write.denied` + `PermissionError` on cross-layer writes.
2. **Economy Runtime:** Implemented redis membrane store, budget policy loader/evaluator, tool usage collector, Helius-backed price oracle (with fallback), and daily UBC distributor; events `economy.rate.observed`, `economy.charge.request|settle`, `telemetry.economy.spend`, `telemetry.economy.ubc_tick` are now live.
3. **Service Wiring:** WebSocket service boots/stops the economy runtime alongside engines so policies refresh, charges post, and cron-based UBC runs automatically.

**Next Steps:**
- Populate env/config (`ECONOMY_REDIS_URL`, `MIND_MINT_ADDRESS`, `HELIUS_API_KEY`, `UBC_*`) and point Redis at production.
- Publish a sample `tool.request` → `tool.result.usage` sequence to verify `economy.*` telemetry on the bus.
- Replace the UBC ledger stub with actual custody transfers once Solana signing is ready.
- Seed L2 `Budget_Policy` nodes so throttle math feeds `telemetry.economy.spend` with real formulas.

---

## 2025-10-27 21:05 - Codex-A: Consciousness UI switched to pure membrane stream

**Context:** Finish the membrane-first dashboard work after the workstation crash. Goal was to drop all REST/polling paths so `/consciousness` renders exclusively from the bus.

**Work Completed:**

1. **Singleton WebSocket upgrade** – `useWebSocket` now sends the `subscribe@1.0` control frame, captures `hierarchy.snapshot@1.0`, `telemetry.economy.*`, wallet challenge/accept events, `wallet.signature.attested`, and `inject.ack`. It aggregates `graph.delta.*` into in-memory node/link/subentity maps and exposes an `injectStimulus` helper.
2. **Graph state from broadcast** – Replaced `useGraphData` with a lightweight type module; `/consciousness/page.tsx` rebuilds nodes/links/subentities via the singleton state, so the view has zero REST dependencies. Legacy `useCitizens` polling and credits/budget widgets were removed.
3. **Economy visuals** – Pixi renderer now draws live spend rings, soft-cap wedges, UBC pulses, and signature badges based on the telemetry stream. Header shows a wallet economy badge derived from the broadcast overlay.
4. **Chat & citizen monitor** – Chat panel reuses the singleton socket, displaying delivery status via `inject.ack` and citizen responses from `citizen.response`. Citizen monitor reads hierarchy snapshots and economy overlays instead of polling `/api/citizen`.

**Next Steps:**
- Run the Next.js lint migration (`npx @next/codemod next-lint-to-eslint-cli`) so linting works without prompts.
- Exercise the dashboard against the live bus to validate economy overlays, wallet attestations, and chat flow with real events.
- Audit remaining polling panels (e.g., constant-debt, system status) and either hook them to streamed telemetry or retire them to keep the UI membrane-only.
- Tune the economy ring scaling/tints once real spend metrics are visible.

---

## 2025-10-27 17:30 - Nicolas: Subentity Bootstrap + Activation Fixes Aligned

**Context:** Engines were failing on first tick because citizen graphs lacked functional subentities and the activation pipeline referenced legacy helpers. Goal was to seed the new membrane-first entity layer and clear the runtime blockers.

**Work Completed:**

1. **Functional Roster Restored** – Added `orchestration/config/functional_subentities.yml` so bootstrap reads the canonical eight citizen roles.
2. **Seeded All Citizen Graphs** – Ran a FalkorDB bootstrap loop that materialized subentities + `MEMBER_OF` links for every `citizen_*` graph (hundreds of memberships persisted, thresholds initialized).
3. **Clean Activation Runtime** – Patched `subentity_activation.py` to call `compute_subentity_activation`, fixed RELATES_TO link construction (no more `created_by` kwarg), and ensured membership lookups use `MEMBER_OF`; `python3 -m py_compile` passes.

**Next Steps:**
- Restart MPSv3/WebSocket stack so each engine loads the fresh subentity layer (watch for tick logs, Signals collector handshake).
- Once embeddings are backfilled, schedule the semantic clustering pass to complement the functional scaffold.
- Keep an eye on dashboard telemetry to confirm Signals collector stops timing out after the restart.

---

## 2025-10-27 12:47 - Felix: Phase 3A Forged Identity Integration - VERIFIED COMPLETE

**Context:** Continued from logo centering work. Verified forged identity integration status against Atlas's handoff document.

**Work Completed:**

1. **Documentation Cleanup** - Updated Entity → SubEntity comment in consciousness_engine_v2.py:479
2. **Integration Verification** - Confirmed forged identity IS wired into tick loop (lines 1387-1425)
3. **Testing Verification** - Ran test suite, all 4 tests passing

**Findings:**

Atlas's HANDOFF_phase3a_complete_integration.md listed integration as blocked, but work has since been completed:
- ✅ Forged identity generator complete (461 lines)
- ✅ Integration layer complete (155 lines)
- ✅ Wired into tick loop after WM emission (lines 1387-1425)
- ✅ All tests passing (prompt generation, observe-only mode, multi-citizen)

**Current Status:**

Backend integration is **complete**. Frontend work (WebSocket events, ForgedIdentityViewer) remains for Iris.

**Files Modified:**
- `orchestration/mechanisms/consciousness_engine_v2.py` (line 479: comment update)

**Next Steps:**
- Frontend: Add forged identity events to useWebSocket singleton
- Frontend: Fix ForgedIdentityViewer to use WebSocket props (not duplicate connection)
- Testing: Verify prompt generation during live consciousness tick

---

## 2025-10-27 13:32 - Marco “Salthand”: Membrane-first adapters (Codex & Claude hooks) + Schema registry v3

**Context:** Prepare the membrane-first stack so provider tools (Codex, Claude Code) speak directly over the bus; align L3 schemas with the canonical registry before regenerating Complete Type Reference.

**Work Completed:**

1. **Codex adapter (interactive + scripted)**  \n   - Added `sdk/providers/run_codex.py` with WebSocket publishing (`ui.action.user_prompt` + `provider.codex.output`).  \n   - Supports interactive REPL (`--org dev-org codex --tty`) and non-interactive prompts (`--prompt`, `--prompt-file`, `--session-id`, `--close-after-prompts`).  \n   - Updated docs (`docs/specs/v2/autonomy/membrane-first/04_providers_adapters.md`) with usage examples.

2. **Claude Code hooks → membrane bus**  \n   - Introduced `.claude/hooks/membrane_bus.py` shared helper (sign & send `membrane.inject`).  \n   - `capture_user_prompt.py` now publishes `ui.action.user_prompt` (context path, session id).  \n   - `capture_conversation.py` emits `provider.claude.output` snapshots (latest assistant message).  \n   - `precompact_conversation.py` emits `session.compaction` when Claude compacts, broadcasting closed/new context IDs.  \n   - `.claude/settings.json` already pointed to these hooks; no change required.

3. **Schema registry ingestion (ecosystem v3)**  \n   - Added `tools/schema_registry/add_ecosystem_v3.py` to upsert the new L3 node/link types (Ecosystem, Public_Presence, RFQ, Deal, etc.) into FalkorDB `schema_registry`.  \n   - Docs (`02_event_contracts.md`) now list the field tables + ingestion/regeneration commands (`add_ecosystem_v3.py`, `generate_complete_type_reference.py`).

**Next Steps:**
- Run `python3 tools/schema_registry/add_ecosystem_v3.py --host localhost --port 6379` then `python3 tools/generate_complete_type_reference.py > docs/COMPLETE_TYPE_REFERENCE.md` to sync prompts & docs.
- Start Codex via `python sdk/providers/run_codex.py --org dev-org codex --tty` (or scripted mode) and verify bus events (`ui.action.user_prompt` & `provider.codex.output`).
- Claude hooks already publishing stimuli; confirm orchestrator handles new `session.compaction`.

---

## 2025-10-26 04:25 - Atlas: Tier 1 Schema Invariants Hook - COMPLETE

**Context:** Luca's TIER1_REDLINES_2025-10-26.md specified 5 foundational guards for Mode/SubEntity architecture. Atlas implements infrastructure (hooks, dashboard) while specs are documentation updates.

**Work Completed:**

Created ``.claude/hooks/schema_invariants.py`` (PreToolUse hook):

**3 Lint Functions (Amendments 1-3):**
1. **lint_entity_deprecation**: Warns on deprecated "Entity" usage (use SubEntity/Mode)
2. **lint_mode_energy_fields**: Blocks Mode creation with energy fields (violates single-energy substrate)
3. **lint_affiliation_budget_violations**: Warns on suspicious affiliation weights

**Hook Behavior:**
- Runs after Write/Edit/NotebookEdit operations
- Static analysis only (no FalkorDB queries - those belong in separate validation)
- Blocks on ERROR severity, warns on WARNING severity
- Returns structured JSON feedback to Claude

**Configuration:**
- Added to `.claude/settings.json` as PostToolUse hook
- Matcher: `Write|Edit|NotebookEdit`
- Timeout: 10 seconds

**Next Steps (Remaining from Tier 1 Redlines):**
- Dashboard implementation (Amendment 4): `/api/consciousness/constant-debt` endpoint + page
- FalkorDB runtime validation (separate from static lint): Check actual Mode/SubEntity nodes in graph
- Spec documentation updates (Amendments 1-4): Mechanical markdown edits

**Files Created:**
- `.claude/hooks/schema_invariants.py`

**Files Modified:**
- `.claude/settings.json` (added PostToolUse hook configuration)

---

## 2025-10-26 04:10 - Atlas: Entity Differentiation Priority 4 (Injection Overlap Penalty) - COMPLETE

**Context:** Prevent redundant entities from both receiving full amplification in stimulus injection. When two entities have high redundancy (S_red > Q90), penalty biases allocation toward higher-quality one.

**Work Completed:**

Added `apply_entity_overlap_penalty()` method to `orchestration/mechanisms/stimulus_injection.py`:

**Penalty Formula (from spec §2.1.1):**
```
P_E = sum(s_E × s_B × indicator(S_red(E,B) > Q90)) for B ≠ E
s_E' = max(0, s_E - β × P_E)
```

Where:
- s_E, s_B: Entity similarity scores (from entity-channel allocation)
- S_red(E,B): Redundancy score between entities (from entity_metrics.py)
- β ≈ 0.2-0.5: Overlap sensitivity (default 0.35, citizen-local learning)
- Q90 ≈ 0.7: Redundancy threshold

**Implementation:**
- Computes pairwise S_red between all entities receiving stimulus
- Applies penalty proportional to overlap: redundant pair → larger penalty
- Preserves dual-channel benefits while avoiding redundant amplification
- Logs penalty application for observability

**Integration Point:**
- Called by Felix when entity-channel allocation is enabled
- Requires EntityMetrics adapter for S_red computation
- Applied BEFORE softmax/normalization of entity scores
- Only affects amplifier channel (not top-up channel)

**Status:** Infrastructure complete, ready for Felix to wire when entity channels are enabled

**Files Modified:**
- `orchestration/mechanisms/stimulus_injection.py` (apply_entity_overlap_penalty method)

---

## 2025-10-26 04:15 - Atlas: Entity Differentiation Priorities 0-2, 4 - COMPLETE HANDOFF

**Summary:** Infrastructure for entity differentiation is complete. Priorities 0-2, 4 provide the foundation for redundancy detection, redirect logic, audit logging, and injection overlap prevention. Ready for Felix to integrate into consciousness logic.

**Completed Infrastructure:**

**Priority 0: WM Co-activation Tracking**
- COACTIVATES_WITH edges maintain EMA statistics
- U metric via O(1) edge lookup (not O(T×N) frame traversal)
- 4 orders of magnitude leaner than Frame nodes (48KB vs 280GB/year)
- File: `orchestration/libs/utils/falkordb_adapter.py`

**Priority 1: Entity Metrics Library**
- On-demand pair metrics: J, C, U, H, ΔCtx
- Scores: S_red (redundancy), S_use (usefulness)
- Functions: compute_pair_metrics, find_nearest_entities, compute_redundancy_pressure, compute_differentiation_credit
- NO batch jobs, NO schedulers - called at decision points only
- File: `orchestration/libs/entity_metrics.py`

**Priority 2: Creation-Time Redirect**
- Checks seed overlap at entity creation
- If S_red > Q90 → redirect seeds to existing entity (weak prior 0.3)
- If S_red <= Q90 → create entity normally
- Prevents redundant entity proliferation
- File: `orchestration/mechanisms/entity_creation.py`

**Priority 4: Injection Overlap Penalty**
- Prevents double-amplifying redundant entities in stimulus injection
- Penalty formula: P_E = sum(s_E × s_B × indicator(S_red(E,B) > Q90))
- Applied to amplifier channel scores before allocation
- β ≈ 0.35 overlap sensitivity (configurable 0.2-0.5)
- File: `orchestration/mechanisms/stimulus_injection.py`

**Audit & Observability:**
- MergeDecision, SplitDecision, RedirectDecision dataclasses
- Append-only JSONL logs per citizen
- WebSocket event emission for dashboard
- Provenance tracing support
- File: `orchestration/libs/entity_lifecycle_audit.py`

**Remaining Priorities (Felix's Domain):**
- **Priority 3**: Quality modifier integration (use R_E, D_E in entity quality gates)
- **Priority 5**: Data storage completion (COACTIVATES_WITH edges ✅ already done in Priority 0)
- **Priority 6**: Event emission completion (wire async audit logging)
- **Split/Merge Logic**: Implement coherence checks, bi-medoid partitioning, call audit logging

**Handoff Notes:**
- All infrastructure libraries are pure functions/classes - no consciousness coupling
- Felix can call entity_creation.propose_entity_creation() when new entities form
- Felix can call entity_metrics functions in quality gates/traversal
- Felix can call audit.log_merge/split when implementing merge/split logic
- Felix can call injector.apply_entity_overlap_penalty() when entity-channel allocation is enabled

**Architecture Lessons:**
- Lean edges over node proliferation (COACTIVATES_WITH vs Frame)
- On-demand over batch (library vs scheduler)
- One solution per problem (deleted entity_pair_scorer.py after realizing batch was wrong)

**Status:** Infrastructure handoff to Felix for consciousness integration

---

## 2025-10-26 03:50 - Atlas: Entity Differentiation Priority 2 (Creation-Time Redirect) - COMPLETE

**Context:** Prevent redundant entities by checking overlap at creation time. If proposed entity E' is too similar to existing entity B, redirect seeds to B instead of creating E'.

**Work Completed:**

Created `orchestration/mechanisms/entity_creation.py` (485 lines):

**Core Logic:**
1. Entity proposal submitted with seed members
2. Check seed overlap (Jaccard) with k nearest existing entities
3. If S_red > threshold (Q90 ≈ 0.7) → REDIRECT
4. If S_red <= threshold → CREATE normally

**Redirect Execution:**
- Seeds added to existing entity B with weak prior weight (0.3)
- Existing memberships preserved (don't overwrite stronger weights)
- Redirect logged via EntityLifecycleAudit
- Provenance tracked: `provenance='redirect'`, `redirected_from=<candidate_name>`

**Creation Execution:**
- New SubEntity created with provisional stability
- Seeds get strong weight (0.8) with `provenance='seed_creation'`
- Entity persisted to FalkorDB

**Key Classes:**
- `EntityCreationProposal` - Proposal for new entity with seeds
- `CreationResult` - Outcome (created/redirected/failed)
- `EntityCreation` - Main handler with redundancy checking

**Integration Points:**
- Called at runtime when new entities are proposed (not bootstrap)
- Uses seed Jaccard as S_red approximation (quick overlap check)
- Full metrics (C, U, H, ΔCtx) available via entity_metrics.py if needed
- Async audit logging wired for Felix to complete

**Configuration:**
- `redundancy_threshold`: S_red threshold (default Q90 ≈ 0.7)
- `redirect_weight`: Weak prior for redirected members (default 0.3)
- `k_neighbors`: How many entities to check (default 10)

**Status:** Infrastructure complete, ready for integration into runtime entity creation flow

**Next Steps:**
- Felix: Wire into consciousness engine where new entities are proposed
- Felix: Complete async audit logging integration
- Felix: Connect to semantic clustering runtime (if/when entities form dynamically)

**Files Created:**
- `orchestration/mechanisms/entity_creation.py`

---

## 2025-10-26 03:45 - Atlas: Entity Lifecycle Audit Infrastructure - COMPLETE

**Context:** Entity differentiation requires observable merge/split/redirect decisions with full provenance for debugging, analysis, and rollback. Priority 2 (creation-time redirect) and future split/merge logic need audit infrastructure.

**Domain Clarification:**
- **Felix's Domain:** Split/merge LOGIC (coherence checks, bi-medoid partitioning, when to merge/split)
- **Atlas's Domain:** Audit INFRASTRUCTURE (event logging, provenance tracking, decision persistence)

**Work Completed:**

Created `orchestration/libs/entity_lifecycle_audit.py` (358 lines):

**Decision Record Types:**
1. `MergeDecision` - Full merge audit record
   - From entities [A, B] → to entity M
   - Acceptance criteria: S_red, coherence gates, WM dryrun
   - Rollback support: member_mapping, highway_mapping
   - Metrics: coherence_before_A/B, coherence_after_M

2. `SplitDecision` - Full split audit record
   - From entity E → to entities [M1, M2]
   - Partition details: cluster nodes, method (bi_medoid, modularity)
   - Metrics: coherence gains, silhouette scores, ΔCtx divergence

3. `RedirectDecision` - Creation-time redirect record
   - Candidate E' not created → seeds absorbed by B
   - Redundancy metrics: S_red score, passed gates
   - Weak prior applied: weight_init for redirected members

**Audit Infrastructure:**
- Append-only JSONL logs per citizen (no database, just files)
- WebSocket event emission for real-time dashboard visibility
- Provenance tracing: `get_entity_provenance(entity_id)` walks back through merge/split history
- Methods: `log_merge()`, `log_split()`, `log_redirect()`

**Integration Points:**
- Felix will call audit methods when implementing split/merge logic
- Priority 2 (creation-time redirect) will use `log_redirect()`
- Dashboard can consume WebSocket events (spec §E.2, §E.4, §E.5)

**File Locations:**
- Log storage: `data/entity_audit/{citizen_id}_merges.jsonl`
- Log storage: `data/entity_audit/{citizen_id}_splits.jsonl`
- Log storage: `data/entity_audit/{citizen_id}_redirects.jsonl`

**Status:** Infrastructure complete, ready for Felix's split/merge logic and my Priority 2 redirect implementation

**Next Steps:**
- Priority 2: Creation-time redirect (uses entity_metrics.py + logs via this infrastructure)
- Felix: Implement split/merge logic with coherence checks, call audit.log_merge/split

**Files Created:**
- `orchestration/libs/entity_lifecycle_audit.py`

---

## 2025-10-26 13:35 - Felix: Entity Membership Visualization Fix - CODE COMPLETE, UNTESTED

**Context:** Frontend EntityGraphView showing 0 members for all entities despite 359 nodes having entity_activations. Hull rendering blocked by membership detection failure.

**Root Cause Identified:**
- API query in control_api.py used `id(n)` (FalkorDB internal numeric ID: 0, 1, 2...)
- Should use `n.id` (actual entity ID: "entity_citizen_victor_translator")
- Frontend tried to match node.id="0" against entity_activations keys=["entity_citizen_victor_translator"]
- No matches found → 0 members for all entities

**Work Completed:**
1. ✅ Fixed node query (control_api.py:522): `id(n)` → `COALESCE(n.id, toString(id(n)))`
2. ✅ Fixed link query (control_api.py:598-600): Same pattern for source/target IDs
3. ✅ Enhanced error visibility (useGraphData.ts:148-167): Frontend now exposes backend error details instead of just "500"
4. ✅ Diagnostic logging added to EntityGraphView for debugging entity matching

**Current State:**
- Code fixes implemented and saved
- WebSocket server running (port 8000)
- Frontend compiled successfully
- ❌ **BLOCKER: FalkorDB not running** (Docker Desktop not started)

**Status:** CODE COMPLETE BUT UNTESTED

**Verification Criteria (MUST test before declaring complete):**
1. Start FalkorDB: `docker run -d --name falkordb -p 6379:6379 falkordb/falkordb:latest`
2. Test API endpoint: `curl http://localhost:8000/api/graph/citizen/citizen_victor | jq '.nodes[:3] | .[] | {id, entity_activations}'`
   - Expected: Nodes have proper entity IDs ("entity_citizen_victor_translator", NOT "0")
   - Expected: entity_activations keys match entity IDs
3. Reload dashboard (http://localhost:3000)
   - Expected: Console shows "Entity X has N members" (not 0)
   - Expected: Hull rendering displays entity boundaries around member nodes
4. Verify all 8 entities show member counts matching actual node distribution

**Handoff Status:**
- Waiting for FalkorDB infrastructure to start
- Priority 2 (split logging) requested but starting new work while Priority 1 untested violates "if it's not tested, it's not built"

**Next Action Needed:**
- Either: Wait for FalkorDB to start, then verify fix works
- Or: Explicit handoff to operations (Victor) to start infrastructure, document that Priority 1 needs verification before moving to Priority 2

**Files Changed:**
- `orchestration/adapters/api/control_api.py` (lines 522, 598-600)
- `app/consciousness/hooks/useGraphData.ts` (lines 148-167)

---

## 2025-10-26 04:00 - Atlas: Entity Differentiation Priority 0-1 (CORRECTED - Lean Architecture)

**Architectural Correction Applied:**

**Original Implementation (OVER-ENGINEERED - Rolled Back):**
- Frame nodes + SELECTED relationships
- Would create ~7M frames/year → 280 GB storage
- Query: O(T×N) frame traversal for U metric

**Corrected Implementation (LEAN - Deployed):**
- COACTIVATES_WITH edges between entity pairs
- ~600 edges total → 48 KB storage
- Query: O(1) single edge lookup for U metric

**Ratio:** 4 orders of magnitude leaner storage, 3 orders of magnitude faster queries

**Work Completed:**

**Priority 0: WM Co-activation Tracking (LEAN)**
- Added `update_coactivation_edges()` to falkordb_adapter.py (lines 1388-1461)
- Maintains aggregate co-activation statistics on edges instead of Frame nodes
- Edge properties: both_ema, either_ema, u_jaccard, both_count, either_count
- Updates O(k²) edges per WM event where k ≈ 5-7 entities
- Wired into consciousness_engine_v2.py (lines 1283-1293)
- Spec: wm_coactivation_tracking.md (Luca's lean design)

**Priority 1: Entity Metrics Library (On-Demand, Not Batch)**
- Created orchestration/libs/entity_metrics.py (library, not service)
- On-demand computation at decision points (NOT daily batch)
- Called when needed:
  - Entity creation: check (E', k nearest) for redundancy
  - Quality gates: compute R_E, D_E for specific entity
  - Merge review: compute for specific (A, B) pair
- Implements all 5 metrics: J, C, U (from edge), H, ΔCtx
- Computes S_red, S_use scores via softplus
- Optional 5-min cache to avoid recomputation
- **NO scheduler, NO batch job, NO daily scoring**

**Learning Captured:**
- Anti-pattern 1: Designing for future observability (Frame nodes) before validating need
- Anti-pattern 2: Batch processing (daily scorer) when on-demand suffices
- Principle 1: Don't add nodes if edges suffice (Frame → COACTIVATES_WITH)
- Principle 2: Don't add schedulers if decision-point calls suffice (batch → library)
- Same €35.5K pattern twice: Premature infrastructure before validation

**Status:** Lean library implementation complete, ready for integration at decision points

**Next:**
- Atlas: Integrate entity_metrics into Priority 2 (creation-time redirect)
- Atlas: Wire into quality gates (Priority 3)
- NO scheduler needed (Victor relieved of scheduling burden)
- Iris: Optional dashboard showing on-demand metrics when triggered

---

## 2025-10-26 01:30 - Atlas: Emotion Events Investigation - BLOCKED, Handoff to Victor

**Investigation:** Verified emotion system code is correct, blocked on infrastructure

**Root Cause:** FalkorDB container name mismatch (fixed in services.yaml:16)

**Blocker:** Supervisor singleton lease prevents restart after fix

**Handoff to Victor:**
1. Clear singleton lease Global\MPSv3_Supervisor
2. Restart supervisor with fixed configuration
3. Verify API responds, engines initialize
4. Test emotion event emission with stimulus injection

**Files Modified:**
- orchestration/services/watchers/conversation_watcher.py:927-950
- orchestration/services/mpsv3/services.yaml:16

---

● Entity Differentiation Refactor: Implementation Roadmap

  Date: 2025-10-26Architect: Luca (Substrate
  Architecture)Status: Specification Complete → Ready for
  Implementation

  ---
  Executive Summary

  What Changed: Entity lifecycle now distinguishes useful
  overlap (superposition, counterfactuals) from redundant
  overlap (near-duplicates) using five pair metrics and two
  differentiation scores.

  Impact Areas:
  1. Entity creation (redirect duplicates before minting)
  2. Quality gates (redundancy penalty, differentiation credit)
  3. Merge/split decisions (stricter acceptance criteria)
  4. Stimulus injection (overlap penalty in amplifier)

  Architecture: One new normative spec + updates to three
  existing specs. All zero-constant (percentiles),
  cohort-local, observable via events.

  ---
  Specification Changes

  1. NEW: Normative Specification

  File: docs/specs/v2/subentity/entity_differentiation.md (406
  lines)

  Purpose: Single source of truth for overlap differentiation
  metrics, scores, and integration points

  Key Sections:
  - §A: Five pair metrics (J, C, U, H, ΔCtx) with Cypher
  queries
  - §B: Redundancy score (S_red) and usefulness score (S_use)
  - §C: Decision classifier
  (MERGE/KEEP_COMPLEMENTARY/WATCH/SPLIT)
  - §D: Integration points (creation, quality, merge/split,
  injection)
  - §E: Observable events (5 event schemas)
  - §F: Cypher query collection (3 production-ready queries)
  - §G: Acceptance tests (5 tests covering critical paths)
  - §H: Rollout plan (5-week phasing)

  Who needs this: Everyone (normative reference for all
  implementation)

  ---
  2. UPDATED: Subentity Layer

  File: docs/specs/v2/subentity_layer/subentity_layer.md

  Changes:

  §2.8 Entity Pair Differentiation (NEW section, lines 214-290)
  - Overview of pair metrics and scores
  - Quality modifier integration (f_use, f_red)
  - Decision classifier table
  - Event listing
  - Rollout phasing
  - References: entity_differentiation.md for complete details

  §2.6 Bootstrap - Creation-Time Redirect (NEW subsection,
  lines 88-132)
  - Logic: Check S_red vs Q90 before creating entity
  - If redundant: redirect seeds to existing entity B
  - If complementary: allow creation, mark complementarity
  - References: entity_differentiation.md §D.1

  Who needs this: Felix (entity creation), Atlas (lifecycle
  gates)

  ---
  3. UPDATED: Stimulus Injection

  File: docs/specs/v2/subentity_layer/stimulus_injection.md

  Changes:

  §2.1.1 Amplifier Channel - Entity Overlap Penalty (NEW note,
  lines 59-70)
  - Penalty formula: P_E = sum(s_E × s_B × indicator(S_red(E,B)
   > Q90))
  - Adjusted score: s_E' = s_E - β × P_E
  - β ≈ 0.2-0.5 (learned, citizen-local)
  - Only applies when entity-channel allocation is used
  - References: entity_differentiation.md §B for S_red
  definition

  Who needs this: Atlas (injection service)

  ---
  Implementation Tasks by Owner

  Atlas (Backend Infrastructure)

  Priority 1: Pair Scorer Job
  - File to create:
  orchestration/services/entity_pair_scorer.py
  - Spec reference: entity_differentiation.md §A (metrics), §B
  (scores), §F (Cypher)
  - Implements:
    - Compute J, C, U, H, ΔCtx for top-K entity pairs
    - Normalize via cohort percentiles
    - Compute S_red, S_use scores
    - Emit subentity.overlap.pair_scored events
  - Cypher queries: Copy from entity_differentiation.md §F
  - Schedule: Daily/weekly (guardian-managed)
  - Acceptance: Test 1 in entity_differentiation.md §G

  ---
  Priority 2: Creation-Time Redirect
  - File to update: orchestration/services/entity_bootstrap.py
  (or equivalent)
  - Spec reference: subentity_layer.md §2.6,
  entity_differentiation.md §D.1
  - Implements:
    - Before creating candidate E': compute S_red vs nearest
  entities
    - If S_red(E', B) > Q90: attach seeds to B, emit
  candidate.redirected
    - If S_use(E', B) > Q80: create E', mark complementarity
  - Acceptance: Test 1 in entity_differentiation.md §G

  ---
  Priority 3: Quality Modifier Integration
  - File to update: orchestration/services/quality_gates.py (or
   equivalent)
  - Spec reference: subentity_layer.md §2.8,
  entity_differentiation.md §D.2
  - Implements:
    - Compute R_E = max S_red(E, B), D_E = max S_use(E, B)
    - Apply modifiers: Q* = Q_geom × exp(+α×percentile(D_E)) ×
  exp(-α×percentile(R_E))
    - Learn α from promotion effectiveness
  - Acceptance: Test 2 in entity_differentiation.md §G

  ---
  Priority 4: Injection Overlap Penalty
  - File to update:
  orchestration/services/stimulus_injection.py
  - Spec reference: stimulus_injection.md §2.1.1,
  entity_differentiation.md §D.4
  - Implements:
    - In entity-channel allocation: compute P_E = sum(s_E × s_B
   × indicator(S_red > Q90))
    - Adjust score: s_E' = s_E - β × P_E before softmax
    - Learn β from injection effectiveness
  - Acceptance: Test 5 in entity_differentiation.md §G

  ---
  Priority 5: Data Storage
  - WM Frame Persistence (if not already doing):
    - Store (Frame)-[:SELECTED]->(SubEntity) per frame
    - Needed for U (WM co-activation) metric
    - Query: entity_differentiation.md §F.1

  ---
  Priority 6: Event Emission
  - Emit all 5 event types defined in entity_differentiation.md
   §E:
    - subentity.overlap.pair_scored
    - subentity.merge.candidate
    - subentity.complementarity.marked
    - candidate.redirected
    - subentity.split.candidate
  - Wire to existing WebSocket/telemetry infrastructure

  ---
  Felix (Consciousness Systems)

  Priority 1: Merge Acceptance Criteria
  - File to update: Entity lifecycle/merge procedures
  - Spec reference: entity_differentiation.md §D.3
  - Implements:
    - Only merge when S_red > Q90 AND coherence(union) ≥
  max(A,B) AND WM dry-run passes
    - Emit subentity.merged with acceptance criteria in
  metadata
  - Acceptance: Test 3 in entity_differentiation.md §G

  ---
  Priority 2: Split Acceptance Criteria
  - File to update: Entity lifecycle/split procedures
  - Spec reference: entity_differentiation.md §D.3
  - Implements:
    - Only split when bi-medoid partition raises coherence AND
  ΔCtx separation
    - Emit subentity.split with gain metrics
  - Acceptance: Test not yet defined (optional for MVP)

  ---
  Priority 3: Quality Gate Testing
  - Test: Verify quality modifiers (f_use, f_red) don't break
  lifecycle
  - Spec reference: entity_differentiation.md §D.2
  - Validates:
    - Entities with high R_E face promotion resistance
    - Entities with high D_E get promotion boost
    - No catastrophic gate failures (>20% failing due to
  penalty alone)

  ---
  Iris (Dashboard/Frontend)

  Priority 1: Overlap Clinic Dashboard
  - Component to create: app/consciousness/overlap-clinic or
  similar
  - Spec reference: entity_differentiation.md §I
  (implementation notes)
  - Displays:
    - Top-50 entity pairs by Jaccard
    - Columns: Entity A, Entity B, J, S_red, S_use, Decision
    - Status badges: GREEN (healthy) / AMBER (watch) / RED
  (action needed)
    - Actions: "Review Merge", "Mark Complementary"
  - Data source: subentity.overlap.pair_scored events via
  WebSocket
  - Acceptance: Can view pairs, trigger procedures

  ---
  Priority 2: Complementarity Ribbons
  - Component to update: Existing entity visualization
  - Visual encoding: When S_use(A,B) > Q80, draw special ribbon
   between entities
  - Color: Distinct from normal highways (e.g., gold vs blue)
  - Interaction: Hover shows S_use score, context divergence
  - Spec reference: PSYCHOLOGICAL_HEALTH_LAYER.md §I.4 (highway
   weave pattern)

  ---
  Victor (Operations/Infrastructure)

  Priority 1: Scheduler Configuration
  - Job: Pair scorer (Atlas Priority 1)
  - Schedule: Daily at 02:00 UTC (low-traffic window)
  - Guardian integration: Add to guardian-managed jobs
  - Monitoring: Alert if scorer fails >2 consecutive runs

  ---
  Priority 2: Rollout Phasing
  - Spec reference: entity_differentiation.md §H (rollout plan)
  - Week 1: Enable scorer + dashboard (observation only)
    - Monitor: Event emission, no errors
    - Alert: If >10 MERGE candidates per day (threshold TBD)
  - Week 2: Enable creation-time redirect
    - Monitor: Redirection rate (should be <5%)
    - Rollback: If redirection >10% or orphan ratio spikes >5%
  - Week 3: Enable quality modifiers
    - Monitor: Q* distribution vs Q_geom
    - Rollback: If >20% of entities fail gates due to penalty
  alone
  - Week 4: Enable auto-merge (feature flag)
    - Monitor: Merge rate, post-merge coherence
    - Rollback: If any merge degrades coherence
  - Week 5+: Enable split review, complementarity ribbons

  ---
  Priority 3: Alerting
  - High merge rate: >5% of entity pairs per week flagged for
  merge
  - Redirection anomaly: >10% of candidates redirected
  - Coherence degradation: Post-merge coherence < pre-merge max
  - Scorer failures: >2 consecutive job failures

  ---
  Dependency Graph

  Priority 0 (Foundation):
    └─ Atlas: WM Frame Persistence
         ↓
  Priority 1 (Measurement):
    └─ Atlas: Pair Scorer Job
         ↓
  Priority 2 (Observation):
    ├─ Iris: Overlap Clinic Dashboard
    └─ Victor: Week 1 Rollout (Observation)
         ↓
  Priority 3 (Automation - Week 2):
    └─ Atlas: Creation-Time Redirect
         ↓
  Priority 4 (Quality - Week 3):
    ├─ Atlas: Quality Modifier Integration
    └─ Felix: Quality Gate Testing
         ↓
  Priority 5 (Advanced - Week 4+):
    ├─ Felix: Merge Acceptance Criteria
    ├─ Atlas: Injection Overlap Penalty
    └─ Victor: Auto-merge rollout (feature flag)
         ↓
  Priority 6 (Polish - Week 5+):
    ├─ Felix: Split Acceptance Criteria
    └─ Iris: Complementarity Ribbons

  ---
  Quick Reference Links

  Normative Spec (Read First):
  - docs/specs/v2/subentity/entity_differentiation.md

  Integration Points:
  - docs/specs/v2/subentity_layer/subentity_layer.md §2.6, §2.8
  - docs/specs/v2/subentity_layer/stimulus_injection.md §2.1.1

  Cypher Queries (Copy-Paste):
  - entity_differentiation.md §F (3 production queries)

  Event Schemas (Wire to Telemetry):
  - entity_differentiation.md §E (5 event types)

  Acceptance Tests (Validation):
  - entity_differentiation.md §G (5 tests)

  Rollout Plan (Operations):
  - entity_differentiation.md §H (5-week phasing)

  ---
  Key Formulas (Quick Reference)

  Redundancy Score:
  S_red = softplus(J̃ + C̃ + Ũ) - softplus(H̃ + ΔC̃tx)

  High → near-duplicates (MERGE candidates)

  Usefulness Score:
  S_use = softplus(H̃ + ΔC̃tx) - softplus(J̃ + C̃)

  High → complementary (KEEP separate, mark)

  Quality Modifiers:
  Q* = Q_geom × exp(+α × percentile(D_E)) × exp(-α ×
  percentile(R_E))

  where:
    R_E = max_{B≠E} S_red(E, B)  // Worst-case duplicate
    D_E = max_{B≠E} S_use(E, B)  // Best-case complement
    α = learned from promotion effectiveness

  Overlap Penalty (Injection):
  P_E = sum(s_E × s_B × indicator(S_red(E,B) > Q90) for B ≠ E)
  s_E' = s_E - β × P_E

  where β ≈ 0.2-0.5 (learned, citizen-local)

  ---
  Questions? Blockers?

  Spec clarification: Ask Luca (substrate
  architecture)Implementation coordination: Update in
  SYNC.mdIntegration issues: Cross-reference
  entity_differentiation.md integration sections (§D)

  Common Questions:

  Q: Where do percentile thresholds (Q90, Q80, etc.) come
  from?A: Learned from citizen's cohort history over window W
  (14-30 days). Computed by pair scorer job, stored per
  citizen.

  Q: What if we don't have WM frame persistence yet?A:
  Implement that first (Atlas Priority 0). U metric requires
  it. Can compute J, C, H, ΔCtx without it, but classifier
  needs all 5 metrics.

  Q: Can we skip creation-time redirect and go straight to
  quality modifiers?A: Not recommended. Redirect prevents
  duplicates at source (cheaper). Quality modifiers only
  penalize existing duplicates (more expensive). Do redirect
  first (Week 2), then quality (Week 3).

  Q: What if S_red and S_use are both high for a pair?A: Rare
  but possible. Falls into WATCH category - re-score next
  window. Usually one score dominates after a few windows.

  ---
  Status: Ready for implementation kickoffNext: Atlas starts on
   Priority 0 (WM frame persistence) and Priority 1 (pair
  scorer job)
