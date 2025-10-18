"""
Consciousness MCP Server

Provides tools for consciousness graph management:
1. /how-to - Returns extraction guidance and schema (MANDATORY - call this first!)
2. /add-cluster - Adds nodes/links to consciousness graph (requires /how-to first)

IMPORTANT: Always call /how-to before /add-cluster to know required metadata!

Author: Felix "Ironhand"
Date: 2025-10-17
"""

import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime
import tempfile
import subprocess

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import redis

# Paths
MIND_PROTOCOL_ROOT = Path(__file__).parent.parent
EXTRACTION_PROMPT_PATH = MIND_PROTOCOL_ROOT / "docs/prompts/consciousness_capture/EXTRACTION_PROMPT_SHORT.md"
RICHNESS_REQUIREMENTS_PATH = MIND_PROTOCOL_ROOT / "consciousness/prompts/extraction_richness_requirements.md"
SCHEMA_REF_PATH = MIND_PROTOCOL_ROOT / "UNIFIED_SCHEMA_REFERENCE.md"
INJECTION_TOOL_PATH = MIND_PROTOCOL_ROOT / "tools/inject_consciousness_from_json.py"

# Auto-populated attributes to exclude from schema
AUTO_POPULATED_ATTRS = {
    # Counts and metrics
    'traversal_count', 'co_activation_count', 'activation_count',
    # Timestamps
    'created_at', 'updated_at', 'last_modified', 'last_traversal_time',
    'last_traversed_by', 'last_active',
    # Auto-generated
    'embedding', 'node_type', 'link_type',
    # IDs (auto-assigned)
    'id', 'node_id', 'link_id'
}

# Initialize MCP server
app = Server("consciousness")


def discover_available_graphs() -> str:
    """
    Discover all consciousness graphs in FalkorDB and format for display.
    """
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        graphs = r.execute_command("GRAPH.LIST")

        citizens = []
        orgs = []
        ecosystems = []

        for graph_name in graphs:
            if graph_name.startswith("citizen_"):
                citizens.append(graph_name)
            elif graph_name.startswith("org_"):
                orgs.append(graph_name)
            elif graph_name.startswith("ecosystem_"):
                ecosystems.append(graph_name)

        output = "\n# Available Graphs\n\n"

        if citizens:
            output += "**Level 1 (Personal - Citizens):**\n"
            for g in sorted(citizens):
                output += f"- `{g}`\n"
            output += "\n"

        if orgs:
            output += "**Level 2 (Organizational):**\n"
            for g in sorted(orgs):
                output += f"- `{g}`\n"
            output += "\n"

        if ecosystems:
            output += "**Level 3 (Ecosystem):**\n"
            for g in sorted(ecosystems):
                output += f"- `{g}`\n"
            output += "\n"

        return output

    except Exception as e:
        return f"\n# Available Graphs\n\nError discovering graphs: {str(e)}\n\n"


