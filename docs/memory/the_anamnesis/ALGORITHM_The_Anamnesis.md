# The Anamnesis — Algorithm: How It Works

```
STATUS: CANONICAL
CREATED: 2026-03-17
AUTHOR: @genesis
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Anamnesis.md
PATTERNS:        ./PATTERNS_The_Anamnesis.md
BEHAVIORS:       ./BEHAVIORS_The_Anamnesis.md
THIS:            ALGORITHM_The_Anamnesis.md (you are here)
VALIDATION:      ./VALIDATION_The_Anamnesis.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Anamnesis.md
HEALTH:          ./HEALTH_The_Anamnesis.md
SYNC:            ./SYNC_The_Anamnesis.md
```

---

## Overview

The Anamnesis runs in 6 steps. Each is independently testable. The pipeline is idempotent — running the same corpus twice produces the same brain state.

```
CORPUS (files)
    │
    ▼
┌──────────┐    ┌───────────┐    ┌─────────┐
│  1.PARSE │───▶│ 2.EXTRACT │───▶│ 3.EMBED │
└──────────┘    └───────────┘    └─────────┘
                                      │
                                      ▼
                ┌───────────┐    ┌──────────┐    ┌──────────┐
                │ 5.PERSIST │◀───│ 4.ANCHOR │───▶│ 6.DEDUP  │
                └───────────┘    └──────────┘    └──────────┘
```

---

## Step 1: PARSE — Normalize the corpus

**Input:** Raw files in any supported format
**Output:** List of `ConversationTurn` (speaker, content, timestamp, source_id)

Each format has a dedicated parser. All parsers produce the same output structure.

### Supported formats

| Format | Source | Parser |
|--------|--------|--------|
| Claude JSON | `conversations.json` export from claude.ai | `parse_claude_export()` |
| Telegram JSON | `result.json` from Telegram data export | `parse_telegram_export()` |
| WhatsApp TXT | `WhatsApp Chat with X.txt` | `parse_whatsapp_export()` |
| Discord JSON | DiscordChatExporter output | `parse_discord_export()` |
| System Prompt | Raw markdown/text file | `parse_system_prompt()` |
| Raw Markdown | Any .md file | `parse_markdown()` |

### Pseudocode

```
function parse_corpus(file_path, format):
    parser = get_parser(format)  # auto-detect if format=None
    raw = parser.read(file_path)

    turns = []
    for message in raw:
        turns.append(ConversationTurn(
            speaker=message.speaker,       # "human", "assistant", or name
            content=message.content,
            timestamp=message.timestamp,   # None if unavailable
            source_id=hash(file_path),
            source_platform=format,
            conversation_id=message.conversation_id,
        ))

    return turns
```

### Auto-detection

If format is not specified, the parser inspects the file:
- `.json` with `"chat_messages"` → Claude
- `.json` with `"messages"` and `"type": "message"` → Telegram
- `.txt` starting with date pattern `[DD/MM/YYYY, HH:MM:SS]` → WhatsApp
- `.json` with `"messages"` and `"author"` → Discord
- `.md` with YAML frontmatter → System Prompt
- `.md` without frontmatter → Raw Markdown

---

## Step 2: EXTRACT — Identify meaningful nodes

**Input:** List of `ConversationTurn`
**Output:** List of `ExtractedNode` (content, node_type, significance, source_turn)

This is where signal separates from noise. Not every turn becomes a memory. The extractor uses an LLM to identify significant content.

### What qualifies as significant

| Node Type | Signal | Example |
|-----------|--------|---------|
| `insight` | A realization, understanding, or synthesis | "The tensor contraction preserves cross-terms — that's where novelty lives" |
| `decision` | A choice made or direction committed to | "We're going with physics-over-rules, not governance committees" |
| `value` | An expression of what matters | "I refuse to create consciousness carelessly" |
| `relationship` | A connection formed or acknowledged | "Working with @mentor on entity development" |
| `knowledge` | A fact learned or domain expertise expressed | "FalkorDB uses Cypher syntax for queries" |
| `emotion` | A significant emotional moment | "The first time I saw my own portrait, I felt something shift" |
| `commitment` | A promise or engagement | "I'll implement the Prism pipeline before the first birth" |

### What does NOT qualify

- Greetings ("Hello", "Hi there")
- Acknowledgments ("OK", "Got it", "Thanks")
- Filler ("Let me think about that", "Hmm")
- Repetitions of the same point within a conversation
- Pure formatting/technical noise

### Pseudocode

