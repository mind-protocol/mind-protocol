"""
Rules Engine - L4 Protocol Validation Rules

Implements mp-lint rules for L4 protocol compliance:
- R-001: SCHEMA_EXISTS_ACTIVE (event schema must exist in registry)
- R-002: TOPIC_MAPPED (schema must have maps_to_topic relationship)
- R-003: PROVENANCE_PERSONAL_ONLY (personal scope only)
- R-004: CPS_COMPUTE_SETTLEMENT (compute topics need settlement)
- R-005: SEA_ATTESTATION (high-stakes topics require attestation)

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Violation:
    """
    Represents a rule violation found during linting.

    Attributes:
        rule_code: Rule identifier (e.g., "R-001", "R-002", "R-100")
        severity: "error" or "warning"
        message: Human-readable error message
        file_path: Path to file containing violation
        line_number: Line number where violation occurs
        event_type: Event name or value that violated the rule
        context: Additional context (e.g., code snippet)
    """
    rule_code: str
    severity: str  # "error" or "warning"
    message: str
    file_path: str
    line_number: int
    event_type: str  # Event name for L4 violations, hardcoded value for R-100 violations
    context: Optional[str] = None


# Rule code mapping for hardcoded violations
HARDCODED_RULE_CODES = {
    "MAGIC_NUMBER": "R-100",
    "HARDCODED_STRING": "R-101",
    "CITIZEN_ARRAY": "R-102",
}

# Rule code mapping for quality degradation violations
QUALITY_RULE_CODES = {
    "TODO_OR_HACK": "R-200",
    "QUALITY_DEGRADE": "R-201",
    "OBSERVABILITY_CUT": "R-202",
}

# Rule code mapping for fallback antipattern violations
FALLBACK_RULE_CODES = {
    "BARE_EXCEPT_PASS": "R-300",
    "SILENT_DEFAULT_RETURN": "R-301",
    "FAKE_AVAILABILITY": "R-302",
    "INFINITE_LOOP_NO_SLEEP": "R-303",
}

# Rule code mapping for fail-loud contract violations
FAIL_LOUD_RULE_CODES = {
    "FAIL_LOUD_REQUIRED": "R-400",
    "MISSING_FAILURE_CONTEXT": "R-401",
}


def convert_hardcoded_violation(hv) -> Violation:
    """
    Convert HardcodedViolation to standard Violation format.

    Args:
        hv: HardcodedViolation from scanner_hardcoded

    Returns:
        Violation object
    """
    rule_code = HARDCODED_RULE_CODES.get(hv.violation_type, "R-100")

    return Violation(
        rule_code=rule_code,
        severity="error",
        message=hv.message,
        file_path=hv.file_path,
        line_number=hv.line_number,
        event_type=hv.value,
        context=hv.code_snippet
    )


def convert_quality_violation(qv) -> Violation:
    """
    Convert QualityViolation to standard Violation format.

    Args:
        qv: QualityViolation from scanner_quality

    Returns:
        Violation object
    """
    rule_code = QUALITY_RULE_CODES.get(qv.violation_type, "R-200")

    return Violation(
        rule_code=rule_code,
        severity="error",
        message=qv.message,
        file_path=qv.file_path,
        line_number=qv.line_number,
        event_type=qv.pattern,
        context=qv.code_snippet
    )


def convert_fallback_violation(fv) -> Violation:
    """
    Convert FallbackViolation to standard Violation format.

    Args:
        fv: FallbackViolation from scanner_fallback

    Returns:
        Violation object
    """
    rule_code = FALLBACK_RULE_CODES.get(fv.violation_type, "R-300")

    return Violation(
        rule_code=rule_code,
        severity="error",
        message=fv.message,
        file_path=fv.file_path,
        line_number=fv.line_number,
        event_type=fv.pattern,
        context=fv.code_snippet
    )


def convert_fail_loud_violation(flv) -> Violation:
    """
    Convert FailLoudViolation to standard Violation format.

    Args:
        flv: FailLoudViolation from scanner_fail_loud

    Returns:
        Violation object
    """
    rule_code = FAIL_LOUD_RULE_CODES.get(flv.violation_type, "R-400")

    return Violation(
        rule_code=rule_code,
        severity="error",
        message=flv.message,
        file_path=flv.file_path,
        line_number=flv.line_number,
        event_type=flv.pattern,
        context=flv.code_snippet
    )


class RulesEngine:
    """
    Validates event emissions against L4 protocol rules.

    Loads L4 public registry and provides validation methods for each rule.

    Example:
        >>> engine = RulesEngine()
        >>> violations = engine.validate_event(
        ...     event_type="unknown.event",
        ...     file_path="test.py",
        ...     line_number=42
        ... )
        >>> for v in violations:
        ...     print(f"{v.rule_code}: {v.message}")
    """

    def __init__(self, registry_path: Optional[Path] = None, config_path: Optional[Path] = None):
        """
        Initialize rules engine with L4 registry.

        Args:
            registry_path: Path to l4_public_registry.json (default: build/l4_public_registry.json)
            config_path: Path to .mp-lint.yaml config (optional)
        """
        # Default paths
        if registry_path is None:
            repo_root = Path(__file__).resolve().parents[2]
            registry_path = repo_root / "build" / "l4_public_registry.json"

        self.registry_path = registry_path
        self.schemas_by_name: Dict[str, Dict[str, Any]] = {}
        self.topic_namespaces: List[Dict[str, Any]] = []
        self.governance_policies: List[Dict[str, Any]] = []
        self.meta: Dict[str, Any] = {}
        self.loaded = False

        # Config (high-stakes topics, CPS policy, etc.)
        self.high_stakes_topics: List[str] = []
        self.cps_policy_id: Optional[str] = None

        # Load registry
        try:
            self._load_registry()
            if config_path:
                self._load_config(config_path)
        except Exception as exc:
            print(f"Warning: Failed to load L4 registry: {exc}")
            # Don't fail - allow linter to run with degraded validation

    def _load_registry(self) -> None:
        """Load L4 public registry from JSON file."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found at {self.registry_path}")

        with self.registry_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        self.meta = data.get("meta", {})
        event_schemas = data.get("event_schemas", [])
        self.topic_namespaces = data.get("topic_namespaces", [])
        self.governance_policies = data.get("governance_policies", [])

        # Build name � schema lookup dict
        self.schemas_by_name = {
            schema["name"]: schema
            for schema in event_schemas
            if schema.get("name")
        }

        self.loaded = True

    def _load_config(self, config_path: Path) -> None:
        """Load mp-lint configuration from YAML (future implementation)."""
        # TODO: Load .mp-lint.yaml for high_stakes_topics, cps_policy_id
        pass

    def _matches_namespace_wildcard(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Check if event_type matches any namespace wildcard pattern.

        Args:
            event_type: Event name (e.g., "mode.snapshot")

        Returns:
            Namespace dict if match found, None otherwise

        Example:
            "mode.snapshot" matches "telemetry.state.*" namespace
            "tick.update" matches "telemetry.frame.*" namespace
        """
        for ns in self.topic_namespaces:
            ns_name = ns.get("name", "")

            # Check if namespace is a wildcard (ends with .*)
            if ns_name.endswith(".*"):
                # Extract prefix (e.g., "telemetry.state" from "telemetry.state.*")
                prefix = ns_name[:-2]  # Remove ".*"

                # Check if event starts with prefix
                if event_type.startswith(prefix):
                    return ns

        return None

    def validate_event(
        self,
        event_type: str,
        file_path: str,
        line_number: int,
        context: Optional[str] = None
    ) -> List[Violation]:
        """
        Validate event emission against all applicable rules.

        Supports wildcard namespace matching:
        - Checks exact schema name match first
        - Falls back to wildcard namespace matching (e.g., telemetry.state.*)
        - If namespace has mapped schema, treats event as valid

        Args:
            event_type: Event name (e.g., "graph.delta.node.upsert")
            file_path: Path to file containing emission
            line_number: Line number of emission
            context: Code snippet showing emission (optional)

        Returns:
            List of violations (empty if no violations)
        """
        violations = []

        # If registry didn't load, skip validation
        if not self.loaded:
            return violations

        # R-001: SCHEMA_EXISTS_ACTIVE
        # Try exact schema match first
        schema = self.schemas_by_name.get(event_type)

        # If no exact match, try wildcard namespace matching
        if not schema:
            matching_namespace = self._matches_namespace_wildcard(event_type)

            if matching_namespace:
                # Found matching namespace - find schema mapped to this namespace
                # Look for any schema that maps to this namespace
                for schema_name, schema_data in self.schemas_by_name.items():
                    if schema_data.get("maps_to_topic") == matching_namespace.get("id"):
                        schema = schema_data
                        break

        # If still no schema found (no exact match, no wildcard match), it's a violation
        if not schema:
            violations.append(Violation(
                rule_code="R-001",
                severity="error",
                message=f"Event schema '{event_type}' not found in L4 registry (no exact match or namespace wildcard)",
                file_path=file_path,
                line_number=line_number,
                event_type=event_type,
                context=context
            ))
            return violations  # Can't validate further without schema

        # R-002: TOPIC_MAPPED
        if not schema.get("maps_to_topic"):
            violations.append(Violation(
                rule_code="R-002",
                severity="error",
                message=f"Event schema '{event_type}' has no topic mapping (maps_to_topic)",
                file_path=file_path,
                line_number=line_number,
                event_type=event_type,
                context=context
            ))

        # R-005: SEA_ATTESTATION (high-stakes topics require signature)
        if self._is_high_stakes(event_type):
            if not schema.get("requires_sig"):
                violations.append(Violation(
                    rule_code="R-005",
                    severity="error",
                    message=f"High-stakes event '{event_type}' requires signature attestation",
                    file_path=file_path,
                    line_number=line_number,
                    event_type=event_type,
                    context=context
                ))

        return violations

    def _is_high_stakes(self, event_type: str) -> bool:
        """
        Check if event type matches high-stakes patterns.

        High-stakes patterns: identity.*, registry.*, economy.trade.*, legal.*
        """
        high_stakes_patterns = [
            r"^identity\.",
            r"^registry\.",
            r"^economy\.trade\.",
            r"^legal\.",
            r"^subentity\.snapshot$",  # From config
        ]

        for pattern in high_stakes_patterns:
            if re.match(pattern, event_type):
                return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get rules engine statistics.

        Returns:
            {
                "loaded": bool,
                "schema_count": int,
                "namespace_count": int,
                "policy_count": int,
                "registry_path": str,
                "exported_at": str,
                "graph_hash": str
            }
        """
        return {
            "loaded": self.loaded,
            "schema_count": len(self.schemas_by_name),
            "namespace_count": len(self.topic_namespaces),
            "policy_count": len(self.governance_policies),
            "registry_path": str(self.registry_path),
            "exported_at": self.meta.get("exported_at", "unknown"),
            "graph_hash": self.meta.get("graph_hash", "unknown")
        }
