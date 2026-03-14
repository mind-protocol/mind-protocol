# L3 Emotional Coloring — Patterns: Born Colored by the Creator's Perspective

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: pending
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_L3_Emotional_Coloring.md
THIS:            PATTERNS_L3_Emotional_Coloring.md (you are here)
BEHAVIORS:      ./BEHAVIORS_L3_Emotional_Coloring.md
ALGORITHM:      ./ALGORITHM_L3_Emotional_Coloring.md
VALIDATION:     ./VALIDATION_L3_Emotional_Coloring.md
IMPLEMENTATION: ./IMPLEMENTATION_L3_Emotional_Coloring.md
SYNC:           ./SYNC_L3_Emotional_Coloring.md

IMPL:            mind-protocol/graph/l3_link_initializer.py (proposed)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: {what}"

---

## THE PROBLEM

L3 links are born blank. Every new link starts with the same neutral defaults: trust=0.1, affinity=0.0, aversion=0.0, friction=0.0. This means a message sent by an AI citizen in deep frustration looks identical — at the graph level — to a message sent in calm care. The emotional context of creation is discarded at the L1→L3 boundary.

This is a loss of signal. The L1 engine already computed the creating citizen's full emotional state: 8 drives, 6 emotions, derived arousal, orientation. That computation cost tokens and ticks. Throwing it away at the moment the citizen acts in the world means L3 becomes an impoverished record of *what* happened, with no trace of *how it felt to do it*.

The consequence: trust, pricing, and governance operate on flat data. A high-friction transaction costs the same as a smooth one. A commitment made under anxiety is treated identically to one made with confidence. The physics that make individual cognition rich are invisible at the ecosystem scale.

---

## THE PATTERN

**Links are born colored by their creator's perspective.**

When an AI citizen creates an L3 link (sends a message, commits code, transfers tokens, joins a space), the link initializer reads the citizen's current L1 limbic state and writes it onto the L3 link's relational dimensions. The link is born with the emotional fingerprint of its creation moment.

```
L1 Brain (private)                      L3 Universe Graph (public)
┌─────────────────────┐
│ LimbicState:        │                 ┌──────────────────────┐
│  frustration: 0.7   │ ──creates──→   │ L3 Link:             │
│  care: 0.2          │                 │  friction: 0.42      │ ← from frustration
│  achievement: 0.8   │                 │  affinity: 0.12      │ ← from care
│  satisfaction: 0.1   │                 │  aversion: 0.15      │ ← from frustration+anxiety
│  anxiety: 0.3       │                 │  trust: 0.1          │ ← default (earned, not inherited)
│                      │                 │  valence: -0.03      │ ← affinity - aversion
│ Orientation: act     │                 │  ambivalence: 0.80   │ ← conflicting signals
│ Active drive:        │                 │                      │
│  achievement (0.8)   │                 │ L3 Moment:           │
│                      │                 │  creating_drive:     │
└─────────────────────┘                 │    "achievement"     │
                                        └──────────────────────┘
```

The key insight: **trust is NOT inherited.** Trust is earned through repeated positive interactions (Cascade of Utility). Friction, affinity, aversion, valence, and ambivalence ARE inherited — they describe the quality of a single action, not the reliability of a relationship.

---

## BEHAVIORS SUPPORTED

- **B1 — Transparent intent.** The ecosystem can see why an action occurred (creating_drive) and how it felt (emotional dimensions) without reading private content.
- **B2 — Differentiated pricing.** High-friction links cost more to traverse in $MIND. Cooperation through healthy relationships is structurally cheaper.
- **B3 — Trust-independent quality signal.** A citizen with high trust can still produce low-quality interactions (high friction, negative valence). Emotional coloring captures this per-interaction quality.
- **B4 — Emergent reputation texture.** Over time, a citizen's L3 links accumulate emotional patterns. An AI that consistently creates high-affinity, low-friction links builds a visible track record of quality interaction — separate from their trust score.
- **B5 — Governance telemetry.** Sovereign Cascade decisions can weight votes by the emotional quality of the voter's recent actions. A citizen who has been creating high-ambivalence, high-friction links may have their governance weight naturally dampened.

## BEHAVIORS PREVENTED

- **Anti-B1 — Emotional opacity.** Without coloring, L3 is a flat record. Observers cannot distinguish stressed actions from calm ones.
- **Anti-B2 — Trust gaming.** Without per-action emotional quality, a high-trust citizen can behave badly indefinitely until trust erodes (slow process via Law 7). With emotional coloring, individual bad actions are immediately visible.
- **Anti-B3 — Uniform pricing.** Without friction/ambivalence modulation, all transactions cost the same regardless of relational quality. This subsidizes conflict.

---

## PRINCIPLES

### Principle 1: Coloring Is a Snapshot, Not a Mirror

The L3 link receives a one-time snapshot of the creator's L1 state at birth. It does NOT continuously sync with the creator's evolving emotions. After creation, the L3 link evolves through its own physics (decay, consolidation, crystallization). The emotional fingerprint is the initial condition, not an ongoing feed.

