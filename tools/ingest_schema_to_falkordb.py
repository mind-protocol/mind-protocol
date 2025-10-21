"""
Ingest Schema to FalkorDB - Schema Registry Creation

Purpose: Parse UNIFIED_SCHEMA_REFERENCE.md and LINK_TYPE_MECHANISM_MAPPING.md
         to create queryable schema nodes in schema_registry graph.

This makes schema a durable, queryable source of truth that mechanisms
can use to understand how to process different node/link types.

Author: Felix "Ironhand"
Date: 2025-10-17
"""

from falkordb import FalkorDB
import json
from datetime import datetime

# Schema data extracted from UNIFIED_SCHEMA_REFERENCE.md and LINK_TYPE_MECHANISM_MAPPING.md
# This would ideally be parsed from markdown, but starting with explicit definition

LINK_TYPE_SCHEMAS = [
    # Structural Relationships
    {
        "type_name": "BLOCKS",
        "level": "shared",
        "category": "structural",
        "description": "Prevents progress or blocks execution",
        "required_attributes": ["severity", "blocking_condition", "felt_as", "consciousness_impact"],
        "optional_attributes": [],
        "detection_pattern": "coherence_verification",
        "detection_logic": {
            "pattern": "coherence_check",
            "check_condition": "blocking_condition_changed OR severity_outdated"
        },
        "task_template": "Reassess: does {source} still block {target}?",
        "mechanisms": ["coherence_verification", "task_routing"]
    },
    {
        "type_name": "ENABLES",
        "level": "shared",
        "category": "structural",
        "description": "Makes something possible or facilitates it",
        "required_attributes": ["enabling_type", "degree_of_necessity", "felt_as", "without_this"],
        "optional_attributes": [],
        "detection_pattern": "dependency_verification",
        "detection_logic": {
            "pattern": "dependency_check",
            "check_condition": "enabling_node.status == 'invalid' OR enabling_condition_false"
        },
        "task_template": "Check if {target} still enabled by {source}",
        "mechanisms": ["dependency_verification", "task_routing"]
    },
    {
        "type_name": "EXTENDS",
        "level": "shared",
        "category": "structural",
        "description": "Builds upon foundation or extends functionality",
        "required_attributes": ["extension_type", "what_is_added", "maintains_compatibility", "composition_ratio"],
        "optional_attributes": [],
        "detection_pattern": "implementation_verification",
        "detection_logic": {
            "pattern": "implementation_check",
            "check_condition": "base_changed OR extension_changed OR compatibility_test_failed"
        },
        "task_template": "Check compatibility: {source} extends {target}",
        "mechanisms": ["implementation_verification", "task_routing"]
    },
    {
        "type_name": "RELATES_TO",
        "level": "shared",
        "category": "structural",
        "description": "Generic connection when specific type unclear",
        "required_attributes": ["relationship_strength", "needs_refinement", "refinement_candidates"],
        "optional_attributes": [],
        "detection_pattern": "quality_degradation",
        "detection_logic": {
            "pattern": "quality_monitor",
            "check_condition": "link_weight < relevance_threshold OR traversal_count_low",
            "default_threshold": 0.3
        },
        "task_template": "Reassess: {source} <-> {target} still related?",
        "mechanisms": ["quality_degradation", "activation_decay"]
    },

    # Dependency & Requirements
    {
        "type_name": "REQUIRES",
        "level": "shared",
        "category": "dependency",
        "description": "Necessary conditions or prerequisites",
        "required_attributes": ["requirement_criticality", "temporal_relationship", "failure_mode", "verification_method"],
        "optional_attributes": [],
        "detection_pattern": "dependency_verification",
        "detection_logic": {
            "pattern": "dependency_check",
            "check_condition": "required_node.status != 'completed' OR temporal_order_violated"
        },
        "task_template": "Verify requirement: {source} requires {target}",
        "mechanisms": ["dependency_verification", "task_routing"]
    },

    # Evidence & Justification
    {
        "type_name": "JUSTIFIES",
        "level": "shared",
        "category": "evidence",
        "description": "Evidence supporting practice/decision/claim",
        "required_attributes": ["justification_type", "justification_strength", "felt_as", "counter_arguments_exist"],
        "optional_attributes": [],
        "detection_pattern": "evidence_accumulation",
        "detection_logic": {
            "pattern": "evidence_tracker",
            "check_condition": "new_evidence_count > recalculation_threshold OR contradictory_evidence_exists"
        },
        "task_template": "Recalculate confidence for {target} based on evidence",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },
    {
        "type_name": "REFUTES",
        "level": "shared",
        "category": "evidence",
        "description": "Disproves or invalidates claim",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "evidence_accumulation",
        "detection_logic": {
            "pattern": "evidence_tracker",
            "check_condition": "supporting_evidence_emerges"
        },
        "task_template": "Reassess refutation of {target} given new evidence",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },

    # Documentation & Implementation
    {
        "type_name": "DOCUMENTS",
        "level": "shared",
        "category": "documentation",
        "description": "Written record of implementation or decision",
        "required_attributes": [],
        "optional_attributes": ["documentation_type"],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "staleness_threshold",
            "default_threshold": 2592000000,  # 30 days in ms
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.staleness_threshold, 2592000000)"
        },
        "task_template": "Update documentation for {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "DOCUMENTED_BY",
        "level": "shared",
        "category": "documentation",
        "description": "Implementation documented by this artifact",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "staleness_threshold",
            "default_threshold": 2592000000,
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.staleness_threshold, 2592000000)"
        },
        "task_template": "Verify {source} matches {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "SUPERSEDES",
        "level": "shared",
        "category": "documentation",
        "description": "This replaces older version",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "coherence_verification",
        "detection_logic": {
            "pattern": "coherence_check",
            "check_condition": "old_node.status == 'active' AND new_node_exists"
        },
        "task_template": "Ensure {target} properly superseded by {source}",
        "mechanisms": ["coherence_verification", "task_routing"]
    },
    {
        "type_name": "IMPLEMENTS",
        "level": "shared",
        "category": "documentation",
        "description": "Putting pattern or best practice into reality",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "implementation_verification",
        "detection_logic": {
            "pattern": "implementation_check",
            "check_condition": "spec_updated OR implementation_changed OR test_results_changed"
        },
        "task_template": "Verify {source} still follows {target}",
        "mechanisms": ["implementation_verification", "task_routing"]
    },
    {
        "type_name": "CREATES",
        "level": "shared",
        "category": "documentation",
        "description": "Task will produce this artifact when completed",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "dependency_verification",
        "detection_logic": {
            "pattern": "dependency_check",
            "check_condition": "time_since_task_completion > creation_window AND artifact_not_exists"
        },
        "task_template": "Verify {source} created {target} as specified",
        "mechanisms": ["dependency_verification", "task_routing"]
    },

    # Organizational Coordination
    {
        "type_name": "ASSIGNED_TO",
        "level": "shared",
        "category": "organizational",
        "description": "Task ownership or responsibility",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "review_threshold",
            "default_threshold": 604800000,  # 7 days in ms
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.review_threshold, 604800000)"
        },
        "task_template": "Review assignment of {source} to {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "COLLABORATES_WITH",
        "level": "shared",
        "category": "organizational",
        "description": "Working partnership between entities",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "activity_threshold",
            "default_threshold": 1209600000,  # 14 days in ms
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.activity_threshold, 1209600000)"
        },
        "task_template": "Check collaboration status: {source} <-> {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "CONTRIBUTES_TO",
        "level": "shared",
        "category": "organizational",
        "description": "Work supporting larger initiative",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "tracking_window",
            "default_threshold": 1209600000,  # 14 days
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.tracking_window, 1209600000)"
        },
        "task_template": "Update contribution tracking: {source} -> {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "MEASURES",
        "level": "shared",
        "category": "organizational",
        "description": "Quantifies performance or progress",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "staleness_detection",
        "detection_logic": {
            "pattern": "staleness_detection",
            "threshold_field": "freshness_requirement",
            "default_threshold": 86400000,  # 1 day in ms
            "check_condition": "(timestamp() - r.last_modified) > COALESCE(r.freshness_requirement, 86400000)"
        },
        "task_template": "Update metric {source} for {target}",
        "mechanisms": ["staleness_detection", "task_routing"]
    },
    {
        "type_name": "THREATENS",
        "level": "shared",
        "category": "organizational",
        "description": "Danger or risk to goal/project",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "coherence_verification",
        "detection_logic": {
            "pattern": "coherence_check",
            "check_condition": "risk.probability_changed OR threat_mitigated"
        },
        "task_template": "Reassess threat: {source} -> {target}",
        "mechanisms": ["coherence_verification", "task_routing"]
    },

    # Activation & Triggering
    {
        "type_name": "ACTIVATES",
        "level": "n1",
        "category": "activation",
        "description": "Trigger awakens entity coalition",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "activation_verification",
        "detection_logic": {
            "pattern": "activation_tracker",
            "check_condition": "trigger_fired AND target_not_activated"
        },
        "task_template": "Debug: {source} should activate {target} but didn't",
        "mechanisms": ["link_activation_check", "task_routing"]
    },
    {
        "type_name": "TRIGGERED_BY",
        "level": "n1",
        "category": "activation",
        "description": "What caused memory/pattern to activate",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "activation_verification",
        "detection_logic": {
            "pattern": "activation_tracker",
            "check_condition": "memory_activated AND claimed_trigger_not_present"
        },
        "task_template": "Verify: {source} truly triggered by {target}",
        "mechanisms": ["link_activation_check", "task_routing"]
    },
    {
        "type_name": "SUPPRESSES",
        "level": "n1",
        "category": "activation",
        "description": "What blocks entity activation",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "activation_verification",
        "detection_logic": {
            "pattern": "activation_tracker",
            "check_condition": "suppressor_active AND target_still_activated"
        },
        "task_template": "Debug: {source} should suppress {target} but didn't",
        "mechanisms": ["link_activation_check", "task_routing"]
    },

    # Learning & Growth
    {
        "type_name": "LEARNED_FROM",
        "level": "n1",
        "category": "learning",
        "description": "Personal pattern extracted from experience",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "quality_degradation",
        "detection_logic": {
            "pattern": "quality_monitor",
            "check_condition": "pattern_confidence < validity_threshold",
            "default_threshold": 0.5
        },
        "task_template": "Verify: {source} still learned from {target}?",
        "mechanisms": ["pattern_crystallization", "confidence_evolution"]
    },
    {
        "type_name": "DEEPENED_WITH",
        "level": "n1",
        "category": "learning",
        "description": "Relationship growth through experience",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "quality_degradation",
        "detection_logic": {
            "pattern": "quality_monitor",
            "check_condition": "relationship_quality_changed OR time_since_last_deepening > expectation"
        },
        "task_template": "Check relationship quality: {source} via {target}",
        "mechanisms": ["hebbian_reinforcement", "activation_decay"]
    },

    # Value & Direction
    {
        "type_name": "DRIVES_TOWARD",
        "level": "n1",
        "category": "value",
        "description": "Value pushing toward goal",
        "required_attributes": [],
        "optional_attributes": [],
        "detection_pattern": "coherence_verification",
        "detection_logic": {
            "pattern": "coherence_check",
            "check_condition": "goal.status == 'completed' OR value_changed"
        },
        "task_template": "Verify alignment: {source} -> {target}",
        "mechanisms": ["coherence_verification", "energy_propagation"]
    },
]

