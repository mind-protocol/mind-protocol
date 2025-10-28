# Implementation To-Do (localhost-first)

## A. Bus & Sidecar
- [ ] WebSocket mux (`/inject`, `/broadcast`) with schema validation & signature check.  
      _Include_: in-memory persistence (circular buffer), console logging, TLS toggle placeholder.  
- [ ] Sidecar client (buffer + replay, key management, CLI for quick sends).  
      _Deliverables_: Python package with `sidecar run`, `sidecar send`, `sidecar key rotate`.  
- [ ] Schema loader + signature utility shared across bus & sidecar.  
- [ ] CLI helper to send sample stimuli (`ui.action.*`, `citizen_file_ops`, `tool.request.git.commit`).  
- [ ] Unit tests: invalid signature rejected, TTL expiry triggers `inject.rejected`.

## B. SDK & Adapters
- [ ] SDK (TS & Python): helper to build/sign `membrane.inject`, typed event payloads.  
- [ ] Claude Code hook scripts (`UserPromptSubmit`, `Stop`, `PreCompact`, `PreToolUse`).  
- [ ] Codex / Gemini PTY wrappers (stdin/stdout bridging, environment setup).  
- [ ] Shared FS watcher (dedupe, rate, TTL).  
- [ ] Code samples (`sdk/examples/*.py, *.ts`) demonstrating usage.  
- [ ] Smoke tests: run adapter hook end-to-end emitting to local bus.

## C. Engines & Orchestrator
- [ ] Integrator with saturation buckets, refractory timers, trust EMA updates (telemetry exposed).  
- [ ] Membrane gate implementing Pareto record, MAD guard, emission ledger, κ-learning (per flow).  
- [ ] Orchestrator lanes (capacity, ACK policy), mission lifecycle, tool routing heuristics.  
- [ ] Telemetry broadcasts (`telemetry.integrator`, `telemetry.mem_gates`).  
- [ ] Config loader `.mind/config.yaml` (lanes, citizens, tools).  
- [ ] Simulation script injecting sample stimuli to exercise gates.

## D. Tool Mesh
- [ ] Git Runner (`commit`, `branch`, `pr`) with configurable templates.  
- [ ] Renderer (docs/site generator) triggered by `mission.done` / `tool.result`.  
- [ ] Stub tool for notifications (optional) to test capability routing.  
- [ ] Tool registry loader; `tool.offer` auto-published on startup.  
- [ ] Tests verifying `tool.request` with missing capability emits `tool.result {ok:false}`.

## E. UI / Observer
- [ ] Simple observer UI or console view subscribing to `percept.frame`, `graph.delta.*`, `intent.*`, `tool.*`.  
- [ ] Emit `ui.action.*` and `ui.render.backpressure` from the interface.  
- [ ] Ensure zero HTTP pulls (guard rails / lint rule).  
- [ ] Provide JSON console viewer (`python tools/observe.py`) for quick debugging.  
- [ ] Document how to plug in existing dashboard once streaming-only is ready.

## Acceptance Criteria (v0)
- [ ] **No REST/state pulls**: UI renders 100% from broadcasts; p95 inject→visible ≤ 150 ms (localhost benchmark script).  
- [ ] **Git discipline**: all commits/PRs traverse `tool.request.git.*` / `tool.result`; IDE push is disabled.  
- [ ] **Dynamic tool mesh**: a new tool binary can start, emit `tool.offer`, and serve requests without restarting orchestrator.  
- [ ] **Physics observable**: `membrane.export.rejected`, `telemetry.integrator`, κ metrics visible via observer logs; include sample dashboards.  
- [ ] **Renderer output**: produces PR-ready artifacts referencing evidence hashes (no raw chats) and opens PR via Git Runner stub.  
- [ ] **Policy change path**: injecting signed `policy.change` adjusts orchestrator configuration live and emits `policy.applied`.  
