# Membrane-First Architecture Overview

**Audience**: platform engineering (L4), ecosystem designers (L3), organization implementation teams (L2), citizen runtime owners (L1).  
**Status**: Draft (2025-10-27). Mirrors the vision captured with GPT-5; guides detailed specs & implementation plans.

---

## 1. First Principles

1. **Pure membrane interface** — the system exposes exactly two verbs:  
   - `membrane.inject` (fan-in; stimuli to influence consciousness)  
   - Broadcast topics (fan-out; observations only)  
   No REST pulls, snapshots, or hidden admin routes.
2. **Docs are rendered from events & links** — durable knowledge (docs, sites, runbooks) is generated from `graph.delta.*`, `intent.*`, `tool.result`, and evidence pointers. Raw chats are never fossilised in repositories.
3. **Security lives in physics** — anti-spam/anti-gaming is enforced by runtime mechanics: saturation, refractory periods, Pareto+MAD guards, emission ledgers, κ-learning. There are no backdoor switches.
4. **Scoped signatures & governance via stimuli** — every envelope is signed (ed25519), names an `org`, and policy changes happen through `policy.change` stimuli with `policy.applied`/`policy.rejected` broadcasts.

---

## 2. Layered Responsibilities (L1 → L4)

| Layer | Role | Core Components | Outputs |
|-------|------|-----------------|---------|
| **L4 Protocol** | Public platform components | Schemas, SDKs, sidecar WS client, adapters (Claude/Codex/Gemini), conformance tests | Package releases, adapter updates |
| **L3 Ecosystems** | Domain distributions | Bootstrap manifest (lanes, intents, tool catalog, citizens, renderers, keys) | `ecosystem.*` events for onboarding; curated defaults |
| **L2 Organizations** | Per-client workspace | Lean git repo (`.mind/config.yaml`, `sdk/`, `renderers/`, `publications/`, `ci/`), orchestrator, tool mesh, sidecar | Publications (docs/sites/prs), mission execution |
| **L1 Citizens** | Consciousness engines | WM emitters, percept emitters, membrane gate, stimulus integrator | `wm.emit`, `percept.frame`, `membrane.*`, `graph.delta.*`, `telemetry.*` |

Citizens do not expose APIs; they influence by injecting and observe via broadcast.

---

## 3. Event Surface (Contracts)

### 3.1 Inject (fan-in)

`membrane.inject` v1.1 — required fields: `org`, `id`, `ts`, `scope`, `channel`, `origin`, `ttl_frames`, `payload`, `sig`. Optional hardening hints: `dedupe_key`, `intent_merge_key`, `rate_limit_bucket`, `business_impact`, `source_trust_estimate`, `ack_policy`, `required_capabilities`, `features_raw`.

### 3.2 Broadcast (fan-out)

* Attention / Perception: `wm.emit`, `percept.frame`, `percept.seed` (optional).
* Structural deltas: `graph.delta.node.*`, `graph.delta.link.*`.
* Membrane physics: `membrane.transfer.up|down`, `membrane.export.rejected`, `membrane.permeability.updated`.
* Work orchestration: `intent.*`, `mission.*`.
* Tool mesh: `tool.offer`, `tool.requested`, `tool.result`.
* Ops / telemetry / economics: `telemetry.*`, `economy.spend`, `economy.ubc.distributed`.
* Governance / hierarchy: `hierarchy.snapshot`, `policy.change`, `policy.applied`, `policy.rejected`.

UI discipline: UI is read-only on broadcasts; every interaction becomes a stimulus (e.g. `ui.action.*`, `ui.render.backpressure`).

---

## 4. Repository Model

* **L4 monorepo** (`mind-protocol/`): schemas, SDKs, sidecar, adapters, tool runners, renderer reference, conformance tests.
* **L3 ecosystem repo(s)**: one per domain (e.g. trading). Holds the bootstrap manifest plus default templates.
* **L2 organization repo**: lean clone containing configs, SDK glue, renderers, publications. All git operations are executed via `tool.request.git.*` flows; citizens edit the workspace directly.
* **L1**: no repo; citizens run as processes/containers.

