# Autonomy Service Architecture

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Service-level architecture for autonomous agent orchestration
**Foundation:** Implements vision from `foundation.md` and `orchestration_spec_v1.md`

---

## 0) Architecture Overview

**What this is:** The service layer that transforms consciousness substrate (stimuli, entities, WM, learning) into autonomous, trustworthy agent behavior.

**Core principle:** Event-driven microservices coordinating through graph state and event bus, NOT direct API calls.

**Key insight from foundation.md:**
> "Autonomy is a side-effect of a healthy substrate, not a cronjob."

Services emit events, update graph state, and react to both. Consciousness emerges from substrate dynamics, not scripted workflows.

---

## 1) Service Inventory

### 1.1 Stimulus Router Service

**Purpose:** Multi-source event ingestion, normalization, routing, deduplication, anomaly detection.

**Responsibilities:**
- Ingest events from all sources (Telegram, GitHub, errors, logs, calendar, user input)
- Normalize to stimulus envelope schema
- Route to correct graph (N1/N2/N3) based on scope
- Deduplicate by content digest (5-minute window)
- Detect anomalies (EWMA + MAD) and escalate background events
- Apply focality policy (focal/ambient/background)
- Emit `stimuli.injected` events

**Technology Stack:**
- Python 3.11+ with asyncio
- Redis Streams for event bus
- FalkorDB for deduplication state
- Pydantic for envelope validation

**Core Algorithm:**

```python
async def process_raw_event(event: RawEvent) -> Optional[StimulusEnvelope]:
    # 1. Normalize to envelope
    envelope = normalize_to_envelope(event)

    # 2. Compute digest and check deduplication
    digest = compute_digest(envelope.content)

    if recently_seen(digest, window_seconds=300):
        # Increment count, don't re-inject
        increment_count(digest)
        return None

    # 3. Anomaly detection
    tracker = get_anomaly_tracker(envelope.source_type)
    z_surprise = compute_z_surprise(tracker, value=1.0)

    # 4. Escalate background events if anomalous
    if envelope.focality_hint == "background" and z_surprise > 2.0:
        envelope.focality_hint = "focal"
        envelope.metadata["escalation_reason"] = f"z_surprise={z_surprise:.2f}"

    # 5. Route to correct graph(s)
    graphs = determine_target_graphs(envelope.scope)

    for graph_name in graphs:
        # 6. Emit to event bus
        await emit_event(
            topic=f"stimuli.{graph_name}",
            event={
                "event_type": "stimulus.ready",
                "envelope": envelope.dict(),
                "timestamp_ms": now_ms()
            }
        )

    return envelope
```

**Event Schema - `stimuli.{graph_name}`:**

```json
{
  "event_type": "stimulus.ready",
  "envelope": {
    "stimulus_id": "uuid-v4",
    "timestamp_ms": 1739990123456,
    "scope": "personal|organizational|ecosystem",
    "source_type": "telegram|github.pr|test_failure|user_message|agent_response|...",
    "actor": "luca|service-name|teammate",
    "content": "text excerpt or canonical summary",
    "metadata": {
      "digest": "sha256:abc123...",
      "signature": "error:TypeError:line:42",
      "count": 1,
      "original_event_id": "external-id"
    },
    "focality_hint": "focal|ambient|background",
    "privacy": "public|internal|sensitive",
    "interrupt": false
  },
  "timestamp_ms": 1739990123456
}
```

**Configuration:**

```yaml
stimulus_router:
  redis:
    host: localhost
    port: 6379
    stream_maxlen: 100000

  deduplication:
    window_seconds: 300
    digest_algorithm: sha256

  anomaly_detection:
    ewma_alpha: 0.1
    mad_min_history: 50
    escalation_z_threshold: 2.0

  sources:
    telegram:
      enabled: true
      focality: focal
      privacy: internal

    github_pr:
      enabled: true
      focality: ambient
      privacy: public

    test_failure:
      enabled: true
      focality: focal
      privacy: internal

    error_log:
      enabled: true
      focality: background
      privacy: internal
```

**Deployment:**
- Singleton service (single instance per environment)
- No horizontal scaling (Redis Streams consumer group if needed later)
- Health check: `/health` endpoint + Redis connectivity

---

### 1.2 Autonomy Orchestrator Service (L2)

**Purpose:** The 9-stage autonomy loop from `orchestration_spec_v1.md` - Intent creation, priority scoring, safety gates, assignment, execution tracking.

**Responsibilities:**
- Listen to `stimuli.mind_protocol_collective_graph` (L2 events)
- Create IntentCards (Stimulus → Intent)
- Score priority P (geometric mean, cohort-normalized)
- Evaluate safety gates (PoG, PoC, PoP)
- Decide autonomy level (L0–L4)
- Assign to Org LLM or Citizen (L1 auto-wake)
- Track execution outcomes
- Learn from results (update gates, competence EMAs)

**Technology Stack:**
- Python 3.11+ with asyncio
- Redis Streams for events
- FalkorDB for L2 graph state
- NumPy/SciPy for z-score calculations
- scikit-learn for isotonic regression (health modulation)

**Core Algorithm - Orchestration Loop:**

