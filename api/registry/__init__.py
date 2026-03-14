"""
REST API for L4 Registry — FastAPI application.

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md

Exports the FastAPI app for use with uvicorn:
    uvicorn api.registry.app:app --port 8766
"""

from .app import app

__all__ = ["app"]
