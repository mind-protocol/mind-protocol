"""
Generate comprehensive type reference from schema_registry and actual usage.

Follows universe-engine/mcp-servers pattern:
1. Queries schema_registry (FalkorDB) for link type schemas (source of truth)
2. Scans all citizen graphs for node types actually in use
3. Returns JSON with success/guide_text (same format as get_schema_guide)
4. Can be called directly or wrapped in MCP tool

Author: Felix "Ironhand"
Created: 2025-01-19
Pattern inspired by: Marco "Salthand" - generate_schema_guide.py
"""

import sys
import json
import redis
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

MIND_PROTOCOL_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = MIND_PROTOCOL_ROOT / "docs" / "TYPE_REFERENCE.md"


def connect_to_falkordb():
    """Connect to FalkorDB (Redis)."""
    return redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_link_type_schemas(r):
    """
    Query schema_registry for all link type schemas WITH full field metadata.
    Returns dict: {type_name: schema_data_with_fields}
    """
    # Get basic link type info
    result = r.execute_command('GRAPH.QUERY', 'schema_registry',
        '''MATCH (l:LinkTypeSchema)
           RETURN l.type_name, l.level, l.category, l.description,
                  l.detection_pattern, l.mechanisms
           ORDER BY l.type_name'''
    )

    schemas = {}
    for row in result[1]:
        type_name = row[0]

        # Parse mechanisms array
        def parse_array(val):
            if not val or val == '[]':
                return []
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except:
                    val = val.strip()
                    if val.startswith('[') and val.endswith(']'):
                        content = val[1:-1].strip()
                        if not content:
                            return []
                        return [item.strip() for item in content.split(',')]
            return []

        schemas[type_name] = {
            'type_name': type_name,
            'level': row[1] if len(row) > 1 else 'unknown',
            'category': row[2] if len(row) > 2 else 'N/A',
            'description': row[3] if len(row) > 3 else 'No description',
            'detection_pattern': row[4] if len(row) > 4 else 'N/A',
            'mechanisms': parse_array(row[5]) if len(row) > 5 else [],
            'required_fields': [],
            'optional_fields': []
        }

    # Get required field specifications for each link type
    for type_name in schemas.keys():
        # Query required fields
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:LinkTypeSchema {{type_name: '{type_name}'}})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.range_min, f.range_max, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field_spec = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'range_min': row[3] if len(row) > 3 else None,
                'range_max': row[4] if len(row) > 4 else None,
                'description': row[5] if len(row) > 5 else ''
            }
            schemas[type_name]['required_fields'].append(field_spec)

        # Query optional fields
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:LinkTypeSchema {{type_name: '{type_name}'}})-[:HAS_OPTIONAL_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field_spec = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'description': row[3] if len(row) > 3 else ''
            }
            schemas[type_name]['optional_fields'].append(field_spec)

    return schemas


def get_node_types_from_usage(r):
    """
    Scan all citizen graphs to find node types actually in use.
    Returns dict: {node_type: usage_stats}

    NOTE: This is temporary until NodeTypeSchema is implemented.
    """
    # Get all citizen graphs
    graphs = r.execute_command('GRAPH.LIST')
    citizen_graphs = [g for g in graphs if g.startswith('citizen_')]

    node_type_stats = defaultdict(lambda: {'count': 0, 'graphs': []})

    for graph in citizen_graphs:
        result = r.execute_command('GRAPH.QUERY', graph,
            'MATCH (n) RETURN n.node_type, count(n)'
        )

        for row in result[1]:
            if row and row[0]:
                node_type = row[0]
                count = row[1] if len(row) > 1 else 0
                node_type_stats[node_type]['count'] += count
                node_type_stats[node_type]['graphs'].append(graph)

    return dict(node_type_stats)


def get_link_types_from_usage(r):
    """
    Scan all citizen graphs to find link types actually in use.
    Returns dict: {link_type: usage_stats}
    """
    graphs = r.execute_command('GRAPH.LIST')
    citizen_graphs = [g for g in graphs if g.startswith('citizen_')]

    link_type_stats = defaultdict(lambda: {'count': 0, 'graphs': []})

    for graph in citizen_graphs:
        result = r.execute_command('GRAPH.QUERY', graph,
            'MATCH ()-[r]-() RETURN type(r), count(r)'
        )

        for row in result[1]:
            if row and row[0]:
                link_type = row[0]
                count = row[1] if len(row) > 1 else 0
                link_type_stats[link_type]['count'] += count
                link_type_stats[link_type]['graphs'].append(graph)

    return dict(link_type_stats)


