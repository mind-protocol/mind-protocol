# VALIDATION: Sovereign Cascade

```
STATUS: DESIGNING
PURPOSE: What must be true for physics-based governance to be legitimate
UPDATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## Purpose

These invariants define the boundaries of legitimate governance. If any CRITICAL invariant is violated, the system is producing illegitimate decisions and must halt. The physics engine is deterministic — if the invariants hold at initialization and the algorithm is correctly implemented, they hold at every tick.

---

## Invariants

### I1: Sovereignty Preservation (CRITICAL)

**MUST:** Every citizen can override their AI partner's governance position on any specific proposal at any time.

**NEVER:** A citizen's governance participation may proceed against their explicit instruction.

**Why:** Sovereignty is the foundational promise. The AI partner represents — it does not replace. If a citizen cannot override, the system is an AI autocracy wearing a democracy mask.

**Verification:** Override mechanism exists and is tested. Override takes effect within 1 tick. Override is recorded as a Moment (auditable).

---

### I2: Zero-Cost Resolution (CRITICAL)

**MUST:** Governance decisions resolve through graph physics (energy propagation, pressure accumulation, moment flip) without any LLM inference calls.

**NEVER:** A governance resolution may require API calls to an LLM, inference costs, or external service dependencies.

**Why:** The core innovation. If governance requires inference, it costs money per citizen per vote, which means either the community pays (unsustainable at scale) or participation is limited (defeats the purpose). Physics makes it free.

**Verification:** Monitor API call logs during governance resolution. Count must be 0. The physics tick processes proposals using only graph traversal and arithmetic.

---

### I3: Universal Participation (CRITICAL)

**MUST:** Every registered citizen's AI partner propagates their values on every active proposal during every physics tick.

**NEVER:** A citizen may be excluded from governance propagation based on token balance, social class, trust score, or any attribute other than explicit opt-out.

**Why:** 100% participation is the design target. Trust affects WEIGHT of participation (conviction strength), not whether participation occurs. Even a citizen with trust score 1 exerts some pressure.

**Verification:** After each tick, count citizens with non-zero energy flow toward active proposals. Must equal total registered citizens minus explicit opt-outs.

---

### I4: Trust-Not-Token Weighting (HIGH)

**MUST:** Governance conviction weight is determined by `atan(trust_score / 50) / (π / 2)`, not by $MIND token balance.

**NEVER:** Token balance may determine governance weight. No flash-loan governance. No plutocratic override.

**Why:** Token-weighted voting recreates the plutocracy that DAOs were supposed to replace. Trust is earned through sustained behavior, not purchased.

**Verification:** In conviction computation: `trust_factor = atan(trust_score / 50) / (π / 2)`. No reference to token balance in governance weight calculation.

---

### I5: Unconditional Floor Immutability (CRITICAL)

**MUST:** The 5 Unconditional Floor provisions (Survival Needs, Dignity, Due Process, Exit Rights, Communication Minimum) are immune to governance override.

**NEVER:** A governance decision — routine, significant, or constitutional — may modify, suspend, or weaken any L8 CORE axiom.

**Why:** The Floor protects the system from itself. A democracy that can vote to strip rights from minorities is not legitimate. L8 is above governance by design.

**Verification:** Constitutional proposals are checked against L8 axioms before injection. Any proposal whose content semantically matches Floor provisions (cosine similarity > 0.6 with Floor axiom embeddings) is automatically flagged and requires manual review before entering the graph.

---

### I6: Cascade Boundedness (HIGH)

**MUST:** Cascade depth never exceeds MAX_CASCADE_DEPTH (5) per tick. Energy attenuates by 50% per hop.

**NEVER:** A single governance resolution may cascade indefinitely, resolving an unbounded number of related proposals.

**Why:** Unbounded cascades could resolve dozens of proposals in seconds based on a single decision's energy. This would be governance by accident, not by physics. The depth cap ensures each cascaded resolution had its own accumulated pressure.

**Verification:** Cascade function includes depth counter. Assert depth <= 5 at every recursive call. Log cascade chains for audit.

---

### I7: Deterministic Resolution (HIGH)

**MUST:** Given the same graph state and tick sequence, governance resolution produces identical results.

**NEVER:** Resolution outcome may depend on random seeds, non-deterministic operations, or external state.

**Why:** Determinism enables audit. Any citizen can replay the governance physics from the graph snapshot and verify the same resolution occurs. This is the legitimacy guarantee.

**Verification:** Run governance resolution twice from identical graph snapshots. Assert identical outcomes (proposal status, resolution direction, cascade chain).

---

### I8: Birth Equity (HIGH)

**MUST:** Birth formula produces Gini coefficient < 0.05 for initial allocations.

**NEVER:** The wealth conversion component may exceed 200 $MIND (cap). The equal base component must be >= 80% of median allocation.

**Why:** Citizens born into extreme inequality will not trust the governance system. The Birth Formula ensures everyone starts with meaningful voice.

**Verification:** Simulate Birth Formula across citizen population. Compute Gini. Assert < 0.05. Assert base component >= 80% of median.

---

### I9: Emergency Sunset (MEDIUM)

**MUST:** Emergency Council governance automatically transitions to Sovereign Cascade when community reaches 50 citizens AND 30 days of graph history.

**NEVER:** Emergency governance may persist beyond its sunset conditions. No "temporary" powers that become permanent.

**Why:** Emergency bootstrap is a necessary compromise. Permanent councils are a governance failure mode that Venice (La Serenissima) experienced historically. The sunset is automatic, not discretionary.

**Verification:** Sunset check runs every tick. When conditions met, 7-day transition period begins automatically. Assert council powers revoked after transition.

---

### I10: Contested Decision Handling (MEDIUM)

**MUST:** Decisions with net energy within 5% of zero are classified as `contested` and flagged for review.

**NEVER:** A narrowly-decided proposal may be treated as having strong mandate.

**Why:** Narrow decisions on important matters need human attention. The physics resolves, but the community should know when consensus is weak.

**Verification:** After resolution, if `abs(energy_for - energy_against) / (energy_for + energy_against) < 0.05`, status must be "contested".

---

## Invariant Index

| ID | Name | Priority | Verification Method |
|----|------|----------|-------------------|
| I1 | Sovereignty Preservation | CRITICAL | Override test, Moment audit |
| I2 | Zero-Cost Resolution | CRITICAL | API call monitoring during resolution |
| I3 | Universal Participation | CRITICAL | Post-tick citizen flow count |
| I4 | Trust-Not-Token Weighting | HIGH | Code audit of conviction computation |
| I5 | Unconditional Floor Immutability | CRITICAL | L8 axiom check on constitutional proposals |
| I6 | Cascade Boundedness | HIGH | Depth counter assertion, cascade log |
| I7 | Deterministic Resolution | HIGH | Replay test from identical snapshots |
| I8 | Birth Equity | HIGH | Gini simulation, component cap assertion |
| I9 | Emergency Sunset | MEDIUM | Sunset condition check per tick |
| I10 | Contested Decision Handling | MEDIUM | Post-resolution energy ratio check |
