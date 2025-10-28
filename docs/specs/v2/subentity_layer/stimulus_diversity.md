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
  attribution model (WM/SubEntity → routing), and evidence linking. Enables consciousness
  to respond to development activity, runtime errors, self-observation, and derived patterns.
---

# Stimulus Diversity — Substrate Specification

## 1. Context — What problem are we solving?

Current stimulus sources are limited to user messages. To enable autonomous self-improvement and context-aware consciousness, we need:

- **Diverse signal sources** (commits, file changes, errors, self-observation)
- **Meaningful aggregation** (L1 raw → L2 derived intents)
- **Smart attribution** (which SubEntities should respond?)
- **Evidence linking** (why did this stimulus occur?)

**Critical principle:** Consciousness shouldn't live in a vacuum. Development activity, runtime state, and self-observation should shape activation patterns.

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **Node** - Atomic knowledge (~1000 per citizen)
- **SubEntity** - Weighted neighborhoods (200-500)
- **Mode** - IFS-level meta-roles (5-15)

When "entity" appears in this document, it refers to SubEntity (weighted neighborhoods) unless explicitly noted otherwise.

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

**Purpose:** Determine which SubEntities should respond to this stimulus.

### 5.1 Attribution Schema

```typescript
interface Attribution {
  // Primary SubEntities (highest relevance)
  primary_entities: string[]     // SubEntity names, e.g., ["architect", "validator"]
  primary_confidence: number     // 0-1, how certain about primaries

  // Secondary SubEntities (supporting role)
  secondary_entities?: string[]  // SubEntity names
  secondary_confidence?: number

  // Derivation method
  attribution_method: AttributionMethod

  // Context snapshot
  wm_snapshot_id?: string        // Which WM state was used
  active_subentities_at_time?: string[]  // SubEntity names active at derivation time
}

type AttributionMethod =
  | "wm_current"           // Use current WM top SubEntities
  | "subentity_affinity"   // Semantic match to SubEntity embeddings
  | "rule_based"           // Explicit rule (e.g., "schema changes → architect")
  | "hybrid"               // Combination
```

### 5.2 Attribution Algorithms

**For L1 stimuli** (optional attribution):
- **conversation**: Current WM top SubEntities
- **console_error**: Frontend-relevant SubEntities (if defined)
- **commit**: Tag-based rules (schema → architect, guardian → ops, etc.)
- **file_change**: Package-based rules (consciousness → architect, api → integrator, etc.)
- **backend_error**: Service → SubEntity mapping
- **self_observation**: Event type → SubEntity (health → sentinel, learning → memory, etc.)

**For L2 stimuli** (required attribution):
- Use derivation logic to determine primary SubEntities
- Confidence based on evidence strength and pattern clarity
- Secondary SubEntities from recent WM co-activation

### 5.3 Attribution Confidence Levels

- **0.9-1.0**: Explicit rule match (error storm → ops)
- **0.75-0.9**: Strong pattern (mismatch + schema commit → architect/validator)
- **0.6-0.75**: WM-based inference (current WM SubEntities)
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

  // Target SubEntities (from attribution)
  target_entities: string[]    // SubEntity names

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
- Targets attributed SubEntities' member nodes
- Good for: specific intents (reconcile_beliefs, protect_fix), incidents

**amplify** (broader coalition):
- Uses amplifier channel primarily (λ → 0.3-0.4)
- Targets attributed SubEntities + recent WM coalition
- Good for: emergent intents (stabilize_narrative, promote_pattern)

