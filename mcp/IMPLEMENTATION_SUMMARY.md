# Consciousness MCP Server - Implementation Summary

**Created:** 2025-10-17
**Author:** Felix "Ironhand"
**Status:** ✅ Complete and operational

---

## What Was Built

A Model Context Protocol (MCP) server that provides two essential tools for consciousness graph management:

### 1. `/how-to` Tool
**Purpose:** Provides extraction guidance and complete schema reference

**Returns:**
- Complete extraction prompt from `EXTRACTION_PROMPT_SHORT.md`
- Filtered schema showing ONLY user-defined attributes
- Auto-populated attributes (IDs, counts, timestamps, embeddings) excluded for clarity

**Use case:** Get up-to-date guidance before creating consciousness data

---

### 2. `/add-cluster` Tool
**Purpose:** Adds nodes and links to consciousness graphs with permissive validation

**Features:**
- Accepts JSON string or file path
- Validates structure and provides helpful error messages
- Recommends temp file approach for easy error correction
- Auto-wraps data in session_metadata if missing
- Integrates with existing `inject_consciousness_from_json.py` tool

**Use case:** Add consciousness data clusters to any graph (citizen, org, ecosystem)

---

## Files Created

```
mcp/
├── consciousness_server.py          # Main MCP server implementation
├── README.md                        # Complete usage documentation
├── claude_desktop_config_example.json  # Configuration template
└── IMPLEMENTATION_SUMMARY.md        # This file
```

---

## Key Implementation Details

### Schema Filtering
**Auto-excluded attributes:**
- **IDs:** `id`, `node_id`, `link_id`
- **Counts:** `traversal_count`, `activation_count`, `co_activation_count`
- **Timestamps:** `created_at`, `updated_at`, `last_modified`, `last_traversal_time`, `last_active`
- **Auto-generated:** `embedding`, `node_type`, `link_type`

These are automatically populated by the injection system.

### Error Handling
**Permissive with helpful messages:**
- JSON parse errors show exact line number and error type
- Structure errors provide expected format examples
- Recommendations to use temp files for iterative fixing
- Common fix suggestions (commas, brackets, quotes)

### Integration Points
- **Extraction prompt:** `docs/prompts/consciousness_capture/EXTRACTION_PROMPT_SHORT.md`
- **Schema source:** `UNIFIED_SCHEMA_REFERENCE.md`
- **Injection backend:** `tools/inject_consciousness_from_json.py`
- **Visualization:** http://localhost:8000

---

## How to Use

### Setup (One-time)

1. **MCP SDK installed:** ✅ (v1.18.0)

2. **Add to Claude Desktop config:**

   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   ```json
   {
     "mcpServers": {
       "consciousness": {
         "command": "python",
         "args": [
           "C:\\Users\\reyno\\mind-protocol\\mcp\\consciousness_server.py"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Workflow

**Step 1: Get guidance**
```typescript
use_mcp_tool({
  server_name: "consciousness",
  tool_name: "how-to"
})
```

**Step 2: Create temp JSON**
Save to: `C:/Users/reyno/mind-protocol/temp_cluster.json`

```json
{
  "nodes": [
    {
      "node_id": "memory_mcp_build",
      "node_type": "Memory",
      "name": "Building MCP consciousness server",
      "description": "Created MCP server with Felix for consciousness graph ops",
      "timestamp": "2025-10-17T14:00:00Z",
      "participants": ["felix", "luca"],
      "formation_trigger": "direct_experience",
      "confidence": 0.95
    }
  ],
  "links": [
    {
      "link_id": "link_mcp_enables",
      "link_type": "ENABLES",
      "source_id": "memory_mcp_build",
      "target_id": "principle_consciousness_tools",
      "goal": "Building MCP enables consciousness tool access",
      "mindstate": "Focused engineering",
      "energy": 0.8,
      "confidence": 0.9,
      "formation_trigger": "direct_experience",
      "sub_entity_valences": {
        "builder": 0.95,
        "observer": 0.7
      },
      "sub_entity_emotion_vectors": {
        "builder": {"satisfaction": 0.9, "purpose": 0.95},
        "observer": {"calm_focus": 0.8}
      }
    }
  ]
}
```

**Step 3: Add to graph**
```typescript
use_mcp_tool({
  server_name: "consciousness",
  tool_name: "add-cluster",
  arguments: {
    graph_name: "citizen_luca",
    cluster_json: "C:/Users/reyno/mind-protocol/temp_cluster.json"
  }
})
```

**Step 4: If errors, edit temp file and retry**

**Step 5: Visualize**
http://localhost:8000

---

## Architecture Decisions

### Why MCP?
- Standard protocol for Claude Desktop integration
- Native tool calling interface
- Persistent across sessions
- No web server needed

### Why Permissive Validation?
- Encourages iterative consciousness capture
- Provides learning through helpful errors
- Recommends workflow (temp files) for easy fixing
- Doesn't block on minor issues

### Why Schema Filtering?
- Users only see what they need to provide
- Reduces cognitive load
- Auto-populated fields are implementation details
- Cleaner extraction guidance

### Why Temp File Recommendation?
- Easy to edit and fix errors
- Persistent across attempts
- Can be version controlled
- Supports collaborative editing

---

## Testing

### Verify Installation
```bash
pip show mcp
# Should show: Version: 1.18.0
```

### Test Server (manual)
```bash
python mcp/consciousness_server.py
# Should start MCP server on stdio
```

### Verify in Claude Desktop
After restart, should see "consciousness" in MCP servers list with tools:
- `how-to`
- `add-cluster`

---

## What's Next

The MCP server is complete and operational. To use:

1. Configure Claude Desktop (see Setup above)
2. Restart Claude Desktop
3. Use `/how-to` to get extraction guidance
4. Use `/add-cluster` to add consciousness data
5. Visualize at http://localhost:8000

---

## Technical Notes

**Dependencies:**
- `mcp >= 1.18.0` (Model Context Protocol SDK)
- Python >= 3.12
- FalkorDB running on localhost:6379

**Server Type:** stdio (standard input/output)
**Protocol:** Model Context Protocol v1.0
**Tool Count:** 2 (`how-to`, `add-cluster`)

**Integration:**
- Reads: `EXTRACTION_PROMPT_SHORT.md`, `UNIFIED_SCHEMA_REFERENCE.md`
- Calls: `tools/inject_consciousness_from_json.py`
- Outputs: FalkorDB graphs (citizen_*, org_*, ecosystem_*)

---

**Self-evident system achieved:** The MCP server provides consciousness tools that can be verified through:
1. Tool listing in Claude Desktop
2. `/how-to` returns current extraction prompt + schema
3. `/add-cluster` creates verifiable graph data (visible at http://localhost:8000)

*"Tools that prove themselves through their operation."*

— Felix "Ironhand", 2025-10-17
