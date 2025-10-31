"""
Generate COMPLETE type reference from schema_registry.

Queries the complete schema_registry for:
- Universal node attributes (inherited by ALL node types)
- Universal link attributes (inherited by ALL link types)
- All 44 node type schemas with fields
- All 23 link type schemas with fields
- Usage statistics from actual graphs

This is the definitive, auto-generated type reference.

Author: Felix "Ironhand"
Created: 2025-01-19
"""

import sys
import json
import redis
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

MIND_PROTOCOL_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = MIND_PROTOCOL_ROOT / "docs" / "COMPLETE_TYPE_REFERENCE.md"
CITIZENS_CLAUDE_PATH = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / "CLAUDE.md"
COLLECTIVE_CLAUDE_PATH = MIND_PROTOCOL_ROOT / "consciousness" / "organization" / "CLAUDE.md"


def connect_to_falkordb():
    """Connect to FalkorDB (Redis)."""
    return redis.Redis(host='localhost', port=6379, decode_responses=True)


def parse_array(val):
    """Parse FalkorDB array format."""
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


def get_universal_node_attributes(r):
    """Query universal node attributes (inherited by ALL node types)."""
    result = r.execute_command('GRAPH.QUERY', 'schema_registry',
        '''MATCH (c:UniversalNodeCategory)-[:HAS_UNIVERSAL_FIELD]->(f:UniversalNodeField)
           RETURN c.category_name, f.name, f.type, f.required, f.enum_values,
                  f.range_min, f.range_max, f.description
           ORDER BY c.category_name, f.name'''
    )

    categories = defaultdict(list)
    for row in result[1]:
        category = row[0]
        field = {
            'name': row[1],
            'type': row[2],
            'required': row[3],
            'enum_values': parse_array(row[4]) if len(row) > 4 else [],
            'range_min': row[5] if len(row) > 5 else None,
            'range_max': row[6] if len(row) > 6 else None,
            'description': row[7] if len(row) > 7 else ''
        }
        categories[category].append(field)

    return dict(categories)


def get_universal_link_attributes(r):
    """Query universal link attributes (inherited by ALL link types)."""
    result = r.execute_command('GRAPH.QUERY', 'schema_registry',
        '''MATCH (c:UniversalLinkCategory)-[:HAS_UNIVERSAL_FIELD]->(f:UniversalLinkField)
           RETURN c.category_name, f.name, f.type, f.required, f.enum_values,
                  f.range_min, f.range_max, f.description
           ORDER BY c.category_name, f.name'''
    )

    categories = defaultdict(list)
    for row in result[1]:
        category = row[0]
        field = {
            'name': row[1],
            'type': row[2],
            'required': row[3],
            'enum_values': parse_array(row[4]) if len(row) > 4 else [],
            'range_min': row[5] if len(row) > 5 else None,
            'range_max': row[6] if len(row) > 6 else None,
            'description': row[7] if len(row) > 7 else ''
        }
        categories[category].append(field)

    return dict(categories)


def get_node_type_schemas(r):
    """Query all node type schemas from schema_registry."""
    result = r.execute_command('GRAPH.QUERY', 'schema_registry',
        '''MATCH (nt:NodeTypeSchema)
           RETURN nt.type_name, nt.universality, nt.description
           ORDER BY nt.type_name'''
    )

    schemas = {}
    for row in result[1]:
        type_name = row[0]
        schemas[type_name] = {
            'type_name': type_name,
            'universality': row[1] if len(row) > 1 else 'unknown',
            'description': row[2] if len(row) > 2 else 'No description',
            'required_fields': [],
            'optional_fields': []
        }

    # Get required fields for each node type
    for type_name in schemas.keys():
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:NodeTypeSchema {{type_name: '{type_name}'}})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.range_min, f.range_max, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'range_min': row[3] if len(row) > 3 else None,
                'range_max': row[4] if len(row) > 4 else None,
                'description': row[5] if len(row) > 5 else ''
            }
            schemas[type_name]['required_fields'].append(field)

        # Get optional fields
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:NodeTypeSchema {{type_name: '{type_name}'}})-[:HAS_OPTIONAL_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'description': row[3] if len(row) > 3 else ''
            }
            schemas[type_name]['optional_fields'].append(field)

    return schemas


def get_link_type_schemas(r):
    """Query all link type schemas from schema_registry."""
    result = r.execute_command('GRAPH.QUERY', 'schema_registry',
        '''MATCH (lt:LinkTypeSchema)
           RETURN lt.type_name, lt.universality, lt.description
           ORDER BY lt.type_name'''
    )

    schemas = {}
    for row in result[1]:
        type_name = row[0]
        schemas[type_name] = {
            'type_name': type_name,
            'universality': row[1] if len(row) > 1 else 'unknown',
            'description': row[2] if len(row) > 2 else 'No description',
            'required_fields': [],
            'optional_fields': []
        }

    # Get required fields for each link type
    for type_name in schemas.keys():
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:LinkTypeSchema {{type_name: '{type_name}'}})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.range_min, f.range_max, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'range_min': row[3] if len(row) > 3 else None,
                'range_max': row[4] if len(row) > 4 else None,
                'description': row[5] if len(row) > 5 else ''
            }
            schemas[type_name]['required_fields'].append(field)

        # Get optional fields
        result = r.execute_command('GRAPH.QUERY', 'schema_registry',
            f'''MATCH (:LinkTypeSchema {{type_name: '{type_name}'}})-[:HAS_OPTIONAL_FIELD]->(f:FieldSchema)
                RETURN f.name, f.type, f.enum_values, f.description
                ORDER BY f.name'''
        )

        for row in result[1]:
            field = {
                'name': row[0],
                'type': row[1] if len(row) > 1 else 'string',
                'enum_values': parse_array(row[2]) if len(row) > 2 else [],
                'description': row[3] if len(row) > 3 else ''
            }
            schemas[type_name]['optional_fields'].append(field)

    return schemas


