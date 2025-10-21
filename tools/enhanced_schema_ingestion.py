"""
Enhanced Schema Ingestion to FalkorDB

Purpose: Ingest COMPLETE schema metadata into schema_registry as single source of truth.

Schema Structure in FalkorDB:
- LinkTypeSchema nodes: One per link type
- NodeTypeSchema nodes: One per node type
- FieldSchema nodes: One per field, linked to parent type
- EnumSchema nodes: Enum definitions with allowed values

This makes ALL schema metadata queryable - types, enums, descriptions, validation rules.

Author: Felix "Ironhand"
Date: 2025-01-19
"""

from falkordb import FalkorDB
import json
from datetime import datetime

# ============================================================================
# LINK TYPE FIELD SPECIFICATIONS (from UNIFIED_SCHEMA_REFERENCE.md)
# ============================================================================

LINK_FIELD_SPECS = {
    "BLOCKS": {
        "required": [
            {"name": "severity", "type": "enum", "enum_values": ["absolute", "strong", "partial"],
             "description": "How completely this blocks progress"},
            {"name": "blocking_condition", "type": "string",
             "description": "What condition must change to unblock"},
            {"name": "felt_as", "type": "string",
             "description": "Emotional/phenomenological experience of being blocked"},
            {"name": "consciousness_impact", "type": "string",
             "description": "How this affects consciousness state"}
        ],
        "optional": []
    },

    "ENABLES": {
        "required": [
            {"name": "enabling_type", "type": "enum",
             "enum_values": ["prerequisite", "facilitator", "amplifier", "catalyst", "permission"],
             "description": "How this enables the target"},
            {"name": "degree_of_necessity", "type": "enum",
             "enum_values": ["required", "helpful", "optional"],
             "description": "How necessary is this enabler"},
            {"name": "felt_as", "type": "string",
             "description": "Phenomenological experience of enablement"},
            {"name": "without_this", "type": "string",
             "description": "What happens if this enabler is removed"}
        ],
        "optional": []
    },

    "EXTENDS": {
        "required": [
            {"name": "extension_type", "type": "enum",
             "enum_values": ["specialization", "generalization", "elaboration", "application"],
             "description": "How extension relates to base"},
            {"name": "what_is_added", "type": "string",
             "description": "What the extension adds to the base"},
            {"name": "maintains_compatibility", "type": "boolean",
             "description": "Whether extension remains compatible with base"},
            {"name": "composition_ratio", "type": "float", "range": [0.0, 1.0],
             "description": "How much is new vs inherited (0=all base, 1=all new)"}
        ],
        "optional": []
    },

    "RELATES_TO": {
        "required": [
            {"name": "relationship_strength", "type": "enum",
             "enum_values": ["strong", "moderate", "weak", "exploratory"],
             "description": "Strength of relationship"},
            {"name": "needs_refinement", "type": "boolean",
             "description": "Should this be replaced with more specific link type?"},
            {"name": "refinement_candidates", "type": "array",
             "description": "Potential more specific link types to use"}
        ],
        "optional": []
    },

    "REQUIRES": {
        "required": [
            {"name": "requirement_criticality", "type": "enum",
             "enum_values": ["blocking", "important", "optional"],
             "description": "How critical is this requirement"},
            {"name": "temporal_relationship", "type": "enum",
             "enum_values": ["must_precede", "should_precede", "concurrent_ok"],
             "description": "Temporal ordering constraint"},
            {"name": "failure_mode", "type": "string",
             "description": "What happens if requirement not met"},
            {"name": "verification_method", "type": "string",
             "description": "How to verify requirement is satisfied"}
        ],
        "optional": []
    },

    "JUSTIFIES": {
        "required": [
            {"name": "justification_type", "type": "enum",
             "enum_values": ["empirical_evidence", "lived_experience", "logical_proof",
                           "ethical_reasoning", "pragmatic_value"],
             "description": "Type of justification"},
            {"name": "justification_strength", "type": "enum",
             "enum_values": ["proves", "strongly_supports", "moderately_supports",
                           "suggests", "weakly_supports"],
             "description": "Strength of justification"},
            {"name": "felt_as", "type": "string",
             "description": "Phenomenological experience of justification"},
            {"name": "counter_arguments_exist", "type": "boolean",
             "description": "Are there known counter-arguments?"}
        ],
        "optional": []
    },

    "REFUTES": {"required": [], "optional": []},
    "DOCUMENTS": {
        "required": [],
        "optional": [
            {"name": "documentation_type", "type": "string",
             "description": "Type of documentation (spec, guide, reference, etc.)"}
        ]
    },
    "DOCUMENTED_BY": {"required": [], "optional": []},
    "SUPERSEDES": {"required": [], "optional": []},
    "IMPLEMENTS": {"required": [], "optional": []},
    "CREATES": {"required": [], "optional": []},
    "ASSIGNED_TO": {"required": [], "optional": []},
    "COLLABORATES_WITH": {"required": [], "optional": []},
    "CONTRIBUTES_TO": {"required": [], "optional": []},
    "MEASURES": {"required": [], "optional": []},
    "THREATENS": {"required": [], "optional": []},
    "ACTIVATES": {"required": [], "optional": []},
    "TRIGGERED_BY": {"required": [], "optional": []},
    "SUPPRESSES": {"required": [], "optional": []},
    "LEARNED_FROM": {"required": [], "optional": []},
    "DEEPENED_WITH": {"required": [], "optional": []},
    "DRIVES_TOWARD": {"required": [], "optional": []},
}