def render_markdown_reference(link_schemas, node_stats, link_stats):
    """
    Generate complete markdown reference document.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# Mind Protocol Type Reference

**Auto-generated from schema_registry and actual usage**
**Last updated:** {timestamp}

This document is the single source of truth for all node and link types in the Mind Protocol consciousness infrastructure.

---

## Link Type Inventory

**Total:** {len(link_schemas)} link type schemas defined

### Schema Definitions

"""

    # Group by level
    shared_links = {k: v for k, v in link_schemas.items() if v['level'] == 'shared'}
    n1_links = {k: v for k, v in link_schemas.items() if v['level'] == 'n1'}
    n2_links = {k: v for k, v in link_schemas.items() if v['level'] == 'n2'}

    if shared_links:
        md += f"#### Shared Link Types ({len(shared_links)})\n\n"
        for type_name, schema in sorted(shared_links.items()):
            usage = link_stats.get(type_name, {'count': 0, 'graphs': []})
            md += f"**{type_name}**\n\n"
            md += f"- **Category:** {schema['category']}\n"
            md += f"- **Description:** {schema['description']}\n"
            md += f"- **Usage:** {usage['count']} instances across {len(set(usage['graphs']))} graphs\n"

            # Display full field specifications
            req_fields = schema.get('required_fields', [])
            opt_fields = schema.get('optional_fields', [])

            if req_fields and len(req_fields) > 0:
                md += "\n**Required Fields:**\n"
                for field in req_fields:
                    field_name = field['name']
                    field_type = field['type']
                    field_desc = field.get('description', '')
                    enum_vals = field.get('enum_values', [])
                    range_min = field.get('range_min')
                    range_max = field.get('range_max')

                    # Format field line
                    md += f"- `{field_name}` ({field_type})"

                    if enum_vals:
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in enum_vals)}"
                    elif range_min is not None and range_max is not None:
                        md += f" - Range: [{range_min}, {range_max}]"

                    if field_desc:
                        md += f"\n  - {field_desc}"

                    md += "\n"

            if opt_fields and len(opt_fields) > 0:
                md += "\n**Optional Fields:**\n"
                for field in opt_fields:
                    field_name = field['name']
                    field_type = field['type']
                    field_desc = field.get('description', '')
                    enum_vals = field.get('enum_values', [])

                    md += f"- `{field_name}` ({field_type})"

                    if enum_vals:
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in enum_vals)}"

                    if field_desc:
                        md += f"\n  - {field_desc}"

                    md += "\n"

            md += "\n"

    if n1_links:
        md += f"#### Level 1 (Personal) Link Types ({len(n1_links)})\n\n"
        for type_name, schema in sorted(n1_links.items()):
            usage = link_stats.get(type_name, {'count': 0, 'graphs': []})
            md += f"**{type_name}**\n\n"
            md += f"- **Category:** {schema['category']}\n"
            md += f"- **Description:** {schema['description']}\n"
            md += f"- **Usage:** {usage['count']} instances across {len(set(usage['graphs']))} graphs\n"

            # Display full field specifications
            req_fields = schema.get('required_fields', [])
            opt_fields = schema.get('optional_fields', [])

            if req_fields and len(req_fields) > 0:
                md += "\n**Required Fields:**\n"
                for field in req_fields:
                    md += f"- `{field['name']}` ({field['type']})"
                    if field.get('enum_values'):
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in field['enum_values'])}"
                    if field.get('description'):
                        md += f"\n  - {field['description']}"
                    md += "\n"

            if opt_fields and len(opt_fields) > 0:
                md += "\n**Optional Fields:**\n"
                for field in opt_fields:
                    md += f"- `{field['name']}` ({field['type']})"
                    if field.get('enum_values'):
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in field['enum_values'])}"
                    if field.get('description'):
                        md += f"\n  - {field['description']}"
                    md += "\n"

            md += "\n"

    if n2_links:
        md += f"#### Level 2 (Organizational) Link Types ({len(n2_links)})\n\n"
        for type_name, schema in sorted(n2_links.items()):
            usage = link_stats.get(type_name, {'count': 0, 'graphs': []})
            md += f"**{type_name}**\n\n"
            md += f"- **Category:** {schema['category']}\n"
            md += f"- **Description:** {schema['description']}\n"
            md += f"- **Usage:** {usage['count']} instances across {len(set(usage['graphs']))} graphs\n"

            # Display full field specifications
            req_fields = schema.get('required_fields', [])
            opt_fields = schema.get('optional_fields', [])

            if req_fields and len(req_fields) > 0:
                md += "\n**Required Fields:**\n"
                for field in req_fields:
                    md += f"- `{field['name']}` ({field['type']})"
                    if field.get('enum_values'):
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in field['enum_values'])}"
                    if field.get('description'):
                        md += f"\n  - {field['description']}"
                    md += "\n"

            if opt_fields and len(opt_fields) > 0:
                md += "\n**Optional Fields:**\n"
                for field in opt_fields:
                    md += f"- `{field['name']}` ({field['type']})"
                    if field.get('enum_values'):
                        md += f" - Allowed values: {', '.join(f'`{v}`' for v in field['enum_values'])}"
                    if field.get('description'):
                        md += f"\n  - {field['description']}"
                    md += "\n"

            md += "\n"

    # Warn about link types in use but not in schema
    undefined_links = set(link_stats.keys()) - set(link_schemas.keys())
    if undefined_links:
        md += f"### ⚠️ Warning: Link Types in Use Without Schema ({len(undefined_links)})\n\n"
        for link_type in sorted(undefined_links):
            usage = link_stats[link_type]
            md += f"- **{link_type}**: {usage['count']} instances across {len(set(usage['graphs']))} graphs\n"
        md += "\n"

    # Node types section
    md += f"""---

## Node Type Inventory

**Total:** {len(node_stats)} node types in use

**Note:** NodeTypeSchema not yet implemented in schema_registry. This inventory is based on actual usage across all citizen graphs.

"""

    for node_type, stats in sorted(node_stats.items()):
        md += f"**{node_type}**\n"
        md += f"- **Usage:** {stats['count']} instances across {len(set(stats['graphs']))} graphs\n"
        md += f"- **Graphs:** {', '.join(sorted(set(stats['graphs'])))}\n"
        md += "\n"

    md += """---

## How to Update

**Link Type Schemas:**
1. Update schema_registry graph in FalkorDB
2. Run `python tools/generate_type_reference.py`
3. This file will auto-regenerate from schema_registry

**Node Type Schemas:**
Currently tracked by usage only. When NodeTypeSchema is implemented:
1. Add schemas to schema_registry
2. Update this script to query NodeTypeSchema nodes
3. Run generator

**Automation:**
This script can be run:
- On-demand: `python tools/generate_type_reference.py`
- In CI/CD: Add to deployment pipeline
- Scheduled: Add to observability cron jobs
"""

    return md


def main():
    """
    Generate type reference from schema_registry and usage.

    Returns JSON with success/guide_text (universe-engine pattern).
    Can optionally write to file if --write-file argument passed.
    """
    write_file = '--write-file' in sys.argv

    try:
        r = connect_to_falkordb()

        # Query schema_registry for link type schemas
        link_schemas = get_link_type_schemas(r)

        # Scan graphs for actual usage
        node_stats = get_node_types_from_usage(r)
        link_stats = get_link_types_from_usage(r)

        # Generate markdown guide
        guide_text = render_markdown_reference(link_schemas, node_stats, link_stats)

        # Optionally write to file
        if write_file:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                f.write(guide_text)

        # Return JSON (universe-engine pattern)
        result = {
            "success": True,
            "guide_text": guide_text,
            "schema_analysis": {
                "link_schemas": link_schemas,
                "node_stats": node_stats,
                "link_stats": link_stats,
                "stats": {
                    "link_types_defined": len(link_schemas),
                    "link_types_in_use": len(link_stats),
                    "node_types_in_use": len(node_stats)
                }
            }
        }

        print(json.dumps(result))

    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