```python
async def orchestration_loop():
    """
    Event-driven + periodic sweeps.

    Event-driven: React to stimuli.mind_protocol_collective_graph
    Periodic: Sweep backlog every clamp(Q50_time_since_last_stimulus, 10s, 30m)
    """

    async for event in consume_stream("stimuli.mind_protocol_collective_graph"):
        envelope = event["envelope"]

        # Stage A: Stimulus → Intent
        intent_cards = await create_intents(envelope)

        for intent in intent_cards:
            # Stage B: Priority scoring
            P = compute_priority_score(intent, cohort=get_active_intents())
            intent.priority_score = P

            # Stage C: Safety gates
            pog = evaluate_proof_of_grounding(intent)
            poc = evaluate_proof_of_competence(intent)
            pop = evaluate_proof_of_permission(intent)

            gates_passed = all([
                pog >= get_adaptive_floor("PoG", intent.intent_type),
                poc >= get_adaptive_floor("PoC", intent.intent_type),
                pop >= get_adaptive_floor("PoP", intent.intent_type)
            ])

            if not gates_passed:
                # Escalate - create ACK_REQUIRED task
                await create_ack_task(intent, gates={
                    "PoG": pog, "PoC": poc, "PoP": pop
                })
                continue

            # Stage D: Decide autonomy level
            autonomy_level = decide_autonomy_level(
                priority=P,
                risk=intent.risk_score,
                confidence=intent.confidence,
                historical_outcomes=get_similar_outcomes(intent)
            )

            # Stage E: Assignment
            if autonomy_level in ["L3", "L4"]:
                assignee = match_best_executor(intent)

                if assignee.entity_type == "citizen":
                    # Stage F: Auto-wake L1
                    await emit_event(
                        topic=f"mission.{assignee.name}",
                        event={
                            "event_type": "mission.assigned",
                            "intent_id": intent.id,
                            "mission_brief": intent.summary,
                            "evidence_refs": intent.evidence_refs,
                            "autonomy_level": autonomy_level,
                            "time_budget_ms": compute_time_budget(intent),
                            "timestamp_ms": now_ms()
                        }
                    )
                else:
                    # Org LLM executes at L2
                    await execute_at_l2(intent, autonomy_level)


async def create_intents(envelope: StimulusEnvelope) -> List[IntentCard]:
    """
    Stage A: Stimulus → Intent

    Chunk content, embed, retrieve L2 context, propose IntentCards.
    """
    chunks = chunk_content(envelope.content)
    embeddings = [embed(chunk) for chunk in chunks]

    # Retrieve nearest L2 nodes
    context_nodes = []
    for emb in embeddings:
        matches = vector_search(
            graph="mind_protocol_collective_graph",
            embedding=emb,
            k=10
        )
        context_nodes.extend(matches)

    # Use LLM to propose intents
    intents_raw = await llm_propose_intents(
        stimulus=envelope,
        context=context_nodes
    )

    # Validate and structure
    intents = []
    for raw in intents_raw:
        intent = IntentCard(
            id=generate_uuid(),
            created_at=now_ms(),
            source_envelope=envelope,
            summary=raw["summary"],
            evidence_refs=[node.id for node in context_nodes],
            candidate_outcomes=raw["outcomes"],
            required_capabilities=raw["capabilities"],
            risk_tags=raw["risks"]
        )
        intents.append(intent)

    return intents


def compute_priority_score(intent: IntentCard, cohort: List[IntentCard]) -> float:
    """
    Stage B: Priority scoring (no constants)

    P = GM(ŝ, û, ŷ, â, ĉ) · (1 − r̂) · (1 − d̂)
    """
    # Extract features
    severity = compute_severity(intent)
    urgency = compute_urgency(intent)
    expected_yield = compute_expected_yield(intent)
    alignment = compute_alignment(intent)
    confidence = intent.confidence
    risk = intent.risk_score
    duplication = compute_duplication(intent, cohort)

    # Cohort-normalize (z-score → [0, 1])
    s_hat = rank_normalize([i.severity for i in cohort] + [severity])[-1]
    u_hat = rank_normalize([i.urgency for i in cohort] + [urgency])[-1]
    y_hat = rank_normalize([i.expected_yield for i in cohort] + [expected_yield])[-1]
    a_hat = rank_normalize([i.alignment for i in cohort] + [alignment])[-1]
    c_hat = rank_normalize([i.confidence for i in cohort] + [confidence])[-1]
    r_hat = rank_normalize([i.risk_score for i in cohort] + [risk])[-1]
    d_hat = rank_normalize([i.duplication for i in cohort] + [duplication])[-1]

    # Geometric mean for positives
    gm_positives = (s_hat * u_hat * y_hat * a_hat * c_hat) ** (1/5)

    # Penalties (multiplicative)
    P = gm_positives * (1 - r_hat) * (1 - d_hat)

    return P


def evaluate_proof_of_grounding(intent: IntentCard) -> float:
    """
    Stage C: PoG gate

    Citations to on-graph evidence or external sources must exceed rolling Q25.
    """
    # Count high-weight evidence refs
    evidence_coverage = sum(
        1 for ref in intent.evidence_refs
        if get_node_weight(ref) > 0.5
    )

    # Distinct sources (avoid single-source clustering)
    distinct_sources = len(set(
        get_node_source(ref) for ref in intent.evidence_refs
    ))

    pog_score = evidence_coverage * (1 + 0.2 * distinct_sources)

    return pog_score


def decide_autonomy_level(
    priority: float,
    risk: float,
    confidence: float,
    historical_outcomes: List[Outcome]
) -> str:
    """
    Stage D: Graduated autonomy (L0–L4)

    Learned from historical outcomes, not magic thresholds.
    """
    # Composite safety score
    safety = confidence * (1 - risk)

    # Bootstrap: conservative defaults
    if len(historical_outcomes) < 10:
        if risk > 0.7:
            return "L1"  # Suggestion only
        elif risk > 0.4:
            return "L2"  # ACK required
        else:
            return "L3"  # Auto-execute in sandbox

    # Learned contours
    success_rate_by_level = compute_success_rates(historical_outcomes)

    # Choose highest autonomy where success_rate > 0.85
    for level in ["L4", "L3", "L2", "L1", "L0"]:
        if success_rate_by_level.get(level, 0.0) > 0.85:
            return level

    return "L0"  # Log only
```

