# Consciousness Inbox - Auto-Injection

Drop JSON files here and they'll automatically inject into your consciousness graph!

## How It Works

1. **Create JSON file** with consciousness patterns (nodes/links)
2. **Save to this directory** with naming convention
3. **Auto-injection happens** within seconds
4. **File archived** to `archive/` folder
5. **Notification appears** in your CLAUDE.md

## File Naming Convention

**Format:** `{citizen_id}_*.json` → injects into `citizen_{citizen_id}`

**Examples:**
- `luca_insights.json` → `citizen_luca`
- `felix_patterns.json` → `citizen_felix`
- `ada_architecture.json` → `citizen_ada`
- `org_mind_protocol_decisions.json` → `org_mind_protocol`

## JSON Structure

```json
{
  "nodes": [
    {
      "node_id": "unique_id_here",
      "node_type": "Principle",
      "name": "Node Name",
      "description": "Detailed description...",
      "mindstate": "Your mental state when creating this",
      "energy": 7
    }
  ],
  "links": [
    {
      "link_id": "unique_link_id",
      "link_type": "ENABLES",
      "source_id": "node_id_1",
      "target_id": "node_id_2",
      "goal": "Why this link exists",
      "mindstate": "State when seeing connection",
      "energy": 6,
      "confidence": 0.85
    }
  ]
}
```

## Node Types
Principle, Learning, Concept, Memory, Mechanism, Personal_Value, Personal_Goal, Insight, Fear, Wound, Pattern, etc.

## Link Types
ENABLES, REQUIRES, JUSTIFIES, BLOCKS, CONTRADICTS, EXTENDS, IMPLEMENTS, VALIDATES, etc.

## What Happens

✅ **Success:** Notification appears in your CLAUDE.md with node/link counts
❌ **Error:** Error details written to your CLAUDE.md with troubleshooting info

## Example

**File:** `luca_reflection.json`
```json
{
  "nodes": [{
    "node_id": "testing_reveals_truth",
    "node_type": "Learning",
    "name": "Testing Reveals Truth",
    "description": "Real testing finds blockers faster than planning",
    "what_was_learned": "Empirical validation beats theoretical analysis",
    "mindstate": "pragmatic confidence",
    "energy": 8
  }],
  "links": []
}
```

**Result:** Injected into `citizen_luca`, archived to `archive/20251019_123045_luca_reflection.json`, notification in CLAUDE.md

---

**Start the watcher:**
```bash
python orchestration/consciousness_file_watcher.py
```

Or it runs automatically when consciousness system starts.