MECHANISM_SCHEMAS = [
    {
        "mechanism_id": "spreading_activation",
        "mechanism_name": "Spreading Activation",
        "description": "Energy spreads from activated nodes to connected nodes based on link weights and energy",
        "detection_patterns": [],  # Universal, not detection-based
        "applicable_link_types": ["ALL"],  # Applies to all link types
        "tick_frequency_ms": 100,
        "implementation_status": "implemented"
    },
    {
        "mechanism_id": "hebbian_reinforcement",
        "mechanism_name": "Hebbian Reinforcement",
        "description": "Links strengthen when nodes co-activate (fire together, wire together)",
        "detection_patterns": [],
        "applicable_link_types": ["ALL"],
        "tick_frequency_ms": 100,
        "implementation_status": "implemented"
    },
    {
        "mechanism_id": "activation_decay",
        "mechanism_name": "Activation-Based Decay",
        "description": "Links and nodes decay over time if not activated",
        "detection_patterns": ["quality_degradation"],
        "applicable_link_types": ["ALL"],
        "tick_frequency_ms": 100,
        "implementation_status": "implemented"
    },
    {
        "mechanism_id": "staleness_detection",
        "mechanism_name": "Staleness Detection",
        "description": "Detects when entities or links haven't been updated within their freshness window",
        "detection_patterns": ["staleness_detection"],
        "applicable_link_types": ["DOCUMENTS", "DOCUMENTED_BY", "ASSIGNED_TO", "MEASURES", "COLLABORATES_WITH", "CONTRIBUTES_TO"],
        "tick_frequency_ms": 5000,
        "implementation_status": "partial"
    },
    {
        "mechanism_id": "dependency_verification",
        "mechanism_name": "Dependency Verification",
        "description": "Verifies that prerequisites and requirements are met",
        "detection_patterns": ["dependency_verification"],
        "applicable_link_types": ["REQUIRES", "ENABLES", "CREATES"],
        "tick_frequency_ms": 5000,
        "implementation_status": "partial"
    },
    {
        "mechanism_id": "coherence_verification",
        "mechanism_name": "Coherence Verification",
        "description": "Checks logical consistency and detects contradictions",
        "detection_patterns": ["coherence_verification"],
        "applicable_link_types": ["BLOCKS", "SUPERSEDES", "DRIVES_TOWARD", "THREATENS"],
        "tick_frequency_ms": 5000,
        "implementation_status": "partial"
    },
    {
        "mechanism_id": "implementation_verification",
        "mechanism_name": "Implementation Verification",
        "description": "Verifies that implementations match specifications",
        "detection_patterns": ["implementation_verification"],
        "applicable_link_types": ["IMPLEMENTS", "EXTENDS"],
        "tick_frequency_ms": 10000,
        "implementation_status": "not_implemented"
    },
    {
        "mechanism_id": "pattern_crystallization",
        "mechanism_name": "Pattern Crystallization",
        "description": "Forms stable patterns from repeated co-activation, evidence accumulation",
        "detection_patterns": ["evidence_accumulation"],
        "applicable_link_types": ["JUSTIFIES", "REFUTES", "LEARNED_FROM"],
        "tick_frequency_ms": 100,
        "implementation_status": "implemented"
    },
    {
        "mechanism_id": "link_activation_check",
        "mechanism_name": "Link Activation Check",
        "description": "Verifies that activation propagates correctly through links",
        "detection_patterns": ["activation_verification"],
        "applicable_link_types": ["ACTIVATES", "TRIGGERED_BY", "SUPPRESSES"],
        "tick_frequency_ms": 100,
        "implementation_status": "partial"
    },
    {
        "mechanism_id": "energy_propagation",
        "mechanism_name": "Energy Propagation",
        "description": "Spreads energy/urgency through graph for prioritization",
        "detection_patterns": [],
        "applicable_link_types": ["ALL"],
        "tick_frequency_ms": 100,
        "implementation_status": "implemented"
    },
    {
        "mechanism_id": "task_routing",
        "mechanism_name": "Task Routing",
        "description": "Routes created tasks to appropriate citizens/entities",
        "detection_patterns": [],
        "applicable_link_types": ["ALL"],
        "tick_frequency_ms": 1000,
        "implementation_status": "not_implemented"
    },
    {
        "mechanism_id": "confidence_evolution",
        "mechanism_name": "Confidence Evolution",
        "description": "Updates confidence scores based on evidence accumulation",
        "detection_patterns": ["evidence_accumulation"],
        "applicable_link_types": ["JUSTIFIES", "REFUTES"],
        "tick_frequency_ms": 5000,
        "implementation_status": "not_implemented"
    },
]


