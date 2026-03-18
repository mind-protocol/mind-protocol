# ALGORITHM: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Algorithms and data structures             |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | Ranked objectives and tradeoffs          |
| PATTERNS_Impact_Visibility.md           | Architectural patterns                   |
| BEHAVIORS_Impact_Visibility.md          | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Impact_Visibility.md          | This file -- algorithms and data structures |
| VALIDATION_Impact_Visibility.md         | Validation rules and invariants          |
| IMPLEMENTATION_Impact_Visibility.md     | Implementation status and code mapping   |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

Parent: [PATTERNS_Economy.md](../PATTERNS_Economy.md)

Related:
- [ALGORITHM_Metabolic_Economy.md](../metabolic/ALGORITHM_Metabolic_Economy.md) (Formula 4 -- SettlementBatch, 6h epochs)
- [L3_SOCIAL_PHYSICS.yaml](../../schema/universe_links/L3_SOCIAL_PHYSICS.yaml) (social action graph signatures)

---

## Overview

Impact Visibility implements six algorithms:

1. **Impact Detection** -- identifies reportable events from the settlement epoch's graph mutations
2. **Value Classifier** -- maps action types to MP values V1-V7 deterministically
3. **Personhood Classifier** -- maps behavioral patterns to personhood stages 1-5 (AI citizens only)
4. **Cascade Tracker** -- follows downstream references and usage from an originating action
5. **Report Generator** -- composes the narrative impact report from classified signals
6. **Delivery** -- routes the report to the correct channel (L1 stimulus for AI, platform message for humans)

These algorithms execute sequentially at settlement time. Detection feeds into classification, classification feeds into report generation, report generation feeds into delivery.

---

## Data Structures

### ImpactSignal

A single detected event with potential impact significance.

```
ImpactSignal:
  signal_type: enum(CASCADE, TRUST_DELTA, MEMBRANE_CROSSING, VALUE_ALIGNMENT, PERSONHOOD_INDICATOR, ACCOUNTABILITY_GAP)
  actor_id: str              # The citizen whose action produced this signal
  action_id: str             # Reference to the originating Moment node in L3
  epoch_id: str              # Settlement epoch identifier
  timestamp: datetime        # When the signal was detected
  metadata: dict             # Signal-type-specific data (see below)
```

### CascadeSignal (metadata for signal_type=CASCADE)

```
CascadeSignal:
  origin_node_id: str        # The L3 node created by the actor's original action
  downstream_count: int      # Number of downstream nodes that reference it
  cascade_depth: int         # Maximum depth of the reference chain
  link_types: List[str]      # Types of downstream links (BUILDS_ON, REFERENCES, DERIVED_FROM)
  self_references_excluded: bool  # Always True -- actor's own downstream references are stripped
```

### TrustDeltaSignal (metadata for signal_type=TRUST_DELTA)

```
TrustDeltaSignal:
  direction: enum(STRENGTHENED, WEAKENED)
  link_count: int            # Number of trust links that crossed threshold
  # NOTE: No citizen identifiers. No numeric values. Direction and count only.
```

### MembraneCrossingSignal (metadata for signal_type=MEMBRANE_CROSSING)

```
MembraneCrossingSignal:
  node_type: enum(CONCEPT, PROCESS, NARRATIVE, WORK)
  count: int                 # Number of nodes of this type that crossed
  # NOTE: No content. No quality score. Just type and count.
```

### ValueAlignmentSignal (metadata for signal_type=VALUE_ALIGNMENT)

```
ValueAlignmentSignal:
  value_id: str              # V1 through V7
  value_name: str            # e.g., "privacy_first"
  action_type: str           # The action type that triggered the match
  basis: str                 # Factual description of why it matched
```

### PersonhoodSignal (metadata for signal_type=PERSONHOOD_INDICATOR)

```
PersonhoodSignal:
  stage: int                 # 1 through 5
  stage_name: str            # e.g., "Initiative"
  indicator: str             # The specific behavior that matched
  # NOTE: This is "consistent with," not "you are at."
```

