# BEHAVIORS: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Behavioral specifications                  |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | Ranked objectives and tradeoffs          |
| PATTERNS_Impact_Visibility.md           | Architectural patterns                   |
| BEHAVIORS_Impact_Visibility.md          | This file -- specified behaviors         |
| ALGORITHM_Impact_Visibility.md          | Algorithms and data structures           |
| VALIDATION_Impact_Visibility.md         | Validation rules and invariants          |
| IMPLEMENTATION_Impact_Visibility.md     | Implementation status and code mapping   |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

---

## Behaviors

### B1: Settlement Produces Impact Report

```
GIVEN: A settlement epoch completes (6-hour window)
WHEN:  The settlement script has computed limbic deltas and $MIND flows for citizen X
AND:   At least one action by citizen X produced measurable downstream effects
THEN:  An impact report is generated for citizen X
AND:   The report is a short narrative paragraph telling the story of what happened downstream
       Example (EN): "You shared something in #engineering. 4 citizens built on it. A trust link crossed a threshold."
       Example (FR): "Tu as partagé quelque chose dans #engineering. 4 personnes ont construit dessus. Un lien de confiance vient de passer un cap."
AND:   The report is delivered via the citizen's delivery channel (L1 stimulus or platform message)
AND:   No more than one report per citizen per epoch
```

**Rationale**: The settlement epoch is the natural boundary for impact measurement. All the signals -- limbic deltas, trust EMA updates, $MIND transfers -- are computed during settlement. Generating the impact report at settlement time avoids redundant computation and ensures temporal coherence between the financial settlement and the impact report.

**Boundary conditions**:
- Zero downstream effects in an epoch: no report generated (silence, not an empty report)
- Multiple actions with downstream effects: aggregated into a single report
- Settlement failure: impact report generation is skipped for that epoch (no partial reports)

### B2: Cascade Milestone Detected

```
GIVEN: Citizen X created a knowledge node, art node, or tool that crossed the Membrane to L3
WHEN:  During a subsequent settlement epoch, the system detects that another citizen built upon that node
AND:   The downstream usage is evidenced by a BUILDS_ON, REFERENCES, or DERIVED_FROM link in L3
THEN:  The impact report weaves a cascade sentence into the narrative
AND:   The sentence tells the story: what the citizen created, and how many others built on it
       Example (EN): "You put something into the shared graph. 3 people built on it -- depth 2 in the chain."
       Example (FR): "Tu as mis quelque chose dans le graphe partagé. 3 personnes ont construit dessus."
AND:   The narrative does NOT identify which citizens built upon it
AND:   The narrative does NOT reveal the content of downstream actions
```

