"""
Update Schema in ALL Graphs (Citizens + Orgs + schema_registry)

Runs the complete schema ingestion on every relevant graph.
"""

from falkordb import FalkorDB
import os
import sys

# Import the ingestion logic
from complete_schema_ingestion import (
    UNIVERSAL_NODE_ATTRIBUTES,
    UNIVERSAL_LINK_ATTRIBUTES,
    LINK_FIELD_SPECS,
    NODE_TYPE_SCHEMAS,
    build_field_properties
)
from datetime import datetime


def ingest_schema_to_graph(graph_name):
    """Ingest complete schema to specified graph."""

    db = FalkorDB(host=os.getenv('FALKOR_HOST', 'localhost'), port=6379)
    g = db.select_graph(graph_name)

    try:
        # Clear existing schema
        g.query("MATCH (n:UniversalNodeCategory) DETACH DELETE n")
        g.query("MATCH (n:UniversalLinkCategory) DETACH DELETE n")
        g.query("MATCH (n:LinkTypeSchema) DETACH DELETE n")
        g.query("MATCH (n:NodeTypeSchema) DETACH DELETE n")

        # Ingest Universal Node Attributes
        for category_name, fields in UNIVERSAL_NODE_ATTRIBUTES.items():
            g.query("""
                CREATE (c:UniversalNodeCategory {
                    category_name: $category_name,
                    applies_to: 'ALL_NODE_TYPES',
                    field_count: $field_count,
                    created_at: $created_at
                })
            """, params={
                "category_name": category_name,
                "field_count": len(fields),
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            for field in fields:
                props = build_field_properties(field, None, category_name, field["required"])
                props["category"] = category_name
                props["category_name"] = category_name

                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "category_name"])
                query = f"""
                    MATCH (c:UniversalNodeCategory {{category_name: $category_name}})
                    CREATE (f:UniversalNodeField {{{prop_list}}})
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """
                g.query(query, params=props)

        # Ingest Universal Link Attributes
        for category_name, fields in UNIVERSAL_LINK_ATTRIBUTES.items():
            g.query("""
                CREATE (c:UniversalLinkCategory {
                    category_name: $category_name,
                    applies_to: 'ALL_LINK_TYPES',
                    field_count: $field_count,
                    created_at: $created_at
                })
            """, params={
                "category_name": category_name,
                "field_count": len(fields),
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            for field in fields:
                props = build_field_properties(field, None, category_name, field["required"])
                props["category"] = category_name
                props["category_name"] = category_name

                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "category_name"])
                query = f"""
                    MATCH (c:UniversalLinkCategory {{category_name: $category_name}})
                    CREATE (f:UniversalLinkField {{{prop_list}}})
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """
                g.query(query, params=props)

        # Ingest Link Type Schemas
        for type_name, spec in LINK_FIELD_SPECS.items():
            g.query("""
                CREATE (lt:LinkTypeSchema {
                    type_name: $type_name,
                    universality: $universality,
                    description: $description,
                    created_at: $created_at,
                    version: 'v3.0'
                })
            """, params={
                "type_name": type_name,
                "universality": spec["universality"],
                "description": spec["description"],
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            for field in spec["required"]:
                props = build_field_properties(field, type_name, "link", True)
                props["type_name"] = type_name
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (lt:LinkTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (lt)-[:HAS_REQUIRED_FIELD]->(f)
                """
                g.query(query, params=props)

            for field in spec["optional"]:
                props = build_field_properties(field, type_name, "link", False)
                props["type_name"] = type_name
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (lt:LinkTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (lt)-[:HAS_OPTIONAL_FIELD]->(f)
                """
                g.query(query, params=props)

        # Ingest Node Type Schemas
        for type_name, spec in NODE_TYPE_SCHEMAS.items():
            g.query("""
                CREATE (nt:NodeTypeSchema {
                    type_name: $type_name,
                    universality: $universality,
                    description: $description,
                    created_at: $created_at,
                    version: 'v3.0'
                })
            """, params={
                "type_name": type_name,
                "universality": spec["universality"],
                "description": spec["description"],
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            for field in spec["required"]:
                props = build_field_properties(field, type_name, "node", True)
                props["type_name"] = type_name
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (nt:NodeTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (nt)-[:HAS_REQUIRED_FIELD]->(f)
                """
                g.query(query, params=props)

            for field in spec["optional"]:
                props = build_field_properties(field, type_name, "node", False)
                props["type_name"] = type_name
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (nt:NodeTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (nt)-[:HAS_OPTIONAL_FIELD]->(f)
                """
                g.query(query, params=props)

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    """Update all relevant graphs."""

    db = FalkorDB(host=os.getenv('FALKOR_HOST', 'localhost'), port=6379)
    all_graphs = db.list_graphs()

    # Target graphs: consciousness_, citizen_, ecosystem
    target_graphs = [
        g for g in all_graphs
        if 'consciousness_' in g or 'citizen_' in g or 'ecosystem' in g
    ]

    # Always include schema_registry
    if 'schema_registry' not in target_graphs:
        target_graphs.append('schema_registry')

    print("=" * 80)
    print("UPDATING SCHEMA IN ALL GRAPHS")
    print("=" * 80)
    print(f"Total graphs to update: {len(target_graphs)}")
    print()

    success_count = 0
    fail_count = 0

    for graph_name in sorted(target_graphs):
        print(f"Updating: {graph_name:50s} ", end="", flush=True)
        if ingest_schema_to_graph(graph_name):
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1

    print()
    print("=" * 80)
    print(f"SUCCESS: {success_count} graphs updated")
    print(f"FAILED:  {fail_count} graphs")
    print("=" * 80)


if __name__ == "__main__":
    main()
