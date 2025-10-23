---
title: Type‑Dependent Decay (Dual‑Clock: Energy vs Weight)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/19_type_dependent_decay.md
depends_on:
  - foundations/decay.md
  - foundations/criticality.md
summary: >
  Energy (activation) decays fast; weights decay much slower — both scaled by type. No per‑entity channels.
---

# Type‑Dependent Decay

## 1) Context — Problem we’re solving
We need **fast** forgetting of activation and **slow** forgetting of structure, with differences by type (Memory vs Task, etc.). It must operate on the **single‑energy** substrate and remain compatible with the ρ controller. :contentReference[oaicite:12]{index=12}

## 2) Mechanism — What it is
- **Activation (energy) decay:** \(E_i \leftarrow \lambda_E^{dt}\,E_i\) with **type multiplier** \(m_E(\text{type})\).  
- **Weight decay (node/link):** `log_weight ← log_weight − γ(type)·dt` (or multiplicative in weight‑space) at a **much slower** rate \(m_W(\text{type})\).  
- ρ‑controller may adjust **effective** activation decay within bounds; **never** couples to weight decay.

### 2.1 Suggested profiles (illustrative)
| Type | Energy half‑life | Weight half‑life | Rationale |
|---|---:|---:|---|
| Memory | 12–24 h | weeks–months | “Sticks” structurally, fades in attention |
| Principle | 6–12 h | months | Persistent structure |
| Concept | 3–6 h | weeks | Moderate persistence |
| Task | 1–3 h | days | Clears quickly |
| Trigger | 2–4 h | weeks | Contextual cues |

Configure per type in `core/settings.py` (or a JSON table).

### 2.2 Links by type
Apply slower decay to semantic links (RELATES_TO), faster to BLOCKS, moderate to ENABLES/TRIGGERED_BY.

## 3) Why this makes sense
- **Phenomenology:** you can let go (energy fades) but still **resume** (weights persist).  
- **Bio‑inspiration:** short‑term activity vs long‑term synaptic change.  
- **Systems‑dynamics:** separates the lever used by the ρ controller (energy) from slow structure.

## 4) Expected behaviors
- Contexts become **cold** within hours, yet re‑assemble quickly after days thanks to weight persistence.  
- Temporary scaffolding (Tasks) vanishes on its own.

## 5) Why this vs alternatives
| Alternative | Issue | This mechanism |
|---|---|---|
| One decay for everything | Either sticky or amnesic | Dual‑clock |
| Per‑entity energy decay | Violates single‑energy | Type‑based only |
| Tie weight decay to ρ | Conflates stability with memory | Decoupled clocks |

## 6) Observability — How & what
- **Metrics:** per‑type **half‑life** estimates (fit from telemetry), energy/weight histograms, **decay vs reinforcement** balance.  
- **Events:** periodic `decay.tick` aggregates; type‑panels in viz.

## 7) Failure modes & guards
| Risk | Guard |
|---|---|
| Over‑decay of activation | Lower bound on λ_E; controller bounds |
| Over‑decay of weights | Min γ(type); audits of retrieval regressions |
| Hidden coupling | Keep weight decay off ρ loop; separate schedules |

## 8) Integration in code
- **Where:** `consciousness_engine_v2.apply_activation_decay(dt)`; weight decay in a slow task (worker).  
- **Config:** tables for node/link types; global multipliers; controller bounds.  
- **Tests:** verify half‑life per type; resume‑context scenario.

## 9) Success criteria
- Meets half‑life targets; reconstruction success after long gaps; stable ρ; no silent memory drift.

## 10) Open questions / future
- Sleep‑stage multipliers; learned per‑type schedules from telemetry; per‑relation‑subtype decay tables.
