---
title: Glossary (v2)
status: draft
owner: @luca
last_updated: 2025-10-26
summary: >
  Canonical definitions to eliminate ambiguity across teams.
  See TAXONOMY_RECONCILIATION.md for normative terminology reference.
---

# Glossary

**Note:** This glossary uses the clean taxonomy defined in `TAXONOMY_RECONCILIATION.md`. For migration guidance from deprecated terms, see §3 of that document.

## Node
Atomic unit of knowledge in consciousness graph. ~1000 per citizen. Has dynamic activation energy (E), base_weight, decay_rate, and metadata. Nodes are connected by links and grouped into SubEntities. See `TAXONOMY_RECONCILIATION.md`.

## SubEntity
Weighted neighborhood of nodes discovered via clustering. **Scale A** of two-scale architecture. 200-500 per citizen. Tracks semantic/functional coherence. A first-class graph node with members (connected via MEMBER_OF edges with weights), centroid embedding, learned log_weight, and dynamic activation derived from member nodes. Examples: *consciousness_architecture* (semantic topic), *translator* (functional role). See `subentity_layer.md`.

## Mode
IFS-level meta-role emergent from COACTIVATES_WITH communities. **Scale B** of two-scale architecture. 5-15 per citizen. Examples: The Translator, The Validator, The Architect. Detected via Leiden community detection over COACTIVATES_WITH edges between SubEntities. See `emergent_ifs_modes.md`.

## Entity
**DEPRECATED.** Ambiguous term that conflated Scale A (SubEntity) and Scale B (Mode). Use **SubEntity** for weighted neighborhoods or **Mode** for IFS-level roles. See `TAXONOMY_RECONCILIATION.md` §3 Migration Guide.

## Scale A
SubEntity layer. Weighted neighborhoods (200-500 per citizen), semantic/functional clustering, supports retrieval and context formation. First-scale traversal routing.

## Scale B
Mode layer. IFS-level meta-roles (5-15 per citizen), emergent community detection over COACTIVATES_WITH, supports consciousness coordination and phenomenology. Higher-scale meta-patterns.

## Energy (E)
Dynamic activation mass on a node (≥0). Energy is **conserved under traversal** and is **only injected** by stimuli (reality). Threshold crossing makes a node active.

## Node weight (log_weight)
Slow, learned attractor strength of a node (anchors WM). Updated by: flip yield, gap-closure ROI, WM presence, TRACE reinforcement.

## Link energy (affect)
Static, author-declared **affective intensity** on the link (TRACE metadata). Not activation mass. Links **do not** store activation energy.

## φ (phi)
Gap-closure utility for a traversed link: the fraction of the target's pre-gap closed by the delivered ΔE. High φ = "this path actually recruited awareness".

## subentity energy
Aggregate of member node energies with saturation: \(E_{ent} = \sum_i \log(1+E_i) \cdot m_{i,ent}\). subentity threshold is cohort-based (μ + z·σ with health modulation).

## MEMBER_OF
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
- **organizational** (N2) - Organization Mind Protocol graph
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
