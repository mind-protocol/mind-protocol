---
title: Duplicate Node Merging (Single‑Energy + Bitemporal)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - learning_and_trace/14_duplicate_node_merging.md
depends_on:
  - foundations/bitemporal_tracking.md
  - core/models.md
  - adapters/storage/engine_registry.py
---

# Duplicate Node Merging (Single‑Energy + Bitemporal)

## 1) Context — Problem we’re solving
Formation and ingestion create **semantic duplicates** (same concept, different IDs/aliases). Duplicates fragment traversal and learning: activation spreads thin; weights and telemetry split; WM misses coherent chunks. We need a **safe, auditable merge** that preserves history, telemetry, and observability **without** violating the **single‑energy per node** substrate. :contentReference[oaicite:1]{index=1}

## 2) Mechanism — What it is
**Detect** near‑equivalents, choose a **canonical**, **redirect** structure, **consolidate** metadata/telemetry, and **record** the merge bitemporally.

**2.1 Detection (candidates)**
- Same type; high **embedding** similarity; normalized **name** similarity; overlapping **metadata/provenance**.  
- ANN index for scale; human veto lists (`NEVER_MERGE`). (Keep scorecard for explainability.)

**2.2 Canonical selection**
- Ties broken by **age→connectivity→standardized weight** (z‑W). Prefer the object with the richest lineage.  

**2.3 Consolidation rules (single‑energy substrate)**
- **Activation Eᵢ (runtime)**: choose `E_canon = saturate(E_a + E_b)` if merged live, or `max(E_a,E_b)` if merged during quiescence. Activation is **ephemeral**; the merge should **not** invent energy.  
- **Memberships m_{iS} (node→entity)**: `m_canon(S) = max(m_a(S), m_b(S))`, with optional Bayesian update when confidence is available.  
- **Links**: redirect all **incoming/outgoing** to canonical; if a parallel link exists, **combine** telemetry and keep the larger `log_weight` (or average in standardized space), preserving **EMAs** by sum‑weights.  
- **Names/aliases**: keep canonical `name`; store others in `aliases[]` for retrieval and UI; expose `merge_history[]`.

**2.4 Bitemporal lineage**
- Old versions’ `known_to` close; canonical gets a **new version id** with `supersedes=[vid_a,vid_b]`; merge event recorded with reason/scores. See **Bitemporal Tracking**. :contentReference[oaicite:2]{index=2}

**2.5 Safety timing**
- Prefer **low‑activity** windows (both E below threshold); otherwise, stage merge with gradual link weight interpolation to avoid flips.

## 3) Why this makes sense

### Phenomenology
After merge, a single concept feels **obvious and reachable**—activation and retrieval are no longer split among aliases.

### Bio‑inspiration
Memory consolidation unifies redundant traces into **stable engrams**.

### Systems‑dynamics
Single‑energy keeps physics clear; entity aggregation + link consolidation reduces fan‑out and stabilizes **ρ‑control**.

## 4) Expected resulting behaviors
- Higher **recall quality** (fewer misses); **shorter path lengths** to the concept; **cleaner WM** items.  
- Reduced compute (fewer near‑duplicates to traverse).  
- Better learning signals (telemetry no longer split).

## 5) Why this vs alternatives
| Alternative | Issue | Our approach |
|---|---|---|
| Hard delete one duplicate | Loses lineage/telemetry | Bitemporal supersession preserves history |
| Weighted soft‑alias only | Keeps fan‑out & confusion | Structural redirect + consolidation |
| Per‑entity energy merges | Violates single‑energy | Aggregate memberships; E remains scalar |

## 6) Observability — How & what to measure, and how to read it
**Events:** `node.merge{kept, absorbed[], scores, before/after_degree, before/after_zW}`; `link.redirect` entries for changed edges.  
**Metrics:** **Merge rate**, **false‑positive appeals**, **post‑merge retrieval lift** (MRR/Recall@k), **telemetry consolidation ratio** (flow EMA before→after).  
**Dashboards:** Before/after ego‑nets; drift of aliases; cohort‑level fan‑out reduction.

## 7) Failure modes & guards
| Risk | Why bad | Guard |
|---|---|---|
| False positive merge | Semantically different concepts collapse | High threshold + type match + veto list + human confirm for top‑impact merges |
| Energy spike | Live sum creates runaway | Quiescent scheduling; `E_canon=saturate(sum)`; cap deltas |
| Link duplication | Parallel edges explode degree | Merge parallel edges with **telemetry combine** |
| Silent lineage loss | Audit gaps | Bitemporal records + `merge_history[]` UI |

## 8) Integration in code
- **Where**: `adapters/storage/engine_registry.py` (canonical selection, redirects), `workers/maintenance.py` (periodic pass), `services/api` (manual review endpoints).  
- **APIs**: `POST /v1/graph/merge` with candidate pair + scores; emits `node.merge`.  
- **WM/Traversal**: No service imports service—merge is storage‑level; traversal sees canonical node next tick.

## 9) Success criteria
- 30–60% drop in alias collisions; measurable **recall@k** improvement; zero critical false merges over N weeks.

## 10) Open questions / future
- Learned merge threshold per **type/scope**; merge suggestion explanations; reversible “split” op.
