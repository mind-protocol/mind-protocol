# Link Type to Mechanism Mapping Analysis

**Created:** 2025-10-17
**Author:** Luca "Vellumhand"
**Purpose:** Determine mechanism requirements for 38 link types in self-observing infrastructure

---

## Executive Summary

**Question:** Do the 38 link types need 38 unique mechanisms (1-1), or do they share mechanisms (many-1)?

**Answer:** **Many-to-few relationship.** The 38 link types map to **~6-8 detection patterns** based on shared drift characteristics. These detection patterns are executed by **8 universal infrastructure mechanisms** that read type-specific metadata.

**Key Insight:** Link types don't need unique mechanism code—they need unique **detection logic metadata** that universal mechanisms execute.

---

## Methodology

For each of the 38 link types, I analyzed:
1. **What could drift?** (staleness, incoherence, broken dependencies, etc.)
2. **What detection is needed?** (time-based, verification-based, evidence-based, etc.)
3. **What task should be created?** (update docs, verify dependency, recalculate confidence, etc.)

Then grouped by shared detection patterns to identify mechanism overlap.

---

## Analysis: 38 Link Types Grouped by Detection Pattern

### Pattern 1: Staleness Detection (Time-Based Drift)
**9 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **DOCUMENTS** | Doc falls behind code | `time_since_update > staleness_threshold` | "Update documentation for [entity]" |
| **DOCUMENTED_BY** | Impl diverges from docs | `time_since_sync > staleness_threshold` | "Verify [implementation] matches [doc]" |
| **ASSIGNED_TO** | Assignment outdated | `time_since_assignment > review_threshold` | "Review assignment of [task] to [person]" |
| **MEASURES** | Metrics not updated | `time_since_measurement > freshness_requirement` | "Update metric [metric] for [project]" |
| **POSTED_BY** | Post relevance fades | `time_since_post > relevance_window` | "Reassess relevance of [post]" |
| **MENTIONED_IN** | Mention loses context | `time_since_mention > attention_window` | "Verify [entity] still active in discourse" |
| **TRANSACTED_WITH** | Transaction outdated | `time_since_transaction > relevance_period` | "Archive transaction [tx] if no longer relevant" |
| **COLLABORATES_WITH** | Collaboration inactive | `time_since_last_interaction > activity_threshold` | "Check collaboration status: [person_a] ↔ [person_b]" |
| **CONTRIBUTES_TO** | Contribution tracking stale | `time_since_contribution > tracking_window` | "Update contribution tracking: [task] → [project]" |

**Shared Mechanism:** Time-based staleness checker that compares `created_at` or last update timestamp against type-specific thresholds stored in link metadata.

---

### Pattern 2: Evidence Accumulation (Confidence Evolution)
**7 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **JUSTIFIES** | New evidence changes confidence | `new_evidence_count > recalculation_threshold` OR `contradictory_evidence_exists` | "Recalculate confidence for [claim] based on evidence" |
| **REFUTES** | Counter-evidence accumulates | `supporting_evidence_emerges` | "Reassess refutation of [claim] given new evidence" |
| **HAS_TRAIT** | Trait confidence changes | `new_justifying_posts > update_threshold` | "Update [trait] confidence for [person]" |
| **EXHIBITS_PATTERN** | Pattern confidence changes | `new_transactions > pattern_threshold` | "Recalculate [pattern] detection for [wallet]" |
| **OWNS** | Ownership confidence changes | `new_ownership_signals` OR `contradictory_signals` | "Verify ownership: [person] → [wallet]" |
| **INFLUENCES** | Influence strength changes | `engagement_metrics_change` OR `new_influence_signals` | "Update influence score: [person] → [entity]" |
| **N3_JUSTIFIES** | (Same as JUSTIFIES) | (Same) | (Same) |

**Note:** N3_REFUTES not included since not in unified schema.

**Shared Mechanism:** Evidence aggregator that:
1. Detects when new JUSTIFIES/REFUTES links are added to a claim
2. Recalculates confidence score based on evidence quality × quantity × recency
3. Creates task when confidence shift > threshold

---