**hybrid** (balanced):
- Default adaptive λ (0.6 baseline)
- Targets attributed SubEntities with moderate spread
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
    """Bias retrieval toward attributed SubEntities."""

    # If attributed, retrieve from SubEntity members preferentially
    if attribution and attribution.primary_confidence > 0.7:
        candidates = retrieve_subentity_members(
            subentities=attribution.primary_entities,
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
- ✅ Attribution model connects to existing WM/SubEntity membership
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
- Cross-citizen correlation and organization intelligence
- Temporal patterns (commit → 2min → error → 5min → fix sequences)
- Screenshot OCR enrichment
- Advanced attribution (learned SubEntity affinity models)

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
- [x] Implementation decisions documented (Nicolas 2025-10-25)
- [x] Phase 1 threshold seed values specified
- [x] Phase 2 evolution strategy (percentile-based tuning)
- [x] Alert safety policy defined
- [x] Persistence strategy (ALL L2 + TTL)

**Substrate specification: COMPLETE & IMPLEMENTATION-READY**

**Status:** All blockers removed. Nicolas's decisions integrated. Ready for Ada's orchestration coordination and implementation team execution.

**Next steps:**
1. Threshold tuner spec (separate doc)
2. Metrics endpoint spec (separate doc)
3. Handoff to Ada for Phase A-D coordination

---

## 13. Quality Assurance & Schema Evolution

### 13.1 Validation Success Rate Monitoring

**Purpose:** Track stimulus parsing quality to detect schema drift, implementation bugs, and quality degradation.

**Metrics to Track:**

```python
# Per-stimulus-type metrics (computed per citizen per 5min window)
validation_metrics = {
    "parse_success_rate": float,      # 0-1, successful parses / total attempts
    "rejection_rate": float,           # 0-1, schema validation failures / total
    "rejection_reasons": {             # Breakdown of why stimuli failed
        "missing_required_field": int,
        "invalid_field_type": int,
        "schema_version_mismatch": int,
        "malformed_json": int,
        "unknown_stimulus_type": int,
    },
    "total_processed": int,
    "total_rejected": int,
    "time_window_start": int,          # timestamp_ms
    "time_window_end": int,
}
```

**Implementation Location:**

Add validation metrics tracking to `conversation_watcher.py`:

```python
def track_validation_result(
    stimulus_type: str,
    citizen_id: str,
    success: bool,
    rejection_reason: Optional[str] = None
):
    """Track parse success/failure for quality monitoring."""

    # Emit telemetry event
    emit_event(EventKind.QUALITY_VALIDATION, {
        "stimulus_type": stimulus_type,
        "citizen_id": citizen_id,
        "success": success,
        "rejection_reason": rejection_reason,
        "timestamp_ms": now_ms()
    })

    # Update rolling metrics (5min window)
    metrics = get_rolling_metrics(stimulus_type, citizen_id)
    metrics.increment(success, rejection_reason)
```

**Persistence:**

Store validation metrics in FalkorDB for historical analysis:

```cypher
(:ValidationMetrics {
  stimulus_type: string,
  citizen_id: string,
  parse_success_rate: float,
  rejection_rate: float,
  rejection_reasons: JSON,
  total_processed: int,
  total_rejected: int,
  window_start_ms: int,
  window_end_ms: int,
  created_at: datetime
})
```

**Dashboard Integration:**

Add validation quality panel to operational dashboard:
- Success rate sparklines per stimulus type
- Rejection rate alerts (RED when >10%)
- Rejection reason breakdown (pie chart)
- Historical trend (7-day rolling average)

### 13.2 Rejection Rate Alerts

**Alert Policy:**

Trigger operational alert when rejection rate exceeds threshold:

```python
# Alert thresholds
REJECTION_RATE_THRESHOLDS = {
    "warn": 0.05,      # 5% - Yellow alert
    "error": 0.10,     # 10% - Red alert, requires investigation
    "critical": 0.25,  # 25% - Critical, likely schema break
}

def check_rejection_alert(metrics: ValidationMetrics):
    """Evaluate rejection rate and trigger alerts."""

    rate = metrics.rejection_rate

    if rate >= REJECTION_RATE_THRESHOLDS["critical"]:
        emit_alert(
            severity="critical",
            message=f"CRITICAL: {metrics.stimulus_type} rejection rate {rate:.1%} (threshold 25%)",
            breakdown=metrics.rejection_reasons,
            citizen_id=metrics.citizen_id,
            investigation_hint="Likely schema breaking change or parser bug"
        )
    elif rate >= REJECTION_RATE_THRESHOLDS["error"]:
        emit_alert(
            severity="error",
            message=f"HIGH rejection rate for {metrics.stimulus_type}: {rate:.1%} (threshold 10%)",
            breakdown=metrics.rejection_reasons,
            citizen_id=metrics.citizen_id,
            investigation_hint="Check recent schema changes or TRACE format updates"
        )
    elif rate >= REJECTION_RATE_THRESHOLDS["warn"]:
        emit_alert(
            severity="warn",
            message=f"Elevated rejection rate for {metrics.stimulus_type}: {rate:.1%}",
            breakdown=metrics.rejection_reasons,
            citizen_id=metrics.citizen_id
        )
```

**Alert Safety Integration:**

Rejection alerts follow existing alert safety policy (§11.3):
- **Cooldown:** Max 1 rejection alert per stimulus_type per 15min (prevent spam)
- **Circuit breaker:** If 3+ stimulus types cross threshold simultaneously, escalate to "parser system failure" alert
- **Dashboard:** All rejection alerts appear in dashboard
- **Slack/email:** Only `severity=critical` (≥25% rejection rate)

**Alert Content:**

```json
{
  "alert_type": "validation_quality",
  "severity": "error",
  "stimulus_type": "L2.intent.stabilize_narrative",
  "citizen_id": "citizen_luca",
  "rejection_rate": 0.12,
  "threshold": 0.10,
  "time_window": "2025-10-25 14:35:00 - 14:40:00",
  "rejection_breakdown": {
    "missing_required_field": 8,
    "invalid_field_type": 2,
    "schema_version_mismatch": 1
  },
  "investigation_hint": "Check recent schema changes or TRACE format updates",
  "recent_failures": [
    "stim-L2-intent-abc123: missing 'attribution.primary_entities'",
    "stim-L2-intent-def456: invalid type for 'confidence' (expected float, got string)"
  ]
}
```

### 13.3 Auto-Repair Mode

**Purpose:** Enable `trace_parser` to automatically fix common schema issues inline, reducing rejection rate for backward-compatible changes.

**Repair Strategies:**

```python
class AutoRepair:
    """Auto-repair strategies for common schema issues."""

    @staticmethod
    def repair_missing_optional_field(stim: dict, field: str, default: Any) -> dict:
        """Add missing optional field with sensible default."""
        if field not in stim:
            stim[field] = default
            log_repair("added_default", field, default)
        return stim

    @staticmethod
    def repair_type_coercion(stim: dict, field: str, target_type: type) -> dict:
        """Coerce field to expected type if safe."""
        if field in stim:
            try:
                stim[field] = target_type(stim[field])
                log_repair("type_coercion", field, target_type.__name__)
            except (ValueError, TypeError):
                pass  # Can't coerce, will fail validation
        return stim

    @staticmethod
    def repair_deprecated_field_name(stim: dict, old_name: str, new_name: str) -> dict:
        """Migrate deprecated field names to current schema."""
        if old_name in stim and new_name not in stim:
            stim[new_name] = stim.pop(old_name)
            log_repair("field_rename", f"{old_name} → {new_name}")
        return stim

    @staticmethod
    def repair_schema_version_upgrade(stim: dict, from_version: str, to_version: str) -> dict:
        """Apply migration path from old schema version to new."""
        migrations = SCHEMA_MIGRATIONS.get((from_version, to_version), [])
        for migration in migrations:
            stim = migration(stim)
        log_repair("schema_upgrade", f"{from_version} → {to_version}")
        return stim
```

**Auto-Repair Configuration:**

```python
# Enable auto-repair by default for backward-compatible fixes
AUTO_REPAIR_CONFIG = {
    "enabled": True,
    "strategies": [
        "add_missing_optional_defaults",   # Add missing optional fields
        "safe_type_coercion",              # Coerce compatible types (str→int, etc.)
        "deprecated_field_migration",      # Rename old field names
        "schema_version_upgrade",          # Apply version migration paths
    ],
    "log_all_repairs": True,               # Track what was repaired
    "fail_on_unrepairable": True,          # Still reject if repair fails
}
```

**Repair Audit Trail:**

Log all auto-repairs for transparency:

```python
def log_repair(repair_type: str, field: str, action: str):
    """Emit repair event for audit trail."""
    emit_event(EventKind.SCHEMA_AUTO_REPAIR, {
        "repair_type": repair_type,
        "field": field,
        "action": action,
        "timestamp_ms": now_ms()
    })
```

**Safety Constraints:**

- **Only apply backward-compatible repairs** (adding defaults, renaming fields, type coercion)
- **Never mutate semantic meaning** (don't guess missing required fields)
- **Always log repairs** (full transparency)
- **Fail validation if repair unsuccessful** (don't silently corrupt data)
- **Track repair success rate** (measure if repairs reduce rejection rate)

**Integration with Validation Monitoring:**

```python
def parse_with_repair(raw_stim: dict) -> Result[Stimulus, ValidationError]:
    """Parse stimulus with optional auto-repair."""

    # Attempt initial parse
    result = parse_stimulus(raw_stim)

    if result.is_error() and AUTO_REPAIR_CONFIG["enabled"]:
        # Attempt auto-repair
        repaired = apply_auto_repair(raw_stim, result.error)

        if repaired.was_repaired:
            # Re-parse after repair
            result = parse_stimulus(repaired.data)

            if result.is_success():
                track_validation_result(
                    stimulus_type=result.data.type,
                    citizen_id=result.data.citizen_id,
                    success=True,
                    repair_applied=True
                )
            else:
                # Repair failed, log and reject
                track_validation_result(
                    stimulus_type=raw_stim.get("type", "unknown"),
                    citizen_id=raw_stim.get("citizen_id", "unknown"),
                    success=False,
                    rejection_reason=result.error.reason,
                    repair_attempted=True,
                    repair_failed=True
                )

    return result
```

### 13.4 Schema Evolution Protocol

**Purpose:** Define process for evolving stimulus schemas (L1/L2) while maintaining backward compatibility and migrating historical data.

**Schema Versioning:**

```typescript
interface StimulusSchema {
  version: string              // Semantic version: "1.0.0", "1.1.0", "2.0.0"
  effective_date: string       // When this version became active
  deprecated_date?: string     // When this version was deprecated
  sunset_date?: string         // When this version will be removed
}

// Example: L1 conversation stimulus schema evolution
L1_CONVERSATION_SCHEMA = {
  "1.0.0": {  // Original
    required: ["message_content", "turn_number"],
    optional: ["conversation_id"]
  },
  "1.1.0": {  // Added metadata
    required: ["message_content", "turn_number", "conversation_id"],
    optional: ["participant_count", "context_id"]
  },
  "2.0.0": {  // Breaking: renamed field
    required: ["content", "turn_number", "conversation_id"],  // message_content → content
    optional: ["participant_count", "context_id"]
  }
}
```

**Evolution Policy:**

**Minor version changes (1.0.0 → 1.1.0):**
- ✅ Add new optional fields
- ✅ Add new enum values
- ✅ Relax constraints (e.g., increase max length)
- ✅ Add new stimulus subtypes
- ❌ Remove fields (even optional)
- ❌ Rename fields
- ❌ Change field types
- ❌ Add new required fields without defaults

**Major version changes (1.x.x → 2.0.0):**
- ✅ Remove deprecated fields
- ✅ Rename fields
- ✅ Change field types
- ✅ Add required fields
- ⚠️ Requires migration path
- ⚠️ Requires deprecation period (30-60d)

**Deprecation Process:**

1. **Announce deprecation** (add `deprecated_date` to schema)
2. **Support both old and new** (auto-repair migrates old → new)
3. **Monitor usage** (track % of stimuli still using old schema)
4. **Sunset after grace period** (remove old schema support after 30-60d)

**Migration Strategy:**

```python
# Define migration paths between schema versions
SCHEMA_MIGRATIONS = {
    # (from_version, to_version): [migration_functions]
    ("1.0.0", "1.1.0"): [
        lambda s: {**s, "conversation_id": s.get("conversation_id", generate_conversation_id(s))}
    ],
    ("1.1.0", "2.0.0"): [
        lambda s: {**{k: v for k, v in s.items() if k != "message_content"}, "content": s["message_content"]}
    ],
}

def migrate_stimulus(stim: dict, from_version: str, to_version: str) -> dict:
    """Apply migration path to upgrade stimulus to target schema version."""

    # Find shortest migration path
    path = find_migration_path(from_version, to_version)

    # Apply each migration in sequence
    for (v_from, v_to) in path:
        migrations = SCHEMA_MIGRATIONS.get((v_from, v_to), [])
        for migration in migrations:
            stim = migration(stim)
        stim["_schema_version"] = v_to

    return stim
```

**Historical Data Migration:**

When deploying breaking schema changes, migrate historical data:

```python
def migrate_historical_stimuli(
    citizen_id: str,
    stimulus_type: str,
    from_version: str,
    to_version: str,
    dry_run: bool = True
):
    """Migrate all historical stimuli of given type to new schema version."""

    # Query all stimuli matching type and old version
    query = """
    MATCH (s:Stimulus {citizen_id: $citizen_id, type: $type})
    WHERE s._schema_version = $from_version
    RETURN s
    """

    stimuli = db.execute(query, {
        "citizen_id": citizen_id,
        "type": stimulus_type,
        "from_version": from_version
    })

    migrated_count = 0
    failed_count = 0

    for stim in stimuli:
        try:
            # Apply migration
            migrated = migrate_stimulus(stim, from_version, to_version)

            # Validate migrated stimulus
            validate_stimulus(migrated, to_version)

            if not dry_run:
                # Update in database
                db.update_node(stim.id, migrated)

            migrated_count += 1

        except ValidationError as e:
            log_error(f"Failed to migrate {stim.id}: {e}")
            failed_count += 1

    return MigrationResult(
        total=len(stimuli),
        migrated=migrated_count,
        failed=failed_count,
        dry_run=dry_run
    )
```

**Schema Change Checklist:**

Before deploying schema change:

- [ ] Increment schema version appropriately (minor vs major)
- [ ] Add migration function to SCHEMA_MIGRATIONS
- [ ] Test migration on sample historical data
- [ ] Add auto-repair strategy for backward compatibility (if minor)
- [ ] Update validation schemas in trace_parser
- [ ] Document breaking changes in CHANGELOG
- [ ] Set deprecation timeline (if major)
- [ ] Run historical data migration (if major)
- [ ] Monitor rejection rate post-deployment (should not spike)
- [ ] Verify auto-repair success rate (if applicable)

**Rollback Plan:**

If schema change causes rejection rate spike:

1. **Immediate:** Rollback schema version to previous
2. **Investigate:** Review rejection reasons, check migration logic
3. **Fix:** Update migration/auto-repair strategies
4. **Retest:** Validate on historical sample data
5. **Redeploy:** With corrected migration logic

---

## 14. Updated Completeness Checklist

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
- [x] Implementation decisions documented (Nicolas 2025-10-25)
- [x] Phase 1 threshold seed values specified
- [x] Phase 2 evolution strategy (percentile-based tuning)
- [x] Alert safety policy defined
- [x] Persistence strategy (ALL L2 + TTL)
- [x] **Validation success rate monitoring (§13.1)**
- [x] **Rejection rate alerts (§13.2)**
- [x] **Auto-repair mode specification (§13.3)**
- [x] **Schema evolution protocol (§13.4)**

**Substrate specification: COMPLETE & IMPLEMENTATION-READY**

**Quality assurance infrastructure: SPECIFIED**
