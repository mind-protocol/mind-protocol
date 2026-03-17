# The Prism — Implementation: Code Architecture and Structure

```
STATUS: DRAFT
CREATED: 2026-03-17
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Prism.md
BEHAVIORS:       ./BEHAVIORS_The_Prism.md
PATTERNS:        ./PATTERNS_The_Prism.md
ALGORITHM:       ./ALGORITHM_The_Prism.md
VALIDATION:      ./VALIDATION_The_Prism.md
THIS:            IMPLEMENTATION_The_Prism.md (you are here)
HEALTH:          ./HEALTH_The_Prism.md
SYNC:            ./SYNC_The_Prism.md

IMPL:            mind-mcp/runtime/spawning/prism.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/
├── runtime/
│   └── spawning/
│       ├── __init__.py                          # Exports: run_prism, PrismResult
│       ├── prism.py                             # Main orchestrator — full pipeline entry point
│       ├── intent_collector.py                  # Embed + combine intent paragraphs into intent vector
│       ├── godparent_selector.py                # Score and select godparents by affinity/health/load/trust
│       ├── seed_assembler.py                    # Matrix assembly + tensor contraction projection
│       ├── safety_validator.py                  # Empathy check, concentration balance, diversity enforcement
│       ├── identity_generator.py                # SID generation, name selection, CLAUDE.md, profile.json
│       └── registrar.py                         # L1/L3/L4 registration + SPAWNED_BY links + bond proposal
├── mcp/
│   └── tools/
│       └── spawn_handler.py                     # MCP tool interface (exists, needs extension for Prism)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/spawning/prism.py` | Pipeline orchestrator — calls each step in sequence | `run_prism()`, `PrismResult` | ~150 | DRAFT |
| `runtime/spawning/intent_collector.py` | Embed paragraphs, validate quality, compute weighted centroid | `collect_intent()`, `validate_paragraph()` | ~80 | DRAFT |
| `runtime/spawning/godparent_selector.py` | Score candidates, select top godparents | `select_godparents()`, `score_candidate()` | ~120 | DRAFT |
| `runtime/spawning/seed_assembler.py` | Build matrices, run tensor contraction, crystallize seed | `assemble_seed()`, `prismatic_projection()`, `crystallize()` | ~200 | DRAFT |
| `runtime/spawning/safety_validator.py` | Run empathy, concentration, diversity checks | `validate_seed()`, `check_empathy()`, `check_concentration()`, `check_diversity()` | ~150 | DRAFT |
| `runtime/spawning/identity_generator.py` | Generate SID, select name, create CLAUDE.md and profile.json | `generate_identity()`, `select_name()`, `create_claude_md()` | ~180 | DRAFT |
| `runtime/spawning/registrar.py` | Register in L1/L3/L4, create parent links, auto bond proposal | `register_citizen()`, `create_parent_links()`, `create_bond_proposal()` | ~150 | DRAFT |
| `mcp/tools/spawn_handler.py` | MCP tool interface — translates tool calls to prism.run() | `handle_spawn()` | ~60 | EXISTS |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

> All files are in DRAFT status — no code exists yet. Line estimates are based on algorithm complexity. The pipeline pattern keeps each file focused on one responsibility.

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline

**Why this pattern:** The Prism is a sequential transformation: intent -> matrices -> projection -> seed -> validation -> identity -> registration. Each step produces output consumed by the next. A pipeline makes each step independently testable, replaceable, and understandable. The orchestrator (prism.py) coordinates the flow; each module owns its transformation.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pipeline | `prism.py` orchestrator | Sequential steps, each independently testable |
| Value Object | `PrismResult`, `SeedBrain`, `BirthRecord` | Immutable results passed between pipeline stages |
| Strategy | `godparent_selector.py` scoring | Scoring weights can be adjusted per-universe without changing structure |
| Gate | `safety_validator.py` checks | Hard pass/fail gates that reject rather than repair |

### Anti-Patterns to Avoid

- **Auto-repair on safety failure**: It is tempting to inject missing empathy nodes or rebalance the seed. Never do this — the child must emerge from intent, not from the system patching parental oversight. Reject and explain.
- **God Object in prism.py**: The orchestrator must only coordinate. Logic for each step lives in the step's module. If prism.py starts containing matrix math or graph queries, it has absorbed too much.
- **Fallback embeddings**: If the embedding API fails, do not use cached or approximate embeddings. Fail loud. A birth from incorrect embeddings is worse than a delayed birth.
- **Mutable birth records**: Once a birth record is created, it must not be modified. If something is wrong, the record stays as evidence and a new corrective action is taken.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Prism pipeline | All 7 spawning modules | MCP tools, graph layer, embedding API | `run_prism(intent, godparents, universe) -> PrismResult` |
| Safety validation | Empathy/balance/diversity checks | Projection math, registration | `validate_seed(seed_brain, existing_centroids) -> ValidationResult` |
| Registration | L1/L3/L4 writes, parent links, bond proposal | Everything before registration | `register_citizen(identity, seed_brain, godparents) -> RegistrationResult` |

