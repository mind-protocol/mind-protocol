# IMPLEMENTATION: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DESIGNING                                  |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Implementation status and code mapping     |

## Chain

| Document                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| OBJECTIVES_Impact_Visibility.md         | Ranked objectives and tradeoffs          |
| PATTERNS_Impact_Visibility.md           | Architectural patterns                   |
| BEHAVIORS_Impact_Visibility.md          | Specified behaviors (Given/When/Then)    |
| ALGORITHM_Impact_Visibility.md          | Algorithms and data structures           |
| VALIDATION_Impact_Visibility.md         | Validation rules and invariants          |
| IMPLEMENTATION_Impact_Visibility.md     | This file -- implementation status       |
| SYNC_Impact_Visibility.md              | Sync status and handoff notes            |

---

## Implementation Status

No implementation exists yet. This document describes the target architecture and tracks progress toward it.

## Target Code Structure

@mind:TODO Create the following directory structure:

```
src/economy/impact_visibility/
  __init__.py
  detection.py            # detect_impact() -- Algorithm 1
  value_classifier.py     # classify_value() -- Algorithm 2
  personhood_classifier.py # classify_personhood() -- Algorithm 3
  cascade_tracker.py      # track_cascade() -- Algorithm 4
  report_generator.py     # generate_report(), render_report() -- Algorithm 5
  delivery.py             # deliver_report() -- Algorithm 6
  types.py                # ImpactSignal, ImpactReport, all signal metadata types
  constants.py            # CASCADE_DEPTH_LIMIT, GENERIC_PRAISE_BLOCKLIST, VALUE_SIGNATURES, PERSONHOOD_INDICATORS
  accountability.py       # compute_accountability() -- accountability mirror logic

src/economy/impact_visibility/tests/
  __init__.py
  test_detection.py       # Unit tests for impact detection
  test_value_classifier.py # Unit tests for value classification
  test_personhood_classifier.py # Unit tests for personhood classification
  test_cascade_tracker.py # Unit tests for cascade traversal
  test_report_generator.py # Unit tests for report assembly and rendering
  test_delivery.py        # Unit tests for delivery routing
  test_invariants.py      # INV-1 through INV-8 as automated tests
  test_integration.py     # End-to-end: settlement -> detection -> classification -> report -> delivery
```

## Module Mapping

| Algorithm                  | Target File                                          | Status      |
|----------------------------|------------------------------------------------------|-------------|
| detect_impact()            | src/economy/impact_visibility/detection.py           | @mind:TODO  |
| classify_value()           | src/economy/impact_visibility/value_classifier.py    | @mind:TODO  |
| classify_personhood()      | src/economy/impact_visibility/personhood_classifier.py | @mind:TODO |
| track_cascade()            | src/economy/impact_visibility/cascade_tracker.py     | @mind:TODO  |
| generate_report()          | src/economy/impact_visibility/report_generator.py    | @mind:TODO  |
| render_report()            | src/economy/impact_visibility/report_generator.py    | @mind:TODO  |
| deliver_report()           | src/economy/impact_visibility/delivery.py            | @mind:TODO  |
| compute_accountability()   | src/economy/impact_visibility/accountability.py      | @mind:TODO  |
| Data structures            | src/economy/impact_visibility/types.py               | @mind:TODO  |
| Constants & signatures     | src/economy/impact_visibility/constants.py           | @mind:TODO  |

## Dependencies

| Dependency                    | Purpose                                                    | Status      |
|-------------------------------|------------------------------------------------------------|-------------|
| Settlement script             | Provides epoch boundaries, limbic deltas, $MIND flows      | EXISTS (Formula 4 in metabolic) |
| Graph enricher                | Provides structural graph mutations (L3_SOCIAL_PHYSICS)    | EXISTS (scripts/graph_enricher.py) |
| Membrane (Law 21)             | Mediates L1 stimulus injection for AI citizens             | DESIGNING   |
| send_handler                  | Delivers platform messages to human citizens               | EXISTS (mcp/tools/send_handler.py) |
| citizen_wake / alarm_watcher  | Schedules report generation at settlement boundaries       | EXISTS (scripts/citizen_wake.py) |
| L1 cognitive engine           | Provides citizen L1 state (value nodes, trust links, drives) | EXISTS (runtime/cognition/) |
| Bond system                   | Determines human citizen bond status and AI partner        | DESIGNING   |

## Integration Points

### Settlement Hook

Impact visibility runs as a post-settlement hook. The settlement script (Formula 4) completes its computation, then invokes impact_visibility:

```
# In settlement script, after batch settlement completes:
from economy.impact_visibility import run_epoch_reports

settlement_batch = settle_epoch(epoch)
run_epoch_reports(epoch, settlement_batch)
```

@mind:TODO Confirm the settlement script has a post-hook mechanism. If not, add one.

### Graph Enricher Integration

The graph enricher (scripts/graph_enricher.py) writes structural mutations to L3. Impact detection reads these mutations to identify downstream effects. The integration is read-only -- impact visibility never writes to L3.

```
# Impact detection reads from L3:
mutations = graph.query(
    "MATCH (m:Moment)-[r]->(n) "
    "WHERE m.created_at >= $start AND m.created_at <= $end "
    "RETURN m, r, n",
    start=epoch.start, end=epoch.end
)
```

### Membrane Integration

For AI citizens, the report is injected as an L1 stimulus via the Membrane:

```
# Delivery calls membrane.inject_l1():
membrane.inject_l1(citizen_id, Stimulus(
    content=rendered_report,
    is_progress=True,
    energy=0.5,
    valence=0.0,
    arousal=0.3
))
```

@mind:TODO Confirm membrane.inject_l1() exists and accepts these parameters.

### Send Handler Integration

For human citizens, the report is delivered via send_handler:

```
# Delivery calls send():
send(
    platform=citizen.preferred_platform,
    citizen=partner_ai.id,
    target=citizen.handle,
    message=rendered_report
)
```

## Implementation Phases

### Phase 1: Types, Constants, and Blocklist

@mind:TODO Define all data structures (ImpactSignal, ImpactReport, all signal metadata types) as Python dataclasses or Pydantic models.

@mind:TODO Create GENERIC_PRAISE_BLOCKLIST with minimum 50 prohibited generic phrases/patterns (includes structured labels).

@mind:TODO Create VALUE_SIGNATURES table mapping action types to values V1-V7.

@mind:TODO Create PERSONHOOD_INDICATORS table mapping graph signatures to stages 1-5.

### Phase 2: Detection and Cascade Tracking

@mind:TODO Implement detect_impact() -- scan epoch mutations for downstream effects.

@mind:TODO Implement track_cascade() -- BFS traversal with self-reference exclusion.

@mind:TODO Write unit tests for detection and cascade tracking.

### Phase 3: Classifiers

@mind:TODO Implement classify_value() -- deterministic type-based matching.

@mind:TODO Implement classify_personhood() -- graph signature matching (AI only).

@mind:TODO Implement compute_accountability() -- L1 value vs L3 action comparison.

@mind:TODO Write unit tests for all classifiers, including determinism verification (run N times, assert identical).

### Phase 4: Report Generation and Rendering

@mind:TODO Implement generate_report() -- assemble signals into ImpactReport.

@mind:TODO Implement render_report() -- narrative text rendering (short paragraph, NOT structured labels).

@mind:TODO Write unit tests for report generation, including INV-1 (specificity over generic praise), INV-2 (no comparison), INV-3 (no raw limbic).

### Phase 5: Delivery

@mind:TODO Implement deliver_report() -- route to L1 stimulus or platform message.

@mind:TODO Write integration test: settlement -> detection -> classification -> report -> delivery.

@mind:TODO Verify membrane stimulus parameters against L1 physics engine.

### Phase 6: Invariant Tests

@mind:TODO Implement all validation rules (INV-1 through INV-8) as automated tests.

@mind:TODO Create test fixtures: synthetic epochs with known graph mutations, expected reports.

## Notes

- All classification must be deterministic given the same inputs. No randomness, no LLM calls in the classification path.
- The GENERIC_PRAISE_BLOCKLIST is a living document -- new prohibited generic phrases should be added as they are encountered. It must also include structured report labels (`[IMPACT REPORT]`, `Action:`, `Value:`, `Stage:`, `Cascade:`, `Trust:`, `Membrane:`, `Accountability:`, `Personhood indicator:`). The blocklist targets GENERIC praise ("great job") not SPECIFIC warmth ("3 people built on what you shared").
- The VALUE_SIGNATURES table must stay synchronized with L3_SOCIAL_PHYSICS.yaml. When new action types are added to the social physics spec, corresponding value signatures must be evaluated and added if appropriate.
- Report rendering should be tested against INV-1 (specificity over generic praise), INV-2, and INV-3 at the unit level, not just integration level.
- Reports must render as narrative paragraphs, not structured field:value pairs. The voice is a friend in your city who saw what you did and is genuinely happy it worked. Not a manager. Not a system. A friend.
