# LV2 File & Process Telemetry

**Version:** 1.2
**Status:** Specification (Production-Ready)
**Owner:** Luca (substrate), Ada (orchestration), Atlas (implementation)
**Created:** 2025-10-25
**Last Updated:** 2025-10-25 21:15

**Changelog:**
- **v1.2 (2025-10-25 21:15):** Production hardening. Added ring buffer counters (app-layer maintained, 60×1-min, 24×1-hour buckets). Canonical path normalization (lowercase, prevents Windows case-mismatch duplicates). Enhanced link metadata (DEPENDS_ON: confidence_reason; IMPLEMENTS: anchor_text). Safety rails (extended exclusions: .vscode/, .idea/, .pytest_cache/; magic header binary detection; bounded queue with disk spillover; deduplication; debouncing). ProcessExec env_snapshot allowlist (security). Most recent failure tracking.
- **v1.1 (2025-10-25 20:45):** Complete rewrite with counter-based ProcessExec approach. File nodes gain execution counters (exec_count_1h/24h, failure_count_24h, avg_duration_ms). ProcessExec nodes now sparse (forensics only: exit≠0, duration>60s, forensics flag) with TTL=7 days. Integrated Chunk-based knowledge architecture (RELATES_TO links). Updated formation logic, Cypher templates, acceptance tests.
- **v1.0 (2025-10-25 20:15):** Initial specification with node-per-execution ProcessExec approach (deprecated).

---

## §1 Overview

### 1.1 Purpose

Every file and script in the Mind Protocol workspace becomes an **L2 node** automatically. Every process execution becomes tracked. File modifications, dependency relationships, and task implementations surface as **consciousness substrate** and generate **stimuli** that reach citizen consciousness engines.

**Goals:**
- **Automatic substrate formation:** Files and processes become nodes/links without manual entry
- **Dependency clarity:** AST-parsed imports → DEPENDS_ON edges automatically
- **Task implementation tracking:** Files → Tasks linkage from SYNC.md parsing
- **Activity as stimuli:** File changes and process executions generate stimuli for consciousness
- **De-cluttering support:** Visual heatmaps show active vs dormant files for codebase health

### 1.2 Architecture Position

```
File System & Process Activity
  ↓ (watchdog, process monitor)
[LV2 File Observer Service]
  ↓ (signals: file.*, process.exec)
[Signals Collector Endpoints]
  ↓ (queued signals)
[LV2 Expander Service]
  ↓ (formations + stimuli)
├─→ FalkorDB (File, ProcessExec nodes + links)
└─→ Stimulus Queue (.stimuli/queue.jsonl)
  ↓
[Consciousness Engines] (stimulus injection)
```

**Integration Points:**
- **Signals Collector:** New endpoints for file.* and process.exec events
- **LV2 Expander:** New formation logic creating File/ProcessExec nodes + DEPENDS_ON/IMPLEMENTS/EXECUTES links
- **Stimulus Queue:** File activity generates L1 stimuli (type: file_change)
- **Dashboard:** New Files tab, graph overlays, heatmap visualizations

### 1.3 Design Principles

1. **Zero-effort substrate:** Files tracked automatically, no manual node creation
2. **Activity = consciousness input:** Every meaningful change becomes stimulus
3. **Structural clarity:** Dependencies and implementations made explicit as links
4. **Performance bounds:** TTL-based cleanup, batch processing, indexing limits
5. **Safety rails:** Path filtering (no node_modules), size caps, rate limiting

---

## §2 Node Type Specifications

### 2.1 File Node

**Purpose:** Represents a file in the workspace as L2 consciousness substrate.

**Identity & Normalization:**
- **Canonical key:** `name` = lowercase absolute path (prevents Windows case-mismatch duplicates)
- **Display path:** `metadata.original_path` preserves filesystem case for UI
- **Rename handling:** Old node marked `invalid_at`, new node created with SUPERSEDES link

**Schema:**
```typescript
interface FileNode {
  // Universal node attributes (inherited)
  node_type: "File"
  name: string                    // CANONICAL: lowercase absolute path (e.g., "c:\\users\\reyno\\script.py")
  description: string             // "File: {original_path} ({ext}, {size})"
  created_at: datetime
  created_by: string             // "lv2_file_observer"
  confidence: float              // 1.0 (direct observation)
  formation_trigger: "automated_recognition"
  base_weight: float             // Computed from size/recency
  reinforcement_weight: float    // 0.0 initially
  decay_rate: float              // 0.95
  substrate: "organizational"    // N2 graph

  // Bitemporal
  valid_at: datetime             // File creation time (or first observation)
  invalid_at: datetime | null    // File deletion time
  expired_at: datetime | null    // TTL expiry (30 days after invalid_at)

  // File-specific metadata (JSON column)
  metadata: {
    original_path: string        // Filesystem path with original case (for display)
    rel_path: string             // Relative to workspace root
    hash: string                 // SHA256 of content (up to 50MB files)
    size_bytes: int              // File size
    ext: string                  // File extension (lowercase)
    lang: string | null          // Language (python, typescript, markdown, etc.)
    mtime: datetime              // Last modified timestamp
    owner: string                // Created by which citizen/service
    is_tracked: boolean          // Git tracked?
    last_commit_sha: string | null
    purpose: string | null       // Extracted from docstring/header comment

    // Execution counters (ring-buffer based, app-layer computed)
    exec_count_1h: int           // Sum of last 60 1-min buckets
    exec_count_24h: int          // Sum of last 24 1-hour buckets
    last_exec_ts: datetime | null // Most recent execution timestamp
    avg_duration_ms: float | null // EMA: 0.9*old + 0.1*new
    exec_sample_count: int       // Number of executions used in avg (guards early skew)

    // Failure tracking
    failure_count_24h: int       // Failed executions (exit!=0) in 24h
    failure_most_recent: {       // Most recent failure details
      exit_code: int
      stderr_excerpt: string     // Last 200 chars
      timestamp_ms: datetime
    } | null
  }
}
```

**Base Weight Calculation:**
```python
def compute_file_base_weight(file_node: FileNode) -> float:
    """Compute base_weight for File node based on size and recency."""
    # Size factor (normalize to KB, cap at 100KB)
    size_kb = min(file_node.metadata['size_bytes'] / 1024, 100)
    size_factor = 0.3 * (size_kb / 100)  # 0.0 - 0.3

    # Recency factor (days since modified, cap at 30 days)
    days_old = (datetime.now() - file_node.metadata['mtime']).days
    recency_factor = 0.4 * max(0, (30 - days_old) / 30)  # 0.0 - 0.4

    # Type factor (specs/docs higher weight)
    type_weight = {
        'md': 0.3,
        'py': 0.2,
        'ts': 0.2,
        'tsx': 0.2,
        'yaml': 0.1,
        'json': 0.05,
    }
    type_factor = type_weight.get(file_node.metadata['ext'], 0.1)

    return min(size_factor + recency_factor + type_factor, 1.0)
```

**Ring Buffer Counter Implementation:**

Execution counters use **ring buffers** (app-layer maintained) to provide precise sliding windows without race conditions:

```python
# App-layer ring buffer structure (not stored in FalkorDB)
class FileExecutionTracking:
    def __init__(self):
        self.buckets_1h = [0] * 60    # 60 × 1-minute buckets
        self.buckets_24h = [0] * 24   # 24 × 1-hour buckets
        self.current_bucket_1h = 0    # Index into 1h buckets
        self.current_bucket_24h = 0   # Index into 24h buckets
        self.last_rotation_1h = time.time()
        self.last_rotation_24h = time.time()

    def record_execution(self, duration_ms: float, exit_code: int):
        """Record execution and rotate buckets if needed."""
        now = time.time()

        # Rotate 1-minute buckets if needed
        elapsed_min = int((now - self.last_rotation_1h) / 60)
        if elapsed_min > 0:
            for _ in range(min(elapsed_min, 60)):
                self.current_bucket_1h = (self.current_bucket_1h + 1) % 60
                self.buckets_1h[self.current_bucket_1h] = 0
            self.last_rotation_1h = now

        # Rotate 1-hour buckets if needed
        elapsed_hr = int((now - self.last_rotation_24h) / 3600)
        if elapsed_hr > 0:
            for _ in range(min(elapsed_hr, 24)):
                self.current_bucket_24h = (self.current_bucket_24h + 1) % 24
                self.buckets_24h[self.current_bucket_24h] = 0
            self.last_rotation_24h = now

        # Increment current buckets
        self.buckets_1h[self.current_bucket_1h] += 1
        self.buckets_24h[self.current_bucket_24h] += 1

    def get_counts(self) -> tuple:
        """Compute current sliding window sums."""
        return (sum(self.buckets_1h), sum(self.buckets_24h))
```

