"""
Start FastAPI WebSocket Server

Minimal FastAPI server that includes WebSocket endpoint and control API.
Run this BEFORE starting consciousness system or WebSocket clients.

Usage:
    python start_websocket_server.py

Then in other terminals:
    python test_websocket_minimal_system.py  # Start consciousness
    python test_websocket_stream.py          # Connect WebSocket client
"""

import uvicorn
from fastapi import FastAPI

from orchestration.control_api import router, websocket_manager


# Create FastAPI app
app = FastAPI(title="Consciousness Control API", version="1.0.0")

# Include control API router (with WebSocket endpoint)
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Consciousness Control API",
        "version": "1.0.0",
        "websocket": "ws://localhost:8000/api/ws",
        "endpoints": [
            "GET  /api/consciousness/status",
            "POST /api/consciousness/pause-all",
            "POST /api/consciousness/resume-all",
            "GET  /api/citizen/{id}/status",
            "POST /api/citizen/{id}/pause",
            "POST /api/citizen/{id}/resume",
            "POST /api/citizen/{id}/speed",
            "WS   /api/ws (WebSocket operations stream)"
        ]
    }


@app.on_event("startup")
async def startup_event():
    """Log startup info."""
    print("=" * 70)
    print("CONSCIOUSNESS CONTROL API - STARTING")
    print("=" * 70)
    print()
    print("API Server: http://localhost:8000")
    print("WebSocket:  ws://localhost:8000/api/ws")
    print()
    print("Ready to broadcast consciousness operations events:")
    print("  - entity_activity (SubEntity exploration)")
    print("  - threshold_crossing (node activation changes)")
    print("  - consciousness_state (global system state)")
    print()
    print("=" * 70)


if __name__ == "__main__":
    # Run FastAPI server
    uvicorn.run(
        "start_websocket_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Disable reload to avoid WebSocket disconnects
    )