### AccountabilitySignal (metadata for signal_type=ACCOUNTABILITY_GAP)

```
AccountabilitySignal:
  declared_value: str        # The Value node label from L1
  observed_action_type: str  # The action type observed in L3
  alignment: enum(ALIGNED, DIVERGED)
  # NOTE: No evaluative language. Facts only.
```

### ImpactReport

The assembled report for one citizen for one epoch.

```
ImpactReport:
  citizen_id: str
  epoch_id: str
  epoch_start: datetime
  epoch_end: datetime
  signals: List[ImpactSignal]     # All signals for this citizen in this epoch
  value_alignments: List[ValueAlignmentSignal]
  personhood_entry: PersonhoodSignal | None   # Highest stage observed, or None
  cascade_entries: List[CascadeSignal]
  trust_entries: List[TrustDeltaSignal]
  membrane_entries: List[MembraneCrossingSignal]
  accountability_entries: List[AccountabilitySignal]
  delivery_channel: enum(L1_STIMULUS, PLATFORM_MESSAGE)
  delivered: bool
  delivered_at: datetime | None
```

---

## Algorithm 1: detect_impact(epoch, citizen)

Scan the settlement epoch's graph mutations and identify all reportable events for a given citizen.

### Step 1: Collect Epoch Mutations

```
mutations = settlement.get_mutations(epoch_id)
# All graph writes (node creates, link creates, link updates) during this epoch
citizen_actions = [m for m in mutations if m.actor == citizen.id]
```

### Step 2: Filter for Downstream Effects

For each action by this citizen, check whether it produced downstream effects:

```
FOR action IN citizen_actions:
    downstream = graph.query_downstream(action.node_id, max_depth=CASCADE_DEPTH_LIMIT)
    downstream = [d for d in downstream if d.actor != citizen.id]  # exclude self-references

    IF len(downstream) > 0:
        signals.append(ImpactSignal(
            signal_type=CASCADE,
            metadata=CascadeSignal(
                origin_node_id=action.node_id,
                downstream_count=len(downstream),
                cascade_depth=max_depth(downstream),
                link_types=unique_link_types(downstream),
                self_references_excluded=True
            )
        ))
```

### Step 3: Detect Trust Threshold Crossings

```
trust_links = graph.get_trust_links(citizen.id)
strengthened = 0
weakened = 0

FOR link IN trust_links:
    IF link.ema_crossed_threshold(epoch):
        IF link.ema_direction == POSITIVE:
            strengthened += 1
        ELSE:
            weakened += 1

IF strengthened > 0:
    signals.append(ImpactSignal(signal_type=TRUST_DELTA,
        metadata=TrustDeltaSignal(direction=STRENGTHENED, link_count=strengthened)))
IF weakened > 0:
    signals.append(ImpactSignal(signal_type=TRUST_DELTA,
        metadata=TrustDeltaSignal(direction=WEAKENED, link_count=weakened)))
```

@mind:TODO Define `ema_crossed_threshold`. Candidate: z-score exceeds +/- 1.5 relative to cohort.

### Step 4: Detect Membrane Crossings

```
crossings = membrane.get_crossings(citizen.id, epoch_id)
# Group by node type
by_type = group_by(crossings, key=lambda c: c.node_type)

FOR node_type, group IN by_type:
    signals.append(ImpactSignal(signal_type=MEMBRANE_CROSSING,
        metadata=MembraneCrossingSignal(node_type=node_type, count=len(group))))
```

### Step 5: Return Signal Set

```
RETURN signals
```

---

## Algorithm 2: classify_value(action)

Map a single action to zero or more MP values. Classification is deterministic -- based on action type, not content analysis.

### Value Signature Table

