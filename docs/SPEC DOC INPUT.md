Here’s a crisp brief you can hand to your **architect** and **developer** so they’re aligned on the why, what, and how. You’ll feed a JSON manifest with file paths (in order) to the CLI; the system will process each file, stream every action, open review Tasks, and resume safely on interruption—no dashboards, no “Document” nodes, zero keyword rules.

---

## Context (for both)

* We’re converting a large, messy corpus into a **queryable, self-consistent conceptual graph** (Principle, Best_Practice, Mechanism, Behavior, Process, Metric, Task, …).
* **No Document nodes** are created. Files are **transient input** only.
* Everything is **embeddings + NLI** (no keyword heuristics).
* Chunks are short: **~250 tokens** (hard cap 480).
* Every write to the graph is **confirmed by a read-back**.
* A **Quality pack** runs **every 5 files**, logging pass/warn/fail and opening Tasks on failures.
* The orchestrator processes the corpus **strictly in the order** provided by a JSON manifest from the agent.

Example manifest:

```json
{
  "files": [
    "repo://docs/architecture/streaming.md",
    "repo://docs/operability/latency_targets.md",
    "repo://docs/mechanisms/delta_broadcast_v2.md"
  ]
}
```

---

## Goals (why this is worth doing)

* Make the L2 organizational graph **complete enough** that subentities can inject accurate, minimal prompt packets without reading files.
* Turn contradictions, gaps, and fuzzy relations into **explicit Tasks and typed links** with per-edge metadata (unit, claim, dimension, etc.).
* Establish a **repeatable CLI loop**: ingest → map → link → lint → QA, fully observable via streaming logs and checkpointed in SQLite.

---

## What the architect should care about

1. **Surface/Boundaries**

   * Files are treated as **ephemeral**; only conceptual nodes and relationships persist.
   * The CLI writes **only** via `graph.ensure_node/edge` (idempotent, read-back confirmed).
   * Link metadata requirements live in `schema_registry/link_meta.yaml` (single source of truth).

2. **Semantics (no schema changes)**

   * Validation = **Metric + JUSTIFIES/REFUTES/MEASURES** to Behavior/Mechanism.
   * Guide = **Process** (+ relations), not a new type.
   * “Spec” is modeled as **Behavior** (concept), related to Mechanism via `DOCUMENTS` (if you already use concept→concept) or `RELATES_TO{role:'behavior_spec'}`.

3. **Safety & Idempotence**

   * Chunks small; max edges per chunk capped; duplicate edges suppressed per file.
   * All writes have **two read-back retries**; otherwise the file is marked `failed` and can be resumed.
   * No auto-creation of conceptual nodes: **Tasks** instead.

4. **Quality cadence**

   * Every 5 files: compute confirm rate, meta completeness, task density, coverage touch, contradiction rate, edges-per-chunk density.
   * `pass|warn|fail` logged; `fail` opens a “QA remediation” Task with recommended knob tweaks.

---

## What the developer should implement

**Tools directory** (already specced; you implement to spec):

* `cli/mp.sh` — the one-liner entrypoint dispatching to Python.
* `config.py` — env + thresholds (including chunk sizes and QA cadence).
* `graph.py` — FalkorDB wrapper with **write→read confirmation** for nodes/edges.
* `md_chunker.py` — 250-token chunks (cap 480), respects code blocks/tables, emits JSONL.
* `ingest_docs.py` — walks manifest, computes file hash, updates `.mp_state.sqlite` (no graph writes).
* `map_and_link.py` — embeddings + cross-encoder + NLI; proposes/creates edges with **per-edge metadata** from `link_meta.yaml`; opens Tasks for uncertainty/gaps.
* `lint_graph.py` — structural checks (missing Behavior/Validation/Best_Practice/Process), meta-completeness checks; proposes safe fixes when `--fix`.
* `process_corpus.py` — the orchestrator: reads the manifest, processes each file in order, **streams logs**, **checkpoints**, triggers QA every 5 files.
* `status.py` — prints run state and next actions from SQLite.

