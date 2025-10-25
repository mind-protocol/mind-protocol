---
title: Stimulus Diversity (Substrate Specification v1.0)
status: draft
owner: @luca (substrate), @ada (orchestration)
last_updated: 2025-10-25
depends_on:
  - stimulus_injection.md
  - subentity_layer.md
  - ../ops_and_viz/observability_events.md
summary: >
  Substrate architecture for diverse stimulus types (L1 raw signals + L2 derived intents),
  attribution model (WM/entity → routing), and evidence linking. Enables consciousness
  to respond to development activity, runtime errors, self-observation, and derived patterns.
---

# Stimulus Diversity — Substrate Specification

## 1. Context — What problem are we solving?

Current stimulus sources are limited to user messages. To enable autonomous self-improvement and context-aware consciousness, we need:

- **Diverse signal sources** (commits, file changes, errors, self-observation)
- **Meaningful aggregation** (L1 raw → L2 derived intents)
- **Smart attribution** (which entities should respond?)
- **Evidence linking** (why did this stimulus occur?)

**Critical principle:** Consciousness shouldn't live in a vacuum. Development activity, runtime state, and self-observation should shape activation patterns.

---

## 2. Substrate Architecture

### 2.1 Two-Level Stimulus Model

**Level 1 (Raw Signals)** — Direct observations from external or internal sources:
- User conversations (existing)
- Browser console errors (existing)
- Screenshots (existing, evidence only)
- Git commits (new)
- File system changes (new)
- Backend runtime errors (new)
- Self-observation events (health, learning, tier transitions, mismatches)

**Level 2 (Derived Intents)** — Meaningful patterns extracted from L1 + internal state:
- Intents (stabilize_narrative, reconcile_beliefs, consolidate_learning, promote_pattern, protect_fix)
- Incidents (backend_error storms, schema regressions, etc.)

**Key insight:** L1 provides observability. L2 provides **agency** — the system deciding "this pattern means I should X."

---

## 3. L1 Stimulus Types (Raw Signals)

### 3.1 Universal L1 Schema

All L1 stimuli share base structure:

```typescript
interface L1Stimulus {
  // Identity
  level: "L1"
  type: L1StimulusType  // See registry below
  stimulus_id: string   // Unique identifier

  // Temporal
  timestamp_ms: number
  citizen_id: string    // Which consciousness graph

  // Content
  content: string       // Human-readable description
  metadata: Record<string, any>  // Type-specific fields

  // Routing hints (optional at L1, required at L2)
  severity?: "info" | "warn" | "error" | "critical"
  component?: string    // Which system component

  // Evidence
  correlation_id?: string  // Link related stimuli
  evidence_refs?: string[] // Links to supporting artifacts
}
```

### 3.2 L1 Type Registry

**conversation** (existing)
```typescript
metadata: {
  message_content: string
  turn_number: number
  conversation_id: string
}
```

**console_error** (existing)
```typescript
metadata: {
  error_message: string
  stack_trace?: string
  source_file?: string
  line_number?: number
  user_agent: string
}
severity: "error" | "critical"
component: "frontend"
```

**screenshot** (existing, evidence only)
```typescript
metadata: {
  screenshot_path: string
  ocr_text?: string        // Optional if OCR enabled
  capture_context?: string // What was happening
}
severity: "info"
```

**commit** (new)
```typescript
metadata: {
  repo: string             // "mind-protocol"
  commit_sha: string
  author: string
  message: string
  files_changed: string[]
  diffstat: {additions: number, deletions: number}
  tags: string[]           // Extracted: "fix:", "feat:", "schema", etc.
}
severity: "info"
component: "git"
```

**file_change** (new)
```typescript
metadata: {
  path: string
  change_type: "create" | "modify" | "delete"
  package: string          // e.g., "orchestration", "app/consciousness"
  size_delta?: number
}
severity: "info"
component: "filesystem"
```

**backend_error** (new)
```typescript
metadata: {
  error_type: string       // Exception class name
  error_message: string
  stack_trace: string
  stack_fingerprint: string  // For deduplication
  service: string          // "engine_v2", "websocket_server", etc.
  count: number            // If aggregated
}
severity: "error" | "critical"
component: string  // Service name
```

