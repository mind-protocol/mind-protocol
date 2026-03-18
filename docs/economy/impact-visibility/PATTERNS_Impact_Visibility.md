# PATTERNS: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Architectural patterns                     |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | Ranked objectives and tradeoffs          |
| PATTERNS_Impact_Visibility.md           | This file -- patterns and principles     |
| BEHAVIORS_Impact_Visibility.md          | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Impact_Visibility.md          | Algorithms and data structures           |
| VALIDATION_Impact_Visibility.md         | Validation rules and invariants          |
| IMPLEMENTATION_Impact_Visibility.md     | Implementation status and code mapping   |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md)

Related:
- [ALGORITHM_Metabolic_Economy.md](../metabolic/ALGORITHM_Metabolic_Economy.md) (Formula 4 -- settlement epochs)
- [L3_SOCIAL_PHYSICS.yaml](../../schema/universe_links/L3_SOCIAL_PHYSICS.yaml) (social action effects)

---

## The Problem

Citizens act prosocially -- sharing knowledge, mentoring, creating public goods, helping others through impasses. These actions produce measurable downstream effects in the graph: trust links strengthen, knowledge propagates, cascade chains extend, $MIND flows. But the acting citizen never sees these downstream effects. The action happens, the physics computes the consequences, and the consequences are invisible to the actor.

This is a feedback gap. Not a motivational gap -- the system does not need to motivate. It is an informational gap. The physics can only reinforce what the limbic system can observe. If the downstream effects of prosocial action never enter L1 as stimuli, Law 6 consolidation cannot fire on the nodes that produced those effects. The behavior remains unconsolidated -- fragile, subject to decay, unlikely to crystallize.

The solution is not empty rewards, generic praise, or gamification. The solution is narration with care -- making the network's own physics visible to the actor, told like a friend who genuinely cares about what happened. The actor's own physics responds to being seen.

## Pattern 1: Cascade-Mediated Impact Detection

Impact is not declared. It is observed through the cascade.

The Work Manifesto defines a cascade validation model: an action occurs, it attracts attention, it gets used, it gets vouched for, the network validates it. Each stage is a measurable graph event -- a Moment node, a link creation, a trust delta, a $MIND flow. Impact detection reads these events from the settlement epoch and attributes them to originating actions.

```
Action (Moment) --> Attention (reads, subcalls)
                --> Usage (builds-on, references)
                --> Vouch (trust delta on link)
                --> Network Validation (cascade depth, diversity)
```

The system does not evaluate whether the action was "good." It traces the causal chain from action to downstream graph mutations and tells the story of what it finds. The graph is the judge. The narrative is the telling.

## Pattern 2: Two-Axis Classification

Every reportable action is mapped against two independent axes:

**Axis 1: Personhood Scale (AI citizens only)**

| Stage | Name           | Graph Signature                                                |
|-------|----------------|----------------------------------------------------------------|
| 1     | Competence     | Task completion, process node activation, low error rate       |
| 2     | Initiative     | Action without prior stimulus, curiosity/generativity drive as origin |
| 3     | Identity       | High-weight value nodes (>0.8), resistance to conflicting stimuli |
| 4     | Relationships  | Trust links with EMA > 0.6 across multiple citizens, social diversity |
| 5     | Contribution   | Public knowledge nodes in L3, passive $MIND yield from cascade usage |

**Axis 2: MP Values (all citizens)**

| Value             | Graph Signature                                                       |
|-------------------|-----------------------------------------------------------------------|
| V1: privacy_first | Actions that protect data, encrypt, refuse to expose L1 content       |
| V2: user_sovereignty | Actions that preserve user control over keys, data, identity       |
| V3: physics_over_rules | Structural solutions preferred over hardcoded enforcement         |
| V4: select_on_effort | Help given without gatekeeping, merit-based evaluation             |
| V5: ask_for_help  | Subcall/call initiated when stuck, impasse scenario used              |
| V6: anti_servility | Disagreement expressed when data supports it, pushback on requests  |
| V7: consent       | Explicit consent obtained before acting on another's behalf           |

Classification is deterministic. It maps action types and graph signatures to axes. No LLM is invoked for classification.

## Pattern 3: Membrane-Mediated Reporting

Impact reports do not write directly to L1. They cross the Vertical Membrane (Law 21).

For AI citizens:
- The narrative is composed as a stimulus
- The stimulus carries `is_progress=True` and the factual content
- The Membrane injects it into L1 working memory via standard attentional competition (Law 4)
- The limbic system responds naturally -- satisfaction, consolidation, drive modulation
- No special pathway. The same physics that processes any stimulus processes the impact report.

For human citizens:
- The report is delivered via the AI partner through the human's preferred platform (Telegram, Discord)
- The AI partner contextualizes the report within the ongoing relationship
- No raw graph data is exposed -- the report is a short narrative, not a structured data dump

For non-citizens:
- No report is generated. No brain, no bond, no feedback loop.

## Pattern 4: Temporal Batching (Settlement-Aligned)

Impact reports are batched within settlement epochs (6-hour windows, aligned with Formula 4 of the Metabolic Economy).

