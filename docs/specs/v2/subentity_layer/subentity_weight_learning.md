---
title: Subentity Weight Learning (MEMBER_OF)
status: stable
owner: @felix
last_updated: 2025-10-22
depends_on:
  - ../entity_layer/subentity_layer.md
  - ../ops_and_viz/observability_events.md
summary: >
  Learn soft memberships (MEMBER_OF.weight) from co-activation of nodes with
  subentities using rank-normalized signals and EMAs. Single log-weight per membership,
  one-speed updates, no dual fast/slow channels.
---

# Subentity Weight Learning (MEMBER_OF)

## 1. Context — What problem are we solving?

We need memberships that reflect **which nodes truly belong** to each subentity so that:
- SubEntity activation (read-out) is meaningful and stable,
- two-scale traversal has coherent within-SubEntity neighborhoods,
- WM chunks are representative—not noisy or bloated. :contentReference[oaicite:62]{index=62}

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **Node** - Atomic knowledge (~1000 per citizen)
- **SubEntity** - Weighted neighborhoods (200-500)
- **Mode** - IFS-level meta-roles (5-15)

When "entity" appears in this document, it refers to SubEntity (weighted neighborhoods) unless explicitly noted otherwise.

## 2. Mechanism (Design)

### 2.1 Single log-weight & one-speed updates

Each membership keeps a **single** `log_weight` updated from all evidence sources (no fast/slow channels). This mirrors the global “one-speed learning” invariants used elsewhere. :contentReference[oaicite:63]{index=63}

### 2.2 Evidence signals (rank-normalized)

- **Co-activation signal**: Node active (above \(\Theta_i\)) while SubEntity active (above \(\Theta_E\)) within a frame/window → update EMA.
- **WM presence**: SubEntity selected for WM with node among its top members → positive evidence.
- **TRACE reinforcement / formation quality**: when available, include as low-frequency but high-value signals (rank-z within SubEntity-type cohorts).
All signals convert to **rank-based z-scores** in appropriate cohorts before aggregation. :contentReference[oaicite:64]{index=64}

### 2.3 Update rule (conceptual)

\[
\Delta \log W_{iE} \;=\; \eta_{iE} \cdot \big(z_{\text{coact}} + z_{\text{wm}} + z_{\text{rein}} + z_{\text{form}}\big)
\]
with \(\eta\) from EWMA inter-update intervals (frequent updates → larger \(\eta\); rare → smaller), following the global step-size rule. :contentReference[oaicite:65]{index=65}

### 2.4 Gates

- **Sparsity gate:** encourage few strong memberships by applying L1-like pressure (periodic shrink toward 0 for the weakest memberships per node).
- **Novelty gate:** prefer evidence when the node's membership set is under-diversified to avoid "SubEntity creep".
These complement the *link* "newness gate" (frontier criterion) pattern used elsewhere, adapted to memberships. :contentReference[oaicite:66]{index=66}

### 2.5 Read-time normalization

For ranking members inside a SubEntity, standardize log-weights by SubEntity-type baselines (μ/σ); storage stays as plain `log_weight`. This keeps comparisons stable without mutating stored values. :contentReference[oaicite:67]{index=67}

## 3. Why this makes sense

### 3.1 Phenomenology

Belonging emerges from **repeated co-activation** while the SubEntity is active and relevant to WM/TRACE—mirrors how humans form tight associations to a topic or role. :contentReference[oaicite:68]{index=68}

### 3.2 Human bio-inspiration

Hebbian-like consolidation (co-activation) with slow decay; occasional “top-down” reinforcement when the topic dominates conscious output (TRACE/WM). :contentReference[oaicite:69]{index=69}

### 3.3 Systems dynamics

- Respects the **single-energy** substrate (membership learning reads activation; doesn’t add channels).  
- Plays nicely with **type-dependent decay** (memberships decay indirectly if unused via fewer co-activations over time). :contentReference[oaicite:70]{index=70}

## 4. Expected resulting behaviors

- SubEntities sharpen around **core** members (high standardized membership).
- Peripheral members fall away without recent co-activation.
- WM chunks list stable, representative top-k members with high **coherence**. :contentReference[oaicite:71]{index=71}

## 5. Why this over alternatives

- **Vs binary membership:** can't express graded belonging; brittle under noise.
- **Vs per-SubEntity energy buffers:** conflates activation with belonging; duplicates energy state; violates substrate rules. :contentReference[oaicite:72]{index=72}

## 6. Observability — how & what

**Events.**  
Emit `subentity.weights.updated` with **source** (“coact|wm|trace|form”), `log_weight_before/after`, `η`, and per-signal z-scores (mirrors node/link weight updates). :contentReference[oaicite:73]{index=73}  
Transport and snapshot semantics follow the WS viz contract. :contentReference[oaicite:74]{index=74}

**Meaningful dashboards.**
- Rising members per SubEntity (Δ log_weight rank).
- Membership sparsity & **coherence EMA** vs SubEntity size. :contentReference[oaicite:75]{index=75}

## 7. Failure Modes & Guards

- **SubEntity creep:** set minimum deltas + scheduled sparsification trims. :contentReference[oaicite:76]{index=76}
- **Collapsed variance (all members equal):** alert on near-zero σ for a given SubEntity-type. :contentReference[oaicite:77]{index=77}
- **Whiplash:** cap per-update \(|\Delta \log W|\) and use \(\eta\) schedule from inter-update intervals. :contentReference[oaicite:78]{index=78}

## 8. Integration points

- **Runtime:** `mechanisms/sub_entity_traversal.py` (when SubEntity flips / WM emission, update co-activation & WM signals). :contentReference[oaicite:79]{index=79}
- **Learning infra:** shared z-scoring cohorts & EWMA stores used by node/link weight learning. :contentReference[oaicite:80]{index=80}
- **Viz:** `subentity.weights.updated` routed via WS. :contentReference[oaicite:81]{index=81}

## 9. What success looks like

- For active SubEntities, top members stabilize (low churn) while tail remains plastic.
- WM summaries feel **on-topic**; boundary strides reflect coherent neighborhoods. :contentReference[oaicite:82]{index=82}

## 10. Open questions & future improvements

- When to **merge/split** SubEntities based on membership distributions (bimodality tests)? :contentReference[oaicite:83]{index=83}
- Learn SubEntity-specific **decay** of membership weights (currently uniform schedule).
