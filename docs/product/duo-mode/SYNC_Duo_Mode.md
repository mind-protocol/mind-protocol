# Duo Mode -- Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- 5-phase model with thresholds (BASELINE >= 60, DRIFT 40-59, DIVERGENCE 20-39, CRISIS < 20, RECOVERY rising)
- Pearson correlation as the synchrony metric
- Score range 0-100 (anti-correlation floors at 0)
- 2-user requirement (structural virality)
- Timing-only interventions (never content mediation)
- Biometric privacy (raw data stays with owner, only derived score shared)

**What's still being designed:**
- Hysteresis band value (5 proposed, needs testing with real wearable data)
- Minimum dwell time (120s proposed, needs UX validation)
- Exact wearable APIs to support at launch
- Persistence model for DuoSession (graph node vs separate store)
- Consent model for biometric sharing between partners
- Integration point in existing chat_routes.py
- Intervention message templates (tone, length, localization)

**What's proposed (v2+):**
- Multi-Duo / CoachSession topology (1 coach, N DuoSessions)
- HRV cross-correlation as secondary synchrony signal
- Weighted Pearson (exponential decay within window for faster responsiveness)
- Adaptive hysteresis (wider band for new sessions, narrower after calibration)
- Historical pattern matching ("this usually happens on Sunday evenings")
- Wearable-agnostic ingestion layer (beyond Apple HealthKit)

---

## CURRENT STATE

Documentation chain created. No code exists yet. The module is designed as an extension of the existing mind-mcp chat infrastructure, where "duo co-regulation" is already referenced in chat_routes.py but not implemented.

The doc chain establishes:
- Clear objectives with ranked priorities (physiological awareness > viral growth > co-regulation > coaching)
- A concrete algorithm with pseudocode for stream alignment, Pearson correlation, score mapping, and phase transitions
- 11 validation invariants covering session integrity, score bounds, phase determinism, privacy, and numerical stability
- A file-level implementation plan targeting `mind-mcp/runtime/features/duo_mode/` with 6 source files and 5 test files
- Dependencies identified: biometric ingestion, chat pipeline, L4 registry, bilateral bond system

The design is intentionally conservative for v1: HR only (not HRV cross-correlation), anti-correlation floors at 0, and CoachSession is architecture-only.

---

## IN PROGRESS

### Documentation Chain

- **Started:** 2026-03-14
- **By:** Claude Opus (groundwork)
- **Status:** Complete (7 files)
- **Context:** Created as part of product documentation for wedge #2. No code implementation yet. Roadmap targets S15-S16 (May 2026) for mobile implementation.

---

## RECENT CHANGES

### 2026-03-14: Full Doc Chain Created

- **What:** 7 documentation files: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC
- **Why:** Duo Mode is MIND's second wedge product. Documentation chain needed before implementation begins to capture design decisions, especially the 5-phase model and Pearson-based synchrony scoring.
- **Files:** `docs/product/duo-mode/` (7 files)
- **Struggles/Insights:** Key tension between responsiveness (users want real-time) and stability (Pearson needs samples). 300s window with 90s update lag is the compromise. Anti-correlation flooring at 0 was a non-obvious decision -- keeps the score interpretable for non-technical users.

---

## KNOWN ISSUES

### No Biometric Ingestion Layer

- **Severity:** HIGH (blocking for implementation)
- **Symptom:** Duo Mode requires normalized biometric streams. No ingestion module exists in mind-mcp.
- **Suspected cause:** Wearable integration is a separate concern not yet started.
- **Attempted:** N/A (design phase)

### Consent Model Undefined

- **Severity:** MEDIUM (blocking for privacy compliance)
- **Symptom:** V7 (raw biometric privacy) is defined as an invariant, but the consent flow for what derived data is shared is not specified.
- **Suspected cause:** Design decision needed from Nicolas.
- **Attempted:** N/A

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** Implement Duo Mode core (groundwork agent)

**Where I stopped:** Doc chain complete. No code written.