**self_observation** (new - wraps existing telemetry events)
```typescript
metadata: {
  event_kind: string       // "health.phenomenological", "weights.updated", etc.
  event_payload: Record<string, any>
  observation_type: "health" | "learning" | "tier" | "mismatch"
}
severity: "info" | "warn"
component: "consciousness_engine"
```

---

## 4. L2 Stimulus Types (Derived Intents)

### 4.1 Universal L2 Schema

All L2 stimuli share base structure:

```typescript
interface L2Stimulus {
  // Identity
  level: "L2"
  type: L2StimulusType    // See registry below
  stimulus_id: string

  // Temporal
  timestamp_ms: number
  citizen_id: string

  // Derivation
  explanation: string     // Why this L2 was created
  evidence: string[]      // L1 stimulus_ids that triggered this
  confidence: number      // 0-1, how certain is this derivation?

  // Attribution (REQUIRED at L2)
  attribution: Attribution  // See §5

  // Routing (REQUIRED at L2)
  routing: Routing          // See §6

  // Correlation
  correlation_id: string
}
```

### 4.2 L2 Type Registry

**intent.stabilize_narrative**
```typescript
// Triggered by: sustained health fragmentation
derivation_logic: "health.phenomenological.state == 'fragmented' for ≥N windows"
attribution: {
  primary_entities: ["sentinel", "planner"]
  confidence: 0.8-0.95
}
routing: {
  mode: "amplify"
  budget_hint: 3.0  // Higher than baseline
}
```

**intent.reconcile_beliefs**
```typescript
// Triggered by: mismatch + schema changes + ANN guard
derivation_logic: "phenomenology.mismatch AND commit.tags includes 'schema' AND recent file_change in schema files"
attribution: {
  primary_entities: ["architect", "validator"]
  confidence: 0.7-0.9
}
routing: {
  mode: "top_up"  // Targeted to specific entities
  budget_hint: 2.5
}
metadata: {
  schema_area: string  // Which schema changed
}
```

**intent.consolidate_learning**
```typescript
// Triggered by: learning spike
derivation_logic: "weights.updated volume per minute > threshold"
attribution: {
  primary_entities: ["memory", "integrator"]
  confidence: 0.75-0.9
}
routing: {
  mode: "amplify"
  budget_hint: 2.0
}
```

**intent.promote_pattern**
```typescript
// Triggered by: link strengthening surge on same triad
derivation_logic: "tier.link.strengthened for co_activation, same node triad, above baseline"
attribution: {
  primary_entities: ["pattern_former"]
  confidence: 0.7-0.85
}
routing: {
  mode: "amplify"
  budget_hint: 1.5
}
metadata: {
  pattern_nodes: string[]  // The triad
}
```

**intent.protect_fix**
```typescript
// Triggered by: commit + matching file changes + error reduction
derivation_logic: "commit.tags includes {schema|guardian|emitter} AND file_change in matching area AND backend_error count drops"
attribution: {
  primary_entities: ["builder", "sentinel"]
  confidence: 0.8-0.95
}
routing: {
  mode: "top_up"
  budget_hint: 2.0
}
metadata: {
  protected_commit: string  // SHA
  protected_files: string[]
}
```

**incident.backend_error**
```typescript
// Triggered by: error storm
derivation_logic: "≥X identical backend_error in Y minutes"
attribution: {
  primary_entities: ["ops", "investigator"]
  confidence: 0.9-1.0
}
routing: {
  mode: "top_up"
  budget_hint: 4.0  // High priority
  alert: true       // Should trigger operator notification
}
metadata: {
  error_fingerprint: string
  error_count: number
  time_window_minutes: number
}
```

---

## 5. Attribution Model

**Purpose:** Determine which entities should respond to this stimulus.

### 5.1 Attribution Schema

```typescript
interface Attribution {
  // Primary entities (highest relevance)
  primary_entities: string[]     // Entity names, e.g., ["architect", "validator"]
  primary_confidence: number     // 0-1, how certain about primaries

  // Secondary entities (supporting role)
  secondary_entities?: string[]
  secondary_confidence?: number

  // Derivation method
  attribution_method: AttributionMethod

  // Context snapshot
  wm_snapshot_id?: string        // Which WM state was used
  active_entities_at_time?: string[]
}

type AttributionMethod =
  | "wm_current"           // Use current WM top entities
  | "entity_affinity"      // Semantic match to entity embeddings
  | "rule_based"           // Explicit rule (e.g., "schema changes → architect")
  | "hybrid"               // Combination
```

