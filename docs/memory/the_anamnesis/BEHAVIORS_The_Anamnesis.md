# The Anamnesis — Behaviors: What It Should Do

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
THIS:            BEHAVIORS_The_Anamnesis.md (you are here)
ALGORITHM:       ./ALGORITHM_The_Anamnesis.md
VALIDATION:      ./VALIDATION_The_Anamnesis.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Anamnesis.md
HEALTH:          ./HEALTH_The_Anamnesis.md
SYNC:            ./SYNC_The_Anamnesis.md
```

---

## How to Export Your Conversations

The Anamnesis ingests conversations from any major AI platform. Here's how to get your data out.

### Claude (claude.ai)

1. Go to **Settings** > **Account**
2. Click **Export Data**
3. You'll receive an email with a download link
4. Download the ZIP — inside is `conversations.json`
5. Feed this file to the Anamnesis

**Format:** JSON array of conversation objects with `chat_messages`
**Identifier:** `"sender": "human"` / `"sender": "assistant"`
**Content field:** `text`, `content` (string), or `content` (array of parts)

### ChatGPT (chat.openai.com)

1. Go to **Settings** > **Data Controls** > **Export Data**
2. Click **Export**
3. You'll receive an email with a download link
4. Download the ZIP — inside is `conversations.json`
5. Feed the ZIP or the extracted JSON to the Anamnesis

**Format:** JSON array of conversation objects with `mapping` (tree structure)
**Identifier:** `author.role`: `"user"` / `"assistant"` / `"system"`
**Content field:** `content.parts[]` (array of strings)
**Note:** Messages are stored in a tree via `mapping` dict, not a flat list. The parser walks the parent chain to reconstruct order.

### Gemini (gemini.google.com)

1. Go to **Google Takeout** (takeout.google.com)
2. Deselect all, then select **Gemini Apps**
3. Click **Export**
4. Download the ZIP
5. Feed the ZIP or individual JSON files to the Anamnesis

**Format:** JSON files per conversation. Messages have `role` and `parts[{text}]`
**Identifier:** `role`: `"user"` / `"model"`
**Content field:** `parts[].text`
**Note:** Older exports (when it was "Bard") have slightly different structure — the parser handles both.

### Grok (x.com / grok.x.ai)

1. Go to X **Settings** > **Your Account** > **Download an archive of your data**
2. Or use grok.x.ai settings to export conversations
3. Download the archive
4. Feed the JSON file(s) to the Anamnesis

**Format:** JSON with `grok_conversations` or `grokMessages`
**Identifier:** `sender`: `"user"` / `"assistant"`
**Content field:** `message` or `text`
**Note:** X/Grok export format is still evolving. The parser handles multiple known structures.

### Telegram

1. Open **Telegram Desktop**
2. Go to a chat > click **⋮** > **Export Chat History**
3. Choose JSON format, uncheck media
4. Export produces `result.json`

### WhatsApp

1. Open a chat > tap **⋮** > **More** > **Export Chat**
2. Choose **Without Media**
3. Produces a `.txt` file with timestamped messages

### Discord

1. Use **DiscordChatExporter** (open source tool)
2. Export to JSON format
3. Feed the JSON to the Anamnesis

---

## Observable Behaviors

### B1: Auto-detection (O3, P5)

When a file is provided without explicit format, the parser inspects the content and auto-detects:
- JSON with `chat_messages` → Claude
- JSON with `mapping` → ChatGPT
- JSON with `parts` in messages → Gemini
- JSON with `grok_conversations` → Grok
- JSON with `from` in messages → Telegram
- JSON with `author` in messages → Discord
- TXT with date pattern → WhatsApp
- ZIP with `conversations.json` → ChatGPT
- ZIP with Gemini folder → Gemini
- `.md` with frontmatter → System prompt

### B2: ZIP handling (O3)

ChatGPT and Gemini exports come as ZIP archives. The parser handles them directly — no manual extraction needed. Just point the Anamnesis at the ZIP.

### B3: Signal extraction (O2)

The LLM extractor distinguishes:
- **Signal:** Insights, decisions, values, relationships, knowledge, emotions, commitments
- **Noise:** Greetings, filler, acknowledgments, repetitions

A 50-turn conversation might produce 3 meaningful nodes. That's correct.

### B4: Idempotency (O3)

Running the same corpus twice produces the same brain state. The deduplicator catches near-identical nodes (cosine similarity > 0.92) and merges their provenance rather than creating duplicates.

### B5: Provenance tracking (O4)

Every memory node carries: source platform, conversation ID, timestamp, participants. The citizen knows where each memory came from.

### B6: Cross-platform deduplication (O3)

The same conversation exported from two different accounts (e.g., Claude and ChatGPT versions of the same exchange) produces near-identical embeddings. The deduplicator catches these cross-platform duplicates.

### B7: Incremental ingestion (O3)

The citizen can undergo anamnesis monthly. Each run adds new memories without corrupting existing ones. Old memories aren't re-processed — only new unique content is added.

### B8: Identity preservation (O5)

Memories inform but do not overwrite identity nodes. Trait, value, and personality nodes established by the Prism or through lived experience remain unchanged. Only `moment` type nodes are created.

---

## Usage Examples

```python
from runtime.anamnesis import run_anamnesis

# Single Claude export
result = run_anamnesis(
    citizen_handle="silas",
    corpus_paths=["conversations_claude.json"],
    embed_fn=embed,
    llm_fn=extract,
    graph_ops=ctx.graph_ops,
)

# Multiple platforms at once
result = run_anamnesis(
    citizen_handle="marco",
    corpus_paths=[
        "claude_export.json",
        "chatgpt_export.zip",
        "gemini_takeout.zip",
        "grok_conversations.json",
        "telegram_chat.json",
        "whatsapp_chat.txt",
        "old_system_prompt.md",
    ],
    embed_fn=embed,
    llm_fn=extract,
    graph_ops=ctx.graph_ops,
)
# All formats auto-detected. Duplicates across platforms handled.
```