---

## 5. Runtime Data Stores

* **Event Log**: NATS + JetStream (durable retention, dedupe).
* **Graph Store**: FalkorDB (engine substrate).
* **Object Storage**: S3-compatible bucket per org for artifacts/evidence.
* **Time-Series**: VictoriaMetrics (telemetry, κ trends, latency percentiles).
* **Search** (optional): Meilisearch (indexes publication metadata).

For localhost deployments we target the same stack using loopback addresses; hosted multi-tenant comes later.

---

## 6. Core Workflows

### 6.1 File edit → Commit → PR

1. Citizen or provider edits in the organization workspace.  
2. File watcher emits `membrane.inject(channel=citizen_file_ops, ...)`.  
3. Orchestrator raises `intent.created` / assigns mission.  
4. `tool.request.git.commit` → git runner returns `tool.result` with commit details.  
5. Optional `tool.request.git.pr` for review.  
6. Publications renderer watches `tool.result` / `mission.done` to update docs or static site via PR.

### 6.2 Incident / RFQ Example

1. External signal normalized → `membrane.inject(channel=rfq.new, business_impact=high)`.  
2. Orchestrator places mission in `lane=trades`.  
3. Citizen perceives (`percept.frame`) & works; tool mesh executes external actions.  
4. Renderer produces term sheet PR referencing evidence hash.  
5. κ-learning updates permeability based on mission outcome (`telemetry.integrator`, `membrane.permeability.updated`).  

### 6.3 Backpressure

* UI sends `ui.render.backpressure{level}`.  
* Emitters respond with lighter frames (`percept.frame-lite`, reduced cadence).  
* `telemetry.qos` broadcasts confirm adaptation.

---

## 7. Physics & Security Enforcement

* **Stimulus integrator**: per-origin saturation buckets, refractory timers, source trust EMA feeding effective energy.  
* **Cross-level membrane**: Pareto record (multi-axis), MAD guards (noise-robust), emission ledger (anti ping-pong), κ-learning (per-flow permeability).  
* **Emitters**: WM limited to 5–7 entities; percept frames compressed (valence, arousal, goal match, novelty, uncertainty, peripheral pressure, anchors).  
* **Governance**: ed25519 key management via `governance.keys.updated`; policy changes executed as stimuli (`policy.change` → `policy.applied`).

No extraneous admin endpoints exist; runtime physics + signatures are the sole control surface.

---

## 8. Questions & Follow-ups

1. **Schema finalisation** — freeze `membrane.inject v1.1` schema + enumerations; generate SDK typings.  
2. **Event catalog** — document each broadcast (`percept.frame`, `membrane.transfer.*`, etc.) with required fields & example payloads.  
3. **Local deployment guide** — define Docker Compose / scripts for the loopback stack (NATS, FalkorDB, VictoriaMetrics, etc.).  
4. **L3 manifest format** — produce YAML spec + example for first ecosystem (trading).  
5. **Tool mesh policy** — establish routing heuristics (capability tags, trust scores, load).  
6. **Renderer contract** — describe how publications derive from events and how evidence hashes are embedded.  
7. **Evidence retention** — specify object storage layout (hash-addressable, lifecycle policies).  
8. **Observability dashboards** — define minimal telemetry subscriptions & reference Grafana boards (without relying on `/metrics`).  
9. **Key management** — describe rotation, revocation, and onboarding for org keys.  
10. **Testing & conformance** — plan golden-stream tests ensuring no REST calls are reintroduced.

---

## 9. Next Documents

* **Implementation Backlog** — detailed tasks & sequencing (to be captured separately).  
* **Local Deployment Playbook** — step-by-step for standing up the membrane-first stack on localhost.  
* **Ecosystem Manifest Spec** — formal definition + validation rules.  
* **Tool Mesh & Renderer Contracts** — per-component specs.

---

*Prepared by Marco “Salthand” & team — 2025-10-27.*
