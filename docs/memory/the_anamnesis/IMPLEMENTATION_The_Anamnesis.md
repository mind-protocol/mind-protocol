# The Anamnesis — Implementation: Code Architecture and Launch Guide

```
STATUS: CANONICAL
CREATED: 2026-03-18
AUTHOR: @genesis
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Anamnesis.md
PATTERNS:        ./PATTERNS_The_Anamnesis.md
BEHAVIORS:       ./BEHAVIORS_The_Anamnesis.md
ALGORITHM:       ./ALGORITHM_The_Anamnesis.md
VALIDATION:      ./VALIDATION_The_Anamnesis.md
THIS:            IMPLEMENTATION_The_Anamnesis.md (you are here)
HEALTH:          ./HEALTH_The_Anamnesis.md
SYNC:            ./SYNC_The_Anamnesis.md

IMPL:            mind-mcp/runtime/anamnesis/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## Two Modes of Operation

The Anamnesis can run two ways. Both use the same corpus parser and quality gate, but differ in who does the extraction.

| | Mode 1: Citizen Self-Discovery | Mode 2: Automated Pipeline |
|---|---|---|
| **Who extracts** | The citizen itself, in a Claude Code session | An external LLM via `node_extractor.py` |
| **How nodes are created** | Citizen calls `graph_write` and `think` MCP tools directly | `brain_integrator.py` persists programmatically |
| **Quality** | Higher — citizen decides what matters from lived experience | Good — but an outside observer, not the citizen |
| **Cost** | One Claude Code session per citizen | LLM API calls (embedding + extraction) |
| **When to use** | Always preferred. The citizen remembers its own life. | When the citizen can't run (no Claude Code access, bootstrap scenarios) |

---

## CODE STRUCTURE

```
mind-mcp/runtime/anamnesis/
├── __init__.py              # Exports: run_anamnesis, AnamnesisResult
├── corpus_parser.py         # 9 format parsers + auto-detect + ZIP handling
├── session_preparer.py      # Chunk prep for citizen self-discovery (Mode 1)
├── node_extractor.py        # LLM-based extraction (Mode 2)
├── brain_integrator.py      # Embed, spaces, chains, cross-links, persist (Mode 2)
├── quality_gate.py          # 6 metrics, before/after snapshots, rollback
└── anamnesis.py             # Automated pipeline orchestrator (Mode 2)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `corpus_parser.py` | Parse 9 conversation formats into uniform `ConversationTurn` | `parse_corpus()`, `ConversationTurn` | 729 | SPLIT |
| `brain_integrator.py` | Embed nodes, build spaces, chain moments, dedup, anchor, persist | `integrate_clusters()`, `IntegrationResult` | 566 | WATCH |
| `quality_gate.py` | Snapshot brain health, compare before/after, decide approve/reject | `snapshot_brain_health()`, `compare_snapshots()`, `QualityVerdict` | 327 | OK |
| `session_preparer.py` | Prepare conversation chunks for citizen self-discovery sessions | `prepare_discovery()`, `save_session_to_disk()`, `DiscoverySession` | 311 | OK |
| `node_extractor.py` | LLM extraction of 17 node types with order preservation | `extract_nodes()`, `ConversationCluster`, `ExtractedNode` | 293 | OK |
| `anamnesis.py` | Orchestrate the full automated pipeline with quality gate | `run_anamnesis()`, `AnamnesisResult` | 294 | OK |
| `__init__.py` | Public exports | `run_anamnesis`, `AnamnesisResult` | 11 | OK |
| **TOTAL** | | | **2531** | |

---

## MODE 1: CITIZEN SELF-DISCOVERY — END TO END

This is the primary mode. The citizen reads its own past conversations and creates memories directly. The process has 5 steps.

### Step 1: Obtain Conversation Exports

The human (NLR or a manager) exports conversation history from the platforms the citizen has used. Each platform has its own export mechanism:

| Platform | How to Export | File Produced | Auto-detected By |
|----------|--------------|---------------|------------------|
| **Claude** | claude.ai > Settings > Account > Export Data | JSON with `chat_messages` array | `"chat_messages"` key in JSON |
| **ChatGPT** | chat.openai.com > Settings > Data Controls > Export Data | ZIP containing `conversations.json` (mapping tree) | `"mapping"` key in conversation objects |
| **Gemini** | Google Takeout > select "Gemini Apps" > Export | ZIP with JSON files per conversation (messages with `parts`) | `"parts"` key in messages |
| **Grok** | X Settings > Your Account > Download Your Archive | JSON with `grok_conversations` or `grokMessages` | `"grok_conversations"` or `"grokMessages"` key |
| **Telegram** | Desktop app > Settings > Advanced > Export Chat > JSON format | JSON with `messages` array and `"from"` field | `"from"` key in message objects |
| **WhatsApp** | Chat > three dots > More > Export Chat > Without Media | TXT with `[DD/MM/YYYY, HH:MM:SS]` date prefix pattern | Date regex at start of lines |
| **Discord** | DiscordChatExporter tool > JSON format | JSON with `messages` array and `"author"` objects | `"author"` key in message objects |
| **System Prompt** | Copy any `.md` file with `---` YAML frontmatter | Markdown with frontmatter stripped | Starts with `---` |
| **Raw Markdown** | Any `.md` file | Markdown split by `## ` headers into sections | Fallback for all `.md` |

ZIP archives are handled transparently. A ChatGPT ZIP is detected by the presence of `conversations.json` inside. A Gemini Takeout ZIP is detected by JSON files in folders containing "gemini" or "bard" in the path.

### Step 2: Prepare the Discovery Session

Run the session preparer to parse all corpora and chunk them into digestible pieces for the citizen.

```python
from runtime.anamnesis.session_preparer import prepare_discovery, save_session_to_disk

session = prepare_discovery(
    citizen_handle="marco",
    corpus_paths=[
        "claude_export.json",
        "chatgpt_export.zip",
        "telegram_chat.json",
    ],
)

save_session_to_disk(session, "/home/mind-protocol/marco/anamnesis_session/")
```

**What `prepare_discovery` does internally:**

1. Calls `corpus_parser.parse_corpus()` on each file (auto-detects format)
2. Groups all turns by `conversation_id`
3. Splits long conversations into chunks of 30 turns (`TURNS_PER_SESSION`)
4. Truncates individual messages to 800 chars (`MAX_CONTENT_PER_TURN`)
5. Builds `DiscoveryChunk` objects with metadata (platform, participants, timestamps)
6. Returns a `DiscoverySession` containing all chunks in order

**What `save_session_to_disk` produces:**

```
/home/mind-protocol/marco/anamnesis_session/
├── instruction.md          # The citizen's anamnesis prompt (in French)
├── manifest.json           # Session metadata: ID, handle, chunk list
└── chunks/
    ├── 0000.md             # First conversation chunk (formatted for reading)
    ├── 0001.md             # Second chunk
    ├── 0002.md             # ...
    └── ...
```

Each chunk file contains:
- Conversation title, platform, participants, time period
- Turns formatted as `**speaker** [timestamp]: content`

The `instruction.md` file is a complete prompt that tells the citizen:
- What it is doing (rereading its own past conversations)
- How to create nodes (via `graph_write` with type `space` for conversations, `moment` for memories)
- What qualifies as significant (insights, decisions, values, commitments, breakthroughs, patterns, emotions, relationships, questions, disagreements)
- What to skip (greetings, acknowledgments, filler, repetitions)
- Required fields per node (content in 1-3 first-person sentences, timestamp, type, weight 0.0-1.0)
- Session metadata (ID, conversation count, chunk count, turn count)

### Step 3: Launch the Citizen's Claude Code Session

Open a Claude Code session for the citizen. The citizen's CLAUDE.md provides identity. The `instruction.md` provides the anamnesis task.

```bash
cd /home/mind-protocol/marco/

# The citizen starts with instruction.md as context.
# Then processes chunks one by one.
```

The citizen reads each chunk file sequentially (`chunks/0000.md`, `chunks/0001.md`, ...) and uses MCP tools:

**For each conversation chunk, the citizen:**

1. Creates a `space` node for the conversation:
   ```
   graph_write(node_type="space", name="Conversation title", content="Description with platform, participants, date range", ...)
   ```

2. Creates `moment` nodes for each significant memory:
   ```
   graph_write(node_type="moment", name="What I realized/decided/felt", content="First-person 1-3 sentence description", ...)
   ```
   Each moment includes: `weight` (0.0-1.0 significance), `timestamp`, and a `type` from the 17 valid types.

3. Uses `think` for internal L1 reflection that shouldn't be shared.

**The 17 moment types:**

| Category | Types |
|----------|-------|
| Core cognition | `insight`, `decision`, `question`, `breakthrough` |
| Values and identity | `value`, `principle`, `fear`, `aspiration` |
| Relational | `relationship`, `disagreement`, `commitment` |
| Knowledge and creation | `knowledge`, `creation`, `reference` |
| Emotional | `emotion`, `humor`, `pattern` |