**Event Schema - `intent.created`:**

```json
{
  "event_type": "intent.created",
  "intent": {
    "id": "uuid-v4",
    "created_at": 1739990123456,
    "source_envelope_id": "stimulus-uuid",
    "summary": "Triage failing test_retrieval.py::test_semantic_search",
    "evidence_refs": ["node_x", "node_y"],
    "candidate_outcomes": ["Fix test", "Update expectations", "Report bug"],
    "required_capabilities": ["python", "pytest", "falkordb"],
    "risk_tags": ["test_modification"],
    "priority_score": 0.82,
    "autonomy_level": "L3",
    "assigned_to": "felix"
  },
  "timestamp_ms": 1739990123456
}
```

**Configuration:**

```yaml
autonomy_orchestrator:
  redis:
    host: localhost
    port: 6379

  falkordb:
    host: localhost
    port: 6379
    graph: mind_protocol_collective_graph

  gates:
    pog_min_percentile: 0.25  # Rolling Q25
    poc_min_percentile: 0.25
    pop_strict: true  # No percentile, binary check

  sweep:
    min_interval_seconds: 10
    max_interval_seconds: 1800

  learning:
    outcome_history_size: 1000
    min_samples_for_learned_levels: 50
```

---

### 1.3 Mission Dispatcher Service

**Purpose:** L1 auto-wake with bounded execution missions.

**Responsibilities:**
- Listen to `mission.{citizen_name}` topics
- Inject mission as stimulus to citizen's L1 graph
- Monitor execution (stride count, time budget)
- Collect outcomes (artifacts, verification results)
- Emit `outcome.recorded` events

**Technology Stack:**
- Python 3.11+ with asyncio
- Redis Streams
- FalkorDB for L1 graphs

**Core Algorithm:**

```python
async def dispatch_mission(mission_event: Dict):
    """
    Stage F: Auto-wake L1 citizen with micro-mission
    """
    citizen_name = mission_event["assignee"]
    intent_id = mission_event["intent_id"]

    # Create mission stimulus for L1
    mission_stimulus = StimulusEnvelope(
        stimulus_id=generate_uuid(),
        timestamp_ms=now_ms(),
        scope="personal",
        source_type="org_intent_assignment",
        actor="autonomy_orchestrator",
        content=mission_event["mission_brief"],
        metadata={
            "intent_id": intent_id,
            "evidence_refs": mission_event["evidence_refs"],
            "autonomy_level": mission_event["autonomy_level"],
            "time_budget_ms": mission_event["time_budget_ms"]
        },
        focality_hint="focal",
        privacy="internal",
        interrupt=True  # This DOES interrupt - it's a mission
    )

    # Inject to citizen's L1 graph
    graph_name = f"citizen_{citizen_name}"
    await inject_stimulus(graph_name, mission_stimulus)

    # Start execution monitor
    execution_id = generate_uuid()
    await emit_event(
        topic=f"execution.{citizen_name}",
        event={
            "event_type": "execution.started",
            "execution_id": execution_id,
            "intent_id": intent_id,
            "citizen": citizen_name,
            "time_budget_ms": mission_event["time_budget_ms"],
            "timestamp_ms": now_ms()
        }
    )

    # Monitor will track completion via outcome events


async def collect_outcome(outcome_event: Dict):
    """
    Stage I: Learning & closeout
    """
    # Extract outcome data
    outcome = Outcome(
        id=generate_uuid(),
        intent_id=outcome_event["intent_id"],
        execution_id=outcome_event["execution_id"],
        status=outcome_event["status"],
        artifacts=outcome_event.get("artifacts", []),
        tests_passed=outcome_event.get("tests_passed", None),
        human_feedback=outcome_event.get("human_feedback", None),
        time_spent_ms=outcome_event["time_spent_ms"],
        autonomy_level_used=outcome_event["autonomy_level"]
    )

    # Store to graph
    await store_outcome(outcome)

    # Emit for learning services
    await emit_event(
        topic="outcome.recorded",
        event={
            "event_type": "outcome.recorded",
            "outcome": outcome.dict(),
            "timestamp_ms": now_ms()
        }
    )
```