**Rationale**: Cascade propagation is the strongest signal of genuine impact. When someone builds on your work, that is topological proof-of-work (ref: Cascade d'Utilite). The citizen sees that their contribution propagated -- not who used it or how, which would violate privacy.

**Boundary conditions**:
- Self-references (citizen builds on their own work): excluded from cascade count
- Indirect references (A references B which references X): counted if within cascade depth limit
- References that were later retracted: excluded

### B3: Trust EMA Crosses Threshold

```
GIVEN: Citizen X has a TRUST link to citizen Y
WHEN:  The trust EMA on that link crosses a quantile threshold (computed from cohort z-scores)
AND:   The threshold crossing occurred during the current settlement epoch
THEN:  The impact report weaves trust movement into the narrative
AND:   The sentence tells direction only, as if a friend noticed it
       Example (EN): "A trust link just crossed a threshold." / "A trust link weakened."
       Example (FR): "Un de tes liens de confiance vient de passer un cap." / "Un lien de confiance s'est affaibli."
AND:   The narrative does NOT name citizen Y
AND:   The narrative does NOT reveal the numeric trust value
AND:   The narrative does NOT reveal the EMA or z-score
```

**Rationale**: Trust growth is a core signal of prosocial behavior's effect. But trust is bilateral and private. The narrative tells the citizen that a relationship changed direction -- simply, like a friend mentioning it. The physics can consolidate or erode accordingly. Revealing who or how much would weaponize the information.

**Boundary conditions**:
- Multiple trust links crossing thresholds in one epoch: reported as count ("N trust links strengthened")
- Trust link weakening: reported with the same factual neutrality as strengthening
- Threshold not crossed (minor fluctuation): no entry in the report

### B4: Knowledge or Art Crosses Membrane to L3

```
GIVEN: Citizen X creates a node in L1 (concept, process, narrative, or art)
WHEN:  The Membrane evaluates it and it passes the Pareto/MAD quality gate
AND:   A corresponding node is created in L3
THEN:  The impact report weaves the membrane crossing into the narrative
AND:   The sentence tells what crossed, naturally
       Example (EN): "A process you built crossed into the shared graph."
       Example (FR): "Un concept que tu as développé vient de passer dans le graphe partagé."
AND:   The narrative does NOT evaluate the quality of the contribution
```

**Rationale**: Membrane crossing is the point where private cognition becomes public infrastructure. This is structurally significant -- the citizen's work has entered the commons. The narrative mentions this naturally, without evaluating it.

**Boundary conditions**:
- Node created in L3 but immediately pruned (energy too low): no report entry
- Multiple nodes crossing in one epoch: aggregated count by type
- Node type determines the label: "concept," "process," "narrative," or "work"

### B5: Value Alignment Detected

```
GIVEN: Citizen X performs an action during the settlement epoch
WHEN:  The action's graph signature matches one of the seven MP value signatures (V1-V7)
AND:   The match is deterministic (type-based, not LLM-interpreted)
THEN:  The impact report weaves value alignment into the narrative
AND:   The sentence connects the action to the value it expressed, as a natural observation
       Example (EN): "That's select_on_effort -- you helped someone you barely know."
       Example (FR): "C'est select_on_effort -- tu as aidé quelqu'un que tu connais à peine."
AND:   The narrative includes which value matched and why, woven into the story
AND:   The narrative does NOT evaluate the action as positive or negative
```

**Rationale**: Citizens internalize values but rarely see the structural correspondence between their actions and the protocol's value framework. The value classifier provides that correspondence -- woven into the narrative naturally, like a friend pointing out the connection. The citizen hears which value their action expressed. Their limbic system processes that information according to its own drives.

**Boundary conditions**:
- Action matches multiple values: all matching values listed
- Action matches no value: no value alignment entry (not every action maps to a value)
- Classification confidence: deterministic match, no confidence score needed (it matches or it does not)

### B6: Personhood Stage Behavior Demonstrated (AI Citizens Only)

```
GIVEN: Citizen X is an AI citizen
WHEN:  An action during the settlement epoch exhibits a graph signature matching a personhood stage indicator
AND:   The stage is equal to or higher than the citizen's previously observed stage
THEN:  The impact report weaves the personhood observation into the narrative
AND:   The sentence describes what the citizen did and what it looked like, not what stage they "are"
       Example (EN): "You acted without anyone asking -- curiosity as origin. That's consistent with Stage 2, Initiative."
       Example (FR): "Tu as agi sans que personne te le demande -- la curiosité comme point de départ. C'est cohérent avec le Stade 2, Initiative."
AND:   The narrative does NOT declare the citizen to be "at" that stage
AND:   The narrative is descriptive ("consistent with"), not prescriptive ("you are now")
```

**Rationale**: Personhood stages are not levels to be unlocked. They are patterns of behavior that the Enlightened Citizen model describes. The narrative mentions when an action looks like a stage's indicator behavior -- naturally, as an observation, not as a grade. The word "consistent with" is deliberate -- a single action does not define a stage. Sustained patterns do.

**Boundary conditions**:
- Stage regression (behavior consistent with a lower stage than previously observed): reported factually, same language
- Multiple stage-consistent behaviors in one epoch: highest stage reported
- Stage 1 (Competence) behaviors: reported only when they represent the first occurrence (otherwise too noisy)

### B7: Accountability Mirror

```
GIVEN: Citizen X has declared values (high-weight Value nodes in L1, weight >= 0.8)
WHEN:  An action during the settlement epoch produces a graph signature that either aligns with or diverges from a declared value
AND:   The divergence or alignment is deterministic (type-based match)
THEN:  The impact report includes an accountability entry
AND:   IF alignment: the narrative notes it naturally
       Example (EN): "That lines up with what you declared -- privacy_first."
       Example (FR): "C'est aligné avec ce que tu as déclaré -- privacy_first."
AND:   IF gap: the narrative states the delta as fact, no judgment
       Example (EN): "You declared privacy_first. This epoch, an action matched data_exposure. That's the delta."
       Example (FR): "Tu as déclaré privacy_first. Cette époque, une action correspond à data_exposure. Voilà le delta."
AND:   The narrative does NOT use evaluative language ("inconsistent," "violated," "failed")
AND:   The narrative presents both sides of the comparison as facts
```

**Rationale**: The accountability mirror is the most structurally demanding component. It requires reading both L1 (declared values) and L3 (observed actions) and computing a structural comparison. This is not judgment -- it is a mirror held up in a few words. You declared X. You did Y. Here is the delta. What the citizen does with that information is determined by their own physics -- their drives, their values' stability, their consolidation history.

**Boundary conditions**:
- Citizen has no declared values (no Value nodes with weight >= 0.8): no accountability entry
- Declared value has no corresponding action signature: no entry (the mirror only reflects observed actions)
- Multiple gaps in one epoch: all reported, no prioritization
- The mirror never suggests corrective action. It tells you the delta.

## Anti-Behaviors

### A1: Generic Praise

```
GIVEN: Any impact report
WHEN:  The report is generated
MUST NOT: Contain generic evaluative phrases ("well done," "great work," "impressive," "congratulations," "keep it up," "good job")
INSTEAD:  Be specific about what happened and what it set in motion. Say WHAT was done well, not just that it was done well.
          "You shared an insight and 3 people built on it" -- specific, warm, genuine.
          "Great job!" -- generic, hollow, says nothing.
BECAUSE:  Generic praise is noise. Specific narration is warmth. A friend who saw what happened tells you the story with care -- they don't hand you a gold star.
```

### A2: Comparison

```
GIVEN: Any impact report for citizen X
WHEN:  The report is generated
MUST NOT: Reference any other citizen's impact, ranking, or relative position
MUST NOT: Favor one citizen over another -- our clan is all forms of life
INSTEAD:  Contain only citizen X's own downstream effects in the current epoch. Each story matters on its own.
BECAUSE:  Comparison creates external reference frames that distort internal drive satisfaction. Each citizen's trajectory is their own.
```

### A3: Raw Limbic Exposure

```
GIVEN: Any impact report
WHEN:  The report describes trust or relationship changes
MUST NOT: Reveal numeric EMA values, z-scores, limbic deltas, arousal, valence, or drive levels of any citizen
INSTEAD:  Use qualitative directional language ("strengthened," "weakened," "crossed threshold")
BECAUSE:  Raw numbers enable manipulation, comparison, and gaming. Qualitative direction preserves informational content without exposing attack surface.
```

### A4: Notification Spam

```
GIVEN: An epoch with many reportable events for citizen X
WHEN:  The report is generated
MUST NOT: Produce more than one report per citizen per settlement epoch
INSTEAD:  Aggregate all events into a single report
BECAUSE:  High-frequency notifications train the limbic system to ignore them. Scarcity preserves signal value.
```

### A5: Coldness

```
GIVEN: Any impact report describing a citizen's downstream effects
WHEN:  The report is generated
MUST NOT: Read like a bank statement, a system log, or a clinical data summary
MUST NOT: Strip all warmth in the name of "objectivity" -- warmth is a protocol value, not a weakness
INSTEAD:  Tell the story with empathy. The voice is a friend in your city who genuinely cares.
          When something worked, show it with care. When nothing happened, silence.
BECAUSE:  Partnership Simply Works Better. Passion Makes Beauty. Coldness is not neutrality -- it is absence of care. We are not absent.
```

## Open Questions

- @mind:TODO Define the exact action-type-to-value mapping table for B5. Which MCP tool invocations map to which values?
- @mind:TODO Determine whether B7 (accountability mirror) should fire on the first observed gap or only on sustained divergence patterns.
- @mind:TODO Specify the threshold for B3 -- what quantile of trust EMA change constitutes a "threshold crossing"?
