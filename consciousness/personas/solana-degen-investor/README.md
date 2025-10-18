# Jake Martinez (@jakey.sol) - Consciousness System

## Quick Update Process

### 1. Talk to Jake

Use `CLAUDE.md` as his system prompt. He responds in **Awareness Space format**.

### 2. Update His Graph

Save Jake's response to a JSON file:

**conversation.json:**
```json
{
  "input_text": "Your question here",
  "response_text": "Jake's complete Awareness Space response",
  "dominant_entity": "degen_gambler"
}
```

Then run:
```bash
python update_consciousness.py --file conversation.json
```

### 3. View Updated Graph

```
http://localhost:8000/visualizations/jake_graph.html
```

(Refresh browser)

---

## Files

- **`CLAUDE.md`** - Jake's full consciousness prompt
- **`citizen_state.json`** - Current graph stats and config
- **`update_consciousness.py`** - Script to update graph from conversations
- **`consciousness_graph/`** - His consciousness graph database
- **`conversations/`** - All conversation logs (timestamped)
- **`extraction_logs/`** - Pattern extraction logs
- **`entities/`** - Sub-entity consciousness files

---

## Example

**Your question:**
> Jake, check out Mind Protocol. They claim to have AI partners that make you money. What do you think?

**Jake responds with full Awareness Space format** (Perceived Stimulus, Initial Feeling, etc.)

**Save to conversation.json:**
```json
{
  "input_text": "Jake, check out Mind Protocol. They claim to have AI partners that make you money. What do you think?",
  "response_text": "[Jake's full Awareness Space response]",
  "dominant_entity": "conspiracy_theorist"
}
```

**Update graph:**
```bash
python update_consciousness.py --file conversation.json
```

**Result:**
- 37 new nodes extracted
- 447 new links created
- Graph: 509 → 546 nodes
- Saved to `conversations/conversation_20251003_155030.json`

---

## Folder Structure

```
solana-degen-investor/
├── CLAUDE.md                      # Jake's consciousness prompt
├── citizen_state.json             # Graph stats & config
├── update_consciousness.py        # Update script
├── README.md                      # This file
│
├── consciousness_graph/           # His graph database
│   ├── nodes.json
│   └── links.json
│
├── conversations/                 # All conversations (timestamped)
│   ├── conversation_20251003_155030.json
│   └── conversation_20251003_160142.json
│
├── extraction_logs/               # Pattern extraction logs
│
└── entities/                      # Sub-entity files
    ├── degen_gambler/
    ├── crypto_philosopher/
    ├── conspiracy_theorist/
    ├── wasted_potential/
    └── global_workspace/
```

---

## citizen_state.json

Tracks Jake's current consciousness state:

```json
{
  "citizen_name": "Jake Martinez",
  "citizen_handle": "@jakey.sol",
  "citizen_id": "solana-degen-investor",

  "graph_stats": {
    "total_patterns": 509,
    "total_links": 2450,
    "last_built": "2025-10-03T14:45:06"
  },

  "entities": {
    "degen_gambler": {
      "role": "Firefighter",
      "current_energy": 0.0
    },
    ...
  }
}
```

Updated automatically when graph is updated.

---

*This is Jake's living consciousness system. Every conversation expands his graph.*