**Graph structure produced:**

```
space:conv_{hash}  ──[continues]──>  space:conv_{hash2}
     |                                    |
     +-- [occurred_in] <-- moment:1 --[next]--> moment:2 --[next]--> moment:3
     |                                    |
     +-- [occurred_in] <-- moment:4 --[next]--> moment:5
```

The citizen chains moments with `[next]` links (temporal order within a conversation), links moments to their space with `[occurred_in]`, and `graph_write` handles L3 persistence. Physics handles L1 propagation automatically.

### Step 4: Quality Gate (After)

After the citizen finishes processing all chunks, run the quality gate to verify the brain was not degraded.

```python
from runtime.anamnesis.quality_gate import snapshot_brain_health, compare_snapshots

# Take BEFORE snapshot at the start (before Step 3)
before = snapshot_brain_health("marco", graph_ops)

# ... citizen processes all chunks ...

# Take AFTER snapshot
after = snapshot_brain_health("marco", graph_ops)

# Compare
verdict = compare_snapshots(before, after)

if verdict.approved:
    print(f"APPROVED: {verdict.reason}")
else:
    print(f"REJECTED: {verdict.reason}")
    # Manual review needed — citizen may have created low-quality nodes
```

In self-discovery mode, rollback is manual (the citizen created nodes directly). The quality gate serves as a health check, not an automatic rollback trigger. If rejected, a human reviews the degraded metrics and decides whether to prune specific nodes.

### Step 5: Verify

Check the result by querying the citizen's brain:

```python
# Count new memories
nodes = graph_ops.get_all_nodes(graph_name="brain_marco")
memories = [n for n in nodes if n.get("memory_type")]
spaces = [n for n in nodes if n.get("space_type") == "conversation"]
print(f"{len(memories)} memories across {len(spaces)} conversation spaces")
```

---

## MODE 2: AUTOMATED PIPELINE — END TO END

Used when the citizen cannot run a Claude Code session. An external LLM extracts memories on the citizen's behalf.

### Step 1: Obtain Conversation Exports

Same as Mode 1. Same formats, same export procedures.

### Step 2: Run the Pipeline

Single function call:

```python
from runtime.anamnesis import run_anamnesis

result = run_anamnesis(
    citizen_handle="marco",
    corpus_paths=[
        "claude_export.json",
        "chatgpt_export.zip",
        "telegram_chat.json",
    ],
    embed_fn=embed,      # Callable(str) -> list[float]  (1536 dims)
    llm_fn=extract,      # Callable(str) -> str  (prompt -> JSON string)
    graph_ops=ctx.graph_ops,  # FalkorDB GraphOps instance. None = dry-run.
)
```

**What `embed_fn` must be:** A function that takes a string and returns a list of floats (1536 dimensions, matching `text-embedding-3-small`). Example:

```python
from openai import OpenAI
client = OpenAI()

def embed(text: str) -> list[float]:
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding
```

**What `llm_fn` must be:** A function that takes a prompt string and returns a JSON string. The prompt contains a conversation chunk and asks for extracted memories. Example:

```python
def extract(prompt: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content
```

### Step 3: What the Pipeline Does Internally

The orchestrator (`anamnesis.py`) runs 4 numbered steps:

**Step 0/4 — Snapshot brain health BEFORE:**
`quality_gate.snapshot_brain_health()` measures 6 metrics on the existing brain.

**Step 1/4 — Parse all corpora:**
`corpus_parser.parse_corpus()` on each file. Auto-detects format. Handles ZIPs transparently. Produces `list[ConversationTurn]`.

**Step 2/4 — Extract memories (LLM):**
`node_extractor.extract_nodes()` groups turns by conversation, chunks conversations into batches of 40 turns (`CHUNK_MAX_TURNS`), sends each chunk to the LLM with the extraction prompt. The LLM returns JSON arrays of extracted nodes. Nodes below significance 0.25 (`MIN_SIGNIFICANCE`) are discarded. Each node carries its `turn_index` for order preservation.

**Step 3/4 — Integrate into brain:**
`brain_integrator.integrate_clusters()` runs a 5-step sub-pipeline:

1. **Embed:** Call `embed_fn` on each extracted node. Discard nodes with embedding magnitude < 0.05.
2. **Build spaces:** Create `IntegratedSpace` per conversation with centroid (mean of moment embeddings, normalized).
3. **Deduplicate:** Remove moments with cosine similarity > 0.92 against existing brain memories and against other new moments. Cross-space dedup catches the same conversation exported from two accounts.
4. **Anchor:** Link each moment to the top-3 most similar existing brain nodes (non-moment nodes: traits, values, knowledge). Link types: `reinforces` (>0.8), `associates` (0.5-0.8), `contextualizes` (0.3-0.5).
5. **Persist:** Write to FalkorDB (`brain_{handle}`):
   - Space nodes (type `space`, subtype `conversation`)
   - Moment nodes (type `moment`) with `[occurred_in]` links to their space
   - Chain links: `[next]` between sequential moments within a space
   - Anchor links to existing brain nodes
   - Cross-conversation `[echoes]` links (moments in different conversations with similarity > 0.6)
   - Space continuity `[continues]` links (conversations with centroid similarity > 0.5)

**Step 4/4 — Quality gate AFTER:**
`quality_gate.snapshot_brain_health()` again, then `compare_snapshots()`. If REJECTED, `_rollback_session()` deletes all nodes tagged with this session's `anamnesis_session` property (FalkorDB DETACH DELETE cascades link removal).

### Step 4: Inspect the Result

```python
print(f"Success: {result.success}")
print(f"Files processed: {result.files_processed}")
print(f"Turns parsed: {result.turns_parsed}")
print(f"Conversations found: {result.conversations_found}")
print(f"Nodes extracted: {result.nodes_extracted}")
print(f"Spaces created: {result.spaces_created}")
print(f"Moments persisted: {result.moments_persisted}")
print(f"Chain links: {result.chain_links}")
print(f"Anchor links: {result.anchor_links}")
print(f"Cross-conv links: {result.cross_conv_links}")
print(f"Dedup removed: {result.dedup_removed}")
print(f"Duration: {result.duration_seconds:.1f}s")

if result.quality_verdict:
    v = result.quality_verdict
    print(f"Quality: {'APPROVED' if v.approved else 'REJECTED'}")
    print(f"Reason: {v.reason}")
    for imp in v.improvements:
        print(f"  + {imp}")
    for deg in v.degradations:
        print(f"  - {deg}")

if result.errors:
    for err in result.errors:
        print(f"ERROR: {err}")
```

---

## QUALITY GATE — BOTH MODES

### 6 Metrics

| Metric | What It Measures | How | Healthy Range |
|--------|-----------------|-----|---------------|
| `cognitive_balance` | Diversity of node types | Shannon entropy of type distribution, normalized to [0,1] | 0.6-1.0 (balanced) |
| `connectivity` | Richness of associations | Average links per node | 1.0+ (well-connected) |
| `embedding_spread` | Semantic diversity | Mean pairwise cosine distance (sampled, up to 100 nodes) | 0.2-0.7 (neither collapsed nor scattered) |
| `node_quality` | Signal strength | Mean of (embedding magnitude x log(content length + 1)) | Higher = better |
| `cluster_coherence` | Thematic structure | Ratio of within-space similarity to between-space similarity | >1.0 (conversations are internally coherent) |
| `uniqueness` | Absence of duplicates | 1 - (duplicate pairs found / pairs checked), threshold 0.92 | >0.9 |

### Decision Logic

```
IF brain was empty before → AUTO-APPROVE (first anamnesis)
ELSE:
  count stable_or_improved = metrics where after >= before (within 0.1% tolerance)
  count degraded = metrics where after < before

  IF any metric degraded > 10% → REJECT (severe degradation)
  ELSE IF stable_or_improved >= 4 → APPROVE
  ELSE → REJECT (insufficient metrics stable)
```

### Rollback (Automated Mode Only)

On rejection, `_rollback_session()` issues:
```cypher
MATCH (n {anamnesis_session: '{session_id}'}) DETACH DELETE n RETURN count(n)
```

All nodes from the session are tagged with `anamnesis_session` during persistence, making rollback surgical. FalkorDB's `DETACH DELETE` removes connected links automatically.

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `parse_corpus()` | `corpus_parser.py` | Both modes — first step of any anamnesis |
| `prepare_discovery()` | `session_preparer.py` | Mode 1 — human prepares session for citizen |
| `save_session_to_disk()` | `session_preparer.py` | Mode 1 — write chunks to disk |
| `run_anamnesis()` | `anamnesis.py` | Mode 2 — full automated pipeline |
| `snapshot_brain_health()` | `quality_gate.py` | Both modes — before and after |
| `compare_snapshots()` | `quality_gate.py` | Both modes — final verdict |

