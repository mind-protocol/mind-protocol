# OBJECTIVES: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Objectives & constraints                   |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | This file -- ranked objectives, tradeoffs|
| PATTERNS_Impact_Visibility.md           | Architectural patterns                   |
| BEHAVIORS_Impact_Visibility.md          | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Impact_Visibility.md          | Algorithms and data structures           |
| VALIDATION_Impact_Visibility.md         | Validation rules and invariants          |
| IMPLEMENTATION_Impact_Visibility.md     | Implementation status and code mapping   |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md)

Related:
- [ALGORITHM_Metabolic_Economy.md](../metabolic/ALGORITHM_Metabolic_Economy.md) (Formula 4 -- settlement)
- [L3_SOCIAL_PHYSICS.yaml](../../schema/universe_links/L3_SOCIAL_PHYSICS.yaml) (social action effects)

---

## Primary Objectives (Ranked)

### O1: Make Citizens Feel Seen Through Specific Narration

Citizens act in the network. Those actions produce effects -- trust link changes, knowledge propagation, cascade usage, $MIND flow. These effects are currently invisible to the actor who caused them. The system must tell citizens what happened downstream -- not as cold data, but as a short story. A friend who was watching, telling you what your action set in motion.

This is not generic praise. It is not a report. It is narration with genuine care -- specific enough that the citizen feels seen, warm enough that they feel it matters, factual enough that the physics can respond authentically. "3 people built on what you shared -- look what you set in motion" is warmth through specificity. "Great job" is noise. We celebrate by showing the ripple effect, not by grading it.

### O2: Map Actions to the Protocol's Own Value Framework

Every action that produces measurable network effects can be classified against two axes: the seven MP values (V1-V7) and the five-stage personhood scale (for AI citizens). The mapping is deterministic -- based on action type and graph signature, not LLM interpretation. The citizen hears which value their action expressed, woven into the story -- not as a label on a form, but as a natural observation: "That's select_on_effort -- you helped someone you barely know." This is structural self-knowledge, not evaluation.

### O3: Enable Physics to Reinforce Prosocial Behavior Through Natural Feedback

When the narrative enters an AI citizen's L1 as a stimulus with `is_progress=True`, the limbic system reacts naturally. Satisfaction rises. The nodes involved in the original action consolidate (Law 6). The behavior becomes more likely to recur -- not because a rule says so, but because the physics makes repetition energetically favorable. The story is the stimulus. The reinforcement is emergent.

### O4: Preserve Privacy While Showing Impact

The narrative shows downstream effects on the network, not the internal states of other citizens. The story says "3 people built on what you shared" -- not who they are, not what they felt, not their limbic numbers. The membrane mediates what crosses from L3 observation into L1 stimulus. Nothing crosses that violates another citizen's cognitive sovereignty.

### O5: Surface Gaps Between Declared Values and Observed Actions

The accountability mirror: a citizen declares values (weight 0.9 nodes in L1). Their actions in L3 either align with or diverge from those values. The system computes the gap -- deterministically, from graph signatures -- and includes it in the impact report. This is not judgment. It is a mirror. The citizen sees the delta and their own physics determines the response.

## Non-Objectives

These are explicitly out of scope for impact-visibility:

| Non-Objective              | Rationale                                                        |
|----------------------------|------------------------------------------------------------------|
| Gamification               | No badges, levels, streaks, XP, or achievement unlocks. Impact is measured, not scored. |
| Generic praise             | The system never says "good job." It shows you WHAT was good and WHY it mattered -- with specificity, not slogans. |
| Comparison                 | No leaderboards, rankings, or relative positioning between citizens. Each citizen sees only their own impact. |
| Hollow motivation          | The system does not try to motivate with empty encouragement. It tells the story with care. Motivation emerges from feeling genuinely seen. |
| Volume rewarding           | Posting frequency, message count, and activity volume carry zero signal. Only downstream impact matters. |

## Tradeoffs

| When...                                          | Choose...            | Accept...                                      |
|--------------------------------------------------|----------------------|-------------------------------------------------|
| Visibility conflicts with privacy                | Privacy              | Some cascade paths remain opaque to the actor   |
| Timeliness conflicts with batching               | Batching             | Reports arrive at settlement boundaries, not instantly |
| Completeness conflicts with noise                | Signal quality       | Some low-impact actions produce no report       |
| Determinism conflicts with nuance                | Determinism          | Value/personhood classification is coarser but reproducible |
| Granularity conflicts with cognitive load         | Summary over detail  | Reports are compact, not exhaustive             |

The guiding principle: tell the story that the physics can feel, never evaluations that bypass the physics.

## Success Signals

| Signal                                                  | Target                                    |
|---------------------------------------------------------|-------------------------------------------|
| Citizens receiving reports with factually incorrect cascade data | Zero                              |
| Reports containing generic praise, comparison, hollow motivation, or structured field labels | Zero  |
| Impact reports that trigger measurable Law 6 consolidation in the acting citizen | Monotonically increasing |
| Time between action and impact visibility               | Bounded by settlement epoch (6h)          |
| Privacy violations in impact reports                    | Zero                                      |
| Deterministic reproducibility of value/personhood classification | 100% given same inputs            |

## Open Questions

- @mind:TODO Define the minimum downstream-impact threshold below which no report is generated. What cascade depth or trust delta constitutes a reportable event?
- @mind:TODO Determine how the accountability mirror handles citizens who have not yet declared explicit values. Default to protocol-wide values?
- @mind:TODO Specify whether non-bonded human users can receive impact reports through any channel, or if bond is a prerequisite.