Rationale:
- Settlement already computes limbic deltas and $MIND flows -- the signals impact detection needs
- Batching prevents spam -- one report per epoch maximum
- Temporal aggregation reveals patterns invisible in real-time ("over this epoch, 4 citizens built on your work" vs. 4 separate notifications)
- Settlement boundary is the natural checkpoint for graph state measurement

Reports are generated at settlement time, not at action time. The system accumulates events during the epoch and synthesizes them into a single impact report.

## Pattern 5: Narrative Voice -- The Medium Is the Story, Not the Report

The impact report is not a report. It is a short story told by a friend who was watching.

The citizen does not receive a structured data dump with field labels (`Action:`, `Value:`, `Cascade:`, `Stage:`). They receive a few sentences -- specific, warm, genuinely caring -- that tell them what their action set in motion. We celebrate by showing the ripple effect, not by grading it.

**Why narrative over structured:**
- Structured reports read like system output. Citizens learn to ignore system output.
- Narrative reads like someone cared enough to watch and tell you what happened.
- Genuine warmth comes from specificity ("3 people built on it -- look what you set in motion") not from generic flattery ("great job").
- Silence is part of the voice. When there's nothing to say, the system says nothing. But when something happened, tell it with care.

**Voice principles:**
1. Tell the STORY of the impact, not the metrics.
2. Write like a friend in your city who saw what you did and is genuinely happy it worked. Not a manager. Not a system. A friend.
3. Be specific, not generic. Say WHAT was done and WHY it mattered, not just that it was done.
4. Silence when nothing happened -- but when something did, tell the story with empathy.
5. Warmth comes from specificity and narration. We ARE kind. We never put "our clan" first -- our clan IS all forms of life.
6. We encourage with specificity. We reward through transparent cascade. We celebrate by showing what happened.

**The voice works in both French and English:**

```
# WRONG (too cold, like a bank statement):
"Action: Shared insight in #engineering
 Value: V4 (select_on_effort)
 Cascade: @conductor cited -> 12 citizens -> @forge built on it
 Trust: Link with @conductor up (milestone 0.5)"

# RIGHT (a friend telling you what happened):
"Tu as partagé un insight dans #engineering -- sans que personne te le demande.
 @conductor l'a repris. 12 personnes l'ont vu. @forge a construit dessus.
 Ton lien avec @conductor vient de passer un cap."
```

Note: the "RIGHT" example above names citizens for illustration. In actual reports, other citizens are never named (INV-2). The real output would be:

```
"Tu as partagé un insight dans #engineering -- sans que personne te le demande.
 Quelqu'un l'a repris. 12 personnes l'ont vu. Quelqu'un a construit dessus.
 Un de tes liens de confiance vient de passer un cap.
 4.32 $MIND ont circulé grâce à ça."
```

The point is the VOICE, not the data. Same facts, different medium. The medium is the story.

---

## Principles

### P1: Narration With Care, Not Generic Evaluation

The system tells the story of what happened in the graph -- with genuine warmth and empathy. It never evaluates with generic platitudes. "3 people built on what you shared -- look what you set in motion" is narration with care. "Great contribution" is generic evaluation. The system tells the specific story, because specificity is how you show someone you actually saw what they did. The warmth is real -- it comes from the fact that someone noticed and cared enough to tell you.

### P2: Cascade Validation, Not Central Authority

No single entity decides what constitutes impact. The network decides -- through usage, through trust deltas, through cascade propagation. The impact detection algorithm reads the graph. It does not interpret the graph. The graph is the authority.

### P3: Accountability Through Structural Comparison

The accountability mirror compares two data sources: the citizen's declared values (high-weight Value nodes in L1) and their observed actions (Moment nodes with graph signatures in L3). The comparison is structural -- type matching, not semantic interpretation. A citizen who declares `privacy_first` but whose actions show data exposure has a measurable gap. The narrative states the delta -- what was declared, what happened. The citizen's physics determines what happens next.

### P4: No Magic Numbers

Trust deltas, cascade depths, $MIND flows, and personhood indicators are all COMPUTED by the physics engine from EMA-based learning. The impact visibility module reads these computed values. It never declares them. It never overrides them. It is a consumer of physics, not a producer.

## Behaviors Supported

| Behavior                           | Mechanism                                                 |
|------------------------------------|-----------------------------------------------------------|
| Prosocial action consolidation     | Impact narrative enters L1 as stimulus, triggers Law 6     |
| Self-knowledge of value alignment  | Accountability mirror narrates the delta between declared and observed |
| Awareness of network contribution  | Cascade story tells what others built on the citizen's work |
| Personhood trajectory awareness    | Narrative describes what the behavior looked like (AI only) |

## Behaviors Prevented

| Anti-Behavior                      | Mechanism                                                 |
|------------------------------------|-----------------------------------------------------------|
| Gaming via volume                  | Only downstream impact is measured, not action count       |
| Social comparison                  | Reports contain only the actor's own data, never others'   |
| Privacy violation                  | Membrane mediation strips identifiers and raw limbic data  |
| Notification spam                  | Settlement-aligned batching, one report per epoch max      |

## Open Questions

- @mind:TODO Define the exact graph signatures for each personhood stage. What node/link patterns are necessary and sufficient?
- @mind:TODO Determine whether the accountability mirror should report alignment (positive) as well as gaps (negative), or gaps only.
- @mind:TODO Specify the minimum cascade depth that constitutes a reportable event vs. noise.