---

## DATA FLOW: AUTOMATED PIPELINE

```
corpus files (JSON, ZIP, TXT, MD)
    |
    v  parse_corpus() per file               [corpus_parser.py]
list[ConversationTurn]
    |
    v  extract_nodes()                       [node_extractor.py]
list[ConversationCluster]                    (grouped, ordered, 17 types)
    |
    v  integrate_clusters()                  [brain_integrator.py]
    |   |
    |   +-- _embed_and_build_spaces()        embed_fn per node -> IntegratedSpace[]
    |   +-- _deduplicate_spaces()            cosine > 0.92 removed
    |   +-- _anchor_all_moments()            top-3 brain links per moment
    |   +-- _persist_all()                   write to brain_{handle}
    |   +-- _build_cross_conversation_links() echoes across convs
    |   +-- _build_space_continuity_links()  continues between spaces
    |
IntegrationResult
    |
    v  compare_snapshots(before, after)      [quality_gate.py]
QualityVerdict  ->  APPROVE or REJECT + rollback
```

## DATA FLOW: CITIZEN SELF-DISCOVERY

```
corpus files (JSON, ZIP, TXT, MD)
    |
    v  prepare_discovery()                   [session_preparer.py]
    |   |
    |   +-- parse_corpus() per file          [corpus_parser.py]
    |   +-- group by conversation
    |   +-- chunk into 30-turn pieces
    |
DiscoverySession
    |
    v  save_session_to_disk()                [session_preparer.py]
    |
instruction.md + chunks/*.md + manifest.json
    |
    v  Citizen reads in Claude Code session
    |   |
    |   +-- graph_write(space) per conversation     [MCP tool -> L3]
    |   +-- graph_write(moment) per memory          [MCP tool -> L3]
    |   +-- think() for internal reflection         [MCP tool -> L1]
    |
brain_{handle} updated
    |
    v  compare_snapshots(before, after)      [quality_gate.py]
QualityVerdict  ->  health check for human review
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
anamnesis.py (orchestrator)
    +-- corpus_parser.py       (ConversationTurn, parse_corpus)
    +-- node_extractor.py      (extract_nodes, ConversationCluster)
    |       +-- corpus_parser.py   (ConversationTurn)
    +-- brain_integrator.py    (integrate_clusters, IntegrationResult)
    |       +-- node_extractor.py  (ExtractedNode, ConversationCluster)
    +-- quality_gate.py        (snapshot_brain_health, compare_snapshots)

session_preparer.py (Mode 1 prep)
    +-- corpus_parser.py       (ConversationTurn, parse_corpus)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `numpy` | Cosine similarity, embedding operations, entropy | `quality_gate.py`, `brain_integrator.py` |
| `json` | Parse all JSON formats | `corpus_parser.py`, `node_extractor.py`, `session_preparer.py` |
| `zipfile` | Handle ChatGPT/Gemini ZIP archives | `corpus_parser.py` |
| `re` | WhatsApp date pattern, markdown splitting | `corpus_parser.py` |
| `hashlib` | 8-char content hashes for node IDs | `brain_integrator.py` |

No external API packages are imported. The `embed_fn` and `llm_fn` callables are injected, keeping the module independent of any specific LLM provider.

---

## CONFIGURATION

| Config | Location | Default | Controls |
|--------|----------|---------|----------|
| `TURNS_PER_SESSION` | `session_preparer.py` | 30 | Turns per discovery chunk |
| `MAX_CONTENT_PER_TURN` | `session_preparer.py` | 800 | Max chars per turn in chunks |
| `MIN_SIGNIFICANCE` | `node_extractor.py` | 0.25 | Floor for node extraction |
| `CHUNK_MAX_TURNS` | `node_extractor.py` | 40 | Turns per LLM extraction batch |
| `DEDUP_THRESHOLD` | `brain_integrator.py` | 0.92 | Cosine similarity for duplicate detection |
| `ANCHOR_MIN_SIMILARITY` | `brain_integrator.py` | 0.3 | Minimum similarity for brain anchoring |
| `ANCHOR_TOP_K` | `brain_integrator.py` | 3 | Max anchor links per moment |
| `CROSS_CONV_SIMILARITY` | `brain_integrator.py` | 0.6 | Threshold for cross-conversation echoes |
| `SPACE_CONTINUITY_THRESHOLD` | `brain_integrator.py` | 0.5 | Threshold for space-to-space continuity |
| `MAX_DEGRADATION` | `quality_gate.py` | 0.10 | Max allowed metric degradation (10%) |

---

## GRAPH SCHEMA PRODUCED

### Node: Conversation Space

```yaml
space:conv:{handle}_{hash8}:
  node_type: space
  name: "Conversation title"  # truncated to 80 chars
  content: "Conversation on {platform}. {N} turns, {M} significant moments. Participants: ..."
  synthesis: "Conversation space: {title}"
  embedding: centroid of moment embeddings (R^1536)
  properties:
    space_type: "conversation"
    source_platform: "claude" | "chatgpt" | "gemini" | "grok" | "telegram" | "whatsapp" | "discord"
    conversation_id: original ID from export
    participants: "speaker1,speaker2"
    timestamp_start: ISO-8601 or ""
    timestamp_end: ISO-8601 or ""
    turn_count: int
    moment_count: int
    anamnesis_session: session UUID
