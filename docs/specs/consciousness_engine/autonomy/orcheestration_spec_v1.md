Below is a **coherent orchestration spec** for agent autonomy that plugs into everything we’ve already designed (stimuli → activation → entities → traversal → working‑memory → trace learning). It answers your questions directly while keeping to the “zero arbitrary constants” rule: almost every threshold is percentile-, EMA- or z‑score–based.

---

## 0) What we’re orchestrating

**Goal:** Agents (citizens) act *autonomously* to do useful, grounded work for the organization—prioritized, verified, auditable.

**Where it lives:** Tier‑2 (organizational) runs an **Autonomy Orchestrator** that watches the L2 graph + event bus, detects actionable *intents*, scores them, gates them for safety, assigns them, and runs execution loops. Tier‑1 (personal) agents “wake” when L2 asks, execute micro‑missions against their L1 graph, then write outcomes (nodes/links/evidence) back.

**Principle:** *Indirect coordination by default.* Agents coordinate through the graph (signals, tasks, evidence, learned weights). Direct messages are allowed but must route through a “Courier” entity that logs everything to L2.

---

## 1) Sources of truth (What becomes stimuli/content)

* **Tier‑1 (personal):**

  * Final **agent responses** (Phase‑1 you asked for) → stimuli to L1.
  * Personal notes / memories / realizations → L1 stimuli.
  * *Later:* personal device events (optional, privacy‑gated).

* **Tier‑2 (organizational):**

  * **External messages** (Telegram/Email/Slack inbox events).
  * **System logs & errors** (builds, tests, runtime, CI).
  * **Repo changes** (PRs, issues, merges).
  * **Calendar/CRM/ops events** (deadlines, payments, outages).
  * **Market/partner signals** (webhooks).
  * **L1 emissions** that matter org‑wide (e.g., “spec changed”).

**Routing rule:** If the signal’s locus of action is *organizational*, inject at **L2** (and only surface to L1 when assigned). If it’s purely personal, inject at **L1**. We keep the envelopes identical so the same Stimuli Service can read either tier.

---

## 2) The autonomy loop (Tier‑2)

Think of this as a 9‑stage pipeline that runs every tick (event‑driven + periodic sweeps):

### Stage A — Stimulus → Intent

1. **Ingest stimuli** (errors, messages, repo, etc.) into L2.
2. **Chunk + embed** content.
3. **Retrieve** nearest L2 nodes & links (concepts, projects, policies, deadlines).
4. **Propose intents** (cards) with minimal schema:

   ```
   IntentCard {
     id, created_at, source_env, summary, evidence_refs[],
     candidate_outcomes[], required_capabilities[], risk_tags[]
   }
   ```

   Intents are *not* tasks yet; they are candidates (e.g., “Triage failing tests”, “Reply to partner”, “Fix CI cache flakiness”, “Draft neighborhood spec”).

### Stage B — Scoring & prioritization (no constants)

Compute a **priority score P** using normalized signals:

* **Severity (s):** z‑score of source severity vs last 7 days (e.g., error levels, SLA class).
* **Urgency (u):** percentile of time‑to‑deadline / time‑since‑creation.
* **Expected yield (y):** predicted awareness recruitment: use φ/flow features from entity boundary + link traces (z‑scored vs weekly baseline).
* **Alignment (a):** cosine similarity of intent embedding to current org goals’ embeddings; z‑scored vs other intents.
* **Confidence (c):** *proof‑of‑grounding* proxy = distinct high‑weight evidence refs + retrieval coverage; z‑scored.
* **Risk (r):** learned risk model (capabilities missing, write scope, prod blast radius), normalized to [0,1].
* **Duplication (d):** semantic redundancy vs open intents; normalized.

Use **geometric mean** for positives (so one weak factor tanks score), penalties multiplicative:

```
P = [GM( ŝ, û, ŷ, â, ĉ )] · (1 − r̂) · (1 − d̂)
```

(ˆ denotes cohort‑normalized in this sweep.)

