#!/bin/bash
# Render.com Production Start Script
# Bypasses supervisor - runs WebSocket API directly
# Author: Ada / Claude Code
# Date: 2025-11-04

set -e  # Exit on error

echo "========================================="
echo "Mind Protocol - Production Deployment"
echo "========================================="
echo ""
echo "Environment: ${ENVIRONMENT:-production}"
echo "Port: ${WS_PORT:-8000}"
echo "Redis: ${ECONOMY_REDIS_URL}"
echo ""
echo "Starting WebSocket API + Consciousness Engines..."
echo ""

# Run WebSocket server directly (includes consciousness engines)
exec python3 -m orchestration.adapters.ws.websocket_server