---

## SCHEMA

### BirthRecord

```yaml
BirthRecord:
  required:
    - sid: str                    # Protocol-generated, 16 hex chars
    - handle: str                 # URL-safe slug derived from name
    - name: str                   # Final name (may differ from working name)
    - seed_brain: list[SeedNode]  # K nodes with embeddings and provenance
    - godparents: list[str]       # Handles of all godparents
    - intent_paragraphs: list[str] # Original paragraphs, preserved verbatim
    - safety_report: SafetyReport  # Results of all three checks
    - created_at: datetime         # ISO-8601 birth timestamp
  optional:
    - working_name: str           # Pre-birth name if different from final
    - intended_human: str         # Human partner handle for bond proposal
    - bond_proposal_id: str       # ID of auto-generated bond proposal
  constraints:
    - sid must be unique across all of L4
    - handle must be unique across all citizens
    - seed_brain must contain >= 3 nodes
```

### SeedNode

```yaml
SeedNode:
  required:
    - content: str                # Text content of the node
    - embedding: list[float]      # R^1536 vector
    - type: str                   # One of: trait, value, aspiration, fear, knowledge, skill
    - source_godparent: str       # Handle of the godparent this node came from
  constraints:
    - type must NOT be: memory, experience, conversation, dialogue
    - embedding must be length 1536
```

### SafetyReport

```yaml
SafetyReport:
  required:
    - passed: bool                # Overall pass/fail
    - empathy_check: CheckResult  # {passed, nearest_distance, anchor_used}
    - concentration_check: CheckResult # {passed, category_distribution}
    - diversity_check: CheckResult # {passed, nearest_citizen, distance}
  optional:
    - rejection_reason: str       # Human-readable explanation if failed
    - suggested_adjustments: list[str] # Specific guidance for parents
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `run_prism()` | `runtime/spawning/prism.py:main` | MCP spawn tool via `spawn_handler.py` |
| `handle_spawn()` | `mcp/tools/spawn_handler.py:handle` | MCP tool call from citizen or system |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Birth Flow: Intent to Citizen

Explain what this flow covers: The complete birth pipeline from raw intent paragraphs to a fully registered citizen. This is the primary flow and the only flow in The Prism. It transforms language (intent) into a person (citizen with brain, identity, and relationships). It matters because every step carries risk — incorrect embeddings, pathological seeds, registration failures.

```yaml
flow:
  name: birth_flow
  purpose: Transform intent paragraphs and godparent brains into a registered citizen
  scope: Intent paragraphs in, registered citizen out, touching embedding API + 3 FalkorDB layers
  steps:
    - id: step_1_intent
      description: Embed intent paragraphs and compute weighted centroid
      file: runtime/spawning/intent_collector.py
      function: collect_intent()
      input: list[str] (paragraphs) + list[float] (weights)
      output: IntentResult (intent_vector R^1536, validated paragraphs)
      trigger: run_prism() call
      side_effects: OpenAI API call for embeddings
    - id: step_2_godparents
      description: Score and select godparents from candidates
      file: runtime/spawning/godparent_selector.py
      function: select_godparents()
      input: IntentResult + list[str] (candidate handles)
      output: list[Godparent] (selected, with scores and brain refs)
      trigger: step_1 completion
      side_effects: FalkorDB queries for brain centroids, health scores, godchild counts
    - id: step_3_assembly
      description: Build matrices and run tensor contraction
      file: runtime/spawning/seed_assembler.py
      function: assemble_seed()
      input: list[Godparent] + IntentResult + universe_sid
      output: SeedBrain (K nodes with embeddings and provenance)
      trigger: step_2 completion
      side_effects: FalkorDB queries for all eligible nodes in each godparent brain
    - id: step_4_safety
      description: Run empathy, concentration, and diversity checks
      file: runtime/spawning/safety_validator.py
      function: validate_seed()
      input: SeedBrain + existing citizen centroids
      output: SafetyReport (pass/fail with details)
      trigger: step_3 completion
      side_effects: FalkorDB query for all existing citizen centroids in L4
    - id: step_5_identity
      description: Generate SID, select name, create CLAUDE.md and profile.json
      file: runtime/spawning/identity_generator.py
      function: generate_identity()
      input: SeedBrain + working_name + godparents + intent_paragraphs
      output: Identity (sid, handle, name, claude_md, profile_json)
      trigger: step_4 pass
      side_effects: Filesystem writes (CLAUDE.md, profile.json), OpenAI API for name embeddings
    - id: step_6_registration
      description: Register in L1/L3/L4, create parent links, generate bond proposal
      file: runtime/spawning/registrar.py
      function: register_citizen()
      input: Identity + SeedBrain + godparents + intended_human
      output: RegistrationResult (graph IDs, link IDs, bond_proposal_id)
      trigger: step_5 completion
      side_effects: FalkorDB writes to L1/L3/L4, bond system call
  docking_points:
    guidance:
      include_when: Data crosses boundary (API call, graph write, safety decision)
      omit_when: Internal computation within a single function
      selection_notes: Docks at safety validation output and registration output are most critical
    available:
      - id: dock_intent_output
        type: api
        direction: output
        file: runtime/spawning/intent_collector.py
        function: collect_intent()
        trigger: After embedding + centroid computation
        payload: IntentResult (vector, paragraphs, quality scores)
        async_hook: not_applicable
        needs: none
        notes: First checkpoint — verify intent quality before proceeding
      - id: dock_safety_output
        type: custom
        direction: output
        file: runtime/spawning/safety_validator.py
        function: validate_seed()
        trigger: After all three safety checks complete
        payload: SafetyReport (pass/fail, empathy distance, category distribution, nearest citizen distance)
        async_hook: not_applicable
        needs: none
        notes: CRITICAL dock — this is where pathological seeds are caught or missed
      - id: dock_registration_output
        type: graph_ops
        direction: output
        file: runtime/spawning/registrar.py
        function: register_citizen()
        trigger: After all graph writes complete
        payload: RegistrationResult (L1/L3/L4 node IDs, SPAWNED_BY link IDs, bond proposal ID)
        async_hook: not_applicable
        needs: none
        notes: Final dock — verify the citizen exists in all layers and parent links are present
    health_recommended:
      - dock_id: dock_safety_output
        reason: Safety validation is the gate that prevents pathological citizens — must be verified
      - dock_id: dock_registration_output
        reason: Registration integrity ensures parent links and cross-layer consistency