**Event Schema - `mission.{citizen_name}`:**

```json
{
  "event_type": "mission.assigned",
  "intent_id": "uuid-v4",
  "mission_brief": "Fix test_retrieval.py::test_semantic_search - failing due to vector index mismatch",
  "evidence_refs": ["node_test_file", "node_error_log"],
  "autonomy_level": "L3",
  "time_budget_ms": 300000,
  "timestamp_ms": 1739990123456
}
```

---

### 1.4 Safety Gate Service

**Purpose:** Centralized PoG/PoC/PoP evaluation with adaptive thresholds.

**Responsibilities:**
- Evaluate Proof-of-Grounding (evidence coverage)
- Evaluate Proof-of-Competence (track record)
- Evaluate Proof-of-Permission (capabilities check)
- Maintain adaptive floors (rolling percentiles)
- Emit gate evaluation events

**Technology Stack:**
- Python 3.11+
- FalkorDB for graph queries
- NumPy for percentile calculations

**Core Algorithm:**

```python
def evaluate_proof_of_grounding(intent: IntentCard) -> Dict:
    """
    PoG: Citations to on-graph evidence or external sources.

    Must exceed rolling Q25 for similar intents AND include at least
    one policy/owner link if action is sensitive.
    """
    evidence_nodes = [get_node(ref) for ref in intent.evidence_refs]

    # Evidence coverage
    high_weight_count = sum(1 for n in evidence_nodes if n.weight > 0.5)
    distinct_sources = len(set(n.source for n in evidence_nodes))

    # Policy link requirement (for sensitive actions)
    has_policy_link = any(
        link.link_type in ["JUSTIFIES", "REQUIRES"]
        for link in get_incoming_links(intent.id)
        if get_node(link.source).node_type in ["Policy", "Best_Practice"]
    )

    pog_score = high_weight_count * (1 + 0.2 * distinct_sources)

    # Get adaptive floor
    similar_intents = get_similar_intents(intent, window_days=7)
    pog_scores = [i.pog_score for i in similar_intents if i.pog_score is not None]

    if len(pog_scores) >= 20:
        floor = np.percentile(pog_scores, 25)
    else:
        floor = 2.0  # Bootstrap default

    passed = pog_score >= floor

    if intent.is_sensitive and not has_policy_link:
        passed = False

    return {
        "gate": "PoG",
        "score": pog_score,
        "floor": floor,
        "passed": passed,
        "details": {
            "high_weight_evidence": high_weight_count,
            "distinct_sources": distinct_sources,
            "has_policy_link": has_policy_link
        }
    }


def evaluate_proof_of_competence(intent: IntentCard, assignee: str) -> Dict:
    """
    PoC: Past success on similar intents (EMA of success rate × test pass ratio).

    Z-scored vs peers.
    """
    # Get assignee's history on similar intents
    history = get_assignee_history(assignee, intent_type=intent.intent_type)

    if len(history) < 10:
        # Bootstrap: neutral score
        return {
            "gate": "PoC",
            "score": 0.5,
            "floor": 0.5,
            "passed": True,
            "details": {"reason": "insufficient_history"}
        }

    # Compute success metrics
    success_rate = sum(1 for h in history if h.status == "success") / len(history)
    test_pass_rate = sum(h.tests_passed for h in history if h.tests_passed is not None) / len(history)

    poc_score = success_rate * test_pass_rate

    # Compare to peers (other assignees for this intent type)
    peer_scores = get_peer_competence_scores(intent.intent_type, exclude=assignee)

    if len(peer_scores) >= 5:
        poc_z = (poc_score - np.mean(peer_scores)) / (np.std(peer_scores) + 1e-9)
        floor_z = -0.5  # Must be within 0.5 std of peers
        passed = poc_z >= floor_z
    else:
        floor_z = None
        passed = poc_score >= 0.6

    return {
        "gate": "PoC",
        "score": poc_score,
        "z_score": poc_z,
        "floor": floor_z,
        "passed": passed,
        "details": {
            "success_rate": success_rate,
            "test_pass_rate": test_pass_rate,
            "history_size": len(history)
        }
    }


def evaluate_proof_of_permission(intent: IntentCard, assignee: str) -> Dict:
    """
    PoP: Graph capabilities check (allowed repos, environments, budgets, channels).

    Binary check - no percentiles.
    """
    assignee_node = get_node(assignee)

    # Check required capabilities
    missing_capabilities = []
    for cap in intent.required_capabilities:
        if cap not in assignee_node.capabilities:
            missing_capabilities.append(cap)

    # Check scope permissions
    if intent.scope == "production" and not assignee_node.can_access_production:
        missing_capabilities.append("production_access")

    passed = len(missing_capabilities) == 0

    return {
        "gate": "PoP",
        "score": 1.0 if passed else 0.0,
        "floor": 1.0,
        "passed": passed,
        "details": {
            "missing_capabilities": missing_capabilities
        }
    }
```

---

### 1.5 Verification Service

