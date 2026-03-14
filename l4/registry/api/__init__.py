"""
L4 Registry REST API — FastAPI application.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

Exports the FastAPI app for use with uvicorn:
    uvicorn l4.registry.api.app:app --port 8766
"""

from .app import app

__all__ = ["app"]