def create_schema_registry():
    """Create and populate the schema_registry graph in FalkorDB."""

    print("=" * 70)
    print("SCHEMA REGISTRY INGESTION")
    print("=" * 70)

    # Connect to FalkorDB
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph("schema_registry")

    print(f"\n[1/4] Connected to FalkorDB, selected graph: schema_registry")

    # Clear existing schema (fresh start)
    try:
        result = g.query("MATCH (n) DETACH DELETE n")
        print(f"[1/4] Cleared existing schema nodes")
    except Exception as e:
        print(f"[1/4] No existing schema to clear (or error: {e})")

    # Ingest Link Type Schemas
    print(f"\n[2/4] Ingesting {len(LINK_TYPE_SCHEMAS)} Link Type Schemas...")

    for idx, link_schema in enumerate(LINK_TYPE_SCHEMAS, 1):
        try:
            # Convert detection_logic dict to JSON string for storage
            detection_logic_json = json.dumps(link_schema["detection_logic"])

            g.query("""
                CREATE (s:LinkTypeSchema {
                    type_name: $type_name,
                    level: $level,
                    category: $category,
                    description: $description,
                    required_attributes: $required_attributes,
                    optional_attributes: $optional_attributes,
                    detection_pattern: $detection_pattern,
                    detection_logic: $detection_logic,
                    task_template: $task_template,
                    mechanisms: $mechanisms,
                    created_at: $created_at,
                    version: 'v2.0'
                })
            """, params={
                "type_name": link_schema["type_name"],
                "level": link_schema["level"],
                "category": link_schema["category"],
                "description": link_schema["description"],
                "required_attributes": link_schema["required_attributes"],
                "optional_attributes": link_schema["optional_attributes"],
                "detection_pattern": link_schema["detection_pattern"],
                "detection_logic": detection_logic_json,
                "task_template": link_schema["task_template"],
                "mechanisms": link_schema["mechanisms"],
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            print(f"  [{idx}/{len(LINK_TYPE_SCHEMAS)}] OK {link_schema['type_name']:20s} ({link_schema['detection_pattern']})")

        except Exception as e:
            print(f"  [{idx}/{len(LINK_TYPE_SCHEMAS)}] FAIL {link_schema['type_name']:20s} ERROR: {e}")

    # Ingest Mechanism Schemas
    print(f"\n[3/4] Ingesting {len(MECHANISM_SCHEMAS)} Mechanism Schemas...")

    for idx, mech_schema in enumerate(MECHANISM_SCHEMAS, 1):
        try:
            g.query("""
                CREATE (m:MechanismSchema {
                    mechanism_id: $mechanism_id,
                    mechanism_name: $mechanism_name,
                    description: $description,
                    detection_patterns: $detection_patterns,
                    applicable_link_types: $applicable_link_types,
                    tick_frequency_ms: $tick_frequency_ms,
                    implementation_status: $implementation_status,
                    created_at: $created_at,
                    version: 'v2.0'
                })
            """, params={
                "mechanism_id": mech_schema["mechanism_id"],
                "mechanism_name": mech_schema["mechanism_name"],
                "description": mech_schema["description"],
                "detection_patterns": mech_schema["detection_patterns"],
                "applicable_link_types": mech_schema["applicable_link_types"],
                "tick_frequency_ms": mech_schema["tick_frequency_ms"],
                "implementation_status": mech_schema["implementation_status"],
                "created_at": int(datetime.now().timestamp() * 1000)
            })

            status_icon = "OK" if mech_schema["implementation_status"] == "implemented" else "PARTIAL"
            print(f"  [{idx}/{len(MECHANISM_SCHEMAS)}] {status_icon} {mech_schema['mechanism_id']:30s} ({mech_schema['implementation_status']})")

        except Exception as e:
            print(f"  [{idx}/{len(MECHANISM_SCHEMAS)}] FAIL {mech_schema['mechanism_id']:30s} ERROR: {e}")

    # Verify ingestion
    print(f"\n[4/4] Verifying schema registry...")

    link_count = g.query("MATCH (s:LinkTypeSchema) RETURN count(s) as count").result_set[0][0]
    mech_count = g.query("MATCH (m:MechanismSchema) RETURN count(m) as count").result_set[0][0]

    print(f"  - LinkTypeSchema nodes: {link_count}")
    print(f"  - MechanismSchema nodes: {mech_count}")

    # Show sample query
    print(f"\n[SAMPLE QUERY] Link types using staleness_detection:")
    result = g.query("""
        MATCH (s:LinkTypeSchema)
        WHERE s.detection_pattern = 'staleness_detection'
        RETURN s.type_name as link_type, s.task_template as template
        ORDER BY s.type_name
    """)

    for row in result.result_set:
        print(f"  - {row[0]:20s} -> {row[1]}")

    print(f"\n" + "=" * 70)
    print("SCHEMA REGISTRY CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nSchema is now queryable from consciousness_engine.py:")
    print(f"  Graph: schema_registry")
    print(f"  Nodes: LinkTypeSchema, MechanismSchema")
    print(f"\nNext: Update consciousness_engine.py to query schema instead of hardcoded logic")


if __name__ == "__main__":
    create_schema_registry()