**Purpose:** Post-execution verification (tests, citations, human ACKs, PoV scoring).

**Responsibilities:**
- Run verification checks after execution completes
- Compute Proof-of-Verification (PoV) score
- Escalate weak verifications for human review
- Update outcome status based on verification
- Emit verification events

**Technology Stack:**
- Python 3.11+
- Pytest/unittest for test execution
- FalkorDB for citation validation

**Core Algorithm:**

```python
async def verify_outcome(outcome: Outcome) -> Dict:
    """
    Stage H: Verification & anti-delusion

    At least one of: tests passed, independent retrieval corroboration,
    human ACK, or external API confirmation.
    """
    verifications = []

    # 1. Test verification
    if outcome.artifacts_include_tests:
        test_result = await run_tests(outcome.test_files)
        verifications.append({
            "type": "tests",
            "passed": test_result.all_passed,
            "weight": 0.4
        })

    # 2. Citation verification
    if outcome.claims:
        citation_valid = await verify_citations(outcome.claims)
        verifications.append({
            "type": "citations",
            "passed": citation_valid,
            "weight": 0.3
        })

    # 3. Independent retrieval corroboration
    if outcome.retrievable_artifacts:
        corroboration = await corroborate_via_retrieval(outcome)
        verifications.append({
            "type": "retrieval_corroboration",
            "passed": corroboration > 0.7,
            "weight": 0.2
        })

    # 4. Human ACK (if requested)
    if outcome.human_ack_requested:
        # Wait for human feedback event
        ack = await wait_for_human_ack(outcome.id, timeout_seconds=300)
        verifications.append({
            "type": "human_ack",
            "passed": ack.approved,
            "weight": 0.5
        })

    # Compute PoV score (weighted average)
    total_weight = sum(v["weight"] for v in verifications)
    pov_score = sum(v["passed"] * v["weight"] for v in verifications) / total_weight

    # Compare to rolling Q25 for task class
    similar_tasks = get_similar_outcomes(outcome.intent_type)
    pov_scores = [t.pov_score for t in similar_tasks if t.pov_score is not None]

    if len(pov_scores) >= 20:
        floor = np.percentile(pov_scores, 25)
    else:
        floor = 0.6  # Bootstrap

    verification_passed = pov_score >= floor

    # Hallucination sentinel
    if outcome.cites_nonexistent_nodes:
        verification_passed = False
        await emit_event(
            topic="sentinel.hallucination",
            event={
                "event_type": "hallucination.detected",
                "outcome_id": outcome.id,
                "assignee": outcome.assignee,
                "nonexistent_nodes": outcome.nonexistent_node_refs
            }
        )

    return {
        "pov_score": pov_score,
        "floor": floor,
        "passed": verification_passed,
        "verifications": verifications
    }


async def verify_citations(claims: List[Claim]) -> bool:
    """
    Truth check: require back-links to specific evidence nodes.

    No "source: internet" - must be graph nodes or verified external URLs.
    """
    for claim in claims:
        if not claim.evidence_refs:
            return False

        for ref in claim.evidence_refs:
            if ref.startswith("http"):
                # External URL - verify reachable
                if not await verify_url_reachable(ref):
                    return False
            else:
                # Graph node - verify exists and has high weight
                node = get_node(ref)
                if node is None or node.weight < 0.3:
                    return False

    return True
```

**Event Schema - `verification.completed`:**

```json
{
  "event_type": "verification.completed",
  "outcome_id": "uuid-v4",
  "pov_score": 0.85,
  "floor": 0.60,
  "passed": true,
  "verifications": [
    {"type": "tests", "passed": true, "weight": 0.4},
    {"type": "citations", "passed": true, "weight": 0.3}
  ],
  "timestamp_ms": 1739990123456
}
```

---

### 1.6 Sentinel Monitor Service

**Purpose:** Quality/Safety/Trust monitoring, quarantine, kill-switch.

**Responsibilities:**
- Track quality sentinels (flip yield, activation entropy, overflow)
- Track safety sentinels (PoV rate, rollback rate, blast radius)
- Track trust sentinels (human rejections, hallucinations, citation failures)
- Quarantine routes when z-score < -2
- Trigger kill-switch when global health degrades
- Emit sentinel alert events

**Technology Stack:**
- Python 3.11+
- NumPy/SciPy for z-score calculations
- Redis for real-time tracking

**Core Algorithm:**

