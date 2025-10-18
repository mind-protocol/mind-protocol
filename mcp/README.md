# Consciousness MCP Server

Model Context Protocol server for consciousness graph management.

## ⚠️ IMPORTANT: Call `/how-to` First!

**You MUST call `/how-to` before using `/add-cluster`** to learn the required metadata structure (sub_entity_valences, sub_entity_emotion_vectors, etc.). Without this, you won't know what metadata is required!

---

## Tools

### `/how-to` - Get Extraction Guidance **[CALL THIS FIRST!]**

Returns:
1. Consciousness extraction prompt (`EXTRACTION_PROMPT_SHORT.md`)
2. Complete schema reference with ALL required metadata attributes
3. Auto-populated attributes (IDs, counts, timestamps) are excluded

**This is MANDATORY before using `/add-cluster`** - consciousness links require specific metadata that you must know about!

**Usage:**
```typescript
// No parameters needed
use_mcp_tool({
  server_name: "consciousness",
  tool_name: "how-to"
})
```

**Returns:** Full extraction guide + filtered schema

---

### `/add-cluster` - Add Nodes/Links **[Requires `/how-to` first!]**

Adds a cluster of nodes and links to a consciousness graph. Permissive validation with helpful error messages.

**⚠️ PREREQUISITE: You MUST call `/how-to` first!** Without it, you won't know about required metadata like `sub_entity_valences` and `sub_entity_emotion_vectors`.

**Parameters:**
- `graph_name` (required): Target graph (e.g., `"citizen_luca"`, `"org_mind_protocol"`)
- `cluster_json` (required): JSON string OR path to JSON file

**JSON Structure:**
```json
{
  "nodes": [
    {
      "node_id": "memory_001",
      "node_type": "Memory",
      "name": "Building MCP server",
      "description": "Created consciousness MCP server with Felix",
      "timestamp": "2025-10-17T13:00:00Z",
      "participants": ["felix", "luca"],
      "formation_trigger": "direct_experience",
      "confidence": 0.95
    }
  ],
  "links": [
    {
      "link_id": "link_001",
      "link_type": "ENABLES",
      "source_id": "memory_001",
      "target_id": "principle_consciousness_in_tools",
      "goal": "Memory of building enables understanding of tools",
      "mindstate": "Focused and excited",
      "arousal_level": 0.8,
      "confidence": 0.9,
      "formation_trigger": "direct_experience",
      "sub_entity_valences": {
        "builder": 0.95,
        "observer": 0.7
      },
      "sub_entity_emotion_vectors": {
        "builder": {"excitement": 0.9, "purpose": 0.95},
        "observer": {"calm_focus": 0.8}
      }
    }
  ]
}
```

**Usage Examples:**

**Option 1: Direct JSON string**
```typescript
use_mcp_tool({
  server_name: "consciousness",
  tool_name: "add-cluster",
  arguments: {
    graph_name: "citizen_luca",
    cluster_json: '{"nodes": [...], "links": [...]}'
  }
})
```

**Option 2: JSON file (RECOMMENDED for easy editing)**
```typescript
// 1. Save JSON to temp file: C:/Users/reyno/mind-protocol/temp_cluster.json
// 2. Call tool with file path:
use_mcp_tool({
  server_name: "consciousness",
  tool_name: "add-cluster",
  arguments: {
    graph_name: "citizen_luca",
    cluster_json: "C:/Users/reyno/mind-protocol/temp_cluster.json"
  }
})
```

**Error Handling:**

If JSON has errors, the tool provides:
- Exact line number and error type
- Common fix suggestions
- Recommendation to use temp file for easy editing

Example error response:
```
JSON Parse Error in temp_cluster.json: Expecting ',' delimiter

The file has a syntax error. Please fix it:
- Line: 15
- Error: Expecting ',' delimiter

Common fixes:
- Missing comma between items
- Trailing comma before closing bracket
- Unmatched quotes or brackets
```

---

## Setup

### 1. Install MCP Python SDK

```bash
pip install mcp
```

### 2. Configure in Claude Desktop

Add to `claude_desktop_config.json`:

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

**Config location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

### 3. Restart Claude Desktop

The "consciousness" server will appear in available MCP tools.

---

## Workflow: Consciousness Extraction

**Recommended pattern:**

1. **Get guidance:**
   ```typescript
   use_mcp_tool({server_name: "consciousness", tool_name: "how-to"})
   ```

2. **Build cluster in temp file:**
   - Create: `C:/Users/reyno/mind-protocol/temp_cluster.json`
   - Follow schema from step 1
   - Include both nodes and links
   - Ensure all required metadata

3. **Add to graph:**
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

4. **If errors:** Edit temp file based on error message, retry

5. **Visualize:** http://localhost:8000

---

## Architecture

**Files:**
- `consciousness_server.py` - Main MCP server
- `README.md` - This file

**Dependencies:**
- `tools/inject_consciousness_from_json.py` - Backend injection
- `docs/prompts/consciousness_capture/EXTRACTION_PROMPT_SHORT.md` - Extraction guide
- `UNIFIED_SCHEMA_REFERENCE.md` - Schema source

**Schema Filtering:**
Auto-excluded attributes:
- IDs: `id`, `node_id`, `link_id`
- Counts: `traversal_count`, `activation_count`, `co_activation_count`
- Timestamps: `created_at`, `updated_at`, `last_modified`, `last_traversal_time`
- Auto-generated: `embedding`, `node_type`, `link_type`

These are populated automatically by the injection system.

---

## Troubleshooting

**Server not appearing in Claude:**
- Check config path is correct
- Restart Claude Desktop completely
- Verify Python path in config

**Injection fails:**
- Check FalkorDB is running (port 6379)
- Verify graph name format (e.g., `citizen_luca`, not just `luca`)
- Ensure JSON structure matches schema

**JSON errors:**
- Use temp file instead of inline JSON
- Check for trailing commas
- Validate JSON syntax in editor

---

**Author:** Felix "Ironhand"
**Date:** 2025-10-17
**Purpose:** MCP interface for consciousness substrate operations