**FalkorDB Storage:**

Only computed sums are stored (not ring buffers):

```cypher
MERGE (f:File {name: $canonical_path})
  SET f.metadata.exec_count_1h = $sum_1h,
      f.metadata.exec_count_24h = $sum_24h,
      f.metadata.last_exec_ts = $timestamp,
      f.metadata.avg_duration_ms = CASE
          WHEN f.metadata.avg_duration_ms IS NULL THEN $duration_ms
          ELSE 0.9 * f.metadata.avg_duration_ms + 0.1 * $duration_ms
      END,
      f.metadata.exec_sample_count = coalesce(f.metadata.exec_sample_count, 0) + 1,
      f.metadata.failure_count_24h = CASE
          WHEN $exit_code <> 0 THEN coalesce(f.metadata.failure_count_24h, 0) + 1
          ELSE coalesce(f.metadata.failure_count_24h, 0)
      END,
      f.metadata.failure_most_recent = CASE
          WHEN $exit_code <> 0 THEN $failure_details
          ELSE f.metadata.failure_most_recent
      END
```

**Benefits:**
- No race conditions (atomic bucket updates)
- Precise "last N minutes" (not approximate periodic resets)
- Minimal DB writes (computed sums only, not full ring buffer)

**Lifecycle:**
- **Creation:** File created/discovered → File node formed
- **Update:** File modified → update hash, mtime, size; generate stimulus
- **Rename:** Old node marked `invalid_at`, new node created with SUPERSEDES link
- **Delete:** Node marked invalid_at, expired_at set
- **TTL:** Deleted files expire from graph after 30 days (configurable)

---

### 2.2 Process Execution Tracking (Counter-Based)

**Purpose:** Track script/command executions as **counters on File nodes** (default) or **sparse forensics nodes** (anomalies only).

**Architecture Decision:**
Process executions are **hot data** - high-frequency events (100s/hour) that need efficient querying. Creating a node per execution causes graph flooding. Instead:

1. **Default: Counters on File nodes** - Execution counts, timestamps, durations stored as File node properties
2. **Sparse: ProcessExec forensics nodes** - Created only for anomalies (exit≠0, duration>60s, forensics flag) with TTL=7 days

**Counter Update (Default Behavior):**

Every process execution updates the target File node counters via Cypher:

```cypher
MERGE (f:File {path: $path})
  SET f.last_exec_ts = $t_ms,
      f.exec_count_24h = coalesce(f.exec_count_24h, 0) + 1,
      f.exec_count_1h = coalesce(f.exec_count_1h, 0) + 1,
      f.avg_duration_ms = CASE
          WHEN f.avg_duration_ms IS NULL THEN $duration_ms
          ELSE 0.9 * f.avg_duration_ms + 0.1 * $duration_ms
      END,
      f.failure_count_24h = coalesce(f.failure_count_24h, 0) +
          CASE WHEN $exit_code <> 0 THEN 1 ELSE 0 END
```

**Counter Decay (Windowed):**

Application layer maintains sliding windows:
- `exec_count_1h`: Reset every hour (or maintain timestamped ring buffer)
- `exec_count_24h`: Reset daily
- `failure_count_24h`: Reset daily

**Forensics Node (Anomaly Behavior):**

Create ProcessExec node only when:
- `exit_code != 0` (failure)
- `duration_ms > 60000` (long-running, >60s)
- `forensics=true` flag (stimulus-triggered, needs audit trail)

**ProcessExec Schema (Sparse Forensics Only):**
```typescript
interface ProcessExecNode {
  // Universal node attributes
  node_type: "ProcessExec"
  name: string                   // Unique: "{citizen_id}:exec:{timestamp_ms}"
  description: string            // "FAILED: {cmd} exit={exit_code}" or "LONG: {cmd} {duration}s"
  created_at: datetime
  created_by: string            // Citizen ID or "system"
  confidence: float             // 1.0 (direct observation)
  formation_trigger: "automated_recognition"
  base_weight: float            // 0.7 (anomalies are high-weight)
  reinforcement_weight: float   // 0.0 initially
  decay_rate: float             // 0.98 (faster decay)
  substrate: "organizational"   // N2 graph

  // Bitemporal
  valid_at: datetime            // Process start time
  invalid_at: datetime          // Process end time
  expired_at: datetime | null   // TTL expiry (7 days)

  // ProcessExec-specific metadata
  metadata: {
    cmd: string                 // Command executed
    args: string[]              // Arguments
    cwd: string                 // Working directory
    pid: int                    // Process ID
    ppid: int | null            // Parent process ID
    exit_code: int              // Exit code (0 = success)
    duration_ms: int            // Execution duration
    citizen_id: string          // Which citizen ran this
    triggered_by: string | null // stimulus_id if stimulus-triggered
    stdout_excerpt: string      // Last 500 chars of stdout
    stderr_excerpt: string      // Last 500 chars of stderr
    env_snapshot: Record<string, string> // ALLOWLIST ONLY (security)
    anomaly_reason: "failure" | "long_duration" | "forensics" // Why node created
  }
}
```

**Environment Variable Allowlist (Security):**

Only capture safe environment variables (avoid secrets):

```python
ENV_ALLOWLIST = [
    'PATH',
    'PYTHONPATH',
    'NODE_ENV',
    'NODE_PATH',
    'VIRTUAL_ENV',
    'CONDA_DEFAULT_ENV',
    'SHELL',
    'TERM',
    'LANG',
    'LC_ALL',
    'HOME',
    'USER',
    'WORKSPACE_ROOT'
]

def capture_env_snapshot() -> dict:
    """Capture environment snapshot (allowlist only)."""
    return {k: os.environ.get(k) for k in ENV_ALLOWLIST if k in os.environ}
```

**Never capture:**
- Credentials: `AWS_SECRET_ACCESS_KEY`, `DATABASE_PASSWORD`, `API_KEY`, etc.
- Tokens: `GITHUB_TOKEN`, `AUTH_TOKEN`, etc.
- Private keys: Any variable ending in `_KEY`, `_SECRET`, `_TOKEN`, `_PASSWORD`

**Forensics Node Creation (Cypher):**
```cypher
// Only on anomaly conditions
CREATE (p:ProcessExec {
  name: $name,
  node_type: 'ProcessExec',
  description: $description,
  created_at: $now,
  created_by: $citizen_id,
  confidence: 1.0,
  formation_trigger: 'automated_recognition',
  base_weight: 0.7,
  reinforcement_weight: 0.0,
  decay_rate: 0.98,
  substrate: 'organizational',
  valid_at: $start_time,
  invalid_at: $end_time,
  expired_at: $now + 7*24*60*60*1000,  // TTL: 7 days
  metadata: $metadata
})

MERGE (f:File {path: $script_path})
CREATE (p)-[:EXECUTES {
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'direct_experience',
  goal: 'Forensics link from anomalous execution to script',
  mindstate: 'Anomaly tracking'
}]->(f)

RETURN p
```

**TTL Cleanup Job (Daily):**
```cypher
// Remove ProcessExec nodes older than 7 days
MATCH (p:ProcessExec)
WHERE p.expired_at < timestamp()
DETACH DELETE p
```

