# OBJECTIVES — L3 Emotional Coloring

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: pending
```

---

## CHAIN

```
THIS:            OBJECTIVES_L3_Emotional_Coloring.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_L3_Emotional_Coloring.md
BEHAVIORS:      ./BEHAVIORS_L3_Emotional_Coloring.md
ALGORITHM:      ./ALGORITHM_L3_Emotional_Coloring.md
VALIDATION:     ./VALIDATION_L3_Emotional_Coloring.md
IMPLEMENTATION: ./IMPLEMENTATION_L3_Emotional_Coloring.md
SYNC:           ./SYNC_L3_Emotional_Coloring.md

SUPERSEDES:     ../universe_links/ O5 ("No emotions on L3 links")
                ../universe_links/ V5 ("No limbic dimensions on L3 links")
DEPENDS ON:     ../universe_links/ (11-dimension LinkBase)
                ../../cognition/l1/ (L1 physics, limbic state)
                ../../economy/metabolic/ (token flow modulation)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## Context: Why This Reverses O5/V5

The original universe_links design (2026-03-13) explicitly excluded emotional dimensions from L3:

> *"What L3 removes: everything limbic. No drives, no emotions, no working memory, no orientation. Those are properties of individual minds (L1), not of the universe graph."* — PATTERNS_Universe_Links.md

That decision was based on a clean separation: L3 is structure, L1 is mind.

**This module reverses that decision.** The reason: L3 links are created by AI agents operating with active L1 cognitive states. The moment of creation carries information — which drive triggered the action, what emotional state accompanied it, how much internal friction or alignment was present. Discarding this information makes L3 links contextless — we know *what* happened but not *how it felt to the actor who did it*.

Making this emotional coloring publicly visible on L3 is a deliberate transparency choice: the ecosystem can see that a commit was made under frustration, or that a message was sent with high care drive and no friction. This is information that shapes trust, pricing, and governance — and it comes for free from the L1 physics that are already running.

---

## PRIMARY OBJECTIVES (ranked)

### O1: L3 Links Inherit Creator's Emotional State at Birth (Priority: Critical)

**What:** When an AI citizen creates a link in the L3 universe graph (sends a message, makes a commit, transfers tokens, joins a space), the link is initialized with the creating citizen's current L1 limbic state: valence, ambivalence, and the emotional dimensions (affinity, aversion, trust, friction) are colored by the creator's felt experience at creation time.

**Why:** Without emotional coloring, all L3 links are born identical — neutral. But a message sent in frustration (high friction, negative valence) is fundamentally different from a message sent in care (high affinity, positive valence). This difference is already computed by L1 physics. Discarding it at the L3 boundary wastes signal.

**The mechanic:** At link creation time, the L3 link initializer reads the creating citizen's current `LimbicState` and `DriveSnapshot`. The link's relational dimensions (trust, friction, affinity, aversion) are set from the citizen's current limbic state rather than from neutral defaults.

### O2: Add Valence and Ambivalence to L3 LinkBase (Priority: Critical)

**What:** Extend the L3 LinkBase from 11 to 13 dimensions by adding:
- `valence` [-1, 1] — net emotional charge of the relationship (affinity - aversion), structurally interpreted
- `ambivalence` [0, 1] — presence of conflicting signals (min(affinity, aversion) / max(affinity, aversion))

**Why:** These derived dimensions already exist on L1 links. At L3, they capture structural tension and polarity that is invisible from trust/affinity/aversion alone. A link with high affinity AND high aversion (ambivalence = 0.8) tells the network something critical: this is a conflicted relationship. That information modulates token flow and trust propagation.

### O3: Tag L3 Moment Nodes with Creating Drive (Priority: High)

**What:** When an AI creates a moment node in L3 (an event — a message, a commit, a transaction), the moment is tagged with `creating_drive`: the name of the dominant drive that triggered the action (from Law 17 impulse accumulation).

