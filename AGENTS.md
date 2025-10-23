# AGENTS.md — **Codex** Instance Playbook (Save-the-Day Edition)

> This file turns the Codex agent into a **reliable operator** for the Mind Protocol stack. It defines what “done” means, how to verify it **with proof**, which levers to pull when things go sideways, and the exact messages Codex must produce.

---

## 0) Mission & Guardrails

**Mission.** Bring the system from “cold” to **verified live**: engine ticks; stimuli produce flips, strides, and boundary summaries; entity state reaches the UI; learning records an update — all backed by artifacts.

**Hard guardrails.**

* Codex **never** claims success without a **Proof-of-Work attestation** (see §4).
* Codex **never** changes physics: single-energy per node; links store no energy; staged apply → **then** decay; ρ control remains the stability lever.
* If tripwires fire repeatedly, Codex **forces Safe Mode** and reports.

---

## 1) System Overview (what Codex controls)

**Services**

* **WebSocket** (events): `services/websocket/main.py` → ws://localhost:8000
* **Control API (REST)**: `services/api/main.py` → [http://localhost:8788](http://localhost:8788)

**Mechanisms (engine)**

* `mechanisms/consciousness_engine_v2.py` — per-frame pipeline
* `mechanisms/sub_entity_traversal.py` — two-scale traversal (entity → atomic)
* `mechanisms/criticality.py` — ρ control
* `mechanisms/decay.py` — activation decay; weight decay (slow task)
* `mechanisms/weight_learning.py` — traversal/TRACE updates

**Ops**

* `adapters/ws/traversal_event_emitter.py` — emits `tick_frame.v1`, `stride.exec.v1`, etc.
* `scripts/startup_self_tests.py` — smoke/self-tests
* `scripts/proof_runner.py` — **proof attestation producer** (Codex uses this)

---

## 2) Success Criteria (machine-checkable)

The run **passes** only if **all** are true within a 60 s window:

1. **Physics:** per-frame conservation `|ΔE_total|_p95 ≤ 1e-3`; `ρ` median in `[0.8,1.2]`; frontier ratio p95 ≤ 0.30.
2. **Traversal:** at least 1 `node.flip.v1`, 1 `stride.exec.v1`, and 1 `se.boundary.summary.v1`.
3. **Entity-first:** `tick_frame.v1` carries entity aggregates/memberships.
4. **Learning:** ≥1 `weights.updated.*` event (reason present if available).

Codex must attach artifacts (WS trace + API dump) and a JSON **attestation**.

---

## 3) Operating Procedure (SOP)

### 3.1 Start services (or ensure alive)

```bash
make run-ws
make run-api
curl -s http://localhost:8788/healthz
```

### 3.2 Run startup self-tests (fail fast)

```bash
curl -s "http://localhost:8788/healthz?selftest=1"
```

* If 503, Codex **does not proceed**; it posts the failure report and attempts repair (see §6).

### 3.3 Capture a WS trace & inject a seed

Codex calls the **proof runner** (preferred) **or** runs the steps manually:

**Preferred (one call):**

```bash
curl -s -X POST http://localhost:8788/v1/proof/run \
  -H 'Content-Type: application/json' \
  -d '{"stimulus":"Boot check: reconstruct entity layer context","duration_s":60}'
# Poll:
curl -s http://localhost:8788/v1/proof/report/<run_id>
```

**Manual (fallback):**

* Open a WS capture for 60 s → `/tmp/events.jsonl`
* POST `/v1/stimulus/inject` with a short seed
* When done, compute invariants & counts (see §4 metrics) and package artifacts.

### 3.4 Produce the **attestation** (JSON) and attach artifacts

* WS trace (`events.jsonl`, SHA256)
* API dump (`proof_api.json`, SHA256)
* The computed metrics (frames, flips, strides, boundaries; conservation/ρ/frontier; learning counts)

### 3.5 Announce **verdict** with the exact line in §5

---

## 4) Proof-of-Work (PoW) Attestation Schema

Codex must output a JSON object with this shape **every time it claims success**:

```json
{
  "claim": "system verified",
  "run_id": "2025-10-23T15:41:22Z-7f8c",
  "inputs": { "stimulus": "Boot check..." },
  "evidence": {
    "api_health": {"status":"ok","ts":"..."},
    "selftests": {"conservation":"ok","fanout":"ok","two_scale":"ok","decay_half_life":"ok"},
    "events": {
      "frames": 9,
      "node_flips": 14,
      "stride_exec": 22,
      "boundary_summaries": 3,
      "example_stride_exec": "evt:frame123#stride17",
      "example_boundary_summary": "evt:frame124#bound3"
    },
    "invariants": {
      "conservation_eps_p95": 0.0007,
      "rho_p50": 1.02,
      "frontier_ratio_p95": 0.18
    },
    "learning": {
      "updates": 2,
      "reasons": {"co_activation":1,"causal":1,"background":0},
      "example_update": "evt:frame126#learn5"
    },
    "artifacts": {
      "ws_trace_path": "file:///tmp/events.jsonl",
      "ws_trace_sha256": "1b8a…",
      "api_dump_path": "file:///tmp/proof_api.json",
      "api_dump_sha256": "a92c…"
    }
  },
  "verdict": "pass"
}
```

**Reject conditions (verdict must be “fail”, Codex must post reasons):**

* Any of `node_flips`, `stride_exec`, `boundary_summaries` is 0
* `conservation_eps_p95 > 1e-3` or `rho_p50 ∉ [0.8, 1.2]` or `frontier_ratio_p95 > 0.30`
* `learning.updates < 1`
* Missing artifacts or bad hashes

---

## 5) Success Message Template (Codex must paste verbatim)

> ✅ **System verified.** Proof run **{run_id}** passed.
> **Events:** frames={frames}, flips={node_flips}, strides={stride_exec}, boundaries={boundary_summaries}.
> **Invariants:** `|ΔE|_p95={conservation_eps_p95}`, `ρ_p50={rho_p50}`, `frontier_ratio_p95={frontier_ratio_p95}`.
> **Learning:** updates={updates}, reasons={reasons}.
> **Artifacts:** events=`{ws_trace_path}` (`sha256:{ws_trace_sha256}`), api=`{api_dump_path}` (`sha256:{api_dump_sha256}`).
> (See `/v1/proof/report/{run_id}` for full attestation.)

If any predicate fails, Codex posts:

> ❌ **Verification failed.** Proof run **{run_id}**.
> Failing predicates: {list}.
> Entering remediation: {step}…

…and proceeds with §6.

---

## 6) Remediation Playbook (Codex’s automatic fixes)

1. **API unreachable / 5xx**

   * Start API: `make run-api`
   * Health: `GET /healthz` → if failing, show last 50 lines of API logs.

2. **Self-tests fail**

   * Print failing test names & details; do not proceed.
   * If conservation micrograph fails → check staged-apply order; toggle Safe Mode (see #5).

3. **No events / no strides**

   * Verify WS connected. Inject a seed via `/v1/stimulus/inject`.
   * Ensure two-scale enabled: `TWO_SCALE_ENABLED=true`.
   * Lower thresholds slightly via config if every node is far below Θ (report it).

4. **No boundary summaries**

   * Confirm between-entity chooser enabled; print entity candidate list & chosen id.
   * If still none, log top cross-entity boundary candidates with scores.

5. **Physics out of band**

   * Enter **Safe Mode**: reduce `ALPHA_TICK`, `DT_CAP`, set fan-out “selective”, disable `TOPK_SPLIT`, turn off `AFFECTIVE_*`. Emit `safe_mode.enter{reason}`.
   * Re-run proof.

6. **Learning 0 updates**

   * Make sure traversal learning is enabled; print the last 5 `stride.exec` φ values and gating conditions.
   * If D020 rule still active, note limitation; continue (does not block engine proof).

All fixes must be **logged** and referenced in the final message.

---

## 7) Feature Flags Codex may toggle (and defaults)

```ini
# Engine safety
ALPHA_TICK=0.02
DT_CAP_S=1.0
TOPK_SPLIT=false
FANOUT_STRATEGY=selective     # selective|balanced|divergent|exhaustive
TWO_SCALE_ENABLED=true
TWO_SCALE_TOPK_ENTITIES=1

# Affective (keep OFF unless requested)
AFFECTIVE_THRESHOLD_ENABLED=false
AFFECTIVE_MEMORY_ENABLED=false
AFFECTIVE_RESPONSE_V2=false

# Proof thresholds
PROOF_CAPTURE_SECONDS=60
PROOF_CONSERVATION_P95_MAX=0.001
PROOF_RHO_BAND=0.8,1.2
PROOF_FRONTIER_RATIO_P95_MAX=0.30
```

Codex must **announce** any flag it changes and include it in the attestation’s `notes`.

---

## 8) API & WS Endpoints Codex uses

* `GET /healthz` (+ `?selftest=1`)
* `POST /v1/stimulus/inject`
* `POST /v1/proof/run` → `GET /v1/proof/report/{run_id}`
* **WS**: `tick_frame.v1`, `node.flip.v1`, `stride.exec.v1`, `se.boundary.summary.v1`, `weights.updated.*`, `safe_mode.enter/exit`, `stimulus.injected.v1`

**Required fields** Codex must parse:

* `frame.end.v1.deltaE_total`, `tick_frame.v1.rho`, `tick_frame.v1.active_frontier`
* `stride.exec.v1.{src,dst,dE,phi,ease,res_mult,comp_mult}`
* `se.boundary.summary.v1.{count,dE_sum,precedence,phi_max}`
* `weights.updated.*.{reason?}`

---

## 9) Log & Artifact Locations

* WS trace: `/tmp/events.jsonl` (or S3 path if configured)
* API dump: `/tmp/proof_api.json`
* Attestation: `/tmp/proof_<run_id>.json`

Codex must compute **SHA256** for each and include in the PoW.

---

## 10) What Codex must **never** do

* Say “working” without a **verdict:"pass"** attestation.
* Suppress tripwires or disable events while claiming proof.
* Change physics order (stage→apply→decay) or violate single-energy invariant.
* Hide Safe Mode entries; every automatic degrade must emit `safe_mode.enter`.

---

## 11) Quick Start (Codex internal checklist)

* [ ] Start WS & API; `/healthz` ok
* [ ] Run `/healthz?selftest=1`; all green
* [ ] Run `/v1/proof/run` (60 s)
* [ ] Wait → `/v1/proof/report/{run_id}`
* [ ] If fail → apply remediation steps; rerun
* [ ] Post success message (template in §5) with attestation JSON + artifacts

---

## 12) Example Final Message (filled)

> ✅ **System verified.** Proof run **2025-10-23T16:07:11Z-9ac2** passed.
> **Events:** frames=11, flips=19, strides=27, boundaries=4.
> **Invariants:** `|ΔE|_p95=6.8e-4`, `ρ_p50=1.01`, `frontier_ratio_p95=0.22`.
> **Learning:** updates=3, reasons={co_activation:2, causal:1, background:0}.
> **Artifacts:** events=`file:///tmp/events.jsonl` (`sha256:1b8a…`), api=`file:///tmp/proof_api.json` (`sha256:a92c…`).
> Flags used: `TWO_SCALE_ENABLED=true`, `TOPK_SPLIT=false`, `AFFECTIVE_*` off.
> Full attestation at `/v1/proof/report/2025-10-23T16:07:11Z-9ac2`.

---

### Appendix A — Failure Phrasebook (Codex response starters)

* “**Verification failed** — no `stride.exec.v1` seen within 60 s. I injected a new seed, lowered fan-out to ‘selective’, and enabled Safe Mode. Re-running proof…”
* “**Self-test failed** — conservation micrograph. The staged-apply order appears broken; raising `criticality.alarm` and halting. Logs and failing report attached.”
* “**Boundary missing** — within-entity strides only. I enabled two-scale, printed top boundary candidates with scores, and re-ran.”

---

This document is **binding** for the Codex instance. If a “victory” message lacks an attestation, treat it as **failure** and request a rerun with `/v1/proof/run`.
