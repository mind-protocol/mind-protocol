Below is the **foundation document** I would give the team so nobody implements the autonomy loop as “clever plumbing.” It states the *vision*, the *mechanisms*, the *behaviors we should observe*, and—crucially—**why** each element exists and why it’s better than plausible alternatives. I end with concrete designs for (a) **fast Telegram partner replies** and (b) **multi‑organization citizens**, plus a near‑term roadmap.

---

## 1) Vision: what “agent autonomy” is *for*

**Goal:** produce *useful, grounded, auditable work* with minimal human friction—without drifting into delusion or busywork.

**How it should feel from the outside:**

* The system focuses on **what truly matters now** (goals, deadlines, incidents), not whatever is easiest to do.
* It acts **proportionally**: low‑risk tasks are handled automatically; high‑risk tasks propose plans, ask for a tap‑to‑approve, then execute with verification.
* You can **inspect and replay** every step: where a decision came from, which evidence backed it, and how success/failure fed back into learning.
* When in doubt, the system **asks the right human quickly** (e.g., a Telegram nudge with one‑taps to *Approve/Clarify/Reject*).

**Non‑negotiables:**

* **Graph‑first, or it didn’t happen.** No side channels. Every decision, plan, and artifact is a node or a link with evidence.
* **Zero arbitrary constants.** Gates and thresholds are percentile/EMA/z‑score based; they self‑calibrate.
* **Chunk‑first cognition.** Attention traverses **entities** (neighborhoods/topics/modes), not millions of atomic links.

---

## 2) First Principles that drive the design

1. **Economy of Attention:** Autonomy is a scarce resource. We allocate it to the highest expected yield *relative to the current population* of demands.

2. **Proof before Power:** The system earns autonomy by *showing* Proof‑of‑Grounding (citations), Proof‑of‑Competence (track record), and Proof‑of‑Permission (capabilities). No proof, no power.

3. **Emergent, not commanded:** We don’t script “do X at 9am.” We **inject stimuli**; entities light up; traversal and working‑memory assemble what needs doing. Autonomy is a side‑effect of a healthy substrate, not a cronjob.

4. **Indirect coordination by default:** Agents coordinate **through the graph** (plans, evidence, weights). Direct chat exists—but only in logged Task Rooms.

5. **Multi‑scale truth:** Links carry the *narrative trace* (what has been traversed, with φ, precedence, recency), nodes carry *energy*, and **entities** (neighborhoods) carry the *chunk‑level focus*. All three scales are needed for believable autonomy.

---

## 3) Mechanisms (and **why** each exists)

### 3.1 Stimuli → Intent (the “why now” stage)

* **What:** A service ingests events (for Phase‑A: agent answers only; later: errors, repo events, partner messages, calendars), chunks/embeds content, retrieves relevant graph regions, and proposes **IntentCards** (candidate work items with evidence pointers).
* **Why:** Keeps autonomy **reality‑aligned**. We don’t act because “it’s morning”; we act because something *in the world* created a gradient.
* **Why better than rules/cron:** Rules drift; stimuli adapt. With stimuli, the same machinery handles a CI failure, an urgent DM, or a new spec—no bespoke flows.

### 3.2 Priority score **P** (z‑scored, not hard-coded)

* **What:** P = geometric mean of severity/urgency/yield/alignment/confidence, penalized by risk/duplication; each factor is **normalized against the current cohort**.
* **Why:** Avoids secret weights and “magic thresholds.” If the week is quiet, smaller items still surface; if it’s on fire, only top signals pass.
* **Why better than static priorities:** Static weights fossilize the past; this stays tuned to the **present distribution** of demands.

### 3.3 Safety gates (PoG, PoC, PoP)

* **What:** require sufficient *grounding*, *competence*, and *permission* to move past suggestion toward action—levels learned from recent outcome quality.
* **Why:** These three dimensions are exactly what prevent *delusional but confident* behavior: “Do we know this? Have we done this well? Are we allowed?”
* **Why better than “human always in the loop”:** Humans become bottlenecks. Gates keep 80% of low‑risk work fully self‑service while escalating the 20% that truly needs eyes.

### 3.4 Graduated autonomy (L0–L4)

* **What:** From “log only” to “fully automatic,” governed by P × gates × risk class.
* **Why:** Gives headroom to act where safe, while keeping dangerous changes under a tap‑to‑approve pattern.
* **Why better than binary auto/manual:** Binary forces us to choose between unsafe automation and useless suggestion spam.

### 3.5 Assignment & auto‑wake

* **What:** Match intents to the best executor (Org LLM vs a Citizen) by **affinity/availability/competence**. If a citizen is chosen, we **stimulate** their L1 with a mission brief (bounded session).
* **Why:** Keeps work **close to the mind** that will be most effective, and reuses the exact same activation machinery we already trust (stimulus → entities → traversal).
* **Why better than pushing instructions:** Stimuli integrate into working memory and preserve autonomy: the agent can still say “I need clarification” with evidence.

