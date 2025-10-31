"""
Schema Registry - Runtime Event Validation

Loads L4 public registry (exported from FalkorDB protocol graph) and provides
fast schema lookups for runtime validation in SafeBroadcaster.

Architecture:
- Load build/l4_public_registry.json at startup
- Cache schemas in memory (dict lookup by event name)
- Validate events against schema before emission
- Report violations for mp-lint compliance

Integration:
    from orchestration.libs.schema_registry import SchemaRegistry, ValidationResult

    registry = SchemaRegistry()
    result = registry.validate_event("presence.beacon", {"citizen_id": "ada", ...})

    if not result.valid:
        print(f"Validation failed: {result.error} (rule: {result.rule_code})")

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
Architecture: mp-lint infrastructure (runtime validation layer)
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of event schema validation.

    Attributes:
        valid: True if event passes validation, False otherwise
        rule_code: mp-lint rule code (e.g., "R-001", "R-002") if validation failed
        error: Human-readable error message if validation failed
        schema: Matched Event_Schema dict if found, None otherwise
    """
    valid: bool
    rule_code: Optional[str] = None
    error: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None


class SchemaRegistry:
    """
    In-memory cache of L4 event schemas for runtime validation.

    Loads build/l4_public_registry.json and provides fast lookups by event name.

    Example:
        >>> registry = SchemaRegistry()
        >>> result = registry.validate_event("presence.beacon", {...})
        >>> if result.valid:
        ...     print("Event is valid")
        ... else:
        ...     print(f"Validation failed: {result.error}")
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize schema registry.

        Args:
            registry_path: Path to l4_public_registry.json (default: build/l4_public_registry.json)
        """
        # Default path relative to repo root
        if registry_path is None:
            repo_root = Path(__file__).resolve().parents[2]
            registry_path = repo_root / "build" / "l4_public_registry.json"

        self.registry_path = registry_path
        self.schemas_by_name: Dict[str, Dict[str, Any]] = {}
        self.topic_namespaces: List[Dict[str, Any]] = []
        self.governance_policies: List[Dict[str, Any]] = []
        self.meta: Dict[str, Any] = {}
        self.loaded = False

        # Attempt to load registry
        try:
            self._load_registry()
        except Exception as exc:
            logger.warning(f"[SchemaRegistry] Failed to load registry: {exc}")
            # Don't fail initialization - allow graceful degradation
            # SafeBroadcaster can still function without validation

    def _load_registry(self) -> None:
        """
        Load L4 public registry from JSON file.

        Raises:
            FileNotFoundError: If registry file doesn't exist
            json.JSONDecodeError: If registry file is malformed
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found at {self.registry_path}")

        with self.registry_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        self.meta = data.get("meta", {})
        event_schemas = data.get("event_schemas", [])
        self.topic_namespaces = data.get("topic_namespaces", [])
        self.governance_policies = data.get("governance_policies", [])

        # Build name → schema lookup dict
        self.schemas_by_name = {
            schema["name"]: schema
            for schema in event_schemas
            if schema.get("name")
        }

        self.loaded = True

        logger.info(
            f"[SchemaRegistry] Loaded registry from {self.registry_path} "
            f"({len(self.schemas_by_name)} schemas, "
            f"exported_at={self.meta.get('exported_at', 'unknown')})"
        )

    def get_schema(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Get Event_Schema for the given event type.

        Args:
            event_type: Event name (e.g., "presence.beacon")

        Returns:
            Event_Schema dict if found, None otherwise

        Example:
            >>> schema = registry.get_schema("presence.beacon")
            >>> if schema:
            ...     print(schema["direction"])  # "broadcast"
            ...     print(schema["topic_pattern"])  # "ecosystem/{ecosystem_id}/..."
        """
        if not self.loaded:
            return None

        return self.schemas_by_name.get(event_type)

    def validate_event(self, event_type: str, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate event against L4 schema registry.

        Checks:
        - R-001: Event schema exists in registry
        - R-002: Event schema has topic mapping (maps_to_topic)

        Args:
            event_type: Event name (e.g., "presence.beacon")
            data: Event data dict (payload)

        Returns:
            ValidationResult with valid=True if passes, valid=False with error details otherwise

        Example:
            >>> result = registry.validate_event("presence.beacon", {...})
            >>> if not result.valid:
            ...     print(f"{result.rule_code}: {result.error}")
        """
        # If registry didn't load, allow events through (graceful degradation)
        if not self.loaded:
            return ValidationResult(
                valid=True,
                rule_code=None,
                error=None,
                schema=None
            )

        # R-001: SCHEMA_EXISTS_ACTIVE
        schema = self.get_schema(event_type)
        if not schema:
            return ValidationResult(
                valid=False,
                rule_code="R-001",
                error=f"Event schema '{event_type}' not found in L4 registry",
                schema=None
            )

        # R-002: TOPIC_MAPPED
        if not schema.get("maps_to_topic"):
            return ValidationResult(
                valid=False,
                rule_code="R-002",
                error=f"Event schema '{event_type}' has no topic mapping (maps_to_topic)",
                schema=schema
            )

        # Validation passed
        return ValidationResult(
            valid=True,
            rule_code=None,
            error=None,
            schema=schema
        )

    def validate_event_basic(self, event_type: str) -> ValidationResult:
        """
        Quick validation without payload inspection (R-001 and R-002 only).

        Faster than validate_event() since it doesn't inspect payload data.

        Args:
            event_type: Event name (e.g., "presence.beacon")

        Returns:
            ValidationResult with valid=True if schema exists and has topic mapping
        """
        return self.validate_event(event_type, {})

    def get_stats(self) -> Dict[str, Any]:
        """
        Get schema registry statistics.

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

    def reload(self) -> bool:
        """
        Reload registry from disk (useful if export was updated).

        Returns:
            True if reload succeeded, False otherwise
        """
        try:
            self._load_registry()
            logger.info("[SchemaRegistry] Registry reloaded successfully")
            return True
        except Exception as exc:
            logger.error(f"[SchemaRegistry] Reload failed: {exc}")
            return False


# ------------------------------------------------------------------ Singleton Instance

# Global singleton instance for use across the system
_global_registry: Optional[SchemaRegistry] = None


def get_schema_registry() -> SchemaRegistry:
    """
    Get global SchemaRegistry singleton.

    Lazily initializes on first call.

    Returns:
        Global SchemaRegistry instance

    Example:
        >>> from orchestration.libs.schema_registry import get_schema_registry
        >>> registry = get_schema_registry()
        >>> result = registry.validate_event("presence.beacon", {...})
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = SchemaRegistry()

    return _global_registry


def reset_schema_registry() -> None:
    """
    Reset global SchemaRegistry singleton (for testing).

    Forces next call to get_schema_registry() to reload from disk.
    """
    global _global_registry
    _global_registry = None