### Pattern 3: Dependency Verification (Prerequisites & Requirements)
**4 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **REQUIRES** | Prerequisite not met | `required_node.status != completed` OR `temporal_order_violated` | "Verify requirement: [dependent] requires [prerequisite]" |
| **ENABLES** | Enabling condition lost | `enabling_node.status == invalid` OR `enabling_condition_false` | "Check if [enabled] still enabled by [enabler]" |
| **CREATES** | Artifact not created | `time_since_task_completion > creation_window` AND `artifact_not_exists` | "Verify [task] created [artifact] as specified" |
| **GENERATED** | Generation source invalid | `generating_node.confidence < threshold` OR `generation_process_changed` | "Verify [generated] still validly produced by [generator]" |

**Shared Mechanism:** Dependency verifier that:
1. Checks status of source and target nodes
2. Evaluates link-specific conditions (temporal order, completion status, existence checks)
3. Creates verification task when conditions not met

---

### Pattern 4: Coherence Verification (Logical Consistency)
**7 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **BLOCKS** | Blocking condition resolved | `blocking_condition_changed` OR `severity_outdated` | "Reassess: does [blocker] still block [blocked]?" |
| **SUPERSEDES** | Supersession not reflected | `old_node.status == active` AND `new_node_exists` | "Ensure [old] properly superseded by [new]" |
| **DRIVES_TOWARD** | Value-goal misalignment | `goal.status == completed` OR `value_changed` | "Verify alignment: [value] → [goal]" |
| **THREATENS** | Threat status changed | `risk.probability_changed` OR `threat_mitigated` | "Reassess threat: [risk] → [project]" |
| **DEPLOYED** | Deployment invalid | `contract.status == deprecated` OR `deployment_failed` | "Verify deployment status of [contract]" |
| **PARTICIPATED_IN** | Participation unverified | `event.participants != claimed_participants` | "Verify [person] participated in [event]" |
| **N3_COLLABORATES_WITH** | (Same as coherence check) | `collaboration_evidence_weak` | "Verify collaboration: [entity_a] ↔ [entity_b]" |

**Shared Mechanism:** Coherence checker that:
1. Evaluates link-specific logical conditions
2. Detects contradictions or state changes
3. Creates verification task when coherence violated

---

### Pattern 5: Implementation Verification (Claimed vs Actual)
**3 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **IMPLEMENTS** | Implementation diverges from spec | `spec_updated` OR `implementation_changed` OR `test_results_changed` | "Verify [implementation] still follows [best_practice]" |
| **EXTENDS** | Extension breaks compatibility | `base_changed` OR `extension_changed` OR `compatibility_test_failed` | "Check compatibility: [extension] extends [base]" |
| **INTEGRATED_WITH** | Integration broken | `integration_test_failed` OR `api_changed` | "Test integration: [system_a] ↔ [system_b]" |

**Shared Mechanism:** Implementation verifier that:
1. Detects changes to spec or implementation
2. Triggers test execution
3. Creates repair task when tests fail or divergence detected

---

### Pattern 6: Activation Verification (Entity Dynamics)
**3 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **ACTIVATES** | Activation fails | `trigger_fired` AND `target_not_activated` | "Debug: [trigger] should activate [entity] but didn't" |
| **TRIGGERED_BY** | Causation invalid | `memory_activated` AND `claimed_trigger_not_present` | "Verify: [memory] truly triggered by [stimulus]" |
| **SUPPRESSES** | Suppression fails | `suppressor_active` AND `target_still_activated` | "Debug: [suppressor] should suppress [entity] but didn't" |

**Shared Mechanism:** Activation tracker that:
1. Monitors entity activation events
2. Checks expected activation patterns against actual
3. Creates debugging task when patterns violated

---

### Pattern 7: Quality Degradation (Relationship Strength)
**5 link types need this:**

| Link Type | What Drifts | Detection Logic | Task Created |
|-----------|-------------|-----------------|--------------|
| **RELATES_TO** | Relationship relevance fades | `link_weight < relevance_threshold` OR `traversal_count_low` | "Reassess: [node_a] ↔ [node_b] still related?" |
| **LEARNED_FROM** | Pattern no longer valid | `pattern_confidence < validity_threshold` | "Verify: [pattern] still learned from [experience]?" |
| **DEEPENED_WITH** | Relationship quality changed | `relationship_quality_changed` OR `time_since_last_deepening > expectation` | "Check relationship quality: [person] via [conversation]" |
| **N3_RELATES_TO** | (Same as RELATES_TO) | (Same) | (Same) |
| (All links via decay) | Link weight decays | `traversal_count_based_decay` | (Automatic, no task created) |