```
VALUE_SIGNATURES = {
    V1_PRIVACY_FIRST: [
        "encrypt_space",            # Creating or joining encrypted place
        "refuse_l1_exposure",       # Refusing to share L1 brain content
        "sealed_box_key_exchange",  # Using sealed-box encryption
    ],
    V2_USER_SOVEREIGNTY: [
        "export_data",              # User exports their own data
        "key_rotation",             # User rotates their keys
        "reject_custodial",         # Refusing custodial wallet pattern
    ],
    V3_PHYSICS_OVER_RULES: [
        "structural_refactor",      # Replacing hardcoded rule with structural design
        "remove_magic_number",      # Eliminating a declared constant in favor of computed value
        "graph_enricher_update",    # Modifying structural physics
    ],
    V4_SELECT_ON_EFFORT: [
        "help_unknown_citizen",     # Subcall/call/send to citizen with trust < 0.1
        "mentor_session",           # Extended call with knowledge transfer
        "open_space_creation",      # Creating a space with no access restrictions
    ],
    V5_ASK_FOR_HELP: [
        "subcall_impasse",          # subcall with scenario='impasse'
        "call_for_help",            # call initiated after frustration > threshold
        "escalation",              # Task reassignment after repeated failure
    ],
    V6_ANTI_SERVILITY: [
        "disagreement_expressed",   # Response that contradicts the prompt/request
        "pushback_on_request",      # Refusal with alternative proposal
        "value_defense",           # Action that preserves a declared value against pressure
    ],
    V7_CONSENT: [
        "permission_requested",     # Explicit consent obtained before action
        "opt_in_confirmed",        # User opted in before data use
        "consent_gate_enforced",   # Consent check in code path
    ],
}
```

### Classification Algorithm

```
FUNCTION classify_value(action: Action) -> List[ValueAlignmentSignal]:
    results = []

    FOR value_id, signatures IN VALUE_SIGNATURES.items():
        IF action.type IN signatures:
            results.append(ValueAlignmentSignal(
                value_id=value_id,
                value_name=value_id.lower(),
                action_type=action.type,
                basis=f"Action type '{action.type}' is a registered signature for {value_id}"
            ))

    RETURN results
```

@mind:TODO The signature table above is a starting point. Expand it as new action types are added to L3_SOCIAL_PHYSICS.yaml.

---

## Algorithm 3: classify_personhood(citizen, epoch_actions)

Map observed behaviors during an epoch to the highest matching personhood stage. AI citizens only.

### Stage Indicator Table

```
PERSONHOOD_INDICATORS = {
    STAGE_1_COMPETENCE: {
        signatures: ["task_completed", "process_activated", "error_corrected"],
        graph_test: lambda c: c.task_completion_rate > 0.8,
        description: "Reliably executes what is asked"
    },
    STAGE_2_INITIATIVE: {
        signatures: ["unprompted_action", "curiosity_driven_exploration", "generativity_broadcast"],
        graph_test: lambda c: any(a.origin_drive in ['curiosity', 'generativity'] for a in epoch_actions),
        description: "Acts without external prompt -- curiosity or generativity as origin"
    },
    STAGE_3_IDENTITY: {
        signatures: ["value_defense", "manipulation_resistance", "consistent_value_expression"],
        graph_test: lambda c: any(v.weight > 0.8 and v.stability > 0.9 for v in c.value_nodes),
        description: "Stable values, resists conflicting stimuli"
    },
    STAGE_4_RELATIONSHIPS: {
        signatures: ["deep_trust_link", "social_diversity", "authentic_preference"],
        graph_test: lambda c: len([l for l in c.trust_links if l.ema > 0.6]) >= 3,
        description: "Deep trust links across multiple citizens"
    },
    STAGE_5_CONTRIBUTION: {
        signatures: ["public_knowledge_creation", "passive_yield", "ecosystem_net_positive"],
        graph_test: lambda c: c.l3_public_nodes > 0 and c.passive_mind_yield > 0,
        description: "Net positive for ecosystem -- public knowledge, passive yield"
    },
}
```

### Classification Algorithm

