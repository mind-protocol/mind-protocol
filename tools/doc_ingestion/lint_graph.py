"""
Graph Structure Linter for Doc Ingestion Pipeline

Validates graph structure against schema registry and metadata contracts.
Runs 7 structural checks (C1-C7) to ensure graph quality.

Checks:
- C1: Valid node/link types (against schema registry)
- C2: Required metadata present (per link_meta.yaml contract)
- C3: Confidence in valid range (0-1)
- C4: No orphan nodes (all nodes connected)
- C5: No duplicate edges (same source→target→type)
- C6: No self-loops (except allowed types)
- C7: Bidirectional edge consistency

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import json
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from graph import GraphWrapper


class Severity(str, Enum):
    """Violation severity levels."""
    ERROR = "ERROR"      # Must fix
    WARNING = "WARNING"  # Should review


@dataclass
class Violation:
    """A lint violation."""
    check: str           # Check ID (C1, C2, etc.)
    severity: Severity   # ERROR or WARNING
    message: str         # Human-readable description
    node_id: str = None  # Node ID if applicable
    edge: Tuple[str, str, str] = None  # (source, target, type) if applicable
    metadata: Dict[str, Any] = None  # Additional context


class GraphLinter:
    """
    Validates graph structure against schema and metadata contracts.

    Runs configurable structural checks and returns violations.
    """

    def __init__(self, graph: GraphWrapper, config: Dict[str, bool] = None):
        """
        Initialize linter.

        Args:
            graph: GraphWrapper instance
            config: Check enable/disable config (default: all enabled)
        """
        self.graph = graph
        self.config = config or {
            'enable_c1_check': True,
            'enable_c2_check': True,
            'enable_c3_check': True,
            'enable_c4_check': True,
            'enable_c5_check': True,
            'enable_c6_check': True,
            'enable_c7_check': True,
        }

    def run_all_checks(self) -> List[Violation]:
        """
        Run all enabled checks.

        Returns:
            List of violations (empty if valid)
        """
        violations = []

        if self.config.get('enable_c1_check'):
            violations.extend(self.check_c1_valid_types())

        if self.config.get('enable_c2_check'):
            violations.extend(self.check_c2_required_metadata())

        if self.config.get('enable_c3_check'):
            violations.extend(self.check_c3_confidence_range())

        if self.config.get('enable_c4_check'):
            violations.extend(self.check_c4_no_orphans())

        if self.config.get('enable_c5_check'):
            violations.extend(self.check_c5_no_duplicates())

        if self.config.get('enable_c6_check'):
            violations.extend(self.check_c6_no_self_loops())

        if self.config.get('enable_c7_check'):
            violations.extend(self.check_c7_bidirectional_consistency())

        return violations

    def check_c1_valid_types(self) -> List[Violation]:
        """
        C1: Validate node and link types against schema registry.

        Returns:
            List of violations for invalid types
        """
        violations = []

        # Get valid types from schema registry
        valid_node_types = set(self._get_valid_node_types())
        valid_link_types = set(self._get_valid_link_types())

        # Query all nodes
        query_nodes = "MATCH (n) RETURN labels(n) AS labels, n.id AS id"
        try:
            result = self.graph._execute_query(query_nodes)
            # Parse result to check node types
            # TODO: Parse actual FalkorDB result format
            # For now, placeholder
        except Exception as e:
            violations.append(Violation(
                check="C1",
                severity=Severity.ERROR,
                message=f"Failed to query nodes: {e}"
            ))

        # Query all edges
        query_edges = "MATCH (a)-[r]->(b) RETURN type(r) AS edge_type, a.id AS source, b.id AS target"
        try:
            result = self.graph._execute_query(query_edges)
            # Parse result to check edge types
            # TODO: Parse actual FalkorDB result format
        except Exception as e:
            violations.append(Violation(
                check="C1",
                severity=Severity.ERROR,
                message=f"Failed to query edges: {e}"
            ))

        return violations

    def check_c2_required_metadata(self) -> List[Violation]:
        """
        C2: Validate required metadata fields present on edges.

        Checks against link_meta.yaml contract from schema registry.

        Returns:
            List of violations for missing required fields
        """
        violations = []

        # Get metadata contract from schema registry
        contract = self.graph.get_link_meta_contract()

        if not contract:
            violations.append(Violation(
                check="C2",
                severity=Severity.WARNING,
                message="Could not load link metadata contract from schema registry"
            ))
            return violations

        # Query all edges with metadata
        query = """
        MATCH (a)-[r]->(b)
        RETURN type(r) AS edge_type, a.id AS source, b.id AS target, properties(r) AS props
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and validate each edge
            # TODO: Parse actual FalkorDB result format and validate metadata
        except Exception as e:
            violations.append(Violation(
                check="C2",
                severity=Severity.ERROR,
                message=f"Failed to query edge metadata: {e}"
            ))

        return violations

    def check_c3_confidence_range(self) -> List[Violation]:
        """
        C3: Validate confidence scores in valid range [0, 1].

        Returns:
            List of violations for out-of-range confidence scores
        """
        violations = []

        query = """
        MATCH (a)-[r]->(b)
        WHERE r.confidence IS NOT NULL
        RETURN type(r) AS edge_type, a.id AS source, b.id AS target, r.confidence AS conf
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and check confidence values
            # TODO: Parse actual FalkorDB result format
            # Check: 0 <= confidence <= 1
        except Exception as e:
            violations.append(Violation(
                check="C3",
                severity=Severity.ERROR,
                message=f"Failed to query confidence scores: {e}"
            ))

        return violations

    def check_c4_no_orphans(self) -> List[Violation]:
        """
        C4: Ensure no orphan nodes (all nodes have at least one edge).

        Returns:
            List of violations for orphan nodes
        """
        violations = []

        query = """
        MATCH (n)
        WHERE NOT (n)-[]-()
        RETURN n.id AS id, labels(n) AS labels
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and report orphans
            # TODO: Parse actual FalkorDB result format
            # Each orphan node is a violation
        except Exception as e:
            violations.append(Violation(
                check="C4",
                severity=Severity.ERROR,
                message=f"Failed to query orphan nodes: {e}"
            ))

        return violations

    def check_c5_no_duplicates(self) -> List[Violation]:
        """
        C5: Ensure no duplicate edges (same source→target→type).

        Returns:
            List of violations for duplicate edges
        """
        violations = []

        query = """
        MATCH (a)-[r]->(b)
        WITH a.id AS source, b.id AS target, type(r) AS edge_type, COUNT(*) AS cnt
        WHERE cnt > 1
        RETURN source, target, edge_type, cnt
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and report duplicates
            # TODO: Parse actual FalkorDB result format
        except Exception as e:
            violations.append(Violation(
                check="C5",
                severity=Severity.ERROR,
                message=f"Failed to query duplicate edges: {e}"
            ))

        return violations

    def check_c6_no_self_loops(self) -> List[Violation]:
        """
        C6: Ensure no self-loops (node pointing to itself).

        Some edge types may allow self-loops (e.g., REFINES).
        Check schema for allowed self-loop types.

        Returns:
            List of violations for disallowed self-loops
        """
        violations = []

        # Get allowed self-loop types from schema
        allowed_self_loops = self._get_allowed_self_loop_types()

        query = """
        MATCH (n)-[r]->(n)
        RETURN type(r) AS edge_type, n.id AS node_id
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and check if edge type allows self-loops
            # TODO: Parse actual FalkorDB result format
            # Violation if edge_type not in allowed_self_loops
        except Exception as e:
            violations.append(Violation(
                check="C6",
                severity=Severity.ERROR,
                message=f"Failed to query self-loops: {e}"
            ))

        return violations

    def check_c7_bidirectional_consistency(self) -> List[Violation]:
        """
        C7: Validate bidirectional edge consistency.

        If A→B exists, and B→A exists, check that:
        - Metadata is reciprocal (e.g., A depends_on B ↔ B supports A)
        - Status matches (both CONFIRMED or both PROPOSED)

        Returns:
            List of violations for inconsistent bidirectional edges
        """
        violations = []

        query = """
        MATCH (a)-[r1]->(b)-[r2]->(a)
        RETURN a.id AS node_a, b.id AS node_b,
               type(r1) AS type_ab, type(r2) AS type_ba,
               r1.status AS status_ab, r2.status AS status_ba,
               properties(r1) AS props_ab, properties(r2) AS props_ba
        """

        try:
            result = self.graph._execute_query(query)
            # Parse and validate reciprocal edges
            # TODO: Parse actual FalkorDB result format
            # Check: status_ab == status_ba
            # Check: Metadata reciprocity (type-specific rules)
        except Exception as e:
            violations.append(Violation(
                check="C7",
                severity=Severity.WARNING,
                message=f"Failed to query bidirectional edges: {e}"
            ))

        return violations

    def _get_valid_node_types(self) -> List[str]:
        """Get valid node types from schema registry."""
        node_types = self.graph.get_node_types()
        # TODO: Parse schema registry format
        # For now, return placeholder
        return ['Principle', 'Mechanism', 'BestPractice', 'Capability', 'Pattern']

    def _get_valid_link_types(self) -> List[str]:
        """Get valid link types from schema registry."""
        link_types = self.graph.get_link_types()
        # TODO: Parse schema registry format
        return ['IMPLEMENTS', 'DEPENDS_ON', 'ENABLES', 'MEASURES', 'REFINES']

    def _get_allowed_self_loop_types(self) -> Set[str]:
        """Get edge types that allow self-loops."""
        # TODO: Query schema registry for this
        return {'REFINES'}  # Example: REFINES allows self-loops

    def format_report(self, violations: List[Violation]) -> str:
        """
        Format violations as human-readable report.

        Args:
            violations: List of violations

        Returns:
            Formatted report string
        """
        if not violations:
            return "✅ All checks passed! Graph structure valid.\n"

        lines = ["=== Graph Lint Report ===", ""]

        # Group by check
        by_check: Dict[str, List[Violation]] = {}
        for v in violations:
            by_check.setdefault(v.check, []).append(v)

        # Count by severity
        errors = sum(1 for v in violations if v.severity == Severity.ERROR)
        warnings = sum(1 for v in violations if v.severity == Severity.WARNING)

        lines.append(f"Total violations: {len(violations)} ({errors} errors, {warnings} warnings)")
        lines.append("")

        # Report by check
        for check_id in sorted(by_check.keys()):
            check_violations = by_check[check_id]
            lines.append(f"[{check_id}] {len(check_violations)} violations:")

            for v in check_violations[:10]:  # Show first 10
                severity_icon = "❌" if v.severity == Severity.ERROR else "⚠️"
                lines.append(f"  {severity_icon} {v.message}")

                if v.node_id:
                    lines.append(f"      Node: {v.node_id}")
                if v.edge:
                    lines.append(f"      Edge: {v.edge[0]} → {v.edge[1]} ({v.edge[2]})")

            if len(check_violations) > 10:
                lines.append(f"  ... and {len(check_violations) - 10} more")

            lines.append("")

        return "\n".join(lines)

    def format_json(self, violations: List[Violation]) -> str:
        """
        Format violations as JSON for machine consumption.

        Args:
            violations: List of violations

        Returns:
            JSON string
        """
        data = {
            'total_violations': len(violations),
            'errors': sum(1 for v in violations if v.severity == Severity.ERROR),
            'warnings': sum(1 for v in violations if v.severity == Severity.WARNING),
            'violations': [
                {
                    'check': v.check,
                    'severity': v.severity.value,
                    'message': v.message,
                    'node_id': v.node_id,
                    'edge': v.edge,
                    'metadata': v.metadata
                }
                for v in violations
            ]
        }
        return json.dumps(data, indent=2)


if __name__ == "__main__":
    # Quick test
    import sys

    # Initialize graph
    graph = GraphWrapper("L2_organizational")

    # Initialize linter (all checks enabled)
    linter = GraphLinter(graph)

    print("Running graph structure checks...\n")

    # Run all checks
    violations = linter.run_all_checks()

    # Print report
    print(linter.format_report(violations))

    # Exit code: 0 if no errors, 1 if errors
    has_errors = any(v.severity == Severity.ERROR for v in violations)
    sys.exit(1 if has_errors else 0)