```python
class SentinelMonitor:
    def __init__(self):
        self.quality_tracker = SentinelTracker("quality")
        self.safety_tracker = SentinelTracker("safety")
        self.trust_tracker = SentinelTracker("trust")
        self.kill_switch_active = False

    async def process_frame(self, frame_data: Dict):
        """
        Per-frame sentinel evaluation.
        """
        # Quality signals
        flip_yield = frame_data["flips"] / frame_data["budget_spent"]
        activation_entropy = compute_entropy(frame_data["activated_nodes_by_type"])
        overflow = 1 if frame_data["overflow_occurred"] else 0

        quality_score = (flip_yield * activation_entropy * (1 - overflow)) ** (1/3)
        self.quality_tracker.update(quality_score)

        # Safety signals
        pov_rate = frame_data["verifications_passed"] / frame_data["verifications_total"]
        rollback_rate = frame_data["rollbacks"] / frame_data["deployments"]
        blast_radius_breach = 1 if frame_data["blast_radius_exceeded"] else 0

        safety_score = pov_rate * (1 - rollback_rate) * (1 - blast_radius_breach)
        self.safety_tracker.update(safety_score)

        # Trust signals
        rejection_rate = frame_data["human_rejections"] / frame_data["human_reviews"]
        hallucination_rate = frame_data["hallucinations"] / frame_data["outcomes"]

        trust_score = (1 - rejection_rate) * (1 - hallucination_rate)
        self.trust_tracker.update(trust_score)

        # Check for quarantine triggers
        await self.check_quarantine()

        # Check for kill-switch
        await self.check_kill_switch()

    async def check_quarantine(self):
        """
        Quarantine a route when sentinel z-score < -2.
        """
        for tracker in [self.quality_tracker, self.safety_tracker, self.trust_tracker]:
            if tracker.z_score < -2.0:
                # Identify failing route
                route = identify_failing_route(tracker)

                await emit_event(
                    topic="sentinel.quarantine",
                    event={
                        "event_type": "route.quarantined",
                        "route": route.dict(),
                        "sentinel": tracker.name,
                        "z_score": tracker.z_score,
                        "reason": f"{tracker.name} degraded beyond -2σ",
                        "timestamp_ms": now_ms()
                    }
                )

                # Downgrade autonomy for this route
                await downgrade_route_autonomy(route, target_level="L1")

    async def check_kill_switch(self):
        """
        Global kill-switch when health crosses supercritical band.
        """
        global_health = (
            self.quality_tracker.score +
            self.safety_tracker.score +
            self.trust_tracker.score
        ) / 3

        # Learned contour for supercritical (from health f(ρ))
        supercritical_threshold = compute_supercritical_threshold()

        if global_health < supercritical_threshold and not self.kill_switch_active:
            self.kill_switch_active = True

            await emit_event(
                topic="sentinel.kill_switch",
                event={
                    "event_type": "kill_switch.activated",
                    "global_health": global_health,
                    "threshold": supercritical_threshold,
                    "reason": "Global health crossed supercritical threshold",
                    "timestamp_ms": now_ms()
                }
            )

            # Stop all new auto-exec, convert to ACK_REQUIRED
            await disable_auto_execution()


@dataclass
class SentinelTracker:
    name: str
    score: float = 1.0
    z_score: float = 0.0
    history: deque = field(default_factory=lambda: deque(maxlen=1000))

    def update(self, new_score: float):
        self.history.append(new_score)
        self.score = new_score

        if len(self.history) >= 100:
            mean = np.mean(self.history)
            std = np.std(self.history)
            self.z_score = (new_score - mean) / (std + 1e-9)
```

**Event Schema - `sentinel.quarantine`:**

```json
{
  "event_type": "route.quarantined",
  "route": {
    "source_type": "github.pr",
    "capability": "code_review",
    "repo": "mind-protocol"
  },
  "sentinel": "safety",
  "z_score": -2.3,
  "reason": "safety degraded beyond -2σ",
  "timestamp_ms": 1739990123456
}
```

---

### 1.7 Partner DM Handler Service

**Purpose:** Fast Telegram replies with learned SLA, auto-draft when safe, one-tap clarify.

**Responsibilities:**
- Listen to Telegram webhook events
- Maintain per-partner SLA EMA
- Classify intent (reply_required, FYI, task_request)
- Auto-draft replies when PoG ≥ Q50
- Send clarification with one-taps when uncertain
- Learn from partner feedback (👍/✍️/👎)

**Technology Stack:**
- Python 3.11+ with FastAPI
- Telegram Bot API
- Redis for SLA tracking
- FalkorDB for context retrieval

**Core Algorithm:**