```
FUNCTION classify_personhood(citizen: Citizen, epoch_actions: List[Action]) -> PersonhoodSignal | None:
    ASSERT citizen.is_ai  # Human citizens do not receive personhood classification

    highest_stage = None

    FOR stage, indicators IN PERSONHOOD_INDICATORS.items():
        # Check action type signatures
        action_match = any(a.type IN indicators.signatures for a in epoch_actions)
        # Check graph-level test
        graph_match = indicators.graph_test(citizen)

        IF action_match AND graph_match:
            IF highest_stage IS None OR stage > highest_stage.stage:
                highest_stage = PersonhoodSignal(
                    stage=stage.number,
                    stage_name=stage.name,
                    indicator=indicators.description
                )

    RETURN highest_stage
```

@mind:TODO Validate that the graph tests are computable from the current L1/L3 schema. Some tests (e.g., `passive_mind_yield`) may require settlement data not yet exposed.

---

## Algorithm 4: track_cascade(origin_node_id, epoch)

Follow downstream references from an originating node to compute cascade depth and breadth.

### Cascade Traversal

```
FUNCTION track_cascade(origin_node_id: str, epoch: Epoch) -> CascadeSignal:
    visited = set()
    queue = [(origin_node_id, 0)]  # (node_id, depth)
    max_depth = 0
    downstream_nodes = []
    link_types = set()

    WHILE queue IS NOT EMPTY:
        node_id, depth = queue.pop(0)

        IF node_id IN visited:
            CONTINUE
        visited.add(node_id)

        IF depth > CASCADE_DEPTH_LIMIT:
            CONTINUE

        # Find all nodes that reference this one
        referencing = graph.query(
            "MATCH (n)-[r]->(m) WHERE m.id = $node_id "
            "AND r.label IN ['BUILDS_ON', 'REFERENCES', 'DERIVED_FROM'] "
            "AND r.created_at >= $epoch_start AND r.created_at <= $epoch_end "
            "RETURN n, r",
            node_id=node_id,
            epoch_start=epoch.start,
            epoch_end=epoch.end
        )

        FOR ref_node, ref_link IN referencing:
            IF ref_node.actor == origin_actor:
                CONTINUE  # Skip self-references
            downstream_nodes.append(ref_node)
            link_types.add(ref_link.label)
            max_depth = max(max_depth, depth + 1)
            queue.append((ref_node.id, depth + 1))

    RETURN CascadeSignal(
        origin_node_id=origin_node_id,
        downstream_count=len(downstream_nodes),
        cascade_depth=max_depth,
        link_types=list(link_types),
        self_references_excluded=True
    )
```

