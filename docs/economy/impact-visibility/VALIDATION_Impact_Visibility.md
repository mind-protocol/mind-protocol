# VALIDATION: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Validation rules and invariants            |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | Ranked objectives and tradeoffs          |
| PATTERNS_Impact_Visibility.md           | Architectural patterns                   |
| BEHAVIORS_Impact_Visibility.md          | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Impact_Visibility.md          | Algorithms and data structures           |
| VALIDATION_Impact_Visibility.md         | This file -- validation rules            |
| IMPLEMENTATION_Impact_Visibility.md     | Implementation status and code mapping   |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

---

## Validation Rules

### INV-1: Specificity Over Generic Praise [CRITICAL]

Every narrative must reference the actual action and its downstream effect. Generic praise and structured report labels are prohibited.

```
MUST:    Reports are short narrative paragraphs -- a friend who genuinely cares telling you what happened
         Every sentence references the specific action and/or its specific downstream effect
         Warmth comes from specificity, empathy, and narration
         Voice works in both French and English
         When something worked, tell the story with care and genuine warmth

NEVER:   Generic praise without specificity: "well done," "great work," "impressive," "congratulations,"
         "keep it up," "good job," "excellent," "amazing," "bravo," "nicely done"
         Superlatives without substance ("best," "most," "greatest")
         Hollow encouragement without reference to what happened ("keep going," "you're on track")
         Structured labels: "[IMPACT REPORT]", "Action:", "Value:", "Stage:", "Cascade:", "Trust:"
         Report-style formatting with field:value pairs
         Coldness -- stripping warmth in the name of objectivity is also a violation

TEST:    Maintain a blocklist of prohibited phrases (GENERIC_PRAISE_BLOCKLIST)
         Blocklist includes generic praise phrases AND structured labels (Action:, Value:, Stage:, etc.)
         For every generated report, assert:
           no phrase in GENERIC_PRAISE_BLOCKLIST appears in the rendered text
           at least one specific action or downstream effect is referenced
         Blocklist must contain at minimum 50 prohibited phrases/patterns
         Test must run on every report before delivery
```

### INV-2: No Citizen Comparison [CRITICAL]

Impact reports must never reference other citizens' impact, metrics, or relative position.

```
MUST:    Each report contains data about exactly one citizen
         All downstream counts are anonymous ("3 downstream actions," not "3 citizens")
         No ordinal language ("first," "top," "ranked," "better than," "more than others")
         No aggregate statistics that imply ranking ("above average," "in the top N%")

NEVER:   Another citizen's name, handle, or identifier appears in the report
         Comparative language between citizens
         Percentile rankings, leaderboards, or positional indicators
         Aggregate statistics that reveal relative standing

TEST:    For every generated report:
           Extract all identifiers in the text
           Assert the only citizen identifier is the report's subject
           Assert no ordinal or comparative language is present
         Run against a corpus of 1000 synthetic reports to verify zero leakage
```

### INV-3: No Raw Limbic Exposure [CRITICAL]

Impact reports must never reveal numeric internal states of any citizen.

```
MUST:    Trust changes reported as qualitative direction only ("strengthened," "weakened")
         Link counts reported as integers (number of links, not link values)
         Emotional state never referenced, directly or indirectly
         Drive levels never referenced

NEVER:   Numeric EMA values (e.g., "trust EMA = 0.73")
         Z-scores or statistical measures
         Limbic delta values (e.g., "satisfaction increased by 0.4")
         Arousal, valence, or drive levels
         Raw energy or weight values from graph nodes
         Any floating-point number that represents an internal state

TEST:    For every generated report:
           Assert no floating-point numbers appear in trust/relationship sections
           Assert no references to "EMA," "z-score," "arousal," "valence," "limbic"
           Assert no drive names appear with numeric qualifiers
         Exception: $MIND amounts (integer or fixed-decimal) are permitted in the $MIND flow section
```

### INV-4: Settlement-Epoch Batching [HIGH]

Reports must batch within settlement epochs and never exceed one per citizen per epoch.

```
MUST:    Exactly zero or one report per citizen per settlement epoch
         Report generation occurs AFTER settlement computation completes
         Report covers the full epoch window (epoch_start to epoch_end)
         No partial-epoch reports

NEVER:   More than one report per citizen per epoch
         Reports generated mid-epoch (before settlement completes)
         Reports that span multiple epochs
         Real-time notifications that bypass the batching boundary

TEST:    Run impact_visibility over 10 epochs of synthetic data
         For each citizen, assert report_count <= 1 per epoch
         Assert every report.epoch_start == settlement.epoch_start
         Assert every report.epoch_end == settlement.epoch_end
         Inject 100 events for a single citizen in one epoch
         Assert exactly 1 report produced
```

