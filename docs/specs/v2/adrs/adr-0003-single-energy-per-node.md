---
title: Single Energy per Node
status: accepted
owner: @luca
last_updated: 2025-10-22
---

# ADR-0003: Single Activation Energy per Node

**Decision:** Nodes carry one dynamic activation energy E. TRACE updates weights only.

**Why:** Simplifies model, matches physics (energy conservation).

**Implementation:**
- Nodes: one E field (not per-subentity channels)
- Subentities: aggregate via membership weights
- Links: transport energy, store affect + telemetry (no activation buffer)
- TRACE: updates log_weight (nodes/links), does NOT inject activation
- Stimuli: ONLY source of activation injection

**False:** Per-subentity energy channels, link activation buffers, TRACE activation injection
