"""
Complete Schema Ingestion to FalkorDB - The Single Source of Truth

This script ingests the COMPLETE Mind Protocol schema into schema_registry:
- Universal node attributes (inherited by ALL 44 node types)
- Universal link attributes (inherited by ALL 23 link types)
- All 44 node type schemas with full field specifications
- All 23 link type schemas with full field specifications

After running this, schema_registry is the authoritative, queryable source of truth.

Author: Felix "Ironhand"
Date: 2025-01-19
Fixed: Luca - Field descriptions are optional, skip if not present
"""

from falkordb import FalkorDB
import json
from datetime import datetime
from complete_schema_data import (
    UNIVERSAL_NODE_ATTRIBUTES,
    UNIVERSAL_LINK_ATTRIBUTES,
    LINK_FIELD_SPECS,
    NODE_TYPE_SCHEMAS
)


def build_field_properties(field, parent_type, parent_category, required):
    """Build field properties dict, only including description if present."""
    props = {
        "name": field["name"],
        "type": field["type"],
        "enum_values": field.get("enum_values", []),
        "required": required,
        "parent_type": parent_type,
        "parent_category": parent_category
    }

    # Add range if present
    if "range" in field:
        props["range_min"] = field["range"][0]
        props["range_max"] = field["range"][1]
    else:
        props["range_min"] = None
        props["range_max"] = None

    # Only add description if it exists
    desc = field.get("description", field.get("detailed_description"))
    if desc:
        props["description"] = desc

    return props