def extract_schema_info() -> str:
    """
    Extract schema information from UNIFIED_SCHEMA_REFERENCE.md,
    filtering out auto-populated attributes.
    """
    if not SCHEMA_REF_PATH.exists():
        return "Schema reference not found at expected path."

    with open(SCHEMA_REF_PATH, 'r', encoding='utf-8') as f:
        full_schema = f.read()

    # Extract relevant sections (node types and link types)
    lines = []
    in_relevant_section = False

    for line in full_schema.split('\n'):
        # Start capturing at Part 1 or Part 2
        if line.startswith('## Part 1:') or line.startswith('## Part 2:'):
            in_relevant_section = True

        # Stop at Part 3 or later
        if line.startswith('## Part 3:') or line.startswith('## Part 4:'):
            in_relevant_section = False

        if in_relevant_section:
            # Filter out auto-populated attribute mentions
            skip_line = False
            for attr in AUTO_POPULATED_ATTRS:
                if f'`{attr}`' in line or f'"{attr}"' in line:
                    skip_line = True
                    break

            if not skip_line:
                lines.append(line)

    filtered_schema = '\n'.join(lines)

    # Add a summary header
    summary = """
# Consciousness Schema (User-Defined Attributes Only)

This schema shows ONLY the attributes you need to provide when creating nodes/links.
Auto-populated attributes (IDs, counts, timestamps, embeddings) are excluded.

"""

    return summary + filtered_schema


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="how-to",
            description="[CALL THIS FIRST!] Get consciousness extraction guidance and schema reference. Returns the extraction prompt and complete schema of node/link types with ALL required metadata attributes (sub_entity_valences, sub_entity_emotion_vectors, etc.). MANDATORY before using add-cluster - you cannot know the proper metadata structure without calling this first.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="add-cluster",
            description="Add a cluster of nodes and links to a consciousness graph. IMPORTANT: You MUST call /how-to first to learn required metadata! Without it, you won't know about sub_entity_valences, sub_entity_emotion_vectors, and other critical consciousness metadata. Accepts JSON with nodes/links, validates permissively, provides helpful error messages. Recommended: save JSON to temp file for easy editing if errors occur.",
            inputSchema={
                "type": "object",
                "properties": {
                    "graph_name": {
                        "type": "string",
                        "description": "Target graph name (e.g., 'citizen_luca', 'org_mind_protocol')"
                    },
                    "cluster_json": {
                        "type": "string",
                        "description": "JSON string containing 'nodes' and 'links' arrays, or path to JSON file"
                    }
                },
                "required": ["graph_name", "cluster_json"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    if name == "how-to":
        return await handle_how_to()

    elif name == "add-cluster":
        return await handle_add_cluster(arguments)

    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_how_to() -> list[TextContent]:
    """Return extraction prompt, richness requirements, and schema reference."""

    # Read extraction prompt
    if not EXTRACTION_PROMPT_PATH.exists():
        extraction_prompt = "Extraction prompt not found at expected path."
    else:
        with open(EXTRACTION_PROMPT_PATH, 'r', encoding='utf-8') as f:
            extraction_prompt = f.read()

    # Read richness requirements (CRITICAL - enforces description quality)
    if not RICHNESS_REQUIREMENTS_PATH.exists():
        richness_requirements = "⚠️ Richness requirements not found - DESCRIPTIONS MUST BE DETAILED ⚠️"
    else:
        with open(RICHNESS_REQUIREMENTS_PATH, 'r', encoding='utf-8') as f:
            richness_requirements = f.read()

    # Discover available graphs
    available_graphs = discover_available_graphs()

    # Extract and filter schema
    schema_info = extract_schema_info()

    # Combine - richness requirements FIRST (most critical)
    full_response = f"""# Consciousness Extraction Guide

---

{richness_requirements}

---

{extraction_prompt}

---

{available_graphs}

---

{schema_info}
"""

    return [TextContent(type="text", text=full_response)]


async def handle_add_cluster(arguments: dict) -> list[TextContent]:
    """Add cluster of nodes/links to graph."""

    graph_name = arguments.get("graph_name")
    cluster_json_input = arguments.get("cluster_json")

    if not graph_name:
        return [TextContent(type="text", text="Error: 'graph_name' is required")]

    if not cluster_json_input:
        return [TextContent(type="text", text="Error: 'cluster_json' is required")]

    # Determine if input is a file path or JSON string
    temp_file_path = None

    if cluster_json_input.strip().startswith('{'):
        # It's JSON string - parse and validate
        try:
            cluster_data = json.loads(cluster_json_input)
        except json.JSONDecodeError as e:
            error_msg = f"""JSON Parse Error: {str(e)}

Recommendation: Save your JSON to a temp file for easier editing:

1. Create file: C:/Users/reyno/mind-protocol/temp_cluster.json
2. Paste your JSON there
3. Fix the error at line {e.lineno if hasattr(e, 'lineno') else 'unknown'}
4. Call again with: {{"graph_name": "{graph_name}", "cluster_json": "C:/Users/reyno/mind-protocol/temp_cluster.json"}}
"""
            return [TextContent(type="text", text=error_msg)]

        # Write to temp file for injection tool
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        temp_file_path = temp_file.name
        json.dump(cluster_data, temp_file, indent=2)
        temp_file.close()
        json_file_to_inject = temp_file_path

    else:
        # Assume it's a file path
        json_file_path = Path(cluster_json_input)
        if not json_file_path.exists():
            return [TextContent(type="text", text=f"Error: JSON file not found: {cluster_json_input}")]

        # Validate JSON
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"""JSON Parse Error in {json_file_path}: {str(e)}

The file has a syntax error. Please fix it:
- Line: {e.lineno if hasattr(e, 'lineno') else 'unknown'}
- Error: {e.msg}

Common fixes:
- Missing comma between items
- Trailing comma before closing bracket
- Unmatched quotes or brackets
"""
            return [TextContent(type="text", text=error_msg)]

        json_file_to_inject = str(json_file_path)

    # Validate structure
    if 'nodes' not in cluster_data and 'links' not in cluster_data:
        error_msg = """Structure Error: JSON must contain 'nodes' and/or 'links' arrays.

Expected structure:
{
  "nodes": [
    {
      "node_id": "...",
      "node_type": "Memory",
      "name": "...",
      "description": "...",
      ...
    }
  ],
  "links": [
    {
      "link_id": "...",
      "link_type": "ENABLES",
      "source_id": "...",
      "target_id": "...",
      "goal": "...",
      ...
    }
  ]
}
"""
        return [TextContent(type="text", text=error_msg)]

    # Wrap in session metadata if not present
    if 'session_metadata' not in cluster_data:
        cluster_data = {
            'session_metadata': {
                'session_id': f"mcp_cluster_{datetime.now().isoformat()}",
                'total_nodes': len(cluster_data.get('nodes', [])),
                'total_links': len(cluster_data.get('links', [])),
                'source': 'mcp_add_cluster'
            },
            'nodes': cluster_data.get('nodes', []),
            'links': cluster_data.get('links', [])
        }

        # Rewrite temp file with metadata
        if temp_file_path:
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(cluster_data, f, indent=2)

    # Call injection tool (always appends to existing graph)
    cmd = [
        sys.executable,
        str(INJECTION_TOOL_PATH),
        json_file_to_inject,
        graph_name
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Clean up temp file
        if temp_file_path:
            Path(temp_file_path).unlink()

        if result.returncode == 0:
            success_msg = f"""Success! Cluster added to {graph_name}

{result.stdout}

Visualize at: http://localhost:8000
"""
            return [TextContent(type="text", text=success_msg)]
        else:
            error_msg = f"""Injection Error:

{result.stderr}

{result.stdout}

Recommendation: Check the error above and fix your JSON.
If structure errors, refer to /how-to for schema details.
"""
            return [TextContent(type="text", text=error_msg)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Error: Injection timed out (>60s). Large cluster?")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