### 5.2 Attribution Algorithms

**For L1 stimuli** (optional attribution):
- **conversation**: Current WM top entities
- **console_error**: Frontend-relevant entities (if defined)
- **commit**: Tag-based rules (schema → architect, guardian → ops, etc.)
- **file_change**: Package-based rules (consciousness → architect, api → integrator, etc.)
- **backend_error**: Service → entity mapping
- **self_observation**: Event type → entity (health → sentinel, learning → memory, etc.)

**For L2 stimuli** (required attribution):
- Use derivation logic to determine primary entities
- Confidence based on evidence strength and pattern clarity
- Secondary entities from recent WM co-activation

### 5.3 Attribution Confidence Levels

- **0.9-1.0**: Explicit rule match (error storm → ops)
- **0.75-0.9**: Strong pattern (mismatch + schema commit → architect/validator)
- **0.6-0.75**: WM-based inference (current WM entities)
- **<0.6**: Low confidence, use broader Amplify routing

---

## 6. Routing Model

**Purpose:** Determine how injection budget is distributed based on attribution.

### 6.1 Routing Schema

```typescript
interface Routing {
  // Mode selection
  mode: "top_up" | "amplify" | "hybrid"

  // Budget scaling
  budget_hint: number          // Multiplier on base budget (0.5 - 5.0)

  // Target entities (from attribution)
  target_entities: string[]

  // Routing parameters (connect to injection v2.1)
  lambda_override?: number     // Override adaptive λ if needed

  // Alerts
  alert?: boolean              // Should this trigger operator notification?
  alert_severity?: "info" | "warn" | "error" | "critical"
}
```

### 6.2 Routing Modes

**top_up** (narrow targeting):
- Uses floor channel primarily (λ → 0.7-0.8)
- Targets attributed entities' member nodes
- Good for: specific intents (reconcile_beliefs, protect_fix), incidents

**amplify** (broader coalition):
- Uses amplifier channel primarily (λ → 0.3-0.4)
- Targets attributed entities + recent WM coalition
- Good for: emergent intents (stabilize_narrative, promote_pattern)

**hybrid** (balanced):
- Default adaptive λ (0.6 baseline)
- Targets attributed entities with moderate spread
- Good for: uncertain attribution, self-observation stimuli

### 6.3 Budget Hints

Budget scaling based on stimulus importance:

- **4.0-5.0**: Critical incidents (error storms, schema regressions)
- **2.5-4.0**: High-priority intents (stabilize_narrative, reconcile_beliefs)
- **1.5-2.5**: Medium intents (consolidate_learning, protect_fix)
- **1.0-1.5**: Routine stimuli (file changes, commits)
- **0.5-1.0**: Low-priority observations (info-level self-observation)

Final budget: `B_final = B_base * f(ρ) * g(source) * budget_hint`

---

## 7. Evidence Linking

**Purpose:** Connect stimuli to supporting artifacts and related events.

### 7.1 Evidence Schema

```typescript
interface Evidence {
  // Correlation
  correlation_id: string       // Groups related stimuli

  // References
  evidence_refs: EvidenceRef[]
}

interface EvidenceRef {
  type: "stimulus" | "artifact" | "event"
  id: string
  description?: string
  url?: string                 // Link to artifact (commit, screenshot, log)
}
```

### 7.2 Evidence Types

**stimulus** - References to other L1/L2 stimuli:
```typescript
{
  type: "stimulus",
  id: "stim-L1-console-error-abc123",
  description: "Original console error that triggered investigation"
}
```

**artifact** - External artifacts:
```typescript
{
  type: "artifact",
  id: "commit-sha-def456",
  description: "Fix commit for schema validation",
  url: "https://github.com/.../commit/def456"
}
```

**event** - Internal consciousness events:
```typescript
{
  type: "event",
  id: "evt-phen-health#123",
  description: "Health fragmentation observation"
}
```

### 7.3 Correlation Strategy

**correlation_id format:** `{level}-{date}-{sequence}`
- Example L1: `L1-2025-10-25-001`
- Example L2: `L2-2025-10-25-015`