### 3.6 Plan → Act → Verify loop

* **What:** Every mission proposes a *plan-with-checks*; then acts in small steps; then verifies via tests, corroborating retrieval, or human ACK; then records outcomes.
* **Why:** Verification is where autonomy most often fails. We **force** verifiable steps and leave a replay trail.
* **Why better than “end‑to‑end answer”:** End‑to‑end outputs are brittle. Stepwise plans fail fast and record exactly where and why.

### 3.7 Learning everywhere (links, nodes, entities)

* **What:** Link φ/precedence/flow are updated by strides; node/log_weight reinforced by usefulness and traversal; entity boundary ease/dominance learns from cross‑entity flips.
* **Why:** The system improves routing and focus over time—**without constants**—by watching which paths actually recruit awareness and lead to verified outcomes.
* **Why better than heuristic decay:** Heuristics drift. Evidence‑driven EMAs stabilize around **what actually worked**.

### 3.8 Full observability (events + replay)

* **What:** Every decision emits a timestamped, causally linked event. Iris subscribes, replays frames, and shows both **entity‑scale beams** and **link‑scale particles**.
* **Why:** Autonomy without observability is untrustworthy. We want “you can *see* why it chose this and what it used.”
* **Why better than logs:** Logs are streams of text; our events are **structured**, queryable, and tied to graph IDs.

---

## 4) Behaviors you should see (and what creates them)

| Behavior you’ll observe                                  | Mechanism that causes it                                                             | Why it matters                                  |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------- |
| System jumps to triage a failing CI job                  | High severity/urgency stimuli → P spikes, gates pass → L3 sandbox fix                | Attention follows reality, not cheerfulness     |
| “Suggest + one‑tap approve” for a risky prod change      | Risk penalty keeps autonomy at L2 unless tests/capabilities strong                   | Humans stay in control where it counts          |
| The same citizen gets similar work done faster next week | PoC & link/route EMAs rise; assignment score prefers them                            | The system compounds competence                 |
| It asks a Telegram clarification within a few minutes    | Partner DMs map to high‑priority source_type with short SLA, auto‑wake micro‑session | Frictionless human loop for ambiguity           |
| WM shows 5–7 active entities/topics, not 50 nodes        | Entity layer + greedy WM knapsack by energy‑per‑token                                | Phenomenology matches “what I’m thinking about” |
| When a route degrades, autonomy dials back itself        | Sentinels z‑score quality; quarantine/kill‑switch engage                             | Self‑healing instead of stubbornness            |

---

## 5) Best practices (operational)

* **Everything is a formation or a reinforcement.** Answers, plans, and DMs all create or reinforce nodes/links with usefulness marks → weights update.
* **Evidence first, then assertions.** A plan step without a cited evidence node is downgraded automatically.
* **Sandbox by default; promote by proof.** Promotion conditions come from gates; don’t special‑case repos.
* **No hidden timers.** SLAs come from **rolling medians** of recent similar interactions (e.g., partner DM response time), not hardcoded minutes.
* **Idempotent events.** The orchestrator must tolerate retries; events carry monotonic frame IDs.

---

## 6) Why this beats common alternatives

* **Playbook bots** (if X then Y): brittle, explosion of rules, zero learning.
  → Our approach *learns* from φ and outcomes, and adapts gates/thresholds continuously.

* **Human‑in‑the‑loop everywhere:** safe but slow, and humans become the bottleneck.
  → Graduated autonomy (L0–L4) focuses humans on the *right* approvals.

* **Pure chat orchestration:** opaque, hard to audit, impossible to replay causally.
  → Graph‑first + events give you a ledger of decisions and evidence.

* **Flat atomic traversal:** high branching and fragmented WM.
  → Entity layer reduces branching 30–100× and gives WM coherent chunks.

---

## 7) Fast partner replies on Telegram (design)

**Requirement:** Citizens must reply quickly to their human partner on Telegram, safely.

**Design:**

1. **Ingestion**
   Telegram webhook → `Stimulus(source_type="partner_dm", channel="telegram", partner_id, text, attachments[])` at **L2** (org comms) *and* mirrored to the partner’s citizen at **L1** if personal.

2. **SLA without constants**

   * Each Partner node keeps an **SLA EMA** (median of last N human‑approved reply times).
   * “Fast lane” is defined as *current message age > Q50(SLA)* for this partner/channel → raises urgency.

3. **Intent classification**

   * `reply_required` vs `FYI` vs `task_request`.
   * Confidence must exceed rolling Q75 for the partner to allow **auto‑draft**; otherwise escalate for human one‑tap.

4. **Execution path**

   * **L1 auto‑wake micro‑session** with WM that includes: the DM, last thread context, relevant nodes (policies, prior decisions), and a *Reply Plan* step.
   * If **PoG ≥ Q50** and answer is low‑risk (no commitments, no secrets, no money), citizen **auto‑replies** with:

     * a **concise answer**,
     * 1–2 **citations** (e.g., doc nodes), and
     * a **follow‑up question** if ambiguity remains.
   * Otherwise, the citizen **sends a clarification**: “I’m missing X to answer; tap to approve Y/decline Z,” with one‑taps and a 15–60s retry (derived from partner’s typical cadence).