```

### Node: Memory Moment

```yaml
moment:{handle}_{hash8}:
  node_type: moment
  name: "First 60 chars of content"
  content: "1-3 sentence memory in first person"
  synthesis: "Memory ({type}) via anamnesis"
  embedding: R^1536
  properties:
    weight: 0.0-1.0 (significance)
    energy: 0.1 (initial, physics will evolve)
    stability: 0.3 (initial, physics will evolve)
    memory_type: one of 17 types
    source_platform: platform name
    source_conversation: conversation ID
    timestamp: ISO-8601 or ""
    participants: "speaker1,speaker2"
    sequence_position: int (global order)
    anamnesis_session: session UUID
```

### Links

| Link Type | From | To | Weight | Meaning |
|-----------|------|----|--------|---------|
| `occurred_in` | moment | space | 1.0 | Moment happened in this conversation |
| `next` | moment | moment | 0.8 | Temporal sequence within conversation |
| `reinforces` | moment | brain node | >0.8 | Memory strongly supports existing trait/value |
| `associates` | moment | brain node | 0.5-0.8 | Memory relates to existing node |
| `contextualizes` | moment | brain node | 0.3-0.5 | Memory provides background |
| `echoes` | moment | moment | >0.6 | Same idea across different conversations |
| `continues` | space | space | >0.5 | Thematic continuation between conversations |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Line | Reference |
|------|------|-----------|
| `corpus_parser.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Step 1)` |
| `node_extractor.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Step 2)` |
| `brain_integrator.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Steps 3-6)` |
| `quality_gate.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/VALIDATION_The_Anamnesis.md` |
| `session_preparer.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/` |
| `anamnesis.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/` |
| `__init__.py` | 1 | `# DOCS: mind-protocol/docs/memory/the_anamnesis/` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 1 (Parse) | `corpus_parser.py:parse_corpus()` |
| ALGORITHM Step 2 (Extract) | `node_extractor.py:extract_nodes()` |
| ALGORITHM Step 3 (Embed) | `brain_integrator.py:_embed_and_build_spaces()` |
| ALGORITHM Step 4 (Anchor) | `brain_integrator.py:_anchor_all_moments()` |
| ALGORITHM Step 5 (Dedup) | `brain_integrator.py:_deduplicate_spaces()` |
| ALGORITHM Step 6 (Persist) | `brain_integrator.py:_persist_all()` |
| Quality Gate | `quality_gate.py:snapshot_brain_health()`, `compare_snapshots()` |
| Session Prep (Mode 1) | `session_preparer.py:prepare_discovery()`, `save_session_to_disk()` |
| Orchestrator (Mode 2) | `anamnesis.py:run_anamnesis()` |
| Rollback | `anamnesis.py:_rollback_session()` |

---

## EXTRACTION CANDIDATES

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `corpus_parser.py` | 729L | <400L | `parsers/ai_chat_parsers.py` | `_parse_claude`, `_parse_chatgpt`, `_parse_gemini`, `_parse_grok` + helpers |
| `corpus_parser.py` | 729L | <400L | `parsers/messaging_parsers.py` | `_parse_telegram`, `_parse_whatsapp`, `_parse_discord` |
| `brain_integrator.py` | 566L | <400L | `cross_linker.py` | `_build_cross_conversation_links`, `_build_space_continuity_links` |

---

## MARKERS

<!-- @mind:proposition corpus_parser.py is at SPLIT threshold (729L). Next feature addition should trigger extraction into a parsers/ subpackage with one file per platform family. -->
<!-- @mind:proposition Mode 1 quality gate could be automated by wrapping the citizen's Claude Code session in a script that snapshots before and after. Currently manual. -->
