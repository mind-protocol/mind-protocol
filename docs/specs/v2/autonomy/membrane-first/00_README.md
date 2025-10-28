# Membrane-First – Specification Pack (v2 / Autonomy)

**Goal**: capture the membrane-first architecture (inject / broadcast only), the event contracts, and the localhost-first implementation track. This pack is the working source of truth for GPT-5 / Codex agents and human maintainers while we stand up the v0 stack.

## Contents
- `01_architecture_conceptuelle.md` — L1→L4 view, roles, invariants.
- `02_event_contracts.md` — event schemas (`membrane.inject`, `percept.frame`, `graph.delta.*`, `intent.*`, `tool.*`, …).
- `03_topologie_localhost.md` — bus / graph / storage / observability for localhost.
- `04_providers_adapters.md` — Claude Code / Codex / Gemini (hooks & watchers).
- `05_impl_todo.md` — executable backlog + acceptance criteria.
- `06_manifest_L3_template.yaml` — bootstrap manifest for an ecosystem (e.g. trading).
- `07_glossaire.md` — definitions.

## How to use this folder
1. **Read `01_architecture_conceptuelle.md` first** to understand invariant principles and layer responsibilities.
2. Consult `02_event_contracts.md` when adding an event or verifying payloads.
3. Follow `03_topologie_localhost.md` to install/run the local stack.
4. Adapt provider-specific hooks via `04_providers_adapters.md`.
5. Track implementation progress in `05_impl_todo.md` (update checkboxes as tasks land).
6. Copy `06_manifest_L3_template.yaml` when designing a new ecosystem bootstrap.
7. Add terms to `07_glossaire.md` as the lexicon evolves.

## Status
- Audience: internal (L4 / L3 / L2 teams); this folder is meant for us and collaborating agents.
- Scope: specifications + localhost implementation (hosted deployment will follow later).
- Change process: open PRs touching these docs must include a short rationale referencing the relevant broadcast events or implementation tasks.