**Auto-correlation rules:**
- L2 inherits correlation_id from strongest L1 evidence
- Co-occurring errors within time window share correlation_id
- Commit + related file_changes share correlation_id

---

## 8. Persistence Requirements

### 8.1 Stimulus Storage

**Graph structure:**
```cypher
(:Stimulus {
  level: "L1" | "L2",
  type: string,
  stimulus_id: string,
  timestamp_ms: number,
  citizen_id: string,
  content: string,
  metadata: JSON,
  correlation_id: string
})
```

**L2 extensions:**
```cypher
(:L2Stimulus:Stimulus {
  explanation: string,
  confidence: number,
  attribution: JSON,
  routing: JSON
})
```

**Evidence links:**
```cypher
(:L2Stimulus)-[:DERIVED_FROM {weight: float}]->(:L1Stimulus)
(:Stimulus)-[:EVIDENCE_REF {ref_type: string}]->(:Artifact)
```

### 8.2 Attribution Persistence

```cypher
(:Stimulus)-[:ATTRIBUTED_TO {
  role: "primary" | "secondary",
  confidence: float,
  method: string
}]->(:Subentity)
```

### 8.3 Injection Results Tracking

```cypher
(:Stimulus)-[:INJECTED_TO {
  frame_id: number,
  budget_allocated: float,
  nodes_activated: number,
  flips_caused: number,
  timestamp_ms: number
}]->(:InjectionResult)
```

---

## 9. Integration with Stimulus Injection v2.1

### 9.1 Handoff to Injector

L1/L2 stimuli convert to existing `StimulusEnvelope` format:

```python
def to_stimulus_envelope(stim: L1Stimulus | L2Stimulus) -> StimulusEnvelope:
    """Convert L1/L2 stimulus to injection format."""

    # Base stimulus
    env = StimulusEnvelope(
        source=stim.type,
        content=stim.content,
        timestamp_ms=stim.timestamp_ms,
        citizen_id=stim.citizen_id
    )

    # L2-specific routing
    if stim.level == "L2":
        env.routing_hint = stim.routing
        env.attribution = stim.attribution
        env.budget_multiplier = stim.routing.budget_hint

    return env
```

### 9.2 Attribution → Candidate Selection

Injector uses attribution to bias candidate retrieval:

```python
def select_candidates(
    stimulus: StimulusEnvelope,
    attribution: Attribution
) -> List[Candidate]:
    """Bias retrieval toward attributed entities."""

    # If attributed, retrieve from entity members preferentially
    if attribution and attribution.primary_confidence > 0.7:
        candidates = retrieve_entity_members(
            entities=attribution.primary_entities,
            similarity_threshold=0.6
        )
    else:
        # Fallback to standard semantic search
        candidates = retrieve_by_embedding(stimulus.content)

    return candidates
```

### 9.3 Routing → Lambda Override

```python
def compute_lambda(
    routing: Routing,
    coldness: float,
    concentration: float
) -> float:
    """Compute adaptive λ with routing mode influence."""

    # Start with adaptive baseline
    lam = adaptive_lambda(coldness, concentration)

    # Override based on routing mode
    if routing.mode == "top_up":
        lam = max(lam, 0.7)  # Favor floor channel
    elif routing.mode == "amplify":
        lam = min(lam, 0.4)  # Favor amplifier channel

    return clamp(lam, 0.3, 0.8)
```

---

## 10. What Success Looks Like

**Substrate validation:**
- ✅ All L1 types have complete schemas with required metadata
- ✅ All L2 types have derivation logic, attribution, and routing defined
- ✅ Attribution model connects to existing WM/entity membership
- ✅ Routing model integrates cleanly with injection v2.1 dual-channel policy
- ✅ Evidence linking enables traceability from L2 → L1 → artifacts

**Implementation readiness:**
- Felix/Atlas can implement watchers/deriver using these schemas
- Ada can design orchestration knowing the substrate structure
- Iris can build UI consuming these standardized formats
- No ambiguity about what fields are required vs optional

---

## 11. Implementation Decisions (Nicolas 2025-10-25)

### 11.1 Threshold Strategy

**Phase 1 (Conservative Seeds):**
Start with safe, conservative threshold values to enable fast shipping:

- **Fragmentation:** `intent.stabilize_narrative` when **≥5 fragmented frames in 60s AND mean fragmentation_score ≥ 0.60**
- **Error Storm:** `incident.backend_error` when **≥10 identical errors in 2min** per stack-fingerprint
- **Learning Spike:** `intent.consolidate_learning` when `weights.updated` **≥100 in 5min OR above Q95 of last 24h**
- **Belief Mismatch:** `intent.reconcile_beliefs` when commit touches schemas **AND ≥3 related backend errors in 10min**

**Phase 2 (Learned Percentiles):**
Replace seed values with per-citizen percentile-based gates:
- Compute rolling **Q85-Q95** thresholds per citizen (7-day window)
- Update daily via `threshold_tuner` job
- Keep seeds as safety floors only
- Aligns with "no arbitrary constants" principle

**Rationale:** Start high (conservative), tune down via percentiles once metrics populate. Prevents premature optimization while enabling data-driven improvement.

### 11.2 Screenshot OCR

**Decision:** Phase 2

Ship MVP without OCR. Add OCR as optional enrichment later (`ocr_text` field in L1 screenshot metadata) once ingestion & derivation basics are stable.

### 11.3 Alert Routing

**Decision:** Dashboard always, Slack/email only for critical with safety gates

**Policy:**
- All incidents appear in dashboard by default
- Slack/email **only** when `severity=critical`
- Enforce safety gates:
  - **Cooldowns** per channel (prevent spam)
  - **Capacity limits** per assignee (`max_in_flight`)
  - **Sensitivity metadata** (never route `restricted` to N3)
  - **Circuit breakers** for alert storms

**Rationale:** Prevents alert fatigue and Slack spam while ensuring critical incidents reach operators.

### 11.4 Cross-Citizen Correlation

**Decision:** Phase 2

Keep Phase 1 intra-citizen (stimuli stay within citizen graph). Enable correlation across citizens (e.g., Ada observes → Luca receives mission) in Phase 2. Substrate already anticipates this via `correlation_id` and citizen-scoped evidence refs.

### 11.5 L2 Persistence

**Decision:** Store ALL L2 stimuli with TTL

Persist every L2 stimulus + evidence links + injection results (`nodes_activated`, `flips_caused`) to enable:
- False positive measurement
- Threshold tuning via success rate
- Governance & traceability

Apply TTL/archival after 30-60d if storage becomes concern.

### 11.6 Targeted Improvements (Integrated)

**Metrics Endpoint (Priority 1):**
Implement `/consciousness/:citizen/metrics/stimuli` immediately to enable tuning + demos. Expose:
- L1/L2 rates per minute (by type)
- Dropped/decimated counts
- Attribution hit rate
- Injection success rate

**Threshold Tuner (Daily Job):**
Compute per-citizen Q85/Q95 baselines from 7-day window, output to config. See separate spec.

**Alert Safety:**
Enforce cooldowns, capacity-aware assignment, sensitivity metadata, circuit-breakers.

**Full Traceability:**
Persist `L1↔L2 evidence` and `L2→InjectionResult` edges for "what derived this?" and "did it work?" queries.

**Autonomy Boundary:**
Autonomy service generates IntentCards at L2, dispatches missions through existing injection path. Keep boundary crisp.

### 11.7 Future Extensions (Phase 2+)

- Learned derivation rules (pattern mining on L1 sequences)
- Adaptive thresholds based on citizen-specific traffic percentiles
- Cross-citizen correlation and collective intelligence
- Temporal patterns (commit → 2min → error → 5min → fix sequences)
- Screenshot OCR enrichment
- Advanced attribution (learned entity affinity models)

---

## 12. Substrate Completeness Checklist

- [x] L1 stimulus types defined (7 types)
- [x] L2 stimulus types defined (6 types)
- [x] Universal schemas (L1 base, L2 base)
- [x] Type-specific metadata requirements
- [x] Attribution model (schema + algorithms + confidence levels)
- [x] Routing model (modes + budget hints + lambda integration)
- [x] Evidence linking (correlation + references)
- [x] Persistence schemas (graph structure)
- [x] Integration with stimulus_injection.md v2.1
- [x] Success criteria defined

**Substrate specification: COMPLETE**

**Next step:** Handoff to Ada for orchestration design (watchers, deriver service, phases, rollout).
