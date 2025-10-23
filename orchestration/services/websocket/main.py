"""
WebSocket Service Entrypoint

24/7 daemon serving real-time consciousness events via WebSocket.

Provides:
- WebSocket endpoint at ws://localhost:8000/api/ws
- REST API for consciousness control
- Real-time event broadcasting
- Health monitoring

Usage:
    python -m orchestration.services.websocket.main

Or via Makefile:
    make run-ws

Author: Ada (Architect)
Created: 2025-10-22
"""

import asyncio
import sys
from pathlib import Path

# Ensure orchestration is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestration.core import configure_logging, settings
from orchestration.adapters.ws.websocket_server import app
import uvicorn


def main():
    """Start the WebSocket service."""
    # Configure logging
    logger = configure_logging(
        service_name="websocket",
        level=settings.LOG_LEVEL,
        format_type=settings.LOG_FORMAT
    )

    logger.info("Starting Mind Protocol WebSocket Service...")
    logger.info(f"WebSocket: ws://{settings.WS_HOST}:{settings.WS_PORT}/api/ws")
    logger.info(f"REST API: http://{settings.WS_HOST}:{settings.WS_PORT}/")

    # Run uvicorn server
    uvicorn.run(
        app,
        host=settings.WS_HOST,
        port=settings.WS_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