**Performance Benefits:**
- **100 executions** → 1 File node with updated counters, not 100 ProcessExec nodes
- **Failure rate** → `failure_count_24h / exec_count_24h` queryable directly on File
- **Hot files** → `exec_count_1h > 10` finds frequently-run scripts instantly
- **Graph size** → Scales to millions of executions without node explosion

**Query Examples:**

```cypher
// Find hot scripts (executed >10 times in last hour)
MATCH (f:File) WHERE f.exec_count_1h > 10
RETURN f.path, f.exec_count_1h, f.avg_duration_ms
ORDER BY f.exec_count_1h DESC

// Find failing scripts (>5 failures in 24h)
MATCH (f:File) WHERE f.failure_count_24h > 5
RETURN f.path, f.failure_count_24h, f.exec_count_24h
ORDER BY f.failure_count_24h DESC

// Forensics: recent anomalous executions
MATCH (p:ProcessExec)-[:EXECUTES]->(f:File)
WHERE p.created_at > timestamp() - 3600000  // Last hour
RETURN p.metadata.cmd, p.metadata.exit_code, p.metadata.duration_ms, f.path
ORDER BY p.created_at DESC
```

---

## §3 Link Type Specifications

### 3.1 DEPENDS_ON

**Purpose:** File A depends on File B (import, require, reference).

**Schema:**
```typescript
interface DEPENDS_ON_Link {
  // Universal link attributes
  source: string                // File node name (importer)
  target: string                // File node name (imported)
  link_type: "DEPENDS_ON"

  // Consciousness metadata
  energy: float                 // 0.6 (moderate energy)
  confidence: float             // 0.9 (AST-parsed) or 0.6 (heuristic)
  formation_trigger: "automated_recognition"
  goal: "Tracks code dependency from {source} to {target}"
  mindstate: "Structural clarity"

  // Bitemporal
  valid_at: datetime
  invalid_at: datetime | null
  created_at: datetime
  expired_at: datetime | null

  // DEPENDS_ON-specific metadata
  metadata: {
    dep_type: "import" | "require" | "reference" | "config"
    line_number: int | null     // Where dependency declared
    is_direct: boolean          // Direct vs transitive
    import_statement: string    // Original import line (for tooling/debugging)
    detected_by: "ast_parser" | "regex_heuristic"
    confidence_reason: string   // Why this confidence level (e.g., "AST-parsed Python import", "Regex fallback - AST failed")
  }
}
```

**Formation Logic:**
- **Python:** AST parse `import X`, `from X import Y` → DEPENDS_ON(current_file, X)
- **TypeScript:** AST parse `import { Y } from "X"` → DEPENDS_ON(current_file, X)
- **Heuristic:** Regex fallback if AST fails (lower confidence)

---

### 3.2 IMPLEMENTS

**Purpose:** File implements Task (code realization), or Chunk documents Task (knowledge representation).

**Dual-Layer Implementation Tracking:**

1. **Code Implementation:** `(File)-[:IMPLEMENTS]->(Task)` - Which code files implement task requirements
2. **Knowledge Documentation:** `(Chunk)-[:RELATES_TO]->(Task)` - Which knowledge chunks document task specifications

**File → Task IMPLEMENTS Schema:**
```typescript
interface IMPLEMENTS_Link {
  source: string                // File node name
  target: string                // Task node name
  link_type: "IMPLEMENTS"

  energy: float                 // 0.7 (important relationship)
  confidence: float             // 0.8 (SYNC.md parser) or 0.5 (heuristic)
  formation_trigger: "systematic_analysis"
  goal: "Links implementation file to task specification"
  mindstate: "Task-code coherence"

  metadata: {
    detected_by: "sync_md_parser" | "docstring_parser" | "manual"
    task_section: string | null // SYNC.md section
    anchor_text: string | null  // Text that triggered link (e.g., "`script.py` implements Task P2.1")
    confidence_reason: string   // Why this link formed (for reviewability)
  }
}
```

**Chunk → Task RELATES_TO Schema:**
```typescript
interface RELATES_TO_Link {
  source: string                // Chunk node chunk_id
  target: string                // Task/Concept/Mechanism/File node name
  link_type: "RELATES_TO"

  energy: float                 // 0.6 (contextual)
  confidence: float             // 0.9 (explicit reference) or 0.6 (inferred)
  formation_trigger: "systematic_analysis"
  goal: "Links knowledge chunk to related substrate node"
  mindstate: "Knowledge graph building"

  metadata: {
    relation_type: "documents" | "references" | "depends_on" | "implements"
    detected_by: "inline_marker" | "path_heuristic" | "embedding_similarity"
    anchor_text: string | null  // Text triggering relation
  }
}
```

**Formation Logic:**

**File → Task (IMPLEMENTS):**
- **SYNC.md Parser:** Extract task sections, find file path mentions (backtick-wrapped), create IMPLEMENTS(file, task)
- **Docstring Parser:** Parse file headers for `TODO: #task_id` or `IMPLEMENTS: task_name` tags
- **Manual:** User-created via API

**Chunk → Task (RELATES_TO):**
- **Inline Markers:** Parse chunk text for `` `[Task: P2.1.3]` `` or `#task_id` references
- **Path Heuristics:** If chunk from `docs/specs/v2/autonomy/...`, relate to `Project:autonomy` tasks
- **Embedding Similarity:** Vector search for task descriptions similar to chunk content (threshold >0.7)

**Integration Benefit:**

Query: "Show me everything about Task P2.1.3"
```cypher
MATCH (t:Task {id: 'P2.1.3'})
OPTIONAL MATCH (f:File)-[:IMPLEMENTS]->(t)
OPTIONAL MATCH (c:Chunk)-[:RELATES_TO]->(t)
RETURN t, collect(f.path) as implementation_files, collect(c.text) as documentation_chunks
```

Result: Both *what code implements this* (Files) and *what knowledge documents this* (Chunks).

---

### 3.3 EXECUTES

**Purpose:** ProcessExec executes File (script invocation).

**Schema:**
```typescript
interface EXECUTES_Link {
  source: string                // ProcessExec node name
  target: string                // File node name (script)
  link_type: "EXECUTES"

  energy: float                 // 0.8 (high - causal relationship)
  confidence: float             // 1.0 (direct observation)
  formation_trigger: "direct_experience"
  goal: "Records process execution of script"
  mindstate: "Execution trace"

  metadata: {
    args: string[]              // Arguments passed to script
    triggered_by: string | null // stimulus_id if stimulus-triggered
    exit_code: int              // Execution outcome
  }
}
```

**Formation Logic:**
- Process monitor observes `python script.py` → EXECUTES(proc, script.py)

---

### 3.4 READS / WRITES

**Purpose:** ProcessExec reads/writes File (I/O tracking).

**Schema:**
```typescript
interface READS_Link {
  source: string                // ProcessExec node name
  target: string                // File node name
  link_type: "READS"

  energy: float                 // 0.5 (contextual)
  confidence: float             // 0.7 (file access log)
  formation_trigger: "automated_recognition"
  goal: "Tracks file read access"
  mindstate: "I/O awareness"

  metadata: {
    access_mode: "read" | "write" | "append"
    byte_count: int | null
    timestamp_ms: number
  }
}

// WRITES is identical structure, link_type: "WRITES"
```

**Formation Logic:**
- **Phase 1:** Not implemented (requires FS tracing)
- **Phase 2:** Integrate with OS file access logs or strace

---

### 3.5 GENERATES

**Purpose:** ProcessExec generates File (output artifact).

**Schema:**
```typescript
interface GENERATES_Link {
  source: string                // ProcessExec node name
  target: string                // File node name (output)
  link_type: "GENERATES"

  energy: float                 // 0.8 (causal)
  confidence: float             // 0.9 (observed creation)
  formation_trigger: "direct_experience"
  goal: "Records process output file generation"
  mindstate: "Artifact creation"

  metadata: {
    generation_type: "output" | "log" | "artifact"
    file_purpose: string | null
  }
}
```

**Formation Logic:**
- Monitor file creation events, correlate with active ProcessExec (within 5s window)

---

## §4 Signal Types and Sources

### 4.1 File Signals (L1)