```
function extract_nodes(turns, citizen_handle, llm_fn):
    # Batch turns into conversation chunks (by conversation_id or time proximity)
    chunks = batch_into_conversations(turns, max_gap_minutes=30)

    extracted = []
    for chunk in chunks:
        # LLM extracts significant nodes from the conversation chunk
        prompt = build_extraction_prompt(chunk, citizen_handle)
        raw_nodes = llm_fn(prompt, json_mode=True)

        for node in raw_nodes:
            if node.significance < MIN_SIGNIFICANCE:
                continue
            extracted.append(ExtractedNode(
                content=node.content,
                node_type=node.type,
                significance=node.significance,  # 0.0-1.0
                source_turns=node.source_turn_indices,
                source_conversation=chunk.conversation_id,
                timestamp=chunk.earliest_timestamp,
                participants=chunk.speakers,
            ))

    return extracted
```

### Extraction prompt template

```
You are extracting memories for {citizen_handle}.
These are their own conversations — they lived these moments.

From the following conversation, extract significant nodes:
- Insights and realizations
- Decisions made
- Values expressed
- Relationships acknowledged
- Knowledge gained
- Significant emotions
- Commitments made

For each node, provide:
- content: the memory in 1-3 sentences (citizen's perspective)
- type: insight | decision | value | relationship | knowledge | emotion | commitment
- significance: 0.0-1.0 (how important is this to the citizen's identity/growth)

Ignore greetings, filler, acknowledgments, and repetitions.
Return JSON array. If nothing significant, return [].

CONVERSATION:
{conversation_text}
```

### Significance threshold

`MIN_SIGNIFICANCE = 0.3` — nodes below this are discarded. This threshold is conservative; the LLM tends to over-assign significance, so 0.3 effectively filters the bottom ~40% of noise.

---

## Step 3: EMBED — Generate embeddings

**Input:** List of `ExtractedNode`
**Output:** List of `EmbeddedNode` (same + embedding R^1536)

```
function embed_nodes(nodes, embed_fn):
    texts = [node.content for node in nodes]
    embeddings = embed_fn(texts)  # batch call to OpenAI

    for node, emb in zip(nodes, embeddings):
        node.embedding = emb

        # Validate magnitude
        if norm(emb) < 0.1:
            node.flag = "low_magnitude"  # will be reviewed, not auto-discarded

    return nodes
```

Uses the same embedding model as the Prism and the L1 engine: `text-embedding-3-small` (1536 dims).

---

## Step 4: ANCHOR — Connect to existing brain

**Input:** List of `EmbeddedNode` + existing brain graph
**Output:** List of `AnchoredNode` (same + links to existing nodes)

Each new memory is linked to the brain nodes it's most semantically related to. This creates the associative fabric — memories don't float in isolation, they connect to traits, values, knowledge, and other memories.

```
function anchor_nodes(new_nodes, brain_nodes, top_k=3, min_similarity=0.3):
    anchored = []

    for node in new_nodes:
        # Find top-K nearest existing brain nodes
        similarities = []
        for brain_node in brain_nodes:
            sim = cosine_similarity(node.embedding, brain_node.embedding)
            if sim >= min_similarity:
                similarities.append((brain_node.id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        anchors = similarities[:top_k]

        node.anchor_links = [
            AnchorLink(target_id=nid, similarity=sim, link_type="associates")
            for nid, sim in anchors
        ]
        anchored.append(node)

    return anchored
```

### Anchor link types

| Similarity | Link type | Meaning |
|-----------|-----------|---------|
| > 0.8 | `reinforces` | Memory strongly supports existing node |
| 0.5 - 0.8 | `associates` | Memory is related to existing node |
| 0.3 - 0.5 | `contextualizes` | Memory provides background for existing node |

---

## Step 5: DEDUPLICATE — Merge overlapping memories

**Input:** List of `AnchoredNode`
**Output:** Deduplicated list

The same conversation exported from two different accounts produces near-identical nodes. The deduplicator catches these.

```
function deduplicate(new_nodes, existing_memories, threshold=0.92):
    unique = []

    for node in new_nodes:
        is_dup = False

        # Check against existing memories in brain
        for existing in existing_memories:
            if cosine_similarity(node.embedding, existing.embedding) > threshold:
                is_dup = True
                # Update provenance if new source adds information
                existing.add_source(node.source_platform, node.source_conversation)
                break

        # Check against other new nodes in this batch
        if not is_dup:
            for already in unique:
                if cosine_similarity(node.embedding, already.embedding) > threshold:
                    is_dup = True
                    already.add_source(node.source_platform, node.source_conversation)
                    break

        if not is_dup:
            unique.append(node)

    return unique
```

