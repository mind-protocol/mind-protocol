"""
Schema version tracking for Mind Protocol.

DOCS: docs/l4/schema/IMPLEMENTATION_Schema.md
"""

from enum import Enum
from dataclasses import dataclass


# Current schema version
SCHEMA_VERSION = "1.8.1"

# Protocol version (independent of schema)
PROTOCOL_VERSION = "1.0.0"


class VersionCompatibility(str, Enum):
    """Result of version compatibility check."""

    EXACT_MATCH = "exact_match"
    MINOR_DIFF = "minor_diff"  # Compatible with warnings
    MAJOR_DIFF = "major_diff"  # Incompatible


@dataclass
class VersionInfo:
    """Parsed semantic version."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version: str) -> "VersionInfo":
        """Parse semver string."""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2]),
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def check_version_compatibility(local: str, protocol: str) -> VersionCompatibility:
    """
    Check if local schema version is compatible with protocol.

    - Major differs → INCOMPATIBLE (breaking change)
    - Minor differs → COMPATIBLE with warnings (new features)
    - Only patch differs → COMPATIBLE (bug fixes)
    """
    local_v = VersionInfo.parse(local)
    protocol_v = VersionInfo.parse(protocol)

    if local_v.major != protocol_v.major:
        return VersionCompatibility.MAJOR_DIFF

    if local_v.minor != protocol_v.minor:
        return VersionCompatibility.MINOR_DIFF

    return VersionCompatibility.EXACT_MATCH


def get_schema_version() -> str:
    """Get current schema version."""
    return SCHEMA_VERSION


def get_protocol_version() -> str:
    """Get current protocol version."""
    return PROTOCOL_VERSION
