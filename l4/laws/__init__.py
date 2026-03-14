"""
L4 Laws module for Mind Protocol.

DOCS: docs/l4/laws/IMPLEMENTATION_Laws.md

Exports:
- Stimulus and compliance checking
- Audit reporting
- Law definitions and fee constants
"""

from .compliance import (
    Stimulus,
    ComplianceResult,
    check_stimulus_compliance,
)

from .audit import (
    AuditReport,
    audit_org,
)

from .constants import (
    LAWS,
    MIN_FEE_RATE,
    MAX_FEE_RATE,
    REQUIRED_SCHEMA_VERSION,
)

__all__ = [
    # Compliance
    "Stimulus",
    "ComplianceResult",
    "check_stimulus_compliance",
    # Audit
    "AuditReport",
    "audit_org",
    # Constants
    "LAWS",
    "MIN_FEE_RATE",
    "MAX_FEE_RATE",
    "REQUIRED_SCHEMA_VERSION",
]