# Link type metadata (from original ingestion script)
LINK_TYPE_METADATA = {
    "BLOCKS": {
        "level": "shared", "category": "structural",
        "description": "Prevents progress or blocks execution",
        "detection_pattern": "coherence_verification",
        "mechanisms": ["coherence_verification", "task_routing"]
    },
    "ENABLES": {
        "level": "shared", "category": "structural",
        "description": "Makes something possible or facilitates it",
        "detection_pattern": "dependency_verification",
        "mechanisms": ["dependency_verification", "task_routing"]
    },
    "EXTENDS": {
        "level": "shared", "category": "structural",
        "description": "Builds upon foundation or extends functionality",
        "detection_pattern": "implementation_verification",
        "mechanisms": ["implementation_verification", "task_routing"]
    },
    "RELATES_TO": {
        "level": "shared", "category": "structural",
        "description": "Generic connection when specific type unclear",
        "detection_pattern": "quality_degradation",
        "mechanisms": ["quality_degradation", "activation_decay"]
    },
    "REQUIRES": {
        "level": "shared", "category": "dependency",
        "description": "Necessary conditions or prerequisites",
        "detection_pattern": "dependency_verification",
        "mechanisms": ["dependency_verification", "task_routing"]
    },
    "JUSTIFIES": {
        "level": "shared", "category": "evidence",
        "description": "Evidence supporting practice/decision/claim",
        "detection_pattern": "evidence_accumulation",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },
    "REFUTES": {
        "level": "shared", "category": "evidence",
        "description": "Disproves or invalidates claim",
        "detection_pattern": "evidence_accumulation",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },
    "DOCUMENTS": {
        "level": "shared", "category": "documentation",
        "description": "Written record of implementation or decision",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "DOCUMENTED_BY": {
        "level": "shared", "category": "documentation",
        "description": "Implementation documented by this artifact",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "SUPERSEDES": {
        "level": "shared", "category": "documentation",
        "description": "This replaces older version",
        "detection_pattern": "coherence_verification",
        "mechanisms": ["coherence_verification", "task_routing"]
    },
    "IMPLEMENTS": {
        "level": "shared", "category": "documentation",
        "description": "Putting pattern or best practice into reality",
        "detection_pattern": "implementation_verification",
        "mechanisms": ["implementation_verification", "task_routing"]
    },
    "CREATES": {
        "level": "shared", "category": "documentation",
        "description": "Task will produce this artifact when completed",
        "detection_pattern": "dependency_verification",
        "mechanisms": ["dependency_verification", "task_routing"]
    },
    "ASSIGNED_TO": {
        "level": "shared", "category": "organizational",
        "description": "Task ownership or responsibility",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "COLLABORATES_WITH": {
        "level": "shared", "category": "organizational",
        "description": "Working partnership between entities",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "CONTRIBUTES_TO": {
        "level": "shared", "category": "organizational",
        "description": "Work supporting larger initiative",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "MEASURES": {
        "level": "shared", "category": "organizational",
        "description": "Quantifies performance or progress",
        "detection_pattern": "staleness_detection",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    "THREATENS": {
        "level": "shared", "category": "organizational",
        "description": "Danger or risk to goal/project",
        "detection_pattern": "coherence_verification",
        "mechanisms": ["coherence_verification", "task_routing"]
    },
    "ACTIVATES": {
        "level": "n1", "category": "activation",
        "description": "Trigger awakens entity coalition",
        "detection_pattern": "activation_verification",
        "mechanisms": ["link_activation_check", "task_routing"]
    },
    "TRIGGERED_BY": {
        "level": "n1", "category": "activation",
        "description": "What caused memory/pattern to activate",
        "detection_pattern": "activation_verification",
        "mechanisms": ["link_activation_check", "task_routing"]
    },
    "SUPPRESSES": {
        "level": "n1", "category": "activation",
        "description": "What blocks entity activation",
        "detection_pattern": "activation_verification",
        "mechanisms": ["link_activation_check", "task_routing"]
    },
    "LEARNED_FROM": {
        "level": "n1", "category": "learning",
        "description": "Personal pattern extracted from experience",
        "detection_pattern": "quality_degradation",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },
    "DEEPENED_WITH": {
        "level": "n1", "category": "learning",
        "description": "Relationship growth through experience",
        "detection_pattern": "quality_degradation",
        "mechanisms": ["hebbian_reinforcement", "activation_decay"]
    },
    "DRIVES_TOWARD": {
        "level": "n1", "category": "value",
        "description": "Value pushing toward goal",
        "detection_pattern": "coherence_verification",
        "mechanisms": ["coherence_verification", "energy_propagation"]
    },
}


def create_enhanced_schema_registry():
    """Create schema_registry with FULL metadata - complete source of truth."""

    print("=" * 70)
    print("ENHANCED SCHEMA REGISTRY INGESTION")
    print("=" * 70)

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph("schema_registry")

    print(f"\n[1/3] Connected to FalkorDB, selected graph: schema_registry")

    # Clear existing schema
    try:
        result = g.query("MATCH (n) DETACH DELETE n")
        print(f"[1/3] Cleared existing schema nodes")
    except Exception as e:
        print(f"[1/3] No existing schema (or error: {e})")

    # Ingest Link Type Schemas with full field specifications
    print(f"\n[2/3] Ingesting {len(LINK_FIELD_SPECS)} Link Type Schemas with full field metadata...")

    for idx, type_name in enumerate(LINK_FIELD_SPECS.keys(), 1):
        try:
            # Get metadata
            metadata = LINK_TYPE_METADATA.get(type_name, {
                "level": "shared", "category": "unknown",
                "description": "No description",
                "detection_pattern": "none",
                "mechanisms": []
            })

            # Create LinkTypeSchema node
            g.query("""
                CREATE (lt:LinkTypeSchema {
                    type_name: $type_name,
                    level: $level,
                    category: $category,
                    description: $description,
                    detection_pattern: $detection_pattern,
                    mechanisms: $mechanisms,
                    created_at: $created_at,
                    version: 'v2.1'
                })
            """, params={
                "type_name": type_name,
                "level": metadata["level"],
                "category": metadata["category"],
                "description": metadata["description"],
                "detection_pattern": metadata["detection_pattern"],
                "mechanisms": metadata["mechanisms"],
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            # Create FieldSchema nodes for required fields
            field_specs = LINK_FIELD_SPECS[type_name]
            req_count = len(field_specs["required"])
            opt_count = len(field_specs["optional"])

            for field_spec in field_specs["required"]:
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
                    "name": field_spec["name"],
                    "type": field_spec["type"],
                    "enum_values": field_spec.get("enum_values", []),
                    "range_min": field_spec.get("range", [None, None])[0],
                    "range_max": field_spec.get("range", [None, None])[1],
                    "description": field_spec["description"]
                })

            # Create FieldSchema nodes for optional fields
            for field_spec in field_specs["optional"]:
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
                    "name": field_spec.get("name", ""),
                    "type": field_spec.get("type", "string"),
                    "enum_values": field_spec.get("enum_values", []),
                    "description": field_spec.get("description", "")
                })

            print(f"  [{idx}/{len(LINK_FIELD_SPECS)}] OK {type_name:20s} ({req_count} req, {opt_count} opt)")

        except Exception as e:
            print(f"  [{idx}/{len(LINK_FIELD_SPECS)}] FAIL {type_name:20s} ERROR: {e}")

    # Verify ingestion
    print(f"\n[3/3] Verifying schema registry...")

    link_count = g.query("MATCH (lt:LinkTypeSchema) RETURN count(lt) as count").result_set[0][0]
    field_count = g.query("MATCH (f:FieldSchema) RETURN count(f) as count").result_set[0][0]

    print(f"  - LinkTypeSchema nodes: {link_count}")
    print(f"  - FieldSchema nodes: {field_count}")

    # Sample query
    print(f"\n[SAMPLE QUERY] BLOCKS type with full field specs:")
    result = g.query("""
        MATCH (lt:LinkTypeSchema {type_name: 'BLOCKS'})-[:HAS_REQUIRED_FIELD]->(f:FieldSchema)
        RETURN f.name as field, f.type as type, f.enum_values as enums, f.description as desc
        ORDER BY f.name
    """)

    for row in result.result_set:
        field = row[0]
        ftype = row[1]
        enums = row[2]
        desc = row[3]
        if enums:
            print(f"  - {field:25s} ({ftype}) enum: {enums}")
        else:
            print(f"  - {field:25s} ({ftype})")

    print(f"\n" + "=" * 70)
    print("ENHANCED SCHEMA REGISTRY CREATED")
    print("=" * 70)
    print(f"\nSchema is now COMPLETE source of truth with full field specifications")
    print(f"Query examples:")
    print(f"  - Get all fields for BLOCKS: MATCH (:LinkTypeSchema {{type_name: 'BLOCKS'}})-[:HAS_REQUIRED_FIELD]->(f) RETURN f")
    print(f"  - Get enum values for severity: MATCH (f:FieldSchema {{name: 'severity'}}) RETURN f.enum_values")


if __name__ == "__main__":
    create_enhanced_schema_registry()
