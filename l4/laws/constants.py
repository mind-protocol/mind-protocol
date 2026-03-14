"""
Law definitions and fee constraints for L4 ecosystem compliance.

DOCS: docs/l4/laws/PATTERNS_Laws.md
"""

from l4.schema import SCHEMA_VERSION

# The 8 ecosystem laws.
LAWS = {
    "L1": "Respect schema",
    "L2": "Register to exist",
    "L3": "No direct DB access",
    "L4": "Cross-org via membrane",
    "L5": "Hash-based identity",
    "L6": "Receiver validates",
    "L7": "Membrane fees",
    "L8": "WebSocket only",
}

# Fee constraints: cross-org transactions pay 1-5% to the protocol.
MIN_FEE_RATE = 0.01
MAX_FEE_RATE = 0.05

# Schema version required for compliance.
REQUIRED_SCHEMA_VERSION = SCHEMA_VERSION
