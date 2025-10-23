"""
Services package for Mind Protocol orchestration layer.

24/7 daemons:
- api: REST API service
- websocket: WebSocket event streaming
- watchers: File/conversation monitoring
- telemetry: Health monitoring and metrics
- learning: Learning system services

Each service has a main.py entrypoint with graceful shutdown.

Author: Ada (Architect)
Created: 2025-10-22
"""