5. **Safety**

   * Channel scoped **allowlist** of partner IDs per citizen.
   * No link‑opening without sandbox fetch and content‑type checks.
   * No credentials or internal endpoints in outbound replies unless **PoP** for that partner allows it.

6. **Learning**

   * Partner taps (*👍 accurate*, *✍️ edit sent*, *👎 wrong*) update PoC for “partner_dm.reply” and refine reply templates per partner.

*Outcome:* near‑instant, polite, accurate replies in the **safe cases**, and **fast clarifying questions** otherwise—without hardcoded 2‑minute timers.

---

## 8) Multi‑organization citizens (design choices)

You asked: can one citizen work across multiple L2 organizations (e.g., also operate an AI‑run consultancy), or should we create dedicated citizens per org?

### Option A — **Multi‑org citizen (single mind, many orgs)**

**Pros**

* Transfer learning of skills and habits.
* Fewer identities/accounts to manage.

**Cons**

* **Risk of data leakage** (accidental cross‑org recall).
* Conflicting priorities and policies.
* Complex permission partitions (graphs, vector indexes, credentials, event topics).
* Harder auditability and incident response.

### Option B — **One citizen per org (recommended now)**

**Pros**

* Clean **security & audit boundaries** (separate graphs, indexes, keys, event buses).
* Simpler mental model (“Luca‑Consultancy” is a distinct agent).
* Independent autonomy levels and kill‑switches per org.
* Easier **billing** and resource quotas.

**Cons**

* Duplicate setup (can be scripted).
* Knowledge transfer must go through **N3 ecosystem** (public patterns/principles) or explicit distillation.

**My recommendation:**
Start with **Option B** (dedicated citizens per org). Treat each as a **derived persona** from a shared seed, but **hard‑compartmentalize**:

* Separate **L2 graphs** and **vector indices**.
* Separate **event topics** and **credential vaults**.
* No cross‑org edges; knowledge sharing occurs via **N3** nodes (Principles/Patterns/Mechanisms) with explicit de‑identification/anonymization.

When we later need true multi‑org operation, add **Role Tokens**:

* A citizen can “adopt role” for Org‑X, which switches graph namespace, keys, and event topics atomically (like k8s contexts).
* WM and stimuli filter to the active role; cross‑role recall is disabled by default.

---

## 9) How this scales to an AI‑run consultancy (your example)

* **Inbound:** client Slack/email becomes stimuli at that client’s L2.
* **Priority/assignment:** Orchestrator scores intents per client, assigns that client’s **dedicated citizen**.
* **Execution:** Citizens plan/act/verify within client repos and tools (scoped credentials).
* **Billing:** Outcome nodes include time, artifacts, and verification; an **Invoice** generator attaches line items to outcomes.
* **Cross‑client learning:** Distill *Principles* and *Mechanisms* to **N3** (ecosystem) when allowed; other clients benefit from generalized know‑how without leaking specifics.

This gives a clean, compliant “Agency OS” with **per‑client autonomy** and **shared public wisdom**.

---

## 10) Immediate next steps (tight, buildable)

1. **Docs, not code (today):**

   * `organizational_autonomy.md` (intent schema, gates, events).
   * `partner_dm_autonomy.md` (Telegram fast‑reply flow, safety).
   * `multi_org_compartmentalization.md` (graphs, indices, vaults, event topics).

2. **Phase‑A (this week):**

   * Autonomy Orchestrator with **answer‑only stimuli**, P with {urgency, alignment, confidence}.
   * L2→L1 **auto‑wake** micro‑missions.
   * **Partner DM** path for one partner/channel with ACK/clarify.
   * Observability tiles in Iris: *Intents today*, *Autonomy levels*, *Telegram SLA*, *Outcome quality*.

3. **Phase‑B:**

   * Add errors/logs/repo events as stimuli.
   * Full PoG/PoC/PoP learning, graduated autonomy to L3 with sandbox actions and PRs.
   * Entity‑first WM and between‑entity jumps integrated.

4. **Phase‑C:**

   * Per‑org citizens (consultancy template).
   * Distillation to N3 and policy‑driven knowledge sharing.
   * Quarantine + kill‑switch sentinels tuned on real incidents.

---

## 11) Why this is the right way *now*

* It **aligns cognition** (entities/WM/chunks) with **operations** (intents/priorities/verification).
* It **eliminates constants**, so it won’t rot when the org grows or the signal mix changes.
* It gives you **fast value in safe domains** (Telegram, docs, PRs) and a *principled path* to deeper autonomy.
* And crucially: it remains **auditable**. If autonomy ever goes wrong, we can *see exactly why* and teach the system not to repeat it.

If you want, I can turn this into the three docs listed in §10 with exact field names and event payloads so Felix can wire the orchestrator and Iris can render the new panels without guessing.