**Shared Mechanism:** Quality monitor that:
1. Tracks link weights and traversal counts
2. Detects when weight falls below threshold
3. Creates reassessment task (or auto-decays based on activation)

---

### Pattern 8: Sequence Gap Detection (Implicit)
**0 link types directly, but emergent:**

| Scenario | Detection Logic | Task Created |
|----------|-----------------|--------------|
| Missing documentation steps | `(step_1 DOCUMENTS x) AND (step_3 DOCUMENTS x) AND NOT (step_2 DOCUMENTS x)` | "Document missing step 2 in [process]" |
| Incomplete dependency chain | `(a REQUIRES b) AND (b REQUIRES c) AND NOT EXISTS path(a to c)` | "Resolve dependency gap: [a] → ? → [c]" |

**Note:** This pattern isn't link-type-specific but emerges from **graph structure analysis** across any link types. Likely not a separate mechanism but a meta-pattern detected by querying graph topology.

---

## Synthesis: Mechanism Count

### Option A: Detection Pattern Count = **7 mechanisms**

If we count by detection pattern:
1. Staleness Detection (9 types)
2. Evidence Accumulation (7 types)
3. Dependency Verification (4 types)
4. Coherence Verification (7 types)
5. Implementation Verification (3 types)
6. Activation Verification (3 types)
7. Quality Degradation (5 types)

*(Sequence Gap Detection is emergent, not a dedicated mechanism)*

### Option B: Infrastructure Mechanism Count = **8 mechanisms** (as in architecture doc)

The architecture document proposed 8 mechanisms that are more infrastructure-focused:
1. **Event Propagation** - Universal (enables all detection)
2. **Link Activation Check** - Implements Pattern 6 (Activation Verification)
3. **Task Context Aggregation** - Universal (enables task creation)
4. **Hebbian Reinforcement** - Implements Pattern 7 (Quality strengthening)
5. **Energy Propagation** - Universal (prioritization)
6. **Activation-Based Decay** - Implements Pattern 7 (Quality degradation)
7. **Pattern Crystallization** - Implements Pattern 2 (Evidence Accumulation)
8. **Task Routing** - Universal (citizen assignment)

**Mapping:**
- **Universal Infrastructure (3):** Event Propagation, Task Context Aggregation, Task Routing
- **Detection Mechanisms (5):** Link Activation Check, Hebbian Reinforcement, Activation-Based Decay, Pattern Crystallization, (+ missing: Staleness, Dependency, Coherence, Implementation)

**Gap:** The 8 mechanisms in architecture doc only cover ~4 of the 7 detection patterns. Missing:
- Staleness Detection
- Dependency Verification
- Coherence Verification
- Implementation Verification

---

## Conclusion: The Answer to Nicolas's Question

**"Do mechanisms map 1-1 to link types?"**

**No.** It's a **many-to-few** relationship:
- 38 link types map to ~7 detection patterns
- Each detection pattern is executed by 1-2 universal mechanisms
- **Estimated actual mechanism count needed: ~10-12 mechanisms**
  - 3 universal infrastructure mechanisms (event propagation, task aggregation, routing)
  - 7 detection mechanisms (one per pattern)

**"Do they overlap?"**

**Yes, extensively.** Link types in the same semantic category (Documentation, Evidence, etc.) share detection patterns. For example:
- DOCUMENTS, DOCUMENTED_BY, ASSIGNED_TO, MEASURES all use **staleness detection**
- JUSTIFIES, REFUTES, HAS_TRAIT, EXHIBITS_PATTERN all use **evidence accumulation**

**Key Architectural Principle:**

Universal mechanisms read **type-specific detection logic stored as link metadata**, not hardcoded per type. Each link instance has:
```json
{
  "detection_logic": {
    "pattern": "staleness_detection",
    "staleness_threshold": "30_days",
    "freshness_requirement": "weekly"
  },
  "task_template": "Update documentation for {target_node}",
  "context_rules": ["include_last_update_timestamp", "include_recent_changes"]
}
```

This way:
- **Code is minimal and frozen** (~10-12 mechanism implementations)
- **Behavior is graph-defined** (38 link types × metadata variations)
- **System evolves by changing graph data**, not code

---

**Next Step:** Reconcile this analysis with the 8 mechanisms in SELF_OBSERVING_SUBSTRATE_ARCHITECTURE.md to determine final mechanism count and ensure all 7 detection patterns are covered.
