"""
Membrane Lint Rules - L4 Protocol Enforcement

Lint rules that validate code/schemas/data against L4 registry.

Each rule:
- Takes registry + target data
- Returns (passed: bool, violations: List[str])

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

from typing import Dict, List, Tuple, Any
from falkordb import FalkorDB


def lint_label_property_coherence(db: FalkorDB, graph_name: str) -> Tuple[bool, List[str]]:
    """
    Rule: type_name property must match primary U3_/U4_ label

    Query: Find nodes where type_name doesn't match label
    """
    violations = []

    g = db.select_graph(graph_name)

    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
        WITH n, head([label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_']) as primary_label
        WHERE n.type_name <> primary_label OR n.type_name IS NULL
        RETURN n.name as name, n.type_name as type_name, primary_label, labels(n) as all_labels
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0]
        type_name = record[1]
        expected = record[2]
        all_labels = record[3]
        violations.append(
            f"Node '{name}': type_name='{type_name}' doesn't match label '{expected}' (labels: {all_labels})"
        )

    return (len(violations) == 0, violations)


def lint_universality_level_coherence(db: FalkorDB, graph_name: str) -> Tuple[bool, List[str]]:
    """
    Rule: U3 types must have level ∈ {L1,L2,L3}, U4 types must have level ∈ {L1,L2,L3,L4}

    Query: Find nodes violating level bounds
    """
    violations = []

    g = db.select_graph(graph_name)

    # Check U3 types
    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_')
        AND NOT (n.level = 'L1' OR n.level = 'L2' OR n.level = 'L3')
        RETURN n.name as name, n.type_name as type_name, n.level as level
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0]
        type_name = record[1]
        level = record[2]
        violations.append(
            f"U3 node '{name}' ({type_name}) has invalid level '{level}' (must be L1/L2/L3)"
        )

    # Check U4 types
    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U4_')
        AND NOT (n.level = 'L1' OR n.level = 'L2' OR n.level = 'L3' OR n.level = 'L4')
        RETURN n.name as name, n.type_name as type_name, n.level as level
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0]
        type_name = record[1]
        level = record[2]
        violations.append(
            f"U4 node '{name}' ({type_name}) has invalid level '{level}' (must be L1/L2/L3/L4)"
        )

    return (len(violations) == 0, violations)


def lint_no_double_labels(db: FalkorDB, graph_name: str) -> Tuple[bool, List[str]]:
    """
    Rule: Nodes should have exactly one U3_/U4_ label, not multiple

    Query: Find nodes with multiple universal labels
    """
    violations = []

    g = db.select_graph(graph_name)

    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
        WITH n, [label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_'] as u_labels
        WHERE size(u_labels) > 1
        RETURN n.name as name, labels(n) as all_labels
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0]
        all_labels = record[1]
        violations.append(
            f"Node '{name}' has multiple U3_/U4_ labels: {all_labels}"
        )

    return (len(violations) == 0, violations)


def lint_schema_code_drift(registry: Dict[str, Any], code_schemas: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Rule: Code schemas (complete_schema_data.py) must match L4 registry

    Checks:
    - Same set of universal types
    - No extra types in code
    - No missing types from registry
    """
    violations = []

    # Build sets
    registry_types = {t["type_name"] for t in registry["node_types"]}
    code_types = set(code_schemas.keys())

    # Find mismatches
    extra_in_code = code_types - registry_types
    missing_from_code = registry_types - code_types

    if extra_in_code:
        violations.append(
            f"Types in code but not in L4 registry: {sorted(extra_in_code)}"
        )

    if missing_from_code:
        violations.append(
            f"Types in L4 registry but not in code: {sorted(missing_from_code)}"
        )

    return (len(violations) == 0, violations)


# Registry invariants (for when L4 registry is actually implemented)

def lint_event_schema_topic_mapping(db: FalkorDB) -> Tuple[bool, List[str]]:
    """
    Rule: Every U4_Event_Schema must have exactly one U4_MAPS_TO_TOPIC edge

    This will be used once schema registry is in L4.
    """
    # TODO: Implement when L4 registry nodes exist
    return (True, [])


def lint_envelope_signature_requirements(db: FalkorDB) -> Tuple[bool, List[str]]:
    """
    Rule: Every U4_Envelope_Schema must have at least one U4_REQUIRES_SIG edge

    This will be used once schema registry is in L4.
    """
    # TODO: Implement when L4 registry nodes exist
    return (True, [])


def lint_active_bundle_reachability(db: FalkorDB) -> Tuple[bool, List[str]]:
    """
    Rule: All active schema bundles must be reachable from registry root via GOVERNS

    This will be used once schema registry is in L4.
    """
    # TODO: Implement when L4 registry nodes exist
    return (True, [])