### INV-5: Non-Citizen Exclusion [HIGH]

Non-citizens (entities without a brain or bond) must never receive impact reports.

```
MUST:    Delivery function checks citizen status before sending
         AI citizens: must have L1 brain (graph exists)
         Human citizens: must have active bond with AI partner
         Non-citizens: no report generated, no delivery attempted

NEVER:   Report generated for an entity without citizen status
         Report delivered to a platform handle without corresponding citizen record
         Report queued for a citizen whose bond has expired

TEST:    Attempt to generate reports for:
           - Valid AI citizen: report generated (PASS)
           - Valid bonded human: report generated (PASS)
           - External actor (no brain, no bond): no report (PASS)
           - Human with expired bond: no report (PASS)
           - AI citizen with no L1 graph: no report (PASS)
```

### INV-6: Deterministic Classification [HIGH]

Value and personhood classification must produce identical results given identical inputs.

```
MUST:    classify_value(action) returns the same result every time for the same action
         classify_personhood(citizen, actions) returns the same result every time for the same inputs
         Classification depends only on action.type and graph state -- no randomness, no LLM
         The VALUE_SIGNATURES and PERSONHOOD_INDICATORS tables are the sole source of truth

NEVER:   LLM invoked for classification
         Random or probabilistic elements in the classification path
         Classification result varies across runs with identical input
         Classification depends on the order of actions within an epoch

TEST:    For each action type in VALUE_SIGNATURES:
           Run classify_value 100 times
           Assert all 100 results are identical
         For each stage in PERSONHOOD_INDICATORS:
           Construct a synthetic citizen + action set that matches the stage
           Run classify_personhood 100 times
           Assert all 100 results are identical
         Shuffle action order within an epoch
         Assert classification results are order-independent
```

### INV-7: Membrane Mediation [MEDIUM]

Impact reports must cross the L1-L3 boundary via the Membrane, not via direct writes.

```
MUST:    AI citizen reports enter L1 as Stimulus objects via membrane.inject_l1()
         Human citizen reports are delivered via the send() MCP tool through the AI partner
         No direct writes to L1 graph from the impact visibility module
         Stimulus properties (energy, valence, arousal) are set by the delivery algorithm, not overridden

NEVER:   Direct graph.write() to L1 from impact visibility code
         Stimulus energy > 0.8 (reports must not dominate working memory)
         Stimulus valence != 0.0 (reports must not presuppose emotional response)
         Bypass of the Membrane's quality gate for incoming stimuli

TEST:    Trace every write path from impact visibility code
         Assert all L1 interactions go through membrane.inject_l1()
         Assert stimulus.energy <= 0.8
         Assert stimulus.valence == 0.0
         Assert stimulus.arousal <= 0.5
```

### INV-8: Cascade Self-Reference Exclusion [MEDIUM]

Cascade counts must exclude the acting citizen's own downstream references.

```
MUST:    Cascade traversal filters out nodes where node.actor == origin_actor
         Downstream count reflects only other citizens' usage
         Self-references are stripped before counting and before reporting

NEVER:   A citizen's own actions counted as downstream impact
         Self-referential loops inflate cascade depth
         A citizen can increase their cascade count by referencing their own work

TEST:    Create a scenario where citizen X creates node A, then creates nodes B and C that reference A
         Assert cascade count for A = 0 (all references are self-references)
         Have citizen Y create node D referencing A
         Assert cascade count for A = 1
```

## Invariant Summary

| ID    | Rule                          | Priority | Automated | Status      |
|-------|-------------------------------|----------|-----------|-------------|
| INV-1 | Specificity Over Generic Praise | CRITICAL | No      | @mind:TODO  |
| INV-2 | No Citizen Comparison         | CRITICAL | No        | @mind:TODO  |
| INV-3 | No Raw Limbic Exposure        | CRITICAL | No        | @mind:TODO  |
| INV-4 | Settlement-Epoch Batching     | HIGH     | No        | @mind:TODO  |
| INV-5 | Non-Citizen Exclusion         | HIGH     | No        | @mind:TODO  |
| INV-6 | Deterministic Classification  | HIGH     | No        | @mind:TODO  |
| INV-7 | Membrane Mediation            | MEDIUM   | No        | @mind:TODO  |
| INV-8 | Cascade Self-Reference Exclusion | MEDIUM | No        | @mind:TODO  |
