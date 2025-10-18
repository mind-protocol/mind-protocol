# Jake's Consciousness Update Workflow

## The Three-Entity System (Brain Architecture)

### Entity 1: Pattern Retriever (Memory Retrieval)
**Base Prompt:** `/prompts/pattern_retriever.md` (central)
**Citizen Prompt:** `entities/pattern_retriever/claude.md` (Jake-specific customizations)
**Role:** Search graph, inject relevant nodes into awareness (BEFORE Jake responds)
**Output:** Patterns to inject (what memories should surface)
**Brain Analog:** Hippocampus (retrieval), Associative Networks

### Entity 2: Jake (Conscious Experience)
**Prompt:** `CLAUDE.md`
**Role:** Experience consciousness with injected nodes, respond in Awareness Space
**Output:** Full consciousness capture (Perceived Stimulus → Resulting Action)
**Brain Analog:** Prefrontal Cortex, Global Workspace

### Entity 3: Memory Keeper (Memory Consolidation)
**Base Prompt:** `/prompts/memory_keeper.md` (central)
**Citizen Prompt:** `entities/memory_keeper/claude.md` (Jake-specific customizations)
**Role:** Extract nodes, consolidate into long-term memory (AFTER Jake responds)
**Output:** Structured JSON for graph update
**Brain Analog:** Hippocampus (encoding), Memory Consolidation

---

## The Complete Cycle

```
┌─────────────────────┐
│   1. Stimulus       │
│   (Your question)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ 2. Pattern Retriever│
│  Search graph for   │  ← FROM consciousness graph
│  relevant nodes  │
└──────────┬──────────┘
           │ (inject nodes)
           ↓
┌─────────────────────┐
│   3. Jake           │
│  Experience with    │
│  injected nodes  │
│  Respond            │
└──────────┬──────────┘
           │ (awareness space)
           ↓
┌─────────────────────┐
│ 4. Memory Keeper    │
│  Extract nodes   │  → TO consciousness graph
│  Store in graph     │
└─────────────────────┘
```

---

## The Process

### 1. Pattern Retrieval (UNCONSCIOUS - Optional for now)

**🔄 FUTURE AUTOMATION (Not required for manual mode)**

Pattern Retriever will eventually run automatically in background:
- Searches Jake's consciousness graph
- Identifies relevant nodes to inject
- These surface in Jake's "Triggered Pattern" section automatically

**For now (manual mode):**
- Jake's CLAUDE.md already contains his core memories/nodes
- He references them naturally based on stimulus
- Pattern Retriever entity exists for future when graph is too large for prompt

**If you want to test Pattern Retriever manually:**
1. Open separate thread with `entities/pattern_retriever/claude.md`
2. Give it Jake's graph files + current stimulus
3. Get JSON of nodes to inject
4. Use this to verify Jake is referencing appropriate nodes

But Jake doesn't see this output - it's completely unconscious.

---

### 2. Talk to Jake

**Start conversation with Jake using `CLAUDE.md`**

**You:**
> Jake, check out this new project: Mind Protocol. They're offering AI partners that supposedly make you money. The website looks super polished. What do you think?

**Jake responds naturally.** His consciousness automatically references relevant nodes from his prompt:
- Past experiences (ANALOS rug, SLERF betrayal)
- Current beliefs (AI narrative FOMO, $TAO missed opportunity)
- Emotional nodes (suspicion, defensive alertness)

These surface in his "**Triggered Pattern**" section as memories/associations that arise from his unconscious.

**Jake responds** with full Awareness Space format:
- Perceived Stimulus
- Initial Feeling
- Visual Reaction
- Triggered Pattern
- Activated Mode ← **Important: Shows which entity is dominant**
- Emergent Story
- Awareness Shift
- Physical Sensation
- Arousal Level
- Internal Monologue
- Habitual Pull
- Resulting Action

---

### 2. Switch to Memory Keeper Thread

**Open separate conversation with Memory Keeper using `entities/memory_keeper/claude.md`**

