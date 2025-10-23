---
title: Deprecate Global Workspace doc as design driver
status: accepted
owner: @luca
last_updated: 2025-10-22
---

# ADR-0001: Deprecate Global Workspace Theory

**Decision:** Stop using Global Workspace Theory as architectural driver.

**Why:** Mismatch with actual WM implementation (token budgets, subentity-first selection).

**Now:** WM is subentity-first knapsack, detailed in entity_layer/entity_layer.md

**Supersedes:**
- 04_global_workspace_theory.md
- 12_workspace_capacity.md
