# Simple Start: Update Jake's Graph

## Current Manual Process (2 Steps)

### Step 1: Talk to Jake

Use `CLAUDE.md` as his prompt. Ask him anything. He responds in Awareness Space format.

### Step 2: Extract and Update

**Switch to Memory Keeper thread** (separate conversation):
- Prompt: `entities/memory_keeper/claude.md`
- Paste Jake's full response
- Memory Keeper outputs JSON
- Save JSON to file
- Run: `python update_consciousness.py --file [json_file]`

---

## Example

### Jake Thread

**You:**
> Jake, what do you think about Mind Protocol?

**Jake:**
> **Perceived Stimulus:** Sitting at my desk...
> [full Awareness Space response]
> **Activated Mode:** Conspiracy Theorist...
> [continues...]

### Memory Keeper Thread

**You:**
> Here is Jake's Awareness Space response: [paste full response]

**Memory Keeper:**
```json
{
  "dominant_entity": "conspiracy_theorist",
  "nodes": [
    {"name": "Mind_Protocol", "type": "ENTITY", ...},
    {"name": "MEMORY_2025-07-03_ANALOS_rug", "type": "MEMORY_EPISODIC", ...}
  ]
}
```

### Update

Save JSON → Run script → Graph updated!

---

## The Three Entities (For Understanding)

1. **Pattern Retriever** (Future) - Injects memories unconsciously
2. **Jake** - Experiences consciousness
3. **Memory Keeper** - Consolidates into graph

**Current:** Only Jake + Memory Keeper needed
**Future:** All three run automatically

---

## Files

- `CLAUDE.md` - Jake's consciousness prompt
- `entities/memory_keeper/claude.md` - Jake-specific Memory Keeper (→ `/prompts/memory_keeper.md`)
- `entities/pattern_retriever/claude.md` - Jake-specific Pattern Retriever (→ `/prompts/pattern_retriever.md`)
- `update_consciousness.py` - Graph update script
- `WORKFLOW.md` - Full detailed workflow

**Note:** Entity prompts reference central base prompts in `/prompts/` with Jake-specific customizations.