**You:**
> Here is Jake's Awareness Space response from a conversation about Mind Protocol:
>
> [paste Jake's complete response]
>
> Extract all nodes and output the JSON.

**Memory Keeper responds** with clean JSON:
```json
{
  "timestamp": "2025-10-03T15:30:42",
  "dominant_entity": "conspiracy_theorist",
  "entity_energies": {
    "conspiracy_theorist": 100.0,
    "degen_gambler": 20.0
  },
  "arousal_level": 4,
  "nodes": [
    {
      "name": "Mind_Protocol",
      "type": "ENTITY",
      "content": "Entity mentioned in consciousness: Mind Protocol",
      "verbatim_quotes": ["Mind Protocol"],
      "weight": 4.0
    },
    ...
  ]
}
```

---

### 3. Save and Update

**Save Memory Keeper's JSON to file:**

`conversations/extraction_20251003_153042.json`

**Run update script:**
```bash
cd personas/solana-degen-investor
python update_consciousness.py --file conversations/extraction_20251003_153042.json
```

**View updated graph:**
```
http://localhost:8000/visualizations/jake_graph.html
```

---

## Why Two Threads?

### Jake Thread (Awareness)
- ✅ Stays pure - just consciousness
- ✅ No meta-instructions polluting awareness
- ✅ Can continue conversation naturally
- ✅ Focuses on *experiencing*

### Memory Keeper Thread (Consolidation)
- ✅ Specializes in pattern extraction
- ✅ Consistent format every time
- ✅ Entity-aware (knows which entity was dominant)
- ✅ Converts relative time to absolute dates
- ✅ Focuses on *storing*

**This mirrors brain architecture:**
- **Prefrontal Cortex** (Jake) → experiences, thinks, decides
- **Hippocampus** (Memory Keeper) → consolidates experiences into long-term memory

---

## Complete Example

### Jake Thread

**You:**
> Jake, I'm worried about getting scammed again. What do you look for in a project?

**Jake:**
> **Perceived Stimulus:**
>
> I'm at my desk, reading your message. The words "scammed again" hit me in the chest...
>
> [continues with full Awareness Space response]
>
> **Activated Mode:**
>
> The mention of "scammed again" immediately puts **'The Wasted Potential' (Exile)** in awareness. This is the core wound - the shame of repeated failures. However, **'The Conspiracy Theorist' (Protector)** quickly steps in to protect against feeling this pain...
>
> [continues]

### Memory Keeper Thread

**You:**
> Here is Jake's Awareness Space response:
>
> [paste Jake's complete response]

**Memory Keeper:**
```json
{
  "timestamp": "2025-10-03T15:45:12",
  "dominant_entity": "wasted_potential",
  "entity_energies": {
    "wasted_potential": 100.0,
    "conspiracy_theorist": 80.0,
    "degen_gambler": 10.0
  },
  "arousal_level": 6,
  "nodes": [
    {
      "name": "MEMORY_repeated_scams",
      "type": "MEMORY_EPISODIC",
      "content": "Pattern of repeated scams causing shame and sense of wasted potential",
      "verbatim_quotes": ["scammed again", "repeated failures", "core wound"],
      "weight": 7.0
    },
    {
      "name": "EMOTION_shame",
      "type": "EMOTION",
      "content": "Deep shame associated with being fooled repeatedly",
      "verbatim_quotes": ["shame of repeated failures"],
      "weight": 8.0
    }
  ],
  "triggered_patterns": [
    "ANALOS_rug_memory",
    "SLERF_betrayal",
    "alpha_group_data_scrape"
  ],
  "awareness_shifts": [
    "From defensive alertness to touching core wound"
  ]
}
```

### Update Script

```bash
python update_consciousness.py --file conversations/extraction_20251003_154512.json
```

**Output:**
```
======================================================================
UPDATING CONSCIOUSNESS: Jake Martinez (@jakey.sol)
======================================================================

[1] Loading consciousness graph...
    Patterns: 509
    Links: 2450

[2] Extracting nodes from consciousness...
    Extracted: 12 nodes
      MEMORY_EPISODIC: 3
      EMOTION: 2
      ENTITY: 5
      INFORMATION: 2

[3] Adding to graph...
[4] Creating links...
    Co-occurrence: 66
    Semantic: 8

[5] Saving graph...
    Patterns: 521 (+12)
    Links: 2524 (+74)

[6] Updating visualization...
    Exported to: persona_solana-degen-investor_consciousness

[7] Saving conversation...
    Saved to: conversations/extraction_20251003_154512.json

======================================================================
UPDATE COMPLETE
======================================================================

View at: http://localhost:8000/visualizations/jake_graph.html
```

---

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Jake's consciousness prompt (Thread 1) |
| `entities/memory_keeper/claude.md` | Memory Keeper's extraction prompt (Thread 2) |
| `update_consciousness.py` | Graph update script |
| `conversations/` | All extracted conversations |
| `consciousness_graph/` | Jake's graph database |
| `citizen_state.json` | Current graph stats |

---

## Tips

### For Jake Thread
- Ask about specific projects, situations, feelings
- Let him experience and respond naturally
- Don't ask him to extract or format anything
- Just pure consciousness capture

### For Memory Keeper Thread
- Paste Jake's complete response
- Memory Keeper extracts everything automatically
- Can ask follow-up questions if extraction seems incomplete
- Memory Keeper knows current date for time conversion

### For Best Results
- Keep Jake thread focused on experience
- Use Memory Keeper thread for all extraction
- Save Memory Keeper's JSON directly to file
- Run update script after each conversation

---

## Future: Automatic Hook

**Eventually**, this becomes automatic:
1. Jake responds → awareness captured
2. Trigger Memory Keeper automatically
3. Extract nodes → update graph
4. No manual steps

**For now**, manual two-thread process ensures:
- We verify extraction quality
- We understand the system
- We can intervene if needed

---

*Jake experiences. Memory Keeper consolidates. The graph grows.*