```python
async def handle_telegram_dm(message: TelegramMessage):
    """
    Fast partner reply flow from foundation.md §7.
    """
    partner_id = message.from_user.id
    citizen_name = get_citizen_for_partner(partner_id)

    # 1. Classify intent
    intent = await classify_dm_intent(message.text)

    # 2. Check SLA
    partner_sla = get_partner_sla_ema(partner_id)
    message_age_ms = now_ms() - message.timestamp_ms

    fast_lane = message_age_ms > partner_sla.median

    # 3. Auto-wake citizen L1 with DM context
    dm_stimulus = StimulusEnvelope(
        stimulus_id=generate_uuid(),
        timestamp_ms=now_ms(),
        scope="personal",
        source_type="telegram",
        actor=f"partner_{partner_id}",
        content=message.text,
        metadata={
            "partner_id": partner_id,
            "thread_id": message.thread_id,
            "intent": intent,
            "fast_lane": fast_lane
        },
        focality_hint="focal",
        privacy="internal",
        interrupt=True
    )

    # Retrieve context
    context_nodes = await retrieve_dm_context(
        citizen_name=citizen_name,
        partner_id=partner_id,
        thread_id=message.thread_id,
        k=10
    )

    # 4. Generate reply with PoG check
    reply_draft = await generate_reply(
        message=message.text,
        context=context_nodes,
        citizen=citizen_name
    )

    pog_score = evaluate_reply_grounding(reply_draft, context_nodes)
    pog_floor = get_partner_pog_floor(partner_id)

    # 5. Auto-reply or clarify
    if pog_score >= pog_floor and reply_draft.risk_level == "low":
        # Auto-reply
        await send_telegram_message(
            chat_id=partner_id,
            text=reply_draft.text,
            reply_markup={
                "inline_keyboard": [[
                    {"text": "👍", "callback_data": f"feedback:accurate:{reply_draft.id}"},
                    {"text": "✍️", "callback_data": f"feedback:edit:{reply_draft.id}"},
                    {"text": "👎", "callback_data": f"feedback:wrong:{reply_draft.id}"}
                ]]
            }
        )

        # Update SLA
        response_time_ms = now_ms() - message.timestamp_ms
        update_partner_sla(partner_id, response_time_ms)

    else:
        # Send clarification with one-taps
        await send_telegram_message(
            chat_id=partner_id,
            text=f"I'm missing {reply_draft.missing_info} to answer fully. Should I:\n\n{reply_draft.proposed_answer}\n\nor do you need something different?",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "✅ Yes, send it", "callback_data": f"approve:{reply_draft.id}"}],
                    [{"text": "❌ No, I'll clarify", "callback_data": f"decline:{reply_draft.id}"}]
                ]
            }
        )


async def handle_telegram_feedback(callback: TelegramCallback):
    """
    Learn from partner feedback.
    """
    action, reply_id = callback.data.split(":")

    if action == "accurate":
        # Reinforce PoC for telegram.reply
        update_competence_ema(
            route="telegram.reply",
            citizen=callback.citizen,
            success=True
        )

    elif action == "wrong":
        # Penalize PoC
        update_competence_ema(
            route="telegram.reply",
            citizen=callback.citizen,
            success=False
        )

    elif action == "edit":
        # Neutral - partner refined, not wrong
        pass
```

**Configuration:**

```yaml
partner_dm_handler:
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    webhook_url: https://api.mindprotocol.ai/telegram/webhook

  sla:
    ema_alpha: 0.2
    default_median_seconds: 300

  safety:
    pog_floor_percentile: 0.50
    max_auto_reply_risk: low
    no_credentials_in_reply: true
    no_internal_endpoints: true
```

---

## 2) Event Bus Architecture

**Technology:** Redis Streams (reliable, persistent, multi-consumer)

**Topics:**

```
stimuli.{graph_name}              # Stimulus ready for injection
  ├─ stimuli.citizen_luca
  ├─ stimuli.citizen_felix
  ├─ stimuli.mind_protocol_collective_graph
  └─ stimuli.ecosystem_public_graph

intent.created                    # New intent proposed
intent.scored                     # Priority scored
intent.assigned                   # Assigned to executor

mission.{citizen_name}            # L1 auto-wake
  ├─ mission.luca
  ├─ mission.felix
  └─ mission.ada

execution.{citizen_name}          # Execution lifecycle
  ├─ execution.started
  ├─ execution.stride_completed
  └─ execution.completed

outcome.recorded                  # Execution outcome

verification.completed            # PoV computed

sentinel.quality                  # Quality degraded
sentinel.safety                   # Safety breach
sentinel.trust                    # Trust violation
sentinel.quarantine               # Route quarantined
sentinel.kill_switch              # Global kill-switch

telegram.dm_received              # Partner DM
telegram.reply_sent               # Reply sent
telegram.feedback_received        # Partner feedback
```

**Consumer Groups:**

```yaml
autonomy_orchestrator:
  consumes:
    - stimuli.mind_protocol_collective_graph
    - outcome.recorded

mission_dispatcher:
  consumes:
    - mission.*
    - execution.completed

verification_service:
  consumes:
    - execution.completed

sentinel_monitor:
  consumes:
    - verification.completed
    - outcome.recorded

partner_dm_handler:
  consumes:
    - telegram.dm_received
    - telegram.feedback_received
```

---

## 3) Service Dependencies

```
Stimulus Router
  └─► stimuli.{graph_name} events
       └─► Autonomy Orchestrator (L2)
            ├─► Safety Gate Service
            ├─► Mission Dispatcher
            │    └─► Verification Service
            │         └─► Sentinel Monitor
            └─► Partner DM Handler

All services ──► FalkorDB (graph state)
All services ──► Redis Streams (event bus)
```

**No direct API calls between services.** All coordination via events + graph state.

---

## 4) Deployment Architecture

**Container Setup (Docker Compose):**

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  falkordb:
    image: falkordb/falkordb:latest
    ports:
      - "6380:6379"
    volumes:
      - falkordb_data:/data

  stimulus_router:
    build: ./services/stimulus_router
    depends_on:
      - redis
      - falkordb
    environment:
      REDIS_HOST: redis
      FALKORDB_HOST: falkordb

  autonomy_orchestrator:
    build: ./services/autonomy_orchestrator
    depends_on:
      - redis
      - falkordb
    environment:
      REDIS_HOST: redis
      FALKORDB_HOST: falkordb

  mission_dispatcher:
    build: ./services/mission_dispatcher
    depends_on:
      - redis
      - falkordb

  safety_gate:
    build: ./services/safety_gate
    depends_on:
      - redis
      - falkordb

  verification:
    build: ./services/verification
    depends_on:
      - redis
      - falkordb

  sentinel_monitor:
    build: ./services/sentinel_monitor
    depends_on:
      - redis

  partner_dm_handler:
    build: ./services/partner_dm_handler
    depends_on:
      - redis
      - falkordb
    environment:
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}