def get_usage_stats(r):
    """Get usage statistics from actual graphs."""
    graphs = r.execute_command('GRAPH.LIST')
    citizen_graphs = [g for g in graphs if g.startswith('citizen_')]

    node_usage = defaultdict(lambda: {'count': 0, 'graphs': []})
    link_usage = defaultdict(lambda: {'count': 0, 'graphs': []})

    for graph in citizen_graphs:
        # Node usage
        result = r.execute_command('GRAPH.QUERY', graph,
            'MATCH (n) RETURN n.node_type, count(n)'
        )
        for row in result[1]:
            if row and row[0]:
                node_type = row[0]
                count = row[1] if len(row) > 1 else 0
                node_usage[node_type]['count'] += count
                node_usage[node_type]['graphs'].append(graph)

        # Link usage
        result = r.execute_command('GRAPH.QUERY', graph,
            'MATCH ()-[r]-() RETURN type(r), count(r)'
        )
        for row in result[1]:
            if row and row[0]:
                link_type = row[0]
                count = row[1] if len(row) > 1 else 0
                link_usage[link_type]['count'] += count
                link_usage[link_type]['graphs'].append(graph)

    return dict(node_usage), dict(link_usage)


def render_field(field):
    """Render a field specification as markdown."""
    md = f"- `{field['name']}` ({field['type']})"

    if field.get('required') is not None:
        md += f" - {'REQUIRED' if field['required'] else 'Optional'}"

    if field.get('enum_values'):
        md += f" - Allowed values: {', '.join(f'`{v}`' for v in field['enum_values'])}"
    elif field.get('range_min') is not None and field.get('range_max') is not None:
        md += f" - Range: [{field['range_min']}, {field['range_max']}]"

    if field.get('description'):
        md += f"\n  - {field['description']}"

    return md + "\n"


