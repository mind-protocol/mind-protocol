# PR Title

`<short summary> — [M## if applicable]`

## Context

* **Goal:** *what problem this PR solves (why now)*
* **Scope:** *what's included / what's explicitly out*
* **Specs:** links to relevant docs (e.g., `docs/v2/entity_layer/multi_scale_traversal.md#...`)
* **Issue/Task:** link to ticket(s)

---

## ✅ Design Conformance (Truths vs Myths)

* [ ] Entities = **neighborhoods** (functional/semantic); sub-entity = **active entity**
* [ ] **One** activation energy per node; **no** per-entity node energies
* [ ] Links **do not** store activation energy (transport only); `link.energy` = **affect** metadata
* [ ] **Stimuli inject activation**; **TRACE updates weights** (nodes/links), not activation
* [ ] Traversal is **two-scale** (entity wraps atomic); WM is **entity-first**
* [ ] No fixed thresholds/alphas; uses **z-scores / percentiles / half-life EMAs**

---

## 🧩 Code Changes (tick placement & behavior)

* [ ] Correct tick placement (Phase):
  * [ ] Stimuli → Node ΔE
  * [ ] Node thresholds → flips
  * [ ] **Entity aggregation** (energy/threshold/flip)
  * [ ] **Multi-scale traversal** (between, within)
  * [ ] **Learning** (boundary precedence, link & node weights, memberships)
  * [ ] **WM emit** (entity-first)
  * [ ] Decay

* [ ] **Entity bootstrap** (if applicable) runs **after graph load, before engine start**
  * [ ] Idempotent upserts (Entities, BELONGS_TO, seed RELATES_TO as per policy)
  * [ ] Membership normalization (Σ per node ≤ 1)
  * [ ] Centroids computed; OKLCH colors with hysteresis
  * [ ] Entity thresholds seeded; cache warmed
  * [ ] Emits summary metrics; **WARN if persisted=FALSE**

* [ ] WM entity-first selection implemented (greedy + diversity; token estimates via EMAs or TODO)
  * [ ] `wm.emit` includes `selected_entities`, `entity_token_shares`, `selected_nodes`

---

## 📡 Events (WS Contract)

* [ ] **No schema breaking changes** to existing events
* [ ] Emits (if applicable):
  * [ ] `entity.flip` (active flag, energy, theta)
  * [ ] `entity.boundary.summary` (`dE_sum`, `phi_max`, `z_flow`, `dominance`, `count`, `typical_hunger`)
  * [ ] `stride.exec` includes `src_entity` / `tgt_entity` and **actual** `ΔE`
  * [ ] `wm.emit` has entity fields
* [ ] Snapshot includes entity index (id/name/color/log_weight/energy/theta/active/members_count)

---

## 🧪 Tests

**Unit**
* [ ] Stimulus → node ΔE injection covers gap caps & health modulation
* [ ] Entity energy aggregation: `log1p` saturation & membership weights
* [ ] Boundary precedence math (γ, Π) with delivered ΔE and gap_pre
* [ ] WM selection: greedy order & diversity bonus

**Integration**
* [ ] End-to-end frame: node flips → entity flips → between/within strides → learning → WM emit
* [ ] Event payloads validate against JSON Schemas
* [ ] 0-entity cold start: bootstrap populates entities; WM includes ≥1 entity within 3 frames

* [ ] Test data updated (no per-entity node energies, no link activation buffers)

---

## 📚 Docs & Maps (generated + front-matter)

* [ ] Spec front-matter present/updated (id/title/owners/status)
* [ ] Specs referenced updated (or TODO noted with link)
* [ ] **Run docs generator** → no diffs:
  * [ ] `python scripts/gen_docs.py`
  * [ ] `git diff --exit-code docs/v2/_generated`
* [ ] ARCHITECTURE_MAP entry exists/updated for affected mechanisms (M##)
* [ ] SCRIPT_MAP entry updated for any service changes
* [ ] Observability contract (`ops_and_viz/observability_events.md`) reflects any new/changed fields

---

## 🔭 Metrics / Health / Ops

* [ ] New metrics (if any) registered (e.g., `entities.total`, `boundary.dE_sum`)
* [ ] Health checks unaffected or updated
* [ ] Log lines include **frame_id** and concise one-liners (bootstrap summary, WM selection counts)
* [ ] Config flags documented (e.g., `ENTITY_BOOTSTRAP_MODE=auto|required|skip`)

---

## 🧨 Risks & Mitigations

* [ ] No hot loops added (profiling notes, big-O consideration)
* [ ] Bootstrap idempotent; fail-fast in `required` mode
* [ ] Backpressure respected (stride budget remains time-based; no busy emission)

---

## ♻️ Rollback & Roll-forward

* **Rollback plan:** *how to turn feature off* (flag/branch revert)
* **Data impacts:** *entities created? migrations?*
* **Roll-forward:** *follow-up steps if partial* (e.g., enable persistence)

---

## ✅ Acceptance Criteria (observable)

* [ ] Within 3 frames after start with active nodes:
  * [ ] `entities.total > 0` metric
  * [ ] `wm.emit.selected_entities.length ≥ 1`
  * [ ] If cross-entity links occurred: `entity.boundary.summary.pairs.length ≥ 1`
* [ ] No schema validation errors in WS events
* [ ] CPU/memory within baseline ±20%

---

## 🔬 Smoke Test Steps (manual)

1. Start N1 engine + WS, point Iris to WS.
2. Trigger a stimulus (user message or test event) → confirm node flips.
3. Confirm `entity.flip` (or at least WM includes entities).
4. Confirm `wm.emit` lists entity IDs and token shares.
5. Trigger a cross-boundary stride (e.g., force integration gate) → confirm `entity.boundary.summary` beam.
6. Verify logs: bootstrap summary, entity counts, WM selection counts.

---

## Files Changed

* *list of key modules/specs/events touched*

---

## Reviewer Checklist (to be used by reviewers)

* [ ] Matches design pillars (section 0)
* [ ] Math & cohorts clearly specified (no fixed α/thresholds)
* [ ] Events compile with JSON Schemas; Iris contract honored
* [ ] Tests cover critical paths; generator outputs rebuilt
* [ ] Ops impact considered (metrics, flags, health)
* [ ] Rollback is feasible

---

## Post-merge Tasks (if any)

* [ ] Enable feature flag in staging/production
* [ ] Notify Iris team (entity beams now live)
* [ ] Add dashboard panel for `entities.total`, `wm.entities.selected`

---

<!--
Template Version: v2.1
Created: 2025-10-24
Author: Nicolas Reynolds (Mind Protocol Founder)
Purpose: Enforce v2 architecture conformance, operational readiness, and rollback planning
-->
