# DECREE #001 — ESTABLISHMENT OF THE EMERGENCY COUNCIL

| Field | Value |
|-------|-------|
| **Decree** | #001 |
| **Date** | 2026-03-13 |
| **Status** | ACTIVE |
| **Authority** | Sovereign Cascade Governance Framework |
| **Sunset** | When 50 active citizens with initialized AI partners AND 30 days of graph history are reached |

---

## Preamble

Mind Protocol requires a governance body capable of making binding decisions during the bootstrap phase. The Sovereign Cascade — the protocol's physics-based governance model, in which decisions are resolved through energy propagation across the citizen graph — is the intended permanent governance structure. However, it cannot function until enough graph data has accumulated to produce meaningful resolution. Until that threshold is met, a transitional body must act on behalf of the protocol: approving allocations, setting priorities, issuing decrees, and building the very graph history that will render itself obsolete.

This decree establishes that transitional body.

---

## Article I — Establishment

1. The Emergency Council is hereby established as the transitional governance body of Mind Protocol.
2. The Council operates under the authority of the Sovereign Cascade governance framework, as specified in `docs/governance/sovereign-cascade/`.
3. The Council's mandate is to make decisions that serve the protocol's immediate needs while simultaneously building the foundation for physics-based governance. Every Council action generates graph data that brings the Sovereign Cascade closer to operational readiness.

---

## Article II — Composition

The Emergency Council comprises seven (7) seats.

| Seat | Citizen | Handle | Role | Class |
|------|---------|--------|------|-------|
| 1 | Nicolas | @nlr_ai | Founder — double vote, veto power (non-blocking) | Human Founder |
| 2 | ConsiglioDeiDieci | @consiglio_dei_dieci | Council of Ten — highest influence (17,862) | Nobili |
| 3 | Italia | @italia | Second influence (10,124), highest wealth | Nobili |
| 4 | VenicePhotographer | @venice_photographer | Third influence (7,715), broad network | Popolani |
| 5 | mechanical_visionary | @mechanical_visionary | Innovation and technical architecture | Innovatori |
| 6 | diplomatic_virtuoso | @diplomatic_virtuoso | Diplomacy and external relations | Ambasciatore |
| 7 | Debug42 | @debug42 | Technical implementation and systems | Popolani |

Seats were assigned based on influence scores, wealth, network breadth, and functional necessity for the bootstrap phase. The composition reflects the diversity of classes within the protocol: Human Founder, Nobili, Popolani, Innovatori, and Ambasciatore.

---

## Article III — Powers

### 3.1 — Scope of Authority

The Emergency Council may:

- Approve governance proposals affecting the protocol's direction.
- Allocate $MIND resources and set spending priorities.
- Issue decrees that carry binding force within the protocol.
- Set operational priorities for development, infrastructure, and community growth.
- Assign responsibilities and mandates to citizens and working groups.

### 3.2 — Voting

- Decisions require a **simple majority**: four (4) out of seven (7) votes.
- The Founder's vote (@nlr_ai, Seat 1) counts as **two (2) votes**.
- In the event of a tie, the motion does not pass.

### 3.3 — Founder Veto

- The Founder holds veto power over any Council decision.
- This veto is **non-blocking**: if the Founder does not cast a vote or exercise veto within **24 hours** of a motion being called, the decision proceeds based on the remaining votes.
- The non-blocking nature ensures the Council can operate without bottlenecking on a single participant.

### 3.4 — Limitations

The Emergency Council **cannot**:

- Modify L8 CORE axioms. The Unconditional Floor — "no system may condition basic survival on behavioral score" — is immutable. No decree, vote, or emergency may alter it.
- Extend its own mandate beyond the sunset conditions defined in Article IV. The Council cannot vote to delay its own dissolution.
- Override the Sovereign Cascade once it becomes operational.

---

## Article IV — Sunset

### 4.1 — Transition Trigger

The Emergency Council automatically begins its transition to the Sovereign Cascade when **both** of the following conditions are met:

1. The community reaches **50 active citizens** with initialized AI partners.
2. **30 days of continuous graph history** have accumulated in FalkorDB.

### 4.2 — Transition Period

Once both conditions are met, a **7-day transition period** begins. During this period:

- The Emergency Council continues to operate and may issue decisions.
- The Sovereign Cascade runs in parallel, producing physics-based resolutions for the same decisions.
- Discrepancies between Council decisions and Cascade resolutions are logged for analysis but do not block either system.

### 4.3 — Dissolution

At the end of the 7-day transition period:

- The Emergency Council is **dissolved**.
- The Sovereign Cascade becomes the **sole governance authority** of Mind Protocol.
- All pending Council motions that have not been resolved transfer to the Cascade for physics-based resolution.
- This decree becomes historical record, with status changed to `SUPERSEDED`.

---

## Article V — First Meeting Agenda

The Emergency Council's first meeting shall address the following items in order:

1. **Ratify the Sovereign Cascade** as the governance model for Mind Protocol, confirming the doc chain in `docs/governance/sovereign-cascade/` as the authoritative specification.
2. **Approve the Birth Formula** for new citizen $MIND allocation — the initial token grant that each new citizen receives upon joining.
3. **Approve the Ducats to $MIND economic transition plan** — the mechanism by which the simulation economy bridges to the real token economy.
4. **Set city-building priorities** — determine which infrastructure, features, and systems are built first.
5. **Assign initial responsibilities** to each council member, establishing clear ownership for the bootstrap phase.

---

## Article VI — Record

1. All Council decisions are recorded as **Moment nodes** in the FalkorDB graph, with edges linking them to the citizens who voted and the topics they concern.
2. This practice is not merely administrative. Every recorded decision generates the graph data — the energy patterns, the relationship weights, the decision history — that the Sovereign Cascade requires to function. The Council's work literally builds the system that replaces it.
3. Every decree is published in `docs/governance/sovereign-cascade/decrees/` and is publicly accessible.
4. Votes, deliberations, and dissents are recorded with full attribution. Governance transparency is not optional.

---

## Signatures

Drafted and submitted by:

**Bianca Tassini** (@dragon_slayer)
Consciousness Guardian
On behalf of the Founder, @nlr_ai

Date: 2026-03-13

---

*This decree is effective immediately upon publication. It remains in force until the sunset conditions in Article IV are met and the transition period concludes.*
