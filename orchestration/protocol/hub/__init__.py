"""
L4 Protocol Hub - Membrane Bus Infrastructure

This package contains the L4 protocol enforcement layer.
It is the boundary between layers (L1↔L2↔L3) and enforces:
- Envelope schemas
- SEA-1.0 signatures
- CPS-1 quotas
- Rate limits
- Tenant scoping

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

from .membrane_hub import main

__all__ = ["main"]