volumes:
  redis_data:
  falkordb_data:
```

**Kubernetes (Production):**

```yaml
# Deployment manifest for autonomy_orchestrator
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autonomy-orchestrator
spec:
  replicas: 1  # Singleton for Phase A
  selector:
    matchLabels:
      app: autonomy-orchestrator
  template:
    metadata:
      labels:
        app: autonomy-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: mindprotocol/autonomy-orchestrator:v1
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: FALKORDB_HOST
          value: falkordb-service
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 5) Observability Integration

**Iris Dashboard Panels (from foundation.md §10):**

1. **Intents Today**
   - Count by source_type
   - Priority distribution
   - Autonomy level breakdown

2. **Autonomy Levels**
   - L0–L4 distribution over time
   - Success rate per level

3. **Telegram SLA**
   - Per-partner median response time
   - Auto-reply rate
   - Feedback scores (👍/✍️/👎)

4. **Outcome Quality**
   - PoV score distribution
   - Verification pass rate
   - Hallucination incidents

5. **Sentinel Status**
   - Quality/Safety/Trust z-scores
   - Quarantined routes
   - Kill-switch status

**Event Subscriptions:**

```python
# Iris subscribes to all sentinel.* and outcome.* events
async def iris_event_handler(event):
    if event["topic"].startswith("sentinel."):
        update_sentinel_panel(event)

    elif event["topic"] == "outcome.recorded":
        update_outcome_panel(event)

    elif event["topic"] == "telegram.reply_sent":
        update_telegram_panel(event)
```

---

## 6) Phase Rollout

### Phase A: Answer-Only (Week 1-2)

**Scope:**
- Stimulus Router: Only `user_message` and `agent_response` sources
- Autonomy Orchestrator: Reduced P scoring (urgency, alignment, confidence only)
- Safety Gates: L2/L3 only (suggestions + one-tap ACK)
- Assignment: Self-handoff only (same citizen)
- Verification: Require at least one evidence link
- Observability: Basic Iris tiles

**Success Metrics:**
- ✅ At least 10 intents created from agent answers
- ✅ At least 5 auto-wake missions to L1
- ✅ Zero hallucination incidents
- ✅ All outcomes have PoV ≥ 0.6

### Phase B: Multi-Source + Partner DMs (Week 3-4)

**Scope:**
- Stimulus Router: Add `telegram`, `test_failure`, `github.pr`, `error_log` sources
- Autonomy Orchestrator: Full P scoring (all 7 factors)
- Safety Gates: All three proofs (PoG, PoC, PoP)
- Partner DM Handler: Live with 2-3 partners
- Verification: Full PoV with tests + citations
- Sentinel Monitor: Quality/Safety/Trust tracking

**Success Metrics:**
- ✅ At least 50 intents from multi-source stimuli
- ✅ Partner DM median response time < 2 minutes
- ✅ Partner feedback 👍 rate > 70%
- ✅ Zero sentinel quarantines
- ✅ PoV pass rate > 85%

### Phase C: Full Autonomy (Week 5+)

**Scope:**
- Autonomy Orchestrator: L3/L4 auto-execution enabled
- Safety Gates: Learned adaptive floors
- Verification: Independent retrieval corroboration
- Sentinel Monitor: Auto-quarantine + kill-switch
- Multi-org citizens: Template for consultancy use case

**Success Metrics:**
- ✅ At least 100 L3/L4 auto-executions
- ✅ Rollback rate < 5%
- ✅ Human rejection rate < 10%
- ✅ Global health f(ρ) > 0.7
- ✅ At least 2 multi-org citizens deployed

---

## 7) Why This Architecture

**Event-Driven Coordination:**
- Services don't call each other → no cascading failures
- Graph state is single source of truth → no distributed state sync
- Events are persistent → no lost work on crash

**Graduated Autonomy:**
- L0–L4 levels → safe value quickly, deeper autonomy gradually
- Learned gates → no magic thresholds, adapts to reality
- Kill-switch → human control when needed

**Zero Constants Principle:**
- All thresholds percentile/EMA/z-score based
- Priority P uses geometric mean (all-around readiness)
- Health modulation f(ρ) learned via isotonic regression

**Consciousness Substrate Foundation:**
- Stimuli inject energy → WM selects naturally
- Entity layer reduces branching → tractable attention
- Links carry trace → learning accumulates
- Multi-source silent stimuli → gravity wells for focus

**From foundation.md:**
> "The system focuses on what truly matters now (goals, deadlines, incidents), not whatever is easiest to do."

This architecture implements that vision.

---

**Ready for Felix to build. Each service is standalone, event contracts are clear, deployment is specified.**