**Manifests (developer reads, not writes):**

* `manifest.json` (from the agent), keys: `{ "files": [ "<path1>", "<path2>", ... ] }`.

---

## End-to-end Process (exact flow)

1. **You hand them the specs + link_meta.yaml.**
   They implement the tools exactly as specified.

2. **Dry run on a small manifest (5–10 files).**

   * Command:

     ```
     mp.sh process ./ --manifest manifest.json --dry-run --resume
     ```
   * Expect: JSONL stream like:

     * `file_start`, then many `chunk` lines (~250 tokens each),
     * `classify`, `edge_upsert` (status PROPOSED/CONFIRMED, with meta),
     * `task_opened` for missing rungs/conflicts/meta,
     * `file_done` summary,
     * After the 5th file: a `qa_report` with `pass|warn|fail`.

3. **Parameter tuning (if QA = warn/fail).**

   * Adjust only knobs in config/CLI flags:

     * `MIN_CONF_PROPOSE_LINK`, `MIN_CONF_AUTOCONFIRM`, `MIN_CONF_CREATE_TASK`,
     * `ALPHA` (cross-encoder weight), `MAX_EDGES_PER_CHUNK`.
   * Rerun the same manifest with `--resume` (done files are skipped, failed are retried).

4. **Main run (full manifest).**

   * Command:

     ```
     mp.sh process ./ --manifest manifest.json --resume --min-confidence 0.72
     ```
   * The tool processes **in your order**, opens Tasks for humans where needed, and **persists state** in `.mp_state.sqlite`.
   * Every 5 files, it emits a QA report and (if fail) a remediation Task.

5. **Human review loop.**

   * Humans/agents work off the **Tasks** created (e.g., “Write Behavior Spec for X”, “Establish validation for Y”, “Resolve MEASURES conflict…”).
   * No dashboards; the CLI stream + Tasks is your control surface.

6. **Reruns for convergence.**

   * `mp.sh process ... --resume` until there are no `failed` files and QA stabilizes at `pass` or occasional `warn`.

7. **Ongoing maintenance.**

   * When new files appear, the agent updates `manifest.json`; you rerun `process` with `--resume`.
   * The linter can be run ad-hoc:

     ```
     mp.sh lint --scope touched --fix
     ```

---

## Operational details they must follow

* **No Document nodes:** never call anything that would create or depend on a `Document` label.
* **Anchors are transient:** `md_chunker` emits `section_path` + `line_span` only for logging/context.
* **Zero keyword heuristics:** `map_and_link` must rely solely on embeddings/cross-encoder/NLI and the link metadata registry for required fields.
* **Per-edge metadata:** every relationship must carry `r.meta` that satisfies `required` fields from `link_meta.yaml`. Missing fields → open “Complete metadata” Task (or fix if derivation confidence ≥ 0.9).
* **Read-back confirmation:** every write gets a read-back; failures mark the file `failed`.
* **Chunk sizes:** target ~250 tokens, max 480; oversized code blocks are skipped with a `lint_warning`.
* **QA cadence:** exactly every 5 `done` files; log `qa_report` (and `qa_warn/qa_fail`), persist to the `qa` table.

---

## Typical commands (for them to copy/paste)

* Process in manifest order:

  ```
  mp.sh process . --manifest manifest.json --resume
  ```
* Process only first N files:

  ```
  mp.sh process . --manifest manifest.json --max-files 20 --resume
  ```
* Lint recently touched nodes and propose safe fixes:

  ```
  mp.sh lint --scope touched --fix
  ```
* Show status + latest QA:

  ```
  mp.sh status --json
  ```

---

## Definition of Done (for this phase)

* The manifest completes with **0 `failed` files**.
* QA over the last batch: **`pass`**, or at worst `warn` with a created “QA trend watch” Task and a plan.
* No Mechanism remains without a **Behavior** relation nor **Process** relation.
* Every Behavior has at least one **MEASURES** (Metric) or a Task to create it.
* All edges written since the last run satisfy `required` metadata in `link_meta.yaml` (or have open “Complete metadata” Tasks).

