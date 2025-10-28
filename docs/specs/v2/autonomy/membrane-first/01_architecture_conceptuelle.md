# Conceptual Architecture (L1 → L4)

## Open Questions (to resolve before locking specs)
- Provider surface for v0: which adapters are in-scope (Claude Code, Codex, Gemini)?
- Success criteria for v0: latency target, number/type of end-to-end demos?
- Default lane policy for local dev: capacities, ACK requirements?
- Local security model: how are org dev keys issued/rotated?
- Publication flow: documentation PRs only, or static-site preview as well?
- Ecosystem L3 example: include the trading manifest during v0 or defer until after the POC?
- Object storage: use a local mock folder or connect to a dev S3-compatible bucket?

## Invariants
- **Pure Membrane**: all influence flows through `membrane.inject`; all observation happens via broadcast topics. No REST pulls or hidden admin routes.
- **Physics-first hardening**: Integrator enforces saturation & refractory windows; Membrane enforces Pareto + MAD guards, emission ledger, κ-learning. No side switches.
- **Tenancy & signatures**: each envelope carries `org` and is ed25519-signed; policy updates are stimuli (`policy.change` → `policy.applied`).

> **Reference specs (do not duplicate)**
> - [Stimulus Integrator Mechanism](../architecture/stimulus_integrator_mechanism.md) – saturation, refractory, trust EMA.
> - [Cross-Level Membrane](../architecture/cross_level_membrane.md) – Pareto, MAD guard, emission ledger, κ-learning.
> - [Membrane Hardening](../architecture/membrane_hardening.md) – anti-spam, anti-gaming rationale.
> - [Signals → Stimuli Bridge](../architecture/signals_to_stimuli_bridge.md) – normalization pipeline feeding the bus.
> - [Membrane Systems Map](../architecture/membrane_systems_map.md) & [Foundation](../architecture/foundation.md) – historical context and invariants.
> - [Implementation Gap Analysis](../../IMPLEMENTATION_GAP_ANALYSIS.md) – prior checklist for repo lean / publishing discipline.

## Layer Overview
- **L4 (Protocol)**  
  - Owns canonical schemas (`membrane.inject`, `percept.frame`, `graph.delta.*`, etc.).  
  - Publishes SDKs (TS/Python/Go) and the Sidecar client.  
  - Maintains adapters (Claude Code, Codex, Gemini) and conformance streams.  
  - Guarantees backward compatibility by versioning schemas and generators.
- **L3 (Ecosystems)**  
  - Defines domain-specific bootstrap manifests (lanes, intent templates, tool catalog, citizens, renderers, security).  
  - Emits onboarding events (`ecosystem.announce`, `ecosystem.onboard.request/accepted`).  
  - Provides curated defaults (e.g., trading vs incidents) but never edits org repos directly.
- **L2 (Organization)**  
  - Runs orchestrator + tool mesh inside the organization workspace.  
  - Keeps git repos lean: `.mind/config.yaml`, `sdk/`, `renderers/`, `publications/`, `ci/`.  
  - Executes all provider interactions via Sidecar; manages evidence storage & publication PRs.  
  - No raw conversations persisted; publications reference evidence hashes from object storage.
- **L1 (Citizens)**  
  - Consciousness engines: working memory emitters, percept frame emitters, membrane integrator.  
  - Consume broadcast events, influence only through `membrane.inject`.  
  - Persist long-term state in FalkorDB (graph) and stream telemetry via broadcast.

### Layer interactions diagram
```
Providers → Sidecar → Bus (inject) → Integrator → Engine (L1) → Membrane → Bus (broadcast) → UI / Orchestrator / Tool Mesh
                                     ↑                                   ↓
                              Graph Store (FalkorDB)           Object Store / Publications
```

## Canonical Flow (summary)
1. **Workspace edit** – Provider saves a file → FS watcher emits `membrane.inject(channel=citizen_file_ops, payload={path, sha256, change})`.  
2. **Orchestration** – Orchestrator ingests the stimulus, instantiates `intent.created`, then assigns a citizen via `mission.assigned`.  
3. **Tool execution** – Citizen/tool mesh issues `tool.request.git.commit` → Git Runner executes, responds through `tool.result {commit_sha, branch}`.  
4. **Publication** – Renderer subscribes to `mission.done` / `tool.result`, generates docs/static assets under `publications/`, and optionally triggers `tool.request.git.pr`.  
5. **Observability** – UI / dashboards consume `percept.frame`, `graph.delta.*`, `telemetry.*` to visualise real-time state; backpressure feedback flows via `ui.render.backpressure`.  
6. **Governance** – Any policy change uses `policy.change`; acceptance is emitted as `policy.applied` before effect takes place.

## Guiding principles for implementers
- Treat the bus as the **single source of truth**; avoid “shortcuts” (direct DB writes, HTTP bypass).
- Every new capability must declare how it fits into the event contract surface.
- If you cannot express a control operation as a stimulus, revisit the design.