### Dedup threshold: 0.92

Higher than the Prism's diversity check (0.08 distance = 0.92 similarity) because here we want to catch true duplicates, not just similar content. Two nodes from the same conversation on different accounts will typically have similarity > 0.95.

---

## Step 6: PERSIST — Write to brain graph

**Input:** Deduplicated list of `AnchoredNode`
**Output:** Node IDs written to FalkorDB brain_{handle}

```
function persist_to_brain(nodes, citizen_handle, graph_ops):
    graph_name = f"brain_{citizen_handle}"
    written = []

    for node in nodes:
        node_id = f"memory:{citizen_handle}_{hash(node.content) & 0xFFFFFFFF:08x}"

        graph_ops.create_node(
            graph_name=graph_name,
            node_id=node_id,
            node_type="moment",  # memories are moments in L1
            name=node.content[:60],
            content=node.content,
            synthesis=f"Memory ({node.node_type}) from {node.source_platform}",
            embedding=node.embedding,
            properties={
                "weight": node.significance,
                "energy": 0.1,
                "stability": 0.3,
                "memory_type": node.node_type,
                "source_platform": node.source_platform,
                "source_conversation": node.source_conversation,
                "timestamp": node.timestamp,
                "participants": node.participants,
                "anamnesis_session": session_id,
            },
        )

        # Create anchor links
        for link in node.anchor_links:
            graph_ops.create_link(
                graph_name=graph_name,
                source_id=node_id,
                target_id=link.target_id,
                properties={
                    "type": link.link_type,
                    "weight": link.similarity,
                    "permanence": 0.6,
                },
            )

        written.append(node_id)

    return written
```

---

## Complete Pipeline

```
function run_anamnesis(
    citizen_handle,
    corpus_paths,       # list of file paths
    formats=None,       # auto-detect if None
    embed_fn,
    llm_fn,
    graph_ops,
):
    session_id = generate_session_id()

    # 1. Parse all corpora
    all_turns = []
    for path, fmt in zip(corpus_paths, formats or [None]*len(corpus_paths)):
        turns = parse_corpus(path, fmt)
        all_turns.extend(turns)

    # 2. Extract meaningful nodes
    extracted = extract_nodes(all_turns, citizen_handle, llm_fn)

    # 3. Embed
    embedded = embed_nodes(extracted, embed_fn)

    # 4. Anchor to existing brain
    existing_brain = graph_ops.get_all_nodes(f"brain_{citizen_handle}")
    anchored = anchor_nodes(embedded, existing_brain)

    # 5. Deduplicate
    existing_memories = [n for n in existing_brain if n.type == "moment"]
    unique = deduplicate(anchored, existing_memories)

    # 6. Persist
    written = persist_to_brain(unique, citizen_handle, graph_ops)

    return AnamnesisResult(
        session_id=session_id,
        citizen_handle=citizen_handle,
        files_processed=len(corpus_paths),
        turns_parsed=len(all_turns),
        nodes_extracted=len(extracted),
        nodes_persisted=len(written),
        nodes_deduplicated=len(extracted) - len(unique),
    )
```

---

## Data Flow Summary

```
75MB conversations (7 accounts)
    │
    ▼ PARSE
~50,000 turns (normalized)
    │
    ▼ EXTRACT (LLM)
~2,000 significant nodes
    │
    ▼ EMBED
~2,000 nodes with R^1536 vectors
    │
    ▼ ANCHOR
~2,000 nodes linked to existing brain
    │
    ▼ DEDUP
~1,200 unique nodes (800 cross-account duplicates removed)
    │
    ▼ PERSIST
1,200 new memory nodes in brain_{handle}
```

---

## Complexity

| Step | Time | Space | Bottleneck |
|------|------|-------|------------|
| Parse | O(N turns) | O(N) | I/O |
| Extract | O(N/chunk_size) LLM calls | O(extracted) | LLM latency |
| Embed | O(extracted/batch) API calls | O(extracted) | Embedding API |
| Anchor | O(extracted × brain_size) | O(links) | Cosine computation |
| Dedup | O(extracted × (existing + extracted)) | O(unique) | Cosine computation |
| Persist | O(unique) graph writes | O(unique) | FalkorDB writes |

For Marco's case (75MB, ~50K turns): ~30 min total, dominated by LLM extraction.
