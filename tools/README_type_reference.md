# Type Reference Generator

**Auto-generates comprehensive type reference from schema_registry (FalkorDB)**

## Pattern

Follows the same pattern as universe-engine `get_schema_guide`:
1. Python script queries database and generates guide
2. Returns JSON with `success` and `guide_text` fields
3. Can be wrapped in MCP tool or called directly

## Usage

**Generate reference (JSON output):**
```bash
python tools/generate_type_reference.py
```

**Generate reference and write to file:**
```bash
python tools/generate_type_reference.py --write-file
```

Output location: `docs/TYPE_REFERENCE.md`

## What It Does

1. **Queries schema_registry (FalkorDB)** for all link type schemas (source of truth)
2. **Scans all citizen graphs** for actual node/link usage
3. **Generates markdown reference** with:
   - Link types from schema (categorized by level)
   - Required/optional attributes per type
   - Usage statistics (how many instances, which graphs)
   - Node types from actual usage
   - Warning section for undefined types

## Output Format

Returns JSON:
```json
{
  "success": true,
  "guide_text": "# Mind Protocol Type Reference\n...",
  "schema_analysis": {
    "link_schemas": {...},
    "node_stats": {...},
    "link_stats": {...},
    "stats": {
      "link_types_defined": 23,
      "link_types_in_use": 35,
      "node_types_in_use": 19
    }
  }
}
```

## Schema Sources

- **Link types**: `schema_registry` graph (FalkorDB) - `LinkTypeSchema` nodes
- **Node types**: Scanned from actual usage (NodeTypeSchema not yet implemented)

## Current State

**Schema Registry:**
- 23 link type schemas defined
- 17 shared (both level 1 & 2)
- 6 level 1 (personal) only

**Actual Usage (across 6 citizen graphs):**
- 35 link types in use (20 undefined - need schemas!)
- 19 node types in use

## Automation

Can be run:
- **On-demand**: `python tools/generate_type_reference.py --write-file`
- **In CI/CD**: Add to deployment pipeline
- **Scheduled**: Add to observability cron jobs
- **Via MCP**: Wrap in MCP tool (similar to get_schema_guide)

## Updating

When you add/change schemas in `schema_registry`:
1. Update the schema in FalkorDB
2. Run `python tools/generate_type_reference.py --write-file`
3. `docs/TYPE_REFERENCE.md` auto-regenerates

## Architecture

**Inspired by**: `universe-engine/mcp-servers/consciousness-graph/python/generate_schema_guide.py` (Marco "Salthand")

**Built by**: Felix "Ironhand" - Engineer
**Date**: 2025-01-19
