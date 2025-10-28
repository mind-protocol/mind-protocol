# Localhost Topology (v0)

## Core Services (local)
- **Protocol graph (L4)**  
  - Seed via `python tools/protocol/build_protocol_snapshot.py` then `python tools/protocol/seed_protocol_graph.py --apply`.  
  - Populates FalkorDB `protocol` graph with schema/runtime releases (separate from `schema_registry`).

- **Bus**  
  - Process: `python ./scripts/ws_bus.py` (to be implemented).  
  - Provides `/inject` (ingest, schema validation, signature check) and `/broadcast` (fan-out).  
  - Logs decision events (`inject.accepted`, `inject.rejected`) to stdout for visibility.  
  - Persistence: start with in-memory queue; plan for JetStream once stable.
- **Sidecar**  
  - CLI: `python ./sdk/sidecar/run.py --inject ws://localhost:8765/inject --broadcast ws://localhost:8766/broadcast`.  
  - Responsibilities: key management, offline buffer (`~/.mind/sidecar/buffer.jsonl`), automatic retry.  
  - Provides helper commands (`sidecar send ui.action.user_prompt "..."`).
- **Orchestrator**  
  - Process: `python ./orchestration/run_orchestrator.py --config .mind/config.yaml`.  
  - Subscribes to all `membrane.inject` stimuli, enforces lane rules, emits `intent.*` and `mission.*`, routes `tool.request.*`.  
  - Writes progress logs to `./logs/orchestrator.log`.
- **Engines (L1 / L2)**  
  - Launch via `python ./orchestration/run_engine.py --citizen E.builder`.  
  - Connect to FalkorDB (`redis://localhost:6379`).  
  - Emit `wm.emit`, `percept.frame`, `graph.delta.*`, `telemetry.*`.
- **Tool runners**  
  - Git Runner: `python ./tools/git_runner.py`.  
  - Renderer: `python ./tools/renderer.py` (monitors missions, generates docs).  
  - Each runner listens on broadcast for `tool.requested` directed to its capability set.
- **Object storage**  
  - Local mock path `C:\Users\reyno\mind-protocol\_objects`.  
  - CLI `python ./tools/object_store.py put <file>` returns a content-addressed URI (`local://sha256/...`).
- **Graph store**  
  - FalkorDB local container: `docker compose up falkordb`.  
  - Seed script: `python ./tools/seed_graph.py`.
- **Observability**  
  - Simple subscriber `python ./tools/subscriber.py --topics telemetry.*` printing metrics.  
  - Later: integrate VictoriaMetrics (push via `telemetry.exporter`).

## Suggested Topics / URLs
- Inject WS: `ws://localhost:8765/inject`
- Broadcast WS: `ws://localhost:8766/broadcast`
- Local object folder: `C:\Users\reyno\mind-protocol\_objects`
- Graph endpoint: `redis://localhost:6379` (if FalkorDB via Redis protocol)

## Environment Variables (example)
```
ORG_ID=dev-org
MEMBRANE_WS_INJECT=ws://localhost:8765/inject
MEMBRANE_WS_BROADCAST=ws://localhost:8766/broadcast
WORKSPACE_DIR=C:\Users\reyno\mind-protocol\orgs\dev-org\workspace
OBJECT_STORE_PATH=C:\Users\reyno\mind-protocol\_objects
FALKORDB_URL=redis://localhost:6379
```

## Smoke Tests
- Save a file in the workspace → watch `membrane.inject` (`citizen_file_ops`) via bus logs → confirm `intent.created` and `mission.assigned` on broadcast.
- Submit `tool.request.git.commit` (CLI or orchestrator) → Git Runner writes commit → `tool.result` visible with `commit_sha`.
- Send `ui.render.backpressure level=2` via Sidecar CLI → observe lighter `percept.frame` cadence and `telemetry.qos` update.
- Inject `policy.change` with a test key → expect `policy.applied` (if signature valid) or `policy.rejected` (if not) within two broadcast ticks.