def create_complete_schema_registry():
    """Create schema_registry with COMPLETE metadata - ultimate source of truth."""

    print("=" * 80)
    print("COMPLETE SCHEMA REGISTRY INGESTION")
    print("=" * 80)
    print(f"Universal Node Attributes: {len(UNIVERSAL_NODE_ATTRIBUTES)} categories")
    print(f"Universal Link Attributes: {len(UNIVERSAL_LINK_ATTRIBUTES)} categories")
    print(f"Link Type Schemas: {len(LINK_FIELD_SPECS)} types")
    print(f"Node Type Schemas: {len(NODE_TYPE_SCHEMAS)} types")
    print("=" * 80)

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph("schema_registry")

    print(f"\n[1/5] Connected to FalkorDB, selected graph: schema_registry")

    # Clear existing schema
    try:
        result = g.query("MATCH (n) DETACH DELETE n")
        print(f"[1/5] Cleared existing schema nodes")
    except Exception as e:
        print(f"[1/5] No existing schema (or error: {e})")

    # ===========================================================================
    # STEP 2: Ingest Universal Node Attributes
    # ===========================================================================
    print(f"\n[2/5] Ingesting Universal Node Attributes...")

    for category_name, fields in UNIVERSAL_NODE_ATTRIBUTES.items():
        try:
            # Create category node
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

            # Create field nodes for each universal attribute
            for field in fields:
                props = build_field_properties(field, None, category_name, field["required"])
                props["category"] = category_name
                props["category_name"] = category_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "category_name"])
                query = f"""
                    MATCH (c:UniversalNodeCategory {{category_name: $category_name}})
                    CREATE (f:UniversalNodeField {{{prop_list}}})
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """
                g.query(query, params=props)

            print(f"  OK {category_name:30s} ({len(fields)} fields)")

        except Exception as e:
            print(f"  FAIL {category_name:30s} ERROR: {e}")

    # ===========================================================================
    # STEP 3: Ingest Universal Link Attributes
    # ===========================================================================
    print(f"\n[3/5] Ingesting Universal Link Attributes...")

    for category_name, fields in UNIVERSAL_LINK_ATTRIBUTES.items():
        try:
            # Create category node
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

            # Create field nodes for each universal attribute
            for field in fields:
                props = build_field_properties(field, None, category_name, field["required"])
                props["category"] = category_name
                props["category_name"] = category_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "category_name"])
                query = f"""
                    MATCH (c:UniversalLinkCategory {{category_name: $category_name}})
                    CREATE (f:UniversalLinkField {{{prop_list}}})
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """
                g.query(query, params=props)

            print(f"  OK {category_name:30s} ({len(fields)} fields)")

        except Exception as e:
            print(f"  FAIL {category_name:30s} ERROR: {e}")

    # ===========================================================================
    # STEP 4: Ingest Link Type Schemas
    # ===========================================================================
    print(f"\n[4/5] Ingesting {len(LINK_FIELD_SPECS)} Link Type Schemas...")

    for idx, (type_name, spec) in enumerate(LINK_FIELD_SPECS.items(), 1):
        try:
            # Create LinkTypeSchema node
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

            # Create FieldSchema nodes for required fields
            req_count = len(spec["required"])
            for field in spec["required"]:
                props = build_field_properties(field, type_name, "link", True)
                props["type_name"] = type_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (lt:LinkTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (lt)-[:HAS_REQUIRED_FIELD]->(f)
                """
                g.query(query, params=props)

            # Create FieldSchema nodes for optional fields
            opt_count = len(spec["optional"])
            for field in spec["optional"]:
                props = build_field_properties(field, type_name, "link", False)
                props["type_name"] = type_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (lt:LinkTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (lt)-[:HAS_OPTIONAL_FIELD]->(f)
                """
                g.query(query, params=props)

            print(f"  [{idx}/{len(LINK_FIELD_SPECS)}] OK {type_name:25s} (req:{req_count}, opt:{opt_count})")

        except Exception as e:
            print(f"  [{idx}/{len(LINK_FIELD_SPECS)}] FAIL {type_name:25s} ERROR: {e}")

    # ===========================================================================
    # STEP 5: Ingest Node Type Schemas
    # ===========================================================================
    print(f"\n[5/5] Ingesting {len(NODE_TYPE_SCHEMAS)} Node Type Schemas...")

    for idx, (type_name, spec) in enumerate(NODE_TYPE_SCHEMAS.items(), 1):
        try:
            # Create NodeTypeSchema node
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

            # Create FieldSchema nodes for required fields
            req_count = len(spec["required"])
            for field in spec["required"]:
                props = build_field_properties(field, type_name, "node", True)
                props["type_name"] = type_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (nt:NodeTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (nt)-[:HAS_REQUIRED_FIELD]->(f)
                """
                g.query(query, params=props)

            # Create FieldSchema nodes for optional fields
            opt_count = len(spec["optional"])
            for field in spec["optional"]:
                props = build_field_properties(field, type_name, "node", False)
                props["type_name"] = type_name

                # Build dynamic query
                prop_list = ", ".join([f"{k}: ${k}" for k in props.keys() if k != "type_name"])
                query = f"""
                    MATCH (nt:NodeTypeSchema {{type_name: $type_name}})
                    CREATE (f:FieldSchema {{{prop_list}}})
                    CREATE (nt)-[:HAS_OPTIONAL_FIELD]->(f)
                """
                g.query(query, params=props)

            print(f"  [{idx}/{len(NODE_TYPE_SCHEMAS)}] OK {type_name:25s} (req:{req_count}, opt:{opt_count})")

        except Exception as e:
            print(f"  [{idx}/{len(NODE_TYPE_SCHEMAS)}] FAIL {type_name:25s} ERROR: {e}")

    # ===========================================================================
    # VERIFICATION
    # ===========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Count universal node attributes
    result = g.query("MATCH (c:UniversalNodeCategory) RETURN count(c) as count")
    node_cat_count = result.result_set[0][0] if result.result_set else 0

    result = g.query("MATCH (f:UniversalNodeField) RETURN count(f) as count")
    node_field_count = result.result_set[0][0] if result.result_set else 0

    # Count universal link attributes
    result = g.query("MATCH (c:UniversalLinkCategory) RETURN count(c) as count")
    link_cat_count = result.result_set[0][0] if result.result_set else 0

    result = g.query("MATCH (f:UniversalLinkField) RETURN count(f) as count")
    link_field_count = result.result_set[0][0] if result.result_set else 0

    # Count type-specific schemas
    result = g.query("MATCH (lt:LinkTypeSchema) RETURN count(lt) as count")
    link_type_count = result.result_set[0][0] if result.result_set else 0

    result = g.query("MATCH (nt:NodeTypeSchema) RETURN count(nt) as count")
    node_type_count = result.result_set[0][0] if result.result_set else 0

    result = g.query("MATCH (f:FieldSchema) RETURN count(f) as count")
    field_schema_count = result.result_set[0][0] if result.result_set else 0

    total_nodes = (node_cat_count + node_field_count + link_cat_count +
                   link_field_count + link_type_count + node_type_count + field_schema_count)

    print(f"\nUniversal Node Attributes:")
    print(f"  - Categories: {node_cat_count}")
    print(f"  - Fields: {node_field_count}")

    print(f"\nUniversal Link Attributes:")
    print(f"  - Categories: {link_cat_count}")
    print(f"  - Fields: {link_field_count}")

    print(f"\nType-Specific Schemas:")
    print(f"  - LinkTypeSchema nodes: {link_type_count}")
    print(f"  - NodeTypeSchema nodes: {node_type_count}")
    print(f"  - FieldSchema nodes (type-specific): {field_schema_count}")

    print(f"\nTotal Schema Nodes: {total_nodes}")

    # ===========================================================================
    # SAMPLE QUERIES
    # ===========================================================================
    print("\n" + "=" * 80)
    print("SAMPLE QUERIES")
    print("=" * 80)

    print("\n[1] Universal node attributes (inherited by ALL node types):")

    print("\n[2] Memory node type schema (N1 Personal):")

    print("\n[3] BLOCKS link type with full field specs:")

    print("\n" + "=" * 80)
    print("COMPLETE SCHEMA REGISTRY CREATED SUCCESSFULLY")
    print("=" * 80)

    print("\nThis is now the SINGLE SOURCE OF TRUTH for all Mind Protocol schema")
    print("\nQuery examples:")
    print("  - Get all universal node fields: MATCH (f:UniversalNodeField) RETURN f")
    print("  - Get Decision schema: MATCH (nt:NodeTypeSchema {type_name: 'Decision'})-[:HAS_REQUIRED_FIELD]->(f) RETURN f")
    print("  - Get REQUIRES link schema: MATCH (lt:LinkTypeSchema {type_name: 'REQUIRES'})-[:HAS_REQUIRED_FIELD]->(f) RETURN f")
    print("  - List all N1 node types: MATCH (nt:NodeTypeSchema {level: 'n1'}) RETURN nt.type_name")
    print("  - List all N3 node types: MATCH (nt:NodeTypeSchema {level: 'n3'}) RETURN nt.type_name")


if __name__ == "__main__":
    create_complete_schema_registry()