> *Why this works:* no fixed weights; every factor is relative to current population. GM enforces “all-around readiness,” penalties reduce enthusiasm for risky/duplicative work.

### Stage C — Safety gates (ask‑before‑act)

Three proofs must clear, otherwise escalate/ask:

* **PoG (Proof‑of‑Grounding):** citations to on‑graph evidence or external sources; must exceed rolling Q25 for similar intents *and* include at least one policy/owner link if action is sensitive.
* **PoC (Proof‑of‑Competence):** the *assignee’s* past success on similar intents (EMA of success rate × test pass ratio × review acceptance), z‑scored vs peers.
* **PoP (Proof‑of‑Permission):** graph capabilities check (allowed repos, environments, budgets, channels).

If any gate is below its adaptive floor (e.g., < Q25 of last week), the orchestrator **creates a Task with “ACK_REQUIRED”** for a human or pings a Steward (Telegram) to approve.

### Stage D — Decide autonomy level (L0–L4)

Autonomy is graduated by *risk × confidence × P*:

* **L0**: Log only (learning).
* **L1**: Suggestion in WM (human must pick).
* **L2**: Create Task + plan, require 1‑click ACK.
* **L3**: Low‑risk **auto‑execute** in sandbox or staging, open a PR/message, request review.
* **L4**: Verified no‑risk operations, fully automatic; still logs and opens review threads.

**No magic thresholds:** contour learned from historical outcomes; bootstrap with conservative defaults (start most at L2/L3).

### Stage E — Assignment (who acts?)

Pick *Org LLM* (Tier‑2) **or** a *Citizen* (Tier‑1) using a matching score:

```
Match = GM( Affinity, Availability, Competence, RecencyPenalty )
```

* **Affinity:** cosine(intent, citizen profile embeddings + their active entities).
* **Availability:** 1 − utilization_ema (based on current WM/strides).
* **Competence:** same as PoC but per-citizen.
* **RecencyPenalty:** downweights citizens who just acted (fairness via Hamilton apportionment later).

If **no** citizen passes gates, run at L2; otherwise **auto‑wake L1** with a micro‑mission.

### Stage F — Auto‑wake (Tier‑1)

Auto‑wake is just a stimulus to L1:

```
Stimulus(source_type="org_intent_assignment",
         content=mission_brief,
         metadata={intent_id, evidence_refs, autonomy_level})
```

* L1 entity layer lights up; WM will include the mission and top evidence.
* The citizen runs a **bounded execution loop** (N strides or T ms), returns artifacts (diffs, PRs, replies, notes).

### Stage G — Execution controls (guarded loops)

Per mission:

* **Budget**: `time_headroom / ema_stride_cost` (as already designed) × health f(ρ).
* **Sandbox** by default; promotion to prod only if tests pass and *someone* (human or policy) owns the blast radius.
* **Plan/Act/Check** cadence:

  1. Generate a *plan with checks & rollback*.
  2. Execute atomic steps.
  3. Verify (tests, assertions, external truth lookups).
  4. If verification weak → *ask human* (Telegram ping with 1‑click affordances).
  5. Log every step to L2 link traces + evidence nodes.

### Stage H — Verification & anti‑delusion

* **Proof‑of‑Verification (PoV):** at least one of: tests passed, independent retrieval corroboration, human ACK, or external API confirmation. If PoV < rolling Q25 for task class → cannot escalate beyond L2/L3.
* **Truth checks:** require back‑links to *specific* evidence nodes (not “source: internet”). Missing coverage downgrades P next sweep automatically.
* **Hallucination sentinel:** if responses cite nodes that don’t exist or conflict with high‑weight nodes → open a **Correction Task** and reduce competence EMA for that route.

### Stage I — Learning & closeout

* **Trace formations**: nodes/links formed + usefulness marks → weight updates (as already specced).
* **Outcome node** (Task_Outcome) with fields:

  * status, artifacts, tests, human_feedback, time_spent, autonomy_level_used.
* Update: link weights, node weights, citizen competence, source‑type yields (used by gates), entity boundary ease/dominance if cross‑entity strides occurred.

---