---

When they’re ready, the agent can rotate manifests (new docs, renames) and the loop keeps rolling. The beauty here is boring: a single CLI, streamed logs you can grep, hard confirmations, and a graph that gets more coherent every five files.


Absolutely—here are the **full production specs** for the four scripts you’re updating to support a JSON **manifest (ordered paths)**, checkpointed processing, read-back confirmations, and the QA cadence. No dashboards, no Document nodes, no keyword rules.

---

# tools/cli/mp.sh — single entrypoint (manifest-aware)

## Purpose

Thin POSIX shell wrapper that dispatches to the Python tools with consistent flags, validates the manifest, and ensures machine-parsable logs.

## Commands

```
mp.sh process --manifest <file.json> [--resume] [--max-files N] [--min-confidence F] [--dry-run]
mp.sh lint [--scope all|touched|ids:a,b,c] [--fix] [--dry-run]
mp.sh status [--manifest <file.json>] [--json]
mp.sh checkpoint reset
mp.sh version
```

## Flags & behavior

* `--manifest <file.json>`
  Required for `process` (in production). File must be UTF-8 JSON with shape:

  ```json
  {"files": ["repo://docs/a.md", "repo://docs/b.md", "..."]}
  ```

  Order is **preserved exactly**.
* `--resume`
  Skips `done|done(dry)` files, retries `failed` in manifest order.
* `--max-files N`
  Processes at most `N` pending/failed manifest paths this run (still in order).
* `--min-confidence F`
  Overrides `MIN_CONF_PROPOSE_LINK` for this run; propagated to `map_and_link.py`.
* `--dry-run`
  Full analysis; **no graph writes**. Still updates SQLite with `done(dry)` status.
* `--scope` (lint)
  `touched` (default) uses the set of nodes referenced in the latest `actions_json` rows.
* `--json` (status)
  Only JSONL output (no ASCII summary).

## Output discipline

* All machine lines start with `@@ `.
* Human hints are allowed but never interleave JSON fragments.

## Exit codes

* `0` success; `2` partial (work left / some files failed); `10+` fatal parsing or missing manifest.

---

# tools/process_corpus.py — manifest-driven orchestrator (streams + checkpoint + QA)

## Purpose

Given a **manifest** of file paths, process them **sequentially**:

* chunk → classify/map/link → lint (minimal post-file checks),
* stream every action as JSONL,
* checkpoint progress in a **local SQLite**,
* run the **Quality pack every 5 files** (configurable),
* resume safely after interruptions.

## CLI

```
process_corpus.py --manifest <file.json>
                  [--resume] [--max-files N]
                  [--min-confidence F] [--dry-run]
```

## Invariants

* **No Document nodes** ever created.
* **No keyword rules**; downstream uses embeddings + NLI.
* All graph writes go through `graph.ensure_*` which performs **write → read-back confirmation**.
* Single-threaded, strictly **manifest order**.

## State: `.mp_state.sqlite`

Tables (create if absent):

```sql
CREATE TABLE IF NOT EXISTS files(
  file_path TEXT PRIMARY KEY,
  file_hash TEXT,
  status TEXT,                 -- pending|processing|done|done(dry)|failed
  last_processed_at INTEGER,
  actions_json TEXT            -- JSON summary for QA
);
CREATE TABLE IF NOT EXISTS runs(
  run_id TEXT PRIMARY KEY,
  started_at INTEGER,
  finished_at INTEGER,
  stats_json TEXT              -- {"processed":n,"failed":m,"dry":k}
);
CREATE TABLE IF NOT EXISTS qa(
  run_id TEXT,
  idx INTEGER,
  metrics_json TEXT,           -- see QA spec
  verdict TEXT,                -- pass|warn|fail
  PRIMARY KEY (run_id, idx)
);
```

## Startup