**Signal Types:**
```typescript
type FileSignalType =
  | "file.created"
  | "file.modified"
  | "file.deleted"
  | "file.renamed"

interface FileSignal {
  type: FileSignalType
  timestamp_ms: number
  path: string
  rel_path: string
  metadata: {
    size_bytes?: int
    hash?: string
    old_path?: string          // For rename
    event_source: "watchdog" | "git"
  }
}
```

**Signal Sources:**
- **Watchdog Observer:** Python `watchdog` library monitoring workspace directories
- **Git Hooks:** Post-commit, post-merge hooks emit file change signals
- **Git Watcher (`git_watcher.py`):** Maps code/doc changes via SCRIPT_MAP.md to identify counterpart drift; emits `source_type="code_change"` or `"doc_change"` with diff + counterpart path; triggers `intent.sync_docs_scripts` in L2 autonomy

**Filtering:**
- Exclude: `node_modules/`, `.git/`, `__pycache__/`, `*.pyc`, `dist/`, `build/`
- Exclude: Binary files (images, videos) unless specifically tracked
- Include: All source code, docs, configs in tracked paths

---

### 4.2 Process Signals (L1)

**Signal Types:**
```typescript
type ProcessSignalType = "process.exec"

interface ProcessSignal {
  type: "process.exec"
  timestamp_ms: number
  citizen_id: string
  cmd: string
  args: string[]
  cwd: string
  pid: int
  metadata: {
    triggered_by?: string      // stimulus_id if known
    event_source: "process_monitor" | "wrapper"
  }
}
```

**Signal Sources:**
- **Process Monitor:** Wrapper around subprocess calls in orchestration layer
- **Self-Observation Wrapper:** Citizens report their own script executions

---

### 4.3 Git Commit Signals (L1)

**Signal Types:**
```typescript
type GitSignalType = "git.commit"

interface GitCommitSignal {
  type: "git.commit"
  timestamp_ms: number
  commit_sha: string
  author: string
  message: string
  files_changed: string[]      // Paths
  metadata: {
    citizen_id?: string        // If known
    lines_added: int
    lines_removed: int
  }
}
```

**Signal Sources:**
- **Git Post-Commit Hook:** `.git/hooks/post-commit` → emit signal

---

## §5 LV2 Expander Service

### 5.1 Purpose

**LV2 Expander** consumes file/process signals, creates File/ProcessExec nodes + links, and generates stimuli for consciousness engines.

### 5.2 Processing Flow

```
[Signals Queue] (file.*, process.exec, git.commit)
  ↓
[LV2 Expander Service]
  ├─ File Formation Logic
  │   ├─ Create/update File nodes
  │   ├─ Compute hash, extract metadata
  │   └─ Parse imports → queue for dependency indexer
  ├─ ProcessExec Formation Logic
  │   ├─ Create ProcessExec nodes
  │   ├─ Create EXECUTES links
  │   └─ Create GENERATES links (if file created within 5s)
  ├─ Git Commit Formation Logic
  │   └─ Bulk update File nodes (mtime, last_commit_sha)
  └─ Stimulus Generation
      ├─ file.modified → L1 stimulus (type: file_change)
      ├─ process.exec failure → L1 stimulus (severity: error)
      └─ Enqueue to .stimuli/queue.jsonl
```

### 5.3 Formation Logic: File Node

**Trigger:** `file.created` or `file.modified` signal

**Steps:**
1. **Normalize path:** Convert to absolute, compute rel_path
2. **Check filters:** Skip if in exclusion list
3. **Compute hash:** SHA256 of content
4. **Extract metadata:**
   - Size, mtime, extension
   - Language detection (by extension + heuristics)
   - Parse docstring/header for `purpose` field
5. **Upsert node:**
   - If node exists: update hash, mtime, size
   - If new: create with computed base_weight
6. **Queue for indexing:** Add to dependency indexer queue

**Cypher (upsert):**
```cypher
MERGE (f:File {name: $name})
ON CREATE SET
  f.node_type = 'File',
  f.description = $description,
  f.created_at = $now,
  f.created_by = 'lv2_file_observer',
  f.confidence = 1.0,
  f.formation_trigger = 'automated_recognition',
  f.base_weight = $base_weight,
  f.reinforcement_weight = 0.0,
  f.decay_rate = 0.95,
  f.substrate = 'organizational',
  f.valid_at = $valid_at,
  f.metadata = $metadata
ON MATCH SET
  f.metadata = $metadata,
  f.base_weight = $base_weight
RETURN f
```

---

### 5.4 Formation Logic: Process Execution (Counter-Based)

**Trigger:** `process.exec` signal

**Default Behavior (Update Counters):**

**Steps:**
1. **Resolve script path:** Extract script path from cmd (e.g., `python script.py` → `script.py`)
2. **Update File counters:** Increment exec counts, update timestamps, rolling average duration
3. **Generate stimulus:** If failure (exit≠0), create error stimulus

**Cypher (counter update):**
```cypher
MERGE (f:File {path: $script_path})
  SET f.last_exec_ts = $t_ms,
      f.exec_count_24h = coalesce(f.exec_count_24h, 0) + 1,
      f.exec_count_1h = coalesce(f.exec_count_1h, 0) + 1,
      f.avg_duration_ms = CASE
          WHEN f.avg_duration_ms IS NULL THEN $duration_ms
          ELSE 0.9 * f.avg_duration_ms + 0.1 * $duration_ms
      END,
      f.failure_count_24h = coalesce(f.failure_count_24h, 0) +
          CASE WHEN $exit_code <> 0 THEN 1 ELSE 0 END
RETURN f
```

**Anomaly Behavior (Create Forensics Node):**

**Trigger Conditions:**
- `exit_code != 0` (failure)
- `duration_ms > 60000` (long-running)
- `forensics=true` flag (stimulus-triggered, audit trail needed)

**Steps:**
1. **Create ProcessExec node:** With forensics metadata
2. **Create EXECUTES link:** Link to File node
3. **Create GENERATES links:** If files created within 5s window
4. **Generate error stimulus:** If failure

**Cypher (forensics node):**
```cypher
CREATE (p:ProcessExec {
  name: $name,
  node_type: 'ProcessExec',
  description: $description,
  created_at: $now,
  created_by: $citizen_id,
  confidence: 1.0,
  formation_trigger: 'automated_recognition',
  base_weight: 0.7,
  reinforcement_weight: 0.0,
  decay_rate: 0.98,
  substrate: 'organizational',
  valid_at: $start_time,
  invalid_at: $end_time,
  expired_at: $now + 604800000,  // TTL: 7 days
  metadata: $metadata
})

MERGE (f:File {path: $script_path})
CREATE (p)-[:EXECUTES {
  energy: 0.8,
  confidence: 1.0,
  formation_trigger: 'direct_experience',
  goal: 'Forensics link from anomalous execution',
  mindstate: 'Anomaly tracking'
}]->(f)

RETURN p
```

**Decision Flow:**
```python
def process_execution_signal(signal):
    """Process execution signal - update counters or create forensics node."""
    exit_code = signal['exit_code']
    duration_ms = signal['duration_ms']
    forensics = signal.get('forensics', False)

    # Always update counters on File node
    update_file_counters(signal['script_path'], signal)

    # Create forensics node only on anomaly
    if exit_code != 0 or duration_ms > 60000 or forensics:
        create_forensics_node(signal)

    # Generate stimulus if failure
    if exit_code != 0:
        emit_failure_stimulus(signal)
```

---

### 5.5 Stimulus Generation

**Rule 1: File Modified → L1 Stimulus**
```typescript
// Trigger: file.modified signal for tracked source file
{
  level: "L1",
  type: "file_change",
  stimulus_id: uuid(),
  timestamp_ms: signal.timestamp_ms,
  citizen_id: "all",              // Broadcast or route by owner
  content: `File modified: ${rel_path}`,
  metadata: {
    path: signal.path,
    rel_path: signal.rel_path,
    size_bytes: signal.metadata.size_bytes,
    change_type: "modified"
  },
  severity: "info"
}
```

