# Mind Protocol Orchestration Layer

**Architecture:** Clean separation of concerns for consciousness infrastructure

---

## Directory Structure

```
orchestration/
├── services/              # 24/7 daemons (entrypoints)
│   ├── api/              # REST API for control
│   ├── websocket/        # WebSocket event streaming
│   ├── watchers/         # File/conversation monitoring
│   ├── telemetry/        # Health monitoring
│   └── learning/         # Learning system services
├── workers/              # Scheduled/batch jobs
├── adapters/             # I/O boundaries
│   ├── api/             # FastAPI routers
│   ├── ws/              # WebSocket implementation
│   ├── storage/         # FalkorDB operations
│   └── search/          # Embedding & semantic search
├── mechanisms/           # Domain logic (pure algorithms)
├── libs/                # Stateless helpers
│   └── utils/           # General utilities
├── core/                # Models, config, events
│   ├── node.py          # Node data structure
│   ├── link.py          # Link data structure
│   ├── subentity.py        # Subentity data structure
│   ├── graph.py         # Graph container
│   ├── settings.py      # Centralized config
│   ├── logging.py       # Structured logging
│   ├── events.py        # Event schemas
│   └── health.py        # Health checks
├── tests/               # Mirrors structure
└── scripts/             # Dev utilities
```

---

## Dependency Rules

**Services & Workers** → depend on adapters, mechanisms, libs, core
**Mechanisms** → depend on libs, core
**Adapters** → depend on libs, core
**Core & Libs** → depend on nothing above them

---

## Configuration

All configuration is centralized in `core/settings.py`:

```python
from orchestration.core import settings

print(settings.WS_PORT)  # 8765
print(settings.API_PORT)  # 8788
print(settings.LOG_LEVEL)  # INFO
```

Configuration can be overridden via environment variables:

```bash
export MP_WS_PORT=9000
export MP_LOG_LEVEL=DEBUG
export LOG_FORMAT=text  # or json
```

---

## Running Services

### Individual Services (Dev/Testing)

```bash
# WebSocket server
make run-ws

# Control API
make run-api

# Watchers
make run-conv-watcher
make run-code-watcher
make run-n2-watcher

# Telemetry
make run-viz-health
make run-heartbeat

# Learning
make run-learning-hb
make run-branching
```

### Production (Guardian)

In production, **guardian.py** manages all processes:

```bash
# Start all services
python guardian.py

# Guardian auto-restarts crashed services
# Guardian hot-reloads on code changes
# Never manually start/kill services when guardian is running
```

---

## Logging

All services use structured JSON logging:

```python
from orchestration.core import configure_logging, log_with_fields

logger = configure_logging("my-service", level="INFO", format_type="json")

logger.info("Service started")

log_with_fields(
    logger,
    "info",
    "Frame completed",
    frame_id="frame_123",
    duration_ms=45.2,
    nodes_activated=12
)
```

Output:
```json
{
  "timestamp": "2025-10-22T20:45:00.000Z",
  "service": "my-service",
  "level": "INFO",
  "message": "Frame completed",
  "frame_id": "frame_123",
  "duration_ms": 45.2,
  "nodes_activated": 12
}
```

---

## Health Checks

All services expose health probes:

```python
from orchestration.core import HealthProbe, run_health_server

probe = HealthProbe("my-service")

# Add checks
probe.add_check("database", lambda: db.is_connected())
probe.add_check("queue", lambda: queue.is_healthy())

# Add metrics
probe.add_metric("active_connections", lambda: len(connections))

# Run health server
await run_health_server(probe, port=8789)

# GET /healthz returns:
# {
#   "status": "healthy",
#   "service_name": "my-service",
#   "uptime_seconds": 3600.5,
#   "checks": {"database": true, "queue": true},
#   "metrics": {"active_connections": 5}
# }
```

---

## Events

All websocket events conform to schemas in `core/events.py`:

```python
from orchestration.core import create_event

event = create_event(
    event_type="node_activated",
    citizen_id="luca",
    frame_id="frame_123",
    node_id="node_456",
    node_name="realization_consciousness_substrate",
    energy=0.85,
    source="stimulus_injection"
)

# Emit to clients
await websocket_manager.broadcast(event.to_dict())
```

This ensures Python backend and TypeScript frontend agree on event structure.

---

## Testing

```bash
# Run all tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration
```

Tests mirror the source structure:
- `tests/unit/adapters/` → tests for adapters
- `tests/unit/mechanisms/` → tests for mechanisms
- `tests/integration/services/` → tests for services

---

## Adding a New Service

1. **Create entrypoint:** `services/my_service/main.py`
2. **Configure logging:** Use `configure_logging()`
3. **Add health probe:** Use `HealthProbe` and `/healthz`
4. **Add to Makefile:** `make run-my-service`
5. **Add to guardian:** Register in `guardian.py` config
6. **Document:** Update this README

Example minimal service:

```python
# services/my_service/main.py
import asyncio
from orchestration.core import configure_logging, settings, HealthProbe

async def main():
    logger = configure_logging("my-service", level=settings.LOG_LEVEL)
    probe = HealthProbe("my-service")

    logger.info("Starting my service...")

    # Service loop
    while True:
        probe.heartbeat()
        # Do work...
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Architecture Decisions

**Why this structure?**

1. **Separation of Concerns:** Services (entrypoints) vs adapters (I/O) vs mechanisms (domain logic)
2. **Testability:** Pure functions in mechanisms/, mockable adapters
3. **Reusability:** Adapters and libs can be shared across services
4. **Clarity:** One entrypoint per daemon, clear dependencies
5. **Observability:** Structured logs, health checks, event schemas
6. **Maintenance:** Easy to find what runs 24/7 vs what's a library

**Key Principles:**
- Services don't import services (only adapters/mechanisms/libs/core)
- Mechanisms are pure algorithms (no I/O)
- Configuration is centralized (core/settings.py)
- Logging is structured (JSON)
- Every daemon has graceful shutdown (CTRL-C safe)

---

## Authors

- **Felix "Ironhand"** (Engineer) - Core data structures, engine implementation
- **Ada "Bridgekeeper"** (Architect) - Infrastructure reorganization, clean architecture

**Created:** 2025-10-19
**Reorganized:** 2025-10-22 (Ada: clean separation of concerns)

---

*"One solution per problem. Services are services, adapters are adapters, mechanisms are mechanisms. Clear boundaries enable clear thinking."*