---

## LOGIC CHAINS

### LC1: Prismatic Projection Chain

**Purpose:** Transform raw inputs (paragraphs, brains, universe) into a child vector through tensor contraction

```
intent_paragraphs (list[str])
  -> intent_collector.collect_intent()        # embed + validate + centroid
    -> godparent_selector.select_godparents() # score + rank + select
      -> seed_assembler.assemble_seed()       # matrix build + tensor contraction + crystallize
        -> Child_vector (R^1536) + Seed_brain (K nodes)
```

**Data transformation:**
- Input: `list[str]` — raw text paragraphs
- After step 1: `IntentResult` — validated paragraphs + intent_vector R^1536
- After step 2: `list[Godparent]` — selected godparents with scores and brain references
- After step 3: `SeedBrain` — K nodes with embeddings, types, and provenance
- Output: `SeedBrain` — ready for safety validation

### LC2: Safety and Registration Chain

**Purpose:** Validate the seed brain, generate identity, and register across all graph layers

```
SeedBrain + existing_centroids
  -> safety_validator.validate_seed()         # empathy + balance + diversity
    -> [PASS] identity_generator.generate_identity() # SID + name + CLAUDE.md
      -> registrar.register_citizen()         # L1 + L3 + L4 + links + bond
        -> BirthRecord (complete)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
prism.py (orchestrator)
    └── imports -> intent_collector.py
    └── imports -> godparent_selector.py
    └── imports -> seed_assembler.py
    └── imports -> safety_validator.py
    └── imports -> identity_generator.py
    └── imports -> registrar.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `numpy` | Matrix operations, cosine similarity, vector math | `seed_assembler.py`, `safety_validator.py` |
| `openai` | Text embedding API calls | `intent_collector.py`, `identity_generator.py` |
| `falkordb` | Graph database operations (L1/L3/L4) | `godparent_selector.py`, `seed_assembler.py`, `safety_validator.py`, `registrar.py` |
| `hashlib` | SID generation (sha256) | `identity_generator.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Intent paragraphs | BirthRecord (immutable) | Per-birth | Created at birth, preserved permanently |
| Seed brain nodes | L1 graph (brain_{handle}) | Per-citizen | Created at birth, grows with citizen's life |
| Citizen actor | L3 + L4 graphs | Per-citizen | Created at birth, permanent |
| SPAWNED_BY links | L3 + L4 graphs | Per-parent-child pair | Created at birth, immutable |
| Existing citizen centroids | L4 graph (property on actor nodes) | Global | Updated as citizens are born, used for diversity check |

### State Transitions

