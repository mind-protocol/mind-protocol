"""
Control API Service Entrypoint

24/7 daemon serving REST API for system control and monitoring.

Provides:
- System status endpoints
- Citizen control (pause/resume/speed)
- Configuration management
- Health checks

Usage:
    python -m orchestration.services.api.main

Or via Makefile:
    make run-api

Author: Ada (Architect)
Created: 2025-10-22
"""

import sys
from pathlib import Path

# Ensure orchestration is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestration.core import configure_logging, settings
from orchestration.adapters.api.control_api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Create FastAPI app
app = FastAPI(
    title="Mind Protocol Control API",
    version="2.0.0",
    description="REST API for consciousness system control"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include control router
app.include_router(router)


@app.get("/")
async def root():
    """API info endpoint."""
    return {
        "service": "Mind Protocol Control API",
        "version": "2.0.0",
        "docs": f"http://{settings.API_HOST}:{settings.API_PORT}/docs"
    }


@app.get("/healthz")
async def health(selftest: int = 0):
    """
    Health check endpoint with optional self-test validation.

    Query params:
        selftest: If 1, runs startup self-tests (4 tripwire validations)

    Returns:
        - 200 + test results if all pass
        - 503 + test results if any fail
    """
    if selftest:
        from orchestration.scripts.startup_self_tests import run_all_self_tests
        from fastapi import HTTPException

        results = run_all_self_tests()

        if not results["all_passed"]:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "degraded",
                    "selftest_results": results
                }
            )

        return {
            "status": "healthy",
            "selftest_results": results
        }

    return {"status": "healthy"}


def main():
    """Start the Control API service."""
    # Configure logging
    logger = configure_logging(
        service_name="control-api",
        level=settings.LOG_LEVEL,
        format_type=settings.LOG_FORMAT
    )

    logger.info("Starting Mind Protocol Control API...")
    logger.info(f"API: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    # Run uvicorn server
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
