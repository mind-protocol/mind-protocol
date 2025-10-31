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
                g.query("""
                    MATCH (c:UniversalNodeCategory {category_name: $category_name})
                    CREATE (f:UniversalNodeField {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        range_min: $range_min,
                        range_max: $range_max,
                        description: $description,
                        required: $required,
                        category: $category_name
                    })
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """, params={
                    "category_name": category_name,
                    "name": field["name"],
                    "type": field["type"],
                    "enum_values": field.get("enum_values", []),
                    "range_min": field.get("range", [None, None])[0] if "range" in field else None,
                    "range_max": field.get("range", [None, None])[1] if "range" in field else None,
                    "description": field.get("description", field.get("detailed_description", "")),
                    "required": field["required"]
                })

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
                g.query("""
                    MATCH (c:UniversalLinkCategory {category_name: $category_name})
                    CREATE (f:UniversalLinkField {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        range_min: $range_min,
                        range_max: $range_max,
                        description: $description,
                        required: $required,
                        category: $category_name
                    })
                    CREATE (c)-[:HAS_UNIVERSAL_FIELD]->(f)
                """, params={
                    "category_name": category_name,
                    "name": field["name"],
                    "type": field["type"],
                    "enum_values": field.get("enum_values", []),
                    "range_min": field.get("range", [None, None])[0] if "range" in field else None,
                    "range_max": field.get("range", [None, None])[1] if "range" in field else None,
                    "description": field.get("description", field.get("detailed_description", "")),
                    "required": field["required"]
                })

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
                g.query("""
                    MATCH (lt:LinkTypeSchema {type_name: $type_name})
                    CREATE (f:FieldSchema {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        range_min: $range_min,
                        range_max: $range_max,
                        description: $description,
                        required: true,
                        parent_type: $type_name,
                        parent_category: 'link'
                    })
                    CREATE (lt)-[:HAS_REQUIRED_FIELD]->(f)
                """, params={
                    "type_name": type_name,
                    "name": field["name"],
                    "type": field["type"],
                    "enum_values": field.get("enum_values", []),
                    "range_min": field.get("range", [None, None])[0] if "range" in field else None,
                    "range_max": field.get("range", [None, None])[1] if "range" in field else None,
                    "description": field.get("description", field.get("detailed_description", field["name"]))
                })

            # Create FieldSchema nodes for optional fields
            opt_count = len(spec["optional"])
            for field in spec["optional"]:
                g.query("""
                    MATCH (lt:LinkTypeSchema {type_name: $type_name})
                    CREATE (f:FieldSchema {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        description: $description,
                        required: false,
                        parent_type: $type_name,
                        parent_category: 'link'
                    })
                    CREATE (lt)-[:HAS_OPTIONAL_FIELD]->(f)
                """, params={
                    "type_name": type_name,
                    "name": field.get("name", ""),
                    "type": field.get("type", "string"),
                    "enum_values": field.get("enum_values", []),
                    "description": field.get("description", field.get("detailed_description", ""))
                })

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
                g.query("""
                    MATCH (nt:NodeTypeSchema {type_name: $type_name})
                    CREATE (f:FieldSchema {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        range_min: $range_min,
                        range_max: $range_max,
                        description: $description,
                        required: true,
                        parent_type: $type_name,
                        parent_category: 'node'
                    })
                    CREATE (nt)-[:HAS_REQUIRED_FIELD]->(f)
                """, params={
                    "type_name": type_name,
                    "name": field["name"],
                    "type": field["type"],
                    "enum_values": field.get("enum_values", []),
                    "range_min": field.get("range", [None, None])[0] if "range" in field else None,
                    "range_max": field.get("range", [None, None])[1] if "range" in field else None,
                    "description": field.get("description", field.get("detailed_description", field["name"]))
                })

            # Create FieldSchema nodes for optional fields
            opt_count = len(spec["optional"])
            for field in spec["optional"]:
                g.query("""
                    MATCH (nt:NodeTypeSchema {type_name: $type_name})
                    CREATE (f:FieldSchema {
                        name: $name,
                        type: $type,
                        enum_values: $enum_values,
                        description: $description,
                        required: false,
                        parent_type: $type_name,
                        parent_category: 'node'
                    })
                    CREATE (nt)-[:HAS_OPTIONAL_FIELD]->(f)
                """, params={
                    "type_name": type_name,
                    "name": field.get("name", ""),
                    "type": field.get("type", "string"),
                    "enum_values": field.get("enum_values", []),
                    "description": field.get("description", field.get("detailed_description", ""))
                })

            print(f"  [{idx}/{len(NODE_TYPE_SCHEMAS)}] OK {type_name:30s} (req:{req_count}, opt:{opt_count})")

        except Exception as e:
            print(f"  [{idx}/{len(NODE_TYPE_SCHEMAS)}] FAIL {type_name:30s} ERROR: {e}")

    # ===========================================================================
    # VERIFICATION
    # ===========================================================================
    print(f"\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    universal_node_cats = g.query("MATCH (c:UniversalNodeCategory) RETURN count(c)").result_set[0][0]
    universal_link_cats = g.query("MATCH (c:UniversalLinkCategory) RETURN count(c)").result_set[0][0]
    universal_node_fields = g.query("MATCH (f:UniversalNodeField) RETURN count(f)").result_set[0][0]
    universal_link_fields = g.query("MATCH (f:UniversalLinkField) RETURN count(f)").result_set[0][0]
    link_types = g.query("MATCH (lt:LinkTypeSchema) RETURN count(lt)").result_set[0][0]
    node_types = g.query("MATCH (nt:NodeTypeSchema) RETURN count(nt)").result_set[0][0]
    field_schemas = g.query("MATCH (f:FieldSchema) RETURN count(f)").result_set[0][0]

    print(f"\nUniversal Node Attributes:")
    print(f"  - Categories: {universal_node_cats}")
    print(f"  - Fields: {universal_node_fields}")

    print(f"\nUniversal Link Attributes:")
    print(f"  - Categories: {universal_link_cats}")
    print(f"  - Fields: {universal_link_fields}")

    print(f"\nType-Specific Schemas:")
    print(f"  - LinkTypeSchema nodes: {link_types}")
    print(f"  - NodeTypeSchema nodes: {node_types}")
    print(f"  - FieldSchema nodes (type-specific): {field_schemas}")

    print(f"\nTotal Schema Nodes: {universal_node_cats + universal_link_cats + link_types + node_types + universal_node_fields + universal_link_fields + field_schemas}")

    # Sample queries
    print(f"\n" + "=" * 80)
    print("SAMPLE QUERIES")
    print("=" * 80)

    print(f"\n[1] Universal node attributes (inherited by ALL node types):")
    result = g.query("""
        MATCH (c:UniversalNodeCategory)-[:HAS_UNIVERSAL_FIELD]->(f:UniversalNodeField)
        WHERE c.category_name = 'core_idsubentity'
        RETURN f.name, f.type, f.required, f.description
        ORDER BY f.name
        LIMIT 3
    """)
    for row in result.result_set:
        print(f"  - {row[0]:20s} ({row[1]:10s}) required={row[2]:5} | {row[3]}")

    print(f"\n[2] Memory node type schema (N1 Personal):")
    result = g.query("""
        MATCH (nt:NodeTypeSchema {type_name: 'Memory'})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
        RETURN f.name, f.type, f.description
        ORDER BY f.name
    """)
    for row in result.result_set:
        print(f"  - {row[0]:20s} ({row[1]:10s}) | {row[2]}")

    print(f"\n[3] BLOCKS link type with full field specs:")
    result = g.query("""
        MATCH (lt:LinkTypeSchema {type_name: 'BLOCKS'})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
        RETURN f.name, f.type, f.enum_values, f.description
        ORDER BY f.name
    """)
    for row in result.result_set:
        field = row[0]
        ftype = row[1]
        enums = row[2] if len(row) > 2 else []
        desc = row[3] if len(row) > 3 else ""
        if enums:
            print(f"  - {field:25s} ({ftype:10s}) enum: {enums}")
        else:
            print(f"  - {field:25s} ({ftype:10s})")

    print(f"\n" + "=" * 80)
    print("COMPLETE SCHEMA REGISTRY CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nThis is now the SINGLE SOURCE OF TRUTH for all Mind Protocol schema")
    print(f"\nQuery examples:")
    print(f"  - Get all universal node fields: MATCH (f:UniversalNodeField) RETURN f")
    print(f"  - Get Decision schema: MATCH (nt:NodeTypeSchema {{type_name: 'Decision'}})-[:HAS_REQUIRED_FIELD]->(f) RETURN f")
    print(f"  - Get REQUIRES link schema: MATCH (lt:LinkTypeSchema {{type_name: 'REQUIRES'}})-[:HAS_REQUIRED_FIELD]->(f) RETURN f")
    print(f"  - List all N1 node types: MATCH (nt:NodeTypeSchema {{level: 'n1'}}) RETURN nt.type_name")
    print(f"  - List all N3 node types: MATCH (nt:NodeTypeSchema {{level: 'n3'}}) RETURN nt.type_name")


if __name__ == "__main__":
    create_complete_schema_registry()