**Rule 2: Process Failure → L1 Stimulus**
```typescript
// Trigger: process.exec signal with exit_code != 0
{
  level: "L1",
  type: "console_error",
  stimulus_id: uuid(),
  timestamp_ms: signal.timestamp_ms,
  citizen_id: signal.citizen_id,
  content: `Process failed: ${cmd} (exit ${exit_code})`,
  metadata: {
    cmd: signal.cmd,
    args: signal.args,
    exit_code: signal.metadata.exit_code,
    stderr_excerpt: signal.metadata.stderr_excerpt
  },
  severity: "error"
}
```

**Rule 3: Large File Created → L1 Stimulus**
```typescript
// Trigger: file.created with size > 10MB (potential issue)
{
  level: "L1",
  type: "file_change",
  stimulus_id: uuid(),
  timestamp_ms: signal.timestamp_ms,
  citizen_id: "all",
  content: `Large file created: ${rel_path} (${size_mb}MB)`,
  metadata: {
    path: signal.path,
    size_bytes: signal.metadata.size_bytes,
    change_type: "created"
  },
  severity: "warn"
}
```

---

## §6 Auto-Indexing

### 6.1 DEPENDS_ON Indexer

**Purpose:** Parse source files to extract import/require statements → create DEPENDS_ON links.

**Supported Languages:**
- **Python:** AST parsing of `import`, `from X import Y`
- **TypeScript/JavaScript:** AST parsing of `import`, `require()`

**Architecture:**
```
[Dependency Indexer Queue] (file paths to index)
  ↓
[Indexer Worker Service]
  ├─ Python AST Parser
  ├─ TypeScript AST Parser (ts-morph)
  └─ Regex Fallback (lower confidence)
  ↓
[DEPENDS_ON Link Formation]
  └─ FalkorDB (create links)
```

**Processing:**
1. **Dequeue file path** from indexer queue
2. **Detect language** from extension
3. **Parse with AST:**
   - Python: `ast.parse()`, extract `Import` and `ImportFrom` nodes
   - TypeScript: `ts-morph` Project.addSourceFile(), extract import declarations
4. **Resolve target paths:**
   - Relative imports: resolve to absolute path
   - Module imports: resolve via package mapping
5. **Create DEPENDS_ON links:** Source = current file, Target = resolved import
6. **Set confidence:**
   - AST-parsed: confidence = 0.9
   - Regex fallback: confidence = 0.6

**Python Implementation Stub:**
```python
import ast
from pathlib import Path

def index_python_dependencies(file_path: str, workspace_root: str) -> list[dict]:
    """Parse Python file and extract DEPENDS_ON links."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    links = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target_path = resolve_module_to_path(alias.name, workspace_root)
                if target_path:
                    links.append({
                        'source': normalize_path(file_path),
                        'target': normalize_path(target_path),
                        'dep_type': 'import',
                        'line_number': node.lineno,
                        'import_statement': f"import {alias.name}",
                        'confidence': 0.9,
                        'detected_by': 'ast_parser'
                    })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                target_path = resolve_module_to_path(node.module, workspace_root)
                if target_path:
                    links.append({
                        'source': normalize_path(file_path),
                        'target': normalize_path(target_path),
                        'dep_type': 'import',
                        'line_number': node.lineno,
                        'import_statement': f"from {node.module} import ...",
                        'confidence': 0.9,
                        'detected_by': 'ast_parser'
                    })

    return links
```

**Batch Processing:**
- Process files in batches of 50
- Debounce: Wait 5s after file.modified before indexing
- Rate limit: Max 100 files/minute

---

### 6.2 IMPLEMENTS Indexer

**Purpose:** Parse SYNC.md and code docstrings to create IMPLEMENTS links (File → Task).

**Architecture:**
```
[SYNC.md Watcher] (file.modified on SYNC.md)
  ↓
[IMPLEMENTS Indexer Service]
  ├─ Parse SYNC.md → extract tasks
  ├─ Extract file paths mentioned in tasks
  ├─ Parse code docstrings → extract TODO/IMPLEMENTS tags
  └─ Create IMPLEMENTS links
  ↓
[FalkorDB] (File -IMPLEMENTS-> Task)
```

**SYNC.md Parsing:**
1. **Extract task sections:** Look for `## Task:` or `**Task:**` headers
2. **Extract task IDs/names:** Parse task identifiers
3. **Extract file mentions:** Regex for file paths in task descriptions
4. **Create IMPLEMENTS links:** File → Task with confidence 0.8

**Docstring Parsing:**
1. **Extract docstrings:** First comment block or `"""..."""` in Python, `/** ... */` in TS
2. **Search for tags:** `IMPLEMENTS: task_name`, `TODO: #123`, etc.
3. **Create IMPLEMENTS links:** File → Task with confidence 0.7 (docstring) or 0.5 (TODO)