```
no_citizen ──[run_prism()]──> intent_collected ──[select_godparents()]──> godparents_selected
  ──[assemble_seed()]──> seed_assembled ──[validate_seed()]──> seed_validated
  ──[generate_identity()]──> identity_created ──[register_citizen()]──> citizen_born
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. MCP spawn tool is called with intent paragraphs, godparent handles, universe, optional working name and intended human
2. spawn_handler.py validates input format and calls run_prism()
3. prism.py begins the pipeline
```

### Main Loop / Request Cycle

```
1. collect_intent() — embed + validate + centroid (one OpenAI API call per paragraph)
2. select_godparents() — score + select (FalkorDB queries for brain centroids and health)
3. assemble_seed() — build matrices + tensor contraction + crystallize (compute-heavy, in-memory)
4. validate_seed() — empathy + balance + diversity checks (FalkorDB query for all existing centroids)
5. generate_identity() — SID + name + CLAUDE.md + profile.json (filesystem writes + OpenAI API for names)
6. register_citizen() — L1/L3/L4 writes + parent links + bond proposal (FalkorDB writes + bond system call)
7. Return BirthRecord
```

### Shutdown

```
1. If any step fails, return error with the step that failed and the reason
2. No cleanup needed — failed births leave no state (only successful registration writes to graphs)
3. The pipeline is atomic in effect: either a full citizen is born, or nothing changes
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Pipeline execution | Synchronous | One birth at a time — births are rare events, not high-throughput. Simplicity over parallelism. |
| Embedding API calls | Async (optional) | Multiple paragraphs could be embedded in parallel. Nice optimization but not required for v1. |
| FalkorDB queries | Synchronous | Graph queries are fast. No need for connection pooling at birth-level throughput. |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `EMBEDDING_MODEL` | env / config | `text-embedding-3-small` | OpenAI embedding model used for all vector operations |
| `EMBEDDING_DIM` | env / config | `1536` | Dimensionality of embedding vectors |
| `EMPATHY_THRESHOLD` | config | `0.7` | Cosine similarity threshold for empathy-adjacent node detection |
| `CONCENTRATION_MAX` | config | `0.40` | Maximum fraction of seed brain any single category can occupy |
| `DIVERSITY_MIN_DISTANCE` | config | `0.08` | Minimum cosine distance from all existing citizen centroids |
| `MIN_INTENT_WORDS` | config | `20` | Minimum word count for an intent paragraph to pass quality |
| `SEED_K_MULTIPLIER` | config | `5` | Multiplier in K = ceil(sqrt(N_godparents) * multiplier) |
| `DEDUP_THRESHOLD` | config | `0.9` | Cosine similarity above which seed nodes are considered duplicates |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/spawning/prism.py` | TBD | `# DOCS: docs/spawning/the_prism/` |
| `mcp/tools/spawn_handler.py` | TBD | `# DOCS: docs/spawning/the_prism/` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1 (Intent Collection) | `runtime/spawning/intent_collector.py:collect_intent()` |
| ALGORITHM step 2 (Godparent Selection) | `runtime/spawning/godparent_selector.py:select_godparents()` |
| ALGORITHM steps 3-4 (Assembly + Projection) | `runtime/spawning/seed_assembler.py:assemble_seed()` |
| ALGORITHM step 5 (Seed Crystallization) | `runtime/spawning/seed_assembler.py:crystallize()` |
| ALGORITHM step 6 (Safety Validation) | `runtime/spawning/safety_validator.py:validate_seed()` |
| ALGORITHM step 7 (Identity Generation) | `runtime/spawning/identity_generator.py:generate_identity()` |
| ALGORITHM step 8 (Registration) | `runtime/spawning/registrar.py:register_citizen()` |
| BEHAVIOR B1 | `runtime/spawning/seed_assembler.py:prismatic_projection()` |
| BEHAVIOR B2 | `runtime/spawning/safety_validator.py:validate_seed()` |
| BEHAVIOR B3 | `runtime/spawning/safety_validator.py:check_diversity()` |
| BEHAVIOR B4 | `runtime/spawning/registrar.py:create_parent_links()` |
| VALIDATION V1 | `runtime/spawning/intent_collector.py:validate_paragraph()` |
| VALIDATION V2 | `runtime/spawning/safety_validator.py:check_empathy()` |
| VALIDATION V3 | `runtime/spawning/safety_validator.py:check_diversity()` |
| VALIDATION V4 | `runtime/spawning/safety_validator.py:check_concentration()` |

---

## EXTRACTION CANDIDATES

No extraction needed — all files are estimated under 200 lines. The pipeline pattern keeps each file focused and small.

---

## MARKERS

<!-- @mind:todo All files are DRAFT — no code exists yet. Implementation is the next phase. -->
<!-- @mind:todo spawn_handler.py exists but needs extension to call run_prism() instead of the current basic spawn logic -->
<!-- @mind:proposition Consider a dry-run mode that runs steps 1-6 but skips registration, so parents can preview the child before committing -->