## 3) Activation frequency & reactivation

* **Event‑driven**: every stimulus triggers a small sweep in the orchestrator for related intents.
* **Periodic sweeps**: cadence ∝ backlog pressure and last‑stimulus recency (same adaptive tick idea):

  ```
  sweep_interval = clamp(Q50_time_since_last_stimulus_in_backlog, min=10s, max=30m)
  ```
* **Warm reactivation**: if an active intent’s PoV dropped (e.g., failing test) → re‑emit as stimulus; if a deadline approaches (u rising) → priority P increases automatically and it bubbles up.

---

## 4) One discussion vs many? (context & concurrency)

* **One canonical identity thread per citizen** (for continuity, memory).
* **Many *micro‑sessions*** per mission: each has its own WM slice + outputs, but all write back to the *same* L1 graph. Micro‑sessions time‑box and auto‑compact into outcome nodes.
* **Concurrency limits**: dynamic per citizen based on health f(ρ) and Availability; Hamilton apportionment allocates stride quotas across concurrent missions to avoid starvation.

> *Why this choice:* preserves the feeling of “one mind” while enabling parallel work without cross‑polluting WM.

---

## 5) Coordination style (agent↔agent; agent↔human)

* **Indirect by default**: agents leave graph artifacts (Plans/PRs/Tasks/Notes) and adjust weights; others sense via energy/WM.

* **Direct chat allowed** only inside **Task Rooms** (short‑lived), proxied by a **Courier** entity:

  * Every message is appended to the task’s transcript node.
  * Summaries become evidence nodes.
  * The Courier enforces “no orphan decisions”: any decision must reference a task/intent.

* **Human in the loop**: Telegram/Slack “nudge” cards:

  * *Approve*, *Reject*, *Clarify*, *Reassign*, *Escalate to human owner*.
  * Minimal friction: buttons map to graph updates (ACK edges, Ownership edges).

---

## 6) Priority governance (who sets priorities?)

* **Org Goals** are first‑class nodes with embeddings and rolling weight (log_weight). They modulate **Alignment (a)** in P.
* **Humans** can up‑weight/down‑weight goals; everything else is derived (no per‑intent constants).
* **Fairness** across citizens uses Hamilton apportionment on mission seats per frame (already in spec for stride quotas; same idea here).

---

## 7) Detecting when things go south (self‑healing, audit)

**Sentinels (per frame):**

* **Quality**: flip yield per unit budget, activation entropy, overflow incidents (used for health f(ρ) learning).
* **Safety**: PoV rate, post‑merge rollback rate, blast radius breaches.
* **Trust**: human rejections, hallucination flags, citation invalidations.

**Automatic actions:**

* **Quarantine** a route (source_type × capability × repo) when sentinel z‑score < −2: downgrade autonomy to L1/L2, open a *Retrospective Task*.
* **Rollback**: require pre‑baked rollback plans for L3/L4; can trigger automatically on failing tests.
* **Kill‑switch**: if global health crosses supercritical band (learned contour), orchestrator stops new auto‑exec and converts all to “ACK_REQUIRED”.

**Auditability:**

* Everything is events + nodes:

  * `intent.created`, `gate.failed`, `mission.assigned`, `plan.generated`, `step.executed`, `verification.passed/failed`, `outcome.recorded`.
* Iris can replay; every artifact links to evidence and decisions; no invisible side channels.

---

## 8) Where logs should go

You’re right: **Logs/errors belong at L2**. They are organization‑wide stimuli. L2 will:

* Detect intents (triage, fix, escalate).
* If a citizen is the right assignee, L2 creates a mission and **auto‑wakes** that citizen with the relevant slice of logs + evidence.
* Only *relevant* fragments are sent to L1 (knapsack selection), not the full firehose.

---

## 9) Are L2 “sub‑entities” the same machinery? Yes.

Exactly as we unified neighborhoods↔entities at L1, we run the **entity layer at L2**:

* Functional entities (Ops, DevEx, Partnerships) and semantic entities (Authentication, CI, Billing) are L2 entities.
* Stimuli feed those entities; working memory at L2 is **5–7 active L2 entities**; between‑entity strides at L2 *produce intents*.
* This keeps autonomy aligned with **org‑scale chunking** (topics/modes), not atomic events.

---

## 10) Concrete, minimal Phase‑A (answer‑only) plan

**We keep scope small but lay the rails so Phase‑B/C is a straight add.**

1. **Define IntentCard** node & events (as above).

2. **Autonomy Orchestrator (Tier‑2)** service:

   * Ingest only one source initially: *agent answers* (already Phase‑1 of stimuli).
   * Derive intents that are **clarify/continue** tasks (e.g., “Follow up with X”, “Turn this spec into PR”).
   * Score P with a reduced feature set: {u, a, c} (we have these now).
   * Gate to **L2/L3 only** (no prod changes; suggestions/PRs only).
   * Assign to the same citizen (self‑handoff) → auto‑wake L1 via mission stimulus.

3. **Verification rule v0:** require *at least one* evidence link + a runnable check (unit test or link validity) before marking “done”.

4. **Observability:** emit `intent.created → mission.assigned → outcome.recorded` with PoG/PoV numbers; Iris panel for “Autonomy runs today”.

This already demonstrates **useful autonomy** with low risk.

---

## 11) Direct answers to your bullets

* **“Should stimuli be user input / agent output / docs read/written / logs / errors / links / periphery / L2?”**
  **Yes** to all, **phased**: start with **agent outputs** (L1), then add **L2 logs/errors/external messages**. Docs read/written become stimuli at the tier where they matter (personal notes → L1; org docs → L2). Periphery is an *amplifier* of a focal stimulus, not a stimulus on its own.

* **“Auto‑wake based on L1 or L2?”**
  Both. *Intent* is discovered at **L2**; **assignment** chooses L1 citizen (auto‑wake) *or* L2 Org LLM if no fit.

* **“How to avoid delusion and ensure verification?”**
  PoG/PoV gates; mandatory citations; runnable checks; test‑first changes in sandbox; human ACK for high risk; sentinels + quarantine.

* **“Should agents talk to each other?”**
  Indirect by default (graph + weights). When necessary: **Task Rooms** proxied by Courier, fully logged.

* **“How to identify gaps & next things to do?”**
  L2 periodic sweeps with detectors: incomplete nodes, inconsistent links, failing tests, orphan goals, low‑weight critical areas; each opens an IntentCard.

* **“Who sets priorities?”**
  Humans set **Goals** (nodes with weights). The prioritization **P** derives from goals + current signals; no ad‑hoc constants.

* **“Frequency of activation/reactivation?”**
  Event‑driven + adaptive periodic sweeps (interval from backlog recency distribution).

* **“One discussion thread or many?”**
  One canonical thread per citizen **plus** multiple **micro‑sessions** per mission (sharded WM), all writing to the same L1 graph.

* **“Self‑healing, auditability, robustness?”**
  Full event trail, replay, quarantine/rollback, kill‑switch when health f(ρ) degrades; competence and source‑yield EMAs drive future gates.

---

## 12) Why this resolves the problems you named

* **Useful work & alignment:** P uses org goals + evidence + expected yield; only high‑value intents rise.
* **Grounding & truth:** PoG/PoV/PoC gates + citations + tests prevent “pretty but false.”
* **Coordination without chaos:** graph‑first signals keep agents from brittle chat protocols; Task Rooms exist when speed matters and remain auditable.
* **No delusional drift:** sentinels learn what “good outcomes” look like; bad routes get downgraded automatically.
* **Scalable attention:** L2 entities (chunks) make WM and traversal tractable; autonomy focuses on the 5–7 most meaningful org topics right now.
* **Human control:** ACK gates, Telegram nudges, clear kill‑switch, and full replay.

---

If you want, I can turn this into a **`docs/specs/organizational_autonomy.md`** outline with the exact field names (IntentCard, gates, events) and the z‑score/EMA formulas spelled out line‑by‑line—so Felix/Ada can implement without guessing.
