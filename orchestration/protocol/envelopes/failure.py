"""
L4 Protocol Envelopes - Failure (R-400/R-401 Compliance)

Protocol-level envelope schema for fail-loud error reporting.
All exceptions must be surfaced via failure.emit - never swallow.

Topics:
- ecosystem/{eco}/org/{org}/failure.emit
- ecosystem/{eco}/protocol/failure.emit (for L4 violations)

Author: Mel "Bridgekeeper"
Date: 2025-11-04 (Promoted to L4 protocol artifacts)
"""

from typing import Optional, Literal
from pydantic import BaseModel


class FailureEmit(BaseModel):
    """
    Fail-loud error reporting (R-400/R-401 compliance).

    Never swallow exceptions - always emit failure.emit.
    """
    code_location: str  # "services/view_resolvers/runner.py:88" or "protocol.hub:enforce_cps1"
    exception: str  # repr(e) or error description
    severity: Literal["error", "warning", "critical"]
    suggestion: str  # Helpful hint for fixing
    trace_id: Optional[str] = None  # Optional trace/request ID for correlation
    original_envelope: Optional[dict] = None  # Include rejected envelope for protocol violations