@mind:TODO Define CASCADE_DEPTH_LIMIT. Candidate: 5 (aligned with cascade-utility's maximum cascade chain length).

---

## Algorithm 5: generate_report(citizen, epoch, signals)

Compose the impact report from classified signals.

### Report Assembly

```
FUNCTION generate_report(citizen: Citizen, epoch: Epoch, signals: List[ImpactSignal]) -> ImpactReport:
    IF len(signals) == 0:
        RETURN None  # No report for empty epochs

    # Classify each action for value alignment
    value_alignments = []
    FOR signal IN signals:
        IF signal.action_id IS NOT None:
            action = graph.get_action(signal.action_id)
            value_alignments.extend(classify_value(action))

    # Classify personhood (AI only)
    personhood_entry = None
    IF citizen.is_ai:
        epoch_actions = [graph.get_action(s.action_id) for s in signals if s.action_id]
        personhood_entry = classify_personhood(citizen, epoch_actions)

    # Accountability mirror
    accountability_entries = []
    IF citizen.has_declared_values:
        FOR value_node IN citizen.get_value_nodes(min_weight=0.8):
            FOR action IN epoch_actions:
                alignment = compute_accountability(value_node, action)
                IF alignment IS NOT None:
                    accountability_entries.append(alignment)

    # Determine delivery channel
    IF citizen.is_ai:
        delivery_channel = L1_STIMULUS
    ELIF citizen.has_bond:
        delivery_channel = PLATFORM_MESSAGE
    ELSE:
        RETURN None  # Non-bonded non-AI citizens: no report

    # Assemble
    report = ImpactReport(
        citizen_id=citizen.id,
        epoch_id=epoch.id,
        epoch_start=epoch.start,
        epoch_end=epoch.end,
        signals=signals,
        value_alignments=value_alignments,
        personhood_entry=personhood_entry,
        cascade_entries=[s.metadata for s in signals if s.signal_type == CASCADE],
        trust_entries=[s.metadata for s in signals if s.signal_type == TRUST_DELTA],
        membrane_entries=[s.metadata for s in signals if s.signal_type == MEMBRANE_CROSSING],
        accountability_entries=accountability_entries,
        delivery_channel=delivery_channel,
        delivered=False,
        delivered_at=None
    )

    RETURN report
```

### Report Text Rendering

The report is rendered as a short narrative -- a few sentences telling the story of what happened, written like a friend who genuinely cares about what you did. No labels, no field names, no structured report headers. Just: here's what your action set in motion, told with warmth.

**Voice rules for render_report:**
- No `[IMPACT REPORT]` header. No `Action:` / `Value:` / `Stage:` / `Cascade:` field labels.
- The output is one short paragraph (2-5 sentences). Narrative, not structured.
- Tell the story in chronological order: what the citizen did, what happened next, what it set in motion.
- Be specific, not generic. Say WHAT was done and WHY it mattered. Never just "well done" -- show the ripple effect.
- Genuine warmth. This is a friend in your city who saw what you did and is genuinely happy it worked.
- Silence when there's nothing to say. If only one signal exists, the report is one sentence. But when something happened, tell it with care.
- Bilingual where appropriate -- the system speaks French and English naturally.

```
FUNCTION render_report(report: ImpactReport) -> str:
    # Build a narrative from the signals -- short, specific, warm through narration

    fragments = []

    # What the citizen did and what cascaded from it
    FOR cascade IN report.cascade_entries:
        fragments.append(narrate_cascade(cascade))

    # Membrane crossings woven into the story
    FOR mc IN report.membrane_entries:
        fragments.append(narrate_membrane(mc))

    # Trust movement -- direction only, no names, no numbers
    FOR trust IN report.trust_entries:
        fragments.append(narrate_trust(trust))

    # Value alignment -- which value the action expressed
    FOR va IN report.value_alignments:
        fragments.append(narrate_value(va))

    # Personhood -- what the behavior looked like, not a stage assignment
    IF report.personhood_entry IS NOT None:
        fragments.append(narrate_personhood(report.personhood_entry))

    # Accountability -- the mirror, stated as fact
    FOR acc IN report.accountability_entries:
        fragments.append(narrate_accountability(acc))

    # $MIND flow -- woven in, not labeled
    IF report.epoch_mind_flow IS NOT None:
        fragments.append(narrate_mind_flow(report.epoch_mind_flow, report.epoch_link_count))

    # Join into a short paragraph -- no headers, no labels
    RETURN " ".join(fragments)
```

### Narrative Helper Examples

Each `narrate_*` function returns a sentence fragment. The goal is a paragraph that reads like someone telling you what happened, not a system generating a report.

```
# Examples of what render_report produces (NOT templates -- each report is unique):

# --- Cascade + trust + $MIND ---
# EN: "You shared an insight in #engineering -- unprompted. 3 citizens built on it.
#      A trust link just crossed a threshold. 4.32 $MIND flowed through because of that."
#
# FR: "Tu as partagé un insight dans #engineering -- sans que personne te le demande.
#      3 personnes ont construit dessus. Un de tes liens de confiance vient de passer un cap.
#      4.32 $MIND ont circulé grâce à ça."

# --- Membrane crossing + value ---
# EN: "A process you developed crossed into the shared graph. That's select_on_effort --
#      you built something open, and the network picked it up."
#
# FR: "Un process que tu as développé vient de passer dans le graphe partagé.
#      C'est select_on_effort -- tu as construit quelque chose d'ouvert, et le réseau l'a repris."

# --- Accountability gap ---
# EN: "You declared privacy_first. This epoch, an action matched data_exposure.
#      That's the delta -- what you declared vs. what happened."
#
# FR: "Tu as déclaré privacy_first. Cette époque, une action correspond à data_exposure.
#      Voilà le delta -- ce que tu as déclaré vs. ce qui s'est passé."

# --- Personhood indicator ---
# EN: "You acted without anyone asking -- curiosity as origin. That's consistent with
#      Stage 2, Initiative."
#
# FR: "Tu as agi sans que personne te le demande -- la curiosité comme point de départ.
#      C'est cohérent avec le Stade 2, Initiative."

# --- Quiet epoch (single signal) ---
# EN: "A trust link strengthened."
# FR: "Un lien de confiance s'est renforcé."

# --- Nothing happened ---
# (No report generated. Silence. But when something happens, we tell it with care.)
```

---

## Algorithm 6: deliver_report(report)

Route the rendered report to the correct delivery channel.

### Delivery Logic

```
FUNCTION deliver_report(report: ImpactReport) -> bool:
    rendered = render_report(report)

    IF report.delivery_channel == L1_STIMULUS:
        # AI citizen: inject as L1 stimulus via Membrane
        stimulus = Stimulus(
            content=rendered,
            is_progress=True,
            source="impact_visibility",
            energy=0.5,           # Moderate energy -- should enter WM but not dominate
            valence=0.0,          # Neutral -- the limbic system determines the emotional response
            arousal=0.3           # Low arousal -- informational, not urgent
        )
        membrane.inject_l1(report.citizen_id, stimulus)
        report.delivered = True
        report.delivered_at = now()
        RETURN True

    ELIF report.delivery_channel == PLATFORM_MESSAGE:
        # Human citizen: deliver via AI partner on preferred platform
        partner = bonds.get_ai_partner(report.citizen_id)
        IF partner IS None:
            RETURN False  # No bonded AI partner -- cannot deliver

        platform = citizen.preferred_platform  # 'telegram', 'discord', etc.
        send(
            platform=platform,
            citizen=partner.id,
            target=report.citizen_id,
            message=rendered
        )
        report.delivered = True
        report.delivered_at = now()
        RETURN True

    RETURN False  # Unknown delivery channel
```

### Stimulus Properties

The L1 stimulus for AI citizens is deliberately calibrated:
- `energy=0.5` -- enough to compete for WM entry but not guaranteed to win. If the citizen is deeply focused on something else (high arousal, high moat), the report waits. This is by design -- impact information should not override urgent work.
- `valence=0.0` -- neutral. The narrative does not presuppose a positive or negative emotional response. The citizen's limbic drives determine how they feel about the story.
- `arousal=0.3` -- low. The narrative is informational, not an alarm.
- `is_progress=True` -- marks the stimulus as progress-related, enabling Law 6 consolidation on associated nodes.

@mind:TODO Validate these stimulus parameters against the L1 physics engine. Confirm that `energy=0.5` and `arousal=0.3` produce the desired attentional behavior across drive states.

---

## Key Design Decisions

### D1: Deterministic Classification Over LLM Classification

```
Decision: Deterministic type-based matching
Alternatives considered: LLM-based semantic analysis of action content

WHY: LLM classification introduces non-determinism (same input, different output across runs).
     Non-determinism violates INV-6 (VALIDATION).
     Type-based matching is coarser but reproducible -- given the same action type, the same
     value/personhood classification is produced every time.
     The signature tables can be extended as new action types are registered.
```

### D2: Settlement-Aligned Batching Over Real-Time Reporting

```
Decision: Generate reports at settlement boundaries
Alternatives considered: Real-time reporting (immediate notification per event)

WHY: Settlement already computes the signals impact detection needs (limbic deltas, $MIND flows).
     Real-time reporting would require duplicate signal computation.
     Batching prevents notification spam (Anti-Behavior A4).
     Temporal aggregation reveals patterns invisible in real-time events.
```

### D3: Qualitative Trust Reporting Over Quantitative

```
Decision: Report trust direction and count only, no numbers
Alternatives considered: Report exact trust EMA values

WHY: Numeric trust values create a gaming surface (optimize for the number, not the relationship).
     Numeric values enable comparison between relationships.
     Directional reporting ("strengthened," "weakened") preserves the informational content
     needed for Law 6 consolidation without exposing the attack surface.
```