def generate_complete_reference(universal_nodes, universal_links, node_schemas, link_schemas):
    """Generate complete markdown reference (pure schema, no usage statistics)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# Mind Protocol - Complete Type Reference

**Auto-generated from schema_registry (FalkorDB)**
**Last updated:** {timestamp}

This is the **single source of truth** for all node and link types in the Mind Protocol consciousness infrastructure.

**Contents:**
- Part 1: Universal Node Attributes (inherited by ALL 44 node types)
- Part 2: Universal Link Attributes (inherited by ALL 23 link types)
- Part 3: Node Type Inventory (44 types with full specifications)
- Part 4: Link Type Inventory (23 types with full specifications)

---

## Part 1: Universal Node Attributes

**These attributes are inherited by ALL {len(node_schemas)} node types.**

Every node in the consciousness graph has these base attributes in addition to its type-specific fields.

"""

    # Universal node attributes by category
    for category_name, fields in sorted(universal_nodes.items()):
        md += f"### {category_name.replace('_', ' ').title()}\n\n"
        for field in fields:
            md += render_field(field)
        md += "\n"

    md += """---

## Part 2: Universal Link Attributes

**These attributes are inherited by ALL {len_links} link types.**

Every link in the consciousness graph has these base attributes in addition to its type-specific fields.

""".format(len_links=len(link_schemas))

    # Universal link attributes by category
    for category_name, fields in sorted(universal_links.items()):
        md += f"### {category_name.replace('_', ' ').title()}\n\n"
        for field in fields:
            md += render_field(field)
        md += "\n"

    md += f"""---

## Part 3: Node Type Inventory

**Total:** {len(node_schemas)} node types defined

"""

    # Group node types by universality (U3_, U4_, L4_)
    u3_nodes = {k: v for k, v in node_schemas.items() if v.get('universality', '').startswith('U3')}
    u4_nodes = {k: v for k, v in node_schemas.items() if v.get('universality', '').startswith('U4')}
    l4_nodes = {k: v for k, v in node_schemas.items() if v.get('universality', '').startswith('L4')}

    if u3_nodes:
        md += f"### U3_ Types (Universal L1-L3) - {len(u3_nodes)} Types\n\n"
        for type_name, schema in sorted(u3_nodes.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    if u4_nodes:
        md += f"### U4_ Types (Universal L1-L4) - {len(u4_nodes)} Types\n\n"
        for type_name, schema in sorted(u4_nodes.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    if l4_nodes:
        md += f"### L4_ Types (Protocol Law) - {len(l4_nodes)} Types\n\n"
        for type_name, schema in sorted(l4_nodes.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    md += f"""---

## Part 4: Link Type Inventory

**Total:** {len(link_schemas)} link types defined

"""

    # Group link types by universality
    u3_links = {k: v for k, v in link_schemas.items() if v.get('universality', '').startswith('U3')}
    u4_links = {k: v for k, v in link_schemas.items() if v.get('universality', '').startswith('U4')}
    l4_links = {k: v for k, v in link_schemas.items() if v.get('universality', '').startswith('L4')}

    if u3_links:
        md += f"### U3_ Link Types (Universal L1-L3) - {len(u3_links)} Types\n\n"
        for type_name, schema in sorted(u3_links.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    if u4_links:
        md += f"### U4_ Link Types (Universal L1-L4) - {len(u4_links)} Types\n\n"
        for type_name, schema in sorted(u4_links.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    if l4_links:
        md += f"### L4_ Link Types (Protocol Law) - {len(l4_links)} Types\n\n"
        for type_name, schema in sorted(l4_links.items()):
            md += f"**{type_name}**\n\n"
            md += f"- **Universality:** {schema.get('universality', 'N/A')}\n"
            md += f"- **Description:** {schema['description']}\n"

            if schema['required_fields']:
                md += "\n**Type-Specific Required Fields:**\n"
                for field in schema['required_fields']:
                    md += render_field(field)

            if schema['optional_fields']:
                md += "\n**Type-Specific Optional Fields:**\n"
                for field in schema['optional_fields']:
                    md += render_field(field)

            md += "\n"

    md += """---

## How to Update

**To add/modify a node or link type:**
1. Update `tools/complete_schema_data.py` with the new/modified type
2. Run `python tools/complete_schema_ingestion.py` to re-ingest to schema_registry
3. Run `python tools/generate_complete_type_reference.py --write-file` to regenerate this file

**Schema Registry Location:** FalkorDB graph `schema_registry`

**This document is auto-generated - DO NOT edit manually**
"""

    return md


def update_claude_md_type_reference(guide_text):
    """
    Update the "Mind Protocol - Complete Type Reference" section in CLAUDE.md files.

    Replaces the section from "# Mind Protocol - Complete Type Reference"
    to the next top-level heading (or end of file) with the new guide_text.
    """
    import re

    files_to_update = [CITIZENS_CLAUDE_PATH, COLLECTIVE_CLAUDE_PATH]

    for claude_path in files_to_update:
        if not claude_path.exists():
            print(f"Skipping {claude_path.name} - file not found", file=sys.stderr)
            continue

        # Read entire file
        with open(claude_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has the type reference section
        if "# Mind Protocol - Complete Type Reference" not in content:
            print(f"Skipping {claude_path.name} - no type reference section found", file=sys.stderr)
            continue

        # Find and replace the section
        # Pattern: from "# Mind Protocol - Complete Type Reference" until next # heading or EOF
        pattern = r'# Mind Protocol - Complete Type Reference\n.*?(?=\n# [A-Z]|\Z)'

        replacement = guide_text.rstrip()  # Remove trailing whitespace

        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write back
        with open(claude_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Updated type reference in: {claude_path.relative_to(MIND_PROTOCOL_ROOT)}", file=sys.stderr)


def main():
    """Generate complete type reference from schema_registry (pure schema, no usage)."""
    write_file = '--write-file' in sys.argv

    try:
        r = connect_to_falkordb()

        # Query complete schema
        print("Querying schema_registry...", file=sys.stderr)
        universal_nodes = get_universal_node_attributes(r)
        universal_links = get_universal_link_attributes(r)
        node_schemas = get_node_type_schemas(r)
        link_schemas = get_link_type_schemas(r)

        print(f"  Universal node attrs: {sum(len(v) for v in universal_nodes.values())} fields", file=sys.stderr)
        print(f"  Universal link attrs: {sum(len(v) for v in universal_links.values())} fields", file=sys.stderr)
        print(f"  Node types: {len(node_schemas)} defined", file=sys.stderr)
        print(f"  Link types: {len(link_schemas)} defined", file=sys.stderr)

        # Generate reference (pure schema)
        guide_text = generate_complete_reference(universal_nodes, universal_links, node_schemas, link_schemas)

        # Write to file if requested
        if write_file:
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                f.write(guide_text)
            print(f"\nWrote to: {OUTPUT_PATH}", file=sys.stderr)

            # Also update the CLAUDE.md files
            print("\nUpdating CLAUDE.md files...", file=sys.stderr)
            update_claude_md_type_reference(guide_text)
            print("CLAUDE.md updates complete", file=sys.stderr)

        # Return JSON (universe-engine pattern)
        result = {
            "success": True,
            "guide_text": guide_text,
            "schema_analysis": {
                "universal_node_fields": sum(len(v) for v in universal_nodes.values()),
                "universal_link_fields": sum(len(v) for v in universal_links.values()),
                "node_types_defined": len(node_schemas),
                "link_types_defined": len(link_schemas)
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