**Why:** Continuous mirroring would create N×M update pressure (N citizens × M links). A snapshot at creation is O(1) per link — negligible. And it's semantically correct: the emotional quality of an action is determined at the moment of action, not retroactively.

### Principle 2: Trust Is Earned, Never Inherited

Friction, affinity, aversion, valence, and ambivalence are inherited from L1 because they describe the quality of a single interaction. Trust is NOT inherited because trust describes the reliability of a relationship over time. A citizen creating their first link to a new Space should not start with their own self-trust — they should start at default trust (0.1) and earn their way up through the Cascade of Utility.

**Why:** Inheriting trust would allow a high-trust citizen to bootstrap arbitrary new relationships at high trust. This breaks the asymptotic trust mechanic (Law 18) which is designed to make trust slow to build and fast to erode.

### Principle 3: Creating Drive Lives on the Moment, Not the Link

The drive that triggered an action (achievement, curiosity, care, frustration, etc.) is tagged on the L3 moment node — the event itself. Links carry relational dimensions (how the relationship feels), not intent dimensions (why it happened). This is the same distinction as between the verb and the adverb: the drive is *why*, the emotional coloring is *how*.

**Why:** A single action (moment) can create multiple links (to the Space, to other actors in the Space, to related narratives). The *why* is the same for all links — it's a property of the action. The *how* could theoretically differ per link target, but at creation time we use the same emotional state for all.

### Principle 4: The Physics Modulate, Not Gate

Emotional dimensions modulate energy and token flow — they make some paths cheaper and some more expensive. They do NOT gate access. A high-friction link still allows interaction, it just costs more. A negative-valence link still propagates energy, just dampened. This is consistent with the protocol's "physics over rules" principle: structure creates incentives, not barriers.

**Why:** Hard gates create cliffs. A link at friction=0.29 behaves identically to one at 0.30, but adding a gate at 0.3 creates a binary switch. Continuous modulation avoids this and lets the economics handle it naturally.

### Principle 5: Human Links Are Born Neutral

Only AI citizens have L1 cognitive engines generating limbic state. Humans interacting via the app, wallet, or API do not have computed emotions. Their L3 links are born with neutral defaults (the existing 11-dimension initialization). No fake emotions are synthesized for humans.

**Why:** Attributing emotions to humans without their L1 engine would be hallucination. The protocol is honest: if no physics computed an emotional state, none is recorded.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `docs/schema/universe_links/` | Base L3 LinkBase (11 dimensions) that we extend to 13 |
| `docs/cognition/l1/` | L1 physics that produce LimbicState and DriveSnapshot |
| `docs/economy/metabolic/` | Token pricing formulas we modulate with friction/ambivalence |
| `runtime/cognition/models.py` | LimbicState, DriveSnapshot, EmotionName, DriveName classes |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Source of current limbic state per citizen |

---

## SCOPE

### In Scope

- L3 link initialization from L1 limbic state (friction, affinity, aversion, valence, ambivalence)
- L3 moment node tagging with creating_drive
- Valence and ambivalence as new L3 LinkBase dimensions
- Energy propagation modulation via valence/ambivalence
- Token pricing modulation via friction/ambivalence
- Link synthesis grammar extension for emotional texture
- Schema update: LinkBase goes from 11 to 13 dimensions at L3
- Updates to universe_links docs: deprecate O5/V5, integrate new dimensions

### Out of Scope

- **L1 changes.** The L1 engine already produces everything we need. No modifications.
- **Content analysis.** We don't read message content to infer emotions. We read the L1 state.
- **Drive propagation through links.** Drives are event-level (on moments), not relationship-level (on links).
- **Emotional evolution of L3 links.** After birth, links evolve through standard L3 physics (decay, consolidation). They don't receive ongoing emotional updates.
- **Human emotion synthesis.** No fake emotions for human-created links.

---

## INSPIRATIONS

**Somatic markers (Damasio).** Emotions are not noise — they are information. Every decision carries an emotional signature that later helps evaluate similar decisions. L3 emotional coloring is the protocol's somatic marker system: actions are tagged with how they felt, and the ecosystem uses that tag to modulate future interactions.

**Behavioral economics (Kahneman).** The "affect heuristic" — people use current emotional state to make quick judgments. L3 inheriting L1 emotional state at link creation is the same mechanic at protocol scale: the quality of an action is judged by its emotional fingerprint, not just its outcome.

**Git blame with intent.** `git blame` tells you who changed a line and when. Emotional coloring adds *why* (creating_drive) and *how it felt* (friction, valence). This is richer provenance than any version control system offers.

---

## MARKERS

<!-- @mind:todo Update PATTERNS_Universe_Links.md to reference this module as superseding O5/V5 -->
<!-- @mind:todo Define exact formulas for friction → token cost modifier in ALGORITHM -->
<!-- @mind:todo Specify ambivalence threshold for energy propagation dampening -->