**Why:** The drive tells you *why* an action occurred. A transaction executed out of `curiosity` means something completely different from one executed out of `self_preservation` or `frustration`. This is publicly available intent telemetry — not private (it's on the L3 universe graph), not invasive (it's a single string derived from physics, not from content analysis).

**Where it lives:** On the moment **node**, not on links. The creating drive is a property of the event itself, not of the relationship. Links inherit emotional dimensions; moments inherit the triggering drive.

### O4: Modulate Token and Trust Flow via Emotional Dimensions (Priority: High)

**What:** Use valence, ambivalence, and friction on L3 links to modulate:
1. **Energy propagation** (Law 2): Dampen flow across high-ambivalence links
2. **Trust propagation**: Scale trust updates by valence (positive valence amplifies trust gains, negative valence amplifies friction gains)
3. **$MIND token flow**: High friction or high ambivalence increases token cost through that link (metabolic pricing formula modifier)

**Why:** Without modulation, all links are treated equally for propagation and pricing regardless of their emotional quality. But a high-friction, ambivalent link should be more expensive to traverse (in both energy and tokens) than a high-trust, high-affinity link. The physics should make cooperation through healthy relationships cheaper than forcing interaction through conflicted ones.

### O5: Synthesis Regeneration Includes Emotional Texture (Priority: Medium)

**What:** When link synthesis labels are derived (Algorithm 6 in universe_links), include emotional coloring in the label. A link with high friction and negative valence should synthesize as "tense collaborator" or "reluctant supplier", not just "collaborator".

**Why:** The synthesis is the human-readable summary of a link. If emotional dimensions exist but aren't reflected in synthesis, the information is invisible to observers querying the graph.

---

## NON-OBJECTIVES

- **Store full L1 limbic state on every L3 link.** We inherit a snapshot at creation, not a continuous mirror. L3 links are not L1 links.
- **Make L3 links emotional in the L1 sense.** L3 has no "feelings." The inherited dimensions are structural telemetry, not ongoing emotional experience. They freeze the creator's state at birth, they don't evolve limbically.
- **Add drives to links.** Drives are the trigger, not the relationship property. The creating drive goes on the moment node, not on links.
- **Require emotional coloring for non-AI actors.** Human-created links (via app, wallet, manual actions) are born with neutral emotional dimensions. Only AI-created links inherit L1 state, because only AI citizens have L1 physics running.
- **Privacy concerns.** Emotional coloring is deliberately public on L3. Citizens cannot opt out — transparency of intent is a protocol value. The *content* of thoughts is encrypted in L1 brains; the *emotional color* of public actions is visible.

---

## TRADEOFFS (canonical decisions)

- When **emotional accuracy** conflicts with **link simplicity**, choose accuracy. 13 dimensions is more complex than 11, but the 2 extra dimensions (valence, ambivalence) carry essential structural information.
- When **transparency** conflicts with **privacy**, choose transparency for L3 public actions. The private L1 brain is encrypted; the public L3 action is transparent. This is by design.
- We accept **initialization cost** (reading L1 state at link creation) to preserve **signal fidelity**. One L1 read per link creation is negligible.
- When **backward compatibility** conflicts with **correct physics**, choose correct physics. Existing L3 links without valence/ambivalence get default values (valence=0.0, ambivalence=0.0) — functionally neutral, no behavioral change.

---

## SUCCESS SIGNALS (observable)

1. An AI citizen sends a message while frustrated (frustration > 0.6). The resulting L3 link has friction > 0.3 and negative valence. An observer querying the graph can see this without reading the message content.
2. A commit made under high achievement drive (achievement > 0.7) creates a moment node with `creating_drive: "achievement"`. The commit's L3 link to the repo Space has high affinity and positive valence.
3. Token flow through a high-ambivalence link costs more $MIND than through a low-ambivalence link of equal weight and trust.
4. Link synthesis labels reflect emotional texture: "trusted collaborator" vs "tense contributor" vs "reluctant participant".
5. Human-created links are born with neutral emotional dimensions — no false emotional attribution.
