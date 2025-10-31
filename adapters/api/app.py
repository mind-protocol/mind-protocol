"""FastAPI application wiring for the strangler façade."""
from __future__ import annotations

from fastapi import FastAPI

from adapters.api.routers import engine, snapshot, tasks


def create_app() -> FastAPI:
    """Create a FastAPI application with the membrane-ready routers."""

    app = FastAPI(
        title="Mind Protocol Control API",
        description="Router-first API exposing engine snapshots and intent planning.",
        version="3.0.0",
    )

    app.include_router(engine.router)
    app.include_router(snapshot.router)
    app.include_router(tasks.router)

    return app


app = create_app()


__all__ = ["app", "create_app"]
