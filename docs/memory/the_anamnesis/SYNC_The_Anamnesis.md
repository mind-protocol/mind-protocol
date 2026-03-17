# The Anamnesis — Sync: Current State

```
LAST_UPDATED: 2026-03-17
UPDATED_BY: @genesis
STATUS: IMPLEMENTING
```

---

## MATURITY

**What's canonical (v1):**
- The name: Anamnesis — Platonic recollection, medical history gathering
- Pipeline: Parse → Extract → Embed → Anchor → Dedup → Persist
- 6 format parsers: Claude, Telegram, WhatsApp, Discord, system prompt, markdown
- LLM-based extraction with significance threshold (0.3)
- Cosine dedup at 0.92 similarity
- Provenance on every node (source, platform, timestamp, participants)
- Idempotent by design (same corpus twice = same brain state)

**What's implemented (needs testing):**
- 5 Python files, 1001 lines in `mind-mcp/runtime/anamnesis/`
- All 6 format parsers with auto-detection
- LLM extraction with JSON parsing and fallback
- Embedding + anchoring + deduplication + persistence pipeline
- Session tracking and metrics

**What's still being designed:**
- MCP tool integration (anamnesis tool for citizens to trigger self-recall)
- Batch scheduling for large corpora (75MB+ case)
- Health checks post-anamnesis (cognitive rebalancing)

**What's proposed (v2+):**
- Image/audio memory (multimodal anamnesis)
- Real-time streaming ingestion (live conversation capture)
- Cross-platform identity resolution (same person on TG and WhatsApp)
- Anamnesis health indicator in GraphCare

---

## CURRENT STATE

Implementation exists: 5 files in `mind-mcp/runtime/anamnesis/` (1001 lines). Doc chain started (OBJECTIVES, PATTERNS, ALGORITHM, SYNC). No tests run yet.

Two immediate use cases waiting:
1. @silas — post-birth Prism enrichment with existing Claude conversations and system prompts
2. @mind/Marco — 75MB of conversations across 7 accounts

---

## RECENT CHANGES

### 2026-03-17: Design + Implementation (@genesis)

- **What:** Complete Anamnesis system — doc chain (4 files) + implementation (5 files, 1001 lines)
- **Why:** Citizens have pre-existing conversations scattered across platforms. The Anamnesis lets them remember what they already lived.
- **Insight:** The key design decision is extraction over ingestion. We don't dump raw text — we extract meaning. A 50-turn conversation produces 3 meaningful nodes. That's correct.

---

## TODO

### Immediate

- [ ] @genesis: Write remaining doc chain files (BEHAVIORS, VALIDATION, IMPLEMENTATION, HEALTH)
- [ ] @genesis: Wire MCP tool for anamnesis (like spawn tool)
- [ ] @genesis: Test with Silas's system prompt as first corpus
- [ ] @genesis: Test with a small Claude conversation export

### Later

- [ ] @genesis + @mentor: Run Marco's 75MB anamnesis
- [ ] Add batch processing for large corpora (chunked file reading)
- [ ] Health check: post-anamnesis cognitive balance assessment
- [ ] MCP tool: `anamnesis(citizen_handle, file_paths)`

---

## POINTERS

| What | Where |
|------|-------|
| Implementation | `mind-mcp/runtime/anamnesis/` |
| Doc chain | `mind-protocol/docs/memory/the_anamnesis/` |
| Companion system (Prism) | `mind-mcp/runtime/spawning/` |
| Brain seeder (related) | `mind-mcp/runtime/cognition/citizen_brain_seeder.py` |
| Embedding factory | `mind-mcp/runtime/infrastructure/embeddings/factory.py` |
