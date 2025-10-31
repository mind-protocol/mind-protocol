"""FastAPI application entrypoint for membrane-ready routers."""

from adapters.api.app import create_app

__all__ = ["create_app"]