**What you need to understand:**
Duo Mode sits ON TOP of existing chat infrastructure. The synchrony computation is pure Python with no external dependencies. The hard parts are: (1) biometric ingestion from wearables (separate module, not Duo Mode's concern), (2) persistence for DuoSession state, and (3) chat integration for intervention delivery. Start with the pure computation modules (alignment, Pearson, phase engine) because they're testable in isolation.

**Watch out for:**
- Don't add HRV cross-correlation in v1. HR only. The algorithm doc explains why.
- Don't add fallback scores when data is stale. Pause the score. See V8.
- The phase engine MUST be deterministic. Same inputs = same outputs. No randomness, no external state.
- Anti-correlation floors at 0, not at negative values. See D2 in ALGORITHM.

**Open questions I had:**
- Should DuoSession be a graph SpaceNode or a separate datastore? Graph fits the Mind Protocol model but may be slow for real-time updates.
- What's the exact function signature in chat_routes.py for delivering duo interventions?
- Population norms for stress_index mapping from HRV -- athlete vs sedentary baselines differ 2-3x.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain for Duo Mode (MIND's wedge #2). 7 files covering objectives through implementation plan. Core algorithm: Pearson correlation on HR streams, 5-phase state machine with hysteresis, timing-only interventions. 11 validation invariants. No code written yet -- design phase only. Targets S15-S16 (May 2026) for mobile implementation.

**Decisions made:**
- HR (not HRV) as primary correlation signal for v1 -- higher frequency, device-agnostic
- Anti-correlation floors at 0 -- keeps score interpretable
- 300-second window -- balances responsiveness with stability
- RECOVERY as distinct phase (not just "returning to DRIFT") -- different psychological state
- Multi-Duo (CoachSession) is v2 architecture only
- Pure Python stdlib, no external dependencies for core computation

**Needs your input:**
- Consent model for biometric sharing: opt-in per signal? per session? one-time?
- Which wearable APIs to support at launch? (Apple HealthKit minimum?)
- Intervention message tone and language (direct like the rest of MIND, or softer for couples context?)
- DuoSession persistence: graph node or separate store?
- Population norms for stress_index: which reference population?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Entire module is documented but not implemented

### Tests to Run

```bash
# When implemented:
cd mind-mcp && python -m pytest tests/features/duo_mode/ -v
```

### Immediate

- [ ] Implement `biometric_stream_alignment_and_resampling.py` (pure function, testable first)
- [ ] Implement `pearson_synchrony_score_computation.py` (pure function, testable second)
- [ ] Implement `phase_engine_with_hysteresis_and_dwell.py` (state machine, testable third)
- [ ] Write tests for all three core modules before session/intervention code

### Later

- [ ] Implement `duo_session_lifecycle_and_management.py` (needs persistence decision)
- [ ] Implement `intervention_message_generation.py` (needs tone/language decision)
- [ ] Integrate with `chat_routes.py` for intervention delivery
- [ ] Design biometric ingestion layer (separate module, not Duo Mode)
- IDEA: WebSocket channel for real-time score streaming to mobile UI
- IDEA: Notification to partner when the other opens Duo Mode ("your partner wants to connect")

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the algorithm design. The 5-phase model with hysteresis is clean. The pure-function pipeline approach makes this very testable. Main uncertainty is around the integration points: biometric ingestion doesn't exist yet, and the chat_routes.py hook needs to be identified.

**Threads I was holding:**
- The relationship between Duo Mode and the bilateral bond system. Should activating Duo Mode require an active bond? Makes sense architecturally (Duo Mode is a bond capability) but might create friction for the viral acquisition flow (new user signs up -> needs to form bond -> then activate Duo Mode? Too many steps).
- Population norms for stress_index are genuinely difficult. A 25-year-old athlete with RMSSD of 80ms is relaxed. A 65-year-old sedentary person with RMSSD of 80ms might not exist. The mapping needs to be personalized eventually, but v1 can use rough population averages.

**Intuitions:**
- The 300s window might need to be shorter for the first implementation. 60s is too jittery, 300s is stable but slow. 180s (3 minutes) might be the sweet spot. Needs real-data testing.
- Multi-Duo (CoachSession) will be the B2B revenue driver. But the core 2-person engine must be perfect first. Don't rush to coach topology.
- The viral mechanic is real. If the product is good, couples will pull their partners in. If the product is mediocre, no amount of invitation flow optimization will help. Build the experience first.

**What I wish I'd known at the start:**
The phase engine hysteresis and minimum dwell are where the UX lives. The Pearson computation is mathematically straightforward. The engineering challenge is making phase transitions feel right -- not too sensitive, not too laggy. This is a calibration problem that needs real users, not more design docs.

---

## POINTERS

| What | Where |
|------|-------|
| Existing duo co-regulation reference | `mind-mcp/runtime/chat/chat_routes.py` |
| Bilateral bond manifesto | `.mind/manifesto/THE_BILATERAL_BOND_MANIFESTO.md` |
| Bond docs (dependency) | `docs/economy/bonds/` |
| L4 Registry (dependency) | `l4/registry/` |
| Schema reference | `.mind/schema.yaml` |