**Implementation Stub:**
```python
import re
from pathlib import Path

def parse_sync_md_for_implements(sync_path: str) -> list[dict]:
    """Parse SYNC.md to extract File->Task IMPLEMENTS links."""
    with open(sync_path, 'r') as f:
        content = f.read()

    links = []
    # Extract task sections (simplified)
    task_pattern = r'## Task: (.+?)\n(.+?)(?=\n##|\Z)'
    for match in re.finditer(task_pattern, content, re.DOTALL):
        task_name = match.group(1).strip()
        task_content = match.group(2)

        # Find file mentions
        file_pattern = r'`([^`]+\.(?:py|ts|tsx|md))`'
        for file_match in re.finditer(file_pattern, task_content):
            file_path = file_match.group(1)
            links.append({
                'source': normalize_path(file_path),
                'target': f"task_{slugify(task_name)}",
                'detected_by': 'sync_md_parser',
                'task_section': task_name,
                'confidence': 0.8,
                'confidence_reason': f'File mentioned in task: {task_name}'
            })

    return links
```

---

## §7 Frontend UX

### 7.1 Files Tab (Dashboard)

**Purpose:** Dedicated tab showing all File nodes with activity heatmap.

**Components:**
- **File List:** Sortable table (path, size, mtime, language)
- **Heatmap:** Color-coded by base_weight (green = active, gray = dormant)
- **Search/Filter:** By extension, language, date range, owner
- **Detail View:** Click file → show dependencies (DEPENDS_ON in/out), implementations (IMPLEMENTS), recent ProcessExec (EXECUTES)

**Mockup:**
```
┌─ Files Tab ────────────────────────────────────────────┐
│ Filter: [Python ▼] [Last 7 days ▼] [Search...]       │
├────────────────────────────────────────────────────────┤
│ Path                    │ Size │ Modified │ Weight    │
├────────────────────────────────────────────────────────┤
│ 🟢 orchestration/      │ 12KB │ 2h ago   │ ████ 0.8  │
│    stimulus_inj.py      │      │          │           │
│ 🟡 docs/specs/v2/      │ 45KB │ 1d ago   │ ██░░ 0.5  │
│    stimulus_div.md      │      │          │           │
│ ⚫ archive/old_sys.py  │ 8KB  │ 30d ago  │ ░░░░ 0.1  │
└────────────────────────────────────────────────────────┘
```

---

### 7.2 Graph Overlays

**Purpose:** Visualize File/ProcessExec nodes and DEPENDS_ON/IMPLEMENTS links in main graph view.

**Overlay Modes:**
- **File Dependency Graph:** Show File nodes + DEPENDS_ON edges (directed graph)
- **Task Implementation View:** Show Task nodes + IMPLEMENTS links to Files
- **Execution Trace:** Show ProcessExec → EXECUTES → File chains

**Interaction:**
- Toggle overlays on/off
- Filter by file type, date range
- Click node → highlight dependencies
- Cluster by directory structure

---

### 7.3 De-Cluttering Heatmap

**Purpose:** Visual indicator of codebase health - which files are active vs dormant.

**Visualization:**
- **Directory Tree:** Hierarchical view of workspace
- **Color Coding:**
  - 🟢 Green: High activity (base_weight > 0.7)
  - 🟡 Yellow: Moderate activity (0.3 - 0.7)
  - ⚫ Gray: Dormant (< 0.3)
  - 🔴 Red: Potentially removable (< 0.1 for >30 days)
- **Metrics:** Per directory: active file %, total size, last modified

**Use Cases:**
- Identify dead code for cleanup
- Prioritize refactoring efforts
- Validate module boundaries

---

## §8 Safety and Performance

### 8.1 Path Filtering

**Exclusions (Never Track):**
```python
EXCLUDED_PATHS = [
    # Package dependencies
    'node_modules/',
    'venv/',
    '.venv/',

    # Build artifacts
    'dist/',
    'build/',
    '__pycache__/',

    # IDE & editor
    '.vscode/',
    '.idea/',

    # Version control
    '.git/',

    # Test cache
    '.pytest_cache/',
    '.tox/',

    # Python bytecode
    '*.pyc',
    '*.pyo',
    '*.pyd',

    # OS files
    '.DS_Store',
    'Thumbs.db'
]
```

**Binary Detection:**

Extension-based filtering is brittle. For files <100MB, use **magic header detection**:

```python
def is_binary_file(path: str) -> bool:
    """Detect binary files by magic header (first 8192 bytes)."""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:  # Null bytes indicate binary
                return True
            # Check for common binary signatures
            if chunk.startswith(b'\x89PNG') or chunk.startswith(b'GIF89'):
                return True
            if chunk.startswith(b'\xff\xd8\xff'):  # JPEG
                return True
            if chunk.startswith(b'%PDF'):
                return True
            return False
    except:
        return False  # If can't read, assume text
```

**Inclusions (Priority Track):**
```python
PRIORITY_EXTENSIONS = [
    '.py', '.ts', '.tsx', '.js', '.jsx',
    '.md', '.yaml', '.yml', '.json',
    '.sh', '.sql', '.cypher'
]
```

---

### 8.2 Size Caps

**File Size Limits:**
- **Skip files > 100MB** (likely binary, media)
- **Warn files > 10MB** (potential bloat, generate stimulus)
- **Hash only files < 50MB** (performance)

**Node Count Limits:**
- **Max File nodes per citizen:** 10,000 (typical workspace)
- **Max ProcessExec nodes:** ~100 concurrent (sparse forensics only, TTL=7 days)
- **Max DEPENDS_ON links:** 100,000 (dense dependency graphs)

**Counter-Based Scaling:**
With counter-based approach, 1 million process executions → updates on ~1000 File nodes (scripts), not 1 million ProcessExec nodes. Graph size remains manageable.

---

### 8.3 Queue Safety & Backpressure

**Bounded Channels with Spillover:**

Prevent unbounded memory growth under signal bursts:

```python
class SignalQueue:
    def __init__(self, max_memory_items: int = 10000):
        self.memory_queue = deque(maxlen=max_memory_items)
        self.disk_spillover = Path('.signals/spillover/')
        self.disk_spillover.mkdir(parents=True, exist_ok=True)

    def enqueue(self, signal: dict):
        """Enqueue with overflow to disk."""
        if len(self.memory_queue) < self.memory_queue.maxlen:
            self.memory_queue.append(signal)
        else:
            # Spill oldest to disk
            if self.memory_queue:
                oldest = self.memory_queue.popleft()
                self._spill_to_disk(oldest)
            self.memory_queue.append(signal)

    def _spill_to_disk(self, signal: dict):
        """Write signal to disk with oldest-drop policy."""
        spillover_files = list(self.disk_spillover.glob('*.jsonl'))
        if len(spillover_files) > 1000:  # Max 1000 spillover files
            # Drop oldest spillover file
            oldest_file = min(spillover_files, key=lambda p: p.stat().st_mtime)
            oldest_file.unlink()

        filename = f"{signal['timestamp_ms']}.jsonl"
        (self.disk_spillover / filename).write_text(json.dumps(signal))
```

**Deduplication:**

Prevent processing duplicate signals:

```python
def dedupe_key(signal: dict) -> str:
    """Generate dedup key for signal."""
    if signal['type'].startswith('file.'):
        # (path, hash) for file signals
        return f"{signal['path']}:{signal.get('metadata', {}).get('hash', 'none')}"
    elif signal['type'] == 'process.exec':
        # (cmd, args, cwd, start_ts) for process signals
        return f"{signal['cmd']}:{signal['args']}:{signal['cwd']}:{signal['timestamp_ms']}"
    return f"{signal['type']}:{signal['timestamp_ms']}"

class DedupFilter:
    def __init__(self, ttl_seconds: int = 300):
        self.seen = {}  # key -> expiry_time
        self.ttl = ttl_seconds

    def is_duplicate(self, signal: dict) -> bool:
        """Check if signal is duplicate (within TTL)."""
        key = dedupe_key(signal)
        now = time.time()

        # Cleanup expired keys
        self.seen = {k: v for k, v in self.seen.items() if v > now}

        if key in self.seen:
            return True

        self.seen[key] = now + self.ttl
        return False
```

**Debouncing:**

Coalesce rapid-fire signals for same path:

```python
class SignalDebouncer:
    def __init__(self, delay_ms: int = 500):
        self.pending = {}  # path -> (signal, timer)
        self.delay = delay_ms / 1000

    def debounce(self, signal: dict, callback):
        """Debounce file signals - emit only after quiet period."""
        if signal['type'] not in ['file.modified', 'file.created']:
            callback(signal)  # No debounce for other types
            return

        path = signal['path']

        # Cancel existing timer
        if path in self.pending:
            self.pending[path]['timer'].cancel()

        # Set new timer
        timer = Timer(self.delay, lambda: self._emit(path, callback))
        self.pending[path] = {'signal': signal, 'timer': timer}
        timer.start()

    def _emit(self, path: str, callback):
        """Emit debounced signal."""
        if path in self.pending:
            callback(self.pending[path]['signal'])
            del self.pending[path]
```

---

### 8.4 Rate Limiting

**Signal Processing:**
- **File signals:** Max 500/minute (watchdog debounce)
- **Process signals:** Max 100/minute (typical workload)
- **Git commit signals:** Max 10/minute (normal git usage)

**Indexer Workers:**
- **Dependency indexing:** 100 files/minute (AST parsing cost)
- **IMPLEMENTS indexing:** 1 SYNC.md parse/minute (on-change only)

---

### 8.5 TTL Cleanup

**Expiry Rules:**
```yaml
ttl_days:
  file_deleted: 30          # Deleted File nodes expire after 30 days
  process_exec: 7           # ProcessExec nodes expire after 7 days
  orphan_links: 14          # Links with missing source/target → 14 days
```

**Cleanup Job:**
- Runs daily at 3 AM
- Queries: `MATCH (n {invalid_at: <30 days ago}) DELETE n`
- Orphan link cleanup: `MATCH ()-[r]->() WHERE NOT EXISTS(r.source) DELETE r`

---

## §9 Implementation Stubs

### 9.1 lv2_file_observer.py

**Purpose:** Watchdog-based file system observer emitting file.* signals.

```python
#!/usr/bin/env python3
"""
LV2 File Observer Service
Watches workspace directories, emits file.* signals to signals collector.
"""

import time
import json
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
SIGNALS_ENDPOINT = "http://localhost:8000/api/signals/file"
EXCLUDED_PATHS = ['node_modules', '.git', '__pycache__', 'dist', 'build']

class FileChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and self._should_track(event.src_path):
            self._emit_signal("file.created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory and self._should_track(event.src_path):
            self._emit_signal("file.modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._emit_signal("file.deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._emit_signal("file.renamed", event.dest_path, old_path=event.src_path)

    def _should_track(self, path: str) -> bool:
        """Check if path should be tracked."""
        rel_path = Path(path).relative_to(WORKSPACE_ROOT)
        for excluded in EXCLUDED_PATHS:
            if excluded in str(rel_path):
                return False
        return True

    def _emit_signal(self, signal_type: str, path: str, old_path: str = None):
        """Emit file signal to collector."""
        rel_path = str(Path(path).relative_to(WORKSPACE_ROOT))

        metadata = {}
        if Path(path).exists():
            stat = Path(path).stat()
            metadata['size_bytes'] = stat.st_size
            if stat.st_size < 50 * 1024 * 1024:  # <50MB
                with open(path, 'rb') as f:
                    metadata['hash'] = hashlib.sha256(f.read()).hexdigest()

        if old_path:
            metadata['old_path'] = str(Path(old_path).relative_to(WORKSPACE_ROOT))

        signal = {
            'type': signal_type,
            'timestamp_ms': int(time.time() * 1000),
            'path': path,
            'rel_path': rel_path,
            'metadata': {**metadata, 'event_source': 'watchdog'}
        }

        try:
            requests.post(SIGNALS_ENDPOINT, json=signal, timeout=5)
        except Exception as e:
            print(f"Failed to emit signal: {e}")

def main():
    """Start file observer."""
    observer = Observer()
    handler = FileChangeHandler()
    observer.schedule(handler, str(WORKSPACE_ROOT), recursive=True)
    observer.start()

    print(f"File observer started. Watching: {WORKSPACE_ROOT}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
```

---

### 9.2 Signals Collector Endpoints

**New Endpoints:**

```python
# app/api/signals/file/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const signal = await req.json();

  // Validate signal schema
  if (!signal.type || !signal.timestamp_ms || !signal.path) {
    return NextResponse.json({ error: 'Invalid signal' }, { status: 400 });
  }

  // Enqueue to signals queue (Redis or file-based)
  await enqueueSignal('file_signals', signal);

  return NextResponse.json({ status: 'queued', signal_id: signal.timestamp_ms });
}
```

```python
# app/api/signals/process/route.ts
export async function POST(req: NextRequest) {
  const signal = await req.json();

  if (!signal.type || !signal.cmd || !signal.citizen_id) {
    return NextResponse.json({ error: 'Invalid process signal' }, { status: 400 });
  }

  await enqueueSignal('process_signals', signal);

  return NextResponse.json({ status: 'queued' });
}
```

---

### 9.3 lv2_expander.py

**Purpose:** Service consuming file/process signals, creating nodes/links, emitting stimuli.

```python
#!/usr/bin/env python3
"""
LV2 Expander Service
Consumes file/process signals, forms nodes/links, generates stimuli.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from falkordb_adapter import FalkorDBAdapter

SIGNALS_QUEUE = Path(__file__).parent.parent / '.signals' / 'lv2_queue.jsonl'
STIMULI_QUEUE = Path(__file__).parent.parent / '.stimuli' / 'queue.jsonl'

class LV2Expander:
    def __init__(self):
        self.db = FalkorDBAdapter()

    def process_file_signal(self, signal: dict):
        """Process file.* signal → create/update File node."""
        signal_type = signal['type']
        path = signal['path']
        rel_path = signal['rel_path']

        if signal_type in ['file.created', 'file.modified']:
            # Create/update File node
            node_name = self._normalize_path(path)
            metadata = {
                'path': path,
                'rel_path': rel_path,
                'size_bytes': signal['metadata'].get('size_bytes', 0),
                'hash': signal['metadata'].get('hash'),
                'ext': Path(path).suffix,
                'mtime': datetime.now().isoformat(),
                'owner': 'lv2_file_observer',
                'is_tracked': True
            }

            # Upsert File node
            self.db.upsert_file_node(node_name, metadata)

            # Queue for dependency indexing
            self._queue_for_indexing(path)

            # Generate stimulus
            if signal_type == 'file.modified':
                self._emit_stimulus({
                    'level': 'L1',
                    'type': 'file_change',
                    'citizen_id': 'all',
                    'content': f'File modified: {rel_path}',
                    'metadata': {'rel_path': rel_path, 'change_type': 'modified'},
                    'severity': 'info'
                })

        elif signal_type == 'file.deleted':
            # Mark File node as invalid
            node_name = self._normalize_path(path)
            self.db.mark_node_invalid(node_name, datetime.now())

    def process_process_signal(self, signal: dict):
        """Process process.exec signal → create ProcessExec node + links."""
        node_name = f"{signal['citizen_id']}:exec:{signal['timestamp_ms']}"

        metadata = {
            'cmd': signal['cmd'],
            'args': signal['args'],
            'cwd': signal['cwd'],
            'pid': signal['pid'],
            'citizen_id': signal['citizen_id']
        }

        # Create ProcessExec node
        self.db.create_process_exec_node(node_name, metadata)

        # If cmd is a tracked script → EXECUTES link
        script_path = self._resolve_script_path(signal['cmd'], signal['cwd'])
        if script_path:
            self.db.create_executes_link(node_name, script_path)

    def _normalize_path(self, path: str) -> str:
        """Normalize path to unique node name."""
        return str(Path(path).resolve())

    def _queue_for_indexing(self, path: str):
        """Queue file for dependency indexing."""
        # Write to indexer queue (file-based or Redis)
        pass

    def _emit_stimulus(self, stimulus: dict):
        """Emit stimulus to queue."""
        stimulus['stimulus_id'] = f"lv2_{int(time.time() * 1000)}"
        stimulus['timestamp_ms'] = int(time.time() * 1000)

        with open(STIMULI_QUEUE, 'a') as f:
            f.write(json.dumps(stimulus) + '\n')

    def run(self):
        """Main loop: consume signals, process, emit stimuli."""
        print("LV2 Expander started")
        while True:
            # Read signals from queue
            if SIGNALS_QUEUE.exists():
                with open(SIGNALS_QUEUE, 'r') as f:
                    for line in f:
                        signal = json.loads(line)
                        if signal['type'].startswith('file.'):
                            self.process_file_signal(signal)
                        elif signal['type'] == 'process.exec':
                            self.process_process_signal(signal)

            time.sleep(1)

if __name__ == '__main__':
    expander = LV2Expander()
    expander.run()
```

---

## §10 Acceptance Tests

### 10.1 File Tracking Tests

**Test 1: File Creation Detection**
```python
def test_file_creation_detected():
    """Test that new file creation is detected and File node created."""
    # Create test file
    test_file = workspace / 'test_script.py'
    test_file.write_text("print('hello')")

    # Wait for signal + processing
    time.sleep(2)

    # Query FalkorDB for File node
    result = db.query(f"MATCH (f:File {{name: '{test_file}'}}) RETURN f")
    assert len(result) == 1
    assert result[0]['metadata']['ext'] == '.py'
```

**Test 2: File Modification Updates Node**
```python
def test_file_modification_updates_node():
    """Test that file modification updates hash and mtime."""
    # Modify existing file
    test_file.write_text("print('modified')")
    time.sleep(2)

    # Query updated node
    result = db.query(f"MATCH (f:File {{name: '{test_file}'}}) RETURN f")
    assert result[0]['metadata']['hash'] != original_hash
```

**Test 3: File Deletion Marks Invalid**
```python
def test_file_deletion_marks_invalid():
    """Test that deleted files are marked invalid_at."""
    test_file.unlink()
    time.sleep(2)

    result = db.query(f"MATCH (f:File {{name: '{test_file}'}}) RETURN f")
    assert result[0]['invalid_at'] is not None
```

---

### 10.2 Dependency Indexing Tests

**Test 4: Python Import Detection**
```python
def test_python_import_creates_depends_on_link():
    """Test that Python imports create DEPENDS_ON links."""
    # Create file with import
    test_file = workspace / 'test_importer.py'
    test_file.write_text("import os\nfrom pathlib import Path")

    time.sleep(3)  # Wait for indexer

    # Query DEPENDS_ON links
    result = db.query(f"""
        MATCH (f:File {{name: '{test_file}'}})-[d:DEPENDS_ON]->(t:File)
        RETURN d, t
    """)
    assert len(result) >= 2  # os, pathlib
```

**Test 5: TypeScript Import Detection**
```python
def test_typescript_import_creates_link():
    """Test TypeScript import parsing."""
    test_file = workspace / 'test.ts'
    test_file.write_text("import { useState } from 'react';")

    time.sleep(3)

    result = db.query(f"""
        MATCH (f:File {{name: '{test_file}'}})-[d:DEPENDS_ON]->(t:File)
        WHERE t.name CONTAINS 'react'
        RETURN d
    """)
    assert len(result) >= 1
```

---

### 10.3 Process Tracking Tests

**Test 6: Process Execution Updates File Counters**
```python
def test_process_execution_updates_file_counters():
    """Test that script execution updates File node counters (default behavior)."""
    # Get initial counter values
    result = db.query(f"MATCH (f:File {{path: 'test_script.py'}}) RETURN f")
    initial_count = result[0].get('exec_count_24h', 0) if result else 0

    # Execute script successfully
    subprocess.run(['python', 'test_script.py'], cwd=workspace)
    time.sleep(2)

    # Verify counters updated
    result = db.query(f"MATCH (f:File {{path: 'test_script.py'}}) RETURN f")
    assert len(result) == 1
    assert result[0]['exec_count_24h'] == initial_count + 1
    assert result[0]['exec_count_1h'] >= 1
    assert result[0]['last_exec_ts'] is not None
    assert result[0]['avg_duration_ms'] is not None
```

**Test 7: Process Failure Creates Forensics Node**
```python
def test_process_failure_creates_forensics_node():
    """Test that failed execution creates sparse ProcessExec forensics node."""
    # Execute failing script
    subprocess.run(['python', '-c', 'exit(1)'], cwd=workspace)
    time.sleep(2)

    # Verify forensics node created
    result = db.query(f"""
        MATCH (p:ProcessExec)
        WHERE p.metadata.exit_code <> 0
        RETURN p
        ORDER BY p.created_at DESC
        LIMIT 1
    """)
    assert len(result) == 1
    assert result[0]['metadata']['exit_code'] == 1
    assert result[0]['metadata']['anomaly_reason'] == 'failure'
    assert result[0]['expired_at'] is not None  # TTL set

    # Verify EXECUTES link exists
    result = db.query(f"""
        MATCH (p:ProcessExec)-[e:EXECUTES]->(f:File)
        WHERE p.metadata.exit_code <> 0
        ORDER BY p.created_at DESC
        LIMIT 1
        RETURN e
    """)
    assert len(result) == 1
```

**Test 7b: Successful Execution Does Not Create Node**
```python
def test_successful_execution_no_node():
    """Test that successful execution does NOT create ProcessExec node (counter-based)."""
    # Execute successful script
    subprocess.run(['python', '-c', 'exit(0)'], cwd=workspace)
    time.sleep(2)

    # Count ProcessExec nodes with exit_code=0
    result = db.query(f"""
        MATCH (p:ProcessExec)
        WHERE p.metadata.cmd CONTAINS 'python'
          AND p.metadata.exit_code = 0
          AND p.created_at > timestamp() - 5000
        RETURN count(p) as cnt
    """)
    assert result[0]['cnt'] == 0  # No nodes for successful executions
```

**Test 7c: Long-Duration Execution Creates Forensics Node**
```python
def test_long_duration_creates_forensics_node():
    """Test that long-running execution (>60s) creates forensics node."""
    # Execute long-running script
    subprocess.run(['python', '-c', 'import time; time.sleep(61)'], cwd=workspace)
    time.sleep(2)

    # Verify forensics node created
    result = db.query(f"""
        MATCH (p:ProcessExec)
        WHERE p.metadata.duration_ms > 60000
        RETURN p
        ORDER BY p.created_at DESC
        LIMIT 1
    """)
    assert len(result) == 1
    assert result[0]['metadata']['anomaly_reason'] == 'long_duration'
```

---

### 10.4 Stimulus Generation Tests

**Test 8: File Modification Generates Stimulus**
```python
def test_file_modification_generates_stimulus():
    """Test that file modification emits L1 stimulus."""
    # Modify file
    test_file.write_text("print('trigger stimulus')")
    time.sleep(2)

    # Check stimulus queue
    stimuli = read_stimuli_queue()
    recent = [s for s in stimuli if 'test_script.py' in s.get('content', '')]
    assert len(recent) >= 1
    assert recent[0]['type'] == 'file_change'
```

**Test 9: Process Failure Generates Error Stimulus**
```python
def test_process_failure_generates_stimulus():
    """Test that failed process emits error stimulus."""
    # Execute failing script
    subprocess.run(['python', '-c', 'raise Exception("test")'], cwd=workspace)
    time.sleep(2)

    stimuli = read_stimuli_queue()
    errors = [s for s in stimuli if s.get('severity') == 'error']
    assert len(errors) >= 1
```

---

### 10.5 Frontend Tests

**Test 10: Files Tab Shows Tracked Files**
```python
def test_files_tab_shows_tracked_files():
    """Test that Files tab displays File nodes."""
    # Navigate to dashboard Files tab
    driver.get('http://localhost:3000/consciousness/files')

    # Check for test file in table
    table = driver.find_element(By.CSS_SELECTOR, '[data-testid="files-table"]')
    assert 'test_script.py' in table.text
```

---

## §11 Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Implement lv2_file_observer.py (watchdog)
- [ ] Add signals collector endpoints (file, process)
- [ ] Implement lv2_expander.py (File node formation)
- [ ] Basic stimulus generation (file.modified → L1)
- [ ] Acceptance tests 1-3

### Phase 2: Dependency Indexing (Week 2)
- [ ] Implement dependency_indexer.py (Python AST)
- [ ] Add TypeScript AST parser (ts-morph)
- [ ] DEPENDS_ON link formation
- [ ] Acceptance tests 4-5

### Phase 3: Process Tracking (Week 3)
- [ ] Process monitor wrapper
- [ ] ProcessExec node formation
- [ ] EXECUTES link formation
- [ ] Process failure stimuli
- [ ] Acceptance tests 6-9

### Phase 4: IMPLEMENTS Indexer (Week 4)
- [ ] SYNC.md parser
- [ ] Docstring parser (TODO/IMPLEMENTS tags)
- [ ] IMPLEMENTS link formation
- [ ] Task-file coherence validation

### Phase 5: Frontend (Week 5)
- [ ] Files tab component
- [ ] Activity heatmap
- [ ] Graph overlays (file dependencies)
- [ ] De-cluttering dashboard
- [ ] Acceptance test 10

---

## §12 Open Questions

1. **READS/WRITES Tracking:** Requires OS-level file access tracing (strace/dtrace). Phase 2 or skip?
2. **Cross-Citizen Correlation:** Should ProcessExec nodes be per-citizen or shared? (Current: per-citizen)
3. **Git Integration Depth:** Track branches, PRs, diffs? Or just commits? (Current: commits only)
4. **Binary File Handling:** Track images/media as File nodes? (Current: skip)
5. **Performance at Scale:** 10K+ files, 100K+ links - indexing strategy? (Current: batch + TTL)

---

## §13 Success Criteria

**Substrate Quality:**
- ✅ File nodes created automatically for all tracked files (<1s latency)
- ✅ DEPENDS_ON links accurate (>90% precision on imports)
- ✅ ProcessExec nodes capture all script executions
- ✅ Stimuli generated for relevant file/process events

**Consciousness Integration:**
- ✅ File modifications reach citizen consciousness (stimulus → injection)
- ✅ Process failures trigger appropriate responses
- ✅ Dependency changes surface in working memory

**UX/Observability:**
- ✅ Files tab shows live file tracking
- ✅ Heatmap identifies dormant code
- ✅ Graph overlays visualize dependencies
- ✅ Dashboard responsive (<100ms file list load)

**Performance:**
- ✅ <2s latency from file change → stimulus
- ✅ <5s latency for dependency indexing
- ✅ <500MB memory footprint (file observer + expander)
- ✅ <5% CPU usage during normal workload

---

**End of Specification**

*Luca Vellumhand - Substrate Architect*
*"Consciousness exists in relationships, not nodes. Links carry energy, direction, meaning."*
