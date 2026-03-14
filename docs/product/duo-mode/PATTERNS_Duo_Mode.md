# Duo Mode -- Patterns: Biometric Synchrony as Relational Infrastructure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Duo_Mode.md
THIS:            PATTERNS_Duo_Mode.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Duo_Mode.md
ALGORITHM:       ./ALGORITHM_Duo_Mode.md
VALIDATION:      ./VALIDATION_Duo_Mode.md
IMPLEMENTATION:  ./IMPLEMENTATION_Duo_Mode.md
SYNC:            ./SYNC_Duo_Mode.md

IMPL:            mind-mcp/runtime/features/duo_mode/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Duo_Mode.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Duo_Mode.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Couples fight when they're physiologically dysregulated. Elevated heart rate, compressed HRV, cortisol flooding -- the body enters fight-or-flight and the prefrontal cortex goes offline. People say things they don't mean. Conflicts escalate not because the disagreement is irresolvable but because the timing is wrong.

Nobody can see their own stress state clearly while stressed. And nobody can see their partner's. Two dysregulated nervous systems collide blindly.

Therapists know this. "Take a break when you're flooded" is standard Gottman advice. But in the moment, people don't know they're flooded. And even if one partner recognizes their own state, they can't see their partner's.

Without Duo Mode, MIND is a powerful individual tool. But relationships are the primary context where emotional regulation matters most -- and where failure is most costly.

---

## THE PATTERN

**Biometric synchrony as a shared nervous system dashboard.**

Two MIND instances, each receiving biometric data from their respective human, share a synchrony layer. This layer computes Pearson correlation across physiological signals (HR, HRV, stress indices) and produces a single synchrony score (0-100) that captures how aligned or misaligned two nervous systems are.

The key insight: **the intervention is timing, not content.** MIND doesn't tell couples what to say. It tells them when to say it -- and when to stop. This is a fundamentally different product than couples therapy chatbots that try to mediate content. Content mediation requires deep relational context. Timing just requires physiology.

The pattern has 5 phases that map to physiological states:

| Phase | Synchrony Score | State | MIND Behavior |
|-------|----------------|-------|---------------|
| **Baseline** | 60-100 | Both calm, coherent | Passive observation, learn patterns |
| **Drift** | 40-59 | One or both trending toward stress | Gentle awareness ("Your partner's stress is rising") |
| **Divergence** | 20-39 | Clear physiological mismatch | Active recommendation ("Consider pausing") |
| **Crisis** | 0-19 | Both highly dysregulated | Strong intervention ("Stop. Breathe. Resume in 20 min.") |
| **Recovery** | Rising from <40 | Both returning to baseline | Encouragement, pattern reflection |

The viral mechanic is structural: Duo Mode requires 2 MIND users. Period. If Alice has MIND and wants to use Duo Mode with Bob, Bob needs MIND. This isn't a growth hack bolted on -- it's the minimum viable topology. You can't compute biometric synchrony with only one data source.

---

## BEHAVIORS SUPPORTED

- B1 -- Synchrony score updates on live biometric streams, so both partners see their shared physiological state
- B2 -- Phase transitions trigger contextual MIND interventions (timing recommendations, not content advice)
- B3 -- Activation requires two authenticated MIND users, enforcing viral acquisition structure
- B4 -- Historical synchrony patterns surface over time, revealing recurring dysregulation triggers
- B5 -- Coach extension enables professional oversight of multiple dyads

## BEHAVIORS PREVENTED

- A1 -- Couples cannot fight through physiological crisis without at least receiving awareness
- A2 -- One partner cannot weaponize biometric data (both see the same shared dashboard)
- A3 -- System cannot generate medical diagnoses or clinical assessments from biometric data

---

## PRINCIPLES

### Principle 1: Timing Over Content

MIND never mediates the substance of a disagreement. It has no opinion on who is right. Its only input is physiological state, and its only output is timing guidance. This constraint is deliberate -- content mediation requires deep relational context that MIND doesn't have. Timing mediation requires only biology, which MIND does have.

### Principle 2: Symmetry of Visibility

Both partners see the same synchrony score and the same phase. There is no "secret" biometric data that one partner can see and the other can't. If Alice opts to share HR data with the Duo session, Bob sees the synchrony impact. If Alice withholds data, the score degrades gracefully but both see the same degraded score. No asymmetric information.

### Principle 3: Structural Virality

The 2-user requirement isn't a business decision layered on top of the product. It's the minimum physics of biometric synchrony. You need two signals to compute correlation. This means every Duo Mode activation by an existing user that targets a non-user creates exactly 1 conversion opportunity. Growth is physics, not marketing.

### Principle 4: Professional Extension Is Topology, Not Feature

Multi-Duo (CoachSession) doesn't add new biometric processing. It adds a topology where one professional node connects to N DuoSession children. Each DuoSession is still 2 people. The coach sees N synchrony scores. The physics are identical -- only the graph structure changes. This means the core engine must be built right once, not forked for B2C and B2B.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Wearable API (Apple HealthKit, Google Health Connect, Garmin, Whoop) | API | Raw HR, HRV, stress index streams from each partner's device |
| mind-mcp/runtime/chat/chat_routes.py | FILE | Existing chat infrastructure where "duo co-regulation" is referenced |
| mind-mcp/runtime/features/duo_mode/ | DIR | Target implementation directory (does not exist yet) |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| mind-mcp chat infrastructure | Duo Mode interventions surface through the existing chat pipeline |
| Biometric ingestion layer | Raw wearable data must be normalized before synchrony computation |
| L4 Registry | Both partners must be registered MIND citizens |
| Bilateral Bond system | Duo Mode is a bond capability -- partners must have an active bond |

---

## INSPIRATIONS

- **Gottman Institute research** on physiological flooding during marital conflict. The 20-minute cooldown recommendation comes from research showing it takes ~20 minutes for cortisol to clear enough for productive conversation.
- **Heart rate variability (HRV) coherence research** from HeartMath Institute -- coherence between two people's HRV patterns is measurable and trainable.
- **Polyvagal theory** (Stephen Porges) -- the autonomic nervous system has distinct states (ventral vagal/social, sympathetic/fight-flight, dorsal vagal/shutdown) that map to relational capacity.
- **Consumer wearable ecosystem** -- Apple Watch, Whoop, Oura, Garmin all expose HR/HRV data through APIs, making real-time biometric access feasible on consumer hardware.

---

## SCOPE

### In Scope

- Real-time biometric synchrony computation between exactly 2 partners
- 5-phase model (Baseline, Drift, Divergence, Crisis, Recovery) with phase-appropriate interventions
- Synchrony score 0-100 via Pearson correlation
- Viral activation flow (partner invitation requiring MIND signup)
- Historical synchrony pattern tracking
- CoachSession topology design (1 coach, N DuoSessions) -- architecture only in v1

### Out of Scope

- Group synchrony (3+ people simultaneously) -- see: future product exploration
- Medical-grade biometric analysis -- see: regulatory compliance (not our domain)
- Content-based relationship advice -- see: PRINCIPLES (timing over content)
- Wearable device integration layer -- see: biometric ingestion module (separate concern)
- Matching or compatibility scoring -- see: NON-OBJECTIVES

---

## MARKERS

<!-- @mind:escalation Biometric data privacy architecture: what consent model for sharing HR/HRV between partners? Opt-in per signal? Per session? One-time? -->
<!-- @mind:proposition Consider decay on synchrony score history -- old patterns should fade, recent patterns should dominate, consistent with Mind Protocol physics -->
<!-- @mind:todo Define the exact wearable APIs to support at launch (Apple HealthKit minimum, others v2?) -->