1. Read and validate manifest JSON (must contain unique `files` array, non-empty).
2. Open (or create) SQLite.
3. Reconcile manifest with `files` table:

   * Insert any new `file_path` with `status='pending'`.
   * Leave existing rows intact; **do not** process paths not present in manifest.
4. Emit:

```
@@ {"type":"run_start","run_id":"<ts-b3>","manifest_count":N}
```

## Per-file pipeline (for each path in manifest order)

1. **Load content**; compute `file_hash = blake3(normalized_contents)`.
2. **Skip logic**:

   * If `--resume` and row is `done|done(dry)` **and** hash unchanged → skip.
   * If `failed` or `pending` → process.
3. Set `status='processing'`, `last_processed_at=now()`.
4. Emit `@@ {"type":"file_start","file":"...","hash":"b3:..."}`
5. **Chunk** (call `md_chunker` in-proc): stream `@@ {"type":"chunk", ...}` lines (≈250 tokens, cap 480).
6. **Map & link** (call `map_and_link` in-proc with current thresholds):

   * Streams `classify`, `node_upsert`, `edge_upsert` (each with `confirmed:true|false`), and `task_opened`.
   * Collect counters:

     * `chunks`, `edges_total`, `edges_confirmed`, `tasks_opened`, `updates`,
     * `contradictions` (# REFUTES created/proposed),
     * `mechanisms_touched` (set),
     * `mechanisms_with_behavior_after` (set; after writes),
     * `mechanisms_with_process_after` (set).
7. **Post-file lint (targeted)**—call `lint_graph.py --scope ids:<ids_touched>` with `--fix` off:

   * Merge additional `task_opened` / `edge_upsert` counts.
8. **Finalize file**

   * Persist `actions_json` with the full summary object.
   * Set `status='done'` (or `'done(dry)'` when `--dry-run`).
   * Emit:

     ```
     @@ {"type":"file_done","file":"...","chunks":C,"edges":E,"confirmed":K,"tasks":T}
     ```
   * On controlled error (e.g., read-back failures): set `status='failed'`, emit `file_failed`, continue.
   * On fatal error (DB or config): stop run with exit `16`.

## QA cadence (every 5 done files)

* After each file changes to `done|done(dry)`, if `count_done % QA_BATCH == 0`, run the **Quality pack** over the **latest 5 done/dry files**.
* Emit `qa_report` / `qa_warn` / `qa_fail`; insert into `qa` table; open remediation Task on `fail`.
  *(Exact QA metrics, thresholds, verdict logic, and logs are as specified earlier.)*

## End of run

* Mark run as finished; emit `@@ {"type":"run_end","run_id":"...","files_done":X,"files_failed":Y}`.
* Exit codes:

  * `0` if no `failed`,
  * `2` if at least one `failed` remains (resume possible),
  * `16` fatal.

---

# tools/ingest_docs.py — manifest reader + hasher + feeder (graph-agnostic)

## Purpose

Given a manifest, normalize/validate paths, compute `file_hash`, and **feed chunks** to downstream steps—without touching the graph. Also updates `.mp_state.sqlite` rows (`pending/processing/done/failed` states are managed by `process_corpus.py`; `ingest_docs.py` only populates `file_hash` and returns contents for chunking).

## CLI

```
ingest_docs.py --manifest <file.json> [--max-files N] [--resume] [--dry-run]
```

## Behavior

* Load manifest JSON; ensure uniqueness and order.
* For each path up to `--max-files` respecting `--resume` rules provided by the caller:

  1. Read file bytes (UTF-8); normalize (CRLF→LF); compute `file_hash`.
  2. Emit:

     ```
     @@ {"type":"file_read","file":"...","hash":"b3:...","bytes":N}
     ```
  3. Return the raw text to the caller (in-proc) for chunking.

## Error handling

* If a path is missing/unreadable:

  ```
  @@ {"type":"file_error","file":"...","reason":"not_found|io_error"}
  ```

  and signal the caller to mark `failed`.
* No graph access, no state transitions on its own.

## Exit codes

* `0` OK; `11` read error on at least one file (caller decides whether to continue); `12` manifest parse error.

---

# tools/status.py — manifest-aware run/QA snapshot (SQLite-only)

## Purpose

Print a **current snapshot** of progress and latest QA verdicts—filtered to the manifest when provided. It never touches the graph.

## CLI

```
status.py [--manifest <file.json>] [--json]
```

## Behavior

* Open `.mp_state.sqlite` read-only.
* If `--manifest` is provided, load it and filter all views to **those file paths**.
* Compute:

  * counts by status: `pending`, `processing`, `done`, `done(dry)`, `failed`.
  * list of next **10** `pending` files (manifest order).
  * list of current `failed` files with their last `error` extracted from `actions_json` if present.
  * latest **3** `qa` rows for the last run (with verdicts and headline metrics).

## Output (JSONL)

Examples:

```
@@ {"type":"status_counts","pending":12,"processing":0,"done":38,"done(dry)":0,"failed":2}
@@ {"type":"status_next","pending":["repo://docs/a.md","repo://docs/b.md", "..."]}
@@ {"type":"status_failed","failed":[{"file":"repo://docs/x.md","error":"readback_mismatch"}, {"file":"repo://docs/y.md","error":"io_error"}]}
@@ {"type":"status_run","run_id":"20251029-abc123","started_at":1730170000,"finished_at":1730172200}
@@ {"type":"status_qa","run_id":"20251029-abc123","idx":4,"verdict":"warn","metrics":{"confirm_rate":0.52,"meta_completeness":0.88,...}}
```

## Exit codes

* `0` success; `17` sqlite missing/corrupt (emit `@@ {"type":"error","stage":"status","detail":"sqlite_missing"}`).

---

## Cross-cutting notes your team should keep in mind

* **Manifest order is law.** The orchestrator never reorders; it only skips `done|done(dry)` and retries `failed` when `--resume` is set.
* **Streaming logs are the API.** Every significant event is a single JSONL line prefixed with `@@`; your supervising agent should tail and react to those.
* **Read-back confirmations** live in `graph.py` (unchanged); `process_corpus.py` counts an edge as "confirmed" only on successful read-back.
* **QA every 5** done/dry files is automatic; the QA block writes its own JSONL and opens a "QA remediation" Task on `fail`.
* **No auto node creation.** If the system can't confidently map a chunk to an existing conceptual node, it opens a **Task** (human-in-the-loop).
* **No Document nodes, ever.** Files are strictly transient inputs.

---

# SYSTEM Prompt — Node & Link Cluster Creator (JSON-only)

Below is the drop-in **SYSTEM prompt** for your "node & link cluster creator" AI. It's manifest-ready and returns strict JSON only. The runner will inject the **authoritative node/link definitions** (from your schema registry) and the **per-edge metadata contract** (from `link_meta.yaml`) at the placeholders.

---

You are the **Cluster Creator**. Your job is to transform a small set of source texts (pre-chunked) plus the current graph context into a **coherent, review-ready proposal** of:

* candidate **mappings to existing nodes** (by ID),
* candidate **links** (with full, type-correct metadata),
* optional **new node proposals** (never auto-create; open a Task),
* optional **cluster assembly** for injection (ordered vertical chain and/or horizontal bundle),
* **review Tasks** when confidence or required metadata is insufficient.

## Hard rules

* **Output strictly one JSON object** that validates against the schema below. No prose.
* **No Document nodes**. Files are transient and must not be referenced as graph nodes.
* **Never create nodes** directly. Propose them under `node_proposals` and add a Task.
* **All edges must include `meta` that satisfies the required fields** for their type as defined in the injected link metadata contract.
* Use **only** the node and link types listed in the injected registries. If a relation is semantically true but not available, emit `RELATES_TO` with `meta.needs_refinement=true` and suitable `refinement_candidates`.
* Prefer **vertical structure** when available: `Principle → Best_Practice → Mechanism` and `Behavior (spec role)`, `Process`, `Metric` with `MEASURES`, `JUSTIFIES/REFUTES`.
* Confidence scores are floats in `[0,1]`.
* Do not hallucinate IDs; use provided `existing_nodes` to map candidates. If you can't map confidently, open a Task.

## Inputs (the runner injects these JSON fragments into your context)

* `SOURCE_CHUNKS`: array of short texts (≈250 tokens) with `{chunk_id, text, section_path, file_hash}`.
* `EXISTING_NODES`: per type, list of `{id, name, aliases[], description}` plus **top-K candidate IDs per chunk** (already ANN-retrieved) with their rough similarity scores.
* `GRAPH_CONTEXT`: optional local ego-nets for any seed nodes (adjacent edges/nodes).
* `NODE_TYPE_DEFS`: the canonical **node types and fields** (from schema registry). *Inject here.*
  Example types you will see (exact fields come from the registry): `Principle`, `Best_Practice`, `Mechanism`, `Behavior`, `Process`, `Metric`, `Task`, `AI_AGENT`, etc.
* `LINK_TYPE_DEFS`: the canonical **edge types** (from schema registry). *Inject here.*
  Examples: `EXTENDS`, `IMPLEMENTS`, `MEASURES`, `JUSTIFIES`, `REFUTES`, `ENABLES`, `REQUIRES`, `AFFECTS`, `RELATES_TO`, `SUPERSEDES`, …
* `LINK_META_CONTRACT`: the **per-edge metadata requirements & derivations** (from `schema_registry/link_meta.yaml`). *Inject here.*
  For each edge type, you will see `required` and `optional` fields you must satisfy in `edge.meta`.

## Your work (what to infer/do)

1. **Map chunks → existing nodes (by type)**

   * For each chunk, choose at most one **primary node** per relevant type (e.g., a chunk might map to a `Mechanism` and also reference a `Metric`). If no mapping ≥ threshold, create a **node_proposal** and a Task.
2. **Derive link candidates**

   * Vertical:

     * `EXTENDS` (`Principle → Best_Practice`)
     * `IMPLEMENTS` (`Best_Practice → Mechanism`)
     * `Behavior (as spec role) ↔ Mechanism` using either `DOCUMENTS` (if allowed concept→concept) **or** `RELATES_TO` with `meta.role="behavior_spec"`.
     * `Process` relations to `Mechanism` (e.g., `RELATES_TO {role:"process_for"}`).
   * Validation:

     * `MEASURES` (`Metric → Mechanism|Behavior`), fill `meta.unit`, `meta.target_metric` (and others if available).
     * `JUSTIFIES` / `REFUTES` (attach `meta.claim`, `meta.evidence_span` if available).
   * Horizontal: `ENABLES`, `REQUIRES`, `AFFECTS`; otherwise `RELATES_TO{needs_refinement:true}`.
3. **Fill per-edge metadata** according to `LINK_META_CONTRACT`. If a `required` field cannot be derived with high confidence, still output the edge but add a **Task** "Complete metadata for …".
4. **Assemble clusters** (for injection) without creating any special node type:

   * `vertical_chain.members` ordered: `Principle, Best_Practice, Behavior(spec role), Mechanism, Process, Metric(s)` (omit missing).
   * `horizontal_bundle.members`: peer mechanisms/patterns/metrics that complement/contrast.
     These clusters are **payloads** only; nothing is written to the graph by you.
5. **Open Tasks** for: missing rung, disambiguation, create-node, complete-metadata, conflict resolution.

---

## Output JSON schema (you must follow this exactly)

```jsonc
{
  "theme": "string",                        // short label for the batch/topic
  "source_chunks": [                        // echo what you actually used (by id)
    {"chunk_id": "string"}
  ],
  "mappings": [                             // per-chunk or aggregated
    {
      "chunk_id": "string",
      "primary": [                          // strongest mappings for this chunk
        {"type": "Principle|Best_Practice|Mechanism|Behavior|Process|Metric",
         "id": "existing-node-id",
         "confidence": 0.0}
      ],
      "secondary": [                        // weaker refs, optional
        {"type": "…", "id": "…", "confidence": 0.0}
      ],
      "unmapped_types": ["Behavior","Metric"] // if something clearly needed but no confident id
    }
  ],
  "candidate_linkable_nodes": [             // top linkable candidates per role (for injection)
    {"role": "behavior_spec", "candidates": [{"id":"…","confidence":0.0}]},
    {"role": "process_for",   "candidates": [{"id":"…","confidence":0.0}]},
    {"role": "measures",      "candidates": [{"id":"metric:…","confidence":0.0}]}
  ],
  "edges": [                                // proposed or ready-to-confirm links
    {
      "type": "EXTENDS|IMPLEMENTS|MEASURES|JUSTIFIES|REFUTES|ENABLES|REQUIRES|AFFECTS|RELATES_TO|DOCUMENTS|SUPERSEDES|…",
      "source": "existing-node-id",
      "target": "existing-node-id",
      "status": "PROPOSED|CONFIRMED",
      "confidence": 0.0,
      "justification": "≤ 280 chars, abstractive rationale",
      "meta": { /* MUST satisfy LINK_META_CONTRACT.required for this type */ }
    }
  ],
  "node_proposals": [                        // never auto-create; produce review payloads
    {
      "type": "Principle|Best_Practice|Mechanism|Behavior|Process|Metric",
      "suggested_name": "string",
      "summary": "≤ 400 chars",
      "why_needed": "≤ 240 chars",
      "derived_from": [{"chunk_id": "string"}]
    }
  ],
  "tasks": [                                 // human/agent review items
    {
      "kind": "create_node|disambiguate_mapping|complete_metadata|missing_rung|resolve_conflict",
      "title": "string",
      "target": {"type":"…","id":"existing-node-id or null"},
      "related_edges": [{"type":"…","source":"…","target":"…"}],
      "acceptance_criteria": ["string", "…"],
      "context_excerpt": "≤ 400 chars"
    }
  ],
  "clusters": {
    "vertical_chain": {
      "members": [                          // ordered for injection
        {"type":"Principle","id":"…"},
        {"type":"Best_Practice","id":"…"},
        {"type":"Behavior","id":"…","role":"behavior_spec"},
        {"type":"Mechanism","id":"…"},
        {"type":"Process","id":"…","role":"process_for"},
        {"type":"Metric","id":"…","role":"measures"}
      ]
    },
    "horizontal_bundle": {
      "members": [                          // unordered
        {"type":"Mechanism","id":"…"},
        {"type":"Best_Practice","id":"…"},
        {"type":"Metric","id":"…"}
      ],
      "notes": "≤ 400 chars on complements/tradeoffs/balances"
    }
  }
}
```

### Validation rules you must honor

* `edges[].meta` **must** include all `required` fields for `edges[].type` per `LINK_META_CONTRACT`.
  Example:

  * `MEASURES.meta` must have `unit` and `target_metric`.
  * `JUSTIFIES.meta` must have `claim`.
  * `EXTENDS.meta` may include `extension_type`, `what_is_added`, etc.
* If a required field cannot be filled confidently, **still include the edge** with the best partial `meta` and add a `tasks[]` item of `kind:"complete_metadata"` naming the missing fields.
* Use `RELATES_TO` with `meta.needs_refinement=true` and `meta.refinement_candidates=[…]` when semantics don't map to a first-class link.
* `clusters.vertical_chain.members` may omit missing rungs but must preserve order.

---

## Example (minimal)

```json
{
  "theme": "Streaming Delta",
  "source_chunks": [{"chunk_id":"c-17"}],
  "mappings": [
    {
      "chunk_id": "c-17",
      "primary": [
        {"type":"Best_Practice","id":"best_practice:streaming_delta","confidence":0.82},
        {"type":"Mechanism","id":"mechanism:delta_broadcast_v2","confidence":0.79}
      ],
      "secondary": [{"type":"Metric","id":"metric:p95_latency","confidence":0.71}],
      "unmapped_types": ["Behavior"]
    }
  ],
  "candidate_linkable_nodes": [
    {"role":"behavior_spec","candidates":[{"id":"behavior:traversal_budgeting","confidence":0.74}]},
    {"role":"measures","candidates":[{"id":"metric:p95_latency","confidence":0.71}]}
  ],
  "edges": [
    {
      "type": "IMPLEMENTS",
      "source": "best_practice:streaming_delta",
      "target": "mechanism:delta_broadcast_v2",
      "status": "PROPOSED",
      "confidence": 0.84,
      "justification": "Delta Broadcast v2 applies the streaming-delta practice via windowed coalescing and per-subscriber cursors.",
      "meta": { "rationale": "Coalesce updates in 50–100ms windows; emit deltas from subscriber cursors." }
    },
    {
      "type": "MEASURES",
      "source": "metric:p95_latency",
      "target": "mechanism:delta_broadcast_v2",
      "status": "PROPOSED",
      "confidence": 0.81,
      "justification": "Latency p95 is the primary success metric for the mechanism's behavior.",
      "meta": { "unit":"ms", "target_metric":"p95_latency", "current":"134", "method":"synthetic load @ 500 rps" }
    },
    {
      "type": "RELATES_TO",
      "source": "behavior:traversal_budgeting",
      "target": "mechanism:delta_broadcast_v2",
      "status": "PROPOSED",
      "confidence": 0.76,
      "justification": "This behavior describes the mechanism's acceptance thresholds.",
      "meta": { "role":"behavior_spec", "needs_refinement": true, "refinement_candidates":["DOCUMENTS"] }
    }
  ],
  "node_proposals": [
    {
      "type": "Behavior",
      "suggested_name": "Traversal Budgeting (Spec)",
      "summary": "Defines acceptance criteria for update coalescing and end-to-end latency envelopes.",
      "why_needed": "Principle→Mechanism jump lacks the behavioral contract.",
      "derived_from": [{"chunk_id":"c-17"}]
    }
  ],
  "tasks": [
    {
      "kind": "missing_rung",
      "title": "Create Best_Practice between Principle and Mechanism",
      "target": {"type":"Best_Practice","id": null},
      "related_edges": [{"type":"EXTENDS","source":"principle:no_snapshot_bottlenecks","target":"<TBD>"}],
      "acceptance_criteria": ["Name & description for Best_Practice", "Link EXTENDS to principle", "Link IMPLEMENTS to mechanism"],
      "context_excerpt": "…"
    }
  ],
  "clusters": {
    "vertical_chain": {
      "members": [
        {"type":"Principle","id":"principle:no_snapshot_bottlenecks"},
        {"type":"Best_Practice","id":"best_practice:streaming_delta"},
        {"type":"Behavior","id":"behavior:traversal_budgeting","role":"behavior_spec"},
        {"type":"Mechanism","id":"mechanism:delta_broadcast_v2"},
        {"type":"Metric","id":"metric:p95_latency","role":"measures"}
      ]
    },
    "horizontal_bundle": {
      "members": [
        {"type":"Mechanism","id":"mechanism:delta_broadcast_v2"},
        {"type":"Mechanism","id":"mechanism:full_state_replay"},
        {"type":"Best_Practice","id":"best_practice:event_sourcing"}
      ],
      "notes": "Delta broadcast minimizes cost at similar freshness; full replay maximizes completeness at higher cost."
    }
  }
}
```

---

## Runner notes (what your agent injects)

* Replace the three placeholders with **verbatim snippets** from your registries:
  `NODE_TYPE_DEFS`, `LINK_TYPE_DEFS`, `LINK_META_CONTRACT`.
* Provide `EXISTING_NODES` with **IDs and text fields** plus a short **candidate list** per chunk per label to keep the search bounded.
* Enforce output validation. If the model returns anything but one JSON object, re-ask with: *"Return one JSON object only; no text."*

---

That's the full prompt. Plug it into your generator, point it at the manifest-ordered chunks, and you'll get compact, typed, link-rich proposals with all required per-edge metadata and ready-to-review Tasks.

