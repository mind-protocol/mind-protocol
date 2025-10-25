---
title: Glossary (v2)
status: draft
owner: @luca
last_updated: 2025-10-22
summary: >
  Canonical definitions to eliminate ambiguity across teams.
---

# Glossary

## Sub-entity
A first-class **neighborhood** node (functional role or semantic topic). Has members (nodes), a centroid embedding, a learned log_weight, and a **dynamic activation** derived from member nodes. "Active subentity" = sub-subentity (agent) this frame.

Dynamic activation mass on a node (≥0). Energy is **conserved under traversal** and is **only injected** by stimuli (reality). Threshold crossing makes a node active.

## Node weight (log_weight)
Slow, learned attractor strength of a node (anchors WM). Updated by: flip yield, gap-closure ROI, WM presence, TRACE reinforcement.

## Link energy (affect)
Static, author-declared **affective intensity** on the link (TRACE metadata). Not activation mass. Links **do not** store activation energy.

## φ (phi)
Gap-closure utility for a traversed link: the fraction of the target's pre-gap closed by the delivered ΔE. High φ = "this path actually recruited awareness".

## subentity energy
Aggregate of member node energies with saturation: \(E_{ent} = \sum_i \log(1+E_i) \cdot m_{i,ent}\). subentity threshold is cohort-based (μ + z·σ with health modulation).

## BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF")
Membership relation (Node → subentity) with weight ∈ [0,1]. Updated by co-activation (Hebbian), normalized per node.

## RELATES_TO
subentity → subentity relation with learned **ease** (flow EMA), **precedence** (causal credit), and **dominance** (directional bias).

## Working Memory (WM)
subentity-first selection of 5–7 **chunks** (subentities) with summaries + top members, within token budget.

## Criticality (ρ)
Spectral proxy for system health. Damp/boost stimulus budget and thresholds via a **learned monotone** function \(f(\rho)\).

## Surprise gating
Per-hunger gate = rectified z-score vs EMA baseline; drives both node-scale and subentity-scale valence.

## Scope
Routing level determining which graph database receives formations:
- **personal** (N1) - Individual citizen consciousness graphs
- **organizational** (N2) - Collective Mind Protocol graph
- **ecosystem** (N3) - Public ecosystem knowledge graph

## Bitemporal Tracking
Four timestamps on every node/link:
- `valid_at` / `invalid_at` - When fact was true in reality
- `created_at` / `expired_at` - When we learned/superseded knowledge

## Formation Trigger
How a node/link was discovered: `direct_experience`, `inference`, `external_input`, `traversal_discovery`, `systematic_analysis`, `spontaneous_insight`, `automated_recognition`, `collective_deliberation`.

## TRACE Format
Consciousness stream format that transforms autonomous thinking into persistent graph structure through:
- **Reinforcement mode** - Inline marking of existing nodes (useful/not useful)
- **Formation mode** - Structured declarations of new nodes/links with rich metadata
